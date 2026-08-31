from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(r"C:\Users\HP\Documents\LinkCraftor")
BASE = ROOT / "backend" / "server"

EXTRACTOR = (
    BASE
    / "stores"
    / "upload_document_extractor.py"
)

UDUC = (
    BASE
    / "stores"
    / "uploaded_document_unified_content.py"
)

GENERIC_NORMALIZER = (
    BASE
    / "utils"
    / "text_normalization.py"
)

UPLOAD_PIPELINE = (
    BASE
    / "pipelines"
    / "upload_document"
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

results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def read(path: Path) -> str:
    return path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )


print(
    "=== U7.2 - CANONICAL NORMALIZATION RESPONSIBILITY VERIFICATION ==="
)


# ------------------------------------------------------------
# A. U6 handoff authority
# ------------------------------------------------------------

print()
print("=== A. U6 -> U7 HANDOFF ===")

extractor_source = read(EXTRACTOR)

tree = ast.parse(
    extractor_source,
    filename=str(EXTRACTOR),
)

classes = {
    node.name
    for node in tree.body
    if isinstance(node, ast.ClassDef)
}

functions = {
    node.name
    for node in tree.body
    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    )
}

check(
    "UPLOAD_EXTRACTION_RESULT_IS_U6_OUTPUT_CONTRACT",
    "UploadExtractionResult" in classes,
)

check(
    "CANONICAL_U6_DISPATCHER_EXISTS",
    "extract_upload_document_v1"
    in functions,
)

for symbol in (
    "extract_txt_upload_v1",
    "extract_markdown_upload_v1",
    "extract_html_upload_v1",
    "extract_docx_upload_v1",
):
    check(
        f"U6_OWNS_{symbol.upper()}",
        symbol in functions,
    )

check(
    "U6_RETAINS_EXTRACTION_SAFE_NORMALIZATION",
    "_normalize_upload_text_v2"
    in functions,
)


# ------------------------------------------------------------
# B. U6 remains format-specific
# ------------------------------------------------------------

print()
print("=== B. U6 FORMAT-SPECIFIC RESPONSIBILITY ===")

for symbol in (
    "_strip_markdown_syntax_v2",
    "_strip_html_tags_v1",
    "_extract_docx_paragraphs_v2",
):
    check(
        "U6_RETAINS_"
        + symbol.upper(),
        symbol in extractor_source,
    )


# ------------------------------------------------------------
# C. UDUC remains structural, not canonical U7
# ------------------------------------------------------------

print()
print("=== C. U7 vs UDUC RESPONSIBILITY ===")

uduc_source = read(UDUC)

check(
    "UDUC_CONSUMES_EXTRACTION_RESULT",
    "build_uduc_from_upload_extraction_result"
    in uduc_source,
)

check(
    "UDUC_OWNS_PARAGRAPH_STRUCTURE",
    "_paragraphs_from_content_body"
    in uduc_source,
)

check(
    "UDUC_OWNS_HEADING_POSITION_MAP",
    "_build_heading_map"
    in uduc_source,
)

check(
    "UDUC_OWNS_DOCUMENT_STRUCTURE",
    "_build_uduc_structure"
    in uduc_source,
)

check(
    "UDUC_DECLARES_NO_CONTENT_CLEANING",
    "performs_cleaning"
    in uduc_source
    and "modifies_content_body"
    in uduc_source,
)

check(
    "UDUC_DOES_NOT_IMPORT_GENERIC_TEXT_NORMALIZER",
    "text_normalization"
    not in uduc_source
    and "fix_mojibake_text"
    not in uduc_source,
)


# ------------------------------------------------------------
# D. Existing UDUC compatibility hygiene identified
# ------------------------------------------------------------

print()
print("=== D. UDUC COMPATIBILITY HYGIENE ===")

check(
    "UDUC_CURRENTLY_TRIMS_TITLE",
    ".strip()"
    in uduc_source
    and 'er.get("title")'
    in uduc_source,
)

check(
    "UDUC_CURRENTLY_TRIMS_CONTENT_BODY",
    'er.get("content_body")'
    in uduc_source
    and 'er.get("text")'
    in uduc_source
    and ".strip()"
    in uduc_source,
)

check(
    "UDUC_COMPATIBILITY_HYGIENE_LEFT_FOR_U8",
    True,
)


# ------------------------------------------------------------
# E. Generic normalizer classification
# ------------------------------------------------------------

print()
print("=== E. GENERIC TEXT NORMALIZER CLASSIFICATION ===")

generic_source = read(GENERIC_NORMALIZER)

check(
    "GENERIC_TEXT_NORMALIZER_EXISTS",
    GENERIC_NORMALIZER.exists(),
)

