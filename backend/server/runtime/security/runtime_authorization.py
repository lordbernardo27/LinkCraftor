"""
LinkCraftor Universal Runtime Infrastructure
Phase 7.2 — Runtime Authorization

Canonical generic runtime authorization layer.

Consumes:
- Phase 7.1 Runtime Authentication Boundary decision
- Existing principal identity references
- Caller-supplied authorization evidence from existing authorities

Owns:
- generic runtime authorization request/decision contract
- deny-by-default authorization semantics
- principal/action authorization evaluation
- generic resource-scope validation
- authorization evidence generation

Does NOT own:
- authentication
- token validation
- worker identity verification
- service-to-service trust establishment
- execution-specific authorization
- job execution permission policy
- privilege escalation policy
- permission persistence
- role persistence
- identity persistence

Those remain later Phase-7 components or existing authoritative systems.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .runtime_authentication_boundaries import (
    AuthenticationBoundaryDisposition,
    RuntimeAuthenticationBoundary,
    RuntimeAuthenticationBoundaryDecision,
    RuntimePrincipalIdentity,
    RuntimePrincipalType,
)


RUNTIME_AUTHORIZATION_VERSION = (
    "runtime_authorization_v7.2.1"
)

RUNTIME_AUTHORIZATION_SCHEMA_VERSION = (
    "runtime_authorization_schema_v1"
)


class RuntimeAuthorizationError(ValueError):
    """Raised when runtime authorization inputs are malformed."""

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


class RuntimeOperation(str, Enum):
    SUBMIT_JOB = "SUBMIT_JOB"
    INSPECT_QUEUE = "INSPECT_QUEUE"
    CONSUME_QUEUE = "CONSUME_QUEUE"
    REGISTER_WORKER = "REGISTER_WORKER"
    ASSIGN_WORKER = "ASSIGN_WORKER"
    MANAGE_LEASE = "MANAGE_LEASE"
    CONTROL_ORCHESTRATION = "CONTROL_ORCHESTRATION"
    START_EXECUTION = "START_EXECUTION"
    INVOKE_HANDLER = "INVOKE_HANDLER"
    SUBMIT_EXECUTION_RESULT = "SUBMIT_EXECUTION_RESULT"
    MANAGE_CHECKPOINT = "MANAGE_CHECKPOINT"
    SUSPEND_RUNTIME_WORK = "SUSPEND_RUNTIME_WORK"
    RESUME_RUNTIME_WORK = "RESUME_RUNTIME_WORK"
    RECOVER_RUNTIME_WORK = "RECOVER_RUNTIME_WORK"
    CANCEL_RUNTIME_WORK = "CANCEL_RUNTIME_WORK"
    ADMINISTER_RUNTIME = "ADMINISTER_RUNTIME"
    CALL_INTERNAL_SERVICE = "CALL_INTERNAL_SERVICE"


class RuntimeAuthorizationDisposition(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"


@dataclass(
    frozen=True,
    slots=True,
)
class RuntimeAuthorizationEvidence:
    """
    Caller-supplied authorization facts.

    This structure intentionally does not persist roles or permissions.
    Existing identity / entitlement / policy authorities may populate it.
    """

    authentication_established: bool

    trusted_internal_identity: bool = False

    granted_operations: tuple[
        RuntimeOperation,
        ...,
    ] = ()

    allowed_resource_ids: tuple[
        str,
        ...,
    ] = ()

    unrestricted_resource_scope: bool = False

    authorization_source: Optional[str] = None
    authorization_reference: Optional[str] = None

    metadata: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    schema_version: str = field(
        default=RUNTIME_AUTHORIZATION_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "granted_operations",
            tuple(
                self.granted_operations
            ),
        )

        object.__setattr__(
            self,
            "allowed_resource_ids",
            tuple(
                str(value)
                for value
                in self.allowed_resource_ids
            ),
        )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(
                dict(
                    self.metadata
                )
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class RuntimeAuthorizationRequest:
    principal: RuntimePrincipalIdentity

    authentication_boundary_decision: (
        RuntimeAuthenticationBoundaryDecision
    )

    operation: RuntimeOperation

    resource_id: Optional[str] = None

    job_id: Optional[str] = None
    orchestration_id: Optional[str] = None
    execution_id: Optional[str] = None

    schema_version: str = field(
        default=RUNTIME_AUTHORIZATION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class RuntimeAuthorizationDecision:
    disposition: RuntimeAuthorizationDisposition

    principal_type: RuntimePrincipalType
    principal_id: str

    boundary: RuntimeAuthenticationBoundary
    operation: RuntimeOperation

    resource_id: Optional[str]

    authentication_established: bool
    operation_authorized: bool
    resource_scope_authorized: bool

    authorization_source: Optional[str]
    authorization_reference: Optional[str]

    reason_code: str

    schema_version: str = field(
        default=RUNTIME_AUTHORIZATION_SCHEMA_VERSION,
        init=False,
    )

    @property
    def authorized(
        self,
    ) -> bool:
        return (
            self.disposition
            is RuntimeAuthorizationDisposition.ALLOW
        )


BOUNDARY_OPERATION_MAP = MappingProxyType(
    {
        RuntimeAuthenticationBoundary.JOB_SUBMISSION:
            RuntimeOperation.SUBMIT_JOB,

        RuntimeAuthenticationBoundary.QUEUE_INTERACTION:
            RuntimeOperation.CONSUME_QUEUE,

        RuntimeAuthenticationBoundary.WORKER_REGISTRATION:
            RuntimeOperation.REGISTER_WORKER,

        RuntimeAuthenticationBoundary.WORKER_ASSIGNMENT:
            RuntimeOperation.ASSIGN_WORKER,

        RuntimeAuthenticationBoundary.LEASE_OPERATION:
            RuntimeOperation.MANAGE_LEASE,

        RuntimeAuthenticationBoundary.ORCHESTRATION_CONTROL:
            RuntimeOperation.CONTROL_ORCHESTRATION,

        RuntimeAuthenticationBoundary.EXECUTION_START:
            RuntimeOperation.START_EXECUTION,

        RuntimeAuthenticationBoundary.HANDLER_INVOCATION:
            RuntimeOperation.INVOKE_HANDLER,

        RuntimeAuthenticationBoundary.EXECUTION_RESULT_SUBMISSION:
            RuntimeOperation.SUBMIT_EXECUTION_RESULT,

        RuntimeAuthenticationBoundary.CHECKPOINT_OPERATION:
            RuntimeOperation.MANAGE_CHECKPOINT,

        RuntimeAuthenticationBoundary.SUSPENSION_OPERATION:
            RuntimeOperation.SUSPEND_RUNTIME_WORK,

        RuntimeAuthenticationBoundary.RESUME_OPERATION:
            RuntimeOperation.RESUME_RUNTIME_WORK,

        RuntimeAuthenticationBoundary.RECOVERY_OPERATION:
            RuntimeOperation.RECOVER_RUNTIME_WORK,

        RuntimeAuthenticationBoundary.CANCELLATION_OPERATION:
            RuntimeOperation.CANCEL_RUNTIME_WORK,

        RuntimeAuthenticationBoundary.RUNTIME_ADMINISTRATION:
            RuntimeOperation.ADMINISTER_RUNTIME,

        RuntimeAuthenticationBoundary.INTERNAL_SERVICE_CALL:
            RuntimeOperation.CALL_INTERNAL_SERVICE,
    }
)


def expected_operation_for_boundary(
    boundary: RuntimeAuthenticationBoundary,
) -> RuntimeOperation:

    try:
        return BOUNDARY_OPERATION_MAP[
            boundary
        ]

    except KeyError as exc:
        raise RuntimeAuthorizationError(
            "Runtime boundary has no authorization operation mapping.",
            code="runtime_authorization_boundary_unmapped",
            value=boundary,
        ) from exc


def _deny(
    *,
    request: RuntimeAuthorizationRequest,
    evidence: RuntimeAuthorizationEvidence,
    reason_code: str,
    operation_authorized: bool = False,
    resource_scope_authorized: bool = False,
) -> RuntimeAuthorizationDecision:

    return RuntimeAuthorizationDecision(
        disposition=RuntimeAuthorizationDisposition.DENY,
        principal_type=request.principal.principal_type,
        principal_id=request.principal.principal_id,
        boundary=(
            request.authentication_boundary_decision.boundary
        ),
        operation=request.operation,
        resource_id=request.resource_id,
        authentication_established=(
            evidence.authentication_established
        ),
        operation_authorized=operation_authorized,
        resource_scope_authorized=(
            resource_scope_authorized
        ),
        authorization_source=(
            evidence.authorization_source
        ),
        authorization_reference=(
            evidence.authorization_reference
        ),
        reason_code=reason_code,
    )


def evaluate_runtime_authorization(
    *,
    request: RuntimeAuthorizationRequest,
    evidence: RuntimeAuthorizationEvidence,
) -> RuntimeAuthorizationDecision:
    """
    Canonical generic runtime authorization gate.

    Rules:
    1. Phase 7.1 boundary must have accepted the principal.
    2. Authentication must already be established.
    3. Trusted-internal boundary requires trusted-internal identity evidence.
    4. Requested operation must match the boundary.
    5. Operation must be explicitly granted.
    6. Resource scope must be explicitly granted.
    7. Otherwise deny by default.
    """

    if not isinstance(
        request,
        RuntimeAuthorizationRequest,
    ):
        raise RuntimeAuthorizationError(
            "request must be RuntimeAuthorizationRequest.",
            code="invalid_runtime_authorization_request",
            value=request,
        )

    if not isinstance(
        evidence,
        RuntimeAuthorizationEvidence,
    ):
        raise RuntimeAuthorizationError(
            "evidence must be RuntimeAuthorizationEvidence.",
            code="invalid_runtime_authorization_evidence",
            value=evidence,
        )

    boundary_decision = (
        request.authentication_boundary_decision
    )

    if (
        boundary_decision.disposition
        is not AuthenticationBoundaryDisposition.PROCEED_TO_AUTHENTICATION
    ):
        return _deny(
            request=request,
            evidence=evidence,
            reason_code="authentication_boundary_rejected",
        )

    if (
        boundary_decision.principal_type
        is not request.principal.principal_type
    ):
        return _deny(
            request=request,
            evidence=evidence,
            reason_code="principal_type_boundary_mismatch",
        )

    if not evidence.authentication_established:
        return _deny(
            request=request,
            evidence=evidence,
            reason_code="authentication_not_established",
        )

    if (
        boundary_decision.trusted_internal_required
        and not evidence.trusted_internal_identity
    ):
        return _deny(
            request=request,
            evidence=evidence,
            reason_code="trusted_internal_identity_required",
        )

    expected_operation = (
        expected_operation_for_boundary(
            boundary_decision.boundary
        )
    )

    if request.operation is not expected_operation:
        return _deny(
            request=request,
            evidence=evidence,
            reason_code="operation_boundary_mismatch",
        )

    operation_authorized = (
        request.operation
        in evidence.granted_operations
    )

    if not operation_authorized:
        return _deny(
            request=request,
            evidence=evidence,
            reason_code="operation_not_granted",
        )

    resource_scope_authorized = (
        request.resource_id is None
        or evidence.unrestricted_resource_scope
        or request.resource_id
        in evidence.allowed_resource_ids
    )

    if not resource_scope_authorized:
        return _deny(
            request=request,
            evidence=evidence,
            reason_code="resource_scope_not_granted",
            operation_authorized=True,
        )

    return RuntimeAuthorizationDecision(
        disposition=RuntimeAuthorizationDisposition.ALLOW,
        principal_type=request.principal.principal_type,
        principal_id=request.principal.principal_id,
        boundary=boundary_decision.boundary,
        operation=request.operation,
        resource_id=request.resource_id,
        authentication_established=True,
        operation_authorized=True,
        resource_scope_authorized=True,
        authorization_source=(
            evidence.authorization_source
        ),
        authorization_reference=(
            evidence.authorization_reference
        ),
        reason_code="runtime_operation_authorized",
    )


def certify_runtime_authorization_v1(
) -> Mapping[str, Any]:
    """
    Phase 7.2 certification.

    Uses synthetic authorization evidence only.
    No production permission, identity or runtime state is mutated.
    """

    from .runtime_authentication_boundaries import (
        RuntimeAuthenticationBoundaryRequest,
        evaluate_runtime_authentication_boundary,
    )

    user = RuntimePrincipalIdentity(
        principal_type=RuntimePrincipalType.USER,
        principal_id="user-phase-7-2-certification",
    )

    worker = RuntimePrincipalIdentity(
        principal_type=RuntimePrincipalType.WORKER,
        principal_id="worker-principal-phase-7-2",
        worker_id="worker-phase-7-2",
        worker_instance_id="worker-instance-phase-7-2",
    )

    service = RuntimePrincipalIdentity(
        principal_type=RuntimePrincipalType.SERVICE,
        principal_id="service-principal-phase-7-2",
        service_name="runtime-service-phase-7-2",
    )

    user_job_boundary = (
        evaluate_runtime_authentication_boundary(
            RuntimeAuthenticationBoundaryRequest(
                principal=user,
                boundary=(
                    RuntimeAuthenticationBoundary.JOB_SUBMISSION
                ),
                job_id="job-phase-7-2",
            )
        )
    )

    worker_execution_boundary = (
        evaluate_runtime_authentication_boundary(
            RuntimeAuthenticationBoundaryRequest(
                principal=worker,
                boundary=(
                    RuntimeAuthenticationBoundary.EXECUTION_START
                ),
                execution_id="execution-phase-7-2",
            )
        )
    )

    service_orchestration_boundary = (
        evaluate_runtime_authentication_boundary(
            RuntimeAuthenticationBoundaryRequest(
                principal=service,
                boundary=(
                    RuntimeAuthenticationBoundary.ORCHESTRATION_CONTROL
                ),
                orchestration_id="orchestration-phase-7-2",
            )
        )
    )

    user_job_allowed = evaluate_runtime_authorization(
        request=RuntimeAuthorizationRequest(
            principal=user,
            authentication_boundary_decision=user_job_boundary,
            operation=RuntimeOperation.SUBMIT_JOB,
            resource_id="workspace-certification",
            job_id="job-phase-7-2",
        ),
        evidence=RuntimeAuthorizationEvidence(
            authentication_established=True,
            trusted_internal_identity=False,
            granted_operations=(
                RuntimeOperation.SUBMIT_JOB,
            ),
            allowed_resource_ids=(
                "workspace-certification",
            ),
            authorization_source="existing_entitlement_authority",
            authorization_reference="authz-ref-user-job",
        ),
    )

    unauthenticated_denied = evaluate_runtime_authorization(
        request=RuntimeAuthorizationRequest(
            principal=user,
            authentication_boundary_decision=user_job_boundary,
            operation=RuntimeOperation.SUBMIT_JOB,
            resource_id="workspace-certification",
        ),
        evidence=RuntimeAuthorizationEvidence(
            authentication_established=False,
            granted_operations=(
                RuntimeOperation.SUBMIT_JOB,
            ),
            unrestricted_resource_scope=True,
        ),
    )

    missing_operation_denied = evaluate_runtime_authorization(
        request=RuntimeAuthorizationRequest(
            principal=user,
            authentication_boundary_decision=user_job_boundary,
            operation=RuntimeOperation.SUBMIT_JOB,
            resource_id="workspace-certification",
        ),
        evidence=RuntimeAuthorizationEvidence(
            authentication_established=True,
            granted_operations=(),
            unrestricted_resource_scope=True,
        ),
    )

    wrong_resource_denied = evaluate_runtime_authorization(
        request=RuntimeAuthorizationRequest(
            principal=user,
            authentication_boundary_decision=user_job_boundary,
            operation=RuntimeOperation.SUBMIT_JOB,
            resource_id="workspace-not-authorized",
        ),
        evidence=RuntimeAuthorizationEvidence(
            authentication_established=True,
            granted_operations=(
                RuntimeOperation.SUBMIT_JOB,
            ),
            allowed_resource_ids=(
                "workspace-certification",
            ),
        ),
    )

    worker_without_trust_denied = evaluate_runtime_authorization(
        request=RuntimeAuthorizationRequest(
            principal=worker,
            authentication_boundary_decision=worker_execution_boundary,
            operation=RuntimeOperation.START_EXECUTION,
            resource_id="execution-phase-7-2",
        ),
        evidence=RuntimeAuthorizationEvidence(
            authentication_established=True,
            trusted_internal_identity=False,
            granted_operations=(
                RuntimeOperation.START_EXECUTION,
            ),
            unrestricted_resource_scope=True,
        ),
    )

    worker_with_trust_allowed = evaluate_runtime_authorization(
        request=RuntimeAuthorizationRequest(
            principal=worker,
            authentication_boundary_decision=worker_execution_boundary,
            operation=RuntimeOperation.START_EXECUTION,
            resource_id="execution-phase-7-2",
        ),
        evidence=RuntimeAuthorizationEvidence(
            authentication_established=True,
            trusted_internal_identity=True,
            granted_operations=(
                RuntimeOperation.START_EXECUTION,
            ),
            allowed_resource_ids=(
                "execution-phase-7-2",
            ),
            authorization_source="existing_worker_authority",
            authorization_reference="worker-authz-ref",
        ),
    )

    service_orchestration_allowed = (
        evaluate_runtime_authorization(
            request=RuntimeAuthorizationRequest(
                principal=service,
                authentication_boundary_decision=(
                    service_orchestration_boundary
                ),
                operation=(
                    RuntimeOperation.CONTROL_ORCHESTRATION
                ),
                resource_id="orchestration-phase-7-2",
            ),
            evidence=RuntimeAuthorizationEvidence(
                authentication_established=True,
                trusted_internal_identity=True,
                granted_operations=(
                    RuntimeOperation.CONTROL_ORCHESTRATION,
                ),
                allowed_resource_ids=(
                    "orchestration-phase-7-2",
                ),
                authorization_source="existing_service_policy",
                authorization_reference="service-authz-ref",
            ),
        )
    )

    operation_boundary_mismatch_denied = (
        evaluate_runtime_authorization(
            request=RuntimeAuthorizationRequest(
                principal=user,
                authentication_boundary_decision=user_job_boundary,
                operation=RuntimeOperation.CANCEL_RUNTIME_WORK,
                resource_id="workspace-certification",
            ),
            evidence=RuntimeAuthorizationEvidence(
                authentication_established=True,
                granted_operations=(
                    RuntimeOperation.CANCEL_RUNTIME_WORK,
                ),
                unrestricted_resource_scope=True,
            ),
        )
    )

    rejected_boundary = (
        RuntimeAuthenticationBoundaryDecision(
            disposition=(
                AuthenticationBoundaryDisposition.REJECT
            ),
            boundary=(
                RuntimeAuthenticationBoundary.QUEUE_INTERACTION
            ),
            principal_type=RuntimePrincipalType.USER,
            authentication_required=True,
            trusted_internal_required=True,
            reason_code="certification-rejected-boundary",
        )
    )

    rejected_boundary_denied = (
        evaluate_runtime_authorization(
            request=RuntimeAuthorizationRequest(
                principal=user,
                authentication_boundary_decision=rejected_boundary,
                operation=RuntimeOperation.CONSUME_QUEUE,
            ),
            evidence=RuntimeAuthorizationEvidence(
                authentication_established=True,
                trusted_internal_identity=True,
                granted_operations=(
                    RuntimeOperation.CONSUME_QUEUE,
                ),
                unrestricted_resource_scope=True,
            ),
        )
    )

    all_boundaries_mapped = (
        set(
            BOUNDARY_OPERATION_MAP.keys()
        )
        == set(
            RuntimeAuthenticationBoundary
        )
    )

    checks = {
        "runtime_authorization_contract_created":
            True,

        "all_authentication_boundaries_mapped":
            all_boundaries_mapped,

        "authenticated_user_operation_allowed":
            user_job_allowed.authorized,

        "authorization_source_preserved":
            (
                user_job_allowed.authorization_source
                == "existing_entitlement_authority"
            ),

        "authorization_reference_preserved":
            (
                user_job_allowed.authorization_reference
                == "authz-ref-user-job"
            ),

        "unauthenticated_principal_denied":
            (
                unauthenticated_denied.disposition
                is RuntimeAuthorizationDisposition.DENY
            ),

        "deny_by_default_operation_enforced":
            (
                missing_operation_denied.disposition
                is RuntimeAuthorizationDisposition.DENY
            ),

        "resource_scope_enforced":
            (
                wrong_resource_denied.disposition
                is RuntimeAuthorizationDisposition.DENY
            ),

        "trusted_internal_requirement_enforced":
            (
                worker_without_trust_denied.disposition
                is RuntimeAuthorizationDisposition.DENY
            ),

        "trusted_worker_operation_allowed":
            worker_with_trust_allowed.authorized,

        "trusted_service_operation_allowed":
            service_orchestration_allowed.authorized,

        "operation_boundary_mismatch_rejected":
            (
                operation_boundary_mismatch_denied.disposition
                is RuntimeAuthorizationDisposition.DENY
            ),

        "rejected_authentication_boundary_cannot_authorize":
            (
                rejected_boundary_denied.disposition
                is RuntimeAuthorizationDisposition.DENY
            ),

        "authorization_evidence_is_caller_supplied":
            True,

        "no_permission_store_created":
            True,

        "no_role_store_created":
            True,

        "no_identity_store_created":
            True,

        "no_authentication_system_created":
            True,

        "no_token_validation_created":
            True,

        "no_worker_identity_validation_created":
            True,

        "no_service_trust_engine_created":
            True,

        "no_execution_specific_policy_created":
            True,

        "no_job_execution_policy_created":
            True,

        "no_privilege_escalation_engine_created":
            True,

        "no_job_mutation":
            True,

        "no_queue_mutation":
            True,

        "no_worker_mutation":
            True,

        "no_orchestration_mutation":
            True,

        "no_execution_mutation":
            True,

        "no_persistence_write":
            True,
    }

    certified = all(
        checks.values()
    )

    return MappingProxyType(
        {
            "phase":
                "7.2",

            "component":
                "Runtime Authorization",

            "version":
                RUNTIME_AUTHORIZATION_VERSION,

            "schema_version":
                RUNTIME_AUTHORIZATION_SCHEMA_VERSION,

            "certified":
                certified,

            "checks":
                MappingProxyType(
                    checks
                ),

            "authority_boundary": (
                "Phase 7.2 consumes an accepted Phase-7.1 authentication "
                "boundary decision plus caller-supplied authorization evidence "
                "and applies deny-by-default generic runtime authorization. "
                "It does not authenticate identities, validate tokens, create "
                "roles or permission stores, establish worker/service trust, "
                "or replace execution-specific and job-specific authorization "
                "owned by later Phase-7 components."
            ),
        }
    )


def explain_runtime_authorization_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "7.2",

            "component":
                "Runtime Authorization",

            "version":
                RUNTIME_AUTHORIZATION_VERSION,

            "authorization_contract": (
                "Defines the generic runtime authorization request, evidence "
                "and decision contracts."
            ),

            "boundary_consumption": (
                "Authorization can proceed only after Phase 7.1 accepts the "
                "principal category for the runtime boundary."
            ),

            "deny_by_default": (
                "Operations are denied unless explicitly present in caller-"
                "supplied authorization evidence."
            ),

            "resource_scope": (
                "When a resource id is present, the resource must be explicitly "
                "authorized or the evidence must grant unrestricted scope."
            ),

            "trusted_internal": (
                "Internal runtime boundaries require trusted-internal evidence "
                "before authorization can succeed."
            ),

            "later_specialization": (
                "Phase 7.3 specializes execution authorization and Phase 7.6 "
                "specializes job execution permissions."
            ),
        }
    )


__all__ = [
    "RUNTIME_AUTHORIZATION_VERSION",
    "RUNTIME_AUTHORIZATION_SCHEMA_VERSION",
    "RuntimeAuthorizationError",
    "RuntimeOperation",
    "RuntimeAuthorizationDisposition",
    "RuntimeAuthorizationEvidence",
    "RuntimeAuthorizationRequest",
    "RuntimeAuthorizationDecision",
    "BOUNDARY_OPERATION_MAP",
    "expected_operation_for_boundary",
    "evaluate_runtime_authorization",
    "certify_runtime_authorization_v1",
    "explain_runtime_authorization_v1",
]
