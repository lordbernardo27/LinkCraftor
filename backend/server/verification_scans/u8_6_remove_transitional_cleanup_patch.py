from pathlib import Path
import shutil


path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

backup = Path(
    "backend/server/backups/"
    "u8_6_remove_transitional_content_cleanup/"
    "uploaded_document_unified_content.py"
)

backup.parent.mkdir(
    parents=True,
    exist_ok=True,
)

shutil.copy2(
    path,
    backup,
)

print(
    "U8.6_BACKUP_CREATED: YES"
)


source = path.read_text(
    encoding="utf-8-sig",
)


# ============================================================
# 1. REMOVE OBSOLETE _as_list HELPER
# ============================================================

old_as_list = '''def _as_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, tuple):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


'''

if old_as_list not in source:
    raise RuntimeError(
        "U8.6 could not locate obsolete _as_list helper."
    )

source = source.replace(
    old_as_list,
    "",
    1,
)


# ============================================================
# 2. PRESERVE EXACT PARAGRAPH MATCH TEXT
# ============================================================

old_paragraph_line = (
    "        block = m.group(0).strip()\n"
)

new_paragraph_line = (
    "        block = m.group(0)\n"
)

if old_paragraph_line not in source:
    raise RuntimeError(
        "U8.6 could not locate paragraph strip."
    )

source = source.replace(
    old_paragraph_line,
    new_paragraph_line,
    1,
)


old_fallback = '''    if not paragraphs and raw.strip():
        block = raw.strip()
'''

new_fallback = '''    if not paragraphs and raw:
        block = raw
'''

if old_fallback not in source:
    raise RuntimeError(
        "U8.6 could not locate paragraph fallback strip."
    )

source = source.replace(
    old_fallback,
    new_fallback,
    1,
)


# ============================================================
# 3. PRESERVE EXACT U7 HEADING IDENTITY
# ============================================================

old_heading = '''        h = str(heading or "").strip()
        if not h:
            continue
'''

new_heading = '''        h = heading
        if not h:
            continue
'''

if old_heading not in source:
    raise RuntimeError(
        "U8.6 could not locate heading-map strip."
    )

source = source.replace(
    old_heading,
    new_heading,
    1,
)


path.write_text(
    source,
    encoding="utf-8",
)


# ============================================================
# 4. STATIC ASSERTIONS
# ============================================================

patched = path.read_text(
    encoding="utf-8-sig",
)

if "def _as_list(" in patched:
    raise RuntimeError(
        "Obsolete _as_list helper still exists."
    )

if "block = m.group(0).strip()" in patched:
    raise RuntimeError(
        "Paragraph structural strip still exists."
    )

if "block = raw.strip()" in patched:
    raise RuntimeError(
        "Paragraph fallback strip still exists."
    )

if 'h = str(heading or "").strip()' in patched:
    raise RuntimeError(
        "Heading-map structural strip still exists."
    )

if "h1 = str(" not in patched:
    raise RuntimeError(
        "H1 compatibility block was unexpectedly removed."
    )


print(
    "U8.6_OBSOLETE_AS_LIST_REMOVED: YES"
)

print(
    "U8.6_PARAGRAPH_TEXT_RENORMALIZATION_REMOVED: YES"
)

print(
    "U8.6_HEADING_MAP_RENORMALIZATION_REMOVED: YES"
)

print(
    "U8.6_H1_COMPATIBILITY_DEFERRED_UNCHANGED: YES"
)

print(
    "U8.6_PATCH_APPLICATION: COMPLETE"
)

print(
    "U8.6_NEXT_STEP: STRUCTURAL_PARITY_AND_OFFSET_VERIFICATION"
)