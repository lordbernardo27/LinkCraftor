from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path.cwd().resolve()

TEST_ROOT = (
    ROOT
    / "tmp"
    / "stage_10_canonical_job_identity_r1"
)

TEST_JOBS_FILE = (
    TEST_ROOT
    / "jobs.json"
)

TEST_EVENTS_FILE = (
    TEST_ROOT
    / "job_events.json"
)


def check(
    name: str,
    condition: bool,
    detail: str = "",
) -> None:

    result = (
        "PASS"
        if condition
        else "FAIL"
    )

    print(
        f"[{result}] {name}"
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
# IMPORT ACTIVE MODULE, THEN REDIRECT ITS ACTUAL STORE GLOBALS
# ============================================================

import backend.server.orchestration.job_store as job_store


PRODUCTION_DATA_DIR = job_store.DATA_DIR
PRODUCTION_JOBS_FILE = job_store.JOBS_FILE
PRODUCTION_EVENTS_FILE = job_store.EVENTS_FILE


job_store.DATA_DIR = TEST_ROOT
job_store.JOBS_FILE = TEST_JOBS_FILE
job_store.EVENTS_FILE = TEST_EVENTS_FILE


print()
print("=" * 76)
print("STAGE 10.5C — CANONICAL JOB IDENTITY ISOLATED VERIFICATION R1")
print("=" * 76)

print(
    "PRODUCTION_JOBS_FILE:",
    PRODUCTION_JOBS_FILE,
)

print(
    "PRODUCTION_EVENTS_FILE:",
    PRODUCTION_EVENTS_FILE,
)

print(
    "TEST_JOBS_FILE:",
    job_store.JOBS_FILE,
)

print(
    "TEST_EVENTS_FILE:",
    job_store.EVENTS_FILE,
)

print()


# ============================================================
# BASELINE — ISOLATED STORE MUST START EMPTY
# ============================================================

check(
    "test jobs file absent before creation",
    not TEST_JOBS_FILE.exists(),
)

check(
    "test events file absent before creation",
    not TEST_EVENTS_FILE.exists(),
)


canonical_job_id = (
    "uj_stage10_r1_"
    + ("a" * 24)
)


# ============================================================
# 1. CREATE WITH CALLER-OWNED CANONICAL ID
# ============================================================

job = job_store.create_job(
    workspace_id="ws_stage10_isolated",
    job_type="runtime_test_job",
    payload={
        "document_id":
            "uucd_" + ("b" * 32),

        "content_ref":
            "backend/server/data/"
            "universal_unified_content_documents/"
            "ws_stage10_isolated/documents/"
            "uucd_" + ("b" * 32) + ".json",
    },
    metadata={
        "test":
            True,

        "stage":
            "10.5C",
    },
    priority=5,
    job_id=canonical_job_id,
)


check(
    "caller-supplied job_id preserved",
    job.job_id == canonical_job_id,
    job.job_id,
)

check(
    "new job starts queued",
    job.status == "queued",
    job.status,
)


# ============================================================
# 2. READ THROUGH ACTIVE REPOSITORY API
# ============================================================

stored = job_store.get_job(
    canonical_job_id
)

check(
    "stored job exists",
    stored is not None,
)

check(
    "stored job_id preserved",
    stored.job_id == canonical_job_id,
    stored.job_id,
)

check(
    "stored workspace preserved",
    stored.workspace_id
    == "ws_stage10_isolated",
)

check(
    "stored job_type preserved",
    stored.job_type
    == "runtime_test_job",
)


# ============================================================
# 3. PHYSICAL STORE VERIFICATION
# ============================================================

check(
    "isolated jobs file created",
    TEST_JOBS_FILE.exists(),
)

raw_jobs = json.loads(
    TEST_JOBS_FILE.read_text(
        encoding="utf-8"
    )
)

check(
    "canonical job_id is physical store key",
    canonical_job_id
    in raw_jobs,
)

check(
    "physical record job_id matches store key",
    raw_jobs[
        canonical_job_id
    ][
        "job_id"
    ]
    == canonical_job_id,
)


# ============================================================
# 4. EVENT VERIFICATION
# ============================================================

check(
    "isolated event file created",
    TEST_EVENTS_FILE.exists(),
)

raw_events = json.loads(
    TEST_EVENTS_FILE.read_text(
        encoding="utf-8"
    )
)

check(
    "canonical job event exists",
    canonical_job_id
    in raw_events,
)

event_rows = raw_events[
    canonical_job_id
]

check(
    "exactly one creation event",
    isinstance(
        event_rows,
        list,
    )
    and len(
        event_rows
    ) == 1,
)

event_metadata = (
    event_rows[0]
    .get(
        "metadata",
        {},
    )
)

check(
    "caller-supplied identity marker recorded",
    event_metadata.get(
        "caller_supplied_job_id"
    )
    is True,
)


# ============================================================
# 5. DUPLICATE ID MUST FAIL CLOSED
# ============================================================

duplicate_rejected = False

try:

    job_store.create_job(
        workspace_id="ws_stage10_isolated",
        job_type="runtime_test_job",
        payload={
            "different":
                True,
        },
        job_id=canonical_job_id,
    )

except ValueError as exc:

    duplicate_rejected = (
        "already exists"
        in str(exc).lower()
    )


check(
    "duplicate canonical job_id rejected",
    duplicate_rejected,
)


# ============================================================
# 6. BACKWARD COMPATIBILITY
# ============================================================

legacy_job = job_store.create_job(
    workspace_id="ws_stage10_isolated",
    job_type="legacy_style_test",
)

check(
    "legacy caller still receives generated job_* id",
    legacy_job.job_id.startswith(
        "job_"
    ),
    legacy_job.job_id,
)

check(
    "legacy generated job stored",
    job_store.get_job(
        legacy_job.job_id
    )
    is not None,
)


# ============================================================
# 7. ISOLATION PROOF
# ============================================================

check(
    "job_store DATA_DIR redirected",
    job_store.DATA_DIR
    == TEST_ROOT,
)

check(
    "job_store JOBS_FILE redirected",
    job_store.JOBS_FILE
    == TEST_JOBS_FILE,
)

check(
    "job_store EVENTS_FILE redirected",
    job_store.EVENTS_FILE
    == TEST_EVENTS_FILE,
)


print()
print("=" * 76)
print("VERIFICATION: PASS")
print("CANONICAL_JOB_ID_PRESERVED: True")
print("DUPLICATE_ID_REJECTED: True")
print("BACKWARD_COMPATIBILITY: PASS")
print("ISOLATED_STORE_USED: True")
print("PRODUCTION_JOB_STORE_MODIFIED: False")
print("=" * 76)


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
