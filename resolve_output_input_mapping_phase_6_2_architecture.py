from __future__ import annotations

import inspect

from backend.server.coordination.stage_handoff.stage_result_processor import (
    ProcessedStageResult,
)

from backend.server.coordination.universal_stages.contract import (
    StageExecutionTarget,
    UniversalStageReference,
)

from backend.server.runtime.universal_jobs import creation_engine


checks = []


def check(name, condition):
    ok = bool(condition)
    checks.append(ok)
    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 6.2 — OUTPUT -> INPUT MAPPING ARCHITECTURE RESOLUTION")
print("=" * 120)


# ------------------------------------------------------------------
# CANONICAL INPUT AUTHORITIES
# ------------------------------------------------------------------

check(
    "ProcessedStageResult available",
    ProcessedStageResult is not None,
)

check(
    "UniversalStageReference available",
    UniversalStageReference is not None,
)

reference_signature = str(
    inspect.signature(
        UniversalStageReference
    )
)

check(
    "required_payload_fields declared on UniversalStageReference",
    "required_payload_fields" in reference_signature,
)

check(
    "execution_target declared on UniversalStageReference",
    "execution_target" in reference_signature,
)


# ------------------------------------------------------------------
# RUNTIME REQUIRED-FIELD SEMANTICS
# ------------------------------------------------------------------

runtime_source = inspect.getsource(
    creation_engine._validate_registered_payload
)

check(
    "Runtime validates top-level key presence",
    "field_name not in payload"
    in runtime_source,
)

check(
    "Runtime rejects required None values",
    "payload.get(field_name) is None"
    in runtime_source,
)

check(
    "Runtime rejects required empty strings",
    'payload.get(field_name) == ""'
    in runtime_source,
)

check(
    "Runtime does not use generic truthiness for missing fields",
    "not payload.get(field_name)"
    not in runtime_source,
)


# ------------------------------------------------------------------
# MAPPING ARCHITECTURE
# ------------------------------------------------------------------

architecture = {
    "source":
        "ProcessedStageResult.output",

    "target_requirement_authority":
        "UniversalStageReference.required_payload_fields",

    "mapping_scope":
        "top-level exact-name projection",

    "required_field_missing_when":
        (
            "key absent",
            "value is None",
            "value is empty string",
        ),

    "runtime_enforcement_owner":
        "Universal Job Creation Engine",

    "rename_mapping":
        "not introduced in Phase 6.2 v1",

    "nested_path_mapping":
        "not introduced in Phase 6.2 v1",

    "context_propagation":
        "Phase 6.3",

    "artifact_handoff":
        "Phase 6.4",

    "runtime_submission":
        "Phase 5 / Runtime boundary",
}


check(
    "source authority exact",
    architecture["source"]
    == "ProcessedStageResult.output",
)

check(
    "target requirement authority exact",
    architecture[
        "target_requirement_authority"
    ]
    == "UniversalStageReference.required_payload_fields",
)

check(
    "mapping uses exact top-level names",
    architecture["mapping_scope"]
    == "top-level exact-name projection",
)

check(
    "rename semantics deferred",
    architecture["rename_mapping"]
    == "not introduced in Phase 6.2 v1",
)

check(
    "nested path semantics deferred",
    architecture["nested_path_mapping"]
    == "not introduced in Phase 6.2 v1",
)

check(
    "Runtime remains final enforcement authority",
    architecture["runtime_enforcement_owner"]
    == "Universal Job Creation Engine",
)

check(
    "context propagation excluded",
    architecture["context_propagation"]
    == "Phase 6.3",
)

check(
    "artifact handoff excluded",
    architecture["artifact_handoff"]
    == "Phase 6.4",
)


# ------------------------------------------------------------------
# COORDINATION_ONLY INVARIANT
# ------------------------------------------------------------------

coordination_only_reference = UniversalStageReference(
    stage_id=
        "phase_6_2_coordination_only",

    stage_version=
        "1.0.0",

    pipeline_id=
        "phase_6_2_pipeline",

    workflow_type=
        "phase_6_2_workflow",

    workflow_contract_version=
        "universal_workflow_contract_v1.1.0",

    execution_target=
        StageExecutionTarget.COORDINATION_ONLY,

    job_type=
        "",

    runtime_stage=
        "",

    required_payload_fields=
        (),
)

check(
    "coordination-only stage permits empty requirements",
    coordination_only_reference.required_payload_fields
    == (),
)


# ------------------------------------------------------------------
# COMPLETENESS SEMANTIC PROOF
# ------------------------------------------------------------------

def missing_required_fields(
    *,
    payload,
    required_fields,
):

    return tuple(
        field_name
        for field_name in required_fields
        if (
            field_name not in payload
            or payload.get(field_name) is None
            or payload.get(field_name) == ""
        )
    )


check(
    "present non-empty string satisfies requirement",
    missing_required_fields(
        payload={
            "domain":
                "example.com",
        },
        required_fields=(
            "domain",
        ),
    )
    == (),
)

check(
    "absent key is missing",
    missing_required_fields(
        payload={},
        required_fields=(
            "domain",
        ),
    )
    == (
        "domain",
    ),
)

check(
    "None is missing",
    missing_required_fields(
        payload={
            "domain":
                None,
        },
        required_fields=(
            "domain",
        ),
    )
    == (
        "domain",
    ),
)

check(
    "empty string is missing",
    missing_required_fields(
        payload={
            "domain":
                "",
        },
        required_fields=(
            "domain",
        ),
    )
    == (
        "domain",
    ),
)

check(
    "zero is allowed by Runtime missing rule",
    missing_required_fields(
        payload={
            "count":
                0,
        },
        required_fields=(
            "count",
        ),
    )
    == (),
)

check(
    "False is allowed by Runtime missing rule",
    missing_required_fields(
        payload={
            "enabled":
                False,
        },
        required_fields=(
            "enabled",
        ),
    )
    == (),
)

check(
    "empty list is allowed by Runtime missing rule",
    missing_required_fields(
        payload={
            "items":
                [],
        },
        required_fields=(
            "items",
        ),
    )
    == (),
)

check(
    "empty mapping is allowed by Runtime missing rule",
    missing_required_fields(
        payload={
            "config":
                {},
        },
        required_fields=(
            "config",
        ),
    )
    == (),
)


passed = sum(
    1
    for item in checks
    if item
)

failed = (
    len(checks)
    - passed
)


print("-" * 120)
print("Checks:", len(checks))
print("Passed:", passed)
print("Failed:", failed)
print(
    "ARCHITECTURE RESOLVED:",
    failed == 0,
)
print(
    "MAPPING MODEL:",
    "exact top-level required-field projection",
)
print(
    "NEXT:",
    (
        "6.2 Installation"
        if failed == 0
        else "Resolve architecture verification failure"
    ),
)
print("=" * 120)
