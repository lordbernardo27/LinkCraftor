from __future__ import annotations

import hashlib
import shutil
from pathlib import Path


ROOT = Path.cwd().resolve()

TEST_ROOT = (
    ROOT
    / "tmp"
    / "stage_10_10c_contract_error"
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


def check(name, condition, detail=""):
    print(
        f"[{'PASS' if condition else 'FAIL'}] {name}"
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


import backend.server.orchestration.job_store as job_store
import backend.server.orchestration.queue as queue_module

from backend.server.runtime.universal_runtime_worker_v1 import (
    run_one_universal_runtime_job_v1,
)

from backend.server.runtime.universal_runtime_registration import (
    get_runtime_registration,
)


# ============================================================
# SAVE PRODUCTION STATE
# ============================================================

PRODUCTION_DATA_DIR = job_store.DATA_DIR
PRODUCTION_JOBS_FILE = job_store.JOBS_FILE
PRODUCTION_EVENTS_FILE = job_store.EVENTS_FILE

PRODUCTION_LOCK_PATH = getattr(
    queue_module,
    "_LOCK_PATH",
    None,
)

production_jobs_hash_before = sha256_file(
    PRODUCTION_JOBS_FILE
)

production_events_hash_before = sha256_file(
    PRODUCTION_EVENTS_FILE
)


# ============================================================
# REDIRECT TO ISOLATED STORE
# ============================================================

job_store.DATA_DIR = TEST_ROOT
job_store.JOBS_FILE = TEST_JOBS_FILE
job_store.EVENTS_FILE = TEST_EVENTS_FILE

if hasattr(queue_module, "_LOCK_PATH"):
    queue_module._LOCK_PATH = TEST_LOCK_FILE


print()
print("=" * 86)
print("STAGE 10.10C — CONTRACT ERROR NO-RETRY ISOLATED VERIFICATION")
print("=" * 86)


# ============================================================
# VERIFY REGISTRATION POLICY
# ============================================================

registration = get_runtime_registration(
    "uucd_runtime_handoff"
)

check(
    "registration exists",
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

check(
    "contract errors are non-retryable",
    retry_policy.get(
        "retry_on_contract_error"
    )
    is False,
)

check(
    "handler errors remain retryable",
    retry_policy.get(
        "retry_on_handler_error"
    )
    is True,
)


# ============================================================
# CREATE ONE CANONICAL JOB
# ============================================================

canonical_job_id = (
    "uj_stage10_10c_contract_"
    + ("a" * 16)
)

workspace_id = (
    "ws_stage10_10c_contract"
)

job_store.create_job(
    workspace_id=
        workspace_id,

    job_type=
        "uucd_runtime_handoff",

    payload={
        "document_id":
            "uucd_" + ("b" * 32),

        "content_ref":
            "synthetic/content/ref",

        "body_ref":
            "synthetic/body/ref",

        "source_type":
            "website",

        "content_hash":
            "c" * 64,

        "persistence_fingerprint":
            "d" * 64,
    },

    metadata={
        "idempotency_key":
            "synthetic_contract_error_key",

        "body_content_in_job":
            False,
    },

    priority=
        5,

    job_id=
        canonical_job_id,
)


# ============================================================
# SYNTHETIC CONTRACT ERROR
# ============================================================

class LifecycleEligibilityContractError(
    ValueError
):
    pass


dispatch_call_count = 0


def contract_failure_dispatcher(
    runtime_job,
):
    global dispatch_call_count

    dispatch_call_count += 1

    check(
        "dispatcher receives same canonical job_id",
        runtime_job.get(
            "job_id"
        )
        == canonical_job_id,
    )

    raise LifecycleEligibilityContractError(
        "Synthetic contract violation."
    )


# ============================================================
# ATTEMPT 1
# ============================================================

result = (
    run_one_universal_runtime_job_v1(
        worker_id=
            "stage10_10c_contract_worker",

        dispatcher=
            contract_failure_dispatcher,
    )
)


check(
    "worker status FAILED immediately",
    result[
        "worker_status"
    ]
    == "FAILED",
)

check(
    "attempt number is 1",
    result[
        "attempt_number"
    ]
    == 1,
)

check(
    "classified as contract error",
    result[
        "contract_error"
    ]
    is True,
)

check(
    "retry type not allowed",
    result[
        "retry_type_allowed"
    ]
    is False,
)

check(
    "retry not allowed",
    result[
        "retry_allowed"
    ]
    is False,
)

check(
    "retry not scheduled",
    result[
        "retry_scheduled"
    ]
    is False,
)

check(
    "same canonical job_id returned",
    result[
        "job_id"
    ]
    == canonical_job_id,
)

check(
    "no replacement job created",
    result[
        "retry_created_new_job"
    ]
    is False,
)

check(
    "terminal status failed",
    result[
        "terminal_status"
    ]
    == "failed",
)


# ============================================================
# PERSISTED STATE
# ============================================================

jobs = job_store.load_jobs()

check(
    "physical job count remains exactly 1",
    len(jobs)
    == 1,
)

check(
    "only original canonical job exists",
    list(
        jobs.keys()
    )
    == [
        canonical_job_id
    ],
)

persisted = jobs[
    canonical_job_id
]

check(
    "persisted status failed",
    persisted.status
    == "failed",
)

check(
    "failure count persisted as 1",
    persisted.metadata.get(
        "runtime_failure_attempt_count"
    )
    == 1,
)

check(
    "contract-error flag persisted",
    persisted.metadata.get(
        "runtime_contract_error"
    )
    is True,
)

check(
    "retry scheduled false persisted",
    persisted.metadata.get(
        "runtime_retry_scheduled"
    )
    is False,
)

check(
    "retry type allowed false persisted",
    persisted.metadata.get(
        "runtime_retry_type_allowed"
    )
    is False,
)

check(
    "canonical job identity persisted",
    persisted.metadata.get(
        "canonical_job_id_preserved"
    )
    is True,
)


# ============================================================
# FAILED JOB MUST NOT BE RECLAIMED
# ============================================================

second = (
    run_one_universal_runtime_job_v1(
        worker_id=
            "stage10_10c_contract_worker_2",

        dispatcher=
            contract_failure_dispatcher,
    )
)

check(
    "failed contract job not reclaimed",
    second[
        "worker_status"
    ]
    == "IDLE",
)

check(
    "dispatcher called exactly once",
    dispatch_call_count
    == 1,
)


# ============================================================
# RESTORE PRODUCTION GLOBALS
# ============================================================

job_store.DATA_DIR = PRODUCTION_DATA_DIR
job_store.JOBS_FILE = PRODUCTION_JOBS_FILE
job_store.EVENTS_FILE = PRODUCTION_EVENTS_FILE

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
# PRODUCTION STORE MUST REMAIN UNCHANGED
# ============================================================

production_jobs_hash_after = sha256_file(
    PRODUCTION_JOBS_FILE
)

production_events_hash_after = sha256_file(
    PRODUCTION_EVENTS_FILE
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


shutil.rmtree(
    TEST_ROOT
)


print()
print("=" * 86)
print("VERIFICATION: PASS")
print("CONTRACT_ERROR_POLICY: PASS")
print("CONTRACT_ERROR_CLASSIFIED: True")
print("ATTEMPT_NUMBER: 1")
print("RETRY_ALLOWED: False")
print("RETRY_SCHEDULED: False")
print("TERMINAL_STATUS: FAILED")
print("CANONICAL_JOB_ID_PRESERVED: True")
print("PHYSICAL_JOB_COUNT: 1")
print("NEW_RETRY_JOB_CREATED: False")
print("FAILED_JOB_RECLAIMED: False")
print("DISPATCH_CALL_COUNT: 1")
print("PRODUCTION_JOBS_HASH_UNCHANGED: True")
print("PRODUCTION_EVENTS_HASH_UNCHANGED: True")
print("TEMP_TEST_ROOT_REMOVED: True")
print("=" * 86)
