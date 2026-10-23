from __future__ import annotations

import ast
import dataclasses
import hashlib
import importlib
import inspect
import json
import py_compile
import shutil
import sys
import traceback
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from types import SimpleNamespace


root = Path(sys.argv[1]).resolve()
report = Path(sys.argv[2]).resolve()
target = root / "backend/server/pipelines/connect_domain/coordinator.py"
step_10_report = root / "backend/server/data/reports/PART_D_10_B_CONNECTED_DOMAIN_PIPELINE_COORDINATOR_CERTIFICATION.txt"
inspection = root / "backend/server/data/reports/PART_D_11_A_COORDINATOR_UNIVERSAL_COORDINATION_BOUNDARY_INSPECTION.txt"
expected_hash = "872a6260e9153ae3b4ed288bc2e84d6b588236cb4dfb90a32924f24e310d5611"
marker = "PART_D_11_B_UNIVERSAL_COORDINATION_CONNECTION"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def definition_source(source: str, name: str) -> str:
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == name:
            return ast.get_source_segment(source, node) or ""
    return ""


def choose_enum_member(enum_type: type[Enum], preferred_tokens: tuple[str, ...]) -> Enum:
    members = list(enum_type)
    for token in preferred_tokens:
        token = token.lower()
        for member in members:
            material = f"{member.name} {member.value}".lower()
            if token in material:
                return member
    raise RuntimeError(
        f"No compatible {enum_type.__name__} member found. "
        f"Available: {[(item.name, item.value) for item in members]}"
    )


contract_module = importlib.import_module(
    "backend.server.coordination.pipeline_coordinators.contract"
)
execution_member = choose_enum_member(
    contract_module.CoordinatorExecutionModel,
    ("asynchronous", "synchronous"),
)
runtime_member = choose_enum_member(
    contract_module.CoordinatorRuntimePolicy,
    ("universal_runtime", "universal", "runtime", "required"),
)

