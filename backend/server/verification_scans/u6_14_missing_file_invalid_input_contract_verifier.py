from __future__ import annotations

import inspect
from pathlib import Path
from tempfile import TemporaryDirectory

import backend.server.stores.upload_document_extractor as extractor


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U6.14 - MISSING FILE / INVALID INPUT CONTRACT ===")


# ------------------------------------------------------------
# A. Missing-file contract across all format extractors
# ------------------------------------------------------------

print()
print("=== A. MISSING-FILE CONTRACT ===")

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
        "MISSING_RESULTS_USE_CANONICAL_RESULT_TYPE",
        all(
            isinstance(
                result,
                extractor.UploadExtractionResult,
            )
            for result in missing_results
        ),
    )

    check(
        "MISSING_RESULTS_STATUS_MISSING_FILE",
        all(
            result.extraction_status
            == "missing_file"
            for result in missing_results
        ),
    )

    check(
        "MISSING_RESULTS_CONFIDENCE_ZERO",
        all(
            result.extraction_confidence
            == 0.0
            for result in missing_results
        ),
    )

    check(
        "MISSING_RESULTS_TEXT_EMPTY",
        all(
            result.text == ""
            for result in missing_results
        ),
    )

    check(
        "MISSING_RESULTS_HEADINGS_EMPTY",
        all(
            result.headings == []
            for result in missing_results
        ),
    )

    check(
        "MISSING_RESULTS_SAFE_STRING_TITLE",
        all(
            isinstance(result.title, str)
            and result.title == "missing"
            for result in missing_results
        ),
    )

    check(
        "MISSING_RESULTS_METADATA_DICTIONARY",
        all(
            isinstance(result.metadata, dict)
            for result in missing_results
        ),
    )

    check(
        "MISSING_RESULTS_STRUCTURED_ERROR",
        all(
            isinstance(
                result.metadata.get("error"),
                str,
            )
            and bool(
                result.metadata.get("error")
            )
            for result in missing_results
        ),
    )


# ------------------------------------------------------------
# B. Direct extractor extension mismatches
# ------------------------------------------------------------

