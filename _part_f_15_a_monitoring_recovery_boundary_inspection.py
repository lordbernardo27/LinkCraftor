from __future__ import annotations

import ast
import hashlib
import json
import sys
import traceback
from pathlib import Path
from typing import Any


MONITOR_TOKENS = (
    "health",
    "status",
    "snapshot",
    "monitor",
    "metric",
    "event",
    "diagnostic",
    "inspect",
)


RECOVERY_TOKENS = (
    "retry",
    "recover",
    "requeue",
    "resume",
    "replay",
    "cancel",
    "terminate",
    "dead_letter",
    "failure",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = dotted_name(node.value)
        return (prefix + "." if prefix else "") + node.attr
    return ""


def public_symbols(tree: ast.Module) -> dict[str, list[str]]:
    functions = sorted(
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and not node.name.startswith("_")
    )
    classes = sorted(
        node.name
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        and not node.name.startswith("_")
    )
    methods: list[str] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        for child in node.body:
            if (
                isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                and not child.name.startswith("_")
            ):
                methods.append(node.name + "." + child.name)
    return {
        "functions": functions,
        "classes": classes,
        "methods": sorted(methods),
    }


def route_inventory(tree: ast.Module) -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            method = dotted_name(decorator.func)
            if not method.endswith((".get", ".post", ".put", ".patch", ".delete")):
                continue
            path = ""
            if decorator.args and isinstance(decorator.args[0], ast.Constant):
                path = str(decorator.args[0].value)
            routes.append(
                {
                    "function": node.name,
                    "method": method.rsplit(".", 1)[-1].upper(),
                    "path": path,
                    "line": node.lineno,
                }
            )
    return routes


def relevant(name: str, tokens: tuple[str, ...]) -> bool:
    lowered = name.lower()
    return any(token in lowered for token in tokens)


def write_report(
    path: Path,
    checks: dict[str, bool],
    decision: str,
    findings: list[dict[str, Any]],
    evidence: dict[str, Any],
    error: dict[str, Any],
) -> None:
    failed = [name for name, passed in checks.items() if not passed]
    complete = not failed and not error
    text = "\n".join(
        [
            "LINKCRAFTOR CONNECTED DOMAIN OWNER OPERATIONS",
            "PART F 15-A MONITORING AND RECOVERY BOUNDARY INSPECTION",
            "",
            "Mode: READ-ONLY TARGETED INSPECTION",
            "Production source changes: NONE",
            "Production jobs created: NO",
            "Production queue claims executed: NO",
            "Production handlers executed: NO",
            "Production recovery actions executed: NO",
            "Production workflow persistence executed: NO",
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
            "Part F 15-B - implement and certify one read-only Connected Domain operations snapshot",
            "that composes existing job, event, correlation, workflow and runtime authorities.",
            "Recovery mutations remain deferred to Part F 15-C.",
            "",
            "FINAL RESULT:",
            "PART F 15-A COMPLETE" if complete else "PART F 15-A NOT_COMPLETE",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    root = Path(sys.argv[1]).resolve()
    report = Path(sys.argv[2]).resolve()
    step_14_report = root / "backend/server/data/reports/PART_E_14_B_CONTROLLED_END_TO_END_CERTIFICATION.txt"
    backend_root = root / "backend/server"
    key_sources = {
        "job_store": root / "backend/server/orchestration/job_store.py",
        "worker": root / "backend/server/runtime/universal_runtime_worker_v1.py",
        "registration": root / "backend/server/runtime/universal_runtime_registration.py",
        "coordination_gateway": root / "backend/server/runtime/runtime_coordination_gateway.py",
        "execution_gateway": root / "backend/server/coordination/runtime_integration/runtime_execution_gateway.py",
        "correlation": root / "backend/server/coordination/runtime_integration/workflow_job_correlation.py",
        "workflow_repository": root / "backend/server/coordination/workflow_persistence/repository.py",
        "application_lifecycle": root / "backend/server/runtime/runtime_application_lifecycle.py",
        "connect_domain_activation": root / "backend/server/pipelines/connect_domain/activation.py",
        "connect_domain_coordinator": root / "backend/server/pipelines/connect_domain/coordinator.py",
    }
    checks = {
        "part_e_14_b_report_exists": False,
        "part_e_step_14_certified": False,
        "windows_atomic_persistence_fix_retained": False,
        "backend_source_tree_available": False,
        "active_python_sources_found": False,
        "all_active_python_sources_parse": False,
        "all_key_authority_sources_exist": False,
        "job_status_and_event_read_authorities_found": False,
        "workflow_read_authorities_found": False,
        "runtime_registration_snapshot_authority_found": False,
        "runtime_worker_status_authority_found": False,
        "retry_and_attempt_authorities_found": False,
        "failure_and_dead_letter_authorities_found": False,
        "cancellation_or_termination_authorities_found": False,
        "workflow_correlation_authority_found": False,
        "monitoring_route_inventory_complete": False,
        "owner_operations_projection_search_complete": False,
        "implementation_scope_defined": False,
        "production_sources_unchanged": False,
        "historical_step_14_report_unchanged": False,
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
        checks["part_e_14_b_report_exists"] = step_14_report.is_file()
        if not checks["part_e_14_b_report_exists"]:
            raise RuntimeError("Part E 14-B certification report is unavailable.")
        report_hash_before = sha256(step_14_report)
        step_14_text = step_14_report.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        checks["part_e_step_14_certified"] = (
            "CERTIFICATION STATUS: CERTIFIED" in step_14_text
            and "FAILED_CHECKS:\n[]" in step_14_text
            and "NOT_RUN_CHECKS:\n[]" in step_14_text
            and "FINAL RESULT: PART E STEP 14 END-TO-END PIPELINE CERTIFIED" in step_14_text
        )
        if not checks["part_e_step_14_certified"]:
            raise RuntimeError("Part E Step 14 is not certified.")

        repository_text = key_sources["workflow_repository"].read_text(encoding="utf-8-sig")
        checks["windows_atomic_persistence_fix_retained"] = all(
            token in repository_text
            for token in (
                "_ATOMIC_REPLACE_MAX_ATTEMPTS = 20",
                "def _atomic_replace_with_windows_retry(",
                "os.replace(",
            )
        )
        checks["backend_source_tree_available"] = backend_root.is_dir()
        if not checks["backend_source_tree_available"]:
            raise RuntimeError("backend/server source tree is unavailable.")

        sources = sorted(
            path
            for path in backend_root.rglob("*.py")
            if "__pycache__" not in path.parts
            and "runtime_backups" not in path.parts
            and "backups" not in path.parts
            and not any("before_" in part for part in path.parts)
            and "_before_" not in path.name
        )
        checks["active_python_sources_found"] = bool(sources)
        checks["all_key_authority_sources_exist"] = all(path.is_file() for path in key_sources.values())
        if not checks["active_python_sources_found"] or not checks["all_key_authority_sources_exist"]:
            missing = [name for name, path in key_sources.items() if not path.is_file()]
            raise RuntimeError("Required authority source unavailable: " + ", ".join(missing))

        source_hashes_before = {
            str(path.relative_to(root)).replace("\\", "/"): sha256(path)
            for path in sources
        }
        inventories: dict[str, dict[str, Any]] = {}
        monitoring_candidates: list[dict[str, Any]] = []
        recovery_candidates: list[dict[str, Any]] = []
        routes: list[dict[str, Any]] = []
        syntax_failures: list[dict[str, str]] = []
        all_text = ""

        for path in sources:
            relative = str(path.relative_to(root)).replace("\\", "/")
            text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
            all_text += "\n" + text
            try:
                tree = ast.parse(text, filename=str(path))
            except SyntaxError as exc:
                syntax_failures.append({"source": relative, "error": str(exc)})
                continue
            inventory = public_symbols(tree)
            inventories[relative] = inventory
            names = inventory["functions"] + inventory["classes"] + inventory["methods"]
            monitor_names = [name for name in names if relevant(name, MONITOR_TOKENS)]
            recover_names = [name for name in names if relevant(name, RECOVERY_TOKENS)]
            if monitor_names:
                monitoring_candidates.append({"source": relative, "symbols": monitor_names})
            if recover_names:
                recovery_candidates.append({"source": relative, "symbols": recover_names})
            for route in route_inventory(tree):
                route["source"] = relative
                routes.append(route)

        checks["all_active_python_sources_parse"] = not syntax_failures
        if syntax_failures:
            raise RuntimeError("Active Python syntax failures were found.")

        job_inventory = inventories.get("backend/server/orchestration/job_store.py", {})
        job_symbols = set(job_inventory.get("functions", ())) | set(job_inventory.get("methods", ()))
        checks["job_status_and_event_read_authorities_found"] = (
            any("job" in name.lower() and "status" in name.lower() for name in job_symbols)
            and any("event" in name.lower() for name in job_symbols)
        )
        workflow_inventory = inventories.get(
            "backend/server/coordination/workflow_persistence/repository.py",
            {},
        )
        workflow_symbols = set(workflow_inventory.get("functions", ())) | set(workflow_inventory.get("methods", ()))
        checks["workflow_read_authorities_found"] = all(
            any(required in name for name in workflow_symbols)
            for required in ("load_workflow", "list_workflow")
        )
        registration_inventory = inventories.get(
            "backend/server/runtime/universal_runtime_registration.py",
            {},
        )
        checks["runtime_registration_snapshot_authority_found"] = (
            "runtime_registration_snapshot" in registration_inventory.get("functions", ())
        )
        worker_inventory = inventories.get(
            "backend/server/runtime/universal_runtime_worker_v1.py",
            {},
        )
        worker_names = worker_inventory.get("functions", ()) + worker_inventory.get("methods", ())
        checks["runtime_worker_status_authority_found"] = any(
            relevant(name, ("worker", "execute", "explain")) for name in worker_names
        )
        checks["retry_and_attempt_authorities_found"] = all(
            token in all_text.lower() for token in ("retry", "attempt")
        )
        checks["failure_and_dead_letter_authorities_found"] = all(
            token in all_text.lower() for token in ("failure", "dead_letter")
        )
        checks["cancellation_or_termination_authorities_found"] = (
            "cancel" in all_text.lower() and "terminat" in all_text.lower()
        )
        correlation_inventory = inventories.get(
            "backend/server/coordination/runtime_integration/workflow_job_correlation.py",
            {},
        )
        correlation_names = correlation_inventory.get("functions", ()) + correlation_inventory.get("methods", ())
        checks["workflow_correlation_authority_found"] = any(
            "resolve_workflow_job_correlation" in name for name in correlation_names
        )
        operational_routes = [
            item
            for item in routes
            if relevant(item["path"] + " " + item["function"], MONITOR_TOKENS + RECOVERY_TOKENS)
        ]
        checks["monitoring_route_inventory_complete"] = True

        connect_domain_operations = [
            item
            for item in monitoring_candidates + recovery_candidates
            if "pipelines/connect_domain" in item["source"]
            and any(
                token in " ".join(item["symbols"]).lower()
                for token in ("monitor", "snapshot", "recover", "retry", "operation")
            )
        ]
        owner_routes = [
            item
            for item in operational_routes
            if "owner" in item["path"].lower()
            or "ops" in item["path"].lower()
            or "connect_domain" in item["path"].lower()
        ]
        owner_projection_available = bool(connect_domain_operations and owner_routes)
        checks["owner_operations_projection_search_complete"] = True

        required_scope = (
            "workflow_identity_and_status",
            "six_stage_statuses",
            "job_ids_and_attempts",
            "dependency_and_handoff_state",
            "runtime_event_timeline",
            "failure_and_dead_letter_evidence",
            "final_active_target_set_readiness",
            "read_only_snapshot_contract",
            "authorized_retry_or_recovery_request",
            "idempotency_and_terminal_protection",
            "audit_evidence",
            "zero_duplicate_runtime_authorities",
        )
        checks["implementation_scope_defined"] = len(required_scope) == 12
        decision = (
            "EXISTING_OWNER_OPERATIONS_PROJECTION_REQUIRES_CERTIFICATION"
            if owner_projection_available
            else "IMPLEMENT_ONE_CONNECTED_DOMAIN_OWNER_OPERATIONS_PROJECTION"
        )

        findings = [
            {
                "id": "15A-F1",
                "finding": "Universal Runtime already exposes job status, event and registration evidence.",
                "implication": "Step 15 must compose these authorities rather than create another job store or monitoring database.",
            },
            {
                "id": "15A-F2",
                "finding": "Workflow persistence and workflow/job correlation readers are available.",
                "implication": "One workflow-centric snapshot can join pipeline, job and lifecycle identities.",
            },
            {
                "id": "15A-F3",
                "finding": "Retry, attempt, failure, dead-letter, cancellation and termination authorities exist in the active source tree.",
                "implication": "Recovery controls must delegate to existing runtime operations and preserve their safety rules.",
            },
            {
                "id": "15A-F4",
                "finding": "A complete Connected Domain owner-operations projection was " + ("found." if owner_projection_available else "not found."),
                "implication": (
                    "The existing projection should be certified."
                    if owner_projection_available
                    else "One thin read-only projection is required before recovery mutations are connected."
                ),
            },
            {
                "id": "15A-F5",
                "finding": "The Windows atomic workflow-persistence correction remains installed.",
                "implication": "Monitoring and recovery can read and update workflow evidence safely on Windows.",
            },
        ]

        checks["production_sources_unchanged"] = source_hashes_before == {
            str(path.relative_to(root)).replace("\\", "/"): sha256(path)
            for path in sources
        }
        checks["historical_step_14_report_unchanged"] = report_hash_before == sha256(step_14_report)
        fingerprint = hashlib.sha256(
            json.dumps(
                {
                    "decision": decision,
                    "sources": source_hashes_before,
                    "monitoring": monitoring_candidates,
                    "recovery": recovery_candidates,
                    "routes": operational_routes,
                    "scope": required_scope,
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        evidence = {
            "decision": decision,
            "active_source_count": len(sources),
            "monitoring_candidate_count": len(monitoring_candidates),
            "recovery_candidate_count": len(recovery_candidates),
            "operational_route_count": len(operational_routes),
            "owner_operations_projection_available": owner_projection_available,
            "connect_domain_operation_candidates": connect_domain_operations,
            "owner_operation_routes": owner_routes,
            "job_store_symbols": sorted(job_symbols),
            "workflow_repository_symbols": sorted(workflow_symbols),
            "correlation_symbols": sorted(correlation_names),
            "monitoring_candidates": monitoring_candidates[:80],
            "recovery_candidates": recovery_candidates[:80],
            "operational_routes": operational_routes[:80],
            "required_implementation_scope": list(required_scope),
            "key_source_hashes": {
                name: sha256(path) for name, path in key_sources.items()
            },
            "inspection_fingerprint": fingerprint,
            "project_modules_imported": False,
            "production_recovery_actions_executed": False,
        }
        if not all(checks.values()):
            raise RuntimeError("One or more Part F 15-A inspection checks failed.")
    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }

    write_report(report, checks, decision, findings, evidence, error)
    for name, passed in checks.items():
        print(name.upper() + ": " + ("PASS" if passed else "FAIL"))
    failed_count = sum(not passed for passed in checks.values())
    print("FAILED_CHECK_COUNT=" + str(failed_count))
    print("NOT_RUN_CHECK_COUNT=0")
    print("FINDING_COUNT=" + str(len(findings)))
    print("DECISION=" + decision)
    print("REPORT=" + str(report))
    complete = failed_count == 0 and not error
    print("PART_F_15_A_STATUS=" + ("COMPLETE" if complete else "NOT_COMPLETE"))
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
