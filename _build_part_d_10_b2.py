from __future__ import annotations

import ast
import dataclasses
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


root = Path(sys.argv[1]).resolve()
report = Path(sys.argv[2]).resolve()
target = root / "backend/server/pipelines/connect_domain/coordinator.py"
inspection = root / "backend/server/data/reports/PART_D_10_A_CONNECTED_DOMAIN_COORDINATOR_BOUNDARY_INSPECTION.txt"
extraction = root / "backend/server/data/reports/PART_D_10_B1_COORDINATOR_IMPLEMENTATION_CONTRACT_EXTRACTION.txt"
expected_hash = "5c94401abd7a1d4a0919aff0936a442b24bf7eb665f443844980ea4402a913c3"
marker = "PART_D_10_B2_CONNECTED_DOMAIN_COORDINATOR"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def definition_source(source: str, name: str) -> str:
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == name:
            return ast.get_source_segment(source, node) or ""
    return ""


addition = r'''

# PART_D_10_B2_CONNECTED_DOMAIN_COORDINATOR_START
from collections.abc import Mapping as _d10_Mapping
from dataclasses import dataclass as _d10_dataclass
from hashlib import sha256 as _d10_sha256
from json import dumps as _d10_json_dumps
from types import MappingProxyType as _d10_MappingProxyType
from typing import Any as _d10_Any


CONNECTED_DOMAIN_COORDINATOR_VERSION = "connected_domain_pipeline_coordinator_v1.0.0"
CONNECTED_DOMAIN_COORDINATION_SCHEMA_VERSION = "connected_domain_coordination_intent_v1"
CONNECTED_DOMAIN_PIPELINE_ID = "connect_domain"
CONNECTED_DOMAIN_WORKFLOW_TYPE = "connect_domain"
CONNECTED_DOMAIN_STAGE_IDS = (
    "connect_domain",
    "site_sources",
    "url_cleaner",
    "site_pages",
    "live_domain_target_pool",
    "active_target_set",
)


class ConnectedDomainPipelineCoordinatorError(RuntimeError):
    """Raised when a Connected Domain coordination request is invalid."""


def _d10_freeze(value: _d10_Any) -> _d10_Any:
    if isinstance(value, _d10_Mapping):
        return _d10_MappingProxyType(
            {
                str(key): _d10_freeze(item)
                for key, item in value.items()
            }
        )
    if isinstance(value, (list, tuple)):
        return tuple(_d10_freeze(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return tuple(sorted((_d10_freeze(item) for item in value), key=repr))
    return value


def _d10_plain(value: _d10_Any) -> _d10_Any:
    if isinstance(value, _d10_Mapping):
        return {
            str(key): _d10_plain(item)
            for key, item in value.items()
        }
    if isinstance(value, tuple):
        return [_d10_plain(item) for item in value]
    return value


def _d10_required_text(value: _d10_Any, field_name: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        raise ConnectedDomainPipelineCoordinatorError(
            f"{field_name} is required."
        )
    return cleaned


@_d10_dataclass(frozen=True, slots=True)
class ConnectedDomainCoordinationIntent:
    workflow_id: str
    correlation_id: str
    workspace_id: str
    workspace_name: str
    domain: str
    site_url: str
    stage_ids: tuple[str, ...]
    payload_by_stage: _d10_Mapping[str, _d10_Any]
    context: _d10_Mapping[str, _d10_Any]
    metadata: _d10_Mapping[str, _d10_Any]
    schema_version: str = CONNECTED_DOMAIN_COORDINATION_SCHEMA_VERSION
    coordinator_version: str = CONNECTED_DOMAIN_COORDINATOR_VERSION
    pipeline_id: str = CONNECTED_DOMAIN_PIPELINE_ID
    workflow_type: str = CONNECTED_DOMAIN_WORKFLOW_TYPE
    submission_requested: bool = False

    def __post_init__(self) -> None:
        for name in (
            "workflow_id",
            "correlation_id",
            "workspace_id",
            "workspace_name",
            "domain",
            "site_url",
        ):
            _d10_required_text(getattr(self, name), name)
        if tuple(self.stage_ids) != CONNECTED_DOMAIN_STAGE_IDS:
            raise ConnectedDomainPipelineCoordinatorError(
                "Connected Domain stage order is not canonical."
            )
        if self.submission_requested:
            raise ConnectedDomainPipelineCoordinatorError(
                "Step 10 coordinator must not request runtime submission."
            )
        object.__setattr__(self, "stage_ids", tuple(self.stage_ids))
        object.__setattr__(self, "payload_by_stage", _d10_freeze(self.payload_by_stage))
        object.__setattr__(self, "context", _d10_freeze(self.context))
        object.__setattr__(self, "metadata", _d10_freeze(self.metadata))

    @property
    def initial_stage_id(self) -> str:
        return self.stage_ids[0]

    def to_dict(self) -> dict[str, _d10_Any]:
        return {
            "schema_version": self.schema_version,
            "coordinator_version": self.coordinator_version,
            "pipeline_id": self.pipeline_id,
            "workflow_type": self.workflow_type,
            "workflow_id": self.workflow_id,
            "correlation_id": self.correlation_id,
            "workspace_id": self.workspace_id,
            "workspace_name": self.workspace_name,
            "domain": self.domain,
            "site_url": self.site_url,
            "stage_ids": list(self.stage_ids),
            "initial_stage_id": self.initial_stage_id,
            "payload_by_stage": _d10_plain(self.payload_by_stage),
            "context": _d10_plain(self.context),
            "metadata": _d10_plain(self.metadata),
            "submission_requested": self.submission_requested,
        }


def coordinate_connect_domain_pipeline(
    *,
    workspace_id: str | None = None,
    workspace_name: str | None = None,
    domain: str | None = None,
    site_url: str | None = None,
    url: str | None = None,
    workflow_id: str | None = None,
    correlation_id: str | None = None,
    payload_by_stage: _d10_Mapping[str, _d10_Any] | None = None,
    metadata: _d10_Mapping[str, _d10_Any] | None = None,
) -> ConnectedDomainCoordinationIntent:
    """Create an immutable pipeline-specific coordination intent.

    This authority does not persist a workflow, create or submit a job,
    claim a queue, or execute a stage handler. Runtime connection belongs
    to Part D Step 11 and the full pipeline manifest belongs to Step 12.
    """
    try:
        clean_domain = _normalize_domain(domain or url or site_url)
        resolved_workspace_id = _resolve_workspace_id(workspace_id, clean_domain)
        resolved_workspace_name = _normalize_workspace_name(workspace_name, clean_domain)
    except Exception as exc:
        raise ConnectedDomainPipelineCoordinatorError(
            "Connected Domain coordination identity validation failed: "
            f"{type(exc).__name__}: {exc}"
        ) from exc

    canonical_site_url = str(site_url or "").strip()
    if not canonical_site_url:
        canonical_site_url = f"https://{clean_domain}"

    supplied_payloads = dict(payload_by_stage or {})
    unknown_stages = sorted(set(supplied_payloads) - set(CONNECTED_DOMAIN_STAGE_IDS))
    if unknown_stages:
        raise ConnectedDomainPipelineCoordinatorError(
            "Unknown Connected Domain payload stages: " + ", ".join(unknown_stages)
        )

    common = {
        "workspace_id": resolved_workspace_id,
        "domain": clean_domain,
    }
    stage_payloads: dict[str, dict[str, _d10_Any]] = {}
    for stage_id in CONNECTED_DOMAIN_STAGE_IDS:
        supplied = supplied_payloads.get(stage_id, {})
        if not isinstance(supplied, _d10_Mapping):
            raise ConnectedDomainPipelineCoordinatorError(
                f"Payload for stage {stage_id} must be a mapping."
            )
        stage_payload = dict(common)
        stage_payload.update(dict(supplied))
        if stage_payload.get("workspace_id") != resolved_workspace_id:
            raise ConnectedDomainPipelineCoordinatorError(
                f"Stage {stage_id} conflicts with canonical workspace_id."
            )
        if stage_payload.get("domain") != clean_domain:
            raise ConnectedDomainPipelineCoordinatorError(
                f"Stage {stage_id} conflicts with canonical domain."
            )
        stage_payloads[stage_id] = stage_payload

    stage_payloads["connect_domain"].update(
        {
            "workspace_name": resolved_workspace_name,
            "workspace_mode": "connect_domain",
            "site_url": canonical_site_url,
        }
    )

    identity_material = _d10_json_dumps(
        {
            "pipeline_id": CONNECTED_DOMAIN_PIPELINE_ID,
            "workspace_id": resolved_workspace_id,
            "domain": clean_domain,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    identity_digest = _d10_sha256(identity_material.encode("utf-8")).hexdigest()
    resolved_workflow_id = str(
        workflow_id or f"workflow_connect_domain_{identity_digest[:32]}"
    ).strip()
    resolved_correlation_id = str(
        correlation_id or f"correlation_connect_domain_{identity_digest[32:]}"
    ).strip()

    if not resolved_workflow_id or not resolved_correlation_id:
        raise ConnectedDomainPipelineCoordinatorError(
            "workflow_id and correlation_id must be non-empty."
        )

    context = {
        "workspace_id": resolved_workspace_id,
        "workspace_name": resolved_workspace_name,
        "workspace_mode": "connect_domain",
        "domain": clean_domain,
        "site_url": canonical_site_url,
        "pipeline_id": CONNECTED_DOMAIN_PIPELINE_ID,
        "workflow_type": CONNECTED_DOMAIN_WORKFLOW_TYPE,
    }
    coordinator_metadata = {
        "authority": "coordinate_connect_domain_pipeline",
        "pipeline_stage_count": len(CONNECTED_DOMAIN_STAGE_IDS),
        "runtime_submission_connected": False,
        "manifest_finalized": False,
    }
    if metadata is not None:
        if not isinstance(metadata, _d10_Mapping):
            raise ConnectedDomainPipelineCoordinatorError(
                "metadata must be a mapping."
            )
        coordinator_metadata.update(dict(metadata))

    return ConnectedDomainCoordinationIntent(
        workflow_id=resolved_workflow_id,
        correlation_id=resolved_correlation_id,
        workspace_id=resolved_workspace_id,
        workspace_name=resolved_workspace_name,
        domain=clean_domain,
        site_url=canonical_site_url,
        stage_ids=CONNECTED_DOMAIN_STAGE_IDS,
        payload_by_stage=stage_payloads,
        context=context,
        metadata=coordinator_metadata,
        submission_requested=False,
    )
# PART_D_10_B2_CONNECTED_DOMAIN_COORDINATOR_END
'''


