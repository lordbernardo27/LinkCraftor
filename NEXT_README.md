# AK.6 + AK.7 — integrated readiness gate

This package validates the *installed* signed-grant verification hooks without executing live jobs. It does **not** create an authority, mint signing credentials, alter source, or enable any worker. Run after installing the earlier signed authority integration and retaining `test_ak6_signed_grants_isolated.py` at the LinkCraftor root.

## Run

1. Extract `ak6_ak7_integrated_readiness.py` into `C:\Users\HP\Documents\LinkCraftor`.
2. Run from the activated environment:

```powershell
$ErrorActionPreference = 'Stop'
python .\ak6_ak7_integrated_readiness.py
if ($LASTEXITCODE -ne 0) { throw 'AK.6/AK.7 readiness verification failed.' }
```

3. Review or upload `AK6_AK7_INTEGRATED_READINESS.json`.

## Scope and limits

The readiness gate independently checks source structure, verifies both handler entry guards, checks the atomic queue placement, invokes the isolated 21-check suite, fingerprints production source and records the missing trust prerequisites. All negative production readiness findings are intentionally recorded as `BLOCK` and a NO-GO decision.

No production activation until an externally controlled trusted issuer and worker identity proof are provisioned and lease, anti-replay, revocation, queue-to-handler binding, and real integrated tests pass. **An environment variable holding a public key is not a robust trust anchor if the worker process can replace it.** A signed grant allowing both `claim` and `execute` does not by itself prevent replay.
