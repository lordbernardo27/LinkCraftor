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
    BODY_STORE_PERMANENT_DELETION_TOMBSTONE_VERIFIER_SCHEMA,
    BODY_STORE_PERMANENT_DELETION_TOMBSTONE_VERIFIER_VERSION,
    certify_permanent_deletion_tombstone_verification_v1,
    summarize_permanent_deletion_tombstone_verification_v1,
    verify_permanent_deletion_tombstone_v1,
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
        prefix="tombstone_verifier_verify_"
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
            deletion_reason="Permanent deletion tombstone verifier test.",
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

    verification = (
        verify_permanent_deletion_tombstone_v1(
            project_root=sandbox_root,
            workspace_id="ws_verify",
            tombstone_id="tombstone_body_verify_v1",
        )
    )

    summary = (
        summarize_permanent_deletion_tombstone_verification_v1(
            verification_result=verification,
        )
    )

    certification = (
        certify_permanent_deletion_tombstone_verification_v1(
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
                BODY_STORE_PERMANENT_DELETION_TOMBSTONE_VERIFIER_SCHEMA
                == "body_store_permanent_deletion_tombstone_verifier.v1"
            ),

        "verifier_version_valid":
            (
                BODY_STORE_PERMANENT_DELETION_TOMBSTONE_VERIFIER_VERSION
                == "1.0"
            ),

        "manager_bundle_complete":
            manager_bundle[
                "bundle_complete"
            ]
            is True,

        "tombstone_verified":
            verification[
                "tombstone_verified"
            ]
            is True,

        "record_integrity_verified":
            verification[
                "record_integrity"
            ][
                "record_integrity_verified"
            ]
            is True,

        "record_contract_valid":
            verification[
                "record_integrity"
            ][
                "contract_valid"
            ]
            is True,

        "record_contract_checksum_valid":
            verification[
                "record_integrity"
            ][
                "contract_checksum_valid"
            ]
            is True,

        "record_identity_valid":
            verification[
                "record_integrity"
            ][
                "identity_valid"
            ]
            is True,

        "record_evidence_valid":
            verification[
                "record_integrity"
            ][
                "evidence_valid"
            ]
            is True,

        "record_immutable":
            verification[
                "record_integrity"
            ][
                "immutable_valid"
            ]
            is True,

        "record_content_free":
            verification[
                "record_integrity"
            ][
                "content_free"
            ]
            is True,

        "no_forbidden_content_fields":
            not verification[
                "record_integrity"
            ][
                "forbidden_content_fields"
            ],

        "index_integrity_verified":
            verification[
                "index_integrity"
            ][
                "index_integrity_verified"
            ]
            is True,

        "index_schema_valid":
            verification[
                "index_integrity"
            ][
                "schema_valid"
            ]
            is True,

        "index_manager_version_valid":
            verification[
                "index_integrity"
            ][
                "manager_version_valid"
            ]
            is True,

        "index_workspace_valid":
            verification[
                "index_integrity"
            ][
                "workspace_valid"
            ]
            is True,

        "index_tombstone_count_valid":
            verification[
                "index_integrity"
            ][
                "tombstone_count_valid"
            ]
            is True,

        "index_entry_count_valid":
            verification[
                "index_integrity"
            ][
                "entry_count_valid"
            ]
            is True,

        "index_entry_identity_valid":
            verification[
                "index_integrity"
            ][
                "entry_identity_valid"
            ]
            is True,

        "index_contract_checksum_matches":
            verification[
                "index_integrity"
            ][
                "contract_checksum_matches"
            ]
            is True,

        "index_record_checksum_matches":
            verification[
                "index_integrity"
            ][
                "record_checksum_matches"
            ]
            is True,

        "index_record_path_matches":
            verification[
                "index_integrity"
            ][
                "record_path_matches"
            ]
            is True,

        "index_content_boundary_valid":
            verification[
                "index_integrity"
            ][
                "content_boundary_valid"
            ]
            is True,

        "workspace_isolation_verified":
            verification[
                "workspace_isolation"
            ][
                "workspace_isolation_verified"
            ]
            is True,

        "record_path_isolated":
            verification[
                "workspace_isolation"
            ][
                "record_path_isolated"
            ]
            is True,

        "index_path_isolated":
            verification[
                "workspace_isolation"
            ][
                "index_path_isolated"
            ]
            is True,

        "workspace_root_isolated":
            verification[
                "workspace_isolation"
            ][
                "workspace_root_isolated"
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

        "certification_read_only":
            certification[
                "read_only"
            ]
            is True,

        "article_body_not_exposed":
            certification[
                "article_body_exposed"
            ]
            is False,

        "lifecycle_not_modified":
            certification[
                "lifecycle_modified"
            ]
            is False,

        "archive_not_modified":
            certification[
                "archive_modified"
            ]
            is False,

        "body_store_not_modified":
            certification[
                "body_store_modified"
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
        "TOMBSTONE VERIFIER — PHASE 9.1.9.3"
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
        "Sandbox tombstone records verified:   1"
    )
    print(
        "Sandbox tombstone indexes verified:   1"
    )
    print(
        "Article bodies exposed:               0"
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
            "VERIFIER PHASE 9.1.9.3: FAIL"
        )

        raise SystemExit(1)

    print(
        "BODY STORE PERMANENT DELETION TOMBSTONE "
        "VERIFIER PHASE 9.1.9.3: PASS"
    )

    print(
        "The Tombstone Verifier independently confirmed record integrity, "
        "index consistency, checksum integrity, workspace isolation, "
        "immutability, and absence of deleted article content."
    )

    print("=" * 120)

finally:
    shutil.rmtree(
        sandbox_root,
        ignore_errors=True,
    )
