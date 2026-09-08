from pathlib import Path

P = Path("certify_runtime_integration_phase_5_6_success_path.py")
S = P.read_text(encoding="utf-8")

replacements = [
    (
        '"phase_5_6_success_test"',
        '"linking_target_pipeline_batch"',
    ),
    (
        '"pipeline_phase_5_6_success"',
        '"linking_target_pipeline"',
    ),
    (
        '"phase_5_6_success_stage"',
        '"linking_target_pipeline_batch"',
    ),
]

for old, new in replacements:
    if old not in S:
        raise SystemExit(
            f"Expected verifier fixture not found: {old}"
        )
    S = S.replace(old, new, 1)

old_payload = '''PAYLOAD = {
    "document_id":
        "doc_phase_5_6_success",
}
'''

new_payload = '''PAYLOAD = {
    "workspace_id":
        WORKSPACE_ID,

    "domain":
        "phase-5-6-success.example.com",
}
'''

if old_payload not in S:
    raise SystemExit(
        "Expected PAYLOAD fixture not found. Production untouched."
    )

S = S.replace(
    old_payload,
    new_payload,
    1,
)

old_required = '''"required_payload_fields":
        (
            "document_id",
        ),'''

new_required = '''"required_payload_fields":
        (
            "workspace_id",
            "domain",
        ),'''

if old_required not in S:
    raise SystemExit(
        "Expected required_payload_fields fixture not found. Production untouched."
    )

S = S.replace(
    old_required,
    new_required,
    1,
)

old_dispatch = '''        "document_id":
            PAYLOAD[
                "document_id"
            ],'''

new_dispatch = '''        "domain":
            PAYLOAD[
                "domain"
            ],'''

if old_dispatch not in S:
    raise SystemExit(
        "Expected dispatcher payload fixture not found. Production untouched."
    )

S = S.replace(
    old_dispatch,
    new_dispatch,
    1,
)

P.write_text(
    S,
    encoding="utf-8",
)

print("5.6.5 verifier aligned to real Runtime registration")
print("Production modified: False")
