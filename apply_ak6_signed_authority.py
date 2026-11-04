"""AK.6 scoped, fail-closed execution grant verifier insertion.

Never enables jobs, queue flag or workers. Backups and exact source preconditions.
Safe to retry: detects already-installed marker and verifies syntax.
"""
from __future__ import annotations
import ast
import hashlib
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd().resolve()
if ROOT.name != "LinkCraftor":
    raise SystemExit("STOP: run at LinkCraftor repository root")
SOURCE = Path(__file__).with_name("ak6_signed_execution_grants.py")
DEST = ROOT / "backend/server/runtime/security/ak6_signed_execution_grants.py"
QUEUE = ROOT / "backend/server/orchestration/queue.py"
HANDLERS = ROOT / "backend/server/runtime/universal_runtime_registration.py"
ADAPTER = ROOT / "backend/server/runtime/security/connected_domain_job_permission.py"
FLAGS = ROOT / "backend/server/runtime/runtime_feature_flag_gateway.py"
SCOPE = ROOT / "backend/server/runtime/universal_runtime_worker_scope_contract.py"
for p in (SOURCE, QUEUE, HANDLERS, ADAPTER, FLAGS, SCOPE):
    if not p.is_file():
        raise SystemExit(f"STOP: missing required source {p}")

queue_original = QUEUE.read_bytes()
handler_original = HANDLERS.read_bytes()
q = queue_original.decode("utf-8-sig").replace("\r\n", "\n")
h = handler_original.decode("utf-8-sig").replace("\r\n", "\n")
if "AK6_SIGNED_EXECUTION_AUTHORITY_INTEGRATED" in q or "AK6_SIGNED_EXECUTION_AUTHORITY_INTEGRATED" in h:
    if ("AK6_SIGNED_EXECUTION_AUTHORITY_INTEGRATED" in q
        and "AK6_SIGNED_EXECUTION_AUTHORITY_INTEGRATED" in h
        and DEST.is_file()):
        print("ALREADY INSTALLED: signed authority verification hooks")
        raise SystemExit(0)
    raise SystemExit("STOP: partial integration detected")
if DEST.exists():
    raise SystemExit("STOP: signed grant module exists but integration absent")
if "AK6_CANONICAL_STAGE_HANDLER_BINDING" not in ADAPTER.read_text(encoding="utf-8-sig"):
    raise SystemExit("STOP: certified stage-binding patch absent")
if "AK_CANONICAL_CONNECTED_DOMAIN_AUTHORIZATION_GUARD" not in q or "AK_REGISTERED_HANDLER_EXECUTION_GUARD" not in h:
    raise SystemExit("STOP: previously certified safeguards absent")

q_old = '''            if candidate.job_id in _protected_connected_domain_jobs:
                raise PermissionError(
                    "Connected Domain queue claim denied: "
                    "trusted production authorization is not connected."
                )'''
q_new = '''            if candidate.job_id in _protected_connected_domain_jobs:
                # AK6_SIGNED_EXECUTION_AUTHORITY_INTEGRATED
                # Verified UNDER the atomic queue lock, before all mutations.
                from backend.server.runtime.security.ak6_signed_execution_grants import (
                    require_signed_ak6_execution_authority,
                )
                require_signed_ak6_execution_authority(
                    job=candidate, worker_id=worker_id, action="claim",
                )'''
h_old = '''        if job_id in EXPECTED_SCOPE:
            raise PermissionError(
                "Connected Domain handler execution denied: "
                "trusted per-job authorization is not connected."
            )'''
h_new = '''        if job_id in EXPECTED_SCOPE:
            # AK6_SIGNED_EXECUTION_AUTHORITY_INTEGRATED
            from backend.server.runtime.security.ak6_signed_execution_grants import (
                require_signed_ak6_execution_authority,
                WORKER_ID,
            )
            require_signed_ak6_execution_authority(
                job=job, worker_id=WORKER_ID, action="execute",
            )'''
