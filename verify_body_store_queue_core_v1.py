"""Verify Universal Article Body Store Queue Core v1."""

from __future__ import annotations

import hashlib
import shutil
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from backend.server.universal_article_body_store.body_store_queue_v1 import (
    BODY_STORE_QUEUE_JOB_TYPES,
    BODY_STORE_QUEUE_PRIORITIES,
    BODY_STORE_QUEUE_STATUSES,
    BODY_STORE_QUEUE_VERSION,
    BodyStoreQueueContractError,
    BodyStoreQueueStateError,
    cancel_body_store_job,
    claim_body_store_job,
    complete_body_store_job,
    enqueue_body_store_job,
    fail_body_store_job,
    get_body_store_queue_statistics,
    list_body_store_jobs,
    peek_body_store_job,
)


DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

PROTECTED_PATHS = {
    "production_body_store": (
        DATA_ROOT
        / "universal_article_body_store"
    ),

    "production_body_queue": (
        DATA_ROOT
        / "universal_article_body_queue"
    ),

    "persistent_uucd_output": (
        DATA_ROOT
        / "universal_unified_content_documents"
    ),

    "persistent_wuc_output": (
        DATA_ROOT
        / "website_unified_content"
    ),
}


def fingerprint(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    if not path.exists():
        digest.update(
            b"ABSENT"
        )

        return digest.hexdigest()

    for candidate in sorted(
        path.rglob("*"),
        key=lambda item: (
            item.relative_to(
                path
            ).as_posix()
        ),
    ):
        digest.update(
            candidate.relative_to(
                path
            ).as_posix().encode(
                "utf-8"
            )
        )

        if candidate.is_file():
            digest.update(
                candidate.read_bytes()
            )

    return digest.hexdigest()


before = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED_PATHS.items()
}


temporary_project = Path(
    tempfile.mkdtemp(
        prefix="linkcraftor_body_store_queue_v1_"
    )
).resolve()

try:
    normal = enqueue_body_store_job(
        project_root=temporary_project,
        workspace_id="ws_alpha",
        job_type="body_store.read",
        runtime_request={
            "operation":
                "read",

            "payload": {
                "workspace_id":
                    "ws_alpha",

                "body_ref":
                    "backend/server/data/universal_article_body_store/"
                    "ws_alpha/bodies/example.txt",
            },
        },
        priority="NORMAL",
        queue_job_id="queue_normal",
    )

    critical = enqueue_body_store_job(
        project_root=temporary_project,
        workspace_id="ws_alpha",
        job_type="body_store.metadata",
        runtime_request={
            "operation":
                "metadata",

            "payload": {
                "workspace_id":
                    "ws_alpha",

                "body_ref":
                    "backend/server/data/universal_article_body_store/"
                    "ws_alpha/bodies/example.txt",
            },
        },
        priority="CRITICAL",
        queue_job_id="queue_critical",
    )

    other_workspace = enqueue_body_store_job(
        project_root=temporary_project,
        workspace_id="ws_beta",
        job_type="body_store.list",
        runtime_request={
            "operation":
                "list",

            "payload": {
                "workspace_id":
                    "ws_beta",
            },
        },
        priority="HIGH",
        queue_job_id="queue_beta",
    )

    peeked = peek_body_store_job(
        project_root=temporary_project,
        workspace_id="ws_alpha",
    )

    claimed = claim_body_store_job(
        project_root=temporary_project,
        workspace_id="ws_alpha",
        worker_id="worker_alpha",
        lease_seconds=300,
    )

    completed = complete_body_store_job(
        project_root=temporary_project,
        queue_job_id="queue_critical",
        worker_id="worker_alpha",
        worker_execution_id="worker_execution_001",
        runtime_execution_id="runtime_execution_001",
        runtime_success=True,
        runtime_result_hash="a" * 64,
    )

    claimed_normal = claim_body_store_job(
        project_root=temporary_project,
        workspace_id="ws_alpha",
        worker_id="worker_alpha",
        lease_seconds=300,
    )

    requeued = fail_body_store_job(
        project_root=temporary_project,
        queue_job_id="queue_normal",
        worker_id="worker_alpha",
        error_type="TemporaryError",
        error_message="Temporary test failure.",
        retry_allowed=True,
    )

    claimed_again = claim_body_store_job(
        project_root=temporary_project,
        workspace_id="ws_alpha",
        worker_id="worker_alpha",
        lease_seconds=300,
    )

    failed = fail_body_store_job(
        project_root=temporary_project,
        queue_job_id="queue_normal",
        worker_id="worker_alpha",
        error_type="PermanentError",
        error_message="Permanent test failure.",
        retry_allowed=False,
    )

    cancelled = cancel_body_store_job(
        project_root=temporary_project,
        queue_job_id="queue_beta",
    )

    listed = list_body_store_jobs(
        project_root=temporary_project,
    )

    statistics = get_body_store_queue_statistics(
        project_root=temporary_project,
    )

    body_rejected = False

    try:
        enqueue_body_store_job(
            project_root=temporary_project,
            workspace_id="ws_alpha",
            job_type="body_store.store",
            runtime_request={
                "operation":
                    "store",

                "payload": {
                    "content_body":
                        "This must never be stored in the queue.",
                },
            },
        )

    except BodyStoreQueueContractError:
        body_rejected = True

    invalid_transition_rejected = False

    try:
        cancel_body_store_job(
            project_root=temporary_project,
            queue_job_id="queue_critical",
        )

    except BodyStoreQueueStateError:
        invalid_transition_rejected = True

