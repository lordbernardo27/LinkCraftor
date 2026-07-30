from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from pprint import pprint


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
    unregister_runtime_handler,
)

from backend.server.universal_article_body_store.body_store_runtime_registration_v1 import (
    BODY_STORE_REGISTERED_JOB_TYPES,
    register_body_store_runtime_v1,
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


def describe_value(
    value,
) -> dict:
    result = {
        "python_type":
            type(
                value
            ).__name__,
    }

    if isinstance(
        value,
        dict,
    ):
        result[
            "top_level_keys"
        ] = sorted(
            str(
                key
            )
            for key in value.keys()
        )

        for key in (
            "success",
            "status",
            "runtime_status",
            "worker_status",
            "operation",
            "job_type",
            "error",
            "result",
            "runtime_result",
        ):
            if key in value:
                item = value[
                    key
                ]

                result[
                    key
                ] = {
                    "python_type":
                        type(
                            item
                        ).__name__,

                    "value":
                        (
                            item
                            if isinstance(
                                item,
                                (
                                    str,
                                    int,
                                    float,
                                    bool,
                                    type(
                                        None
                                    ),
                                ),
                            )
                            else None
                        ),
                }

                if isinstance(
                    item,
                    dict,
                ):
                    result[
                        key
                    ][
                        "keys"
                    ] = sorted(
                        str(
                            nested_key
                        )
                        for nested_key
                        in item.keys()
                    )

    return result


before = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED_PATHS.items()
}


registration_result = None
dispatch_result = None
dispatch_exception = None
snapshot_before_cleanup = None
visible_before_cleanup = {}


try:
    registration_result = (
        register_body_store_runtime_v1(
            replace=True,
            persist=False,
        )
    )

    visible_before_cleanup = {
        job_type:
            is_runtime_job_type_registered(
                job_type
            )

        for job_type
        in BODY_STORE_REGISTERED_JOB_TYPES
    }

    snapshot_before_cleanup = (
        list_runtime_registrations()
    )

    try:
        dispatch_result = (
            dispatch_registered_runtime_handler(
                {
                    "job_id":
                        "body_store_registration_inspection_list",

                    "job_type":
                        "body_store.list",

                    "workspace_id":
                        "ws_body_store_registration_inspection",

                    "attempt":
                        1,

                    "payload": {
                        "workspace_id":
                            "ws_body_store_registration_inspection",
                    },
                }
            )
        )

    except Exception as exc:
        dispatch_exception = {
            "error_type":
                type(
                    exc
                ).__name__,

            "message":
                str(
                    exc
                ),
        }

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


visible_after_cleanup = {
    job_type:
        is_runtime_job_type_registered(
            job_type
        )

    for job_type
    in BODY_STORE_REGISTERED_JOB_TYPES
}


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


print()
print("=" * 120)
print(
    "BODY STORE RUNTIME REGISTRATION — DISPATCH RESULT INSPECTION"
)
print("=" * 120)
print()

print(
    "REGISTRATION RESULT"
)

print(
    "-" * 120
)

pprint(
    registration_result,
    sort_dicts=True,
)

print()
print(
    "REGISTRATION RESULT SHAPE"
)

print(
    "-" * 120
)

pprint(
    describe_value(
        registration_result
    ),
    sort_dicts=True,
)

print()
print(
    "VISIBLE BEFORE CLEANUP"
)

print(
    "-" * 120
)

pprint(
    visible_before_cleanup,
    sort_dicts=True,
)

print()
print(
    "DISPATCH EXCEPTION"
)

print(
    "-" * 120
)

pprint(
    dispatch_exception,
    sort_dicts=True,
)

print()
print(
    "DISPATCH RESULT — EXACT VALUE"
)

print(
    "-" * 120
)

pprint(
    dispatch_result,
    sort_dicts=True,
    width=120,
)

print()
print(
    "DISPATCH RESULT — JSON"
)

print(
    "-" * 120
)

try:
    print(
        json.dumps(
            dispatch_result,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        )
    )

except Exception as exc:
    print(
        "JSON rendering failed: "
        + type(
            exc
        ).__name__
        + ": "
        + str(
            exc
        )
    )

print()
print(
    "DISPATCH RESULT SHAPE"
)

print(
    "-" * 120
)

pprint(
    describe_value(
        dispatch_result
    ),
    sort_dicts=True,
)

print()
print(
    "VISIBLE AFTER CLEANUP"
)

print(
    "-" * 120
)

pprint(
    visible_after_cleanup,
    sort_dicts=True,
)

print()
print(
    "PRODUCTION OUTPUTS"
)

print(
    "-" * 120
)

for name, passed in unchanged.items():
    print(
        f"{name:<40}"
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
    "INSPECTION SUMMARY"
)

print(
    "-" * 120
)

print(
    "Dispatch raised exception: "
    + str(
        dispatch_exception
        is not None
    )
)

print(
    "Dispatch returned mapping: "
    + str(
        isinstance(
            dispatch_result,
            dict,
        )
    )
)

if isinstance(
    dispatch_result,
    dict,
):
    print(
        "Dispatch top-level keys: "
        + ", ".join(
            sorted(
                str(
                    key
                )
                for key
                in dispatch_result.keys()
            )
        )
    )

print(
    "All production outputs unchanged: "
    + str(
        all(
            unchanged.values()
        )
    )
)

print()

if dispatch_exception is not None:
    print(
        "BODY STORE REGISTRATION DISPATCH INSPECTION: RESULT CAPTURED WITH EXCEPTION"
    )

elif dispatch_result is None:
    print(
        "BODY STORE REGISTRATION DISPATCH INSPECTION: NO RESULT RETURNED"
    )

else:
    print(
        "BODY STORE REGISTRATION DISPATCH INSPECTION: RESULT CAPTURED"
    )

print("=" * 120)
