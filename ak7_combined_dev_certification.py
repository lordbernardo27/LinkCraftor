"""LinkCraftor AK.7 - isolated, read-only integrated development certification.

Run from LinkCraftor repository root. Does not access production jobs or provision trust.
Tests existing auth suites plus real SQLite nonce lifecycle across fresh Python processes.
"""
from __future__ import annotations
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime, timezone

ROOT = Path.cwd().resolve()
if ROOT.name.lower() != 'linkcraftor':
    raise SystemExit('STOP: run from LinkCraftor repository root')

CHECKS = []
def record(name, ok, detail=''):
    CHECKS.append(dict(name=name, status='PASS' if ok else 'BLOCKED', detail=str(detail)))
    print(('PASS: ' if ok else 'BLOCK: ') + name + (' - '+str(detail) if detail else ''), flush=True)

protected = {
    'queue': 'backend/server/orchestration/queue.py',
    'handler': 'backend/server/runtime/universal_runtime_registration.py',
    'scope': 'backend/server/runtime/universal_runtime_worker_scope_contract.py',
    'service': 'backend/server/runtime/universal_runtime_worker_service.py',
    'registration': 'backend/server/runtime/universal_runtime_worker_service_registration.py',
    'feature_flags': 'backend/server/runtime/runtime_feature_flag_gateway.py',
    'signed': 'backend/server/runtime/security/ak6_signed_execution_grants.py',
    'operational': 'backend/server/runtime/security/ak6_operational_trust.py',
    'lease': 'backend/server/runtime/security/ak6_authoritative_lease.py',
}
files = {k: ROOT / p for k,p in protected.items()}
original_hashes = {k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in files.items() if p.is_file()}
for key,path in files.items():
    record('source_present_'+key, path.is_file(), protected[key])
    if path.is_file():
        try: ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
        except SyntaxError as e: record('syntax_'+key, False, str(e))
        else: record('syntax_'+key, True)

def get_function(tree, name):
    return next((n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name),None)

def get_first_call(fn):
    if fn is None: return None
    statements = [s for s in fn.body if not (isinstance(s,ast.Expr) and isinstance(s.value,ast.Constant) and isinstance(s.value.value,str))]
    if not statements: return None
    statement = statements[0]
    calls = [n for n in ast.walk(statement) if isinstance(n,ast.Call)]
    return [ast.unparse(c.func) for c in calls]

if files['handler'].is_file():
    tree = ast.parse(files['handler'].read_text(encoding='utf-8-sig'))
    for fnname in ('dispatch_registered_runtime_handler','execute_registered_runtime_job_v1'):
        calls = get_first_call(get_function(tree,fnname))
        record('handler_guard_first_'+fnname, bool(calls and any('_ak_require_connected_domain_execution_authority' in c for c in calls)), calls)
if files['queue'].is_file():
    src = files['queue'].read_text(encoding='utf-8-sig')
    record('atomic_queue_guard_present', 'AK_CANONICAL_CONNECTED_DOMAIN_AUTHORIZATION_GUARD' in src)
    record('signed_queue_guard_present','AK6_SIGNED_EXECUTION_AUTHORITY_INTEGRATED' in src)
if files['operational'].is_file():
    src = files['operational'].read_text(encoding='utf-8-sig')
    record('operational_guard_present', 'def require_operational_ak6_trust' in src)

