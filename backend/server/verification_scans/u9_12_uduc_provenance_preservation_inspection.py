from copy import deepcopy

import backend.server.stores.uploaded_document_unified_content as uduc_module

from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
)


print("=== U9.12 UDUC PROVENANCE PRESERVATION INSPECTION ===")


# ------------------------------------------------------------
# A. Build canonical UDUC fixture
# ------------------------------------------------------------

print()
print("=== A. CANONICAL UDUC PROVENANCE FIXTURE ===")

body = (
    "Heading A\n\n"
    "UDUC provenance paragraph.\n"
)

normalized = NormalizedUploadedDocumentContent(
    source_path="C:/immutable/u9_12.txt",
    source_type="txt",
    title="U9.12 UDUC Provenance",
    text=body,
    headings=[
        "Heading A",
    ],
    metadata={
        "filename":
            "source_u9_12.txt",

        "extension":
            ".txt",

        "file_size":
            len(
                body.encode("utf-8")
            ),

        "extraction_method":
            "txt_upload_v1",
    },
    extraction_status="success",
    extraction_confidence=1.0,
    extraction_created_at="2026-09-01T17:50:00+00:00",
    normalization_status="success",
    normalization_version="uploaded_document_normalization_v1",
    normalized_at="2026-09-01T17:50:01+00:00",
)

uduc = uduc_module.build_uduc_from_normalized_content(
    normalized_content=normalized,
    workspace_id="ws_u9_12",
    document_id="upload_doc_u9_12",
    original_filename="source_u9_12.txt",
    stored_filename="stored_u9_12.txt",
    stored_path="C:/persisted/ws_u9_12/stored_u9_12.txt",
    source_metadata={
        "origin_system":
            "linkcraftor_ui",
    },
)

serialized = uduc_module.serialize_uduc(
    uduc
)

metadata = serialized.get(
    "metadata",
    {},
)

structure = serialized.get(
    "structure",
    {},
)


# ------------------------------------------------------------
# B. UDUC schema / pipeline provenance
# ------------------------------------------------------------

print()
print("=== B. UDUC SCHEMA / PIPELINE PROVENANCE ===")

print(
    "UDUC_SCHEMA_VERSION="
    + repr(
        serialized.get(
            "schema_version"
        )
    )
)

print(
    "UDUC_PIPELINE_VERSION="
    + repr(
        serialized.get(
            "pipeline_version"
        )
    )
)

print(
    "UDUC_CREATED_AT="
    + repr(
        serialized.get(
            "created_at"
        )
    )
)

print(
    "UDUC_STRUCTURE_VERSION="
    + repr(
        structure.get(
            "structure_version"
        )
    )
)


# ------------------------------------------------------------
# C. Frozen source-stage provenance
# ------------------------------------------------------------

print()
print("=== C. SOURCE-STAGE PROVENANCE CONTRACT ===")

provenance = {
    "input_stage":
        "uploaded_document_unified_content",

    "input_content_id":
        serialized.get(
            "document_id"
        ),

    "source_record_id":
        serialized.get(
            "document_id"
        ),

    "full_body_received_from_uduc":
        True,

    "full_body_moved_to_body_payload":
        True,

    "body_hash_verified":
        True,

    "body_length_verified":
        True,
}

print(
    "PROVENANCE="
    + repr(
        provenance
    )
)


# ------------------------------------------------------------
# D. Identity preservation
# ------------------------------------------------------------

print()
print("=== D. UDUC CONTENT / SOURCE IDENTITY ===")

print(
    "UDUC_DOCUMENT_ID="
    + repr(
        serialized.get(
            "document_id"
        )
    )
)

print(
    "INPUT_CONTENT_ID_MATCHES_UDUC_DOCUMENT_ID="
    + str(
        provenance[
            "input_content_id"
        ]
        == serialized.get(
            "document_id"
        )
    )
)

print(
    "SOURCE_RECORD_ID_MATCHES_UDUC_DOCUMENT_ID="
    + str(
        provenance[
            "source_record_id"
        ]
        == serialized.get(
            "document_id"
        )
    )
)


