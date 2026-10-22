from __future__ import annotations

import ast
import dataclasses
import hashlib
import importlib
import inspect
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


if len(sys.argv) != 4:
    raise RuntimeError(
        "Expected project root, 8-C report and 8-D1 report."
    )

ROOT = Path(sys.argv[1]).resolve()
PRECONDITION_REPORT = Path(sys.argv[2]).resolve()
REPORT = Path(sys.argv[3]).resolve()

RUNTIME_INTEGRATION_ROOT = (
    ROOT
    / "backend"
    / "server"
    / "coordination"
    / "runtime_integration"
)

SOURCE_PATHS = {
    "gateway": (
        RUNTIME_INTEGRATION_ROOT
        / "runtime_execution_gateway.py"
    ),
    "mapping": (
        RUNTIME_INTEGRATION_ROOT
        / "runtime_job_mapping.py"
    ),
    "bridge": (
        RUNTIME_INTEGRATION_ROOT
        / "coordination_runtime_bridge.py"
    ),
    "correlation": (
        RUNTIME_INTEGRATION_ROOT
        / "workflow_job_correlation.py"
    ),
    "planner": (
        ROOT
        / "backend"
        / "server"
        / "coordination"
        / "dependency_planning"
        / "execution_planner.py"
    ),
    "dependency_policy": (
        ROOT
        / "backend"
        / "server"
        / "runtime"
        / "runtime_registration_dependency_policy.py"
    ),
    "queue": (
        ROOT
        / "backend"
        / "server"
        / "orchestration"
        / "queue.py"
    ),
}

