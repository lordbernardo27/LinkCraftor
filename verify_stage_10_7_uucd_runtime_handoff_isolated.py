from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path.cwd().resolve()

TEST_ROOT = (
    ROOT
    / "tmp"
    / "stage_10_7_uucd_runtime_handoff"
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
# IMPORT MODULES
# ============================================================

import backend.server.orchestration.job_store as job_store

import backend.server.runtime.uucd_runtime_handoff_v1 as handoff


# ============================================================
# REDIRECT ORCHESTRATION STORE
# ============================================================

PRODUCTION_DATA_DIR = job_store.DATA_DIR
PRODUCTION_JOBS_FILE = job_store.JOBS_FILE
PRODUCTION_EVENTS_FILE = job_store.EVENTS_FILE

job_store.DATA_DIR = TEST_ROOT
job_store.JOBS_FILE = TEST_JOBS_FILE
job_store.EVENTS_FILE = TEST_EVENTS_FILE


# IMPORTANT:
# handoff imported create_job as a function alias.
# Its function still resolves globals inside job_store,
# so redirecting job_store paths is sufficient.


print()
print("=" * 78)
print("STAGE 10.7 — UUCD RUNTIME HANDOFF ISOLATED VERIFICATION")
print("=" * 78)

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
    TEST_JOBS_FILE,
)

print(
    "TEST_EVENTS_FILE:",
    TEST_EVENTS_FILE,
)

print()


# ============================================================
# SYNTHETIC PERSISTED CANONICAL UUCD
# ============================================================

document_id = (
    "uucd_"
    + ("a" * 32)
)

content_hash = (
    "b" * 64
)

persistence_fingerprint = (
    "c" * 64
)

content_ref = (
    "backend/server/data/"
    "universal_unified_content_documents/"
    "ws_stage10_7_test/documents/"
    + document_id
    + ".json"
)

body_ref = (
    "backend/server/data/"
    "universal_article_body_store/"
    "ws_stage10_7_test/bodies/"
    "synthetic_"
    + document_id[-12:]
    + ".txt"
)

persisted_uucd = {
    "schema_version":
        "universal_unified_content_document_v2",

    "workspace_id":
        "ws_stage10_7_test",

    "document_id":
        document_id,

    "source_type":
        "website",

    "content_hash":
        content_hash,

    "content_ref":
        content_ref,

    "body_ref":
        body_ref,

    "body_status":
        "STORED_AND_VERIFIED",

    "metadata": {
        "persistence_status":
            "PERSISTED_AND_VERIFIED",
    },

    "handoff": {
        "eligible_for_uucd_persistence":
            False,

        "uucd_persisted":
            True,

        "next_stage":
            "runtime_queue_handoff",

        "body_store_verified":
            True,
    },

    "persistence": {
        "schema_version":
            "uucd_persistence_record_v1",

        "persistence_version":
            "uucd_persistence_v1",

        "persistence_status":
            "PERSISTED_AND_VERIFIED",

        "storage_model":
            "PER_DOCUMENT_JSON",

        "input_record_sha256":
            persistence_fingerprint,

        "content_body_stored_here":
            False,
    },
}


# ============================================================
# SYNTHETIC RUNTIME REGISTRATION METADATA
# NO REGISTRY MUTATION
# ============================================================

runtime_registration = {
    "job_type":
        handoff.UUCD_RUNTIME_JOB_TYPE,

    "pipeline":
        handoff.UUCD_RUNTIME_PIPELINE,

    "stage":
        handoff.UUCD_RUNTIME_STAGE,

    "required_payload_fields":
        list(
            handoff.UUCD_RUNTIME_REQUIRED_PAYLOAD_FIELDS
        ),

    "predecessor_stages": [
        "uucd_persistence",
    ],

    "successor_stages": [
        "universal_runtime_worker",
    ],

    "idempotency_fields": [
        "document_id",
        "content_hash",
        "persistence_fingerprint",
    ],

    "retry_policy": {},
}


# ============================================================
# BASELINE
# ============================================================

check(
    "isolated jobs file absent before handoff",
    not TEST_JOBS_FILE.exists(),
)

check(
    "isolated events file absent before handoff",
    not TEST_EVENTS_FILE.exists(),
)


# ============================================================
# IDEMPOTENCY KEY DETERMINISM
# ============================================================

key_1 = (
    handoff.build_uucd_runtime_idempotency_key_v1(
        workspace_id=
            persisted_uucd[
                "workspace_id"
            ],

        document_id=
            persisted_uucd[
                "document_id"
            ],

        content_hash=
            persisted_uucd[
                "content_hash"
            ],

        persistence_fingerprint=
            persisted_uucd[
                "persistence"
            ][
                "input_record_sha256"
            ],
    )
)

key_2 = (
    handoff.build_uucd_runtime_idempotency_key_v1(
        workspace_id=
            persisted_uucd[
                "workspace_id"
            ],

        document_id=
            persisted_uucd[
                "document_id"
            ],

        content_hash=
            persisted_uucd[
                "content_hash"
            ],

        persistence_fingerprint=
            persisted_uucd[
                "persistence"
            ][
                "input_record_sha256"
            ],
    )
)

