from __future__ import annotations

import ast
import hashlib
import inspect
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
    / "runtime_failure_intake_phase_5_5_initial_verification.txt"
)


EXPECTED_TARGET_SHA = (
    "CDEE8D641AC045956E2A203BF0A62DE7"
    "0933F0755B946D63310EFBABE7DFE241"
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
        workflow_id="wf_initial_5_5",
        correlation_id="corr_initial_5_5",
        stage_id="stage_initial_failure",
        stage_version="stage_initial_failure_v1",
        workflow_type="initial_failure_workflow",
        workspace_id="ws_initial_5_5",
        job_id="uj_initial_5_5",
        job_type="initial.failure.stage",
        pipeline_id="pipeline_initial_failure",
        runtime_stage="runtime_stage_initial_failure",
        wave_index=3,
    )


def make_metadata():
    return {
        "worker_id":
            "worker_initial",

        "runtime_worker_version":
            "universal_runtime_worker_v1",

        "runtime_dispatch_completed":
            False,

        "runtime_dispatch_failed":
            True,

        "runtime_retry_scheduled":
            False,

        "runtime_failure_attempt_count":
            2,

        "runtime_maximum_attempts":
            2,

        "runtime_retry_type_allowed":
            True,

        "runtime_retry_exhausted":
            True,

        "runtime_contract_error":
            False,

        "runtime_dispatch_error_type":
            "ConnectionError",

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
    error_message="ConnectionError: connection lost",
    job_id="uj_initial_5_5",
    workspace_id="ws_initial_5_5",
    job_type="initial.failure.stage",
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
                "evt_initial_created",

            "job_id":
                "uj_initial_5_5",

            "old_status":
                "none",

            "new_status":
                "queued",

            "created_at":
                "2026-09-08T06:00:00+00:00",
        },
        {
            "event_id":
                "evt_initial_running",

            "job_id":
                "uj_initial_5_5",

            "old_status":
                "queued",

            "new_status":
                "running",

            "created_at":
                "2026-09-08T06:01:00+00:00",
        },
        {
            "event_id":
                "evt_initial_failed",

            "job_id":
                "uj_initial_5_5",

            "old_status":
                "running",

            "new_status":
                "failed",

            "created_at":
                "2026-09-08T06:02:00+00:00",
        },
    ]


print()
print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 5.5 — RUNTIME FAILURE INTAKE")
print("INITIAL VERIFICATION")
print("=" * 120)


# =========================================================================
# 1. Candidate and frozen authority integrity
# =========================================================================

target_sha = sha256(
    TARGET
)


check(
    "Phase 5.5 candidate SHA exact",
    target_sha == EXPECTED_TARGET_SHA,
    target_sha,
)


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
# 2. Version/schema/API
# =========================================================================

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

check(
    "Builder keyword-only",
    str(
        inspect.signature(
            build_runtime_failure_stage_result
        )
    ).startswith(
        "(*,"
    ),
)

check(
    "Wrapper keyword-only",
    str(
        inspect.signature(
            intake_runtime_failure
        )
    ).startswith(
        "(*,"
    ),
)

check(
    "Validation error inheritance",
    issubclass(
        RuntimeFailureValidationError,
        RuntimeFailureIntakeError,
    ),
)

check(
    "NotReady inheritance",
    issubclass(
        RuntimeFailureNotReadyError,
        RuntimeFailureValidationError,
    ),
)


# =========================================================================
# 3. Canonical terminal failure
# =========================================================================

corr = make_correlation()
job = make_job()
events = make_events()


result = build_runtime_failure_stage_result(
    correlation=corr,
    failure_job=job,
    events=events,
)


check(
    "Result type exact",
    isinstance(
        result,
        UniversalStageResult,
    ),
)

check(
    "Status FAILED exact",
    result.status
    == UniversalStageResultStatus.FAILED,
)

check(
    "result_id exact",
    result.result_id
    == "evt_initial_failed",
)

check(
    "started_at exact",
    result.started_at
    == "2026-09-08T06:01:00+00:00",
)

check(
    "finished_at exact",
    result.finished_at
    == "2026-09-08T06:02:00+00:00",
)

check(
    "failure_code exact",
    result.failure_code
    == "ConnectionError",
)

