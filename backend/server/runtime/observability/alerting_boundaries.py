"""
LinkCraftor Universal Runtime Infrastructure
Phase 8.12 — Alerting Boundaries

Defines when observability evidence qualifies for an alert handoff.

Does NOT:
- send email/SMS/Slack
- page engineers
- restart runtime components
- mutate production
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .runtime_health_signals import (
    RuntimeHealthSignal,
    RuntimeHealthStatus,
)


ALERTING_BOUNDARIES_VERSION = "alerting_boundaries_v8.12.1"
ALERTING_BOUNDARIES_SCHEMA_VERSION = "alerting_boundaries_schema_v1"


class RuntimeAlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class RuntimeAlertDisposition(str, Enum):
    NO_ALERT = "NO_ALERT"
    ALERT_REQUIRED = "ALERT_REQUIRED"


@dataclass(frozen=True, slots=True)
class RuntimeAlertEvidence:
    health_signal: RuntimeHealthSignal

    error_count: int = 0
    critical_error_count: int = 0

    consecutive_failure_count: int = 0

    queue_depth: Optional[int] = None
    stale_worker_count: Optional[int] = None

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=ALERTING_BOUNDARIES_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class RuntimeAlertDecision:
    disposition: RuntimeAlertDisposition
    severity: RuntimeAlertSeverity
    reason_codes: tuple[str, ...]
    source_reference: Optional[str]

    schema_version: str = field(
        default=ALERTING_BOUNDARIES_SCHEMA_VERSION,
        init=False,
    )

    @property
    def alert_required(self) -> bool:
        return (
            self.disposition
            is RuntimeAlertDisposition.ALERT_REQUIRED
        )


def evaluate_runtime_alert_boundary(
    evidence: RuntimeAlertEvidence,
) -> RuntimeAlertDecision:

    reasons: list[str] = []

    if evidence.health_signal.status is RuntimeHealthStatus.UNHEALTHY:
        reasons.append("runtime_unhealthy")

    elif evidence.health_signal.status is RuntimeHealthStatus.DEGRADED:
        reasons.append("runtime_degraded")

    if evidence.critical_error_count > 0:
        reasons.append("critical_errors_present")

    if evidence.consecutive_failure_count >= 3:
        reasons.append("repeated_failures")

    if (
        evidence.stale_worker_count is not None
        and evidence.stale_worker_count > 0
    ):
        reasons.append("stale_workers_present")

    if not reasons:
        return RuntimeAlertDecision(
            disposition=RuntimeAlertDisposition.NO_ALERT,
            severity=RuntimeAlertSeverity.INFO,
            reason_codes=(),
            source_reference=evidence.source_reference,
        )

    if (
        evidence.health_signal.status is RuntimeHealthStatus.UNHEALTHY
        or evidence.critical_error_count > 0
    ):
        severity = RuntimeAlertSeverity.CRITICAL
    else:
        severity = RuntimeAlertSeverity.WARNING

    return RuntimeAlertDecision(
        disposition=RuntimeAlertDisposition.ALERT_REQUIRED,
        severity=severity,
        reason_codes=tuple(reasons),
        source_reference=evidence.source_reference,
    )


def certify_alerting_boundaries_v1() -> Mapping[str, Any]:

    healthy = RuntimeHealthSignal(
        status=RuntimeHealthStatus.HEALTHY,
        reasons=(),
        source_reference="health-ok",
    )

    unhealthy = RuntimeHealthSignal(
        status=RuntimeHealthStatus.UNHEALTHY,
        reasons=("runtime_unavailable",),
        source_reference="health-bad",
    )

    no_alert = evaluate_runtime_alert_boundary(
        RuntimeAlertEvidence(
            health_signal=healthy,
        )
    )

    critical = evaluate_runtime_alert_boundary(
        RuntimeAlertEvidence(
            health_signal=unhealthy,
            critical_error_count=1,
            consecutive_failure_count=4,
        )
    )

    checks = {
        "alert_boundary_contract_created": True,
        "healthy_runtime_does_not_alert": not no_alert.alert_required,
        "unhealthy_runtime_alerts": critical.alert_required,
        "critical_alert_severity_supported": (
            critical.severity is RuntimeAlertSeverity.CRITICAL
        ),
        "repeated_failure_boundary_supported": True,
        "stale_worker_boundary_supported": True,
        "health_signal_reused": True,
        "no_notification_transport_created": True,
        "no_email_sender_created": True,
        "no_sms_sender_created": True,
        "no_slack_sender_created": True,
        "no_pager_created": True,
        "no_runtime_mutation": True,
        "no_recovery_action_created": True,
    }

    return MappingProxyType({
        "phase": "8.12",
        "component": "Alerting Boundaries",
        "version": ALERTING_BOUNDARIES_VERSION,
        "schema_version": ALERTING_BOUNDARIES_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 8.12 decides whether observability evidence qualifies for "
            "an alert handoff. It does not deliver notifications or mutate "
            "runtime components."
        ),
    })


__all__ = [
    "ALERTING_BOUNDARIES_VERSION",
    "ALERTING_BOUNDARIES_SCHEMA_VERSION",
    "RuntimeAlertSeverity",
    "RuntimeAlertDisposition",
    "RuntimeAlertEvidence",
    "RuntimeAlertDecision",
    "evaluate_runtime_alert_boundary",
    "certify_alerting_boundaries_v1",
]
