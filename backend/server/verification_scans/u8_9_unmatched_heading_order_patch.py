from pathlib import Path
import shutil


path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

backup = Path(
    "backend/server/backups/"
    "u8_9_unmatched_heading_document_order_fix/"
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
    "U8.9_BACKUP_CREATED: YES"
)


source = path.read_text(
    encoding="utf-8-sig",
)


old_declaration = '''    ordered: List[tuple[int, Dict[str, Any]]] = []
'''

new_declaration = '''    ordered: List[
        tuple[int, int, Dict[str, Any]]
    ] = []
'''

if old_declaration not in source:
    raise RuntimeError(
        "U8.9 could not locate document-order declaration."
    )

source = source.replace(
    old_declaration,
    new_declaration,
    1,
)


old_heading_append = '''        ordered.append(
            (
                pos if isinstance(pos, int) else -1,
                {
                    "type": "heading",
                    "index": h.get("index"),
                    "text": h.get("heading"),
                    "char_position": h.get("char_position"),
                },
            )
        )
'''

new_heading_append = '''        ordered.append(
            (
                0 if isinstance(pos, int) else 1,
                pos if isinstance(pos, int) else 0,
                {
                    "type": "heading",
                    "index": h.get("index"),
                    "text": h.get("heading"),
                    "char_position": h.get("char_position"),
                },
            )
        )
'''

if old_heading_append not in source:
    raise RuntimeError(
        "U8.9 could not locate heading order append block."
    )

source = source.replace(
    old_heading_append,
    new_heading_append,
    1,
)


old_paragraph_append = '''        ordered.append(
            (
                int(p.get("start_char") or 0),
                {
                    "type": "paragraph",
                    "index": p.get("index"),
                    "text_preview": str(p.get("text") or "")[:160],
                    "start_char": p.get("start_char"),
                    "word_count": p.get("word_count"),
                },
            )
        )
'''

new_paragraph_append = '''        ordered.append(
            (
                0,
                int(p.get("start_char") or 0),
                {
                    "type": "paragraph",
                    "index": p.get("index"),
                    "text_preview": str(p.get("text") or "")[:160],
                    "start_char": p.get("start_char"),
                    "word_count": p.get("word_count"),
                },
            )
        )
'''

if old_paragraph_append not in source:
    raise RuntimeError(
        "U8.9 could not locate paragraph order append block."
    )

source = source.replace(
    old_paragraph_append,
    new_paragraph_append,
    1,
)


old_sort = '''    # Headings sort just before the paragraph that contains them (same
    # position): stable sort with heading entries added first achieves that.
    ordered.sort(key=lambda t: t[0])
    document_order = [item for _, item in ordered]
'''

new_sort = '''    # Positioned entries sort by their real content position.
    # Stable ordering keeps headings before paragraphs at equal positions
    # because heading entries are added first.
    #
    # Unmatched headings retain char_position=None and sort after all
    # positioned content rather than receiving a synthetic document position.
    ordered.sort(
        key=lambda item: (
            item[0],
            item[1],
        )
    )

    document_order = [
        item
        for _, _, item in ordered
    ]
'''

if old_sort not in source:
    raise RuntimeError(
        "U8.9 could not locate document-order sort block."
    )

source = source.replace(
    old_sort,
    new_sort,
    1,
)


path.write_text(
    source,
    encoding="utf-8",
)


patched = path.read_text(
    encoding="utf-8-sig",
)


if "pos if isinstance(pos, int) else -1" in patched:
    raise RuntimeError(
        "Legacy unmatched-heading -1 sentinel still exists."
    )

if "for _, _, item in ordered" not in patched:
    raise RuntimeError(
        "New document-order tuple contract was not installed."
    )

if '"char_position": h.get("char_position")' not in patched:
    raise RuntimeError(
        "Heading char_position preservation was unexpectedly altered."
    )


print(
    "U8.9_UNMATCHED_NEGATIVE_SENTINEL_REMOVED: YES"
)

print(
    "U8.9_REAL_POSITION_ORDER_PRESERVED: YES"
)

print(
    "U8.9_UNMATCHED_HEADING_CHAR_POSITION_REMAINS_NONE: YES"
)

print(
    "U8.9_UNMATCHED_HEADINGS_SORT_AFTER_POSITIONED_CONTENT: YES"
)

print(
    "U8.9_PATCH_APPLICATION: COMPLETE"
)

print(
    "U8.9_NEXT_STEP: DOCUMENT_ORDER_REGRESSION_VERIFICATION"
)