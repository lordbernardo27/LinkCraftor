# LinkCraftor AK.6 — signed authorization integration (inactive)

## Scope
This package changes only the existing atomic queue guard and registered-handler guard, and adds a small signature **verifier**. It DOES NOT add a worker, queue, dispatcher or job. It does not enable the feature flag, provision an issuer, or execute jobs.

## Source-grounded details
- Queue: `backend/server/orchestration/queue.py` checks signed authorization within `_dequeue_lock()` and **before** registration policy, job reuse, dependency policy, and `update_job_status()`.
- Registered handlers: `backend/server/runtime/universal_runtime_registration.py` checks authorization at the existing first-statement guard in each entry point.
- Verification module: `backend/server/runtime/security/ak6_signed_execution_grants.py` verifies externally issued Ed25519 signatures on exact job/workspace/workflow/stage/handler/registration-fingerprint/worker identity, timestamp bounds and claimed lease metadata. It contains no issuer/private-key code.
- Previous stage-binding adapter is left unchanged. Claim feature flag and worker remain disabled.

## Preflight / installation
1. Unzip the 3 active scripts `apply_ak6_signed_authority.py`, `ak6_signed_execution_grants.py`, `test_ak6_signed_grants_isolated.py` PLUS `scope_snapshot.py` to the **LinkCraftor project root**. This README may also be copied.
2. Review the scripts. Do **not** provision/activate an authority as part of this package.
3. In existing activated venv from project root, run:

```powershell
$ErrorActionPreference = 'Stop'
python .\test_ak6_signed_grants_isolated.py
if ($LASTEXITCODE -ne 0) { throw 'AK.6 isolated tests failed; do not install' }
python .\apply_ak6_signed_authority.py
if ($LASTEXITCODE -ne 0) { throw 'AK.6 integration patch failed; production remains blocked' }
```

The test requires `cryptography` (Ed25519 support); if unavailable, **stop**, do not bypass. The patch refuses unexpected differences in queue and handler guard text. Backups are written to `backend/server/data/runtime_backups/connect_domain_AK6_SIGNED_AUTHORITY_*`. It checks source AST and does automatic rollback on failure after installation begins.

## IMPORTANT — What is NOT certified
- The signing authority (private key, issuance policy, operator authorization, rotation/revocation, key custody, issuer audit) **does not exist in this package**. Do not generate a private key inside the runtime worker process or hard-code it in the repo. Real production issuer must be separately controlled.
- Grant replay protection is NOT complete. A signed short-lived grant is checked for a correct running/claimed job and lease identity, but its nonce is not recorded in a durable one-time ledger. Revocation and a trusted worker-instance attestation are NOT certified. These require AK.7/AN closure.
- These tests are isolated and patch structural tests; they are not successful live production authorization or integrated worker execution.
- The verifier's environment variables `LC_AK6_AUTHORITY_PUBLIC_KEY_B64` and `LC_AK6_SIGNED_JOB_GRANTS_JSON` are intentionally **not** set by this package. With no production provisioning, protected queue/handler operations continue to deny.
- Feature flag remains off, registration remains disabled, and no job is claimed or modified.

## Outcomes
- Success: `AK.6 SIGNED GRANT VERIFIER: INSTALLED INACTIVE`; 21/21 isolated tests.
- NO-GO for production until externally trusted issuance, durable replay/revocation, worker-instance authentication, and integrated positive/negative tests are demonstrably complete.

## Recovery
If patch reports a failure after writes, it restores backed-up queue/handler files and removes the verifier module. Manual recovery: use its printed backup path to restore `queue.py` and `universal_runtime_registration.py`; remove `backend/server/runtime/security/ak6_signed_execution_grants.py` only if this installation created it. Do not remove older AK safety guards.
