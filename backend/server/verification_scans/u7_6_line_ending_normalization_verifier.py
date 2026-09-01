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


print("=== U7.6 - LINE ENDING NORMALIZATION VERIFICATION ===")


# ------------------------------------------------------------
# A. CRLF -> LF
# ------------------------------------------------------------

print()
print("=== A. CRLF NORMALIZATION ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="Title\r\nLine",
        text="A\r\nB\r\nC",
        headings=["H1\r\nH2"],
    )
)

check(
    "TITLE_CRLF_TO_LF",
    result.title == "Title\nLine",
)

check(
    "TEXT_CRLF_TO_LF",
    result.text == "A\nB\nC",
)

check(
    "HEADINGS_CRLF_TO_LF",
    result.headings == ["H1\nH2"],
)


# ------------------------------------------------------------
# B. Lone CR -> LF
# ------------------------------------------------------------

print()
print("=== B. LONE CR NORMALIZATION ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="Title\rLine",
        text="A\rB\rC",
        headings=["H1\rH2"],
    )
)

check(
    "TITLE_CR_TO_LF",
    result.title == "Title\nLine",
)

check(
    "TEXT_CR_TO_LF",
    result.text == "A\nB\nC",
)

check(
    "HEADINGS_CR_TO_LF",
    result.headings == ["H1\nH2"],
)


# ------------------------------------------------------------
# C. Existing LF preserved
# ------------------------------------------------------------

print()
print("=== C. EXISTING LF PRESERVATION ===")

source_text = "A\nB\nC"

result = normalize_uploaded_document_v1(
    make_result(
        title="Title\nLine",
        text=source_text,
        headings=["H1\nH2"],
    )
)

check(
    "EXISTING_LF_TEXT_PRESERVED",
    result.text == source_text,
)

check(
    "EXISTING_LF_TITLE_PRESERVED",
    result.title == "Title\nLine",
)

check(
    "EXISTING_LF_HEADINGS_PRESERVED",
    result.headings == ["H1\nH2"],
)


# ------------------------------------------------------------
# D. Paragraph boundary preservation
# ------------------------------------------------------------

print()
print("=== D. PARAGRAPH BOUNDARY PRESERVATION ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="Title",
        text="Paragraph one.\r\n\r\nParagraph two.",
        headings=[],
    )
)

check(
    "CRLF_BLANK_LINE_TO_LF_BLANK_LINE",
    result.text
    == "Paragraph one.\n\nParagraph two.",
)

check(
    "PARAGRAPH_BOUNDARY_NOT_COLLAPSED",
    "\n\n" in result.text,
)


# ------------------------------------------------------------
# E. Intentional single line break preservation
# ------------------------------------------------------------

print()
print("=== E. SINGLE LINE BREAK PRESERVATION ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="Title",
        text="Line one\r\nLine two",
        headings=[],
    )
)

check(
    "SINGLE_LINE_BREAK_PRESERVED",
    result.text == "Line one\nLine two",
)


# ------------------------------------------------------------
# F. No whitespace normalization yet
# ------------------------------------------------------------

print()
print("=== F. WHITESPACE DEFERRED ===")

value = "A\t  B\r\nC   D"

result = normalize_uploaded_document_v1(
    make_result(
        title=value,
        text=value,
        headings=[value],
    )
)

check(
    "TAB_PRESERVED",
    "\t" in result.text,
)

check(
    "MULTIPLE_SPACES_PRESERVED",
    "  " in result.text,
)

check(
    "INLINE_WHITESPACE_NOT_COLLAPSED",
    result.text == "A\t  B\nC   D",
)


# ------------------------------------------------------------
# G. Unicode NFC still preserved
# ------------------------------------------------------------

print()
print("=== G. U7.5 REGRESSION CHECK ===")

decomposed = "Cafe\u0301"

result = normalize_uploaded_document_v1(
    make_result(
        title=decomposed,
        text=f"{decomposed}\r\nBody",
        headings=[decomposed],
    )
)

check(
    "UNICODE_NFC_STILL_ACTIVE",
    result.title == "Café",
)

check(
    "UNICODE_AND_LINE_ENDING_COMPOSE_CORRECTLY",
    result.text == "Café\nBody",
)


# ------------------------------------------------------------
# H. Metadata operation order
# ------------------------------------------------------------

print()
print("=== H. NORMALIZATION METADATA ===")

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
    ],
)

check(
    "UNICODE_FORM_RETAINED",
    result.metadata
    .get("normalization", {})
    .get("unicode_form")
    == "NFC",
)


# ------------------------------------------------------------
# I. Source identity and provenance
# ------------------------------------------------------------

print()
print("=== I. PROVENANCE PRESERVATION ===")

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
# J. Determinism
# ------------------------------------------------------------

print()
print("=== J. DETERMINISM ===")

source = make_result(
    title="T\r\nX",
    text="A\r\n\r\nB\rC\nD",
    headings=["H\r\n1"],
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
    first.headings
    == second.headings,
)


# ------------------------------------------------------------
# K. Input immutability
# ------------------------------------------------------------

print()
print("=== K. INPUT IMMUTABILITY ===")

original = make_result(
    title="T\r\nX",
    text="A\r\nB",
    headings=["H\r\n1"],
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
# L. Final decision
# ------------------------------------------------------------

print()
print("=== L. U7.6 DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U7.6_LINE_ENDING_NORMALIZATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U7.6 line ending normalization verification failed."
    )

print(
    "U7.6_LINE_ENDING_NORMALIZATION: CERTIFIED"
)

print(
    "U7.6_CANONICAL_LINE_ENDING: LF"
)

print(
    "U7.6_CRLF_TO_LF: YES"
)

print(
    "U7.6_LONE_CR_TO_LF: YES"
)

print(
    "U7.6_PARAGRAPH_BOUNDARIES_PRESERVED: YES"
)

print(
    "U7.6_WHITESPACE_COLLAPSING_INCLUDED: NO"
)

print(
    "U7.6_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U7.7_WHITESPACE_NORMALIZATION_TRANSITION: AUTHORIZED"
)

print(
    "U7.6_FINAL_LINE_ENDING_NORMALIZATION_VERIFICATION: PASS"
)