from __future__ import annotations

import asyncio
import io
import json
import shutil
import tempfile

from pathlib import Path

from fastapi import HTTPException, UploadFile

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


def make_upload(filename, raw: bytes) -> UploadFile:
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


async def expect_http_failure(
    *,
    name: str,
    workspace_id: str,
    filename,
    raw: bytes,
    deps: UploadIntakeDependencies,
    expected_status: int,
):
    raised = False
    actual_status = None

    try:
        await intake_module.run_upload_intake(
            workspace_id=workspace_id,
            file=make_upload(filename, raw),
            dependencies=deps,
        )
    except HTTPException as exc:
        raised = True
        actual_status = exc.status_code

    check(
        f"{name}_HTTP_EXCEPTION",
        raised,
    )

    check(
        f"{name}_STATUS_{expected_status}",
        actual_status == expected_status,
    )


async def main() -> None:
    temp_root = Path(
        tempfile.mkdtemp(
            prefix="linkcraftor_u3_13_failure_"
        )
    )

    docs_root = temp_root / "docs"

    original_data_dir = files_route.DATA_DIR
    original_docs_dir = files_route.DOCS_DIR
    original_max_upload_bytes = intake_module.MAX_UPLOAD_BYTES

    try:
        files_route.DATA_DIR = temp_root
        files_route.DOCS_DIR = docs_root

        store_calls = []
        rollback_calls = []

        def store_spy(*args, **kwargs):
            store_calls.append(
                {
                    "args": args,
                    "kwargs": kwargs,
                }
            )

            return files_route._store_and_index(
                *args,
                **kwargs,
            )

        def rollback_spy(
            workspace_id,
            document_id,
            *,
            expected_stored_name,
        ):
            rollback_calls.append(
                {
                    "workspace_id": workspace_id,
                    "document_id": document_id,
                    "stored_name": expected_stored_name,
                }
            )

            return files_route._rollback_committed_upload(
                workspace_id,
                document_id,
                expected_stored_name=expected_stored_name,
            )

        deps = UploadIntakeDependencies(
            guess_extension=files_route._guess_ext,
            normalize_workspace_id=files_route._ws,
            extract_preview=files_route._extract_preview_from_bytes,
            store_and_index=store_spy,
            rollback_committed_upload=rollback_spy,
            workspace_directory=files_route._ws_dir,
            allowed_extensions=files_route.ALLOWED_EXT,
        )

        # ----------------------------------------------------
        # TEST 1
        # Real production upload limit configuration.
        # ----------------------------------------------------

        check(
            "CANONICAL_UPLOAD_LIMIT_IS_250_MIB",
            original_max_upload_bytes
            == 250 * 1024 * 1024,
        )

        # ----------------------------------------------------
        # TEST 2
        # Blank filename must fail before persistence.
        # ----------------------------------------------------

        before_store = len(store_calls)
        before_rollback = len(rollback_calls)

        await expect_http_failure(
            name="BLANK_FILENAME",
            workspace_id="ws_u3_13_blank_filename",
            filename="",
            raw=b"content",
            deps=deps,
            expected_status=400,
        )

        check(
            "BLANK_FILENAME_NO_STORAGE",
            len(store_calls) == before_store,
        )

        check(
            "BLANK_FILENAME_NO_ROLLBACK",
            len(rollback_calls) == before_rollback,
        )

        # ----------------------------------------------------
        # TEST 3
        # Unsupported extension before persistence.
        # ----------------------------------------------------

        before_store = len(store_calls)
        before_rollback = len(rollback_calls)

        await expect_http_failure(
            name="UNSUPPORTED_EXTENSION",
            workspace_id="ws_u3_13_bad_ext",
            filename="malware.exe",
            raw=b"not allowed",
            deps=deps,
            expected_status=400,
        )

        check(
            "UNSUPPORTED_EXTENSION_NO_STORAGE",
            len(store_calls) == before_store,
        )

        check(
            "UNSUPPORTED_EXTENSION_NO_ROLLBACK",
            len(rollback_calls) == before_rollback,
        )

        # ----------------------------------------------------
        # TEST 4
        # Zero-byte upload before persistence.
        # ----------------------------------------------------

        before_store = len(store_calls)
        before_rollback = len(rollback_calls)

        await expect_http_failure(
            name="ZERO_BYTE_UPLOAD",
            workspace_id="ws_u3_13_zero",
            filename="empty.txt",
            raw=b"",
            deps=deps,
            expected_status=400,
        )

        check(
            "ZERO_BYTE_NO_STORAGE",
            len(store_calls) == before_store,
        )

        check(
            "ZERO_BYTE_NO_ROLLBACK",
            len(rollback_calls) == before_rollback,
        )

        # ----------------------------------------------------
        # TEST 5
        # Oversize branch.
        #
        # Do not allocate 250 MiB. Temporarily reduce only the
        # verifier-process constant after proving production's
        # configured value above.
        # ----------------------------------------------------

        intake_module.MAX_UPLOAD_BYTES = 16

        before_store = len(store_calls)
        before_rollback = len(rollback_calls)

        await expect_http_failure(
            name="OVERSIZED_UPLOAD",
            workspace_id="ws_u3_13_oversize",
            filename="too-large.txt",
            raw=b"x" * 17,
            deps=deps,
            expected_status=413,
        )

        check(
            "OVERSIZED_UPLOAD_NO_STORAGE",
            len(store_calls) == before_store,
        )

        check(
            "OVERSIZED_UPLOAD_NO_ROLLBACK",
            len(rollback_calls) == before_rollback,
        )

        intake_module.MAX_UPLOAD_BYTES = original_max_upload_bytes

        # ----------------------------------------------------
        # TEST 6
        # Workspace normalization rejection.
        #
        # Use the actual route normalizer. Test blank and an
        # unsafe traversal-shaped value independently.
        # ----------------------------------------------------

        workspace_cases = [
            ("BLANK_WORKSPACE", ""),
            ("INVALID_WORKSPACE", "..."),
        ]

        for label, workspace_value in workspace_cases:
            before_store = len(store_calls)
            before_rollback = len(rollback_calls)

            raised = False
            status_code = None

            try:
                await intake_module.run_upload_intake(
                    workspace_id=workspace_value,
                    file=make_upload(
                        "workspace.txt",
                        b"workspace validation",
                    ),
                    dependencies=deps,
                )
            except HTTPException as exc:
                raised = True
                status_code = exc.status_code

            check(
                f"{label}_REJECTED",
                raised,
            )

            check(
                f"{label}_STATUS_400",
                status_code == 400,
            )

            check(
                f"{label}_NO_STORAGE",
                len(store_calls) == before_store,
            )

            check(
                f"{label}_NO_ROLLBACK",
                len(rollback_calls) == before_rollback,
            )

        # Traversal-shaped workspace input is intentionally
        # sanitized into a canonical safe workspace ID.
        traversal_result = await intake_module.run_upload_intake(
            workspace_id="../unsafe",
            file=make_upload(
                "workspace-sanitized.txt",
                b"workspace canonicalization",
            ),
            dependencies=deps,
        )

        check(
            "TRAVERSAL_WORKSPACE_SANITIZED",
            traversal_result.get("workspace_id") == "ws_unsafe",
        )

        check(
            "TRAVERSAL_WORKSPACE_INTAKE_OK",
            traversal_result.get("ok") is True,
        )

        traversal_doc = traversal_result.get("doc") or {}
        traversal_stored_name = str(
            traversal_doc.get("stored_name") or ""
        ).strip()

        traversal_path = (
            files_route._ws_dir("ws_unsafe")
            / traversal_stored_name
        )

        check(
            "TRAVERSAL_WORKSPACE_SOURCE_INSIDE_CANONICAL_DIRECTORY",
            traversal_path.is_file()
            and traversal_path.parent
            == files_route._ws_dir("ws_unsafe"),
        )

        # ----------------------------------------------------
        # TEST 7
        # Force canonical extraction failure AFTER source/index
        # commit. Must compensate with document-scoped rollback.
        # ----------------------------------------------------

        failure_workspace = "ws_u3_13_extraction_failure"

        original_extractor = intake_module.extract_upload_document_v1

        class SyntheticExtractionFailure:
            extraction_status = "synthetic_failure"
            metadata = {
                "error": "synthetic extractor failure"
            }

        def failing_extractor(path):
            return SyntheticExtractionFailure()

        intake_module.extract_upload_document_v1 = failing_extractor

        before_store = len(store_calls)
        before_rollback = len(rollback_calls)

        failure_raised = False

        try:
            await intake_module.run_upload_intake(
                workspace_id=failure_workspace,
                file=make_upload(
                    "rollback.txt",
                    b"source must be rolled back",
                ),
                dependencies=deps,
            )
        except RuntimeError as exc:
            failure_raised = (
                "Canonical uploaded-document extraction failed"
                in str(exc)
                and "synthetic_failure" in str(exc)
            )
        finally:
            intake_module.extract_upload_document_v1 = (
                original_extractor
            )

        check(
            "EXTRACTION_FAILURE_PROPAGATES",
            failure_raised,
        )

        check(
            "EXTRACTION_FAILURE_STORAGE_COMMITTED_ONCE",
            len(store_calls) == before_store + 1,
        )

        check(
            "EXTRACTION_FAILURE_ROLLBACK_CALLED_ONCE",
            len(rollback_calls) == before_rollback + 1,
        )

        failure_ws_dir = files_route._ws_dir(
            failure_workspace
        )

        failure_index = failure_ws_dir / "index.json"

        failure_rows = []

        if failure_index.is_file():
            raw_index = json.loads(
                failure_index.read_text(
                    encoding="utf-8"
                )
            )

            failure_rows = normalize_index_rows(
                raw_index
            )

        check(
            "EXTRACTION_FAILURE_REGISTRY_RECORD_REMOVED",
            len(failure_rows) == 0,
        )

        remaining_source_files = []

        if failure_ws_dir.exists():
            remaining_source_files = [
                p
                for p in failure_ws_dir.iterdir()
                if p.is_file()
                and p.name != "index.json"
                and not p.name.endswith(".tmp")
            ]

        check(
            "EXTRACTION_FAILURE_SOURCE_REMOVED",
            len(remaining_source_files) == 0,
        )

        # ----------------------------------------------------
        # TEST 8
        # Successful intake must never invoke rollback.
        # ----------------------------------------------------

        success_workspace = "ws_u3_13_success_control"

        before_rollback = len(rollback_calls)

        success_result = await intake_module.run_upload_intake(
            workspace_id=success_workspace,
            file=make_upload(
                "success.txt",
                b"successful canonical intake",
            ),
            dependencies=deps,
        )

        check(
            "SUCCESS_CONTROL_OK",
            success_result.get("ok") is True,
        )

        check(
            "SUCCESS_CONTROL_NO_ROLLBACK",
            len(rollback_calls) == before_rollback,
        )

        check(
            "SUCCESS_CONTROL_JOB_ID_NONE",
            success_result.get("job_id") is None,
        )

        check(
            "SUCCESS_CONTROL_PROCESSING_NOT_APPLICABLE",
            success_result.get("processing_status")
            == "not_applicable",
        )

    finally:
        intake_module.MAX_UPLOAD_BYTES = (
            original_max_upload_bytes
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

    check(
        "UPLOAD_LIMIT_RESTORED",
        intake_module.MAX_UPLOAD_BYTES
        == 250 * 1024 * 1024,
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
            "U3.13_INTAKE_FAILURE_ROLLBACK_VERIFICATION: FAIL"
        )

        print("FAILED_CHECKS:")

        for failure in failures:
            print(f" - {failure}")

        raise RuntimeError(
            "U3.13 failure/rollback verification failed."
        )

    print(
        "U3.13_INTAKE_FAILURE_ROLLBACK_VERIFICATION: PASS"
    )


if __name__ == "__main__":
    asyncio.run(main())