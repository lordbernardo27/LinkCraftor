from __future__ import annotations

import inspect
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import backend.server.stores.upload_document_extractor as extractor


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U6.5 - MARKDOWN EXTRACTOR CONTRACT ===")


md_source = inspect.getsource(
    extractor.extract_markdown_upload_v1
).lower()

heading_source = inspect.getsource(
    extractor._extract_markdown_headings_v1
).lower()

strip_source = inspect.getsource(
    extractor._strip_markdown_syntax_v2
).lower()


# ------------------------------------------------------------
# A. Input / extension contract
# ------------------------------------------------------------

print()
print("=== A. INPUT / EXTENSION CONTRACT ===")

signature = inspect.signature(
    extractor.extract_markdown_upload_v1
)

params = list(
    signature.parameters.values()
)

check(
    "MARKDOWN_ACCEPTS_SINGLE_PATH_PARAMETER",
    len(params) == 1
    and params[0].name == "path",
)

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    md_path = root / "document.md"
    md_path.write_text(
        "# Heading\n\nBody",
        encoding="utf-8",
    )

    markdown_path = root / "document.markdown"
    markdown_path.write_text(
        "# Heading\n\nBody",
        encoding="utf-8",
    )

    upper_md_path = root / "DOCUMENT.MD"
    upper_md_path.write_text(
        "# Heading\n\nBody",
        encoding="utf-8",
    )

    mixed_markdown_path = root / "Document.MarkDown"
    mixed_markdown_path.write_text(
        "# Heading\n\nBody",
        encoding="utf-8",
    )

    wrong_path = root / "document.txt"
    wrong_path.write_text(
        "# Heading\n\nBody",
        encoding="utf-8",
    )

    md_result = extractor.extract_markdown_upload_v1(
        md_path
    )

    markdown_result = extractor.extract_markdown_upload_v1(
        markdown_path
    )

    upper_md_result = extractor.extract_markdown_upload_v1(
        upper_md_path
    )

    mixed_markdown_result = extractor.extract_markdown_upload_v1(
        mixed_markdown_path
    )

    wrong_result = extractor.extract_markdown_upload_v1(
        wrong_path
    )

    check(
        "MD_EXTENSION_ACCEPTED",
        md_result.extraction_status
        == "success",
    )

    check(
        "MARKDOWN_EXTENSION_ACCEPTED",
        markdown_result.extraction_status
        == "success",
    )

    check(
        "UPPERCASE_MD_ACCEPTED",
        upper_md_result.extraction_status
        == "success",
    )

    check(
        "MIXED_CASE_MARKDOWN_ACCEPTED",
        mixed_markdown_result.extraction_status
        == "success",
    )

    check(
        "NON_MARKDOWN_RETURNS_UNSUPPORTED_EXTENSION",
        wrong_result.extraction_status
        == "unsupported_extension",
    )

    check(
        "NON_MARKDOWN_ERROR_IS_STRUCTURED",
        isinstance(
            wrong_result,
            extractor.UploadExtractionResult,
        )
        and isinstance(
            wrong_result.metadata,
            dict,
        ),
    )


# ------------------------------------------------------------
# B. Missing-file contract
# ------------------------------------------------------------

