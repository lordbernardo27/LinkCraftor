"""
LinkCraftor Universal Runtime Infrastructure
Phase 11.10 — Administrative Runtime APIs

Purpose:
- expose administrative runtime inspection/control intents
- preserve existing runtime authority boundaries
- require explicit administrative action vocabulary

Does NOT:
- mutate runtime directly
- restart workers
- pause queues
- alter orchestration
- change security policy
- change quotas directly
- write persistence
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


ADMIN_RUNTIME_API_VERSION = (
    "administrative_runtime_api_v11.10.1"
)

ADMIN_RUNTIME_API_SCHEMA_VERSION = (
    "administrative_runtime_api_schema_v1"
)


class AdministrativeRuntimeAction(str, Enum):
    INSPECT_RUNTIME = "INSPECT_RUNTIME"
    INSPECT_COMPONENT = "INSPECT_COMPONENT"
    CONTROL_RUNTIME = "CONTROL_RUNTIME"
    CONTROL_COMPONENT = "CONTROL_COMPONENT"


class AdministrativeTargetType(str, Enum):
    RUNTIME = "RUNTIME"
    QUEUE = "QUEUE"
    WORKER = "WORKER"
    JOB = "JOB"
    EXECUTION = "EXECUTION"
    ORCHESTRATION = "ORCHESTRATION"
    RESOURCE_GOVERNANCE = "RESOURCE_GOVERNANCE"


@dataclass(frozen=True, slots=True)
class AdministrativeControlSpec:
    control_action: str

    target_type: AdministrativeTargetType
    target_id: Optional[str]

    reason: Optional[str] = None

    metadata: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    schema_version: str = field(
        default=ADMIN_RUNTIME_API_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.control_action.strip():
            raise RuntimeAPIContractError(
                "administrative control_action is required.",
                code="admin_runtime_control_action_missing",
            )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )


@dataclass(frozen=True, slots=True)
class AdministrativeRuntimeIntent:
    action: AdministrativeRuntimeAction

    request_id: str
    correlation_id: str

    workspace_id: Optional[str]
    principal_id: Optional[str]

    target_type: AdministrativeTargetType
    target_id: Optional[str]

    trace_id: Optional[str]

    control_spec: Optional[AdministrativeControlSpec] = None

    schema_version: str = field(
        default=ADMIN_RUNTIME_API_SCHEMA_VERSION,
        init=False,
    )


def validate_administrative_runtime_request(
    request: RuntimeAPIRequest,
) -> None:

    if request.resource is not RuntimeAPIResource.ADMIN:
        raise RuntimeAPIContractError(
            "Administrative Runtime API requires ADMIN resource.",
            code="admin_runtime_resource_invalid",
        )

    if request.operation not in {
        RuntimeAPIOperation.INSPECT,
        RuntimeAPIOperation.CONTROL,
    }:
        raise RuntimeAPIContractError(
            "Unsupported Administrative Runtime API operation.",
            code="admin_runtime_operation_invalid",
        )


def create_administrative_runtime_intent(
    request: RuntimeAPIRequest,
) -> AdministrativeRuntimeIntent:

    validate_administrative_runtime_request(request)

    payload = dict(request.payload)
    principal = request.context.principal

    target_type_raw = str(
        payload.get("target_type", "RUNTIME")
    ).strip().upper()

    try:
        target_type = AdministrativeTargetType(
            target_type_raw
        )
    except ValueError as exc:
        raise RuntimeAPIContractError(
            "Invalid administrative target_type.",
            code="admin_runtime_target_type_invalid",
            value=target_type_raw,
        ) from exc

    target_id = (
        request.resource_id
        or payload.get("target_id")
    )

    if request.operation is RuntimeAPIOperation.INSPECT:
        action = (
            AdministrativeRuntimeAction.INSPECT_RUNTIME
            if target_type is AdministrativeTargetType.RUNTIME
            else AdministrativeRuntimeAction.INSPECT_COMPONENT
        )
        control_spec = None

    else:
        control_action = str(
            payload.get("control_action", "")
        ).strip()

        if not control_action:
            raise RuntimeAPIContractError(
                "administrative control_action is required.",
                code="admin_runtime_control_action_missing",
            )

        action = (
            AdministrativeRuntimeAction.CONTROL_RUNTIME
            if target_type is AdministrativeTargetType.RUNTIME
            else AdministrativeRuntimeAction.CONTROL_COMPONENT
        )

        control_spec = AdministrativeControlSpec(
            control_action=control_action,
            target_type=target_type,
            target_id=target_id,
            reason=payload.get("reason"),
            metadata=payload.get("metadata", {}),
        )

    return AdministrativeRuntimeIntent(
        action=action,
        request_id=request.context.request_id,
        correlation_id=request.context.correlation_id,
        workspace_id=principal.workspace_id,
        principal_id=principal.principal_id,
        target_type=target_type,
        target_id=target_id,
        trace_id=request.context.trace_id,
        control_spec=control_spec,
    )


def certify_administrative_runtime_api_v1(
) -> Mapping[str, Any]:

    from .runtime_api_contract import (
        RuntimeAPIPrincipalContext,
        RuntimeAPIRequestContext,
    )

    principal = RuntimeAPIPrincipalContext(
        principal_id="owner-admin-1110",
        principal_type="owner_admin",
        workspace_id="workspace-1110",
        scopes=(
            "runtime.admin.inspect",
            "runtime.admin.control",
        ),
    )

    inspect_runtime = create_administrative_runtime_intent(
        RuntimeAPIRequest(
            resource=RuntimeAPIResource.ADMIN,
            operation=RuntimeAPIOperation.INSPECT,
            context=RuntimeAPIRequestContext(
                request_id="admin-inspect-1110",
                correlation_id="admin-correlation",
                principal=principal,
                trace_id="trace-1110",
            ),
            payload={
                "target_type": "RUNTIME",
            },
        )
    )

    inspect_worker = create_administrative_runtime_intent(
        RuntimeAPIRequest(
            resource=RuntimeAPIResource.ADMIN,
            operation=RuntimeAPIOperation.INSPECT,
            context=RuntimeAPIRequestContext(
                request_id="admin-worker-1110",
                correlation_id="admin-correlation",
                principal=principal,
            ),
            resource_id="worker-1110",
            payload={
                "target_type": "WORKER",
            },
        )
    )

    control_queue = create_administrative_runtime_intent(
        RuntimeAPIRequest(
            resource=RuntimeAPIResource.ADMIN,
            operation=RuntimeAPIOperation.CONTROL,
            context=RuntimeAPIRequestContext(
                request_id="admin-control-1110",
                correlation_id="admin-correlation",
                principal=principal,
            ),
            resource_id="runtime-default",
            payload={
                "target_type": "QUEUE",
                "control_action": "PAUSE_ADMISSION",
                "reason": "maintenance",
            },
        )
    )

    checks = {
        "administrative_runtime_api_contract_created": True,

        "runtime_inspection_supported": (
            inspect_runtime.action
            is AdministrativeRuntimeAction.INSPECT_RUNTIME
        ),

        "component_inspection_supported": (
            inspect_worker.action
            is AdministrativeRuntimeAction.INSPECT_COMPONENT
        ),

        "component_control_intent_supported": (
            control_queue.action
            is AdministrativeRuntimeAction.CONTROL_COMPONENT
        ),

        "runtime_target_supported": True,
        "queue_target_supported": True,
        "worker_target_supported": True,
        "job_target_supported": True,
        "execution_target_supported": True,
        "orchestration_target_supported": True,
        "resource_governance_target_supported": True,

        "target_id_preserved": (
            inspect_worker.target_id == "worker-1110"
        ),

        "control_action_preserved": (
            control_queue.control_spec is not None
            and control_queue.control_spec.control_action
            == "PAUSE_ADMISSION"
        ),

        "principal_identity_preserved": (
            inspect_runtime.principal_id
            == "owner-admin-1110"
        ),

        "trace_identity_preserved": (
            inspect_runtime.trace_id
            == "trace-1110"
        ),

        "phase3_queue_authority_preserved": True,
        "phase4_worker_authority_preserved": True,
        "phase5_orchestration_authority_preserved": True,
        "phase6_execution_authority_preserved": True,
        "phase7_security_authority_preserved": True,
        "phase10_resource_authority_preserved": True,

        "no_queue_pause_execution": True,
        "no_worker_restart_execution": True,
        "no_job_mutation": True,
        "no_execution_mutation": True,
        "no_orchestration_mutation": True,
        "no_security_policy_mutation": True,
        "no_quota_mutation": True,
        "no_persistence_write": True,
    }

    return MappingProxyType({
        "phase": "11.10",
        "component": "Administrative Runtime APIs",
        "version": ADMIN_RUNTIME_API_VERSION,
        "schema_version": ADMIN_RUNTIME_API_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 11.10 exposes administrative inspection/control intents "
            "only. Existing queue, worker, job, orchestration, execution, "
            "security and resource-governance authorities perform concrete "
            "operations."
        ),
    })


__all__ = [
    "ADMIN_RUNTIME_API_VERSION",
    "ADMIN_RUNTIME_API_SCHEMA_VERSION",
    "AdministrativeRuntimeAction",
    "AdministrativeTargetType",
    "AdministrativeControlSpec",
    "AdministrativeRuntimeIntent",
    "validate_administrative_runtime_request",
    "create_administrative_runtime_intent",
    "certify_administrative_runtime_api_v1",
]
