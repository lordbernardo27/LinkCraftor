from __future__ import annotations

import ast
from pathlib import Path


FILES = [
    Path(
        "backend/server/workers/"
        "udare_reconstruction_worker.py"
    ),
    Path(
        "backend/server/stores/"
        "raw_website_html_store.py"
    ),
]

TARGETS = {
    "_default_raw_record_loader_v1",
    "get_raw_html_record",
    "read_raw_html_record",
    "load_raw_html_record",
    "get_raw_website_html_record",
}


for path in FILES:
    print()
    print("=" * 110)
    print(path)
    print("=" * 110)

    if not path.is_file():
        print("FILE MISSING")
        continue

    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    found = 0

    for node in ast.walk(tree):
        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        name = node.name

        if (
            name in TARGETS
            or (
                "raw" in name.casefold()
                and "record" in name.casefold()
                and (
                    "load" in name.casefold()
                    or "read" in name.casefold()
                    or "get" in name.casefold()
                )
            )
        ):
            found += 1

            print()
            print("-" * 110)
            print(
                f"FUNCTION: {name}"
            )
            print(
                f"LINES: {node.lineno}-"
                f"{getattr(node, 'end_lineno', node.lineno)}"
            )
            print("-" * 110)

            print(
                ast.get_source_segment(
                    source,
                    node,
                )
            )

    if found == 0:
        print()
        print("No matching loader functions found.")


print()
print("=" * 110)
print("INSPECTION COMPLETE")
print("=" * 110)
print("No queue or store file was modified.")
