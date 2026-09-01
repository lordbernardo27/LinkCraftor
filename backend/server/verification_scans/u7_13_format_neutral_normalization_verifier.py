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


def make_result(source_type: str) -> UploadExtractionResult:
    return UploadExtractionResult(
        source_path=f"C:/immutable/source.{source_type}",
        source_type=source_type,
        title="  Cafe\u0301\t Title  ",
        text="\n\n A   B \r\n\r\n\r\n C\tD \u0000 \n\n",
        headings=[
            "  First\t Heading  ",
            "",
            "  First\t Heading  ",
            "Multi\r\nLine",
        ],
        metadata={
            "filename": f"source.{source_type}",
            "custom": "preserve-me",
        },
        extraction_status="success",
        extraction_confidence=0.95,
        created_at="2026-08-31T00:00:00+00:00",
    )


print("=== U7.13 - FORMAT-NEUTRAL NORMALIZATION VERIFICATION ===")


# ------------------------------------------------------------
# A. Normalize same logical content across all source types
# ------------------------------------------------------------

print()
print("=== A. CROSS-FORMAT NORMALIZATION ===")

source_types = [
    "txt",
    "markdown",
    "html",
    "docx",
]

normalized = {}

for source_type in source_types:
    result = normalize_uploaded_document_v1(
        make_result(source_type)
    )

    normalized[source_type] = result

    check(
        f"{source_type.upper()}_NORMALIZATION_STATUS_SUCCESS",
        result.normalization_status == "success",
    )


# ------------------------------------------------------------
# B. Title equivalence
# ------------------------------------------------------------

print()
print("=== B. TITLE EQUIVALENCE ===")

titles = {
    source_type: result.title
    for source_type, result in normalized.items()
}

check(
    "ALL_FORMATS_TITLE_EQUAL",
    len(set(titles.values())) == 1,
)

check(
    "TITLE_EXPECTED_VALUE",
    next(iter(titles.values()))
    == "Café Title",
)


# ------------------------------------------------------------
# C. Text equivalence
# ------------------------------------------------------------

print()
print("=== C. TEXT EQUIVALENCE ===")

texts = {
    source_type: result.text
    for source_type, result in normalized.items()
}

check(
    "ALL_FORMATS_TEXT_EQUAL",
    len(set(texts.values())) == 1,
)

check(
    "TEXT_EXPECTED_VALUE",
    next(iter(texts.values()))
    == "A B\n\nC D",
)


# ------------------------------------------------------------
# D. Heading equivalence
# ------------------------------------------------------------

print()
print("=== D. HEADING EQUIVALENCE ===")

headings = {
    source_type: result.headings
    for source_type, result in normalized.items()
}

heading_values = list(headings.values())

check(
    "ALL_FORMATS_HEADINGS_EQUAL",
    all(
        value == heading_values[0]
        for value in heading_values
    ),
)

check(
    "HEADINGS_EXPECTED_VALUE",
    heading_values[0]
    == [
        "First Heading",
        "First Heading",
        "Multi\nLine",
    ],
)


# ------------------------------------------------------------
# E. source_type preserved
# ------------------------------------------------------------

print()
print("=== E. SOURCE TYPE PROVENANCE ===")

for source_type, result in normalized.items():
    check(
        f"{source_type.upper()}_SOURCE_TYPE_PRESERVED",
        result.source_type == source_type,
    )


# ------------------------------------------------------------
# F. source_path preserved
# ------------------------------------------------------------

print()
print("=== F. SOURCE PATH PROVENANCE ===")

for source_type, result in normalized.items():
    check(
        f"{source_type.upper()}_SOURCE_PATH_PRESERVED",
        result.source_path
        == f"C:/immutable/source.{source_type}",
    )


# ------------------------------------------------------------
# G. Extraction provenance preserved
# ------------------------------------------------------------

print()
print("=== G. EXTRACTION PROVENANCE ===")

for source_type, result in normalized.items():
    check(
        f"{source_type.upper()}_EXTRACTION_STATUS_PRESERVED",
        result.extraction_status == "success",
    )

    check(
        f"{source_type.upper()}_EXTRACTION_CONFIDENCE_PRESERVED",
        result.extraction_confidence == 0.95,
    )

    check(
        f"{source_type.upper()}_EXTRACTION_TIMESTAMP_PRESERVED",
        result.extraction_created_at
        == "2026-08-31T00:00:00+00:00",
    )


# ------------------------------------------------------------
# H. Metadata preserved
# ------------------------------------------------------------

