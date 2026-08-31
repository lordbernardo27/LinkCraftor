from __future__ import annotations

import asyncio
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from fastapi import HTTPException

import backend.server.routes.files as files_route
import backend.server.stores.upload_document_extractor as extractor
import backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake as upload_intake


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


print("=== U5.14 - ERROR CONTRACT ===")


intake_source = inspect.getsource(
    upload_intake.run_upload_intake
).lower()

route_source = inspect.getsource(
    files_route.upload_file
).lower()

router_source = inspect.getsource(
    extractor.detect_upload_source_type
).lower()

dispatcher_source = inspect.getsource(
    extractor.extract_upload_document_v1
).lower()


# ------------------------------------------------------------
# A. Intake client-error contracts
# ------------------------------------------------------------

print()
print("=== A. INTAKE CLIENT ERRORS ===")


class FakeUpload:
    def __init__(
        self,
        filename,
        body=b"x",
        content_type="application/octet-stream",
    ):
        self.filename = filename
        self._body = body
        self.content_type = content_type
        self.read_calls = 0

    async def read(self, *args, **kwargs):
        self.read_calls += 1

        limit = args[0] if args else None

        if limit is None:
            return self._body

        return self._body[:limit]


def dependencies(
    *,
    guess_extension=Mock(return_value=".txt"),
    normalize_workspace_id=Mock(return_value="ws_test"),
    extract_preview=Mock(
        return_value={
            "filename": "document.txt",
            "ext": ".txt",
            "text": "hello",
            "html": "",
            "is_html": False,
            "truncated": False,
        }
    ),
    store_and_index=Mock(),
    rollback_committed_upload=Mock(),
    workspace_directory=Mock(return_value=Path(".")),
    allowed_extensions=None,
):
    return upload_intake.UploadIntakeDependencies(
        guess_extension=guess_extension,
        normalize_workspace_id=normalize_workspace_id,
        extract_preview=extract_preview,
        store_and_index=store_and_index,
        rollback_committed_upload=rollback_committed_upload,
        workspace_directory=workspace_directory,
        allowed_extensions=(
            allowed_extensions
            if allowed_extensions is not None
            else {
                ".txt",
                ".md",
                ".markdown",
                ".html",
                ".htm",
                ".docx",
            }
        ),
    )


async def capture_http_error(
    file_obj,
    deps,
    workspace_id="ws_test",
):
    try:
        await upload_intake.run_upload_intake(
            workspace_id=workspace_id,
            file=file_obj,
            dependencies=deps,
        )
    except HTTPException as exc:
        return exc
    except Exception as exc:
        return exc

    return None


blank_file = FakeUpload("")
blank_exc = asyncio.run(
    capture_http_error(
        blank_file,
        dependencies(),
    )
)

check(
    "BLANK_FILENAME_HTTP_400",
    isinstance(blank_exc, HTTPException)
    and blank_exc.status_code == 400,
)

check(
    "BLANK_FILENAME_ERROR_SANITIZED",
    isinstance(blank_exc, HTTPException)
    and blank_exc.detail
    == "Uploaded file must have a filename.",
)


invalid_guess = Mock(
    side_effect=ValueError("internal filename diagnostic")
)

invalid_filename_exc = asyncio.run(
    capture_http_error(
        FakeUpload("../bad?.txt"),
        dependencies(
            guess_extension=invalid_guess,
        ),
    )
)

check(
    "INVALID_FILENAME_HTTP_400",
    isinstance(invalid_filename_exc, HTTPException)
    and invalid_filename_exc.status_code == 400,
)

check(
    "INVALID_FILENAME_INTERNAL_DETAIL_HIDDEN",
    isinstance(invalid_filename_exc, HTTPException)
    and invalid_filename_exc.detail
    == "Uploaded filename is invalid."
    and "internal filename diagnostic"
    not in str(invalid_filename_exc.detail),
)


