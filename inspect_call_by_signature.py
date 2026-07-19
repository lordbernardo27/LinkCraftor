from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path("backend/server")
TARGET = "_call_by_signature_v1"

matches = []

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

    for node in ast.walk(tree):
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ) and node.name == TARGET:
            matches.append(
                (
                    path,
                    source,
                    node,
                )
            )

print()
print("=" * 112)
print("INSPECTING _call_by_signature_v1")
print("=" * 112)

if not matches:
    print()
    print("Function not found.")
else:
    for path, source, node in matches:
        print()
        print("-" * 112)
        print("FILE:", path)
        print(
            "LINES:",
            f"{node.lineno}-"
            f"{getattr(node, 'end_lineno', node.lineno)}",
        )
        print("-" * 112)
        print(
            ast.get_source_segment(
                source,
                node,
            )
        )

print()
print("=" * 112)
print("INSPECTION COMPLETE")
print("=" * 112)
print("No files were modified.")
