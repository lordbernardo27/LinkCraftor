from __future__ import annotations

from copy import deepcopy

from backend.server.stores.upload_document_extractor import (
    UploadExtractionResult,
)

import backend.server.stores.upload_document_normalizer as normalizer


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def make_result(
    *,
    source_type: str = "txt",
    extraction_status: str = "success",
) -> UploadExtractionResult:
    return UploadExtractionResult(
        source_path=f"C:/immutable/source.{source_type}",
        source_type=source_type,
        title="  Cafe\u0301\t Title \u0000 ",
        text=(
            "\n\n"
            " A   B \r\n\r\n\r\n"
            " C\tD \u0000 \n"
            " E\u200DF\u200CG\u00A0H "
            "\n\n"
        ),
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
        extraction_status=extraction_status,
        extraction_confidence=0.95,
        created_at="2026-08-31T00:00:00+00:00",
    )


print("=== U7.16 - DETERMINISM VERIFICATION ===")


# ------------------------------------------------------------
# A. Repeated eligible normalization
# ------------------------------------------------------------

print()
print("=== A. REPEATED ELIGIBLE NORMALIZATION ===")

source = make_result()
before = deepcopy(source)

runs = [
    normalizer.normalize_uploaded_document_v1(
        source
    )
    for _ in range(10)
]

first = runs[0]

check(
    "TEN_RUNS_TITLE_IDENTICAL",
    all(
        value.title == first.title
        for value in runs
    ),
)

check(
    "TEN_RUNS_TEXT_IDENTICAL",
    all(
        value.text == first.text
        for value in runs
    ),
)

check(
    "TEN_RUNS_HEADINGS_IDENTICAL",
    all(
        value.headings == first.headings
        for value in runs
    ),
)

check(
    "TEN_RUNS_STATUS_IDENTICAL",
    all(
        value.normalization_status
        == first.normalization_status
        for value in runs
    ),
)

check(
    "TEN_RUNS_OPERATIONS_IDENTICAL",
    all(
        value.metadata
        .get("normalization", {})
        .get("operations")
        ==
        first.metadata
        .get("normalization", {})
        .get("operations")
        for value in runs
    ),
)

check(
    "REPEATED_RUN_INPUT_NOT_MUTATED",
    source == before,
)


# ------------------------------------------------------------
# B. Expected deterministic content
# ------------------------------------------------------------

print()
print("=== B. EXPECTED CONTENT ===")

check(
    "EXPECTED_TITLE",
    first.title == "Café Title",
)

check(
    "EXPECTED_TEXT",
    first.text
    == "A B\n\nC D\nE\u200DF\u200CG\u00A0H",
)

check(
    "EXPECTED_HEADINGS",
    first.headings
    == [
        "First Heading",
        "First Heading",
        "Multi\nLine",
    ],
)


# ------------------------------------------------------------
# C. normalized_at separated from content determinism
# ------------------------------------------------------------

print()
print("=== C. PROVENANCE TIMESTAMP SEPARATION ===")

check(
    "NORMALIZED_AT_PRESENT_ALL_RUNS",
    all(
        isinstance(
            value.normalized_at,
            str,
        )
        and bool(value.normalized_at)
        for value in runs
    ),
)

check(
    "NORMALIZED_AT_NOT_USED_AS_CONTENT",
    all(
        value.normalized_at
        not in (
            value.title,
            value.text,
        )
        and value.normalized_at
        not in value.headings
        for value in runs
    ),
)

check(
    "EXTRACTION_TIMESTAMP_IDENTICAL_ALL_RUNS",
    all(
        value.extraction_created_at
        == "2026-08-31T00:00:00+00:00"
        for value in runs
    ),
)


# ------------------------------------------------------------
# D. Cross-format determinism
# ------------------------------------------------------------

print()
print("=== D. CROSS-FORMAT DETERMINISM ===")

source_types = [
    "txt",
    "markdown",
    "html",
    "docx",
]

cross_format = {
    source_type:
    normalizer.normalize_uploaded_document_v1(
        make_result(
            source_type=source_type,
        )
    )
    for source_type in source_types
}

reference = cross_format["txt"]

check(
    "CROSS_FORMAT_TITLE_IDENTICAL",
    all(
        value.title == reference.title
        for value in cross_format.values()
    ),
)

