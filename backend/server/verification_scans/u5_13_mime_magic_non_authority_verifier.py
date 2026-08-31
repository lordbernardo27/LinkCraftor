from __future__ import annotations

import asyncio
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock

from fastapi import HTTPException

import backend.server.routes.files as files_route
import backend.server.stores.upload_document_extractor as extractor
import backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake as upload_intake


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U5.13 - MIME / MAGIC NON-AUTHORITY CONFIRMATION ===")


router = extractor.detect_upload_source_type
router_source = inspect.getsource(router).lower()

intake_source = inspect.getsource(
    upload_intake.run_upload_intake
).lower()

route_source = inspect.getsource(
    files_route.upload_file
).lower()


# ------------------------------------------------------------
# A. Physical suffix remains sole routing authority
# ------------------------------------------------------------

print()
print("=== A. PHYSICAL SUFFIX AUTHORITY ===")

check(
    "TXT_SUFFIX_ROUTES_TXT",
    router("document.txt") == "txt",
)

check(
    "MARKDOWN_SUFFIX_ROUTES_MARKDOWN",
    router("document.md") == "markdown"
    and router("document.markdown") == "markdown",
)

check(
    "HTML_SUFFIX_ROUTES_HTML",
    router("document.html") == "html"
    and router("document.htm") == "html",
)

check(
    "DOCX_SUFFIX_ROUTES_DOCX",
    router("document.docx") == "docx",
)

check(
    "UNSUPPORTED_SUFFIX_REMAINS_UNSUPPORTED",
    router("document.pdf") == "unsupported",
)


# ------------------------------------------------------------
# B. Router has no MIME/content-type authority
# ------------------------------------------------------------

print()
print("=== B. MIME / CONTENT-TYPE NON-AUTHORITY ===")

check(
    "ROUTER_DOES_NOT_USE_MIME",
    "mime" not in router_source,
)

check(
    "ROUTER_DOES_NOT_USE_CONTENT_TYPE",
    "content_type" not in router_source,
)

check(
    "ROUTER_DOES_NOT_REFERENCE_UPLOADFILE",
    "uploadfile" not in router_source,
)

check(
    "ROUTER_DOES_NOT_REFERENCE_REQUEST_HEADERS",
    "headers" not in router_source,
)


# ------------------------------------------------------------
# C. MIME cannot rescue unsupported suffix
# ------------------------------------------------------------

print()
print("=== C. MIME CANNOT RESCUE UNSUPPORTED SUFFIX ===")


class FakeUpload:
    def __init__(
        self,
        filename: str,
        content_type: str,
        body: bytes,
    ) -> None:
        self.filename = filename
        self.content_type = content_type
        self._body = body
        self.read_calls = 0

    async def read(self, *args, **kwargs):
        self.read_calls += 1
        return self._body


def build_dependencies(guess_value: str):
    return upload_intake.UploadIntakeDependencies(
        guess_extension=Mock(return_value=guess_value),
        normalize_workspace_id=Mock(return_value="ws_test"),
        extract_preview=Mock(),
        store_and_index=Mock(),
        rollback_committed_upload=Mock(),
        workspace_directory=Mock(return_value=Path(".")),
        allowed_extensions={
            ".txt",
            ".md",
            ".markdown",
            ".html",
            ".htm",
            ".docx",
        },
    )


async def run_rejected(file_obj, dependencies):
    try:
        await upload_intake.run_upload_intake(
            workspace_id="ws_test",
            file=file_obj,
            dependencies=dependencies,
        )
    except HTTPException as exc:
        return exc

    return None


mime_rescue_cases = [
    (
        "fake.pdf",
        "text/plain",
        b"Plain text that looks like TXT",
    ),
    (
        "fake.pdf",
        "text/html",
        b"<html><body>Hello</body></html>",
    ),
    (
        "fake.pdf",
        "text/markdown",
        b"# Markdown heading",
    ),
    (
        "fake.pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        b"PK\x03\x04fake-docx",
    ),
]

for filename, content_type, body in mime_rescue_cases:
    fake = FakeUpload(
        filename,
        content_type,
        body,
    )

    exc = asyncio.run(
        run_rejected(
            fake,
            build_dependencies(".pdf"),
        )
    )

    check(
        f"MIME_CANNOT_RESCUE_{content_type.replace('/', '_').replace('-', '_').upper()}",
        isinstance(exc, HTTPException)
        and exc.status_code == 400
        and fake.read_calls == 0,
    )


# ------------------------------------------------------------
# D. Magic/signature/content sniffing is not router authority
# ------------------------------------------------------------

print()
print("=== D. MAGIC / SIGNATURE NON-AUTHORITY ===")

check(
    "ROUTER_DOES_NOT_READ_BYTES",
    ".read(" not in router_source
    and "read_bytes" not in router_source,
)

check(
    "ROUTER_DOES_NOT_USE_MAGIC",
    "magic" not in router_source,
)

check(
    "ROUTER_DOES_NOT_USE_FILE_SIGNATURE",
    "file_signature" not in router_source,
)

check(
    "ROUTER_DOES_NOT_USE_CONTENT_SIGNATURE",
    "content_signature" not in router_source,
)

check(
    "ROUTER_DOES_NOT_USE_SIGNATURE_BYTES",
    "signature_bytes" not in router_source,
)

check(
    "ROUTER_DOES_NOT_DETECT_SIGNATURE",
    "detect_signature" not in router_source,
)

check(
    "ROUTER_DOES_NOT_USE_ZIPFILE",
    "zipfile" not in router_source,
)

