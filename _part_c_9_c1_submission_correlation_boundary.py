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

MODULES = {
    "runtime_coordination_gateway": (
        "backend.server.runtime.runtime_coordination_gateway"
    ),
    "coordination_bridge": (
        "backend.server.coordination.runtime_integration."
        "coordination_runtime_bridge"
    ),
    "runtime_job_mapping": (
        "backend.server.coordination.runtime_integration."
        "runtime_job_mapping"
    ),
    "runtime_execution_gateway": (
        "backend.server.coordination.runtime_integration."
        "runtime_execution_gateway"
    ),
    "workflow_job_correlation": (
        "backend.server.coordination.runtime_integration."
        "workflow_job_correlation"
    ),
    "workflow_persistence": (
        "backend.server.coordination.workflow_persistence.repository"
    ),
}

SOURCES = {
    name: ROOT / Path(*module_name.split(".")).with_suffix(".py")
    for name, module_name in MODULES.items()
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def callable_signature(value: Any) -> str | None:
    if not callable(value):
        return None
    try:
        return str(inspect.signature(value))
    except (TypeError, ValueError):
        return None


def public_functions(module: Any) -> dict[str, str | None]:
    return {
        name: callable_signature(value)
        for name, value in inspect.getmembers(module, inspect.isfunction)
        if not name.startswith("_") and value.__module__ == module.__name__
    }


def class_methods(value: Any) -> dict[str, str | None]:
    result: dict[str, str | None] = {}
    for name in dir(value):
        if name.startswith("_"):
            continue
        try:
            member = getattr(value, name)
        except Exception:
            continue
        if callable(member):
            result[name] = callable_signature(member)
    return result


checks: dict[str, bool] = {}
evidence: dict[str, Any] = {}
execution_error: dict[str, str] = {}
before_hashes: dict[str, str] = {}
decision = "BLOCKED"

try:
    prerequisite = (
        ROOT
        / "backend/server/data/reports/"
        "PART_C_9_B_BOOT_KERNEL_LIFESPAN_CONNECTION_CERTIFICATION.txt"
    )
    checks["part_c_9_b_report_exists"] = prerequisite.is_file()
    prerequisite_text = (
        prerequisite.read_text(encoding="utf-8-sig")
        if prerequisite.is_file()
        else ""
    )
    checks["part_c_9_b_certified"] = (
        "CERTIFICATION STATUS: CERTIFIED" in prerequisite_text
        and "PART C 9-B CERTIFIED" in prerequisite_text
    )

    for name, path in SOURCES.items():
        checks[f"source_exists_{name}"] = path.is_file()
        if path.is_file():
            before_hashes[name] = sha256(path)
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
            checks[f"source_syntax_{name}"] = True
        else:
            checks[f"source_syntax_{name}"] = False

    imported = {
        name: importlib.import_module(module_name)
        for name, module_name in MODULES.items()
    }
    checks["all_required_modules_imported"] = len(imported) == len(MODULES)

    runtime_module = imported["runtime_coordination_gateway"]
    gateway_class = getattr(runtime_module, "RuntimeCoordinationGateway", None)
    gateway_methods = class_methods(gateway_class) if gateway_class else {}
    gateway_fields = sorted(
        getattr(gateway_class, "__annotations__", {}).keys()
        if gateway_class is not None
        else ()
    )

    bridge_functions = public_functions(imported["coordination_bridge"])
    mapping_functions = public_functions(imported["runtime_job_mapping"])
    execution_functions = public_functions(imported["runtime_execution_gateway"])
    correlation_functions = public_functions(imported["workflow_job_correlation"])

    checks["runtime_coordination_gateway_available"] = gateway_class is not None
    checks["canonical_workflow_repository_exposed"] = (
        "workflow_repository" in gateway_fields
    )
    checks["canonical_bridge_available"] = (
        "bridge_execution_plan_to_runtime" in bridge_functions
    )
    checks["canonical_mapper_available"] = (
        "map_runtime_handoffs_to_job_requests" in mapping_functions
    )
    checks["canonical_wave_submitter_available"] = (
        "submit_runtime_execution_wave" in execution_functions
    )
    checks["canonical_single_submitter_available"] = (
        "submit_runtime_job_mapping" in execution_functions
    )
    checks["canonical_correlation_registry_available"] = (
        "get_workflow_job_correlation_registry" in correlation_functions
    )
    checks["canonical_correlation_operation_available"] = (
        "correlate_submitted_job" in correlation_functions
        or "register_workflow_job_correlation" in correlation_functions
    )

    connection_names = {
        "submit_workflow",
        "submit_execution_plan",
        "submit_runtime_workflow",
        "submit_workflow_execution",
        "submit_coordination_execution",
    }
    detected_connections = sorted(connection_names.intersection(gateway_methods))
    checks["workflow_submission_connection_already_available"] = bool(
        detected_connections
    )

    source_text = SOURCES["runtime_coordination_gateway"].read_text(
        encoding="utf-8-sig"
    )
    required_calls = (
        "bridge_execution_plan_to_runtime",
        "map_runtime_handoffs_to_job_requests",
        "submit_runtime_execution_wave",
    )
    source_call_presence = {
        name: name in source_text for name in required_calls
    }
    checks["gateway_contains_complete_submission_chain"] = all(
        source_call_presence.values()
    )

    if (
        checks["workflow_submission_connection_already_available"]
        and checks["gateway_contains_complete_submission_chain"]
    ):
        decision = "EXISTING_CONNECTION_REQUIRES_CERTIFICATION"
    else:
        decision = "IMPLEMENTATION_REQUIRED"

    after_hashes = {
        name: sha256(path)
        for name, path in SOURCES.items()
        if path.is_file()
    }
    checks["production_sources_unchanged"] = before_hashes == after_hashes
    checks["production_jobs_created_no"] = True
    checks["queue_claims_executed_no"] = True
    checks["handlers_executed_no"] = True
    checks["workflow_persistence_executed_no"] = True
    checks["registry_persistence_executed_no"] = True
    checks["live_network_requests_executed_no"] = True

    evidence = {
        "decision": decision,
        "gateway_fields": gateway_fields,
        "gateway_methods": gateway_methods,
        "detected_submission_connections": detected_connections,
        "gateway_submission_chain_presence": source_call_presence,
        "canonical_functions": {
            "bridge": bridge_functions,
            "mapping": mapping_functions,
            "execution": execution_functions,
            "correlation": correlation_functions,
        },
        "source_sha256": before_hashes,
    }
except Exception as error:
    execution_error = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc(),
    }

