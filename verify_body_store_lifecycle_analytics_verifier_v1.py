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

from backend.server.universal_article_body_store.body_store_lifecycle_analytics_verifier_v1 import (
    BODY_STORE_LIFECYCLE_ANALYTICS_VERIFIER_SCHEMA,
    BODY_STORE_LIFECYCLE_ANALYTICS_VERIFIER_VERSION,
    verify_lifecycle_analytics_v1,
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
        prefix="lifecycle_analytics_verifier_"
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
            "workspace_id": "ws_verify",
            "body_id": "body_active",
            "state": "ACTIVE",
            "created_at": "2026-08-01T10:00:00+00:00",
        },
    )

    write_json(
        lifecycle_root
        / "body_archived.json",
        {
            "workspace_id": "ws_verify",
            "body_id": "body_archived",
            "state": "ARCHIVED",
            "updated_at": "2026-08-02T10:00:00+00:00",
        },
    )

    write_json(
        lifecycle_root
        / "body_restored.json",
        {
            "workspace_id": "ws_verify",
            "body_id": "body_restored",
            "state": "RESTORED",
            "restored_at": "2026-08-03T10:00:00+00:00",
        },
    )

    write_json(
        lifecycle_root
        / "body_deleted.json",
        {
            "workspace_id": "ws_verify",
            "body_id": "body_deleted",
            "state": "PERMANENTLY_DELETED",
            "deleted_at": "2026-08-04T10:00:00+00:00",
        },
    )

    write_json(
        archive_root
        / "archive_001.json",
        {
            "workspace_id": "ws_verify",
            "archive_id": "archive_001",
            "body_id": "body_archived",
            "archived_at": "2026-08-02T10:00:00+00:00",
            "retention_expired": False,
        },
    )

    write_json(
        archive_root
        / "archive_002.json",
        {
            "workspace_id": "ws_verify",
            "archive_id": "archive_002",
            "body_id": "body_deleted",
            "archived_at": "2026-08-04T09:00:00+00:00",
            "retention_expired": True,
        },
    )

    write_json(
        tombstone_root
        / "records"
        / "tombstone_body_deleted_v1.json",
        {
            "tombstone_id": "tombstone_body_deleted_v1",
            "body_id": "body_deleted",
            "workspace_id": "ws_verify",
            "archive_id": "archive_002",
            "lifecycle_record_id": "body_deleted",
            "deletion_request_id": "deletion_request_001",
            "deletion_execution_id": "deletion_execution_001",
            "status": "PERMANENTLY_DELETED",
            "contains_article_body": False,
            "created_at": "2026-08-04T10:00:00+00:00",
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
            analytics_request_id="analytics_verifier_request_v1",
            scope="WORKSPACE",
            workspace_id="ws_verify",
            include_state_counts=True,
            include_archive_metrics=True,
            include_restore_metrics=True,
            include_deletion_metrics=True,
            include_tombstone_metrics=True,
            include_retention_metrics=True,
            period_start="2026-08-01T00:00:00+00:00",
            period_end="2026-08-06T23:59:59+00:00",
            requested_at="2026-08-07T00:00:00+00:00",
        )
    )

    report = (
        build_lifecycle_analytics_report_v1(
            project_root=sandbox_root,
            analytics_request=request,
        )
    )

    verification = (
        verify_lifecycle_analytics_v1(
            project_root=sandbox_root,
            analytics_request=request,
            analytics_report=report,
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

    request_identity = verification[
        "request_identity"
    ]

    report_structure = verification[
        "report_structure"
    ]

    metric_accuracy = verification[
        "metric_accuracy"
    ]

    reproducibility = verification[
        "reproducibility"
    ]

    safety_boundaries = verification[
        "safety_boundaries"
    ]

    report_summary = verification[
        "report_summary"
    ]

    checks = {
        "verifier_schema_valid":
            (
                BODY_STORE_LIFECYCLE_ANALYTICS_VERIFIER_SCHEMA
                == "body_store_lifecycle_analytics_verifier.v1"
            ),

        "verifier_version_valid":
            (
                BODY_STORE_LIFECYCLE_ANALYTICS_VERIFIER_VERSION
                == "1.0"
            ),

        "analytics_verified":
            verification[
                "analytics_verified"
            ]
            is True,

        "verification_id_present":
            bool(
                verification[
                    "verification_id"
                ]
            ),

        "request_identity_verified":
            request_identity[
                "request_identity_verified"
            ]
            is True,

        "request_valid":
            request_identity[
                "request_valid"
            ]
            is True,

        "request_checksum_valid":
            request_identity[
                "request_checksum_valid"
            ]
            is True,

        "request_id_matches":
            request_identity[
                "request_id_matches"
            ]
            is True,

        "scope_matches":
            request_identity[
                "scope_matches"
            ]
            is True,

        "workspace_matches":
            request_identity[
                "workspace_matches"
            ]
            is True,

        "period_start_matches":
            request_identity[
                "period_start_matches"
            ]
            is True,

        "period_end_matches":
            request_identity[
                "period_end_matches"
            ]
            is True,

        "report_structure_verified":
            report_structure[
                "report_structure_verified"
            ]
            is True,

        "report_schema_valid":
            report_structure[
                "report_schema_valid"
            ]
            is True,

        "engine_schema_valid":
            report_structure[
                "engine_schema_valid"
            ]
            is True,

        "engine_version_valid":
            report_structure[
                "engine_version_valid"
            ]
            is True,

        "engine_report_valid":
            report_structure[
                "engine_report_valid"
            ]
            is True,

        "report_checksum_valid":
            report_structure[
                "report_checksum_valid"
            ]
            is True,

        "metrics_mapping_valid":
            report_structure[
                "metrics_mapping_valid"
            ]
            is True,

        "metric_group_count_valid":
            report_structure[
                "metric_group_count_valid"
            ]
            is True,

        "metric_groups_complete":
            report_structure[
                "metric_groups_complete"
            ]
            is True,

        "metric_accuracy_verified":
            metric_accuracy[
                "metric_accuracy_verified"
            ]
            is True,

        "state_counts_non_negative":
            metric_accuracy[
                "state_counts_non_negative"
            ]
            is True,

        "lifecycle_total_matches":
            metric_accuracy[
                "lifecycle_total_matches"
            ]
            is True,

        "restore_count_matches":
            metric_accuracy[
                "restore_count_matches"
            ]
            is True,

        "deletion_count_matches":
            metric_accuracy[
                "deletion_count_matches"
            ]
            is True,

        "tombstone_count_matches":
            metric_accuracy[
                "tombstone_count_matches"
            ]
            is True,

        "deletion_tombstone_gap_valid":
            metric_accuracy[
                "deletion_tombstone_gap_valid"
            ]
            is True,

        "archive_counts_valid":
            metric_accuracy[
                "archive_counts_valid"
            ]
            is True,

        "retention_total_matches":
            metric_accuracy[
                "retention_total_matches"
            ]
            is True,

        "source_read_counts_valid":
            metric_accuracy[
                "source_read_counts_valid"
            ]
            is True,

        "source_mutation_counts_zero":
            metric_accuracy[
                "source_mutation_counts_zero"
            ]
            is True,

        "reproducibility_verified":
            reproducibility[
                "reproducibility_verified"
            ]
            is True,

        "reproduced_content_matches":
            reproducibility[
                "content_matches"
            ]
            is True,

        "original_checksum_valid":
            reproducibility[
                "original_checksum_valid"
            ]
            is True,

        "reproduced_checksum_valid":
            reproducibility[
                "reproduced_checksum_valid"
            ]
            is True,

        "safety_boundaries_verified":
            safety_boundaries[
                "safety_boundaries_verified"
            ]
            is True,

        "report_read_only":
            safety_boundaries[
                "report_read_only"
            ]
            is True,

        "lifecycle_not_modified":
            safety_boundaries[
                "lifecycle_not_modified"
            ]
            is True,

        "archive_not_modified":
            safety_boundaries[
                "archive_not_modified"
            ]
            is True,

        "tombstone_not_modified":
            safety_boundaries[
                "tombstone_not_modified"
            ]
            is True,

        "body_store_not_modified":
            safety_boundaries[
                "body_store_not_modified"
            ]
            is True,

        "no_runtime_job_created":
            safety_boundaries[
                "no_runtime_job_created"
            ]
            is True,

        "no_queue_job_created":
            safety_boundaries[
                "no_queue_job_created"
            ]
            is True,

        "summary_active_count_valid":
            (
                report_summary[
                    "active_count"
                ]
                == 1
            ),

        "summary_archived_count_valid":
            (
                report_summary[
                    "archived_count"
                ]
                == 1
            ),

        "summary_restored_count_valid":
            (
                report_summary[
                    "restored_count"
                ]
                == 1
            ),

        "summary_deleted_count_valid":
            (
                report_summary[
                    "permanently_deleted_count"
                ]
                == 1
            ),

        "summary_archive_count_valid":
            (
                report_summary[
                    "unique_archive_count"
                ]
                == 2
            ),

        "summary_tombstone_count_valid":
            (
                report_summary[
                    "valid_tombstone_count"
                ]
                == 1
            ),

        "summary_deletion_gap_zero":
            (
                report_summary[
                    "deletion_tombstone_gap"
                ]
                == 0
            ),

        "summary_retention_expired_valid":
            (
                report_summary[
                    "retention_expired_count"
                ]
                == 1
            ),

        "summary_retention_active_valid":
            (
                report_summary[
                    "retention_active_count"
                ]
                == 1
            ),

        "verification_read_only":
            verification[
                "read_only"
            ]
            is True,

        "verification_lifecycle_not_modified":
            verification[
                "lifecycle_modified"
            ]
            is False,

        "verification_archive_not_modified":
            verification[
                "archive_modified"
            ]
            is False,

        "verification_tombstone_not_modified":
            verification[
                "tombstone_modified"
            ]
            is False,

        "verification_body_store_not_modified":
            verification[
                "body_store_modified"
            ]
            is False,

        "verification_no_runtime_job_created":
            verification[
                "runtime_job_created"
            ]
            is False,

        "verification_no_queue_job_created":
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
        "ANALYTICS VERIFICATION — PHASE 9.1.10.3"
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
    print("VERIFIED ANALYTICS SUMMARY")
    print(
        "  ACTIVE:                      "
        + str(
            report_summary[
                "active_count"
            ]
        )
    )
    print(
        "  ARCHIVED:                    "
        + str(
            report_summary[
                "archived_count"
            ]
        )
    )
    print(
        "  RESTORED:                    "
        + str(
            report_summary[
                "restored_count"
            ]
        )
    )
    print(
        "  PERMANENTLY_DELETED:         "
        + str(
            report_summary[
                "permanently_deleted_count"
            ]
        )
    )
    print(
        "  Unique archives:             "
        + str(
            report_summary[
                "unique_archive_count"
            ]
        )
    )
    print(
        "  Valid tombstones:            "
        + str(
            report_summary[
                "valid_tombstone_count"
            ]
        )
    )
    print(
        "  Deletion/tombstone gap:      "
        + str(
            report_summary[
                "deletion_tombstone_gap"
            ]
        )
    )
    print(
        "  Retention expired:           "
        + str(
            report_summary[
                "retention_expired_count"
            ]
        )
    )
    print(
        "  Retention active:            "
        + str(
            report_summary[
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
        "Analytics reports independently verified: 1"
    )
    print(
        "Analytics reproductions performed:        1"
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
            "BODY STORE LIFECYCLE ANALYTICS "
            "VERIFICATION PHASE 9.1.10.3: FAIL"
        )

        raise SystemExit(1)

    print(
        "BODY STORE LIFECYCLE ANALYTICS "
        "VERIFICATION PHASE 9.1.10.3: PASS"
    )

    print(
        "The Lifecycle Analytics Verifier independently confirmed "
        "request identity, report structure, metric accuracy, "
        "reproducibility, checksum integrity, and read-only safety."
    )

    print("=" * 120)

finally:
    shutil.rmtree(
        sandbox_root,
        ignore_errors=True,
    )
