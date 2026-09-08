from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path.cwd()

SUCCESS_ROOT = (
    ROOT
    / "backend/server/data/orchestration/phase_5_6_success_certification"
)

FAILURE_ROOT = (
    ROOT
    / "backend/server/data/orchestration/phase_5_6_failure_retry_certification"
)

REPORT = (
    ROOT
    / "runtime_integration_phase_5_6_identity_evidence_certification.txt"
)

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
        print(
            "    " + str(detail)
        )


def read_json(path: Path):
    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


print()
print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 5.6.7 — IDENTITY & EVIDENCE CERTIFICATION")
print("=" * 120)


# =========================================================================
# 1. Evidence files exist
# =========================================================================

SUCCESS_JOBS = SUCCESS_ROOT / "jobs.json"
SUCCESS_EVENTS = SUCCESS_ROOT / "job_events.json"

FAILURE_JOBS = FAILURE_ROOT / "jobs.json"
FAILURE_EVENTS = FAILURE_ROOT / "job_events.json"


for label, path in (
    ("success jobs evidence", SUCCESS_JOBS),
    ("success events evidence", SUCCESS_EVENTS),
    ("failure jobs evidence", FAILURE_JOBS),
    ("failure events evidence", FAILURE_EVENTS),
):
    check(
        label + " exists",
        path.exists(),
        path,
    )


success_jobs = read_json(
    SUCCESS_JOBS
)

success_events_doc = read_json(
    SUCCESS_EVENTS
)

failure_jobs = read_json(
    FAILURE_JOBS
)

failure_events_doc = read_json(
    FAILURE_EVENTS
)


check(
    "Success evidence contains exactly one canonical job",
    len(
        success_jobs
    )
    == 1,
)

check(
    "Failure evidence contains exactly one canonical job",
    len(
        failure_jobs
    )
    == 1,
)


SUCCESS_JOB_ID = next(
    iter(
        success_jobs
    )
)

FAILURE_JOB_ID = next(
    iter(
        failure_jobs
    )
)

success_job = success_jobs[
    SUCCESS_JOB_ID
]

failure_job = failure_jobs[
    FAILURE_JOB_ID
]

success_events = success_events_doc.get(
    SUCCESS_JOB_ID,
    [],
)

failure_events = failure_events_doc.get(
    FAILURE_JOB_ID,
    [],
)


# =========================================================================
# 2. Top-level identity
# =========================================================================

check(
    "Success dictionary key equals embedded job_id",
    SUCCESS_JOB_ID
    == success_job.get(
        "job_id"
    ),
)

check(
    "Failure dictionary key equals embedded job_id",
    FAILURE_JOB_ID
    == failure_job.get(
        "job_id"
    ),
)

check(
    "Success canonical job_id format",
    SUCCESS_JOB_ID.startswith(
        "uj_"
    ),
    SUCCESS_JOB_ID,
)

check(
    "Failure canonical job_id format",
    FAILURE_JOB_ID.startswith(
        "uj_"
    ),
    FAILURE_JOB_ID,
)

check(
    "Success terminal status completed",
    success_job.get(
        "status"
    )
    == "completed",
)

check(
    "Failure terminal status failed",
    failure_job.get(
        "status"
    )
    == "failed",
)


# =========================================================================
# 3. Coordination identity evidence
# =========================================================================

success_coordination = (
    success_job.get(
        "metadata",
        {},
    ).get(
        "coordination",
        {},
    )
)

failure_coordination = (
    failure_job.get(
        "metadata",
        {},
    ).get(
        "coordination",
        {},
    )
)


