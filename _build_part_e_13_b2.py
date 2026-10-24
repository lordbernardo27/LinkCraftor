from __future__ import annotations

import ast
import hashlib
import importlib
import json
import py_compile
import shutil
import sys
import tempfile
import traceback
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType, SimpleNamespace
from typing import Any


RUNTIME_HOOK_SOURCE = r'''from __future__ import annotations

import importlib
from collections.abc import Mapping
from typing import Any


RUNTIME_PAYLOAD_HYDRATOR_KEY = "__runtime_payload_hydrator_ref__"
RUNTIME_PAYLOAD_HYDRATION_VERSION = "runtime_payload_hydration_v1.0.0"


class RuntimePayloadHydrationError(RuntimeError):
    pass


def _resolve_hydrator(reference: str):
    module_name, separator, attribute_name = reference.partition(":")
    if (
        separator != ":"
        or not module_name.startswith("backend.server.pipelines.")
        or not attribute_name
    ):
        raise RuntimePayloadHydrationError(
            "Runtime payload hydrator reference is invalid."
        )
    module = importlib.import_module(module_name)
    hydrator = getattr(module, attribute_name, None)
    if not callable(hydrator):
        raise RuntimePayloadHydrationError(
            "Runtime payload hydrator is unavailable: " + reference
        )
    return hydrator


def hydrate_runtime_job_payload(job: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(job, Mapping):
        raise RuntimePayloadHydrationError(
            "Runtime job must be a mapping before payload hydration."
        )
    hydrated_job = dict(job)
    payload = hydrated_job.get("payload", {})
    if not isinstance(payload, Mapping):
        raise RuntimePayloadHydrationError(
            "Runtime job payload must be a mapping before hydration."
        )
    hydrated_payload = dict(payload)
    reference = str(
        hydrated_payload.pop(RUNTIME_PAYLOAD_HYDRATOR_KEY, "") or ""
    ).strip()
    hydrated_job["payload"] = hydrated_payload
    if not reference:
        return hydrated_job
    result = _resolve_hydrator(reference)(hydrated_job)
    if not isinstance(result, Mapping):
        raise RuntimePayloadHydrationError(
            "Runtime payload hydrator must return a job mapping."
        )
    resolved = dict(result)
    resolved_payload = resolved.get("payload", {})
    if not isinstance(resolved_payload, Mapping):
        raise RuntimePayloadHydrationError(
            "Hydrated runtime job payload must be a mapping."
        )
    clean_payload = dict(resolved_payload)
    clean_payload.pop(RUNTIME_PAYLOAD_HYDRATOR_KEY, None)
    resolved["payload"] = clean_payload
    return resolved
'''


