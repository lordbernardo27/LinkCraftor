from pathlib import Path
import shutil


path = Path(
    "backend/server/stores/"
    "uploaded_document_unified_content.py"
)

backup = Path(
    "backend/server/backups/"
    "u8_16_h1_contract/"
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
    "U8.16_BACKUP_CREATED: YES"
)


source = path.read_text(
    encoding="utf-8-sig",
)


old_block = '''    # Existing H1 compatibility behavior remains temporarily.
    # U8.16 owns the final H1 contract decision.
    h1 = str(
        meta.get("h1")
        or src_meta.get("h1")
        or (
            headings[0]
            if headings
            else title
        )
        or ""
    ).strip()
'''

new_block = '''    # Canonical H1 is a structural compatibility field derived
    # only from U7-normalized content.
    h1 = (
        headings[0]
        if headings
        else title
    )
'''


if old_block not in source:
    raise RuntimeError(
        "U8.16 could not locate exact legacy H1 block."
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


if new_block not in patched:
    raise RuntimeError(
        "U8.16 canonical H1 block was not installed."
    )


for forbidden in [
    'meta.get("h1")',
    'src_meta.get("h1")',
]:
    canonical_start = patched.find(
        "def build_uduc_from_normalized_content"
    )

    canonical_end = patched.find(
        "\ndef ",
        canonical_start + 1,
    )

    if canonical_end == -1:
        canonical_end = len(
            patched
        )

    canonical_builder = patched[
        canonical_start:canonical_end
    ]

    if forbidden in canonical_builder:
        raise RuntimeError(
            "U8.16 legacy H1 authority still exists "
            f"in canonical builder: {forbidden}"
        )


if ").strip()" in new_block:
    raise RuntimeError(
        "U8.16 H1 block unexpectedly performs cleanup."
    )


print(
    "U8.16_METADATA_H1_AUTHORITY_REMOVED: YES"
)

print(
    "U8.16_SOURCE_METADATA_H1_AUTHORITY_REMOVED: YES"
)

print(
    "U8.16_CANONICAL_H1_PRIMARY: FIRST_U7_NORMALIZED_HEADING"
)

print(
    "U8.16_CANONICAL_H1_FALLBACK: U7_NORMALIZED_TITLE"
)

print(
    "U8.16_H1_EXTRA_CLEANUP_REMOVED: YES"
)

print(
    "U8.16_H1_CONTRACT_PATCH: COMPLETE"
)

print(
    "U8.16_NEXT_STEP: H1_CONTRACT_REGRESSION_VERIFICATION"
)