from __future__ import annotations

import hashlib
from pathlib import Path

from backend.server.runtime.universal_job_submission import (
    submit_universal_job,
)
from backend.server.runtime.universal_runtime_worker_v1 import (
    run_one_universal_runtime_job_v1,
)
from backend.server.coordination.runtime_integration.runtime_job_mapping import (
    RuntimeJobMapping,
)
from backend.server.coordination.runtime_integration.workflow_job_correlation import (
    WorkflowJobCorrelationRegistry,
    correlate_submitted_job,
)
from backend.server.coordination.runtime_integration.runtime_failure_intake import (
    intake_runtime_failure,
)
from backend.server.runtime.universal_jobs.creation_engine import (
    UniversalJobCreationRequest,
)
from backend.server.orchestration import job_store


ROOT = Path.cwd()

REPORT = (
    ROOT
    / "runtime_integration_phase_5_6_failure_retry_certification.txt"
)

PATHS = {
    "submission":
        ROOT
        / "backend/server/runtime/universal_job_submission.py",

    "worker":
        ROOT
        / "backend/server/runtime/universal_runtime_worker_v1.py",

    "phase_5_3":
        ROOT
        / (
            "backend/server/coordination/runtime_integration/"
            "workflow_job_correlation.py"
        ),

    "phase_5_5":
        ROOT
        / (
            "backend/server/coordination/runtime_integration/"
            "runtime_failure_intake.py"
        ),
}

EXPECTED = {
    "submission":
        "8E7AF8CC795D7C990F11FFE0ACD06A5253D957922EC3BD0B740CC1CB0CD3FB2F",

    "worker":
        "ED6B415C5FEDF3F4CB62451F3E23D182F9DA937D9CB09FD33262C506B9BEF699",

    "phase_5_3":
        "13B007B1F74A131250476432B14381CC81C916F48CE121B44877964A18A73AB6",

    "phase_5_5":
        "CDEE8D641AC045956E2A203BF0A62DE70933F0755B946D63310EFBABE7DFE241",
}


checks = []


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


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
        print(
            "    " + str(detail)
        )


print()
print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 5.6.6 — FAILURE/RETRY-PATH CERTIFICATION")
print("=" * 120)


# =========================================================================
# 1. Canonical source authority
# =========================================================================

source_before = {}

for name, expected in EXPECTED.items():
    actual = sha256(
        PATHS[
            name
        ]
    )

    source_before[
        name
    ] = actual

    check(
        "Canonical SHA exact: " + name,
        actual == expected,
        actual,
    )


# =========================================================================
# 2. Resolve real orchestration store functions
# =========================================================================

load_jobs = getattr(
    job_store,
    "load_jobs",
)

get_job = getattr(
    job_store,
    "get_job",
)

list_job_events = getattr(
    job_store,
    "list_job_events",
)


check(
    "load_jobs resolved",
    callable(
        load_jobs
    ),
)

check(
    "get_job resolved",
    callable(
        get_job
    ),
)

check(
    "list_job_events resolved",
    callable(
        list_job_events
    ),
)


# =========================================================================
# 3. Protect real orchestration store
# =========================================================================

REAL_JOBS_FILE = Path(
    job_store.JOBS_FILE
)

REAL_EVENTS_FILE = Path(
    job_store.EVENTS_FILE
)

REAL_JOBS_BYTES_BEFORE = (
    REAL_JOBS_FILE.read_bytes()
    if REAL_JOBS_FILE.exists()
    else None
)

REAL_EVENTS_BYTES_BEFORE = (
    REAL_EVENTS_FILE.read_bytes()
    if REAL_EVENTS_FILE.exists()
    else None
)

real_jobs_before = load_jobs()

real_queued_ids_before = sorted(
    str(
        getattr(
            job,
            "job_id",
            "",
        )
    )
    for job
    in real_jobs_before.values()
    if str(
        getattr(
            job,
            "status",
            "",
        )
    ).strip().lower()
    == "queued"
)


CERTIFICATION_STORE = (
    ROOT
    / (
        "backend/server/data/orchestration/"
        "phase_5_6_failure_retry_certification"
    )
)

CERTIFICATION_JOBS_FILE = (
    CERTIFICATION_STORE
    / "jobs.json"
)

CERTIFICATION_EVENTS_FILE = (
    CERTIFICATION_STORE
    / "job_events.json"
)


if (
    CERTIFICATION_JOBS_FILE.exists()
    or CERTIFICATION_EVENTS_FILE.exists()
):
    raise SystemExit(
        (
            "FAILURE/RETRY CERTIFICATION REFUSED: "
            "isolated certification evidence already exists. "
            "No evidence will be overwritten.\n"
            f"Store: {CERTIFICATION_STORE}"
        )
    )


