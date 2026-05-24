
from __future__ import annotations

from typing import Any, Dict

from backend.server.orchestration.workspace_context import (
    WorkspaceContext,
    load_workspace_context,
)


def build_worker_context(job: Dict[str, Any]) -> WorkspaceContext:
    """
    Load workspace-aware orchestration context
    before worker execution.
    """

    workspace_id = (job.get("workspace_id") or "").strip()

    if not workspace_id:
        raise ValueError("worker job missing workspace_id")

    plan = (job.get("plan") or "business").strip().lower()

    return load_workspace_context(
        workspace_id=workspace_id,
        plan=plan,
    )
