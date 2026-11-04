# AK.6 — Windows SQLite connection-close correction

The previous package's `test_ak6_four_controls.py` failed with `[WinError 32]` during `TemporaryDirectory` cleanup because the SQLite database remained open. Python's `with sqlite3.connect(...)` handles transactions but does **not** automatically close the connection.

The replacement package modifies exactly two files:
- `test_ak6_four_controls.py`: explicitly closes both temporary manual SQLite connections, and commits updates before closing.
- `ak6_operational_trust.py`: explicitly closes every operational ledger connection on normal return or exception, including fail-closed authorization rejects.

No change to authorization decision policy, production provisioning, queue gates, or handler guards.

## Install / test
1. Extract the ZIP into the **LinkCraftor project root**, replacing `test_ak6_four_controls.py`, `ak6_operational_trust.py` (the project-root source copy) and `apply_ak6_four_controls.py`. Do not change the runtime's existing `backend/server/runtime/security/ak6_operational_trust.py` if the prior installation never completed.
2. Run:

```powershell
$ErrorActionPreference = "Stop"
python .\test_ak6_four_controls.py
if ($LASTEXITCODE -ne 0) { throw "AK.6 isolated tests failed. Installation stopped." }
python .\apply_ak6_four_controls.py
if ($LASTEXITCODE -ne 0) { throw "AK.6 integration failed. Production remains blocked." }
```

The installer makes source backups before modifying runtime files. Do not run provisioning scripts or enable jobs as part of this correction.

## Verified locally
`python -B test_ak6_four_controls.py`: **28/28 PASS** (Linux environment). Windows-specific confirmation awaits the user's PowerShell run.

Production issuer and dedicated service identity remain unprovisioned. **Production NO-GO.**
