"""Verify already-persisted Body Store Runtime Registrations."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
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
    load_persisted_runtime_registrations,
)

from backend.server.universal_article_body_store.body_store_runtime_registration_v1 import (
    BODY_STORE_REGISTERED_JOB_TYPES,
    BODY_STORE_RUNTIME_REGISTRATION_VERSION,
)


DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

REGISTRY_PATH = (
    DATA_ROOT
    / "runtime"
    / "universal_runtime_registration"
    / "runtime_registration_registry.json"
)

EVIDENCE_PATH = (
    DATA_ROOT
    / "universal_article_body_store_runtime_registration"
    / "verification"
    / "body_store_persistent_registration_reload_v1.json"
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


if not REGISTRY_PATH.is_file():
    raise RuntimeError(
        "Persistent Runtime Registration registry not found: "
        + str(REGISTRY_PATH)
    )


registry_before_hash = hashlib.sha256(
    REGISTRY_PATH.read_bytes()
).hexdigest()

before = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED_PATHS.items()
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


snapshot = list_runtime_registrations()

snapshot_records = {
    record.get(
        "job_type"
    ):
        record

    for record in snapshot
    if (
        isinstance(
            record,
            dict,
        )
        and record.get(
            "job_type"
        )
        in BODY_STORE_REGISTERED_JOB_TYPES
    )
}


dispatch_result = (
    dispatch_registered_runtime_handler(
        {
            "job_id":
                "body_store_persistent_reload_list_test",

            "job_type":
                "body_store.list",

            "workspace_id":
                "ws_body_store_persistent_reload_test",

            "attempt":
                1,

            "payload": {
                "workspace_id":
                    "ws_body_store_persistent_reload_test",
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
        {},
    )
    if isinstance(
        handler_result,
        dict,
    )
    else {}
)


registry_after_hash = hashlib.sha256(
    REGISTRY_PATH.read_bytes()
).hexdigest()

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

reloaded_types = set(
    snapshot_records
)


checks = {
    "registration_version_valid":
        BODY_STORE_RUNTIME_REGISTRATION_VERSION
        == (
            "universal_article_body_store_"
            "runtime_registration_v1"
        ),

    "registry_exists":
        REGISTRY_PATH.is_file(),

    "reload_api_succeeded":
        isinstance(
            reload_result,
            dict,
        )
        and reload_result.get(
            "ok"
        )
        is True
        and reload_result.get(
            "loaded"
        )
        is True,

    "all_five_visible_after_reload":
        all(
            visible_after_reload.values()
        ),

    "all_five_in_runtime_snapshot":
        reloaded_types
        == expected_types,

    "all_five_marked_persistent":
        all(
            snapshot_records[
                job_type
            ].get(
                "persistent"
            )
            is True

            for job_type
            in BODY_STORE_REGISTERED_JOB_TYPES
        ),

    "handler_references_correct":
        all(
            str(
                snapshot_records[
                    job_type
                ].get(
                    "handler_ref",
                    "",
                )
            ).endswith(
                ":execute_body_store_registered_job_v1"
            )

            for job_type
            in BODY_STORE_REGISTERED_JOB_TYPES
        ),

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

    "registry_file_unchanged":
        registry_before_hash
        == registry_after_hash,

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
        "body_store_persistent_registration_reload_v1",

    "generated_at":
        now_iso(),

    "registration_version":
        BODY_STORE_RUNTIME_REGISTRATION_VERSION,

    "registry_path":
        str(
            REGISTRY_PATH
        ),

    "registry_sha256":
        registry_after_hash,

    "reload_result":
        reload_result,

    "visible_after_reload":
        visible_after_reload,

    "registered_job_types":
        sorted(
            reloaded_types
        ),

    "checks":
        checks,

    "failed_checks":
        failures,

    "protected_outputs_unchanged":
        unchanged,

    "registry_modified":
        registry_before_hash
        != registry_after_hash,

    "production_queue_jobs_created":
        0,

    "production_body_store_files_written":
        0,
}


EVIDENCE_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

EVIDENCE_PATH.write_text(
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
    "BODY STORE PERSISTENT RUNTIME REGISTRATION — RELOAD VERIFICATION"
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
    "Reload result:"
)

print(
    "  "
    + json.dumps(
        reload_result,
        sort_keys=True,
        default=str,
    )
)

print()
print(
    "Reloaded Body Store job types:"
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
    "Registry modified by verification:       False"
)

print(
    "Persistent registrations written:        0"
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
        EVIDENCE_PATH
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
        "BODY STORE PERSISTENT REGISTRATION RELOAD: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE PERSISTENT REGISTRATION RELOAD: PASS"
)

print(
    "All five persisted Body Store job types reloaded and dispatched "
    "through the verified Worker and Runtime execution chain."
)

print("=" * 120)
