from __future__ import annotations

import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

import backend.server.stores.upload_document_extractor as extractor


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def snapshot(path: Path):
    stat = path.stat()
    return {
        "bytes": path.read_bytes(),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


def unchanged(before, after) -> bool:
    return (
        before["bytes"] == after["bytes"]
        and before["size"] == after["size"]
        and before["mtime_ns"] == after["mtime_ns"]
    )


def write_docx(path: Path, paragraphs: list[str]) -> None:
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document '
        'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>"
        + "".join(paragraphs)
        + "</w:body>"
        "</w:document>"
    )

    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("word/document.xml", xml)


def docx_p(text: str, style: str | None = None) -> str:
    style_xml = (
        f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>'
        if style
        else ""
    )

    return (
        "<w:p>"
        + style_xml
        + "<w:r>"
        + f"<w:t>{text}</w:t>"
        + "</w:r>"
        + "</w:p>"
    )


def docx_p_with_break_and_tab() -> str:
    return (
        "<w:p>"
        "<w:r><w:t>Alpha</w:t></w:r>"
        "<w:r><w:br/></w:r>"
        "<w:r><w:t>Beta</w:t></w:r>"
        "<w:r><w:tab/></w:r>"
        "<w:r><w:t>Gamma</w:t></w:r>"
        "</w:p>"
    )


print("=== U6.20 - BEHAVIORAL EXTRACTION VERIFICATION ===")


# ------------------------------------------------------------
# A. TXT behavior
# ------------------------------------------------------------

