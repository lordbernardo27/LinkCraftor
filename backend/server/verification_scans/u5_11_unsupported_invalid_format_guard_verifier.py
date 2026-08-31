from __future__ import annotations

import asyncio
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from fastapi import HTTPException, UploadFile

import backend.server.routes.files as files_route
import backend.server.stores.upload_document_extractor as extractor
import backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake as upload_intake


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U5.11 - UNSUPPORTED / INVALID FORMAT GUARD ===")


router = extractor.detect_upload_source_type
router_source = inspect.getsource(router).lower()

intake_source = inspect.getsource(
    upload_intake.run_upload_intake
).lower()

safe_filename_source = inspect.getsource(
    files_route._safe_upload_filename
).lower()


# ------------------------------------------------------------
# A. Unsupported router outputs
# ------------------------------------------------------------

print()
print("=== A. UNSUPPORTED ROUTER OUTPUTS ===")

unsupported_cases = {
    "document.pdf": "unsupported",
    "document.exe": "unsupported",
    "document": "unsupported",
    "document.": "unsupported",
    "document.md.exe": "unsupported",
    "document.docx.zip": "unsupported",
}

for filename, expected in unsupported_cases.items():
    check(
        f"UNSUPPORTED_{filename.replace('.', '_').upper()}",
        router(filename) == expected,
    )

check(
    "FINAL_SUFFIX_DOCX_REMAINS_AUTHORITATIVE",
    router("document.pdf.docx") == "docx",
)


# ------------------------------------------------------------
# B. Unsupported suffix cannot reach format extractors
# ------------------------------------------------------------

print()
print("=== B. UNSUPPORTED DISPATCH GUARD ===")

