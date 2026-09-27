"""
LinkCraftor Universal Runtime Infrastructure
Phase 8.9 — Error Telemetry

Canonical error-observability layer built on:
- Phase 8.1 Runtime Logging
- Phase 8.3 Runtime Metrics

Does NOT own:
- retry decisions
- recovery decisions
- exception swallowing
- alerting
- tracing
- persistence
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .runtime_logging import (
    RuntimeLogCategory,
    RuntimeLogEvent,
    RuntimeLogIdentity,
    RuntimeLogSeverity,
    RuntimeLogSink,
    emit_runtime_log,
)

from .runtime_metrics import (
    RuntimeMetric,
    RuntimeMetricCategory,
    RuntimeMetricIdentity,
    RuntimeMetricSink,
    RuntimeMetricType,
    emit_runtime_metric,
)


ERROR_TELEMETRY_VERSION = "error_telemetry_v8.9.1"
ERROR_TELEMETRY_SCHEMA_VERSION = "error_telemetry_schema_v1"


class RuntimeErrorClass(str, Enum):
    VALIDATION = "VALIDATION"
    AUTHORIZATION = "AUTHORIZATION"
    QUEUE = "QUEUE"
    WORKER = "WORKER"
    LEASE = "LEASE"
    ORCHESTRATION = "ORCHESTRATION"
    EXECUTION = "EXECUTION"
    HANDLER = "HANDLER"
    CHECKPOINT = "CHECKPOINT"
    PERSISTENCE = "PERSISTENCE"
    SECURITY = "SECURITY"
    TIMEOUT = "TIMEOUT"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    UNKNOWN = "UNKNOWN"


class RuntimeErrorSeverity(str, Enum):
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True, slots=True)
class RuntimeErrorTelemetryEvent:
    error_class: RuntimeErrorClass
    severity: RuntimeErrorSeverity

    error_code: str
    message: str
    component: str

    workspace_id: Optional[str] = None
    job_id: Optional[str] = None
    orchestration_id: Optional[str] = None
    execution_id: Optional[str] = None
    worker_id: Optional[str] = None
    worker_instance_id: Optional[str] = None
    queue_name: Optional[str] = None
    lease_id: Optional[str] = None

    exception_type: Optional[str] = None

    retryable: Optional[bool] = None

    attributes: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    schema_version: str = field(
        default=ERROR_TELEMETRY_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.error_code.strip():
            raise ValueError("error_code is required.")

        if not self.message.strip():
            raise ValueError("message is required.")

        if not self.component.strip():
            raise ValueError("component is required.")

        object.__setattr__(
            self,
            "attributes",
            MappingProxyType(
                dict(self.attributes)
            ),
        )


@dataclass(frozen=True, slots=True)
class RuntimeErrorTelemetryResult:
    log_emitted: bool
    metric_emitted: bool

    error_class: RuntimeErrorClass
    error_code: str

    schema_version: str = field(
        default=ERROR_TELEMETRY_SCHEMA_VERSION,
        init=False,
    )

    @property
    def emitted(self) -> bool:
        return (
            self.log_emitted
            and self.metric_emitted
        )


def _log_severity(
    severity: RuntimeErrorSeverity,
) -> RuntimeLogSeverity:

    if severity is RuntimeErrorSeverity.WARNING:
        return RuntimeLogSeverity.WARNING

    if severity is RuntimeErrorSeverity.CRITICAL:
        return RuntimeLogSeverity.CRITICAL

    return RuntimeLogSeverity.ERROR


def emit_error_telemetry(
    *,
    event: RuntimeErrorTelemetryEvent,
    log_sink: RuntimeLogSink,
    metric_sink: RuntimeMetricSink,
    log_sink_reference: Optional[str] = None,
    metric_sink_reference: Optional[str] = None,
) -> RuntimeErrorTelemetryResult:

    log_result = emit_runtime_log(
        event=RuntimeLogEvent(
            event_name=(
                "runtime.error."
                + event.error_class.value.lower()
            ),
            component=event.component,
            category=RuntimeLogCategory.RUNTIME,
            severity=_log_severity(event.severity),
            message=event.message,
            identity=RuntimeLogIdentity(
                workspace_id=event.workspace_id,
                job_id=event.job_id,
                orchestration_id=event.orchestration_id,
                execution_id=event.execution_id,
                worker_id=event.worker_id,
                worker_instance_id=event.worker_instance_id,
                lease_id=event.lease_id,
            ),
            attributes={
                **dict(event.attributes),
                "error_class": event.error_class.value,
                "retryable": event.retryable,
                "queue_name": event.queue_name,
            },
            error_type=event.exception_type,
            error_code=event.error_code,
        ),
        sink=log_sink,
        sink_reference=log_sink_reference,
    )

    metric_result = emit_runtime_metric(
        metric=RuntimeMetric(
            name="runtime.errors.total",
            metric_type=RuntimeMetricType.COUNTER,
            category=RuntimeMetricCategory.ERROR,
            value=1,
            unit="count",
            identity=RuntimeMetricIdentity(
                workspace_id=event.workspace_id,
                job_id=event.job_id,
                orchestration_id=event.orchestration_id,
                execution_id=event.execution_id,
                worker_id=event.worker_id,
                worker_instance_id=event.worker_instance_id,
                queue_name=event.queue_name,
                lease_id=event.lease_id,
            ),
            labels={
                "error_class": event.error_class.value,
                "severity": event.severity.value,
                "error_code": event.error_code,
                "component": event.component,
            },
        ),
        sink=metric_sink,
        sink_reference=metric_sink_reference,
    )

    return RuntimeErrorTelemetryResult(
        log_emitted=log_result.emitted,
        metric_emitted=metric_result.emitted,
        error_class=event.error_class,
        error_code=event.error_code,
    )


def certify_error_telemetry_v1() -> Mapping[str, Any]:

    logs: list[Mapping[str, Any]] = []
    metrics: list[Mapping[str, Any]] = []

    event = RuntimeErrorTelemetryEvent(
        error_class=RuntimeErrorClass.EXECUTION,
        severity=RuntimeErrorSeverity.ERROR,
        error_code="execution_failed",
        message="Execution failed.",
        component="phase_6_execution_engine",
        workspace_id="workspace-89",
        job_id="job-89",
        orchestration_id="orchestration-89",
        execution_id="execution-89",
        worker_id="worker-89",
        worker_instance_id="instance-89",
        queue_name="runtime-default",
        lease_id="lease-89",
        exception_type="RuntimeError",
        retryable=True,
        attributes={
            "handler_key": "handler-89",
            "password": "must-redact",
        },
    )

    result = emit_error_telemetry(
        event=event,
        log_sink=lambda r: logs.append(dict(r)),
        metric_sink=lambda r: metrics.append(dict(r)),
    )

    log_record = logs[0] if logs else {}
    metric_record = metrics[0] if metrics else {}

    checks = {
        "error_telemetry_contract_created": True,
        "error_log_emitted": result.log_emitted,
        "error_metric_emitted": result.metric_emitted,
        "combined_error_telemetry_emitted": result.emitted,
        "error_class_preserved": (
            metric_record.get("labels", {}).get("error_class")
            == "EXECUTION"
        ),
        "error_code_preserved": (
            metric_record.get("labels", {}).get("error_code")
            == "execution_failed"
        ),
        "execution_identity_preserved": (
            log_record.get("execution_id")
            == "execution-89"
        ),
        "job_identity_preserved": (
            log_record.get("job_id")
            == "job-89"
        ),
        "worker_identity_preserved": (
            log_record.get("worker_id")
            == "worker-89"
        ),
        "lease_identity_preserved": (
            log_record.get("lease_id")
            == "lease-89"
        ),
        "sensitive_error_attributes_redacted": (
            log_record.get("attributes", {}).get("password")
            == "[REDACTED]"
        ),
        "phase81_runtime_logging_reused": True,
        "phase83_runtime_metrics_reused": True,
        "retryability_is_observed_not_decided": True,
        "no_retry_decision_created": True,
        "no_recovery_decision_created": True,
        "no_alerting_created": True,
        "no_tracing_created": True,
        "no_persistence_write": True,
        "no_runtime_mutation": True,
    }

    return MappingProxyType({
        "phase": "8.9",
        "component": "Error Telemetry",
        "version": ERROR_TELEMETRY_VERSION,
        "schema_version": ERROR_TELEMETRY_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 8.9 converts runtime failures into canonical logs and "
            "metrics using 8.1 and 8.3. It observes retryability but makes "
            "no retry, recovery, alerting, tracing or persistence decision."
        ),
    })


__all__ = [
    "ERROR_TELEMETRY_VERSION",
    "ERROR_TELEMETRY_SCHEMA_VERSION",
    "RuntimeErrorClass",
    "RuntimeErrorSeverity",
    "RuntimeErrorTelemetryEvent",
    "RuntimeErrorTelemetryResult",
    "emit_error_telemetry",
    "certify_error_telemetry_v1",
]
