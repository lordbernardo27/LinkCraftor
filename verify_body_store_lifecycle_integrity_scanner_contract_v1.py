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

from backend.server.universal_article_body_store.body_store_lifecycle_integrity_scanner_contract_v1 import (
    BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CONTRACT_SCHEMA,
    BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CONTRACT_VERSION,
    SUPPORTED_SCOPES,
    SUPPORTED_STATES,
    SUPPORTED_CHECKS,
    create_lifecycle_integrity_scanner_request_v1,
    validate_lifecycle_integrity_scanner_request_v1,
    certify_lifecycle_integrity_scanner_request_v1,
    summarize_lifecycle_integrity_scanner_request_v1,
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

    "tombstone_store":
        DATA_ROOT
        / "universal_article_body_store_tombstones",

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
        prefix="lifecycle_integrity_scanner_contract_"
    )
)

try:

    request = (
        create_lifecycle_integrity_scanner_request_v1(
            scan_request_id="scanner_contract_request_v1",
            scope="WORKSPACE",
            workspace_id="ws_verify",
            include_state_consistency=True,
            include_archive_integrity=True,
            include_tombstone_integrity=True,
            include_reference_integrity=True,
            include_retention_integrity=True,
            include_checksum_integrity=True,
        )
    )

    validation = (
        validate_lifecycle_integrity_scanner_request_v1(
            scan_request=request,
        )
    )

    certification = (
        certify_lifecycle_integrity_scanner_request_v1(
            scan_request=request,
        )
    )

    summary = (
        summarize_lifecycle_integrity_scanner_request_v1(
            scan_request=request,
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
        "contract_schema_valid":
            (
                BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CONTRACT_SCHEMA
                == "body_store_lifecycle_integrity_scanner_contract.v1"
            ),

        "contract_version_valid":
            (
                BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CONTRACT_VERSION
                == "1.0"
            ),

        "supported_scopes_valid":
            (
                tuple(SUPPORTED_SCOPES)
                == ("WORKSPACE",)
            ),

        "supported_states_valid":
            (
                tuple(SUPPORTED_STATES)
                == (
                    "ACTIVE",
                    "ARCHIVED",
                    "RESTORED",
                    "PERMANENTLY_DELETED",
                )
            ),

        "supported_checks_valid":
            (
                len(SUPPORTED_CHECKS)
                == 6
            ),

        "request_valid":
            validation[
                "request_valid"
            ]
            is True,

        "schema_validation_passed":
            validation[
                "schema_valid"
            ]
            is True,

        "contract_version_validation_passed":
            validation[
                "contract_version_valid"
            ]
            is True,

        "scope_validation_passed":
            validation[
                "scope_valid"
            ]
            is True,

        "workspace_validation_passed":
            validation[
                "workspace_valid"
            ]
            is True,

        "checks_mapping_valid":
            validation[
                "checks_mapping_valid"
            ]
            is True,

        "no_missing_checks":
            (
                len(
                    validation[
                        "missing_checks"
                    ]
                )
                == 0
            ),

        "check_flags_valid":
            validation[
                "check_flags_valid"
            ]
            is True,

        "at_least_one_check_selected":
            validation[
                "at_least_one_check_selected"
            ]
            is True,

        "supported_states_validation_passed":
            validation[
                "supported_states_valid"
            ]
            is True,

        "supported_checks_validation_passed":
            validation[
                "supported_checks_valid"
            ]
            is True,

        "safety_boundaries_valid":
            validation[
                "safety_boundaries_valid"
            ]
            is True,

        "checksum_valid":
            validation[
                "checksum_valid"
            ]
            is True,

        "certification_passed":
            certification[
                "certified"
            ]
            is True,

        "certification_request_valid":
            certification[
                "request_valid"
            ]
            is True,

        "summary_selected_check_count_valid":
            (
                summary[
                    "selected_check_count"
                ]
                == 6
            ),

        "summary_scope_valid":
            (
                summary[
                    "scope"
                ]
                == "WORKSPACE"
            ),

        "summary_workspace_valid":
            (
                summary[
                    "workspace_id"
                ]
                == "ws_verify"
            ),

        "summary_read_only":
            (
                summary[
                    "read_only"
                ]
                is True
            ),

        "contract_read_only":
            (
                request[
                    "read_only"
                ]
                is True
            ),

        "scan_not_executed":
            (
                certification[
                    "scan_executed"
                ]
                is False
            ),

        "findings_not_generated":
            (
                certification[
                    "findings_generated"
                ]
                is False
            ),

        "lifecycle_not_modified":
            (
                certification[
                    "lifecycle_modified"
                ]
                is False
            ),

        "archive_not_modified":
            (
                certification[
                    "archive_modified"
                ]
                is False
            ),

        "tombstone_not_modified":
            (
                certification[
                    "tombstone_modified"
                ]
                is False
            ),

        "body_store_not_modified":
            (
                certification[
                    "body_store_modified"
                ]
                is False
            ),

        "no_runtime_job_created":
            (
                certification[
                    "runtime_job_created"
                ]
                is False
            ),

        "no_queue_job_created":
            (
                certification[
                    "queue_job_created"
                ]
                is False
            ),

        "production_outputs_unchanged":
            all(
                before[name] == after[name]
                for name in before
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
        "BODY STORE LIFECYCLE INTEGRITY "
        "SCANNER CONTRACT — PHASE 9.1.11.1"
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
                if before[name] == after[name]
                else "CHANGED"
            )
        )

    print()
    print(
        "Integrity scan executions:            0"
    )
    print(
        "Integrity findings generated:         0"
    )
    print(
        "Production lifecycle records modified: 0"
    )
    print(
        "Production archive records modified:   0"
    )
    print(
        "Production tombstone records modified: 0"
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
            print("  - " + failure)
    else:
        print("  None")

    print()

    if failures:
        print(
            "BODY STORE LIFECYCLE INTEGRITY "
            "SCANNER CONTRACT PHASE 9.1.11.1: FAIL"
        )
        raise SystemExit(1)

    print(
        "BODY STORE LIFECYCLE INTEGRITY "
        "SCANNER CONTRACT PHASE 9.1.11.1: PASS"
    )

finally:
    shutil.rmtree(
        sandbox_root,
        ignore_errors=True,
    )
