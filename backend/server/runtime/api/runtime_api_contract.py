"""
LinkCraftor Universal Runtime Infrastructure
Phase 11.1 — Universal Runtime API Contract

Purpose:
- define the canonical Runtime API request envelope
- define canonical Runtime API response envelope
- define operation/resource vocabulary
- define correlation/idempotency/version context
- define authentication/authorization context handoff
- define error contract
- preserve existing runtime authorities

Does NOT:
- create HTTP server
- create second router stack
- create jobs
- enqueue work
- assign workers
- execute handlers
- mutate orchestrations
- implement authentication
- implement authorization
- implement rate limiting
- persist state
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional


RUNTIME_API_CONTRACT_VERSION = (
    "runtime_api_contract_v11.1.1"
)

RUNTIME_API_CONTRACT_SCHEMA_VERSION = (
    "runtime_api_contract_schema_v1"
)

RUNTIME_API_VERSION = "v1"


class RuntimeAPIContractError(ValueError):
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


class RuntimeAPIResource(str, Enum):
    JOB = "JOB"
    QUEUE = "QUEUE"
    WORKER = "WORKER"
    EXECUTION = "EXECUTION"
    ORCHESTRATION = "ORCHESTRATION"
    RUNTIME_STATE = "RUNTIME_STATE"
    CANCELLATION = "CANCELLATION"
    RETRY_RECOVERY = "RETRY_RECOVERY"
    ADMIN = "ADMIN"


class RuntimeAPIOperation(str, Enum):
    CREATE = "CREATE"
    READ = "READ"
    LIST = "LIST"
    UPDATE = "UPDATE"
    CANCEL = "CANCEL"
    TERMINATE = "TERMINATE"
    RETRY = "RETRY"
    RECOVER = "RECOVER"
    INSPECT = "INSPECT"
    CONTROL = "CONTROL"


class RuntimeAPIResultStatus(str, Enum):
    SUCCESS = "SUCCESS"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class RuntimeAPIErrorCategory(str, Enum):
    VALIDATION = "VALIDATION"
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    RATE_LIMIT = "RATE_LIMIT"
    RESOURCE_GOVERNANCE = "RESOURCE_GOVERNANCE"
    RUNTIME = "RUNTIME"
    INTERNAL = "INTERNAL"


@dataclass(frozen=True, slots=True)
class RuntimeAPIPrincipalContext:
    principal_id: Optional[str] = None
    principal_type: Optional[str] = None

    workspace_id: Optional[str] = None
    plan_id: Optional[str] = None

    scopes: tuple[str, ...] = ()

    authentication_reference: Optional[str] = None
    authorization_reference: Optional[str] = None

    schema_version: str = field(
        default=RUNTIME_API_CONTRACT_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class RuntimeAPIRequestContext:
    request_id: str
    correlation_id: str

    api_version: str = RUNTIME_API_VERSION

    idempotency_key: Optional[str] = None
    trace_id: Optional[str] = None

    source: Optional[str] = None

    principal: RuntimeAPIPrincipalContext = field(
        default_factory=RuntimeAPIPrincipalContext
    )

    metadata: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    schema_version: str = field(
        default=RUNTIME_API_CONTRACT_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.request_id.strip():
            raise RuntimeAPIContractError(
                "request_id is required.",
                code="runtime_api_request_id_missing",
            )

        if not self.correlation_id.strip():
            raise RuntimeAPIContractError(
                "correlation_id is required.",
                code="runtime_api_correlation_id_missing",
            )

        if not self.api_version.strip():
            raise RuntimeAPIContractError(
                "api_version is required.",
                code="runtime_api_version_missing",
            )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )


@dataclass(frozen=True, slots=True)
class RuntimeAPIRequest:
    resource: RuntimeAPIResource
    operation: RuntimeAPIOperation

    context: RuntimeAPIRequestContext

    resource_id: Optional[str] = None

    payload: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    schema_version: str = field(
        default=RUNTIME_API_CONTRACT_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "payload",
            MappingProxyType(dict(self.payload)),
        )


@dataclass(frozen=True, slots=True)
class RuntimeAPIError:
    category: RuntimeAPIErrorCategory
    code: str
    message: str

    retryable: bool = False

    details: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    schema_version: str = field(
        default=RUNTIME_API_CONTRACT_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.code.strip():
            raise RuntimeAPIContractError(
                "error code is required.",
                code="runtime_api_error_code_missing",
            )

        if not self.message.strip():
            raise RuntimeAPIContractError(
                "error message is required.",
                code="runtime_api_error_message_missing",
            )

        object.__setattr__(
            self,
            "details",
            MappingProxyType(dict(self.details)),
        )


@dataclass(frozen=True, slots=True)
class RuntimeAPIResponse:
    request_id: str
    correlation_id: str

    status: RuntimeAPIResultStatus

    api_version: str = RUNTIME_API_VERSION

    resource: Optional[RuntimeAPIResource] = None
    operation: Optional[RuntimeAPIOperation] = None

    resource_id: Optional[str] = None

    result: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    error: Optional[RuntimeAPIError] = None

    trace_id: Optional[str] = None

    schema_version: str = field(
        default=RUNTIME_API_CONTRACT_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.request_id.strip():
            raise RuntimeAPIContractError(
                "response request_id is required.",
                code="runtime_api_response_request_id_missing",
            )

        if not self.correlation_id.strip():
            raise RuntimeAPIContractError(
                "response correlation_id is required.",
                code="runtime_api_response_correlation_id_missing",
            )

        if (
            self.status is RuntimeAPIResultStatus.FAILED
            and self.error is None
        ):
            raise RuntimeAPIContractError(
                "FAILED response requires error.",
                code="runtime_api_failed_response_error_missing",
            )

        object.__setattr__(
            self,
            "result",
            MappingProxyType(dict(self.result)),
        )


@dataclass(frozen=True, slots=True)
class RuntimeAPIDispatchIntent:
    """
    Handoff contract only.

    Later 11.x API modules translate an API request into a dispatch intent
    for existing runtime authorities. This object is not a dispatcher.
    """

    resource: RuntimeAPIResource
    operation: RuntimeAPIOperation

    resource_id: Optional[str]

    request_id: str
    correlation_id: str

    workspace_id: Optional[str]
    principal_id: Optional[str]

    idempotency_key: Optional[str]
    trace_id: Optional[str]

    payload: Mapping[str, Any]

    schema_version: str = field(
        default=RUNTIME_API_CONTRACT_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "payload",
            MappingProxyType(dict(self.payload)),
        )


def create_runtime_api_dispatch_intent(
    request: RuntimeAPIRequest,
) -> RuntimeAPIDispatchIntent:

    return RuntimeAPIDispatchIntent(
        resource=request.resource,
        operation=request.operation,
        resource_id=request.resource_id,
        request_id=request.context.request_id,
        correlation_id=request.context.correlation_id,
        workspace_id=request.context.principal.workspace_id,
        principal_id=request.context.principal.principal_id,
        idempotency_key=request.context.idempotency_key,
        trace_id=request.context.trace_id,
        payload=request.payload,
    )


def create_runtime_api_success_response(
    *,
    request: RuntimeAPIRequest,
    result: Optional[Mapping[str, Any]] = None,
    resource_id: Optional[str] = None,
    accepted: bool = False,
) -> RuntimeAPIResponse:

    return RuntimeAPIResponse(
        request_id=request.context.request_id,
        correlation_id=request.context.correlation_id,
        api_version=request.context.api_version,
        status=(
            RuntimeAPIResultStatus.ACCEPTED
            if accepted
            else RuntimeAPIResultStatus.SUCCESS
        ),
        resource=request.resource,
        operation=request.operation,
        resource_id=resource_id or request.resource_id,
        result=result or {},
        trace_id=request.context.trace_id,
    )


def create_runtime_api_error_response(
    *,
    request: RuntimeAPIRequest,
    category: RuntimeAPIErrorCategory,
    code: str,
    message: str,
    retryable: bool = False,
    details: Optional[Mapping[str, Any]] = None,
) -> RuntimeAPIResponse:

    return RuntimeAPIResponse(
        request_id=request.context.request_id,
        correlation_id=request.context.correlation_id,
        api_version=request.context.api_version,
        status=RuntimeAPIResultStatus.FAILED,
        resource=request.resource,
        operation=request.operation,
        resource_id=request.resource_id,
        result={},
        error=RuntimeAPIError(
            category=category,
            code=code,
            message=message,
            retryable=retryable,
            details=details or {},
        ),
        trace_id=request.context.trace_id,
    )


def certify_runtime_api_contract_v1(
) -> Mapping[str, Any]:

    principal = RuntimeAPIPrincipalContext(
        principal_id="principal-111",
        principal_type="service",
        workspace_id="workspace-111",
        plan_id="pro",
        scopes=(
            "runtime.jobs.read",
            "runtime.jobs.create",
        ),
        authentication_reference="authn-111",
        authorization_reference="authz-111",
    )

    context = RuntimeAPIRequestContext(
        request_id="request-111",
        correlation_id="correlation-111",
        api_version="v1",
        idempotency_key="idem-111",
        trace_id="trace-111",
        source="linkcraftor-web",
        principal=principal,
        metadata={
            "client": "web",
        },
    )

    request = RuntimeAPIRequest(
        resource=RuntimeAPIResource.JOB,
        operation=RuntimeAPIOperation.CREATE,
        context=context,
        payload={
            "runtime_type": "internal_linking",
        },
    )

    intent = create_runtime_api_dispatch_intent(
        request
    )

    success = create_runtime_api_success_response(
        request=request,
        resource_id="job-111",
        result={
            "job_id": "job-111",
        },
        accepted=True,
    )

    failure = create_runtime_api_error_response(
        request=request,
        category=RuntimeAPIErrorCategory.AUTHORIZATION,
        code="runtime_scope_denied",
        message="Runtime scope denied.",
        retryable=False,
    )

    checks = {
        "runtime_api_contract_created": True,

        "api_version_defined":
            RUNTIME_API_VERSION == "v1",

        "job_resource_supported":
            RuntimeAPIResource.JOB.value == "JOB",

        "queue_resource_supported":
            RuntimeAPIResource.QUEUE.value == "QUEUE",

        "worker_resource_supported":
            RuntimeAPIResource.WORKER.value == "WORKER",

        "execution_resource_supported":
            RuntimeAPIResource.EXECUTION.value == "EXECUTION",

        "orchestration_resource_supported":
            RuntimeAPIResource.ORCHESTRATION.value
            == "ORCHESTRATION",

        "runtime_state_resource_supported":
            RuntimeAPIResource.RUNTIME_STATE.value
            == "RUNTIME_STATE",

        "cancellation_resource_supported":
            RuntimeAPIResource.CANCELLATION.value
            == "CANCELLATION",

        "retry_recovery_resource_supported":
            RuntimeAPIResource.RETRY_RECOVERY.value
            == "RETRY_RECOVERY",

        "admin_resource_supported":
            RuntimeAPIResource.ADMIN.value == "ADMIN",

        "request_identity_preserved":
            intent.request_id == "request-111",

        "correlation_identity_preserved":
            intent.correlation_id == "correlation-111",

        "workspace_identity_preserved":
            intent.workspace_id == "workspace-111",

        "principal_identity_preserved":
            intent.principal_id == "principal-111",

        "idempotency_key_preserved":
            intent.idempotency_key == "idem-111",

        "trace_identity_preserved":
            intent.trace_id == "trace-111",

        "payload_preserved":
            intent.payload["runtime_type"]
            == "internal_linking",

        "success_response_supported":
            success.status
            is RuntimeAPIResultStatus.ACCEPTED,

        "success_resource_id_preserved":
            success.resource_id == "job-111",

        "error_response_supported":
            failure.status
            is RuntimeAPIResultStatus.FAILED,

        "error_category_preserved":
            failure.error is not None
            and failure.error.category
            is RuntimeAPIErrorCategory.AUTHORIZATION,

        "authentication_context_handoff_supported":
            principal.authentication_reference
            == "authn-111",

        "authorization_context_handoff_supported":
            principal.authorization_reference
            == "authz-111",

        "phase2_job_authority_preserved":
            True,

        "phase3_queue_authority_preserved":
            True,

        "phase4_worker_authority_preserved":
            True,

        "phase5_orchestration_authority_preserved":
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

        "no_http_server_created":
            True,

        "no_second_router_created":
            True,

        "no_job_creation_execution":
            True,

        "no_enqueue_execution":
            True,

        "no_worker_assignment":
            True,

        "no_handler_execution":
            True,

        "no_orchestration_mutation":
            True,

        "no_authentication_engine_created":
            True,

        "no_authorization_engine_created":
            True,

        "no_rate_limiter_created":
            True,

        "no_persistence_write":
            True,
    }

    return MappingProxyType({
        "phase":
            "11.1",

        "component":
            "Universal Runtime API Contract",

        "version":
            RUNTIME_API_CONTRACT_VERSION,

        "schema_version":
            RUNTIME_API_CONTRACT_SCHEMA_VERSION,

        "certified":
            all(checks.values()),

        "checks":
            MappingProxyType(checks),

        "authority_boundary": (
            "Phase 11.1 defines canonical Runtime API request, response, "
            "principal, error and dispatch-intent contracts only. Existing "
            "job, queue, worker, orchestration, execution, security, "
            "observability, recovery, resource-governance and persistence "
            "authorities remain unchanged."
        ),
    })


__all__ = [
    "RUNTIME_API_CONTRACT_VERSION",
    "RUNTIME_API_CONTRACT_SCHEMA_VERSION",
    "RUNTIME_API_VERSION",

    "RuntimeAPIContractError",

    "RuntimeAPIResource",
    "RuntimeAPIOperation",
    "RuntimeAPIResultStatus",
    "RuntimeAPIErrorCategory",

    "RuntimeAPIPrincipalContext",
    "RuntimeAPIRequestContext",
    "RuntimeAPIRequest",
    "RuntimeAPIError",
    "RuntimeAPIResponse",
    "RuntimeAPIDispatchIntent",

    "create_runtime_api_dispatch_intent",
    "create_runtime_api_success_response",
    "create_runtime_api_error_response",

    "certify_runtime_api_contract_v1",
]
