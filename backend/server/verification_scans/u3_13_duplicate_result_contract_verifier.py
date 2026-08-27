from __future__ import annotations

import asyncio
import io
import json
import shutil
import tempfile

from pathlib import Path

from fastapi import UploadFile

import backend.server.routes.files as files_route

from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake import (
    UploadIntakeDependencies,
    run_upload_intake,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def make_upload(filename: str, raw: bytes) -> UploadFile:
    return UploadFile(
        filename=filename,
        file=io.BytesIO(raw),
    )


def normalize_index_rows(payload):
    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):
        items = payload.get("items")

        if isinstance(items, list):
            return items

    return []


async def main() -> None:
    temp_root = Path(
        tempfile.mkdtemp(
            prefix="linkcraftor_u3_13_duplicate_"
        )
    )

    docs_root = temp_root / "docs"

    original_data_dir = files_route.DATA_DIR
    original_docs_dir = files_route.DOCS_DIR

    try:
        files_route.DATA_DIR = temp_root
        files_route.DOCS_DIR = docs_root

        deps = UploadIntakeDependencies(
            guess_extension=files_route._guess_ext,
            normalize_workspace_id=files_route._ws,
            extract_preview=files_route._extract_preview_from_bytes,
            store_and_index=files_route._store_and_index,
            rollback_committed_upload=files_route._rollback_committed_upload,
            workspace_directory=files_route._ws_dir,
            allowed_extensions=files_route.ALLOWED_EXT,
        )

        workspace_id = "ws_u3_13_duplicate"
        filename = "same-document.txt"
        raw = (
            b"Identical source bytes for duplicate-create verification.\n"
            b"Each request must create a fresh canonical document identity."
        )

        first = await run_upload_intake(
            workspace_id=workspace_id,
            file=make_upload(filename, raw),
            dependencies=deps,
        )

        second = await run_upload_intake(
            workspace_id=workspace_id,
            file=make_upload(filename, raw),
            dependencies=deps,
        )

        required_result_keys = {
            "ok",
            "workspace_id",
            "doc",
            "extraction",
            "filename",
            "ext",
            "text",
            "html",
            "is_html",
            "truncated",
            "job_id",
            "processing_status",
            "pipeline",
            "pipeline_stage",
        }

        for label, result in (
            ("FIRST", first),
            ("SECOND", second),
        ):
            check(
                f"{label}_RESULT_IS_DICT",
                isinstance(result, dict),
            )

            check(
                f"{label}_RESULT_CONTRACT_COMPLETE",
                required_result_keys.issubset(
                    result.keys()
                ),
            )

            check(
                f"{label}_OK_TRUE",
                result.get("ok") is True,
            )

            check(
                f"{label}_WORKSPACE_CANONICAL",
                result.get("workspace_id")
                == "ws_u3_13_duplicate",
            )

            check(
                f"{label}_FILENAME_PRESERVED",
                result.get("filename") == filename,
            )

            check(
                f"{label}_EXT_TXT",
                result.get("ext") == ".txt",
            )

            check(
                f"{label}_JOB_ID_NONE",
                result.get("job_id") is None,
            )

            check(
                f"{label}_PROCESSING_STATUS_NOT_APPLICABLE",
                result.get("processing_status")
                == "not_applicable",
            )

            check(
                f"{label}_PIPELINE_NAME",
                result.get("pipeline")
                == "uploaded_document_to_uduc_pipeline",
            )

            check(
                f"{label}_PIPELINE_STAGE",
                result.get("pipeline_stage")
                == "upload_intake",
            )

            extraction = result.get("extraction") or {}

            check(
                f"{label}_EXTRACTION_SUCCESS",
                extraction.get("extraction_status")
                == "success",
            )

        first_doc = first.get("doc") or {}
        second_doc = second.get("doc") or {}

        first_id = str(
            first_doc.get("doc_id")
            or first_doc.get("document_id")
            or ""
        ).strip()

        second_id = str(
            second_doc.get("doc_id")
            or second_doc.get("document_id")
            or ""
        ).strip()

        first_stored = str(
            first_doc.get("stored_name") or ""
        ).strip()

        second_stored = str(
            second_doc.get("stored_name") or ""
        ).strip()

        check(
            "FIRST_DOCUMENT_ID_CREATED",
            bool(first_id),
        )

        check(
            "SECOND_DOCUMENT_ID_CREATED",
            bool(second_id),
        )

        check(
            "IDENTICAL_UPLOAD_CREATES_FRESH_DOCUMENT_ID",
            bool(first_id)
            and bool(second_id)
            and first_id != second_id,
        )

        check(
            "IDENTICAL_UPLOAD_CREATES_FRESH_STORED_NAME",
            bool(first_stored)
            and bool(second_stored)
            and first_stored != second_stored,
        )

        ws_dir = files_route._ws_dir(
            workspace_id
        )

        first_path = ws_dir / first_stored
        second_path = ws_dir / second_stored

        check(
            "FIRST_SOURCE_EXISTS",
            first_path.is_file(),
        )

        check(
            "SECOND_SOURCE_EXISTS",
            second_path.is_file(),
        )

        check(
            "FIRST_SOURCE_BYTES_EXACT",
            first_path.is_file()
            and first_path.read_bytes() == raw,
        )

        check(
            "SECOND_SOURCE_BYTES_EXACT",
            second_path.is_file()
            and second_path.read_bytes() == raw,
        )

        index_path = ws_dir / "index.json"

        rows = []

        if index_path.is_file():
            payload = json.loads(
                index_path.read_text(
                    encoding="utf-8"
                )
            )

            rows = normalize_index_rows(
                payload
            )

        matching = [
            row
            for row in rows
            if isinstance(row, dict)
            and row.get("doc_id")
            in {first_id, second_id}
        ]

        matching_ids = {
            row.get("doc_id")
            for row in matching
        }

        check(
            "REGISTRY_CONTAINS_TWO_DISTINCT_DOCUMENTS",
            len(matching) == 2
            and matching_ids
            == {first_id, second_id},
        )

    finally:
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
            "U3.13_DUPLICATE_RESULT_CONTRACT_VERIFICATION: FAIL"
        )

        print("FAILED_CHECKS:")

        for failure in failures:
            print(f" - {failure}")

        raise RuntimeError(
            "U3.13 duplicate/result-contract verification failed."
        )

    print(
        "U3.13_DUPLICATE_RESULT_CONTRACT_VERIFICATION: PASS"
    )


if __name__ == "__main__":
    asyncio.run(main())