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
    title: str = "",
    text: str = "",
    headings: list[str] | None = None,
    extraction_status: str = "success",
) -> UploadExtractionResult:
    return UploadExtractionResult(
        source_path=f"C:/immutable/source.{source_type}",
        source_type=source_type,
        title=title,
        text=text,
        headings=list(
            headings
            if headings is not None
            else []
        ),
        metadata={
            "filename": f"source.{source_type}",
            "custom": {
                "preserve": True,
            },
        },
        extraction_status=extraction_status,
        extraction_confidence=0.93,
        created_at="2026-08-31T00:00:00+00:00",
    )


print(
    "=== U7.21 BEHAVIORAL NORMALIZATION VERIFICATION ==="
)


# ------------------------------------------------------------
# A. Complete success-path normalization
# ------------------------------------------------------------

print()
print("=== A. COMPLETE SUCCESS PATH ===")

source = make_result(
    title=(
        "  Cafe\u0301\tTitle "
        "\u0000"
    ),
    text=(
        "\n\n\n"
        "  Alpha   Beta  \r\n"
        "Gamma\tDelta\r"
        "\r\n\r\n\r\n"
        "Para\u0000graph Two"
        "\n\n"
        "NBSP\u00A0Here "
        "ZWJ\u200DHere "
        "ZWNJ\u200CHere"
        "\n\n\n\n"
    ),
    headings=[
        "  Cafe\u0301\tHeading  ",
        "",
        "Duplicate",
        "Duplicate",
        "Multi\r\nLine",
        "\u0000Control",
    ],
)

before = deepcopy(source)

result = (
    normalizer.normalize_uploaded_document_v1(
        source
    )
)

check(
    "SUCCESS_STATUS",
    result.normalization_status
    == "success",
)

check(
    "SUCCESS_UNICODE_NFC_TITLE",
    result.title
    == "Café Title",
)

check(
    "SUCCESS_CRLF_CR_TO_LF",
    "\r" not in result.text
    and all(
        "\r" not in heading
        for heading in result.headings
    ),
)

check(
    "SUCCESS_HORIZONTAL_WHITESPACE",
    result.text.startswith(
        "Alpha Beta\nGamma Delta"
    ),
)

check(
    "SUCCESS_CONTROL_REMOVAL",
    "\u0000" not in result.title
    and "\u0000" not in result.text
    and all(
        "\u0000" not in heading
        for heading in result.headings
    ),
)

check(
    "SUCCESS_NBSP_PRESERVED",
    "\u00A0" in result.text,
)

check(
    "SUCCESS_ZWJ_PRESERVED",
    "\u200D" in result.text,
)

check(
    "SUCCESS_ZWNJ_PRESERVED",
    "\u200C" in result.text,
)


# ------------------------------------------------------------
# B. Paragraph semantics
# ------------------------------------------------------------

print()
print("=== B. PARAGRAPH SEMANTICS ===")

check(
    "LEADING_BLANK_LINES_REMOVED",
    not result.text.startswith("\n"),
)

check(
    "TRAILING_BLANK_LINES_REMOVED",
    not result.text.endswith("\n"),
)

check(
    "THREE_PLUS_LF_COLLAPSED_TO_TWO",
    "\n\n\n" not in result.text,
)

check(
    "DOUBLE_LF_PRESERVED",
    "\n\n" in result.text,
)

check(
    "SINGLE_LF_PRESERVED",
    "Alpha Beta\nGamma Delta"
    in result.text,
)

check(
    "NO_GLOBAL_WHITESPACE_COLLAPSE",
    "\n" in result.text
    and "\n\n" in result.text,
)


# ------------------------------------------------------------
# C. Heading behavior
# ------------------------------------------------------------

print()
print("=== C. HEADING BEHAVIOR ===")

check(
    "EMPTY_HEADINGS_REMOVED",
    "" not in result.headings,
)