unsupported_exc = asyncio.run(
    capture_http_error(
        FakeUpload("document.pdf"),
        dependencies(
            guess_extension=Mock(
                return_value=".pdf"
            ),
        ),
    )
)

check(
    "UNSUPPORTED_EXTENSION_HTTP_400",
    isinstance(unsupported_exc, HTTPException)
    and unsupported_exc.status_code == 400,
)

check(
    "UNSUPPORTED_EXTENSION_ERROR_SANITIZED",
    isinstance(unsupported_exc, HTTPException)
    and unsupported_exc.detail
    == "File type not allowed: .pdf",
)


empty_exc = asyncio.run(
    capture_http_error(
        FakeUpload("empty.txt", body=b""),
        dependencies(),
    )
)

check(
    "EMPTY_UPLOAD_HTTP_400",
    isinstance(empty_exc, HTTPException)
    and empty_exc.status_code == 400,
)

check(
    "EMPTY_UPLOAD_ERROR_SANITIZED",
    isinstance(empty_exc, HTTPException)
    and empty_exc.detail
    == "Uploaded file is empty.",
)


invalid_workspace_exc = asyncio.run(
    capture_http_error(
        FakeUpload("document.txt"),
        dependencies(
            normalize_workspace_id=Mock(
                side_effect=ValueError(
                    "internal workspace diagnostic"
                )
            ),
        ),
    )
)

check(
    "INVALID_WORKSPACE_HTTP_400",
    isinstance(invalid_workspace_exc, HTTPException)
    and invalid_workspace_exc.status_code == 400,
)

check(
    "INVALID_WORKSPACE_INTERNAL_DETAIL_HIDDEN",
    isinstance(invalid_workspace_exc, HTTPException)
    and invalid_workspace_exc.detail
    == "workspace_id is invalid."
    and "internal workspace diagnostic"
    not in str(invalid_workspace_exc.detail),
)


# ------------------------------------------------------------
# B. Oversized upload contract
# ------------------------------------------------------------

print()
print("=== B. OVERSIZED UPLOAD CONTRACT ===")


class OversizedUpload:
    filename = "huge.txt"
    content_type = "text/plain"

    def __init__(self):
        self.read_calls = []

    async def read(self, size=-1):
        self.read_calls.append(size)
        return b"x" * (
            upload_intake.MAX_UPLOAD_BYTES + 1
        )


oversized = OversizedUpload()

oversized_exc = asyncio.run(
    capture_http_error(
        oversized,
        dependencies(),
    )
)

check(
    "OVERSIZED_UPLOAD_USES_BOUNDED_READ",
    oversized.read_calls
    == [upload_intake.MAX_UPLOAD_BYTES + 1],
)

check(
    "OVERSIZED_UPLOAD_HTTP_413",
    isinstance(oversized_exc, HTTPException)
    and oversized_exc.status_code == 413,
)

check(
    "OVERSIZED_UPLOAD_ERROR_SANITIZED",
    isinstance(oversized_exc, HTTPException)
    and oversized_exc.detail
    == "Uploaded file exceeds the 250 MB limit.",
)


# ------------------------------------------------------------
# C. Router / dispatcher structured errors
# ------------------------------------------------------------

print()
print("=== C. ROUTER / DISPATCHER ERROR CONTRACT ===")

check(
    "ORDINARY_UNSUPPORTED_ROUTER_RESULT_DOES_NOT_RAISE",
    extractor.detect_upload_source_type(
        "document.pdf"
    )
    == "unsupported",
)

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    unsupported_path = root / "document.pdf"
    unsupported_path.write_text(
        "unsupported",
        encoding="utf-8",
    )

    unsupported_result = (
        extractor.extract_upload_document_v1(
            unsupported_path
        )
    )

    check(
        "DISPATCHER_UNSUPPORTED_RESULT_IS_STRUCTURED",
        unsupported_result.source_type
        == "unsupported"
        and unsupported_result.extraction_status
        == "unsupported_source_type",
    )

    check(
        "DISPATCHER_UNSUPPORTED_ERROR_IS_SANITIZED",
        isinstance(
            unsupported_result.metadata,
            dict,
        )
        and unsupported_result.metadata.get(
            "error"
        )
        == "Unsupported uploaded document type.",
    )

    missing_path = root / "missing.txt"

    missing_result = (
        extractor.extract_txt_upload_v1(
            missing_path
        )
    )

    check(
        "MISSING_FILE_RESULT_IS_STRUCTURED",
        missing_result.source_type == "txt"
        and missing_result.extraction_status
        == "missing_file",
    )


