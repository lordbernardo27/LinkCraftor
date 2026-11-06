"""AK.7 POSITIVE EXECUTION BRIDGE (isolated source-function harness).
Runs ACTUAL installed queue/handler FUNCTION BODIES with disposable in-memory
records and explicit test doubles for grants, registration and job persistence.
No production modules imported, no production storage read, no worker started.
NOT production issuer, true worker service, six real stage handlers or full E2E.
"""
from __future__ import annotations
import ast
import contextlib
import hashlib
import json
import sys
import threading
import types
from collections.abc import Mapping
from datetime import datetime,timezone
from pathlib import Path
from unittest.mock import patch

ROOT=Path.cwd().resolve()
if ROOT.name.lower()!='linkcraftor': raise SystemExit('STOP: run at LinkCraftor root')
Q=ROOT/'backend/server/orchestration/queue.py'
H=ROOT/'backend/server/runtime/universal_runtime_registration.py'
S=ROOT/'backend/server/runtime/universal_runtime_worker_scope_contract.py'
F=ROOT/'backend/server/runtime/runtime_feature_flag_gateway.py'
files=(Q,H,S,F)
if not all(p.is_file() for p in files): raise SystemExit('STOP: required source missing')
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
def readtree(p):return ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
def extract(p,names):
    nodes=[n for n in readtree(p).body if isinstance(n,ast.FunctionDef) and n.name in names]
    if {n.name for n in nodes}!=set(names):raise RuntimeError('Source layout changed: '+str(names))
    mod=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)]+nodes,type_ignores=[])
    ast.fix_missing_locations(mod)
    return compile(mod,str(p),'exec')
assigns={}
for n in readtree(S).body:
    if isinstance(n,ast.Assign):
        for t in n.targets:
            if isinstance(t,ast.Name) and t.id in {'STAGES','WORKSPACE_ID','WORKFLOW_ID','LEGACY_IDS'}:
                v=n.value.args[0] if t.id=='LEGACY_IDS' and isinstance(n.value,ast.Call) else n.value
                assigns[t.id]=ast.literal_eval(v)
stages=assigns['STAGES'];ids=[x[1] for x in stages]
if len(ids)!=6 or len(set(ids))!=6 or len({x[0] for x in stages})!=6:raise RuntimeError('Unexpected six-stage scope')
if any(i in assigns['LEGACY_IDS'] for i in ids):raise RuntimeError('Scope includes legacy')
checks=[]
def check(name,condition,detail=''):
    ok=bool(condition);checks.append({'name':name,'passed':ok,'detail':str(detail)})
    print(('PASS' if ok else 'FAIL')+': '+name+((' - '+str(detail)) if detail else ''))

# Guard shape checks: positive path must reach signed hooks before any write.
qtree=readtree(Q);htree=readtree(H)
qfn=next(n for n in qtree.body if isinstance(n,ast.FunctionDef) and n.name=='dequeue_job')
hfns={n.name:n for n in htree.body if isinstance(n,ast.FunctionDef) and n.name in {'_ak_require_connected_domain_execution_authority','dispatch_registered_runtime_handler','execute_registered_runtime_job_v1'}}
check('signed_hooks_present',all('AK6_SIGNED_EXECUTION_AUTHORITY_INTEGRATED' in p.read_text(encoding='utf-8-sig') for p in (Q,H)))
check('four_controls_present','AK6_FOUR_CONTROLS_OPERATIONAL_BOUNDARY' in H.read_text(encoding='utf-8-sig'))
check('six_stage_scope',len(stages)==6)
check('handlers_guard_first',all(isinstance(hfns[k].body[0],ast.Expr) and isinstance(hfns[k].body[0].value,ast.Call) and isinstance(hfns[k].body[0].value.func,ast.Name) and hfns[k].body[0].value.func.id=='_ak_require_connected_domain_execution_authority' for k in ('dispatch_registered_runtime_handler','execute_registered_runtime_job_v1')))
if not all(c['passed'] for c in checks):raise SystemExit('STOP: expected production guards missing')

# Test-only in-memory registered modules. Not inserted in real package globals.
mods=('backend','backend.server','backend.server.runtime','backend.server.runtime.runtime_feature_flag_gateway',
      'backend.server.runtime.universal_runtime_worker_scope_contract',
      'backend.server.runtime.security','backend.server.runtime.security.ak6_signed_execution_grants',
      'backend.server.orchestration','backend.server.orchestration.job_store',
      'backend.server.runtime.runtime_registration_execution_policy',
      'backend.server.runtime.universal_runtime_registration',
      'backend.server.runtime.runtime_registration_dependency_policy',
      'backend.server.jobs','backend.server.jobs.universal_knowledge_orchestrator')