check(
    "CROSS_FORMAT_TEXT_IDENTICAL",
    all(
        value.text == reference.text
        for value in cross_format.values()
    ),
)

check(
    "CROSS_FORMAT_HEADINGS_IDENTICAL",
    all(
        value.headings == reference.headings
        for value in cross_format.values()
    ),
)

check(
    "CROSS_FORMAT_STATUS_IDENTICAL",
    all(
        value.normalization_status
        == "success"
        for value in cross_format.values()
    ),
)

check(
    "SOURCE_TYPE_PRESERVED_PER_FORMAT",
    all(
        cross_format[source_type].source_type
        == source_type
        for source_type in source_types
    ),
)


# ------------------------------------------------------------
# E. Heading ordering / duplicates
# ------------------------------------------------------------

print()
print("=== E. ORDERING DETERMINISM ===")

check(
    "HEADING_ORDER_PRESERVED",
    first.headings
    == [
        "First Heading",
        "First Heading",
        "Multi\nLine",
    ],
)

check(
    "DUPLICATE_HEADING_ORDER_PRESERVED",
    first.headings[0]
    == first.headings[1]
    == "First Heading",
)

expected_operations = [
    "unicode_nfc",
    "line_endings_lf",
    "horizontal_whitespace",
    "paragraph_boundaries",
    "heading_normalization",
    "title_normalization",
    "control_character_handling",
]

check(
    "OPERATION_ORDER_FIXED",
    first.metadata
    .get("normalization", {})
    .get("operations")
    == expected_operations,
)


# ------------------------------------------------------------
# F. Unicode / whitespace / controls deterministic
# ------------------------------------------------------------

print()
print("=== F. NORMALIZATION RULE DETERMINISM ===")

check(
    "UNICODE_NFC_DETERMINISTIC",
    first.title.startswith("Café"),
)

check(
    "LINE_ENDING_DETERMINISTIC",
    "\r" not in first.text
    and "\r" not in first.title
    and all(
        "\r" not in heading
        for heading in first.headings
    ),
)

check(
    "CONTROL_REMOVAL_DETERMINISTIC",
    "\u0000" not in first.title
    and "\u0000" not in first.text,
)

check(
    "ZWJ_PRESERVED_DETERMINISTICALLY",
    "\u200D" in first.text,
)

check(
    "ZWNJ_PRESERVED_DETERMINISTICALLY",
    "\u200C" in first.text,
)

check(
    "NBSP_PRESERVED_DETERMINISTICALLY",
    "\u00A0" in first.text,
)


# ------------------------------------------------------------
# G. Ineligible determinism
# ------------------------------------------------------------

print()
print("=== G. INELIGIBLE DETERMINISM ===")

ineligible_source = make_result(
    extraction_status="empty_text",
)

ineligible_before = deepcopy(
    ineligible_source
)

ineligible_runs = [
    normalizer.normalize_uploaded_document_v1(
        ineligible_source
    )
    for _ in range(5)
]

ineligible_first = ineligible_runs[0]

check(
    "INELIGIBLE_STATUS_IDENTICAL",
    all(
        value.normalization_status
        == "ineligible_extraction"
        for value in ineligible_runs
    ),
)

check(
    "INELIGIBLE_TITLE_IDENTICAL",
    all(
        value.title
        == ineligible_first.title
        for value in ineligible_runs
    ),
)

check(
    "INELIGIBLE_TEXT_IDENTICAL",
    all(
        value.text
        == ineligible_first.text
        for value in ineligible_runs
    ),
)

check(
    "INELIGIBLE_HEADINGS_IDENTICAL",
    all(
        value.headings
        == ineligible_first.headings
        for value in ineligible_runs
    ),
)

check(
    "INELIGIBLE_OPERATIONS_EMPTY",
    all(
        value.metadata
        .get("normalization", {})
        .get("operations")
        == []
        for value in ineligible_runs
    ),
)

check(
    "INELIGIBLE_INPUT_NOT_MUTATED",
    ineligible_source
    == ineligible_before,
)


# ------------------------------------------------------------
# H. Normalization-error determinism
# ------------------------------------------------------------

print()
print("=== H. ERROR RESULT DETERMINISM ===")

error_source = make_result()
error_before = deepcopy(
    error_source
)

