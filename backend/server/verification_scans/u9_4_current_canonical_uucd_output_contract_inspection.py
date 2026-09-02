from pathlib import Path
import copy

import backend.server.universal_unified_content_document.uucd_engine_v1 as uucd


print("=== U9.4 CURRENT CANONICAL UUCD OUTPUT CONTRACT INSPECTION ===")


# ------------------------------------------------------------
# A. Canonical version constants
# ------------------------------------------------------------

print()
print("=== A. CANONICAL VERSION CONSTANTS ===")

for name in [
    "UUCD_SCHEMA_VERSION",
    "UUCD_ENGINE_VERSION",
    "BODY_PAYLOAD_SCHEMA_VERSION",
    "HANDOFF_ENVELOPE_SCHEMA_VERSION",
]:
    print(
        f"{name}="
        + repr(
            getattr(
                uucd,
                name,
                None,
            )
        )
    )


# ------------------------------------------------------------
# B. Canonical required-field sets
# ------------------------------------------------------------

print()
print("=== B. REQUIRED FIELD SETS ===")

for name in [
    "REQUIRED_UUCD_RECORD_FIELDS",
    "REQUIRED_BODY_PAYLOAD_FIELDS",
    "REQUIRED_BINDING_FIELDS",
    "BINDING_FIELD_NAMES",
]:
    value = getattr(
        uucd,
        name,
        None,
    )

    print()
    print(
        f"{name}="
        + repr(value)
    )

    if isinstance(
        value,
        (set, frozenset, tuple, list),
    ):
        print(
            f"{name}_COUNT="
            + str(len(value))
        )

        for item in sorted(
            value
        ):
            print(
                f"{name}_FIELD={item}"
            )


# ------------------------------------------------------------
# C. Build a valid canonical WUC fixture only to observe
#    the existing Option-3 output contract.
# ------------------------------------------------------------

print()
print("=== C. CURRENT OPTION-3 OUTPUT FIXTURE ===")

content_body = (
    "Heading A\n\n"
    "Paragraph one.\n\n"
    "Paragraph two."
)

content_hash = (
    uucd.compute_canonical_content_hash_v1(
        content_body
    )
)

wuc_package = {
    "schema_version":
        "website_unified_content_v1",

    "engine_version":
        "website_unified_content_engine_v1",

    "workspace_id":
        "ws_u9_4",

    "source_type":
        "website",

    "source_format":
        "html",

    "content_id":
        "wuc_u9_4_001",

    "title":
        "U9.4 Contract Title",

    "h1":
        "Heading A",

    "headings": [
        "Heading A",
    ],

    "canonical_url":
        "https://example.com/u9-4",

    "content_body":
        content_body,

    "content_hash":
        content_hash,

    "body_length":
        len(content_body),

    "body_word_count":
        len(
            content_body.split()
        ),

    "source_identity": {
        "source_record_id":
            "source_u9_4_001",

        "canonical_url":
            "https://example.com/u9-4",

        "source_snapshot_reference":
            "snapshot/u9_4/001",

        "version_asset_reference":
            "version/u9_4/001",
    },

    "structure": {
        "structure_version":
            "u9_4_fixture",

        "paragraph_count":
            3,
    },

    "metadata": {
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
    },

    "handoff": {
        "eligible_for_uucd":
            True,

        "full_body_handoff":
            True,

        "body_field":
            "content_body",
    },
}

wuc_before = copy.deepcopy(
    wuc_package
)

envelope = (
    uucd.build_transient_uucd_from_wuc_v1(
        wuc_package
    )
)

print(
    "INPUT_MUTATED="
    + str(
        wuc_package
        != wuc_before
    )
)


# ------------------------------------------------------------
# D. Envelope top-level contract
# ------------------------------------------------------------

print()
print("=== D. ENVELOPE TOP-LEVEL CONTRACT ===")

print(
    "ENVELOPE_TYPE="
    + type(envelope).__name__
)

print(
    "ENVELOPE_FIELD_COUNT="
    + str(
        len(envelope)
    )
)