check(
    "ROUTER_DOES_NOT_USE_PK_SIGNATURE",
    "pk\\x03\\x04" not in router_source,
)


# ------------------------------------------------------------
# E. Content appearance cannot determine family
# ------------------------------------------------------------

print()
print("=== E. CONTENT APPEARANCE NON-AUTHORITY ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    html_bytes_txt = root / "looks_html.txt"
    html_bytes_txt.write_text(
        "<html><body>Hello</body></html>",
        encoding="utf-8",
    )

    markdown_bytes_html = root / "looks_markdown.html"
    markdown_bytes_html.write_text(
        "# Markdown heading",
        encoding="utf-8",
    )

    plain_text_md = root / "looks_plain.md"
    plain_text_md.write_text(
        "Plain text only",
        encoding="utf-8",
    )

    fake_zip_txt = root / "looks_docx.txt"
    fake_zip_txt.write_bytes(
        b"PK\x03\x04not-really-a-docx"
    )

    check(
        "HTML_LOOKING_TXT_STILL_ROUTES_TXT",
        router(html_bytes_txt) == "txt",
    )

    check(
        "MARKDOWN_LOOKING_HTML_STILL_ROUTES_HTML",
        router(markdown_bytes_html) == "html",
    )

    check(
        "PLAIN_TEXT_MD_STILL_ROUTES_MARKDOWN",
        router(plain_text_md) == "markdown",
    )

    check(
        "ZIP_LOOKING_TXT_STILL_ROUTES_TXT",
        router(fake_zip_txt) == "txt",
    )


# ------------------------------------------------------------
# F. DOCX suffix authority precedes archive parsing
# ------------------------------------------------------------

print()
print("=== F. DOCX SUFFIX AUTHORITY BEFORE PARSING ===")

with TemporaryDirectory() as temp_dir:
    fake_docx = Path(temp_dir) / "fake.docx"
    fake_docx.write_bytes(
        b"not-a-real-docx"
    )

    check(
        "FAKE_DOCX_STILL_ROUTES_DOCX_BY_SUFFIX",
        router(fake_docx) == "docx",
    )

    fake_docx_result = extractor.extract_docx_upload_v1(
        fake_docx
    )

    check(
        "DOCX_PARSING_FAILURE_DOES_NOT_CHANGE_ROUTER_FAMILY",
        router(fake_docx) == "docx"
        and fake_docx_result.source_type == "docx",
    )

    check(
        "DOCX_PARSING_FAILURE_REMAINS_EXTRACTOR_CONCERN",
        fake_docx_result.extraction_status
        in {
            "invalid_docx",
            "extraction_error",
            "empty_text",
        },
    )


# ------------------------------------------------------------
# G. Intake and route do not use MIME for family selection
# ------------------------------------------------------------

print()
print("=== G. INTAKE / ROUTE MIME ISOLATION ===")

check(
    "INTAKE_DOES_NOT_USE_CONTENT_TYPE_FOR_ROUTING",
    "content_type" not in intake_source,
)

check(
    "INTAKE_DOES_NOT_USE_MIME_FOR_ROUTING",
    "mime" not in intake_source,
)

check(
    "ROUTE_DOES_NOT_COMPARE_CONTENT_TYPE_FOR_ROUTING",
    'if file.content_type' not in route_source
    and 'if content_type' not in route_source,
)

check(
    "ROUTE_DOES_NOT_USE_MIME_FOR_ROUTING",
    "mimetypes" not in route_source
    and "magic" not in route_source,
)


# ------------------------------------------------------------
# H. Content type may exist as metadata without routing authority
# ------------------------------------------------------------

print()
print("=== H. CONTENT TYPE IS METADATA ONLY ===")

check(
    "PUBLIC_RESPONSE_MAY_EXPOSE_CONTENT_TYPE_METADATA",
    '"content_type"' in route_source,
)

check(
    "CONTENT_TYPE_METADATA_DOES_NOT_FEED_ROUTER",
    "detect_upload_source_type("
    not in route_source
    or "content_type" not in router_source,
)


# ------------------------------------------------------------
# I. Website logic remains separate
# ------------------------------------------------------------

print()
print("=== I. WEBSITE / OTHER PIPELINE ISOLATION ===")

combined_upload_source = (
    router_source
    + "\n"
    + intake_source
    + "\n"
    + route_source
)

check(
    "WEBSITE_CONTENT_ACQUISITION_NOT_ROUTER_AUTHORITY",
    "enterprise_raw_html_acquisition_engine"
    not in combined_upload_source
    and "raw_website_html_fetch_runner"
    not in combined_upload_source
    and "article_body_cleaning_engine"
    not in combined_upload_source
    and "article_cleaning_pipeline"
    not in combined_upload_source,
)

check(
    "URL_IMPORT_NOT_ROUTER_AUTHORITY",
    "/api/urls/import"
    not in combined_upload_source,
)

check(
    "DRAFT_IMPORT_NOT_ROUTER_AUTHORITY",
    "/api/draft/import"
    not in combined_upload_source,
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
        "U5.13_MIME_MAGIC_NON_AUTHORITY: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U5.13 MIME/magic non-authority verification failed."
    )

print(
    "U5.13_MIME_MAGIC_NON_AUTHORITY: CERTIFIED"
)

print(
    "U5.13_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U5.14_ERROR_CONTRACT_TRANSITION: AUTHORIZED"
)

print(
    "U5.13_FINAL_MIME_MAGIC_VERIFICATION: PASS"
)