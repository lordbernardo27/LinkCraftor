from __future__ import annotations

import ast
import hashlib
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
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
    / "runtime_completion_intake_phase_5_4_installation_smoke.txt"
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

        return

    except Exception as exc:

        check(
            name,
            False,
            "Unexpected exception: "
            + repr(
                exc
            ),
        )

        return

    check(
        name,
        False,
        "Expected RuntimeCompletionValidationError.",
    )


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

        return

    except Exception as exc:

        check(
            name,
            False,
            "Unexpected exception: "
            + repr(
                exc
            ),
        )

        return

    check(
        name,
        False,
        "Expected RuntimeCompletionNotReadyError.",
    )


def make_correlation(
) -> WorkflowJobCorrelation:

    return WorkflowJobCorrelation(
        workflow_id=
            "wf_smoke_5_4",

        correlation_id=
            "corr_smoke_5_4",

        stage_id=
            "stage_smoke",

        stage_version=
            "stage_smoke_v1",

        workflow_type=
            "smoke_workflow",

        workspace_id=
            "ws_smoke_5_4",

        job_id=
            "uj_smoke_5_4",

        job_type=
            "smoke.runtime.stage",

        pipeline_id=
            "pipeline_smoke",

        runtime_stage=
            "runtime_stage_smoke",

        wave_index=
            0,
    )


def make_completion_job(
    *,
    job_id="uj_smoke_5_4",
    workspace_id="ws_smoke_5_4",
    job_type="smoke.runtime.stage",
    status="completed",
    runtime_dispatch_completed=True,
    canonical_job_id_preserved=True,
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

        "metadata": {
            "runtime_dispatch_completed":
                runtime_dispatch_completed,

            "canonical_job_id_preserved":
                canonical_job_id_preserved,

            "runtime_dispatch_result": {
                "ok":
                    True,

                "document_id":
                    "doc_smoke",

                "value":
                    42,

                "result_reference":
                    "result://smoke/doc",

                "artifact_references": [
                    "artifact://smoke/a",
                    "artifact://smoke/b",
                ],
            },
        },
    }


def make_events(
):

    return [
        {
            "event_id":
                "evt_created",

            "job_id":
                "uj_smoke_5_4",

            "old_status":
                "none",

            "new_status":
                "queued",

            "created_at":
                "2026-09-08T02:00:00+00:00",
        },
        {
            "event_id":
                "evt_running",

            "job_id":
                "uj_smoke_5_4",

            "old_status":
                "queued",

            "new_status":
                "running",

            "created_at":
                "2026-09-08T02:01:00+00:00",
        },
        {
            "event_id":
                "evt_completed",

            "job_id":
                "uj_smoke_5_4",

            "old_status":
                "running",

            "new_status":
                "completed",

            "created_at":
                "2026-09-08T02:02:00+00:00",
        },
    ]


print()
print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 5.4 — RUNTIME COMPLETION INTAKE")
print("INSTALLATION SMOKE")
print("=" * 120)


# =========================================================================
# 1. Installation integrity
# =========================================================================

check(
    "Phase 5.4 production file exists",
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
    "Phase 5.4 Python syntax parses",
    syntax_ok,
)

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
# 2. Frozen/canonical authority hashes
# =========================================================================

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
# 3. Happy path
# =========================================================================

correlation = (
    make_correlation()
)

completion_job = (
    make_completion_job()
)

events = (
    make_events()
)


result = build_runtime_completion_stage_result(
    correlation=
        correlation,

    completion_job=
        completion_job,

    events=
        events,
)


check(
    "Happy-path result type exact",
    isinstance(
        result,
        UniversalStageResult,
    ),
)

check(
    "Result status COMPLETED",
    result.status
    == UniversalStageResultStatus.COMPLETED,
)

check(
    "result_id from completion event",
    result.result_id
    == "evt_completed",
)

check(
    "workflow_id preserved",
    result.workflow_id
    == correlation.workflow_id,
)

check(
    "correlation_id preserved",
    result.correlation_id
    == correlation.correlation_id,
)

check(
    "stage_id preserved",
    result.stage_id
    == correlation.stage_id,
)

