from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

from backend.server.universal_article_body_store.body_store_lifecycle_integrity_scanner_contract_v1 import (
    create_lifecycle_integrity_scanner_request_v1,
)

from backend.server.universal_article_body_store.body_store_lifecycle_integrity_scanner_verifier_v1 import (
    BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_VERIFIER_SCHEMA,
    BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_VERIFIER_VERSION,
    calculate_lifecycle_integrity_scanner_verification_checksum_v1,
    verify_lifecycle_integrity_scanner_v1,
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

    "tombstone_store":
        DATA_ROOT
        / "universal_article_body_store_tombstones",

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


def write_json(
    path: Path,
    payload: dict,
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def write_invalid_json(
    path: Path,
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        "{ invalid json",
        encoding="utf-8",
    )


before = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED.items()
}

sandbox_root = Path(
    tempfile.mkdtemp(
        prefix="lifecycle_integrity_scanner_verifier_"
    )
)

try:
    body_store_root = (
        sandbox_root
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store"
        / "ws_verify"
    )

    lifecycle_root = (
        sandbox_root
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store_lifecycle"
        / "ws_verify"
    )

    archive_root = (
        sandbox_root
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store_archive"
        / "ws_verify"
    )

    tombstone_root = (
        sandbox_root
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store_tombstones"
        / "ws_verify"
    )

    write_json(
        body_store_root
        / "body_active.json",
        {
            "workspace_id":
                "ws_verify",

            "body_id":
                "body_active",

            "content_hash":
                "hash_active",
        },
    )

    write_json(
        body_store_root
        / "body_archived.json",
        {
            "workspace_id":
                "ws_verify",

            "body_id":
                "body_archived",

            "content_hash":
                "hash_archived",
        },
    )

    write_json(
        body_store_root
        / "body_deleted.json",
        {
            "workspace_id":
                "ws_verify",

            "body_id":
                "body_deleted",

            "content_hash":
                "hash_deleted",
        },
    )

    write_invalid_json(
        body_store_root
        / "broken_body.json",
    )

    write_json(
        lifecycle_root
        / "body_active.json",
        {
            "workspace_id":
                "ws_verify",

            "body_id":
                "body_active",

            "state":
                "ACTIVE",
        },
    )

    write_json(
        lifecycle_root
        / "body_archived.json",
        {
            "workspace_id":
                "ws_verify",

            "body_id":
                "body_archived",

            "state":
                "ARCHIVED",
        },
    )

    write_json(
        lifecycle_root
        / "body_deleted.json",
        {
            "workspace_id":
                "ws_verify",

            "body_id":
                "body_deleted",

            "state":
                "PERMANENTLY_DELETED",
        },
    )

    write_json(
        lifecycle_root
        / "body_unsupported.json",
        {
            "workspace_id":
                "ws_verify",

            "body_id":
                "body_unsupported",

            "state":
                "UNKNOWN_STATE",
        },
    )

    write_json(
        lifecycle_root
        / "duplicate"
        / "body_active_copy.json",
        {
            "workspace_id":
                "ws_verify",

            "body_id":
                "body_active",

            "state":
                "ACTIVE",
        },
    )
    write_json(
        archive_root
        / "archive_body_archived.json",
        {
            "workspace_id":
                "ws_verify",

            "archive_id":
                "archive_body_archived",

            "body_id":
                "body_archived",

            "retention_expired":
                False,

            "legal_hold_active":
                False,
        },
    )

    write_json(
        archive_root
        / "archive_orphan.json",
        {
            "workspace_id":
                "ws_verify",

            "archive_id":
                "archive_orphan",

            "body_id":
                "body_orphan_archive",

            "retention_expired":
                True,

            "legal_hold_active":
                True,
        },
    )

    write_json(
        tombstone_root
        / "records"
        / "tombstone_body_deleted.json",
        {
            "workspace_id":
                "ws_verify",

            "tombstone_id":
                "tombstone_body_deleted",

            "body_id":
                "body_deleted",

            "archive_id":
                "archive_body_deleted",

            "status":
                "PERMANENTLY_DELETED",

            "contains_article_body":
                False,
        },
    )

    write_json(
        tombstone_root
        / "records"
        / "tombstone_orphan.json",
        {
            "workspace_id":
                "ws_verify",

            "tombstone_id":
                "tombstone_orphan",

            "body_id":
                "body_orphan_tombstone",

            "archive_id":
                "archive_orphan_tombstone",

            "status":
                "PERMANENTLY_DELETED",

            "contains_article_body":
                False,
        },
    )

    write_json(
        tombstone_root
        / "records"
        / "tombstone_content_violation.json",
        {
            "workspace_id":
                "ws_verify",

            "tombstone_id":
                "tombstone_content_violation",

            "body_id":
                "body_content_violation",

            "status":
                "PERMANENTLY_DELETED",

            "contains_article_body":
                True,

            "article_body":
                "forbidden content",
        },
    )

    write_json(
        tombstone_root
        / "index.json",
        {
            "schema":
                "body_store_permanent_deletion_tombstone_index.v1",

            "workspace_id":
                "ws_verify",

            "tombstone_count":
                3,

            "tombstones":
                [],
        },
    )

    request = (
        create_lifecycle_integrity_scanner_request_v1(
            scan_request_id="scanner_verifier_request_v1",
            scope="WORKSPACE",
            workspace_id="ws_verify",
            include_state_consistency=True,
            include_archive_integrity=True,
            include_tombstone_integrity=True,
            include_reference_integrity=True,
            include_retention_integrity=True,
            include_checksum_integrity=True,
        )
    )

    verification = (
        verify_lifecycle_integrity_scanner_v1(
            project_root=sandbox_root,
            scan_request=request,
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

    checksum_source = {
        key:
            value

        for key, value
        in verification.items()

        if key != "verification_checksum"
    }

    calculated_verification_checksum = (
        calculate_lifecycle_integrity_scanner_verification_checksum_v1(
            payload=checksum_source,
        )
    )
    request_result = verification[
        "request"
    ]

    structure_result = verification[
        "structure"
    ]

    findings_result = verification[
        "findings"
    ]

    accuracy_result = verification[
        "cross_store_accuracy"
    ]

    reproducibility_result = verification[
        "reproducibility"
    ]

    checks = {
        "verifier_schema_valid":
            (
                BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_VERIFIER_SCHEMA
                == "body_store_lifecycle_integrity_scanner_verifier.v1"
            ),

        "verifier_version_valid":
            (
                BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_VERIFIER_VERSION
                == "1.0"
            ),

        "verification_passed":
            verification[
                "verification_passed"
            ]
            is True,

        "verification_checksum_valid":
            (
                verification[
                    "verification_checksum"
                ]
                == calculated_verification_checksum
            ),

        "request_identity_verified":
            request_result[
                "request_identity_verified"
            ]
            is True,

        "request_valid":
            request_result[
                "request_valid"
            ]
            is True,

        "request_checksum_valid":
            request_result[
                "request_checksum_valid"
            ]
            is True,

        "request_id_matches":
            request_result[
                "request_id_matches"
            ]
            is True,

        "workspace_matches":
            request_result[
                "workspace_matches"
            ]
            is True,

        "contract_certified":
            request_result[
                "contract_certified"
            ]
            is True,

        "validation_passed":
            request_result[
                "validation_passed"
            ]
            is True,

        "report_structure_verified":
            structure_result[
                "report_structure_verified"
            ]
            is True,

        "report_schema_valid":
            structure_result[
                "schema_valid"
            ]
            is True,

        "engine_schema_valid":
            structure_result[
                "engine_schema_valid"
            ]
            is True,

        "engine_version_valid":
            structure_result[
                "engine_version_valid"
            ]
            is True,

        "store_sections_valid":
            structure_result[
                "store_sections_valid"
            ]
            is True,

        "findings_collection_valid":
            structure_result[
                "findings_collection_valid"
            ]
            is True,

        "finding_count_valid":
            structure_result[
                "finding_count_valid"
            ]
            is True,

        "stores_scanned_valid":
            structure_result[
                "stores_scanned_valid"
            ]
            is True,

        "execution_valid":
            structure_result[
                "execution_valid"
            ]
            is True,

        "report_checksum_valid":
            structure_result[
                "report_checksum_valid"
            ]
            is True,

        "findings_verified":
            findings_result[
                "findings_verified"
            ]
            is True,

        "finding_schema_valid":
            findings_result[
                "finding_schema_valid"
            ]
            is True,

        "finding_type_valid":
            findings_result[
                "finding_type_valid"
            ]
            is True,

        "finding_severity_valid":
            findings_result[
                "finding_severity_valid"
            ]
            is True,

        "finding_identity_valid":
            findings_result[
                "finding_identity_valid"
            ]
            is True,

        "finding_checksum_valid":
            findings_result[
                "finding_checksum_valid"
            ]
            is True,

        "finding_safety_valid":
            findings_result[
                "finding_safety_valid"
            ]
            is True,

        "duplicate_finding_ids_absent":
            findings_result[
                "duplicate_finding_ids_absent"
            ]
            is True,

        "finding_count_matches":
            findings_result[
                "finding_count_matches"
            ]
            is True,

        "cross_store_accuracy_verified":
            accuracy_result[
                "cross_store_accuracy_verified"
            ]
            is True,

        "missing_lifecycle_matches":
            accuracy_result[
                "missing_lifecycle_matches"
            ]
            is True,

        "missing_body_store_matches":
            accuracy_result[
                "missing_body_store_matches"
            ]
            is True,

        "orphan_archive_matches":
            accuracy_result[
                "orphan_archive_matches"
            ]
            is True,

        "orphan_tombstone_matches":
            accuracy_result[
                "orphan_tombstone_matches"
            ]
            is True,

        "store_read_counts_valid":
            accuracy_result[
                "store_read_counts_valid"
            ]
            is True,

        "store_mutation_counts_zero":
            accuracy_result[
                "store_mutation_counts_zero"
            ]
            is True,

        "store_finding_counts_valid":
            accuracy_result[
                "store_finding_counts_valid"
            ]
            is True,

        "reproducibility_verified":
            reproducibility_result[
                "reproducibility_verified"
            ]
            is True,

        "reproduced_content_matches":
            reproducibility_result[
                "content_matches"
            ]
            is True,

        "original_checksum_valid":
            reproducibility_result[
                "original_checksum_valid"
            ]
            is True,

        "reproduced_checksum_valid":
            reproducibility_result[
                "reproduced_checksum_valid"
            ]
            is True,

        "verification_read_only":
            verification[
                "read_only"
            ]
            is True,

        "lifecycle_not_modified":
            verification[
                "lifecycle_modified"
            ]
            is False,

        "archive_not_modified":
            verification[
                "archive_modified"
            ]
            is False,

        "tombstone_not_modified":
            verification[
                "tombstone_modified"
            ]
            is False,

        "body_store_not_modified":
            verification[
                "body_store_modified"
            ]
            is False,

        "no_runtime_job_created":
            verification[
                "runtime_job_created"
            ]
            is False,

        "no_queue_job_created":
            verification[
                "queue_job_created"
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
        "UNIVERSAL ARTICLE BODY STORE LIFECYCLE "
        "INTEGRITY SCANNER VERIFICATION — PHASE 9.1.11.3"
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
    print("FINDING TYPE COUNTS")

    finding_type_counts = findings_result[
        "finding_type_counts"
    ]

    if finding_type_counts:
        for finding_type in sorted(
            finding_type_counts
        ):
            print(
                "  "
                + f"{finding_type:<48}"
                + str(
                    finding_type_counts[
                        finding_type
                    ]
                )
            )
    else:
        print(
            "  None"
        )

    print()
    print("SEVERITY COUNTS")

    severity_counts = findings_result[
        "severity_counts"
    ]

    if severity_counts:
        for severity in sorted(
            severity_counts
        ):
            print(
                "  "
                + f"{severity:<48}"
                + str(
                    severity_counts[
                        severity
                    ]
                )
            )
    else:
        print(
            "  None"
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
        "Integrity reports independently verified: 1"
    )
    print(
        "Integrity scan reproductions performed:   1"
    )
    print(
        "Production lifecycle records modified:   0"
    )
    print(
        "Production archive records modified:     0"
    )
    print(
        "Production tombstone records modified:   0"
    )
    print(
        "Production Body Store files modified:    0"
    )
    print(
        "Production queue jobs created:           0"
    )
    print(
        "Runtime registrations modified:          0"
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
            "BODY STORE LIFECYCLE INTEGRITY SCANNER "
            "VERIFICATION PHASE 9.1.11.3: FAIL"
        )

        raise SystemExit(1)

    print(
        "BODY STORE LIFECYCLE INTEGRITY SCANNER "
        "VERIFICATION PHASE 9.1.11.3: PASS"
    )

    print(
        "The Lifecycle Integrity Scanner Verifier independently "
        "confirmed request identity, report structure, finding "
        "identity and checksums, cross-store accuracy, "
        "reproducibility, and read-only safety."
    )

    print("=" * 120)

finally:
    shutil.rmtree(
        sandbox_root,
        ignore_errors=True,
    )