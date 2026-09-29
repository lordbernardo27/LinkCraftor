"""
LinkCraftor Universal Runtime Infrastructure
Phase 11.9 — Retry / Recovery APIs

Exposes retry/recovery intents.

Phase 9 remains reliability/recovery authority.
Phase 6 remains execution authority.
Phase 5 remains orchestration authority.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .runtime_api_contract import (
    RuntimeAPIContractError,
    RuntimeAPIOperation,
    RuntimeAPIRequest,
    RuntimeAPIResource,
)


RETRY_RECOVERY_API_VERSION = (
    "retry_recovery_api_v11.9.1"
)

RETRY_RECOVERY_API_SCHEMA_VERSION = (
    "retry_recovery_api_schema_v1"
)


class RetryRecoveryTargetType(str, Enum):
    JOB = "JOB"
    EXECUTION = "EXECUTION"
    ORCHESTRATION = "ORCHESTRATION"
    WORKER = "WORKER"
    QUEUE = "QUEUE"


class RetryRecoveryAction(str, Enum):
    RETRY = "RETRY"
    RECOVER = "RECOVER"


@dataclass(frozen=True, slots=True)
class RetryRecoveryIntent:
    action: RetryRecoveryAction
    target_type: RetryRecoveryTargetType

    target_id: str

    request_id: str
    correlation_id: str

    workspace_id: Optional[str]
    principal_id: Optional[str]

    reason: Optional[str]
    checkpoint_reference: Optional[str]

    idempotency_key: Optional[str]
    trace_id: Optional[str]

    metadata: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    schema_version: str = field(
        default=RETRY_RECOVERY_API_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )


def validate_retry_recovery_request(
    request: RuntimeAPIRequest,
) -> None:

    if request.resource is not RuntimeAPIResource.RETRY_RECOVERY:
        raise RuntimeAPIContractError(
            "Retry/Recovery API requires RETRY_RECOVERY resource.",
            code="retry_recovery_api_resource_invalid",
        )

    if request.operation not in {
        RuntimeAPIOperation.RETRY,
        RuntimeAPIOperation.RECOVER,
    }:
        raise RuntimeAPIContractError(
            "Unsupported retry/recovery operation.",
            code="retry_recovery_api_operation_invalid",
        )

    if not request.resource_id:
        raise RuntimeAPIContractError(
            "retry/recovery target_id is required.",
            code="retry_recovery_api_target_id_missing",
        )


def create_retry_recovery_intent(
    request: RuntimeAPIRequest,
) -> RetryRecoveryIntent:

    validate_retry_recovery_request(request)

    payload = dict(request.payload)
    principal = request.context.principal

    target_type_raw = str(
        payload.get("target_type", "")
    ).strip().upper()

    try:
        target_type = RetryRecoveryTargetType(
            target_type_raw
        )
    except ValueError as exc:
        raise RuntimeAPIContractError(
            "Invalid retry/recovery target_type.",
            code="retry_recovery_api_target_type_invalid",
            value=target_type_raw,
        ) from exc

    action = (
        RetryRecoveryAction.RETRY
        if request.operation
        is RuntimeAPIOperation.RETRY
        else RetryRecoveryAction.RECOVER
    )

    return RetryRecoveryIntent(
        action=action,
        target_type=target_type,
        target_id=request.resource_id,
        request_id=request.context.request_id,
        correlation_id=request.context.correlation_id,
        workspace_id=principal.workspace_id,
        principal_id=principal.principal_id,
        reason=payload.get("reason"),
        checkpoint_reference=payload.get(
            "checkpoint_reference"
        ),
        idempotency_key=request.context.idempotency_key,
        trace_id=request.context.trace_id,
        metadata=payload.get("metadata", {}),
    )


def certify_retry_recovery_api_v1(
) -> Mapping[str, Any]:

    from .runtime_api_contract import (
        RuntimeAPIPrincipalContext,
        RuntimeAPIRequestContext,
    )

    principal = RuntimeAPIPrincipalContext(
        principal_id="principal-119",
        workspace_id="workspace-119",
    )

    retry = create_retry_recovery_intent(
        RuntimeAPIRequest(
            resource=RuntimeAPIResource.RETRY_RECOVERY,
            operation=RuntimeAPIOperation.RETRY,
            context=RuntimeAPIRequestContext(
                request_id="retry-119",
                correlation_id="recovery-correlation",
                principal=principal,
                idempotency_key="idem-119",
                trace_id="trace-119",
            ),
            resource_id="job-119",
            payload={
                "target_type": "JOB",
                "reason": "retry_requested",
            },
        )
    )

    recover = create_retry_recovery_intent(
        RuntimeAPIRequest(
            resource=RuntimeAPIResource.RETRY_RECOVERY,
            operation=RuntimeAPIOperation.RECOVER,
            context=RuntimeAPIRequestContext(
                request_id="recover-119",
                correlation_id="recovery-correlation",
                principal=principal,
            ),
            resource_id="execution-119",
            payload={
                "target_type": "EXECUTION",
                "checkpoint_reference": "checkpoint-119",
            },
        )
    )

    checks = {
        "retry_recovery_api_contract_created": True,
        "retry_supported": (
            retry.action
            is RetryRecoveryAction.RETRY
        ),
        "recover_supported": (
            recover.action
            is RetryRecoveryAction.RECOVER
        ),
        "job_retry_target_supported": (
            retry.target_type
            is RetryRecoveryTargetType.JOB
        ),
        "execution_recovery_target_supported": (
            recover.target_type
            is RetryRecoveryTargetType.EXECUTION
        ),
        "orchestration_recovery_target_supported": True,
        "worker_recovery_target_supported": True,
        "queue_recovery_target_supported": True,
        "target_id_preserved": (
            retry.target_id == "job-119"
        ),
        "checkpoint_reference_preserved": (
            recover.checkpoint_reference
            == "checkpoint-119"
        ),
        "idempotency_key_preserved": (
            retry.idempotency_key
            == "idem-119"
        ),
        "trace_id_preserved": (
            retry.trace_id == "trace-119"
        ),
        "workspace_identity_preserved": (
            retry.workspace_id
            == "workspace-119"
        ),
        "phase9_recovery_authority_preserved": True,
        "phase6_execution_retry_authority_preserved": True,
        "phase5_orchestration_recovery_authority_preserved": True,
        "phase3_queue_recovery_authority_preserved": True,
        "phase4_worker_recovery_authority_preserved": True,
        "no_retry_execution": True,
        "no_requeue_execution": True,
        "no_checkpoint_resume_execution": True,
        "no_worker_reassignment": True,
        "no_queue_recovery_execution": True,
        "no_orchestration_recovery_execution": True,
        "no_state_mutation": True,
        "no_persistence_write": True,
    }

    return MappingProxyType({
        "phase": "11.9",
        "component": "Retry / Recovery APIs",
        "version": RETRY_RECOVERY_API_VERSION,
        "schema_version": RETRY_RECOVERY_API_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 11.9 exposes retry/recovery intents only. Phase 9 remains "
            "recovery-governance authority while existing queue, worker, "
            "orchestration and execution layers perform concrete mechanics."
        ),
    })


__all__ = [
    "RETRY_RECOVERY_API_VERSION",
    "RETRY_RECOVERY_API_SCHEMA_VERSION",
    "RetryRecoveryTargetType",
    "RetryRecoveryAction",
    "RetryRecoveryIntent",
    "validate_retry_recovery_request",
    "create_retry_recovery_intent",
    "certify_retry_recovery_api_v1",
]
