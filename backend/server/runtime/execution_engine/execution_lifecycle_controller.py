"""
LinkCraftor Universal Runtime
Phase 6.4 — Execution Lifecycle Controller

Canonical execution lifecycle control.

This component consumes:
- Phase 6.2 ExecutionRequest / ExecutionResult
- Phase 6.3 ExecutionPermissionDecision / ExecutionFenceIdentity

It owns the Phase-6 execution lifecycle state machine.

It intentionally does NOT:
- mutate the production Universal Job store
- enqueue or dequeue jobs
- acquire or release worker leases
- invoke runtime handlers
- persist lifecycle state
- mutate Phase-5 orchestration state
- decide retries
- perform checkpoint I/O

Production job / queue / worker wiring is deferred to Phase 6.15.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .execution_contracts import (
    ExecutionOutcome,
    ExecutionRequest,
    ExecutionResult,
)

from .execution_permission_fencing import (
    ExecutionFenceIdentity,
    ExecutionPermissionDecision,
)


EXECUTION_LIFECYCLE_VERSION = (
    "execution_lifecycle_controller_v6.4.1"
)

EXECUTION_LIFECYCLE_SCHEMA_VERSION = (
    "execution_lifecycle_controller_schema_v1"
)


class ExecutionLifecycleError(ValueError):
    """Raised when an execution lifecycle operation is invalid."""

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


def _optional_text(
    value: Any,
    *,
    field_name: str,
) -> Optional[str]:
    if value is None:
        return None

    if not isinstance(value, str):
        raise ExecutionLifecycleError(
            f"{field_name} must be a string or None.",
            code=f"invalid_{field_name}_type",
            value=value,
        )

    normalized = value.strip()

    return normalized or None


class ExecutionLifecycleState(str, Enum):
    """
    Canonical Phase-6 execution lifecycle states.

    These are execution-engine lifecycle states, not direct persistence
    mutations of UniversalJob.
    """

    READY = "READY"
    RUNNING = "RUNNING"
    FINALIZING = "FINALIZING"

    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    SUSPENDED = "SUSPENDED"


_TERMINAL_EXECUTION_STATES = frozenset(
    {
        ExecutionLifecycleState.SUCCEEDED,
        ExecutionLifecycleState.FAILED,
        ExecutionLifecycleState.CANCELLED,
        ExecutionLifecycleState.SUSPENDED,
    }
)


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionLifecycleRecord:
    """
    Immutable lifecycle representation for one execution attempt.

    Each transition creates a new record rather than mutating the previous
    record in place.
    """

    execution_id: str
    job_id: str
    attempt_number: int

    fence_id: str
    state: ExecutionLifecycleState

    active: bool

    started_at: Optional[str] = None
    finalized_at: Optional[str] = None

    result_outcome: Optional[ExecutionOutcome] = None

    schema_version: str = field(
        default=EXECUTION_LIFECYCLE_SCHEMA_VERSION,
        init=False,
    )

    @property
    def terminal(self) -> bool:
        return self.state in _TERMINAL_EXECUTION_STATES

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
            "state":
                self.state.value,
            "active":
                self.active,
            "started_at":
                self.started_at,
            "finalized_at":
                self.finalized_at,
            "result_outcome":
                (
                    self.result_outcome.value
                    if self.result_outcome is not None
                    else None
                ),
            "terminal":
                self.terminal,
        }


def validate_pre_execution(
    *,
    request: ExecutionRequest,
    permission: ExecutionPermissionDecision,
) -> ExecutionFenceIdentity:
    """
    Pre-execution validation.

    Requires:
    - valid ExecutionRequest
    - ALLOW permission decision
    - canonical fence
    - request/fence identity agreement
    """

    if not isinstance(
        request,
        ExecutionRequest,
    ):
        raise ExecutionLifecycleError(
            "request must be ExecutionRequest.",
            code="invalid_execution_request",
            value=request,
        )

    if not isinstance(
        permission,
        ExecutionPermissionDecision,
    ):
        raise ExecutionLifecycleError(
            "permission must be ExecutionPermissionDecision.",
            code="invalid_execution_permission",
            value=permission,
        )

    if not permission.allowed:
        raise ExecutionLifecycleError(
            "Execution permission was denied.",
            code="execution_permission_denied",
            value=permission.reason.value,
        )

    fence = permission.fence

    if fence is None:
        raise ExecutionLifecycleError(
            "Allowed execution requires an execution fence.",
            code="allowed_execution_missing_fence",
        )

    if (
        fence.execution_id
        != request.identity.execution_id
    ):
        raise ExecutionLifecycleError(
            "Execution fence execution_id does not match request.",
            code="execution_fence_execution_mismatch",
            value=fence.execution_id,
        )

    if fence.job_id != request.identity.job_id:
        raise ExecutionLifecycleError(
            "Execution fence job_id does not match request.",
            code="execution_fence_job_mismatch",
            value=fence.job_id,
        )

    if (
        fence.attempt_number
        != request.identity.attempt_number
    ):
        raise ExecutionLifecycleError(
            "Execution fence attempt_number does not match request.",
            code="execution_fence_attempt_mismatch",
            value=fence.attempt_number,
        )

    return fence


def create_execution_start(
    *,
    request: ExecutionRequest,
    permission: ExecutionPermissionDecision,
) -> ExecutionLifecycleRecord:
    """
    Create the READY lifecycle record after successful pre-execution
    validation.

    This does not invoke the runtime handler.
    """

    fence = validate_pre_execution(
        request=request,
        permission=permission,
    )

    return ExecutionLifecycleRecord(
        execution_id=request.identity.execution_id,
        job_id=request.identity.job_id,
        attempt_number=request.identity.attempt_number,
        fence_id=fence.fence_id,
        state=ExecutionLifecycleState.READY,
        active=False,
    )


def apply_running_state(
    *,
    record: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
    started_at: Optional[str] = None,
) -> ExecutionLifecycleRecord:
    """
    Apply the Phase-6 RUNNING lifecycle state.

    This is an execution-engine lifecycle transition only.
    Production UniversalJob status mutation is deferred to integration.
    """

    if not isinstance(
        record,
        ExecutionLifecycleRecord,
    ):
        raise ExecutionLifecycleError(
            "record must be ExecutionLifecycleRecord.",
            code="invalid_execution_lifecycle_record",
            value=record,
        )

    if not isinstance(
        fence,
        ExecutionFenceIdentity,
    ):
        raise ExecutionLifecycleError(
            "fence must be ExecutionFenceIdentity.",
            code="invalid_execution_fence",
            value=fence,
        )

    if record.state is not ExecutionLifecycleState.READY:
        raise ExecutionLifecycleError(
            "Only READY execution may enter RUNNING.",
            code="invalid_execution_start_state",
            value=record.state.value,
        )

    if record.fence_id != fence.fence_id:
        raise ExecutionLifecycleError(
            "Execution fence changed before RUNNING transition.",
            code="execution_fence_changed",
            value=fence.fence_id,
        )

    canonical_started_at = _optional_text(
        started_at,
        field_name="started_at",
    )

    return ExecutionLifecycleRecord(
        execution_id=record.execution_id,
        job_id=record.job_id,
        attempt_number=record.attempt_number,
        fence_id=record.fence_id,
        state=ExecutionLifecycleState.RUNNING,
        active=True,
        started_at=canonical_started_at,
    )


def is_execution_active(
    record: ExecutionLifecycleRecord,
) -> bool:
    """
    Canonical active-execution query.
    """

    if not isinstance(
        record,
        ExecutionLifecycleRecord,
    ):
        raise ExecutionLifecycleError(
            "record must be ExecutionLifecycleRecord.",
            code="invalid_execution_lifecycle_record",
            value=record,
        )

    return (
        record.active
        and record.state
        is ExecutionLifecycleState.RUNNING
    )


def begin_execution_finalization(
    *,
    record: ExecutionLifecycleRecord,
    result: ExecutionResult,
    fence: ExecutionFenceIdentity,
) -> ExecutionLifecycleRecord:
    """
    Enter FINALIZING after handler/result production.

    Result acceptance remains fence-bound.
    """

    if not isinstance(
        record,
        ExecutionLifecycleRecord,
    ):
        raise ExecutionLifecycleError(
            "record must be ExecutionLifecycleRecord.",
            code="invalid_execution_lifecycle_record",
            value=record,
        )

    if record.state is not ExecutionLifecycleState.RUNNING:
        raise ExecutionLifecycleError(
            "Only RUNNING execution may begin finalization.",
            code="invalid_finalization_source_state",
            value=record.state.value,
        )

    if not isinstance(
        result,
        ExecutionResult,
    ):
        raise ExecutionLifecycleError(
            "result must be ExecutionResult.",
            code="invalid_execution_result",
            value=result,
        )

    if not isinstance(
        fence,
        ExecutionFenceIdentity,
    ):
        raise ExecutionLifecycleError(
            "fence must be ExecutionFenceIdentity.",
            code="invalid_execution_fence",
            value=fence,
        )

    if record.fence_id != fence.fence_id:
        raise ExecutionLifecycleError(
            "Execution fence changed before finalization.",
            code="execution_finalization_fence_mismatch",
            value=fence.fence_id,
        )

    if (
        result.identity.execution_id
        != record.execution_id
    ):
        raise ExecutionLifecycleError(
            "Result execution_id does not match active execution.",
            code="execution_result_identity_mismatch",
            value=result.identity.execution_id,
        )

    if result.identity.job_id != record.job_id:
        raise ExecutionLifecycleError(
            "Result job_id does not match active execution.",
            code="execution_result_job_mismatch",
            value=result.identity.job_id,
        )

    if (
        result.identity.attempt_number
        != record.attempt_number
    ):
        raise ExecutionLifecycleError(
            "Result attempt_number does not match active execution.",
            code="execution_result_attempt_mismatch",
            value=result.identity.attempt_number,
        )

    return ExecutionLifecycleRecord(
        execution_id=record.execution_id,
        job_id=record.job_id,
        attempt_number=record.attempt_number,
        fence_id=record.fence_id,
        state=ExecutionLifecycleState.FINALIZING,
        active=False,
        started_at=record.started_at,
        result_outcome=result.outcome,
    )


def _terminal_state_for_outcome(
    outcome: ExecutionOutcome,
) -> ExecutionLifecycleState:

    if outcome is ExecutionOutcome.SUCCEEDED:
        return ExecutionLifecycleState.SUCCEEDED

    if outcome is ExecutionOutcome.FAILED:
        return ExecutionLifecycleState.FAILED

    if outcome is ExecutionOutcome.CANCELLED:
        return ExecutionLifecycleState.CANCELLED

    if outcome is ExecutionOutcome.SUSPENDED:
        return ExecutionLifecycleState.SUSPENDED

    raise ExecutionLifecycleError(
        "Unsupported execution outcome.",
        code="unsupported_execution_outcome",
        value=outcome,
    )


def apply_terminal_state(
    *,
    record: ExecutionLifecycleRecord,
    finalized_at: Optional[str] = None,
) -> ExecutionLifecycleRecord:
    """
    Apply the canonical terminal lifecycle state.

    Does not persist or mutate UniversalJob.
    """

    if not isinstance(
        record,
        ExecutionLifecycleRecord,
    ):
        raise ExecutionLifecycleError(
            "record must be ExecutionLifecycleRecord.",
            code="invalid_execution_lifecycle_record",
            value=record,
        )

    if record.state is not ExecutionLifecycleState.FINALIZING:
        raise ExecutionLifecycleError(
            "Only FINALIZING execution may enter terminal state.",
            code="invalid_terminal_transition_source",
            value=record.state.value,
        )

    if record.result_outcome is None:
        raise ExecutionLifecycleError(
            "FINALIZING execution requires result_outcome.",
            code="missing_finalization_outcome",
        )

    terminal_state = _terminal_state_for_outcome(
        record.result_outcome,
    )

    canonical_finalized_at = _optional_text(
        finalized_at,
        field_name="finalized_at",
    )

    return ExecutionLifecycleRecord(
        execution_id=record.execution_id,
        job_id=record.job_id,
        attempt_number=record.attempt_number,
        fence_id=record.fence_id,
        state=terminal_state,
        active=False,
        started_at=record.started_at,
        finalized_at=canonical_finalized_at,
        result_outcome=record.result_outcome,
    )


def finalize_execution(
    *,
    record: ExecutionLifecycleRecord,
    result: ExecutionResult,
    fence: ExecutionFenceIdentity,
    finalized_at: Optional[str] = None,
) -> ExecutionLifecycleRecord:
    """
    Canonical convenience operation:

    RUNNING
      -> FINALIZING
      -> terminal execution state
    """

    finalizing = begin_execution_finalization(
        record=record,
        result=result,
        fence=fence,
    )

    return apply_terminal_state(
        record=finalizing,
        finalized_at=finalized_at,
    )


def certify_execution_lifecycle_controller_v1(
) -> Mapping[str, Any]:
    """
    Phase 6.4 certification.

    Synthetic in-memory contracts only.
    No production runtime state is modified.
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

    identity = ExecutionIdentity(
        execution_id=(
            "33333333-3333-4333-8333-333333333333"
        ),
        job_id="job-phase-6-4-certification",
        attempt_number=1,
    )

    context = ExecutionContext(
        handler_key="certification.handler",
        worker_id="worker-certification",
        lease_id="lease-certification",
        lease_owner="worker-certification::instance-1",
    )

    request = ExecutionRequest(
        identity=identity,
        context=context,
        action=ExecutionAction.START,
    )

    evidence = ExecutionPermissionEvidence(
        job_status="RUNNING",
        current_worker_id="worker-certification",
        current_lease_id="lease-certification",
        current_lease_owner=(
            "worker-certification::instance-1"
        ),
        lease_state="ACTIVE",
    )

    permission = evaluate_execution_permission(
        request=request,
        evidence=evidence,
    )

    ready = create_execution_start(
        request=request,
        permission=permission,
    )

    fence = permission.fence

    if fence is None:
        raise ExecutionLifecycleError(
            "Certification permission did not produce fence.",
            code="certification_missing_fence",
        )

    running = apply_running_state(
        record=ready,
        fence=fence,
        started_at="2026-01-01T00:00:00Z",
    )

    success_result = ExecutionResult(
        identity=identity,
        outcome=ExecutionOutcome.SUCCEEDED,
        result_reference="result://phase-6-4/certification",
    )

    finalizing = begin_execution_finalization(
        record=running,
        result=success_result,
        fence=fence,
    )

    terminal = apply_terminal_state(
        record=finalizing,
        finalized_at="2026-01-01T00:00:01Z",
    )

    convenience_terminal = finalize_execution(
        record=running,
        result=success_result,
        fence=fence,
        finalized_at="2026-01-01T00:00:01Z",
    )

    denied_validation_passed = False

    try:
        denied_permission = ExecutionPermissionDecision(
            disposition=permission.disposition.DENY,
            reason=permission.reason,
            fence=None,
            job_state_eligible=False,
            lease_valid=False,
            worker_valid=False,
            duplicate_safe=False,
        )

        create_execution_start(
            request=request,
            permission=denied_permission,
        )

    except ExecutionLifecycleError:
        denied_validation_passed = True

    checks = {
        "pre_execution_validation_passed":
            permission.allowed,

        "execution_start_created_ready":
            (
                ready.state
                is ExecutionLifecycleState.READY
            ),

        "running_state_applied":
            (
                running.state
                is ExecutionLifecycleState.RUNNING
            ),

        "active_execution_tracking_passed":
            is_execution_active(running),

        "running_execution_marked_active":
            running.active,

        "finalization_started":
            (
                finalizing.state
                is ExecutionLifecycleState.FINALIZING
            ),

        "finalizing_execution_not_active":
            not finalizing.active,

        "terminal_state_applied":
            (
                terminal.state
                is ExecutionLifecycleState.SUCCEEDED
            ),

        "terminal_execution_not_active":
            not terminal.active,

        "terminal_property_true":
            terminal.terminal,

        "finalize_execution_matches":
            (
                convenience_terminal.state
                is terminal.state
            ),

        "fence_preserved_across_lifecycle":
            (
                ready.fence_id
                == running.fence_id
                == finalizing.fence_id
                == terminal.fence_id
            ),

        "denied_permission_rejected":
            denied_validation_passed,

        "no_production_job_mutation":
            True,

        "no_queue_mutation":
            True,

        "no_lease_mutation":
            True,

        "no_handler_execution":
            True,

        "no_orchestration_mutation":
            True,

        "no_persistence":
            True,
    }

    certified = all(checks.values())

    return MappingProxyType(
        {
            "phase": "6.4",
            "component":
                "Execution Lifecycle Controller",
            "version":
                EXECUTION_LIFECYCLE_VERSION,
            "schema_version":
                EXECUTION_LIFECYCLE_SCHEMA_VERSION,
            "certified":
                certified,
            "checks":
                MappingProxyType(checks),
            "authority_boundary": (
                "Phase 6.4 owns the canonical in-engine execution "
                "lifecycle from permission validation through READY, "
                "RUNNING, FINALIZING and terminal execution states. "
                "It does not yet apply production UniversalJob, queue, "
                "lease or orchestration mutations."
            ),
        }
    )


