"""Scoped Semantic Memory certification workspace policy.

This is a specialized, non-consuming policy adapter.
It does not replace Universal Runtime authorization or establish
the authenticity of a provisioned resolver.
"""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from backend.server.engine.semantic_memory_certification_workspace_boundary import (
    ProvisionedCertificationWorkspaceBoundary,
    CertificationWorkspaceAccessDenied,
)


CERTIFICATION_WORKSPACE_OPERATION = (
    "SEMANTIC_MEMORY_CERTIFICATION_CONTEXT_READ"
)


class CertificationWorkspacePolicyDenied(RuntimeError):
    """The requested certification workspace operation is denied."""


class ProvisionedCertificationWorkspacePolicy:
    """Evaluate the exact certification workspace operation."""

    def __init__(
        self,
        *,
        workspace_boundary: ProvisionedCertificationWorkspaceBoundary,
    ) -> None:
        if not isinstance(
            workspace_boundary,
            ProvisionedCertificationWorkspaceBoundary,
        ):
            raise ValueError("Provisioned workspace boundary required")

        self._workspace_boundary = workspace_boundary

    def evaluate(
        self,
        *,
        request_lookup: object,
        workspace_id: str,
        operation: str,
    ) -> Mapping:
        if (
            type(operation) is not str
            or operation != CERTIFICATION_WORKSPACE_OPERATION
        ):
            raise CertificationWorkspacePolicyDenied(
                "Unsupported certification workspace operation"
            )

        try:
            access = self._workspace_boundary.evaluate(
                request_lookup=request_lookup,
                workspace_id=workspace_id,
            )
        except CertificationWorkspaceAccessDenied as exc:
            raise CertificationWorkspacePolicyDenied(
                "Certification workspace access denied"
            ) from exc

        return MappingProxyType({
            "operation": CERTIFICATION_WORKSPACE_OPERATION,
            "principal_id": access["principal_id"],
            "workspace_id": access["workspace_id"],
            "workspace_evidence_matched": True,
            "authorization_source": access["authorization_source"],
            "authorization_reference": access[
                "authorization_reference"
            ],
            "fully_certified": False,
            "consumption_authorized": False,
        })
