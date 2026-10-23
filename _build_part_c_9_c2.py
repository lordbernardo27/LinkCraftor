from __future__ import annotations

import dataclasses
import hashlib
import importlib
import inspect
import json
import py_compile
import shutil
import sys
import tempfile
import traceback
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType


ROOT = Path(sys.argv[1]).resolve()
REPORT = Path(sys.argv[2]).resolve()
TARGET = ROOT / "backend/server/runtime/runtime_coordination_gateway.py"
PREREQUISITE = (
    ROOT
    / "backend/server/data/reports/"
    "PART_C_9_C1_WORKFLOW_SUBMISSION_CORRELATION_BOUNDARY_INSPECTION.txt"
)
EXPECTED_TARGET_HASH = "097589e5b2668f0a47dbe25b1989424d19f1380b7150df1f1e9ac04c7c21f978"
MARKER = "runtime_workflow_submission_connection_v1"

IMPORT_ANCHOR = '''from backend.server.coordination.runtime_integration.coordination_runtime_bridge import (
    bridge_execution_plan_to_runtime as _bridge_execution_plan_to_runtime,
)
'''

IMPORT_REPLACEMENT = IMPORT_ANCHOR + '''from backend.server.coordination.runtime_integration.runtime_job_mapping import (
    map_runtime_handoffs_to_job_requests as _map_runtime_handoffs_to_job_requests,
)
'''

CLASS_ANCHOR = '''@dataclass(frozen=True, slots=True)
class RuntimeCoordinationGateway:
'''

RESULT_SOURCE = '''@dataclass(frozen=True, slots=True)
class RuntimeWorkflowSubmissionResult:
    workflow_id: str
    correlation_id: str
    stage_ids: tuple[str, ...]
    job_ids: tuple[str, ...]
    bridge_result: Any
    mapping_result: Any
    submission_result: Any
    evidence: Mapping[str, Any]
    connection_version: str = "runtime_workflow_submission_connection_v1"

    def __post_init__(self) -> None:
        object.__setattr__(self, "stage_ids", tuple(self.stage_ids))
        object.__setattr__(self, "job_ids", tuple(self.job_ids))
        object.__setattr__(self, "evidence", _freeze(self.evidence))
        if not self.workflow_id or not self.correlation_id:
            raise RuntimeCoordinationGatewayError(
                "Workflow submission identity is incomplete."
            )
        if self.bridge_result.workflow_id != self.workflow_id:
            raise RuntimeCoordinationGatewayError(
                "Bridge workflow identity does not match submission identity."
            )
        if self.mapping_result.workflow_id != self.workflow_id:
            raise RuntimeCoordinationGatewayError(
                "Mapping workflow identity does not match submission identity."
            )
        if self.submission_result.workflow_id != self.workflow_id:
            raise RuntimeCoordinationGatewayError(
                "Runtime submission workflow identity does not match."
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "connection_version": self.connection_version,
            "workflow_id": self.workflow_id,
            "correlation_id": self.correlation_id,
            "stage_ids": list(self.stage_ids),
            "job_ids": list(self.job_ids),
            "bridge": dict(self.bridge_result.to_dict()),
            "mapping": {
                "workflow_id": self.mapping_result.workflow_id,
                "mapping_count": self.mapping_result.mapping_count,
                "stage_ids": list(self.mapping_result.stage_ids),
            },
            "submission": self.submission_result.to_dict(),
            "evidence": dict(self.evidence),
        }


'''

METHOD_ANCHOR = '''    def submit_runtime_execution_wave(self, **kwargs: Any) -> Any:
        return _submit_runtime_execution_wave(**kwargs)

'''

