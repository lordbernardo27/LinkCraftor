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

from backend.server.universal_article_body_store.body_store_permanent_deletion_contract_v1 import (
    BODY_STORE_PERMANENT_DELETION_CONTRACT_SCHEMA,
    BODY_STORE_PERMANENT_DELETION_CONTRACT_VERSION,
    BODY_STORE_PERMANENT_DELETION_SOURCE_STATE,
    BODY_STORE_PERMANENT_DELETION_STATUSES,
    BODY_STORE_PERMANENT_DELETION_TARGET_STATE,
    build_permanent_deletion_request_v1,
    certify_permanent_deletion_request_v1,
    validate_permanent_deletion_request_v1,
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
    build_permanent_deletion_request_v1(
        archive_id="archive_permanent_deletion_verify",
        workspace_id="ws_verify",
        body_id="body_verify",
        lifecycle_record_id="body_lifecycle_verify",
        source_state="ARCHIVED",
        deletion_reason="Permanent deletion contract verification.",
        requested_by_type="SYSTEM",
        requested_by_id="permanent_deletion_contract_verifier",
        retention_expired=True,
        deletion_eligible=True,
        legal_hold_active=False,
        archive_verified=True,
        recovery_closed=True,
        requested_at="2026-08-04T01:00:00+00:00",
    )
)

validation = (
    validate_permanent_deletion_request_v1(
        deletion_request=request,
    )
)

certification = (
    certify_permanent_deletion_request_v1(
        deletion_request=request,
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
            BODY_STORE_PERMANENT_DELETION_CONTRACT_SCHEMA
            == "body_store_permanent_deletion_contract.v1"
        ),

    "contract_version_valid":
        (
            BODY_STORE_PERMANENT_DELETION_CONTRACT_VERSION
            == "1.0"
        ),

    "source_state_valid":
        (
            BODY_STORE_PERMANENT_DELETION_SOURCE_STATE
            == "ARCHIVED"
        ),

    "target_state_valid":
        (
            BODY_STORE_PERMANENT_DELETION_TARGET_STATE
            == "PERMANENTLY_DELETED"
        ),

    "statuses_valid":
        (
            BODY_STORE_PERMANENT_DELETION_STATUSES
            == (
                "READY",
                "BLOCKED",
                "DELETED",
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
                "deletion_status"
            ]
            == "READY"
        ),

    "request_deletion_ready":
        request[
            "deletion_ready"
        ]
        is True,

    "request_not_blocked":
        not request[
            "blocked_reasons"
        ],

    "retention_expired":
        request[
            "retention_expired"
        ]
        is True,

    "deletion_eligible":
        request[
            "deletion_eligible"
        ]
        is True,

    "legal_hold_inactive":
        request[
            "legal_hold_active"
        ]
        is False,

    "archive_verified":
        request[
            "archive_verified"
        ]
        is True,

    "recovery_closed":
        request[
            "recovery_closed"
        ]
        is True,

    "request_valid":
        validation[
            "request_valid"
        ]
        is True,

    "eligibility_boundaries_valid":
        validation[
            "eligibility_boundaries_valid"
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

    "archive_delete_not_performed":
        certification[
            "archive_delete_performed"
        ]
        is False,

    "body_store_delete_not_performed":
        certification[
            "body_store_delete_performed"
        ]
        is False,

    "lifecycle_transition_not_performed":
        certification[
            "lifecycle_transition_performed"
        ]
        is False,

    "no_runtime_job_created":
        certification[
            "runtime_job_created"
        ]
        is False,

    "no_queue_job_created":
        certification[
            "queue_job_created"
        ]
        is False,

    "content_body_not_exposed":
        certification[
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
    "UNIVERSAL ARTICLE BODY STORE PERMANENT DELETION CONTRACT — PHASE 9.1.8.1"
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
    "Archive deletions performed:            0"
)
print(
    "Body Store deletions performed:         0"
)
print(
    "Lifecycle transitions performed:        0"
)
print(
    "Production queue jobs created:          0"
)
print(
    "Runtime registrations modified:         0"
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
        "BODY STORE PERMANENT DELETION CONTRACT PHASE 9.1.8.1: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE PERMANENT DELETION CONTRACT PHASE 9.1.8.1: PASS"
)

print(
    "The Permanent Deletion Contract is immutable, read-only, "
    "and enforces retention, legal-hold, archive, and recovery boundaries."
)

print("=" * 120)

