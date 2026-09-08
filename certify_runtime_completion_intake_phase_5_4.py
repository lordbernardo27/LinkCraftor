from __future__ import annotations

import ast
import hashlib
import inspect
import subprocess
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
    / "runtime_completion_intake_phase_5_4_final_certification.txt"
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


def check(name, condition, detail=""):
    ok = bool(condition)
    checks.append((name, ok, detail))

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

    except RuntimeCompletionValidationError as exc:
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
        "Expected RuntimeCompletionValidationError.",
    )


def make_correlation():
    return WorkflowJobCorrelation(
        workflow_id="wf_final_5_4",
        correlation_id="corr_final_5_4",
        stage_id="stage_final",
        stage_version="stage_final_v1",
        workflow_type="final_workflow",
        workspace_id="ws_final_5_4",
        job_id="uj_final_5_4",
        job_type="final.runtime.stage",
        pipeline_id="pipeline_final",
        runtime_stage="runtime_stage_final",
        wave_index=4,
    )


def make_job():
    return {
        "job_id":
            "uj_final_5_4",

        "workspace_id":
            "ws_final_5_4",

        "job_type":
            "final.runtime.stage",

        "status":
            "completed",

        "metadata": {
            "runtime_dispatch_completed":
                True,

            "canonical_job_id_preserved":
                True,

            "runtime_dispatch_result": {
                "ok":
                    True,

                "value":
                    999,

                "result_reference":
                    "result://final/999",

                "artifact_references": [
                    "artifact://final/a",
                    "artifact://final/b",
                ],
            },
        },
    }


def make_events():
    return [
        {
            "event_id":
                "evt_created",

            "job_id":
                "uj_final_5_4",

            "old_status":
                "none",

            "new_status":
                "queued",

            "created_at":
                "2026-09-08T04:00:00+00:00",
        },
        {
            "event_id":
                "evt_running",

            "job_id":
                "uj_final_5_4",

            "old_status":
                "queued",

            "new_status":
                "running",

            "created_at":
                "2026-09-08T04:01:00+00:00",
        },
        {
            "event_id":
                "evt_completed",

            "job_id":
                "uj_final_5_4",

            "old_status":
                "running",

            "new_status":
                "completed",

            "created_at":
                "2026-09-08T04:02:00+00:00",
        },
    ]


print()
print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 5.4 — RUNTIME COMPLETION INTAKE")
print("FINAL CERTIFICATION")
print("=" * 120)


# =========================================================================
# 1. Artifact integrity
# =========================================================================

target_sha = sha256(TARGET)

check(
    "Phase 5.4 candidate SHA exact",
    target_sha == EXPECTED_TARGET_SHA,
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

    actual = sha256(path)

    check(
        "Authority SHA exact: " + name,
        actual == EXPECTED[name],
        actual,
    )


# =========================================================================
# 2. Contract identity
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
# 3. Canonical successful completion
# =========================================================================

corr = make_correlation()
job = make_job()
events = make_events()

result = build_runtime_completion_stage_result(
    correlation=corr,
    completion_job=job,
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
    "Status COMPLETED",
    result.status
    == UniversalStageResultStatus.COMPLETED,
)

check(
    "result_id exact",
    result.result_id
    == "evt_completed",
)

check(
    "workflow_id exact",
    result.workflow_id
    == corr.workflow_id,
)

check(
    "correlation_id exact",
    result.correlation_id
    == corr.correlation_id,
)

check(
    "stage_id exact",
    result.stage_id
    == corr.stage_id,
)

check(
    "stage_version exact",
    result.stage_version
    == corr.stage_version,
)

check(
    "pipeline_id exact",
    result.pipeline_id
    == corr.pipeline_id,
)

check(
    "workflow_type exact",
    result.workflow_type
    == corr.workflow_type,
)

check(
    "workspace_id exact",
    result.workspace_id
    == corr.workspace_id,
)

check(
    "job_id exact",
    result.job_id
    == corr.job_id,
)

check(
    "job_type exact",
    result.job_type
    == corr.job_type,
)

check(
    "execution target exact",
    getattr(
        result.execution_target,
        "value",
        result.execution_target,
    )
    == "universal_runtime",
)

check(
    "started_at exact",
    result.started_at
    == "2026-09-08T04:01:00+00:00",
)

check(
    "finished_at exact",
    result.finished_at
    == "2026-09-08T04:02:00+00:00",
)

check(
    "Output exact",
    result.output[
        "value"
    ]
    == 999,
)

check(
    "result_reference exact",
    result.result_reference
    == "result://final/999",
)

check(
    "artifact references exact",
    tuple(
        result.artifact_references
    )
    == (
        "artifact://final/a",
        "artifact://final/b",
    ),
)


# =========================================================================
# 4. Strict transition semantics
# =========================================================================

bad_completion = make_events()

bad_completion[
    2
][
    "old_status"
] = "queued"


expect_validation_error(
    "Invalid completion transition rejected",
    lambda:
        build_runtime_completion_stage_result(
            correlation=corr,
            completion_job=job,
            events=bad_completion,
        ),
)


bad_running = make_events()

bad_running[
    1
][
    "old_status"
] = "completed"


expect_validation_error(
    "Invalid RUNNING transition rejected",
    lambda:
        build_runtime_completion_stage_result(
            correlation=corr,
            completion_job=job,
            events=bad_running,
        ),
)


# =========================================================================
# 5. Retry-safe attempt isolation
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
            "2026-09-08T04:00:00+00:00",
    },
    {
        "event_id":
            "evt_r1",
        "job_id":
            corr.job_id,
        "old_status":
            "queued",
        "new_status":
            "running",
        "created_at":
            "2026-09-08T04:01:00+00:00",
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
            "2026-09-08T04:02:00+00:00",
    },
    {
        "event_id":
            "evt_r2",
        "job_id":
            corr.job_id,
        "old_status":
            "queued",
        "new_status":
            "running",
        "created_at":
            "2026-09-08T04:03:00+00:00",
    },
    {
        "event_id":
            "evt_done",
        "job_id":
            corr.job_id,
        "old_status":
            "running",
        "new_status":
            "completed",
        "created_at":
            "2026-09-08T04:04:00+00:00",
    },
]


