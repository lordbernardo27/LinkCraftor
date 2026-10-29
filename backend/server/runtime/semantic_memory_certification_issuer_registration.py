
"""PT4 ? Fail-closed Semantic Memory issuer bootstrap registration.

This establishes a backend-owned registration point only.
No production issuer, signing authority, or trust registry is provisioned.
"""

from __future__ import annotations


CERTIFICATION_ISSUER_COMPONENT_KEY = (
    "semantic_memory.certification.issuer_authority.v1"
)


class CertificationIssuerRegistrationError(RuntimeError):
    pass


class CertificationIssuerUnavailable(RuntimeError):
    pass


class UnprovisionedCertificationIssuerAuthority:
    """Deny issuance and verification until trusted bootstrap exists."""

    __slots__ = ()

    def issue(self, **kwargs):
        raise CertificationIssuerUnavailable(
            "Production Semantic Memory issuer not provisioned"
        )

    def verify(self, **kwargs):
        raise CertificationIssuerUnavailable(
            "Production Semantic Memory issuer not provisioned"
        )


def register_semantic_memory_certification_issuer(
    composition,
) -> UnprovisionedCertificationIssuerAuthority:
    """Bind a deny-only authority without accepting caller configuration."""

    kernel = composition.kernel

    if kernel.has_component(CERTIFICATION_ISSUER_COMPONENT_KEY):
        raise CertificationIssuerRegistrationError(
            "Certification issuer authority already registered"
        )

    authority = UnprovisionedCertificationIssuerAuthority()

    kernel.bind_component(
        CERTIFICATION_ISSUER_COMPONENT_KEY,
        authority,
    )

    return authority
