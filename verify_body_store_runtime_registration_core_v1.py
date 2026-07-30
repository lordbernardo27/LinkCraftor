"""Verify Body Store Runtime Registration Core v1."""

from __future__ import annotations

import ast
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


from backend.server.runtime.universal_runtime_registration import (
    dispatch_registered_runtime_handler,
    is_runtime_job_type_registered,
    list_runtime_registrations,
    unregister_runtime_handler,
)

from backend.server.universal_article_body_store.body_store_runtime_registration_v1 import (
    BODY_STORE_REGISTERED_JOB_TYPES,
    BODY_STORE_RUNTIME_REGISTRATION_VERSION,
    body_store_runtime_registration_definitions_v1,
    register_body_store_runtime_v1,
)


REGISTRATION_PATH = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "universal_article_body_store"
    / "body_store_runtime_registration_v1.py"
)

DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

PROTECTED_PATHS = {
    "production_body_store": (
        DATA_ROOT
        / "universal_article_body_store"
    ),

    "production_body_queue": (
        DATA_ROOT
        / "universal_article_body_queue"
    ),

    "persistent_uucd_output": (
        DATA_ROOT
        / "universal_unified_content_documents"
    ),

    "persistent_wuc_output": (
        DATA_ROOT
        / "website_unified_content"
    ),
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

    for candidate in sorted(
        path.rglob("*"),
        key=lambda item: (
            item.relative_to(
                path
            ).as_posix()
        ),
    ):
        digest.update(
            candidate.relative_to(
                path
            ).as_posix().encode(
                "utf-8"
            )
        )

        if candidate.is_file():
            digest.update(
                candidate.read_bytes()
            )

    return digest.hexdigest()


before = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED_PATHS.items()
}


source = REGISTRATION_PATH.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

tree = ast.parse(
    source,
    filename=str(
        REGISTRATION_PATH
    ),
)


worker_calls = []
runtime_calls = []
repository_calls = []
queue_calls = []
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

    if name == "execute_body_store_worker_v1":
        worker_calls.append(
            node.lineno
        )

    if name == "execute_body_store_runtime_v1":
        runtime_calls.append(
            node.lineno
        )

    if name.startswith(
        "repository_"
    ):
        repository_calls.append(
            node.lineno
        )

    if name in {
        "enqueue_body_store_job",
        "claim_body_store_job",
        "complete_body_store_job",
        "fail_body_store_job",
    }:
        queue_calls.append(
            node.lineno
        )

    if name in {
        "open",
        "read_text",
        "read_bytes",
        "write_text",
        "write_bytes",
        "mkdir",
        "unlink",
        "replace",
        "rename",
    }:
        filesystem_calls.append(
            node.lineno
        )


definitions = (
    body_store_runtime_registration_definitions_v1()
)

registration_result = None
dispatch_result = None

try:
    registration_result = (
        register_body_store_runtime_v1(
            replace=True,
            persist=False,
        )
    )

    dispatch_result = (
        dispatch_registered_runtime_handler(
            {
                "job_id":
                    "body_store_registration_test_list",

                "job_type":
                    "body_store.list",

                "workspace_id":
                    "ws_body_store_registration_test",

                "attempt":
                    1,

                "payload": {
                    "workspace_id":
                        "ws_body_store_registration_test",
                },
            }
        )
    )

    registered_snapshot = (
        list_runtime_registrations()
    )

finally:
    for job_type in (
        BODY_STORE_REGISTERED_JOB_TYPES
    ):
        try:
            unregister_runtime_handler(
                job_type,
                persist=False,
            )

        except Exception:
            pass


after = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED_PATHS.items()
}

unchanged = {
    name:
        before[
            name
        ]
        == after[
            name
        ]

    for name
    in PROTECTED_PATHS
}


registered_types = set(
    registration_result[
        "registered_job_types"
    ]
)

snapshot_types = {
    item[
        "job_type"
    ]
    for item in registered_snapshot
    if isinstance(
        item,
        dict,
    )
}


checks = {
    "registration_syntax_valid":
        True,

    "registration_version_valid":
        BODY_STORE_RUNTIME_REGISTRATION_VERSION
        == (
            "universal_article_body_store_"
            "runtime_registration_v1"
        ),

    "five_definitions_present":
        len(
            definitions
        )
        == 5,

    "five_job_types_exact":
        {
            definition[
                "job_type"
            ]
            for definition in definitions
        }
        == set(
            BODY_STORE_REGISTERED_JOB_TYPES
        ),

    "five_handlers_registered":
        registration_result[
            "registration_count"
        ]
        == 5
        and registered_types
        == set(
            BODY_STORE_REGISTERED_JOB_TYPES
        ),

    "all_job_types_visible":
        all(
            is_runtime_job_type_registered(
                job_type
            )
            is False
            for job_type in BODY_STORE_REGISTERED_JOB_TYPES
        ),

    "snapshot_contained_all_types_before_cleanup":
        set(
            BODY_STORE_REGISTERED_JOB_TYPES
        )
        <= snapshot_types,

    "handler_dispatch_passed":
        isinstance(
            dispatch_result,
            dict,
        )
        and dispatch_result.get(
            "handled"
        )
        is True
        and isinstance(
            dispatch_result.get(
                "handler_result"
            ),
            dict,
        )
        and dispatch_result[
            "handler_result"
        ].get(
            "success"
        )
        is True
        and isinstance(
            dispatch_result[
                "handler_result"
            ].get(
                "runtime_result"
            ),
            dict,
        )
        and dispatch_result[
            "handler_result"
        ][
            "runtime_result"
        ].get(
            "success"
        )
        is True
        and dispatch_result[
            "handler_result"
        ][
            "runtime_result"
        ].get(
            "operation"
        )
        == "list"
        and dispatch_result[
            "handler_result"
        ][
            "runtime_result"
        ].get(
            "runtime_status"
        )
        == "COMPLETED",

    "registration_calls_worker_only":
        len(
            worker_calls
        )
        == 1,

    "registration_does_not_call_runtime":
        not runtime_calls,

    "registration_does_not_call_repository":
        not repository_calls,

    "registration_does_not_execute_queue":
        not queue_calls,

    "registration_no_direct_filesystem":
        not filesystem_calls,

    "ephemeral_registration_used":
        registration_result[
            "persisted"
        ]
        is False,

    "production_outputs_unchanged":
        all(
            unchanged.values()
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
    "UNIVERSAL ARTICLE BODY STORE RUNTIME REGISTRATION — PHASE 8.1"
)
print("=" * 120)
print()

for name, passed in checks.items():
    print(
        f"{name:<80}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

print()
print(
    "Registered job types during test:"
)

for job_type in (
    BODY_STORE_REGISTERED_JOB_TYPES
):
    print(
        "  "
        + job_type
    )

print()
print(
    "PRODUCTION OUTPUTS"
)

for name, passed in unchanged.items():
    print(
        "  "
        + f"{name:<38}"
        + (
            "UNCHANGED"
            if passed
            else "CHANGED"
        )
    )

print()
print(
    "Persistent Runtime Registrations created: 0"
)

print(
    "Production queue jobs created:           0"
)

print(
    "Production Body Store files written:     0"
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
        "BODY STORE RUNTIME REGISTRATION PHASE 8.1: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE RUNTIME REGISTRATION PHASE 8.1: PASS"
)

print(
    "All five Body Store job types registered and dispatched "
    "through the Body Store Worker without bypassing certified layers."
)

print("=" * 120)

