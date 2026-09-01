from pathlib import Path
import ast

target = Path(
    "backend/server/stores/upload_document_normalizer.py"
)

source = target.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(source)

print(
    "=== U7.15 FAILURE CONTRACT INSPECTION ==="
)
print("FILE=", target)


print()
print("=== NORMALIZATION STATUS CONSTANTS ===")

for node in tree.body:
    if not isinstance(node, ast.Assign):
        continue

    names = [
        target.id
        for target in node.targets
        if isinstance(target, ast.Name)
    ]

    if any(
        name.startswith(
            "NORMALIZATION_STATUS_"
        )
        for name in names
    ):
        print(
            ast.get_source_segment(
                source,
                node,
            )
        )


fn = next(
    node
    for node in tree.body
    if isinstance(node, ast.FunctionDef)
    and node.name
    == "normalize_uploaded_document_v1"
)


print()
print(
    "=== normalize_uploaded_document_v1 ==="
)

print(
    ast.get_source_segment(
        source,
        fn,
    )
)


print()
print("=== RAISE STATEMENTS ===")

raises = [
    node
    for node in ast.walk(fn)
    if isinstance(node, ast.Raise)
]

for node in raises:
    print(
        f"LINE {node.lineno}: "
        f"{ast.get_source_segment(source, node)}"
    )

print(
    "RAISE_COUNT=",
    len(raises),
)


print()
print("=== EXCEPTION HANDLERS ===")

handlers = [
    node
    for node in ast.walk(fn)
    if isinstance(node, ast.ExceptHandler)
]

for node in handlers:
    print(
        f"LINE {node.lineno}:"
    )

    print(
        ast.get_source_segment(
            source,
            node,
        )
    )

print(
    "EXCEPTION_HANDLER_COUNT=",
    len(handlers),
)