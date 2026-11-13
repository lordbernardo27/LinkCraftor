"""
LinkCraftor — Universal Coordination Framework

Phase 9.1 — Failure Policy

Deterministic workflow-level policy classification for one terminal
failed ProcessedStageResult.

Canonical input authority:
- Phase 6.1 ProcessedStageResult.

Optional supporting Runtime reliability authorities:
- Runtime Failure Classification & Containment,
- Runtime Retry Governance,
- Runtime Recovery Coordination.

This component decides only the workflow-level policy posture:

- RECOVER
- COMPENSATE
- MANUAL_INTERVENTION
- FAIL_WORKFLOW

This component does NOT:
- retry or requeue Runtime jobs,
- execute Runtime recovery,
- mutate Runtime jobs, queues, workers or executions,
- mutate workflow lifecycle state,
- persist workflow recovery state,
- perform compensation,
- perform manual intervention,
- enforce recovery-attempt ceilings.

Those mechanics belong to their owning later phases/components.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional, Tuple

from backend.server.coordination.stage_handoff.stage_result_processor import (
    ProcessedStageResult,
    StageResultDisposition,
)

from backend.server.runtime.reliability.failure_classification_containment import (
    ContainmentAction,
    FailureContainmentDecision,
    FailureContainmentDisposition,
    FailureRetryability,
    RuntimeFailureDomain,
    RuntimeFailureSeverity,
)

from backend.server.runtime.reliability.retry_governance import (
    RetryGovernanceDecision,
    RetryGovernanceDisposition,
)

from backend.server.runtime.reliability.recovery_coordination import (
    RecoveryCoordinationDecision,
    RecoveryRoute,
)


FAILURE_POLICY_VERSION = "failure_policy_v9.1.0"
FAILURE_POLICY_SCHEMA_VERSION = "failure_policy_schema_v1"


class FailurePolicyError(ValueError):
    pass


class WorkflowFailurePolicyOutcome(
    str,
    Enum,
):
    RECOVER = "RECOVER"
    COMPENSATE = "COMPENSATE"
    MANUAL_INTERVENTION = "MANUAL_INTERVENTION"
    FAIL_WORKFLOW = "FAIL_WORKFLOW"


@dataclass(
    frozen=True,
    slots=True,
)
class WorkflowFailurePolicyDecision:

    outcome: WorkflowFailurePolicyOutcome

    reason_codes: Tuple[
        str,
        ...
    ]

    source_result_id: str
    workflow_id: str
    correlation_id: str
    stage_id: str
    job_id: str

    failure_code: str

    runtime_failure_domain: Optional[str]
    runtime_failure_severity: Optional[str]
    runtime_retry_disposition: Optional[str]
    runtime_recovery_primary_route: Optional[str]

    compensation_required: bool
    manual_intervention_required: bool

    source_processor_version: str

    policy_version: str = FAILURE_POLICY_VERSION
    schema_version: str = FAILURE_POLICY_SCHEMA_VERSION

    def to_dict(
        self,
    ) -> Mapping[
        str,
        Any,
    ]:

        return MappingProxyType({
            "outcome":
                self.outcome.value,

            "reason_codes":
                self.reason_codes,

            "source_result_id":
                self.source_result_id,

            "workflow_id":
                self.workflow_id,

            "correlation_id":
                self.correlation_id,

            "stage_id":
                self.stage_id,

            "job_id":
                self.job_id,

            "failure_code":
                self.failure_code,

            "runtime_failure_domain":
                self.runtime_failure_domain,

            "runtime_failure_severity":
                self.runtime_failure_severity,

            "runtime_retry_disposition":
                self.runtime_retry_disposition,

            "runtime_recovery_primary_route":
                self.runtime_recovery_primary_route,

            "compensation_required":
                self.compensation_required,

            "manual_intervention_required":
                self.manual_intervention_required,

            "source_processor_version":
                self.source_processor_version,

            "policy_version":
                self.policy_version,

            "schema_version":
                self.schema_version,
        })


def _flag(
    source: ProcessedStageResult,
    name: str,
) -> bool:

    values = (
        source.failure_details,
        source.metadata,
    )

    for mapping in values:

        value = mapping.get(
            name
        )

        if value is True:
            return True

    return False


def _validate_source(
    source: ProcessedStageResult,
) -> None:

    if not isinstance(
        source,
        ProcessedStageResult,
    ):
        raise FailurePolicyError(
            "source must be ProcessedStageResult"
        )

    if not source.terminal:
        raise FailurePolicyError(
            "source must be terminal"
        )

    if (
        source.disposition
        is not StageResultDisposition.FAILED
    ):
        raise FailurePolicyError(
            "Phase 9.1 requires FAILED ProcessedStageResult"
        )

    if source.normal_handoff_allowed:
        raise FailurePolicyError(
            "FAILED source cannot allow normal handoff"
        )

    if source.prerequisite_satisfied:
        raise FailurePolicyError(
            "FAILED source cannot satisfy prerequisite"
        )


def evaluate_failure_policy(
    source: ProcessedStageResult,
    *,
    containment_decision: Optional[
        FailureContainmentDecision
    ] = None,
    retry_decision: Optional[
        RetryGovernanceDecision
    ] = None,
    recovery_decision: Optional[
        RecoveryCoordinationDecision
    ] = None,
) -> WorkflowFailurePolicyDecision:

    _validate_source(
        source
    )

    if (
        containment_decision is not None
        and not isinstance(
            containment_decision,
            FailureContainmentDecision,
        )
    ):
        raise FailurePolicyError(
            "containment_decision must be FailureContainmentDecision or None"
        )

    if (
        retry_decision is not None
        and not isinstance(
            retry_decision,
            RetryGovernanceDecision,
        )
    ):
        raise FailurePolicyError(
            "retry_decision must be RetryGovernanceDecision or None"
        )

    if (
        recovery_decision is not None
        and not isinstance(
            recovery_decision,
            RecoveryCoordinationDecision,
        )
    ):
        raise FailurePolicyError(
            "recovery_decision must be RecoveryCoordinationDecision or None"
        )

    reasons = []

    compensation_required = (
        _flag(
            source,
            "compensation_required",
        )
    )

    manual_intervention_required = (
        _flag(
            source,
            "manual_intervention_required",
        )
    )

    # --------------------------------------------------------------
    # Highest priority: explicit Coordination safety requirements.
    # --------------------------------------------------------------

    if compensation_required:
        reasons.append(
            "explicit_compensation_required"
        )

        outcome = (
            WorkflowFailurePolicyOutcome.COMPENSATE
        )

    elif manual_intervention_required:
        reasons.append(
            "explicit_manual_intervention_required"
        )

        outcome = (
            WorkflowFailurePolicyOutcome.MANUAL_INTERVENTION
        )

    # --------------------------------------------------------------
    # Runtime containment evidence can force human intervention.
    # --------------------------------------------------------------

    elif (
        containment_decision is not None
        and (
            containment_decision.severity
            is RuntimeFailureSeverity.CRITICAL

            or containment_decision.domain
            in (
                RuntimeFailureDomain.SECURITY,
                RuntimeFailureDomain.AUTHENTICATION,
                RuntimeFailureDomain.AUTHORIZATION,
                RuntimeFailureDomain.PERSISTENCE,
            )

            or containment_decision.disposition
            is FailureContainmentDisposition.ESCALATE

            or containment_decision.containment_action
            is ContainmentAction.ESCALATE
        )
    ):
        reasons.append(
            "runtime_failure_requires_escalation"
        )

        outcome = (
            WorkflowFailurePolicyOutcome.MANUAL_INTERVENTION
        )

    # --------------------------------------------------------------
    # Runtime recovery route can support UCF workflow recovery.
    # UCF does not execute the route.
    # --------------------------------------------------------------

    elif (
        recovery_decision is not None
        and recovery_decision.primary_route
        in (
            RecoveryRoute.WORKER_RECOVERY,
            RecoveryRoute.QUEUE_RECOVERY,
            RecoveryRoute.EXECUTION_RECOVERY,
            RecoveryRoute.ORCHESTRATION_RECOVERY,
            RecoveryRoute.CRASH_RESTART_RECOVERY,
        )
    ):
        reasons.append(
            "runtime_recovery_route_available"
        )

        outcome = (
            WorkflowFailurePolicyOutcome.RECOVER
        )

    elif (
        recovery_decision is not None
        and recovery_decision.primary_route
        in (
            RecoveryRoute.DEGRADED_MODE,
            RecoveryRoute.ESCALATION,
        )
    ):
        reasons.append(
            "runtime_recovery_requires_escalation"
        )

        outcome = (
            WorkflowFailurePolicyOutcome.MANUAL_INTERVENTION
        )

    # --------------------------------------------------------------
    # Runtime retry governance is authoritative for Runtime retries.
    # RETRY_ALLOWED supports recovery posture but does not execute it.
    # --------------------------------------------------------------

    elif (
        retry_decision is not None
        and retry_decision.disposition
        is RetryGovernanceDisposition.RETRY_ALLOWED
    ):
        reasons.append(
            "runtime_retry_allowed"
        )

        outcome = (
            WorkflowFailurePolicyOutcome.RECOVER
        )

    elif (
        retry_decision is not None
        and retry_decision.disposition
        in (
            RetryGovernanceDisposition.RETRY_DENIED,
            RetryGovernanceDisposition.RETRY_EXHAUSTED,
        )
    ):
        reasons.append(
            (
                "runtime_retry_denied"
                if retry_decision.disposition
                is RetryGovernanceDisposition.RETRY_DENIED
                else "runtime_retry_exhausted"
            )
        )

        outcome = (
            WorkflowFailurePolicyOutcome.FAIL_WORKFLOW
        )

    # --------------------------------------------------------------
    # Terminal Phase-5.5 failure evidence may directly prove retry
    # exhaustion even when no Runtime RetryGovernanceDecision object
    # is supplied to UCF.
    # --------------------------------------------------------------

    elif (
        source.failure_details.get(
            "runtime_retry_exhausted"
        )
        is True
    ):
        reasons.append(
            "terminal_runtime_retry_exhausted"
        )

        outcome = (
            WorkflowFailurePolicyOutcome.FAIL_WORKFLOW
        )

    # --------------------------------------------------------------
    # Non-retryable Runtime classification also closes automatic
    # recovery unless stronger explicit evidence above supersedes it.
    # --------------------------------------------------------------

    elif (
        containment_decision is not None
        and containment_decision.retryability
        is FailureRetryability.NON_RETRYABLE
    ):
        reasons.append(
            "runtime_failure_non_retryable"
        )

        outcome = (
            WorkflowFailurePolicyOutcome.FAIL_WORKFLOW
        )

    # --------------------------------------------------------------
    # Unknown or absent policy evidence fails closed to workflow
    # failure rather than inventing automatic recovery.
    # --------------------------------------------------------------

    else:
        reasons.append(
            "no_authorized_recovery_evidence"
        )

        outcome = (
            WorkflowFailurePolicyOutcome.FAIL_WORKFLOW
        )

    return WorkflowFailurePolicyDecision(
        outcome=
            outcome,

        reason_codes=
            tuple(
                reasons
            ),

        source_result_id=
            source.result_id,

        workflow_id=
            source.workflow_id,

        correlation_id=
            source.correlation_id,

        stage_id=
            source.stage_id,

        job_id=
            source.job_id,

        failure_code=
            source.failure_code,

        runtime_failure_domain=
            (
                containment_decision.domain.value
                if containment_decision
                is not None
                else None
            ),

        runtime_failure_severity=
            (
                containment_decision.severity.value
                if containment_decision
                is not None
                else None
            ),

        runtime_retry_disposition=
            (
                retry_decision.disposition.value
                if retry_decision
                is not None
                else None
            ),

        runtime_recovery_primary_route=
            (
                recovery_decision.primary_route.value
                if recovery_decision
                is not None
                else None
            ),

        compensation_required=
            compensation_required,

        manual_intervention_required=
            manual_intervention_required,

        source_processor_version=
            source.processor_version,
    )


__all__ = [
    "FAILURE_POLICY_VERSION",
    "FAILURE_POLICY_SCHEMA_VERSION",
    "FailurePolicyError",
    "WorkflowFailurePolicyOutcome",
    "WorkflowFailurePolicyDecision",
    "evaluate_failure_policy",
]
