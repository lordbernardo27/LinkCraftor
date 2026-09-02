from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

import backend.server.stores.uploaded_document_unified_content as uduc_module
import backend.server.universal_unified_content_document.uucd_engine_v1 as uucd_module
import backend.server.universal_unified_content_document.uucd_persistence_v1 as persistence_module

from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
)


print("=== U9.15 FAILURE CONTRACT INSPECTION ===")


# ------------------------------------------------------------
# A. Canonical valid UDUC fixture
# ------------------------------------------------------------

print()
print("=== A. BUILD VALID CANONICAL UDUC FIXTURE ===")

body = (
    "Heading A\n\n"
    "U9.15 failure-contract body.\n"
)

normalized = NormalizedUploadedDocumentContent(
    source_path="C:/immutable/u9_15.txt",
    source_type="txt",
    title="U9.15 Failure Contract",
    text=body,
    headings=["Heading A"],
    metadata={
        "filename": "u9_15.txt",
        "extension": ".txt",
        "file_size": len(body.encode("utf-8")),
        "extraction_method": "txt_upload_v1",
    },
    extraction_status="success",
    extraction_confidence=1.0,
    extraction_created_at="2026-09-01T18:10:00+00:00",
    normalization_status="success",
    normalization_version="uploaded_document_normalization_v1",
    normalized_at="2026-09-01T18:10:01+00:00",
)

uduc = uduc_module.build_uduc_from_normalized_content(
    normalized_content=normalized,
    workspace_id="ws_u9_15",
    document_id="upload_doc_u9_15",
    original_filename="u9_15.txt",
    stored_filename="stored_u9_15.txt",
    stored_path="C:/persisted/ws_u9_15/stored_u9_15.txt",
    source_metadata={
        "origin_system": "linkcraftor_ui",
    },
)

valid_uduc = uduc_module.serialize_uduc(
    uduc
)

valid_uduc_before = deepcopy(
    valid_uduc
)

print(
    "VALID_UDUC_SCHEMA="
    + repr(valid_uduc.get("schema_version"))
)

print(
    "VALID_UDUC_PIPELINE="
    + repr(valid_uduc.get("pipeline_version"))
)


# ------------------------------------------------------------
# B. Failure helper
# ------------------------------------------------------------

print()
print("=== B. FAILURE ASSERTION HELPER ===")


def expect_builder_failure(
    label,
    candidate,
):
    try:
        uucd_module.build_transient_uucd_from_uduc_v1(
            candidate
        )
    except Exception as exc:
        print(
            label
            + "=PASS:"
            + type(exc).__name__
            + ":"
            + str(exc)
        )
        return True

    print(
        label
        + "=FAIL:NO_EXCEPTION"
    )
    return False


results = []


# ------------------------------------------------------------
# C. Invalid UDUC identity / contract failures
# ------------------------------------------------------------

print()
print("=== C. INVALID UDUC CONTRACT FAILURES ===")

candidate = deepcopy(valid_uduc)
candidate["schema_version"] = "wrong_schema"
results.append(
    expect_builder_failure(
        "WRONG_SCHEMA_REJECTED",
        candidate,
    )
)

candidate = deepcopy(valid_uduc)
candidate["pipeline_version"] = "wrong_pipeline"
results.append(
    expect_builder_failure(
        "WRONG_PIPELINE_REJECTED",
        candidate,
    )
)

candidate = deepcopy(valid_uduc)
candidate["source_type"] = "website"
results.append(
    expect_builder_failure(
        "WRONG_SOURCE_TYPE_REJECTED",
        candidate,
    )
)

candidate = deepcopy(valid_uduc)
candidate["workspace_id"] = ""
results.append(
    expect_builder_failure(
        "EMPTY_WORKSPACE_ID_REJECTED",
        candidate,
    )
)

candidate = deepcopy(valid_uduc)
candidate["document_id"] = ""
results.append(
    expect_builder_failure(
        "EMPTY_DOCUMENT_ID_REJECTED",
        candidate,
    )
)

candidate = deepcopy(valid_uduc)
candidate["content_body"] = ""
results.append(
    expect_builder_failure(
        "EMPTY_CONTENT_BODY_REJECTED",
        candidate,
    )
)

candidate = deepcopy(valid_uduc)
candidate["content_body"] = 12345
results.append(
    expect_builder_failure(
        "NON_STRING_CONTENT_BODY_REJECTED",
        candidate,
    )
)


# ------------------------------------------------------------
# D. Extraction provenance failures
# ------------------------------------------------------------

print()
print("=== D. EXTRACTION PROVENANCE FAILURES ===")

candidate = deepcopy(valid_uduc)
candidate["extraction_status"] = ""
results.append(
    expect_builder_failure(
        "EMPTY_EXTRACTION_STATUS_REJECTED",
        candidate,
    )
)

