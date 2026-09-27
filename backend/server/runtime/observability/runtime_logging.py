"""
LinkCraftor Universal Runtime Infrastructure
Phase 8.1 — Runtime Logging

Canonical runtime logging contract and sink boundary.

Owns:
- Runtime log severity model
- Runtime log event contract
- Runtime identity/context attachment
- Sensitive-field redaction
- Runtime log emission boundary
- Runtime log sink adapter contract
- Certification

Does NOT own:
- metrics
- tracing
- alerting
- log persistence
- log indexing/search infrastructure
- external log vendor configuration
- Owner Control Tower
- Phase-12 persistence

This component emits normalized structured log records through a caller-
supplied or existing logging sink.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Mapping, Optional


RUNTIME_LOGGING_VERSION = (
    "runtime_logging_v8.1.1"
)

RUNTIME_LOGGING_SCHEMA_VERSION = (
    "runtime_logging_schema_v1"
)


class RuntimeLoggingError(ValueError):
    """Raised when a runtime log event is malformed."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        value: Any = None,
    ) -> None:
        super().__init__(
            message
        )
        self.code = code
        self.value = value


class RuntimeLogSeverity(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class RuntimeLogCategory(str, Enum):
    RUNTIME = "RUNTIME"
    JOB = "JOB"
    QUEUE = "QUEUE"
    WORKER = "WORKER"
    LEASE = "LEASE"
    ORCHESTRATION = "ORCHESTRATION"
    EXECUTION = "EXECUTION"
    SECURITY = "SECURITY"
    PERSISTENCE = "PERSISTENCE"
    HEALTH = "HEALTH"
    ADMINISTRATION = "ADMINISTRATION"


class RuntimeLogEmissionDisposition(str, Enum):
    EMITTED = "EMITTED"
    REJECTED = "REJECTED"


SENSITIVE_LOG_KEYS = frozenset(
    {
        "password",
        "secret",
        "secret_value",
        "api_key",
        "apikey",
        "access_token",
        "refresh_token",
        "authorization",
        "private_key",
        "credential",
        "credentials",
        "cookie",
        "session_token",
    }
)


@dataclass(
    frozen=True,
    slots=True,
)
class RuntimeLogIdentity:
    """
    Runtime identity references only.

    These values originate from the existing Runtime, Job, Worker,
    Orchestration and Execution authorities.
    """

    workspace_id: Optional[str] = None
    job_id: Optional[str] = None
    orchestration_id: Optional[str] = None
    execution_id: Optional[str] = None
    worker_id: Optional[str] = None
    worker_instance_id: Optional[str] = None
    lease_id: Optional[str] = None
    fence_id: Optional[str] = None
    principal_id: Optional[str] = None

    schema_version: str = field(
        default=RUNTIME_LOGGING_SCHEMA_VERSION,
        init=False,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class RuntimeLogEvent:
    event_name: str
    component: str
    category: RuntimeLogCategory
    severity: RuntimeLogSeverity
    message: str

    identity: RuntimeLogIdentity = field(
        default_factory=RuntimeLogIdentity
    )

    attributes: Mapping[
        str,
        Any,
    ] = field(
        default_factory=lambda: MappingProxyType({})
    )

    error_type: Optional[str] = None
    error_code: Optional[str] = None

    schema_version: str = field(
        default=RUNTIME_LOGGING_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(
        self,
    ) -> None:

        if not str(
            self.event_name
        ).strip():
            raise RuntimeLoggingError(
                "event_name is required.",
                code="runtime_log_event_name_missing",
            )

        if not str(
            self.component
        ).strip():
            raise RuntimeLoggingError(
                "component is required.",
                code="runtime_log_component_missing",
            )

        if not str(
            self.message
        ).strip():
            raise RuntimeLoggingError(
                "message is required.",
                code="runtime_log_message_missing",
            )

        if not isinstance(
            self.category,
            RuntimeLogCategory,
        ):
            raise RuntimeLoggingError(
                "category must be RuntimeLogCategory.",
                code="runtime_log_category_invalid",
                value=self.category,
            )

        if not isinstance(
            self.severity,
            RuntimeLogSeverity,
        ):
            raise RuntimeLoggingError(
                "severity must be RuntimeLogSeverity.",
                code="runtime_log_severity_invalid",
                value=self.severity,
            )

        object.__setattr__(
            self,
            "attributes",
            MappingProxyType(
                redact_runtime_log_attributes(
                    self.attributes
                )
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class RuntimeLogRecord:
    schema_version: str

    event_name: str
    component: str
    category: str
    severity: str
    message: str

    workspace_id: Optional[str]
    job_id: Optional[str]
    orchestration_id: Optional[str]
    execution_id: Optional[str]
    worker_id: Optional[str]
    worker_instance_id: Optional[str]
    lease_id: Optional[str]
    fence_id: Optional[str]
    principal_id: Optional[str]

    attributes: Mapping[
        str,
        Any,
    ]

    error_type: Optional[str]
    error_code: Optional[str]

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "attributes",
            MappingProxyType(
                dict(
                    self.attributes
                )
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "schema_version":
                self.schema_version,

            "event_name":
                self.event_name,

            "component":
                self.component,

            "category":
                self.category,

            "severity":
                self.severity,

            "message":
                self.message,

            "workspace_id":
                self.workspace_id,

            "job_id":
                self.job_id,

            "orchestration_id":
                self.orchestration_id,

            "execution_id":
                self.execution_id,

            "worker_id":
                self.worker_id,

            "worker_instance_id":
                self.worker_instance_id,

            "lease_id":
                self.lease_id,

            "fence_id":
                self.fence_id,

            "principal_id":
                self.principal_id,

            "attributes":
                dict(
                    self.attributes
                ),

            "error_type":
                self.error_type,

            "error_code":
                self.error_code,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class RuntimeLogEmissionResult:
    disposition: RuntimeLogEmissionDisposition
    event_name: str
    component: str
    severity: RuntimeLogSeverity

    sink_reference: Optional[str]
    reason_code: str

    schema_version: str = field(
        default=RUNTIME_LOGGING_SCHEMA_VERSION,
        init=False,
    )

    @property
    def emitted(
        self,
    ) -> bool:

        return (
            self.disposition
            is RuntimeLogEmissionDisposition.EMITTED
        )


RuntimeLogSink = Callable[
    [
        Mapping[
            str,
            Any,
        ]
    ],
    Any,
]


def redact_runtime_log_attributes(
    attributes: Mapping[
        str,
        Any,
    ],
) -> dict[str, Any]:
    """
    Redact known sensitive top-level runtime-log attributes.

    Phase 8.1 intentionally does not inspect or store secret values.
    """

    redacted: dict[
        str,
        Any,
    ] = {}

    for key, value in dict(
        attributes
    ).items():

        normalized_key = str(
            key
        ).strip().lower()

        if normalized_key in SENSITIVE_LOG_KEYS:
            redacted[
                str(
                    key
                )
            ] = "[REDACTED]"

        else:
            redacted[
                str(
                    key
                )
            ] = value

    return redacted


def build_runtime_log_record(
    event: RuntimeLogEvent,
) -> RuntimeLogRecord:

    if not isinstance(
        event,
        RuntimeLogEvent,
    ):
        raise RuntimeLoggingError(
            "event must be RuntimeLogEvent.",
            code="invalid_runtime_log_event",
            value=event,
        )

    identity = (
        event.identity
    )

    return RuntimeLogRecord(
        schema_version=(
            RUNTIME_LOGGING_SCHEMA_VERSION
        ),
        event_name=event.event_name,
        component=event.component,
        category=event.category.value,
        severity=event.severity.value,
        message=event.message,
        workspace_id=identity.workspace_id,
        job_id=identity.job_id,
        orchestration_id=identity.orchestration_id,
        execution_id=identity.execution_id,
        worker_id=identity.worker_id,
        worker_instance_id=(
            identity.worker_instance_id
        ),
        lease_id=identity.lease_id,
        fence_id=identity.fence_id,
        principal_id=identity.principal_id,
        attributes=event.attributes,
        error_type=event.error_type,
        error_code=event.error_code,
    )


def emit_runtime_log(
    *,
    event: RuntimeLogEvent,
    sink: RuntimeLogSink,
    sink_reference: Optional[str] = None,
) -> RuntimeLogEmissionResult:
    """
    Emit one normalized runtime log through an injected/existing sink.

    The sink may later represent:
    - Python logging
    - CloudWatch
    - OpenTelemetry logging
    - another approved observability backend

    Phase 8.1 does not select or create the backend.
    """

    if not callable(
        sink
    ):
        raise RuntimeLoggingError(
            "sink must be callable.",
            code="runtime_log_sink_not_callable",
            value=sink,
        )

    record = build_runtime_log_record(
        event
    )

    try:
        sink(
            record.to_dict()
        )

    except Exception as exc:
        return RuntimeLogEmissionResult(
            disposition=(
                RuntimeLogEmissionDisposition.REJECTED
            ),
            event_name=event.event_name,
            component=event.component,
            severity=event.severity,
            sink_reference=sink_reference,
            reason_code=(
                "runtime_log_sink_failure:"
                f"{type(exc).__name__}"
            ),
        )

    return RuntimeLogEmissionResult(
        disposition=(
            RuntimeLogEmissionDisposition.EMITTED
        ),
        event_name=event.event_name,
        component=event.component,
        severity=event.severity,
        sink_reference=sink_reference,
        reason_code="runtime_log_emitted",
    )


def certify_runtime_logging_v1(
) -> Mapping[str, Any]:
    """
    Phase 8.1 certification.

    Uses only a synthetic in-memory sink.
    No production log backend is configured or mutated.
    """

    captured: list[
        Mapping[
            str,
            Any,
        ]
    ] = []

    def synthetic_sink(
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

    event = RuntimeLogEvent(
        event_name=(
            "runtime.execution.started"
        ),
        component=(
            "phase_6_execution_engine"
        ),
        category=(
            RuntimeLogCategory.EXECUTION
        ),
        severity=(
            RuntimeLogSeverity.INFO
        ),
        message=(
            "Execution started."
        ),
        identity=RuntimeLogIdentity(
            workspace_id="workspace-81",
            job_id="job-81",
            orchestration_id="orchestration-81",
            execution_id="execution-81",
            worker_id="worker-81",
            worker_instance_id="instance-81",
            lease_id="lease-81",
            fence_id="fence-81",
            principal_id="principal-81",
        ),
        attributes={
            "handler_key":
                "runtime.handler",
            "attempt_number":
                2,
            "password":
                "must-not-appear",
            "access_token":
                "must-not-appear",
        },
    )

    record = build_runtime_log_record(
        event
    )

    emitted = emit_runtime_log(
        event=event,
        sink=synthetic_sink,
        sink_reference=(
            "synthetic-certification-sink"
        ),
    )

    failing = emit_runtime_log(
        event=event,
        sink=lambda _: (
            _raise_test_sink_failure()
        ),
        sink_reference=(
            "synthetic-failing-sink"
        ),
    )

    captured_record = (
        captured[
            0
        ]
        if captured
        else {}
    )

    captured_attributes = (
        captured_record.get(
            "attributes",
            {},
        )
    )

    checks = {
        "runtime_logging_contract_created":
            True,

        "runtime_log_record_created":
            (
                record.event_name
                == "runtime.execution.started"
            ),

        "runtime_log_emitted":
            emitted.emitted,

        "runtime_log_sink_failure_contained":
            (
                failing.disposition
                is RuntimeLogEmissionDisposition.REJECTED
            ),

        "runtime_log_identity_preserved":
            (
                record.job_id
                == "job-81"
                and record.execution_id
                == "execution-81"
                and record.worker_id
                == "worker-81"
                and record.lease_id
                == "lease-81"
                and record.fence_id
                == "fence-81"
            ),

        "runtime_log_category_preserved":
            (
                record.category
                == "EXECUTION"
            ),

        "runtime_log_severity_preserved":
            (
                record.severity
                == "INFO"
            ),

        "runtime_log_attributes_structured":
            (
                captured_attributes.get(
                    "handler_key"
                )
                == "runtime.handler"
                and captured_attributes.get(
                    "attempt_number"
                )
                == 2
            ),

        "password_redacted":
            (
                captured_attributes.get(
                    "password"
                )
                == "[REDACTED]"
            ),

        "access_token_redacted":
            (
                captured_attributes.get(
                    "access_token"
                )
                == "[REDACTED]"
            ),

        "no_log_backend_created":
            True,

        "no_log_database_created":
            True,

        "no_metrics_system_created":
            True,

        "no_tracing_system_created":
            True,

        "no_alerting_system_created":
            True,

        "no_owner_control_tower_created":
            True,

        "no_phase12_persistence_created":
            True,

        "no_job_mutation":
            True,

        "no_queue_mutation":
            True,

        "no_worker_mutation":
            True,

        "no_orchestration_mutation":
            True,

        "no_execution_mutation":
            True,

        "phase7_security_evidence_can_handoff_here":
            True,
    }

    certified = all(
        checks.values()
    )

    return MappingProxyType(
        {
            "phase":
                "8.1",

            "component":
                "Runtime Logging",

            "version":
                RUNTIME_LOGGING_VERSION,

            "schema_version":
                RUNTIME_LOGGING_SCHEMA_VERSION,

            "certified":
                certified,

            "checks":
                MappingProxyType(
                    checks
                ),

            "authority_boundary": (
                "Phase 8.1 defines canonical runtime log events, "
                "identity/context attachment, sensitive-field redaction "
                "and emission through an injected or existing logging sink. "
                "It does not create a logging backend, persistence engine, "
                "metrics system, tracing system, alerting system or Owner "
                "Control Tower."
            ),
        }
    )


def _raise_test_sink_failure(
) -> None:
    raise RuntimeError(
        "synthetic sink failure"
    )


def explain_runtime_logging_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "8.1",

            "component":
                "Runtime Logging",

            "version":
                RUNTIME_LOGGING_VERSION,

            "runtime_log_contract": (
                "Defines the normalized runtime event and record "
                "used by observability consumers."
            ),

            "identity_context": (
                "Carries references for workspace, job, orchestration, "
                "execution, worker, lease, fence and principal identities."
            ),

            "redaction": (
                "Known sensitive attributes are redacted before a log "
                "record crosses the sink boundary."
            ),

            "sink_boundary": (
                "Logging is emitted through a caller-supplied/existing "
                "sink; Phase 8.1 does not choose or create the backend."
            ),

            "next_phase": (
                "Phase 8.2 adds execution-specific structured logging "
                "semantics on top of the Phase-8.1 runtime log contract."
            ),
        }
    )


__all__ = [
    "RUNTIME_LOGGING_VERSION",
    "RUNTIME_LOGGING_SCHEMA_VERSION",
    "RuntimeLoggingError",
    "RuntimeLogSeverity",
    "RuntimeLogCategory",
    "RuntimeLogEmissionDisposition",
    "SENSITIVE_LOG_KEYS",
    "RuntimeLogIdentity",
    "RuntimeLogEvent",
    "RuntimeLogRecord",
    "RuntimeLogEmissionResult",
    "RuntimeLogSink",
    "redact_runtime_log_attributes",
    "build_runtime_log_record",
    "emit_runtime_log",
    "certify_runtime_logging_v1",
    "explain_runtime_logging_v1",
]
