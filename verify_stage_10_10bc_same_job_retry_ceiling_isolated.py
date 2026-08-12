from __future__ import annotations

import hashlib
import shutil
from pathlib import Path


ROOT = Path.cwd().resolve()

TEST_ROOT = (
    ROOT
    / "tmp"
    / "stage_10_10bc_same_job_retry"
)

TEST_JOBS_FILE = (
    TEST_ROOT
    / "jobs.json"
)

TEST_EVENTS_FILE = (
    TEST_ROOT
    / "job_events.json"
)

TEST_LOCK_FILE = (
    TEST_ROOT
    / ".queue.lock"
)


def sha256_file(
    path: Path,
) -> str | None:

    if not path.exists():
        return None

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def check(
    name: str,
    condition: bool,
    detail: str = "",
) -> None:

    label = (
        "PASS"
        if condition
        else "FAIL"
    )

    print(
        f"[{label}] {name}"
        + (
            f" — {detail}"
            if detail
            else ""
        )
    )

    if not condition:
        raise AssertionError(
            name
        )


if TEST_ROOT.exists():
    shutil.rmtree(
        TEST_ROOT
    )

TEST_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# IMPORT CANONICAL COMPONENTS
# ============================================================

import backend.server.orchestration.job_store as job_store
import backend.server.orchestration.queue as queue_module

from backend.server.runtime.universal_runtime_worker_v1 import (
    run_one_universal_runtime_job_v1,
)

from backend.server.runtime.universal_runtime_registration import (
    get_runtime_registration,
)


# ============================================================
# CAPTURE PRODUCTION STATE
# ============================================================

PRODUCTION_DATA_DIR = (
    job_store.DATA_DIR
)

PRODUCTION_JOBS_FILE = (
    job_store.JOBS_FILE
)

PRODUCTION_EVENTS_FILE = (
    job_store.EVENTS_FILE
)

PRODUCTION_LOCK_PATH = getattr(
    queue_module,
    "_LOCK_PATH",
    None,
)

production_jobs_hash_before = (
    sha256_file(
        PRODUCTION_JOBS_FILE
    )
)

production_events_hash_before = (
    sha256_file(
        PRODUCTION_EVENTS_FILE
    )
)


# ============================================================
# REDIRECT CANONICAL ORCHESTRATION STORE TO TEMP
# ============================================================

job_store.DATA_DIR = (
    TEST_ROOT
)

job_store.JOBS_FILE = (
    TEST_JOBS_FILE
)

job_store.EVENTS_FILE = (
    TEST_EVENTS_FILE
)

if hasattr(
    queue_module,
    "_LOCK_PATH",
):
    queue_module._LOCK_PATH = (
        TEST_LOCK_FILE
    )


print()
print("=" * 86)
print("STAGE 10.10B/C — SAME-JOB RETRY + CEILING ISOLATED VERIFICATION")
print("=" * 86)


# ============================================================
# VERIFY REAL PERSISTED REGISTRATION POLICY
# ============================================================

registration = (
    get_runtime_registration(
        "uucd_runtime_handoff"
    )
)

check(
    "uucd_runtime_handoff registration exists",
    isinstance(
        registration,
        dict,
    ),
)

retry_policy = (
    registration.get(
        "retry_policy"
    )
    or {}
)

maximum_attempts = (
    retry_policy.get(
        "maximum_attempts",
        retry_policy.get(
            "max_attempts"
        ),
    )
)

check(
    "maximum attempts is 3",
    int(
        maximum_attempts
    )
    == 3,
)

check(
    "handler errors are retryable",
    retry_policy.get(
        "retry_on_handler_error"
    )
    is True,
)

check(
    "contract errors are non-retryable",
    retry_policy.get(
        "retry_on_contract_error"
    )
    is False,
)


# ============================================================
# CREATE EXACTLY ONE CANONICAL ORCHESTRATION JOB
# ============================================================

canonical_job_id = (
    "uj_stage10_10bc_"
    + ("a" * 20)
)

workspace_id = (
    "ws_stage10_10bc_test"
)

document_id = (
    "uucd_"
    + ("b" * 32)
)

payload = {
    "document_id":
        document_id,

    "content_ref":
        (
            "backend/server/data/"
            "universal_unified_content_documents/"
            f"{workspace_id}/documents/"
            f"{document_id}.json"
        ),

    "body_ref":
        (
            "backend/server/data/"
            "universal_article_body_store/"
            f"{workspace_id}/bodies/test.txt"
        ),

    "source_type":
        "website",

    "content_hash":
        "c" * 64,

    "persistence_fingerprint":
        "d" * 64,
}

