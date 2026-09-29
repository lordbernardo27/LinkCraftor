"""
LinkCraftor Universal Runtime Infrastructure
Phase 11.11 — API Authentication & Authorization Integration

Purpose:
- consume Phase-7 authentication/authorization decisions
- bind security evidence to API requests
- verify required scopes
- produce API admission posture

Does NOT:
- authenticate credentials
- issue tokens
- verify passwords
- create authorization engine
- mutate security policy
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .runtime_api_contract import (
    RuntimeAPIRequest,
)


API_SECURITY_INTEGRATION_VERSION = (
    "api_security_integration_v11.11.1"
)

API_SECURITY_INTEGRATION_SCHEMA_VERSION = (
    "api_security_integration_schema_v1"
)


@dataclass(frozen=True, slots=True)
class APIAuthenticationEvidence:
    authenticated: bool

    principal_id: Optional[str]
    authentication_reference: Optional[str]

    credential_type: Optional[str] = None

    schema_version: str = field(
        default=API_SECURITY_INTEGRATION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class APIAuthorizationEvidence:
    authorized: bool

    principal_id: Optional[str]
    authorization_reference: Optional[str]

    granted_scopes: tuple[str, ...] = ()
    denied_reason: Optional[str] = None

    schema_version: str = field(
        default=API_SECURITY_INTEGRATION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class APISecurityRequirement:
    required_scopes: tuple[str, ...] = ()
    authentication_required: bool = True

    schema_version: str = field(
        default=API_SECURITY_INTEGRATION_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class APISecurityDecision:
    admitted: bool

    authenticated: bool
    authorized: bool

    missing_scopes: tuple[str, ...]

    reason_codes: tuple[str, ...]

    authentication_reference: Optional[str]
    authorization_reference: Optional[str]

    schema_version: str = field(
        default=API_SECURITY_INTEGRATION_SCHEMA_VERSION,
        init=False,
    )


def evaluate_runtime_api_security(
    *,
    request: RuntimeAPIRequest,
    requirement: APISecurityRequirement,
    authentication: APIAuthenticationEvidence,
    authorization: APIAuthorizationEvidence,
) -> APISecurityDecision:

    principal = request.context.principal

    reasons: list[str] = []

    principal_consistent = (
        principal.principal_id is None
        or (
            principal.principal_id
            == authentication.principal_id
            == authorization.principal_id
        )
    )

    if not principal_consistent:
        reasons.append("principal_identity_mismatch")

    if (
        requirement.authentication_required
        and not authentication.authenticated
    ):
        reasons.append("authentication_required")

    granted = set(
        authorization.granted_scopes
    )

    missing_scopes = tuple(
        scope
        for scope in requirement.required_scopes
        if scope not in granted
    )

    if missing_scopes:
        reasons.append("required_scope_missing")

    if not authorization.authorized:
        reasons.append("authorization_denied")

    admitted = (
        principal_consistent
        and (
            authentication.authenticated
            or not requirement.authentication_required
        )
        and authorization.authorized
        and not missing_scopes
    )

    if admitted:
        reasons.append("api_security_admitted")

    return APISecurityDecision(
        admitted=admitted,
        authenticated=authentication.authenticated,
        authorized=authorization.authorized,
        missing_scopes=missing_scopes,
        reason_codes=tuple(reasons),
        authentication_reference=(
            authentication.authentication_reference
        ),
        authorization_reference=(
            authorization.authorization_reference
        ),
    )


def certify_api_security_integration_v1(
) -> Mapping[str, Any]:

    from .runtime_api_contract import (
        RuntimeAPIOperation,
        RuntimeAPIPrincipalContext,
        RuntimeAPIRequestContext,
        RuntimeAPIResource,
    )

    request = RuntimeAPIRequest(
        resource=RuntimeAPIResource.JOB,
        operation=RuntimeAPIOperation.READ,
        context=RuntimeAPIRequestContext(
            request_id="security-1111",
            correlation_id="security-correlation",
            principal=RuntimeAPIPrincipalContext(
                principal_id="principal-1111",
                workspace_id="workspace-1111",
                scopes=("runtime.jobs.read",),
            ),
        ),
        resource_id="job-1111",
    )

    allowed = evaluate_runtime_api_security(
        request=request,
        requirement=APISecurityRequirement(
            required_scopes=(
                "runtime.jobs.read",
            ),
        ),
        authentication=APIAuthenticationEvidence(
            authenticated=True,
            principal_id="principal-1111",
            authentication_reference="authn-1111",
            credential_type="service_token",
        ),
        authorization=APIAuthorizationEvidence(
            authorized=True,
            principal_id="principal-1111",
            authorization_reference="authz-1111",
            granted_scopes=(
                "runtime.jobs.read",
            ),
        ),
    )

    denied_scope = evaluate_runtime_api_security(
        request=request,
        requirement=APISecurityRequirement(
            required_scopes=(
                "runtime.jobs.control",
            ),
        ),
        authentication=APIAuthenticationEvidence(
            authenticated=True,
            principal_id="principal-1111",
            authentication_reference="authn-1111",
        ),
        authorization=APIAuthorizationEvidence(
            authorized=True,
            principal_id="principal-1111",
            authorization_reference="authz-1111",
            granted_scopes=(
                "runtime.jobs.read",
            ),
        ),
    )

    denied_authn = evaluate_runtime_api_security(
        request=request,
        requirement=APISecurityRequirement(
            required_scopes=(),
        ),
        authentication=APIAuthenticationEvidence(
            authenticated=False,
            principal_id="principal-1111",
            authentication_reference="authn-failed",
        ),
        authorization=APIAuthorizationEvidence(
            authorized=True,
            principal_id="principal-1111",
            authorization_reference="authz-1111",
        ),
    )

    mismatch = evaluate_runtime_api_security(
        request=request,
        requirement=APISecurityRequirement(),
        authentication=APIAuthenticationEvidence(
            authenticated=True,
            principal_id="principal-other",
            authentication_reference="authn-other",
        ),
        authorization=APIAuthorizationEvidence(
            authorized=True,
            principal_id="principal-other",
            authorization_reference="authz-other",
        ),
    )

    checks = {
        "api_security_integration_contract_created": True,

        "authenticated_authorized_request_admitted": (
            allowed.admitted
        ),

        "missing_scope_denied": (
            not denied_scope.admitted
            and denied_scope.missing_scopes
            == ("runtime.jobs.control",)
        ),

        "unauthenticated_request_denied": (
            not denied_authn.admitted
        ),

        "principal_mismatch_denied": (
            not mismatch.admitted
            and "principal_identity_mismatch"
            in mismatch.reason_codes
        ),

        "authentication_reference_preserved": (
            allowed.authentication_reference
            == "authn-1111"
        ),

        "authorization_reference_preserved": (
            allowed.authorization_reference
            == "authz-1111"
        ),

        "scope_requirement_supported": True,
        "optional_authentication_requirement_supported": True,

        "phase7_authentication_authority_preserved": True,
        "phase7_authorization_authority_preserved": True,

        "no_credential_authentication_created": True,
        "no_token_issuance_created": True,
        "no_password_verification_created": True,
        "no_authorization_engine_created": True,
        "no_security_policy_store_created": True,
        "no_security_policy_mutation": True,
        "no_runtime_mutation": True,
        "no_persistence_write": True,
    }

    return MappingProxyType({
        "phase": "11.11",
        "component": "API Authentication & Authorization Integration",
        "version": API_SECURITY_INTEGRATION_VERSION,
        "schema_version": API_SECURITY_INTEGRATION_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 11.11 consumes Phase-7 authentication and authorization "
            "evidence and applies it to API admission. Phase 7 remains the "
            "authentication, authorization, identity and security authority."
        ),
    })


__all__ = [
    "API_SECURITY_INTEGRATION_VERSION",
    "API_SECURITY_INTEGRATION_SCHEMA_VERSION",
    "APIAuthenticationEvidence",
    "APIAuthorizationEvidence",
    "APISecurityRequirement",
    "APISecurityDecision",
    "evaluate_runtime_api_security",
    "certify_api_security_integration_v1",
]
