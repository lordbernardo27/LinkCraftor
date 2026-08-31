from __future__ import annotations

import ast
import re
from pathlib import Path


ROOT = Path(r"C:\Users\HP\Documents\LinkCraftor")
BACKEND = ROOT / "backend" / "server"

EXCLUDED_PARTS = {
    "backups",
    "verification_scans",
    "__pycache__",
    ".pytest_cache",
    "tests",
    "test",
    "logs",
}

EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".log",
    ".txt",
    ".json",
}

CANONICAL_EXTRACTOR = (
    BACKEND
    / "stores"
    / "upload_document_extractor.py"
).resolve()

results = []


def emit(section: str, path: Path, detail: str) -> None:
    rel = path.relative_to(ROOT)
    results.append((section, str(rel), detail))
    print(f"[{section}] {rel}")
    print(f"  {detail}")


def production_python_files():
    for path in BACKEND.rglob("*.py"):
        parts = set(path.parts)

        if parts & EXCLUDED_PARTS:
            continue

        if path.suffix.lower() in EXCLUDED_SUFFIXES:
            continue

        yield path


files = list(production_python_files())

print("=== U6.19 - LEGACY EXTRACTOR CLEANUP SCAN ===")
print(f"PRODUCTION_PYTHON_FILES_SCANNED={len(files)}")
print()


# ------------------------------------------------------------
# A. Legacy extractor names / duplicate extraction APIs
# ------------------------------------------------------------

print("=== A. LEGACY / DUPLICATE EXTRACTOR SYMBOL SCAN ===")

legacy_patterns = [
    r"\bextract_uploaded_document\b",
    r"\bextract_document\b",
    r"\bparse_uploaded_document\b",
    r"\bparse_document_upload\b",
    r"\bupload_extractor\b",
    r"\bdocument_extractor\b",
    r"\bextract_txt\b",
    r"\bextract_markdown\b",
    r"\bextract_html\b",
    r"\bextract_docx\b",
]

for path in files:
    text = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    if path.resolve() == CANONICAL_EXTRACTOR:
        continue

    hits = []

    for pattern in legacy_patterns:
        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):
            hits.append(pattern)

    if hits:
        emit(
            "LEGACY_NAME_HIT",
            path,
            "Patterns: " + ", ".join(hits),
        )


# ------------------------------------------------------------
# B. Direct canonical format-extractor references
# ------------------------------------------------------------

print()
print("=== B. DIRECT FORMAT EXTRACTOR REFERENCE SCAN ===")

direct_format_symbols = (
    "extract_txt_upload_v1",
    "extract_markdown_upload_v1",
    "extract_html_upload_v1",
    "extract_docx_upload_v1",
)

for path in files:
    if path.resolve() == CANONICAL_EXTRACTOR:
        continue

    text = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    hits = [
        name
        for name in direct_format_symbols
        if name in text
    ]

    if hits:
        emit(
            "DIRECT_FORMAT_EXTRACTOR_REFERENCE",
            path,
            "Symbols: " + ", ".join(hits),
        )


# ------------------------------------------------------------
# C. Canonical dispatcher references
# ------------------------------------------------------------

print()
print("=== C. CANONICAL DISPATCHER REFERENCE SCAN ===")

dispatcher_refs = []

for path in files:
    if path.resolve() == CANONICAL_EXTRACTOR:
        continue

    text = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    if "extract_upload_document_v1" in text:
        dispatcher_refs.append(path)
        emit(
            "CANONICAL_DISPATCHER_REFERENCE",
            path,
            "References extract_upload_document_v1",
        )


# ------------------------------------------------------------
# D. Upload-pipeline source rereads
# ------------------------------------------------------------

print()
print("=== D. UPLOAD PIPELINE SOURCE REREAD SCAN ===")

upload_pipeline_root = (
    BACKEND
    / "pipelines"
    / "upload_document"
)

if upload_pipeline_root.exists():
    for path in upload_pipeline_root.rglob("*.py"):
        if set(path.parts) & EXCLUDED_PARTS:
            continue

        text = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        reread_hits = [
            token
            for token in (
                ".read_text(",
                ".read_bytes(",
                "Path.read_text(",
                "Path.read_bytes(",
            )
            if token in text
        ]

        if reread_hits:
            emit(
                "UPLOAD_PIPELINE_SOURCE_REREAD",
                path,
                "Tokens: " + ", ".join(reread_hits),
            )


# ------------------------------------------------------------
# E. DOCX ZIP parsing outside canonical extractor
# ------------------------------------------------------------

print()
print("=== E. DOCX ZIP PARSING OUTSIDE CANONICAL EXTRACTOR ===")

for path in files:
    if path.resolve() == CANONICAL_EXTRACTOR:
        continue

    text = path.read_text(
        encoding="utf-8",
        errors="ignore",
    ).lower()

    if (
        "zipfile" in text
        and (
            "document.xml" in text
            or ".docx" in text
        )
    ):
        emit(
            "DOCX_PARSER_OUTSIDE_CANONICAL_EXTRACTOR",
            path,
            "Contains ZIP/DOCX parsing indicators",
        )


# ------------------------------------------------------------
# F. Markdown stripping logic outside canonical extractor
# ------------------------------------------------------------

print()
print("=== F. MARKDOWN EXTRACTION LOGIC OUTSIDE CANONICAL EXTRACTOR ===")

