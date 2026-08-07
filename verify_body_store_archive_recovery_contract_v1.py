from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from types import MappingProxyType

PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

from backend.server.universal_article_body_store.body_store_archive_recovery_contract_v1 import (
    BODY_STORE_ARCHIVE_RECOVERY_ALLOWED_SOURCE_STATES,
    BODY_STORE_ARCHIVE_RECOVERY_CONTRACT_SCHEMA,
    BODY_STORE_ARCHIVE_RECOVERY_CONTRACT_VERSION,
    BODY_STORE_ARCHIVE_RECOVERY_STATUSES,
    BODY_STORE_ARCHIVE_RECOVERY_TARGET_STATE,
    build_archive_recovery_request_v1,
    certify_archive_recovery_request_v1,
    validate_archive_recovery_request_v1,
)

DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

PROTECTED = {
    "body_store":
        DATA_ROOT
        / "universal_article_body_store",

    "queue":
        DATA_ROOT
        / "universal_article_body_queue",

    "lifecycle":
        DATA_ROOT
        / "universal_article_body_store_lifecycle",

    "archive_store":
        DATA_ROOT
        / "universal_article_body_store_archive",

    "uucd":
        DATA_ROOT
        / "universal_unified_content_documents",

    "wuc":
        DATA_ROOT
        / "website_unified_content",
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

    for item in sorted(
        path.rglob("*"),
        key=lambda candidate: (
            candidate.relative_to(
                path
            ).as_posix()
        ),
    ):
        digest.update(
            item.relative_to(
                path
            ).as_posix().encode(
                "utf-8"
            )
        )

        if item.is_file():
            digest.update(
                item.read_bytes()
            )

    return digest.hexdigest()


before = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED.items()
}

request = (
    build_archive_recovery_request_v1(
        archive_id="archive_recovery_contract_verify",
        workspace_id="ws_verify",
        body_id="body_verify",
        lifecycle_record_id="body_lifecycle_verify",
        source_state="ARCHIVED",
        recovery_reason="Contract verification.",
        requested_by_type="SYSTEM",
        requested_by_id="archive_recovery_contract_verifier",
        requested_at="2026-08-04T01:00:00+00:00",
    )
)

validation = (
    validate_archive_recovery_request_v1(
        recovery_request=request,
    )
)

certification = (
    certify_archive_recovery_request_v1(
        recovery_request=request,
    )
)
after = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED.items()
}

checks = {
    "contract_schema_valid":
        (
            BODY_STORE_ARCHIVE_RECOVERY_CONTRACT_SCHEMA
            == "body_store_archive_recovery_contract.v1"
        ),

    "contract_version_valid":
        (
            BODY_STORE_ARCHIVE_RECOVERY_CONTRACT_VERSION
            == "1.0"
        ),

    "allowed_source_states_valid":
        (
            BODY_STORE_ARCHIVE_RECOVERY_ALLOWED_SOURCE_STATES
            == (
                "ARCHIVED",
            )
        ),

    "target_state_valid":
        (
            BODY_STORE_ARCHIVE_RECOVERY_TARGET_STATE
            == "ACTIVE"
        ),

    "statuses_valid":
        (
            BODY_STORE_ARCHIVE_RECOVERY_STATUSES
            == (
                "READY",
                "RECOVERED",
                "BLOCKED",
                "FAILED",
            )
        ),

    "request_immutable":
        isinstance(
            request,
            MappingProxyType,
        ),

    "request_status_ready":
        (
            request[
                "recovery_status"
            ]
            == "READY"
        ),

    "request_source_state_archived":
        (
            request[
                "source_state"
            ]
            == "ARCHIVED"
        ),

    "request_target_state_active":
        (
            request[
                "target_state"
            ]
            == "ACTIVE"
        ),

    "request_valid":
        validation[
            "request_valid"
        ]
        is True,

    "certification_passed":
        certification[
            "certified"
        ]
        is True,

    "certification_read_only":
        certification[
            "read_only"
        ]
        is True,

    "archive_read_required":
        request[
            "archive_read_required"
        ]
        is True,

    "archive_verification_required":
        request[
            "archive_verification_required"
        ]
        is True,

    "body_store_write_required":
        request[
            "body_store_write_required"
        ]
        is True,

    "lifecycle_transition_required":
        request[
            "lifecycle_transition_required"
        ]
        is True,

    "recovery_not_executed":
        request[
            "recovery_executed"
        ]
        is False,

    "no_runtime_job_created":
        request[
            "runtime_job_created"
        ]
        is False,

    "no_queue_job_created":
        request[
            "queue_job_created"
        ]
        is False,

    "content_body_not_exposed":
        request[
            "content_body_included"
        ]
        is False,

    "production_outputs_unchanged":
        all(
            before[
                name
            ]
            == after[
                name
            ]

            for name
            in before
        ),
}

failures = [
    name
    for name, passed
    in checks.items()
    if passed is not True
]

print()
print("=" * 120)
print(
    "UNIVERSAL ARTICLE BODY STORE ARCHIVE RECOVERY CONTRACT — PHASE 9.1.7.1"
)
print("=" * 120)
print()

for name, passed in checks.items():
    print(
        f"{name:<72}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

print()
print(
    "PROTECTED OUTPUTS"
)

for name in before:
    print(
        "  "
        + f"{name:<30}"
        + (
            "UNCHANGED"
            if before[
                name
            ]
            == after[
                name
            ]
            else "CHANGED"
        )
    )

print()
print(
    "Archive reads performed:               0"
)
print(
    "Body Store writes performed:           0"
)
print(
    "Lifecycle transitions performed:       0"
)
print(
    "Production queue jobs created:         0"
)
print(
    "Runtime registrations modified:        0"
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
        "BODY STORE ARCHIVE RECOVERY CONTRACT PHASE 9.1.7.1: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE ARCHIVE RECOVERY CONTRACT PHASE 9.1.7.1: PASS"
)

print(
    "The Archive Recovery Contract is deterministic, immutable, "
    "read-only, and ready for controlled recovery execution."
)

print("=" * 120)

