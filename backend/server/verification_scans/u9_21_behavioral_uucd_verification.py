from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from backend.server.universal_unified_content_document.uucd_engine_v1 import (
    UUCDContractError,
    build_transient_uucd_from_uduc_v1,
)
from backend.server.universal_article_body_store.body_store_writer_v1 import (
    write_verified_body_from_envelope_v1,
)
from backend.server.universal_article_body_store.body_store_repository_v1 import (
    verify_body,
)
from backend.server.universal_unified_content_document.uucd_persistence_v1 import (
    UUCDPersistenceContractError,
    persist_finalized_uucd_v1,
)
from backend.server.runtime.uucd_runtime_handoff_v1 import (
    UUCDRuntimeHandoffContractError,
    _validate_persisted_uucd,
    build_uucd_runtime_payload_v1,
)


print("=== U9.21 BEHAVIORAL UUCD VERIFICATION ===")

BODY = (
    "LinkCraftor behavioral verification document.\n\n"
    "This exact body must travel from canonical UDUC into the "
    "Universal Article Body Store without rewriting, truncation, "
    "summarization, normalization, or semantic processing.\n\n"
    "The final Current Canonical UUCD must remain bodyless."
)

BODY_HASH = hashlib.sha256(
    BODY.encode("utf-8")
).hexdigest()

UDUC = {
    "schema_version":
        "uploaded_document_unified_content_v2",

    "pipeline_version":
        "uploaded_document_uduc_pipeline_v2",

    "workspace_id":
        "ws_u9_21_behavioral",

    "document_id":
        "uploaded_doc_u9_21_001",

    "source_type":
        "uploaded_document",

    "source_format":
        "txt",

    "original_filename":
        "u9_21_behavioral.txt",

    "stored_filename":
        "u9_21_behavioral.txt",

    "stored_path":
        "uploads/ws_u9_21_behavioral/u9_21_behavioral.txt",

    "title":
        "U9.21 Behavioral Verification",

    "h1":
        "U9.21 Behavioral Verification",

    "headings": [
        "U9.21 Behavioral Verification",
        "Behavioral Boundary",
    ],

    "content_body":
        BODY,

    "structure": {
        "structure_version":
            "uduc_structure_v1_2",

        "heading_count":
            2,

        "paragraph_count":
            3,

        "source_format":
            "txt",
    },

    "metadata": {
        "extraction_method":
            "u9_21_fixture",

        "extraction_timestamp":
            "2026-09-01T19:00:00+00:00",

        "extension":
            ".txt",

        "file_size":
            len(BODY.encode("utf-8")),

        "source_metadata": {
            "fixture":
                "u9_21_behavioral_verification",
        },

        "normalization": {
            "fixture":
                True,
        },

        "boundary": {
            "input":
                "canonical_uduc",

            "output":
                "current_canonical_uucd",
        },
    },

    "extraction_status":
        "EXTRACTED",

    "extraction_confidence":
        1.0,

    "extraction_created_at":
        "2026-09-01T19:00:00+00:00",

    "normalization_status":
        "NORMALIZED",

    "normalization_version":
        "upload_normalization_v1",

    "normalized_at":
        "2026-09-01T19:00:01+00:00",

    "created_at":
        "2026-09-01T19:00:02+00:00",
}


checks: list[tuple[str, bool]] = []


def check(
    name: str,
    condition: bool,
) -> None:

    value = bool(
        condition
    )

    checks.append(
        (
            name,
            value,
        )
    )

    print(
        f"{name}={value}"
    )


def reject_check(
    name: str,
    callable_obj,
    accepted_errors: tuple[type[BaseException], ...],
) -> None:

    try:
        callable_obj()
        rejected = False

    except accepted_errors:
        rejected = True

    check(
        name,
        rejected,
    )


original_uduc = deepcopy(
    UDUC
)


print()
print("=== A. CURRENT CANONICAL UUCD CONSTRUCTION ===")

envelope = build_transient_uucd_from_uduc_v1(
    UDUC
)

record = envelope[
    "uucd_record"
]

payload = envelope[
    "body_payload"
]

binding = envelope[
    "binding"
]


