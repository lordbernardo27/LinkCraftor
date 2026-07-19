from pathlib import Path
import re


path = Path(
    "backend/server/stores/udare_store.py"
)

text = path.read_text(
    encoding="utf-8-sig"
)

pattern = re.compile(
    r"""
    FORBIDDEN_OPERATIONAL_METADATA_KEYS
    \s*
    \r?\n
    \s*
    =
    \s*
    \{
    """,
    re.VERBOSE,
)

replacement = (
    "FORBIDDEN_OPERATIONAL_METADATA_KEYS = {"
)

updated_text, replacement_count = (
    pattern.subn(
        replacement,
        text,
        count=1,
    )
)

if replacement_count != 1:
    raise RuntimeError(
        "Expected malformed assignment was not found. "
        "No source file was changed."
    )

path.write_text(
    updated_text,
    encoding="utf-8",
)

print(
    "LINE 76 REPAIR: PASS"
)
