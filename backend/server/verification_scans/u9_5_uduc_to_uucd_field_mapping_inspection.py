from pathlib import Path
import ast
import inspect

import backend.server.universal_unified_content_document.uucd_engine_v1 as uucd
import backend.server.stores.uploaded_document_unified_content as uduc


print("=== U9.5 UDUC -> UUCD FIELD MAPPING INSPECTION ===")


engine_path = Path(
    "backend/server/"
    "universal_unified_content_document/"
    "uucd_engine_v1.py"
)

uduc_path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

engine_source = engine_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

uduc_source = uduc_path.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

tree = ast.parse(
    engine_source
)


# ------------------------------------------------------------
# A. Optional-string behavior
# ------------------------------------------------------------

print()
print("=== A. OPTIONAL STRING BEHAVIOR ===")

optional_string = getattr(
    uucd,
    "_optional_string",
)

for value in [
    None,
    "",
    "   ",
    "example",
]:
    print(
        f"OPTIONAL_STRING_{value!r}="
        f"{optional_string(value)!r}"
    )


# ------------------------------------------------------------
# B. Existing source_name precedence
# ------------------------------------------------------------

print()
print("=== B. EXISTING SOURCE_NAME PRECEDENCE ===")

builder = next(
    node
    for node in tree.body
    if isinstance(
        node,
        ast.FunctionDef,
    )
    and node.name
    == "build_transient_uucd_from_wuc_v1"
)

builder_source = (
    ast.get_source_segment(
        engine_source,
        builder,
    )
    or ""
)

lines = builder_source.splitlines()

for index, line in enumerate(
    lines,
    start=1,
):
    if (
        "source_name"
        in line
        or "canonical_url"
        in line
        or "original_filename"
        in line
        or '"filename"'
        in line
        or "source_record_id"
        in line
    ):
        start = max(
            1,
            index - 3,
        )

        end = min(
            len(lines),
            index + 5,
        )

        print()
        print(
            f"--- BUILDER LINES {start}-{end} ---"
        )

        for pos in range(
            start,
            end + 1,
        ):
            print(
                f"{pos}: {lines[pos - 1]}"
            )


# ------------------------------------------------------------
# C. canonical_url validation semantics
# ------------------------------------------------------------

print()
print("=== C. CANONICAL_URL VALIDATION SEMANTICS ===")

validator = inspect.getsource(
    uucd.validate_universal_handoff_envelope_v1
)

for marker in [
    "canonical_url",
    "source_name",
    "source_identity",
]:
    print(
        f"ENVELOPE_VALIDATOR_REFERENCES_{marker.upper()}="
        f"{marker in validator}"
    )


wuc_validator = inspect.getsource(
    uucd._validate_wuc_contract
)

for marker in [
    'wuc_package.get(\n            "canonical_url"',
    'field_name="canonical_url"',
    "_optional_string",
]:
    print(
        f"WUC_VALIDATOR_MARKER_{marker!r}="
        f"{marker in wuc_validator}"
    )


# ------------------------------------------------------------
# D. Current UDUC identity fields
# ------------------------------------------------------------

print()
print("=== D. CANONICAL UDUC IDENTITY FIELD EVIDENCE ===")

for marker in [
    "original_filename",
    "stored_filename",
    "stored_path",
    "document_id",
    "source_type",
    "source_format",
]:
    print(
        f"UDUC_FIELD_{marker.upper()}="
        f"{marker in uduc_source}"
    )


# ------------------------------------------------------------
# E. UDUC metadata source_metadata behavior
# ------------------------------------------------------------

print()
print("=== E. UDUC SOURCE_METADATA BEHAVIOR ===")

for marker in [
    "source_metadata",
    "source_snapshot_reference",
    "version_asset_reference",
]:
    print(
        f"UDUC_METADATA_MARKER_{marker.upper()}="
        f"{marker in uduc_source}"
    )


# ------------------------------------------------------------
# F. Shared deterministic identity helpers
# ------------------------------------------------------------

print()
print("=== F. UPLOADED DOCUMENT DETERMINISTIC IDENTITY SAMPLE ===")

workspace_id = "ws_u9_5"
source_type = "uploaded_document"
source_record_id = "upload_doc_001"
title = "Uploaded Contract Example"

document_id = uucd._stable_document_id(
    workspace_id=workspace_id,
    source_type=source_type,
    source_record_id=source_record_id,
)

content_ref = uucd._stable_content_ref(
    workspace_id=workspace_id,
    document_id=document_id,
)

body_ref = uucd._stable_body_ref(
    workspace_id=workspace_id,
    document_id=document_id,
    title=title,
)

print(
    "UPLOADED_DOCUMENT_CANONICAL_DOCUMENT_ID="
    + repr(document_id)
)

print(
    "UPLOADED_DOCUMENT_CONTENT_REF="
    + repr(content_ref)
)

print(
    "UPLOADED_DOCUMENT_BODY_REF="
    + repr(body_ref)
)


# ------------------------------------------------------------
# G. Canonical source_name candidates
# ------------------------------------------------------------

print()
print("=== G. UPLOADED DOCUMENT SOURCE_NAME CANDIDATES ===")

fixture = {
    "original_filename":
        "original_article.docx",

    "stored_filename":
        "8ac3_upload.docx",

    "document_id":
        "upload_doc_001",
}

