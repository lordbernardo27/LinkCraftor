"""Fail-closed trusted identity boundary for Semantic Memory V2.

This module does not authenticate credentials or create an identity
authority. The identity resolver must be provisioned by a trusted
backend composition root, never by an ordinary verification request.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from types import MappingProxyType


class CertificationIdentityConfigurationError(ValueError):
    """Invalid trusted identity boundary configuration."""


class CertificationIdentityUnavailable(RuntimeError):
    """Trusted authentication evidence is missing or invalid."""


_REQUIRED_FIELDS = (
    "principal_id",
    "principal_type",
    "authentication_established",
    "identity_authority",
    "authentication_reference",
)


class ProvisionedCertificationIdentityBoundary:
    """Resolve verified identity through a provisioned backend authority."""

    def __init__(
        self,
        *,
        identity_resolver: Callable,
    ) -> None:
        if not callable(identity_resolver):
            raise CertificationIdentityConfigurationError(
                "Trusted identity resolver must be callable"
            )

        self._identity_resolver = identity_resolver

    def resolve(self, *, request_lookup: object) -> Mapping:
        """Return immutable verified identity evidence or fail closed."""
        try:
            evidence = self._identity_resolver(request_lookup)
        except Exception as exc:
            raise CertificationIdentityUnavailable(
                "Trusted identity authority unavailable"
            ) from exc

        if not isinstance(evidence, Mapping):
            raise CertificationIdentityUnavailable(
                "Trusted identity evidence missing"
            )

        if set(evidence) != set(_REQUIRED_FIELDS):
            raise CertificationIdentityUnavailable(
                "Trusted identity evidence schema invalid"
            )

        for field in (
            "principal_id",
            "principal_type",
            "identity_authority",
            "authentication_reference",
        ):
            value = evidence[field]
            if not isinstance(value, str) or not value.strip():
                raise CertificationIdentityUnavailable(
                    "Trusted identity evidence invalid: " + field
                )

        if evidence["authentication_established"] is not True:
            raise CertificationIdentityUnavailable(
                "Authentication not established"
            )

        if evidence["principal_type"] not in (
            "USER",
            "SERVICE",
            "WORKER",
            "ADMINISTRATOR",
            "SYSTEM",
        ):
            raise CertificationIdentityUnavailable(
                "Unsupported principal type"
            )

        return MappingProxyType(dict(evidence))
