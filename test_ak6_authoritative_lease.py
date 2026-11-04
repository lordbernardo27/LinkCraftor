"""Isolated AK.6 persisted claim/lease checks. No production files, queues or jobs."""
from __future__ import annotations
import ast
import copy
import importlib.util
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

src = Path(__file__).with_name('ak6_authoritative_lease.py')
ast.parse(src.read_text(encoding='utf-8'))
spec = importlib.util.spec_from_file_location('ak6_lease_isolated', src)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
now = datetime(2026, 11, 4, 12, 0, tzinfo=timezone.utc)
worker = 'universal_runtime_worker_v1'
base_meta = {
    'claimed_by_dequeue':True, 'worker_id':worker,
    'assigned_worker_id':worker, 'assigned_worker_instance_id':'instance-1',
    'lease_owner':worker, 'lease_id':'lease-id-1',
    'lease_started_at':(now-timedelta(seconds=10)).isoformat(),
    'lease_expires_at':(now+timedelta(seconds=300)).isoformat(),
    'lease_active':True, 'lease_released':False,
}
job = {'job_id':'uj_test', 'workspace_id':'ws_test', 'job_type':'connect_domain_stage',
       'status':'running','metadata':base_meta}

def loader(jid):
    return SimpleNamespace(job_id=job['job_id'], workspace_id=job['workspace_id'],
                           job_type=job['job_type'], status=job['status'],
                           metadata=copy.deepcopy(base_meta))

def check(candidate=None, store=None, wid=worker, current=now):
    return module.require_persisted_ak6_lease(job=candidate if candidate is not None else job,
        worker_id=wid, job_loader=store if store is not None else loader, now=current)

n=0
def passed(fn):
    global n
    assert fn() == 'lease-id-1'
    n+=1

def denied(fn):
    global n
    try:fn()
    except PermissionError: n+=1
    else:raise AssertionError('FAIL: prohibited execution accepted')

passed(lambda:check())
denied(lambda:check(store=lambda jid:None))
denied(lambda:check(store=lambda jid: (_ for _ in ()).throw(OSError('down'))))
denied(lambda:check(store=lambda jid: SimpleNamespace(**{**vars(loader(jid)), 'status':'queued'})))
denied(lambda:check(store=lambda jid: SimpleNamespace(**{**vars(loader(jid)), 'workspace_id':'other'})))
denied(lambda:check(store=lambda jid: SimpleNamespace(**{**vars(loader(jid)), 'job_type':'other'})))
denied(lambda:check(candidate={**job,'status':'completed'}))
denied(lambda:check(candidate={**job,'metadata':{**base_meta,'lease_id':'forged'}}))
denied(lambda:check(candidate={**job,'metadata':{**base_meta,'worker_id':'forged'}}))
denied(lambda:check(wid='forged'))
denied(lambda:check(current=now+timedelta(hours=1)))
denied(lambda:check(current=now-timedelta(hours=1)))
denied(lambda:check(store=lambda jid: SimpleNamespace(**{**vars(loader(jid)), 'metadata':{**base_meta,'lease_active':False}})))
denied(lambda:check(store=lambda jid: SimpleNamespace(**{**vars(loader(jid)), 'metadata':{**base_meta,'lease_released':True}})))
denied(lambda:check(store=lambda jid: SimpleNamespace(**{**vars(loader(jid)), 'metadata':{**base_meta,'assigned_worker_instance_id':''}})))
denied(lambda:check(store=lambda jid: SimpleNamespace(**{**vars(loader(jid)), 'metadata':{**base_meta,'lease_expires_at':'not-time'}})))
denied(lambda:check(candidate={**job,'metadata':{**base_meta,'lease_started_at':'forged'}}))
denied(lambda:check(candidate={**job,'job_id':'fake'}))
print(f'PASS: {n}/{n} isolated authoritative persisted-lease checks')
print('LIVE JOBS / QUEUE: NOT ACCESSED')
