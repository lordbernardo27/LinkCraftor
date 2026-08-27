"""
Upload Document Pipeline 2 — Upload Intake Boundary

Responsibilities:
- validate the upload request;
- validate the allowed extension;
- normalize the workspace identity;
- read the uploaded file;
- produce the immediate UI/API preview extraction;
- save and index the uploaded source file;
- run the dedicated Uploaded Document Extractor on the stored source file;
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

# Canonical Uploaded Document per-file limit:
# 250 MiB = 262,144,000 bytes.
MAX_UPLOAD_BYTES = 250 * 1024 * 1024


from backend.server.stores.upload_document_extractor import (
    extract_upload_document_v1,
    serialize_upload_extraction_result,
)


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
    rollback_committed_upload: Callable[..., None]
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

    if not file:
        raise HTTPException(
            status_code=400,
            detail="No file uploaded.",
        )

    filename = str(file.filename or "").strip()

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file must have a filename.",
        )

    try:
        extension = dependencies.guess_extension(filename)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Uploaded filename is invalid.",
        ) from None

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

    try:
        normalized_workspace_id = dependencies.normalize_workspace_id(
            workspace_id
        )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="workspace_id is invalid.",
        ) from None

    # Read at most one byte beyond the canonical limit so oversized
    # uploads can be rejected without unbounded application-memory reads.
    raw = await file.read(MAX_UPLOAD_BYTES + 1)

    if not raw:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Uploaded file exceeds the 250 MB limit.",
        )

    preview = dependencies.extract_preview(
        Path(filename).name,
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

    if not isinstance(metadata, dict):
        raise RuntimeError(
            "Upload storage completed without canonical document metadata."
        )

    document_id = str(metadata.get("doc_id") or "").strip()
    stored_name = str(metadata.get("stored_name") or "").strip()

    try:
        if not document_id:
            raise RuntimeError(
                "Upload storage completed without a document_id."
            )
    
        if not stored_name:
            raise RuntimeError(
                "Upload storage completed without a stored_name."
            )
    
        stored_path = (
            dependencies.workspace_directory(
                normalized_workspace_id
            )
            / stored_name
        )

        if not stored_path.is_file():
            raise RuntimeError(
                "Stored uploaded source file could not be found: "
                f"{stored_path}"
            )

        extraction_result = extract_upload_document_v1(
            stored_path
        )

        extraction_status = str(
            getattr(
                extraction_result,
                "extraction_status",
                "",
            )
            or ""
        ).strip().lower()

        if extraction_status != "success":
            extraction_metadata = getattr(
                extraction_result,
                "metadata",
                {},
            )

            extraction_error = ""

            if isinstance(extraction_metadata, dict):
                extraction_error = str(
                    extraction_metadata.get("error") or ""
                ).strip()

            detail = (
                f": {extraction_error}"
                if extraction_error
                else ""
            )

            raise RuntimeError(
                "Canonical uploaded-document extraction failed "
                f"with status '{extraction_status or 'unknown'}'"
                f"{detail}"
            )

        extraction = serialize_upload_extraction_result(
            extraction_result
        )

    except Exception as intake_exc:
        try:
            dependencies.rollback_committed_upload(
                normalized_workspace_id,
                document_id,
                expected_stored_name=stored_name,
            )
        except Exception as rollback_exc:
            raise RuntimeError(
                "Upload intake failed after storage commit and "
                "the committed upload could not be rolled back safely."
            ) from rollback_exc

        raise

    return {
        "ok": True,
        "workspace_id": normalized_workspace_id,
        "doc": metadata,
        "extraction": extraction,
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

