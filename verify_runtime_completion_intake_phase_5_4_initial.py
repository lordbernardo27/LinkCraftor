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

from backend.server.coordination.runtime_integration.runtime_completion_intake import (
    RUNTIME_COMPLETION_INTAKE_VERSION,
    RUNTIME_COMPLETION_INTAKE_SCHEMA_VERSION,
    RuntimeCompletionIntakeError,
    RuntimeCompletionValidationError,
    RuntimeCompletionNotReadyError,
    build_runtime_completion_stage_result,
    intake_runtime_completion,
    explain_runtime_completion_intake_v5_4,
)

from backend.server.coordination.universal_stages.result_contract import (
    UniversalStageResult,
    UniversalStageResultStatus,
)


ROOT = Path.cwd()

TARGET = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "runtime_completion_intake.py"
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

STAGE_RESULT = (
    ROOT
    / "backend/server/coordination/universal_stages/"
      "result_contract.py"
)

ORCHESTRATION_MODELS = (
    ROOT
    / "backend/server/orchestration/models.py"
)

ORCHESTRATION_STORE = (
    ROOT
    / "backend/server/orchestration/job_store.py"
)

ORCHESTRATION_SERVICE = (
    ROOT
    / "backend/server/orchestration/service.py"
)

ORCHESTRATION_QUEUE = (
    ROOT
    / "backend/server/orchestration/queue.py"
)

RUNTIME_WORKER = (
    ROOT
    / "backend/server/runtime/"
      "universal_runtime_worker_v1.py"
)

REPORT = (
    ROOT
    / "runtime_completion_intake_phase_5_4_initial_verification.txt"
)


EXPECTED_TARGET_SHA = (
    "A9F2A8E4242A08A2BDBE6AF0B96DC104"
    "2A53DDD3B2F72BB355259FA0E5D2E6FB"
)

EXPECTED = {
    "phase_5_3":
        "C0D88ECC69680106B6833DF8CB3113FC"
        "9ABD23C1EE8B7D413BA4AAE3375648FA",

    "phase_5_3_manifest":
        "53F2B149EF904CE5692D85F349038CEA"
        "B901E00B06C6C273CA5B74EB31ACE8E5",

    "stage_result":
        "B3469B10BB2F8F9372E4336784D09A14"
        "3C78FABE45BF039B61B76F4A2DC33B24",

    "orchestration_models":
        "C2D014CF071D34F478F7E4B108F6192"
        "A21F4D7AD7958F394D3443BD59C884923",

    "orchestration_store":
        "AE88C201C1A1A4740A50F607DA067212"
        "EEAC2ABA4DE5416E75DD38043B8D487E",

    "orchestration_service":
        "A14CF668B20EECF5D90F675E8DC5DDE3"
        "5DC866D183C303A5B59C33100C72BEC4",

    "orchestration_queue":
        "3590DE4CA38A2252ACB8944B39B0AF82"
        "EBCB67F2563A7E751E14AA6B00DE9F2F",

    "runtime_worker":
        "ED6B415C5FEDF3F4CB62451F3E23D182"
        "F9DA937D9CB09FD33262C506B9BEF699",
}


checks = []


def check(
    name,
    condition,
    detail="",
):
    ok = bool(
        condition
    )

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
        print(
            "    "
            + detail
        )


def sha256(
    path: Path,
) -> str:

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def expect_validation_error(
    name,
    fn,
):

    try:
        fn()

    except RuntimeCompletionValidationError as exc:

        check(
            name,
            True,
            str(
                exc
            ),
        )

        return True

    except Exception as exc:

        check(
            name,
            False,
            "Unexpected exception: "
            + repr(
                exc
            ),
        )

        return False

    check(
        name,
        False,
        "Expected RuntimeCompletionValidationError.",
    )

    return False


def expect_not_ready(
    name,
    fn,
):

    try:
        fn()

    except RuntimeCompletionNotReadyError as exc:

        check(
            name,
            True,
            str(
                exc
            ),
        )

        return True

    except Exception as exc:

        check(
            name,
            False,
            "Unexpected exception: "
            + repr(
                exc
            ),
        )

        return False

    check(
        name,
        False,
        "Expected RuntimeCompletionNotReadyError.",
    )

    return False


