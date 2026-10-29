from __future__ import annotations

import ast
import hashlib
import importlib
import inspect
import json
import py_compile
import shutil
import sys
import tempfile
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType, SimpleNamespace
from typing import Any, Mapping


PIPELINE_OPERATIONS_SOURCE = r'''"""Read-only universal per-pipeline Runtime operations projection.

This module composes existing Runtime authorities.  It owns no jobs, queues,
registrations, correlations, workflows, handlers, or recovery mutations.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Callable, Mapping

from backend.server.orchestration.job_store import load_jobs, list_job_events
from backend.server.coordination.runtime_integration.workflow_job_correlation import (
    get_workflow_job_correlation_registry,
)
from backend.server.runtime.universal_runtime_registration import (
    list_runtime_registrations,
)


PIPELINE_OPERATIONS_VERSION = "runtime_pipeline_operations_v1.0.0"
PIPELINE_OPERATIONS_SCHEMA_VERSION = "runtime_pipeline_operations_schema_v1"


class PipelineOperationsError(RuntimeError):
    pass


class PipelineOperationsNotFoundError(PipelineOperationsError):
    pass


def _plain(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_plain(item) for item in value]
    if is_dataclass(value):
        return _plain(asdict(value))
    for name in ("to_dict", "to_canonical_dict"):
        method = getattr(value, name, None)
        if callable(method):
            return _plain(method())
    raw = getattr(value, "__dict__", None)
    if isinstance(raw, Mapping):
        return _plain(raw)
    return str(value)


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple, set, frozenset)):
        return tuple(_freeze(item) for item in value)
    return value


def _text(value: Any) -> str:
    return str(value if value is not None else "").strip()


def _status(value: Any) -> str:
    raw = getattr(value, "value", value)
    return _text(raw).lower()


def _mapping(value: Any) -> dict[str, Any]:
    plain = _plain(value)
    return dict(plain) if isinstance(plain, Mapping) else {}


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _pipeline_id(value: Any) -> str:
    text = _text(value).lower()
    if not text or text != _text(value) or any(not (c.isalnum() or c in "_-") for c in text):
        raise PipelineOperationsError("pipeline_id must be canonical and non-empty.")
    return text


def _registration_pipeline(record: Mapping[str, Any]) -> str:
    return _text(record.get("pipeline") or record.get("pipeline_id")).lower()


def _stage_order(registrations: tuple[dict[str, Any], ...]) -> tuple[str, ...]:
    by_stage = {_text(item.get("stage")): item for item in registrations if _text(item.get("stage"))}
    if not by_stage:
        return ()
    ordered: list[str] = []
    remaining = set(by_stage)
    while remaining:
        runnable = sorted(
            stage for stage in remaining
            if not ({_text(v) for v in by_stage[stage].get("predecessor_stages", ()) if _text(v)} & remaining)
        )
        if not runnable:
            raise PipelineOperationsError("Runtime registration dependency graph contains a cycle.")
        for stage in runnable:
            ordered.append(stage)
            remaining.remove(stage)
    return tuple(ordered)


def _workflow_matches(workflow: Any, pipeline_id: str) -> bool:
    workflow_type = _text(getattr(workflow, "workflow_type", "")).lower()
    metadata = _mapping(getattr(workflow, "metadata", {}))
    declared = _text(metadata.get("pipeline_id") or metadata.get("pipeline")).lower()
    return workflow_type == pipeline_id or declared == pipeline_id


def _job_matches_workflow(payload: Mapping[str, Any], workflow: Any) -> bool:
    metadata = _mapping(payload.get("metadata"))
    job_payload = _mapping(payload.get("payload"))
    workflow_id = _text(getattr(workflow, "workflow_id", ""))
    correlation_id = _text(getattr(workflow, "correlation_id", ""))
    values = {
        _text(metadata.get("workflow_id")),
        _text(job_payload.get("workflow_id")),
        _text(metadata.get("correlation_id")),
        _text(job_payload.get("correlation_id")),
    }
    return workflow_id in values or (correlation_id and correlation_id in values)


def _job_stage(payload: Mapping[str, Any], correlation_by_job: Mapping[str, Any]) -> str:
    job_id = _text(payload.get("job_id"))
    correlation = correlation_by_job.get(job_id)
    if correlation is not None:
        stage = _text(getattr(correlation, "stage_id", "") or getattr(correlation, "runtime_stage", ""))
        if stage:
            return stage
    metadata = _mapping(payload.get("metadata"))
    job_payload = _mapping(payload.get("payload"))
    stage = _text(
        metadata.get("stage_id")
        or metadata.get("runtime_stage")
        or job_payload.get("stage_id")
        or job_payload.get("runtime_stage")
    )
    if stage:
        return stage
    job_type = _text(payload.get("job_type"))
    return job_type[:-6] if job_type.endswith("_stage") else job_type


def _job_projection(job: Any, events_reader: Callable[[str], Any]) -> Mapping[str, Any]:
    payload = _mapping(job)
    metadata = _mapping(payload.get("metadata"))
    job_id = _text(payload.get("job_id") or getattr(job, "job_id", ""))
    events = events_reader(job_id) if job_id else ()
    dispatch_result = metadata.get("runtime_dispatch_result")
    attempt = metadata.get("runtime_failure_attempt_count", metadata.get("runtime_attempt_number", 0))
    maximum = metadata.get("runtime_maximum_attempts", 0)
    return _freeze({
        "job_id": job_id,
        "job_type": _text(payload.get("job_type")),
        "status": _status(payload.get("status")),
        "priority": payload.get("priority"),
        "progress_percent": payload.get("progress_percent", 0.0),
        "progress_message": _text(payload.get("progress_message")),
        "assigned_worker_id": payload.get("assigned_worker_id"),
        "created_at": _plain(payload.get("created_at")),
        "started_at": _plain(payload.get("started_at")),
        "completed_at": _plain(payload.get("completed_at")),
        "updated_at": _plain(payload.get("updated_at")),
        "error_message": payload.get("error_message") or metadata.get("runtime_dispatch_error_message"),
        "attempt": attempt,
        "maximum_attempts": maximum,
        "retry_scheduled": bool(metadata.get("runtime_retry_scheduled", False)),
        "retry_exhausted": bool(metadata.get("runtime_retry_exhausted", False)),
        "runtime_dispatch_result_available": dispatch_result is not None,
        "runtime_dispatch_result": _plain(dispatch_result),
        "events": _plain(events),
    })


@dataclass(frozen=True, slots=True)
class PipelineOperationsSnapshot:
    generated_at: str
    pipeline_id: str
    health_status: str
    registrations: tuple[Mapping[str, Any], ...]
    stage_order: tuple[str, ...]
    workflows: tuple[Mapping[str, Any], ...]
    counts: Mapping[str, Any]
    output_readiness: Mapping[str, Any]
    read_only: bool = True
    schema_version: str = PIPELINE_OPERATIONS_SCHEMA_VERSION
    projection_version: str = PIPELINE_OPERATIONS_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "pipeline_id": self.pipeline_id,
            "health_status": self.health_status,
            "registrations": _plain(self.registrations),
            "stage_order": _plain(self.stage_order),
            "workflows": _plain(self.workflows),
            "counts": _plain(self.counts),
            "output_readiness": _plain(self.output_readiness),
            "read_only": self.read_only,
            "schema_version": self.schema_version,
            "projection_version": self.projection_version,
        }


@dataclass(frozen=True, slots=True)
class PipelineOperationsIndex:
    generated_at: str
    pipelines: tuple[Mapping[str, Any], ...]
    read_only: bool = True
    schema_version: str = PIPELINE_OPERATIONS_SCHEMA_VERSION
    projection_version: str = PIPELINE_OPERATIONS_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "pipelines": _plain(self.pipelines),
            "read_only": self.read_only,
            "schema_version": self.schema_version,
            "projection_version": self.projection_version,
        }


def build_pipeline_operations_snapshot(
    *,
    pipeline_id: str,
    workflow_repository: Any,
    registrations_reader: Callable[[], Any] = list_runtime_registrations,
    jobs_reader: Callable[[], Any] = load_jobs,
    events_reader: Callable[[str], Any] = list_job_events,
    correlation_registry: Any = None,
) -> PipelineOperationsSnapshot:
    canonical_pipeline = _pipeline_id(pipeline_id)
    raw_registrations = registrations_reader()
    registrations = tuple(
        _mapping(item) for item in raw_registrations
        if _registration_pipeline(_mapping(item)) == canonical_pipeline
    )
    if not registrations:
        raise PipelineOperationsNotFoundError(
            f"No persisted Runtime registrations exist for pipeline {canonical_pipeline!r}."
        )
    order = _stage_order(registrations)
    registration_by_stage = {_text(item.get("stage")): item for item in registrations}
    registry = correlation_registry or get_workflow_job_correlation_registry()
    jobs_payload = jobs_reader()
    if not isinstance(jobs_payload, Mapping):
        raise PipelineOperationsError("jobs_reader must return a mapping.")
    all_jobs = tuple(jobs_payload.values())
    workflow_rows: list[Mapping[str, Any]] = []
    status_counts: dict[str, int] = {}
    total_jobs = failed_jobs = running_jobs = queued_jobs = 0
    final_outputs_ready = 0
    workflow_ids = workflow_repository.list_workflow_ids()
    for workflow_id in workflow_ids:
        workflow = workflow_repository.load_workflow(workflow_id)
        if not _workflow_matches(workflow, canonical_pipeline):
            continue
        correlations = tuple(registry.all_for_workflow(workflow_id))
        correlation_by_job = {_text(getattr(item, "job_id", "")): item for item in correlations}
        correlated_ids = set(correlation_by_job)
        workflow_jobs = tuple(
            job for job in all_jobs
            if _text(getattr(job, "job_id", "") or _mapping(job).get("job_id")) in correlated_ids
            or _job_matches_workflow(_mapping(job), workflow)
        )
        jobs_by_stage: dict[str, list[Any]] = {stage: [] for stage in order}
        for job in workflow_jobs:
            stage = _job_stage(_mapping(job), correlation_by_job)
            jobs_by_stage.setdefault(stage, []).append(job)
        stages: list[Mapping[str, Any]] = []
        for stage_id in order:
            stage_jobs = tuple(jobs_by_stage.get(stage_id, ()))
            projected_jobs = tuple(_job_projection(job, events_reader) for job in stage_jobs)
            latest = projected_jobs[-1] if projected_jobs else None
            registration = registration_by_stage[stage_id]
            stages.append(_freeze({
                "stage_id": stage_id,
                "job_type": _text(registration.get("job_type")),
                "predecessor_stages": _plain(registration.get("predecessor_stages", ())),
                "successor_stages": _plain(registration.get("successor_stages", ())),
                "persistent_registration": bool(registration.get("persistent", False)),
                "status": latest.get("status") if latest else (
                    "completed" if stage_id in tuple(getattr(workflow, "completed_stages", ()))
                    else "failed" if stage_id in tuple(getattr(workflow, "failed_stages", ()))
                    else "pending"
                ),
                "job_count": len(projected_jobs),
                "jobs": projected_jobs,
                "output_ready": bool(latest and latest.get("runtime_dispatch_result_available")),
            }))
        workflow_status = _status(getattr(workflow, "status", "unknown")) or "unknown"
        status_counts[workflow_status] = status_counts.get(workflow_status, 0) + 1
        job_statuses = [_status(_mapping(job).get("status")) for job in workflow_jobs]
        total_jobs += len(workflow_jobs)
        failed_jobs += sum(value == "failed" for value in job_statuses)
        running_jobs += sum(value == "running" for value in job_statuses)
        queued_jobs += sum(value == "queued" for value in job_statuses)
        final_stage = order[-1] if order else ""
        final_stage_row = next((item for item in stages if item.get("stage_id") == final_stage), None)
        output_ready = bool(final_stage_row and final_stage_row.get("output_ready"))
        final_outputs_ready += int(output_ready)
        workflow_rows.append(_freeze({
            "workflow_id": _text(getattr(workflow, "workflow_id", workflow_id)),
            "correlation_id": _text(getattr(workflow, "correlation_id", "")),
            "workspace_id": _text(getattr(workflow, "workspace_id", "")),
            "status": workflow_status,
            "current_stage": getattr(workflow, "current_stage", None),
            "completed_stages": _plain(getattr(workflow, "completed_stages", ())),
            "pending_stages": _plain(getattr(workflow, "pending_stages", ())),
            "failed_stages": _plain(getattr(workflow, "failed_stages", ())),
            "created_at": getattr(workflow, "created_at", None),
            "updated_at": getattr(workflow, "updated_at", None),
            "job_count": len(workflow_jobs),
            "stage_count": len(stages),
            "output_ready": output_ready,
            "stages": tuple(stages),
        }))
    workflow_rows.sort(key=lambda item: (_text(item.get("updated_at")), _text(item.get("workflow_id"))), reverse=True)
    workflow_count = len(workflow_rows)
    failed_workflows = status_counts.get("failed", 0)
    active_workflows = sum(status_counts.get(value, 0) for value in ("created", "pending", "running", "processing"))
    if failed_workflows or failed_jobs:
        health = "CRITICAL"
    elif workflow_count == 0:
        health = "IDLE"
    elif running_jobs or queued_jobs or active_workflows:
        health = "ACTIVE"
    else:
        health = "HEALTHY"
    return PipelineOperationsSnapshot(
        generated_at=_timestamp(),
        pipeline_id=canonical_pipeline,
        health_status=health,
        registrations=tuple(_freeze(item) for item in registrations),
        stage_order=order,
        workflows=tuple(workflow_rows),
        counts=_freeze({
            "registration_count": len(registrations),
            "workflow_count": workflow_count,
            "active_workflow_count": active_workflows,
            "failed_workflow_count": failed_workflows,
            "job_count": total_jobs,
            "queued_job_count": queued_jobs,
            "running_job_count": running_jobs,
            "failed_job_count": failed_jobs,
        }),
        output_readiness=_freeze({
            "final_stage_id": order[-1] if order else None,
            "ready_workflow_count": final_outputs_ready,
            "all_completed_outputs_ready": bool(
                workflow_count and final_outputs_ready == status_counts.get("completed", 0)
            ),
        }),
    )


def build_pipeline_operations_index(
    *,
    workflow_repository: Any,
    registrations_reader: Callable[[], Any] = list_runtime_registrations,
    jobs_reader: Callable[[], Any] = load_jobs,
    events_reader: Callable[[str], Any] = list_job_events,
    correlation_registry: Any = None,
) -> PipelineOperationsIndex:
    registrations = tuple(_mapping(item) for item in registrations_reader())
    pipeline_ids = tuple(sorted({_registration_pipeline(item) for item in registrations if _registration_pipeline(item)}))
    rows = []
    for pipeline_id in pipeline_ids:
        snapshot = build_pipeline_operations_snapshot(
            pipeline_id=pipeline_id,
            workflow_repository=workflow_repository,
            registrations_reader=lambda records=registrations: records,
            jobs_reader=jobs_reader,
            events_reader=events_reader,
            correlation_registry=correlation_registry,
        )
        rows.append(_freeze({
            "pipeline_id": snapshot.pipeline_id,
            "health_status": snapshot.health_status,
            "stage_order": snapshot.stage_order,
            "counts": snapshot.counts,
            "output_readiness": snapshot.output_readiness,
        }))
    return PipelineOperationsIndex(generated_at=_timestamp(), pipelines=tuple(rows))


__all__ = [
    "PIPELINE_OPERATIONS_VERSION",
    "PIPELINE_OPERATIONS_SCHEMA_VERSION",
    "PipelineOperationsError",
    "PipelineOperationsNotFoundError",
    "PipelineOperationsSnapshot",
    "PipelineOperationsIndex",
    "build_pipeline_operations_snapshot",
    "build_pipeline_operations_index",
]
'''


