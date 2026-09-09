from __future__ import annotations

import copy
import hashlib
import inspect
import json
from pathlib import Path

from backend.server.coordination.stage_handoff.stage_result_processor import (
    ProcessedStageResult,
    StageResultDisposition,
    StageResultProcessorError,
    STAGE_RESULT_PROCESSOR_SCHEMA_VERSION,
    STAGE_RESULT_PROCESSOR_VERSION,
    process_stage_result,
)

from backend.server.coordination.universal_stages.result_contract import (
    UniversalStageResult,
    UniversalStageResultStatus,
)

from backend.server.coordination.universal_stages.contract import (
    StageExecutionTarget,
)


TARGET = Path(
    "backend/server/coordination/stage_handoff/stage_result_processor.py"
)

print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 6.1 — STAGE RESULT PROCESSOR INITIAL VERIFICATION")
print("=" * 120)

checks = []


def check(name, condition):
    ok = bool(condition)
    checks.append(ok)
    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


def sha256(path):
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


source_sha_before = sha256(
    TARGET
)

check(
    "processor source exists",
    TARGET.exists(),
)

check(
    "processor version exact",
    STAGE_RESULT_PROCESSOR_VERSION
    == "stage_result_processor_v6.1.0",
)

check(
    "processor schema exact",
    STAGE_RESULT_PROCESSOR_SCHEMA_VERSION
    == "stage_result_processor_schema_v1",
)

check(
    "disposition enum exact",
    tuple(
        x.value
        for x in StageResultDisposition
    )
    == (
        "completed",
        "failed",
        "skipped",
        "cancelled",
    ),
)


def make_result(
    *,
    status,
    suffix,
    output=None,
    artifacts=None,
    metadata=None,
    failure_code=None,
    failure_message=None,
    failure_details=None,
):

    failed = (
        status
        == UniversalStageResultStatus.FAILED
    )

    if output is None:
        output = {
            "alpha": 1,
            "nested": {
                "beta": [
                    "x",
                    "y",
                ],
            },
            "suffix": suffix,
        }

    if artifacts is None:
        artifacts = (
            "artifact://alpha",
            "artifact://beta",
            "artifact://gamma",
        )

    if metadata is None:
        metadata = {
            "coordination": {
                "workflow_id":
                    "wf_phase_6_1_initial",
                "stage_id":
                    f"stage_{suffix}",
            },
            "flags": [
                "one",
                "two",
            ],
        }

    if failure_code is None:
        failure_code = (
            "initial_failure"
            if failed
            else ""
        )

    if failure_message is None:
        failure_message = (
            "deterministic failure"
            if failed
            else ""
        )

    if failure_details is None:
        failure_details = (
            {
                "attempt":
                    3,
                "retry_exhausted":
                    True,
                "nested":
                    {
                        "error_type":
                            "RuntimeError",
                    },
            }
            if failed
            else {}
        )

    return UniversalStageResult(
        result_id=
            f"usr_phase_6_1_initial_{suffix}",

        workflow_id=
            "wf_phase_6_1_initial",

        correlation_id=
            "corr_phase_6_1_initial",

        stage_id=
            f"stage_{suffix}",

        stage_version=
            "2.5.7",

        pipeline_id=
            "phase_6_1_initial_pipeline",

        workflow_type=
            "phase_6_1_initial_workflow",

        workspace_id=
            "ws_phase_6_1_initial",

        execution_target=
            StageExecutionTarget.UNIVERSAL_RUNTIME,

        job_id=
            f"uj_phase_6_1_initial_{suffix}",

        job_type=
            "linking_target_pipeline_batch",

        status=
            status,

        output=
            output,

        result_reference=
            f"result://phase-6-1/initial/{suffix}",

        artifact_references=
            tuple(
                artifacts
            ),

        started_at=
            "2026-09-09T04:10:00+00:00",

        finished_at=
            "2026-09-09T04:11:00+00:00",

        failure_code=
            failure_code,

        failure_message=
            failure_message,

        failure_details=
            failure_details,

        metadata=
            metadata,
    )


