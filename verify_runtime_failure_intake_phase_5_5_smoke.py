from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from types import MappingProxyType

from backend.server.coordination.runtime_integration.workflow_job_correlation import (
    WorkflowJobCorrelation,
    WorkflowJobCorrelationRegistry,
)

from backend.server.coordination.runtime_integration.runtime_failure_intake import (
    RUNTIME_FAILURE_INTAKE_VERSION,
    RUNTIME_FAILURE_INTAKE_SCHEMA_VERSION,
    RuntimeFailureIntakeError,
    RuntimeFailureValidationError,
    RuntimeFailureNotReadyError,
    build_runtime_failure_stage_result,
    intake_runtime_failure,
    explain_runtime_failure_intake_v5_5,
)

from backend.server.coordination.universal_stages.result_contract import (
    UniversalStageResult,
    UniversalStageResultStatus,
)


ROOT = Path.cwd()

TARGET = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "runtime_failure_intake.py"
)

PHASE_5_3 = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "workflow_job_correlation.py"
)

PHASE_5_3_MANIFEST = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "workflow_job_correlation.freeze.json"
)

PHASE_5_4 = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "runtime_completion_intake.py"
)

PHASE_5_4_MANIFEST = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "runtime_completion_intake.freeze.json"
)

STAGE_RESULT = (
    ROOT
    / "backend/server/coordination/universal_stages/"
      "result_contract.py"
)

RUNTIME_WORKER = (
    ROOT
    / "backend/server/runtime/"
      "universal_runtime_worker_v1.py"
)

REPORT = (
    ROOT
    / "runtime_failure_intake_phase_5_5_installation_smoke.txt"
)


EXPECTED = {
    "phase_5_3":
        "C0D88ECC69680106B6833DF8CB3113FC"
        "9ABD23C1EE8B7D413BA4AAE3375648FA",

    "phase_5_3_manifest":
        "53F2B149EF904CE5692D85F349038CEA"
        "B901E00B06C6C273CA5B74EB31ACE8E5",

    "phase_5_4":
        "A9F2A8E4242A08A2BDBE6AF0B96DC104"
        "2A53DDD3B2F72BB355259FA0E5D2E6FB",

    "phase_5_4_manifest":
        "CCAC1624848FA623F59DF92C9D70773C"
        "6532E6D48C956C243AD06B35FF8166DD",

    "stage_result":
        "B3469B10BB2F8F9372E4336784D09A14"
        "3C78FABE45BF039B61B76F4A2DC33B24",

    "runtime_worker":
        "ED6B415C5FEDF3F4CB62451F3E23D182"
        "F9DA937D9CB09FD33262C506B9BEF699",
}


checks = []


