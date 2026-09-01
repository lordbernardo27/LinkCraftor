from pathlib import Path
import ast
import json

import backend.server.stores.uploaded_document_unified_content as uduc_module

from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
)

from backend.server.universal_unified_content_document.uucd_engine_v1 import (
    compute_canonical_content_hash_v1,
)


print("=== U9.3 CANONICAL UDUC INPUT CONTRACT INSPECTION ===")


uduc_path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
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

uucd_source = uucd_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

uduc_tree = ast.parse(
    uduc_source
)


# ------------------------------------------------------------
# A. UDUC version constants
# ------------------------------------------------------------

print()
print("=== A. CANONICAL UDUC VERSION AUTHORITY ===")

print(
    "UDUC_SCHEMA_VERSION="
    + repr(
        uduc_module.UDUC_SCHEMA_VERSION
    )
)

print(
    "UDUC_PIPELINE_VERSION="
    + repr(
        uduc_module.UDUC_PIPELINE_VERSION
    )
)


# ------------------------------------------------------------
# B. Exact UDUC dataclass fields
# ------------------------------------------------------------

print()
print("=== B. EXACT UDUC FIELD CONTRACT ===")

uduc_class = next(
    (
        node
        for node in uduc_tree.body
        if isinstance(
            node,
            ast.ClassDef,
        )
        and node.name
        == "UploadedDocumentUnifiedContent"
    ),
    None,
)

fields = []

if uduc_class is not None:
    for node in uduc_class.body:
        if isinstance(
            node,
            ast.AnnAssign,
        ) and isinstance(
            node.target,
            ast.Name,
        ):
            fields.append(
                node.target.id
            )

print(
    "UDUC_FIELD_COUNT="
    + str(len(fields))
)

for index, field in enumerate(
    fields,
    start=1,
):
    print(
        f"UDUC_FIELD_{index}={field}"
    )


# ------------------------------------------------------------
# C. Canonical UDUC output fixture
# ------------------------------------------------------------

print()
print("=== C. CANONICAL UDUC OUTPUT SAMPLE ===")

normalized = NormalizedUploadedDocumentContent(
    source_path="C:/immutable/u9_3.txt",
    source_type="txt",
    title="U9.3 Title",
    text=(
        "Heading A\n\n"
        "Paragraph one.\n\n"
        "Paragraph two."
    ),
    headings=[
        "Heading A",
    ],
    metadata={
        "filename": "u9_3.txt",
        "extension": ".txt",
        "file_size": 903,
        "extraction_method": "txt_upload_v1",
        "custom": {
            "u9_3": True,
        },
    },
    extraction_status="success",
    extraction_confidence=0.95,
    extraction_created_at="2026-09-01T01:40:00+00:00",
    normalization_status="success",
    normalization_version="uploaded_document_normalization_v1",
    normalized_at="2026-09-01T01:40:01+00:00",
)

uduc = uduc_module.build_uduc_from_normalized_content(
    normalized_content=normalized,
    workspace_id="ws_u9_3",
    document_id="upload_doc_001",
    original_filename="u9_3.txt",
    stored_filename="stored_u9_3.txt",
    stored_path="C:/persisted/ws_u9_3/stored_u9_3.txt",
    source_metadata={
        "source_snapshot_reference":
            "snapshot/u9_3/001",
        "version_asset_reference":
            "version/u9_3/001",
    },
)

serialized = uduc_module.serialize_uduc(
    uduc
)

print(
    json.dumps(
        serialized,
        indent=2,
        ensure_ascii=False,
        sort_keys=False,
    )
)


# ------------------------------------------------------------
# D. Required U9 input fields
# ------------------------------------------------------------

print()
print("=== D. U9 INPUT FIELD CLASSIFICATION ===")

groups = {
    "IDENTITY": [
        "schema_version",
        "pipeline_version",
        "workspace_id",
        "document_id",
        "source_type",
        "source_format",
    ],

    "CONTENT": [
        "title",
        "h1",
        "headings",
        "content_body",
        "structure",
        "metadata",
    ],

    "EXTRACTION_PROVENANCE": [
        "extraction_status",
        "extraction_confidence",
        "extraction_created_at",
    ],

    "NORMALIZATION_PROVENANCE": [
        "normalization_status",
        "normalization_version",
        "normalized_at",
    ],

    "UDUC_PROVENANCE": [
        "created_at",
    ],
}

for group_name, group in groups.items():
    print()
    print(
        f"GROUP={group_name}"
    )

    for field in group:
        print(
            f"{field}_PRESENT="
            f"{field in serialized}"
        )


# ------------------------------------------------------------
# E. Source identity candidates
# ------------------------------------------------------------

