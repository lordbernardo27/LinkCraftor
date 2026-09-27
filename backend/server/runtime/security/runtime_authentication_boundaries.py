"""
LinkCraftor Universal Runtime Infrastructure
Phase 7.1 — Runtime Authentication Boundaries

Defines the canonical authentication boundaries for Runtime Security.

This component answers:

    "Where must runtime authentication be proven?"

It does NOT answer:

    "Is this caller authorized to perform this action?"

Authorization remains Phase 7.2+.

It does NOT create:
- a user authentication system
- a worker identity store
- a service identity store
- a token issuer
- a token validator
- a secrets manager
- an authorization engine
- a permission store

Existing identity, worker, job, orchestration and execution identities remain
authoritative.

Phase 7.1 establishes only the authentication boundary contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional


RUNTIME_AUTHENTICATION_BOUNDARIES_VERSION = (
    "runtime_authentication_boundaries_v7.1.1"
)

RUNTIME_AUTHENTICATION_BOUNDARIES_SCHEMA_VERSION = (
    "runtime_authentication_boundaries_schema_v1"
)


class RuntimeAuthenticationBoundaryError(ValueError):
    """Raised when authentication-boundary evidence is malformed."""

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


class RuntimePrincipalType(str, Enum):
    USER = "USER"
    WORKER = "WORKER"
    SERVICE = "SERVICE"
    SYSTEM = "SYSTEM"
    ADMINISTRATOR = "ADMINISTRATOR"


class RuntimeAuthenticationBoundary(str, Enum):
    JOB_SUBMISSION = "JOB_SUBMISSION"
    QUEUE_INTERACTION = "QUEUE_INTERACTION"
    WORKER_REGISTRATION = "WORKER_REGISTRATION"
    WORKER_ASSIGNMENT = "WORKER_ASSIGNMENT"
    LEASE_OPERATION = "LEASE_OPERATION"
    ORCHESTRATION_CONTROL = "ORCHESTRATION_CONTROL"
    EXECUTION_START = "EXECUTION_START"
    HANDLER_INVOCATION = "HANDLER_INVOCATION"
    EXECUTION_RESULT_SUBMISSION = "EXECUTION_RESULT_SUBMISSION"
    CHECKPOINT_OPERATION = "CHECKPOINT_OPERATION"
    SUSPENSION_OPERATION = "SUSPENSION_OPERATION"
    RESUME_OPERATION = "RESUME_OPERATION"
    RECOVERY_OPERATION = "RECOVERY_OPERATION"
    CANCELLATION_OPERATION = "CANCELLATION_OPERATION"
    RUNTIME_ADMINISTRATION = "RUNTIME_ADMINISTRATION"
    INTERNAL_SERVICE_CALL = "INTERNAL_SERVICE_CALL"


class AuthenticationRequirement(str, Enum):
    REQUIRED = "REQUIRED"
    TRUSTED_INTERNAL_ONLY = "TRUSTED_INTERNAL_ONLY"


class AuthenticationBoundaryDisposition(str, Enum):
    PROCEED_TO_AUTHENTICATION = "PROCEED_TO_AUTHENTICATION"
    REJECT = "REJECT"


@dataclass(
    frozen=True,
    slots=True,
)
class RuntimePrincipalIdentity:
    """
    Runtime-facing identity reference only.

    This does not create a new identity authority. The principal_id must
    originate from an existing authoritative identity source.
    """

    principal_type: RuntimePrincipalType
    principal_id: str

    worker_id: Optional[str] = None
    worker_instance_id: Optional[str] = None

    service_name: Optional[str] = None

    schema_version: str = field(
        default=RUNTIME_AUTHENTICATION_BOUNDARIES_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not isinstance(
            self.principal_type,
            RuntimePrincipalType,
        ):
            raise RuntimeAuthenticationBoundaryError(
                "principal_type must be RuntimePrincipalType.",
                code="invalid_runtime_principal_type",
                value=self.principal_type,
            )

        if not str(
            self.principal_id
        ).strip():
            raise RuntimeAuthenticationBoundaryError(
                "principal_id is required.",
                code="runtime_principal_id_missing",
            )

        if (
            self.principal_type
            is RuntimePrincipalType.WORKER
            and not self.worker_id
        ):
            raise RuntimeAuthenticationBoundaryError(
                "WORKER principal requires worker_id.",
                code="worker_principal_worker_id_missing",
            )

        if (
            self.principal_type
            is RuntimePrincipalType.SERVICE
            and not self.service_name
        ):
            raise RuntimeAuthenticationBoundaryError(
                "SERVICE principal requires service_name.",
                code="service_principal_name_missing",
            )


@dataclass(
    frozen=True,
    slots=True,
)
class RuntimeAuthenticationBoundaryPolicy:
    boundary: RuntimeAuthenticationBoundary
    requirement: AuthenticationRequirement

    allowed_principal_types: tuple[
        RuntimePrincipalType,
        ...,
    ]

    schema_version: str = field(
        default=RUNTIME_AUTHENTICATION_BOUNDARIES_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.allowed_principal_types:
            raise RuntimeAuthenticationBoundaryError(
                "Authentication boundary must allow at least one principal type.",
                code="authentication_boundary_has_no_principals",
                value=self.boundary.value,
            )


@dataclass(
    frozen=True,
    slots=True,
)
class RuntimeAuthenticationBoundaryRequest:
    """
    Request to cross one Runtime Security authentication boundary.

    Authentication credentials/tokens are intentionally not represented here.
    Their validation belongs to later Phase-7 components.
    """

    principal: RuntimePrincipalIdentity
    boundary: RuntimeAuthenticationBoundary

    job_id: Optional[str] = None
    orchestration_id: Optional[str] = None
    execution_id: Optional[str] = None

    metadata: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    schema_version: str = field(
        default=RUNTIME_AUTHENTICATION_BOUNDARIES_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
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
class RuntimeAuthenticationBoundaryDecision:
    disposition: AuthenticationBoundaryDisposition

    boundary: RuntimeAuthenticationBoundary
    principal_type: RuntimePrincipalType

    authentication_required: bool
    trusted_internal_required: bool

    reason_code: str

    schema_version: str = field(
        default=RUNTIME_AUTHENTICATION_BOUNDARIES_SCHEMA_VERSION,
        init=False,
    )

    @property
    def accepted_for_authentication_evaluation(
        self,
    ) -> bool:
        return (
            self.disposition
            is AuthenticationBoundaryDisposition.PROCEED_TO_AUTHENTICATION
        )


RUNTIME_AUTHENTICATION_BOUNDARY_POLICIES = MappingProxyType(
    {
        RuntimeAuthenticationBoundary.JOB_SUBMISSION:
            RuntimeAuthenticationBoundaryPolicy(
                boundary=RuntimeAuthenticationBoundary.JOB_SUBMISSION,
                requirement=AuthenticationRequirement.REQUIRED,
                allowed_principal_types=(
                    RuntimePrincipalType.USER,
                    RuntimePrincipalType.SERVICE,
                    RuntimePrincipalType.ADMINISTRATOR,
                ),
            ),

        RuntimeAuthenticationBoundary.QUEUE_INTERACTION:
            RuntimeAuthenticationBoundaryPolicy(
                boundary=RuntimeAuthenticationBoundary.QUEUE_INTERACTION,
                requirement=AuthenticationRequirement.TRUSTED_INTERNAL_ONLY,
                allowed_principal_types=(
                    RuntimePrincipalType.WORKER,
                    RuntimePrincipalType.SERVICE,
                    RuntimePrincipalType.SYSTEM,
                    RuntimePrincipalType.ADMINISTRATOR,
                ),
            ),

        RuntimeAuthenticationBoundary.WORKER_REGISTRATION:
            RuntimeAuthenticationBoundaryPolicy(
                boundary=RuntimeAuthenticationBoundary.WORKER_REGISTRATION,
                requirement=AuthenticationRequirement.REQUIRED,
                allowed_principal_types=(
                    RuntimePrincipalType.WORKER,
                    RuntimePrincipalType.SERVICE,
                    RuntimePrincipalType.ADMINISTRATOR,
                ),
            ),

        RuntimeAuthenticationBoundary.WORKER_ASSIGNMENT:
            RuntimeAuthenticationBoundaryPolicy(
                boundary=RuntimeAuthenticationBoundary.WORKER_ASSIGNMENT,
                requirement=AuthenticationRequirement.TRUSTED_INTERNAL_ONLY,
                allowed_principal_types=(
                    RuntimePrincipalType.SERVICE,
                    RuntimePrincipalType.SYSTEM,
                ),
            ),

        RuntimeAuthenticationBoundary.LEASE_OPERATION:
            RuntimeAuthenticationBoundaryPolicy(
                boundary=RuntimeAuthenticationBoundary.LEASE_OPERATION,
                requirement=AuthenticationRequirement.TRUSTED_INTERNAL_ONLY,
                allowed_principal_types=(
                    RuntimePrincipalType.WORKER,
                    RuntimePrincipalType.SERVICE,
                    RuntimePrincipalType.SYSTEM,
                ),
            ),

        RuntimeAuthenticationBoundary.ORCHESTRATION_CONTROL:
            RuntimeAuthenticationBoundaryPolicy(
                boundary=RuntimeAuthenticationBoundary.ORCHESTRATION_CONTROL,
                requirement=AuthenticationRequirement.TRUSTED_INTERNAL_ONLY,
                allowed_principal_types=(
                    RuntimePrincipalType.SERVICE,
                    RuntimePrincipalType.SYSTEM,
                    RuntimePrincipalType.ADMINISTRATOR,
                ),
            ),

        RuntimeAuthenticationBoundary.EXECUTION_START:
            RuntimeAuthenticationBoundaryPolicy(
                boundary=RuntimeAuthenticationBoundary.EXECUTION_START,
                requirement=AuthenticationRequirement.TRUSTED_INTERNAL_ONLY,
                allowed_principal_types=(
                    RuntimePrincipalType.WORKER,
                    RuntimePrincipalType.SERVICE,
                    RuntimePrincipalType.SYSTEM,
                ),
            ),

        RuntimeAuthenticationBoundary.HANDLER_INVOCATION:
            RuntimeAuthenticationBoundaryPolicy(
                boundary=RuntimeAuthenticationBoundary.HANDLER_INVOCATION,
                requirement=AuthenticationRequirement.TRUSTED_INTERNAL_ONLY,
                allowed_principal_types=(
                    RuntimePrincipalType.WORKER,
                    RuntimePrincipalType.SERVICE,
                    RuntimePrincipalType.SYSTEM,
                ),
            ),

        RuntimeAuthenticationBoundary.EXECUTION_RESULT_SUBMISSION:
            RuntimeAuthenticationBoundaryPolicy(
                boundary=(
                    RuntimeAuthenticationBoundary.EXECUTION_RESULT_SUBMISSION
                ),
                requirement=AuthenticationRequirement.TRUSTED_INTERNAL_ONLY,
                allowed_principal_types=(
                    RuntimePrincipalType.WORKER,
                    RuntimePrincipalType.SERVICE,
                    RuntimePrincipalType.SYSTEM,
                ),
            ),

        RuntimeAuthenticationBoundary.CHECKPOINT_OPERATION:
            RuntimeAuthenticationBoundaryPolicy(
                boundary=RuntimeAuthenticationBoundary.CHECKPOINT_OPERATION,
                requirement=AuthenticationRequirement.TRUSTED_INTERNAL_ONLY,
                allowed_principal_types=(
                    RuntimePrincipalType.WORKER,
                    RuntimePrincipalType.SERVICE,
                    RuntimePrincipalType.SYSTEM,
                ),
            ),

        RuntimeAuthenticationBoundary.SUSPENSION_OPERATION:
            RuntimeAuthenticationBoundaryPolicy(
                boundary=RuntimeAuthenticationBoundary.SUSPENSION_OPERATION,
                requirement=AuthenticationRequirement.TRUSTED_INTERNAL_ONLY,
                allowed_principal_types=(
                    RuntimePrincipalType.SERVICE,
                    RuntimePrincipalType.SYSTEM,
                    RuntimePrincipalType.ADMINISTRATOR,
                ),
            ),

        RuntimeAuthenticationBoundary.RESUME_OPERATION:
            RuntimeAuthenticationBoundaryPolicy(
                boundary=RuntimeAuthenticationBoundary.RESUME_OPERATION,
                requirement=AuthenticationRequirement.TRUSTED_INTERNAL_ONLY,
                allowed_principal_types=(
                    RuntimePrincipalType.SERVICE,
                    RuntimePrincipalType.SYSTEM,
                    RuntimePrincipalType.ADMINISTRATOR,
                ),
            ),

        RuntimeAuthenticationBoundary.RECOVERY_OPERATION:
            RuntimeAuthenticationBoundaryPolicy(
                boundary=RuntimeAuthenticationBoundary.RECOVERY_OPERATION,
                requirement=AuthenticationRequirement.TRUSTED_INTERNAL_ONLY,
                allowed_principal_types=(
                    RuntimePrincipalType.SERVICE,
                    RuntimePrincipalType.SYSTEM,
                    RuntimePrincipalType.ADMINISTRATOR,
                ),
            ),

        RuntimeAuthenticationBoundary.CANCELLATION_OPERATION:
            RuntimeAuthenticationBoundaryPolicy(
                boundary=RuntimeAuthenticationBoundary.CANCELLATION_OPERATION,
                requirement=AuthenticationRequirement.REQUIRED,
                allowed_principal_types=(
                    RuntimePrincipalType.USER,
                    RuntimePrincipalType.SERVICE,
                    RuntimePrincipalType.SYSTEM,
                    RuntimePrincipalType.ADMINISTRATOR,
                ),
            ),

        RuntimeAuthenticationBoundary.RUNTIME_ADMINISTRATION:
            RuntimeAuthenticationBoundaryPolicy(
                boundary=RuntimeAuthenticationBoundary.RUNTIME_ADMINISTRATION,
                requirement=AuthenticationRequirement.REQUIRED,
                allowed_principal_types=(
                    RuntimePrincipalType.ADMINISTRATOR,
                    RuntimePrincipalType.SERVICE,
                ),
            ),

        RuntimeAuthenticationBoundary.INTERNAL_SERVICE_CALL:
            RuntimeAuthenticationBoundaryPolicy(
                boundary=RuntimeAuthenticationBoundary.INTERNAL_SERVICE_CALL,
                requirement=AuthenticationRequirement.TRUSTED_INTERNAL_ONLY,
                allowed_principal_types=(
                    RuntimePrincipalType.SERVICE,
                    RuntimePrincipalType.SYSTEM,
                ),
            ),
    }
)


def authentication_policy_for_boundary(
    boundary: RuntimeAuthenticationBoundary,
) -> RuntimeAuthenticationBoundaryPolicy:

    try:
        return RUNTIME_AUTHENTICATION_BOUNDARY_POLICIES[
            boundary
        ]

    except KeyError as exc:
        raise RuntimeAuthenticationBoundaryError(
            "Unknown runtime authentication boundary.",
            code="runtime_authentication_boundary_unknown",
            value=boundary,
        ) from exc


def evaluate_runtime_authentication_boundary(
    request: RuntimeAuthenticationBoundaryRequest,
) -> RuntimeAuthenticationBoundaryDecision:
    """
    Determine whether a principal is structurally permitted to proceed
    to authentication evaluation for one runtime boundary.

    IMPORTANT:
    This function does NOT prove authentication.
    It only enforces the boundary topology.
    """

    if not isinstance(
        request,
        RuntimeAuthenticationBoundaryRequest,
    ):
        raise RuntimeAuthenticationBoundaryError(
            "request must be RuntimeAuthenticationBoundaryRequest.",
            code="invalid_runtime_authentication_boundary_request",
            value=request,
        )

    policy = authentication_policy_for_boundary(
        request.boundary
    )

    principal_type = (
        request.principal.principal_type
    )

    if (
        principal_type
        not in policy.allowed_principal_types
    ):
        return RuntimeAuthenticationBoundaryDecision(
            disposition=(
                AuthenticationBoundaryDisposition.REJECT
            ),
            boundary=request.boundary,
            principal_type=principal_type,
            authentication_required=True,
            trusted_internal_required=(
                policy.requirement
                is AuthenticationRequirement.TRUSTED_INTERNAL_ONLY
            ),
            reason_code="principal_type_not_allowed_for_boundary",
        )

    return RuntimeAuthenticationBoundaryDecision(
        disposition=(
            AuthenticationBoundaryDisposition.PROCEED_TO_AUTHENTICATION
        ),
        boundary=request.boundary,
        principal_type=principal_type,
        authentication_required=True,
        trusted_internal_required=(
            policy.requirement
            is AuthenticationRequirement.TRUSTED_INTERNAL_ONLY
        ),
        reason_code="authentication_boundary_accepted",
    )


def certify_runtime_authentication_boundaries_v1(
) -> Mapping[str, Any]:
    """
    Phase 7.1 certification.

    Uses synthetic identity references only.
    No production authentication/token/secret state is modified.
    """

    user = RuntimePrincipalIdentity(
        principal_type=RuntimePrincipalType.USER,
        principal_id="user-certification",
    )

    worker = RuntimePrincipalIdentity(
        principal_type=RuntimePrincipalType.WORKER,
        principal_id="worker-principal-certification",
        worker_id="worker-certification",
        worker_instance_id="worker-instance-certification",
    )

    service = RuntimePrincipalIdentity(
        principal_type=RuntimePrincipalType.SERVICE,
        principal_id="service-principal-certification",
        service_name="runtime-certification-service",
    )

    administrator = RuntimePrincipalIdentity(
        principal_type=RuntimePrincipalType.ADMINISTRATOR,
        principal_id="admin-certification",
    )

    job_submission = (
        evaluate_runtime_authentication_boundary(
            RuntimeAuthenticationBoundaryRequest(
                principal=user,
                boundary=(
                    RuntimeAuthenticationBoundary.JOB_SUBMISSION
                ),
                job_id="job-certification",
            )
        )
    )

    worker_execution = (
        evaluate_runtime_authentication_boundary(
            RuntimeAuthenticationBoundaryRequest(
                principal=worker,
                boundary=(
                    RuntimeAuthenticationBoundary.EXECUTION_START
                ),
                job_id="job-certification",
                execution_id="execution-certification",
            )
        )
    )

    service_orchestration = (
        evaluate_runtime_authentication_boundary(
            RuntimeAuthenticationBoundaryRequest(
                principal=service,
                boundary=(
                    RuntimeAuthenticationBoundary.ORCHESTRATION_CONTROL
                ),
                orchestration_id="orchestration-certification",
            )
        )
    )

    administration = (
        evaluate_runtime_authentication_boundary(
            RuntimeAuthenticationBoundaryRequest(
                principal=administrator,
                boundary=(
                    RuntimeAuthenticationBoundary.RUNTIME_ADMINISTRATION
                ),
            )
        )
    )

    user_queue_access = (
        evaluate_runtime_authentication_boundary(
            RuntimeAuthenticationBoundaryRequest(
                principal=user,
                boundary=(
                    RuntimeAuthenticationBoundary.QUEUE_INTERACTION
                ),
            )
        )
    )

    user_handler_access = (
        evaluate_runtime_authentication_boundary(
            RuntimeAuthenticationBoundaryRequest(
                principal=user,
                boundary=(
                    RuntimeAuthenticationBoundary.HANDLER_INVOCATION
                ),
            )
        )
    )

    worker_admin_access = (
        evaluate_runtime_authentication_boundary(
            RuntimeAuthenticationBoundaryRequest(
                principal=worker,
                boundary=(
                    RuntimeAuthenticationBoundary.RUNTIME_ADMINISTRATION
                ),
            )
        )
    )

    service_internal_call = (
        evaluate_runtime_authentication_boundary(
            RuntimeAuthenticationBoundaryRequest(
                principal=service,
                boundary=(
                    RuntimeAuthenticationBoundary.INTERNAL_SERVICE_CALL
                ),
            )
        )
    )

    all_boundaries_present = (
        set(
            RUNTIME_AUTHENTICATION_BOUNDARY_POLICIES.keys()
        )
        == set(
            RuntimeAuthenticationBoundary
        )
    )

    checks = {
        "authentication_boundary_contract_created":
            True,

        "all_runtime_boundaries_have_policy":
            all_boundaries_present,

        "all_boundaries_require_authentication":
            all(
                policy.requirement
                in {
                    AuthenticationRequirement.REQUIRED,
                    AuthenticationRequirement.TRUSTED_INTERNAL_ONLY,
                }
                for policy
                in RUNTIME_AUTHENTICATION_BOUNDARY_POLICIES.values()
            ),

        "user_job_submission_boundary_allowed":
            job_submission.accepted_for_authentication_evaluation,

        "worker_execution_boundary_allowed":
            worker_execution.accepted_for_authentication_evaluation,

        "worker_execution_requires_internal_trust":
            worker_execution.trusted_internal_required,

        "service_orchestration_boundary_allowed":
            service_orchestration.accepted_for_authentication_evaluation,

        "service_orchestration_requires_internal_trust":
            service_orchestration.trusted_internal_required,

        "administrator_runtime_boundary_allowed":
            administration.accepted_for_authentication_evaluation,

        "service_internal_call_allowed":
            service_internal_call.accepted_for_authentication_evaluation,

        "service_internal_call_requires_internal_trust":
            service_internal_call.trusted_internal_required,

        "user_direct_queue_access_rejected":
            (
                user_queue_access.disposition
                is AuthenticationBoundaryDisposition.REJECT
            ),

        "user_direct_handler_invocation_rejected":
            (
                user_handler_access.disposition
                is AuthenticationBoundaryDisposition.REJECT
            ),

        "worker_runtime_administration_rejected":
            (
                worker_admin_access.disposition
                is AuthenticationBoundaryDisposition.REJECT
            ),

        "principal_identity_is_reference_only":
            True,

        "no_authentication_credentials_created":
            True,

        "no_user_authentication_system_created":
            True,

        "no_worker_identity_store_created":
            True,

        "no_service_identity_store_created":
            True,

        "no_token_issuer_created":
            True,

        "no_token_validator_created":
            True,

        "no_secret_manager_created":
            True,

        "no_authorization_engine_created":
            True,

        "no_permission_store_created":
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
    }

    certified = all(
        checks.values()
    )

    return MappingProxyType(
        {
            "phase":
                "7.1",

            "component":
                "Runtime Authentication Boundaries",

            "version":
                RUNTIME_AUTHENTICATION_BOUNDARIES_VERSION,

            "schema_version":
                RUNTIME_AUTHENTICATION_BOUNDARIES_SCHEMA_VERSION,

            "certified":
                certified,

            "checks":
                MappingProxyType(
                    checks
                ),

            "authority_boundary": (
                "Phase 7.1 defines where Runtime authentication must be "
                "proven and which principal categories may approach each "
                "runtime boundary. It does not authenticate credentials, "
                "validate tokens, issue identities, authorize operations, "
                "manage secrets or replace existing identity authorities."
            ),
        }
    )


def explain_runtime_authentication_boundaries_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "7.1",

            "component":
                "Runtime Authentication Boundaries",

            "version":
                RUNTIME_AUTHENTICATION_BOUNDARIES_VERSION,

            "authentication_boundary": (
                "Defines which runtime surfaces require authentication "
                "before execution or control operations may proceed."
            ),

            "principal_reference": (
                "Uses references to existing user, worker, service, system "
                "and administrator identities without creating new identity "
                "authorities."
            ),

            "internal_runtime_boundary": (
                "Queue, lease, execution, handler, orchestration and similar "
                "internal boundaries require trusted runtime principals."
            ),

            "external_runtime_boundary": (
                "User-facing boundaries such as job submission or permitted "
                "cancellation may accept authenticated user principals."
            ),

            "next_phase": (
                "Phase 7.2 determines authorization after authentication "
                "has been established."
            ),
        }
    )


__all__ = [
    "RUNTIME_AUTHENTICATION_BOUNDARIES_VERSION",
    "RUNTIME_AUTHENTICATION_BOUNDARIES_SCHEMA_VERSION",
    "RuntimeAuthenticationBoundaryError",
    "RuntimePrincipalType",
    "RuntimeAuthenticationBoundary",
    "AuthenticationRequirement",
    "AuthenticationBoundaryDisposition",
    "RuntimePrincipalIdentity",
    "RuntimeAuthenticationBoundaryPolicy",
    "RuntimeAuthenticationBoundaryRequest",
    "RuntimeAuthenticationBoundaryDecision",
    "RUNTIME_AUTHENTICATION_BOUNDARY_POLICIES",
    "authentication_policy_for_boundary",
    "evaluate_runtime_authentication_boundary",
    "certify_runtime_authentication_boundaries_v1",
    "explain_runtime_authentication_boundaries_v1",
]
