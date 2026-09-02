import copy

import backend.server.universal_unified_content_document.uucd_engine_v1 as uucd


print("=== U9.4 CURRENT CANONICAL UUCD OUTPUT CONTRACT INSPECTION V2 ===")


# ------------------------------------------------------------
# A. Canonical constants
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
# B. Required field sets
# ------------------------------------------------------------

print()
print("=== B. REQUIRED FIELD SETS ===")

for name in [
    "REQUIRED_WUC_FIELDS",
    "REQUIRED_WUC_HANDOFF_FIELDS",
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

        for item in sorted(value):
            print(
                f"{name}_FIELD={item}"
            )


# ------------------------------------------------------------
# C. Valid current WUC fixture
#    This observes existing Option-3 output only.
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

    "document_id":
        "website_document_u9_4_001",

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
        "next_stage":
            "universal_unified_content_document",

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
# D. Envelope
# ------------------------------------------------------------

print()
print("=== D. ENVELOPE CONTRACT ===")

print(
    "ENVELOPE_FIELD_COUNT="
    + str(len(envelope))
)

for key in envelope:
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
# E. UUCD record
# ------------------------------------------------------------

print()
print("=== E. UUCD RECORD CONTRACT ===")

record = envelope["uucd_record"]

print(
    "UUCD_RECORD_FIELD_COUNT="
    + str(len(record))
)

for key in record:
    print(
        f"UUCD_RECORD_FIELD={key}"
    )

print(
    "CONTENT_BODY_IN_UUCD_RECORD="
    + str(
        "content_body"
        in record
    )
)

for key in [
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
        f"RECORD_{key.upper()}="
        + repr(
            record.get(key)
        )
    )


# ------------------------------------------------------------
# F. Body payload
# ------------------------------------------------------------

print()
print("=== F. BODY PAYLOAD CONTRACT ===")

body_payload = envelope["body_payload"]

print(
    "BODY_PAYLOAD_FIELD_COUNT="
    + str(len(body_payload))
)

for key in body_payload:
    print(
        f"BODY_PAYLOAD_FIELD={key}"
    )

print(
    "BODY_PAYLOAD_CONTENT_BODY_EXACT="
    + str(
        body_payload.get(
            "content_body"
        )
        == content_body
    )
)

for key in [
    "payload_schema_version",
    "document_id",
    "workspace_id",
    "source_type",
    "content_hash",
    "body_length",
    "body_word_count",
    "body_ref",
    "content_encoding",
]:
    print(
        f"BODY_PAYLOAD_{key.upper()}="
        + repr(
            body_payload.get(key)
        )
    )


# ------------------------------------------------------------
# G. Binding
# ------------------------------------------------------------

print()
print("=== G. BINDING CONTRACT ===")

binding = envelope["binding"]

print(
    "BINDING_FIELD_COUNT="
    + str(len(binding))
)

for key in binding:
    print(
        f"BINDING_FIELD={key}"
    )

for key in uucd.BINDING_FIELD_NAMES:
    print(
        f"BINDING_SHARED_{key.upper()}="
        + repr(
            binding.get(key)
        )
    )

print(
    "BINDING_HASH="
    + repr(
        binding.get(
            "binding_hash"
        )
    )
)

print(
    "BINDING_STATUS="
    + repr(
        binding.get(
            "binding_status"
        )
    )
)


# ------------------------------------------------------------
# H. Initial states
# ------------------------------------------------------------

print()
print("=== H. INITIAL STATE CONTRACT ===")

metadata = record["metadata"]
lifecycle = record["lifecycle"]
versioning = record["versioning"]
provenance = record["provenance"]
handoff = record["handoff"]

for group_name, group in [
    ("METADATA", metadata),
    ("LIFECYCLE", lifecycle),
    ("VERSIONING", versioning),
    ("PROVENANCE", provenance),
    ("HANDOFF", handoff),
]:
    print()
    print(
        f"GROUP={group_name}"
    )

    for key, value in group.items():
        print(
            f"{group_name}_{key.upper()}="
            + repr(value)
        )


# ------------------------------------------------------------
# I. Stable identity and refs
# ------------------------------------------------------------

print()
print("=== I. STABLE IDENTITY / REFERENCES ===")

expected_document_id = (
    uucd._stable_document_id(
        workspace_id="ws_u9_4",
        source_type="website",
        source_record_id="source_u9_4_001",
    )
)

expected_content_ref = (
    uucd._stable_content_ref(
        workspace_id="ws_u9_4",
        document_id=expected_document_id,
    )
)

expected_body_ref = (
    uucd._stable_body_ref(
        workspace_id="ws_u9_4",
        document_id=expected_document_id,
        title="U9.4 Contract Title",
    )
)

print(
    "DOCUMENT_ID_DETERMINISTIC="
    + str(
        record["document_id"]
        == expected_document_id
    )
)

print(
    "CONTENT_REF_DETERMINISTIC="
    + str(
        record["content_ref"]
        == expected_content_ref
    )
)

print(
    "BODY_REF_DETERMINISTIC="
    + str(
        record["body_ref"]
        == expected_body_ref
    )
)


# ------------------------------------------------------------
# J. Record / payload binding equality
# ------------------------------------------------------------

print()
print("=== J. BINDING EQUALITY ===")

for field in uucd.BINDING_FIELD_NAMES:
    record_value = record.get(field)
    payload_value = body_payload.get(field)
    binding_value = binding.get(field)

    print(
        f"BINDING_EQUAL_{field.upper()}="
        + str(
            record_value
            == payload_value
            == binding_value
        )
    )


# ------------------------------------------------------------
# K. Canonical envelope validation
# ------------------------------------------------------------

print()
print("=== K. CANONICAL VALIDATION ===")

print(
    "ENVELOPE_VALIDATION_RESULT="
    + repr(
        uucd.validate_universal_handoff_envelope_v1(
            envelope
        )
    )
)


# ------------------------------------------------------------
# L. Summary
# ------------------------------------------------------------

print()
print("=== L. U9.4 OUTPUT CONTRACT SUMMARY ===")

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
    "U9.4_INPUT_MUTATION="
    + str(
        wuc_package
        != wuc_before
    )
)

print(
    "U9.4_PATCH_DECISION: NONE_INSPECTION_ONLY"
)

print(
    "U9.4_NEXT_STEP: FREEZE_UPLOADED_DOCUMENT_OPTION3_OUTPUT_CONTRACT"
)
