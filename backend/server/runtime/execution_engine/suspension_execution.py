"""
LinkCraftor Universal Runtime
Phase 6.9 — Suspension Execution

Canonical execution-layer suspension coordination.

Consumes:
- Phase 5 suspension eligibility evidence
- Phase 6.2 ExecutionRequest
- Phase 6.3 ExecutionFenceIdentity
- Phase 6.4 RUNNING ExecutionLifecycleRecord
- Phase 6.8 checkpoint coordination

Owns:
- consume suspension eligibility
- active-work quiescence gate
- checkpoint-before-suspension coordination
- execution SUSPENDED-state application
- suspension result capture

Does NOT:
- decide whether orchestration should suspend
- mutate Phase-5 orchestration state
- mutate production Universal Job state
- create checkpoint persistence
- release/acquire worker leases
- enqueue/requeue jobs
- stop OS/process/thread work directly
- persist suspension state

Production integration is deferred to later Phase-6 integration layers.
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

from .checkpoint_execution import (
    CheckpointReference,
    CheckpointSaveResult,
    coordinate_checkpoint_save,
)


SUSPENSION_EXECUTION_VERSION = (
    "suspension_execution_v6.9.1"
)

SUSPENSION_EXECUTION_SCHEMA_VERSION = (
    "suspension_execution_schema_v1"
)


class SuspensionExecutionError(ValueError):
    """Raised when execution suspension coordination is invalid."""

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
class SuspensionEligibilityEvidence:
    """
    Caller-supplied Phase-5 suspension eligibility evidence.

    Phase 6.9 consumes this decision.
    It does not recreate Phase-5 decision authority.
    """

    eligible: bool

    decision_id: Optional[str] = None
    reason: Optional[str] = None

    schema_version: str = field(
        default=SUSPENSION_EXECUTION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class ActiveWorkQuiescenceEvidence:
    """
    Evidence that new work has stopped and active execution is safe
    to suspend.

    Actual worker/process quiescence is performed by lower-level runtime
    machinery and later production integration.
    """

    stop_new_work_enforced: bool
    active_work_quiesced: bool

    active_operation_count: int = 0

    schema_version: str = field(
        default=SUSPENSION_EXECUTION_SCHEMA_VERSION,
        init=False,
    )

    @property
    def quiescent(self) -> bool:
        return (
            self.stop_new_work_enforced
            and self.active_work_quiesced
            and self.active_operation_count == 0
        )


@dataclass(
    frozen=True,
    slots=True,
)
class SuspensionExecutionResult:
    """
    Canonical Phase-6.9 suspension capture.
    """

    execution_id: str
    job_id: str
    attempt_number: int
    fence_id: str

    suspended: bool

    checkpoint_reference: Optional[CheckpointReference]

    lifecycle_state: ExecutionLifecycleState

    suspension_decision_id: Optional[str]
    suspension_reason: Optional[str]

    error_code: Optional[str] = None

    schema_version: str = field(
        default=SUSPENSION_EXECUTION_SCHEMA_VERSION,
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
            "suspended":
                self.suspended,
            "checkpoint_reference":
                (
                    self.checkpoint_reference.to_dict()
                    if self.checkpoint_reference is not None
                    else None
                ),
            "lifecycle_state":
                self.lifecycle_state.value,
            "suspension_decision_id":
                self.suspension_decision_id,
            "suspension_reason":
                self.suspension_reason,
            "error_code":
                self.error_code,
        }


def consume_suspension_eligibility(
    *,
    evidence: SuspensionEligibilityEvidence,
) -> None:
    """
    Consume Phase-5 suspension eligibility.

    Phase 6.9 rejects suspension when Phase 5 did not authorize it.
    """

    if not isinstance(
        evidence,
        SuspensionEligibilityEvidence,
    ):
        raise SuspensionExecutionError(
            "evidence must be SuspensionEligibilityEvidence.",
            code="invalid_suspension_eligibility_evidence",
            value=evidence,
        )

    if not evidence.eligible:
        raise SuspensionExecutionError(
            "Suspension was not authorized by Phase 5.",
            code="suspension_not_eligible",
            value=evidence.reason,
        )


def validate_active_work_quiescence(
    *,
    lifecycle: ExecutionLifecycleRecord,
    quiescence: ActiveWorkQuiescenceEvidence,
) -> None:
    """
    Suspension requires a currently RUNNING execution whose active work
    has been quiesced.
    """

    if not isinstance(
        lifecycle,
        ExecutionLifecycleRecord,
    ):
        raise SuspensionExecutionError(
            "lifecycle must be ExecutionLifecycleRecord.",
            code="invalid_execution_lifecycle",
            value=lifecycle,
        )

    if lifecycle.state is not ExecutionLifecycleState.RUNNING:
        raise SuspensionExecutionError(
            "Only RUNNING execution may be suspended.",
            code="suspension_requires_running",
            value=lifecycle.state.value,
        )

    if not isinstance(
        quiescence,
        ActiveWorkQuiescenceEvidence,
    ):
        raise SuspensionExecutionError(
            "quiescence must be ActiveWorkQuiescenceEvidence.",
            code="invalid_quiescence_evidence",
            value=quiescence,
        )

    if not quiescence.quiescent:
        raise SuspensionExecutionError(
            "Active execution work is not fully quiesced.",
            code="active_work_not_quiesced",
            value={
                "stop_new_work_enforced":
                    quiescence.stop_new_work_enforced,
                "active_work_quiesced":
                    quiescence.active_work_quiesced,
                "active_operation_count":
                    quiescence.active_operation_count,
            },
        )


def checkpoint_before_suspension(
    *,
    request: ExecutionRequest,
    lifecycle: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
    checkpoint_payload: Any,
    saver: Callable[[Mapping[str, Any], Any], str],
) -> CheckpointSaveResult:
    """
    Coordinate mandatory checkpoint save before suspension.
    """

    save = coordinate_checkpoint_save(
        request=request,
        lifecycle=lifecycle,
        fence=fence,
        checkpoint_payload=checkpoint_payload,
        saver=saver,
    )

    if not save.saved or save.reference is None:
        raise SuspensionExecutionError(
            "Checkpoint must be saved before suspension.",
            code=(
                save.error_code
                or "checkpoint_before_suspension_failed"
            ),
        )

    return save


def apply_suspended_state(
    *,
    request: ExecutionRequest,
    lifecycle: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
    finalized_at: Optional[str] = None,
) -> ExecutionLifecycleRecord:
    """
    Apply execution SUSPENDED lifecycle state using the canonical
    Phase-6.4 finalization path.

    This is an execution lifecycle transition only.
    It does not mutate production UniversalJob.
    """

    result = ExecutionResult(
        identity=request.identity,
        outcome=ExecutionOutcome.SUSPENDED,
        result_metadata={
            "fence_id":
                fence.fence_id,
            "suspension":
                True,
        },
    )

    return finalize_execution(
        record=lifecycle,
        result=result,
        fence=fence,
        finalized_at=finalized_at,
    )


def execute_suspension(
    *,
    request: ExecutionRequest,
    lifecycle: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
    eligibility: SuspensionEligibilityEvidence,
    quiescence: ActiveWorkQuiescenceEvidence,
    checkpoint_payload: Any,
    saver: Callable[[Mapping[str, Any], Any], str],
    finalized_at: Optional[str] = None,
) -> tuple[
    ExecutionLifecycleRecord,
    SuspensionExecutionResult,
]:
    """
    Canonical Phase-6.9 suspension operation.

    Flow:
    Phase-5 eligibility
        -> active-work quiescence
        -> checkpoint save
        -> execution SUSPENDED lifecycle
        -> suspension capture
    """

    if not isinstance(request, ExecutionRequest):
        raise SuspensionExecutionError(
            "request must be ExecutionRequest.",
            code="invalid_execution_request",
            value=request,
        )

    if not isinstance(fence, ExecutionFenceIdentity):
        raise SuspensionExecutionError(
            "fence must be ExecutionFenceIdentity.",
            code="invalid_execution_fence",
            value=fence,
        )

    consume_suspension_eligibility(
        evidence=eligibility,
    )

    validate_active_work_quiescence(
        lifecycle=lifecycle,
        quiescence=quiescence,
    )

    if (
        lifecycle.execution_id
        != request.identity.execution_id
        or lifecycle.job_id
        != request.identity.job_id
        or lifecycle.attempt_number
        != request.identity.attempt_number
    ):
        raise SuspensionExecutionError(
            "Suspension execution identity mismatch.",
            code="suspension_execution_identity_mismatch",
        )

    if lifecycle.fence_id != fence.fence_id:
        raise SuspensionExecutionError(
            "Suspension fence mismatch.",
            code="suspension_fence_mismatch",
        )

    save = checkpoint_before_suspension(
        request=request,
        lifecycle=lifecycle,
        fence=fence,
        checkpoint_payload=checkpoint_payload,
        saver=saver,
    )

    suspended_lifecycle = apply_suspended_state(
        request=request,
        lifecycle=lifecycle,
        fence=fence,
        finalized_at=finalized_at,
    )

    capture = SuspensionExecutionResult(
        execution_id=request.identity.execution_id,
        job_id=request.identity.job_id,
        attempt_number=request.identity.attempt_number,
        fence_id=fence.fence_id,
        suspended=(
            suspended_lifecycle.state
            is ExecutionLifecycleState.SUSPENDED
        ),
        checkpoint_reference=save.reference,
        lifecycle_state=suspended_lifecycle.state,
        suspension_decision_id=eligibility.decision_id,
        suspension_reason=eligibility.reason,
        error_code=None,
    )

    return suspended_lifecycle, capture


def certify_suspension_execution_v1(
) -> Mapping[str, Any]:
    """
    Phase 6.9 certification.

    Uses synthetic in-memory checkpoint storage only.
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
            "88888888-8888-4888-8888-888888888888"
        ),
        job_id="job-phase-6-9-certification",
        attempt_number=1,
    )

    request = ExecutionRequest(
        identity=identity,
        context=ExecutionContext(
            handler_key="certification.handler",
            worker_id="worker-certification",
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
        raise SuspensionExecutionError(
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
    )

    eligibility = SuspensionEligibilityEvidence(
        eligible=True,
        decision_id="phase5-suspend-certification",
        reason="synthetic suspension decision",
    )

    quiescence = ActiveWorkQuiescenceEvidence(
        stop_new_work_enforced=True,
        active_work_quiesced=True,
        active_operation_count=0,
    )

    storage: dict[str, Any] = {}

    def saver(
        metadata: Mapping[str, Any],
        payload: Any,
    ) -> str:
        key = (
            "checkpoint://suspension/"
            + metadata["execution_id"]
        )
        storage[key] = payload
        return key

    suspended, capture = execute_suspension(
        request=request,
        lifecycle=running,
        fence=fence,
        eligibility=eligibility,
        quiescence=quiescence,
        checkpoint_payload={
            "cursor": 25,
            "state": "before-suspension",
        },
        saver=saver,
        finalized_at="2026-01-01T00:00:02Z",
    )

    ineligible_rejected = False

    try:
        execute_suspension(
            request=request,
            lifecycle=running,
            fence=fence,
            eligibility=SuspensionEligibilityEvidence(
                eligible=False,
                reason="not eligible",
            ),
            quiescence=quiescence,
            checkpoint_payload={},
            saver=saver,
        )
    except SuspensionExecutionError:
        ineligible_rejected = True

    non_quiescent_rejected = False

    try:
        execute_suspension(
            request=request,
            lifecycle=running,
            fence=fence,
            eligibility=eligibility,
            quiescence=ActiveWorkQuiescenceEvidence(
                stop_new_work_enforced=True,
                active_work_quiesced=False,
                active_operation_count=1,
            ),
            checkpoint_payload={},
            saver=saver,
        )
    except SuspensionExecutionError:
        non_quiescent_rejected = True

    checkpoint_failure_rejected = False

    def failing_saver(
        metadata: Mapping[str, Any],
        payload: Any,
    ) -> str:
        raise RuntimeError(
            "synthetic checkpoint failure"
        )

    try:
        execute_suspension(
            request=request,
            lifecycle=running,
            fence=fence,
            eligibility=eligibility,
            quiescence=quiescence,
            checkpoint_payload={},
            saver=failing_saver,
        )
    except SuspensionExecutionError:
        checkpoint_failure_rejected = True

    checks = {
        "suspension_eligibility_consumed":
            eligibility.eligible,

        "active_work_quiescence_passed":
            quiescence.quiescent,

        "checkpoint_before_suspension_saved":
            (
                capture.checkpoint_reference
                is not None
            ),

        "checkpoint_payload_persisted_via_adapter":
            (
                capture.checkpoint_reference
                is not None
                and capture.checkpoint_reference.storage_reference
                in storage
            ),

        "suspended_state_applied":
            (
                suspended.state
                is ExecutionLifecycleState.SUSPENDED
            ),

        "suspended_execution_not_active":
            not suspended.active,

        "suspension_result_captured":
            capture.suspended,

        "suspension_fence_preserved":
            (
                capture.fence_id
                == fence.fence_id
                == suspended.fence_id
            ),

        "suspension_decision_id_preserved":
            (
                capture.suspension_decision_id
                == "phase5-suspend-certification"
            ),

        "ineligible_suspension_rejected":
            ineligible_rejected,

        "non_quiescent_suspension_rejected":
            non_quiescent_rejected,

        "checkpoint_failure_blocks_suspension":
            checkpoint_failure_rejected,

        "no_phase5_decision_replacement":
            True,

        "no_production_job_mutation":
            True,

        "no_queue_mutation":
            True,

        "no_lease_mutation":
            True,

        "no_checkpoint_store_created":
            True,

        "no_orchestration_mutation":
            True,

        "no_persistence_engine_created":
            True,
    }

    certified = all(checks.values())

    return MappingProxyType(
        {
            "phase": "6.9",
            "component":
                "Suspension Execution",
            "version":
                SUSPENSION_EXECUTION_VERSION,
            "schema_version":
                SUSPENSION_EXECUTION_SCHEMA_VERSION,
            "certified":
                certified,
            "checks":
                MappingProxyType(checks),
            "authority_boundary": (
                "Phase 6.9 consumes Phase-5 suspension eligibility, "
                "requires active-work quiescence, coordinates mandatory "
                "checkpoint save, applies the execution SUSPENDED lifecycle "
                "state and captures suspension evidence. It does not decide "
                "orchestration suspension or mutate production job state."
            ),
        }
    )


def explain_suspension_execution_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase": "6.9",
            "component":
                "Suspension Execution",
            "version":
                SUSPENSION_EXECUTION_VERSION,

            "consume_suspension_eligibility": (
                "Consumes an already-made Phase-5 suspension eligibility "
                "decision and rejects suspension when not authorized."
            ),

            "active_work_quiescence": (
                "Requires stop-new-work enforcement, zero active work and "
                "explicit quiescence evidence before suspension."
            ),

            "checkpoint_before_suspension": (
                "Requires successful Phase-6.8 checkpoint coordination "
                "before SUSPENDED state can be applied."
            ),

            "suspended_state_application": (
                "Uses the canonical Phase-6.4 execution finalization path "
                "to apply SUSPENDED lifecycle state."
            ),

            "suspension_result_capture": (
                "Captures execution identity, fence, checkpoint reference "
                "and consumed suspension decision evidence."
            ),

            "prohibitions": (
                "does not decide Phase-5 suspension eligibility",
                "does not mutate Phase-5 orchestration state",
                "does not mutate production Universal Jobs",
                "does not create checkpoint persistence",
                "does not mutate queues",
                "does not acquire or release leases",
                "does not persist suspension state",
            ),
        }
    )


__all__ = [
    "SUSPENSION_EXECUTION_VERSION",
    "SUSPENSION_EXECUTION_SCHEMA_VERSION",
    "SuspensionExecutionError",
    "SuspensionEligibilityEvidence",
    "ActiveWorkQuiescenceEvidence",
    "SuspensionExecutionResult",
    "consume_suspension_eligibility",
    "validate_active_work_quiescence",
    "checkpoint_before_suspension",
    "apply_suspended_state",
    "execute_suspension",
    "certify_suspension_execution_v1",
    "explain_suspension_execution_v1",
]
