AK.7 — Existing Universal Worker Runner Isolated Certification

Copy ak7_worker_runner_isolated.py into the LinkCraftor repository root.
From activated PowerShell at C:\Users\HP\Documents\LinkCraftor:

python .\ak7_worker_runner_isolated.py
if ($LASTEXITCODE -ne 0) { throw 'AK.7 worker runner certification failed.' }

This executes the AST-compiled REAL run_one_universal_runtime_job_v1 function body
with isolated, injected implementations of admission, dequeue, mapping,
registration, capability validation, dispatch, lease release and state changes.
No live imports of backend modules, job store, services, or stage handlers.
Output: AK7_WORKER_RUNNER_ISOLATED_CERTIFICATION.json

It is NOT end-to-end live worker or production authorization certification.
AK.6 operational trust and final AK.7/AK.8 production gates remain blocked.
