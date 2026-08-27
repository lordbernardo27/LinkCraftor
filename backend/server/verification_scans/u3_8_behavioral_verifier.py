from __future__ import annotations

import asyncio
import io
import json
import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace

from fastapi import UploadFile

import backend.server.routes.files as files_route
import backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake as intake_module
from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake import (
    UploadIntakeDependencies,
    run_upload_intake,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def make_upload(name: str, data: bytes) -> UploadFile:
    return UploadFile(
        filename=name,
        file=io.BytesIO(data),
    )


def fake_preview(filename: str, ext: str, raw: bytes):
    text = raw.decode("utf-8", errors="ignore")
    return {
        "filename": filename,
        "ext": ext,
        "text": text,
        "html": "",
        "is_html": False,
        "truncated": False,
    }


def successful_extractor(path: Path):
    return SimpleNamespace(
        extraction_status="success",
        metadata={},
    )


def successful_serializer(result):
    return {
        "extraction_status": "success",
        "metadata": {},
    }


async def main() -> None:
    root = Path(
        tempfile.mkdtemp(prefix="linkcraftor_u3_8_")
    )

    original_data_dir = files_route.DATA_DIR
    original_extractor = intake_module.extract_upload_document_v1
    original_serializer = (
        intake_module.serialize_upload_extraction_result
    )

    try:
        files_route.DATA_DIR = root

        intake_module.extract_upload_document_v1 = (
            successful_extractor
        )
        intake_module.serialize_upload_extraction_result = (
            successful_serializer
        )

        workspace_id = "ws_u3_8_test"

        deps = UploadIntakeDependencies(
            guess_extension=files_route._guess_ext,
            normalize_workspace_id=files_route._ws,
            extract_preview=fake_preview,
            store_and_index=files_route._store_and_index,
            rollback_committed_upload=(
                files_route._rollback_committed_upload
            ),
            workspace_directory=files_route._ws_dir,
            allowed_extensions=files_route.ALLOWED_EXT,
        )

        # ----------------------------------------------------
        # TEST 1:
        # Exact same filename + exact same content twice.
        # ----------------------------------------------------

        payload = b"identical uploaded document"

        first = await run_upload_intake(
            workspace_id=workspace_id,
            file=make_upload("same.txt", payload),
            dependencies=deps,
        )

        second = await run_upload_intake(
            workspace_id=workspace_id,
            file=make_upload("same.txt", payload),
            dependencies=deps,
        )

        first_doc = first.get("doc") or {}
        second_doc = second.get("doc") or {}

        first_id = str(
            first_doc.get("doc_id") or ""
        )
        second_id = str(
            second_doc.get("doc_id") or ""
        )

        first_name = str(
            first_doc.get("stored_name") or ""
        )
        second_name = str(
            second_doc.get("stored_name") or ""
        )

        check(
            "IDENTICAL_UPLOAD_1_SUCCESS",
            first.get("ok") is True,
        )

        check(
            "IDENTICAL_UPLOAD_2_SUCCESS",
            second.get("ok") is True,
        )

        check(
            "REPEATED_SUCCESS_GETS_FRESH_DOCUMENT_ID",
            bool(first_id)
            and bool(second_id)
            and first_id != second_id,
        )

        check(
            "REPEATED_SUCCESS_GETS_FRESH_STORED_NAME",
            bool(first_name)
            and bool(second_name)
            and first_name != second_name,
        )

        check(
            "STORED_NAME_1_IS_DOCUMENT_SCOPED",
            first_name.startswith(first_id + "__"),
        )

        check(
            "STORED_NAME_2_IS_DOCUMENT_SCOPED",
            second_name.startswith(second_id + "__"),
        )

        ws_dir = files_route._ws_dir(workspace_id)

        check(
            "FIRST_SOURCE_PRESERVED",
            (ws_dir / first_name).is_file(),
        )

        check(
            "SECOND_SOURCE_PRESERVED",
            (ws_dir / second_name).is_file(),
        )

        index_path = files_route._index_path(
            workspace_id
        )

        records = json.loads(
            index_path.read_text(encoding="utf-8")
        )

        ids = [
            str(item.get("doc_id") or "")
            for item in records
        ]

        check(
            "FIRST_REGISTRY_RECORD_PRESERVED",
            ids.count(first_id) == 1,
        )

        check(
            "SECOND_REGISTRY_RECORD_PRESERVED",
            ids.count(second_id) == 1,
        )

        check(
            "EXACTLY_TWO_SUCCESSFUL_RECORDS",
            len(records) == 2,
        )

        # ----------------------------------------------------
        # TEST 2:
        # Same filename, different content remains independent.
        # ----------------------------------------------------

        third = await run_upload_intake(
            workspace_id=workspace_id,
            file=make_upload(
                "same.txt",
                b"different document bytes",
            ),
            dependencies=deps,
        )

        third_doc = third.get("doc") or {}
        third_id = str(
            third_doc.get("doc_id") or ""
        )
        third_name = str(
            third_doc.get("stored_name") or ""
        )

        check(
            "SAME_FILENAME_DIFFERENT_CONTENT_FRESH_ID",
            bool(third_id)
            and third_id not in {first_id, second_id},
        )

        check(
            "SAME_FILENAME_DIFFERENT_CONTENT_FRESH_STORAGE",
            bool(third_name)
            and third_name not in {
                first_name,
                second_name,
            },
        )

        final_records = json.loads(
            index_path.read_text(encoding="utf-8")
        )

        check(
            "THREE_CREATION_REQUESTS_THREE_RECORDS",
            len(final_records) == 3,
        )

        # ----------------------------------------------------
        # TEST 3:
        # Repeated failures do not accumulate registry/source
        # artifacts after U3.7 compensation.
        # ----------------------------------------------------

        def failed_extractor(path: Path):
            return SimpleNamespace(
                extraction_status="extraction_error",
                metadata={
                    "error": "forced repeated failure"
                },
            )

        intake_module.extract_upload_document_v1 = (
            failed_extractor
        )

        before_failure_records = json.loads(
            index_path.read_text(encoding="utf-8")
        )

        before_sources = {
            p.name
            for p in ws_dir.iterdir()
            if p.is_file()
            and p.name != "index.json"
        }

        failure_count = 0

        for _ in range(2):
            try:
                await run_upload_intake(
                    workspace_id=workspace_id,
                    file=make_upload(
                        "failed-retry.txt",
                        b"same failing payload",
                    ),
                    dependencies=deps,
                )
            except RuntimeError:
                failure_count += 1

        after_failure_records = json.loads(
            index_path.read_text(encoding="utf-8")
        )

        after_sources = {
            p.name
            for p in ws_dir.iterdir()
            if p.is_file()
            and p.name != "index.json"
        }

        check(
            "REPEATED_FAILURES_BOTH_RAISE",
            failure_count == 2,
        )

        check(
            "REPEATED_FAILURES_NO_REGISTRY_ACCUMULATION",
            after_failure_records
            == before_failure_records,
        )

        check(
            "REPEATED_FAILURES_NO_SOURCE_ACCUMULATION",
            after_sources == before_sources,
        )

        # ----------------------------------------------------
        # TEST 4:
        # Rollback retry remains idempotent.
        # ----------------------------------------------------

        files_route._rollback_committed_upload(
            workspace_id,
            third_id,
            expected_stored_name=third_name,
        )

        files_route._rollback_committed_upload(
            workspace_id,
            third_id,
            expected_stored_name=third_name,
        )

        check(
            "ROLLBACK_RETRY_REMAINS_IDEMPOTENT",
            not (ws_dir / third_name).exists(),
        )

    finally:
        intake_module.extract_upload_document_v1 = (
            original_extractor
        )
        intake_module.serialize_upload_extraction_result = (
            original_serializer
        )

        files_route.DATA_DIR = original_data_dir
        shutil.rmtree(root, ignore_errors=True)

    failures = [
        name
        for name, status in results
        if status != "PASS"
    ]

    print()
    print("========================================")

    if failures:
        print("U3.8_BEHAVIORAL_VERIFICATION: FAIL")
        print("FAILED_CHECKS:")
        for failure in failures:
            print(f" - {failure}")
        raise SystemExit(1)

    print("U3.8_BEHAVIORAL_VERIFICATION: PASS")


if __name__ == "__main__":
    asyncio.run(main())