check(
    "HEADING_ORDER_PRESERVED",
    result.headings[:4]
    == [
        "Café Heading",
        "Duplicate",
        "Duplicate",
        "Multi\nLine",
    ],
)

check(
    "HEADING_DUPLICATES_PRESERVED",
    result.headings.count(
        "Duplicate"
    )
    == 2,
)

check(
    "MULTILINE_HEADING_PRESERVED",
    "Multi\nLine"
    in result.headings,
)

check(
    "CONTROL_HEADING_NORMALIZED",
    "Control"
    in result.headings,
)

check(
    "NO_HEADING_HIERARCHY_FIELDS",
    not hasattr(
        result,
        "heading_map",
    )
    and not hasattr(
        result,
        "heading_levels",
    ),
)


# ------------------------------------------------------------
# D. Title behavior
# ------------------------------------------------------------

print()
print("=== D. TITLE BEHAVIOR ===")

empty_title_source = make_result(
    title="",
    text="Body content",
    headings=["Heading"],
)

empty_title_result = (
    normalizer.normalize_uploaded_document_v1(
        empty_title_source
    )
)

check(
    "EMPTY_TITLE_REMAINS_EMPTY",
    empty_title_result.title == "",
)

check(
    "NO_FILENAME_TITLE_FALLBACK",
    empty_title_result.title
    != "source.txt",
)

check(
    "NO_HEADING_TITLE_FALLBACK",
    empty_title_result.title
    != "Heading",
)

check(
    "NO_BODY_TITLE_FALLBACK",
    empty_title_result.title
    != "Body content",
)

multiline_title_source = make_result(
    title="First\r\nSecond",
    text="Body",
)

multiline_title_result = (
    normalizer.normalize_uploaded_document_v1(
        multiline_title_source
    )
)

check(
    "MULTILINE_TITLE_PRESERVED",
    multiline_title_result.title
    == "First\nSecond",
)


# ------------------------------------------------------------
# E. Source / provenance preservation
# ------------------------------------------------------------

print()
print("=== E. SOURCE / PROVENANCE ===")

check(
    "SOURCE_PATH_PRESERVED",
    result.source_path
    == source.source_path,
)

check(
    "SOURCE_TYPE_PRESERVED",
    result.source_type
    == source.source_type,
)

check(
    "EXTRACTION_STATUS_PRESERVED",
    result.extraction_status
    == source.extraction_status,
)

check(
    "EXTRACTION_CONFIDENCE_PRESERVED",
    result.extraction_confidence
    == source.extraction_confidence,
)

check(
    "EXTRACTION_CREATED_AT_PRESERVED",
    result.extraction_created_at
    == source.created_at,
)

check(
    "ORIGINAL_METADATA_VALUE_PRESERVED",
    result.metadata.get(
        "custom"
    )
    == source.metadata.get(
        "custom"
    ),
)


# ------------------------------------------------------------
# F. Normalization metadata
# ------------------------------------------------------------

print()
print("=== F. NORMALIZATION METADATA ===")

norm_meta = result.metadata.get(
    "normalization",
    {},
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
    "NORMALIZATION_VERSION",
    result.normalization_version
    == "uploaded_document_normalization_v1",
)

check(
    "NORMALIZATION_METADATA_VERSION",
    norm_meta.get("version")
    == "uploaded_document_normalization_v1",
)

check(
    "NORMALIZATION_METADATA_STATUS",
    norm_meta.get("status")
    == "success",
)

check(
    "NORMALIZATION_METADATA_UNICODE_FORM",
    norm_meta.get("unicode_form")
    == "NFC",
)

check(
    "NORMALIZATION_OPERATION_ORDER",
    norm_meta.get("operations")
    == expected_operations,
)

check(
    "NORMALIZED_AT_PRESENT",
    isinstance(
        result.normalized_at,
        str,
    )
    and bool(
        result.normalized_at
    ),
)


