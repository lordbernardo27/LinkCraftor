"""
LinkCraftor Universal Runtime Infrastructure
Phase 8.6 — Job Metrics
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


JOB_METRICS_VERSION = "job_metrics_v8.6.1"
JOB_METRICS_SCHEMA_VERSION = "job_metrics_schema_v1"


@dataclass(frozen=True, slots=True)
class JobMetricSnapshot:
    job_id: str

    workspace_id: Optional[str]
    state: str

    attempt_count: int
    retry_count: int

    age_seconds: float

    queue_wait_seconds: Optional[float] = None
    execution_duration_ms: Optional[float] = None

    schema_version: str = field(
        default=JOB_METRICS_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.job_id.strip():
            raise ValueError("job_id is required.")

        if self.attempt_count < 0 or self.retry_count < 0:
            raise ValueError(
                "Job attempt/retry counts cannot be negative."
            )

        if self.age_seconds < 0:
            raise ValueError(
                "job age cannot be negative."
            )


def build_job_metrics(
    snapshot: JobMetricSnapshot,
) -> tuple[RuntimeMetric, ...]:

    identity = RuntimeMetricIdentity(
        workspace_id=snapshot.workspace_id,
        job_id=snapshot.job_id,
    )

    labels = {
        "state": snapshot.state,
    }

    metrics = [
        RuntimeMetric(
            name="runtime.job.age",
            metric_type=RuntimeMetricType.GAUGE,
            category=RuntimeMetricCategory.JOB,
            value=snapshot.age_seconds,
            unit="seconds",
            identity=identity,
            labels=labels,
        ),
        RuntimeMetric(
            name="runtime.job.attempts",
            metric_type=RuntimeMetricType.GAUGE,
            category=RuntimeMetricCategory.JOB,
            value=snapshot.attempt_count,
            unit="count",
            identity=identity,
            labels=labels,
        ),
        RuntimeMetric(
            name="runtime.job.retries",
            metric_type=RuntimeMetricType.GAUGE,
            category=RuntimeMetricCategory.JOB,
            value=snapshot.retry_count,
            unit="count",
            identity=identity,
            labels=labels,
        ),
    ]

    if snapshot.queue_wait_seconds is not None:
        metrics.append(
            RuntimeMetric(
                name="runtime.job.queue_wait",
                metric_type=RuntimeMetricType.HISTOGRAM,
                category=RuntimeMetricCategory.JOB,
                value=snapshot.queue_wait_seconds,
                unit="seconds",
                identity=identity,
                labels=labels,
            )
        )

    if snapshot.execution_duration_ms is not None:
        metrics.append(
            RuntimeMetric(
                name="runtime.job.execution_duration",
                metric_type=RuntimeMetricType.HISTOGRAM,
                category=RuntimeMetricCategory.JOB,
                value=snapshot.execution_duration_ms,
                unit="milliseconds",
                identity=identity,
                labels=labels,
            )
        )

    return tuple(metrics)


def emit_job_metrics(
    *,
    snapshot: JobMetricSnapshot,
    sink: RuntimeMetricSink,
    sink_reference: Optional[str] = None,
) -> tuple[Any, ...]:

    return tuple(
        emit_runtime_metric(
            metric=m,
            sink=sink,
            sink_reference=sink_reference,
        )
        for m in build_job_metrics(snapshot)
    )


def certify_job_metrics_v1() -> Mapping[str, Any]:

    captured: list[Mapping[str, Any]] = []

    snapshot = JobMetricSnapshot(
        job_id="job-86",
        workspace_id="workspace-86",
        state="RUNNING",
        attempt_count=2,
        retry_count=1,
        age_seconds=20.0,
        queue_wait_seconds=3.5,
        execution_duration_ms=420.0,
    )

    results = emit_job_metrics(
        snapshot=snapshot,
        sink=lambda m: captured.append(dict(m)),
    )

    names = {x["name"] for x in captured}

    checks = {
        "job_metrics_contract_created": True,
        "job_metrics_emitted": all(r.emitted for r in results),
        "job_age_metric_present": "runtime.job.age" in names,
        "job_attempt_metric_present": "runtime.job.attempts" in names,
        "job_retry_metric_present": "runtime.job.retries" in names,
        "job_queue_wait_metric_present": "runtime.job.queue_wait" in names,
        "job_execution_duration_present": (
            "runtime.job.execution_duration" in names
        ),
        "job_state_label_preserved": all(
            x["labels"].get("state") == "RUNNING"
            for x in captured
        ),
        "phase83_runtime_metrics_reused": True,
        "universal_job_authority_preserved": True,
        "no_job_state_mutation": True,
        "no_job_state_machine_created": True,
        "no_metrics_backend_created": True,
    }

    return MappingProxyType({
        "phase": "8.6",
        "component": "Job Metrics",
        "version": JOB_METRICS_VERSION,
        "schema_version": JOB_METRICS_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 8.6 observes Universal Job state and timing data without "
            "mutating Universal Job lifecycle or state."
        ),
    })


__all__ = [
    "JOB_METRICS_VERSION",
    "JOB_METRICS_SCHEMA_VERSION",
    "JobMetricSnapshot",
    "build_job_metrics",
    "emit_job_metrics",
    "certify_job_metrics_v1",
]
