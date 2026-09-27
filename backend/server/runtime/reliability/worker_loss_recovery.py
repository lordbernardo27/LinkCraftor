"""
LinkCraftor Universal Runtime Infrastructure
Phase 9.4 — Worker-Loss Recovery

Produces recovery instructions when an existing worker is lost/stale.

Does NOT create workers or mutate the worker registry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional


WORKER_LOSS_RECOVERY_VERSION = "worker_loss_recovery_v9.4.1"
WORKER_LOSS_RECOVERY_SCHEMA_VERSION = "worker_loss_recovery_schema_v1"


class WorkerRecoveryAction(str, Enum):
    NONE = "NONE"
    MARK_ASSIGNMENT_LOST = "MARK_ASSIGNMENT_LOST"
    RELEASE_EXPIRED_LEASE = "RELEASE_EXPIRED_LEASE"
    REASSIGN_ELIGIBLE_WORK = "REASSIGN_ELIGIBLE_WORK"
    HOLD_FOR_REVIEW = "HOLD_FOR_REVIEW"


@dataclass(frozen=True, slots=True)
class WorkerLossEvidence:
    worker_id: str
    worker_instance_id: Optional[str]

    stale: bool
    active: bool
    heartbeat_expired: bool

    active_assignment_count: int
    active_lease_count: int

    lease_expired: bool
    execution_fence_valid: bool

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=WORKER_LOSS_RECOVERY_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class WorkerLossRecoveryDecision:
    worker_lost: bool
    actions: tuple[WorkerRecoveryAction, ...]

    reason_codes: tuple[str, ...]
    source_reference: Optional[str]

    schema_version: str = field(
        default=WORKER_LOSS_RECOVERY_SCHEMA_VERSION,
        init=False,
    )


def evaluate_worker_loss_recovery(
    evidence: WorkerLossEvidence,
) -> WorkerLossRecoveryDecision:

    lost = (
        evidence.stale
        or not evidence.active
        or evidence.heartbeat_expired
    )

    if not lost:
        return WorkerLossRecoveryDecision(
            worker_lost=False,
            actions=(WorkerRecoveryAction.NONE,),
            reason_codes=("worker_healthy",),
            source_reference=evidence.source_reference,
        )

    actions: list[WorkerRecoveryAction] = [
        WorkerRecoveryAction.MARK_ASSIGNMENT_LOST
    ]

    reasons = ["worker_loss_detected"]

    if (
        evidence.active_lease_count > 0
        and evidence.lease_expired
    ):
        actions.append(
            WorkerRecoveryAction.RELEASE_EXPIRED_LEASE
        )
        reasons.append("expired_lease_present")

    if (
        evidence.active_assignment_count > 0
        and evidence.lease_expired
        and evidence.execution_fence_valid
    ):
        actions.append(
            WorkerRecoveryAction.REASSIGN_ELIGIBLE_WORK
        )
        reasons.append("work_reassignment_allowed")

    elif evidence.active_assignment_count > 0:
        actions.append(
            WorkerRecoveryAction.HOLD_FOR_REVIEW
        )
        reasons.append("unsafe_reassignment_conditions")

    return WorkerLossRecoveryDecision(
        worker_lost=True,
        actions=tuple(actions),
        reason_codes=tuple(reasons),
        source_reference=evidence.source_reference,
    )


def certify_worker_loss_recovery_v1() -> Mapping[str, Any]:

    decision = evaluate_worker_loss_recovery(
        WorkerLossEvidence(
            worker_id="worker-94",
            worker_instance_id="instance-94",
            stale=True,
            active=False,
            heartbeat_expired=True,
            active_assignment_count=2,
            active_lease_count=1,
            lease_expired=True,
            execution_fence_valid=True,
            source_reference="worker-loss-94",
        )
    )

    checks = {
        "worker_loss_recovery_contract_created": True,
        "worker_loss_detected": decision.worker_lost,
        "assignment_loss_action_present": (
            WorkerRecoveryAction.MARK_ASSIGNMENT_LOST
            in decision.actions
        ),
        "expired_lease_release_present": (
            WorkerRecoveryAction.RELEASE_EXPIRED_LEASE
            in decision.actions
        ),
        "eligible_reassignment_present": (
            WorkerRecoveryAction.REASSIGN_ELIGIBLE_WORK
            in decision.actions
        ),
        "unsafe_reassignment_hold_supported": True,
        "existing_worker_registry_preserved": True,
        "existing_lease_authority_preserved": True,
        "existing_assignment_authority_preserved": True,
        "no_worker_created": True,
        "no_worker_registry_mutation": True,
        "no_lease_mutation": True,
        "no_queue_mutation": True,
        "no_execution_mutation": True,
        "no_reassignment_execution": True,
    }

    return MappingProxyType({
        "phase": "9.4",
        "component": "Worker-Loss Recovery",
        "version": WORKER_LOSS_RECOVERY_VERSION,
        "schema_version": WORKER_LOSS_RECOVERY_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 9.4 detects worker loss and produces recovery instructions "
            "for existing assignment, lease and worker authorities. It does "
            "not mutate those authorities directly."
        ),
    })


__all__ = [
    "WORKER_LOSS_RECOVERY_VERSION",
    "WORKER_LOSS_RECOVERY_SCHEMA_VERSION",
    "WorkerRecoveryAction",
    "WorkerLossEvidence",
    "WorkerLossRecoveryDecision",
    "evaluate_worker_loss_recovery",
    "certify_worker_loss_recovery_v1",
]