# ------------------------------------------------------------
# D. Extraction failure and compensating rollback
# ------------------------------------------------------------

print()
print("=== D. EXTRACTION FAILURE / ROLLBACK CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)
    stored_path = root / "doc123__document.txt"
    stored_path.write_text(
        "hello",
        encoding="utf-8",
    )

    rollback = Mock()

    failure_dependencies = dependencies(
        extract_preview=Mock(
            return_value={
                "filename": "document.txt",
                "ext": ".txt",
                "text": "hello",
                "html": "",
                "is_html": False,
                "truncated": False,
            }
        ),
        store_and_index=Mock(
            return_value={
                "doc_id": "doc123",
                "stored_name": stored_path.name,
                "filename": "document.txt",
            }
        ),
        rollback_committed_upload=rollback,
        workspace_directory=Mock(
            return_value=root
        ),
    )

    failed_result = (
        extractor.build_empty_upload_result(
            stored_path,
            status="extraction_error",
            confidence=0.0,
        )
    )
    failed_result.metadata["error"] = (
        "controlled extractor failure"
    )

    with patch.object(
        upload_intake,
        "extract_upload_document_v1",
        return_value=failed_result,
    ):
        extraction_failure_exc = asyncio.run(
            capture_http_error(
                FakeUpload(
                    "document.txt",
                    body=b"hello",
                ),
                failure_dependencies,
            )
        )

    check(
        "EXTRACTION_FAILURE_IS_NOT_ROUTER_ERROR",
        isinstance(
            extraction_failure_exc,
            RuntimeError,
        )
        and "canonical uploaded-document extraction failed"
        in str(extraction_failure_exc).lower(),
    )

    check(
        "POST_STORAGE_EXTRACTION_FAILURE_TRIGGERS_ROLLBACK",
        rollback.call_count == 1,
    )

    check(
        "ROLLBACK_RECEIVES_CANONICAL_DOCUMENT_ID",
        rollback.call_args is not None
        and rollback.call_args.args[1]
        == "doc123",
    )

    check(
        "ROLLBACK_RECEIVES_EXPECTED_STORED_NAME",
        rollback.call_args is not None
        and rollback.call_args.kwargs.get(
            "expected_stored_name"
        )
        == stored_path.name,
    )


# ------------------------------------------------------------
# E. Rollback failure contract
# ------------------------------------------------------------

print()
print("=== E. ROLLBACK FAILURE CONTRACT ===")

with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)
    stored_path = root / "doc456__document.txt"
    stored_path.write_text(
        "hello",
        encoding="utf-8",
    )

    rollback_failure_dependencies = dependencies(
        store_and_index=Mock(
            return_value={
                "doc_id": "doc456",
                "stored_name": stored_path.name,
                "filename": "document.txt",
            }
        ),
        rollback_committed_upload=Mock(
            side_effect=RuntimeError(
                "private rollback detail"
            )
        ),
        workspace_directory=Mock(
            return_value=root
        ),
    )

    failed_result = (
        extractor.build_empty_upload_result(
            stored_path,
            status="extraction_error",
            confidence=0.0,
        )
    )

    with patch.object(
        upload_intake,
        "extract_upload_document_v1",
        return_value=failed_result,
    ):
        rollback_failure_exc = asyncio.run(
            capture_http_error(
                FakeUpload(
                    "document.txt",
                    body=b"hello",
                ),
                rollback_failure_dependencies,
            )
        )

    check(
        "ROLLBACK_FAILURE_IS_CONTROLLED_RUNTIMEERROR",
        isinstance(
            rollback_failure_exc,
            RuntimeError,
        )
        and str(rollback_failure_exc)
        == (
            "Upload intake failed after storage commit and "
            "the committed upload could not be rolled back safely."
        ),
    )