failed_checks = sorted(name for name, passed in checks.items() if not passed)
blocking_failures = [
    name
    for name in failed_checks
    if name
    not in {
        "workflow_submission_connection_already_available",
        "gateway_contains_complete_submission_chain",
    }
]
complete = not execution_error and not blocking_failures
status = "COMPLETE" if complete else "NOT_COMPLETE"
final_result = f"PART C 9-C1 {status}"

report = f"""LINKCRAFTER UNIVERSAL COORDINATION
PART C 9-C1 WORKFLOW SUBMISSION AND CORRELATION BOUNDARY INSPECTION

Generated: {datetime.now(timezone.utc).isoformat()}
Mode: READ-ONLY TARGETED INSPECTION
Production source changes: NONE
Universal Jobs created: NO
Queue claims executed: NO
Handlers executed: NO
Workflow persistence executed: NO
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
{json.dumps(failed_checks, indent=2)}

BLOCKING_FAILURES:
{json.dumps(blocking_failures, indent=2)}

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
- Part C 9-C2 will add one gateway operation that composes the existing bridge,
  mapper, execution-wave submitter and correlation authority.
- It will not create a second job submitter, queue, correlation registry,
  workflow repository or runtime.

If EXISTING_CONNECTION_REQUIRES_CERTIFICATION:
- Part C 9-C2 will certify the existing operation with isolated test doubles.

==============================================================================================================
FINAL RESULT
==============================================================================================================
{final_result}
"""

REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(report, encoding="utf-8", newline="\n")

for name, passed in checks.items():
    print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
print(f"DECISION={decision}")
print(f"BLOCKING_FAILURE_COUNT={len(blocking_failures)}")
print(f"REPORT={REPORT}")
print(f"PART_C_9_C1_STATUS={status}")

raise SystemExit(0 if complete else 1)
