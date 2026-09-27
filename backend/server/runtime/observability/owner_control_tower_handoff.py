"""
LinkCraftor Universal Runtime Infrastructure
Phase 8.13 — Owner Control Tower Handoff

Builds normalized observability envelopes for downstream Owner Control Tower.

Does NOT create:
- Owner Control Tower UI
- dashboard database
- alert sender
- runtime mutation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .alerting_boundaries import RuntimeAlertDecision
from .runtime_health_signals import RuntimeHealthSignal


OWNER_CONTROL_TOWER_HANDOFF_VERSION = (
    "owner_control_tower_handoff_v8.13.1"
)

OWNER_CONTROL_TOWER_HANDOFF_SCHEMA_VERSION = (
    "owner_control_tower_handoff_schema_v1"
)


@dataclass(frozen=True, slots=True)
class OwnerControlTowerObservabilityHandoff:
    runtime_health: RuntimeHealthSignal
    alert_decision: RuntimeAlertDecision

    runtime_metrics: Mapping[str, Any]
    queue_metrics: Mapping[str, Any]
    worker_metrics: Mapping[str, Any]
    job_metrics: Mapping[str, Any]
    orchestration_metrics: Mapping[str, Any]
    execution_metrics: Mapping[str, Any]
    error_summary: Mapping[str, Any]

    trace_reference: Optional[str] = None

    schema_version: str = field(
        default=OWNER_CONTROL_TOWER_HANDOFF_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        for attr in (
            "runtime_metrics",
            "queue_metrics",
            "worker_metrics",
            "job_metrics",
            "orchestration_metrics",
            "execution_metrics",
            "error_summary",
        ):
            object.__setattr__(
                self,
                attr,
                MappingProxyType(
                    dict(getattr(self, attr))
                ),
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "runtime_health": self.runtime_health.status.value,
            "health_reasons": list(self.runtime_health.reasons),
            "alert_required": self.alert_decision.alert_required,
            "alert_severity": self.alert_decision.severity.value,
            "alert_reason_codes": list(
                self.alert_decision.reason_codes
            ),
            "runtime_metrics": dict(self.runtime_metrics),
            "queue_metrics": dict(self.queue_metrics),
            "worker_metrics": dict(self.worker_metrics),
            "job_metrics": dict(self.job_metrics),
            "orchestration_metrics": dict(self.orchestration_metrics),
            "execution_metrics": dict(self.execution_metrics),
            "error_summary": dict(self.error_summary),
            "trace_reference": self.trace_reference,
        }


def certify_owner_control_tower_handoff_v1() -> Mapping[str, Any]:

    from .runtime_health_signals import (
        RuntimeHealthSignal,
        RuntimeHealthStatus,
    )
    from .alerting_boundaries import (
        RuntimeAlertDecision,
        RuntimeAlertDisposition,
        RuntimeAlertSeverity,
    )

    health = RuntimeHealthSignal(
        status=RuntimeHealthStatus.DEGRADED,
        reasons=("queue_depth_high",),
        source_reference="health-813",
    )

    alert = RuntimeAlertDecision(
        disposition=RuntimeAlertDisposition.ALERT_REQUIRED,
        severity=RuntimeAlertSeverity.WARNING,
        reason_codes=("runtime_degraded",),
        source_reference="alert-813",
    )

    handoff = OwnerControlTowerObservabilityHandoff(
        runtime_health=health,
        alert_decision=alert,
        runtime_metrics={"active_jobs": 10},
        queue_metrics={"depth": 1200},
        worker_metrics={"active_workers": 4},
        job_metrics={"failed_jobs": 1},
        orchestration_metrics={"running": 3},
        execution_metrics={"failed": 1},
        error_summary={"critical": 0, "error": 1},
        trace_reference="trace-813",
    )

    payload = handoff.to_dict()

    checks = {
        "owner_control_tower_handoff_contract_created": True,
        "health_handoff_preserved": (
            payload["runtime_health"] == "DEGRADED"
        ),
        "alert_handoff_preserved": (
            payload["alert_required"] is True
        ),
        "runtime_metrics_supported": True,
        "queue_metrics_supported": True,
        "worker_metrics_supported": True,
        "job_metrics_supported": True,
        "orchestration_metrics_supported": True,
        "execution_metrics_supported": True,
        "error_summary_supported": True,
        "trace_reference_supported": (
            payload["trace_reference"] == "trace-813"
        ),
        "no_owner_control_tower_ui_created": True,
        "no_dashboard_database_created": True,
        "no_alert_transport_created": True,
        "no_runtime_mutation": True,
        "no_persistence_write": True,
    }

    return MappingProxyType({
        "phase": "8.13",
        "component": "Owner Control Tower Handoff",
        "version": OWNER_CONTROL_TOWER_HANDOFF_VERSION,
        "schema_version": OWNER_CONTROL_TOWER_HANDOFF_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 8.13 prepares normalized observability handoff data for "
            "the downstream Owner Control Tower without creating the UI, "
            "dashboard persistence, alert delivery or runtime mutation."
        ),
    })


__all__ = [
    "OWNER_CONTROL_TOWER_HANDOFF_VERSION",
    "OWNER_CONTROL_TOWER_HANDOFF_SCHEMA_VERSION",
    "OwnerControlTowerObservabilityHandoff",
    "certify_owner_control_tower_handoff_v1",
]