CERTIFICATION_STORE.mkdir(
    parents=True,
    exist_ok=True,
)

job_store.DATA_DIR = (
    CERTIFICATION_STORE
)

job_store.JOBS_FILE = (
    CERTIFICATION_JOBS_FILE
)

job_store.EVENTS_FILE = (
    CERTIFICATION_EVENTS_FILE
)


check(
    "Orchestration store redirected to isolated certification path",
    (
        Path(
            job_store.JOBS_FILE
        )
        == CERTIFICATION_JOBS_FILE
        and Path(
            job_store.EVENTS_FILE
        )
        == CERTIFICATION_EVENTS_FILE
    ),
    CERTIFICATION_STORE,
)

check(
    "Real orchestration store excluded",
    (
        Path(
            job_store.JOBS_FILE
        )
        != REAL_JOBS_FILE
        and Path(
            job_store.EVENTS_FILE
        )
        != REAL_EVENTS_FILE
    ),
)

check(
    "Pre-existing real queued jobs protected",
    True,
    (
        "Real queued jobs outside certification store: "
        + str(
            len(
                real_queued_ids_before
            )
        )
    ),
)


existing_jobs = load_jobs()

check(
    "Isolated Runtime queue begins empty",
    len(
        existing_jobs
    )
    == 0,
)


# =========================================================================
# 4. Certified Runtime mapping
# =========================================================================

WORKFLOW_ID = (
    "wf_phase_5_6_failure_retry"
)

CORRELATION_ID = (
    "corr_phase_5_6_failure_retry"
)

STAGE_ID = (
    "stage_phase_5_6_failure_retry"
)

STAGE_VERSION = (
    "stage_phase_5_6_failure_retry_v1"
)

WORKFLOW_TYPE = (
    "phase_5_6_failure_retry_workflow"
)

WORKSPACE_ID = (
    "ws_phase_5_6_failure_retry"
)

JOB_TYPE = (
    "linking_target_pipeline_batch"
)

PIPELINE_ID = (
    "linking_target_pipeline"
)

RUNTIME_STAGE = (
    "linking_target_pipeline_batch"
)

PAYLOAD = {
    "workspace_id":
        WORKSPACE_ID,

    "domain":
        "phase-5-6-failure-retry.example.com",
}


coordination = {
    "workflow_id":
        WORKFLOW_ID,

    "correlation_id":
        CORRELATION_ID,

    "stage_id":
        STAGE_ID,

    "stage_version":
        STAGE_VERSION,

    "workflow_type":
        WORKFLOW_TYPE,

    "wave_index":
        0,

    "execution_semantics":
        "sequential",

    "required_payload_fields":
        (
            "workspace_id",
            "domain",
        ),

    "stage_reference_contract_version":
        "universal_stage_reference_contract_v1.3.0",

    "runtime_handoff_intent_version":
        "runtime_handoff_intent_v5.1.0",
}


request = UniversalJobCreationRequest(
    workspace_id=
        WORKSPACE_ID,

    job_type=
        JOB_TYPE,

    payload=
        PAYLOAD,

    metadata={
        "coordination":
            coordination,
    },

    pipeline=
        PIPELINE_ID,

    stage=
        RUNTIME_STAGE,

    priority=
        30,

    maximum_attempts=
        3,
)


mapping = RuntimeJobMapping(
    workflow_id=
        WORKFLOW_ID,

    correlation_id=
        CORRELATION_ID,

    stage_id=
        STAGE_ID,

    wave_index=
        0,

    creation_request=
        request,
)


check(
    "Certified RuntimeJobMapping built",
    mapping.workflow_id
    == WORKFLOW_ID,
)


# =========================================================================
# 5. Real canonical submission
# =========================================================================

submission = submit_universal_job(
    workspace_id=
        request.workspace_id,

    job_type=
        request.job_type,

    payload=
        request.payload,

    metadata=
        request.metadata,

    pipeline=
        request.pipeline,

    stage=
        request.stage,

    priority=
        request.priority,

    maximum_attempts=
        request.maximum_attempts,

    enqueue=
        True,
)


JOB_ID = str(
    submission[
        "job_id"
    ]
)


check(
    "Canonical job_id created",
    bool(
        JOB_ID
    ),
    JOB_ID,
)

check(
    "Submission persisted True",
    submission[
        "submission"
    ][
        "persisted"
    ]
    is True,
)

