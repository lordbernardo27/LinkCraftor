from pathlib import Path
import shutil


path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

backup = Path(
    "backend/server/backups/"
    "u8_14_file_size_provenance/"
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
    "U8.14_BACKUP_CREATED: YES"
)


source = path.read_text(
    encoding="utf-8-sig",
)


old_block = '''    file_size = (
        src_meta.get("file_size")
        or src_meta.get("bytes")
        or None
    )
'''

new_block = '''    if meta.get("file_size") is not None:
        file_size = meta.get("file_size")
    elif src_meta.get("file_size") is not None:
        file_size = src_meta.get("file_size")
    elif src_meta.get("bytes") is not None:
        file_size = src_meta.get("bytes")
    else:
        file_size = None
'''


if old_block not in source:
    raise RuntimeError(
        "U8.14 could not locate exact file_size block."
    )


source = source.replace(
    old_block,
    new_block,
    1,
)


path.write_text(
    source,
    encoding="utf-8",
)


patched = path.read_text(
    encoding="utf-8-sig",
)


expected = '''    if meta.get("file_size") is not None:
        file_size = meta.get("file_size")
    elif src_meta.get("file_size") is not None:
        file_size = src_meta.get("file_size")
    elif src_meta.get("bytes") is not None:
        file_size = src_meta.get("bytes")
    else:
        file_size = None
'''


if expected not in patched:
    raise RuntimeError(
        "U8.14 file_size precedence patch not installed."
    )


print(
    "U8.14_CANONICAL_FILE_SIZE_KEY_ADDED: YES"
)

print(
    "U8.14_SOURCE_METADATA_FILE_SIZE_FALLBACK_PRESERVED: YES"
)

print(
    "U8.14_LEGACY_BYTES_FALLBACK_PRESERVED: YES"
)

print(
    "U8.14_ZERO_BYTE_VALUE_PRESERVATION: YES"
)

print(
    "U8.14_FILE_SIZE_PROVENANCE_PATCH: COMPLETE"
)

print(
    "U8.14_NEXT_STEP: EXTRACTION_PROVENANCE_REGRESSION_VERIFICATION"
)