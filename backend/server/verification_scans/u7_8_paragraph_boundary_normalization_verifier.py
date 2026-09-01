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


print("=== U7.8 - PARAGRAPH BOUNDARY NORMALIZATION VERIFICATION ===")


# ------------------------------------------------------------
# A. Excessive blank lines -> canonical paragraph separator
# ------------------------------------------------------------

print()
print("=== A. EXCESSIVE BLANK-LINE NORMALIZATION ===")

for source in (
    "A\n\n\nB",
    "A\n\n\n\nB",
    "A\n\n\n\n\n\nB",
):
    result = normalize_uploaded_document_v1(
        make_result(
            title="Title",
            text=source,
            headings=[],
        )
    )

    check(
        "EXCESSIVE_BLANK_LINES_COLLAPSED_"
        + str(source.count("\n")),
        result.text == "A\n\nB",
    )


# ------------------------------------------------------------
# B. Existing canonical paragraph boundary preserved
# ------------------------------------------------------------

print()
print("=== B. CANONICAL PARAGRAPH BOUNDARY PRESERVATION ===")

source = "Paragraph one.\n\nParagraph two."

result = normalize_uploaded_document_v1(
    make_result(
        title="Title",
        text=source,
        headings=[],
    )
)

check(
    "EXISTING_DOUBLE_LF_PRESERVED",
    result.text == source,
)


# ------------------------------------------------------------
# C. Single LF preserved
# ------------------------------------------------------------

print()
print("=== C. SINGLE LINE BREAK PRESERVATION ===")

source = "Line one\nLine two"

result = normalize_uploaded_document_v1(
    make_result(
        title="Title",
        text=source,
        headings=[],
    )
)

check(
    "SINGLE_LF_PRESERVED",
    result.text == source,
)


# ------------------------------------------------------------
# D. Leading / trailing blank lines removed
# ------------------------------------------------------------

print()
print("=== D. DOCUMENT EDGE BLANK-LINE NORMALIZATION ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="Title",
        text="\n\n\nA\n\nB\n\n\n",
        headings=[],
    )
)

check(
    "LEADING_BLANK_LINES_REMOVED",
    not result.text.startswith("\n"),
)

check(
    "TRAILING_BLANK_LINES_REMOVED",
    not result.text.endswith("\n"),
)

check(
    "INTERNAL_PARAGRAPH_BOUNDARY_PRESERVED",
    result.text == "A\n\nB",
)


# ------------------------------------------------------------
# E. Blank lines containing ordinary spaces
# ------------------------------------------------------------

print()
print("=== E. SPACE-ONLY BLANK LINES ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="Title",
        text="A\n   \n   \nB",
        headings=[],
    )
)

check(
    "SPACE_ONLY_LINES_BECOME_CANONICAL_PARAGRAPH_BOUNDARY",
    result.text == "A\n\nB",
)


# ------------------------------------------------------------
# F. Paragraph normalization is text-only
# ------------------------------------------------------------

print()
print("=== F. TEXT-ONLY PARAGRAPH NORMALIZATION ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="A\n\n\nB",
        text="A\n\n\nB",
        headings=["H1\n\n\nH2"],
    )
)

check(
    "TEXT_PARAGRAPH_BOUNDARY_COLLAPSED",
    result.text == "A\n\nB",
)

check(
    "TITLE_NOT_PARAGRAPH_COLLAPSED",
    result.title == "A\n\n\nB",
)

check(
    "HEADING_NOT_PARAGRAPH_COLLAPSED",
    result.headings == ["H1\n\n\nH2"],
)


# ------------------------------------------------------------
# G. No paragraph objects or UDUC structure
# ------------------------------------------------------------

print()
print("=== G. UDUC BOUNDARY ===")

check(
    "RESULT_HAS_NO_STRUCTURE_FIELD",
    not hasattr(result, "structure"),
)

check(
    "RESULT_HAS_NO_PARAGRAPHS_FIELD",
    not hasattr(result, "paragraphs"),
)

check(
    "RESULT_HAS_NO_HEADING_MAP_FIELD",
    not hasattr(result, "heading_map"),
)


# ------------------------------------------------------------
# H. U7.5 Unicode regression
# ------------------------------------------------------------

print()
print("=== H. U7.5 REGRESSION CHECK ===")

decomposed = "Cafe\u0301"

result = normalize_uploaded_document_v1(
    make_result(
        title=decomposed,
        text=f"{decomposed}\n\n\nBody",
        headings=[decomposed],
    )
)

