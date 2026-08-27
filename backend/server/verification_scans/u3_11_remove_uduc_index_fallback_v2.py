from pathlib import Path

path = Path(
    r"backend/server/stores/uploaded_document_unified_content.py"
)

raw = path.read_text(encoding="utf-8")
newline = "\r\n" if "\r\n" in raw else "\n"
text = raw.replace("\r\n", "\n")


# ------------------------------------------------------------
# 1. Remove obsolete registry reread helper.
# ------------------------------------------------------------

start_marker = (
    "def _read_upload_index_hit("
    "workspace_id: str, document_id: str"
    ") -> Dict[str, Any]:\n"
)

end_marker = (
    "def _paragraphs_from_content_body("
    "content_body: str"
    ") -> List[Dict[str, Any]]:\n"
)

start = text.find(start_marker)
end = text.find(end_marker)

if start < 0:
    raise RuntimeError(
        "_read_upload_index_hit() definition not found. "
        "No production file written."
    )

if end < 0 or end <= start:
    raise RuntimeError(
        "Could not determine safe end of "
        "_read_upload_index_hit() helper. "
        "No production file written."
    )

text = text[:start] + text[end:]


# ------------------------------------------------------------
# 2. Remove unconditional index reread.
# ------------------------------------------------------------

old = '''    index_hit = _read_upload_index_hit(ws, doc_id) if doc_id != "unknown_document" else {}

    source_path = str(er.get("source_path") or stored_path or index_hit.get("stored_path") or "")
'''

new = '''    source_path = str(
        er.get("source_path")
        or stored_path
        or src_meta.get("stored_path")
        or ""
    )
'''

if text.count(old) != 1:
    raise RuntimeError(
        "Canonical UDUC index-reread block was not found exactly once. "
        "No production file written."
    )

text = text.replace(old, new, 1)


# ------------------------------------------------------------
# 3. Original filename.
# ------------------------------------------------------------

old = '''    original_name = (
        original_filename
        or src_meta.get("original_filename")
        or src_meta.get("filename")
        or meta.get("filename")
        or index_hit.get("filename")
        or Path(source_path).name
        or ""
    )
'''

new = '''    original_name = (
        original_filename
        or src_meta.get("original_filename")
        or src_meta.get("filename")
        or meta.get("filename")
        or Path(source_path).name
        or ""
    )
'''

if text.count(old) != 1:
    raise RuntimeError(
        "Original-filename fallback block was not found exactly once. "
        "No production file written."
    )

text = text.replace(old, new, 1)


# ------------------------------------------------------------
# 4. Stored filename.
# ------------------------------------------------------------

old = '''    stored_name = (
        stored_filename
        or src_meta.get("stored_filename")
        or src_meta.get("stored_name")
        or meta.get("stored_filename")
        or meta.get("stored_name")
        or index_hit.get("stored_name")
        or Path(source_path).name
        or ""
    )
'''

new = '''    stored_name = (
        stored_filename
        or src_meta.get("stored_filename")
        or src_meta.get("stored_name")
        or meta.get("stored_filename")
        or meta.get("stored_name")
        or Path(source_path).name
        or ""
    )
'''

if text.count(old) != 1:
    raise RuntimeError(
        "Stored-filename fallback block was not found exactly once. "
        "No production file written."
    )

text = text.replace(old, new, 1)


# ------------------------------------------------------------
# 5. Stored source path.
# ------------------------------------------------------------

old = '''    final_stored_path = (
        stored_path
        or src_meta.get("stored_path")
        or meta.get("stored_path")
        or index_hit.get("stored_path")
        or source_path
        or ""
    )
'''

new = '''    final_stored_path = (
        stored_path
        or src_meta.get("stored_path")
        or meta.get("stored_path")
        or source_path
        or ""
    )
'''

if text.count(old) != 1:
    raise RuntimeError(
        "Stored-path fallback block was not found exactly once. "
        "No production file written."
    )

text = text.replace(old, new, 1)


# ------------------------------------------------------------
# 6. Title / H1.
# ------------------------------------------------------------

old = '''    title = str(er.get("title") or meta.get("title") or index_hit.get("h1") or "").strip()
    headings = _as_list(er.get("headings"))
    h1 = str(meta.get("h1") or index_hit.get("h1") or (headings[0] if headings else title) or "").strip()
'''

new = '''    title = str(
        er.get("title")
        or meta.get("title")
        or src_meta.get("title")
        or src_meta.get("h1")
        or ""
    ).strip()

    headings = _as_list(er.get("headings"))

    h1 = str(
        meta.get("h1")
        or src_meta.get("h1")
        or (headings[0] if headings else title)
        or ""
    ).strip()
'''

if text.count(old) != 1:
    raise RuntimeError(
        "Title/H1 fallback block was not found exactly once. "
        "No production file written."
    )

text = text.replace(old, new, 1)


# ------------------------------------------------------------
# 7. File size.
# ------------------------------------------------------------

old = '''    # FIX: file_size falls back to None (was ""), avoiding mixed int/str typing.
    file_size = src_meta.get("file_size") or src_meta.get("bytes") or index_hit.get("bytes") or None
'''

new = '''    # Canonical upload source metadata owns persisted byte-count evidence.
    file_size = (
        src_meta.get("file_size")
        or src_meta.get("bytes")
        or None
    )
'''

if text.count(old) != 1:
    raise RuntimeError(
        "File-size fallback block was not found exactly once. "
        "No production file written."
    )

text = text.replace(old, new, 1)


# ------------------------------------------------------------
# 8. Remove obsolete comment mentioning removed helper.
# ------------------------------------------------------------

lines = text.splitlines()

lines = [
    line
    for line in lines
    if "_read_upload_index_hit silently found nothing" not in line
]

text = "\n".join(lines) + "\n"


# ------------------------------------------------------------
# 9. Precise safety assertions.
# ------------------------------------------------------------

for forbidden in (
    "def _read_upload_index_hit(",
    "_read_upload_index_hit(ws, doc_id)",
    "index_hit.get(",
    'BASE_DIR / "data" / "uploads" / workspace_id / "index.json"',
):
    if forbidden in text:
        raise RuntimeError(
            "Forbidden UDUC registry fallback residue remains: "
            f"{forbidden!r}. No production file written."
        )


path.write_text(
    text.replace("\n", newline),
    encoding="utf-8",
    newline="",
)

print("U3.11_UDUC_HANDOFF_REALIGNMENT_V2: APPLIED")