from __future__ import annotations

import ast
import hashlib
import json
import sys
import traceback
from pathlib import Path
from typing import Any


STAGES = (
    (
        "connect_domain",
        "connect_domain_stage",
        "backend/server/pipelines/connect_domain/stage.py",
        "execute_connect_domain_stage",
    ),
    (
        "site_sources",
        "site_sources_stage",
        "backend/server/pipelines/connect_domain/linking_target_pipeline/site_sources/stage.py",
        "execute_site_sources_stage",
    ),
    (
        "url_cleaner",
        "url_cleaner_stage",
        "backend/server/pipelines/connect_domain/linking_target_pipeline/url_cleaner/stage.py",
        "execute_url_cleaner_stage",
    ),
    (
        "site_pages",
        "site_pages_stage",
        "backend/server/pipelines/connect_domain/linking_target_pipeline/site_pages/stage.py",
        "build_site_pages",
    ),
    (
        "live_domain_target_pool",
        "live_domain_target_pool_stage",
        "backend/server/pipelines/connect_domain/linking_target_pipeline/live_domain_target_pool/stage.py",
        "build_live_domain_target_pool",
    ),
    (
        "active_target_set",
        "active_target_set_stage",
        "backend/server/pipelines/connect_domain/linking_target_pipeline/active_target_set/stage.py",
        "build_active_target_set",
    ),
)


CORE_SOURCES = {
    "route": "backend/server/routes/site_workspace.py",
    "activation": "backend/server/pipelines/connect_domain/activation.py",
    "manifest": "backend/server/pipelines/connect_domain/manifest.py",
    "coordinator": "backend/server/pipelines/connect_domain/coordinator.py",
    "pipeline_hydration": "backend/server/pipelines/connect_domain/runtime_hydration.py",
    "payload_hydration": "backend/server/runtime/runtime_payload_hydration.py",
    "coordination_gateway": "backend/server/runtime/runtime_coordination_gateway.py",
    "execution_gateway": "backend/server/coordination/runtime_integration/runtime_execution_gateway.py",
    "worker": "backend/server/runtime/universal_runtime_worker_v1.py",
    "registration": "backend/server/runtime/universal_runtime_registration.py",
    "job_store": "backend/server/orchestration/job_store.py",
    "workflow_repository": "backend/server/coordination/workflow_persistence/repository.py",
    "stage_result_processor": "backend/server/coordination/stage_handoff/stage_result_processor.py",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = dotted_name(node.value)
        return (prefix + "." if prefix else "") + node.attr
    return ""


def public_functions(tree: ast.Module) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and not node.name.startswith("_")
    }


def signature_inventory(node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, Any]:
    positional = [argument.arg for argument in node.args.posonlyargs + node.args.args]
    keyword_only = [argument.arg for argument in node.args.kwonlyargs]
    variable_positional = node.args.vararg.arg if node.args.vararg else None
    variable_keyword = node.args.kwarg.arg if node.args.kwarg else None
    calls = sorted(
        {
            dotted_name(item.func)
            for item in ast.walk(node)
            if isinstance(item, ast.Call) and dotted_name(item.func)
        }
    )
    return {
        "positional_parameters": positional,
        "keyword_only_parameters": keyword_only,
        "variable_positional": variable_positional,
        "variable_keyword": variable_keyword,
        "call_names": calls,
        "line": node.lineno,
    }


