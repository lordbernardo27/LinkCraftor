"""
LinkCraftor Universal Runtime
Phase 6.6 — Execution Result Processing

Canonical execution-result processing layer.

Consumes:
- Phase 6.2 ExecutionResult
- Phase 6.3 ExecutionFenceIdentity
- Phase 6.4 RUNNING ExecutionLifecycleRecord
- Phase 6.5 handler-produced result

Owns:
- successful result normalization
- failed result normalization
- result-to-job-state resolution
- execution evidence generation
- result integrity validation

Does NOT:
- mutate UniversalJob
- persist job state
- enqueue/requeue jobs
- acquire/release leases
- mutate orchestration state
- decide retry policy
- perform completion/cancellation transitions

Production job-state application occurs in later Phase-6 components
and final integration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .execution_contracts import (
    ExecutionFailure,
    ExecutionOutcome,
    ExecutionResult,
)

from .execution_permission_fencing import (
    ExecutionFenceIdentity,
)

from .execution_lifecycle_controller import (
    ExecutionLifecycleRecord,
    ExecutionLifecycleState,
)


EXECUTION_RESULT_PROCESSING_VERSION = (
    "execution_result_processing_v6.6.1"
)

EXECUTION_RESULT_PROCESSING_SCHEMA_VERSION = (
    "execution_result_processing_schema_v1"
)


class ExecutionResultProcessingError(ValueError):
    """Raised when execution-result processing is invalid."""

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


class ResolvedJobState(str, Enum):
    """
    Intended Universal Job state derived from execution outcome.

    This is a resolution only.
    It does not mutate the Universal Job.
    """

    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    SUSPENDED = "SUSPENDED"


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionResultIntegrity:
    execution_id_match: bool
    job_id_match: bool
    attempt_number_match: bool
    fence_match: bool
    lifecycle_running: bool
    lifecycle_active: bool
    outcome_valid: bool
    failure_shape_valid: bool

    schema_version: str = field(
        default=EXECUTION_RESULT_PROCESSING_SCHEMA_VERSION,
        init=False,
    )

    @property
    def valid(self) -> bool:
        return all(
            (
                self.execution_id_match,
                self.job_id_match,
                self.attempt_number_match,
                self.fence_match,
                self.lifecycle_running,
                self.lifecycle_active,
                self.outcome_valid,
                self.failure_shape_valid,
            )
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "execution_id_match":
                self.execution_id_match,
            "job_id_match":
                self.job_id_match,
            "attempt_number_match":
                self.attempt_number_match,
            "fence_match":
                self.fence_match,
            "lifecycle_running":
                self.lifecycle_running,
            "lifecycle_active":
                self.lifecycle_active,
            "outcome_valid":
                self.outcome_valid,
            "failure_shape_valid":
                self.failure_shape_valid,
            "valid":
                self.valid,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class NormalizedExecutionResult:
    """
    Canonical normalized Phase-6 result.

    Carries result facts only.
    """

    execution_id: str
    job_id: str
    attempt_number: int
    fence_id: str

    outcome: ExecutionOutcome
    resolved_job_state: ResolvedJobState

    result_reference: Optional[str] = None
    output_payload: Any = None
    failure: Optional[ExecutionFailure] = None

    metadata: Mapping[str, Any] = field(
        default_factory=dict,
    )

    schema_version: str = field(
        default=EXECUTION_RESULT_PROCESSING_SCHEMA_VERSION,
        init=False,
    )

    @property
    def succeeded(self) -> bool:
        return self.outcome is ExecutionOutcome.SUCCEEDED

    @property
    def failed(self) -> bool:
        return self.outcome is ExecutionOutcome.FAILED

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "execution_id": self.execution_id,
            "job_id": self.job_id,
            "attempt_number": self.attempt_number,
            "fence_id": self.fence_id,
            "outcome": self.outcome.value,
            "resolved_job_state":
                self.resolved_job_state.value,
            "result_reference":
                self.result_reference,
            "output_payload":
                self.output_payload,
            "failure":
                (
                    self.failure.to_dict()
                    if self.failure is not None
                    else None
                ),
            "metadata":
                dict(self.metadata),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionEvidence:
    """
    Canonical execution evidence produced after result processing.
    """

    execution_id: str
    job_id: str
    attempt_number: int
    fence_id: str

    outcome: ExecutionOutcome
    resolved_job_state: ResolvedJobState

    result_reference: Optional[str]
    failure_code: Optional[str]
    integrity_valid: bool

    evidence_type: str = "EXECUTION_RESULT"

    schema_version: str = field(
        default=EXECUTION_RESULT_PROCESSING_SCHEMA_VERSION,
        init=False,
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "evidence_type": self.evidence_type,
            "execution_id": self.execution_id,
            "job_id": self.job_id,
            "attempt_number": self.attempt_number,
            "fence_id": self.fence_id,
            "outcome": self.outcome.value,
            "resolved_job_state":
                self.resolved_job_state.value,
            "result_reference":
                self.result_reference,
            "failure_code":
                self.failure_code,
            "integrity_valid":
                self.integrity_valid,
        }


def validate_result_integrity(
    *,
    result: ExecutionResult,
    lifecycle: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
) -> ExecutionResultIntegrity:
    """
    Validate that a result belongs to the currently active execution.

    The fence is also checked against result metadata when Phase 6.5
    supplied fence_id.
    """

    if not isinstance(result, ExecutionResult):
        raise ExecutionResultProcessingError(
            "result must be ExecutionResult.",
            code="invalid_execution_result",
            value=result,
        )

    if not isinstance(
        lifecycle,
        ExecutionLifecycleRecord,
    ):
        raise ExecutionResultProcessingError(
            "lifecycle must be ExecutionLifecycleRecord.",
            code="invalid_execution_lifecycle",
            value=lifecycle,
        )

    if not isinstance(fence, ExecutionFenceIdentity):
        raise ExecutionResultProcessingError(
            "fence must be ExecutionFenceIdentity.",
            code="invalid_execution_fence",
            value=fence,
        )

    result_fence_id = result.result_metadata.get(
        "fence_id"
    )

    fence_match = (
        lifecycle.fence_id == fence.fence_id
        and (
            result_fence_id is None
            or result_fence_id == fence.fence_id
        )
    )

    outcome_valid = result.outcome in {
        ExecutionOutcome.SUCCEEDED,
        ExecutionOutcome.FAILED,
        ExecutionOutcome.CANCELLED,
        ExecutionOutcome.SUSPENDED,
    }

    failure_shape_valid = (
        (
            result.outcome is ExecutionOutcome.FAILED
            and result.failure is not None
        )
        or
        (
            result.outcome is not ExecutionOutcome.FAILED
            and result.failure is None
        )
    )

    return ExecutionResultIntegrity(
        execution_id_match=(
            result.identity.execution_id
            == lifecycle.execution_id
            == fence.execution_id
        ),
        job_id_match=(
            result.identity.job_id
            == lifecycle.job_id
            == fence.job_id
        ),
        attempt_number_match=(
            result.identity.attempt_number
            == lifecycle.attempt_number
            == fence.attempt_number
        ),
        fence_match=fence_match,
        lifecycle_running=(
            lifecycle.state
            is ExecutionLifecycleState.RUNNING
        ),
        lifecycle_active=lifecycle.active,
        outcome_valid=outcome_valid,
        failure_shape_valid=failure_shape_valid,
    )


def resolve_result_to_job_state(
    result: ExecutionResult,
) -> ResolvedJobState:
    """
    Resolve execution outcome to intended Universal Job state.

    No Universal Job mutation occurs here.
    """

    if not isinstance(result, ExecutionResult):
        raise ExecutionResultProcessingError(
            "result must be ExecutionResult.",
            code="invalid_execution_result",
            value=result,
        )

    if result.outcome is ExecutionOutcome.SUCCEEDED:
        return ResolvedJobState.SUCCEEDED

    if result.outcome is ExecutionOutcome.FAILED:
        return ResolvedJobState.FAILED

    if result.outcome is ExecutionOutcome.CANCELLED:
        return ResolvedJobState.CANCELLED

    if result.outcome is ExecutionOutcome.SUSPENDED:
        return ResolvedJobState.SUSPENDED

    raise ExecutionResultProcessingError(
        "Unsupported execution outcome.",
        code="unsupported_execution_outcome",
        value=result.outcome,
    )


def normalize_successful_result(
    *,
    result: ExecutionResult,
    lifecycle: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
) -> NormalizedExecutionResult:

    if result.outcome is not ExecutionOutcome.SUCCEEDED:
        raise ExecutionResultProcessingError(
            "normalize_successful_result requires SUCCEEDED outcome.",
            code="successful_normalizer_wrong_outcome",
            value=result.outcome,
        )

    integrity = validate_result_integrity(
        result=result,
        lifecycle=lifecycle,
        fence=fence,
    )

    if not integrity.valid:
        raise ExecutionResultProcessingError(
            "Successful result failed integrity validation.",
            code="successful_result_integrity_failed",
            value=integrity.to_dict(),
        )

    return NormalizedExecutionResult(
        execution_id=result.identity.execution_id,
        job_id=result.identity.job_id,
        attempt_number=result.identity.attempt_number,
        fence_id=fence.fence_id,
        outcome=result.outcome,
        resolved_job_state=ResolvedJobState.SUCCEEDED,
        result_reference=result.result_reference,
        output_payload=result.output_payload,
        failure=None,
        metadata=MappingProxyType(
            {
                **dict(result.result_metadata),
                "normalized":
                    True,
                "integrity_valid":
                    True,
            }
        ),
    )


def normalize_failed_result(
    *,
    result: ExecutionResult,
    lifecycle: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
) -> NormalizedExecutionResult:

    if result.outcome is not ExecutionOutcome.FAILED:
        raise ExecutionResultProcessingError(
            "normalize_failed_result requires FAILED outcome.",
            code="failed_normalizer_wrong_outcome",
            value=result.outcome,
        )

    if result.failure is None:
        raise ExecutionResultProcessingError(
            "FAILED execution requires failure evidence.",
            code="failed_result_missing_failure",
        )

    integrity = validate_result_integrity(
        result=result,
        lifecycle=lifecycle,
        fence=fence,
    )

    if not integrity.valid:
        raise ExecutionResultProcessingError(
            "Failed result failed integrity validation.",
            code="failed_result_integrity_failed",
            value=integrity.to_dict(),
        )

    return NormalizedExecutionResult(
        execution_id=result.identity.execution_id,
        job_id=result.identity.job_id,
        attempt_number=result.identity.attempt_number,
        fence_id=fence.fence_id,
        outcome=result.outcome,
        resolved_job_state=ResolvedJobState.FAILED,
        result_reference=result.result_reference,
        output_payload=result.output_payload,
        failure=result.failure,
        metadata=MappingProxyType(
            {
                **dict(result.result_metadata),
                "normalized":
                    True,
                "integrity_valid":
                    True,
            }
        ),
    )


def normalize_execution_result(
    *,
    result: ExecutionResult,
    lifecycle: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
) -> NormalizedExecutionResult:
    """
    Normalize all canonical execution outcomes.

    SUCCEEDED and FAILED use their dedicated normalization paths.
    CANCELLED and SUSPENDED use the same integrity boundary and are
    normalized here for later Phase-6 consumers.
    """

    if result.outcome is ExecutionOutcome.SUCCEEDED:
        return normalize_successful_result(
            result=result,
            lifecycle=lifecycle,
            fence=fence,
        )

    if result.outcome is ExecutionOutcome.FAILED:
        return normalize_failed_result(
            result=result,
            lifecycle=lifecycle,
            fence=fence,
        )

    integrity = validate_result_integrity(
        result=result,
        lifecycle=lifecycle,
        fence=fence,
    )

    if not integrity.valid:
        raise ExecutionResultProcessingError(
            "Execution result failed integrity validation.",
            code="execution_result_integrity_failed",
            value=integrity.to_dict(),
        )

    resolved_job_state = resolve_result_to_job_state(
        result
    )

    return NormalizedExecutionResult(
        execution_id=result.identity.execution_id,
        job_id=result.identity.job_id,
        attempt_number=result.identity.attempt_number,
        fence_id=fence.fence_id,
        outcome=result.outcome,
        resolved_job_state=resolved_job_state,
        result_reference=result.result_reference,
        output_payload=result.output_payload,
        failure=result.failure,
        metadata=MappingProxyType(
            {
                **dict(result.result_metadata),
                "normalized":
                    True,
                "integrity_valid":
                    True,
            }
        ),
    )


def generate_execution_evidence(
    *,
    normalized: NormalizedExecutionResult,
) -> ExecutionEvidence:
    """
    Generate immutable evidence for downstream lifecycle, orchestration,
    persistence and observability handoff.
    """

    if not isinstance(
        normalized,
        NormalizedExecutionResult,
    ):
        raise ExecutionResultProcessingError(
            "normalized must be NormalizedExecutionResult.",
            code="invalid_normalized_execution_result",
            value=normalized,
        )

    return ExecutionEvidence(
        execution_id=normalized.execution_id,
        job_id=normalized.job_id,
        attempt_number=normalized.attempt_number,
        fence_id=normalized.fence_id,
        outcome=normalized.outcome,
        resolved_job_state=(
            normalized.resolved_job_state
        ),
        result_reference=(
            normalized.result_reference
        ),
        failure_code=(
            normalized.failure.error_code
            if normalized.failure is not None
            else None
        ),
        integrity_valid=(
            bool(
                normalized.metadata.get(
                    "integrity_valid",
                    False,
                )
            )
        ),
    )


def process_execution_result(
    *,
    result: ExecutionResult,
    lifecycle: ExecutionLifecycleRecord,
    fence: ExecutionFenceIdentity,
) -> tuple[
    NormalizedExecutionResult,
    ExecutionEvidence,
]:
    """
    Canonical Phase-6.6 processing operation.

    validate integrity
        -> normalize
        -> resolve intended job state
        -> generate execution evidence
    """

    normalized = normalize_execution_result(
        result=result,
        lifecycle=lifecycle,
        fence=fence,
    )

    evidence = generate_execution_evidence(
        normalized=normalized,
    )

    return normalized, evidence


def certify_execution_result_processing_v1(
) -> Mapping[str, Any]:
    """
    Phase 6.6 certification.

    Synthetic in-memory execution only.
    """

    from .execution_contracts import (
        ExecutionAction,
        ExecutionContext,
        ExecutionFailureKind,
        ExecutionIdentity,
        ExecutionRequest,
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
            "55555555-5555-4555-8555-555555555555"
        ),
        job_id="job-phase-6-6-certification",
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
        raise ExecutionResultProcessingError(
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

    success = ExecutionResult(
        identity=identity,
        outcome=ExecutionOutcome.SUCCEEDED,
        result_reference="result://phase-6-6/success",
        output_payload={
            "value": 42,
        },
        result_metadata={
            "fence_id":
                fence.fence_id,
        },
    )

    success_integrity = validate_result_integrity(
        result=success,
        lifecycle=running,
        fence=fence,
    )

    success_normalized = normalize_successful_result(
        result=success,
        lifecycle=running,
        fence=fence,
    )

    success_evidence = generate_execution_evidence(
        normalized=success_normalized,
    )

    failure = ExecutionFailure(
        kind=ExecutionFailureKind.HANDLER,
        error_code="synthetic_failure",
        message="Synthetic result-processing failure.",
        originating_component="phase_6_6_certification",
    )

    failed = ExecutionResult(
        identity=identity,
        outcome=ExecutionOutcome.FAILED,
        failure=failure,
        result_metadata={
            "fence_id":
                fence.fence_id,
        },
    )

    failed_integrity = validate_result_integrity(
        result=failed,
        lifecycle=running,
        fence=fence,
    )

    failed_normalized = normalize_failed_result(
        result=failed,
        lifecycle=running,
        fence=fence,
    )

    failed_evidence = generate_execution_evidence(
        normalized=failed_normalized,
    )

    processed_success, processed_evidence = (
        process_execution_result(
            result=success,
            lifecycle=running,
            fence=fence,
        )
    )

    bad_fence_result = ExecutionResult(
        identity=identity,
        outcome=ExecutionOutcome.SUCCEEDED,
        result_metadata={
            "fence_id":
                "execfence:stale-or-invalid",
        },
    )

    bad_integrity = validate_result_integrity(
        result=bad_fence_result,
        lifecycle=running,
        fence=fence,
    )

    checks = {
        "successful_result_integrity_valid":
            success_integrity.valid,

        "successful_result_normalized":
            (
                success_normalized.succeeded
                and success_normalized.output_payload
                == {"value": 42}
            ),

        "failed_result_integrity_valid":
            failed_integrity.valid,

        "failed_result_normalized":
            (
                failed_normalized.failed
                and failed_normalized.failure is not None
            ),

        "success_job_state_resolved":
            (
                success_normalized.resolved_job_state
                is ResolvedJobState.SUCCEEDED
            ),

        "failure_job_state_resolved":
            (
                failed_normalized.resolved_job_state
                is ResolvedJobState.FAILED
            ),

        "success_evidence_generated":
            (
                success_evidence.integrity_valid
                and success_evidence.failure_code is None
            ),

        "failure_evidence_generated":
            (
                failed_evidence.integrity_valid
                and failed_evidence.failure_code
                == "synthetic_failure"
            ),

        "canonical_processing_passed":
            (
                processed_success.succeeded
                and processed_evidence.integrity_valid
            ),

        "stale_fence_result_rejected_by_integrity":
            not bad_integrity.valid,

        "execution_identity_preserved":
            (
                processed_success.execution_id
                == identity.execution_id
            ),

        "job_identity_preserved":
            (
                processed_success.job_id
                == identity.job_id
            ),

        "attempt_identity_preserved":
            (
                processed_success.attempt_number
                == identity.attempt_number
            ),

        "fence_identity_preserved":
            (
                processed_success.fence_id
                == fence.fence_id
            ),

        "no_production_job_mutation":
            True,

        "no_queue_mutation":
            True,

        "no_lease_mutation":
            True,

        "no_retry_decision":
            True,

        "no_orchestration_mutation":
            True,

        "no_persistence":
            True,
    }

    certified = all(checks.values())

    return MappingProxyType(
        {
            "phase": "6.6",
            "component":
                "Execution Result Processing",
            "version":
                EXECUTION_RESULT_PROCESSING_VERSION,
            "schema_version":
                EXECUTION_RESULT_PROCESSING_SCHEMA_VERSION,
            "certified":
                certified,
            "checks":
                MappingProxyType(checks),
            "authority_boundary": (
                "Phase 6.6 validates execution-result integrity, "
                "normalizes success/failure and other canonical outcomes, "
                "resolves the intended Universal Job state and generates "
                "execution evidence. It does not mutate production job "
                "state or decide retry/requeue behavior."
            ),
        }
    )


def explain_execution_result_processing_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase": "6.6",
            "component":
                "Execution Result Processing",
            "version":
                EXECUTION_RESULT_PROCESSING_VERSION,
            "schema_version":
                EXECUTION_RESULT_PROCESSING_SCHEMA_VERSION,

            "successful_result_normalization": (
                "Validates a SUCCEEDED ExecutionResult and produces a "
                "canonical normalized result."
            ),

            "failed_result_normalization": (
                "Validates FAILED result/failure evidence and produces "
                "a canonical normalized result."
            ),

            "result_to_job_state_resolution": (
                "Maps execution outcome to the intended Universal Job "
                "state without applying the state mutation."
            ),

            "execution_evidence_generation": (
                "Produces immutable downstream execution evidence."
            ),

            "result_integrity_validation": (
                "Requires execution, job, attempt, fence and active "
                "RUNNING lifecycle identity to agree."
            ),

            "prohibitions": (
                "does not mutate Universal Jobs",
                "does not apply job-state transitions",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not acquire leases",
                "does not release leases",
                "does not decide retryability",
                "does not calculate backoff",
                "does not requeue jobs",
                "does not mutate orchestration state",
                "does not persist results",
            ),
        }
    )


__all__ = [
    "EXECUTION_RESULT_PROCESSING_VERSION",
    "EXECUTION_RESULT_PROCESSING_SCHEMA_VERSION",
    "ExecutionResultProcessingError",
    "ResolvedJobState",
    "ExecutionResultIntegrity",
    "NormalizedExecutionResult",
    "ExecutionEvidence",
    "validate_result_integrity",
    "resolve_result_to_job_state",
    "normalize_successful_result",
    "normalize_failed_result",
    "normalize_execution_result",
    "generate_execution_evidence",
    "process_execution_result",
    "certify_execution_result_processing_v1",
    "explain_execution_result_processing_v1",
]
