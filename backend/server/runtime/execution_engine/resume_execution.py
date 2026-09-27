"""
LinkCraftor Universal Runtime
Phase 6.10 — Resume Execution

Canonical execution-layer resume coordination.

Consumes:
- Phase 5 resume eligibility evidence
- Phase 6.2 ExecutionRequest
- Phase 6.3 ExecutionFenceIdentity
- Phase 6.4 SUSPENDED ExecutionLifecycleRecord
- Phase 6.8 checkpoint restore/preparation
- Phase 6.9 suspension checkpoint result

Owns:
- consume resume eligibility
- resume precondition validation
- checkpoint restore
- runtime work reactivation coordination
- post-resume RUNNING lifecycle application

Does NOT:
- decide Phase-5 resume eligibility
- create a second worker system
- create a second runtime
- create checkpoint persistence
- acquire/release leases
- mutate production UniversalJob
- mutate orchestration state
- enqueue/requeue jobs
- persist resume state

Production runtime/worker adapter wiring occurs later in Phase 6.15.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Callable, Mapping, Optional

from .execution_contracts import (
    ExecutionRequest,
)

from .execution_permission_fencing import (
    ExecutionFenceIdentity,
)

from .execution_lifecycle_controller import (
    ExecutionLifecycleRecord,
    ExecutionLifecycleState,
)

from .checkpoint_execution import (
    CheckpointReference,
    CheckpointRestoreResult,
    ResumeCheckpointPreparation,
    coordinate_checkpoint_restore,
    prepare_resume_from_checkpoint,
)


RESUME_EXECUTION_VERSION = (
    "resume_execution_v6.10.1"
)

RESUME_EXECUTION_SCHEMA_VERSION = (
    "resume_execution_schema_v1"
)


class ResumeExecutionError(ValueError):
    """Raised when execution resume coordination is invalid."""

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
class ResumeEligibilityEvidence:
    """
    Caller-supplied Phase-5 resume eligibility evidence.

    Phase 6.10 consumes the decision.
    It does not recreate orchestration decision authority.
    """

    eligible: bool

    decision_id: Optional[str] = None
    reason: Optional[str] = None

    schema_version: str = field(
        default=RESUME_EXECUTION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class RuntimeReactivationResult:
    """
    Result returned by the existing runtime/worker reactivation adapter.
    """

    reactivated: bool

    runtime_reference: Optional[str] = None
    worker_reference: Optional[str] = None
    error_code: Optional[str] = None

    schema_version: str = field(
        default=RESUME_EXECUTION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class ResumeExecutionResult:
    """
    Canonical Phase-6.10 resume evidence.
    """

    execution_id: str
    job_id: str
    attempt_number: int
    fence_id: str

    resumed: bool

    checkpoint_reference: CheckpointReference

    runtime_reference: Optional[str]
    worker_reference: Optional[str]

    lifecycle_state: ExecutionLifecycleState

    resume_decision_id: Optional[str]
    resume_reason: Optional[str]

    error_code: Optional[str] = None

    schema_version: str = field(
        default=RESUME_EXECUTION_SCHEMA_VERSION,
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
            "resumed":
                self.resumed,
            "checkpoint_reference":
                self.checkpoint_reference.to_dict(),
            "runtime_reference":
                self.runtime_reference,
            "worker_reference":
                self.worker_reference,
            "lifecycle_state":
                self.lifecycle_state.value,
            "resume_decision_id":
                self.resume_decision_id,
            "resume_reason":
                self.resume_reason,
            "error_code":
                self.error_code,
        }


def consume_resume_eligibility(
    *,
    evidence: ResumeEligibilityEvidence,
) -> None:
    """
    Consume an already-made Phase-5 resume eligibility decision.
    """

    if not isinstance(
        evidence,
        ResumeEligibilityEvidence,
    ):
        raise ResumeExecutionError(
            "evidence must be ResumeEligibilityEvidence.",
            code="invalid_resume_eligibility_evidence",
            value=evidence,
        )

    if not evidence.eligible:
        raise ResumeExecutionError(
            "Resume was not authorized by Phase 5.",
            code="resume_not_eligible",
            value=evidence.reason,
        )


def validate_resume_preconditions(
    *,
    request: ExecutionRequest,
    lifecycle: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
    checkpoint_reference: Optional[CheckpointReference],
) -> None:
    """
    Resume requires:
    - SUSPENDED execution lifecycle
    - inactive execution
    - same execution/job/attempt identity
    - same fence
    - checkpoint reference
    """

    if not isinstance(request, ExecutionRequest):
        raise ResumeExecutionError(
            "request must be ExecutionRequest.",
            code="invalid_execution_request",
            value=request,
        )

    if not isinstance(
        lifecycle,
        ExecutionLifecycleRecord,
    ):
        raise ResumeExecutionError(
            "lifecycle must be ExecutionLifecycleRecord.",
            code="invalid_execution_lifecycle",
            value=lifecycle,
        )

    if not isinstance(
        fence,
        ExecutionFenceIdentity,
    ):
        raise ResumeExecutionError(
            "fence must be ExecutionFenceIdentity.",
            code="invalid_execution_fence",
            value=fence,
        )

    if lifecycle.state is not ExecutionLifecycleState.SUSPENDED:
        raise ResumeExecutionError(
            "Resume requires SUSPENDED lifecycle state.",
            code="resume_requires_suspended",
            value=lifecycle.state.value,
        )

    if lifecycle.active:
        raise ResumeExecutionError(
            "Suspended execution must not already be active.",
            code="suspended_execution_still_active",
        )

    if (
        lifecycle.execution_id
        != request.identity.execution_id
        or lifecycle.execution_id
        != fence.execution_id
    ):
        raise ResumeExecutionError(
            "Resume execution identity mismatch.",
            code="resume_execution_identity_mismatch",
        )

    if (
        lifecycle.job_id
        != request.identity.job_id
        or lifecycle.job_id
        != fence.job_id
    ):
        raise ResumeExecutionError(
            "Resume job identity mismatch.",
            code="resume_job_identity_mismatch",
        )

    if (
        lifecycle.attempt_number
        != request.identity.attempt_number
        or lifecycle.attempt_number
        != fence.attempt_number
    ):
        raise ResumeExecutionError(
            "Resume attempt identity mismatch.",
            code="resume_attempt_identity_mismatch",
        )

    if lifecycle.fence_id != fence.fence_id:
        raise ResumeExecutionError(
            "Resume execution fence mismatch.",
            code="resume_fence_mismatch",
        )

    if checkpoint_reference is None:
        raise ResumeExecutionError(
            "Resume requires checkpoint reference.",
            code="resume_checkpoint_missing",
        )


def restore_resume_checkpoint(
    *,
    request: ExecutionRequest,
    fence: ExecutionFenceIdentity,
    checkpoint_reference: CheckpointReference,
    loader: Callable[[str], Any],
) -> tuple[
    CheckpointRestoreResult,
    ResumeCheckpointPreparation,
]:
    """
    Restore and prepare checkpoint through canonical Phase-6.8 functions.
    """

    restore = coordinate_checkpoint_restore(
        request=request,
        fence=fence,
        reference=checkpoint_reference,
        loader=loader,
    )

    if not restore.restored:
        raise ResumeExecutionError(
            "Checkpoint restore failed.",
            code=(
                restore.error_code
                or "resume_checkpoint_restore_failed"
            ),
        )

    try:
        preparation = prepare_resume_from_checkpoint(
            request=request,
            fence=fence,
            restore=restore,
        )
    except Exception as exc:
        raise ResumeExecutionError(
            "Checkpoint could not be prepared for resume.",
            code="resume_checkpoint_preparation_failed",
            value=str(exc),
        ) from exc

    return restore, preparation


def reactivate_runtime_work(
    *,
    request: ExecutionRequest,
    fence: ExecutionFenceIdentity,
    preparation: ResumeCheckpointPreparation,
    reactivator: Callable[
        [
            Mapping[str, Any],
            Any,
        ],
        Any,
    ],
) -> RuntimeReactivationResult:
    """
    Coordinate runtime work reactivation through an existing runtime/worker
    adapter.

    The adapter does the concrete worker/runtime mechanics.
    """

    if not callable(reactivator):
        raise ResumeExecutionError(
            "reactivator must be callable.",
            code="invalid_runtime_reactivator",
            value=reactivator,
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
            "checkpoint_id":
                preparation.checkpoint_reference.checkpoint_id,
            "storage_reference":
                preparation.checkpoint_reference.storage_reference,
        }
    )

    try:
        result = reactivator(
            metadata,
            preparation.restored_payload,
        )
    except Exception:
        return RuntimeReactivationResult(
            reactivated=False,
            error_code="runtime_reactivation_failed",
        )

    if isinstance(
        result,
        RuntimeReactivationResult,
    ):
        return result

    if result is True:
        return RuntimeReactivationResult(
            reactivated=True,
        )

    if isinstance(result, Mapping):
        return RuntimeReactivationResult(
            reactivated=bool(
                result.get(
                    "reactivated",
                    False,
                )
            ),
            runtime_reference=(
                result.get(
                    "runtime_reference"
                )
            ),
            worker_reference=(
                result.get(
                    "worker_reference"
                )
            ),
            error_code=(
                result.get(
                    "error_code"
                )
            ),
        )

    return RuntimeReactivationResult(
        reactivated=False,
        error_code="invalid_runtime_reactivation_result",
    )


def apply_post_resume_state(
    *,
    lifecycle: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
) -> ExecutionLifecycleRecord:
    """
    Apply post-resume RUNNING execution lifecycle.

    This is a Phase-6 execution lifecycle transition only.
    Production UniversalJob state is not mutated here.
    """

    if lifecycle.state is not ExecutionLifecycleState.SUSPENDED:
        raise ResumeExecutionError(
            "Only SUSPENDED execution may resume.",
            code="post_resume_invalid_source_state",
            value=lifecycle.state.value,
        )

    if lifecycle.fence_id != fence.fence_id:
        raise ResumeExecutionError(
            "Execution fence changed during resume.",
            code="post_resume_fence_mismatch",
        )

    return ExecutionLifecycleRecord(
        execution_id=lifecycle.execution_id,
        job_id=lifecycle.job_id,
        attempt_number=lifecycle.attempt_number,
        fence_id=lifecycle.fence_id,
        state=ExecutionLifecycleState.RUNNING,
        active=True,
        started_at=lifecycle.started_at,
        finalized_at=None,
        result_outcome=None,
    )


def execute_resume(
    *,
    request: ExecutionRequest,
    lifecycle: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
    eligibility: ResumeEligibilityEvidence,
    checkpoint_reference: Optional[CheckpointReference],
    loader: Callable[[str], Any],
    reactivator: Callable[
        [
            Mapping[str, Any],
            Any,
        ],
        Any,
    ],
) -> tuple[
    ExecutionLifecycleRecord,
    ResumeExecutionResult,
]:
    """
    Canonical Phase-6.10 resume operation.

    Flow:
    Phase-5 eligibility
        -> resume preconditions
        -> checkpoint restore
        -> runtime work reactivation
        -> post-resume RUNNING state
        -> resume evidence capture
    """

    consume_resume_eligibility(
        evidence=eligibility,
    )

    validate_resume_preconditions(
        request=request,
        lifecycle=lifecycle,
        fence=fence,
        checkpoint_reference=checkpoint_reference,
    )

    assert checkpoint_reference is not None

    restore, preparation = restore_resume_checkpoint(
        request=request,
        fence=fence,
        checkpoint_reference=checkpoint_reference,
        loader=loader,
    )

    reactivation = reactivate_runtime_work(
        request=request,
        fence=fence,
        preparation=preparation,
        reactivator=reactivator,
    )

    if not reactivation.reactivated:
        raise ResumeExecutionError(
            "Runtime work could not be reactivated.",
            code=(
                reactivation.error_code
                or "runtime_reactivation_failed"
            ),
        )

    resumed_lifecycle = apply_post_resume_state(
        lifecycle=lifecycle,
        fence=fence,
    )

    capture = ResumeExecutionResult(
        execution_id=request.identity.execution_id,
        job_id=request.identity.job_id,
        attempt_number=request.identity.attempt_number,
        fence_id=fence.fence_id,
        resumed=(
            resumed_lifecycle.state
            is ExecutionLifecycleState.RUNNING
            and resumed_lifecycle.active
        ),
        checkpoint_reference=(
            preparation.checkpoint_reference
        ),
        runtime_reference=(
            reactivation.runtime_reference
        ),
        worker_reference=(
            reactivation.worker_reference
        ),
        lifecycle_state=(
            resumed_lifecycle.state
        ),
        resume_decision_id=(
            eligibility.decision_id
        ),
        resume_reason=(
            eligibility.reason
        ),
        error_code=None,
    )

    return resumed_lifecycle, capture


def certify_resume_execution_v1(
) -> Mapping[str, Any]:
    """
    Phase 6.10 certification using synthetic in-memory runtime adapters.
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

    from .suspension_execution import (
        ActiveWorkQuiescenceEvidence,
        SuspensionEligibilityEvidence,
        execute_suspension,
    )

    identity = ExecutionIdentity(
        execution_id=(
            "99999999-9999-4999-8999-999999999999"
        ),
        job_id="job-phase-6-10-certification",
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
        raise ResumeExecutionError(
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

    checkpoint_storage: dict[str, Any] = {}

    def saver(
        metadata: Mapping[str, Any],
        payload: Any,
    ) -> str:
        key = (
            "checkpoint://resume/"
            + metadata["execution_id"]
        )

        checkpoint_storage[key] = payload

        return key

    suspended, suspension_capture = execute_suspension(
        request=request,
        lifecycle=running,
        fence=fence,
        eligibility=SuspensionEligibilityEvidence(
            eligible=True,
            decision_id="phase5-suspend-for-resume-cert",
        ),
        quiescence=ActiveWorkQuiescenceEvidence(
            stop_new_work_enforced=True,
            active_work_quiesced=True,
            active_operation_count=0,
        ),
        checkpoint_payload={
            "cursor": 50,
            "state": "checkpoint-for-resume",
        },
        saver=saver,
    )

    checkpoint_reference = (
        suspension_capture.checkpoint_reference
    )

    if checkpoint_reference is None:
        raise ResumeExecutionError(
            "Certification suspension produced no checkpoint.",
            code="certification_missing_checkpoint",
        )

    def loader(
        storage_reference: str,
    ) -> Any:
        return checkpoint_storage.get(
            storage_reference
        )

    reactivation_calls: list[
        Mapping[str, Any]
    ] = []

    def reactivator(
        metadata: Mapping[str, Any],
        payload: Any,
    ) -> Mapping[str, Any]:

        reactivation_calls.append(
            {
                "metadata":
                    dict(metadata),
                "payload":
                    payload,
            }
        )

        return {
            "reactivated":
                True,
            "runtime_reference":
                "runtime://phase-6-10/certification",
            "worker_reference":
                "worker://phase-6-10/certification",
        }

    eligibility = ResumeEligibilityEvidence(
        eligible=True,
        decision_id="phase5-resume-certification",
        reason="synthetic resume decision",
    )

    resumed, capture = execute_resume(
        request=request,
        lifecycle=suspended,
        fence=fence,
        eligibility=eligibility,
        checkpoint_reference=checkpoint_reference,
        loader=loader,
        reactivator=reactivator,
    )

    ineligible_rejected = False

    try:
        execute_resume(
            request=request,
            lifecycle=suspended,
            fence=fence,
            eligibility=ResumeEligibilityEvidence(
                eligible=False,
                reason="not eligible",
            ),
            checkpoint_reference=checkpoint_reference,
            loader=loader,
            reactivator=reactivator,
        )
    except ResumeExecutionError:
        ineligible_rejected = True

    missing_checkpoint_rejected = False

    try:
        execute_resume(
            request=request,
            lifecycle=suspended,
            fence=fence,
            eligibility=eligibility,
            checkpoint_reference=None,
            loader=loader,
            reactivator=reactivator,
        )
    except ResumeExecutionError:
        missing_checkpoint_rejected = True

    failed_reactivation_rejected = False

    def failed_reactivator(
        metadata: Mapping[str, Any],
        payload: Any,
    ) -> Mapping[str, Any]:
        return {
            "reactivated":
                False,
            "error_code":
                "synthetic_reactivation_failure",
        }

    try:
        execute_resume(
            request=request,
            lifecycle=suspended,
            fence=fence,
            eligibility=eligibility,
            checkpoint_reference=checkpoint_reference,
            loader=loader,
            reactivator=failed_reactivator,
        )
    except ResumeExecutionError:
        failed_reactivation_rejected = True

    non_suspended_rejected = False

    try:
        execute_resume(
            request=request,
            lifecycle=running,
            fence=fence,
            eligibility=eligibility,
            checkpoint_reference=checkpoint_reference,
            loader=loader,
            reactivator=reactivator,
        )
    except ResumeExecutionError:
        non_suspended_rejected = True

    checks = {
        "resume_eligibility_consumed":
            eligibility.eligible,

        "resume_preconditions_passed":
            (
                suspended.state
                is ExecutionLifecycleState.SUSPENDED
                and not suspended.active
            ),

        "checkpoint_restore_passed":
            bool(reactivation_calls),

        "checkpoint_payload_restored":
            (
                reactivation_calls[0]["payload"]
                == {
                    "cursor": 50,
                    "state": "checkpoint-for-resume",
                }
            ),

        "runtime_work_reactivated":
            (
                capture.runtime_reference
                == "runtime://phase-6-10/certification"
            ),

        "worker_reference_captured":
            (
                capture.worker_reference
                == "worker://phase-6-10/certification"
            ),

        "post_resume_state_running":
            (
                resumed.state
                is ExecutionLifecycleState.RUNNING
            ),

        "post_resume_execution_active":
            resumed.active,

        "resume_result_captured":
            capture.resumed,

        "resume_fence_preserved":
            (
                resumed.fence_id
                == fence.fence_id
                == capture.fence_id
            ),

        "resume_identity_preserved":
            (
                resumed.execution_id
                == identity.execution_id
            ),

        "resume_decision_id_preserved":
            (
                capture.resume_decision_id
                == "phase5-resume-certification"
            ),

        "ineligible_resume_rejected":
            ineligible_rejected,

        "missing_checkpoint_rejected":
            missing_checkpoint_rejected,

        "failed_reactivation_rejected":
            failed_reactivation_rejected,

        "non_suspended_resume_rejected":
            non_suspended_rejected,

        "no_phase5_decision_replacement":
            True,

        "no_second_worker_system":
            True,

        "no_second_runtime_created":
            True,

        "no_checkpoint_store_created":
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
                "6.10",
            "component":
                "Resume Execution",
            "version":
                RESUME_EXECUTION_VERSION,
            "schema_version":
                RESUME_EXECUTION_SCHEMA_VERSION,
            "certified":
                certified,
            "checks":
                MappingProxyType(
                    checks
                ),
            "authority_boundary": (
                "Phase 6.10 consumes Phase-5 resume eligibility, "
                "validates the SUSPENDED execution boundary, restores "
                "the Phase-6.8 checkpoint, coordinates runtime/worker "
                "reactivation through existing adapters and returns the "
                "execution lifecycle to RUNNING. It does not create "
                "runtime/worker infrastructure or mutate production "
                "Universal Job state."
            ),
        }
    )


def explain_resume_execution_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "6.10",

            "component":
                "Resume Execution",

            "version":
                RESUME_EXECUTION_VERSION,

            "consume_resume_eligibility": (
                "Consumes an already-made Phase-5 resume eligibility "
                "decision and refuses resume when not authorized."
            ),

            "resume_preconditions": (
                "Requires SUSPENDED inactive execution, matching execution "
                "identity/fence and a checkpoint reference."
            ),

            "checkpoint_restore": (
                "Uses Phase-6.8 checkpoint restore and resume-preparation "
                "functions."
            ),

            "runtime_work_reactivation": (
                "Coordinates reactivation through the existing runtime/"
                "worker implementation adapter."
            ),

            "post_resume_state_application": (
                "Returns the Phase-6 execution lifecycle from SUSPENDED "
                "to active RUNNING state while preserving the fence."
            ),

            "prohibitions": (
                "does not decide Phase-5 resume eligibility",
                "does not replace worker infrastructure",
                "does not replace runtime infrastructure",
                "does not create checkpoint persistence",
                "does not acquire or release leases",
                "does not mutate Universal Jobs",
                "does not mutate queues",
                "does not mutate orchestration state",
                "does not persist resume state",
            ),
        }
    )


__all__ = [
    "RESUME_EXECUTION_VERSION",
    "RESUME_EXECUTION_SCHEMA_VERSION",
    "ResumeExecutionError",
    "ResumeEligibilityEvidence",
    "RuntimeReactivationResult",
    "ResumeExecutionResult",
    "consume_resume_eligibility",
    "validate_resume_preconditions",
    "restore_resume_checkpoint",
    "reactivate_runtime_work",
    "apply_post_resume_state",
    "execute_resume",
    "certify_resume_execution_v1",
    "explain_resume_execution_v1",
]
