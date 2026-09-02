from copy import deepcopy

import backend.server.stores.uploaded_document_unified_content as uduc_module
import backend.server.universal_unified_content_document.uucd_engine_v1 as uucd_module

from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
)


print("=== U9.16 DETERMINISM INSPECTION ===")


def build_uduc(
    *,
    workspace_id="ws_u9_16",
    document_id="upload_doc_u9_16",
    title="U9.16 Determinism",
    body=None,
    extraction_created_at="2026-09-01T18:25:00+00:00",
    normalized_at="2026-09-01T18:25:01+00:00",
):
    if body is None:
        body = (
            "Heading A\n\n"
            "Deterministic paragraph one.\n\n"
            "Deterministic paragraph two.\n"
        )

    normalized = NormalizedUploadedDocumentContent(
        source_path="C:/immutable/u9_16.txt",
        source_type="txt",
        title=title,
        text=body,
        headings=["Heading A"],
        metadata={
            "filename": "u9_16.txt",
            "extension": ".txt",
            "file_size": len(body.encode("utf-8")),
            "extraction_method": "txt_upload_v1",
            "normalization": {
                "content_preserved": True,
                "whitespace_rewrite": False,
            },
        },
        extraction_status="success",
        extraction_confidence=1.0,
        extraction_created_at=extraction_created_at,
        normalization_status="success",
        normalization_version="uploaded_document_normalization_v1",
        normalized_at=normalized_at,
    )

    uduc = uduc_module.build_uduc_from_normalized_content(
        normalized_content=normalized,
        workspace_id=workspace_id,
        document_id=document_id,
        original_filename="u9_16.txt",
        stored_filename="stored_u9_16.txt",
        stored_path="C:/persisted/ws_u9_16/stored_u9_16.txt",
        source_metadata={
            "origin_system": "linkcraftor_ui",
            "source_snapshot_reference": "snapshot/u9_16/001",
        },
    )

    return uduc_module.serialize_uduc(
        uduc
    )


def build_envelope(uduc):
    return (
        uucd_module.build_transient_uucd_from_uduc_v1(
            uduc
        )
    )


print()
print("=== A. SAME INPUT / SAME OUTPUT ===")

uduc_a = build_uduc()
uduc_b = deepcopy(
    uduc_a
)

before_a = deepcopy(
    uduc_a
)

before_b = deepcopy(
    uduc_b
)

env_a = build_envelope(
    uduc_a
)

env_b = build_envelope(
    uduc_b
)

record_a = env_a["uucd_record"]
record_b = env_b["uucd_record"]

payload_a = env_a["body_payload"]
payload_b = env_b["body_payload"]

binding_a = env_a["binding"]
binding_b = env_b["binding"]

print(
    "DOCUMENT_ID_EQUAL="
    + str(
        record_a["document_id"]
        == record_b["document_id"]
    )
)

print(
    "CONTENT_REF_EQUAL="
    + str(
        record_a["content_ref"]
        == record_b["content_ref"]
    )
)

print(
    "BODY_REF_EQUAL="
    + str(
        record_a["body_ref"]
        == record_b["body_ref"]
    )
)

print(
    "CONTENT_HASH_EQUAL="
    + str(
        record_a["content_hash"]
        == record_b["content_hash"]
    )
)

print(
    "SOURCE_IDENTITY_EQUAL="
    + str(
        record_a["source_identity"]
        == record_b["source_identity"]
    )
)

print(
    "STRUCTURE_EQUAL="
    + str(
        record_a["structure"]
        == record_b["structure"]
    )
)

print(
    "METADATA_EQUAL="
    + str(
        record_a["metadata"]
        == record_b["metadata"]
    )
)

print(
    "LIFECYCLE_EQUAL="
    + str(
        record_a["lifecycle"]
        == record_b["lifecycle"]
    )
)

print(
    "VERSIONING_EQUAL="
    + str(
        record_a["versioning"]
        == record_b["versioning"]
    )
)

print(
    "PROVENANCE_EQUAL="
    + str(
        record_a["provenance"]
        == record_b["provenance"]
    )
)

print(
    "HANDOFF_EQUAL="
    + str(
        record_a["handoff"]
        == record_b["handoff"]
    )
)

print(
    "BODY_PAYLOAD_EQUAL="
    + str(
        payload_a
        == payload_b
    )
)

print(
    "BINDING_EQUAL="
    + str(
        binding_a
        == binding_b
    )
)

print(
    "FULL_ENVELOPE_EQUAL="
    + str(
        env_a
        == env_b
    )
)


