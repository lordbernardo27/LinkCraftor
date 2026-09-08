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
    / "runtime_failure_intake_phase_5_5_final_certification.txt"
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
        workflow_id="wf_final_5_5",
        correlation_id="corr_final_5_5",
        stage_id="stage_final_failure",
        stage_version="stage_final_failure_v1",
        workflow_type="final_failure_workflow",
        workspace_id="ws_final_5_5",
        job_id="uj_final_5_5",
        job_type="final.failure.stage",
        pipeline_id="pipeline_final_failure",
        runtime_stage="runtime_stage_final_failure",
        wave_index=5,
    )


def make_metadata():
    return {
        "worker_id":
            "worker_final",

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
    error_message="TimeoutError: final timeout",
    job_id="uj_final_5_5",
    workspace_id="ws_final_5_5",
    job_type="final.failure.stage",
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
                "evt_final_created",

            "job_id":
                "uj_final_5_5",

            "old_status":
                "none",

            "new_status":
                "queued",

            "created_at":
                "2026-09-08T07:00:00+00:00",
        },
        {
            "event_id":
                "evt_final_running",

            "job_id":
                "uj_final_5_5",

            "old_status":
                "queued",

            "new_status":
                "running",

            "created_at":
                "2026-09-08T07:01:00+00:00",
        },
        {
            "event_id":
                "evt_final_failed",

            "job_id":
                "uj_final_5_5",

            "old_status":
                "running",

            "new_status":
                "failed",

            "created_at":
                "2026-09-08T07:02:00+00:00",
        },
    ]


print()
print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 5.5 — RUNTIME FAILURE INTAKE")
print("FINAL CERTIFICATION")
print("=" * 120)


# =========================================================================
# 1. Candidate and authority integrity
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
# 2. Public contract identity
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
    "NotReady error inheritance",
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
    == "evt_final_failed",
)

check(
    "started_at exact",
    result.started_at
    == "2026-09-08T07:01:00+00:00",
)

check(
    "finished_at exact",
    result.finished_at
    == "2026-09-08T07:02:00+00:00",
)

check(
    "failure_code exact",
    result.failure_code
    == "TimeoutError",
)

check(
    "failure_message exact",
    result.failure_message
    == "TimeoutError: final timeout",
)

check(
    "output empty exact",
    dict(result.output) == {},
)

check(
    "result_reference empty exact",
    result.result_reference == "",
)

check(
    "artifact_references empty exact",
    tuple(result.artifact_references) == (),
)


# =========================================================================
# 4. Exact identity preservation
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
        "Identity exact: " + field,
        getattr(result, field)
        == getattr(corr, field),
    )


# =========================================================================
# 5. Complete canonical failure evidence
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
    "Failure details exact key set",
    set(result.failure_details)
    == set(required_detail_keys),
)


for key in required_detail_keys:

    check(
        "Failure evidence preserved: " + key,
        result.failure_details[key]
        == make_metadata()[key],
    )


for key in required_detail_keys:

    bad_metadata = make_metadata()

    bad_metadata.pop(
        key
    )

    if key == "runtime_retry_scheduled":
        expect_not_ready(
            "Missing terminal proof rejected: " + key,
            lambda bad_metadata=bad_metadata:
                build_runtime_failure_stage_result(
                    correlation=corr,
                    failure_job=make_job(
                        metadata=bad_metadata
                    ),
                    events=events,
                ),
        )

    else:
        expect_validation_error(
            "Missing canonical evidence rejected: " + key,
            lambda bad_metadata=bad_metadata:
                build_runtime_failure_stage_result(
                    correlation=corr,
                    failure_job=make_job(
                        metadata=bad_metadata
                    ),
                    events=events,
                ),
        )


# =========================================================================
# 6. Literal terminal proof
# =========================================================================

