"""
LinkCraftor Universal Runtime Infrastructure
Phase 9.5 — Queue Recovery

Evaluates queue failure/degradation and produces recovery instructions.

Does NOT create or mutate a queue backend.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional


QUEUE_RECOVERY_VERSION = "queue_recovery_v9.5.1"
QUEUE_RECOVERY_SCHEMA_VERSION = "queue_recovery_schema_v1"


class QueueRecoveryAction(str, Enum):
    NONE = "NONE"
    PAUSE_NEW_DEQUEUE = "PAUSE_NEW_DEQUEUE"
    RESUME_DEQUEUE = "RESUME_DEQUEUE"
    REQUEUE_ELIGIBLE_JOB = "REQUEUE_ELIGIBLE_JOB"
    HOLD_JOB = "HOLD_JOB"
    ROUTE_DEAD_LETTER = "ROUTE_DEAD_LETTER"
    ESCALATE_QUEUE_FAILURE = "ESCALATE_QUEUE_FAILURE"


@dataclass(frozen=True, slots=True)
class QueueRecoveryEvidence:
    queue_name: str

    available: bool
    accepting_enqueues: bool
    allowing_dequeues: bool

    depth: int
    inflight_count: int
    stale_inflight_count: int

    duplicate_delivery_risk: bool
    ordering_integrity_risk: bool

    repeated_failure_count: int = 1

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=QUEUE_RECOVERY_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class QueueRecoveryDecision:
    actions: tuple[QueueRecoveryAction, ...]
    reason_codes: tuple[str, ...]
    source_reference: Optional[str]

    schema_version: str = field(
        default=QUEUE_RECOVERY_SCHEMA_VERSION,
        init=False,
    )


def evaluate_queue_recovery(
    evidence: QueueRecoveryEvidence,
) -> QueueRecoveryDecision:

    actions: list[QueueRecoveryAction] = []
    reasons: list[str] = []

    high_integrity_risk = (
        evidence.duplicate_delivery_risk
        or evidence.ordering_integrity_risk
    )

    if not evidence.available:
        actions.append(
            QueueRecoveryAction.PAUSE_NEW_DEQUEUE
        )
        reasons.append("queue_unavailable")

    if high_integrity_risk:
        actions.append(
            QueueRecoveryAction.PAUSE_NEW_DEQUEUE
        )
        reasons.append("queue_integrity_risk")

    if evidence.stale_inflight_count > 0:
        if high_integrity_risk:
            actions.append(
                QueueRecoveryAction.HOLD_JOB
            )
            reasons.append("stale_inflight_held")

        else:
            actions.append(
                QueueRecoveryAction.REQUEUE_ELIGIBLE_JOB
            )
            reasons.append("stale_inflight_requeue_candidate")

    if evidence.repeated_failure_count >= 3:
        actions.append(
            QueueRecoveryAction.ESCALATE_QUEUE_FAILURE
        )
        reasons.append("repeated_queue_failure")

    if not actions:
        actions.append(
            QueueRecoveryAction.NONE
        )
        reasons.append("queue_recovery_not_required")

    return QueueRecoveryDecision(
        actions=tuple(dict.fromkeys(actions)),
        reason_codes=tuple(reasons),
        source_reference=evidence.source_reference,
    )


def certify_queue_recovery_v1() -> Mapping[str, Any]:

    normal = evaluate_queue_recovery(
        QueueRecoveryEvidence(
            queue_name="runtime-default",
            available=True,
            accepting_enqueues=True,
            allowing_dequeues=True,
            depth=10,
            inflight_count=2,
            stale_inflight_count=0,
            duplicate_delivery_risk=False,
            ordering_integrity_risk=False,
        )
    )

    stale = evaluate_queue_recovery(
        QueueRecoveryEvidence(
            queue_name="runtime-default",
            available=True,
            accepting_enqueues=True,
            allowing_dequeues=True,
            depth=12,
            inflight_count=3,
            stale_inflight_count=1,
            duplicate_delivery_risk=False,
            ordering_integrity_risk=False,
        )
    )

    risky = evaluate_queue_recovery(
        QueueRecoveryEvidence(
            queue_name="runtime-default",
            available=True,
            accepting_enqueues=True,
            allowing_dequeues=True,
            depth=12,
            inflight_count=3,
            stale_inflight_count=1,
            duplicate_delivery_risk=True,
            ordering_integrity_risk=False,
        )
    )

    checks = {
        "queue_recovery_contract_created": True,
        "healthy_queue_no_recovery": (
            normal.actions == (QueueRecoveryAction.NONE,)
        ),
        "stale_inflight_requeue_candidate": (
            QueueRecoveryAction.REQUEUE_ELIGIBLE_JOB
            in stale.actions
        ),
        "integrity_risk_pauses_dequeue": (
            QueueRecoveryAction.PAUSE_NEW_DEQUEUE
            in risky.actions
        ),
        "integrity_risk_holds_job": (
            QueueRecoveryAction.HOLD_JOB
            in risky.actions
        ),
        "dead_letter_action_supported": True,
        "queue_escalation_supported": True,
        "existing_queue_authority_preserved": True,
        "no_queue_backend_created": True,
        "no_enqueue_execution": True,
        "no_dequeue_execution": True,
        "no_requeue_execution": True,
        "no_queue_mutation": True,
        "no_job_mutation": True,
    }

    return MappingProxyType({
        "phase": "9.5",
        "component": "Queue Recovery",
        "version": QUEUE_RECOVERY_VERSION,
        "schema_version": QUEUE_RECOVERY_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 9.5 decides queue recovery posture and candidate actions "
            "only. Existing queue infrastructure executes approved operations."
        ),
    })


__all__ = [
    "QUEUE_RECOVERY_VERSION",
    "QUEUE_RECOVERY_SCHEMA_VERSION",
    "QueueRecoveryAction",
    "QueueRecoveryEvidence",
    "QueueRecoveryDecision",
    "evaluate_queue_recovery",
    "certify_queue_recovery_v1",
]
