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

remove_imports = {
    (
        "backend.server.stores."
        "upload_document_extractor",
        "UploadExtractionResult",
    ),
    (
        "backend.server.stores."
        "upload_document_normalizer",
        "normalize_uploaded_document_v1",
    ),
}

lines = source.splitlines(
    keepends=True
)

edits = []

for node in tree.body:
    if not isinstance(
        node,
        ast.ImportFrom,
    ):
        continue

    module = node.module or ""

    names_to_remove = {
        name
        for import_module, name
        in remove_imports
        if import_module == module
    }

    if not names_to_remove:
        continue

    remaining = [
        alias
        for alias in node.names
        if alias.name
        not in names_to_remove
    ]

    if len(remaining) == len(node.names):
        continue

    if not remaining:
        replacement = ""
    else:
        rendered = []

        for alias in remaining:
            if alias.asname:
                rendered.append(
                    f"{alias.name} as {alias.asname}"
                )
            else:
                rendered.append(
                    alias.name
                )

        replacement = (
            f"from {module} import (\n"
            + "".join(
                f"    {name},\n"
                for name in rendered
            )
            + ")\n"
        )

    edits.append(
        (
            node.lineno - 1,
            node.end_lineno,
            replacement,
        )
    )


for start, end, replacement in sorted(
    edits,
    reverse=True,
):
    lines[start:end] = [
        replacement
    ]


new_source = "".join(lines)

if "UploadExtractionResult" in new_source:
    raise RuntimeError(
        "UploadExtractionResult still remains."
    )

if "normalize_uploaded_document_v1" in new_source:
    raise RuntimeError(
        "normalize_uploaded_document_v1 still remains."
    )

path.write_text(
    new_source,
    encoding="utf-8",
)

print(
    "U8.22_STALE_IMPORT_REMOVAL: COMPLETE"
)
print(
    "REMOVED_IMPORT: UploadExtractionResult"
)
print(
    "REMOVED_IMPORT: normalize_uploaded_document_v1"
)