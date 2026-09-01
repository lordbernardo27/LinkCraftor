from __future__ import annotations

from backend.server.stores.upload_document_extractor import (
    UploadExtractionResult,
)

from backend.server.stores.upload_document_normalizer import (
    normalize_uploaded_document_v1,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def make_result(
    *,
    title: str,
    text: str,
    headings: list[str],
) -> UploadExtractionResult:
    return UploadExtractionResult(
        source_path="C:/immutable/source.txt",
        source_type="txt",
        title=title,
        text=text,
        headings=headings,
        metadata={
            "filename": "source.txt",
            "custom": "preserve-me",
        },
        extraction_status="success",
        extraction_confidence=0.95,
        created_at="2026-08-31T00:00:00+00:00",
    )


print("=== U7.9 - HEADING NORMALIZATION VERIFICATION ===")


# ------------------------------------------------------------
# A. Basic heading normalization
# ------------------------------------------------------------

print()
print("=== A. BASIC HEADING NORMALIZATION ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="Title",
        text="Body",
        headings=[
            "  Heading   One  ",
            "Heading\tTwo",
            "Heading\r\nThree",
        ],
    )
)

check(
    "HEADING_SPACES_NORMALIZED",
    result.headings[0] == "Heading One",
)

check(
    "HEADING_TAB_NORMALIZED",
    result.headings[1] == "Heading Two",
)

check(
    "HEADING_CRLF_NORMALIZED",
    result.headings[2] == "Heading\nThree",
)


# ------------------------------------------------------------
# B. Empty headings removed
# ------------------------------------------------------------

print()
print("=== B. EMPTY HEADING REMOVAL ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="Title",
        text="Body",
        headings=[
            "",
            "   ",
            "\t",
            "Valid Heading",
            " \t ",
        ],
    )
)

check(
    "EMPTY_HEADINGS_REMOVED",
    result.headings == ["Valid Heading"],
)


# ------------------------------------------------------------
# C. Heading order preserved
# ------------------------------------------------------------

print()
print("=== C. HEADING ORDER PRESERVATION ===")

source_headings = [
    "Third",
    "First",
    "Second",
]

result = normalize_uploaded_document_v1(
    make_result(
        title="Title",
        text="Body",
        headings=source_headings,
    )
)

check(
    "HEADING_ORDER_PRESERVED",
    result.headings
    == [
        "Third",
        "First",
        "Second",
    ],
)


# ------------------------------------------------------------
# D. Duplicate headings preserved
# ------------------------------------------------------------

print()
print("=== D. DUPLICATE HEADING PRESERVATION ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="Title",
        text="Body",
        headings=[
            "Overview",
            "Details",
            "Overview",
        ],
    )
)

check(
    "DUPLICATE_HEADINGS_PRESERVED",
    result.headings
    == [
        "Overview",
        "Details",
        "Overview",
    ],
)

check(
    "NO_HEADING_DEDUPLICATION",
    result.headings.count("Overview") == 2,
)


# ------------------------------------------------------------
# E. Multi-line headings preserved
# ------------------------------------------------------------

print()
print("=== E. MULTI-LINE HEADING PRESERVATION ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="Title",
        text="Body",
        headings=[
            "Part One\r\nPart Two",
            "A\n\n\nB",
        ],
    )
)

check(
    "SINGLE_LF_IN_HEADING_PRESERVED",
    result.headings[0]
    == "Part One\nPart Two",
)

check(
    "HEADING_PARAGRAPH_COLLAPSE_NOT_APPLIED",
    result.headings[1]
    == "A\n\n\nB",
)


# ------------------------------------------------------------
# F. Unicode headings
# ------------------------------------------------------------

print()
print("=== F. UNICODE HEADING PRESERVATION ===")

decomposed = "Cafe\u0301"

unicode_headings = [
    decomposed,
    "Καλημέρα",
    "Привет",
    "مرحبا",
    "שלום",
    "東京",
    "€ ± ∑",
]

result = normalize_uploaded_document_v1(
    make_result(
        title="Title",
        text="Body",
        headings=unicode_headings,
    )
)

check(
    "ACCENTED_HEADING_NFC",
    result.headings[0] == "Café",
)

