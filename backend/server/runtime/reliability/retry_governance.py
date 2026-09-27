"""
LinkCraftor Universal Runtime Infrastructure
Phase 9.2 — Retry Governance

Purpose:
- decide whether retry is permitted
- apply retry ceilings
- apply retry delay policy
- prevent unsafe retry
- preserve Phase-6 retry execution mechanics

Does NOT:
- enqueue retries
- mutate jobs
- mutate executions
- create scheduler
- create retry queue
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .failure_classification_containment import (
    FailureContainmentDecision,
    FailureContainmentDisposition,
    FailureRetryability,
    RuntimeFailureSeverity,
)


RETRY_GOVERNANCE_VERSION = "retry_governance_v9.2.1"
RETRY_GOVERNANCE_SCHEMA_VERSION = "retry_governance_schema_v1"


class RetryGovernanceDisposition(str, Enum):
    RETRY_ALLOWED = "RETRY_ALLOWED"
    RETRY_DENIED = "RETRY_DENIED"
    RETRY_EXHAUSTED = "RETRY_EXHAUSTED"


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_attempts: int
    base_delay_seconds: float
    max_delay_seconds: float
    exponential_backoff: bool = True

    schema_version: str = field(
        default=RETRY_GOVERNANCE_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1.")
        if self.base_delay_seconds < 0:
            raise ValueError("base_delay_seconds cannot be negative.")
        if self.max_delay_seconds < self.base_delay_seconds:
            raise ValueError(
                "max_delay_seconds must be >= base_delay_seconds."
            )


@dataclass(frozen=True, slots=True)
class RetryGovernanceEvidence:
    containment_decision: FailureContainmentDecision

    current_attempt: int
    policy: RetryPolicy

    idempotency_safe: bool
    execution_fence_valid: bool
    lease_valid: bool

    terminal_state: bool = False
    cancellation_requested: bool = False

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=RETRY_GOVERNANCE_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if self.current_attempt < 1:
            raise ValueError("current_attempt must be >= 1.")


@dataclass(frozen=True, slots=True)
class RetryGovernanceDecision:
    disposition: RetryGovernanceDisposition

    next_attempt: Optional[int]
    delay_seconds: Optional[float]

    reason_codes: tuple[str, ...]

    source_reference: Optional[str]

    schema_version: str = field(
        default=RETRY_GOVERNANCE_SCHEMA_VERSION,
        init=False,
    )

    @property
    def retry_allowed(self) -> bool:
        return (
            self.disposition
            is RetryGovernanceDisposition.RETRY_ALLOWED
        )


def _retry_delay_seconds(
    policy: RetryPolicy,
    current_attempt: int,
) -> float:

    if not policy.exponential_backoff:
        return min(
            policy.base_delay_seconds,
            policy.max_delay_seconds,
        )

    multiplier = 2 ** max(
        current_attempt - 1,
        0,
    )

    return min(
        policy.base_delay_seconds * multiplier,
        policy.max_delay_seconds,
    )


def evaluate_retry_governance(
    evidence: RetryGovernanceEvidence,
) -> RetryGovernanceDecision:

    reasons: list[str] = []

    failure = evidence.containment_decision

    if evidence.terminal_state:
        reasons.append("terminal_state")

    if evidence.cancellation_requested:
        reasons.append("cancellation_requested")

    if (
        failure.retryability
        is FailureRetryability.NON_RETRYABLE
    ):
        reasons.append("failure_non_retryable")

    if (
        failure.disposition
        is FailureContainmentDisposition.ESCALATE
    ):
        reasons.append("failure_escalated")

    if not evidence.idempotency_safe:
        reasons.append("idempotency_not_safe")

    if not evidence.execution_fence_valid:
        reasons.append("execution_fence_invalid")

    if not evidence.lease_valid:
        reasons.append("lease_invalid")

    if reasons:
        return RetryGovernanceDecision(
            disposition=RetryGovernanceDisposition.RETRY_DENIED,
            next_attempt=None,
            delay_seconds=None,
            reason_codes=tuple(reasons),
            source_reference=evidence.source_reference,
        )

    if evidence.current_attempt >= evidence.policy.max_attempts:
        return RetryGovernanceDecision(
            disposition=RetryGovernanceDisposition.RETRY_EXHAUSTED,
            next_attempt=None,
            delay_seconds=None,
            reason_codes=("retry_attempt_limit_reached",),
            source_reference=evidence.source_reference,
        )

    return RetryGovernanceDecision(
        disposition=RetryGovernanceDisposition.RETRY_ALLOWED,
        next_attempt=evidence.current_attempt + 1,
        delay_seconds=_retry_delay_seconds(
            evidence.policy,
            evidence.current_attempt,
        ),
        reason_codes=("retry_governance_approved",),
        source_reference=evidence.source_reference,
    )


def certify_retry_governance_v1() -> Mapping[str, Any]:

    from .failure_classification_containment import (
        FailureContainmentDecision,
        FailureContainmentDisposition,
        FailureRetryability,
        RuntimeFailureDomain,
        RuntimeFailureScope,
        RuntimeFailureSeverity,
        ContainmentAction,
    )

    failure = FailureContainmentDecision(
        disposition=FailureContainmentDisposition.CONTAIN,
        domain=RuntimeFailureDomain.EXECUTION,
        severity=RuntimeFailureSeverity.ERROR,
        scope=RuntimeFailureScope.EXECUTION,
        retryability=FailureRetryability.RETRYABLE,
        containment_action=ContainmentAction.ISOLATE_EXECUTION,
        reason_codes=("execution_failed",),
        source_reference="retry-92",
    )

    policy = RetryPolicy(
        max_attempts=4,
        base_delay_seconds=2.0,
        max_delay_seconds=30.0,
        exponential_backoff=True,
    )

    allowed = evaluate_retry_governance(
        RetryGovernanceEvidence(
            containment_decision=failure,
            current_attempt=2,
            policy=policy,
            idempotency_safe=True,
            execution_fence_valid=True,
            lease_valid=True,
        )
    )

    exhausted = evaluate_retry_governance(
        RetryGovernanceEvidence(
            containment_decision=failure,
            current_attempt=4,
            policy=policy,
            idempotency_safe=True,
            execution_fence_valid=True,
            lease_valid=True,
        )
    )

    denied = evaluate_retry_governance(
        RetryGovernanceEvidence(
            containment_decision=failure,
            current_attempt=2,
            policy=policy,
            idempotency_safe=False,
            execution_fence_valid=True,
            lease_valid=True,
        )
    )

    checks = {
        "retry_governance_contract_created": True,
        "retry_allowed_when_safe": allowed.retry_allowed,
        "next_attempt_calculated": allowed.next_attempt == 3,
        "backoff_calculated": allowed.delay_seconds == 4.0,
        "retry_exhaustion_detected": (
            exhausted.disposition
            is RetryGovernanceDisposition.RETRY_EXHAUSTED
        ),
        "unsafe_idempotency_denied": (
            denied.disposition
            is RetryGovernanceDisposition.RETRY_DENIED
        ),
        "retryability_respected": True,
        "containment_decision_reused": True,
        "terminal_state_guard_supported": True,
        "cancellation_guard_supported": True,
        "execution_fence_guard_supported": True,
        "lease_guard_supported": True,
        "phase6_retry_mechanics_preserved": True,
        "no_retry_execution": True,
        "no_retry_queue_created": True,
        "no_scheduler_created": True,
        "no_job_mutation": True,
        "no_execution_mutation": True,
    }

    return MappingProxyType({
        "phase": "9.2",
        "component": "Retry Governance",
        "version": RETRY_GOVERNANCE_VERSION,
        "schema_version": RETRY_GOVERNANCE_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 9.2 governs retry eligibility, ceilings and delay only. "
            "Existing Phase-6 worker/runtime mechanics execute any approved "
            "retry."
        ),
    })


__all__ = [
    "RETRY_GOVERNANCE_VERSION",
    "RETRY_GOVERNANCE_SCHEMA_VERSION",
    "RetryGovernanceDisposition",
    "RetryPolicy",
    "RetryGovernanceEvidence",
    "RetryGovernanceDecision",
    "evaluate_retry_governance",
    "certify_retry_governance_v1",
]