print()
print("=== E. SOURCE IDENTITY CANDIDATES ===")

metadata = serialized.get(
    "metadata",
    {},
)

nested_source_metadata = metadata.get(
    "source_metadata",
    {},
)

identity_candidates = {
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

    "source_snapshot_reference":
        nested_source_metadata.get(
            "source_snapshot_reference"
        ),

    "version_asset_reference":
        nested_source_metadata.get(
            "version_asset_reference"
        ),
}

for key, value in identity_candidates.items():
    print(
        f"{key}={value!r}"
    )


# ------------------------------------------------------------
# F. Content derivation candidates
# ------------------------------------------------------------

print()
print("=== F. CONTENT DERIVATION CANDIDATES ===")

content_body = serialized.get(
    "content_body"
)

print(
    "CONTENT_BODY_TYPE="
    + type(content_body).__name__
)

print(
    "CONTENT_BODY_LENGTH="
    + str(
        len(content_body)
        if isinstance(
            content_body,
            str,
        )
        else None
    )
)

print(
    "BODY_WORD_COUNT="
    + str(
        len(
            content_body.split()
        )
        if isinstance(
            content_body,
            str,
        )
        else None
    )
)

print(
    "CANONICAL_CONTENT_HASH="
    + repr(
        compute_canonical_content_hash_v1(
            content_body
        )
    )
)


# ------------------------------------------------------------
# G. Title / body requirement evidence
# ------------------------------------------------------------

print()
print("=== G. TITLE / BODY REQUIREMENT EVIDENCE ===")

for marker in [
    'field_name="title"',
    'field_name="content_body"',
    "must not be empty",
]:
    print(
        f"UUCD_ENGINE_MARKER_{marker}="
        f"{marker in uucd_source}"
    )


# ------------------------------------------------------------
# H. UDUC structural provenance
# ------------------------------------------------------------

print()
print("=== H. UDUC STRUCTURAL PROVENANCE ===")

structure = serialized.get(
    "structure",
    {},
)

print(
    "STRUCTURE_VERSION="
    + repr(
        structure.get(
            "structure_version"
        )
    )
)

print(
    "STRUCTURE_KEYS="
    + repr(
        list(
            structure.keys()
        )
    )
)


# ------------------------------------------------------------
# I. Contract decision evidence
# ------------------------------------------------------------

print()
print("=== I. U9.3 CONTRACT DECISION EVIDENCE ===")

print(
    "UDUC_SCHEMA_MATCH="
    + str(
        serialized.get(
            "schema_version"
        )
        == "uploaded_document_unified_content_v2"
    )
)

print(
    "UDUC_PIPELINE_MATCH="
    + str(
        serialized.get(
            "pipeline_version"
        )
        == "uploaded_document_uduc_pipeline_v2"
    )
)

print(
    "UDUC_SOURCE_TYPE_MATCH="
    + str(
        serialized.get(
            "source_type"
        )
        == "uploaded_document"
    )
)

print(
    "UDUC_WORKSPACE_ID_NONEMPTY="
    + str(
        isinstance(
            serialized.get(
                "workspace_id"
            ),
            str,
        )
        and bool(
            serialized.get(
                "workspace_id"
            )
        )
    )
)

print(
    "UDUC_DOCUMENT_ID_NONEMPTY="
    + str(
        isinstance(
            serialized.get(
                "document_id"
            ),
            str,
        )
        and bool(
            serialized.get(
                "document_id"
            )
        )
    )
)

print(
    "UDUC_TITLE_NONEMPTY="
    + str(
        isinstance(
            serialized.get(
                "title"
            ),
            str,
        )
        and bool(
            serialized.get(
                "title"
            )
        )
    )
)

print(
    "UDUC_CONTENT_BODY_NONEMPTY="
    + str(
        isinstance(
            serialized.get(
                "content_body"
            ),
            str,
        )
        and bool(
            serialized.get(
                "content_body"
            )
        )
    )
)

print(
    "UDUC_STRUCTURE_IS_MAPPING="
    + str(
        isinstance(
            serialized.get(
                "structure"
            ),
            dict,
        )
    )
)

print(
    "UDUC_METADATA_IS_MAPPING="
    + str(
        isinstance(
            serialized.get(
                "metadata"
            ),
            dict,
        )
    )
)

print(
    "SOURCE_RECORD_ID_CANDIDATE="
    + repr(
        serialized.get(
            "document_id"
        )
    )
)

print(
    "U9.3_PATCH_DECISION: NONE_INSPECTION_ONLY"
)

print(
    "U9.3_NEXT_STEP: FREEZE_CANONICAL_UDUC_INPUT_VALIDATION_AND_DERIVATION_RULES"
)