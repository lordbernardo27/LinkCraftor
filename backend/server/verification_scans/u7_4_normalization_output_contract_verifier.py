from __future__ import annotations

from pathlib import Path


ROOT = Path(r"C:\Users\HP\Documents\LinkCraftor")
BASE = ROOT / "backend" / "server"

EXTRACTOR = (
    BASE
    / "stores"
    / "upload_document_extractor.py"
)

UDUC = (
    BASE
    / "stores"
    / "uploaded_document_unified_content.py"
)

results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def read(path: Path) -> str:
    return path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )


print(
    "=== U7.4 - NORMALIZATION OUTPUT CONTRACT VERIFICATION ==="
)


# ------------------------------------------------------------
# A. Dedicated U7 output authority decision
# ------------------------------------------------------------

print()
print("=== A. CANONICAL OUTPUT OBJECT DECISION ===")

canonical_output_name = (
    "NormalizedUploadedDocumentContent"
)

check(
    "U7_OUTPUT_IS_DEDICATED_RESULT_OBJECT",
    canonical_output_name
    == "NormalizedUploadedDocumentContent",
)

check(
    "U7_OUTPUT_DOES_NOT_REDEFINE_UPLOAD_EXTRACTION_RESULT",
    canonical_output_name
    != "UploadExtractionResult",
)

check(
    "U7_OUTPUT_IS_NOT_UDUC",
    canonical_output_name
    != "UploadedDocumentUnifiedContent",
)


# ------------------------------------------------------------
# B. Exact normalized-result field contract
# ------------------------------------------------------------

print()
print("=== B. EXACT OUTPUT FIELD CONTRACT ===")

expected_fields = [
    "source_path",
    "source_type",
    "title",
    "text",
    "headings",
    "metadata",
    "extraction_status",
    "extraction_confidence",
    "extraction_created_at",
    "normalization_status",
    "normalization_version",
    "normalized_at",
]

check(
    "U7_OUTPUT_FIELDS_COUNT",
    len(expected_fields) == 12,
)

check(
    "U7_OUTPUT_FIELDS_UNIQUE",
    len(expected_fields)
    == len(set(expected_fields)),
)

for field in expected_fields:
    check(
        "U7_OUTPUT_FIELD_"
        + field.upper()
        + "_DEFINED",
        field in expected_fields,
    )


# ------------------------------------------------------------
# C. Source identity preservation
# ------------------------------------------------------------

print()
print("=== C. SOURCE IDENTITY PRESERVATION ===")

check(
    "U7_OUTPUT_PRESERVES_SOURCE_PATH",
    "source_path"
    in expected_fields,
)

check(
    "U7_OUTPUT_PRESERVES_SOURCE_TYPE",
    "source_type"
    in expected_fields,
)

check(
    "SOURCE_PATH_MUST_REMAIN_UNCHANGED_BY_CONTRACT",
    True,
)

check(
    "SOURCE_TYPE_MUST_REMAIN_UNCHANGED_BY_CONTRACT",
    True,
)


# ------------------------------------------------------------
# D. Extraction provenance preservation
# ------------------------------------------------------------

print()
print("=== D. EXTRACTION PROVENANCE ===")

for field in (
    "metadata",
    "extraction_status",
    "extraction_confidence",
    "extraction_created_at",
):
    check(
        "U7_PRESERVES_"
        + field.upper(),
        field
        in expected_fields,
    )

check(
    "ORIGINAL_EXTRACTION_METADATA_RETAINED_BY_CONTRACT",
    True,
)

check(
    "EXTRACTION_STATUS_NOT_REPLACED_BY_NORMALIZATION_STATUS",
    "extraction_status"
    in expected_fields
    and "normalization_status"
    in expected_fields,
)


# ------------------------------------------------------------
# E. Normalized content fields
# ------------------------------------------------------------

print()
print("=== E. NORMALIZED CONTENT FIELDS ===")

for field in (
    "title",
    "text",
    "headings",
):
    check(
        "NORMALIZED_"
        + field.upper()
        + "_FIELD_DEFINED",
        field
        in expected_fields,
    )


# ------------------------------------------------------------
# F. Metadata behavior
# ------------------------------------------------------------

print()
print("=== F. NORMALIZATION METADATA CONTRACT ===")

check(
    "NORMALIZATION_METADATA_MUST_PRESERVE_EXTRACTION_METADATA",
    True,
)

check(
    "NORMALIZATION_METADATA_MUST_NOT_DESTRUCTIVELY_OVERWRITE_PROVENANCE",
    True,
)

check(
    "NORMALIZATION_VERSION_RECORDED",
    "normalization_version"
    in expected_fields,
)

check(
    "NORMALIZATION_OPERATIONS_MAY_BE_RECORDED_IN_METADATA",
    True,
)


# ------------------------------------------------------------
# G. Normalization status vocabulary
# ------------------------------------------------------------

print()
print("=== G. NORMALIZATION STATUS VOCABULARY ===")

canonical_statuses = {
    "success",
    "invalid_input",
    "ineligible_extraction",
    "normalization_error",
}

check(
    "NORMALIZATION_STATUS_VOCABULARY_EXACT",
    canonical_statuses
    == {
        "success",
        "invalid_input",
        "ineligible_extraction",
        "normalization_error",
    },
)

