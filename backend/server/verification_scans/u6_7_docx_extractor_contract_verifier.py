from __future__ import annotations

import inspect
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZIP_DEFLATED

import backend.server.stores.upload_document_extractor as extractor


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U6.7 - DOCX EXTRACTOR CONTRACT ===")


docx_source = inspect.getsource(
    extractor.extract_docx_upload_v1
).lower()

paragraph_source = inspect.getsource(
    extractor._extract_docx_paragraphs_v2
).lower()

heading_source = inspect.getsource(
    extractor._extract_docx_headings_v2
).lower()

style_source = inspect.getsource(
    extractor._docx_style_is_heading
).lower()


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


def paragraph(
    text: str,
    style_id: str = "",
) -> str:
    style_xml = ""

    if style_id:
        style_xml = (
            '<w:pPr>'
            f'<w:pStyle w:val="{style_id}"/>'
            '</w:pPr>'
        )

    return (
        "<w:p>"
        f"{style_xml}"
        "<w:r>"
        f"<w:t>{text}</w:t>"
        "</w:r>"
        "</w:p>"
    )


def doc_xml(*paragraphs: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document '
        'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>"
        + "".join(paragraphs)
        + "</w:body>"
        "</w:document>"
    )


# ------------------------------------------------------------
# A. Input / extension contract
# ------------------------------------------------------------

print()
print("=== A. INPUT / EXTENSION CONTRACT ===")

signature = inspect.signature(
    extractor.extract_docx_upload_v1
)

params = list(
    signature.parameters.values()
)