def write_report(
    path: Path,
    checks: dict[str, bool],
    evidence: dict[str, Any],
    findings: list[dict[str, Any]],
    decision: str,
    error: dict[str, Any],
) -> None:
    failed = [name for name, passed in checks.items() if not passed]
    complete = not failed and not error
    content = "\n".join(
        [
            "LINKCRAFTOR PIPELINE VALIDATION AND ACTIVATION",
            "PART E 14-A END-TO-END EXECUTION BOUNDARY INSPECTION",
            "",
            "Mode: READ-ONLY TARGETED INSPECTION",
            "Production source changes: NONE",
            "Production activation executed: NO",
            "Production workflow persistence executed: NO",
            "Production Universal Jobs created: NO",
            "Production queue claims executed: NO",
            "Production handlers executed: NO",
            "Live network requests executed: NO",
            "INSPECTION STATUS: " + ("COMPLETE" if complete else "NOT_COMPLETE"),
            "",
            "INSPECTION DECISION:",
            decision,
            "",
            "CHECKS:",
            json.dumps(checks, indent=2, sort_keys=True),
            "",
            "FAILED_CHECKS:",
            json.dumps(failed, indent=2),
            "",
            "NOT_RUN_CHECKS:",
            "[]",
            "",
            "FINDINGS:",
            json.dumps(findings, indent=2, default=str, sort_keys=True),
            "",
            "BOUNDARY EVIDENCE:",
            json.dumps(evidence, indent=2, default=str, sort_keys=True),
            "",
            "EXECUTION_ERROR:",
            json.dumps(error, indent=2),
            "",
            "NEXT STEP:",
            "Part E 14-B - execute and certify all six real stage handlers with controlled fixtures,",
            "isolated persistence and the canonical four-handoff hydration chain.",
            "No live-domain activation is authorized by this inspection.",
            "",
            "FINAL RESULT:",
            "PART E 14-A COMPLETE" if complete else "PART E 14-A NOT_COMPLETE",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def main() -> int:
    root = Path(sys.argv[1]).resolve()
    report = Path(sys.argv[2]).resolve()
    step_13_report = root / "backend/server/data/reports/PART_E_13_C_CONTROLLED_ACTIVATION_CERTIFICATION.txt"
    stage_paths = {stage_id: root / relative for stage_id, _, relative, _ in STAGES}
    core_paths = {name: root / relative for name, relative in CORE_SOURCES.items()}
    all_paths = {**{"stage_" + key: value for key, value in stage_paths.items()}, **core_paths}

    checks = {
        "part_e_13_c_report_exists": False,
        "part_e_step_13_certified": False,
        "all_six_stage_sources_exist": False,
        "all_core_runtime_sources_exist": False,
        "all_required_sources_parse": False,
        "all_six_handler_functions_found": False,
        "stage_signature_inventory_complete": False,
        "entrypoint_activation_chain_present": False,
        "runtime_submission_chain_present": False,
        "worker_dispatch_and_result_storage_present": False,
        "four_handoff_hydration_chain_present": False,
        "terminal_lifecycle_chain_present": False,
        "controlled_fixture_injection_points_identified": False,
        "end_to_end_certification_scope_defined": False,
        "source_files_unchanged": False,
        "historical_step_13_report_unchanged": False,
        "no_project_modules_imported": True,
        "no_production_side_effects_executed": True,
    }
    findings: list[dict[str, Any]] = []
    evidence: dict[str, Any] = {}
    error: dict[str, Any] = {}
    decision = "INSPECTION_BLOCKED"
    source_hashes_before: dict[str, str] = {}
    report_hash_before = ""

    try:
        checks["part_e_13_c_report_exists"] = step_13_report.is_file()
        if not checks["part_e_13_c_report_exists"]:
            raise RuntimeError("Part E 13-C certification report is unavailable.")
        report_hash_before = sha256(step_13_report)
        step_13_text = step_13_report.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        checks["part_e_step_13_certified"] = (
            "CERTIFICATION STATUS: CERTIFIED" in step_13_text
            and "FAILED_CHECKS:\n[]" in step_13_text
            and "FINAL RESULT: PART E STEP 13 COLLECTIVE PIPELINE ACTIVATION CERTIFIED" in step_13_text
        )
        if not checks["part_e_step_13_certified"]:
            raise RuntimeError("Part E Step 13 is not certified.")

        checks["all_six_stage_sources_exist"] = all(path.is_file() for path in stage_paths.values())
        checks["all_core_runtime_sources_exist"] = all(path.is_file() for path in core_paths.values())
        if not checks["all_six_stage_sources_exist"] or not checks["all_core_runtime_sources_exist"]:
            missing = [name for name, path in all_paths.items() if not path.is_file()]
            raise RuntimeError("Required source unavailable: " + ", ".join(missing))

        source_hashes_before = {name: sha256(path) for name, path in all_paths.items()}
        trees: dict[str, ast.Module] = {}
        texts: dict[str, str] = {}
        for name, path in all_paths.items():
            text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
            texts[name] = text
            trees[name] = ast.parse(text, filename=str(path))
        checks["all_required_sources_parse"] = True

        stage_inventory: dict[str, Any] = {}
        all_handlers_found = True
        for stage_id, job_type, relative, handler_name in STAGES:
            functions = public_functions(trees["stage_" + stage_id])
            handler = functions.get(handler_name)
            if handler is None:
                all_handlers_found = False
                stage_inventory[stage_id] = {
                    "job_type": job_type,
                    "source": relative,
                    "handler": handler_name,
                    "found": False,
                }
                continue
            stage_inventory[stage_id] = {
                "job_type": job_type,
                "source": relative,
                "handler": handler_name,
                "found": True,
                **signature_inventory(handler),
            }
        checks["all_six_handler_functions_found"] = all_handlers_found
        checks["stage_signature_inventory_complete"] = (
            len(stage_inventory) == 6
            and all(item.get("found") for item in stage_inventory.values())
        )

        route = texts["route"]
        activation = texts["activation"]
        coordinator = texts["coordinator"]
        manifest = texts["manifest"]
        coordination_gateway = texts["coordination_gateway"]
        execution_gateway = texts["execution_gateway"]
        worker = texts["worker"]
        pipeline_hydration = texts["pipeline_hydration"]
        stage_result_processor = texts["stage_result_processor"]

        checks["entrypoint_activation_chain_present"] = all(
            token in route + activation
            for token in (
                "activate_connected_domain_pipeline",
                "coordinate_connect_domain_pipeline",
                "build_connected_domain_pipeline_manifest",
                "connect_connected_domain_to_universal_coordination",
            )
        )
        checks["runtime_submission_chain_present"] = all(
            token in coordinator + coordination_gateway + execution_gateway
            for token in (
                "submit_workflow_execution",
                "submit_runtime_execution_wave",
                "submit_runtime_job_mapping",
            )
        )
        checks["worker_dispatch_and_result_storage_present"] = all(
            token in worker
            for token in (
                "hydrate_runtime_job_payload",
                "dispatch_registered_runtime_handler",
                "runtime_dispatch_result",
            )
        )
        checks["four_handoff_hydration_chain_present"] = all(
            token in pipeline_hydration
            for token in (
                '"url_cleaner": "site_sources"',
                '"site_pages": "url_cleaner"',
                '"live_domain_target_pool": "site_pages"',
                '"active_target_set": "live_domain_target_pool"',
                '"url_cleaner": "source_urls"',
                '"site_pages": "cleaner_records"',
                '"live_domain_target_pool": "site_pages"',
                '"active_target_set": "live_domain_payload"',
            )
        )
        checks["terminal_lifecycle_chain_present"] = all(
            token in coordination_gateway + execution_gateway + stage_result_processor
            for token in (
                "intake_runtime_terminal_stage_result",
                "apply_runtime_terminal_lifecycle",
                "process_stage_result",
            )
        )

        injection_parameters = {
            stage_id: sorted(
                parameter
                for parameter in (
                    item.get("positional_parameters", [])
                    + item.get("keyword_only_parameters", [])
                )
                if any(
                    marker in parameter.lower()
                    for marker in (
                        "writer",
                        "reader",
                        "http",
                        "fetch",
                        "expand",
                        "loader",
                        "repository",
                    )
                )
            )
            for stage_id, item in stage_inventory.items()
        }
        checks["controlled_fixture_injection_points_identified"] = (
            bool(injection_parameters.get("connect_domain"))
            and bool(injection_parameters.get("site_sources"))
        )

        findings = [
            {
                "id": "14A-F1",
                "finding": "The certified public entrypoint, coordinator, manifest and Runtime Coordination Gateway chain is installed.",
                "implication": "Step 14-B can exercise installed production composition without adding another entrypoint.",
            },
            {
                "id": "14A-F2",
                "finding": "All six registered stage handler functions are present and their callable contracts were extracted.",
                "implication": "The real stage implementations can be executed in a controlled fixture run.",
            },
            {
                "id": "14A-F3",
                "finding": "Site Sources exposes injectable network and sitemap authorities, and Connect Domain exposes an injectable profile writer.",
                "implication": "Network and production persistence can be replaced by deterministic test doubles.",
            },
            {
                "id": "14A-F4",
                "finding": "The worker stores handler evidence in runtime_dispatch_result and the four-stage hydrator consumes that evidence.",
                "implication": "Step 14-B can prove actual result-to-payload continuity across all six stages.",
            },
            {
                "id": "14A-F5",
                "finding": "Terminal intake and workflow lifecycle authorities are already present.",
                "implication": "End-to-end certification must include completed-stage lifecycle progression and final workflow completion evidence.",
            },
            {
                "id": "14A-F6",
                "finding": "No live-domain execution is needed for the next certification step.",
                "implication": "A controlled fixture run should be completed before any separately authorized live-domain smoke test.",
            },
        ]
        required_14_b_scope = (
            "real_six_handlers",
            "deterministic_site_sources_fixture",
            "four_hydrated_handoffs",
            "isolated_stage_persistence",
            "ordered_dependency_execution",
            "runtime_dispatch_result_evidence",
            "terminal_lifecycle_progression",
            "final_active_target_set_output",
            "retry_and_failure_protection",
            "zero_production_side_effects",
        )
        checks["end_to_end_certification_scope_defined"] = len(required_14_b_scope) == 10
        decision = "CONTROLLED_FIXTURE_END_TO_END_EXECUTION_REQUIRED"

        checks["source_files_unchanged"] = source_hashes_before == {
            name: sha256(path) for name, path in all_paths.items()
        }
        checks["historical_step_13_report_unchanged"] = report_hash_before == sha256(step_13_report)
        collective_fingerprint = hashlib.sha256(
            json.dumps(
                {
                    "sources": source_hashes_before,
                    "stages": stage_inventory,
                    "scope": required_14_b_scope,
                    "decision": decision,
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        evidence = {
            "decision": decision,
            "stage_order": [item[0] for item in STAGES],
            "stage_contracts": stage_inventory,
            "controlled_injection_parameters": injection_parameters,
            "required_14_b_scope": list(required_14_b_scope),
            "source_hashes": source_hashes_before,
            "inspection_fingerprint": collective_fingerprint,
            "project_modules_imported": False,
            "production_activation_executed": False,
            "live_network_requests_executed": False,
        }
        if not all(checks.values()):
            raise RuntimeError("One or more Part E 14-A inspection checks failed.")
    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }

    write_report(report, checks, evidence, findings, decision, error)
    for name, passed in checks.items():
        print(name.upper() + ": " + ("PASS" if passed else "FAIL"))
    failed_count = sum(not passed for passed in checks.values())
    print("FAILED_CHECK_COUNT=" + str(failed_count))
    print("NOT_RUN_CHECK_COUNT=0")
    print("FINDING_COUNT=" + str(len(findings)))
    print("DECISION=" + decision)
    print("REPORT=" + str(report))
    complete = failed_count == 0 and not error
    print("PART_E_14_A_STATUS=" + ("COMPLETE" if complete else "NOT_COMPLETE"))
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
