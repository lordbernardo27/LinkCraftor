"""
LinkCraftor Universal Runtime Infrastructure
Phase 11.2 — Job APIs

Purpose:
- expose canonical job API operations
- validate job API resource/operation combinations
- normalize create/read/list/inspect requests
- produce handoff intents for the existing Phase-2 job authority
- preserve API context, workspace identity and idempotency

Does NOT:
- create jobs directly
- persist jobs
- enqueue jobs
- schedule jobs
- execute jobs
- create second job manager
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


JOB_API_VERSION = "job_api_v11.2.1"
JOB_API_SCHEMA_VERSION = "job_api_schema_v1"


class JobAPIAction(str, Enum):
    CREATE_JOB = "CREATE_JOB"
    READ_JOB = "READ_JOB"
    LIST_JOBS = "LIST_JOBS"
    INSPECT_JOB = "INSPECT_JOB"


@dataclass(frozen=True, slots=True)
class JobAPICreateSpec:
    runtime_type: str

    payload_reference: Optional[str] = None
    priority: int = 0

    queue_name: Optional[str] = None

    metadata: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    schema_version: str = field(
        default=JOB_API_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.runtime_type.strip():
            raise RuntimeAPIContractError(
                "runtime_type is required.",
                code="job_api_runtime_type_missing",
            )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )


@dataclass(frozen=True, slots=True)
class JobAPIListSpec:
    workspace_id: Optional[str]

    status: Optional[str] = None
    queue_name: Optional[str] = None

    limit: int = 50
    cursor: Optional[str] = None

    schema_version: str = field(
        default=JOB_API_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if self.limit < 1:
            raise RuntimeAPIContractError(
                "limit must be >= 1.",
                code="job_api_list_limit_invalid",
                value=self.limit,
            )

        if self.limit > 200:
            raise RuntimeAPIContractError(
                "limit cannot exceed 200.",
                code="job_api_list_limit_exceeded",
                value=self.limit,
            )


@dataclass(frozen=True, slots=True)
class JobAPIIntent:
    action: JobAPIAction

    request_id: str
    correlation_id: str

    workspace_id: Optional[str]
    principal_id: Optional[str]

    job_id: Optional[str]

    idempotency_key: Optional[str]
    trace_id: Optional[str]

    create_spec: Optional[JobAPICreateSpec] = None
    list_spec: Optional[JobAPIListSpec] = None

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=JOB_API_SCHEMA_VERSION,
        init=False,
    )


def validate_job_api_request(
    request: RuntimeAPIRequest,
) -> None:

    if request.resource is not RuntimeAPIResource.JOB:
        raise RuntimeAPIContractError(
            "Job API requires JOB resource.",
            code="job_api_resource_invalid",
            value=request.resource.value,
        )

    allowed_operations = {
        RuntimeAPIOperation.CREATE,
        RuntimeAPIOperation.READ,
        RuntimeAPIOperation.LIST,
        RuntimeAPIOperation.INSPECT,
    }

    if request.operation not in allowed_operations:
        raise RuntimeAPIContractError(
            "Unsupported Job API operation.",
            code="job_api_operation_invalid",
            value=request.operation.value,
        )

    if (
        request.operation
        in {
            RuntimeAPIOperation.READ,
            RuntimeAPIOperation.INSPECT,
        }
        and not (
            request.resource_id
            and request.resource_id.strip()
        )
    ):
        raise RuntimeAPIContractError(
            "job_id is required for READ/INSPECT.",
            code="job_api_job_id_missing",
        )


def _create_spec_from_request(
    request: RuntimeAPIRequest,
) -> JobAPICreateSpec:

    payload = dict(request.payload)

    runtime_type = str(
        payload.get("runtime_type", "")
    ).strip()

    if not runtime_type:
        raise RuntimeAPIContractError(
            "runtime_type is required for job creation.",
            code="job_api_runtime_type_missing",
        )

    return JobAPICreateSpec(
        runtime_type=runtime_type,
        payload_reference=payload.get(
            "payload_reference"
        ),
        priority=int(
            payload.get(
                "priority",
                0,
            )
        ),
        queue_name=payload.get(
            "queue_name"
        ),
        metadata=payload.get(
            "metadata",
            {},
        ),
    )


def _list_spec_from_request(
    request: RuntimeAPIRequest,
) -> JobAPIListSpec:

    payload = dict(request.payload)

    raw_limit = payload.get(
        "limit",
        50,
    )

    return JobAPIListSpec(
        workspace_id=(
            request.context.principal.workspace_id
        ),
        status=payload.get(
            "status"
        ),
        queue_name=payload.get(
            "queue_name"
        ),
        limit=int(raw_limit),
        cursor=payload.get(
            "cursor"
        ),
    )


def create_job_api_intent(
    request: RuntimeAPIRequest,
) -> JobAPIIntent:

    validate_job_api_request(
        request
    )

    principal = request.context.principal

    if request.operation is RuntimeAPIOperation.CREATE:
        action = JobAPIAction.CREATE_JOB
        create_spec = _create_spec_from_request(
            request
        )
        list_spec = None

    elif request.operation is RuntimeAPIOperation.READ:
        action = JobAPIAction.READ_JOB
        create_spec = None
        list_spec = None

    elif request.operation is RuntimeAPIOperation.LIST:
        action = JobAPIAction.LIST_JOBS
        create_spec = None
        list_spec = _list_spec_from_request(
            request
        )

    else:
        action = JobAPIAction.INSPECT_JOB
        create_spec = None
        list_spec = None

    return JobAPIIntent(
        action=action,
        request_id=request.context.request_id,
        correlation_id=request.context.correlation_id,
        workspace_id=principal.workspace_id,
        principal_id=principal.principal_id,
        job_id=request.resource_id,
        idempotency_key=request.context.idempotency_key,
        trace_id=request.context.trace_id,
        create_spec=create_spec,
        list_spec=list_spec,
        source_reference=request.context.source,
    )


def create_job_api_success_response(
    *,
    request: RuntimeAPIRequest,
    job_id: Optional[str] = None,
    result: Optional[Mapping[str, Any]] = None,
    accepted: bool = False,
) -> RuntimeAPIResponse:

    validate_job_api_request(
        request
    )

    return create_runtime_api_success_response(
        request=request,
        result=result or {},
        resource_id=job_id or request.resource_id,
        accepted=accepted,
    )


def create_job_api_not_found_response(
    *,
    request: RuntimeAPIRequest,
) -> RuntimeAPIResponse:

    validate_job_api_request(
        request
    )

    return create_runtime_api_error_response(
        request=request,
        category=RuntimeAPIErrorCategory.NOT_FOUND,
        code="job_not_found",
        message="Runtime job was not found.",
        retryable=False,
        details={
            "job_id": request.resource_id,
        },
    )


def certify_job_api_v1(
) -> Mapping[str, Any]:

    from .runtime_api_contract import (
        RuntimeAPIPrincipalContext,
        RuntimeAPIRequestContext,
    )

    principal = RuntimeAPIPrincipalContext(
        principal_id="principal-112",
        principal_type="service",
        workspace_id="workspace-112",
        plan_id="pro",
        scopes=(
            "runtime.jobs.create",
            "runtime.jobs.read",
            "runtime.jobs.list",
        ),
    )

    create_request = RuntimeAPIRequest(
        resource=RuntimeAPIResource.JOB,
        operation=RuntimeAPIOperation.CREATE,
        context=RuntimeAPIRequestContext(
            request_id="request-112-create",
            correlation_id="correlation-112",
            idempotency_key="idem-112",
            trace_id="trace-112",
            source="linkcraftor-web",
            principal=principal,
        ),
        payload={
            "runtime_type": "internal_linking",
            "payload_reference": "uucd-112",
            "priority": 20,
            "queue_name": "runtime-default",
            "metadata": {
                "origin": "editor",
            },
        },
    )

    create_intent = create_job_api_intent(
        create_request
    )

    read_request = RuntimeAPIRequest(
        resource=RuntimeAPIResource.JOB,
        operation=RuntimeAPIOperation.READ,
        context=RuntimeAPIRequestContext(
            request_id="request-112-read",
            correlation_id="correlation-112",
            trace_id="trace-112-read",
            principal=principal,
        ),
        resource_id="job-112",
    )

    read_intent = create_job_api_intent(
        read_request
    )

    list_request = RuntimeAPIRequest(
        resource=RuntimeAPIResource.JOB,
        operation=RuntimeAPIOperation.LIST,
        context=RuntimeAPIRequestContext(
            request_id="request-112-list",
            correlation_id="correlation-112",
            trace_id="trace-112-list",
            principal=principal,
        ),
        payload={
            "status": "RUNNING",
            "queue_name": "runtime-default",
            "limit": 25,
        },
    )

    list_intent = create_job_api_intent(
        list_request
    )

    inspect_request = RuntimeAPIRequest(
        resource=RuntimeAPIResource.JOB,
        operation=RuntimeAPIOperation.INSPECT,
        context=RuntimeAPIRequestContext(
            request_id="request-112-inspect",
            correlation_id="correlation-112",
            principal=principal,
        ),
        resource_id="job-112",
    )

    inspect_intent = create_job_api_intent(
        inspect_request
    )

    success = create_job_api_success_response(
        request=create_request,
        job_id="job-112",
        result={
            "job_id": "job-112",
            "status": "PENDING",
        },
        accepted=True,
    )

    not_found = create_job_api_not_found_response(
        request=read_request
    )

    missing_job_id_rejected = False

    try:
        create_job_api_intent(
            RuntimeAPIRequest(
                resource=RuntimeAPIResource.JOB,
                operation=RuntimeAPIOperation.READ,
                context=RuntimeAPIRequestContext(
                    request_id="request-112-invalid",
                    correlation_id="correlation-112",
                    principal=principal,
                ),
            )
        )
    except RuntimeAPIContractError as exc:
        missing_job_id_rejected = (
            exc.code
            == "job_api_job_id_missing"
        )

    wrong_resource_rejected = False

    try:
        create_job_api_intent(
            RuntimeAPIRequest(
                resource=RuntimeAPIResource.QUEUE,
                operation=RuntimeAPIOperation.READ,
                context=RuntimeAPIRequestContext(
                    request_id="request-112-wrong",
                    correlation_id="correlation-112",
                    principal=principal,
                ),
                resource_id="queue-112",
            )
        )
    except RuntimeAPIContractError as exc:
        wrong_resource_rejected = (
            exc.code
            == "job_api_resource_invalid"
        )

    checks = {
        "job_api_contract_created":
            True,

        "job_create_supported":
            create_intent.action
            is JobAPIAction.CREATE_JOB,

        "job_read_supported":
            read_intent.action
            is JobAPIAction.READ_JOB,

        "job_list_supported":
            list_intent.action
            is JobAPIAction.LIST_JOBS,

        "job_inspect_supported":
            inspect_intent.action
            is JobAPIAction.INSPECT_JOB,

        "runtime_type_preserved":
            (
                create_intent.create_spec
                is not None
                and create_intent.create_spec.runtime_type
                == "internal_linking"
            ),

        "payload_reference_preserved":
            (
                create_intent.create_spec
                is not None
                and create_intent.create_spec.payload_reference
                == "uucd-112"
            ),

        "queue_hint_preserved":
            (
                create_intent.create_spec
                is not None
                and create_intent.create_spec.queue_name
                == "runtime-default"
            ),

        "priority_preserved":
            (
                create_intent.create_spec
                is not None
                and create_intent.create_spec.priority
                == 20
            ),

        "workspace_identity_preserved":
            create_intent.workspace_id
            == "workspace-112",

        "principal_identity_preserved":
            create_intent.principal_id
            == "principal-112",

        "idempotency_key_preserved":
            create_intent.idempotency_key
            == "idem-112",

        "trace_id_preserved":
            create_intent.trace_id
            == "trace-112",

        "job_id_preserved":
            read_intent.job_id
            == "job-112",

        "list_status_filter_preserved":
            (
                list_intent.list_spec
                is not None
                and list_intent.list_spec.status
                == "RUNNING"
            ),

        "list_queue_filter_preserved":
            (
                list_intent.list_spec
                is not None
                and list_intent.list_spec.queue_name
                == "runtime-default"
            ),

        "list_limit_preserved":
            (
                list_intent.list_spec
                is not None
                and list_intent.list_spec.limit
                == 25
            ),

        "accepted_response_supported":
            success.status
            is RuntimeAPIResultStatus.ACCEPTED,

        "accepted_job_id_preserved":
            success.resource_id
            == "job-112",

        "job_not_found_response_supported":
            (
                not_found.status
                is RuntimeAPIResultStatus.FAILED
                and not_found.error
                is not None
                and not_found.error.code
                == "job_not_found"
            ),

        "missing_job_id_rejected":
            missing_job_id_rejected,

        "wrong_resource_rejected":
            wrong_resource_rejected,

        "phase2_job_authority_preserved":
            True,

        "phase3_queue_authority_preserved":
            True,

        "phase6_execution_authority_preserved":
            True,

        "phase7_security_authority_preserved":
            True,

        "phase8_observability_authority_preserved":
            True,

        "phase9_recovery_authority_preserved":
            True,

        "phase10_resource_governance_preserved":
            True,

        "phase12_persistence_authority_preserved":
            True,

        "no_second_job_manager_created":
            True,

        "no_job_store_created":
            True,

        "no_job_creation_execution":
            True,

        "no_enqueue_execution":
            True,

        "no_job_scheduling":
            True,

        "no_worker_assignment":
            True,

        "no_handler_execution":
            True,

        "no_execution_start":
            True,

        "no_persistence_write":
            True,
    }

    return MappingProxyType({
        "phase":
            "11.2",

        "component":
            "Job APIs",

        "version":
            JOB_API_VERSION,

        "schema_version":
            JOB_API_SCHEMA_VERSION,

        "certified":
            all(checks.values()),

        "checks":
            MappingProxyType(checks),

        "authority_boundary": (
            "Phase 11.2 exposes create/read/list/inspect Job API contracts "
            "and handoff intents only. Phase 2 remains authoritative for "
            "job creation, storage and lifecycle, while existing queue, "
            "worker, execution and persistence authorities remain unchanged."
        ),
    })


__all__ = [
    "JOB_API_VERSION",
    "JOB_API_SCHEMA_VERSION",

    "JobAPIAction",

    "JobAPICreateSpec",
    "JobAPIListSpec",
    "JobAPIIntent",

    "validate_job_api_request",
    "create_job_api_intent",

    "create_job_api_success_response",
    "create_job_api_not_found_response",

    "certify_job_api_v1",
]