print()
print("=== B. MISSING FILE CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    missing = Path(temp_dir) / "missing.md"

    missing_result = (
        extractor.extract_markdown_upload_v1(
            missing
        )
    )

    check(
        "MISSING_MARKDOWN_RETURNS_CANONICAL_TYPE",
        isinstance(
            missing_result,
            extractor.UploadExtractionResult,
        ),
    )

    check(
        "MISSING_MARKDOWN_STATUS",
        missing_result.extraction_status
        == "missing_file",
    )

    check(
        "MISSING_MARKDOWN_CONFIDENCE_ZERO",
        missing_result.extraction_confidence
        == 0.0,
    )


# ------------------------------------------------------------
# C. Heading extraction contract
# ------------------------------------------------------------

print()
print("=== C. HEADING EXTRACTION ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "headings.md"

    path.write_text(
        "# Main Title\n\n"
        "Body paragraph.\n\n"
        "## Section One\n\n"
        "Text.\n\n"
        "### Section Two\n",
        encoding="utf-8",
    )

    result = extractor.extract_markdown_upload_v1(
        path
    )

    check(
        "MARKDOWN_HEADING_EXTRACTION_SUCCEEDS",
        result.headings
        == [
            "Main Title",
            "Section One",
            "Section Two",
        ],
    )

    check(
        "MARKDOWN_TITLE_USES_FIRST_HEADING",
        result.title == "Main Title",
    )

    check(
        "MARKDOWN_HEADING_COUNT_METADATA_MATCHES",
        result.metadata.get(
            "heading_count"
        )
        == len(result.headings),
    )


# ------------------------------------------------------------
# D. Fenced-code heading protection
# ------------------------------------------------------------

print()
print("=== D. FENCED CODE PROTECTION ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "fenced.md"

    path.write_text(
        "# Real Heading\n\n"
        "```python\n"
        "# fake heading inside code\n"
        "print('hello')\n"
        "```\n\n"
        "~~~text\n"
        "## another fake heading\n"
        "~~~\n\n"
        "## Real Section\n",
        encoding="utf-8",
    )

    result = extractor.extract_markdown_upload_v1(
        path
    )

    check(
        "FENCED_CODE_DOES_NOT_CREATE_FALSE_HEADINGS",
        result.headings
        == [
            "Real Heading",
            "Real Section",
        ],
    )

    check(
        "HEADING_EXTRACTOR_TRACKS_FENCES",
        "in_fence" in heading_source
        and "```" in heading_source
        and "~~~" in heading_source,
    )


# ------------------------------------------------------------
# E. Markdown syntax stripping / normalization
# ------------------------------------------------------------

print()
print("=== E. MARKDOWN TEXT EXTRACTION ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "syntax.md"

    path.write_text(
        "# Title\n\n"
        "This is **bold** and *italic* text.\n\n"
        "A [link](https://example.com) appears here.\n\n"
        "- Item one\n"
        "- Item two\n\n"
        "`inline_code` remains meaningful.\n",
        encoding="utf-8",
    )

    result = extractor.extract_markdown_upload_v1(
        path
    )

    check(
        "MARKDOWN_TEXT_EXTRACTION_SUCCEEDS",
        result.extraction_status
        == "success",
    )

    check(
        "MARKDOWN_STRIPS_HEADING_MARKERS",
        "# Title" not in result.text,
    )

    check(
        "MARKDOWN_STRIPS_BOLD_MARKERS",
        "**bold**" not in result.text
        and "bold" in result.text,
    )

    check(
        "MARKDOWN_STRIPS_LINK_DESTINATION",
        "https://example.com"
        not in result.text
        and "link" in result.text,
    )

    check(
        "MARKDOWN_PRESERVES_PARAGRAPH_BOUNDARIES",
        "\n\n" in result.text,
    )


# ------------------------------------------------------------
# F. Underscore / identifier safety
# ------------------------------------------------------------

print()
print("=== F. IDENTIFIER / UNDERSCORE SAFETY ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "identifiers.md"

    path.write_text(
        "# Identifiers\n\n"
        "user_id should remain intact.\n\n"
        "product_name should remain intact.\n\n"
        "account_status_value should remain intact.\n",
        encoding="utf-8",
    )

    result = extractor.extract_markdown_upload_v1(
        path
    )

    check(
        "USER_ID_PRESERVED",
        "user_id" in result.text,
    )

    check(
        "PRODUCT_NAME_PRESERVED",
        "product_name" in result.text,
    )

    check(
        "MULTI_UNDERSCORE_IDENTIFIER_PRESERVED",
        "account_status_value"
        in result.text,
    )


# ------------------------------------------------------------
# G. Empty / whitespace-only contract
# ------------------------------------------------------------

print()
print("=== G. EMPTY TEXT CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    empty_path = root / "empty.md"
    empty_path.write_text(
        "",
        encoding="utf-8",
    )

    whitespace_path = root / "whitespace.markdown"
    whitespace_path.write_text(
        " \n\t\n ",
        encoding="utf-8",
    )

    empty_result = extractor.extract_markdown_upload_v1(
        empty_path
    )

    whitespace_result = extractor.extract_markdown_upload_v1(
        whitespace_path
    )

    check(
        "EMPTY_MARKDOWN_RETURNS_EMPTY_TEXT",
        empty_result.extraction_status
        == "empty_text",
    )

    check(
        "WHITESPACE_MARKDOWN_RETURNS_EMPTY_TEXT",
        whitespace_result.extraction_status
        == "empty_text",
    )

    check(
        "EMPTY_MARKDOWN_CONFIDENCE_ZERO",
        empty_result.extraction_confidence
        == 0.0,
    )


# ------------------------------------------------------------
# H. Title fallback contract
# ------------------------------------------------------------

print()
print("=== H. TITLE FALLBACK CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "fallback_title.md"

    path.write_text(
        "Plain paragraph with no heading.",
        encoding="utf-8",
    )

    result = extractor.extract_markdown_upload_v1(
        path
    )

    check(
        "MARKDOWN_NO_HEADING_USES_FILENAME_STEM",
        result.title == "fallback_title",
    )

    check(
        "MARKDOWN_NO_HEADING_RETURNS_EMPTY_HEADINGS",
        result.headings == [],
    )


# ------------------------------------------------------------
# I. Successful result contract
# ------------------------------------------------------------

print()
print("=== I. SUCCESS RESULT CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "article.md"

    path.write_text(
        "# Article Title\n\n"
        "Paragraph one.\n\n"
        "## Section\n\n"
        "Paragraph two.",
        encoding="utf-8",
    )

    result = extractor.extract_markdown_upload_v1(
        path
    )

    check(
        "MARKDOWN_RESULT_IS_CANONICAL_TYPE",
        isinstance(
            result,
            extractor.UploadExtractionResult,
        ),
    )

    check(
        "MARKDOWN_SOURCE_TYPE",
        result.source_type
        == "markdown",
    )

    check(
        "MARKDOWN_TITLE_IS_STRING",
        isinstance(result.title, str),
    )

    check(
        "MARKDOWN_TEXT_IS_NONEMPTY_STRING",
        isinstance(result.text, str)
        and bool(result.text),
    )

    check(
        "MARKDOWN_HEADINGS_LIST_OF_STRINGS",
        isinstance(result.headings, list)
        and all(
            isinstance(item, str)
            for item in result.headings
        ),
    )

    check(
        "MARKDOWN_METADATA_IS_DICT",
        isinstance(result.metadata, dict),
    )

    check(
        "MARKDOWN_STATUS_SUCCESS",
        result.extraction_status
        == "success",
    )

    check(
        "MARKDOWN_CONFIDENCE_NUMERIC",
        isinstance(
            result.extraction_confidence,
            (int, float),
        )
        and not isinstance(
            result.extraction_confidence,
            bool,
        ),
    )

    try:
        datetime.fromisoformat(
            result.created_at
        )
        created_ok = True
    except Exception:
        created_ok = False

    check(
        "MARKDOWN_CREATED_AT_IS_ISO_TIMESTAMP",
        created_ok,
    )


# ------------------------------------------------------------
# J. Metadata contract / physical alias preservation
# ------------------------------------------------------------

print()
print("=== J. METADATA / PHYSICAL ALIAS CONTRACT ===")

required_metadata = {
    "filename",
    "extension",
    "extractor",
    "raw_char_count",
    "normalized_char_count",
    "line_count",
    "heading_count",
    "paragraph_count",
}

check(
    "MARKDOWN_METADATA_HAS_REQUIRED_KEYS",
    required_metadata.issubset(
        set(result.metadata.keys())
    ),
)

check(
    "MARKDOWN_METADATA_EXTRACTOR_IDENTITY",
    result.metadata.get("extractor")
    == "extract_markdown_upload_v1",
)

check(
    "MARKDOWN_NORMALIZED_CHAR_COUNT_MATCHES_TEXT",
    result.metadata.get(
        "normalized_char_count"
    )
    == len(result.text),
)

check(
    "MARKDOWN_LINE_COUNT_MATCHES_TEXT",
    result.metadata.get("line_count")
    == len(result.text.splitlines()),
)

check(
    "MARKDOWN_PARAGRAPH_COUNT_MATCHES_TEXT",
    result.metadata.get(
        "paragraph_count"
    )
    == result.text.count("\n\n") + 1,
)

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    md_alias = root / "alias.md"
    markdown_alias = root / "alias.markdown"

    md_alias.write_text(
        "# Heading\n\nBody",
        encoding="utf-8",
    )

    markdown_alias.write_text(
        "# Heading\n\nBody",
        encoding="utf-8",
    )

    md_alias_result = extractor.extract_markdown_upload_v1(
        md_alias
    )

    markdown_alias_result = extractor.extract_markdown_upload_v1(
        markdown_alias
    )

    check(
        "MD_METADATA_PRESERVES_DOT_MD",
        md_alias_result.metadata.get(
            "extension"
        )
        == ".md",
    )

    check(
        "MARKDOWN_METADATA_PRESERVES_DOT_MARKDOWN",
        markdown_alias_result.metadata.get(
            "extension"
        )
        == ".markdown",
    )


# ------------------------------------------------------------
# K. Source immutability
# ------------------------------------------------------------

print()
print("=== K. SOURCE IMMUTABILITY ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "immutable.md"

    source = (
        "# Title\n\n"
        "Original **Markdown** source."
    )

    path.write_text(
        source,
        encoding="utf-8",
    )

    before = path.read_bytes()

    extractor.extract_markdown_upload_v1(
        path
    )

    after = path.read_bytes()

    check(
        "MARKDOWN_SOURCE_BYTES_UNCHANGED",
        before == after,
    )

check(
    "MARKDOWN_HAS_NO_SOURCE_MUTATION_CALLS",
    "write_text(" not in md_source
    and "write_bytes(" not in md_source
    and ".unlink(" not in md_source
    and ".rename(" not in md_source
    and ".replace(" not in md_source,
)


# ------------------------------------------------------------
# L. Cross-format / downstream isolation
# ------------------------------------------------------------

print()
print("=== L. CROSS-FORMAT / DOWNSTREAM ISOLATION ===")

check(
    "MARKDOWN_DOES_NOT_CALL_TXT_EXTRACTOR",
    "extract_txt_upload_v1"
    not in md_source,
)

check(
    "MARKDOWN_DOES_NOT_CALL_HTML_EXTRACTOR",
    "extract_html_upload_v1"
    not in md_source,
)

check(
    "MARKDOWN_DOES_NOT_CALL_DOCX_EXTRACTOR",
    "extract_docx_upload_v1"
    not in md_source,
)

for forbidden in (
    "uduc",
    "highlight",
    "active_target",
    "uucd",
    "semantic",
    "runtime",
    "scorer",
):
    check(
        f"MARKDOWN_DOES_NOT_INVOKE_{forbidden.upper()}",
        forbidden not in md_source,
    )


# ------------------------------------------------------------
# M. Unexpected extraction failure contract
# ------------------------------------------------------------

print()
print("=== M. EXTRACTION ERROR CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "failure.md"

    path.write_text(
        "# Heading\n\nBody",
        encoding="utf-8",
    )

    with patch.object(
        Path,
        "read_text",
        side_effect=OSError(
            "private markdown read failure"
        ),
    ):
        failure_result = (
            extractor.extract_markdown_upload_v1(
                path
            )
        )

    check(
        "MARKDOWN_READ_FAILURE_RETURNS_CANONICAL_TYPE",
        isinstance(
            failure_result,
            extractor.UploadExtractionResult,
        ),
    )

    check(
        "MARKDOWN_READ_FAILURE_STATUS",
        failure_result.extraction_status
        == "extraction_error",
    )

    check(
        "MARKDOWN_READ_FAILURE_CONFIDENCE_ZERO",
        failure_result.extraction_confidence
        == 0.0,
    )

    check(
        "MARKDOWN_READ_FAILURE_REMAINS_STRUCTURED",
        isinstance(
            failure_result.metadata,
            dict,
        )
        and "error"
        in failure_result.metadata,
    )


# ------------------------------------------------------------
# Final
# ------------------------------------------------------------

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U6.5_MARKDOWN_EXTRACTOR_CONTRACT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U6.5 Markdown extractor contract verification failed."
    )

print(
    "U6.5_MARKDOWN_EXTRACTOR_CONTRACT: CERTIFIED"
)

print(
    "U6.5_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U6.6_HTML_EXTRACTOR_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U6.5_FINAL_MARKDOWN_EXTRACTOR_VERIFICATION: PASS"
)