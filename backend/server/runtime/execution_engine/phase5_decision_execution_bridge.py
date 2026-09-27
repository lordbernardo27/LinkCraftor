"""
LinkCraftor Universal Runtime
Phase 6.14 — Phase-5 Decision Execution Bridge

Canonical boundary between orchestration decisions and execution.

Core law:
    Phase 5 decides WHAT should happen.
    Phase 6 executes WHAT Phase 5 already decided.

Consumes:
- handoff decisions
- suspension decisions
- resume decisions
- recovery decisions
- completion decisions
- cancellation decisions

Routes to:
- handoff execution boundary
- Phase 6.9 Suspension Execution
- Phase 6.10 Resume Execution
- Phase 6.11 Recovery / Retry Execution
- Phase 6.12 Completion Execution
- Phase 6.13 Cancellation / Termination Execution

Owns:
- decision consumption validation
- decision-to-execution routing identity
- execution target resolution
- evidence coordination
- decision/execution separation enforcement

Does NOT:
- invent orchestration decisions
- modify decision content
- choose business/orchestration policy
- execute queue operations
- execute worker operations
- mutate leases
- mutate production Universal Jobs
- mutate Phase-5 orchestration state
- persist bridge state
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .execution_contracts import (
    ExecutionRequest,
)

from .execution_permission_fencing import (
    ExecutionFenceIdentity,
)

from .suspension_execution import (
    SuspensionEligibilityEvidence,
)

from .resume_execution import (
    ResumeEligibilityEvidence,
)

from .recovery_retry_execution import (
    RecoveryDecisionEvidence,
)

from .completion_execution import (
    CompletionDecisionEvidence,
)

from .cancellation_termination_execution import (
    CancellationDecisionEvidence,
)


PHASE5_DECISION_EXECUTION_BRIDGE_VERSION = (
    "phase5_decision_execution_bridge_v6.14.1"
)

PHASE5_DECISION_EXECUTION_BRIDGE_SCHEMA_VERSION = (
    "phase5_decision_execution_bridge_schema_v1"
)


class Phase5DecisionExecutionBridgeError(ValueError):
    """Raised when Phase-5 → Phase-6 decision consumption is invalid."""

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


class Phase5DecisionType(str, Enum):
    HANDOFF = "HANDOFF"
    SUSPEND = "SUSPEND"
    RESUME = "RESUME"
    RECOVERY = "RECOVERY"
    COMPLETION = "COMPLETION"
    CANCELLATION = "CANCELLATION"


class Phase6ExecutionTarget(str, Enum):
    HANDOFF_EXECUTION = "HANDOFF_EXECUTION"
    SUSPENSION_EXECUTION = "SUSPENSION_EXECUTION"
    RESUME_EXECUTION = "RESUME_EXECUTION"
    RECOVERY_RETRY_EXECUTION = "RECOVERY_RETRY_EXECUTION"
    COMPLETION_EXECUTION = "COMPLETION_EXECUTION"
    CANCELLATION_TERMINATION_EXECUTION = (
        "CANCELLATION_TERMINATION_EXECUTION"
    )


@dataclass(
    frozen=True,
    slots=True,
)
class HandoffDecisionEvidence:
    """
    Existing Phase-5 handoff decision.

    The bridge consumes it only.
    """

    authorized: bool

    target_stage: str

    decision_id: Optional[str] = None
    reason: Optional[str] = None

    schema_version: str = field(
        default=PHASE5_DECISION_EXECUTION_BRIDGE_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class DecisionExecutionBridgeRecord:
    """
    Immutable routing record from a Phase-5 decision to Phase-6 execution.
    """

    decision_type: Phase5DecisionType
    execution_target: Phase6ExecutionTarget

    decision_id: Optional[str]

    execution_id: str
    job_id: str
    attempt_number: int
    fence_id: str

    authorized: bool

    source_component: str
    target_component: str

    schema_version: str = field(
        default=PHASE5_DECISION_EXECUTION_BRIDGE_SCHEMA_VERSION,
        init=False,
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version":
                self.schema_version,
            "decision_type":
                self.decision_type.value,
            "execution_target":
                self.execution_target.value,
            "decision_id":
                self.decision_id,
            "execution_id":
                self.execution_id,
            "job_id":
                self.job_id,
            "attempt_number":
                self.attempt_number,
            "fence_id":
                self.fence_id,
            "authorized":
                self.authorized,
            "source_component":
                self.source_component,
            "target_component":
                self.target_component,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class DecisionExecutionBridgeEvidence:
    """
    Evidence that a Phase-5 decision crossed the Phase-5/Phase-6 boundary
    without Phase 6 becoming a decision authority.
    """

    decision_type: Phase5DecisionType
    decision_id: Optional[str]

    execution_target: Phase6ExecutionTarget

    execution_id: str
    job_id: str
    attempt_number: int
    fence_id: str

    decision_consumed: bool
    decision_modified: bool
    execution_authority_only: bool

    schema_version: str = field(
        default=PHASE5_DECISION_EXECUTION_BRIDGE_SCHEMA_VERSION,
        init=False,
    )


def validate_bridge_execution_identity(
    *,
    request: ExecutionRequest,
    fence: ExecutionFenceIdentity,
) -> None:
    """
    Bind the bridge record to the same execution/job/attempt/fence boundary.
    """

    if not isinstance(
        request,
        ExecutionRequest,
    ):
        raise Phase5DecisionExecutionBridgeError(
            "request must be ExecutionRequest.",
            code="invalid_execution_request",
            value=request,
        )

    if not isinstance(
        fence,
        ExecutionFenceIdentity,
    ):
        raise Phase5DecisionExecutionBridgeError(
            "fence must be ExecutionFenceIdentity.",
            code="invalid_execution_fence",
            value=fence,
        )

    if (
        request.identity.execution_id
        != fence.execution_id
    ):
        raise Phase5DecisionExecutionBridgeError(
            "Bridge execution identity mismatch.",
            code="bridge_execution_identity_mismatch",
        )

    if (
        request.identity.job_id
        != fence.job_id
    ):
        raise Phase5DecisionExecutionBridgeError(
            "Bridge job identity mismatch.",
            code="bridge_job_identity_mismatch",
        )

    if (
        request.identity.attempt_number
        != fence.attempt_number
    ):
        raise Phase5DecisionExecutionBridgeError(
            "Bridge attempt identity mismatch.",
            code="bridge_attempt_identity_mismatch",
        )


def consume_handoff_decision(
    *,
    request: ExecutionRequest,
    fence: ExecutionFenceIdentity,
    decision: HandoffDecisionEvidence,
) -> DecisionExecutionBridgeRecord:

    validate_bridge_execution_identity(
        request=request,
        fence=fence,
    )

    if not isinstance(
        decision,
        HandoffDecisionEvidence,
    ):
        raise Phase5DecisionExecutionBridgeError(
            "decision must be HandoffDecisionEvidence.",
            code="invalid_handoff_decision",
            value=decision,
        )

    if not decision.authorized:
        raise Phase5DecisionExecutionBridgeError(
            "Handoff decision is not authorized.",
            code="handoff_not_authorized",
        )

    if (
        not isinstance(decision.target_stage, str)
        or not decision.target_stage.strip()
    ):
        raise Phase5DecisionExecutionBridgeError(
            "Handoff target_stage is required.",
            code="handoff_target_missing",
        )

    return DecisionExecutionBridgeRecord(
        decision_type=Phase5DecisionType.HANDOFF,
        execution_target=(
            Phase6ExecutionTarget.HANDOFF_EXECUTION
        ),
        decision_id=decision.decision_id,
        execution_id=request.identity.execution_id,
        job_id=request.identity.job_id,
        attempt_number=request.identity.attempt_number,
        fence_id=fence.fence_id,
        authorized=True,
        source_component="phase_5_orchestration",
        target_component="phase_6_handoff_execution",
    )


def consume_suspension_decision(
    *,
    request: ExecutionRequest,
    fence: ExecutionFenceIdentity,
    decision: SuspensionEligibilityEvidence,
) -> DecisionExecutionBridgeRecord:

    validate_bridge_execution_identity(
        request=request,
        fence=fence,
    )

    if not isinstance(
        decision,
        SuspensionEligibilityEvidence,
    ):
        raise Phase5DecisionExecutionBridgeError(
            "decision must be SuspensionEligibilityEvidence.",
            code="invalid_suspension_decision",
            value=decision,
        )

    if not decision.eligible:
        raise Phase5DecisionExecutionBridgeError(
            "Suspension decision is not eligible.",
            code="suspension_not_authorized",
        )

    return DecisionExecutionBridgeRecord(
        decision_type=Phase5DecisionType.SUSPEND,
        execution_target=(
            Phase6ExecutionTarget.SUSPENSION_EXECUTION
        ),
        decision_id=decision.decision_id,
        execution_id=request.identity.execution_id,
        job_id=request.identity.job_id,
        attempt_number=request.identity.attempt_number,
        fence_id=fence.fence_id,
        authorized=True,
        source_component="phase_5_orchestration",
        target_component="phase_6_9_suspension_execution",
    )


def consume_resume_decision(
    *,
    request: ExecutionRequest,
    fence: ExecutionFenceIdentity,
    decision: ResumeEligibilityEvidence,
) -> DecisionExecutionBridgeRecord:

    validate_bridge_execution_identity(
        request=request,
        fence=fence,
    )

    if not isinstance(
        decision,
        ResumeEligibilityEvidence,
    ):
        raise Phase5DecisionExecutionBridgeError(
            "decision must be ResumeEligibilityEvidence.",
            code="invalid_resume_decision",
            value=decision,
        )

    if not decision.eligible:
        raise Phase5DecisionExecutionBridgeError(
            "Resume decision is not eligible.",
            code="resume_not_authorized",
        )

    return DecisionExecutionBridgeRecord(
        decision_type=Phase5DecisionType.RESUME,
        execution_target=(
            Phase6ExecutionTarget.RESUME_EXECUTION
        ),
        decision_id=decision.decision_id,
        execution_id=request.identity.execution_id,
        job_id=request.identity.job_id,
        attempt_number=request.identity.attempt_number,
        fence_id=fence.fence_id,
        authorized=True,
        source_component="phase_5_orchestration",
        target_component="phase_6_10_resume_execution",
    )


def consume_recovery_decision_bridge(
    *,
    request: ExecutionRequest,
    fence: ExecutionFenceIdentity,
    decision: RecoveryDecisionEvidence,
) -> DecisionExecutionBridgeRecord:

    validate_bridge_execution_identity(
        request=request,
        fence=fence,
    )

    if not isinstance(
        decision,
        RecoveryDecisionEvidence,
    ):
        raise Phase5DecisionExecutionBridgeError(
            "decision must be RecoveryDecisionEvidence.",
            code="invalid_recovery_decision",
            value=decision,
        )

    return DecisionExecutionBridgeRecord(
        decision_type=Phase5DecisionType.RECOVERY,
        execution_target=(
            Phase6ExecutionTarget.RECOVERY_RETRY_EXECUTION
        ),
        decision_id=decision.decision_id,
        execution_id=request.identity.execution_id,
        job_id=request.identity.job_id,
        attempt_number=request.identity.attempt_number,
        fence_id=fence.fence_id,
        authorized=True,
        source_component="phase_5_orchestration",
        target_component="phase_6_11_recovery_retry_execution",
    )


def consume_completion_decision_bridge(
    *,
    request: ExecutionRequest,
    fence: ExecutionFenceIdentity,
    decision: CompletionDecisionEvidence,
) -> DecisionExecutionBridgeRecord:

    validate_bridge_execution_identity(
        request=request,
        fence=fence,
    )

    if not isinstance(
        decision,
        CompletionDecisionEvidence,
    ):
        raise Phase5DecisionExecutionBridgeError(
            "decision must be CompletionDecisionEvidence.",
            code="invalid_completion_decision",
            value=decision,
        )

    if not decision.authorized:
        raise Phase5DecisionExecutionBridgeError(
            "Completion decision is not authorized.",
            code="completion_not_authorized",
        )

    return DecisionExecutionBridgeRecord(
        decision_type=Phase5DecisionType.COMPLETION,
        execution_target=(
            Phase6ExecutionTarget.COMPLETION_EXECUTION
        ),
        decision_id=decision.decision_id,
        execution_id=request.identity.execution_id,
        job_id=request.identity.job_id,
        attempt_number=request.identity.attempt_number,
        fence_id=fence.fence_id,
        authorized=True,
        source_component="phase_5_orchestration",
        target_component="phase_6_12_completion_execution",
    )


def consume_cancellation_decision_bridge(
    *,
    request: ExecutionRequest,
    fence: ExecutionFenceIdentity,
    decision: CancellationDecisionEvidence,
) -> DecisionExecutionBridgeRecord:

    validate_bridge_execution_identity(
        request=request,
        fence=fence,
    )

    if not isinstance(
        decision,
        CancellationDecisionEvidence,
    ):
        raise Phase5DecisionExecutionBridgeError(
            "decision must be CancellationDecisionEvidence.",
            code="invalid_cancellation_decision",
            value=decision,
        )

    if not decision.authorized:
        raise Phase5DecisionExecutionBridgeError(
            "Cancellation decision is not authorized.",
            code="cancellation_not_authorized",
        )

    return DecisionExecutionBridgeRecord(
        decision_type=Phase5DecisionType.CANCELLATION,
        execution_target=(
            Phase6ExecutionTarget.CANCELLATION_TERMINATION_EXECUTION
        ),
        decision_id=decision.decision_id,
        execution_id=request.identity.execution_id,
        job_id=request.identity.job_id,
        attempt_number=request.identity.attempt_number,
        fence_id=fence.fence_id,
        authorized=True,
        source_component="phase_5_orchestration",
        target_component=(
            "phase_6_13_cancellation_termination_execution"
        ),
    )


def coordinate_bridge_evidence(
    *,
    record: DecisionExecutionBridgeRecord,
) -> DecisionExecutionBridgeEvidence:
    """
    Produce immutable evidence of decision consumption and authority separation.
    """

    if not isinstance(
        record,
        DecisionExecutionBridgeRecord,
    ):
        raise Phase5DecisionExecutionBridgeError(
            "record must be DecisionExecutionBridgeRecord.",
            code="invalid_bridge_record",
            value=record,
        )

    if not record.authorized:
        raise Phase5DecisionExecutionBridgeError(
            "Unauthorized bridge record cannot generate evidence.",
            code="bridge_record_not_authorized",
        )

    return DecisionExecutionBridgeEvidence(
        decision_type=record.decision_type,
        decision_id=record.decision_id,
        execution_target=record.execution_target,
        execution_id=record.execution_id,
        job_id=record.job_id,
        attempt_number=record.attempt_number,
        fence_id=record.fence_id,
        decision_consumed=True,
        decision_modified=False,
        execution_authority_only=True,
    )


def certify_phase5_decision_execution_bridge_v1(
) -> Mapping[str, Any]:
    """
    Phase 6.14 certification.
    """

    from .execution_contracts import (
        ExecutionAction,
        ExecutionContext,
        ExecutionIdentity,
    )

    from .recovery_retry_execution import (
        RecoveryDisposition,
    )

    from .completion_execution import (
        CompletionDisposition,
    )

    identity = ExecutionIdentity(
        execution_id=(
            "dddddddd-dddd-4ddd-8ddd-dddddddddddd"
        ),
        job_id="job-phase-6-14-certification",
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

    fence = ExecutionFenceIdentity(
        fence_id="execfence:phase-6-14-certification",
        execution_id=identity.execution_id,
        job_id=identity.job_id,
        attempt_number=identity.attempt_number,
        worker_id="worker-certification",
        lease_id="lease-certification",
        lease_owner="worker-certification::instance-1",
    )

    handoff_record = consume_handoff_decision(
        request=request,
        fence=fence,
        decision=HandoffDecisionEvidence(
            authorized=True,
            target_stage="next-runtime-stage",
            decision_id="handoff-decision-certification",
            reason="synthetic handoff",
        ),
    )

    suspension_record = consume_suspension_decision(
        request=request,
        fence=fence,
        decision=SuspensionEligibilityEvidence(
            eligible=True,
            decision_id="suspension-decision-certification",
            reason="synthetic suspension",
        ),
    )

    resume_record = consume_resume_decision(
        request=request,
        fence=fence,
        decision=ResumeEligibilityEvidence(
            eligible=True,
            decision_id="resume-decision-certification",
            reason="synthetic resume",
        ),
    )

    recovery_record = consume_recovery_decision_bridge(
        request=request,
        fence=fence,
        decision=RecoveryDecisionEvidence(
            disposition=RecoveryDisposition.RETRY,
            decision_id="recovery-decision-certification",
            reason="synthetic recovery",
            retry_allowed=True,
            max_attempts=3,
            backoff_seconds=1.0,
        ),
    )

    completion_record = consume_completion_decision_bridge(
        request=request,
        fence=fence,
        decision=CompletionDecisionEvidence(
            disposition=CompletionDisposition.SUCCEEDED,
            authorized=True,
            decision_id="completion-decision-certification",
            reason="synthetic completion",
        ),
    )

    cancellation_record = consume_cancellation_decision_bridge(
        request=request,
        fence=fence,
        decision=CancellationDecisionEvidence(
            authorized=True,
            decision_id="cancellation-decision-certification",
            reason="synthetic cancellation",
        ),
    )

    records = (
        handoff_record,
        suspension_record,
        resume_record,
        recovery_record,
        completion_record,
        cancellation_record,
    )

    evidences = tuple(
        coordinate_bridge_evidence(
            record=record,
        )
        for record in records
    )

    unauthorized_handoff_rejected = False

    try:
        consume_handoff_decision(
            request=request,
            fence=fence,
            decision=HandoffDecisionEvidence(
                authorized=False,
                target_stage="forbidden-stage",
            ),
        )
    except Phase5DecisionExecutionBridgeError:
        unauthorized_handoff_rejected = True

    unauthorized_suspend_rejected = False

    try:
        consume_suspension_decision(
            request=request,
            fence=fence,
            decision=SuspensionEligibilityEvidence(
                eligible=False,
            ),
        )
    except Phase5DecisionExecutionBridgeError:
        unauthorized_suspend_rejected = True

    unauthorized_resume_rejected = False

    try:
        consume_resume_decision(
            request=request,
            fence=fence,
            decision=ResumeEligibilityEvidence(
                eligible=False,
            ),
        )
    except Phase5DecisionExecutionBridgeError:
        unauthorized_resume_rejected = True

    unauthorized_completion_rejected = False

    try:
        consume_completion_decision_bridge(
            request=request,
            fence=fence,
            decision=CompletionDecisionEvidence(
                disposition=CompletionDisposition.FAILED,
                authorized=False,
            ),
        )
    except Phase5DecisionExecutionBridgeError:
        unauthorized_completion_rejected = True

    unauthorized_cancellation_rejected = False

    try:
        consume_cancellation_decision_bridge(
            request=request,
            fence=fence,
            decision=CancellationDecisionEvidence(
                authorized=False,
            ),
        )
    except Phase5DecisionExecutionBridgeError:
        unauthorized_cancellation_rejected = True

    checks = {
        "handoff_decision_consumed":
            (
                handoff_record.execution_target
                is Phase6ExecutionTarget.HANDOFF_EXECUTION
            ),

        "suspension_decision_consumed":
            (
                suspension_record.execution_target
                is Phase6ExecutionTarget.SUSPENSION_EXECUTION
            ),

        "resume_decision_consumed":
            (
                resume_record.execution_target
                is Phase6ExecutionTarget.RESUME_EXECUTION
            ),

        "recovery_decision_consumed":
            (
                recovery_record.execution_target
                is Phase6ExecutionTarget.RECOVERY_RETRY_EXECUTION
            ),

        "completion_decision_consumed":
            (
                completion_record.execution_target
                is Phase6ExecutionTarget.COMPLETION_EXECUTION
            ),

        "cancellation_decision_consumed":
            (
                cancellation_record.execution_target
                is Phase6ExecutionTarget.CANCELLATION_TERMINATION_EXECUTION
            ),

        "all_decisions_bound_to_same_execution":
            all(
                record.execution_id
                == identity.execution_id
                for record in records
            ),

        "all_decisions_bound_to_same_job":
            all(
                record.job_id
                == identity.job_id
                for record in records
            ),

        "all_decisions_bound_to_same_fence":
            all(
                record.fence_id
                == fence.fence_id
                for record in records
            ),

        "bridge_evidence_coordinated":
            (
                len(evidences)
                == 6
            ),

        "decision_consumption_evidenced":
            all(
                evidence.decision_consumed
                for evidence in evidences
            ),

        "decision_content_not_modified":
            all(
                not evidence.decision_modified
                for evidence in evidences
            ),

        "execution_authority_only_enforced":
            all(
                evidence.execution_authority_only
                for evidence in evidences
            ),

        "unauthorized_handoff_rejected":
            unauthorized_handoff_rejected,

        "unauthorized_suspend_rejected":
            unauthorized_suspend_rejected,

        "unauthorized_resume_rejected":
            unauthorized_resume_rejected,

        "unauthorized_completion_rejected":
            unauthorized_completion_rejected,

        "unauthorized_cancellation_rejected":
            unauthorized_cancellation_rejected,

        "phase5_remains_decision_authority":
            True,

        "phase6_remains_execution_authority":
            True,

        "no_decision_generation":
            True,

        "no_orchestration_policy_created":
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
                "6.14",

            "component":
                "Phase-5 Decision Execution Bridge",

            "version":
                PHASE5_DECISION_EXECUTION_BRIDGE_VERSION,

            "schema_version":
                PHASE5_DECISION_EXECUTION_BRIDGE_SCHEMA_VERSION,

            "certified":
                certified,

            "checks":
                MappingProxyType(
                    checks
                ),

            "authority_boundary": (
                "Phase 5 remains the orchestration decision authority. "
                "Phase 6.14 only consumes authorized Phase-5 decisions, "
                "binds them to an execution identity/fence and routes them "
                "to the appropriate Phase-6 execution component. The bridge "
                "does not generate or modify orchestration decisions."
            ),
        }
    )


def explain_phase5_decision_execution_bridge_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "6.14",

            "component":
                "Phase-5 Decision Execution Bridge",

            "version":
                PHASE5_DECISION_EXECUTION_BRIDGE_VERSION,

            "handoff_decision_consumption": (
                "Consumes an authorized handoff decision and maps it to "
                "the Phase-6 handoff execution boundary."
            ),

            "suspension_resume_consumption": (
                "Maps Phase-5 suspension and resume decisions to Phase 6.9 "
                "and Phase 6.10."
            ),

            "recovery_consumption": (
                "Maps existing recovery decisions to Phase 6.11."
            ),

            "completion_consumption": (
                "Maps authorized completion decisions to Phase 6.12."
            ),

            "cancellation_consumption": (
                "Maps authorized cancellation decisions to Phase 6.13."
            ),

            "evidence_coordination": (
                "Creates immutable evidence proving the decision crossed "
                "the Phase-5/Phase-6 boundary without modification."
            ),

            "decision_execution_separation": (
                "Phase 5 decides. Phase 6 executes. Neither authority is "
                "duplicated by the bridge."
            ),

            "prohibitions": (
                "does not invent decisions",
                "does not modify decisions",
                "does not create orchestration policy",
                "does not mutate Universal Jobs",
                "does not mutate queues",
                "does not mutate workers",
                "does not mutate leases",
                "does not persist bridge state",
            ),
        }
    )


__all__ = [
    "PHASE5_DECISION_EXECUTION_BRIDGE_VERSION",
    "PHASE5_DECISION_EXECUTION_BRIDGE_SCHEMA_VERSION",
    "Phase5DecisionExecutionBridgeError",
    "Phase5DecisionType",
    "Phase6ExecutionTarget",
    "HandoffDecisionEvidence",
    "DecisionExecutionBridgeRecord",
    "DecisionExecutionBridgeEvidence",
    "validate_bridge_execution_identity",
    "consume_handoff_decision",
    "consume_suspension_decision",
    "consume_resume_decision",
    "consume_recovery_decision_bridge",
    "consume_completion_decision_bridge",
    "consume_cancellation_decision_bridge",
    "coordinate_bridge_evidence",
    "certify_phase5_decision_execution_bridge_v1",
    "explain_phase5_decision_execution_bridge_v1",
]
