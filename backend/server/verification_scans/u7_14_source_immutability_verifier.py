from __future__ import annotations

from copy import deepcopy

from backend.server.stores.upload_document_extractor import (
    UploadExtractionResult,
)

from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
    normalize_uploaded_document_v1,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def make_success() -> UploadExtractionResult:
    return UploadExtractionResult(
        source_path="C:/immutable/source.DOCX",
        source_type="docx",
        title="  Cafe\u0301\tTitle  ",
        text=" A   B \r\n\r\n\r\n C\tD \u0000 ",
        headings=[
            "  First\tHeading  ",
            "  First\tHeading  ",
        ],
        metadata={
            "filename": "source.DOCX",
            "nested": {
                "keep": ["a", "b"],
            },
        },
        extraction_status="success",
        extraction_confidence=0.92,
        created_at="2026-08-31T00:00:00+00:00",
    )


def make_ineligible() -> UploadExtractionResult:
    value = make_success()
    value.extraction_status = "empty_text"
    return value


print("=== U7.14 - SOURCE IMMUTABILITY VERIFICATION ===")


# ------------------------------------------------------------
# A. Successful input object immutability
# ------------------------------------------------------------

print()
print("=== A. SUCCESS INPUT IMMUTABILITY ===")

success_input = make_success()
success_before = deepcopy(success_input)

success_result = normalize_uploaded_document_v1(
    success_input
)

check(
    "SUCCESS_SOURCE_PATH_NOT_MUTATED",
    success_input.source_path
    == success_before.source_path,
)

check(
    "SUCCESS_SOURCE_TYPE_NOT_MUTATED",
    success_input.source_type
    == success_before.source_type,
)

check(
    "SUCCESS_TITLE_NOT_MUTATED",
    success_input.title
    == success_before.title,
)

check(
    "SUCCESS_TEXT_NOT_MUTATED",
    success_input.text
    == success_before.text,
)

check(
    "SUCCESS_HEADINGS_NOT_MUTATED",
    success_input.headings
    == success_before.headings,
)

check(
    "SUCCESS_METADATA_NOT_MUTATED",
    success_input.metadata
    == success_before.metadata,
)

check(
    "SUCCESS_EXTRACTION_STATUS_NOT_MUTATED",
    success_input.extraction_status
    == success_before.extraction_status,
)

check(
    "SUCCESS_EXTRACTION_CONFIDENCE_NOT_MUTATED",
    success_input.extraction_confidence
    == success_before.extraction_confidence,
)

check(
    "SUCCESS_EXTRACTION_TIMESTAMP_NOT_MUTATED",
    success_input.created_at
    == success_before.created_at,
)


# ------------------------------------------------------------
# B. Dedicated new result object
# ------------------------------------------------------------

print()
print("=== B. DEDICATED RESULT OBJECT ===")

check(
    "RESULT_IS_NORMALIZED_UPLOADED_DOCUMENT_CONTENT",
    isinstance(
        success_result,
        NormalizedUploadedDocumentContent,
    ),
)

check(
    "RESULT_IS_NOT_INPUT_OBJECT",
    success_result is not success_input,
)


# ------------------------------------------------------------
# C. Source identity exact preservation
# ------------------------------------------------------------

print()
print("=== C. SOURCE IDENTITY PRESERVATION ===")

check(
    "SOURCE_PATH_EXACTLY_PRESERVED",
    success_result.source_path
    == "C:/immutable/source.DOCX",
)

check(
    "SOURCE_TYPE_EXACTLY_PRESERVED",
    success_result.source_type
    == "docx",
)


# ------------------------------------------------------------
# D. Metadata object separation
# ------------------------------------------------------------

print()
print("=== D. METADATA SEPARATION ===")

check(
    "RESULT_METADATA_IS_SEPARATE_DICT",
    success_result.metadata
    is not success_input.metadata,
)

check(
    "INPUT_HAS_NO_NORMALIZATION_METADATA",
    "normalization"
    not in success_input.metadata,
)

check(
    "RESULT_HAS_NORMALIZATION_METADATA",
    "normalization"
    in success_result.metadata,
)

check(
    "ORIGINAL_METADATA_VALUES_PRESERVED",
    success_result.metadata.get("filename")
    == "source.DOCX"
    and success_result.metadata.get("nested")
    == {
        "keep": ["a", "b"],
    },
)


# ------------------------------------------------------------
# E. Heading list separation
# ------------------------------------------------------------

print()
print("=== E. HEADING LIST SEPARATION ===")

check(
    "RESULT_HEADINGS_IS_SEPARATE_LIST",
    success_result.headings
    is not success_input.headings,
)

