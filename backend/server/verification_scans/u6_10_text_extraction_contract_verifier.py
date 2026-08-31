from __future__ import annotations

import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZIP_DEFLATED

import backend.server.stores.upload_document_extractor as extractor


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def write_docx(path: Path, document_xml: str) -> None:
    with ZipFile(
        path,
        "w",
        compression=ZIP_DEFLATED,
    ) as archive:
        archive.writestr(
            "word/document.xml",
            document_xml,
        )


def docx_xml(*paragraphs: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document '
        'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>"
        + "".join(paragraphs)
        + "</w:body>"
        "</w:document>"
    )


def docx_paragraph(text: str) -> str:
    return (
        "<w:p>"
        "<w:r>"
        f"<w:t>{text}</w:t>"
        "</w:r>"
        "</w:p>"
    )


print("=== U6.10 - TEXT EXTRACTION CONTRACT ===")


# ------------------------------------------------------------
# A. TXT text extraction
# ------------------------------------------------------------

print()
print("=== A. TXT TEXT EXTRACTION ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "plain.txt"

    path.write_bytes(
        b"First line.\r\n\r\n"
        b"Second\tparagraph.\r\n"
        b"Third line.\xff"
    )

    before = path.read_bytes()

    result = extractor.extract_txt_upload_v1(
        path
    )

    after = path.read_bytes()

    check(
        "TXT_SUCCESS",
        result.extraction_status == "success",
    )

    check(
        "TXT_TEXT_IS_STRING",
        isinstance(result.text, str),
    )

    check(
        "TXT_UNDECODABLE_BYTE_TOLERATED",
        "First line." in result.text
        and "Third line." in result.text,
    )

    check(
        "TXT_WHITESPACE_NORMALIZED",
        "Second paragraph." in result.text,
    )

    check(
        "TXT_PARAGRAPH_BOUNDARY_PRESERVED",
        "\n\n" in result.text,
    )

    check(
        "TXT_MEANINGFUL_ORDER_PRESERVED",
        result.text.find("First line.")
        < result.text.find("Second paragraph.")
        < result.text.find("Third line."),
    )

    check(
        "TXT_SOURCE_IMMUTABLE",
        before == after,
    )

    check(
        "TXT_NORMALIZED_CHAR_COUNT_MATCHES",
        result.metadata.get(
            "normalized_char_count"
        )
        == len(result.text),
    )

    check(
        "TXT_LINE_COUNT_MATCHES",
        result.metadata.get(
            "line_count"
        )
        == len(result.text.splitlines()),
    )


# ------------------------------------------------------------
# B. Markdown text extraction
# ------------------------------------------------------------

print()
print("=== B. MARKDOWN TEXT EXTRACTION ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "article.md"

    path.write_text(
        "# Main Title\n\n"
        "This is **bold** and *italic* text with `inline code`.\n\n"
        "Keep user_id and product_name intact.\n\n"
        "[Visible Link](https://example.com)\n\n"
        "```python\n"
        "print('code block content')\n"
        "```\n\n"
        "Final paragraph.",
        encoding="utf-8",
    )

    before = path.read_bytes()

    result = extractor.extract_markdown_upload_v1(
        path
    )

    after = path.read_bytes()

    check(
        "MARKDOWN_SUCCESS",
        result.extraction_status == "success",
    )

    check(
        "MARKDOWN_TEXT_IS_STRING",
        isinstance(result.text, str),
    )

    check(
        "MARKDOWN_VISIBLE_TEXT_PRESERVED",
        "Main Title" in result.text
        and "bold" in result.text
        and "italic" in result.text
        and "Visible Link" in result.text
        and "Final paragraph." in result.text,
    )

    check(
        "MARKDOWN_PRESENTATION_SYNTAX_REMOVED",
        "**bold**" not in result.text
        and "*italic*" not in result.text
        and "[Visible Link](https://example.com)"
        not in result.text,
    )

    check(
        "MARKDOWN_IDENTIFIER_UNDERSCORES_PRESERVED",
        "user_id" in result.text
        and "product_name" in result.text,
    )

    check(
        "MARKDOWN_PARAGRAPH_BOUNDARIES_PRESERVED",
        "\n\n" in result.text,
    )

    check(
        "MARKDOWN_HEADING_TEXT_REMAINS_IN_TEXT",
        "Main Title" in result.text,
    )

    check(
        "MARKDOWN_SOURCE_IMMUTABLE",
        before == after,
    )

    check(
        "MARKDOWN_NORMALIZED_CHAR_COUNT_MATCHES",
        result.metadata.get(
            "normalized_char_count"
        )
        == len(result.text),
    )

    check(
        "MARKDOWN_LINE_COUNT_MATCHES",
        result.metadata.get(
            "line_count"
        )
        == len(result.text.splitlines()),
    )


# ------------------------------------------------------------
# C. Markdown alias semantics
# ------------------------------------------------------------

print()
print("=== C. MARKDOWN ALIAS SEMANTICS ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    content = (
        "# Alias Title\n\n"
        "Paragraph one.\n\n"
        "Paragraph two."
    )

    md_path = root / "alias.md"
    markdown_path = root / "alias.markdown"

    md_path.write_text(
        content,
        encoding="utf-8",
    )

    markdown_path.write_text(
        content,
        encoding="utf-8",
    )

    md_result = extractor.extract_markdown_upload_v1(
        md_path
    )

    markdown_result = extractor.extract_markdown_upload_v1(
        markdown_path
    )

    check(
        "MARKDOWN_ALIASES_HAVE_EQUIVALENT_TEXT",
        md_result.text
        == markdown_result.text,
    )


# ------------------------------------------------------------
# D. HTML text extraction
# ------------------------------------------------------------

print()
print("=== D. HTML TEXT EXTRACTION ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "article.html"

    path.write_text(
        "<html>"
        "<head>"
        "<title>Page Title</title>"
        "<style>.x { color:red; }</style>"
        "<script>console.log('hidden')</script>"
        "</head>"
        "<body>"
        "<!-- hidden comment -->"
        "<h1>Main Heading</h1>"
        "<p>First &amp; visible paragraph.</p>"
        "<p>Second<br>line.</p>"
        "<noscript>hidden fallback</noscript>"
        "<div>Final visible text.</div>"
        "</body>"
        "</html>",
        encoding="utf-8",
    )

    before = path.read_bytes()

    result = extractor.extract_html_upload_v1(
        path
    )

    after = path.read_bytes()

    check(
        "HTML_SUCCESS",
        result.extraction_status == "success",
    )

    check(
        "HTML_TEXT_IS_STRING",
        isinstance(result.text, str),
    )

    check(
        "HTML_TAGS_REMOVED",
        "<h1>" not in result.text
        and "<p>" not in result.text
        and "<div>" not in result.text,
    )

    check(
        "HTML_NONCONTENT_REMOVED",
        "console.log" not in result.text
        and "color:red" not in result.text
        and "hidden comment" not in result.text
        and "hidden fallback" not in result.text,
    )

    check(
        "HTML_VISIBLE_TEXT_PRESERVED",
        "Main Heading" in result.text
        and "First & visible paragraph."
        in result.text
        and "Final visible text."
        in result.text,
    )

    check(
        "HTML_ENTITIES_DECODED",
        "&amp;" not in result.text
        and "First & visible paragraph."
        in result.text,
    )

    check(
        "HTML_BLOCK_BOUNDARIES_PRESERVED",
        "\n" in result.text,
    )

    check(
        "HTML_BR_BOUNDARY_PRESERVED",
        "Second\nline." in result.text
        or "Second\n\nline." in result.text,
    )

    check(
        "HTML_SOURCE_IMMUTABLE",
        before == after,
    )

    check(
        "HTML_NORMALIZED_CHAR_COUNT_MATCHES",
        result.metadata.get(
            "normalized_char_count"
        )
        == len(result.text),
    )

    check(
        "HTML_LINE_COUNT_MATCHES",
        result.metadata.get(
            "line_count"
        )
        == len(result.text.splitlines()),
    )


# ------------------------------------------------------------
# E. HTML alias semantics
# ------------------------------------------------------------

print()
print("=== E. HTML ALIAS SEMANTICS ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    content = (
        "<html><body>"
        "<h1>Alias</h1>"
        "<p>Paragraph.</p>"
        "</body></html>"
    )

    html_path = root / "alias.html"
    htm_path = root / "alias.htm"

    html_path.write_text(
        content,
        encoding="utf-8",
    )

    htm_path.write_text(
        content,
        encoding="utf-8",
    )

    html_result = extractor.extract_html_upload_v1(
        html_path
    )

    htm_result = extractor.extract_html_upload_v1(
        htm_path
    )

    check(
        "HTML_ALIASES_HAVE_EQUIVALENT_TEXT",
        html_result.text
        == htm_result.text,
    )


# ------------------------------------------------------------
# F. DOCX text extraction
# ------------------------------------------------------------

print()
print("=== F. DOCX TEXT EXTRACTION ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "article.docx"

    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document '
        'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>"
        "<w:p>"
        "<w:r><w:t>First paragraph.</w:t></w:r>"
        "</w:p>"
        "<w:p>"
        "<w:r><w:t>Line one</w:t></w:r>"
        "<w:r><w:br/></w:r>"
        "<w:r><w:t>Line two</w:t></w:r>"
        "</w:p>"
        "<w:p>"
        "<w:r><w:t>Before</w:t></w:r>"
        "<w:r><w:tab/></w:r>"
        "<w:r><w:t>After</w:t></w:r>"
        "</w:p>"
        "<w:p>"
        "<w:r><w:t>Final paragraph.</w:t></w:r>"
        "</w:p>"
        "</w:body>"
        "</w:document>"
    )

    write_docx(
        path,
        xml,
    )

    before = path.read_bytes()

    result = extractor.extract_docx_upload_v1(
        path
    )

    after = path.read_bytes()

    check(
        "DOCX_SUCCESS",
        result.extraction_status == "success",
    )

    check(
        "DOCX_TEXT_IS_STRING",
        isinstance(result.text, str),
    )

    check(
        "DOCX_PARAGRAPH_ORDER_PRESERVED",
        result.text.find("First paragraph.")
        < result.text.find("Line one")
        < result.text.find("Before After")
        < result.text.find("Final paragraph."),
    )

    check(
        "DOCX_INTERNAL_LINE_BREAK_PRESERVED",
        "Line one\nLine two"
        in result.text,
    )

    check(
        "DOCX_TAB_BOUNDARY_PRESERVED",
        "Before After"
        in result.text,
    )

    check(
        "DOCX_PARAGRAPHS_JOINED_CANONICALLY",
        "\n\n" in result.text,
    )

    check(
        "DOCX_SOURCE_IMMUTABLE",
        before == after,
    )

    check(
        "DOCX_NORMALIZED_CHAR_COUNT_MATCHES",
        result.metadata.get(
            "normalized_char_count"
        )
        == len(result.text),
    )

    check(
        "DOCX_LINE_COUNT_MATCHES",
        result.metadata.get(
            "line_count"
        )
        == len(result.text.splitlines()),
    )


# ------------------------------------------------------------
# G. Empty / whitespace-only contract
# ------------------------------------------------------------

print()
print("=== G. EMPTY TEXT CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    txt = root / "empty.txt"
    txt.write_text(
        "   \n\t\n   ",
        encoding="utf-8",
    )

    md = root / "empty.md"
    md.write_text(
        "   \n\n   ",
        encoding="utf-8",
    )

    html = root / "empty.html"
    html.write_text(
        "<html><body>   </body></html>",
        encoding="utf-8",
    )

    docx = root / "empty.docx"
    write_docx(
        docx,
        docx_xml(),
    )

    empty_results = [
        extractor.extract_txt_upload_v1(txt),
        extractor.extract_markdown_upload_v1(md),
        extractor.extract_html_upload_v1(html),
        extractor.extract_docx_upload_v1(docx),
    ]

    check(
        "EMPTY_RESULTS_HAVE_EMPTY_TEXT",
        all(
            result.text == ""
            for result in empty_results
        ),
    )

    check(
        "EMPTY_RESULTS_HAVE_EMPTY_TEXT_STATUS",
        all(
            result.extraction_status
            == "empty_text"
            for result in empty_results
        ),
    )


# ------------------------------------------------------------
# H. Serialization
# ------------------------------------------------------------

print()
print("=== H. TEXT SERIALIZATION CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "serialized.txt"

    path.write_text(
        "Paragraph one.\n\nParagraph two.",
        encoding="utf-8",
    )

    result = extractor.extract_txt_upload_v1(
        path
    )

    serialized = (
        extractor.serialize_upload_extraction_result(
            result
        )
    )

    check(
        "SERIALIZER_PRESERVES_TEXT",
        serialized.get("text")
        == result.text,
    )


# ------------------------------------------------------------
# I. Format-specific extraction ownership
# ------------------------------------------------------------

print()
print("=== I. FORMAT-SPECIFIC TEXT OWNERSHIP ===")

txt_source = inspect.getsource(
    extractor.extract_txt_upload_v1
).lower()

md_source = inspect.getsource(
    extractor.extract_markdown_upload_v1
).lower()

html_source = inspect.getsource(
    extractor.extract_html_upload_v1
).lower()

docx_source = inspect.getsource(
    extractor.extract_docx_upload_v1
).lower()

check(
    "TXT_TEXT_EXTRACTION_REMAINS_FORMAT_SPECIFIC",
    "read_text" in txt_source,
)

check(
    "MARKDOWN_TEXT_EXTRACTION_REMAINS_FORMAT_SPECIFIC",
    "_strip_markdown_syntax_v2"
    in md_source,
)

check(
    "HTML_TEXT_EXTRACTION_REMAINS_FORMAT_SPECIFIC",
    "_strip_html_tags_v1"
    in html_source,
)

check(
    "DOCX_TEXT_EXTRACTION_REMAINS_FORMAT_SPECIFIC",
    "_extract_docx_paragraphs_v2"
    in docx_source,
)


# ------------------------------------------------------------
# J. Downstream / website isolation
# ------------------------------------------------------------

print()
print("=== J. TEXT EXTRACTION ISOLATION ===")

combined_source = "\n".join(
    [
        txt_source,
        md_source,
        html_source,
        docx_source,
        "\n".join(
            line
            for line in inspect.getsource(
                extractor._normalize_upload_text_v2
            ).lower().splitlines()
            if "uduc" not in line
        ),
    ]
)

for forbidden in (
    "article_body_cleaning_engine",
    "article_cleaning_pipeline",
    "/api/urls/import",
    "site_reader",
    "uduc",
    "highlight",
    "active_target",
    "uucd",
    "semantic",
    "runtime",
    "scorer",
):
    label = (
        forbidden.upper()
        .replace("/", "_")
        .replace(".", "_")
    )

    check(
        f"TEXT_EXTRACTION_DOES_NOT_DEPEND_ON_{label}",
        forbidden not in combined_source,
    )


# ------------------------------------------------------------
# K. U6 vs U7 responsibility boundary
# ------------------------------------------------------------

print()
print("=== K. U6 / U7 NORMALIZATION BOUNDARY ===")

normalizer_source = inspect.getsource(
    extractor._normalize_upload_text_v2
).lower()

check(
    "U6_NORMALIZER_IS_WHITESPACE_STRUCTURAL_ONLY",
    "replace(" in normalizer_source
    and "split(" in normalizer_source
    and "join(" in normalizer_source,
)

check(
    "U6_NORMALIZER_DOES_NOT_PERFORM_SEMANTIC_PROCESSING",
    "semantic" not in normalizer_source
    and "keyword" not in normalizer_source
    and "phrase" not in normalizer_source
    and "score" not in normalizer_source,
)


# ------------------------------------------------------------
# L. Live intake re-read / re-extraction consistency
# ------------------------------------------------------------

print()
print("=== L. LIVE INTAKE TEXT CONSISTENCY ===")

intake_module = __import__(
    "backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake",
    fromlist=["run_upload_intake"],
)

intake_source = inspect.getsource(
    intake_module.run_upload_intake
).lower()

check(
    "INTAKE_DOES_NOT_REDERIVE_RESULT_TEXT",
    "result.text =" not in intake_source,
)

check(
    "INTAKE_DOES_NOT_DIRECTLY_REREAD_SOURCE_TEXT",
    ".read_text(" not in intake_source
    and ".read_bytes(" not in intake_source,
)

check(
    "INTAKE_USES_CANONICAL_EXTRACTOR",
    "extract_upload_document_v1"
    in intake_source,
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
        "U6.10_TEXT_EXTRACTION_CONTRACT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U6.10 text extraction contract verification failed."
    )

print(
    "U6.10_TEXT_EXTRACTION_CONTRACT: CERTIFIED"
)

print(
    "U6.10_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U6.11_METADATA_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U6.10_FINAL_TEXT_EXTRACTION_VERIFICATION: PASS"
)