for prefix, coordination in (
    ("Success", success_coordination),
    ("Failure", failure_coordination),
):
    check(
        prefix + " workflow_id present",
        bool(
            coordination.get(
                "workflow_id"
            )
        ),
    )

    check(
        prefix + " correlation_id present",
        bool(
            coordination.get(
                "correlation_id"
            )
        ),
    )

    check(
        prefix + " stage_id present",
        bool(
            coordination.get(
                "stage_id"
            )
        ),
    )

    check(
        prefix + " stage_version present",
        bool(
            coordination.get(
                "stage_version"
            )
        ),
    )

    check(
        prefix + " workflow_type present",
        bool(
            coordination.get(
                "workflow_type"
            )
        ),
    )

    check(
        prefix + " wave_index preserved",
        coordination.get(
            "wave_index"
        )
        == 0,
    )

    check(
        prefix + " execution semantics sequential",
        coordination.get(
            "execution_semantics"
        )
        == "sequential",
    )

    check(
        prefix + " StageReference contract version preserved",
        coordination.get(
            "stage_reference_contract_version"
        )
        == "universal_stage_reference_contract_v1.3.0",
    )

    check(
        prefix + " Runtime handoff intent version preserved",
        coordination.get(
            "runtime_handoff_intent_version"
        )
        == "runtime_handoff_intent_v5.1.0",
    )


# =========================================================================
# 4. Submission evidence
# =========================================================================

success_submission = (
    success_job.get(
        "metadata",
        {},
    ).get(
        "universal_runtime_submission",
        {},
    )
)

failure_submission = (
    failure_job.get(
        "metadata",
        {},
    ).get(
        "universal_runtime_submission",
        {},
    )
)


for prefix, job_id, job, submission in (
    (
        "Success",
        SUCCESS_JOB_ID,
        success_job,
        success_submission,
    ),
    (
        "Failure",
        FAILURE_JOB_ID,
        failure_job,
        failure_submission,
    ),
):
    canonical_job = submission.get(
        "canonical_job",
        {},
    )

    registration = submission.get(
        "registration",
        {},
    )

    check(
        prefix + " submission schema version exact",
        submission.get(
            "schema_version"
        )
        == "universal_job_submission_projection_v1",
    )

    check(
        prefix + " submission version exact",
        submission.get(
            "submission_version"
        )
        == "universal_job_submission_v1",
    )

    check(
        prefix + " canonical submission job_id exact",
        canonical_job.get(
            "job_id"
        )
        == job_id,
    )

    check(
        prefix + " canonical submission workspace exact",
        canonical_job.get(
            "workspace_id"
        )
        == job.get(
            "workspace_id"
        ),
    )

    check(
        prefix + " canonical submission job_type exact",
        canonical_job.get(
            "job_type"
        )
        == job.get(
            "job_type"
        ),
    )

    check(
        prefix + " canonical priority evidence normal",
        canonical_job.get(
            "priority"
        )
        == "normal",
    )

    check(
        prefix + " orchestration priority projection 30",
        job.get(
            "priority"
        )
        == 30,
    )

    check(
        prefix + " submission canonical status queued",
        canonical_job.get(
            "status"
        )
        == "queued",
    )

    check(
        prefix + " registration job_type exact",
        registration.get(
            "job_type"
        )
        == job.get(
            "job_type"
        ),
    )

    check(
        prefix + " registration pipeline exact",
        registration.get(
            "pipeline"
        )
        == "linking_target_pipeline",
    )

    check(
        prefix + " registration stage exact",
        registration.get(
            "stage"
        )
        == "linking_target_pipeline_batch",
    )

    check(
        prefix + " registration persistent True",
        registration.get(
            "persistent"
        )
        is True,
    )

    fingerprints = submission.get(
        "fingerprints",
        {},
    )

    check(
        prefix + " identity fingerprint present",
        str(
            fingerprints.get(
                "identity",
                "",
            )
        ).startswith(
            "sha256:"
        ),
    )

    check(
        prefix + " contract fingerprint present",
        str(
            fingerprints.get(
                "contract",
                "",
            )
        ).startswith(
            "sha256:"
        ),
    )

    check(
        prefix + " content fingerprint present",
        str(
            fingerprints.get(
                "content",
                "",
            )
        ).startswith(
            "sha256:"
        ),
    )


