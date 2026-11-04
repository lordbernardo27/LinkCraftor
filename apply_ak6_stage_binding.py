"""AK.6 source-grounded hardening: exact per-job stage binding.

Execute from LinkCraftor repository root. Modifies only the AK.6 adapter.
Does NOT activate workers, queue claims, or real jobs.
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
if ROOT.name != 'LinkCraftor':
    raise SystemExit('STOP: Run from LinkCraftor project root')

adapter = ROOT / 'backend/server/runtime/security/connected_domain_job_permission.py'
scope = ROOT / 'backend/server/runtime/universal_runtime_worker_scope_contract.py'
queue = ROOT / 'backend/server/orchestration/queue.py'
handlers = ROOT / 'backend/server/runtime/universal_runtime_registration.py'
registration = ROOT / 'backend/server/runtime/universal_runtime_worker_service_registration.py'
for p in (adapter, scope, queue, handlers, registration):
    if not p.is_file():
        raise SystemExit('STOP: Missing required source: ' + str(p))

WATCH = [queue, handlers, registration, scope]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
before = {str(p): sha(p) for p in WATCH}

q = queue.read_text(encoding='utf-8-sig')
h = handlers.read_text(encoding='utf-8-sig')
if 'AK_CANONICAL_CONNECTED_DOMAIN_AUTHORIZATION_GUARD' not in q:
    raise SystemExit('STOP: Atomic queue deny guard absent')
if 'AK_REGISTERED_HANDLER_EXECUTION_GUARD' not in h:
    raise SystemExit('STOP: Handler deny guard absent')

original = adapter.read_bytes()
source = original.decode('utf-8-sig')
MARKER = 'AK6_CANONICAL_STAGE_HANDLER_BINDING'
if MARKER in source:
    print('ALREADY INSTALLED: canonical stage-handler binding')
    raise SystemExit(0)
old = '''    WORKSPACE_ID,\n)'''
new = '''    WORKSPACE_ID,\n    STAGES,\n)'''
newline = '\r\n' if '\r\n' in source else '\n'
old = old.replace('\n', newline)
new = new.replace('\n', newline)
if source.count(old) != 1:
    raise SystemExit('STOP: Unexpected scope import; no edits made')
source = source.replace(old, new, 1)
anchor = '''    if not isinstance(evidence, JobExecutionPermissionEvidence):'''
inject = '''    # AK6_CANONICAL_STAGE_HANDLER_BINDING
    # The handler key supplied by a caller must match the job's
    # frozen stage identity. Merely listing a key in evidence is
    # insufficient to authorize a different handler for this job.
    expected_stage = next(
        (stage for stage, canonical_job_id, _, _ in STAGES
         if canonical_job_id == job_id),
        None,
    )
    if handler_key != expected_stage:
        raise PermissionError("AK_DENY_STAGE_HANDLER_MISMATCH")

'''
if source.count(anchor) != 1:
    raise SystemExit('STOP: Unexpected evidence location; no edits made')
inject = inject.replace('\n', newline)
source = source.replace(anchor, inject + anchor, 1)
ast.parse(source)

# No authorization provider is wired here. The existing queue and handler
# denial controls are intentionally left unchanged.
backupdir = ROOT / 'backend/server/data/runtime_backups' / (
    'connect_domain_AK6_STAGE_BINDING_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
backupdir.mkdir(parents=True, exist_ok=False)
backup = backupdir / adapter.name
shutil.copy2(adapter, backup)
if backup.read_bytes() != original:
    raise SystemExit('STOP: Backup integrity failed')

changed = False
try:
    if adapter.read_bytes() != original:
        raise RuntimeError('STOP: Concurrent adapter edit detected')
    fd, tmpname = tempfile.mkstemp(prefix='.ak6_', suffix='.tmp', dir=adapter.parent)
    os.close(fd)
    tmp = Path(tmpname)
    try:
        tmp.write_bytes(source.encode('utf-8'))
        os.replace(tmp, adapter)
        changed = True
    finally:
        tmp.unlink(missing_ok=True)
    import importlib
    from backend.server.runtime import universal_runtime_worker_scope_contract as canonical
    from backend.server.runtime.security import connected_domain_job_permission as permission
    from backend.server.runtime import runtime_feature_flag_gateway as flags
    importlib.reload(permission)
    assert len(canonical.EXPECTED_SCOPE) == 6
    assert flags.runtime_queue_claims_enabled(worker_id='universal_runtime_worker_v1') is False
    for stage, job_id, _, _ in canonical.STAGES:
        try:
            permission.require_connected_domain_job_execution_permission(
                job_id=job_id,
                workspace_id=canonical.WORKSPACE_ID,
                worker_id='universal_runtime_worker_v1',
                handler_key='deliberately_wrong_stage',
                evidence=None,
            )
        except PermissionError as exc:
            assert 'AK_DENY_STAGE_HANDLER_MISMATCH' in str(exc), str(exc)
        else:
            raise AssertionError('wrong stage accepted: ' + stage)
        try:
            permission.require_connected_domain_job_execution_permission(
                job_id=job_id,
                workspace_id=canonical.WORKSPACE_ID,
                worker_id='universal_runtime_worker_v1',
                handler_key=stage,
                evidence=None,
            )
        except PermissionError as exc:
            assert 'AK_DENY_MISSING_EVIDENCE' in str(exc), str(exc)
        else:
            raise AssertionError('missing evidence accepted: ' + stage)
    for p in WATCH:
        if sha(p) != before[str(p)]:
            raise AssertionError('STOP: Protected source changed: ' + str(p))
    print('PASS: 6/6 wrong-stage handler bindings denied')
    print('PASS: 6/6 correct-stage calls still denied without authority')
    print('PASS: Queue/handlers/registration/scope source unchanged')
    print('PASS: Production queue claim flag disabled')
    print('SOURCE BACKUP:', backup)
    print('AK.6 STAGE BINDING: INSTALLED (12/12 tests)')
    print('AK.6 AUTHENTICATED PROVIDER: BLOCKED — not supplied by reviewed files')
    print('AK.7 INTEGRATED AUTHORIZATION CERTIFICATION: NOT COMPLETE')
    print('PRODUCTION ACTIVATION: NOT AUTHORIZED')
except BaseException:
    if changed:
        shutil.copy2(backup, adapter)
        print('ROLLBACK: original permission adapter restored')
    raise