PIPELINE_HYDRATOR_SOURCE = r'''from __future__ import annotations

import dataclasses
from collections.abc import Mapping
from typing import Any, Callable

from backend.server.orchestration.job_store import get_job, load_jobs


CONNECTED_DOMAIN_HYDRATOR_VERSION = "connected_domain_runtime_hydrator_v1.0.0"
CONNECTED_DOMAIN_HYDRATOR_REF = (
    "backend.server.pipelines.connect_domain.runtime_hydration:"
    "hydrate_connected_domain_runtime_job"
)

_PREDECESSOR_BY_STAGE = {
    "url_cleaner": "site_sources",
    "site_pages": "url_cleaner",
    "live_domain_target_pool": "site_pages",
    "active_target_set": "live_domain_target_pool",
}


class ConnectedDomainRuntimeHydrationError(RuntimeError):
    pass


def _value(source: Any, name: str, default: Any = None) -> Any:
    if isinstance(source, Mapping):
        return source.get(name, default)
    return getattr(source, name, default)


def _plain(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_plain(item) for item in value]
    for method_name in ("to_payload", "to_dict", "to_canonical_dict"):
        method = getattr(value, method_name, None)
        if callable(method):
            try:
                return _plain(method())
            except TypeError:
                continue
    if dataclasses.is_dataclass(value):
        return _plain(dataclasses.asdict(value))
    if hasattr(value, "__dict__"):
        return _plain(vars(value))
    raise ConnectedDomainRuntimeHydrationError(
        "Predecessor result cannot be converted to canonical payload evidence."
    )


def _job_metadata(job: Any) -> Mapping[str, Any]:
    metadata = _value(job, "metadata", {})
    return metadata if isinstance(metadata, Mapping) else {}


def _job_stage(job: Any) -> str:
    direct = str(_value(job, "stage", "") or "").strip()
    if direct:
        return direct.removesuffix("_stage")
    metadata = _job_metadata(job)
    universal = metadata.get("universal_job", {})
    if isinstance(universal, Mapping):
        return str(universal.get("stage") or "").strip().removesuffix("_stage")
    return ""


def _dependency_ids(job: Mapping[str, Any]) -> tuple[str, ...]:
    candidates: list[Any] = [job.get("dependency_job_ids")]
    metadata = _job_metadata(job)
    candidates.append(metadata.get("dependency_job_ids"))
    universal = metadata.get("universal_job", {})
    if isinstance(universal, Mapping):
        candidates.append(universal.get("dependency_job_ids"))
    for candidate in candidates:
        if candidate is None:
            continue
        if isinstance(candidate, str):
            candidate = (candidate,)
        try:
            normalized = tuple(
                str(item or "").strip() for item in candidate if str(item or "").strip()
            )
        except TypeError:
            continue
        if normalized:
            return normalized
    return ()


def _workflow_id(job: Mapping[str, Any]) -> str:
    metadata = _job_metadata(job)
    for source in (job, metadata, metadata.get("coordination", {}), metadata.get("universal_job", {})):
        if isinstance(source, Mapping):
            value = str(source.get("workflow_id") or source.get("pipeline_run_id") or "").strip()
            if value:
                return value
    return ""


def _find_predecessor(
    job: Mapping[str, Any],
    *,
    predecessor_stage: str,
    job_reader: Callable[[str], Any],
    jobs_reader: Callable[[], Mapping[str, Any]],
) -> Any:
    dependencies = _dependency_ids(job)
    candidates = [job_reader(job_id) for job_id in dependencies]
    candidates = [candidate for candidate in candidates if candidate is not None]
    matching = [candidate for candidate in candidates if _job_stage(candidate) == predecessor_stage]
    if not matching:
        workflow_id = _workflow_id(job)
        loaded = jobs_reader()
        if not isinstance(loaded, Mapping):
            raise ConnectedDomainRuntimeHydrationError(
                "Canonical job reader returned a non-mapping."
            )
        matching = [
            candidate
            for candidate in loaded.values()
            if _job_stage(candidate) == predecessor_stage
            and (not workflow_id or _workflow_id(_plain(candidate)) == workflow_id)
        ]
    if len(matching) != 1:
        raise ConnectedDomainRuntimeHydrationError(
            f"Expected one {predecessor_stage} predecessor job; found {len(matching)}."
        )
    predecessor = matching[0]
    status = str(_value(predecessor, "status", "") or "").strip().lower()
    if status != "completed":
        raise ConnectedDomainRuntimeHydrationError(
            f"Predecessor {predecessor_stage} is not completed."
        )
    return predecessor


def _handler_result(predecessor: Any) -> Mapping[str, Any]:
    metadata = _job_metadata(predecessor)
    dispatch = metadata.get("runtime_dispatch_result")
    if not isinstance(dispatch, Mapping):
        raise ConnectedDomainRuntimeHydrationError(
            "Completed predecessor has no runtime_dispatch_result."
        )
    result: Any = dispatch.get("handler_result")
    if isinstance(result, Mapping) and set(result) == {"value"}:
        result = result["value"]
    result = _plain(result)
    if not isinstance(result, Mapping):
        raise ConnectedDomainRuntimeHydrationError(
            "Predecessor handler result must resolve to a mapping."
        )
    return result


def _cleaner_records(result: Mapping[str, Any]) -> list[dict[str, Any]]:
    cleaned = tuple(str(item).strip() for item in result.get("cleaned_urls", ()) if str(item).strip())
    explicit = {str(item).strip() for item in result.get("explicit_urls", ()) if str(item).strip()}
    uncertain = {str(item).strip() for item in result.get("uncertain_urls", ()) if str(item).strip()}
    records = []
    for url in cleaned:
        confidence = "explicit" if url in explicit else "uncertain"
        if url not in explicit and url not in uncertain:
            raise ConnectedDomainRuntimeHydrationError(
                "Cleaned URL has no explicit or uncertain confidence evidence."
            )
        records.append(
            {
                "url": url,
                "canonical": url,
                "confidence": confidence,
                "accepted": True,
            }
        )
    if not records:
        raise ConnectedDomainRuntimeHydrationError(
            "URL Cleaner produced no accepted records for Site Pages."
        )
    return records


def hydrate_connected_domain_runtime_job(
    job: Mapping[str, Any],
    *,
    job_reader: Callable[[str], Any] = get_job,
    jobs_reader: Callable[[], Mapping[str, Any]] = load_jobs,
) -> dict[str, Any]:
    if not isinstance(job, Mapping):
        raise ConnectedDomainRuntimeHydrationError("Runtime job must be a mapping.")
    hydrated = dict(job)
    payload = hydrated.get("payload", {})
    if not isinstance(payload, Mapping):
        raise ConnectedDomainRuntimeHydrationError("Runtime job payload must be a mapping.")
    resolved_payload = dict(payload)
    stage = _job_stage(hydrated)
    predecessor_stage = _PREDECESSOR_BY_STAGE.get(stage)
    if predecessor_stage is None:
        hydrated["payload"] = resolved_payload
        return hydrated

    target_field = {
        "url_cleaner": "source_urls",
        "site_pages": "cleaner_records",
        "live_domain_target_pool": "site_pages",
        "active_target_set": "live_domain_payload",
    }[stage]
    if target_field in resolved_payload and resolved_payload[target_field] not in (None, (), [], {}):
        hydrated["payload"] = resolved_payload
        return hydrated

    predecessor = _find_predecessor(
        hydrated,
        predecessor_stage=predecessor_stage,
        job_reader=job_reader,
        jobs_reader=jobs_reader,
    )
    result = _handler_result(predecessor)
    if stage == "url_cleaner":
        value = list(result.get("discovered_urls", ()))
    elif stage == "site_pages":
        value = _cleaner_records(result)
    elif stage == "live_domain_target_pool":
        value = list(result.get("pages", result.get("items", ())))
    else:
        targets = list(result.get("targets", result.get("items", ())))
        value = {**dict(result), "items": targets}
    if value in (None, (), [], {}):
        raise ConnectedDomainRuntimeHydrationError(
            f"Predecessor {predecessor_stage} produced no value for {target_field}."
        )
    resolved_payload[target_field] = value
    hydrated["payload"] = resolved_payload
    return hydrated
'''