check(
    "UNICODE_NFC_STILL_ACTIVE",
    result.title == "Café",
)

check(
    "UNICODE_AND_PARAGRAPH_NORMALIZATION_COMPOSE",
    result.text == "Café\n\nBody",
)


# ------------------------------------------------------------
# I. U7.6 line-ending regression
# ------------------------------------------------------------

print()
print("=== I. U7.6 REGRESSION CHECK ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="T\r\nX",
        text="A\r\n\r\n\r\nB\rC",
        headings=["H\r\n1"],
    )
)

check(
    "CRLF_AND_CR_STILL_NORMALIZED",
    "\r" not in result.text,
)

check(
    "LINE_ENDING_AND_PARAGRAPH_RULES_COMPOSE",
    result.text == "A\n\nB\nC",
)


# ------------------------------------------------------------
# J. U7.7 whitespace regression
# ------------------------------------------------------------

print()
print("=== J. U7.7 REGRESSION CHECK ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="  T\t X  ",
        text="  A   B  \n   \n   \n  C\tD  ",
        headings=["  H\t 1  "],
    )
)

check(
    "HORIZONTAL_WHITESPACE_STILL_ACTIVE",
    result.title == "T X",
)

check(
    "WHITESPACE_AND_PARAGRAPH_RULES_COMPOSE",
    result.text == "A B\n\nC D",
)

check(
    "HEADING_WHITESPACE_STILL_ACTIVE",
    result.headings == ["H 1"],
)


# ------------------------------------------------------------
# K. NBSP / zero-width policies preserved
# ------------------------------------------------------------

print()
print("=== K. UNICODE SPACING POLICY PRESERVATION ===")

nbsp = "\u00A0"
zwj = "\u200D"

source = f"A{nbsp}B\n\n\nC{zwj}D"

result = normalize_uploaded_document_v1(
    make_result(
        title="Title",
        text=source,
        headings=[],
    )
)

check(
    "NBSP_STILL_PRESERVED",
    nbsp in result.text,
)

check(
    "ZERO_WIDTH_JOINER_STILL_PRESERVED",
    zwj in result.text,
)

check(
    "PARAGRAPH_NORMALIZATION_DOES_NOT_REMOVE_UNICODE_SPACING",
    result.text == f"A{nbsp}B\n\nC{zwj}D",
)


# ------------------------------------------------------------
# L. Metadata operation order
# ------------------------------------------------------------

print()
print("=== L. NORMALIZATION METADATA ===")

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
    ],
)


# ------------------------------------------------------------
# M. Provenance preservation
# ------------------------------------------------------------

print()
print("=== M. PROVENANCE PRESERVATION ===")

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
# N. Determinism
# ------------------------------------------------------------

print()
print("=== N. DETERMINISM ===")

source = make_result(
    title=" T ",
    text="\n\n A   B \r\n\r\n\r\n C\tD \n\n",
    headings=[" H  1 "],
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
# O. Input immutability
# ------------------------------------------------------------

print()
print("=== O. INPUT IMMUTABILITY ===")

original = make_result(
    title=" T ",
    text="\n\nA\n\n\nB\n\n",
    headings=[" H "],
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
# P. Final decision
# ------------------------------------------------------------

print()
print("=== P. U7.8 DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U7.8_PARAGRAPH_BOUNDARY_NORMALIZATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U7.8 paragraph-boundary normalization verification failed."
    )

print(
    "U7.8_PARAGRAPH_BOUNDARY_NORMALIZATION: CERTIFIED"
)

print(
    "U7.8_CANONICAL_PARAGRAPH_SEPARATOR: DOUBLE_LF"
)

print(
    "U7.8_EXCESSIVE_BLANK_LINES_COLLAPSED: YES"
)

print(
    "U7.8_SINGLE_LF_PRESERVED: YES"
)

print(
    "U7.8_DOCUMENT_EDGE_BLANK_LINES_REMOVED: YES"
)

print(
    "U7.8_TEXT_ONLY_PARAGRAPH_NORMALIZATION: YES"
)

print(
    "U7.8_UDUC_STRUCTURE_CREATED: NO"
)

print(
    "U7.8_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U7.9_HEADING_NORMALIZATION_TRANSITION: AUTHORIZED"
)

print(
    "U7.8_FINAL_PARAGRAPH_BOUNDARY_NORMALIZATION_VERIFICATION: PASS"
)