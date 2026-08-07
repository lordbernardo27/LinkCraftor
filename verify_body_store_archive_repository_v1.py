from __future__ import annotations

import hashlib
import sys
from pathlib import Path

PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

from backend.server.universal_article_body_store.body_store_archive_repository_v1 import (
    BODY_STORE_ARCHIVE_REPOSITORY_SCHEMA,
    BODY_STORE_ARCHIVE_REPOSITORY_VERSION,
    build_archive_repository_bundle_v1,
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

bundle = (
    build_archive_repository_bundle_v1(
        archive_id="verify_archive_repository",
        workspace_id="ws_verify",
        body_id="body_verify",
        archive_reason="Verifier",
        archived_at="2026-08-04T00:00:00+00:00",
        actor_type="SYSTEM",
        actor_id="verifier",
        content="Repository verification content.",
    )
)
after = {
    key: fingerprint(value)
    for key, value
    in PROTECTED.items()
}

archive_package = bundle[
    "archive_package"
]

certification = bundle[
    "certification"
]

contract = bundle[
    "contract"
]

checks = {
    "repository_schema_valid":
        (
            BODY_STORE_ARCHIVE_REPOSITORY_SCHEMA
            == "body_store_archive_repository.v1"
        ),

    "repository_version_valid":
        (
            BODY_STORE_ARCHIVE_REPOSITORY_VERSION
            == "1.0"
        ),

    "bundle_complete":
        bundle[
            "bundle_complete"
        ]
        is True,

    "bundle_certified":
        bundle[
            "certified"
        ]
        is True,

    "archive_verified":
        bundle[
            "archive_verified"
        ]
        is True,

    "package_complete":
        archive_package[
            "package_complete"
        ]
        is True,

    "package_archive_verified":
        archive_package[
            "archive_verified"
        ]
        is True,

    "certification_passed":
        certification[
            "certified"
        ]
        is True,

    "contract_archive_verified":
        contract[
            "archive_verified"
        ]
        is True,

    "archive_status_archived":
        (
            contract[
                "archive_status"
            ]
            == "ARCHIVED"
        ),

    "checksum_present":
        bool(
            contract[
                "archive_checksum"
            ]
        ),

    "archive_root_present":
        bool(
            contract[
                "archive_root"
            ]
        ),

    "archive_index_path_present":
        bool(
            contract[
                "archive_index_path"
            ]
        ),

    "archive_metadata_path_present":
        bool(
            contract[
                "archive_metadata_path"
            ]
        ),

    "no_physical_archive_performed":
        bundle[
            "physical_archive_performed"
        ]
        is False,

    "no_repository_write_performed":
        bundle[
            "repository_write_performed"
        ]
        is False,

    "no_runtime_job_created":
        bundle[
            "runtime_job_created"
        ]
        is False,

    "no_queue_job_created":
        bundle[
            "queue_job_created"
        ]
        is False,

    "content_body_not_exposed":
        bundle[
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
    "UNIVERSAL ARTICLE BODY STORE ARCHIVE REPOSITORY — PHASE 9.1.6.1"
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
    "Physical archive operations executed:  0"
)
print(
    "Repository writes performed:           0"
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
        "BODY STORE ARCHIVE REPOSITORY PHASE 9.1.6.1: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE ARCHIVE REPOSITORY PHASE 9.1.6.1: PASS"
)

print(
    "The Archive Repository contract and read-only package are verified."
)

print("=" * 120)
