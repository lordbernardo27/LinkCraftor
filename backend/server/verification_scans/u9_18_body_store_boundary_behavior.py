from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

import backend.server.stores.uploaded_document_unified_content as uduc_module

from backend.server.stores.upload_document_normalizer import (
    NormalizedUploadedDocumentContent,
)

from backend.server.universal_unified_content_document.uucd_engine_v1 import (
    build_transient_uucd_from_uduc_v1,
)

from backend.server.universal_article_body_store.body_store_writer_v1 import (
    write_verified_body_from_envelope_v1,
)


print("=== U9.18 BODY STORE BOUNDARY BEHAVIOR ===")


body = (
    "Heading A\n\n"
    "U9.18 exact body-store boundary test.\n"
)

normalized = NormalizedUploadedDocumentContent(
    source_path="C:/immutable/u9_18.txt",
    source_type="txt",
    title="U9.18 Body Store Boundary",
    text=body,
    headings=["Heading A"],
    metadata={
        "filename": "u9_18.txt",
        "extension": ".txt",
        "file_size": len(
            body.encode("utf-8")
        ),
        "extraction_method": "txt_upload_v1",
        "normalization": {
            "content_preserved": True,
            "whitespace_rewrite": False,
        },
    },
    extraction_status="success",
    extraction_confidence=1.0,
    extraction_created_at="2026-09-01T18:40:00+00:00",
    normalization_status="success",
    normalization_version="uploaded_document_normalization_v1",
    normalized_at="2026-09-01T18:40:01+00:00",
)

uduc = uduc_module.serialize_uduc(
    uduc_module.build_uduc_from_normalized_content(
        normalized_content=normalized,
        workspace_id="ws_u9_18",
        document_id="upload_doc_u9_18",
        original_filename="u9_18.txt",
        stored_filename="stored_u9_18.txt",
        stored_path="C:/persisted/ws_u9_18/stored_u9_18.txt",
        source_metadata={
            "origin_system": "linkcraftor_ui",
        },
    )
)

uduc_before = deepcopy(
    uduc
)

envelope = build_transient_uucd_from_uduc_v1(
    uduc
)

envelope_before = deepcopy(
    envelope
)

print()
print("=== A. PRE-WRITE CONTRACT ===")

print(
    "ENVELOPE_STATUS="
    + repr(
        envelope["envelope_status"]
    )
)

print(
    "PRE_BODY_STATUS="
    + repr(
        envelope[
            "uucd_record"
        ][
            "body_status"
        ]
    )
)

print(
    "BODY_PAYLOAD_PRESENT="
    + str(
        isinstance(
            envelope.get("body_payload"),
            dict,
        )
    )
)

print(
    "BINDING_STATUS="
    + repr(
        envelope[
            "binding"
        ][
            "binding_status"
        ]
    )
)

print(
    "CONTENT_BODY_IN_UUCD_RECORD="
    + str(
        "content_body"
        in envelope["uucd_record"]
    )
)


print()
print("=== B. BODY STORE WRITE ===")

