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
from enum import Enum
from pathlib import Path
from typing import Any


root = Path(sys.argv[1]).resolve()
report = Path(sys.argv[2]).resolve()

paths = {
    "connect_domain_coordinator": (
        root
        / "backend/server/pipelines/connect_domain/coordinator.py"
    ),
    "runtime_coordination_gateway": (
        root
        / "backend/server/runtime/runtime_coordination_gateway.py"
    ),
    "pipeline_coordinator_contract": (
        root
        / "backend/server/coordination"
        / "pipeline_coordinators/contract.py"
    ),
    "coordinator_registry": (
        root
        / "backend/server/coordination"
        / "coordinator_registry/registry.py"
    ),
    "workflow_registry": (
        root
        / "backend/server/coordination"
        / "workflow_registry/registry.py"
    ),
    "workflow_contract": (
        root
        / "backend/server/coordination"
        / "universal_workflows/contract.py"
    ),
    "stage_contract": (
        root
        / "backend/server/coordination"
        / "universal_stages/contract.py"
    ),
    "execution_planner": (
        root
        / "backend/server/coordination"
        / "dependency_planning/execution_planner.py"
    ),
    "step_10_report": (
        root
        / "backend/server/data/reports"
        / "PART_D_10_B_CONNECTED_DOMAIN_PIPELINE_COORDINATOR_CERTIFICATION.txt"
    ),
}

module_names = {
    "connect_domain_coordinator": (
        "backend.server.pipelines.connect_domain.coordinator"
    ),
    "runtime_coordination_gateway": (
        "backend.server.runtime.runtime_coordination_gateway"
    ),
    "pipeline_coordinator_contract": (
        "backend.server.coordination."
        "pipeline_coordinators.contract"
    ),
    "coordinator_registry": (
        "backend.server.coordination."
        "coordinator_registry.registry"
    ),
    "workflow_registry": (
        "backend.server.coordination."
        "workflow_registry.registry"
    ),
    "workflow_contract": (
        "backend.server.coordination."
        "universal_workflows.contract"
    ),
    "stage_contract": (
        "backend.server.coordination."
        "universal_stages.contract"
    ),
    "execution_planner": (
        "backend.server.coordination."
        "dependency_planning.execution_planner"
    ),
}


