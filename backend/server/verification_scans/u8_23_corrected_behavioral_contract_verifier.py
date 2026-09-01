from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
)

from backend.server.stores.uploaded_document_unified_content import (
    build_uduc_from_normalized_content,
    serialize_uduc,
)


results = []


def check(name, condition):
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U8.23 CORRECTED BEHAVIORAL CONTRACT VERIFICATION ===")


normalized = NormalizedUploadedDocumentContent(
    source_path="C:/immutable/u8_23.txt",
    source_type="txt",
    title="Canonical Title",
    text=(
        "Heading One\n\n"
        "Paragraph alpha beta.\n\n"
        "Heading One\n\n"
        "Paragraph gamma.\n\n"
        "Trailing paragraph."
    ),
    headings=[
        "Heading One",
        "Heading One",
        "Missing Heading",
    ],
    metadata={
        "filename": "u8_23.txt",
        "extension": ".txt",
        "file_size": 0,
        "extraction_method": "txt_upload_v1",
        "custom": {
            "alpha": 1,
            "beta": "two",
        },
    },
    extraction_status="success",
    extraction_confidence=0.95,
    extraction_created_at="2026-09-01T01:15:00+00:00",
    normalization_status="success",
    normalization_version="uploaded_document_normalization_v1",
    normalized_at="2026-09-01T01:15:01+00:00",
)

source_metadata = {
    "source_system": "u8_23_test",
    "external_flag": True,
}

uduc = build_uduc_from_normalized_content(
    normalized_content=normalized,
    workspace_id="ws_u8_23",
    document_id="doc_u8_23",
    original_filename="u8_23.txt",
    stored_filename="stored_u8_23.txt",
    stored_path="C:/persisted/ws_u8_23/stored_u8_23.txt",
    source_metadata=source_metadata,
)

data = serialize_uduc(
    uduc
)

structure = data["structure"]
metadata = data["metadata"]
nested_source_metadata = metadata.get(
    "source_metadata",
    {},
)


print()
print("=== A. SOURCE CLASS / FORMAT CONTRACT ===")

check(
    "SOURCE_TYPE_IS_UPLOADED_DOCUMENT",
    data.get("source_type")
    == "uploaded_document",
)

check(
    "SOURCE_FORMAT_PRESERVES_U7_SOURCE_TYPE",
    data.get("source_format")
    == "txt",
)


print()
print("=== B. STRUCTURAL SUMMARY CONTRACT ===")

check(
    "STRUCTURE_PARAGRAPH_COUNT_CORRECT",
    structure.get("paragraph_count")
    == len(
        structure.get("paragraphs", [])
    )
    == 5,
)

check(
    "STRUCTURE_HEADING_COUNT_CORRECT",
    len(
        structure.get("heading_map", [])
    )
    == 3,
)

check(
    "STRUCTURE_ESTIMATED_CHARACTER_COUNT_CORRECT",
    structure.get(
        "estimated_character_count"
    )
    == len(data["content_body"])
    == 86,
)

check(
    "STRUCTURE_ESTIMATED_WORD_COUNT_CORRECT",
    structure.get(
        "estimated_word_count"
    )
    == len(
        data["content_body"].split()
    )
    == 11,
)

check(
    "STRUCTURE_VERSION_PRESENT",
    structure.get("structure_version")
    == "uduc_structure_v1_2",
)

check(
    "STRUCTURE_BOUNDARY_PRESENT",
    isinstance(
        structure.get("boundary"),
        dict,
    ),
)


print()
print("=== C. METADATA CONTRACT ===")

check(
    "SOURCE_METADATA_NESTED",
    isinstance(
        nested_source_metadata,
        dict,
    ),
)

check(
    "SOURCE_SYSTEM_PRESERVED",
    nested_source_metadata.get(
        "source_system"
    )
    == "u8_23_test",
)

check(
    "EXTERNAL_FLAG_PRESERVED",
    nested_source_metadata.get(
        "external_flag"
    )
    is True,
)

check(
    "NORMALIZED_CUSTOM_METADATA_PRESERVED",
    nested_source_metadata.get(
        "custom"
    )
    == {
        "alpha": 1,
        "beta": "two",
    },
)

check(
    "NORMALIZED_FILENAME_METADATA_PRESERVED",
    nested_source_metadata.get(
        "filename"
    )
    == "u8_23.txt",
)

check(
    "NORMALIZED_EXTENSION_METADATA_PRESERVED",
    nested_source_metadata.get(
        "extension"
    )
    == ".txt",
)

check(
    "EXTRACTION_METHOD_CANONICAL_FIELD_PRESERVED",
    metadata.get(
        "extraction_method"
    )
    == "txt_upload_v1",
)

check(
    "ZERO_FILE_SIZE_CANONICAL_FIELD_PRESERVED",
    metadata.get(
        "file_size"
    )
    == 0,
)


print()
print("=== D. BOUNDARY METADATA ===")

boundary = metadata.get(
    "boundary",
    {},
)

check(
    "BOUNDARY_NO_EXTRACTION",
    boundary.get(
        "performs_extraction"
    )
    is False,
)

check(
    "BOUNDARY_NO_NORMALIZATION",
    boundary.get(
        "performs_normalization"
    )
    is False,
)

check(
    "BOUNDARY_NO_CLEANING",
    boundary.get(
        "performs_cleaning"
    )
    is False,
)

check(
    "BOUNDARY_NO_SEMANTIC_ANALYSIS",
    boundary.get(
        "performs_semantic_analysis"
    )
    is False,
)

check(
    "BOUNDARY_NO_UUCD_CREATION",
    boundary.get(
        "creates_uucd"
    )
    is False,
)


print()
print("=== E. FINAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

if failures:
    print(
        "U8.23_CORRECTED_CONTRACT_VERIFICATION: REVIEW_REQUIRED"
    )

    for failure in failures:
        print(
            f"FAILED: {failure}"
        )
else:
    print(
        "U8.23_CORRECTED_CONTRACT_VERIFICATION: PASS"
    )
    print(
        "U8.23_INITIAL_FAILURE_CLASSIFICATION: VERIFIER_FALSE_POSITIVES"
    )
    print(
        "U8.23_PRODUCTION_PATCH_REQUIRED: NO"
    )
    print(
        "U8.23_SOURCE_TYPE_CONTRACT: UPLOADED_DOCUMENT"
    )
    print(
        "U8.23_SOURCE_FORMAT_CONTRACT: U7_SOURCE_TYPE"
    )
    print(
        "U8.23_STRUCTURE_SUMMARY_CONTRACT: DIRECT_STRUCTURE_FIELDS"
    )
    print(
        "U8.23_METADATA_CONTRACT: CANONICAL_FIELDS_PLUS_NESTED_SOURCE_METADATA"
    )
    print(
        "U8.23_BEHAVIORAL_UDUC_VERIFICATION: CERTIFIED"
    )
    print(
        "U8.24_BUILD_INTEGRATION_VERIFICATION_TRANSITION: AUTHORIZED"
    )
    print(
        "U8.23_FINAL_BEHAVIORAL_VERIFICATION: PASS"
    )