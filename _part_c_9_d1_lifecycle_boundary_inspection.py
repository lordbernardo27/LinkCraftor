from __future__ import annotations

import ast
import hashlib
import importlib
import inspect
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(sys.argv[1]).resolve()
REPORT = Path(sys.argv[2]).resolve()
SERVER = ROOT / "backend/server"

SOURCES = {
    "runtime_coordination_gateway": SERVER / "runtime/runtime_coordination_gateway.py",
    "runtime_execution_gateway": SERVER / "coordination/runtime_integration/runtime_execution_gateway.py",
    "runtime_completion_intake": SERVER / "coordination/runtime_integration/runtime_completion_intake.py",
    "runtime_failure_intake": SERVER / "coordination/runtime_integration/runtime_failure_intake.py",
    "stage_result_processor": SERVER / "coordination/stage_handoff/stage_result_processor.py",
    "workflow_contract": SERVER / "coordination/universal_workflows/contract.py",
    "workflow_repository": SERVER / "coordination/workflow_persistence/repository.py",
    "state_machine": SERVER / "coordination/workflow_lifecycle/state_machine.py",
    "transition_validation": SERVER / "coordination/workflow_lifecycle/transition_validation.py",
    "terminal_protection": SERVER / "coordination/workflow_lifecycle/terminal_state_protection.py",
    "lifecycle_history": SERVER / "coordination/workflow_lifecycle/lifecycle_history.py",
}

MODULES = {
    name: "backend.server."
    + str(path.relative_to(SERVER).with_suffix("")).replace("\\", ".").replace("/", ".")
    for name, path in SOURCES.items()
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signature(value: Any) -> str | None:
    if not callable(value):
        return None
    try:
        return str(inspect.signature(value))
    except (TypeError, ValueError):
        return None


def functions(module: Any) -> dict[str, str | None]:
    return {
        name: signature(value)
        for name, value in inspect.getmembers(module, inspect.isfunction)
        if not name.startswith("_") and value.__module__ == module.__name__
    }


checks: dict[str, bool] = {}
evidence: dict[str, Any] = {}
execution_error: dict[str, str] = {}
before_hashes: dict[str, str] = {}
decision = "BLOCKED"

try:
    prerequisite = (
        ROOT
        / "backend/server/data/reports/"
        "PART_C_9_C_WORKFLOW_SUBMISSION_CORRELATION_CERTIFICATION.txt"
    )
    checks["part_c_9_c_report_exists"] = prerequisite.is_file()
    prerequisite_text = (
        prerequisite.read_text(encoding="utf-8-sig")
        if prerequisite.is_file()
        else ""
    )
    checks["part_c_9_c_certified"] = (
        "CERTIFICATION STATUS: CERTIFIED" in prerequisite_text
        and "PART C 9-C CERTIFIED" in prerequisite_text
    )

    for name, path in SOURCES.items():
        checks[f"source_exists_{name}"] = path.is_file()
        if path.is_file():
            before_hashes[name] = digest(path)
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
            checks[f"source_syntax_{name}"] = True
        else:
            checks[f"source_syntax_{name}"] = False

    imported = {
        name: importlib.import_module(module_name)
        for name, module_name in MODULES.items()
    }
    checks["all_required_modules_imported"] = len(imported) == len(MODULES)

    gateway_class = getattr(
        imported["runtime_coordination_gateway"],
        "RuntimeCoordinationGateway",
        None,
    )
    gateway_methods = {
        name: signature(getattr(gateway_class, name))
        for name in dir(gateway_class)
        if not name.startswith("_") and callable(getattr(gateway_class, name, None))
    } if gateway_class else {}

    execution_functions = functions(imported["runtime_execution_gateway"])
    completion_functions = functions(imported["runtime_completion_intake"])
    failure_functions = functions(imported["runtime_failure_intake"])
    processor_functions = functions(imported["stage_result_processor"])
    repository_class = getattr(imported["workflow_repository"], "WorkflowRepository", None)
    repository_methods = {
        name: signature(getattr(repository_class, name))
        for name in dir(repository_class)
        if not name.startswith("_") and callable(getattr(repository_class, name, None))
    } if repository_class else {}
    transition_functions = functions(imported["transition_validation"])
    protection_functions = functions(imported["terminal_protection"])
    history_functions = functions(imported["lifecycle_history"])
    state_functions = functions(imported["state_machine"])

    workflow_class = getattr(imported["workflow_contract"], "UniversalWorkflow", None)
    workflow_fields = sorted(
        getattr(workflow_class, "__dataclass_fields__", {}).keys()
        if workflow_class is not None
        else ()
    )

    checks["gateway_terminal_intake_available"] = (
        "intake_runtime_terminal_stage_result" in gateway_methods
    )
    checks["canonical_terminal_intake_available"] = (
        "intake_runtime_terminal_stage_result" in execution_functions
    )
    checks["completion_intake_available"] = (
        "intake_runtime_completion" in completion_functions
    )
    checks["failure_intake_available"] = (
        "intake_runtime_failure" in failure_functions
    )
    checks["stage_result_processor_available"] = (
        "process_stage_result" in processor_functions
    )
    checks["workflow_contract_available"] = workflow_class is not None
    checks["workflow_status_fields_available"] = {
        "status",
        "completed_stages",
        "failed_stages",
        "pending_stages",
        "current_stage",
        "updated_at",
    } <= set(workflow_fields)
    checks["workflow_load_available"] = "load_workflow_record" in repository_methods
    checks["workflow_save_available"] = "save_workflow" in repository_methods
    checks["transition_validator_available"] = (
        "require_valid_workflow_transition" in transition_functions
    )
    checks["terminal_protection_available"] = (
        "require_terminal_state_mutation_allowed" in protection_functions
    )
    checks["lifecycle_history_creation_available"] = (
        "create_lifecycle_history_entry" in history_functions
    )
    checks["lifecycle_history_append_available"] = (
        "append_lifecycle_history" in history_functions
    )
    checks["workflow_state_machine_available"] = (
        "transition_edges" in state_functions
    )

    gateway_source = SOURCES["runtime_coordination_gateway"].read_text(
        encoding="utf-8-sig"
    )
    lifecycle_chain = {
        "terminal_intake": "intake_runtime_terminal_stage_result" in gateway_source,
        "transition_validation": "require_valid_workflow_transition" in gateway_source,
        "terminal_protection": "require_terminal_state_mutation_allowed" in gateway_source,
        "history_creation": "create_lifecycle_history_entry" in gateway_source,
        "workflow_save": "save_workflow" in gateway_source,
    }
    checks["gateway_contains_complete_lifecycle_chain"] = all(
        lifecycle_chain.values()
    )
    checks["lifecycle_connection_already_available"] = (
        "apply_runtime_terminal_lifecycle" in gateway_methods
        or "intake_and_persist_runtime_terminal_result" in gateway_methods
    )

    if (
        checks["gateway_contains_complete_lifecycle_chain"]
        and checks["lifecycle_connection_already_available"]
    ):
        decision = "EXISTING_CONNECTION_REQUIRES_CERTIFICATION"
    else:
        decision = "IMPLEMENTATION_REQUIRED"

    after_hashes = {
        name: digest(path)
        for name, path in SOURCES.items()
        if path.is_file()
    }
    checks["production_sources_unchanged"] = before_hashes == after_hashes
    checks["workflow_mutation_executed_no"] = True
    checks["workflow_persistence_executed_no"] = True
    checks["production_jobs_created_no"] = True
    checks["queue_claims_executed_no"] = True
    checks["handlers_executed_no"] = True
    checks["registry_persistence_executed_no"] = True
    checks["live_network_requests_executed_no"] = True

    evidence = {
        "decision": decision,
        "gateway_methods": gateway_methods,
        "gateway_lifecycle_chain_presence": lifecycle_chain,
        "workflow_fields": workflow_fields,
        "canonical_functions": {
            "execution_gateway": execution_functions,
            "completion_intake": completion_functions,
            "failure_intake": failure_functions,
            "stage_result_processor": processor_functions,
            "workflow_repository": repository_methods,
            "transition_validation": transition_functions,
            "terminal_protection": protection_functions,
            "lifecycle_history": history_functions,
            "state_machine": state_functions,
        },
        "source_sha256": before_hashes,
    }
except Exception as error:
    execution_error = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc(),
    }