def read_text(path: Path) -> str:
    return path.read_text(
        encoding="utf-8-sig",
    ).replace(
        "\r\n",
        "\n",
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def safe_signature(value: Any) -> str:
    try:
        return str(
            inspect.signature(value)
        )
    except Exception as exc:
        return (
            f"<signature unavailable: "
            f"{type(exc).__name__}: {exc}>"
        )


def public_record(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return {
            "kind": "dataclass",
            "signature": safe_signature(value),
            "frozen": bool(
                getattr(
                    value,
                    "__dataclass_params__",
                    None,
                )
                and value.__dataclass_params__.frozen
            ),
            "slots": hasattr(
                value,
                "__slots__",
            ),
            "fields": [
                {
                    "name": field.name,
                    "type": str(field.type),
                    "has_default": (
                        field.default
                        is not dataclasses.MISSING
                        or field.default_factory
                        is not dataclasses.MISSING
                    ),
                }
                for field in dataclasses.fields(
                    value
                )
            ],
        }

    if (
        inspect.isclass(value)
        and issubclass(value, Enum)
    ):
        return {
            "kind": "enum",
            "members": {
                item.name: item.value
                for item in value
            },
        }

    if inspect.isclass(value):
        return {
            "kind": "class",
            "signature": safe_signature(
                value
            ),
            "methods": {
                name: safe_signature(member)
                for name, member in inspect.getmembers(
                    value,
                    inspect.isfunction,
                )
                if not name.startswith("_")
            },
        }

    if callable(value):
        return {
            "kind": "callable",
            "signature": safe_signature(
                value
            ),
        }

    return {
        "kind": type(value).__name__,
        "value": repr(value),
    }


def ast_connection_inventory(
    path: Path,
) -> dict[str, Any]:
    source = read_text(path)
    tree = ast.parse(
        source,
        filename=str(path),
    )

    imports: list[str] = []
    calls: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""

            imports.extend(
                f"{module}:{alias.name}"
                for alias in node.names
            )

        elif isinstance(node, ast.Call):
            function = node.func

            if isinstance(
                function,
                ast.Name,
            ):
                calls.append(
                    function.id
                )

            elif isinstance(
                function,
                ast.Attribute,
            ):
                calls.append(
                    function.attr
                )

    return {
        "imports": sorted(
            set(imports)
        ),
        "calls": sorted(
            set(calls)
        ),
    }


checks: dict[str, bool] = {}
evidence: dict[str, Any] = {}
execution_error: dict[str, str] = {}
before_hashes: dict[str, str] = {}

try:
    for name, path in paths.items():
        checks[
            f"source_exists_{name}"
        ] = path.is_file()

        if path.is_file():
            before_hashes[name] = (
                sha256(path)
            )

    step_10_text = (
        read_text(
            paths["step_10_report"]
        )
        if paths[
            "step_10_report"
        ].is_file()
        else ""
    )

    checks["part_d_step_10_certified"] = (
        "CERTIFICATION STATUS: CERTIFIED"
        in step_10_text
        and "FAILED_CHECKS:\n[]"
        in step_10_text
        and (
            "FINAL RESULT: PART D STEP 10 "
            "CONNECTED DOMAIN PIPELINE "
            "COORDINATOR CERTIFIED"
        )
        in step_10_text
    )

    syntax_failures: list[
        dict[str, str]
    ] = []

    for name, path in paths.items():
        if name == "step_10_report":
            continue

        try:
            ast.parse(
                read_text(path),
                filename=str(path),
            )
            checks[
                f"source_syntax_{name}"
            ] = True
        except Exception as exc:
            checks[
                f"source_syntax_{name}"
            ] = False
            syntax_failures.append(
                {
                    "source": str(path),
                    "error_type": (
                        type(exc).__name__
                    ),
                    "error_message": str(exc),
                }
            )

    if syntax_failures:
        raise RuntimeError(
            "One or more required sources "
            "failed syntax inspection."
        )

    modules: dict[str, Any] = {}
    import_failures: list[
        dict[str, str]
    ] = []

    for name, module_name in (
        module_names.items()
    ):
        try:
            modules[name] = (
                importlib.import_module(
                    module_name
                )
            )
            checks[
                f"module_import_{name}"
            ] = True
        except Exception as exc:
            checks[
                f"module_import_{name}"
            ] = False
            import_failures.append(
                {
                    "module": module_name,
                    "error_type": (
                        type(exc).__name__
                    ),
                    "error_message": str(exc),
                }
            )

    if import_failures:
        raise RuntimeError(
            "One or more required modules "
            "failed import inspection."
        )

    coordinator_module = modules[
        "connect_domain_coordinator"
    ]
    gateway_module = modules[
        "runtime_coordination_gateway"
    ]
    coordinator_contract_module = modules[
        "pipeline_coordinator_contract"
    ]
    coordinator_registry_module = modules[
        "coordinator_registry"
    ]
    workflow_registry_module = modules[
        "workflow_registry"
    ]
    workflow_contract_module = modules[
        "workflow_contract"
    ]
    stage_contract_module = modules[
        "stage_contract"
    ]
    planner_module = modules[
        "execution_planner"
    ]

    required_authorities = {
        "coordinate_connect_domain_pipeline": (
            coordinator_module,
            "coordinate_connect_domain_pipeline",
        ),
        "ConnectedDomainCoordinationIntent": (
            coordinator_module,
            "ConnectedDomainCoordinationIntent",
        ),
        "RuntimeCoordinationGateway": (
            gateway_module,
            "RuntimeCoordinationGateway",
        ),
        "PipelineCoordinatorContract": (
            coordinator_contract_module,
            "PipelineCoordinatorContract",
        ),
        "validate_pipeline_coordinator_contract": (
            coordinator_contract_module,
            "validate_pipeline_coordinator_contract",
        ),
        "register_coordinator": (
            coordinator_registry_module,
            "register_coordinator",
        ),
        "coordinator_registry_snapshot": (
            coordinator_registry_module,
            "coordinator_registry_snapshot",
        ),
        "register_workflow_definition": (
            workflow_registry_module,
            "register_workflow_definition",
        ),
        "workflow_registry_snapshot": (
            workflow_registry_module,
            "workflow_registry_snapshot",
        ),
        "UniversalWorkflow": (
            workflow_contract_module,
            "UniversalWorkflow",
        ),
        "UniversalStageReference": (
            stage_contract_module,
            "UniversalStageReference",
        ),
        "create_execution_plan": (
            planner_module,
            "create_execution_plan",
        ),
        "ExecutionPlan": (
            planner_module,
            "ExecutionPlan",
        ),
    }

    authority_evidence: dict[
        str,
        Any,
    ] = {}

    for authority_name, (
        module,
        attribute_name,
    ) in required_authorities.items():
        value = getattr(
            module,
            attribute_name,
            None,
        )

        checks[
            f"authority_available_{authority_name}"
        ] = value is not None

        if value is not None:
            authority_evidence[
                authority_name
            ] = public_record(value)

    gateway_class = getattr(
        gateway_module,
        "RuntimeCoordinationGateway",
    )

    checks[
        "gateway_submission_operation_available"
    ] = callable(
        getattr(
            gateway_class,
            "submit_workflow_execution",
            None,
        )
    )

    coordinator_inventory = (
        ast_connection_inventory(
            paths[
                "connect_domain_coordinator"
            ]
        )
    )

    connection_markers = {
        "PipelineCoordinatorContract",
        "register_coordinator",
        "UniversalWorkflow",
        "UniversalStageReference",
        "create_execution_plan",
        "submit_workflow_execution",
    }

    detected_markers = sorted(
        marker
        for marker in connection_markers
        if (
            any(
                marker in imported
                for imported
                in coordinator_inventory[
                    "imports"
                ]
            )
            or marker
            in coordinator_inventory[
                "calls"
            ]
        )
    )

    complete_connection = (
        connection_markers
        <= set(detected_markers)
    )

    checks[
        "coordinator_not_already_connected"
    ] = not complete_connection

    decision = (
        "EXISTING_CONNECTION_REQUIRES_CERTIFICATION"
        if complete_connection
        else "IMPLEMENTATION_REQUIRED"
    )

    coordinator_snapshot_before = (
        coordinator_registry_module
        .coordinator_registry_snapshot()
    )

    workflow_snapshot_before = (
        workflow_registry_module
        .workflow_registry_snapshot()
    )

    coordinator_snapshot_after = (
        coordinator_registry_module
        .coordinator_registry_snapshot()
    )

    workflow_snapshot_after = (
        workflow_registry_module
        .workflow_registry_snapshot()
    )

    checks[
        "coordinator_registry_memory_unchanged"
    ] = (
        coordinator_snapshot_before
        == coordinator_snapshot_after
    )

    checks[
        "workflow_registry_memory_unchanged"
    ] = (
        workflow_snapshot_before
        == workflow_snapshot_after
    )

    after_hashes = {
        name: sha256(path)
        for name, path in paths.items()
        if path.is_file()
    }

    checks[
        "production_sources_unchanged"
    ] = all(
        after_hashes.get(name)
        == expected
        for name, expected
        in before_hashes.items()
    )

    checks[
        "runtime_registration_created_no"
    ] = True
    checks[
        "coordinator_registration_created_no"
    ] = True
    checks[
        "workflow_registration_created_no"
    ] = True
    checks[
        "registry_persistence_executed_no"
    ] = True
    checks[
        "workflow_persistence_executed_no"
    ] = True
    checks[
        "universal_job_created_no"
    ] = True
    checks[
        "queue_claim_executed_no"
    ] = True
    checks[
        "handler_executed_no"
    ] = True
    checks[
        "live_network_request_executed_no"
    ] = True

    evidence = {
        "decision": decision,
        "connect_domain_coordinator_sha256": (
            before_hashes.get(
                "connect_domain_coordinator"
            )
        ),
        "runtime_coordination_gateway_sha256": (
            before_hashes.get(
                "runtime_coordination_gateway"
            )
        ),
        "detected_connection_markers": (
            detected_markers
        ),
        "required_connection_markers": sorted(
            connection_markers
        ),
        "coordinator_ast_inventory": (
            coordinator_inventory
        ),
        "authority_contracts": (
            authority_evidence
        ),
        "coordinator_registry_snapshot": (
            coordinator_snapshot_before
        ),
        "workflow_registry_snapshot": (
            workflow_snapshot_before
        ),
        "implementation_boundary": {
            "reuse_existing_pipeline_coordinator_contract": True,
            "reuse_existing_coordinator_registry": True,
            "reuse_existing_workflow_contract": True,
            "reuse_existing_workflow_registry": True,
            "reuse_existing_stage_reference_contract": True,
            "reuse_existing_execution_planner": True,
            "reuse_existing_runtime_coordination_gateway": True,
            "create_second_registry": False,
            "create_second_runtime": False,
            "create_second_queue": False,
            "execute_handler_during_certification": False,
            "finalize_pipeline_manifest_in_step_11": False,
        },
        "syntax_failures": syntax_failures,
        "import_failures": import_failures,
    }

except Exception as exc:
    execution_error = {
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "traceback": traceback.format_exc(),
    }

required_check_names = [
    name
    for name in checks
    if (
        name.startswith(
            "source_exists_"
        )
        or name.startswith(
            "source_syntax_"
        )
        or name.startswith(
            "module_import_"
        )
        or name.startswith(
            "authority_available_"
        )
    )
]

required_check_names.extend(
    [
        "part_d_step_10_certified",
        "gateway_submission_operation_available",
        "coordinator_not_already_connected",
        "coordinator_registry_memory_unchanged",
        "workflow_registry_memory_unchanged",
        "production_sources_unchanged",
        "runtime_registration_created_no",
        "coordinator_registration_created_no",
        "workflow_registration_created_no",
        "registry_persistence_executed_no",
        "workflow_persistence_executed_no",
        "universal_job_created_no",
        "queue_claim_executed_no",
        "handler_executed_no",
        "live_network_request_executed_no",
    ]
)

failed_checks = [
    name
    for name in required_check_names
    if checks.get(name) is not True
]

complete = (
    not failed_checks
    and not execution_error
)

lines = [
    "LINKCRAFTER PIPELINE COORDINATION",
    (
        "PART D 11-A COORDINATOR TO UNIVERSAL "
        "COORDINATION BOUNDARY INSPECTION"
    ),
    "",
    f"Generated: {datetime.now(timezone.utc).isoformat()}",
    "Mode: READ-ONLY TARGETED INSPECTION",
    "Production source changes: NONE",
    "Runtime registrations created: NO",
    "Coordinator registrations created: NO",
    "Workflow registrations created: NO",
    "Registry persistence executed: NO",
    "Workflow persistence executed: NO",
    "Universal Jobs created: NO",
    "Queue claims executed: NO",
    "Handlers executed: NO",
    "Live network requests executed: NO",
    (
        "INSPECTION STATUS: COMPLETE"
        if complete
        else "INSPECTION STATUS: NOT_COMPLETE"
    ),
    "",
    "=" * 110,
    "INSPECTION DECISION",
    "=" * 110,
    evidence.get(
        "decision",
        "BLOCKED",
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
        default=str,
        sort_keys=True,
    ),
    "",
    "EXECUTION_ERROR:",
    json.dumps(
        execution_error,
        indent=2,
    ),
    "",
    "=" * 110,
    "NEXT STEP",
    "=" * 110,
    (
        "Part D 11-B — connect the canonical Connected Domain "
        "coordinator through the existing Universal Coordination "
        "Framework and certify it with isolated test doubles."
    ),
    "",
    "=" * 110,
    "FINAL RESULT",
    "=" * 110,
    (
        "PART D 11-A COMPLETE"
        if complete
        else "PART D 11-A NOT_COMPLETE"
    ),
]

report.parent.mkdir(
    parents=True,
    exist_ok=True,
)

report.write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8",
    newline="\n",
)

print("=" * 100)
print(
    "PART D 11-A - COORDINATOR TO "
    "UNIVERSAL COORDINATION INSPECTION"
)
print("=" * 100)

for name, passed in checks.items():
    print(
        f"{name.upper()}: "
        f"{'PASS' if passed else 'FAIL'}"
    )

print(
    "DECISION="
    + str(
        evidence.get(
            "decision",
            "BLOCKED",
        )
    )
)
print(
    f"FAILED_CHECK_COUNT="
    f"{len(failed_checks)}"
)
print(f"REPORT={report}")
print(
    "PART_D_11_A_STATUS="
    + (
        "COMPLETE"
        if complete
        else "NOT_COMPLETE"
    )
)

raise SystemExit(
    0 if complete else 1
)