from pathlib import Path
import shutil


path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

backup = Path(
    "backend/server/backups/"
    "u8_12_strict_document_identity_v2/"
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
    "U8.12_V2_BACKUP_CREATED: YES"
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
        "U8.12 V2 could not locate current _safe_document_id implementation."
    )

source = source.replace(
    old_fn,
    new_fn,
    1,
)


# ------------------------------------------------------------
# 2. Remove exact current fallback chain
# ------------------------------------------------------------

old_builder_block = '''    inferred_document_id = (
        document_id
        or src_meta.get("doc_id")
        or src_meta.get("document_id")
        or meta.get("doc_id")
        or meta.get("document_id")
        or ""
    )

    doc_id = _safe_document_id(
        inferred_document_id
    )
'''

new_builder_block = '''    doc_id = _safe_document_id(
        document_id
    )
'''

if old_builder_block not in source:
    raise RuntimeError(
        "U8.12 V2 could not locate exact document fallback block."
    )

source = source.replace(
    old_builder_block,
    new_builder_block,
    1,
)


# ------------------------------------------------------------
# 3. Write production patch
# ------------------------------------------------------------

path.write_text(
    source,
    encoding="utf-8",
)


# ------------------------------------------------------------
# 4. Static assertions
# ------------------------------------------------------------

patched = path.read_text(
    encoding="utf-8-sig",
)


for forbidden in [
    'src_meta.get("doc_id")',
    'src_meta.get("document_id")',
    'meta.get("doc_id")',
    'meta.get("document_id")',
    "unknown_document",
    "inferred_document_id",
]:
    if forbidden in patched:
        raise RuntimeError(
            f"U8.12 V2 legacy document fallback still exists: {forbidden}"
        )


if "document_id is None" not in patched:
    raise RuntimeError(
        "U8.12 V2 None document guard missing."
    )

if "document_id must be non-blank." not in patched:
    raise RuntimeError(
        "U8.12 V2 blank document guard missing."
    )

if '''doc_id = _safe_document_id(
        document_id
    )''' not in patched:
    raise RuntimeError(
        "U8.12 V2 canonical document_id wiring missing."
    )


print(
    "U8.12_V2_UNKNOWN_DOCUMENT_FALLBACK_REMOVED: YES"
)

print(
    "U8.12_V2_SRC_META_DOC_ID_FALLBACK_REMOVED: YES"
)

print(
    "U8.12_V2_SRC_META_DOCUMENT_ID_FALLBACK_REMOVED: YES"
)

print(
    "U8.12_V2_META_DOC_ID_FALLBACK_REMOVED: YES"
)

print(
    "U8.12_V2_META_DOCUMENT_ID_FALLBACK_REMOVED: YES"
)

print(
    "U8.12_V2_EXTERNAL_DOCUMENT_ID_REQUIRED: YES"
)

print(
    "U8.12_V2_NONE_DOCUMENT_REJECTED: YES"
)

print(
    "U8.12_V2_BLANK_DOCUMENT_REJECTED: YES"
)

print(
    "U8.12_V2_PATH_SAFETY_SANITIZATION_PRESERVED: YES"
)

print(
    "U8.12_V2_PATCH_APPLICATION: COMPLETE"
)

print(
    "U8.12_NEXT_STEP: DOCUMENT_IDENTITY_REGRESSION_VERIFICATION"
)