original_helper = (
    normalizer._normalize_title
)


def forced_failure(
    _: str,
) -> str:
    raise RuntimeError(
        "SECRET NONDETERMINISTIC MESSAGE"
    )


normalizer._normalize_title = (
    forced_failure
)

try:
    error_runs = [
        normalizer.normalize_uploaded_document_v1(
            error_source
        )
        for _ in range(5)
    ]
finally:
    normalizer._normalize_title = (
        original_helper
    )

error_first = error_runs[0]

check(
    "ERROR_STATUS_IDENTICAL",
    all(
        value.normalization_status
        == "normalization_error"
        for value in error_runs
    ),
)

check(
    "ERROR_TYPE_IDENTICAL",
    all(
        value.metadata
        .get("normalization", {})
        .get("error_type")
        == "RuntimeError"
        for value in error_runs
    ),
)

check(
    "ERROR_OPERATIONS_EMPTY",
    all(
        value.metadata
        .get("normalization", {})
        .get("operations")
        == []
        for value in error_runs
    ),
)

check(
    "ERROR_FALLBACK_TITLE_IDENTICAL",
    all(
        value.title
        == error_first.title
        for value in error_runs
    ),
)

check(
    "ERROR_FALLBACK_TEXT_IDENTICAL",
    all(
        value.text
        == error_first.text
        for value in error_runs
    ),
)

check(
    "ERROR_FALLBACK_HEADINGS_IDENTICAL",
    all(
        value.headings
        == error_first.headings
        for value in error_runs
    ),
)

check(
    "ERROR_MESSAGE_NOT_EXPOSED",
    all(
        "SECRET"
        not in repr(value.metadata)
        for value in error_runs
    ),
)

check(
    "ERROR_INPUT_NOT_MUTATED",
    error_source == error_before,
)


# ------------------------------------------------------------
# I. Source identity / provenance
# ------------------------------------------------------------

print()
print("=== I. SOURCE / PROVENANCE DETERMINISM ===")

check(
    "SOURCE_PATH_IDENTICAL_ALL_RUNS",
    all(
        value.source_path
        == "C:/immutable/source.txt"
        for value in runs
    ),
)

check(
    "SOURCE_TYPE_IDENTICAL_ALL_RUNS",
    all(
        value.source_type == "txt"
        for value in runs
    ),
)

check(
    "EXTRACTION_CONFIDENCE_IDENTICAL_ALL_RUNS",
    all(
        value.extraction_confidence
        == 0.95
        for value in runs
    ),
)


# ------------------------------------------------------------
# J. Downstream boundary
# ------------------------------------------------------------

print()
print("=== J. DOWNSTREAM BOUNDARY ===")

check(
    "RESULT_HAS_NO_STRUCTURE",
    not hasattr(first, "structure"),
)

check(
    "RESULT_HAS_NO_HEADING_MAP",
    not hasattr(first, "heading_map"),
)

check(
    "RESULT_HAS_NO_UUCD",
    not hasattr(first, "uucd"),
)

check(
    "RESULT_HAS_NO_SEMANTIC_SCORE",
    not hasattr(first, "semantic_score"),
)


# ------------------------------------------------------------
# K. Final decision
# ------------------------------------------------------------

print()
print("=== K. U7.16 DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U7.16_DETERMINISM: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U7.16 determinism verification failed."
    )

print(
    "U7.16_DETERMINISM: CERTIFIED"
)

print(
    "U7.16_CONTENT_DETERMINISM: YES"
)

print(
    "U7.16_NORMALIZED_AT_CONTENT_DEPENDENCY: NO"
)

print(
    "U7.16_RANDOMNESS_DEPENDENCY: NO"
)

print(
    "U7.16_EXTERNAL_STATE_DEPENDENCY: NO"
)

print(
    "U7.16_CROSS_FORMAT_DETERMINISM: YES"
)

print(
    "U7.16_INELIGIBLE_DETERMINISM: YES"
)

print(
    "U7.16_ERROR_RESULT_DETERMINISM: YES"
)

print(
    "U7.16_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U7.17_UDUC_RESPONSIBILITY_BOUNDARY_TRANSITION: AUTHORIZED"
)

print(
    "U7.16_FINAL_DETERMINISM_VERIFICATION: PASS"
)