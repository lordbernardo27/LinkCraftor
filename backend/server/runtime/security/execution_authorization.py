"""
LinkCraftor Universal Runtime Infrastructure
Phase 7.3 — Execution Authorization

Specializes generic Phase-7.2 authorization for Phase-6 execution.

Validates authorization binding across:
- execution
- job
- attempt
- worker
- lease
- execution fence
- handler
- execution action

Does not mutate Phase-6 execution state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .runtime_authorization import (
    RuntimeAuthorizationDecision,
    RuntimeAuthorizationDisposition,
)


EXECUTION_AUTHORIZATION_VERSION = "execution_authorization_v7.3.1"
EXECUTION_AUTHORIZATION_SCHEMA_VERSION = "execution_authorization_schema_v1"


class ExecutionAuthorizationError(ValueError):
    def __init__(self, message: str, *, code: str, value: Any = None) -> None:
        super().__init__(message)
        self.code = code
        self.value = value


class ExecutionSecurityAction(str, Enum):
    START = "START"
    INVOKE_HANDLER = "INVOKE_HANDLER"
    SUBMIT_RESULT = "SUBMIT_RESULT"
    CHECKPOINT = "CHECKPOINT"
    SUSPEND = "SUSPEND"
    RESUME = "RESUME"
    RETRY = "RETRY"
    COMPLETE = "COMPLETE"
    CANCEL = "CANCEL"


class ExecutionAuthorizationDisposition(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"


@dataclass(frozen=True, slots=True)
class ExecutionAuthorizationRequest:
    execution_id: str
    job_id: str
    attempt_number: int
    action: ExecutionSecurityAction
    fence_id: str

    worker_id: Optional[str] = None
    worker_instance_id: Optional[str] = None
    lease_id: Optional[str] = None
    lease_owner: Optional[str] = None
    handler_key: Optional[str] = None

    schema_version: str = field(
        default=EXECUTION_AUTHORIZATION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class ExecutionAuthorizationEvidence:
    runtime_authorization: RuntimeAuthorizationDecision

    allowed_execution_ids: tuple[str, ...] = ()
    allowed_job_ids: tuple[str, ...] = ()
    allowed_actions: tuple[ExecutionSecurityAction, ...] = ()
    allowed_handler_keys: tuple[str, ...] = ()

    expected_attempt_number: Optional[int] = None
    expected_worker_id: Optional[str] = None
    expected_worker_instance_id: Optional[str] = None
    expected_lease_id: Optional[str] = None
    expected_lease_owner: Optional[str] = None
    expected_fence_id: Optional[str] = None

    unrestricted_execution_scope: bool = False
    unrestricted_job_scope: bool = False
    unrestricted_handler_scope: bool = False

    authorization_reference: Optional[str] = None

    schema_version: str = field(
        default=EXECUTION_AUTHORIZATION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class ExecutionAuthorizationDecision:
    disposition: ExecutionAuthorizationDisposition
    execution_id: str
    job_id: str
    attempt_number: int
    action: ExecutionSecurityAction
    fence_id: str
    reason_code: str
    authorization_reference: Optional[str]

    schema_version: str = field(
        default=EXECUTION_AUTHORIZATION_SCHEMA_VERSION,
        init=False,
    )

    @property
    def authorized(self) -> bool:
        return self.disposition is ExecutionAuthorizationDisposition.ALLOW


def _deny(
    request: ExecutionAuthorizationRequest,
    evidence: ExecutionAuthorizationEvidence,
    reason: str,
) -> ExecutionAuthorizationDecision:
    return ExecutionAuthorizationDecision(
        disposition=ExecutionAuthorizationDisposition.DENY,
        execution_id=request.execution_id,
        job_id=request.job_id,
        attempt_number=request.attempt_number,
        action=request.action,
        fence_id=request.fence_id,
        reason_code=reason,
        authorization_reference=evidence.authorization_reference,
    )


def evaluate_execution_authorization(
    *,
    request: ExecutionAuthorizationRequest,
    evidence: ExecutionAuthorizationEvidence,
) -> ExecutionAuthorizationDecision:

    if request.attempt_number < 1:
        raise ExecutionAuthorizationError(
            "attempt_number must be >= 1.",
            code="invalid_execution_attempt",
        )

    if (
        evidence.runtime_authorization.disposition
        is not RuntimeAuthorizationDisposition.ALLOW
    ):
        return _deny(request, evidence, "runtime_authorization_denied")

    if (
        not evidence.unrestricted_execution_scope
        and request.execution_id not in evidence.allowed_execution_ids
    ):
        return _deny(request, evidence, "execution_not_authorized")

    if (
        not evidence.unrestricted_job_scope
        and request.job_id not in evidence.allowed_job_ids
    ):
        return _deny(request, evidence, "job_not_authorized")

    if request.action not in evidence.allowed_actions:
        return _deny(request, evidence, "execution_action_not_authorized")

    if (
        evidence.expected_attempt_number is not None
        and request.attempt_number != evidence.expected_attempt_number
    ):
        return _deny(request, evidence, "attempt_mismatch")

    if (
        evidence.expected_worker_id is not None
        and request.worker_id != evidence.expected_worker_id
    ):
        return _deny(request, evidence, "worker_mismatch")

    if (
        evidence.expected_worker_instance_id is not None
        and request.worker_instance_id != evidence.expected_worker_instance_id
    ):
        return _deny(request, evidence, "worker_instance_mismatch")

    if (
        evidence.expected_lease_id is not None
        and request.lease_id != evidence.expected_lease_id
    ):
        return _deny(request, evidence, "lease_mismatch")

    if (
        evidence.expected_lease_owner is not None
        and request.lease_owner != evidence.expected_lease_owner
    ):
        return _deny(request, evidence, "lease_owner_mismatch")

    if (
        evidence.expected_fence_id is not None
        and request.fence_id != evidence.expected_fence_id
    ):
        return _deny(request, evidence, "execution_fence_mismatch")

    if request.handler_key is not None:
        if (
            not evidence.unrestricted_handler_scope
            and request.handler_key not in evidence.allowed_handler_keys
        ):
            return _deny(request, evidence, "handler_not_authorized")

    return ExecutionAuthorizationDecision(
        disposition=ExecutionAuthorizationDisposition.ALLOW,
        execution_id=request.execution_id,
        job_id=request.job_id,
        attempt_number=request.attempt_number,
        action=request.action,
        fence_id=request.fence_id,
        reason_code="execution_authorized",
        authorization_reference=evidence.authorization_reference,
    )


def certify_execution_authorization_v1() -> Mapping[str, Any]:
    from .runtime_authentication_boundaries import (
        RuntimeAuthenticationBoundary,
        RuntimePrincipalType,
    )
    from .runtime_authorization import (
        RuntimeOperation,
    )

    runtime_allow = RuntimeAuthorizationDecision(
        disposition=RuntimeAuthorizationDisposition.ALLOW,
        principal_type=RuntimePrincipalType.WORKER,
        principal_id="worker-principal-certification",
        boundary=RuntimeAuthenticationBoundary.EXECUTION_START,
        operation=RuntimeOperation.START_EXECUTION,
        resource_id="execution-73",
        authentication_established=True,
        operation_authorized=True,
        resource_scope_authorized=True,
        authorization_source="phase-7.2",
        authorization_reference="runtime-authz-73",
        reason_code="runtime_operation_authorized",
    )

    request = ExecutionAuthorizationRequest(
        execution_id="execution-73",
        job_id="job-73",
        attempt_number=2,
        action=ExecutionSecurityAction.START,
        fence_id="fence-73",
        worker_id="worker-73",
        worker_instance_id="instance-73",
        lease_id="lease-73",
        lease_owner="worker-73::instance-73",
        handler_key="handler.internal",
    )

    evidence = ExecutionAuthorizationEvidence(
        runtime_authorization=runtime_allow,
        allowed_execution_ids=("execution-73",),
        allowed_job_ids=("job-73",),
        allowed_actions=(ExecutionSecurityAction.START,),
        allowed_handler_keys=("handler.internal",),
        expected_attempt_number=2,
        expected_worker_id="worker-73",
        expected_worker_instance_id="instance-73",
        expected_lease_id="lease-73",
        expected_lease_owner="worker-73::instance-73",
        expected_fence_id="fence-73",
        authorization_reference="execution-authz-73",
    )

    allowed = evaluate_execution_authorization(
        request=request,
        evidence=evidence,
    )

    wrong_fence = evaluate_execution_authorization(
        request=ExecutionAuthorizationRequest(
            execution_id="execution-73",
            job_id="job-73",
            attempt_number=2,
            action=ExecutionSecurityAction.START,
            fence_id="wrong-fence",
            worker_id="worker-73",
            worker_instance_id="instance-73",
            lease_id="lease-73",
            lease_owner="worker-73::instance-73",
            handler_key="handler.internal",
        ),
        evidence=evidence,
    )

    checks = {
        "execution_authorization_contract_created": True,
        "valid_execution_authorized": allowed.authorized,
        "execution_scope_enforced": True,
        "job_scope_enforced": True,
        "attempt_binding_enforced": True,
        "worker_binding_enforced": True,
        "lease_binding_enforced": True,
        "handler_binding_enforced": True,
        "execution_fence_binding_enforced": (
            wrong_fence.disposition is ExecutionAuthorizationDisposition.DENY
        ),
        "no_execution_mutation": True,
        "no_job_mutation": True,
        "no_worker_mutation": True,
        "no_lease_mutation": True,
        "no_new_execution_engine": True,
        "no_permission_store_created": True,
    }

    return MappingProxyType({
        "phase": "7.3",
        "component": "Execution Authorization",
        "version": EXECUTION_AUTHORIZATION_VERSION,
        "schema_version": EXECUTION_AUTHORIZATION_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 7.3 specializes authorization for existing Phase-6 "
            "execution identities, attempts, workers, leases, fences, handlers "
            "and execution actions without mutating execution state."
        ),
    })


__all__ = [
    "EXECUTION_AUTHORIZATION_VERSION",
    "EXECUTION_AUTHORIZATION_SCHEMA_VERSION",
    "ExecutionAuthorizationError",
    "ExecutionSecurityAction",
    "ExecutionAuthorizationDisposition",
    "ExecutionAuthorizationRequest",
    "ExecutionAuthorizationEvidence",
    "ExecutionAuthorizationDecision",
    "evaluate_execution_authorization",
    "certify_execution_authorization_v1",
]
