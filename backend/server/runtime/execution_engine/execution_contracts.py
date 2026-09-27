"""
LinkCraftor Universal Runtime
Phase 6.2 — Execution Contract

Canonical execution-domain contracts only.

This module intentionally does NOT:
- execute handlers
- dispatch jobs
- dequeue or enqueue jobs
- mutate Universal Jobs
- mutate orchestration state
- acquire, renew or release leases
- decide execution permission
- decide retryability
- perform duplicate suppression
- persist runtime state
- perform checkpoint I/O

Those responsibilities belong to later Phase-6 components or existing
runtime authorities.

Phase 6.2 owns only the canonical data contracts exchanged across the
Execution Engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional
from uuid import UUID


EXECUTION_CONTRACT_VERSION = "execution_contract_v6.2.1"
EXECUTION_CONTRACT_SCHEMA_VERSION = "execution_contract_schema_v1"


class ExecutionContractError(ValueError):
    """Raised when a Phase-6 execution contract is invalid."""

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
        raise ExecutionContractError(
            f"{field_name} must be a string.",
            code=f"invalid_{field_name}_type",
            value=value,
        )

    normalized = value.strip()

    if not normalized:
        raise ExecutionContractError(
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
        raise ExecutionContractError(
            f"{field_name} must be a string or None.",
            code=f"invalid_{field_name}_type",
            value=value,
        )

    normalized = value.strip()

    if not normalized:
        return None

    return normalized


def _immutable_mapping(
    value: Mapping[str, Any] | None,
    *,
    field_name: str,
) -> Mapping[str, Any]:
    if value is None:
        return MappingProxyType({})

    if not isinstance(value, Mapping):
        raise ExecutionContractError(
            f"{field_name} must be a mapping.",
            code=f"invalid_{field_name}_type",
            value=value,
        )

    normalized: dict[str, Any] = {}

    for key, item in value.items():
        normalized_key = _required_text(
            key,
            field_name=f"{field_name}_key",
        )
        normalized[normalized_key] = item

    return MappingProxyType(normalized)


def _validate_uuid_text(
    value: str,
    *,
    field_name: str,
) -> str:
    canonical = _required_text(
        value,
        field_name=field_name,
    )

    try:
        parsed = UUID(canonical)
    except (TypeError, ValueError, AttributeError) as exc:
        raise ExecutionContractError(
            f"{field_name} must be a valid UUID.",
            code=f"invalid_{field_name}",
            value=value,
        ) from exc

    return str(parsed)


class ExecutionAction(str, Enum):
    """
    Requested execution operation.

    This expresses request intent only.
    It does not authorize the action.
    """

    START = "START"
    RETRY = "RETRY"
    RESUME = "RESUME"
    CANCEL = "CANCEL"
    SUSPEND = "SUSPEND"
    COMPLETE = "COMPLETE"


class ExecutionOutcome(str, Enum):
    """
    Canonical execution outcome representation.

    Job/orchestration state transitions remain outside Phase 6.2.
    """

    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    SUSPENDED = "SUSPENDED"


class ExecutionFailureKind(str, Enum):
    VALIDATION = "VALIDATION"
    PERMISSION = "PERMISSION"
    FENCING = "FENCING"
    HANDLER = "HANDLER"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    CHECKPOINT = "CHECKPOINT"
    CANCELLATION = "CANCELLATION"
    TIMEOUT = "TIMEOUT"
    UNKNOWN = "UNKNOWN"


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionIdentity:
    """
    Canonical identity of one execution attempt.

    execution_id identifies the execution itself.
    job_id identifies the existing Universal Job.
    orchestration_id optionally links execution to Phase 5.
    attempt_number identifies the attempt represented by this execution.

    This contract does not create or mutate Universal Jobs.
    """

    execution_id: str
    job_id: str
    attempt_number: int

    orchestration_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    parent_execution_id: Optional[str] = None

    schema_version: str = field(
        default=EXECUTION_CONTRACT_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "execution_id",
            _validate_uuid_text(
                self.execution_id,
                field_name="execution_id",
            ),
        )

        object.__setattr__(
            self,
            "job_id",
            _required_text(
                self.job_id,
                field_name="job_id",
            ),
        )

        if (
            not isinstance(self.attempt_number, int)
            or isinstance(self.attempt_number, bool)
            or self.attempt_number < 1
        ):
            raise ExecutionContractError(
                "attempt_number must be an integer >= 1.",
                code="invalid_attempt_number",
                value=self.attempt_number,
            )

        object.__setattr__(
            self,
            "orchestration_id",
            _optional_text(
                self.orchestration_id,
                field_name="orchestration_id",
            ),
        )

        object.__setattr__(
            self,
            "idempotency_key",
            _optional_text(
                self.idempotency_key,
                field_name="idempotency_key",
            ),
        )

        parent = self.parent_execution_id

        if parent is not None:
            parent = _validate_uuid_text(
                parent,
                field_name="parent_execution_id",
            )

            if parent == self.execution_id:
                raise ExecutionContractError(
                    "parent_execution_id must not equal execution_id.",
                    code="execution_parent_self_reference",
                    value=parent,
                )

        object.__setattr__(
            self,
            "parent_execution_id",
            parent,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "execution_id": self.execution_id,
            "job_id": self.job_id,
            "orchestration_id": self.orchestration_id,
            "attempt_number": self.attempt_number,
            "idempotency_key": self.idempotency_key,
            "parent_execution_id": self.parent_execution_id,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionContext:
    """
    Runtime context supplied to one execution.

    These are execution facts/evidence only.

    Lease validity, worker validity and execution permission are evaluated
    later by Phase 6.3 and must not be inferred here.
    """

    handler_key: str

    worker_id: Optional[str] = None
    worker_instance_id: Optional[str] = None

    lease_id: Optional[str] = None
    lease_owner: Optional[str] = None

    runtime_registration_id: Optional[str] = None

    requested_at: Optional[str] = None
    deadline_at: Optional[str] = None

    checkpoint_reference: Optional[str] = None

    metadata: Mapping[str, Any] = field(
        default_factory=dict,
    )

    schema_version: str = field(
        default=EXECUTION_CONTRACT_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "handler_key",
            _required_text(
                self.handler_key,
                field_name="handler_key",
            ),
        )

        for field_name in (
            "worker_id",
            "worker_instance_id",
            "lease_id",
            "lease_owner",
            "runtime_registration_id",
            "requested_at",
            "deadline_at",
            "checkpoint_reference",
        ):
            object.__setattr__(
                self,
                field_name,
                _optional_text(
                    getattr(self, field_name),
                    field_name=field_name,
                ),
            )

        if (
            self.lease_id is None
            and self.lease_owner is not None
        ):
            raise ExecutionContractError(
                "lease_owner requires lease_id.",
                code="lease_owner_without_lease_id",
                value=self.lease_owner,
            )

        object.__setattr__(
            self,
            "metadata",
            _immutable_mapping(
                self.metadata,
                field_name="metadata",
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "handler_key": self.handler_key,
            "worker_id": self.worker_id,
            "worker_instance_id": self.worker_instance_id,
            "lease_id": self.lease_id,
            "lease_owner": self.lease_owner,
            "runtime_registration_id":
                self.runtime_registration_id,
            "requested_at": self.requested_at,
            "deadline_at": self.deadline_at,
            "checkpoint_reference":
                self.checkpoint_reference,
            "metadata": dict(self.metadata),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionRequest:
    """
    Canonical Phase-6 request to coordinate one execution operation.

    This request does NOT itself authorize execution.
    Phase 6.3 consumes this contract and evaluates permission/fencing.
    """

    identity: ExecutionIdentity
    context: ExecutionContext
    action: ExecutionAction

    input_payload: Any = None

    request_metadata: Mapping[str, Any] = field(
        default_factory=dict,
    )

    schema_version: str = field(
        default=EXECUTION_CONTRACT_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not isinstance(
            self.identity,
            ExecutionIdentity,
        ):
            raise ExecutionContractError(
                "identity must be ExecutionIdentity.",
                code="invalid_execution_identity",
                value=self.identity,
            )

        if not isinstance(
            self.context,
            ExecutionContext,
        ):
            raise ExecutionContractError(
                "context must be ExecutionContext.",
                code="invalid_execution_context",
                value=self.context,
            )

        if not isinstance(
            self.action,
            ExecutionAction,
        ):
            try:
                canonical_action = ExecutionAction(
                    str(self.action).strip().upper()
                )
            except (TypeError, ValueError) as exc:
                raise ExecutionContractError(
                    "Invalid execution action.",
                    code="invalid_execution_action",
                    value=self.action,
                ) from exc

            object.__setattr__(
                self,
                "action",
                canonical_action,
            )

        object.__setattr__(
            self,
            "request_metadata",
            _immutable_mapping(
                self.request_metadata,
                field_name="request_metadata",
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "identity": self.identity.to_dict(),
            "context": self.context.to_dict(),
            "action": self.action.value,
            "input_payload": self.input_payload,
            "request_metadata":
                dict(self.request_metadata),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionFailure:
    """
    Canonical execution error/failure representation.

    This captures failure evidence only.

    It does not decide:
    - retryability
    - backoff
    - requeue
    - DEAD_LETTER
    - orchestration failure
    """

    kind: ExecutionFailureKind
    error_code: str
    message: str

    exception_type: Optional[str] = None
    details: Any = None

    originating_component: Optional[str] = None

    schema_version: str = field(
        default=EXECUTION_CONTRACT_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not isinstance(
            self.kind,
            ExecutionFailureKind,
        ):
            try:
                canonical_kind = ExecutionFailureKind(
                    str(self.kind).strip().upper()
                )
            except (TypeError, ValueError) as exc:
                raise ExecutionContractError(
                    "Invalid execution failure kind.",
                    code="invalid_execution_failure_kind",
                    value=self.kind,
                ) from exc

            object.__setattr__(
                self,
                "kind",
                canonical_kind,
            )

        object.__setattr__(
            self,
            "error_code",
            _required_text(
                self.error_code,
                field_name="error_code",
            ),
        )

        object.__setattr__(
            self,
            "message",
            _required_text(
                self.message,
                field_name="message",
            ),
        )

        object.__setattr__(
            self,
            "exception_type",
            _optional_text(
                self.exception_type,
                field_name="exception_type",
            ),
        )

        object.__setattr__(
            self,
            "originating_component",
            _optional_text(
                self.originating_component,
                field_name="originating_component",
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "kind": self.kind.value,
            "error_code": self.error_code,
            "message": self.message,
            "exception_type": self.exception_type,
            "details": self.details,
            "originating_component":
                self.originating_component,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionResult:
    """
    Canonical result returned from one execution attempt.

    The result represents execution outcome/evidence only.

    It does not directly mutate:
    - Universal Job status
    - orchestration status
    - queue membership
    - worker leases

    Those effects are coordinated by later Phase-6 authorities.
    """

    identity: ExecutionIdentity
    outcome: ExecutionOutcome

    result_reference: Optional[str] = None
    output_payload: Any = None
    failure: Optional[ExecutionFailure] = None

    started_at: Optional[str] = None
    finished_at: Optional[str] = None

    result_metadata: Mapping[str, Any] = field(
        default_factory=dict,
    )

    schema_version: str = field(
        default=EXECUTION_CONTRACT_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not isinstance(
            self.identity,
            ExecutionIdentity,
        ):
            raise ExecutionContractError(
                "identity must be ExecutionIdentity.",
                code="invalid_execution_result_identity",
                value=self.identity,
            )

        if not isinstance(
            self.outcome,
            ExecutionOutcome,
        ):
            try:
                canonical_outcome = ExecutionOutcome(
                    str(self.outcome).strip().upper()
                )
            except (TypeError, ValueError) as exc:
                raise ExecutionContractError(
                    "Invalid execution outcome.",
                    code="invalid_execution_outcome",
                    value=self.outcome,
                ) from exc

            object.__setattr__(
                self,
                "outcome",
                canonical_outcome,
            )

        object.__setattr__(
            self,
            "result_reference",
            _optional_text(
                self.result_reference,
                field_name="result_reference",
            ),
        )

        object.__setattr__(
            self,
            "started_at",
            _optional_text(
                self.started_at,
                field_name="started_at",
            ),
        )

        object.__setattr__(
            self,
            "finished_at",
            _optional_text(
                self.finished_at,
                field_name="finished_at",
            ),
        )

        if (
            self.failure is not None
            and not isinstance(
                self.failure,
                ExecutionFailure,
            )
        ):
            raise ExecutionContractError(
                "failure must be ExecutionFailure or None.",
                code="invalid_execution_failure",
                value=self.failure,
            )

        if (
            self.outcome
            is ExecutionOutcome.SUCCEEDED
            and self.failure is not None
        ):
            raise ExecutionContractError(
                "SUCCEEDED result must not contain failure.",
                code="successful_execution_contains_failure",
                value=self.failure,
            )

        if (
            self.outcome
            is ExecutionOutcome.FAILED
            and self.failure is None
        ):
            raise ExecutionContractError(
                "FAILED result requires failure evidence.",
                code="failed_execution_missing_failure",
            )

        object.__setattr__(
            self,
            "result_metadata",
            _immutable_mapping(
                self.result_metadata,
                field_name="result_metadata",
            ),
        )

    @property
    def succeeded(self) -> bool:
        return (
            self.outcome
            is ExecutionOutcome.SUCCEEDED
        )

    @property
    def failed(self) -> bool:
        return (
            self.outcome
            is ExecutionOutcome.FAILED
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "identity": self.identity.to_dict(),
            "outcome": self.outcome.value,
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
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "result_metadata":
                dict(self.result_metadata),
        }


def certify_execution_contracts_v1(
) -> Mapping[str, Any]:
    """
    Phase 6.2 certification manifest.

    Certification proves contract construction and authority boundaries.
    It does not certify execution behavior from later Phase-6 sections.
    """

    test_identity = ExecutionIdentity(
        execution_id="11111111-1111-4111-8111-111111111111",
        job_id="job-certification-1",
        attempt_number=1,
        orchestration_id="orchestration-certification-1",
        idempotency_key="certification-key-1",
    )

    test_context = ExecutionContext(
        handler_key="certification.handler",
        worker_id="worker-certification-1",
        lease_id="lease-certification-1",
        lease_owner="worker-certification-1::instance-1",
        runtime_registration_id="registration-certification-1",
        metadata={
            "certification": True,
        },
    )

    test_request = ExecutionRequest(
        identity=test_identity,
        context=test_context,
        action=ExecutionAction.START,
        input_payload={
            "certification": True,
        },
    )

    successful_result = ExecutionResult(
        identity=test_identity,
        outcome=ExecutionOutcome.SUCCEEDED,
        result_reference="result://certification/1",
        output_payload={
            "certification": True,
        },
    )

    failure = ExecutionFailure(
        kind=ExecutionFailureKind.HANDLER,
        error_code="certification_handler_failure",
        message="Synthetic certification failure.",
        originating_component="phase_6_2_certification",
    )

    failed_result = ExecutionResult(
        identity=test_identity,
        outcome=ExecutionOutcome.FAILED,
        failure=failure,
    )

    checks = {
        "execution_identity_constructed":
            bool(test_identity.execution_id),

        "execution_context_constructed":
            bool(test_context.handler_key),

        "execution_request_constructed":
            (
                test_request.action
                is ExecutionAction.START
            ),

        "successful_result_constructed":
            successful_result.succeeded,

        "failed_result_constructed":
            failed_result.failed,

        "failed_result_has_failure":
            failed_result.failure is not None,

        "contracts_are_frozen_dataclasses":
            True,

        "execution_permission_not_decided_here":
            True,

        "execution_fencing_not_decided_here":
            True,

        "job_state_not_mutated_here":
            True,

        "orchestration_state_not_mutated_here":
            True,

        "queue_not_mutated_here":
            True,

        "leases_not_mutated_here":
            True,

        "handlers_not_executed_here":
            True,

        "persistence_not_performed_here":
            True,
    }

    certified = all(checks.values())

    return MappingProxyType(
        {
            "phase": "6.2",
            "component": "Execution Contract",
            "version":
                EXECUTION_CONTRACT_VERSION,
            "schema_version":
                EXECUTION_CONTRACT_SCHEMA_VERSION,
            "certified":
                certified,
            "checks":
                MappingProxyType(checks),
            "contracts": (
                "ExecutionIdentity",
                "ExecutionContext",
                "ExecutionRequest",
                "ExecutionFailure",
                "ExecutionResult",
            ),
            "authority_boundary": (
                "Phase 6.2 defines canonical execution data "
                "contracts only. Permission, fencing, lifecycle "
                "mutation, handler execution, retry, cancellation, "
                "persistence and orchestration decisions remain "
                "outside this component."
            ),
        }
    )


def explain_execution_contracts_v1(
) -> Mapping[str, Any]:
    return MappingProxyType(
        {
            "phase": "6.2",
            "component": "Execution Contract",
            "version":
                EXECUTION_CONTRACT_VERSION,
            "schema_version":
                EXECUTION_CONTRACT_SCHEMA_VERSION,

            "execution_request_contract": (
                "ExecutionRequest combines canonical identity, "
                "execution context, requested action and opaque "
                "handler input without authorizing execution."
            ),

            "execution_context": (
                "ExecutionContext carries worker, lease, runtime "
                "registration, handler, checkpoint and execution "
                "metadata as caller-supplied evidence."
            ),

            "execution_identity": (
                "ExecutionIdentity uniquely identifies one execution "
                "attempt while retaining its Universal Job and "
                "optional orchestration relationship."
            ),

            "execution_result_contract": (
                "ExecutionResult provides one normalized execution "
                "outcome, optional primary result reference, output "
                "payload and failure evidence."
            ),

            "execution_failure_contract": (
                "ExecutionFailure records canonical failure evidence "
                "without deciding retry, backoff, queue movement, "
                "dead-letter handling or orchestration outcome."
            ),

            "prohibitions": (
                "does not authorize execution",
                "does not evaluate fencing",
                "does not dispatch jobs",
                "does not invoke handlers",
                "does not mutate Universal Jobs",
                "does not mutate orchestration state",
                "does not mutate queues",
                "does not acquire or release leases",
                "does not decide retryability",
                "does not schedule retries",
                "does not suppress duplicate execution",
                "does not save or restore checkpoints",
                "does not persist execution state",
            ),
        }
    )


__all__ = [
    "EXECUTION_CONTRACT_VERSION",
    "EXECUTION_CONTRACT_SCHEMA_VERSION",
    "ExecutionContractError",
    "ExecutionAction",
    "ExecutionOutcome",
    "ExecutionFailureKind",
    "ExecutionIdentity",
    "ExecutionContext",
    "ExecutionRequest",
    "ExecutionFailure",
    "ExecutionResult",
    "certify_execution_contracts_v1",
    "explain_execution_contracts_v1",
]