for key in envelope.keys():
    print(
        f"ENVELOPE_FIELD={key}"
    )

print(
    "ENVELOPE_SCHEMA_VERSION="
    + repr(
        envelope.get(
            "envelope_schema_version"
        )
    )
)

print(
    "ENVELOPE_ENGINE_VERSION="
    + repr(
        envelope.get(
            "engine_version"
        )
    )
)

print(
    "ENVELOPE_STATUS="
    + repr(
        envelope.get(
            "envelope_status"
        )
    )
)


# ------------------------------------------------------------
# E. UUCD record contract
# ------------------------------------------------------------

print()
print("=== E. UUCD RECORD CONTRACT ===")

record = envelope.get(
    "uucd_record",
    {},
)

print(
    "UUCD_RECORD_FIELD_COUNT="
    + str(
        len(record)
    )
)

for key in record.keys():
    print(
        f"UUCD_RECORD_FIELD={key}"
    )

for name in [
    "schema_version",
    "engine_version",
    "document_id",
    "workspace_id",
    "source_id",
    "source_type",
    "source_name",
    "source_format",
    "source_identity",
    "title",
    "h1",
    "headings",
    "canonical_url",
    "structure",
    "content_hash",
    "content_ref",
    "body_ref",
    "body_status",
    "body_length",
    "body_word_count",
    "metadata",
    "lifecycle",
    "versioning",
    "provenance",
    "handoff",
]:
    print(
        f"UUCD_RECORD_{name.upper()}="
        + repr(
            record.get(name)
        )
    )

print(
    "CONTENT_BODY_IN_UUCD_RECORD="
    + str(
        "content_body"
        in record
    )
)


# ------------------------------------------------------------
# F. Body payload contract
# ------------------------------------------------------------

print()
print("=== F. BODY PAYLOAD CONTRACT ===")

body_payload = envelope.get(
    "body_payload",
    {},
)

print(
    "BODY_PAYLOAD_FIELD_COUNT="
    + str(
        len(body_payload)
    )
)

for key in body_payload.keys():
    print(
        f"BODY_PAYLOAD_FIELD={key}"
    )

for name in [
    "payload_schema_version",
    "document_id",
    "workspace_id",
    "source_type",
    "content_body",
    "content_hash",
    "body_length",
    "body_word_count",
    "body_ref",
    "content_encoding",
]:
    value = body_payload.get(
        name
    )

    if name == "content_body":
        print(
            "BODY_PAYLOAD_CONTENT_BODY_PRESENT="
            + str(
                isinstance(
                    value,
                    str,
                )
            )
        )

        print(
            "BODY_PAYLOAD_CONTENT_BODY_EXACT="
            + str(
                value
                == content_body
            )
        )
    else:
        print(
            f"BODY_PAYLOAD_{name.upper()}="
            + repr(value)
        )


# ------------------------------------------------------------
# G. Binding contract
# ------------------------------------------------------------

print()
print("=== G. BINDING CONTRACT ===")

binding = envelope.get(
    "binding",
    {},
)

print(
    "BINDING_FIELD_COUNT="
    + str(
        len(binding)
    )
)

for key in binding.keys():
    print(
        f"BINDING_FIELD={key}"
    )

for name in [
    "binding_hash",
    "binding_status",
]:
    print(
        f"BINDING_{name.upper()}="
        + repr(
            binding.get(name)
        )
    )

for field in getattr(
    uucd,
    "BINDING_FIELD_NAMES",
    (),
):
    print(
        f"BINDING_VALUE_{field.upper()}="
        + repr(
            binding.get(field)
        )
    )


# ------------------------------------------------------------
# H. Initial metadata / lifecycle / versioning
# ------------------------------------------------------------

print()
print("=== H. INITIAL STATE CONTRACT ===")

metadata = record.get(
    "metadata",
    {},
)

lifecycle = record.get(
    "lifecycle",
    {},
)

versioning = record.get(
    "versioning",
    {},
)

provenance = record.get(
    "provenance",
    {},
)