check(
    "UDUC_INPUT_UNCHANGED_AFTER_BUILD",
    UDUC == original_uduc,
)

check(
    "ENVELOPE_READY_FOR_BODY_STORE",
    envelope.get(
        "envelope_status"
    )
    == "READY_FOR_BODY_STORE",
)

check(
    "SOURCE_TYPE_UPLOADED_DOCUMENT",
    record.get(
        "source_type"
    )
    == "uploaded_document",
)

check(
    "SOURCE_ID_PRESERVED",
    record.get(
        "source_id"
    )
    == UDUC[
        "document_id"
    ],
)

check(
    "WORKSPACE_ID_PRESERVED",
    record.get(
        "workspace_id"
    )
    == UDUC[
        "workspace_id"
    ],
)

check(
    "CANONICAL_DOCUMENT_ID_PRESENT",
    isinstance(
        record.get(
            "document_id"
        ),
        str,
    )
    and record[
        "document_id"
    ].startswith(
        "uucd_"
    ),
)

check(
    "CONTENT_HASH_EXACT",
    record.get(
        "content_hash"
    )
    == BODY_HASH,
)

check(
    "BODY_LENGTH_EXACT",
    record.get(
        "body_length"
    )
    == len(
        BODY
    ),
)

check(
    "BODY_WORD_COUNT_EXACT",
    record.get(
        "body_word_count"
    )
    == len(
        BODY.split()
    ),
)

check(
    "UUCD_RECORD_HAS_NO_CONTENT_BODY",
    "content_body"
    not in record,
)

check(
    "INITIAL_BODY_STATUS_PENDING",
    record.get(
        "body_status"
    )
    == "PENDING_BODY_STORE_WRITE",
)

check(
    "CONTENT_REF_PRESENT",
    isinstance(
        record.get(
            "content_ref"
        ),
        str,
    )
    and bool(
        record.get(
            "content_ref"
        )
    ),
)

check(
    "BODY_REF_PRESENT",
    isinstance(
        record.get(
            "body_ref"
        ),
        str,
    )
    and bool(
        record.get(
            "body_ref"
        )
    ),
)


print()
print("=== B. BODY PAYLOAD / BINDING ===")

check(
    "BODY_PAYLOAD_EXACT_CONTENT",
    payload.get(
        "content_body"
    )
    == BODY,
)

check(
    "BODY_PAYLOAD_DOCUMENT_ID_MATCH",
    payload.get(
        "document_id"
    )
    == record.get(
        "document_id"
    ),
)

check(
    "BODY_PAYLOAD_WORKSPACE_MATCH",
    payload.get(
        "workspace_id"
    )
    == record.get(
        "workspace_id"
    ),
)

check(
    "BODY_PAYLOAD_HASH_MATCH",
    payload.get(
        "content_hash"
    )
    == record.get(
        "content_hash"
    ),
)

check(
    "BODY_PAYLOAD_BODY_REF_MATCH",
    payload.get(
        "body_ref"
    )
    == record.get(
        "body_ref"
    ),
)

check(
    "BINDING_STATUS_VERIFIED",
    binding.get(
        "binding_status"
    )
    == "BOUND_AND_VERIFIED",
)

check(
    "BINDING_HASH_PRESENT",
    isinstance(
        binding.get(
            "binding_hash"
        ),
        str,
    )
    and bool(
        binding.get(
            "binding_hash"
        )
    ),
)

check(
    "HANDOFF_NEXT_STAGE_BODY_STORE",
    record[
        "handoff"
    ].get(
        "next_stage"
    )
    == "universal_article_body_store",
)

check(
    "HANDOFF_BODY_STORE_ELIGIBLE",
    record[
        "handoff"
    ].get(
        "eligible_for_body_store"
    )
    is True,
)


print()
print("=== C. DETERMINISTIC REBUILD ===")

envelope_again = build_transient_uucd_from_uduc_v1(
    deepcopy(
        UDUC
    )
)

check(
    "DETERMINISTIC_DOCUMENT_ID",
    envelope_again[
        "uucd_record"
    ][
        "document_id"
    ]
    == record[
        "document_id"
    ],
)

