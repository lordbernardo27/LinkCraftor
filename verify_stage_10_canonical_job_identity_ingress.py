from __future__ import annotations

import importlib
import json
import os
import shutil
from pathlib import Path


ROOT = Path.cwd().resolve()

TEST_ROOT = (
    ROOT
    / "tmp"
    / "stage_10_canonical_job_identity"
)

STORE_FILE = (
    TEST_ROOT
    / "orchestration_jobs.json"
)

EVENT_FILE = (
    TEST_ROOT
    / "orchestration_job_events.jsonl"
)


def check(name: str, condition: bool, detail: str = "") -> None:
    result = "PASS" if condition else "FAIL"

    print(
        f"[{result}] {name}"
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


# ------------------------------------------------------------
# Redirect the orchestration store BEFORE importing job_store.
# ------------------------------------------------------------

os.environ[
    "ORCHESTRATION_JOBS_FILE"
] = str(STORE_FILE)

os.environ[
    "ORCHESTRATION_JOB_EVENTS_FILE"
] = str(EVENT_FILE)


import backend.server.orchestration.job_store as job_store

job_store = importlib.reload(
    job_store
)


print()
print("=" * 72)
print("STAGE 10 — CANONICAL JOB IDENTITY INGRESS VERIFICATION")
print("=" * 72)
print("TEST_ROOT:", TEST_ROOT)
print()


canonical_job_id = (
    "uj_stage10_"
    + ("a" * 24)
)


# ------------------------------------------------------------
# 1. CALLER-SUPPLIED ID
# ------------------------------------------------------------

first = job_store.create_job(
    workspace_id="ws_stage10_test",
    job_type="runtime_test_job",
    payload={
        "document_id":
            "uucd_" + ("b" * 32),

        "content_ref":
            "backend/server/data/"
            "universal_unified_content_documents/"
            "ws_stage10_test/documents/"
            "uucd_" + ("b" * 32) + ".json",
    },
    metadata={
        "test":
            True,
    },
    priority=5,
    job_id=canonical_job_id,
)

check(
    "caller job_id preserved",
    first.job_id == canonical_job_id,
    first.job_id,
)

check(
    "job starts queued",
    first.status == "queued",
    first.status,
)


# ------------------------------------------------------------
# 2. STORED UNDER SAME ID
# ------------------------------------------------------------

stored = job_store.get_job(
    canonical_job_id
)

check(
    "stored job exists",
    stored is not None,
)

check(
    "stored identity unchanged",
    stored.job_id == canonical_job_id,
    stored.job_id,
)


# ------------------------------------------------------------
# 3. RAW STORE CONTAINS SAME KEY
# ------------------------------------------------------------

raw = json.loads(
    STORE_FILE.read_text(
        encoding="utf-8"
    )
)

check(
    "raw store keyed by canonical job_id",
    canonical_job_id in raw,
)

check(
    "raw record job_id matches key",
    raw[
        canonical_job_id
    ][
        "job_id"
    ] == canonical_job_id,
)


# ------------------------------------------------------------
# 4. DUPLICATE CANONICAL ID FAILS CLOSED
# ------------------------------------------------------------

duplicate_rejected = False

try:
    job_store.create_job(
        workspace_id="ws_stage10_test",
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


# ------------------------------------------------------------
# 5. BACKWARD COMPATIBILITY
# ------------------------------------------------------------

legacy_style = job_store.create_job(
    workspace_id="ws_stage10_test",
    job_type="legacy_style_test",
)

check(
    "legacy caller still receives generated job_id",
    legacy_style.job_id.startswith(
        "job_"
    ),
    legacy_style.job_id,
)

check(
    "legacy job stored",
    job_store.get_job(
        legacy_style.job_id
    ) is not None,
)


# ------------------------------------------------------------
# 6. EVENT AUDIT
# ------------------------------------------------------------

event_text = EVENT_FILE.read_text(
    encoding="utf-8"
)

check(
    "caller-supplied identity event recorded",
    canonical_job_id in event_text,
)

check(
    "caller-supplied marker recorded",
    '"caller_supplied_job_id": true'
    in event_text.lower(),
)


# ------------------------------------------------------------
# FINAL
# ------------------------------------------------------------

print()
print("=" * 72)
print("VERIFICATION: PASS")
print("CANONICAL_JOB_ID_PRESERVED: True")
print("DUPLICATE_ID_REJECTED: True")
print("BACKWARD_COMPATIBILITY: PASS")
print("PRODUCTION_JOB_STORE_MODIFIED: False")
print("=" * 72)

shutil.rmtree(
    TEST_ROOT
)

print("TEMP_TEST_ROOT_REMOVED: True")
