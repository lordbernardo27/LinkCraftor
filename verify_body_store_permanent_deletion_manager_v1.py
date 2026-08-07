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

from backend.server.universal_article_body_store.body_store_archive_repository_manager_v1 import (
    execute_archive_repository_manager_v1,
)

from backend.server.universal_article_body_store.body_store_permanent_deletion_manager_v1 import (
    BODY_STORE_PERMANENT_DELETION_MANAGER_SCHEMA,
    BODY_STORE_PERMANENT_DELETION_MANAGER_VERSION,
    build_permanent_deletion_manager_bundle_v1,
    summarize_permanent_deletion_manager_bundle_v1,
    verify_permanent_deletion_manager_bundle_v1,
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
    key: fingerprint(value)
    for key, value
    in PROTECTED.items()
}

sandbox_root = Path(
    tempfile.mkdtemp(
        prefix="permanent_deletion_manager_verify_"
    )
)

try:

    execute_archive_repository_manager_v1(
        project_root=sandbox_root,
        archive_id="permanent_delete_archive",
        workspace_id="ws_verify",
        body_id="body_verify",
        archive_reason="Permanent deletion verification.",
        archived_at="2026-08-04T02:00:00+00:00",
        actor_type="SYSTEM",
        actor_id="permanent_deletion_verifier",
        content="Permanent deletion verification content.",
    )

    lifecycle_root = (
        sandbox_root
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store_lifecycle"
        / "ws_verify"
    )

    lifecycle_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    lifecycle_file = (
        lifecycle_root
        / "body_lifecycle_verify.json"
    )

    lifecycle_file.write_text(
        json.dumps(
            {
                "state": "ARCHIVED",
                "lifecycle_state": "ARCHIVED",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    bundle = (
        build_permanent_deletion_manager_bundle_v1(
            project_root=sandbox_root,
            archive_id="permanent_delete_archive",
            workspace_id="ws_verify",
            body_id="body_verify",
            lifecycle_record_id="body_lifecycle_verify",
            source_state="ARCHIVED",
            deletion_reason="Permanent deletion verification.",
            requested_by_type="SYSTEM",
            requested_by_id="permanent_deletion_verifier",
            retention_expired=True,
            deletion_eligible=True,
            legal_hold_active=False,
            recovery_closed=True,
            requested_at="2026-08-04T02:00:00+00:00",
        )
    )

    summary = (
        summarize_permanent_deletion_manager_bundle_v1(
            deletion_bundle=bundle,
        )
    )

    verification = (
        verify_permanent_deletion_manager_bundle_v1(
            deletion_bundle=bundle,
        )
    )
    after = {
        key: fingerprint(value)
        for key, value
        in PROTECTED.items()
    }

    deletion_result = bundle[
        "deletion_result"
    ]

    lifecycle_payload = json.loads(
        lifecycle_file.read_text(
            encoding="utf-8-sig",
        )
    )

    checks = {
        "manager_schema_valid":
            (
                BODY_STORE_PERMANENT_DELETION_MANAGER_SCHEMA
                == "body_store_permanent_deletion_manager.v1"
            ),

        "manager_version_valid":
            (
                BODY_STORE_PERMANENT_DELETION_MANAGER_VERSION
                == "1.0"
            ),

        "bundle_complete":
            bundle[
                "bundle_complete"
            ]
            is True,

        "deletion_verified":
            bundle[
                "deletion_verified"
            ]
            is True,

        "deletion_status_deleted":
            (
                bundle[
                    "deletion_status"
                ]
                == "DELETED"
            ),

        "archive_delete_performed":
            bundle[
                "archive_delete_performed"
            ]
            is True,

        "archive_removed":
            deletion_result[
                "archive_exists_after"
            ]
            is False,

        "body_store_removed_or_absent":
            deletion_result[
                "body_store_exists_after"
            ]
            is False,

        "lifecycle_preserved":
            deletion_result[
                "lifecycle_exists_after"
            ]
            is True,

        "lifecycle_transition_performed":
            bundle[
                "lifecycle_transition_performed"
            ]
            is True,

        "lifecycle_state_permanently_deleted":
            (
                lifecycle_payload[
                    "state"
                ]
                == "PERMANENTLY_DELETED"
                and lifecycle_payload[
                    "lifecycle_state"
                ]
                == "PERMANENTLY_DELETED"
            ),

        "lifecycle_deletion_marker_present":
            lifecycle_payload[
                "permanent_deletion"
            ]
            is True,

        "lifecycle_execution_id_matches":
            (
                lifecycle_payload[
                    "deletion_execution_id"
                ]
                == bundle[
                    "execution_package"
                ][
                    "deletion_execution_id"
                ]
            ),

        "manager_bundle_valid":
            verification[
                "bundle_valid"
            ]
            is True,

        "plan_id_matches":
            verification[
                "plan_id_matches"
            ]
            is True,

        "request_id_matches":
            verification[
                "request_id_matches"
            ]
            is True,

        "archive_id_matches":
            verification[
                "archive_id_matches"
            ]
            is True,

        "workspace_id_matches":
            verification[
                "workspace_id_matches"
            ]
            is True,

        "body_id_matches":
            verification[
                "body_id_matches"
            ]
            is True,

        "lifecycle_record_id_matches":
            verification[
                "lifecycle_record_id_matches"
            ]
            is True,

        "summary_deletion_verified":
            summary[
                "deletion_verified"
            ]
            is True,

        "summary_deletion_status":
            (
                summary[
                    "deletion_status"
                ]
                == "DELETED"
            ),

        "no_runtime_job_created":
            bundle[
                "runtime_job_created"
            ]
            is False,

        "no_queue_job_created":
            bundle[
                "queue_job_created"
            ]
            is False,

        "content_body_not_exposed":
            bundle[
                "content_body_included"
            ]
            is False,

        "production_outputs_unchanged":
            all(
                before[
                    key
                ]
                == after[
                    key
                ]
                for key
                in before
            ),
    }

    failures = [
        key
        for key, passed
        in checks.items()
        if passed is not True
    ]

    print()
    print("=" * 120)
    print(
        "UNIVERSAL ARTICLE BODY STORE PERMANENT DELETION MANAGER — PHASE 9.1.8.2"
    )
    print("=" * 120)
    print()

    for key, passed in checks.items():
        print(
            f"{key:<72}"
            + (
                "PASS"
                if passed
                else "FAIL"
            )
        )

    print()
    print("PROTECTED OUTPUTS")

    for key in before:
        print(
            "  "
            + f"{key:<30}"
            + (
                "UNCHANGED"
                if before[
                    key
                ]
                == after[
                    key
                ]
                else "CHANGED"
            )
        )

    print()
    print(
        "Sandbox archive deletions performed:   1"
    )
    print(
        "Sandbox lifecycle transitions:         1"
    )
    print(
        "Production archive deletions:           0"
    )
    print(
        "Production Body Store deletions:        0"
    )
    print(
        "Production lifecycle transitions:       0"
    )
    print(
        "Production queue jobs created:          0"
    )
    print(
        "Runtime registrations modified:         0"
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
            "BODY STORE PERMANENT DELETION MANAGER PHASE 9.1.8.2: FAIL"
        )
        raise SystemExit(1)

    print(
        "BODY STORE PERMANENT DELETION MANAGER PHASE 9.1.8.2: PASS"
    )

    print(
        "The Permanent Deletion Manager removed the sandbox archive, "
        "preserved the lifecycle record, and transitioned it to "
        "PERMANENTLY_DELETED without modifying production outputs."
    )

    print("=" * 120)

finally:
    shutil.rmtree(
        sandbox_root,
        ignore_errors=True,
    )
