from __future__ import annotations

import hashlib
import inspect
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


from backend.server.universal_article_body_store.body_store_lifecycle_repair_executor_engine_v1 import (
    LifecycleRepairExecutorEngineError,
    calculate_lifecycle_repair_executor_engine_checksum_v1,
    execute_lifecycle_repair_plan_v1,
    prepare_lifecycle_repair_execution_v1,
    validate_lifecycle_repair_execution_context_v1,
)

from backend.server.universal_article_body_store.body_store_lifecycle_repair_executor_contract_v1 import (
    create_lifecycle_repair_execution_authorization_v1,
    create_lifecycle_repair_execution_request_v1,
)

from backend.server.universal_article_body_store.body_store_lifecycle_repair_planner_contract_v1 import (
    create_lifecycle_repair_planner_request_v1,
)

from backend.server.universal_article_body_store.body_store_lifecycle_repair_planner_engine_v1 import (
    build_lifecycle_repair_plan_v1,
)

from backend.server.universal_article_body_store.body_store_lifecycle_repair_planner_certification_v1 import (
    build_lifecycle_repair_planner_certification_bundle_v1,
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
        / "universal_knowledge_queue",

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
        / "universal_unified_content_document",

    "wuc":
        DATA_ROOT
        / "website_unified_content",
}


def fingerprint(
    path: Path,
) -> str:

    if not path.exists():
        return "ABSENT"

    digest = hashlib.sha256()

    if path.is_file():
        digest.update(
            path.name.encode(
                "utf-8"
            )
        )

        digest.update(
            path.read_bytes()
        )

        return digest.hexdigest()

    files = sorted(
        item
        for item in path.rglob("*")
        if item.is_file()
    )

    for file_path in files:

        relative_path = file_path.relative_to(
            path
        )

        digest.update(
            str(
                relative_path
            ).replace(
                "\\",
                "/",
            ).encode(
                "utf-8"
            )
        )

        digest.update(
            file_path.read_bytes()
        )

    return digest.hexdigest()


production_before = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED.items()
}


print()
print("=" * 120)
print(
    "LIFECYCLE REPAIR EXECUTOR ENGINE "
    "VERIFIER — PHASE 9.1.13.2"
)
print("=" * 120)
print()

print("ENGINE IMPORTS: PASS")
print()

print("EXACT ENGINE FUNCTION SIGNATURES")
print()

print(
    "validate_lifecycle_repair_execution_context_v1"
)
print(
    inspect.signature(
        validate_lifecycle_repair_execution_context_v1
    )
)

print()

print(
    "prepare_lifecycle_repair_execution_v1"
)
print(
    inspect.signature(
        prepare_lifecycle_repair_execution_v1
    )
)

print()

print(
    "execute_lifecycle_repair_plan_v1"
)
print(
    inspect.signature(
        execute_lifecycle_repair_plan_v1
    )
)

print()

print(
    "calculate_lifecycle_repair_executor_engine_checksum_v1"
)
print(
    inspect.signature(
        calculate_lifecycle_repair_executor_engine_checksum_v1
    )
)

print()
print("PROTECTED PRODUCTION FINGERPRINTS CAPTURED")
print()

for name in production_before:
    print(
        f"  {name:<30}"
        + (
            "PRESENT"
            if production_before[name] != "ABSENT"
            else "ABSENT"
        )
    )

print()
print(
    "No repair was executed."
)
print(
    "No sandbox has been created yet."
)
print(
    "No production mutation was requested."
)
print("=" * 120)

print()
print("=" * 120)
print("UPSTREAM CONSTRUCTOR SIGNATURES")
print("=" * 120)
print()

constructors = (
    (
        "create_lifecycle_repair_planner_request_v1",
        create_lifecycle_repair_planner_request_v1,
    ),
    (
        "build_lifecycle_repair_plan_v1",
        build_lifecycle_repair_plan_v1,
    ),
    (
        "build_lifecycle_repair_planner_certification_bundle_v1",
        build_lifecycle_repair_planner_certification_bundle_v1,
    ),
    (
        "create_lifecycle_repair_execution_authorization_v1",
        create_lifecycle_repair_execution_authorization_v1,
    ),
    (
        "create_lifecycle_repair_execution_request_v1",
        create_lifecycle_repair_execution_request_v1,
    ),
)

for name, function in constructors:
    print(name)
    print(inspect.signature(function))
    print()

print("=" * 120)

print()
print("=" * 120)
print("UPSTREAM CONSTRUCTOR SIGNATURES")
print("=" * 120)
print()

constructors = (
    (
        "create_lifecycle_repair_planner_request_v1",
        create_lifecycle_repair_planner_request_v1,
    ),
    (
        "build_lifecycle_repair_plan_v1",
        build_lifecycle_repair_plan_v1,
    ),
    (
        "build_lifecycle_repair_planner_certification_bundle_v1",
        build_lifecycle_repair_planner_certification_bundle_v1,
    ),
    (
        "create_lifecycle_repair_execution_authorization_v1",
        create_lifecycle_repair_execution_authorization_v1,
    ),
    (
        "create_lifecycle_repair_execution_request_v1",
        create_lifecycle_repair_execution_request_v1,
    ),
)

for name, function in constructors:
    print(name)
    print(inspect.signature(function))
    print()

print("=" * 120)
