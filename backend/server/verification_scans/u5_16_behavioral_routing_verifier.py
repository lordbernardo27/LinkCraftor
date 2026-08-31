from __future__ import annotations

import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import backend.server.stores.upload_document_extractor as extractor
import backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake as upload_intake


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U5.16 - BEHAVIORAL ROUTING VERIFICATION ===")


router = extractor.detect_upload_source_type
dispatcher = extractor.extract_upload_document_v1

intake_source = inspect.getsource(
    upload_intake.run_upload_intake
).lower()


# ------------------------------------------------------------
# A. Direct router behavior
# ------------------------------------------------------------

print()
print("=== A. DIRECT ROUTER BEHAVIOR ===")

routing_cases = {
    "document.txt": "txt",
    "document.md": "markdown",
    "document.markdown": "markdown",
    "document.html": "html",
    "document.htm": "html",
    "document.docx": "docx",

    "DOCUMENT.TXT": "txt",
    "DOCUMENT.MD": "markdown",
    "DOCUMENT.MARKDOWN": "markdown",
    "DOCUMENT.HTML": "html",
    "DOCUMENT.HTM": "html",
    "DOCUMENT.DOCX": "docx",

    "Mixed.TxT": "txt",
    "Mixed.Md": "markdown",
    "Mixed.MarkDown": "markdown",
    "Mixed.HtMl": "html",
    "Mixed.HtM": "html",
    "Mixed.DoCx": "docx",

    "document.pdf": "unsupported",
    "document": "unsupported",
    "document.": "unsupported",
    "document.md.exe": "unsupported",
    "document.docx.zip": "unsupported",
    "document.pdf.docx": "docx",
}

for filename, expected in routing_cases.items():
    check(
        f"ROUTER_{filename.replace('.', '_').upper()}",
        router(filename) == expected,
    )


# ------------------------------------------------------------
# B. Alias convergence + physical distinction
# ------------------------------------------------------------

print()
print("=== B. ALIAS CONVERGENCE ===")

check(
    "MD_AND_MARKDOWN_CONVERGE_LOGICALLY",
    router("a.md") == "markdown"
    and router("a.markdown") == "markdown",
)

check(
    "HTML_AND_HTM_CONVERGE_LOGICALLY",
    router("a.html") == "html"
    and router("a.htm") == "html",
)

check(
    "MD_AND_MARKDOWN_REMAIN_PHYSICALLY_DISTINCT",
    Path("a.md").suffix.lower() == ".md"
    and Path("a.markdown").suffix.lower()
    == ".markdown",
)

check(
    "HTML_AND_HTM_REMAIN_PHYSICALLY_DISTINCT",
    Path("a.html").suffix.lower() == ".html"
    and Path("a.htm").suffix.lower()
    == ".htm",
)


# ------------------------------------------------------------
# C. Determinism
# ------------------------------------------------------------

print()
print("=== C. ROUTER DETERMINISM ===")

for filename in routing_cases:
    outputs = [
        router(filename)
        for _ in range(5)
    ]

    check(
        f"DETERMINISTIC_{filename.replace('.', '_').upper()}",
        len(set(outputs)) == 1,
    )


# ------------------------------------------------------------
# D. Dispatcher invokes only the resolved family extractor
# ------------------------------------------------------------

print()
print("=== D. DISPATCHER FAMILY INVOCATION ===")


def build_success_result(
    path: Path,
    source_type: str,
):
    return extractor.UploadExtractionResult(
        source_path=str(path),
        source_type=source_type,
        title=path.stem,
        text="test",
        headings=[],
        metadata={
            "filename": path.name,
            "extension": path.suffix.lower(),
            "extractor": "u5_16_mock",
        },
        extraction_status="success",
        extraction_confidence=1.0,
        created_at="2026-08-30T00:00:00+00:00",
    )


