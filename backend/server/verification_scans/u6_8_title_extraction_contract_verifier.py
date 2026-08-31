from __future__ import annotations

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


print("=== U6.8 - TITLE EXTRACTION CONTRACT ===")


# ------------------------------------------------------------
# A. TXT title contract
# ------------------------------------------------------------

print()
print("=== A. TXT TITLE CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "plain_document.txt"

    path.write_text(
        "THIS LOOKS LIKE A HEADING\n\nBody paragraph.",
        encoding="utf-8",
    )

    result = extractor.extract_txt_upload_v1(
        path
    )

    check(
        "TXT_TITLE_USES_FILENAME_STEM_ONLY",
        result.title == "plain_document",
    )

    check(
        "TXT_TITLE_IS_STRING",
        isinstance(result.title, str),
    )

    check(
        "TXT_TITLE_NOT_NULL",
        result.title is not None,
    )


# ------------------------------------------------------------
# B. Markdown title contract
# ------------------------------------------------------------

print()
print("=== B. MARKDOWN TITLE CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    heading_path = root / "article.md"
    heading_path.write_text(
        "# Markdown Title\n\nBody.",
        encoding="utf-8",
    )

    fallback_path = root / "fallback.markdown"
    fallback_path.write_text(
        "Body without a heading.",
        encoding="utf-8",
    )

    alias_md = root / "alias.md"
    alias_md.write_text(
        "# Same Title\n\nBody.",
        encoding="utf-8",
    )

    alias_markdown = root / "alias.markdown"
    alias_markdown.write_text(
        "# Same Title\n\nBody.",
        encoding="utf-8",
    )

    heading_result = extractor.extract_markdown_upload_v1(
        heading_path
    )

    fallback_result = extractor.extract_markdown_upload_v1(
        fallback_path
    )

    alias_md_result = extractor.extract_markdown_upload_v1(
        alias_md
    )

    alias_markdown_result = extractor.extract_markdown_upload_v1(
        alias_markdown
    )

    check(
        "MARKDOWN_FIRST_HEADING_IS_TITLE",
        heading_result.title
        == "Markdown Title",
    )

    check(
        "MARKDOWN_FILENAME_STEM_FALLBACK",
        fallback_result.title
        == "fallback",
    )

    check(
        "MARKDOWN_ALIAS_TITLE_SEMANTICS_MATCH",
        alias_md_result.title
        == alias_markdown_result.title
        == "Same Title",
    )

    check(
        "MARKDOWN_TITLE_IS_STRING",
        isinstance(
            heading_result.title,
            str,
        )
        and isinstance(
            fallback_result.title,
            str,
        ),
    )


# ------------------------------------------------------------
# C. HTML title contract
# ------------------------------------------------------------

print()
print("=== C. HTML TITLE CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    title_path = root / "title.html"
    title_path.write_text(
        "<html><head><title>HTML Title</title></head>"
        "<body><h1>H1 Title</h1></body></html>",
        encoding="utf-8",
    )

    h1_path = root / "h1.htm"
    h1_path.write_text(
        "<html><body><h1>H1 Fallback</h1><p>Body.</p></body></html>",
        encoding="utf-8",
    )

    filename_path = root / "filename_only.html"
    filename_path.write_text(
        "<html><body><p>Body.</p></body></html>",
        encoding="utf-8",
    )

    alias_html = root / "alias.html"
    alias_html.write_text(
        "<html><head><title>Same HTML Title</title></head>"
        "<body><p>Body.</p></body></html>",
        encoding="utf-8",
    )

    alias_htm = root / "alias.htm"
    alias_htm.write_text(
        "<html><head><title>Same HTML Title</title></head>"
        "<body><p>Body.</p></body></html>",
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

    alias_html_result = extractor.extract_html_upload_v1(
        alias_html
    )

    alias_htm_result = extractor.extract_html_upload_v1(
        alias_htm
    )

    check(
        "HTML_TITLE_TAG_PRIORITY",
        title_result.title
        == "HTML Title",
    )

    check(
        "HTML_H1_FALLBACK",
        h1_result.title
        == "H1 Fallback",
    )

    check(
        "HTML_FILENAME_STEM_FALLBACK",
        filename_result.title
        == "filename_only",
    )

    check(
        "HTML_ALIAS_TITLE_SEMANTICS_MATCH",
        alias_html_result.title
        == alias_htm_result.title
        == "Same HTML Title",
    )

    check(
        "HTML_TITLE_IS_STRING",
        isinstance(
            title_result.title,
            str,
        )
        and isinstance(
            h1_result.title,
            str,
        )
        and isinstance(
            filename_result.title,
            str,
        ),
    )


# ------------------------------------------------------------
# D. DOCX title contract
# ------------------------------------------------------------

print()
print("=== D. DOCX TITLE CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    heading_path = root / "heading.docx"

    write_docx(
        heading_path,
        docx_xml(
            docx_paragraph(
                "DOCX Title",
                "Heading1",
            ),
            docx_paragraph(
                "Body paragraph."
            ),
        ),
    )

    fallback_path = root / "fallback_docx.docx"

    write_docx(
        fallback_path,
        docx_xml(
            docx_paragraph(
                "this is a normal paragraph ending with a period."
            ),
            docx_paragraph(
                "another normal paragraph ending with a period."
            ),
        ),
    )

    heading_result = extractor.extract_docx_upload_v1(
        heading_path
    )

    fallback_result = extractor.extract_docx_upload_v1(
        fallback_path
    )

    check(
        "DOCX_FIRST_HEADING_IS_TITLE",
        heading_result.title
        == "DOCX Title",
    )

    check(
        "DOCX_FILENAME_STEM_FALLBACK",
        fallback_result.title
        == "fallback_docx",
    )

    check(
        "DOCX_TITLE_IS_STRING",
        isinstance(
            heading_result.title,
            str,
        )
        and isinstance(
            fallback_result.title,
            str,
        ),
    )


# ------------------------------------------------------------
# E. Failure-result safe title contract
# ------------------------------------------------------------

print()
print("=== E. FAILURE RESULT TITLE CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    missing_txt = extractor.extract_txt_upload_v1(
        root / "missing.txt"
    )

    missing_md = extractor.extract_markdown_upload_v1(
        root / "missing.md"
    )

    missing_html = extractor.extract_html_upload_v1(
        root / "missing.html"
    )

    missing_docx = extractor.extract_docx_upload_v1(
        root / "missing.docx"
    )

    unsupported = extractor.extract_upload_document_v1(
        root / "unsupported.pdf"
    )

    failure_results = [
        missing_txt,
        missing_md,
        missing_html,
        missing_docx,
        unsupported,
    ]

    check(
        "FAILURE_RESULTS_ALWAYS_HAVE_STRING_TITLE",
        all(
            isinstance(result.title, str)
            for result in failure_results
        ),
    )

    check(
        "FAILURE_RESULTS_NEVER_HAVE_NULL_TITLE",
        all(
            result.title is not None
            for result in failure_results
        ),
    )

    check(
        "FAILURE_TITLES_USE_SAFE_FILENAME_STEM",
        missing_txt.title == "missing"
        and missing_md.title == "missing"
        and missing_html.title == "missing"
        and missing_docx.title == "missing"
        and unsupported.title == "unsupported",
    )


# ------------------------------------------------------------
# F. Serialization preservation
# ------------------------------------------------------------

print()
print("=== F. TITLE SERIALIZATION CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "serialized.md"

    path.write_text(
        "# Serialized Title\n\nBody.",
        encoding="utf-8",
    )

    result = extractor.extract_markdown_upload_v1(
        path
    )

    serialized = (
        extractor.serialize_upload_extraction_result(
            result
        )
    )

    check(
        "SERIALIZER_PRESERVES_TITLE",
        serialized.get("title")
        == result.title
        == "Serialized Title",
    )


# ------------------------------------------------------------
# G. Downstream isolation
# ------------------------------------------------------------

print()
print("=== G. TITLE DOWNSTREAM ISOLATION ===")

title_sources = "\n".join(
    [
        extractor.extract_txt_upload_v1.__name__,
        extractor.extract_markdown_upload_v1.__name__,
        extractor.extract_html_upload_v1.__name__,
        extractor.extract_docx_upload_v1.__name__,
    ]
)

import inspect

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
            extractor._extract_html_title_v1
        ).lower(),
    ]
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
        f"TITLE_LOGIC_DOES_NOT_DEPEND_ON_{forbidden.upper()}",
        forbidden not in combined_source,
    )


# ------------------------------------------------------------
# H. Source immutability
# ------------------------------------------------------------

print()
print("=== H. TITLE EXTRACTION SOURCE IMMUTABILITY ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "immutable.md"

    path.write_text(
        "# Immutable Title\n\nBody.",
        encoding="utf-8",
    )

    before = path.read_bytes()

    extractor.extract_markdown_upload_v1(
        path
    )

    after = path.read_bytes()

    check(
        "TITLE_EXTRACTION_DOES_NOT_MUTATE_SOURCE",
        before == after,
    )


# ------------------------------------------------------------
# I. Conflicting title derivation within live upload path
# ------------------------------------------------------------

print()
print("=== I. LIVE UPLOAD TITLE DERIVATION CONSISTENCY ===")

intake_module = __import__(
    "backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake",
    fromlist=["run_upload_intake"],
)

intake_source = inspect.getsource(
    intake_module.run_upload_intake
).lower()

check(
    "INTAKE_DOES_NOT_REDERIVE_TITLE",
    "result.title =" not in intake_source
    and "title =" not in intake_source,
)

check(
    "TITLE_DERIVATION_REMAINS_FORMAT_SPECIFIC",
    'title=p.stem'
    in inspect.getsource(
        extractor.extract_txt_upload_v1
    ).replace(" ", "").lower()
    or "title=p.stem"
    in inspect.getsource(
        extractor.extract_txt_upload_v1
    ).replace(" ", "").lower(),
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
        "U6.8_TITLE_EXTRACTION_CONTRACT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U6.8 title extraction contract verification failed."
    )

print(
    "U6.8_TITLE_EXTRACTION_CONTRACT: CERTIFIED"
)

print(
    "U6.8_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U6.9_HEADING_EXTRACTION_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U6.8_FINAL_TITLE_EXTRACTION_VERIFICATION: PASS"
)