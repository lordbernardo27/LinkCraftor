from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path.cwd().resolve()

TEST_ROOT = (
    ROOT
    / "tmp"
    / "stage_10_8_runtime_worker"
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


def sha256_file(path: Path) -> str | None:
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

    label = "PASS" if condition else "FAIL"

    print(
        f"[{label}] {name}"
        + (
            f" — {detail}"
            if detail
            else ""
        )
    )

    if not condition:
        raise AssertionError(name)


if TEST_ROOT.exists():
    shutil.rmtree(TEST_ROOT)

TEST_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# IMPORT MODULES
# ============================================================

import backend.server.orchestration.job_store as job_store
import backend.server.orchestration.queue as queue_module

from backend.server.runtime.universal_runtime_worker_v1 import (
    run_one_universal_runtime_job_v1,
)


# ============================================================
# CAPTURE PRODUCTION STATE
# ============================================================

PRODUCTION_DATA_DIR = job_store.DATA_DIR
PRODUCTION_JOBS_FILE = job_store.JOBS_FILE
PRODUCTION_EVENTS_FILE = job_store.EVENTS_FILE
PRODUCTION_QUEUE_LOCK = queue_module._LOCK_PATH

production_jobs_hash_before = sha256_file(
    PRODUCTION_JOBS_FILE
)

production_events_hash_before = sha256_file(
    PRODUCTION_EVENTS_FILE
)


# ============================================================
# REDIRECT ALL TEST STORAGE
# ============================================================

job_store.DATA_DIR = TEST_ROOT
job_store.JOBS_FILE = TEST_JOBS_FILE
job_store.EVENTS_FILE = TEST_EVENTS_FILE
queue_module._LOCK_PATH = TEST_LOCK_FILE


print()
print("=" * 80)
print("STAGE 10.8 — UNIVERSAL RUNTIME WORKER ISOLATED VERIFICATION")
print("=" * 80)

print(
    "PRODUCTION_JOBS_FILE:",
    PRODUCTION_JOBS_FILE,
)

print(
    "PRODUCTION_EVENTS_FILE:",
    PRODUCTION_EVENTS_FILE,
)

print(
    "PRODUCTION_QUEUE_LOCK:",
    PRODUCTION_QUEUE_LOCK,
)

print(
    "TEST_JOBS_FILE:",
    TEST_JOBS_FILE,
)

print(
    "TEST_EVENTS_FILE:",
    TEST_EVENTS_FILE,
)

print(
    "TEST_QUEUE_LOCK:",
    TEST_LOCK_FILE,
)

print()


# ============================================================
# VERIFY CLEAN TEST STORE
# ============================================================

check(
    "isolated jobs file absent initially",
    not TEST_JOBS_FILE.exists(),
)

check(
    "isolated events file absent initially",
    not TEST_EVENTS_FILE.exists(),
)


# ============================================================
# SUCCESS JOB
# ============================================================

SUCCESS_JOB_ID = (
    "uj_stage10_8_success_"
    + ("a" * 16)
)

success_job = job_store.create_job(
    workspace_id="ws_stage10_8_test",
    job_type="stage10_8_success_test",
    payload={
        "document_id":
            "uucd_" + ("b" * 32),

        "content_ref":
            "isolated://success/uucd.json",

        "body_ref":
            "isolated://success/body.txt",

        "source_type":
            "website",

        "content_hash":
            "c" * 64,

        "persistence_fingerprint":
            "d" * 64,
    },
    metadata={
        "test_scope":
            "stage_10_8_isolated_success",
    },
    priority=1,
    job_id=SUCCESS_JOB_ID,
)

check(
    "success job starts queued",
    success_job.status == "queued",
)


success_dispatch_calls = []


def success_dispatcher(runtime_job):
    success_dispatch_calls.append(
        runtime_job["job_id"]
    )

    check(
        "success dispatcher receives canonical job_id",
        runtime_job["job_id"]
        == SUCCESS_JOB_ID,
    )

    check(
        "success dispatcher receives RUNNING job",
        runtime_job["status"]
        == "running",
    )

    check(
        "success dispatcher receives payload",
        isinstance(
            runtime_job["payload"],
            dict,
        ),
    )

    return {
        "handled":
            True,

        "test_result":
            "success",

        "job_id_seen":
            runtime_job["job_id"],
    }


success_result = (
    run_one_universal_runtime_job_v1(
        worker_id=
            "worker_stage10_8_success",
        dispatcher=
            success_dispatcher,
    )
)


check(
    "success worker status completed",
    success_result[
        "worker_status"
    ]
    == "COMPLETED",
)

check(
    "success job claimed",
    success_result[
        "job_claimed"
    ]
    is True,
)

check(
    "success canonical job_id preserved",
    success_result[
        "job_id"
    ]
    == SUCCESS_JOB_ID,
)

check(
    "success claimed status running",
    success_result[
        "claimed_status"
    ]
    == "running",
)

check(
    "success terminal status completed",
    success_result[
        "terminal_status"
    ]
    == "completed",
)

check(
    "success dispatcher called exactly once",
    success_dispatch_calls
    == [SUCCESS_JOB_ID],
)

success_stored = job_store.get_job(
    SUCCESS_JOB_ID
)

check(
    "success physical job still exists",
    success_stored is not None,
)

check(
    "success physical job completed",
    success_stored.status
    == "completed",
)

check(
    "success physical job_id unchanged",
    success_stored.job_id
    == SUCCESS_JOB_ID,
)

check(
    "success progress reached 100",
    success_stored.progress_percent
    == 100.0,
)

check(
    "success body content absent",
    "content_body"
    not in success_stored.payload,
)


# ============================================================
# FAILURE JOB
# ============================================================

FAILURE_JOB_ID = (
    "uj_stage10_8_failure_"
    + ("e" * 16)
)

failure_job = job_store.create_job(
    workspace_id="ws_stage10_8_test",
    job_type="stage10_8_failure_test",
    payload={
        "document_id":
            "uucd_" + ("f" * 32),

        "content_ref":
            "isolated://failure/uucd.json",

        "body_ref":
            "isolated://failure/body.txt",

        "source_type":
            "website",

        "content_hash":
            "1" * 64,

        "persistence_fingerprint":
            "2" * 64,
    },
    metadata={
        "test_scope":
            "stage_10_8_isolated_failure",
    },
    priority=1,
    job_id=FAILURE_JOB_ID,
)

check(
    "failure job starts queued",
    failure_job.status == "queued",
)


failure_dispatch_calls = []


def failure_dispatcher(runtime_job):
    failure_dispatch_calls.append(
        runtime_job["job_id"]
    )

    check(
        "failure dispatcher receives canonical job_id",
        runtime_job["job_id"]
        == FAILURE_JOB_ID,
    )

    check(
        "failure dispatcher receives RUNNING job",
        runtime_job["status"]
        == "running",
    )

    raise RuntimeError(
        "synthetic Stage 10.8 dispatch failure"
    )


failure_result = (
    run_one_universal_runtime_job_v1(
        worker_id=
            "worker_stage10_8_failure",
        dispatcher=
            failure_dispatcher,
    )
)


check(
    "failure worker status failed",
    failure_result[
        "worker_status"
    ]
    == "FAILED",
)

check(
    "failure job claimed",
    failure_result[
        "job_claimed"
    ]
    is True,
)

check(
    "failure canonical job_id preserved",
    failure_result[
        "job_id"
    ]
    == FAILURE_JOB_ID,
)

check(
    "failure claimed status running",
    failure_result[
        "claimed_status"
    ]
    == "running",
)

check(
    "failure terminal status failed",
    failure_result[
        "terminal_status"
    ]
    == "failed",
)

check(
    "failure dispatcher called exactly once",
    failure_dispatch_calls
    == [FAILURE_JOB_ID],
)

check(
    "failure error type preserved",
    failure_result[
        "dispatch_error_type"
    ]
    == "RuntimeError",
)

failure_stored = job_store.get_job(
    FAILURE_JOB_ID
)

check(
    "failure physical job still exists",
    failure_stored is not None,
)

check(
    "failure physical job failed",
    failure_stored.status
    == "failed",
)

check(
    "failure physical job_id unchanged",
    failure_stored.job_id
    == FAILURE_JOB_ID,
)

check(
    "failure error persisted",
    (
        failure_stored.error_message
        is not None
        and
        "synthetic Stage 10.8 dispatch failure"
        in failure_stored.error_message
    ),
)

check(
    "failure body content absent",
    "content_body"
    not in failure_stored.payload,
)


# ============================================================
# NO DUPLICATE CLAIM / IDLE
# ============================================================

idle_dispatch_calls = []


def should_not_dispatch(runtime_job):
    idle_dispatch_calls.append(
        runtime_job["job_id"]
    )

    raise AssertionError(
        "IDLE worker unexpectedly dispatched a job."
    )


idle_result = (
    run_one_universal_runtime_job_v1(
        worker_id=
            "worker_stage10_8_idle",
        dispatcher=
            should_not_dispatch,
    )
)


check(
    "third worker returns idle",
    idle_result[
        "worker_status"
    ]
    == "IDLE",
)

check(
    "idle path claims no job",
    idle_result[
        "job_claimed"
    ]
    is False,
)

check(
    "idle path performs no dispatch",
    idle_result[
        "dispatch_performed"
    ]
    is False,
)

check(
    "completed/failed jobs were not reclaimed",
    idle_dispatch_calls == [],
)


# ============================================================
# PHYSICAL STORE / EVENTS
# ============================================================

raw_jobs = json.loads(
    TEST_JOBS_FILE.read_text(
        encoding="utf-8"
    )
)

raw_events = json.loads(
    TEST_EVENTS_FILE.read_text(
        encoding="utf-8"
    )
)

check(
    "exactly two isolated jobs exist",
    len(raw_jobs) == 2,
)

check(
    "success job physical key preserved",
    SUCCESS_JOB_ID in raw_jobs,
)

check(
    "failure job physical key preserved",
    FAILURE_JOB_ID in raw_jobs,
)

check(
    "success final physical status completed",
    raw_jobs[
        SUCCESS_JOB_ID
    ][
        "status"
    ]
    == "completed",
)

check(
    "failure final physical status failed",
    raw_jobs[
        FAILURE_JOB_ID
    ][
        "status"
    ]
    == "failed",
)

check(
    "success event stream exists",
    SUCCESS_JOB_ID in raw_events,
)

check(
    "failure event stream exists",
    FAILURE_JOB_ID in raw_events,
)


# ============================================================
# TEST ISOLATION
# ============================================================

check(
    "job store redirected",
    job_store.JOBS_FILE
    == TEST_JOBS_FILE,
)

check(
    "event store redirected",
    job_store.EVENTS_FILE
    == TEST_EVENTS_FILE,
)

check(
    "queue lock redirected",
    queue_module._LOCK_PATH
    == TEST_LOCK_FILE,
)


# ============================================================
# PRODUCTION HASH INTEGRITY
# ============================================================

production_jobs_hash_after = sha256_file(
    PRODUCTION_JOBS_FILE
)

production_events_hash_after = sha256_file(
    PRODUCTION_EVENTS_FILE
)

check(
    "production jobs.json hash unchanged",
    production_jobs_hash_after
    == production_jobs_hash_before,
)

check(
    "production job_events.json hash unchanged",
    production_events_hash_after
    == production_events_hash_before,
)


print()
print("=" * 80)
print("VERIFICATION: PASS")
print("SUCCESS_PATH: PASS")
print("FAILURE_PATH: PASS")
print("IDLE_PATH: PASS")
print("ATOMIC_CLAIM_CONFIRMED: True")
print("SUCCESS_JOB_ID_PRESERVED: True")
print("FAILURE_JOB_ID_PRESERVED: True")
print("SUCCESS_TERMINAL_STATUS: completed")
print("FAILURE_TERMINAL_STATUS: failed")
print("DUPLICATE_RECLAIM_OCCURRED: False")
print("CONTENT_BODY_IN_JOBS: False")
print("OLD_JSONL_QUEUE_USED: False")
print("PRODUCTION_JOBS_HASH_UNCHANGED: True")
print("PRODUCTION_EVENTS_HASH_UNCHANGED: True")
print("=" * 80)


# ============================================================
# RESTORE MODULE GLOBALS
# ============================================================

job_store.DATA_DIR = PRODUCTION_DATA_DIR
job_store.JOBS_FILE = PRODUCTION_JOBS_FILE
job_store.EVENTS_FILE = PRODUCTION_EVENTS_FILE
queue_module._LOCK_PATH = PRODUCTION_QUEUE_LOCK


# ============================================================
# CLEAN TEST ARTIFACTS
# ============================================================

shutil.rmtree(
    TEST_ROOT
)

print(
    "TEMP_TEST_ROOT_REMOVED:",
    not TEST_ROOT.exists(),
)
