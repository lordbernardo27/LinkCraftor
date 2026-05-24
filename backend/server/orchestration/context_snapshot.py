
from __future__ import annotations

from typing import Any, Dict

from backend.server.orchestration.workspace_context import WorkspaceContext


def build_context_snapshot(
    job: Dict[str, Any],
    context: WorkspaceContext,
    profile: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Store immutable orchestration context
    snapshot alongside job execution.
    """

    profile = profile or {}

    return {
        "job_id": job.get("job_id"),
        "workspace_id": context.workspace_id,
        "domain": context.domain,
        "plan": context.plan,
        "enabled_modules": list(context.enabled_modules),
        "feature_flags": dict(context.feature_flags),
        "billing_limits": dict(context.billing_limits),
        "document_limits": dict(context.document_limits),
        "au_limits": dict(context.au_limits),
        "workspace_profile": dict(profile),
    }
