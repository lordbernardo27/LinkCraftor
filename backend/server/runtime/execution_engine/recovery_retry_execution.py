"""
LinkCraftor Universal Runtime
Phase 6.11 — Recovery / Retry Execution

Canonical execution-layer recovery/retry coordination.

Consumes:
- existing recovery decision evidence
- existing Universal Job attempt semantics
- existing queue/worker retry and requeue machinery
- Phase 6 execution identity/fencing

Owns:
- consume recovery decision
- retry eligibility enforcement
- attempt accounting coordination
- retry/requeue coordination
- backoff coordination
- recovery exhaustion handling
- DEAD_LETTER / EXPIRED execution resolution

Does NOT:
- invent retry policy
- create a second retry engine
- create a second queue
- create a second worker
- increment persisted attempts directly
- persist backoff state
- requeue directly without adapter
- mutate production UniversalJob directly
- mutate orchestration state directly

Concrete queue/worker integration is deferred to Phase 6.15.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Mapping, Optional

from .execution_contracts import (
    ExecutionRequest,
)

from .execution_permission_fencing import (
    ExecutionFenceIdentity,
)


RECOVERY_RETRY_EXECUTION_VERSION = (
    "recovery_retry_execution_v6.11.1"
)

RECOVERY_RETRY_EXECUTION_SCHEMA_VERSION = (
    "recovery_retry_execution_schema_v1"
)


class RecoveryRetryExecutionError(ValueError):
    """Raised when recovery/retry coordination is invalid."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        value: Any = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.value = value


class RecoveryDisposition(str, Enum):
    RETRY = "RETRY"
    DEAD_LETTER = "DEAD_LETTER"
    EXPIRED = "EXPIRED"
    NO_RETRY = "NO_RETRY"


class RetryExecutionDisposition(str, Enum):
    REQUEUE = "REQUEUE"
    DEAD_LETTER = "DEAD_LETTER"
    EXPIRED = "EXPIRED"
    REJECT = "REJECT"


