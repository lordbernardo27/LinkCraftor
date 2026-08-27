from pathlib import Path

path = Path(
    "backend/server/stores/upload_document_extractor.py"
)

text = path.read_text(encoding="utf-8")

old_regex = '''_MD_EMPHASIS_RE = re.compile(r"(\\*\\*|__|\\*|_|`)(.+?)\\1")'''

new_regex = '''_MD_STAR_OR_CODE_RE = re.compile(
    r"(\\*\\*|\\*|`)(.+?)\\1"
)

_MD_UNDERSCORE_EMPHASIS_RE = re.compile(
    r"(?<!\\w)(__|_)(.+?)\\1(?!\\w)"
)'''

if old_regex not in text:
    raise RuntimeError(
        "Expected legacy Markdown emphasis regex was not found."
    )

text = text.replace(
    old_regex,
    new_regex,
    1,
)

old_function = '''def _strip_md_inline_v1(text: str) -> str:
    out = _MD_IMAGE_RE.sub(lambda m: m.group(1), text)   # ![alt](src) -> alt
    out = _MD_LINK_RE.sub(lambda m: m.group(1), out)     # [text](url) -> text
    prev = None
    while prev != out:  # nested emphasis: **bold *italic***
        prev = out
        out = _MD_EMPHASIS_RE.sub(lambda m: m.group(2), out)
    return out'''

new_function = '''def _strip_md_inline_v1(text: str) -> str:
    out = _MD_IMAGE_RE.sub(lambda m: m.group(1), text)   # ![alt](src) -> alt
    out = _MD_LINK_RE.sub(lambda m: m.group(1), out)     # [text](url) -> text

    # Strip real Markdown emphasis/code delimiters while preserving
    # underscores that are part of ordinary tokens such as user_id,
    # product_name, API_RESPONSE_CODE, and similar identifiers.
    prev = None

    while prev != out:  # nested emphasis: **bold *italic***
        prev = out

        out = _MD_STAR_OR_CODE_RE.sub(
            lambda m: m.group(2),
            out,
        )

        out = _MD_UNDERSCORE_EMPHASIS_RE.sub(
            lambda m: m.group(2),
            out,
        )

    return out'''

if old_function not in text:
    raise RuntimeError(
        "Expected Markdown inline-strip implementation was not found."
    )

text = text.replace(
    old_function,
    new_function,
    1,
)

for forbidden in (
    '_MD_EMPHASIS_RE = re.compile(',
    '_MD_EMPHASIS_RE.sub(',
):
    if forbidden in text:
        raise RuntimeError(
            f"Legacy Markdown emphasis implementation remains: {forbidden}"
        )

path.write_text(
    text,
    encoding="utf-8",
)

print("U3.13_MARKDOWN_INTRAWORD_UNDERSCORE_FIX: APPLIED")