fakes={name:types.ModuleType(name) for name in mods}
for name in mods:
    if '.' in name and name.rsplit('.',1)[0] in fakes:
        setattr(fakes[name.rsplit('.',1)[0]],name.rsplit('.',1)[-1],fakes[name])
fakes['backend.server.runtime.runtime_feature_flag_gateway'].runtime_queue_claims_enabled=lambda worker_id:worker_id=='universal_runtime_worker_v1'
fakes['backend.server.runtime.universal_runtime_worker_scope_contract'].EXPECTED_SCOPE=frozenset(ids)

class Job:
    def __init__(self,stage,jid):
        self.job_type=stage;self.job_id=jid;self.workspace_id=assigns['WORKSPACE_ID'];self.status='queued';self.payload={};self.metadata={'stage_reference':{'handler_ref':next(x[2] for x in stages if x[1]==jid),'registration_fingerprint':next(x[3] for x in stages if x[1]==jid)},'coordination':{'workflow_id':assigns['WORKFLOW_ID'],'workflow_type':'connect_domain'}}

jobs={j:Job(s,j) for s,j,*_ in stages}
claims=[]; handler_calls=[]; status_calls=[];progress_calls=[];verifications=[]
def verifier(*,job,worker_id,action,phase='claim'):
    """Explicit TEST DOUBLE, NOT actual signing authority or operational attestation."""
    j=job if isinstance(job,Mapping) else job.__dict__
    jid=j.get('job_id');stage=next((v[0] for v in stages if v[1]==jid),None)
    if worker_id!='universal_runtime_worker_v1' or action not in ('claim','execute') or jid not in jobs or j.get('workspace_id')!=assigns['WORKSPACE_ID'] or (j.get('job_type') or j.get('stage'))!=stage:
        raise PermissionError('ISOLATED_TEST_DENY_IDENTITY')
    if action=='claim' and j.get('status')!='queued':raise PermissionError('ISOLATED_TEST_DENY_STATE')
    if action=='execute':
        m=j.get('metadata') or {}
        if j.get('status')!='running' or not m.get('claimed_by_dequeue') or not m.get('lease_id') or m.get('assigned_worker_id')!=worker_id:raise PermissionError('ISOLATED_TEST_DENY_LEASE')
    verifications.append((jid,action,phase))
    return 'test-only-authorization'
fakes['backend.server.runtime.security.ak6_signed_execution_grants'].require_signed_ak6_execution_authority=verifier
fakes['backend.server.runtime.security.ak6_signed_execution_grants'].WORKER_ID='universal_runtime_worker_v1'

@contextlib.contextmanager
def lock():yield

def queued():return tuple(v for v in jobs.values() if v.status=='queued')
def transition(jid,status,metadata=None,**kwargs):
    j=jobs[jid];j.status=status;j.metadata.update(metadata or {});claims.append((jid,status));return j

def lease(*,job_id,registration,lease_seconds):
    return {'lease_id':'ISOLATED_LEASE_'+job_id,'lease_owner':'universal_runtime_worker_v1','assigned_worker_id':'universal_runtime_worker_v1','lease_started_at':'2026-11-05T00:00:00+00:00','lease_expires_at':'2099-01-01T00:00:00+00:00'}
class Action:
    DEFER='DEFER';REUSE_EXISTING='REUSE';CLAIM='CLAIM'
class Decision:
    action=Action.CLAIM
    def to_metadata(self):return {}
class DepAction:
    DEFER='DEFER';RUN='RUN'
class DepDecision:
    action=DepAction.RUN
    def to_metadata(self):return {}
fakes['backend.server.orchestration.job_store'].load_jobs=lambda:jobs
fakes['backend.server.runtime.runtime_registration_execution_policy'].RuntimeRegistrationQueueAction=Action
fakes['backend.server.runtime.runtime_registration_execution_policy'].evaluate_runtime_registration_queue_candidate=lambda **kwargs:Decision()
fakes['backend.server.runtime.runtime_registration_dependency_policy'].RuntimeRegistrationDependencyAction=DepAction
fakes['backend.server.runtime.runtime_registration_dependency_policy'].evaluate_runtime_registration_stage_dependencies=lambda **kwargs:DepDecision()
fakes['backend.server.runtime.universal_runtime_registration'].get_runtime_registration=lambda job_type:object()

qn={'__name__':'isolated_ak7_queue','_dequeue_lock':lock,'_queued_jobs':queued,
    'recover_interrupted_runtime_jobs':lambda:(_ for _ in ()).throw(AssertionError('production recovery reached')),
    'update_job_status':transition,'prepare_universal_runtime_job_lease':lease,
    'JOB_STATUS_RUNNING':'running','Mapping':Mapping,'Any':object,'Optional':__import__('typing').Optional,'OrchestrationJob':Job,'Dict':dict}