# All isolated suites are rerun in separate child interpreters, not the worker process.
suites = [
 'test_ak6_signed_grants_isolated.py',
 'test_ak6_authoritative_lease.py',
 'test_ak6_four_controls.py',
]
for suite in suites:
    path=ROOT/suite
    if not path.is_file():
        record('suite_'+suite,False,'missing test file')
        continue
    try:
        run = subprocess.run([sys.executable,str(path)],cwd=ROOT,capture_output=True,text=True,timeout=90,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        out=' '.join((run.stdout+' '+run.stderr).strip().split())
        record('suite_'+suite,run.returncode==0,out[:450])
    except (OSError,subprocess.TimeoutExpired) as exc:
        record('suite_'+suite,False,type(exc).__name__)

# Exercise actual operational ledger across multiple real processes in an isolated temp directory.
# This does not use a live worker, real grant, queue, or production trust root.
if files['operational'].is_file():
    with tempfile.TemporaryDirectory(prefix='ak7_ledger_') as td:
        db = Path(td)/'nonces.db'
        nonce = uuid.uuid4().hex + uuid.uuid4().hex
        expiry = int(time.time()) + 600
        module_path = str(files['operational'])
        runner = r'''
import importlib.util,sys
spec=importlib.util.spec_from_file_location('ak7_isolated_operational',sys.argv[1])
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
try:
 m._ledger_step(ledger=sys.argv[2],nonce=sys.argv[3],job_id='ak7_test_job',worker_sid='S-1-5-21-AK7-ISOLATED',phase=sys.argv[4],expires_at=int(sys.argv[5]),lease_id='ak7_test_lease')
 print('PASS');sys.exit(0)
except PermissionError as e:
 print('DENIED:'+str(e));sys.exit(12)
'''
        def step(phase):
            return subprocess.run([sys.executable,'-c',runner,module_path,str(db),nonce,phase,str(expiry)],capture_output=True,text=True,timeout=15)
        try:
            claim=step('claim')
            record('ledger_claim_process_1',claim.returncode==0,claim.stdout.strip()[:120])
            replay=step('claim')
            record('ledger_replay_rejected_process_2',replay.returncode==12 and 'DENIED:' in replay.stdout,replay.stdout.strip()[:120])
            pre=step('pre_execute')
            record('ledger_preexecute_process_3',pre.returncode==0,pre.stdout.strip()[:120])
            dispatch=step('dispatch')
            record('ledger_dispatch_process_4',dispatch.returncode==0,dispatch.stdout.strip()[:120])
            again=step('dispatch')
            record('ledger_consumed_rejected_process_5',again.returncode==12 and 'DENIED:' in again.stdout,again.stdout.strip()[:120])
        except (OSError,subprocess.TimeoutExpired) as exc:
            record('ledger_multiprocess',False,type(exc).__name__)
        # Revocation of a freshly reserved nonce, with real SQLite update in test store.
        revoked = uuid.uuid4().hex + uuid.uuid4().hex
        try:
            c = sqlite3.connect(str(db))
            try:
                c.execute('INSERT INTO grant_ledger (nonce,job_id,worker_sid,expires_at,state,lease_id,revoked,changed_utc) VALUES (?,?,?,?,?,?,?,?)',
                    (revoked,'ak7_test_job','S-1-5-21-AK7-ISOLATED',expiry,'reserved','ak7_test_lease',1,datetime.now(timezone.utc).isoformat()))
                c.commit()
            finally: c.close()
            check=subprocess.run([sys.executable,'-c',runner,module_path,str(db),revoked,'dispatch',str(expiry)],capture_output=True,text=True,timeout=15)
            record('ledger_revoked_rejected_after_restart',check.returncode==12 and 'DENIED:' in check.stdout,check.stdout.strip()[:120])
        except (OSError,sqlite3.Error,subprocess.TimeoutExpired) as exc:
            record('ledger_revoked_rejected_after_restart',False,type(exc).__name__)

for key,path in files.items():
    if key in original_hashes:
        record('source_unchanged_'+key,hashlib.sha256(path.read_bytes()).hexdigest()==original_hashes[key])

success = all(c['status']=='PASS' for c in CHECKS)
report = {
    'name':'AK7_ISOLATED_DEVELOPMENT_CERTIFICATION',
    'generated_utc':datetime.now(timezone.utc).isoformat(),
    'all_isolated_checks_passed':success,
    'development_isolated_only':True,
    'real_worker_identity_certified':False,
    'external_issuer_provisioned':False,
    'production_execution_authorized':False,
    'production_jobs_executed':False,
    'checks':CHECKS,
}
output=ROOT/'AK7_COMBINED_DEVELOPMENT_CERTIFICATION.json'
output.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('\nREPORT:',output)
print('ISOLATED CHECKS:',sum(c['status']=='PASS' for c in CHECKS),'/',len(CHECKS))
print('PRODUCTION ACTIVATION: NO-GO')
print('SOURCE MODIFICATIONS: NONE (report file only)')
raise SystemExit(0 if success else 1)
