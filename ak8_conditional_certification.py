"""LinkCraftor AK.8: read-only evidence verification and conditional development certification.

Run from LinkCraftor repository root with Python 3.13. Does not execute worker,
queue, handlers, stage jobs, provisioning or authorization actions.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd().resolve()
SPECS = (
    ('combined_development', 'AK7_COMBINED_DEVELOPMENT_CERTIFICATION.json', 41),
    ('negative_entrypoints', 'AK7_ISOLATED_ENTRYPOINT_CERTIFICATION.json', 24),
    ('positive_queue_handler', 'AK7_ISOLATED_POSITIVE_BRIDGE.json', 41),
    ('worker_runner', 'AK7_WORKER_RUNNER_ISOLATED_CERTIFICATION.json', 26),
)
REQUIRED_SOURCE = (
    'backend/server/runtime/universal_runtime_worker_service.py',
    'backend/server/runtime/universal_runtime_worker_service_registration.py',
    'backend/server/runtime/universal_runtime_worker_v1.py',
    'backend/server/orchestration/queue.py',
    'backend/server/runtime/universal_runtime_registration.py',
    'backend/server/runtime/universal_runtime_worker_scope_contract.py',
    'backend/server/runtime/security/ak6_signed_execution_grants.py',
    'backend/server/runtime/security/ak6_authoritative_lease.py',
    'backend/server/runtime/security/ak6_operational_trust.py',
)

def stop(message: str) -> None:
    print('STOP:', message)
    raise SystemExit(1)


def check_report(label: str, path: Path, expected: int) -> dict:
    if not path.is_file():
        stop(f'Missing AK.7 evidence: {path.name}')
    raw = path.read_bytes()
    try:
        obj = json.loads(raw.decode('utf-8-sig'))
    except (ValueError, UnicodeError) as exc:
        stop(f'Invalid JSON evidence in {path.name}: {type(exc).__name__}')
    if not isinstance(obj, dict) or not isinstance(obj.get('checks'), list):
        stop(f'Invalid checks structure: {path.name}')
    checks = obj['checks']
    if len(checks) != expected:
        stop(f'{path.name}: expected {expected} checks, got {len(checks)}')
    for idx, c in enumerate(checks):
        if not isinstance(c, dict) or not isinstance(c.get('name'), str) or not c['name']:
            stop(f'{path.name}: invalid check at index {idx}')
        ok = c.get('status') == 'PASS' if label == 'combined_development' else c.get('passed') is True
        if not ok:
            stop(f'{path.name}: non-passing check: {c.get("name")}')
    if len({c['name'] for c in checks}) != expected:
        stop(f'{path.name}: duplicate check names found')
    if label == 'combined_development':
        if obj.get('all_isolated_checks_passed') is not True or obj.get('development_isolated_only') is not True:
            stop(f'{path.name}: missing isolated-development attestation')
        for field in ('real_worker_identity_certified', 'external_issuer_provisioned', 'production_execution_authorized', 'production_jobs_executed'):
            if obj.get(field) is not False:
                stop(f'{path.name}: unexpected production claim in {field}')
    elif label == 'negative_entrypoints':
        for key, expected_value in (('passed', 24),('total',24),('development_entrypoint_negative_certified',True),('integrated_authorized_path_certified',False),('production_issuer_certified',False),('job_data_accessed',False),('production_claims_executed',False),('production_activation','NO-GO')):
            if obj.get(key) != expected_value:
                stop(f'{path.name}: invalid {key}')
    elif label == 'positive_queue_handler':
        for key, expected_value in (('passed',41),('total',41),('source_function_bodies_executed',True),('full_worker_runner_executed',False),('real_stage_handlers_executed',False),('live_job_store_accessed',False),('production_worker_started',False),('production_authorized_execution_certified',False),('production_activation','NO-GO')):
            if obj.get(key) != expected_value:
                stop(f'{path.name}: invalid {key}')
    else:
        for key, expected_value in (('checks_passed',26),('checks_total',26),('status','PASS'),('production_activation','NO-GO')):
            if obj.get(key) != expected_value:
                stop(f'{path.name}: invalid {key}')
        if obj.get('error') is not None or not obj.get('limitations'):
            stop(f'{path.name}: missing limitations or reported error')
    print(f'PASS: {label}: {expected}/{expected} evidenced checks')
    return {'name': label, 'file': path.name, 'checks_passed': expected, 'checks_total':expected, 'sha256':hashlib.sha256(raw).hexdigest(), 'generated_utc':obj.get('generated_utc')}


def main() -> None:
    if ROOT.name.lower() != 'linkcraftor':
        stop('Run from the LinkCraftor repository root')
    before = {}
    for relative in REQUIRED_SOURCE:
        p = ROOT / relative
        if not p.is_file():
            stop(f'Missing required runtime source: {relative}')
        before[relative] = hashlib.sha256(p.read_bytes()).hexdigest()
    evidence = [check_report(label, ROOT / filename, n) for label,filename,n in SPECS]
    if any(hashlib.sha256((ROOT / f).read_bytes()).hexdigest() != digest for f,digest in before.items()):
        stop('Runtime source changed during evidence validation')
    total = sum(e['checks_passed'] for e in evidence)
    result = {
        'schema_version':'linkcraftor.ak8.conditional_development_certification.v1',
        'generated_utc':datetime.now(timezone.utc).isoformat(),
        'checkpoint':'6.9.8 / AK.8',
        'decision':'CONDITIONAL_DEVELOPMENT_EVIDENCE_ACCEPTED',
        'ak7_isolated_evidence':'PASS',
        'ak6_operational_provisioning':'DEFERRED_NOT_CERTIFIED',
        'ak7_production_integrated_certification':'NOT_CERTIFIED',
        'ak8_final_production_certification':'NOT_CERTIFIED',
        'an_production_readiness_gate':'NO-GO',
        'ao_controlled_worker_activation':'NOT_AUTHORIZED',
        'ap_worker_activation_certification':'NOT_CERTIFIED',
        'evidence':evidence,
        'total_evidenced_checks':total,
        'runtime_source_sha256':before,
        'limitations':[
            'Reports certify separate isolated harnesses; their combined count is not a single live end-to-end test.',
            'Real operational worker identity and trusted issuer are not provisioned.',
            'No real issuer-signed grant, production stage handler, or full six-stage live pipeline execution was certified.',
            'Development tests do not authorize queue feature flags, production claims, or worker startup.',
            'AWS workload identity and trust provisioning remain future deployment requirements.',
        ],
        'production_jobs_accessed_by_this_review':False,
        'production_sources_modified_by_this_review':False,
    }
    report_path = ROOT / 'AK8_CONDITIONAL_DEVELOPMENT_CERTIFICATION.json'
    summary_path = ROOT / 'AK8_CONDITIONAL_DEVELOPMENT_CERTIFICATION.md'
    lines = [
        '# LinkCraftor AK.8 — Conditional Development Certification', '',
        f"Generated (UTC): {result['generated_utc']}", '',
        '**Decision: CONDITIONAL DEVELOPMENT EVIDENCE ACCEPTED. NOT final production certification.**', '',
        f'AK.7 isolated evidence: **{total}/{total} checks across four independent reports**.', '',
        '| Evidence report | Result |', '|---|---:|',
    ]
    lines += [f"| {e['file']} | {e['checks_passed']}/{e['checks_total']} |" for e in evidence]
    lines += [
        '', '## Mandatory unresolved gates', '',
        '- AK.6 production worker identity, trusted issuer and protected operational trust provisioning: **DEFERRED / NOT CERTIFIED**.',
        '- AK.7 real integrated production worker/issuer, stage handler and execution certification: **NOT CERTIFIED**.',
        '- AK.8 final production authorization: **NOT CERTIFIED**.',
        '- AN production readiness: **NO-GO**.',
        '- AO controlled worker activation: **NOT AUTHORIZED**.',
        '- AP activation certification: **NOT CERTIFIED**.',
        '', '## Evidence boundary', '',
    ]
    lines += [f'- {s}' for s in result['limitations']]
    lines += ['', 'No runtime source, production job, feature flag or queue record was modified by this review.', '']
    # Write both deliverables after every source/report check has passed.
    report_path.write_text(json.dumps(result,indent=2) + '\n',encoding='utf-8')
    summary_path.write_text('\n'.join(lines),encoding='utf-8')
    print(f'PASS: AK.8 development evidence: {total}/{total} across 4 reports')
    print('DECISION: CONDITIONAL DEVELOPMENT EVIDENCE ACCEPTED')
    print('AK.8 FINAL PRODUCTION CERTIFICATION: NOT CERTIFIED')
    print('AN: NO-GO | AO: NOT AUTHORIZED | AP: NOT CERTIFIED')
    print('PRODUCTION JOBS / RUNTIME SOURCE MODIFIED: NONE')
    print('REPORT:', report_path)
    print('SUMMARY:', summary_path)

if __name__ == '__main__':
    main()