def correlation():
    return WorkflowJobCorrelation(
        workflow_id=
            "wf_initial_5_4",

        correlation_id=
            "corr_initial_5_4",

        stage_id=
            "stage_initial",

        stage_version=
            "stage_initial_v1",

        workflow_type=
            "initial_workflow",

        workspace_id=
            "ws_initial_5_4",

        job_id=
            "uj_initial_5_4",

        job_type=
            "initial.runtime.stage",

        pipeline_id=
            "pipeline_initial",

        runtime_stage=
            "runtime_stage_initial",

        wave_index=
            2,
    )


def completion_job(
    *,
    status="completed",
    metadata_overrides=None,
):

    metadata = {
        "runtime_dispatch_completed":
            True,

        "canonical_job_id_preserved":
            True,

        "runtime_dispatch_result": {
            "ok":
                False,

            "business_status":
                "historical-handler-value",

            "value":
                123,

            "nested": {
                "a":
                    1,
            },
        },
    }

    if metadata_overrides:
        metadata.update(
            metadata_overrides
        )

    return {
        "job_id":
            "uj_initial_5_4",

        "workspace_id":
            "ws_initial_5_4",

        "job_type":
            "initial.runtime.stage",

        "status":
            status,

        "metadata":
            metadata,
    }


def normal_events():
    return [
        {
            "event_id":
                "evt_created",

            "job_id":
                "uj_initial_5_4",

            "old_status":
                "none",

            "new_status":
                "queued",

            "created_at":
                "2026-09-08T03:00:00+00:00",
        },
        {
            "event_id":
                "evt_running",

            "job_id":
                "uj_initial_5_4",

            "old_status":
                "queued",

            "new_status":
                "running",

            "created_at":
                "2026-09-08T03:01:00+00:00",
        },
        {
            "event_id":
                "evt_completed",

            "job_id":
                "uj_initial_5_4",

            "old_status":
                "running",

            "new_status":
                "completed",

            "created_at":
                "2026-09-08T03:02:00+00:00",
        },
    ]


print()
print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 5.4 — RUNTIME COMPLETION INTAKE")
print("INITIAL VERIFICATION")
print("=" * 120)


# =========================================================================
# 1. Candidate and authority integrity
# =========================================================================

target_sha = sha256(
    TARGET
)

check(
    "Phase 5.4 candidate SHA exact",
    target_sha
    == EXPECTED_TARGET_SHA,
    target_sha,
)


authority_paths = {
    "phase_5_3":
        PHASE_5_3,

    "phase_5_3_manifest":
        PHASE_5_3_MANIFEST,

    "stage_result":
        STAGE_RESULT,

    "orchestration_models":
        ORCHESTRATION_MODELS,

    "orchestration_store":
        ORCHESTRATION_STORE,

    "orchestration_service":
        ORCHESTRATION_SERVICE,

    "orchestration_queue":
        ORCHESTRATION_QUEUE,

    "runtime_worker":
        RUNTIME_WORKER,
}


for name, path in authority_paths.items():

    actual = sha256(
        path
    )

    check(
        "Authority SHA exact: "
        + name,
        actual
        == EXPECTED[
            name
        ],
        actual,
    )


# =========================================================================
# 2. Version/schema
# =========================================================================

check(
    "Version exact",
    RUNTIME_COMPLETION_INTAKE_VERSION
    == "runtime_completion_intake_v5.4.0",
)

check(
    "Schema exact",
    RUNTIME_COMPLETION_INTAKE_SCHEMA_VERSION
    == "runtime_completion_intake_schema_v1",
)


# =========================================================================
# 3. Canonical completed attempt
# =========================================================================

corr = correlation()

job = completion_job()

events = normal_events()


result = build_runtime_completion_stage_result(
    correlation=
        corr,

    completion_job=
        job,

    events=
        events,
)


