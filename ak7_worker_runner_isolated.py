"""AK.7 isolated test of actual Universal Runtime Worker function body.

No production imports, worker process, queue, database, or stage handler calls.
Only top-level AST definitions from local source are compiled; all dependencies
are injected, in-memory test doubles. No production source modifications.
"""
from __future__ import annotations

import ast
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace, ModuleType
from collections.abc import Mapping
import hashlib
import json
import sys
import traceback

ROOT = Path.cwd().resolve()
SOURCE = ROOT / 'backend/server/runtime/universal_runtime_worker_v1.py'
SCOPE = ROOT / 'backend/server/runtime/universal_runtime_worker_scope_contract.py'
REPORT = ROOT / 'AK7_WORKER_RUNNER_ISOLATED_CERTIFICATION.json'
WORKER = 'universal_runtime_worker_v1'
checks=[]


def record(name, ok, detail=''):
    checks.append({'name': name, 'passed': bool(ok), 'detail': str(detail)})
    print(('PASS' if ok else 'FAIL') + ': ' + name + ((' - ' + str(detail)) if detail else ''))
    if not ok:
        raise AssertionError(name + ' ' + str(detail))


def read_source(p):
    if not p.is_file():
        raise FileNotFoundError('Missing required active source: ' + str(p))
    raw=p.read_bytes()
    return raw.decode('utf-8-sig'), hashlib.sha256(raw).hexdigest()


def literal_assignment(tree, name):
    for n in tree.body:
        if isinstance(n, (ast.Assign, ast.AnnAssign)):
            targets=n.targets if isinstance(n, ast.Assign) else [n.target]
            if any(isinstance(t,ast.Name) and t.id==name for t in targets):
                return (frozenset(ast.literal_eval(n.value.args[0]))
                        if isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name)
                        and n.value.func.id == 'frozenset' and len(n.value.args) == 1
                        else ast.literal_eval(n.value))
    raise RuntimeError('Required static scope missing: ' + name)


def make_body_function(tree, name):
    nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name]
    if len(nodes)!=1: raise RuntimeError('Function not found exactly once: '+name)
    n=nodes[0]
    if not isinstance(n,ast.FunctionDef): raise RuntimeError('Unexpected async runner')
    # Compile authentic function node, with its original defaults and body.
    module=ast.Module(body=[n],type_ignores=[])
    ast.fix_missing_locations(module)
    return compile(module,str(SOURCE),'exec')


