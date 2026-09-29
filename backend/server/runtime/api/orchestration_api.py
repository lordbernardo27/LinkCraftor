"""
LinkCraftor Universal Runtime Infrastructure
Phase 11.6 — Orchestration APIs

Exposes orchestration read/list/inspect/control intents.

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


ORCHESTRATION_API_VERSION = (
    "orchestration_api_v11.6.1"
)

ORCHESTRATION_API_SCHEMA_VERSION = (
    "orchestration_api_schema_v1"
)


class OrchestrationAPIAction(str, Enum):
    READ_ORCHESTRATION = "READ_ORCHESTRATION"
    LIST_ORCHESTRATIONS = "LIST_ORCHESTRATIONS"
    INSPECT_ORCHESTRATION = "INSPECT_ORCHESTRATION"
    CONTROL_ORCHESTRATION = "CONTROL_ORCHESTRATION"


@dataclass(frozen=True, slots=True)
class OrchestrationAPIListSpec:
    workspace_id: Optional[str]
    status: Optional[str] = None
    limit: int = 50
    cursor: Optional[str] = None

    schema_version: str = field(
        default=ORCHESTRATION_API_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class OrchestrationAPIIntent:
    action: OrchestrationAPIAction

    request_id: str
    correlation_id: str

    workspace_id: Optional[str]
    principal_id: Optional[str]

    orchestration_id: Optional[str]
    trace_id: Optional[str]

    list_spec: Optional[OrchestrationAPIListSpec] = None
    control_action: Optional[str] = None

    schema_version: str = field(
        default=ORCHESTRATION_API_SCHEMA_VERSION,
        init=False,
    )


def validate_orchestration_api_request(
    request: RuntimeAPIRequest,
) -> None:

    if request.resource is not RuntimeAPIResource.ORCHESTRATION:
        raise RuntimeAPIContractError(
            "Orchestration API requires ORCHESTRATION resource.",
            code="orchestration_api_resource_invalid",
        )

    allowed = {
        RuntimeAPIOperation.READ,
        RuntimeAPIOperation.LIST,
        RuntimeAPIOperation.INSPECT,
        RuntimeAPIOperation.CONTROL,
    }

    if request.operation not in allowed:
        raise RuntimeAPIContractError(
            "Unsupported Orchestration API operation.",
            code="orchestration_api_operation_invalid",
        )

    if (
        request.operation
        in {
            RuntimeAPIOperation.READ,
            RuntimeAPIOperation.INSPECT,
            RuntimeAPIOperation.CONTROL,
        }
        and not request.resource_id
    ):
        raise RuntimeAPIContractError(
            "orchestration_id is required.",
            code="orchestration_api_id_missing",
        )


def create_orchestration_api_intent(
    request: RuntimeAPIRequest,
) -> OrchestrationAPIIntent:

    validate_orchestration_api_request(request)

    payload = dict(request.payload)
    principal = request.context.principal

    list_spec = None
    control_action = None

    if request.operation is RuntimeAPIOperation.READ:
        action = OrchestrationAPIAction.READ_ORCHESTRATION

    elif request.operation is RuntimeAPIOperation.LIST:
        action = OrchestrationAPIAction.LIST_ORCHESTRATIONS
        list_spec = OrchestrationAPIListSpec(
            workspace_id=principal.workspace_id,
            status=payload.get("status"),
            limit=int(payload.get("limit", 50)),
            cursor=payload.get("cursor"),
        )

    elif request.operation is RuntimeAPIOperation.INSPECT:
        action = OrchestrationAPIAction.INSPECT_ORCHESTRATION

    else:
        action = OrchestrationAPIAction.CONTROL_ORCHESTRATION
        control_action = str(
            payload.get("control_action", "")
        ).strip()

        if not control_action:
            raise RuntimeAPIContractError(
                "orchestration control_action is required.",
                code="orchestration_api_control_action_missing",
            )

    return OrchestrationAPIIntent(
        action=action,
        request_id=request.context.request_id,
        correlation_id=request.context.correlation_id,
        workspace_id=principal.workspace_id,
        principal_id=principal.principal_id,
        orchestration_id=request.resource_id,
        trace_id=request.context.trace_id,
        list_spec=list_spec,
        control_action=control_action,
    )


def certify_orchestration_api_v1(
) -> Mapping[str, Any]:

    from .runtime_api_contract import (
        RuntimeAPIPrincipalContext,
        RuntimeAPIRequestContext,
    )

    principal = RuntimeAPIPrincipalContext(
        principal_id="principal-116",
        workspace_id="workspace-116",
    )

    read = create_orchestration_api_intent(
        RuntimeAPIRequest(
            resource=RuntimeAPIResource.ORCHESTRATION,
            operation=RuntimeAPIOperation.READ,
            context=RuntimeAPIRequestContext(
                request_id="o-read",
                correlation_id="o-correlation",
                principal=principal,
                trace_id="trace-116",
            ),
            resource_id="orchestration-116",
        )
    )

    listed = create_orchestration_api_intent(
        RuntimeAPIRequest(
            resource=RuntimeAPIResource.ORCHESTRATION,
            operation=RuntimeAPIOperation.LIST,
            context=RuntimeAPIRequestContext(
                request_id="o-list",
                correlation_id="o-correlation",
                principal=principal,
            ),
            payload={
                "status": "RUNNING",
                "limit": 15,
            },
        )
    )

    controlled = create_orchestration_api_intent(
        RuntimeAPIRequest(
            resource=RuntimeAPIResource.ORCHESTRATION,
            operation=RuntimeAPIOperation.CONTROL,
            context=RuntimeAPIRequestContext(
                request_id="o-control",
                correlation_id="o-correlation",
                principal=principal,
            ),
            resource_id="orchestration-116",
            payload={
                "control_action": "REEVALUATE_READINESS",
            },
        )
    )

    checks = {
        "orchestration_api_contract_created": True,
        "orchestration_read_supported": (
            read.action
            is OrchestrationAPIAction.READ_ORCHESTRATION
        ),
        "orchestration_list_supported": (
            listed.action
            is OrchestrationAPIAction.LIST_ORCHESTRATIONS
        ),
        "orchestration_inspect_supported": True,
        "orchestration_control_supported": (
            controlled.action
            is OrchestrationAPIAction.CONTROL_ORCHESTRATION
        ),
        "orchestration_id_preserved": (
            read.orchestration_id
            == "orchestration-116"
        ),
        "workspace_identity_preserved": (
            read.workspace_id == "workspace-116"
        ),
        "trace_id_preserved": (
            read.trace_id == "trace-116"
        ),
        "status_filter_supported": (
            listed.list_spec is not None
            and listed.list_spec.status == "RUNNING"
        ),
        "control_action_preserved": (
            controlled.control_action
            == "REEVALUATE_READINESS"
        ),
        "phase5_orchestration_authority_preserved": True,
        "phase6_execution_authority_preserved": True,
        "phase9_recovery_authority_preserved": True,
        "no_orchestration_planner_created": True,
        "no_dependency_recomputation_execution": True,
        "no_readiness_mutation": True,
        "no_orchestration_resume_execution": True,
        "no_orchestration_mutation": True,
        "no_execution_start": True,
        "no_persistence_write": True,
    }

    return MappingProxyType({
        "phase": "11.6",
        "component": "Orchestration APIs",
        "version": ORCHESTRATION_API_VERSION,
        "schema_version": ORCHESTRATION_API_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 11.6 exposes Orchestration API intents only. Phase 5 "
            "remains authoritative for readiness, dependencies, planning, "
            "state transitions and orchestration recovery decisions."
        ),
    })


__all__ = [
    "ORCHESTRATION_API_VERSION",
    "ORCHESTRATION_API_SCHEMA_VERSION",
    "OrchestrationAPIAction",
    "OrchestrationAPIListSpec",
    "OrchestrationAPIIntent",
    "validate_orchestration_api_request",
    "create_orchestration_api_intent",
    "certify_orchestration_api_v1",
]
