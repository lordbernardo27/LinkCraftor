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


print("=== U6.9 - HEADING EXTRACTION CONTRACT ===")


# ------------------------------------------------------------
# A. TXT heading contract
# ------------------------------------------------------------

print()
print("=== A. TXT HEADING CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "plain.txt"

    path.write_text(
        "THIS LOOKS LIKE A HEADING\n\n"
        "Body paragraph.",
        encoding="utf-8",
    )

    result = extractor.extract_txt_upload_v1(
        path
    )

    check(
        "TXT_HEADINGS_ALWAYS_EMPTY",
        result.headings == [],
    )

    check(
        "TXT_DOES_NOT_HEURISTICALLY_INFER_HEADINGS",
        "THIS LOOKS LIKE A HEADING"
        not in result.headings,
    )

    check(
        "TXT_HEADINGS_IS_LIST",
        isinstance(result.headings, list),
    )


# ------------------------------------------------------------
# B. Markdown heading contract
# ------------------------------------------------------------

print()
print("=== B. MARKDOWN HEADING CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "article.md"

    path.write_text(
        "# **Main** Title\n\n"
        "Body.\n\n"
        "## Section `One`\n\n"
        "Text.\n\n"
        "### [Section Two](https://example.com)\n",
        encoding="utf-8",
    )

    result = extractor.extract_markdown_upload_v1(
        path
    )

    check(
        "MARKDOWN_ATX_HEADINGS_EXTRACTED",
        result.headings
        == [
            "Main Title",
            "Section One",
            "Section Two",
        ],
    )

    check(
        "MARKDOWN_HEADING_ORDER_PRESERVED",
        result.headings[0]
        == "Main Title"
        and result.headings[-1]
        == "Section Two",
    )

    check(
        "MARKDOWN_INLINE_SYNTAX_REMOVED_FROM_HEADINGS",
        all(
            token not in " ".join(
                result.headings
            )
            for token in (
                "**",
                "`",
                "https://",
                "[",
                "]",
            )
        ),
    )

    check(
        "MARKDOWN_HEADING_COUNT_MATCHES",
        result.metadata.get(
            "heading_count"
        )
        == len(result.headings),
    )


# ------------------------------------------------------------
# C. Markdown fenced-code protection
# ------------------------------------------------------------

print()
print("=== C. MARKDOWN FENCED-CODE PROTECTION ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "fenced.md"

    path.write_text(
        "# Real Heading\n\n"
        "```python\n"
        "# Fake Heading\n"
        "```\n\n"
        "~~~text\n"
        "## Another Fake Heading\n"
        "~~~\n\n"
        "## Real Section\n",
        encoding="utf-8",
    )

    result = extractor.extract_markdown_upload_v1(
        path
    )

    check(
        "MARKDOWN_FENCED_HEADINGS_IGNORED",
        result.headings
        == [
            "Real Heading",
            "Real Section",
        ],
    )


# ------------------------------------------------------------
# D. HTML heading contract
# ------------------------------------------------------------

print()
print("=== D. HTML HEADING CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "headings.html"

    path.write_text(
        "<html><body>"
        "<h1>Main <strong>Heading</strong></h1>"
        "<p>Body.</p>"
        "<h2>Section &amp; Details</h2>"
        "<h3><em>Third</em> Heading</h3>"
        "<h4>Fourth</h4>"
        "<h5>Fifth</h5>"
        "<h6>Sixth</h6>"
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
            "Main Heading",
            "Section & Details",
            "Third Heading",
            "Fourth",
            "Fifth",
            "Sixth",
        ],
    )

    check(
        "HTML_HEADING_DOCUMENT_ORDER_PRESERVED",
        result.headings[0]
        == "Main Heading"
        and result.headings[-1]
        == "Sixth",
    )

    check(
        "HTML_NESTED_TAGS_REMOVED_FROM_HEADINGS",
        "<strong>" not in " ".join(
            result.headings
        )
        and "<em>" not in " ".join(
            result.headings
        ),
    )

    check(
        "HTML_HEADING_ENTITIES_DECODED",
        "Section & Details"
        in result.headings,
    )

    check(
        "HTML_HEADING_COUNT_MATCHES",
        result.metadata.get(
            "heading_count"
        )
        == len(result.headings),
    )


# ------------------------------------------------------------
# E. DOCX style-based heading contract
# ------------------------------------------------------------

print()
print("=== E. DOCX STYLE-BASED HEADING CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "styled.docx"

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
            docx_paragraph(
                "Section Heading",
                "Heading2",
            ),
            docx_paragraph(
                "Another body paragraph."
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
        "DOCX_HEADING_ORDER_PRESERVED",
        result.headings[0]
        == "Main Heading"
        and result.headings[-1]
        == "Section Heading",
    )

    check(
        "DOCX_HEADING_METHOD_STYLE_BASED",
        result.metadata.get(
            "heading_method"
        )
        == "style_based",
    )

    check(
        "DOCX_HEADING_COUNT_MATCHES",
        result.metadata.get(
            "heading_count"
        )
        == len(result.headings),
    )


# ------------------------------------------------------------
# F. DOCX heuristic fallback contract
# ------------------------------------------------------------

print()
print("=== F. DOCX HEURISTIC FALLBACK ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "heuristic.docx"

    write_docx(
        path,
        docx_xml(
            docx_paragraph(
                "Possible Heading"
            ),
            docx_paragraph(
                "This is a normal body paragraph ending with a period."
            ),
        ),
    )

    result = extractor.extract_docx_upload_v1(
        path
    )

    check(
        "DOCX_HEURISTIC_FALLBACK_USED_WHEN_NO_STYLES",
        result.metadata.get(
            "heading_method"
        )
        == "heuristic_fallback",
    )

    check(
        "DOCX_HEURISTIC_HEADING_EXTRACTED",
        "Possible Heading"
        in result.headings,
    )


# ------------------------------------------------------------
# G. DOCX style precedence over heuristic
# ------------------------------------------------------------

print()
print("=== G. DOCX STYLE PRECEDENCE ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "precedence.docx"

    write_docx(
        path,
        docx_xml(
            docx_paragraph(
                "Styled Heading",
                "Heading1",
            ),
            docx_paragraph(
                "Possible Heuristic Heading"
            ),
            docx_paragraph(
                "Normal paragraph ending with a period."
            ),
        ),
    )

    result = extractor.extract_docx_upload_v1(
        path
    )

    check(
        "DOCX_STYLE_BASED_PRECEDENCE",
        result.metadata.get(
            "heading_method"
        )
        == "style_based",
    )

    check(
        "DOCX_HEURISTIC_NOT_MIXED_WHEN_STYLES_EXIST",
        result.headings
        == ["Styled Heading"],
    )


# ------------------------------------------------------------
# H. DOCX heading cap
# ------------------------------------------------------------

print()
print("=== H. DOCX HEADING CAP ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "many_headings.docx"

    paragraphs = [
        docx_paragraph(
            f"Heading {index}",
            "Heading1",
        )
        for index in range(1, 31)
    ]

    write_docx(
        path,
        docx_xml(*paragraphs),
    )

    result = extractor.extract_docx_upload_v1(
        path
    )

    check(
        "DOCX_CURRENT_HEADING_CAP_IS_25",
        len(result.headings) == 25,
    )

    check(
        "DOCX_HEADING_CAP_PRESERVES_FIRST_25_IN_ORDER",
        result.headings[0]
        == "Heading 1"
        and result.headings[-1]
        == "Heading 25",
    )


# ------------------------------------------------------------
# I. Empty/no-heading output contract
# ------------------------------------------------------------

print()
print("=== I. EMPTY / NO-HEADING CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    md_path = root / "no_heading.md"
    md_path.write_text(
        "Body paragraph only.",
        encoding="utf-8",
    )

    html_path = root / "no_heading.html"
    html_path.write_text(
        "<html><body><p>Body only.</p></body></html>",
        encoding="utf-8",
    )

    txt_path = root / "empty.txt"
    txt_path.write_text(
        "",
        encoding="utf-8",
    )

    md_result = extractor.extract_markdown_upload_v1(
        md_path
    )

    html_result = extractor.extract_html_upload_v1(
        html_path
    )

    txt_result = extractor.extract_txt_upload_v1(
        txt_path
    )

    check(
        "MARKDOWN_NO_HEADING_RETURNS_EMPTY_LIST",
        md_result.headings == [],
    )

    check(
        "HTML_NO_HEADING_RETURNS_EMPTY_LIST",
        html_result.headings == [],
    )

    check(
        "EMPTY_TXT_RETURNS_EMPTY_HEADING_LIST",
        txt_result.headings == [],
    )

    check(
        "ALL_HEADING_OUTPUTS_ARE_LISTS",
        all(
            isinstance(item.headings, list)
            for item in (
                md_result,
                html_result,
                txt_result,
            )
        ),
    )


# ------------------------------------------------------------
# J. Serialization preservation
# ------------------------------------------------------------

print()
print("=== J. HEADING SERIALIZATION CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "serialized.md"

    path.write_text(
        "# Main\n\n## Section\n",
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
        "SERIALIZER_PRESERVES_HEADINGS",
        serialized.get(
            "headings"
        )
        == result.headings,
    )


# ------------------------------------------------------------
# K. Downstream isolation
# ------------------------------------------------------------

print()
print("=== K. HEADING DOWNSTREAM ISOLATION ===")

combined_source = "\n".join(
    [
        inspect.getsource(
            extractor.extract_txt_upload_v1
        ).lower(),
        inspect.getsource(
            extractor._extract_markdown_headings_v1
        ).lower(),
        inspect.getsource(
            extractor._extract_html_headings_v1
        ).lower(),
        inspect.getsource(
            extractor._extract_docx_headings_v2
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
        f"HEADING_LOGIC_DOES_NOT_DEPEND_ON_{forbidden.upper()}",
        forbidden not in combined_source,
    )


# ------------------------------------------------------------
# L. Source immutability
# ------------------------------------------------------------

print()
print("=== L. HEADING SOURCE IMMUTABILITY ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "immutable.md"

    path.write_text(
        "# Heading\n\nBody.",
        encoding="utf-8",
    )

    before = path.read_bytes()

    extractor.extract_markdown_upload_v1(
        path
    )

    after = path.read_bytes()

    check(
        "HEADING_EXTRACTION_DOES_NOT_MUTATE_SOURCE",
        before == after,
    )


# ------------------------------------------------------------
# M. Live upload-path consistency
# ------------------------------------------------------------

print()
print("=== M. LIVE UPLOAD HEADING CONSISTENCY ===")

intake_module = __import__(
    "backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake",
    fromlist=["run_upload_intake"],
)

intake_source = inspect.getsource(
    intake_module.run_upload_intake
).lower()

check(
    "INTAKE_DOES_NOT_REDERIVE_HEADINGS",
    "result.headings =" not in intake_source
    and "headings =" not in intake_source,
)

check(
    "MARKDOWN_HEADING_LOGIC_REMAINS_FORMAT_SPECIFIC",
    "_extract_markdown_headings_v1"
    in inspect.getsource(
        extractor.extract_markdown_upload_v1
    ),
)

check(
    "HTML_HEADING_LOGIC_REMAINS_FORMAT_SPECIFIC",
    "_extract_html_headings_v1"
    in inspect.getsource(
        extractor.extract_html_upload_v1
    ),
)

check(
    "DOCX_HEADING_LOGIC_REMAINS_FORMAT_SPECIFIC",
    "_extract_docx_headings_v2"
    in inspect.getsource(
        extractor.extract_docx_upload_v1
    ),
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
        "U6.9_HEADING_EXTRACTION_CONTRACT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U6.9 heading extraction contract verification failed."
    )

print(
    "U6.9_HEADING_EXTRACTION_CONTRACT: CERTIFIED"
)

print(
    "U6.9_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U6.10_TEXT_EXTRACTION_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U6.9_FINAL_HEADING_EXTRACTION_VERIFICATION: PASS"
)