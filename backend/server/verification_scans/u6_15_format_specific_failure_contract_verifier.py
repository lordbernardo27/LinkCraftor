from __future__ import annotations

import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZIP_DEFLATED
from unittest.mock import patch

import backend.server.stores.upload_document_extractor as extractor


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def safe_failure_shape(result) -> bool:
    return (
        isinstance(
            result,
            extractor.UploadExtractionResult,
        )
        and isinstance(result.source_path, str)
        and isinstance(result.source_type, str)
        and isinstance(result.title, str)
        and isinstance(result.text, str)
        and result.text == ""
        and isinstance(result.headings, list)
        and result.headings == []
        and isinstance(result.metadata, dict)
        and isinstance(result.created_at, str)
        and bool(result.created_at)
        and result.extraction_confidence == 0.0
    )


print("=== U6.15 - FORMAT-SPECIFIC FAILURE CONTRACT ===")


# ------------------------------------------------------------
# A. TXT failure behavior
# ------------------------------------------------------------

print()
print("=== A. TXT FAILURE CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "broken.txt"
    path.write_text(
        "Body.",
        encoding="utf-8",
    )

    before = path.read_bytes()

    with patch.object(
        Path,
        "read_text",
        side_effect=OSError(
            "simulated TXT read failure"
        ),
    ):
        result = extractor.extract_txt_upload_v1(
            path
        )

    after = path.read_bytes()

    check(
        "TXT_FAILURE_RETURNS_CANONICAL_RESULT",
        safe_failure_shape(result),
    )

    check(
        "TXT_FAILURE_STATUS_EXTRACTION_ERROR",
        result.extraction_status
        == "extraction_error",
    )

    check(
        "TXT_FAILURE_HAS_STRUCTURED_ERROR_METADATA",
        isinstance(
            result.metadata.get("error"),
            str,
        )
        and bool(
            result.metadata.get("error")
        ),
    )

    check(
        "TXT_FAILURE_SOURCE_IMMUTABLE",
        before == after,
    )


# ------------------------------------------------------------
# B. Markdown failure behavior
# ------------------------------------------------------------

print()
print("=== B. MARKDOWN FAILURE CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "broken.md"
    path.write_text(
        "# Heading\n\nBody.",
        encoding="utf-8",
    )

    before = path.read_bytes()

    with patch.object(
        Path,
        "read_text",
        side_effect=OSError(
            "simulated Markdown read failure"
        ),
    ):
        result = (
            extractor.extract_markdown_upload_v1(
                path
            )
        )

    after = path.read_bytes()

    check(
        "MARKDOWN_FAILURE_RETURNS_CANONICAL_RESULT",
        safe_failure_shape(result),
    )

    check(
        "MARKDOWN_FAILURE_STATUS_EXTRACTION_ERROR",
        result.extraction_status
        == "extraction_error",
    )

    check(
        "MARKDOWN_FAILURE_HAS_STRUCTURED_ERROR_METADATA",
        isinstance(
            result.metadata.get("error"),
            str,
        )
        and bool(
            result.metadata.get("error")
        ),
    )

    check(
        "MARKDOWN_FAILURE_SOURCE_IMMUTABLE",
        before == after,
    )


# ------------------------------------------------------------
# C. HTML failure behavior
# ------------------------------------------------------------

print()
print("=== C. HTML FAILURE CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "broken.html"
    path.write_text(
        "<h1>Heading</h1><p>Body.</p>",
        encoding="utf-8",
    )

    before = path.read_bytes()

    with patch.object(
        Path,
        "read_text",
        side_effect=OSError(
            "simulated HTML read failure"
        ),
    ):
        result = extractor.extract_html_upload_v1(
            path
        )

    after = path.read_bytes()

    check(
        "HTML_FAILURE_RETURNS_CANONICAL_RESULT",
        safe_failure_shape(result),
    )

    check(
        "HTML_FAILURE_STATUS_EXTRACTION_ERROR",
        result.extraction_status
        == "extraction_error",
    )

    check(
        "HTML_FAILURE_HAS_STRUCTURED_ERROR_METADATA",
        isinstance(
            result.metadata.get("error"),
            str,
        )
        and bool(
            result.metadata.get("error")
        ),
    )

    check(
        "HTML_FAILURE_SOURCE_IMMUTABLE",
        before == after,
    )


# ------------------------------------------------------------
# D. DOCX package / structural failures
# ------------------------------------------------------------

print()
print("=== D. DOCX PACKAGE FAILURE CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    broken = root / "broken.docx"
    broken.write_bytes(
        b"not-a-valid-zip"
    )

    broken_before = broken.read_bytes()

    broken_result = (
        extractor.extract_docx_upload_v1(
            broken
        )
    )

    broken_after = broken.read_bytes()

    check(
        "DOCX_INVALID_CONTAINER_RETURNS_CANONICAL_RESULT",
        safe_failure_shape(
            broken_result
        ),
    )

    check(
        "DOCX_INVALID_CONTAINER_STATUS_EXTRACTION_ERROR",
        broken_result.extraction_status
        == "extraction_error",
    )

    check(
        "DOCX_INVALID_CONTAINER_SOURCE_IMMUTABLE",
        broken_before == broken_after,
    )

    missing_xml = root / "missing_document_xml.docx"

    with ZipFile(
        missing_xml,
        "w",
        compression=ZIP_DEFLATED,
    ) as archive:
        archive.writestr(
            "word/other.xml",
            "<root/>",
        )

    missing_xml_before = (
        missing_xml.read_bytes()
    )

    missing_xml_result = (
        extractor.extract_docx_upload_v1(
            missing_xml
        )
    )

    missing_xml_after = (
        missing_xml.read_bytes()
    )

    check(
        "DOCX_MISSING_DOCUMENT_XML_RETURNS_CANONICAL_RESULT",
        safe_failure_shape(
            missing_xml_result
        ),
    )

    check(
        "DOCX_MISSING_DOCUMENT_XML_STATUS_INVALID_DOCX",
        missing_xml_result.extraction_status
        == "invalid_docx",
    )

    check(
        "DOCX_MISSING_DOCUMENT_XML_SOURCE_IMMUTABLE",
        missing_xml_before
        == missing_xml_after,
    )


# ------------------------------------------------------------
# E. DOCX malformed XML determinism
# ------------------------------------------------------------

print()
print("=== E. DOCX MALFORMED XML CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "malformed.docx"

    with ZipFile(
        path,
        "w",
        compression=ZIP_DEFLATED,
    ) as archive:
        archive.writestr(
            "word/document.xml",
            "<w:document><w:body><w:p>",
        )

    before = path.read_bytes()

    first = extractor.extract_docx_upload_v1(
        path
    )

    second = extractor.extract_docx_upload_v1(
        path
    )

    after = path.read_bytes()

    check(
        "DOCX_MALFORMED_XML_RETURNS_STRUCTURED_RESULT",
        isinstance(
            first,
            extractor.UploadExtractionResult,
        ),
    )

    check(
        "DOCX_MALFORMED_XML_STATUS_DETERMINISTIC",
        first.extraction_status
        == second.extraction_status,
    )

    check(
        "DOCX_MALFORMED_XML_CONFIDENCE_DETERMINISTIC",
        first.extraction_confidence
        == second.extraction_confidence,
    )

    check(
        "DOCX_MALFORMED_XML_SOURCE_IMMUTABLE",
        before == after,
    )


# ------------------------------------------------------------
# F. Error payload safety
# ------------------------------------------------------------

print()
print("=== F. FAILURE ERROR PAYLOAD SAFETY ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "broken.txt"
    path.write_text(
        "Body.",
        encoding="utf-8",
    )

    with patch.object(
        Path,
        "read_text",
        side_effect=OSError(
            "simulated safe failure"
        ),
    ):
        result = extractor.extract_txt_upload_v1(
            path
        )

    error_text = str(
        result.metadata.get("error") or ""
    )

    check(
        "FAILURE_ERROR_METADATA_IS_STRING",
        isinstance(
            result.metadata.get("error"),
            str,
        ),
    )

    check(
        "FAILURE_ERROR_METADATA_HAS_NO_TRACEBACK",
        "traceback" not in error_text.lower(),
    )

    check(
        "FAILURE_ERROR_METADATA_HAS_NO_PYTHON_STACK_MARKER",
        'file "' not in error_text.lower(),
    )


# ------------------------------------------------------------
# G. Canonical failure serialization
# ------------------------------------------------------------

print()
print("=== G. FAILURE SERIALIZATION CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "broken.html"
    path.write_text(
        "<p>Body.</p>",
        encoding="utf-8",
    )

    with patch.object(
        Path,
        "read_text",
        side_effect=OSError(
            "simulated serialization failure"
        ),
    ):
        result = extractor.extract_html_upload_v1(
            path
        )

    serialized = (
        extractor.serialize_upload_extraction_result(
            result
        )
    )

    check(
        "FAILURE_SERIALIZER_PRESERVES_SOURCE_PATH",
        serialized.get("source_path")
        == result.source_path,
    )

    check(
        "FAILURE_SERIALIZER_PRESERVES_SOURCE_TYPE",
        serialized.get("source_type")
        == result.source_type,
    )

    check(
        "FAILURE_SERIALIZER_PRESERVES_TITLE",
        serialized.get("title")
        == result.title,
    )

    check(
        "FAILURE_SERIALIZER_PRESERVES_METADATA",
        serialized.get("metadata")
        == result.metadata,
    )

    check(
        "FAILURE_SERIALIZER_PRESERVES_CREATED_AT",
        serialized.get("created_at")
        == result.created_at,
    )

    check(
        "FAILURE_SERIALIZER_PRESERVES_STATUS",
        serialized.get(
            "extraction_status"
        )
        == result.extraction_status,
    )

    check(
        "FAILURE_SERIALIZER_PRESERVES_CONFIDENCE",
        serialized.get(
            "extraction_confidence"
        )
        == 0.0,
    )


# ------------------------------------------------------------
# H. Format isolation
# ------------------------------------------------------------

print()
print("=== H. FORMAT-SPECIFIC FAILURE ISOLATION ===")

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
    "TXT_FAILURE_DOES_NOT_CALL_MARKDOWN_EXTRACTOR",
    "extract_markdown_upload_v1"
    not in txt_source,
)

check(
    "TXT_FAILURE_DOES_NOT_CALL_HTML_EXTRACTOR",
    "extract_html_upload_v1"
    not in txt_source,
)

check(
    "TXT_FAILURE_DOES_NOT_CALL_DOCX_EXTRACTOR",
    "extract_docx_upload_v1"
    not in txt_source,
)

check(
    "MARKDOWN_FAILURE_DOES_NOT_CALL_TXT_EXTRACTOR",
    "extract_txt_upload_v1"
    not in md_source,
)

check(
    "HTML_FAILURE_DOES_NOT_CALL_TXT_EXTRACTOR",
    "extract_txt_upload_v1"
    not in html_source,
)

check(
    "DOCX_FAILURE_DOES_NOT_CALL_OTHER_FORMAT_EXTRACTORS",
    all(
        name not in docx_source
        for name in (
            "extract_txt_upload_v1",
            "extract_markdown_upload_v1",
            "extract_html_upload_v1",
        )
    ),
)


# ------------------------------------------------------------
# I. Website / downstream isolation
# ------------------------------------------------------------

print()
print("=== I. FAILURE DOWNSTREAM ISOLATION ===")

combined_source = "\n".join(
    [
        txt_source,
        md_source,
        html_source,
        docx_source,
        inspect.getsource(
            extractor.extract_upload_document_v1
        ).lower(),
    ]
)

for forbidden in (
    "article_body_cleaning_engine",
    "article_cleaning_pipeline",
    "uduc",
    "highlight",
    "active_target",
    "uucd",
    "semantic",
    "runtime",
    "scorer",
):
    check(
        f"FAILURE_HANDLING_DOES_NOT_DEPEND_ON_{forbidden.upper()}",
        forbidden not in combined_source,
    )


# ------------------------------------------------------------
# J. Intake handling of non-success
# ------------------------------------------------------------

print()
print("=== J. LIVE INTAKE NON-SUCCESS HANDLING ===")

intake_module = __import__(
    "backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake",
    fromlist=["run_upload_intake"],
)

intake_source = inspect.getsource(
    intake_module.run_upload_intake
).lower()

check(
    "INTAKE_READS_EXTRACTION_STATUS",
    "extraction_status"
    in intake_source,
)

check(
    "INTAKE_REJECTS_ANY_NON_SUCCESS_STATUS",
    'if extraction_status != "success":'
    in intake_source,
)

check(
    "INTAKE_DOES_NOT_SPECIAL_CASE_FAILURE_STATUS_VOCABULARY",
    all(
        literal not in intake_source
        for literal in (
            '"empty_text"',
            '"missing_file"',
            '"unsupported_extension"',
            '"unsupported_source_type"',
            '"invalid_docx"',
            '"extraction_error"',
        )
    ),
)


# ------------------------------------------------------------
# K. Failure status consistency
# ------------------------------------------------------------

print()
print("=== K. FORMAT FAILURE STATUS CONSISTENCY ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    txt = root / "x.txt"
    md = root / "x.md"
    html = root / "x.html"

    txt.write_text("Body.", encoding="utf-8")
    md.write_text("Body.", encoding="utf-8")
    html.write_text("Body.", encoding="utf-8")

    with patch.object(
        Path,
        "read_text",
        side_effect=OSError(
            "simulated format read failure"
        ),
    ):
        text_results = [
            extractor.extract_txt_upload_v1(
                txt
            ),
            extractor.extract_markdown_upload_v1(
                md
            ),
            extractor.extract_html_upload_v1(
                html
            ),
        ]

    check(
        "TEXT_FORMAT_PROCESSING_FAILURES_SHARE_EXTRACTION_ERROR",
        {
            result.extraction_status
            for result in text_results
        }
        == {"extraction_error"},
    )

    check(
        "TEXT_FORMAT_PROCESSING_FAILURES_SHARE_ZERO_CONFIDENCE",
        {
            result.extraction_confidence
            for result in text_results
        }
        == {0.0},
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
        "U6.15_FORMAT_SPECIFIC_FAILURE_CONTRACT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U6.15 format-specific failure contract verification failed."
    )

print(
    "U6.15_FORMAT_SPECIFIC_FAILURE_CONTRACT: CERTIFIED"
)

print(
    "U6.15_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U6.16_SOURCE_IMMUTABILITY_CONFIRMATION_TRANSITION: AUTHORIZED"
)

print(
    "U6.15_FINAL_FORMAT_SPECIFIC_FAILURE_VERIFICATION: PASS"
)