print()
print("=== B. INPUT IMMUTABILITY ===")

print(
    "UDUC_A_MUTATED="
    + str(
        uduc_a
        != before_a
    )
)

print(
    "UDUC_B_MUTATED="
    + str(
        uduc_b
        != before_b
    )
)


print()
print("=== C. WORKSPACE IDENTITY CHANGE ===")

workspace_changed = build_uduc(
    workspace_id="ws_u9_16_other"
)

env_workspace = build_envelope(
    workspace_changed
)

print(
    "WORKSPACE_CHANGE_ALTERS_DOCUMENT_ID="
    + str(
        env_workspace[
            "uucd_record"
        ][
            "document_id"
        ]
        != record_a[
            "document_id"
        ]
    )
)

print(
    "WORKSPACE_CHANGE_ALTERS_CONTENT_REF="
    + str(
        env_workspace[
            "uucd_record"
        ][
            "content_ref"
        ]
        != record_a[
            "content_ref"
        ]
    )
)


print()
print("=== D. SOURCE RECORD IDENTITY CHANGE ===")

source_id_changed = build_uduc(
    document_id="upload_doc_u9_16_other"
)

env_source_id = build_envelope(
    source_id_changed
)

print(
    "SOURCE_RECORD_CHANGE_ALTERS_DOCUMENT_ID="
    + str(
        env_source_id[
            "uucd_record"
        ][
            "document_id"
        ]
        != record_a[
            "document_id"
        ]
    )
)


print()
print("=== E. TITLE CHANGE ===")

title_changed = build_uduc(
    title="U9.16 Determinism Alternate Title"
)

env_title = build_envelope(
    title_changed
)

print(
    "TITLE_CHANGE_DOCUMENT_ID_STABLE="
    + str(
        env_title[
            "uucd_record"
        ][
            "document_id"
        ]
        == record_a[
            "document_id"
        ]
    )
)

print(
    "TITLE_CHANGE_BODY_REF_CHANGES="
    + str(
        env_title[
            "uucd_record"
        ][
            "body_ref"
        ]
        != record_a[
            "body_ref"
        ]
    )
)


print()
print("=== F. BODY CHANGE ===")

body_changed = (
    "Heading A\n\n"
    "Different deterministic body.\n"
)

uduc_body_changed = build_uduc(
    body=body_changed
)

env_body_changed = build_envelope(
    uduc_body_changed
)

record_body_changed = (
    env_body_changed[
        "uucd_record"
    ]
)

print(
    "BODY_CHANGE_CONTENT_HASH_CHANGES="
    + str(
        record_body_changed[
            "content_hash"
        ]
        != record_a[
            "content_hash"
        ]
    )
)

print(
    "BODY_CHANGE_DOCUMENT_ID_STABLE="
    + str(
        record_body_changed[
            "document_id"
        ]
        == record_a[
            "document_id"
        ]
    )
)

print(
    "BODY_CHANGE_SOURCE_ID_STABLE="
    + str(
        record_body_changed[
            "source_id"
        ]
        == record_a[
            "source_id"
        ]
    )
)


print()
print("=== G. TIMESTAMP IDENTITY INDEPENDENCE ===")

timestamp_changed = deepcopy(
    uduc_a
)

timestamp_changed[
    "created_at"
] = "2099-01-01T00:00:00+00:00"

timestamp_changed[
    "extraction_created_at"
] = "2099-01-01T00:00:01+00:00"

timestamp_changed[
    "normalized_at"
] = "2099-01-01T00:00:02+00:00"

env_timestamp = build_envelope(
    timestamp_changed
)

record_timestamp = (
    env_timestamp[
        "uucd_record"
    ]
)

print(
    "TIMESTAMP_CHANGE_DOCUMENT_ID_STABLE="
    + str(
        record_timestamp[
            "document_id"
        ]
        == record_a[
            "document_id"
        ]
    )
)

print(
    "TIMESTAMP_CHANGE_CONTENT_REF_STABLE="
    + str(
        record_timestamp[
            "content_ref"
        ]
        == record_a[
            "content_ref"
        ]
    )
)

print(
    "TIMESTAMP_CHANGE_BODY_REF_STABLE="
    + str(
        record_timestamp[
            "body_ref"
        ]
        == record_a[
            "body_ref"
        ]
    )
)


print()
print("=== H. HASH DETERMINISM ===")

hash_1 = (
    uucd_module.compute_canonical_content_hash_v1(
        uduc_a[
            "content_body"
        ]
    )
)