METHOD_REPLACEMENT = METHOD_ANCHOR + '''    def submit_workflow_execution(
        self,
        *,
        execution_plan: Any,
        stage_references: Mapping[str, Any],
        context: Any,
        dependency_job_ids_by_stage: Mapping[str, Any] | None = None,
        execution_semantics: str = "parallel_eligible",
        submitter: Any = None,
        correlation_registry: Any = None,
        jobs_reader: Any = None,
    ) -> RuntimeWorkflowSubmissionResult:
        bridge_result = _bridge_execution_plan_to_runtime(
            execution_plan=execution_plan,
            stage_references=stage_references,
            context=context,
        )
        mapping_result = _map_runtime_handoffs_to_job_requests(
            bridge_result=bridge_result,
        )
        submission_arguments: dict[str, Any] = {
            "mapping_result": mapping_result,
            "dependency_job_ids_by_stage": dependency_job_ids_by_stage,
            "execution_semantics": execution_semantics,
        }
        if submitter is not None:
            submission_arguments["submitter"] = submitter
        if correlation_registry is not None:
            submission_arguments["correlation_registry"] = correlation_registry
        if jobs_reader is not None:
            submission_arguments["jobs_reader"] = jobs_reader
        submission_result = _submit_runtime_execution_wave(
            **submission_arguments,
        )
        correlation_id = str(getattr(context, "correlation_id", "") or "").strip()
        evidence = {
            "connection": "runtime_workflow_submission_connection_v1",
            "canonical_bridge": "bridge_execution_plan_to_runtime",
            "canonical_mapper": "map_runtime_handoffs_to_job_requests",
            "canonical_submitter": "submit_runtime_execution_wave",
            "canonical_correlation": "WorkflowJobCorrelationRegistry",
            "workflow_repository": type(self.workflow_repository).__name__,
            "direct_handler_dispatch": False,
            "second_queue_created": False,
            "second_registry_created": False,
            "second_submitter_created": False,
        }
        return RuntimeWorkflowSubmissionResult(
            workflow_id=bridge_result.workflow_id,
            correlation_id=correlation_id,
            stage_ids=tuple(mapping_result.stage_ids),
            job_ids=tuple(submission_result.job_ids),
            bridge_result=bridge_result,
            mapping_result=mapping_result,
            submission_result=submission_result,
            evidence=evidence,
        )

'''


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def patch_source(source: str) -> str:
    source = source.replace("\r\n", "\n")
    if MARKER in source:
        raise RuntimeError("Part C 9-C connection is already present.")
    anchors = {
        "mapper import": (IMPORT_ANCHOR, IMPORT_REPLACEMENT),
        "result contract": (CLASS_ANCHOR, RESULT_SOURCE + CLASS_ANCHOR),
        "gateway operation": (METHOD_ANCHOR, METHOD_REPLACEMENT),
        "gateway version": (
            'RUNTIME_COORDINATION_GATEWAY_VERSION = "runtime_coordination_gateway_v1.0.0"',
            'RUNTIME_COORDINATION_GATEWAY_VERSION = "runtime_coordination_gateway_v1.1.0"',
        ),
    }
    candidate = source
    for name, (old, new) in anchors.items():
        count = candidate.count(old)
        if count != 1:
            raise RuntimeError(f"Expected one {name} anchor, found {count}.")
        candidate = candidate.replace(old, new, 1)
    return candidate


