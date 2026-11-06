LinkCraftor AK.8 Conditional Development Evidence Review

Extract ak8_conditional_certification.py to your repository root:
C:\Users\HP\Documents\LinkCraftor

Four existing reports must already be present in the repository root:
AK7_COMBINED_DEVELOPMENT_CERTIFICATION.json
AK7_ISOLATED_ENTRYPOINT_CERTIFICATION.json
AK7_ISOLATED_POSITIVE_BRIDGE.json
AK7_WORKER_RUNNER_ISOLATED_CERTIFICATION.json

In the activated PowerShell environment:
python .\ak8_conditional_certification.py
if ($LASTEXITCODE -ne 0) { throw 'AK.8 evidence verification failed.' }

Output:
AK8_CONDITIONAL_DEVELOPMENT_CERTIFICATION.json
AK8_CONDITIONAL_DEVELOPMENT_CERTIFICATION.md

Fail closed on missing/invalid evidence; no worker startup, job execution,
production key provisioning, feature-flag changes, or source-code modifications.

IMPORTANT: Conditional development evidence only. AK.6 production trust and
AK.7 operational certification remain unresolved. AN/AO/AP are NO-GO.
