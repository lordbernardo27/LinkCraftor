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

from backend.server.stores.upload_document_extractor import (
    UploadExtractionResult,
)
from backend.server.stores.upload_document_normalizer import (
    normalize_uploaded_document_v1,
)
from backend.server.stores.uploaded_document_unified_content import (
    build_and_write_uduc_from_normalized_content,
)
from backend.server.universal_unified_content_document.uucd_engine_v1 import (
    build_transient_uucd_from_uduc_v1,
)

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

    # ------------------------------------------------------------
    # Dedicated extraction is authoritative for ingestion.
    # Immediate preview fields remain UI/highlight compatibility only.
    # ------------------------------------------------------------

    extraction_result = pipeline_2.get("extraction")

    if not isinstance(extraction_result, dict):
        raise RuntimeError(
            "Pipeline 2 result does not contain the dedicated "
            "UploadExtractionResult."
        )

    extraction_text = _required_string(
        extraction_result,
        "text",
        "content_body",
    )

    extraction_title = _required_string(
        extraction_result,
        "title",
    ) or _required_string(
        document_metadata,
        "title",
        "filename",
    )

    extraction_source_format = _required_string(
        extraction_result,
        "source_type",
        "source_format",
    )

    normalized_workspace_id = str(
        pipeline_2.get("workspace_id") or workspace_id
    )

    # ------------------------------------------------------------
    # Canonical U7 normalization.
    #
    # Pipeline 2 returns the serialized UploadExtractionResult for
    # compatibility. Reconstruct the canonical U6 result, then pass it
    # through U7 before UDUC construction.
    # ------------------------------------------------------------

    extraction_metadata = extraction_result.get(
        "metadata"
    )

    if not isinstance(
        extraction_metadata,
        dict,
    ):
        extraction_metadata = {}

    extraction_headings = extraction_result.get(
        "headings"
    )

    if not isinstance(
        extraction_headings,
        list,
    ) or not all(
        isinstance(
            heading,
            str,
        )
        for heading in extraction_headings
    ):
        raise RuntimeError(
            "Pipeline 2 extraction headings are malformed."
        )

    canonical_extraction_result = UploadExtractionResult(
        source_path=str(
            extraction_result.get(
                "source_path"
            )
            or ""
        ),
        source_type=str(
            extraction_result.get(
                "source_type"
            )
            or ""
        ),
        title=str(
            extraction_result.get(
                "title"
            )
            or ""
        ),
        text=str(
            extraction_result.get(
                "text"
            )
            or ""
        ),
        headings=list(
            extraction_headings
        ),
        metadata=dict(
            extraction_metadata
        ),
        extraction_status=str(
            extraction_result.get(
                "extraction_status"
            )
            or ""
        ),
        extraction_confidence=float(
            extraction_result.get(
                "extraction_confidence"
            )
            or 0.0
        ),
        created_at=str(
            extraction_result.get(
                "created_at"
            )
            or ""
        ),
    )

    normalized_content = (
        normalize_uploaded_document_v1(
            canonical_extraction_result
        )
    )

    if (
        normalized_content.normalization_status
        != "success"
    ):
        raise RuntimeError(
            "Canonical uploaded-document normalization did not complete successfully."
        )

    # ------------------------------------------------------------
    # Canonical U8 UDUC construction + persistence.
    # ------------------------------------------------------------

    uduc_result = build_and_write_uduc_from_normalized_content(
        normalized_content=normalized_content,
        workspace_id=normalized_workspace_id,
        document_id=document_id,
        original_filename=_required_string(
            document_metadata,
            "filename",
        ),
        stored_filename=_required_string(
            document_metadata,
            "stored_name",
        ),
        source_metadata=document_metadata,
    )

    if not isinstance(uduc_result, dict):
        raise RuntimeError(
            "UDUC builder/writer returned a non-dictionary result."
        )

    if uduc_result.get("ok") is not True:
        raise RuntimeError(
            "UDUC builder/writer did not complete successfully."
        )

    uduc = uduc_result.get("uduc")

    if not isinstance(uduc, dict):
        raise RuntimeError(
            "UDUC builder/writer result does not contain "
            "serialized UDUC."
        )

    # ------------------------------------------------------------
    # ------------------------------------------------------------
    # Canonical U9 UDUC -> Current Canonical UUCD convergence.
    #
    # Produces only the transient Current Canonical Option-3
    # Universal Handoff Envelope.
    #
    # No Body Store write.
    # No finalized UUCD persistence.
    # No runtime.
    # No Semantic Intelligence.
    # No scorer.
    # ------------------------------------------------------------

    uucd_envelope = build_transient_uucd_from_uduc_v1(
        uduc
    )

    if not isinstance(
        uucd_envelope,
        dict,
    ):
        raise RuntimeError(
            "Uploaded Document U9 UUCD builder returned "
            "a non-dictionary envelope."
        )

    if (
        uucd_envelope.get(
            "envelope_status"
        )
        != "READY_FOR_BODY_STORE"
    ):
        raise RuntimeError(
            "Uploaded Document U9 UUCD envelope is not "
            "READY_FOR_BODY_STORE."
        )
    # Highlight pipeline receives dedicated extracted text.
    # Preview HTML remains compatibility-only because the dedicated
    # extractor's canonical output is plain extracted document content.
    # ------------------------------------------------------------

    highlight_extraction_result = {
        "title": extraction_title,
        "text": extraction_text,
        "html": _required_string(
            pipeline_2,
            "html",
        ),
        "source_format": extraction_source_format,
    }

    pipeline_1 = run_uploaded_document_to_highlight_pipeline(
        workspace_id=normalized_workspace_id,
        document_id=document_id,
        extraction_result=highlight_extraction_result,
    )

    # ------------------------------------------------------------
    # Registry handoff receives real UDUC instead of a hand-built
    # preview-derived pseudo-unified-content dictionary.
    # ------------------------------------------------------------

    pipeline_3 = (
        run_uploaded_document_registry_to_active_target_set_pipeline(
            workspace_id=normalized_workspace_id,
            document_id=document_id,
            unified_content=uduc,
        )
    )

    overall_ok = (
        pipeline_2.get("ok") is True
        and uduc_result.get("ok") is True
        and uucd_envelope.get(
            "envelope_status"
        ) == "READY_FOR_BODY_STORE"
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
            "uploaded_document_to_current_canonical_uucd",
            "uploaded_document_to_highlight_pipeline",
            (
                "uploaded_document_registry_to_"
                "active_target_set_pipeline"
            ),
        ],
        "pipelines": {
            "uploaded_document_to_uduc_pipeline": pipeline_2,
            "uploaded_document_to_current_canonical_uucd": {
                "ok": True,
                "status": "READY_FOR_BODY_STORE",
                "envelope": uucd_envelope,
            },
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
