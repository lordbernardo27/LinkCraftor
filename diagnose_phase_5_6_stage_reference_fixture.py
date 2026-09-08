from __future__ import annotations

import inspect

from backend.server.coordination.runtime_integration import (
    coordination_runtime_bridge as b,
)

C = b.UniversalStageReference

print("MODULE:", C.__module__)
print("SIGNATURE:", inspect.signature(C))

values = {
    "stage_id": "stage_phase_5_6_integration",
    "stage_version": "stage_phase_5_6_integration_v1",
    "pipeline_id": "pipeline_phase_5_6_integration",
    "workflow_type": "phase_5_6_integration_workflow",
    "workflow_contract_version": "universal_workflow_contract_v1.1.0",
    "execution_target": "UNIVERSAL_RUNTIME",
    "job_type": "phase_5_6.integration.test",
    "runtime_stage": "phase_5_6_integration_stage",
    "required_payload_fields": ("document_id",),
    "metadata": {"phase": "5.6.integration"},
    "contract_version": "universal_stage_reference_v1.3.0",
}

signature = inspect.signature(C)

kwargs = {
    name: value
    for name, value in values.items()
    if name in signature.parameters
}

print("KWARGS:", kwargs)
print()

try:
    obj = C(**kwargs)

except Exception as exc:
    print("ERROR TYPE:", type(exc).__name__)
    print("ERROR:", exc)
    print(
        "VIOLATIONS:",
        getattr(exc, "violations", None),
    )
    print(
        "CODE:",
        getattr(exc, "code", None),
    )

else:
    print("CONSTRUCTED:", obj)
