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

from backend.server.universal_article_body_store.body_store_lifecycle_integrity_scanner_engine_v1 import (
    BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_ENGINE_SCHEMA,
    BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_ENGINE_VERSION,
    BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_REPORT_SCHEMA,
    SUPPORTED_FINDING_SEVERITIES,
    SUPPORTED_FINDING_TYPES,
    build_lifecycle_integrity_report_v1,
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
        prefix="lifecycle_integrity_scanner_engine_"
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
            "workspace_id": "ws_verify",
            "archive_id": "archive_body_archived",
            "body_id": "body_archived",
            "retention_expired": False,
            "legal_hold_active": False,
        },
    )

    write_json(
        archive_root
        / "archive_orphan.json",
        {
            "workspace_id": "ws_verify",
            "archive_id": "archive_orphan",
            "body_id": "body_orphan_archive",
            "retention_expired": True,
            "legal_hold_active": True,
        },
    )

    write_json(
        tombstone_root
        / "records"
        / "tombstone_body_deleted.json",
        {
            "workspace_id": "ws_verify",
            "tombstone_id": "tombstone_body_deleted",
            "body_id": "body_deleted",
            "archive_id": "archive_body_deleted",
            "status": "PERMANENTLY_DELETED",
            "contains_article_body": False,
        },
    )

    write_json(
        tombstone_root
        / "records"
        / "tombstone_orphan.json",
        {
            "workspace_id": "ws_verify",
            "tombstone_id": "tombstone_orphan",
            "body_id": "body_orphan_tombstone",
            "archive_id": "archive_orphan_tombstone",
            "status": "PERMANENTLY_DELETED",
            "contains_article_body": False,
        },
    )

    write_json(
        tombstone_root
        / "records"
        / "tombstone_content_violation.json",
        {
            "workspace_id": "ws_verify",
            "tombstone_id": "tombstone_content_violation",
            "body_id": "body_content_violation",
            "status": "PERMANENTLY_DELETED",
            "contains_article_body": True,
            "article_body": "forbidden content",
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
            scan_request_id="scanner_engine_request_v1",
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

    report = (
        build_lifecycle_integrity_report_v1(
            project_root=sandbox_root,
            scan_request=request,
        )
    )
    finding_types = {
        finding["finding_type"]
        for finding in report["findings"]
    }

    severities = {
        finding["severity"]
        for finding in report["findings"]
    }

    checks: list[tuple[str, bool]] = []

    checks.append(
        (
            "engine_schema_valid",
            report["engine_schema"]
            == BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_ENGINE_SCHEMA,
        )
    )

    checks.append(
        (
            "engine_version_valid",
            report["engine_version"]
            == BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_ENGINE_VERSION,
        )
    )

    checks.append(
        (
            "report_schema_valid",
            report["schema"]
            == BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_REPORT_SCHEMA,
        )
    )

    checks.append(
        (
            "scan_executed",
            report["scan_executed"] is True,
        )
    )

    checks.append(
        (
            "contract_certified",
            report["contract_certified"] is True,
        )
    )

    checks.append(
        (
            "validation_passed",
            report["validation_passed"] is True,
        )
    )

    checks.append(
        (
            "stores_scanned",
            report["stores_scanned"] == 4,
        )
    )

    checks.append(
        (
            "report_read_only",
            report["read_only"] is True,
        )
    )

    checks.append(
        (
            "repair_not_planned",
            report["repair_planned"] is False,
        )
    )

    checks.append(
        (
            "repair_not_executed",
            report["repair_executed"] is False,
        )
    )

    checks.append(
        (
            "body_store_not_modified",
            report["body_store_modified"] is False,
        )
    )

    checks.append(
        (
            "lifecycle_not_modified",
            report["lifecycle_modified"] is False,
        )
    )

    checks.append(
        (
            "archive_not_modified",
            report["archive_modified"] is False,
        )
    )

    checks.append(
        (
            "tombstone_not_modified",
            report["tombstone_modified"] is False,
        )
    )

    checks.append(
        (
            "runtime_job_not_created",
            report["runtime_job_created"] is False,
        )
    )

    checks.append(
        (
            "queue_job_not_created",
            report["queue_job_created"] is False,
        )
    )

    checks.append(
        (
            "finding_count_valid",
            report["finding_count"]
            == len(report["findings"]),
        )
    )

    checks.append(
        (
            "supported_finding_types",
            finding_types.issubset(
                set(SUPPORTED_FINDING_TYPES)
            ),
        )
    )

    checks.append(
        (
            "supported_severities",
            severities.issubset(
                set(SUPPORTED_FINDING_SEVERITIES)
            ),
        )
    )

    checks.append(
        (
            "invalid_json_detected",
            "INVALID_JSON_RECORD"
            in finding_types,
        )
    )

    checks.append(
        (
            "unsupported_state_detected",
            "UNSUPPORTED_LIFECYCLE_STATE"
            in finding_types,
        )
    )

    checks.append(
        (
            "duplicate_identity_detected",
            "DUPLICATE_LIFECYCLE_IDENTITY"
            in finding_types,
        )
    )

    checks.append(
        (
            "retention_issue_detected",
            "RETENTION_STATE_INCONSISTENCY"
            in finding_types,
        )
    )

    checks.append(
        (
            "content_boundary_detected",
            "TOMBSTONE_CONTENT_BOUNDARY_VIOLATION"
            in finding_types,
        )
    )

    def json_ready(
        value,
    ):
        if isinstance(
            value,
            dict,
        ) or hasattr(
            value,
            "items",
        ):
            return {
                str(key):
                    json_ready(item)

                for key, item
                in value.items()
            }

        if isinstance(
            value,
            (
                tuple,
                list,
            ),
        ):
            return [
                json_ready(item)
                for item in value
            ]

        return value


    report_checksum = report[
        "report_checksum"
    ]

    report_without_checksum = {
        key:
            value

        for key, value
        in report.items()

        if key != "report_checksum"
    }

    recomputed_checksum = hashlib.sha256(
        json.dumps(
            json_ready(
                report_without_checksum
            ),
            sort_keys=True,
            ensure_ascii=False,
            separators=(
                ",",
                ":",
            ),
        ).encode(
            "utf-8"
        )
    ).hexdigest()

    checks.append(
        (
            "report_checksum_valid",
            report_checksum == recomputed_checksum,
        )
    )
finally:
    shutil.rmtree(
        sandbox_root,
        ignore_errors=True,
    )

after = {
    name: fingerprint(path)
    for name, path in PROTECTED.items()
}

checks.extend(
    [
        (
            "production_outputs_unchanged",
            before == after,
        ),
    ]
)

print()

for name, passed in checks:
    print(
        f"{name:<70}"
        + ("PASS" if passed else "FAIL")
    )

print()
print("FAILURES")

failures = [
    name
    for name, passed in checks
    if not passed
]

if failures:
    print()
    for failure in failures:
        print("-", failure)

    raise SystemExit(1)

print("None")
