
from __future__ import annotations

from typing import Any, Dict

from backend.server.orchestration.workspace_context import WorkspaceContext


DEFAULT_PROFILES = {
    "starter": {
        "processing_priority": "normal",
        "linking_mode": "balanced",
        "batch_enabled": False,
    },
    "pro": {
        "processing_priority": "high",
        "linking_mode": "balanced",
        "batch_enabled": True,
    },
    "business": {
        "processing_priority": "high",
        "linking_mode": "aggressive",
        "batch_enabled": True,
    },
    "enterprise": {
        "processing_priority": "critical",
        "linking_mode": "custom",
        "batch_enabled": True,
    },
}


def build_workspace_profile(
    context: WorkspaceContext,
) -> Dict[str, Any]:
    """
    Build orchestration behavior profile
    for the workspace.
    """

    profile = DEFAULT_PROFILES.get(
        context.plan,
        DEFAULT_PROFILES["business"],
    )

    return dict(profile)
