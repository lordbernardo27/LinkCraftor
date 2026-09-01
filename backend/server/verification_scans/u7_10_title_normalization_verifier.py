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
    source_path: str = "C:/immutable/source.txt",
) -> UploadExtractionResult:
    return UploadExtractionResult(
        source_path=source_path,
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


print("=== U7.10 - TITLE NORMALIZATION VERIFICATION ===")


# ------------------------------------------------------------
# A. Basic title normalization
# ------------------------------------------------------------

print()
print("=== A. BASIC TITLE NORMALIZATION ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="   My\t  Title   ",
        text="Body",
        headings=[],
    )
)

check(
    "TITLE_HORIZONTAL_WHITESPACE_NORMALIZED",
    result.title == "My Title",
)


# ------------------------------------------------------------
# B. Unicode title normalization
# ------------------------------------------------------------

print()
print("=== B. UNICODE TITLE NORMALIZATION ===")

decomposed = "Cafe\u0301"

result = normalize_uploaded_document_v1(
    make_result(
        title=decomposed,
        text="Body",
        headings=[],
    )
)

check(
    "TITLE_UNICODE_NFC",
    result.title == "Café",
)


# ------------------------------------------------------------
# C. Title line endings
# ------------------------------------------------------------

print()
print("=== C. TITLE LINE ENDING NORMALIZATION ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="Line One\r\nLine Two\rLine Three",
        text="Body",
        headings=[],
    )
)

check(
    "TITLE_CRLF_AND_CR_TO_LF",
    result.title
    == "Line One\nLine Two\nLine Three",
)


# ------------------------------------------------------------
# D. Multi-line title preservation
# ------------------------------------------------------------

print()
print("=== D. MULTI-LINE TITLE PRESERVATION ===")

source = "Part One\nPart Two"

result = normalize_uploaded_document_v1(
    make_result(
        title=source,
        text="Body",
        headings=[],
    )
)

check(
    "TITLE_SINGLE_LF_PRESERVED",
    result.title == source,
)


# ------------------------------------------------------------
# E. No paragraph collapsing in title
# ------------------------------------------------------------

print()
print("=== E. TITLE PARAGRAPH BOUNDARY EXCLUSION ===")

source = "A\n\n\nB"

result = normalize_uploaded_document_v1(
    make_result(
        title=source,
        text="Body",
        headings=[],
    )
)

check(
    "TITLE_NOT_PARAGRAPH_COLLAPSED",
    result.title == source,
)


# ------------------------------------------------------------
# F. Empty title behavior
# ------------------------------------------------------------

print()
print("=== F. EMPTY TITLE CONTRACT ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="",
        text="Body",
        headings=["First Heading"],
        source_path="C:/immutable/fallback-name.txt",
    )
)

check(
    "EMPTY_TITLE_REMAINS_EMPTY",
    result.title == "",
)

check(
    "NO_FIRST_HEADING_FALLBACK",
    result.title != "First Heading",
)

check(
    "NO_FILENAME_FALLBACK",
    result.title != "fallback-name",
)

check(
    "NO_BODY_FALLBACK",
    result.title != "Body",
)


# ------------------------------------------------------------
# G. Whitespace-only title behavior
# ------------------------------------------------------------

print()
print("=== G. WHITESPACE-ONLY TITLE ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="   \t   ",
        text="Body",
        headings=["Heading"],
    )
)

check(
    "WHITESPACE_ONLY_TITLE_NORMALIZES_EMPTY",
    result.title == "",
)

check(
    "WHITESPACE_ONLY_TITLE_NOT_REPLACED",
    result.title != "Heading",
)


# ------------------------------------------------------------
# H. Non-English title preservation
# ------------------------------------------------------------

print()
print("=== H. NON-ENGLISH TITLE PRESERVATION ===")

samples = {
    "GREEK": "Καλημέρα κόσμε",
    "CYRILLIC": "Привет мир",
    "ARABIC": "مرحبا بالعالم",
    "HEBREW": "שלום עולם",
    "CJK": "東京 世界",
    "ACCENTED_LATIN": "São Tomé",
}

for name, value in samples.items():
    result = normalize_uploaded_document_v1(
        make_result(
            title=value,
            text="Body",
            headings=[],
        )
    )

    check(
        name + "_TITLE_PRESERVED",
        result.title == value,
    )


# ------------------------------------------------------------
# I. Symbols / punctuation preservation
# ------------------------------------------------------------

print()
print("=== I. TITLE SYMBOL PRESERVATION ===")

value = "“Title” — € £ ¥ ± ∑ © ™"

result = normalize_uploaded_document_v1(
    make_result(
        title=value,
        text="Body",
        headings=[],
    )
)

check(
    "TITLE_SYMBOLS_PRESERVED",
    result.title == value,
)


# ------------------------------------------------------------
# J. NBSP / zero-width policy
# ------------------------------------------------------------