print()
print("=== B. DIRECT EXTRACTOR EXTENSION MISMATCH ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    wrong_for_txt = root / "wrong.md"
    wrong_for_txt.write_text(
        "Body.",
        encoding="utf-8",
    )

    wrong_for_md = root / "wrong.txt"
    wrong_for_md.write_text(
        "Body.",
        encoding="utf-8",
    )

    wrong_for_html = root / "wrong.txt"
    wrong_for_html.write_text(
        "Body.",
        encoding="utf-8",
    )

    wrong_for_docx = root / "wrong.txt"
    wrong_for_docx.write_text(
        "Body.",
        encoding="utf-8",
    )

    mismatch_results = [
        extractor.extract_txt_upload_v1(
            wrong_for_txt
        ),
        extractor.extract_markdown_upload_v1(
            wrong_for_md
        ),
        extractor.extract_html_upload_v1(
            wrong_for_html
        ),
        extractor.extract_docx_upload_v1(
            wrong_for_docx
        ),
    ]

    check(
        "TXT_REJECTS_NON_TXT_WITH_UNSUPPORTED_EXTENSION",
        mismatch_results[0].extraction_status
        == "unsupported_extension",
    )

    check(
        "MARKDOWN_REJECTS_NON_MARKDOWN_WITH_UNSUPPORTED_EXTENSION",
        mismatch_results[1].extraction_status
        == "unsupported_extension",
    )

    check(
        "HTML_REJECTS_NON_HTML_WITH_UNSUPPORTED_EXTENSION",
        mismatch_results[2].extraction_status
        == "unsupported_extension",
    )

    check(
        "DOCX_REJECTS_NON_DOCX_WITH_UNSUPPORTED_EXTENSION",
        mismatch_results[3].extraction_status
        == "unsupported_extension",
    )

    check(
        "EXTENSION_MISMATCH_CONFIDENCE_ZERO",
        all(
            result.extraction_confidence
            == 0.0
            for result in mismatch_results
        ),
    )

    check(
        "EXTENSION_MISMATCH_PRESERVES_RESULT_CONTRACT",
        all(
            isinstance(
                result,
                extractor.UploadExtractionResult,
            )
            and isinstance(
                result.title,
                str,
            )
            and result.text == ""
            and result.headings == []
            and isinstance(
                result.metadata,
                dict,
            )
            for result in mismatch_results
        ),
    )


# ------------------------------------------------------------
# C. Dispatcher unsupported physical extension
# ------------------------------------------------------------

print()
print("=== C. DISPATCHER UNSUPPORTED SOURCE TYPE ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "unsupported.pdf"

    path.write_bytes(
        b"%PDF-test"
    )

    result = extractor.extract_upload_document_v1(
        path
    )

    check(
        "DISPATCHER_UNSUPPORTED_STATUS",
        result.extraction_status
        == "unsupported_source_type",
    )

    check(
        "DISPATCHER_UNSUPPORTED_CONFIDENCE_ZERO",
        result.extraction_confidence
        == 0.0,
    )

    check(
        "DISPATCHER_UNSUPPORTED_IS_STRUCTURED_RESULT",
        isinstance(
            result,
            extractor.UploadExtractionResult,
        ),
    )

    check(
        "DISPATCHER_UNSUPPORTED_HAS_SUPPORTED_EXTENSIONS_METADATA",
        isinstance(
            result.metadata.get(
                "supported_extensions"
            ),
            list,
        )
        and set(
            result.metadata.get(
                "supported_extensions"
            )
        )
        == set(
            extractor.SUPPORTED_UPLOAD_EXTENSIONS.keys()
        ),
    )


# ------------------------------------------------------------
# D. Directory / non-file path behavior
# ------------------------------------------------------------

print()
print("=== D. DIRECTORY PATH BEHAVIOR ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    directory_txt = root / "folder.txt"
    directory_txt.mkdir()

    directory_md = root / "folder.md"
    directory_md.mkdir()

    directory_html = root / "folder.html"
    directory_html.mkdir()

    directory_docx = root / "folder.docx"
    directory_docx.mkdir()

    directory_results = [
        extractor.extract_txt_upload_v1(
            directory_txt
        ),
        extractor.extract_markdown_upload_v1(
            directory_md
        ),
        extractor.extract_html_upload_v1(
            directory_html
        ),
        extractor.extract_docx_upload_v1(
            directory_docx
        ),
    ]

    check(
        "DIRECTORY_PATHS_RETURN_STRUCTURED_RESULTS",
        all(
            isinstance(
                result,
                extractor.UploadExtractionResult,
            )
            for result in directory_results
        ),
    )

    check(
        "DIRECTORY_PATHS_DO_NOT_REPORT_SUCCESS",
        all(
            result.extraction_status
            != "success"
            for result in directory_results
        ),
    )

    check(
        "DIRECTORY_PATHS_HAVE_ZERO_CONFIDENCE",
        all(
            result.extraction_confidence
            == 0.0
            for result in directory_results
        ),
    )


# ------------------------------------------------------------
# E. Failure-result serialization
# ------------------------------------------------------------

print()
print("=== E. FAILURE SERIALIZATION CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    result = extractor.extract_txt_upload_v1(
        Path(temp_dir) / "missing.txt"
    )

    serialized = (
        extractor.serialize_upload_extraction_result(
            result
        )
    )

    check(
        "FAILURE_SERIALIZER_PRESERVES_STATUS",
        serialized.get(
            "extraction_status"
        )
        == "missing_file",
    )

    check(
        "FAILURE_SERIALIZER_PRESERVES_CONFIDENCE",
        serialized.get(
            "extraction_confidence"
        )
        == 0.0,
    )

    check(
        "FAILURE_SERIALIZER_PRESERVES_EMPTY_TEXT",
        serialized.get("text") == "",
    )

    check(
        "FAILURE_SERIALIZER_PRESERVES_METADATA",
        serialized.get("metadata")
        == result.metadata,
    )


# ------------------------------------------------------------
# F. Source immutability on invalid inputs
# ------------------------------------------------------------

print()
print("=== F. INVALID-INPUT SOURCE IMMUTABILITY ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "wrong.txt"

    path.write_bytes(
        b"ORIGINAL_INVALID_INPUT_BYTES"
    )

    before = path.read_bytes()

    extractor.extract_docx_upload_v1(
        path
    )

    after = path.read_bytes()

    check(
        "INVALID_INPUT_SOURCE_BYTES_UNCHANGED",
        before == after,
    )


# ------------------------------------------------------------
# G. Extractor-vs-HTTP validation boundary
# ------------------------------------------------------------

print()
print("=== G. EXTRACTOR / HTTP VALIDATION BOUNDARY ===")

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
    "EXTRACTOR_LAYER_DOES_NOT_USE_HTTPEXCEPTION",
    "httpexception"
    not in extractor_sources,
)

check(
    "EXTRACTOR_LAYER_DOES_NOT_USE_HTTP_STATUS_CODES",
    "status_code="
    not in extractor_sources
    and "status_code ="
    not in extractor_sources,
)


# ------------------------------------------------------------
# H. Downstream / runtime isolation
# ------------------------------------------------------------

print()
print("=== H. INVALID-INPUT DOWNSTREAM ISOLATION ===")

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
        f"INVALID_INPUT_HANDLING_DOES_NOT_DEPEND_ON_{forbidden.upper()}",
        forbidden not in extractor_sources,
    )


# ------------------------------------------------------------
# I. Cross-format consistency
# ------------------------------------------------------------

print()
print("=== I. CROSS-FORMAT FAILURE CONSISTENCY ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    missing_results = [
        extractor.extract_txt_upload_v1(
            root / "same.txt"
        ),
        extractor.extract_markdown_upload_v1(
            root / "same.md"
        ),
        extractor.extract_html_upload_v1(
            root / "same.html"
        ),
        extractor.extract_docx_upload_v1(
            root / "same.docx"
        ),
    ]

    check(
        "ALL_FORMATS_SHARE_MISSING_FILE_STATUS",
        {
            result.extraction_status
            for result in missing_results
        }
        == {"missing_file"},
    )

    check(
        "ALL_FORMATS_SHARE_ZERO_CONFIDENCE_ON_MISSING_FILE",
        {
            result.extraction_confidence
            for result in missing_results
        }
        == {0.0},
    )

    check(
        "ALL_FORMATS_SHARE_EMPTY_TEXT_ON_MISSING_FILE",
        {
            result.text
            for result in missing_results
        }
        == {""},
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
        "U6.14_MISSING_FILE_INVALID_INPUT_CONTRACT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U6.14 missing-file / invalid-input contract verification failed."
    )

print(
    "U6.14_MISSING_FILE_INVALID_INPUT_CONTRACT: CERTIFIED"
)

print(
    "U6.14_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U6.15_FORMAT_SPECIFIC_FAILURE_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U6.14_FINAL_MISSING_FILE_INVALID_INPUT_VERIFICATION: PASS"
)