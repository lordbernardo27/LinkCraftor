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
    extraction_status: str = "success",
) -> UploadExtractionResult:
    return UploadExtractionResult(
        source_path="C:/immutable/source.txt",
        source_type="txt",
        title=" Title ",
        text=" Body ",
        headings=[" Heading "],
        metadata={
            "filename": "source.txt",
            "custom": "preserve-me",
        },
        extraction_status=extraction_status,
        extraction_confidence=0.95,
        created_at="2026-08-31T00:00:00+00:00",
    )


print("=== U7.15 - FAILURE CONTRACT VERIFICATION ===")


# ------------------------------------------------------------
# A. Status vocabulary
# ------------------------------------------------------------

print()
print("=== A. STATUS VOCABULARY ===")

check(
    "STATUS_SUCCESS",
    normalizer.NORMALIZATION_STATUS_SUCCESS
    == "success",
)

check(
    "STATUS_INVALID_INPUT",
    normalizer.NORMALIZATION_STATUS_INVALID_INPUT
    == "invalid_input",
)

check(
    "STATUS_INELIGIBLE_EXTRACTION",
    normalizer.NORMALIZATION_STATUS_INELIGIBLE_EXTRACTION
    == "ineligible_extraction",
)

check(
    "STATUS_NORMALIZATION_ERROR",
    normalizer.NORMALIZATION_STATUS_ERROR
    == "normalization_error",
)


# ------------------------------------------------------------
# B. Missing / incompatible input
# ------------------------------------------------------------

print()
print("=== B. INCOMPATIBLE INPUT ===")

for name, value in [
    ("NONE_INPUT", None),
    ("PLAIN_OBJECT", object()),
]:

    raised = None

    try:
        normalizer.normalize_uploaded_document_v1(
            value
        )
    except Exception as exc:
        raised = exc

    check(
        f"{name}_RAISES_TYPE_ERROR",
        isinstance(raised, TypeError),
    )


# ------------------------------------------------------------
# C. Malformed title
# ------------------------------------------------------------

print()
print("=== C. MALFORMED TITLE ===")

value = make_result()
value.title = 123

before = deepcopy(value)

raised = None

try:
    normalizer.normalize_uploaded_document_v1(
        value
    )
except Exception as exc:
    raised = exc

check(
    "MALFORMED_TITLE_RAISES_TYPE_ERROR",
    isinstance(raised, TypeError),
)

check(
    "MALFORMED_TITLE_INPUT_NOT_MUTATED",
    value == before,
)


# ------------------------------------------------------------
# D. Malformed text
# ------------------------------------------------------------

print()
print("=== D. MALFORMED TEXT ===")

value = make_result()
value.text = 123

before = deepcopy(value)

raised = None

try:
    normalizer.normalize_uploaded_document_v1(
        value
    )
except Exception as exc:
    raised = exc

check(
    "MALFORMED_TEXT_RAISES_TYPE_ERROR",
    isinstance(raised, TypeError),
)

check(
    "MALFORMED_TEXT_INPUT_NOT_MUTATED",
    value == before,
)


# ------------------------------------------------------------
# E. Malformed headings container
# ------------------------------------------------------------

print()
print("=== E. MALFORMED HEADINGS CONTAINER ===")

value = make_result()
value.headings = "Heading"

before = deepcopy(value)

raised = None

try:
    normalizer.normalize_uploaded_document_v1(
        value
    )
except Exception as exc:
    raised = exc

check(
    "MALFORMED_HEADINGS_CONTAINER_RAISES_TYPE_ERROR",
    isinstance(raised, TypeError),
)

check(
    "MALFORMED_HEADINGS_CONTAINER_INPUT_NOT_MUTATED",
    value == before,
)


# ------------------------------------------------------------
# F. Malformed heading element
# ------------------------------------------------------------

print()
print("=== F. MALFORMED HEADING ELEMENT ===")

value = make_result()
value.headings = [
    "Valid",
    123,
]

before = deepcopy(value)

raised = None

try:
    normalizer.normalize_uploaded_document_v1(
        value
    )
except Exception as exc:
    raised = exc

check(
    "MALFORMED_HEADING_ELEMENT_RAISES_TYPE_ERROR",
    isinstance(raised, TypeError),
)

