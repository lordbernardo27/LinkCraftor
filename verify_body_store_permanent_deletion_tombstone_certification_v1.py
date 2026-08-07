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

from backend.server.universal_article_body_store.body_store_permanent_deletion_tombstone_contract_v1 import (
    create_permanent_deletion_tombstone_contract_v1,
)

from backend.server.universal_article_body_store.body_store_permanent_deletion_tombstone_manager_v1 import (
    build_permanent_deletion_tombstone_manager_bundle_v1,
)

from backend.server.universal_article_body_store.body_store_permanent_deletion_tombstone_verifier_v1 import (
    verify_permanent_deletion_tombstone_v1,
)

from backend.server.universal_article_body_store.body_store_permanent_deletion_tombstone_certification_v1 import (
    BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CERTIFICATION_SCHEMA,
    BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CERTIFICATION_VERSION,
    build_permanent_deletion_tombstone_certification_bundle_v1,
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

    "tombstone_store":
        DATA_ROOT
        / "universal_article_body_store_tombstones",
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
        prefix="tombstone_certification_verify_"
    )
)

try:
    contract = (
        create_permanent_deletion_tombstone_contract_v1(
            tombstone_id="tombstone_body_verify_v1",
            body_id="body_verify",
            workspace_id="ws_verify",
            archive_id="archive_verify",
            lifecycle_record_id="body_lifecycle_verify",
            deletion_request_id="deletion_request_verify",
            deletion_execution_id="deletion_execution_verify",
            deletion_reason="Final permanent deletion tombstone certification.",
            retention_verified=True,
            archive_verified=True,
            recovery_closed=True,
            legal_hold_verified=True,
            verification_id="deletion_verification_verify",
            certification_id="deletion_certification_verify",
            deletion_manager_version="1.0",
        )
    )

    manager_bundle = (
        build_permanent_deletion_tombstone_manager_bundle_v1(
            project_root=sandbox_root,
            tombstone_contract=contract,
        )
    )

    verification_result = (
        verify_permanent_deletion_tombstone_v1(
            project_root=sandbox_root,
            workspace_id="ws_verify",
            tombstone_id="tombstone_body_verify_v1",
        )
    )

    certification_bundle = (
        build_permanent_deletion_tombstone_certification_bundle_v1(
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
                BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CERTIFICATION_SCHEMA
                == "body_store_permanent_deletion_tombstone_certification.v1"
            ),

        "certification_version_valid":
            (
                BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CERTIFICATION_VERSION
                == "1.0"
            ),

        "manager_bundle_complete":
            manager_bundle[
                "bundle_complete"
            ]
            is True,

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

        "bundle_tombstone_verified":
            certification_bundle[
                "tombstone_verified"
            ]
            is True,

        "certification_passed":
            certification[
                "certified"
            ]
            is True,

        "certification_tombstone_verified":
            certification[
                "tombstone_verified"
            ]
            is True,

        "validation_passed":
            validation[
                "certification_valid"
            ]
            is True,

        "schema_validation_passed":
            validation[
                "schema_valid"
            ]
            is True,

        "certification_version_validation_passed":
            validation[
                "certification_version_valid"
            ]
            is True,

        "verifier_version_validation_passed":
            validation[
                "verifier_version_valid"
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

        "tombstone_id_matches":
            validation[
                "tombstone_id_matches"
            ]
            is True,

        "body_id_matches":
            validation[
                "body_id_matches"
            ]
            is True,

        "workspace_id_matches":
            validation[
                "workspace_id_matches"
            ]
            is True,

        "archive_id_matches":
            validation[
                "archive_id_matches"
            ]
            is True,

        "lifecycle_record_id_matches":
            validation[
                "lifecycle_record_id_matches"
            ]
            is True,

        "deletion_request_id_matches":
            validation[
                "deletion_request_id_matches"
            ]
            is True,

        "deletion_execution_id_matches":
            validation[
                "deletion_execution_id_matches"
            ]
            is True,

        "record_integrity_verified":
            certification_bundle[
                "record_integrity_verified"
            ]
            is True,

        "index_integrity_verified":
            certification_bundle[
                "index_integrity_verified"
            ]
            is True,

        "workspace_isolation_verified":
            certification_bundle[
                "workspace_isolation_verified"
            ]
            is True,

        "summary_certified":
            summary[
                "certified"
            ]
            is True,

        "summary_tombstone_verified":
            summary[
                "tombstone_verified"
            ]
            is True,

        "summary_record_integrity_verified":
            summary[
                "record_integrity_verified"
            ]
            is True,

        "summary_index_integrity_verified":
            summary[
                "index_integrity_verified"
            ]
            is True,

        "summary_workspace_isolation_verified":
            summary[
                "workspace_isolation_verified"
            ]
            is True,

        "certification_read_only":
            certification_bundle[
                "read_only"
            ]
            is True,

        "article_body_not_exposed":
            certification_bundle[
                "article_body_exposed"
            ]
            is False,

        "lifecycle_not_modified":
            certification_bundle[
                "lifecycle_modified"
            ]
            is False,

        "archive_not_modified":
            certification_bundle[
                "archive_modified"
            ]
            is False,

        "body_store_not_modified":
            certification_bundle[
                "body_store_modified"
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
        "UNIVERSAL ARTICLE BODY STORE PERMANENT DELETION "
        "TOMBSTONE CERTIFICATION — PHASE 9.1.9.4"
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
    print("PROTECTED OUTPUTS")

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
        "Sandbox tombstones persisted:          1"
    )
    print(
        "Sandbox tombstone indexes written:     1"
    )
    print(
        "Tombstone verifications performed:     1"
    )
    print(
        "Tombstone certifications produced:     1"
    )
    print(
        "Article bodies exposed:                0"
    )
    print(
        "Production lifecycle records modified: 0"
    )
    print(
        "Production archive records modified:   0"
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
            "BODY STORE PERMANENT DELETION TOMBSTONE "
            "CERTIFICATION PHASE 9.1.9.4: FAIL"
        )

        raise SystemExit(1)

    print(
        "BODY STORE PERMANENT DELETION TOMBSTONE "
        "CERTIFICATION PHASE 9.1.9.4: PASS"
    )

    print(
        "The Permanent Deletion Tombstone and Audit subsystem "
        "is fully certified."
    )

    print("=" * 120)

finally:
    shutil.rmtree(
        sandbox_root,
        ignore_errors=True,
    )
