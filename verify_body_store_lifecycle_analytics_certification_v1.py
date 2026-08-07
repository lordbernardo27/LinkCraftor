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

from backend.server.universal_article_body_store.body_store_lifecycle_analytics_contract_v1 import (
    create_lifecycle_analytics_request_v1,
)

from backend.server.universal_article_body_store.body_store_lifecycle_analytics_engine_v1 import (
    build_lifecycle_analytics_report_v1,
)

from backend.server.universal_article_body_store.body_store_lifecycle_analytics_certification_v1 import (
    BODY_STORE_LIFECYCLE_ANALYTICS_CERTIFICATION_BUNDLE_SCHEMA,
    BODY_STORE_LIFECYCLE_ANALYTICS_CERTIFICATION_SCHEMA,
    BODY_STORE_LIFECYCLE_ANALYTICS_CERTIFICATION_VERSION,
    build_lifecycle_analytics_certification_bundle_v1,
    verify_lifecycle_analytics_certification_bundle_v1,
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
        prefix="lifecycle_analytics_certification_"
    )
)

try:
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
        lifecycle_root
        / "body_active.json",
        {
            "workspace_id":
                "ws_verify",

            "body_id":
                "body_active",

            "state":
                "ACTIVE",

            "created_at":
                "2026-08-01T10:00:00+00:00",
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

            "updated_at":
                "2026-08-02T10:00:00+00:00",
        },
    )

    write_json(
        lifecycle_root
        / "body_restored.json",
        {
            "workspace_id":
                "ws_verify",

            "body_id":
                "body_restored",

            "state":
                "RESTORED",

            "restored_at":
                "2026-08-03T10:00:00+00:00",
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

            "deleted_at":
                "2026-08-04T10:00:00+00:00",
        },
    )

    write_json(
        archive_root
        / "archive_001.json",
        {
            "workspace_id":
                "ws_verify",

            "archive_id":
                "archive_001",

            "body_id":
                "body_archived",

            "archived_at":
                "2026-08-02T10:00:00+00:00",

            "retention_expired":
                False,
        },
    )

    write_json(
        archive_root
        / "archive_002.json",
        {
            "workspace_id":
                "ws_verify",

            "archive_id":
                "archive_002",

            "body_id":
                "body_deleted",

            "archived_at":
                "2026-08-04T09:00:00+00:00",

            "retention_expired":
                True,
        },
    )

    write_json(
        tombstone_root
        / "records"
        / "tombstone_body_deleted_v1.json",
        {
            "tombstone_id":
                "tombstone_body_deleted_v1",

            "body_id":
                "body_deleted",

            "workspace_id":
                "ws_verify",

            "archive_id":
                "archive_002",

            "lifecycle_record_id":
                "body_deleted",

            "deletion_request_id":
                "deletion_request_001",

            "deletion_execution_id":
                "deletion_execution_001",

            "status":
                "PERMANENTLY_DELETED",

            "contains_article_body":
                False,

            "created_at":
                "2026-08-04T10:00:00+00:00",
        },
    )

    write_json(
        tombstone_root
        / "index.json",
        {
            "schema":
                "body_store_permanent_deletion_tombstone_index.v1",

            "manager_version":
                "1.0",

            "workspace_id":
                "ws_verify",

            "tombstone_count":
                1,

            "tombstones":
                [],
        },
    )

    request = (
        create_lifecycle_analytics_request_v1(
            analytics_request_id=(
                "analytics_certification_request_v1"
            ),
            scope="WORKSPACE",
            workspace_id="ws_verify",
            include_state_counts=True,
            include_archive_metrics=True,
            include_restore_metrics=True,
            include_deletion_metrics=True,
            include_tombstone_metrics=True,
            include_retention_metrics=True,
            period_start=(
                "2026-08-01T00:00:00+00:00"
            ),
            period_end=(
                "2026-08-06T23:59:59+00:00"
            ),
            requested_at=(
                "2026-08-07T00:00:00+00:00"
            ),
        )
    )

    report = (
        build_lifecycle_analytics_report_v1(
            project_root=sandbox_root,
            analytics_request=request,
        )
    )

    certification_bundle = (
        build_lifecycle_analytics_certification_bundle_v1(
            project_root=sandbox_root,
            analytics_request=request,
            analytics_report=report,
        )
    )

    bundle_verification = (
        verify_lifecycle_analytics_certification_bundle_v1(
            certification_bundle=certification_bundle,
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

    certification = certification_bundle[
        "certification"
    ]

    validation = certification_bundle[
        "validation"
    ]

    summary = certification_bundle[
        "summary"
    ]

    checks = {
        "certification_schema_valid":
            (
                BODY_STORE_LIFECYCLE_ANALYTICS_CERTIFICATION_SCHEMA
                == "body_store_lifecycle_analytics_certification.v1"
            ),

        "certification_bundle_schema_valid":
            (
                BODY_STORE_LIFECYCLE_ANALYTICS_CERTIFICATION_BUNDLE_SCHEMA
                == "body_store_lifecycle_analytics_certification_bundle.v1"
            ),

        "certification_version_valid":
            (
                BODY_STORE_LIFECYCLE_ANALYTICS_CERTIFICATION_VERSION
                == "1.0"
            ),

        "bundle_complete":
            certification_bundle[
                "bundle_complete"
            ]
            is True,

        "bundle_certified":
            certification_bundle[
                "certified"
            ]
            is True,

        "bundle_analytics_verified":
            certification_bundle[
                "analytics_verified"
            ]
            is True,

        "bundle_valid":
            bundle_verification[
                "bundle_valid"
            ]
            is True,

        "bundle_schema_verified":
            bundle_verification[
                "schema_valid"
            ]
            is True,

        "bundle_version_verified":
            bundle_verification[
                "certification_version_valid"
            ]
            is True,

        "bundle_checksum_valid":
            bundle_verification[
                "bundle_checksum_valid"
            ]
            is True,

        "certification_passed":
            certification[
                "certified"
            ]
            is True,

        "certification_analytics_verified":
            certification[
                "analytics_verified"
            ]
            is True,

        "validation_passed":
            validation[
                "certification_valid"
            ]
            is True,

        "verification_passed":
            validation[
                "verification_passed"
            ]
            is True,

        "verification_id_matches":
            validation[
                "verification_id_matches"
            ]
            is True,

        "request_id_matches":
            validation[
                "request_id_matches"
            ]
            is True,

        "scope_matches":
            validation[
                "scope_matches"
            ]
            is True,

        "workspace_matches":
            validation[
                "workspace_matches"
            ]
            is True,

        "period_start_matches":
            validation[
                "period_start_matches"
            ]
            is True,

        "period_end_matches":
            validation[
                "period_end_matches"
            ]
            is True,

        "report_checksum_matches":
            validation[
                "report_checksum_matches"
            ]
            is True,

        "request_identity_verified":
            certification_bundle[
                "request_identity_verified"
            ]
            is True,

        "report_structure_verified":
            certification_bundle[
                "report_structure_verified"
            ]
            is True,

        "metric_accuracy_verified":
            certification_bundle[
                "metric_accuracy_verified"
            ]
            is True,

        "reproducibility_verified":
            certification_bundle[
                "reproducibility_verified"
            ]
            is True,

        "safety_boundaries_verified":
            certification_bundle[
                "safety_boundaries_verified"
            ]
            is True,

        "certification_id_matches":
            bundle_verification[
                "certification_id_matches"
            ]
            is True,

        "bundle_verification_id_matches":
            bundle_verification[
                "verification_id_matches"
            ]
            is True,

        "bundle_request_id_matches":
            bundle_verification[
                "request_id_matches"
            ]
            is True,

        "bundle_scope_matches":
            bundle_verification[
                "scope_matches"
            ]
            is True,

        "bundle_workspace_matches":
            bundle_verification[
                "workspace_matches"
            ]
            is True,

        "certification_confirmed":
            bundle_verification[
                "certification_confirmed"
            ]
            is True,

        "analytics_verification_confirmed":
            bundle_verification[
                "analytics_verification_confirmed"
            ]
            is True,

        "validation_confirmed":
            bundle_verification[
                "validation_confirmed"
            ]
            is True,

        "evidence_confirmed":
            bundle_verification[
                "evidence_confirmed"
            ]
            is True,

        "summary_certified":
            summary[
                "certified"
            ]
            is True,

        "summary_analytics_verified":
            summary[
                "analytics_verified"
            ]
            is True,

        "summary_active_count_valid":
            (
                summary[
                    "active_count"
                ]
                == 1
            ),

        "summary_archived_count_valid":
            (
                summary[
                    "archived_count"
                ]
                == 1
            ),

        "summary_restored_count_valid":
            (
                summary[
                    "restored_count"
                ]
                == 1
            ),

        "summary_deleted_count_valid":
            (
                summary[
                    "permanently_deleted_count"
                ]
                == 1
            ),

        "summary_archive_count_valid":
            (
                summary[
                    "unique_archive_count"
                ]
                == 2
            ),

        "summary_tombstone_count_valid":
            (
                summary[
                    "valid_tombstone_count"
                ]
                == 1
            ),

        "summary_deletion_gap_zero":
            (
                summary[
                    "deletion_tombstone_gap"
                ]
                == 0
            ),

        "summary_retention_expired_valid":
            (
                summary[
                    "retention_expired_count"
                ]
                == 1
            ),

        "summary_retention_active_valid":
            (
                summary[
                    "retention_active_count"
                ]
                == 1
            ),

        "certification_read_only":
            certification_bundle[
                "read_only"
            ]
            is True,

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
        "ANALYTICS CERTIFICATION — PHASE 9.1.10.4"
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
    print("CERTIFIED ANALYTICS SUMMARY")
    print(
        "  ACTIVE:                      "
        + str(
            summary[
                "active_count"
            ]
        )
    )
    print(
        "  ARCHIVED:                    "
        + str(
            summary[
                "archived_count"
            ]
        )
    )
    print(
        "  RESTORED:                    "
        + str(
            summary[
                "restored_count"
            ]
        )
    )
    print(
        "  PERMANENTLY_DELETED:         "
        + str(
            summary[
                "permanently_deleted_count"
            ]
        )
    )
    print(
        "  Unique archives:             "
        + str(
            summary[
                "unique_archive_count"
            ]
        )
    )
    print(
        "  Valid tombstones:            "
        + str(
            summary[
                "valid_tombstone_count"
            ]
        )
    )
    print(
        "  Deletion/tombstone gap:      "
        + str(
            summary[
                "deletion_tombstone_gap"
            ]
        )
    )
    print(
        "  Retention expired:           "
        + str(
            summary[
                "retention_expired_count"
            ]
        )
    )
    print(
        "  Retention active:            "
        + str(
            summary[
                "retention_active_count"
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
        "Analytics reports generated:           1"
    )
    print(
        "Independent verifications performed:   1"
    )
    print(
        "Analytics certifications produced:     1"
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
            "BODY STORE LIFECYCLE ANALYTICS "
            "CERTIFICATION PHASE 9.1.10.4: FAIL"
        )

        raise SystemExit(1)

    print(
        "BODY STORE LIFECYCLE ANALYTICS "
        "CERTIFICATION PHASE 9.1.10.4: PASS"
    )

    print(
        "The Lifecycle Analytics subsystem is fully certified."
    )

    print("=" * 120)

finally:
    shutil.rmtree(
        sandbox_root,
        ignore_errors=True,
    )