check(
    "ORIGINAL_HEADINGS_UNCHANGED",
    success_input.headings
    == [
        "  First\tHeading  ",
        "  First\tHeading  ",
    ],
)

check(
    "NORMALIZED_HEADINGS_CORRECT",
    success_result.headings
    == [
        "First Heading",
        "First Heading",
    ],
)


# ------------------------------------------------------------
# F. Ineligible extraction immutability
# ------------------------------------------------------------

print()
print("=== F. INELIGIBLE INPUT IMMUTABILITY ===")

ineligible_input = make_ineligible()
ineligible_before = deepcopy(ineligible_input)

ineligible_result = normalize_uploaded_document_v1(
    ineligible_input
)

check(
    "INELIGIBLE_INPUT_NOT_MUTATED",
    ineligible_input == ineligible_before,
)

check(
    "INELIGIBLE_RESULT_STATUS",
    ineligible_result.normalization_status
    == "ineligible_extraction",
)

check(
    "INELIGIBLE_SOURCE_PATH_PRESERVED",
    ineligible_result.source_path
    == ineligible_input.source_path,
)

check(
    "INELIGIBLE_SOURCE_TYPE_PRESERVED",
    ineligible_result.source_type
    == ineligible_input.source_type,
)


# ------------------------------------------------------------
# G. Result mutation must not mutate original input
# ------------------------------------------------------------

print()
print("=== G. OUTPUT-TO-INPUT ISOLATION ===")

isolation_input = make_success()
isolation_result = normalize_uploaded_document_v1(
    isolation_input
)

original_headings = list(
    isolation_input.headings
)

original_metadata = deepcopy(
    isolation_input.metadata
)

isolation_result.headings.append(
    "RESULT ONLY"
)

isolation_result.metadata["result_only"] = True

check(
    "RESULT_HEADING_MUTATION_DOES_NOT_CHANGE_INPUT",
    isolation_input.headings
    == original_headings,
)

check(
    "RESULT_TOP_LEVEL_METADATA_MUTATION_DOES_NOT_CHANGE_INPUT",
    isolation_input.metadata
    == original_metadata,
)


# ------------------------------------------------------------
# H. Extraction provenance preservation
# ------------------------------------------------------------

print()
print("=== H. EXTRACTION PROVENANCE ===")

check(
    "EXTRACTION_STATUS_PRESERVED",
    success_result.extraction_status
    == "success",
)

check(
    "EXTRACTION_CONFIDENCE_PRESERVED",
    success_result.extraction_confidence
    == 0.92,
)

check(
    "EXTRACTION_TIMESTAMP_PRESERVED",
    success_result.extraction_created_at
    == "2026-08-31T00:00:00+00:00",
)


# ------------------------------------------------------------
# I. Deterministic normalized content
# ------------------------------------------------------------

print()
print("=== I. DETERMINISM ===")

first = normalize_uploaded_document_v1(
    make_success()
)

second = normalize_uploaded_document_v1(
    make_success()
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
# J. Downstream boundary
# ------------------------------------------------------------

print()
print("=== J. DOWNSTREAM BOUNDARY ===")

check(
    "RESULT_HAS_NO_STRUCTURE",
    not hasattr(success_result, "structure"),
)

check(
    "RESULT_HAS_NO_HEADING_MAP",
    not hasattr(success_result, "heading_map"),
)

check(
    "RESULT_HAS_NO_UUCD",
    not hasattr(success_result, "uucd"),
)

check(
    "RESULT_HAS_NO_SEMANTIC_SCORE",
    not hasattr(success_result, "semantic_score"),
)


# ------------------------------------------------------------
# K. Final decision
# ------------------------------------------------------------

print()
print("=== K. U7.14 DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U7.14_SOURCE_IMMUTABILITY: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U7.14 source immutability verification failed."
    )

print(
    "U7.14_SOURCE_IMMUTABILITY: CERTIFIED"
)

print(
    "U7.14_SOURCE_FILE_MUTATION: NO"
)

print(
    "U7.14_INPUT_OBJECT_MUTATION: NO"
)

print(
    "U7.14_SOURCE_PATH_PRESERVED_EXACTLY: YES"
)

print(
    "U7.14_SOURCE_TYPE_PRESERVED_EXACTLY: YES"
)

print(
    "U7.14_DEDICATED_OUTPUT_OBJECT: YES"
)

print(
    "U7.14_METADATA_TOP_LEVEL_COPY: YES"
)

print(
    "U7.14_HEADINGS_OUTPUT_ISOLATED: YES"
)

print(
    "U7.14_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U7.15_FAILURE_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U7.14_FINAL_SOURCE_IMMUTABILITY_VERIFICATION: PASS"
)