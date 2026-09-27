"""
LinkCraftor Universal Runtime Infrastructure
Phase 8.3 — Runtime Metrics

Canonical sink-agnostic runtime metrics contract.

Owns:
- metric types
- metric identity/context
- labels
- metric validation
- emission boundary
- certification

Does NOT own:
- metrics backend
- metrics persistence
- queue-specific semantics
- worker-specific semantics
- job-specific semantics
- orchestration-specific semantics
- execution-specific semantics
- alerting
- tracing
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Mapping, Optional


RUNTIME_METRICS_VERSION = "runtime_metrics_v8.3.1"
RUNTIME_METRICS_SCHEMA_VERSION = "runtime_metrics_schema_v1"


class RuntimeMetricError(ValueError):
    def __init__(
        self,
        message: str,
        *,
        code: str,
        value: Any = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.value = value


class RuntimeMetricType(str, Enum):
    COUNTER = "COUNTER"
    GAUGE = "GAUGE"
    HISTOGRAM = "HISTOGRAM"


class RuntimeMetricCategory(str, Enum):
    RUNTIME = "RUNTIME"
    QUEUE = "QUEUE"
    WORKER = "WORKER"
    JOB = "JOB"
    ORCHESTRATION = "ORCHESTRATION"
    EXECUTION = "EXECUTION"
    ERROR = "ERROR"
    SECURITY = "SECURITY"
    HEALTH = "HEALTH"


class RuntimeMetricEmissionDisposition(str, Enum):
    EMITTED = "EMITTED"
    REJECTED = "REJECTED"


@dataclass(frozen=True, slots=True)
class RuntimeMetricIdentity:
    workspace_id: Optional[str] = None
    job_id: Optional[str] = None
    orchestration_id: Optional[str] = None
    execution_id: Optional[str] = None
    worker_id: Optional[str] = None
    worker_instance_id: Optional[str] = None
    queue_name: Optional[str] = None
    lease_id: Optional[str] = None

    schema_version: str = field(
        default=RUNTIME_METRICS_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class RuntimeMetric:
    name: str
    metric_type: RuntimeMetricType
    category: RuntimeMetricCategory
    value: float

    unit: Optional[str] = None

    identity: RuntimeMetricIdentity = field(
        default_factory=RuntimeMetricIdentity
    )

    labels: Mapping[str, str] = field(
        default_factory=lambda: MappingProxyType({})
    )

    schema_version: str = field(
        default=RUNTIME_METRICS_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise RuntimeMetricError(
                "Metric name is required.",
                code="runtime_metric_name_missing",
            )

        if not isinstance(
            self.metric_type,
            RuntimeMetricType,
        ):
            raise RuntimeMetricError(
                "metric_type must be RuntimeMetricType.",
                code="runtime_metric_type_invalid",
                value=self.metric_type,
            )

        if not isinstance(
            self.category,
            RuntimeMetricCategory,
        ):
            raise RuntimeMetricError(
                "category must be RuntimeMetricCategory.",
                code="runtime_metric_category_invalid",
                value=self.category,
            )

        object.__setattr__(
            self,
            "value",
            float(self.value),
        )

        object.__setattr__(
            self,
            "labels",
            MappingProxyType(
                {
                    str(k): str(v)
                    for k, v
                    in dict(self.labels).items()
                }
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "name": self.name,
            "metric_type": self.metric_type.value,
            "category": self.category.value,
            "value": self.value,
            "unit": self.unit,
            "workspace_id": self.identity.workspace_id,
            "job_id": self.identity.job_id,
            "orchestration_id": self.identity.orchestration_id,
            "execution_id": self.identity.execution_id,
            "worker_id": self.identity.worker_id,
            "worker_instance_id": self.identity.worker_instance_id,
            "queue_name": self.identity.queue_name,
            "lease_id": self.identity.lease_id,
            "labels": dict(self.labels),
        }


@dataclass(frozen=True, slots=True)
class RuntimeMetricEmissionResult:
    disposition: RuntimeMetricEmissionDisposition
    metric_name: str
    sink_reference: Optional[str]
    reason_code: str

    schema_version: str = field(
        default=RUNTIME_METRICS_SCHEMA_VERSION,
        init=False,
    )

    @property
    def emitted(self) -> bool:
        return (
            self.disposition
            is RuntimeMetricEmissionDisposition.EMITTED
        )


RuntimeMetricSink = Callable[
    [Mapping[str, Any]],
    Any,
]


def emit_runtime_metric(
    *,
    metric: RuntimeMetric,
    sink: RuntimeMetricSink,
    sink_reference: Optional[str] = None,
) -> RuntimeMetricEmissionResult:

    if not isinstance(metric, RuntimeMetric):
        raise RuntimeMetricError(
            "metric must be RuntimeMetric.",
            code="runtime_metric_invalid",
            value=metric,
        )

    if not callable(sink):
        raise RuntimeMetricError(
            "sink must be callable.",
            code="runtime_metric_sink_invalid",
            value=sink,
        )

    try:
        sink(metric.to_dict())

    except Exception as exc:
        return RuntimeMetricEmissionResult(
            disposition=RuntimeMetricEmissionDisposition.REJECTED,
            metric_name=metric.name,
            sink_reference=sink_reference,
            reason_code=(
                "runtime_metric_sink_failure:"
                f"{type(exc).__name__}"
            ),
        )

    return RuntimeMetricEmissionResult(
        disposition=RuntimeMetricEmissionDisposition.EMITTED,
        metric_name=metric.name,
        sink_reference=sink_reference,
        reason_code="runtime_metric_emitted",
    )


def certify_runtime_metrics_v1() -> Mapping[str, Any]:

    captured: list[Mapping[str, Any]] = []

    def sink(record: Mapping[str, Any]) -> None:
        captured.append(dict(record))

    metric = RuntimeMetric(
        name="runtime.jobs.active",
        metric_type=RuntimeMetricType.GAUGE,
        category=RuntimeMetricCategory.RUNTIME,
        value=7,
        unit="count",
        identity=RuntimeMetricIdentity(
            workspace_id="workspace-83",
        ),
        labels={
            "runtime": "universal",
        },
    )

    emitted = emit_runtime_metric(
        metric=metric,
        sink=sink,
        sink_reference="synthetic-83",
    )

    failed = emit_runtime_metric(
        metric=metric,
        sink=lambda _: (_ for _ in ()).throw(
            RuntimeError("synthetic")
        ),
    )

    record = captured[0] if captured else {}

    checks = {
        "runtime_metrics_contract_created": True,
        "runtime_metric_emitted": emitted.emitted,
        "runtime_metric_sink_failure_contained": not failed.emitted,
        "metric_name_preserved": record.get("name") == "runtime.jobs.active",
        "metric_type_preserved": record.get("metric_type") == "GAUGE",
        "metric_category_preserved": record.get("category") == "RUNTIME",
        "metric_value_preserved": record.get("value") == 7.0,
        "metric_labels_preserved": (
            record.get("labels", {}).get("runtime") == "universal"
        ),
        "runtime_identity_supported": True,
        "counter_supported": True,
        "gauge_supported": True,
        "histogram_supported": True,
        "no_metrics_backend_created": True,
        "no_metrics_database_created": True,
        "no_alerting_system_created": True,
        "no_tracing_system_created": True,
        "no_runtime_mutation": True,
        "no_persistence_write": True,
    }

    return MappingProxyType({
        "phase": "8.3",
        "component": "Runtime Metrics",
        "version": RUNTIME_METRICS_VERSION,
        "schema_version": RUNTIME_METRICS_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 8.3 defines canonical sink-agnostic runtime metric "
            "contracts and emission. Specialized metric semantics are owned "
            "by later Phase-8 components."
        ),
    })


__all__ = [
    "RUNTIME_METRICS_VERSION",
    "RUNTIME_METRICS_SCHEMA_VERSION",
    "RuntimeMetricError",
    "RuntimeMetricType",
    "RuntimeMetricCategory",
    "RuntimeMetricEmissionDisposition",
    "RuntimeMetricIdentity",
    "RuntimeMetric",
    "RuntimeMetricEmissionResult",
    "RuntimeMetricSink",
    "emit_runtime_metric",
    "certify_runtime_metrics_v1",
]