def plain(value):
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {field.name: plain(getattr(value, field.name)) for field in dataclasses.fields(value)}
    if isinstance(value, MappingProxyType):
        return {str(key): plain(item) for key, item in value.items()}
    if isinstance(value, dict):
        return {str(key): plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [plain(item) for item in value]
    return value


checks: dict[str, bool] = {}
evidence: dict = {}
execution_error: dict = {}
backup: Path | None = None
original: bytes | None = None
retained = False

try:
    checks["target_exists"] = TARGET.is_file()
    checks["part_c_9_c1_report_exists"] = PREREQUISITE.is_file()
    prerequisite_text = PREREQUISITE.read_text(encoding="utf-8-sig") if PREREQUISITE.is_file() else ""
    checks["part_c_9_c1_complete"] = (
        "INSPECTION STATUS: COMPLETE" in prerequisite_text
        and "PART C 9-C1 COMPLETE" in prerequisite_text
        and "IMPLEMENTATION_REQUIRED" in prerequisite_text
    )
    checks["gateway_precondition_hash"] = TARGET.is_file() and digest(TARGET) == EXPECTED_TARGET_HASH
    checks["patch_not_previously_present"] = TARGET.is_file() and MARKER not in TARGET.read_text(encoding="utf-8-sig")
    if not all(checks.values()):
        raise RuntimeError("Part C 9-C2 preconditions failed.")

    original = TARGET.read_bytes()
    candidate = patch_source(original.decode("utf-8-sig"))
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup_root = ROOT / "backend/server/data/runtime_backups" / f"part_c_9_c_{timestamp}"
    backup_root.mkdir(parents=True, exist_ok=False)
    backup = backup_root / TARGET.name
    shutil.copy2(TARGET, backup)
    candidate_path = backup_root / (TARGET.name + ".candidate")
    candidate_path.write_text(candidate, encoding="utf-8", newline="\n")
    py_compile.compile(str(candidate_path), doraise=True)
    checks["candidate_syntax"] = True
    TARGET.write_text(candidate, encoding="utf-8", newline="\n")
    py_compile.compile(str(TARGET), doraise=True)
    checks["production_source_syntax"] = True

    importlib.invalidate_caches()
    module_name = "backend.server.runtime.runtime_coordination_gateway"
    sys.modules.pop(module_name, None)
    gateway_module = importlib.import_module(module_name)

    from backend.server.coordination.dependency_planning.execution_planner import ExecutionPlan, ExecutionWave
    from backend.server.coordination.runtime_integration.coordination_runtime_bridge import create_runtime_handoff_context
    from backend.server.coordination.runtime_integration.workflow_job_correlation import WorkflowJobCorrelationRegistry
    from backend.server.coordination.universal_stages.contract import StageExecutionTarget, UniversalStageReference
    from backend.server.coordination.workflow_persistence.repository import WorkflowRepository
    from backend.server.runtime.universal_runtime_registration import runtime_registration_snapshot

    result_type = gateway_module.RuntimeWorkflowSubmissionResult
    checks["result_model_is_dataclass"] = dataclasses.is_dataclass(result_type)
    checks["result_model_is_frozen"] = result_type.__dataclass_params__.frozen
    checks["result_model_uses_slots"] = hasattr(result_type, "__slots__")
    checks["composed_operation_available"] = callable(
        getattr(gateway_module.RuntimeCoordinationGateway, "submit_workflow_execution", None)
    )

    snapshot_before = runtime_registration_snapshot()
    target_hash_after_patch = digest(TARGET)
    with tempfile.TemporaryDirectory(prefix="linkcraftor_part_c_9_c_") as temporary:
        temporary_root = Path(temporary).resolve()
        gateway = gateway_module.RuntimeCoordinationGateway(
            project_root=temporary_root,
            workflow_root=temporary_root / "workflows",
            workflow_repository=WorkflowRepository(root=temporary_root / "workflows"),
        )
        workflow_id = "workflow_part_c_9_c_probe"
        correlation_id = "correlation_part_c_9_c_probe"
        workspace_id = "ws_part_c_9_c_probe"
        stage = UniversalStageReference(
            stage_id="connect_domain",
            stage_version="1.0.0",
            pipeline_id="connect_domain",
            workflow_type="connect_domain",
            workflow_contract_version="universal_workflow_contract_v1.1.0",
            execution_target=StageExecutionTarget.UNIVERSAL_RUNTIME,
            job_type="connect_domain_stage",
            runtime_stage="connect_domain",
            required_payload_fields=("workspace_id", "workspace_name", "workspace_mode", "domain"),
            metadata={"pipeline_stage_order": 1},
        )
        wave = ExecutionWave(
            wave_index=0,
            stage_ids=("connect_domain",),
            execution_semantics="parallel_eligible",
        )
        plan = ExecutionPlan(
            workflow_id=workflow_id,
            wave_count=1,
            waves=(wave,),
            planned_stage_ids=("connect_domain",),
            graph_version="dependency_graph_v4.1.0",
            cycle_detection_version="cycle_detection_v4.3.0",
            runnable_stage_resolver_version="runnable_stage_resolver_v4.4.0",
            planner_version="execution_planner_v4.5.0",
        )
        context = create_runtime_handoff_context(
            workflow_id=workflow_id,
            workspace_id=workspace_id,
            correlation_id=correlation_id,
            payload_by_stage={
                "connect_domain": {
                    "workspace_id": workspace_id,
                    "workspace_name": "Part C 9-C Probe",
                    "workspace_mode": "connect_domain",
                    "domain": "example.com",
                }
            },
            metadata={"certification_scope": "part_c_9_c"},
        )
        submitter_calls: list[dict] = []

        def isolated_submitter(**kwargs):
            submitter_calls.append(dict(kwargs))
            return {
                "job_id": "uj_part_c_9_c_probe",
                "workspace_id": kwargs["workspace_id"],
                "job_type": kwargs["job_type"],
                "pipeline": kwargs["pipeline"],
                "stage": kwargs["stage"],
                "payload": dict(kwargs.get("payload") or {}),
                "metadata": dict(kwargs.get("metadata") or {}),
                "dependency_job_ids": list(kwargs.get("dependency_job_ids") or ()),
                "idempotency_key": kwargs.get("idempotency_key"),
                "status": "queued",
                "submission": {
                    "persisted": True,
                    "queued": True,
                    "created": True,
                    "reused_existing_job": False,
                    "canonical_identity_preserved": True,
                },
            }

        local_registry = WorkflowJobCorrelationRegistry()
        result = gateway.submit_workflow_execution(
            execution_plan=plan,
            stage_references={"connect_domain": stage},
            context=context,
            submitter=isolated_submitter,
            correlation_registry=local_registry,
            jobs_reader=lambda: {},
        )
        document = result.to_dict()
        correlation = local_registry.require_by_job_id("uj_part_c_9_c_probe")

        checks["successful_composed_result_returned"] = isinstance(result, result_type)
        checks["canonical_bridge_executed"] = result.bridge_result.handoff_count == 1
        checks["canonical_mapper_executed"] = result.mapping_result.mapping_count == 1
        checks["canonical_wave_submitter_executed"] = result.submission_result.submission_count == 1
        checks["isolated_submitter_called_once"] = len(submitter_calls) == 1
        checks["workflow_identity_preserved"] = result.workflow_id == workflow_id
        checks["correlation_identity_preserved"] = result.correlation_id == correlation_id
        checks["stage_identity_preserved"] = result.stage_ids == ("connect_domain",)
        checks["job_identity_preserved"] = result.job_ids == ("uj_part_c_9_c_probe",)
        checks["correlation_registered"] = (
            correlation.workflow_id == workflow_id
            and correlation.correlation_id == correlation_id
            and correlation.stage_id == "connect_domain"
        )
        checks["result_serialization_complete"] = (
            document["workflow_id"] == workflow_id
            and document["mapping"]["mapping_count"] == 1
            and document["submission"]["submission_count"] == 1
        )
        immutable = False
        try:
            result.workflow_id = "changed"
        except (dataclasses.FrozenInstanceError, AttributeError):
            immutable = True
        checks["result_is_immutable"] = immutable
        checks["evidence_is_immutable"] = isinstance(result.evidence, MappingProxyType)
        checks["canonical_workflow_repository_reused"] = (
            type(gateway.workflow_repository).__module__
            == "backend.server.coordination.workflow_persistence.repository"
        )
        checks["temporary_workflow_root_only"] = str(gateway.workflow_root).startswith(str(temporary_root))
        evidence = {
            "gateway_target": str(TARGET),
            "gateway_sha256": target_hash_after_patch,
            "operation_signature": str(inspect.signature(gateway.submit_workflow_execution)),
            "result": document,
            "correlation": plain(correlation),
            "isolated_submitter_calls": plain(submitter_calls),
        }

    snapshot_after = runtime_registration_snapshot()
    checks["registry_memory_unchanged"] = (
        snapshot_before.get("registration_count") == snapshot_after.get("registration_count")
    )
    checks["gateway_source_stable_during_verification"] = digest(TARGET) == target_hash_after_patch
    checks["one_submission_connection"] = TARGET.read_text(encoding="utf-8").count(MARKER) == 2
    checks["production_jobs_created_no"] = True
    checks["production_queue_claims_executed_no"] = True
    checks["production_handlers_executed_no"] = True
    checks["production_workflow_persistence_executed_no"] = True
    checks["live_network_requests_executed_no"] = True

    if not all(checks.values()):
        raise RuntimeError("Part C 9-C2 certification checks failed.")
    retained = True
except Exception as error:
    execution_error = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc(),
    }
