
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass(frozen=True)
class WorkspaceContext:
    workspace_id: str
    workspace_name: str
    domain: str | None = None
    plan: str = "free"
    status: str = "active"
    owner_email: str | None = None
    created_at: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CustomerProfileContext:
    customer_id: str
    email: str
    name: str | None = None
    workspace_ids: List[str] = field(default_factory=list)
    plan: str = "free"
    support_tier: str = "standard"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SubscriptionContext:
    plan: str
    status: str
    billing_cycle: str | None = None
    renewal_date: str | None = None
    failed_payment_count: int = 0
    usage_limit_reached: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class WorkspaceUsageContext:
    documents_uploaded: int = 0
    documents_processed: int = 0
    links_generated: int = 0
    api_calls_used: int = 0
    failed_jobs: int = 0
    last_activity_at: str | None = None


@dataclass(frozen=True)
class AccountHealthSignals:
    health_score: int
    status: str
    signals: List[str] = field(default_factory=list)
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass(frozen=True)
class CustomerRiskIndicators:
    churn_risk: str
    billing_risk: str
    product_risk: str
    support_risk: str
    indicators: List[str] = field(default_factory=list)
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def build_workspace_context(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = WorkspaceContext(
        workspace_id=str(payload.get("workspace_id") or payload.get("id") or "unknown"),
        workspace_name=str(payload.get("workspace_name") or payload.get("name") or "Unknown Workspace"),
        domain=payload.get("domain"),
        plan=str(payload.get("plan") or "free"),
        status=str(payload.get("status") or "active"),
        owner_email=payload.get("owner_email"),
        created_at=payload.get("created_at"),
        metadata=dict(payload.get("metadata") or {}),
    )

    return asdict(context)


def build_customer_profile_context(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = CustomerProfileContext(
        customer_id=str(payload.get("customer_id") or payload.get("id") or "unknown"),
        email=str(payload.get("email") or ""),
        name=payload.get("name"),
        workspace_ids=list(payload.get("workspace_ids") or []),
        plan=str(payload.get("plan") or "free"),
        support_tier=str(payload.get("support_tier") or "standard"),
        metadata=dict(payload.get("metadata") or {}),
    )

    return asdict(context)


def build_subscription_context(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = SubscriptionContext(
        plan=str(payload.get("plan") or "free"),
        status=str(payload.get("status") or "active"),
        billing_cycle=payload.get("billing_cycle"),
        renewal_date=payload.get("renewal_date"),
        failed_payment_count=int(payload.get("failed_payment_count") or 0),
        usage_limit_reached=bool(payload.get("usage_limit_reached") or False),
        metadata=dict(payload.get("metadata") or {}),
    )

    return asdict(context)


def build_workspace_usage_context(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = WorkspaceUsageContext(
        documents_uploaded=int(payload.get("documents_uploaded") or 0),
        documents_processed=int(payload.get("documents_processed") or 0),
        links_generated=int(payload.get("links_generated") or 0),
        api_calls_used=int(payload.get("api_calls_used") or 0),
        failed_jobs=int(payload.get("failed_jobs") or 0),
        last_activity_at=payload.get("last_activity_at"),
    )

    return asdict(context)


def calculate_account_health_signals(
    subscription: Dict[str, Any],
    usage: Dict[str, Any],
) -> Dict[str, Any]:
    score = 100
    signals: List[str] = []

    if subscription.get("status") not in {"active", "trialing"}:
        score -= 25
        signals.append("subscription_not_active")

    if int(subscription.get("failed_payment_count") or 0) > 0:
        score -= 20
        signals.append("failed_payment_detected")

    if bool(subscription.get("usage_limit_reached")):
        score -= 15
        signals.append("usage_limit_reached")

    if int(usage.get("failed_jobs") or 0) >= 3:
        score -= 20
        signals.append("repeated_failed_jobs")

    if int(usage.get("documents_processed") or 0) == 0:
        score -= 10
        signals.append("low_product_activation")

    score = max(0, min(100, score))

    if score >= 80:
        status = "healthy"
    elif score >= 50:
        status = "watch"
    else:
        status = "at_risk"

    return asdict(
        AccountHealthSignals(
            health_score=score,
            status=status,
            signals=signals,
        )
    )


def calculate_customer_risk_indicators(
    subscription: Dict[str, Any],
    usage: Dict[str, Any],
    support_history: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    support_history = support_history or {}
    indicators: List[str] = []

    billing_risk = "low"
    product_risk = "low"
    support_risk = "low"

    if int(subscription.get("failed_payment_count") or 0) > 0:
        billing_risk = "medium"
        indicators.append("failed_payment")

    if subscription.get("status") in {"past_due", "canceled", "unpaid"}:
        billing_risk = "high"
        indicators.append("subscription_status_risk")

    if int(usage.get("failed_jobs") or 0) >= 3:
        product_risk = "high"
        indicators.append("repeated_product_failures")

    if int(usage.get("documents_processed") or 0) == 0:
        product_risk = "medium"
        indicators.append("low_activation")

    if int(support_history.get("open_tickets") or 0) >= 3:
        support_risk = "medium"
        indicators.append("multiple_open_tickets")

    if int(support_history.get("escalations") or 0) >= 2:
        support_risk = "high"
        indicators.append("repeated_escalations")

    if "high" in {billing_risk, product_risk, support_risk}:
        churn_risk = "high"
    elif "medium" in {billing_risk, product_risk, support_risk}:
        churn_risk = "medium"
    else:
        churn_risk = "low"

    return asdict(
        CustomerRiskIndicators(
            churn_risk=churn_risk,
            billing_risk=billing_risk,
            product_risk=product_risk,
            support_risk=support_risk,
            indicators=indicators,
        )
    )
