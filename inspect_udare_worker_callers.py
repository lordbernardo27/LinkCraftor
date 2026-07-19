from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path("backend/server")

TARGET_NAMES = {
    "execute_udare_reconstruction_worker_v1",
    "run_udare_reconstruction_worker_v1",
    "udare_reconstruction_worker_v1",
}


def get_name(node):
    if isinstance(node, ast.Name):
        return node.id

    if isinstance(node, ast.Attribute):
        left = get_name(node.value)
        if left:
            return f"{left}.{node.attr}"
        return node.attr

    return None


print()
print("=" * 112)
print("UDARE WORKER CALLER INSPECTION")
print("=" * 112)

matches = 0

for path in ROOT.rglob("*.py"):

    try:
        source = path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )
        tree = ast.parse(
            source,
            filename=str(path),
        )
    except Exception:
        continue

    lines = source.splitlines()

    for node in ast.walk(tree):

        if not isinstance(node, ast.Call):
            continue

        called = get_name(node.func)

        if not called:
            continue

        if not any(
            name in called
            for name in TARGET_NAMES
        ):
            continue

        matches += 1

        print()
        print("-" * 112)
        print("FILE:", path)
        print("LINE:", node.lineno)
        print("CALL:", called)
        print("-" * 112)

        start = max(1, node.lineno - 10)
        end = min(len(lines), getattr(node, "end_lineno", node.lineno) + 10)

        for current in range(start, end + 1):
            marker = ">>>" if current == node.lineno else "   "
            print(f"{marker} {current:5}: {lines[current-1]}")

        if node.keywords:
            print()
            print("KEYWORD ARGUMENTS")
            print("-----------------")
            for kw in node.keywords:
                print(
                    f"{kw.arg}: "
                    f"{ast.unparse(kw.value)}"
                )
        else:
            print()
            print("No keyword arguments.")

print()
print("=" * 112)
print("SUMMARY")
print("=" * 112)
print("Worker call sites found:", matches)

if matches == 0:
    print(
        "No direct worker invocation found. "
        "The worker may be imported under another name."
    )

print()
print("No backend files were modified.")
