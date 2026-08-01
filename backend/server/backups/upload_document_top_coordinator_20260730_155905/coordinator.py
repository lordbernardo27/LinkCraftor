"""
LinkCraftor — Canonical Upload Document Coordinator

UPLOAD DOCUMENT
    ├── Pipeline 1 — Highlight Intelligence
    ├── Pipeline 2 — Ingestion and Unified Content
    └── Pipeline 3 — Registry and Target Activation

This coordinator owns orchestration boundaries only.

The live /api/files/upload route is not wired to this coordinator yet.
That migration will occur in controlled stages after each existing pipeline
implementation is identified and moved.
"""

from __future__ import annotations

from typing import Any, Dict


def run_upload_document(
    *,
    workspace_id: str,
    document_id: str,
    stored_path: str,
    upload_metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Future canonical fan-out entry point for Upload Document.

    No live pipeline is executed during the namespace-foundation step.
    """

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "document_id": document_id,
        "stored_path": stored_path,
        "status": "UPLOAD_DOCUMENT_NAMESPACE_READY",
        "execution_started": False,
        "pipelines": {
            "uploaded_document_to_highlight_pipeline": {
                "registered": True,
                "executed": False,
            },
            "uploaded_document_to_uduc_pipeline": {
                "registered": True,
                "executed": False,
            },
            "uploaded_document_registry_to_active_target_set_pipeline": {
                "registered": True,
                "executed": False,
            },
        },
        "upload_metadata_received": isinstance(upload_metadata, dict),
    }

