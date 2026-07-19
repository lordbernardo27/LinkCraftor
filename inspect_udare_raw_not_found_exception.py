from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path("backend/server")

SEARCH_TERMS = (
    "Raw HTML record was not found",
    "raw html record was not found",
)


if not ROOT.is_dir():
    raise RuntimeError(
        f"Backend directory is missing: {ROOT}"
    )


matches: list[tuple[Path, int, str]] = []

for path in ROOT.rglob("*.py"):
    try:
        source = path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )
    except Exception:
        continue

    for line_number, line in enumerate(
        source.splitlines(),
        start=1,
    ):
        if any(
            term.casefold() in line.casefold()
            for term in SEARCH_TERMS
        ):
            matches.append(
                (
                    path,
                    line_number,
                    line.strip(),
                )
            )


print()
print("=" * 112)
print("RAW HTML NOT-FOUND EXCEPTION SEARCH")
print("=" * 112)

print()
print("Exact-message occurrences:", len(matches))

if not matches:
    print()
    print(
        "No exact occurrence was found under backend/server."
    )
else:
    for path, line_number, line in matches:
        print()
        print("-" * 112)
        print("FILE:", path)
        print("LINE:", line_number)
        print("TEXT:", line)

        source = path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )

        try:
            tree = ast.parse(
                source,
                filename=str(path),
            )
        except SyntaxError as exc:
            print()
            print(
                "AST parsing unavailable for this file:",
                exc,
            )

            lines = source.splitlines()

            start = max(
                0,
                line_number - 21,
            )

            end = min(
                len(lines),
                line_number + 20,
            )

            print()
            print("SURROUNDING LINES")

            for index in range(
                start,
                end,
            ):
                marker = (
                    ">>>"
                    if index + 1 == line_number
                    else "   "
                )

                print(
                    f"{marker} {index + 1:5}: "
                    f"{lines[index]}"
                )

            continue

        containing_nodes = []

        for node in ast.walk(tree):
            if not isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            ):
                continue

            node_start = node.lineno
            node_end = getattr(
                node,
                "end_lineno",
                node.lineno,
            )

            if node_start <= line_number <= node_end:
                containing_nodes.append(
                    node
                )

        if containing_nodes:
            containing_nodes.sort(
                key=lambda node: (
                    getattr(
                        node,
                        "end_lineno",
                        node.lineno,
                    )
                    - node.lineno
                )
            )

            node = containing_nodes[0]

            print()
            print(
                "CONTAINING FUNCTION:",
                node.name,
            )

            print(
                "FUNCTION LINES:",
                f"{node.lineno}-"
                f"{getattr(node, 'end_lineno', node.lineno)}",
            )

            print()
            print("COMPLETE FUNCTION")
            print("-" * 112)

            segment = ast.get_source_segment(
                source,
                node,
            )

            print(
                segment
                or "Unable to extract function source."
            )
        else:
            lines = source.splitlines()

            start = max(
                0,
                line_number - 21,
            )

            end = min(
                len(lines),
                line_number + 20,
            )

            print()
            print(
                "No containing function found. "
                "Printing surrounding lines."
            )

            for index in range(
                start,
                end,
            ):
                marker = (
                    ">>>"
                    if index + 1 == line_number
                    else "   "
                )

                print(
                    f"{marker} {index + 1:5}: "
                    f"{lines[index]}"
                )


print()
print("=" * 112)
print("INSPECTION COMPLETE")
print("=" * 112)
print("No backend, queue, job, or store file was modified.")
