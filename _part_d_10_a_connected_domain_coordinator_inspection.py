from __future__ import annotations

import ast
import hashlib
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


root = Path(sys.argv[1]).resolve()
report = Path(sys.argv[2]).resolve()

paths = {
    "primary_coordinator": (
        root
        / "backend/server/pipelines/connect_domain/coordinator.py"
    ),
    "linking_coordinator": (
        root
        / "backend/server/pipelines/connect_domain"
        / "linking_target_pipeline/coordinator.py"
    ),
    "runtime_coordination_gateway": (
        root
        / "backend/server/runtime/runtime_coordination_gateway.py"
    ),
    "part_c_final_report": (
        root
        / "backend/server/data/reports"
        / "PART_C_9_E_FINAL_UNIVERSAL_COORDINATION_CERTIFICATION.txt"
    ),
}


def read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def call_name(node: ast.Call) -> str:
    value = node.func

    if isinstance(value, ast.Name):
        return value.id

    if isinstance(value, ast.Attribute):
        parts: list[str] = []
        current: ast.AST = value

        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value

        if isinstance(current, ast.Name):
            parts.append(current.id)

        return ".".join(reversed(parts))

    return ""


def inventory(path: Path) -> dict[str, Any]:
    source = read_source(path)
    tree = ast.parse(source, filename=str(path))

    functions: dict[str, dict[str, Any]] = {}
    classes: list[str] = []
    calls: set[str] = set()
    imports: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef),
        ):
            arguments = [
                argument.arg
                for argument in (
                    list(node.args.posonlyargs)
                    + list(node.args.args)
                    + list(node.args.kwonlyargs)
                )
            ]

            functions[node.name] = {
                "kind": (
                    "async"
                    if isinstance(node, ast.AsyncFunctionDef)
                    else "sync"
                ),
                "arguments": arguments,
                "line": node.lineno,
            }

        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)

        elif isinstance(node, ast.Call):
            name = call_name(node)

            if name:
                calls.add(name)

        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""

            for alias in node.names:
                imports.add(
                    f"{module}:{alias.name}"
                )

    return {
        "source": str(path),
        "sha256": sha256(path),
        "functions": dict(sorted(functions.items())),
        "classes": sorted(classes),
        "calls": sorted(calls),
        "imports": sorted(imports),
    }


checks: dict[str, bool] = {}
evidence: dict[str, Any] = {}
error: dict[str, str] = {}
before_hashes: dict[str, str] = {}

try:
    for name, path in paths.items():
        checks[f"source_exists_{name}"] = path.is_file()

        if path.is_file():
            before_hashes[name] = sha256(path)

    part_c_text = (
        read_source(paths["part_c_final_report"])
        if paths["part_c_final_report"].is_file()
        else ""
    )

    checks["part_c_certified"] = (
        "CERTIFICATION STATUS: CERTIFIED"
        in part_c_text
        and (
            "FINAL RESULT: PART C UNIVERSAL COORDINATION CERTIFIED"
            in part_c_text
        )
    )

    inventories: dict[str, Any] = {}

    for name in (
        "primary_coordinator",
        "linking_coordinator",
        "runtime_coordination_gateway",
    ):
        path = paths[name]

        try:
            inventories[name] = inventory(path)
            checks[f"source_syntax_{name}"] = True
        except Exception:
            checks[f"source_syntax_{name}"] = False
            raise

    primary = inventories["primary_coordinator"]
    linking = inventories["linking_coordinator"]
    gateway = inventories["runtime_coordination_gateway"]

    combined_calls = set(primary["calls"]) | set(
        linking["calls"]
    )
    combined_imports = set(primary["imports"]) | set(
        linking["imports"]
    )
    combined_functions = set(primary["functions"]) | set(
        linking["functions"]
    )

    coordination_markers = {
        "submit_workflow_execution",
        "RuntimeCoordinationGateway",
        "get_runtime_coordination_gateway",
    }

    detected_markers = sorted(
        marker
        for marker in coordination_markers
        if (
            any(
                marker in call
                for call in combined_calls
            )
            or any(
                marker in imported
                for imported in combined_imports
            )
        )
    )

    gateway_functions = set(gateway["functions"])

    checks["coordinator_authority_available"] = bool(
        combined_functions
    )
    checks["runtime_coordination_gateway_available"] = (
        "RuntimeCoordinationGateway"
        in gateway["classes"]
    )
    checks["workflow_submission_operation_available"] = (
        "submit_workflow_execution"
        in gateway_functions
    )

    existing_connection = (
        "submit_workflow_execution"
        in detected_markers
    )

    decision = (
        "EXISTING_COORDINATOR_REQUIRES_CERTIFICATION"
        if existing_connection
        else "IMPLEMENTATION_REQUIRED"
    )

    evidence = {
        "decision": decision,
        "existing_coordination_markers": (
            detected_markers
        ),
        "primary_coordinator": primary,
        "linking_coordinator": linking,
        "runtime_coordination_gateway": {
            "source": gateway["source"],
            "sha256": gateway["sha256"],
            "classes": gateway["classes"],
            "functions": gateway["functions"],
        },
        "coordinator_boundary": {
            "must_reuse_runtime_coordination_gateway": True,
            "must_not_dispatch_handlers_directly": True,
            "must_not_create_second_runtime": True,
            "must_not_create_second_queue": True,
            "must_not_create_second_registry": True,
            "must_not_create_second_workflow_repository": True,
        },
    }

    after_hashes = {
        name: sha256(path)
        for name, path in paths.items()
        if path.is_file()
    }

    checks["production_sources_unchanged"] = all(
        after_hashes.get(name)
        == digest
        for name, digest in before_hashes.items()
    )
    checks["runtime_registration_created_no"] = True
    checks["registry_persistence_executed_no"] = True
    checks["universal_job_created_no"] = True
    checks["queue_claim_executed_no"] = True
    checks["handler_executed_no"] = True
    checks["workflow_persistence_executed_no"] = True
    checks["live_network_request_executed_no"] = True

