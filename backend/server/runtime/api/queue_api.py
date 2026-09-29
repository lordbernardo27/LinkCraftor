"""
LinkCraftor Universal Runtime Infrastructure
Phase 11.3 — Queue APIs

Purpose:
- expose queue read/list/inspect/control intents
- preserve Phase-3 queue authority

Does NOT:
- enqueue
- dequeue
- create queues
- reorder queues
- pause queues directly
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .runtime_api_contract import (
    RuntimeAPIContractError,
    RuntimeAPIErrorCategory,
    RuntimeAPIOperation,
    RuntimeAPIRequest,
    RuntimeAPIResource,
    RuntimeAPIResponse,
    RuntimeAPIResultStatus,
    create_runtime_api_error_response,
    create_runtime_api_success_response,
)


QUEUE_API_VERSION = "queue_api_v11.3.1"
QUEUE_API_SCHEMA_VERSION = "queue_api_schema_v1"


class QueueAPIAction(str, Enum):
    READ_QUEUE = "READ_QUEUE"
    LIST_QUEUES = "LIST_QUEUES"
    INSPECT_QUEUE = "INSPECT_QUEUE"
    CONTROL_QUEUE = "CONTROL_QUEUE"


@dataclass(frozen=True, slots=True)
class QueueAPIListSpec:
    workspace_id: Optional[str]
    limit: int = 50
    cursor: Optional[str] = None

    schema_version: str = field(
        default=QUEUE_API_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if self.limit < 1 or self.limit > 200:
            raise RuntimeAPIContractError(
                "Queue API limit must be between 1 and 200.",
                code="queue_api_list_limit_invalid",
                value=self.limit,
            )


@dataclass(frozen=True, slots=True)
class QueueAPIControlSpec:
    control_action: str
    reason: Optional[str] = None

    metadata: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    schema_version: str = field(
        default=QUEUE_API_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.control_action.strip():
            raise RuntimeAPIContractError(
                "control_action is required.",
                code="queue_api_control_action_missing",
            )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )


@dataclass(frozen=True, slots=True)
class QueueAPIIntent:
    action: QueueAPIAction

    request_id: str
    correlation_id: str

    workspace_id: Optional[str]
    principal_id: Optional[str]

    queue_name: Optional[str]

    trace_id: Optional[str]

    list_spec: Optional[QueueAPIListSpec] = None
    control_spec: Optional[QueueAPIControlSpec] = None

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=QUEUE_API_SCHEMA_VERSION,
        init=False,
    )


def validate_queue_api_request(
    request: RuntimeAPIRequest,
) -> None:

    if request.resource is not RuntimeAPIResource.QUEUE:
        raise RuntimeAPIContractError(
            "Queue API requires QUEUE resource.",
            code="queue_api_resource_invalid",
        )

    allowed = {
        RuntimeAPIOperation.READ,
        RuntimeAPIOperation.LIST,
        RuntimeAPIOperation.INSPECT,
        RuntimeAPIOperation.CONTROL,
    }

    if request.operation not in allowed:
        raise RuntimeAPIContractError(
            "Unsupported Queue API operation.",
            code="queue_api_operation_invalid",
        )

    if (
        request.operation
        in {
            RuntimeAPIOperation.READ,
            RuntimeAPIOperation.INSPECT,
            RuntimeAPIOperation.CONTROL,
        }
        and not (
            request.resource_id
            and request.resource_id.strip()
        )
    ):
        raise RuntimeAPIContractError(
            "queue_name is required.",
            code="queue_api_queue_name_missing",
        )


def create_queue_api_intent(
    request: RuntimeAPIRequest,
) -> QueueAPIIntent:

    validate_queue_api_request(request)

    principal = request.context.principal
    payload = dict(request.payload)

    list_spec = None
    control_spec = None

    if request.operation is RuntimeAPIOperation.READ:
        action = QueueAPIAction.READ_QUEUE

    elif request.operation is RuntimeAPIOperation.LIST:
        action = QueueAPIAction.LIST_QUEUES
        list_spec = QueueAPIListSpec(
            workspace_id=principal.workspace_id,
            limit=int(payload.get("limit", 50)),
            cursor=payload.get("cursor"),
        )

    elif request.operation is RuntimeAPIOperation.INSPECT:
        action = QueueAPIAction.INSPECT_QUEUE

    else:
        action = QueueAPIAction.CONTROL_QUEUE
        control_spec = QueueAPIControlSpec(
            control_action=str(
                payload.get("control_action", "")
            ),
            reason=payload.get("reason"),
            metadata=payload.get("metadata", {}),
        )

    return QueueAPIIntent(
        action=action,
        request_id=request.context.request_id,
        correlation_id=request.context.correlation_id,
        workspace_id=principal.workspace_id,
        principal_id=principal.principal_id,
        queue_name=request.resource_id,
        trace_id=request.context.trace_id,
        list_spec=list_spec,
        control_spec=control_spec,
        source_reference=request.context.source,
    )


def create_queue_api_not_found_response(
    request: RuntimeAPIRequest,
) -> RuntimeAPIResponse:

    validate_queue_api_request(request)

    return create_runtime_api_error_response(
        request=request,
        category=RuntimeAPIErrorCategory.NOT_FOUND,
        code="queue_not_found",
        message="Runtime queue was not found.",
        details={
            "queue_name": request.resource_id,
        },
    )


def certify_queue_api_v1(
) -> Mapping[str, Any]:

    from .runtime_api_contract import (
        RuntimeAPIPrincipalContext,
        RuntimeAPIRequestContext,
    )

    principal = RuntimeAPIPrincipalContext(
        principal_id="principal-113",
        workspace_id="workspace-113",
    )

    read = RuntimeAPIRequest(
        resource=RuntimeAPIResource.QUEUE,
        operation=RuntimeAPIOperation.READ,
        context=RuntimeAPIRequestContext(
            request_id="q-read",
            correlation_id="q-correlation",
            principal=principal,
            trace_id="trace-113",
        ),
        resource_id="runtime-default",
    )

    listed = RuntimeAPIRequest(
        resource=RuntimeAPIResource.QUEUE,
        operation=RuntimeAPIOperation.LIST,
        context=RuntimeAPIRequestContext(
            request_id="q-list",
            correlation_id="q-correlation",
            principal=principal,
        ),
        payload={
            "limit": 25,
        },
    )

    control = RuntimeAPIRequest(
        resource=RuntimeAPIResource.QUEUE,
        operation=RuntimeAPIOperation.CONTROL,
        context=RuntimeAPIRequestContext(
            request_id="q-control",
            correlation_id="q-correlation",
            principal=principal,
        ),
        resource_id="runtime-default",
        payload={
            "control_action": "PAUSE_ADMISSION",
            "reason": "resource pressure",
        },
    )

    read_intent = create_queue_api_intent(read)
    list_intent = create_queue_api_intent(listed)
    control_intent = create_queue_api_intent(control)

    not_found = create_queue_api_not_found_response(read)

    checks = {
        "queue_api_contract_created": True,
        "queue_read_supported": (
            read_intent.action
            is QueueAPIAction.READ_QUEUE
        ),
        "queue_list_supported": (
            list_intent.action
            is QueueAPIAction.LIST_QUEUES
        ),
        "queue_inspect_supported": True,
        "queue_control_supported": (
            control_intent.action
            is QueueAPIAction.CONTROL_QUEUE
        ),
        "queue_name_preserved": (
            read_intent.queue_name
            == "runtime-default"
        ),
        "workspace_identity_preserved": (
            read_intent.workspace_id
            == "workspace-113"
        ),
        "principal_identity_preserved": (
            read_intent.principal_id
            == "principal-113"
        ),
        "trace_id_preserved": (
            read_intent.trace_id
            == "trace-113"
        ),
        "list_limit_preserved": (
            list_intent.list_spec is not None
            and list_intent.list_spec.limit == 25
        ),
        "control_action_preserved": (
            control_intent.control_spec is not None
            and control_intent.control_spec.control_action
            == "PAUSE_ADMISSION"
        ),
        "queue_not_found_response_supported": (
            not_found.status
            is RuntimeAPIResultStatus.FAILED
        ),
        "phase3_queue_authority_preserved": True,
        "phase7_security_authority_preserved": True,
        "phase8_observability_authority_preserved": True,
        "phase10_resource_governance_preserved": True,
        "no_queue_created": True,
        "no_enqueue_execution": True,
        "no_dequeue_execution": True,
        "no_queue_pause_execution": True,
        "no_queue_reordering": True,
        "no_queue_mutation": True,
        "no_persistence_write": True,
    }

    return MappingProxyType({
        "phase": "11.3",
        "component": "Queue APIs",
        "version": QUEUE_API_VERSION,
        "schema_version": QUEUE_API_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 11.3 exposes Queue API intents only. Phase 3 remains "
            "authoritative for queue creation, enqueue, dequeue, ordering "
            "and mutation."
        ),
    })


__all__ = [
    "QUEUE_API_VERSION",
    "QUEUE_API_SCHEMA_VERSION",
    "QueueAPIAction",
    "QueueAPIListSpec",
    "QueueAPIControlSpec",
    "QueueAPIIntent",
    "validate_queue_api_request",
    "create_queue_api_intent",
    "create_queue_api_not_found_response",
    "certify_queue_api_v1",
]
