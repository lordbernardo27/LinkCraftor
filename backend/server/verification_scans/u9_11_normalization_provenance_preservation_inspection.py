from copy import deepcopy

import backend.server.stores.uploaded_document_unified_content as uduc_module

from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
)


print("=== U9.11 NORMALIZATION PROVENANCE PRESERVATION INSPECTION ===")


# ------------------------------------------------------------
# A. Build canonical UDUC fixture
# ------------------------------------------------------------

print()
print("=== A. CANONICAL UDUC NORMALIZATION PROVENANCE FIXTURE ===")

body = (
    "Heading A\n\n"
    "Normalization provenance paragraph.\n"
)

normalized = NormalizedUploadedDocumentContent(
    source_path="C:/immutable/u9_11.md",
    source_type="md",
    title="U9.11 Normalization Provenance",
    text=body,
    headings=[
        "Heading A",
    ],
    metadata={
        "filename":
            "source_u9_11.md",

        "extension":
            ".md",

        "file_size":
            76543,

        "extraction_method":
            "markdown_upload_v1",

        "normalization": {
            "input_encoding":
                "utf-8",

            "content_preserved":
                True,

            "whitespace_rewrite":
                False,
        },
    },
    extraction_status="success",
    extraction_confidence=0.991,
    extraction_created_at="2026-09-01T17:46:00+00:00",
    normalization_status="success",
    normalization_version="uploaded_document_normalization_v1",
    normalized_at="2026-09-01T17:46:01+00:00",
)

