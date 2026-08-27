from __future__ import annotations

import asyncio
import io
import json
import shutil
import tempfile

from pathlib import Path

from fastapi import UploadFile

import backend.server.routes.files as files_route
import backend.server.pipelines.upload_document.coordinator as upload_coordinator

from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake import (
    UploadIntakeDependencies,
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
            prefix="linkcraftor_u3_13_uduc_failure_"
        )
    )

    docs_root = temp_root / "docs"

    original_data_dir = files_route.DATA_DIR
    original_docs_dir = files_route.DOCS_DIR

    original_uduc_builder = (
        upload_coordinator.build_and_write_uduc_from_extraction_result
    )

    original_highlight = (
        upload_coordinator.run_uploaded_document_to_highlight_pipeline
    )

    original_active_target = (
        upload_coordinator
        .run_uploaded_document_registry_to_active_target_set_pipeline
    )

    rollback_calls = []
    uduc_calls = []
    highlight_calls = []
    active_target_calls = []

    try:
        # ----------------------------------------------------
        # Strict isolation.
        # ----------------------------------------------------

        files_route.DATA_DIR = temp_root
        files_route.DOCS_DIR = docs_root

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
            store_and_index=files_route._store_and_index,
            rollback_committed_upload=rollback_spy,
            workspace_directory=files_route._ws_dir,
            allowed_extensions=files_route.ALLOWED_EXT,
        )

        # ----------------------------------------------------
        # Force failure only AFTER intake succeeds.
        # ----------------------------------------------------

        def failing_uduc_builder(**kwargs):
            uduc_calls.append(kwargs)

            return {
                "ok": False,
                "status": "synthetic_uduc_failure",
            }

        def highlight_spy(**kwargs):
            highlight_calls.append(kwargs)

            return {
                "ok": True,
            }

        def active_target_spy(**kwargs):
            active_target_calls.append(kwargs)

            return {
                "ok": True,
            }

        upload_coordinator.build_and_write_uduc_from_extraction_result = (
            failing_uduc_builder
        )

        upload_coordinator.run_uploaded_document_to_highlight_pipeline = (
            highlight_spy
        )

        upload_coordinator.run_uploaded_document_registry_to_active_target_set_pipeline = (
            active_target_spy
        )

        workspace_id = "ws_u3_13_post_intake_uduc_failure"

        raw = (
            b"U3.13 post-intake UDUC failure preservation test.\n"
            b"The source and registry must remain committed."
        )

        raised_expected_failure = False

        try:
            await upload_coordinator.run_upload_document(
                workspace_id=workspace_id,
                file=make_upload(
                    "post-intake-failure.txt",
                    raw,
                ),
                dependencies=deps,
            )
        except RuntimeError as exc:
            raised_expected_failure = (
                "UDUC builder/writer did not complete successfully"
                in str(exc)
            )

        check(
            "UDUC_FAILURE_PROPAGATES",
            raised_expected_failure,
        )

        check(
            "UDUC_BUILDER_CALLED_EXACTLY_ONCE",
            len(uduc_calls) == 1,
        )

        # ----------------------------------------------------
        # Intake rollback MUST NOT run here.
        #
        # The upload intake itself succeeded. Failure happened
        # later in downstream UDUC construction.
        # ----------------------------------------------------

        check(
            "POST_INTAKE_FAILURE_DOES_NOT_CALL_INTAKE_ROLLBACK",
            len(rollback_calls) == 0,
        )

        # ----------------------------------------------------
        # Since UDUC failed first, later independent branches
        # must not execute.
        # ----------------------------------------------------

        check(
            "HIGHLIGHT_NOT_EXECUTED_AFTER_UDUC_FAILURE",
            len(highlight_calls) == 0,
        )

        check(
            "ACTIVE_TARGET_SET_NOT_EXECUTED_AFTER_UDUC_FAILURE",
            len(active_target_calls) == 0,
        )

        # ----------------------------------------------------
        # Prove committed registry remains.
        # ----------------------------------------------------

        ws_dir = files_route._ws_dir(
            workspace_id
        )

        index_path = ws_dir / "index.json"

        check(
            "REGISTRY_FILE_REMAINS",
            index_path.is_file(),
        )

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

        check(
            "REGISTRY_RETAINS_EXACTLY_ONE_COMMITTED_DOCUMENT",
            len(rows) == 1,
        )

        document_id = ""

        stored_name = ""

        if len(rows) == 1:
            document_id = str(
                rows[0].get("doc_id")
                or rows[0].get("document_id")
                or ""
            ).strip()

            stored_name = str(
                rows[0].get("stored_name")
                or ""
            ).strip()

        check(
            "COMMITTED_DOCUMENT_ID_REMAINS",
            bool(document_id),
        )

        check(
            "COMMITTED_STORED_NAME_REMAINS",
            bool(stored_name),
        )

        # ----------------------------------------------------
        # Prove committed immutable source remains byte-exact.
        # ----------------------------------------------------

        stored_path = ws_dir / stored_name

        check(
            "COMMITTED_SOURCE_REMAINS",
            bool(stored_name)
            and stored_path.is_file(),
        )

        check(
            "COMMITTED_SOURCE_BYTES_REMAIN_EXACT",
            bool(stored_name)
            and stored_path.is_file()
            and stored_path.read_bytes() == raw,
        )

        # ----------------------------------------------------
        # Prove UDUC handoff received canonical intake identity
        # and extraction rather than preview-derived content.
        # ----------------------------------------------------

        if len(uduc_calls) == 1:
            call = uduc_calls[0]

            extraction_result = (
                call.get("extraction_result") or {}
            )

            check(
                "UDUC_HANDOFF_DOCUMENT_ID_MATCHES_REGISTRY",
                call.get("document_id")
                == document_id,
            )

            check(
                "UDUC_HANDOFF_WORKSPACE_MATCHES",
                call.get("workspace_id")
                == "ws_u3_13_post_intake_uduc_failure",
            )

            check(
                "UDUC_HANDOFF_EXTRACTION_SUCCESS",
                extraction_result.get("extraction_status")
                == "success",
            )

            check(
                "UDUC_HANDOFF_CONTAINS_CANONICAL_TEXT",
                "UDUC failure preservation test"
                in str(
                    extraction_result.get("text") or ""
                ),
            )
        else:
            check(
                "UDUC_HANDOFF_DOCUMENT_ID_MATCHES_REGISTRY",
                False,
            )

            check(
                "UDUC_HANDOFF_WORKSPACE_MATCHES",
                False,
            )

            check(
                "UDUC_HANDOFF_EXTRACTION_SUCCESS",
                False,
            )

            check(
                "UDUC_HANDOFF_CONTAINS_CANONICAL_TEXT",
                False,
            )

    finally:
        upload_coordinator.build_and_write_uduc_from_extraction_result = (
            original_uduc_builder
        )

        upload_coordinator.run_uploaded_document_to_highlight_pipeline = (
            original_highlight
        )

        upload_coordinator.run_uploaded_document_registry_to_active_target_set_pipeline = (
            original_active_target
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
        "UDUC_BUILDER_RESTORED",
        upload_coordinator.build_and_write_uduc_from_extraction_result
        is original_uduc_builder,
    )

    check(
        "HIGHLIGHT_FUNCTION_RESTORED",
        upload_coordinator.run_uploaded_document_to_highlight_pipeline
        is original_highlight,
    )

    check(
        "ACTIVE_TARGET_FUNCTION_RESTORED",
        upload_coordinator.run_uploaded_document_registry_to_active_target_set_pipeline
        is original_active_target,
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
            "U3.13_POST_INTAKE_UDUC_FAILURE_VERIFICATION: FAIL"
        )

        print("FAILED_CHECKS:")

        for failure in failures:
            print(f" - {failure}")

        raise RuntimeError(
            "U3.13 post-intake UDUC failure verification failed."
        )

    print(
        "U3.13_POST_INTAKE_UDUC_FAILURE_VERIFICATION: PASS"
    )


if __name__ == "__main__":
    asyncio.run(main())