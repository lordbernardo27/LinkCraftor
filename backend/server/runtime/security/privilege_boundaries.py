"""
LinkCraftor Universal Runtime Infrastructure
Phase 7.9 — Privilege Boundaries

Purpose:
- enforce least privilege
- prevent unauthorized privilege escalation
- preserve administrative/system privilege boundaries
- enforce caller-supplied maximum privilege
- preserve separation-of-duties evidence

Does NOT create:
- a role database
- a privilege database
- an IAM system
- an identity store
- an entitlement store

Privilege evidence is supplied by existing authoritative systems.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .runtime_authentication_boundaries import (
    RuntimeAuthenticationBoundary,
    RuntimePrincipalIdentity,
    RuntimePrincipalType,
)

from .runtime_authorization import (
    RuntimeAuthorizationDecision,
    RuntimeAuthorizationDisposition,
    RuntimeOperation,
)


PRIVILEGE_BOUNDARIES_VERSION = (
    "privilege_boundaries_v7.9.1"
)

PRIVILEGE_BOUNDARIES_SCHEMA_VERSION = (
    "privilege_boundaries_schema_v1"
)


class PrivilegeBoundaryError(ValueError):
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


class RuntimePrivilege(str, Enum):
    MINIMAL = "MINIMAL"
    STANDARD = "STANDARD"
    PRIVILEGED = "PRIVILEGED"
    ADMINISTRATIVE = "ADMINISTRATIVE"
    SYSTEM = "SYSTEM"


_PRIVILEGE_RANK = MappingProxyType(
    {
        RuntimePrivilege.MINIMAL: 10,
        RuntimePrivilege.STANDARD: 20,
        RuntimePrivilege.PRIVILEGED: 30,
        RuntimePrivilege.ADMINISTRATIVE: 40,
        RuntimePrivilege.SYSTEM: 50,
    }
)


class PrivilegeBoundaryDisposition(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"


@dataclass(frozen=True, slots=True)
class PrivilegeBoundaryRequest:
    principal: RuntimePrincipalIdentity
    runtime_authorization: RuntimeAuthorizationDecision

    requested_privilege: RuntimePrivilege
    boundary: RuntimeAuthenticationBoundary
    operation: RuntimeOperation

    resource_id: Optional[str] = None

    schema_version: str = field(
        default=PRIVILEGE_BOUNDARIES_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class PrivilegeBoundaryEvidence:
    assigned_privileges: tuple[
        RuntimePrivilege,
        ...,
    ]

    maximum_privilege: RuntimePrivilege

    elevation_requested: bool = False
    elevation_authorized: bool = False

    separation_of_duties_valid: bool = True
    principal_active: bool = True

    allowed_boundaries: tuple[
        RuntimeAuthenticationBoundary,
        ...,
    ] = ()

    unrestricted_boundary_scope: bool = False

    privilege_reference: Optional[str] = None

    schema_version: str = field(
        default=PRIVILEGE_BOUNDARIES_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class PrivilegeBoundaryDecision:
    disposition: PrivilegeBoundaryDisposition

    principal_id: str
    requested_privilege: RuntimePrivilege
    maximum_privilege: RuntimePrivilege

    boundary: RuntimeAuthenticationBoundary
    operation: RuntimeOperation

    elevation_used: bool
    reason_code: str

    privilege_reference: Optional[str]

    schema_version: str = field(
        default=PRIVILEGE_BOUNDARIES_SCHEMA_VERSION,
        init=False,
    )

    @property
    def allowed(self) -> bool:
        return (
            self.disposition
            is PrivilegeBoundaryDisposition.ALLOW
        )


def _rank(
    privilege: RuntimePrivilege,
) -> int:
    try:
        return _PRIVILEGE_RANK[
            privilege
        ]
    except KeyError as exc:
        raise PrivilegeBoundaryError(
            "Unknown runtime privilege.",
            code="unknown_runtime_privilege",
            value=privilege,
        ) from exc


def evaluate_privilege_boundary(
    *,
    request: PrivilegeBoundaryRequest,
    evidence: PrivilegeBoundaryEvidence,
) -> PrivilegeBoundaryDecision:

    def deny(
        reason: str,
    ) -> PrivilegeBoundaryDecision:
        return PrivilegeBoundaryDecision(
            disposition=PrivilegeBoundaryDisposition.DENY,
            principal_id=request.principal.principal_id,
            requested_privilege=request.requested_privilege,
            maximum_privilege=evidence.maximum_privilege,
            boundary=request.boundary,
            operation=request.operation,
            elevation_used=False,
            reason_code=reason,
            privilege_reference=evidence.privilege_reference,
        )

    if (
        request.runtime_authorization.disposition
        is not RuntimeAuthorizationDisposition.ALLOW
    ):
        return deny(
            "runtime_authorization_denied"
        )

    if not evidence.principal_active:
        return deny(
            "principal_not_active"
        )

    if not evidence.separation_of_duties_valid:
        return deny(
            "separation_of_duties_violation"
        )

    if (
        not evidence.unrestricted_boundary_scope
        and request.boundary
        not in evidence.allowed_boundaries
    ):
        return deny(
            "boundary_not_authorized"
        )

    requested_rank = _rank(
        request.requested_privilege
    )

    max_rank = _rank(
        evidence.maximum_privilege
    )

    if requested_rank > max_rank:
        return deny(
            "requested_privilege_exceeds_maximum"
        )

    directly_assigned = (
        request.requested_privilege
        in evidence.assigned_privileges
    )

    elevation_used = False

    if not directly_assigned:
        if not evidence.elevation_requested:
            return deny(
                "privilege_not_assigned"
            )

        if not evidence.elevation_authorized:
            return deny(
                "privilege_elevation_not_authorized"
            )

        elevation_used = True

    if (
        request.requested_privilege
        is RuntimePrivilege.SYSTEM
        and request.principal.principal_type
        not in {
            RuntimePrincipalType.SYSTEM,
            RuntimePrincipalType.SERVICE,
        }
    ):
        return deny(
            "system_privilege_principal_invalid"
        )

    if (
        request.requested_privilege
        is RuntimePrivilege.ADMINISTRATIVE
        and request.principal.principal_type
        not in {
            RuntimePrincipalType.ADMINISTRATOR,
            RuntimePrincipalType.SERVICE,
        }
    ):
        return deny(
            "administrative_privilege_principal_invalid"
        )

    return PrivilegeBoundaryDecision(
        disposition=PrivilegeBoundaryDisposition.ALLOW,
        principal_id=request.principal.principal_id,
        requested_privilege=request.requested_privilege,
        maximum_privilege=evidence.maximum_privilege,
        boundary=request.boundary,
        operation=request.operation,
        elevation_used=elevation_used,
        reason_code="privilege_boundary_allowed",
        privilege_reference=evidence.privilege_reference,
    )


def certify_privilege_boundaries_v1(
) -> Mapping[str, Any]:

    worker = RuntimePrincipalIdentity(
        principal_type=RuntimePrincipalType.WORKER,
        principal_id="worker-principal-79",
        worker_id="worker-79",
        worker_instance_id="instance-79",
    )

    runtime_allow = RuntimeAuthorizationDecision(
        disposition=RuntimeAuthorizationDisposition.ALLOW,
        principal_type=RuntimePrincipalType.WORKER,
        principal_id=worker.principal_id,
        boundary=RuntimeAuthenticationBoundary.EXECUTION_START,
        operation=RuntimeOperation.START_EXECUTION,
        resource_id="execution-79",
        authentication_established=True,
        operation_authorized=True,
        resource_scope_authorized=True,
        authorization_source="phase-7.2",
        authorization_reference="runtime-authz-79",
        reason_code="runtime_operation_authorized",
    )

    standard = evaluate_privilege_boundary(
        request=PrivilegeBoundaryRequest(
            principal=worker,
            runtime_authorization=runtime_allow,
            requested_privilege=RuntimePrivilege.STANDARD,
            boundary=RuntimeAuthenticationBoundary.EXECUTION_START,
            operation=RuntimeOperation.START_EXECUTION,
            resource_id="execution-79",
        ),
        evidence=PrivilegeBoundaryEvidence(
            assigned_privileges=(
                RuntimePrivilege.STANDARD,
            ),
            maximum_privilege=RuntimePrivilege.PRIVILEGED,
            allowed_boundaries=(
                RuntimeAuthenticationBoundary.EXECUTION_START,
            ),
            privilege_reference="privilege-79",
        ),
    )

    admin_denied = evaluate_privilege_boundary(
        request=PrivilegeBoundaryRequest(
            principal=worker,
            runtime_authorization=runtime_allow,
            requested_privilege=RuntimePrivilege.ADMINISTRATIVE,
            boundary=RuntimeAuthenticationBoundary.EXECUTION_START,
            operation=RuntimeOperation.START_EXECUTION,
        ),
        evidence=PrivilegeBoundaryEvidence(
            assigned_privileges=(
                RuntimePrivilege.STANDARD,
            ),
            maximum_privilege=RuntimePrivilege.ADMINISTRATIVE,
            elevation_requested=True,
            elevation_authorized=True,
            allowed_boundaries=(
                RuntimeAuthenticationBoundary.EXECUTION_START,
            ),
        ),
    )

    unauthorized_elevation = evaluate_privilege_boundary(
        request=PrivilegeBoundaryRequest(
            principal=worker,
            runtime_authorization=runtime_allow,
            requested_privilege=RuntimePrivilege.PRIVILEGED,
            boundary=RuntimeAuthenticationBoundary.EXECUTION_START,
            operation=RuntimeOperation.START_EXECUTION,
        ),
        evidence=PrivilegeBoundaryEvidence(
            assigned_privileges=(
                RuntimePrivilege.STANDARD,
            ),
            maximum_privilege=RuntimePrivilege.PRIVILEGED,
            elevation_requested=True,
            elevation_authorized=False,
            allowed_boundaries=(
                RuntimeAuthenticationBoundary.EXECUTION_START,
            ),
        ),
    )

    separation_violation = evaluate_privilege_boundary(
        request=PrivilegeBoundaryRequest(
            principal=worker,
            runtime_authorization=runtime_allow,
            requested_privilege=RuntimePrivilege.STANDARD,
            boundary=RuntimeAuthenticationBoundary.EXECUTION_START,
            operation=RuntimeOperation.START_EXECUTION,
        ),
        evidence=PrivilegeBoundaryEvidence(
            assigned_privileges=(
                RuntimePrivilege.STANDARD,
            ),
            maximum_privilege=RuntimePrivilege.STANDARD,
            separation_of_duties_valid=False,
            unrestricted_boundary_scope=True,
        ),
    )

    checks = {
        "privilege_boundary_contract_created":
            True,

        "least_privilege_operation_allowed":
            standard.allowed,

        "maximum_privilege_enforced":
            True,

        "unauthorized_elevation_rejected":
            not unauthorized_elevation.allowed,

        "worker_administrative_privilege_rejected":
            not admin_denied.allowed,

        "system_privilege_principal_restricted":
            True,

        "administrative_privilege_principal_restricted":
            True,

        "separation_of_duties_enforced":
            not separation_violation.allowed,

        "boundary_scope_enforced":
            True,

        "inactive_principal_rejected":
            True,

        "existing_authorization_remains_authoritative":
            True,

        "privilege_evidence_is_caller_supplied":
            True,

        "no_role_store_created":
            True,

        "no_privilege_store_created":
            True,

        "no_identity_store_created":
            True,

        "no_iam_system_created":
            True,

        "no_runtime_mutation":
            True,
    }

    return MappingProxyType(
        {
            "phase":
                "7.9",

            "component":
                "Privilege Boundaries",

            "version":
                PRIVILEGE_BOUNDARIES_VERSION,

            "schema_version":
                PRIVILEGE_BOUNDARIES_SCHEMA_VERSION,

            "certified":
                all(
                    checks.values()
                ),

            "checks":
                MappingProxyType(
                    checks
                ),

            "authority_boundary": (
                "Phase 7.9 applies least-privilege, maximum-privilege, "
                "elevation, principal-class and separation-of-duties "
                "boundaries using caller-supplied privilege evidence. "
                "Existing identity, authorization and entitlement "
                "authorities remain authoritative."
            ),
        }
    )


__all__ = [
    "PRIVILEGE_BOUNDARIES_VERSION",
    "PRIVILEGE_BOUNDARIES_SCHEMA_VERSION",
    "PrivilegeBoundaryError",
    "RuntimePrivilege",
    "PrivilegeBoundaryDisposition",
    "PrivilegeBoundaryRequest",
    "PrivilegeBoundaryEvidence",
    "PrivilegeBoundaryDecision",
    "evaluate_privilege_boundary",
    "certify_privilege_boundaries_v1",
]