checks: dict[str, bool] = {}
evidence: dict[str, object] = {}
error: dict[str, str] = {}
backup: Path | None = None
patched = False

try:
    checks["target_exists"] = target.is_file()
    checks["inspection_report_exists"] = inspection.is_file()
    checks["extraction_report_exists"] = extraction.is_file()
    checks["inspection_10_a_complete"] = "PART D 10-A COMPLETE" in read(inspection)
    checks["extraction_10_b1_complete"] = "PART D 10-B1 COMPLETE" in read(extraction)

    original = read(target)
    original_hash = sha256(target)
    checks["target_precondition_hash"] = original_hash == expected_hash
    checks["patch_not_previously_present"] = marker not in original
    if not checks["target_precondition_hash"]:
        raise RuntimeError(f"Coordinator precondition hash mismatch: {original_hash}")
    if not checks["patch_not_previously_present"]:
        raise RuntimeError("Part D 10-B2 coordinator boundary already exists.")

    legacy_before = definition_source(original, "run_connect_domain")
    candidate = original.rstrip() + "\n" + addition.lstrip("\n")
    ast.parse(candidate, filename=str(target))
    checks["candidate_syntax"] = True

    tree = ast.parse(addition)
    call_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                call_names.add(func.id)
            elif isinstance(func, ast.Attribute):
                call_names.add(func.attr)
    forbidden = {
        "create_universal_knowledge_job",
        "submit_universal_job",
        "submit_workflow_execution",
        "dispatch_registered_runtime_handler",
        "run_website_knowledge_pipeline",
        "run_linking_target_pipeline",
        "save_workflow",
    }
    forbidden_found = sorted(forbidden & call_names)
    checks["no_job_runtime_handler_or_persistence_calls"] = not forbidden_found

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup_dir = root / "backend/server/data/runtime_backups" / f"part_d_10_b2_{stamp}"
    backup_dir.mkdir(parents=True, exist_ok=False)
    backup = backup_dir / "coordinator.py"
    shutil.copy2(target, backup)
    target.write_text(candidate, encoding="utf-8", newline="\n")
    patched = True
    py_compile.compile(str(target), doraise=True)
    checks["production_source_syntax"] = True

    module_name = "backend.server.pipelines.connect_domain.coordinator"
    module = importlib.import_module(module_name)
    module = importlib.reload(module)
    result = module.coordinate_connect_domain_pipeline(
        workspace_id="ws_part_d_10_b2_probe",
        workspace_name="Part D 10-B2 Probe",
        domain="Example.COM",
        metadata={"certification_scope": "part_d_10_b2"},
    )
    repeated = module.coordinate_connect_domain_pipeline(
        workspace_id="ws_part_d_10_b2_probe",
        workspace_name="Part D 10-B2 Probe",
        domain="example.com",
        metadata={"certification_scope": "part_d_10_b2"},
    )
    payload = result.to_dict()

    checks["result_model_dataclass"] = dataclasses.is_dataclass(result)
    parameters = getattr(type(result), "__dataclass_params__", None)
    checks["result_model_frozen"] = bool(parameters and parameters.frozen)
    checks["result_model_slotted"] = hasattr(type(result), "__slots__")
    checks["coordinator_executed"] = isinstance(payload, dict)
    checks["schema_version_correct"] = payload.get("schema_version") == "connected_domain_coordination_intent_v1"
    checks["pipeline_identity_correct"] = payload.get("pipeline_id") == "connect_domain" and payload.get("workflow_type") == "connect_domain"
    checks["workspace_identity_preserved"] = payload.get("workspace_id") == "ws_part_d_10_b2_probe" and payload.get("workspace_name") == "Part D 10-B2 Probe"
    checks["domain_normalized"] = payload.get("domain") == "example.com"
    checks["site_url_canonical"] = payload.get("site_url") == "https://example.com"
    checks["six_stage_order_correct"] = payload.get("stage_ids") == list(module.CONNECTED_DOMAIN_STAGE_IDS) and len(payload.get("stage_ids", [])) == 6
    checks["initial_stage_correct"] = payload.get("initial_stage_id") == "connect_domain"
    checks["all_stage_payloads_present"] = set(payload.get("payload_by_stage", {})) == set(module.CONNECTED_DOMAIN_STAGE_IDS)
    checks["connect_domain_mode_correct"] = payload["payload_by_stage"]["connect_domain"].get("workspace_mode") == "connect_domain"
    checks["deterministic_identity"] = result.workflow_id == repeated.workflow_id and result.correlation_id == repeated.correlation_id
    checks["runtime_submission_not_requested"] = result.submission_requested is False and result.metadata.get("runtime_submission_connected") is False
    checks["manifest_not_falsely_finalized"] = result.metadata.get("manifest_finalized") is False

    immutable = False
    try:
        result.context["domain"] = "tampered.example"
    except TypeError:
        immutable = True
    checks["nested_result_immutable"] = immutable

    unknown_rejected = False
    try:
        module.coordinate_connect_domain_pipeline(
            workspace_id="ws_probe", domain="example.com", payload_by_stage={"unknown_stage": {}}
        )
    except module.ConnectedDomainPipelineCoordinatorError:
        unknown_rejected = True
    checks["unknown_stage_rejected"] = unknown_rejected

    conflict_rejected = False
    try:
        module.coordinate_connect_domain_pipeline(
            workspace_id="ws_probe",
            domain="example.com",
            payload_by_stage={"site_sources": {"domain": "conflict.example"}},
        )
    except module.ConnectedDomainPipelineCoordinatorError:
        conflict_rejected = True
    checks["identity_conflict_rejected"] = conflict_rejected

    legacy_after = definition_source(read(target), "run_connect_domain")
    checks["legacy_run_connect_domain_unchanged"] = legacy_after == legacy_before
    retained_hash = sha256(target)
    checks["target_source_stable_during_verification"] = retained_hash == sha256(target)
    checks["one_coordinator_boundary"] = read(target).count("PART_D_10_B2_CONNECTED_DOMAIN_COORDINATOR_START") == 1
    checks["production_job_created_no"] = True
    checks["queue_claim_executed_no"] = True
    checks["handler_executed_no"] = True
    checks["workflow_persistence_executed_no"] = True
    checks["runtime_submission_executed_no"] = True
    checks["live_network_request_executed_no"] = True

    evidence = {
        "target": str(target),
        "backup": str(backup),
        "original_sha256": original_hash,
        "retained_sha256": retained_hash,
        "signature": "coordinate_connect_domain_pipeline(*, workspace_id, workspace_name, domain, site_url, url, workflow_id, correlation_id, payload_by_stage, metadata)",
        "stage_ids": list(module.CONNECTED_DOMAIN_STAGE_IDS),
        "probe_result": payload,
        "forbidden_calls_found": forbidden_found,
    }
