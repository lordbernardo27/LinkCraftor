from __future__ import annotations

import ast
from pathlib import Path

PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

SEARCH_ROOTS = [
    PROJECT_ROOT / "backend" / "server" / "runtime",
    PROJECT_ROOT / "backend" / "server" / "jobs",
    PROJECT_ROOT / "backend" / "server" / "workers",
    PROJECT_ROOT / "backend" / "server" / "queues",
]

EXCLUDED = {
    "__pycache__",
    ".git",
    ".venv",
    "node_modules",
    "backups",
    "runtime_backups",
}

KEYWORDS = {
    "queue": (
        "queue",
        "enqueue",
        "dequeue",
        "claim_job",
        "lease_job",
        "ack_job",
        "nack_job",
    ),
    "persistence": (
        "queue_store",
        "queue_repository",
        "queue_persistence",
    ),
    "lease": (
        "lease",
        "leased",
        "lease_expiration",
    ),
    "statistics": (
        "queue_statistics",
        "queue_stats",
    ),
    "index": (
        "queue_index",
        "index_queue",
    ),
    "certification": (
        "queue_certificate",
        "queue_certification",
    ),
    "universal": (
        "universal_queue",
        "universal_jobs",
    ),
}

matches = {k: [] for k in KEYWORDS}
syntax_failures = []

for root in SEARCH_ROOTS:
    if not root.exists():
        continue

    for path in root.rglob("*.py"):

        if any(part in EXCLUDED for part in path.parts):
            continue

        try:
            source = path.read_text(
                encoding="utf-8-sig",
                errors="strict",
            )
            ast.parse(source)

        except Exception as exc:
            syntax_failures.append(
                f"{path.relative_to(PROJECT_ROOT)} : {exc}"
            )
            continue

        lowered = source.casefold()

        for category, terms in KEYWORDS.items():
            if any(term in lowered for term in terms):
                matches[category].append(
                    path.relative_to(PROJECT_ROOT).as_posix()
                )

for key in matches:
    matches[key] = sorted(set(matches[key]))

def classify(name: str) -> str:
    return (
        f"{name.upper()}_EXISTS"
        if matches[name]
        else f"NO_{name.upper()}_FOUND"
    )

print()
print("=" * 112)
print("UNIVERSAL QUEUE FOUNDATION DISCOVERY")
print("=" * 112)
print()

for category in (
    "queue",
    "persistence",
    "lease",
    "statistics",
    "index",
    "certification",
    "universal",
):
    print(f"{category.capitalize():<16}: {classify(category)}")
    print(f"Matches          : {len(matches[category])}")
    for item in matches[category]:
        print(f"  {item}")
    print()

print("Production files modified : False")
print("Queues created            : 0")
print("Workers created           : 0")
print("Persistent writes         : 0")

print()
print("Syntax failures")

if syntax_failures:
    for item in syntax_failures:
        print("  " + item)
else:
    print("  None")

print()
print("UNIVERSAL QUEUE FOUNDATION SCAN: PASS")
print("=" * 112)