check(
    "Canonical StageResult constructed",
    isinstance(
        result,
        UniversalStageResult,
    ),
)

check(
    "Canonical status COMPLETED",
    result.status
    == UniversalStageResultStatus.COMPLETED,
)

check(
    "result_id equals terminal completion event_id",
    result.result_id
    == "evt_completed",
)

check(
    "started_at uses RUNNING event",
    result.started_at
    == "2026-09-08T03:01:00+00:00",
)

check(
    "finished_at uses COMPLETED event",
    result.finished_at
    == "2026-09-08T03:02:00+00:00",
)

check(
    "Business ok=False remains opaque",
    result.output[
        "ok"
    ]
    is False,
)

check(
    "Business ok=False does not override COMPLETED",
    result.status
    == UniversalStageResultStatus.COMPLETED,
)


# =========================================================================
# 4. Retry-attempt selection
# =========================================================================

retry_events = [
    {
        "event_id":
            "evt_created",

        "job_id":
            corr.job_id,

        "old_status":
            "none",

        "new_status":
            "queued",

        "created_at":
            "2026-09-08T03:00:00+00:00",
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
            "2026-09-08T03:01:00+00:00",
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
            "2026-09-08T03:02:00+00:00",
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
            "2026-09-08T03:03:00+00:00",
    },
    {
        "event_id":
            "evt_done_2",

        "job_id":
            corr.job_id,

        "old_status":
            "running",

        "new_status":
            "completed",

        "created_at":
            "2026-09-08T03:04:00+00:00",
    },
]


retry_result = build_runtime_completion_stage_result(
    correlation=
        corr,

    completion_job=
        job,

    events=
        retry_events,
)


check(
    "Retry completion identity uses final attempt",
    retry_result.result_id
    == "evt_done_2",
)

check(
    "Retry started_at uses final RUNNING transition",
    retry_result.started_at
    == "2026-09-08T03:03:00+00:00",
)

check(
    "Retry finished_at exact",
    retry_result.finished_at
    == "2026-09-08T03:04:00+00:00",
)


# =========================================================================
# 5. Completion transition must be RUNNING -> COMPLETED
# =========================================================================

invalid_completion_transition = [
    {
        "event_id":
            "evt_created",

        "job_id":
            corr.job_id,

        "old_status":
            "none",

        "new_status":
            "queued",

        "created_at":
            "2026-09-08T03:00:00+00:00",
    },
    {
        "event_id":
            "evt_running_old",

        "job_id":
            corr.job_id,

        "old_status":
            "queued",

        "new_status":
            "running",

        "created_at":
            "2026-09-08T03:01:00+00:00",
    },
    {
        "event_id":
            "evt_requeued",

        "job_id":
            corr.job_id,

        "old_status":
            "running",

        "new_status":
            "queued",

        "created_at":
            "2026-09-08T03:02:00+00:00",
    },
    {
        "event_id":
            "evt_invalid_complete",

        "job_id":
            corr.job_id,

        "old_status":
            "queued",

        "new_status":
            "completed",

        "created_at":
            "2026-09-08T03:03:00+00:00",
    },
]


expect_validation_error(
    "QUEUED -> COMPLETED transition rejected",
    lambda:
        build_runtime_completion_stage_result(
            correlation=
                corr,

            completion_job=
                job,

            events=
                invalid_completion_transition,
        ),
)


# =========================================================================
# 6. RUNNING attempt event must be a real transition into RUNNING
# =========================================================================

invalid_running_transition = [
    {
        "event_id":
            "evt_created",

        "job_id":
            corr.job_id,

        "old_status":
            "none",

        "new_status":
            "queued",

        "created_at":
            "2026-09-08T03:00:00+00:00",
    },
    {
        "event_id":
            "evt_bad_running",

        "job_id":
            corr.job_id,

        "old_status":
            "completed",

        "new_status":
            "running",

        "created_at":
            "2026-09-08T03:01:00+00:00",
    },
    {
        "event_id":
            "evt_complete",

        "job_id":
            corr.job_id,

        "old_status":
            "running",

        "new_status":
            "completed",

        "created_at":
            "2026-09-08T03:02:00+00:00",
    },
]