check(
    "GREEK_HEADING_PRESERVED",
    "Καλημέρα" in result.headings,
)

check(
    "CYRILLIC_HEADING_PRESERVED",
    "Привет" in result.headings,
)

check(
    "ARABIC_HEADING_PRESERVED",
    "مرحبا" in result.headings,
)

check(
    "HEBREW_HEADING_PRESERVED",
    "שלום" in result.headings,
)

check(
    "CJK_HEADING_PRESERVED",
    "東京" in result.headings,
)

check(
    "SYMBOL_HEADING_PRESERVED",
    "€ ± ∑" in result.headings,
)


# ------------------------------------------------------------
# G. No heading structural interpretation
# ------------------------------------------------------------

print()
print("=== G. HEADING STRUCTURAL BOUNDARY ===")

check(
    "RESULT_HAS_NO_HEADING_LEVELS",
    not hasattr(result, "heading_levels"),
)

check(
    "RESULT_HAS_NO_HEADING_MAP",
    not hasattr(result, "heading_map"),
)

check(
    "RESULT_HAS_NO_STRUCTURE",
    not hasattr(result, "structure"),
)

check(
    "RESULT_HAS_NO_DOCUMENT_ORDER",
    not hasattr(result, "document_order"),
)


# ------------------------------------------------------------
# H. No body-position mapping
# ------------------------------------------------------------

print()
print("=== H. NO BODY POSITION MAPPING ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="Title",
        text="Intro\n\nOverview\n\nBody",
        headings=["Overview"],
    )
)

check(
    "HEADING_REMAINS_PLAIN_STRING",
    result.headings == ["Overview"],
)

check(
    "NO_HEADING_POSITION_FIELD",
    not hasattr(result, "heading_positions"),
)


# ------------------------------------------------------------
# I. No title promotion
# ------------------------------------------------------------

print()
print("=== I. NO HEADING TO TITLE PROMOTION ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="Original Title",
        text="Body",
        headings=[
            "First Heading",
        ],
    )
)

check(
    "TITLE_NOT_REPLACED_BY_FIRST_HEADING",
    result.title == "Original Title",
)


# ------------------------------------------------------------
# J. U7.5 Unicode regression
# ------------------------------------------------------------

print()
print("=== J. U7.5 REGRESSION CHECK ===")

result = normalize_uploaded_document_v1(
    make_result(
        title=decomposed,
        text=decomposed,
        headings=[decomposed],
    )
)

check(
    "UNICODE_NFC_STILL_ACTIVE",
    result.title == "Café"
    and result.text == "Café"
    and result.headings == ["Café"],
)


# ------------------------------------------------------------
# K. U7.6 line-ending regression
# ------------------------------------------------------------

print()
print("=== K. U7.6 REGRESSION CHECK ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="A\rB",
        text="A\r\nB\rC",
        headings=["H\r\n1"],
    )
)

check(
    "LINE_ENDINGS_STILL_NORMALIZED",
    result.title == "A\nB"
    and result.text == "A\nB\nC"
    and result.headings == ["H\n1"],
)


# ------------------------------------------------------------
# L. U7.7 whitespace regression
# ------------------------------------------------------------

print()
print("=== L. U7.7 REGRESSION CHECK ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="  T\t X ",
        text=" A   B ",
        headings=[" H\t  1 "],
    )
)

check(
    "HORIZONTAL_WHITESPACE_STILL_ACTIVE",
    result.title == "T X"
    and result.text == "A B"
    and result.headings == ["H 1"],
)


# ------------------------------------------------------------
# M. U7.8 paragraph regression
# ------------------------------------------------------------

print()
print("=== M. U7.8 REGRESSION CHECK ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="Title",
        text="\n\nA\n\n\n\nB\n\n",
        headings=["Heading"],
    )
)

check(
    "TEXT_PARAGRAPH_NORMALIZATION_STILL_ACTIVE",
    result.text == "A\n\nB",
)


# ------------------------------------------------------------
# N. Unicode spacing policy
# ------------------------------------------------------------

print()
print("=== N. UNICODE SPACING POLICY ===")

nbsp = "\u00A0"
zwj = "\u200D"

result = normalize_uploaded_document_v1(
    make_result(
        title="Title",
        text="Body",
        headings=[
            f"A{nbsp}B",
            f"C{zwj}D",
        ],
    )
)

