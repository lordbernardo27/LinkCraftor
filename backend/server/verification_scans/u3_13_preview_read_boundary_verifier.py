from __future__ import annotations

import asyncio
import io
import shutil
import tempfile

from pathlib import Path

from fastapi import UploadFile

import backend.server.routes.files as files_route
import backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake as intake_module

from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake import (
    UploadIntakeDependencies,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


class CountingUploadFile(UploadFile):
    def __init__(self, *, filename: str, raw: bytes):
        super().__init__(
            filename=filename,
            file=io.BytesIO(raw),
        )
        self.read_calls = 0

    async def read(self, size: int = -1) -> bytes:
        self.read_calls += 1
        return await super().read(size)


async def main() -> None:
    temp_root = Path(
        tempfile.mkdtemp(
            prefix="linkcraftor_u3_13_preview_"
        )
    )

    docs_root = temp_root / "docs"

    original_data_dir = files_route.DATA_DIR
    original_docs_dir = files_route.DOCS_DIR
    original_extractor = intake_module.extract_upload_document_v1

    preview_calls = []
    extraction_calls = []

    try:
        # ----------------------------------------------------
        # Strict filesystem isolation.
        # ----------------------------------------------------

        files_route.DATA_DIR = temp_root
        files_route.DOCS_DIR = docs_root

        text_limit = int(files_route.TEXT_LIMIT)

        check(
            "TEXT_LIMIT_POSITIVE",
            text_limit > 0,
        )

        marker = "U3_13_CANONICAL_AFTER_PREVIEW_LIMIT"

        prefix = "A" * (text_limit + 100)

        full_text = (
            prefix
            + "\n\n"
            + marker
            + "\n\n"
            + "END_OF_CANONICAL_DOCUMENT"
        )

        raw = full_text.encode("utf-8")

        check(
            "TEST_PAYLOAD_EXCEEDS_PREVIEW_LIMIT",
            len(full_text) > text_limit,
        )

        check(
            "TEST_PAYLOAD_BELOW_UPLOAD_LIMIT",
            len(raw) < intake_module.MAX_UPLOAD_BYTES,
        )

        upload = CountingUploadFile(
            filename="preview-boundary.txt",
            raw=raw,
        )

        def preview_spy(filename, ext, raw_bytes):
            preview_calls.append(
                {
                    "filename": filename,
                    "ext": ext,
                    "raw_len": len(raw_bytes),
                }
            )

            return files_route._extract_preview_from_bytes(
                filename,
                ext,
                raw_bytes,
            )

        def extractor_spy(path):
            extraction_calls.append(
                str(Path(path).resolve())
            )

            return original_extractor(path)

        intake_module.extract_upload_document_v1 = extractor_spy

        deps = UploadIntakeDependencies(
            guess_extension=files_route._guess_ext,
            normalize_workspace_id=files_route._ws,
            extract_preview=preview_spy,
            store_and_index=files_route._store_and_index,
            rollback_committed_upload=files_route._rollback_committed_upload,
            workspace_directory=files_route._ws_dir,
            allowed_extensions=files_route.ALLOWED_EXT,
        )

        result = await intake_module.run_upload_intake(
            workspace_id="ws_u3_13_preview_boundary",
            file=upload,
            dependencies=deps,
        )

        # ----------------------------------------------------
        # Request read contract.
        # ----------------------------------------------------

        check(
            "REQUEST_BODY_READ_EXACTLY_ONCE",
            upload.read_calls == 1,
        )

        # ----------------------------------------------------
        # Preview execution contract.
        # ----------------------------------------------------

        check(
            "PREVIEW_EXECUTED_EXACTLY_ONCE",
            len(preview_calls) == 1,
        )

        check(
            "PREVIEW_RECEIVED_FULL_RAW_BYTES",
            len(preview_calls) == 1
            and preview_calls[0]["raw_len"] == len(raw),
        )

        check(
            "PREVIEW_TRUNCATED_TRUE",
            result.get("truncated") is True,
        )

        preview_text = str(
            result.get("text") or ""
        )

        check(
            "PREVIEW_TEXT_LENGTH_AT_LIMIT",
            len(preview_text) == text_limit,
        )

        check(
            "MARKER_NOT_PRESENT_IN_TRUNCATED_PREVIEW",
            marker not in preview_text,
        )

        # ----------------------------------------------------
        # Persistence contract.
        # ----------------------------------------------------

        doc = result.get("doc") or {}

        stored_name = str(
            doc.get("stored_name") or ""
        ).strip()

        persisted_path = (
            files_route._ws_dir(
                "ws_u3_13_preview_boundary"
            )
            / stored_name
        )

        check(
            "PERSISTED_SOURCE_EXISTS",
            persisted_path.is_file(),
        )

        check(
            "PERSISTED_SOURCE_BYTES_ARE_FULL_AND_EXACT",
            persisted_path.is_file()
            and persisted_path.read_bytes() == raw,
        )

        check(
            "PERSISTED_SOURCE_LONGER_THAN_PREVIEW",
            persisted_path.is_file()
            and len(persisted_path.read_bytes())
            > len(preview_text.encode("utf-8")),
        )

        # ----------------------------------------------------
        # Canonical extraction contract.
        # ----------------------------------------------------

        check(
            "CANONICAL_EXTRACTOR_EXECUTED_EXACTLY_ONCE",
            len(extraction_calls) == 1,
        )

        check(
            "CANONICAL_EXTRACTOR_RECEIVED_PERSISTED_SOURCE",
            len(extraction_calls) == 1
            and extraction_calls[0]
            == str(persisted_path.resolve()),
        )

        extraction = result.get("extraction") or {}

        canonical_text = str(
            extraction.get("text") or ""
        )

        check(
            "CANONICAL_EXTRACTION_STATUS_SUCCESS",
            extraction.get("extraction_status")
            == "success",
        )

        check(
            "MARKER_PRESENT_IN_CANONICAL_EXTRACTION",
            marker in canonical_text,
        )

        check(
            "CANONICAL_EXTRACTION_EXTENDS_BEYOND_PREVIEW",
            len(canonical_text) > len(preview_text),
        )

        # ----------------------------------------------------
        # Critical separation proof.
        # ----------------------------------------------------

        check(
            "PREVIEW_DOES_NOT_BECOME_CANONICAL_CONTENT",
            marker not in preview_text
            and marker in canonical_text,
        )

        check(
            "INTAKE_SUCCESS",
            result.get("ok") is True,
        )

        check(
            "JOB_ID_NONE",
            result.get("job_id") is None,
        )

        check(
            "PROCESSING_STATUS_NOT_APPLICABLE",
            result.get("processing_status")
            == "not_applicable",
        )

    finally:
        intake_module.extract_upload_document_v1 = (
            original_extractor
        )

        files_route.DATA_DIR = original_data_dir
        files_route.DOCS_DIR = original_docs_dir

        temp_prefix = str(
            temp_root.resolve()
        )

        with files_route._INDEX_LOCKS_GUARD:
            stale_keys = [
                key
                for key in files_route._INDEX_LOCKS
                if key.startswith(temp_prefix)
            ]

            for key in stale_keys:
                files_route._INDEX_LOCKS.pop(
                    key,
                    None,
                )

        shutil.rmtree(
            temp_root,
            ignore_errors=True,
        )

    check(
        "TEMP_TEST_ROOT_REMOVED",
        not temp_root.exists(),
    )

    failures = [
        name
        for name, status in results
        if status != "PASS"
    ]

    print()
    print("========================================")

    if failures:
        print(
            "U3.13_PREVIEW_READ_BOUNDARY_VERIFICATION: FAIL"
        )

        print("FAILED_CHECKS:")

        for failure in failures:
            print(f" - {failure}")

        raise RuntimeError(
            "U3.13 preview/read-boundary verification failed."
        )

    print(
        "U3.13_PREVIEW_READ_BOUNDARY_VERIFICATION: PASS"
    )


if __name__ == "__main__":
    asyncio.run(main())