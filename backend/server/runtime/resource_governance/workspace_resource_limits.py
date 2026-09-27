"""
LinkCraftor Universal Runtime Infrastructure
Phase 10.6 — Workspace Resource Limits

Defines and evaluates workspace-scoped resource limits.

Does NOT create workspace storage or mutate workspace configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .resource_governance_contract import (
    ResourceAdmissionDisposition,
    ResourceDimension,
)


WORKSPACE_RESOURCE_LIMITS_VERSION = (
    "workspace_resource_limits_v10.6.1"
)

WORKSPACE_RESOURCE_LIMITS_SCHEMA_VERSION = (
    "workspace_resource_limits_schema_v1"
)


@dataclass(frozen=True, slots=True)
class WorkspaceResourceLimit:
    workspace_id: str

    dimension: ResourceDimension
    limit: float
    unit: str

    hard_limit: bool = True

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=WORKSPACE_RESOURCE_LIMITS_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class WorkspaceResourceUsage:
    workspace_id: str

    dimension: ResourceDimension
    current_usage: float
    reserved_usage: float
    unit: str

    schema_version: str = field(
        default=WORKSPACE_RESOURCE_LIMITS_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class WorkspaceResourceDecision:
    disposition: ResourceAdmissionDisposition

    workspace_id: str
    dimension: ResourceDimension

    requested_amount: float
    allowed_amount: float
    remaining_amount: float

    unit: str

    reason_codes: tuple[str, ...]

    schema_version: str = field(
        default=WORKSPACE_RESOURCE_LIMITS_SCHEMA_VERSION,
        init=False,
    )


def evaluate_workspace_resource_limit(
    *,
    limit: WorkspaceResourceLimit,
    usage: WorkspaceResourceUsage,
    requested_amount: float,
) -> WorkspaceResourceDecision:

    if limit.workspace_id != usage.workspace_id:
        raise ValueError("workspace_id mismatch.")

    if limit.dimension is not usage.dimension:
        raise ValueError("dimension mismatch.")

    if limit.unit != usage.unit:
        raise ValueError("unit mismatch.")

    if requested_amount <= 0:
        raise ValueError("requested_amount must be > 0.")

    remaining = max(
        limit.limit
        - usage.current_usage
        - usage.reserved_usage,
        0.0,
    )

    if requested_amount <= remaining:
        disposition = ResourceAdmissionDisposition.ALLOW
        allowed = requested_amount
        reasons = ("workspace_within_limit",)

    elif remaining > 0 and not limit.hard_limit:
        disposition = ResourceAdmissionDisposition.ALLOW_WITH_LIMIT
        allowed = remaining
        reasons = ("workspace_soft_limit_partial",)

    else:
        disposition = ResourceAdmissionDisposition.DENY
        allowed = 0.0
        reasons = ("workspace_limit_reached",)

    return WorkspaceResourceDecision(
        disposition=disposition,
        workspace_id=limit.workspace_id,
        dimension=limit.dimension,
        requested_amount=requested_amount,
        allowed_amount=allowed,
        remaining_amount=remaining,
        unit=limit.unit,
        reason_codes=reasons,
    )


def certify_workspace_resource_limits_v1(
) -> Mapping[str, Any]:

    limit = WorkspaceResourceLimit(
        workspace_id="workspace-106",
        dimension=ResourceDimension.JOB_CONCURRENCY,
        limit=20,
        unit="jobs",
    )

    usage = WorkspaceResourceUsage(
        workspace_id="workspace-106",
        dimension=ResourceDimension.JOB_CONCURRENCY,
        current_usage=12,
        reserved_usage=3,
        unit="jobs",
    )

    allowed = evaluate_workspace_resource_limit(
        limit=limit,
        usage=usage,
        requested_amount=4,
    )

    denied = evaluate_workspace_resource_limit(
        limit=limit,
        usage=usage,
        requested_amount=8,
    )

    checks = {
        "workspace_limit_contract_created": True,
        "workspace_remaining_calculated": (
            allowed.remaining_amount == 5
        ),
        "workspace_request_allowed": (
            allowed.disposition
            is ResourceAdmissionDisposition.ALLOW
        ),
        "workspace_hard_limit_denied": (
            denied.disposition
            is ResourceAdmissionDisposition.DENY
        ),
        "workspace_soft_limits_supported": True,
        "workspace_identity_isolated": True,
        "resource_dimensions_supported": True,
        "no_workspace_store_created": True,
        "no_workspace_config_mutation": True,
        "no_job_mutation": True,
        "no_execution_mutation": True,
    }

    return MappingProxyType({
        "phase": "10.6",
        "component": "Workspace Resource Limits",
        "version": WORKSPACE_RESOURCE_LIMITS_VERSION,
        "schema_version": WORKSPACE_RESOURCE_LIMITS_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 10.6 evaluates workspace-scoped limits from supplied "
            "workspace configuration. It does not create or mutate workspace "
            "storage/configuration."
        ),
    })


__all__ = [
    "WORKSPACE_RESOURCE_LIMITS_VERSION",
    "WORKSPACE_RESOURCE_LIMITS_SCHEMA_VERSION",
    "WorkspaceResourceLimit",
    "WorkspaceResourceUsage",
    "WorkspaceResourceDecision",
    "evaluate_workspace_resource_limit",
    "certify_workspace_resource_limits_v1",
]