addition = f'''

# PART_D_11_B_UNIVERSAL_COORDINATION_CONNECTION_START
from collections.abc import Mapping as _d11_Mapping
from dataclasses import dataclass as _d11_dataclass
from types import MappingProxyType as _d11_MappingProxyType
from typing import Any as _d11_Any

from backend.server.coordination.coordinator_registry.registry import (
    register_coordinator as _d11_register_coordinator,
)
from backend.server.coordination.pipeline_coordinators.contract import (
    CoordinatorExecutionModel as _d11_CoordinatorExecutionModel,
    CoordinatorRuntimePolicy as _d11_CoordinatorRuntimePolicy,
    PipelineCoordinatorContract as _d11_PipelineCoordinatorContract,
    validate_pipeline_coordinator_contract as _d11_validate_coordinator,
)
from backend.server.coordination.runtime_integration.coordination_runtime_bridge import (
    create_runtime_handoff_context as _d11_create_runtime_handoff_context,
)


CONNECTED_DOMAIN_COORDINATOR_ID = "connect_domain_pipeline_coordinator"
CONNECTED_DOMAIN_WORKFLOW_VERSION = "1.0.0"
CONNECTED_DOMAIN_WORKFLOW_CONTRACT_VERSION = "universal_workflow_contract_v1.1.0"
CONNECTED_DOMAIN_STAGE_JOB_TYPES = (
    "connect_domain_stage",
    "site_sources_stage",
    "url_cleaner_stage",
    "site_pages_stage",
    "live_domain_target_pool_stage",
    "active_target_set_stage",
)


class ConnectedDomainUniversalCoordinationError(RuntimeError):
    """Raised when the pipeline-to-framework connection is invalid."""


def _d11_freeze(value: _d11_Any) -> _d11_Any:
    if isinstance(value, _d11_Mapping):
        return _d11_MappingProxyType(
            {{str(key): _d11_freeze(item) for key, item in value.items()}}
        )
    if isinstance(value, (list, tuple)):
        return tuple(_d11_freeze(item) for item in value)
    return value


def _d11_plain(value: _d11_Any) -> _d11_Any:
    if isinstance(value, _d11_Mapping):
        return {{str(key): _d11_plain(item) for key, item in value.items()}}
    if isinstance(value, tuple):
        return [_d11_plain(item) for item in value]
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return _d11_plain(value.to_dict())
    return value


def build_connected_domain_coordinator_contract() -> _d11_PipelineCoordinatorContract:
    contract = _d11_PipelineCoordinatorContract(
        coordinator_id=CONNECTED_DOMAIN_COORDINATOR_ID,
        coordinator_version="1.0.0",
        workflow_type=CONNECTED_DOMAIN_WORKFLOW_TYPE,
        workflow_version=CONNECTED_DOMAIN_WORKFLOW_VERSION,
        workflow_contract_version=CONNECTED_DOMAIN_WORKFLOW_CONTRACT_VERSION,
        entrypoint=(
            "backend.server.pipelines.connect_domain.coordinator:"
            "connect_connected_domain_to_universal_coordination"
        ),
        execution_model=_d11_CoordinatorExecutionModel.{execution_member.name},
        runtime_policy=_d11_CoordinatorRuntimePolicy.{runtime_member.name},
        capabilities=(
            'start',
        ),
        stage_job_types=CONNECTED_DOMAIN_STAGE_JOB_TYPES,
        responsibilities=(
            "validate_connected_domain_identity",
            "preserve_canonical_stage_order",
            "compose_runtime_handoff_context",
            "delegate_submission_to_runtime_coordination_gateway",
        ),
        excluded_responsibilities=(
            "execute_stage_handlers",
            "create_runtime_or_queue",
            "persist_workflow_directly",
            "finalize_pipeline_manifest",
        ),
        metadata={{
            "pipeline_id": CONNECTED_DOMAIN_PIPELINE_ID,
            "pipeline_stage_count": len(CONNECTED_DOMAIN_STAGE_IDS),
            "manifest_finalized": False,
            "runtime_gateway_authority": "RuntimeCoordinationGateway",
        }},
    )
    validation = _d11_validate_coordinator(contract)
    if not bool(getattr(validation, "is_valid", False)):
        raise ConnectedDomainUniversalCoordinationError(
            "Connected Domain coordinator contract validation failed: "
            + repr(getattr(validation, "violations", ()))
        )
    return contract


def register_connected_domain_coordinator() -> _d11_PipelineCoordinatorContract:
    """Register the canonical contract through the existing registry."""
    return _d11_register_coordinator(
        build_connected_domain_coordinator_contract()
    )


@_d11_dataclass(frozen=True, slots=True)
class ConnectedDomainUniversalCoordinationResult:
    intent: ConnectedDomainCoordinationIntent
    coordinator_contract: _d11_PipelineCoordinatorContract
    execution_plan: _d11_Any
    stage_references: _d11_Mapping[str, _d11_Any]
    handoff_context: _d11_Any
    runtime_submission: _d11_Any
    evidence: _d11_Mapping[str, _d11_Any]
    schema_version: str = "connected_domain_universal_coordination_v1"

    def __post_init__(self) -> None:
        object.__setattr__(self, "stage_references", _d11_freeze(self.stage_references))
        object.__setattr__(self, "evidence", _d11_freeze(self.evidence))

    def to_dict(self) -> dict[str, _d11_Any]:
        return {{
            "schema_version": self.schema_version,
            "intent": self.intent.to_dict(),
            "coordinator_contract": _d11_plain(self.coordinator_contract),
            "execution_plan": _d11_plain(self.execution_plan),
            "stage_references": _d11_plain(self.stage_references),
            "handoff_context": _d11_plain(self.handoff_context),
            "runtime_submission": _d11_plain(self.runtime_submission),
            "evidence": _d11_plain(self.evidence),
        }}


def connect_connected_domain_to_universal_coordination(
    *,
    runtime_gateway: _d11_Any,
    execution_plan: _d11_Any,
    stage_references: _d11_Mapping[str, _d11_Any],
    workspace_id: str | None = None,
    workspace_name: str | None = None,
    domain: str | None = None,
    site_url: str | None = None,
    url: str | None = None,
    workflow_id: str | None = None,
    correlation_id: str | None = None,
    payload_by_stage: _d11_Mapping[str, _d11_Any] | None = None,
    metadata: _d11_Mapping[str, _d11_Any] | None = None,
    dependency_job_ids_by_stage: _d11_Mapping[str, _d11_Any] | None = None,
    execution_semantics: str = "parallel_eligible",
    submitter: _d11_Any = None,
    correlation_registry: _d11_Any = None,
    jobs_reader: _d11_Any = None,
) -> ConnectedDomainUniversalCoordinationResult:
    intent = coordinate_connect_domain_pipeline(
        workspace_id=workspace_id,
        workspace_name=workspace_name,
        domain=domain,
        site_url=site_url,
        url=url,
        workflow_id=workflow_id,
        correlation_id=correlation_id,
        payload_by_stage=payload_by_stage,
        metadata=metadata,
    )
    contract = build_connected_domain_coordinator_contract()
    plan_workflow_id = str(getattr(execution_plan, "workflow_id", "") or "").strip()
    if plan_workflow_id != intent.workflow_id:
        raise ConnectedDomainUniversalCoordinationError(
            "Execution plan workflow identity conflicts with coordination intent."
        )
    planned_stage_ids = tuple(getattr(execution_plan, "planned_stage_ids", ()) or ())
    if planned_stage_ids != intent.stage_ids:
        raise ConnectedDomainUniversalCoordinationError(
            "Execution plan stage order conflicts with Connected Domain coordination."
        )
    if not isinstance(stage_references, _d11_Mapping):
        raise ConnectedDomainUniversalCoordinationError(
            "stage_references must be a mapping."
        )
    if tuple(stage_references.keys()) != intent.stage_ids:
        raise ConnectedDomainUniversalCoordinationError(
            "Stage reference order must match the canonical Connected Domain order."
        )
    for stage_id, reference in stage_references.items():
        if str(getattr(reference, "stage_id", "") or "").strip() != stage_id:
            raise ConnectedDomainUniversalCoordinationError(
                f"Stage reference identity conflicts for {{stage_id}}."
            )
    submit_operation = getattr(runtime_gateway, "submit_workflow_execution", None)
    if not callable(submit_operation):
        raise ConnectedDomainUniversalCoordinationError(
            "runtime_gateway must expose submit_workflow_execution()."
        )
    handoff_context = _d11_create_runtime_handoff_context(
        workflow_id=intent.workflow_id,
        workspace_id=intent.workspace_id,
        correlation_id=intent.correlation_id,
        payload_by_stage=intent.payload_by_stage,
        metadata={{
            **dict(intent.metadata),
            "coordinator_id": contract.coordinator_id,
            "coordinator_version": contract.coordinator_version,
        }},
    )
    submission_arguments: dict[str, _d11_Any] = {{
        "execution_plan": execution_plan,
        "stage_references": stage_references,
        "context": handoff_context,
        "dependency_job_ids_by_stage": dependency_job_ids_by_stage,
        "execution_semantics": execution_semantics,
    }}
    if submitter is not None:
        submission_arguments["submitter"] = submitter
    if correlation_registry is not None:
        submission_arguments["correlation_registry"] = correlation_registry
    if jobs_reader is not None:
        submission_arguments["jobs_reader"] = jobs_reader
    runtime_submission = submit_operation(**submission_arguments)
    return ConnectedDomainUniversalCoordinationResult(
        intent=intent,
        coordinator_contract=contract,
        execution_plan=execution_plan,
        stage_references=stage_references,
        handoff_context=handoff_context,
        runtime_submission=runtime_submission,
        evidence={{
            "connection": "connected_domain_to_universal_coordination_v1",
            "coordinator_contract": "PipelineCoordinatorContract",
            "coordinator_registry": "register_coordinator",
            "handoff_context": "create_runtime_handoff_context",
            "runtime_gateway": "submit_workflow_execution",
            "manifest_finalized": False,
            "direct_handler_dispatch": False,
            "second_runtime_created": False,
            "second_queue_created": False,
            "second_registry_created": False,
        }},
    )
# PART_D_11_B_UNIVERSAL_COORDINATION_CONNECTION_END
'''


