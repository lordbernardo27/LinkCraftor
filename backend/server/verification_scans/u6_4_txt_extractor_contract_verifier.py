from __future__ import annotations

import inspect
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import backend.server.stores.upload_document_extractor as extractor


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U6.4 - TXT EXTRACTOR CONTRACT ===")


txt_source = inspect.getsource(
    extractor.extract_txt_upload_v1
).lower()

normalizer_source = inspect.getsource(
    extractor._normalize_upload_text_v2
).lower()


# ------------------------------------------------------------
# A. Input / extension contract
# ------------------------------------------------------------

print()
print("=== A. INPUT / EXTENSION CONTRACT ===")

signature = inspect.signature(
    extractor.extract_txt_upload_v1
)

params = list(
    signature.parameters.values()
)

check(
    "TXT_ACCEPTS_SINGLE_PATH_PARAMETER",
    len(params) == 1
    and params[0].name == "path",
)

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    txt_path = root / "document.txt"
    txt_path.write_text(
        "Hello",
        encoding="utf-8",
    )

    upper_txt_path = root / "DOCUMENT.TXT"
    upper_txt_path.write_text(
        "Hello",
        encoding="utf-8",
    )

    wrong_path = root / "document.md"
    wrong_path.write_text(
        "Hello",
        encoding="utf-8",
    )

    txt_result = extractor.extract_txt_upload_v1(
        txt_path
    )

    upper_result = extractor.extract_txt_upload_v1(
        upper_txt_path
    )

    wrong_result = extractor.extract_txt_upload_v1(
        wrong_path
    )

    check(
        "LOWERCASE_TXT_ACCEPTED",
        txt_result.extraction_status
        == "success",
    )

    check(
        "UPPERCASE_TXT_ACCEPTED",
        upper_result.extraction_status
        == "success",
    )

    check(
        "NON_TXT_RETURNS_UNSUPPORTED_EXTENSION",
        wrong_result.extraction_status
        == "unsupported_extension",
    )

    check(
        "NON_TXT_ERROR_IS_STRUCTURED",
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
    missing = Path(temp_dir) / "missing.txt"

    missing_result = (
        extractor.extract_txt_upload_v1(
            missing
        )
    )

    check(
        "MISSING_TXT_RETURNS_CANONICAL_TYPE",
        isinstance(
            missing_result,
            extractor.UploadExtractionResult,
        ),
    )

    check(
        "MISSING_TXT_STATUS",
        missing_result.extraction_status
        == "missing_file",
    )

    check(
        "MISSING_TXT_CONFIDENCE_ZERO",
        missing_result.extraction_confidence
        == 0.0,
    )


# ------------------------------------------------------------
# C. UTF-8 reading / normalization
# ------------------------------------------------------------

print()
print("=== C. TEXT READING / NORMALIZATION ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    path = root / "normalized.txt"

    raw = (
        "  First   paragraph line.  \r\n"
        "Second\tline.\r\n"
        "\r\n"
        "\r\n"
        "  Third   paragraph.  "
    )

    path.write_text(
        raw,
        encoding="utf-8",
    )

    result = extractor.extract_txt_upload_v1(
        path
    )

    check(
        "TXT_UTF8_READ_SUCCEEDS",
        result.extraction_status
        == "success",
    )

    check(
        "TXT_NORMALIZATION_COLLAPSES_INTRA_LINE_WHITESPACE",
        "First paragraph line."
        in result.text
        and "Second line."
        in result.text
        and "Third paragraph."
        in result.text,
    )

    check(
        "TXT_PARAGRAPH_BOUNDARY_PRESERVED",
        "\n\n" in result.text,
    )

    check(
        "TXT_NORMALIZED_TEXT_HAS_NO_CR",
        "\r" not in result.text,
    )

    check(
        "TXT_NORMALIZER_EXPLICITLY_PRESERVES_PARAGRAPH_BOUNDARY",
        '"\\n\\n".join(blocks)'
        in normalizer_source,
    )


# ------------------------------------------------------------
# D. Empty / whitespace-only contract
# ------------------------------------------------------------

print()
print("=== D. EMPTY TEXT CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    empty_path = root / "empty.txt"
    empty_path.write_text(
        "",
        encoding="utf-8",
    )

    whitespace_path = root / "whitespace.txt"
    whitespace_path.write_text(
        " \n\t\n   ",
        encoding="utf-8",
    )

    empty_result = extractor.extract_txt_upload_v1(
        empty_path
    )

    whitespace_result = (
        extractor.extract_txt_upload_v1(
            whitespace_path
        )
    )

    check(
        "EMPTY_TXT_RETURNS_EMPTY_TEXT",
        empty_result.extraction_status
        == "empty_text",
    )

    check(
        "WHITESPACE_ONLY_TXT_RETURNS_EMPTY_TEXT",
        whitespace_result.extraction_status
        == "empty_text",
    )

    check(
        "EMPTY_TXT_CONFIDENCE_ZERO",
        empty_result.extraction_confidence
        == 0.0,
    )

    check(
        "WHITESPACE_TXT_NORMALIZED_COUNT_ZERO",
        whitespace_result.metadata.get(
            "normalized_char_count"
        )
        == 0,
    )


# ------------------------------------------------------------
# E. Successful result contract
# ------------------------------------------------------------

print()
print("=== E. SUCCESS RESULT CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "my_document.txt"

    path.write_text(
        "Paragraph one.\n\nParagraph two.",
        encoding="utf-8",
    )

    result = extractor.extract_txt_upload_v1(
        path
    )

    check(
        "TXT_RESULT_IS_CANONICAL_TYPE",
        isinstance(
            result,
            extractor.UploadExtractionResult,
        ),
    )

    check(
        "TXT_SOURCE_TYPE_IS_TXT",
        result.source_type == "txt",
    )

    check(
        "TXT_TITLE_FROM_FILENAME_STEM",
        result.title == "my_document",
    )

    check(
        "TXT_TEXT_IS_NONEMPTY_STRING",
        isinstance(result.text, str)
        and bool(result.text),
    )

    check(
        "TXT_HEADINGS_ALWAYS_EMPTY",
        result.headings == [],
    )

    check(
        "TXT_METADATA_IS_DICT",
        isinstance(result.metadata, dict),
    )

    check(
        "TXT_STATUS_SUCCESS",
        result.extraction_status == "success",
    )

    check(
        "TXT_CONFIDENCE_NUMERIC",
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
        "TXT_CREATED_AT_IS_ISO_TIMESTAMP",
        created_ok,
    )


# ------------------------------------------------------------
# F. Metadata contract
# ------------------------------------------------------------

print()
print("=== F. TXT METADATA CONTRACT ===")

required_metadata = {
    "filename",
    "extension",
    "extractor",
    "raw_char_count",
    "normalized_char_count",
    "line_count",
    "paragraph_count",
}

check(
    "TXT_METADATA_HAS_REQUIRED_KEYS",
    required_metadata.issubset(
        set(result.metadata.keys())
    ),
)

check(
    "TXT_METADATA_FILENAME",
    result.metadata.get("filename")
    == "my_document.txt",
)

check(
    "TXT_METADATA_EXTENSION",
    result.metadata.get("extension")
    == ".txt",
)

check(
    "TXT_METADATA_EXTRACTOR_IDENTITY",
    result.metadata.get("extractor")
    == "extract_txt_upload_v1",
)

check(
    "TXT_RAW_CHAR_COUNT_NUMERIC",
    isinstance(
        result.metadata.get(
            "raw_char_count"
        ),
        int,
    ),
)

check(
    "TXT_NORMALIZED_CHAR_COUNT_MATCHES_TEXT",
    result.metadata.get(
        "normalized_char_count"
    )
    == len(result.text),
)

check(
    "TXT_LINE_COUNT_MATCHES_TEXT",
    result.metadata.get("line_count")
    == len(result.text.splitlines()),
)

check(
    "TXT_PARAGRAPH_COUNT_MATCHES_TEXT",
    result.metadata.get(
        "paragraph_count"
    )
    == result.text.count("\n\n") + 1,
)


# ------------------------------------------------------------
# G. TXT does not infer headings
# ------------------------------------------------------------

print()
print("=== G. NO TXT HEADING INFERENCE ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "headings.txt"

    path.write_text(
        "THIS LOOKS LIKE A HEADING\n\n"
        "Body paragraph.",
        encoding="utf-8",
    )

    heading_result = (
        extractor.extract_txt_upload_v1(
            path
        )
    )

    check(
        "TXT_DOES_NOT_INFER_HEADINGS",
        heading_result.headings == [],
    )

    check(
        "TXT_TITLE_STILL_FILENAME_STEM",
        heading_result.title == "headings",
    )


# ------------------------------------------------------------
# H. Source immutability
# ------------------------------------------------------------

print()
print("=== H. SOURCE IMMUTABILITY ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "immutable.txt"

    original = (
        "Original source.\n\n"
        "Second paragraph."
    )

    path.write_text(
        original,
        encoding="utf-8",
    )

    before = path.read_bytes()

    extractor.extract_txt_upload_v1(
        path
    )

    after = path.read_bytes()

    check(
        "TXT_SOURCE_BYTES_UNCHANGED",
        before == after,
    )

check(
    "TXT_SOURCE_HAS_NO_WRITE_MUTATION_CALLS",
    "write_text(" not in txt_source
    and "write_bytes(" not in txt_source
    and ".unlink(" not in txt_source
    and ".rename(" not in txt_source
    and ".replace(" not in txt_source,
)


# ------------------------------------------------------------
# I. Cross-format / downstream isolation
# ------------------------------------------------------------

print()
print("=== I. CROSS-FORMAT / DOWNSTREAM ISOLATION ===")

check(
    "TXT_DOES_NOT_CALL_MARKDOWN_EXTRACTOR",
    "extract_markdown_upload_v1"
    not in txt_source,
)

check(
    "TXT_DOES_NOT_CALL_HTML_EXTRACTOR",
    "extract_html_upload_v1"
    not in txt_source,
)

check(
    "TXT_DOES_NOT_CALL_DOCX_EXTRACTOR",
    "extract_docx_upload_v1"
    not in txt_source,
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
        f"TXT_DOES_NOT_INVOKE_{forbidden.upper()}",
        forbidden not in txt_source,
    )


# ------------------------------------------------------------
# J. Unexpected extraction failure contract
# ------------------------------------------------------------

print()
print("=== J. EXTRACTION ERROR CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "failure.txt"

    path.write_text(
        "Hello",
        encoding="utf-8",
    )

    with patch.object(
        Path,
        "read_text",
        side_effect=OSError(
            "private read failure detail"
        ),
    ):
        failure_result = (
            extractor.extract_txt_upload_v1(
                path
            )
        )

    check(
        "UNEXPECTED_READ_FAILURE_RETURNS_CANONICAL_TYPE",
        isinstance(
            failure_result,
            extractor.UploadExtractionResult,
        ),
    )

    check(
        "UNEXPECTED_READ_FAILURE_STATUS",
        failure_result.extraction_status
        == "extraction_error",
    )

    check(
        "UNEXPECTED_READ_FAILURE_CONFIDENCE_ZERO",
        failure_result.extraction_confidence
        == 0.0,
    )

    check(
        "UNEXPECTED_READ_FAILURE_REMAINS_STRUCTURED",
        isinstance(
            failure_result.metadata,
            dict,
        )
        and "error"
        in failure_result.metadata,
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
        "U6.4_TXT_EXTRACTOR_CONTRACT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U6.4 TXT extractor contract verification failed."
    )

print(
    "U6.4_TXT_EXTRACTOR_CONTRACT: CERTIFIED"
)

print(
    "U6.4_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U6.5_MARKDOWN_EXTRACTOR_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U6.4_FINAL_TXT_EXTRACTOR_VERIFICATION: PASS"
)