print()
print("=== A. TXT BEHAVIOR ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    path = root / "sample.txt"
    path.write_text(
        "  First   paragraph.  \r\n"
        "\r\n"
        "\r\n"
        " Second\tparagraph. ",
        encoding="utf-8",
    )

    before = snapshot(path)
    result = extractor.extract_txt_upload_v1(path)
    after = snapshot(path)

    check(
        "TXT_SUCCESS",
        result.extraction_status == "success",
    )

    check(
        "TXT_TITLE_FROM_FILENAME",
        result.title == "sample",
    )

    check(
        "TXT_HEADINGS_EMPTY",
        result.headings == [],
    )

    check(
        "TXT_WHITESPACE_NORMALIZED",
        "First paragraph." in result.text
        and "Second paragraph." in result.text,
    )

    check(
        "TXT_PARAGRAPH_BOUNDARY_PRESERVED",
        "\n\n" in result.text
        and "\n\n\n" not in result.text,
    )

    check(
        "TXT_SOURCE_IMMUTABLE",
        unchanged(before, after),
    )

    empty = root / "empty.txt"
    empty.write_text(" \n\t ", encoding="utf-8")

    check(
        "TXT_EMPTY_TEXT",
        extractor.extract_txt_upload_v1(
            empty
        ).extraction_status
        == "empty_text",
    )

    missing = root / "missing.txt"

    check(
        "TXT_MISSING_FILE",
        extractor.extract_txt_upload_v1(
            missing
        ).extraction_status
        == "missing_file",
    )

    wrong = root / "wrong.md"
    wrong.write_text("Body", encoding="utf-8")

    check(
        "TXT_WRONG_EXTENSION",
        extractor.extract_txt_upload_v1(
            wrong
        ).extraction_status
        == "unsupported_extension",
    )


# ------------------------------------------------------------
# B. Markdown behavior
# ------------------------------------------------------------

print()
print("=== B. MARKDOWN BEHAVIOR ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    path = root / "article.md"
    path.write_text(
        "# Main **Heading**\n\n"
        "Paragraph with **bold**, *italic*, and `code`.\n\n"
        "> Quoted text.\n\n"
        "- First item\n"
        "- Second item\n\n"
        "---\n\n"
        "```python\n"
        "user_id = product_name\n"
        "```\n\n"
        "## Second Heading",
        encoding="utf-8",
    )

    before = snapshot(path)
    result = extractor.extract_markdown_upload_v1(path)
    after = snapshot(path)

    check(
        "MARKDOWN_SUCCESS",
        result.extraction_status == "success",
    )

    check(
        "MARKDOWN_FIRST_HEADING_IS_TITLE",
        result.title == "Main Heading",
    )

    check(
        "MARKDOWN_HEADINGS_ORDER",
        result.headings[:2]
        == [
            "Main Heading",
            "Second Heading",
        ],
    )

    check(
        "MARKDOWN_INLINE_SYNTAX_REMOVED",
        "**" not in result.text
        and "`" not in result.text,
    )

    check(
        "MARKDOWN_VISIBLE_WORDS_PRESERVED",
        "bold" in result.text
        and "italic" in result.text
        and "code" in result.text,
    )

    check(
        "MARKDOWN_FENCED_CODE_CONTENT_PRESERVED",
        "user_id = product_name"
        in result.text,
    )

    check(
        "MARKDOWN_IDENTIFIERS_PRESERVED",
        "user_id" in result.text
        and "product_name" in result.text,
    )

    check(
        "MARKDOWN_LIST_TEXT_PRESERVED",
        "First item" in result.text
        and "Second item" in result.text,
    )

    check(
        "MARKDOWN_BLOCKQUOTE_TEXT_PRESERVED",
        "Quoted text." in result.text,
    )

    check(
        "MARKDOWN_HORIZONTAL_RULE_REMOVED",
        "\n---\n" not in result.text,
    )

    check(
        "MARKDOWN_SOURCE_IMMUTABLE",
        unchanged(before, after),
    )

    alias = root / "alias.markdown"
    alias.write_text(
        "# Alias Heading\n\nBody.",
        encoding="utf-8",
    )

    alias_result = (
        extractor.extract_markdown_upload_v1(
            alias
        )
    )

    check(
        "MARKDOWN_LONG_EXTENSION_SUPPORTED",
        alias_result.extraction_status
        == "success",
    )

    empty = root / "empty.md"
    empty.write_text("   ", encoding="utf-8")

    check(
        "MARKDOWN_EMPTY_TEXT",
        extractor.extract_markdown_upload_v1(
            empty
        ).extraction_status
        == "empty_text",
    )

    missing = root / "missing.md"

    check(
        "MARKDOWN_MISSING_FILE",
        extractor.extract_markdown_upload_v1(
            missing
        ).extraction_status
        == "missing_file",
    )

    wrong = root / "wrong.txt"
    wrong.write_text("Body", encoding="utf-8")

    check(
        "MARKDOWN_WRONG_EXTENSION",
        extractor.extract_markdown_upload_v1(
            wrong
        ).extraction_status
        == "unsupported_extension",
    )


# ------------------------------------------------------------
# C. HTML behavior
# ------------------------------------------------------------

print()
print("=== C. HTML BEHAVIOR ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    path = root / "article.html"
    path.write_text(
        "<html>"
        "<head>"
        "<title>Document Title</title>"
        "<style>.x{display:none}</style>"
        "<script>bad_script()</script>"
        "<noscript>hidden fallback</noscript>"
        "</head>"
        "<body>"
        "<!-- hidden comment -->"
        "<h1>First Heading</h1>"
        "<p>Visible &amp; meaningful.</p>"
        "<h2>Second <strong>Heading</strong></h2>"
        "<div>Another block<br>Next line</div>"
        "</body>"
        "</html>",
        encoding="utf-8",
    )

    before = snapshot(path)
    result = extractor.extract_html_upload_v1(path)
    after = snapshot(path)

    check(
        "HTML_SUCCESS",
        result.extraction_status == "success",
    )

    check(
        "HTML_TITLE_TAG_PRIORITY",
        result.title == "Document Title",
    )

    check(
        "HTML_HEADINGS_ORDER",
        result.headings[:2]
        == [
            "First Heading",
            "Second Heading",
        ],
    )

    check(
        "HTML_VISIBLE_TEXT_PRESERVED",
        "Visible & meaningful."
        in result.text,
    )

    check(
        "HTML_COMMENT_REMOVED",
        "hidden comment"
        not in result.text,
    )

    check(
        "HTML_SCRIPT_REMOVED",
        "bad_script()"
        not in result.text,
    )

    check(
        "HTML_STYLE_REMOVED",
        "display:none"
        not in result.text,
    )

    check(
        "HTML_NOSCRIPT_REMOVED",
        "hidden fallback"
        not in result.text,
    )

    check(
        "HTML_ENTITIES_DECODED",
        "&amp;" not in result.text
        and "&" in result.text,
    )

    check(
        "HTML_TAGS_REMOVED",
        "<h1>" not in result.text
        and "<p>" not in result.text
        and "<strong>" not in result.text,
    )

    check(
        "HTML_BLOCK_BOUNDARIES_PRESENT",
        "\n\n" in result.text,
    )

    check(
        "HTML_BR_HANDLED",
        "Another block" in result.text
        and "Next line" in result.text,
    )

    check(
        "HTML_SOURCE_IMMUTABLE",
        unchanged(before, after),
    )

    no_title = root / "fallback.html"
    no_title.write_text(
        "<h1>Fallback Heading</h1><p>Body.</p>",
        encoding="utf-8",
    )

    check(
        "HTML_H1_TITLE_FALLBACK",
        extractor.extract_html_upload_v1(
            no_title
        ).title
        == "Fallback Heading",
    )

    filename_fallback = root / "filename_fallback.html"
    filename_fallback.write_text(
        "<p>Body.</p>",
        encoding="utf-8",
    )

    check(
        "HTML_FILENAME_TITLE_FALLBACK",
        extractor.extract_html_upload_v1(
            filename_fallback
        ).title
        == "filename_fallback",
    )

    alias = root / "alias.htm"
    alias.write_text(
        "<h1>Alias</h1><p>Body.</p>",
        encoding="utf-8",
    )

    check(
        "HTML_HTM_ALIAS_SUPPORTED",
        extractor.extract_html_upload_v1(
            alias
        ).extraction_status
        == "success",
    )

    empty = root / "empty.html"
    empty.write_text(
        "<html><body>   </body></html>",
        encoding="utf-8",
    )

    check(
        "HTML_EMPTY_TEXT",
        extractor.extract_html_upload_v1(
            empty
        ).extraction_status
        == "empty_text",
    )

    missing = root / "missing.html"

    check(
        "HTML_MISSING_FILE",
        extractor.extract_html_upload_v1(
            missing
        ).extraction_status
        == "missing_file",
    )

    wrong = root / "wrong.txt"
    wrong.write_text("Body", encoding="utf-8")

    check(
        "HTML_WRONG_EXTENSION",
        extractor.extract_html_upload_v1(
            wrong
        ).extraction_status
        == "unsupported_extension",
    )


# ------------------------------------------------------------
# D. DOCX behavior
# ------------------------------------------------------------

print()
print("=== D. DOCX BEHAVIOR ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    styled = root / "styled.docx"

    write_docx(
        styled,
        [
            docx_p(
                "Primary Heading",
                "Heading1",
            ),
            docx_p("Body paragraph."),
            docx_p(
                "Secondary Heading",
                "Heading2",
            ),
            docx_p_with_break_and_tab(),
        ],
    )

    before = snapshot(styled)
    result = extractor.extract_docx_upload_v1(
        styled
    )
    after = snapshot(styled)

    check(
        "DOCX_SUCCESS",
        result.extraction_status == "success",
    )

    check(
        "DOCX_STYLE_BASED_HEADING_METHOD",
        result.metadata.get(
            "heading_method"
        )
        == "style_based",
    )

    check(
        "DOCX_STYLE_HEADINGS_ORDER",
        result.headings[:2]
        == [
            "Primary Heading",
            "Secondary Heading",
        ],
    )

    check(
        "DOCX_TITLE_FROM_FIRST_HEADING",
        result.title == "Primary Heading",
    )

    check(
        "DOCX_PARAGRAPH_ORDER",
        result.text.find(
            "Primary Heading"
        )
        < result.text.find(
            "Body paragraph."
        )
        < result.text.find(
            "Secondary Heading"
        ),
    )

    check(
        "DOCX_LINE_BREAK_PRESERVED",
        "Alpha\nBeta"
        in result.text,
    )

    check(
        "DOCX_TAB_PRESERVED_AS_SPACE",
        "Beta Gamma"
        in result.text,
    )

    check(
        "DOCX_SOURCE_IMMUTABLE",
        unchanged(before, after),
    )

    heuristic = root / "heuristic.docx"

    write_docx(
        heuristic,
        [
            docx_p("THIS LOOKS LIKE A HEADING"),
            docx_p("Normal body paragraph."),
        ],
    )

    heuristic_result = (
        extractor.extract_docx_upload_v1(
            heuristic
        )
    )

    check(
        "DOCX_HEURISTIC_EXTRACTION_SUCCESS",
        heuristic_result.extraction_status
        == "success",
    )

    check(
        "DOCX_HEURISTIC_HEADING_METHOD",
        heuristic_result.metadata.get(
            "heading_method"
        )
        == "heuristic_fallback",
    )

    check(
        "DOCX_HEURISTIC_CONFIDENCE",
        heuristic_result.extraction_confidence
        == 0.88,
    )

    precedence = root / "precedence.docx"

    write_docx(
        precedence,
        [
            docx_p(
                "Styled Heading",
                "Heading1",
            ),
            docx_p("ANOTHER POSSIBLE HEADING"),
            docx_p("Normal body."),
        ],
    )

    precedence_result = (
        extractor.extract_docx_upload_v1(
            precedence
        )
    )

    check(
        "DOCX_STYLE_PRECEDENCE_OVER_HEURISTIC",
        precedence_result.metadata.get(
            "heading_method"
        )
        == "style_based"
        and "Styled Heading"
        in precedence_result.headings,
    )

    no_heading = root / "filename_title.docx"

    write_docx(
        no_heading,
        [
            docx_p(
                "This is a normal sentence with enough words."
            ),
        ],
    )

    no_heading_result = (
        extractor.extract_docx_upload_v1(
            no_heading
        )
    )

    check(
        "DOCX_FILENAME_TITLE_FALLBACK",
        no_heading_result.title
        == "filename_title",
    )

    empty = root / "empty.docx"
    write_docx(empty, [])

    check(
        "DOCX_EMPTY_TEXT",
        extractor.extract_docx_upload_v1(
            empty
        ).extraction_status
        == "empty_text",
    )

    missing_xml = root / "missing_xml.docx"

    with ZipFile(
        missing_xml,
        "w",
        compression=ZIP_DEFLATED,
    ) as archive:
        archive.writestr(
            "word/other.xml",
            "<root/>",
        )

    check(
        "DOCX_MISSING_DOCUMENT_XML",
        extractor.extract_docx_upload_v1(
            missing_xml
        ).extraction_status
        == "invalid_docx",
    )

    malformed = root / "malformed.docx"
    malformed.write_bytes(
        b"not-a-valid-docx-package"
    )

    check(
        "DOCX_MALFORMED_ZIP",
        extractor.extract_docx_upload_v1(
            malformed
        ).extraction_status
        == "extraction_error",
    )

    missing = root / "missing.docx"

    check(
        "DOCX_MISSING_FILE",
        extractor.extract_docx_upload_v1(
            missing
        ).extraction_status
        == "missing_file",
    )

    wrong = root / "wrong.txt"
    wrong.write_text(
        "Not DOCX",
        encoding="utf-8",
    )

    check(
        "DOCX_WRONG_EXTENSION",
        extractor.extract_docx_upload_v1(
            wrong
        ).extraction_status
        == "unsupported_extension",
    )


# ------------------------------------------------------------
# E. Dispatcher routing
# ------------------------------------------------------------

print()
print("=== E. CANONICAL DISPATCHER ROUTING ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    txt = root / "a.txt"
    txt.write_text("Body", encoding="utf-8")

    md = root / "b.md"
    md.write_text("# H\n\nBody", encoding="utf-8")

    markdown = root / "c.markdown"
    markdown.write_text(
        "# H\n\nBody",
        encoding="utf-8",
    )

    html = root / "d.html"
    html.write_text(
        "<p>Body</p>",
        encoding="utf-8",
    )

    htm = root / "e.htm"
    htm.write_text(
        "<p>Body</p>",
        encoding="utf-8",
    )

    docx = root / "f.docx"
    write_docx(
        docx,
        [
            docx_p("Body paragraph."),
        ],
    )

    expected = {
        txt: "txt",
        md: "markdown",
        markdown: "markdown",
        html: "html",
        htm: "html",
        docx: "docx",
    }

    for path, expected_type in expected.items():
        result = extractor.extract_upload_document_v1(
            path
        )

        check(
            "DISPATCH_"
            + path.suffix.replace(
                ".",
                "",
            ).upper()
            + "_SUCCESS",
            result.extraction_status
            == "success",
        )

        check(
            "DISPATCH_"
            + path.suffix.replace(
                ".",
                "",
            ).upper()
            + "_SOURCE_TYPE",
            result.source_type
            == expected_type,
        )

    unsupported = root / "unsupported.pdf"
    unsupported.write_bytes(b"%PDF-test")

    unsupported_result = (
        extractor.extract_upload_document_v1(
            unsupported
        )
    )

    check(
        "DISPATCH_UNSUPPORTED_STATUS",
        unsupported_result.extraction_status
        == "unsupported_source_type",
    )

    check(
        "DISPATCH_UNSUPPORTED_CONFIDENCE_ZERO",
        unsupported_result.extraction_confidence
        == 0.0,
    )


# ------------------------------------------------------------
# F. UploadExtractionResult consistency
# ------------------------------------------------------------

print()
print("=== F. UPLOAD EXTRACTION RESULT CONSISTENCY ===")

fields = set(
    extractor.UploadExtractionResult
    .__dataclass_fields__
    .keys()
)

expected_fields = {
    "source_path",
    "source_type",
    "title",
    "text",
    "headings",
    "metadata",
    "extraction_status",
    "extraction_confidence",
    "created_at",
}

check(
    "RESULT_FIELDS_EXACT",
    fields == expected_fields,
)

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "result.txt"
    path.write_text(
        "Result body.",
        encoding="utf-8",
    )

    result = extractor.extract_upload_document_v1(
        path
    )

    check(
        "RESULT_SUCCESS_STATUS",
        result.extraction_status
        == "success",
    )

    check(
        "RESULT_SUCCESS_CONFIDENCE_VALID",
        isinstance(
            result.extraction_confidence,
            (int, float),
        )
        and 0.0
        <= result.extraction_confidence
        <= 1.0,
    )

    check(
        "RESULT_METADATA_IS_DICT",
        isinstance(
            result.metadata,
            dict,
        ),
    )

    check(
        "RESULT_TITLE_IS_STRING",
        isinstance(
            result.title,
            str,
        ),
    )

    check(
        "RESULT_TEXT_IS_STRING",
        isinstance(
            result.text,
            str,
        ),
    )

    check(
        "RESULT_HEADINGS_IS_LIST",
        isinstance(
            result.headings,
            list,
        ),
    )

    check(
        "RESULT_CREATED_AT_PRESENT",
        isinstance(
            result.created_at,
            str,
        )
        and bool(
            result.created_at.strip()
        ),
    )


# ------------------------------------------------------------
# G. Determinism and serialization
# ------------------------------------------------------------

print()
print("=== G. DETERMINISM AND SERIALIZATION ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "repeat.md"

    path.write_text(
        "# Heading\n\n"
        "Body with **bold** text.",
        encoding="utf-8",
    )

    before = snapshot(path)

    first = extractor.extract_upload_document_v1(
        path
    )

    second = extractor.extract_upload_document_v1(
        path
    )

    after = snapshot(path)

    check(
        "REPEATED_EXTRACTION_TEXT_DETERMINISTIC",
        first.text == second.text,
    )

    check(
        "REPEATED_EXTRACTION_TITLE_DETERMINISTIC",
        first.title == second.title,
    )

    check(
        "REPEATED_EXTRACTION_HEADINGS_DETERMINISTIC",
        first.headings == second.headings,
    )

    check(
        "REPEATED_EXTRACTION_STATUS_DETERMINISTIC",
        first.extraction_status
        == second.extraction_status,
    )

    check(
        "REPEATED_EXTRACTION_CONFIDENCE_DETERMINISTIC",
        first.extraction_confidence
        == second.extraction_confidence,
    )

    check(
        "REPEATED_EXTRACTION_SOURCE_IMMUTABLE",
        unchanged(before, after),
    )

    serialized = (
        extractor.serialize_upload_extraction_result(
            first
        )
    )

    check(
        "SERIALIZATION_PRESERVES_SOURCE_PATH",
        serialized.get(
            "source_path"
        )
        == first.source_path,
    )

    check(
        "SERIALIZATION_PRESERVES_SOURCE_TYPE",
        serialized.get(
            "source_type"
        )
        == first.source_type,
    )

    check(
        "SERIALIZATION_PRESERVES_TITLE",
        serialized.get(
            "title"
        )
        == first.title,
    )

    check(
        "SERIALIZATION_PRESERVES_TEXT",
        serialized.get(
            "text"
        )
        == first.text,
    )

    check(
        "SERIALIZATION_PRESERVES_HEADINGS",
        serialized.get(
            "headings"
        )
        == first.headings,
    )

    check(
        "SERIALIZATION_PRESERVES_METADATA",
        serialized.get(
            "metadata"
        )
        == first.metadata,
    )

    check(
        "SERIALIZATION_PRESERVES_STATUS",
        serialized.get(
            "extraction_status"
        )
        == first.extraction_status,
    )

    check(
        "SERIALIZATION_PRESERVES_CONFIDENCE",
        serialized.get(
            "extraction_confidence"
        )
        == first.extraction_confidence,
    )

    check(
        "SERIALIZATION_PRESERVES_CREATED_AT",
        serialized.get(
            "created_at"
        )
        == first.created_at,
    )


# ------------------------------------------------------------
# H. Isolation from downstream systems
# ------------------------------------------------------------

print()
print("=== H. DOWNSTREAM ISOLATION ===")

module_source = inspect.getsource(
    extractor
).lower()

for forbidden in (
    "article_body_cleaning_engine",
    "article_cleaning_pipeline",
    "build_uduc_from_upload_extraction_result",
    "write_uduc",
    "build_and_write_uduc",
    "uucd_persistence",
    "write_uucd",
    "highlight_selection_engine",
    "active_target_set",
    "semantic_score",
    "relevance_score",
    "scorer",
):
    check(
        "EXTRACTOR_ISOLATED_FROM_"
        + forbidden.upper(),
        forbidden
        not in module_source,
    )


# ------------------------------------------------------------
# I. Final behavioral decision
# ------------------------------------------------------------

print()
print("=== I. BEHAVIORAL DECISION ===")

failures = [
    name
    for name, status in results
    if status != "PASS"
]

print()
print("========================================")

if failures:
    print(
        "U6.20_BEHAVIORAL_EXTRACTION_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U6.20 behavioral extraction verification failed."
    )

print(
    "U6.20_BEHAVIORAL_EXTRACTION_VERIFICATION: CERTIFIED"
)

print(
    "U6.20_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U6.21_BUILD_INTEGRATION_VERIFICATION_TRANSITION: AUTHORIZED"
)

print(
    "U6.20_FINAL_BEHAVIORAL_EXTRACTION_VERIFICATION: PASS"
)