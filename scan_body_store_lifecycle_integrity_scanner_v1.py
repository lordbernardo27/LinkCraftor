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

DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

EXPECTED_FILES = [
    PACKAGE_ROOT
    / "body_store_lifecycle_analytics_contract_v1.py",

    PACKAGE_ROOT
    / "body_store_lifecycle_analytics_engine_v1.py",

    PACKAGE_ROOT
    / "body_store_permanent_deletion_tombstone_manager_v1.py",

    PACKAGE_ROOT
    / "body_store_archive_repository_manager_v1.py",

    PACKAGE_ROOT
    / "body_store_permanent_deletion_manager_v1.py",
]

SCANNER_PATH = (
    PACKAGE_ROOT
    / "body_store_lifecycle_integrity_scanner_contract_v1.py"
)

STORE_PATHS = {
    "body_store":
        DATA_ROOT
        / "universal_article_body_store",

    "lifecycle_store":
        DATA_ROOT
        / "universal_article_body_store_lifecycle",

    "archive_store":
        DATA_ROOT
        / "universal_article_body_store_archive",

    "tombstone_store":
        DATA_ROOT
        / "universal_article_body_store_tombstones",
}

INTEGRITY_TERMS = (
    "integrity_scanner",
    "scan_integrity",
    "orphan",
    "broken_reference",
    "state_mismatch",
    "checksum_mismatch",
    "missing_archive",
    "missing_tombstone",
)

missing_files = []
syntax_failures = []
integrity_functions = []
discovered_states = set()


for path in EXPECTED_FILES:
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
        )

        tree = ast.parse(
            source,
            filename=str(path),
        )

    except Exception as exc:
        syntax_failures.append(
            f"{path.relative_to(PROJECT_ROOT)}: {exc}"
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
                for term in INTEGRITY_TERMS
            ):
                integrity_functions.append(
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
                in {
                    "ACTIVE",
                    "ARCHIVED",
                    "RESTORED",
                    "PERMANENTLY_DELETED",
                }
            ):
                discovered_states.add(
                    node.value
                )


if SCANNER_PATH.is_file():
    classification = (
        "LIFECYCLE_INTEGRITY_SCANNER_CONTRACT_EXISTS"
    )

elif integrity_functions:
    classification = (
        "PARTIAL_LIFECYCLE_INTEGRITY_LOGIC_FOUND"
    )

else:
    classification = (
        "LIFECYCLE_INTEGRITY_SCANNER_READY_FOR_CONTRACT"
    )


print()
print("=" * 120)
print(
    "UNIVERSAL ARTICLE BODY STORE LIFECYCLE "
    "INTEGRITY SCANNER — READ-ONLY DISCOVERY"
)
print("=" * 120)
print()

print(
    "Classification:",
    classification,
)

print()
print(
    "Dedicated Scanner Contract exists:",
    SCANNER_PATH.is_file(),
)

print()
print(
    "Integrity-related functions found:",
    len(
        integrity_functions
    ),
)

if integrity_functions:
    for item in integrity_functions:
        print(
            f"  {item['path']}:{item['line']}:{item['name']}"
        )
else:
    print(
        "  None"
    )

print()
print(
    "Lifecycle states discovered:",
    len(
        discovered_states
    ),
)

for state in sorted(
    discovered_states
):
    print(
        "  "
        + state
    )

print()
print("SOURCE STORES")

for name, path in STORE_PATHS.items():
    print(
        "  "
        + f"{name:<24}"
        + (
            "PRESENT"
            if path.exists()
            else "ABSENT"
        )
    )

print()
print(
    "Missing expected files:",
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
print("SYNTAX FAILURES")

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
print(
    "Production files modified:      False"
)
print(
    "Lifecycle records modified:     False"
)
print(
    "Archive records modified:       False"
)
print(
    "Tombstone records modified:     False"
)
print(
    "Body Store files modified:      False"
)
print(
    "Queue modified:                 False"
)
print(
    "Runtime registrations modified: 0"
)

print()

if syntax_failures:
    print(
        "LIFECYCLE INTEGRITY SCANNER DISCOVERY: FAIL"
    )

    raise SystemExit(1)

print(
    "LIFECYCLE INTEGRITY SCANNER DISCOVERY: PASS"
)

print("=" * 120)