with TemporaryDirectory() as temp_root:

    result = write_verified_body_from_envelope_v1(
        envelope,
        project_root=temp_root,
    )

    finalized = result[
        "finalized_uucd_record"
    ]

    certificate = result[
        "write_certificate"
    ]

    body_path = Path(
        result["body_path"]
    )

    print(
        "WRITE_STATUS="
        + repr(
            result["write_status"]
        )
    )

    print(
        "BODY_FILE_EXISTS="
        + str(
            body_path.is_file()
        )
    )

    stored_body = body_path.read_text(
        encoding="utf-8"
    )

    print(
        "STORED_BODY_EXACT="
        + str(
            stored_body == body
        )
    )

    print(
        "FINAL_BODY_STATUS="
        + repr(
            finalized[
                "body_status"
            ]
        )
    )

    print(
        "BODY_STORE_WRITE_VERIFIED="
        + str(
            finalized[
                "metadata"
            ][
                "body_store_write_verified"
            ]
        )
    )

    print(
        "PERSISTENCE_STATUS="
        + repr(
            finalized[
                "metadata"
            ][
                "persistence_status"
            ]
        )
    )

    print(
        "NEXT_STAGE="
        + repr(
            finalized[
                "handoff"
            ][
                "next_stage"
            ]
        )
    )

    print(
        "ELIGIBLE_FOR_BODY_STORE="
        + str(
            finalized[
                "handoff"
            ][
                "eligible_for_body_store"
            ]
        )
    )

    print(
        "ELIGIBLE_FOR_UUCD_PERSISTENCE="
        + str(
            finalized[
                "handoff"
            ][
                "eligible_for_uucd_persistence"
            ]
        )
    )

    print(
        "BODY_STORE_VERIFIED="
        + str(
            finalized[
                "handoff"
            ][
                "body_store_verified"
            ]
        )
    )

    print(
        "CONTENT_BODY_IN_FINAL_UUCD_RECORD="
        + str(
            "content_body"
            in finalized
        )
    )

    print(
        "CERTIFICATE_UUCD_PERSISTED="
        + str(
            certificate[
                "uucd_record_persisted"
            ]
        )
    )

    print(
        "CERTIFICATE_RUNTIME_EXECUTED="
        + str(
            certificate[
                "runtime_executed"
            ]
        )
    )

    print(
        "CERTIFICATE_SEMANTIC_PROCESSING="
        + str(
            certificate[
                "semantic_processing_performed"
            ]
        )
    )

    checks = [
        envelope[
            "envelope_status"
        ] == "READY_FOR_BODY_STORE",

        envelope[
            "uucd_record"
        ][
            "body_status"
        ] == "PENDING_BODY_STORE_WRITE",

        envelope[
            "binding"
        ][
            "binding_status"
        ] == "BOUND_AND_VERIFIED",

        "content_body"
        not in envelope[
            "uucd_record"
        ],

        result[
            "write_status"
        ] == "STORED_AND_VERIFIED",

        body_path.is_file(),

        stored_body == body,

        finalized[
            "body_status"
        ] == "STORED_AND_VERIFIED",

        finalized[
            "metadata"
        ][
            "body_store_write_verified"
        ] is True,

        finalized[
            "metadata"
        ][
            "persistence_status"
        ] == "READY_FOR_UUCD_PERSISTENCE",

        finalized[
            "handoff"
        ][
            "next_stage"
        ] == "uucd_persistence",

        finalized[
            "handoff"
        ][
            "eligible_for_body_store"
        ] is False,

        finalized[
            "handoff"
        ][
            "eligible_for_uucd_persistence"
        ] is True,

        finalized[
            "handoff"
        ][
            "body_store_verified"
        ] is True,

        "content_body"
        not in finalized,

        certificate[
            "uucd_record_persisted"
        ] is False,

        certificate[
            "runtime_executed"
        ] is False,

        certificate[
            "semantic_processing_performed"
        ] is False,
    ]


print()
print("=== C. INPUT IMMUTABILITY ===")

print(
    "UDUC_MUTATED="
    + str(
        uduc != uduc_before
    )
)

print(
    "TRANSIENT_ENVELOPE_MUTATED="
    + str(
        envelope != envelope_before
    )
)

checks.extend(
    [
        uduc == uduc_before,
        envelope == envelope_before,
    ]
)


print()
print("=== D. FINAL U9.18 DECISION ===")

print(
    "TOTAL_U9_18_CHECKS="
    + str(
        len(checks)
    )
)

print(
    "TOTAL_U9_18_CHECKS_PASSED="
    + str(
        sum(
            1
            for check in checks
            if check
        )
    )
)

print(
    "ALL_U9_18_CHECKS_PASSED="
    + str(
        all(checks)
    )
)

print(
    "U9.18_NEXT_STEP=CERTIFY_BODY_STORE_BOUNDARY"
)