expect_validation_error(
    "Impossible COMPLETED -> RUNNING attempt transition rejected",
    lambda:
        build_runtime_completion_stage_result(
            correlation=
                corr,

            completion_job=
                job,

            events=
                invalid_running_transition,
        ),
)


# =========================================================================
# 7. Event timestamps
# =========================================================================

missing_started_time = normal_events()

missing_started_time[
    1
][
    "created_at"
] = ""


expect_validation_error(
    "Missing RUNNING event timestamp rejected",
    lambda:
        build_runtime_completion_stage_result(
            correlation=
                corr,

            completion_job=
                job,

            events=
                missing_started_time,
        ),
)


missing_finished_time = normal_events()

missing_finished_time[
    2
][
    "created_at"
] = ""


expect_validation_error(
    "Missing COMPLETED event timestamp rejected",
    lambda:
        build_runtime_completion_stage_result(
            correlation=
                corr,

            completion_job=
                job,

            events=
                missing_finished_time,
        ),
)


reversed_time = normal_events()

reversed_time[
    1
][
    "created_at"
] = "2026-09-08T03:05:00+00:00"


expect_validation_error(
    "finished_at earlier than started_at rejected",
    lambda:
        build_runtime_completion_stage_result(
            correlation=
                corr,

            completion_job=
                job,

            events=
                reversed_time,
        ),
)


# =========================================================================
# 8. Completion event identity
# =========================================================================

missing_event_id = normal_events()

missing_event_id[
    2
][
    "event_id"
] = ""


expect_validation_error(
    "Missing completion event_id rejected",
    lambda:
        build_runtime_completion_stage_result(
            correlation=
                corr,

            completion_job=
                job,

            events=
                missing_event_id,
        ),
)


# =========================================================================
# 9. No foreign event contamination
# =========================================================================

foreign_before_completion = normal_events()

foreign_before_completion.insert(
    2,
    {
        "event_id":
            "evt_foreign",

        "job_id":
            "uj_foreign",

        "old_status":
            "running",

        "new_status":
            "queued",

        "created_at":
            "2026-09-08T03:01:30+00:00",
    },
)


expect_validation_error(
    "Foreign event in canonical trail rejected",
    lambda:
        build_runtime_completion_stage_result(
            correlation=
                corr,

            completion_job=
                job,

            events=
                foreign_before_completion,
        ),
)


# =========================================================================
# 10. Terminal completion evidence
# =========================================================================

expect_validation_error(
    "Persisted RUNNING job rejected",
    lambda:
        build_runtime_completion_stage_result(
            correlation=
                corr,

            completion_job=
                completion_job(
                    status=
                        "running"
                ),

            events=
                events,
        ),
)


expect_validation_error(
    "runtime_dispatch_completed must be literal True",
    lambda:
        build_runtime_completion_stage_result(
            correlation=
                corr,

            completion_job=
                completion_job(
                    metadata_overrides={
                        "runtime_dispatch_completed":
                            1,
                    }
                ),

            events=
                events,
        ),
)


expect_validation_error(
    "canonical_job_id_preserved must be literal True",
    lambda:
        build_runtime_completion_stage_result(
            correlation=
                corr,

            completion_job=
                completion_job(
                    metadata_overrides={
                        "canonical_job_id_preserved":
                            1,
                    }
                ),

            events=
                events,
        ),
)


# =========================================================================
# 11. Output requirements
# =========================================================================

non_mapping_output = completion_job(
    metadata_overrides={
        "runtime_dispatch_result":
            "not-a-mapping",
    }
)


expect_validation_error(
    "Non-mapping runtime_dispatch_result rejected",
    lambda:
        build_runtime_completion_stage_result(
            correlation=
                corr,

            completion_job=
                non_mapping_output,

            events=
                events,
        ),
)


# =========================================================================
# 12. Wrapper deterministic lookup
# =========================================================================