def check(name, condition, detail=""):
    ok = bool(condition)

    checks.append(
        (
            name,
            ok,
            detail,
        )
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if detail:
        print("    " + detail)


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def expect_validation_error(name, fn):
    try:
        fn()

    except RuntimeFailureValidationError as exc:
        check(
            name,
            True,
            str(exc),
        )
        return

    except Exception as exc:
        check(
            name,
            False,
            "Unexpected exception: " + repr(exc),
        )
        return

    check(
        name,
        False,
        "Expected RuntimeFailureValidationError.",
    )


def expect_not_ready(name, fn):
    try:
        fn()

    except RuntimeFailureNotReadyError as exc:
        check(
            name,
            True,
            str(exc),
        )
        return

    except Exception as exc:
        check(
            name,
            False,
            "Unexpected exception: " + repr(exc),
        )
        return

    check(
        name,
        False,
        "Expected RuntimeFailureNotReadyError.",
    )


def make_correlation():
    return WorkflowJobCorrelation(
        workflow_id=
            "wf_smoke_5_5",

        correlation_id=
            "corr_smoke_5_5",

        stage_id=
            "stage_failure_smoke",

        stage_version=
            "stage_failure_smoke_v1",

        workflow_type=
            "failure_smoke_workflow",

        workspace_id=
            "ws_smoke_5_5",

        job_id=
            "uj_smoke_5_5",

        job_type=
            "smoke.failure.stage",

        pipeline_id=
            "pipeline_failure_smoke",

        runtime_stage=
            "runtime_stage_failure_smoke",

        wave_index=
            2,
    )


def make_metadata():
    return {
        "worker_id":
            "worker_smoke",

        "runtime_worker_version":
            "universal_runtime_worker_v1",

        "runtime_dispatch_completed":
            False,

        "runtime_dispatch_failed":
            True,

        "runtime_retry_scheduled":
            False,

        "runtime_failure_attempt_count":
            3,

        "runtime_maximum_attempts":
            3,

        "runtime_retry_type_allowed":
            True,

        "runtime_retry_exhausted":
            True,

        "runtime_contract_error":
            False,

        "runtime_dispatch_error_type":
            "TimeoutError",

        "canonical_job_id_preserved":
            True,

        "retry_created_new_job":
            False,

        "old_universal_knowledge_jsonl_used":
            False,
    }


def make_job(
    *,
    status="failed",
    metadata=None,
    error_message="TimeoutError: upstream timeout",
    job_id="uj_smoke_5_5",
    workspace_id="ws_smoke_5_5",
    job_type="smoke.failure.stage",
):
    return {
        "job_id":
            job_id,

        "workspace_id":
            workspace_id,

        "job_type":
            job_type,

        "status":
            status,

        "metadata":
            make_metadata()
            if metadata is None
            else metadata,

        "error_message":
            error_message,
    }


def make_events():
    return [
        {
            "event_id":
                "evt_created",

            "job_id":
                "uj_smoke_5_5",

            "old_status":
                "none",

            "new_status":
                "queued",

            "created_at":
                "2026-09-08T05:00:00+00:00",
        },
        {
            "event_id":
                "evt_running",

            "job_id":
                "uj_smoke_5_5",

            "old_status":
                "queued",

            "new_status":
                "running",

            "created_at":
                "2026-09-08T05:01:00+00:00",
        },
        {
            "event_id":
                "evt_failed",

            "job_id":
                "uj_smoke_5_5",

            "old_status":
                "running",

            "new_status":
                "failed",

            "created_at":
                "2026-09-08T05:02:00+00:00",
        },
    ]


print()
print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 5.5 — RUNTIME FAILURE INTAKE")
print("INSTALLATION SMOKE")
print("=" * 120)


# =========================================================================
# 1. Installation integrity
# =========================================================================

check(
    "Phase 5.5 production file exists",
    TARGET.exists(),
)


source = TARGET.read_text(
    encoding="utf-8"
)


try:
    tree = ast.parse(
        source
    )
    syntax_ok = True

except SyntaxError:
    tree = None
    syntax_ok = False


check(
    "Phase 5.5 Python syntax parses",
    syntax_ok,
)

check(
    "Version exact",
    RUNTIME_FAILURE_INTAKE_VERSION
    == "runtime_failure_intake_v5.5.0",
)

check(
    "Schema exact",
    RUNTIME_FAILURE_INTAKE_SCHEMA_VERSION
    == "runtime_failure_intake_schema_v1",
)


# =========================================================================
# 2. Canonical authority hashes
# =========================================================================

authority_paths = {
    "phase_5_3":
        PHASE_5_3,

    "phase_5_3_manifest":
        PHASE_5_3_MANIFEST,

    "phase_5_4":
        PHASE_5_4,

    "phase_5_4_manifest":
        PHASE_5_4_MANIFEST,

    "stage_result":
        STAGE_RESULT,

    "runtime_worker":
        RUNTIME_WORKER,
}


for name, path in authority_paths.items():

    actual = sha256(
        path
    )

    check(
        "Authority SHA exact: " + name,
        actual == EXPECTED[name],
        actual,
    )


# =========================================================================
# 3. Canonical happy path
# =========================================================================

corr = make_correlation()
job = make_job()
events = make_events()


result = build_runtime_failure_stage_result(
    correlation=
        corr,

    failure_job=
        job,

    events=
        events,
)


check(
    "Result type exact",
    isinstance(
        result,
        UniversalStageResult,
    ),
)

check(
    "Result status FAILED",
    result.status
    == UniversalStageResultStatus.FAILED,
)

check(
    "result_id from FAILED event",
    result.result_id
    == "evt_failed",
)

check(
    "workflow_id preserved",
    result.workflow_id
    == corr.workflow_id,
)

check(
    "correlation_id preserved",
    result.correlation_id
    == corr.correlation_id,
)

check(
    "stage_id preserved",
    result.stage_id
    == corr.stage_id,
)

check(
    "stage_version preserved",
    result.stage_version
    == corr.stage_version,
)

check(
    "pipeline_id preserved",
    result.pipeline_id
    == corr.pipeline_id,
)

check(
    "workflow_type preserved",
    result.workflow_type
    == corr.workflow_type,
)

check(
    "workspace_id preserved",
    result.workspace_id
    == corr.workspace_id,
)

check(
    "job_id preserved",
    result.job_id
    == corr.job_id,
)

check(
    "job_type preserved",
    result.job_type
    == corr.job_type,
)

check(
    "execution target universal_runtime",
    getattr(
        result.execution_target,
        "value",
        result.execution_target,
    )
    == "universal_runtime",
)

check(
    "started_at from final QUEUED->RUNNING",
    result.started_at
    == "2026-09-08T05:01:00+00:00",
)

check(
    "finished_at from RUNNING->FAILED",
    result.finished_at
    == "2026-09-08T05:02:00+00:00",
)

check(
    "failure_code from Runtime exception type",
    result.failure_code
    == "TimeoutError",
)

check(
    "failure_message from persisted job",
    result.failure_message
    == "TimeoutError: upstream timeout",
)

check(
    "FAILED output empty",
    dict(
        result.output
    )
    == {},
)

check(
    "FAILED result_reference empty",
    result.result_reference
    == "",
)

check(
    "FAILED artifact_references empty",
    tuple(
        result.artifact_references
    )
    == (),
)


# =========================================================================
# 4. Canonical failure details
# =========================================================================

expected_detail_keys = {
    "runtime_dispatch_completed",
    "runtime_dispatch_failed",
    "runtime_retry_scheduled",
    "runtime_failure_attempt_count",
    "runtime_maximum_attempts",
    "runtime_retry_type_allowed",
    "runtime_retry_exhausted",
    "runtime_contract_error",
    "runtime_dispatch_error_type",
    "canonical_job_id_preserved",
    "retry_created_new_job",
    "runtime_worker_version",
}


check(
    "Failure details contain exact canonical key set",
    set(
        result.failure_details
    )
    == expected_detail_keys,
    repr(
        sorted(
            result.failure_details
        )
    ),
)

check(
    "Failure attempt count preserved",
    result.failure_details[
        "runtime_failure_attempt_count"
    ]
    == 3,
)

check(
    "Maximum attempts preserved",
    result.failure_details[
        "runtime_maximum_attempts"
    ]
    == 3,
)

check(
    "Retry exhausted preserved",
    result.failure_details[
        "runtime_retry_exhausted"
    ]
    is True,
)

check(
    "Contract-error classification preserved",
    result.failure_details[
        "runtime_contract_error"
    ]
    is False,
)


# =========================================================================
# 5. Retryable failures must not emit FAILED
# =========================================================================

retry_metadata = make_metadata()

retry_metadata[
    "runtime_retry_scheduled"
] = True


expect_validation_error(
    "Persisted QUEUED retry job rejected",
    lambda:
        build_runtime_failure_stage_result(
            correlation=
                corr,

            failure_job=
                make_job(
                    status=
                        "queued",

                    metadata=
                        retry_metadata,
                ),

            events=[
                events[
                    0
                ],
                events[
                    1
                ],
                {
                    "event_id":
                        "evt_retry",

                    "job_id":
                        corr.job_id,

                    "old_status":
                        "running",

                    "new_status":
                        "queued",

                    "created_at":
                        "2026-09-08T05:02:00+00:00",
                },
            ],
        ),
)


# =========================================================================
# 6. Terminal evidence strictness
# =========================================================================

for key, bad_value in (
    (
        "runtime_dispatch_failed",
        False,
    ),
    (
        "runtime_dispatch_completed",
        True,
    ),
    (
        "canonical_job_id_preserved",
        False,
    ),
    (
        "retry_created_new_job",
        True,
    ),
):

    bad_metadata = make_metadata()

    bad_metadata[
        key
    ] = bad_value

    expect_validation_error(
        key + " invalid rejected",
        lambda bad_metadata=bad_metadata:
            build_runtime_failure_stage_result(
                correlation=
                    corr,

                failure_job=
                    make_job(
                        metadata=
                            bad_metadata
                    ),

                events=
                    events,
            ),
    )


retry_scheduled_metadata = make_metadata()

retry_scheduled_metadata[
    "runtime_retry_scheduled"
] = True


expect_not_ready(
    "retry_scheduled=True is not terminal",
    lambda:
        build_runtime_failure_stage_result(
            correlation=
                corr,

            failure_job=
                make_job(
                    metadata=
                        retry_scheduled_metadata
                ),

            events=
                events,
        ),
)


# =========================================================================
# 7. Identity protection
# =========================================================================

for field, value in (
    (
        "job_id",
        "uj_wrong",
    ),
    (
        "workspace_id",
        "ws_wrong",
    ),
    (
        "job_type",
        "wrong.job",
    ),
):

    kwargs = {
        field:
            value
    }

    expect_validation_error(
        field + " mismatch rejected",
        lambda kwargs=kwargs:
            build_runtime_failure_stage_result(
                correlation=
                    corr,

                failure_job=
                    make_job(
                        **kwargs
                    ),

                events=
                    events,
            ),
    )


# =========================================================================
# 8. Failure code/message protection
# =========================================================================

missing_code = make_metadata()

missing_code.pop(
    "runtime_dispatch_error_type"
)


expect_validation_error(
    "Missing failure code rejected",
    lambda:
        build_runtime_failure_stage_result(
            correlation=
                corr,

            failure_job=
                make_job(
                    metadata=
                        missing_code
                ),

            events=
                events,
        ),
)


expect_validation_error(
    "Missing failure message rejected",
    lambda:
        build_runtime_failure_stage_result(
            correlation=
                corr,

            failure_job=
                make_job(
                    error_message=
                        ""
                ),

            events=
                events,
        ),
)


# =========================================================================
# 9. Event transition protection
# =========================================================================

bad_failed = make_events()

bad_failed[
    2
][
    "old_status"
] = "queued"


expect_validation_error(
    "QUEUED->FAILED rejected",
    lambda:
        build_runtime_failure_stage_result(
            correlation=
                corr,

            failure_job=
                job,

            events=
                bad_failed,
        ),
)


bad_running = make_events()

bad_running[
    1
][
    "old_status"
] = "completed"


expect_validation_error(
    "Invalid transition into RUNNING rejected",
    lambda:
        build_runtime_failure_stage_result(
            correlation=
                corr,

            failure_job=
                job,

            events=
                bad_running,
        ),
)


expect_not_ready(
    "Missing FAILED event not ready",
    lambda:
        build_runtime_failure_stage_result(
            correlation=
                corr,

            failure_job=
                job,

            events=
                events[:-1],
        ),
)


foreign = make_events()

foreign[
    1
][
    "job_id"
] = "uj_foreign"


expect_validation_error(
    "Foreign event identity rejected",
    lambda:
        build_runtime_failure_stage_result(
            correlation=
                corr,

            failure_job=
                job,

            events=
                foreign,
        ),
)


# =========================================================================
# 10. Retry-attempt isolation
# =========================================================================

retry_events = [
    {
        "event_id":
            "evt_q0",

        "job_id":
            corr.job_id,

        "old_status":
            "none",

        "new_status":
            "queued",

        "created_at":
            "2026-09-08T05:00:00+00:00",
    },
    {
        "event_id":
            "evt_run_1",

        "job_id":
            corr.job_id,

        "old_status":
            "queued",

        "new_status":
            "running",

        "created_at":
            "2026-09-08T05:01:00+00:00",
    },
    {
        "event_id":
            "evt_retry_1",

        "job_id":
            corr.job_id,

        "old_status":
            "running",

        "new_status":
            "queued",

        "created_at":
            "2026-09-08T05:02:00+00:00",
    },
    {
        "event_id":
            "evt_run_2",

        "job_id":
            corr.job_id,

        "old_status":
            "queued",

        "new_status":
            "running",

        "created_at":
            "2026-09-08T05:03:00+00:00",
    },
    {
        "event_id":
            "evt_failed_2",

        "job_id":
            corr.job_id,

        "old_status":
            "running",

        "new_status":
            "failed",

        "created_at":
            "2026-09-08T05:04:00+00:00",
    },
]


retry_result = build_runtime_failure_stage_result(
    correlation=
        corr,

    failure_job=
        job,

    events=
        retry_events,
)


check(
    "Retry-safe result_id final failure",
    retry_result.result_id
    == "evt_failed_2",
)

check(
    "Retry-safe started_at final attempt",
    retry_result.started_at
    == "2026-09-08T05:03:00+00:00",
)

check(
    "Retry-safe finished_at final failure",
    retry_result.finished_at
    == "2026-09-08T05:04:00+00:00",
)


# =========================================================================
# 11. Timestamp validation
# =========================================================================

bad_time = make_events()

bad_time[
    1
][
    "created_at"
] = "2026-09-08T05:10:00+00:00"


expect_validation_error(
    "Reversed timestamps rejected",
    lambda:
        build_runtime_failure_stage_result(
            correlation=
                corr,

            failure_job=
                job,

            events=
                bad_time,
        ),
)


invalid_time = make_events()

invalid_time[
    2
][
    "created_at"
] = "not-a-time"


expect_validation_error(
    "Invalid timestamp rejected",
    lambda:
        build_runtime_failure_stage_result(
            correlation=
                corr,

            failure_job=
                job,

            events=
                invalid_time,
        ),
)


# =========================================================================
# 12. Public wrapper
# =========================================================================

registry = WorkflowJobCorrelationRegistry()

registry.register(
    corr
)


reader_calls = []


def failure_reader(job_id):
    reader_calls.append(
        (
            "failure",
            job_id,
        )
    )

    return {
        "job":
            job,

        "events":
            events,
    }


def unused_events_reader(job_id):
    raise AssertionError(
        "Embedded events should be used."
    )


wrapped = intake_runtime_failure(
    job_id=
        corr.job_id,

    registry=
        registry,

    failure_reader=
        failure_reader,

    events_reader=
        unused_events_reader,
)


check(
    "Wrapper returns canonical result",
    wrapped
    == result,
)

check(
    "Wrapper reader uses canonical job_id",
    reader_calls
    == [
        (
            "failure",
            corr.job_id,
        )
    ],
    repr(
        reader_calls
    ),
)


expect_not_ready(
    "Missing failure document not ready",
    lambda:
        intake_runtime_failure(
            job_id=
                corr.job_id,

            registry=
                registry,

            failure_reader=
                lambda job_id: None,

            events_reader=
                lambda job_id: [],
        ),
)


# =========================================================================
# 13. Architecture declaration
# =========================================================================

architecture = (
    explain_runtime_failure_intake_v5_5()
)


check(
    "Architecture declaration immutable",
    isinstance(
        architecture,
        MappingProxyType,
    ),
)

check(
    "Architecture phase exact",
    architecture[
        "phase"
    ]
    == "5.5",
)

check(
    "Architecture scope exact",
    architecture[
        "scope"
    ]
    == "terminal Runtime failure only",
)

check(
    "Failure code authority exact",
    architecture[
        "failure_code_authority"
    ]
    == "runtime_dispatch_error_type",
)

check(
    "Failure message authority exact",
    architecture[
        "failure_message_authority"
    ]
    == "persisted orchestration job.error_message",
)

check(
    "Recovery ownership Phase 9",
    architecture[
        "workflow_recovery_owner"
    ]
    == "Phase 9 Coordination Recovery",
)


for key, value in architecture[
    "execution_properties"
].items():

    check(
        "Execution authority disabled: " + key,
        value is False,
    )


# =========================================================================
# 14. Static read-only boundary
# =========================================================================

forbidden_calls = {
    "create_job",
    "create_orchestration_job",
    "create_universal_job",
    "submit_universal_job",
    "update_job_status",
    "update_job_progress",
    "mark_job_running",
    "mark_job_completed",
    "mark_job_failed",
    "dispatch_registered_runtime_handler",
    "run_one_universal_runtime_job_v1",
    "uuid4",
    "utc_now",
    "write_text",
    "write_bytes",
    "mkdir",
    "unlink",
    "open",
}


called = set()

if tree is not None:

    for node in ast.walk(
        tree
    ):

        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        if isinstance(
            node.func,
            ast.Name,
        ):
            called.add(
                node.func.id
            )

        elif isinstance(
            node.func,
            ast.Attribute,
        ):
            called.add(
                node.func.attr
            )


hits = (
    called
    & forbidden_calls
)


check(
    "No forbidden Runtime/orchestration mutation calls",
    hits == set(),
    repr(
        sorted(
            hits
        )
    ),
)


# =========================================================================
# 15. Candidate SHA
# =========================================================================

candidate_sha = sha256(
    TARGET
)


check(
    "Candidate SHA structurally valid",
    (
        len(candidate_sha) == 64
        and all(
            c in "0123456789ABCDEF"
            for c in candidate_sha
        )
    ),
    candidate_sha,
)


# =========================================================================
# Final
# =========================================================================

passed = sum(
    1
    for _, ok, _
    in checks
    if ok
)

failed = (
    len(checks)
    - passed
)


lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.5 — RUNTIME FAILURE INTAKE",
    "INSTALLATION SMOKE",
    "=" * 120,
    "",
]


for name, ok, detail in checks:

    lines.append(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if detail:
        lines.append(
            "    " + detail
        )


lines.extend(
    (
        "",
        "=" * 120,
        "PHASE 5.5 INSTALLATION SMOKE RESULT",
        "=" * 120,
        f"Checks: {len(checks)}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        (
            "STATUS: SMOKE PASSED"
            if failed == 0
            else "STATUS: SMOKE FAILED"
        ),
        (
            "PHASE 5.5 CANDIDATE SHA256: "
            + candidate_sha
        ),
    )
)


REPORT.write_text(
    "\n".join(
        lines
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 120)
print("PHASE 5.5 INSTALLATION SMOKE RESULT")
print("=" * 120)
print("Checks:", len(checks))
print("Passed:", passed)
print("Failed:", failed)
print(
    "STATUS:",
    (
        "SMOKE PASSED"
        if failed == 0
        else "SMOKE FAILED"
    ),
)
print(
    "PHASE 5.5 CANDIDATE SHA256:",
    candidate_sha,
)
print(
    "REPORT:",
    REPORT.name,
)
print("=" * 120)


raise SystemExit(
    0
    if failed == 0
    else 1
)