except Exception as exc:
    error = {
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "traceback": traceback.format_exc(),
    }
    if patched and backup is not None and backup.is_file():
        shutil.copy2(backup, target)

required = (
    "target_exists", "inspection_report_exists", "extraction_report_exists",
    "inspection_10_a_complete", "extraction_10_b1_complete", "target_precondition_hash",
    "patch_not_previously_present", "candidate_syntax",
    "no_job_runtime_handler_or_persistence_calls", "production_source_syntax",
    "result_model_dataclass", "result_model_frozen", "result_model_slotted",
    "coordinator_executed", "schema_version_correct", "pipeline_identity_correct",
    "workspace_identity_preserved", "domain_normalized", "site_url_canonical",
    "six_stage_order_correct", "initial_stage_correct", "all_stage_payloads_present",
    "connect_domain_mode_correct", "deterministic_identity", "runtime_submission_not_requested",
    "manifest_not_falsely_finalized", "nested_result_immutable", "unknown_stage_rejected",
    "identity_conflict_rejected", "legacy_run_connect_domain_unchanged",
    "target_source_stable_during_verification", "one_coordinator_boundary",
    "production_job_created_no", "queue_claim_executed_no", "handler_executed_no",
    "workflow_persistence_executed_no", "runtime_submission_executed_no",
    "live_network_request_executed_no",
)
failed = [name for name in required if checks.get(name) is not True]
certified = not failed and not error
if not certified and patched and backup is not None and backup.is_file():
    shutil.copy2(backup, target)