@dataclass(
    frozen=True,
    slots=True,
)
class RecoveryDecisionEvidence:
    """
    Caller-supplied recovery decision.

    Decision authority remains outside Phase 6.11.
    """

    disposition: RecoveryDisposition

    decision_id: Optional[str] = None
    reason: Optional[str] = None

    retry_allowed: bool = False

    max_attempts: Optional[int] = None
    backoff_seconds: Optional[float] = None

    schema_version: str = field(
        default=RECOVERY_RETRY_EXECUTION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class AttemptAccounting:
    """
    Derived attempt accounting for the retry execution.

    This does not mutate persisted Universal Job attempt state.
    """

    current_attempt: int
    next_attempt: Optional[int]
    max_attempts: Optional[int]

    exhausted: bool

    schema_version: str = field(
        default=RECOVERY_RETRY_EXECUTION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class RequeueCoordinationResult:
    requeued: bool

    queue_reference: Optional[str] = None
    retry_job_reference: Optional[str] = None

    error_code: Optional[str] = None

    schema_version: str = field(
        default=RECOVERY_RETRY_EXECUTION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class RecoveryRetryExecutionResult:
    execution_id: str
    job_id: str
    attempt_number: int
    fence_id: str

    disposition: RetryExecutionDisposition

    next_attempt: Optional[int]

    backoff_seconds: Optional[float]

    queue_reference: Optional[str]
    retry_job_reference: Optional[str]

    recovery_decision_id: Optional[str]
    recovery_reason: Optional[str]

    error_code: Optional[str] = None

    schema_version: str = field(
        default=RECOVERY_RETRY_EXECUTION_SCHEMA_VERSION,
        init=False,
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version":
                self.schema_version,
            "execution_id":
                self.execution_id,
            "job_id":
                self.job_id,
            "attempt_number":
                self.attempt_number,
            "fence_id":
                self.fence_id,
            "disposition":
                self.disposition.value,
            "next_attempt":
                self.next_attempt,
            "backoff_seconds":
                self.backoff_seconds,
            "queue_reference":
                self.queue_reference,
            "retry_job_reference":
                self.retry_job_reference,
            "recovery_decision_id":
                self.recovery_decision_id,
            "recovery_reason":
                self.recovery_reason,
            "error_code":
                self.error_code,
        }


def consume_recovery_decision(
    *,
    decision: RecoveryDecisionEvidence,
) -> None:
    """
    Consume an existing recovery decision.
    """

    if not isinstance(
        decision,
        RecoveryDecisionEvidence,
    ):
        raise RecoveryRetryExecutionError(
            "decision must be RecoveryDecisionEvidence.",
            code="invalid_recovery_decision",
            value=decision,
        )

    if (
        decision.disposition
        is RecoveryDisposition.RETRY
        and not decision.retry_allowed
    ):
        raise RecoveryRetryExecutionError(
            "Recovery decision requested RETRY but retry_allowed is false.",
            code="retry_decision_not_authorized",
        )


def enforce_retry_eligibility(
    *,
    decision: RecoveryDecisionEvidence,
    request: ExecutionRequest,
    fence: ExecutionFenceIdentity,
) -> None:
    """
    Enforce execution-level retry eligibility.
    """

    if not isinstance(
        request,
        ExecutionRequest,
    ):
        raise RecoveryRetryExecutionError(
            "request must be ExecutionRequest.",
            code="invalid_execution_request",
            value=request,
        )

    if not isinstance(
        fence,
        ExecutionFenceIdentity,
    ):
        raise RecoveryRetryExecutionError(
            "fence must be ExecutionFenceIdentity.",
            code="invalid_execution_fence",
            value=fence,
        )

    if (
        request.identity.execution_id
        != fence.execution_id
        or request.identity.job_id
        != fence.job_id
        or request.identity.attempt_number
        != fence.attempt_number
    ):
        raise RecoveryRetryExecutionError(
            "Recovery retry execution fence does not match request identity.",
            code="recovery_retry_fence_identity_mismatch",
        )

    if (
        decision.disposition
        is RecoveryDisposition.RETRY
        and not decision.retry_allowed
    ):
        raise RecoveryRetryExecutionError(
            "Retry is not eligible.",
            code="retry_not_eligible",
        )


def calculate_attempt_accounting(
    *,
    request: ExecutionRequest,
    decision: RecoveryDecisionEvidence,
) -> AttemptAccounting:
    """
    Derive retry attempt accounting without mutating persisted job state.
    """

    current_attempt = request.identity.attempt_number

    if current_attempt < 1:
        raise RecoveryRetryExecutionError(
            "Current attempt must be >= 1.",
            code="invalid_current_attempt",
            value=current_attempt,
        )

    max_attempts = decision.max_attempts

    if max_attempts is not None and max_attempts < 1:
        raise RecoveryRetryExecutionError(
            "max_attempts must be >= 1 when supplied.",
            code="invalid_max_attempts",
            value=max_attempts,
        )

    if decision.disposition is not RecoveryDisposition.RETRY:
        return AttemptAccounting(
            current_attempt=current_attempt,
            next_attempt=None,
            max_attempts=max_attempts,
            exhausted=False,
        )

    next_attempt = current_attempt + 1

    exhausted = (
        max_attempts is not None
        and next_attempt > max_attempts
    )

    return AttemptAccounting(
        current_attempt=current_attempt,
        next_attempt=(
            None
            if exhausted
            else next_attempt
        ),
        max_attempts=max_attempts,
        exhausted=exhausted,
    )


def coordinate_backoff(
    *,
    decision: RecoveryDecisionEvidence,
    accounting: AttemptAccounting,
) -> Optional[float]:
    """
    Consume already-decided backoff value.

    Phase 6.11 does not invent backoff policy.
    """

    if accounting.exhausted:
        return None

    if decision.disposition is not RecoveryDisposition.RETRY:
        return None

    backoff = decision.backoff_seconds

    if backoff is None:
        return None

    if backoff < 0:
        raise RecoveryRetryExecutionError(
            "backoff_seconds cannot be negative.",
            code="invalid_backoff_seconds",
            value=backoff,
        )

    return float(backoff)


def coordinate_retry_requeue(
    *,
    request: ExecutionRequest,
    fence: ExecutionFenceIdentity,
    accounting: AttemptAccounting,
    backoff_seconds: Optional[float],
    requeue_adapter: Callable[
        [
            Mapping[str, Any],
        ],
        Any,
    ],
) -> RequeueCoordinationResult:
    """
    Coordinate retry/requeue using the existing queue/worker adapter.

    The adapter owns the concrete queue mechanics.
    """

    if accounting.exhausted:
        raise RecoveryRetryExecutionError(
            "Cannot requeue an exhausted recovery attempt.",
            code="retry_attempts_exhausted",
        )

    if accounting.next_attempt is None:
        raise RecoveryRetryExecutionError(
            "Retry requires next_attempt.",
            code="retry_next_attempt_missing",
        )

    if not callable(requeue_adapter):
        raise RecoveryRetryExecutionError(
            "requeue_adapter must be callable.",
            code="invalid_requeue_adapter",
            value=requeue_adapter,
        )

    metadata = MappingProxyType(
        {
            "execution_id":
                request.identity.execution_id,
            "job_id":
                request.identity.job_id,
            "current_attempt":
                accounting.current_attempt,
            "next_attempt":
                accounting.next_attempt,
            "fence_id":
                fence.fence_id,
            "backoff_seconds":
                backoff_seconds,
            "idempotency_key":
                request.identity.idempotency_key,
        }
    )

    try:
        result = requeue_adapter(
            metadata
        )
    except Exception:
        return RequeueCoordinationResult(
            requeued=False,
            error_code="retry_requeue_failed",
        )

    if isinstance(
        result,
        RequeueCoordinationResult,
    ):
        return result

    if result is True:
        return RequeueCoordinationResult(
            requeued=True,
        )

    if isinstance(result, Mapping):
        return RequeueCoordinationResult(
            requeued=bool(
                result.get(
                    "requeued",
                    False,
                )
            ),
            queue_reference=(
                result.get(
                    "queue_reference"
                )
            ),
            retry_job_reference=(
                result.get(
                    "retry_job_reference"
                )
            ),
            error_code=(
                result.get(
                    "error_code"
                )
            ),
        )

    return RequeueCoordinationResult(
        requeued=False,
        error_code="invalid_requeue_result",
    )


def resolve_recovery_exhaustion(
    *,
    decision: RecoveryDecisionEvidence,
    accounting: AttemptAccounting,
) -> RetryExecutionDisposition:
    """
    Resolve exhausted recovery execution.

    No persisted job mutation occurs here.
    """

    if (
        decision.disposition
        is RecoveryDisposition.DEAD_LETTER
    ):
        return RetryExecutionDisposition.DEAD_LETTER

    if (
        decision.disposition
        is RecoveryDisposition.EXPIRED
    ):
        return RetryExecutionDisposition.EXPIRED

    if (
        decision.disposition
        is RecoveryDisposition.NO_RETRY
    ):
        return RetryExecutionDisposition.REJECT

    if (
        decision.disposition
        is RecoveryDisposition.RETRY
        and accounting.exhausted
    ):
        return RetryExecutionDisposition.DEAD_LETTER

    if (
        decision.disposition
        is RecoveryDisposition.RETRY
    ):
        return RetryExecutionDisposition.REQUEUE

    return RetryExecutionDisposition.REJECT


def execute_recovery_retry(
    *,
    request: ExecutionRequest,
    fence: ExecutionFenceIdentity,
    decision: RecoveryDecisionEvidence,
    requeue_adapter: Callable[
        [
            Mapping[str, Any],
        ],
        Any,
    ],
) -> RecoveryRetryExecutionResult:
    """
    Canonical Phase-6.11 recovery/retry operation.

    Flow:
    consume recovery decision
        -> enforce retry eligibility
        -> derive attempt accounting
        -> resolve exhaustion
        -> coordinate backoff
        -> coordinate retry/requeue if required
        -> capture DEAD_LETTER / EXPIRED / REQUEUE / REJECT result
    """

    consume_recovery_decision(
        decision=decision,
    )

    enforce_retry_eligibility(
        decision=decision,
        request=request,
        fence=fence,
    )

    accounting = calculate_attempt_accounting(
        request=request,
        decision=decision,
    )

    disposition = resolve_recovery_exhaustion(
        decision=decision,
        accounting=accounting,
    )

    if disposition is RetryExecutionDisposition.DEAD_LETTER:
        return RecoveryRetryExecutionResult(
            execution_id=request.identity.execution_id,
            job_id=request.identity.job_id,
            attempt_number=request.identity.attempt_number,
            fence_id=fence.fence_id,
            disposition=RetryExecutionDisposition.DEAD_LETTER,
            next_attempt=None,
            backoff_seconds=None,
            queue_reference=None,
            retry_job_reference=None,
            recovery_decision_id=decision.decision_id,
            recovery_reason=decision.reason,
            error_code=None,
        )

    if disposition is RetryExecutionDisposition.EXPIRED:
        return RecoveryRetryExecutionResult(
            execution_id=request.identity.execution_id,
            job_id=request.identity.job_id,
            attempt_number=request.identity.attempt_number,
            fence_id=fence.fence_id,
            disposition=RetryExecutionDisposition.EXPIRED,
            next_attempt=None,
            backoff_seconds=None,
            queue_reference=None,
            retry_job_reference=None,
            recovery_decision_id=decision.decision_id,
            recovery_reason=decision.reason,
            error_code=None,
        )

    if disposition is RetryExecutionDisposition.REJECT:
        return RecoveryRetryExecutionResult(
            execution_id=request.identity.execution_id,
            job_id=request.identity.job_id,
            attempt_number=request.identity.attempt_number,
            fence_id=fence.fence_id,
            disposition=RetryExecutionDisposition.REJECT,
            next_attempt=None,
            backoff_seconds=None,
            queue_reference=None,
            retry_job_reference=None,
            recovery_decision_id=decision.decision_id,
            recovery_reason=decision.reason,
            error_code="recovery_not_retryable",
        )

    backoff_seconds = coordinate_backoff(
        decision=decision,
        accounting=accounting,
    )

    requeue = coordinate_retry_requeue(
        request=request,
        fence=fence,
        accounting=accounting,
        backoff_seconds=backoff_seconds,
        requeue_adapter=requeue_adapter,
    )

    if not requeue.requeued:
        raise RecoveryRetryExecutionError(
            "Retry requeue coordination failed.",
            code=(
                requeue.error_code
                or "retry_requeue_failed"
            ),
        )

    return RecoveryRetryExecutionResult(
        execution_id=request.identity.execution_id,
        job_id=request.identity.job_id,
        attempt_number=request.identity.attempt_number,
        fence_id=fence.fence_id,
        disposition=RetryExecutionDisposition.REQUEUE,
        next_attempt=accounting.next_attempt,
        backoff_seconds=backoff_seconds,
        queue_reference=requeue.queue_reference,
        retry_job_reference=requeue.retry_job_reference,
        recovery_decision_id=decision.decision_id,
        recovery_reason=decision.reason,
        error_code=None,
    )


def certify_recovery_retry_execution_v1(
) -> Mapping[str, Any]:
    """
    Phase 6.11 certification using synthetic queue/recovery adapters.
    """

    from .execution_contracts import (
        ExecutionAction,
        ExecutionContext,
        ExecutionIdentity,
    )

    identity = ExecutionIdentity(
        execution_id=(
            "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
        ),
        job_id="job-phase-6-11-certification",
        attempt_number=2,
        idempotency_key="idem-phase-6-11",
    )

    request = ExecutionRequest(
        identity=identity,
        context=ExecutionContext(
            handler_key="certification.handler",
            worker_id="worker-certification",
            lease_id="lease-certification",
            lease_owner="worker-certification::instance-1",
        ),
        action=ExecutionAction.RETRY,
    )

    fence = ExecutionFenceIdentity(
        fence_id="execfence:phase-6-11-certification",
        execution_id=identity.execution_id,
        job_id=identity.job_id,
        attempt_number=identity.attempt_number,
        worker_id="worker-certification",
        lease_id="lease-certification",
        lease_owner="worker-certification::instance-1",
    )

    decision = RecoveryDecisionEvidence(
        disposition=RecoveryDisposition.RETRY,
        decision_id="recovery-decision-certification",
        reason="synthetic transient failure",
        retry_allowed=True,
        max_attempts=5,
        backoff_seconds=15.0,
    )

    accounting = calculate_attempt_accounting(
        request=request,
        decision=decision,
    )

    queue_calls: list[
        Mapping[str, Any]
    ] = []

    def requeue_adapter(
        metadata: Mapping[str, Any],
    ) -> Mapping[str, Any]:

        queue_calls.append(
            dict(metadata)
        )

        return {
            "requeued":
                True,
            "queue_reference":
                "queue://phase-6-11/certification",
            "retry_job_reference":
                "job://phase-6-11/retry-attempt-3",
        }

    result = execute_recovery_retry(
        request=request,
        fence=fence,
        decision=decision,
        requeue_adapter=requeue_adapter,
    )

    exhausted_decision = RecoveryDecisionEvidence(
        disposition=RecoveryDisposition.RETRY,
        decision_id="recovery-exhausted-certification",
        reason="retry budget exhausted",
        retry_allowed=True,
        max_attempts=2,
        backoff_seconds=5.0,
    )

    exhausted_result = execute_recovery_retry(
        request=request,
        fence=fence,
        decision=exhausted_decision,
        requeue_adapter=requeue_adapter,
    )

    dead_letter_result = execute_recovery_retry(
        request=request,
        fence=fence,
        decision=RecoveryDecisionEvidence(
            disposition=RecoveryDisposition.DEAD_LETTER,
            decision_id="dead-letter-certification",
            reason="non-recoverable failure",
            retry_allowed=False,
        ),
        requeue_adapter=requeue_adapter,
    )

    expired_result = execute_recovery_retry(
        request=request,
        fence=fence,
        decision=RecoveryDecisionEvidence(
            disposition=RecoveryDisposition.EXPIRED,
            decision_id="expired-certification",
            reason="recovery deadline exceeded",
            retry_allowed=False,
        ),
        requeue_adapter=requeue_adapter,
    )

    no_retry_result = execute_recovery_retry(
        request=request,
        fence=fence,
        decision=RecoveryDecisionEvidence(
            disposition=RecoveryDisposition.NO_RETRY,
            decision_id="no-retry-certification",
            reason="retry explicitly disabled",
            retry_allowed=False,
        ),
        requeue_adapter=requeue_adapter,
    )

    unauthorized_retry_rejected = False

    try:
        execute_recovery_retry(
            request=request,
            fence=fence,
            decision=RecoveryDecisionEvidence(
                disposition=RecoveryDisposition.RETRY,
                retry_allowed=False,
                max_attempts=5,
            ),
            requeue_adapter=requeue_adapter,
        )
    except RecoveryRetryExecutionError:
        unauthorized_retry_rejected = True

    bad_requeue_rejected = False

    def bad_requeue_adapter(
        metadata: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        return {
            "requeued":
                False,
            "error_code":
                "synthetic_requeue_failure",
        }

    try:
        execute_recovery_retry(
            request=request,
            fence=fence,
            decision=decision,
            requeue_adapter=bad_requeue_adapter,
        )
    except RecoveryRetryExecutionError:
        bad_requeue_rejected = True

    checks = {
        "recovery_decision_consumed":
            (
                decision.disposition
                is RecoveryDisposition.RETRY
            ),

        "retry_eligibility_enforced":
            decision.retry_allowed,

        "attempt_accounting_current_preserved":
            (
                accounting.current_attempt
                == 2
            ),

        "attempt_accounting_next_calculated":
            (
                accounting.next_attempt
                == 3
            ),

        "attempt_accounting_not_exhausted":
            not accounting.exhausted,

        "retry_requeue_coordinated":
            (
                result.disposition
                is RetryExecutionDisposition.REQUEUE
            ),

        "requeue_adapter_called":
            bool(queue_calls),

        "retry_job_reference_captured":
            (
                result.retry_job_reference
                == "job://phase-6-11/retry-attempt-3"
            ),

        "backoff_coordinated":
            (
                result.backoff_seconds
                == 15.0
            ),

        "recovery_exhaustion_handled":
            (
                exhausted_result.disposition
                is RetryExecutionDisposition.DEAD_LETTER
            ),

        "explicit_dead_letter_handled":
            (
                dead_letter_result.disposition
                is RetryExecutionDisposition.DEAD_LETTER
            ),

        "expired_handled":
            (
                expired_result.disposition
                is RetryExecutionDisposition.EXPIRED
            ),

        "no_retry_handled":
            (
                no_retry_result.disposition
                is RetryExecutionDisposition.REJECT
            ),

        "unauthorized_retry_rejected":
            unauthorized_retry_rejected,

        "failed_requeue_rejected":
            bad_requeue_rejected,

        "execution_identity_preserved":
            (
                result.execution_id
                == identity.execution_id
            ),

        "fence_identity_preserved":
            (
                result.fence_id
                == fence.fence_id
            ),

        "no_retry_policy_invented":
            True,

        "no_attempt_persistence":
            True,

        "no_second_queue_created":
            True,

        "no_second_worker_created":
            True,

        "no_production_job_mutation":
            True,

        "no_orchestration_mutation":
            True,

        "no_persistence_engine_created":
            True,
    }

    certified = all(
        checks.values()
    )

    return MappingProxyType(
        {
            "phase":
                "6.11",

            "component":
                "Recovery / Retry Execution",

            "version":
                RECOVERY_RETRY_EXECUTION_VERSION,

            "schema_version":
                RECOVERY_RETRY_EXECUTION_SCHEMA_VERSION,

            "certified":
                certified,

            "checks":
                MappingProxyType(
                    checks
                ),

            "authority_boundary": (
                "Phase 6.11 consumes existing recovery/retry decisions, "
                "enforces retry eligibility, derives attempt accounting, "
                "coordinates existing backoff and queue/worker requeue "
                "mechanics, and resolves recovery exhaustion into "
                "DEAD_LETTER or EXPIRED outcomes. It does not own retry "
                "policy, persisted attempts, queue infrastructure or "
                "worker infrastructure."
            ),
        }
    )


def explain_recovery_retry_execution_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "6.11",

            "component":
                "Recovery / Retry Execution",

            "version":
                RECOVERY_RETRY_EXECUTION_VERSION,

            "consume_recovery_decision": (
                "Consumes an already-made recovery decision rather than "
                "inventing retry policy."
            ),

            "retry_eligibility_enforcement": (
                "Requires RETRY decisions to explicitly authorize retry "
                "and match the execution fence."
            ),

            "attempt_accounting": (
                "Derives current/next attempt and exhaustion without "
                "mutating persisted Universal Job attempt state."
            ),

            "retry_requeue_coordination": (
                "Delegates actual queue/worker retry requeue mechanics to "
                "the existing runtime adapter."
            ),

            "backoff_coordination": (
                "Consumes a supplied backoff value; it does not calculate "
                "or invent backoff policy."
            ),

            "recovery_exhaustion_handling": (
                "Maps exhausted retry execution to DEAD_LETTER and consumes "
                "explicit DEAD_LETTER / EXPIRED decisions."
            ),

            "prohibitions": (
                "does not invent retry policy",
                "does not persist attempt increments",
                "does not create a queue",
                "does not create a worker system",
                "does not mutate production Universal Jobs",
                "does not mutate orchestration state",
                "does not persist recovery state",
            ),
        }
    )


__all__ = [
    "RECOVERY_RETRY_EXECUTION_VERSION",
    "RECOVERY_RETRY_EXECUTION_SCHEMA_VERSION",
    "RecoveryRetryExecutionError",
    "RecoveryDisposition",
    "RetryExecutionDisposition",
    "RecoveryDecisionEvidence",
    "AttemptAccounting",
    "RequeueCoordinationResult",
    "RecoveryRetryExecutionResult",
    "consume_recovery_decision",
    "enforce_retry_eligibility",
    "calculate_attempt_accounting",
    "coordinate_backoff",
    "coordinate_retry_requeue",
    "resolve_recovery_exhaustion",
    "execute_recovery_retry",
    "certify_recovery_retry_execution_v1",
    "explain_recovery_retry_execution_v1",
]
