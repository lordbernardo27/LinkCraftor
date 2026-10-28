"""Fail-closed workspace binding for Semantic Memory certification.

PT2C.2 foundation. This is not a production authorization provider.
An authenticated identity and independent workspace-access evidence
are both required. No client-supplied access claim is trusted.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from types import MappingProxyType

from backend.server.engine.semantic_memory_certification_identity_boundary import (
    ProvisionedCertificationIdentityBoundary,
)


class CertificationWorkspaceAccessDenied(RuntimeError):
    """Workspace access could not be established."""


class CertificationWorkspaceConfigurationError(ValueError):
    """Trusted workspace boundary configuration is invalid."""


class ProvisionedCertificationWorkspaceBoundary:
    """Bind authenticated identity to independently resolved workspace access."""

    def __init__(
        self,
        *,
        identity_boundary: ProvisionedCertificationIdentityBoundary,
        workspace_access_resolver: Callable,
    ) -> None:
        if not isinstance(
            identity_boundary,
            ProvisionedCertificationIdentityBoundary,
        ):
            raise CertificationWorkspaceConfigurationError(
                "Provisioned identity boundary required"
            )

        if not callable(workspace_access_resolver):
            raise CertificationWorkspaceConfigurationError(
                "Workspace access resolver required"
            )

        self._identity_boundary = identity_boundary
        self._workspace_access_resolver = workspace_access_resolver

    def evaluate(
        self,
        *,
        request_lookup: object,
        workspace_id: str,
    ) -> Mapping:
        if (
            not isinstance(workspace_id, str)
            or not workspace_id
            or workspace_id != workspace_id.strip()
        ):
            raise CertificationWorkspaceAccessDenied(
                "Invalid workspace identifier"
            )

        try:
            identity = self._identity_boundary.resolve(
                request_lookup=request_lookup
            )
        except Exception as exc:
            raise CertificationWorkspaceAccessDenied(
                "Authenticated identity unavailable"
            ) from exc

        try:
            evidence = self._workspace_access_resolver(
                identity=identity,
                workspace_id=workspace_id,
            )
        except Exception as exc:
            raise CertificationWorkspaceAccessDenied(
                "Workspace access authority unavailable"
            ) from exc

        if not isinstance(evidence, Mapping):
            raise CertificationWorkspaceAccessDenied(
                "Workspace access evidence missing"
            )

        required = {
            "principal_id",
            "workspace_id",
            "access_granted",
            "authorization_source",
            "authorization_reference",
        }

        if set(evidence) != required:
            raise CertificationWorkspaceAccessDenied(
                "Workspace access evidence schema invalid"
            )

        if (
            type(evidence["principal_id"]) is not str
            or evidence["principal_id"] != identity["principal_id"]
            or type(evidence["workspace_id"]) is not str
            or evidence["workspace_id"] != workspace_id
            or evidence["access_granted"] is not True
        ):
            raise CertificationWorkspaceAccessDenied(
                "Workspace access not established"
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
                raise CertificationWorkspaceAccessDenied(
                    "Workspace authorization provenance invalid"
                )

        return MappingProxyType(
            {
                "principal_id": identity["principal_id"],
                "workspace_id": workspace_id,
                "access_granted": True,
                "authorization_source": evidence["authorization_source"],
                "authorization_reference": evidence[
                    "authorization_reference"
                ],
            }
        )
