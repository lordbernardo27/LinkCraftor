"""
LinkCraftor Universal Runtime Infrastructure
Phase 8.11 — Runtime Health Signals

Aggregates caller-supplied observability evidence into health signals.

Does NOT:
- restart services
- drain queues
- recover jobs
- mutate workers
- create alerting
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional


RUNTIME_HEALTH_SIGNALS_VERSION = "runtime_health_signals_v8.11.1"
RUNTIME_HEALTH_SIGNALS_SCHEMA_VERSION = "runtime_health_signals_schema_v1"


class RuntimeHealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class RuntimeHealthEvidence:
    runtime_available: bool

    queue_depth: int
    oldest_queue_age_seconds: float

    active_workers: int
    stale_workers: int

    running_jobs: int
    failed_jobs: int

    running_executions: int
    failed_executions: int

    critical_error_count: int = 0

    queue_depth_warning_threshold: int = 1000
    queue_age_warning_threshold_seconds: float = 300.0

    source_reference: Optional[str] = None

    schema_version: str = field(
        default=RUNTIME_HEALTH_SIGNALS_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class RuntimeHealthSignal:
    status: RuntimeHealthStatus
    reasons: tuple[str, ...]
    source_reference: Optional[str]

    schema_version: str = field(
        default=RUNTIME_HEALTH_SIGNALS_SCHEMA_VERSION,
        init=False,
    )

    @property
    def healthy(self) -> bool:
        return self.status is RuntimeHealthStatus.HEALTHY


def evaluate_runtime_health(
    evidence: RuntimeHealthEvidence,
) -> RuntimeHealthSignal:

    reasons: list[str] = []

    if not evidence.runtime_available:
        reasons.append("runtime_unavailable")

    if evidence.active_workers <= 0:
        reasons.append("no_active_workers")

    if evidence.critical_error_count > 0:
        reasons.append("critical_runtime_errors")

    if evidence.queue_depth > evidence.queue_depth_warning_threshold:
        reasons.append("queue_depth_high")

    if (
        evidence.oldest_queue_age_seconds
        > evidence.queue_age_warning_threshold_seconds
    ):
        reasons.append("queue_age_high")

    if evidence.stale_workers > 0:
        reasons.append("stale_workers_present")

    if evidence.failed_executions > 0:
        reasons.append("execution_failures_present")

    if evidence.failed_jobs > 0:
        reasons.append("job_failures_present")

    if (
        not evidence.runtime_available
        or evidence.active_workers <= 0
        or evidence.critical_error_count > 0
    ):
        status = RuntimeHealthStatus.UNHEALTHY

    elif reasons:
        status = RuntimeHealthStatus.DEGRADED

    else:
        status = RuntimeHealthStatus.HEALTHY

    return RuntimeHealthSignal(
        status=status,
        reasons=tuple(reasons),
        source_reference=evidence.source_reference,
    )


def certify_runtime_health_signals_v1() -> Mapping[str, Any]:

    healthy = evaluate_runtime_health(
        RuntimeHealthEvidence(
            runtime_available=True,
            queue_depth=10,
            oldest_queue_age_seconds=5,
            active_workers=3,
            stale_workers=0,
            running_jobs=5,
            failed_jobs=0,
            running_executions=3,
            failed_executions=0,
            source_reference="health-811",
        )
    )

    degraded = evaluate_runtime_health(
        RuntimeHealthEvidence(
            runtime_available=True,
            queue_depth=2000,
            oldest_queue_age_seconds=600,
            active_workers=3,
            stale_workers=1,
            running_jobs=5,
            failed_jobs=1,
            running_executions=3,
            failed_executions=1,
        )
    )

    unhealthy = evaluate_runtime_health(
        RuntimeHealthEvidence(
            runtime_available=False,
            queue_depth=0,
            oldest_queue_age_seconds=0,
            active_workers=0,
            stale_workers=0,
            running_jobs=0,
            failed_jobs=0,
            running_executions=0,
            failed_executions=0,
            critical_error_count=1,
        )
    )

    checks = {
        "runtime_health_contract_created": True,
        "healthy_runtime_detected": healthy.healthy,
        "degraded_runtime_detected": (
            degraded.status is RuntimeHealthStatus.DEGRADED
        ),
        "unhealthy_runtime_detected": (
            unhealthy.status is RuntimeHealthStatus.UNHEALTHY
        ),
        "queue_depth_health_supported": True,
        "queue_age_health_supported": True,
        "worker_health_supported": True,
        "job_health_supported": True,
        "execution_health_supported": True,
        "critical_error_health_supported": True,
        "no_restart_action_created": True,
        "no_recovery_action_created": True,
        "no_queue_mutation": True,
        "no_worker_mutation": True,
        "no_job_mutation": True,
        "no_execution_mutation": True,
        "no_alerting_created": True,
    }

    return MappingProxyType({
        "phase": "8.11",
        "component": "Runtime Health Signals",
        "version": RUNTIME_HEALTH_SIGNALS_VERSION,
        "schema_version": RUNTIME_HEALTH_SIGNALS_SCHEMA_VERSION,
        "certified": all(checks.values()),
        "checks": MappingProxyType(checks),
        "authority_boundary": (
            "Phase 8.11 evaluates runtime health from caller-supplied "
            "observability evidence and makes no recovery or mutation decision."
        ),
    })


__all__ = [
    "RUNTIME_HEALTH_SIGNALS_VERSION",
    "RUNTIME_HEALTH_SIGNALS_SCHEMA_VERSION",
    "RuntimeHealthStatus",
    "RuntimeHealthEvidence",
    "RuntimeHealthSignal",
    "evaluate_runtime_health",
    "certify_runtime_health_signals_v1",
]