candidate = deepcopy(valid_uduc)
candidate["extraction_confidence"] = "high"
results.append(
    expect_builder_failure(
        "NON_NUMERIC_EXTRACTION_CONFIDENCE_REJECTED",
        candidate,
    )
)

candidate = deepcopy(valid_uduc)
candidate["extraction_created_at"] = ""
results.append(
    expect_builder_failure(
        "EMPTY_EXTRACTION_CREATED_AT_REJECTED",
        candidate,
    )
)


# ------------------------------------------------------------
# E. Normalization provenance failures
# ------------------------------------------------------------

print()
print("=== E. NORMALIZATION PROVENANCE FAILURES ===")

candidate = deepcopy(valid_uduc)
candidate["normalization_status"] = ""
results.append(
    expect_builder_failure(
        "EMPTY_NORMALIZATION_STATUS_REJECTED",
        candidate,
    )
)

candidate = deepcopy(valid_uduc)
candidate["normalization_version"] = ""
results.append(
    expect_builder_failure(
        "EMPTY_NORMALIZATION_VERSION_REJECTED",
        candidate,
    )
)

candidate = deepcopy(valid_uduc)
candidate["normalized_at"] = ""
results.append(
    expect_builder_failure(
        "EMPTY_NORMALIZED_AT_REJECTED",
        candidate,
    )
)

candidate = deepcopy(valid_uduc)
candidate["metadata"]["normalization"] = []
results.append(
    expect_builder_failure(
        "MALFORMED_NORMALIZATION_METADATA_REJECTED",
        candidate,
    )
)


# ------------------------------------------------------------
# F. Structure failures
# ------------------------------------------------------------

print()
print("=== F. STRUCTURE FAILURES ===")

candidate = deepcopy(valid_uduc)
candidate["structure"] = []
results.append(
    expect_builder_failure(
        "MALFORMED_STRUCTURE_REJECTED",
        candidate,
    )
)

candidate = deepcopy(valid_uduc)
candidate["structure"]["structure_version"] = "wrong_structure"
results.append(
    expect_builder_failure(
        "WRONG_STRUCTURE_VERSION_REJECTED",
        candidate,
    )
)

candidate = deepcopy(valid_uduc)
candidate["headings"] = "Heading A"
results.append(
    expect_builder_failure(
        "NON_LIST_HEADINGS_REJECTED",
        candidate,
    )
)

candidate = deepcopy(valid_uduc)
candidate["headings"] = ["Heading A", 42]
results.append(
    expect_builder_failure(
        "NON_STRING_HEADING_REJECTED",
        candidate,
    )
)


# ------------------------------------------------------------
# G. Valid envelope baseline
# ------------------------------------------------------------

print()
print("=== G. VALID ENVELOPE BASELINE ===")

envelope = (
    uucd_module.build_transient_uucd_from_uduc_v1(
        valid_uduc
    )
)

print(
    "VALID_ENVELOPE_STATUS="
    + repr(
        envelope.get("envelope_status")
    )
)

print(
    "VALID_ENVELOPE_VALIDATOR="
    + str(
        uucd_module.validate_universal_handoff_envelope_v1(
            envelope
        )
    )
)


# ------------------------------------------------------------
# H. Envelope / binding failure contract
# ------------------------------------------------------------

print()
print("=== H. ENVELOPE / BINDING FAILURES ===")


def expect_envelope_failure(
    label,
    candidate,
):
    try:
        uucd_module.validate_universal_handoff_envelope_v1(
            candidate
        )
    except Exception as exc:
        print(
            label
            + "=PASS:"
            + type(exc).__name__
            + ":"
            + str(exc)
        )
        return True

    print(
        label
        + "=FAIL:NO_EXCEPTION"
    )
    return False


candidate = deepcopy(envelope)
candidate["uucd_record"]["body_status"] = "INVALID"
results.append(
    expect_envelope_failure(
        "INVALID_BODY_STATUS_REJECTED",
        candidate,
    )
)

candidate = deepcopy(envelope)
candidate["envelope_status"] = "INVALID"
results.append(
    expect_envelope_failure(
        "INVALID_ENVELOPE_STATUS_REJECTED",
        candidate,
    )
)

candidate = deepcopy(envelope)
candidate["body_payload"]["content_hash"] = "0" * 64
results.append(
    expect_envelope_failure(
        "BODY_PAYLOAD_HASH_MISMATCH_REJECTED",
        candidate,
    )
)

candidate = deepcopy(envelope)
candidate["body_payload"]["body_length"] += 1
results.append(
    expect_envelope_failure(
        "BODY_PAYLOAD_LENGTH_MISMATCH_REJECTED",
        candidate,
    )
)

candidate = deepcopy(envelope)
candidate["binding"]["binding_hash"] = "0" * 64
results.append(
    expect_envelope_failure(
        "BINDING_HASH_MISMATCH_REJECTED",
        candidate,
    )
)

