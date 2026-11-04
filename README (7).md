# AK.6 + AK.7 — operational trust onboarding, bounded batch

This package advances the **existing** LinkCraftor Universal Runtime. It **does not** create another queue, worker or customer IAM system.

## Verified starting point (from 2026-11-04 terminal output)

- Four-control runtime verifiers installed inactive, 28/28 isolated tests passed.
- Signed grants, persisted lease validation and queue/handler verification hooks are installed.
- Production Windows service identity and independently controlled signing issuer **are not provisioned**.
- Actual AK.7 integrated execution certification remains pending. **NO-GO**.

## One combined operator audit (safe to run now)

From `C:\Users\HP\Documents\LinkCraftor` in PowerShell, save `AK6_AK7_Operator_Trust_Audit.ps1` at the project root and run:

```powershell
$ErrorActionPreference = 'Stop'
.\AK6_AK7_Operator_Trust_Audit.ps1
```

It reports missing provisioning requirements and writes `AK6_AK7_OPERATOR_TRUST_AUDIT.json`. **It never provisions keys, identities, databases, services, or turns on worker claims**.

If an independently operated signer and a real Windows service already exist, provide their public-facing identifiers (not a secret):

```powershell
.\AK6_AK7_Operator_Trust_Audit.ps1 -WorkerServiceName 'ActualWindowsServiceName' -IssuerPublicKeyFile 'C:\secure-staging\real_issuer_public.b64'
```

Do not fabricate an issuer or use isolated test keys. Never upload or paste a private key or account password.

## How to actually finish AK.6, as opposed to just adding code

1. **Issuer:** An organization-controlled signing service must authenticate authorizing operators/workflows, approve the exact canonical job/workspace/workflow/stage/handler/worker/expiry, issue unique nonces and sign grants using a private Ed25519 key **kept off the worker host**. The worker never signs its own grants.
2. **Dedicated worker identity:** Register/deploy the existing Universal Runtime Worker as a restricted Windows service under a dedicated, non-interactive identity; confirm the actual process token, service ACLs, start permissions and deployment controls. Do not use the interactive developer account.
3. **Provision and pin trust:** After verifying the issuer public key fingerprint out-of-band and dedicated service account/SID, review and run the previously installed `provision_ak6_machine_trust.ps1` in a controlled elevated change window. Do not run it before the exact account and public key are verified. The bundled script performs an audit, **not** provisioning.
4. **Authorize and certify:** On a disposable, backed-up clone of the six-job store, verify actual service token, signed grants from the real issuer, lock/lease ownership, nonce reservation/consumption, revocation, restart/recovery, expired/forged/mismatched grant rejection, and legacy-job isolation. Do not enable the production queue as a shortcut. Only then certify AK.7, AK.8 and AN and consider AO.

## Important limitations

- Windows service identity / key control cannot be independently provisioned or validated from this chat. There is currently **no evidence of a production issuer or dedicated service**.
- The existing provisioning utility has **not** been audited and executed on the user's Windows host. Its security properties must be verified against real ACLs and service configuration before use.
- The combined operator audit is **read-only** and does not certify live execution. Its `PASS` signals are limited to what the audit verifies. It deliberately keeps live-worker token and issuer-owned grant certification blocked.
- Passing earlier 28/28 isolated tests proves isolated logic, not real issuer identity or trust deployment.

Keep the original frozen checklist: AK.6 → AK.7 → AK.8/AN → AO/AP. No new phase.
