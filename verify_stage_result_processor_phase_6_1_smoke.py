from __future__ import annotations

import py_compile
from pathlib import Path

TARGET = Path(
    "backend/server/coordination/stage_handoff/stage_result_processor.py"
)

print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 6.1 — STAGE RESULT PROCESSOR SMOKE VERIFICATION")
print("=" * 120)

checks = []

def check(name, condition):
    ok = bool(condition)
    checks.append(ok)
    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

# ------------------------------------------------------------------
# 1. SOURCE / COMPILE / IMPORT
# ------------------------------------------------------------------

check(
    "processor source exists",
    TARGET.exists(),
)

py_compile.compile(
    str(TARGET),
    doraise=True,
)

check(
    "processor compiles",
    True,
)

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

from backend.server.coordination.universal_stages.contract import StageExecutionTarget

check(
    "processor version",
    STAGE_RESULT_PROCESSOR_VERSION
    == "stage_result_processor_v6.1.0",
)

check(
    "processor schema version",
    STAGE_RESULT_PROCESSOR_SCHEMA_VERSION
    == "stage_result_processor_schema_v1",
)

check(
    "four dispositions",
    {
        item.value
        for item in StageResultDisposition
    }
    == {
        "completed",
        "failed",
        "skipped",
        "cancelled",
    },
)

# ------------------------------------------------------------------
# 2. INVALID INPUT GUARD
# ------------------------------------------------------------------

try:
    process_stage_result(
        {"status": "completed"}
    )
except StageResultProcessorError:
    invalid_rejected = True
else:
    invalid_rejected = False

check(
    "non-UniversalStageResult rejected",
    invalid_rejected,
)

# ------------------------------------------------------------------
# 3. BUILD CANONICAL TEST RESULTS
# ------------------------------------------------------------------

execution_target = (
    StageExecutionTarget.UNIVERSAL_RUNTIME
)

def make_result(
    *,
    status,
    suffix,
):
    failure = (
        status
        == UniversalStageResultStatus.FAILED
    )

    return UniversalStageResult(
        result_id=
            f"usr_phase_6_1_smoke_{suffix}",

        workflow_id=
            "wf_phase_6_1_smoke",

        correlation_id=
            "corr_phase_6_1_smoke",

        stage_id=
            f"stage_{suffix}",

        stage_version=
            "1.0.0",

        pipeline_id=
            "phase_6_1_smoke_pipeline",

        workflow_type=
            "phase_6_1_smoke_workflow",

        workspace_id=
            "ws_phase_6_1_smoke",

        execution_target=
            execution_target,

        job_id=
            f"uj_phase_6_1_smoke_{suffix}",

        job_type=
            "phase_6_1_smoke_job",

        status=
            status,

        output=
            {
                "status":
                    status.value,

                "nested":
                    {
                        "value":
                            suffix,
                    },
            },

        result_reference=
            f"result://phase-6-1/{suffix}",

        artifact_references=
            (
                f"artifact://phase-6-1/{suffix}",
            ),

        started_at=
            "2026-09-09T04:00:00+00:00",

        finished_at=
            "2026-09-09T04:01:00+00:00",

        failure_code=
            (
                "phase_6_1_smoke_failure"
                if failure
                else ""
            ),

        failure_message=
            (
                "deterministic smoke failure"
                if failure
                else ""
            ),

        failure_details=
            (
                {
                    "source":
                        "phase_6_1_smoke",
                }
                if failure
                else {}
            ),

        metadata=
            {
                "certification":
                    "phase_6_1_smoke",

                "suffix":
                    suffix,
            },
    )


cases = (
    (
        UniversalStageResultStatus.COMPLETED,
        StageResultDisposition.COMPLETED,
        True,
        True,
        "completed",
    ),
    (
        UniversalStageResultStatus.FAILED,
        StageResultDisposition.FAILED,
        False,
        False,
        "failed",
    ),
    (
        UniversalStageResultStatus.SKIPPED,
        StageResultDisposition.SKIPPED,
        False,
        False,
        "skipped",
    ),
    (
        UniversalStageResultStatus.CANCELLED,
        StageResultDisposition.CANCELLED,
        False,
        False,
        "cancelled",
    ),
)

for (
    status,
    expected_disposition,
    expected_handoff,
    expected_prerequisite,
    suffix,
) in cases:

    source = make_result(
        status=status,
        suffix=suffix,
    )

    source_validation = (
        source.validate()
    )

    source_valid = getattr(
        source_validation,
        "valid",
        getattr(
            source_validation,
            "is_valid",
            False,
        ),
    )

    check(
        f"{suffix}: canonical source validates",
        source_valid,
    )

    processed = process_stage_result(
        source
    )

    check(
        f"{suffix}: returns ProcessedStageResult",
        isinstance(
            processed,
            ProcessedStageResult,
        ),
    )

    check(
        f"{suffix}: disposition",
        processed.disposition
        == expected_disposition,
    )

    check(
        f"{suffix}: terminal",
        processed.terminal is True,
    )

    check(
        f"{suffix}: normal handoff flag",
        processed.normal_handoff_allowed
        is expected_handoff,
    )

    check(
        f"{suffix}: prerequisite flag",
        processed.prerequisite_satisfied
        is expected_prerequisite,
    )

    check(
        f"{suffix}: workflow identity preserved",
        processed.workflow_id
        == source.workflow_id
        and processed.correlation_id
        == source.correlation_id
        and processed.stage_id
        == source.stage_id,
    )

    check(
        f"{suffix}: job identity preserved",
        processed.job_id
        == source.job_id
        and processed.job_type
        == source.job_type,
    )

    check(
        f"{suffix}: output preserved",
        processed.to_dict()["output"]
        == dict(
            source.to_dict()["output"]
        ),
    )

    check(
        f"{suffix}: artifact reference preserved",
        processed.artifact_references
        == tuple(
            source.artifact_references
        ),
    )

    check(
        f"{suffix}: contract version preserved",
        processed.source_result_contract_version
        == source.contract_version,
    )

# ------------------------------------------------------------------
# 4. MUTABILITY / OWNERSHIP BOUNDARY
# ------------------------------------------------------------------

completed_source = make_result(
    status=
        UniversalStageResultStatus.COMPLETED,

    suffix=
        "immutability",
)

completed_processed = process_stage_result(
    completed_source
)

try:
    completed_processed.output[
        "mutation"
    ] = True
except TypeError:
    immutable_output = True
else:
    immutable_output = False

check(
    "processed output is immutable",
    immutable_output,
)

check(
    "processor performs no coordinator invocation surface",
    not hasattr(
        completed_processed,
        "advance",
    )
    and not hasattr(
        completed_processed,
        "stage_completed",
    )
    and not hasattr(
        completed_processed,
        "stage_failed",
    ),
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
        "6.1 Initial Verification"
        if failed == 0
        else "Diagnose smoke failure before proceeding"
    ),
)
print("=" * 120)



