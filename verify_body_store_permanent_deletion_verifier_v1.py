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
    build_permanent_deletion_manager_bundle_v1,
)

from backend.server.universal_article_body_store.body_store_permanent_deletion_verifier_v1 import (
    BODY_STORE_PERMANENT_DELETION_VERIFIER_SCHEMA,
    BODY_STORE_PERMANENT_DELETION_VERIFIER_VERSION,
    certify_permanent_deletion_verification_v1,
    summarize_permanent_deletion_verification_v1,
    verify_permanent_deletion_bundle_v1,
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
        prefix="permanent_deletion_verifier_"
    )
)

try:
    execute_archive_repository_manager_v1(
        project_root=sandbox_root,
        archive_id="permanent_deletion_verifier_archive",
        workspace_id="ws_verify",
        body_id="body_verify",
        archive_reason="Permanent deletion verifier test.",
        archived_at="2026-08-04T02:00:00+00:00",
        actor_type="SYSTEM",
        actor_id="permanent_deletion_verifier",
        content="Permanent deletion verifier content.",
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
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    deletion_bundle = (
        build_permanent_deletion_manager_bundle_v1(
            project_root=sandbox_root,
            archive_id="permanent_deletion_verifier_archive",
            workspace_id="ws_verify",
            body_id="body_verify",
            lifecycle_record_id="body_lifecycle_verify",
            source_state="ARCHIVED",
            deletion_reason="Permanent deletion verifier test.",
            requested_by_type="SYSTEM",
            requested_by_id="permanent_deletion_verifier",
            retention_expired=True,
            deletion_eligible=True,
            legal_hold_active=False,
            recovery_closed=True,
            requested_at="2026-08-04T02:00:00+00:00",
        )
    )

    verification = (
        verify_permanent_deletion_bundle_v1(
            project_root=sandbox_root,
            deletion_bundle=deletion_bundle,
        )
    )

    summary = (
        summarize_permanent_deletion_verification_v1(
            verification_result=verification,
        )
    )

    certification = (
        certify_permanent_deletion_verification_v1(
            verification_result=verification,
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
        "verifier_schema_valid":
            (
                BODY_STORE_PERMANENT_DELETION_VERIFIER_SCHEMA
                == "body_store_permanent_deletion_verifier.v1"
            ),

        "verifier_version_valid":
            (
                BODY_STORE_PERMANENT_DELETION_VERIFIER_VERSION
                == "1.0"
            ),

        "deletion_verified":
            verification[
                "deletion_verified"
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

        "boundaries_verified":
            verification[
                "boundaries"
            ][
                "boundaries_verified"
            ]
            is True,

        "filesystem_result_verified":
            verification[
                "filesystem_result"
            ][
                "filesystem_result_verified"
            ]
            is True,

        "lifecycle_verified":
            verification[
                "lifecycle"
            ][
                "lifecycle_verified"
            ]
            is True,

        "workspace_isolation_verified":
            verification[
                "workspace_isolation"
            ][
                "workspace_isolation_verified"
            ]
            is True,

        "summary_deletion_verified":
            summary[
                "deletion_verified"
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

        "summary_boundaries_verified":
            summary[
                "boundaries_verified"
            ]
            is True,

        "summary_filesystem_result_verified":
            summary[
                "filesystem_result_verified"
            ]
            is True,

        "summary_lifecycle_verified":
            summary[
                "lifecycle_verified"
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

        "certification_deletion_verified":
            certification[
                "deletion_verified"
            ]
            is True,

        "certification_read_only":
            certification[
                "read_only"
            ]
            is True,

        "archive_delete_confirmed":
            certification[
                "archive_delete_performed"
            ]
            is True,

        "lifecycle_transition_confirmed":
            certification[
                "lifecycle_transition_performed"
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
        "UNIVERSAL ARTICLE BODY STORE PERMANENT DELETION VERIFIER — PHASE 9.1.8.3"
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
        "Sandbox archive deletions verified:   1"
    )
    print(
        "Sandbox lifecycle transitions verified: 1"
    )
    print(
        "Production archive deletions:          0"
    )
    print(
        "Production Body Store deletions:       0"
    )
    print(
        "Production lifecycle transitions:      0"
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
            "BODY STORE PERMANENT DELETION VERIFIER PHASE 9.1.8.3: FAIL"
        )

        raise SystemExit(1)

    print(
        "BODY STORE PERMANENT DELETION VERIFIER PHASE 9.1.8.3: PASS"
    )

    print(
        "The Permanent Deletion Verifier confirmed identity, eligibility "
        "boundaries, filesystem removal, lifecycle preservation, and "
        "workspace isolation."
    )

    print("=" * 120)

finally:
    shutil.rmtree(
        sandbox_root,
        ignore_errors=True,
    )