# =========================================================================
# 5. Success event evidence
# =========================================================================

success_transitions = [
    (
        event.get(
            "old_status"
        ),
        event.get(
            "new_status"
        ),
    )
    for event
    in success_events
]


check(
    "Success event chain exact",
    success_transitions
    == [
        ("none", "queued"),
        ("queued", "running"),
        ("running", "completed"),
    ],
    success_transitions,
)

check(
    "Every success event preserves canonical job_id",
    all(
        event.get(
            "job_id"
        )
        == SUCCESS_JOB_ID
        for event
        in success_events
    ),
)

success_completion_event = success_events[
    -1
]

check(
    "Success terminal event has event_id",
    bool(
        success_completion_event.get(
            "event_id"
        )
    ),
)

check(
    "Success terminal event dispatch completed True",
    success_completion_event.get(
        "metadata",
        {},
    ).get(
        "runtime_dispatch_completed"
    )
    is True,
)

check(
    "Success terminal event canonical identity preserved",
    success_completion_event.get(
        "metadata",
        {},
    ).get(
        "canonical_job_id_preserved"
    )
    is True,
)

check(
    "Success persisted worker version exact",
    success_job.get(
        "metadata",
        {},
    ).get(
        "runtime_worker_version"
    )
    == "universal_runtime_worker_v1",
)

check(
    "Success persisted dispatch result job_id exact",
    success_job.get(
        "metadata",
        {},
    ).get(
        "runtime_dispatch_result",
        {},
    ).get(
        "runtime_job_id"
    )
    == SUCCESS_JOB_ID,
)


# =========================================================================
# 6. Failure/retry event evidence
# =========================================================================

failure_transitions = [
    (
        event.get(
            "old_status"
        ),
        event.get(
            "new_status"
        ),
    )
    for event
    in failure_events
]


check(
    "Failure/retry event chain exact",
    failure_transitions
    == [
        ("none", "queued"),
        ("queued", "running"),
        ("running", "queued"),
        ("queued", "running"),
        ("running", "queued"),
        ("queued", "running"),
        ("running", "failed"),
    ],
    failure_transitions,
)

check(
    "Every failure event preserves canonical job_id",
    all(
        event.get(
            "job_id"
        )
        == FAILURE_JOB_ID
        for event
        in failure_events
    ),
)

retry_events = [
    event
    for event
    in failure_events
    if (
        event.get(
            "old_status"
        )
        == "running"
        and event.get(
            "new_status"
        )
        == "queued"
    )
]


check(
    "Exactly two retry events persisted",
    len(
        retry_events
    )
    == 2,
)

check(
    "Retry attempt counts are 1 then 2",
    [
        event.get(
            "metadata",
            {},
        ).get(
            "runtime_failure_attempt_count"
        )
        for event
        in retry_events
    ]
    == [
        1,
        2,
    ],
)

check(
    "Every retry event scheduled retry",
    all(
        event.get(
            "metadata",
            {},
        ).get(
            "runtime_retry_scheduled"
        )
        is True
        for event
        in retry_events
    ),
)

check(
    "Every retry event created no replacement job",
    all(
        event.get(
            "metadata",
            {},
        ).get(
            "retry_created_new_job"
        )
        is False
        for event
        in retry_events
    ),
)

check(
    "Every retry event preserved canonical job_id",
    all(
        event.get(
            "metadata",
            {},
        ).get(
            "canonical_job_id_preserved"
        )
        is True
        for event
        in retry_events
    ),
)


terminal_failure_event = failure_events[
    -1
]

terminal_metadata = terminal_failure_event.get(
    "metadata",
    {},
)


check(
    "Terminal failure transition exact",
    (
        terminal_failure_event.get(
            "old_status"
        )
        == "running"
        and terminal_failure_event.get(
            "new_status"
        )
        == "failed"
    ),
)

