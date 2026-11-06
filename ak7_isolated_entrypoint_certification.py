"""AK.7: execute real queue + handler function bodies in memory-only harness.
No package imports, production job reads, database connections, source writes, or live claims.
NOT a positive production execution or final AK.7 certification.
"""
from __future__ import annotations
import ast
import contextlib
import hashlib
import json
import sys
import tempfile
import traceback
import types
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch

ROOT = Path.cwd().resolve()
if ROOT.name.lower() != 'linkcraftor':
    raise SystemExit('STOP: Run in LinkCraftor project root')
QUEUE = ROOT/'backend/server/orchestration/queue.py'
HANDLER = ROOT/'backend/server/runtime/universal_runtime_registration.py'
SCOPE = ROOT/'backend/server/runtime/universal_runtime_worker_scope_contract.py'
FILES=(QUEUE,HANDLER,SCOPE)
if not all(p.is_file() for p in FILES):
    raise SystemExit('STOP: required original source files absent')
BEFORE={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in FILES}

def extract(source_file, names):
    tree=ast.parse(source_file.read_text(encoding='utf-8-sig'), filename=str(source_file))
    selected=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name in names]
    if {n.name for n in selected}!=set(names):
        raise RuntimeError('Source shape mismatch: '+str(names))
    module=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)]+selected,type_ignores=[])
    ast.fix_missing_locations(module)
    return compile(module,str(source_file),'exec')

# Extract canonical identity data from source AST, never load the production job store.
tree=ast.parse(SCOPE.read_text(encoding='utf-8-sig'))
assignments={}
for node in tree.body:
    if isinstance(node,ast.Assign):
        for target in node.targets:
            if isinstance(target,ast.Name) and target.id in {'STAGES','WORKSPACE_ID','WORKFLOW_ID','LEGACY_IDS'}:
                assignments[target.id]=ast.literal_eval(node.value.args[0] if target.id=='LEGACY_IDS' and isinstance(node.value,ast.Call) else node.value)
stages=assignments['STAGES']; ids=[v[1] for v in stages]
if len(ids)!=6 or len(set(ids))!=6: raise RuntimeError('Canonical scope not exactly six')
legacy=set(assignments['LEGACY_IDS'])
assert set(ids).isdisjoint(legacy)
checks=[]

def record(name,ok,detail=''):
    checks.append(dict(name=name,passed=bool(ok),detail=detail))
    print(('PASS' if ok else 'FAIL')+': '+name+((' - '+detail) if detail else ''))

# Mock the ONLY imports reached in the tested boundaries; never import job-store modules.
module_names=('backend','backend.server','backend.server.runtime',
              'backend.server.runtime.runtime_feature_flag_gateway',
              'backend.server.runtime.universal_runtime_worker_scope_contract',
              'backend.server.runtime.security',
              'backend.server.runtime.security.ak6_signed_execution_grants')
fakes={name:types.ModuleType(name) for name in module_names}
fakes['backend.server.runtime.universal_runtime_worker_scope_contract'].EXPECTED_SCOPE=frozenset(ids)
fakes['backend.server.runtime.runtime_feature_flag_gateway'].runtime_queue_claims_enabled=lambda worker_id:True
signed_calls=[]
def refuse_without_live_issuer(*,job,worker_id,action,**kwargs):
    signed_calls.append((getattr(job,'job_id',None) or (job.get('job_id') if isinstance(job,dict) else None),action))
    raise PermissionError('AK7_ISOLATED_NO_PRODUCTION_AUTHORITY')
fakes['backend.server.runtime.security.ak6_signed_execution_grants'].require_signed_ak6_execution_authority=refuse_without_live_issuer
fakes['backend.server.runtime.security.ak6_signed_execution_grants'].WORKER_ID='universal_runtime_worker_v1'
for i in range(1,len(module_names)):
    parent=module_names[i].rsplit('.',1)[0]
    setattr(fakes[parent],module_names[i].split('.')[-1],fakes[module_names[i]])

@contextlib.contextmanager
def lock(): yield
class Candidate:
    def __init__(self,jid):
        self.job_id=jid;self.job_type='connect_domain_stage';self.metadata={}

# Bind *source bodies*, but replace storage/locking/mutation dependencies with inert stubs.
queue_ns={'__name__':'ak7_queue_test', '_dequeue_lock':lock,
          '_queued_jobs':lambda:(),
          'update_job_status':lambda *a,**k: (_ for _ in ()).throw(AssertionError('unsafe write reached')),
          'recover_interrupted_runtime_jobs':lambda: (_ for _ in ()).throw(AssertionError('recovery reached')),
          'prepare_universal_runtime_job_lease':lambda **kw: (_ for _ in ()).throw(AssertionError('lease creation reached')),
          'JOB_STATUS_RUNNING':'running','Mapping':__import__('collections').abc.Mapping}
