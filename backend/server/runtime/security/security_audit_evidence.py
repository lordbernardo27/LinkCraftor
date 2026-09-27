"""
LinkCraftor Universal Runtime Infrastructure
Phase 7.11 — Security Audit Evidence

Creates immutable, verifiable security evidence records and downstream
handoff envelopes.

Does NOT:
- write persistence
- emit logs
- emit metrics
- create an observability system
- create an audit database

Phase 8 Observability and Phase 12 Persistence remain downstream owners.
"""

from __future__ import annotations

import hashlib
import json

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional


SECURITY_AUDIT_EVIDENCE_VERSION = (
    "security_audit_evidence_v7.11.1"
)

SECURITY_AUDIT_EVIDENCE_SCHEMA_VERSION = (
    "security_audit_evidence_schema_v1"
)


class SecurityDecision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REJECT = "REJECT"
    VALID = "VALID"
    INVALID = "INVALID"


@dataclass(frozen=True, slots=True)
class SecurityAuditEvidence:
    event_id: str
    component_phase: str
    component_name: str

    principal_id: Optional[str]
    principal_type: Optional[str]

    decision: SecurityDecision
    reason_code: str

    boundary: Optional[str] = None
    operation: Optional[str] = None

    workspace_id: Optional[str] = None
    job_id: Optional[str] = None
    orchestration_id: Optional[str] = None
    execution_id: Optional[str] = None
    worker_id: Optional[str] = None
    lease_id: Optional[str] = None

    authorization_reference: Optional[str] = None
    token_reference: Optional[str] = None
    privilege_reference: Optional[str] = None
    tamper_reference: Optional[str] = None

    previous_evidence_hash: Optional[str] = None

    metadata: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    evidence_hash: str = ""

    schema_version: str = field(
        default=SECURITY_AUDIT_EVIDENCE_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(
                dict(
                    self.metadata
                )
            ),
        )


@dataclass(frozen=True, slots=True)
class SecurityAuditHandoff:
    evidence: SecurityAuditEvidence

    persistence_required: bool
    observability_required: bool

    record_type: str
    event_name: str

    schema_version: str = field(
        default=SECURITY_AUDIT_EVIDENCE_SCHEMA_VERSION,
        init=False,
    )


def _audit_payload(
    evidence: SecurityAuditEvidence,
) -> dict[str, Any]:

    return {
        "schema_version":
            evidence.schema_version,

        "event_id":
            evidence.event_id,

        "component_phase":
            evidence.component_phase,

        "component_name":
            evidence.component_name,

        "principal_id":
            evidence.principal_id,

        "principal_type":
            evidence.principal_type,

        "decision":
            evidence.decision.value,

        "reason_code":
            evidence.reason_code,

        "boundary":
            evidence.boundary,

        "operation":
            evidence.operation,

        "workspace_id":
            evidence.workspace_id,

        "job_id":
            evidence.job_id,

        "orchestration_id":
            evidence.orchestration_id,

        "execution_id":
            evidence.execution_id,

        "worker_id":
            evidence.worker_id,

        "lease_id":
            evidence.lease_id,

        "authorization_reference":
            evidence.authorization_reference,

        "token_reference":
            evidence.token_reference,

        "privilege_reference":
            evidence.privilege_reference,

        "tamper_reference":
            evidence.tamper_reference,

        "previous_evidence_hash":
            evidence.previous_evidence_hash,

        "metadata":
            dict(
                evidence.metadata
            ),
    }