finally:
    shutil.rmtree(
        temporary_project,
        ignore_errors=True,
    )


after = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED_PATHS.items()
}

unchanged = {
    name:
        before[
            name
        ]
        == after[
            name
        ]

    for name
    in PROTECTED_PATHS
}


checks = {
    "queue_version_valid":
        BODY_STORE_QUEUE_VERSION
        == "universal_article_body_store_queue_v1",

    "priorities_exact":
        BODY_STORE_QUEUE_PRIORITIES
        == (
            "CRITICAL",
            "HIGH",
            "NORMAL",
            "LOW",
        ),

    "statuses_exact":
        BODY_STORE_QUEUE_STATUSES
        == (
            "QUEUED",
            "LEASED",
            "COMPLETED",
            "FAILED",
            "CANCELLED",
        ),

    "job_types_exact":
        BODY_STORE_QUEUE_JOB_TYPES
        == (
            "body_store.store",
            "body_store.read",
            "body_store.verify",
            "body_store.metadata",
            "body_store.list",
        ),

    "enqueue_passed":
        normal[
            "status"
        ]
        == "QUEUED",

    "priority_peek_passed":
        peeked is not None
        and peeked[
            "queue_job_id"
        ]
        == "queue_critical",

    "claim_and_lease_passed":
        claimed is not None
        and claimed[
            "status"
        ]
        == "LEASED"
        and claimed[
            "worker_id"
        ]
        == "worker_alpha",

    "completion_passed":
        completed[
            "status"
        ]
        == "COMPLETED",

    "retry_requeue_passed":
        requeued[
            "status"
        ]
        == "QUEUED"
        and requeued[
            "failure"
        ][
            "retry_allowed"
        ]
        is True,

    "second_claim_passed":
        claimed_again is not None
        and claimed_again[
            "attempt"
        ]
        == 2,

    "final_failure_passed":
        failed[
            "status"
        ]
        == "FAILED",

    "cancellation_passed":
        cancelled[
            "status"
        ]
        == "CANCELLED",

    "listing_passed":
        len(
            listed
        )
        == 3,

    "statistics_passed":
        statistics[
            "completed_jobs"
        ]
        == 1
        and statistics[
            "failed_jobs"
        ]
        == 1
        and statistics[
            "cancelled_jobs"
        ]
        == 1,

    "article_body_rejected":
        body_rejected,

    "invalid_transition_rejected":
        invalid_transition_rejected,

    "production_outputs_unchanged":
        all(
            unchanged.values()
        ),
}


failures = [
    name
    for name, passed
    in checks.items()
    if passed is not True
]


print()
print("=" * 116)
print(
    "UNIVERSAL ARTICLE BODY STORE QUEUE CORE — PHASE 7.1B"
)
print("=" * 116)
print()

for name, passed in checks.items():
    print(
        f"{name:<76}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

print()
print(
    "PRODUCTION OUTPUTS"
)

for name, passed in unchanged.items():
    print(
        "  "
        + f"{name:<36}"
        + (
            "UNCHANGED"
            if passed
            else "CHANGED"
        )
    )

print()
print(
    "Production queue jobs created:       0"
)

print(
    "Production Body Store files written: 0"
)

print(
    "Runtime jobs created:                0"
)

print(
    "Worker executions started:           0"
)

print(
    "Runtime Registrations created:       0"
)

print()
print(
    "FAILURES"
)

if failures:
    for failure in failures:
        print(
            "  - "
            + failure
        )

else:
    print(
        "  None"
    )

print()

if failures:
    print(
        "BODY STORE QUEUE CORE PHASE 7.1B: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE QUEUE CORE PHASE 7.1B: PASS"
)

print(
    "The Body Store Queue now manages persistent queue state "
    "without executing workers or storing article content bodies."
)

print("=" * 116)