markdown_indicators = (
    "_strip_markdown",
    "_md_ordered_list",
    "_md_hr_re",
    "fenced code",
)

for path in files:
    if path.resolve() == CANONICAL_EXTRACTOR:
        continue

    text = path.read_text(
        encoding="utf-8",
        errors="ignore",
    ).lower()

    hits = [
        token
        for token in markdown_indicators
        if token in text
    ]

    if hits:
        emit(
            "MARKDOWN_EXTRACTION_LOGIC",
            path,
            "Indicators: " + ", ".join(hits),
        )


# ------------------------------------------------------------
# G. HTML stripping logic outside canonical extractor
# ------------------------------------------------------------

print()
print("=== G. HTML EXTRACTION LOGIC OUTSIDE CANONICAL EXTRACTOR ===")

html_indicators = (
    "_strip_html_tags",
    "_html_comment_re",
    "<script",
    "<noscript",
)

for path in files:
    if path.resolve() == CANONICAL_EXTRACTOR:
        continue

    text = path.read_text(
        encoding="utf-8",
        errors="ignore",
    ).lower()

    hits = [
        token
        for token in html_indicators
        if token in text
    ]

    if len(hits) >= 2:
        emit(
            "HTML_EXTRACTION_LOGIC",
            path,
            "Indicators: " + ", ".join(hits),
        )


# ------------------------------------------------------------
# H. Upload routing duplication
# ------------------------------------------------------------

print()
print("=== H. SOURCE-FORMAT ROUTING DUPLICATION ===")

routing_tokens = (
    '".txt"',
    '".md"',
    '".markdown"',
    '".html"',
    '".htm"',
    '".docx"',
)

for path in files:
    if path.resolve() == CANONICAL_EXTRACTOR:
        continue

    text = path.read_text(
        encoding="utf-8",
        errors="ignore",
    ).lower()

    count = sum(
        token in text
        for token in routing_tokens
    )

    if count >= 4:
        emit(
            "POSSIBLE_FORMAT_ROUTER_DUPLICATION",
            path,
            f"Contains {count}/6 canonical upload extensions",
        )


# ------------------------------------------------------------
# I. Direct extraction logic in known upload entry files
# ------------------------------------------------------------

print()
print("=== I. KNOWN LIVE ENTRY FILE CHECK ===")

known_files = [
    BACKEND / "routes" / "files.py",
    BACKEND
    / "pipelines"
    / "upload_document"
    / "uploaded_document_to_uduc_pipeline"
    / "upload_intake.py",
    BACKEND
    / "pipelines"
    / "upload_document"
    / "coordinator.py",
    BACKEND
    / "pipelines"
    / "upload_document"
    / "uploaded_document_to_uduc_pipeline"
    / "coordinator.py",
]

for path in known_files:
    if not path.exists():
        continue

    text = path.read_text(
        encoding="utf-8",
        errors="ignore",
    ).lower()

    direct_logic_tokens = []

    for token in (
        "zipfile",
        "document.xml",
        "_strip_markdown",
        "_strip_html_tags",
        "_normalize_upload_text",
    ):
        if token in text:
            direct_logic_tokens.append(token)

    if direct_logic_tokens:
        emit(
            "DIRECT_EXTRACTION_LOGIC_IN_ENTRY_FILE",
            path,
            "Indicators: "
            + ", ".join(direct_logic_tokens),
        )
    else:
        emit(
            "ENTRY_FILE_CLEAN",
            path,
            "No embedded format-specific extraction logic detected",
        )


# ------------------------------------------------------------
# J. Imports of extractor-like modules
# ------------------------------------------------------------

print()
print("=== J. EXTRACTOR IMPORT GRAPH ===")

for path in files:
    try:
        tree = ast.parse(
            path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        )
    except SyntaxError:
        continue

    imported = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if "extract" in alias.name.lower():
                    imported.append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""

            names = [
                alias.name
                for alias in node.names
            ]

            if (
                "extract" in module.lower()
                or any(
                    "extract" in name.lower()
                    for name in names
                )
            ):
                imported.append(
                    module
                    + ":"
                    + ",".join(names)
                )

    if imported:
        emit(
            "EXTRACTOR_IMPORT",
            path,
            "Imports: " + " | ".join(imported),
        )


# ------------------------------------------------------------
# K. Candidate unreachable extractor modules
# ------------------------------------------------------------

print()
print("=== K. EXTRACTOR-LIKE MODULE INVENTORY ===")

for path in files:
    if path.resolve() == CANONICAL_EXTRACTOR:
        emit(
            "CANONICAL_EXTRACTOR",
            path,
            "Canonical upload extraction authority",
        )
        continue

    name = path.name.lower()

    if (
        "extractor" in name
        or "extraction" in name
        or (
            "upload" in name
            and "parse" in name
        )
    ):
        emit(
            "EXTRACTOR_LIKE_MODULE",
            path,
            "Requires classification if upload-related",
        )


# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

print()
print("========================================")
print("U6.19_SCAN_COMPLETE: YES")
print(f"U6.19_TOTAL_HITS={len(results)}")

categories = {}

for section, _, _ in results:
    categories[section] = (
        categories.get(section, 0) + 1
    )

for section in sorted(categories):
    print(
        f"{section}={categories[section]}"
    )

print()
print(
    "U6.19_NOTE: THIS IS DISCOVERY ONLY; "
    "NO FILE HAS BEEN DELETED OR PATCHED."
)