print()
print("=== J. TITLE UNICODE SPACING POLICY ===")

nbsp = "\u00A0"
zwj = "\u200D"

result = normalize_uploaded_document_v1(
    make_result(
        title=f"A{nbsp}B{zwj}C",
        text="Body",
        headings=[],
    )
)

check(
    "TITLE_NBSP_PRESERVED",
    nbsp in result.title,
)

check(
    "TITLE_ZERO_WIDTH_JOINER_PRESERVED",
    zwj in result.title,
)


# ------------------------------------------------------------
# K. No title re-extraction
# ------------------------------------------------------------

print()
print("=== K. EXTRACTOR TITLE AUTHORITY ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="Extractor Title",
        text="Different Body Title\n\nBody",
        headings=["Different Heading"],
        source_path="C:/immutable/DifferentFilename.txt",
    )
)

check(
    "EXTRACTOR_TITLE_REMAINS_AUTHORITY",
    result.title == "Extractor Title",
)

check(
    "BODY_NOT_USED_AS_TITLE",
    result.title != "Different Body Title",
)

check(
    "HEADING_NOT_USED_AS_TITLE",
    result.title != "Different Heading",
)

check(
    "SOURCE_PATH_NOT_USED_AS_TITLE",
    result.title != "DifferentFilename",
)


# ------------------------------------------------------------
# L. Text normalization unchanged
# ------------------------------------------------------------

print()
print("=== L. TEXT NORMALIZATION REGRESSION ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="Title",
        text="\n\n A   B \r\n\r\n\r\n C\tD \n\n",
        headings=[],
    )
)

check(
    "TEXT_NORMALIZATION_STILL_ACTIVE",
    result.text == "A B\n\nC D",
)


# ------------------------------------------------------------
# M. Heading normalization unchanged
# ------------------------------------------------------------

print()
print("=== M. HEADING NORMALIZATION REGRESSION ===")

result = normalize_uploaded_document_v1(
    make_result(
        title="Title",
        text="Body",
        headings=[
            "  H\t 1  ",
            "",
            "  H\t 1  ",
        ],
    )
)

check(
    "HEADING_NORMALIZATION_STILL_ACTIVE",
    result.headings == ["H 1", "H 1"],
)


# ------------------------------------------------------------
# N. Metadata operation order
# ------------------------------------------------------------

print()
print("=== N. NORMALIZATION METADATA ===")

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
        "title_normalization",
    ],
)


# ------------------------------------------------------------
# O. Provenance preservation
# ------------------------------------------------------------

print()
print("=== O. PROVENANCE PRESERVATION ===")

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
# P. Determinism
# ------------------------------------------------------------

print()
print("=== P. DETERMINISM ===")

source = make_result(
    title="  Cafe\u0301\t Title  ",
    text=" A  B\n\n\nC ",
    headings=[
        " H\t1 ",
        "",
        " H\t1 ",
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
# Q. Input immutability
# ------------------------------------------------------------

print()
print("=== Q. INPUT IMMUTABILITY ===")

original = make_result(
    title="  Title\tHere  ",
    text=" A  B ",
    headings=[" H\t1 "],
)

before = (
    original.source_path,
    original.title,
    original.text,
    list(original.headings),
    dict(original.metadata),
)

normalize_uploaded_document_v1(
    original
)

after = (
    original.source_path,
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
# R. UDUC / downstream boundary
# ------------------------------------------------------------

print()
print("=== R. DOWNSTREAM BOUNDARY ===")

check(
    "RESULT_HAS_NO_STRUCTURE",
    not hasattr(result, "structure"),
)

check(
    "RESULT_HAS_NO_HEADING_MAP",
    not hasattr(result, "heading_map"),
)

check(
    "RESULT_HAS_NO_UUCD_FIELD",
    not hasattr(result, "uucd"),
)

check(
    "RESULT_HAS_NO_SEMANTIC_SCORE",
    not hasattr(result, "semantic_score"),
)


# ------------------------------------------------------------
# S. Final decision
# ------------------------------------------------------------

print()
print("=== S. U7.10 DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U7.10_TITLE_NORMALIZATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U7.10 title normalization verification failed."
    )

print(
    "U7.10_TITLE_NORMALIZATION: CERTIFIED"
)

print(
    "U7.10_EMPTY_TITLE_PRESERVED: YES"
)

print(
    "U7.10_FILENAME_FALLBACK: NO"
)

print(
    "U7.10_HEADING_FALLBACK: NO"
)

print(
    "U7.10_BODY_FALLBACK: NO"
)

print(
    "U7.10_TITLE_REEXTRACTION: NO"
)

print(
    "U7.10_MULTI_LINE_TITLE_PRESERVED: YES"
)

print(
    "U7.10_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U7.11_CONTROL_CHARACTER_HANDLING_TRANSITION: AUTHORIZED"
)

print(
    "U7.10_FINAL_TITLE_NORMALIZATION_VERIFICATION: PASS"
)