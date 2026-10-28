
"""PT2C.5.5K-L ? Fail-closed entitlement composition.

Not a production credential, signing, or provisioning authority.
"""

from __future__ import annotations

from backend.server.runtime.security.semantic_memory_workspace_entitlement import (
    ProvisionedWorkspaceEntitlementAuthority,
    WorkspaceEntitlementDenied,
)
from backend.server.runtime.security.semantic_memory_verified_membership_provider import (
    VerifiedWorkspaceMembershipResolver,
)


class TrustedEntitlementIntegrationUnavailable(RuntimeError):
    pass


class CertificationEntitlementIntegration:
    def __init__(self, *, membership_resolver):
        if not isinstance(
            membership_resolver, VerifiedWorkspaceMembershipResolver
        ):
            raise TrustedEntitlementIntegrationUnavailable(
                "Verified membership resolver required"
            )

        self._authority = ProvisionedWorkspaceEntitlementAuthority(
            entitlement_resolver=membership_resolver
        )

    def resolve(self, *, identity, workspace_id):
        try:
            return self._authority.resolve(
                identity=identity,
                workspace_id=workspace_id,
            )
        except Exception as exc:
            raise TrustedEntitlementIntegrationUnavailable(
                "Certification entitlement unavailable"
            ) from exc
