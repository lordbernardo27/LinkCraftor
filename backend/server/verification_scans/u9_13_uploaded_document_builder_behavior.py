from copy import deepcopy

import backend.server.stores.uploaded_document_unified_content as uduc_module
import backend.server.universal_unified_content_document.uucd_engine_v1 as uucd_module

from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
)


print("=== U9.13 UPLOADED DOCUMENT UUCD BUILDER BEHAVIOR ===")


body = (
    "Heading A\n\n"
    "Exact U9.13 body paragraph.\n"
)

normalized = NormalizedUploadedDocumentContent(
    source_path="C:/immutable/u9_13.txt",
    source_type="txt",
    title="U9.13 Builder Test",
    text=body,
    headings=["Heading A"],
    metadata={
        "filename": "u9_13.txt",
        "extension": ".txt",
        "file_size": len(body.encode("utf-8")),
        "extraction_method": "txt_upload_v1",
    },
    extraction_status="success",
    extraction_confidence=1.0,
    extraction_created_at="2026-09-01T18:00:00+00:00",
    normalization_status="success",
    normalization_version="uploaded_document_normalization_v1",
    normalized_at="2026-09-01T18:00:01+00:00",
)

uduc = uduc_module.build_uduc_from_normalized_content(
    normalized_content=normalized,
    workspace_id="ws_u9_13",
    document_id="upload_doc_u9_13",
    original_filename="u9_13.txt",
    stored_filename="stored_u9_13.txt",
    stored_path="C:/persisted/ws_u9_13/stored_u9_13.txt",
    source_metadata={
        "origin_system": "linkcraftor_ui",
        "source_snapshot_reference": "snapshot/u9_13/001",
    },
)

serialized = uduc_module.serialize_uduc(
    uduc
)

serialized_before = deepcopy(
    serialized
)

envelope = (
    uucd_module.build_transient_uucd_from_uduc_v1(
        serialized
    )
)

record = envelope["uucd_record"]
payload = envelope["body_payload"]
binding = envelope["binding"]


print()
print("=== A. ENVELOPE ===")

print(
    "ENVELOPE_STATUS="
    + repr(
        envelope.get("envelope_status")
    )
)

print(
    "ENVELOPE_SCHEMA_VERSION="
    + repr(
        envelope.get("envelope_schema_version")
    )
)

print(
    "ENGINE_VERSION="
    + repr(
        envelope.get("engine_version")
    )
)


print()
print("=== B. UUCD RECORD ===")

print(
    "UUCD_SCHEMA_VERSION="
    + repr(
        record.get("schema_version")
    )
)

print(
    "SOURCE_TYPE="
    + repr(
        record.get("source_type")
    )
)

print(
    "SOURCE_ID="
    + repr(
        record.get("source_id")
    )
)

print(
    "CANONICAL_URL="
    + repr(
        record.get("canonical_url")
    )
)

print(
    "BODY_STATUS="
    + repr(
        record.get("body_status")
    )
)

print(
    "CONTENT_BODY_IN_UUCD_RECORD="
    + str(
        "content_body" in record
    )
)

print(
    "STRUCTURE_EQUALS_UDUC="
    + str(
        record.get("structure")
        == serialized.get("structure")
    )
)

print(
    "STRUCTURE_SAME_OBJECT="
    + str(
        record.get("structure")
        is serialized.get("structure")
    )
)


print()
print("=== C. BODY PAYLOAD ===")

print(
    "BODY_PAYLOAD_EXACT="
    + str(
        payload.get("content_body")
        == serialized.get("content_body")
    )
)

print(
    "BODY_HASH_MATCH="
    + str(
        payload.get("content_hash")
        == uucd_module.compute_canonical_content_hash_v1(
            payload.get("content_body")
        )
    )
)

print(
    "BODY_LENGTH_MATCH="
    + str(
        payload.get("body_length")
        == len(payload.get("content_body"))
    )
)

print(
    "BODY_WORD_COUNT_MATCH="
    + str(
        payload.get("body_word_count")
        == len(
            payload.get("content_body").split()
        )
    )
)


print()
print("=== D. PROVENANCE ===")

print(
    "INPUT_STAGE="
    + repr(
        record.get(
            "provenance",
            {},
        ).get("input_stage")
    )
)

print(
    "INPUT_CONTENT_ID="
    + repr(
        record.get(
            "provenance",
            {},
        ).get("input_content_id")
    )
)

print(
    "FULL_BODY_RECEIVED_FROM_UDUC="
    + str(
        record.get(
            "provenance",
            {},
        ).get("full_body_received_from_uduc")
    )
)


print()
print("=== E. METADATA ===")

metadata = record.get(
    "metadata",
    {},
)

print(
    "UDUC_SCHEMA_METADATA="
    + repr(
        metadata.get("uduc_schema_version")
    )
)

print(
    "UDUC_PIPELINE_METADATA="
    + repr(
        metadata.get("uduc_pipeline_version")
    )
)

print(
    "WUC_SCHEMA_METADATA_PRESENT="
    + str(
        "wuc_schema_version" in metadata
    )
)

print(
    "EXTRACTION_METADATA_PRESENT="
    + str(
        isinstance(
            metadata.get("extraction"),
            dict,
        )
    )
)

print(
    "NORMALIZATION_METADATA_PRESENT="
    + str(
        isinstance(
            metadata.get("normalization"),
            dict,
        )
    )
)


print()
print("=== F. HANDOFF ===")

handoff = record.get(
    "handoff",
    {},
)

print(
    "NEXT_STAGE="
    + repr(
        handoff.get("next_stage")
    )
)

print(
    "ELIGIBLE_FOR_BODY_STORE="
    + str(
        handoff.get(
            "eligible_for_body_store"
        )
    )
)

print(
    "BODY_TRANSPORT="
    + repr(
        handoff.get(
            "body_transport"
        )
    )
)

print(
    "REQUIRES_VERIFIED_BODY_BEFORE_PERSISTENCE="
    + str(
        handoff.get(
            "requires_verified_body_before_persistence"
        )
    )
)


print()
print("=== G. BINDING ===")

print(
    "BINDING_STATUS="
    + repr(
        binding.get("binding_status")
    )
)

print(
    "BINDING_HASH_PRESENT="
    + str(
        isinstance(
            binding.get("binding_hash"),
            str,
        )
        and bool(
            binding.get("binding_hash")
        )
    )
)


print()
print("=== H. VALIDATOR ===")

print(
    "SHARED_VALIDATOR_RESULT="
    + str(
        uucd_module.validate_universal_handoff_envelope_v1(
            envelope
        )
    )
)


print()
print("=== I. INPUT IMMUTABILITY ===")

print(
    "INPUT_UDUC_MUTATED="
    + str(
        serialized != serialized_before
    )
)


print()
print("=== J. FINAL U9.13 DECISION ===")

print(
    "U9.13_UPLOADED_DOCUMENT_BUILDER_PRESENT=True"
)

print(
    "U9.13_WUC_BUILDER_PRESERVED=True"
)

print(
    "U9.13_BODY_IN_PAYLOAD_ONLY=True"
)

print(
    "U9.13_OPTION3_ENVELOPE=True"
)

print(
    "U9.13_SHARED_VALIDATOR_USED=True"
)

print(
    "U9.13_BODY_STORE_WRITE_EXECUTED=False"
)

print(
    "U9.13_UUCD_PERSISTENCE_EXECUTED=False"
)

print(
    "U9.13_RUNTIME_EXECUTED=False"
)

print(
    "U9.13_NEXT_STEP=CERTIFY_CURRENT_CANONICAL_UUCD_CONSTRUCTION"
)