check(
    "DOCX_ACCEPTS_SINGLE_PATH_PARAMETER",
    len(params) == 1
    and params[0].name == "path",
)

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    docx_path = root / "document.docx"
    write_docx(
        docx_path,
        doc_xml(
            paragraph("Heading", "Heading1"),
            paragraph("Body paragraph."),
        ),
    )

    upper_path = root / "DOCUMENT.DOCX"
    write_docx(
        upper_path,
        doc_xml(
            paragraph("Heading", "Heading1"),
            paragraph("Body paragraph."),
        ),
    )

    mixed_path = root / "Document.DoCx"
    write_docx(
        mixed_path,
        doc_xml(
            paragraph("Heading", "Heading1"),
            paragraph("Body paragraph."),
        ),
    )

    wrong_path = root / "document.txt"
    wrong_path.write_text(
        "plain text",
        encoding="utf-8",
    )

    docx_result = extractor.extract_docx_upload_v1(
        docx_path
    )

    upper_result = extractor.extract_docx_upload_v1(
        upper_path
    )

    mixed_result = extractor.extract_docx_upload_v1(
        mixed_path
    )

    wrong_result = extractor.extract_docx_upload_v1(
        wrong_path
    )

    check(
        "LOWERCASE_DOCX_ACCEPTED",
        docx_result.extraction_status
        == "success",
    )

    check(
        "UPPERCASE_DOCX_ACCEPTED",
        upper_result.extraction_status
        == "success",
    )

    check(
        "MIXED_CASE_DOCX_ACCEPTED",
        mixed_result.extraction_status
        == "success",
    )

    check(
        "NON_DOCX_RETURNS_UNSUPPORTED_EXTENSION",
        wrong_result.extraction_status
        == "unsupported_extension",
    )

    check(
        "NON_DOCX_ERROR_IS_STRUCTURED",
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
    missing = Path(temp_dir) / "missing.docx"

    missing_result = (
        extractor.extract_docx_upload_v1(
            missing
        )
    )

    check(
        "MISSING_DOCX_RETURNS_CANONICAL_TYPE",
        isinstance(
            missing_result,
            extractor.UploadExtractionResult,
        ),
    )

    check(
        "MISSING_DOCX_STATUS",
        missing_result.extraction_status
        == "missing_file",
    )

    check(
        "MISSING_DOCX_CONFIDENCE_ZERO",
        missing_result.extraction_confidence
        == 0.0,
    )


# ------------------------------------------------------------
# C. Canonical archive/content source
# ------------------------------------------------------------

print()
print("=== C. DOCX ARCHIVE SOURCE CONTRACT ===")

check(
    "DOCX_PARAGRAPH_HELPER_USES_ZIPFILE",
    "zipfile" in paragraph_source
    or "zipfile(" in paragraph_source
    or "with zipfile" in paragraph_source
    or "with zipfile(" in paragraph_source
    or "with zipfile" in paragraph_source
    or "with zipfile" in paragraph_source,
)

check(
    "DOCX_PARAGRAPH_HELPER_READS_WORD_DOCUMENT_XML",
    'z.read("word/document.xml")'
    in paragraph_source
    or "z.read('word/document.xml')"
    in paragraph_source,
)

check(
    "DOCX_CANONICAL_EXTRACTOR_USES_V2_PARAGRAPH_HELPER",
    "_extract_docx_paragraphs_v2"
    in docx_source,
)


# ------------------------------------------------------------
# D. Paragraph ordering / boundaries / breaks / tabs
# ------------------------------------------------------------

print()
print("=== D. PARAGRAPH / BREAK / TAB EXTRACTION ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "structure.docx"

    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document '
        'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>"
        "<w:p>"
        '<w:pPr><w:pStyle w:val="Heading1"/></w:pPr>'
        "<w:r><w:t>Main Heading</w:t></w:r>"
        "</w:p>"
        "<w:p>"
        "<w:r><w:t>First line</w:t></w:r>"
        "<w:r><w:br/></w:r>"
        "<w:r><w:t>Second line</w:t></w:r>"
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

    paragraphs = extractor._extract_docx_paragraphs_v2(
        path
    )

    result = extractor.extract_docx_upload_v1(
        path
    )

    texts = [
        item.get("text", "")
        for item in paragraphs
    ]

    check(
        "DOCX_PARAGRAPH_ORDER_PRESERVED",
        texts[0] == "Main Heading"
        and texts[-1]
        == "Final paragraph.",
    )

    check(
        "DOCX_INTERNAL_LINE_BREAK_PRESERVED",
        any(
            "First line\nSecond line"
            in text
            for text in texts
        ),
    )

    check(
        "DOCX_TAB_BECOMES_SPACE",
        any(
            "Before After"
            in text
            for text in texts
        ),
    )

    check(
        "DOCX_PARAGRAPH_BOUNDARIES_PRESERVED",
        "\n\n" in result.text,
    )

    check(
        "DOCX_NORMALIZED_TEXT_HAS_NO_CR",
        "\r" not in result.text,
    )


# ------------------------------------------------------------
# E. Style-based heading extraction
# ------------------------------------------------------------

print()
print("=== E. STYLE-BASED HEADING CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "styled.docx"

    write_docx(
        path,
        doc_xml(
            paragraph(
                "Main Heading",
                "Heading1",
            ),
            paragraph(
                "Section Heading",
                "Heading2",
            ),
            paragraph(
                "Body paragraph.",
            ),
        ),
    )

    result = extractor.extract_docx_upload_v1(
        path
    )

    check(
        "DOCX_STYLE_BASED_HEADINGS_EXTRACTED",
        result.headings
        == [
            "Main Heading",
            "Section Heading",
        ],
    )

    check(
        "DOCX_HEADING_METHOD_STYLE_BASED",
        result.metadata.get(
            "heading_method"
        )
        == "style_based",
    )

    check(
        "DOCX_TITLE_USES_FIRST_HEADING",
        result.title
        == "Main Heading",
    )

    check(
        "DOCX_STYLE_HELPER_RECOGNIZES_HEADING_IDS",
        "heading" in style_source,
    )


# ------------------------------------------------------------
# F. Heuristic fallback
# ------------------------------------------------------------

print()
print("=== F. HEURISTIC FALLBACK CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "heuristic.docx"

    write_docx(
        path,
        doc_xml(
            paragraph(
                "Possible Heading"
            ),
            paragraph(
                "This is a normal paragraph that ends with a period."
            ),
        ),
    )

    result = extractor.extract_docx_upload_v1(
        path
    )

    check(
        "DOCX_HEURISTIC_FALLBACK_USED_WITHOUT_STYLES",
        result.metadata.get(
            "heading_method"
        )
        == "heuristic_fallback",
    )

    check(
        "DOCX_HEURISTIC_HEADING_AVAILABLE",
        "Possible Heading"
        in result.headings,
    )

    check(
        "DOCX_TITLE_USES_HEURISTIC_FIRST_HEADING",
        result.title
        == result.headings[0],
    )


# ------------------------------------------------------------
# G. Title fallback when no heading is found
# ------------------------------------------------------------

print()
print("=== G. TITLE FALLBACK ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "fallback_title.docx"

    write_docx(
        path,
        doc_xml(
            paragraph(
                "this is a normal paragraph ending with a period."
            ),
            paragraph(
                "another normal paragraph ending with a period."
            ),
        ),
    )

    result = extractor.extract_docx_upload_v1(
        path
    )

    check(
        "DOCX_NO_HEADING_USES_FILENAME_STEM",
        result.title
        == "fallback_title",
    )


# ------------------------------------------------------------
# H. Empty DOCX contract
# ------------------------------------------------------------

print()
print("=== H. EMPTY DOCX CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "empty.docx"

    write_docx(
        path,
        doc_xml(),
    )

    result = extractor.extract_docx_upload_v1(
        path
    )

    check(
        "EMPTY_DOCX_RETURNS_EMPTY_TEXT",
        result.extraction_status
        == "empty_text",
    )

    check(
        "EMPTY_DOCX_CONFIDENCE_ZERO",
        result.extraction_confidence
        == 0.0,
    )

    check(
        "EMPTY_DOCX_PARAGRAPH_COUNT_ZERO",
        result.metadata.get(
            "paragraph_count"
        )
        == 0,
    )


# ------------------------------------------------------------
# I. Invalid DOCX contract
# ------------------------------------------------------------

print()
print("=== I. INVALID DOCX CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "invalid.docx"

    with ZipFile(
        path,
        "w",
        compression=ZIP_DEFLATED,
    ) as archive:
        archive.writestr(
            "word/other.xml",
            "<root/>",
        )

    result = extractor.extract_docx_upload_v1(
        path
    )

    check(
        "DOCX_WITHOUT_DOCUMENT_XML_RETURNS_INVALID_DOCX",
        result.extraction_status
        == "invalid_docx",
    )

    check(
        "INVALID_DOCX_CONFIDENCE_ZERO",
        result.extraction_confidence
        == 0.0,
    )

    check(
        "INVALID_DOCX_ERROR_IS_STRUCTURED",
        isinstance(
            result.metadata,
            dict,
        )
        and result.metadata.get(
            "error"
        )
        == "word/document.xml not found in DOCX archive.",
    )


# ------------------------------------------------------------
# J. General processing failure contract
# ------------------------------------------------------------

print()
print("=== J. EXTRACTION ERROR CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "broken.docx"

    path.write_bytes(
        b"this is not a zip archive"
    )

    result = extractor.extract_docx_upload_v1(
        path
    )

    check(
        "BROKEN_DOCX_RETURNS_CANONICAL_TYPE",
        isinstance(
            result,
            extractor.UploadExtractionResult,
        ),
    )

    check(
        "BROKEN_DOCX_RETURNS_EXTRACTION_ERROR",
        result.extraction_status
        == "extraction_error",
    )

    check(
        "BROKEN_DOCX_CONFIDENCE_ZERO",
        result.extraction_confidence
        == 0.0,
    )

    check(
        "BROKEN_DOCX_ERROR_REMAINS_STRUCTURED",
        isinstance(
            result.metadata,
            dict,
        )
        and "error"
        in result.metadata,
    )


# ------------------------------------------------------------
# K. Success result / metadata contract
# ------------------------------------------------------------

print()
print("=== K. SUCCESS RESULT / METADATA CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "article.docx"

    write_docx(
        path,
        doc_xml(
            paragraph(
                "Article Title",
                "Heading1",
            ),
            paragraph(
                "Paragraph one."
            ),
            paragraph(
                "Section",
                "Heading2",
            ),
            paragraph(
                "Paragraph two."
            ),
        ),
    )

    result = extractor.extract_docx_upload_v1(
        path
    )

    check(
        "DOCX_RESULT_IS_CANONICAL_TYPE",
        isinstance(
            result,
            extractor.UploadExtractionResult,
        ),
    )

    check(
        "DOCX_SOURCE_TYPE",
        result.source_type == "docx",
    )

    check(
        "DOCX_TITLE_IS_STRING",
        isinstance(result.title, str),
    )

    check(
        "DOCX_TEXT_IS_NONEMPTY_STRING",
        isinstance(result.text, str)
        and bool(result.text),
    )

    check(
        "DOCX_HEADINGS_LIST_OF_STRINGS",
        isinstance(result.headings, list)
        and all(
            isinstance(item, str)
            for item in result.headings
        ),
    )

    check(
        "DOCX_METADATA_IS_DICT",
        isinstance(result.metadata, dict),
    )

    check(
        "DOCX_STATUS_SUCCESS",
        result.extraction_status
        == "success",
    )

    check(
        "DOCX_CONFIDENCE_NUMERIC",
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
        "DOCX_CREATED_AT_IS_ISO_TIMESTAMP",
        created_ok,
    )

    required_metadata = {
        "filename",
        "extension",
        "extractor",
        "normalized_char_count",
        "line_count",
        "paragraph_count",
        "heading_count",
        "heading_method",
        "method",
    }

    check(
        "DOCX_METADATA_HAS_REQUIRED_KEYS",
        required_metadata.issubset(
            set(result.metadata.keys())
        ),
    )

    check(
        "DOCX_METADATA_FILENAME",
        result.metadata.get(
            "filename"
        )
        == "article.docx",
    )

    check(
        "DOCX_METADATA_EXTENSION",
        result.metadata.get(
            "extension"
        )
        == ".docx",
    )

    check(
        "DOCX_METADATA_EXTRACTOR_IDENTITY",
        result.metadata.get(
            "extractor"
        )
        == "extract_docx_upload_v1",
    )

    check(
        "DOCX_METADATA_METHOD",
        result.metadata.get(
            "method"
        )
        == "zipfile_word_document_xml_v2",
    )

    check(
        "DOCX_NORMALIZED_CHAR_COUNT_MATCHES_TEXT",
        result.metadata.get(
            "normalized_char_count"
        )
        == len(result.text),
    )

    check(
        "DOCX_LINE_COUNT_MATCHES_TEXT",
        result.metadata.get(
            "line_count"
        )
        == len(result.text.splitlines()),
    )

    check(
        "DOCX_PARAGRAPH_COUNT_MATCHES_PARSED_PARAGRAPHS",
        result.metadata.get(
            "paragraph_count"
        )
        == 4,
    )

    check(
        "DOCX_HEADING_COUNT_MATCHES_HEADINGS",
        result.metadata.get(
            "heading_count"
        )
        == len(result.headings),
    )


# ------------------------------------------------------------
# L. Confidence differentiation
# ------------------------------------------------------------

print()
print("=== L. CONFIDENCE CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    styled_path = root / "styled.docx"
    heuristic_path = root / "heuristic.docx"

    write_docx(
        styled_path,
        doc_xml(
            paragraph(
                "Styled Heading",
                "Heading1",
            ),
            paragraph(
                "Body paragraph."
            ),
        ),
    )

    write_docx(
        heuristic_path,
        doc_xml(
            paragraph(
                "Heuristic Heading"
            ),
            paragraph(
                "Body paragraph ending with a period."
            ),
        ),
    )

    styled_result = extractor.extract_docx_upload_v1(
        styled_path
    )

    heuristic_result = extractor.extract_docx_upload_v1(
        heuristic_path
    )

    check(
        "STYLE_BASED_CONFIDENCE_GREATER_THAN_HEURISTIC",
        styled_result.extraction_confidence
        > heuristic_result.extraction_confidence,
    )


# ------------------------------------------------------------
# M. Source immutability
# ------------------------------------------------------------

print()
print("=== M. SOURCE IMMUTABILITY ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "immutable.docx"

    write_docx(
        path,
        doc_xml(
            paragraph(
                "Heading",
                "Heading1",
            ),
            paragraph(
                "Original body."
            ),
        ),
    )

    before = path.read_bytes()

    extractor.extract_docx_upload_v1(
        path
    )

    after = path.read_bytes()

    check(
        "DOCX_SOURCE_BYTES_UNCHANGED",
        before == after,
    )

check(
    "DOCX_HAS_NO_SOURCE_MUTATION_CALLS",
    "write_text(" not in docx_source
    and "write_bytes(" not in docx_source
    and ".unlink(" not in docx_source
    and ".rename(" not in docx_source
    and ".replace(" not in docx_source,
)


# ------------------------------------------------------------
# N. Cross-format / downstream isolation
# ------------------------------------------------------------

print()
print("=== N. CROSS-FORMAT / DOWNSTREAM ISOLATION ===")

check(
    "DOCX_DOES_NOT_CALL_TXT_EXTRACTOR",
    "extract_txt_upload_v1"
    not in docx_source,
)

check(
    "DOCX_DOES_NOT_CALL_MARKDOWN_EXTRACTOR",
    "extract_markdown_upload_v1"
    not in docx_source,
)

check(
    "DOCX_DOES_NOT_CALL_HTML_EXTRACTOR",
    "extract_html_upload_v1"
    not in docx_source,
)

check(
    "DOCX_DOES_NOT_CALL_WEBSITE_CLEANERS",
    "article_body_cleaning_engine"
    not in docx_source
    and "article_cleaning_pipeline"
    not in docx_source
    and "raw_website_html"
    not in docx_source,
)

check(
    "DOCX_DOES_NOT_CALL_URL_ACQUISITION",
    "/api/urls/import"
    not in docx_source
    and "site_reader"
    not in docx_source,
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
        f"DOCX_DOES_NOT_INVOKE_{forbidden.upper()}",
        forbidden not in docx_source,
    )


# ------------------------------------------------------------
# O. Legacy v1 helper non-use
# ------------------------------------------------------------

print()
print("=== O. LEGACY V1 HELPER NON-USE ===")

check(
    "CANONICAL_DOCX_EXTRACTOR_DOES_NOT_USE_V1_PARAGRAPH_HELPER",
    "_extract_docx_paragraphs_v1"
    not in docx_source,
)

check(
    "CANONICAL_DOCX_EXTRACTOR_DOES_NOT_USE_V1_HEADING_HELPER",
    "_extract_docx_headings_v1"
    not in docx_source,
)

check(
    "CANONICAL_DOCX_EXTRACTOR_USES_V2_HEADING_HELPER",
    "_extract_docx_headings_v2"
    in docx_source,
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
        "U6.7_DOCX_EXTRACTOR_CONTRACT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U6.7 DOCX extractor contract verification failed."
    )

print(
    "U6.7_DOCX_EXTRACTOR_CONTRACT: CERTIFIED"
)

print(
    "U6.7_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U6.8_TITLE_EXTRACTION_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U6.7_FINAL_DOCX_EXTRACTOR_VERIFICATION: PASS"
)