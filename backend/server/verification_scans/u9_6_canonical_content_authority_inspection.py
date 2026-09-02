from pathlib import Path
import ast
import copy

import backend.server.stores.uploaded_document_unified_content as uduc_module
import backend.server.universal_unified_content_document.uucd_engine_v1 as uucd_module

from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
)


print("=== U9.6 CANONICAL CONTENT AUTHORITY INSPECTION ===")


uduc_path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

normalizer_path = Path(
    "backend/server/stores/"
    "upload_document_normalizer.py"
)

extractor_path = Path(
    "backend/server/stores/"
    "upload_document_extractor.py"
)

coordinator_path = Path(
    "backend/server/pipelines/"
    "upload_document/coordinator.py"
)

uucd_path = Path(
    "backend/server/"
    "universal_unified_content_document/"
    "uucd_engine_v1.py"
)


uduc_source = uduc_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

normalizer_source = normalizer_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

extractor_source = extractor_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

coordinator_source = coordinator_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

uucd_source = uucd_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)


# ------------------------------------------------------------
# A. Canonical UDUC body authority fixture
# ------------------------------------------------------------

print()
print("=== A. CANONICAL UDUC BODY AUTHORITY ===")

body = (
    "Heading A\n\n"
    "Exact paragraph one.\n\n"
    "Exact paragraph two.\n"
)

normalized = NormalizedUploadedDocumentContent(
    source_path="C:/immutable/u9_6.txt",
    source_type="txt",
    title="U9.6 Content Authority",
    text=body,
    headings=[
        "Heading A",
    ],
    metadata={
        "filename": "u9_6.txt",
        "extension": ".txt",
        "file_size": len(
            body.encode("utf-8")
        ),
        "extraction_method": "txt_upload_v1",
    },
    extraction_status="success",
    extraction_confidence=1.0,
    extraction_created_at="2026-09-01T17:20:00+00:00",
    normalization_status="success",
    normalization_version="uploaded_document_normalization_v1",
    normalized_at="2026-09-01T17:20:01+00:00",
)

uduc = uduc_module.build_uduc_from_normalized_content(
    normalized_content=normalized,
    workspace_id="ws_u9_6",
    document_id="upload_doc_u9_6",
    original_filename="u9_6.txt",
    stored_filename="stored_u9_6.txt",
    stored_path="C:/persisted/ws_u9_6/stored_u9_6.txt",
    source_metadata={},
)

serialized = uduc_module.serialize_uduc(
    uduc
)

uduc_body = serialized.get(
    "content_body"
)

print(
    "UDUC_BODY_TYPE="
    + type(
        uduc_body
    ).__name__
)

print(
    "UDUC_BODY_EXACTLY_EQUALS_NORMALIZED_TEXT="
    + str(
        uduc_body == body
    )
)

print(
    "UDUC_BODY_REPR="
    + repr(
        uduc_body
    )
)


# ------------------------------------------------------------
# B. Body-derived canonical values
# ------------------------------------------------------------

print()
print("=== B. BODY-DERIVED CANONICAL VALUES ===")

content_hash = (
    uucd_module.compute_canonical_content_hash_v1(
        uduc_body
    )
)

body_length = len(
    uduc_body
)

body_word_count = len(
    uduc_body.split()
)

print(
    "CONTENT_HASH="
    + repr(
        content_hash
    )
)

print(
    "BODY_LENGTH="
    + str(
        body_length
    )
)

print(
    "BODY_WORD_COUNT="
    + str(
        body_word_count
    )
)

print(
    "CONTENT_HASH_RECOMPUTE_MATCH="
    + str(
        content_hash
        == uucd_module.compute_canonical_content_hash_v1(
            serialized[
                "content_body"
            ]
        )
    )
)


# ------------------------------------------------------------
# C. Prohibited alternate content authorities
# ------------------------------------------------------------

print()
print("=== C. PROHIBITED ALTERNATE CONTENT AUTHORITY INVENTORY ===")

prohibited_authorities = {
    "SOURCE_FILE_REREAD": [
        "read_text(",
        "read_bytes(",
        "open(",
    ],

    "EXTRACTION_RERUN": [
        "extract_uploaded_document",
        "UploadExtractionResult",
    ],

    "NORMALIZATION_RERUN": [
        "normalize_uploaded_document_v1",
        "NormalizedUploadedDocumentContent(",
    ],

    "WUC_FALLBACK": [
        "build_transient_uucd_from_wuc_v1",
        "website_unified_content",
        "wuc_package",
    ],

    "PREVIEW_FALLBACK": [
        "preview",
        "editor_text",
        "editor_content",
    ],
}

for group, markers in prohibited_authorities.items():
    print()
    print(
        f"GROUP={group}"
    )

    for marker in markers:
        print(
            f"{marker}="
            f"{marker in uduc_source}"
        )


# ------------------------------------------------------------
# D. UDUC boundary metadata
# ------------------------------------------------------------

print()
print("=== D. UDUC BOUNDARY METADATA ===")

structure = serialized.get(
    "structure",
    {}
)

structure_boundary = structure.get(
    "boundary",
    {},
)

metadata = serialized.get(
    "metadata",
    {}
)

metadata_boundary = metadata.get(
    "boundary",
    {},
)

for key, value in structure_boundary.items():
    print(
        f"STRUCTURE_BOUNDARY_{key.upper()}="
        + repr(value)
    )

for key, value in metadata_boundary.items():
    print(
        f"METADATA_BOUNDARY_{key.upper()}="
        + repr(value)
    )


# ------------------------------------------------------------
# E. Exact content-preservation evidence
# ------------------------------------------------------------

