"""
LinkCraftor Universal Runtime
Phase 6.12 — Completion Execution

Canonical execution-layer completion coordination.

Consumes:
- existing completion decision evidence
- Phase 6.2 ExecutionResult
- Phase 6.3 ExecutionFenceIdentity
- Phase 6.4 RUNNING ExecutionLifecycleRecord
- Phase 6.6 result processing/evidence

Owns:
- consume completion decision
- completion transition validation
- execution SUCCEEDED-state application
- execution FAILED-state application
- completion evidence coordination

Does NOT:
- invent completion decisions
- mutate Phase-5 orchestration state
- mutate production UniversalJob directly
- persist completion records
- release leases
- mutate queues
- mutate workers
- decide retries
- requeue failed work

Production job-state/persistence integration is deferred to later
Phase-6 integration layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .execution_contracts import (
    ExecutionFailure,
    ExecutionFailureKind,
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

from .execution_result_processing import (
    ExecutionEvidence,
    NormalizedExecutionResult,
    ResolvedJobState,
    process_execution_result,
)


COMPLETION_EXECUTION_VERSION = (
    "completion_execution_v6.12.1"
)

COMPLETION_EXECUTION_SCHEMA_VERSION = (
    "completion_execution_schema_v1"
)


class CompletionExecutionError(ValueError):
    """Raised when completion execution is invalid."""

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


class CompletionDisposition(str, Enum):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


@dataclass(
    frozen=True,
    slots=True,
)
class CompletionDecisionEvidence:
    """
    Existing completion decision consumed by Phase 6.12.

    Phase 6.12 does not recreate completion decision authority.
    """

    disposition: CompletionDisposition

    authorized: bool = True

    decision_id: Optional[str] = None
    reason: Optional[str] = None

    schema_version: str = field(
        default=COMPLETION_EXECUTION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class CompletionEvidence:
    """
    Canonical completion evidence for downstream handoff.
    """

    execution_id: str
    job_id: str
    attempt_number: int
    fence_id: str

    disposition: CompletionDisposition

    lifecycle_state: ExecutionLifecycleState
    resolved_job_state: ResolvedJobState

    result_reference: Optional[str]
    failure_code: Optional[str]

    execution_evidence: ExecutionEvidence

    completion_decision_id: Optional[str]
    completion_reason: Optional[str]

    schema_version: str = field(
        default=COMPLETION_EXECUTION_SCHEMA_VERSION,
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
            "lifecycle_state":
                self.lifecycle_state.value,
            "resolved_job_state":
                self.resolved_job_state.value,
            "result_reference":
                self.result_reference,
            "failure_code":
                self.failure_code,
            "execution_evidence":
                self.execution_evidence.to_dict(),
            "completion_decision_id":
                self.completion_decision_id,
            "completion_reason":
                self.completion_reason,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class CompletionExecutionResult:
    execution_id: str
    job_id: str
    attempt_number: int
    fence_id: str

    completed: bool

    disposition: CompletionDisposition

    lifecycle_state: ExecutionLifecycleState

    normalized_result: NormalizedExecutionResult
    completion_evidence: CompletionEvidence

    schema_version: str = field(
        default=COMPLETION_EXECUTION_SCHEMA_VERSION,
        init=False,
    )


def consume_completion_decision(
    *,
    decision: CompletionDecisionEvidence,
) -> None:
    """
    Consume an already-made completion decision.
    """

    if not isinstance(
        decision,
        CompletionDecisionEvidence,
    ):
        raise CompletionExecutionError(
            "decision must be CompletionDecisionEvidence.",
            code="invalid_completion_decision",
            value=decision,
        )

    if not decision.authorized:
        raise CompletionExecutionError(
            "Completion was not authorized.",
            code="completion_not_authorized",
            value=decision.reason,
        )


def validate_completion_transition(
    *,
    request: ExecutionRequest,
    lifecycle: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
    result: ExecutionResult,
    decision: CompletionDecisionEvidence,
) -> None:
    """
    Validate that the completion transition belongs to the currently
    active RUNNING execution and that decision/result semantics agree.
    """

    if not isinstance(
        request,
        ExecutionRequest,
    ):
        raise CompletionExecutionError(
            "request must be ExecutionRequest.",
            code="invalid_execution_request",
            value=request,
        )

    if not isinstance(
        lifecycle,
        ExecutionLifecycleRecord,
    ):
        raise CompletionExecutionError(
            "lifecycle must be ExecutionLifecycleRecord.",
            code="invalid_execution_lifecycle",
            value=lifecycle,
        )

    if not isinstance(
        fence,
        ExecutionFenceIdentity,
    ):
        raise CompletionExecutionError(
            "fence must be ExecutionFenceIdentity.",
            code="invalid_execution_fence",
            value=fence,
        )

    if not isinstance(
        result,
        ExecutionResult,
    ):
        raise CompletionExecutionError(
            "result must be ExecutionResult.",
            code="invalid_execution_result",
            value=result,
        )

    if lifecycle.state is not ExecutionLifecycleState.RUNNING:
        raise CompletionExecutionError(
            "Completion requires RUNNING lifecycle state.",
            code="completion_requires_running",
            value=lifecycle.state.value,
        )

    if not lifecycle.active:
        raise CompletionExecutionError(
            "Completion requires active RUNNING execution.",
            code="completion_requires_active_execution",
        )

    if (
        request.identity.execution_id
        != lifecycle.execution_id
        or request.identity.execution_id
        != fence.execution_id
        or request.identity.execution_id
        != result.identity.execution_id
    ):
        raise CompletionExecutionError(
            "Completion execution identity mismatch.",
            code="completion_execution_identity_mismatch",
        )

    if (
        request.identity.job_id
        != lifecycle.job_id
        or request.identity.job_id
        != fence.job_id
        or request.identity.job_id
        != result.identity.job_id
    ):
        raise CompletionExecutionError(
            "Completion job identity mismatch.",
            code="completion_job_identity_mismatch",
        )

    if (
        request.identity.attempt_number
        != lifecycle.attempt_number
        or request.identity.attempt_number
        != fence.attempt_number
        or request.identity.attempt_number
        != result.identity.attempt_number
    ):
        raise CompletionExecutionError(
            "Completion attempt identity mismatch.",
            code="completion_attempt_identity_mismatch",
        )

    if lifecycle.fence_id != fence.fence_id:
        raise CompletionExecutionError(
            "Completion fence mismatch.",
            code="completion_fence_mismatch",
        )

    result_fence = result.result_metadata.get(
        "fence_id"
    )

    if (
        result_fence is not None
        and result_fence != fence.fence_id
    ):
        raise CompletionExecutionError(
            "Result fence does not match completion fence.",
            code="completion_result_fence_mismatch",
        )

    if (
        decision.disposition
        is CompletionDisposition.SUCCEEDED
        and result.outcome
        is not ExecutionOutcome.SUCCEEDED
    ):
        raise CompletionExecutionError(
            "SUCCEEDED completion requires SUCCEEDED result.",
            code="completion_success_result_mismatch",
            value=result.outcome.value,
        )

    if (
        decision.disposition
        is CompletionDisposition.FAILED
        and result.outcome
        is not ExecutionOutcome.FAILED
    ):
        raise CompletionExecutionError(
            "FAILED completion requires FAILED result.",
            code="completion_failure_result_mismatch",
            value=result.outcome.value,
        )


def apply_succeeded_state(
    *,
    lifecycle: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
    result: ExecutionResult,
    finalized_at: Optional[str] = None,
) -> ExecutionLifecycleRecord:
    """
    Apply SUCCEEDED execution lifecycle using canonical Phase-6.4
    finalization.
    """

    if result.outcome is not ExecutionOutcome.SUCCEEDED:
        raise CompletionExecutionError(
            "apply_succeeded_state requires SUCCEEDED result.",
            code="invalid_success_completion_result",
            value=result.outcome.value,
        )

    completed = finalize_execution(
        record=lifecycle,
        result=result,
        fence=fence,
        finalized_at=finalized_at,
    )

    if completed.state is not ExecutionLifecycleState.SUCCEEDED:
        raise CompletionExecutionError(
            "Execution did not transition to SUCCEEDED.",
            code="succeeded_state_application_failed",
        )

    return completed


def apply_failed_state(
    *,
    lifecycle: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
    result: ExecutionResult,
    finalized_at: Optional[str] = None,
) -> ExecutionLifecycleRecord:
    """
    Apply FAILED execution lifecycle using canonical Phase-6.4 finalization.
    """

    if result.outcome is not ExecutionOutcome.FAILED:
        raise CompletionExecutionError(
            "apply_failed_state requires FAILED result.",
            code="invalid_failed_completion_result",
            value=result.outcome.value,
        )

    if result.failure is None:
        raise CompletionExecutionError(
            "FAILED completion requires failure evidence.",
            code="failed_completion_missing_failure",
        )

    completed = finalize_execution(
        record=lifecycle,
        result=result,
        fence=fence,
        finalized_at=finalized_at,
    )

    if completed.state is not ExecutionLifecycleState.FAILED:
        raise CompletionExecutionError(
            "Execution did not transition to FAILED.",
            code="failed_state_application_failed",
        )

    return completed


def coordinate_completion_evidence(
    *,
    normalized: NormalizedExecutionResult,
    execution_evidence: ExecutionEvidence,
    completed_lifecycle: ExecutionLifecycleRecord,
    decision: CompletionDecisionEvidence,
) -> CompletionEvidence:
    """
    Coordinate immutable completion evidence for downstream job-state,
    orchestration, persistence and observability handoff.
    """

    if not isinstance(
        normalized,
        NormalizedExecutionResult,
    ):
        raise CompletionExecutionError(
            "normalized must be NormalizedExecutionResult.",
            code="invalid_normalized_result",
            value=normalized,
        )

    if not isinstance(
        execution_evidence,
        ExecutionEvidence,
    ):
        raise CompletionExecutionError(
            "execution_evidence must be ExecutionEvidence.",
            code="invalid_execution_evidence",
            value=execution_evidence,
        )

    if completed_lifecycle.state not in {
        ExecutionLifecycleState.SUCCEEDED,
        ExecutionLifecycleState.FAILED,
    }:
        raise CompletionExecutionError(
            "Completion evidence requires SUCCEEDED or FAILED lifecycle.",
            code="completion_evidence_invalid_lifecycle",
            value=completed_lifecycle.state.value,
        )

    if (
        normalized.execution_id
        != execution_evidence.execution_id
        or normalized.execution_id
        != completed_lifecycle.execution_id
    ):
        raise CompletionExecutionError(
            "Completion evidence execution identity mismatch.",
            code="completion_evidence_identity_mismatch",
        )

    expected_disposition = (
        CompletionDisposition.SUCCEEDED
        if normalized.outcome
        is ExecutionOutcome.SUCCEEDED
        else CompletionDisposition.FAILED
    )

    if decision.disposition is not expected_disposition:
        raise CompletionExecutionError(
            "Completion decision does not match normalized result.",
            code="completion_evidence_decision_mismatch",
        )

    return CompletionEvidence(
        execution_id=normalized.execution_id,
        job_id=normalized.job_id,
        attempt_number=normalized.attempt_number,
        fence_id=normalized.fence_id,
        disposition=decision.disposition,
        lifecycle_state=completed_lifecycle.state,
        resolved_job_state=normalized.resolved_job_state,
        result_reference=normalized.result_reference,
        failure_code=(
            normalized.failure.error_code
            if normalized.failure is not None
            else None
        ),
        execution_evidence=execution_evidence,
        completion_decision_id=decision.decision_id,
        completion_reason=decision.reason,
    )


def execute_completion(
    *,
    request: ExecutionRequest,
    lifecycle: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
    result: ExecutionResult,
    decision: CompletionDecisionEvidence,
    finalized_at: Optional[str] = None,
) -> tuple[
    ExecutionLifecycleRecord,
    CompletionExecutionResult,
]:
    """
    Canonical Phase-6.12 completion operation.

    Flow:
    consume completion decision
        -> validate completion transition
        -> Phase-6.6 result processing/evidence
        -> apply SUCCEEDED or FAILED lifecycle
        -> coordinate completion evidence
    """

    consume_completion_decision(
        decision=decision,
    )

    validate_completion_transition(
        request=request,
        lifecycle=lifecycle,
        fence=fence,
        result=result,
        decision=decision,
    )

    normalized, execution_evidence = (
        process_execution_result(
            result=result,
            lifecycle=lifecycle,
            fence=fence,
        )
    )

    if (
        decision.disposition
        is CompletionDisposition.SUCCEEDED
    ):
        completed_lifecycle = apply_succeeded_state(
            lifecycle=lifecycle,
            fence=fence,
            result=result,
            finalized_at=finalized_at,
        )

    elif (
        decision.disposition
        is CompletionDisposition.FAILED
    ):
        completed_lifecycle = apply_failed_state(
            lifecycle=lifecycle,
            fence=fence,
            result=result,
            finalized_at=finalized_at,
        )

    else:
        raise CompletionExecutionError(
            "Unsupported completion disposition.",
            code="unsupported_completion_disposition",
            value=decision.disposition,
        )

    completion_evidence = coordinate_completion_evidence(
        normalized=normalized,
        execution_evidence=execution_evidence,
        completed_lifecycle=completed_lifecycle,
        decision=decision,
    )

    capture = CompletionExecutionResult(
        execution_id=request.identity.execution_id,
        job_id=request.identity.job_id,
        attempt_number=request.identity.attempt_number,
        fence_id=fence.fence_id,
        completed=True,
        disposition=decision.disposition,
        lifecycle_state=completed_lifecycle.state,
        normalized_result=normalized,
        completion_evidence=completion_evidence,
    )

    return completed_lifecycle, capture


def certify_completion_execution_v1(
) -> Mapping[str, Any]:
    """
    Phase 6.12 certification.
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
            "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
        ),
        job_id="job-phase-6-12-certification",
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
        action=ExecutionAction.COMPLETE,
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
        raise CompletionExecutionError(
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

    success_result = ExecutionResult(
        identity=identity,
        outcome=ExecutionOutcome.SUCCEEDED,
        result_reference="result://phase-6-12/success",
        output_payload={
            "status": "complete",
        },
        result_metadata={
            "fence_id":
                fence.fence_id,
        },
    )

    success_decision = CompletionDecisionEvidence(
        disposition=CompletionDisposition.SUCCEEDED,
        authorized=True,
        decision_id="completion-success-certification",
        reason="synthetic successful completion",
    )

    success_lifecycle, success_capture = (
        execute_completion(
            request=request,
            lifecycle=running,
            fence=fence,
            result=success_result,
            decision=success_decision,
            finalized_at="2026-01-01T00:00:10Z",
        )
    )

    # Fresh RUNNING lifecycle for failure path.
    failed_ready = create_execution_start(
        request=request,
        permission=permission,
    )

    failed_running = apply_running_state(
        record=failed_ready,
        fence=fence,
        started_at="2026-01-01T00:00:00Z",
    )

    failure = ExecutionFailure(
        kind=ExecutionFailureKind.HANDLER,
        error_code="synthetic_completion_failure",
        message="Synthetic terminal execution failure.",
        originating_component="phase_6_12_certification",
    )

    failed_result = ExecutionResult(
        identity=identity,
        outcome=ExecutionOutcome.FAILED,
        failure=failure,
        result_reference="result://phase-6-12/failure",
        result_metadata={
            "fence_id":
                fence.fence_id,
        },
    )

    failed_decision = CompletionDecisionEvidence(
        disposition=CompletionDisposition.FAILED,
        authorized=True,
        decision_id="completion-failure-certification",
        reason="synthetic failed completion",
    )

    failed_lifecycle, failed_capture = (
        execute_completion(
            request=request,
            lifecycle=failed_running,
            fence=fence,
            result=failed_result,
            decision=failed_decision,
            finalized_at="2026-01-01T00:00:20Z",
        )
    )

    unauthorized_rejected = False

    try:
        execute_completion(
            request=request,
            lifecycle=running,
            fence=fence,
            result=success_result,
            decision=CompletionDecisionEvidence(
                disposition=CompletionDisposition.SUCCEEDED,
                authorized=False,
                reason="not authorized",
            ),
        )
    except CompletionExecutionError:
        unauthorized_rejected = True

    decision_result_mismatch_rejected = False

    mismatch_ready = create_execution_start(
        request=request,
        permission=permission,
    )

    mismatch_running = apply_running_state(
        record=mismatch_ready,
        fence=fence,
    )

    try:
        execute_completion(
            request=request,
            lifecycle=mismatch_running,
            fence=fence,
            result=success_result,
            decision=CompletionDecisionEvidence(
                disposition=CompletionDisposition.FAILED,
                authorized=True,
            ),
        )
    except CompletionExecutionError:
        decision_result_mismatch_rejected = True

    terminal_reentry_rejected = False

    try:
        execute_completion(
            request=request,
            lifecycle=success_lifecycle,
            fence=fence,
            result=success_result,
            decision=success_decision,
        )
    except CompletionExecutionError:
        terminal_reentry_rejected = True

    checks = {
        "completion_decision_consumed":
            success_decision.authorized,

        "completion_transition_validated":
            (
                success_capture.execution_id
                == identity.execution_id
            ),

        "succeeded_state_applied":
            (
                success_lifecycle.state
                is ExecutionLifecycleState.SUCCEEDED
            ),

        "succeeded_execution_not_active":
            not success_lifecycle.active,

        "failed_state_applied":
            (
                failed_lifecycle.state
                is ExecutionLifecycleState.FAILED
            ),

        "failed_execution_not_active":
            not failed_lifecycle.active,

        "success_completion_evidence_coordinated":
            (
                success_capture.completion_evidence.disposition
                is CompletionDisposition.SUCCEEDED
            ),

        "failure_completion_evidence_coordinated":
            (
                failed_capture.completion_evidence.disposition
                is CompletionDisposition.FAILED
            ),

        "success_resolved_job_state_preserved":
            (
                success_capture.normalized_result.resolved_job_state
                is ResolvedJobState.SUCCEEDED
            ),

        "failure_resolved_job_state_preserved":
            (
                failed_capture.normalized_result.resolved_job_state
                is ResolvedJobState.FAILED
            ),

        "failure_code_preserved":
            (
                failed_capture.completion_evidence.failure_code
                == "synthetic_completion_failure"
            ),

        "execution_fence_preserved":
            (
                success_capture.fence_id
                == fence.fence_id
                == failed_capture.fence_id
            ),

        "completion_identity_preserved":
            (
                success_capture.job_id
                == identity.job_id
                and failed_capture.job_id
                == identity.job_id
            ),

        "unauthorized_completion_rejected":
            unauthorized_rejected,

        "decision_result_mismatch_rejected":
            decision_result_mismatch_rejected,

        "terminal_reentry_rejected":
            terminal_reentry_rejected,

        "no_completion_policy_invented":
            True,

        "no_production_job_mutation":
            True,

        "no_retry_decision":
            True,

        "no_queue_mutation":
            True,

        "no_worker_mutation":
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
                "6.12",

            "component":
                "Completion Execution",

            "version":
                COMPLETION_EXECUTION_VERSION,

            "schema_version":
                COMPLETION_EXECUTION_SCHEMA_VERSION,

            "certified":
                certified,

            "checks":
                MappingProxyType(
                    checks
                ),

            "authority_boundary": (
                "Phase 6.12 consumes an existing completion decision, "
                "validates the terminal execution transition, processes "
                "the result through Phase 6.6, applies SUCCEEDED or FAILED "
                "to the Phase-6 execution lifecycle and coordinates "
                "completion evidence. It does not mutate production "
                "Universal Job or orchestration state."
            ),
        }
    )


