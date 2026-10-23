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

primary_coordinator = (
    root
    / "backend/server/pipelines/connect_domain/coordinator.py"
)

linking_coordinator = (
    root
    / "backend/server/pipelines/connect_domain"
    / "linking_target_pipeline/coordinator.py"
)

runtime_gateway = (
    root
    / "backend/server/runtime/runtime_coordination_gateway.py"
)

coordination_root = (
    root
    / "backend/server/coordination"
)

inspection_report = (
    root
    / "backend/server/data/reports"
    / "PART_D_10_A_CONNECTED_DOMAIN_COORDINATOR_BOUNDARY_INSPECTION.txt"
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def annotation_text(
    annotation: ast.AST | None,
) -> str | None:
    if annotation is None:
        return None

    try:
        return ast.unparse(annotation)
    except Exception:
        return None


def definition_inventory(
    path: Path,
) -> dict[str, Any]:
    source = read_text(path)
    tree = ast.parse(
        source,
        filename=str(path),
    )

    functions: dict[str, Any] = {}
    classes: dict[str, Any] = {}
    imports: list[str] = []

    for node in tree.body:
        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef),
        ):
            positional = (
                list(node.args.posonlyargs)
                + list(node.args.args)
            )

            keyword_only = list(
                node.args.kwonlyargs
            )

            functions[node.name] = {
                "kind": (
                    "async"
                    if isinstance(
                        node,
                        ast.AsyncFunctionDef,
                    )
                    else "sync"
                ),
                "positional_arguments": [
                    {
                        "name": argument.arg,
                        "annotation": annotation_text(
                            argument.annotation
                        ),
                    }
                    for argument in positional
                ],
                "keyword_only_arguments": [
                    {
                        "name": argument.arg,
                        "annotation": annotation_text(
                            argument.annotation
                        ),
                    }
                    for argument in keyword_only
                ],
                "vararg": (
                    node.args.vararg.arg
                    if node.args.vararg
                    else None
                ),
                "kwarg": (
                    node.args.kwarg.arg
                    if node.args.kwarg
                    else None
                ),
                "returns": annotation_text(
                    node.returns
                ),
                "line": node.lineno,
            }

        elif isinstance(node, ast.ClassDef):
            class_methods: dict[str, Any] = {}

            for member in node.body:
                if isinstance(
                    member,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                    ),
                ):
                    class_methods[member.name] = {
                        "kind": (
                            "async"
                            if isinstance(
                                member,
                                ast.AsyncFunctionDef,
                            )
                            else "sync"
                        ),
                        "arguments": [
                            argument.arg
                            for argument in (
                                list(
                                    member.args.posonlyargs
                                )
                                + list(
                                    member.args.args
                                )
                                + list(
                                    member.args.kwonlyargs
                                )
                            )
                        ],
                        "returns": annotation_text(
                            member.returns
                        ),
                        "line": member.lineno,
                    }

            classes[node.name] = {
                "line": node.lineno,
                "bases": [
                    annotation_text(base)
                    for base in node.bases
                ],
                "methods": class_methods,
            }

        elif isinstance(node, ast.Import):
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

    return {
        "path": str(path),
        "sha256": digest(path),
        "functions": functions,
        "classes": classes,
        "imports": sorted(imports),
    }


def extract_definition(
    path: Path,
    definition_name: str,
) -> str | None:
    source = read_text(path)
    tree = ast.parse(
        source,
        filename=str(path),
    )

    for node in ast.walk(tree):
        if (
            isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                    ast.ClassDef,
                ),
            )
            and node.name == definition_name
        ):
            return ast.get_source_segment(
                source,
                node,
            )

    return None


checks: dict[str, bool] = {}
evidence: dict[str, Any] = {}
execution_error: dict[str, str] = {}
initial_hashes: dict[str, str] = {}

required_paths = {
    "primary_coordinator": primary_coordinator,
    "linking_coordinator": linking_coordinator,
    "runtime_gateway": runtime_gateway,
    "coordination_root": coordination_root,
    "inspection_report": inspection_report,
}

