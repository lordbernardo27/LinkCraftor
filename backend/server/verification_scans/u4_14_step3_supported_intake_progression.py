from __future__ import annotations

import asyncio

from backend.server.routes.files import (
    _guess_ext,
    ALLOWED_EXT,
)

from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake import (
    UploadIntakeDependencies,
    run_upload_intake,
)


class ExpectedReadReached(Exception):
    pass


class FakeFile:
    def __init__(self, filename: str):
        self.filename = filename
        self.content_type = "application/octet-stream"
        self.read_called = False

    async def read(self, *args, **kwargs):
        self.read_called = True
        raise ExpectedReadReached(
            "Supported format successfully reached file-read stage."
        )


def normalize_workspace_id(value: str) -> str:
    return "ws_test"


def forbidden_preview(*args, **kwargs):
    raise AssertionError(
        "preview should not be reached in this test"
    )


def forbidden_store(*args, **kwargs):
    raise AssertionError(
        "storage should not be reached in this test"
    )


def forbidden_rollback(*args, **kwargs):
    raise AssertionError(
        "rollback should not be reached in this test"
    )


def forbidden_workspace_directory(*args, **kwargs):
    raise AssertionError(
        "workspace_directory should not be reached in this test"
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


async def verify(filename: str):
    fake = FakeFile(filename)

    try:
        await run_upload_intake(
            file=fake,
            workspace_id="test",
            dependencies=dependencies,
        )

    except ExpectedReadReached:
        assert fake.read_called is True

        ext = _guess_ext(filename)

        assert ext in ALLOWED_EXT, (
            filename,
            ext,
        )

        print(
            f"PASS | {filename!r} "
            f"-> ext={ext!r} "
            f"reached file-read stage"
        )
        return

    raise AssertionError(
        f"{filename!r} did not progress through the format gate"
    )


async def main():
    print(
        "=== U4.14 STEP 3 - SUPPORTED INTAKE PROGRESSION ==="
    )

    cases = [
        "article.txt",
        "article.md",
        "article.markdown",
        "article.html",
        "article.htm",
        "article.docx",

        "ARTICLE.TXT",
        "ARTICLE.MD",
        "ARTICLE.MARKDOWN",
        "ARTICLE.HTML",
        "ARTICLE.HTM",
        "ARTICLE.DOCX",

        "article.MarkDown",
        "article.HtMl",
        "article.DoCx",
    ]

    for filename in cases:
        await verify(filename)

    print()
    print(
        "U4.14_STEP3_SUPPORTED_INTAKE_PROGRESSION: PASS"
    )


asyncio.run(main())