# ------------------------------------------------------------
# F. HTTP route error boundary
# ------------------------------------------------------------

print()
print("=== F. HTTP ROUTE ERROR BOUNDARY ===")

check(
    "ROUTE_PRESERVES_HTTP_EXCEPTION",
    "except httpexception:" in route_source
    and "\n        raise" in route_source,
)

check(
    "UNEXPECTED_ERRORS_MAP_TO_HTTP_500",
    "status_code=500" in route_source,
)

check(
    "GENERIC_PUBLIC_500_MESSAGE",
    'detail="upload processing failed."' in route_source,
)

check(
    "TRACEBACK_DIAGNOSTICS_ARE_SERVER_SIDE",
    "traceback.print_exc()" in route_source,
)


# ------------------------------------------------------------
# G. Public response leak prevention
# ------------------------------------------------------------

print()
print("=== G. PUBLIC RESPONSE BOUNDARY ===")

check(
    "PUBLIC_RESPONSE_USES_FIELD_WHITELIST",
    "public_doc_fields" in route_source,
)

check(
    "PUBLIC_RESPONSE_DOES_NOT_RETURN_INTERNAL_RESULT_DIRECTLY",
    "return internal_result"
    not in route_source,
)

check(
    "PUBLIC_RESPONSE_DOES_NOT_EXPOSE_SOURCE_PATH",
    '"source_path"' not in route_source,
)

check(
    "PUBLIC_RESPONSE_DOES_NOT_EXPOSE_EXTRACTION_OBJECT",
    '"extraction"' not in route_source,
)

check(
    "PUBLIC_RESPONSE_DOES_NOT_EXPOSE_UDUC_OBJECT",
    '"uduc"' not in route_source,
)

check(
    "PUBLIC_RESPONSE_DOES_NOT_EXPOSE_TRACEBACK",
    '"traceback"' not in route_source,
)

check(
    "FAILED_PUBLIC_RESPONSE_USES_GENERIC_DETAIL",
    "upload processing did not complete successfully."
    in route_source,
)


# ------------------------------------------------------------
# H. Routing errors stay within upload pipeline
# ------------------------------------------------------------

print()
print("=== H. ERROR ISOLATION ===")

combined_source = (
    router_source
    + "\n"
    + dispatcher_source
    + "\n"
    + intake_source
    + "\n"
    + route_source
)

check(
    "ERRORS_DO_NOT_FALLTHROUGH_TO_WEBSITE",
    "article_body_cleaning_engine"
    not in combined_source
    and "article_cleaning_pipeline"
    not in combined_source,
)

check(
    "ERRORS_DO_NOT_FALLTHROUGH_TO_URL_IMPORT",
    "/api/urls/import"
    not in combined_source,
)

check(
    "ERRORS_DO_NOT_FALLTHROUGH_TO_DRAFT_IMPORT",
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
        "U5.14_ERROR_CONTRACT: FAIL"
    )

    print("FAILED_CHECKS:")

    for failure in failures:
        print(f" - {failure}")

    raise RuntimeError(
        "U5.14 error contract verification failed."
    )

print(
    "U5.14_ERROR_CONTRACT: CERTIFIED"
)

print(
    "U5.14_PRODUCTION_PATCH_REQUIRED: NO"
)

print(
    "U5.15_LEGACY_ROUTING_CLEANUP_TRANSITION: AUTHORIZED"
)

print(
    "U5.14_FINAL_ERROR_CONTRACT_VERIFICATION: PASS"
)