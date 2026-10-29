"""Read-only universal per-pipeline Runtime operations projection.

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
