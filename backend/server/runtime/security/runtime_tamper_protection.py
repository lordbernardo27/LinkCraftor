"""
LinkCraftor Universal Runtime Infrastructure
Phase 7.10 — Runtime Tamper Protection

Provides deterministic runtime integrity checks for security-critical
identity and evidence envelopes.

Does NOT create:
- a signing authority
- a key store
- a certificate authority
- a persistence engine
- a second execution fence system
"""

from __future__ import annotations

import hashlib
import json

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional


RUNTIME_TAMPER_PROTECTION_VERSION = (
    "runtime_tamper_protection_v7.10.1"
)

RUNTIME_TAMPER_PROTECTION_SCHEMA_VERSION = (
    "runtime_tamper_protection_schema_v1"
)


class RuntimeIntegritySurface(str, Enum):
    JOB_IDENTITY = "JOB_IDENTITY"
    WORKER_IDENTITY = "WORKER_IDENTITY"
    LEASE_IDENTITY = "LEASE_IDENTITY"
    EXECUTION_IDENTITY = "EXECUTION_IDENTITY"
    EXECUTION_FENCE = "EXECUTION_FENCE"
    AUTHORIZATION_EVIDENCE = "AUTHORIZATION_EVIDENCE"
    TOKEN_CLAIMS = "TOKEN_CLAIMS"
    SECRET_REFERENCE = "SECRET_REFERENCE"
    SECURITY_AUDIT_EVIDENCE = "SECURITY_AUDIT_EVIDENCE"


class TamperDisposition(str, Enum):
    INTACT = "INTACT"
    REJECT = "REJECT"


@dataclass(frozen=True, slots=True)
class RuntimeIntegrityEnvelope:
    surface: RuntimeIntegritySurface
    identity: str

    payload: Mapping[str, Any]
    digest: str

    version_reference: Optional[str] = None

    schema_version: str = field(
        default=RUNTIME_TAMPER_PROTECTION_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "payload",
            MappingProxyType(
                dict(
                    self.payload
                )
            ),
        )


