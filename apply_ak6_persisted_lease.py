"""Fail-closed AK.6 persisted-lease enforcement. Does not enable production claims.

Requires earlier signed-grant hooks. Changes only AK6 grant verifier plus new
lease validation module. Backups, exact anchors, syntax and dry-run checks.
"""
from __future__ import annotations
import ast
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd().resolve()
if ROOT.name != 'LinkCraftor':
    raise SystemExit('STOP: run from LinkCraftor project root')
HERE = Path(__file__).resolve().parent
SRC = HERE / 'ak6_authoritative_lease.py'
TEST = HERE / 'test_ak6_authoritative_lease.py'
DEST = ROOT / 'backend/server/runtime/security/ak6_authoritative_lease.py'
VERIFIER = ROOT / 'backend/server/runtime/security/ak6_signed_execution_grants.py'
QUEUE = ROOT / 'backend/server/orchestration/queue.py'
HANDLER = ROOT / 'backend/server/runtime/universal_runtime_registration.py'
FLAGS = ROOT / 'backend/server/runtime/runtime_feature_flag_gateway.py'
for p in (SRC, TEST, VERIFIER, QUEUE, HANDLER, FLAGS):
    if not p.is_file(): raise SystemExit('STOP: required source missing: ' + str(p))
q = QUEUE.read_text(encoding='utf-8-sig')
h = HANDLER.read_text(encoding='utf-8-sig')
if ('AK6_SIGNED_EXECUTION_AUTHORITY_INTEGRATED' not in q
    or 'AK6_SIGNED_EXECUTION_AUTHORITY_INTEGRATED' not in h):
    raise SystemExit('STOP: signed integration is not installed at both boundaries')
original = VERIFIER.read_bytes()
original_src = original.decode('utf-8-sig')
marker = 'AK6_AUTHORITATIVE_PERSISTED_LEASE_ENFORCED'
if marker in original_src:
    if DEST.is_file() and DEST.read_bytes() == SRC.read_bytes():
        print('ALREADY INSTALLED: persisted lease check, no changes')
        raise SystemExit(0)
    raise SystemExit('STOP: partial or changed installation detected')
if DEST.exists(): raise SystemExit('STOP: lease module exists but verifier is not wired')
# Check only the exact local call site. No rewriting queue, handler or worker.
needle = '''    return payload["nonce"]'''
if original_src.count(needle) != 1:
    raise SystemExit('STOP: unexpected signed grant verification return anchor')
replacement = '''    if action == "execute":
        # AK6_AUTHORITATIVE_PERSISTED_LEASE_ENFORCED
        # Never trust self-declared claimed status or lease metadata.
        from backend.server.runtime.security.ak6_authoritative_lease import (
            require_persisted_ak6_lease,
        )
        require_persisted_ak6_lease(job=job, worker_id=worker_id)
    return payload["nonce"]'''
updated = original_src.replace(needle, replacement, 1)
for p, content in ((VERIFIER, updated), (SRC, SRC.read_text(encoding='utf-8-sig'))):
    ast.parse(content, filename=str(p))
# Before installation, isolated tests must succeed without importing production.
run = subprocess.run([sys.executable, '-B', str(TEST)], capture_output=True,
                     text=True, timeout=40)
if run.returncode != 0 or '18/18' not in run.stdout:
    raise SystemExit('STOP: isolated lease test failed: ' + run.stdout + run.stderr)
print(run.stdout.rstrip())
watch = (QUEUE, HANDLER, FLAGS)
hashes = {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in watch}
backup_dir = ROOT / 'backend/server/data/runtime_backups' / (
    'connect_domain_AK6_PERSISTED_LEASE_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
backup_dir.mkdir(parents=True, exist_ok=False)
shutil.copy2(VERIFIER, backup_dir / VERIFIER.name)
if (backup_dir / VERIFIER.name).read_bytes() != original:
    raise SystemExit('STOP: backup integrity mismatch')
changed = []
try:
    for path, was, text_or_bytes in ((DEST, None, SRC.read_bytes()),
                                    (VERIFIER, original, updated)):
        if was is None and path.exists(): raise RuntimeError('concurrent new module')
        if was is not None and path.read_bytes() != was:
            raise RuntimeError('concurrent verifier edit')
        if isinstance(text_or_bytes, str):
            if b'\r\n' in original:
                content = text_or_bytes.replace('\r\n','\n').replace('\n','\r\n').encode('utf-8')
            else: content = text_or_bytes.encode('utf-8')
        else: content = text_or_bytes
        fd, tmp_path = tempfile.mkstemp(prefix='.ak6_lease_', suffix='.tmp',dir=path.parent)
        os.close(fd)
        tmp=Path(tmp_path)
        try:
            tmp.write_bytes(content)
            ast.parse(tmp.read_text(encoding='utf-8-sig'))
            os.replace(tmp, path)
            changed.append(path)
        finally: tmp.unlink(missing_ok=True)
    for p in watch:
        if hashlib.sha256(p.read_bytes()).hexdigest() != hashes[str(p)]:
            raise RuntimeError('STOP: protected source changed')
    assert marker in VERIFIER.read_text(encoding='utf-8-sig')
    print('PASS: signed execution verifier now checks persisted job and live lease')
    print('PASS: atomic queue, handler and production feature flags unchanged')
    print('BACKUP:', backup_dir)
    print('AK.6 PERSISTED LEASE VALIDATION: INSTALLED INACTIVE')
    print('ISSUER / WORKER IDENTITY / REPLAY / REVOCATION: NOT CERTIFIED')
    print('PRODUCTION ACTIVATION: NO-GO')
except BaseException:
    for path in reversed(changed):
        if path == DEST: path.unlink(missing_ok=True)
        else: shutil.copy2(backup_dir / VERIFIER.name, VERIFIER)
    print('ROLLBACK: original signed verifier restored')
    raise