check(
    "DETERMINISTIC_CONTENT_REF",
    envelope_again[
        "uucd_record"
    ][
        "content_ref"
    ]
    == record[
        "content_ref"
    ],
)

check(
    "DETERMINISTIC_BODY_REF",
    envelope_again[
        "uucd_record"
    ][
        "body_ref"
    ]
    == record[
        "body_ref"
    ],
)

check(
    "DETERMINISTIC_CONTENT_HASH",
    envelope_again[
        "uucd_record"
    ][
        "content_hash"
    ]
    == record[
        "content_hash"
    ],
)


print()
print("=== D. FAILURE CONTRACT BEFORE BODY STORE ===")

bad_uduc = deepcopy(
    UDUC
)

bad_uduc[
    "schema_version"
] = "wrong_schema"

reject_check(
    "BAD_UDUC_SCHEMA_REJECTED",
    lambda: build_transient_uucd_from_uduc_v1(
        bad_uduc
    ),
    (
        UUCDContractError,
    ),
)


with TemporaryDirectory(
    prefix="linkcraftor_u9_21_"
) as temp_root:

    root = Path(
        temp_root
    )

    envelope_before_write = deepcopy(
        envelope
    )


    print()
    print("=== E. BODY STORE WRITE ===")

    write_result = (
        write_verified_body_from_envelope_v1(
            envelope,
            project_root=root,
            overwrite=False,
        )
    )

    finalized = write_result[
        "finalized_uucd_record"
    ]

    certificate = write_result[
        "write_certificate"
    ]

    check(
        "BODY_STORE_WRITE_STATUS_VERIFIED",
        write_result.get(
            "write_status"
        )
        == "STORED_AND_VERIFIED",
    )

    check(
        "ENVELOPE_INPUT_UNCHANGED_AFTER_BODY_WRITE",
        envelope
        == envelope_before_write,
    )

    check(
        "WRITE_CERTIFICATE_EXACT_CONTENT_MATCH",
        certificate.get(
            "exact_content_match"
        )
        is True,
    )

    check(
        "WRITE_CERTIFICATE_HASH_VERIFIED",
        certificate.get(
            "hash_verified"
        )
        is True,
    )

    check(
        "WRITE_CERTIFICATE_LENGTH_VERIFIED",
        certificate.get(
            "character_length_verified"
        )
        is True,
    )

    check(
        "WRITE_CERTIFICATE_WORD_COUNT_VERIFIED",
        certificate.get(
            "word_count_verified"
        )
        is True,
    )

    check(
        "WRITE_CERTIFICATE_NO_UUCD_PERSISTENCE",
        certificate.get(
            "uucd_record_persisted"
        )
        is False,
    )

    check(
        "WRITE_CERTIFICATE_NO_RUNTIME",
        certificate.get(
            "runtime_executed"
        )
        is False,
    )

    check(
        "WRITE_CERTIFICATE_NO_SEMANTIC",
        certificate.get(
            "semantic_processing_performed"
        )
        is False,
    )

    check(
        "FINALIZED_BODY_STATUS_VERIFIED",
        finalized.get(
            "body_status"
        )
        == "STORED_AND_VERIFIED",
    )

    check(
        "FINALIZED_BODY_STORE_WRITE_VERIFIED",
        finalized[
            "metadata"
        ].get(
            "body_store_write_verified"
        )
        is True,
    )

    check(
        "FINALIZED_READY_FOR_PERSISTENCE",
        finalized[
            "metadata"
        ].get(
            "persistence_status"
        )
        == "READY_FOR_UUCD_PERSISTENCE",
    )

    check(
        "FINALIZED_NEXT_STAGE_PERSISTENCE",
        finalized[
            "handoff"
        ].get(
            "next_stage"
        )
        == "uucd_persistence",
    )

    check(
        "FINALIZED_UUCD_PERSISTENCE_ELIGIBLE",
        finalized[
            "handoff"
        ].get(
            "eligible_for_uucd_persistence"
        )
        is True,
    )

    check(
        "FINALIZED_BODY_STORE_VERIFIED",
        finalized[
            "handoff"
        ].get(
            "body_store_verified"
        )
        is True,
    )

    check(
        "FINALIZED_UUCD_HAS_NO_CONTENT_BODY",
        "content_body"
        not in finalized,
    )


    print()
    print("=== F. INDEPENDENT BODY VERIFICATION ===")

    body_verification = verify_body(
        project_root=root,
        workspace_id=finalized[
            "workspace_id"
        ],
        body_ref=finalized[
            "body_ref"
        ],
        expected_content_hash=finalized[
            "content_hash"
        ],
        expected_body_length=finalized[
            "body_length"
        ],
        expected_body_byte_length=len(
            BODY.encode(
                "utf-8"
            )
        ),
        expected_body_word_count=finalized[
            "body_word_count"
        ],
    )

    check(
        "BODY_VERIFICATION_RETURNED_MAPPING",
        isinstance(
            body_verification,
            dict,
        ),
    )

    body_path = Path(
        write_result[
            "body_path"
        ]
    )

    check(
        "BODY_FILE_EXISTS",
        body_path.exists(),
    )

    stored_body = body_path.read_text(
        encoding="utf-8"
    )

    check(
        "STORED_BODY_TEXT_EXACT",
        stored_body == BODY,
    )

    check(
        "STORED_BODY_HASH_EXACT",
        hashlib.sha256(
            stored_body.encode(
                "utf-8"
            )
        ).hexdigest()
        == BODY_HASH,
    )


    print()
    print("=== G. PRE-PERSISTENCE RUNTIME REJECTION ===")

    reject_check(
        "FINALIZED_BUT_UNPERSISTED_RUNTIME_REJECTED",
        lambda: _validate_persisted_uucd(
            finalized
        ),
        (
            UUCDRuntimeHandoffContractError,
        ),
    )


    print()
    print("=== H. CURRENT CANONICAL UUCD PERSISTENCE ===")

    finalized_before_persistence = deepcopy(
        finalized
    )

    persistence_result = persist_finalized_uucd_v1(
        finalized,
        project_root=root,
        overwrite=False,
    )

    persisted = persistence_result[
        "persisted_uucd_record"
    ]

    persistence_certificate = (
        persistence_result[
            "persistence_certificate"
        ]
    )

    check(
        "FINALIZED_INPUT_UNCHANGED_AFTER_PERSISTENCE",
        finalized
        == finalized_before_persistence,
    )

    check(
        "PERSISTENCE_RESULT_STATUS_VERIFIED",
        persistence_result.get(
            "persistence_status"
        )
        == "PERSISTED_AND_VERIFIED",
    )

    check(
        "PERSISTED_METADATA_STATUS_VERIFIED",
        persisted[
            "metadata"
        ].get(
            "persistence_status"
        )
        == "PERSISTED_AND_VERIFIED",
    )

    check(
        "PERSISTED_HANDOFF_FLAG_TRUE",
        persisted[
            "handoff"
        ].get(
            "uucd_persisted"
        )
        is True,
    )

    check(
        "PERSISTED_NEXT_STAGE_RUNTIME",
        persisted[
            "handoff"
        ].get(
            "next_stage"
        )
        == "runtime_queue_handoff",
    )

    check(
        "PERSISTED_BODY_STATUS_STILL_VERIFIED",
        persisted.get(
            "body_status"
        )
        == "STORED_AND_VERIFIED",
    )

    check(
        "PERSISTED_UUCD_HAS_NO_CONTENT_BODY",
        "content_body"
        not in persisted,
    )

    check(
        "PERSISTENCE_CERT_BODYLESS",
        persistence_certificate.get(
            "content_body_persisted_in_uucd"
        )
        is False,
    )

    check(
        "PERSISTENCE_CERT_NO_RUNTIME",
        persistence_certificate.get(
            "runtime_executed"
        )
        is False,
    )

    check(
        "PERSISTENCE_CERT_NO_JOB_CREATION",
        persistence_certificate.get(
            "queue_job_created"
        )
        is False,
    )

    check(
        "PERSISTENCE_CERT_NO_SEMANTIC",
        persistence_certificate.get(
            "semantic_processing_performed"
        )
        is False,
    )

    uucd_path = Path(
        persistence_result[
            "uucd_path"
        ]
    )

    check(
        "PERSISTED_UUCD_FILE_EXISTS",
        uucd_path.exists(),
    )

    persisted_disk = json.loads(
        uucd_path.read_text(
            encoding="utf-8"
        )
    )

    check(
        "PERSISTED_DISK_HAS_NO_CONTENT_BODY",
        "content_body"
        not in persisted_disk,
    )


    print()
    print("=== I. RUNTIME BOUNDARY ===")

    validated_runtime = _validate_persisted_uucd(
        persisted
    )

    check(
        "PERSISTED_UUCD_RUNTIME_ACCEPTED",
        isinstance(
            validated_runtime,
            dict,
        ),
    )

    runtime_payload = build_uucd_runtime_payload_v1(
        persisted
    )

    expected_runtime_fields = {
        "document_id",
        "content_ref",
        "body_ref",
        "source_type",
        "content_hash",
        "persistence_fingerprint",
    }

    check(
        "RUNTIME_PAYLOAD_FIELDS_EXACT",
        set(
            runtime_payload.keys()
        )
        == expected_runtime_fields,
    )

    check(
        "RUNTIME_PAYLOAD_HAS_NO_CONTENT_BODY",
        "content_body"
        not in runtime_payload,
    )

    check(
        "RUNTIME_DOCUMENT_ID_PRESERVED",
        runtime_payload[
            "document_id"
        ]
        == persisted[
            "document_id"
        ],
    )

    check(
        "RUNTIME_CONTENT_REF_PRESERVED",
        runtime_payload[
            "content_ref"
        ]
        == persisted[
            "content_ref"
        ],
    )

    check(
        "RUNTIME_BODY_REF_PRESERVED",
        runtime_payload[
            "body_ref"
        ]
        == persisted[
            "body_ref"
        ],
    )

    check(
        "RUNTIME_CONTENT_HASH_PRESERVED",
        runtime_payload[
            "content_hash"
        ]
        == persisted[
            "content_hash"
        ],
    )


    print()
    print("=== J. INVALID PERSISTED STATE REJECTION ===")

    bad_persisted = deepcopy(
        persisted
    )

    bad_persisted[
        "body_status"
    ] = "PENDING_BODY_STORE_WRITE"

    reject_check(
        "BAD_PERSISTED_BODY_STATUS_REJECTED",
        lambda: _validate_persisted_uucd(
            bad_persisted
        ),
        (
            UUCDRuntimeHandoffContractError,
        ),
    )

    bad_persisted = deepcopy(
        persisted
    )

    bad_persisted[
        "content_body"
    ] = BODY

    reject_check(
        "PERSISTED_CONTENT_BODY_REJECTED",
        lambda: _validate_persisted_uucd(
            bad_persisted
        ),
        (
            UUCDRuntimeHandoffContractError,
        ),
    )


