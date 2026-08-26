"""
Upload Document Pipeline 2 — Upload Intake Boundary

Responsibilities:
- validate the upload request;
- validate the allowed extension;
- normalize the workspace identity;
- read the uploaded file;
- produce the immediate preview extraction;
- save and index the uploaded file;
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
        "job_id": None,
        "processing_status": "not_applicable",
        "pipeline": "uploaded_document_to_uduc_pipeline",
        "pipeline_stage": "upload_intake",
    }

