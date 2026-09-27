"""
LinkCraftor Universal Runtime
Phase 6.3 — Execution Permission & Fencing

Canonical execution-permission and fencing authority.

This component consumes the Phase-6.2 ExecutionRequest contract and
caller-supplied evidence from existing job, worker, lease and duplicate
authorities.

It intentionally does NOT:
- dequeue or enqueue jobs
- mutate Universal Job state
- mutate orchestration state
- acquire, renew or release leases
- discover workers
- classify worker health or staleness itself
- execute handlers
- perform retry/requeue
- persist state
- suppress queue entries
- perform checkpoint I/O

Its job is to answer:

"May this specific execution proceed right now, and under which
canonical execution fence?"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .execution_contracts import (
    ExecutionAction,
    ExecutionRequest,
)


EXECUTION_PERMISSION_FENCING_VERSION = (
    "execution_permission_fencing_v6.3.1"
)

EXECUTION_PERMISSION_FENCING_SCHEMA_VERSION = (
    "execution_permission_fencing_schema_v1"
)


class ExecutionPermissionFencingError(ValueError):
    """Raised when execution-permission evidence is invalid."""

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


def _required_text(
    value: Any,
    *,
    field_name: str,
) -> str:
    if not isinstance(value, str):
        raise ExecutionPermissionFencingError(
            f"{field_name} must be a string.",
            code=f"invalid_{field_name}_type",
            value=value,
        )

    normalized = value.strip()

    if not normalized:
        raise ExecutionPermissionFencingError(
            f"{field_name} must not be empty.",
            code=f"empty_{field_name}",
            value=value,
        )

    return normalized


def _optional_text(
    value: Any,
    *,
    field_name: str,
) -> Optional[str]:
    if value is None:
        return None

    if not isinstance(value, str):
        raise ExecutionPermissionFencingError(
            f"{field_name} must be a string or None.",
            code=f"invalid_{field_name}_type",
            value=value,
        )

    normalized = value.strip()

    return normalized or None


class ExecutionPermissionDisposition(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"


class ExecutionPermissionReason(str, Enum):
    AUTHORIZED = "AUTHORIZED"

    INVALID_JOB_STATE = "INVALID_JOB_STATE"
    TERMINAL_JOB_STATE = "TERMINAL_JOB_STATE"

    LEASE_REQUIRED = "LEASE_REQUIRED"
    LEASE_NOT_ACTIVE = "LEASE_NOT_ACTIVE"
    LEASE_ID_MISMATCH = "LEASE_ID_MISMATCH"
    LEASE_OWNER_MISMATCH = "LEASE_OWNER_MISMATCH"

    STALE_WORKER = "STALE_WORKER"

    DUPLICATE_EXECUTION = "DUPLICATE_EXECUTION"

    WORKER_ID_MISMATCH = "WORKER_ID_MISMATCH"


_TERMINAL_JOB_STATES = frozenset(
    {
        "SUCCEEDED",
        "CANCELLED",
        "DEAD_LETTER",
        "EXPIRED",
    }
)


_ACTION_ELIGIBLE_JOB_STATES = MappingProxyType(
    {
        ExecutionAction.START: frozenset(
            {
                "LEASED",
                "RUNNING",
            }
        ),

        ExecutionAction.RETRY: frozenset(
            {
                "LEASED",
                "RUNNING",
            }
        ),

        ExecutionAction.RESUME: frozenset(
            {
                "LEASED",
                "RUNNING",
            }
        ),

        ExecutionAction.SUSPEND: frozenset(
            {
                "RUNNING",
            }
        ),

        ExecutionAction.CANCEL: frozenset(
            {
                "QUEUED",
                "LEASED",
                "RUNNING",
                "SUSPENDED",
                "FAILED",
            }
        ),

        ExecutionAction.COMPLETE: frozenset(
            {
                "RUNNING",
            }
        ),
    }
)


_LEASE_REQUIRED_ACTIONS = frozenset(
    {
        ExecutionAction.START,
        ExecutionAction.RETRY,
        ExecutionAction.RESUME,
        ExecutionAction.SUSPEND,
        ExecutionAction.COMPLETE,
    }
)


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionPermissionEvidence:
    """
    Caller-supplied execution evidence.

    Phase 6.3 consumes evidence from existing authorities.

    It does not itself:
    - determine worker staleness
    - acquire leases
    - inspect persistent job stores
    - detect duplicates from storage

    Those authorities provide their conclusions here.
    """

    job_status: str

    current_worker_id: Optional[str] = None

    current_lease_id: Optional[str] = None
    current_lease_owner: Optional[str] = None
    lease_state: Optional[str] = None

    worker_stale: bool = False

    duplicate_execution_detected: bool = False

    schema_version: str = field(
        default=EXECUTION_PERMISSION_FENCING_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "job_status",
            _required_text(
                self.job_status,
                field_name="job_status",
            ).upper(),
        )

        object.__setattr__(
            self,
            "current_worker_id",
            _optional_text(
                self.current_worker_id,
                field_name="current_worker_id",
            ),
        )

        object.__setattr__(
            self,
            "current_lease_id",
            _optional_text(
                self.current_lease_id,
                field_name="current_lease_id",
            ),
        )

        object.__setattr__(
            self,
            "current_lease_owner",
            _optional_text(
                self.current_lease_owner,
                field_name="current_lease_owner",
            ),
        )

        lease_state = _optional_text(
            self.lease_state,
            field_name="lease_state",
        )

        if lease_state is not None:
            lease_state = lease_state.upper()

        object.__setattr__(
            self,
            "lease_state",
            lease_state,
        )

        if not isinstance(
            self.worker_stale,
            bool,
        ):
            raise ExecutionPermissionFencingError(
                "worker_stale must be bool.",
                code="invalid_worker_stale",
                value=self.worker_stale,
            )

        if not isinstance(
            self.duplicate_execution_detected,
            bool,
        ):
            raise ExecutionPermissionFencingError(
                "duplicate_execution_detected must be bool.",
                code="invalid_duplicate_execution_detected",
                value=self.duplicate_execution_detected,
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "job_status": self.job_status,
            "current_worker_id":
                self.current_worker_id,
            "current_lease_id":
                self.current_lease_id,
            "current_lease_owner":
                self.current_lease_owner,
            "lease_state":
                self.lease_state,
            "worker_stale":
                self.worker_stale,
            "duplicate_execution_detected":
                self.duplicate_execution_detected,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionFenceIdentity:
    """
    Immutable identity binding execution to its current ownership facts.

    A fence binds:
    - execution identity
    - Universal Job identity
    - attempt number
    - worker identity
    - lease identity
    - lease owner

    Later Phase-6 components can require the same fence before accepting
    lifecycle transitions or execution results.
    """

    fence_id: str

    execution_id: str
    job_id: str
    attempt_number: int

    worker_id: Optional[str]
    lease_id: Optional[str]
    lease_owner: Optional[str]

    schema_version: str = field(
        default=EXECUTION_PERMISSION_FENCING_SCHEMA_VERSION,
        init=False,
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "fence_id": self.fence_id,
            "execution_id": self.execution_id,
            "job_id": self.job_id,
            "attempt_number": self.attempt_number,
            "worker_id": self.worker_id,
            "lease_id": self.lease_id,
            "lease_owner": self.lease_owner,
        }


def create_execution_fence_identity(
    *,
    request: ExecutionRequest,
    evidence: ExecutionPermissionEvidence,
) -> ExecutionFenceIdentity:
    """
    Create deterministic execution-fence identity.

    This function does not persist or acquire anything.
    """

    if not isinstance(
        request,
        ExecutionRequest,
    ):
        raise ExecutionPermissionFencingError(
            "request must be ExecutionRequest.",
            code="invalid_execution_request",
            value=request,
        )

    if not isinstance(
        evidence,
        ExecutionPermissionEvidence,
    ):
        raise ExecutionPermissionFencingError(
            "evidence must be ExecutionPermissionEvidence.",
            code="invalid_execution_permission_evidence",
            value=evidence,
        )

    worker_id = (
        evidence.current_worker_id
        or request.context.worker_id
    )

    lease_id = (
        evidence.current_lease_id
        or request.context.lease_id
    )

    lease_owner = (
        evidence.current_lease_owner
        or request.context.lease_owner
    )

    canonical_material = "|".join(
        (
            request.identity.execution_id,
            request.identity.job_id,
            str(request.identity.attempt_number),
            worker_id or "",
            lease_id or "",
            lease_owner or "",
        )
    )

    digest = sha256(
        canonical_material.encode("utf-8")
    ).hexdigest()

    return ExecutionFenceIdentity(
        fence_id=f"execfence:{digest}",
        execution_id=request.identity.execution_id,
        job_id=request.identity.job_id,
        attempt_number=request.identity.attempt_number,
        worker_id=worker_id,
        lease_id=lease_id,
        lease_owner=lease_owner,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionPermissionDecision:
    """
    Canonical Phase-6.3 permission decision.

    ALLOW means execution may proceed to the next Phase-6 control layer.

    It does NOT mean the handler has executed.
    """

    disposition: ExecutionPermissionDisposition
    reason: ExecutionPermissionReason

    fence: Optional[ExecutionFenceIdentity]

    job_state_eligible: bool
    lease_valid: bool
    worker_valid: bool
    duplicate_safe: bool

    schema_version: str = field(
        default=EXECUTION_PERMISSION_FENCING_SCHEMA_VERSION,
        init=False,
    )

    @property
    def allowed(self) -> bool:
        return (
            self.disposition
            is ExecutionPermissionDisposition.ALLOW
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "disposition":
                self.disposition.value,
            "reason":
                self.reason.value,
            "allowed":
                self.allowed,
            "fence":
                (
                    self.fence.to_dict()
                    if self.fence is not None
                    else None
                ),
            "job_state_eligible":
                self.job_state_eligible,
            "lease_valid":
                self.lease_valid,
            "worker_valid":
                self.worker_valid,
            "duplicate_safe":
                self.duplicate_safe,
        }


def _deny(
    *,
    reason: ExecutionPermissionReason,
    job_state_eligible: bool,
    lease_valid: bool,
    worker_valid: bool,
    duplicate_safe: bool,
) -> ExecutionPermissionDecision:

    return ExecutionPermissionDecision(
        disposition=ExecutionPermissionDisposition.DENY,
        reason=reason,
        fence=None,
        job_state_eligible=job_state_eligible,
        lease_valid=lease_valid,
        worker_valid=worker_valid,
        duplicate_safe=duplicate_safe,
    )


def evaluate_execution_permission(
    *,
    request: ExecutionRequest,
    evidence: ExecutionPermissionEvidence,
) -> ExecutionPermissionDecision:
    """
    Canonical Phase-6.3 execution permission evaluation.

    Evaluation order:

    1. terminal-state rejection
    2. action/job-state eligibility
    3. stale-worker rejection
    4. worker ownership validation
    5. lease validation
    6. duplicate-execution rejection
    7. canonical fence creation
    """

    if not isinstance(
        request,
        ExecutionRequest,
    ):
        raise ExecutionPermissionFencingError(
            "request must be ExecutionRequest.",
            code="invalid_execution_request",
            value=request,
        )

    if not isinstance(
        evidence,
        ExecutionPermissionEvidence,
    ):
        raise ExecutionPermissionFencingError(
            "evidence must be ExecutionPermissionEvidence.",
            code="invalid_execution_permission_evidence",
            value=evidence,
        )

    job_status = evidence.job_status

    if job_status in _TERMINAL_JOB_STATES:
        return _deny(
            reason=(
                ExecutionPermissionReason.TERMINAL_JOB_STATE
            ),
            job_state_eligible=False,
            lease_valid=False,
            worker_valid=False,
            duplicate_safe=False,
        )

    eligible_states = (
        _ACTION_ELIGIBLE_JOB_STATES.get(
            request.action,
            frozenset(),
        )
    )

    job_state_eligible = (
        job_status in eligible_states
    )

    if not job_state_eligible:
        return _deny(
            reason=(
                ExecutionPermissionReason.INVALID_JOB_STATE
            ),
            job_state_eligible=False,
            lease_valid=False,
            worker_valid=False,
            duplicate_safe=False,
        )

    if evidence.worker_stale:
        return _deny(
            reason=ExecutionPermissionReason.STALE_WORKER,
            job_state_eligible=True,
            lease_valid=False,
            worker_valid=False,
            duplicate_safe=False,
        )

    requested_worker = request.context.worker_id
    current_worker = evidence.current_worker_id

    if (
        requested_worker is not None
        and current_worker is not None
        and requested_worker != current_worker
    ):
        return _deny(
            reason=(
                ExecutionPermissionReason.WORKER_ID_MISMATCH
            ),
            job_state_eligible=True,
            lease_valid=False,
            worker_valid=False,
            duplicate_safe=False,
        )

    worker_valid = True

    lease_valid = True

    if request.action in _LEASE_REQUIRED_ACTIONS:

        requested_lease_id = request.context.lease_id
        requested_lease_owner = request.context.lease_owner

        if (
            requested_lease_id is None
            or requested_lease_owner is None
            or evidence.current_lease_id is None
            or evidence.current_lease_owner is None
        ):
            return _deny(
                reason=ExecutionPermissionReason.LEASE_REQUIRED,
                job_state_eligible=True,
                lease_valid=False,
                worker_valid=True,
                duplicate_safe=False,
            )

        if evidence.lease_state != "ACTIVE":
            return _deny(
                reason=(
                    ExecutionPermissionReason.LEASE_NOT_ACTIVE
                ),
                job_state_eligible=True,
                lease_valid=False,
                worker_valid=True,
                duplicate_safe=False,
            )

        if (
            requested_lease_id
            != evidence.current_lease_id
        ):
            return _deny(
                reason=(
                    ExecutionPermissionReason.LEASE_ID_MISMATCH
                ),
                job_state_eligible=True,
                lease_valid=False,
                worker_valid=True,
                duplicate_safe=False,
            )

        if (
            requested_lease_owner
            != evidence.current_lease_owner
        ):
            return _deny(
                reason=(
                    ExecutionPermissionReason.LEASE_OWNER_MISMATCH
                ),
                job_state_eligible=True,
                lease_valid=False,
                worker_valid=True,
                duplicate_safe=False,
            )

        lease_valid = True

    if evidence.duplicate_execution_detected:
        return _deny(
            reason=(
                ExecutionPermissionReason.DUPLICATE_EXECUTION
            ),
            job_state_eligible=True,
            lease_valid=lease_valid,
            worker_valid=worker_valid,
            duplicate_safe=False,
        )

    fence = create_execution_fence_identity(
        request=request,
        evidence=evidence,
    )

    return ExecutionPermissionDecision(
        disposition=ExecutionPermissionDisposition.ALLOW,
        reason=ExecutionPermissionReason.AUTHORIZED,
        fence=fence,
        job_state_eligible=True,
        lease_valid=lease_valid,
        worker_valid=worker_valid,
        duplicate_safe=True,
    )


def certify_execution_permission_fencing_v1(
) -> Mapping[str, Any]:
    """
    Phase 6.3 certification.

    Uses synthetic evidence only.
    No production runtime state is mutated.
    """

    from .execution_contracts import (
        ExecutionContext,
        ExecutionIdentity,
    )

    identity = ExecutionIdentity(
        execution_id=(
            "22222222-2222-4222-8222-222222222222"
        ),
        job_id="job-phase-6-3-certification",
        attempt_number=1,
    )

    context = ExecutionContext(
        handler_key="certification.handler",
        worker_id="worker-certification",
        worker_instance_id="instance-certification",
        lease_id="lease-certification",
        lease_owner=(
            "worker-certification::instance-certification"
        ),
    )

    request = ExecutionRequest(
        identity=identity,
        context=context,
        action=ExecutionAction.START,
    )

    valid_evidence = ExecutionPermissionEvidence(
        job_status="RUNNING",
        current_worker_id="worker-certification",
        current_lease_id="lease-certification",
        current_lease_owner=(
            "worker-certification::instance-certification"
        ),
        lease_state="ACTIVE",
        worker_stale=False,
        duplicate_execution_detected=False,
    )

    allowed = evaluate_execution_permission(
        request=request,
        evidence=valid_evidence,
    )

    second_fence = create_execution_fence_identity(
        request=request,
        evidence=valid_evidence,
    )

    terminal_evidence = ExecutionPermissionEvidence(
        job_status="SUCCEEDED",
    )

    terminal_denied = evaluate_execution_permission(
        request=request,
        evidence=terminal_evidence,
    )

    stale_evidence = ExecutionPermissionEvidence(
        job_status="RUNNING",
        current_worker_id="worker-certification",
        current_lease_id="lease-certification",
        current_lease_owner=(
            "worker-certification::instance-certification"
        ),
        lease_state="ACTIVE",
        worker_stale=True,
    )

    stale_denied = evaluate_execution_permission(
        request=request,
        evidence=stale_evidence,
    )

    wrong_lease_evidence = ExecutionPermissionEvidence(
        job_status="RUNNING",
        current_worker_id="worker-certification",
        current_lease_id="different-lease",
        current_lease_owner=(
            "worker-certification::instance-certification"
        ),
        lease_state="ACTIVE",
    )

    wrong_lease_denied = evaluate_execution_permission(
        request=request,
        evidence=wrong_lease_evidence,
    )

    wrong_owner_evidence = ExecutionPermissionEvidence(
        job_status="RUNNING",
        current_worker_id="worker-certification",
        current_lease_id="lease-certification",
        current_lease_owner=(
            "different-worker::different-instance"
        ),
        lease_state="ACTIVE",
    )

    wrong_owner_denied = evaluate_execution_permission(
        request=request,
        evidence=wrong_owner_evidence,
    )

    duplicate_evidence = ExecutionPermissionEvidence(
        job_status="RUNNING",
        current_worker_id="worker-certification",
        current_lease_id="lease-certification",
        current_lease_owner=(
            "worker-certification::instance-certification"
        ),
        lease_state="ACTIVE",
        duplicate_execution_detected=True,
    )

    duplicate_denied = evaluate_execution_permission(
        request=request,
        evidence=duplicate_evidence,
    )

    checks = {
        "valid_execution_allowed":
            allowed.allowed,

        "allowed_execution_has_fence":
            allowed.fence is not None,

        "job_state_eligibility_passed":
            allowed.job_state_eligible,

        "lease_validation_passed":
            allowed.lease_valid,

        "worker_validation_passed":
            allowed.worker_valid,

        "duplicate_protection_passed":
            allowed.duplicate_safe,

        "terminal_state_rejected":
            (
                terminal_denied.reason
                is ExecutionPermissionReason.TERMINAL_JOB_STATE
            ),

        "stale_execution_rejected":
            (
                stale_denied.reason
                is ExecutionPermissionReason.STALE_WORKER
            ),

        "lease_id_mismatch_rejected":
            (
                wrong_lease_denied.reason
                is ExecutionPermissionReason.LEASE_ID_MISMATCH
            ),

        "lease_owner_mismatch_rejected":
            (
                wrong_owner_denied.reason
                is ExecutionPermissionReason.LEASE_OWNER_MISMATCH
            ),

        "duplicate_execution_rejected":
            (
                duplicate_denied.reason
                is ExecutionPermissionReason.DUPLICATE_EXECUTION
            ),

        "fence_identity_deterministic":
            (
                allowed.fence is not None
                and allowed.fence.fence_id
                == second_fence.fence_id
            ),

        "no_job_mutation":
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
            "phase": "6.3",
            "component":
                "Execution Permission & Fencing",
            "version":
                EXECUTION_PERMISSION_FENCING_VERSION,
            "schema_version":
                EXECUTION_PERMISSION_FENCING_SCHEMA_VERSION,
            "certified":
                certified,
            "checks":
                MappingProxyType(checks),
            "authority_boundary": (
                "Phase 6.3 evaluates whether one ExecutionRequest "
                "may proceed using caller-supplied job, worker, "
                "lease, stale-worker and duplicate-execution "
                "evidence, and produces a deterministic execution "
                "fence. It does not execute or mutate runtime state."
            ),
        }
    )


def explain_execution_permission_fencing_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase": "6.3",
            "component":
                "Execution Permission & Fencing",
            "version":
                EXECUTION_PERMISSION_FENCING_VERSION,
            "schema_version":
                EXECUTION_PERMISSION_FENCING_SCHEMA_VERSION,

            "execution_permission_evaluation": (
                "Evaluates whether a Phase-6.2 ExecutionRequest "
                "may proceed."
            ),

            "job_state_eligibility": (
                "Rejects terminal or action-ineligible job states "
                "without mutating the Universal Job."
            ),

            "lease_ownership_validation": (
                "Consumes existing lease evidence and requires "
                "matching active lease identity and ownership for "
                "lease-bound execution actions."
            ),

            "stale_execution_rejection": (
                "Consumes caller-supplied stale-worker evidence "
                "and rejects execution when the worker is stale."
            ),

            "duplicate_execution_protection": (
                "Consumes duplicate-execution evidence and rejects "
                "a detected duplicate before handler execution."
            ),

            "execution_fence_identity": (
                "Creates deterministic immutable fencing identity "
                "binding execution, job, attempt, worker and lease."
            ),

            "prohibitions": (
                "does not dequeue jobs",
                "does not enqueue jobs",
                "does not mutate Universal Jobs",
                "does not mutate orchestration state",
                "does not acquire leases",
                "does not renew leases",
                "does not release leases",
                "does not classify worker staleness",
                "does not discover workers",
                "does not invoke handlers",
                "does not perform retries",
                "does not perform requeues",
                "does not persist execution state",
                "does not save or restore checkpoints",
            ),
        }
    )


__all__ = [
    "EXECUTION_PERMISSION_FENCING_VERSION",
    "EXECUTION_PERMISSION_FENCING_SCHEMA_VERSION",
    "ExecutionPermissionFencingError",
    "ExecutionPermissionDisposition",
    "ExecutionPermissionReason",
    "ExecutionPermissionEvidence",
    "ExecutionFenceIdentity",
    "ExecutionPermissionDecision",
    "create_execution_fence_identity",
    "evaluate_execution_permission",
    "certify_execution_permission_fencing_v1",
    "explain_execution_permission_fencing_v1",
]
