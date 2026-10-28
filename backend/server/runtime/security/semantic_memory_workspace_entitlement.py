"""Semantic Memory workspace entitlement contract.

Fail-closed foundation. No production identity or membership
provider is provisioned by this module.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from types import MappingProxyType


CERTIFICATION_ENTITLEMENT_OPERATION = (
    "SEMANTIC_MEMORY_CERTIFICATION_CONTEXT_READ"
)


class WorkspaceEntitlementDenied(RuntimeError):
    """Authoritative workspace entitlement is unavailable or denied."""


class WorkspaceEntitlementConfigurationError(ValueError):
    """Workspace entitlement provider configuration is invalid."""


class ProvisionedWorkspaceEntitlementAuthority:
    """Validate workspace access evidence returned by a provisioned authority."""

    def __init__(self, *, entitlement_resolver: Callable) -> None:
        if not callable(entitlement_resolver):
            raise WorkspaceEntitlementConfigurationError(
                "Trusted entitlement resolver required"
            )
        self._resolver = entitlement_resolver

    def resolve(
        self,
        *,
        identity: Mapping,
        workspace_id: str,
        operation: str = CERTIFICATION_ENTITLEMENT_OPERATION,
    ) -> Mapping:
        if not isinstance(identity, Mapping):
            raise WorkspaceEntitlementDenied("Identity evidence missing")

        principal_id = identity.get("principal_id")

        if (
            type(principal_id) is not str
            or not principal_id.strip()
            or principal_id != principal_id.strip()
            or identity.get("authentication_established") is not True
        ):
            raise WorkspaceEntitlementDenied(
                "Authenticated principal unavailable"
            )

        if (
            type(workspace_id) is not str
            or not workspace_id.strip()
            or workspace_id != workspace_id.strip()
        ):
            raise WorkspaceEntitlementDenied(
                "Workspace identifier invalid"
            )

        if operation != CERTIFICATION_ENTITLEMENT_OPERATION:
            raise WorkspaceEntitlementDenied(
                "Unsupported entitlement operation"
            )

        try:
            evidence = self._resolver(
                principal_id=principal_id,
                workspace_id=workspace_id,
                operation=operation,
            )
        except Exception as exc:
            raise WorkspaceEntitlementDenied(
                "Entitlement authority unavailable"
            ) from exc

        if not isinstance(evidence, Mapping):
            raise WorkspaceEntitlementDenied(
                "Entitlement evidence unavailable"
            )

        required = {
            "principal_id",
            "workspace_id",
            "operation",
            "access_granted",
            "authorization_source",
            "authorization_reference",
        }

        if set(evidence) != required:
            raise WorkspaceEntitlementDenied(
                "Entitlement evidence schema invalid"
            )

        if (
            type(evidence["principal_id"]) is not str
            or evidence["principal_id"] != principal_id
            or type(evidence["workspace_id"]) is not str
            or evidence["workspace_id"] != workspace_id
            or type(evidence["operation"]) is not str
            or evidence["operation"] != operation
            or evidence["access_granted"] is not True
        ):
            raise WorkspaceEntitlementDenied(
                "Workspace entitlement not established"
            )

        for field in (
            "authorization_source",
            "authorization_reference",
        ):
            value = evidence[field]
            if (
                type(value) is not str
                or not value.strip()
                or value != value.strip()
            ):
                raise WorkspaceEntitlementDenied(
                    "Entitlement provenance invalid"
                )

        return MappingProxyType({
            "principal_id": principal_id,
            "workspace_id": workspace_id,
            "operation": operation,
            "access_granted": True,
            "authorization_source": evidence["authorization_source"],
            "authorization_reference": evidence[
                "authorization_reference"
            ],
        })
