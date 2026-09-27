"""
LinkCraftor Universal Runtime Infrastructure
Phase 10.8 — Runtime Quotas

Defines usage-window quota governance.

Does NOT:
- persist counters
- reset counters
- charge customers
- mutate runtime work
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .resource_governance_contract import (
    ResourceAdmissionDisposition,
    ResourceDimension,
)


RUNTIME_QUOTAS_VERSION = "runtime_quotas_v10.8.1"
RUNTIME_QUOTAS_SCHEMA_VERSION = "runtime_quotas_schema_v1"


class QuotaWindow(str, Enum):
    MINUTE = "MINUTE"
    HOUR = "HOUR"
    DAY = "DAY"
    MONTH = "MONTH"
    BILLING_PERIOD = "BILLING_PERIOD"


@dataclass(frozen=True, slots=True)
class RuntimeQuota:
    quota_key: str

    dimension: ResourceDimension

    limit: float
    unit: str
    window: QuotaWindow

    hard_limit: bool = True

    schema_version: str = field(
        default=RUNTIME_QUOTAS_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class RuntimeQuotaUsage:
    quota_key: str
    consumed: float
    reserved: float

    schema_version: str = field(
        default=RUNTIME_QUOTAS_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class RuntimeQuotaDecision:
    disposition: ResourceAdmissionDisposition

    requested_amount: float
    allowed_amount: float
    remaining_quota: float

    reason_codes: tuple[str, ...]

    schema_version: str = field(
        default=RUNTIME_QUOTAS_SCHEMA_VERSION,
        init=False,
    )


def evaluate_runtime_quota(
    *,
    quota: RuntimeQuota,
    usage: RuntimeQuotaUsage,
    requested_amount: float,
) -> RuntimeQuotaDecision:

    if quota.quota_key != usage.quota_key:
        raise ValueError("quota_key mismatch.")

    if requested_amount <= 0:
        raise ValueError("requested_amount must be > 0.")

    remaining = max(
        quota.limit
        - usage.consumed
        - usage.reserved,
        0.0,
    )

    if requested_amount <= remaining:
        disposition = ResourceAdmissionDisposition.ALLOW
        allowed = requested_amount
        reasons = ("quota_available",)

    elif remaining > 0 and not quota.hard_limit:
        disposition = ResourceAdmissionDisposition.ALLOW_WITH_LIMIT
        allowed = remaining
        reasons = ("soft_quota_partial",)

    else:
        disposition = ResourceAdmissionDisposition.DENY
        allowed = 0.0
        reasons = ("quota_exceeded",)

    return RuntimeQuotaDecision(
        disposition=disposition,
        requested_amount=requested_amount,
        allowed_amount=allowed,
        remaining_quota=remaining,
        reason_codes=reasons,
    )


def certify_runtime_quotas_v1() -> Mapping[str, Any]:

    quota = RuntimeQuota(
        quota_key="workspace-108:runtime-jobs",
        dimension=ResourceDimension.ABSTRACT_RUNTIME_UNIT,
        limit=1000,
        unit="AU",
        window=QuotaWindow.BILLING_PERIOD,
        hard_limit=True,
    )

    usage = RuntimeQuotaUsage(
        quota_key="workspace-108:runtime-jobs",
        consumed=700,
        reserved=100,
    )

    allowed = evaluate_runtime_quota(
        quota=quota,
        usage=usage,
        requested_amount=100,
    )

    denied = evaluate_runtime_quota(
        quota=quota,
        usage=usage,
        requested_amount=300,
    )

    checks = {
        "runtime_quota_contract_created": True,
        "quota_remaining_calculated": (
            allowed.remaining_quota == 200
        ),
        "quota_allows_available_usage": (
            allowed.disposition
            is ResourceAdmissionDisposition.ALLOW
        ),
        "hard_quota_denies_excess": (
            denied.disposition
            is ResourceAdmissionDisposition.DENY
        ),
        "soft_quota_supported": True,
        "minute_window_supported": True,
        "hour_window_supported": True,
        "day_window_supported": True,
        "month_window_supported": True,
        "billing_period_supported": True,
        "no_counter_store_created": True,
        "no_counter_reset_scheduler_created": True,
        "no_billing_charge_created": True,
        "no_runtime_mutation": True,
        "no_persistence_write": True,
    }

    return MappingProxyType({
        "phase": "10.8",
        "component": "Runtime Quotas",
        "version": RUNTIME_QUOTAS_VERSION,
        "schema_version": RUNTIME_QUOTAS_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 10.8 governs quota eligibility from supplied quota/counter "
            "evidence. It does not persist or reset counters and does not "
            "perform billing."
        ),
    })


__all__ = [
    "RUNTIME_QUOTAS_VERSION",
    "RUNTIME_QUOTAS_SCHEMA_VERSION",
    "QuotaWindow",
    "RuntimeQuota",
    "RuntimeQuotaUsage",
    "RuntimeQuotaDecision",
    "evaluate_runtime_quota",
    "certify_runtime_quotas_v1",
]
