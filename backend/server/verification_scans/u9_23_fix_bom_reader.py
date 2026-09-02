from pathlib import Path

path = Path(
    r"backend/server/verification_scans/u9_23_phase_u9_certification.py"
)

text = path.read_text(
    encoding="utf-8-sig"
)

old = '''def read_text(path: Path) -> str:
    return path.read_text(
        encoding="utf-8-sig"
    )
'''

new = '''def read_text(path: Path) -> str:
    raw = path.read_bytes()

    if raw.startswith(b"\\xff\\xfe"):
        return raw.decode("utf-16-le").lstrip("\\ufeff")

    if raw.startswith(b"\\xfe\\xff"):
        return raw.decode("utf-16-be").lstrip("\\ufeff")

    if raw.startswith(b"\\xef\\xbb\\xbf"):
        return raw.decode("utf-8-sig")

    return raw.decode("utf-8")
'''

if old not in text:
    raise RuntimeError(
        "Expected U9.23 read_text helper was not found."
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

print("U9.23_PATCH_STATUS=BOM_AWARE_LOG_READER_ADDED")