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


print("=== U6.6 - HTML EXTRACTOR CONTRACT ===")


html_source = inspect.getsource(
    extractor.extract_html_upload_v1
).lower()

title_source = inspect.getsource(
    extractor._extract_html_title_v1
).lower()

heading_source = inspect.getsource(
    extractor._extract_html_headings_v1
).lower()

strip_source = inspect.getsource(
    extractor._strip_html_tags_v1
).lower()


# ------------------------------------------------------------
# A. Input / extension contract
# ------------------------------------------------------------

print()
print("=== A. INPUT / EXTENSION CONTRACT ===")

signature = inspect.signature(
    extractor.extract_html_upload_v1
)

params = list(
    signature.parameters.values()
)

check(
    "HTML_ACCEPTS_SINGLE_PATH_PARAMETER",
    len(params) == 1
    and params[0].name == "path",
)

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    html_path = root / "document.html"
    html_path.write_text(
        "<html><body><p>Hello</p></body></html>",
        encoding="utf-8",
    )

    htm_path = root / "document.htm"
    htm_path.write_text(
        "<html><body><p>Hello</p></body></html>",
        encoding="utf-8",
    )

    upper_html_path = root / "DOCUMENT.HTML"
    upper_html_path.write_text(
        "<html><body><p>Hello</p></body></html>",
        encoding="utf-8",
    )

    mixed_htm_path = root / "Document.HtM"
    mixed_htm_path.write_text(
        "<html><body><p>Hello</p></body></html>",
        encoding="utf-8",
    )

    wrong_path = root / "document.md"
    wrong_path.write_text(
        "<html><body><p>Hello</p></body></html>",
        encoding="utf-8",
    )

    html_result = extractor.extract_html_upload_v1(
        html_path
    )

    htm_result = extractor.extract_html_upload_v1(
        htm_path
    )

    upper_html_result = extractor.extract_html_upload_v1(
        upper_html_path
    )

    mixed_htm_result = extractor.extract_html_upload_v1(
        mixed_htm_path
    )

    wrong_result = extractor.extract_html_upload_v1(
        wrong_path
    )

    check(
        "HTML_EXTENSION_ACCEPTED",
        html_result.extraction_status
        == "success",
    )

    check(
        "HTM_EXTENSION_ACCEPTED",
        htm_result.extraction_status
        == "success",
    )

    check(
        "UPPERCASE_HTML_ACCEPTED",
        upper_html_result.extraction_status
        == "success",
    )

    check(
        "MIXED_CASE_HTM_ACCEPTED",
        mixed_htm_result.extraction_status
        == "success",
    )

    check(
        "NON_HTML_RETURNS_UNSUPPORTED_EXTENSION",
        wrong_result.extraction_status
        == "unsupported_extension",
    )

    check(
        "NON_HTML_ERROR_IS_STRUCTURED",
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
    missing = Path(temp_dir) / "missing.html"

    missing_result = (
        extractor.extract_html_upload_v1(
            missing
        )
    )

    check(
        "MISSING_HTML_RETURNS_CANONICAL_TYPE",
        isinstance(
            missing_result,
            extractor.UploadExtractionResult,
        ),
    )

    check(
        "MISSING_HTML_STATUS",
        missing_result.extraction_status
        == "missing_file",
    )

    check(
        "MISSING_HTML_CONFIDENCE_ZERO",
        missing_result.extraction_confidence
        == 0.0,
    )


# ------------------------------------------------------------
# C. Title extraction contract
# ------------------------------------------------------------

print()
print("=== C. TITLE EXTRACTION CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    title_path = root / "title.html"
    title_path.write_text(
        "<html><head><title>Document Title</title></head>"
        "<body><h1>Heading One</h1></body></html>",
        encoding="utf-8",
    )

    h1_path = root / "h1_fallback.html"
    h1_path.write_text(
        "<html><body><h1>Main Heading</h1><p>Body</p></body></html>",
        encoding="utf-8",
    )

    filename_path = root / "filename_fallback.html"
    filename_path.write_text(
        "<html><body><p>Body only</p></body></html>",
        encoding="utf-8",
    )

    title_result = extractor.extract_html_upload_v1(
        title_path
    )

    h1_result = extractor.extract_html_upload_v1(
        h1_path
    )

    filename_result = extractor.extract_html_upload_v1(
        filename_path
    )

    check(
        "HTML_TITLE_TAG_HAS_PRIORITY",
        title_result.title
        == "Document Title",
    )

    check(
        "HTML_H1_TITLE_FALLBACK",
        h1_result.title
        == "Main Heading",
    )

    check(
        "HTML_FILENAME_STEM_TITLE_FALLBACK",
        filename_result.title
        == "filename_fallback",
    )


# ------------------------------------------------------------
# D. Heading extraction contract
# ------------------------------------------------------------

print()
print("=== D. HEADING EXTRACTION CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "headings.html"

    path.write_text(
        "<html><body>"
        "<h1>H1 Heading</h1>"
        "<h2>H2 Heading</h2>"
        "<h3>H3 Heading</h3>"
        "<h4>H4 Heading</h4>"
        "<h5>H5 Heading</h5>"
        "<h6>H6 Heading</h6>"
        "</body></html>",
        encoding="utf-8",
    )

    result = extractor.extract_html_upload_v1(
        path
    )

    check(
        "HTML_H1_TO_H6_EXTRACTED",
        result.headings
        == [
            "H1 Heading",
            "H2 Heading",
            "H3 Heading",
            "H4 Heading",
            "H5 Heading",
            "H6 Heading",
        ],
    )

    check(
        "HTML_HEADING_COUNT_METADATA_MATCHES",
        result.metadata.get(
            "heading_count"
        )
        == len(result.headings),
    )


# ------------------------------------------------------------
# E. Script/style/noscript/comment exclusion
# ------------------------------------------------------------

print()
print("=== E. NON-CONTENT HTML EXCLUSION ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "excluded.html"

    path.write_text(
        "<html><body>"
        "<!-- hidden comment text -->"
        "<script>secret_script_text</script>"
        "<style>.x{content:'secret_style_text';}</style>"
        "<noscript>secret_noscript_text</noscript>"
        "<p>Visible content.</p>"
        "</body></html>",
        encoding="utf-8",
    )

    result = extractor.extract_html_upload_v1(
        path
    )

    check(
        "HTML_COMMENT_CONTENT_EXCLUDED",
        "hidden comment text"
        not in result.text,
    )

    check(
        "HTML_SCRIPT_CONTENT_EXCLUDED",
        "secret_script_text"
        not in result.text,
    )

    check(
        "HTML_STYLE_CONTENT_EXCLUDED",
        "secret_style_text"
        not in result.text,
    )

    check(
        "HTML_NOSCRIPT_CONTENT_EXCLUDED",
        "secret_noscript_text"
        not in result.text,
    )

    check(
        "HTML_VISIBLE_CONTENT_PRESERVED",
        "Visible content."
        in result.text,
    )


# ------------------------------------------------------------
# F. Entity decoding / tag stripping / boundaries
# ------------------------------------------------------------

print()
print("=== F. TEXT EXTRACTION / NORMALIZATION ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "text.html"

    path.write_text(
        "<html><body>"
        "<p>First &amp; second.</p>"
        "<p>Third paragraph.</p>"
        "<div>Fourth block.</div>"
        "<br>"
        "Line after break."
        "</body></html>",
        encoding="utf-8",
    )

    result = extractor.extract_html_upload_v1(
        path
    )

    check(
        "HTML_ENTITIES_DECODED",
        "First & second."
        in result.text,
    )

    check(
        "HTML_TAGS_REMOVED",
        "<p>" not in result.text
        and "<div>" not in result.text
        and "<br" not in result.text,
    )

    check(
        "HTML_BLOCK_BOUNDARIES_PRESERVED",
        "\n\n" in result.text,
    )

    check(
        "HTML_BR_PRESERVES_LINE_BREAK",
        "Fourth block.\n\nLine after break."
        in result.text
        or "Fourth block.\nLine after break."
        in result.text,
    )

    check(
        "HTML_STRIPPER_HANDLES_COMMENTS_FIRST",
        "_html_comment_re.sub"
        in strip_source,
    )

    check(
        "HTML_STRIPPER_DECODES_ENTITIES",
        "html_lib.unescape"
        in strip_source,
    )


# ------------------------------------------------------------
# G. Empty / markup-only contract
# ------------------------------------------------------------

print()
print("=== G. EMPTY TEXT CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    empty_path = root / "empty.html"
    empty_path.write_text(
        "",
        encoding="utf-8",
    )

    markup_path = root / "markup.htm"
    markup_path.write_text(
        "<html><head></head><body>"
        "<script>only script</script>"
        "<style>body{}</style>"
        "</body></html>",
        encoding="utf-8",
    )

    empty_result = extractor.extract_html_upload_v1(
        empty_path
    )

    markup_result = extractor.extract_html_upload_v1(
        markup_path
    )

    check(
        "EMPTY_HTML_RETURNS_EMPTY_TEXT",
        empty_result.extraction_status
        == "empty_text",
    )

    check(
        "MARKUP_ONLY_HTML_RETURNS_EMPTY_TEXT",
        markup_result.extraction_status
        == "empty_text",
    )

    check(
        "EMPTY_HTML_CONFIDENCE_ZERO",
        empty_result.extraction_confidence
        == 0.0,
    )


# ------------------------------------------------------------
# H. Successful result contract
# ------------------------------------------------------------

print()
print("=== H. SUCCESS RESULT CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "article.html"

    path.write_text(
        "<html>"
        "<head><title>Article Title</title></head>"
        "<body>"
        "<h1>Main Heading</h1>"
        "<p>Paragraph one.</p>"
        "<h2>Section</h2>"
        "<p>Paragraph two.</p>"
        "</body>"
        "</html>",
        encoding="utf-8",
    )

    result = extractor.extract_html_upload_v1(
        path
    )

    check(
        "HTML_RESULT_IS_CANONICAL_TYPE",
        isinstance(
            result,
            extractor.UploadExtractionResult,
        ),
    )

    check(
        "HTML_SOURCE_TYPE",
        result.source_type == "html",
    )

    check(
        "HTML_TITLE_IS_STRING",
        isinstance(result.title, str),
    )

    check(
        "HTML_TEXT_IS_NONEMPTY_STRING",
        isinstance(result.text, str)
        and bool(result.text),
    )

    check(
        "HTML_HEADINGS_LIST_OF_STRINGS",
        isinstance(result.headings, list)
        and all(
            isinstance(item, str)
            for item in result.headings
        ),
    )

    check(
        "HTML_METADATA_IS_DICT",
        isinstance(result.metadata, dict),
    )

    check(
        "HTML_STATUS_SUCCESS",
        result.extraction_status
        == "success",
    )

    check(
        "HTML_CONFIDENCE_NUMERIC",
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
        "HTML_CREATED_AT_IS_ISO_TIMESTAMP",
        created_ok,
    )


# ------------------------------------------------------------
# I. Metadata / alias preservation
# ------------------------------------------------------------

print()
print("=== I. METADATA / PHYSICAL ALIAS CONTRACT ===")

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
    "HTML_METADATA_HAS_REQUIRED_KEYS",
    required_metadata.issubset(
        set(result.metadata.keys())
    ),
)

check(
    "HTML_METADATA_EXTRACTOR_IDENTITY",
    result.metadata.get("extractor")
    == "extract_html_upload_v1",
)

check(
    "HTML_NORMALIZED_CHAR_COUNT_MATCHES_TEXT",
    result.metadata.get(
        "normalized_char_count"
    )
    == len(result.text),
)

check(
    "HTML_LINE_COUNT_MATCHES_TEXT",
    result.metadata.get("line_count")
    == len(result.text.splitlines()),
)

check(
    "HTML_PARAGRAPH_COUNT_MATCHES_TEXT",
    result.metadata.get(
        "paragraph_count"
    )
    == result.text.count("\n\n") + 1,
)

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    html_alias = root / "alias.html"
    htm_alias = root / "alias.htm"

    html_alias.write_text(
        "<html><body><p>Hello</p></body></html>",
        encoding="utf-8",
    )

    htm_alias.write_text(
        "<html><body><p>Hello</p></body></html>",
        encoding="utf-8",
    )

    html_alias_result = extractor.extract_html_upload_v1(
        html_alias
    )

    htm_alias_result = extractor.extract_html_upload_v1(
        htm_alias
    )

    check(
        "HTML_METADATA_PRESERVES_DOT_HTML",
        html_alias_result.metadata.get(
            "extension"
        )
        == ".html",
    )

    check(
        "HTM_METADATA_PRESERVES_DOT_HTM",
        htm_alias_result.metadata.get(
            "extension"
        )
        == ".htm",
    )


# ------------------------------------------------------------
# J. Source immutability
# ------------------------------------------------------------

print()
print("=== J. SOURCE IMMUTABILITY ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "immutable.html"

    source = (
        "<html><body><p>"
        "Original HTML source."
        "</p></body></html>"
    )

    path.write_text(
        source,
        encoding="utf-8",
    )

    before = path.read_bytes()

    extractor.extract_html_upload_v1(
        path
    )

    after = path.read_bytes()

    check(
        "HTML_SOURCE_BYTES_UNCHANGED",
        before == after,
    )

check(
    "HTML_HAS_NO_SOURCE_MUTATION_CALLS",
    "write_text(" not in html_source
    and "write_bytes(" not in html_source
    and ".unlink(" not in html_source
    and ".rename(" not in html_source
    and ".replace(" not in html_source,
)


# ------------------------------------------------------------
# K. Cross-format / Website / downstream isolation
# ------------------------------------------------------------

print()
print("=== K. CROSS-FORMAT / DOWNSTREAM ISOLATION ===")

check(
    "HTML_DOES_NOT_CALL_TXT_EXTRACTOR",
    "extract_txt_upload_v1"
    not in html_source,
)

check(
    "HTML_DOES_NOT_CALL_MARKDOWN_EXTRACTOR",
    "extract_markdown_upload_v1"
    not in html_source,
)

check(
    "HTML_DOES_NOT_CALL_DOCX_EXTRACTOR",
    "extract_docx_upload_v1"
    not in html_source,
)

check(
    "HTML_DOES_NOT_CALL_WEBSITE_CLEANERS",
    "article_body_cleaning_engine"
    not in html_source
    and "article_cleaning_pipeline"
    not in html_source
    and "raw_website_html"
    not in html_source,
)

check(
    "HTML_DOES_NOT_CALL_URL_ACQUISITION",
    "/api/urls/import"
    not in html_source
    and "site_reader"
    not in html_source,
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
        f"HTML_DOES_NOT_INVOKE_{forbidden.upper()}",
        forbidden not in html_source,
    )


# ------------------------------------------------------------
# L. Unexpected extraction failure contract
# ------------------------------------------------------------

print()
print("=== L. EXTRACTION ERROR CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "failure.html"

    path.write_text(
        "<html><body>Hello</body></html>",
        encoding="utf-8",
    )

    with patch.object(
        Path,
        "read_text",
        side_effect=OSError(
            "private html read failure"
        ),
    ):
        failure_result = (
            extractor.extract_html_upload_v1(
                path
            )
        )

    check(
        "HTML_READ_FAILURE_RETURNS_CANONICAL_TYPE",
        isinstance(
            failure_result,
            extractor.UploadExtractionResult,
        ),
    )

    check(
        "HTML_READ_FAILURE_STATUS",
        failure_result.extraction_status
        == "extraction_error",
    )

    check(
        "HTML_READ_FAILURE_CONFIDENCE_ZERO",
        failure_result.extraction_confidence
        == 0.0,
    )

    check(
        "HTML_READ_FAILURE_REMAINS_STRUCTURED",
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
        "U6.6_HTML_EXTRACTOR_CONTRACT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U6.6 HTML extractor contract verification failed."
    )

print(
    "U6.6_HTML_EXTRACTOR_CONTRACT: CERTIFIED"
)

print(
    "U6.6_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U6.7_DOCX_EXTRACTOR_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U6.6_FINAL_HTML_EXTRACTOR_VERIFICATION: PASS"
)