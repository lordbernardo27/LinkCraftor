from __future__ import annotations

import asyncio
import io
import json
import shutil
import tempfile

from pathlib import Path

from fastapi import UploadFile

import backend.server.routes.files as files_route
import backend.server.stores.uploaded_document_unified_content as uduc_store
import backend.server.pipelines.upload_document.coordinator as coordinator

from backend.server.pipelines.upload_document.uploaded_document_to_uduc_pipeline.upload_intake import (
    UploadIntakeDependencies,
)


results = []


def check(name: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{name}: {status}")


def make_upload(name: str, raw: bytes) -> UploadFile:
    return UploadFile(
        filename=name,
        file=io.BytesIO(raw),
    )


async def main() -> None:
    temp_root = Path(
        tempfile.mkdtemp(
            prefix="linkcraftor_u3_11_"
        )
    )

    docs_root = temp_root / "docs"
    uduc_root = temp_root / "uduc"

    original_data_dir = files_route.DATA_DIR
    original_docs_dir = files_route.DOCS_DIR
    original_uduc_output_dir = uduc_store.UDUC_OUTPUT_DIR

    original_builder = (
        coordinator.build_and_write_uduc_from_extraction_result
    )

    original_highlight = (
        coordinator.run_uploaded_document_to_highlight_pipeline
    )

    original_registry = (
        coordinator.run_uploaded_document_registry_to_active_target_set_pipeline
    )

    try:
        # ----------------------------------------------------
        # Strict isolation from production filesystem data.
        # ----------------------------------------------------

        files_route.DATA_DIR = temp_root
        files_route.DOCS_DIR = docs_root
        uduc_store.UDUC_OUTPUT_DIR = uduc_root

        rollback_calls = []

        def rollback_spy(
            workspace_id,
            document_id,
            *,
            expected_stored_name,
        ):
            rollback_calls.append(
                (
                    workspace_id,
                    document_id,
                    expected_stored_name,
                )
            )

            return files_route._rollback_committed_upload(
                workspace_id,
                document_id,
                expected_stored_name=expected_stored_name,
            )

        def preview_poison(
            filename: str,
            ext: str,
            raw: bytes,
        ):
            return {
                "filename": filename,
                "ext": ext,
                "text": "U3_11_PREVIEW_POISON_TEXT",
                "html": "<p>U3_11_PREVIEW_POISON_HTML</p>",
                "is_html": True,
                "truncated": False,
            }

        deps = UploadIntakeDependencies(
            guess_extension=files_route._guess_ext,
            normalize_workspace_id=files_route._ws,
            extract_preview=preview_poison,
            store_and_index=files_route._store_and_index,
            rollback_committed_upload=rollback_spy,
            workspace_directory=files_route._ws_dir,
            allowed_extensions=files_route.ALLOWED_EXT,
        )

        # Prevent later branches from doing unrelated work.
        coordinator.run_uploaded_document_to_highlight_pipeline = (
            lambda **kwargs: {
                "ok": True,
                "test_stub": "highlight",
            }
        )

        coordinator.run_uploaded_document_registry_to_active_target_set_pipeline = (
            lambda **kwargs: {
                "ok": True,
                "test_stub": "registry",
            }
        )

        # ----------------------------------------------------
        # TEST 1
        # Successful canonical handoff.
        # ----------------------------------------------------

        builder_calls = []

        real_builder = (
            uduc_store.build_and_write_uduc_from_extraction_result
        )

        def builder_spy(**kwargs):
            builder_calls.append(dict(kwargs))
            return real_builder(**kwargs)

        coordinator.build_and_write_uduc_from_extraction_result = (
            builder_spy
        )

        canonical_text = (
            "U3.11 canonical extraction body. "
            "This content must reach UDUC."
        )

        success = await coordinator.run_upload_document(
            workspace_id="ws_u3_11_success",
            file=make_upload(
                "canonical.txt",
                canonical_text.encode("utf-8"),
            ),
            dependencies=deps,
        )

        check(
            "SUCCESSFUL_UPLOAD_DOCUMENT_PIPELINE",
            success.get("ok") is True,
        )

        check(
            "UDUC_BUILDER_CALLED_EXACTLY_ONCE",
            len(builder_calls) == 1,
        )

        handoff = (
            builder_calls[0]
            if builder_calls
            else {}
        )

        extraction = handoff.get("extraction_result") or {}
        source_metadata = handoff.get("source_metadata") or {}

        required_fields = {
            "source_path",
            "source_type",
            "title",
            "text",
            "headings",
            "metadata",
            "extraction_status",
            "extraction_confidence",
            "created_at",
        }

        check(
            "ALL_UPLOAD_EXTRACTION_RESULT_FIELDS_PRESENT",
            required_fields.issubset(
                extraction.keys()
            ),
        )

        check(
            "EXTRACTION_STATUS_SUCCESS_BEFORE_UDUC",
            extraction.get("extraction_status")
            == "success",
        )

        check(
            "CANONICAL_TEXT_HANDED_TO_UDUC",
            canonical_text
            in str(extraction.get("text") or ""),
        )

        check(
            "PREVIEW_TEXT_NOT_HANDED_AS_CANONICAL_CONTENT",
            "U3_11_PREVIEW_POISON_TEXT"
            not in str(extraction.get("text") or ""),
        )

        check(
            "PREVIEW_HTML_NOT_UDUC_BUILDER_ARGUMENT",
            "html" not in handoff
            and "preview_html" not in handoff
            and "preview_text" not in handoff,
        )

        success_doc = success.get("doc") or {}

        success_doc_id = str(
            success_doc.get("doc_id") or ""
        )

        success_stored_name = str(
            success_doc.get("stored_name") or ""
        )

        check(
            "WORKSPACE_ID_PRESERVED",
            handoff.get("workspace_id")
            == "ws_u3_11_success",
        )

        check(
            "DOCUMENT_ID_PRESERVED",
            handoff.get("document_id")
            == success_doc_id
            and bool(success_doc_id),
        )

        check(
            "ORIGINAL_FILENAME_PRESERVED",
            handoff.get("original_filename")
            == "canonical.txt",
        )

        check(
            "STORED_FILENAME_PRESERVED",
            handoff.get("stored_filename")
            == success_stored_name
            and bool(success_stored_name),
        )

        check(
            "CANONICAL_SOURCE_METADATA_PASSED",
            source_metadata.get("doc_id")
            == success_doc_id
            and source_metadata.get("stored_name")
            == success_stored_name,
        )

        uduc_path = (
            uduc_root
            / "ws_u3_11_success"
            / f"{success_doc_id}.json"
        )

        check(
            "UDUC_PERSISTED_THROUGH_APPROVED_STORE",
            uduc_path.is_file(),
        )

        persisted_uduc = {}

        if uduc_path.is_file():
            persisted_uduc = json.loads(
                uduc_path.read_text(
                    encoding="utf-8"
                )
            )

        check(
            "UDUC_CONTENT_BODY_IS_CANONICAL_EXTRACTION",
            canonical_text
            in str(
                persisted_uduc.get(
                    "content_body"
                )
                or ""
            ),
        )

        check(
            "UDUC_PREVIEW_POISON_ABSENT",
            "U3_11_PREVIEW_POISON_TEXT"
            not in json.dumps(
                persisted_uduc,
                ensure_ascii=False,
            )
            and "U3_11_PREVIEW_POISON_HTML"
            not in json.dumps(
                persisted_uduc,
                ensure_ascii=False,
            ),
        )

        check(
            "UDUC_IDENTITY_MATCHES_UPLOAD",
            persisted_uduc.get("workspace_id")
            == "ws_u3_11_success"
            and persisted_uduc.get("document_id")
            == success_doc_id,
        )

        check(
            "UDUC_SOURCE_FILENAMES_MATCH_UPLOAD",
            persisted_uduc.get("original_filename")
            == "canonical.txt"
            and persisted_uduc.get("stored_filename")
            == success_stored_name,
        )

        extraction_timestamp = str(
            (
                persisted_uduc.get("metadata")
                or {}
            ).get("extraction_timestamp")
            or ""
        )

        check(
            "EXTRACTION_CREATED_AT_PRESERVED_AS_TIMESTAMP",
            extraction_timestamp
            == str(
                extraction.get("created_at")
                or ""
            )
            and bool(extraction_timestamp),
        )

        check(
            "NO_INTAKE_ROLLBACK_ON_SUCCESS",
            len(rollback_calls) == 0,
        )

        # ----------------------------------------------------
        # TEST 2
        # UDUC failure AFTER successful intake must preserve
        # source + registry and must NOT invoke intake rollback.
        # ----------------------------------------------------

        rollback_calls.clear()

        def failing_uduc_builder(**kwargs):
            raise RuntimeError(
                "synthetic UDUC write failure"
            )

        coordinator.build_and_write_uduc_from_extraction_result = (
            failing_uduc_builder
        )

        failure_raised = False

        try:
            await coordinator.run_upload_document(
                workspace_id="ws_u3_11_failure",
                file=make_upload(
                    "preserve-source.txt",
                    b"committed source must survive UDUC failure",
                ),
                dependencies=deps,
            )
        except RuntimeError as exc:
            failure_raised = (
                "synthetic UDUC write failure"
                in str(exc)
            )

        check(
            "UDUC_FAILURE_PROPAGATES",
            failure_raised,
        )

        check(
            "UDUC_FAILURE_DOES_NOT_CALL_INTAKE_ROLLBACK",
            len(rollback_calls) == 0,
        )

        failure_ws = files_route._ws_dir(
            "ws_u3_11_failure"
        )

        failure_index = (
            failure_ws / "index.json"
        )

        failure_rows = []

        if failure_index.is_file():
            failure_rows = json.loads(
                failure_index.read_text(
                    encoding="utf-8"
                )
            )

        check(
            "UDUC_FAILURE_PRESERVES_REGISTRY_RECORD",
            isinstance(failure_rows, list)
            and len(failure_rows) == 1,
        )

        failure_stored_name = ""

        if (
            isinstance(failure_rows, list)
            and failure_rows
            and isinstance(failure_rows[0], dict)
        ):
            failure_stored_name = str(
                failure_rows[0].get(
                    "stored_name"
                )
                or ""
            )

        failure_source = (
            failure_ws / failure_stored_name
        )

        check(
            "UDUC_FAILURE_PRESERVES_SOURCE_FILE",
            bool(failure_stored_name)
            and failure_source.is_file(),
        )

        check(
            "UDUC_FAILURE_SOURCE_BYTES_EXACT",
            failure_source.is_file()
            and failure_source.read_bytes()
            == b"committed source must survive UDUC failure",
        )

        # ----------------------------------------------------
        # TEST 3
        # Current UDUC implementation must have no legacy
        # registry reread/helper residue.
        # ----------------------------------------------------

        uduc_source = Path(
            uduc_store.__file__
        ).read_text(
            encoding="utf-8"
        )

        forbidden_residue = (
            "def _read_upload_index_hit(",
            "_read_upload_index_hit(ws, doc_id)",
            "index_hit.get(",
            'BASE_DIR / "data" / "uploads" / workspace_id / "index.json"',
        )

        check(
            "NO_UDUC_REGISTRY_REREAD_RESIDUE",
            all(
                token not in uduc_source
                for token in forbidden_residue
            ),
        )

    finally:
        coordinator.build_and_write_uduc_from_extraction_result = (
            original_builder
        )

        coordinator.run_uploaded_document_to_highlight_pipeline = (
            original_highlight
        )

        coordinator.run_uploaded_document_registry_to_active_target_set_pipeline = (
            original_registry
        )

        files_route.DATA_DIR = original_data_dir
        files_route.DOCS_DIR = original_docs_dir
        uduc_store.UDUC_OUTPUT_DIR = original_uduc_output_dir

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

    failures = [
        name
        for name, status in results
        if status != "PASS"
    ]

    print()
    print("========================================")

    if failures:
        print(
            "U3.11_UDUC_HANDOFF_BEHAVIORAL_VERIFICATION: FAIL"
        )

        print("FAILED_CHECKS:")

        for failure in failures:
            print(f" - {failure}")

        raise RuntimeError(
            "U3.11 behavioral verification failed."
        )

    print(
        "U3.11_UDUC_HANDOFF_BEHAVIORAL_VERIFICATION: PASS"
    )


if __name__ == "__main__":
    asyncio.run(main())