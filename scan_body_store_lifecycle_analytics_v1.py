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
    / "body_store_archive_repository_manager_v1.py",

    PACKAGE_ROOT
    / "body_store_archive_recovery_manager_v1.py",

    PACKAGE_ROOT
    / "body_store_permanent_deletion_manager_v1.py",

    PACKAGE_ROOT
    / "body_store_permanent_deletion_tombstone_manager_v1.py",
]

ANALYTICS_FUNCTION_TERMS = {
    "analytics",
    "metric",
    "statistics",
    "summary",
    "aggregate",
    "count_by_state",
    "lifecycle_report",
}

EXPECTED_DEPENDENCIES = {
    "load_tombstone_index_v1",
    "load_archive_repository",
}

STATE_FIELDS = {
    "ACTIVE",
    "ARCHIVED",
    "PERMANENTLY_DELETED",
    "RESTORED",
    "RECOVERED",
}

analytics_functions = []
dependency_functions = []
state_values = set()
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
                for term in ANALYTICS_FUNCTION_TERMS
            ):
                analytics_functions.append(
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
                in STATE_FIELDS
            ):
                state_values.add(
                    node.value
                )


analytics_path = (
    PACKAGE_ROOT
    / "body_store_lifecycle_analytics_contract_v1.py"
)

analytics_exists = analytics_path.is_file()

if analytics_exists:
    classification = (
        "LIFECYCLE_ANALYTICS_CONTRACT_EXISTS"
    )

elif analytics_functions:
    classification = (
        "PARTIAL_LIFECYCLE_ANALYTICS_LOGIC_FOUND"
    )

else:
    classification = (
        "LIFECYCLE_ANALYTICS_READY_FOR_CONTRACT"
    )


print()
print("=" * 118)
print(
    "BODY STORE LIFECYCLE ANALYTICS — READ-ONLY DISCOVERY"
)
print("=" * 118)
print()

print(
    "Classification:",
    classification,
)

print()

print(
    "Dedicated Analytics Contract exists:",
    analytics_exists,
)

print()

print(
    "Analytics-related functions found:",
    len(
        analytics_functions
    ),
)

for item in analytics_functions:
    print(
        f"  {item['path']}:{item['line']}:{item['name']}"
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
    "Lifecycle state values found:",
    len(
        state_values
    ),
)

for item in sorted(
    state_values
):
    print(
        "  "
        + item
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
    "Archive Store modified:         False"
)
print(
    "Tombstone Store modified:       False"
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
        "BODY STORE LIFECYCLE ANALYTICS SCAN: FAIL"
    )
    raise SystemExit(1)

print(
    "BODY STORE LIFECYCLE ANALYTICS SCAN: PASS"
)

print("=" * 118)