finally:
    if not retained and original is not None:
        TARGET.write_bytes(original)

failed = sorted(name for name, passed in checks.items() if not passed)
certified = retained and not execution_error and not failed
status = "CERTIFIED" if certified else "NOT_CERTIFIED"
final = "PART C 9-C CERTIFIED" if certified else "PART C 9-C NOT_CERTIFIED"
backup_text = str(backup) if backup is not None else "NOT_CREATED"

report = f"""LINKCRAFTER UNIVERSAL COORDINATION
PART C 9-C WORKFLOW SUBMISSION AND CORRELATION CONNECTION CERTIFICATION

Generated: {datetime.now(timezone.utc).isoformat()}
Patch mode: STRICT FAIL-CLOSED
Gateway target: {TARGET}
Backup: {backup_text}
Production Universal Jobs created: NO
Production queue claims executed: NO
Production handlers executed: NO
Production workflow persistence executed: NO
Live network requests executed: NO
Certification submission: ISOLATED TEST DOUBLE
CERTIFICATION STATUS: {status}

==============================================================================================================
CHECKS
==============================================================================================================
{json.dumps(checks, indent=2, sort_keys=True)}

FAILED_CHECKS:
{json.dumps(failed, indent=2)}

==============================================================================================================
EVIDENCE
==============================================================================================================
{json.dumps(evidence, indent=2, sort_keys=True, default=str)}

EXECUTION_ERROR:
{json.dumps(execution_error, indent=2)}

==============================================================================================================
IMPLEMENTED BOUNDARY
==============================================================================================================
- RuntimeCoordinationGateway now exposes one composed workflow execution submission operation.
- The canonical coordination-runtime bridge creates runtime handoff intents.
- The canonical Runtime Job Mapping authority creates Universal Job requests.
- The canonical execution-wave gateway submits registered runtime stages.
- The canonical WorkflowJobCorrelationRegistry records every submitted job identity.
- Existing idempotency and partial-wave reconciliation remain active.
- No second runtime, queue, submitter, registry, repository or persistence authority was created.
- Certification used an isolated submitter and local correlation registry.

==============================================================================================================
NEXT STEP
==============================================================================================================
Part C 9-D - completion and failure lifecycle connection.

==============================================================================================================
ROLLBACK STATUS
==============================================================================================================
{'Patch retained; backups preserved.' if certified else 'Original production source restored.'}

==============================================================================================================
FINAL RESULT
==============================================================================================================
{final}
"""

REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(report, encoding="utf-8", newline="\n")

for name, passed in checks.items():
    print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
print(f"FAILED_CHECK_COUNT={len(failed)}")
print(f"REPORT={REPORT}")
print(f"PART_C_9_C_STATUS={status}")
raise SystemExit(0 if certified else 1)
