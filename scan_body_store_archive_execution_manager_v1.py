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
    / "body_store_archive_manager_v1.py",

    PACKAGE_ROOT
    / "body_store_lifecycle_state_manager_v1.py",

    PACKAGE_ROOT
    / "body_store_state_transition_engine_v1.py",

    PACKAGE_ROOT
    / "body_store_manager_v1.py",

    PACKAGE_ROOT
    / "body_store_repository_v1.py",

    PACKAGE_ROOT
    / "body_store_runtime_v1.py",

    PACKAGE_ROOT
    / "body_store_worker_v1.py",

    PACKAGE_ROOT
    / "body_store_queue_core_v1.py",
]

EXPECTED_DEPENDENCIES = {
    "evaluate_body_store_archive_eligibility_v1",
    "transition_body_store_lifecycle_state_v1",
}

ARCHIVE_EXECUTION_FUNCTION_TERMS = {
    "execute_archive",
    "archive_execution",
    "perform_archive",
    "commit_archive",
    "archive_body",
    "move_to_archive",
}

ARCHIVE_EXECUTION_FIELDS = {
    "archive_execution_id",
    "archive_location",
    "archive_reference",
    "archive_checksum",
    "archive_verified",
    "physical_archive_performed",
    "lifecycle_transition_performed",
}

dependency_functions = []
execution_functions = []
execution_fields = set()
filesystem_calls = []
syntax_failures = []
missing_files = []


for path in TARGET_FILES:
    if not path.is_file():
        missing_files.append(
            path.relative_to(
                PROJECT_ROOT
            ).as_posix()
        )
        continue

    try:
        source = path.read_text(
            encoding="utf-8-sig",
            errors="strict",
        )

        tree = ast.parse(
            source,
            filename=str(
                path
            ),
        )

    except Exception as exc:
        syntax_failures.append(
            f"{path.relative_to(PROJECT_ROOT)} : {exc}"
        )
        continue

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            if node.name in EXPECTED_DEPENDENCIES:
                dependency_functions.append(
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

            lowered_name = node.name.casefold()

            if any(
                term in lowered_name
                for term in ARCHIVE_EXECUTION_FUNCTION_TERMS
            ):
                execution_functions.append(
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
                and node.value
                in ARCHIVE_EXECUTION_FIELDS
            ):
                execution_fields.add(
                    node.value
                )

        elif isinstance(
            node,
            ast.Call,
        ):
            call_name = ""

            if isinstance(
                node.func,
                ast.Name,
            ):
                call_name = node.func.id

            elif isinstance(
                node.func,
                ast.Attribute,
            ):
                call_name = node.func.attr

            if call_name in {
                "write_text",
                "write_bytes",
                "mkdir",
                "replace",
                "rename",
                "unlink",
                "copy",
                "copy2",
                "move",
            }:
                filesystem_calls.append(
                    {
                        "path":
                            path.relative_to(
                                PROJECT_ROOT
                            ).as_posix(),

                        "line":
                            node.lineno,

                        "call":
                            call_name,
                    }
                )


dedicated_execution_path = (
    PACKAGE_ROOT
    / "body_store_archive_execution_manager_v1.py"
)

dedicated_execution_exists = (
    dedicated_execution_path.is_file()
)

found_dependency_names = {
    item[
        "name"
    ]
    for item in dependency_functions
}

missing_dependencies = sorted(
    EXPECTED_DEPENDENCIES
    - found_dependency_names
)


if dedicated_execution_exists:
    classification = (
        "BODY_STORE_ARCHIVE_EXECUTION_MANAGER_EXISTS"
    )

elif execution_functions:
    classification = (
        "PARTIAL_ARCHIVE_EXECUTION_LOGIC_FOUND"
    )

elif not missing_dependencies:
    classification = (
        "ARCHIVE_EXECUTION_DEPENDENCIES_READY"
    )

else:
    classification = (
        "ARCHIVE_EXECUTION_DEPENDENCIES_INCOMPLETE"
    )


print()
print("=" * 116)
print(
    "BODY STORE ARCHIVE EXECUTION MANAGER — READ-ONLY DISCOVERY"
)
print("=" * 116)
print()

print(
    "Classification:",
    classification,
)

print()

print(
    "Dedicated Archive Execution Manager exists:",
    dedicated_execution_exists,
)

print()

print(
    "Required dependency functions found:",
    len(
        dependency_functions
    ),
)

for item in dependency_functions:
    print(
        f"  {item['path']}:{item['line']}:{item['name']}"
    )

print()

print(
    "Missing dependency functions:",
    len(
        missing_dependencies
    ),
)

if missing_dependencies:
    for item in missing_dependencies:
        print(
            "  "
            + item
        )
else:
    print(
        "  None"
    )

print()

print(
    "Existing archive execution functions:",
    len(
        execution_functions
    ),
)

for item in execution_functions:
    print(
        f"  {item['path']}:{item['line']}:{item['name']}"
    )

print()

print(
    "Archive execution fields found:",
    len(
        execution_fields
    ),
)

for item in sorted(
    execution_fields
):
    print(
        "  "
        + item
    )

print()

print(
    "Filesystem-operation references:",
    len(
        filesystem_calls
    ),
)

for item in filesystem_calls:
    print(
        f"  {item['path']}:{item['line']}:{item['call']}"
    )

print()

print(
    "Missing target files:",
    len(
        missing_files
    ),
)

if missing_files:
    for item in missing_files:
        print(
            "  "
            + item
        )
else:
    print(
        "  None"
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
        "BODY STORE ARCHIVE EXECUTION MANAGER SCAN: FAIL"
    )
    raise SystemExit(1)

print(
    "BODY STORE ARCHIVE EXECUTION MANAGER SCAN: PASS"
)

print("=" * 116)
