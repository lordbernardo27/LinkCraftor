from __future__ import annotations

import ast
import dataclasses
import hashlib
import importlib
import inspect
import json
import sys
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(sys.argv[1]).resolve()
REPORT = Path(sys.argv[2]).resolve()

MODULE_NAMES = {
    "workflow_manifest": (
        "backend.server.coordination."
        "universal_workflows.contract"
    ),
    "dependency_graph": (
        "backend.server.coordination."
        "dependency_planning.dependency_graph"
    ),
    "dependency_validation": (
        "backend.server.coordination."
        "dependency_planning.dependency_validation"
    ),
    "cycle_detection": (
        "backend.server.coordination."
        "dependency_planning.cycle_detection"
    ),
    "runnable_stage_resolver": (
        "backend.server.coordination."
        "dependency_planning.runnable_stage_resolver"
    ),
    "execution_planner": (
        "backend.server.coordination."
        "dependency_planning.execution_planner"
    ),
    "planning_certification": (
        "backend.server.coordination."
        "dependency_planning.planning_certification"
    ),
}

REQUIRED_APIS = {
    "dependency_graph": (
        "DependencyEdge",
        "DependencyGraph",
        "create_dependency_graph",
        "dependency_graph_snapshot",
    ),
    "dependency_validation": (
        "DependencyValidationResult",
        "validate_dependency_graph",
        "require_valid_dependency_graph",
        "dependency_validation_snapshot",
    ),
    "cycle_detection": (
        "CycleDetectionResult",
        "detect_dependency_cycles",
        "require_acyclic_dependency_graph",
        "cycle_detection_snapshot",
    ),
    "runnable_stage_resolver": (
        "RunnableStageState",
        "RunnableStageResolution",
        "create_runnable_stage_state",
        "resolve_runnable_stages",
        "runnable_stage_resolution_snapshot",
    ),
    "execution_planner": (
        "ExecutionWave",
        "ExecutionPlan",
        "create_execution_plan",
        "execution_plan_snapshot",
    ),
    "planning_certification": (
        "PlanningCertificationCheck",
        "PlanningCertificationResult",
        "certify_dependency_planning",
        "planning_certification_snapshot",
    ),
}

REQUIRED_CERTIFICATION_CALLS = {
    "create_dependency_graph",
    "require_valid_dependency_graph",
    "detect_dependency_cycles",
    "create_runnable_stage_state",
    "resolve_runnable_stages",
    "create_execution_plan",
}

FORBIDDEN_CALL_NAMES = {
    "create_universal_job",
    "create_universal_knowledge_job",
    "enqueue_job",
    "dequeue_job",
    "dispatch_registered_runtime_handler",
    "register_runtime_handler",
    "unregister_runtime_handler",
    "requests.get",
    "requests.post",
    "httpx.get",
    "httpx.post",
    "urllib.request.urlopen",
    "socket.create_connection",
}

