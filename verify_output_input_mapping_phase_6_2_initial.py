from __future__ import annotations

import copy
import hashlib
import inspect
import json
from pathlib import Path

from backend.server.coordination.stage_handoff.output_input_mapping import (
    OUTPUT_INPUT_MAPPING_SCHEMA_VERSION,
    OUTPUT_INPUT_MAPPING_VERSION,
    OutputInputMappingError,
    OutputInputMappingResult,
    map_output_to_input,
)

from backend.server.coordination.stage_handoff.stage_result_processor import (
    STAGE_RESULT_PROCESSOR_VERSION,
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


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


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
print("PHASE 6.2 — OUTPUT -> INPUT MAPPING INITIAL VERIFICATION")
print("=" * 120)


source_sha_before = sha256(
    TARGET
)


# ------------------------------------------------------------------
# STATIC AUTHORITY
# ------------------------------------------------------------------

check(
    "mapper source exists",
    TARGET.exists(),
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

check(
    "mapper API signature exact",
    str(
        inspect.signature(
            map_output_to_input
        )
    )
    == "(source: 'ProcessedStageResult', target: 'UniversalStageReference') -> 'OutputInputMappingResult'",
)


# ------------------------------------------------------------------
# FACTORIES
# ------------------------------------------------------------------

def make_source(
    *,
    suffix,
    output,
    status=
        UniversalStageResultStatus.COMPLETED,
):

    failed = (
        status
        == UniversalStageResultStatus.FAILED
    )

    canonical = UniversalStageResult(
        result_id=
            f"usr_phase_6_2_initial_{suffix}",

        workflow_id=
            "wf_phase_6_2_initial",

        correlation_id=
            "corr_phase_6_2_initial",

        stage_id=
            f"source_{suffix}",

        stage_version=
            "2.4.6",

        pipeline_id=
            "phase_6_2_initial_pipeline",

        workflow_type=
            "phase_6_2_initial_workflow",

        workspace_id=
            "ws_phase_6_2_initial",

        execution_target=
            StageExecutionTarget.UNIVERSAL_RUNTIME,

        job_id=
            f"uj_phase_6_2_initial_{suffix}",

        job_type=
            "linking_target_pipeline_batch",

        status=
            status,

        output=
            output,

        result_reference=
            f"result://phase-6-2/initial/{suffix}",

        artifact_references=
            (
                f"artifact://phase-6-2/{suffix}/a",
                f"artifact://phase-6-2/{suffix}/b",
            ),

        started_at=
            "2026-09-09T04:30:00+00:00",

        finished_at=
            "2026-09-09T04:31:00+00:00",

        failure_code=
            (
                "phase_6_2_initial_failure"
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
                    "retry_exhausted":
                        True,
                }
                if failed
                else {}
            ),

        metadata=
            {
                "verification":
                    "phase_6_2_initial",
            },
    )

    return process_stage_result(
        canonical
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
            f"target_{suffix}",

        stage_version=
            "3.7.2",

        pipeline_id=
            "phase_6_2_initial_pipeline",

        workflow_type=
            "phase_6_2_initial_workflow",

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
                f"runtime_{suffix}"
                if runtime
                else ""
            ),

        required_payload_fields=
            tuple(
                required_fields
            ),

        metadata=
            {
                "verification":
                    "phase_6_2_initial",
            },
    )


# ------------------------------------------------------------------
# FULL PROJECTION / IDENTITY
# ------------------------------------------------------------------

source = make_source(
    suffix=
        "full",

    output={
        "workspace_id":
            "ws_phase_6_2_initial",

        "domain":
            "example.com",

        "pages":
            [
                {
                    "url":
                        "/a",
                },
                {
                    "url":
                        "/b",
                },
            ],

        "count":
            0,

        "enabled":
            False,

        "settings":
            {},

        "unused":
            "must-not-flow",
    },
)

target = make_target(
    suffix=
        "full",

    required_fields=(
        "domain",
        "workspace_id",
        "pages",
        "count",
        "enabled",
        "settings",
    ),
)

source_before = copy.deepcopy(
    source.to_dict()
)

target_before = copy.deepcopy(
    target.to_dict()
)

mapped = map_output_to_input(
    source,
    target,
)


check(
    "mapping result type exact",
    isinstance(
        mapped,
        OutputInputMappingResult,
    ),
)

check(
    "complete mapping true",
    mapped.complete is True,
)

check(
    "required order exactly follows target",
    mapped.required_payload_fields
    == (
        "domain",
        "workspace_id",
        "pages",
        "count",
        "enabled",
        "settings",
    ),
)

check(
    "satisfied order exactly follows target",
    mapped.satisfied_payload_fields
    == mapped.required_payload_fields,
)

check(
    "no missing fields",
    mapped.missing_payload_fields
    == (),
)

check(
    "payload key order follows target requirements",
    tuple(
        mapped.to_dict()["payload"].keys()
    )
    == mapped.required_payload_fields,
)

check(
    "only required fields projected",
    set(
        mapped.to_dict()["payload"].keys()
    )
    == set(
        target.required_payload_fields
    ),
)