except Exception as exc:
    error = {
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "traceback": traceback.format_exc(),
    }

required_checks = (
    "source_exists_primary_coordinator",
    "source_exists_linking_coordinator",
    "source_exists_runtime_coordination_gateway",
    "source_exists_part_c_final_report",
    "part_c_certified",
    "source_syntax_primary_coordinator",
    "source_syntax_linking_coordinator",
    "source_syntax_runtime_coordination_gateway",
    "coordinator_authority_available",
    "runtime_coordination_gateway_available",
    "workflow_submission_operation_available",
    "production_sources_unchanged",
)

failed_checks = [
    name
    for name in required_checks
    if checks.get(name) is not True
]

complete = not failed_checks and not error

lines = [
    "LINKCRAFTER PIPELINE COORDINATION",
    "PART D 10-A CONNECTED DOMAIN COORDINATOR BOUNDARY INSPECTION",
    "",
    f"Generated: {datetime.now(timezone.utc).isoformat()}",
    "Mode: READ-ONLY TARGETED INSPECTION",
    "Production source changes: NONE",
    "Runtime registrations created: NO",
    "Registry persistence executed: NO",
    "Universal Jobs created: NO",
    "Queue claims executed: NO",
    "Handlers executed: NO",
    "Workflow persistence executed: NO",
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
    evidence.get("decision", "BLOCKED"),
    "",
    "=" * 110,
    "CHECKS",
    "=" * 110,
    json.dumps(checks, indent=2, sort_keys=True),
    "",
    "FAILED_CHECKS:",
    json.dumps(failed_checks, indent=2),
    "",
    "=" * 110,
    "BOUNDARY EVIDENCE",
    "=" * 110,
    json.dumps(evidence, indent=2, default=str),
    "",
    "EXECUTION_ERROR:",
    json.dumps(error, indent=2),
    "",
    "=" * 110,
    "NEXT STEP",
    "=" * 110,
    (
        "Part D 10-B — implement or certify one canonical "
        "Connected Domain pipeline coordinator."
    ),
    "",
    "=" * 110,
    "FINAL RESULT",
    "=" * 110,
    (
        "PART D 10-A COMPLETE"
        if complete
        else "PART D 10-A NOT_COMPLETE"
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
print("PART D 10-A - CONNECTED DOMAIN COORDINATOR INSPECTION")
print("=" * 100)

for name, passed in checks.items():
    print(
        f"{name.upper()}: "
        f"{'PASS' if passed else 'FAIL'}"
    )

print(
    "DECISION="
    + str(evidence.get("decision", "BLOCKED"))
)
print(f"FAILED_CHECK_COUNT={len(failed_checks)}")
print(f"REPORT={report}")
print(
    "PART_D_10_A_STATUS="
    + ("COMPLETE" if complete else "NOT_COMPLETE")
)

raise SystemExit(0 if complete else 1)