check(
    "stage_version preserved",
    result.stage_version
    == correlation.stage_version,
)

check(
    "pipeline_id preserved",
    result.pipeline_id
    == correlation.pipeline_id,
)

check(
    "workflow_type preserved",
    result.workflow_type
    == correlation.workflow_type,
)

check(
    "workspace_id exact",
    result.workspace_id
    == correlation.workspace_id,
)

check(
    "job_id exact",
    result.job_id
    == correlation.job_id,
)

check(
    "job_type exact",
    result.job_type
    == correlation.job_type,
)

check(
    "execution_target universal_runtime",
    getattr(
        result.execution_target,
        "value",
        result.execution_target,
    )
    == "universal_runtime",
)

check(
    "started_at from RUNNING event",
    result.started_at
    == "2026-09-08T02:01:00+00:00",
)

check(
    "finished_at from COMPLETED event",
    result.finished_at
    == "2026-09-08T02:02:00+00:00",
)

check(
    "Opaque output preserved",
    result.output[
        "document_id"
    ]
    == "doc_smoke",
)

check(
    "Business ok remains inside output",
    result.output[
        "ok"
    ]
    is True,
)

check(
    "result_reference extracted",
    result.result_reference
    == "result://smoke/doc",
)

check(
    "artifact_references extracted",
    tuple(
        result.artifact_references
    )
    == (
        "artifact://smoke/a",
        "artifact://smoke/b",
    ),
)

check(
    "Successful result failure_code empty",
    result.failure_code
    == "",
)

check(
    "Successful result failure_message empty",
    result.failure_message
    == "",
)

check(
    "Successful result failure_details empty",
    dict(
        result.failure_details
    )
    == {},
)


# =========================================================================
# 4. Runtime evidence metadata
# =========================================================================

check(
    "Completion intake version recorded",
    result.metadata[
        "runtime_completion_intake_version"
    ]
    == RUNTIME_COMPLETION_INTAKE_VERSION,
)

check(
    "Completion event id recorded",
    result.metadata[
        "runtime_completion_event_id"
    ]
    == "evt_completed",
)

check(
    "Timing source recorded",
    result.metadata[
        "runtime_completion_timing_source"
    ]
    == "orchestration_status_events",
)

check(
    "Output source recorded",
    result.metadata[
        "runtime_output_source"
    ]
    == "runtime_dispatch_result",
)

check(
    "Canonical identity preservation recorded",
    result.metadata[
        "canonical_job_id_preserved"
    ]
    is True,
)


# =========================================================================
# 5. Retry-safe event selection
# =========================================================================

retry_events = [
    {
        "event_id":
            "evt_created",

        "job_id":
            "uj_smoke_5_4",

        "old_status":
            "none",

        "new_status":
            "queued",

        "created_at":
            "2026-09-08T02:00:00+00:00",
    },
    {
        "event_id":
            "evt_running_attempt_1",

        "job_id":
            "uj_smoke_5_4",

        "old_status":
            "queued",

        "new_status":
            "running",

        "created_at":
            "2026-09-08T02:01:00+00:00",
    },
    {
        "event_id":
            "evt_retry",

        "job_id":
            "uj_smoke_5_4",

        "old_status":
            "running",

        "new_status":
            "queued",

        "created_at":
            "2026-09-08T02:02:00+00:00",
    },
    {
        "event_id":
            "evt_running_attempt_2",

        "job_id":
            "uj_smoke_5_4",

        "old_status":
            "queued",

        "new_status":
            "running",

        "created_at":
            "2026-09-08T02:03:00+00:00",
    },
    {
        "event_id":
            "evt_completed_attempt_2",

        "job_id":
            "uj_smoke_5_4",

        "old_status":
            "running",

        "new_status":
            "completed",

        "created_at":
            "2026-09-08T02:04:00+00:00",
    },
]


retry_result = build_runtime_completion_stage_result(
    correlation=
        correlation,

    completion_job=
        completion_job,

    events=
        retry_events,
)


check(
    "Retry result uses latest COMPLETED event",
    retry_result.result_id
    == "evt_completed_attempt_2",
)

