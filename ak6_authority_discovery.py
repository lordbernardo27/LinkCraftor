"""AK.6 bounded, read-only worker authority discovery.

Run at LinkCraftor repository root. Searches Python *source structure*, not
configurations, environment variables, private keys, tokens, or job records.
Does not import application modules or execute runtime code.
"""
from __future__ import annotations

import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd().resolve()
if ROOT.name.lower() != "linkcraftor":
    raise SystemExit("STOP: run from LinkCraftor repository root")

REQUIRED = {
    "queue": ROOT / "backend/server/orchestration/queue.py",
    "handler": ROOT / "backend/server/runtime/universal_runtime_registration.py",
    "permission": ROOT / "backend/server/runtime/security/connected_domain_job_permission.py",
    "scope": ROOT / "backend/server/runtime/universal_runtime_worker_scope_contract.py",
    "flags": ROOT / "backend/server/runtime/runtime_feature_flag_gateway.py",
}
for name, path in REQUIRED.items():
    if not path.is_file():
        raise SystemExit(f"STOP: missing {name}: {path.relative_to(ROOT)}")

original_hashes = {name: hashlib.sha256(p.read_bytes()).hexdigest() for name, p in REQUIRED.items()}
texts = {name: p.read_text(encoding="utf-8-sig") for name, p in REQUIRED.items()}
def verify_handler_entry_guards(source: str) -> bool:
    """Ensure both protected entry points start with the actual guard call.

    AST checking does not count the guard's definition as an invocation.
    """
    tree = ast.parse(source)
    expected = {"dispatch_registered_runtime_handler", "execute_registered_runtime_job_v1"}
    functions = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in expected]
    if len(functions) != len(expected) or {node.name for node in functions} != expected:
        return False
    for node in functions:
        if not node.body:
            return False
        first = node.body[0]
        if not isinstance(first, ast.Expr) or not isinstance(first.value, ast.Call):
            return False
        call = first.value
        if not isinstance(call.func, ast.Name) or call.func.id != "_ak_require_connected_domain_execution_authority":
            return False
        if len(call.args) != 1 or not isinstance(call.args[0], ast.Name) or call.args[0].id != "job" or call.keywords:
            return False
    return True

protection = {
    "queue_has_fail_closed_guard": "AK_CANONICAL_CONNECTED_DOMAIN_AUTHORIZATION_GUARD" in texts["queue"],
    "handler_has_fail_closed_guard": verify_handler_entry_guards(texts["handler"]),
    "permission_has_stage_binding": "AK6_CANONICAL_STAGE_HANDLER_BINDING" in texts["permission"],
    "permission_evaluator_present": "evaluate_job_execution_permission(" in texts["permission"],
    "queue_flag_function_present": "runtime_queue_claims_enabled" in texts["flags"],
}
if not all(protection.values()):
    raise SystemExit("STOP: a required AK.6 protection is absent; no runtime actions taken. " + repr(protection))

# Symbol-only discovery avoids printing credential values and sensitive source code.
terms = (
    "worker", "identity", "authorization", "authentication", "issuer", "principal",
    "attest", "credential", "permission", "trust", "service_token", "job_claim",
    "signed", "verify_token", "verify_signature", "lease",
)
strong_terms = ("issue", "verify", "validate", "authenticate", "authorize", "attest", "sign", "resolve", "bind")
paths = ROOT / "backend/server"
if not paths.is_dir():
    raise SystemExit("STOP: backend/server directory unavailable")

candidates = []
scanned = 0
parse_errors = []
for path in sorted(paths.rglob("*.py")):
    if any(part in {"__pycache__", "tests", "test", "fixtures", "runtime_backups", "data"} for part in path.relative_to(paths).parts):
        continue
    scanned += 1
    try:
        source = path.read_text(encoding="utf-8-sig")
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, UnicodeError, OSError) as exc:
        parse_errors.append({"file": str(path.relative_to(ROOT)), "error_type": type(exc).__name__})
        continue
    matches = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        name = node.name.lower()
        if any(t in name for t in terms) and any(v in name for v in strong_terms):
            matches.append({"symbol": node.name, "line": node.lineno})
    if matches:
        candidates.append({"path": str(path.relative_to(ROOT)), "symbols": matches[:15]})

# Do not claim that matching names authenticate anyone. Require source review.
report = {
    "purpose": "AK.6 discovery of existing authoritative worker evidence source",
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "read_only": True,
    "source_files_scanned": scanned,
    "protections": protection,
    "potential_authority_candidates": candidates,
    "parse_errors": parse_errors[:30],
    "production_authority_certified": False,
    "queue_or_handler_modified": False,
    "jobs_executed": False,
    "authorization_integration_status": "BLOCKED pending manual source verification of genuine trusted issuer",
    "scope": "AK.6 / AK.7 (no new architecture phase)",
}
for name, path in REQUIRED.items():
    if hashlib.sha256(path.read_bytes()).hexdigest() != original_hashes[name]:
        raise SystemExit(f"STOP: protected source changed during read-only review: {name}")

output = ROOT / "AK6_TRUSTED_AUTHORITY_DISCOVERY.json"
# Avoid overwriting an existing report.
if output.exists():
    output = ROOT / f"AK6_TRUSTED_AUTHORITY_DISCOVERY_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
output.write_text(json.dumps(report, indent=2), encoding="utf-8")
print("AK.6 — TRUSTED AUTHORITY DISCOVERY")
print("PASS: Queue, handler, scope and permission protections found")
print("PASS: Required source files unchanged")
print(f"Python source files scanned: {scanned}")
print(f"Files containing possible authority symbols: {len(candidates)}")
print("Production provider authenticated: NOT YET VERIFIED")
print("Atomic claim / handler production activation: NOT AUTHORIZED")
print(f"REPORT: {output}")
print("NEXT: share the JSON report for source-grounded provider integration")
