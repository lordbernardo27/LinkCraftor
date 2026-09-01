from pathlib import Path
import ast
from collections import Counter

path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

source = path.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(source)

print("=== U8.22 POST-CLEANUP IMPORT INVENTORY ===")

imports = []

for node in tree.body:
    if isinstance(node, ast.Import):
        for alias in node.names:
            imports.append(
                (
                    alias.asname or alias.name.split(".")[0],
                    alias.name,
                    node.lineno,
                )
            )

    elif isinstance(node, ast.ImportFrom):
        module = node.module or ""

        for alias in node.names:
            imports.append(
                (
                    alias.asname or alias.name,
                    f"{module}.{alias.name}",
                    node.lineno,
                )
            )


name_counts = Counter(
    node.id
    for node in ast.walk(tree)
    if isinstance(node, ast.Name)
)


for local_name, source_name, line_number in imports:
    # Import declaration itself contributes one Store occurrence,
    # so a count greater than zero in ast.Name reflects actual usage
    # only for imported symbols referenced elsewhere.
    usage_count = name_counts.get(
        local_name,
        0,
    )

    print(
        f"IMPORT: {local_name} <- {source_name} "
        f"(line {line_number}) "
        f"REFERENCE_COUNT={usage_count}"
    )


print()
print("=== LEGACY-COMPATIBILITY IMPORT CHECK ===")

for target in [
    "UploadExtractionResult",
    "normalize_uploaded_document_v1",
]:
    print(
        f"{target}_REFERENCE_COUNT="
        f"{name_counts.get(target, 0)}"
    )


print()
print("=== CANONICAL SYMBOL PRESENCE ===")

for target in [
    "NormalizedUploadedDocumentContent",
    "build_uduc_from_normalized_content",
    "build_and_write_uduc_from_normalized_content",
    "serialize_uduc",
    "write_uduc",
    "read_uduc",
]:
    print(
        f"{target}_PRESENT="
        f"{target in source}"
    )