# ------------------------------------------------------------
# G. Immutability / isolation
# ------------------------------------------------------------

print()
print("=== G. IMMUTABILITY / OUTPUT ISOLATION ===")

check(
    "SOURCE_OBJECT_UNCHANGED",
    source == before,
)

check(
    "DEDICATED_OUTPUT_TYPE",
    isinstance(
        result,
        normalizer.NormalizedUploadedDocumentContent,
    ),
)

check(
    "OUTPUT_IS_NEW_OBJECT",
    result is not source,
)

check(
    "HEADINGS_LIST_ISOLATED",
    result.headings
    is not source.headings,
)

check(
    "METADATA_DICT_ISOLATED",
    result.metadata
    is not source.metadata,
)


# ------------------------------------------------------------
# H. Ineligible extraction behavior
# ------------------------------------------------------------

print()
print("=== H. INELIGIBLE EXTRACTION ===")

ineligible = make_result(
    title=" Title ",
    text=" Text \r\n",
    headings=[" Heading "],
    extraction_status="empty_text",
)

ineligible_before = deepcopy(
    ineligible
)

ineligible_result = (
    normalizer.normalize_uploaded_document_v1(
        ineligible
    )
)

check(
    "INELIGIBLE_STATUS",
    ineligible_result.normalization_status
    == "ineligible_extraction",
)

check(
    "INELIGIBLE_TITLE_UNCHANGED",
    ineligible_result.title
    == ineligible.title,
)

check(
    "INELIGIBLE_TEXT_UNCHANGED",
    ineligible_result.text
    == ineligible.text,
)

check(
    "INELIGIBLE_HEADINGS_UNCHANGED",
    ineligible_result.headings
    == ineligible.headings,
)

check(
    "INELIGIBLE_OPERATIONS_EMPTY",
    ineligible_result.metadata
    .get("normalization", {})
    .get("operations")
    == [],
)

check(
    "INELIGIBLE_INPUT_UNCHANGED",
    ineligible == ineligible_before,
)


# ------------------------------------------------------------
# I. Programmer-contract violations
# ------------------------------------------------------------

print()
print("=== I. PROGRAMMER-CONTRACT VIOLATIONS ===")


class MissingFields:
    pass


raised = None

try:
    normalizer.normalize_uploaded_document_v1(
        MissingFields()
    )
except Exception as exc:
    raised = exc

check(
    "MISSING_REQUIRED_FIELDS_RAISE",
    isinstance(
        raised,
        TypeError,
    ),
)


bad_title = make_result(
    title="Title",
    text="Body",
)
bad_title.title = 123

raised = None

try:
    normalizer.normalize_uploaded_document_v1(
        bad_title
    )
except Exception as exc:
    raised = exc

check(
    "MALFORMED_TITLE_RAISES",
    isinstance(
        raised,
        TypeError,
    ),
)


bad_text = make_result(
    title="Title",
    text="Body",
)
bad_text.text = 123

raised = None

try:
    normalizer.normalize_uploaded_document_v1(
        bad_text
    )
except Exception as exc:
    raised = exc

check(
    "MALFORMED_TEXT_RAISES",
    isinstance(
        raised,
        TypeError,
    ),
)


bad_headings = make_result(
    title="Title",
    text="Body",
)
bad_headings.headings = "not-a-list"

raised = None

try:
    normalizer.normalize_uploaded_document_v1(
        bad_headings
    )
except Exception as exc:
    raised = exc

check(
    "MALFORMED_HEADINGS_RAISES",
    isinstance(
        raised,
        TypeError,
    ),
)


# ------------------------------------------------------------
# J. Unexpected normalization failure
# ------------------------------------------------------------

print()
print("=== J. UNEXPECTED NORMALIZATION FAILURE ===")

failure_source = make_result(
    title="Title",
    text="Body",
    headings=["Heading"],
)