check(
    "Retry result uses latest RUNNING event",
    retry_result.started_at
    == "2026-09-08T02:03:00+00:00",
)

check(
    "Retry result ignores older RUNNING attempt",
    retry_result.started_at
    != "2026-09-08T02:01:00+00:00",
)


# =========================================================================
# 6. Identity cross-check failures
# =========================================================================

expect_validation_error(
    "job_id mismatch rejected",
    lambda:
        build_runtime_completion_stage_result(
            correlation=
                correlation,

            completion_job=
                make_completion_job(
                    job_id=
                        "uj_wrong"
                ),

            events=
                events,
        ),
)


expect_validation_error(
    "workspace_id mismatch rejected",
    lambda:
        build_runtime_completion_stage_result(
            correlation=
                correlation,

            completion_job=
                make_completion_job(
                    workspace_id=
                        "ws_wrong"
                ),

            events=
                events,
        ),
)


expect_validation_error(
    "job_type mismatch rejected",
    lambda:
        build_runtime_completion_stage_result(
            correlation=
                correlation,

            completion_job=
                make_completion_job(
                    job_type=
                        "wrong.job"
                ),

            events=
                events,
        ),
)


expect_validation_error(
    "Non-completed job rejected",
    lambda:
        build_runtime_completion_stage_result(
            correlation=
                correlation,

            completion_job=
                make_completion_job(
                    status=
                        "running"
                ),

            events=
                events,
        ),
)


# =========================================================================
# 7. Completion evidence protection
# =========================================================================

expect_validation_error(
    "runtime_dispatch_completed False rejected",
    lambda:
        build_runtime_completion_stage_result(
            correlation=
                correlation,

            completion_job=
                make_completion_job(
                    runtime_dispatch_completed=
                        False
                ),

            events=
                events,
        ),
)


expect_validation_error(
    "canonical_job_id_preserved False rejected",
    lambda:
        build_runtime_completion_stage_result(
            correlation=
                correlation,

            completion_job=
                make_completion_job(
                    canonical_job_id_preserved=
                        False
                ),

            events=
                events,
        ),
)


missing_output_job = (
    make_completion_job()
)

missing_output_job[
    "metadata"
].pop(
    "runtime_dispatch_result"
)


expect_validation_error(
    "Missing runtime_dispatch_result rejected",
    lambda:
        build_runtime_completion_stage_result(
            correlation=
                correlation,

            completion_job=
                missing_output_job,

            events=
                events,
        ),
)


# =========================================================================
# 8. Event evidence protection
# =========================================================================

expect_not_ready(
    "Missing COMPLETED event not ready",
    lambda:
        build_runtime_completion_stage_result(
            correlation=
                correlation,

            completion_job=
                completion_job,

            events=
                events[:-1],
        ),
)


expect_validation_error(
    "Missing RUNNING event rejected",
    lambda:
        build_runtime_completion_stage_result(
            correlation=
                correlation,

            completion_job=
                completion_job,

            events=[
                events[
                    0
                ],
                events[
                    2
                ],
            ],
        ),
)


foreign_events = (
    make_events()
)

foreign_events[
    1
][
    "job_id"
] = "uj_foreign"


expect_validation_error(
    "Foreign event job_id rejected",
    lambda:
        build_runtime_completion_stage_result(
            correlation=
                correlation,

            completion_job=
                completion_job,

            events=
                foreign_events,
        ),
)


# =========================================================================
# 9. Empty optional result references
# =========================================================================

minimal_job = (
    make_completion_job()
)

minimal_job[
    "metadata"
][
    "runtime_dispatch_result"
] = {
    "value":
        "minimal"
}


minimal_result = build_runtime_completion_stage_result(
    correlation=
        correlation,

    completion_job=
        minimal_job,

    events=
        events,
)


check(
    "Missing result_reference becomes empty",
    minimal_result.result_reference
    == "",
)

check(
    "Missing artifact_references becomes empty tuple",
    tuple(
        minimal_result.artifact_references
    )
    == (),
)


