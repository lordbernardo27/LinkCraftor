from __future__ import annotations

import ast
from pathlib import Path

TARGET = Path(
    "backend/server/jobs/universal_knowledge_orchestrator.py"
)

FUNCTIONS = {
    "queue_path",
    "read_queue",
}


print()
print("=" * 112)
print("UNIVERSAL KNOWLEDGE ORCHESTRATOR INSPECTION")
print("=" * 112)

if not TARGET.exists():
    raise RuntimeError(f"File not found: {TARGET}")

source = TARGET.read_text(
    encoding="utf-8-sig",
    errors="replace",
)

lines = source.splitlines()

tree = ast.parse(source)


def functions(tree):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield node


found = 0

for node in functions(tree):

    if node.name not in FUNCTIONS:
        continue

    found += 1

    print()
    print("-" * 112)
    print("FUNCTION:", node.name)
    print("LINES:", f"{node.lineno}-{node.end_lineno}")
    print("-" * 112)

    start = max(1, node.lineno - 20)
    end = min(len(lines), node.end_lineno + 20)

    for i in range(start, end + 1):

        marker = ">>> " if node.lineno <= i <= node.end_lineno else "    "

        print(f"{marker}{i:5}: {lines[i-1]}")


print()
print("=" * 112)
print("QUEUE PATH CONSTANTS")
print("=" * 112)

KEYWORDS = (
    "queue_ws_",
    "queue.jsonl",
    "queues/universal_knowledge",
    "jobs/universal_knowledge",
    "QUEUE_DIR",
    "QUEUE_ROOT",
    "QUEUE_PATH",
)

for lineno, line in enumerate(lines, start=1):

    if any(k.lower() in line.lower() for k in KEYWORDS):
        print(f"{lineno:5}: {line}")


print()
print("=" * 112)
print("SUMMARY")
print("=" * 112)
print("Functions found:", found)
print("No files were modified.")
