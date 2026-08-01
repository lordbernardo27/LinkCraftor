"""
Uploaded Document Registry-to-Active Target Set Pipeline

Entry-point scope only:

UPLOADED DOCUMENT
    -> Uploaded Document Registry-to-Active Target Set Pipeline
    -> Document Pre-validation

Downstream registry and Active Target Set stages remain in their existing
production locations and are not executed by this coordinator during the
pipeline-separation phase.
"""

from __future__ import annotations

from typing import Any, Dict

from .document_pre_validation import (
    run_document_pre_validation,
)


def run_uploaded_document_registry_to_active_target_set_pipeline(
    *,
    workspace_id: str,
    document_id: str,
    unified_content: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Canonical entry point for the Uploaded Document Registry-to-Active
    Target Set Pipeline.

    This coordinator delegates only to Document Pre-validation.
    """

    if not isinstance(unified_content, dict):
        raise TypeError("unified_content must be a dictionary.")

    pre_validation = run_document_pre_validation(
        workspace_id=workspace_id,
        document_id=document_id,
        unified_content=unified_content,
    )

    return {
        "ok": bool(pre_validation.get("ok")),
        "pipeline": (
            "uploaded_document_registry_to_active_target_set_pipeline"
        ),
        "workspace_id": pre_validation["workspace_id"],
        "document_id": pre_validation["document_id"],
        "status": pre_validation["status"],
        "executed": True,
        "entry_point": "document_pre_validation",
        "pre_validation": pre_validation,
    }


__all__ = [
    "run_uploaded_document_registry_to_active_target_set_pipeline",
]