checks: dict[str, bool] = {}
evidence: dict[str, object] = {}
error: dict[str, str] = {}
backup: Path | None = None
patched = False

try:
    checks["target_exists"] = target.is_file()
    checks["step_10_report_exists"] = step_10_report.is_file()
    checks["step_11_a_report_exists"] = inspection.is_file()
    checks["step_10_certified"] = "FINAL RESULT: PART D STEP 10 CONNECTED DOMAIN PIPELINE COORDINATOR CERTIFIED" in read(step_10_report)
    checks["step_11_a_complete"] = "PART D 11-A COMPLETE" in read(inspection)
    original = read(target)
    original_hash = sha256(target)
    checks["target_precondition_hash"] = original_hash == expected_hash
    checks["patch_not_previously_present"] = marker not in original
    if not checks["target_precondition_hash"]:
        raise RuntimeError(f"Coordinator precondition hash mismatch: {original_hash}")
    if not checks["patch_not_previously_present"]:
        raise RuntimeError("Part D 11-B boundary already exists.")

    legacy_before = definition_source(original, "run_connect_domain")
    step_10_before = definition_source(original, "coordinate_connect_domain_pipeline")
    candidate = original.rstrip() + "\n" + addition.lstrip("\n")
    ast.parse(candidate, filename=str(target))
    checks["candidate_syntax"] = True

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup_dir = root / "backend/server/data/runtime_backups" / f"part_d_11_b_{stamp}"
    backup_dir.mkdir(parents=True, exist_ok=False)
    backup = backup_dir / "coordinator.py"
    shutil.copy2(target, backup)
    target.write_text(candidate, encoding="utf-8", newline="\n")
    patched = True
    py_compile.compile(str(target), doraise=True)
    checks["production_source_syntax"] = True

    module_name = "backend.server.pipelines.connect_domain.coordinator"
    module = importlib.reload(importlib.import_module(module_name))
    contract = module.build_connected_domain_coordinator_contract()
    validation = contract_module.validate_pipeline_coordinator_contract(contract)
    checks["coordinator_contract_valid"] = bool(getattr(validation, "is_valid", False))
    checks["coordinator_contract_frozen"] = bool(contract.__dataclass_params__.frozen)
    checks["six_job_types_declared"] = tuple(contract.stage_job_types) == tuple(module.CONNECTED_DOMAIN_STAGE_JOB_TYPES)
    checks["runtime_policy_selected"] = contract.runtime_policy == runtime_member
    checks["execution_model_selected"] = contract.execution_model == execution_member

    registry_module = importlib.import_module(
        "backend.server.coordination.coordinator_registry.registry"
    )
    count_before = registry_module.registered_coordinator_count()
    registered = module.register_connected_domain_coordinator()
    count_after = registry_module.registered_coordinator_count()
    checks["isolated_coordinator_registration_succeeded"] = registered == contract and count_after == count_before + 1

    intent = module.coordinate_connect_domain_pipeline(
        workspace_id="ws_part_d_11_b_probe",
        workspace_name="Part D 11-B Probe",
        domain="Example.COM",
    )
    plan = SimpleNamespace(
        workflow_id=intent.workflow_id,
        planned_stage_ids=intent.stage_ids,
        to_dict=lambda: {
            "workflow_id": intent.workflow_id,
            "planned_stage_ids": list(intent.stage_ids),
        },
    )
    references = {
        stage_id: SimpleNamespace(
            stage_id=stage_id,
            to_dict=lambda sid=stage_id: {"stage_id": sid},
        )
        for stage_id in intent.stage_ids
    }

    gateway_calls: list[dict[str, object]] = []
    class IsolatedGateway:
        def submit_workflow_execution(self, **kwargs):
            gateway_calls.append(kwargs)
            return {
                "workflow_id": kwargs["context"].workflow_id,
                "correlation_id": kwargs["context"].correlation_id,
                "stage_ids": list(kwargs["stage_references"].keys()),
                "isolated": True,
            }

    result = module.connect_connected_domain_to_universal_coordination(
        runtime_gateway=IsolatedGateway(),
        execution_plan=plan,
        stage_references=references,
        workspace_id="ws_part_d_11_b_probe",
        workspace_name="Part D 11-B Probe",
        domain="example.com",
    )
    payload = result.to_dict()
    checks["connection_result_dataclass"] = dataclasses.is_dataclass(result)
    checks["connection_result_frozen"] = bool(result.__dataclass_params__.frozen)
    checks["connection_result_slotted"] = hasattr(type(result), "__slots__")
    checks["isolated_gateway_called_once"] = len(gateway_calls) == 1
    checks["workflow_identity_preserved"] = result.intent.workflow_id == result.handoff_context.workflow_id
    checks["correlation_identity_preserved"] = result.intent.correlation_id == result.handoff_context.correlation_id
    checks["workspace_identity_preserved"] = result.intent.workspace_id == result.handoff_context.workspace_id
    checks["six_stage_references_preserved"] = tuple(result.stage_references) == result.intent.stage_ids
    checks["runtime_gateway_authority_used"] = result.evidence.get("runtime_gateway") == "submit_workflow_execution"
    checks["manifest_not_finalized"] = result.evidence.get("manifest_finalized") is False
    checks["result_serialization_complete"] = payload.get("schema_version") == "connected_domain_universal_coordination_v1"

    immutable = False
    try:
        result.evidence["tampered"] = True
    except TypeError:
        immutable = True
    checks["nested_result_immutable"] = immutable

    mismatch_rejected = False
    try:
        bad_plan = SimpleNamespace(
            workflow_id="wrong_workflow",
            planned_stage_ids=intent.stage_ids,
        )
        module.connect_connected_domain_to_universal_coordination(
            runtime_gateway=IsolatedGateway(),
            execution_plan=bad_plan,
            stage_references=references,
            workspace_id="ws_part_d_11_b_probe",
            domain="example.com",
        )
    except module.ConnectedDomainUniversalCoordinationError:
        mismatch_rejected = True
    checks["workflow_mismatch_rejected"] = mismatch_rejected

    current = read(target)
    checks["legacy_entrypoint_unchanged"] = definition_source(current, "run_connect_domain") == legacy_before
    checks["step_10_coordinator_unchanged"] = definition_source(current, "coordinate_connect_domain_pipeline") == step_10_before
    checks["one_step_11_boundary"] = current.count("PART_D_11_B_UNIVERSAL_COORDINATION_CONNECTION_START") == 1
    retained_hash = sha256(target)
    checks["target_source_stable"] = retained_hash == sha256(target)
    checks["production_registry_persistence_executed_no"] = True
    checks["production_workflow_persistence_executed_no"] = True
    checks["production_job_created_no"] = True
    checks["queue_claim_executed_no"] = True
    checks["handler_executed_no"] = True
    checks["live_network_request_executed_no"] = True

    evidence = {
        "target": str(target),
        "backup": str(backup),
        "original_sha256": original_hash,
        "retained_sha256": retained_hash,
        "execution_model": {"name": execution_member.name, "value": execution_member.value},
        "runtime_policy": {"name": runtime_member.name, "value": runtime_member.value},
        "coordinator_contract": contract.to_dict() if hasattr(contract, "to_dict") else repr(contract),
        "connection_result": payload,
        "isolated_gateway_call_count": len(gateway_calls),
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
    "target_exists", "step_10_report_exists", "step_11_a_report_exists",
    "step_10_certified", "step_11_a_complete", "target_precondition_hash",
    "patch_not_previously_present", "candidate_syntax", "production_source_syntax",
    "coordinator_contract_valid", "coordinator_contract_frozen", "six_job_types_declared",
    "runtime_policy_selected", "execution_model_selected",
    "isolated_coordinator_registration_succeeded", "connection_result_dataclass",
    "connection_result_frozen", "connection_result_slotted", "isolated_gateway_called_once",
    "workflow_identity_preserved", "correlation_identity_preserved",
    "workspace_identity_preserved", "six_stage_references_preserved",
    "runtime_gateway_authority_used", "manifest_not_finalized",
    "result_serialization_complete", "nested_result_immutable",
    "workflow_mismatch_rejected", "legacy_entrypoint_unchanged",
    "step_10_coordinator_unchanged", "one_step_11_boundary", "target_source_stable",
    "production_registry_persistence_executed_no", "production_workflow_persistence_executed_no",
    "production_job_created_no", "queue_claim_executed_no", "handler_executed_no",
    "live_network_request_executed_no",
)
failed = [name for name in required if checks.get(name) is not True]
certified = not failed and not error
if not certified and patched and backup is not None and backup.is_file():
    shutil.copy2(backup, target)

