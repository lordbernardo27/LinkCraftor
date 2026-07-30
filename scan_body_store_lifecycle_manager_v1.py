from __future__ import annotations

import ast
from pathlib import Path

PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

SERVER_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
)

EXCLUDED = {
    "__pycache__",
    ".venv",
    ".git",
    "node_modules",
    "runtime_backups",
    "backups",
}

KEYWORDS = {
    "lifecycle": (
        "lifecycle",
        "life_cycle",
        "body_store_lifecycle",
    ),
    "retention": (
        "retention",
        "retain",
        "retained",
    ),
    "expiration": (
        "expiration",
        "expire",
        "expired",
        "expiry",
    ),
    "archive": (
        "archive",
        "archived",
    ),
    "restore": (
        "restore",
        "restored",
        "recover",
        "recovery",
    ),
    "cleanup": (
        "cleanup",
        "clean_up",
        "purge",
        "delete_expired",
    ),
    "scheduler": (
        "schedule",
        "scheduler",
        "cron",
        "periodic",
    ),
    "certification": (
        "lifecycle_certification",
        "lifecycle_certificate",
    ),
}

matches = {k: [] for k in KEYWORDS}
manager_classes = []
manager_functions = []
syntax_failures = []

for path in SERVER_ROOT.rglob("*.py"):

    if any(
        part in EXCLUDED
        for part in path.parts
    ):
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

    lowered = source.casefold()

    for category, words in KEYWORDS.items():
        if any(
            word in lowered
            for word in words
        ):
            matches[category].append(
                path.relative_to(PROJECT_ROOT).as_posix()
            )

    for node in ast.walk(tree):

        if isinstance(node, ast.ClassDef):

            name = node.name.casefold()

            if (
                "lifecycle" in name
                or (
                    "body" in name
                    and "manager" in name
                )
            ):
                manager_classes.append(
                    f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}:{node.name}"
                )

        elif isinstance(node, ast.FunctionDef):

            name = node.name.casefold()

            if (
                "lifecycle" in name
                or "expire" in name
                or "archive" in name
                or "restore" in name
                or "cleanup" in name
            ):
                manager_functions.append(
                    f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}:{node.name}"
                )

for key in matches:
    matches[key] = sorted(set(matches[key]))

manager_classes = sorted(set(manager_classes))
manager_functions = sorted(set(manager_functions))

if manager_classes:
    classification = "BODY_STORE_LIFECYCLE_MANAGER_EXISTS"
elif any(matches.values()) or manager_functions:
    classification = "PARTIAL_LIFECYCLE_REFERENCES_FOUND"
else:
    classification = "NO_BODY_STORE_LIFECYCLE_MANAGER_FOUND"

print()
print("=" * 112)
print("BODY STORE LIFECYCLE MANAGER — READ-ONLY DISCOVERY")
print("=" * 112)
print()

print("Classification :", classification)
print()

for category in (
    "lifecycle",
    "retention",
    "expiration",
    "archive",
    "restore",
    "cleanup",
    "scheduler",
    "certification",
):
    print(f"{category.capitalize():<16}: {len(matches[category])}")
    for item in matches[category]:
        print("  ", item)
    print()

print("Manager classes :", len(manager_classes))
for item in manager_classes:
    print("  ", item)

print()

print("Manager functions :", len(manager_functions))
for item in manager_functions:
    print("  ", item)

print()
print("Production files modified : False")
print("Body Store modified       : False")
print("Runtime registrations     : 0")
print("Persistent writes         : 0")

print()
print("Syntax failures")

if syntax_failures:
    for item in syntax_failures:
        print("  ", item)
else:
    print("  None")

print()
print("BODY STORE LIFECYCLE DISCOVERY: PASS")
print("=" * 112)