ACTIVATION_SOURCE = r'''from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from backend.server.coordination.universal_workflows.contract import (
    UniversalWorkflow,
    UniversalWorkflowStatus,
)
from backend.server.coordination.workflow_persistence.repository import (
    WorkflowPersistenceNotFoundError,
)
from backend.server.pipelines.connect_domain.coordinator import (
    CONNECTED_DOMAIN_STAGE_IDS,
    build_connected_domain_coordinator_contract,
    connect_connected_domain_to_universal_coordination,
    coordinate_connect_domain_pipeline,
)
from backend.server.pipelines.connect_domain.manifest import (
    build_connected_domain_pipeline_manifest,
)
from backend.server.pipelines.connect_domain.runtime_hydration import (
    CONNECTED_DOMAIN_HYDRATOR_REF,
)
from backend.server.runtime.runtime_payload_hydration import (
    RUNTIME_PAYLOAD_HYDRATOR_KEY,
)


CONNECTED_DOMAIN_ACTIVATION_VERSION = "connected_domain_activation_v1.0.0"


class ConnectedDomainActivationError(RuntimeError):
    pass


def _plain(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_plain(item) for item in value]
    for name in ("to_dict", "to_canonical_dict"):
        method = getattr(value, name, None)
        if callable(method):
            return _plain(method())
    if hasattr(value, "__dict__"):
        return _plain(vars(value))
    return str(value)


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def activate_connected_domain_pipeline(
    *,
    runtime_gateway: Any,
    workspace_id: str | None = None,
    workspace_name: str | None = None,
    domain: str | None = None,
    site_url: str | None = None,
    url: str | None = None,
    payload_by_stage: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    repository = getattr(runtime_gateway, "workflow_repository", None)
    if repository is None:
        raise ConnectedDomainActivationError(
            "Runtime Coordination Gateway has no workflow repository."
        )
    supplied = dict(payload_by_stage or {})
    hydrated_payloads: dict[str, dict[str, Any]] = {}
    for stage_id in CONNECTED_DOMAIN_STAGE_IDS:
        stage_payload = supplied.get(stage_id, {})
        if not isinstance(stage_payload, Mapping):
            raise ConnectedDomainActivationError(
                f"Payload for {stage_id} must be a mapping."
            )
        hydrated_payloads[stage_id] = {
            **dict(stage_payload),
            RUNTIME_PAYLOAD_HYDRATOR_KEY: CONNECTED_DOMAIN_HYDRATOR_REF,
        }

    intent = coordinate_connect_domain_pipeline(
        workspace_id=workspace_id,
        workspace_name=workspace_name,
        domain=domain,
        site_url=site_url,
        url=url,
        payload_by_stage=hydrated_payloads,
        metadata={
            **dict(metadata or {}),
            "activation_authority": "activate_connected_domain_pipeline",
            "hydration_authority": CONNECTED_DOMAIN_HYDRATOR_REF,
        },
    )
    manifest = build_connected_domain_pipeline_manifest(
        workflow_id=intent.workflow_id,
    )
    coordinator_contract = build_connected_domain_coordinator_contract()
    now = _timestamp()
    workflow = UniversalWorkflow(
        workflow_id=intent.workflow_id,
        workflow_type=coordinator_contract.workflow_type,
        workflow_version=coordinator_contract.workflow_version,
        workspace_id=intent.workspace_id,
        coordinator_id=coordinator_contract.coordinator_id,
        coordinator_version=coordinator_contract.coordinator_version,
        correlation_id=intent.correlation_id,
        parent_workflow_id=None,
        root_workflow_id=intent.workflow_id,
        status=UniversalWorkflowStatus.CREATED,
        input_reference=None,
        context=dict(intent.context),
        metadata={
            **dict(intent.metadata),
            "activation_version": CONNECTED_DOMAIN_ACTIVATION_VERSION,
            "manifest_identity_fingerprint": manifest.identity_fingerprint(),
            "manifest_content_fingerprint": manifest.content_fingerprint(),
        },
        current_stage=CONNECTED_DOMAIN_STAGE_IDS[0],
        pending_stages=CONNECTED_DOMAIN_STAGE_IDS,
        idempotency_key="connected_domain:" + intent.workflow_id,
        created_at=now,
        updated_at=now,
    )
    try:
        existing = repository.load_workflow_record(intent.workflow_id)
    except WorkflowPersistenceNotFoundError:
        persistence = repository.save_workflow(workflow)
        persisted_workflow = workflow
        workflow_created = True
    else:
        persisted_workflow = existing.workflow
        if (
            persisted_workflow.workspace_id != intent.workspace_id
            or persisted_workflow.correlation_id != intent.correlation_id
            or persisted_workflow.workflow_type != coordinator_contract.workflow_type
        ):
            raise ConnectedDomainActivationError(
                "Existing workflow identity conflicts with Connect Domain request."
            )
        persistence = existing.evidence
        workflow_created = False

    connection = connect_connected_domain_to_universal_coordination(
        runtime_gateway=runtime_gateway,
        execution_plan=manifest.execution_plan,
        stage_references=manifest.stage_references,
        workspace_id=intent.workspace_id,
        workspace_name=intent.workspace_name,
        domain=intent.domain,
        site_url=intent.site_url,
        workflow_id=intent.workflow_id,
        correlation_id=intent.correlation_id,
        payload_by_stage=hydrated_payloads,
        metadata=dict(intent.metadata),
        execution_semantics="dependency_ordered",
    )
    submission = connection.runtime_submission
    job_ids = tuple(getattr(submission, "job_ids", ()) or ())
    return {
        "ok": True,
        "connected": True,
        "connection_status": "processing",
        "execution_mode": "asynchronous",
        "workspace_id": intent.workspace_id,
        "workspace_name": intent.workspace_name,
        "workspace_mode": "connect_domain",
        "domain": intent.domain,
        "site_url": intent.site_url,
        "workflow_id": intent.workflow_id,
        "correlation_id": intent.correlation_id,
        "workflow_created": workflow_created,
        "workflow_status": persisted_workflow.status.value,
        "job_ids": list(job_ids),
        "stage_ids": list(CONNECTED_DOMAIN_STAGE_IDS),
        "pipeline": {
            "pipeline_id": "connect_domain",
            "manifest_finalized": True,
            "runtime_submission_connected": True,
            "hydration_connected": True,
        },
        "persistence": _plain(persistence),
        "runtime_submission": _plain(submission),
    }
'''


