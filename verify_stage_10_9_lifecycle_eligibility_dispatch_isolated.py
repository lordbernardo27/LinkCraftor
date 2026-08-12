from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path.cwd().resolve()

TEST_ROOT = (
    ROOT
    / "tmp"
    / "stage_10_9_lifecycle_eligibility"
)

TEST_UUCD_ROOT = (
    TEST_ROOT
    / "backend"
    / "server"
    / "data"
    / "universal_unified_content_documents"
    / "ws_stage10_9_test"
    / "documents"
)

TEST_BODY_ROOT = (
    TEST_ROOT
    / "backend"
    / "server"
    / "data"
    / "universal_article_body_store"
    / "ws_stage10_9_test"
    / "bodies"
)


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

TEST_UUCD_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)

TEST_BODY_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# IMPORT CANONICAL COMPONENTS
# ============================================================

import backend.server.runtime.lifecycle_eligibility_runtime_handler_v1 as eligibility

import backend.server.runtime.universal_runtime_registration as registry

from backend.server.runtime.uucd_runtime_handoff_registration_v1 import (
    register_uucd_runtime_handoff_v1,
)


# ============================================================
# SAVE REGISTRY STATE
# ============================================================

original_registry = dict(
    registry._RUNTIME_HANDLER_REGISTRY
)


# ============================================================
# PATCH PROJECT ROOT FOR ISOLATED FILE REFERENCES
# ============================================================

original_project_root = (
    eligibility._project_root
)

eligibility._project_root = (
    lambda: TEST_ROOT
)


print()
print("=" * 82)
print("STAGE 10.9 — LIFECYCLE ELIGIBILITY REAL DISPATCH VERIFICATION")
print("=" * 82)


# ============================================================
# SYNTHETIC CANONICAL BODY
# ============================================================

body_text = (
    "Stage 10.9 isolated canonical body for Lifecycle Eligibility."
)

body_bytes = body_text.encode(
    "utf-8"
)

content_hash = hashlib.sha256(
    body_bytes
).hexdigest()

document_id = (
    "uucd_"
    + ("a" * 32)
)

persistence_fingerprint = (
    "b" * 64
)

body_ref = (
    "backend/server/data/"
    "universal_article_body_store/"
    "ws_stage10_9_test/bodies/"
    "stage10_9_body.txt"
)

content_ref = (
    "backend/server/data/"
    "universal_unified_content_documents/"
    "ws_stage10_9_test/documents/"
    + document_id
    + ".json"
)

body_path = (
    TEST_ROOT
    / body_ref
)

uucd_path = (
    TEST_ROOT
    / content_ref
)

body_path.parent.mkdir(
    parents=True,
    exist_ok=True,
)

uucd_path.parent.mkdir(
    parents=True,
    exist_ok=True,
)

body_path.write_bytes(
    body_bytes
)


# ============================================================
# SYNTHETIC PERSISTED UUCD V2
# ============================================================

persisted_uucd = {
    "schema_version":
        "universal_unified_content_document_v2",

    "document_id":
        document_id,

    "workspace_id":
        "ws_stage10_9_test",

    "source_type":
        "website",

    "content_ref":
        content_ref,

    "body_ref":
        body_ref,

    "content_hash":
        content_hash,

    "metadata": {
        "persistence_status":
            "PERSISTED_AND_VERIFIED",
    },

    "handoff": {
        "uucd_persisted":
            True,

        "body_store_verified":
            True,

        "next_stage":
            "runtime_queue_handoff",
    },

    "persistence": {
        "persistence_status":
            "PERSISTED_AND_VERIFIED",

        "input_record_sha256":
            persistence_fingerprint,

        "content_body_stored_here":
            False,
    },
}

uucd_path.write_text(
    json.dumps(
        persisted_uucd,
        indent=2,
    ),
    encoding="utf-8",
)


# ============================================================
# RUNTIME JOB
# ============================================================

job = {
    "job_id":
        "uj_stage10_9_dispatch_test",

    "workspace_id":
        "ws_stage10_9_test",

    "job_type":
        "uucd_runtime_handoff",

    "status":
        "running",

    "payload": {
        "document_id":
            document_id,

        "content_ref":
            content_ref,

        "body_ref":
            body_ref,

        "source_type":
            "website",

        "content_hash":
            content_hash,

        "persistence_fingerprint":
            persistence_fingerprint,
    },

    "metadata": {
        "test_scope":
            "stage_10_9_isolated",
    },
}


# ============================================================
# CONFIRM REGISTRATION ABSENT BEFORE TEST
# ============================================================

registry._RUNTIME_HANDLER_REGISTRY.pop(
    "uucd_runtime_handoff",
    None,
)

check(
    "test registration absent initially",
    "uucd_runtime_handoff"
    not in registry._RUNTIME_HANDLER_REGISTRY,
)


# ============================================================
# REGISTER IN MEMORY ONLY
# ============================================================

registration = (
    register_uucd_runtime_handoff_v1(
        persist=False,
        replace=False,
    )
)

check(
    "registration created",
    isinstance(
        registration,
        dict,
    ),
)

check(
    "job type registered",
    "uucd_runtime_handoff"
    in registry._RUNTIME_HANDLER_REGISTRY,
)

