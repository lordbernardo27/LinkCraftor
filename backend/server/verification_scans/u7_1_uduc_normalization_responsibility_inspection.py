from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(r"C:\Users\HP\Documents\LinkCraftor")
BASE = ROOT / "backend" / "server"

UDUC = (
    BASE
    / "stores"
    / "uploaded_document_unified_content.py"
)

TEXT_NORMALIZATION = (
    BASE
    / "utils"
    / "text_normalization.py"
)

EXCLUDED = {
    "backups",
    "verification_scans",
    "runtime_backups",
    "__pycache__",
    ".pytest_cache",
    "tests",
    "test",
    "logs",
}


def read(path: Path) -> str:
    return path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )


def live_files():
    for path in BASE.rglob("*.py"):
        if set(path.parts) & EXCLUDED:
            continue
        yield path


def show_function(source: str, name: str) -> None:
    tree = ast.parse(source)

    for node in tree.body:
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ) and node.name == name:
            print()
            print(f"--- FUNCTION {name} ---")
            print(ast.unparse(node))
            return

    print()
    print(f"--- FUNCTION {name}: NOT FOUND ---")


print(
    "=== U7.1 UDUC NORMALIZATION RESPONSIBILITY INSPECTION ==="
)


# ------------------------------------------------------------
# A. Exact UDUC function bodies
# ------------------------------------------------------------

print()
print("=== A. UDUC CONTENT-SHAPING FUNCTIONS ===")

uduc_source = read(UDUC)

for function_name in (
    "_as_list",
    "_paragraphs_from_content_body",
    "_build_heading_map",
    "_build_uduc_structure",
    "build_uduc_from_upload_extraction_result",
):
    show_function(
        uduc_source,
        function_name,
    )


# ------------------------------------------------------------
# B. Exact references to extracted content
# ------------------------------------------------------------

print()
print("=== B. EXTRACTION RESULT FIELD REFERENCES ===")

for lineno, line in enumerate(
    uduc_source.splitlines(),
    start=1,
):
    lower = line.lower()

    if any(
        token in lower
        for token in (
            "extraction_result",
            "content_body",
            "headings",
            "title",
            "paragraph",
            "word_count",
        )
    ):
        print(
            f"L{lineno}: {line.rstrip()}"
        )


# ------------------------------------------------------------
# C. Generic text-normalization usage graph
# ------------------------------------------------------------

print()
print("=== C. TEXT_NORMALIZATION IMPORT / USE GRAPH ===")

module_names = (
    "backend.server.utils.text_normalization",
    "utils.text_normalization",
)

symbol = "fix_mojibake_text"

users = []

for path in live_files():
    if path.resolve() == TEXT_NORMALIZATION.resolve():
        continue

    source = read(path)

    if (
        symbol in source
        or any(
            module_name in source
            for module_name in module_names
        )
    ):
        users.append(
            path.relative_to(ROOT)
        )

if users:
    for path in users:
        print(f"TEXT_NORMALIZATION_USER: {path}")
else:
    print("TEXT_NORMALIZATION_USERS: NONE")


# ------------------------------------------------------------
# D. Upload branch usage specifically
# ------------------------------------------------------------

print()
print("=== D. UPLOAD BRANCH TEXT_NORMALIZATION USAGE ===")

upload_root = (
    BASE
    / "pipelines"
    / "upload_document"
)

upload_users = []

for path in upload_root.rglob("*.py"):
    if set(path.parts) & EXCLUDED:
        continue

    source = read(path)

    if (
        symbol in source
        or "text_normalization" in source
    ):
        upload_users.append(
            path.relative_to(ROOT)
        )

if upload_users:
    for path in upload_users:
        print(
            f"UPLOAD_TEXT_NORMALIZATION_USER: {path}"
        )
else:
    print(
        "UPLOAD_TEXT_NORMALIZATION_USERS: NONE"
    )


# ------------------------------------------------------------
# E. UDUC imports
# ------------------------------------------------------------

print()
print("=== E. UDUC IMPORTS ===")

tree = ast.parse(uduc_source)

for node in tree.body:
    if isinstance(
        node,
        (
            ast.Import,
            ast.ImportFrom,
        ),
    ):
        print(
            ast.unparse(node)
        )


print()
print(
    "U7.1_UDUC_RESPONSIBILITY_INSPECTION_COMPLETE: YES"
)
print(
    "NO_PRODUCTION_FILES_MODIFIED: YES"
)