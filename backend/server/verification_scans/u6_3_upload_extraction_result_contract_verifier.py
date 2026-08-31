from __future__ import annotations

import inspect
from dataclasses import fields, is_dataclass
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import backend.server.stores.upload_document_extractor as extractor
import backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake as upload_intake


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U6.3 - UPLOAD EXTRACTION RESULT CONTRACT ===")


ResultType = extractor.UploadExtractionResult


# ------------------------------------------------------------
# A. Canonical result type
# ------------------------------------------------------------

print()
print("=== A. CANONICAL RESULT TYPE ===")

check(
    "UPLOAD_EXTRACTION_RESULT_IS_DATACLASS",
    is_dataclass(ResultType),
)

expected_fields = [
    "source_path",
    "source_type",
    "title",
    "text",
    "headings",
    "metadata",
    "extraction_status",
    "extraction_confidence",
    "created_at",
]

actual_fields = [
    item.name
    for item in fields(ResultType)
]

check(
    "UPLOAD_EXTRACTION_RESULT_HAS_EXACT_FIELDS",
    actual_fields == expected_fields,
)


# ------------------------------------------------------------
# B. Empty/failure result contract
# ------------------------------------------------------------

print()
print("=== B. EMPTY / FAILURE RESULT CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "missing.txt"

    empty_result = extractor.build_empty_upload_result(
        path,
        status="missing_file",
        confidence=0.0,
    )

    check(
        "EMPTY_RESULT_IS_CANONICAL_TYPE",
        isinstance(empty_result, ResultType),
    )

    check(
        "SOURCE_PATH_IS_STRING",
        isinstance(empty_result.source_path, str),
    )

    check(
        "SOURCE_TYPE_IS_STRING",
        isinstance(empty_result.source_type, str),
    )

    check(
        "TITLE_IS_STRING",
        isinstance(empty_result.title, str),
    )

    check(
        "TEXT_IS_STRING",
        isinstance(empty_result.text, str),
    )

    check(
        "HEADINGS_IS_LIST",
        isinstance(empty_result.headings, list),
    )

    check(
        "HEADINGS_ELEMENTS_ARE_STRINGS",
        all(
            isinstance(item, str)
            for item in empty_result.headings
        ),
    )

    check(
        "METADATA_IS_DICT",
        isinstance(empty_result.metadata, dict),
    )

    check(
        "EXTRACTION_STATUS_IS_STRING",
        isinstance(
            empty_result.extraction_status,
            str,
        ),
    )

    check(
        "EXTRACTION_CONFIDENCE_IS_NUMERIC",
        isinstance(
            empty_result.extraction_confidence,
            (int, float),
        )
        and not isinstance(
            empty_result.extraction_confidence,
            bool,
        ),
    )

    check(
        "CREATED_AT_IS_STRING",
        isinstance(empty_result.created_at, str),
    )

    try:
        datetime.fromisoformat(
            empty_result.created_at
        )
        timestamp_ok = True
    except Exception:
        timestamp_ok = False

    check(
        "CREATED_AT_IS_ISO_TIMESTAMP",
        timestamp_ok,
    )


# ------------------------------------------------------------
# C. Logical source types
# ------------------------------------------------------------

print()
print("=== C. LOGICAL SOURCE TYPE CONTRACT ===")

logical_cases = {
    "file.txt": "txt",
    "file.md": "markdown",
    "file.markdown": "markdown",
    "file.html": "html",
    "file.htm": "html",
    "file.docx": "docx",
    "file.pdf": "unsupported",
}

for filename, expected in logical_cases.items():
    result = extractor.build_empty_upload_result(
        filename,
        status="test",
        confidence=0.0,
    )

    check(
        f"SOURCE_TYPE_{filename.replace('.', '_').upper()}",
        result.source_type == expected,
    )


# ------------------------------------------------------------
# D. Successful extractor result contracts
# ------------------------------------------------------------

print()
print("=== D. SUCCESSFUL EXTRACTOR RESULT CONTRACTS ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    txt_path = root / "sample.txt"
    txt_path.write_text(
        "Hello world.\n\nSecond paragraph.",
        encoding="utf-8",
    )

    md_path = root / "sample.md"
    md_path.write_text(
        "# Heading\n\nHello **world**.",
        encoding="utf-8",
    )

    html_path = root / "sample.html"
    html_path.write_text(
        "<html><head><title>Example</title></head>"
        "<body><h1>Heading</h1><p>Hello world.</p></body></html>",
        encoding="utf-8",
    )

    success_cases = [
        (
            "TXT",
            extractor.extract_txt_upload_v1(
                txt_path
            ),
            "txt",
        ),
        (
            "MARKDOWN",
            extractor.extract_markdown_upload_v1(
                md_path
            ),
            "markdown",
        ),
        (
            "HTML",
            extractor.extract_html_upload_v1(
                html_path
            ),
            "html",
        ),
    ]

    for label, result, expected_type in success_cases:
        check(
            f"{label}_SUCCESS_IS_CANONICAL_TYPE",
            isinstance(result, ResultType),
        )

        check(
            f"{label}_SUCCESS_SOURCE_TYPE",
            result.source_type
            == expected_type,
        )

        check(
            f"{label}_SUCCESS_TITLE_STRING",
            isinstance(result.title, str),
        )

        check(
            f"{label}_SUCCESS_TEXT_STRING",
            isinstance(result.text, str),
        )

        check(
            f"{label}_SUCCESS_HEADINGS_LIST_OF_STRINGS",
            isinstance(result.headings, list)
            and all(
                isinstance(item, str)
                for item in result.headings
            ),
        )

        check(
            f"{label}_SUCCESS_METADATA_DICT",
            isinstance(result.metadata, dict),
        )

        check(
            f"{label}_SUCCESS_STATUS_STRING",
            isinstance(
                result.extraction_status,
                str,
            )
            and result.extraction_status
            == "success",
        )

        check(
            f"{label}_SUCCESS_CONFIDENCE_NUMERIC",
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
            f"{label}_SUCCESS_CREATED_AT_ISO",
            created_ok,
        )


# ------------------------------------------------------------
# E. Structured failure results
# ------------------------------------------------------------

print()
print("=== E. STRUCTURED FAILURE RESULTS ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    wrong_path = root / "wrong.pdf"
    wrong_path.write_text(
        "plain text",
        encoding="utf-8",
    )

    failures_to_test = [
        (
            "TXT_UNSUPPORTED_EXTENSION",
            extractor.extract_txt_upload_v1(
                wrong_path
            ),
            "unsupported_extension",
        ),
        (
            "MARKDOWN_UNSUPPORTED_EXTENSION",
            extractor.extract_markdown_upload_v1(
                wrong_path
            ),
            "unsupported_extension",
        ),
        (
            "HTML_UNSUPPORTED_EXTENSION",
            extractor.extract_html_upload_v1(
                wrong_path
            ),
            "unsupported_extension",
        ),
        (
            "DOCX_UNSUPPORTED_EXTENSION",
            extractor.extract_docx_upload_v1(
                wrong_path
            ),
            "unsupported_extension",
        ),
        (
            "DISPATCHER_UNSUPPORTED_SOURCE",
            extractor.extract_upload_document_v1(
                wrong_path
            ),
            "unsupported_source_type",
        ),
    ]

    for label, result, expected_status in failures_to_test:
        check(
            f"{label}_IS_CANONICAL_TYPE",
            isinstance(result, ResultType),
        )

        check(
            f"{label}_STATUS",
            result.extraction_status
            == expected_status,
        )

        check(
            f"{label}_PRESERVES_ALL_CONTRACT_FIELDS",
            all(
                hasattr(result, field_name)
                for field_name in expected_fields
            ),
        )


# ------------------------------------------------------------
# F. Serialization contract
# ------------------------------------------------------------

print()
print("=== F. SERIALIZATION CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "document.txt"
    path.write_text(
        "Hello",
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
        "SERIALIZER_RETURNS_DICT",
        isinstance(serialized, dict),
    )

    check(
        "SERIALIZER_PRESERVES_EXACT_TOP_LEVEL_FIELDS",
        list(serialized.keys())
        == expected_fields,
    )

    check(
        "SERIALIZER_PRESERVES_SOURCE_PATH",
        serialized["source_path"]
        == result.source_path,
    )

    check(
        "SERIALIZER_PRESERVES_SOURCE_TYPE",
        serialized["source_type"]
        == result.source_type,
    )

    check(
        "SERIALIZER_PRESERVES_TITLE",
        serialized["title"]
        == result.title,
    )

    check(
        "SERIALIZER_PRESERVES_TEXT",
        serialized["text"]
        == result.text,
    )

    check(
        "SERIALIZER_PRESERVES_HEADINGS",
        serialized["headings"]
        == result.headings,
    )

    check(
        "SERIALIZER_PRESERVES_METADATA",
        serialized["metadata"]
        == result.metadata,
    )

    check(
        "SERIALIZER_PRESERVES_STATUS",
        serialized["extraction_status"]
        == result.extraction_status,
    )

    check(
        "SERIALIZER_PRESERVES_CONFIDENCE",
        serialized["extraction_confidence"]
        == result.extraction_confidence,
    )

    check(
        "SERIALIZER_PRESERVES_CREATED_AT",
        serialized["created_at"]
        == result.created_at,
    )


# ------------------------------------------------------------
# G. Intake consumes canonical result
# ------------------------------------------------------------

print()
print("=== G. INTAKE CONSUMPTION CONTRACT ===")

intake_source = inspect.getsource(
    upload_intake.run_upload_intake
).lower()

check(
    "INTAKE_CALLS_CANONICAL_DISPATCHER",
    "extract_upload_document_v1"
    in intake_source,
)

check(
    "INTAKE_READS_EXTRACTION_STATUS",
    "extraction_status"
    in intake_source,
)

check(
    "INTAKE_SERIALIZES_CANONICAL_RESULT",
    "serialize_upload_extraction_result"
    in intake_source,
)

check(
    "INTAKE_DOES_NOT_DEFINE_COMPETING_RESULT_SCHEMA",
    "class uploadextractionresult"
    not in intake_source
    and "@dataclass" not in intake_source,
)


# ------------------------------------------------------------
# H. No competing live extraction result type
# ------------------------------------------------------------

print()
print("=== H. RESULT TYPE SINGULARITY ===")

module_source = inspect.getsource(
    extractor
).lower()

check(
    "EXACTLY_ONE_UPLOAD_EXTRACTION_RESULT_CLASS",
    module_source.count(
        "class uploadextractionresult"
    )
    == 1,
)


# ------------------------------------------------------------
# I. Extraction evidence only
# ------------------------------------------------------------

print()
print("=== I. EXTRACTION EVIDENCE BOUNDARY ===")

result_source = inspect.getsource(
    ResultType
).lower()

for forbidden in (
    "uduc",
    "highlight",
    "active_target",
    "uucd",
    "runtime",
    "scorer",
):
    check(
        f"RESULT_DOES_NOT_EMBED_{forbidden.upper()}",
        forbidden not in result_source,
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
        "U6.3_UPLOAD_EXTRACTION_RESULT_CONTRACT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U6.3 UploadExtractionResult contract verification failed."
    )

print(
    "U6.3_UPLOAD_EXTRACTION_RESULT_CONTRACT: CERTIFIED"
)

print(
    "U6.3_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U6.4_TXT_EXTRACTOR_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U6.3_FINAL_RESULT_CONTRACT_VERIFICATION: PASS"
)