truth_table = {
    UniversalStageResultStatus.COMPLETED: (
        StageResultDisposition.COMPLETED,
        True,
        True,
    ),
    UniversalStageResultStatus.FAILED: (
        StageResultDisposition.FAILED,
        False,
        False,
    ),
    UniversalStageResultStatus.SKIPPED: (
        StageResultDisposition.SKIPPED,
        False,
        False,
    ),
    UniversalStageResultStatus.CANCELLED: (
        StageResultDisposition.CANCELLED,
        False,
        False,
    ),
}


for status, expected in truth_table.items():

    disposition_expected, handoff_expected, prerequisite_expected = expected

    suffix = status.value

    source = make_result(
        status=status,
        suffix=suffix,
    )

    source_before = copy.deepcopy(
        source.to_dict()
    )

    validation = source.validate()

    source_valid = getattr(
        validation,
        "valid",
        getattr(
            validation,
            "is_valid",
            False,
        ),
    )

    check(
        f"{suffix}: source validates",
        source_valid,
    )

    processed = process_stage_result(
        source
    )

    check(
        f"{suffix}: result type exact",
        isinstance(
            processed,
            ProcessedStageResult,
        ),
    )

    check(
        f"{suffix}: disposition exact",
        processed.disposition
        == disposition_expected,
    )

    check(
        f"{suffix}: handoff truth table",
        processed.normal_handoff_allowed
        is handoff_expected,
    )

    check(
        f"{suffix}: prerequisite truth table",
        processed.prerequisite_satisfied
        is prerequisite_expected,
    )

    check(
        f"{suffix}: terminal true",
        processed.terminal is True,
    )

    check(
        f"{suffix}: result identity preserved",
        processed.result_id
        == source.result_id,
    )

    check(
        f"{suffix}: workflow identity preserved",
        (
            processed.workflow_id
            == source.workflow_id
            and processed.correlation_id
            == source.correlation_id
            and processed.workspace_id
            == source.workspace_id
        ),
    )

    check(
        f"{suffix}: stage identity preserved",
        (
            processed.stage_id
            == source.stage_id
            and processed.stage_version
            == source.stage_version
            and processed.pipeline_id
            == source.pipeline_id
            and processed.workflow_type
            == source.workflow_type
        ),
    )

    check(
        f"{suffix}: job identity preserved",
        (
            processed.job_id
            == source.job_id
            and processed.job_type
            == source.job_type
        ),
    )

    check(
        f"{suffix}: output exact",
        processed.to_dict()["output"]
        == source.to_dict()["output"],
    )

    check(
        f"{suffix}: result reference exact",
        processed.result_reference
        == source.result_reference,
    )

    check(
        f"{suffix}: artifact ordering preserved",
        processed.artifact_references
        == tuple(
            source.artifact_references
        ),
    )

    check(
        f"{suffix}: failure code preserved",
        processed.failure_code
        == source.failure_code,
    )

    check(
        f"{suffix}: failure message preserved",
        processed.failure_message
        == source.failure_message,
    )

    check(
        f"{suffix}: failure details preserved",
        processed.to_dict()["failure_details"]
        == source.to_dict()["failure_details"],
    )

    check(
        f"{suffix}: metadata preserved",
        processed.to_dict()["metadata"]
        == source.to_dict()["metadata"],
    )

    check(
        f"{suffix}: source contract version preserved",
        processed.source_result_contract_version
        == source.contract_version,
    )

    check(
        f"{suffix}: processor version attached",
        processed.processor_version
        == STAGE_RESULT_PROCESSOR_VERSION,
    )

    check(
        f"{suffix}: schema version attached",
        processed.schema_version
        == STAGE_RESULT_PROCESSOR_SCHEMA_VERSION,
    )

    source_after = source.to_dict()

    check(
        f"{suffix}: source object unchanged",
        source_before
        == source_after,
    )

    serial_a = processed.to_dict()
    serial_b = processed.to_dict()

    check(
        f"{suffix}: deterministic serialization",
        serial_a
        == serial_b,
    )

    canonical_json_a = json.dumps(
        serial_a,
        sort_keys=True,
        separators=(",", ":"),
    )

    canonical_json_b = json.dumps(
        serial_b,
        sort_keys=True,
        separators=(",", ":"),
    )

    check(
        f"{suffix}: deterministic canonical JSON",
        canonical_json_a
        == canonical_json_b,
    )


