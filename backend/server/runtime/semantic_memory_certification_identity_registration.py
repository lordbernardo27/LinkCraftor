"""Fail-closed Universal Runtime registration for certification identity.

PT2B.4B: No credential authority is provisioned by this module.
Registration does not enable authentication or certification consumption.
"""

from __future__ import annotations

from typing import Any

from backend.server.engine.semantic_memory_certification_identity_boundary import (
    CertificationIdentityUnavailable,
    ProvisionedCertificationIdentityBoundary,
)


CERTIFICATION_IDENTITY_COMPONENT_KEY = (
    "semantic_memory.certification.identity_boundary.v1"
)


class CertificationIdentityRegistrationError(RuntimeError):
    """Invalid or duplicate certification identity registration."""


def _unavailable_identity_authority(
    request_lookup: object,
) -> None:
    """Deny resolution until a real authenticated authority is integrated."""
    raise CertificationIdentityUnavailable(
        "Production certification identity authority is not provisioned"
    )


def register_semantic_memory_certification_identity(
    composition: Any,
    **_: Any,
) -> ProvisionedCertificationIdentityBoundary:
    """Register one non-authorizing boundary in the existing runtime kernel.

    No caller-selected identity resolver, issuer, key or workspace
    entitlement is accepted by this registrar.
    """
    kernel = composition.kernel

    if kernel.has_component(CERTIFICATION_IDENTITY_COMPONENT_KEY):
        raise CertificationIdentityRegistrationError(
            "Certification identity boundary already registered"
        )

    boundary = ProvisionedCertificationIdentityBoundary(
        identity_resolver=_unavailable_identity_authority
    )

    kernel.bind_component(
        CERTIFICATION_IDENTITY_COMPONENT_KEY,
        boundary,
    )

    return boundary