retry_result = build_runtime_completion_stage_result(
    correlation=corr,
    completion_job=job,
    events=retry_events,
)


check(
    "Retry result_id final attempt exact",
    retry_result.result_id
    == "evt_done",
)

check(
    "Retry started_at final attempt exact",
    retry_result.started_at
    == "2026-09-08T04:03:00+00:00",
)

check(
    "Retry finished_at final attempt exact",
    retry_result.finished_at
    == "2026-09-08T04:04:00+00:00",
)


# =========================================================================
# 6. Timestamp integrity
# =========================================================================

reverse_times = make_events()

reverse_times[
    1
][
    "created_at"
] = "2026-09-08T04:05:00+00:00"


expect_validation_error(
    "Reversed timestamps rejected by Phase 5.4",
    lambda:
        build_runtime_completion_stage_result(
            correlation=corr,
            completion_job=job,
            events=reverse_times,
        ),
)


invalid_time = make_events()

invalid_time[
    2
][
    "created_at"
] = "not-a-timestamp"


expect_validation_error(
    "Invalid timestamp rejected by Phase 5.4",
    lambda:
        build_runtime_completion_stage_result(
            correlation=corr,
            completion_job=job,
            events=invalid_time,
        ),
)


# =========================================================================
# 7. Runtime evidence strictness
# =========================================================================

for key in (
    "runtime_dispatch_completed",
    "canonical_job_id_preserved",
):

    bad_job = make_job()

    bad_job[
        "metadata"
    ][
        key
    ] = False

    expect_validation_error(
        key + " false rejected",
        lambda bad_job=bad_job:
            build_runtime_completion_stage_result(
                correlation=corr,
                completion_job=bad_job,
                events=events,
            ),
    )


# =========================================================================
# 8. Cross-correlation protection
# =========================================================================

for field_name, wrong_value in (
    (
        "job_id",
        "wrong_job",
    ),
    (
        "workspace_id",
        "wrong_workspace",
    ),
    (
        "job_type",
        "wrong.job",
    ),
):

    bad_job = make_job()
    bad_job[
        field_name
    ] = wrong_value

    expect_validation_error(
        field_name + " mismatch rejected",
        lambda bad_job=bad_job:
            build_runtime_completion_stage_result(
                correlation=corr,
                completion_job=bad_job,
                events=events,
            ),
    )


# =========================================================================
# 9. Wrapper behavior
# =========================================================================

registry = WorkflowJobCorrelationRegistry()

registry.register(
    corr
)