API_IMPORT_ANCHOR = "from fastapi import APIRouter, HTTPException, Request\n"
API_IMPORT_PATCH = '''from fastapi import APIRouter, HTTPException, Request

from backend.server.owner.pipeline_operations import (
    PipelineOperationsNotFoundError,
    build_pipeline_operations_index,
    build_pipeline_operations_snapshot,
)
'''

API_ROUTE_ANCHOR = '''    return dict(summary)


'''

API_ROUTE_PATCH = '''    return dict(summary)


def _pipeline_operations_repository(request: Request) -> Any:
    repository = getattr(
        request.app.state,
        "runtime_coordination_workflow_repository",
        None,
    )
    if repository is None:
        gateway = getattr(
            request.app.state,
            "runtime_coordination_gateway",
            None,
        )
        repository = getattr(gateway, "workflow_repository", None)
    if repository is None:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "runtime_pipeline_operations_repository_unavailable",
                "message": "The canonical Runtime workflow repository is unavailable.",
                "read_only": True,
            },
        )
    return repository


@router.get("/pipelines")
async def runtime_pipeline_operations_index(
    request: Request,
) -> Mapping[str, Any]:
    """List read-only operations summaries for every registered pipeline."""
    try:
        result = build_pipeline_operations_index(
            workflow_repository=_pipeline_operations_repository(request),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "runtime_pipeline_operations_unavailable",
                "message": str(exc),
                "read_only": True,
            },
        ) from exc
    return result.to_dict()


@router.get("/pipelines/{pipeline_id}")
async def runtime_pipeline_operations_detail(
    pipeline_id: str,
    request: Request,
) -> Mapping[str, Any]:
    """Read one registered pipeline's workflows, stages, jobs and evidence."""
    try:
        result = build_pipeline_operations_snapshot(
            pipeline_id=pipeline_id,
            workflow_repository=_pipeline_operations_repository(request),
        )
    except PipelineOperationsNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "runtime_pipeline_not_found",
                "message": str(exc),
                "read_only": True,
            },
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "runtime_pipeline_operations_unavailable",
                "message": str(exc),
                "read_only": True,
            },
        ) from exc
    return result.to_dict()


'''


