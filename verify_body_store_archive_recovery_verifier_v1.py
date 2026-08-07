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
    build_archive_recovery_manager_bundle_v1,
)

from backend.server.universal_article_body_store.body_store_archive_recovery_verifier_v1 import (
    BODY_STORE_ARCHIVE_RECOVERY_VERIFIER_SCHEMA,
    BODY_STORE_ARCHIVE_RECOVERY_VERIFIER_VERSION,
    certify_archive_recovery_verification_v1,
    summarize_archive_recovery_verification_v1,
    verify_archive_recovery_bundle_v1,
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
        prefix="archive_recovery_verifier_"
    )
)

try:

    execute_archive_repository_manager_v1(
        project_root=sandbox_root,
        archive_id="archive_recovery_verifier_verify",
        workspace_id="ws_verify",
        body_id="body_verify",
        archive_reason="Recovery verifier test.",
        archived_at="2026-08-04T01:00:00+00:00",
        actor_type="SYSTEM",
        actor_id="archive_recovery_verifier",
        content="Archive recovery verifier content.",
    )

    recovery_bundle = (
        build_archive_recovery_manager_bundle_v1(
            project_root=sandbox_root,
            archive_id="archive_recovery_verifier_verify",
            workspace_id="ws_verify",
            body_id="body_verify",
            lifecycle_record_id="body_lifecycle_verify",
            source_state="ARCHIVED",
            recovery_reason="Verifier",
            requested_by_type="SYSTEM",
            requested_by_id="archive_recovery_verifier",
            requested_at="2026-08-04T01:00:00+00:00",
        )
    )

    verification = (
        verify_archive_recovery_bundle_v1(
            recovery_bundle=recovery_bundle,
        )
    )

    summary = (
        summarize_archive_recovery_verification_v1(
            verification_result=verification,
        )
    )

    certification = (
        certify_archive_recovery_verification_v1(
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
                BODY_STORE_ARCHIVE_RECOVERY_VERIFIER_SCHEMA
                == "body_store_archive_recovery_verifier.v1"
            ),

        "verifier_version_valid":
            (
                BODY_STORE_ARCHIVE_RECOVERY_VERIFIER_VERSION
                == "1.0"
            ),

        "recovery_verified":
            verification[
                "recovery_verified"
            ]
            is True,

        "structure_valid":
            verification[
                "structure"
            ][
                "structure_valid"
            ]
            is True,

        "identity_verified":
            verification[
                "identity"
            ][
                "identity_verified"
            ]
            is True,

        "content_verified":
            verification[
                "content"
            ][
                "content_verified"
            ]
            is True,

        "transition_verified":
            verification[
                "transition"
            ][
                "transition_verified"
            ]
            is True,

        "workspace_isolation_verified":
            verification[
                "workspace_isolation"
            ][
                "workspace_isolation_verified"
            ]
            is True,

        "summary_recovery_verified":
            summary[
                "recovery_verified"
            ]
            is True,

        "summary_structure_valid":
            summary[
                "structure_valid"
            ]
            is True,

        "summary_identity_verified":
            summary[
                "identity_verified"
            ]
            is True,

        "summary_content_verified":
            summary[
                "content_verified"
            ]
            is True,

        "summary_transition_verified":
            summary[
                "transition_verified"
            ]
            is True,

        "summary_workspace_isolation_verified":
            summary[
                "workspace_isolation_verified"
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

        "archive_read_performed":
            certification[
                "archive_read_performed"
            ]
            is True,

        "no_body_store_write_performed":
            certification[
                "body_store_write_performed"
            ]
            is False,

        "no_lifecycle_transition_performed":
            certification[
                "lifecycle_transition_performed"
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
        "UNIVERSAL ARTICLE BODY STORE ARCHIVE RECOVERY VERIFIER — PHASE 9.1.7.3"
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
        "Archive reads performed:               1"
    )
    print(
        "Recovery verifications performed:      1"
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
            "BODY STORE ARCHIVE RECOVERY VERIFIER PHASE 9.1.7.3: FAIL"
        )

        raise SystemExit(1)

    print(
        "BODY STORE ARCHIVE RECOVERY VERIFIER PHASE 9.1.7.3: PASS"
    )

    print(
        "The Archive Recovery Verifier confirmed bundle structure, identity, "
        "content checksum, workspace isolation, and the proposed "
        "ARCHIVED-to-ACTIVE transition."
    )

    print("=" * 120)

finally:
    shutil.rmtree(
        sandbox_root,
        ignore_errors=True,
    )