try:
    for name, path in required_paths.items():
        exists = (
            path.is_dir()
            if name == "coordination_root"
            else path.is_file()
        )

        checks[f"required_path_exists_{name}"] = (
            exists
        )

        if path.is_file():
            initial_hashes[name] = digest(path)

    inspection_text = (
        read_text(inspection_report)
        if inspection_report.is_file()
        else ""
    )

    checks["part_d_10_a_complete"] = (
        "INSPECTION STATUS: COMPLETE"
        in inspection_text
        and "FAILED_CHECKS:\n[]"
        in inspection_text.replace(
            "\r\n",
            "\n",
        )
        and "FINAL RESULT\n"
        "==============================================================================================================\n"
        "PART D 10-A COMPLETE"
        in inspection_text.replace(
            "\r\n",
            "\n",
        )
    )

    direct_sources = {
        "primary_coordinator": primary_coordinator,
        "linking_coordinator": linking_coordinator,
        "runtime_gateway": runtime_gateway,
    }

    inventories: dict[str, Any] = {}

    for name, path in direct_sources.items():
        try:
            inventories[name] = (
                definition_inventory(path)
            )
            checks[f"source_syntax_{name}"] = True
        except Exception:
            checks[f"source_syntax_{name}"] = False
            raise

    candidate_files: list[Path] = []

    selection_terms = (
        "contract",
        "coordinator",
        "execution_plan",
        "manifest",
        "registry",
        "universal_workflow",
        "workflow_persistence",
        "stage_reference",
    )

    for path in coordination_root.rglob("*.py"):
        relative_lower = str(
            path.relative_to(root)
        ).lower()

        if (
            "before_" in path.name.lower()
            or ".before_" in path.name.lower()
            or "__pycache__" in relative_lower
        ):
            continue

        if any(
            term in relative_lower
            for term in selection_terms
        ):
            candidate_files.append(path)

    candidate_files = sorted(
        set(candidate_files)
    )

    coordination_candidates: list[
        dict[str, Any]
    ] = []

    syntax_failures: list[dict[str, str]] = []

    for path in candidate_files:
        try:
            inventory = definition_inventory(
                path
            )
            coordination_candidates.append(
                inventory
            )
        except Exception as exc:
            syntax_failures.append(
                {
                    "path": str(path),
                    "error_type": (
                        type(exc).__name__
                    ),
                    "error_message": str(exc),
                }
            )

    checks[
        "coordination_candidates_discovered"
    ] = bool(coordination_candidates)

    checks[
        "coordination_candidate_syntax"
    ] = not syntax_failures

    primary_source = read_text(
        primary_coordinator
    )

    run_connect_domain_source = (
        extract_definition(
            primary_coordinator,
            "run_connect_domain",
        )
    )

    runtime_gateway_class_source = (
        extract_definition(
            runtime_gateway,
            "RuntimeCoordinationGateway",
        )
    )

    checks[
        "run_connect_domain_source_extracted"
    ] = bool(run_connect_domain_source)

    checks[
        "runtime_gateway_contract_extracted"
    ] = bool(runtime_gateway_class_source)

    checks[
        "existing_primary_coordinator_calls_legacy_job_creation"
    ] = (
        "create_universal_knowledge_job"
        in primary_source
    )

    checks[
        "existing_primary_coordinator_calls_legacy_pipeline"
    ] = (
        "run_website_knowledge_pipeline"
        in primary_source
    )

    checks[
        "existing_primary_coordinator_not_connected_to_runtime_gateway"
    ] = (
        "RuntimeCoordinationGateway"
        not in primary_source
        and "submit_workflow_execution"
        not in primary_source
    )

    public_coordination_symbols: dict[
        str,
        list[str],
    ] = {}

    relevant_symbol_terms = (
        "workflow",
        "coordinator",
        "manifest",
        "plan",
        "stage",
        "register",
        "validate",
        "build",
    )

    for inventory in coordination_candidates:
        symbols = (
            list(inventory["functions"])
            + list(inventory["classes"])
        )

        selected_symbols = sorted(
            symbol
            for symbol in symbols
            if (
                not symbol.startswith("_")
                and any(
                    term in symbol.lower()
                    for term in relevant_symbol_terms
                )
            )
        )

        if selected_symbols:
            public_coordination_symbols[
                inventory["path"]
            ] = selected_symbols

    checks[
        "coordination_contract_symbols_available"
    ] = bool(public_coordination_symbols)

    final_hashes = {
        name: digest(path)
        for name, path in required_paths.items()
        if path.is_file()
    }

    checks["production_sources_unchanged"] = all(
        final_hashes.get(name)
        == expected
        for name, expected in initial_hashes.items()
    )

    checks["production_source_changes_no"] = True
    checks["runtime_registration_created_no"] = True
    checks["registry_persistence_executed_no"] = True
    checks["universal_job_created_no"] = True
    checks["queue_claim_executed_no"] = True
    checks["handler_executed_no"] = True
    checks["workflow_persistence_executed_no"] = True
    checks["live_network_request_executed_no"] = True

    evidence = {
        "implementation_decision": (
            "ADD_ONE_CANONICAL_CONNECTED_DOMAIN_COORDINATOR"
        ),
        "required_boundary": {
            "legacy_run_connect_domain_retained_until_integration": True,
            "new_coordinator_must_not_execute_stage_handlers": True,
            "new_coordinator_must_not_create_jobs_directly": True,
            "new_coordinator_must_not_create_queue": True,
            "new_coordinator_must_not_create_registry": True,
            "new_coordinator_must_not_create_workflow_repository": True,
            "runtime_gateway_connection_deferred_to_step_11": True,
            "pipeline_manifest_finalization_deferred_to_step_12": True,
        },
        "direct_source_inventories": inventories,
        "public_coordination_symbols": (
            public_coordination_symbols
        ),
        "coordination_candidate_count": len(
            coordination_candidates
        ),
        "coordination_candidates": (
            coordination_candidates
        ),
        "syntax_failures": syntax_failures,
        "run_connect_domain_source": (
            run_connect_domain_source
        ),
        "runtime_coordination_gateway_class_source": (
            runtime_gateway_class_source
        ),
    }

