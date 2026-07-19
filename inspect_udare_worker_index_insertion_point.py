from __future__ import annotations

import ast
from pathlib import Path


PATH = Path(
    "backend/server/workers/"
    "udare_reconstruction_worker.py"
)

if not PATH.is_file():
    raise RuntimeError(
        f"Missing worker file: {PATH}"
    )

source = PATH.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

tree = ast.parse(
    source,
    filename=str(PATH),
)

TARGET_TERMS = (
    "persist_udare",
    "write_udare",
    "store_udare",
    "save_udare",
    "refresh_udare_store_manifest",
    "verify_udare_store",
    "article_document",
    "persistence_result",
    "store_result",
)


def contains_target(node: ast.AST) -> bool:
    segment = ast.get_source_segment(
        source,
        node,
    ) or ""

    lowered = segment.casefold()

    return any(
        term in lowered
        for term in TARGET_TERMS
    )


print()
print("=" * 110)
print("UDARE WORKER FUNCTIONS")
print("=" * 110)

functions = []

for node in ast.walk(tree):
    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    ):
        functions.append(node)

        print(
            f"{node.name}: lines "
            f"{node.lineno}-{getattr(node, 'end_lineno', node.lineno)}"
        )


print()
print("=" * 110)
print("FUNCTIONS CONTAINING STORE/PERSISTENCE TERMS")
print("=" * 110)

matched = []

for node in functions:
    if contains_target(node):
        matched.append(node)

        print()
        print(
            f"FUNCTION: {node.name}"
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


print()
print("=" * 110)
print("RETURN STATEMENTS IN MATCHED FUNCTIONS")
print("=" * 110)

for function in matched:
    for node in ast.walk(function):
        if isinstance(
            node,
            ast.Return,
        ):
            print()
            print(
                f"FUNCTION: {function.name}"
            )
            print(
                f"RETURN LINE: {node.lineno}"
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
print("INDEX INTEGRATION CURRENT STATE")
print("=" * 110)

print(
    "Index import present:",
    (
        "from backend.server.stores."
        "udare_store_index_builder "
        "import build_udare_store_index_v1"
    )
    in source,
)

print(
    "Index call present:",
    "build_udare_store_index_v1("
    in source,
)

print()
print("Inspection only.")
print("No worker source was modified.")
print("No queue or article was touched.")
