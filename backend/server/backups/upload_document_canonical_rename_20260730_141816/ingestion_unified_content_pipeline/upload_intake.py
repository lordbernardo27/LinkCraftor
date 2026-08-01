"""
Upload Document Pipeline 2 — Upload Intake Boundary

Responsibilities:
- validate the upload request;
- validate the allowed extension;
- normalize the workspace identity;
- read the uploaded file;
- produce the immediate preview extraction;
- save and index the uploaded file;
- create the existing asynchronous document_upload_job;
- preserve the existing API response contract.

This module does not own:
- phrase intelligence;
- highlight selection;
- editor painting;
- Document Registry persistence;
- Active Target Set mutation.
"""

from __future__ import annotations

import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable

from fastapi import HTTPException, UploadFile


@dataclass(frozen=True)
class UploadIntakeDependencies:
    """
    Transitional dependency boundary.

    The existing low-level storage and extraction helpers still live in
    routes/files.py. They are injected here so Pipeline 2 can own the upload
    workflow without introducing a circular import.
    """

    guess_extension: Callable[[str], str]
    normalize_workspace_id: Callable[[str], str]
    extract_preview: Callable[[str, str, bytes], Dict[str, Any]]
    store_and_index: Callable[..., Dict[str, Any]]
    workspace_directory: Callable[[str], Path]
    allowed_extensions: Iterable[str]


async def run_upload_intake(
    *,
    workspace_id: str,
    file: UploadFile,
    dependencies: UploadIntakeDependencies,
) -> Dict[str, Any]:
    """
    Execute the canonical Pipeline 2 upload-intake boundary.
    """

    if not file or not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file uploaded.",
        )

    extension = dependencies.guess_extension(file.filename)

    allowed_extensions = {
        str(value or "").strip().lower()
        for value in dependencies.allowed_extensions
        if str(value or "").strip()
    }

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed: {extension}",
        )

    normalized_workspace_id = dependencies.normalize_workspace_id(
        workspace_id
    )

    raw = await file.read()

    preview = dependencies.extract_preview(
        Path(file.filename).name,
        extension,
        raw,
    )

    metadata = dependencies.store_and_index(
        normalized_workspace_id,
        file,
        raw,
        preview_html=str(preview.get("html") or ""),
        preview_text=str(preview.get("text") or ""),
    )

    processing_job_id = None

    try:
        from backend.server.orchestration.service import (
            create_orchestration_job,
        )

        stored_path = str(
            dependencies.workspace_directory(
                normalized_workspace_id
            )
            / str(metadata.get("stored_name") or "")
        )

        document_id = str(
            metadata.get("doc_id") or ""
        ).strip()

        processing_job = create_orchestration_job(
            workspace_id=normalized_workspace_id,
            job_type="document_upload_job",
            payload={
                "workspace_id": normalized_workspace_id,
                "doc_id": document_id,
                "stored_path": stored_path,
                "stored_name": str(
                    metadata.get("stored_name") or ""
                ),
                "original_name": str(
                    metadata.get("filename") or ""
                ),
                "html": str(preview.get("html") or ""),
                "text": str(preview.get("text") or ""),
                "source_route": "/upload",
                "document_count": 1,
            },
            metadata={
                "phase": "phase_2_background_orchestration",
                "filename": str(
                    metadata.get("filename") or ""
                ),
                "stored_name": str(
                    metadata.get("stored_name") or ""
                ),
                "document_count": 1,
            },
            priority=5,
        )

        processing_job_id = processing_job.job_id

        metadata["universal_knowledge_orchestration"] = {
            "ok": True,
            "status": "queued",
            "note": (
                "Phase 2: orchestration job created and queued "
                "without blocking upload."
            ),
            "job_id": processing_job_id,
        }

    except Exception as exc:
        print(
            "[UPLOAD_ORCHESTRATION_QUEUE_ERROR]",
            repr(exc),
        )
        traceback.print_exc()

        metadata["universal_knowledge_orchestration"] = {
            "ok": False,
            "status": "queue_failed",
            "error": str(exc)[:160],
            "job_id": None,
        }

    return {
        "ok": True,
        "workspace_id": normalized_workspace_id,
        "doc": metadata,
        "filename": preview.get("filename"),
        "ext": preview.get("ext"),
        "text": preview.get("text"),
        "html": preview.get("html"),
        "is_html": bool(preview.get("is_html")),
        "truncated": bool(preview.get("truncated")),
        "job_id": processing_job_id,
        "processing_status": (
            "queued"
            if processing_job_id
            else "queue_failed"
        ),
        "pipeline": "ingestion_unified_content_pipeline",
        "pipeline_stage": "upload_intake",
    }
