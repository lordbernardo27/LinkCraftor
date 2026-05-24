
from __future__ import annotations

from typing import Any, Dict, Tuple

from backend.server.orchestration.workspace_context import WorkspaceContext


def check_workspace_limits(
    context: WorkspaceContext,
    usage: Dict[str, Any] | None = None,
) -> Tuple[bool, str]:
    """
    Check workspace limits before worker execution.

    This is intentionally lightweight for now.
    Later this will connect to real usage/billing storage.
    """

    usage = usage or {}

    used_documents = int(usage.get("monthly_documents_used", 0) or 0)
    used_aus = int(usage.get("monthly_aus_used", 0) or 0)

    max_documents = int(context.document_limits.get("monthly_documents", 0) or 0)
    max_aus = int(context.au_limits.get("monthly_aus", 0) or 0)

    if max_documents and used_documents >= max_documents:
        return False, "document_limit_reached"

    if max_aus and used_aus >= max_aus:
        return False, "au_limit_reached"

    return True, "ok"
