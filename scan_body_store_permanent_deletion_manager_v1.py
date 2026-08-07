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
    / "body_store_retention_policy_engine_v1.py",

    PACKAGE_ROOT
    / "body_store_expiration_manager_v1.py",

    PACKAGE_ROOT
    / "body_store_archive_repository_v1.py",

    PACKAGE_ROOT
    / "body_store_archive_repository_manager_v1.py",

    PACKAGE_ROOT
    / "body_store_archive_repository_verifier_v1.py",

    PACKAGE_ROOT
    / "body_store_archive_recovery_contract_v1.py",

    PACKAGE_ROOT
    / "body_store_archive_recovery_manager_v1.py",

    PACKAGE_ROOT
    / "body_store_archive_recovery_verifier_v1.py",

    PACKAGE_ROOT
    / "body_store_lifecycle_state_manager_v1.py",

    PACKAGE_ROOT
    / "body_store_state_transition_engine_v1.py",
]

EXPECTED_DEPENDENCIES = {
    "evaluate_body_store_deletion_eligibility_v1",
    "evaluate_body_store_expiration_v1",
    "verify_archive_repository_v1",
    "load_archive_repository_v1",
}

DELETION_FUNCTION_TERMS = {
    "permanent_delete",
    "permanent_deletion",
    "delete_archive",
    "delete_body_store",
    "purge_archive",
    "purge_body",
    "destroy_archive",
    "destroy_body",
}

DELETION_FIELDS = {
    "deletion_id",
    "deletion_status",
    "deletion_reason",
    "deleted_at",
    "deleted_by",
    "deletion_verified",
    "deletion_eligible",
    "permanent_deletion",
}

dependency_functions = []
deletion_functions = []
deletion_fields = set()
filesystem_delete_calls = []
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
                for term in DELETION_FUNCTION_TERMS
            ):
                deletion_functions.append(
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
                in DELETION_FIELDS
            ):
                deletion_fields.add(
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
                "unlink",
                "rmdir",
                "rmtree",
                "remove",
            }:
                filesystem_delete_calls.append(
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


manager_path = (
    PACKAGE_ROOT
    / "body_store_permanent_deletion_manager_v1.py"
)

manager_exists = (
    manager_path.is_file()
)

found_dependencies = {
    item[
        "name"
    ]
    for item in dependency_functions
}

missing_dependencies = sorted(
    EXPECTED_DEPENDENCIES
    - found_dependencies
)


if manager_exists:
    classification = (
        "BODY_STORE_PERMANENT_DELETION_MANAGER_EXISTS"
    )

elif deletion_functions:
    classification = (
        "PARTIAL_PERMANENT_DELETION_LOGIC_FOUND"
    )

elif not missing_dependencies:
    classification = (
        "PERMANENT_DELETION_DEPENDENCIES_READY"
    )

else:
    classification = (
        "PERMANENT_DELETION_DEPENDENCIES_INCOMPLETE"
    )


print()
print("=" * 118)
print(
    "BODY STORE PERMANENT DELETION MANAGER — READ-ONLY DISCOVERY"
)
print("=" * 118)
print()

print(
    "Classification:",
    classification,
)

print()

print(
    "Dedicated Permanent Deletion Manager exists:",
    manager_exists,
)

print()

print(
    "Dependency functions found:",
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
    "Permanent deletion functions found:",
    len(
        deletion_functions
    ),
)

for item in deletion_functions:
    print(
        f"  {item['path']}:{item['line']}:{item['name']}"
    )

print()

print(
    "Permanent deletion fields found:",
    len(
        deletion_fields
    ),
)

for item in sorted(
    deletion_fields
):
    print(
        "  "
        + item
    )

print()

print(
    "Filesystem delete references:",
    len(
        filesystem_delete_calls
    ),
)

for item in filesystem_delete_calls:
    print(
        f"  {item['path']}:{item['line']}:{item['call']}"
    )

print()

print(
    "Missing scanned files:",
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
        "BODY STORE PERMANENT DELETION MANAGER SCAN: FAIL"
    )

    raise SystemExit(1)

print(
    "BODY STORE PERMANENT DELETION MANAGER SCAN: PASS"
)

print("=" * 118)
