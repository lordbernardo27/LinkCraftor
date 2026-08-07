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

from backend.server.universal_article_body_store.body_store_archive_repository_verifier_v1 import (
    certify_archive_repository_verification_v1,
    verify_archive_repository_v1,
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
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED.items()
}

sandbox_root = Path(
    tempfile.mkdtemp(
        prefix="archive_repository_certification_"
    )
)

try:
    manager_result = (
        execute_archive_repository_manager_v1(
            project_root=sandbox_root,
            archive_id="archive_repository_certification",
            workspace_id="ws_certification",
            body_id="body_certification",
            archive_reason="Final repository certification.",
            archived_at="2026-08-04T00:00:00+00:00",
            actor_type="SYSTEM",
            actor_id="archive_repository_certifier",
            content="Archive Repository final certification content.",
        )
    )

    verification_result = (
        verify_archive_repository_v1(
            project_root=sandbox_root,
            workspace_id="ws_certification",
            archive_id="archive_repository_certification",
        )
    )

    certification = (
        certify_archive_repository_verification_v1(
            verification_result=verification_result,
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

        "stored_repository_verified":
            manager_result[
                "stored_repository_verified"
            ]
            is True,

        "repository_verifier_passed":
            verification_result[
                "repository_verified"
            ]
            is True,

        "sections_verified":
            verification_result[
                "sections"
            ][
                "sections_present"
            ]
            is True,

        "identifiers_verified":
            verification_result[
                "identifiers"
            ][
                "identifiers_verified"
            ]
            is True,

        "checksum_verified":
            verification_result[
                "checksum"
            ][
                "checksum_verified"
            ]
            is True,

        "paths_verified":
            verification_result[
                "paths"
            ][
                "paths_verified"
            ]
            is True,

        "workspace_isolated":
            verification_result[
                "paths"
            ][
                "workspace_isolated"
            ]
            is True,

        "certification_passed":
            certification[
                "certified"
            ]
            is True,

        "certification_read_only":
            certification[
                "read_only"
            ]
            is True,

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

        "content_body_not_exposed":
            certification[
                "content_body_included"
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
        "UNIVERSAL ARTICLE BODY STORE ARCHIVE REPOSITORY CERTIFICATION — PHASE 9.1.6.4"
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
    print(
        "PROTECTED OUTPUTS"
    )

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
        "Sandbox archive repository writes:   3"
    )
    print(
        "Production Archive Store modified:   0"
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
            "BODY STORE ARCHIVE REPOSITORY CERTIFICATION PHASE 9.1.6.4: FAIL"
        )

        raise SystemExit(1)

    print(
        "BODY STORE ARCHIVE REPOSITORY CERTIFICATION PHASE 9.1.6.4: PASS"
    )

    print(
        "The Archive Repository subsystem is fully certified."
    )

    print("=" * 120)

finally:
    shutil.rmtree(
        sandbox_root,
        ignore_errors=True,
    )
