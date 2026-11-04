"""Single fail-closed installation of AK.6 four-control enforcement.

Requires previous stage binding, signed grant and persisted lease integrations.
Backups are created before any production source update; no worker is enabled.
Issuer provisioning is a separate privileged operator action (not automatic).
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
VERIFIER = ROOT / 'backend/server/runtime/security/ak6_signed_execution_grants.py'
OPERATIONAL = ROOT / 'backend/server/runtime/security/ak6_operational_trust.py'
HANDLERS = ROOT / 'backend/server/runtime/universal_runtime_registration.py'
LEASE = ROOT / 'backend/server/runtime/security/ak6_authoritative_lease.py'
QUEUE = ROOT / 'backend/server/orchestration/queue.py'
FLAGS = ROOT / 'backend/server/runtime/runtime_feature_flag_gateway.py'
SOURCE = HERE / 'ak6_operational_trust.py'
TESTS = HERE / 'test_ak6_four_controls.py'
for f in (VERIFIER,HANDLERS,LEASE,QUEUE,FLAGS,SOURCE,TESTS):
    if not f.is_file():
        raise SystemExit(f'STOP: missing required file: {f}')

watch = (QUEUE, FLAGS, LEASE)
watch_hashes = {str(f): hashlib.sha256(f.read_bytes()).hexdigest() for f in watch}
v_bytes = VERIFIER.read_bytes()
h_bytes = HANDLERS.read_bytes()
v = v_bytes.decode('utf-8-sig').replace('\r\n','\n')
h = h_bytes.decode('utf-8-sig').replace('\r\n','\n')
marker = 'AK6_FOUR_CONTROLS_OPERATIONAL_BOUNDARY'
if marker in v or marker in h:
    if marker in v and marker in h and OPERATIONAL.read_bytes() == SOURCE.read_bytes():
        print('ALREADY INSTALLED: AK.6 four-control enforcement; no changes')
        raise SystemExit(0)
    raise SystemExit('STOP: partial AK.6 four-control integration')
if OPERATIONAL.exists():
    raise SystemExit('STOP: operational trust module already exists')
if ('AK6_AUTHORITATIVE_PERSISTED_LEASE_ENFORCED' not in v
    or 'AK6_SIGNED_EXECUTION_AUTHORITY_INTEGRATED' not in h
    or 'AK6_SIGNED_EXECUTION_AUTHORITY_INTEGRATED' not in QUEUE.read_text(encoding='utf-8-sig')):
    raise SystemExit('STOP: prerequisite signed/lease integrations are absent')
if not ('AK_REGISTERED_HANDLER_EXECUTION_GUARD' in h and
        'AK_CANONICAL_CONNECTED_DOMAIN_AUTHORIZATION_GUARD' in QUEUE.read_text(encoding='utf-8-sig')):
    raise SystemExit('STOP: original guards absent')

# The signed verifier executes this AFTER Ed25519 validation and AFTER the
# authoritative persisted-lease check. It is the single shared integration
# boundary for atomic claim and both handler entry points.
def replace_one(text, old, new, label):
    if text.count(old) != 1:
        raise SystemExit('STOP: exact source anchor mismatch: '+label)
    return text.replace(old,new,1)

v = replace_one(v,
    'def require_signed_ak6_execution_authority(*, job, worker_id: str, action: str) -> str:',
    'def require_signed_ak6_execution_authority(*, job, worker_id: str, action: str, phase: str = "claim") -> str:',
    'signed-verifier-signature')
v = replace_one(v,
    '    return payload["nonce"]',
    '''    # AK6_FOUR_CONTROLS_OPERATIONAL_BOUNDARY
    # Attested worker SID, protected pinned issuer, durable replay/revocation.
    from backend.server.runtime.security.ak6_operational_trust import (
        require_operational_ak6_trust,
    )
    return require_operational_ak6_trust(
        job=job, worker_id=worker_id, action=action, phase=phase,
        payload=payload, public_key_bytes=raw_public, nonce=payload["nonce"],
    )''', 'signed-verifier-return')
h = replace_one(h,
    'def _ak_require_connected_domain_execution_authority(job):',
    'def _ak_require_connected_domain_execution_authority(job, *, phase="dispatch"):',
    'handler-guard-signature')
h = replace_one(h,
    '                job=job, worker_id=WORKER_ID, action="execute",',
    '                job=job, worker_id=WORKER_ID, action="execute", phase=phase,',
    'handler-verifier-call')
# AST-anchored change ONLY in execute_registered_runtime_job_v1 body, not dispatch.
tree = ast.parse(h)
fn = next((n for n in tree.body if isinstance(n, ast.FunctionDef)
           and n.name == 'execute_registered_runtime_job_v1'), None)
if fn is None or not fn.body:
    raise SystemExit('STOP: execute entrypoint missing')
lines = h.splitlines(keepends=True)
start = fn.body[0].lineno - 1
if '_ak_require_connected_domain_execution_authority(job)' not in lines[start]:
    # Might be a comment just before the first executable statement; seek within function.
    matches = [i for i in range(fn.lineno, min(fn.lineno+8,len(lines)))
               if '_ak_require_connected_domain_execution_authority(job)' in lines[i]]
    if len(matches) != 1:
        raise SystemExit('STOP: cannot resolve exact execute-guard call')
    start = matches[0]
if lines[start].count('_ak_require_connected_domain_execution_authority(job)') != 1:
    raise SystemExit('STOP: execute guard altered')
lines[start] = lines[start].replace('_ak_require_connected_domain_execution_authority(job)',
                                   '_ak_require_connected_domain_execution_authority(job, phase="pre_execute")  # AK6_FOUR_CONTROLS_OPERATIONAL_BOUNDARY',1)
h = ''.join(lines)
for f, text in ((VERIFIER, v), (HANDLERS, h), (SOURCE, SOURCE.read_text(encoding='utf-8'))):
    ast.parse(text, filename=str(f))
h_tree = ast.parse(h)
for name, expected in [('dispatch_registered_runtime_handler', None),
                       ('execute_registered_runtime_job_v1', 'pre_execute')]:
    fn = next((x for x in h_tree.body if isinstance(x, ast.FunctionDef) and x.name == name),None)
    if not fn:
        raise SystemExit('STOP: missing protected handler '+name)
    body = fn.body
    call = body[0] if not (isinstance(body[0], ast.Expr) and isinstance(body[0].value,ast.Constant)
                          and isinstance(body[0].value.value,str)) else body[1]
    if not isinstance(call,ast.Expr) or not isinstance(call.value,ast.Call) or getattr(call.value.func,'id',None) != '_ak_require_connected_domain_execution_authority':
        raise SystemExit('STOP: handler guard not first statement '+name)
    kw = next((k.value.value for k in call.value.keywords if k.arg=='phase' and isinstance(k.value,ast.Constant)), None)
    if kw != expected:
        raise SystemExit('STOP: unexpected guard phase '+name)

r = subprocess.run([sys.executable,'-B',str(TESTS)], capture_output=True,text=True,timeout=45)
if r.returncode != 0:
    raise SystemExit('STOP: isolated four-control tests failed:\n'+r.stdout+'\n'+r.stderr)
print(r.stdout.rstrip())

def preserve(text,was):
    return (text.replace('\n','\r\n') if b'\r\n' in was else text).encode('utf-8')

backup = ROOT/'backend/server/data/runtime_backups'/('connect_domain_AK6_FOUR_CONTROLS_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
backup.mkdir(parents=True,exist_ok=False)
for p in (VERIFIER,HANDLERS):
    shutil.copy2(p, backup/p.name)
    if (backup/p.name).read_bytes()!=p.read_bytes():
        raise SystemExit('STOP: backup verification failed')
changed=[]
try:
    for p,prior,data in ((OPERATIONAL,None,SOURCE.read_bytes()),
                         (VERIFIER,v_bytes,preserve(v,v_bytes)),
                         (HANDLERS,h_bytes,preserve(h,h_bytes))):
        if (prior is None and p.exists()) or (prior is not None and p.read_bytes()!=prior):
            raise RuntimeError('STOP: concurrent edit: '+str(p))
        fd,name=tempfile.mkstemp(prefix='.ak6_four_',suffix='.tmp',dir=p.parent)
        os.close(fd)
        tmp=Path(name)
        try:
            tmp.write_bytes(data)
            ast.parse(tmp.read_text(encoding='utf-8-sig'))
            os.replace(tmp,p)
            changed.append(p)
        finally:
            tmp.unlink(missing_ok=True)
    for p in watch:
        if hashlib.sha256(p.read_bytes()).hexdigest()!=watch_hashes[str(p)]:
            raise RuntimeError('STOP: protected queue/flag/lease source changed')
    print('PASS: independent Windows worker token verification is installed')
    print('PASS: protected machine-pinned issuer key check is installed')
    print('PASS: atomic durable nonce reserve / execute / dispatch / revoke is installed')
    print('PASS: original handler/queue structure and feature flags retained')
    print('BACKUP:',backup)
    print('AK.6 FOUR-CONTROL VERIFIERS: INSTALLED INACTIVE')
    print('EXTERNAL ISSUER & PROTECTED MACHINE PROVISIONING: NOT PERFORMED')
    print('AK.7 PRODUCTION CERTIFICATION: PENDING')
    print('PRODUCTION ACTIVATION: NO-GO')
except BaseException:
    for p in reversed(changed):
        if p==OPERATIONAL: p.unlink(missing_ok=True)
        else: shutil.copy2(backup/p.name,p)
    print('ROLLBACK: AK.6 original integration restored')
    raise