check(
    "unused source field excluded",
    "unused"
    not in mapped.payload,
)


# ------------------------------------------------------------------
# SOURCE IDENTITY PRESERVATION
# ------------------------------------------------------------------

check(
    "source result id preserved",
    mapped.source_result_id
    == source.result_id,
)

check(
    "source workflow id preserved",
    mapped.source_workflow_id
    == source.workflow_id,
)

check(
    "source correlation id preserved",
    mapped.source_correlation_id
    == source.correlation_id,
)

check(
    "source stage id preserved",
    mapped.source_stage_id
    == source.stage_id,
)

check(
    "source stage version preserved",
    mapped.source_stage_version
    == source.stage_version,
)

check(
    "source pipeline id preserved",
    mapped.source_pipeline_id
    == source.pipeline_id,
)

check(
    "source workspace id preserved",
    mapped.source_workspace_id
    == source.workspace_id,
)

check(
    "source job id preserved",
    mapped.source_job_id
    == source.job_id,
)


# ------------------------------------------------------------------
# TARGET IDENTITY PRESERVATION
# ------------------------------------------------------------------

check(
    "target stage id preserved",
    mapped.target_stage_id
    == target.stage_id,
)

check(
    "target stage version preserved",
    mapped.target_stage_version
    == target.stage_version,
)

check(
    "target pipeline id preserved",
    mapped.target_pipeline_id
    == target.pipeline_id,
)

check(
    "target workflow type preserved",
    mapped.target_workflow_type
    == target.workflow_type,
)

check(
    "target execution target preserved",
    mapped.target_execution_target
    == target.execution_target.value,
)

check(
    "target job type preserved",
    mapped.target_job_type
    == target.job_type,
)

check(
    "target runtime stage preserved",
    mapped.target_runtime_stage
    == target.runtime_stage,
)


# ------------------------------------------------------------------
# VERSION LINEAGE
# ------------------------------------------------------------------

check(
    "source processor version exact",
    mapped.source_processor_version
    == STAGE_RESULT_PROCESSOR_VERSION,
)

