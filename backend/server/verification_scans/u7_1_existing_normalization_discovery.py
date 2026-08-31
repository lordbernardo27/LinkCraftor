from __future__ import annotations

import ast
import re
from pathlib import Path


ROOT = Path(r"C:\Users\HP\Documents\LinkCraftor")
BASE = ROOT / "backend" / "server"

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

CANONICAL_EXTRACTOR = (
    BASE
    / "stores"
    / "upload_document_extractor.py"
).resolve()

UPLOAD_PIPELINE = (
    BASE
    / "pipelines"
    / "upload_document"
)

results = []


def emit(section: str, path: Path, detail: str) -> None:
    rel = path.relative_to(ROOT)
    results.append((section, str(rel), detail))
    print(f"[{section}] {rel}")
    print(f"  {detail}")


def live_python_files():
    for path in BASE.rglob("*.py"):
        if set(path.parts) & EXCLUDED:
            continue
        yield path


files = list(live_python_files())

print("=== U7.1 - EXISTING NORMALIZATION DISCOVERY ===")
print(f"LIVE_PYTHON_FILES={len(files)}")
print()


# ------------------------------------------------------------
# A. Normalization currently inside canonical U6 extractor
# ------------------------------------------------------------

print("=== A. NORMALIZATION INSIDE U6 EXTRACTOR ===")

source = CANONICAL_EXTRACTOR.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

tree = ast.parse(
    source,
    filename=str(CANONICAL_EXTRACTOR),
)

for node in tree.body:
    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    ):
        name = node.name.lower()

        if any(
            token in name
            for token in (
                "normalize",
                "strip",
                "clean",
                "whitespace",
            )
        ):
            emit(
                "U6_NORMALIZATION_HELPER",
                CANONICAL_EXTRACTOR,
                f"Function: {node.name}",
            )


# ------------------------------------------------------------
# B. Normalization references in upload pipeline
# ------------------------------------------------------------

print()
print("=== B. UPLOAD PIPELINE NORMALIZATION REFERENCES ===")

normalization_tokens = (
    "normalize",
    "normalise",
    "normalized",
    "normalised",
    "clean_text",
    "cleaned_text",
    "strip_text",
    "whitespace",
    "unicode",
)

if UPLOAD_PIPELINE.exists():
    for path in UPLOAD_PIPELINE.rglob("*.py"):
        if set(path.parts) & EXCLUDED:
            continue

        text = path.read_text(
            encoding="utf-8-sig",
            errors="ignore",
        ).lower()

        hits = sorted({
            token
            for token in normalization_tokens
            if token in text
        })

        if hits:
            emit(
                "UPLOAD_PIPELINE_NORMALIZATION_REFERENCE",
                path,
                "Tokens: " + ", ".join(hits),
            )


# ------------------------------------------------------------
# C. Normalization-like modules across live backend
# ------------------------------------------------------------

print()
print("=== C. NORMALIZATION-LIKE MODULE INVENTORY ===")

for path in files:
    name = path.name.lower()

    if any(
        token in name
        for token in (
            "normaliz",
            "clean",
            "sanitize",
            "canonical",
        )
    ):
        emit(
            "NORMALIZATION_LIKE_MODULE",
            path,
            "Requires responsibility classification",
        )


# ------------------------------------------------------------
# D. Duplicate upload normalization helpers
# ------------------------------------------------------------

print()
print("=== D. POSSIBLE DUPLICATE UPLOAD NORMALIZATION HELPERS ===")

function_patterns = (
    r"def\s+[_a-zA-Z0-9]*normalize[_a-zA-Z0-9]*\s*\(",
    r"def\s+[_a-zA-Z0-9]*clean[_a-zA-Z0-9]*\s*\(",
    r"def\s+[_a-zA-Z0-9]*sanitize[_a-zA-Z0-9]*\s*\(",
)

for path in files:
    if path.resolve() == CANONICAL_EXTRACTOR:
        continue

    text = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    function_hits = []

    for pattern in function_patterns:
        function_hits.extend(
            match.group(0)
            for match in re.finditer(
                pattern,
                text,
                flags=re.IGNORECASE,
            )
        )

    lower = text.lower()

    upload_context = any(
        token in lower
        for token in (
            "upload_document",
            "uploaded_document",
            "upload extraction",
            "upload_extraction",
            "uduc",
        )
    )

    if function_hits and upload_context:
        emit(
            "POSSIBLE_UPLOAD_NORMALIZATION_DUPLICATE",
            path,
            "Functions: "
            + ", ".join(
                function_hits[:12]
            ),
        )


