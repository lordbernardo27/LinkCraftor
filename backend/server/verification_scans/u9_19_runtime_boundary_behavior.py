from copy import deepcopy

from backend.server.runtime.uucd_runtime_handoff_v1 import (
    _validate_persisted_uucd,
    build_uucd_runtime_payload_v1,
    UUCDRuntimeHandoffContractError,
)

print("=== U9.19 RUNTIME BOUNDARY BEHAVIOR ===")

base = {
    "workspace_id": "ws_u9_19",
    "document_id": "uucd_0123456789abcdef0123456789abcdef",
    "source_type": "uploaded_document",
    "content_ref": "content_ref_u9_19",
    "body_ref": "body_ref_u9_19",
    "content_hash": "a" * 64,
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
        "input_record_sha256": "b" * 64,
    },
}

original = deepcopy(base)

checks = []

print()
print("=== A. VALID PERSISTED UUCD ===")

validated = _validate_persisted_uucd(
    base
)

checks.append(
    isinstance(
        validated,
        dict,
    )
)

print(
    "VALID_PERSISTED_UUCD_ACCEPTED="
    + str(checks[-1])
)


print()
print("=== B. BODY STATUS GATE ===")

case = deepcopy(base)
case["body_status"] = "PENDING_BODY_STORE_WRITE"

try:
    _validate_persisted_uucd(case)
    rejected = False
except UUCDRuntimeHandoffContractError:
    rejected = True

checks.append(rejected)

print(
    "PRE_BODY_STORE_UUCD_REJECTED="
    + str(rejected)
)


print()
print("=== C. PERSISTENCE STATUS GATES ===")

case = deepcopy(base)
case["metadata"]["persistence_status"] = "READY_FOR_UUCD_PERSISTENCE"

try:
    _validate_persisted_uucd(case)
    rejected = False
except UUCDRuntimeHandoffContractError:
    rejected = True

checks.append(rejected)

print(
    "UNPERSISTED_METADATA_STATE_REJECTED="
    + str(rejected)
)

case = deepcopy(base)
case["persistence"]["persistence_status"] = "READY_FOR_UUCD_PERSISTENCE"

try:
    _validate_persisted_uucd(case)
    rejected = False
except UUCDRuntimeHandoffContractError:
    rejected = True

checks.append(rejected)

print(
    "UNPERSISTED_PERSISTENCE_STATE_REJECTED="
    + str(rejected)
)


print()
print("=== D. HANDOFF ELIGIBILITY ===")

case = deepcopy(base)
case["handoff"]["uucd_persisted"] = False

try:
    _validate_persisted_uucd(case)
    rejected = False
except UUCDRuntimeHandoffContractError:
    rejected = True

checks.append(rejected)

print(
    "UUCD_PERSISTED_FALSE_REJECTED="
    + str(rejected)
)

case = deepcopy(base)
case["handoff"]["body_store_verified"] = False

try:
    _validate_persisted_uucd(case)
    rejected = False
except UUCDRuntimeHandoffContractError:
    rejected = True

checks.append(rejected)

print(
    "BODY_STORE_UNVERIFIED_REJECTED="
    + str(rejected)
)

case = deepcopy(base)
case["handoff"]["next_stage"] = "uucd_persistence"

try:
    _validate_persisted_uucd(case)
    rejected = False
except UUCDRuntimeHandoffContractError:
    rejected = True

checks.append(rejected)

print(
    "WRONG_NEXT_STAGE_REJECTED="
    + str(rejected)
)


print()
print("=== E. CONTENT BODY EXCLUSION ===")

case = deepcopy(base)
case["content_body"] = "FORBIDDEN BODY"

try:
    _validate_persisted_uucd(case)
    rejected = False
except UUCDRuntimeHandoffContractError:
    rejected = True

checks.append(rejected)

print(
    "PERSISTED_UUCD_CONTENT_BODY_REJECTED="
    + str(rejected)
)

case = deepcopy(base)
case["persistence"]["content_body_stored_here"] = True

try:
    _validate_persisted_uucd(case)
    rejected = False
except UUCDRuntimeHandoffContractError:
    rejected = True

checks.append(rejected)

print(
    "PERSISTENCE_BODY_STORED_HERE_TRUE_REJECTED="
    + str(rejected)
)


print()
print("=== F. REFERENCE-ONLY RUNTIME PAYLOAD ===")

payload = build_uucd_runtime_payload_v1(
    base
)

expected_fields = {
    "document_id",
    "content_ref",
    "body_ref",
    "source_type",
    "content_hash",
    "persistence_fingerprint",
}

checks.append(
    set(payload.keys())
    == expected_fields
)

print(
    "RUNTIME_PAYLOAD_FIELDS_EXACT="
    + str(checks[-1])
)

checks.append(
    "content_body"
    not in payload
)

print(
    "RUNTIME_PAYLOAD_HAS_NO_CONTENT_BODY="
    + str(checks[-1])
)

checks.append(
    payload["content_ref"]
    == base["content_ref"]
)

print(
    "CONTENT_REF_PRESERVED="
    + str(checks[-1])
)

checks.append(
    payload["body_ref"]
    == base["body_ref"]
)

print(
    "BODY_REF_PRESERVED="
    + str(checks[-1])
)


print()
print("=== G. INPUT IMMUTABILITY ===")

checks.append(
    base == original
)

print(
    "PERSISTED_UUCD_MUTATED="
    + str(
        base != original
    )
)


print()
print("=== H. UPLOADED DOCUMENT COORDINATOR BOUNDARY ===")

from pathlib import Path

coordinator_path = Path(
    "backend/server/pipelines/upload_document/coordinator.py"
)

coordinator_source = coordinator_path.read_text(
    encoding="utf-8-sig"
)

runtime_tokens = [
    "handoff_persisted_uucd_to_runtime_v1",
    "build_uucd_runtime_payload_v1",
    "create_universal_job",
    "create_orchestration_job",
]

runtime_calls_present = any(
    token in coordinator_source
    for token in runtime_tokens
)

checks.append(
    runtime_calls_present is False
)

print(
    "UPLOADED_DOCUMENT_COORDINATOR_RUNTIME_CALL_PRESENT="
    + str(runtime_calls_present)
)


print()
print("=== I. FINAL U9.19 DECISION ===")

print(
    "TOTAL_U9_19_CHECKS="
    + str(len(checks))
)

print(
    "TOTAL_U9_19_CHECKS_PASSED="
    + str(
        sum(
            1
            for check in checks
            if check
        )
    )
)

print(
    "ALL_U9_19_CHECKS_PASSED="
    + str(
        all(checks)
    )
)

print(
    "U9.19_NEXT_STEP=CERTIFY_RUNTIME_BOUNDARY"
)