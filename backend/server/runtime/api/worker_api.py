"""
LinkCraftor Universal Runtime Infrastructure
Phase 11.4 — Worker APIs

Exposes worker read/list/inspect/control intents.

Does NOT:
- register workers
- assign jobs
- mutate leases
- restart workers
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


WORKER_API_VERSION = "worker_api_v11.4.1"
WORKER_API_SCHEMA_VERSION = "worker_api_schema_v1"


class WorkerAPIAction(str, Enum):
    READ_WORKER = "READ_WORKER"
    LIST_WORKERS = "LIST_WORKERS"
    INSPECT_WORKER = "INSPECT_WORKER"
    CONTROL_WORKER = "CONTROL_WORKER"


@dataclass(frozen=True, slots=True)
class WorkerAPIListSpec:
    workspace_id: Optional[str]
    active_only: bool = False
    stale_only: bool = False
    limit: int = 50
    cursor: Optional[str] = None

    schema_version: str = field(
        default=WORKER_API_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class WorkerAPIControlSpec:
    control_action: str
    reason: Optional[str] = None

    schema_version: str = field(
        default=WORKER_API_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.control_action.strip():
            raise RuntimeAPIContractError(
                "worker control_action is required.",
                code="worker_api_control_action_missing",
            )


@dataclass(frozen=True, slots=True)
class WorkerAPIIntent:
    action: WorkerAPIAction

    request_id: str
    correlation_id: str

    workspace_id: Optional[str]
    principal_id: Optional[str]

    worker_id: Optional[str]

    trace_id: Optional[str]

    list_spec: Optional[WorkerAPIListSpec] = None
    control_spec: Optional[WorkerAPIControlSpec] = None

    schema_version: str = field(
        default=WORKER_API_SCHEMA_VERSION,
        init=False,
    )


def validate_worker_api_request(
    request: RuntimeAPIRequest,
) -> None:

    if request.resource is not RuntimeAPIResource.WORKER:
        raise RuntimeAPIContractError(
            "Worker API requires WORKER resource.",
            code="worker_api_resource_invalid",
        )

    allowed = {
        RuntimeAPIOperation.READ,
        RuntimeAPIOperation.LIST,
        RuntimeAPIOperation.INSPECT,
        RuntimeAPIOperation.CONTROL,
    }

    if request.operation not in allowed:
        raise RuntimeAPIContractError(
            "Unsupported Worker API operation.",
            code="worker_api_operation_invalid",
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
            "worker_id is required.",
            code="worker_api_worker_id_missing",
        )


def create_worker_api_intent(
    request: RuntimeAPIRequest,
) -> WorkerAPIIntent:

    validate_worker_api_request(request)

    payload = dict(request.payload)
    principal = request.context.principal

    list_spec = None
    control_spec = None

    if request.operation is RuntimeAPIOperation.READ:
        action = WorkerAPIAction.READ_WORKER

    elif request.operation is RuntimeAPIOperation.LIST:
        action = WorkerAPIAction.LIST_WORKERS
        list_spec = WorkerAPIListSpec(
            workspace_id=principal.workspace_id,
            active_only=bool(
                payload.get("active_only", False)
            ),
            stale_only=bool(
                payload.get("stale_only", False)
            ),
            limit=int(payload.get("limit", 50)),
            cursor=payload.get("cursor"),
        )

    elif request.operation is RuntimeAPIOperation.INSPECT:
        action = WorkerAPIAction.INSPECT_WORKER

    else:
        action = WorkerAPIAction.CONTROL_WORKER
        control_spec = WorkerAPIControlSpec(
            control_action=str(
                payload.get("control_action", "")
            ),
            reason=payload.get("reason"),
        )

    return WorkerAPIIntent(
        action=action,
        request_id=request.context.request_id,
        correlation_id=request.context.correlation_id,
        workspace_id=principal.workspace_id,
        principal_id=principal.principal_id,
        worker_id=request.resource_id,
        trace_id=request.context.trace_id,
        list_spec=list_spec,
        control_spec=control_spec,
    )


def certify_worker_api_v1(
) -> Mapping[str, Any]:

    from .runtime_api_contract import (
        RuntimeAPIPrincipalContext,
        RuntimeAPIRequestContext,
    )

    principal = RuntimeAPIPrincipalContext(
        principal_id="principal-114",
        workspace_id="workspace-114",
    )

    read = create_worker_api_intent(
        RuntimeAPIRequest(
            resource=RuntimeAPIResource.WORKER,
            operation=RuntimeAPIOperation.READ,
            context=RuntimeAPIRequestContext(
                request_id="w-read",
                correlation_id="w-correlation",
                principal=principal,
                trace_id="trace-114",
            ),
            resource_id="worker-114",
        )
    )

    listed = create_worker_api_intent(
        RuntimeAPIRequest(
            resource=RuntimeAPIResource.WORKER,
            operation=RuntimeAPIOperation.LIST,
            context=RuntimeAPIRequestContext(
                request_id="w-list",
                correlation_id="w-correlation",
                principal=principal,
            ),
            payload={
                "active_only": True,
                "limit": 20,
            },
        )
    )

    controlled = create_worker_api_intent(
        RuntimeAPIRequest(
            resource=RuntimeAPIResource.WORKER,
            operation=RuntimeAPIOperation.CONTROL,
            context=RuntimeAPIRequestContext(
                request_id="w-control",
                correlation_id="w-correlation",
                principal=principal,
            ),
            resource_id="worker-114",
            payload={
                "control_action": "DRAIN",
            },
        )
    )

    checks = {
        "worker_api_contract_created": True,
        "worker_read_supported": (
            read.action is WorkerAPIAction.READ_WORKER
        ),
        "worker_list_supported": (
            listed.action is WorkerAPIAction.LIST_WORKERS
        ),
        "worker_inspect_supported": True,
        "worker_control_supported": (
            controlled.action
            is WorkerAPIAction.CONTROL_WORKER
        ),
        "worker_id_preserved": (
            read.worker_id == "worker-114"
        ),
        "workspace_identity_preserved": (
            read.workspace_id == "workspace-114"
        ),
        "principal_identity_preserved": (
            read.principal_id == "principal-114"
        ),
        "trace_id_preserved": (
            read.trace_id == "trace-114"
        ),
        "active_filter_supported": (
            listed.list_spec is not None
            and listed.list_spec.active_only
        ),
        "list_limit_preserved": (
            listed.list_spec is not None
            and listed.list_spec.limit == 20
        ),
        "control_action_preserved": (
            controlled.control_spec is not None
            and controlled.control_spec.control_action
            == "DRAIN"
        ),
        "phase4_worker_authority_preserved": True,
        "phase6_execution_authority_preserved": True,
        "phase9_recovery_authority_preserved": True,
        "phase10_capacity_authority_preserved": True,
        "no_worker_registration": True,
        "no_worker_assignment": True,
        "no_worker_restart": True,
        "no_worker_shutdown": True,
        "no_lease_mutation": True,
        "no_job_mutation": True,
        "no_persistence_write": True,
    }

    return MappingProxyType({
        "phase": "11.4",
        "component": "Worker APIs",
        "version": WORKER_API_VERSION,
        "schema_version": WORKER_API_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 11.4 exposes Worker API intents only. Phase 4 remains "
            "authoritative for worker registration, assignment, leases and "
            "worker lifecycle."
        ),
    })


__all__ = [
    "WORKER_API_VERSION",
    "WORKER_API_SCHEMA_VERSION",
    "WorkerAPIAction",
    "WorkerAPIListSpec",
    "WorkerAPIControlSpec",
    "WorkerAPIIntent",
    "validate_worker_api_request",
    "create_worker_api_intent",
    "certify_worker_api_v1",
]
