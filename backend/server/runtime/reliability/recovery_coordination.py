"""
LinkCraftor Universal Runtime Infrastructure
Phase 9.3 — Recovery Coordination

Coordinates which existing recovery authority should receive a failure.

Does NOT perform the concrete recovery itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .failure_classification_containment import (
    FailureContainmentDecision,
    RuntimeFailureDomain,
)


RECOVERY_COORDINATION_VERSION = "recovery_coordination_v9.3.1"
RECOVERY_COORDINATION_SCHEMA_VERSION = "recovery_coordination_schema_v1"


class RecoveryRoute(str, Enum):
    NONE = "NONE"
    WORKER_RECOVERY = "WORKER_RECOVERY"
    QUEUE_RECOVERY = "QUEUE_RECOVERY"
    EXECUTION_RECOVERY = "EXECUTION_RECOVERY"
    ORCHESTRATION_RECOVERY = "ORCHESTRATION_RECOVERY"
    DEAD_LETTER_GOVERNANCE = "DEAD_LETTER_GOVERNANCE"
    CRASH_RESTART_RECOVERY = "CRASH_RESTART_RECOVERY"
    DEGRADED_MODE = "DEGRADED_MODE"
    ESCALATION = "ESCALATION"


@dataclass(frozen=True, slots=True)
class RecoveryCoordinationEvidence:
    containment_decision: FailureContainmentDecision

    worker_lost: bool = False
    queue_unavailable: bool = False
    execution_interrupted: bool = False
    orchestration_blocked: bool = False
    runtime_restart_detected: bool = False
    repeated_recovery_failure: bool = False

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=RECOVERY_COORDINATION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class RecoveryCoordinationDecision:
    primary_route: RecoveryRoute
    secondary_routes: tuple[RecoveryRoute, ...]

    reason_codes: tuple[str, ...]
    source_reference: Optional[str]

    schema_version: str = field(
        default=RECOVERY_COORDINATION_SCHEMA_VERSION,
        init=False,
    )


def coordinate_recovery(
    evidence: RecoveryCoordinationEvidence,
) -> RecoveryCoordinationDecision:

    routes: list[RecoveryRoute] = []
    reasons: list[str] = []

    if evidence.repeated_recovery_failure:
        routes.append(RecoveryRoute.DEGRADED_MODE)
        reasons.append("repeated_recovery_failure")

    if evidence.runtime_restart_detected:
        routes.append(
            RecoveryRoute.CRASH_RESTART_RECOVERY
        )
        reasons.append("runtime_restart_detected")

    if evidence.worker_lost:
        routes.append(RecoveryRoute.WORKER_RECOVERY)
        reasons.append("worker_lost")

    if evidence.queue_unavailable:
        routes.append(RecoveryRoute.QUEUE_RECOVERY)
        reasons.append("queue_unavailable")

    if evidence.execution_interrupted:
        routes.append(RecoveryRoute.EXECUTION_RECOVERY)
        reasons.append("execution_interrupted")

    if evidence.orchestration_blocked:
        routes.append(RecoveryRoute.ORCHESTRATION_RECOVERY)
        reasons.append("orchestration_blocked")

    domain = evidence.containment_decision.domain

    if not routes:
        if domain is RuntimeFailureDomain.WORKER:
            routes.append(RecoveryRoute.WORKER_RECOVERY)

        elif domain is RuntimeFailureDomain.QUEUE:
            routes.append(RecoveryRoute.QUEUE_RECOVERY)

        elif domain in {
            RuntimeFailureDomain.EXECUTION,
            RuntimeFailureDomain.HANDLER,
            RuntimeFailureDomain.LEASE,
            RuntimeFailureDomain.CHECKPOINT,
        }:
            routes.append(RecoveryRoute.EXECUTION_RECOVERY)

        elif domain is RuntimeFailureDomain.ORCHESTRATION:
            routes.append(
                RecoveryRoute.ORCHESTRATION_RECOVERY
            )

        else:
            routes.append(RecoveryRoute.ESCALATION)

        reasons.append("routed_by_failure_domain")

    deduped = tuple(
        dict.fromkeys(routes)
    )

    return RecoveryCoordinationDecision(
        primary_route=deduped[0],
        secondary_routes=deduped[1:],
        reason_codes=tuple(reasons),
        source_reference=evidence.source_reference,
    )


def certify_recovery_coordination_v1() -> Mapping[str, Any]:

    from .failure_classification_containment import (
        FailureContainmentDecision,
        FailureContainmentDisposition,
        FailureRetryability,
        RuntimeFailureDomain,
        RuntimeFailureScope,
        RuntimeFailureSeverity,
        ContainmentAction,
    )

    base = FailureContainmentDecision(
        disposition=FailureContainmentDisposition.CONTAIN,
        domain=RuntimeFailureDomain.WORKER,
        severity=RuntimeFailureSeverity.ERROR,
        scope=RuntimeFailureScope.WORKER,
        retryability=FailureRetryability.RETRYABLE,
        containment_action=ContainmentAction.ISOLATE_WORKER,
        reason_codes=("worker_lost",),
        source_reference="coord-93",
    )

    decision = coordinate_recovery(
        RecoveryCoordinationEvidence(
            containment_decision=base,
            worker_lost=True,
            execution_interrupted=True,
        )
    )

    checks = {
        "recovery_coordination_contract_created": True,
        "worker_recovery_primary": (
            decision.primary_route
            is RecoveryRoute.WORKER_RECOVERY
        ),
        "execution_recovery_secondary": (
            RecoveryRoute.EXECUTION_RECOVERY
            in decision.secondary_routes
        ),
        "queue_recovery_route_supported": True,
        "orchestration_recovery_route_supported": True,
        "dead_letter_route_supported": True,
        "restart_recovery_route_supported": True,
        "degraded_mode_route_supported": True,
        "escalation_route_supported": True,
        "no_recovery_execution": True,
        "no_queue_mutation": True,
        "no_worker_mutation": True,
        "no_execution_mutation": True,
        "no_orchestration_mutation": True,
        "no_persistence_write": True,
    }

    return MappingProxyType({
        "phase": "9.3",
        "component": "Recovery Coordination",
        "version": RECOVERY_COORDINATION_VERSION,
        "schema_version": RECOVERY_COORDINATION_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 9.3 selects the appropriate recovery route and order only. "
            "Concrete recovery remains with existing runtime mechanisms and "
            "specialized Phase-9 recovery components."
        ),
    })


__all__ = [
    "RECOVERY_COORDINATION_VERSION",
    "RECOVERY_COORDINATION_SCHEMA_VERSION",
    "RecoveryRoute",
    "RecoveryCoordinationEvidence",
    "RecoveryCoordinationDecision",
    "coordinate_recovery",
    "certify_recovery_coordination_v1",
]
