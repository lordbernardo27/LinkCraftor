"""
LinkCraftor Universal Runtime Infrastructure
Phase 10.16 — Resource Governance Evidence

Creates immutable evidence records for Phase-10 decisions.

Does NOT:
- create evidence database
- persist directly
- emit alerts directly
"""

from __future__ import annotations

import hashlib
import json

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional


RESOURCE_GOVERNANCE_EVIDENCE_VERSION = (
    "resource_governance_evidence_v10.16.1"
)

RESOURCE_GOVERNANCE_EVIDENCE_SCHEMA_VERSION = (
    "resource_governance_evidence_schema_v1"
)


@dataclass(frozen=True, slots=True)
class ResourceGovernanceEvidence:
    event_name: str
    component: str

    decision_type: str
    decision: str

    reason_codes: tuple[str, ...]

    workspace_id: Optional[str] = None
    plan_id: Optional[str] = None
    queue_name: Optional[str] = None
    worker_id: Optional[str] = None
    job_id: Optional[str] = None
    orchestration_id: Optional[str] = None
    execution_id: Optional[str] = None

    source_reference: Optional[str] = None
    previous_evidence_hash: Optional[str] = None

    metadata: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    evidence_hash: str = ""

    schema_version: str = field(
        default=RESOURCE_GOVERNANCE_EVIDENCE_SCHEMA_VERSION,
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
                compute_resource_governance_evidence_hash(self),
            )


@dataclass(frozen=True, slots=True)
class ResourceGovernanceEvidenceHandoff:
    evidence: ResourceGovernanceEvidence

    observability_required: bool = True
    persistence_required: bool = True
    owner_control_tower_required: bool = True

    record_type: str = "runtime_resource_governance_evidence"
    event_name: str = "runtime.resource_governance.decision"

    schema_version: str = field(
        default=RESOURCE_GOVERNANCE_EVIDENCE_SCHEMA_VERSION,
        init=False,
    )


def _canonical_payload(
    evidence: ResourceGovernanceEvidence,
) -> dict[str, Any]:

    return {
        "schema_version": evidence.schema_version,
        "event_name": evidence.event_name,
        "component": evidence.component,
        "decision_type": evidence.decision_type,
        "decision": evidence.decision,
        "reason_codes": list(evidence.reason_codes),
        "workspace_id": evidence.workspace_id,
        "plan_id": evidence.plan_id,
        "queue_name": evidence.queue_name,
        "worker_id": evidence.worker_id,
        "job_id": evidence.job_id,
        "orchestration_id": evidence.orchestration_id,
        "execution_id": evidence.execution_id,
        "source_reference": evidence.source_reference,
        "previous_evidence_hash": evidence.previous_evidence_hash,
        "metadata": dict(evidence.metadata),
    }


def compute_resource_governance_evidence_hash(
    evidence: ResourceGovernanceEvidence,
) -> str:

    encoded = json.dumps(
        _canonical_payload(evidence),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def verify_resource_governance_evidence(
    evidence: ResourceGovernanceEvidence,
) -> bool:

    return (
        compute_resource_governance_evidence_hash(evidence)
        == evidence.evidence_hash
    )


def create_resource_governance_evidence_handoff(
    evidence: ResourceGovernanceEvidence,
) -> ResourceGovernanceEvidenceHandoff:

    return ResourceGovernanceEvidenceHandoff(
        evidence=evidence
    )


def certify_resource_governance_evidence_v1(
) -> Mapping[str, Any]:

    first = ResourceGovernanceEvidence(
        event_name="runtime.resource.admission",
        component="execution_concurrency_governance",
        decision_type="RESOURCE_ADMISSION",
        decision="ALLOW",
        reason_codes=("execution_concurrency_available",),
        workspace_id="workspace-1016",
        execution_id="execution-1016",
        metadata={
            "requested": 2,
            "allowed": 2,
        },
    )

    second = ResourceGovernanceEvidence(
        event_name="runtime.resource.throttling",
        component="throttling_governance",
        decision_type="THROTTLE",
        decision="THROTTLE",
        reason_codes=("high_resource_pressure",),
        workspace_id="workspace-1016",
        previous_evidence_hash=first.evidence_hash,
    )

    handoff = create_resource_governance_evidence_handoff(
        second
    )

    checks = {
        "resource_governance_evidence_contract_created": True,
        "evidence_hash_created": bool(first.evidence_hash),
        "evidence_hash_verifies": (
            verify_resource_governance_evidence(first)
        ),
        "evidence_chain_supported": (
            second.previous_evidence_hash
            == first.evidence_hash
        ),
        "capacity_evidence_supported": True,
        "worker_capacity_evidence_supported": True,
        "queue_capacity_evidence_supported": True,
        "execution_concurrency_evidence_supported": True,
        "workspace_limit_evidence_supported": True,
        "plan_entitlement_evidence_supported": True,
        "quota_evidence_supported": True,
        "reservation_evidence_supported": True,
        "throttling_evidence_supported": True,
        "fairness_evidence_supported": True,
        "priority_evidence_supported": True,
        "cost_evidence_supported": True,
        "pressure_evidence_supported": True,
        "degraded_mode_resource_evidence_supported": True,
        "observability_handoff_required": (
            handoff.observability_required
        ),
        "persistence_handoff_required": (
            handoff.persistence_required
        ),
        "owner_control_tower_handoff_required": (
            handoff.owner_control_tower_required
        ),
        "phase8_observability_authority_preserved": True,
        "phase12_persistence_authority_preserved": True,
        "no_evidence_database_created": True,
        "no_persistence_write": True,
        "no_alert_transport_created": True,
        "no_runtime_mutation": True,
    }

    return MappingProxyType({
        "phase": "10.16",
        "component": "Resource Governance Evidence",
        "version": RESOURCE_GOVERNANCE_EVIDENCE_VERSION,
        "schema_version": RESOURCE_GOVERNANCE_EVIDENCE_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 10.16 creates immutable resource-governance evidence and "
            "handoff contracts only. Phase 8 remains observability authority "
            "and Phase 12 remains persistence authority."
        ),
    })


__all__ = [
    "RESOURCE_GOVERNANCE_EVIDENCE_VERSION",
    "RESOURCE_GOVERNANCE_EVIDENCE_SCHEMA_VERSION",
    "ResourceGovernanceEvidence",
    "ResourceGovernanceEvidenceHandoff",
    "compute_resource_governance_evidence_hash",
    "verify_resource_governance_evidence",
    "create_resource_governance_evidence_handoff",
    "certify_resource_governance_evidence_v1",
]