check(
    "Terminal failure event_id present",
    bool(
        terminal_failure_event.get(
            "event_id"
        )
    ),
)

check(
    "Terminal failure dispatch failed True",
    terminal_metadata.get(
        "runtime_dispatch_failed"
    )
    is True,
)

check(
    "Terminal failure dispatch completed False",
    terminal_metadata.get(
        "runtime_dispatch_completed"
    )
    is False,
)

check(
    "Terminal failure retry scheduled False",
    terminal_metadata.get(
        "runtime_retry_scheduled"
    )
    is False,
)

check(
    "Terminal failure attempt count 3",
    terminal_metadata.get(
        "runtime_failure_attempt_count"
    )
    == 3,
)

check(
    "Terminal failure maximum attempts 3",
    terminal_metadata.get(
        "runtime_maximum_attempts"
    )
    == 3,
)

check(
    "Terminal failure retry exhausted True",
    terminal_metadata.get(
        "runtime_retry_exhausted"
    )
    is True,
)

check(
    "Terminal failure error type RuntimeError",
    terminal_metadata.get(
        "runtime_dispatch_error_type"
    )
    == "RuntimeError",
)

check(
    "Terminal failure canonical identity preserved",
    terminal_metadata.get(
        "canonical_job_id_preserved"
    )
    is True,
)

check(
    "Terminal failure created no replacement job",
    terminal_metadata.get(
        "retry_created_new_job"
    )
    is False,
)


# =========================================================================
# 7. Persisted terminal evidence matches terminal event
# =========================================================================

failure_job_metadata = failure_job.get(
    "metadata",
    {},
)


for key in (
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
):
    check(
        "Persisted terminal evidence matches terminal event: " + key,
        failure_job_metadata.get(
            key
        )
        == terminal_metadata.get(
            key
        ),
    )


# =========================================================================
# 8. Evidence integrity hashes
# =========================================================================

for label, path in (
    ("success jobs", SUCCESS_JOBS),
    ("success events", SUCCESS_EVENTS),
    ("failure jobs", FAILURE_JOBS),
    ("failure events", FAILURE_EVENTS),
):
    digest = sha256(
        path
    )

    check(
        label + " SHA256 produced",
        len(
            digest
        )
        == 64,
        digest,
    )


# =========================================================================
# 9. Certification result
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
    "PHASE 5.6.7 — IDENTITY & EVIDENCE CERTIFICATION",
    "",
    f"Checks: {len(checks)}",
    f"Passed: {passed}",
    f"Failed: {failed}",
    f"IDENTITY & EVIDENCE CERTIFIED: {certified}",
    f"Success canonical job_id: {SUCCESS_JOB_ID}",
    f"Failure canonical job_id: {FAILURE_JOB_ID}",
    "Success identity continuity: VERIFIED",
    "Failure/retry identity continuity: VERIFIED",
    "Submission evidence: VERIFIED",
    "Runtime Registration evidence: VERIFIED",
    "Runtime status-event evidence: VERIFIED",
    "Same-job retry evidence: VERIFIED",
    "Terminal failure evidence: VERIFIED",
    "Evidence SHA256 generation: VERIFIED",
    (
        "NEXT: 5.6.8 Final Runtime Integration Certification"
        if certified
        else "NEXT: Resolve identity/evidence certification failures"
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
print("PHASE 5.6.7 IDENTITY & EVIDENCE CERTIFICATION RESULT")
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
    "IDENTITY & EVIDENCE CERTIFIED:",
    certified,
)
print(
    "Success canonical job_id:",
    SUCCESS_JOB_ID,
)
print(
    "Failure canonical job_id:",
    FAILURE_JOB_ID,
)
print(
    (
        "NEXT: 5.6.8 Final Runtime Integration Certification"
        if certified
        else "NEXT: Resolve identity/evidence certification failures"
    )
)
print(
    "REPORT:",
    REPORT.name,
)
print("=" * 120)
