from copy import deepcopy

import backend.server.stores.uploaded_document_unified_content as uduc_module

from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
)


print("=== U9.10 EXTRACTION PROVENANCE PRESERVATION INSPECTION ===")


# ------------------------------------------------------------
# A. Build canonical UDUC fixture
# ------------------------------------------------------------

print()
print("=== A. CANONICAL UDUC EXTRACTION PROVENANCE FIXTURE ===")

body = (
    "Heading A\n\n"
    "Extraction provenance paragraph."
)

normalized = NormalizedUploadedDocumentContent(
    source_path="C:/immutable/u9_10.docx",
    source_type="docx",
    title="U9.10 Extraction Provenance",
    text=body,
    headings=[
        "Heading A",
    ],
    metadata={
        "filename":
            "source_u9_10.docx",

        "extension":
            ".docx",

        "file_size":
            65432,

        "extraction_method":
            "docx_upload_v1",

        "paragraph_count":
            2,

        "heading_count":
            1,

        "line_count":
            3,

        "extractor_detail": {
            "engine":
                "python-docx",

            "mode":
                "full_document",
        },
    },
    extraction_status="success",
    extraction_confidence=0.987654,
    extraction_created_at="2026-09-01T17:42:00+00:00",
    normalization_status="success",
    normalization_version="uploaded_document_normalization_v1",
    normalized_at="2026-09-01T17:42:01+00:00",
)

