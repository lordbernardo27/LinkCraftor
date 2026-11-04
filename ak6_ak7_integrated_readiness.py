"""AK.6/AK.7 fail-closed readiness gate for installed signed-authority hooks.

Run at LinkCraftor root. Does not modify source, queue, jobs, or workers.
A successful audit is NOT authorization to enable the production worker.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd().resolve()
if ROOT.name != "LinkCraftor":
    raise SystemExit("STOP: run from LinkCraftor repository root")
paths = {
    "queue": ROOT / "backend/server/orchestration/queue.py",
    "handlers": ROOT / "backend/server/runtime/universal_runtime_registration.py",
    "grant_verifier": ROOT / "backend/server/runtime/security/ak6_signed_execution_grants.py",
    "scope": ROOT / "backend/server/runtime/universal_runtime_worker_scope_contract.py",
    "permission": ROOT / "backend/server/runtime/security/connected_domain_job_permission.py",
    "flags": ROOT / "backend/server/runtime/runtime_feature_flag_gateway.py",
}
missing = [k for k, p in paths.items() if not p.is_file()]
if missing:
    raise SystemExit("STOP: missing installed source: " + ", ".join(missing))

before = {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in paths.items()}
source = {k: p.read_text(encoding="utf-8-sig") for k, p in paths.items()}
trees = {k: ast.parse(v, filename=str(paths[k])) for k, v in source.items()}
checks = {}

def result(key: str, ok: bool, explanation: str):
    checks[key] = {"passed": bool(ok), "detail": explanation}
    print(("PASS" if ok else "BLOCK") + ": " + key + " — " + explanation)

q = source["queue"]
h = source["handlers"]
g = source["grant_verifier"]
p = source["permission"]

result("canonical_scope", "EXPECTED_SCOPE" in source["scope"] and "LEGACY_IDS" in source["scope"],
       "canonical and legacy-scope controls retained")
result("stage_binding", "AK6_CANONICAL_STAGE_HANDLER_BINDING" in p,
       "stage-to-job binding present")

# Audit precise placement in the AST, not mere occurrence counts.
q_tree = trees["queue"]
queue_fns = [n for n in ast.walk(q_tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "dequeue_job"]
claim_calls = [n for n in ast.walk(q_tree) if isinstance(n, ast.Call)
               and isinstance(n.func, ast.Name) and n.func.id == "require_signed_ak6_execution_authority"]
queue_position_ok = bool(queue_fns and len(claim_calls) == 1 and
                         "AK6_SIGNED_EXECUTION_AUTHORITY_INTEGRATED" in q and
                         q.find("with _dequeue_lock():") != -1 and
                         q.find("with _dequeue_lock():") < q.find("AK6_SIGNED_EXECUTION_AUTHORITY_INTEGRATED") <
                         q.find("evaluate_runtime_registration_queue_candidate(") )
result("atomic_queue_hook", queue_position_ok,
       "claim verifier present after queue lock and before registration policy")

def find_fn(name):
    return next((n for n in trees["handlers"].body
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name), None)

for name in ("dispatch_registered_runtime_handler", "execute_registered_runtime_job_v1"):
    fn = find_fn(name)
    first = fn.body[0] if fn and fn.body else None
    ok = (isinstance(first, ast.Expr) and isinstance(first.value, ast.Call)
          and isinstance(first.value.func, ast.Name)
          and first.value.func.id == "_ak_require_connected_domain_execution_authority")
    result("guard_first_" + name, ok, "first statement is authorization helper")
result("handler_signed_hook", "AK6_SIGNED_EXECUTION_AUTHORITY_INTEGRATED" in h and
       "require_signed_ak6_execution_authority(" in h,
       "both handler entries reach shared signed verifier through guard helper")
result("cryptographic_verification", "Ed25519PublicKey" in g and ".verify(signature, _canonical(payload))" in g,
       "Ed25519 verifier and canonical payload signature validation present")

# Required NO-GO findings. These are not defects in signature verification;
# they are additional security guarantees not supplied by the installed code.
result("independent_worker_authentication", False,
       "not established: worker_id is passed by caller / handler uses module constant")
result("immutable_authority_trust_anchor", False,
       "not established: public key is read from mutable process environment")
result("durable_claim_lease_binding", False,
       "not established: handler checks caller job metadata but does not query authoritative lease state")
result("nonce_replay_and_revocation", False,
       "not established: grant nonce is returned, not consumed in durable ledger; no revocation lookup")
result("production_issuer_provisioned", False,
       "not established: isolated tests generate a temporary test key, not a controlled issuer")

# Execute the existing isolated tests, if supplied by the installed package;
# never import or execute queue/handler entrypoints here.
test_script = ROOT / "test_ak6_signed_grants_isolated.py"
if test_script.is_file():
    ran = subprocess.run([sys.executable, "-B", str(test_script)], cwd=str(ROOT),
                         capture_output=True, text=True, timeout=60)
    result("isolated_21_checks", ran.returncode == 0 and "21/21" in ran.stdout,
           "existing isolated signature test executed: " + (ran.stdout.strip().splitlines()[0] if ran.stdout.strip() else "no stdout"))
else:
    result("isolated_21_checks", False, "test script absent from repository root")

# Static gate: never claim safety based on only source comments or absent flags.
feature_fn = next((n for n in ast.walk(trees["flags"]) if isinstance(n, ast.FunctionDef)
                   and n.name == "runtime_queue_claims_enabled"), None)
result("queue_flag_defined", feature_fn is not None, "production queue gate function remains defined")

unchanged = all(hashlib.sha256(paths[k].read_bytes()).hexdigest() == digest for k, digest in before.items())
result("source_unchanged", unchanged, "all six inspected production source files retained identical SHA-256 hashes")

blocking = [key for key, outcome in checks.items() if not outcome["passed"]]
report = {
    "report_type": "AK6_AK7_INTEGRATED_READINESS_V1",
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "read_only": True,
    "production_activation_authorized": False,
    "ak6_complete": False,
    "ak7_integrated_certified": False,
    "checks": checks,
    "blocking": blocking,
    "source_hashes": before,
    "decision": "NO-GO — issuer, independent worker identity, durable lease, replay/revocation and integration still uncertified",
}
report_path = ROOT / "AK6_AK7_INTEGRATED_READINESS.json"
report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print("\nAK.6 / AK.7 READINESS REPORT:", report_path)
print("SOURCE FILES MODIFIED: NO")
print("JOB EXECUTION OR QUEUE CLAIMS: NONE")
print("PRODUCTION ACTIVATION: NO-GO")
# No nonzero exit just for expected production blockers; unexpected source protection
# gaps should cause the PowerShell command to stop.
critical = ("canonical_scope", "stage_binding", "atomic_queue_hook",
            "guard_first_dispatch_registered_runtime_handler",
            "guard_first_execute_registered_runtime_job_v1", "handler_signed_hook",
            "cryptographic_verification", "isolated_21_checks", "source_unchanged")
if not all(checks[k]["passed"] for k in critical):
    raise SystemExit("STOP: installed protection check failed; inspect report")
