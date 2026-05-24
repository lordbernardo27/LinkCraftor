
from __future__ import annotations

from backend.server.orchestration.workspace_context import WorkspaceContext


def module_enabled(
    context: WorkspaceContext,
    module_name: str,
) -> bool:
    """
    Check whether a module is enabled for this workspace.
    """

    module_name = (module_name or "").strip()

    if not module_name:
        return False

    return module_name in set(context.enabled_modules)


def require_module(
    context: WorkspaceContext,
    module_name: str,
) -> None:
    """
    Raise safely if a worker tries to run a disabled module.
    """

    if not module_enabled(context, module_name):
        raise PermissionError(f"module disabled for workspace: {module_name}")