print()
print("=== K. WEBSITE / SEMANTIC BOUNDARY ===")

website_engine = Path(
    "backend/server/website_unified_content/"
    "website_unified_content_engine_v1.py"
)

check(
    "WEBSITE_ENGINE_STILL_EXISTS",
    website_engine.exists(),
)

check(
    "UDUC_METADATA_NO_SEMANTIC_PROCESSING",
    envelope[
        "uucd_record"
    ][
        "metadata"
    ].get(
        "semantic_processing_performed"
    )
    is False,
)


print()
print("=== L. FINAL U9.21 DECISION ===")

passed = sum(
    1
    for _,
    value
    in checks
    if value
)

print(
    "TOTAL_U9_21_CHECKS="
    + str(
        len(
            checks
        )
    )
)

print(
    "TOTAL_U9_21_CHECKS_PASSED="
    + str(
        passed
    )
)

print(
    "ALL_U9_21_CHECKS_PASSED="
    + str(
        all(
            value
            for _,
            value
            in checks
        )
    )
)

failed = [
    name
    for name,
    value
    in checks
    if not value
]

print(
    "FAILED_U9_21_CHECKS="
    + repr(
        failed
    )
)

if not failed:
    print(
        "U9.21_NEXT_STEP=CERTIFY_BEHAVIORAL_UUCD"
    )
else:
    print(
        "U9.21_NEXT_STEP=INVESTIGATE_FAILED_CHECKS"
    )