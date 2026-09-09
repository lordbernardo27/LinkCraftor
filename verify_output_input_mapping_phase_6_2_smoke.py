from __future__ import annotations

import py_compile
from pathlib import Path

from backend.server.coordination.stage_handoff.output_input_mapping import (
    OUTPUT_INPUT_MAPPING_SCHEMA_VERSION,
    OUTPUT_INPUT_MAPPING_VERSION,
    OutputInputMappingError,
    OutputInputMappingResult,
    map_output_to_input,
)

from backend.server.coordination.stage_handoff.stage_result_processor import (
    process_stage_result,
)

from backend.server.coordination.universal_stages.contract import (
    StageExecutionTarget,
    UniversalStageReference,
)

from backend.server.coordination.universal_stages.result_contract import (
    UniversalStageResult,
    UniversalStageResultStatus,
)


TARGET = Path(
    "backend/server/coordination/stage_handoff/output_input_mapping.py"
)


print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 6.2 — OUTPUT -> INPUT MAPPING SMOKE VERIFICATION")
print("=" * 120)


checks = []


def check(name, condition):
    ok = bool(condition)
    checks.append(ok)
    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


# ------------------------------------------------------------------
# SOURCE / COMPILE / VERSION
# ------------------------------------------------------------------

check(
    "mapper source exists",
    TARGET.exists(),
)

py_compile.compile(
    str(TARGET),
    doraise=True,
)

check(
    "mapper compiles",
    True,
)

check(
    "mapper version exact",
    OUTPUT_INPUT_MAPPING_VERSION
    == "output_input_mapping_v6.2.0",
)

check(
    "mapper schema exact",
    OUTPUT_INPUT_MAPPING_SCHEMA_VERSION
    == "output_input_mapping_schema_v1",
)


# ------------------------------------------------------------------
# CANONICAL FACTORIES
# ------------------------------------------------------------------

def make_processed_source(
    *,
    status=
        UniversalStageResultStatus.COMPLETED,
    suffix=
        "source",
    output=None,
):

    if output is None:
        output = {
            "workspace_id":
                "ws_phase_6_2",

            "domain":
                "example.com",

            "count":
                0,

            "enabled":
                False,

            "items":
                [],

            "config":
                {},

            "extra":
                "must-not-be-projected",
        }

    failed = (
        status
        == UniversalStageResultStatus.FAILED
    )

    result = UniversalStageResult(
        result_id=
            f"usr_phase_6_2_smoke_{suffix}",

        workflow_id=
            "wf_phase_6_2_smoke",

        correlation_id=
            "corr_phase_6_2_smoke",

        stage_id=
            f"source_stage_{suffix}",

        stage_version=
            "1.0.0",

        pipeline_id=
            "phase_6_2_smoke_pipeline",

        workflow_type=
            "phase_6_2_smoke_workflow",

        workspace_id=
            "ws_phase_6_2",

        execution_target=
            StageExecutionTarget.UNIVERSAL_RUNTIME,

        job_id=
            f"uj_phase_6_2_smoke_{suffix}",

        job_type=
            "linking_target_pipeline_batch",

        status=
            status,

        output=
            output,

        result_reference=
            f"result://phase-6-2/{suffix}",

        artifact_references=
            (
                f"artifact://phase-6-2/{suffix}",
            ),

        started_at=
            "2026-09-09T04:25:00+00:00",

        finished_at=
            "2026-09-09T04:26:00+00:00",

        failure_code=
            (
                "phase_6_2_failure"
                if failed
                else ""
            ),

        failure_message=
            (
                "deterministic failure"
                if failed
                else ""
            ),

        failure_details=
            (
                {
                    "source":
                        "phase_6_2_smoke",
                }
                if failed
                else {}
            ),

        metadata=
            {
                "certification":
                    "phase_6_2_smoke",
            },
    )

    return process_stage_result(
        result
    )