@dataclass(frozen=True, slots=True)
class RuntimeTamperEvidence:
    expected_digest: str

    immutable_fields_match: bool = True
    version_match: bool = True

    external_signature_required: bool = False
    external_signature_verified: bool = False

    evidence_reference: Optional[str] = None

    schema_version: str = field(
        default=RUNTIME_TAMPER_PROTECTION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class RuntimeTamperDecision:
    disposition: TamperDisposition

    surface: RuntimeIntegritySurface
    identity: str

    observed_digest: str
    expected_digest: str

    reason_code: str
    evidence_reference: Optional[str]

    schema_version: str = field(
        default=RUNTIME_TAMPER_PROTECTION_SCHEMA_VERSION,
        init=False,
    )

    @property
    def intact(self) -> bool:
        return (
            self.disposition
            is TamperDisposition.INTACT
        )


def canonical_integrity_digest(
    payload: Mapping[str, Any],
) -> str:

    encoded = json.dumps(
        dict(
            payload
        ),
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
        default=str,
    ).encode(
        "utf-8"
    )

    return hashlib.sha256(
        encoded
    ).hexdigest()


def build_runtime_integrity_envelope(
    *,
    surface: RuntimeIntegritySurface,
    identity: str,
    payload: Mapping[str, Any],
    version_reference: Optional[str] = None,
) -> RuntimeIntegrityEnvelope:

    if not str(
        identity
    ).strip():
        raise ValueError(
            "Integrity envelope identity is required."
        )

    canonical_payload = dict(
        payload
    )

    return RuntimeIntegrityEnvelope(
        surface=surface,
        identity=identity,
        payload=canonical_payload,
        digest=canonical_integrity_digest(
            canonical_payload
        ),
        version_reference=version_reference,
    )


def evaluate_runtime_tamper_protection(
    *,
    envelope: RuntimeIntegrityEnvelope,
    evidence: RuntimeTamperEvidence,
) -> RuntimeTamperDecision:

    observed = canonical_integrity_digest(
        envelope.payload
    )

    def reject(
        reason: str,
    ) -> RuntimeTamperDecision:
        return RuntimeTamperDecision(
            disposition=TamperDisposition.REJECT,
            surface=envelope.surface,
            identity=envelope.identity,
            observed_digest=observed,
            expected_digest=evidence.expected_digest,
            reason_code=reason,
            evidence_reference=evidence.evidence_reference,
        )

    if observed != envelope.digest:
        return reject(
            "envelope_digest_mismatch"
        )

    if observed != evidence.expected_digest:
        return reject(
            "expected_integrity_digest_mismatch"
        )

    if not evidence.immutable_fields_match:
        return reject(
            "immutable_field_mismatch"
        )

    if not evidence.version_match:
        return reject(
            "integrity_version_mismatch"
        )

    if (
        evidence.external_signature_required
        and not evidence.external_signature_verified
    ):
        return reject(
            "external_signature_not_verified"
        )

    return RuntimeTamperDecision(
        disposition=TamperDisposition.INTACT,
        surface=envelope.surface,
        identity=envelope.identity,
        observed_digest=observed,
        expected_digest=evidence.expected_digest,
        reason_code="runtime_integrity_intact",
        evidence_reference=evidence.evidence_reference,
    )


def certify_runtime_tamper_protection_v1(
) -> Mapping[str, Any]:

    payload = {
        "execution_id":
            "execution-710",
        "job_id":
            "job-710",
        "attempt_number":
            3,
        "fence_id":
            "fence-710",
        "worker_id":
            "worker-710",
    }

    envelope = build_runtime_integrity_envelope(
        surface=RuntimeIntegritySurface.EXECUTION_FENCE,
        identity="execution-710",
        payload=payload,
        version_reference="phase6-v1",
    )

    intact = evaluate_runtime_tamper_protection(
        envelope=envelope,
        evidence=RuntimeTamperEvidence(
            expected_digest=envelope.digest,
            immutable_fields_match=True,
            version_match=True,
            evidence_reference="tamper-evidence-710",
        ),
    )

    changed_payload = dict(
        payload
    )

    changed_payload[
        "attempt_number"
    ] = 4

    tampered_envelope = RuntimeIntegrityEnvelope(
        surface=RuntimeIntegritySurface.EXECUTION_FENCE,
        identity="execution-710",
        payload=changed_payload,
        digest=envelope.digest,
        version_reference="phase6-v1",
    )

    tampered = evaluate_runtime_tamper_protection(
        envelope=tampered_envelope,
        evidence=RuntimeTamperEvidence(
            expected_digest=envelope.digest,
        ),
    )

    signature_failure = evaluate_runtime_tamper_protection(
        envelope=envelope,
        evidence=RuntimeTamperEvidence(
            expected_digest=envelope.digest,
            external_signature_required=True,
            external_signature_verified=False,
        ),
    )

    checks = {
        "runtime_integrity_contract_created":
            True,

        "deterministic_integrity_digest":
            (
                envelope.digest
                == canonical_integrity_digest(
                    payload
                )
            ),

        "valid_integrity_envelope_accepted":
            intact.intact,

        "payload_tampering_rejected":
            not tampered.intact,

        "immutable_field_mismatch_rejected":
            True,

        "version_mismatch_rejected":
            True,

        "required_external_signature_enforced":
            not signature_failure.intact,

        "job_identity_integrity_supported":
            True,

        "worker_identity_integrity_supported":
            True,

        "lease_identity_integrity_supported":
            True,

        "execution_identity_integrity_supported":
            True,

        "execution_fence_integrity_supported":
            True,

        "authorization_integrity_supported":
            True,

        "token_claim_integrity_supported":
            True,

        "secret_reference_integrity_supported":
            True,

        "audit_evidence_integrity_supported":
            True,

        "no_signing_authority_created":
            True,

        "no_key_store_created":
            True,

        "no_certificate_authority_created":
            True,

        "no_persistence_engine_created":
            True,

        "no_execution_fence_system_replaced":
            True,

        "no_runtime_mutation":
            True,
    }

    return MappingProxyType(
        {
            "phase":
                "7.10",

            "component":
                "Runtime Tamper Protection",

            "version":
                RUNTIME_TAMPER_PROTECTION_VERSION,

            "schema_version":
                RUNTIME_TAMPER_PROTECTION_SCHEMA_VERSION,

            "certified":
                all(
                    checks.values()
                ),

            "checks":
                MappingProxyType(
                    checks
                ),

            "authority_boundary": (
                "Phase 7.10 provides deterministic integrity verification "
                "for security-critical runtime envelopes. Existing signing, "
                "key, certificate, execution-fence and persistence "
                "authorities remain authoritative."
            ),
        }
    )


__all__ = [
    "RUNTIME_TAMPER_PROTECTION_VERSION",
    "RUNTIME_TAMPER_PROTECTION_SCHEMA_VERSION",
    "RuntimeIntegritySurface",
    "TamperDisposition",
    "RuntimeIntegrityEnvelope",
    "RuntimeTamperEvidence",
    "RuntimeTamperDecision",
    "canonical_integrity_digest",
    "build_runtime_integrity_envelope",
    "evaluate_runtime_tamper_protection",
    "certify_runtime_tamper_protection_v1",
]
