from copy import deepcopy

import backend.server.stores.uploaded_document_unified_content as uduc_module

from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
)


print("=== U9.9 SOURCE METADATA CONVERGENCE INSPECTION ===")


# ------------------------------------------------------------
# A. Build canonical UDUC fixture with rich metadata
# ------------------------------------------------------------

print()
print("=== A. CANONICAL UDUC METADATA FIXTURE ===")

body = (
    "Heading A\n\n"
    "Metadata paragraph."
)

normalized = NormalizedUploadedDocumentContent(
    source_path="C:/immutable/u9_9.docx",
    source_type="docx",
    title="U9.9 Metadata Contract",
    text=body,
    headings=[
        "Heading A",
    ],
    metadata={
        "filename":
            "source_u9_9.docx",

        "extension":
            ".docx",

        "file_size":
            54321,

        "extraction_method":
            "docx_upload_v1",

        "paragraph_count":
            2,

        "heading_count":
            1,

        "line_count":
            3,

        "custom": {
            "department":
                "editorial",

            "batch":
                "u9_9",
        },
    },
    extraction_status="success",
    extraction_confidence=0.99,
    extraction_created_at="2026-09-01T17:40:00+00:00",
    normalization_status="success",
    normalization_version="uploaded_document_normalization_v1",
    normalized_at="2026-09-01T17:40:01+00:00",
)

uduc = uduc_module.build_uduc_from_normalized_content(
    normalized_content=normalized,
    workspace_id="ws_u9_9",
    document_id="upload_doc_u9_9",
    original_filename="source_u9_9.docx",
    stored_filename="stored_u9_9.docx",
    stored_path="C:/persisted/ws_u9_9/stored_u9_9.docx",
    source_metadata={
        "source_snapshot_reference":
            "snapshot/u9_9/001",

        "version_asset_reference":
            "version/u9_9/001",

        "origin_system":
            "linkcraftor_ui",

        "custom_source_flag":
            True,
    },
)

serialized = uduc_module.serialize_uduc(
    uduc
)

metadata = serialized.get(
    "metadata",
    {},
)

source_metadata = metadata.get(
    "source_metadata",
    {},
)


print(
    "UDUC_ORIGINAL_FILENAME="
    + repr(
        serialized.get(
            "original_filename"
        )
    )
)

print(
    "UDUC_STORED_FILENAME="
    + repr(
        serialized.get(
            "stored_filename"
        )
    )
)

print(
    "UDUC_STORED_PATH="
    + repr(
        serialized.get(
            "stored_path"
        )
    )
)

print(
    "UDUC_SOURCE_FORMAT="
    + repr(
        serialized.get(
            "source_format"
        )
    )
)


# ------------------------------------------------------------
# B. Top-level UDUC metadata inventory
# ------------------------------------------------------------

print()
print("=== B. TOP-LEVEL UDUC METADATA INVENTORY ===")

print(
    "UDUC_METADATA_TYPE="
    + type(
        metadata
    ).__name__
)

print(
    "UDUC_METADATA_KEYS="
    + repr(
        list(
            metadata.keys()
        )
    )
)

for key, value in metadata.items():
    print(
        f"UDUC_METADATA_{key.upper()}="
        + repr(value)
    )


# ------------------------------------------------------------
# C. Nested source_metadata inventory
# ------------------------------------------------------------

print()
print("=== C. NESTED SOURCE_METADATA INVENTORY ===")

print(
    "SOURCE_METADATA_TYPE="
    + type(
        source_metadata
    ).__name__
)

print(
    "SOURCE_METADATA_KEYS="
    + repr(
        list(
            source_metadata.keys()
        )
    )
)

for key, value in source_metadata.items():
    print(
        f"SOURCE_METADATA_{key.upper()}="
        + repr(value)
    )


# ------------------------------------------------------------
# D. Identity-source candidates
# ------------------------------------------------------------

print()
print("=== D. UUCD SOURCE_IDENTITY CANDIDATES ===")

source_identity = {
    "source_record_id":
        serialized.get(
            "document_id"
        ),

    "original_filename":
        serialized.get(
            "original_filename"
        ),

    "stored_filename":
        serialized.get(
            "stored_filename"
        ),

    "stored_path":
        serialized.get(
            "stored_path"
        ),
}

for optional_key in [
    "source_snapshot_reference",
    "version_asset_reference",
]:
    value = source_metadata.get(
        optional_key
    )

    if value not in (
        None,
        "",
    ):
        source_identity[
            optional_key
        ] = value


print(
    "SOURCE_IDENTITY="
    + repr(
        source_identity
    )
)


# ------------------------------------------------------------
# E. Optional references are copy-only
# ------------------------------------------------------------

print()
print("=== E. OPTIONAL SNAPSHOT / VERSION REFERENCES ===")

print(
    "SOURCE_SNAPSHOT_REFERENCE_PRESENT="
    + str(
        "source_snapshot_reference"
        in source_metadata
    )
)

print(
    "VERSION_ASSET_REFERENCE_PRESENT="
    + str(
        "version_asset_reference"
        in source_metadata
    )
)

missing_source_metadata = {
    "origin_system":
        "linkcraftor_ui"
}

missing_identity = {
    "source_record_id":
        serialized.get(
            "document_id"
        ),
}

for optional_key in [
    "source_snapshot_reference",
    "version_asset_reference",
]:
    value = missing_source_metadata.get(
        optional_key
    )

    if value not in (
        None,
        "",
    ):
        missing_identity[
            optional_key
        ] = value

print(
    "MISSING_OPTIONAL_REFS_SYNTHESIZED="
    + str(
        "source_snapshot_reference"
        in missing_identity
        or "version_asset_reference"
        in missing_identity
    )
)


