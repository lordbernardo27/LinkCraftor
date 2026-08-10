"""
Canonical Upload Document Coordinator

Dependency-aware execution:

UPLOADED DOCUMENT
    -> Uploaded Document-to-UDUC Pipeline
    -> Uploaded Document-to-Highlight Pipeline
    -> Uploaded Document Registry-to-Active Target Set Pipeline

Pipeline 2 executes first because it creates the uploaded-document identity,
stored-file metadata, and extracted content required by Pipelines 1 and 3.

After Pipeline 2 completes, Pipelines 1 and 3 execute as independent
downstream branches using the Pipeline 2 result.
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import UploadFile

from .uploaded_document_to_uduc_pipeline import (
    UploadIntakeDependencies,
    run_uploaded_document_to_uduc_pipeline,
)
from .uploaded_document_to_highlight_pipeline import (
    run_uploaded_document_to_highlight_pipeline,
)
from .uploaded_document_registry_to_active_target_set_pipeline import (
    run_uploaded_document_registry_to_active_target_set_pipeline,
)


def _required_string(
    source: Dict[str, Any],
    *keys: str,
) -> str:
    for key in keys:
        value = source.get(key)

        if value is None:
            continue

        cleaned = str(value).strip()

        if cleaned:
            return cleaned

    return ""


async def run_upload_document(
    *,
    workspace_id: str,
    file: UploadFile,
    dependencies: UploadIntakeDependencies,
) -> Dict[str, Any]:
    """
    Canonical top-level Upload Document entry point.

    Execution order:
    1. Uploaded Document-to-UDUC Pipeline
    2. Uploaded Document-to-Highlight Pipeline
    3. Uploaded Document Registry-to-Active Target Set Pipeline
    """

    pipeline_2 = await run_uploaded_document_to_uduc_pipeline(
        workspace_id=workspace_id,
        file=file,
        dependencies=dependencies,
    )

    if not isinstance(pipeline_2, dict):
        raise RuntimeError(
            "Uploaded Document-to-UDUC Pipeline returned "
            "a non-dictionary result."
        )

    if pipeline_2.get("ok") is not True:
        return {
            "ok": False,
            "pipeline": "upload_document",
            "status": "UDUC_PIPELINE_FAILED",
            "execution_started": True,
            "execution_completed": False,
            "pipelines": {
                "uploaded_document_to_uduc_pipeline": pipeline_2,
                "uploaded_document_to_highlight_pipeline": {
                    "executed": False,
                    "reason": "Blocked by Pipeline 2 failure.",
                },
                "uploaded_document_registry_to_active_target_set_pipeline": {
                    "executed": False,
                    "reason": "Blocked by Pipeline 2 failure.",
                },
            },
        }

    document_metadata = pipeline_2.get("doc")

    if not isinstance(document_metadata, dict):
        raise RuntimeError(
            "Pipeline 2 result does not contain document metadata."
        )

    document_id = _required_string(
        document_metadata,
        "doc_id",
        "document_id",
        "id",
    )

    if not document_id:
        raise RuntimeError(
            "Pipeline 2 result does not contain a document ID."
        )

    extraction_result = {
        "title": _required_string(
            document_metadata,
            "title",
            "filename",
        ),
        "text": _required_string(
            pipeline_2,
            "text",
        ),
        "html": _required_string(
            pipeline_2,
            "html",
        ),
        "source_format": _required_string(
            pipeline_2,
            "ext",
        ),
    }

    pipeline_1 = run_uploaded_document_to_highlight_pipeline(
        workspace_id=str(
            pipeline_2.get("workspace_id") or workspace_id
        ),
        document_id=document_id,
        extraction_result=extraction_result,
    )

    pipeline_3 = (
        run_uploaded_document_registry_to_active_target_set_pipeline(
            workspace_id=str(
                pipeline_2.get("workspace_id") or workspace_id
            ),
            document_id=document_id,
            unified_content={
                "document_id": document_id,
                "workspace_id": str(
                    pipeline_2.get("workspace_id") or workspace_id
                ),
                "title": extraction_result["title"],
                "content_body": extraction_result["text"],
                "content_html": extraction_result["html"],
                "source_format": extraction_result["source_format"],
                "upload_metadata": document_metadata,
            },
        )
    )

    overall_ok = (
        pipeline_2.get("ok") is True
        and pipeline_1.get("ok") is True
        and pipeline_3.get("ok") is True
    )

    return {
        # ------------------------------------------------------------
        # Canonical HTTP upload compatibility contract
        # ------------------------------------------------------------
        # The editor upload client consumes these fields directly.
        # Pipeline 2 remains the authoritative producer.
        "ok": overall_ok,
        "workspace_id": str(
            pipeline_2.get("workspace_id") or workspace_id
        ),
        "doc": document_metadata,
        "filename": pipeline_2.get("filename")
        or document_metadata.get("filename")
        or document_metadata.get("title")
        or "",
        "ext": pipeline_2.get("ext") or "",
        "text": pipeline_2.get("text") or "",
        "html": pipeline_2.get("html") or "",
        "is_html": pipeline_2.get("is_html", False),
        "truncated": pipeline_2.get("truncated", False),

        # ------------------------------------------------------------
        # Canonical orchestration metadata
        # ------------------------------------------------------------
        "pipeline": "upload_document",
        "document_id": document_id,
        "status": (
            "UPLOAD_DOCUMENT_PIPELINES_COMPLETED"
            if overall_ok
            else "UPLOAD_DOCUMENT_PIPELINES_PARTIALLY_FAILED"
        ),
        "execution_started": True,
        "execution_completed": True,
        "execution_order": [
            "uploaded_document_to_uduc_pipeline",
            "uploaded_document_to_highlight_pipeline",
            (
                "uploaded_document_registry_to_"
                "active_target_set_pipeline"
            ),
        ],
        "pipelines": {
            "uploaded_document_to_uduc_pipeline": pipeline_2,
            "uploaded_document_to_highlight_pipeline": pipeline_1,
            (
                "uploaded_document_registry_to_"
                "active_target_set_pipeline"
            ): pipeline_3,
        },
    }


__all__ = [
    "run_upload_document",
]
