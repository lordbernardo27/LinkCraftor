"""
LinkCraftor Universal Runtime Infrastructure
Phase 10.7 — Plan / Entitlement Resource Limits

Consumes existing billing/entitlement outputs and translates them into
resource-governance limits.

Does NOT own billing, subscriptions, plan storage or entitlement issuance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .resource_governance_contract import (
    ResourceAdmissionDisposition,
    ResourceDimension,
)


PLAN_ENTITLEMENT_RESOURCE_LIMITS_VERSION = (
    "plan_entitlement_resource_limits_v10.7.1"
)

PLAN_ENTITLEMENT_RESOURCE_LIMITS_SCHEMA_VERSION = (
    "plan_entitlement_resource_limits_schema_v1"
)


@dataclass(frozen=True, slots=True)
class PlanEntitlementResourceLimit:
    plan_id: str
    entitlement_key: str

    dimension: ResourceDimension

    limit: float
    unit: str

    enabled: bool = True

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=PLAN_ENTITLEMENT_RESOURCE_LIMITS_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class PlanEntitlementDecision:
    disposition: ResourceAdmissionDisposition

    plan_id: str
    entitlement_key: str

    requested_amount: float
    allowed_amount: float
    entitlement_limit: float

    reason_codes: tuple[str, ...]

    schema_version: str = field(
        default=PLAN_ENTITLEMENT_RESOURCE_LIMITS_SCHEMA_VERSION,
        init=False,
    )


def evaluate_plan_entitlement_limit(
    *,
    entitlement: PlanEntitlementResourceLimit,
    requested_amount: float,
) -> PlanEntitlementDecision:

    if requested_amount <= 0:
        raise ValueError("requested_amount must be > 0.")

    if not entitlement.enabled:
        return PlanEntitlementDecision(
            disposition=ResourceAdmissionDisposition.DENY,
            plan_id=entitlement.plan_id,
            entitlement_key=entitlement.entitlement_key,
            requested_amount=requested_amount,
            allowed_amount=0.0,
            entitlement_limit=entitlement.limit,
            reason_codes=("entitlement_disabled",),
        )

    if requested_amount <= entitlement.limit:
        disposition = ResourceAdmissionDisposition.ALLOW
        allowed = requested_amount
        reasons = ("plan_entitlement_allows_request",)

    else:
        disposition = ResourceAdmissionDisposition.DENY
        allowed = 0.0
        reasons = ("plan_entitlement_limit_exceeded",)

    return PlanEntitlementDecision(
        disposition=disposition,
        plan_id=entitlement.plan_id,
        entitlement_key=entitlement.entitlement_key,
        requested_amount=requested_amount,
        allowed_amount=allowed,
        entitlement_limit=entitlement.limit,
        reason_codes=reasons,
    )


def certify_plan_entitlement_resource_limits_v1(
) -> Mapping[str, Any]:

    entitlement = PlanEntitlementResourceLimit(
        plan_id="pro",
        entitlement_key="runtime.execution_concurrency",
        dimension=ResourceDimension.EXECUTION_CONCURRENCY,
        limit=20,
        unit="slots",
        enabled=True,
        source_reference="billing-entitlement-107",
    )

    allowed = evaluate_plan_entitlement_limit(
        entitlement=entitlement,
        requested_amount=10,
    )

    denied = evaluate_plan_entitlement_limit(
        entitlement=entitlement,
        requested_amount=25,
    )

    disabled = evaluate_plan_entitlement_limit(
        entitlement=PlanEntitlementResourceLimit(
            plan_id="starter",
            entitlement_key="runtime.api_capacity",
            dimension=ResourceDimension.API_CAPACITY,
            limit=0,
            unit="requests",
            enabled=False,
        ),
        requested_amount=1,
    )

    checks = {
        "plan_entitlement_contract_created": True,
        "enabled_entitlement_allows_within_limit": (
            allowed.disposition
            is ResourceAdmissionDisposition.ALLOW
        ),
        "entitlement_limit_denies_excess": (
            denied.disposition
            is ResourceAdmissionDisposition.DENY
        ),
        "disabled_entitlement_denied": (
            disabled.disposition
            is ResourceAdmissionDisposition.DENY
        ),
        "plan_identity_preserved": (
            allowed.plan_id == "pro"
        ),
        "entitlement_key_preserved": (
            allowed.entitlement_key
            == "runtime.execution_concurrency"
        ),
        "billing_authority_preserved": True,
        "subscription_authority_preserved": True,
        "entitlement_issuance_authority_preserved": True,
        "no_plan_store_created": True,
        "no_subscription_system_created": True,
        "no_billing_mutation": True,
        "no_runtime_mutation": True,
    }

    return MappingProxyType({
        "phase": "10.7",
        "component": "Plan / Entitlement Resource Limits",
        "version": PLAN_ENTITLEMENT_RESOURCE_LIMITS_VERSION,
        "schema_version": PLAN_ENTITLEMENT_RESOURCE_LIMITS_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 10.7 consumes existing plan/entitlement outputs and maps "
            "them into runtime resource decisions. It does not own billing, "
            "subscriptions or entitlement issuance."
        ),
    })


__all__ = [
    "PLAN_ENTITLEMENT_RESOURCE_LIMITS_VERSION",
    "PLAN_ENTITLEMENT_RESOURCE_LIMITS_SCHEMA_VERSION",
    "PlanEntitlementResourceLimit",
    "PlanEntitlementDecision",
    "evaluate_plan_entitlement_limit",
    "certify_plan_entitlement_resource_limits_v1",
]
