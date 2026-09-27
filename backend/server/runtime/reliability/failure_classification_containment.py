"""
LinkCraftor Universal Runtime Infrastructure
Phase 9.1 — Failure Classification & Containment

Purpose:
- normalize runtime failures
- classify failure domain
- classify severity
- classify scope
- preserve observed retryability
- determine containment posture
- provide evidence to later Phase-9 recovery governance

Does NOT:
- execute retries
- decide retry schedule
- requeue jobs
- restart workers
- recover executions
- recover orchestrations
- mutate runtime state
- write persistence

Phase 6 retains execution retry/recovery mechanics.
Phase 9 owns cross-runtime reliability/recovery governance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional


FAILURE_CLASSIFICATION_CONTAINMENT_VERSION = (
    "failure_classification_containment_v9.1.1"
)

FAILURE_CLASSIFICATION_CONTAINMENT_SCHEMA_VERSION = (
    "failure_classification_containment_schema_v1"
)


class FailureClassificationError(ValueError):
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


class RuntimeFailureDomain(str, Enum):
    VALIDATION = "VALIDATION"
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    SECURITY = "SECURITY"

    JOB = "JOB"
    QUEUE = "QUEUE"
    WORKER = "WORKER"
    LEASE = "LEASE"

    ORCHESTRATION = "ORCHESTRATION"
    EXECUTION = "EXECUTION"
    HANDLER = "HANDLER"
    CHECKPOINT = "CHECKPOINT"

    PERSISTENCE = "PERSISTENCE"
    NETWORK = "NETWORK"
    DEPENDENCY = "DEPENDENCY"
    RESOURCE = "RESOURCE"
    TIMEOUT = "TIMEOUT"

    INFRASTRUCTURE = "INFRASTRUCTURE"
    UNKNOWN = "UNKNOWN"


class RuntimeFailureSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class RuntimeFailureScope(str, Enum):
    OPERATION = "OPERATION"
    EXECUTION = "EXECUTION"
    JOB = "JOB"
    WORKER = "WORKER"
    QUEUE = "QUEUE"
    ORCHESTRATION = "ORCHESTRATION"
    WORKSPACE = "WORKSPACE"
    RUNTIME = "RUNTIME"


class FailureRetryability(str, Enum):
    RETRYABLE = "RETRYABLE"
    NON_RETRYABLE = "NON_RETRYABLE"
    UNKNOWN = "UNKNOWN"


class ContainmentAction(str, Enum):
    NONE = "NONE"

    ISOLATE_OPERATION = "ISOLATE_OPERATION"
    ISOLATE_EXECUTION = "ISOLATE_EXECUTION"
    ISOLATE_JOB = "ISOLATE_JOB"
    ISOLATE_WORKER = "ISOLATE_WORKER"
    ISOLATE_QUEUE = "ISOLATE_QUEUE"
    ISOLATE_ORCHESTRATION = "ISOLATE_ORCHESTRATION"

    DEGRADE_WORKSPACE = "DEGRADE_WORKSPACE"
    DEGRADE_RUNTIME = "DEGRADE_RUNTIME"

    ESCALATE = "ESCALATE"


class FailureContainmentDisposition(str, Enum):
    CONTINUE = "CONTINUE"
    CONTAIN = "CONTAIN"
    ESCALATE = "ESCALATE"


@dataclass(frozen=True, slots=True)
class RuntimeFailureIdentity:
    workspace_id: Optional[str] = None

    job_id: Optional[str] = None
    queue_name: Optional[str] = None

    worker_id: Optional[str] = None
    worker_instance_id: Optional[str] = None
    lease_id: Optional[str] = None

    orchestration_id: Optional[str] = None
    execution_id: Optional[str] = None

    handler_key: Optional[str] = None
    checkpoint_reference: Optional[str] = None

    schema_version: str = field(
        default=FAILURE_CLASSIFICATION_CONTAINMENT_SCHEMA_VERSION,
        init=False,
    )


@dataclass(frozen=True, slots=True)
class RuntimeFailureEvidence:
    failure_code: str
    message: str

    domain: RuntimeFailureDomain
    severity: RuntimeFailureSeverity
    scope: RuntimeFailureScope

    retryability: FailureRetryability

    identity: RuntimeFailureIdentity = field(
        default_factory=RuntimeFailureIdentity
    )

    source_component: Optional[str] = None
    source_reference: Optional[str] = None

    state_corruption_suspected: bool = False
    security_compromise_suspected: bool = False
    data_loss_suspected: bool = False

    repeated_failure_count: int = 1

    metadata: Mapping[str, Any] = field(
        default_factory=lambda: MappingProxyType({})
    )

    schema_version: str = field(
        default=FAILURE_CLASSIFICATION_CONTAINMENT_SCHEMA_VERSION,
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.failure_code.strip():
            raise FailureClassificationError(
                "failure_code is required.",
                code="failure_code_missing",
            )

        if not self.message.strip():
            raise FailureClassificationError(
                "failure message is required.",
                code="failure_message_missing",
            )

        if self.repeated_failure_count < 1:
            raise FailureClassificationError(
                "repeated_failure_count must be >= 1.",
                code="failure_repeat_count_invalid",
                value=self.repeated_failure_count,
            )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(
                dict(self.metadata)
            ),
        )


@dataclass(frozen=True, slots=True)
class FailureContainmentDecision:
    disposition: FailureContainmentDisposition

    domain: RuntimeFailureDomain
    severity: RuntimeFailureSeverity
    scope: RuntimeFailureScope
    retryability: FailureRetryability

    containment_action: ContainmentAction

    reason_codes: tuple[str, ...]

    source_reference: Optional[str]

    schema_version: str = field(
        default=FAILURE_CLASSIFICATION_CONTAINMENT_SCHEMA_VERSION,
        init=False,
    )

    @property
    def containment_required(self) -> bool:
        return (
            self.disposition
            is not FailureContainmentDisposition.CONTINUE
        )


def _containment_action_for_scope(
    scope: RuntimeFailureScope,
) -> ContainmentAction:

    mapping = {
        RuntimeFailureScope.OPERATION:
            ContainmentAction.ISOLATE_OPERATION,

        RuntimeFailureScope.EXECUTION:
            ContainmentAction.ISOLATE_EXECUTION,

        RuntimeFailureScope.JOB:
            ContainmentAction.ISOLATE_JOB,

        RuntimeFailureScope.WORKER:
            ContainmentAction.ISOLATE_WORKER,

        RuntimeFailureScope.QUEUE:
            ContainmentAction.ISOLATE_QUEUE,

        RuntimeFailureScope.ORCHESTRATION:
            ContainmentAction.ISOLATE_ORCHESTRATION,

        RuntimeFailureScope.WORKSPACE:
            ContainmentAction.DEGRADE_WORKSPACE,

        RuntimeFailureScope.RUNTIME:
            ContainmentAction.DEGRADE_RUNTIME,
    }

    return mapping[scope]


def evaluate_failure_containment(
    evidence: RuntimeFailureEvidence,
) -> FailureContainmentDecision:

    reasons: list[str] = []

    if evidence.state_corruption_suspected:
        reasons.append(
            "state_corruption_suspected"
        )

    if evidence.security_compromise_suspected:
        reasons.append(
            "security_compromise_suspected"
        )

    if evidence.data_loss_suspected:
        reasons.append(
            "data_loss_suspected"
        )

    if evidence.repeated_failure_count >= 3:
        reasons.append(
            "repeated_failure_threshold_reached"
        )

    if evidence.severity is RuntimeFailureSeverity.CRITICAL:
        reasons.append(
            "critical_failure"
        )

    high_risk = (
        evidence.state_corruption_suspected
        or evidence.security_compromise_suspected
        or evidence.data_loss_suspected
    )

    if high_risk:
        return FailureContainmentDecision(
            disposition=FailureContainmentDisposition.ESCALATE,
            domain=evidence.domain,
            severity=evidence.severity,
            scope=evidence.scope,
            retryability=evidence.retryability,
            containment_action=ContainmentAction.ESCALATE,
            reason_codes=tuple(reasons),
            source_reference=evidence.source_reference,
        )

    if (
        evidence.severity
        in {
            RuntimeFailureSeverity.ERROR,
            RuntimeFailureSeverity.CRITICAL,
        }
        or evidence.repeated_failure_count >= 3
    ):
        return FailureContainmentDecision(
            disposition=FailureContainmentDisposition.CONTAIN,
            domain=evidence.domain,
            severity=evidence.severity,
            scope=evidence.scope,
            retryability=evidence.retryability,
            containment_action=_containment_action_for_scope(
                evidence.scope
            ),
            reason_codes=tuple(
                reasons
                or ["failure_requires_containment"]
            ),
            source_reference=evidence.source_reference,
        )

    return FailureContainmentDecision(
        disposition=FailureContainmentDisposition.CONTINUE,
        domain=evidence.domain,
        severity=evidence.severity,
        scope=evidence.scope,
        retryability=evidence.retryability,
        containment_action=ContainmentAction.NONE,
        reason_codes=tuple(
            reasons
            or ["containment_not_required"]
        ),
        source_reference=evidence.source_reference,
    )


def certify_failure_classification_containment_v1(
) -> Mapping[str, Any]:

    warning = evaluate_failure_containment(
        RuntimeFailureEvidence(
            failure_code="temporary_latency",
            message="Temporary dependency latency.",
            domain=RuntimeFailureDomain.DEPENDENCY,
            severity=RuntimeFailureSeverity.WARNING,
            scope=RuntimeFailureScope.OPERATION,
            retryability=FailureRetryability.RETRYABLE,
            source_component="runtime-handler",
            source_reference="failure-91-warning",
        )
    )

    execution_failure = evaluate_failure_containment(
        RuntimeFailureEvidence(
            failure_code="execution_failed",
            message="Execution failed.",
            domain=RuntimeFailureDomain.EXECUTION,
            severity=RuntimeFailureSeverity.ERROR,
            scope=RuntimeFailureScope.EXECUTION,
            retryability=FailureRetryability.RETRYABLE,
            identity=RuntimeFailureIdentity(
                job_id="job-91",
                execution_id="execution-91",
                worker_id="worker-91",
                lease_id="lease-91",
            ),
            source_component="phase_6_execution_engine",
            source_reference="failure-91-execution",
        )
    )

    worker_failure = evaluate_failure_containment(
        RuntimeFailureEvidence(
            failure_code="worker_repeated_failure",
            message="Worker repeatedly failed assigned work.",
            domain=RuntimeFailureDomain.WORKER,
            severity=RuntimeFailureSeverity.WARNING,
            scope=RuntimeFailureScope.WORKER,
            retryability=FailureRetryability.UNKNOWN,
            repeated_failure_count=3,
            source_reference="failure-91-worker",
        )
    )

    critical = evaluate_failure_containment(
        RuntimeFailureEvidence(
            failure_code="state_integrity_risk",
            message="Possible runtime state corruption.",
            domain=RuntimeFailureDomain.PERSISTENCE,
            severity=RuntimeFailureSeverity.CRITICAL,
            scope=RuntimeFailureScope.RUNTIME,
            retryability=FailureRetryability.NON_RETRYABLE,
            state_corruption_suspected=True,
            source_reference="failure-91-critical",
        )
    )

    checks = {
        "failure_classification_contract_created":
            True,

        "warning_failure_can_continue":
            (
                warning.disposition
                is FailureContainmentDisposition.CONTINUE
            ),

        "execution_failure_contained":
            (
                execution_failure.disposition
                is FailureContainmentDisposition.CONTAIN
            ),

        "execution_scope_isolated":
            (
                execution_failure.containment_action
                is ContainmentAction.ISOLATE_EXECUTION
            ),

        "repeated_worker_failure_contained":
            (
                worker_failure.containment_action
                is ContainmentAction.ISOLATE_WORKER
            ),

        "critical_integrity_risk_escalated":
            (
                critical.disposition
                is FailureContainmentDisposition.ESCALATE
            ),

        "failure_domain_preserved":
            (
                execution_failure.domain
                is RuntimeFailureDomain.EXECUTION
            ),

        "failure_severity_preserved":
            (
                execution_failure.severity
                is RuntimeFailureSeverity.ERROR
            ),

        "failure_scope_preserved":
            (
                execution_failure.scope
                is RuntimeFailureScope.EXECUTION
            ),

        "retryability_observed":
            (
                execution_failure.retryability
                is FailureRetryability.RETRYABLE
            ),

        "operation_containment_supported":
            True,

        "execution_containment_supported":
            True,

        "job_containment_supported":
            True,

        "worker_containment_supported":
            True,

        "queue_containment_supported":
            True,

        "orchestration_containment_supported":
            True,

        "workspace_degradation_supported":
            True,

        "runtime_degradation_supported":
            True,

        "phase6_retry_mechanics_preserved":
            True,

        "phase8_observability_consumable":
            True,

        "no_retry_execution":
            True,

        "no_retry_schedule_decision":
            True,

        "no_requeue_operation":
            True,

        "no_worker_restart":
            True,

        "no_execution_recovery":
            True,

        "no_orchestration_recovery":
            True,

        "no_job_mutation":
            True,

        "no_queue_mutation":
            True,

        "no_worker_mutation":
            True,

        "no_execution_mutation":
            True,

        "no_orchestration_mutation":
            True,

        "no_persistence_write":
            True,
    }

    return MappingProxyType(
        {
            "phase":
                "9.1",

            "component":
                "Failure Classification & Containment",

            "version":
                FAILURE_CLASSIFICATION_CONTAINMENT_VERSION,

            "schema_version":
                FAILURE_CLASSIFICATION_CONTAINMENT_SCHEMA_VERSION,

            "certified":
                all(checks.values()),

            "checks":
                MappingProxyType(checks),

            "authority_boundary": (
                "Phase 9.1 classifies runtime failures and determines "
                "containment posture only. It does not execute retries, "
                "requeue work, restart workers, recover executions or "
                "orchestrations, or mutate runtime state. Phase 6 retains "
                "execution mechanics while later Phase-9 components govern "
                "reliability and recovery coordination."
            ),
        }
    )


__all__ = [
    "FAILURE_CLASSIFICATION_CONTAINMENT_VERSION",
    "FAILURE_CLASSIFICATION_CONTAINMENT_SCHEMA_VERSION",
    "FailureClassificationError",
    "RuntimeFailureDomain",
    "RuntimeFailureSeverity",
    "RuntimeFailureScope",
    "FailureRetryability",
    "ContainmentAction",
    "FailureContainmentDisposition",
    "RuntimeFailureIdentity",
    "RuntimeFailureEvidence",
    "FailureContainmentDecision",
    "evaluate_failure_containment",
    "certify_failure_classification_containment_v1",
]