EXPECTED_API_HASH = "8a0df4c763a13922cb33108b799e9756e6efd7d3732314e2f45ae4ae065f1d3c"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def parse_report(path: Path, required: str) -> bool:
    return path.is_file() and required in path.read_text(encoding="utf-8-sig")


def freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(k): freeze(v) for k, v in value.items()})
    if isinstance(value, (list, tuple, set, frozenset)):
        return tuple(freeze(v) for v in value)
    return value


def render_report(*, status: str, checks: dict[str, bool], evidence: dict[str, Any], error: dict[str, Any], backup: str) -> str:
    failed = [name for name, passed in checks.items() if not passed]
    return f'''LINKCRAFTOR CONNECTED DOMAIN OWNER OPERATIONS
PART F 15-B3 UNIVERSAL PIPELINE OPERATIONS BACKEND CERTIFICATION

Generated: {datetime.now(timezone.utc).isoformat()}
Patch mode: STRICT FAIL-CLOSED
Backup: {backup}
Production jobs created: NO
Production queue claims executed: NO
Production handlers executed: NO
Production workflow persistence executed: NO
Production recovery actions executed: NO
Live network requests executed: NO
CERTIFICATION STATUS: {status}

CHECKS:
{json.dumps(checks, indent=2, sort_keys=True)}

FAILED_CHECKS:
{json.dumps(failed, indent=2)}

NOT_RUN_CHECKS:
[]

EVIDENCE:
{json.dumps(evidence, indent=2, sort_keys=True, default=str)}

EXECUTION_ERROR:
{json.dumps(error, indent=2, default=str)}

IMPLEMENTED BOUNDARY:
- One read-only universal Pipeline Operations projection now exists under the existing Runtime Owner API.
- GET /owner/api/runtime/pipelines lists every pipeline represented by persisted Runtime registrations.
- GET /owner/api/runtime/pipelines/{{pipeline_id}} returns workflow, stage, job, retry, event, failure and output-readiness evidence.
- Connected Domain is the first certified six-stage pipeline; future registered pipelines use the same projection.
- Existing job store, workflow repository, correlation registry and Runtime registration authority are reused.
- No second Runtime, queue, job store, registry, workflow repository or recovery authority was created.
- Control Tower presentation remains Part F 15-B4; recovery mutations remain Part F 15-C.

FINAL RESULT:
FINAL RESULT: PART F 15-B3 UNIVERSAL PIPELINE OPERATIONS BACKEND {status}
'''