metadata = {
    "idempotency_key":
        (
            "uucd_runtime_test_"
            + ("e" * 32)
        ),

    "canonical_universal_job": {
        "job_id":
            canonical_job_id,

        "workspace_id":
            workspace_id,

        "job_type":
            "uucd_runtime_handoff",

        "idempotency_key":
            (
                "uucd_runtime_test_"
                + ("e" * 32)
            ),
    },

    "body_content_in_job":
        False,
}

created = job_store.create_job(
    workspace_id=
        workspace_id,

    job_type=
        "uucd_runtime_handoff",

    payload=
        payload,

    metadata=
        metadata,

    priority=
        5,

    job_id=
        canonical_job_id,
)

check(
    "single canonical job created",
    created.job_id
    == canonical_job_id,
)

check(
    "initial status queued",
    created.status
    == "queued",
)

initial_jobs = (
    job_store.load_jobs()
)

check(
    "exactly one physical job before execution",
    len(
        initial_jobs
    )
    == 1,
)


# ============================================================
# RETRYABLE DISPATCHER
# ============================================================

dispatch_call_count = 0


def failing_handler_dispatcher(
    runtime_job,
):
    global dispatch_call_count

    dispatch_call_count += 1

    if (
        runtime_job.get(
            "job_id"
        )
        != canonical_job_id
    ):
        raise AssertionError(
            "Dispatcher received changed canonical job_id."
        )

    raise RuntimeError(
        "Synthetic retryable handler failure."
    )


# ============================================================
# ATTEMPT 1
# ============================================================

result_1 = (
    run_one_universal_runtime_job_v1(
        worker_id=
            "stage10_10bc_worker_1",

        dispatcher=
            failing_handler_dispatcher,
    )
)

check(
    "attempt 1 worker status RETRY_QUEUED",
    result_1[
        "worker_status"
    ]
    == "RETRY_QUEUED",
)

check(
    "attempt 1 number is 1",
    result_1[
        "attempt_number"
    ]
    == 1,
)

check(
    "attempt 1 maximum is 3",
    result_1[
        "maximum_attempts"
    ]
    == 3,
)

check(
    "attempt 1 retry scheduled",
    result_1[
        "retry_scheduled"
    ]
    is True,
)

check(
    "attempt 1 same canonical job_id",
    result_1[
        "job_id"
    ]
    == canonical_job_id,
)

check(
    "attempt 1 no replacement job",
    result_1[
        "retry_created_new_job"
    ]
    is False,
)

jobs_after_1 = (
    job_store.load_jobs()
)

check(
    "attempt 1 physical job count remains 1",
    len(
        jobs_after_1
    )
    == 1,
)

job_after_1 = (
    jobs_after_1[
        canonical_job_id
    ]
)

check(
    "attempt 1 persisted status queued",
    job_after_1.status
    == "queued",
)

check(
    "attempt 1 counter persisted",
    job_after_1.metadata.get(
        "runtime_failure_attempt_count"
    )
    == 1,
)


# ============================================================
# ATTEMPT 2
# ============================================================

result_2 = (
    run_one_universal_runtime_job_v1(
        worker_id=
            "stage10_10bc_worker_2",

        dispatcher=
            failing_handler_dispatcher,
    )
)

check(
    "attempt 2 worker status RETRY_QUEUED",
    result_2[
        "worker_status"
    ]
    == "RETRY_QUEUED",
)

check(
    "attempt 2 number is 2",
    result_2[
        "attempt_number"
    ]
    == 2,
)

check(
    "attempt 2 retry scheduled",
    result_2[
        "retry_scheduled"
    ]
    is True,
)

check(
    "attempt 2 same canonical job_id",
    result_2[
        "job_id"
    ]
    == canonical_job_id,
)

check(
    "attempt 2 no replacement job",
    result_2[
        "retry_created_new_job"
    ]
    is False,
)

jobs_after_2 = (
    job_store.load_jobs()
)

check(
    "attempt 2 physical job count remains 1",
    len(
        jobs_after_2
    )
    == 1,
)

job_after_2 = (
    jobs_after_2[
        canonical_job_id
    ]
)

check(
    "attempt 2 persisted status queued",
    job_after_2.status
    == "queued",
)

check(
    "attempt 2 counter persisted",
    job_after_2.metadata.get(
        "runtime_failure_attempt_count"
    )
    == 2,
)


# ============================================================
# ATTEMPT 3 — RETRY CEILING
# ============================================================

result_3 = (
    run_one_universal_runtime_job_v1(
        worker_id=
            "stage10_10bc_worker_3",

        dispatcher=
            failing_handler_dispatcher,
    )
)

check(
    "attempt 3 worker status FAILED",
    result_3[
        "worker_status"
    ]
    == "FAILED",
)

check(
    "attempt 3 number is 3",
    result_3[
        "attempt_number"
    ]
    == 3,
)