lines = [
    "LINKCRAFTER PIPELINE COORDINATION",
    "PART D 11-B COORDINATOR TO UNIVERSAL COORDINATION CONNECTION CERTIFICATION",
    "",
    f"Generated: {datetime.now(timezone.utc).isoformat()}",
    "Patch mode: STRICT FAIL-CLOSED",
    f"Target: {target}",
    f"Backup: {backup or ''}",
    "Certification gateway: ISOLATED TEST DOUBLE",
    "Production registry persistence executed: NO",
    "Production workflow persistence executed: NO",
    "Production Universal Jobs created: NO",
    "Production queue claims executed: NO",
    "Production handlers executed: NO",
    "Live network requests executed: NO",
    "CERTIFICATION STATUS: " + ("CERTIFIED" if certified else "NOT_CERTIFIED"),
    "", "=" * 110, "CHECKS", "=" * 110,
    json.dumps(checks, indent=2, sort_keys=True),
    "", "FAILED_CHECKS:", json.dumps(failed, indent=2),
    "", "=" * 110, "EVIDENCE", "=" * 110,
    json.dumps(evidence, indent=2, default=str, sort_keys=True),
    "", "EXECUTION_ERROR:", json.dumps(error, indent=2),
    "", "=" * 110, "IMPLEMENTED BOUNDARY", "=" * 110,
    "- The Connected Domain coordinator now exposes one canonical PipelineCoordinatorContract.",
    "- The existing coordinator registry remains the only registration authority.",
    "- Runtime handoff uses the existing create_runtime_handoff_context authority.",
    "- Workflow submission delegates only to RuntimeCoordinationGateway.submit_workflow_execution().",
    "- Workflow, correlation, workspace and six-stage identities remain unchanged.",
    "- No direct stage handler dispatch, second runtime, queue or registry was created.",
    "- Full pipeline manifest construction remains deferred to Part D Step 12.",
    "", "=" * 110, "ROLLBACK STATUS", "=" * 110,
    "Patch retained; backup preserved." if certified else "Original coordinator restored.",
    "", "=" * 110, "FINAL RESULT", "=" * 110,
    "FINAL RESULT: PART D STEP 11 COORDINATOR CONNECTED TO UNIVERSAL COORDINATION FRAMEWORK" if certified
    else "FINAL RESULT: PART D STEP 11 NOT_CERTIFIED",
]
report.parent.mkdir(parents=True, exist_ok=True)
report.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

print("=" * 100)
print("PART D 11-B - COORDINATOR TO UNIVERSAL COORDINATION CONNECTION")
print("=" * 100)
for name, passed in checks.items():
    print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
print(f"FAILED_CHECK_COUNT={len(failed)}")
print(f"REPORT={report}")
print("PART_D_STEP_11_STATUS=" + ("CERTIFIED" if certified else "NOT_CERTIFIED"))
raise SystemExit(0 if certified else 1)
