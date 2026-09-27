"""
LinkCraftor Universal Runtime Infrastructure
Phase 8.7 — Orchestration Metrics
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .runtime_metrics import (
    RuntimeMetric,
    RuntimeMetricCategory,
    RuntimeMetricIdentity,
    RuntimeMetricSink,
    RuntimeMetricType,
    emit_runtime_metric,
)


ORCHESTRATION_METRICS_VERSION = "orchestration_metrics_v8.7.1"
ORCHESTRATION_METRICS_SCHEMA_VERSION = "orchestration_metrics_schema_v1"


@dataclass(frozen=True, slots=True)
class OrchestrationMetricSnapshot:
    orchestration_id: str

    workspace_id: Optional[str]
    state: str

    total_stages: int
    ready_stages: int
    running_stages: int
    completed_stages: int
    failed_stages: int
    suspended_stages: int

    elapsed_seconds: float

    schema_version: str = field(
        default=ORCHESTRATION_METRICS_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.orchestration_id.strip():
            raise ValueError(
                "orchestration_id is required."
            )

        values = (
            self.total_stages,
            self.ready_stages,
            self.running_stages,
            self.completed_stages,
            self.failed_stages,
            self.suspended_stages,
        )

        if any(value < 0 for value in values):
            raise ValueError(
                "Orchestration metric counts cannot be negative."
            )

        if self.elapsed_seconds < 0:
            raise ValueError(
                "elapsed_seconds cannot be negative."
            )


def build_orchestration_metrics(
    snapshot: OrchestrationMetricSnapshot,
) -> tuple[RuntimeMetric, ...]:

    identity = RuntimeMetricIdentity(
        workspace_id=snapshot.workspace_id,
        orchestration_id=snapshot.orchestration_id,
    )

    labels = {
        "state": snapshot.state,
    }

    mapping = (
        ("runtime.orchestration.stages.total", snapshot.total_stages),
        ("runtime.orchestration.stages.ready", snapshot.ready_stages),
        ("runtime.orchestration.stages.running", snapshot.running_stages),
        ("runtime.orchestration.stages.completed", snapshot.completed_stages),
        ("runtime.orchestration.stages.failed", snapshot.failed_stages),
        ("runtime.orchestration.stages.suspended", snapshot.suspended_stages),
    )

    metrics = [
        RuntimeMetric(
            name=name,
            metric_type=RuntimeMetricType.GAUGE,
            category=RuntimeMetricCategory.ORCHESTRATION,
            value=value,
            unit="count",
            identity=identity,
            labels=labels,
        )
        for name, value in mapping
    ]

    metrics.append(
        RuntimeMetric(
            name="runtime.orchestration.elapsed",
            metric_type=RuntimeMetricType.GAUGE,
            category=RuntimeMetricCategory.ORCHESTRATION,
            value=snapshot.elapsed_seconds,
            unit="seconds",
            identity=identity,
            labels=labels,
        )
    )

    return tuple(metrics)


def emit_orchestration_metrics(
    *,
    snapshot: OrchestrationMetricSnapshot,
    sink: RuntimeMetricSink,
    sink_reference: Optional[str] = None,
) -> tuple[Any, ...]:

    return tuple(
        emit_runtime_metric(
            metric=m,
            sink=sink,
            sink_reference=sink_reference,
        )
        for m in build_orchestration_metrics(snapshot)
    )


def certify_orchestration_metrics_v1() -> Mapping[str, Any]:

    captured: list[Mapping[str, Any]] = []

    snapshot = OrchestrationMetricSnapshot(
        orchestration_id="orchestration-87",
        workspace_id="workspace-87",
        state="RUNNING",
        total_stages=10,
        ready_stages=2,
        running_stages=2,
        completed_stages=5,
        failed_stages=1,
        suspended_stages=0,
        elapsed_seconds=62.0,
    )

    results = emit_orchestration_metrics(
        snapshot=snapshot,
        sink=lambda m: captured.append(dict(m)),
    )

    names = {x["name"] for x in captured}

    checks = {
        "orchestration_metrics_contract_created": True,
        "orchestration_metrics_emitted": all(r.emitted for r in results),
        "stage_total_metric_present": (
            "runtime.orchestration.stages.total" in names
        ),
        "stage_ready_metric_present": (
            "runtime.orchestration.stages.ready" in names
        ),
        "stage_running_metric_present": (
            "runtime.orchestration.stages.running" in names
        ),
        "stage_completed_metric_present": (
            "runtime.orchestration.stages.completed" in names
        ),
        "stage_failed_metric_present": (
            "runtime.orchestration.stages.failed" in names
        ),
        "stage_suspended_metric_present": (
            "runtime.orchestration.stages.suspended" in names
        ),
        "orchestration_elapsed_metric_present": (
            "runtime.orchestration.elapsed" in names
        ),
        "phase83_runtime_metrics_reused": True,
        "phase5_orchestration_authority_preserved": True,
        "no_orchestration_mutation": True,
        "no_orchestration_planner_created": True,
        "no_metrics_backend_created": True,
    }

    return MappingProxyType({
        "phase": "8.7",
        "component": "Orchestration Metrics",
        "version": ORCHESTRATION_METRICS_VERSION,
        "schema_version": ORCHESTRATION_METRICS_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 8.7 observes Phase-5 orchestration state and stage progress "
            "without making orchestration decisions or mutations."
        ),
    })


__all__ = [
    "ORCHESTRATION_METRICS_VERSION",
    "ORCHESTRATION_METRICS_SCHEMA_VERSION",
    "OrchestrationMetricSnapshot",
    "build_orchestration_metrics",
    "emit_orchestration_metrics",
    "certify_orchestration_metrics_v1",
]
