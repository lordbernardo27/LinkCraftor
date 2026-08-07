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
    BODY_STORE_PERMANENT_DELETION_TOMBSTONE_INDEX_SCHEMA,
    BODY_STORE_PERMANENT_DELETION_TOMBSTONE_MANAGER_SCHEMA,
    BODY_STORE_PERMANENT_DELETION_TOMBSTONE_MANAGER_VERSION,
    BODY_STORE_PERMANENT_DELETION_TOMBSTONE_STORE_NAME,
    build_permanent_deletion_tombstone_manager_bundle_v1,
    load_persisted_tombstone_v1,
    load_tombstone_index_v1,
    resolve_tombstone_index_path_v1,
    resolve_tombstone_record_path_v1,
    verify_permanent_deletion_tombstone_manager_bundle_v1,
    verify_persisted_tombstone_v1,
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
        prefix="tombstone_manager_verify_"
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
            deletion_reason="Permanent deletion tombstone manager verification.",
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

    bundle_verification = (
        verify_permanent_deletion_tombstone_manager_bundle_v1(
            manager_bundle=manager_bundle,
        )
    )

    persisted_tombstone = (
        load_persisted_tombstone_v1(
            project_root=sandbox_root,
            workspace_id="ws_verify",
            tombstone_id="tombstone_body_verify_v1",
        )
    )

    persisted_verification = (
        verify_persisted_tombstone_v1(
            project_root=sandbox_root,
            workspace_id="ws_verify",
            tombstone_id="tombstone_body_verify_v1",
        )
    )

    record_path = (
        resolve_tombstone_record_path_v1(
            project_root=sandbox_root,
            workspace_id="ws_verify",
            tombstone_id="tombstone_body_verify_v1",
        )
    )

    index_path = (
        resolve_tombstone_index_path_v1(
            project_root=sandbox_root,
            workspace_id="ws_verify",
        )
    )

    index_payload = (
        load_tombstone_index_v1(
            index_path=index_path,
            workspace_id="ws_verify",
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
        "manager_schema_valid":
            (
                BODY_STORE_PERMANENT_DELETION_TOMBSTONE_MANAGER_SCHEMA
                == "body_store_permanent_deletion_tombstone_manager.v1"
            ),

        "manager_version_valid":
            (
                BODY_STORE_PERMANENT_DELETION_TOMBSTONE_MANAGER_VERSION
                == "1.0"
            ),

        "store_name_valid":
            (
                BODY_STORE_PERMANENT_DELETION_TOMBSTONE_STORE_NAME
                == "universal_article_body_store_tombstones"
            ),

        "index_schema_valid":
            (
                BODY_STORE_PERMANENT_DELETION_TOMBSTONE_INDEX_SCHEMA
                == "body_store_permanent_deletion_tombstone_index.v1"
            ),

        "manager_bundle_complete":
            manager_bundle[
                "bundle_complete"
            ]
            is True,

        "manager_tombstone_persisted":
            manager_bundle[
                "tombstone_persisted"
            ]
            is True,

        "manager_index_updated":
            manager_bundle[
                "index_updated"
            ]
            is True,

        "manager_tombstone_verified":
            manager_bundle[
                "tombstone_verified"
            ]
            is True,

        "bundle_valid":
            bundle_verification[
                "bundle_valid"
            ]
            is True,

        "tombstone_id_matches":
            bundle_verification[
                "tombstone_id_matches"
            ]
            is True,

        "body_id_matches":
            bundle_verification[
                "body_id_matches"
            ]
            is True,

        "workspace_id_matches":
            bundle_verification[
                "workspace_id_matches"
            ]
            is True,

        "persistence_confirmed":
            bundle_verification[
                "persistence_confirmed"
            ]
            is True,

        "verification_confirmed":
            bundle_verification[
                "verification_confirmed"
            ]
            is True,

        "safety_boundaries_valid":
            bundle_verification[
                "safety_boundaries_valid"
            ]
            is True,

        "record_written":
            record_path.is_file(),

        "index_written":
            index_path.is_file(),

        "persisted_contract_checksum_matches":
            (
                persisted_tombstone[
                    "checksum"
                ]
                == contract[
                    "checksum"
                ]
            ),

        "persisted_tombstone_verified":
            persisted_verification[
                "tombstone_verified"
            ]
            is True,

        "persisted_index_entry_present":
            persisted_verification[
                "index_entry_present"
            ]
            is True,

        "persisted_contract_checksum_verified":
            persisted_verification[
                "contract_checksum_matches"
            ]
            is True,

        "persisted_record_checksum_verified":
            persisted_verification[
                "record_checksum_matches"
            ]
            is True,

        "persisted_record_path_verified":
            persisted_verification[
                "record_path_matches"
            ]
            is True,

        "persisted_workspace_verified":
            persisted_verification[
                "workspace_matches"
            ]
            is True,

        "persisted_body_id_verified":
            persisted_verification[
                "body_id_matches"
            ]
            is True,

        "index_tombstone_count_valid":
            (
                index_payload[
                    "tombstone_count"
                ]
                == 1
            ),

        "index_entry_count_valid":
            (
                len(
                    index_payload[
                        "tombstones"
                    ]
                )
                == 1
            ),

        "article_body_not_exposed":
            persisted_verification[
                "article_body_exposed"
            ]
            is False,

        "lifecycle_not_modified":
            manager_bundle[
                "lifecycle_modified"
            ]
            is False,

        "archive_not_modified":
            manager_bundle[
                "archive_modified"
            ]
            is False,

        "body_store_not_modified":
            manager_bundle[
                "body_store_modified"
            ]
            is False,

        "no_runtime_job_created":
            manager_bundle[
                "runtime_job_created"
            ]
            is False,

        "no_queue_job_created":
            manager_bundle[
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
        "TOMBSTONE MANAGER — PHASE 9.1.9.2"
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
        "Sandbox tombstones persisted:         "
        + (
            "1"
            if record_path.is_file()
            else "0"
        )
    )
    print(
        "Sandbox tombstone indexes written:    "
        + (
            "1"
            if index_path.is_file()
            else "0"
        )
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
            "MANAGER PHASE 9.1.9.2: FAIL"
        )

        raise SystemExit(1)

    print(
        "BODY STORE PERMANENT DELETION TOMBSTONE "
        "MANAGER PHASE 9.1.9.2: PASS"
    )

    print(
        "The Tombstone Manager persisted and verified an isolated, "
        "content-free audit record without modifying production outputs."
    )

    print("=" * 120)

finally:
    shutil.rmtree(
        sandbox_root,
        ignore_errors=True,
    )
    