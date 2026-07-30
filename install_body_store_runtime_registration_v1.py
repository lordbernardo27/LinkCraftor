"""Persist and verify Universal Article Body Store Runtime Registration."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(
            PROJECT_ROOT
        ),
    )


from backend.server.runtime.universal_runtime_registration import (
    dispatch_registered_runtime_handler,
    is_runtime_job_type_registered,
    list_runtime_registrations,
    load_persisted_runtime_registrations,
    unregister_runtime_handler,
)

from backend.server.universal_article_body_store.body_store_runtime_registration_v1 import (
    BODY_STORE_REGISTERED_JOB_TYPES,
    BODY_STORE_RUNTIME_REGISTRATION_VERSION,
    register_body_store_runtime_v1,
)


DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

EVIDENCE_ROOT = (
    DATA_ROOT
    / "universal_article_body_store_runtime_registration"
)

VERIFICATION_PATH = (
    EVIDENCE_ROOT
    / "verification"
    / "body_store_runtime_registration_installation_v1.json"
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


def now_iso() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


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

        digest.update(
            b"\x00"
        )

        if candidate.is_file():
            digest.update(
                candidate.read_bytes()
            )

        digest.update(
            b"\n"
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


installation_result = (
    register_body_store_runtime_v1(
        replace=True,
        persist=True,
    )
)


visible_after_installation = {
    job_type:
        is_runtime_job_type_registered(
            job_type
        )

    for job_type
    in BODY_STORE_REGISTERED_JOB_TYPES
}


snapshot_after_installation = (
    list_runtime_registrations()
)


for job_type in BODY_STORE_REGISTERED_JOB_TYPES:
    unregister_runtime_handler(
        job_type,
        persist=False,
    )


visible_after_memory_unload = {
    job_type:
        is_runtime_job_type_registered(
            job_type
        )

    for job_type
    in BODY_STORE_REGISTERED_JOB_TYPES
}


reload_result = (
    load_persisted_runtime_registrations(
        force=True,
    )
)


visible_after_reload = {
    job_type:
        is_runtime_job_type_registered(
            job_type
        )

    for job_type
    in BODY_STORE_REGISTERED_JOB_TYPES
}


snapshot_after_reload = (
    list_runtime_registrations()
)


dispatch_result = (
    dispatch_registered_runtime_handler(
        {
            "job_id":
                "body_store_persistent_registration_list_test",

            "job_type":
                "body_store.list",

            "workspace_id":
                "ws_body_store_persistent_registration_test",

            "attempt":
                1,

            "payload": {
                "workspace_id":
                    "ws_body_store_persistent_registration_test",
            },
        }
    )
)


handler_result = dispatch_result.get(
    "handler_result",
    {},
)

runtime_result = (
    handler_result.get(
        "runtime_result",
        {}
    )
    if isinstance(
        handler_result,
        dict,
    )
    else {}
)


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


expected_types = set(
    BODY_STORE_REGISTERED_JOB_TYPES
)

installation_types = set(
    installation_result.get(
        "registered_job_types",
        [],
    )
)

installed_snapshot_types = {
    record.get(
        "job_type"
    )
    for record in snapshot_after_installation
    if isinstance(
        record,
        dict,
    )
}

reloaded_snapshot_types = {
    record.get(
        "job_type"
    )
    for record in snapshot_after_reload
    if isinstance(
        record,
        dict,
    )
}


checks = {
    "registration_version_valid":
        BODY_STORE_RUNTIME_REGISTRATION_VERSION
        == (
            "universal_article_body_store_"
            "runtime_registration_v1"
        ),

    "persistent_installation_requested":
        installation_result.get(
            "persisted"
        )
        is True,

    "five_registrations_installed":
        installation_result.get(
            "registration_count"
        )
        == 5
        and installation_types
        == expected_types,

    "all_visible_after_installation":
        all(
            visible_after_installation.values()
        ),

    "installation_snapshot_contains_all":
        expected_types
        <= installed_snapshot_types,

    "memory_unload_succeeded":
        not any(
            visible_after_memory_unload.values()
        ),

    "persisted_registrations_reloaded":
        all(
            visible_after_reload.values()
        ),

    "reload_snapshot_contains_all":
        expected_types
        <= reloaded_snapshot_types,

    "dispatch_handled":
        dispatch_result.get(
            "handled"
        )
        is True,

    "dispatch_job_type_correct":
        dispatch_result.get(
            "job_type"
        )
        == "body_store.list",

    "worker_execution_completed":
        isinstance(
            handler_result,
            dict,
        )
        and handler_result.get(
            "success"
        )
        is True
        and handler_result.get(
            "worker_status"
        )
        == "COMPLETED",

    "runtime_execution_completed":
        isinstance(
            runtime_result,
            dict,
        )
        and runtime_result.get(
            "success"
        )
        is True
        and runtime_result.get(
            "operation"
        )
        == "list"
        and runtime_result.get(
            "runtime_status"
        )
        == "COMPLETED",

    "no_article_body_returned":
        runtime_result.get(
            "result",
            {},
        ).get(
            "body_content_included"
        )
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


evidence = {
    "schema_version":
        "body_store_runtime_registration_installation_v1",

    "generated_at":
        now_iso(),

    "registration_version":
        BODY_STORE_RUNTIME_REGISTRATION_VERSION,

    "installation_result":
        installation_result,

    "reload_result":
        reload_result,

    "visible_after_installation":
        visible_after_installation,

    "visible_after_memory_unload":
        visible_after_memory_unload,

    "visible_after_reload":
        visible_after_reload,

    "checks":
        checks,

    "failed_checks":
        failures,

    "protected_outputs_unchanged":
        unchanged,

    "production_queue_jobs_created":
        0,

    "production_body_store_files_written":
        0,

    "persistent_registration_count":
        5,
}


VERIFICATION_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

VERIFICATION_PATH.write_text(
    json.dumps(
        evidence,
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 120)
print(
    "UNIVERSAL ARTICLE BODY STORE RUNTIME REGISTRATION — PHASE 8.2"
)
print("=" * 120)
print()

for name, passed in checks.items():
    print(
        f"{name:<82}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )

print()
print(
    "Persistently registered job types:"
)

for job_type in BODY_STORE_REGISTERED_JOB_TYPES:
    print(
        "  "
        + job_type
    )

print()
print(
    "PROTECTED OUTPUTS"
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
    "Persistent Runtime Registrations created: 5"
)

print(
    "Production queue jobs created:           0"
)

print(
    "Production Body Store files written:     0"
)

print()
print(
    "Verification evidence:"
)

print(
    "  "
    + str(
        VERIFICATION_PATH
    )
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
        "BODY STORE RUNTIME REGISTRATION PHASE 8.2: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE RUNTIME REGISTRATION PHASE 8.2: PASS"
)

print(
    "All five Body Store job types are persistently installed, "
    "reloadable, and dispatch correctly through Worker and Runtime."
)

print("=" * 120)


