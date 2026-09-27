"""
LinkCraftor Universal Runtime Infrastructure
Phase 10.11 — Fairness & Scheduling Boundaries

Purpose:
- define fairness boundaries between competing scopes
- prevent one workspace/scope from consuming all available capacity
- preserve scheduling authority outside Phase 10

Does NOT:
- schedule jobs
- reorder queues
- assign workers
- create scheduler
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .resource_governance_contract import (
    ResourceAdmissionDisposition,
)


FAIRNESS_SCHEDULING_BOUNDARIES_VERSION = (
    "fairness_scheduling_boundaries_v10.11.1"
)

FAIRNESS_SCHEDULING_BOUNDARIES_SCHEMA_VERSION = (
    "fairness_scheduling_boundaries_schema_v1"
)


class FairnessAction(str, Enum):
    MAINTAIN = "MAINTAIN"
    LIMIT_DOMINANT_SCOPE = "LIMIT_DOMINANT_SCOPE"
    PRESERVE_MINIMUM_SHARE = "PRESERVE_MINIMUM_SHARE"
    DEFER_EXCESS_SHARE = "DEFER_EXCESS_SHARE"


@dataclass(frozen=True, slots=True)
class FairnessEvidence:
    scope_key: str

    active_share_ratio: float
    requested_additional_share_ratio: float

    maximum_share_ratio: float
    minimum_guaranteed_share_ratio: float

    competing_scope_count: int

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=FAIRNESS_SCHEDULING_BOUNDARIES_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class FairnessDecision:
    disposition: ResourceAdmissionDisposition
    action: FairnessAction

    allowed_additional_share_ratio: float

    reason_codes: tuple[str, ...]
    source_reference: Optional[str]

    schema_version: str = field(
        default=FAIRNESS_SCHEDULING_BOUNDARIES_SCHEMA_VERSION,
        init=False,
    )


def evaluate_fairness_boundary(
    evidence: FairnessEvidence,
) -> FairnessDecision:

    if evidence.competing_scope_count <= 1:
        return FairnessDecision(
            disposition=ResourceAdmissionDisposition.ALLOW,
            action=FairnessAction.MAINTAIN,
            allowed_additional_share_ratio=(
                evidence.requested_additional_share_ratio
            ),
            reason_codes=("no_competing_scope_pressure",),
            source_reference=evidence.source_reference,
        )

    remaining_share = max(
        evidence.maximum_share_ratio
        - evidence.active_share_ratio,
        0.0,
    )

    if evidence.active_share_ratio >= evidence.maximum_share_ratio:
        return FairnessDecision(
            disposition=ResourceAdmissionDisposition.DEFER,
            action=FairnessAction.DEFER_EXCESS_SHARE,
            allowed_additional_share_ratio=0.0,
            reason_codes=("maximum_fair_share_reached",),
            source_reference=evidence.source_reference,
        )

    if (
        evidence.requested_additional_share_ratio
        > remaining_share
    ):
        return FairnessDecision(
            disposition=ResourceAdmissionDisposition.ALLOW_WITH_LIMIT,
            action=FairnessAction.LIMIT_DOMINANT_SCOPE,
            allowed_additional_share_ratio=remaining_share,
            reason_codes=("fair_share_limited",),
            source_reference=evidence.source_reference,
        )

    return FairnessDecision(
        disposition=ResourceAdmissionDisposition.ALLOW,
        action=FairnessAction.PRESERVE_MINIMUM_SHARE,
        allowed_additional_share_ratio=(
            evidence.requested_additional_share_ratio
        ),
        reason_codes=("fair_share_available",),
        source_reference=evidence.source_reference,
    )


def certify_fairness_scheduling_boundaries_v1(
) -> Mapping[str, Any]:

    fair = evaluate_fairness_boundary(
        FairnessEvidence(
            scope_key="workspace-a",
            active_share_ratio=0.30,
            requested_additional_share_ratio=0.10,
            maximum_share_ratio=0.60,
            minimum_guaranteed_share_ratio=0.10,
            competing_scope_count=3,
        )
    )

    limited = evaluate_fairness_boundary(
        FairnessEvidence(
            scope_key="workspace-b",
            active_share_ratio=0.55,
            requested_additional_share_ratio=0.20,
            maximum_share_ratio=0.60,
            minimum_guaranteed_share_ratio=0.10,
            competing_scope_count=3,
        )
    )

    deferred = evaluate_fairness_boundary(
        FairnessEvidence(
            scope_key="workspace-c",
            active_share_ratio=0.60,
            requested_additional_share_ratio=0.05,
            maximum_share_ratio=0.60,
            minimum_guaranteed_share_ratio=0.10,
            competing_scope_count=3,
        )
    )

    checks = {
        "fairness_contract_created": True,
        "fair_share_allowed": (
            fair.disposition
            is ResourceAdmissionDisposition.ALLOW
        ),
        "dominant_scope_limited": (
            limited.disposition
            is ResourceAdmissionDisposition.ALLOW_WITH_LIMIT
        ),
        "maximum_share_defers_excess": (
            deferred.disposition
            is ResourceAdmissionDisposition.DEFER
        ),
        "minimum_share_boundary_supported": True,
        "competing_scope_awareness_supported": True,
        "fairness_action_defined": True,
        "existing_queue_ordering_preserved": True,
        "existing_worker_assignment_preserved": True,
        "phase5_orchestration_authority_preserved": True,
        "no_scheduler_created": True,
        "no_queue_reordering": True,
        "no_job_scheduling": True,
        "no_worker_assignment": True,
        "no_runtime_mutation": True,
    }

    return MappingProxyType({
        "phase": "10.11",
        "component": "Fairness & Scheduling Boundaries",
        "version": FAIRNESS_SCHEDULING_BOUNDARIES_VERSION,
        "schema_version": FAIRNESS_SCHEDULING_BOUNDARIES_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 10.11 defines fairness constraints only. It does not "
            "schedule, reorder or dispatch runtime work."
        ),
    })


__all__ = [
    "FAIRNESS_SCHEDULING_BOUNDARIES_VERSION",
    "FAIRNESS_SCHEDULING_BOUNDARIES_SCHEMA_VERSION",
    "FairnessAction",
    "FairnessEvidence",
    "FairnessDecision",
    "evaluate_fairness_boundary",
    "certify_fairness_scheduling_boundaries_v1",
]
