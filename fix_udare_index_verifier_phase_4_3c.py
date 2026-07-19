from pathlib import Path

path = Path(
    "verify_udare_store_index_phase_4_3c.py"
)

text = path.read_text(
    encoding="utf-8-sig"
)

old = '''    "worker_call_present":
        (
            "udare_store_index_result = "
            "build_udare_store_index_v1("
        )
        in worker_text,
'''

new = '''    "worker_call_present":
        (
            "build_udare_store_index_v1("
            in worker_text
            and "index_result"
            in worker_text
        ),
'''

if old not in text:
    raise RuntimeError(
        "Verifier worker_call_present block was not found."
    )

text = text.replace(
    old,
    new,
    1,
)

path.write_text(
    text,
    encoding="utf-8",
)

print("UDARE INDEX VERIFIER FIX: PASS")
