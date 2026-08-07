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
    BODY_STORE_LIFECYCLE_ANALYTICS_ENGINE_SCHEMA,
    BODY_STORE_LIFECYCLE_ANALYTICS_ENGINE_VERSION,
    build_lifecycle_analytics_engine_bundle_v1,
    summarize_lifecycle_analytics_report_v1,
    verify_lifecycle_analytics_engine_bundle_v1,
    verify_lifecycle_analytics_report_v1,
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
        prefix="lifecycle_analytics_engine_verify_"
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
            "schema": "body_store_permanent_deletion_tombstone_index.v1",
            "manager_version": "1.0",
            "workspace_id": "ws_verify",
            "tombstone_count": 1,
            "tombstones": [],
        },
    )

    request = (
        create_lifecycle_analytics_request_v1(
            analytics_request_id="analytics_engine_verify_v1",
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

    engine_bundle = (
        build_lifecycle_analytics_engine_bundle_v1(
            project_root=sandbox_root,
            analytics_request=request,
        )
    )

    bundle_verification = (
        verify_lifecycle_analytics_engine_bundle_v1(
            engine_bundle=engine_bundle,
        )
    )

    report = engine_bundle[
        "analytics_report"
    ]

    report_verification = (
        verify_lifecycle_analytics_report_v1(
            analytics_report=report,
        )
    )

    summary = (
        summarize_lifecycle_analytics_report_v1(
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

    state_counts = report[
        "metrics"
    ][
        "state_counts"
    ]

    archive_metrics = report[
        "metrics"
    ][
        "archive_metrics"
    ]

    restore_metrics = report[
        "metrics"
    ][
        "restore_metrics"
    ]

    deletion_metrics = report[
        "metrics"
    ][
        "deletion_metrics"
    ]

    tombstone_metrics = report[
        "metrics"
    ][
        "tombstone_metrics"
    ]

    retention_metrics = report[
        "metrics"
    ][
        "retention_metrics"
    ]

    checks = {
        "engine_schema_valid":
            (
                BODY_STORE_LIFECYCLE_ANALYTICS_ENGINE_SCHEMA
                == "body_store_lifecycle_analytics_engine.v1"
            ),

        "engine_version_valid":
            (
                BODY_STORE_LIFECYCLE_ANALYTICS_ENGINE_VERSION
                == "1.0"
            ),

        "engine_bundle_complete":
            engine_bundle[
                "bundle_complete"
            ]
            is True,

        "analytics_executed":
            engine_bundle[
                "analytics_executed"
            ]
            is True,

        "report_generated":
            engine_bundle[
                "report_generated"
            ]
            is True,

        "report_verified":
            engine_bundle[
                "report_verified"
            ]
            is True,

        "bundle_valid":
            bundle_verification[
                "bundle_valid"
            ]
            is True,

        "request_id_matches":
            bundle_verification[
                "request_id_matches"
            ]
            is True,

        "scope_matches":
            bundle_verification[
                "scope_matches"
            ]
            is True,

        "workspace_matches":
            bundle_verification[
                "workspace_matches"
            ]
            is True,

        "execution_confirmed":
            bundle_verification[
                "execution_confirmed"
            ]
            is True,

        "verification_confirmed":
            bundle_verification[
                "verification_confirmed"
            ]
            is True,

        "bundle_safety_boundaries_valid":
            bundle_verification[
                "safety_boundaries_valid"
            ]
            is True,

        "report_valid":
            report_verification[
                "report_valid"
            ]
            is True,

        "report_schema_valid":
            report_verification[
                "schema_valid"
            ]
            is True,

        "report_engine_schema_valid":
            report_verification[
                "engine_schema_valid"
            ]
            is True,

        "report_engine_version_valid":
            report_verification[
                "engine_version_valid"
            ]
            is True,

        "report_metrics_valid":
            report_verification[
                "metrics_valid"
            ]
            is True,

        "metric_group_count_valid":
            report_verification[
                "metric_group_count_valid"
            ]
            is True,

        "report_execution_valid":
            report_verification[
                "execution_valid"
            ]
            is True,

        "report_safety_boundaries_valid":
            report_verification[
                "safety_boundaries_valid"
            ]
            is True,

        "report_checksum_valid":
            report_verification[
                "checksum_valid"
            ]
            is True,

        "six_metric_groups_generated":
            (
                report[
                    "metric_group_count"
                ]
                == 6
            ),

        "active_count_valid":
            (
                state_counts[
                    "counts_by_state"
                ][
                    "ACTIVE"
                ]
                == 1
            ),

        "archived_count_valid":
            (
                state_counts[
                    "counts_by_state"
                ][
                    "ARCHIVED"
                ]
                == 1
            ),

        "restored_count_valid":
            (
                state_counts[
                    "counts_by_state"
                ][
                    "RESTORED"
                ]
                == 1
            ),

        "permanently_deleted_count_valid":
            (
                state_counts[
                    "counts_by_state"
                ][
                    "PERMANENTLY_DELETED"
                ]
                == 1
            ),

        "lifecycle_valid_record_count":
            (
                state_counts[
                    "valid_records"
                ]
                == 4
            ),

        "lifecycle_body_count_valid":
            (
                state_counts[
                    "body_count"
                ]
                == 4
            ),

        "archive_record_count_valid":
            (
                archive_metrics[
                    "valid_archive_records"
                ]
                == 2
            ),

        "unique_archive_count_valid":
            (
                archive_metrics[
                    "unique_archive_count"
                ]
                == 2
            ),

        "archive_body_count_valid":
            (
                archive_metrics[
                    "unique_body_count"
                ]
                == 2
            ),

        "restore_event_count_valid":
            (
                restore_metrics[
                    "restore_events_inferred_from_lifecycle"
                ]
                == 1
            ),

        "deletion_count_valid":
            (
                deletion_metrics[
                    "permanently_deleted_count"
                ]
                == 1
            ),

        "certified_tombstone_count_valid":
            (
                deletion_metrics[
                    "certified_tombstone_count"
                ]
                == 1
            ),

        "deletion_tombstone_gap_zero":
            (
                deletion_metrics[
                    "deletion_tombstone_gap"
                ]
                == 0
            ),

        "valid_tombstone_count":
            (
                tombstone_metrics[
                    "valid_tombstones"
                ]
                == 1
            ),

        "tombstone_index_skipped":
            (
                tombstone_metrics[
                    "index_files_skipped"
                ]
                == 1
            ),

        "no_tombstone_content_violations":
            (
                tombstone_metrics[
                    "content_boundary_violations"
                ]
                == 0
            ),

        "retention_records_considered":
            (
                retention_metrics[
                    "records_considered"
                ]
                == 2
            ),

        "retention_expired_count_valid":
            (
                retention_metrics[
                    "retention_expired_count"
                ]
                == 1
            ),

        "retention_active_count_valid":
            (
                retention_metrics[
                    "retention_active_count"
                ]
                == 1
            ),

        "retention_unknown_count_zero":
            (
                retention_metrics[
                    "retention_unknown_count"
                ]
                == 0
            ),

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

        "engine_read_only":
            engine_bundle[
                "read_only"
            ]
            is True,

        "lifecycle_not_modified":
            engine_bundle[
                "lifecycle_modified"
            ]
            is False,

        "archive_not_modified":
            engine_bundle[
                "archive_modified"
            ]
            is False,

        "tombstone_not_modified":
            engine_bundle[
                "tombstone_modified"
            ]
            is False,

        "body_store_not_modified":
            engine_bundle[
                "body_store_modified"
            ]
            is False,

        "no_runtime_job_created":
            engine_bundle[
                "runtime_job_created"
            ]
            is False,

        "no_queue_job_created":
            engine_bundle[
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
        "ANALYTICS ENGINE — PHASE 9.1.10.2"
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
    print("ANALYTICS RESULTS")
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
        "Sandbox lifecycle records read:       4"
    )
    print(
        "Sandbox archive records read:         2"
    )
    print(
        "Sandbox tombstone records analyzed:   1"
    )
    print(
        "Analytics reports generated:          1"
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
            "ENGINE PHASE 9.1.10.2: FAIL"
        )

        raise SystemExit(1)

    print(
        "BODY STORE LIFECYCLE ANALYTICS "
        "ENGINE PHASE 9.1.10.2: PASS"
    )

    print(
        "The Lifecycle Analytics Engine generated and verified "
        "a complete read-only lifecycle report without modifying "
        "production outputs."
    )

    print("=" * 120)

finally:
    shutil.rmtree(
        sandbox_root,
        ignore_errors=True,
    )