source_name = (
    uucd._optional_string(
        fixture.get(
            "original_filename"
        )
    )
    or uucd._optional_string(
        fixture.get(
            "stored_filename"
        )
    )
    or fixture[
        "document_id"
    ]
)

print(
    "PROPOSED_SOURCE_NAME="
    + repr(source_name)
)

print(
    "SOURCE_NAME_PRIORITY="
    "original_filename>stored_filename>document_id"
)


# ------------------------------------------------------------
# H. Proposed canonical_url behavior
# ------------------------------------------------------------

print()
print("=== H. UPLOADED DOCUMENT CANONICAL_URL CANDIDATE ===")

uploaded_document_canonical_url = None

print(
    "UPLOADED_DOCUMENT_CANONICAL_URL="
    + repr(
        uploaded_document_canonical_url
    )
)

print(
    "CANONICAL_URL_IN_RECORD_REQUIRED_AS_FIELD="
    + str(
        "canonical_url"
        in uucd.REQUIRED_UUCD_RECORD_FIELDS
    )
)

print(
    "CANONICAL_URL_REQUIRED_NONEMPTY_BY_ENVELOPE_VALIDATOR="
    + str(
        'field_name="canonical_url"'
        in validator
    )
)


# ------------------------------------------------------------
# I. Proposed Uploaded Document metadata keys
# ------------------------------------------------------------

print()
print("=== I. PROPOSED UPLOADED DOCUMENT METADATA CONTRACT ===")

metadata_keys = [
    "uduc_schema_version",
    "uduc_pipeline_version",
    "uduc_created_at",
    "complete_content_preserved",
    "content_body_in_uucd_record",
    "body_transport",
    "content_reduction_performed",
    "summarization_performed",
    "truncation_performed",
    "word_count_limit_applied",
    "semantic_processing_performed",
    "persistence_status",
]

for key in metadata_keys:
    print(
        f"UPLOADED_DOCUMENT_METADATA_FIELD={key}"
    )


# ------------------------------------------------------------
# J. Proposed Uploaded Document provenance keys
# ------------------------------------------------------------

print()
print("=== J. PROPOSED UPLOADED DOCUMENT PROVENANCE CONTRACT ===")

provenance_keys = [
    "input_stage",
    "input_content_id",
    "source_record_id",
    "full_body_received_from_uduc",
    "full_body_moved_to_body_payload",
    "body_hash_verified",
    "body_length_verified",
]

for key in provenance_keys:
    print(
        f"UPLOADED_DOCUMENT_PROVENANCE_FIELD={key}"
    )


# ------------------------------------------------------------
# K. Field mapping matrix
# ------------------------------------------------------------

print()
print("=== K. UDUC -> UUCD FIELD MAPPING MATRIX ===")

mapping = [
    ("workspace_id", "workspace_id", "DIRECT"),
    ("document_id", "source_id", "DIRECT"),
    ("document_id", "source_identity.source_record_id", "DIRECT"),
    ("document_id", "provenance.input_content_id", "DIRECT"),
    ("document_id", "provenance.source_record_id", "DIRECT"),
    ("source_type", "source_type", "DIRECT"),
    ("source_format", "source_format", "DIRECT"),
    ("original_filename", "source_name", "PRIMARY"),
    ("stored_filename", "source_name", "SECONDARY"),
    ("document_id", "source_name", "FINAL_FALLBACK"),
    ("original_filename", "source_identity.original_filename", "DIRECT"),
    ("stored_filename", "source_identity.stored_filename", "DIRECT"),
    ("stored_path", "source_identity.stored_path", "DIRECT"),
    ("title", "title", "DIRECT"),
    ("h1", "h1", "DIRECT"),
    ("headings", "headings", "DIRECT"),
    ("structure", "structure", "DEEPCOPY"),
    ("content_body", "body_payload.content_body", "DIRECT_FULL_BODY"),
    ("content_body", "content_hash", "DERIVED"),
    ("content_body", "body_length", "DERIVED"),
    ("content_body", "body_word_count", "DERIVED"),
]

for source, target, rule in mapping:
    print(
        f"MAP={source} -> {target} [{rule}]"
    )


# ------------------------------------------------------------
# L. U9.5 decision evidence
# ------------------------------------------------------------

print()
print("=== L. U9.5 DECISION EVIDENCE ===")

print(
    "U9.5_SOURCE_TYPE="
    "'uploaded_document'"
)

print(
    "U9.5_SOURCE_RECORD_ID_AUTHORITY="
    "UDUC_DOCUMENT_ID"
)

print(
    "U9.5_CANONICAL_DOCUMENT_ID="
    "DERIVE_WITH_SHARED_STABLE_DOCUMENT_ID"
)

print(
    "U9.5_SOURCE_NAME_PRIORITY="
    "ORIGINAL_FILENAME>STORED_FILENAME>UDUC_DOCUMENT_ID"
)

print(
    "U9.5_CANONICAL_URL_CANDIDATE=None"
)

print(
    "U9.5_CONTENT_BODY_RECORD_LOCATION=PROHIBITED"
)

print(
    "U9.5_CONTENT_BODY_PAYLOAD_LOCATION=BODY_PAYLOAD"
)

print(
    "U9.5_WUC_PROVENANCE_SYNTHESIS=PROHIBITED"
)

print(
    "U9.5_PATCH_DECISION: NONE_INSPECTION_ONLY"
)

print(
    "U9.5_NEXT_STEP: FREEZE_EXACT_FIELD_MAPPING"
)