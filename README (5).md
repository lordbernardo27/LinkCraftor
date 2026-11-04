# LinkCraftor — AK.6 persisted lease enforcement (inactive)

This is a **real, bounded implementation** of the authoritative persisted-job/lease validation portion of AK.6. It does **not** satisfy the other outstanding trust requirements or authorize production activation.

**Changes:** adds `backend/server/runtime/security/ak6_authoritative_lease.py` and adds a call to it in the previously installed signed-grant verifier for `action="execute"`. The verifier now loads the job from `backend.server.orchestration.job_store.get_job` and checks the persisted `running` state, workspace, stage, claim owner, instance ID, lease ID, start/expiry and active/released fields against the proposed job. Mismatches or storage failures deny execution. The code does not execute jobs, read queue state in tests, create keys, or enable flags.

**Why partial:** this does not authenticate the worker process; an attacker with the worker identity and a valid copied signed grant could still attempt replay. The signing authority is not provisioned, and nonce/revocation controls are still missing. Production remains NO-GO. Do not set the signing authority environment variables or enable the production queue from this package.

## Instructions

1. Extract all three Python files into `C:\Users\HP\Documents\LinkCraftor` (project root).
2. Run from the project's activated `.venv`:

```powershell
$ErrorActionPreference = "Stop"
python .\test_ak6_authoritative_lease.py
if ($LASTEXITCODE -ne 0) { throw "AK.6 lease tests failed" }
python .\apply_ak6_persisted_lease.py
if ($LASTEXITCODE -ne 0) { throw "AK.6 lease integration failed" }
```

The patch script is retry-safe and backups the prior verifier under `backend/server/data/runtime_backups/connect_domain_AK6_PERSISTED_LEASE_...`. It does not modify the queue, handler, worker service or feature flags.

**Limitations:** queued claim-side authorization still checks signatures but lacks independently authenticated worker/process credentials; live lease checks only occur at handler entry. Expiry uses the persisted lease timestamp and is a check-at-start, not ongoing enforcement throughout long jobs. Persisted job-store integrity and deployment permissions need separate certification. This patch is not a replacement for the remaining AK.6 controls.
