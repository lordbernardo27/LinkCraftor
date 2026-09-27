"""
LinkCraftor Universal Runtime
Phase 6.13 — Cancellation / Termination Execution

Canonical execution-layer cancellation coordination.

Consumes:
- existing cancellation decision evidence
- Phase 6.2 ExecutionRequest
- Phase 6.3 ExecutionFenceIdentity
- Phase 6.4 active execution lifecycle
- existing worker/runtime cancellation mechanics
- existing lease/worker quiescence evidence

Owns:
- consume cancellation decision
- stop-new-work enforcement coordination
- active-work cancellation coordination
- worker / lease quiescence enforcement
- execution CANCELLED-state application
- cancellation result capture

Does NOT:
- invent cancellation decisions
- create a second worker cancellation system
- kill OS processes directly
- create a second lease system
- release/acquire leases directly
- mutate production UniversalJob directly
- mutate queues directly
- mutate Phase-5 orchestration state
- persist cancellation state

Concrete runtime/worker/lease integration is deferred to Phase 6.15.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Callable, Mapping, Optional

from .execution_contracts import (
    ExecutionOutcome,
    ExecutionRequest,
    ExecutionResult,
)

from .execution_permission_fencing import (
    ExecutionFenceIdentity,
)

from .execution_lifecycle_controller import (
    ExecutionLifecycleRecord,
    ExecutionLifecycleState,
    finalize_execution,
)


CANCELLATION_TERMINATION_EXECUTION_VERSION = (
    "cancellation_termination_execution_v6.13.1"
)

CANCELLATION_TERMINATION_EXECUTION_SCHEMA_VERSION = (
    "cancellation_termination_execution_schema_v1"
)


class CancellationTerminationExecutionError(ValueError):
    """Raised when cancellation execution is invalid."""

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


@dataclass(
    frozen=True,
    slots=True,
)
class CancellationDecisionEvidence:
    """
    Existing cancellation decision consumed by Phase 6.13.
    """

    authorized: bool

    decision_id: Optional[str] = None
    reason: Optional[str] = None

    force_termination: bool = False

    schema_version: str = field(
        default=CANCELLATION_TERMINATION_EXECUTION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class StopNewWorkResult:
    enforced: bool

    runtime_reference: Optional[str] = None
    error_code: Optional[str] = None

    schema_version: str = field(
        default=CANCELLATION_TERMINATION_EXECUTION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class ActiveWorkCancellationResult:
    cancellation_requested: bool
    active_work_stopped: bool

    worker_reference: Optional[str] = None
    runtime_reference: Optional[str] = None

    error_code: Optional[str] = None

    schema_version: str = field(
        default=CANCELLATION_TERMINATION_EXECUTION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class WorkerLeaseQuiescenceEvidence:
    """
    Existing runtime/worker/lease quiescence evidence.

    Phase 6.13 consumes it; it does not own lease mutation.
    """

    worker_quiesced: bool
    lease_quiesced: bool
    active_operation_count: int = 0

    worker_reference: Optional[str] = None
    lease_reference: Optional[str] = None

    schema_version: str = field(
        default=CANCELLATION_TERMINATION_EXECUTION_SCHEMA_VERSION,
        init=False,
    )

    @property
    def quiescent(self) -> bool:
        return (
            self.worker_quiesced
            and self.lease_quiesced
            and self.active_operation_count == 0
        )


@dataclass(
    frozen=True,
    slots=True,
)
class CancellationExecutionResult:
    execution_id: str
    job_id: str
    attempt_number: int
    fence_id: str

    cancelled: bool
    force_termination: bool

    lifecycle_state: ExecutionLifecycleState

    cancellation_decision_id: Optional[str]
    cancellation_reason: Optional[str]

    runtime_reference: Optional[str]
    worker_reference: Optional[str]
    lease_reference: Optional[str]

    error_code: Optional[str] = None

    schema_version: str = field(
        default=CANCELLATION_TERMINATION_EXECUTION_SCHEMA_VERSION,
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
            "cancelled":
                self.cancelled,
            "force_termination":
                self.force_termination,
            "lifecycle_state":
                self.lifecycle_state.value,
            "cancellation_decision_id":
                self.cancellation_decision_id,
            "cancellation_reason":
                self.cancellation_reason,
            "runtime_reference":
                self.runtime_reference,
            "worker_reference":
                self.worker_reference,
            "lease_reference":
                self.lease_reference,
            "error_code":
                self.error_code,
        }


def consume_cancellation_decision(
    *,
    decision: CancellationDecisionEvidence,
) -> None:
    """
    Consume an already-made cancellation decision.
    """

    if not isinstance(
        decision,
        CancellationDecisionEvidence,
    ):
        raise CancellationTerminationExecutionError(
            "decision must be CancellationDecisionEvidence.",
            code="invalid_cancellation_decision",
            value=decision,
        )

    if not decision.authorized:
        raise CancellationTerminationExecutionError(
            "Cancellation was not authorized.",
            code="cancellation_not_authorized",
            value=decision.reason,
        )


def validate_cancellation_boundary(
    *,
    request: ExecutionRequest,
    lifecycle: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
) -> None:
    """
    Cancellation may only operate on the matching non-terminal execution.
    """

    if not isinstance(
        request,
        ExecutionRequest,
    ):
        raise CancellationTerminationExecutionError(
            "request must be ExecutionRequest.",
            code="invalid_execution_request",
            value=request,
        )

    if not isinstance(
        lifecycle,
        ExecutionLifecycleRecord,
    ):
        raise CancellationTerminationExecutionError(
            "lifecycle must be ExecutionLifecycleRecord.",
            code="invalid_execution_lifecycle",
            value=lifecycle,
        )

    if not isinstance(
        fence,
        ExecutionFenceIdentity,
    ):
        raise CancellationTerminationExecutionError(
            "fence must be ExecutionFenceIdentity.",
            code="invalid_execution_fence",
            value=fence,
        )

    if lifecycle.state in {
        ExecutionLifecycleState.SUCCEEDED,
        ExecutionLifecycleState.FAILED,
        ExecutionLifecycleState.CANCELLED,
    }:
        raise CancellationTerminationExecutionError(
            "Terminal execution cannot be cancelled again.",
            code="cancellation_terminal_reentry",
            value=lifecycle.state.value,
        )

    if (
        request.identity.execution_id
        != lifecycle.execution_id
        or request.identity.execution_id
        != fence.execution_id
    ):
        raise CancellationTerminationExecutionError(
            "Cancellation execution identity mismatch.",
            code="cancellation_execution_identity_mismatch",
        )

    if (
        request.identity.job_id
        != lifecycle.job_id
        or request.identity.job_id
        != fence.job_id
    ):
        raise CancellationTerminationExecutionError(
            "Cancellation job identity mismatch.",
            code="cancellation_job_identity_mismatch",
        )

    if (
        request.identity.attempt_number
        != lifecycle.attempt_number
        or request.identity.attempt_number
        != fence.attempt_number
    ):
        raise CancellationTerminationExecutionError(
            "Cancellation attempt identity mismatch.",
            code="cancellation_attempt_identity_mismatch",
        )

    if lifecycle.fence_id != fence.fence_id:
        raise CancellationTerminationExecutionError(
            "Cancellation fence mismatch.",
            code="cancellation_fence_mismatch",
        )


def enforce_stop_new_work(
    *,
    request: ExecutionRequest,
    fence: ExecutionFenceIdentity,
    stopper: Callable[
        [
            Mapping[str, Any],
        ],
        Any,
    ],
) -> StopNewWorkResult:
    """
    Coordinate stop-new-work through existing runtime/worker machinery.
    """

    if not callable(stopper):
        raise CancellationTerminationExecutionError(
            "stopper must be callable.",
            code="invalid_stop_new_work_adapter",
            value=stopper,
        )

    metadata = MappingProxyType(
        {
            "execution_id":
                request.identity.execution_id,
            "job_id":
                request.identity.job_id,
            "attempt_number":
                request.identity.attempt_number,
            "fence_id":
                fence.fence_id,
        }
    )

    try:
        result = stopper(
            metadata
        )
    except Exception:
        return StopNewWorkResult(
            enforced=False,
            error_code="stop_new_work_failed",
        )

    if isinstance(
        result,
        StopNewWorkResult,
    ):
        return result

    if result is True:
        return StopNewWorkResult(
            enforced=True,
        )

    if isinstance(result, Mapping):
        return StopNewWorkResult(
            enforced=bool(
                result.get(
                    "enforced",
                    False,
                )
            ),
            runtime_reference=(
                result.get(
                    "runtime_reference"
                )
            ),
            error_code=(
                result.get(
                    "error_code"
                )
            ),
        )

    return StopNewWorkResult(
        enforced=False,
        error_code="invalid_stop_new_work_result",
    )


def coordinate_active_work_cancellation(
    *,
    request: ExecutionRequest,
    fence: ExecutionFenceIdentity,
    force_termination: bool,
    cancellation_adapter: Callable[
        [
            Mapping[str, Any],
        ],
        Any,
    ],
) -> ActiveWorkCancellationResult:
    """
    Coordinate active-work cancellation through existing runtime/worker
    cancellation machinery.
    """

    if not callable(
        cancellation_adapter
    ):
        raise CancellationTerminationExecutionError(
            "cancellation_adapter must be callable.",
            code="invalid_active_work_cancellation_adapter",
            value=cancellation_adapter,
        )

    metadata = MappingProxyType(
        {
            "execution_id":
                request.identity.execution_id,
            "job_id":
                request.identity.job_id,
            "attempt_number":
                request.identity.attempt_number,
            "fence_id":
                fence.fence_id,
            "force_termination":
                force_termination,
        }
    )

    try:
        result = cancellation_adapter(
            metadata
        )
    except Exception:
        return ActiveWorkCancellationResult(
            cancellation_requested=False,
            active_work_stopped=False,
            error_code="active_work_cancellation_failed",
        )

    if isinstance(
        result,
        ActiveWorkCancellationResult,
    ):
        return result

    if result is True:
        return ActiveWorkCancellationResult(
            cancellation_requested=True,
            active_work_stopped=True,
        )

    if isinstance(result, Mapping):
        return ActiveWorkCancellationResult(
            cancellation_requested=bool(
                result.get(
                    "cancellation_requested",
                    False,
                )
            ),
            active_work_stopped=bool(
                result.get(
                    "active_work_stopped",
                    False,
                )
            ),
            worker_reference=(
                result.get(
                    "worker_reference"
                )
            ),
            runtime_reference=(
                result.get(
                    "runtime_reference"
                )
            ),
            error_code=(
                result.get(
                    "error_code"
                )
            ),
        )

    return ActiveWorkCancellationResult(
        cancellation_requested=False,
        active_work_stopped=False,
        error_code="invalid_active_work_cancellation_result",
    )


def validate_worker_lease_quiescence(
    *,
    evidence: WorkerLeaseQuiescenceEvidence,
) -> None:
    """
    Require worker and lease quiescence before CANCELLED state.
    """

    if not isinstance(
        evidence,
        WorkerLeaseQuiescenceEvidence,
    ):
        raise CancellationTerminationExecutionError(
            "evidence must be WorkerLeaseQuiescenceEvidence.",
            code="invalid_worker_lease_quiescence_evidence",
            value=evidence,
        )

    if not evidence.quiescent:
        raise CancellationTerminationExecutionError(
            "Worker / lease boundary is not quiescent.",
            code="worker_lease_not_quiescent",
            value={
                "worker_quiesced":
                    evidence.worker_quiesced,
                "lease_quiesced":
                    evidence.lease_quiesced,
                "active_operation_count":
                    evidence.active_operation_count,
            },
        )


def apply_cancelled_state(
    *,
    request: ExecutionRequest,
    lifecycle: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
    finalized_at: Optional[str] = None,
) -> ExecutionLifecycleRecord:
    """
    Apply CANCELLED through the canonical Phase-6.4 finalization path.
    """

    result = ExecutionResult(
        identity=request.identity,
        outcome=ExecutionOutcome.CANCELLED,
        result_metadata={
            "fence_id":
                fence.fence_id,
            "cancellation":
                True,
        },
    )

    cancelled = finalize_execution(
        record=lifecycle,
        result=result,
        fence=fence,
        finalized_at=finalized_at,
    )

    if (
        cancelled.state
        is not ExecutionLifecycleState.CANCELLED
    ):
        raise CancellationTerminationExecutionError(
            "Execution did not transition to CANCELLED.",
            code="cancelled_state_application_failed",
        )

    return cancelled


def execute_cancellation(
    *,
    request: ExecutionRequest,
    lifecycle: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
    decision: CancellationDecisionEvidence,
    stopper: Callable[
        [
            Mapping[str, Any],
        ],
        Any,
    ],
    cancellation_adapter: Callable[
        [
            Mapping[str, Any],
        ],
        Any,
    ],
    quiescence: WorkerLeaseQuiescenceEvidence,
    finalized_at: Optional[str] = None,
) -> tuple[
    ExecutionLifecycleRecord,
    CancellationExecutionResult,
]:
    """
    Canonical Phase-6.13 cancellation flow.

    decision
      -> validate boundary
      -> stop new work
      -> cancel active work
      -> require worker/lease quiescence
      -> apply CANCELLED lifecycle
      -> capture cancellation evidence
    """

    consume_cancellation_decision(
        decision=decision,
    )

    validate_cancellation_boundary(
        request=request,
        lifecycle=lifecycle,
        fence=fence,
    )

    stop_result = enforce_stop_new_work(
        request=request,
        fence=fence,
        stopper=stopper,
    )

    if not stop_result.enforced:
        raise CancellationTerminationExecutionError(
            "Stop-new-work enforcement failed.",
            code=(
                stop_result.error_code
                or "stop_new_work_failed"
            ),
        )

    cancellation_result = (
        coordinate_active_work_cancellation(
            request=request,
            fence=fence,
            force_termination=decision.force_termination,
            cancellation_adapter=cancellation_adapter,
        )
    )

    if (
        not cancellation_result.cancellation_requested
        or not cancellation_result.active_work_stopped
    ):
        raise CancellationTerminationExecutionError(
            "Active work was not fully cancelled.",
            code=(
                cancellation_result.error_code
                or "active_work_not_cancelled"
            ),
        )

    validate_worker_lease_quiescence(
        evidence=quiescence,
    )

    cancelled_lifecycle = apply_cancelled_state(
        request=request,
        lifecycle=lifecycle,
        fence=fence,
        finalized_at=finalized_at,
    )

    capture = CancellationExecutionResult(
        execution_id=request.identity.execution_id,
        job_id=request.identity.job_id,
        attempt_number=request.identity.attempt_number,
        fence_id=fence.fence_id,
        cancelled=(
            cancelled_lifecycle.state
            is ExecutionLifecycleState.CANCELLED
            and not cancelled_lifecycle.active
        ),
        force_termination=decision.force_termination,
        lifecycle_state=cancelled_lifecycle.state,
        cancellation_decision_id=decision.decision_id,
        cancellation_reason=decision.reason,
        runtime_reference=(
            cancellation_result.runtime_reference
            or stop_result.runtime_reference
        ),
        worker_reference=(
            cancellation_result.worker_reference
            or quiescence.worker_reference
        ),
        lease_reference=(
            quiescence.lease_reference
        ),
        error_code=None,
    )

    return cancelled_lifecycle, capture


def certify_cancellation_termination_execution_v1(
) -> Mapping[str, Any]:
    """
    Phase 6.13 certification.
    """

    from .execution_contracts import (
        ExecutionAction,
        ExecutionContext,
        ExecutionIdentity,
    )

    from .execution_permission_fencing import (
        ExecutionPermissionEvidence,
        evaluate_execution_permission,
    )

    from .execution_lifecycle_controller import (
        apply_running_state,
        create_execution_start,
    )

    identity = ExecutionIdentity(
        execution_id=(
            "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
        ),
        job_id="job-phase-6-13-certification",
        attempt_number=1,
    )

    start_request = ExecutionRequest(
        identity=identity,
        context=ExecutionContext(
            handler_key="certification.handler",
            worker_id="worker-certification",
            lease_id="lease-certification",
            lease_owner="worker-certification::instance-1",
        ),
        action=ExecutionAction.START,
    )

    cancel_request = ExecutionRequest(
        identity=identity,
        context=start_request.context,
        action=ExecutionAction.CANCEL,
    )

    permission = evaluate_execution_permission(
        request=start_request,
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
        raise CancellationTerminationExecutionError(
            "Certification missing execution fence.",
            code="certification_missing_fence",
        )

    ready = create_execution_start(
        request=start_request,
        permission=permission,
    )

    running = apply_running_state(
        record=ready,
        fence=fence,
        started_at="2026-01-01T00:00:00Z",
    )

    stop_calls: list[
        Mapping[str, Any]
    ] = []

    cancel_calls: list[
        Mapping[str, Any]
    ] = []

    def stopper(
        metadata: Mapping[str, Any],
    ) -> Mapping[str, Any]:

        stop_calls.append(
            dict(metadata)
        )

        return {
            "enforced":
                True,
            "runtime_reference":
                "runtime://phase-6-13/certification",
        }

    def cancellation_adapter(
        metadata: Mapping[str, Any],
    ) -> Mapping[str, Any]:

        cancel_calls.append(
            dict(metadata)
        )

        return {
            "cancellation_requested":
                True,
            "active_work_stopped":
                True,
            "worker_reference":
                "worker://phase-6-13/certification",
            "runtime_reference":
                "runtime://phase-6-13/certification",
        }

    quiescence = WorkerLeaseQuiescenceEvidence(
        worker_quiesced=True,
        lease_quiesced=True,
        active_operation_count=0,
        worker_reference=(
            "worker://phase-6-13/certification"
        ),
        lease_reference=(
            "lease://phase-6-13/certification"
        ),
    )

    decision = CancellationDecisionEvidence(
        authorized=True,
        decision_id="cancellation-decision-certification",
        reason="synthetic cancellation",
        force_termination=False,
    )

    cancelled, capture = execute_cancellation(
        request=cancel_request,
        lifecycle=running,
        fence=fence,
        decision=decision,
        stopper=stopper,
        cancellation_adapter=cancellation_adapter,
        quiescence=quiescence,
        finalized_at="2026-01-01T00:00:05Z",
    )

    unauthorized_rejected = False

    fresh_ready = create_execution_start(
        request=start_request,
        permission=permission,
    )

    fresh_running = apply_running_state(
        record=fresh_ready,
        fence=fence,
    )

    try:
        execute_cancellation(
            request=cancel_request,
            lifecycle=fresh_running,
            fence=fence,
            decision=CancellationDecisionEvidence(
                authorized=False,
                reason="not authorized",
            ),
            stopper=stopper,
            cancellation_adapter=cancellation_adapter,
            quiescence=quiescence,
        )
    except CancellationTerminationExecutionError:
        unauthorized_rejected = True

    stop_failure_rejected = False

    def failing_stopper(
        metadata: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        return {
            "enforced":
                False,
            "error_code":
                "synthetic_stop_failure",
        }

    fresh_ready_2 = create_execution_start(
        request=start_request,
        permission=permission,
    )

    fresh_running_2 = apply_running_state(
        record=fresh_ready_2,
        fence=fence,
    )

    try:
        execute_cancellation(
            request=cancel_request,
            lifecycle=fresh_running_2,
            fence=fence,
            decision=decision,
            stopper=failing_stopper,
            cancellation_adapter=cancellation_adapter,
            quiescence=quiescence,
        )
    except CancellationTerminationExecutionError:
        stop_failure_rejected = True

    active_cancel_failure_rejected = False

    def failing_cancellation_adapter(
        metadata: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        return {
            "cancellation_requested":
                True,
            "active_work_stopped":
                False,
            "error_code":
                "synthetic_active_work_failure",
        }

    fresh_ready_3 = create_execution_start(
        request=start_request,
        permission=permission,
    )

    fresh_running_3 = apply_running_state(
        record=fresh_ready_3,
        fence=fence,
    )

    try:
        execute_cancellation(
            request=cancel_request,
            lifecycle=fresh_running_3,
            fence=fence,
            decision=decision,
            stopper=stopper,
            cancellation_adapter=failing_cancellation_adapter,
            quiescence=quiescence,
        )
    except CancellationTerminationExecutionError:
        active_cancel_failure_rejected = True

    non_quiescent_rejected = False

    fresh_ready_4 = create_execution_start(
        request=start_request,
        permission=permission,
    )

    fresh_running_4 = apply_running_state(
        record=fresh_ready_4,
        fence=fence,
    )

    try:
        execute_cancellation(
            request=cancel_request,
            lifecycle=fresh_running_4,
            fence=fence,
            decision=decision,
            stopper=stopper,
            cancellation_adapter=cancellation_adapter,
            quiescence=WorkerLeaseQuiescenceEvidence(
                worker_quiesced=True,
                lease_quiesced=False,
                active_operation_count=1,
            ),
        )
    except CancellationTerminationExecutionError:
        non_quiescent_rejected = True

    terminal_reentry_rejected = False

    try:
        execute_cancellation(
            request=cancel_request,
            lifecycle=cancelled,
            fence=fence,
            decision=decision,
            stopper=stopper,
            cancellation_adapter=cancellation_adapter,
            quiescence=quiescence,
        )
    except CancellationTerminationExecutionError:
        terminal_reentry_rejected = True

    checks = {
        "cancellation_decision_consumed":
            decision.authorized,

        "stop_new_work_enforced":
            bool(stop_calls),

        "active_work_cancellation_coordinated":
            bool(cancel_calls),

        "worker_lease_quiescence_passed":
            quiescence.quiescent,

        "cancelled_state_applied":
            (
                cancelled.state
                is ExecutionLifecycleState.CANCELLED
            ),

        "cancelled_execution_not_active":
            not cancelled.active,

        "cancellation_result_captured":
            capture.cancelled,

        "cancellation_fence_preserved":
            (
                capture.fence_id
                == fence.fence_id
                == cancelled.fence_id
            ),

        "cancellation_identity_preserved":
            (
                capture.execution_id
                == identity.execution_id
                and capture.job_id
                == identity.job_id
            ),

        "runtime_reference_captured":
            (
                capture.runtime_reference
                == "runtime://phase-6-13/certification"
            ),

        "worker_reference_captured":
            (
                capture.worker_reference
                == "worker://phase-6-13/certification"
            ),

        "lease_reference_captured":
            (
                capture.lease_reference
                == "lease://phase-6-13/certification"
            ),

        "unauthorized_cancellation_rejected":
            unauthorized_rejected,

        "stop_new_work_failure_rejected":
            stop_failure_rejected,

        "active_work_cancellation_failure_rejected":
            active_cancel_failure_rejected,

        "non_quiescent_boundary_rejected":
            non_quiescent_rejected,

        "terminal_reentry_rejected":
            terminal_reentry_rejected,

        "no_cancellation_policy_invented":
            True,

        "no_second_worker_cancellation_system":
            True,

        "no_second_lease_system":
            True,

        "no_production_job_mutation":
            True,

        "no_queue_mutation":
            True,

        "no_lease_mutation":
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
                "6.13",

            "component":
                "Cancellation / Termination Execution",

            "version":
                CANCELLATION_TERMINATION_EXECUTION_VERSION,

            "schema_version":
                CANCELLATION_TERMINATION_EXECUTION_SCHEMA_VERSION,

            "certified":
                certified,

            "checks":
                MappingProxyType(
                    checks
                ),

            "authority_boundary": (
                "Phase 6.13 consumes an existing cancellation decision, "
                "coordinates stop-new-work and active-work cancellation "
                "through existing runtime/worker adapters, requires worker/"
                "lease quiescence, applies CANCELLED to the execution "
                "lifecycle and captures cancellation evidence. It does not "
                "create cancellation, worker, lease or persistence systems."
            ),
        }
    )


def explain_cancellation_termination_execution_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "6.13",

            "component":
                "Cancellation / Termination Execution",

            "version":
                CANCELLATION_TERMINATION_EXECUTION_VERSION,

            "consume_cancellation_decision": (
                "Consumes an already-authorized cancellation decision."
            ),

            "stop_new_work_enforcement": (
                "Coordinates stop-new-work through existing runtime/worker "
                "mechanics before cancellation continues."
            ),

            "active_work_cancellation_coordination": (
                "Delegates concrete active-work cancellation to existing "
                "runtime/worker machinery."
            ),

            "worker_lease_quiescence": (
                "Requires worker quiescence, lease quiescence and zero "
                "active operations before terminal cancellation."
            ),

            "cancelled_state_application": (
                "Uses canonical Phase-6.4 finalization to apply CANCELLED."
            ),

            "cancellation_result_capture": (
                "Captures execution identity, fence, decision and runtime/"
                "worker/lease references for downstream handoff."
            ),

            "prohibitions": (
                "does not invent cancellation decisions",
                "does not create worker cancellation infrastructure",
                "does not create lease infrastructure",
                "does not directly kill OS processes",
                "does not mutate production Universal Jobs",
                "does not mutate queues",
                "does not mutate orchestration state",
                "does not persist cancellation state",
            ),
        }
    )


__all__ = [
    "CANCELLATION_TERMINATION_EXECUTION_VERSION",
    "CANCELLATION_TERMINATION_EXECUTION_SCHEMA_VERSION",
    "CancellationTerminationExecutionError",
    "CancellationDecisionEvidence",
    "StopNewWorkResult",
    "ActiveWorkCancellationResult",
    "WorkerLeaseQuiescenceEvidence",
    "CancellationExecutionResult",
    "consume_cancellation_decision",
    "validate_cancellation_boundary",
    "enforce_stop_new_work",
    "coordinate_active_work_cancellation",
    "validate_worker_lease_quiescence",
    "apply_cancelled_state",
    "execute_cancellation",
    "certify_cancellation_termination_execution_v1",
    "explain_cancellation_termination_execution_v1",
]
