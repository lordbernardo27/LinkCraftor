from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import HTTPException

from backend.server.routes.files import (
    _guess_ext,
    ALLOWED_EXT,
)

from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake import (
    UploadIntakeDependencies,
    run_upload_intake,
)


class FakeFile:
    def __init__(
        self,
        filename: str,
        content_type: str = "application/octet-stream",
    ):
        self.filename = filename
        self.content_type = content_type
        self.read_called = False

    async def read(self, *args, **kwargs):
        self.read_called = True
        raise AssertionError(
            "file.read() must not run for unsupported format"
        )


def normalize_workspace_id(value: str) -> str:
    return "ws_test"


def forbidden_preview(*args, **kwargs):
    raise AssertionError(
        "preview must not run for unsupported format"
    )


def forbidden_store(*args, **kwargs):
    raise AssertionError(
        "storage must not run for unsupported format"
    )


def forbidden_rollback(*args, **kwargs):
    raise AssertionError(
        "rollback must not run for unsupported format"
    )


def forbidden_workspace_directory(*args, **kwargs):
    raise AssertionError(
        "workspace directory must not be needed for unsupported format"
    )


dependencies = UploadIntakeDependencies(
    guess_extension=_guess_ext,
    normalize_workspace_id=normalize_workspace_id,
    extract_preview=forbidden_preview,
    store_and_index=forbidden_store,
    rollback_committed_upload=forbidden_rollback,
    workspace_directory=forbidden_workspace_directory,
    allowed_extensions=ALLOWED_EXT,
)


async def verify_case(
    filename: str,
    content_type: str,
    expected_detail: str,
):
    fake = FakeFile(
        filename=filename,
        content_type=content_type,
    )

    try:
        await run_upload_intake(
            file=fake,
            workspace_id="test",
            dependencies=dependencies,
        )

    except HTTPException as exc:
        assert exc.status_code == 400, (
            filename,
            exc.status_code,
        )

        assert exc.detail == expected_detail, (
            filename,
            exc.detail,
        )

        assert fake.read_called is False, (
            filename,
            "file.read was called",
        )

        print(
            f"PASS | {filename!r} "
            f"mime={content_type!r} "
            f"-> HTTP {exc.status_code} "
            f"{exc.detail!r}"
        )

        return

    raise AssertionError(
        f"{filename!r} was not rejected"
    )


async def main():
    print(
        "=== U4.14 STEP 2B - INTAKE REJECTION BEHAVIOR ==="
    )

    await verify_case(
        "article.pdf",
        "text/plain",
        "File type not allowed: .pdf",
    )

    await verify_case(
        "article.exe",
        "text/html",
        "File type not allowed: .exe",
    )

    await verify_case(
        "article.zip",
        (
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        "File type not allowed: .zip",
    )

    await verify_case(
        "article.md.exe",
        "text/markdown",
        "File type not allowed: .exe",
    )

    await verify_case(
        "article.docx.zip",
        (
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        "File type not allowed: .zip",
    )

    await verify_case(
        "article.html.pdf",
        "text/html",
        "File type not allowed: .pdf",
    )

    await verify_case(
        "article",
        "text/plain",
        "File type not allowed: ",
    )

    await verify_case(
        "article.",
        "text/plain",
        "File type not allowed: ",
    )

    print()
    print(
        "U4.14_STEP2B_INTAKE_REJECTION_BEHAVIOR: PASS"
    )


asyncio.run(main())