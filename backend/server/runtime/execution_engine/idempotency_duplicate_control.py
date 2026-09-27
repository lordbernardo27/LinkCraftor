"""
LinkCraftor Universal Runtime
Phase 6.7 — Idempotency & Duplicate-Execution Control

Canonical execution-layer duplicate protection.

Consumes:
- Phase 6.2 ExecutionRequest identity/idempotency fields
- Phase 6.3 execution fence
- Phase 6.6 normalized result/evidence

Owns:
- canonical execution idempotency identity
- duplicate invocation evaluation
- replay safety
- duplicate result handling
- concurrent duplicate protection

Does NOT replace:
- Universal Job idempotency-key representation
- existing duplicate-detection primitives
- queue infrastructure
- worker infrastructure
- persistence
- job-state mutation

Existing lower-level primitives remain authoritative and are integrated
later under Phase 6.15.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .execution_contracts import ExecutionRequest

from .execution_permission_fencing import (
    ExecutionFenceIdentity,
)

from .execution_result_processing import (
    ExecutionEvidence,
    NormalizedExecutionResult,
)


IDEMPOTENCY_DUPLICATE_CONTROL_VERSION = (
    "idempotency_duplicate_control_v6.7.1"
)

IDEMPOTENCY_DUPLICATE_CONTROL_SCHEMA_VERSION = (
    "idempotency_duplicate_control_schema_v1"
)


class IdempotencyDuplicateControlError(ValueError):
    """Raised when Phase-6.7 duplicate control is invalid."""

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


class DuplicateInvocationDisposition(str, Enum):
    ALLOW = "ALLOW"
    REJECT_DUPLICATE = "REJECT_DUPLICATE"
    REPLAY_EXISTING = "REPLAY_EXISTING"


class DuplicateResultDisposition(str, Enum):
    ACCEPT = "ACCEPT"
    REUSE_EXISTING = "REUSE_EXISTING"
    REJECT_CONFLICT = "REJECT_CONFLICT"


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionIdempotencyIdentity:
    """
    Canonical Phase-6 idempotency identity.

    This binds execution semantics without replacing the existing
    Universal Job idempotency-key model.
    """

    identity_key: str

    job_id: str
    attempt_number: int
    execution_id: str

    source_idempotency_key: Optional[str]
    handler_key: str

    schema_version: str = field(
        default=IDEMPOTENCY_DUPLICATE_CONTROL_SCHEMA_VERSION,
        init=False,
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "identity_key": self.identity_key,
            "job_id": self.job_id,
            "attempt_number": self.attempt_number,
            "execution_id": self.execution_id,
            "source_idempotency_key":
                self.source_idempotency_key,
            "handler_key":
                self.handler_key,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class DuplicateInvocationEvidence:
    """
    Caller-supplied duplicate evidence.

    Existing duplicate-detection/persistence authorities may later
    provide this evidence during Phase 6.15 integration.
    """

    matching_execution_exists: bool = False
    matching_execution_active: bool = False
    matching_execution_terminal: bool = False

    matching_execution_id: Optional[str] = None
    matching_fence_id: Optional[str] = None

    schema_version: str = field(
        default=IDEMPOTENCY_DUPLICATE_CONTROL_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class DuplicateInvocationDecision:
    disposition: DuplicateInvocationDisposition

    identity: ExecutionIdempotencyIdentity

    existing_execution_id: Optional[str]
    existing_fence_id: Optional[str]

    replay_safe: bool
    concurrent_duplicate: bool

    schema_version: str = field(
        default=IDEMPOTENCY_DUPLICATE_CONTROL_SCHEMA_VERSION,
        init=False,
    )

    @property
    def allowed(self) -> bool:
        return (
            self.disposition
            is DuplicateInvocationDisposition.ALLOW
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "disposition": self.disposition.value,
            "identity": self.identity.to_dict(),
            "existing_execution_id":
                self.existing_execution_id,
            "existing_fence_id":
                self.existing_fence_id,
            "replay_safe":
                self.replay_safe,
            "concurrent_duplicate":
                self.concurrent_duplicate,
            "allowed":
                self.allowed,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class DuplicateResultEvidence:
    """
    Existing accepted result evidence, when any.
    """

    existing_result_present: bool = False

    existing_execution_id: Optional[str] = None
    existing_fence_id: Optional[str] = None

    existing_result_reference: Optional[str] = None
    existing_outcome: Optional[str] = None

    schema_version: str = field(
        default=IDEMPOTENCY_DUPLICATE_CONTROL_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class DuplicateResultDecision:
    disposition: DuplicateResultDisposition

    execution_id: str
    fence_id: str

    existing_result_reference: Optional[str]
    replay_safe: bool

    schema_version: str = field(
        default=IDEMPOTENCY_DUPLICATE_CONTROL_SCHEMA_VERSION,
        init=False,
    )

    @property
    def accepted(self) -> bool:
        return (
            self.disposition
            in {
                DuplicateResultDisposition.ACCEPT,
                DuplicateResultDisposition.REUSE_EXISTING,
            }
        )


def create_execution_idempotency_identity(
    *,
    request: ExecutionRequest,
) -> ExecutionIdempotencyIdentity:
    """
    Create deterministic Phase-6 execution idempotency identity.

    Preference:
    1. explicit request idempotency key
    2. deterministic request identity material
    """

    if not isinstance(request, ExecutionRequest):
        raise IdempotencyDuplicateControlError(
            "request must be ExecutionRequest.",
            code="invalid_execution_request",
            value=request,
        )

    source_key = request.identity.idempotency_key

    canonical_material = "|".join(
        (
            source_key or "",
            request.identity.job_id,
            str(request.identity.attempt_number),
            request.context.handler_key,
        )
    )

    digest = sha256(
        canonical_material.encode("utf-8")
    ).hexdigest()

    return ExecutionIdempotencyIdentity(
        identity_key=f"execidem:{digest}",
        job_id=request.identity.job_id,
        attempt_number=request.identity.attempt_number,
        execution_id=request.identity.execution_id,
        source_idempotency_key=source_key,
        handler_key=request.context.handler_key,
    )


def evaluate_duplicate_invocation(
    *,
    request: ExecutionRequest,
    fence: ExecutionFenceIdentity,
    evidence: DuplicateInvocationEvidence,
) -> DuplicateInvocationDecision:
    """
    Evaluate invocation duplication before handler execution.

    Rules:
    - no match -> ALLOW
    - active matching execution -> REJECT_DUPLICATE
    - terminal matching execution -> REPLAY_EXISTING
    """

    if not isinstance(request, ExecutionRequest):
        raise IdempotencyDuplicateControlError(
            "request must be ExecutionRequest.",
            code="invalid_execution_request",
            value=request,
        )

    if not isinstance(fence, ExecutionFenceIdentity):
        raise IdempotencyDuplicateControlError(
            "fence must be ExecutionFenceIdentity.",
            code="invalid_execution_fence",
            value=fence,
        )

    if not isinstance(
        evidence,
        DuplicateInvocationEvidence,
    ):
        raise IdempotencyDuplicateControlError(
            "evidence must be DuplicateInvocationEvidence.",
            code="invalid_duplicate_invocation_evidence",
            value=evidence,
        )

    identity = create_execution_idempotency_identity(
        request=request,
    )

    if not evidence.matching_execution_exists:
        return DuplicateInvocationDecision(
            disposition=DuplicateInvocationDisposition.ALLOW,
            identity=identity,
            existing_execution_id=None,
            existing_fence_id=None,
            replay_safe=True,
            concurrent_duplicate=False,
        )

    if evidence.matching_execution_active:
        return DuplicateInvocationDecision(
            disposition=(
                DuplicateInvocationDisposition.REJECT_DUPLICATE
            ),
            identity=identity,
            existing_execution_id=(
                evidence.matching_execution_id
            ),
            existing_fence_id=(
                evidence.matching_fence_id
            ),
            replay_safe=False,
            concurrent_duplicate=True,
        )

    if evidence.matching_execution_terminal:
        return DuplicateInvocationDecision(
            disposition=(
                DuplicateInvocationDisposition.REPLAY_EXISTING
            ),
            identity=identity,
            existing_execution_id=(
                evidence.matching_execution_id
            ),
            existing_fence_id=(
                evidence.matching_fence_id
            ),
            replay_safe=True,
            concurrent_duplicate=False,
        )

    return DuplicateInvocationDecision(
        disposition=(
            DuplicateInvocationDisposition.REJECT_DUPLICATE
        ),
        identity=identity,
        existing_execution_id=(
            evidence.matching_execution_id
        ),
        existing_fence_id=(
            evidence.matching_fence_id
        ),
        replay_safe=False,
        concurrent_duplicate=True,
    )


def validate_replay_safety(
    *,
    decision: DuplicateInvocationDecision,
    request: ExecutionRequest,
) -> bool:
    """
    Replay is safe only when a completed matching invocation exists and
    Phase 6.7 explicitly selected REPLAY_EXISTING.
    """

    if not isinstance(
        decision,
        DuplicateInvocationDecision,
    ):
        raise IdempotencyDuplicateControlError(
            "decision must be DuplicateInvocationDecision.",
            code="invalid_duplicate_invocation_decision",
            value=decision,
        )

    expected = create_execution_idempotency_identity(
        request=request,
    )

    if (
        decision.identity.identity_key
        != expected.identity_key
    ):
        return False

    return (
        decision.disposition
        is DuplicateInvocationDisposition.REPLAY_EXISTING
        and decision.replay_safe
        and decision.existing_execution_id is not None
    )


def evaluate_duplicate_result(
    *,
    normalized: NormalizedExecutionResult,
    execution_evidence: ExecutionEvidence,
    existing: DuplicateResultEvidence,
) -> DuplicateResultDecision:
    """
    Decide whether a processed result should be accepted, reused,
    or rejected as a conflicting duplicate.

    Does not persist or mutate the existing result.
    """

    if not isinstance(
        normalized,
        NormalizedExecutionResult,
    ):
        raise IdempotencyDuplicateControlError(
            "normalized must be NormalizedExecutionResult.",
            code="invalid_normalized_execution_result",
            value=normalized,
        )

    if not isinstance(
        execution_evidence,
        ExecutionEvidence,
    ):
        raise IdempotencyDuplicateControlError(
            "execution_evidence must be ExecutionEvidence.",
            code="invalid_execution_evidence",
            value=execution_evidence,
        )

    if not isinstance(
        existing,
        DuplicateResultEvidence,
    ):
        raise IdempotencyDuplicateControlError(
            "existing must be DuplicateResultEvidence.",
            code="invalid_duplicate_result_evidence",
            value=existing,
        )

    if not execution_evidence.integrity_valid:
        return DuplicateResultDecision(
            disposition=(
                DuplicateResultDisposition.REJECT_CONFLICT
            ),
            execution_id=normalized.execution_id,
            fence_id=normalized.fence_id,
            existing_result_reference=(
                existing.existing_result_reference
            ),
            replay_safe=False,
        )

    if not existing.existing_result_present:
        return DuplicateResultDecision(
            disposition=DuplicateResultDisposition.ACCEPT,
            execution_id=normalized.execution_id,
            fence_id=normalized.fence_id,
            existing_result_reference=None,
            replay_safe=True,
        )

    same_execution = (
        existing.existing_execution_id
        == normalized.execution_id
    )

    same_fence = (
        existing.existing_fence_id
        == normalized.fence_id
    )

    same_outcome = (
        existing.existing_outcome
        == normalized.outcome.value
    )

    if same_execution and same_fence and same_outcome:
        return DuplicateResultDecision(
            disposition=(
                DuplicateResultDisposition.REUSE_EXISTING
            ),
            execution_id=normalized.execution_id,
            fence_id=normalized.fence_id,
            existing_result_reference=(
                existing.existing_result_reference
            ),
            replay_safe=True,
        )

    return DuplicateResultDecision(
        disposition=(
            DuplicateResultDisposition.REJECT_CONFLICT
        ),
        execution_id=normalized.execution_id,
        fence_id=normalized.fence_id,
        existing_result_reference=(
            existing.existing_result_reference
        ),
        replay_safe=False,
    )


def concurrent_duplicate_allowed(
    decision: DuplicateInvocationDecision,
) -> bool:
    """
    Canonical concurrent duplicate gate.
    """

    if not isinstance(
        decision,
        DuplicateInvocationDecision,
    ):
        raise IdempotencyDuplicateControlError(
            "decision must be DuplicateInvocationDecision.",
            code="invalid_duplicate_invocation_decision",
            value=decision,
        )

    return (
        decision.allowed
        and not decision.concurrent_duplicate
    )


def certify_idempotency_duplicate_control_v1(
) -> Mapping[str, Any]:
    """
    Phase 6.7 certification.

    Uses synthetic in-memory evidence only.
    """

    from .execution_contracts import (
        ExecutionAction,
        ExecutionContext,
        ExecutionIdentity,
        ExecutionOutcome,
        ExecutionRequest,
    )

    from .execution_result_processing import (
        ExecutionEvidence,
        NormalizedExecutionResult,
        ResolvedJobState,
    )

    identity = ExecutionIdentity(
        execution_id=(
            "66666666-6666-4666-8666-666666666666"
        ),
        job_id="job-phase-6-7-certification",
        attempt_number=1,
        idempotency_key="idem-phase-6-7-certification",
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
        fence_id="execfence:phase-6-7-certification",
        execution_id=identity.execution_id,
        job_id=identity.job_id,
        attempt_number=identity.attempt_number,
        worker_id="worker-certification",
        lease_id="lease-certification",
        lease_owner="worker-certification::instance-1",
    )

    idem_1 = create_execution_idempotency_identity(
        request=request,
    )

    idem_2 = create_execution_idempotency_identity(
        request=request,
    )

    allow_decision = evaluate_duplicate_invocation(
        request=request,
        fence=fence,
        evidence=DuplicateInvocationEvidence(
            matching_execution_exists=False,
        ),
    )

    active_duplicate = evaluate_duplicate_invocation(
        request=request,
        fence=fence,
        evidence=DuplicateInvocationEvidence(
            matching_execution_exists=True,
            matching_execution_active=True,
            matching_execution_id="existing-active-execution",
            matching_fence_id="existing-active-fence",
        ),
    )

    terminal_duplicate = evaluate_duplicate_invocation(
        request=request,
        fence=fence,
        evidence=DuplicateInvocationEvidence(
            matching_execution_exists=True,
            matching_execution_terminal=True,
            matching_execution_id="existing-terminal-execution",
            matching_fence_id="existing-terminal-fence",
        ),
    )

    replay_safe = validate_replay_safety(
        decision=terminal_duplicate,
        request=request,
    )

    normalized = NormalizedExecutionResult(
        execution_id=identity.execution_id,
        job_id=identity.job_id,
        attempt_number=identity.attempt_number,
        fence_id=fence.fence_id,
        outcome=ExecutionOutcome.SUCCEEDED,
        resolved_job_state=ResolvedJobState.SUCCEEDED,
        result_reference="result://phase-6-7/new",
        metadata={
            "integrity_valid": True,
        },
    )

    result_evidence = ExecutionEvidence(
        execution_id=identity.execution_id,
        job_id=identity.job_id,
        attempt_number=identity.attempt_number,
        fence_id=fence.fence_id,
        outcome=ExecutionOutcome.SUCCEEDED,
        resolved_job_state=ResolvedJobState.SUCCEEDED,
        result_reference="result://phase-6-7/new",
        failure_code=None,
        integrity_valid=True,
    )

    new_result = evaluate_duplicate_result(
        normalized=normalized,
        execution_evidence=result_evidence,
        existing=DuplicateResultEvidence(
            existing_result_present=False,
        ),
    )

    same_result = evaluate_duplicate_result(
        normalized=normalized,
        execution_evidence=result_evidence,
        existing=DuplicateResultEvidence(
            existing_result_present=True,
            existing_execution_id=identity.execution_id,
            existing_fence_id=fence.fence_id,
            existing_result_reference=(
                "result://phase-6-7/existing"
            ),
            existing_outcome="SUCCEEDED",
        ),
    )

    conflicting_result = evaluate_duplicate_result(
        normalized=normalized,
        execution_evidence=result_evidence,
        existing=DuplicateResultEvidence(
            existing_result_present=True,
            existing_execution_id="different-execution",
            existing_fence_id="different-fence",
            existing_result_reference=(
                "result://phase-6-7/conflict"
            ),
            existing_outcome="FAILED",
        ),
    )

    checks = {
        "idempotency_identity_created":
            bool(idem_1.identity_key),

        "idempotency_identity_deterministic":
            (
                idem_1.identity_key
                == idem_2.identity_key
            ),

        "explicit_idempotency_key_preserved":
            (
                idem_1.source_idempotency_key
                == "idem-phase-6-7-certification"
            ),

        "new_invocation_allowed":
            allow_decision.allowed,

        "active_duplicate_detected":
            (
                active_duplicate.disposition
                is DuplicateInvocationDisposition.REJECT_DUPLICATE
            ),

        "concurrent_duplicate_blocked":
            (
                not concurrent_duplicate_allowed(
                    active_duplicate
                )
            ),

        "terminal_duplicate_replay_selected":
            (
                terminal_duplicate.disposition
                is DuplicateInvocationDisposition.REPLAY_EXISTING
            ),

        "replay_safety_passed":
            replay_safe,

        "new_result_accepted":
            (
                new_result.disposition
                is DuplicateResultDisposition.ACCEPT
            ),

        "duplicate_same_result_reused":
            (
                same_result.disposition
                is DuplicateResultDisposition.REUSE_EXISTING
            ),

        "conflicting_duplicate_result_rejected":
            (
                conflicting_result.disposition
                is DuplicateResultDisposition.REJECT_CONFLICT
            ),

        "no_idempotency_model_replacement":
            True,

        "no_duplicate_store_created":
            True,

        "no_production_job_mutation":
            True,

        "no_queue_mutation":
            True,

        "no_worker_mutation":
            True,

        "no_lease_mutation":
            True,

        "no_result_persistence":
            True,

        "no_orchestration_mutation":
            True,
    }

    certified = all(checks.values())

    return MappingProxyType(
        {
            "phase": "6.7",
            "component":
                "Idempotency & Duplicate-Execution Control",
            "version":
                IDEMPOTENCY_DUPLICATE_CONTROL_VERSION,
            "schema_version":
                IDEMPOTENCY_DUPLICATE_CONTROL_SCHEMA_VERSION,
            "certified":
                certified,
            "checks":
                MappingProxyType(checks),
            "authority_boundary": (
                "Phase 6.7 derives canonical execution idempotency "
                "identity, evaluates duplicate invocation/replay safety, "
                "handles duplicate results and blocks concurrent duplicate "
                "execution. It does not replace existing Universal Job "
                "idempotency or duplicate-detection primitives and does "
                "not persist duplicate state."
            ),
        }
    )


def explain_idempotency_duplicate_control_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase": "6.7",
            "component":
                "Idempotency & Duplicate-Execution Control",
            "version":
                IDEMPOTENCY_DUPLICATE_CONTROL_VERSION,

            "idempotency_identity": (
                "Creates a deterministic execution-layer identity from "
                "the existing request idempotency key plus job, attempt "
                "and handler identity."
            ),

            "duplicate_invocation_detection": (
                "Consumes existing duplicate evidence and distinguishes "
                "new, active duplicate and terminal duplicate invocation."
            ),

            "replay_safety": (
                "Allows replay only when an equivalent terminal execution "
                "already exists."
            ),

            "duplicate_result_handling": (
                "Accepts new results, reuses identical previously accepted "
                "results and rejects conflicting duplicate results."
            ),

            "concurrent_duplicate_protection": (
                "Rejects an invocation when equivalent execution is "
                "already active."
            ),

            "prohibitions": (
                "does not replace Universal Job idempotency model",
                "does not create duplicate persistence store",
                "does not mutate Universal Jobs",
                "does not mutate queues",
                "does not mutate workers",
                "does not mutate leases",
                "does not persist execution results",
                "does not mutate orchestration state",
            ),
        }
    )


__all__ = [
    "IDEMPOTENCY_DUPLICATE_CONTROL_VERSION",
    "IDEMPOTENCY_DUPLICATE_CONTROL_SCHEMA_VERSION",
    "IdempotencyDuplicateControlError",
    "DuplicateInvocationDisposition",
    "DuplicateResultDisposition",
    "ExecutionIdempotencyIdentity",
    "DuplicateInvocationEvidence",
    "DuplicateInvocationDecision",
    "DuplicateResultEvidence",
    "DuplicateResultDecision",
    "create_execution_idempotency_identity",
    "evaluate_duplicate_invocation",
    "validate_replay_safety",
    "evaluate_duplicate_result",
    "concurrent_duplicate_allowed",
    "certify_idempotency_duplicate_control_v1",
    "explain_idempotency_duplicate_control_v1",
]
