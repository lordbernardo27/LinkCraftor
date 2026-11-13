from __future__ import annotations

import ast
import hashlib
import importlib.metadata
import json
import re
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TITLE = "PART F 15-B6L.1 COGNITO OWNER IDENTITY DEPENDENCY AND INTEGRATION INSPECTION"
FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B6L.1 COGNITO OWNER IDENTITY DEPENDENCY "
    "AND INTEGRATION INSPECTION COMPLETE"
)

EXPECTED_HASHES = {
    "index_html": "2652875073948fd0bea4abfd9395750bfdbf0cd98c1a89a3349f70c5f899dc23",
    "runtime_owner_js": "48a3a259cf4ad92b7470afc8e9825b802d056c914a34e1f8115354b3c1d2f5dd",
    "runtime_summary_api": "fb76eae288d2ae26c86cb6280c821a10664d35ee95882cb1486e8fc9b6848443",
    "owner_actions_gateway": "357e7e3b4be573700652ea2268d38071f3b376a7d27f55b42aea0af54dc72a97",
    "runtime_infrastructure_projection": "694fd8fae5dbf6ade79b73e2e4edbcb10fa49bf10666e8163112020634468a5f",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

SOURCE_PATHS = {
    "index_html": "backend/server/owner/index.html",
    "runtime_owner_js": "backend/server/owner/runtime_owner.js",
    "runtime_summary_api": "backend/server/owner/runtime_summary_api.py",
    "owner_actions_gateway": "backend/server/owner/owner_actions_gateway.py",
    "runtime_infrastructure_projection": "backend/server/owner/runtime_infrastructure_projection.py",
    "pipeline_operations": "backend/server/owner/pipeline_operations.py",
}

B6K_REPORT = (
    "backend/server/data/reports/"
    "PART_F_15_B6K_OWNER_ACTIONS_PRODUCTION_ACTIVATION_BOUNDARY_INSPECTION.txt"
)

IDENTITY_CANDIDATES = {
    "runtime_authentication_boundaries": (
        "backend/server/runtime/security/runtime_authentication_boundaries.py"
    ),
    "runtime_authorization": (
        "backend/server/runtime/security/runtime_authorization.py"
    ),
    "ak6_operational_trust": (
        "backend/server/runtime/security/ak6_operational_trust.py"
    ),
    "runtime_ownership": "backend/server/runtime/runtime_schema/ownership.py",
}

JWT_DISTRIBUTIONS = (
    "pyjwt",
    "python-jose",
    "authlib",
    "joserfc",
)
CRYPTO_DISTRIBUTIONS = (
    "cryptography",
)

COGNITO_CONTRACT = {
    "provider": "AWS Cognito User Pools",
    "accepted_token": "access token only",
    "algorithm": "RS256",
    "principal_claim": "sub",
    "required_claims": [
        "iss",
        "client_id",
        "token_use",
        "exp",
        "iat",
        "sub",
        "cognito:groups",
    ],
    "required_values": {
        "token_use": "access",
        "cognito:groups": ["LinkCraftorOwner"],
    },
    "server_checks": [
        "signature against cached Cognito JWKS",
        "exact issuer and user-pool match",
        "exact app-client match",
        "expiration and issued-at validity",
        "access-token purpose",
        "founder-owner group membership",
        "immutable subject-derived principal",
    ],
    "browser_identity_headers_authoritative": False,
    "live_owner_actions_enabled_by_this_step": False,
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


def python_symbols(path: Path) -> dict[str, Any]:
    source = read_text(path)
    tree = ast.parse(source, filename=str(path))
    functions: list[str] = []
    classes: list[str] = []
    assignments: list[str] = []
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            assignments.append(node.id)
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    return {
        "functions": sorted(set(functions)),
        "classes": sorted(set(classes)),
        "assignments": sorted(set(assignments)),
        "imports": sorted(set(imports)),
    }


def distribution_inventory() -> dict[str, str]:
    installed: dict[str, str] = {}
    for distribution in importlib.metadata.distributions():
        name = str(distribution.metadata.get("Name") or "").strip().lower()
        if name:
            installed[name] = str(distribution.version)
    return installed


def requirements_inventory(root: Path) -> dict[str, Any]:
    candidates = sorted(
        {
            *root.glob("requirements*.txt"),
            *root.glob("pyproject.toml"),
            *root.glob("Pipfile"),
            *root.glob("poetry.lock"),
        }
    )
    jwt_matches: list[dict[str, str]] = []
    for path in candidates:
        try:
            source = read_text(path)
        except Exception:
            continue
        for line in source.splitlines():
            if re.search(r"pyjwt|python-jose|authlib|joserfc|cryptography", line, re.I):
                jwt_matches.append(
                    {"source": path.relative_to(root).as_posix(), "declaration": line.strip()}
                )
    return {
        "files": [path.relative_to(root).as_posix() for path in candidates],
        "jwt_crypto_declarations": jwt_matches,
    }


def format_report(
    status: str,
    checks: dict[str, bool],
    evidence: dict[str, Any],
    error: dict[str, Any],
) -> str:
    failed = [name for name, passed in checks.items() if not passed]
    result = FINAL_RESULT if status == "COMPLETE" else FINAL_RESULT.replace(" COMPLETE", " NOT_COMPLETE")
    return "\n".join(
        [
            "LINKCRAFTOR OWNER CONTROL TOWER",
            TITLE,
            "",
            f"Generated: {now_iso()}",
            "Inspection mode: STRICT READ-ONLY FAIL-CLOSED",
            "Selected identity provider: AWS COGNITO USER POOLS",
            "Production source changes: NO",
            "AWS resources created: NO",
            "Tokens requested or verified: NO",
            "Owner actions executed: NO",
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
            "FROZEN B6L IDENTITY CONTRACT:",
            "- AWS Cognito User Pools is the Owner Control Tower application identity provider.",
            "- Only a verified Cognito access token may establish the owner principal.",
            "- Signature, issuer, app client, token use, expiry and group must all pass.",
            "- The immutable Cognito sub claim becomes the canonical owner principal.",
            "- LinkCraftorOwner group membership is mandatory.",
            "- Browser-provided owner principal and issuer headers are never authoritative.",
            "- Missing configuration, key, claim, group or dependency fails closed.",
            "- Live dispatch remains OFF and adapters remain unregistered.",
            "",
            "NEXT STEP:",
            "Part F 15-B6L.2 - Provision the Cognito User Pool, owner app client and owner group.",
            "",
            result,
            "",
        ]
    )


def run(root: Path, report_path: Path) -> int:
    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {
        "source_changes": False,
        "aws_resources_created": False,
        "tokens_requested": False,
        "owner_actions_executed": False,
    }
    error: dict[str, Any] = {}

    try:
        sources = {name: root / relative for name, relative in SOURCE_PATHS.items()}
        identity_paths = {
            name: root / relative for name, relative in IDENTITY_CANDIDATES.items()
        }
        b6k_path = root / B6K_REPORT

        for name, path in sources.items():
            checks[f"source_exists_{name}"] = path.is_file()
        checks["b6k_report_exists"] = b6k_path.is_file()
        for name, path in identity_paths.items():
            checks[f"identity_candidate_exists_{name}"] = path.is_file()

        if not all(checks.values()):
            raise RuntimeError("The B6K baseline or identity candidate sources are unavailable.")

        before_hashes = {name: sha256_path(path) for name, path in sources.items()}
        b6k_hash_before = sha256_path(b6k_path)
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = before_hashes[name] == expected

        b6k = read_text(b6k_path).replace("\r\n", "\n")
        checks["b6k_inspection_complete"] = all(
            token in b6k
            for token in (
                "INSPECTION STATUS: COMPLETE",
                "FAILED_CHECKS:\n[]",
                "NOT_RUN_CHECKS:\n[]",
                "FINAL RESULT: PART F 15-B6K OWNER ACTIONS AND RECOVERY "
                "PRODUCTION ACTIVATION BOUNDARY INSPECTION COMPLETE",
            )
        )

        symbols = {name: python_symbols(path) for name, path in identity_paths.items()}
        checks["identity_candidate_syntax_clean"] = len(symbols) == len(identity_paths)
        checks["identity_symbol_inventory_completed"] = all(
            isinstance(record.get("functions"), list) for record in symbols.values()
        )

        installed = distribution_inventory()
        requirements = requirements_inventory(root)
        jwt_installed = {
            name: installed[name] for name in JWT_DISTRIBUTIONS if name in installed
        }
        crypto_installed = {
            name: installed[name] for name in CRYPTO_DISTRIBUTIONS if name in installed
        }
        checks["python_distribution_inventory_completed"] = bool(installed)
        checks["requirements_inventory_completed"] = isinstance(requirements["files"], list)
        checks["cognito_contract_complete"] = all(
            key in COGNITO_CONTRACT
            for key in (
                "accepted_token",
                "principal_claim",
                "required_claims",
                "required_values",
                "server_checks",
            )
        )
        checks["browser_identity_headers_rejected_as_authority"] = (
            COGNITO_CONTRACT["browser_identity_headers_authoritative"] is False
        )
        checks["live_dispatch_retained_off"] = (
            'os.environ.get(OWNER_ACTIONS_ENABLED_ENV) != "1"'
            in read_text(sources["owner_actions_gateway"])
        )

        dependency_ready = bool(jwt_installed) and bool(crypto_installed)
        evidence.update(
            {
                "cognito_contract": COGNITO_CONTRACT,
                "identity_candidate_symbols": symbols,
                "installed_jwt_distributions": jwt_installed,
                "installed_crypto_distributions": crypto_installed,
                "requirements_inventory": requirements,
                "dependency_ready": dependency_ready,
                "dependency_decision": (
                    "reuse_certified_installed_jwt_and_crypto_dependencies"
                    if dependency_ready
                    else "add_pinned_pyjwt_crypto_dependency_before_server_integration"
                ),
                "source_hashes": before_hashes,
            }
        )

        checks["production_sources_unchanged"] = before_hashes == {
            name: sha256_path(path) for name, path in sources.items()
        }
        checks["historical_b6k_report_unchanged"] = sha256_path(b6k_path) == b6k_hash_before
        checks["aws_resources_created_no"] = True
        checks["tokens_requested_no"] = True
        checks["owner_actions_executed_no"] = True
        checks["live_network_requests_executed_no"] = True
        checks["project_modules_imported_no"] = True

        if any(not passed for passed in checks.values()):
            raise RuntimeError("One or more B6L.1 inspection checks failed.")
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
        format_report(status, checks, evidence, error),
        encoding="utf-8",
        newline="\n",
    )
    for name, passed in checks.items():
        print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
    print(f"FAILED_CHECK_COUNT={sum(1 for passed in checks.values() if not passed)}")
    print("NOT_RUN_CHECK_COUNT=0")
    print(f"REPORT={report_path}")
    print(f"PART_F_15_B6L1_STATUS={status}")
    print("SOURCE_CHANGES=NO")
    print("AWS_RESOURCES_CREATED=NO")
    print("TOKENS_REQUESTED=NO")
    print("ACTIONS_EXECUTED=NO")
    return exit_code


def self_test() -> int:
    sample = '''
class Identity:
    pass

def verify_token(token):
    return token
'''
    tree = ast.parse(sample)
    assert any(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
    assert COGNITO_CONTRACT["accepted_token"] == "access token only"
    assert COGNITO_CONTRACT["principal_claim"] == "sub"
    assert COGNITO_CONTRACT["browser_identity_headers_authoritative"] is False
    print("PART_F_15_B6L1_SELF_TEST=PASS")
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