failure_before = deepcopy(
    failure_source
)

original_helper = (
    normalizer._normalize_title
)


def forced_failure(
    _: str,
) -> str:
    raise RuntimeError(
        "SECRET C:/internal/private.txt"
    )


normalizer._normalize_title = (
    forced_failure
)

try:
    failure_result = (
        normalizer.normalize_uploaded_document_v1(
            failure_source
        )
    )
finally:
    normalizer._normalize_title = (
        original_helper
    )

check(
    "FAILURE_RETURNS_NORMALIZATION_ERROR",
    failure_result.normalization_status
    == "normalization_error",
)

failure_meta = (
    failure_result.metadata.get(
        "normalization",
        {},
    )
)

check(
    "FAILURE_SAFE_ERROR_TYPE_ONLY",
    failure_meta.get(
        "error_type"
    )
    == "RuntimeError",
)

failure_metadata_repr = repr(
    failure_result.metadata
)

check(
    "FAILURE_NO_MESSAGE_LEAK",
    "SECRET"
    not in failure_metadata_repr,
)

check(
    "FAILURE_NO_PATH_LEAK",
    "C:/internal/private.txt"
    not in failure_metadata_repr,
)

check(
    "FAILURE_SOURCE_UNCHANGED",
    failure_source
    == failure_before,
)


# ------------------------------------------------------------
# K. Format-neutral behavior
# ------------------------------------------------------------

print()
print("=== K. FORMAT-NEUTRAL BEHAVIOR ===")

format_results = {}

for source_type in [
    "txt",
    "markdown",
    "html",
    "docx",
]:
    value = make_result(
        source_type=source_type,
        title=" Cafe\u0301 ",
        text=(
            " A   B\r\n\r\n\r\n"
            "C\tD\u0000 "
        ),
        headings=[
            " Heading ",
        ],
    )

    format_results[source_type] = (
        normalizer.normalize_uploaded_document_v1(
            value
        )
    )

reference = format_results["txt"]

check(
    "FORMAT_NEUTRAL_TITLE",
    all(
        item.title
        == reference.title
        for item in format_results.values()
    ),
)

check(
    "FORMAT_NEUTRAL_TEXT",
    all(
        item.text
        == reference.text
        for item in format_results.values()
    ),
)

check(
    "FORMAT_NEUTRAL_HEADINGS",
    all(
        item.headings
        == reference.headings
        for item in format_results.values()
    ),
)

check(
    "FORMAT_PROVENANCE_SOURCE_TYPE_PRESERVED",
    all(
        format_results[source_type].source_type
        == source_type
        for source_type in format_results
    ),
)


# ------------------------------------------------------------
# L. Determinism
# ------------------------------------------------------------

print()
print("=== L. DETERMINISM ===")

det_source = make_result(
    title=" Cafe\u0301 ",
    text=" A   B\r\n\r\nC ",
    headings=[" H "],
)

det_runs = [
    normalizer.normalize_uploaded_document_v1(
        det_source
    )
    for _ in range(10)
]

det_first = det_runs[0]

check(
    "DETERMINISTIC_TITLE",
    all(
        item.title
        == det_first.title
        for item in det_runs
    ),
)

check(
    "DETERMINISTIC_TEXT",
    all(
        item.text
        == det_first.text
        for item in det_runs
    ),
)

check(
    "DETERMINISTIC_HEADINGS",
    all(
        item.headings
        == det_first.headings
        for item in det_runs
    ),
)

check(
    "DETERMINISTIC_STATUS",
    all(
        item.normalization_status
        == det_first.normalization_status
        for item in det_runs
    ),
)

check(
    "DETERMINISTIC_OPERATIONS",
    all(
        item.metadata
        .get("normalization", {})
        .get("operations")
        ==
        det_first.metadata
        .get("normalization", {})
        .get("operations")
        for item in det_runs
    ),
)