check(
    "HEADING_NBSP_PRESERVED",
    result.headings[0]
    == f"A{nbsp}B",
)

check(
    "HEADING_ZERO_WIDTH_JOINER_PRESERVED",
    result.headings[1]
    == f"C{zwj}D",
)


# ------------------------------------------------------------
# O. Metadata operation order
# ------------------------------------------------------------

print()
print("=== O. NORMALIZATION METADATA ===")

operations = (
    result.metadata
    .get("normalization", {})
    .get("operations")
)

check(
    "NORMALIZATION_OPERATIONS_ORDER",
    operations
    == [
        "unicode_nfc",
        "line_endings_lf",
        "horizontal_whitespace",
        "paragraph_boundaries",
        "heading_normalization",
    ],
)


# ------------------------------------------------------------
# P. Provenance preservation
# ------------------------------------------------------------

print()
print("=== P. PROVENANCE PRESERVATION ===")

check(
    "SOURCE_PATH_PRESERVED",
    result.source_path
    == "C:/immutable/source.txt",
)

check(
    "SOURCE_TYPE_PRESERVED",
    result.source_type == "txt",
)

check(
    "EXTRACTION_STATUS_PRESERVED",
    result.extraction_status
    == "success",
)

check(
    "EXTRACTION_CONFIDENCE_PRESERVED",
    result.extraction_confidence
    == 0.95,
)

check(
    "EXTRACTION_TIMESTAMP_PRESERVED",
    result.extraction_created_at
    == "2026-08-31T00:00:00+00:00",
)

check(
    "CUSTOM_METADATA_PRESERVED",
    result.metadata.get("custom")
    == "preserve-me",
)


# ------------------------------------------------------------
# Q. Determinism
# ------------------------------------------------------------

print()
print("=== Q. DETERMINISM ===")

source = make_result(
    title=" T ",
    text=" A  B\n\n\nC ",
    headings=[
        " H\t1 ",
        "",
        " H\t1 ",
        " Multi\r\nLine ",
    ],
)

first = normalize_uploaded_document_v1(
    source
)

second = normalize_uploaded_document_v1(
    source
)

check(
    "DETERMINISTIC_TITLE",
    first.title == second.title,
)

check(
    "DETERMINISTIC_TEXT",
    first.text == second.text,
)

check(
    "DETERMINISTIC_HEADINGS",
    first.headings == second.headings,
)


# ------------------------------------------------------------
# R. Input immutability
# ------------------------------------------------------------

print()
print("=== R. INPUT IMMUTABILITY ===")

original = make_result(
    title=" T ",
    text=" A  B ",
    headings=[
        " H\t1 ",
        "",
        " H\t1 ",
    ],
)

before = (
    original.title,
    original.text,
    list(original.headings),
    dict(original.metadata),
)

normalize_uploaded_document_v1(
    original
)

after = (
    original.title,
    original.text,
    list(original.headings),
    dict(original.metadata),
)

check(
    "UPLOAD_EXTRACTION_RESULT_NOT_MUTATED",
    before == after,
)


# ------------------------------------------------------------
# S. Final decision
# ------------------------------------------------------------

print()
print("=== S. U7.9 DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U7.9_HEADING_NORMALIZATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U7.9 heading normalization verification failed."
    )

print(
    "U7.9_HEADING_NORMALIZATION: CERTIFIED"
)

print(
    "U7.9_EMPTY_HEADINGS_REMOVED: YES"
)

print(
    "U7.9_HEADING_ORDER_PRESERVED: YES"
)

print(
    "U7.9_DUPLICATE_HEADINGS_PRESERVED: YES"
)

print(
    "U7.9_MULTI_LINE_HEADINGS_PRESERVED: YES"
)

print(
    "U7.9_HEADING_LEVEL_INFERENCE: NO"
)

print(
    "U7.9_HEADING_POSITION_MAPPING: NO"
)

print(
    "U7.9_TITLE_PROMOTION: NO"
)

print(
    "U7.9_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U7.10_TITLE_NORMALIZATION_TRANSITION: AUTHORIZED"
)

print(
    "U7.9_FINAL_HEADING_NORMALIZATION_VERIFICATION: PASS"
)