dispatch_cases = [
    ("document.txt", "txt", "txt"),
    ("document.md", "markdown", "markdown"),
    ("document.markdown", "markdown", "markdown"),
    ("document.html", "html", "html"),
    ("document.htm", "html", "html"),
    ("document.docx", "docx", "docx"),
]

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    for filename, expected_family, expected_called in dispatch_cases:
        path = root / filename
        path.write_bytes(b"placeholder")

        with patch.object(
            extractor,
            "extract_txt_upload_v1",
            return_value=build_success_result(
                path,
                "txt",
            ),
        ) as txt_mock, patch.object(
            extractor,
            "extract_markdown_upload_v1",
            return_value=build_success_result(
                path,
                "markdown",
            ),
        ) as md_mock, patch.object(
            extractor,
            "extract_html_upload_v1",
            return_value=build_success_result(
                path,
                "html",
            ),
        ) as html_mock, patch.object(
            extractor,
            "extract_docx_upload_v1",
            return_value=build_success_result(
                path,
                "docx",
            ),
        ) as docx_mock:

            result = dispatcher(path)

            counts = {
                "txt": txt_mock.call_count,
                "markdown": md_mock.call_count,
                "html": html_mock.call_count,
                "docx": docx_mock.call_count,
            }

            check(
                f"{expected_family.upper()}_DISPATCH_RESULT_SOURCE_TYPE",
                result.source_type
                == expected_family,
            )

            check(
                f"{filename.replace('.', '_').upper()}_ONLY_EXPECTED_EXTRACTOR_CALLED",
                counts[expected_called] == 1
                and sum(counts.values()) == 1,
            )


# ------------------------------------------------------------
# E. Unsupported suffix invokes no extractor
# ------------------------------------------------------------

print()
print("=== E. UNSUPPORTED DISPATCH BEHAVIOR ===")

with TemporaryDirectory() as temp_dir:
    path = Path(temp_dir) / "unsupported.pdf"
    path.write_text(
        "plain text",
        encoding="utf-8",
    )

    with patch.object(
        extractor,
        "extract_txt_upload_v1",
        wraps=extractor.extract_txt_upload_v1,
    ) as txt_mock, patch.object(
        extractor,
        "extract_markdown_upload_v1",
        wraps=extractor.extract_markdown_upload_v1,
    ) as md_mock, patch.object(
        extractor,
        "extract_html_upload_v1",
        wraps=extractor.extract_html_upload_v1,
    ) as html_mock, patch.object(
        extractor,
        "extract_docx_upload_v1",
        wraps=extractor.extract_docx_upload_v1,
    ) as docx_mock:

        result = dispatcher(path)

        check(
            "UNSUPPORTED_RESULT_SOURCE_TYPE",
            result.source_type
            == "unsupported",
        )

        check(
            "UNSUPPORTED_RESULT_STATUS",
            result.extraction_status
            == "unsupported_source_type",
        )

        check(
            "UNSUPPORTED_CALLS_NO_FORMAT_EXTRACTOR",
            txt_mock.call_count == 0
            and md_mock.call_count == 0
            and html_mock.call_count == 0
            and docx_mock.call_count == 0,
        )


# ------------------------------------------------------------
# F. Content appearance cannot change routing
# ------------------------------------------------------------

print()
print("=== F. CONTENT APPEARANCE NON-AUTHORITY ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    cases = [
        (
            "html_looking.txt",
            b"<html><body>Hello</body></html>",
            "txt",
        ),
        (
            "markdown_looking.html",
            b"# Heading\n\nMarkdown",
            "html",
        ),
        (
            "plain_text.md",
            b"Just plain text",
            "markdown",
        ),
        (
            "zip_looking.txt",
            b"PK\x03\x04fake archive",
            "txt",
        ),
        (
            "html_looking.pdf",
            b"<html><body>Hello</body></html>",
            "unsupported",
        ),
    ]

    for filename, body, expected in cases:
        path = root / filename
        path.write_bytes(body)

        check(
            f"CONTENT_DOES_NOT_OVERRIDE_{filename.replace('.', '_').upper()}",
            router(path) == expected,
        )


# ------------------------------------------------------------
# G. Defensive extractor extension guards
# ------------------------------------------------------------