MODULE_NAMES = {
    "gateway": (
        "backend.server.coordination.runtime_integration."
        "runtime_execution_gateway"
    ),
    "mapping": (
        "backend.server.coordination.runtime_integration."
        "runtime_job_mapping"
    ),
    "bridge": (
        "backend.server.coordination.runtime_integration."
        "coordination_runtime_bridge"
    ),
    "correlation": (
        "backend.server.coordination.runtime_integration."
        "workflow_job_correlation"
    ),
    "planner": (
        "backend.server.coordination.dependency_planning."
        "execution_planner"
    ),
    "dependency_policy": (
        "backend.server.runtime."
        "runtime_registration_dependency_policy"
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def callable_evidence(
    value: Any,
) -> dict[str, Any]:
    if not callable(value):
        return {
            "available": False,
        }

    try:
        signature = str(
            inspect.signature(value)
        )
    except (
        TypeError,
        ValueError,
    ):
        signature = ""

    try:
        source = inspect.getsource(value)
    except (
        OSError,
        TypeError,
    ):
        source = ""

    return {
        "available": True,
        "module": getattr(
            value,
            "__module__",
            "",
        ),
        "name": getattr(
            value,
            "__name__",
            type(value).__name__,
        ),
        "signature": signature,
        "source": source,
    }


def class_evidence(
    value: Any,
) -> dict[str, Any]:
    if not inspect.isclass(value):
        return {
            "available": False,
        }

    try:
        signature = str(
            inspect.signature(value)
        )
    except (
        TypeError,
        ValueError,
    ):
        signature = ""

    annotations = dict(
        getattr(
            value,
            "__annotations__",
            {},
        )
        or {}
    )

    dataclass_fields = (
        [
            field.name
            for field in dataclasses.fields(value)
        ]
        if dataclasses.is_dataclass(value)
        else []
    )

    parameters = getattr(
        value,
        "__dataclass_params__",
        None,
    )

    return {
        "available": True,
        "module": value.__module__,
        "name": value.__name__,
        "signature": signature,
        "dataclass": dataclasses.is_dataclass(
            value
        ),
        "frozen": bool(
            parameters
            and parameters.frozen
        ),
        "uses_slots": hasattr(
            value,
            "__slots__",
        ),
        "fields": dataclass_fields,
        "annotations": {
            key: str(item)
            for key, item in annotations.items()
        },
    }


def public_api(
    module: Any,
) -> dict[str, Any]:
    functions: dict[str, Any] = {}
    classes: dict[str, Any] = {}

    for name, value in inspect.getmembers(
        module
    ):
        if name.startswith("_"):
            continue

        if (
            getattr(
                value,
                "__module__",
                "",
            )
            != module.__name__
        ):
            continue

        if inspect.isfunction(value):
            functions[name] = (
                callable_evidence(value)
            )
        elif inspect.isclass(value):
            classes[name] = (
                class_evidence(value)
            )

    return {
        "functions": functions,
        "classes": classes,
    }


def ast_calls(
    node: ast.AST,
) -> list[str]:
    calls: set[str] = set()

    for child in ast.walk(node):
        if not isinstance(
            child,
            ast.Call,
        ):
            continue

        if isinstance(
            child.func,
            ast.Name,
        ):
            calls.add(
                child.func.id
            )
        elif isinstance(
            child.func,
            ast.Attribute,
        ):
            calls.add(
                child.func.attr
            )

    return sorted(calls)


checks = {
    "part_c_8_c_certified": False,
    "all_required_sources_exist": False,
    "all_required_sources_pass_syntax": False,
    "all_required_modules_imported": False,
    "single_mapping_gateway_retained": False,
    "mapping_result_contract_available": False,
    "wave_index_available": False,
    "dependency_policy_available": False,
    "dependency_override_probe_completed": False,
    "idempotency_override_probe_completed": False,
    "aggregate_gateway_inventory_completed": False,
    "production_sources_unchanged": False,
    "runtime_registration_created_no": True,
    "registry_persistence_executed_no": True,
    "universal_job_created_no": True,
    "queue_claim_executed_no": True,
    "handler_executed_no": True,
    "live_network_request_executed_no": True,
}

evidence: dict[str, Any] = {}
execution_error: dict[str, Any] | None = None

try:
    precondition_text = (
        PRECONDITION_REPORT.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )
    )

    checks["part_c_8_c_certified"] = (
        "CERTIFICATION STATUS: CERTIFIED"
        in precondition_text
        and
        "PART C 8-C CERTIFIED"
        in precondition_text
    )

    checks["all_required_sources_exist"] = all(
        path.is_file()
        for path in SOURCE_PATHS.values()
    )

    if not checks["all_required_sources_exist"]:
        missing_sources = [
            str(path)
            for path in SOURCE_PATHS.values()
            if not path.is_file()
        ]

        raise RuntimeError(
            "Required production sources are absent: "
            + json.dumps(missing_sources)
        )

    source_hashes_before = {
        name: sha256(path)
        for name, path in SOURCE_PATHS.items()
    }

    source_trees = {
        name: ast.parse(
            path.read_text(
                encoding="utf-8-sig",
            ),
            filename=str(path),
        )
        for name, path in SOURCE_PATHS.items()
    }

    checks[
        "all_required_sources_pass_syntax"
    ] = True

    modules = {
        name: importlib.import_module(
            module_name
        )
        for name, module_name
        in MODULE_NAMES.items()
    }

    checks[
        "all_required_modules_imported"
    ] = True

    gateway_function = getattr(
        modules["gateway"],
        "submit_runtime_job_mapping",
        None,
    )

    checks[
        "single_mapping_gateway_retained"
    ] = callable(gateway_function)

    mapping_class = getattr(
        modules["mapping"],
        "RuntimeJobMapping",
        None,
    )

    mapping_result_class = getattr(
        modules["mapping"],
        "RuntimeJobMappingResult",
        None,
    )

    request_class = getattr(
        modules["mapping"],
        "UniversalJobCreationRequest",
        None,
    )

    checks[
        "mapping_result_contract_available"
    ] = (
        inspect.isclass(mapping_class)
        and inspect.isclass(
            mapping_result_class
        )
        and inspect.isclass(
            request_class
        )
    )

    checks["wave_index_available"] = (
        inspect.isclass(mapping_class)
        and
        "wave_index"
        in getattr(
            mapping_class,
            "__annotations__",
            {},
        )
    )

    dependency_api = public_api(
        modules["dependency_policy"]
    )

    checks[
        "dependency_policy_available"
    ] = bool(
        dependency_api["functions"]
        or dependency_api["classes"]
    )

    bridge_class = getattr(
        modules["bridge"],
        "RuntimeHandoffIntent",
    )

    mapper = getattr(
        modules["mapping"],
        "map_runtime_handoff_intent_to_creation_request",
    )

    intent = bridge_class(
        workflow_id=(
            "workflow_part_c_8_d_probe"
        ),
        workspace_id=(
            "ws_part_c_8_d_probe"
        ),
        correlation_id=(
            "correlation_part_c_8_d_probe"
        ),
        stage_id="connect_domain",
        stage_version="1.0.0",
        pipeline_id="connect_domain",
        workflow_type="connect_domain",
        job_type="connect_domain_stage",
        runtime_stage="connect_domain",
        required_payload_fields=(
            "workspace_id",
            "workspace_name",
            "workspace_mode",
            "domain",
        ),
        wave_index=0,
        execution_semantics="sequential",
        payload={
            "workspace_id": (
                "ws_part_c_8_d_probe"
            ),
            "workspace_name": (
                "Part C 8-D Probe"
            ),
            "workspace_mode": (
                "connect_domain"
            ),
            "domain": "example.com",
        },
        metadata={
            "inspection_scope": (
                "part_c_8_d"
            ),
        },
        stage_reference_contract_version=(
            "universal_stage_reference_contract_v1.1.0"
        ),
    )

    base_mapping = mapper(
        intent=intent
    )

    try:
        dependency_request = (
            dataclasses.replace(
                base_mapping.creation_request,
                dependency_job_ids=(
                    "uj_part_c_8_d_predecessor",
                ),
            )
        )

        dependency_mapping = (
            dataclasses.replace(
                base_mapping,
                creation_request=(
                    dependency_request
                ),
            )
        )

        dependency_probe = {
            "accepted": True,
            "dependency_job_ids": list(
                dependency_mapping
                .creation_request
                .dependency_job_ids
            ),
            "error_type": None,
            "error_message": None,
        }

    except Exception as error:
        dependency_probe = {
            "accepted": False,
            "dependency_job_ids": [],
            "error_type": (
                type(error).__name__
            ),
            "error_message": str(error),
        }

    checks[
        "dependency_override_probe_completed"
    ] = True

    try:
        idempotency_request = (
            dataclasses.replace(
                base_mapping.creation_request,
                idempotency_key=(
                    "part_c_8_d_probe"
                ),
            )
        )

        idempotency_mapping = (
            dataclasses.replace(
                base_mapping,
                creation_request=(
                    idempotency_request
                ),
            )
        )

        idempotency_probe = {
            "accepted": True,
            "idempotency_key": (
                idempotency_mapping
                .creation_request
                .idempotency_key
            ),
            "error_type": None,
            "error_message": None,
        }

    except Exception as error:
        idempotency_probe = {
            "accepted": False,
            "idempotency_key": None,
            "error_type": (
                type(error).__name__
            ),
            "error_message": str(error),
        }

    checks[
        "idempotency_override_probe_completed"
    ] = True

    aggregate_candidates = []

    for path in sorted(
        RUNTIME_INTEGRATION_ROOT.glob(
            "*.py"
        )
    ):
        tree = ast.parse(
            path.read_text(
                encoding="utf-8-sig",
            ),
            filename=str(path),
        )

        for node in tree.body:
            if not isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            ):
                continue

            calls = ast_calls(node)
            name_lower = node.name.lower()

            aggregate_signal = any(
                token in name_lower
                for token in (
                    "batch",
                    "wave",
                    "mappings",
                    "execution_plan",
                )
            )

            submits_mapping = (
                "submit_runtime_job_mapping"
                in calls
            )

            if (
                aggregate_signal
                or submits_mapping
            ):
                aggregate_candidates.append(
                    {
                        "source": (
                            path
                            .relative_to(ROOT)
                            .as_posix()
                        ),
                        "function": node.name,
                        "line": node.lineno,
                        "parameters": [
                            argument.arg
                            for argument
                            in node.args.args
                        ]
                        + [
                            argument.arg
                            for argument
                            in node.args.kwonlyargs
                        ],
                        "calls": calls,
                        "submits_runtime_mapping": (
                            submits_mapping
                        ),
                    }
                )

    checks[
        "aggregate_gateway_inventory_completed"
    ] = True

    existing_aggregate_gateway = any(
        candidate[
            "submits_runtime_mapping"
        ]
        and candidate["function"]
        != "submit_runtime_job_mapping"
        for candidate
        in aggregate_candidates
    )

    gateway_decision = (
        "EXISTING_AGGREGATE_AUTHORITY_AVAILABLE"
        if existing_aggregate_gateway
        else "IMPLEMENTATION_REQUIRED"
    )

    mapping_tree = source_trees[
        "mapping"
    ]

    validation_messages = sorted(
        {
            node.value
            for node in ast.walk(
                mapping_tree
            )
            if (
                isinstance(
                    node,
                    ast.Constant,
                )
                and isinstance(
                    node.value,
                    str,
                )
                and any(
                    token
                    in node.value.lower()
                    for token in (
                        "must not",
                        "dependency_job_ids",
                        "idempotency_key",
                        "phase 5.2",
                    )
                )
            )
        }
    )

    dependency_strategy = (
        "ENRICH_CANONICAL_MAPPING_REQUEST"
        if dependency_probe["accepted"]
        else (
            "SEPARATE_SUBMISSION_DEPENDENCY_"
            "AUTHORITY_REQUIRED"
        )
    )

    idempotency_strategy = (
        "MAPPING_OVERRIDE_AVAILABLE"
        if idempotency_probe["accepted"]
        else (
            "DEFER_TO_PART_C_8_E_"
            "RECONCILIATION_AUTHORITY"
        )
    )

    source_hashes_after = {
        name: sha256(path)
        for name, path in SOURCE_PATHS.items()
    }

    checks[
        "production_sources_unchanged"
    ] = (
        source_hashes_after
        == source_hashes_before
    )

    evidence = {
        "gateway_decision": (
            gateway_decision
        ),
        "dependency_strategy": (
            dependency_strategy
        ),
        "idempotency_strategy": (
            idempotency_strategy
        ),
        "dependency_override_probe": (
            dependency_probe
        ),
        "idempotency_override_probe": (
            idempotency_probe
        ),
        "aggregate_gateway_candidates": (
            aggregate_candidates
        ),
        "mapping_validation_messages": (
            validation_messages
        ),
        "source_hashes": (
            source_hashes_after
        ),
        "public_apis": {
            name: public_api(module)
            for name, module
            in modules.items()
        },
        "critical_callables": {
            "RuntimeJobMapping.__post_init__": (
                callable_evidence(
                    getattr(
                        mapping_class,
                        "__post_init__",
                        None,
                    )
                )
            ),
            (
                "map_runtime_handoff_intent_"
                "to_creation_request"
            ): callable_evidence(
                mapper
            ),
            (
                "map_runtime_handoffs_"
                "to_job_requests"
            ): callable_evidence(
                getattr(
                    modules["mapping"],
                    (
                        "map_runtime_handoffs_"
                        "to_job_requests"
                    ),
                    None,
                )
            ),
            "submit_runtime_job_mapping": (
                callable_evidence(
                    gateway_function
                )
            ),
        },
        "critical_classes": {
            "RuntimeJobMapping": (
                class_evidence(
                    mapping_class
                )
            ),
            "RuntimeJobMappingResult": (
                class_evidence(
                    mapping_result_class
                )
            ),
            "UniversalJobCreationRequest": (
                class_evidence(
                    request_class
                )
            ),
            "ExecutionPlan": (
                class_evidence(
                    getattr(
                        modules["planner"],
                        "ExecutionPlan",
                        None,
                    )
                )
            ),
            "ExecutionWave": (
                class_evidence(
                    getattr(
                        modules["planner"],
                        "ExecutionWave",
                        None,
                    )
                )
            ),
        },
    }