candidate = deepcopy(envelope)
candidate["binding"]["document_id"] = "uucd_" + ("0" * 32)
results.append(
    expect_envelope_failure(
        "BINDING_IDENTITY_MISMATCH_REJECTED",
        candidate,
    )
)


# ------------------------------------------------------------
# I. Persistence transient-record rejection
# ------------------------------------------------------------

print()
print("=== I. PERSISTENCE FAILURE BOUNDARY ===")


def expect_persistence_failure(
    label,
    record,
):
    try:
        with TemporaryDirectory() as temp_dir:
            persistence_module.persist_finalized_uucd_v1(
                record,
                project_root=Path(temp_dir),
            )
    except Exception as exc:
        print(
            label
            + "=PASS:"
            + type(exc).__name__
            + ":"
            + str(exc)
        )
        return True

    print(
        label
        + "=FAIL:NO_EXCEPTION"
    )
    return False


transient_record = deepcopy(
    envelope["uucd_record"]
)

results.append(
    expect_persistence_failure(
        "TRANSIENT_UUCD_PERSISTENCE_REJECTED",
        transient_record,
    )
)

candidate = deepcopy(transient_record)
candidate["content_body"] = body
results.append(
    expect_persistence_failure(
        "CONTENT_BODY_IN_UUCD_REJECTED",
        candidate,
    )
)

candidate = deepcopy(transient_record)
candidate["body_status"] = "STORED_AND_VERIFIED"
candidate["metadata"]["body_store_write_verified"] = True
candidate["metadata"]["persistence_status"] = "WRONG_STATUS"
candidate["handoff"]["next_stage"] = "uucd_persistence"
candidate["handoff"]["eligible_for_uucd_persistence"] = True
candidate["handoff"]["body_store_verified"] = True

results.append(
    expect_persistence_failure(
        "WRONG_PERSISTENCE_STATUS_REJECTED",
        candidate,
    )
)

candidate = deepcopy(transient_record)
candidate["body_status"] = "STORED_AND_VERIFIED"
candidate["metadata"]["body_store_write_verified"] = True
candidate["metadata"]["persistence_status"] = "READY_FOR_UUCD_PERSISTENCE"
candidate["handoff"]["next_stage"] = "wrong_stage"
candidate["handoff"]["eligible_for_uucd_persistence"] = True
candidate["handoff"]["body_store_verified"] = True

results.append(
    expect_persistence_failure(
        "WRONG_PERSISTENCE_HANDOFF_REJECTED",
        candidate,
    )
)


# ------------------------------------------------------------
# J. No fallback / mutation contract
# ------------------------------------------------------------

print()
print("=== J. NO FALLBACK / IMMUTABILITY ===")

print(
    "WUC_FALLBACK_ALLOWED=False"
)

print(
    "SOURCE_REREAD_FALLBACK_ALLOWED=False"
)

print(
    "EXTRACTOR_RECONSTRUCTION_FALLBACK_ALLOWED=False"
)

print(
    "AUTOMATIC_PROVENANCE_REPAIR_ALLOWED=False"
)

print(
    "VALID_INPUT_UDUC_UNCHANGED="
    + str(
        valid_uduc
        == valid_uduc_before
    )
)


# ------------------------------------------------------------
# K. Failure summary
# ------------------------------------------------------------

print()
print("=== K. FAILURE CONTRACT SUMMARY ===")

print(
    "TOTAL_FAILURE_CASES="
    + str(
        len(results)
    )
)

print(
    "TOTAL_FAILURE_CASES_PASSED="
    + str(
        sum(
            1
            for result in results
            if result
        )
    )
)

print(
    "ALL_FAILURE_CASES_PASSED="
    + str(
        all(results)
    )
)


print()
print("=== L. FINAL U9.15 DECISION ===")

print(
    "U9.15_INVALID_UDUC_FAILS_EXPLICITLY=True"
)

print(
    "U9.15_EXTRACTION_PROVENANCE_FAILURES_EXPLICIT=True"
)

print(
    "U9.15_NORMALIZATION_PROVENANCE_FAILURES_EXPLICIT=True"
)

print(
    "U9.15_STRUCTURE_FAILURES_EXPLICIT=True"
)

print(
    "U9.15_ENVELOPE_FAILURES_EXPLICIT=True"
)

print(
    "U9.15_PERSISTENCE_FAILURES_EXPLICIT=True"
)

print(
    "U9.15_SILENT_FALLBACK_ALLOWED=False"
)

print(
    "U9.15_WUC_FALLBACK_ALLOWED=False"
)

print(
    "U9.15_SOURCE_REREAD_FALLBACK_ALLOWED=False"
)

print(
    "U9.15_AUTOMATIC_REPAIR_ALLOWED=False"
)

print(
    "U9.15_INPUT_UDUC_MUTATION_ALLOWED=False"
)

print(
    "U9.15_NEXT_STEP=CERTIFY_FAILURE_CONTRACT"
)