def explain_execution_lifecycle_controller_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase": "6.4",
            "component":
                "Execution Lifecycle Controller",
            "version":
                EXECUTION_LIFECYCLE_VERSION,
            "schema_version":
                EXECUTION_LIFECYCLE_SCHEMA_VERSION,

            "pre_execution_validation": (
                "Requires an allowed Phase-6.3 permission decision "
                "and validates that the execution fence matches the "
                "request identity."
            ),

            "execution_start": (
                "Creates an immutable READY lifecycle record."
            ),

            "running_state_application": (
                "Transitions READY to the Phase-6 RUNNING lifecycle "
                "state while preserving the execution fence."
            ),

            "active_execution_tracking": (
                "RUNNING lifecycle records are canonically active; "
                "FINALIZING and terminal records are not active."
            ),

            "execution_finalization": (
                "Validates result identity and execution fence before "
                "entering FINALIZING."
            ),

            "terminal_state_application": (
                "Maps normalized execution outcome to SUCCEEDED, "
                "FAILED, CANCELLED or SUSPENDED lifecycle state."
            ),

            "prohibitions": (
                "does not mutate production Universal Jobs",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not acquire leases",
                "does not renew leases",
                "does not release leases",
                "does not invoke runtime handlers",
                "does not decide retries",
                "does not requeue jobs",
                "does not mutate orchestration state",
                "does not persist lifecycle state",
                "does not save or restore checkpoints",
            ),
        }
    )


__all__ = [
    "EXECUTION_LIFECYCLE_VERSION",
    "EXECUTION_LIFECYCLE_SCHEMA_VERSION",
    "ExecutionLifecycleError",
    "ExecutionLifecycleState",
    "ExecutionLifecycleRecord",
    "validate_pre_execution",
    "create_execution_start",
    "apply_running_state",
    "is_execution_active",
    "begin_execution_finalization",
    "apply_terminal_state",
    "finalize_execution",
    "certify_execution_lifecycle_controller_v1",
    "explain_execution_lifecycle_controller_v1",
]
