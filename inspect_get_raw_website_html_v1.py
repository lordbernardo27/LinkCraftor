from __future__ import annotations

import ast
from pathlib import Path


PATH = Path(
    "backend/server/stores/"
    "raw_website_html_store.py"
)

TARGET = "get_raw_website_html_v1"

if not PATH.is_file():
    raise RuntimeError(
        f"Missing file: {PATH}"
    )

source = PATH.read_text(
    encoding="utf-8-sig",
    errors="replace",
)

tree = ast.parse(
    source,
    filename=str(PATH),
)

found = False

for node in ast.walk(tree):
    if not isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    ):
        continue

    if node.name != TARGET:
        continue

    found = True

    print()
    print("=" * 110)
    print("FUNCTION:", node.name)
    print(
        "LINES:",
        f"{node.lineno}-"
        f"{getattr(node, 'end_lineno', node.lineno)}",
    )
    print("=" * 110)

    print(
        ast.get_source_segment(
            source,
            node,
        )
    )

if not found:
    print()
    print(
        "Exact function not found. "
        "Functions containing 'raw_website_html' follow."
    )

    for node in ast.walk(tree):
        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        if "raw_website_html" in node.name.casefold():
            print()
            print("-" * 110)
            print(
                f"{node.name}: "
                f"lines {node.lineno}-"
                f"{getattr(node, 'end_lineno', node.lineno)}"
            )
            print("-" * 110)

            print(
                ast.get_source_segment(
                    source,
                    node,
                )
            )

print()
print("=" * 110)
print("INSPECTION COMPLETE")
print("=" * 110)
print("No queue or store file was modified.")
