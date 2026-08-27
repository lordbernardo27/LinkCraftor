from pathlib import Path

path = Path(r"backend/server/routes/files.py")

raw = path.read_text(encoding="utf-8")
newline = "\r\n" if "\r\n" in raw else "\n"
text = raw.replace("\r\n", "\n")

old = '''    elif ext == ".md":
        md = _decode_text_bytes(raw)
'''

new = '''    elif ext in (".md", ".markdown"):
        md = _decode_text_bytes(raw)
'''

count = text.count(old)

if count != 1:
    raise RuntimeError(
        f"Expected exactly one Markdown preview branch, found {count}. "
        "No production file written."
    )

text = text.replace(old, new, 1)

path.write_text(
    text.replace("\n", newline),
    encoding="utf-8",
    newline="",
)

print("U3.10_MARKDOWN_PREVIEW_ALIGNMENT: APPLIED")