uduc = uduc_module.build_uduc_from_normalized_content(
    normalized_content=normalized,
    workspace_id="ws_u9_11",
    document_id="upload_doc_u9_11",
    original_filename="source_u9_11.md",
    stored_filename="stored_u9_11.md",
    stored_path="C:/persisted/ws_u9_11/stored_u9_11.md",
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

metadata_normalization = metadata.get(
    "normalization",
    {},
)

boundary = metadata.get(
    "boundary",
    {},
)


# ------------------------------------------------------------
# B. Top-level normalization provenance
# ------------------------------------------------------------

print()
print("=== B. TOP-LEVEL NORMALIZATION PROVENANCE ===")

for key in [
    "normalization_status",
    "normalization_version",
    "normalized_at",
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
# C. Metadata normalization contract
# ------------------------------------------------------------

print()
print("=== C. UDUC METADATA.NORMALIZATION ===")

print(
    "METADATA_NORMALIZATION_TYPE="
    + type(
        metadata_normalization
    ).__name__
)

print(
    "METADATA_NORMALIZATION="
    + repr(
        metadata_normalization
    )
)


# ------------------------------------------------------------
# D. Boundary evidence
# ------------------------------------------------------------

print()
print("=== D. NORMALIZATION BOUNDARY EVIDENCE ===")

for key in [
    "performs_extraction",
    "performs_normalization",
    "performs_cleaning",
    "performs_phrase_extraction",
    "performs_semantic_analysis",
    "creates_uucd",
]:
    print(
        f"BOUNDARY_{key.upper()}="
        + repr(
            boundary.get(
                key
            )
        )
    )


# ------------------------------------------------------------
# E. Exact-value preservation
# ------------------------------------------------------------

print()
print("=== E. EXACT NORMALIZATION VALUE PRESERVATION ===")

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

    "details":
        deepcopy(
            metadata_normalization
        ),

    "boundary":
        deepcopy(
            boundary
        ),
}

print(
    "NORMALIZATION_PROVENANCE="
    + repr(
        normalization_provenance
    )
)

print(
    "NORMALIZATION_STATUS_EXACT="
    + str(
        normalization_provenance[
            "status"
        ]
        == "success"
    )
)

print(
    "NORMALIZATION_VERSION_EXACT="
    + str(
        normalization_provenance[
            "version"
        ]
        == "uploaded_document_normalization_v1"
    )
)

print(
    "NORMALIZED_AT_EXACT="
    + str(
        normalization_provenance[
            "normalized_at"
        ]
        == "2026-09-01T17:46:01+00:00"
    )
)


# ------------------------------------------------------------
# F. Extraction / normalization separation
# ------------------------------------------------------------

print()
print("=== F. EXTRACTION / NORMALIZATION SEPARATION ===")

print(
    "EXTRACTION_STATUS="
    + repr(
        serialized.get(
            "extraction_status"
        )
    )
)

print(
    "NORMALIZATION_STATUS="
    + repr(
        serialized.get(
            "normalization_status"
        )
    )
)

print(
    "EXTRACTION_CREATED_AT="
    + repr(
        serialized.get(
            "extraction_created_at"
        )
    )
)

print(
    "NORMALIZED_AT="
    + repr(
        serialized.get(
            "normalized_at"
        )
    )
)

print(
    "EXTRACTION_AND_NORMALIZATION_TIMESTAMPS_DISTINCT_FIELDS=True"
)


# ------------------------------------------------------------
# G. Proposed UUCD normalization metadata
# ------------------------------------------------------------

print()
print("=== G. PROPOSED UUCD NORMALIZATION METADATA CONTRACT ===")

uucd_normalization_metadata = {
    "normalization": {
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

        "details":
            deepcopy(
                metadata_normalization
            ),

        "boundary":
            deepcopy(
                boundary
            ),
    },
}

print(
    "UUCD_NORMALIZATION_METADATA="
    + repr(
        uucd_normalization_metadata
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

metadata_normalization_before = deepcopy(
    metadata_normalization
)

boundary_before = deepcopy(
    boundary
)

uucd_normalization_metadata[
    "normalization"
][
    "status"
] = "MUTATED"

uucd_normalization_metadata[
    "normalization"
][
    "details"
][
    "content_preserved"
] = False

uucd_normalization_metadata[
    "normalization"
][
    "boundary"
][
    "performs_cleaning"
] = True

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
    "UDUC_NORMALIZATION_DETAILS_UNCHANGED="
    + str(
        metadata_normalization
        == metadata_normalization_before
    )
)

print(
    "UDUC_BOUNDARY_UNCHANGED="
    + str(
        boundary
        == boundary_before
    )
)


# ------------------------------------------------------------
# I. Normalization execution exclusions
# ------------------------------------------------------------

print()
print("=== I. NORMALIZATION EXECUTION EXCLUSIONS ===")

print(
    "NORMALIZATION_RERUN_ALLOWED=False"
)

print(
    "NORMALIZER_INVOCATION_ALLOWED=False"
)

print(
    "CONTENT_CLEANING_ALLOWED=False"
)

print(
    "WHITESPACE_NORMALIZATION_ALLOWED=False"
)

print(
    "STRUCTURAL_NORMALIZATION_ALLOWED=False"
)

print(
    "NORMALIZATION_VERSION_SYNTHESIS_ALLOWED=False"
)

print(
    "NORMALIZATION_TIMESTAMP_REPLACEMENT_ALLOWED=False"
)


# ------------------------------------------------------------
# J. WUC naming exclusion
# ------------------------------------------------------------

print()
print("=== J. SOURCE TERMINOLOGY EXCLUSION ===")

for key in [
    "wuc_normalization",
    "wuc_normalization_version",
    "website_normalization",
]:
    print(
        f"PROHIBITED_WUC_NORMALIZATION_KEY={key}"
    )

print(
    "U9.11_WUC_NORMALIZATION_LABELS_ALLOWED=False"
)


# ------------------------------------------------------------
# K. Final U9.11 decision
# ------------------------------------------------------------

print()
print("=== K. U9.11 NORMALIZATION PROVENANCE DECISION ===")

print(
    "U9.11_NORMALIZATION_STATUS_AUTHORITY="
    "UDUC_NORMALIZATION_STATUS"
)

print(
    "U9.11_NORMALIZATION_VERSION_AUTHORITY="
    "UDUC_NORMALIZATION_VERSION"
)

print(
    "U9.11_NORMALIZED_AT_AUTHORITY="
    "UDUC_NORMALIZED_AT"
)

print(
    "U9.11_NORMALIZATION_DETAILS_AUTHORITY="
    "UDUC_METADATA_NORMALIZATION"
)

print(
    "U9.11_BOUNDARY_AUTHORITY="
    "UDUC_METADATA_BOUNDARY"
)

print(
    "U9.11_NORMALIZATION_METADATA_PRESERVATION="
    "DEEPCOPY"
)

print(
    "U9.11_EXTRACTION_NORMALIZATION_SEPARATION=True"
)

print(
    "U9.11_NORMALIZATION_RERUN_ALLOWED=False"
)

print(
    "U9.11_NORMALIZER_INVOCATION_ALLOWED=False"
)

print(
    "U9.11_CONTENT_CLEANING_ALLOWED=False"
)

print(
    "U9.11_WHITESPACE_NORMALIZATION_ALLOWED=False"
)

print(
    "U9.11_STRUCTURAL_NORMALIZATION_ALLOWED=False"
)

print(
    "U9.11_VERSION_SYNTHESIS_ALLOWED=False"
)

print(
    "U9.11_TIMESTAMP_REPLACEMENT_ALLOWED=False"
)

print(
    "U9.11_INPUT_UDUC_MUTATION_ALLOWED=False"
)

print(
    "U9.11_PATCH_DECISION: NONE_INSPECTION_ONLY"
)

print(
    "U9.11_NEXT_STEP: FREEZE_NORMALIZATION_PROVENANCE_PRESERVATION"
)