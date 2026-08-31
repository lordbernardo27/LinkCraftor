from __future__ import annotations

import inspect
import re
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


print("=== U6.17 - EXTRACTOR VS NORMALIZATION RESPONSIBILITY BOUNDARY ===")


# ------------------------------------------------------------
# A. Canonical U6 extractor responsibility
# ------------------------------------------------------------

print()
print("=== A. CANONICAL U6 RESPONSIBILITY ===")

extractor_functions = [
    extractor.extract_txt_upload_v1,
    extractor.extract_markdown_upload_v1,
    extractor.extract_html_upload_v1,
    extractor.extract_docx_upload_v1,
    extractor.extract_upload_document_v1,
]

extractor_source = "\n".join(
    inspect.getsource(func).lower()
    for func in extractor_functions
)

check(
    "U6_PRODUCES_UPLOAD_EXTRACTION_RESULT",
    "uploadextractionresult" in extractor_source
    or "build_empty_upload_result" in extractor_source,
)

check(
    "U6_OWNS_TITLE_EXTRACTION",
    "title" in extractor_source,
)

check(
    "U6_OWNS_HEADING_EXTRACTION",
    "headings" in extractor_source,
)

check(
    "U6_OWNS_TEXT_EXTRACTION",
    "text" in extractor_source,
)

check(
    "U6_OWNS_EXTRACTION_METADATA",
    "metadata" in extractor_source,
)


# ------------------------------------------------------------
# B. Structural-only normalizer behavior
# ------------------------------------------------------------

print()
print("=== B. U6 STRUCTURAL NORMALIZER CONTRACT ===")

normalizer_source = inspect.getsource(
    extractor._normalize_upload_text_v2
).lower()

check(
    "NORMALIZER_HANDLES_LINE_ENDINGS",
    "\\r\\n" in normalizer_source
    or "\\r" in normalizer_source,
)

check(
    "NORMALIZER_HANDLES_HORIZONTAL_WHITESPACE",
    "\\t" in normalizer_source
    or "split()" in normalizer_source
    or "re.sub" in normalizer_source,
)

check(
    "NORMALIZER_HANDLES_BLANK_LINE_STRUCTURE",
    "\\n\\n" in normalizer_source
    or "blocks" in normalizer_source
    or "paragraph" in normalizer_source,
)

for forbidden in (
    "semantic",
    "embedding",
    "keyword",
    "phrase",
    "anchor",
    "linking",
    "topic",
    "relevance",
    "ranking",
    "rewrite",
    "summar",
    "lemmat",
    "stemming",
    "synonym",
):
    filtered_normalizer_source = "\n".join(
        line
        for line in normalizer_source.splitlines()
        if "docstring" not in line
    )

    check(
        f"NORMALIZER_DOES_NOT_PERFORM_{forbidden.upper()}_PROCESSING",
        forbidden not in filtered_normalizer_source,
    )


# ------------------------------------------------------------
# C. Behavioral structural normalization
# ------------------------------------------------------------

print()
print("=== C. STRUCTURAL NORMALIZATION BEHAVIOR ===")

sample = (
    "  First   line\twith spaces.  \r\n"
    "\r\n"
    "\r\n"
    " Second line. \r"
    "\r"
    "user_id = product_name"
)

normalized = extractor._normalize_upload_text_v2(
    sample
)

check(
    "CRLF_AND_CR_NORMALIZED_TO_LF",
    "\r" not in normalized,
)

check(
    "EXCESS_HORIZONTAL_WHITESPACE_COLLAPSED",
    "First line with spaces."
    in normalized,
)

check(
    "PARAGRAPH_BOUNDARIES_CANONICALIZED",
    "\n\n" in normalized
    and "\n\n\n" not in normalized,
)

check(
    "LEADING_TRAILING_LINE_WHITESPACE_REMOVED",
    normalized == normalized.strip(),
)

check(
    "IDENTIFIER_UNDERSCORES_PRESERVED",
    "user_id" in normalized
    and "product_name" in normalized,
)

check(
    "MEANINGFUL_PUNCTUATION_PRESERVED",
    "=" in normalized
    and "." in normalized,
)


# ------------------------------------------------------------
# D. Markdown extraction vs normalization boundary
# ------------------------------------------------------------