# ------------------------------------------------------------
# E. Website-only cleaners / normalizers
# ------------------------------------------------------------

print()
print("=== E. WEBSITE NORMALIZATION / CLEANER INVENTORY ===")

website_indicators = (
    "article_body_cleaning_engine",
    "article_cleaning_pipeline",
    "site_reader",
    "dom_article",
    "main_content_extraction",
    "website",
    "webpage",
)

for path in files:
    text = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    ).lower()

    name = path.name.lower()

    if (
        any(
            token in name
            for token in (
                "clean",
                "normaliz",
                "extract",
            )
        )
        and any(
            token in text
            for token in website_indicators
        )
    ):
        emit(
            "WEBSITE_NORMALIZATION_CANDIDATE",
            path,
            "Likely Website/content-processing responsibility",
        )


# ------------------------------------------------------------
# F. UploadExtractionResult consumers
# ------------------------------------------------------------

print()
print("=== F. UPLOAD EXTRACTION RESULT CONSUMERS ===")

for path in files:
    if path.resolve() == CANONICAL_EXTRACTOR:
        continue

    text = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    if (
        "UploadExtractionResult" in text
        or "extraction_result" in text
    ):
        emit(
            "EXTRACTION_RESULT_CONSUMER",
            path,
            "Consumes or references extraction result data",
        )


# ------------------------------------------------------------
# G. Direct normalization of extraction-result fields
# ------------------------------------------------------------

print()
print("=== G. DOWNSTREAM EXTRACTION FIELD NORMALIZATION ===")

field_patterns = (
    r"extraction_result\.text",
    r"extraction_result\.title",
    r"extraction_result\.headings",
    r"getattr\(\s*extraction_result\s*,\s*[\"']text[\"']",
    r"getattr\(\s*extraction_result\s*,\s*[\"']title[\"']",
    r"getattr\(\s*extraction_result\s*,\s*[\"']headings[\"']",
)

for path in files:
    if path.resolve() == CANONICAL_EXTRACTOR:
        continue

    text = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    hits = []

    for pattern in field_patterns:
        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):
            hits.append(pattern)

    if hits:
        emit(
            "DOWNSTREAM_EXTRACTION_FIELD_USE",
            path,
            "Patterns: " + ", ".join(hits),
        )


# ------------------------------------------------------------
# H. Source reread during possible normalization
# ------------------------------------------------------------

print()
print("=== H. SOURCE REREAD / SECOND-PASS NORMALIZATION CHECK ===")

if UPLOAD_PIPELINE.exists():
    for path in UPLOAD_PIPELINE.rglob("*.py"):
        if set(path.parts) & EXCLUDED:
            continue

        text = path.read_text(
            encoding="utf-8-sig",
            errors="ignore",
        )

        hits = [
            token
            for token in (
                ".read_text(",
                ".read_bytes(",
                "Path.read_text(",
                "Path.read_bytes(",
            )
            if token in text
        ]

        if hits:
            emit(
                "UPLOAD_PIPELINE_SOURCE_REREAD",
                path,
                "Tokens: " + ", ".join(hits),
            )


# ------------------------------------------------------------
# I. UDUC normalization indicators
# ------------------------------------------------------------

print()
print("=== I. UDUC NORMALIZATION INDICATORS ===")

uduc_path = (
    BASE
    / "stores"
    / "uploaded_document_unified_content.py"
)

if uduc_path.exists():
    text = uduc_path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )

    try:
        uduc_tree = ast.parse(
            text,
            filename=str(uduc_path),
        )

        for node in uduc_tree.body:
            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            ):
                lower_name = node.name.lower()

                if any(
                    token in lower_name
                    for token in (
                        "normalize",
                        "clean",
                        "strip",
                        "sanitize",
                    )
                ):
                    emit(
                        "UDUC_NORMALIZATION_HELPER",
                        uduc_path,
                        f"Function: {node.name}",
                    )

    except SyntaxError as exc:
        emit(
            "UDUC_PARSE_ERROR",
            uduc_path,
            f"{type(exc).__name__}: {exc}",
        )


# ------------------------------------------------------------
# J. Summary
# ------------------------------------------------------------

print()
print("========================================")
print("U7.1_DISCOVERY_SCAN_COMPLETE: YES")
print(f"U7.1_TOTAL_HITS={len(results)}")

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
    "U7.1_NOTE: DISCOVERY ONLY; "
    "NO PRODUCTION FILE HAS BEEN PATCHED OR DELETED."
)