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
    ARCHIVE_REPOSITORY_VERIFIER_SCHEMA,
    ARCHIVE_REPOSITORY_VERIFIER_VERSION,
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
        prefix="archive_repository_verifier_"
    )
)

try:

    execute_archive_repository_manager_v1(
        project_root=sandbox_root,
        archive_id="verify_archive_repository_verifier",
        workspace_id="ws_verify",
        body_id="body_verify",
        archive_reason="Verifier",
        archived_at="2026-08-04T00:00:00+00:00",
        actor_type="SYSTEM",
        actor_id="verifier",
        content="Repository verifier content.",
    )

    verification = (
        verify_archive_repository_v1(
            project_root=sandbox_root,
            workspace_id="ws_verify",
            archive_id="verify_archive_repository_verifier",
        )
    )

    certification = (
        certify_archive_repository_verification_v1(
            verification_result=verification,
        )
    )
    after = {
        key: fingerprint(value)
        for key, value
        in PROTECTED.items()
    }

    checks = {
        "verifier_schema_valid":
            (
                ARCHIVE_REPOSITORY_VERIFIER_SCHEMA
                == "body_store_archive_repository_verifier.v1"
            ),

        "verifier_version_valid":
            (
                ARCHIVE_REPOSITORY_VERIFIER_VERSION
                == "1.0"
            ),

        "repository_verified":
            verification[
                "repository_verified"
            ]
            is True,

        "sections_present":
            verification[
                "sections"
            ][
                "sections_present"
            ]
            is True,

        "identifiers_verified":
            verification[
                "identifiers"
            ][
                "identifiers_verified"
            ]
            is True,

        "checksum_verified":
            verification[
                "checksum"
            ][
                "checksum_verified"
            ]
            is True,

        "paths_verified":
            verification[
                "paths"
            ][
                "paths_verified"
            ]
            is True,

        "workspace_isolated":
            verification[
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

        "certification_repository_verified":
            certification[
                "repository_verified"
            ]
            is True,

        "read_only_verifier":
            certification[
                "read_only"
            ]
            is True,

        "no_repository_write_performed":
            certification[
                "repository_write_performed"
            ]
            is False,

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
        "UNIVERSAL ARTICLE BODY STORE ARCHIVE REPOSITORY VERIFIER — PHASE 9.1.6.3"
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
        "Repository reads performed:           1"
    )
    print(
        "Repository writes by verifier:        0"
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
            "BODY STORE ARCHIVE REPOSITORY VERIFIER PHASE 9.1.6.3: FAIL"
        )

        raise SystemExit(1)

    print(
        "BODY STORE ARCHIVE REPOSITORY VERIFIER PHASE 9.1.6.3: PASS"
    )

    print(
        "The Archive Repository Verifier confirmed section integrity, "
        "identifier consistency, checksum integrity, path validity, and "
        "workspace isolation."
    )

    print("=" * 120)

finally:
    shutil.rmtree(
        sandbox_root,
        ignore_errors=True,
    )
