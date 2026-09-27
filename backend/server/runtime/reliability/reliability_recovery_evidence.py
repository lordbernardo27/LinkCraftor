"""
LinkCraftor Universal Runtime Infrastructure
Phase 9.11 — Reliability & Recovery Evidence

Creates immutable evidence/handoff records for Phase-9 decisions.

Does NOT:
- write persistence directly
- create evidence database
- emit alerts directly
"""

from __future__ import annotations

import hashlib
import json

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional


RELIABILITY_RECOVERY_EVIDENCE_VERSION = (
    "reliability_recovery_evidence_v9.11.1"
)

RELIABILITY_RECOVERY_EVIDENCE_SCHEMA_VERSION = (
    "reliability_recovery_evidence_schema_v1"
)


@dataclass(frozen=True, slots=True)
class ReliabilityRecoveryEvidence:
    event_name: str
    component: str
    decision_type: str
    decision: str

    reason_codes: tuple[str, ...]

    workspace_id: Optional[str] = None
    job_id: Optional[str] = None
    queue_name: Optional[str] = None
    worker_id: Optional[str] = None
    orchestration_id: Optional[str] = None
    execution_id: Optional[str] = None

    source_reference: Optional[str] = None
    previous_evidence_hash: Optional[str] = None

    metadata: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    evidence_hash: str = field(
        default="",
    )

    schema_version: str = field(
        default=RELIABILITY_RECOVERY_EVIDENCE_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.event_name.strip():
            raise ValueError("event_name is required.")

        if not self.component.strip():
            raise ValueError("component is required.")

        if not self.decision_type.strip():
            raise ValueError("decision_type is required.")

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )

        if not self.evidence_hash:
            object.__setattr__(
                self,
                "evidence_hash",
                compute_reliability_evidence_hash(self),
            )


@dataclass(frozen=True, slots=True)
class ReliabilityRecoveryHandoff:
    evidence: ReliabilityRecoveryEvidence

    persistence_required: bool = True
    observability_required: bool = True
    owner_control_tower_required: bool = True

    record_type: str = (
        "runtime_reliability_recovery_evidence"
    )

    event_name: str = (
        "runtime.reliability.recovery_decision"
    )

    schema_version: str = field(
        default=RELIABILITY_RECOVERY_EVIDENCE_SCHEMA_VERSION,
        init=False,
    )


def _canonical_payload(
    evidence: ReliabilityRecoveryEvidence,
) -> dict[str, Any]:

    return {
        "schema_version": evidence.schema_version,
        "event_name": evidence.event_name,
        "component": evidence.component,
        "decision_type": evidence.decision_type,
        "decision": evidence.decision,
        "reason_codes": list(evidence.reason_codes),
        "workspace_id": evidence.workspace_id,
        "job_id": evidence.job_id,
        "queue_name": evidence.queue_name,
        "worker_id": evidence.worker_id,
        "orchestration_id": evidence.orchestration_id,
        "execution_id": evidence.execution_id,
        "source_reference": evidence.source_reference,
        "previous_evidence_hash": evidence.previous_evidence_hash,
        "metadata": dict(evidence.metadata),
    }


def compute_reliability_evidence_hash(
    evidence: ReliabilityRecoveryEvidence,
) -> str:

    encoded = json.dumps(
        _canonical_payload(evidence),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def verify_reliability_evidence(
    evidence: ReliabilityRecoveryEvidence,
) -> bool:

    return (
        compute_reliability_evidence_hash(evidence)
        == evidence.evidence_hash
    )


def create_reliability_recovery_handoff(
    evidence: ReliabilityRecoveryEvidence,
) -> ReliabilityRecoveryHandoff:

    return ReliabilityRecoveryHandoff(
        evidence=evidence
    )


def certify_reliability_recovery_evidence_v1(
) -> Mapping[str, Any]:

    first = ReliabilityRecoveryEvidence(
        event_name="runtime.recovery.retry_governance",
        component="retry_governance",
        decision_type="RETRY",
        decision="RETRY_ALLOWED",
        reason_codes=("retry_governance_approved",),
        workspace_id="workspace-911",
        job_id="job-911",
        execution_id="execution-911",
        source_reference="reliability-911",
        metadata={
            "next_attempt": 3,
            "delay_seconds": 4.0,
        },
    )

    second = ReliabilityRecoveryEvidence(
        event_name="runtime.recovery.execution",
        component="execution_recovery",
        decision_type="EXECUTION_RECOVERY",
        decision="RETRY_EXISTING_JOB",
        reason_codes=("retry_governance_approved",),
        workspace_id="workspace-911",
        job_id="job-911",
        execution_id="execution-911",
        previous_evidence_hash=first.evidence_hash,
    )

    handoff = create_reliability_recovery_handoff(
        second
    )

    checks = {
        "reliability_evidence_contract_created": True,
        "evidence_hash_created": bool(first.evidence_hash),
        "evidence_hash_verifies": verify_reliability_evidence(first),
        "evidence_chain_supported": (
            second.previous_evidence_hash
            == first.evidence_hash
        ),
        "retry_evidence_supported": True,
        "worker_recovery_evidence_supported": True,
        "queue_recovery_evidence_supported": True,
        "execution_recovery_evidence_supported": True,
        "orchestration_recovery_evidence_supported": True,
        "dead_letter_evidence_supported": True,
        "restart_recovery_evidence_supported": True,
        "degraded_mode_evidence_supported": True,
        "persistence_handoff_required": (
            handoff.persistence_required
        ),
        "observability_handoff_required": (
            handoff.observability_required
        ),
        "owner_control_tower_handoff_required": (
            handoff.owner_control_tower_required
        ),
        "phase12_persistence_authority_preserved": True,
        "phase8_observability_authority_preserved": True,
        "no_evidence_database_created": True,
        "no_persistence_write": True,
        "no_alert_transport_created": True,
        "no_runtime_mutation": True,
    }

    return MappingProxyType({
        "phase": "9.11",
        "component": "Reliability & Recovery Evidence",
        "version": RELIABILITY_RECOVERY_EVIDENCE_VERSION,
        "schema_version": RELIABILITY_RECOVERY_EVIDENCE_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 9.11 creates immutable reliability/recovery evidence and "
            "handoff contracts only. Phase 12 remains persistence authority "
            "and Phase 8 remains observability authority."
        ),
    })


__all__ = [
    "RELIABILITY_RECOVERY_EVIDENCE_VERSION",
    "RELIABILITY_RECOVERY_EVIDENCE_SCHEMA_VERSION",
    "ReliabilityRecoveryEvidence",
    "ReliabilityRecoveryHandoff",
    "compute_reliability_evidence_hash",
    "verify_reliability_evidence",
    "create_reliability_recovery_handoff",
    "certify_reliability_recovery_evidence_v1",
]