# =========================================================================
# 10. Public intake wrapper with injected readers
# =========================================================================

registry = (
    WorkflowJobCorrelationRegistry()
)

registry.register(
    correlation
)


def completion_reader(
    job_id,
):
    check(
        "Injected completion reader receives canonical job_id",
        job_id
        == "uj_smoke_5_4",
    )

    return {
        "job":
            completion_job,

        "events":
            events,
    }


def events_reader_unused(
    job_id,
):
    raise AssertionError(
        "events_reader should not be used when events are embedded"
    )


wrapper_result = intake_runtime_completion(
    job_id=
        "uj_smoke_5_4",

    registry=
        registry,

    completion_reader=
        completion_reader,

    events_reader=
        events_reader_unused,
)


check(
    "Public intake wrapper returns StageResult",
    isinstance(
        wrapper_result,
        UniversalStageResult,
    ),
)

check(
    "Public intake wrapper result_id exact",
    wrapper_result.result_id
    == "evt_completed",
)


expect_not_ready(
    "Missing completion document reports not ready",
    lambda:
        intake_runtime_completion(
            job_id=
                "uj_smoke_5_4",

            registry=
                registry,

            completion_reader=
                lambda job_id: None,

            events_reader=
                lambda job_id: [],
        ),
)


# =========================================================================
# 11. Error inheritance
# =========================================================================

check(
    "Validation error subclasses Phase 5.4 error",
    issubclass(
        RuntimeCompletionValidationError,
        RuntimeCompletionIntakeError,
    ),
)

check(
    "NotReady error subclasses validation error",
    issubclass(
        RuntimeCompletionNotReadyError,
        RuntimeCompletionValidationError,
    ),
)


# =========================================================================
# 12. Architecture declaration
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
    "Architecture scope exact",
    architecture[
        "scope"
    ]
    == "successful Runtime completion only",
)

check(
    "Result identity authority exact",
    architecture[
        "result_id_authority"
    ]
    == "COMPLETED JobStatusEvent.event_id",
)

check(
    "Output authority exact",
    architecture[
        "output_authority"
    ]
    == "runtime_dispatch_result",
)

check(
    "Failure processing delegated to 5.5",
    architecture[
        "failure_processing_owner"
    ]
    == "Phase 5.5 Runtime Failure Intake",
)


for key in (
    "runtime_job_creation",
    "runtime_submission",
    "runtime_status_mutation",
    "runtime_progress_mutation",
    "runtime_dispatch",
    "handler_execution",
    "completion_persistence",
    "failure_processing",
    "random_result_id_generation",
    "wall_clock_timestamp_generation",
    "correlation_creation",
):

    check(
        "Execution authority disabled: "
        + key,
        architecture[
            "execution_properties"
        ][
            key
        ]
        is False,
    )


# =========================================================================
# 13. Static mutation boundary
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
    "execute_registered_runtime_job_v1",
    "run_one_universal_runtime_job_v1",
    "uuid4",
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


forbidden_hits = (
    called
    & forbidden_calls
)


check(
    "No forbidden Runtime/orchestration mutation calls",
    forbidden_hits
    == set(),
    repr(
        sorted(
            forbidden_hits
        )
    ),
)


# =========================================================================
# 14. Candidate SHA
# =========================================================================

candidate_sha = sha256(
    TARGET
)

check(
    "Candidate SHA256 structurally valid",
    (
        len(
            candidate_sha
        )
        == 64
        and all(
            char
            in "0123456789ABCDEF"
            for char
            in candidate_sha
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
    len(
        checks
    )
    - passed
)


lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.4 — RUNTIME COMPLETION INTAKE",
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
            "    "
            + detail
        )


lines.extend(
    (
        "",
        "=" * 120,
        "PHASE 5.4 INSTALLATION SMOKE RESULT",
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
            "PHASE 5.4 CANDIDATE SHA256: "
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
print("PHASE 5.4 INSTALLATION SMOKE RESULT")
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
        "SMOKE PASSED"
        if failed == 0
        else "SMOKE FAILED"
    ),
)
print(
    "PHASE 5.4 CANDIDATE SHA256:",
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