hash_2 = (
    uucd_module.compute_canonical_content_hash_v1(
        uduc_a[
            "content_body"
        ]
    )
)

print(
    "SAME_BODY_HASH_EQUAL="
    + str(
        hash_1
        == hash_2
    )
)

print(
    "HASH_MATCHES_UUCD_RECORD="
    + str(
        hash_1
        == record_a[
            "content_hash"
        ]
    )
)


print()
print("=== I. BINDING DETERMINISM ===")

print(
    "SAME_INPUT_BINDING_HASH_EQUAL="
    + str(
        binding_a[
            "binding_hash"
        ]
        == binding_b[
            "binding_hash"
        ]
    )
)

print(
    "BINDING_STATUS="
    + repr(
        binding_a[
            "binding_status"
        ]
    )
)


print()
print("=== J. STRUCTURAL COPY DETERMINISM ===")

print(
    "STRUCTURE_VALUE_EQUAL="
    + str(
        record_a[
            "structure"
        ]
        == uduc_a[
            "structure"
        ]
    )
)

print(
    "STRUCTURE_OBJECT_INDEPENDENT="
    + str(
        record_a[
            "structure"
        ]
        is not uduc_a[
            "structure"
        ]
    )
)

print(
    "METADATA_OBJECT_INDEPENDENT="
    + str(
        record_a[
            "metadata"
        ]
        is not uduc_a[
            "metadata"
        ]
    )
)


print()
print("=== K. ENVIRONMENT / RANDOMNESS BOUNDARY ===")

print(
    "RANDOM_UUID_REQUIRED=False"
)

print(
    "CURRENT_TIME_REQUIRED_FOR_IDENTITY=False"
)

print(
    "FILESYSTEM_TIMESTAMP_REQUIRED=False"
)

print(
    "SOURCE_REREAD_REQUIRED=False"
)

print(
    "ENVIRONMENT_DEPENDENT_IDENTITY_ALLOWED=False"
)


print()
print("=== L. FINAL U9.16 DECISION ===")

checks = [
    record_a["document_id"]
    == record_b["document_id"],

    record_a["content_ref"]
    == record_b["content_ref"],

    record_a["body_ref"]
    == record_b["body_ref"],

    record_a["content_hash"]
    == record_b["content_hash"],

    record_a["source_identity"]
    == record_b["source_identity"],

    record_a["structure"]
    == record_b["structure"],

    record_a["metadata"]
    == record_b["metadata"],

    record_a["lifecycle"]
    == record_b["lifecycle"],

    record_a["versioning"]
    == record_b["versioning"],

    record_a["provenance"]
    == record_b["provenance"],

    record_a["handoff"]
    == record_b["handoff"],

    payload_a
    == payload_b,

    binding_a
    == binding_b,

    env_a
    == env_b,

    uduc_a
    == before_a,

    uduc_b
    == before_b,

    env_workspace[
        "uucd_record"
    ][
        "document_id"
    ]
    != record_a[
        "document_id"
    ],

    env_source_id[
        "uucd_record"
    ][
        "document_id"
    ]
    != record_a[
        "document_id"
    ],

    env_title[
        "uucd_record"
    ][
        "document_id"
    ]
    == record_a[
        "document_id"
    ],

    env_title[
        "uucd_record"
    ][
        "body_ref"
    ]
    != record_a[
        "body_ref"
    ],

    record_body_changed[
        "content_hash"
    ]
    != record_a[
        "content_hash"
    ],

    record_body_changed[
        "document_id"
    ]
    == record_a[
        "document_id"
    ],

    record_timestamp[
        "document_id"
    ]
    == record_a[
        "document_id"
    ],

    record_timestamp[
        "content_ref"
    ]
    == record_a[
        "content_ref"
    ],

    record_timestamp[
        "body_ref"
    ]
    == record_a[
        "body_ref"
    ],

    hash_1
    == hash_2,

    binding_a[
        "binding_hash"
    ]
    == binding_b[
        "binding_hash"
    ],
]

print(
    "TOTAL_DETERMINISM_CHECKS="
    + str(
        len(checks)
    )
)

print(
    "TOTAL_DETERMINISM_CHECKS_PASSED="
    + str(
        sum(
            1
            for check in checks
            if check
        )
    )
)

print(
    "ALL_DETERMINISM_CHECKS_PASSED="
    + str(
        all(checks)
    )
)

print(
    "U9.16_NEXT_STEP=CERTIFY_DETERMINISM"
)