exec(extract(QUEUE,{'dequeue_job'}),queue_ns)
handler_ns={'__name__':'ak7_handler_test',
            'ensure_persisted_runtime_registrations_loaded':lambda: (_ for _ in ()).throw(AssertionError('handler registry accessed')),
            'update_job_status':lambda *a,**k: (_ for _ in ()).throw(AssertionError('handler state write'))}
exec(extract(HANDLER,{'_ak_require_connected_domain_execution_authority','dispatch_registered_runtime_handler','execute_registered_runtime_job_v1'}),handler_ns)

with patch.dict(sys.modules,fakes):
    for stage,jid,*_ in stages:
        queue_ns['_queued_jobs']=lambda j=jid:(Candidate(j),)
        try:
            outcome=queue_ns['dequeue_job'](worker_id='universal_runtime_worker_v1',allowed_job_ids=frozenset(ids))
        except (PermissionError,RuntimeError,ValueError) as exc:
            record('canonical_queue_denied_'+stage,True,type(exc).__name__)
        except Exception as exc:
            record('canonical_queue_denied_'+stage,False,repr(exc))
        else:
            record('canonical_queue_denied_'+stage,outcome is None,'returned '+repr(outcome))
        job=dict(job_id=jid,job_type=stage,stage=stage,workspace_id=assignments['WORKSPACE_ID'],payload={})
        for fn in ('dispatch_registered_runtime_handler','execute_registered_runtime_job_v1'):
            try:
                handler_ns[fn](job)
            except (PermissionError,RuntimeError,ValueError) as exc:
                record('canonical_'+fn+'_'+stage,True,type(exc).__name__)
            except Exception as exc:
                record('canonical_'+fn+'_'+stage,False,repr(exc))
            else:
                record('canonical_'+fn+'_'+stage,False,'unauthorized entry accepted')

    # Even with the test-only feature flag enabled, a six-ID scope skips every legacy record.
    queue_ns['_queued_jobs']=lambda:tuple(Candidate(j) for j in sorted(legacy))
    try:
        result=queue_ns['dequeue_job'](worker_id='universal_runtime_worker_v1',allowed_job_ids=frozenset(ids))
        record('legacy_records_excluded_by_canonical_scope',result is None)
    except Exception as exc:
        record('legacy_records_excluded_by_canonical_scope',False,repr(exc))

# For installed signed hooks, prove calls reach the signed-verifier entrypoint,
# represented by an explicitly rejecting fake (never use a live issuer).
queue_has_signed='AK6_SIGNED_EXECUTION_AUTHORITY_INTEGRATED' in QUEUE.read_text(encoding='utf-8-sig')
handler_has_signed='AK6_SIGNED_EXECUTION_AUTHORITY_INTEGRATED' in HANDLER.read_text(encoding='utf-8-sig')
if queue_has_signed:
    record('six_queue_calls_reached_signed_verifier',sum(action=='claim' for _,action in signed_calls)==6)
if handler_has_signed:
    record('twelve_handler_calls_reached_signed_verifier',sum(action=='execute' for _,action in signed_calls)==12)
# Runtime code must not alter any original source file.
for p in FILES:
    record('source_unmodified_'+p.name,hashlib.sha256(p.read_bytes()).hexdigest()==BEFORE[str(p)])

failed=[c for c in checks if not c['passed']]
report={'schema_version':'ak7_isolated_entrypoint_v1','generated_utc':datetime.now(timezone.utc).isoformat(),
        'source':'actual installed function bodies, extracted in-memory',
        'job_data_accessed':False,'production_claims_executed':False,
        'test_flag_override':'memory-only import stub, not production',
        'signed_verifier':'explicitly rejecting fake for entrypoint wiring; real crypto checked by separate suite',
        'passed':len(checks)-len(failed),'total':len(checks),'checks':checks,
        'development_entrypoint_negative_certified':not failed,
        'integrated_authorized_path_certified':False,
        'production_issuer_certified':False,'production_activation':'NO-GO'}
output=ROOT/'AK7_ISOLATED_ENTRYPOINT_CERTIFICATION.json'
output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('\nREPORT:',output)
print('ISOLATED ENTRYPOINT CHECKS:',len(checks)-len(failed),'/',len(checks))
print('PRODUCTION ACTIVATION: NO-GO')
if failed: sys.exit(1)