def make_target(
    *,
    suffix,
    required_fields,
    execution_target=
        StageExecutionTarget.UNIVERSAL_RUNTIME,
):

    runtime = (
        execution_target
        == StageExecutionTarget.UNIVERSAL_RUNTIME
    )

    return UniversalStageReference(
        stage_id=
            f"target_stage_{suffix}",

        stage_version=
            "1.0.0",

        pipeline_id=
            "phase_6_2_smoke_pipeline",

        workflow_type=
            "phase_6_2_smoke_workflow",

        workflow_contract_version=
            "universal_workflow_contract_v1.1.0",

        execution_target=
            execution_target,

        job_type=
            (
                "linking_target_pipeline_batch"
                if runtime
                else ""
            ),

        runtime_stage=
            (
                f"target_stage_{suffix}"
                if runtime
                else ""
            ),

        required_payload_fields=
            tuple(
                required_fields
            ),
    )


# ------------------------------------------------------------------
# COMPLETE EXACT-NAME PROJECTION
# ------------------------------------------------------------------

source = make_processed_source(
    suffix=
        "complete",
)

target = make_target(
    suffix=
        "complete",
    required_fields=(
        "workspace_id",
        "domain",
    ),
)

mapped = map_output_to_input(
    source,
    target,
)

check(
    "complete mapping returns OutputInputMappingResult",
    isinstance(
        mapped,
        OutputInputMappingResult,
    ),
)

check(
    "complete mapping marked complete",
    mapped.complete is True,
)

check(
    "required field ordering preserved",
    mapped.required_payload_fields
    == (
        "workspace_id",
        "domain",
    ),
)

check(
    "satisfied field ordering preserved",
    mapped.satisfied_payload_fields
    == (
        "workspace_id",
        "domain",
    ),
)

check(
    "complete mapping has no missing fields",
    mapped.missing_payload_fields
    == (),
)

check(
    "payload exact required-field projection",
    mapped.to_dict()["payload"]
    == {
        "workspace_id":
            "ws_phase_6_2",

        "domain":
            "example.com",
    },
)

check(
    "extra upstream fields excluded",
    "extra"
    not in mapped.payload,
)

check(
    "source result identity preserved",
    (
        mapped.source_result_id
        == source.result_id
        and mapped.source_workflow_id
        == source.workflow_id
        and mapped.source_correlation_id
        == source.correlation_id
        and mapped.source_stage_id
        == source.stage_id
    ),
)

check(
    "target stage identity preserved",
    (
        mapped.target_stage_id
        == target.stage_id
        and mapped.target_stage_version
        == target.stage_version
        and mapped.target_pipeline_id
        == target.pipeline_id
        and mapped.target_workflow_type
        == target.workflow_type
    ),
)


# ------------------------------------------------------------------
# PARTIAL / MISSING FIELD MAPPING
# ------------------------------------------------------------------

partial_source = make_processed_source(
    suffix=
        "partial",

    output={
        "workspace_id":
            "ws_phase_6_2",

        "domain":
            None,

        "url":
            "",
    },
)

partial_target = make_target(
    suffix=
        "partial",

    required_fields=(
        "workspace_id",
        "domain",
        "url",
        "language",
    ),
)

partial = map_output_to_input(
    partial_source,
    partial_target,
)

check(
    "partial mapping marked incomplete",
    partial.complete is False,
)

check(
    "partial mapping satisfied fields exact",
    partial.satisfied_payload_fields
    == (
        "workspace_id",
    ),
)

check(
    "absent/None/empty-string fields reported missing",
    partial.missing_payload_fields
    == (
        "domain",
        "url",
        "language",
    ),
)

check(
    "missing values not inserted into mapped payload",
    partial.to_dict()["payload"]
    == {
        "workspace_id":
            "ws_phase_6_2",
    },
)


# ------------------------------------------------------------------
# RUNTIME-COMPATIBLE FALSEY VALUES
# ------------------------------------------------------------------

falsey_target = make_target(
    suffix=
        "falsey",

    required_fields=(
        "count",
        "enabled",
        "items",
        "config",
    ),
)

falsey = map_output_to_input(
    source,
    falsey_target,
)

check(
    "0 False empty-list empty-map satisfy requirements",
    falsey.complete is True,
)

