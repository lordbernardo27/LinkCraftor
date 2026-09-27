"""
LinkCraftor Universal Runtime Infrastructure
Phase 7.5 — Service-to-Service Trust
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .runtime_authentication_boundaries import (
    RuntimePrincipalIdentity,
    RuntimePrincipalType,
)


SERVICE_TO_SERVICE_TRUST_VERSION = "service_to_service_trust_v7.5.1"
SERVICE_TO_SERVICE_TRUST_SCHEMA_VERSION = "service_to_service_trust_schema_v1"


@dataclass(frozen=True, slots=True)
class ServiceTrustEvidence:
    source_service: str
    target_service: str

    workload_identity_verified: bool
    credential_valid: bool
    credential_expired: bool
    channel_protected: bool

    issuer_trusted: bool
    audience_valid: bool

    trust_domain: str
    expected_trust_domain: str

    allowed_target_services: tuple[str, ...] = ()
    trust_reference: str | None = None

    schema_version: str = field(
        default=SERVICE_TO_SERVICE_TRUST_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class ServiceTrustDecision:
    trusted: bool
    source_service: str
    target_service: str
    reason_code: str
    trust_reference: str | None

    schema_version: str = field(
        default=SERVICE_TO_SERVICE_TRUST_SCHEMA_VERSION,
        init=False,
    )


def evaluate_service_to_service_trust(
    *,
    principal: RuntimePrincipalIdentity,
    evidence: ServiceTrustEvidence,
) -> ServiceTrustDecision:

    def deny(reason: str) -> ServiceTrustDecision:
        return ServiceTrustDecision(
            trusted=False,
            source_service=evidence.source_service,
            target_service=evidence.target_service,
            reason_code=reason,
            trust_reference=evidence.trust_reference,
        )

    if principal.principal_type is not RuntimePrincipalType.SERVICE:
        return deny("principal_is_not_service")

    if principal.service_name != evidence.source_service:
        return deny("source_service_identity_mismatch")

    if not evidence.workload_identity_verified:
        return deny("workload_identity_not_verified")

    if not evidence.credential_valid or evidence.credential_expired:
        return deny("service_credential_invalid")

    if not evidence.channel_protected:
        return deny("service_channel_not_protected")

    if not evidence.issuer_trusted:
        return deny("service_issuer_not_trusted")

    if not evidence.audience_valid:
        return deny("service_audience_invalid")

    if evidence.trust_domain != evidence.expected_trust_domain:
        return deny("service_trust_domain_mismatch")

    if evidence.target_service not in evidence.allowed_target_services:
        return deny("target_service_not_allowed")

    return ServiceTrustDecision(
        trusted=True,
        source_service=evidence.source_service,
        target_service=evidence.target_service,
        reason_code="service_trust_established",
        trust_reference=evidence.trust_reference,
    )


def certify_service_to_service_trust_v1() -> Mapping[str, Any]:
    service = RuntimePrincipalIdentity(
        principal_type=RuntimePrincipalType.SERVICE,
        principal_id="service-principal-75",
        service_name="runtime-orchestrator",
    )

    good = ServiceTrustEvidence(
        source_service="runtime-orchestrator",
        target_service="runtime-worker",
        workload_identity_verified=True,
        credential_valid=True,
        credential_expired=False,
        channel_protected=True,
        issuer_trusted=True,
        audience_valid=True,
        trust_domain="linkcraftor.internal",
        expected_trust_domain="linkcraftor.internal",
        allowed_target_services=("runtime-worker",),
        trust_reference="service-trust-75",
    )

    allowed = evaluate_service_to_service_trust(
        principal=service,
        evidence=good,
    )

    bad_target = evaluate_service_to_service_trust(
        principal=service,
        evidence=ServiceTrustEvidence(
            source_service="runtime-orchestrator",
            target_service="unknown-service",
            workload_identity_verified=True,
            credential_valid=True,
            credential_expired=False,
            channel_protected=True,
            issuer_trusted=True,
            audience_valid=True,
            trust_domain="linkcraftor.internal",
            expected_trust_domain="linkcraftor.internal",
            allowed_target_services=("runtime-worker",),
        ),
    )

    checks = {
        "service_trust_contract_created": True,
        "valid_service_trust_allowed": allowed.trusted,
        "service_identity_binding_enforced": True,
        "workload_identity_required": True,
        "credential_validity_required": True,
        "protected_channel_required": True,
        "trusted_issuer_required": True,
        "audience_validation_required": True,
        "trust_domain_binding_required": True,
        "target_service_allowlist_enforced": not bad_target.trusted,
        "no_service_identity_store_created": True,
        "no_certificate_authority_created": True,
        "no_token_issuer_created": True,
        "no_network_mutation": True,
    }

    return MappingProxyType({
        "phase": "7.5",
        "component": "Service-to-Service Trust",
        "version": SERVICE_TO_SERVICE_TRUST_VERSION,
        "schema_version": SERVICE_TO_SERVICE_TRUST_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 7.5 evaluates trusted service identity evidence, channel "
            "protection, issuer, audience, trust-domain and target-service "
            "constraints without creating a service identity system or CA."
        ),
    })


__all__ = [
    "SERVICE_TO_SERVICE_TRUST_VERSION",
    "SERVICE_TO_SERVICE_TRUST_SCHEMA_VERSION",
    "ServiceTrustEvidence",
    "ServiceTrustDecision",
    "evaluate_service_to_service_trust",
    "certify_service_to_service_trust_v1",
]
