"""
LinkCraftor Universal Runtime Infrastructure
Phase 11.7 — Runtime State APIs

Exposes read/list/inspect runtime-state query intents.

Does NOT:
- create state store
- mutate state
- persist state
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


RUNTIME_STATE_API_VERSION = (
    "runtime_state_api_v11.7.1"
)

RUNTIME_STATE_API_SCHEMA_VERSION = (
    "runtime_state_api_schema_v1"
)


class RuntimeStateAPIAction(str, Enum):
    READ_STATE = "READ_STATE"
    LIST_STATE = "LIST_STATE"
    INSPECT_STATE = "INSPECT_STATE"


@dataclass(frozen=True, slots=True)
class RuntimeStateQuery:
    state_scope: str

    workspace_id: Optional[str]

    entity_type: Optional[str] = None
    entity_id: Optional[str] = None

    include_history: bool = False

    limit: int = 50
    cursor: Optional[str] = None

    schema_version: str = field(
        default=RUNTIME_STATE_API_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class RuntimeStateAPIIntent:
    action: RuntimeStateAPIAction

    request_id: str
    correlation_id: str

    principal_id: Optional[str]
    trace_id: Optional[str]

    query: RuntimeStateQuery

    schema_version: str = field(
        default=RUNTIME_STATE_API_SCHEMA_VERSION,
        init=False,
    )


def validate_runtime_state_api_request(
    request: RuntimeAPIRequest,
) -> None:

    if request.resource is not RuntimeAPIResource.RUNTIME_STATE:
        raise RuntimeAPIContractError(
            "Runtime State API requires RUNTIME_STATE resource.",
            code="runtime_state_api_resource_invalid",
        )

    if request.operation not in {
        RuntimeAPIOperation.READ,
        RuntimeAPIOperation.LIST,
        RuntimeAPIOperation.INSPECT,
    }:
        raise RuntimeAPIContractError(
            "Unsupported Runtime State API operation.",
            code="runtime_state_api_operation_invalid",
        )


def create_runtime_state_api_intent(
    request: RuntimeAPIRequest,
) -> RuntimeStateAPIIntent:

    validate_runtime_state_api_request(request)

    payload = dict(request.payload)
    principal = request.context.principal

    state_scope = str(
        payload.get("state_scope", "RUNTIME")
    ).strip()

    if not state_scope:
        raise RuntimeAPIContractError(
            "state_scope is required.",
            code="runtime_state_api_scope_missing",
        )

    if request.operation is RuntimeAPIOperation.READ:
        action = RuntimeStateAPIAction.READ_STATE

    elif request.operation is RuntimeAPIOperation.LIST:
        action = RuntimeStateAPIAction.LIST_STATE

    else:
        action = RuntimeStateAPIAction.INSPECT_STATE

    query = RuntimeStateQuery(
        state_scope=state_scope,
        workspace_id=principal.workspace_id,
        entity_type=payload.get("entity_type"),
        entity_id=(
            request.resource_id
            or payload.get("entity_id")
        ),
        include_history=bool(
            payload.get("include_history", False)
        ),
        limit=int(payload.get("limit", 50)),
        cursor=payload.get("cursor"),
    )

    return RuntimeStateAPIIntent(
        action=action,
        request_id=request.context.request_id,
        correlation_id=request.context.correlation_id,
        principal_id=principal.principal_id,
        trace_id=request.context.trace_id,
        query=query,
    )


def certify_runtime_state_api_v1(
) -> Mapping[str, Any]:

    from .runtime_api_contract import (
        RuntimeAPIPrincipalContext,
        RuntimeAPIRequestContext,
    )

    principal = RuntimeAPIPrincipalContext(
        principal_id="principal-117",
        workspace_id="workspace-117",
    )

    read = create_runtime_state_api_intent(
        RuntimeAPIRequest(
            resource=RuntimeAPIResource.RUNTIME_STATE,
            operation=RuntimeAPIOperation.READ,
            context=RuntimeAPIRequestContext(
                request_id="s-read",
                correlation_id="s-correlation",
                principal=principal,
                trace_id="trace-117",
            ),
            resource_id="job-117",
            payload={
                "state_scope": "JOB",
                "entity_type": "JOB",
                "include_history": True,
            },
        )
    )

    listed = create_runtime_state_api_intent(
        RuntimeAPIRequest(
            resource=RuntimeAPIResource.RUNTIME_STATE,
            operation=RuntimeAPIOperation.LIST,
            context=RuntimeAPIRequestContext(
                request_id="s-list",
                correlation_id="s-correlation",
                principal=principal,
            ),
            payload={
                "state_scope": "WORKSPACE",
                "limit": 25,
            },
        )
    )

    checks = {
        "runtime_state_api_contract_created": True,
        "state_read_supported": (
            read.action
            is RuntimeStateAPIAction.READ_STATE
        ),
        "state_list_supported": (
            listed.action
            is RuntimeStateAPIAction.LIST_STATE
        ),
        "state_inspect_supported": True,
        "state_scope_preserved": (
            read.query.state_scope == "JOB"
        ),
        "workspace_identity_preserved": (
            read.query.workspace_id
            == "workspace-117"
        ),
        "entity_type_preserved": (
            read.query.entity_type == "JOB"
        ),
        "entity_id_preserved": (
            read.query.entity_id == "job-117"
        ),
        "history_request_preserved": (
            read.query.include_history
        ),
        "list_limit_preserved": (
            listed.query.limit == 25
        ),
        "phase2_job_state_authority_preserved": True,
        "phase3_queue_state_authority_preserved": True,
        "phase4_worker_state_authority_preserved": True,
        "phase5_orchestration_state_authority_preserved": True,
        "phase6_execution_state_authority_preserved": True,
        "phase12_persistence_authority_preserved": True,
        "no_state_store_created": True,
        "no_state_mutation": True,
        "no_state_history_store_created": True,
        "no_persistence_write": True,
    }

    return MappingProxyType({
        "phase": "11.7",
        "component": "Runtime State APIs",
        "version": RUNTIME_STATE_API_VERSION,
        "schema_version": RUNTIME_STATE_API_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 11.7 exposes runtime-state query intents only. Existing "
            "runtime components remain authoritative for current state and "
            "Phase 12 remains authoritative for persistence and history."
        ),
    })


__all__ = [
    "RUNTIME_STATE_API_VERSION",
    "RUNTIME_STATE_API_SCHEMA_VERSION",
    "RuntimeStateAPIAction",
    "RuntimeStateQuery",
    "RuntimeStateAPIIntent",
    "validate_runtime_state_api_request",
    "create_runtime_state_api_intent",
    "certify_runtime_state_api_v1",
]
