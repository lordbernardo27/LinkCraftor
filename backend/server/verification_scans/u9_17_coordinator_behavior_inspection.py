import ast
from pathlib import Path

path = Path(
    "backend/server/pipelines/upload_document/"
    "coordinator.py"
)

source = path.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(
    source
)

print("=== U9.17 COORDINATOR BEHAVIOR INSPECTION ===")


print()
print("=== A. IMPORT CONTRACT ===")

import_present = (
    "build_transient_uucd_from_uduc_v1"
    in source
)

print(
    "UUCD_BUILDER_IMPORT_PRESENT="
    + str(import_present)
)


print()
print("=== B. CANONICAL INSERTION ORDER ===")

uduc_assignment = source.find(
    'uduc = uduc_result.get("uduc")'
)

uucd_build = source.find(
    "uucd_envelope = "
    "build_transient_uucd_from_uduc_v1("
)

highlight_call = source.find(
    "pipeline_1 = "
    "run_uploaded_document_to_highlight_pipeline("
)

registry_call = source.find(
    "run_uploaded_document_registry_to_active_target_set_pipeline("
)

order_ok = (
    uduc_assignment != -1
    and uucd_build != -1
    and highlight_call != -1
    and registry_call != -1
    and uduc_assignment
        < uucd_build
        < highlight_call
        < registry_call
)

print(
    "UDUC_BEFORE_UUCD="
    + str(
        uduc_assignment
        < uucd_build
    )
)

print(
    "UUCD_BEFORE_HIGHLIGHT="
    + str(
        uucd_build
        < highlight_call
    )
)

print(
    "HIGHLIGHT_BEFORE_REGISTRY_ATS="
    + str(
        highlight_call
        < registry_call
    )
)

print(
    "CANONICAL_EXECUTION_ORDER_OK="
    + str(order_ok)
)


print()
print("=== C. UUCD INPUT AUTHORITY ===")

uucd_call_segment = source[
    uucd_build:
    uucd_build + 220
]

uses_uduc_directly = (
    "build_transient_uucd_from_uduc_v1(\n"
    "        uduc\n"
    "    )"
    in uucd_call_segment
)

print(
    "UUCD_BUILDER_RECEIVES_CANONICAL_UDUC="
    + str(
        uses_uduc_directly
    )
)


print()
print("=== D. ENVELOPE GATE ===")

ready_gate = (
    'uucd_envelope.get(\n'
    '            "envelope_status"\n'
    '        )\n'
    '        != "READY_FOR_BODY_STORE"'
    in source
)

print(
    "READY_FOR_BODY_STORE_GATE_PRESENT="
    + str(
        ready_gate
    )
)


print()
print("=== E. EXISTING BRANCH PRESERVATION ===")

highlight_uses_extraction = (
    "run_uploaded_document_to_highlight_pipeline("
    in source
    and "extraction_result=highlight_extraction_result"
    in source
)

registry_uses_uduc = (
    "run_uploaded_document_registry_to_active_target_set_pipeline("
    in source
    and "unified_content=uduc"
    in source
)

print(
    "HIGHLIGHT_STILL_USES_EXTRACTION_RESULT="
    + str(
        highlight_uses_extraction
    )
)

print(
    "REGISTRY_ATS_STILL_USES_UDUC="
    + str(
        registry_uses_uduc
    )
)


print()
print("=== F. DOWNSTREAM BOUNDARY ===")

forbidden_tokens = [
    "write_body_payload",
    "write_body_store",
    "persist_finalized_uucd_v1",
    "runtime_handoff",
    "semantic_intelligence",
    "scorer.py",
]

for token in forbidden_tokens:
    print(
        "FORBIDDEN_CALL_PRESENT_"
        + token.upper().replace(".", "_")
        + "="
        + str(
            token in source
        )
    )


print()
print("=== G. RESULT EXPOSURE ===")

execution_order_present = (
    '"uploaded_document_to_current_canonical_uucd"'
    in source
)

result_exposure_present = (
    '"uploaded_document_to_current_canonical_uucd": {'
    in source
    and '"status": "READY_FOR_BODY_STORE"'
    in source
    and '"envelope": uucd_envelope'
    in source
)

print(
    "EXECUTION_ORDER_EXPOSES_U9="
    + str(
        execution_order_present
    )
)

print(
    "PIPELINE_RESULT_EXPOSES_U9_ENVELOPE="
    + str(
        result_exposure_present
    )
)


print()
print("=== H. AST CALL INSPECTION ===")

calls = []

for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        func = node.func

        if isinstance(func, ast.Name):
            calls.append(func.id)

        elif isinstance(func, ast.Attribute):
            calls.append(func.attr)

print(
    "UUCD_BUILDER_CALL_COUNT="
    + str(
        calls.count(
            "build_transient_uucd_from_uduc_v1"
        )
    )
)

print(
    "BODY_STORE_WRITER_CALL_COUNT="
    + str(
        sum(
            calls.count(name)
            for name in [
                "write_body_payload_v1",
                "write_body_payload",
                "write_body_store",
            ]
        )
    )
)

print(
    "UUCD_PERSISTENCE_CALL_COUNT="
    + str(
        calls.count(
            "persist_finalized_uucd_v1"
        )
    )
)


print()
print("=== I. FINAL U9.17 DECISION ===")

checks = [
    import_present,
    order_ok,
    uses_uduc_directly,
    ready_gate,
    highlight_uses_extraction,
    registry_uses_uduc,
    execution_order_present,
    result_exposure_present,
    calls.count(
        "build_transient_uucd_from_uduc_v1"
    ) == 1,
    calls.count(
        "persist_finalized_uucd_v1"
    ) == 0,
]

print(
    "TOTAL_U9_17_CHECKS="
    + str(
        len(checks)
    )
)

print(
    "TOTAL_U9_17_CHECKS_PASSED="
    + str(
        sum(
            1
            for check in checks
            if check
        )
    )
)

print(
    "ALL_U9_17_CHECKS_PASSED="
    + str(
        all(checks)
    )
)

print(
    "U9.17_NEXT_STEP=CERTIFY_INTEGRATION"
)