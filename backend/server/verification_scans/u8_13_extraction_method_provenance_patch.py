from pathlib import Path
import shutil


path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

backup = Path(
    "backend/server/backups/"
    "u8_13_extraction_method_provenance/"
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
    "U8.13_BACKUP_CREATED: YES"
)


source = path.read_text(
    encoding="utf-8-sig",
)


old_block = '''        "extraction_method": (
            meta.get("method")
            or meta.get("extractor")
            or ""
        ),
'''

new_block = '''        "extraction_method": (
            meta.get("extraction_method")
            or meta.get("method")
            or meta.get("extractor")
            or src_meta.get("extraction_method")
            or ""
        ),
'''


if old_block not in source:
    raise RuntimeError(
        "U8.13 could not locate exact extraction_method block."
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


expected = '''        "extraction_method": (
            meta.get("extraction_method")
            or meta.get("method")
            or meta.get("extractor")
            or src_meta.get("extraction_method")
            or ""
        ),
'''

if expected not in patched:
    raise RuntimeError(
        "U8.13 extraction_method precedence patch not installed."
    )


print(
    "U8.13_CANONICAL_EXTRACTION_METHOD_KEY_ADDED: YES"
)

print(
    "U8.13_LEGACY_METHOD_FALLBACK_PRESERVED: YES"
)

print(
    "U8.13_LEGACY_EXTRACTOR_FALLBACK_PRESERVED: YES"
)

print(
    "U8.13_SOURCE_METADATA_EXTRACTION_METHOD_FALLBACK_ADDED: YES"
)

print(
    "U8.13_EXTRACTION_METHOD_PROVENANCE_PATCH: COMPLETE"
)

print(
    "U8.13_NEXT_STEP: SOURCE_METADATA_REGRESSION_VERIFICATION"
)