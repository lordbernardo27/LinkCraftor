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
    / "body_store_archive_execution_manager_v1.py",

    PACKAGE_ROOT
    / "body_store_lifecycle_state_manager_v1.py",

    PACKAGE_ROOT
    / "body_store_state_transition_engine_v1.py",

    PACKAGE_ROOT
    / "body_store_repository_v1.py",

    PACKAGE_ROOT
    / "body_store_manager_v1.py",
]

EXPECTED_DEPENDENCIES = {
    "evaluate_body_store_archive_eligibility_v1",
    "build_body_store_archive_execution_bundle_v1",
}

ARCHIVE_REPOSITORY_FUNCTION_TERMS = {
    "archive_repository",
    "store_archive",
    "write_archive",
    "read_archive",
    "list_archives",
    "verify_archive",
}

ARCHIVE_REPOSITORY_FIELDS = {
    "archive_id",
    "archive_reference",
    "archive_path",
    "archive_checksum",
    "archive_created_at",
    "archive_verified",
    "archive_metadata",
}

dependency_functions = []
repository_functions = []
repository_fields = set()
filesystem_operations = []
missing_files = []
syntax_failures = []


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
                for term in ARCHIVE_REPOSITORY_FUNCTION_TERMS
            ):
                repository_functions.append(
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
                in ARCHIVE_REPOSITORY_FIELDS
            ):
                repository_fields.add(
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
                "rename",
                "unlink",
                "copy",
                "copy2",
                "move",
            }:
                filesystem_operations.append(
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


repository_path = (
    PACKAGE_ROOT
    / "body_store_archive_repository_v1.py"
)

repository_exists = repository_path.is_file()

found_dependencies = {
    item["name"]
    for item in dependency_functions
}

missing_dependencies = sorted(
    EXPECTED_DEPENDENCIES
    - found_dependencies
)


if repository_exists:
    classification = (
        "BODY_STORE_ARCHIVE_REPOSITORY_EXISTS"
    )

elif repository_functions:
    classification = (
        "PARTIAL_ARCHIVE_REPOSITORY_LOGIC_FOUND"
    )

elif not missing_dependencies:
    classification = (
        "ARCHIVE_REPOSITORY_DEPENDENCIES_READY"
    )

else:
    classification = (
        "ARCHIVE_REPOSITORY_DEPENDENCIES_INCOMPLETE"
    )


print()
print("=" * 116)
print(
    "BODY STORE ARCHIVE REPOSITORY — READ-ONLY DISCOVERY"
)
print("=" * 116)
print()

print(
    "Classification:",
    classification,
)

print()

print(
    "Dedicated Archive Repository exists:",
    repository_exists,
)

print()

print(
    "Dependency functions found:",
    len(dependency_functions),
)

for item in dependency_functions:
    print(
        f"  {item['path']}:{item['line']}:{item['name']}"
    )

print()

print(
    "Missing dependency functions:",
    len(missing_dependencies),
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
    "Archive repository functions found:",
    len(repository_functions),
)

for item in repository_functions:
    print(
        f"  {item['path']}:{item['line']}:{item['name']}"
    )

print()

print(
    "Archive repository fields found:",
    len(repository_fields),
)

for item in sorted(repository_fields):
    print(
        "  "
        + item
    )

print()

print(
    "Filesystem-operation references:",
    len(filesystem_operations),
)

for item in filesystem_operations:
    print(
        f"  {item['path']}:{item['line']}:{item['call']}"
    )

print()

print(
    "Missing scanned files:",
    len(missing_files),
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
    "Archive Store modified:         False"
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
        "BODY STORE ARCHIVE REPOSITORY SCAN: FAIL"
    )
    raise SystemExit(1)

print(
    "BODY STORE ARCHIVE REPOSITORY SCAN: PASS"
)

print("=" * 116)
