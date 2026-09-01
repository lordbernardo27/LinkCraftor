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


print("=== U7.7 - WHITESPACE NORMALIZATION VERIFICATION ===")


# ------------------------------------------------------------
# A. Tab normalization
# ------------------------------------------------------------

print()
print("=== A. TAB NORMALIZATION ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="Title\tHere",
        text="A\tB\tC",
        headings=["Heading\tOne"],
    )
)

check(
    "TITLE_TAB_TO_SINGLE_SPACE",
    result.title == "Title Here",
)

check(
    "TEXT_TAB_TO_SINGLE_SPACE",
    result.text == "A B C",
)

check(
    "HEADINGS_TAB_TO_SINGLE_SPACE",
    result.headings == ["Heading One"],
)


# ------------------------------------------------------------
# B. Repeated ordinary spaces
# ------------------------------------------------------------

print()
print("=== B. REPEATED SPACE NORMALIZATION ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="Title   Here",
        text="A    B  C",
        headings=["Heading    One"],
    )
)

check(
    "TITLE_REPEATED_SPACES_COLLAPSED",
    result.title == "Title Here",
)

check(
    "TEXT_REPEATED_SPACES_COLLAPSED",
    result.text == "A B C",
)

check(
    "HEADINGS_REPEATED_SPACES_COLLAPSED",
    result.headings == ["Heading One"],
)


# ------------------------------------------------------------
# C. Per-line leading / trailing ordinary spaces
# ------------------------------------------------------------

print()
print("=== C. PER-LINE EDGE SPACE NORMALIZATION ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="   Title   ",
        text="   Line one   \n  Line two    ",
        headings=["   Heading one   "],
    )
)

check(
    "TITLE_EDGE_SPACES_REMOVED",
    result.title == "Title",
)

check(
    "TEXT_LINE_EDGE_SPACES_REMOVED",
    result.text == "Line one\nLine two",
)

check(
    "HEADING_EDGE_SPACES_REMOVED",
    result.headings == ["Heading one"],
)


# ------------------------------------------------------------
# D. LF structure preserved
# ------------------------------------------------------------

print()
print("=== D. LINE STRUCTURE PRESERVATION ===")

source = "Line one  \n  Line two\nLine three"

result = normalize_uploaded_document_v1(
    make_result(
        title="Title",
        text=source,
        headings=[],
    )
)

check(
    "SINGLE_LF_BOUNDARIES_PRESERVED",
    result.text
    == "Line one\nLine two\nLine three",
)

check(
    "NO_NEWLINE_TO_SPACE_CONVERSION",
    result.text.count("\n") == 2,
)


# ------------------------------------------------------------
# E. Blank-line count preserved
# ------------------------------------------------------------

print()
print("=== E. BLANK-LINE PRESERVATION ===")

source = "A\n\n\nB"

result = normalize_uploaded_document_v1(
    make_result(
        title="Title",
        text=source,
        headings=[],
    )
)

check(
    "EXCESSIVE_BLANK_LINES_NOT_YET_COLLAPSED",
    result.text == "A\n\n\nB",
)

check(
    "BLANK_LINE_COUNT_PRESERVED",
    result.text.count("\n") == 3,
)


# ------------------------------------------------------------
# F. Mixed spaces and tabs
# ------------------------------------------------------------

print()
print("=== F. MIXED HORIZONTAL WHITESPACE ===")

source = "A \t  \t B"

result = normalize_uploaded_document_v1(
    make_result(
        title=source,
        text=source,
        headings=[source],
    )
)

check(
    "MIXED_SPACE_TAB_RUN_COLLAPSED",
    result.text == "A B",
)

check(
    "MIXED_SPACE_TAB_TITLE_COLLAPSED",
    result.title == "A B",
)

check(
    "MIXED_SPACE_TAB_HEADING_COLLAPSED",
    result.headings == ["A B"],
)


# ------------------------------------------------------------
# G. NBSP preserved
# ------------------------------------------------------------

print()
print("=== G. NBSP POLICY ===")

nbsp = "\u00A0"
source = f"A{nbsp}B"

