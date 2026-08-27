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

count = text.count(old)

if count != 1:
    raise RuntimeError(
        "Expected exactly one UDUC index reread block, "
        f"found {count}. No production file written."
    )

text = text.replace(old, new, 1)


# ------------------------------------------------------------
# 3. Replace original-filename legacy/index fallback.
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

count = text.count(old)

if count != 1:
    raise RuntimeError(
        "Expected exactly one original-name index fallback, "
        f"found {count}. No production file written."
    )

text = text.replace(old, new, 1)


# ------------------------------------------------------------
# 4. Replace stored-name legacy/index fallback.
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

count = text.count(old)

if count != 1:
    raise RuntimeError(
        "Expected exactly one stored-name index fallback, "
        f"found {count}. No production file written."
    )

text = text.replace(old, new, 1)


# ------------------------------------------------------------
# 5. Replace stored-path index fallback.
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

count = text.count(old)

if count != 1:
    raise RuntimeError(
        "Expected exactly one stored-path index fallback, "
        f"found {count}. No production file written."
    )

text = text.replace(old, new, 1)


# ------------------------------------------------------------
# 6. Replace title/H1 fallback with canonical source metadata.
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

count = text.count(old)

if count != 1:
    raise RuntimeError(
        "Expected exactly one title/H1 index fallback block, "
        f"found {count}. No production file written."
    )

text = text.replace(old, new, 1)


# ------------------------------------------------------------
# 7. Replace byte-count fallback with source_metadata only.
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

count = text.count(old)

if count != 1:
    raise RuntimeError(
        "Expected exactly one file-size index fallback, "
        f"found {count}. No production file written."
    )

text = text.replace(old, new, 1)


# ------------------------------------------------------------
# Safety assertions.
# ------------------------------------------------------------

for forbidden in (
    "_read_upload_index_hit",
    '"uploads" / workspace_id / "index.json"',
    "index_hit",
):
    if forbidden in text:
        raise RuntimeError(
            f"Forbidden UDUC registry fallback residue remains: "
            f"{forbidden!r}. No production file written."
        )


path.write_text(
    text.replace("\n", newline),
    encoding="utf-8",
    newline="",
)

print("U3.11_UDUC_HANDOFF_REALIGNMENT: APPLIED")