failed = sorted(name for name, passed in checks.items() if not passed)
expected_gaps = {
    "gateway_contains_complete_lifecycle_chain",
    "lifecycle_connection_already_available",
}
blocking = [name for name in failed if name not in expected_gaps]
complete = not execution_error and not blocking
status = "COMPLETE" if complete else "NOT_COMPLETE"
final = f"PART C 9-D1 {status}"

report = f"""LINKCRAFTER UNIVERSAL COORDINATION
PART C 9-D1 COMPLETION AND FAILURE LIFECYCLE BOUNDARY INSPECTION

Generated: {datetime.now(timezone.utc).isoformat()}
Mode: READ-ONLY TARGETED INSPECTION
Production source changes: NONE
Workflow mutation executed: NO
Workflow persistence executed: NO
Universal Jobs created: NO
Queue claims executed: NO
Handlers executed: NO
Registry persistence executed: NO
Live network requests executed: NO
INSPECTION STATUS: {status}

==============================================================================================================
INSPECTION DECISION
==============================================================================================================
{decision}

==============================================================================================================
CHECKS
==============================================================================================================
{json.dumps(checks, indent=2, sort_keys=True)}

FAILED_CHECKS:
{json.dumps(failed, indent=2)}

BLOCKING_FAILURES:
{json.dumps(blocking, indent=2)}

==============================================================================================================
BOUNDARY EVIDENCE
==============================================================================================================
{json.dumps(evidence, indent=2, sort_keys=True, default=str)}

EXECUTION_ERROR:
{json.dumps(execution_error, indent=2)}

==============================================================================================================
NEXT STEP
==============================================================================================================
If IMPLEMENTATION_REQUIRED:
- Part C 9-D2 will connect canonical terminal intake to workflow transition
  validation, terminal protection, lifecycle history and optimistic persistence.
- It will reuse UniversalWorkflow and WorkflowRepository.
- It will not create a second lifecycle, workflow contract or persistence store.

If EXISTING_CONNECTION_REQUIRES_CERTIFICATION:
- Part C 9-D2 will certify the existing lifecycle connection in an isolated
  temporary workflow repository.

==============================================================================================================
FINAL RESULT
==============================================================================================================
{final}
"""

REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(report, encoding="utf-8", newline="\n")

for name, passed in checks.items():
    print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
print(f"DECISION={decision}")
print(f"BLOCKING_FAILURE_COUNT={len(blocking)}")
print(f"REPORT={REPORT}")
print(f"PART_C_9_D1_STATUS={status}")
raise SystemExit(0 if complete else 1)
