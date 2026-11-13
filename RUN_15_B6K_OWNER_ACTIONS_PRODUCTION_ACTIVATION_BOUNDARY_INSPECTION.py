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


TITLE = (
    "PART F 15-B6K OWNER ACTIONS AND RECOVERY PRODUCTION ACTIVATION "
    "BOUNDARY INSPECTION"
)
FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B6K OWNER ACTIONS AND RECOVERY PRODUCTION "
    "ACTIVATION BOUNDARY INSPECTION COMPLETE"
)

EXPECTED_HASHES = {
    "index_html": "2652875073948fd0bea4abfd9395750bfdbf0cd98c1a89a3349f70c5f899dc23",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "3ba0fc871d432c013f9a7d43deaf9cde4f968447c4e489394a1f4b3dab2715fd",
    "runtime_owner_js": "48a3a259cf4ad92b7470afc8e9825b802d056c914a34e1f8115354b3c1d2f5dd",
    "runtime_summary_api": "fb76eae288d2ae26c86cb6280c821a10664d35ee95882cb1486e8fc9b6848443",
    "owner_actions_gateway": "357e7e3b4be573700652ea2268d38071f3b376a7d27f55b42aea0af54dc72a97",
    "runtime_infrastructure_projection": "694fd8fae5dbf6ade79b73e2e4edbcb10fa49bf10666e8163112020634468a5f",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

SOURCE_PATHS = {
    "index_html": "backend/server/owner/index.html",
    "owner_css": "backend/server/owner/owner.css",
    "owner_js": "backend/server/owner/owner.js",
    "runtime_owner_css": "backend/server/owner/runtime_owner.css",
    "runtime_owner_js": "backend/server/owner/runtime_owner.js",
    "runtime_summary_api": "backend/server/owner/runtime_summary_api.py",
    "owner_actions_gateway": "backend/server/owner/owner_actions_gateway.py",
    "runtime_infrastructure_projection": (
        "backend/server/owner/runtime_infrastructure_projection.py"
    ),
    "pipeline_operations": "backend/server/owner/pipeline_operations.py",
}

B6J_REPORT = (
    "backend/server/data/reports/"
    "PART_F_15_B6J_OWNER_ACTIONS_RECOVERY_COLLECTIVE_DEVELOPMENT_CERTIFICATION.txt"
)

REQUIRED_GATEWAY_TOKENS = (
    'OWNER_ACTIONS_ENABLED_ENV = "LINKCRAFTOR_OWNER_ACTIONS_ENABLED"',
    'OWNER_ACTION_SECRET_ENV = "LINKCRAFTOR_OWNER_ACTION_SIGNING_SECRET"',
    'OWNER_ACTION_ISSUER_ENV = "LINKCRAFTOR_OWNER_ACTION_TRUSTED_ISSUER"',
    "ACTION_CONTRACTS",
    "register_owner_action_adapter",
    "submit_owner_action",
    "x-linkcraftor-owner-principal",
    "x-linkcraftor-owner-issuer",
    "expected_state",
    "idempotency_key",
    "confirmation_token",
    "_audit(",
)

ACTION_TYPES = (
    "job_claim",
    "job_retry",
    "job_requeue",
    "job_cancel",
    "workflow_retry",
    "workflow_cancel",
    "stage_recover",
    "worker_drain",
    "lease_release",
    "execution_cancel",
    "execution_terminate",
)

MUTATION_PATTERNS = {
    "queue_claim": re.compile(r"\b(claim|claim_next|claim_job|reserve)\b", re.I),
    "job_retry_requeue": re.compile(r"\b(retry|requeue|enqueue|queue_job)\b", re.I),
    "cancel_terminate": re.compile(r"\b(cancel|terminate|abort|kill)\b", re.I),
    "workflow_recovery": re.compile(r"\b(recover|resume|restart|retry_stage)\b", re.I),
    "worker_lease": re.compile(r"\b(drain|release_lease|renew_lease|acquire_lease)\b", re.I),
}

IDENTITY_PATTERNS = {
    "authentication": re.compile(r"\b(authenticate|authentication|current_user)\b", re.I),
    "authorization": re.compile(r"\b(authorize|authorization|permission|role)\b", re.I),
    "owner_principal": re.compile(r"\b(owner_principal|owner_identity|principal)\b", re.I),
    "trusted_issuer": re.compile(r"\b(trusted_issuer|issuer|identity_provider)\b", re.I),
    "aws_identity": re.compile(r"\b(cognito|iam identity center|sts|oidc|jwt)\b", re.I),
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def scan_python_sources(root: Path) -> dict[str, Any]:
    backend = root / "backend" / "server"
    files = sorted(backend.rglob("*.py")) if backend.is_dir() else []
    identity: dict[str, list[str]] = {key: [] for key in IDENTITY_PATTERNS}
    mutations: dict[str, list[str]] = {key: [] for key in MUTATION_PATTERNS}
    routes: list[dict[str, str]] = []
    syntax_failures: list[str] = []

    route_pattern = re.compile(
        r"@(?:router|app)\.(?:post|put|patch|delete)\(\s*[fr]?['\"]([^'\"]+)['\"]"
    )

    for path in files:
        relative = path.relative_to(root).as_posix()
        try:
            source = read_text(path)
            ast.parse(source, filename=relative)
        except Exception:
            syntax_failures.append(relative)
            continue

        for name, pattern in IDENTITY_PATTERNS.items():
            if pattern.search(source):
                identity[name].append(relative)
        for name, pattern in MUTATION_PATTERNS.items():
            if pattern.search(source):
                mutations[name].append(relative)
        for match in route_pattern.finditer(source):
            routes.append({"source": relative, "route": match.group(1)})

    return {
        "python_file_count": len(files),
        "identity_candidates": identity,
        "mutation_candidates": mutations,
        "mutation_routes": routes,
        "syntax_failures": syntax_failures,
    }


def format_report(
    *,
    status: str,
    checks: dict[str, bool],
    evidence: dict[str, Any],
    error: dict[str, Any],
) -> str:
    failed = [name for name, passed in checks.items() if not passed]
    lines = [
        "LINKCRAFTOR OWNER CONTROL TOWER",
        TITLE,
        "",
        f"Generated: {now_iso()}",
        "Inspection mode: STRICT READ-ONLY FAIL-CLOSED",
        "Production source changes: NO",
        "Preview requests executed: NO",
        "Owner action requests executed: NO",
        "Production mutations executed: NO",
        f"INSPECTION STATUS: {status}",
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
        "EVIDENCE:",
        json.dumps(evidence, indent=2, sort_keys=True),
        "",
        "EXECUTION_ERROR:",
        json.dumps(error, indent=2, sort_keys=True),
        "",
        "ACTIVATION BOUNDARY:",
        "- B6L must bind a server-verified production owner principal and trusted issuer.",
        "- Browser-supplied identity headers alone must never establish owner authority.",
        "- B6M must implement one certified server-only adapter per approved action contract.",
        "- Every adapter must enforce expected state, idempotency, bounded scope and audit.",
        "- B6N may enable live dispatch only through controlled configuration after negative tests.",
        "- B6O must certify the complete production chain and rollback authority.",
        "- Missing identity, adapter, state, confirmation or audit authority must fail closed.",
        "",
        "NEXT STEP:",
        "Part F 15-B6L - Trusted production owner identity integration.",
        "",
        FINAL_RESULT if status == "COMPLETE" else FINAL_RESULT.replace(" COMPLETE", " NOT_COMPLETE"),
        "",
    ]
    return "\n".join(lines)


def run(root: Path, report_path: Path) -> int:
    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {
        "source_changes": False,
        "preview_requests_executed": False,
        "owner_actions_executed": False,
    }
    error: dict[str, Any] = {}
    before_hashes: dict[str, str] = {}

    try:
        paths = {name: root / relative for name, relative in SOURCE_PATHS.items()}
        for name, path in paths.items():
            checks[f"source_exists_{name}"] = path.is_file()
        checks["b6j_report_exists"] = (root / B6J_REPORT).is_file()

        if not all(checks.values()):
            raise RuntimeError("The certified B6J source baseline is unavailable.")

        before_hashes = {name: sha256_path(path) for name, path in paths.items()}
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = before_hashes[name] == expected

        b6j_path = root / B6J_REPORT
        b6j_hash_before = sha256_path(b6j_path)
        b6j = read_text(b6j_path).replace("\r\n", "\n")
        checks["b6j_collectively_certified"] = all(
            token in b6j
            for token in (
                "CERTIFICATION STATUS: CERTIFIED",
                "FAILED_CHECKS:\n[]",
                "NOT_RUN_CHECKS:\n[]",
                "FINAL RESULT: PART F 15-B6J OWNER ACTIONS AND RECOVERY "
                "COLLECTIVE DEVELOPMENT CERTIFICATION CERTIFIED",
            )
        )

        gateway = read_text(paths["owner_actions_gateway"])
        api = read_text(paths["runtime_summary_api"])
        checks["gateway_python_syntax"] = bool(ast.parse(gateway))
        checks["runtime_api_python_syntax"] = bool(ast.parse(api))
        checks["gateway_safety_contract_present"] = all(
            token in gateway for token in REQUIRED_GATEWAY_TOKENS
        )
        checks["eleven_action_contracts_present"] = all(
            f'"{action}"' in gateway for action in ACTION_TYPES
        )
        checks["preview_route_present_once"] = (
            api.count('@router.post("/actions/preview")') == 1
        )
        checks["execute_route_present_once"] = (
            api.count('@router.post("/actions/execute")') == 1
        )
        checks["live_dispatch_defaults_off"] = (
            'os.environ.get(OWNER_ACTIONS_ENABLED_ENV) != "1"' in gateway
        )
        checks["identity_requires_principal_and_issuer"] = all(
            token in gateway
            for token in (
                'headers.get("x-linkcraftor-owner-principal")',
                'headers.get("x-linkcraftor-owner-issuer")',
                "issuer != expected_issuer",
            )
        )
        checks["adapter_registration_is_server_only"] = all(
            token in gateway
            for token in (
                "def register_owner_action_adapter(",
                "browser requests cannot register adapters",
                "_ADAPTERS[action_type] = adapter",
            )
        )
        checks["no_installed_adapter_registration_in_gateway"] = (
            gateway.count("register_owner_action_adapter(") == 1
        )

        inventory = scan_python_sources(root)
        checks["backend_source_inventory_completed"] = inventory["python_file_count"] > 0
        checks["backend_python_syntax_inventory_recorded"] = isinstance(
            inventory["syntax_failures"], list
        )
        checks["activation_critical_python_syntax_clean"] = all(
            bool(ast.parse(read_text(paths[name])))
            for name in (
                "runtime_summary_api",
                "owner_actions_gateway",
                "runtime_infrastructure_projection",
                "pipeline_operations",
            )
        )
        checks["identity_candidates_inventory_completed"] = all(
            key in inventory["identity_candidates"] for key in IDENTITY_PATTERNS
        )
        checks["mutation_candidates_inventory_completed"] = all(
            key in inventory["mutation_candidates"] for key in MUTATION_PATTERNS
        )
        checks["mutation_route_inventory_completed"] = isinstance(
            inventory["mutation_routes"], list
        )

        evidence.update(
            {
                "activation_sequence": ["B6L_identity", "B6M_adapters", "B6N_activation", "B6O_certification"],
                "action_contracts": list(ACTION_TYPES),
                "required_environment_authorities": [
                    "LINKCRAFTOR_OWNER_ACTIONS_ENABLED",
                    "LINKCRAFTOR_OWNER_ACTION_SIGNING_SECRET",
                    "LINKCRAFTOR_OWNER_ACTION_TRUSTED_ISSUER",
                ],
                "required_trusted_identity": [
                    "server_verified_owner_principal",
                    "server_verified_trusted_issuer",
                ],
                "inventory": inventory,
                "source_hashes": before_hashes,
            }
        )

        after_hashes = {name: sha256_path(path) for name, path in paths.items()}
        checks["production_sources_unchanged"] = before_hashes == after_hashes
        checks["historical_b6j_report_unchanged"] = (
            sha256_path(b6j_path) == b6j_hash_before
        )
        checks["preview_requests_executed_no"] = True
        checks["owner_action_requests_executed_no"] = True
        checks["production_mutations_executed_no"] = True
        checks["project_modules_imported_no"] = True
        checks["live_network_requests_executed_no"] = True

        failed = [name for name, passed in checks.items() if not passed]
        if failed:
            raise RuntimeError("One or more B6K inspection checks failed.")
        status = "COMPLETE"
        exit_code = 0
    except Exception as exc:
        status = "NOT_COMPLETE"
        exit_code = 1
        error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        format_report(status=status, checks=checks, evidence=evidence, error=error),
        encoding="utf-8",
        newline="\n",
    )

    for name, passed in checks.items():
        print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(f"FAILED_CHECK_COUNT={sum(1 for passed in checks.values() if not passed)}")
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"REPORT={report_path}")
    print(f"PART_F_15_B6K_STATUS={status}")
    print("SOURCE_CHANGES=NO")
    print("PREVIEW_REQUESTS_EXECUTED=NO")
    print("ACTIONS_EXECUTED=NO")
    return exit_code


def self_test() -> int:
    sample = '''
@router.post("/thing")
def retry_job():
    principal = current_user
    action = "retry"
    return claim_job(action)
'''
    ast.parse(sample)
    assert MUTATION_PATTERNS["queue_claim"].search(sample)
    assert MUTATION_PATTERNS["job_retry_requeue"].search(sample)
    assert IDENTITY_PATTERNS["authentication"].search(sample)
    assert IDENTITY_PATTERNS["owner_principal"].search(sample)
    assert len(ACTION_TYPES) == 11
    print("PART_F_15_B6K_SELF_TEST=PASS")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--self-test":
        return self_test()
    if len(argv) != 3:
        print(f"Usage: {argv[0]} ROOT REPORT", file=sys.stderr)
        return 2
    return run(Path(argv[1]).resolve(), Path(argv[2]).resolve())


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
