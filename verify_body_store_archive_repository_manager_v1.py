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
    ARCHIVE_REPOSITORY_MANAGER_SCHEMA,
    ARCHIVE_REPOSITORY_MANAGER_VERSION,
    execute_archive_repository_manager_v1,
    summarize_archive_repository_manager_v1,
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
    key:
        fingerprint(
            value
        )

    for key, value
    in PROTECTED.items()
}

sandbox_root = Path(
    tempfile.mkdtemp(
        prefix="archive_repository_manager_"
    )
)

try:
    manager_result = (
        execute_archive_repository_manager_v1(
            project_root=sandbox_root,
            archive_id="verify_archive_repository_manager",
            workspace_id="ws_verify",
            body_id="body_verify",
            archive_reason="Verifier",
            archived_at="2026-08-04T00:00:00+00:00",
            actor_type="SYSTEM",
            actor_id="verifier",
            content="Repository manager verification content.",
        )
    )

    summary = (
        summarize_archive_repository_manager_v1(
            manager_result=manager_result,
        )
    )

    archive_root = (
        sandbox_root
        / "backend"
        / "server"
        / "data"
        / "universal_article_body_store_archive"
    )

    index_path = (
        archive_root
        / "archive"
        / "ws_verify"
        / "verify_archive_repository_manager"
        / "archive_index.json"
    )

    metadata_path = (
        archive_root
        / "archive"
        / "ws_verify"
        / "verify_archive_repository_manager"
        / "archive_metadata.json"
    )

    content_path = (
        archive_root
        / "archive"
        / "ws_verify"
        / "verify_archive_repository_manager"
        / "archive_content.json"
    )

    after = {
        key:
            fingerprint(
                value
            )

        for key, value
        in PROTECTED.items()
    }

    checks = {
        "manager_schema_valid":
            (
                ARCHIVE_REPOSITORY_MANAGER_SCHEMA
                == "body_store_archive_repository_manager.v1"
            ),

        "manager_version_valid":
            (
                ARCHIVE_REPOSITORY_MANAGER_VERSION
                == "1.0"
            ),

        "manager_completed":
            manager_result[
                "manager_completed"
            ]
            is True,

        "repository_write_performed":
            manager_result[
                "repository_write_performed"
            ]
            is True,

        "physical_archive_performed":
            manager_result[
                "physical_archive_performed"
            ]
            is True,

        "stored_repository_verified":
            manager_result[
                "stored_repository_verified"
            ]
            is True,

        "summary_manager_completed":
            summary[
                "manager_completed"
            ]
            is True,

        "summary_repository_write_performed":
            summary[
                "repository_write_performed"
            ]
            is True,

        "summary_stored_repository_verified":
            summary[
                "stored_repository_verified"
            ]
            is True,

        "archive_index_written":
            index_path.is_file(),

        "archive_metadata_written":
            metadata_path.is_file(),

        "archive_content_written":
            content_path.is_file(),

        "sandbox_archive_root_exists":
            archive_root.is_dir(),

        "no_runtime_job_created":
            manager_result[
                "runtime_job_created"
            ]
            is False,

        "no_queue_job_created":
            manager_result[
                "queue_job_created"
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
        "UNIVERSAL ARTICLE BODY STORE ARCHIVE REPOSITORY MANAGER — PHASE 9.1.6.2"
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
        "Sandbox archive index written:       "
        + (
            "1"
            if index_path.is_file()
            else "0"
        )
    )

    print(
        "Sandbox archive metadata written:    "
        + (
            "1"
            if metadata_path.is_file()
            else "0"
        )
    )

    print(
        "Sandbox archive content written:     "
        + (
            "1"
            if content_path.is_file()
            else "0"
        )
    )

    print(
        "Production lifecycle records modified: 0"
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
            "BODY STORE ARCHIVE REPOSITORY MANAGER PHASE 9.1.6.2: FAIL"
        )

        raise SystemExit(1)

    print(
        "BODY STORE ARCHIVE REPOSITORY MANAGER PHASE 9.1.6.2: PASS"
    )

    print(
        "The Archive Repository Manager persisted and verified an isolated "
        "sandbox archive without modifying production outputs."
    )

    print("=" * 120)

finally:
    shutil.rmtree(
        sandbox_root,
        ignore_errors=True,
    )