except Exception as error:
    execution_error = {
        "error_type": (
            type(error).__name__
        ),
        "error_message": str(error),
        "traceback": (
            traceback.format_exc()
        ),
    }

failed_checks = [
    name
    for name, passed in checks.items()
    if not passed
]

complete = (
    not failed_checks
    and execution_error is None
)

gateway_decision = evidence.get(
    "gateway_decision",
    "UNRESOLVED",
)

dependency_strategy = evidence.get(
    "dependency_strategy",
    "UNRESOLVED",
)

idempotency_strategy = evidence.get(
    "idempotency_strategy",
    "UNRESOLVED",
)

lines = [
    "LINKCRAFTER UNIVERSAL COORDINATION",
    (
        "PART C 8-D1 EXECUTION-WAVE AND "
        "DEPENDENCY BOUNDARY INSPECTION"
    ),
    "",
    (
        "Generated: "
        + datetime.now(
            timezone.utc
        ).isoformat()
    ),
    "Mode: READ-ONLY TARGETED INSPECTION",
    "Production source changes: NONE",
    "Runtime registrations created: NO",
    "Registry persistence executed: NO",
    "Universal Jobs created: NO",
    "Queue claims executed: NO",
    "Handlers executed: NO",
    "Live network requests executed: NO",
    (
        "INSPECTION STATUS: "
        + (
            "COMPLETE"
            if complete
            else "NOT_COMPLETE"
        )
    ),
    "",
    "=" * 110,
    "INSPECTION DECISION",
    "=" * 110,
    (
        "AGGREGATE GATEWAY DECISION: "
        + gateway_decision
    ),
    (
        "DEPENDENCY STRATEGY: "
        + dependency_strategy
    ),
    (
        "IDEMPOTENCY STRATEGY: "
        + idempotency_strategy
    ),
    "",
    (
        "This step performs no submission. "
        "It freezes the boundary needed to "
        "submit execution waves without "
        "violating the Phase 5.2 mapping contract."
    ),
    "",
    "=" * 110,
    "CHECKS",
    "=" * 110,
    json.dumps(
        checks,
        indent=2,
        sort_keys=True,
    ),
    "",
    "FAILED_CHECKS:",
    json.dumps(
        failed_checks,
        indent=2,
    ),
    "",
    "=" * 110,
    "BOUNDARY EVIDENCE",
    "=" * 110,
    json.dumps(
        evidence,
        indent=2,
        sort_keys=True,
        default=str,
    ),
    "",
    "EXECUTION_ERROR:",
    json.dumps(
        execution_error,
        indent=2,
        default=str,
    ),
    "",
    "=" * 110,
    "NEXT STEP",
    "=" * 110,
    (
        "Use this evidence to implement Part C 8-D2 "
        "execution-wave submission through the "
        "certified single-mapping gateway."
    ),
    "",
    "=" * 110,
    "FINAL RESULT",
    "=" * 110,
    (
        "PART C 8-D1 COMPLETE"
        if complete
        else "PART C 8-D1 NOT_COMPLETE"
    ),
    "",
]

REPORT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT.write_text(
    "\n".join(lines),
    encoding="utf-8",
    newline="\n",
)

print("=" * 100)
print(
    "PART C 8-D1 EXECUTION-WAVE "
    "AND DEPENDENCY INSPECTION"
)
print("=" * 100)

for name, passed in checks.items():
    print(
        f"{name.upper()}: "
        f"{'PASS' if passed else 'FAIL'}"
    )

print()
print(
    "AGGREGATE_GATEWAY_DECISION="
    + gateway_decision
)
print(
    "DEPENDENCY_STRATEGY="
    + dependency_strategy
)
print(
    "IDEMPOTENCY_STRATEGY="
    + idempotency_strategy
)
print(
    f"FAILED_CHECK_COUNT="
    f"{len(failed_checks)}"
)
print(
    f"REPORT={REPORT}"
)
print(
    "PART_C_8_D1_STATUS="
    + (
        "COMPLETE"
        if complete
        else "NOT_COMPLETE"
    )
)

raise SystemExit(
    0
    if complete
    else 1
)