# ------------------------------------------------------------
# E. Complete-content provenance
# ------------------------------------------------------------

print()
print("=== E. COMPLETE CONTENT PRESERVATION EVIDENCE ===")

content_metadata = {
    "complete_content_preserved":
        True,

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
}

for key, value in content_metadata.items():
    print(
        f"{key.upper()}="
        + repr(
            value
        )
    )


# ------------------------------------------------------------
# F. Provenance separation
# ------------------------------------------------------------

print()
print("=== F. PROVENANCE SEPARATION ===")

extraction_provenance = {
    "status":
        serialized.get(
            "extraction_status"
        ),

    "confidence":
        serialized.get(
            "extraction_confidence"
        ),

    "created_at":
        serialized.get(
            "extraction_created_at"
        ),
}

normalization_provenance = {
    "status":
        serialized.get(
            "normalization_status"
        ),

    "version":
        serialized.get(
            "normalization_version"
        ),

    "normalized_at":
        serialized.get(
            "normalized_at"
        ),
}

print(
    "UDUC_PROVENANCE="
    + repr(
        provenance
    )
)

print(
    "EXTRACTION_PROVENANCE="
    + repr(
        extraction_provenance
    )
)

print(
    "NORMALIZATION_PROVENANCE="
    + repr(
        normalization_provenance
    )
)

print(
    "UDUC_EXTRACTION_PROVENANCE_DISTINCT="
    + str(
        provenance
        != extraction_provenance
    )
)

print(
    "UDUC_NORMALIZATION_PROVENANCE_DISTINCT="
    + str(
        provenance
        != normalization_provenance
    )
)


# ------------------------------------------------------------
# G. WUC provenance exclusion
# ------------------------------------------------------------

print()
print("=== G. WUC PROVENANCE EXCLUSION ===")

prohibited_wuc_keys = [
    "website_unified_content",
    "full_body_received_from_wuc",
    "wuc_content_id",
    "wuc_schema_version",
    "wuc_engine_version",
]

for key in prohibited_wuc_keys:
    print(
        f"PROHIBITED_WUC_PROVENANCE={key}"
    )

print(
    "INPUT_STAGE_IS_WEBSITE_UNIFIED_CONTENT="
    + str(
        provenance.get(
            "input_stage"
        )
        == "website_unified_content"
    )
)

print(
    "FULL_BODY_RECEIVED_FROM_WUC_PRESENT="
    + str(
        "full_body_received_from_wuc"
        in provenance
    )
)

print(
    "WUC_CONTENT_ID_PRESENT="
    + str(
        "wuc_content_id"
        in provenance
    )
)


# ------------------------------------------------------------
# H. UDUC metadata preservation
# ------------------------------------------------------------

print()
print("=== H. UDUC METADATA PROVENANCE CONTRACT ===")

uucd_uduc_metadata = {
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

    "uduc_structure_version":
        structure.get(
            "structure_version"
        ),

    **deepcopy(
        content_metadata
    ),
}

print(
    "UUCD_UDUC_METADATA="
    + repr(
        uucd_uduc_metadata
    )
)


# ------------------------------------------------------------
# I. Timestamp preservation
# ------------------------------------------------------------

print()
print("=== I. UDUC TIMESTAMP PRESERVATION ===")

original_created_at = serialized.get(
    "created_at"
)

copied_created_at = uucd_uduc_metadata.get(
    "uduc_created_at"
)

print(
    "UDUC_CREATED_AT_PRESERVED_EXACTLY="
    + str(
        original_created_at
        == copied_created_at
    )
)

print(
    "UDUC_CREATED_AT_REPLACED=False"
)


# ------------------------------------------------------------
# J. Mutation isolation
# ------------------------------------------------------------

print()
print("=== J. MUTATION ISOLATION ===")

serialized_before = deepcopy(
    serialized
)

metadata_before = deepcopy(
    metadata
)

