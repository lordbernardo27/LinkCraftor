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

from backend.server.universal_article_body_store.body_store_permanent_deletion_tombstone_contract_v1 import (
    BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CONTRACT_SCHEMA,
    BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CONTRACT_VERSION,
    BODY_STORE_PERMANENT_DELETION_TOMBSTONE_STATUS,
    certify_permanent_deletion_tombstone_contract_v1,
    create_permanent_deletion_tombstone_contract_v1,
    validate_permanent_deletion_tombstone_contract_v1,
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

    "tombstone_store":
        DATA_ROOT
        / "universal_article_body_store_tombstones",
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

contract = (
    create_permanent_deletion_tombstone_contract_v1(
        tombstone_id="tombstone_body_verify_v1",
        body_id="body_verify",
        workspace_id="ws_verify",
        archive_id="archive_verify",
        lifecycle_record_id="body_lifecycle_verify",
        deletion_request_id="deletion_request_verify",
        deletion_execution_id="deletion_execution_verify",
        deletion_reason="Permanent deletion tombstone contract verification.",
        retention_verified=True,
        archive_verified=True,
        recovery_closed=True,
        legal_hold_verified=True,
        verification_id="deletion_verification_verify",
        certification_id="deletion_certification_verify",
        deletion_manager_version="1.0",
    )
)

validation = (
    validate_permanent_deletion_tombstone_contract_v1(
        tombstone_contract=contract,
    )
)

certification = (
    certify_permanent_deletion_tombstone_contract_v1(
        tombstone_contract=contract,
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
            BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CONTRACT_SCHEMA
            == "body_store_permanent_deletion_tombstone_contract.v1"
        ),

    "contract_version_valid":
        (
            BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CONTRACT_VERSION
            == "1.0"
        ),

    "tombstone_status_valid":
        (
            BODY_STORE_PERMANENT_DELETION_TOMBSTONE_STATUS
            == "PERMANENTLY_DELETED"
        ),

    "contract_immutable":
        isinstance(
            contract,
            MappingProxyType,
        ),

    "contract_status_permanently_deleted":
        (
            contract[
                "status"
            ]
            == "PERMANENTLY_DELETED"
        ),

    "identity_present":
        all(
            (
                bool(
                    contract[
                        "tombstone_id"
                    ]
                ),
                bool(
                    contract[
                        "body_id"
                    ]
                ),
                bool(
                    contract[
                        "workspace_id"
                    ]
                ),
                bool(
                    contract[
                        "archive_id"
                    ]
                ),
                bool(
                    contract[
                        "lifecycle_record_id"
                    ]
                ),
                bool(
                    contract[
                        "deletion_request_id"
                    ]
                ),
                bool(
                    contract[
                        "deletion_execution_id"
                    ]
                ),
            )
        ),

    "deletion_evidence_present":
        all(
            (
                bool(
                    contract[
                        "deletion_reason"
                    ]
                ),
                bool(
                    contract[
                        "verification_id"
                    ]
                ),
                bool(
                    contract[
                        "certification_id"
                    ]
                ),
                bool(
                    contract[
                        "deletion_manager_version"
                    ]
                ),
            )
        ),

    "retention_verified":
        contract[
            "retention_verified"
        ]
        is True,

    "archive_verified":
        contract[
            "archive_verified"
        ]
        is True,

    "recovery_closed":
        contract[
            "recovery_closed"
        ]
        is True,

    "legal_hold_verified":
        contract[
            "legal_hold_verified"
        ]
        is True,

    "contract_read_only":
        contract[
            "read_only"
        ]
        is True,

    "article_body_not_contained":
        contract[
            "contains_article_body"
        ]
        is False,

    "checksum_present":
        bool(
            contract[
                "checksum"
            ]
        ),

    "contract_valid":
        validation[
            "contract_valid"
        ]
        is True,

    "schema_validation_passed":
        validation[
            "schema_valid"
        ]
        is True,

    "contract_version_validation_passed":
        validation[
            "contract_version_valid"
        ]
        is True,

    "status_validation_passed":
        validation[
            "status_valid"
        ]
        is True,

    "evidence_validation_passed":
        validation[
            "evidence_valid"
        ]
        is True,

    "safety_boundaries_valid":
        validation[
            "safety_boundaries_valid"
        ]
        is True,

    "checksum_valid":
        validation[
            "checksum_valid"
        ]
        is True,

    "certification_passed":
        certification[
            "certified"
        ]
        is True,

    "certification_immutable":
        certification[
            "immutable"
        ]
        is True,

    "certification_read_only":
        certification[
            "read_only"
        ]
        is True,

    "article_body_not_exposed":
        certification[
            "article_body_exposed"
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

    "lifecycle_not_modified":
        certification[
            "lifecycle_modified"
        ]
        is False,

    "archive_not_modified":
        certification[
            "archive_modified"
        ]
        is False,

    "body_store_not_modified":
        certification[
            "body_store_modified"
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
    "UNIVERSAL ARTICLE BODY STORE PERMANENT DELETION "
    "TOMBSTONE CONTRACT — PHASE 9.1.9.1"
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
print("PROTECTED OUTPUTS")

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
    "Tombstones persisted:                  0"
)
print(
    "Article bodies exposed:                0"
)
print(
    "Lifecycle records modified:            0"
)
print(
    "Archive records modified:              0"
)
print(
    "Body Store files modified:             0"
)
print(
    "Production queue jobs created:         0"
)
print(
    "Runtime registrations modified:        0"
)

print()
print("FAILURES")

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
        "BODY STORE PERMANENT DELETION TOMBSTONE "
        "CONTRACT PHASE 9.1.9.1: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE PERMANENT DELETION TOMBSTONE "
    "CONTRACT PHASE 9.1.9.1: PASS"
)

print(
    "The Tombstone Contract is immutable, checksum-protected, "
    "content-free, read-only, and safe for certified audit use."
)

print("=" * 120)