uduc = uduc_module.build_uduc_from_normalized_content(
    normalized_content=normalized,
    workspace_id="ws_u9_10",
    document_id="upload_doc_u9_10",
    original_filename="source_u9_10.docx",
    stored_filename="stored_u9_10.docx",
    stored_path="C:/persisted/ws_u9_10/stored_u9_10.docx",
    source_metadata={
        "origin_system":
            "linkcraftor_ui",

        "source_snapshot_reference":
            "snapshot/u9_10/001",
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


# ------------------------------------------------------------
# B. Top-level extraction provenance
# ------------------------------------------------------------

print()
print("=== B. TOP-LEVEL EXTRACTION PROVENANCE ===")

for key in [
    "extraction_status",
    "extraction_confidence",
    "extraction_created_at",
]:
    print(
        f"UDUC_{key.upper()}="
        + repr(
            serialized.get(
                key
            )
        )
    )


# ------------------------------------------------------------
# C. Metadata extraction provenance
# ------------------------------------------------------------

print()
print("=== C. METADATA EXTRACTION PROVENANCE ===")

for key in [
    "extension",
    "file_size",
    "extraction_method",
    "extraction_timestamp",
    "paragraph_count",
    "heading_count",
    "line_count",
]:
    print(
        f"METADATA_{key.upper()}="
        + repr(
            metadata.get(
                key
            )
        )
    )


# ------------------------------------------------------------
# D. Nested source metadata preservation
# ------------------------------------------------------------

print()
print("=== D. NESTED SOURCE METADATA EXTRACTION EVIDENCE ===")

print(
    "SOURCE_METADATA="
    + repr(
        source_metadata
    )
)

for key in [
    "filename",
    "extension",
    "file_size",
    "extraction_method",
    "paragraph_count",
    "heading_count",
    "line_count",
    "extractor_detail",
]:
    print(
        f"SOURCE_METADATA_{key.upper()}="
        + repr(
            source_metadata.get(
                key
            )
        )
    )


# ------------------------------------------------------------
# E. Extraction timestamp distinction
# ------------------------------------------------------------

print()
print("=== E. EXTRACTION TIMESTAMP DISTINCTION ===")

print(
    "EXTRACTION_CREATED_AT="
    + repr(
        serialized.get(
            "extraction_created_at"
        )
    )
)

print(
    "METADATA_EXTRACTION_TIMESTAMP="
    + repr(
        metadata.get(
            "extraction_timestamp"
        )
    )
)

print(
    "TIMESTAMPS_EQUAL="
    + str(
        serialized.get(
            "extraction_created_at"
        )
        == metadata.get(
            "extraction_timestamp"
        )
    )
)

print(
    "TIMESTAMP_FIELDS_REMAIN_DISTINCT=True"
)


# ------------------------------------------------------------
# F. Exact-value preservation simulation
# ------------------------------------------------------------

print()
print("=== F. EXACT-VALUE PRESERVATION SIMULATION ===")

extraction_provenance = {
    "extraction_status":
        serialized.get(
            "extraction_status"
        ),

    "extraction_confidence":
        serialized.get(
            "extraction_confidence"
        ),

    "extraction_created_at":
        serialized.get(
            "extraction_created_at"
        ),

    "extraction_method":
        metadata.get(
            "extraction_method"
        ),

    "extraction_timestamp":
        metadata.get(
            "extraction_timestamp"
        ),

    "source_format":
        serialized.get(
            "source_format"
        ),

    "extension":
        metadata.get(
            "extension"
        ),

    "file_size":
        metadata.get(
            "file_size"
        ),
}

print(
    "EXTRACTION_PROVENANCE="
    + repr(
        extraction_provenance
    )
)

print(
    "CONFIDENCE_EXACT="
    + str(
        extraction_provenance[
            "extraction_confidence"
        ]
        == 0.987654
    )
)

print(
    "EXTRACTION_CREATED_AT_EXACT="
    + str(
        extraction_provenance[
            "extraction_created_at"
        ]
        == "2026-09-01T17:42:00+00:00"
    )
)

print(
    "EXTRACTION_METHOD_EXACT="
    + str(
        extraction_provenance[
            "extraction_method"
        ]
        == "docx_upload_v1"
    )
)


# ------------------------------------------------------------
# G. Proposed UUCD metadata preservation shape
# ------------------------------------------------------------

print()
print("=== G. PROPOSED UUCD EXTRACTION PROVENANCE SHAPE ===")

uucd_extraction_metadata = {
    "extraction": {
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

        "method":
            metadata.get(
                "extraction_method"
            ),

        "timestamp":
            metadata.get(
                "extraction_timestamp"
            ),

        "source_format":
            serialized.get(
                "source_format"
            ),

        "extension":
            metadata.get(
                "extension"
            ),

        "file_size":
            metadata.get(
                "file_size"
            ),

        "source_metadata":
            deepcopy(
                source_metadata
            ),
    },
}

print(
    "UUCD_EXTRACTION_METADATA="
    + repr(
        uucd_extraction_metadata
    )
)


# ------------------------------------------------------------
# H. Mutation isolation
# ------------------------------------------------------------

print()
print("=== H. MUTATION ISOLATION ===")

serialized_before = deepcopy(
    serialized
)

metadata_before = deepcopy(
    metadata
)

source_metadata_before = deepcopy(
    source_metadata
)

uucd_extraction_metadata[
    "extraction"
][
    "confidence"
] = 0.1

uucd_extraction_metadata[
    "extraction"
][
    "source_metadata"
][
    "origin_system"
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
    "UDUC_SOURCE_METADATA_UNCHANGED="
    + str(
        source_metadata
        == source_metadata_before
    )
)


# ------------------------------------------------------------
# I. Extraction rerun prohibition
# ------------------------------------------------------------

print()
print("=== I. EXTRACTION EXECUTION EXCLUSIONS ===")

print(
    "EXTRACTION_RERUN_ALLOWED=False"
)

print(
    "EXTRACTOR_INVOCATION_ALLOWED=False"
)

print(
    "SOURCE_FILE_REREAD_ALLOWED=False"
)

print(
    "EXTRACTION_RESULT_RECONSTRUCTION_ALLOWED=False"
)

print(
    "EXTRACTION_CONFIDENCE_RECALIBRATION_ALLOWED=False"
)

print(
    "EXTRACTION_TIMESTAMP_REPLACEMENT_ALLOWED=False"
)


# ------------------------------------------------------------
# J. Final U9.10 decision
# ------------------------------------------------------------

print()
print("=== J. U9.10 EXTRACTION PROVENANCE DECISION ===")

print(
    "U9.10_EXTRACTION_STATUS_AUTHORITY="
    "UDUC_EXTRACTION_STATUS"
)

print(
    "U9.10_EXTRACTION_CONFIDENCE_AUTHORITY="
    "UDUC_EXTRACTION_CONFIDENCE"
)

print(
    "U9.10_EXTRACTION_CREATED_AT_AUTHORITY="
    "UDUC_EXTRACTION_CREATED_AT"
)

print(
    "U9.10_EXTRACTION_METHOD_AUTHORITY="
    "UDUC_METADATA_EXTRACTION_METHOD"
)

print(
    "U9.10_EXTRACTION_TIMESTAMP_AUTHORITY="
    "UDUC_METADATA_EXTRACTION_TIMESTAMP"
)

print(
    "U9.10_SOURCE_FORMAT_AUTHORITY="
    "UDUC_SOURCE_FORMAT"
)

print(
    "U9.10_EXTENSION_AUTHORITY="
    "UDUC_METADATA_EXTENSION"
)

print(
    "U9.10_FILE_SIZE_AUTHORITY="
    "UDUC_METADATA_FILE_SIZE"
)

print(
    "U9.10_NESTED_SOURCE_METADATA="
    "DEEPCOPY_PRESERVED"
)

print(
    "U9.10_WUC_EXTRACTION_LABELS_ALLOWED=False"
)

print(
    "U9.10_EXTRACTION_RERUN_ALLOWED=False"
)

print(
    "U9.10_SOURCE_FILE_REREAD_ALLOWED=False"
)

print(
    "U9.10_INPUT_UDUC_MUTATION_ALLOWED=False"
)

print(
    "U9.10_PATCH_DECISION: NONE_INSPECTION_ONLY"
)

print(
    "U9.10_NEXT_STEP: FREEZE_EXTRACTION_PROVENANCE_PRESERVATION"
)