def main(root: Path, report: Path) -> int:
    root = root.resolve()
    api = root / "backend/server/owner/runtime_summary_api.py"
    module = root / "backend/server/owner/pipeline_operations.py"
    reports = root / "backend/server/data/reports"
    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {}
    error: dict[str, Any] = {}
    backup_dir: Path | None = None
    api_original: bytes | None = None
    module_existed = module.exists()
    module_original = module.read_bytes() if module_existed else None
    retained = False
    try:
        checks["part_f_15_a_complete"] = parse_report(
            reports / "PART_F_15_A_MONITORING_RECOVERY_BOUNDARY_INSPECTION.txt",
            "PART F 15-A COMPLETE",
        )
        checks["part_f_15_b2_certified"] = parse_report(
            reports / "PART_F_15_B2_CORRECTED_UNIVERSAL_RUNTIME_OVERVIEW_CONNECTION_CLOSURE.txt",
            "PART F 15-B2 UNIVERSAL RUNTIME OVERVIEW CONNECTION CERTIFIED",
        )
        checks["implementation_contract_complete"] = parse_report(
            reports / "PART_F_15_B3_UNIVERSAL_PIPELINE_OPERATIONS_IMPLEMENTATION_CONTRACT.txt",
            "PART F 15-B3 IMPLEMENTATION CONTRACT COMPLETE",
        )
        checks["api_exists"] = api.is_file()
        checks["api_precondition_hash"] = checks["api_exists"] and sha256(api) == EXPECTED_API_HASH
        checks["pipeline_operations_previously_absent"] = not module_existed
        checks["api_boundary_previously_absent"] = checks["api_exists"] and "runtime_pipeline_operations_detail" not in api.read_text(encoding="utf-8-sig")
        if not all(checks.values()):
            raise RuntimeError("Part F 15-B3 precondition gate failed.")

        source = api.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        if source.count(API_IMPORT_ANCHOR) != 1:
            raise RuntimeError("Runtime Owner API import anchor is not unique.")
        if source.count(API_ROUTE_ANCHOR) != 1:
            raise RuntimeError("Runtime Owner API route anchor is not unique.")
        api_candidate = source.replace(API_IMPORT_ANCHOR, API_IMPORT_PATCH, 1).replace(API_ROUTE_ANCHOR, API_ROUTE_PATCH, 1)

        with tempfile.TemporaryDirectory(prefix="linkcraftor_part_f_15_b3_candidate_") as temp:
            temp_root = Path(temp)
            candidate_module = temp_root / "pipeline_operations.py"
            candidate_api = temp_root / "runtime_summary_api.py"
            write_text(candidate_module, PIPELINE_OPERATIONS_SOURCE)
            write_text(candidate_api, api_candidate)
            py_compile.compile(str(candidate_module), doraise=True)
            py_compile.compile(str(candidate_api), doraise=True)
        checks["candidate_syntax"] = True

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup_dir = root / "backend/server/data/runtime_backups" / f"part_f_15_b3_{stamp}"
        backup_dir.mkdir(parents=True, exist_ok=False)
        shutil.copy2(api, backup_dir / api.name)
        api_original = api.read_bytes()
        write_text(module, PIPELINE_OPERATIONS_SOURCE)
        write_text(api, api_candidate)
        py_compile.compile(str(module), doraise=True)
        py_compile.compile(str(api), doraise=True)
        checks["production_source_syntax"] = True

        importlib.invalidate_caches()
        sys.path.insert(0, str(root)) if str(root) not in sys.path else None
        operations = importlib.import_module("backend.server.owner.pipeline_operations")
        api_module = importlib.reload(importlib.import_module("backend.server.owner.runtime_summary_api"))

        registrations = (
            {"job_type": "connect_domain_stage", "pipeline": "connect_domain", "stage": "connect_domain", "predecessor_stages": (), "successor_stages": ("site_sources",), "persistent": True},
            {"job_type": "site_sources_stage", "pipeline": "connect_domain", "stage": "site_sources", "predecessor_stages": ("connect_domain",), "successor_stages": ("url_cleaner",), "persistent": True},
            {"job_type": "url_cleaner_stage", "pipeline": "connect_domain", "stage": "url_cleaner", "predecessor_stages": ("site_sources",), "successor_stages": ("site_pages",), "persistent": True},
            {"job_type": "site_pages_stage", "pipeline": "connect_domain", "stage": "site_pages", "predecessor_stages": ("url_cleaner",), "successor_stages": ("live_domain_target_pool",), "persistent": True},
            {"job_type": "live_domain_target_pool_stage", "pipeline": "connect_domain", "stage": "live_domain_target_pool", "predecessor_stages": ("site_pages",), "successor_stages": ("active_target_set",), "persistent": True},
            {"job_type": "active_target_set_stage", "pipeline": "connect_domain", "stage": "active_target_set", "predecessor_stages": ("live_domain_target_pool",), "successor_stages": (), "persistent": True},
            {"job_type": "future_stage", "pipeline": "future_pipeline", "stage": "future", "predecessor_stages": (), "successor_stages": (), "persistent": True},
        )
        workflow = SimpleNamespace(
            workflow_id="workflow_part_f_15_b3_probe",
            workflow_type="connect_domain",
            workspace_id="ws_part_f_15_b3_probe",
            correlation_id="correlation_part_f_15_b3_probe",
            status=SimpleNamespace(value="completed"),
            current_stage="active_target_set",
            completed_stages=tuple(item["stage"] for item in registrations[:6]),
            pending_stages=(), failed_stages=(), created_at="2026-10-24T18:00:00Z", updated_at="2026-10-24T18:06:00Z",
            metadata={"pipeline_id": "connect_domain"},
        )
        class Repository:
            def list_workflow_ids(self): return (workflow.workflow_id,)
            def load_workflow(self, workflow_id):
                if workflow_id != workflow.workflow_id: raise KeyError(workflow_id)
                return workflow
        correlations = tuple(
            SimpleNamespace(
                workflow_id=workflow.workflow_id,
                correlation_id=workflow.correlation_id,
                stage_id=registration["stage"],
                runtime_stage=registration["stage"],
                job_id=f"job_{registration['stage']}",
            ) for registration in registrations[:6]
        )
        class Registry:
            def all_for_workflow(self, workflow_id): return correlations if workflow_id == workflow.workflow_id else ()
        jobs = {}
        events = {}
        for index, registration in enumerate(registrations[:6]):
            stage = registration["stage"]
            job_id = f"job_{stage}"
            jobs[job_id] = SimpleNamespace(
                job_id=job_id, workspace_id=workflow.workspace_id,
                job_type=registration["job_type"], status="completed", priority=5,
                progress_percent=100.0, progress_message="Completed", assigned_worker_id="isolated_worker",
                created_at=f"2026-10-24T18:0{index}:00Z", started_at=f"2026-10-24T18:0{index}:01Z",
                completed_at=f"2026-10-24T18:0{index}:02Z", updated_at=f"2026-10-24T18:0{index}:02Z",
                error_message=None, payload={"workflow_id": workflow.workflow_id, "stage_id": stage},
                metadata={"workflow_id": workflow.workflow_id, "correlation_id": workflow.correlation_id,
                          "runtime_dispatch_result": {"stage_id": stage, "ok": True},
                          "runtime_failure_attempt_count": 1, "runtime_maximum_attempts": 3},
            )
            events[job_id] = ({"old_status": "running", "new_status": "completed"},)

        snapshot = operations.build_pipeline_operations_snapshot(
            pipeline_id="connect_domain", workflow_repository=Repository(),
            registrations_reader=lambda: registrations, jobs_reader=lambda: jobs,
            events_reader=lambda job_id: events.get(job_id, ()), correlation_registry=Registry(),
        )
        snapshot_payload = snapshot.to_dict()
        index = operations.build_pipeline_operations_index(
            workflow_repository=Repository(), registrations_reader=lambda: registrations,
            jobs_reader=lambda: jobs, events_reader=lambda job_id: events.get(job_id, ()),
            correlation_registry=Registry(),
        )
        index_payload = index.to_dict()
        checks["snapshot_dataclass_frozen_slotted"] = (
            hasattr(snapshot, "__dataclass_fields__") and snapshot.__dataclass_params__.frozen and hasattr(type(snapshot), "__slots__")
        )
        checks["six_stage_order_preserved"] = snapshot.stage_order == tuple(item["stage"] for item in registrations[:6])
        checks["six_jobs_projected"] = snapshot_payload["counts"]["job_count"] == 6
        checks["workflow_identity_preserved"] = snapshot_payload["workflows"][0]["workflow_id"] == workflow.workflow_id
        checks["correlation_identity_preserved"] = snapshot_payload["workflows"][0]["correlation_id"] == workflow.correlation_id
        checks["job_events_projected"] = all(row["jobs"][0]["events"] for row in snapshot_payload["workflows"][0]["stages"])
        checks["retry_evidence_projected"] = all(row["jobs"][0]["maximum_attempts"] == 3 for row in snapshot_payload["workflows"][0]["stages"])
        checks["output_readiness_projected"] = snapshot_payload["workflows"][0]["output_ready"] is True
        checks["future_pipeline_discovered"] = {row["pipeline_id"] for row in index_payload["pipelines"]} == {"connect_domain", "future_pipeline"}
        checks["nested_snapshot_immutable"] = isinstance(snapshot.counts, MappingProxyType) and isinstance(snapshot.workflows[0], MappingProxyType)
        checks["api_index_declared"] = callable(api_module.runtime_pipeline_operations_index)
        checks["api_detail_declared"] = callable(api_module.runtime_pipeline_operations_detail)
        routes = {(route.path, tuple(sorted(route.methods or ()))) for route in api_module.router.routes}
        checks["canonical_api_routes_declared"] = (
            ("/owner/api/runtime/pipelines", ("GET",)) in routes
            and ("/owner/api/runtime/pipelines/{pipeline_id}", ("GET",)) in routes
        )
        checks["unknown_pipeline_rejected"] = False
        try:
            operations.build_pipeline_operations_snapshot(
                pipeline_id="missing", workflow_repository=Repository(),
                registrations_reader=lambda: registrations, jobs_reader=lambda: {},
                correlation_registry=Registry(),
            )
        except operations.PipelineOperationsNotFoundError:
            checks["unknown_pipeline_rejected"] = True
        checks["no_mutation_operations_exposed"] = all(
            token not in PIPELINE_OPERATIONS_SOURCE for token in (
                "create_job(", "save_workflow(", "claim", "dispatch_registered_runtime_handler(", "cancel_job(", "retry_job("
            )
        )
        checks["existing_runtime_router_reused"] = api_module.router.prefix == "/owner/api/runtime"
        checks["source_stable_during_verification"] = sha256(module) == hashlib.sha256(PIPELINE_OPERATIONS_SOURCE.encode("utf-8")).hexdigest()

        if not all(checks.values()):
            raise RuntimeError("Part F 15-B3 certification checks failed.")
        evidence = {
            "api_target": str(api), "operations_target": str(module),
            "api_sha256": sha256(api), "operations_sha256": sha256(module),
            "endpoints": ["/owner/api/runtime/pipelines", "/owner/api/runtime/pipelines/{pipeline_id}"],
            "connected_domain_stage_order": list(snapshot.stage_order),
            "connected_domain_counts": snapshot_payload["counts"],
            "connected_domain_output_readiness": snapshot_payload["output_readiness"],
            "discovered_pipeline_ids": [row["pipeline_id"] for row in index_payload["pipelines"]],
            "production_side_effects": {"jobs_created": False, "queues_claimed": False, "handlers_executed": False,
                                           "workflow_persisted": False, "recovery_executed": False, "network_requests": False},
        }
        retained = True
        status = "CERTIFIED"
    except Exception as exc:
        error = {"error_type": type(exc).__name__, "error_message": str(exc), "traceback": traceback.format_exc()}
        status = "NOT_CERTIFIED"
    finally:
        if not retained:
            if api_original is not None:
                api.write_bytes(api_original)
            if module_existed and module_original is not None:
                module.write_bytes(module_original)
            elif module.exists():
                module.unlink()
        report.parent.mkdir(parents=True, exist_ok=True)
        write_text(report, render_report(
            status=status, checks=checks, evidence=evidence, error=error,
            backup=str(backup_dir) if backup_dir else "NOT_CREATED",
        ))
    for name, passed in checks.items():
        print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(f"FAILED_CHECK_COUNT={sum(not value for value in checks.values())}")
    print(f"REPORT={report}")
    print(f"PART_F_15_B3_STATUS={status}")
    return 0 if status == "CERTIFIED" else 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: _build_part_f_15_b3.py PROJECT_ROOT REPORT_PATH")
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
