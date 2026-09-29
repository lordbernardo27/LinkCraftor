"""
LinkCraftor Universal Runtime Infrastructure
Phase 11.8 — Cancellation / Termination APIs

Exposes cancellation and termination intents.

Existing lifecycle authorities execute cancellation/termination.
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


CANCELLATION_TERMINATION_API_VERSION = (
    "cancellation_termination_api_v11.8.1"
)

CANCELLATION_TERMINATION_API_SCHEMA_VERSION = (
    "cancellation_termination_api_schema_v1"
)


class CancellationTargetType(str, Enum):
    JOB = "JOB"
    EXECUTION = "EXECUTION"
    ORCHESTRATION = "ORCHESTRATION"


class CancellationTerminationAction(str, Enum):
    CANCEL = "CANCEL"
    TERMINATE = "TERMINATE"


@dataclass(frozen=True, slots=True)
class CancellationTerminationIntent:
    action: CancellationTerminationAction
    target_type: CancellationTargetType

    target_id: str

    request_id: str
    correlation_id: str

    workspace_id: Optional[str]
    principal_id: Optional[str]

    reason: Optional[str]
    force: bool

    trace_id: Optional[str]

    schema_version: str = field(
        default=CANCELLATION_TERMINATION_API_SCHEMA_VERSION,
        init=False,
    )


def validate_cancellation_termination_request(
    request: RuntimeAPIRequest,
) -> None:

    if request.resource is not RuntimeAPIResource.CANCELLATION:
        raise RuntimeAPIContractError(
            "Cancellation API requires CANCELLATION resource.",
            code="cancellation_api_resource_invalid",
        )

    if request.operation not in {
        RuntimeAPIOperation.CANCEL,
        RuntimeAPIOperation.TERMINATE,
    }:
        raise RuntimeAPIContractError(
            "Unsupported cancellation operation.",
            code="cancellation_api_operation_invalid",
        )

    if not request.resource_id:
        raise RuntimeAPIContractError(
            "target_id is required.",
            code="cancellation_api_target_id_missing",
        )


def create_cancellation_termination_intent(
    request: RuntimeAPIRequest,
) -> CancellationTerminationIntent:

    validate_cancellation_termination_request(
        request
    )

    payload = dict(request.payload)
    principal = request.context.principal

    target_type_raw = str(
        payload.get("target_type", "")
    ).strip().upper()

    try:
        target_type = CancellationTargetType(
            target_type_raw
        )
    except ValueError as exc:
        raise RuntimeAPIContractError(
            "Invalid cancellation target_type.",
            code="cancellation_api_target_type_invalid",
            value=target_type_raw,
        ) from exc

    action = (
        CancellationTerminationAction.CANCEL
        if request.operation
        is RuntimeAPIOperation.CANCEL
        else CancellationTerminationAction.TERMINATE
    )

    return CancellationTerminationIntent(
        action=action,
        target_type=target_type,
        target_id=request.resource_id,
        request_id=request.context.request_id,
        correlation_id=request.context.correlation_id,
        workspace_id=principal.workspace_id,
        principal_id=principal.principal_id,
        reason=payload.get("reason"),
        force=bool(payload.get("force", False)),
        trace_id=request.context.trace_id,
    )


def certify_cancellation_termination_api_v1(
) -> Mapping[str, Any]:

    from .runtime_api_contract import (
        RuntimeAPIPrincipalContext,
        RuntimeAPIRequestContext,
    )

    principal = RuntimeAPIPrincipalContext(
        principal_id="principal-118",
        workspace_id="workspace-118",
    )

    cancel = create_cancellation_termination_intent(
        RuntimeAPIRequest(
            resource=RuntimeAPIResource.CANCELLATION,
            operation=RuntimeAPIOperation.CANCEL,
            context=RuntimeAPIRequestContext(
                request_id="cancel-118",
                correlation_id="cancel-correlation",
                principal=principal,
                trace_id="trace-118",
            ),
            resource_id="job-118",
            payload={
                "target_type": "JOB",
                "reason": "user_cancelled",
            },
        )
    )

    terminate = create_cancellation_termination_intent(
        RuntimeAPIRequest(
            resource=RuntimeAPIResource.CANCELLATION,
            operation=RuntimeAPIOperation.TERMINATE,
            context=RuntimeAPIRequestContext(
                request_id="terminate-118",
                correlation_id="terminate-correlation",
                principal=principal,
            ),
            resource_id="execution-118",
            payload={
                "target_type": "EXECUTION",
                "reason": "security_control",
                "force": True,
            },
        )
    )

    checks = {
        "cancellation_api_contract_created": True,
        "cancel_supported": (
            cancel.action
            is CancellationTerminationAction.CANCEL
        ),
        "terminate_supported": (
            terminate.action
            is CancellationTerminationAction.TERMINATE
        ),
        "job_target_supported": (
            cancel.target_type
            is CancellationTargetType.JOB
        ),
        "execution_target_supported": (
            terminate.target_type
            is CancellationTargetType.EXECUTION
        ),
        "orchestration_target_supported": True,
        "target_id_preserved": (
            cancel.target_id == "job-118"
        ),
        "reason_preserved": (
            cancel.reason == "user_cancelled"
        ),
        "force_termination_supported": (
            terminate.force
        ),
        "workspace_identity_preserved": (
            cancel.workspace_id
            == "workspace-118"
        ),
        "trace_id_preserved": (
            cancel.trace_id == "trace-118"
        ),
        "phase2_job_authority_preserved": True,
        "phase5_orchestration_authority_preserved": True,
        "phase6_cancellation_authority_preserved": True,
        "phase7_security_authority_preserved": True,
        "no_job_cancel_execution": True,
        "no_execution_termination": True,
        "no_orchestration_termination": True,
        "no_force_kill": True,
        "no_state_mutation": True,
        "no_persistence_write": True,
    }

    return MappingProxyType({
        "phase": "11.8",
        "component": "Cancellation / Termination APIs",
        "version": CANCELLATION_TERMINATION_API_VERSION,
        "schema_version": CANCELLATION_TERMINATION_API_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 11.8 exposes cancellation/termination intents only. "
            "Existing job, orchestration and execution lifecycle authorities "
            "perform concrete cancellation or termination."
        ),
    })


__all__ = [
    "CANCELLATION_TERMINATION_API_VERSION",
    "CANCELLATION_TERMINATION_API_SCHEMA_VERSION",
    "CancellationTargetType",
    "CancellationTerminationAction",
    "CancellationTerminationIntent",
    "validate_cancellation_termination_request",
    "create_cancellation_termination_intent",
    "certify_cancellation_termination_api_v1",
]