def run():
    if ROOT.name != 'LinkCraftor': raise RuntimeError('Run from LinkCraftor repository root')
    worker_text, worker_hash = read_source(SOURCE)
    scope_text, scope_hash = read_source(SCOPE)
    tree=ast.parse(worker_text,filename=str(SOURCE))
    stree=ast.parse(scope_text,filename=str(SCOPE))
    stages=literal_assignment(stree,'STAGES')
    legacy=literal_assignment(stree,'LEGACY_IDS')
    record('exact_six_stage_scope', len(stages)==6 and len({s[1] for s in stages})==6)
    record('legacy_disjoint', set(legacy).isdisjoint({s[1] for s in stages}))
    worker_code=make_body_function(tree,'run_one_universal_runtime_job_v1')
    stage_ids=frozenset(s[1] for s in stages)

    class ContractError(RuntimeError): pass
    class FinalizationError(RuntimeError): pass
    class AdmissionError(RuntimeError): pass
    class CapSnapshot:
        def __init__(self,**kwargs): self.capabilities=tuple(kwargs['capabilities'])
    class Job(SimpleNamespace): pass

    # Stub only the import embedded inside the tested function; restore sys.modules.
    hydrate_name='backend.server.runtime.runtime_payload_hydration'
    hydration=ModuleType(hydrate_name)
    hydration.hydrate_runtime_job_payload=lambda mapping: mapping
    previous=sys.modules.get(hydrate_name)
    sys.modules[hydrate_name]=hydration
    try:
        def one_case(stage=None, *, mode='success', legacy_job=False):
            events=[]
            job_id=stage[1] if stage else None
            if legacy_job: job_id=sorted(legacy)[0]
            fake_job=Job(job_id=job_id,job_type=stage[0] if stage else 'legacy_stage',
                        workspace_id='ws_whattoexpect_com',status='running',metadata={'attempt':0},payload={}) if job_id else None
            def admission(**kwargs):
                events.append('admission')
                if mode=='admission_denied': return {'admitted':False}
                return {'admitted':True,'registration':object()}
            def dequeue(**kwargs):
                events.append('dequeue')
                assert kwargs['allowed_job_ids']==stage_ids
                assert kwargs['worker_id']==WORKER
                if fake_job and fake_job.job_id not in stage_ids:
                    return None
                if mode=='idle': return None
                return fake_job
            def runtime_map(j):
                events.append('map')
                return {'job_id':j.job_id,'workspace_id':j.workspace_id,'job_type':j.job_type,
                        'metadata':dict(j.metadata),'payload':dict(j.payload)}
            def getreg(jobtype):
                events.append('registration')
                return {'metadata':{'required_worker_capabilities':['universal_runtime']},
                        'retry_policy':{'maximum_attempts':1,'retry_on_handler_error':False,'retry_on_contract_error':False}}
            def reg_admit(**kwargs):
                events.append('registration_admission')
                return SimpleNamespace(admitted=True)
            def capmatch(**kwargs):
                events.append('capability')
                return SimpleNamespace(compatible=True,missing_capabilities=(),required_capabilities=('universal_runtime',))
            def dispatch(mapping):
                events.append('dispatch')
                if mode=='handler_error': raise RuntimeError('isolated deliberate failure')
                return {'test_only':True,'job_id':mapping['job_id']}
            def release(**kwargs):
                events.append('release')
                return {'lease_released_test_only':True}
            def complete(jid,metadata):
                events.append('completed')
                assert jid==job_id and metadata.get('canonical_job_id_preserved') is True
                return Job(job_id=jid,status='completed')
            def fail(jid,reason,metadata):
                events.append('failed')
                assert jid==job_id and 'isolated deliberate failure' in reason
                return Job(job_id=jid,status='failed')
            def failure_attempt(metadata): return 1
            def failure_policy(**kwargs): return {'maximum_attempts':1,'retry_on_handler_error':False,'retry_on_contract_error':False}
            deps={
                'Any':object,'Callable':object,'Iterable':object,'Mapping':Mapping,
                'deepcopy':deepcopy,'JOB_STATUS_RUNNING':'running','JOB_STATUS_COMPLETED':'completed',
                'JOB_STATUS_FAILED':'failed','JOB_STATUS_QUEUED':'queued',
                'UNIVERSAL_RUNTIME_WORKER_VERSION':'universal_runtime_worker_v1',
                'UNIVERSAL_RUNTIME_WORKER_RESULT_SCHEMA_VERSION':'universal_runtime_worker_result_v1',
                'UniversalRuntimeWorkerContractError':ContractError,
                'UniversalRuntimeWorkerFinalizationError':FinalizationError,
                'RuntimeRegistrationAdmissionError':AdmissionError,
                'UniversalWorkerCapabilitySnapshot':CapSnapshot,
                'admit_universal_runtime_worker':admission,'dequeue_job':dequeue,
                'orchestration_job_to_runtime_mapping_v1':runtime_map,
                'get_runtime_registration':getreg,
                'require_runtime_registration_admission':reg_admit,
                'match_universal_worker_capabilities':capmatch,
                'dispatch_registered_runtime_handler':dispatch,
                'release_universal_runtime_job_lease':release,
                'mark_job_completed':complete,'mark_job_failed':fail,
                '_runtime_failure_attempt_number_v1':failure_attempt,
                '_runtime_retry_policy_v1':failure_policy,
                '_runtime_failure_is_contract_error_v1':lambda exc: isinstance(exc,ContractError),
                '_requeue_same_runtime_job_v1':lambda **kwargs: (_ for _ in ()).throw(RuntimeError('retry not expected')),
            }
            # Executable body uses injected dependencies only.
            exec(worker_code,deps)
            runner=deps['run_one_universal_runtime_job_v1']
            result=runner(worker_id=WORKER, allowed_job_ids=stage_ids,dispatcher=dispatch)
            return result,events

        for stage in stages:
            name,jid=stage[:2]
            result,events=one_case(stage)
            record('worker_runner_completed_'+name,result['worker_status']=='COMPLETED' and result['job_id']==jid and result['terminal_status']=='completed')
            record('worker_runner_sequence_'+name,events==['admission','dequeue','map','registration','registration_admission','capability','dispatch','release','completed'],events)
            record('handler_called_once_'+name,events.count('dispatch')==1)
        result,events=one_case(stages[0],mode='idle')
        record('worker_idle_no_dispatch',result['worker_status']=='IDLE' and events==['admission','dequeue'])
        result,events=one_case(stages[0],mode='handler_error')
        record('worker_failure_finalized',result['worker_status']=='FAILED' and 'failed' in events and 'completed' not in events,events)
        result,events=one_case(stages[0],legacy_job=True)
        record('legacy_excluded_without_claim',result['worker_status']=='IDLE' and 'dispatch' not in events)
        try:
            one_case(stages[0],mode='admission_denied')
        except ContractError:
            record('worker_admission_denied_predequeue',True)
        else: record('worker_admission_denied_predequeue',False)
        record('worker_source_unchanged',hashlib.sha256(SOURCE.read_bytes()).hexdigest()==worker_hash)
        record('scope_source_unchanged',hashlib.sha256(SCOPE.read_bytes()).hexdigest()==scope_hash)
    finally:
        if previous is None: sys.modules.pop(hydrate_name,None)
        else: sys.modules[hydrate_name]=previous

try:
    run()
    passed=all(x['passed'] for x in checks)
    err=None
except BaseException as e:
    passed=False
    err={'type':type(e).__name__,'detail':str(e),'traceback':traceback.format_exc(limit=6)}
    print('STOP:',type(e).__name__,str(e))
finally:
    data={
        'name':'AK7 real worker function body, isolated dependencies',
        'status':'PASS' if passed else 'FAIL',
        'checks_passed':sum(x['passed'] for x in checks),
        'checks_total':len(checks),
        'checks':checks,
        'limitations':[
            'Executes AST-compiled actual worker runner body; no production module imported',
            'Dequeue, admission, stage dispatcher, job store and hydration replaced with isolated doubles',
            'Not real production worker hosting, actual signed issuer, real queue claim or six production stage handlers',
            'Operational trust and full integrated production certification remain incomplete',
        ],
        'production_activation':'NO-GO',
        'error':err,
        'generated_utc':datetime.now(timezone.utc).isoformat(),
    }
    REPORT.write_text(json.dumps(data,indent=2),encoding='utf-8')
    print('\nREPORT:',REPORT)
    print('CHECKS:',data['checks_passed'],'/',data['checks_total'])
    print('PRODUCTION ACTIVATION: NO-GO')
    print('LIVE JOBS / SOURCE MODIFICATIONS: NONE')
    if not passed: sys.exit(1)