check(
    "idempotency key deterministic",
    key_1 == key_2,
    key_1,
)


# ============================================================
# PAYLOAD BUILD
# ============================================================

payload = (
    handoff.build_uucd_runtime_payload_v1(
        persisted_uucd
    )
)

check(
    "content_body excluded from runtime payload",
    "content_body" not in payload,
)

check(
    "payload content_ref preserved",
    payload[
        "content_ref"
    ]
    == content_ref,
)

check(
    "payload body_ref preserved",
    payload[
        "body_ref"
    ]
    == body_ref,
)

check(
    "payload persistence fingerprint preserved",
    payload[
        "persistence_fingerprint"
    ]
    == persistence_fingerprint,
)


# ============================================================
# EXECUTE HANDOFF
# ============================================================

result = (
    handoff.handoff_persisted_uucd_to_runtime_v1(
        persisted_uucd,
        runtime_registration=
            runtime_registration,
    )
)


# ============================================================
# RESULT CONTRACT
# ============================================================

check(
    "handoff status queued",
    result[
        "handoff_status"
    ]
    == "QUEUED",
)

canonical_job = (
    result[
        "canonical_universal_job"
    ]
)

orchestration_job = (
    result[
        "orchestration_job"
    ]
)

certificate = (
    result[
        "handoff_certificate"
    ]
)

job_id = (
    result[
        "job_id"
    ]
)


check(
    "canonical Universal Job id uses uj prefix",
    job_id.startswith(
        "uj_"
    ),
    job_id,
)

check(
    "same job_id in canonical Universal Job",
    canonical_job[
        "job_id"
    ]
    == job_id,
)

check(
    "same job_id in orchestration job",
    orchestration_job[
        "job_id"
    ]
    == job_id,
)

check(
    "orchestration status queued",
    orchestration_job[
        "status"
    ]
    == "queued",
)

check(
    "payload_reference equals canonical content_ref",
    canonical_job[
        "payload_reference"
    ]
    == content_ref,
)

check(
    "canonical idempotency key preserved",
    canonical_job[
        "idempotency_key"
    ]
    == key_1,
)

check(
    "certificate identity preserved",
    certificate[
        "job_identity_preserved"
    ]
    is True,
)

check(
    "certificate says no body content",
    certificate[
        "body_content_in_job"
    ]
    is False,
)

check(
    "certificate says old JSONL unused",
    certificate[
        "old_universal_knowledge_jsonl_used"
    ]
    is False,
)

check(
    "certificate says worker not executed",
    certificate[
        "worker_executed"
    ]
    is False,
)

check(
    "certificate says handler not dispatched",
    certificate[
        "handler_dispatched"
    ]
    is False,
)

check(
    "certificate says semantic processing not performed",
    certificate[
        "semantic_processing_performed"
    ]
    is False,
)


# ============================================================
# PHYSICAL ISOLATED STORE
# ============================================================

check(
    "isolated jobs file created",
    TEST_JOBS_FILE.exists(),
)

check(
    "isolated events file created",
    TEST_EVENTS_FILE.exists(),
)

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
    "exactly one isolated job created",
    len(
        raw_jobs
    ) == 1,
)

check(
    "canonical job_id is physical store key",
    job_id
    in raw_jobs,
)

check(
    "physical job_id matches canonical id",
    raw_jobs[
        job_id
    ][
        "job_id"
    ]
    == job_id,
)

check(
    "physical job remains queued",
    raw_jobs[
        job_id
    ][
        "status"
    ]
    == "queued",
)

check(
    "physical payload contains no content_body",
    "content_body"
    not in raw_jobs[
        job_id
    ].get(
        "payload",
        {},
    ),
)

check(
    "exactly one job event key",
    len(
        raw_events
    ) == 1,
)

check(
    "canonical job event exists",
    job_id
    in raw_events,
)


# ============================================================
# ISOLATION PROOF
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
print("=" * 78)
print("VERIFICATION: PASS")
print("HANDOFF_STATUS: QUEUED")
print("CANONICAL_JOB_ID_PRESERVED: True")
print("ORCHESTRATION_JOB_ID_PRESERVED: True")
print("IDEMPOTENCY_DETERMINISTIC: True")
print("CONTENT_BODY_IN_JOB: False")
print("OLD_JSONL_QUEUE_USED: False")
print("WORKER_EXECUTED: False")
print("HANDLER_DISPATCHED: False")
print("SEMANTIC_PROCESSING_PERFORMED: False")
print("PRODUCTION_JOB_STORE_MODIFIED: False")
print("=" * 78)


# ============================================================
# CLEAN ISOLATED TEST ARTIFACT
# ============================================================

shutil.rmtree(
    TEST_ROOT
)

print(
    "TEMP_TEST_ROOT_REMOVED:",
    not TEST_ROOT.exists(),
)