wrapper_result = intake_runtime_completion(
    job_id=corr.job_id,
    registry=registry,
    completion_reader=lambda job_id: {
        "job":
            job,

        "events":
            events,
    },
    events_reader=lambda job_id: (
        (_ for _ in ())
        .throw(
            AssertionError(
                "embedded events should be used"
            )
        )
    ),
)


check(
    "Wrapper result exact",
    wrapper_result
    == result,
)


# =========================================================================
# 10. API/error boundaries
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
    "Wrapper keyword-only",
    str(
        inspect.signature(
            intake_runtime_completion
        )
    ).startswith(
        "(*,"
    ),
)

check(
    "Validation error inheritance",
    issubclass(
        RuntimeCompletionValidationError,
        RuntimeCompletionIntakeError,
    ),
)

check(
    "NotReady error inheritance",
    issubclass(
        RuntimeCompletionNotReadyError,
        RuntimeCompletionValidationError,
    ),
)


# =========================================================================
# 11. Architecture declaration
# =========================================================================

architecture = explain_runtime_completion_intake_v5_4()

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
    "Completion authority exact",
    architecture[
        "completion_status_authority"
    ]
    == "canonical orchestration persisted job",
)

check(
    "Event authority exact",
    architecture[
        "completion_event_authority"
    ]
    == "orchestration JobStatusEvent trail",
)

check(
    "Failure delegated to 5.5",
    architecture[
        "failure_processing_owner"
    ]
    == "Phase 5.5 Runtime Failure Intake",
)


# =========================================================================
# 12. Static authority isolation
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
# 13. Git scope protection
# =========================================================================

git_status = subprocess.run(
    [
        "git",
        "status",
        "--short",
        "--",
        "backend/server/coordination/runtime_integration",
        "backend/server/runtime",
        "backend/server/orchestration",
        "backend/server/coordination/universal_stages",
    ],
    cwd=ROOT,
    capture_output=True,
    text=True,
    check=True,
).stdout.strip()


status_lines = tuple(
    line
    for line
    in git_status.splitlines()
    if line.strip()
)


check(
    "No Runtime production modification",
    not any(
        "backend/server/runtime/"
        in line.replace(
            "\\",
            "/",
        )
        for line
        in status_lines
    ),
    repr(
        status_lines
    ),
)

check(
    "No orchestration production modification",
    not any(
        "backend/server/orchestration/"
        in line.replace(
            "\\",
            "/",
        )
        for line
        in status_lines
    ),
    repr(
        status_lines
    ),
)

check(
    "No StageResult production modification",
    not any(
        "backend/server/coordination/universal_stages/"
        in line.replace(
            "\\",
            "/",
        )
        for line
        in status_lines
    ),
    repr(
        status_lines
    ),
)

check(
    "Scoped production change is Phase 5.4 only",
    all(
        (
            "backend/server/coordination/runtime_integration/"
            "runtime_completion_intake.py"
        )
        in line.replace(
            "\\",
            "/",
        )
        for line
        in status_lines
    )
    if status_lines
    else False,
    repr(
        status_lines
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
    "FINAL CERTIFICATION",
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
        "FINAL CERTIFICATION RESULT",
        "=" * 120,
        f"Checks: {len(checks)}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        (
            "CERTIFIED: TRUE"
            if failed == 0
            else "CERTIFIED: FALSE"
        ),
        (
            "STATUS: FINAL CERTIFICATION PASSED"
            if failed == 0
            else "STATUS: FINAL CERTIFICATION FAILED"
        ),
        (
            "VERSION: "
            + RUNTIME_COMPLETION_INTAKE_VERSION
        ),
        (
            "SCHEMA: "
            + RUNTIME_COMPLETION_INTAKE_SCHEMA_VERSION
        ),
        (
            "SHA256: "
            + target_sha
        ),
        (
            "NEXT: 5.4.8 SHA256 Freeze"
            if failed == 0
            else "NEXT: Resolve certification failures"
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
print("PHASE 5.4 FINAL CERTIFICATION RESULT")
print("=" * 120)
print("Checks:", len(checks))
print("Passed:", passed)
print("Failed:", failed)
print(
    "CERTIFIED:",
    failed == 0,
)
print(
    "VERSION:",
    RUNTIME_COMPLETION_INTAKE_VERSION,
)
print(
    "SCHEMA:",
    RUNTIME_COMPLETION_INTAKE_SCHEMA_VERSION,
)
print(
    "SHA256:",
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