registry = (
    WorkflowJobCorrelationRegistry()
)

registry.register(
    corr
)


reader_calls = []


def completion_reader(
    job_id,
):
    reader_calls.append(
        (
            "completion",
            job_id,
        )
    )

    return {
        "job":
            job,
    }


def events_reader(
    job_id,
):
    reader_calls.append(
        (
            "events",
            job_id,
        )
    )

    return events


wrapped = intake_runtime_completion(
    job_id=
        corr.job_id,

    registry=
        registry,

    completion_reader=
        completion_reader,

    events_reader=
        events_reader,
)


check(
    "Wrapper constructs canonical result",
    wrapped
    == result,
)

check(
    "Wrapper performs readers with exact job_id",
    reader_calls
    == [
        (
            "completion",
            corr.job_id,
        ),
        (
            "events",
            corr.job_id,
        ),
    ],
    repr(
        reader_calls
    ),
)


# =========================================================================
# 13. Unknown correlation fails before completion read
# =========================================================================

unknown_reader_called = []


try:
    intake_runtime_completion(
        job_id=
            "uj_unknown",

        registry=
            registry,

        completion_reader=
            lambda job_id:
                unknown_reader_called.append(
                    job_id
                ),

        events_reader=
            lambda job_id: [],
    )

except Exception:
    pass


check(
    "Unknown correlation does not query Runtime completion",
    unknown_reader_called
    == [],
    repr(
        unknown_reader_called
    ),
)


# =========================================================================
# 14. Public API shape
# =========================================================================

check(
    "Builder keyword-only",
    str(
        inspect.signature(
            build_runtime_completion_stage_result
        )
    ).startswith(
        "(*,"
    ),
)

check(
    "Intake wrapper keyword-only",
    str(
        inspect.signature(
            intake_runtime_completion
        )
    ).startswith(
        "(*,"
    ),
)

check(
    "Validation error inheritance exact",
    issubclass(
        RuntimeCompletionValidationError,
        RuntimeCompletionIntakeError,
    ),
)

check(
    "NotReady inheritance exact",
    issubclass(
        RuntimeCompletionNotReadyError,
        RuntimeCompletionValidationError,
    ),
)


# =========================================================================
# 15. Architecture declaration
# =========================================================================

architecture = (
    explain_runtime_completion_intake_v5_4()
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
    == "5.4",
)

check(
    "Completion event authority exact",
    architecture[
        "completion_event_authority"
    ]
    == "orchestration JobStatusEvent trail",
)

check(
    "started_at authority exact",
    architecture[
        "started_at_authority"
    ]
    == (
        "latest RUNNING event preceding "
        "selected COMPLETED event"
    ),
)

check(
    "finished_at authority exact",
    architecture[
        "finished_at_authority"
    ]
    == (
        "selected COMPLETED event.created_at"
    ),
)

check(
    "Failure ownership exact",
    architecture[
        "failure_processing_owner"
    ]
    == "Phase 5.5 Runtime Failure Intake",
)


# =========================================================================
# 16. Static authority boundary
# =========================================================================

source = TARGET.read_text(
    encoding="utf-8"
)

tree = ast.parse(
    source
)

forbidden = {
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
    "datetime.now",
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
    & forbidden
)


check(
    "No forbidden mutation/generation calls",
    hits
    == set(),
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
    len(
        checks
    )
    - passed
)


lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.4 — RUNTIME COMPLETION INTAKE",
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
            "    "
            + detail
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
            "PHASE 5.4 SHA256: "
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
print("PHASE 5.4 INITIAL VERIFICATION RESULT")
print("=" * 120)
print(
    "Checks:",
    len(
        checks
    ),
)
print(
    "Passed:",
    passed,
)
print(
    "Failed:",
    failed,
)
print(
    "STATUS:",
    (
        "INITIAL VERIFICATION PASSED"
        if failed == 0
        else "INITIAL VERIFICATION FAILED"
    ),
)
print(
    "PHASE 5.4 SHA256:",
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