print()
print("=== E. CONTENT PRESERVATION EVIDENCE ===")

print(
    "LEADING_CONTENT_PRESERVED="
    + str(
        uduc_body.startswith(
            "Heading A"
        )
    )
)

print(
    "TRAILING_NEWLINE_PRESERVED="
    + str(
        uduc_body.endswith(
            "\n"
        )
    )
)

print(
    "BLANK_LINES_PRESERVED="
    + str(
        "\n\n"
        in uduc_body
    )
)

print(
    "BODY_CHARACTER_COUNT_EXACT="
    + str(
        len(
            uduc_body
        )
        == len(
            body
        )
    )
)


# ------------------------------------------------------------
# F. Canonical body payload simulation
# ------------------------------------------------------------

print()
print("=== F. CANONICAL BODY PAYLOAD SIMULATION ===")

document_id = (
    uucd_module._stable_document_id(
        workspace_id=serialized[
            "workspace_id"
        ],
        source_type="uploaded_document",
        source_record_id=serialized[
            "document_id"
        ],
    )
)

body_ref = (
    uucd_module._stable_body_ref(
        workspace_id=serialized[
            "workspace_id"
        ],
        document_id=document_id,
        title=serialized[
            "title"
        ],
    )
)

body_payload = {
    "payload_schema_version":
        uucd_module.BODY_PAYLOAD_SCHEMA_VERSION,

    "document_id":
        document_id,

    "workspace_id":
        serialized[
            "workspace_id"
        ],

    "source_type":
        "uploaded_document",

    "content_body":
        serialized[
            "content_body"
        ],

    "content_hash":
        content_hash,

    "body_length":
        body_length,

    "body_word_count":
        body_word_count,

    "body_ref":
        body_ref,

    "content_encoding":
        "utf-8",
}

print(
    "BODY_PAYLOAD_BODY_EXACT="
    + str(
        body_payload[
            "content_body"
        ]
        == serialized[
            "content_body"
        ]
    )
)

print(
    "BODY_PAYLOAD_HASH_MATCH="
    + str(
        uucd_module.compute_canonical_content_hash_v1(
            body_payload[
                "content_body"
            ]
        )
        == body_payload[
            "content_hash"
        ]
    )
)

print(
    "BODY_PAYLOAD_LENGTH_MATCH="
    + str(
        len(
            body_payload[
                "content_body"
            ]
        )
        == body_payload[
            "body_length"
        ]
    )
)


# ------------------------------------------------------------
# G. UUCD record must remain bodyless
# ------------------------------------------------------------

print()
print("=== G. BODYLESS UUCD RECORD CONTRACT ===")

print(
    "CONTENT_BODY_REQUIRED_IN_UUCD_RECORD="
    + str(
        "content_body"
        in uucd_module.REQUIRED_UUCD_RECORD_FIELDS
    )
)

print(
    "CONTENT_BODY_REQUIRED_IN_BODY_PAYLOAD="
    + str(
        "content_body"
        in uucd_module.REQUIRED_BODY_PAYLOAD_FIELDS
    )
)


# ------------------------------------------------------------
# H. Downstream execution exclusions
# ------------------------------------------------------------

print()
print("=== H. U9 CONTENT AUTHORITY EXECUTION EXCLUSIONS ===")

for marker in [
    "scorer",
    "semantic",
    "phrase",
    "highlight",
    "active_target_set",
]:
    print(
        f"UDUC_MODULE_REFERENCES_{marker.upper()}="
        f"{marker in uduc_source.lower()}"
    )


# ------------------------------------------------------------
# I. Input mutation check
# ------------------------------------------------------------

print()
print("=== I. INPUT MUTATION CHECK ===")

serialized_before = copy.deepcopy(
    serialized
)

_ = (
    uucd_module.compute_canonical_content_hash_v1(
        serialized[
            "content_body"
        ]
    )
)

_ = len(
    serialized[
        "content_body"
    ]
)

_ = len(
    serialized[
        "content_body"
    ].split()
)

print(
    "UDUC_INPUT_MUTATED_BY_DERIVATION="
    + str(
        serialized
        != serialized_before
    )
)


# ------------------------------------------------------------
# J. Final authority decision
# ------------------------------------------------------------

print()
print("=== J. U9.6 CONTENT AUTHORITY DECISION ===")

print(
    "U9.6_BODY_AUTHORITY="
    "UDUC_CONTENT_BODY"
)

print(
    "U9.6_SOURCE_REREAD_ALLOWED=False"
)

print(
    "U9.6_EXTRACTION_FALLBACK_ALLOWED=False"
)

print(
    "U9.6_NORMALIZATION_FALLBACK_ALLOWED=False"
)

print(
    "U9.6_WUC_FALLBACK_ALLOWED=False"
)

print(
    "U9.6_PREVIEW_FALLBACK_ALLOWED=False"
)

print(
    "U9.6_BODY_REWRITING_ALLOWED=False"
)

print(
    "U9.6_CONTENT_HASH_SOURCE="
    "UDUC_CONTENT_BODY"
)

print(
    "U9.6_BODY_LENGTH_SOURCE="
    "UDUC_CONTENT_BODY"
)

print(
    "U9.6_BODY_WORD_COUNT_SOURCE="
    "UDUC_CONTENT_BODY"
)

print(
    "U9.6_FULL_BODY_DESTINATION="
    "BODY_PAYLOAD"
)

print(
    "U9.6_CONTENT_BODY_IN_UUCD_RECORD=False"
)

print(
    "U9.6_PATCH_DECISION: NONE_INSPECTION_ONLY"
)

print(
    "U9.6_NEXT_STEP: FREEZE_CANONICAL_CONTENT_AUTHORITY"
)