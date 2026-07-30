from __future__ import annotations

import ast
from pathlib import Path

PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

CANDIDATES = [
    PROJECT_ROOT / "backend/server/jobs/universal_knowledge_orchestrator.py",
    PROJECT_ROOT / "backend/server/runtime/runtime_persistence.py",
    PROJECT_ROOT / "backend/server/runtime/runtime_state_store.py",
    PROJECT_ROOT / "backend/server/runtime/universal_jobs/contract.py",
    PROJECT_ROOT / "backend/server/runtime/universal_runtime_kernel.py",
    PROJECT_ROOT / "backend/server/runtime/universal_runtime_infrastructure.py",
]

QUEUE_OPERATIONS = {
    "enqueue",
    "dequeue",
    "claim",
    "lease",
    "ack",
    "acknowledge",
    "nack",
    "fail",
    "cancel",
    "peek",
    "list",
    "statistics",
    "stats",
    "purge",
}

PERSISTENCE_TERMS = {
    "queue_record",
    "queue_store",
    "queue_repository",
    "queue_persistence",
}

STATE_TERMS = {
    "queued",
    "leased",
    "completed",
    "failed",
    "cancelled",
}

api_functions = []
api_classes = []
queue_calls = []
persistence_refs = []
state_refs = []
syntax_failures = []

for path in CANDIDATES:

    if not path.exists():
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

    for term in PERSISTENCE_TERMS:
        if term in lowered:
            persistence_refs.append(
                f"{path.relative_to(PROJECT_ROOT)} : {term}"
            )

    for term in STATE_TERMS:
        if term in lowered:
            state_refs.append(
                f"{path.relative_to(PROJECT_ROOT)} : {term}"
            )

    for node in ast.walk(tree):

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):

            name = node.name.casefold()

            if any(op in name for op in QUEUE_OPERATIONS):
                api_functions.append(
                    f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}:{node.name}"
                )

        elif isinstance(node, ast.ClassDef):

            name = node.name.casefold()

            if "queue" in name:
                api_classes.append(
                    f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}:{node.name}"
                )

        elif isinstance(node, ast.Call):

            func = ""

            if isinstance(node.func, ast.Name):
                func = node.func.id.casefold()

            elif isinstance(node.func, ast.Attribute):
                func = node.func.attr.casefold()

            if any(op == func for op in QUEUE_OPERATIONS):
                queue_calls.append(
                    f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}:{func}"
                )

api_functions = sorted(set(api_functions))
api_classes = sorted(set(api_classes))
queue_calls = sorted(set(queue_calls))
persistence_refs = sorted(set(persistence_refs))
state_refs = sorted(set(state_refs))

if (
    api_functions
    or api_classes
):
    classification = "REUSABLE_QUEUE_API_FOUND"
else:
    classification = "NO_REUSABLE_QUEUE_API"

print()
print("=" * 116)
print("UNIVERSAL QUEUE API DISCOVERY")
print("=" * 116)
print()

print("Classification :", classification)
print()

print("Queue API functions :", len(api_functions))
for item in api_functions:
    print("  ", item)

print()

print("Queue API classes :", len(api_classes))
for item in api_classes:
    print("  ", item)

print()

print("Queue API calls :", len(queue_calls))
for item in queue_calls:
    print("  ", item)

print()

print("Queue persistence references :", len(persistence_refs))
for item in persistence_refs:
    print("  ", item)

print()

print("Queue state references :", len(state_refs))
for item in state_refs:
    print("  ", item)

print()

print("Production files modified : False")
print("Persistent writes         : 0")
print("Queues created            : 0")

print()
print("Syntax failures")

if syntax_failures:
    for item in syntax_failures:
        print("  ", item)
else:
    print("  None")

print()
print("UNIVERSAL QUEUE API SCAN: PASS")
print("=" * 116)