result = normalize_uploaded_document_v1(
    make_result(
        title=source,
        text=source,
        headings=[source],
    )
)

check(
    "NBSP_PRESERVED",
    result.text == source,
)

check(
    "NBSP_NOT_CONVERTED_TO_ORDINARY_SPACE",
    nbsp in result.text,
)


# ------------------------------------------------------------
# H. Zero-width policy preserved
# ------------------------------------------------------------

print()
print("=== H. ZERO-WIDTH POLICY ===")

zwj = "\u200D"
source = f"A{zwj}B"

result = normalize_uploaded_document_v1(
    make_result(
        title=source,
        text=source,
        headings=[source],
    )
)

check(
    "ZERO_WIDTH_JOINER_STILL_PRESERVED",
    zwj in result.text,
)


# ------------------------------------------------------------
# I. U7.5 Unicode regression
# ------------------------------------------------------------

print()
print("=== I. U7.5 REGRESSION CHECK ===")

decomposed = "Cafe\u0301"

result = normalize_uploaded_document_v1(
    make_result(
        title=f"  {decomposed}  ",
        text=f"  {decomposed}  ",
        headings=[f"  {decomposed}  "],
    )
)

check(
    "UNICODE_NFC_STILL_ACTIVE",
    result.text == "Café",
)


# ------------------------------------------------------------
# J. U7.6 line-ending regression
# ------------------------------------------------------------

print()
print("=== J. U7.6 REGRESSION CHECK ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="T\r\nX",
        text="A  \r\n  B\rC",
        headings=["H\r\n1"],
    )
)

check(
    "CRLF_TO_LF_STILL_ACTIVE",
    "\r\n" not in result.text,
)

check(
    "LONE_CR_TO_LF_STILL_ACTIVE",
    "\r" not in result.text,
)

check(
    "LINE_ENDING_AND_WHITESPACE_COMPOSE_CORRECTLY",
    result.text == "A\nB\nC",
)


# ------------------------------------------------------------
# K. Metadata operation order
# ------------------------------------------------------------

print()
print("=== K. NORMALIZATION METADATA ===")

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
    ],
)


# ------------------------------------------------------------
# L. Provenance preservation
# ------------------------------------------------------------

print()
print("=== L. PROVENANCE PRESERVATION ===")

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
    result.extraction_status == "success",
)

check(
    "EXTRACTION_CONFIDENCE_PRESERVED",
    result.extraction_confidence == 0.95,
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
# M. Determinism
# ------------------------------------------------------------

print()
print("=== M. DETERMINISM ===")

source = make_result(
    title="  T\t  X  ",
    text=" A\t  B \r\n  C   D ",
    headings=["  H\t 1  "],
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
# N. Input immutability
# ------------------------------------------------------------

print()
print("=== N. INPUT IMMUTABILITY ===")

original = make_result(
    title="  T\tX  ",
    text=" A\t B ",
    headings=[" H\t1 "],
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
# O. Final decision
# ------------------------------------------------------------

print()
print("=== O. U7.7 DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U7.7_WHITESPACE_NORMALIZATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U7.7 whitespace normalization verification failed."
    )

print(
    "U7.7_WHITESPACE_NORMALIZATION: CERTIFIED"
)

print(
    "U7.7_TAB_POLICY: SINGLE_ORDINARY_SPACE"
)

print(
    "U7.7_REPEATED_SPACE_POLICY: COLLAPSE_TO_ONE"
)

print(
    "U7.7_LINE_EDGE_SPACE_POLICY: REMOVE"
)

print(
    "U7.7_LINE_BOUNDARIES_PRESERVED: YES"
)

print(
    "U7.7_BLANK_LINE_COLLAPSE_INCLUDED: NO"
)

print(
    "U7.7_NBSP_REWRITTEN: NO"
)

print(
    "U7.7_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U7.8_PARAGRAPH_BOUNDARY_NORMALIZATION_TRANSITION: AUTHORIZED"
)

print(
    "U7.7_FINAL_WHITESPACE_NORMALIZATION_VERIFICATION: PASS"
)