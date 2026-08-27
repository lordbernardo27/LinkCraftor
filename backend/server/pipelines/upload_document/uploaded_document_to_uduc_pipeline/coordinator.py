"""
Uploaded Document-to-UDUC Pipeline

Entry-point scope:

UPLOADED DOCUMENT
    -> Upload API / File Route
    -> Uploaded Document-to-UDUC Pipeline Coordinator
    -> Upload Intake

The coordinator delegates the upload request into the existing canonical
upload-intake implementation.

Format detection, format routing, extraction, and UDUC internals
remain in their existing production locations.
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import UploadFile

from .upload_intake import (
    UploadIntakeDependencies,
    run_upload_intake,
)


async def run_uploaded_document_to_uduc_pipeline(
    *,
    workspace_id: str,
    file: UploadFile,
    dependencies: UploadIntakeDependencies,
) -> Dict[str, Any]:
    """
    Canonical entry point for the Uploaded Document-to-UDUC Pipeline.

    This coordinator owns orchestration only and delegates directly to the
    existing upload-intake boundary.
    """

    result = await run_upload_intake(
        workspace_id=workspace_id,
        file=file,
        dependencies=dependencies,
    )

    if not isinstance(result, dict):
        raise RuntimeError(
            "Uploaded Document-to-UDUC upload intake returned "
            "a non-dictionary result."
        )

    result["pipeline"] = "uploaded_document_to_uduc_pipeline"
    result["pipeline_entry"] = (
        "run_uploaded_document_to_uduc_pipeline"
    )

    return result


__all__ = [
    "run_uploaded_document_to_uduc_pipeline",
]