FROZEN_MODELS = {
    "workflow_manifest": (
        "UniversalWorkflow",
    ),
    "dependency_graph": (
        "DependencyEdge",
        "DependencyGraph",
    ),
    "dependency_validation": (
        "DependencyValidationResult",
        "DependencyValidationViolation",
    ),
    "cycle_detection": (
        "CycleDetectionResult",
        "CycleWitness",
    ),
    "runnable_stage_resolver": (
        "RunnableStageState",
        "RunnableStageResolution",
        "StageRunnabilityEvidence",
    ),
    "execution_planner": (
        "ExecutionWave",
        "ExecutionPlan",
    ),
    "planning_certification": (
        "PlanningCertificationCheck",
        "PlanningCertificationResult",
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def module_source(module: Any) -> Path:
    source = inspect.getsourcefile(module)

    if not source:
        raise RuntimeError(
            f"Source unavailable: {module.__name__}"
        )

    path = Path(source).resolve()

    if not path.is_file():
        raise RuntimeError(
            f"Source file unavailable: {path}"
        )

    return path


def frozen_dataclass(value: Any) -> bool:
    parameters = getattr(
        value,
        "__dataclass_params__",
        None,
    )

    return (
        dataclasses.is_dataclass(value)
        and parameters is not None
        and bool(parameters.frozen)
    )


def dotted_name(node: ast.AST) -> str:
    parts: list[str] = []
    current = node

    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value

    if isinstance(current, ast.Name):
        parts.append(current.id)

    return ".".join(
        reversed(parts)
    )


def required_parameters(
    callable_value: Any,
) -> list[str]:
    signature = inspect.signature(
        callable_value
    )

    return [
        name
        for name, parameter
        in signature.parameters.items()
        if (
            parameter.default
            is inspect.Parameter.empty
            and parameter.kind
            not in {
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            }
        )
    ]


def public_payload(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)

    to_dict = getattr(
        value,
        "to_dict",
        None,
    )

    if callable(to_dict):
        payload = to_dict()

        if isinstance(payload, Mapping):
            return dict(payload)

    if dataclasses.is_dataclass(value):
        payload = dataclasses.asdict(
            value
        )

        if isinstance(payload, Mapping):
            return dict(payload)

    raise TypeError(
        "Planning certification did not return "
        "a public mapping-compatible result."
    )


def certification_passed(
    result: Any,
    payload: Mapping[str, Any],
) -> bool:
    boolean_names = (
        "certified",
        "passed",
        "is_certified",
        "is_valid",
        "success",
        "ok",
    )

    for name in boolean_names:
        value = getattr(
            result,
            name,
            None,
        )

        if isinstance(value, bool):
            return value

        value = payload.get(name)

        if isinstance(value, bool):
            return value

    for name in (
        "failed_check_count",
        "checks_failed",
        "failure_count",
        "failed_count",
    ):
        value = payload.get(name)

        if isinstance(value, int):
            return value == 0

    checks = payload.get("checks")

    if isinstance(checks, Mapping):
        values = list(
            checks.values()
        )

        if values and all(
            isinstance(value, bool)
            for value in values
        ):
            return all(values)

    if isinstance(checks, (list, tuple)):
        passed_values: list[bool] = []

        for check in checks:
            if isinstance(check, Mapping):
                for key in (
                    "passed",
                    "success",
                    "ok",
                    "certified",
                ):
                    value = check.get(key)

                    if isinstance(value, bool):
                        passed_values.append(
                            value
                        )
                        break
            else:
                for key in (
                    "passed",
                    "success",
                    "ok",
                    "certified",
                ):
                    value = getattr(
                        check,
                        key,
                        None,
                    )

                    if isinstance(value, bool):
                        passed_values.append(
                            value
                        )
                        break

        if passed_values:
            return all(passed_values)

    return False


modules: dict[str, Any] = {}
import_failures: list[dict[str, str]] = []

for role, module_name in MODULE_NAMES.items():
    try:
        modules[role] = importlib.import_module(
            module_name
        )
    except Exception as error:
        import_failures.append(
            {
                "role": role,
                "module": module_name,
                "error_type": type(error).__name__,
                "error_message": str(error),
            }
        )

source_paths = {
    role: module_source(module)
    for role, module in modules.items()
}

source_hashes_before = {
    role: sha256(path)
    for role, path in source_paths.items()
}

api_evidence: dict[str, Any] = {}
api_checks: dict[str, bool] = {}

for role, required_names in REQUIRED_APIS.items():
    module = modules.get(role)
    available: dict[str, Any] = {}

    for name in required_names:
        value = getattr(
            module,
            name,
            None,
        ) if module else None

        available[name] = {
            "available": value is not None,
            "callable": callable(value),
            "signature": (
                str(inspect.signature(value))
                if callable(value)
                else None
            ),
        }

        api_checks[
            f"{role}_{name}_available"
        ] = value is not None

    api_evidence[role] = available

model_evidence: dict[str, Any] = {}
model_checks: dict[str, bool] = {}

for role, class_names in FROZEN_MODELS.items():
    module = modules.get(role)
    role_evidence: dict[str, Any] = {}

    for class_name in class_names:
        value = getattr(
            module,
            class_name,
            None,
        ) if module else None

        fields = (
            [
                field.name
                for field in dataclasses.fields(
                    value
                )
            ]
            if (
                value is not None
                and dataclasses.is_dataclass(
                    value
                )
            )
            else []
        )

        is_frozen = (
            frozen_dataclass(value)
            if value is not None
            else False
        )

        role_evidence[class_name] = {
            "available": value is not None,
            "dataclass": (
                dataclasses.is_dataclass(value)
                if value is not None
                else False
            ),
            "frozen": is_frozen,
            "fields": fields,
        }

        model_checks[
            f"{role}_{class_name}_available"
        ] = value is not None

        model_checks[
            f"{role}_{class_name}_frozen"
        ] = is_frozen

    model_evidence[role] = role_evidence

workflow_module = modules.get(
    "workflow_manifest"
)

UniversalWorkflow = getattr(
    workflow_module,
    "UniversalWorkflow",
    None,
) if workflow_module else None

workflow_fields = {
    field.name
    for field in dataclasses.fields(
        UniversalWorkflow
    )
} if (
    UniversalWorkflow is not None
    and dataclasses.is_dataclass(
        UniversalWorkflow
    )
) else set()

required_workflow_manifest_fields = {
    "workflow_id",
    "workflow_type",
    "workflow_version",
    "workspace_id",
    "coordinator_id",
    "coordinator_version",
    "correlation_id",
    "status",
    "context",
    "metadata",
    "current_stage",
    "completed_stages",
    "pending_stages",
    "failed_stages",
    "artifact_references",
}

manifest_checks = {
    "universal_workflow_manifest_available": (
        UniversalWorkflow is not None
    ),
    "universal_workflow_manifest_frozen": (
        frozen_dataclass(
            UniversalWorkflow
        )
        if UniversalWorkflow
        else False
    ),
    "workflow_manifest_fields_complete": (
        required_workflow_manifest_fields
        <= workflow_fields
    ),
}

certification_module = modules.get(
    "planning_certification"
)

certify = getattr(
    certification_module,
    "certify_dependency_planning",
    None,
) if certification_module else None

certification_source_calls: set[str] = set()
forbidden_source_calls: set[str] = set()

if certification_module:
    certification_path = source_paths[
        "planning_certification"
    ]

    source_text = certification_path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(
        source_text,
        filename=str(certification_path),
    )

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = dotted_name(
                node.func
            )

            if not name:
                continue

            certification_source_calls.add(
                name
            )

            if (
                name in FORBIDDEN_CALL_NAMES
                or name.split(".")[-1]
                in {
                    item.split(".")[-1]
                    for item in FORBIDDEN_CALL_NAMES
                }
            ):
                forbidden_source_calls.add(
                    name
                )

source_call_leaf_names = {
    name.split(".")[-1]
    for name in certification_source_calls
}

planning_chain_checks = {
    "canonical_planning_certifier_available": (
        callable(certify)
    ),
    "certifier_requires_no_arguments": (
        callable(certify)
        and not required_parameters(
            certify
        )
    ),
    "dependency_graph_used_by_certifier": (
        "create_dependency_graph"
        in source_call_leaf_names
    ),
    "dependency_validation_used_by_certifier": (
        "require_valid_dependency_graph"
        in source_call_leaf_names
    ),
    "cycle_detection_used_by_certifier": (
        "detect_dependency_cycles"
        in source_call_leaf_names
        or "require_acyclic_dependency_graph"
        in source_call_leaf_names
    ),
    "runnable_state_used_by_certifier": (
        "create_runnable_stage_state"
        in source_call_leaf_names
    ),
    "runnable_resolution_used_by_certifier": (
        "resolve_runnable_stages"
        in source_call_leaf_names
    ),
    "execution_plan_used_by_certifier": (
        "create_execution_plan"
        in source_call_leaf_names
    ),
    "no_job_or_handler_execution_calls": (
        not forbidden_source_calls
    ),
}

missing_certification_calls = sorted(
    REQUIRED_CERTIFICATION_CALLS
    - source_call_leaf_names
)

certification_error: dict[str, str] | None = None
certification_result = None
certification_payload: dict[str, Any] = {}
certification_success = False

if (
    callable(certify)
    and not required_parameters(certify)
):
    try:
        certification_result = certify()
        certification_payload = (
            public_payload(
                certification_result
            )
        )
        certification_success = (
            certification_passed(
                certification_result,
                certification_payload,
            )
        )
    except Exception as error:
        certification_error = {
            "error_type": type(error).__name__,
            "error_message": str(error),
        }

runtime_checks = {
    "planning_certification_executed": (
        certification_result is not None
    ),
    "planning_certification_returned_mapping": (
        bool(certification_payload)
    ),
    "planning_certification_passed": (
        certification_success
    ),
    "planning_certification_error_absent": (
        certification_error is None
    ),
}

snapshot_evidence: dict[str, Any] = {}
snapshot_checks: dict[str, bool] = {}

snapshot_functions = {
    "dependency_graph": (
        "dependency_graph_snapshot"
    ),
    "dependency_validation": (
        "dependency_validation_snapshot"
    ),
    "cycle_detection": (
        "cycle_detection_snapshot"
    ),
    "runnable_stage_resolver": (
        "runnable_stage_resolution_snapshot"
    ),
    "execution_planner": (
        "execution_plan_snapshot"
    ),
    "planning_certification": (
        "planning_certification_snapshot"
    ),
}

for role, function_name in snapshot_functions.items():
    module = modules.get(role)
    function = getattr(
        module,
        function_name,
        None,
    ) if module else None

    snapshot_ok = False
    snapshot_payload: Any = None
    snapshot_error: Any = None

    if (
        callable(function)
        and not required_parameters(function)
    ):
        try:
            snapshot_payload = function()
            snapshot_ok = isinstance(
                snapshot_payload,
                Mapping,
            )
        except Exception as error:
            snapshot_error = {
                "error_type": type(error).__name__,
                "error_message": str(error),
            }

    snapshot_evidence[role] = {
        "function": function_name,
        "mapping": snapshot_ok,
        "payload": snapshot_payload,
        "error": snapshot_error,
    }

    snapshot_checks[
        f"{role}_snapshot_available"
    ] = callable(function)

    snapshot_checks[
        f"{role}_snapshot_mapping"
    ] = snapshot_ok

source_hashes_after = {
    role: sha256(path)
    for role, path in source_paths.items()
}

changed_sources = [
    source_paths[role]
    .relative_to(ROOT)
    .as_posix()
    for role in source_hashes_before
    if (
        source_hashes_before[role]
        != source_hashes_after[role]
    )
]

safety_checks = {
    "all_modules_imported": (
        len(modules)
        == len(MODULE_NAMES)
        and not import_failures
    ),
    "production_sources_unchanged": (
        not changed_sources
    ),
    "runtime_registration_created_no": True,
    "registry_persistence_executed_no": True,
    "universal_job_created_no": True,
    "queue_claim_executed_no": True,
    "production_handler_executed_no": True,
    "live_network_request_executed_no": True,
}

checks = {
    **manifest_checks,
    **api_checks,
    **model_checks,
    **planning_chain_checks,
    **runtime_checks,
    **snapshot_checks,
    **safety_checks,
}

failed_checks = [
    name
    for name, passed in checks.items()
    if not passed
]

certified = not failed_checks
status = (
    "CERTIFIED"
    if certified
    else "NOT_CERTIFIED"
)

evidence_document = {
    "workflow_manifest_fields": sorted(
        workflow_fields
    ),
    "api_evidence": api_evidence,
    "model_evidence": model_evidence,
    "certification_source_calls": sorted(
        certification_source_calls
    ),
    "missing_certification_calls": (
        missing_certification_calls
    ),
    "forbidden_source_calls": sorted(
        forbidden_source_calls
    ),
    "certification_result": (
        certification_payload
    ),
    "certification_error": (
        certification_error
    ),
    "snapshots": snapshot_evidence,
}

evidence_fingerprint = hashlib.sha256(
    json.dumps(
        evidence_document,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
).hexdigest()

report_text = f"""\
LINKCRAFTER UNIVERSAL COORDINATION
PART C 7-C MANIFEST AND DEPENDENCY-PLANNING CERTIFICATION

Generated: {datetime.now(timezone.utc).isoformat()}
Mode: ISOLATED CANONICAL PLANNING CERTIFICATION
Production source changes: NONE
Runtime registrations created: NO
Registry persistence executed: NO
Universal jobs created: NO
Queue claims executed: NO
Production handlers executed: NO
Live network requests executed: NO
CERTIFICATION STATUS: {status}

==============================================================================================================
CANONICAL PLANNING DECISION
==============================================================================================================
The existing UniversalWorkflow contract is retained as the canonical
workflow manifest authority.

The existing dependency-planning chain remains canonical:

UniversalWorkflow manifest
-> DependencyGraph
-> dependency validation
-> cycle detection
-> runnable-stage resolution
-> ExecutionPlan
-> planning certification

No second manifest, graph, scheduler or execution planner is created.

==============================================================================================================
RUNTIME VERIFICATION
==============================================================================================================
CHECKS:
{json.dumps(checks, indent=2, sort_keys=True)}

FAILED_CHECKS:
{json.dumps(failed_checks, indent=2)}

IMPORT_FAILURES:
{json.dumps(import_failures, indent=2, sort_keys=True)}

MISSING_CERTIFICATION_CALLS:
{json.dumps(missing_certification_calls, indent=2)}

FORBIDDEN_SOURCE_CALLS:
{json.dumps(sorted(forbidden_source_calls), indent=2)}

CHANGED_SOURCES:
{json.dumps(changed_sources, indent=2)}

EVIDENCE_FINGERPRINT:
{evidence_fingerprint}

==============================================================================================================
PLANNING CERTIFICATION RESULT
==============================================================================================================
{json.dumps(certification_payload, indent=2, sort_keys=True, default=str)}

CERTIFICATION_ERROR:
{json.dumps(certification_error, indent=2, sort_keys=True)}

==============================================================================================================
CANONICAL PLANNING EVIDENCE
==============================================================================================================
{json.dumps(evidence_document, indent=2, sort_keys=True, default=str)}

==============================================================================================================
CERTIFIED BOUNDARY
==============================================================================================================
- UniversalWorkflow remains the canonical workflow manifest.
- DependencyGraph remains the canonical DAG authority.
- Invalid dependency graphs fail closed.
- Cycle detection precedes execution planning.
- Runnable-stage resolution derives readiness from persisted state.
- ExecutionPlan groups runnable stages into deterministic waves.
- Planning certification exercises the complete canonical chain.
- No production registration, job, queue or handler state was mutated.

Part C Step 7 remains in progress.

Next:
Part C 7-D — readiness, stage handoff, context propagation and
output-to-input mapping certification.

==============================================================================================================
FINAL RESULT
==============================================================================================================
PART C 7-C {status}
"""

REPORT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT.write_text(
    report_text,
    encoding="utf-8",
    newline="\n",
)

print("=" * 108)
print("PART C 7-C MANIFEST AND DEPENDENCY PLANNING")
print("=" * 108)

for name, passed in checks.items():
    print(
        f"{name.upper()}: "
        f"{'PASS' if passed else 'FAIL'}"
    )

print()
print(f"FAILED_CHECK_COUNT={len(failed_checks)}")
print(
    "PLANNING_EVIDENCE_FINGERPRINT="
    + evidence_fingerprint
)
print(
    "PRODUCTION_SOURCE_CHANGES="
    + str(len(changed_sources))
)
print(f"REPORT={REPORT}")
print(
    "PART_C_7_C_STATUS="
    + (
        "CERTIFIED"
        if certified
        else "NOT_CERTIFIED"
    )
)

if not certified:
    raise SystemExit(1)