exec(extract(Q,{'dequeue_job'}),qn)

class Reg:
    def __init__(self,stage):self.pipeline='connect_domain';self.stage=stage;self.handler_ref=next(x[2] for x in stages if x[0]==stage);self.handler=lambda job, stage=stage: {'test_stage':stage,'test_only':True}
regs={s:Reg(s) for s,_,*__ in stages}
@contextlib.contextmanager
def handler_lock():yield

def guarded_invoke(handler,job):
    handler_calls.append(job['job_id']);return handler(job)
def update_status(*,workspace_id,job_id,status,**kwargs):status_calls.append((job_id,status))
def update_progress(*,workspace_id,job_id,percent,**kwargs):progress_calls.append((job_id,percent))
def failure(**kw):raise AssertionError('handler failed: '+repr(kw))
fakes['backend.server.jobs.universal_knowledge_orchestrator'].update_job_status=update_status
fakes['backend.server.jobs.universal_knowledge_orchestrator'].update_job_progress=update_progress
fakes['backend.server.jobs.universal_knowledge_orchestrator'].record_job_failure=failure
hn={'__name__':'isolated_ak7_handlers','Mapping':Mapping,'Any':object,'_REGISTRY_LOCK':threading.RLock(),
    '_RUNTIME_HANDLER_REGISTRY':regs,'ensure_persisted_runtime_registrations_loaded':lambda:None,
    '_validate_required_payload_fields':lambda **kw:None,'_invoke_handler':guarded_invoke}
exec(extract(H,set(hfns)),hn)
hn['dispatch_registered_runtime_handler']=hn['dispatch_registered_runtime_handler']

# All six stages: actual queue claim source -> actual execute wrapper source -> actual dispatch source.
with patch.dict(sys.modules,fakes):
    for stage,jid,*_ in stages:
        j=qn['dequeue_job'](worker_id='universal_runtime_worker_v1',allowed_job_ids=frozenset(ids),worker_registration={'test_only':True})
        check('claim_'+stage,j is not None and j.job_id==jid and j.status=='running' and j.metadata.get('lease_id')=='ISOLATED_LEASE_'+jid)
        if j is None:continue
        # Real worker transforms orchestration dataclass into mapping via a separate function;
        # here the in-memory mapping is built explicitly. This is NOT full worker execution.
        job=dict(j.__dict__)
        hn['dispatch_registered_runtime_handler'].__globals__['dispatch_registered_runtime_handler']=hn['dispatch_registered_runtime_handler']
        result=hn['execute_registered_runtime_job_v1'](job)
        check('execute_'+stage,result.get('ok') is True and result.get('result',{}).get('handler_result',{}).get('test_stage')==stage)
        check('handler_once_'+stage,handler_calls.count(jid)==1)
        check('status_progress_'+stage,[(x[1]) for x in status_calls if x[0]==jid]==['running','completed'] and [x[1] for x in progress_calls if x[0]==jid]==[10,100])
        check('authorize_claim_and_both_handlers_'+stage,[x[1:] for x in verifications if x[0]==jid]==[('claim','claim'),('execute','pre_execute'),('execute','dispatch')])
    check('all_six_claims_once',len([x for x in claims if x[1]=='running'])==6)
    check('queue_empty_after_six',qn['dequeue_job'](worker_id='universal_runtime_worker_v1',allowed_job_ids=frozenset(ids)) is None)
    check('legacy_noninterference',all(jid not in assigns['LEGACY_IDS'] for jid,_, in claims))

for p in files:check('source_unchanged_'+p.name,hashlib.sha256(p.read_bytes()).hexdigest()==before[str(p)])
errors=[x for x in checks if not x['passed']]
report={'schema':'ak7_isolated_positive_bridge_v1','generated_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'passed':len(checks)-len(errors),'total':len(checks),
        'source_function_bodies_executed':True,'full_worker_runner_executed':False,'real_stage_handlers_executed':False,'test_authorizer':'explicitly mocked (not signed / not production)',
        'real_crypto_and_lease':'covered by separately installed test suites, not this positive harness',
        'live_job_store_accessed':False,'production_worker_started':False,'production_authorized_execution_certified':False,'production_activation':'NO-GO'}
out=ROOT/'AK7_ISOLATED_POSITIVE_BRIDGE.json';out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('\nREPORT:',out,'\nCHECKS:',len(checks)-len(errors),'/',len(checks),'\nPRODUCTION ACTIVATION: NO-GO')
if errors:sys.exit(1)