for key, bad_value in (
    ("runtime_dispatch_failed", 1),
    ("runtime_dispatch_completed", 0),
    ("runtime_retry_scheduled", 0),
    ("canonical_job_id_preserved", 1),
    ("retry_created_new_job", 0),
):

    bad_metadata = make_metadata()
    bad_metadata[key] = bad_value

    if key == "runtime_retry_scheduled":

        expect_not_ready(
            key + " literal False required",
            lambda bad_metadata=bad_metadata:
                build_runtime_failure_stage_result(
                    correlation=corr,
                    failure_job=make_job(
                        metadata=bad_metadata
                    ),
                    events=events,
                ),
        )

    else:

        expect_validation_error(
            key + " literal enforcement",
            lambda bad_metadata=bad_metadata:
                build_runtime_failure_stage_result(
                    correlation=corr,
                    failure_job=make_job(
                        metadata=bad_metadata
                    ),
                    events=events,
                ),
        )


# =========================================================================
# 7. Retryable state rejection
# =========================================================================

retry_metadata = make_metadata()
retry_metadata["runtime_retry_scheduled"] = True


expect_not_ready(
    "Retry scheduled cannot emit terminal failure",
    lambda:
        build_runtime_failure_stage_result(
            correlation=corr,
            failure_job=make_job(
                metadata=retry_metadata
            ),
            events=events,
        ),
)


expect_validation_error(
    "QUEUED state cannot emit FAILED result",
    lambda:
        build_runtime_failure_stage_result(
            correlation=corr,
            failure_job=make_job(
                status="queued"
            ),
            events=events,
        ),
)


# =========================================================================
# 8. Transition integrity
# =========================================================================

bad_failed = make_events()
bad_failed[2]["old_status"] = "queued"


expect_validation_error(
    "FAILED transition must be RUNNING->FAILED",
    lambda:
        build_runtime_failure_stage_result(
            correlation=corr,
            failure_job=job,
            events=bad_failed,
        ),
)


bad_running = make_events()
bad_running[1]["old_status"] = "failed"


expect_validation_error(
    "RUNNING transition must be QUEUED->RUNNING",
    lambda:
        build_runtime_failure_stage_result(
            correlation=corr,
            failure_job=job,
            events=bad_running,
        ),
)


corrupt_latest = make_events()

corrupt_latest.append(
    {
        "event_id":
            "evt_corrupt_latest_failed",

        "job_id":
            corr.job_id,

        "old_status":
            "queued",

        "new_status":
            "failed",

        "created_at":
            "2026-09-08T07:03:00+00:00",
    }
)


expect_validation_error(
    "Corrupt latest FAILED event fails closed",
    lambda:
        build_runtime_failure_stage_result(
            correlation=corr,
            failure_job=job,
            events=corrupt_latest,
        ),
)


# =========================================================================
# 9. Retry-attempt selection
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
            "2026-09-08T07:00:00+00:00",
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
            "2026-09-08T07:01:00+00:00",
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
            "2026-09-08T07:02:00+00:00",
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
            "2026-09-08T07:03:00+00:00",
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
            "2026-09-08T07:04:00+00:00",
    },
]


retry_result = build_runtime_failure_stage_result(
    correlation=corr,
    failure_job=job,
    events=retry_events,
)


check(
    "Retry final result_id exact",
    retry_result.result_id
    == "evt_failed_2",
)

check(
    "Retry final started_at exact",
    retry_result.started_at
    == "2026-09-08T07:03:00+00:00",
)

check(
    "Retry final finished_at exact",
    retry_result.finished_at
    == "2026-09-08T07:04:00+00:00",
)


# =========================================================================
# 10. Timestamp validation
# =========================================================================

reverse = make_events()
reverse[1]["created_at"] = (
    "2026-09-08T07:05:00+00:00"
)


expect_validation_error(
    "Reverse timestamp rejected",
    lambda:
        build_runtime_failure_stage_result(
            correlation=corr,
            failure_job=job,
            events=reverse,
        ),
)


invalid = make_events()
invalid[2]["created_at"] = "invalid"


expect_validation_error(
    "Invalid timestamp rejected",
    lambda:
        build_runtime_failure_stage_result(
            correlation=corr,
            failure_job=job,
            events=invalid,
        ),
)


# =========================================================================
# 11. Wrapper ordering and behavior
# =========================================================================

empty_registry = WorkflowJobCorrelationRegistry()

reads = []


def should_not_read(job_id):
    reads.append(job_id)

    return {
        "job": job,
        "events": events,
    }


