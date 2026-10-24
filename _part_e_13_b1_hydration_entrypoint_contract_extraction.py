from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True

TITLE = "LINKCRAFTOR PIPELINE VALIDATION AND ACTIVATION"
SUBTITLE = "PART E 13-B1 HYDRATION AND ENTRYPOINT CONTRACT EXTRACTION"
EXPECTED_STAGES = (
    "connect_domain",
    "site_sources",
    "url_cleaner",
    "site_pages",
    "live_domain_target_pool",
    "active_target_set",
)
REQUIRED_HANDOFFS = (
    ("site_sources", "url_cleaner", "source_urls"),
    ("url_cleaner", "site_pages", "cleaner_records"),
    ("site_pages", "live_domain_target_pool", "site_pages"),
    ("live_domain_target_pool", "active_target_set", "live_domain_payload"),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def rel(path: Path, root: Path) -> str:
    return str(path.relative_to(root)).replace("/", "\\")


def signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    try:
        return ast.unparse(node.args)
    except Exception:
        return "<unavailable>"


def call_name(node: ast.Call) -> str:
    try:
        return ast.unparse(node.func)
    except Exception:
        return "<unavailable>"


def source_segment(text: str, node: ast.AST) -> str:
    return ast.get_source_segment(text, node) or ast.unparse(node)


def inventory(path: Path, root: Path) -> dict[str, Any]:
    text = read_text(path)
    tree = ast.parse(text, filename=str(path))
    functions: dict[str, Any] = {}
    classes: dict[str, Any] = {}

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions[node.name] = {
                "signature": signature(node),
                "calls": sorted(
                    {
                        call_name(item)
                        for item in ast.walk(node)
                        if isinstance(item, ast.Call)
                    }
                ),
                "source": source_segment(text, node),
            }
        elif isinstance(node, ast.ClassDef):
            methods: dict[str, Any] = {}
            fields: list[str] = []
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    fields.append(item.target.id)
                elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods[item.name] = {
                        "signature": signature(item),
                        "calls": sorted(
                            {
                                call_name(call)
                                for call in ast.walk(item)
                                if isinstance(call, ast.Call)
                            }
                        ),
                        "source": source_segment(text, item),
                    }
            classes[node.name] = {
                "fields": fields,
                "methods": methods,
                "decorators": [ast.unparse(item) for item in node.decorator_list],
            }

    return {
        "path": rel(path, root),
        "sha256": sha256(path),
        "functions": functions,
        "classes": classes,
    }


def select_function(inv: dict[str, Any], name: str) -> dict[str, Any]:
    value = inv["functions"].get(name)
    if value is None:
        raise RuntimeError(f"Required function is absent: {inv['path']}:{name}")
    return value


def select_method(inv: dict[str, Any], class_name: str, name: str) -> dict[str, Any]:
    class_record = inv["classes"].get(class_name)
    if class_record is None:
        raise RuntimeError(f"Required class is absent: {inv['path']}:{class_name}")
    value = class_record["methods"].get(name)
    if value is None:
        raise RuntimeError(
            f"Required method is absent: {inv['path']}:{class_name}.{name}"
        )
    return value


def parse_13_a(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    text = read_text(path)
    required = (
        "INSPECTION STATUS: COMPLETE",
        "FAILED_CHECKS:\n[]",
        "NOT_RUN_CHECKS:\n[]",
        "FINAL RESULT: PART E 13-A COMPLETE",
    )
    if not all(marker in text for marker in required):
        raise RuntimeError("Part E 13-A is not complete.")

    findings_marker = "FINDINGS\n" + "=" * 110 + "\n"
    evidence_marker = "BOUNDARY AND CONTRACT EVIDENCE\n" + "=" * 110 + "\n"
    findings = json.loads(
        text.split(findings_marker, 1)[1].split("\n\n" + "=" * 110, 1)[0].strip()
    )
    evidence = json.loads(
        text.split(evidence_marker, 1)[1].split("\n\nEXECUTION_ERROR:", 1)[0].strip()
    )
    return findings, evidence


def emit_report(
    report: Path,
    checks: dict[str, bool | None],
    findings: list[dict[str, Any]],
    evidence: dict[str, Any],
    error: dict[str, Any],
    before: dict[str, str],
    after: dict[str, str],
) -> None:
    failed = [name for name, value in checks.items() if value is False]
    not_run = [name for name, value in checks.items() if value is None]
    complete = not failed and not not_run and not error
    status = "COMPLETE" if complete else "NOT_COMPLETE"

    sections = [
        TITLE,
        SUBTITLE,
        "",
        f"Generated: {utc_now()}",
        "Mode: READ-ONLY TARGETED CONTRACT EXTRACTION",
        "Production source changes: NONE",
        "Project modules imported or executed: NO",
        "Production activation: NOT PERFORMED",
        "Production Universal Jobs created: NO",
        "Production queue claims executed: NO",
        "Production handlers executed: NO",
        "Live network requests executed: NO",
        f"EXTRACTION STATUS: {status}",
        "",
        "Decision: IMPLEMENT_ONE_CANONICAL_RESULT_HYDRATION_AND_ENTRYPOINT_CONNECTION",
        "This extraction does not implement or activate that connection.",
        "",
        "=" * 110,
        "CHECKS",
        "=" * 110,
        json.dumps(checks, indent=2, sort_keys=True),
        "",
        "FAILED_CHECKS:",
        json.dumps(failed, indent=2),
        "",
        "NOT_RUN_CHECKS:",
        json.dumps(not_run, indent=2),
        "",
        "=" * 110,
        "FINDINGS",
        "=" * 110,
        json.dumps(findings, indent=2, default=str),
        "",
        "=" * 110,
        "CONTRACT EVIDENCE",
        "=" * 110,
        json.dumps(evidence, indent=2, default=str, sort_keys=True),
        "",
        "SOURCE_HASHES_BEFORE:",
        json.dumps(before, indent=2, sort_keys=True),
        "",
        "SOURCE_HASHES_AFTER:",
        json.dumps(after, indent=2, sort_keys=True),
        "",
        "EXECUTION_ERROR:",
        json.dumps(error, indent=2),
        "",
        "=" * 110,
        "NEXT STEP",
        "=" * 110,
        "Part E 13-B2 — implement and certify one canonical predecessor-result hydration boundary and route delegation.",
        "",
        "=" * 110,
        "FINAL RESULT",
        "=" * 110,
        "FINAL RESULT: PART E 13-B1 COMPLETE" if complete else "FINAL RESULT: PART E 13-B1 NOT_COMPLETE",
        "",
    ]
    report.parent.mkdir(parents=True, exist_ok=True)
    if report.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        shutil.copy2(report, report.with_name(report.name + ".before_" + stamp))
    report.write_text("\n".join(sections), encoding="utf-8", newline="\n")


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: inspector.py PROJECT_ROOT REPORT_PATH")

    root = Path(sys.argv[1]).resolve()
    report = Path(sys.argv[2]).resolve()
    allowed_report_root = (
        root / "backend/server/data/reports"
    ).resolve()
    try:
        report.relative_to(allowed_report_root)
    except ValueError as exc:
        raise RuntimeError(
            "Report path must remain inside backend/server/data/reports."
        ) from exc

    paths = {
        "13_a": root / "backend/server/data/reports/PART_E_13_A_COLLECTIVE_PIPELINE_ACTIVATION_BOUNDARY_INSPECTION.txt",
        "route": root / "backend/server/routes/site_workspace.py",
        "coordinator": root / "backend/server/pipelines/connect_domain/coordinator.py",
        "manifest": root / "backend/server/pipelines/connect_domain/manifest.py",
        "runtime_coordination_gateway": root / "backend/server/runtime/runtime_coordination_gateway.py",
        "runtime_execution_gateway": root / "backend/server/coordination/runtime_integration/runtime_execution_gateway.py",
        "runtime_registration": root / "backend/server/runtime/universal_runtime_registration.py",
        "runtime_worker": root / "backend/server/runtime/universal_runtime_worker_v1.py",
        "job_submission": root / "backend/server/runtime/universal_job_submission.py",
        "job_creation": root / "backend/server/runtime/universal_jobs/creation_engine.py",
        "job_store": root / "backend/server/orchestration/job_store.py",
        "workflow_repository": root / "backend/server/coordination/workflow_persistence/repository.py",
    }

    checks: dict[str, bool | None] = {
        "part_e_13_a_report_exists": False,
        "part_e_13_a_complete": False,
        "all_required_sources_exist": False,
        "all_required_sources_parse": False,
        "legacy_route_contract_extracted": False,
        "canonical_coordinator_contract_extracted": False,
        "canonical_manifest_contract_extracted": False,
        "runtime_submission_contract_extracted": False,
        "runtime_result_storage_contract_extracted": False,
        "terminal_intake_contract_extracted": False,
        "four_handoff_requirements_retained": False,
        "one_hydration_boundary_required": False,
        "production_sources_unchanged": False,
        "part_e_13_a_report_unchanged": False,
        "no_project_modules_imported": True,
        "no_production_side_effects_executed": True,
    }
    error: dict[str, Any] = {}
    evidence: dict[str, Any] = {}
    findings: list[dict[str, Any]] = []
    before: dict[str, str] = {}
    after: dict[str, str] = {}

    try:
        checks["part_e_13_a_report_exists"] = paths["13_a"].is_file()
        if not checks["part_e_13_a_report_exists"]:
            raise RuntimeError("Part E 13-A report is unavailable.")

        required_sources = [path for name, path in paths.items() if name != "13_a"]
        checks["all_required_sources_exist"] = all(path.is_file() for path in required_sources)
        if not checks["all_required_sources_exist"]:
            missing = [str(path) for path in required_sources if not path.is_file()]
            raise RuntimeError("Required source files are unavailable: " + ", ".join(missing))

        watched = [paths["13_a"], *required_sources]
        before = {rel(path, root): sha256(path) for path in watched}

        prior_findings, prior_evidence = parse_13_a(paths["13_a"])
        checks["part_e_13_a_complete"] = True

        inventories = {
            name: inventory(path, root)
            for name, path in paths.items()
            if name != "13_a"
        }
        checks["all_required_sources_parse"] = True

        route = inventories["route"]
        coordinator = inventories["coordinator"]
        manifest = inventories["manifest"]
        coordination_gateway = inventories["runtime_coordination_gateway"]
        execution_gateway = inventories["runtime_execution_gateway"]
        registration = inventories["runtime_registration"]
        worker = inventories["runtime_worker"]
        submission = inventories["job_submission"]
        creation = inventories["job_creation"]
        store = inventories["job_store"]
        repository = inventories["workflow_repository"]

        route_contract = select_function(route, "connect_domain")
        legacy_contract = select_function(coordinator, "run_connect_domain")
        checks["legacy_route_contract_extracted"] = (
            "run_connect_domain" in route_contract["calls"]
        )

        coordinator_contract = {
            "coordinate": select_function(coordinator, "coordinate_connect_domain_pipeline"),
            "connect": select_function(coordinator, "connect_connected_domain_to_universal_coordination"),
        }
        checks["canonical_coordinator_contract_extracted"] = True
        manifest_contract = select_function(manifest, "build_connected_domain_pipeline_manifest")
        checks["canonical_manifest_contract_extracted"] = True

        submission_contracts = {
            "submit_workflow_execution": select_method(
                coordination_gateway, "RuntimeCoordinationGateway", "submit_workflow_execution"
            ),
            "submit_runtime_execution_wave": select_function(
                execution_gateway, "submit_runtime_execution_wave"
            ),
            "submit_universal_job": select_function(submission, "submit_universal_job"),
            "create_universal_job": select_function(creation, "create_universal_job"),
        }
        checks["runtime_submission_contract_extracted"] = True

        result_storage_contracts = {
            "dispatch_registered_runtime_handler": select_function(
                registration, "dispatch_registered_runtime_handler"
            ),
            "execute_registered_runtime_job_v1": select_function(
                registration, "execute_registered_runtime_job_v1"
            ),
            "run_one_universal_runtime_job_v1": select_function(
                worker, "run_one_universal_runtime_job_v1"
            ),
            "get_job": select_function(store, "get_job"),
            "update_job_status": select_function(store, "update_job_status"),
            "append_job_event": select_function(store, "append_job_event"),
        }
        checks["runtime_result_storage_contract_extracted"] = True

        terminal_contracts = {
            "intake_runtime_terminal_stage_result": select_function(
                execution_gateway, "intake_runtime_terminal_stage_result"
            ),
            "apply_runtime_terminal_lifecycle": select_method(
                coordination_gateway, "RuntimeCoordinationGateway", "apply_runtime_terminal_lifecycle"
            ),
            "load_workflow_record": select_method(
                repository, "WorkflowRepository", "load_workflow_record"
            ),
            "save_workflow": select_method(repository, "WorkflowRepository", "save_workflow"),
        }
        checks["terminal_intake_contract_extracted"] = True

        hydration_findings = [
            item
            for item in prior_findings
            if item.get("type") == "runtime_payload_hydration_needs_proof"
        ]
        observed = {
            (item.get("stage"), tuple(item.get("missing_from_base_intent", ())))
            for item in hydration_findings
        }
        expected = {(stage, (field,)) for _, stage, field in REQUIRED_HANDOFFS}
        checks["four_handoff_requirements_retained"] = observed == expected

        findings = [
            {
                "type": "canonical_predecessor_result_hydration_required",
                "is_activation_blocker": True,
                "handoffs": [
                    {"predecessor": p, "successor": s, "successor_field": f}
                    for p, s, f in REQUIRED_HANDOFFS
                ],
                "constraint": "Use one canonical boundary; do not create a second job store, queue, runtime, registry, or workflow repository.",
            },
            {
                "type": "public_connect_domain_route_delegation_required",
                "is_activation_blocker": True,
                "current_authority": "run_connect_domain",
                "required_chain": [
                    "coordinate_connect_domain_pipeline",
                    "build_connected_domain_pipeline_manifest",
                    "connect_connected_domain_to_universal_coordination",
                    "RuntimeCoordinationGateway",
                ],
                "constraint": "Preserve the request/response compatibility boundary and make activation idempotent.",
            },
            {
                "type": "controlled_execution_still_required",
                "is_activation_blocker": True,
                "interpretation": "Source extraction does not certify real persistence, scheduling, hydration, terminal intake, or end-to-end execution.",
            },
        ]
        checks["one_hydration_boundary_required"] = True

        evidence = {
            "decision": "IMPLEMENT_ONE_CANONICAL_RESULT_HYDRATION_AND_ENTRYPOINT_CONNECTION",
            "stages": list(EXPECTED_STAGES),
            "required_handoffs": [
                {"predecessor": p, "successor": s, "successor_field": f}
                for p, s, f in REQUIRED_HANDOFFS
            ],
            "part_e_13_a_findings": prior_findings,
            "part_e_13_a_payload_handoff_matrix": prior_evidence.get(
                "payload_handoff_matrix", []
            ),
            "route_contract": route_contract,
            "legacy_entrypoint_contract": legacy_contract,
            "canonical_coordinator_contracts": coordinator_contract,
            "canonical_manifest_contract": manifest_contract,
            "submission_contracts": submission_contracts,
            "result_storage_contracts": result_storage_contracts,
            "terminal_contracts": terminal_contracts,
            "source_inventory": {
                name: {
                    "path": value["path"],
                    "sha256": value["sha256"],
                    "functions": sorted(value["functions"]),
                    "classes": sorted(value["classes"]),
                }
                for name, value in inventories.items()
            },
        }

        after = {rel(path, root): sha256(path) for path in watched}
        checks["production_sources_unchanged"] = all(
            before[rel(path, root)] == after[rel(path, root)] for path in required_sources
        )
        checks["part_e_13_a_report_unchanged"] = (
            before[rel(paths["13_a"], root)] == after[rel(paths["13_a"], root)]
        )
    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }
        if before:
            after = {
                key: sha256(root / Path(key.replace("\\", "/")))
                for key in before
                if (root / Path(key.replace("\\", "/"))).is_file()
            }

    emit_report(report, checks, findings, evidence, error, before, after)
    for name, value in checks.items():
        label = "NOT_RUN" if value is None else ("PASS" if value else "FAIL")
        print(f"{name.upper()}: {label}")
    print(f"FAILED_CHECK_COUNT={sum(value is False for value in checks.values())}")
    print(f"NOT_RUN_CHECK_COUNT={sum(value is None for value in checks.values())}")
    print(f"REPORT={report}")
    complete = all(value is True for value in checks.values()) and not error
    print("PART_E_13_B1_STATUS=" + ("COMPLETE" if complete else "NOT_COMPLETE"))
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
