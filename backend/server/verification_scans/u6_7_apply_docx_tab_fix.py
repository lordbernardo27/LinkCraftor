from pathlib import Path

path = Path(
    r"C:\Users\HP\Documents\LinkCraftor\backend\server\stores\upload_document_extractor.py"
)

raw = path.read_bytes()

newline = b"\r\n" if b"\r\n" in raw else b"\n"

text = raw.decode("utf-8")

normalized = text.replace("\r\n", "\n")

old = '''            gap = pxml[pos:m.start()]
            if "\\n" in gap:
                parts.append("\\n")
            parts.append(html_lib.unescape(m.group(1)))
            pos = m.end()
        if "\\n" in pxml[pos:]:
            parts.append("\\n")
'''

new = '''            gap = pxml[pos:m.start()]
            if "\\n" in gap:
                parts.append("\\n")
            elif " " in gap:
                parts.append(" ")
            parts.append(html_lib.unescape(m.group(1)))
            pos = m.end()

        trailing_gap = pxml[pos:]
        if "\\n" in trailing_gap:
            parts.append("\\n")
        elif " " in trailing_gap:
            parts.append(" ")
'''

count = normalized.count(old)

print(f"MATCH_COUNT={count}")

if count != 1:
    raise RuntimeError(
        "Expected exactly one DOCX reconstruction block. No patch applied."
    )

updated = normalized.replace(old, new, 1)

if newline == b"\r\n":
    updated = updated.replace("\n", "\r\n")

path.write_bytes(updated.encode("utf-8"))

print("U6.7_DOCX_TAB_FIX_APPLIED: YES")