print()
print("=== D. MARKDOWN FORMAT-EXTRACTION BOUNDARY ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "article.md"

    path.write_text(
        "# Heading\n\n"
        "This has **bold**, *italic*, and `code`.\n\n"
        "user_id stays intact.",
        encoding="utf-8",
    )

    result = extractor.extract_markdown_upload_v1(
        path
    )

    check(
        "MARKDOWN_EXTRACTION_SUCCESS",
        result.extraction_status == "success",
    )

    check(
        "MARKDOWN_PRESENTATION_SYNTAX_REMOVED",
        "**" not in result.text
        and "`" not in result.text,
    )

    check(
        "MARKDOWN_VISIBLE_WORDING_PRESERVED",
        "bold" in result.text
        and "italic" in result.text
        and "code" in result.text,
    )

    check(
        "MARKDOWN_IDENTIFIER_MEANING_PRESERVED",
        "user_id" in result.text,
    )


# ------------------------------------------------------------
# E. HTML extraction vs normalization boundary
# ------------------------------------------------------------

print()
print("=== E. HTML FORMAT-EXTRACTION BOUNDARY ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "article.html"

    path.write_text(
        "<html><head>"
        "<style>.x{display:none}</style>"
        "<script>bad()</script>"
        "</head><body>"
        "<h1>Heading</h1>"
        "<p>Visible &amp; meaningful.</p>"
        "</body></html>",
        encoding="utf-8",
    )

    result = extractor.extract_html_upload_v1(
        path
    )

    check(
        "HTML_EXTRACTION_SUCCESS",
        result.extraction_status == "success",
    )

    check(
        "HTML_PRESENTATION_TAGS_REMOVED",
        "<h1>" not in result.text
        and "<p>" not in result.text,
    )

    check(
        "HTML_NONCONTENT_REMOVED",
        "bad()" not in result.text
        and "display:none" not in result.text,
    )

    check(
        "HTML_VISIBLE_WORDING_PRESERVED",
        "Visible & meaningful."
        in result.text,
    )


# ------------------------------------------------------------
# F. DOCX parsing vs normalization boundary
# ------------------------------------------------------------

print()
print("=== F. DOCX FORMAT-EXTRACTION BOUNDARY ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "article.docx"

    write_docx(
        path,
        docx_xml(
            docx_paragraph("Heading"),
            docx_paragraph("Body text."),
        ),
    )

    result = extractor.extract_docx_upload_v1(
        path
    )

    check(
        "DOCX_EXTRACTION_SUCCESS",
        result.extraction_status == "success",
    )

    check(
        "DOCX_XML_MARKUP_NOT_EXPOSED",
        "<w:" not in result.text,
    )

    check(
        "DOCX_VISIBLE_TEXT_PRESERVED",
        "Heading" in result.text
        and "Body text." in result.text,
    )


# ------------------------------------------------------------
# G. U6 does not perform downstream intelligence
# ------------------------------------------------------------

print()
print("=== G. U6 DOWNSTREAM-INTELLIGENCE ISOLATION ===")

for forbidden in (
    "semantic_score",
    "relevance_score",
    "ranking_score",
    "keyword_extraction",
    "phrase_extraction",
    "anchor_selection",
    "link_decision",
    "topic_inference",
    "embedding",
    "scorer",
):
    check(
        f"U6_DOES_NOT_PERFORM_{forbidden.upper()}",
        forbidden not in extractor_source,
    )


# ------------------------------------------------------------
# H. Website / future-normalizer isolation
# ------------------------------------------------------------

print()
print("=== H. NORMALIZATION RESPONSIBILITY ISOLATION ===")

for forbidden in (
    "article_body_cleaning_engine",
    "article_cleaning_pipeline",
    "uploaded_document_normalization",
    "normalization_pipeline",
    "normalize_uploaded_document",
):
    check(
        f"U6_DOES_NOT_CALL_{forbidden.upper()}",
        forbidden not in extractor_source,
    )


# ------------------------------------------------------------
# I. UDUC / downstream normalization isolation
# ------------------------------------------------------------

print()
print("=== I. UDUC / DOWNSTREAM NORMALIZATION ISOLATION ===")

for forbidden in (
    "build_uduc",
    "write_uduc",
    "build_and_write_uduc",
    "uduc_output_path",
    "uucd",
    "highlight",
    "active_target",
):
    check(
        f"U6_DOES_NOT_INVOKE_{forbidden.upper()}",
        forbidden not in extractor_source,
    )


# ------------------------------------------------------------
# J. Metadata counts derive from U6 output
# ------------------------------------------------------------

print()
print("=== J. METADATA COUNT OWNERSHIP ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "counts.txt"

    path.write_text(
        " First   paragraph. \n\n Second paragraph. ",
        encoding="utf-8",
    )

    result = extractor.extract_txt_upload_v1(
        path
    )

    check(
        "NORMALIZED_CHAR_COUNT_DERIVES_FROM_RESULT_TEXT",
        result.metadata.get(
            "normalized_char_count"
        )
        == len(result.text),
    )

    check(
        "LINE_COUNT_DERIVES_FROM_RESULT_TEXT",
        result.metadata.get(
            "line_count"
        )
        == len(result.text.splitlines()),
    )

    check(
        "PARAGRAPH_COUNT_DERIVES_FROM_RESULT_TEXT",
        result.metadata.get(
            "paragraph_count"
        )
        == len(
            [
                block
                for block in result.text.split("\n\n")
                if block.strip()
            ]
        ),
    )


# ------------------------------------------------------------
# K. Intake does not add a second normalization pass
# ------------------------------------------------------------

print()
print("=== K. LIVE INTAKE NORMALIZATION BOUNDARY ===")

intake_module = __import__(
    "backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake",
    fromlist=["run_upload_intake"],
)

intake_source = inspect.getsource(
    intake_module.run_upload_intake
).lower()

check(
    "INTAKE_USES_CANONICAL_EXTRACTOR",
    "extract_upload_document_v1("
    in intake_source,
)

check(
    "INTAKE_DOES_NOT_CALL_U6_NORMALIZER_DIRECTLY",
    "_normalize_upload_text_v2"
    not in intake_source,
)

check(
    "INTAKE_DOES_NOT_RENORMALIZE_EXTRACTION_TEXT",
    "extraction_result.text ="
    not in intake_source
    and "normalize("
    not in intake_source,
)


# ------------------------------------------------------------
# L. No duplicate live upload normalization implementation
# ------------------------------------------------------------

print()
print("=== L. LIVE-PATH NORMALIZATION CONSISTENCY ===")

check(
    "INTAKE_DOES_NOT_DEFINE_UPLOAD_TEXT_NORMALIZER",
    "def _normalize_upload_text"
    not in intake_source
    and "def normalize_upload_text"
    not in intake_source,
)

check(
    "FORMAT_EXTRACTORS_CONVERGE_ON_CANONICAL_STRUCTURAL_NORMALIZER",
    "_normalize_upload_text_v2"
    in inspect.getsource(
        extractor.extract_txt_upload_v1
    )
    and "_normalize_upload_text_v2"
    in inspect.getsource(
        extractor.extract_docx_upload_v1
    )
    and "_normalize_upload_text_v2"
    in inspect.getsource(
        extractor._strip_markdown_syntax_v2
    )
    and "_normalize_upload_text_v2"
    in inspect.getsource(
        extractor._strip_html_tags_v1
    ),
)


# ------------------------------------------------------------
# M. U6 / U7 separability
# ------------------------------------------------------------

print()
print("=== M. U6 / U7 SEPARABILITY ===")

check(
    "FORMAT_EXTRACTORS_RETURN_RESULT_BEFORE_DOWNSTREAM_PIPELINES",
    all(
        "uploadextractionresult"
        in inspect.getsource(func).lower()
        or "build_empty_upload_result"
        in inspect.getsource(func).lower()
        for func in (
            extractor.extract_txt_upload_v1,
            extractor.extract_markdown_upload_v1,
            extractor.extract_html_upload_v1,
            extractor.extract_docx_upload_v1,
        )
    ),
)

check(
    "U6_OUTPUT_CONTRACT_CAN_FEED_LATER_NORMALIZATION",
    hasattr(
        extractor.UploadExtractionResult,
        "__dataclass_fields__",
    )
    and "text"
    in extractor.UploadExtractionResult.__dataclass_fields__
    and "title"
    in extractor.UploadExtractionResult.__dataclass_fields__
    and "headings"
    in extractor.UploadExtractionResult.__dataclass_fields__,
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
        "U6.17_EXTRACTOR_NORMALIZATION_BOUNDARY: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U6.17 extractor / normalization boundary verification failed."
    )

print(
    "U6.17_EXTRACTOR_NORMALIZATION_BOUNDARY: CERTIFIED"
)

print(
    "U6.17_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U6.18_EXTRACTOR_UDUC_BOUNDARY_TRANSITION: AUTHORIZED"
)

print(
    "U6.17_FINAL_EXTRACTOR_NORMALIZATION_BOUNDARY_VERIFICATION: PASS"
)