try:
    intake_runtime_failure(
        job_id=corr.job_id,
        registry=empty_registry,
        failure_reader=should_not_read,
        events_reader=lambda job_id: events,
    )

except Exception:
    pass


check(
    "Correlation lookup precedes Runtime read",
    reads == [],
    repr(reads),
)


registry = WorkflowJobCorrelationRegistry()
registry.register(corr)


wrapped = intake_runtime_failure(
    job_id=corr.job_id,
    registry=registry,
    failure_reader=lambda job_id: {
        "job":
            job,

        "events":
            events,
    },
    events_reader=lambda job_id:
        (_ for _ in ())
        .throw(
            AssertionError(
                "embedded events must be used"
            )
        ),
)


check(
    "Wrapper equals builder result",
    wrapped == result,
)


# =========================================================================
# 12. Architecture declaration
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
    architecture["phase"] == "5.5",
)

check(
    "Architecture scope exact",
    architecture["scope"]
    == "terminal Runtime failure only",
)

check(
    "Terminal status authority exact",
    architecture["terminal_status_authority"]
    == "canonical orchestration persisted job",
)

check(
    "Terminal event authority exact",
    architecture["terminal_event_authority"]
    == "RUNNING -> FAILED JobStatusEvent",
)

check(
    "Attempt start authority exact",
    architecture["attempt_start_authority"]
    == "QUEUED -> RUNNING JobStatusEvent",
)

check(
    "Failure code authority exact",
    architecture["failure_code_authority"]
    == "runtime_dispatch_error_type",
)

check(
    "Failure message authority exact",
    architecture["failure_message_authority"]
    == "persisted orchestration job.error_message",
)

check(
    "Workflow recovery owner exact",
    architecture["workflow_recovery_owner"]
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
# 13. Static read-only boundaries
# =========================================================================

source = TARGET.read_text(
    encoding="utf-8"
)

tree = ast.parse(source)


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


for node in ast.walk(tree):

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


hits = called & forbidden_calls


check(
    "No forbidden mutation/execution calls",
    hits == set(),
    repr(sorted(hits)),
)


# =========================================================================
# 14. Git production-scope protection
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
        in line.replace("\\", "/")
        for line in status_lines
    ),
    repr(status_lines),
)

check(
    "No orchestration production modification",
    not any(
        "backend/server/orchestration/"
        in line.replace("\\", "/")
        for line in status_lines
    ),
    repr(status_lines),
)

check(
    "No StageResult production modification",
    not any(
        "backend/server/coordination/universal_stages/"
        in line.replace("\\", "/")
        for line in status_lines
    ),
    repr(status_lines),
)

allowed_runtime_integration = {
    "backend/server/coordination/runtime_integration/"
    "runtime_completion_intake.py",

    "backend/server/coordination/runtime_integration/"
    "runtime_completion_intake.freeze.json",

    "backend/server/coordination/runtime_integration/"
    "runtime_failure_intake.py",
}


unexpected = []


for line in status_lines:

    normalized = line.replace(
        "\\",
        "/",
    )

    path = normalized[3:].strip()

    if (
        "backend/server/coordination/runtime_integration/"
        in normalized
        and path not in allowed_runtime_integration
    ):
        unexpected.append(
            normalized
        )


check(
    "Runtime integration scope contains no unexpected production file",
    unexpected == [],
    repr(unexpected),
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

failed = len(checks) - passed


lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.5 — RUNTIME FAILURE INTAKE",
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
            "    " + detail
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
            + RUNTIME_FAILURE_INTAKE_VERSION
        ),
        (
            "SCHEMA: "
            + RUNTIME_FAILURE_INTAKE_SCHEMA_VERSION
        ),
        (
            "SHA256: "
            + target_sha
        ),
        (
            "NEXT: 5.5.8 SHA256 Freeze"
            if failed == 0
            else "NEXT: Resolve certification failures"
        ),
    )
)


REPORT.write_text(
    "\n".join(lines)
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 120)
print("PHASE 5.5 FINAL CERTIFICATION RESULT")
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
    RUNTIME_FAILURE_INTAKE_VERSION,
)
print(
    "SCHEMA:",
    RUNTIME_FAILURE_INTAKE_SCHEMA_VERSION,
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
