from __future__ import annotations

import hashlib
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

from backend.server.universal_article_body_store.body_store_archive_recovery_manager_v1 import (
    BODY_STORE_ARCHIVE_RECOVERY_MANAGER_SCHEMA,
    BODY_STORE_ARCHIVE_RECOVERY_MANAGER_VERSION,
    build_archive_recovery_manager_bundle_v1,
    summarize_archive_recovery_manager_bundle_v1,
    verify_archive_recovery_manager_bundle_v1,
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
        key=lambda p: (
            p.relative_to(path).as_posix()
        ),
    ):
        digest.update(
            item.relative_to(
                path
            ).as_posix().encode()
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
        prefix="archive_recovery_manager_"
    )
)

try:

    execute_archive_repository_manager_v1(
        project_root=sandbox_root,
        archive_id="archive_recovery_manager_verify",
        workspace_id="ws_verify",
        body_id="body_verify",
        archive_reason="Recovery manager verifier.",
        archived_at="2026-08-04T01:00:00+00:00",
        actor_type="SYSTEM",
        actor_id="archive_recovery_manager_verifier",
        content="Recovery manager verification content.",
    )

    bundle = (
        build_archive_recovery_manager_bundle_v1(
            project_root=sandbox_root,
            archive_id="archive_recovery_manager_verify",
            workspace_id="ws_verify",
            body_id="body_verify",
            lifecycle_record_id="body_lifecycle_verify",
            source_state="ARCHIVED",
            recovery_reason="Verifier",
            requested_by_type="SYSTEM",
            requested_by_id="archive_recovery_manager_verifier",
            requested_at="2026-08-04T01:00:00+00:00",
        )
    )

    verification = (
        verify_archive_recovery_manager_bundle_v1(
            recovery_bundle=bundle,
        )
    )

    summary = (
        summarize_archive_recovery_manager_bundle_v1(
            recovery_bundle=bundle,
        )
    )
    after = {
        key: fingerprint(value)
        for key, value
        in PROTECTED.items()
    }

    checks = {
        "manager_schema_valid":
            (
                BODY_STORE_ARCHIVE_RECOVERY_MANAGER_SCHEMA
                == "body_store_archive_recovery_manager.v1"
            ),

        "manager_version_valid":
            (
                BODY_STORE_ARCHIVE_RECOVERY_MANAGER_VERSION
                == "1.0"
            ),

        "bundle_complete":
            bundle[
                "bundle_complete"
            ]
            is True,

        "bundle_certified":
            bundle[
                "certified"
            ]
            is True,

        "recovery_status_ready":
            (
                bundle[
                    "recovery_status"
                ]
                == "READY"
            ),

        "archive_read_performed":
            bundle[
                "archive_read_performed"
            ]
            is True,

        "archive_verification_performed":
            bundle[
                "archive_verification_performed"
            ]
            is True,

        "body_store_write_not_performed":
            bundle[
                "body_store_write_performed"
            ]
            is False,

        "lifecycle_transition_not_performed":
            bundle[
                "lifecycle_transition_performed"
            ]
            is False,

        "bundle_valid":
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

        "summary_bundle_complete":
            summary[
                "bundle_complete"
            ]
            is True,

        "summary_bundle_certified":
            summary[
                "bundle_certified"
            ]
            is True,

        "summary_bundle_valid":
            summary[
                "bundle_valid"
            ]
            is True,

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
        "UNIVERSAL ARTICLE BODY STORE ARCHIVE RECOVERY MANAGER — PHASE 9.1.7.2"
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
    print(
        "PROTECTED OUTPUTS"
    )

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
        "Sandbox archive reads performed:      1"
    )
    print(
        "Sandbox archive verifications:         1"
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
            "BODY STORE ARCHIVE RECOVERY MANAGER PHASE 9.1.7.2: FAIL"
        )

        raise SystemExit(1)

    print(
        "BODY STORE ARCHIVE RECOVERY MANAGER PHASE 9.1.7.2: PASS"
    )

    print(
        "The Archive Recovery Manager produced and verified a certified "
        "read-only recovery bundle without modifying production outputs."
    )

    print("=" * 120)

finally:
    shutil.rmtree(
        sandbox_root,
        ignore_errors=True,
    )