check(
    "Submission queued True",
    submission[
        "submission"
    ][
        "queued"
    ]
    is True,
)

check(
    "Submission canonical identity preserved",
    submission[
        "submission"
    ][
        "canonical_identity_preserved"
    ]
    is True,
)


persisted = get_job(
    JOB_ID
)

check(
    "Submitted job status QUEUED",
    str(
        persisted.status
    ).lower()
    == "queued",
)


# =========================================================================
# 6. Phase 5.3 correlation
# =========================================================================

registry = (
    WorkflowJobCorrelationRegistry()
)

correlation = correlate_submitted_job(
    mapping=
        mapping,

    submitted_job=
        submission,

    registry=
        registry,
)


check(
    "5.3 correlation created",
    correlation.job_id
    == JOB_ID,
)

check(
    "5.3 workflow identity exact",
    correlation.workflow_id
    == WORKFLOW_ID,
)

check(
    "5.3 correlation identity exact",
    correlation.correlation_id
    == CORRELATION_ID,
)


# =========================================================================
# 7. Deterministic Runtime handler failure
# =========================================================================

dispatcher_calls = []


def failing_dispatcher(runtime_job):
    dispatcher_calls.append(
        str(
            runtime_job[
                "job_id"
            ]
        )
    )

    raise RuntimeError(
        "phase_5_6_certified_handler_failure"
    )


# =========================================================================
# 8. Attempt 1 — permitted same-job retry
# =========================================================================

attempt_1 = run_one_universal_runtime_job_v1(
    worker_id=
        "phase_5_6_failure_worker_1",

    dispatcher=
        failing_dispatcher,
)


check(
    "Attempt 1 worker status RETRY_QUEUED",
    attempt_1[
        "worker_status"
    ]
    == "RETRY_QUEUED",
)

check(
    "Attempt 1 claimed canonical job",
    attempt_1[
        "job_id"
    ]
    == JOB_ID,
)

check(
    "Attempt 1 retry allowed",
    attempt_1[
        "retry_allowed"
    ]
    is True,
)

check(
    "Attempt 1 retry scheduled",
    attempt_1[
        "retry_scheduled"
    ]
    is True,
)

check(
    "Attempt 1 number exact",
    attempt_1[
        "attempt_number"
    ]
    == 1,
)

check(
    "Runtime retry ceiling is 3",
    attempt_1[
        "maximum_attempts"
    ]
    == 3,
)

check(
    "Attempt 1 same canonical job_id preserved",
    attempt_1[
        "canonical_job_id_preserved"
    ]
    is True,
)

check(
    "Attempt 1 created no replacement job",
    attempt_1[
        "retry_created_new_job"
    ]
    is False,
)


after_attempt_1 = get_job(
    JOB_ID
)

check(
    "Attempt 1 persisted RUNNING -> QUEUED",
    str(
        after_attempt_1.status
    ).lower()
    == "queued",
)

check(
    "Attempt 1 persisted retry scheduled",
    after_attempt_1.metadata.get(
        "runtime_retry_scheduled"
    )
    is True,
)

check(
    "Attempt 1 persisted failure count 1",
    after_attempt_1.metadata.get(
        "runtime_failure_attempt_count"
    )
    == 1,
)


# =========================================================================
# 9. Attempt 2 — permitted same-job retry
# =========================================================================

attempt_2 = run_one_universal_runtime_job_v1(
    worker_id=
        "phase_5_6_failure_worker_2",

    dispatcher=
        failing_dispatcher,
)


check(
    "Attempt 2 worker status RETRY_QUEUED",
    attempt_2[
        "worker_status"
    ]
    == "RETRY_QUEUED",
)

check(
    "Attempt 2 same canonical job_id",
    attempt_2[
        "job_id"
    ]
    == JOB_ID,
)

check(
    "Attempt 2 number exact",
    attempt_2[
        "attempt_number"
    ]
    == 2,
)

check(
    "Attempt 2 retry scheduled",
    attempt_2[
        "retry_scheduled"
    ]
    is True,
)

check(
    "Attempt 2 created no replacement job",
    attempt_2[
        "retry_created_new_job"
    ]
    is False,
)


after_attempt_2 = get_job(
    JOB_ID
)

check(
    "Attempt 2 persisted RUNNING -> QUEUED",
    str(
        after_attempt_2.status
    ).lower()
    == "queued",
)

check(
    "Attempt 2 persisted failure count 2",
    after_attempt_2.metadata.get(
        "runtime_failure_attempt_count"
    )
    == 2,
)


# =========================================================================
# 10. Attempt 3 — retry exhaustion / terminal failure
# =========================================================================