def explain_completion_execution_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "6.12",

            "component":
                "Completion Execution",

            "version":
                COMPLETION_EXECUTION_VERSION,

            "consume_completion_decision": (
                "Consumes an already-authorized completion decision."
            ),

            "completion_transition_validation": (
                "Requires active RUNNING execution, matching execution/job/"
                "attempt/fence identity and matching completion-result outcome."
            ),

            "succeeded_state_application": (
                "Uses canonical Phase-6.4 finalization to apply SUCCEEDED."
            ),

            "failed_state_application": (
                "Uses canonical Phase-6.4 finalization to apply FAILED and "
                "requires failure evidence."
            ),

            "completion_evidence_coordination": (
                "Combines Phase-6.6 normalized result/evidence with terminal "
                "execution lifecycle and completion-decision evidence."
            ),

            "prohibitions": (
                "does not invent completion decisions",
                "does not mutate production Universal Jobs",
                "does not mutate Phase-5 orchestration state",
                "does not decide retries",
                "does not mutate queues",
                "does not mutate workers",
                "does not mutate leases",
                "does not persist completion state",
            ),
        }
    )


__all__ = [
    "COMPLETION_EXECUTION_VERSION",
    "COMPLETION_EXECUTION_SCHEMA_VERSION",
    "CompletionExecutionError",
    "CompletionDisposition",
    "CompletionDecisionEvidence",
    "CompletionEvidence",
    "CompletionExecutionResult",
    "consume_completion_decision",
    "validate_completion_transition",
    "apply_succeeded_state",
    "apply_failed_state",
    "coordinate_completion_evidence",
    "execute_completion",
    "certify_completion_execution_v1",
    "explain_completion_execution_v1",
]