check(
    "falsey fields all satisfied",
    falsey.satisfied_payload_fields
    == (
        "count",
        "enabled",
        "items",
        "config",
    ),
)

check(
    "falsey mapped payload exact",
    falsey.to_dict()["payload"]
    == {
        "count":
            0,

        "enabled":
            False,

        "items":
            [],

        "config":
            {},
    },
)


# ------------------------------------------------------------------
# ZERO-REQUIREMENT COORDINATION-ONLY TARGET
# ------------------------------------------------------------------

coordination_target = make_target(
    suffix=
        "coordination_only",

    required_fields=
        (),

    execution_target=
        StageExecutionTarget.COORDINATION_ONLY,
)

coordination_mapping = map_output_to_input(
    source,
    coordination_target,
)

check(
    "coordination-only empty requirement mapping complete",
    coordination_mapping.complete is True,
)

check(
    "coordination-only payload empty",
    coordination_mapping.to_dict()["payload"]
    == {},
)

check(
    "coordination-only required fields empty",
    coordination_mapping.required_payload_fields
    == (),
)


# ------------------------------------------------------------------
# IMMUTABILITY
# ------------------------------------------------------------------

try:
    mapped.payload[
        "workspace_id"
    ] = "mutated"
except TypeError:
    immutable_payload = True
else:
    immutable_payload = False

check(
    "mapped payload immutable",
    immutable_payload,
)


# ------------------------------------------------------------------
# PROHIBITED SOURCE DISPOSITIONS
# ------------------------------------------------------------------

for status in (
    UniversalStageResultStatus.FAILED,
    UniversalStageResultStatus.SKIPPED,
    UniversalStageResultStatus.CANCELLED,
):

    prohibited_source = make_processed_source(
        status=status,
        suffix=status.value,
    )

    rejected = False

    try:
        map_output_to_input(
            prohibited_source,
            target,
        )
    except OutputInputMappingError:
        rejected = True

    check(
        f"{status.value}: normal mapping rejected",
        rejected,
    )


# ------------------------------------------------------------------
# INVALID TYPE GUARDS
# ------------------------------------------------------------------

try:
    map_output_to_input(
        {},
        target,
    )
except OutputInputMappingError:
    invalid_source_rejected = True
else:
    invalid_source_rejected = False

check(
    "invalid source type rejected",
    invalid_source_rejected,
)


try:
    map_output_to_input(
        source,
        {},
    )
except OutputInputMappingError:
    invalid_target_rejected = True
else:
    invalid_target_rejected = False

check(
    "invalid target type rejected",
    invalid_target_rejected,
)


# ------------------------------------------------------------------
# SERIALIZATION / VERSION / BOUNDARY
# ------------------------------------------------------------------

serialized_a = mapped.to_dict()
serialized_b = mapped.to_dict()

check(
    "serialization deterministic",
    serialized_a
    == serialized_b,
)

check(
    "mapper version attached",
    mapped.mapper_version
    == OUTPUT_INPUT_MAPPING_VERSION,
)

check(
    "schema version attached",
    mapped.schema_version
    == OUTPUT_INPUT_MAPPING_SCHEMA_VERSION,
)

check(
    "source processor version preserved",
    mapped.source_processor_version
    == source.processor_version,
)

check(
    "target contract version preserved",
    mapped.target_stage_reference_contract_version
    == target.contract_version,
)


source_text = TARGET.read_text(
    encoding="utf-8"
)

for forbidden in (
    "submit_universal_job(",
    "run_one_universal_runtime_job_v1(",
    "create_orchestration_job(",
    "stage_completed(",
    "stage_failed(",
    "advance(",
):

    check(
        f"forbidden execution surface absent: {forbidden}",
        forbidden not in source_text,
    )


# ------------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------------

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
    "SMOKE VERIFIED:",
    failed == 0,
)
print(
    "NEXT:",
    (
        "6.2 Initial Verification"
        if failed == 0
        else "Diagnose 6.2 smoke failure"
    ),
)
print("=" * 120)
