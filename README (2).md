# LinkCraftor AK.6 + AK.7 — source-based implementation update

Reviewed source: the user's 13-file `AK6_AK7_Runtime_Source_20261104_122115.zip`.

## Verified gap
The existing `require_connected_domain_job_execution_permission` validates worker, job, workspace, and that a handler key is nonempty; it delegates allowed handler membership to supplied evidence. A caller could supply a different handler key with matching synthetic evidence. The six frozen stage identities already exist in `universal_runtime_worker_scope_contract.STAGES`.

## What the script does
`apply_ak6_stage_binding.py` makes a narrow, backed-up change to the existing AK.6 permission adapter: exact canonical job-to-stage binding. It tests all six job IDs with wrong stages and valid stages but missing evidence. It preserves the queue and handler deny guards and asserts the claim gate remains disabled. It does not claim jobs, call handlers, or turn on a worker.

Run from project root:

```powershell
$ErrorActionPreference = 'Stop'
python .\apply_ak6_stage_binding.py
if ($LASTEXITCODE -ne 0) { throw 'AK.6 stage-binding patch failed' }
```

## Remaining blocker — **not resolved by this patch**
The reviewed files contain permission *evaluators* and caller-supplied evidence data classes, not a demonstrated independently verified worker authorization issuer. `RuntimeServiceRegistry` proves service object registration, not authentication of a running workload. `admit_universal_runtime_worker` creates a fresh self-reported registration and heartbeat; it does not verify an external worker identity. Before queue/handler denial controls can be replaced, the authenticated source of runtime evidence, its trust boundary, expiry/revocation and bindings for exact job/workspace/worker/handler must be implemented and tested. Do not use `authorization_check=lambda **_: True` or constructed `ALLOW` records as production authority.

## Status
AK.6 still incomplete. AK.7 completed only as isolated evaluator tests (prior 40/40). Keep AK.8, AN, AO and AP blocked until real evidence integration and end-to-end tests have passed. Do not expand the frozen checklist.
