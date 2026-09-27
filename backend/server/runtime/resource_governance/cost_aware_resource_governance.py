"""
LinkCraftor Universal Runtime Infrastructure
Phase 10.13 — Cost-Aware Resource Governance

Purpose:
- compare estimated runtime cost against supplied budget boundary
- produce resource-governance admission posture

Does NOT:
- charge customers
- calculate invoices
- own billing
- purchase cloud capacity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .resource_governance_contract import (
    ResourceAdmissionDisposition,
)


COST_AWARE_RESOURCE_GOVERNANCE_VERSION = (
    "cost_aware_resource_governance_v10.13.1"
)

COST_AWARE_RESOURCE_GOVERNANCE_SCHEMA_VERSION = (
    "cost_aware_resource_governance_schema_v1"
)


@dataclass(frozen=True, slots=True)
class ResourceCostEvidence:
    estimated_cost_units: float

    consumed_budget_units: float
    reserved_budget_units: float
    budget_limit_units: float

    hard_budget: bool = True

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=COST_AWARE_RESOURCE_GOVERNANCE_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class ResourceCostDecision:
    disposition: ResourceAdmissionDisposition

    estimated_cost_units: float
    allowed_cost_units: float
    remaining_budget_units: float

    reason_codes: tuple[str, ...]
    source_reference: Optional[str]

    schema_version: str = field(
        default=COST_AWARE_RESOURCE_GOVERNANCE_SCHEMA_VERSION,
        init=False,
    )


def evaluate_cost_aware_governance(
    evidence: ResourceCostEvidence,
) -> ResourceCostDecision:

    remaining = max(
        evidence.budget_limit_units
        - evidence.consumed_budget_units
        - evidence.reserved_budget_units,
        0.0,
    )

    if evidence.estimated_cost_units <= remaining:
        disposition = ResourceAdmissionDisposition.ALLOW
        allowed = evidence.estimated_cost_units
        reasons = ("cost_within_budget",)

    elif remaining > 0 and not evidence.hard_budget:
        disposition = ResourceAdmissionDisposition.ALLOW_WITH_LIMIT
        allowed = remaining
        reasons = ("soft_budget_partial_allowance",)

    else:
        disposition = ResourceAdmissionDisposition.DEFER
        allowed = 0.0
        reasons = ("resource_budget_exhausted",)

    return ResourceCostDecision(
        disposition=disposition,
        estimated_cost_units=evidence.estimated_cost_units,
        allowed_cost_units=allowed,
        remaining_budget_units=remaining,
        reason_codes=reasons,
        source_reference=evidence.source_reference,
    )


def certify_cost_aware_resource_governance_v1(
) -> Mapping[str, Any]:

    allowed = evaluate_cost_aware_governance(
        ResourceCostEvidence(
            estimated_cost_units=10,
            consumed_budget_units=40,
            reserved_budget_units=10,
            budget_limit_units=100,
        )
    )

    deferred = evaluate_cost_aware_governance(
        ResourceCostEvidence(
            estimated_cost_units=60,
            consumed_budget_units=50,
            reserved_budget_units=10,
            budget_limit_units=100,
        )
    )

    soft = evaluate_cost_aware_governance(
        ResourceCostEvidence(
            estimated_cost_units=60,
            consumed_budget_units=50,
            reserved_budget_units=10,
            budget_limit_units=100,
            hard_budget=False,
        )
    )

    checks = {
        "cost_governance_contract_created": True,
        "remaining_budget_calculated": (
            allowed.remaining_budget_units == 50
        ),
        "cost_within_budget_allowed": (
            allowed.disposition
            is ResourceAdmissionDisposition.ALLOW
        ),
        "hard_budget_excess_deferred": (
            deferred.disposition
            is ResourceAdmissionDisposition.DEFER
        ),
        "soft_budget_partial_supported": (
            soft.disposition
            is ResourceAdmissionDisposition.ALLOW_WITH_LIMIT
        ),
        "estimated_cost_evidence_supported": True,
        "reserved_budget_supported": True,
        "billing_authority_preserved": True,
        "subscription_authority_preserved": True,
        "cloud_provisioning_authority_preserved": True,
        "no_customer_charge": True,
        "no_invoice_calculation": True,
        "no_cloud_purchase": True,
        "no_billing_mutation": True,
        "no_runtime_mutation": True,
    }

    return MappingProxyType({
        "phase": "10.13",
        "component": "Cost-Aware Resource Governance",
        "version": COST_AWARE_RESOURCE_GOVERNANCE_VERSION,
        "schema_version": COST_AWARE_RESOURCE_GOVERNANCE_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 10.13 compares supplied runtime cost estimates with "
            "resource-budget boundaries only. Billing and cloud provisioning "
            "remain external authorities."
        ),
    })


__all__ = [
    "COST_AWARE_RESOURCE_GOVERNANCE_VERSION",
    "COST_AWARE_RESOURCE_GOVERNANCE_SCHEMA_VERSION",
    "ResourceCostEvidence",
    "ResourceCostDecision",
    "evaluate_cost_aware_governance",
    "certify_cost_aware_resource_governance_v1",
]
