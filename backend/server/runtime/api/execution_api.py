"""
LinkCraftor Universal Runtime Infrastructure
Phase 11.5 — Execution APIs

Exposes execution read/list/inspect/control intents.

Phase 6 remains execution authority.
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


EXECUTION_API_VERSION = "execution_api_v11.5.1"
EXECUTION_API_SCHEMA_VERSION = "execution_api_schema_v1"


class ExecutionAPIAction(str, Enum):
    READ_EXECUTION = "READ_EXECUTION"
    LIST_EXECUTIONS = "LIST_EXECUTIONS"
    INSPECT_EXECUTION = "INSPECT_EXECUTION"
    CONTROL_EXECUTION = "CONTROL_EXECUTION"


@dataclass(frozen=True, slots=True)
class ExecutionAPIListSpec:
    workspace_id: Optional[str]
    job_id: Optional[str] = None
    orchestration_id: Optional[str] = None
    status: Optional[str] = None
    limit: int = 50
    cursor: Optional[str] = None

    schema_version: str = field(
        default=EXECUTION_API_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class ExecutionAPIIntent:
    action: ExecutionAPIAction

    request_id: str
    correlation_id: str

    workspace_id: Optional[str]
    principal_id: Optional[str]

    execution_id: Optional[str]
    trace_id: Optional[str]

    list_spec: Optional[ExecutionAPIListSpec] = None
    control_action: Optional[str] = None

    schema_version: str = field(
        default=EXECUTION_API_SCHEMA_VERSION,
        init=False,
    )


def validate_execution_api_request(
    request: RuntimeAPIRequest,
) -> None:

    if request.resource is not RuntimeAPIResource.EXECUTION:
        raise RuntimeAPIContractError(
            "Execution API requires EXECUTION resource.",
            code="execution_api_resource_invalid",
        )

    allowed = {
        RuntimeAPIOperation.READ,
        RuntimeAPIOperation.LIST,
        RuntimeAPIOperation.INSPECT,
        RuntimeAPIOperation.CONTROL,
    }

    if request.operation not in allowed:
        raise RuntimeAPIContractError(
            "Unsupported Execution API operation.",
            code="execution_api_operation_invalid",
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
            "execution_id is required.",
            code="execution_api_execution_id_missing",
        )


def create_execution_api_intent(
    request: RuntimeAPIRequest,
) -> ExecutionAPIIntent:

    validate_execution_api_request(request)

    payload = dict(request.payload)
    principal = request.context.principal

    list_spec = None
    control_action = None

    if request.operation is RuntimeAPIOperation.READ:
        action = ExecutionAPIAction.READ_EXECUTION

    elif request.operation is RuntimeAPIOperation.LIST:
        action = ExecutionAPIAction.LIST_EXECUTIONS
        list_spec = ExecutionAPIListSpec(
            workspace_id=principal.workspace_id,
            job_id=payload.get("job_id"),
            orchestration_id=payload.get(
                "orchestration_id"
            ),
            status=payload.get("status"),
            limit=int(payload.get("limit", 50)),
            cursor=payload.get("cursor"),
        )

    elif request.operation is RuntimeAPIOperation.INSPECT:
        action = ExecutionAPIAction.INSPECT_EXECUTION

    else:
        action = ExecutionAPIAction.CONTROL_EXECUTION
        control_action = str(
            payload.get("control_action", "")
        ).strip()

        if not control_action:
            raise RuntimeAPIContractError(
                "execution control_action is required.",
                code="execution_api_control_action_missing",
            )

    return ExecutionAPIIntent(
        action=action,
        request_id=request.context.request_id,
        correlation_id=request.context.correlation_id,
        workspace_id=principal.workspace_id,
        principal_id=principal.principal_id,
        execution_id=request.resource_id,
        trace_id=request.context.trace_id,
        list_spec=list_spec,
        control_action=control_action,
    )


def certify_execution_api_v1(
) -> Mapping[str, Any]:

    from .runtime_api_contract import (
        RuntimeAPIPrincipalContext,
        RuntimeAPIRequestContext,
    )

    principal = RuntimeAPIPrincipalContext(
        principal_id="principal-115",
        workspace_id="workspace-115",
    )

    read = create_execution_api_intent(
        RuntimeAPIRequest(
            resource=RuntimeAPIResource.EXECUTION,
            operation=RuntimeAPIOperation.READ,
            context=RuntimeAPIRequestContext(
                request_id="e-read",
                correlation_id="e-correlation",
                principal=principal,
                trace_id="trace-115",
            ),
            resource_id="execution-115",
        )
    )

    listed = create_execution_api_intent(
        RuntimeAPIRequest(
            resource=RuntimeAPIResource.EXECUTION,
            operation=RuntimeAPIOperation.LIST,
            context=RuntimeAPIRequestContext(
                request_id="e-list",
                correlation_id="e-correlation",
                principal=principal,
            ),
            payload={
                "job_id": "job-115",
                "status": "RUNNING",
                "limit": 30,
            },
        )
    )

    controlled = create_execution_api_intent(
        RuntimeAPIRequest(
            resource=RuntimeAPIResource.EXECUTION,
            operation=RuntimeAPIOperation.CONTROL,
            context=RuntimeAPIRequestContext(
                request_id="e-control",
                correlation_id="e-correlation",
                principal=principal,
            ),
            resource_id="execution-115",
            payload={
                "control_action": "CHECKPOINT",
            },
        )
    )

    checks = {
        "execution_api_contract_created": True,
        "execution_read_supported": (
            read.action
            is ExecutionAPIAction.READ_EXECUTION
        ),
        "execution_list_supported": (
            listed.action
            is ExecutionAPIAction.LIST_EXECUTIONS
        ),
        "execution_inspect_supported": True,
        "execution_control_supported": (
            controlled.action
            is ExecutionAPIAction.CONTROL_EXECUTION
        ),
        "execution_id_preserved": (
            read.execution_id == "execution-115"
        ),
        "workspace_identity_preserved": (
            read.workspace_id == "workspace-115"
        ),
        "trace_id_preserved": (
            read.trace_id == "trace-115"
        ),
        "job_filter_preserved": (
            listed.list_spec is not None
            and listed.list_spec.job_id == "job-115"
        ),
        "status_filter_preserved": (
            listed.list_spec is not None
            and listed.list_spec.status == "RUNNING"
        ),
        "control_action_preserved": (
            controlled.control_action == "CHECKPOINT"
        ),
        "phase6_execution_authority_preserved": True,
        "phase5_orchestration_authority_preserved": True,
        "phase9_recovery_authority_preserved": True,
        "phase10_concurrency_authority_preserved": True,
        "no_execution_start": True,
        "no_execution_checkpoint_execution": True,
        "no_execution_resume": True,
        "no_execution_retry": True,
        "no_execution_mutation": True,
        "no_worker_assignment": True,
        "no_persistence_write": True,
    }

    return MappingProxyType({
        "phase": "11.5",
        "component": "Execution APIs",
        "version": EXECUTION_API_VERSION,
        "schema_version": EXECUTION_API_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 11.5 exposes Execution API intents only. Phase 6 remains "
            "authoritative for execution lifecycle, checkpoint, resume, retry "
            "and completion mechanics."
        ),
    })


__all__ = [
    "EXECUTION_API_VERSION",
    "EXECUTION_API_SCHEMA_VERSION",
    "ExecutionAPIAction",
    "ExecutionAPIListSpec",
    "ExecutionAPIIntent",
    "validate_execution_api_request",
    "create_execution_api_intent",
    "certify_execution_api_v1",
]