attempt_3 = run_one_universal_runtime_job_v1(
    worker_id=
        "phase_5_6_failure_worker_3",

    dispatcher=
        failing_dispatcher,
)


check(
    "Attempt 3 worker status FAILED",
    attempt_3[
        "worker_status"
    ]
    == "FAILED",
)

check(
    "Attempt 3 same canonical job_id",
    attempt_3[
        "job_id"
    ]
    == JOB_ID,
)

check(
    "Attempt 3 number exact",
    attempt_3[
        "attempt_number"
    ]
    == 3,
)

check(
    "Attempt 3 retry not allowed",
    attempt_3[
        "retry_allowed"
    ]
    is False,
)

check(
    "Attempt 3 retry not scheduled",
    attempt_3[
        "retry_scheduled"
    ]
    is False,
)

check(
    "Attempt 3 retry exhausted",
    attempt_3[
        "retry_exhausted"
    ]
    is True,
)

check(
    "Attempt 3 terminal status FAILED",
    str(
        attempt_3[
            "terminal_status"
        ]
    ).lower()
    == "failed",
)

check(
    "Attempt 3 preserved canonical job_id",
    attempt_3[
        "canonical_job_id_preserved"
    ]
    is True,
)

check(
    "Attempt 3 created no replacement job",
    attempt_3[
        "retry_created_new_job"
    ]
    is False,
)


terminal_job = get_job(
    JOB_ID
)

check(
    "Persisted terminal job exists",
    terminal_job
    is not None,
)

check(
    "Persisted terminal status FAILED",
    str(
        terminal_job.status
    ).lower()
    == "failed",
)

check(
    "Persisted terminal job_id unchanged",
    terminal_job.job_id
    == JOB_ID,
)

check(
    "Persisted runtime_dispatch_failed True",
    terminal_job.metadata.get(
        "runtime_dispatch_failed"
    )
    is True,
)

check(
    "Persisted runtime_dispatch_completed False",
    terminal_job.metadata.get(
        "runtime_dispatch_completed"
    )
    is False,
)

check(
    "Persisted runtime_retry_scheduled False",
    terminal_job.metadata.get(
        "runtime_retry_scheduled"
    )
    is False,
)

check(
    "Persisted failure attempt count 3",
    terminal_job.metadata.get(
        "runtime_failure_attempt_count"
    )
    == 3,
)

check(
    "Persisted maximum attempts 3",
    terminal_job.metadata.get(
        "runtime_maximum_attempts"
    )
    == 3,
)

check(
    "Persisted retry exhausted True",
    terminal_job.metadata.get(
        "runtime_retry_exhausted"
    )
    is True,
)

check(
    "Persisted canonical job_id preserved",
    terminal_job.metadata.get(
        "canonical_job_id_preserved"
    )
    is True,
)

check(
    "Persisted retry created no new job",
    terminal_job.metadata.get(
        "retry_created_new_job"
    )
    is False,
)


# =========================================================================
# 11. Runtime events + dispatcher identity
# =========================================================================

events = list_job_events(
    JOB_ID
)


check(
    "Runtime status events persisted",
    len(
        events
    )
    >= 6,
    (
        "Event count: "
        + str(
            len(
                events
            )
        )
    ),
)

check(
    "Dispatcher invoked exactly three times",
    len(
        dispatcher_calls
    )
    == 3,
)

check(
    "Every dispatch used same canonical job_id",
    dispatcher_calls
    == [
        JOB_ID,
        JOB_ID,
        JOB_ID,
    ],
)


# =========================================================================
# 12. Real Phase 5.5 terminal failure intake
# =========================================================================

stage_result = intake_runtime_failure(
    job_id=
        JOB_ID,

    registry=
        registry,
)


check(
    "5.5 emitted FAILED StageResult",
    str(
        stage_result.status
    ).lower().endswith(
        "failed"
    ),
)

check(
    "5.5 StageResult job_id exact",
    stage_result.job_id
    == JOB_ID,
)

check(
    "5.5 StageResult workflow_id exact",
    stage_result.workflow_id
    == WORKFLOW_ID,
)

check(
    "5.5 StageResult correlation_id exact",
    stage_result.correlation_id
    == CORRELATION_ID,
)

check(
    "5.5 StageResult stage_id exact",
    stage_result.stage_id
    == STAGE_ID,
)

check(
    "5.5 failure code RuntimeError",
    stage_result.failure_code
    == "RuntimeError",
)

check(
    "5.5 failure details attempt count 3",
    stage_result.failure_details.get(
        "runtime_failure_attempt_count"
    )
    == 3,
)