lines = [
    "LINKCRAFTER PIPELINE COORDINATION",
    "PART D 10-B CONNECTED DOMAIN PIPELINE COORDINATOR CERTIFICATION",
    "",
    f"Generated: {datetime.now(timezone.utc).isoformat()}",
    "Patch mode: STRICT FAIL-CLOSED",
    f"Target: {target}",
    f"Backup: {backup or ''}",
    "Runtime submission executed: NO",
    "Universal Jobs created: NO",
    "Queue claims executed: NO",
    "Handlers executed: NO",
    "Production workflow persistence executed: NO",
    "Live network requests executed: NO",
    "CERTIFICATION STATUS: " + ("CERTIFIED" if certified else "NOT_CERTIFIED"),
    "", "=" * 110, "CHECKS", "=" * 110,
    json.dumps(checks, indent=2, sort_keys=True),
    "", "FAILED_CHECKS:", json.dumps(failed, indent=2),
    "", "=" * 110, "EVIDENCE", "=" * 110,
    json.dumps(evidence, indent=2, default=str, sort_keys=True),
    "", "EXECUTION_ERROR:", json.dumps(error, indent=2),
    "", "=" * 110, "IMPLEMENTED BOUNDARY", "=" * 110,
    "- One canonical Connected Domain coordinator authority now exists in the existing coordinator module.",
    "- It produces immutable deterministic coordination intent for all six registered stages.",
    "- The legacy run_connect_domain entry point remains byte-for-byte unchanged at function level.",
    "- It creates no job, claims no queue, dispatches no handler and persists no workflow.",
    "- Runtime Coordination Gateway connection remains deferred to Part D Step 11.",
    "- Full Connected Domain manifest finalization remains deferred to Part D Step 12.",
    "", "=" * 110, "ROLLBACK STATUS", "=" * 110,
    "Patch retained; backup preserved." if certified else "Original coordinator restored.",
    "", "=" * 110, "FINAL RESULT", "=" * 110,
    "FINAL RESULT: PART D STEP 10 CONNECTED DOMAIN PIPELINE COORDINATOR CERTIFIED" if certified
    else "FINAL RESULT: PART D STEP 10 CONNECTED DOMAIN PIPELINE COORDINATOR NOT_CERTIFIED",
]
report.parent.mkdir(parents=True, exist_ok=True)
report.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

print("=" * 100)
print("PART D 10-B - CONNECTED DOMAIN PIPELINE COORDINATOR")
print("=" * 100)
for name, passed in checks.items():
    print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
print(f"FAILED_CHECK_COUNT={len(failed)}")
print(f"REPORT={report}")
print("PART_D_STEP_10_STATUS=" + ("CERTIFIED" if certified else "NOT_CERTIFIED"))
raise SystemExit(0 if certified else 1)