handoff = record.get(
    "handoff",
    {},
)

print(
    "METADATA_PERSISTENCE_STATUS="
    + repr(
        metadata.get(
            "persistence_status"
        )
    )
)

for key, value in metadata.items():
    print(
        f"METADATA_{key.upper()}="
        + repr(value)
    )

for key, value in lifecycle.items():
    print(
        f"LIFECYCLE_{key.upper()}="
        + repr(value)
    )

for key, value in versioning.items():
    print(
        f"VERSIONING_{key.upper()}="
        + repr(value)
    )

for key, value in provenance.items():
    print(
        f"PROVENANCE_{key.upper()}="
        + repr(value)
    )

for key, value in handoff.items():
    print(
        f"HANDOFF_{key.upper()}="
        + repr(value)
    )


# ------------------------------------------------------------
# I. Stable identity/reference behavior
# ------------------------------------------------------------

print()
print("=== I. STABLE IDENTITY / REFERENCES ===")

document_id_2 = uucd._stable_document_id(
    workspace_id="ws_u9_4",
    source_type="website",
    source_record_id="source_u9_4_001",
)

content_ref_2 = uucd._stable_content_ref(
    workspace_id="ws_u9_4",
    document_id=document_id_2,
)

body_ref_2 = uucd._stable_body_ref(
    workspace_id="ws_u9_4",
    document_id=document_id_2,
    title="U9.4 Contract Title",
)

print(
    "DOCUMENT_ID_DETERMINISTIC="
    + str(
        document_id_2
        == record.get(
            "document_id"
        )
    )
)

print(
    "CONTENT_REF_DETERMINISTIC="
    + str(
        content_ref_2
        == record.get(
            "content_ref"
        )
    )
)

print(
    "BODY_REF_DETERMINISTIC="
    + str(
        body_ref_2
        == record.get(
            "body_ref"
        )
    )
)


# ------------------------------------------------------------
# J. Validation
# ------------------------------------------------------------

print()
print("=== J. ENVELOPE VALIDATION ===")

validation_result = (
    uucd.validate_universal_handoff_envelope_v1(
        envelope
    )
)

print(
    "ENVELOPE_VALIDATION_RESULT="
    + repr(
        validation_result
    )
)


# ------------------------------------------------------------
# K. U9.4 output-contract summary
# ------------------------------------------------------------

print()
print("=== K. U9.4 OUTPUT CONTRACT SUMMARY ===")

print(
    "U9.4_UUCD_SCHEMA="
    + repr(
        record.get(
            "schema_version"
        )
    )
)

print(
    "U9.4_ENGINE_VERSION="
    + repr(
        record.get(
            "engine_version"
        )
    )
)

print(
    "U9.4_ENVELOPE_SCHEMA="
    + repr(
        envelope.get(
            "envelope_schema_version"
        )
    )
)

print(
    "U9.4_BODY_PAYLOAD_SCHEMA="
    + repr(
        body_payload.get(
            "payload_schema_version"
        )
    )
)

print(
    "U9.4_INITIAL_BODY_STATUS="
    + repr(
        record.get(
            "body_status"
        )
    )
)

print(
    "U9.4_INITIAL_PERSISTENCE_STATUS="
    + repr(
        metadata.get(
            "persistence_status"
        )
    )
)

print(
    "U9.4_NEXT_STAGE="
    + repr(
        handoff.get(
            "next_stage"
        )
    )
)

print(
    "U9.4_CONTENT_BODY_IN_RECORD="
    + str(
        "content_body"
        in record
    )
)

print(
    "U9.4_CONTENT_BODY_IN_BODY_PAYLOAD="
    + str(
        isinstance(
            body_payload.get(
                "content_body"
            ),
            str,
        )
    )
)

print(
    "U9.4_PATCH_DECISION: NONE_INSPECTION_ONLY"
)

print(
    "U9.4_NEXT_STEP: FREEZE_UPLOADED_DOCUMENT_OPTION3_OUTPUT_CONTRACT"
)