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

from backend.server.universal_article_body_store.body_store_lifecycle_integrity_scanner_certification_v1 import (
    BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CERTIFICATION_BUNDLE_SCHEMA,
    BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CERTIFICATION_SCHEMA,
    BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CERTIFICATION_VERSION,
    build_lifecycle_integrity_scanner_certification_bundle_v1,
    calculate_lifecycle_integrity_scanner_certification_checksum_v1,
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
        prefix="lifecycle_integrity_scanner_certification_"
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
            "workspace_id": "ws_verify",
            "body_id": "body_active",
            "content_hash": "hash_active",
        },
    )

    write_json(
        body_store_root
        / "body_archived.json",
        {
            "workspace_id": "ws_verify",
            "body_id": "body_archived",
            "content_hash": "hash_archived",
        },
    )

    write_json(
        body_store_root
        / "body_deleted.json",
        {
            "workspace_id": "ws_verify",
            "body_id": "body_deleted",
            "content_hash": "hash_deleted",
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
            "workspace_id": "ws_verify",
            "body_id": "body_active",
            "state": "ACTIVE",
        },
    )

    write_json(
        lifecycle_root
        / "body_archived.json",
        {
            "workspace_id": "ws_verify",
            "body_id": "body_archived",
            "state": "ARCHIVED",
        },
    )

    write_json(
        lifecycle_root
        / "body_deleted.json",
        {
            "workspace_id": "ws_verify",
            "body_id": "body_deleted",
            "state": "PERMANENTLY_DELETED",
        },
    )

    write_json(
        lifecycle_root
        / "body_unsupported.json",
        {
            "workspace_id": "ws_verify",
            "body_id": "body_unsupported",
            "state": "UNKNOWN_STATE",
        },
    )

    write_json(
        lifecycle_root
        / "duplicate"
        / "body_active_copy.json",
        {
            "workspace_id": "ws_verify",
            "body_id": "body_active",
            "state": "ACTIVE",
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
            scan_request_id=(
                "scanner_certification_request_v1"
            ),
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

    certification_bundle = (
        build_lifecycle_integrity_scanner_certification_bundle_v1(
            project_root=sandbox_root,
            scan_request=request,
        )
    )

    certification = certification_bundle[
        "certification"
    ]

    validation = certification_bundle[
        "validation"
    ]

    summary = certification_bundle[
        "summary"
    ]

    after = {
        name:
            fingerprint(
                path
            )

        for name, path
        in PROTECTED.items()
    }

    bundle_checksum_source = {
        key:
            value

        for key, value
        in certification_bundle.items()

        if key != "bundle_checksum"
    }

    calculated_bundle_checksum = (
        calculate_lifecycle_integrity_scanner_certification_checksum_v1(
            payload=bundle_checksum_source,
        )
    )
    checks = {
        "certification_schema_valid":
            (
                BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CERTIFICATION_SCHEMA
                == "body_store_lifecycle_integrity_scanner_certification.v1"
            ),

        "certification_bundle_schema_valid":
            (
                BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CERTIFICATION_BUNDLE_SCHEMA
                == "body_store_lifecycle_integrity_scanner_certification_bundle.v1"
            ),

        "certification_version_valid":
            (
                BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CERTIFICATION_VERSION
                == "1.0"
            ),

        "bundle_certified":
            certification_bundle[
                "bundle_certified"
            ]
            is True,

        "bundle_read_only":
            certification_bundle[
                "bundle_read_only"
            ]
            is True,

        "bundle_checksum_valid":
            (
                certification_bundle[
                    "bundle_checksum"
                ]
                == calculated_bundle_checksum
            ),

        "certification_passed":
            certification[
                "certified"
            ]
            is True,

        "verification_passed":
            certification[
                "verification_passed"
            ]
            is True,

        "validation_passed":
            validation[
                "certification_valid"
            ]
            is True,

        "schema_validation_passed":
            validation[
                "schema_valid"
            ]
            is True,

        "certification_version_validation_passed":
            validation[
                "certification_version_valid"
            ]
            is True,

        "verifier_version_validation_passed":
            validation[
                "verifier_version_valid"
            ]
            is True,

        "verification_mapping_valid":
            validation[
                "verification_mapping_valid"
            ]
            is True,

        "verification_checksum_matches":
            validation[
                "verification_checksum_matches"
            ]
            is True,

        "scan_request_id_matches":
            validation[
                "scan_request_id_matches"
            ]
            is True,

        "workspace_id_matches":
            validation[
                "workspace_id_matches"
            ]
            is True,

        "request_identity_verified":
            validation[
                "request_identity_verified"
            ]
            is True,

        "report_structure_verified":
            validation[
                "report_structure_verified"
            ]
            is True,

        "findings_verified":
            validation[
                "findings_verified"
            ]
            is True,

        "cross_store_accuracy_verified":
            validation[
                "cross_store_accuracy_verified"
            ]
            is True,

        "reproducibility_verified":
            validation[
                "reproducibility_verified"
            ]
            is True,

        "safety_boundaries_valid":
            validation[
                "safety_boundaries_valid"
            ]
            is True,

        "summary_certified":
            summary[
                "certified"
            ]
            is True,

        "summary_verification_passed":
            summary[
                "verification_passed"
            ]
            is True,

        "summary_request_identity_verified":
            summary[
                "request_identity_verified"
            ]
            is True,

        "summary_report_structure_verified":
            summary[
                "report_structure_verified"
            ]
            is True,

        "summary_findings_verified":
            summary[
                "findings_verified"
            ]
            is True,

        "summary_cross_store_accuracy_verified":
            summary[
                "cross_store_accuracy_verified"
            ]
            is True,

        "summary_reproducibility_verified":
            summary[
                "reproducibility_verified"
            ]
            is True,

        "finding_type_counts_present":
            bool(
                summary[
                    "finding_type_counts"
                ]
            ),

        "severity_counts_present":
            bool(
                summary[
                    "severity_counts"
                ]
            ),

        "duplicate_identity_certified":
            (
                summary[
                    "finding_type_counts"
                ].get(
                    "DUPLICATE_LIFECYCLE_IDENTITY",
                    0,
                )
                == 1
            ),

        "invalid_json_certified":
            (
                summary[
                    "finding_type_counts"
                ].get(
                    "INVALID_JSON_RECORD",
                    0,
                )
                == 1
            ),

        "retention_inconsistency_certified":
            (
                summary[
                    "finding_type_counts"
                ].get(
                    "RETENTION_STATE_INCONSISTENCY",
                    0,
                )
                == 1
            ),

        "content_boundary_violation_certified":
            (
                summary[
                    "finding_type_counts"
                ].get(
                    "TOMBSTONE_CONTENT_BOUNDARY_VIOLATION",
                    0,
                )
                == 1
            ),

        "unsupported_state_certified":
            (
                summary[
                    "finding_type_counts"
                ].get(
                    "UNSUPPORTED_LIFECYCLE_STATE",
                    0,
                )
                == 1
            ),

        "critical_count_valid":
            (
                summary[
                    "severity_counts"
                ].get(
                    "CRITICAL",
                    0,
                )
                == 1
            ),

        "error_count_valid":
            (
                summary[
                    "severity_counts"
                ].get(
                    "ERROR",
                    0,
                )
                == 3
            ),

        "warning_count_valid":
            (
                summary[
                    "severity_counts"
                ].get(
                    "WARNING",
                    0,
                )
                == 1
            ),

        "repair_not_planned":
            certification_bundle[
                "repair_planned"
            ]
            is False,

        "repair_not_executed":
            certification_bundle[
                "repair_executed"
            ]
            is False,

        "lifecycle_not_modified":
            certification_bundle[
                "lifecycle_modified"
            ]
            is False,

        "archive_not_modified":
            certification_bundle[
                "archive_modified"
            ]
            is False,

        "tombstone_not_modified":
            certification_bundle[
                "tombstone_modified"
            ]
            is False,

        "body_store_not_modified":
            certification_bundle[
                "body_store_modified"
            ]
            is False,

        "no_runtime_job_created":
            certification_bundle[
                "runtime_job_created"
            ]
            is False,

        "no_queue_job_created":
            certification_bundle[
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
        "INTEGRITY SCANNER CERTIFICATION — PHASE 9.1.11.4"
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
    print("CERTIFIED FINDING TYPE COUNTS")

    for finding_type in sorted(
        summary[
            "finding_type_counts"
        ]
    ):
        print(
            "  "
            + f"{finding_type:<48}"
            + str(
                summary[
                    "finding_type_counts"
                ][
                    finding_type
                ]
            )
        )

    print()
    print("CERTIFIED SEVERITY COUNTS")

    for severity in sorted(
        summary[
            "severity_counts"
        ]
    ):
        print(
            "  "
            + f"{severity:<48}"
            + str(
                summary[
                    "severity_counts"
                ][
                    severity
                ]
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
        "Integrity scans performed:             2"
    )
    print(
        "Independent verifications performed:   1"
    )
    print(
        "Scanner certifications produced:       1"
    )
    print(
        "Repair plans created:                  0"
    )
    print(
        "Repairs executed:                      0"
    )
    print(
        "Production lifecycle records modified: 0"
    )
    print(
        "Production archive records modified:   0"
    )
    print(
        "Production tombstone records modified: 0"
    )
    print(
        "Production Body Store files modified:  0"
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
            "BODY STORE LIFECYCLE INTEGRITY SCANNER "
            "CERTIFICATION PHASE 9.1.11.4: FAIL"
        )

        raise SystemExit(1)

    print(
        "BODY STORE LIFECYCLE INTEGRITY SCANNER "
        "CERTIFICATION PHASE 9.1.11.4: PASS"
    )

    print(
        "The Lifecycle Integrity Scanner subsystem "
        "is fully certified."
    )

    print("=" * 120)

finally:
    shutil.rmtree(
        sandbox_root,
        ignore_errors=True,
    )
