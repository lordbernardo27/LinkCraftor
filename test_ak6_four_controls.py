"""Isolated AK.6 four-control suite. Uses synthetic identities and temporary ledger.
Never reads production files or creates production signing credentials.
"""
from __future__ import annotations
import base64
import importlib.util
import sqlite3
from contextlib import closing
import tempfile
import time
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('ak6_operational_trust_test',HERE/'ak6_operational_trust.py')
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
passes=0

def ok(condition,label):
    global passes
    assert condition,label
    passes+=1

def rejects(fn, code):
    try:
        fn()
    except PermissionError as exc:
        ok(code in str(exc),str(exc))
    else:
        raise AssertionError('unexpectedly allowed '+code)

with tempfile.TemporaryDirectory() as td:
    root=Path(td)
    public=bytes(range(32))
    (root/m._ISSUER_KEY).write_text(base64.b64encode(public).decode('ascii'))
    (root/m._WORKER_SID).write_text('S-1-5-80-123456')
    sid='S-1-5-80-123456'
    ok(m._trusted_context(public_key_bytes=public,trust_dir=root,worker_sid_provider=lambda:sid)==sid,'real sid supplied in test')
    rejects(lambda:m._trusted_context(public_key_bytes=bytes(32),trust_dir=root,worker_sid_provider=lambda:sid),'AK6_DENY_UNTRUSTED_ISSUER_KEY')
    rejects(lambda:m._trusted_context(public_key_bytes=public,trust_dir=root,worker_sid_provider=lambda:'S-1-5-80-999'),'AK6_DENY_UNAUTHENTICATED_WORKER')
    rejects(lambda:m._trusted_context(public_key_bytes=public,trust_dir=root,worker_sid_provider=lambda:''),'AK6_DENY_UNAUTHENTICATED_WORKER')
    (root/m._WORKER_SID).unlink()
    rejects(lambda:m._trusted_context(public_key_bytes=public,trust_dir=root,worker_sid_provider=lambda:sid),'AK6_DENY_AUTHORITY_NOT_PROVISIONED')
    (root/m._WORKER_SID).write_text(sid)
    (root/m._ISSUER_KEY).write_text('invalid!')
    rejects(lambda:m._trusted_context(public_key_bytes=public,trust_dir=root,worker_sid_provider=lambda:sid),'AK6_DENY_AUTHORITY_NOT_PROVISIONED')
    (root/m._ISSUER_KEY).write_text(base64.b64encode(public).decode('ascii'))
    db=root/'ledger.db'
    nonce='N'*40
    exp=int(time.time())+400
    def step(phase,*,n=nonce,job='job1',worker=sid,expires=exp,lease='lease1',database=db):
        return m._ledger_step(ledger=database,nonce=n,job_id=job,
                              worker_sid=worker,phase=phase,
                              expires_at=expires,lease_id=lease)
    step('claim')
    ok(db.exists(),'durable sqlite created')
    rejects(lambda:step('claim'),'AK6_DENY_NONCE_REPLAY')
    rejects(lambda:step('pre_execute',job='job2'),'AK6_DENY_REPLAY_REVOKED_OR_MISMATCH')
    rejects(lambda:step('pre_execute',worker='S-1-5-80-2'),'AK6_DENY_REPLAY_REVOKED_OR_MISMATCH')
    rejects(lambda:step('pre_execute',expires=exp+1),'AK6_DENY_REPLAY_REVOKED_OR_MISMATCH')
    rejects(lambda:step('dispatch'),'AK6_DENY_LEASE_NOT_BOUND')
    step('pre_execute')
    ok(True,'pre_execute allowed reserved grant')
    rejects(lambda:step('pre_execute',lease='other'),'AK6_DENY_LEASE_MISMATCH')
    step('dispatch')
    ok(True,'dispatch consumed grant')
    rejects(lambda:step('pre_execute'),'AK6_DENY_REPLAY_REVOKED_OR_MISMATCH')
    rejects(lambda:step('dispatch'),'AK6_DENY_REPLAY_REVOKED_OR_MISMATCH')
    rejects(lambda:step('claim'),'AK6_DENY_NONCE_REPLAY')
    rejects(lambda:step('claim',n='B'*40,expires=int(time.time())-1),'AK6_DENY_LEDGER_EXPIRED')
    rejects(lambda:step('claim',n='bad'),'AK6_DENY_NONCE')
    rejects(lambda:step('unknown',n='C'*40),'AK6_DENY_PHASE')
    other='D'*40
    step('claim',n=other)
    with closing(sqlite3.connect(db)) as cx, cx:
        cx.execute('UPDATE grant_ledger SET revoked=1 WHERE nonce=?',(other,))
    rejects(lambda:step('pre_execute',n=other),'AK6_DENY_REPLAY_REVOKED_OR_MISMATCH')
    rejects(lambda:step('claim',n=other),'AK6_DENY_NONCE_REPLAY')
    rejects(lambda:step('pre_execute',n='E'*40),'AK6_DENY_UNRESERVED_GRANT')
    rejects(lambda:step('claim',n='F'*40,database=root/'nonexistent'/'db.sqlite3'),'AK6_DENY_LEDGER_UNAVAILABLE')
    other2='G'*40
    step('claim',n=other2)
    with closing(sqlite3.connect(db)) as cx, cx:
        cx.execute('UPDATE grant_ledger SET state=? WHERE nonce=?',('consumed',other2))
    rejects(lambda:step('pre_execute',n=other2),'AK6_DENY_REPLAY_REVOKED_OR_MISMATCH')
    other3='H'*40
    step('claim',n=other3)
    step('pre_execute',n=other3,lease='lease99')
    rejects(lambda:step('dispatch',n=other3,lease='lease100'),'AK6_DENY_LEASE_MISMATCH')
    step('dispatch',n=other3,lease='lease99')
    ok(True,'matching lease dispatch completed')

print(f'PASS: {passes}/{passes} isolated authority, identity, durable nonce and revocation checks')
print('PRODUCTION TRUST ROOT / ISSUER: NOT ACCESSED')
print('LIVE JOBS / QUEUE: NOT ACCESSED')
