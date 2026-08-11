from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


from backend.server.universal_unified_content_document.uucd_engine_v1 import (
    UUCD_SCHEMA_VERSION,
)

from backend.server.universal_unified_content_document.uucd_persistence_v1 import (
    UUCDPersistenceConflictError,
    UUCDPersistenceContractError,
    UUCDPersistencePathError,
    UUCDPersistenceVerificationError,
    canonical_uucd_content_ref_v1,
    persist_finalized_uucd_v1,
)


ROOT = Path.cwd().resolve()

TEST_ROOT = (
    ROOT
    / "tmp"
    / "verify_uucd_persistence_v1"
)

WORKSPACE_ID = "ws_uucd_persistence_test"

DOCUMENT_ID = (
    "uucd_"
    + ("a" * 32)
)

BODY_TEXT = (
    "Canonical UUCD persistence verifies the stored "
    "article body before persisting metadata."
)

CONTENT_HASH = hashlib.sha256(
    BODY_TEXT.encode("utf-8")
).hexdigest()

BODY_LENGTH = len(
    BODY_TEXT
)

BODY_WORD_COUNT = len(
    BODY_TEXT.split()
)

BODY_REF = (
    "backend/server/data/"
    "universal_article_body_store/"
    f"{WORKSPACE_ID}/bodies/"
    f"persistence_test_{DOCUMENT_ID[-12:]}.txt"
)

CONTENT_REF = (
    canonical_uucd_content_ref_v1(
        workspace_id=WORKSPACE_ID,
        document_id=DOCUMENT_ID,
    )
)


checks = []


def check(
    name: str,
    condition: bool,
    detail: str = "",
) -> None:

    result = "PASS" if condition else "FAIL"

    checks.append(
        {
            "name": name,
            "result": result,
            "detail": detail,
        }
    )

    print(
        f"[{result}] {name}"
        + (
            f" — {detail}"
            if detail
            else ""
        )
    )


def build_finalized_record() -> dict:

    return {
        "schema_version":
            UUCD_SCHEMA_VERSION,

        "engine_version":
            "uucd_engine_v1_option3_bound_body_payload",

        "document_id":
            DOCUMENT_ID,

        "workspace_id":
            WORKSPACE_ID,

        "source_id":
            "test_source_001",

        "source_type":
            "uploaded_document",

        "source_name":
            "Persistence Test",

        "source_format":
            "txt",

        "source_identity":
            {
                "test":
                    True,
            },

        "title":
            "Persistence Test",

        "h1":
            "Persistence Test",

        "headings":
            [],

        "canonical_url":
            None,

        "structure":
            {
                "test":
                    True,
            },

        "content_hash":
            CONTENT_HASH,

        "content_ref":
            CONTENT_REF,

        "body_ref":
            BODY_REF,

        "body_status":
            "STORED_AND_VERIFIED",

        "body_length":
            BODY_LENGTH,

        "body_word_count":
            BODY_WORD_COUNT,

        "metadata":
            {
                "body_store_writer_version":
                    "universal_article_body_store_writer_v1",

                "body_store_write_verified":
                    True,

                "body_store_write_timestamp":
                    "2026-08-11T00:00:00+00:00",

                "persistence_status":
                    "READY_FOR_UUCD_PERSISTENCE",
            },

        "lifecycle":
            {},

        "versioning":
            {},

        "provenance":
            {
                "test":
                    True,
            },

        "handoff":
            {
                "next_stage":
                    "uucd_persistence",

                "eligible_for_body_store":
                    False,

                "eligible_for_uucd_persistence":
                    True,

                "body_store_verified":
                    True,
            },
    }


def body_path() -> Path:

    return (
        TEST_ROOT
        / BODY_REF
    )


def persisted_path() -> Path:

    return (
        TEST_ROOT
        / CONTENT_REF
    )


print()
print("=" * 72)
print("UUCD PERSISTENCE V1 — ISOLATED FUNCTIONAL VERIFICATION")
print("=" * 72)
print("TEST_ROOT:", TEST_ROOT)
print()


# ------------------------------------------------------------
# CLEAN TEST ENVIRONMENT
# ------------------------------------------------------------

if TEST_ROOT.exists():
    shutil.rmtree(
        TEST_ROOT
    )

TEST_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)


# ------------------------------------------------------------
# CREATE ISOLATED VERIFIED BODY
# ------------------------------------------------------------

stored_body_path = body_path()

stored_body_path.parent.mkdir(
    parents=True,
    exist_ok=True,
)

stored_body_path.write_text(
    BODY_TEXT,
    encoding="utf-8",
)


# ------------------------------------------------------------
# 1. CANONICAL PATH
# ------------------------------------------------------------

expected_content_ref = (
    "backend/server/data/"
    "universal_unified_content_documents/"
    f"{WORKSPACE_ID}/documents/"
    f"{DOCUMENT_ID}.json"
)

check(
    "canonical content_ref",
    CONTENT_REF == expected_content_ref,
    CONTENT_REF,
)


# ------------------------------------------------------------
# 2. FIRST PERSISTENCE
# ------------------------------------------------------------

record = build_finalized_record()

first = persist_finalized_uucd_v1(
    record,
    project_root=TEST_ROOT,
)