print()
print("=== G. FORMAT-SPECIFIC DEFENSIVE GUARDS ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    wrong_txt = root / "wrong.pdf"
    wrong_txt.write_text(
        "text",
        encoding="utf-8",
    )

    txt_result = extractor.extract_txt_upload_v1(
        wrong_txt
    )

    md_result = extractor.extract_markdown_upload_v1(
        wrong_txt
    )

    html_result = extractor.extract_html_upload_v1(
        wrong_txt
    )

    docx_result = extractor.extract_docx_upload_v1(
        wrong_txt
    )

    check(
        "TXT_DEFENSIVE_EXTENSION_GUARD",
        txt_result.extraction_status
        == "unsupported_extension",
    )

    check(
        "MARKDOWN_DEFENSIVE_EXTENSION_GUARD",
        md_result.extraction_status
        == "unsupported_extension",
    )

    check(
        "HTML_DEFENSIVE_EXTENSION_GUARD",
        html_result.extraction_status
        == "unsupported_extension",
    )

    check(
        "DOCX_DEFENSIVE_EXTENSION_GUARD",
        docx_result.extraction_status
        == "unsupported_extension",
    )


# ------------------------------------------------------------
# H. Intake still reaches canonical dispatcher after persistence
# ------------------------------------------------------------

print()
print("=== H. INTAKE / DISPATCHER ORDERING ===")

store_pos = intake_source.find(
    "dependencies.store_and_index"
)

dispatcher_pos = intake_source.find(
    "extract_upload_document_v1"
)

check(
    "INTAKE_USES_CANONICAL_DISPATCHER",
    dispatcher_pos >= 0,
)

check(
    "INTAKE_DISPATCHES_AFTER_PERSISTENCE",
    store_pos >= 0
    and dispatcher_pos > store_pos,
)

check(
    "INTAKE_DOES_NOT_DUPLICATE_LOGICAL_FAMILY_SELECTION",
    'source_type == "txt"'
    not in intake_source
    and 'source_type == "markdown"'
    not in intake_source
    and 'source_type == "html"'
    not in intake_source
    and 'source_type == "docx"'
    not in intake_source,
)


# ------------------------------------------------------------
# I. MIME / magic remain non-authoritative
# ------------------------------------------------------------

print()
print("=== I. MIME / MAGIC NON-AUTHORITY ===")

router_source = inspect.getsource(
    extractor.detect_upload_source_type
).lower()

check(
    "ROUTER_HAS_NO_MIME_AUTHORITY",
    "mime" not in router_source
    and "content_type" not in router_source,
)

check(
    "ROUTER_HAS_NO_MAGIC_AUTHORITY",
    "magic" not in router_source,
)

check(
    "ROUTER_HAS_NO_SIGNATURE_AUTHORITY",
    "file_signature" not in router_source
    and "content_signature" not in router_source
    and "signature_bytes" not in router_source
    and "detect_signature" not in router_source,
)

check(
    "ROUTER_DOES_NOT_READ_CONTENT",
    ".read(" not in router_source
    and "read_bytes" not in router_source,
)


# ------------------------------------------------------------
# J. Unrelated pipeline isolation
# ------------------------------------------------------------

print()
print("=== J. UNRELATED PIPELINE ISOLATION ===")

dispatcher_source = inspect.getsource(
    extractor.extract_upload_document_v1
).lower()

combined_source = (
    router_source
    + "\n"
    + dispatcher_source
    + "\n"
    + intake_source
)

check(
    "WEBSITE_DOES_NOT_PARTICIPATE",
    "article_body_cleaning_engine"
    not in combined_source
    and "article_cleaning_pipeline"
    not in combined_source
    and "raw_website_html"
    not in combined_source,
)

check(
    "URL_IMPORT_DOES_NOT_PARTICIPATE",
    "/api/urls/import"
    not in combined_source,
)

check(
    "DRAFT_IMPORT_DOES_NOT_PARTICIPATE",
    "/api/draft/import"
    not in combined_source,
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
        "U5.16_BEHAVIORAL_ROUTING_VERIFICATION: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U5.16 behavioral routing verification failed."
    )

print(
    "U5.16_BEHAVIORAL_ROUTING_VERIFICATION: CERTIFIED"
)

print(
    "U5.16_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U5.17_BUILD_INTEGRATION_VERIFICATION_TRANSITION: AUTHORIZED"
)

print(
    "U5.16_FINAL_BEHAVIORAL_ROUTING_VERIFICATION: PASS"
)