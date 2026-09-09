from __future__ import annotations

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

EXPECTED_SHA256 = (
    "8106D844B0B4D1C4D4E3A07A6232F4796010C604F538ED0F8E45F823D2C64456"
)

REPORT = Path(
    "stage_result_processor_phase_6_1_final_certification.txt"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


checks = []


def check(name, condition):
    ok = bool(condition)
    checks.append((name, ok))
    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )


print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 6.1 — STAGE RESULT PROCESSOR FINAL CERTIFICATION")
print("=" * 120)


# ------------------------------------------------------------------
# SOURCE AUTHORITY
# ------------------------------------------------------------------

check(
    "processor source exists",
    TARGET.exists(),
)

actual_sha = sha256(
    TARGET
)

check(
    "processor SHA256 exact",
    actual_sha == EXPECTED_SHA256,
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


# ------------------------------------------------------------------
# CANONICAL STATUS MODEL
# ------------------------------------------------------------------

expected_statuses = (
    "completed",
    "failed",
    "skipped",
    "cancelled",
)

check(
    "canonical result status set exact",
    tuple(
        item.value
        for item in UniversalStageResultStatus
    )
    == expected_statuses,
)

check(
    "processor disposition set exact",
    tuple(
        item.value
        for item in StageResultDisposition
    )
    == expected_statuses,
)


# ------------------------------------------------------------------
# FACTORY
# ------------------------------------------------------------------

def make_result(
    status,
    suffix,
):

    failed = (
        status
        == UniversalStageResultStatus.FAILED
    )

    return UniversalStageResult(
        result_id=
            f"usr_phase_6_1_final_{suffix}",

        workflow_id=
            "wf_phase_6_1_final",

        correlation_id=
            "corr_phase_6_1_final",

        stage_id=
            f"stage_{suffix}",

        stage_version=
            "6.1.0",

        pipeline_id=
            "phase_6_1_final_pipeline",

        workflow_type=
            "phase_6_1_final_workflow",

        workspace_id=
            "ws_phase_6_1_final",

        execution_target=
            StageExecutionTarget.UNIVERSAL_RUNTIME,

        job_id=
            f"uj_phase_6_1_final_{suffix}",

        job_type=
            "linking_target_pipeline_batch",

        status=
            status,

        output=
            {
                "terminal_status":
                    status.value,

                "payload":
                    {
                        "suffix":
                            suffix,

                        "sequence":
                            [
                                1,
                                2,
                                3,
                            ],
                    },
            },

        result_reference=
            f"result://phase-6-1/final/{suffix}",

        artifact_references=
            (
                f"artifact://phase-6-1/final/{suffix}/a",
                f"artifact://phase-6-1/final/{suffix}/b",
            ),

        started_at=
            "2026-09-09T04:20:00+00:00",

        finished_at=
            "2026-09-09T04:21:00+00:00",

        failure_code=
            (
                "phase_6_1_final_failure"
                if failed
                else ""
            ),

        failure_message=
            (
                "deterministic terminal failure"
                if failed
                else ""
            ),

        failure_details=
            (
                {
                    "attempt_count":
                        3,

                    "retry_exhausted":
                        True,

                    "error_type":
                        "RuntimeError",
                }
                if failed
                else {}
            ),

        metadata=
            {
                "certification":
                    "phase_6_1_final",

                "source":
                    "UniversalStageResult",
            },
    )


truth = {
    UniversalStageResultStatus.COMPLETED:
        (
            StageResultDisposition.COMPLETED,
            True,
            True,
        ),

    UniversalStageResultStatus.FAILED:
        (
            StageResultDisposition.FAILED,
            False,
            False,
        ),

    UniversalStageResultStatus.SKIPPED:
        (
            StageResultDisposition.SKIPPED,
            False,
            False,
        ),

    UniversalStageResultStatus.CANCELLED:
        (
            StageResultDisposition.CANCELLED,
            False,
            False,
        ),
}


for status, (
    expected_disposition,
    expected_handoff,
    expected_prerequisite,
) in truth.items():

    suffix = status.value

    source = make_result(
        status,
        suffix,
    )

    validation = source.validate()

    valid = getattr(
        validation,
        "valid",
        getattr(
            validation,
            "is_valid",
            False,
        ),
    )

    check(
        f"{suffix}: canonical source valid",
        valid,
    )

    before = json.dumps(
        source.to_dict(),
        sort_keys=True,
        separators=(",", ":"),
    )

    processed = process_stage_result(
        source
    )

    after = json.dumps(
        source.to_dict(),
        sort_keys=True,
        separators=(",", ":"),
    )

    check(
        f"{suffix}: ProcessedStageResult exact",
        isinstance(
            processed,
            ProcessedStageResult,
        ),
    )

    check(
        f"{suffix}: disposition exact",
        processed.disposition
        == expected_disposition,
    )

    check(
        f"{suffix}: normal handoff exact",
        processed.normal_handoff_allowed
        is expected_handoff,
    )

    check(
        f"{suffix}: prerequisite exact",
        processed.prerequisite_satisfied
        is expected_prerequisite,
    )

    check(
        f"{suffix}: terminal",
        processed.terminal is True,
    )

    check(
        f"{suffix}: workflow identity exact",
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
        f"{suffix}: stage identity exact",
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
        f"{suffix}: job identity exact",
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
        f"{suffix}: artifact references exact",
        list(
            processed.artifact_references
        )
        == list(
            source.artifact_references
        ),
    )

    check(
        f"{suffix}: failure evidence exact",
        (
            processed.failure_code
            == source.failure_code
            and processed.failure_message
            == source.failure_message
            and processed.to_dict()["failure_details"]
            == source.to_dict()["failure_details"]
        ),
    )

    check(
        f"{suffix}: metadata exact",
        processed.to_dict()["metadata"]
        == source.to_dict()["metadata"],
    )

    check(
        f"{suffix}: source contract version exact",
        processed.source_result_contract_version
        == source.contract_version,
    )

    check(
        f"{suffix}: source object unchanged",
        before == after,
    )

    serial_1 = json.dumps(
        processed.to_dict(),
        sort_keys=True,
        separators=(",", ":"),
    )

    serial_2 = json.dumps(
        processed.to_dict(),
        sort_keys=True,
        separators=(",", ":"),
    )

    check(
        f"{suffix}: deterministic processed serialization",
        serial_1 == serial_2,
    )


# ------------------------------------------------------------------
# API / OWNERSHIP BOUNDARY
# ------------------------------------------------------------------

check(
    "process_stage_result signature exact",
    str(
        inspect.signature(
            process_stage_result
        )
    )
    == "(result: 'UniversalStageResult') -> 'ProcessedStageResult'",
)

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
):

    check(
        f"forbidden execution surface absent: {forbidden}",
        forbidden not in source_text,
    )


