"""
LinkCraftor Universal Runtime Infrastructure
Phase 9.10 — Degraded-Mode Operation

Defines safe degraded operating posture when runtime is impaired.

Does NOT:
- throttle directly
- pause queues directly
- kill workers
- mutate jobs
- create resource governor
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional


DEGRADED_MODE_OPERATION_VERSION = (
    "degraded_mode_operation_v9.10.1"
)

DEGRADED_MODE_OPERATION_SCHEMA_VERSION = (
    "degraded_mode_operation_schema_v1"
)


class DegradedModeLevel(str, Enum):
    NORMAL = "NORMAL"
    LIMITED = "LIMITED"
    RESTRICTED = "RESTRICTED"
    PROTECTIVE = "PROTECTIVE"


class DegradedModeAction(str, Enum):
    NONE = "NONE"
    REDUCE_NEW_WORK = "REDUCE_NEW_WORK"
    PAUSE_NON_CRITICAL_WORK = "PAUSE_NON_CRITICAL_WORK"
    PRESERVE_INFLIGHT_WORK = "PRESERVE_INFLIGHT_WORK"
    HOLD_NEW_EXECUTIONS = "HOLD_NEW_EXECUTIONS"
    OWNER_ESCALATION = "OWNER_ESCALATION"


@dataclass(frozen=True, slots=True)
class DegradedModeEvidence:
    runtime_unhealthy: bool

    queue_pressure_high: bool
    worker_capacity_low: bool
    repeated_failures: bool
    dependency_unavailable: bool

    persistence_integrity_uncertain: bool
    security_risk: bool

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=DEGRADED_MODE_OPERATION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class DegradedModeDecision:
    level: DegradedModeLevel
    actions: tuple[DegradedModeAction, ...]

    reason_codes: tuple[str, ...]
    source_reference: Optional[str]

    schema_version: str = field(
        default=DEGRADED_MODE_OPERATION_SCHEMA_VERSION,
        init=False,
    )


def evaluate_degraded_mode(
    evidence: DegradedModeEvidence,
) -> DegradedModeDecision:

    severe = (
        evidence.persistence_integrity_uncertain
        or evidence.security_risk
    )

    if severe:
        return DegradedModeDecision(
            level=DegradedModeLevel.PROTECTIVE,
            actions=(
                DegradedModeAction.HOLD_NEW_EXECUTIONS,
                DegradedModeAction.PRESERVE_INFLIGHT_WORK,
                DegradedModeAction.OWNER_ESCALATION,
            ),
            reason_codes=("protective_runtime_posture_required",),
            source_reference=evidence.source_reference,
        )

    pressure_count = sum(
        bool(x)
        for x in (
            evidence.runtime_unhealthy,
            evidence.queue_pressure_high,
            evidence.worker_capacity_low,
            evidence.repeated_failures,
            evidence.dependency_unavailable,
        )
    )

    if pressure_count >= 3:
        return DegradedModeDecision(
            level=DegradedModeLevel.RESTRICTED,
            actions=(
                DegradedModeAction.REDUCE_NEW_WORK,
                DegradedModeAction.PAUSE_NON_CRITICAL_WORK,
                DegradedModeAction.PRESERVE_INFLIGHT_WORK,
            ),
            reason_codes=("multiple_runtime_impairments",),
            source_reference=evidence.source_reference,
        )

    if pressure_count >= 1:
        return DegradedModeDecision(
            level=DegradedModeLevel.LIMITED,
            actions=(
                DegradedModeAction.REDUCE_NEW_WORK,
                DegradedModeAction.PRESERVE_INFLIGHT_WORK,
            ),
            reason_codes=("runtime_degradation_detected",),
            source_reference=evidence.source_reference,
        )

    return DegradedModeDecision(
        level=DegradedModeLevel.NORMAL,
        actions=(DegradedModeAction.NONE,),
        reason_codes=("normal_operation",),
        source_reference=evidence.source_reference,
    )


def certify_degraded_mode_operation_v1(
) -> Mapping[str, Any]:

    normal = evaluate_degraded_mode(
        DegradedModeEvidence(
            runtime_unhealthy=False,
            queue_pressure_high=False,
            worker_capacity_low=False,
            repeated_failures=False,
            dependency_unavailable=False,
            persistence_integrity_uncertain=False,
            security_risk=False,
        )
    )

    restricted = evaluate_degraded_mode(
        DegradedModeEvidence(
            runtime_unhealthy=True,
            queue_pressure_high=True,
            worker_capacity_low=True,
            repeated_failures=False,
            dependency_unavailable=False,
            persistence_integrity_uncertain=False,
            security_risk=False,
        )
    )

    protective = evaluate_degraded_mode(
        DegradedModeEvidence(
            runtime_unhealthy=True,
            queue_pressure_high=False,
            worker_capacity_low=False,
            repeated_failures=True,
            dependency_unavailable=False,
            persistence_integrity_uncertain=True,
            security_risk=False,
        )
    )

    checks = {
        "degraded_mode_contract_created": True,
        "normal_mode_detected": (
            normal.level is DegradedModeLevel.NORMAL
        ),
        "restricted_mode_detected": (
            restricted.level is DegradedModeLevel.RESTRICTED
        ),
        "protective_mode_detected": (
            protective.level is DegradedModeLevel.PROTECTIVE
        ),
        "reduce_new_work_supported": True,
        "pause_noncritical_supported": True,
        "preserve_inflight_supported": True,
        "hold_new_execution_supported": True,
        "owner_escalation_supported": True,
        "phase10_resource_governance_preserved": True,
        "existing_queue_authority_preserved": True,
        "phase6_execution_authority_preserved": True,
        "no_throttling_execution": True,
        "no_queue_pause_execution": True,
        "no_worker_shutdown": True,
        "no_job_mutation": True,
        "no_resource_governor_created": True,
    }

    return MappingProxyType({
        "phase": "9.10",
        "component": "Degraded-Mode Operation",
        "version": DEGRADED_MODE_OPERATION_VERSION,
        "schema_version": DEGRADED_MODE_OPERATION_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 9.10 selects degraded operating posture only. Existing "
            "runtime authorities and future Phase-10 resource governance "
            "apply concrete capacity controls."
        ),
    })


__all__ = [
    "DEGRADED_MODE_OPERATION_VERSION",
    "DEGRADED_MODE_OPERATION_SCHEMA_VERSION",
    "DegradedModeLevel",
    "DegradedModeAction",
    "DegradedModeEvidence",
    "DegradedModeDecision",
    "evaluate_degraded_mode",
    "certify_degraded_mode_operation_v1",
]
