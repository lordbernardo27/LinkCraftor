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


async def main() -> None:
    root = Path(tempfile.mkdtemp(prefix="linkcraftor_u3_7_"))
    original_data_dir = files_route.DATA_DIR

    original_extractor = intake_module.extract_upload_document_v1
    original_serializer = intake_module.serialize_upload_extraction_result

    try:
        # Redirect canonical Files storage into disposable test storage.
        files_route.DATA_DIR = root

        workspace_id = "ws_u3_7_test"

        deps = UploadIntakeDependencies(
            guess_extension=files_route._guess_ext,
            normalize_workspace_id=files_route._ws,
            extract_preview=fake_preview,
            store_and_index=files_route._store_and_index,
            rollback_committed_upload=files_route._rollback_committed_upload,
            workspace_directory=files_route._ws_dir,
            allowed_extensions=files_route.ALLOWED_EXT,
        )

        # --------------------------------------------------------
        # TEST 1 — rollback primitive removes only exact document.
        # --------------------------------------------------------
        upload_a = make_upload("a.txt", b"alpha")
        meta_a = files_route._store_and_index(
            workspace_id,
            upload_a,
            b"alpha",
            preview_html="",
            preview_text="alpha",
        )

        upload_b = make_upload("b.txt", b"beta")
        meta_b = files_route._store_and_index(
            workspace_id,
            upload_b,
            b"beta",
            preview_html="",
            preview_text="beta",
        )

        files_route._rollback_committed_upload(
            workspace_id,
            meta_a["doc_id"],
            expected_stored_name=meta_a["stored_name"],
        )

        idx_path = files_route._index_path(workspace_id)
        items = json.loads(idx_path.read_text(encoding="utf-8"))

        ids = {str(item.get("doc_id") or "") for item in items}

        check(
            "ROLLBACK_REMOVES_TARGET_REGISTRY_RECORD",
            meta_a["doc_id"] not in ids,
        )

        check(
            "ROLLBACK_PRESERVES_NEIGHBOR_REGISTRY_RECORD",
            meta_b["doc_id"] in ids,
        )

        check(
            "ROLLBACK_REMOVES_TARGET_SOURCE",
            not (
                files_route._ws_dir(workspace_id)
                / meta_a["stored_name"]
            ).exists(),
        )

        check(
            "ROLLBACK_PRESERVES_NEIGHBOR_SOURCE",
            (
                files_route._ws_dir(workspace_id)
                / meta_b["stored_name"]
            ).is_file(),
        )

        # --------------------------------------------------------
        # TEST 2 — non-success extraction status rolls back.
        # --------------------------------------------------------
        before = json.loads(idx_path.read_text(encoding="utf-8"))
        before_ids = {
            str(item.get("doc_id") or "")
            for item in before
        }

        def failed_status_extractor(path: Path):
            return SimpleNamespace(
                extraction_status="extraction_error",
                metadata={"error": "forced extraction failure"},
            )

        intake_module.extract_upload_document_v1 = failed_status_extractor

        failed_status_raised = False

        try:
            await run_upload_intake(
                workspace_id=workspace_id,
                file=make_upload(
                    "failed-status.txt",
                    b"forced failure",
                ),
                dependencies=deps,
            )
        except RuntimeError as exc:
            failed_status_raised = (
                "Canonical uploaded-document extraction failed"
                in str(exc)
            )

        after = json.loads(idx_path.read_text(encoding="utf-8"))
        after_ids = {
            str(item.get("doc_id") or "")
            for item in after
        }

        check(
            "FAILED_EXTRACTION_STATUS_RAISES",
            failed_status_raised,
        )

        check(
            "FAILED_EXTRACTION_STATUS_REGISTRY_ROLLED_BACK",
            after_ids == before_ids,
        )

        current_sources = {
            p.name
            for p in files_route._ws_dir(workspace_id).iterdir()
            if p.is_file() and p.name != "index.json"
        }

        check(
            "FAILED_EXTRACTION_STATUS_NO_ORPHAN_SOURCE",
            current_sources == {meta_b["stored_name"]},
        )

        # --------------------------------------------------------
        # TEST 3 — extractor exception rolls back.
        # --------------------------------------------------------
        def exploding_extractor(path: Path):
            raise RuntimeError("forced extractor exception")

        intake_module.extract_upload_document_v1 = exploding_extractor

        extractor_exception_raised = False

        try:
            await run_upload_intake(
                workspace_id=workspace_id,
                file=make_upload(
                    "extractor-exception.txt",
                    b"forced extractor exception",
                ),
                dependencies=deps,
            )
        except RuntimeError as exc:
            extractor_exception_raised = (
                "forced extractor exception" in str(exc)
            )

        after_extractor_exception = json.loads(
            idx_path.read_text(encoding="utf-8")
        )

        check(
            "EXTRACTOR_EXCEPTION_RAISES",
            extractor_exception_raised,
        )

        check(
            "EXTRACTOR_EXCEPTION_REGISTRY_ROLLED_BACK",
            {
                str(item.get("doc_id") or "")
                for item in after_extractor_exception
            }
            == before_ids,
        )

        # --------------------------------------------------------
        # TEST 4 — serializer exception rolls back.
        # --------------------------------------------------------
        def successful_extractor(path: Path):
            return SimpleNamespace(
                extraction_status="success",
                metadata={},
            )

        def exploding_serializer(result):
            raise RuntimeError("forced serializer exception")

        intake_module.extract_upload_document_v1 = successful_extractor
        intake_module.serialize_upload_extraction_result = exploding_serializer

        serializer_exception_raised = False

        try:
            await run_upload_intake(
                workspace_id=workspace_id,
                file=make_upload(
                    "serializer-exception.txt",
                    b"forced serializer exception",
                ),
                dependencies=deps,
            )
        except RuntimeError as exc:
            serializer_exception_raised = (
                "forced serializer exception" in str(exc)
            )

        after_serializer_exception = json.loads(
            idx_path.read_text(encoding="utf-8")
        )

        check(
            "SERIALIZER_EXCEPTION_RAISES",
            serializer_exception_raised,
        )

        check(
            "SERIALIZER_EXCEPTION_REGISTRY_ROLLED_BACK",
            {
                str(item.get("doc_id") or "")
                for item in after_serializer_exception
            }
            == before_ids,
        )

        # --------------------------------------------------------
        # TEST 5 — successful intake keeps source + registry.
        # --------------------------------------------------------
        def successful_serializer(result):
            return {
                "extraction_status": "success",
                "metadata": {},
            }

        intake_module.serialize_upload_extraction_result = successful_serializer

        success_result = await run_upload_intake(
            workspace_id=workspace_id,
            file=make_upload(
                "success.txt",
                b"successful intake",
            ),
            dependencies=deps,
        )

        success_doc = success_result.get("doc") or {}
        success_doc_id = str(
            success_doc.get("doc_id") or ""
        )
        success_stored_name = str(
            success_doc.get("stored_name") or ""
        )

        final_items = json.loads(
            idx_path.read_text(encoding="utf-8")
        )

        final_ids = {
            str(item.get("doc_id") or "")
            for item in final_items
        }

        check(
            "SUCCESSFUL_INTAKE_RETURNS_OK_TRUE",
            success_result.get("ok") is True,
        )

        check(
            "SUCCESSFUL_INTAKE_REGISTRY_PRESERVED",
            bool(success_doc_id)
            and success_doc_id in final_ids,
        )

        check(
            "SUCCESSFUL_INTAKE_SOURCE_PRESERVED",
            bool(success_stored_name)
            and (
                files_route._ws_dir(workspace_id)
                / success_stored_name
            ).is_file(),
        )

        # --------------------------------------------------------
        # TEST 6 — rollback retry is idempotent.
        # --------------------------------------------------------
        files_route._rollback_committed_upload(
            workspace_id,
            success_doc_id,
            expected_stored_name=success_stored_name,
        )

        files_route._rollback_committed_upload(
            workspace_id,
            success_doc_id,
            expected_stored_name=success_stored_name,
        )

        check(
            "ROLLBACK_RETRY_IDEMPOTENT",
            not (
                files_route._ws_dir(workspace_id)
                / success_stored_name
            ).exists(),
        )

    finally:
        intake_module.extract_upload_document_v1 = original_extractor
        intake_module.serialize_upload_extraction_result = original_serializer
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
        print("U3.7_BEHAVIORAL_VERIFICATION: FAIL")
        print("FAILED_CHECKS:")
        for failure in failures:
            print(f" - {failure}")
        raise SystemExit(1)

    print("U3.7_BEHAVIORAL_VERIFICATION: PASS")


if __name__ == "__main__":
    asyncio.run(main())