# ------------------------------------------------------------------
# INVALID INPUT
# ------------------------------------------------------------------

try:
    process_stage_result(
        object()
    )
except StageResultProcessorError:
    invalid_rejected = True
else:
    invalid_rejected = False

check(
    "non-canonical input rejected",
    invalid_rejected,
)


# ------------------------------------------------------------------
# IMMUTABILITY
# ------------------------------------------------------------------

immutability_source = make_result(
    UniversalStageResultStatus.COMPLETED,
    "immutability",
)

immutability_processed = process_stage_result(
    immutability_source
)

try:
    immutability_processed.output[
        "payload"
    ][
        "sequence"
    ][
        0
    ] = 999
except (
    TypeError,
    AttributeError,
):
    deep_immutable = True
else:
    deep_immutable = False

check(
    "processed output deeply immutable",
    deep_immutable,
)


# ------------------------------------------------------------------
# SOURCE INTEGRITY AFTER CERTIFICATION
# ------------------------------------------------------------------

check(
    "processor source unchanged",
    sha256(
        TARGET
    )
    == EXPECTED_SHA256,
)


passed = sum(
    1
    for _, ok in checks
    if ok
)

failed = len(
    checks
) - passed

certified = (
    failed == 0
)


report_lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 6.1 — STAGE RESULT PROCESSOR FINAL CERTIFICATION",
    "",
    f"Checks: {len(checks)}",
    f"Passed: {passed}",
    f"Failed: {failed}",
    f"FINAL CERTIFIED: {certified}",
    "",
    f"Processor Version: {STAGE_RESULT_PROCESSOR_VERSION}",
    f"Schema Version: {STAGE_RESULT_PROCESSOR_SCHEMA_VERSION}",
    f"Processor SHA256: {actual_sha}",
    "",
    "Certified semantics:",
    "- COMPLETED -> normal_handoff_allowed=True, prerequisite_satisfied=True",
    "- FAILED -> normal_handoff_allowed=False, prerequisite_satisfied=False",
    "- SKIPPED -> normal_handoff_allowed=False, prerequisite_satisfied=False",
    "- CANCELLED -> normal_handoff_allowed=False, prerequisite_satisfied=False",
    "",
    "Certified boundaries:",
    "- no Runtime submission or worker execution",
    "- no orchestration job mutation",
    "- no coordinator invocation",
    "- no workflow lifecycle mutation",
    "- no output-to-input mapping",
    "- no context propagation",
    "- no artifact handoff",
    "- no advanced skip semantics",
    "",
    "NEXT: 6.1 SHA256 Freeze"
    if certified
    else "NEXT: Diagnose final certification failure",
]

REPORT.write_text(
    "\n".join(
        report_lines
    ) + "\n",
    encoding="utf-8",
)

report_sha = sha256(
    REPORT
)


print("-" * 120)
print("Checks:", len(checks))
print("Passed:", passed)
print("Failed:", failed)
print(
    "FINAL CERTIFIED:",
    certified,
)
print(
    "PROCESSOR SHA256:",
    actual_sha,
)
print(
    "REPORT:",
    REPORT,
)
print(
    "REPORT SHA256:",
    report_sha,
)
print(
    "NEXT:",
    (
        "6.1 SHA256 Freeze"
        if certified
        else "Diagnose final certification failure"
    ),
)
print("=" * 120)
