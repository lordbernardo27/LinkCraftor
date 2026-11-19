"""Canonical UUCD execution adapter for existing Universal Runtime.

Source-only integration. Registration and worker activation are separate.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from backend.server.runtime.uucd_runtime_handoff_v1 import (
    build_uucd_runtime_payload_v1,
)
from backend.server.universal_unified_content_document.uucd_persistence_v1 import (
    load_persisted_uucd_for_runtime_v1,
)
from backend.server.semantic_intelligence.semantic_intelligence_runtime_reader_v1 import (
    read_semantic_ready_article_v1,
)

JOB_TYPE = "uucd_runtime_handoff"

REQUIRED_FIELDS = (
    "document_id",
    "content_ref",
    "body_ref",
    "source_type",
    "content_hash",
    "persistence_fingerprint",
)


def execute_canonical_uucd_runtime_job_v1(
    job: Mapping[str, Any],
    *,
    project_root: str | Path | None = None,
) -> dict[str, Any]:
    """Execute one canonical article read from a trusted job envelope.

    Must only be invoked by an authorized Universal Runtime dispatcher.
    This function does not itself grant worker execution authority.
    """
    if not isinstance(job, Mapping):
        raise ValueError("Canonical Universal Job mapping required.")

    if job.get("job_type") != JOB_TYPE:
        raise ValueError("Unexpected Universal Runtime job type.")

    workspace_id = job.get("workspace_id")
    if not isinstance(workspace_id, str) or not workspace_id.strip():
        raise ValueError("Canonical workspace identity required.")

    payload = job.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("Canonical job payload required.")

    for field in REQUIRED_FIELDS:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Required canonical field missing: {field}")

    root = (
        Path(project_root).resolve()
        if project_root is not None
        else Path(__file__).resolve().parents[3]
    )

    record = load_persisted_uucd_for_runtime_v1(
        project_root=root,
        workspace_id=workspace_id,
        document_id=payload["document_id"],
        content_ref=payload["content_ref"],
        content_hash=payload["content_hash"],
        source_type=payload["source_type"],
        body_ref=payload["body_ref"],
        persistence_fingerprint=payload["persistence_fingerprint"],
    )

    # Reuse the original handoff validator and require an exact
    # canonical payload match before semantic processing.
    expected_payload = build_uucd_runtime_payload_v1(record)

    if expected_payload != dict(payload):
        raise ValueError("Universal Job and canonical UUCD do not match.")

    # The reader enforces semantic readiness and Body Store integrity.
    return read_semantic_ready_article_v1(
        record,
        project_root=root,
    )