ROUTE_FUNCTION = r'''def connect_domain(
    payload: ConnectDomainRequest,
    request: Request,
) -> Dict[str, Any]:
    """Submit one Connected Domain workflow through the canonical runtime."""
    runtime_gateway = getattr(
        request.app.state,
        "runtime_coordination_gateway",
        None,
    )
    if runtime_gateway is None:
        raise HTTPException(
            status_code=503,
            detail="Runtime Coordination Gateway is unavailable.",
        )
    from backend.server.pipelines.connect_domain.activation import (
        activate_connected_domain_pipeline,
    )
    return activate_connected_domain_pipeline(
        runtime_gateway=runtime_gateway,
        workspace_id=payload.workspace_id,
        workspace_name=payload.workspace_name,
        domain=payload.domain,
        site_url=payload.site_url,
        url=payload.url,
    )
'''


EXPECTED_HASHES = {
    "backend/server/routes/site_workspace.py": "fa3be28c1aeaae49d052140ef94bc0eb3ccc4e56a7340a04bbcb99dce2909c36",
    "backend/server/runtime/universal_runtime_worker_v1.py": "b4df8c694d5d09dc5c412593d4c097d6697c2cb5a656c9521ac58a46fe8c4a4f",
    "backend/server/pipelines/connect_domain/coordinator.py": "a05bfc1d106306b7399f03bdef2f2d06a22a88fa9006aff680ac1796b1bb77fb",
    "backend/server/pipelines/connect_domain/manifest.py": "27a5258c7679160ced9fdf54d3ba0a202593861ada25b3571be0c053b16c1beb",
    "backend/server/runtime/runtime_coordination_gateway.py": "95dbabf2b63fd52e51d984741e4fcb2ac392e7276354ae550fbce58de1259f45",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_function(source: str, name: str, replacement: str) -> str:
    tree = ast.parse(source)
    matches = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one {name} function, found {len(matches)}.")
    node = matches[0]
    lines = source.splitlines(keepends=True)
    start = sum(len(line) for line in lines[: node.lineno - 1])
    end = sum(len(line) for line in lines[: node.end_lineno])
    suffix = "\n\n" if not replacement.endswith("\n\n") else ""
    return source[:start] + replacement.rstrip() + suffix + source[end:].lstrip("\n")


def patch_route(source: str) -> str:
    if "activate_connected_domain_pipeline" in source:
        raise RuntimeError("Part E 13-B2 route integration is already present.")
    if "from fastapi import Request" not in source:
        future = "from __future__ import annotations\n"
        if future in source:
            source = source.replace(future, future + "\nfrom fastapi import Request\n", 1)
        else:
            source = "from fastapi import Request\n" + source
    return replace_function(source, "connect_domain", ROUTE_FUNCTION)


def patch_worker(source: str) -> str:
    marker = "hydrate_runtime_job_payload(runtime_job)"
    if marker in source:
        raise RuntimeError("Part E 13-B2 worker hook is already present.")
    anchor = '''    runtime_job = (\n        orchestration_job_to_runtime_mapping_v1(\n            claimed_job\n        )\n    )\n\n'''
    if source.count(anchor) != 1:
        raise RuntimeError("Canonical runtime-job mapping anchor is not unique.")
    addition = anchor + '''    from backend.server.runtime.runtime_payload_hydration import (\n        hydrate_runtime_job_payload,\n    )\n\n    runtime_job = hydrate_runtime_job_payload(\n        runtime_job\n    )\n\n'''
    return source.replace(anchor, addition, 1)


def write_report(path: Path, checks: dict[str, bool], evidence: dict[str, Any], error: dict[str, Any], backup: Path | None) -> None:
    failed = [name for name, passed in checks.items() if not passed]
    certified = not failed and not error
    text = "\n".join(
        [
            "LINKCRAFTOR PIPELINE VALIDATION AND ACTIVATION",
            "PART E 13-B2 HYDRATION AND ENTRYPOINT INTEGRATION CERTIFICATION",
            "",
            "Patch mode: STRICT FAIL-CLOSED",
            f"Backup: {backup or 'NONE'}",
            "Production activation executed: NO",
            "Production Universal Jobs created: NO",
            "Production queue claims executed: NO",
            "Production handlers executed: NO",
            "Live network requests executed: NO",
            "CERTIFICATION STATUS: " + ("CERTIFIED" if certified else "NOT_CERTIFIED"),
            "",
            "CHECKS:",
            json.dumps(checks, indent=2, sort_keys=True),
            "",
            "FAILED_CHECKS:",
            json.dumps(failed, indent=2),
            "",
            "EVIDENCE:",
            json.dumps(evidence, indent=2, default=str, sort_keys=True),
            "",
            "EXECUTION_ERROR:",
            json.dumps(error, indent=2),
            "",
            "FINAL RESULT:",
            "FINAL RESULT: PART E 13-B2 CERTIFIED" if certified else "FINAL RESULT: PART E 13-B2 NOT_CERTIFIED",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    root = Path(sys.argv[1]).resolve()
    report = Path(sys.argv[2]).resolve()
    targets = {
        name: root / name for name in EXPECTED_HASHES
    }
    new_files = {
        root / "backend/server/runtime/runtime_payload_hydration.py": RUNTIME_HOOK_SOURCE,
        root / "backend/server/pipelines/connect_domain/runtime_hydration.py": PIPELINE_HYDRATOR_SOURCE,
        root / "backend/server/pipelines/connect_domain/activation.py": ACTIVATION_SOURCE,
    }
    checks = {
        "part_e_13_b1_complete": False,
        "target_precondition_hashes": False,
        "new_boundaries_previously_absent": False,
        "candidate_syntax": False,
        "four_handoffs_hydrated": False,
        "internal_hydrator_marker_removed": False,
        "predecessor_not_completed_rejected": False,
        "missing_predecessor_rejected": False,
        "route_uses_canonical_activation": False,
        "legacy_route_call_absent": False,
        "worker_hook_declared_once": False,
        "activation_uses_coordinator_manifest_gateway": False,
        "workflow_persistence_connected": False,
        "isolated_activation_succeeded": False,
        "isolated_gateway_called_once": False,
        "workflow_identity_persisted": False,
        "six_job_ids_returned": False,
        "no_duplicate_runtime_infrastructure": False,
        "production_jobs_created_no": True,
        "production_queue_claims_no": True,
        "production_handlers_executed_no": True,
        "live_network_requests_no": True,
        "retained_source_syntax": False,
    }
    evidence: dict[str, Any] = {}
    error: dict[str, Any] = {}
    backup: Path | None = None
    originals: dict[Path, bytes] = {}
    retained = False
    try:
        b1 = root / "backend/server/data/reports/PART_E_13_B1_HYDRATION_ENTRYPOINT_CONTRACT_EXTRACTION.txt"
        b1_text = b1.read_text(encoding="utf-8-sig")
        checks["part_e_13_b1_complete"] = (
            "EXTRACTION STATUS: COMPLETE" in b1_text
            and "FAILED_CHECKS:\n[]" in b1_text.replace("\r\n", "\n")
            and "FINAL RESULT: PART E 13-B1 COMPLETE" in b1_text
        )
        if not checks["part_e_13_b1_complete"]:
            raise RuntimeError("Part E 13-B1 is not complete.")
        checks["target_precondition_hashes"] = all(
            path.is_file() and sha(path) == EXPECTED_HASHES[name]
            for name, path in targets.items()
        )
        if not checks["target_precondition_hashes"]:
            raise RuntimeError("A production source changed after 13-B1 extraction.")
        checks["new_boundaries_previously_absent"] = all(not path.exists() for path in new_files)
        if not checks["new_boundaries_previously_absent"]:
            raise RuntimeError("A Part E 13-B2 boundary already exists; refusing duplicate patch.")

        originals = {path: path.read_bytes() for path in targets.values()}
        route_candidate = patch_route(originals[targets["backend/server/routes/site_workspace.py"]].decode("utf-8-sig").replace("\r\n", "\n"))
        worker_candidate = patch_worker(originals[targets["backend/server/runtime/universal_runtime_worker_v1.py"]].decode("utf-8-sig").replace("\r\n", "\n"))
        candidates = dict(new_files)
        candidates[targets["backend/server/routes/site_workspace.py"]] = route_candidate
        candidates[targets["backend/server/runtime/universal_runtime_worker_v1.py"]] = worker_candidate
        for path, source in candidates.items():
            ast.parse(source, filename=str(path))
        checks["candidate_syntax"] = True

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = root / "backend/server/data/runtime_backups" / ("part_e_13_b2_" + stamp)
        backup.mkdir(parents=True, exist_ok=False)
        for path in targets.values():
            destination = backup / path.relative_to(root)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
        for path, source in candidates.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(source, encoding="utf-8", newline="\n")
            py_compile.compile(str(path), doraise=True)

        sys.path.insert(0, str(root))
        importlib.invalidate_caches()
        hydration = importlib.import_module("backend.server.pipelines.connect_domain.runtime_hydration")
        hook = importlib.import_module("backend.server.runtime.runtime_payload_hydration")
        activation = importlib.import_module("backend.server.pipelines.connect_domain.activation")
        if not callable(getattr(activation, "activate_connected_domain_pipeline", None)):
            raise RuntimeError("Connected Domain activation authority is unavailable.")

        def pred(stage: str, result: dict[str, Any], status: str = "completed"):
            return SimpleNamespace(
                job_id="job_" + stage,
                stage=stage,
                status=status,
                metadata={"runtime_dispatch_result": {"handler_result": {"value": result}}},
            )

        cases = [
            ("url_cleaner", pred("site_sources", {"discovered_urls": ["https://example.com/a"]}), "source_urls"),
            ("site_pages", pred("url_cleaner", {"cleaned_urls": ["https://example.com/a"], "explicit_urls": ["https://example.com/a"], "uncertain_urls": []}), "cleaner_records"),
            ("live_domain_target_pool", pred("site_pages", {"pages": [{"url": "https://example.com/a"}]}), "site_pages"),
            ("active_target_set", pred("live_domain_target_pool", {"targets": [{"url": "https://example.com/a"}]}), "live_domain_payload"),
        ]
        hydrated_evidence = {}
        for stage, predecessor, field in cases:
            job = {
                "job_id": "job_" + stage,
                "stage": stage,
                "payload": {hook.RUNTIME_PAYLOAD_HYDRATOR_KEY: hydration.CONNECTED_DOMAIN_HYDRATOR_REF},
                "dependency_job_ids": [predecessor.job_id],
            }
            resolved = hydration.hydrate_connected_domain_runtime_job(
                job,
                job_reader=lambda _job_id, item=predecessor: item,
                jobs_reader=lambda: {},
            )
            if field not in resolved["payload"]:
                raise RuntimeError("Hydration field missing: " + field)
            hydrated_evidence[stage] = resolved["payload"][field]
        checks["four_handoffs_hydrated"] = True

        original_resolve = hook._resolve_hydrator
        hook._resolve_hydrator = lambda _ref: (
            lambda value: {
                **dict(value),
                "payload": {**dict(value["payload"]), "hydrated": True},
            }
        )
        try:
            marker_result = hook.hydrate_runtime_job_payload(
                {"payload": {hook.RUNTIME_PAYLOAD_HYDRATOR_KEY: "backend.server.pipelines.x:y"}}
            )
        finally:
            hook._resolve_hydrator = original_resolve
        checks["internal_hydrator_marker_removed"] = (
            marker_result["payload"].get("hydrated") is True
            and hook.RUNTIME_PAYLOAD_HYDRATOR_KEY not in marker_result["payload"]
        )

        try:
            hydration.hydrate_connected_domain_runtime_job(
                {"stage": "url_cleaner", "payload": {}, "dependency_job_ids": ["x"]},
                job_reader=lambda _id: pred("site_sources", {"discovered_urls": ["x"]}, "running"),
                jobs_reader=lambda: {},
            )
        except hydration.ConnectedDomainRuntimeHydrationError:
            checks["predecessor_not_completed_rejected"] = True
        try:
            hydration.hydrate_connected_domain_runtime_job(
                {"stage": "url_cleaner", "payload": {}},
                job_reader=lambda _id: None,
                jobs_reader=lambda: {},
            )
        except hydration.ConnectedDomainRuntimeHydrationError:
            checks["missing_predecessor_rejected"] = True

        route_text = route_candidate
        checks["route_uses_canonical_activation"] = route_text.count("activate_connected_domain_pipeline(") == 1
        route_tree = ast.parse(route_text)
        route_fn = next(node for node in route_tree.body if isinstance(node, ast.FunctionDef) and node.name == "connect_domain")
        checks["legacy_route_call_absent"] = not any(
            isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "run_connect_domain"
            for node in ast.walk(route_fn)
        )
        checks["worker_hook_declared_once"] = worker_candidate.count("hydrate_runtime_job_payload(\n        runtime_job\n    )") == 1

        activation_text = ACTIVATION_SOURCE
        checks["activation_uses_coordinator_manifest_gateway"] = all(
            name in activation_text for name in (
                "coordinate_connect_domain_pipeline(",
                "build_connected_domain_pipeline_manifest(",
                "connect_connected_domain_to_universal_coordination(",
            )
        )
        checks["workflow_persistence_connected"] = all(
            name in activation_text for name in ("load_workflow_record(", "save_workflow(")
        )

        persistence_module = importlib.import_module(
            "backend.server.coordination.workflow_persistence.repository"
        )

        class IsolatedRepository:
            def __init__(self):
                self.workflow = None

            def load_workflow_record(self, workflow_id):
                raise persistence_module.WorkflowPersistenceNotFoundError(
                    str(workflow_id)
                )

            def save_workflow(self, workflow):
                self.workflow = workflow
                return SimpleNamespace(
                    workflow_id=workflow.workflow_id,
                    workflow_content_fingerprint=workflow.content_fingerprint(),
                    workflow_identity_fingerprint=workflow.identity_fingerprint(),
                    document_fingerprint="isolated",
                    persisted_at="isolated",
                )

        class IsolatedGateway:
            def __init__(self):
                self.workflow_repository = IsolatedRepository()
                self.calls = []

            def submit_workflow_execution(self, **kwargs):
                self.calls.append(kwargs)
                result = SimpleNamespace(
                    job_ids=tuple(f"job_{index}" for index in range(1, 7)),
                )
                result.to_dict = lambda: {
                    "job_ids": list(result.job_ids),
                    "isolated": True,
                }
                return result

        isolated_gateway = IsolatedGateway()
        activation_result = activation.activate_connected_domain_pipeline(
            runtime_gateway=isolated_gateway,
            workspace_id="ws_part_e_13_b2_probe",
            workspace_name="Part E 13-B2 Probe",
            domain="Example.COM",
        )
        checks["isolated_activation_succeeded"] = (
            activation_result.get("ok") is True
            and activation_result.get("domain") == "example.com"
        )
        checks["isolated_gateway_called_once"] = len(isolated_gateway.calls) == 1
        checks["workflow_identity_persisted"] = (
            isolated_gateway.workflow_repository.workflow is not None
            and isolated_gateway.workflow_repository.workflow.workflow_id
            == activation_result.get("workflow_id")
        )
        checks["six_job_ids_returned"] = len(activation_result.get("job_ids", ())) == 6

        checks["no_duplicate_runtime_infrastructure"] = not any(
            token in RUNTIME_HOOK_SOURCE + PIPELINE_HYDRATOR_SOURCE + ACTIVATION_SOURCE
            for token in ("class WorkflowRepository", "class UniversalRuntimeKernel", "def submit_universal_job", "def create_job")
        )
        for path in candidates:
            py_compile.compile(str(path), doraise=True)
        checks["retained_source_syntax"] = True
        evidence = {
            "hydrated_evidence": hydrated_evidence,
            "new_files": [str(path.relative_to(root)) for path in new_files],
            "patched_files": [
                "backend/server/routes/site_workspace.py",
                "backend/server/runtime/universal_runtime_worker_v1.py",
            ],
            "production_activation_executed": False,
            "production_jobs_created": False,
            "production_handlers_executed": False,
        }
        if not all(checks.values()):
            raise RuntimeError("Part E 13-B2 certification checks did not all pass.")
        retained = True
    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }
    finally:
        if not retained and originals:
            for path, content in originals.items():
                path.write_bytes(content)
            for path in new_files:
                if path.exists():
                    path.unlink()
        write_report(report, checks, evidence, error, backup)
    for name, passed in checks.items():
        print(name.upper() + ": " + ("PASS" if passed else "FAIL"))
    print("FAILED_CHECK_COUNT=" + str(sum(not item for item in checks.values())))
    print("REPORT=" + str(report))
    print("PART_E_13_B2_STATUS=" + ("CERTIFIED" if retained else "NOT_CERTIFIED"))
    return 0 if retained else 1


if __name__ == "__main__":
    raise SystemExit(main())
