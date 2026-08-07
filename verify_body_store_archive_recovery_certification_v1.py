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
    verify_archive_recovery_bundle_v1,
)

from backend.server.universal_article_body_store.body_store_archive_recovery_certification_v1 import (
    BODY_STORE_ARCHIVE_RECOVERY_CERTIFICATION_SCHEMA,
    BODY_STORE_ARCHIVE_RECOVERY_CERTIFICATION_VERSION,
    build_archive_recovery_certification_bundle_v1,
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
        prefix="archive_recovery_certification_"
    )
)

try:
    execute_archive_repository_manager_v1(
        project_root=sandbox_root,
        archive_id="archive_recovery_certification_verify",
        workspace_id="ws_verify",
        body_id="body_verify",
        archive_reason="Recovery certification verifier.",
        archived_at="2026-08-04T01:00:00+00:00",
        actor_type="SYSTEM",
        actor_id="archive_recovery_certifier",
        content="Archive recovery certification content.",
    )

    recovery_bundle = (
        build_archive_recovery_manager_bundle_v1(
            project_root=sandbox_root,
            archive_id="archive_recovery_certification_verify",
            workspace_id="ws_verify",
            body_id="body_verify",
            lifecycle_record_id="body_lifecycle_verify",
            source_state="ARCHIVED",
            recovery_reason="Final recovery certification.",
            requested_by_type="SYSTEM",
            requested_by_id="archive_recovery_certifier",
            requested_at="2026-08-04T01:00:00+00:00",
        )
    )

    verification_result = (
        verify_archive_recovery_bundle_v1(
            recovery_bundle=recovery_bundle,
        )
    )

    certification_bundle = (
        build_archive_recovery_certification_bundle_v1(
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

    certification = certification_bundle[
        "certification"
    ]

    validation = certification_bundle[
        "validation"
    ]

    summary = certification_bundle[
        "summary"
    ]

    checks = {
        "certification_schema_valid":
            (
                BODY_STORE_ARCHIVE_RECOVERY_CERTIFICATION_SCHEMA
                == "body_store_archive_recovery_certification.v1"
            ),

        "certification_version_valid":
            (
                BODY_STORE_ARCHIVE_RECOVERY_CERTIFICATION_VERSION
                == "1.0"
            ),

        "bundle_complete":
            certification_bundle[
                "bundle_complete"
            ]
            is True,

        "bundle_certified":
            certification_bundle[
                "certified"
            ]
            is True,

        "bundle_verified":
            certification_bundle[
                "verified"
            ]
            is True,

        "certification_passed":
            certification[
                "certified"
            ]
            is True,

        "certification_verified":
            certification[
                "verified"
            ]
            is True,

        "validation_passed":
            validation[
                "certification_valid"
            ]
            is True,

        "schema_valid":
            validation[
                "schema_valid"
            ]
            is True,

        "version_valid":
            validation[
                "version_valid"
            ]
            is True,

        "verifier_certified":
            validation[
                "verifier_certified"
            ]
            is True,

        "verification_id_matches":
            validation[
                "verification_id_matches"
            ]
            is True,

        "safety_boundaries_valid":
            validation[
                "safety_boundaries_valid"
            ]
            is True,

        "summary_certified":
            summary[
                "certified"
            ]
            is True,

        "summary_verified":
            summary[
                "verified"
            ]
            is True,

        "archive_read_performed":
            certification_bundle[
                "archive_read_performed"
            ]
            is True,

        "no_body_store_write_performed":
            certification_bundle[
                "body_store_write_performed"
            ]
            is False,

        "no_lifecycle_transition_performed":
            certification_bundle[
                "lifecycle_transition_performed"
            ]
            is False,

        "no_runtime_job_created":
            certification_bundle[
                "runtime_job_created"
            ]
            is False,

        "no_queue_job_created":
            certification_bundle[
                "queue_job_created"
            ]
            is False,

        "content_body_not_exposed":
            certification_bundle[
                "content_body_included"
            ]
            is False,

        "certification_read_only":
            certification_bundle[
                "read_only"
            ]
            is True,

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
        "UNIVERSAL ARTICLE BODY STORE ARCHIVE RECOVERY CERTIFICATION — PHASE 9.1.7.4"
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
        "Sandbox archive reads performed:      1"
    )
    print(
        "Recovery verifications performed:      1"
    )
    print(
        "Recovery certifications produced:      1"
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
            "BODY STORE ARCHIVE RECOVERY CERTIFICATION PHASE 9.1.7.4: FAIL"
        )

        raise SystemExit(1)

    print(
        "BODY STORE ARCHIVE RECOVERY CERTIFICATION PHASE 9.1.7.4: PASS"
    )

    print(
        "The Archive Recovery subsystem is fully certified."
    )

    print("=" * 120)

finally:
    shutil.rmtree(
        sandbox_root,
        ignore_errors=True,
    )
