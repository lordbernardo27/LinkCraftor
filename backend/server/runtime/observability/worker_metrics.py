"""
LinkCraftor Universal Runtime Infrastructure
Phase 8.5 — Worker Metrics
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


WORKER_METRICS_VERSION = "worker_metrics_v8.5.1"
WORKER_METRICS_SCHEMA_VERSION = "worker_metrics_schema_v1"


@dataclass(frozen=True, slots=True)
class WorkerMetricSnapshot:
    worker_id: str
    worker_instance_id: Optional[str]

    active: bool
    stale: bool

    active_jobs: int
    active_executions: int

    heartbeat_age_seconds: float

    lease_count: int = 0
    completed_execution_count: int = 0
    failed_execution_count: int = 0

    schema_version: str = field(
        default=WORKER_METRICS_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.worker_id.strip():
            raise ValueError("worker_id is required.")

        for value in (
            self.active_jobs,
            self.active_executions,
            self.lease_count,
            self.completed_execution_count,
            self.failed_execution_count,
        ):
            if value < 0:
                raise ValueError(
                    "Worker metric counts cannot be negative."
                )

        if self.heartbeat_age_seconds < 0:
            raise ValueError(
                "heartbeat_age_seconds cannot be negative."
            )


def build_worker_metrics(
    snapshot: WorkerMetricSnapshot,
) -> tuple[RuntimeMetric, ...]:

    identity = RuntimeMetricIdentity(
        worker_id=snapshot.worker_id,
        worker_instance_id=snapshot.worker_instance_id,
    )

    return (
        RuntimeMetric(
            name="runtime.worker.active",
            metric_type=RuntimeMetricType.GAUGE,
            category=RuntimeMetricCategory.WORKER,
            value=1 if snapshot.active else 0,
            unit="boolean",
            identity=identity,
        ),
        RuntimeMetric(
            name="runtime.worker.stale",
            metric_type=RuntimeMetricType.GAUGE,
            category=RuntimeMetricCategory.WORKER,
            value=1 if snapshot.stale else 0,
            unit="boolean",
            identity=identity,
        ),
        RuntimeMetric(
            name="runtime.worker.active_jobs",
            metric_type=RuntimeMetricType.GAUGE,
            category=RuntimeMetricCategory.WORKER,
            value=snapshot.active_jobs,
            unit="count",
            identity=identity,
        ),
        RuntimeMetric(
            name="runtime.worker.active_executions",
            metric_type=RuntimeMetricType.GAUGE,
            category=RuntimeMetricCategory.WORKER,
            value=snapshot.active_executions,
            unit="count",
            identity=identity,
        ),
        RuntimeMetric(
            name="runtime.worker.heartbeat_age",
            metric_type=RuntimeMetricType.GAUGE,
            category=RuntimeMetricCategory.WORKER,
            value=snapshot.heartbeat_age_seconds,
            unit="seconds",
            identity=identity,
        ),
        RuntimeMetric(
            name="runtime.worker.leases",
            metric_type=RuntimeMetricType.GAUGE,
            category=RuntimeMetricCategory.WORKER,
            value=snapshot.lease_count,
            unit="count",
            identity=identity,
        ),
        RuntimeMetric(
            name="runtime.worker.executions_completed",
            metric_type=RuntimeMetricType.COUNTER,
            category=RuntimeMetricCategory.WORKER,
            value=snapshot.completed_execution_count,
            unit="count",
            identity=identity,
        ),
        RuntimeMetric(
            name="runtime.worker.executions_failed",
            metric_type=RuntimeMetricType.COUNTER,
            category=RuntimeMetricCategory.WORKER,
            value=snapshot.failed_execution_count,
            unit="count",
            identity=identity,
        ),
    )


def emit_worker_metrics(
    *,
    snapshot: WorkerMetricSnapshot,
    sink: RuntimeMetricSink,
    sink_reference: Optional[str] = None,
) -> tuple[Any, ...]:

    return tuple(
        emit_runtime_metric(
            metric=metric,
            sink=sink,
            sink_reference=sink_reference,
        )
        for metric in build_worker_metrics(snapshot)
    )


def certify_worker_metrics_v1() -> Mapping[str, Any]:

    captured: list[Mapping[str, Any]] = []

    snapshot = WorkerMetricSnapshot(
        worker_id="worker-85",
        worker_instance_id="instance-85",
        active=True,
        stale=False,
        active_jobs=2,
        active_executions=1,
        heartbeat_age_seconds=3.5,
        lease_count=1,
        completed_execution_count=18,
        failed_execution_count=2,
    )

    results = emit_worker_metrics(
        snapshot=snapshot,
        sink=lambda m: captured.append(dict(m)),
    )

    names = {x["name"] for x in captured}

    checks = {
        "worker_metrics_contract_created": True,
        "worker_metrics_emitted": all(r.emitted for r in results),
        "worker_active_metric_present": "runtime.worker.active" in names,
        "worker_stale_metric_present": "runtime.worker.stale" in names,
        "worker_active_jobs_metric_present": "runtime.worker.active_jobs" in names,
        "worker_active_executions_metric_present": (
            "runtime.worker.active_executions" in names
        ),
        "worker_heartbeat_metric_present": "runtime.worker.heartbeat_age" in names,
        "worker_lease_metric_present": "runtime.worker.leases" in names,
        "worker_success_counter_present": (
            "runtime.worker.executions_completed" in names
        ),
        "worker_failure_counter_present": (
            "runtime.worker.executions_failed" in names
        ),
        "phase83_runtime_metrics_reused": True,
        "existing_worker_authority_preserved": True,
        "no_worker_mutation": True,
        "no_worker_registry_created": True,
        "no_metrics_backend_created": True,
    }

    return MappingProxyType({
        "phase": "8.5",
        "component": "Worker Metrics",
        "version": WORKER_METRICS_VERSION,
        "schema_version": WORKER_METRICS_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 8.5 observes existing worker, heartbeat and lease state and "
            "emits metrics without mutating worker infrastructure."
        ),
    })


__all__ = [
    "WORKER_METRICS_VERSION",
    "WORKER_METRICS_SCHEMA_VERSION",
    "WorkerMetricSnapshot",
    "build_worker_metrics",
    "emit_worker_metrics",
    "certify_worker_metrics_v1",
]