public_registration = (
    registry.get_runtime_registration(
        "uucd_runtime_handoff"
    )
)

check(
    "registration readable",
    public_registration
    is not None,
)

check(
    "registration stage lifecycle_eligibility",
    public_registration[
        "stage"
    ]
    == "lifecycle_eligibility",
)

check(
    "registration successor semantic reader",
    "semantic_intelligence_runtime_reader"
    in public_registration[
        "successor_stages"
    ],
)


# ============================================================
# REAL DISPATCH SUCCESS PATH
# ============================================================

dispatch_result = (
    registry.dispatch_registered_runtime_handler(
        job
    )
)

check(
    "dispatcher handled job",
    dispatch_result[
        "handled"
    ]
    is True,
)

check(
    "dispatcher mode correct",
    dispatch_result[
        "dispatch_mode"
    ]
    == "universal_runtime_registration",
)

check(
    "dispatcher preserved job type",
    dispatch_result[
        "job_type"
    ]
    == "uucd_runtime_handoff",
)

handler_result = (
    dispatch_result[
        "handler_result"
    ]
)

check(
    "lifecycle eligible",
    handler_result[
        "lifecycle_eligible"
    ]
    is True,
)

check(
    "eligibility status ELIGIBLE",
    handler_result[
        "eligibility_status"
    ]
    == "ELIGIBLE",
)

check(
    "next stage semantic runtime reader",
    handler_result[
        "next_stage"
    ]
    == "semantic_intelligence_runtime_reader",
)

check(
    "job identity preserved through handler",
    handler_result[
        "job_id"
    ]
    == job[
        "job_id"
    ],
)

check(
    "body exists verified",
    handler_result[
        "body_verification"
    ][
        "body_exists"
    ]
    is True,
)

check(
    "body hash verified",
    handler_result[
        "body_verification"
    ][
        "body_sha256_verified"
    ]
    is True,
)

certificate = (
    handler_result[
        "certificate"
    ]
)

check(
    "certificate certified",
    certificate[
        "certificate_status"
    ]
    == "CERTIFIED",
)

check(
    "certificate lifecycle eligible",
    certificate[
        "lifecycle_eligible"
    ]
    is True,
)

check(
    "runtime content_body excluded",
    certificate[
        "content_body_in_runtime_job"
    ]
    is False,
)

check(
    "persisted UUCD content_body excluded",
    certificate[
        "content_body_in_persisted_uucd"
    ]
    is False,
)

check(
    "semantic processing not performed",
    certificate[
        "semantic_processing_performed"
    ]
    is False,
)


# ============================================================
# FAILURE PATH — CORRUPT BODY
# ============================================================

body_path.write_text(
    "corrupted body content",
    encoding="utf-8",
)

failure_raised = False
failure_type = None

try:
    registry.dispatch_registered_runtime_handler(
        job
    )

except Exception as exc:
    failure_raised = True
    failure_type = type(
        exc
    ).__name__

    print(
        "EXPECTED_FAILURE_TYPE:",
        failure_type,
    )

    print(
        "EXPECTED_FAILURE_MESSAGE:",
        str(
            exc
        ),
    )


check(
    "corrupt body fails closed",
    failure_raised,
)

check(
    "corrupt body rejected before semantic processing",
    failure_type
    in {
        "LifecycleEligibilityReferenceError",
        "LifecycleEligibilityContractError",
    },
)


# ============================================================
# CONTENT_BODY ATTACK PATH
# ============================================================

body_path.write_bytes(
    body_bytes
)

job_with_body = dict(
    job
)

job_with_body[
    "payload"
] = dict(
    job[
        "payload"
    ]
)

job_with_body[
    "payload"
][
    "content_body"
] = "MUST NOT ENTER RUNTIME"


content_body_rejected = False

try:
    registry.dispatch_registered_runtime_handler(
        job_with_body
    )

except Exception:
    content_body_rejected = True


check(
    "runtime content_body rejected",
    content_body_rejected,
)


# ============================================================
# RESTORE REGISTRY
# ============================================================

registry._RUNTIME_HANDLER_REGISTRY.clear()

registry._RUNTIME_HANDLER_REGISTRY.update(
    original_registry
)

eligibility._project_root = (
    original_project_root
)


# ============================================================
# CLEAN TEMP FILES
# ============================================================

shutil.rmtree(
    TEST_ROOT
)


print()
print("=" * 82)
print("VERIFICATION: PASS")
print("REGISTRATION_PATH: PASS")
print("REAL_DISPATCH_PATH: PASS")
print("LIFECYCLE_ELIGIBILITY: ELIGIBLE")
print("BODY_SHA256_VERIFIED: True")
print("UUCD_V2_VERIFIED: True")
print("PERSISTENCE_VERIFIED: True")
print("CANONICAL_JOB_ID_PRESERVED: True")
print("CONTENT_BODY_REJECTED: True")
print("CORRUPT_BODY_REJECTED: True")
print("SEMANTIC_PROCESSING_PERFORMED: False")
print("REGISTRATION_PERSISTED: False")
print("PRODUCTION_RUNTIME_REGISTRY_RESTORED: True")
print("TEMP_TEST_ROOT_REMOVED: True")
print("=" * 82)
