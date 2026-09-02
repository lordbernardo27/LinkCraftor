from backend.server.runtime.uucd_runtime_handoff_v1 import (
    _validate_persisted_uucd,
    UUCDRuntimeHandoffContractError,
)

base = {
    "workspace_id": "ws_test",
    "document_id": "uucd_0123456789abcdef0123456789abcdef",
    "source_type": "uploaded_document",
    "content_ref": "content_ref_test",
    "body_ref": "body_ref_test",
    "content_hash": (
        "a" * 64
    ),
    "body_status": "STORED_AND_VERIFIED",
    "metadata": {
        "persistence_status": "PERSISTED_AND_VERIFIED",
    },
    "handoff": {
        "uucd_persisted": True,
        "next_stage": "runtime_queue_handoff",
        "body_store_verified": True,
    },
    "persistence": {
        "persistence_status": "PERSISTED_AND_VERIFIED",
        "content_body_stored_here": False,
        "input_record_sha256": (
            "b" * 64
        ),
    },
}

print("=== U9.19 BODY STATUS GATE TEST ===")

valid = _validate_persisted_uucd(
    base
)

print(
    "VALID_BODY_STATUS_ACCEPTED="
    + str(
        isinstance(
            valid,
            dict,
        )
    )
)

invalid = dict(
    base
)

invalid["body_status"] = (
    "PENDING_BODY_STORE_WRITE"
)

try:
    _validate_persisted_uucd(
        invalid
    )

    print(
        "INVALID_BODY_STATUS_REJECTED=False"
    )

except UUCDRuntimeHandoffContractError as exc:
    print(
        "INVALID_BODY_STATUS_REJECTED=True"
    )
    print(
        "ERROR_TYPE="
        + type(exc).__name__
    )
    print(
        "ERROR="
        + str(exc)
    )