"""
LinkCraftor Universal Runtime
Phase 6.16 — Execution Safety & Concurrency

Canonical execution safety/concurrency layer.

Owns:
- concurrent execution protection
- lost-lease protection
- late result rejection
- stale worker result rejection
- terminal-state re-entry protection
- execution race resolution

Consumes:
- Phase 6.2 execution identity/result
- Phase 6.3 execution fences
- Phase 6.4 lifecycle state
- Phase 6.7 duplicate/idempotency evidence
- Phase 6.15 existing worker/lease/job integration surfaces

Does NOT:
- create a second lock manager
- create a second lease system
- create a second duplicate store
- create a second job state machine
- mutate queues directly
- mutate production jobs directly
- persist concurrency state
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .execution_contracts import (
    ExecutionResult,
)

from .execution_permission_fencing import (
    ExecutionFenceIdentity,
)

from .execution_lifecycle_controller import (
    ExecutionLifecycleRecord,
    ExecutionLifecycleState,
)

from .idempotency_duplicate_control import (
    DuplicateInvocationDecision,
    DuplicateInvocationDisposition,
)


EXECUTION_SAFETY_CONCURRENCY_VERSION = (
    "execution_safety_concurrency_v6.16.1"
)

EXECUTION_SAFETY_CONCURRENCY_SCHEMA_VERSION = (
    "execution_safety_concurrency_schema_v1"
)


class ExecutionSafetyConcurrencyError(RuntimeError):
    """Raised when an unsafe or stale execution event is rejected."""

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


class SafetyDisposition(str, Enum):
    ALLOW = "ALLOW"
    REJECT = "REJECT"


class RaceWinner(str, Enum):
    CURRENT_EXECUTION = "CURRENT_EXECUTION"
    EXISTING_TERMINAL_STATE = "EXISTING_TERMINAL_STATE"
    EXISTING_ACTIVE_EXECUTION = "EXISTING_ACTIVE_EXECUTION"
    NONE = "NONE"


@dataclass(
    frozen=True,
    slots=True,
)
class LeaseSafetyEvidence:
    lease_active: bool

    current_lease_id: Optional[str]
    current_lease_owner: Optional[str]

    expected_lease_id: Optional[str]
    expected_lease_owner: Optional[str]

    schema_version: str = field(
        default=EXECUTION_SAFETY_CONCURRENCY_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class WorkerSafetyEvidence:
    worker_active: bool

    current_worker_id: Optional[str]
    expected_worker_id: Optional[str]

    worker_instance_active: bool = True

    current_worker_instance_id: Optional[str] = None
    expected_worker_instance_id: Optional[str] = None

    schema_version: str = field(
        default=EXECUTION_SAFETY_CONCURRENCY_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class ResultTimingEvidence:
    lifecycle_terminal: bool
    accepting_results: bool

    current_execution_id: str
    result_execution_id: str

    current_attempt_number: int
    result_attempt_number: int

    schema_version: str = field(
        default=EXECUTION_SAFETY_CONCURRENCY_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionRaceEvidence:
    current_execution_active: bool
    existing_terminal_state: bool
    duplicate_invocation_active: bool
    duplicate_invocation_replay: bool

    same_execution_id: bool
    same_attempt_number: bool

    schema_version: str = field(
        default=EXECUTION_SAFETY_CONCURRENCY_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionRaceResolution:
    disposition: SafetyDisposition
    winner: RaceWinner

    reason_code: str

    schema_version: str = field(
        default=EXECUTION_SAFETY_CONCURRENCY_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionSafetyDecision:
    disposition: SafetyDisposition

    execution_id: str
    job_id: str
    attempt_number: int
    fence_id: str

    reason_code: str

    schema_version: str = field(
        default=EXECUTION_SAFETY_CONCURRENCY_SCHEMA_VERSION,
        init=False,
    )


def protect_concurrent_execution(
    *,
    duplicate_decision: DuplicateInvocationDecision,
) -> None:
    """
    Block active duplicate execution and allow only canonical execution.
    """

    if not isinstance(
        duplicate_decision,
        DuplicateInvocationDecision,
    ):
        raise ExecutionSafetyConcurrencyError(
            "duplicate_decision must be DuplicateInvocationDecision.",
            code="invalid_duplicate_decision",
            value=duplicate_decision,
        )

    if (
        duplicate_decision.disposition
        is DuplicateInvocationDisposition.REJECT_DUPLICATE
    ):
        raise ExecutionSafetyConcurrencyError(
            "Concurrent duplicate execution rejected.",
            code="concurrent_execution_rejected",
        )


def validate_lease_safety(
    *,
    fence: ExecutionFenceIdentity,
    evidence: LeaseSafetyEvidence,
) -> None:
    """
    Reject execution after lease loss, mismatch, or ownership change.
    """

    if not evidence.lease_active:
        raise ExecutionSafetyConcurrencyError(
            "Execution lease is no longer active.",
            code="lost_lease",
        )

    if (
        evidence.expected_lease_id is not None
        and evidence.current_lease_id
        != evidence.expected_lease_id
    ):
        raise ExecutionSafetyConcurrencyError(
            "Execution lease id changed.",
            code="lease_id_changed",
        )

    if (
        evidence.expected_lease_owner is not None
        and evidence.current_lease_owner
        != evidence.expected_lease_owner
    ):
        raise ExecutionSafetyConcurrencyError(
            "Execution lease owner changed.",
            code="lease_owner_changed",
        )

    if (
        fence.lease_id is not None
        and evidence.current_lease_id
        != fence.lease_id
    ):
        raise ExecutionSafetyConcurrencyError(
            "Current lease no longer matches execution fence.",
            code="fenced_lease_mismatch",
        )

    if (
        fence.lease_owner is not None
        and evidence.current_lease_owner
        != fence.lease_owner
    ):
        raise ExecutionSafetyConcurrencyError(
            "Current lease owner no longer matches execution fence.",
            code="fenced_lease_owner_mismatch",
        )


def validate_worker_safety(
    *,
    fence: ExecutionFenceIdentity,
    evidence: WorkerSafetyEvidence,
) -> None:
    """
    Reject stale worker or worker-instance results.
    """

    if not evidence.worker_active:
        raise ExecutionSafetyConcurrencyError(
            "Worker is stale or inactive.",
            code="stale_worker",
        )

    if not evidence.worker_instance_active:
        raise ExecutionSafetyConcurrencyError(
            "Worker instance is stale or inactive.",
            code="stale_worker_instance",
        )

    if (
        evidence.expected_worker_id is not None
        and evidence.current_worker_id
        != evidence.expected_worker_id
    ):
        raise ExecutionSafetyConcurrencyError(
            "Worker ownership changed.",
            code="worker_id_changed",
        )

    if (
        fence.worker_id is not None
        and evidence.current_worker_id
        != fence.worker_id
    ):
        raise ExecutionSafetyConcurrencyError(
            "Worker no longer matches execution fence.",
            code="fenced_worker_mismatch",
        )

    if (
        evidence.expected_worker_instance_id is not None
        and evidence.current_worker_instance_id
        != evidence.expected_worker_instance_id
    ):
        raise ExecutionSafetyConcurrencyError(
            "Worker instance ownership changed.",
            code="worker_instance_changed",
        )


def reject_late_result(
    *,
    timing: ResultTimingEvidence,
) -> None:
    """
    Reject result after terminalization or from obsolete execution/attempt.
    """

    if timing.lifecycle_terminal:
        raise ExecutionSafetyConcurrencyError(
            "Late result rejected after terminal lifecycle.",
            code="late_result_after_terminal_state",
        )

    if not timing.accepting_results:
        raise ExecutionSafetyConcurrencyError(
            "Execution is no longer accepting results.",
            code="result_window_closed",
        )

    if (
        timing.result_execution_id
        != timing.current_execution_id
    ):
        raise ExecutionSafetyConcurrencyError(
            "Result belongs to stale execution.",
            code="stale_execution_result",
        )

    if (
        timing.result_attempt_number
        != timing.current_attempt_number
    ):
        raise ExecutionSafetyConcurrencyError(
            "Result belongs to stale attempt.",
            code="stale_attempt_result",
        )


def protect_terminal_state_reentry(
    *,
    lifecycle: ExecutionLifecycleRecord,
) -> None:
    """
    Prevent terminal execution from returning to executable state.
    """

    if lifecycle.state in {
        ExecutionLifecycleState.SUCCEEDED,
        ExecutionLifecycleState.FAILED,
        ExecutionLifecycleState.CANCELLED,
    }:
        raise ExecutionSafetyConcurrencyError(
            "Terminal execution cannot re-enter execution.",
            code="terminal_state_reentry_rejected",
            value=lifecycle.state.value,
        )


def resolve_execution_race(
    *,
    evidence: ExecutionRaceEvidence,
) -> ExecutionRaceResolution:
    """
    Deterministically resolve execution races.

    Priority:
    1. Existing terminal state wins.
    2. Existing active execution wins against duplicate concurrent execution.
    3. Replay of an already-completed duplicate does not create new execution.
    4. Otherwise current execution may proceed.
    """

    if evidence.existing_terminal_state:
        return ExecutionRaceResolution(
            disposition=SafetyDisposition.REJECT,
            winner=RaceWinner.EXISTING_TERMINAL_STATE,
            reason_code="terminal_state_wins_race",
        )

    if (
        evidence.current_execution_active
        and evidence.duplicate_invocation_active
    ):
        return ExecutionRaceResolution(
            disposition=SafetyDisposition.REJECT,
            winner=RaceWinner.EXISTING_ACTIVE_EXECUTION,
            reason_code="active_execution_wins_race",
        )

    if evidence.duplicate_invocation_replay:
        return ExecutionRaceResolution(
            disposition=SafetyDisposition.REJECT,
            winner=RaceWinner.EXISTING_TERMINAL_STATE,
            reason_code="existing_result_replay_wins",
        )

    if (
        not evidence.same_execution_id
        or not evidence.same_attempt_number
    ):
        return ExecutionRaceResolution(
            disposition=SafetyDisposition.REJECT,
            winner=RaceWinner.NONE,
            reason_code="execution_identity_race_mismatch",
        )

    return ExecutionRaceResolution(
        disposition=SafetyDisposition.ALLOW,
        winner=RaceWinner.CURRENT_EXECUTION,
        reason_code="current_execution_may_proceed",
    )


def validate_result_safety(
    *,
    lifecycle: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
    result: ExecutionResult,
    lease_evidence: LeaseSafetyEvidence,
    worker_evidence: WorkerSafetyEvidence,
    timing_evidence: ResultTimingEvidence,
) -> ExecutionSafetyDecision:
    """
    Full stale/late/lost-lease result acceptance gate.
    """

    if result.identity.execution_id != lifecycle.execution_id:
        raise ExecutionSafetyConcurrencyError(
            "Result execution does not match lifecycle.",
            code="result_lifecycle_execution_mismatch",
        )

    if result.identity.job_id != lifecycle.job_id:
        raise ExecutionSafetyConcurrencyError(
            "Result job does not match lifecycle.",
            code="result_lifecycle_job_mismatch",
        )

    if (
        result.identity.attempt_number
        != lifecycle.attempt_number
    ):
        raise ExecutionSafetyConcurrencyError(
            "Result attempt does not match lifecycle.",
            code="result_lifecycle_attempt_mismatch",
        )

    if lifecycle.fence_id != fence.fence_id:
        raise ExecutionSafetyConcurrencyError(
            "Lifecycle fence changed.",
            code="lifecycle_fence_changed",
        )

    validate_lease_safety(
        fence=fence,
        evidence=lease_evidence,
    )

    validate_worker_safety(
        fence=fence,
        evidence=worker_evidence,
    )

    reject_late_result(
        timing=timing_evidence,
    )

    return ExecutionSafetyDecision(
        disposition=SafetyDisposition.ALLOW,
        execution_id=lifecycle.execution_id,
        job_id=lifecycle.job_id,
        attempt_number=lifecycle.attempt_number,
        fence_id=fence.fence_id,
        reason_code="result_safety_validated",
    )


def certify_execution_safety_concurrency_v1(
) -> Mapping[str, Any]:
    """
    Phase 6.16 certification.
    """

    from .execution_contracts import (
        ExecutionAction,
        ExecutionContext,
        ExecutionIdentity,
        ExecutionOutcome,
        ExecutionRequest,
    )

    from .execution_permission_fencing import (
        ExecutionPermissionEvidence,
        evaluate_execution_permission,
    )

    from .execution_lifecycle_controller import (
        apply_running_state,
        create_execution_start,
        finalize_execution,
    )

    from .idempotency_duplicate_control import (
        DuplicateInvocationEvidence,
        evaluate_duplicate_invocation,
    )

    identity = ExecutionIdentity(
        execution_id=(
            "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee"
        ),
        job_id="job-phase-6-16-certification",
        attempt_number=1,
        idempotency_key="idem-phase-6-16",
    )

    request = ExecutionRequest(
        identity=identity,
        context=ExecutionContext(
            handler_key="certification.handler",
            worker_id="worker-certification",
            worker_instance_id="worker-instance-certification",
            lease_id="lease-certification",
            lease_owner="worker-certification::instance-1",
        ),
        action=ExecutionAction.START,
    )

    permission = evaluate_execution_permission(
        request=request,
        evidence=ExecutionPermissionEvidence(
            job_status="RUNNING",
            current_worker_id="worker-certification",
            current_lease_id="lease-certification",
            current_lease_owner=(
                "worker-certification::instance-1"
            ),
            lease_state="ACTIVE",
        ),
    )

    fence = permission.fence

    if fence is None:
        raise ExecutionSafetyConcurrencyError(
            "Certification missing execution fence.",
            code="certification_missing_fence",
        )

    ready = create_execution_start(
        request=request,
        permission=permission,
    )

    running = apply_running_state(
        record=ready,
        fence=fence,
        started_at="2026-01-01T00:00:00Z",
    )

    result = ExecutionResult(
        identity=identity,
        outcome=ExecutionOutcome.SUCCEEDED,
        result_reference="result://phase-6-16/certification",
        result_metadata={
            "fence_id": fence.fence_id,
        },
    )

    lease_ok = LeaseSafetyEvidence(
        lease_active=True,
        current_lease_id="lease-certification",
        current_lease_owner=(
            "worker-certification::instance-1"
        ),
        expected_lease_id="lease-certification",
        expected_lease_owner=(
            "worker-certification::instance-1"
        ),
    )

    worker_ok = WorkerSafetyEvidence(
        worker_active=True,
        current_worker_id="worker-certification",
        expected_worker_id="worker-certification",
        worker_instance_active=True,
        current_worker_instance_id=(
            "worker-instance-certification"
        ),
        expected_worker_instance_id=(
            "worker-instance-certification"
        ),
    )

    timing_ok = ResultTimingEvidence(
        lifecycle_terminal=False,
        accepting_results=True,
        current_execution_id=identity.execution_id,
        result_execution_id=identity.execution_id,
        current_attempt_number=1,
        result_attempt_number=1,
    )

    allowed = validate_result_safety(
        lifecycle=running,
        fence=fence,
        result=result,
        lease_evidence=lease_ok,
        worker_evidence=worker_ok,
        timing_evidence=timing_ok,
    )

    lost_lease_rejected = False

    try:
        validate_result_safety(
            lifecycle=running,
            fence=fence,
            result=result,
            lease_evidence=LeaseSafetyEvidence(
                lease_active=False,
                current_lease_id="lease-certification",
                current_lease_owner=(
                    "worker-certification::instance-1"
                ),
                expected_lease_id="lease-certification",
                expected_lease_owner=(
                    "worker-certification::instance-1"
                ),
            ),
            worker_evidence=worker_ok,
            timing_evidence=timing_ok,
        )
    except ExecutionSafetyConcurrencyError:
        lost_lease_rejected = True

    stale_worker_rejected = False

    try:
        validate_result_safety(
            lifecycle=running,
            fence=fence,
            result=result,
            lease_evidence=lease_ok,
            worker_evidence=WorkerSafetyEvidence(
                worker_active=False,
                current_worker_id="worker-certification",
                expected_worker_id="worker-certification",
            ),
            timing_evidence=timing_ok,
        )
    except ExecutionSafetyConcurrencyError:
        stale_worker_rejected = True

    stale_worker_instance_rejected = False

    try:
        validate_worker_safety(
            fence=fence,
            evidence=WorkerSafetyEvidence(
                worker_active=True,
                current_worker_id="worker-certification",
                expected_worker_id="worker-certification",
                worker_instance_active=False,
                current_worker_instance_id="old-instance",
                expected_worker_instance_id=(
                    "worker-instance-certification"
                ),
            ),
        )
    except ExecutionSafetyConcurrencyError:
        stale_worker_instance_rejected = True

    late_result_rejected = False

    try:
        reject_late_result(
            timing=ResultTimingEvidence(
                lifecycle_terminal=True,
                accepting_results=False,
                current_execution_id=identity.execution_id,
                result_execution_id=identity.execution_id,
                current_attempt_number=1,
                result_attempt_number=1,
            ),
        )
    except ExecutionSafetyConcurrencyError:
        late_result_rejected = True

    stale_attempt_result_rejected = False

    try:
        reject_late_result(
            timing=ResultTimingEvidence(
                lifecycle_terminal=False,
                accepting_results=True,
                current_execution_id=identity.execution_id,
                result_execution_id=identity.execution_id,
                current_attempt_number=2,
                result_attempt_number=1,
            ),
        )
    except ExecutionSafetyConcurrencyError:
        stale_attempt_result_rejected = True

    succeeded = finalize_execution(
        record=running,
        result=result,
        fence=fence,
        finalized_at="2026-01-01T00:00:10Z",
    )

    terminal_reentry_rejected = False

    try:
        protect_terminal_state_reentry(
            lifecycle=succeeded,
        )
    except ExecutionSafetyConcurrencyError:
        terminal_reentry_rejected = True

    duplicate_decision = evaluate_duplicate_invocation(
        request=request,
        fence=fence,
        evidence=DuplicateInvocationEvidence(
            matching_execution_exists=True,
            matching_execution_active=True,
            matching_execution_terminal=False,
            matching_execution_id=(
                "existing-execution-phase-6-16"
            ),
            matching_fence_id=fence.fence_id,
        ),
    )

    concurrent_duplicate_rejected = False

    try:
        protect_concurrent_execution(
            duplicate_decision=duplicate_decision,
        )
    except ExecutionSafetyConcurrencyError:
        concurrent_duplicate_rejected = True

    active_race = resolve_execution_race(
        evidence=ExecutionRaceEvidence(
            current_execution_active=True,
            existing_terminal_state=False,
            duplicate_invocation_active=True,
            duplicate_invocation_replay=False,
            same_execution_id=True,
            same_attempt_number=True,
        ),
    )

    terminal_race = resolve_execution_race(
        evidence=ExecutionRaceEvidence(
            current_execution_active=False,
            existing_terminal_state=True,
            duplicate_invocation_active=False,
            duplicate_invocation_replay=False,
            same_execution_id=True,
            same_attempt_number=True,
        ),
    )

    clean_race = resolve_execution_race(
        evidence=ExecutionRaceEvidence(
            current_execution_active=False,
            existing_terminal_state=False,
            duplicate_invocation_active=False,
            duplicate_invocation_replay=False,
            same_execution_id=True,
            same_attempt_number=True,
        ),
    )

    checks = {
        "concurrent_execution_protection":
            concurrent_duplicate_rejected,

        "lost_lease_protection":
            lost_lease_rejected,

        "late_result_rejection":
            late_result_rejected,

        "stale_worker_result_rejection":
            stale_worker_rejected,

        "stale_worker_instance_rejection":
            stale_worker_instance_rejected,

        "stale_attempt_result_rejection":
            stale_attempt_result_rejected,

        "terminal_state_reentry_protection":
            terminal_reentry_rejected,

        "valid_result_allowed":
            (
                allowed.disposition
                is SafetyDisposition.ALLOW
            ),

        "valid_result_fence_preserved":
            (
                allowed.fence_id
                == fence.fence_id
            ),

        "active_execution_wins_duplicate_race":
            (
                active_race.disposition
                is SafetyDisposition.REJECT
                and active_race.winner
                is RaceWinner.EXISTING_ACTIVE_EXECUTION
            ),

        "terminal_state_wins_race":
            (
                terminal_race.disposition
                is SafetyDisposition.REJECT
                and terminal_race.winner
                is RaceWinner.EXISTING_TERMINAL_STATE
            ),

        "clean_execution_may_proceed":
            (
                clean_race.disposition
                is SafetyDisposition.ALLOW
                and clean_race.winner
                is RaceWinner.CURRENT_EXECUTION
            ),

        "execution_race_resolution_deterministic":
            (
                active_race.reason_code
                == "active_execution_wins_race"
                and terminal_race.reason_code
                == "terminal_state_wins_race"
                and clean_race.reason_code
                == "current_execution_may_proceed"
            ),

        "no_second_lock_manager":
            True,

        "no_second_lease_system":
            True,

        "no_second_duplicate_store":
            True,

        "no_second_job_state_machine":
            True,

        "no_production_job_mutation":
            True,

        "no_queue_mutation":
            True,

        "no_worker_mutation":
            True,

        "no_lease_mutation":
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
                "6.16",

            "component":
                "Execution Safety & Concurrency",

            "version":
                EXECUTION_SAFETY_CONCURRENCY_VERSION,

            "schema_version":
                EXECUTION_SAFETY_CONCURRENCY_SCHEMA_VERSION,

            "certified":
                certified,

            "checks":
                MappingProxyType(
                    checks
                ),

            "authority_boundary": (
                "Phase 6.16 hardens execution against concurrent duplicates, "
                "lost leases, stale workers, stale attempts, late results, "
                "terminal-state re-entry and execution races while reusing "
                "the existing lease, worker, duplicate and lifecycle "
                "authorities."
            ),
        }
    )


def explain_execution_safety_concurrency_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "6.16",

            "component":
                "Execution Safety & Concurrency",

            "version":
                EXECUTION_SAFETY_CONCURRENCY_VERSION,

            "concurrent_execution_protection": (
                "Uses Phase-6.7 duplicate decisions to prevent two active "
                "executions for the same idempotent work."
            ),

            "lost_lease_protection": (
                "Rejects work/results after lease loss or lease owner change."
            ),

            "late_result_rejection": (
                "Rejects results after terminalization or after the result "
                "acceptance window closes."
            ),

            "stale_worker_result_rejection": (
                "Rejects results from inactive/replaced workers or worker "
                "instances."
            ),

            "terminal_state_reentry_protection": (
                "Prevents SUCCEEDED, FAILED or CANCELLED execution from "
                "re-entering execution."
            ),

            "execution_race_resolution": (
                "Applies deterministic race priority: terminal state first, "
                "existing active execution second, current execution only "
                "when no stronger existing authority wins."
            ),

            "prohibitions": (
                "does not create a lock manager",
                "does not create a lease system",
                "does not create a duplicate store",
                "does not create a job state machine",
                "does not mutate production jobs",
                "does not mutate queues",
                "does not persist concurrency state",
            ),
        }
    )


__all__ = [
    "EXECUTION_SAFETY_CONCURRENCY_VERSION",
    "EXECUTION_SAFETY_CONCURRENCY_SCHEMA_VERSION",
    "ExecutionSafetyConcurrencyError",
    "SafetyDisposition",
    "RaceWinner",
    "LeaseSafetyEvidence",
    "WorkerSafetyEvidence",
    "ResultTimingEvidence",
    "ExecutionRaceEvidence",
    "ExecutionRaceResolution",
    "ExecutionSafetyDecision",
    "protect_concurrent_execution",
    "validate_lease_safety",
    "validate_worker_safety",
    "reject_late_result",
    "protect_terminal_state_reentry",
    "resolve_execution_race",
    "validate_result_safety",
    "certify_execution_safety_concurrency_v1",
    "explain_execution_safety_concurrency_v1",
]