check(
    "attempt 3 retry not scheduled",
    result_3[
        "retry_scheduled"
    ]
    is False,
)

check(
    "attempt 3 retry exhausted",
    result_3[
        "retry_exhausted"
    ]
    is True,
)

check(
    "attempt 3 terminal status failed",
    result_3[
        "terminal_status"
    ]
    == "failed",
)

check(
    "attempt 3 same canonical job_id",
    result_3[
        "job_id"
    ]
    == canonical_job_id,
)

check(
    "attempt 3 no replacement job",
    result_3[
        "retry_created_new_job"
    ]
    is False,
)


# ============================================================
# FINAL PHYSICAL STORE ASSERTIONS
# ============================================================

final_jobs = (
    job_store.load_jobs()
)

check(
    "final physical job count is exactly 1",
    len(
        final_jobs
    )
    == 1,
)

check(
    "only original canonical job_id exists",
    list(
        final_jobs.keys()
    )
    == [
        canonical_job_id
    ],
)

final_job = (
    final_jobs[
        canonical_job_id
    ]
)

check(
    "final physical status failed",
    final_job.status
    == "failed",
)

check(
    "final failure attempt count is 3",
    final_job.metadata.get(
        "runtime_failure_attempt_count"
    )
    == 3,
)

check(
    "final maximum attempts persisted",
    final_job.metadata.get(
        "runtime_maximum_attempts"
    )
    == 3,
)

check(
    "final retry scheduled false",
    final_job.metadata.get(
        "runtime_retry_scheduled"
    )
    is False,
)

check(
    "final retry exhausted true",
    final_job.metadata.get(
        "runtime_retry_exhausted"
    )
    is True,
)

check(
    "canonical identity preservation persisted",
    final_job.metadata.get(
        "canonical_job_id_preserved"
    )
    is True,
)

check(
    "no retry replacement persisted",
    final_job.metadata.get(
        "retry_created_new_job"
    )
    is False,
)

check(
    "dispatcher called exactly 3 times",
    dispatch_call_count
    == 3,
)


# ============================================================
# TERMINAL JOB MUST NOT BE CLAIMED AGAIN
# ============================================================

result_4 = (
    run_one_universal_runtime_job_v1(
        worker_id=
            "stage10_10bc_worker_4",

        dispatcher=
            failing_handler_dispatcher,
    )
)

check(
    "terminal failed job is not reclaimed",
    result_4[
        "worker_status"
    ]
    == "IDLE",
)

check(
    "dispatcher remains at exactly 3 calls",
    dispatch_call_count
    == 3,
)


# ============================================================
# RESTORE PRODUCTION GLOBALS
# ============================================================

job_store.DATA_DIR = (
    PRODUCTION_DATA_DIR
)

job_store.JOBS_FILE = (
    PRODUCTION_JOBS_FILE
)

job_store.EVENTS_FILE = (
    PRODUCTION_EVENTS_FILE
)

if (
    PRODUCTION_LOCK_PATH
    is not None
    and hasattr(
        queue_module,
        "_LOCK_PATH",
    )
):
    queue_module._LOCK_PATH = (
        PRODUCTION_LOCK_PATH
    )


# ============================================================
# VERIFY PRODUCTION STORE UNCHANGED
# ============================================================

production_jobs_hash_after = (
    sha256_file(
        PRODUCTION_JOBS_FILE
    )
)

production_events_hash_after = (
    sha256_file(
        PRODUCTION_EVENTS_FILE
    )
)

check(
    "production jobs hash unchanged",
    production_jobs_hash_after
    == production_jobs_hash_before,
)

check(
    "production events hash unchanged",
    production_events_hash_after
    == production_events_hash_before,
)


# ============================================================
# CLEAN TEMP STORE
# ============================================================

shutil.rmtree(
    TEST_ROOT
)


print()
print("=" * 86)
print("VERIFICATION: PASS")
print("SAME_JOB_RETRY_ENFORCEMENT: PASS")
print("ATTEMPT_1: RETRY_QUEUED")
print("ATTEMPT_2: RETRY_QUEUED")
print("ATTEMPT_3: FAILED")
print("MAXIMUM_ATTEMPTS: 3")
print("CANONICAL_JOB_ID_PRESERVED_ALL_ATTEMPTS: True")
print("PHYSICAL_JOB_COUNT: 1")
print("NEW_RETRY_JOB_CREATED: False")
print("RETRY_EXHAUSTION_ENFORCED: True")
print("FAILED_JOB_RECLAIMED: False")
print("DISPATCH_CALL_COUNT: 3")
print("PRODUCTION_JOBS_HASH_UNCHANGED: True")
print("PRODUCTION_EVENTS_HASH_UNCHANGED: True")
print("TEMP_TEST_ROOT_REMOVED: True")
print("=" * 86)
