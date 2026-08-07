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
    PACKAGE_ROOT / "body_store_archive_repository_v1.py",
    PACKAGE_ROOT / "body_store_archive_execution_manager_v1.py",
    PACKAGE_ROOT / "body_store_expiration_manager_v1.py",
    PACKAGE_ROOT / "body_store_state_transition_engine_v1.py",
]

EXPECTED_FUNCTIONS = {
    "build_archive_repository_bundle_v1",
    "certify_archive_repository_package_v1",
}

MANAGER_FUNCTIONS = {
    "store_archive_repository",
    "load_archive_repository",
    "verify_archive_repository",
    "archive_repository_manager",
}

manager_functions = []
dependency_functions = []
syntax_failures = []

for path in TARGET_FILES:

    if not path.exists():
        continue

    try:
        tree = ast.parse(
            path.read_text(
                encoding="utf-8-sig"
            )
        )
    except Exception as exc:
        syntax_failures.append(
            f"{path.name}: {exc}"
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

            if node.name in EXPECTED_FUNCTIONS:
                dependency_functions.append(
                    (
                        path.name,
                        node.lineno,
                        node.name,
                    )
                )

            lowered = node.name.casefold()

            if any(
                term in lowered
                for term in MANAGER_FUNCTIONS
            ):
                manager_functions.append(
                    (
                        path.name,
                        node.lineno,
                        node.name,
                    )
                )

print()
print("=" * 110)
print("BODY STORE ARCHIVE REPOSITORY MANAGER DISCOVERY")
print("=" * 110)
print()

print(
    "Dependency functions:",
    len(dependency_functions),
)

for item in dependency_functions:
    print(
        f"  {item[0]}:{item[1]}:{item[2]}"
    )

print()

print(
    "Repository manager functions:",
    len(manager_functions),
)

for item in manager_functions:
    print(
        f"  {item[0]}:{item[1]}:{item[2]}"
    )

print()

print(
    "Production modified: False"
)

print()

if syntax_failures:

    print("SYNTAX FAILURES")

    for item in syntax_failures:
        print(
            "  " + item
        )

    raise SystemExit(1)

print(
    "BODY STORE ARCHIVE REPOSITORY MANAGER SCAN: PASS"
)

print("=" * 110)