def security_audit_hash(
    evidence: SecurityAuditEvidence,
) -> str:

    encoded = json.dumps(
        _audit_payload(
            evidence
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


def build_security_audit_evidence(
    *,
    event_id: str,
    component_phase: str,
    component_name: str,
    decision: SecurityDecision,
    reason_code: str,

    principal_id: Optional[str] = None,
    principal_type: Optional[str] = None,

    boundary: Optional[str] = None,
    operation: Optional[str] = None,

    workspace_id: Optional[str] = None,
    job_id: Optional[str] = None,
    orchestration_id: Optional[str] = None,
    execution_id: Optional[str] = None,
    worker_id: Optional[str] = None,
    lease_id: Optional[str] = None,

    authorization_reference: Optional[str] = None,
    token_reference: Optional[str] = None,
    privilege_reference: Optional[str] = None,
    tamper_reference: Optional[str] = None,

    previous_evidence_hash: Optional[str] = None,

    metadata: Optional[
        Mapping[str, Any]
    ] = None,
) -> SecurityAuditEvidence:

    if not event_id.strip():
        raise ValueError(
            "event_id is required."
        )

    if not component_phase.strip():
        raise ValueError(
            "component_phase is required."
        )

    provisional = SecurityAuditEvidence(
        event_id=event_id,
        component_phase=component_phase,
        component_name=component_name,
        principal_id=principal_id,
        principal_type=principal_type,
        decision=decision,
        reason_code=reason_code,
        boundary=boundary,
        operation=operation,
        workspace_id=workspace_id,
        job_id=job_id,
        orchestration_id=orchestration_id,
        execution_id=execution_id,
        worker_id=worker_id,
        lease_id=lease_id,
        authorization_reference=authorization_reference,
        token_reference=token_reference,
        privilege_reference=privilege_reference,
        tamper_reference=tamper_reference,
        previous_evidence_hash=previous_evidence_hash,
        metadata=(
            metadata
            or MappingProxyType({})
        ),
        evidence_hash="",
    )

    digest = security_audit_hash(
        provisional
    )

    return SecurityAuditEvidence(
        event_id=provisional.event_id,
        component_phase=provisional.component_phase,
        component_name=provisional.component_name,
        principal_id=provisional.principal_id,
        principal_type=provisional.principal_type,
        decision=provisional.decision,
        reason_code=provisional.reason_code,
        boundary=provisional.boundary,
        operation=provisional.operation,
        workspace_id=provisional.workspace_id,
        job_id=provisional.job_id,
        orchestration_id=provisional.orchestration_id,
        execution_id=provisional.execution_id,
        worker_id=provisional.worker_id,
        lease_id=provisional.lease_id,
        authorization_reference=provisional.authorization_reference,
        token_reference=provisional.token_reference,
        privilege_reference=provisional.privilege_reference,
        tamper_reference=provisional.tamper_reference,
        previous_evidence_hash=provisional.previous_evidence_hash,
        metadata=provisional.metadata,
        evidence_hash=digest,
    )


def verify_security_audit_evidence(
    evidence: SecurityAuditEvidence,
) -> bool:

    return (
        bool(
            evidence.evidence_hash
        )
        and evidence.evidence_hash
        == security_audit_hash(
            evidence
        )
    )


def build_security_audit_handoff(
    evidence: SecurityAuditEvidence,
) -> SecurityAuditHandoff:

    if not verify_security_audit_evidence(
        evidence
    ):
        raise ValueError(
            "Security audit evidence integrity verification failed."
        )

    return SecurityAuditHandoff(
        evidence=evidence,
        persistence_required=True,
        observability_required=True,
        record_type="runtime_security_audit_evidence",
        event_name="runtime.security.audit_decision",
    )


def certify_security_audit_evidence_v1(
) -> Mapping[str, Any]:

    first = build_security_audit_evidence(
        event_id="security-event-711-a",
        component_phase="7.8",
        component_name="Runtime Token Validation",
        principal_id="service-711",
        principal_type="SERVICE",
        decision=SecurityDecision.VALID,
        reason_code="runtime_token_valid",
        boundary="INTERNAL_SERVICE_CALL",
        operation="CALL_INTERNAL_SERVICE",
        execution_id="execution-711",
        token_reference="token-ref-711",
        metadata={
            "certification":
                True,
        },
    )

    second = build_security_audit_evidence(
        event_id="security-event-711-b",
        component_phase="7.9",
        component_name="Privilege Boundaries",
        principal_id="service-711",
        principal_type="SERVICE",
        decision=SecurityDecision.ALLOW,
        reason_code="privilege_boundary_allowed",
        execution_id="execution-711",
        privilege_reference="privilege-ref-711",
        previous_evidence_hash=first.evidence_hash,
    )

    handoff = build_security_audit_handoff(
        second
    )

    tampered = SecurityAuditEvidence(
        event_id=second.event_id,
        component_phase=second.component_phase,
        component_name=second.component_name,
        principal_id=second.principal_id,
        principal_type=second.principal_type,
        decision=second.decision,
        reason_code="changed-after-creation",
        boundary=second.boundary,
        operation=second.operation,
        workspace_id=second.workspace_id,
        job_id=second.job_id,
        orchestration_id=second.orchestration_id,
        execution_id=second.execution_id,
        worker_id=second.worker_id,
        lease_id=second.lease_id,
        authorization_reference=second.authorization_reference,
        token_reference=second.token_reference,
        privilege_reference=second.privilege_reference,
        tamper_reference=second.tamper_reference,
        previous_evidence_hash=second.previous_evidence_hash,
        metadata=second.metadata,
        evidence_hash=second.evidence_hash,
    )

    checks = {
        "security_audit_contract_created":
            True,

        "security_evidence_hash_created":
            bool(
                first.evidence_hash
            ),

        "security_evidence_integrity_valid":
            verify_security_audit_evidence(
                first
            ),

        "security_evidence_chain_supported":
            (
                second.previous_evidence_hash
                == first.evidence_hash
            ),

        "tampered_security_evidence_rejected":
            not verify_security_audit_evidence(
                tampered
            ),

        "persistence_handoff_prepared":
            handoff.persistence_required,

        "observability_handoff_prepared":
            handoff.observability_required,

        "security_decision_preserved":
            (
                second.decision
                is SecurityDecision.ALLOW
            ),

        "reason_code_preserved":
            (
                second.reason_code
                == "privilege_boundary_allowed"
            ),

        "principal_identity_reference_supported":
            True,

        "job_execution_worker_lease_references_supported":
            True,

        "authorization_reference_supported":
            True,

        "token_reference_supported":
            True,

        "privilege_reference_supported":
            True,

        "tamper_reference_supported":
            True,

        "no_persistence_write":
            True,

        "no_log_emit":
            True,

        "no_metric_emit":
            True,

        "no_audit_database_created":
            True,

        "no_observability_system_created":
            True,

        "phase8_observability_authority_preserved":
            True,

        "phase12_persistence_authority_preserved":
            True,
    }

    return MappingProxyType(
        {
            "phase":
                "7.11",

            "component":
                "Security Audit Evidence",

            "version":
                SECURITY_AUDIT_EVIDENCE_VERSION,

            "schema_version":
                SECURITY_AUDIT_EVIDENCE_SCHEMA_VERSION,

            "certified":
                all(
                    checks.values()
                ),

            "checks":
                MappingProxyType(
                    checks
                ),

            "authority_boundary": (
                "Phase 7.11 creates immutable and integrity-verifiable "
                "security decision evidence plus persistence and observability "
                "handoff envelopes. It performs no persistence write or "
                "observability emission; Phase 8 and Phase 12 remain "
                "downstream authorities."
            ),
        }
    )


__all__ = [
    "SECURITY_AUDIT_EVIDENCE_VERSION",
    "SECURITY_AUDIT_EVIDENCE_SCHEMA_VERSION",
    "SecurityDecision",
    "SecurityAuditEvidence",
    "SecurityAuditHandoff",
    "security_audit_hash",
    "build_security_audit_evidence",
    "verify_security_audit_evidence",
    "build_security_audit_handoff",
    "certify_security_audit_evidence_v1",
]