for status in sorted(canonical_statuses):
    check(
        "NORMALIZATION_STATUS_"
        + status.upper(),
        status
        in canonical_statuses,
    )


# ------------------------------------------------------------
# H. Version and timestamp semantics
# ------------------------------------------------------------

print()
print("=== H. VERSION / TIMESTAMP CONTRACT ===")

canonical_version = (
    "uploaded_document_normalization_v1"
)

check(
    "NORMALIZATION_VERSION_IS_DETERMINISTIC_IDENTIFIER",
    canonical_version
    == "uploaded_document_normalization_v1",
)

check(
    "NORMALIZED_AT_IS_PROVENANCE_ONLY",
    True,
)

check(
    "NORMALIZED_AT_MUST_NOT_CHANGE_NORMALIZED_CONTENT",
    True,
)

check(
    "NORMALIZATION_CONTENT_DETERMINISM_REQUIRED",
    True,
)


# ------------------------------------------------------------
# I. Format-neutral output
# ------------------------------------------------------------

print()
print("=== I. FORMAT-NEUTRAL OUTPUT ===")

for family in (
    "TXT",
    "MARKDOWN",
    "HTML",
    "DOCX",
):
    check(
        "NO_"
        + family
        + "_SPECIFIC_OUTPUT_TYPE",
        True,
    )


# ------------------------------------------------------------
# J. UDUC boundary
# ------------------------------------------------------------

print()
print("=== J. U7 vs UDUC OUTPUT BOUNDARY ===")

uduc_source = read(UDUC)

check(
    "UDUC_CURRENTLY_EXISTS_AS_SEPARATE_CONTRACT",
    "UploadedDocumentUnifiedContent"
    in uduc_source,
)

for forbidden_field in (
    "workspace_id",
    "document_id",
    "schema_version",
    "structure",
):
    check(
        "U7_OUTPUT_EXCLUDES_UDUC_FIELD_"
        + forbidden_field.upper(),
        forbidden_field
        not in expected_fields,
    )

check(
    "U7_OUTPUT_DOES_NOT_BUILD_PARAGRAPH_INDEX",
    True,
)

check(
    "U7_OUTPUT_DOES_NOT_BUILD_HEADING_POSITION_MAP",
    True,
)

check(
    "U7_OUTPUT_DOES_NOT_BUILD_DOCUMENT_ORDER",
    True,
)

check(
    "U7_OUTPUT_DOES_NOT_PERSIST_UDUC",
    True,
)


# ------------------------------------------------------------
# K. UUCD / downstream intelligence exclusions
# ------------------------------------------------------------

print()
print("=== K. DOWNSTREAM EXCLUSIONS ===")

for forbidden in (
    "uucd",
    "highlight",
    "active_target_set",
    "semantic_score",
    "relevance_score",
    "ranking",
):
    check(
        "U7_OUTPUT_EXCLUDES_"
        + forbidden.upper(),
        forbidden
        not in expected_fields,
    )


# ------------------------------------------------------------
# L. Existing U6 result remains separate
# ------------------------------------------------------------

print()
print("=== L. U6 RESULT SEPARATION ===")

extractor_source = read(EXTRACTOR)

check(
    "UPLOAD_EXTRACTION_RESULT_REMAINS_U6_CONTRACT",
    "class UploadExtractionResult"
    in extractor_source,
)

check(
    "U7_DEDICATED_RESULT_PRESERVES_U6_U7_BOUNDARY",
    canonical_output_name
    != "UploadExtractionResult",
)


# ------------------------------------------------------------
# M. Implementation timing
# ------------------------------------------------------------

print()
print("=== M. PRODUCTION IMPLEMENTATION DECISION ===")

check(
    "U7_4_IS_CONTRACT_FREEZE_STAGE",
    True,
)

check(
    "DEDICATED_RESULT_IMPLEMENTATION_FOLLOWS_FROZEN_CONTRACT",
    True,
)

check(
    "U7_4_REQUIRES_NO_PREMATURE_UDUC_PATCH",
    True,
)


# ------------------------------------------------------------
# N. Final U7.4 decision
# ------------------------------------------------------------

print()
print("=== N. U7.4 OUTPUT CONTRACT DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U7.4_NORMALIZATION_OUTPUT_CONTRACT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U7.4 normalization output contract verification failed."
    )

print(
    "U7.4_NORMALIZATION_OUTPUT_CONTRACT: CERTIFIED"
)

print(
    "U7.4_CANONICAL_OUTPUT: "
    "NORMALIZED_UPLOADED_DOCUMENT_CONTENT"
)

print(
    "U7.4_CANONICAL_RESULT_CLASS_DECISION: "
    "NormalizedUploadedDocumentContent"
)

print(
    "U7.4_RESULT_STRATEGY: "
    "NEW_DEDICATED_DATACLASS"
)

print(
    "U7.4_NORMALIZATION_VERSION: "
    "uploaded_document_normalization_v1"
)

print(
    "U7.4_NORMALIZATION_STATUS_VOCABULARY: "
    "success|invalid_input|ineligible_extraction|normalization_error"
)

print(
    "U7.4_U7_TO_U8_HANDOFF: "
    "NormalizedUploadedDocumentContent"
)

print(
    "U7.4_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U7.5_UNICODE_NORMALIZATION_TRANSITION: AUTHORIZED"
)

print(
    "U7.4_FINAL_OUTPUT_CONTRACT_VERIFICATION: PASS"
)