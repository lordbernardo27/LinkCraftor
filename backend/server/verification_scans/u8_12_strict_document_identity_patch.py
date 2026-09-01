from pathlib import Path
import shutil


path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

backup = Path(
    "backend/server/backups/"
    "u8_12_strict_document_identity/"
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
    "U8.12_BACKUP_CREATED: YES"
)


source = path.read_text(
    encoding="utf-8-sig",
)


# ------------------------------------------------------------
# 1. Tighten _safe_document_id
# ------------------------------------------------------------

old_fn = '''def _safe_document_id(document_id: str | None, fallback: str = "") -> str:
    raw = str(document_id or fallback or "").strip()
    if not raw:
        raw = "unknown_document"
    raw = re.sub(r"[^a-zA-Z0-9_\\-]", "_", raw)
    return raw[:120]
'''

new_fn = '''def _safe_document_id(document_id: str | None) -> str:
    if document_id is None:
        raise ValueError(
            "document_id is required."
        )

    raw = str(document_id).strip()

    if not raw:
        raise ValueError(
            "document_id must be non-blank."
        )

    raw = re.sub(
        r"[^a-zA-Z0-9_\\-]",
        "_",
        raw,
    )

    if not raw:
        raise ValueError(
            "document_id is invalid after sanitization."
        )

    return raw[:120]
'''

if old_fn not in source:
    raise RuntimeError(
        "U8.12 could not locate current _safe_document_id implementation."
    )

source = source.replace(
    old_fn,
    new_fn,
    1,
)


# ------------------------------------------------------------
# 2. Remove canonical builder fallback chain
# ------------------------------------------------------------

old_builder_block = '''    inferred_document_id = (
        document_id
        or src_meta.get("document_id")
        or meta.get("document_id")
    )

    doc_id = _safe_document_id(
        inferred_document_id
        or "uploaded_document"
    )
'''

new_builder_block = '''    doc_id = _safe_document_id(
        document_id
    )
'''

if old_builder_block not in source:
    raise RuntimeError(
        "U8.12 could not locate canonical document fallback block."
    )

source = source.replace(
    old_builder_block,
    new_builder_block,
    1,
)


path.write_text(
    source,
    encoding="utf-8",
)


# ------------------------------------------------------------
# 3. Static assertions
# ------------------------------------------------------------

patched = path.read_text(
    encoding="utf-8-sig",
)


if "unknown_document" in patched:
    raise RuntimeError(
        "Legacy unknown_document fallback still exists."
    )

if 'or src_meta.get("document_id")' in patched:
    raise RuntimeError(
        "Source metadata document_id fallback still exists."
    )

if 'or meta.get("document_id")' in patched:
    raise RuntimeError(
        "Metadata document_id fallback still exists."
    )

if 'or "uploaded_document"' in patched:
    raise RuntimeError(
        "Synthetic uploaded_document identity fallback still exists."
    )

if "document_id is None" not in patched:
    raise RuntimeError(
        "None document rejection was not installed."
    )

if "document_id must be non-blank." not in patched:
    raise RuntimeError(
        "Blank document rejection was not installed."
    )

if "doc_id = _safe_document_id(" not in patched:
    raise RuntimeError(
        "Canonical document safety helper is not wired."
    )


print(
    "U8.12_UNKNOWN_DOCUMENT_FALLBACK_REMOVED: YES"
)

print(
    "U8.12_METADATA_DOCUMENT_FALLBACK_REMOVED: YES"
)

print(
    "U8.12_SOURCE_METADATA_DOCUMENT_FALLBACK_REMOVED: YES"
)

print(
    "U8.12_SYNTHETIC_UPLOADED_DOCUMENT_FALLBACK_REMOVED: YES"
)

print(
    "U8.12_NONE_DOCUMENT_REJECTED: YES"
)

print(
    "U8.12_BLANK_DOCUMENT_REJECTED: YES"
)

print(
    "U8.12_EXTERNAL_DOCUMENT_ID_REQUIRED: YES"
)

print(
    "U8.12_PATH_SAFETY_SANITIZATION_PRESERVED: YES"
)

print(
    "U8.12_PATCH_APPLICATION: COMPLETE"
)

print(
    "U8.12_NEXT_STEP: DOCUMENT_IDENTITY_REGRESSION_VERIFICATION"
)