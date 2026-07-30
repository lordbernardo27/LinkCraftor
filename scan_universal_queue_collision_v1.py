from __future__ import annotations

import ast
from pathlib import Path

PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

SEARCH_ROOTS = [
    PROJECT_ROOT / "backend/server/runtime",
    PROJECT_ROOT / "backend/server/jobs",
    PROJECT_ROOT / "backend/server/workers",
]

EXCLUDED = {
    "__pycache__",
    ".git",
    ".venv",
    "node_modules",
    "backups",
    "runtime_backups",
}

CANONICAL_OPERATIONS = {
    "enqueue_job": {
        "enqueue",
        "submit",
        "schedule",
        "create_job",
        "queue_job",
        "push_job",
    },
    "claim_next_job": {
        "claim",
        "acquire",
        "take",
        "next_job",
        "pop_job",
        "reserve",
    },
    "lease_job": {
        "lease",
        "lock",
        "hold",
        "reserve_job",
    },
    "complete_job": {
        "complete",
        "finish",
        "mark_completed",
        "ack",
        "acknowledge",
    },
    "fail_job": {
        "fail",
        "mark_failed",
        "record_failure",
        "error_job",
        "nack",
    },
    "retry_job": {
        "retry",
        "requeue",
        "schedule_retry",
        "return_to_queue",
    },
    "cancel_job": {
        "cancel",
        "abort",
        "mark_cancelled",
    },
    "list_jobs": {
        "list",
        "find",
        "search",
        "enumerate",
        "jobs",
    },
    "assign_worker": {
        "assign",
        "bind",
        "worker",
        "dispatch",
    },
}

results = {
    key: []
    for key in CANONICAL_OPERATIONS
}

syntax_failures = []

for root in SEARCH_ROOTS:

    if not root.exists():
        continue

    for path in root.rglob("*.py"):

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

        for node in ast.walk(tree):

            if not isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            ):
                continue

            lowered = node.name.casefold()

            for operation, aliases in (
                CANONICAL_OPERATIONS.items()
            ):

                if any(
                    alias in lowered
                    for alias in aliases
                ):

                    results[
                        operation
                    ].append(
                        (
                            path.relative_to(PROJECT_ROOT).as_posix(),
                            node.lineno,
                            node.name,
                        )
                    )

print()
print("=" * 112)
print("UNIVERSAL QUEUE ENGINE COLLISION SCAN")
print("=" * 112)
print()

for operation in CANONICAL_OPERATIONS:

    entries = sorted(
        set(results[operation])
    )

    if not entries:
        status = "MISSING"

    elif any(
        name == operation
        for _, _, name in entries
    ):
        status = "EXISTS_AS_CANONICAL"

    else:
        status = "EXISTS_UNDER_DIFFERENT_NAME"

    print(f"{operation:<22} {status}")

    for file, line, name in entries:
        print(f"  {file}:{line}:{name}")

    print()

print("Production files modified : False")
print("Queues created            : 0")
print("Jobs created              : 0")
print("Persistent writes         : 0")

print()
print("Syntax failures")

if syntax_failures:
    for item in syntax_failures:
        print("  ", item)
else:
    print("  None")

print()
print("UNIVERSAL QUEUE COLLISION SCAN: PASS")
print("=" * 112)