check(
    "MALFORMED_HEADING_ELEMENT_INPUT_NOT_MUTATED",
    value == before,
)


# ------------------------------------------------------------
# G. Malformed metadata handling
# ------------------------------------------------------------

print()
print("=== G. MALFORMED METADATA ===")

value = make_result()
value.metadata = "not-a-dict"

before = deepcopy(value)

result = normalizer.normalize_uploaded_document_v1(
    value
)

check(
    "MALFORMED_METADATA_DOES_NOT_CRASH",
    result.normalization_status
    == "success",
)

check(
    "MALFORMED_METADATA_REPLACED_WITH_SAFE_DICT",
    isinstance(result.metadata, dict),
)

check(
    "MALFORMED_METADATA_INPUT_NOT_MUTATED",
    value == before,
)


# ------------------------------------------------------------
# H. Ineligible extraction
# ------------------------------------------------------------

print()
print("=== H. INELIGIBLE EXTRACTION ===")

value = make_result(
    extraction_status="empty_text",
)

before = deepcopy(value)

result = normalizer.normalize_uploaded_document_v1(
    value
)

check(
    "INELIGIBLE_STATUS_RETURNED",
    result.normalization_status
    == "ineligible_extraction",
)

check(
    "INELIGIBLE_OPERATIONS_EMPTY",
    result.metadata
    .get("normalization", {})
    .get("operations")
    == [],
)

check(
    "INELIGIBLE_TITLE_UNCHANGED",
    result.title == value.title,
)

check(
    "INELIGIBLE_TEXT_UNCHANGED",
    result.text == value.text,
)

check(
    "INELIGIBLE_HEADINGS_UNCHANGED",
    result.headings == value.headings,
)

check(
    "INELIGIBLE_SOURCE_PATH_PRESERVED",
    result.source_path
    == value.source_path,
)

check(
    "INELIGIBLE_SOURCE_TYPE_PRESERVED",
    result.source_type
    == value.source_type,
)

check(
    "INELIGIBLE_EXTRACTION_CONFIDENCE_PRESERVED",
    result.extraction_confidence
    == value.extraction_confidence,
)

check(
    "INELIGIBLE_EXTRACTION_TIMESTAMP_PRESERVED",
    result.extraction_created_at
    == value.created_at,
)

check(
    "INELIGIBLE_INPUT_NOT_MUTATED",
    value == before,
)


# ------------------------------------------------------------
# I. Success behavior
# ------------------------------------------------------------

print()
print("=== I. SUCCESS PATH ===")

value = make_result()
before = deepcopy(value)

result = normalizer.normalize_uploaded_document_v1(
    value
)

check(
    "SUCCESS_STATUS_RETURNED",
    result.normalization_status
    == "success",
)

check(
    "SUCCESS_TITLE_NORMALIZED",
    result.title == "Title",
)

check(
    "SUCCESS_TEXT_NORMALIZED",
    result.text == "Body",
)

check(
    "SUCCESS_HEADINGS_NORMALIZED",
    result.headings == ["Heading"],
)

check(
    "SUCCESS_INPUT_NOT_MUTATED",
    value == before,
)


# ------------------------------------------------------------
# J. Unexpected internal error
# ------------------------------------------------------------

print()
print("=== J. UNEXPECTED INTERNAL ERROR ===")

value = make_result()
before = deepcopy(value)

original_helper = (
    normalizer._normalize_title
)


def forced_internal_failure(
    _: str,
) -> str:
    raise RuntimeError(
        "SECRET C:/private/internal/path.txt"
    )


normalizer._normalize_title = (
    forced_internal_failure
)

try:
    result = (
        normalizer.normalize_uploaded_document_v1(
            value
        )
    )
finally:
    normalizer._normalize_title = (
        original_helper
    )

check(
    "UNEXPECTED_ERROR_RETURNS_RESULT",
    isinstance(
        result,
        normalizer.NormalizedUploadedDocumentContent,
    ),
)

check(
    "UNEXPECTED_ERROR_STATUS",
    result.normalization_status
    == "normalization_error",
)

normalization_metadata = (
    result.metadata.get(
        "normalization",
        {},
    )
)

