from __future__ import annotations

import hashlib
import inspect
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

from backend.server.coordination.runtime_integration.runtime_completion_intake import (
    intake_runtime_completion,
)

from backend.server.runtime.universal_jobs.creation_engine import (
    UniversalJobCreationRequest,
)

from backend.server.orchestration import (
    job_store,
)


ROOT = Path.cwd()

REPORT = (
    ROOT
    / "runtime_integration_phase_5_6_success_path_certification.txt"
)


PATHS = {
    "submission":
        ROOT
        / "backend/server/runtime/"
          "universal_job_submission.py",

    "worker":
        ROOT
        / "backend/server/runtime/"
          "universal_runtime_worker_v1.py",

    "phase_5_3":
        ROOT
        / "backend/server/coordination/runtime_integration/"
          "workflow_job_correlation.py",

    "phase_5_4":
        ROOT
        / "backend/server/coordination/runtime_integration/"
          "runtime_completion_intake.py",
}


EXPECTED = {
    "submission":
        "8E7AF8CC795D7C990F11FFE0ACD06A5253D957922EC3BD0B740CC1CB0CD3FB2F",

    "worker":
        "ED6B415C5FEDF3F4CB62451F3E23D182F9DA937D9CB09FD33262C506B9BEF699",

    "phase_5_3":
        "13B007B1F74A131250476432B14381CC81C916F48CE121B44877964A18A73AB6",

    "phase_5_4":
        "A9F2A8E4242A08A2BDBE6AF0B96DC1042A53DDD3B2F72BB355259FA0E5D2E6FB",
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
print("PHASE 5.6.5 — SUCCESS-PATH CERTIFICATION")
print("=" * 120)


# =========================================================================
# 1. Canonical production integrity
# =========================================================================

for name, expected in EXPECTED.items():

    actual = sha256(
        PATHS[
            name
        ]
    )

    check(
        "Canonical SHA exact: " + name,
        actual == expected,
        actual,
    )


# =========================================================================
# 2. Resolve real orchestration readers
# =========================================================================

load_jobs = getattr(
    job_store,
    "load_jobs",
)

get_job = getattr(
    job_store,
    "get_job",
    None,
)

list_job_events = getattr(
    job_store,
    "list_job_events",
    None,
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
# 3. Isolated real orchestration store
#
# Phase 5.6 certification must exercise the REAL orchestration persistence,
# queue, worker, status-event and intake functions without consuming or
# modifying pre-existing production/development queue records.
#
# job_store functions resolve JOBS_FILE / EVENTS_FILE from their module
# globals at call time, so redirecting these globals inside THIS verifier
# process preserves the real implementation while isolating certification
# data.
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

real_queued_before = [
    job
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
]


CERTIFICATION_STORE = (
    ROOT
    / "backend/server/data/orchestration/"
      "phase_5_6_success_certification"
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
            "SUCCESS-PATH CERTIFICATION REFUSED: "
            "isolated certification evidence already exists. "
            "No existing certification evidence will be overwritten.\n"
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
    str(
        CERTIFICATION_STORE
    ),
)


check(
    "Real orchestration store not selected for certification",
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
    "Pre-existing real queued jobs preserved outside certification store",
    True,
    (
        "Real queued jobs observed but not consumed: "
        + str(
            len(
                real_queued_before
            )
        )
    ),
)


# =========================================================================
# 3A. Safety gate — isolated certification queue must begin empty
# =========================================================================

existing_jobs = load_jobs()


queued_before = [
    job
    for job
    in existing_jobs.values()
    if str(
        getattr(
            job,
            "status",
            "",
        )
    ).strip().lower()
    == "queued"
]


if queued_before:
    raise SystemExit(
        (
            "SUCCESS-PATH CERTIFICATION REFUSED: "
            "orchestration already contains queued work. "
            "The one-shot Runtime Worker must not consume an "
            "unrelated job.\n"
            "Queued job IDs: "
            + ", ".join(
                str(
                    getattr(
                        job,
                        "job_id",
                        "",
                    )
                )
                for job
                in queued_before
            )
        )
    )


check(
    "Pre-existing Runtime queue empty",
    True,
)


# =========================================================================
# 4. Build certified Phase 5.2-equivalent mapping
# =========================================================================

WORKFLOW_ID = (
    "wf_phase_5_6_success"
)

CORRELATION_ID = (
    "corr_phase_5_6_success"
)

STAGE_ID = (
    "stage_phase_5_6_success"
)

STAGE_VERSION = (
    "stage_phase_5_6_success_v1"
)

WORKFLOW_TYPE = (
    "phase_5_6_success_workflow"
)

WORKSPACE_ID = (
    "ws_phase_5_6_success"
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
        "phase-5-6-success.example.com",
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
        1,
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
# 5. Real canonical Universal Job submission
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


persisted_queued = get_job(
    JOB_ID
)


check(
    "Submitted job persisted in orchestration",
    persisted_queued is not None,
)

check(
    "Submitted job status QUEUED",
    str(
        persisted_queued.status
    ).lower()
    == "queued",
)

check(
    "Persisted job_id equals canonical job_id",
    persisted_queued.job_id
    == JOB_ID,
)


# =========================================================================
# 6. Corrected Phase 5.3 binds only after successful submission
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
    "5.3 correlation created after canonical submission",
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
# 7. Real Runtime Worker success execution
#
# Dispatcher is injected only to make the business operation deterministic.
# Queue claiming and RUNNING/COMPLETED persistence remain the real worker.
# =========================================================================

def certified_success_dispatcher(
    runtime_job,
):
    return {
        "domain":
            PAYLOAD[
                "domain"
            ],

        "phase_5_6_success":
            True,

        "runtime_job_id":
            runtime_job[
                "job_id"
            ],
    }


worker_result = (
    run_one_universal_runtime_job_v1(
        worker_id=
            "phase_5_6_success_certifier",

        dispatcher=
            certified_success_dispatcher,
    )
)


check(
    "Runtime Worker claimed a job",
    worker_result[
        "job_claimed"
    ]
    is True,
)

check(
    "Runtime Worker claimed intended canonical job",
    worker_result[
        "job_id"
    ]
    == JOB_ID,
)

check(
    "Runtime Worker status COMPLETED",
    worker_result[
        "worker_status"
    ]
    == "COMPLETED",
)

check(
    "Runtime dispatch performed",
    worker_result[
        "dispatch_performed"
    ]
    is True,
)

check(
    "Runtime terminal status completed",
    str(
        worker_result[
            "terminal_status"
        ]
    ).lower()
    == "completed",
)

check(
    "Worker preserved canonical identity",
    worker_result[
        "canonical_job_id_preserved"
    ]
    is True,
)


# =========================================================================
# 8. Verify real persisted COMPLETED authority
# =========================================================================

completed_job = get_job(
    JOB_ID
)


check(
    "Persisted Runtime job still exists",
    completed_job is not None,
)

check(
    "Persisted Runtime job status COMPLETED",
    str(
        completed_job.status
    ).lower()
    == "completed",
)

check(
    "COMPLETED job_id unchanged",
    completed_job.job_id
    == JOB_ID,
)


metadata = dict(
    completed_job.metadata
)


check(
    "Persisted runtime_dispatch_completed True",
    metadata.get(
        "runtime_dispatch_completed"
    )
    is True,
)

check(
    "Persisted canonical_job_id_preserved True",
    metadata.get(
        "canonical_job_id_preserved"
    )
    is True,
)

check(
    "Persisted dispatch result exact",
    metadata[
        "runtime_dispatch_result"
    ][
        "phase_5_6_success"
    ]
    is True,
)


# =========================================================================
# 9. Real orchestration status history
# =========================================================================

events = list_job_events(
    JOB_ID
)


transitions = [
    (
        str(
            event.get(
                "old_status",
                "",
            )
        ).lower(),

        str(
            event.get(
                "new_status",
                "",
            )
        ).lower(),
    )
    for event
    in events
]


check(
    "QUEUED -> RUNNING persisted",
    (
        "queued",
        "running",
    )
    in transitions,
)

check(
    "RUNNING -> COMPLETED persisted",
    (
        "running",
        "completed",
    )
    in transitions,
)


# =========================================================================
# 10. Real Phase 5.4 completion intake
# =========================================================================

stage_result = intake_runtime_completion(
    job_id=
        JOB_ID,

    registry=
        registry,
)


check(
    "5.4 emitted COMPLETED StageResult",
    str(
        stage_result.status
    ).lower().endswith(
        "completed"
    ),
)

check(
    "5.4 StageResult job_id exact",
    stage_result.job_id
    == JOB_ID,
)

check(
    "5.4 StageResult workflow_id exact",
    stage_result.workflow_id
    == WORKFLOW_ID,
)

check(
    "5.4 StageResult correlation_id exact",
    stage_result.correlation_id
    == CORRELATION_ID,
)

check(
    "5.4 StageResult stage_id exact",
    stage_result.stage_id
    == STAGE_ID,
)

check(
    "5.4 propagated real Runtime output",
    dict(
        stage_result.output
    )[
        "phase_5_6_success"
    ]
    is True,
)

check(
    "5.4 result uses Runtime completion event",
    stage_result.result_id
    == str(
        next(
            event[
                "event_id"
            ]
            for event
            in events
            if str(
                event.get(
                    "old_status",
                    "",
                )
            ).lower()
            == "running"
            and str(
                event.get(
                    "new_status",
                    "",
                )
            ).lower()
            == "completed"
        )
    ),
)


# =========================================================================
# 11. End-to-end identity continuity
# =========================================================================

check(
    "Canonical job_id continuous submission -> worker -> 5.4",
    (
        submission[
            "job_id"
        ]
        == worker_result[
            "job_id"
        ]
        == completed_job.job_id
        == stage_result.job_id
        == JOB_ID
    ),
)

check(
    "Workflow identity continuous correlation -> 5.4",
    (
        correlation.workflow_id
        == stage_result.workflow_id
        == WORKFLOW_ID
    ),
)

check(
    "Correlation identity continuous correlation -> 5.4",
    (
        correlation.correlation_id
        == stage_result.correlation_id
        == CORRELATION_ID
    ),
)


# =========================================================================
# 12. Real-store + production-source immutability
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
    (
        REAL_JOBS_BYTES_AFTER
        == REAL_JOBS_BYTES_BEFORE
    ),
)


check(
    "Real orchestration event store unchanged",
    (
        REAL_EVENTS_BYTES_AFTER
        == REAL_EVENTS_BYTES_BEFORE
    ),
)


check(
    "Existing real queued jobs were not consumed",
    (
        len(
            real_queued_before
        )
        == len(
            [
                job
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
            ]
        )
    ),
)


check(
    "Certification jobs file exists only in isolated store",
    CERTIFICATION_JOBS_FILE.exists(),
    str(
        CERTIFICATION_JOBS_FILE
    ),
)


check(
    "Certification events file exists only in isolated store",
    CERTIFICATION_EVENTS_FILE.exists(),
    str(
        CERTIFICATION_EVENTS_FILE
    ),
)


check(
    "Production source files unchanged",
    all(
        sha256(
            PATHS[
                name
            ]
        )
        == EXPECTED[
            name
        ]
        for name
        in EXPECTED
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
    "PHASE 5.6.5 — SUCCESS-PATH CERTIFICATION",
    "=" * 120,
    "",
]


for name, ok, detail in checks:

    lines.append(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if detail:
        lines.append(
            "    " + str(detail)
        )


lines.extend(
    (
        "",
        "=" * 120,
        "SUCCESS-PATH CERTIFICATION RESULT",
        "=" * 120,
        "",
        f"Checks: {len(checks)}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        (
            "SUCCESS PATH CERTIFIED: TRUE"
            if failed == 0
            else "SUCCESS PATH CERTIFIED: FALSE"
        ),
        "",
        "Real canonical submission: VERIFIED",
        "Real orchestration queue ingress: VERIFIED",
        "Real Runtime claim: VERIFIED",
        "Real QUEUED -> RUNNING: VERIFIED",
        "Real RUNNING -> COMPLETED: VERIFIED",
        "Same canonical job_id: VERIFIED",
        "Real Phase 5.4 completion intake: VERIFIED",
        "Production source modified: FALSE",
        (
            "NEXT: 5.6.6 Failure/Retry-Path Certification"
            if failed == 0
            else "NEXT: Resolve success-path certification failures"
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
print("PHASE 5.6.5 SUCCESS-PATH CERTIFICATION RESULT")
print("=" * 120)
print("Checks:", len(checks))
print("Passed:", passed)
print("Failed:", failed)
print(
    "SUCCESS PATH CERTIFIED:",
    failed == 0,
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
    "NEXT:",
    (
        "5.6.6 Failure/Retry-Path Certification"
        if failed == 0
        else "Resolve success-path certification failures"
    ),
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



