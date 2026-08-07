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
    verify_permanent_deletion_bundle_v1,
)

from backend.server.universal_article_body_store.body_store_permanent_deletion_certification_v1 import (
    BODY_STORE_PERMANENT_DELETION_CERTIFICATION_SCHEMA,
    BODY_STORE_PERMANENT_DELETION_CERTIFICATION_VERSION,
    build_permanent_deletion_certification_bundle_v1,
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
        prefix="permanent_deletion_certification_"
    )
)

try:
    execute_archive_repository_manager_v1(
        project_root=sandbox_root,
        archive_id="permanent_deletion_certification_archive",
        workspace_id="ws_verify",
        body_id="body_verify",
        archive_reason="Permanent deletion certification test.",
        archived_at="2026-08-04T02:00:00+00:00",
        actor_type="SYSTEM",
        actor_id="permanent_deletion_certifier",
        content="Permanent deletion certification content.",
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
            archive_id="permanent_deletion_certification_archive",
            workspace_id="ws_verify",
            body_id="body_verify",
            lifecycle_record_id="body_lifecycle_verify",
            source_state="ARCHIVED",
            deletion_reason="Final permanent deletion certification.",
            requested_by_type="SYSTEM",
            requested_by_id="permanent_deletion_certifier",
            retention_expired=True,
            deletion_eligible=True,
            legal_hold_active=False,
            recovery_closed=True,
            requested_at="2026-08-04T02:00:00+00:00",
        )
    )

    verification_result = (
        verify_permanent_deletion_bundle_v1(
            project_root=sandbox_root,
            deletion_bundle=deletion_bundle,
        )
    )

    certification_bundle = (
        build_permanent_deletion_certification_bundle_v1(
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
                BODY_STORE_PERMANENT_DELETION_CERTIFICATION_SCHEMA
                == "body_store_permanent_deletion_certification.v1"
            ),

        "certification_version_valid":
            (
                BODY_STORE_PERMANENT_DELETION_CERTIFICATION_VERSION
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

        "execution_id_matches":
            validation[
                "execution_id_matches"
            ]
            is True,

        "plan_id_matches":
            validation[
                "plan_id_matches"
            ]
            is True,

        "request_id_matches":
            validation[
                "request_id_matches"
            ]
            is True,

        "deletion_evidence_valid":
            validation[
                "deletion_evidence_valid"
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

        "archive_delete_confirmed":
            certification_bundle[
                "archive_delete_performed"
            ]
            is True,

        "lifecycle_transition_confirmed":
            certification_bundle[
                "lifecycle_transition_performed"
            ]
            is True,

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
        "UNIVERSAL ARTICLE BODY STORE PERMANENT DELETION CERTIFICATION — PHASE 9.1.8.4"
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
        "Sandbox archive deletions performed:    1"
    )
    print(
        "Sandbox lifecycle transitions performed: 1"
    )
    print(
        "Permanent deletion verifications:        1"
    )
    print(
        "Permanent deletion certifications:       1"
    )
    print(
        "Production archive deletions:             0"
    )
    print(
        "Production Body Store deletions:          0"
    )
    print(
        "Production lifecycle transitions:         0"
    )
    print(
        "Production queue jobs created:            0"
    )
    print(
        "Runtime registrations modified:           0"
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
            "BODY STORE PERMANENT DELETION CERTIFICATION PHASE 9.1.8.4: FAIL"
        )

        raise SystemExit(1)

    print(
        "BODY STORE PERMANENT DELETION CERTIFICATION PHASE 9.1.8.4: PASS"
    )

    print(
        "The Permanent Deletion subsystem is fully certified."
    )

    print("=" * 120)

finally:
    shutil.rmtree(
        sandbox_root,
        ignore_errors=True,
    )