check(
    "UNEXPECTED_ERROR_OPERATIONS_EMPTY",
    normalization_metadata.get(
        "operations"
    )
    == [],
)

check(
    "UNEXPECTED_ERROR_TYPE_SAFE",
    normalization_metadata.get(
        "error_type"
    )
    == "RuntimeError",
)

metadata_repr = repr(
    result.metadata
)

check(
    "UNEXPECTED_ERROR_MESSAGE_NOT_EXPOSED",
    "SECRET"
    not in metadata_repr,
)

check(
    "UNEXPECTED_ERROR_PATH_NOT_EXPOSED",
    "C:/private/internal/path.txt"
    not in metadata_repr,
)

check(
    "UNEXPECTED_ERROR_INPUT_NOT_MUTATED",
    value == before,
)

check(
    "UNEXPECTED_ERROR_SOURCE_PATH_PRESERVED",
    result.source_path
    == value.source_path,
)

check(
    "UNEXPECTED_ERROR_SOURCE_TYPE_PRESERVED",
    result.source_type
    == value.source_type,
)

check(
    "UNEXPECTED_ERROR_EXTRACTION_STATUS_PRESERVED",
    result.extraction_status
    == value.extraction_status,
)

check(
    "UNEXPECTED_ERROR_EXTRACTION_CONFIDENCE_PRESERVED",
    result.extraction_confidence
    == value.extraction_confidence,
)

check(
    "UNEXPECTED_ERROR_EXTRACTION_TIMESTAMP_PRESERVED",
    result.extraction_created_at
    == value.created_at,
)


# ------------------------------------------------------------
# K. Version / timestamp on returned results
# ------------------------------------------------------------

print()
print("=== K. RETURNED RESULT CONTRACT ===")

success_result = (
    normalizer.normalize_uploaded_document_v1(
        make_result()
    )
)

ineligible_result = (
    normalizer.normalize_uploaded_document_v1(
        make_result(
            extraction_status="empty_text",
        )
    )
)

for name, value in [
    ("SUCCESS", success_result),
    ("INELIGIBLE", ineligible_result),
    ("ERROR", result),
]:

    check(
        f"{name}_NORMALIZATION_VERSION",
        value.normalization_version
        == "uploaded_document_normalization_v1",
    )

    check(
        f"{name}_NORMALIZED_AT_PRESENT",
        isinstance(
            value.normalized_at,
            str,
        )
        and bool(
            value.normalized_at
        ),
    )


# ------------------------------------------------------------
# L. Downstream boundary
# ------------------------------------------------------------

print()
print("=== L. DOWNSTREAM BOUNDARY ===")

check(
    "ERROR_RESULT_HAS_NO_STRUCTURE",
    not hasattr(result, "structure"),
)

check(
    "ERROR_RESULT_HAS_NO_HEADING_MAP",
    not hasattr(result, "heading_map"),
)

check(
    "ERROR_RESULT_HAS_NO_UUCD",
    not hasattr(result, "uucd"),
)

check(
    "ERROR_RESULT_HAS_NO_SEMANTIC_SCORE",
    not hasattr(result, "semantic_score"),
)


# ------------------------------------------------------------
# M. Final decision
# ------------------------------------------------------------

print()
print("=== M. U7.15 DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U7.15_FAILURE_CONTRACT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U7.15 failure-contract verification failed."
    )

print(
    "U7.15_FAILURE_CONTRACT: CERTIFIED"
)

print(
    "U7.15_PROGRAMMER_CONTRACT_VIOLATIONS: RAISE"
)

print(
    "U7.15_INELIGIBLE_EXTRACTION: RETURN_INELIGIBLE_RESULT"
)

print(
    "U7.15_UNEXPECTED_INTERNAL_ERROR: RETURN_NORMALIZATION_ERROR"
)

print(
    "U7.15_INTERNAL_ERROR_MESSAGE_EXPOSURE: NO"
)

print(
    "U7.15_SOURCE_MUTATION_ON_FAILURE: NO"
)

print(
    "U7.15_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U7.16_DETERMINISM_TRANSITION: AUTHORIZED"
)

print(
    "U7.15_FINAL_FAILURE_CONTRACT_VERIFICATION: PASS"
)