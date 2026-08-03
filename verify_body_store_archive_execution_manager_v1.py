from __future__ import annotations

import ast
import hashlib
import sys
from pathlib import Path
from types import MappingProxyType

PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

from backend.server.universal_article_body_store.body_store_archive_execution_manager_v1 import (
    BODY_STORE_ARCHIVE_EXECUTION_STATUSES,
    BODY_STORE_ARCHIVE_TARGET_STATE,
    build_body_store_archive_execution_bundle_v1,
)

from backend.server.universal_article_body_store.body_store_retention_policy_contract_v1 import (
    build_body_store_retention_policy_v1,
)

MANAGER_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "universal_article_body_store"
    / "body_store_archive_execution_manager_v1.py"
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

source = MANAGER_PATH.read_text(
    encoding="utf-8-sig",
)

tree = ast.parse(
    source
)

filesystem_calls = []

for node in ast.walk(
    tree
):

    if not isinstance(
        node,
        ast.Call,
    ):
        continue

    name = ""

    if isinstance(
        node.func,
        ast.Name,
    ):
        name = node.func.id

    elif isinstance(
        node.func,
        ast.Attribute,
    ):
        name = node.func.attr

    filesystem_owner = ""

    if isinstance(
        node.func,
        ast.Attribute,
    ):
        if isinstance(
            node.func.value,
            ast.Name,
        ):
            filesystem_owner = (
                node.func.value.id
            )

    if (
        name in {
            "write_text",
            "write_bytes",
            "mkdir",
            "rename",
            "unlink",
        }
        or (
            name == "replace"
            and filesystem_owner
            in {
                "os",
                "path",
                "Path",
            }
        )
    ):
        filesystem_calls.append(
            (
                node.lineno,
                filesystem_owner,
                name,
            )
        )

policy = (
    build_body_store_retention_policy_v1(
        retention_policy_id="verify_archive_execution",
        retention_policy_name="Verify",
        lifecycle_record_id="body_lifecycle_verify",
        workspace_id="ws_verify",
        retention_class="STANDARD",
        retention_started_at="2025-01-01T00:00:00+00:00",
        retention_period_days=30,
        eligibility_reason="Verifier",
        evaluated_at="2025-01-01T00:00:00+00:00",
    )
)

bundle = (
    build_body_store_archive_execution_bundle_v1(
        policy=policy,
        lifecycle_state="ACTIVE",
        evaluated_at="2026-08-03T00:00:00+00:00",
        archive_reason="Verifier",
        actor_type="SYSTEM",
        actor_id="verifier",
        source="phase_9_1_5_2",
    )
)
after = {
    key: fingerprint(value)
    for key, value
    in PROTECTED.items()
}

checks = {

    "bundle_complete":
        bundle[
            "bundle_complete"
        ],

    "certified":
        bundle[
            "certification"
        ][
            "certified"
        ],

    "target_state":
        (
            bundle[
                "metadata"
            ][
                "target_state"
            ]
            ==
            BODY_STORE_ARCHIVE_TARGET_STATE
        ),

    "execution_status":
        (
            bundle[
                "certification"
            ][
                "summary"
            ][
                "archive_status"
            ]
            ==
            "EXECUTED"
        ),

    "immutable_bundle":
        isinstance(
            bundle,
            MappingProxyType,
        ),

    "statuses":
        (
            BODY_STORE_ARCHIVE_EXECUTION_STATUSES
            ==
            (
                "EXECUTED",
                "BLOCKED",
                "FAILED",
            )
        ),

    "no_filesystem_writes":
        len(
            filesystem_calls
        ) == 0,

    "production_unchanged":
        all(
            before[key]
            == after[key]
            for key
            in before
        ),
}

failures = [
    key
    for key, passed
    in checks.items()
    if not passed
]

print()
print("=" * 120)
print(
    "BODY STORE ARCHIVE EXECUTION MANAGER — PHASE 9.1.5.2"
)
print("=" * 120)
print()

for key, passed in checks.items():
    print(
        f"{key:<55}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

print()

print("FAILURES")

if failures:

    for item in failures:
        print(
            "  -",
            item,
        )

else:

    print(
        "  None"
    )

print()

if failures:

    print(
        "BODY STORE ARCHIVE EXECUTION MANAGER PHASE 9.1.5.2: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE ARCHIVE EXECUTION MANAGER PHASE 9.1.5.2: PASS"
)

print("=" * 120)

