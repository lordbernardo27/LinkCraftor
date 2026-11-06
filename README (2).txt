LinkCraftor AK.7 — Isolated Positive Queue-to-Handler Bridge

Purpose
- Run source-extracted real dequeue_job(), _ak_require_connected_domain_execution_authority(),
  execute_registered_runtime_job_v1(), and dispatch_registered_runtime_handler() bodies.
- For six canonical stage identities, exercise claim, running-state transition,
  pre-execution guard, dispatch guard, fake handler invocation, completion and progress callbacks.
- Use ONLY in-memory job records and explicit test doubles for the feature gate,
  registration/dependency policies, worker lease, authorization, and persistence.

Requirements
- Existing installed AK.6 signed authorization hook and four-controls marker.
- Windows with Python in LinkCraftor .venv.

Instructions
1. Extract ak7_positive_isolated.py into C:\Users\HP\Documents\LinkCraftor
2. In PowerShell at LinkCraftor project root, run:
   python .\ak7_positive_isolated.py
3. Report: AK7_ISOLATED_POSITIVE_BRIDGE.json

Limits / NO-GO
- No production code modifications (except creation of JSON report in project root).
- No real job store access, live claims, actual worker runner, real pipeline stage handlers,
  production signer, real signed grant, authentic workload identity or AWS deployment.
- Test-only fake verifier ALLOWS expected identities but is NOT the real Ed25519 implementation;
  actual signature/nonce/lease negative tests live in the previous AK.7 suite.
- These 41 synthetic bridge checks do NOT certify the full six-stage live pipeline.
- AK.6 operational trust remains deferred and production activation remains NO-GO.
