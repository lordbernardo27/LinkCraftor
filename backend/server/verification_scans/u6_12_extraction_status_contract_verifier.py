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


print("=== U6.12 - EXTRACTION STATUS CONTRACT ===")


# ------------------------------------------------------------
# A. Successful extraction status
# ------------------------------------------------------------

print()
print("=== A. SUCCESS STATUS ===")

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
            docx_paragraph("Visible text.")
        ),
    )

    success_results = [
        extractor.extract_txt_upload_v1(txt),
        extractor.extract_markdown_upload_v1(md),
        extractor.extract_html_upload_v1(html),
        extractor.extract_docx_upload_v1(docx),
    ]

    check(
        "NONEMPTY_EXTRACTIONS_RETURN_SUCCESS",
        all(
            result.extraction_status == "success"
            for result in success_results
        ),
    )

    check(
        "SUCCESS_STATUS_ALWAYS_STRING",
        all(
            isinstance(
                result.extraction_status,
                str,
            )
            for result in success_results
        ),
    )


# ------------------------------------------------------------
# B. Empty-text status
# ------------------------------------------------------------

print()
print("=== B. EMPTY_TEXT STATUS ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    txt = root / "empty.txt"
    txt.write_text(
        "  \n\t  ",
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
        "EMPTY_CONTENT_RETURNS_EMPTY_TEXT",
        all(
            result.extraction_status
            == "empty_text"
            for result in empty_results
        ),
    )

    check(
        "EMPTY_TEXT_HAS_ZERO_CONFIDENCE",
        all(
            result.extraction_confidence
            == 0.0
            for result in empty_results
        ),
    )


# ------------------------------------------------------------
# C. Missing-file status
# ------------------------------------------------------------

print()
print("=== C. MISSING_FILE STATUS ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    missing_results = [
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

    check(
        "MISSING_FILES_RETURN_MISSING_FILE",
        all(
            result.extraction_status
            == "missing_file"
            for result in missing_results
        ),
    )

    check(
        "MISSING_FILE_HAS_ZERO_CONFIDENCE",
        all(
            result.extraction_confidence
            == 0.0
            for result in missing_results
        ),
    )

    check(
        "MISSING_FILE_STATUS_ALWAYS_STRING",
        all(
            isinstance(
                result.extraction_status,
                str,
            )
            for result in missing_results
        ),
    )


# ------------------------------------------------------------
# D. Direct extractor extension mismatch
# ------------------------------------------------------------

print()
print("=== D. UNSUPPORTED_EXTENSION STATUS ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    wrong_txt = root / "wrong.md"
    wrong_txt.write_text(
        "Body.",
        encoding="utf-8",
    )

    wrong_md = root / "wrong.txt"
    wrong_md.write_text(
        "Body.",
        encoding="utf-8",
    )

    wrong_html = root / "wrong.txt"
    wrong_html.write_text(
        "Body.",
        encoding="utf-8",
    )

    wrong_docx = root / "wrong.txt"
    wrong_docx.write_text(
        "Body.",
        encoding="utf-8",
    )

    mismatch_results = [
        extractor.extract_txt_upload_v1(
            wrong_txt
        ),
        extractor.extract_markdown_upload_v1(
            wrong_md
        ),
        extractor.extract_html_upload_v1(
            wrong_html
        ),
        extractor.extract_docx_upload_v1(
            wrong_docx
        ),
    ]

    check(
        "DIRECT_EXTRACTOR_MISMATCH_RETURNS_UNSUPPORTED_EXTENSION",
        all(
            result.extraction_status
            == "unsupported_extension"
            for result in mismatch_results
        ),
    )

    check(
        "UNSUPPORTED_EXTENSION_HAS_ZERO_CONFIDENCE",
        all(
            result.extraction_confidence
            == 0.0
            for result in mismatch_results
        ),
    )


# ------------------------------------------------------------
# E. Dispatcher unsupported source type
# ------------------------------------------------------------

print()
print("=== E. UNSUPPORTED_SOURCE_TYPE STATUS ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "unsupported.pdf"

    path.write_bytes(
        b"%PDF-test"
    )

    result = extractor.extract_upload_document_v1(
        path
    )

    check(
        "DISPATCHER_UNSUPPORTED_RETURNS_UNSUPPORTED_SOURCE_TYPE",
        result.extraction_status
        == "unsupported_source_type",
    )

    check(
        "UNSUPPORTED_SOURCE_TYPE_HAS_ZERO_CONFIDENCE",
        result.extraction_confidence
        == 0.0,
    )

    check(
        "UNSUPPORTED_SOURCE_TYPE_IS_STRUCTURED_RESULT",
        isinstance(
            result,
            extractor.UploadExtractionResult,
        ),
    )


# ------------------------------------------------------------
# F. Invalid DOCX structural status
# ------------------------------------------------------------

print()
print("=== F. INVALID_DOCX STATUS ===")

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
        "INVALID_DOCX_HAS_ZERO_CONFIDENCE",
        result.extraction_confidence
        == 0.0,
    )


# ------------------------------------------------------------
# G. General extraction-error status
# ------------------------------------------------------------

print()
print("=== G. EXTRACTION_ERROR STATUS ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "broken.docx"

    path.write_bytes(
        b"not-a-valid-zip-file"
    )

    result = extractor.extract_docx_upload_v1(
        path
    )

    check(
        "BROKEN_DOCX_RETURNS_EXTRACTION_ERROR",
        result.extraction_status
        == "extraction_error",
    )

    check(
        "EXTRACTION_ERROR_HAS_ZERO_CONFIDENCE",
        result.extraction_confidence
        == 0.0,
    )


# ------------------------------------------------------------
# H. Status type on representative outcomes
# ------------------------------------------------------------

print()
print("=== H. STATUS TYPE CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    good = root / "good.txt"
    good.write_text(
        "Body.",
        encoding="utf-8",
    )

    empty = root / "empty.txt"
    empty.write_text(
        "   ",
        encoding="utf-8",
    )

    wrong = root / "wrong.md"
    wrong.write_text(
        "Body.",
        encoding="utf-8",
    )

    unsupported = root / "unsupported.pdf"
    unsupported.write_bytes(
        b"test"
    )

    representative_results = [
        extractor.extract_txt_upload_v1(good),
        extractor.extract_txt_upload_v1(empty),
        extractor.extract_txt_upload_v1(
            root / "missing.txt"
        ),
        extractor.extract_txt_upload_v1(wrong),
        extractor.extract_upload_document_v1(
            unsupported
        ),
    ]

    check(
        "ALL_REPRESENTATIVE_STATUSES_ARE_STRINGS",
        all(
            isinstance(
                result.extraction_status,
                str,
            )
            for result in representative_results
        ),
    )


# ------------------------------------------------------------
# I. Serialization preserves status
# ------------------------------------------------------------

print()
print("=== I. STATUS SERIALIZATION CONTRACT ===")

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
        "SERIALIZER_PRESERVES_EXTRACTION_STATUS",
        serialized.get(
            "extraction_status"
        )
        == result.extraction_status
        == "success",
    )


# ------------------------------------------------------------
# J. Intake status ownership
# ------------------------------------------------------------

print()
print("=== J. LIVE INTAKE STATUS CONSISTENCY ===")

intake_module = __import__(
    "backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake",
    fromlist=["run_upload_intake"],
)

intake_source = inspect.getsource(
    intake_module.run_upload_intake
).lower()

check(
    "INTAKE_READS_CANONICAL_EXTRACTION_STATUS",
    "extraction_status"
    in intake_source,
)

check(
    "INTAKE_DOES_NOT_REWRITE_RESULT_STATUS",
    "result.extraction_status ="
    not in intake_source,
)

check(
    "INTAKE_LOCAL_STATUS_COMES_FROM_EXTRACTION_RESULT",
    "extraction_status = str("
    in intake_source
    and "extraction_result"
    in intake_source
    and "extraction_status"
    in intake_source,
)


# ------------------------------------------------------------
# K. Status vocabulary isolation
# ------------------------------------------------------------

print()
print("=== K. STATUS VOCABULARY ISOLATION ===")

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
    ]
)

check(
    "EXTRACTOR_STATUS_DOES_NOT_USE_HTTP_CODES",
    "status_code" not in extractor_sources
    and "httpstatus" not in extractor_sources,
)

for forbidden in (
    "active_target",
    "uucd_status",
    "semantic_status",
    "runtime_status",
    "scorer_status",
):
    check(
        f"EXTRACTION_STATUS_DOES_NOT_USE_{forbidden.upper()}",
        forbidden not in extractor_sources,
    )


# ------------------------------------------------------------
# L. Canonical status vocabulary
# ------------------------------------------------------------

print()
print("=== L. CANONICAL STATUS VOCABULARY ===")

expected_statuses = {
    "success",
    "empty_text",
    "missing_file",
    "unsupported_extension",
    "unsupported_source_type",
    "invalid_docx",
    "extraction_error",
}

observed_status_literals = {
    status
    for status in expected_statuses
    if status in extractor_sources
}

check(
    "EXPECTED_STATUS_VOCABULARY_PRESENT",
    observed_status_literals
    == expected_statuses,
)

check(
    "NO_CONFLICTING_SUCCESS_STATUS",
    '"ok"' not in extractor_sources
    and "'ok'" not in extractor_sources
    and '"complete"' not in extractor_sources
    and "'complete'" not in extractor_sources
    and '"completed"' not in extractor_sources
    and "'completed'" not in extractor_sources,
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
        "U6.12_EXTRACTION_STATUS_CONTRACT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U6.12 extraction status contract verification failed."
    )

print(
    "U6.12_EXTRACTION_STATUS_CONTRACT: CERTIFIED"
)

print(
    "U6.12_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U6.13_EXTRACTION_CONFIDENCE_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U6.12_FINAL_EXTRACTION_STATUS_VERIFICATION: PASS"
)