check(
    "failure_message exact",
    result.failure_message
    == "ConnectionError: connection lost",
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
# 4. Exact identity mapping
# =========================================================================

for field in (
    "workflow_id",
    "correlation_id",
    "stage_id",
    "stage_version",
    "pipeline_id",
    "workflow_type",
    "workspace_id",
    "job_id",
    "job_type",
):

    check(
        "Identity preserved: " + field,
        getattr(
            result,
            field,
        )
        == getattr(
            corr,
            field,
        ),
    )


# =========================================================================
# 5. Canonical failure detail completeness
# =========================================================================

required_detail_keys = (
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
)


check(
    "Canonical failure detail key set exact",
    set(
        result.failure_details
    )
    == set(
        required_detail_keys
    ),
)


for key in required_detail_keys:

    check(
        "Canonical failure detail preserved: " + key,
        result.failure_details[
            key
        ]
        == make_metadata()[
            key
        ],
    )


# =========================================================================
# 6. Prove missing canonical failure evidence is rejected
# =========================================================================

for key in (
    "runtime_failure_attempt_count",
    "runtime_maximum_attempts",
    "runtime_retry_type_allowed",
    "runtime_retry_exhausted",
    "runtime_contract_error",
    "runtime_worker_version",
):

    bad_metadata = make_metadata()

    bad_metadata.pop(
        key
    )

    expect_validation_error(
        "Missing canonical detail rejected: " + key,
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


# =========================================================================
# 7. Terminal boolean evidence must be literal
# =========================================================================

for key, bad_value in (
    (
        "runtime_dispatch_failed",
        1,
    ),
    (
        "runtime_dispatch_completed",
        0,
    ),
    (
        "runtime_retry_scheduled",
        0,
    ),
    (
        "canonical_job_id_preserved",
        1,
    ),
    (
        "retry_created_new_job",
        0,
    ),
):

    bad_metadata = make_metadata()

    bad_metadata[
        key
    ] = bad_value

    if key == "runtime_retry_scheduled":

        expect_not_ready(
            key + " must be literal False",
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

    else:

        expect_validation_error(
            key + " literal enforcement",
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


# =========================================================================
# 8. Retryable / nonterminal behavior
# =========================================================================

retry_metadata = make_metadata()

retry_metadata[
    "runtime_retry_scheduled"
] = True


expect_not_ready(
    "FAILED record with retry scheduled rejected as nonterminal",
    lambda:
        build_runtime_failure_stage_result(
            correlation=
                corr,

            failure_job=
                make_job(
                    metadata=
                        retry_metadata
                ),

            events=
                events,
        ),
)


expect_validation_error(
    "QUEUED job cannot emit FAILED StageResult",
    lambda:
        build_runtime_failure_stage_result(
            correlation=
                corr,

            failure_job=
                make_job(
                    status=
                        "queued"
                ),

            events=
                events,
        ),
)


# =========================================================================
# 9. Transition corruption
# =========================================================================

bad_failed = make_events()

bad_failed[
    2
][
    "old_status"
] = "queued"


expect_validation_error(
    "Latest FAILED transition must be RUNNING->FAILED",
    lambda:
        build_runtime_failure_stage_result(
            correlation=corr,
            failure_job=job,
            events=bad_failed,
        ),
)


bad_running = make_events()

bad_running[
    1
][
    "old_status"
] = "failed"


expect_validation_error(
    "Attempt start must be QUEUED->RUNNING",
    lambda:
        build_runtime_failure_stage_result(
            correlation=corr,
            failure_job=job,
            events=bad_running,
        ),
)


# Latest FAILED event must not be silently skipped if corrupt.
multiple_failed = [
    {
        "event_id":
            "evt_q",
        "job_id":
            corr.job_id,
        "old_status":
            "none",
        "new_status":
            "queued",
        "created_at":
            "2026-09-08T06:00:00+00:00",
    },
    {
        "event_id":
            "evt_r",
        "job_id":
            corr.job_id,
        "old_status":
            "queued",
        "new_status":
            "running",
        "created_at":
            "2026-09-08T06:01:00+00:00",
    },
    {
        "event_id":
            "evt_valid_failed",
        "job_id":
            corr.job_id,
        "old_status":
            "running",
        "new_status":
            "failed",
        "created_at":
            "2026-09-08T06:02:00+00:00",
    },
    {
        "event_id":
            "evt_corrupt_failed",
        "job_id":
            corr.job_id,
        "old_status":
            "queued",
        "new_status":
            "failed",
        "created_at":
            "2026-09-08T06:03:00+00:00",
    },
]


expect_validation_error(
    "Corrupt latest FAILED event fails closed",
    lambda:
        build_runtime_failure_stage_result(
            correlation=
                corr,

            failure_job=
                job,

            events=
                multiple_failed,
        ),
)


# =========================================================================
# 10. Retry-safe final-attempt selection
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
            "2026-09-08T06:00:00+00:00",
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
            "2026-09-08T06:01:00+00:00",
    },
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
            "2026-09-08T06:02:00+00:00",
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
            "2026-09-08T06:03:00+00:00",
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
            "2026-09-08T06:04:00+00:00",
    },
]


retry_result = build_runtime_failure_stage_result(
    correlation=corr,
    failure_job=job,
    events=retry_events,
)


check(
    "Final retry attempt result_id exact",
    retry_result.result_id
    == "evt_failed_2",
)

check(
    "Final retry attempt started_at exact",
    retry_result.started_at
    == "2026-09-08T06:03:00+00:00",
)

check(
    "Final retry attempt finished_at exact",
    retry_result.finished_at
    == "2026-09-08T06:04:00+00:00",
)


# =========================================================================
# 11. Timestamp boundary
# =========================================================================

reverse = make_events()

reverse[
    1
][
    "created_at"
] = "2026-09-08T06:05:00+00:00"


expect_validation_error(
    "finished_at earlier than started_at rejected",
    lambda:
        build_runtime_failure_stage_result(
            correlation=corr,
            failure_job=job,
            events=reverse,
        ),
)


invalid = make_events()

invalid[
    2
][
    "created_at"
] = "invalid"


expect_validation_error(
    "Invalid Runtime failure timestamp rejected",
    lambda:
        build_runtime_failure_stage_result(
            correlation=corr,
            failure_job=job,
            events=invalid,
        ),
)


# =========================================================================
# 12. Correlation lookup must precede Runtime read
# =========================================================================

empty_registry = WorkflowJobCorrelationRegistry()

reader_called = []


def forbidden_reader(job_id):
    reader_called.append(
        job_id
    )

    return {
        "job":
            job,
        "events":
            events,
    }


try:
    intake_runtime_failure(
        job_id=
            corr.job_id,

        registry=
            empty_registry,

        failure_reader=
            forbidden_reader,

        events_reader=
            lambda job_id: events,
    )

except Exception:
    pass


check(
    "Unknown correlation fails before Runtime/orchestration read",
    reader_called == [],
    repr(
        reader_called
    ),
)


# =========================================================================
# 13. Wrapper and embedded-event path
# =========================================================================

registry = WorkflowJobCorrelationRegistry()

registry.register(
    corr
)


wrapped = intake_runtime_failure(
    job_id=
        corr.job_id,

    registry=
        registry,

    failure_reader=
        lambda job_id: {
            "job":
                job,

            "events":
                events,
        },

    events_reader=
        lambda job_id:
            (_ for _ in ())
            .throw(
                AssertionError(
                    "embedded events must be used"
                )
            ),
)


check(
    "Wrapper result equals builder result",
    wrapped == result,
)


# =========================================================================
# 14. Architecture declaration
# =========================================================================

architecture = explain_runtime_failure_intake_v5_5()


check(
    "Architecture immutable",
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
    "Architecture terminal status authority exact",
    architecture[
        "terminal_status_authority"
    ]
    == "canonical orchestration persisted job",
)

check(
    "Architecture terminal event authority exact",
    architecture[
        "terminal_event_authority"
    ]
    == "RUNNING -> FAILED JobStatusEvent",
)

check(
    "Architecture attempt start authority exact",
    architecture[
        "attempt_start_authority"
    ]
    == "QUEUED -> RUNNING JobStatusEvent",
)

check(
    "Architecture recovery owner exact",
    architecture[
        "workflow_recovery_owner"
    ]
    == "Phase 9 Coordination Recovery",
)


# =========================================================================
# 15. Static read-only enforcement
# =========================================================================

source = TARGET.read_text(
    encoding="utf-8"
)

tree = ast.parse(
    source
)


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
    "INITIAL VERIFICATION",
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
        "INITIAL VERIFICATION RESULT",
        "=" * 120,
        f"Checks: {len(checks)}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        (
            "STATUS: INITIAL VERIFICATION PASSED"
            if failed == 0
            else "STATUS: INITIAL VERIFICATION FAILED"
        ),
        (
            "PHASE 5.5 SHA256: "
            + target_sha
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
print("PHASE 5.5 INITIAL VERIFICATION RESULT")
print("=" * 120)
print("Checks:", len(checks))
print("Passed:", passed)
print("Failed:", failed)
print(
    "STATUS:",
    (
        "INITIAL VERIFICATION PASSED"
        if failed == 0
        else "INITIAL VERIFICATION FAILED"
    ),
)
print(
    "PHASE 5.5 SHA256:",
    target_sha,
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

