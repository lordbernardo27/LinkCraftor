"""Fail-closed registration of Semantic Memory workspace policy.

No production workspace entitlement authority is provisioned here.
This registration cannot authorize consumption of Semantic Memory.
"""

from __future__ import annotations

from typing import Any

from backend.server.engine.semantic_memory_certification_identity_boundary import (
    ProvisionedCertificationIdentityBoundary,
)
from backend.server.engine.semantic_memory_certification_workspace_boundary import (
    CertificationWorkspaceAccessDenied,
    ProvisionedCertificationWorkspaceBoundary,
)
from backend.server.engine.semantic_memory_certification_workspace_policy import (
    ProvisionedCertificationWorkspacePolicy,
)
from backend.server.runtime.semantic_memory_certification_identity_registration import (
    CERTIFICATION_IDENTITY_COMPONENT_KEY,
)


CERTIFICATION_WORKSPACE_POLICY_COMPONENT_KEY = (
    "semantic_memory.certification.workspace_policy.v1"
)


class CertificationWorkspaceRegistrationError(RuntimeError):
    """Workspace policy registration failed."""


def _unavailable_workspace_authority(
    *,
    identity: object,
    workspace_id: str,
) -> None:
    raise CertificationWorkspaceAccessDenied(
        "Production workspace access authority is not provisioned"
    )


def register_semantic_memory_certification_workspace(
    composition: Any,
    **_: Any,
) -> ProvisionedCertificationWorkspacePolicy:
    """Bind a deny-by-default workspace policy to the existing kernel."""

    kernel = composition.kernel

    if kernel.has_component(
        CERTIFICATION_WORKSPACE_POLICY_COMPONENT_KEY
    ):
        raise CertificationWorkspaceRegistrationError(
            "Certification workspace policy already registered"
        )

    if not kernel.has_component(
        CERTIFICATION_IDENTITY_COMPONENT_KEY
    ):
        raise CertificationWorkspaceRegistrationError(
            "Certification identity boundary must be registered first"
        )

    identity_boundary = kernel.get_component(
        CERTIFICATION_IDENTITY_COMPONENT_KEY,
        ProvisionedCertificationIdentityBoundary,
    )

    workspace_boundary = ProvisionedCertificationWorkspaceBoundary(
        identity_boundary=identity_boundary,
        workspace_access_resolver=_unavailable_workspace_authority,
    )

    policy = ProvisionedCertificationWorkspacePolicy(
        workspace_boundary=workspace_boundary,
    )

    kernel.bind_component(
        CERTIFICATION_WORKSPACE_POLICY_COMPONENT_KEY,
        policy,
    )

    return policy