# ------------------------------------------------------------
# M. Downstream boundary
# ------------------------------------------------------------

print()
print("=== M. DOWNSTREAM BOUNDARY ===")

forbidden_attributes = [
    "structure",
    "paragraphs",
    "heading_map",
    "document_order",
    "highlights",
    "highlight_spans",
    "active_target_set",
    "target_score",
    "uucd",
    "content_ref",
    "body_ref",
    "semantic_score",
]

for attribute in forbidden_attributes:
    check(
        f"NO_DOWNSTREAM_ATTRIBUTE_{attribute.upper()}",
        not hasattr(
            result,
            attribute,
        ),
    )


# ------------------------------------------------------------
# N. Static dependency boundary
# ------------------------------------------------------------

print()
print("=== N. STATIC DEPENDENCY BOUNDARY ===")

from pathlib import Path

normalizer_path = Path(
    "backend/server/stores/upload_document_normalizer.py"
)

normalizer_source = (
    normalizer_path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )
)

normalizer_lower = (
    normalizer_source.lower()
)

check(
    "NO_SOURCE_REREAD_CALL",
    "read_text(" not in normalizer_lower
    and "read_bytes(" not in normalizer_lower
    and "open(" not in normalizer_lower,
)

check(
    "NO_WEBSITE_CLEANER_REFERENCE",
    "article_body_cleaning_engine"
    not in normalizer_lower
    and "article_cleaning_pipeline"
    not in normalizer_lower,
)

check(
    "NO_GENERIC_NORMALIZER_REFERENCE",
    "fix_mojibake_text"
    not in normalizer_lower
    and "utils.text_normalization"
    not in normalizer_lower,
)

check(
    "NO_HIGHLIGHT_EXECUTION_REFERENCE",
    "highlight" not in normalizer_lower
    or "does not" in normalizer_lower,
)

check(
    "NO_ACTIVE_TARGET_EXECUTION_REFERENCE",
    "active_target" not in normalizer_lower,
)

check(
    "NO_CURRENT_CANONICAL_UUCD_CALL",
    "build_uucd" not in normalizer_lower
    and "write_uucd" not in normalizer_lower
    and "content_ref" not in normalizer_lower
    and "body_ref" not in normalizer_lower,
)


# ------------------------------------------------------------
# O. Final decision
# ------------------------------------------------------------

print()
print("=== O. U7.21 FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U7.21_BEHAVIORAL_NORMALIZATION_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U7.21 behavioral normalization verification failed."
    )

print(
    "U7.21_BEHAVIORAL_NORMALIZATION_VERIFICATION: CERTIFIED"
)

print(
    "U7.21_SUCCESS_PATH: PASS"
)

print(
    "U7.21_PARAGRAPH_SEMANTICS: PASS"
)

print(
    "U7.21_HEADING_BEHAVIOR: PASS"
)

print(
    "U7.21_TITLE_BEHAVIOR: PASS"
)

print(
    "U7.21_SOURCE_PROVENANCE: PASS"
)

print(
    "U7.21_NORMALIZATION_METADATA: PASS"
)

print(
    "U7.21_SOURCE_IMMUTABILITY: PASS"
)

print(
    "U7.21_INELIGIBLE_BEHAVIOR: PASS"
)

print(
    "U7.21_PROGRAMMER_CONTRACT: PASS"
)

print(
    "U7.21_NORMALIZATION_ERROR_CONTRACT: PASS"
)

print(
    "U7.21_FORMAT_NEUTRALITY: PASS"
)

print(
    "U7.21_DETERMINISM: PASS"
)

print(
    "U7.21_DOWNSTREAM_BOUNDARY: PASS"
)

print(
    "U7.21_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U7.22_BUILD_INTEGRATION_VERIFICATION_TRANSITION: AUTHORIZED"
)

print(
    "U7.21_FINAL_BEHAVIORAL_NORMALIZATION_VERIFICATION: PASS"
)