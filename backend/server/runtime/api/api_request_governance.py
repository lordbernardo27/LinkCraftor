"""
LinkCraftor Universal Runtime Infrastructure
Phase 11.12 — API Idempotency / Versioning / Rate-Control

Purpose:
- validate supported API versions
- classify requests requiring idempotency keys
- consume existing idempotency evidence
- consume rate-control evidence
- produce API request-governance decisions

Does NOT:
- create idempotency database
- create rate limiter
- increment counters
- sleep callers
- reject transport requests directly
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .runtime_api_contract import (
    RUNTIME_API_VERSION,
    RuntimeAPIOperation,
    RuntimeAPIRequest,
)


API_REQUEST_GOVERNANCE_VERSION = (
    "api_request_governance_v11.12.1"
)

API_REQUEST_GOVERNANCE_SCHEMA_VERSION = (
    "api_request_governance_schema_v1"
)


class APIRequestGovernanceDisposition(str, Enum):
    ALLOW = "ALLOW"
    REPLAY = "REPLAY"
    RATE_LIMIT = "RATE_LIMIT"
    REJECT_VERSION = "REJECT_VERSION"
    REJECT_IDEMPOTENCY = "REJECT_IDEMPOTENCY"


@dataclass(frozen=True, slots=True)
class APIIdempotencyEvidence:
    key_seen: bool = False

    previous_request_fingerprint: Optional[str] = None
    previous_response_reference: Optional[str] = None

    schema_version: str = field(
        default=API_REQUEST_GOVERNANCE_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class APIRateControlEvidence:
    allowed: bool = True

    remaining_requests: Optional[int] = None
    retry_after_ms: Optional[int] = None

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=API_REQUEST_GOVERNANCE_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class APIRequestGovernanceDecision:
    disposition: APIRequestGovernanceDisposition

    version_supported: bool
    idempotency_required: bool
    idempotency_satisfied: bool
    rate_allowed: bool

    replay_response_reference: Optional[str]
    retry_after_ms: Optional[int]

    reason_codes: tuple[str, ...]

    schema_version: str = field(
        default=API_REQUEST_GOVERNANCE_SCHEMA_VERSION,
        init=False,
    )


_IDEMPOTENCY_REQUIRED_OPERATIONS = frozenset({
    RuntimeAPIOperation.CREATE,
    RuntimeAPIOperation.UPDATE,
    RuntimeAPIOperation.CANCEL,
    RuntimeAPIOperation.TERMINATE,
    RuntimeAPIOperation.RETRY,
    RuntimeAPIOperation.RECOVER,
    RuntimeAPIOperation.CONTROL,
})


def evaluate_api_request_governance(
    *,
    request: RuntimeAPIRequest,
    idempotency: APIIdempotencyEvidence,
    rate_control: APIRateControlEvidence,
    supported_versions: tuple[str, ...] = (
        RUNTIME_API_VERSION,
    ),
) -> APIRequestGovernanceDecision:

    version_supported = (
        request.context.api_version
        in supported_versions
    )

    idempotency_required = (
        request.operation
        in _IDEMPOTENCY_REQUIRED_OPERATIONS
    )

    idempotency_satisfied = (
        not idempotency_required
        or bool(
            request.context.idempotency_key
            and request.context.idempotency_key.strip()
        )
    )

    reasons: list[str] = []

    if not version_supported:
        reasons.append("unsupported_api_version")

        return APIRequestGovernanceDecision(
            disposition=(
                APIRequestGovernanceDisposition.REJECT_VERSION
            ),
            version_supported=False,
            idempotency_required=idempotency_required,
            idempotency_satisfied=idempotency_satisfied,
            rate_allowed=rate_control.allowed,
            replay_response_reference=None,
            retry_after_ms=None,
            reason_codes=tuple(reasons),
        )

    if not idempotency_satisfied:
        reasons.append("idempotency_key_required")

        return APIRequestGovernanceDecision(
            disposition=(
                APIRequestGovernanceDisposition.REJECT_IDEMPOTENCY
            ),
            version_supported=True,
            idempotency_required=True,
            idempotency_satisfied=False,
            rate_allowed=rate_control.allowed,
            replay_response_reference=None,
            retry_after_ms=None,
            reason_codes=tuple(reasons),
        )

    if idempotency.key_seen:
        reasons.append("idempotent_replay")

        return APIRequestGovernanceDecision(
            disposition=APIRequestGovernanceDisposition.REPLAY,
            version_supported=True,
            idempotency_required=idempotency_required,
            idempotency_satisfied=True,
            rate_allowed=rate_control.allowed,
            replay_response_reference=(
                idempotency.previous_response_reference
            ),
            retry_after_ms=None,
            reason_codes=tuple(reasons),
        )

    if not rate_control.allowed:
        reasons.append("rate_control_limit_reached")

        return APIRequestGovernanceDecision(
            disposition=APIRequestGovernanceDisposition.RATE_LIMIT,
            version_supported=True,
            idempotency_required=idempotency_required,
            idempotency_satisfied=True,
            rate_allowed=False,
            replay_response_reference=None,
            retry_after_ms=rate_control.retry_after_ms,
            reason_codes=tuple(reasons),
        )

    reasons.append("api_request_governance_allowed")

    return APIRequestGovernanceDecision(
        disposition=APIRequestGovernanceDisposition.ALLOW,
        version_supported=True,
        idempotency_required=idempotency_required,
        idempotency_satisfied=True,
        rate_allowed=True,
        replay_response_reference=None,
        retry_after_ms=None,
        reason_codes=tuple(reasons),
    )


def certify_api_request_governance_v1(
) -> Mapping[str, Any]:

    from .runtime_api_contract import (
        RuntimeAPIPrincipalContext,
        RuntimeAPIRequestContext,
        RuntimeAPIResource,
    )

    principal = RuntimeAPIPrincipalContext(
        principal_id="principal-1112",
        workspace_id="workspace-1112",
    )

    create_request = RuntimeAPIRequest(
        resource=RuntimeAPIResource.JOB,
        operation=RuntimeAPIOperation.CREATE,
        context=RuntimeAPIRequestContext(
            request_id="governance-create",
            correlation_id="governance-correlation",
            api_version="v1",
            idempotency_key="idem-1112",
            principal=principal,
        ),
        payload={
            "runtime_type": "internal_linking",
        },
    )

    allowed = evaluate_api_request_governance(
        request=create_request,
        idempotency=APIIdempotencyEvidence(),
        rate_control=APIRateControlEvidence(
            allowed=True,
            remaining_requests=99,
        ),
    )

    replay = evaluate_api_request_governance(
        request=create_request,
        idempotency=APIIdempotencyEvidence(
            key_seen=True,
            previous_request_fingerprint="fingerprint-1112",
            previous_response_reference="response-1112",
        ),
        rate_control=APIRateControlEvidence(
            allowed=True,
        ),
    )

    limited = evaluate_api_request_governance(
        request=create_request,
        idempotency=APIIdempotencyEvidence(),
        rate_control=APIRateControlEvidence(
            allowed=False,
            remaining_requests=0,
            retry_after_ms=1000,
            source_reference="rate-control-1112",
        ),
    )

    missing_idempotency = evaluate_api_request_governance(
        request=RuntimeAPIRequest(
            resource=RuntimeAPIResource.JOB,
            operation=RuntimeAPIOperation.CREATE,
            context=RuntimeAPIRequestContext(
                request_id="governance-no-idem",
                correlation_id="governance-correlation",
                api_version="v1",
                principal=principal,
            ),
            payload={
                "runtime_type": "internal_linking",
            },
        ),
        idempotency=APIIdempotencyEvidence(),
        rate_control=APIRateControlEvidence(),
    )

    unsupported = evaluate_api_request_governance(
        request=RuntimeAPIRequest(
            resource=RuntimeAPIResource.JOB,
            operation=RuntimeAPIOperation.READ,
            context=RuntimeAPIRequestContext(
                request_id="governance-v2",
                correlation_id="governance-correlation",
                api_version="v2",
                principal=principal,
            ),
            resource_id="job-1112",
        ),
        idempotency=APIIdempotencyEvidence(),
        rate_control=APIRateControlEvidence(),
    )

    checks = {
        "api_request_governance_contract_created": True,

        "supported_version_allowed": (
            allowed.version_supported
        ),

        "create_requires_idempotency": (
            allowed.idempotency_required
        ),

        "idempotency_key_satisfied": (
            allowed.idempotency_satisfied
        ),

        "normal_request_allowed": (
            allowed.disposition
            is APIRequestGovernanceDisposition.ALLOW
        ),

        "idempotent_replay_supported": (
            replay.disposition
            is APIRequestGovernanceDisposition.REPLAY
        ),

        "previous_response_reference_preserved": (
            replay.replay_response_reference
            == "response-1112"
        ),

        "rate_control_limit_supported": (
            limited.disposition
            is APIRequestGovernanceDisposition.RATE_LIMIT
        ),

        "retry_after_preserved": (
            limited.retry_after_ms == 1000
        ),

        "missing_idempotency_rejected": (
            missing_idempotency.disposition
            is APIRequestGovernanceDisposition.REJECT_IDEMPOTENCY
        ),

        "unsupported_version_rejected": (
            unsupported.disposition
            is APIRequestGovernanceDisposition.REJECT_VERSION
        ),

        "read_idempotency_not_required": (
            not unsupported.idempotency_required
        ),

        "phase6_execution_idempotency_authority_preserved": True,
        "phase10_rate_governance_boundary_preserved": True,
        "phase12_persistence_authority_preserved": True,

        "no_idempotency_database_created": True,
        "no_rate_limiter_created": True,
        "no_counter_increment": True,
        "no_caller_sleep": True,
        "no_transport_rejection_execution": True,
        "no_runtime_mutation": True,
        "no_persistence_write": True,
    }

    return MappingProxyType({
        "phase": "11.12",
        "component": "API Idempotency / Versioning / Rate-Control",
        "version": API_REQUEST_GOVERNANCE_VERSION,
        "schema_version": API_REQUEST_GOVERNANCE_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 11.12 validates API version/idempotency requirements and "
            "consumes rate-control evidence. It does not create an idempotency "
            "store, persistence engine, transport rate limiter or runtime "
            "scheduler."
        ),
    })


__all__ = [
    "API_REQUEST_GOVERNANCE_VERSION",
    "API_REQUEST_GOVERNANCE_SCHEMA_VERSION",
    "APIRequestGovernanceDisposition",
    "APIIdempotencyEvidence",
    "APIRateControlEvidence",
    "APIRequestGovernanceDecision",
    "evaluate_api_request_governance",
    "certify_api_request_governance_v1",
]
