from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

PACKAGE_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "universal_article_body_store"
)

TARGET_FILES = [
    PACKAGE_ROOT
    / "body_store_lifecycle_state_manager_v1.py",

    PACKAGE_ROOT
    / "body_store_state_transition_engine_v1.py",

    PACKAGE_ROOT
    / "body_store_retention_policy_engine_v1.py",

    PACKAGE_ROOT
    / "body_store_expiration_manager_v1.py",

    PACKAGE_ROOT
    / "body_store_manager_v1.py",

    PACKAGE_ROOT
    / "body_store_repository_v1.py",

    PACKAGE_ROOT
    / "body_store_runtime_v1.py",

    PACKAGE_ROOT
    / "body_store_worker_v1.py",
]

ARCHIVE_FUNCTION_TERMS = {
    "archive",
    "archived",
    "archive_body",
    "archive_record",
    "restore_archive",
}

ARCHIVE_FIELDS = {
    "archive_id",
    "archive_status",
    "archive_reason",
    "archived_at",
    "archived_by",
    "archive_location",
    "archive_reference",
    "archive_verified",
}

EXPECTED_SUPPORT_FUNCTIONS = {
    "evaluate_body_store_expiration_v1",
    "evaluate_body_store_retention_policy_v1",
    "transition_body_store_lifecycle_state_v1",
}

archive_functions = []
archive_fields = set()
support_functions = []
syntax_failures = []


for path in TARGET_FILES:
    if not path.is_file():
        continue

    try:
        source = path.read_text(
            encoding="utf-8-sig",
            errors="strict",
        )

        tree = ast.parse(
            source,
            filename=str(path),
        )

    except Exception as exc:
        syntax_failures.append(
            f"{path.relative_to(PROJECT_ROOT)} : {exc}"
        )
        continue

    for node in ast.walk(tree):
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            lowered = node.name.casefold()

            if any(
                term in lowered
                for term in ARCHIVE_FUNCTION_TERMS
            ):
                archive_functions.append(
                    {
                        "path":
                            path.relative_to(
                                PROJECT_ROOT
                            ).as_posix(),

                        "line":
                            node.lineno,

                        "name":
                            node.name,
                    }
                )

            if node.name in EXPECTED_SUPPORT_FUNCTIONS:
                support_functions.append(
                    {
                        "path":
                            path.relative_to(
                                PROJECT_ROOT
                            ).as_posix(),

                        "line":
                            node.lineno,

                        "name":
                            node.name,
                    }
                )

        elif isinstance(
            node,
            ast.Constant,
        ):
            if (
                isinstance(
                    node.value,
                    str,
                )
                and node.value in ARCHIVE_FIELDS
            ):
                archive_fields.add(
                    node.value
                )


dedicated_manager_path = (
    PACKAGE_ROOT
    / "body_store_archive_manager_v1.py"
)

dedicated_manager_exists = (
    dedicated_manager_path.is_file()
)


if dedicated_manager_exists:
    classification = (
        "BODY_STORE_ARCHIVE_MANAGER_EXISTS"
    )

elif archive_functions or archive_fields:
    classification = (
        "PARTIAL_ARCHIVE_LOGIC_FOUND"
    )

elif support_functions:
    classification = (
        "ARCHIVE_DEPENDENCIES_EXIST"
    )

else:
    classification = (
        "NO_BODY_STORE_ARCHIVE_MANAGER_FOUND"
    )


print()
print("=" * 112)
print(
    "BODY STORE ARCHIVE MANAGER — READ-ONLY DISCOVERY"
)
print("=" * 112)
print()

print(
    "Classification:",
    classification,
)

print()

print(
    "Dedicated Archive Manager exists:",
    dedicated_manager_exists,
)

print()

print(
    "Archive functions found:",
    len(
        archive_functions
    ),
)

for item in archive_functions:
    print(
        f"  {item['path']}:{item['line']}:{item['name']}"
    )

print()

print(
    "Archive fields found:",
    len(
        archive_fields
    ),
)

for item in sorted(
    archive_fields
):
    print(
        "  "
        + item
    )

print()

print(
    "Supporting functions found:",
    len(
        support_functions
    ),
)

for item in support_functions:
    print(
        f"  {item['path']}:{item['line']}:{item['name']}"
    )

print()

print(
    "Production files modified:      False"
)

print(
    "Lifecycle records modified:     False"
)

print(
    "Body Store modified:            False"
)

print(
    "Queue modified:                 False"
)

print(
    "Runtime registrations modified: 0"
)

print()
print(
    "SYNTAX FAILURES"
)

if syntax_failures:
    for failure in syntax_failures:
        print(
            "  "
            + failure
        )

else:
    print(
        "  None"
    )

print()

if syntax_failures:
    print(
        "BODY STORE ARCHIVE MANAGER SCAN: FAIL"
    )
    raise SystemExit(1)

print(
    "BODY STORE ARCHIVE MANAGER SCAN: PASS"
)

print("=" * 112)
