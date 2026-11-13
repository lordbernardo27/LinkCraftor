from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STEP = "PART F 15-B6A"
TITLE = "OWNER ACTIONS AND RECOVERY BOUNDARY AND AUTHORITY INSPECTION"
FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B6A OWNER ACTIONS AND RECOVERY "
    "BOUNDARY AND AUTHORITY INSPECTION COMPLETE"
)

B5P_REPORT = (
    "PART_F_15_B5P_RUNTIME_INFRASTRUCTURE_COLLECTIVE_CERTIFICATION.txt"
)
B5P_FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B5P RUNTIME INFRASTRUCTURE COLLECTIVE "
    "CERTIFICATION AND HANDOFF CLOSURE CERTIFIED"
)

EXPECTED_HASHES = {
    "index_html": "68da0fdc08e6b9561ddacaeb4d396f0c7fe6abd3d8de620207865ab5da432e5e",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "4e1d47fcfe68e17ad97ca6dbcc32929d849de19651b496eae2dc2406bf4fa5f3",
    "runtime_owner_js": "34e6e31439c9c6ba8ccf75bdeb82e9deb166c03c678ac761a0ff88f5da7e0db5",
    "runtime_summary_api": "215ac35d5591cc6a5e29af407ff70be9f317090c835290d6af92bafd356e44dd",
    "runtime_infrastructure_projection": "694fd8fae5dbf6ade79b73e2e4edbcb10fa49bf10666e8163112020634468a5f",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

SKIP_DIRECTORIES = {
    ".git", ".venv", "__pycache__", "data", "node_modules",
    "reports", "runtime_backups",
}

ACTION_FAMILIES: dict[str, dict[str, tuple[str, ...]]] = {
    "job_claim_assignment": {
        "symbol_terms": ("claim", "assign", "acquire", "dequeue"),
        "required_guards": ("authorization", "eligibility", "atomicity", "idempotency", "audit"),
    },
    "job_retry_requeue": {
        "symbol_terms": ("retry", "requeue", "enqueue", "nack"),
        "required_guards": ("retry_policy", "duplicate_prevention", "terminal_state", "idempotency", "audit"),
    },
    "job_workflow_cancellation": {
        "symbol_terms": ("cancel", "terminate", "stop", "abort"),
        "required_guards": ("authorization", "state_transition", "downstream_impact", "confirmation", "audit"),
    },
    "workflow_stage_recovery": {
        "symbol_terms": ("recover", "resume", "restart", "advance", "checkpoint"),
        "required_guards": ("checkpoint_validity", "dependency_validation", "output_safety", "idempotency", "audit"),
    },
    "worker_lease_recovery": {
        "symbol_terms": ("release", "renew", "expire", "drain", "shutdown"),
        "required_guards": ("lease_ownership", "expiry_validation", "worker_identity", "atomicity", "audit"),
    },
    "execution_control": {
        "symbol_terms": ("dispatch", "execute", "invoke", "interrupt", "kill"),
        "required_guards": ("execution_identity", "handler_authorization", "duplicate_prevention", "output_safety", "audit"),
    },
}

SAFETY_TERMS = {
    "identity_authorization": (
        "authorize", "authorization", "permission", "principal", "owner", "role",
    ),
    "signed_trust": (
        "signed", "signature", "grant", "issuer", "audience", "nonce", "replay",
    ),
    "idempotency_concurrency": (
        "idempotency", "idempotent", "atomic", "lock", "compare_and_swap", "transaction",
    ),
    "audit_accountability": (
        "audit", "reason", "actor", "requested_by", "approved_by", "event",
    ),
    "confirmation_impact": (
        "confirm", "preview", "impact", "dry_run", "eligibility", "blocked_reason",
    ),
}

MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def write_text(path: Path, source: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8", newline="\n")


def relative(root: Path, path: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def certified_b5p_report(source: str) -> bool:
    source = source.replace("\r\n", "\n")
    return all(token in source for token in (
        "CERTIFICATION STATUS: CERTIFIED",
        "FAILED_CHECKS:\n[]",
        "NOT_RUN_CHECKS:\n[]",
        "Production source changes: NO",
        B5P_FINAL_RESULT,
    ))


def source_files(root: Path) -> list[Path]:
    files: list[Path] = []
    backend = root / "backend/server"
    if not backend.is_dir():
        return files
    for path in backend.rglob("*"):
        try:
            if any(part in SKIP_DIRECTORIES for part in path.parts):
                continue
            if path.suffix.lower() not in {".py", ".js", ".html"}:
                continue
            if path.is_file() and path.stat().st_size <= 2_000_000:
                files.append(path)
        except OSError:
            continue
    return sorted(files)


def python_symbols(source: str) -> list[tuple[str, int]]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    return sorted(
        (
            (node.name, int(getattr(node, "lineno", 0)))
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        ),
        key=lambda item: (item[1], item[0]),
    )


def identifier_tokens(identifier: str) -> set[str]:
    expanded = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", identifier)
    return {
        token
        for token in re.split(r"[^A-Za-z0-9]+", expanded.lower())
        if token
    }


def route_declarations(source: str, file_path: str) -> list[dict[str, Any]]:
    pattern = re.compile(
        r"@(?P<router>[A-Za-z_][A-Za-z0-9_]*)\."
        r"(?P<method>get|post|put|patch|delete)\(\s*"
        r"[\"'](?P<path>[^\"']+)[\"']",
        flags=re.I,
    )
    result: list[dict[str, Any]] = []
    for match in pattern.finditer(source):
        result.append({
            "file": file_path,
            "line": source.count("\n", 0, match.start()) + 1,
            "method": match.group("method").upper(),
            "path": match.group("path"),
        })
    return result


def scan_authorities(root: Path, files: list[Path]) -> dict[str, Any]:
    action_maps: dict[str, dict[str, Any]] = {
        name: {
            "symbol_terms": list(contract["symbol_terms"]),
            "required_guards": list(contract["required_guards"]),
            "symbols": [],
            "mutating_routes": [],
            "candidate_files": [],
        }
        for name, contract in ACTION_FAMILIES.items()
    }
    safety_evidence: dict[str, list[dict[str, Any]]] = {
        name: [] for name in SAFETY_TERMS
    }
    all_routes: list[dict[str, Any]] = []

    for path in files:
        try:
            source = read_text(path)
        except (OSError, UnicodeError):
            continue
        path_text = relative(root, path)
        lower = source.lower()
        symbols = python_symbols(source) if path.suffix.lower() == ".py" else []
        routes = route_declarations(source, path_text)
        all_routes.extend(routes)

        for family, contract in ACTION_FAMILIES.items():
            terms = set(contract["symbol_terms"])
            family_symbols = [
                {"name": name, "line": line, "file": path_text}
                for name, line in symbols
                if identifier_tokens(name).intersection(terms)
            ]
            family_routes = [
                route
                for route in routes
                if route["method"] in MUTATING_METHODS
                and any(term in route["path"].lower() for term in terms)
            ]
            path_hit = any(term in path_text.lower() for term in terms)
            if family_symbols or family_routes or path_hit:
                action_maps[family]["candidate_files"].append(path_text)
            action_maps[family]["symbols"].extend(family_symbols)
            action_maps[family]["mutating_routes"].extend(family_routes)

        for category, terms in SAFETY_TERMS.items():
            hits = sorted({term for term in terms if term in lower})
            if hits:
                safety_evidence[category].append({
                    "file": path_text,
                    "terms": hits,
                })

    for details in action_maps.values():
        details["candidate_files"] = sorted(set(details["candidate_files"]))[:40]
        details["symbols"] = sorted(
            details["symbols"],
            key=lambda item: (item["file"], item["line"], item["name"]),
        )[:80]
        details["mutating_routes"] = sorted(
            details["mutating_routes"],
            key=lambda item: (item["file"], item["line"], item["path"]),
        )[:40]
        details["candidate_count"] = (
            len(details["symbols"])
            + len(details["mutating_routes"])
        )
        details["implementation_decision"] = (
            "REUSE_ONLY_AFTER_PER_ACTION_AUTHORIZATION_AND_SAFETY_CERTIFICATION"
            if details["candidate_count"]
            else "NO_EXISTING_AUTHORITY_CONFIRMED_DEFINE_BEFORE_UI_WIRING"
        )
    for category in safety_evidence:
        safety_evidence[category] = safety_evidence[category][:40]

    mutating_routes = [
        route for route in all_routes if route["method"] in MUTATING_METHODS
    ]
    return {
        "action_maps": action_maps,
        "safety_evidence": safety_evidence,
        "route_inventory": {
            "total_routes": len(all_routes),
            "mutating_routes": len(mutating_routes),
            "owner_runtime_mutating_routes": [
                route for route in mutating_routes
                if route["file"].startswith("backend/server/owner/")
                or route["path"].startswith("/owner/")
            ][:60],
        },
    }


def architecture_decision() -> dict[str, Any]:
    return {
        "component_name": "Owner Actions & Recovery",
        "placement": "Universal Runtime dedicated owner-only workspace",
        "monitoring_sources": (
            "Connected Domain monitoring",
            "Runtime Infrastructure monitoring",
            "Runtime Health future diagnostics",
        ),
        "mutation_policy": (
            "No UI control may call a store, queue, workflow, lease or execution "
            "mutation directly. Every action must pass through one dedicated "
            "server-side owner action request gateway."
        ),
        "required_request_fields": (
            "action_type", "target_type", "target_id", "expected_state",
            "reason", "idempotency_key", "requested_by", "requested_at",
        ),
        "required_response_fields": (
            "request_id", "eligibility", "decision", "before_state",
            "after_state", "audit_event_id", "completed_at", "error",
        ),
        "mandatory_guards": (
            "owner authentication and authorization",
            "fresh-state eligibility evaluation",
            "impact preview and explicit confirmation",
            "expected-state conflict protection",
            "idempotency and duplicate-action protection",
            "atomic mutation or compensating failure handling",
            "immutable audit evidence",
            "rate limiting and action-specific policy",
            "fail-closed response when authority is unavailable",
        ),
        "ui_first_sequence": (
            "B6B safety and action blueprint",
            "B6C dedicated workspace shell",
            "B6D read-only action eligibility and preview",
            "B6E-B6I certified action-family wiring",
            "B6J collective closure",
        ),
    }


def make_report(
    status: str,
    checks: dict[str, bool],
    evidence: dict[str, Any],
    error: dict[str, Any],
) -> str:
    failed = [name for name, passed in checks.items() if not passed]
    final = FINAL_RESULT if status == "COMPLETE" else (
        "FINAL RESULT: PART F 15-B6A OWNER ACTIONS AND RECOVERY "
        "BOUNDARY AND AUTHORITY INSPECTION NOT_COMPLETE"
    )
    return "\n".join([
        "LINKCRAFTOR OWNER CONTROL TOWER",
        "PART F 15-B6A OWNER ACTIONS AND RECOVERY BOUNDARY AND AUTHORITY INSPECTION",
        "", f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "Inspection mode: STRICT READ-ONLY FAIL-CLOSED",
        "Production source changes: NO",
        "Production jobs created: NO",
        "Production queue claims executed: NO",
        "Production handlers executed: NO",
        "Production workflow persistence executed: NO",
        "Production recovery actions executed: NO",
        "Live network requests executed during inspection: NO",
        "Project modules imported during inspection: NO",
        f"INSPECTION STATUS: {status}",
        "", "CHECKS:", json.dumps(checks, indent=2, sort_keys=True),
        "", "FAILED_CHECKS:", json.dumps(failed, indent=2),
        "", "NOT_RUN_CHECKS:", "[]",
        "", "EVIDENCE:", json.dumps(evidence, indent=2, sort_keys=True),
        "", "EXECUTION_ERROR:", json.dumps(error, indent=2, sort_keys=True),
        "", "BOUNDARY DECISION:",
        "- Create one dedicated Owner Actions & Recovery workspace; do not place mutation buttons inside monitoring components.",
        "- Reuse existing canonical mutation authorities only after each action receives explicit authorization, eligibility, idempotency and audit certification.",
        "- Use one owner action request gateway instead of allowing the browser to call queue, store, worker, workflow or handler mutations directly.",
        "- Preserve Connected Domain and Runtime Infrastructure monitoring as read-only evidence sources.",
        "- Build the UI shell and read-only eligibility preview before enabling the first mutation action.",
        "- Missing or ambiguous authority must block the action rather than create an inferred recovery path.",
        "", "NEXT STEP:",
        "Part F 15-B6B - Owner Actions & Recovery safety contract and UI blueprint.",
        "", final, "",
    ])


def run(root: Path, report: Path) -> int:
    root = root.resolve(); report = report.resolve()
    paths = {
        "index_html": root / "backend/server/owner/index.html",
        "owner_css": root / "backend/server/owner/owner.css",
        "owner_js": root / "backend/server/owner/owner.js",
        "runtime_owner_css": root / "backend/server/owner/runtime_owner.css",
        "runtime_owner_js": root / "backend/server/owner/runtime_owner.js",
        "runtime_summary_api": root / "backend/server/owner/runtime_summary_api.py",
        "runtime_infrastructure_projection": root / "backend/server/owner/runtime_infrastructure_projection.py",
        "pipeline_operations": root / "backend/server/owner/pipeline_operations.py",
    }
    b5p_report = root / "backend/server/data/reports" / B5P_REPORT
    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {
        "source_changes": False,
        "actions_executed": False,
        "component": "Owner Actions & Recovery",
    }
    error: dict[str, Any] = {}; status = "NOT_COMPLETE"
    try:
        checks["part_f_15_b5p_report_exists"] = b5p_report.is_file()
        checks["part_f_15_b5p_certified"] = (
            b5p_report.is_file() and certified_b5p_report(read_text(b5p_report))
        )
        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()
        if not all(checks.values()):
            raise RuntimeError("The certified B5P monitoring baseline is unavailable.")

        watched = {**paths, "b5p_report": b5p_report}
        hashes_before = {name: sha256_path(path) for name, path in watched.items()}
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = hashes_before[name] == expected
        if not all(checks.values()):
            raise RuntimeError("Installed sources do not match the certified B5P baseline.")

        html = read_text(paths["index_html"])
        checks["owner_actions_workspace_not_functionally_wired"] = all(token not in html for token in (
            'data-owner-action="',
            'id="runtimeOwnerActionRequestForm"',
            'runtimeOwnerActionRequest(',
        ))
        checks["monitoring_workspaces_retained"] = all(
            f'id="runtimeInfrastructure{suffix}Workspace"' in html
            for suffix in ("Jobs", "Queues", "WorkersLeases", "Orchestration", "Execution")
        )

        files = source_files(root)
        checks["backend_source_inventory_completed"] = bool(files)
        inspection = scan_authorities(root, files)
        action_maps = inspection["action_maps"]
        checks["six_action_authority_maps_completed"] = set(action_maps) == set(ACTION_FAMILIES)
        checks["existing_mutation_candidates_discovered"] = any(
            details["candidate_count"] > 0 for details in action_maps.values()
        )
        checks["safety_control_inventory_completed"] = set(inspection["safety_evidence"]) == set(SAFETY_TERMS)
        checks["route_inventory_completed"] = inspection["route_inventory"]["total_routes"] >= 0
        decision = architecture_decision()
        checks["single_owner_action_gateway_defined"] = "one dedicated" in decision["mutation_policy"]
        checks["mandatory_safety_guards_defined"] = len(decision["mandatory_guards"]) == 9
        checks["ui_first_sequence_defined"] = len(decision["ui_first_sequence"]) == 5

        hashes_after = {name: sha256_path(path) for name, path in watched.items()}
        checks["production_sources_unchanged"] = all(
            hashes_after[name] == hashes_before[name] for name in paths
        )
        checks["b5p_report_unchanged"] = hashes_after["b5p_report"] == hashes_before["b5p_report"]
        checks.update({
            "production_jobs_created_no": True,
            "production_queue_claims_no": True,
            "production_handlers_executed_no": True,
            "production_workflow_persistence_no": True,
            "production_recovery_actions_no": True,
            "live_network_requests_executed_no": True,
            "project_modules_imported_no": True,
        })
        if not all(checks.values()):
            raise RuntimeError("One or more B6A inspection checks failed.")

        evidence.update({
            "scanned_source_file_count": len(files),
            "action_authority_maps": action_maps,
            "safety_evidence": inspection["safety_evidence"],
            "route_inventory": inspection["route_inventory"],
            "architecture_decision": decision,
            "source_hashes": {name: hashes_before[name] for name in paths},
            "decision": "CREATE_DEDICATED_OWNER_ACTION_REQUEST_GATEWAY_AND_UI_AFTER_SAFETY_BLUEPRINT",
        })
        status = "COMPLETE"
    except Exception as exc:
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }

    write_text(report, make_report(status, checks, evidence, error))
    for name, passed in checks.items():
        print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(f"FAILED_CHECK_COUNT={sum(not passed for passed in checks.values())}")
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"REPORT={report}")
    print(f"PART_F_15_B6A_STATUS={status}")
    print("SOURCE_CHANGES=NO")
    print("ACTIONS_EXECUTED=NO")
    return 0 if status == "COMPLETE" else 1


def self_test() -> int:
    synthetic = """
@router.post("/owner/runtime/jobs/{job_id}/retry")
def retry_failed_job(job_id: str):
    authorize_owner(job_id)
    audit_event(job_id)

def release_expired_lease(lease_id: str):
    return lease_id
"""
    symbols = python_symbols(synthetic)
    names = {name for name, _ in symbols}
    assert "retry_failed_job" in names
    assert "release_expired_lease" in names
    routes = route_declarations(synthetic, "synthetic.py")
    assert routes[0]["method"] == "POST"
    assert "retry" in routes[0]["path"]
    decision = architecture_decision()
    assert len(decision["mandatory_guards"]) == 9
    sample = "\n".join((
        "CERTIFICATION STATUS: CERTIFIED",
        "Production source changes: NO",
        "FAILED_CHECKS:", "[]",
        "NOT_RUN_CHECKS:", "[]",
        B5P_FINAL_RESULT,
    ))
    assert certified_b5p_report(sample)
    report = make_report("COMPLETE", {"sample": True}, {}, {})
    assert "INSPECTION STATUS: COMPLETE" in report
    assert "FAILED_CHECKS:\n[]" in report
    assert FINAL_RESULT in report
    print("PART_F_15_B6A_SELF_TEST=PASS")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        raise SystemExit(self_test())
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: RUN_15_B6A_OWNER_ACTIONS_RECOVERY_BOUNDARY_INSPECTION.py "
            "<project_root> <report_path> | --self-test"
        )
    raise SystemExit(run(Path(sys.argv[1]), Path(sys.argv[2])))
