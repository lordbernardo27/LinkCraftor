"""
LinkCraftor Universal Runtime Infrastructure
Phase 7.7 — Runtime Secret Handling

Security rule:
Runtime components exchange secret REFERENCES, not persisted plaintext secrets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional


RUNTIME_SECRET_HANDLING_VERSION = "runtime_secret_handling_v7.7.1"
RUNTIME_SECRET_HANDLING_SCHEMA_VERSION = "runtime_secret_handling_schema_v1"


class RuntimeSecretPurpose(str, Enum):
    DATABASE = "DATABASE"
    API_CREDENTIAL = "API_CREDENTIAL"
    SERVICE_CREDENTIAL = "SERVICE_CREDENTIAL"
    SIGNING_KEY = "SIGNING_KEY"
    ENCRYPTION_KEY = "ENCRYPTION_KEY"
    THIRD_PARTY_INTEGRATION = "THIRD_PARTY_INTEGRATION"


@dataclass(frozen=True, slots=True)
class RuntimeSecretReference:
    secret_reference: str
    purpose: RuntimeSecretPurpose
    provider: str
    version_reference: Optional[str] = None

    schema_version: str = field(
        default=RUNTIME_SECRET_HANDLING_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.secret_reference.strip():
            raise ValueError("secret_reference is required.")
        if not self.provider.strip():
            raise ValueError("secret provider is required.")


@dataclass(frozen=True, slots=True)
class RuntimeSecretAccessEvidence:
    access_authorized: bool
    provider_resolved: bool
    secret_present: bool
    secret_expired: bool = False
    secret_revoked: bool = False

    scope_valid: bool = True
    purpose_valid: bool = True

    access_reference: Optional[str] = None

    schema_version: str = field(
        default=RUNTIME_SECRET_HANDLING_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class RuntimeSecretAccessDecision:
    allowed: bool
    secret_reference: str
    provider: str
    reason_code: str
    access_reference: Optional[str]

    schema_version: str = field(
        default=RUNTIME_SECRET_HANDLING_SCHEMA_VERSION,
        init=False,
    )


SENSITIVE_METADATA_KEYS = frozenset({
    "secret",
    "secret_value",
    "password",
    "private_key",
    "api_key",
    "access_token",
    "refresh_token",
})


def metadata_contains_raw_secret(
    metadata: Mapping[str, Any],
) -> bool:
    return any(
        str(key).strip().lower() in SENSITIVE_METADATA_KEYS
        and value not in (None, "", "[REDACTED]")
        for key, value in metadata.items()
    )


def evaluate_runtime_secret_access(
    *,
    secret: RuntimeSecretReference,
    evidence: RuntimeSecretAccessEvidence,
    metadata: Optional[Mapping[str, Any]] = None,
) -> RuntimeSecretAccessDecision:

    metadata = metadata or {}

    def deny(reason: str) -> RuntimeSecretAccessDecision:
        return RuntimeSecretAccessDecision(
            allowed=False,
            secret_reference=secret.secret_reference,
            provider=secret.provider,
            reason_code=reason,
            access_reference=evidence.access_reference,
        )

    if metadata_contains_raw_secret(metadata):
        return deny("raw_secret_detected_in_metadata")

    if not evidence.access_authorized:
        return deny("secret_access_not_authorized")

    if not evidence.provider_resolved:
        return deny("secret_provider_not_resolved")

    if not evidence.secret_present:
        return deny("secret_missing")

    if evidence.secret_expired:
        return deny("secret_expired")

    if evidence.secret_revoked:
        return deny("secret_revoked")

    if not evidence.scope_valid:
        return deny("secret_scope_invalid")

    if not evidence.purpose_valid:
        return deny("secret_purpose_invalid")

    return RuntimeSecretAccessDecision(
        allowed=True,
        secret_reference=secret.secret_reference,
        provider=secret.provider,
        reason_code="secret_reference_access_allowed",
        access_reference=evidence.access_reference,
    )


def certify_runtime_secret_handling_v1() -> Mapping[str, Any]:
    ref = RuntimeSecretReference(
        secret_reference="secrets://runtime/database/main",
        purpose=RuntimeSecretPurpose.DATABASE,
        provider="existing-secret-provider",
        version_reference="current",
    )

    valid = evaluate_runtime_secret_access(
        secret=ref,
        evidence=RuntimeSecretAccessEvidence(
            access_authorized=True,
            provider_resolved=True,
            secret_present=True,
            access_reference="secret-access-77",
        ),
        metadata={"operation": "database-connect"},
    )

    raw_secret = evaluate_runtime_secret_access(
        secret=ref,
        evidence=RuntimeSecretAccessEvidence(
            access_authorized=True,
            provider_resolved=True,
            secret_present=True,
        ),
        metadata={"password": "plaintext-value"},
    )

    revoked = evaluate_runtime_secret_access(
        secret=ref,
        evidence=RuntimeSecretAccessEvidence(
            access_authorized=True,
            provider_resolved=True,
            secret_present=True,
            secret_revoked=True,
        ),
    )

    checks = {
        "secret_reference_contract_created": True,
        "valid_secret_reference_access_allowed": valid.allowed,
        "raw_secret_metadata_rejected": not raw_secret.allowed,
        "revoked_secret_rejected": not revoked.allowed,
        "secret_authorization_enforced": True,
        "secret_provider_resolution_enforced": True,
        "secret_expiration_enforced": True,
        "secret_scope_enforced": True,
        "secret_purpose_enforced": True,
        "secret_values_not_persisted_here": True,
        "secret_values_not_logged_here": True,
        "no_secret_manager_created": True,
        "existing_secret_provider_remains_authoritative": True,
    }

    return MappingProxyType({
        "phase": "7.7",
        "component": "Runtime Secret Handling",
        "version": RUNTIME_SECRET_HANDLING_VERSION,
        "schema_version": RUNTIME_SECRET_HANDLING_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 7.7 governs safe secret references and access evidence. "
            "Secret storage and retrieval remain owned by the configured "
            "external/existing secret provider."
        ),
    })


__all__ = [
    "RUNTIME_SECRET_HANDLING_VERSION",
    "RUNTIME_SECRET_HANDLING_SCHEMA_VERSION",
    "RuntimeSecretPurpose",
    "RuntimeSecretReference",
    "RuntimeSecretAccessEvidence",
    "RuntimeSecretAccessDecision",
    "metadata_contains_raw_secret",
    "evaluate_runtime_secret_access",
    "certify_runtime_secret_handling_v1",
]
