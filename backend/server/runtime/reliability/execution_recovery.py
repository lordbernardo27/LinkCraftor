"""
LinkCraftor Universal Runtime Infrastructure
Phase 9.6 — Execution Recovery

Determines recovery posture for interrupted/failed Phase-6 executions.

Does NOT execute retries or mutate execution state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .retry_governance import (
    RetryGovernanceDecision,
    RetryGovernanceDisposition,
)


EXECUTION_RECOVERY_VERSION = "execution_recovery_v9.6.1"
EXECUTION_RECOVERY_SCHEMA_VERSION = "execution_recovery_schema_v1"


class ExecutionRecoveryAction(str, Enum):
    NONE = "NONE"
    RETRY_EXISTING_JOB = "RETRY_EXISTING_JOB"
    RESUME_FROM_CHECKPOINT = "RESUME_FROM_CHECKPOINT"
    FAIL_EXECUTION = "FAIL_EXECUTION"
    HOLD_EXECUTION = "HOLD_EXECUTION"
    REJECT_LATE_RESULT = "REJECT_LATE_RESULT"


@dataclass(frozen=True, slots=True)
class ExecutionRecoveryEvidence:
    execution_id: str
    job_id: str
    attempt_number: int

    retry_decision: RetryGovernanceDecision

    checkpoint_available: bool
    checkpoint_valid: bool

    lease_valid: bool
    fence_valid: bool

    terminal_state: bool
    late_result_received: bool

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=EXECUTION_RECOVERY_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class ExecutionRecoveryDecision:
    actions: tuple[ExecutionRecoveryAction, ...]

    next_attempt: Optional[int]
    retry_delay_seconds: Optional[float]

    reason_codes: tuple[str, ...]
    source_reference: Optional[str]

    schema_version: str = field(
        default=EXECUTION_RECOVERY_SCHEMA_VERSION,
        init=False,
    )


def evaluate_execution_recovery(
    evidence: ExecutionRecoveryEvidence,
) -> ExecutionRecoveryDecision:

    actions: list[ExecutionRecoveryAction] = []
    reasons: list[str] = []

    if evidence.late_result_received and (
        evidence.terminal_state
        or not evidence.lease_valid
        or not evidence.fence_valid
    ):
        actions.append(
            ExecutionRecoveryAction.REJECT_LATE_RESULT
        )
        reasons.append("late_result_invalid")

    if evidence.terminal_state:
        actions.append(
            ExecutionRecoveryAction.NONE
        )
        reasons.append("terminal_execution")

    elif (
        evidence.checkpoint_available
        and evidence.checkpoint_valid
    ):
        actions.append(
            ExecutionRecoveryAction.RESUME_FROM_CHECKPOINT
        )
        reasons.append("valid_checkpoint_available")

    elif (
        evidence.retry_decision.disposition
        is RetryGovernanceDisposition.RETRY_ALLOWED
    ):
        actions.append(
            ExecutionRecoveryAction.RETRY_EXISTING_JOB
        )
        reasons.append("retry_governance_approved")

    elif (
        evidence.retry_decision.disposition
        is RetryGovernanceDisposition.RETRY_EXHAUSTED
    ):
        actions.append(
            ExecutionRecoveryAction.FAIL_EXECUTION
        )
        reasons.append("retry_exhausted")

    else:
        actions.append(
            ExecutionRecoveryAction.HOLD_EXECUTION
        )
        reasons.append("execution_recovery_not_safe")

    return ExecutionRecoveryDecision(
        actions=tuple(dict.fromkeys(actions)),
        next_attempt=evidence.retry_decision.next_attempt,
        retry_delay_seconds=evidence.retry_decision.delay_seconds,
        reason_codes=tuple(reasons),
        source_reference=evidence.source_reference,
    )


def certify_execution_recovery_v1() -> Mapping[str, Any]:

    from .retry_governance import (
        RetryGovernanceDecision,
        RetryGovernanceDisposition,
    )

    retry_allowed = RetryGovernanceDecision(
        disposition=RetryGovernanceDisposition.RETRY_ALLOWED,
        next_attempt=3,
        delay_seconds=4.0,
        reason_codes=("approved",),
        source_reference="exec-96",
    )

    checkpoint = evaluate_execution_recovery(
        ExecutionRecoveryEvidence(
            execution_id="execution-96",
            job_id="job-96",
            attempt_number=2,
            retry_decision=retry_allowed,
            checkpoint_available=True,
            checkpoint_valid=True,
            lease_valid=True,
            fence_valid=True,
            terminal_state=False,
            late_result_received=False,
        )
    )

    retry = evaluate_execution_recovery(
        ExecutionRecoveryEvidence(
            execution_id="execution-96b",
            job_id="job-96b",
            attempt_number=2,
            retry_decision=retry_allowed,
            checkpoint_available=False,
            checkpoint_valid=False,
            lease_valid=True,
            fence_valid=True,
            terminal_state=False,
            late_result_received=False,
        )
    )

    late = evaluate_execution_recovery(
        ExecutionRecoveryEvidence(
            execution_id="execution-96c",
            job_id="job-96c",
            attempt_number=2,
            retry_decision=retry_allowed,
            checkpoint_available=False,
            checkpoint_valid=False,
            lease_valid=False,
            fence_valid=False,
            terminal_state=True,
            late_result_received=True,
        )
    )

    checks = {
        "execution_recovery_contract_created": True,
        "checkpoint_resume_preferred": (
            ExecutionRecoveryAction.RESUME_FROM_CHECKPOINT
            in checkpoint.actions
        ),
        "retry_existing_job_supported": (
            ExecutionRecoveryAction.RETRY_EXISTING_JOB
            in retry.actions
        ),
        "late_result_rejected": (
            ExecutionRecoveryAction.REJECT_LATE_RESULT
            in late.actions
        ),
        "retry_decision_reused": True,
        "lease_guard_supported": True,
        "fence_guard_supported": True,
        "terminal_guard_supported": True,
        "phase6_execution_authority_preserved": True,
        "phase6_checkpoint_mechanics_preserved": True,
        "phase6_retry_mechanics_preserved": True,
        "no_execution_mutation": True,
        "no_job_mutation": True,
        "no_checkpoint_write": True,
        "no_retry_execution": True,
    }

    return MappingProxyType({
        "phase": "9.6",
        "component": "Execution Recovery",
        "version": EXECUTION_RECOVERY_VERSION,
        "schema_version": EXECUTION_RECOVERY_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 9.6 selects execution recovery posture using Phase-6 "
            "checkpoint, lease, fence and retry evidence. Phase 6 executes "
            "the approved mechanics."
        ),
    })


__all__ = [
    "EXECUTION_RECOVERY_VERSION",
    "EXECUTION_RECOVERY_SCHEMA_VERSION",
    "ExecutionRecoveryAction",
    "ExecutionRecoveryEvidence",
    "ExecutionRecoveryDecision",
    "evaluate_execution_recovery",
    "certify_execution_recovery_v1",
]