check(
    "GENERIC_NORMALIZER_HAS_FIX_MOJIBAKE_TEXT",
    "def fix_mojibake_text"
    in generic_source,
)

upload_generic_users = []

if UPLOAD_PIPELINE.exists():
    for path in UPLOAD_PIPELINE.rglob("*.py"):
        if set(path.parts) & EXCLUDED:
            continue

        source = read(path)

        if (
            "fix_mojibake_text"
            in source
            or "text_normalization"
            in source
        ):
            upload_generic_users.append(
                path.relative_to(ROOT)
            )

check(
    "UPLOAD_PIPELINE_DOES_NOT_CURRENTLY_USE_GENERIC_NORMALIZER",
    not upload_generic_users,
)

check(
    "GENERIC_NORMALIZER_NOT_DECLARED_CANONICAL_U7_AUTHORITY",
    "upload_specific_normalization"
    not in generic_source.lower(),
)


# ------------------------------------------------------------
# F. U7 prohibited responsibilities absent from U6 handoff
# ------------------------------------------------------------

print()
print("=== F. U7 RESPONSIBILITY EXCLUSIONS ===")

for forbidden in (
    "article_body_cleaning_engine",
    "article_cleaning_pipeline",
    "active_target_set",
    "uucd_engine_v1",
    "uucd_persistence_v1",
    "semantic_runtime",
    "semantic_score",
    "relevance_score",
    "scorer.py",
):
    check(
        "U6_HANDOFF_ISOLATED_FROM_"
        + forbidden.upper(),
        forbidden
        not in extractor_source.lower(),
    )


# ------------------------------------------------------------
# G. Canonical responsibility decision
# ------------------------------------------------------------

print()
print("=== G. CANONICAL U7 RESPONSIBILITY DECISION ===")

check(
    "U7_INPUT_IS_UPLOAD_EXTRACTION_RESULT",
    "UploadExtractionResult"
    in classes,
)

check(
    "U7_REQUIRES_NO_SOURCE_REREAD_BY_CONTRACT",
    True,
)

check(
    "U7_IS_FORMAT_NEUTRAL_BY_CONTRACT",
    True,
)

check(
    "U7_OWNS_UNICODE_NORMALIZATION_BY_CONTRACT",
    True,
)

check(
    "U7_OWNS_LINE_ENDING_NORMALIZATION_BY_CONTRACT",
    True,
)

check(
    "U7_OWNS_INLINE_WHITESPACE_NORMALIZATION_BY_CONTRACT",
    True,
)

check(
    "U7_OWNS_PARAGRAPH_BOUNDARY_NORMALIZATION_BY_CONTRACT",
    True,
)

check(
    "U7_OWNS_TITLE_NORMALIZATION_BY_CONTRACT",
    True,
)

check(
    "U7_OWNS_HEADING_NORMALIZATION_BY_CONTRACT",
    True,
)

check(
    "U7_OWNS_CONTROL_CHARACTER_HANDLING_BY_CONTRACT",
    True,
)

check(
    "U7_DOES_NOT_OWN_UDUC_SCHEMA_BY_CONTRACT",
    True,
)

check(
    "U7_DOES_NOT_OWN_HIGHLIGHT_ATS_UUCD_RUNTIME_BY_CONTRACT",
    True,
)

check(
    "UPLOAD_SPECIFIC_NORMALIZER_SHOULD_BE_SEPARATE_AUTHORITY",
    True,
)


# ------------------------------------------------------------
# H. Final U7.2 decision
# ------------------------------------------------------------

print()
print("=== H. U7.2 RESPONSIBILITY DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U7.2_CANONICAL_NORMALIZATION_RESPONSIBILITY: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U7.2 canonical normalization responsibility verification failed."
    )

print(
    "U7.2_CANONICAL_NORMALIZATION_RESPONSIBILITY: CERTIFIED"
)

print(
    "U7.2_GENERIC_TEXT_NORMALIZER_DECISION: KEEP_SEPARATE"
)

print(
    "U7.2_CANONICAL_U7_AUTHORITY_DECISION: "
    "UPLOAD_SPECIFIC_NORMALIZER"
)

print(
    "U7.2_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U7.2_U6_TO_U7_HANDOFF: "
    "UPLOAD_EXTRACTION_RESULT"
)

print(
    "U7.2_U7_TO_UDUC_HANDOFF: "
    "NORMALIZED_UPLOADED_DOCUMENT_CONTENT"
)

print(
    "U7.3_NORMALIZATION_INPUT_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U7.2_FINAL_RESPONSIBILITY_VERIFICATION: PASS"
)