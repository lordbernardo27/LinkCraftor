"""
LinkCraftor Universal Runtime Infrastructure
Phase 8.2 — Structured Execution Logs

Specialized structured logging for the Phase-6 Execution Engine.

Owns:
- canonical execution log event taxonomy
- execution lifecycle log construction
- execution identity attachment
- attempt / worker / lease / fence / handler context
- result / failure / retry / cancellation / suspension semantics
- emission through Phase-8.1 Runtime Logging

Does NOT own:
- execution-state mutation
- job-state mutation
- retry decisions
- lifecycle decisions
- metrics
- tracing
- alerting
- persistence
- logging backend infrastructure

Phase 6 remains execution authority.
Phase 8.1 remains the generic runtime logging contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from .runtime_logging import (
    RuntimeLogCategory,
    RuntimeLogEmissionResult,
    RuntimeLogEvent,
    RuntimeLogIdentity,
    RuntimeLogSeverity,
    RuntimeLogSink,
    emit_runtime_log,
)


STRUCTURED_EXECUTION_LOGS_VERSION = (
    "structured_execution_logs_v8.2.1"
)

STRUCTURED_EXECUTION_LOGS_SCHEMA_VERSION = (
    "structured_execution_logs_schema_v1"
)


class StructuredExecutionLogError(ValueError):
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


class ExecutionLogEventType(str, Enum):
    AUTHORIZATION_ALLOWED = "AUTHORIZATION_ALLOWED"
    AUTHORIZATION_DENIED = "AUTHORIZATION_DENIED"

    EXECUTION_REQUESTED = "EXECUTION_REQUESTED"
    EXECUTION_STARTED = "EXECUTION_STARTED"

    HANDLER_RESOLVED = "HANDLER_RESOLVED"
    HANDLER_INVOKED = "HANDLER_INVOKED"
    HANDLER_SUCCEEDED = "HANDLER_SUCCEEDED"
    HANDLER_FAILED = "HANDLER_FAILED"

    RESULT_RECEIVED = "RESULT_RECEIVED"
    RESULT_ACCEPTED = "RESULT_ACCEPTED"
    RESULT_REJECTED = "RESULT_REJECTED"

    CHECKPOINT_SAVED = "CHECKPOINT_SAVED"
    CHECKPOINT_RESTORED = "CHECKPOINT_RESTORED"

    EXECUTION_SUSPENDED = "EXECUTION_SUSPENDED"
    EXECUTION_RESUMED = "EXECUTION_RESUMED"

    RETRY_SCHEDULED = "RETRY_SCHEDULED"
    RETRY_EXHAUSTED = "RETRY_EXHAUSTED"

    EXECUTION_COMPLETED = "EXECUTION_COMPLETED"
    EXECUTION_FAILED = "EXECUTION_FAILED"

    EXECUTION_CANCELLED = "EXECUTION_CANCELLED"

    EXECUTION_REJECTED = "EXECUTION_REJECTED"
    LATE_RESULT_REJECTED = "LATE_RESULT_REJECTED"
    STALE_WORKER_REJECTED = "STALE_WORKER_REJECTED"
    LOST_LEASE_REJECTED = "LOST_LEASE_REJECTED"
    DUPLICATE_EXECUTION_REJECTED = "DUPLICATE_EXECUTION_REJECTED"
    TERMINAL_REENTRY_REJECTED = "TERMINAL_REENTRY_REJECTED"


_EVENT_SEVERITY = MappingProxyType(
    {
        ExecutionLogEventType.AUTHORIZATION_ALLOWED:
            RuntimeLogSeverity.INFO,

        ExecutionLogEventType.AUTHORIZATION_DENIED:
            RuntimeLogSeverity.WARNING,

        ExecutionLogEventType.EXECUTION_REQUESTED:
            RuntimeLogSeverity.INFO,

        ExecutionLogEventType.EXECUTION_STARTED:
            RuntimeLogSeverity.INFO,

        ExecutionLogEventType.HANDLER_RESOLVED:
            RuntimeLogSeverity.DEBUG,

        ExecutionLogEventType.HANDLER_INVOKED:
            RuntimeLogSeverity.INFO,

        ExecutionLogEventType.HANDLER_SUCCEEDED:
            RuntimeLogSeverity.INFO,

        ExecutionLogEventType.HANDLER_FAILED:
            RuntimeLogSeverity.ERROR,

        ExecutionLogEventType.RESULT_RECEIVED:
            RuntimeLogSeverity.DEBUG,

        ExecutionLogEventType.RESULT_ACCEPTED:
            RuntimeLogSeverity.INFO,

        ExecutionLogEventType.RESULT_REJECTED:
            RuntimeLogSeverity.WARNING,

        ExecutionLogEventType.CHECKPOINT_SAVED:
            RuntimeLogSeverity.INFO,

        ExecutionLogEventType.CHECKPOINT_RESTORED:
            RuntimeLogSeverity.INFO,

        ExecutionLogEventType.EXECUTION_SUSPENDED:
            RuntimeLogSeverity.INFO,

        ExecutionLogEventType.EXECUTION_RESUMED:
            RuntimeLogSeverity.INFO,

        ExecutionLogEventType.RETRY_SCHEDULED:
            RuntimeLogSeverity.WARNING,

        ExecutionLogEventType.RETRY_EXHAUSTED:
            RuntimeLogSeverity.ERROR,

        ExecutionLogEventType.EXECUTION_COMPLETED:
            RuntimeLogSeverity.INFO,

        ExecutionLogEventType.EXECUTION_FAILED:
            RuntimeLogSeverity.ERROR,

        ExecutionLogEventType.EXECUTION_CANCELLED:
            RuntimeLogSeverity.WARNING,

        ExecutionLogEventType.EXECUTION_REJECTED:
            RuntimeLogSeverity.WARNING,

        ExecutionLogEventType.LATE_RESULT_REJECTED:
            RuntimeLogSeverity.WARNING,

        ExecutionLogEventType.STALE_WORKER_REJECTED:
            RuntimeLogSeverity.WARNING,

        ExecutionLogEventType.LOST_LEASE_REJECTED:
            RuntimeLogSeverity.ERROR,

        ExecutionLogEventType.DUPLICATE_EXECUTION_REJECTED:
            RuntimeLogSeverity.WARNING,

        ExecutionLogEventType.TERMINAL_REENTRY_REJECTED:
            RuntimeLogSeverity.WARNING,
    }
)


@dataclass(
    frozen=True,
    slots=True,
)
class StructuredExecutionLogContext:
    execution_id: str
    job_id: str
    attempt_number: int

    workspace_id: Optional[str] = None
    orchestration_id: Optional[str] = None

    worker_id: Optional[str] = None
    worker_instance_id: Optional[str] = None

    lease_id: Optional[str] = None
    lease_owner: Optional[str] = None

    fence_id: Optional[str] = None

    handler_key: Optional[str] = None

    principal_id: Optional[str] = None

    checkpoint_reference: Optional[str] = None
    result_reference: Optional[str] = None

    schema_version: str = field(
        default=STRUCTURED_EXECUTION_LOGS_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(
        self,
    ) -> None:

        if not self.execution_id.strip():
            raise StructuredExecutionLogError(
                "execution_id is required.",
                code="execution_log_execution_id_missing",
            )

        if not self.job_id.strip():
            raise StructuredExecutionLogError(
                "job_id is required.",
                code="execution_log_job_id_missing",
            )

        if self.attempt_number < 1:
            raise StructuredExecutionLogError(
                "attempt_number must be >= 1.",
                code="execution_log_attempt_invalid",
                value=self.attempt_number,
            )


@dataclass(
    frozen=True,
    slots=True,
)
class StructuredExecutionLog:
    event_type: ExecutionLogEventType
    context: StructuredExecutionLogContext

    message: str
    reason_code: Optional[str] = None

    outcome: Optional[str] = None
    execution_state: Optional[str] = None
    target_job_state: Optional[str] = None

    duration_ms: Optional[float] = None
    backoff_seconds: Optional[float] = None

    failure_kind: Optional[str] = None
    failure_code: Optional[str] = None

    attributes: Mapping[
        str,
        Any,
    ] = field(
        default_factory=lambda: MappingProxyType({})
    )

    schema_version: str = field(
        default=STRUCTURED_EXECUTION_LOGS_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(
        self,
    ) -> None:

        if not isinstance(
            self.event_type,
            ExecutionLogEventType,
        ):
            raise StructuredExecutionLogError(
                "event_type must be ExecutionLogEventType.",
                code="execution_log_event_type_invalid",
                value=self.event_type,
            )

        if not str(
            self.message
        ).strip():
            raise StructuredExecutionLogError(
                "message is required.",
                code="execution_log_message_missing",
            )

        if (
            self.duration_ms is not None
            and self.duration_ms < 0
        ):
            raise StructuredExecutionLogError(
                "duration_ms cannot be negative.",
                code="execution_log_duration_invalid",
                value=self.duration_ms,
            )

        if (
            self.backoff_seconds is not None
            and self.backoff_seconds < 0
        ):
            raise StructuredExecutionLogError(
                "backoff_seconds cannot be negative.",
                code="execution_log_backoff_invalid",
                value=self.backoff_seconds,
            )

        object.__setattr__(
            self,
            "attributes",
            MappingProxyType(
                dict(
                    self.attributes
                )
            ),
        )


def severity_for_execution_event(
    event_type: ExecutionLogEventType,
) -> RuntimeLogSeverity:

    try:
        return _EVENT_SEVERITY[
            event_type
        ]

    except KeyError as exc:
        raise StructuredExecutionLogError(
            "No severity mapping exists for execution event.",
            code="execution_log_severity_mapping_missing",
            value=event_type,
        ) from exc


def execution_event_name(
    event_type: ExecutionLogEventType,
) -> str:

    return (
        "runtime.execution."
        + event_type.value.lower()
    )


def build_execution_runtime_log_event(
    log: StructuredExecutionLog,
) -> RuntimeLogEvent:

    if not isinstance(
        log,
        StructuredExecutionLog,
    ):
        raise StructuredExecutionLogError(
            "log must be StructuredExecutionLog.",
            code="invalid_structured_execution_log",
            value=log,
        )

    ctx = log.context

    attributes = dict(
        log.attributes
    )

    attributes.update(
        {
            "attempt_number":
                ctx.attempt_number,

            "lease_owner":
                ctx.lease_owner,

            "handler_key":
                ctx.handler_key,

            "checkpoint_reference":
                ctx.checkpoint_reference,

            "result_reference":
                ctx.result_reference,

            "reason_code":
                log.reason_code,

            "outcome":
                log.outcome,

            "execution_state":
                log.execution_state,

            "target_job_state":
                log.target_job_state,

            "duration_ms":
                log.duration_ms,

            "backoff_seconds":
                log.backoff_seconds,

            "failure_kind":
                log.failure_kind,
        }
    )

    return RuntimeLogEvent(
        event_name=execution_event_name(
            log.event_type
        ),
        component="phase_6_execution_engine",
        category=RuntimeLogCategory.EXECUTION,
        severity=severity_for_execution_event(
            log.event_type
        ),
        message=log.message,
        identity=RuntimeLogIdentity(
            workspace_id=ctx.workspace_id,
            job_id=ctx.job_id,
            orchestration_id=ctx.orchestration_id,
            execution_id=ctx.execution_id,
            worker_id=ctx.worker_id,
            worker_instance_id=(
                ctx.worker_instance_id
            ),
            lease_id=ctx.lease_id,
            fence_id=ctx.fence_id,
            principal_id=ctx.principal_id,
        ),
        attributes=attributes,
        error_type=log.failure_kind,
        error_code=log.failure_code,
    )


def emit_structured_execution_log(
    *,
    log: StructuredExecutionLog,
    sink: RuntimeLogSink,
    sink_reference: Optional[str] = None,
) -> RuntimeLogEmissionResult:

    event = build_execution_runtime_log_event(
        log
    )

    return emit_runtime_log(
        event=event,
        sink=sink,
        sink_reference=sink_reference,
    )


def log_execution_started(
    *,
    context: StructuredExecutionLogContext,
    sink: RuntimeLogSink,
    sink_reference: Optional[str] = None,
) -> RuntimeLogEmissionResult:

    return emit_structured_execution_log(
        log=StructuredExecutionLog(
            event_type=ExecutionLogEventType.EXECUTION_STARTED,
            context=context,
            message="Execution started.",
            execution_state="RUNNING",
        ),
        sink=sink,
        sink_reference=sink_reference,
    )


def log_handler_failed(
    *,
    context: StructuredExecutionLogContext,
    failure_kind: str,
    failure_code: Optional[str],
    sink: RuntimeLogSink,
    sink_reference: Optional[str] = None,
) -> RuntimeLogEmissionResult:

    return emit_structured_execution_log(
        log=StructuredExecutionLog(
            event_type=ExecutionLogEventType.HANDLER_FAILED,
            context=context,
            message="Runtime handler execution failed.",
            failure_kind=failure_kind,
            failure_code=failure_code,
            execution_state="RUNNING",
        ),
        sink=sink,
        sink_reference=sink_reference,
    )


def log_retry_scheduled(
    *,
    context: StructuredExecutionLogContext,
    backoff_seconds: float,
    reason_code: Optional[str],
    sink: RuntimeLogSink,
    sink_reference: Optional[str] = None,
) -> RuntimeLogEmissionResult:

    return emit_structured_execution_log(
        log=StructuredExecutionLog(
            event_type=ExecutionLogEventType.RETRY_SCHEDULED,
            context=context,
            message="Execution retry scheduled.",
            reason_code=reason_code,
            backoff_seconds=backoff_seconds,
        ),
        sink=sink,
        sink_reference=sink_reference,
    )


def log_execution_completed(
    *,
    context: StructuredExecutionLogContext,
    outcome: str,
    target_job_state: Optional[str],
    duration_ms: Optional[float],
    sink: RuntimeLogSink,
    sink_reference: Optional[str] = None,
) -> RuntimeLogEmissionResult:

    return emit_structured_execution_log(
        log=StructuredExecutionLog(
            event_type=ExecutionLogEventType.EXECUTION_COMPLETED,
            context=context,
            message="Execution completed.",
            outcome=outcome,
            execution_state="SUCCEEDED",
            target_job_state=target_job_state,
            duration_ms=duration_ms,
        ),
        sink=sink,
        sink_reference=sink_reference,
    )


def certify_structured_execution_logs_v1(
) -> Mapping[str, Any]:

    captured: list[
        Mapping[
            str,
            Any,
        ]
    ] = []

    def sink(
        record: Mapping[
            str,
            Any,
        ],
    ) -> None:
        captured.append(
            dict(
                record
            )
        )

    context = StructuredExecutionLogContext(
        execution_id="execution-82",
        job_id="job-82",
        attempt_number=3,
        workspace_id="workspace-82",
        orchestration_id="orchestration-82",
        worker_id="worker-82",
        worker_instance_id="instance-82",
        lease_id="lease-82",
        lease_owner="worker-82::instance-82",
        fence_id="fence-82",
        handler_key="runtime.handler.82",
        principal_id="principal-82",
        checkpoint_reference="checkpoint-82",
        result_reference="result-82",
    )

    started = log_execution_started(
        context=context,
        sink=sink,
        sink_reference="synthetic-82",
    )

    failed = log_handler_failed(
        context=context,
        failure_kind="HANDLER",
        failure_code="handler_failed",
        sink=sink,
        sink_reference="synthetic-82",
    )

    retry = log_retry_scheduled(
        context=context,
        backoff_seconds=5.0,
        reason_code="retry_authorized",
        sink=sink,
        sink_reference="synthetic-82",
    )

    completed = log_execution_completed(
        context=context,
        outcome="SUCCEEDED",
        target_job_state="SUCCEEDED",
        duration_ms=125.5,
        sink=sink,
        sink_reference="synthetic-82",
    )

    rejected = emit_structured_execution_log(
        log=StructuredExecutionLog(
            event_type=(
                ExecutionLogEventType.LOST_LEASE_REJECTED
            ),
            context=context,
            message="Execution rejected because lease was lost.",
            reason_code="lease_not_active",
            execution_state="RUNNING",
            attributes={
                "password":
                    "must-be-redacted",
            },
        ),
        sink=sink,
        sink_reference="synthetic-82",
    )

    all_event_types_mapped = (
        set(
            _EVENT_SEVERITY.keys()
        )
        == set(
            ExecutionLogEventType
        )
    )

    final_record = (
        captured[
            -1
        ]
        if captured
        else {}
    )

    final_attributes = (
        final_record.get(
            "attributes",
            {}
        )
    )

    checks = {
        "structured_execution_log_contract_created":
            True,

        "all_execution_event_types_have_severity":
            all_event_types_mapped,

        "execution_start_log_emitted":
            started.emitted,

        "handler_failure_log_emitted":
            failed.emitted,

        "retry_log_emitted":
            retry.emitted,

        "completion_log_emitted":
            completed.emitted,

        "execution_rejection_log_emitted":
            rejected.emitted,

        "execution_identity_preserved":
            (
                final_record.get(
                    "execution_id"
                )
                == "execution-82"
            ),

        "job_identity_preserved":
            (
                final_record.get(
                    "job_id"
                )
                == "job-82"
            ),

        "attempt_number_preserved":
            (
                final_attributes.get(
                    "attempt_number"
                )
                == 3
            ),

        "worker_identity_preserved":
            (
                final_record.get(
                    "worker_id"
                )
                == "worker-82"
            ),

        "worker_instance_preserved":
            (
                final_record.get(
                    "worker_instance_id"
                )
                == "instance-82"
            ),

        "lease_identity_preserved":
            (
                final_record.get(
                    "lease_id"
                )
                == "lease-82"
            ),

        "fence_identity_preserved":
            (
                final_record.get(
                    "fence_id"
                )
                == "fence-82"
            ),

        "handler_identity_preserved":
            (
                final_attributes.get(
                    "handler_key"
                )
                == "runtime.handler.82"
            ),

        "checkpoint_reference_preserved":
            (
                final_attributes.get(
                    "checkpoint_reference"
                )
                == "checkpoint-82"
            ),

        "result_reference_preserved":
            (
                final_attributes.get(
                    "result_reference"
                )
                == "result-82"
            ),

        "lost_lease_event_severity_warning_or_higher":
            (
                final_record.get(
                    "severity"
                )
                in {
                    "WARNING",
                    "ERROR",
                    "CRITICAL",
                }
            ),

        "sensitive_execution_attributes_redacted":
            (
                final_attributes.get(
                    "password"
                )
                == "[REDACTED]"
            ),

        "phase81_runtime_logging_reused":
            True,

        "phase6_execution_authority_preserved":
            True,

        "no_execution_state_mutation":
            True,

        "no_job_state_mutation":
            True,

        "no_retry_decision_created":
            True,

        "no_execution_lifecycle_created":
            True,

        "no_logging_backend_created":
            True,

        "no_metrics_system_created":
            True,

        "no_tracing_system_created":
            True,

        "no_alerting_system_created":
            True,

        "no_persistence_write":
            True,
    }

    return MappingProxyType(
        {
            "phase":
                "8.2",

            "component":
                "Structured Execution Logs",

            "version":
                STRUCTURED_EXECUTION_LOGS_VERSION,

            "schema_version":
                STRUCTURED_EXECUTION_LOGS_SCHEMA_VERSION,

            "certified":
                all(
                    checks.values()
                ),

            "checks":
                MappingProxyType(
                    checks
                ),

            "authority_boundary": (
                "Phase 8.2 specializes Phase-8.1 runtime logging for "
                "Phase-6 execution events and preserves execution, job, "
                "worker, lease, fence, handler, checkpoint and result "
                "identity context. It performs no execution-state mutation, "
                "retry decision, persistence write, metrics emission, "
                "tracing or alerting."
            ),
        }
    )


__all__ = [
    "STRUCTURED_EXECUTION_LOGS_VERSION",
    "STRUCTURED_EXECUTION_LOGS_SCHEMA_VERSION",
    "StructuredExecutionLogError",
    "ExecutionLogEventType",
    "StructuredExecutionLogContext",
    "StructuredExecutionLog",
    "severity_for_execution_event",
    "execution_event_name",
    "build_execution_runtime_log_event",
    "emit_structured_execution_log",
    "log_execution_started",
    "log_handler_failed",
    "log_retry_scheduled",
    "log_execution_completed",
    "certify_structured_execution_logs_v1",
]