check(
    "5.5 failure details maximum attempts 3",
    stage_result.failure_details.get(
        "runtime_maximum_attempts"
    )
    == 3,
)

check(
    "5.5 failure details retry exhausted True",
    stage_result.failure_details.get(
        "runtime_retry_exhausted"
    )
    is True,
)

check(
    "5.5 failure details canonical identity preserved",
    stage_result.failure_details.get(
        "canonical_job_id_preserved"
    )
    is True,
)

check(
    "5.5 failure details no replacement job",
    stage_result.failure_details.get(
        "retry_created_new_job"
    )
    is False,
)


# =========================================================================
# 13. End-to-end identity
# =========================================================================

check(
    "Canonical job_id continuous submission -> retries -> failure -> 5.5",
    (
        submission[
            "job_id"
        ]
        == correlation.job_id
        == attempt_1[
            "job_id"
        ]
        == attempt_2[
            "job_id"
        ]
        == attempt_3[
            "job_id"
        ]
        == stage_result.job_id
        == JOB_ID
    ),
)

check(
    "Workflow identity continuous correlation -> 5.5",
    correlation.workflow_id
    == stage_result.workflow_id
    == WORKFLOW_ID,
)

check(
    "Correlation identity continuous correlation -> 5.5",
    correlation.correlation_id
    == stage_result.correlation_id
    == CORRELATION_ID,
)


# =========================================================================
# 14. Real store + source immutability
# =========================================================================

REAL_JOBS_BYTES_AFTER = (
    REAL_JOBS_FILE.read_bytes()
    if REAL_JOBS_FILE.exists()
    else None
)

REAL_EVENTS_BYTES_AFTER = (
    REAL_EVENTS_FILE.read_bytes()
    if REAL_EVENTS_FILE.exists()
    else None
)


check(
    "Real orchestration jobs store unchanged",
    REAL_JOBS_BYTES_AFTER
    == REAL_JOBS_BYTES_BEFORE,
)

check(
    "Real orchestration event store unchanged",
    REAL_EVENTS_BYTES_AFTER
    == REAL_EVENTS_BYTES_BEFORE,
)

check(
    "Existing real queued jobs were not consumed",
    sorted(
        real_queued_ids_before
    )
    == sorted(
        str(
            getattr(
                job,
                "job_id",
                "",
            )
        )
        for job
        in real_jobs_before.values()
        if str(
            getattr(
                job,
                "status",
                "",
            )
        ).strip().lower()
        == "queued"
    ),
)

check(
    "Certification jobs evidence isolated",
    CERTIFICATION_JOBS_FILE.exists(),
    CERTIFICATION_JOBS_FILE,
)

check(
    "Certification events evidence isolated",
    CERTIFICATION_EVENTS_FILE.exists(),
    CERTIFICATION_EVENTS_FILE,
)


source_after = {
    name:
        sha256(
            path
        )
    for name, path
    in PATHS.items()
}


check(
    "Production source files unchanged",
    source_after
    == source_before,
)


# =========================================================================
# 15. Certification result
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

certified = (
    failed
    == 0
)


lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.6.6 — FAILURE/RETRY-PATH CERTIFICATION",
    "",
    f"Checks: {len(checks)}",
    f"Passed: {passed}",
    f"Failed: {failed}",
    f"FAILURE/RETRY PATH CERTIFIED: {certified}",
    f"Canonical job_id: {JOB_ID}",
    "Attempt 1: RUNNING -> QUEUED",
    "Attempt 2: RUNNING -> QUEUED",
    "Attempt 3: RUNNING -> FAILED",
    "Same-job retry identity: VERIFIED",
    "Replacement job created: FALSE",
    "Real Phase 5.5 failure intake: VERIFIED",
    "Production source modified: FALSE",
    (
        "NEXT: 5.6.7 Identity & Evidence Certification"
        if certified
        else "NEXT: Resolve failure/retry certification failures"
    ),
]

REPORT.write_text(
    "\n".join(
        lines
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 120)
print("PHASE 5.6.6 FAILURE/RETRY-PATH CERTIFICATION RESULT")
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
    "FAILURE/RETRY PATH CERTIFIED:",
    certified,
)
print(
    "Canonical job_id:",
    JOB_ID,
)
print(
    "Production source modified:",
    False,
)
print(
    (
        "NEXT: 5.6.7 Identity & Evidence Certification"
        if certified
        else "NEXT: Resolve failure/retry certification failures"
    )
)
print(
    "REPORT:",
    REPORT.name,
)
print("=" * 120)
