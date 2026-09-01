from pathlib import Path
import ast

path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

source = path.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(source)

remove_names = {
    "_coerce_upload_extraction_result",
    "build_uduc_from_upload_extraction_result",
    "build_and_write_uduc_from_extraction_result",
    "explain_uploaded_document_unified_content_v1",
}

targets = [
    node
    for node in tree.body
    if isinstance(node, ast.FunctionDef)
    and node.name in remove_names
]

found = {
    node.name
    for node in targets
}

missing = remove_names - found

if missing:
    raise RuntimeError(
        "Expected legacy functions were not found: "
        + ", ".join(sorted(missing))
    )

lines = source.splitlines(
    keepends=True
)

for node in sorted(
    targets,
    key=lambda item: item.lineno,
    reverse=True,
):
    start = node.lineno - 1
    end = node.end_lineno

    while (
        end < len(lines)
        and lines[end].strip() == ""
    ):
        end += 1

    del lines[start:end]

new_source = "".join(lines)

for name in remove_names:
    if f"def {name}(" in new_source:
        raise RuntimeError(
            f"Legacy function still remains after patch: {name}"
        )

path.write_text(
    new_source,
    encoding="utf-8",
)

print("U8.22_LEGACY_FUNCTION_REMOVAL: COMPLETE")

for name in sorted(remove_names):
    print(f"REMOVED: {name}")