with TemporaryDirectory() as temp_dir:
    unsupported_path = Path(temp_dir) / "sample.pdf"
    unsupported_path.write_text(
        "plain content",
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

        result = extractor.extract_upload_document_v1(
            unsupported_path
        )

        check(
            "UNSUPPORTED_DISPATCH_RESULT",
            result.source_type == "unsupported",
        )

        check(
            "UNSUPPORTED_DOES_NOT_CALL_TXT",
            txt_mock.call_count == 0,
        )

        check(
            "UNSUPPORTED_DOES_NOT_CALL_MARKDOWN",
            md_mock.call_count == 0,
        )

        check(
            "UNSUPPORTED_DOES_NOT_CALL_HTML",
            html_mock.call_count == 0,
        )

        check(
            "UNSUPPORTED_DOES_NOT_CALL_DOCX",
            docx_mock.call_count == 0,
        )


# ------------------------------------------------------------
# C. Intake rejection occurs before read/preview/persistence/extraction
# ------------------------------------------------------------

print()
print("=== C. INTAKE EARLY REJECTION ORDER ===")


class FakeUpload:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.read_calls = 0

    async def read(self, *args, **kwargs):
        self.read_calls += 1
        return b"should-not-be-read"


fake_file = FakeUpload("document.pdf")

guess_extension = Mock(
    return_value=".pdf"
)

normalize_workspace_id = Mock(
    return_value="ws_test"
)

extract_preview = Mock()

store_and_index = Mock()

rollback_committed_upload = Mock()

workspace_directory = Mock(
    return_value=Path(".")
)

dependencies = upload_intake.UploadIntakeDependencies(
    guess_extension=guess_extension,
    normalize_workspace_id=normalize_workspace_id,
    extract_preview=extract_preview,
    store_and_index=store_and_index,
    rollback_committed_upload=rollback_committed_upload,
    workspace_directory=workspace_directory,
    allowed_extensions={
        ".txt",
        ".md",
        ".markdown",
        ".html",
        ".htm",
        ".docx",
    },
)


async def run_unsupported_intake_test():
    try:
        await upload_intake.run_upload_intake(
            workspace_id="ws_test",
            file=fake_file,
            dependencies=dependencies,
        )
    except HTTPException as exc:
        return exc

    return None


unsupported_exc = asyncio.run(
    run_unsupported_intake_test()
)

check(
    "UNSUPPORTED_UPLOAD_RAISES_HTTP_400",
    isinstance(unsupported_exc, HTTPException)
    and unsupported_exc.status_code == 400,
)

check(
    "UNSUPPORTED_UPLOAD_ERROR_IS_SANITIZED",
    isinstance(unsupported_exc, HTTPException)
    and str(unsupported_exc.detail).startswith(
        "File type not allowed:"
    ),
)

check(
    "UNSUPPORTED_REJECTED_BEFORE_FILE_READ",
    fake_file.read_calls == 0,
)

check(
    "UNSUPPORTED_REJECTED_BEFORE_WORKSPACE_NORMALIZATION",
    normalize_workspace_id.call_count == 0,
)

check(
    "UNSUPPORTED_REJECTED_BEFORE_PREVIEW",
    extract_preview.call_count == 0,
)

check(
    "UNSUPPORTED_REJECTED_BEFORE_PERSISTENCE",
    store_and_index.call_count == 0,
)

check(
    "UNSUPPORTED_REJECTED_BEFORE_ROLLBACK",
    rollback_committed_upload.call_count == 0,
)


# ------------------------------------------------------------
# D. Invalid / blank filename guard
# ------------------------------------------------------------

print()
print("=== D. INVALID FILENAME GUARD ===")


class BlankUpload:
    def __init__(self, filename):
        self.filename = filename
        self.read_calls = 0

    async def read(self, *args, **kwargs):
        self.read_calls += 1
        return b"unexpected"


async def run_blank_test(filename):
    f = BlankUpload(filename)

    try:
        await upload_intake.run_upload_intake(
            workspace_id="ws_test",
            file=f,
            dependencies=dependencies,
        )
    except HTTPException as exc:
        return f, exc

    return f, None


blank_file, blank_exc = asyncio.run(
    run_blank_test("")
)

check(
    "BLANK_FILENAME_REJECTED_HTTP_400",
    isinstance(blank_exc, HTTPException)
    and blank_exc.status_code == 400,
)

check(
    "BLANK_FILENAME_REJECTED_BEFORE_READ",
    blank_file.read_calls == 0,
)


# ------------------------------------------------------------
# E. Path safety remains upstream
# ------------------------------------------------------------

print()
print("=== E. PATH SAFETY / PHYSICAL SUFFIX ===")

check(
    "SAFE_FILENAME_STRIPS_POSIX_PATH",
    files_route._safe_upload_filename(
        "../../folder/document.md"
    ) == "document.md",
)

check(
    "SAFE_FILENAME_STRIPS_WINDOWS_PATH",
    files_route._safe_upload_filename(
        r"C:\temp\document.htm"
    ) == "document.htm",
)

check(
    "GUESS_EXT_USES_SAFE_FILENAME",
    "_safe_upload_filename"
    in inspect.getsource(
        files_route._guess_ext
    ).lower(),
)

check(
    "FINAL_SUFFIX_USED_AFTER_SANITIZATION",
    files_route._guess_ext(
        "../../folder/document.md.exe"
    ) == ".exe",
)


# ------------------------------------------------------------
# F. MIME / sniffing cannot rescue unsupported extension
# ------------------------------------------------------------

print()
print("=== F. ROUTING AUTHORITY ISOLATION ===")

check(
    "ROUTER_DOES_NOT_USE_MIME",
    "mime" not in router_source,
)

check(
    "ROUTER_DOES_NOT_USE_CONTENT_TYPE",
    "content_type" not in router_source,
)

check(
    "ROUTER_DOES_NOT_READ_FILE_BYTES",
    ".read(" not in router_source
    and "read_bytes" not in router_source,
)

check(
    "ROUTER_DOES_NOT_USE_MAGIC",
    "magic" not in router_source,
)

check(
    "ROUTER_DOES_NOT_USE_SIGNATURE_AUTHORITY",
    "file_signature" not in router_source
    and "content_signature" not in router_source
    and "signature_bytes" not in router_source
    and "detect_signature" not in router_source,
)


# ------------------------------------------------------------
# G. Intake ordering / unrelated pipeline isolation
# ------------------------------------------------------------

print()
print("=== G. GUARD BOUNDARY ISOLATION ===")

extension_pos = intake_source.find(
    "dependencies.guess_extension"
)

gate_pos = intake_source.find(
    "if extension not in allowed_extensions"
)

read_pos = intake_source.find(
    "await file.read(max_upload_bytes + 1)"
)

preview_pos = intake_source.find(
    "dependencies.extract_preview"
)

persist_pos = intake_source.find(
    "dependencies.store_and_index"
)

extractor_pos = intake_source.find(
    "extract_upload_document_v1"
)

check(
    "UNSUPPORTED_GATE_PRECEDES_FILE_READ",
    extension_pos >= 0
    and gate_pos > extension_pos
    and read_pos > gate_pos,
)

check(
    "UNSUPPORTED_GATE_PRECEDES_PREVIEW",
    preview_pos > gate_pos,
)

check(
    "UNSUPPORTED_GATE_PRECEDES_PERSISTENCE",
    persist_pos > gate_pos,
)

check(
    "UNSUPPORTED_GATE_PRECEDES_EXTRACTOR_DISPATCH",
    extractor_pos > gate_pos,
)

combined_source = (
    router_source
    + "\n"
    + intake_source
)

check(
    "NO_WEBSITE_FALLTHROUGH",
    "article_body_cleaning_engine"
    not in combined_source
    and "article_cleaning_pipeline"
    not in combined_source,
)

check(
    "NO_URL_IMPORT_FALLTHROUGH",
    "/api/urls/import"
    not in combined_source,
)

check(
    "NO_DRAFT_IMPORT_FALLTHROUGH",
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
        "U5.11_UNSUPPORTED_INVALID_FORMAT_GUARD: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U5.11 unsupported/invalid format guard verification failed."
    )

print(
    "U5.11_UNSUPPORTED_INVALID_FORMAT_GUARD: CERTIFIED"
)

print(
    "U5.11_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U5.12_ROUTER_EXTRACTOR_RESPONSIBILITY_BOUNDARY_TRANSITION: AUTHORIZED"
)

print(
    "U5.11_FINAL_UNSUPPORTED_GUARD_VERIFICATION: PASS"
)