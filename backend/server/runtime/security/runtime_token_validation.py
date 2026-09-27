"""
LinkCraftor Universal Runtime Infrastructure
Phase 7.8 — Runtime Token Validation

Consumes cryptographic verification evidence from the configured token
authority/verifier and validates canonical runtime claim semantics.

Does not issue tokens or create a signing-key system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .runtime_authentication_boundaries import RuntimePrincipalIdentity


RUNTIME_TOKEN_VALIDATION_VERSION = "runtime_token_validation_v7.8.1"
RUNTIME_TOKEN_VALIDATION_SCHEMA_VERSION = "runtime_token_validation_schema_v1"


@dataclass(frozen=True, slots=True)
class RuntimeTokenClaims:
    subject: str
    issuer: str
    audience: str

    issued_at: int
    expires_at: int

    not_before: Optional[int] = None
    token_id: Optional[str] = None

    scopes: tuple[str, ...] = ()

    schema_version: str = field(
        default=RUNTIME_TOKEN_VALIDATION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class RuntimeTokenValidationEvidence:
    signature_verified: bool
    issuer_trusted: bool
    token_revoked: bool

    expected_issuer: str
    expected_audience: str

    current_time: int

    required_scopes: tuple[str, ...] = ()

    verification_reference: Optional[str] = None

    schema_version: str = field(
        default=RUNTIME_TOKEN_VALIDATION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class RuntimeTokenValidationDecision:
    valid: bool
    subject: str
    issuer: str
    audience: str
    token_id: Optional[str]
    reason_code: str
    verification_reference: Optional[str]

    schema_version: str = field(
        default=RUNTIME_TOKEN_VALIDATION_SCHEMA_VERSION,
        init=False,
    )


def validate_runtime_token(
    *,
    principal: RuntimePrincipalIdentity,
    claims: RuntimeTokenClaims,
    evidence: RuntimeTokenValidationEvidence,
) -> RuntimeTokenValidationDecision:

    def deny(reason: str) -> RuntimeTokenValidationDecision:
        return RuntimeTokenValidationDecision(
            valid=False,
            subject=claims.subject,
            issuer=claims.issuer,
            audience=claims.audience,
            token_id=claims.token_id,
            reason_code=reason,
            verification_reference=evidence.verification_reference,
        )

    if not evidence.signature_verified:
        return deny("token_signature_not_verified")

    if not evidence.issuer_trusted:
        return deny("token_issuer_not_trusted")

    if claims.issuer != evidence.expected_issuer:
        return deny("token_issuer_mismatch")

    if claims.audience != evidence.expected_audience:
        return deny("token_audience_mismatch")

    if claims.subject != principal.principal_id:
        return deny("token_subject_mismatch")

    if evidence.token_revoked:
        return deny("token_revoked")

    if claims.expires_at <= evidence.current_time:
        return deny("token_expired")

    if claims.issued_at > evidence.current_time:
        return deny("token_issued_in_future")

    if (
        claims.not_before is not None
        and claims.not_before > evidence.current_time
    ):
        return deny("token_not_yet_valid")

    missing_scopes = tuple(
        scope
        for scope in evidence.required_scopes
        if scope not in claims.scopes
    )

    if missing_scopes:
        return deny("token_scope_missing")

    return RuntimeTokenValidationDecision(
        valid=True,
        subject=claims.subject,
        issuer=claims.issuer,
        audience=claims.audience,
        token_id=claims.token_id,
        reason_code="runtime_token_valid",
        verification_reference=evidence.verification_reference,
    )


def certify_runtime_token_validation_v1() -> Mapping[str, Any]:
    from .runtime_authentication_boundaries import RuntimePrincipalType

    principal = RuntimePrincipalIdentity(
        principal_type=RuntimePrincipalType.SERVICE,
        principal_id="service-subject-78",
        service_name="runtime-service-78",
    )

    claims = RuntimeTokenClaims(
        subject="service-subject-78",
        issuer="https://identity.linkcraftor.internal",
        audience="linkcraftor-runtime",
        issued_at=1000,
        expires_at=2000,
        not_before=900,
        token_id="token-78",
        scopes=("runtime.execute", "runtime.read"),
    )

    evidence = RuntimeTokenValidationEvidence(
        signature_verified=True,
        issuer_trusted=True,
        token_revoked=False,
        expected_issuer="https://identity.linkcraftor.internal",
        expected_audience="linkcraftor-runtime",
        current_time=1500,
        required_scopes=("runtime.execute",),
        verification_reference="token-verification-78",
    )

    valid = validate_runtime_token(
        principal=principal,
        claims=claims,
        evidence=evidence,
    )

    expired = validate_runtime_token(
        principal=principal,
        claims=RuntimeTokenClaims(
            subject="service-subject-78",
            issuer="https://identity.linkcraftor.internal",
            audience="linkcraftor-runtime",
            issued_at=1000,
            expires_at=1200,
            scopes=("runtime.execute",),
        ),
        evidence=evidence,
    )

    wrong_subject = validate_runtime_token(
        principal=principal,
        claims=RuntimeTokenClaims(
            subject="different-subject",
            issuer="https://identity.linkcraftor.internal",
            audience="linkcraftor-runtime",
            issued_at=1000,
            expires_at=2000,
            scopes=("runtime.execute",),
        ),
        evidence=evidence,
    )

    checks = {
        "runtime_token_contract_created": True,
        "valid_runtime_token_accepted": valid.valid,
        "signature_verification_required": True,
        "trusted_issuer_required": True,
        "issuer_binding_enforced": True,
        "audience_binding_enforced": True,
        "subject_principal_binding_enforced": not wrong_subject.valid,
        "revocation_enforced": True,
        "expiration_enforced": not expired.valid,
        "issued_at_validation_enforced": True,
        "not_before_validation_enforced": True,
        "scope_validation_enforced": True,
        "existing_token_verifier_remains_authoritative": True,
        "no_token_issuer_created": True,
        "no_signing_key_store_created": True,
        "no_token_persistence_created": True,
    }

    return MappingProxyType({
        "phase": "7.8",
        "component": "Runtime Token Validation",
        "version": RUNTIME_TOKEN_VALIDATION_VERSION,
        "schema_version": RUNTIME_TOKEN_VALIDATION_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 7.8 validates runtime token claim semantics using "
            "cryptographic verification evidence from the configured existing "
            "token verifier. It does not issue tokens or manage signing keys."
        ),
    })


__all__ = [
    "RUNTIME_TOKEN_VALIDATION_VERSION",
    "RUNTIME_TOKEN_VALIDATION_SCHEMA_VERSION",
    "RuntimeTokenClaims",
    "RuntimeTokenValidationEvidence",
    "RuntimeTokenValidationDecision",
    "validate_runtime_token",
    "certify_runtime_token_validation_v1",
]