# ------------------------------------------------------------
# F. Extraction/source metadata preservation
# ------------------------------------------------------------

print()
print("=== F. EXTRACTION / SOURCE METADATA PRESERVATION ===")

expected_metadata_fields = [
    "extension",
    "file_size",
    "extraction_method",
    "extraction_timestamp",
    "paragraph_count",
    "heading_count",
    "line_count",
    "source_metadata",
    "normalization",
    "boundary",
]

for field in expected_metadata_fields:
    print(
        f"METADATA_FIELD_{field.upper()}_PRESENT="
        + str(
            field
            in metadata
        )
    )


for key in [
    "extension",
    "file_size",
    "extraction_method",
    "paragraph_count",
    "heading_count",
    "line_count",
]:
    print(
        f"METADATA_VALUE_{key.upper()}="
        + repr(
            metadata.get(
                key
            )
        )
    )


# ------------------------------------------------------------
# G. Custom source metadata preservation
# ------------------------------------------------------------

print()
print("=== G. CUSTOM SOURCE METADATA PRESERVATION ===")

print(
    "CUSTOM_SOURCE_FLAG_PRESERVED="
    + str(
        source_metadata.get(
            "custom_source_flag"
        )
        is True
    )
)

print(
    "ORIGIN_SYSTEM_PRESERVED="
    + str(
        source_metadata.get(
            "origin_system"
        )
        == "linkcraftor_ui"
    )
)

print(
    "NESTED_CUSTOM_METADATA="
    + repr(
        source_metadata.get(
            "custom"
        )
    )
)


# ------------------------------------------------------------
# H. Proposed Uploaded Document UUCD metadata
# ------------------------------------------------------------

print()
print("=== H. UPLOADED DOCUMENT UUCD METADATA CONTRACT ===")

uucd_metadata = {
    "uduc_schema_version":
        serialized.get(
            "schema_version"
        ),

    "uduc_pipeline_version":
        serialized.get(
            "pipeline_version"
        ),

    "uduc_created_at":
        serialized.get(
            "created_at"
        ),

    "complete_content_preserved":
        True,

    "content_body_in_uucd_record":
        False,

    "body_transport":
        "UNIVERSAL_BODY_PAYLOAD",

    "content_reduction_performed":
        False,

    "summarization_performed":
        False,

    "truncation_performed":
        False,

    "word_count_limit_applied":
        False,

    "semantic_processing_performed":
        False,

    "persistence_status":
        "NOT_PERSISTED",
}

print(
    "UUCD_METADATA="
    + repr(
        uucd_metadata
    )
)

for key in [
    "wuc_schema_version",
    "wuc_engine_version",
    "wuc_content_id",
]:
    print(
        f"WUC_METADATA_KEY_{key.upper()}_PRESENT="
        + str(
            key
            in uucd_metadata
        )
    )


# ------------------------------------------------------------
# I. Deep-copy / mutation isolation
# ------------------------------------------------------------

print()
print("=== I. METADATA DEEP-COPY / MUTATION ISOLATION ===")

metadata_before = deepcopy(
    metadata
)

source_metadata_before = deepcopy(
    source_metadata
)

metadata_copy = deepcopy(
    metadata
)

source_metadata_copy = deepcopy(
    source_metadata
)

metadata_copy[
    "file_size"
] = 999999

source_metadata_copy[
    "origin_system"
] = "MUTATED"

print(
    "INPUT_METADATA_UNCHANGED="
    + str(
        metadata
        == metadata_before
    )
)

print(
    "INPUT_SOURCE_METADATA_UNCHANGED="
    + str(
        source_metadata
        == source_metadata_before
    )
)

print(
    "METADATA_COPY_SAME_OBJECT="
    + str(
        metadata_copy
        is metadata
    )
)

print(
    "SOURCE_METADATA_COPY_SAME_OBJECT="
    + str(
        source_metadata_copy
        is source_metadata
    )
)


# ------------------------------------------------------------
# J. No flattening evidence
# ------------------------------------------------------------

print()
print("=== J. SOURCE_METADATA NESTING CONTRACT ===")

print(
    "SOURCE_METADATA_REMAINS_NESTED="
    + str(
        isinstance(
            metadata.get(
                "source_metadata"
            ),
            dict,
        )
    )
)

print(
    "SOURCE_METADATA_FLATTENING_REQUIRED=False"
)


# ------------------------------------------------------------
# K. Final U9.9 decision
# ------------------------------------------------------------

print()
print("=== K. U9.9 SOURCE METADATA DECISION ===")

print(
    "U9.9_METADATA_AUTHORITY="
    "UDUC_METADATA"
)

print(
    "U9.9_SOURCE_IDENTITY_AUTHORITY="
    "UDUC_IDENTITY_FIELDS_PLUS_OPTIONAL_SOURCE_METADATA_REFS"
)

print(
    "U9.9_SOURCE_METADATA_PRESERVATION="
    "DEEPCOPY_NESTED"
)

print(
    "U9.9_SOURCE_SNAPSHOT_REFERENCE="
    "COPY_IF_PRESENT"
)

print(
    "U9.9_VERSION_ASSET_REFERENCE="
    "COPY_IF_PRESENT"
)

print(
    "U9.9_MISSING_OPTIONAL_REFERENCE_SYNTHESIS=False"
)

print(
    "U9.9_WUC_METADATA_LABELS_ALLOWED=False"
)

print(
    "U9.9_SOURCE_FILE_METADATA_REREAD_ALLOWED=False"
)

print(
    "U9.9_INPUT_METADATA_MUTATION_ALLOWED=False"
)

print(
    "U9.9_PATCH_DECISION: NONE_INSPECTION_ONLY"
)

print(
    "U9.9_NEXT_STEP: FREEZE_SOURCE_METADATA_CONVERGENCE"
)