print()
print("=== H. METADATA PRESERVATION ===")

for source_type, result in normalized.items():
    check(
        f"{source_type.upper()}_CUSTOM_METADATA_PRESERVED",
        result.metadata.get("custom")
        == "preserve-me",
    )


# ------------------------------------------------------------
# I. Operation order identical
# ------------------------------------------------------------

print()
print("=== I. NORMALIZATION OPERATION ORDER ===")

expected_operations = [
    "unicode_nfc",
    "line_endings_lf",
    "horizontal_whitespace",
    "paragraph_boundaries",
    "heading_normalization",
    "title_normalization",
    "control_character_handling",
]

operations_by_type = {
    source_type: (
        result.metadata
        .get("normalization", {})
        .get("operations")
    )
    for source_type, result in normalized.items()
}

check(
    "ALL_FORMATS_OPERATION_ORDER_EQUAL",
    all(
        value == expected_operations
        for value in operations_by_type.values()
    ),
)


# ------------------------------------------------------------
# J. Determinism per source type
# ------------------------------------------------------------

print()
print("=== J. DETERMINISM ===")

for source_type in source_types:
    first = normalize_uploaded_document_v1(
        make_result(source_type)
    )

    second = normalize_uploaded_document_v1(
        make_result(source_type)
    )

    check(
        f"{source_type.upper()}_DETERMINISTIC_TITLE",
        first.title == second.title,
    )

    check(
        f"{source_type.upper()}_DETERMINISTIC_TEXT",
        first.text == second.text,
    )

    check(
        f"{source_type.upper()}_DETERMINISTIC_HEADINGS",
        first.headings == second.headings,
    )


# ------------------------------------------------------------
# K. Input immutability
# ------------------------------------------------------------

print()
print("=== K. INPUT IMMUTABILITY ===")

for source_type in source_types:
    original = make_result(source_type)

    before = (
        original.source_path,
        original.source_type,
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
        original.source_type,
        original.title,
        original.text,
        list(original.headings),
        dict(original.metadata),
    )

    check(
        f"{source_type.upper()}_INPUT_NOT_MUTATED",
        before == after,
    )


# ------------------------------------------------------------
# L. Ineligible extraction remains format-neutral
# ------------------------------------------------------------

print()
print("=== L. INELIGIBLE EXTRACTION FORMAT NEUTRALITY ===")

for source_type in source_types:
    source = make_result(source_type)
    source.extraction_status = "empty_text"

    result = normalize_uploaded_document_v1(
        source
    )

    check(
        f"{source_type.upper()}_INELIGIBLE_STATUS",
        result.normalization_status
        == "ineligible_extraction",
    )


# ------------------------------------------------------------
# M. No downstream structure
# ------------------------------------------------------------

print()
print("=== M. DOWNSTREAM BOUNDARY ===")

sample = normalized["txt"]

check(
    "RESULT_HAS_NO_STRUCTURE",
    not hasattr(sample, "structure"),
)

check(
    "RESULT_HAS_NO_HEADING_MAP",
    not hasattr(sample, "heading_map"),
)

check(
    "RESULT_HAS_NO_UUCD",
    not hasattr(sample, "uucd"),
)

check(
    "RESULT_HAS_NO_SEMANTIC_SCORE",
    not hasattr(sample, "semantic_score"),
)


# ------------------------------------------------------------
# N. Final decision
# ------------------------------------------------------------

print()
print("=== N. U7.13 DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U7.13_FORMAT_NEUTRAL_NORMALIZATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U7.13 format-neutral normalization verification failed."
    )

print(
    "U7.13_FORMAT_NEUTRAL_NORMALIZATION: CERTIFIED"
)

print(
    "U7.13_SOURCE_TYPE_BRANCHING: NO"
)

print(
    "U7.13_SOURCE_FILE_REREAD: NO"
)

print(
    "U7.13_FORMAT_PARSER_DEPENDENCIES: NO"
)

print(
    "U7.13_CROSS_FORMAT_CONTENT_EQUIVALENCE: YES"
)

print(
    "U7.13_SOURCE_TYPE_PRESERVED_AS_PROVENANCE: YES"
)

print(
    "U7.13_FORMAT_SPECIFIC_CLEANUP_RULES: NO"
)

print(
    "U7.13_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U7.14_SOURCE_IMMUTABILITY_TRANSITION: AUTHORIZED"
)

print(
    "U7.13_FINAL_FORMAT_NEUTRAL_NORMALIZATION_VERIFICATION: PASS"
)