if q.count(q_old) != 1 or h.count(h_old) != 1:
    raise SystemExit("STOP: actual queue/handler guard differs from reviewed source")

# Preserve Windows CRLF if present; Python read_text universal-newline isn't used.
def preserve(text, original):
    if b"\r\n" in original:
        return text.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8")
    return text.encode("utf-8")

q_updated = q.replace(q_old, q_new, 1)
h_updated = h.replace(h_old, h_new, 1)
for p, data in ((QUEUE, q_updated), (HANDLERS, h_updated), (SOURCE, SOURCE.read_text(encoding="utf-8-sig"))):
    ast.parse(data, filename=str(p))
# Ensure handlers only call guard at first statement.
h_tree = ast.parse(h_updated)
for name in ("dispatch_registered_runtime_handler", "execute_registered_runtime_job_v1"):
    fn = next((x for x in h_tree.body if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef)) and x.name == name), None)
    if not fn or not isinstance(fn.body[0], ast.Expr) or not isinstance(fn.body[0].value, ast.Call) or getattr(fn.body[0].value.func, "id", None) != "_ak_require_connected_domain_execution_authority":
        raise SystemExit("STOP: handler execution guard not first statement: " + name)
# Ensure queue check lives within the lock and precedes runtime registration policy.
if not (q_updated.index("with _dequeue_lock():") < q_updated.index("AK6_SIGNED_EXECUTION_AUTHORITY_INTEGRATED") < q_updated.index("evaluate_runtime_registration_queue_candidate(") ):
    raise SystemExit("STOP: queue authorization boundary not preserved")

backupdir = ROOT / "backend/server/data/runtime_backups" / (
    "connect_domain_AK6_SIGNED_AUTHORITY_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
backupdir.mkdir(parents=True, exist_ok=False)
for src in (QUEUE, HANDLERS):
    shutil.copy2(src, backupdir / src.name)
    assert (backupdir / src.name).read_bytes() == src.read_bytes()
protected = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in (ADAPTER, FLAGS, SCOPE)}
changed = []
try:
    for path, was, updated in ((QUEUE, queue_original, preserve(q_updated, queue_original)),
                                (HANDLERS, handler_original, preserve(h_updated, handler_original)),
                                (DEST, None, SOURCE.read_bytes())):
        if was is None and path.exists():
            raise RuntimeError("STOP: unexpected new module present")
        if was is not None and path.read_bytes() != was:
            raise RuntimeError("STOP: concurrent source edit: " + str(path))
        fd, tmppath = tempfile.mkstemp(prefix=".ak6_", suffix=".tmp", dir=path.parent)
        os.close(fd)
        tmp = Path(tmppath)
        try:
            tmp.write_bytes(updated)
            ast.parse(tmp.read_text(encoding="utf-8-sig"))
            os.replace(tmp, path)
            changed.append(path)
        finally:
            tmp.unlink(missing_ok=True)
    for p, digest in protected.items():
        if hashlib.sha256(p.read_bytes()).hexdigest() != digest:
            raise RuntimeError("STOP: protected scope/flags/adapter unexpectedly changed")
    print("PASS: atomic queue claim verifies externally signed per-job grant")
    print("PASS: both handler entries verify signed authority before execution")
    print("PASS: existing queue lock and handler guard locations retained")
    print("PASS: queue feature flag, scope and permission adapter untouched")
    print("BACKUP:", backupdir)
    print("AK.6 SIGNED GRANT VERIFIER: INSTALLED INACTIVE")
    print("PRODUCTION TRUST ISSUER: NOT PROVISIONED / NOT CERTIFIED")
    print("PRODUCTION ACTIVATION: NOT AUTHORIZED")
except BaseException:
    for p in reversed(changed):
        if p == DEST:
            p.unlink(missing_ok=True)
        else:
            shutil.copy2(backupdir / p.name, p)
    print("ROLLBACK: original queue and handler sources restored")
    raise
