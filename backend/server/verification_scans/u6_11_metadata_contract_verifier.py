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


def docx_paragraph(
    text: str,
    style_id: str = "",
) -> str:
    style = ""

    if style_id:
        style = (
            "<w:pPr>"
            f'<w:pStyle w:val="{style_id}"/>'
            "</w:pPr>"
        )

    return (
        "<w:p>"
        f"{style}"
        "<w:r>"
        f"<w:t>{text}</w:t>"
        "</w:r>"
        "</w:p>"
    )


print("=== U6.11 - METADATA CONTRACT ===")


# ------------------------------------------------------------
# A. Common metadata type / base fields
# ------------------------------------------------------------

print()
print("=== A. COMMON METADATA CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    txt = root / "sample.txt"
    txt.write_text(
        "Paragraph one.\n\nParagraph two.",
        encoding="utf-8",
    )

    md = root / "sample.md"
    md.write_text(
        "# Heading\n\nBody.",
        encoding="utf-8",
    )

    html = root / "sample.html"
    html.write_text(
        "<html><body><h1>Heading</h1><p>Body.</p></body></html>",
        encoding="utf-8",
    )

    docx = root / "sample.docx"
    write_docx(
        docx,
        docx_xml(
            docx_paragraph(
                "Heading",
                "Heading1",
            ),
            docx_paragraph(
                "Body."
            ),
        ),
    )

    success_results = [
        extractor.extract_txt_upload_v1(txt),
        extractor.extract_markdown_upload_v1(md),
        extractor.extract_html_upload_v1(html),
        extractor.extract_docx_upload_v1(docx),
    ]

    check(
        "METADATA_ALWAYS_DICTIONARY_ON_SUCCESS",
        all(
            isinstance(result.metadata, dict)
            for result in success_results
        ),
    )

    check(
        "SUCCESS_METADATA_HAS_FILENAME",
        all(
            "filename" in result.metadata
            for result in success_results
        ),
    )

    check(
        "SUCCESS_METADATA_HAS_EXTENSION",
        all(
            "extension" in result.metadata
            for result in success_results
        ),
    )

    check(
        "SUCCESS_METADATA_HAS_PHASE",
        all(
            "phase" in result.metadata
            for result in success_results
        ),
    )

    check(
        "SUCCESS_METADATA_HAS_EXTRACTOR_IDENTITY",
        all(
            "extractor" in result.metadata
            for result in success_results
        ),
    )


# ------------------------------------------------------------
# B. TXT success metadata
# ------------------------------------------------------------

print()
print("=== B. TXT SUCCESS METADATA ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "article.txt"

    raw = "Paragraph one.\n\nParagraph two."

    path.write_text(
        raw,
        encoding="utf-8",
    )

    result = extractor.extract_txt_upload_v1(
        path
    )

    required = {
        "filename",
        "extension",
        "phase",
        "extractor",
        "raw_char_count",
        "normalized_char_count",
        "line_count",
        "paragraph_count",
    }

    check(
        "TXT_METADATA_REQUIRED_KEYS",
        required.issubset(
            result.metadata.keys()
        ),
    )

    check(
        "TXT_METADATA_FILENAME_CORRECT",
        result.metadata.get("filename")
        == "article.txt",
    )

    check(
        "TXT_METADATA_EXTENSION_CORRECT",
        result.metadata.get("extension")
        == ".txt",
    )

    check(
        "TXT_METADATA_EXTRACTOR_CORRECT",
        result.metadata.get("extractor")
        == "extract_txt_upload_v1",
    )

    check(
        "TXT_RAW_CHAR_COUNT_CORRECT",
        result.metadata.get(
            "raw_char_count"
        )
        == len(raw),
    )

    check(
        "TXT_NORMALIZED_CHAR_COUNT_CORRECT",
        result.metadata.get(
            "normalized_char_count"
        )
        == len(result.text),
    )

    check(
        "TXT_LINE_COUNT_CORRECT",
        result.metadata.get(
            "line_count"
        )
        == len(result.text.splitlines()),
    )

    check(
        "TXT_PARAGRAPH_COUNT_CORRECT",
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
# C. Markdown success metadata
# ------------------------------------------------------------

print()
print("=== C. MARKDOWN SUCCESS METADATA ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "article.markdown"

    raw = "# Main Heading\n\nParagraph."

    path.write_text(
        raw,
        encoding="utf-8",
    )

    result = extractor.extract_markdown_upload_v1(
        path
    )

    required = {
        "filename",
        "extension",
        "phase",
        "extractor",
        "raw_char_count",
        "normalized_char_count",
        "line_count",
        "paragraph_count",
        "heading_count",
    }

    check(
        "MARKDOWN_METADATA_REQUIRED_KEYS",
        required.issubset(
            result.metadata.keys()
        ),
    )

    check(
        "MARKDOWN_METADATA_EXTENSION_CORRECT",
        result.metadata.get("extension")
        == ".markdown",
    )

    check(
        "MARKDOWN_METADATA_EXTRACTOR_CORRECT",
        result.metadata.get("extractor")
        == "extract_markdown_upload_v1",
    )

    check(
        "MARKDOWN_RAW_CHAR_COUNT_CORRECT",
        result.metadata.get(
            "raw_char_count"
        )
        == len(raw),
    )

    check(
        "MARKDOWN_NORMALIZED_CHAR_COUNT_CORRECT",
        result.metadata.get(
            "normalized_char_count"
        )
        == len(result.text),
    )

    check(
        "MARKDOWN_HEADING_COUNT_CORRECT",
        result.metadata.get(
            "heading_count"
        )
        == len(result.headings),
    )


# ------------------------------------------------------------
# D. HTML success metadata
# ------------------------------------------------------------

print()
print("=== D. HTML SUCCESS METADATA ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "article.htm"

    raw = (
        "<html><body>"
        "<h1>Main Heading</h1>"
        "<p>Paragraph.</p>"
        "</body></html>"
    )

    path.write_text(
        raw,
        encoding="utf-8",
    )

    result = extractor.extract_html_upload_v1(
        path
    )

    required = {
        "filename",
        "extension",
        "phase",
        "extractor",
        "raw_char_count",
        "normalized_char_count",
        "line_count",
        "paragraph_count",
        "heading_count",
    }

    check(
        "HTML_METADATA_REQUIRED_KEYS",
        required.issubset(
            result.metadata.keys()
        ),
    )

    check(
        "HTML_METADATA_EXTENSION_CORRECT",
        result.metadata.get("extension")
        == ".htm",
    )

    check(
        "HTML_METADATA_EXTRACTOR_CORRECT",
        result.metadata.get("extractor")
        == "extract_html_upload_v1",
    )

    check(
        "HTML_RAW_CHAR_COUNT_CORRECT",
        result.metadata.get(
            "raw_char_count"
        )
        == len(raw),
    )

    check(
        "HTML_NORMALIZED_CHAR_COUNT_CORRECT",
        result.metadata.get(
            "normalized_char_count"
        )
        == len(result.text),
    )

    check(
        "HTML_HEADING_COUNT_CORRECT",
        result.metadata.get(
            "heading_count"
        )
        == len(result.headings),
    )


# ------------------------------------------------------------
# E. DOCX success metadata
# ------------------------------------------------------------

print()
print("=== E. DOCX SUCCESS METADATA ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "article.docx"

    write_docx(
        path,
        docx_xml(
            docx_paragraph(
                "Main Heading",
                "Heading1",
            ),
            docx_paragraph(
                "Body paragraph."
            ),
        ),
    )

    result = extractor.extract_docx_upload_v1(
        path
    )

    required = {
        "filename",
        "extension",
        "phase",
        "extractor",
        "normalized_char_count",
        "line_count",
        "paragraph_count",
        "heading_count",
        "heading_method",
        "method",
    }

    check(
        "DOCX_METADATA_REQUIRED_KEYS",
        required.issubset(
            result.metadata.keys()
        ),
    )

    check(
        "DOCX_METADATA_FILENAME_CORRECT",
        result.metadata.get("filename")
        == "article.docx",
    )

    check(
        "DOCX_METADATA_EXTENSION_CORRECT",
        result.metadata.get("extension")
        == ".docx",
    )

    check(
        "DOCX_METADATA_EXTRACTOR_CORRECT",
        result.metadata.get("extractor")
        == "extract_docx_upload_v1",
    )

    check(
        "DOCX_NORMALIZED_CHAR_COUNT_CORRECT",
        result.metadata.get(
            "normalized_char_count"
        )
        == len(result.text),
    )

    check(
        "DOCX_LINE_COUNT_CORRECT",
        result.metadata.get(
            "line_count"
        )
        == len(result.text.splitlines()),
    )

    check(
        "DOCX_HEADING_COUNT_CORRECT",
        result.metadata.get(
            "heading_count"
        )
        == len(result.headings),
    )

    check(
        "DOCX_HEADING_METHOD_RECORDED",
        result.metadata.get(
            "heading_method"
        )
        in {
            "style_based",
            "heuristic_fallback",
        },
    )

    check(
        "DOCX_EXTRACTION_METHOD_RECORDED",
        result.metadata.get("method")
        == "zipfile_word_document_xml_v2",
    )


# ------------------------------------------------------------
# F. Alias physical extension metadata
# ------------------------------------------------------------

print()
print("=== F. FORMAT ALIAS METADATA ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    md = root / "alias.md"
    markdown = root / "alias.markdown"

    md.write_text(
        "# Heading\n\nBody.",
        encoding="utf-8",
    )

    markdown.write_text(
        "# Heading\n\nBody.",
        encoding="utf-8",
    )

    html = root / "alias.html"
    htm = root / "alias.htm"

    html.write_text(
        "<h1>Heading</h1><p>Body.</p>",
        encoding="utf-8",
    )

    htm.write_text(
        "<h1>Heading</h1><p>Body.</p>",
        encoding="utf-8",
    )

    md_result = extractor.extract_markdown_upload_v1(
        md
    )

    markdown_result = extractor.extract_markdown_upload_v1(
        markdown
    )

    html_result = extractor.extract_html_upload_v1(
        html
    )

    htm_result = extractor.extract_html_upload_v1(
        htm
    )

    check(
        "MD_ALIAS_PRESERVES_PHYSICAL_EXTENSION",
        md_result.metadata.get("extension")
        == ".md",
    )

    check(
        "MARKDOWN_ALIAS_PRESERVES_PHYSICAL_EXTENSION",
        markdown_result.metadata.get(
            "extension"
        )
        == ".markdown",
    )

    check(
        "HTML_ALIAS_PRESERVES_PHYSICAL_EXTENSION",
        html_result.metadata.get(
            "extension"
        )
        == ".html",
    )

    check(
        "HTM_ALIAS_PRESERVES_PHYSICAL_EXTENSION",
        htm_result.metadata.get(
            "extension"
        )
        == ".htm",
    )


# ------------------------------------------------------------
# G. Failure metadata contract
# ------------------------------------------------------------

print()
print("=== G. FAILURE METADATA CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    missing = [
        extractor.extract_txt_upload_v1(
            root / "missing.txt"
        ),
        extractor.extract_markdown_upload_v1(
            root / "missing.md"
        ),
        extractor.extract_html_upload_v1(
            root / "missing.html"
        ),
        extractor.extract_docx_upload_v1(
            root / "missing.docx"
        ),
    ]

    unsupported = extractor.extract_upload_document_v1(
        root / "missing.pdf"
    )

    failure_results = missing + [unsupported]

    check(
        "FAILURE_METADATA_ALWAYS_DICTIONARY",
        all(
            isinstance(result.metadata, dict)
            for result in failure_results
        ),
    )

    check(
        "FAILURE_METADATA_HAS_SAFE_BASE_FIELDS",
        all(
            {
                "filename",
                "extension",
                "phase",
                "extractor",
            }.issubset(
                result.metadata.keys()
            )
            for result in failure_results
        ),
    )

    check(
        "FAILURE_METADATA_HAS_STRUCTURED_ERROR_WHERE_APPLICABLE",
        all(
            isinstance(
                result.metadata.get("error"),
                str,
            )
            and bool(
                result.metadata.get("error")
            )
            for result in failure_results
        ),
    )


# ------------------------------------------------------------
# H. Metadata payload safety
# ------------------------------------------------------------

print()
print("=== H. METADATA PAYLOAD SAFETY ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "payload.txt"

    unique_text = (
        "UNIQUE_DOCUMENT_BODY_"
        "0123456789_ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    )

    path.write_text(
        unique_text,
        encoding="utf-8",
    )

    result = extractor.extract_txt_upload_v1(
        path
    )

    metadata_repr = repr(
        result.metadata
    )

    check(
        "METADATA_DOES_NOT_CONTAIN_RAW_BYTES",
        not any(
            isinstance(value, bytes)
            for value in result.metadata.values()
        ),
    )

    check(
        "METADATA_DOES_NOT_DUPLICATE_FULL_DOCUMENT_TEXT",
        unique_text not in metadata_repr,
    )


# ------------------------------------------------------------
# I. No downstream/runtime state in metadata
# ------------------------------------------------------------

print()
print("=== I. METADATA DOWNSTREAM ISOLATION ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "isolation.md"

    path.write_text(
        "# Heading\n\nBody.",
        encoding="utf-8",
    )

    result = extractor.extract_markdown_upload_v1(
        path
    )

    keys = {
        str(key).lower()
        for key in result.metadata.keys()
    }

    forbidden_fragments = {
        "uduc",
        "highlight",
        "active_target",
        "uucd",
        "semantic",
        "runtime",
        "scorer",
    }

    check(
        "METADATA_HAS_NO_DOWNSTREAM_STATE_KEYS",
        all(
            not any(
                fragment in key
                for fragment in forbidden_fragments
            )
            for key in keys
        ),
    )


# ------------------------------------------------------------
# J. Serialization preserves metadata
# ------------------------------------------------------------

print()
print("=== J. METADATA SERIALIZATION CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "serialized.html"

    path.write_text(
        "<h1>Heading</h1><p>Body.</p>",
        encoding="utf-8",
    )

    result = extractor.extract_html_upload_v1(
        path
    )

    serialized = (
        extractor.serialize_upload_extraction_result(
            result
        )
    )

    check(
        "SERIALIZER_PRESERVES_METADATA",
        serialized.get("metadata")
        == result.metadata,
    )


# ------------------------------------------------------------
# K. Intake consistency / non-rewrite
# ------------------------------------------------------------

print()
print("=== K. LIVE INTAKE METADATA CONSISTENCY ===")

intake_module = __import__(
    "backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake",
    fromlist=["run_upload_intake"],
)

intake_source = inspect.getsource(
    intake_module.run_upload_intake
).lower()

check(
    "INTAKE_DOES_NOT_REPLACE_RESULT_METADATA",
    "result.metadata =" not in intake_source,
)

check(
    "INTAKE_DOES_NOT_CLEAR_RESULT_METADATA",
    "result.metadata.clear(" not in intake_source,
)

check(
    "INTAKE_DOES_NOT_REBUILD_EXTRACTOR_METADATA",
    "metadata = {" not in intake_source,
)


# ------------------------------------------------------------
# L. Extractor-source metadata isolation
# ------------------------------------------------------------

print()
print("=== L. EXTRACTOR METADATA RESPONSIBILITY BOUNDARY ===")

combined_source = "\n".join(
    [
        inspect.getsource(
            extractor.extract_txt_upload_v1
        ).lower(),
        inspect.getsource(
            extractor.extract_markdown_upload_v1
        ).lower(),
        inspect.getsource(
            extractor.extract_html_upload_v1
        ).lower(),
        inspect.getsource(
            extractor.extract_docx_upload_v1
        ).lower(),
        inspect.getsource(
            extractor.build_empty_upload_result
        ).lower(),
    ]
)

for forbidden in (
    "active_target",
    "uucd",
    "semantic_score",
    "runtime_score",
    "scorer_output",
):
    check(
        f"EXTRACTOR_METADATA_DOES_NOT_CREATE_{forbidden.upper()}",
        forbidden not in combined_source,
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
        "U6.11_METADATA_CONTRACT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U6.11 metadata contract verification failed."
    )

print(
    "U6.11_METADATA_CONTRACT: CERTIFIED"
)

print(
    "U6.11_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U6.12_EXTRACTION_STATUS_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U6.11_FINAL_METADATA_VERIFICATION: PASS"
)