# ------------------------------------------------------------------
# IMMUTABILITY DEEP CHECK
# ------------------------------------------------------------------

deep_source = make_result(
    status=
        UniversalStageResultStatus.COMPLETED,

    suffix=
        "deep_immutability",

    output={
        "nested": {
            "list": [
                {
                    "value": 1,
                },
                {
                    "value": 2,
                },
            ],
        },
    },

    metadata={
        "nested": {
            "flags": [
                "a",
                "b",
            ],
        },
    },
)

deep_processed = process_stage_result(
    deep_source
)

deep_output_immutable = False

try:
    deep_processed.output[
        "nested"
    ][
        "list"
    ][
        0
    ][
        "value"
    ] = 999
except (
    TypeError,
    AttributeError,
):
    deep_output_immutable = True

check(
    "deep nested output immutable",
    deep_output_immutable,
)

deep_metadata_immutable = False

try:
    deep_processed.metadata[
        "nested"
    ][
        "flags"
    ] += (
        "c",
    )
except (
    TypeError,
    AttributeError,
):
    deep_metadata_immutable = True

check(
    "deep nested metadata immutable",
    deep_metadata_immutable,
)


# ------------------------------------------------------------------
# INVALID INPUT GUARDS
# ------------------------------------------------------------------

invalid_inputs = (
    None,
    {},
    [],
    "completed",
    123,
)

for index, invalid in enumerate(
    invalid_inputs,
    start=1,
):

    rejected = False

    try:
        process_stage_result(
            invalid
        )
    except StageResultProcessorError:
        rejected = True

    check(
        f"invalid input {index} rejected",
        rejected,
    )


# ------------------------------------------------------------------
# OWNERSHIP / BOUNDARY CHECKS
# ------------------------------------------------------------------

source_text = TARGET.read_text(
    encoding="utf-8"
)

for forbidden in (
    "submit_universal_job(",
    "run_one_universal_runtime_job_v1(",
    "mark_job_completed(",
    "mark_job_failed(",
    "dequeue_job(",
    "create_orchestration_job(",
):

    check(
        f"forbidden Runtime call absent: {forbidden}",
        forbidden not in source_text,
    )


check(
    "no coordinator execution methods defined",
    all(
        name not in vars(
            ProcessedStageResult
        )
        for name in (
            "advance",
            "stage_completed",
            "stage_failed",
            "start",
            "recover",
            "cancel",
        )
    ),
)

check(
    "processor API signature stable",
    str(
        inspect.signature(
            process_stage_result
        )
    )
    == "(result: 'UniversalStageResult') -> 'ProcessedStageResult'",
)


# ------------------------------------------------------------------
# SOURCE INTEGRITY
# ------------------------------------------------------------------

source_sha_after = sha256(
    TARGET
)

check(
    "processor source unchanged during verification",
    source_sha_before
    == source_sha_after,
)


passed = sum(
    1
    for item in checks
    if item
)

failed = len(
    checks
) - passed

print("-" * 120)
print("Checks:", len(checks))
print("Passed:", passed)
print("Failed:", failed)
print(
    "INITIAL VERIFICATION PASSED:",
    failed == 0,
)
print(
    "PROCESSOR SHA256:",
    source_sha_after,
)
print(
    "NEXT:",
    (
        "6.1 Final Certification"
        if failed == 0
        else "Diagnose Initial Verification failure"
    ),
)
print("=" * 120)
