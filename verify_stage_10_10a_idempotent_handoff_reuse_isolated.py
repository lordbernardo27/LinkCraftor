from __future__ import annotations

import hashlib
import shutil
from pathlib import Path


ROOT = Path.cwd().resolve()

TEST_ROOT = (
    ROOT
    / "tmp"
    / "stage_10_10a_idempotency"
)

TEST_JOBS_FILE = (
    TEST_ROOT
    / "jobs.json"
)

TEST_EVENTS_FILE = (
    TEST_ROOT
    / "job_events.json"
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
# IMPORT CANONICAL MODULES
# ============================================================

import backend.server.orchestration.job_store as job_store

import backend.server.runtime.uucd_runtime_handoff_v1 as handoff


# ============================================================
# SAVE PRODUCTION STORE STATE
# ============================================================

PRODUCTION_DATA_DIR = job_store.DATA_DIR
PRODUCTION_JOBS_FILE = job_store.JOBS_FILE
PRODUCTION_EVENTS_FILE = job_store.EVENTS_FILE

production_jobs_hash_before = sha256_file(
    PRODUCTION_JOBS_FILE
)

production_events_hash_before = sha256_file(
    PRODUCTION_EVENTS_FILE
)


# ============================================================
# REDIRECT ORCHESTRATION STORE
# ============================================================

job_store.DATA_DIR = TEST_ROOT
job_store.JOBS_FILE = TEST_JOBS_FILE
job_store.EVENTS_FILE = TEST_EVENTS_FILE


print()
print("=" * 82)
print("STAGE 10.10A — IDEMPOTENT HANDOFF REUSE ISOLATED VERIFICATION")
print("=" * 82)


# ============================================================
# CANONICAL LOGICAL IDENTITY
# ============================================================

workspace_id = "ws_stage10_10a_test"
document_id = "uucd_" + ("a" * 32)
content_hash = "b" * 64
persistence_fingerprint = "c" * 64

idempotency_key = (
    handoff.build_uucd_runtime_idempotency_key_v1(
        workspace_id=workspace_id,
        document_id=document_id,
        content_hash=content_hash,
        persistence_fingerprint=persistence_fingerprint,
        job_type=handoff.UUCD_RUNTIME_JOB_TYPE,
    )
)

check(
    "idempotency key created",
    isinstance(idempotency_key, str)
    and bool(idempotency_key),
    idempotency_key,
)


# ============================================================
# INSERT ONE EXISTING CANONICAL ORCHESTRATION JOB
# ============================================================

canonical_job_id = (
    "uj_stage10_10a_"
    + ("d" * 20)
)

canonical_universal_job = {
    "job_id":
        canonical_job_id,

    "workspace_id":
        workspace_id,

    "job_type":
        handoff.UUCD_RUNTIME_JOB_TYPE,

    "idempotency_key":
        idempotency_key,

    "payload_reference":
        (
            "backend/server/data/"
            "universal_unified_content_documents/"
            f"{workspace_id}/documents/{document_id}.json"
        ),

    "contract_version":
        "universal_job_contract_v2.1.1-r1",
}

existing_job = job_store.create_job(
    workspace_id=workspace_id,
    job_type=handoff.UUCD_RUNTIME_JOB_TYPE,
    payload={
        "document_id":
            document_id,

        "content_ref":
            canonical_universal_job[
                "payload_reference"
            ],

        "body_ref":
            (
                "backend/server/data/"
                "universal_article_body_store/"
                f"{workspace_id}/bodies/test.txt"
            ),

        "source_type":
            "website",

        "content_hash":
            content_hash,

        "persistence_fingerprint":
            persistence_fingerprint,
    },
    metadata={
        "canonical_universal_job":
            canonical_universal_job,

        "idempotency_key":
            idempotency_key,

        "persistence_fingerprint":
            persistence_fingerprint,

        "body_content_in_job":
            False,
    },
    priority=5,
    job_id=canonical_job_id,
)

check(
    "existing job created in isolated store",
    existing_job.job_id
    == canonical_job_id,
)

check(
    "existing job starts queued",
    existing_job.status
    == "queued",
)


# ============================================================
# VERIFY HELPER FINDS SAME JOB
# ============================================================

found = (
    handoff._find_existing_orchestration_job_by_idempotency_key_v1(
        workspace_id=workspace_id,
        job_type=handoff.UUCD_RUNTIME_JOB_TYPE,
        idempotency_key=idempotency_key,
    )
)

check(
    "existing idempotent job found",
    found is not None,
)

check(
    "helper preserves canonical job_id",
    found.job_id
    == canonical_job_id,
)


# ============================================================
# PATCH ONLY PRE-CREATION VALIDATION FOR BRANCH TEST
# ============================================================

original_validate = (
    handoff._validate_persisted_uucd
)

original_payload_builder = (
    handoff.build_uucd_runtime_payload_v1
)

original_registration_resolver = (
    handoff._resolve_runtime_registration
)

original_create_universal_job = (
    handoff.create_universal_job
)


handoff._validate_persisted_uucd = (
    lambda record: {
        "workspace_id":
            workspace_id,

        "document_id":
            document_id,

        "content_ref":
            canonical_universal_job[
                "payload_reference"
            ],

        "body_ref":
            (
                "backend/server/data/"
                "universal_article_body_store/"
                f"{workspace_id}/bodies/test.txt"
            ),

        "source_type":
            "website",

        "content_hash":
            content_hash,

        "persistence_fingerprint":
            persistence_fingerprint,
    }
)


handoff.build_uucd_runtime_payload_v1 = (
    lambda record: {
        "document_id":
            document_id,

        "content_ref":
            canonical_universal_job[
                "payload_reference"
            ],

        "body_ref":
            (
                "backend/server/data/"
                "universal_article_body_store/"
                f"{workspace_id}/bodies/test.txt"
            ),

        "source_type":
            "website",

        "content_hash":
            content_hash,

        "persistence_fingerprint":
            persistence_fingerprint,
    }
)


handoff._resolve_runtime_registration = (
    lambda **kwargs: {
        "job_type":
            handoff.UUCD_RUNTIME_JOB_TYPE,
    }
)


create_universal_job_called = False


def forbidden_create_universal_job(
    **kwargs,
):
    global create_universal_job_called

    create_universal_job_called = True

    raise AssertionError(
        "create_universal_job MUST NOT run "
        "for an idempotent duplicate handoff."
    )


handoff.create_universal_job = (
    forbidden_create_universal_job
)


# ============================================================
# EXECUTE DUPLICATE HANDOFF
# ============================================================

result = (
    handoff.handoff_persisted_uucd_to_runtime_v1(
        {
            "synthetic":
                True,
        }
    )
)


# ============================================================
# VERIFY IDEMPOTENT REUSE
# ============================================================

check(
    "handoff reports idempotent reuse",
    result[
        "handoff_status"
    ]
    == "IDEMPOTENT_REUSE",
)

check(
    "same canonical job_id returned",
    result[
        "job_id"
    ]
    == canonical_job_id,
)

check(
    "idempotency key preserved",
    result[
        "idempotency_key"
    ]
    == idempotency_key,
)

check(
    "idempotent reuse flag true",
    result[
        "idempotent_reuse"
    ]
    is True,
)

check(
    "new Universal Job not created",
    result[
        "new_universal_job_created"
    ]
    is False,
)

check(
    "new orchestration job not created",
    result[
        "new_orchestration_job_created"
    ]
    is False,
)

check(
    "create_universal_job was never called",
    create_universal_job_called
    is False,
)

check(
    "body content remains excluded",
    result[
        "body_content_in_job"
    ]
    is False,
)


# ============================================================
# PHYSICAL STORE MUST STILL CONTAIN EXACTLY ONE JOB
# ============================================================

jobs_after = job_store.load_jobs()

check(
    "exactly one isolated orchestration job exists",
    len(jobs_after)
    == 1,
)

check(
    "physical store still uses original canonical job_id",
    canonical_job_id
    in jobs_after,
)

check(
    "no replacement job identity minted",
    list(
        jobs_after.keys()
    )
    == [
        canonical_job_id
    ],
)


# ============================================================
# RESTORE PATCHED FUNCTIONS
# ============================================================

handoff._validate_persisted_uucd = (
    original_validate
)

handoff.build_uucd_runtime_payload_v1 = (
    original_payload_builder
)

handoff._resolve_runtime_registration = (
    original_registration_resolver
)

handoff.create_universal_job = (
    original_create_universal_job
)


# ============================================================
# RESTORE PRODUCTION STORE GLOBALS
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


# ============================================================
# VERIFY PRODUCTION HASHES
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


# ============================================================
# CLEAN TEMP STORE
# ============================================================

shutil.rmtree(
    TEST_ROOT
)


print()
print("=" * 82)
print("VERIFICATION: PASS")
print("IDEMPOTENCY_ENFORCEMENT: PASS")
print("IDEMPOTENT_REUSE: True")
print("SAME_CANONICAL_JOB_ID: True")
print("NEW_UNIVERSAL_JOB_CREATED: False")
print("NEW_ORCHESTRATION_JOB_CREATED: False")
print("DUPLICATE_JOB_COUNT: 0")
print("CONTENT_BODY_IN_JOB: False")
print("PRODUCTION_JOBS_HASH_UNCHANGED: True")
print("PRODUCTION_EVENTS_HASH_UNCHANGED: True")
print("TEMP_TEST_ROOT_REMOVED: True")
print("=" * 82)
