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


print("=== U6.13 - EXTRACTION CONFIDENCE CONTRACT ===")


# ------------------------------------------------------------
# A. Success confidence type / bounds
# ------------------------------------------------------------

print()
print("=== A. SUCCESS CONFIDENCE TYPE / BOUNDS ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    txt = root / "success.txt"
    txt.write_text(
        "Visible text.",
        encoding="utf-8",
    )

    md = root / "success.md"
    md.write_text(
        "# Heading\n\nVisible text.",
        encoding="utf-8",
    )

    html = root / "success.html"
    html.write_text(
        "<h1>Heading</h1><p>Visible text.</p>",
        encoding="utf-8",
    )

    docx = root / "success.docx"
    write_docx(
        docx,
        docx_xml(
            docx_paragraph(
                "Heading",
                "Heading1",
            ),
            docx_paragraph(
                "Visible text."
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
        "SUCCESS_CONFIDENCE_ALWAYS_NUMERIC",
        all(
            isinstance(
                result.extraction_confidence,
                (int, float),
            )
            and not isinstance(
                result.extraction_confidence,
                bool,
            )
            for result in success_results
        ),
    )

    check(
        "SUCCESS_CONFIDENCE_BOUNDED_ZERO_TO_ONE",
        all(
            0.0
            <= float(result.extraction_confidence)
            <= 1.0
            for result in success_results
        ),
    )


# ------------------------------------------------------------
# B. Deterministic format confidence
# ------------------------------------------------------------

print()
print("=== B. FORMAT CONFIDENCE VALUES ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    txt = root / "article.txt"
    txt.write_text(
        "Body.",
        encoding="utf-8",
    )

    md = root / "article.md"
    md.write_text(
        "# Heading\n\nBody.",
        encoding="utf-8",
    )

    html = root / "article.html"
    html.write_text(
        "<h1>Heading</h1><p>Body.</p>",
        encoding="utf-8",
    )

    txt_result = extractor.extract_txt_upload_v1(txt)
    md_result = extractor.extract_markdown_upload_v1(md)
    html_result = extractor.extract_html_upload_v1(html)

    check(
        "TXT_SUCCESS_CONFIDENCE_IS_DETERMINISTIC",
        txt_result.extraction_confidence == 0.95,
    )

    check(
        "MARKDOWN_SUCCESS_CONFIDENCE_IS_DETERMINISTIC",
        md_result.extraction_confidence == 0.93,
    )

    check(
        "HTML_SUCCESS_CONFIDENCE_IS_DETERMINISTIC",
        html_result.extraction_confidence == 0.90,
    )


# ------------------------------------------------------------
# C. DOCX confidence differentiation
# ------------------------------------------------------------

print()
print("=== C. DOCX CONFIDENCE DIFFERENTIATION ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    styled = root / "styled.docx"
    heuristic = root / "heuristic.docx"

    write_docx(
        styled,
        docx_xml(
            docx_paragraph(
                "Styled Heading",
                "Heading1",
            ),
            docx_paragraph(
                "Body paragraph."
            ),
        ),
    )

    write_docx(
        heuristic,
        docx_xml(
            docx_paragraph(
                "Possible Heading"
            ),
            docx_paragraph(
                "This is a normal body paragraph ending with a period."
            ),
        ),
    )

    styled_result = extractor.extract_docx_upload_v1(
        styled
    )

    heuristic_result = extractor.extract_docx_upload_v1(
        heuristic
    )

    check(
        "DOCX_STYLE_BASED_CONFIDENCE_IS_DETERMINISTIC",
        styled_result.extraction_confidence
        == 0.92,
    )

    check(
        "DOCX_HEURISTIC_CONFIDENCE_IS_DETERMINISTIC",
        heuristic_result.extraction_confidence
        == 0.88,
    )

    check(
        "DOCX_STYLE_BASED_CONFIDENCE_HIGHER_THAN_HEURISTIC",
        styled_result.extraction_confidence
        > heuristic_result.extraction_confidence,
    )


# ------------------------------------------------------------
# D. Failure / non-success confidence
# ------------------------------------------------------------

print()
print("=== D. FAILURE CONFIDENCE CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    empty_txt = root / "empty.txt"
    empty_txt.write_text(
        "   ",
        encoding="utf-8",
    )

    wrong_txt = root / "wrong.md"
    wrong_txt.write_text(
        "Body.",
        encoding="utf-8",
    )

    unsupported = root / "unsupported.pdf"
    unsupported.write_bytes(
        b"%PDF-test"
    )

    invalid_docx = root / "invalid.docx"
    with ZipFile(
        invalid_docx,
        "w",
        compression=ZIP_DEFLATED,
    ) as archive:
        archive.writestr(
            "word/other.xml",
            "<root/>",
        )

    broken_docx = root / "broken.docx"
    broken_docx.write_bytes(
        b"not-a-valid-zip"
    )

    failure_results = [
        extractor.extract_txt_upload_v1(
            empty_txt
        ),
        extractor.extract_txt_upload_v1(
            root / "missing.txt"
        ),
        extractor.extract_txt_upload_v1(
            wrong_txt
        ),
        extractor.extract_upload_document_v1(
            unsupported
        ),
        extractor.extract_docx_upload_v1(
            invalid_docx
        ),
        extractor.extract_docx_upload_v1(
            broken_docx
        ),
    ]

    expected_statuses = [
        "empty_text",
        "missing_file",
        "unsupported_extension",
        "unsupported_source_type",
        "invalid_docx",
        "extraction_error",
    ]

    check(
        "FAILURE_STATUS_SET_IS_COMPLETE",
        [
            result.extraction_status
            for result in failure_results
        ]
        == expected_statuses,
    )

    check(
        "ALL_FAILURE_CONFIDENCES_ARE_ZERO",
        all(
            result.extraction_confidence == 0.0
            for result in failure_results
        ),
    )

    check(
        "ALL_FAILURE_CONFIDENCES_ARE_NUMERIC",
        all(
            isinstance(
                result.extraction_confidence,
                (int, float),
            )
            and not isinstance(
                result.extraction_confidence,
                bool,
            )
            for result in failure_results
        ),
    )


# ------------------------------------------------------------
# E. Serialization preservation
# ------------------------------------------------------------

print()
print("=== E. CONFIDENCE SERIALIZATION CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "serialized.txt"

    path.write_text(
        "Body.",
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
        "SERIALIZER_PRESERVES_EXTRACTION_CONFIDENCE",
        serialized.get(
            "extraction_confidence"
        )
        == result.extraction_confidence,
    )


# ------------------------------------------------------------
# F. Intake confidence ownership
# ------------------------------------------------------------

print()
print("=== F. LIVE INTAKE CONFIDENCE CONSISTENCY ===")

intake_module = __import__(
    "backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake",
    fromlist=["run_upload_intake"],
)

intake_source = inspect.getsource(
    intake_module.run_upload_intake
).lower()

check(
    "INTAKE_DOES_NOT_RECALCULATE_CONFIDENCE",
    "extraction_confidence ="
    not in intake_source,
)

check(
    "INTAKE_DOES_NOT_OVERWRITE_RESULT_CONFIDENCE",
    "extraction_result.extraction_confidence ="
    not in intake_source,
)


# ------------------------------------------------------------
# G. Confidence responsibility / isolation
# ------------------------------------------------------------

print()
print("=== G. CONFIDENCE RESPONSIBILITY BOUNDARY ===")

extractor_sources = "\n".join(
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
            extractor.extract_upload_document_v1
        ).lower(),
        inspect.getsource(
            extractor.build_empty_upload_result
        ).lower(),
    ]
)

for forbidden in (
    "semantic_score",
    "relevance_score",
    "ranking_score",
    "uduc_score",
    "highlight_score",
    "active_target_score",
    "uucd_score",
    "runtime_score",
    "scorer_output",
):
    check(
        f"EXTRACTION_CONFIDENCE_IS_NOT_{forbidden.upper()}",
        forbidden not in extractor_sources,
    )


# ------------------------------------------------------------
# H. No conflicting confidence vocabulary
# ------------------------------------------------------------

print()
print("=== H. CONFIDENCE VOCABULARY CONSISTENCY ===")

check(
    "CANONICAL_CONFIDENCE_FIELD_PRESENT",
    "extraction_confidence"
    in extractor_sources,
)

for conflicting in (
    "extractor_confidence",
    "confidence_score",
    "extraction_score",
    "parse_confidence",
):
    check(
        f"NO_CONFLICTING_FIELD_{conflicting.upper()}",
        conflicting not in extractor_sources,
    )


# ------------------------------------------------------------
# I. Representative global bounds
# ------------------------------------------------------------

print()
print("=== I. REPRESENTATIVE GLOBAL BOUNDS ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    good = root / "good.md"
    good.write_text(
        "# Heading\n\nBody.",
        encoding="utf-8",
    )

    empty = root / "empty.md"
    empty.write_text(
        "   ",
        encoding="utf-8",
    )

    representative_results = [
        extractor.extract_markdown_upload_v1(
            good
        ),
        extractor.extract_markdown_upload_v1(
            empty
        ),
        extractor.extract_markdown_upload_v1(
            root / "missing.md"
        ),
    ]

    check(
        "ALL_REPRESENTATIVE_CONFIDENCES_WITHIN_BOUNDS",
        all(
            0.0
            <= float(result.extraction_confidence)
            <= 1.0
            for result in representative_results
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
        "U6.13_EXTRACTION_CONFIDENCE_CONTRACT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U6.13 extraction confidence contract verification failed."
    )

print(
    "U6.13_EXTRACTION_CONFIDENCE_CONTRACT: CERTIFIED"
)

print(
    "U6.13_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U6.14_MISSING_FILE_INVALID_INPUT_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U6.13_FINAL_EXTRACTION_CONFIDENCE_VERIFICATION: PASS"
)