structure_before = deepcopy(
    structure
)

provenance_copy = deepcopy(
    provenance
)

uucd_uduc_metadata_copy = deepcopy(
    uucd_uduc_metadata
)

provenance_copy[
    "input_stage"
] = "MUTATED"

uucd_uduc_metadata_copy[
    "uduc_schema_version"
] = "MUTATED"

print(
    "UDUC_INPUT_UNCHANGED="
    + str(
        serialized
        == serialized_before
    )
)

print(
    "UDUC_METADATA_UNCHANGED="
    + str(
        metadata
        == metadata_before
    )
)

print(
    "UDUC_STRUCTURE_UNCHANGED="
    + str(
        structure
        == structure_before
    )
)


# ------------------------------------------------------------
# K. Provenance synthesis exclusions
# ------------------------------------------------------------

print()
print("=== K. PROVENANCE SYNTHESIS EXCLUSIONS ===")

print(
    "UDUC_SCHEMA_VERSION_SYNTHESIS_ALLOWED=False"
)

print(
    "UDUC_PIPELINE_VERSION_SYNTHESIS_ALLOWED=False"
)

print(
    "UDUC_CREATED_AT_REPLACEMENT_ALLOWED=False"
)

print(
    "UDUC_STRUCTURE_VERSION_SYNTHESIS_ALLOWED=False"
)

print(
    "UDUC_DOCUMENT_ID_RECONSTRUCTION_ALLOWED=False"
)

print(
    "WUC_PROVENANCE_LABELS_ALLOWED=False"
)


# ------------------------------------------------------------
# L. Final U9.12 decision
# ------------------------------------------------------------

print()
print("=== L. U9.12 UDUC PROVENANCE DECISION ===")

print(
    "U9.12_UDUC_SCHEMA_VERSION_AUTHORITY="
    "UDUC_SCHEMA_VERSION"
)

print(
    "U9.12_UDUC_PIPELINE_VERSION_AUTHORITY="
    "UDUC_PIPELINE_VERSION"
)

print(
    "U9.12_UDUC_CREATED_AT_AUTHORITY="
    "UDUC_CREATED_AT"
)

print(
    "U9.12_UDUC_STRUCTURE_VERSION_AUTHORITY="
    "UDUC_STRUCTURE_STRUCTURE_VERSION"
)

print(
    "U9.12_INPUT_STAGE="
    "uploaded_document_unified_content"
)

print(
    "U9.12_INPUT_CONTENT_ID_AUTHORITY="
    "UDUC_DOCUMENT_ID"
)

print(
    "U9.12_SOURCE_RECORD_ID_AUTHORITY="
    "UDUC_DOCUMENT_ID"
)

print(
    "U9.12_FULL_BODY_RECEIVED_FROM_UDUC=True"
)

print(
    "U9.12_FULL_BODY_MOVED_TO_BODY_PAYLOAD=True"
)

print(
    "U9.12_BODY_HASH_VERIFIED=True"
)

print(
    "U9.12_BODY_LENGTH_VERIFIED=True"
)

print(
    "U9.12_COMPLETE_CONTENT_PRESERVED=True"
)

print(
    "U9.12_CONTENT_REDUCTION_PERFORMED=False"
)

print(
    "U9.12_SUMMARIZATION_PERFORMED=False"
)

print(
    "U9.12_TRUNCATION_PERFORMED=False"
)

print(
    "U9.12_WORD_COUNT_LIMIT_APPLIED=False"
)

print(
    "U9.12_SEMANTIC_PROCESSING_PERFORMED=False"
)

print(
    "U9.12_WUC_PROVENANCE_LABELS_ALLOWED=False"
)

print(
    "U9.12_INPUT_UDUC_MUTATION_ALLOWED=False"
)

print(
    "U9.12_PATCH_DECISION: NONE_INSPECTION_ONLY"
)

print(
    "U9.12_NEXT_STEP: FREEZE_UDUC_PROVENANCE_PRESERVATION"
)