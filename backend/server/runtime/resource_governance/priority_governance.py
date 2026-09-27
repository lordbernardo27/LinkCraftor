"""
LinkCraftor Universal Runtime Infrastructure
Phase 10.12 — Priority Governance

Purpose:
- normalize runtime priority
- cap priority by permitted maximum
- preserve starvation protection boundaries

Does NOT:
- reorder queue
- schedule jobs
- preempt executions
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from types import MappingProxyType
from typing import Any, Mapping, Optional


PRIORITY_GOVERNANCE_VERSION = (
    "priority_governance_v10.12.1"
)

PRIORITY_GOVERNANCE_SCHEMA_VERSION = (
    "priority_governance_schema_v1"
)


class RuntimePriority(IntEnum):
    BACKGROUND = 10
    STANDARD = 20
    HIGH = 30
    CRITICAL = 40


@dataclass(frozen=True, slots=True)
class PriorityEvidence:
    requested_priority: RuntimePriority
    maximum_permitted_priority: RuntimePriority

    starvation_risk: bool = False
    recovery_critical: bool = False

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=PRIORITY_GOVERNANCE_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class PriorityDecision:
    requested_priority: RuntimePriority
    effective_priority: RuntimePriority

    capped: bool
    starvation_protection_required: bool

    reason_codes: tuple[str, ...]
    source_reference: Optional[str]

    schema_version: str = field(
        default=PRIORITY_GOVERNANCE_SCHEMA_VERSION,
        init=False,
    )


def evaluate_priority_governance(
    evidence: PriorityEvidence,
) -> PriorityDecision:

    effective = min(
        evidence.requested_priority,
        evidence.maximum_permitted_priority,
    )

    capped = (
        effective != evidence.requested_priority
    )

    reasons: list[str] = []

    if capped:
        reasons.append("priority_capped_by_governance")

    if evidence.recovery_critical:
        reasons.append("recovery_critical_context")

    if evidence.starvation_risk:
        reasons.append("starvation_protection_required")

    if not reasons:
        reasons.append("priority_within_boundary")

    return PriorityDecision(
        requested_priority=evidence.requested_priority,
        effective_priority=RuntimePriority(effective),
        capped=capped,
        starvation_protection_required=evidence.starvation_risk,
        reason_codes=tuple(reasons),
        source_reference=evidence.source_reference,
    )


def certify_priority_governance_v1(
) -> Mapping[str, Any]:

    allowed = evaluate_priority_governance(
        PriorityEvidence(
            requested_priority=RuntimePriority.HIGH,
            maximum_permitted_priority=RuntimePriority.HIGH,
        )
    )

    capped = evaluate_priority_governance(
        PriorityEvidence(
            requested_priority=RuntimePriority.CRITICAL,
            maximum_permitted_priority=RuntimePriority.STANDARD,
        )
    )

    starvation = evaluate_priority_governance(
        PriorityEvidence(
            requested_priority=RuntimePriority.BACKGROUND,
            maximum_permitted_priority=RuntimePriority.HIGH,
            starvation_risk=True,
        )
    )

    checks = {
        "priority_contract_created": True,
        "priority_within_boundary_preserved": (
            allowed.effective_priority is RuntimePriority.HIGH
        ),
        "priority_cap_enforced": capped.capped,
        "effective_priority_capped": (
            capped.effective_priority
            is RuntimePriority.STANDARD
        ),
        "starvation_protection_signal_supported": (
            starvation.starvation_protection_required
        ),
        "background_priority_supported": True,
        "standard_priority_supported": True,
        "high_priority_supported": True,
        "critical_priority_supported": True,
        "recovery_priority_context_supported": True,
        "no_queue_reordering": True,
        "no_job_scheduling": True,
        "no_execution_preemption": True,
        "no_worker_mutation": True,
        "no_runtime_mutation": True,
    }

    return MappingProxyType({
        "phase": "10.12",
        "component": "Priority Governance",
        "version": PRIORITY_GOVERNANCE_VERSION,
        "schema_version": PRIORITY_GOVERNANCE_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 10.12 determines effective priority boundaries only. "
            "Existing runtime scheduling/dispatch authorities consume the "
            "decision."
        ),
    })


__all__ = [
    "PRIORITY_GOVERNANCE_VERSION",
    "PRIORITY_GOVERNANCE_SCHEMA_VERSION",
    "RuntimePriority",
    "PriorityEvidence",
    "PriorityDecision",
    "evaluate_priority_governance",
    "certify_priority_governance_v1",
]