check(
    "target stage reference contract version preserved",
    mapped.target_stage_reference_contract_version
    == target.contract_version,
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


# ------------------------------------------------------------------
# SOURCE / TARGET NON-MUTATION
# ------------------------------------------------------------------

check(
    "source not mutated",
    source.to_dict()
    == source_before,
)

check(
    "target not mutated",
    target.to_dict()
    == target_before,
)


# ------------------------------------------------------------------
# DEEP IMMUTABILITY
# ------------------------------------------------------------------

try:
    mapped.payload[
        "pages"
    ][
        0
    ][
        "url"
    ] = "/mutated"
except (
    TypeError,
    AttributeError,
):
    nested_immutable = True
else:
    nested_immutable = False

check(
    "nested mapped payload deeply immutable",
    nested_immutable,
)


try:
    mapped.required_payload_fields += (
        "extra",
    )
except (
    AttributeError,
    TypeError,
):
    result_immutable = True
else:
    result_immutable = False

check(
    "mapping result dataclass immutable",
    result_immutable,
)


# ------------------------------------------------------------------
# TOP-LEVEL ONLY SEMANTICS
# ------------------------------------------------------------------

nested_source = make_source(
    suffix=
        "nested",

    output={
        "container":
            {
                "domain":
                    "nested.example.com",
            },
    },
)

nested_target = make_target(
    suffix=
        "nested",

    required_fields=(
        "domain",
    ),
)

nested_mapping = map_output_to_input(
    nested_source,
    nested_target,
)

check(
    "nested source value not treated as top-level match",
    nested_mapping.complete is False,
)

check(
    "nested source field reported missing",
    nested_mapping.missing_payload_fields
    == (
        "domain",
    ),
)

check(
    "nested object not implicitly traversed",
    nested_mapping.to_dict()["payload"]
    == {},
)


# ------------------------------------------------------------------
# MISSING SEMANTICS / ORDER
# ------------------------------------------------------------------

missing_source = make_source(
    suffix=
        "missing",

    output={
        "first":
            None,

        "second":
            "",

        "fourth":
            "present",

        "fifth":
            False,

        "sixth":
            0,

        "seventh":
            [],

        "eighth":
            {},
    },
)

missing_target = make_target(
    suffix=
        "missing",

    required_fields=(
        "first",
        "second",
        "third",
        "fourth",
        "fifth",
        "sixth",
        "seventh",
        "eighth",
    ),
)

missing_mapping = map_output_to_input(
    missing_source,
    missing_target,
)

check(
    "incomplete mapping false",
    missing_mapping.complete is False,
)

check(
    "missing field order exact",
    missing_mapping.missing_payload_fields
    == (
        "first",
        "second",
        "third",
    ),
)

check(
    "satisfied field order exact",
    missing_mapping.satisfied_payload_fields
    == (
        "fourth",
        "fifth",
        "sixth",
        "seventh",
        "eighth",
    ),
)

check(
    "None not projected",
    "first"
    not in missing_mapping.payload,
)

check(
    "empty string not projected",
    "second"
    not in missing_mapping.payload,
)

check(
    "absent field not projected",
    "third"
    not in missing_mapping.payload,
)

check(
    "False projected",
    missing_mapping.payload[
        "fifth"
    ]
    is False,
)

check(
    "zero projected",
    missing_mapping.payload[
        "sixth"
    ]
    == 0,
)

check(
    "empty list projected",
    missing_mapping.to_dict()["payload"][
        "seventh"
    ]
    == [],
)

check(
    "empty mapping projected",
    missing_mapping.to_dict()["payload"][
        "eighth"
    ]
    == {},
)


# ------------------------------------------------------------------
# ZERO REQUIREMENT SEMANTICS
# ------------------------------------------------------------------

empty_target = make_target(
    suffix=
        "empty",

    required_fields=
        (),

    execution_target=
        StageExecutionTarget.COORDINATION_ONLY,
)

empty_mapping = map_output_to_input(
    source,
    empty_target,
)

check(
    "zero requirements complete",
    empty_mapping.complete is True,
)

check(
    "zero requirements payload empty",
    empty_mapping.to_dict()["payload"]
    == {},
)

check(
    "zero requirements no satisfied fields",
    empty_mapping.satisfied_payload_fields
    == (),
)

check(
    "zero requirements no missing fields",
    empty_mapping.missing_payload_fields
    == (),
)


# ------------------------------------------------------------------
# PROHIBITED SOURCE DISPOSITIONS
# ------------------------------------------------------------------

for status in (
    UniversalStageResultStatus.FAILED,
    UniversalStageResultStatus.SKIPPED,
    UniversalStageResultStatus.CANCELLED,
):

    prohibited = make_source(
        suffix=
            status.value,

        output={
            "domain":
                "example.com",
        },

        status=
            status,
    )

    rejected = False

    try:
        map_output_to_input(
            prohibited,
            target,
        )
    except OutputInputMappingError:
        rejected = True

    check(
        f"{status.value}: prohibited from normal mapping",
        rejected,
    )


# ------------------------------------------------------------------
# INVALID TYPES
# ------------------------------------------------------------------

invalid_sources = (
    None,
    {},
    [],
    "completed",
    123,
)

for index, invalid in enumerate(
    invalid_sources,
    start=1,
):

    rejected = False

    try:
        map_output_to_input(
            invalid,
            target,
        )
    except OutputInputMappingError:
        rejected = True

    check(
        f"invalid source {index} rejected",
        rejected,
    )


invalid_targets = (
    None,
    {},
    [],
    "stage",
    123,
)

for index, invalid in enumerate(
    invalid_targets,
    start=1,
):

    rejected = False

    try:
        map_output_to_input(
            source,
            invalid,
        )
    except OutputInputMappingError:
        rejected = True

    check(
        f"invalid target {index} rejected",
        rejected,
    )


# ------------------------------------------------------------------
# DETERMINISM
# ------------------------------------------------------------------

serial_1 = mapped.to_dict()
serial_2 = mapped.to_dict()

check(
    "to_dict deterministic",
    serial_1
    == serial_2,
)

json_1 = json.dumps(
    serial_1,
    sort_keys=True,
    separators=(",", ":"),
)

json_2 = json.dumps(
    serial_2,
    sort_keys=True,
    separators=(",", ":"),
)

check(
    "canonical JSON deterministic",
    json_1
    == json_2,
)


repeat = map_output_to_input(
    source,
    target,
)

check(
    "repeated mapping deterministic",
    repeat.to_dict()
    == mapped.to_dict(),
)


# ------------------------------------------------------------------
# EXECUTION BOUNDARY
# ------------------------------------------------------------------

source_text = TARGET.read_text(
    encoding="utf-8"
)

for forbidden in (
    "submit_universal_job(",
    "run_one_universal_runtime_job_v1(",
    "create_orchestration_job(",
    "dequeue_job(",
    "mark_job_completed(",
    "mark_job_failed(",
    "stage_completed(",
    "stage_failed(",
    "advance(",
    "pause(",
    "resume(",
    "recover(",
):

    check(
        f"forbidden execution surface absent: {forbidden}",
        forbidden not in source_text,
    )


check(
    "no context propagation API introduced",
    "propagate_context("
    not in source_text,
)

check(
    "no artifact handoff API introduced",
    "handoff_artifact"
    not in source_text,
)

check(
    "no rename mapping semantics introduced",
    "source_field"
    not in source_text
    and "target_field"
    not in source_text,
)


# ------------------------------------------------------------------
# SOURCE INTEGRITY
# ------------------------------------------------------------------

source_sha_after = sha256(
    TARGET
)

check(
    "mapper source unchanged during verification",
    source_sha_before
    == source_sha_after,
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
    "INITIAL VERIFICATION PASSED:",
    failed == 0,
)
print(
    "MAPPER SHA256:",
    source_sha_after,
)
print(
    "NEXT:",
    (
        "6.2 Final Certification"
        if failed == 0
        else "Diagnose 6.2 Initial Verification failure"
    ),
)
print("=" * 120)
