LinkCraftor AK.7 — Isolated Actual Entry-Point Negative Certification

Extract ak7_isolated_entrypoint_certification.py to the LinkCraftor repo root.
PowerShell:
  $ErrorActionPreference = 'Stop'
  python .\ak7_isolated_entrypoint_certification.py
  if ($LASTEXITCODE -ne 0) { throw 'AK.7 entrypoint certification failed' }

The runner extracts the actual on-disk dequeue_job and handler function bodies
and executes them with in-memory queue candidates, mocked locks, and forbidden
state writers. It temporarily mocks the queue-enabled feature flag ONLY in the
harness process so the protected branch can be exercised without live claims.

Reports unauthorized admission checks for all 6 canonical jobs, both handler
entry points, legacy scope exclusion, and file integrity. Source scripts and
job stores are not modified; only the JSON report is written.

Not covered: positive authorization with a real issuer/service account,
full genuine queue -> runtime worker -> handler execution, AWS deployment.
No final AK.7/production certification is implied.