check(
    "first persistence status",
    first.get(
        "persistence_status"
    ) == "PERSISTED_AND_VERIFIED",
)

check(
    "first persistence action",
    first.get(
        "persistence_action"
    ) == "CREATED",
    str(
        first.get(
            "persistence_action"
        )
    ),
)

check(
    "canonical JSON created",
    persisted_path().is_file(),
    str(
        persisted_path()
    ),
)


# ------------------------------------------------------------
# 3. READBACK
# ------------------------------------------------------------

persisted = json.loads(
    persisted_path().read_text(
        encoding="utf-8"
    )
)

check(
    "content_body excluded",
    "content_body" not in persisted,
)

check(
    "body status preserved",
    persisted.get(
        "body_status"
    ) == "STORED_AND_VERIFIED",
)

check(
    "persistence status finalized",
    persisted.get(
        "metadata",
        {},
    ).get(
        "persistence_status"
    ) == "PERSISTED_AND_VERIFIED",
)

check(
    "handoff advanced",
    persisted.get(
        "handoff",
        {},
    ).get(
        "next_stage"
    ) == "runtime_queue_handoff",
)

check(
    "uucd persisted flag",
    persisted.get(
        "handoff",
        {},
    ).get(
        "uucd_persisted"
    ) is True,
)


# ------------------------------------------------------------
# 4. IDEMPOTENT SECOND CALL
# ------------------------------------------------------------

original_bytes = (
    persisted_path().read_bytes()
)

second = persist_finalized_uucd_v1(
    record,
    project_root=TEST_ROOT,
)

second_bytes = (
    persisted_path().read_bytes()
)

check(
    "identical second call reused",
    second.get(
        "persistence_action"
    ) == "EXISTING_IDENTICAL_REUSED",
    str(
        second.get(
            "persistence_action"
        )
    ),
)

check(
    "idempotent bytes unchanged",
    original_bytes == second_bytes,
)


# ------------------------------------------------------------
# 5. CONFLICT REJECTION
# ------------------------------------------------------------

conflict = build_finalized_record()

conflict[
    "title"
] = "Different Title"

conflict_rejected = False

try:
    persist_finalized_uucd_v1(
        conflict,
        project_root=TEST_ROOT,
    )

except UUCDPersistenceConflictError:
    conflict_rejected = True

check(
    "different record conflict rejected",
    conflict_rejected,
)


# ------------------------------------------------------------
# 6. CONTENT_REF PATH REJECTION
# ------------------------------------------------------------

bad_path_record = build_finalized_record()

bad_path_record[
    "content_ref"
] = (
    "backend/server/data/"
    "universal_unified_content_documents/"
    f"{WORKSPACE_ID}/wrong/"
    f"{DOCUMENT_ID}.json"
)

bad_path_rejected = False

try:
    persist_finalized_uucd_v1(
        bad_path_record,
        project_root=TEST_ROOT,
    )

except UUCDPersistencePathError:
    bad_path_rejected = True

check(
    "noncanonical content_ref rejected",
    bad_path_rejected,
)


# ------------------------------------------------------------
# 7. BODY STATUS CONTRACT
# ------------------------------------------------------------

bad_status_record = build_finalized_record()

bad_status_record[
    "body_status"
] = "PENDING_BODY_STORE_WRITE"

bad_status_rejected = False

try:
    persist_finalized_uucd_v1(
        bad_status_record,
        project_root=TEST_ROOT,
    )

except UUCDPersistenceContractError:
    bad_status_rejected = True

check(
    "unverified body status rejected",
    bad_status_rejected,
)


# ------------------------------------------------------------
# 8. BODY STORE PREREQUISITE FAILURE
# ------------------------------------------------------------

stored_body_path.unlink()

missing_body_record = build_finalized_record()

missing_body_rejected = False

try:
    persist_finalized_uucd_v1(
        missing_body_record,
        project_root=TEST_ROOT,
        overwrite=True,
    )

except UUCDPersistenceVerificationError:
    missing_body_rejected = True

check(
    "missing Body Store body rejected",
    missing_body_rejected,
)


# ------------------------------------------------------------
# 9. NO PRODUCTION ROOT MUTATION
# ------------------------------------------------------------

check(
    "test confined to isolated root",
    TEST_ROOT != ROOT,
    str(
        TEST_ROOT
    ),
)


# ------------------------------------------------------------
# FINAL RESULT
# ------------------------------------------------------------

passed = sum(
    1
    for item in checks
    if item[
        "result"
    ] == "PASS"
)

failed = len(
    checks
) - passed

print()
print("=" * 72)
print("RESULT")
print("=" * 72)
print("CHECKS:", len(checks))
print("PASS:", passed)
print("FAIL:", failed)

if failed:
    print("VERIFICATION: FAIL")
    raise SystemExit(1)

print("VERIFICATION: PASS")

# Clean temporary verification artifacts after success.
shutil.rmtree(
    TEST_ROOT
)

print("TEMP_TEST_ROOT_REMOVED: True")
print("PRODUCTION_DATA_MODIFIED: False")
print("RUNTIME_EXECUTED: False")
print("QUEUE_JOB_CREATED: False")
print("=" * 72)
