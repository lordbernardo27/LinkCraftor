from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(r"C:\Users\HP\Documents\LinkCraftor")

PATHS = [
    ROOT / "backend/server/stores/dom_article_structure_extractor.py",
    ROOT / "backend/server/stores/helix_smart_extractor.py",
    ROOT / "backend/server/stores/main_content_extraction_engine.py",
    ROOT / "backend/server/stores/smart_phrase_extractor_backup_before_v2.py",
]

UPLOAD_TERMS = (
    "upload",
    "uploaded_document",
    "docx",
    "markdown",
    "html",
    "txt",
    "extract_upload_document_v1",
    "UploadExtractionResult",
    "UDUC",
)


print("=== U6.19 CANDIDATE RESPONSIBILITY INSPECTION ===")

for path in PATHS:
    print()
    print(f"=== {path.relative_to(ROOT)} ===")
    print(f"SIZE_BYTES={path.stat().st_size}")

    source = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    print("IMPORTS=")

    imports = [
        node
        for node in tree.body
        if isinstance(
            node,
            (
                ast.Import,
                ast.ImportFrom,
            ),
        )
    ]

    if imports:
        for node in imports:
            print(f"  {ast.unparse(node)}")
    else:
        print("  NONE")

    print("TOP_LEVEL_FUNCTIONS=")

    functions = [
        node.name
        for node in tree.body
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
    ]

    if functions:
        for name in functions:
            print(f"  {name}")
    else:
        print("  NONE")

    print("TOP_LEVEL_CLASSES=")

    classes = [
        node.name
        for node in tree.body
        if isinstance(
            node,
            ast.ClassDef,
        )
    ]

    if classes:
        for name in classes:
            print(f"  {name}")
    else:
        print("  NONE")

    terms = [
        term
        for term in UPLOAD_TERMS
        if term.lower() in source.lower()
    ]

    print(
        "UPLOAD_TERMS="
        + (
            ", ".join(terms)
            if terms
            else "NONE"
        )
    )


print()
print(
    "U6.19_CANDIDATE_RESPONSIBILITY_INSPECTION_COMPLETE: YES"
)
print("NO_FILES_MODIFIED: YES")