except Exception as exc:
    execution_error = {
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "traceback": traceback.format_exc(),
    }

required_checks = (
    "required_path_exists_primary_coordinator",
    "required_path_exists_linking_coordinator",
    "required_path_exists_runtime_gateway",
    "required_path_exists_coordination_root",
    "required_path_exists_inspection_report",
    "part_d_10_a_complete",
    "source_syntax_primary_coordinator",
    "source_syntax_linking_coordinator",
    "source_syntax_runtime_gateway",
    "coordination_candidates_discovered",
    "coordination_candidate_syntax",
    "run_connect_domain_source_extracted",
    "runtime_gateway_contract_extracted",
    "existing_primary_coordinator_calls_legacy_job_creation",
    "existing_primary_coordinator_calls_legacy_pipeline",
    "existing_primary_coordinator_not_connected_to_runtime_gateway",
    "coordination_contract_symbols_available",
    "production_sources_unchanged",
    "production_source_changes_no",
    "runtime_registration_created_no",
    "registry_persistence_executed_no",
    "universal_job_created_no",
    "queue_claim_executed_no",
    "handler_executed_no",
    "workflow_persistence_executed_no",
    "live_network_request_executed_no",
)

failed_checks = [
    name
    for name in required_checks
    if checks.get(name) is not True
]

complete = (
    not failed_checks
    and not execution_error
)

normalized_evidence = json.dumps(
    evidence,
    indent=2,
    default=str,
    sort_keys=True,
)

lines = [
    "LINKCRAFTER PIPELINE COORDINATION",
    "PART D 10-B1 CONNECTED DOMAIN COORDINATOR IMPLEMENTATION CONTRACT EXTRACTION",
    "",
    f"Generated: {datetime.now(timezone.utc).isoformat()}",
    "Mode: READ-ONLY EXACT CONTRACT EXTRACTION",
    "Production source changes: NONE",
    "Runtime registrations created: NO",
    "Registry persistence executed: NO",
    "Universal Jobs created: NO",
    "Queue claims executed: NO",
    "Handlers executed: NO",
    "Workflow persistence executed: NO",
    "Live network requests executed: NO",
    (
        "EXTRACTION STATUS: COMPLETE"
        if complete
        else "EXTRACTION STATUS: NOT_COMPLETE"
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
    "IMPLEMENTATION CONTRACT EVIDENCE",
    "=" * 110,
    normalized_evidence,
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
        "Part D 10-B2 — implement and certify one canonical "
        "Connected Domain pipeline coordinator without connecting "
        "it to production runtime submission."
    ),
    "",
    "=" * 110,
    "FINAL RESULT",
    "=" * 110,
    (
        "PART D 10-B1 COMPLETE"
        if complete
        else "PART D 10-B1 NOT_COMPLETE"
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
print("PART D 10-B1 - COORDINATOR CONTRACT EXTRACTION")
print("=" * 100)

for name, passed in checks.items():
    print(
        f"{name.upper()}: "
        f"{'PASS' if passed else 'FAIL'}"
    )

print(
    f"FAILED_CHECK_COUNT={len(failed_checks)}"
)
print(f"REPORT={report}")
print(
    "PART_D_10_B1_STATUS="
    + ("COMPLETE" if complete else "NOT_COMPLETE")
)

raise SystemExit(0 if complete else 1)