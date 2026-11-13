"""
LinkCraftor — Universal Coordination Framework

Phase 9.2 — Terminal Runtime Failure Handling.

Consumes one terminal FAILED ProcessedStageResult and frozen Phase 9.1
Failure Policy.

This component:
- validates terminal failure evidence,
- invokes Phase 9.1 policy classification,
- preserves workflow/stage/job identity,
- returns immutable coordination recovery evidence.

It does NOT:
- re-read Runtime jobs,
- create a second Runtime failure intake path,
- retry/requeue Runtime work,
- mutate workflow lifecycle,
- persist workflow state,
- perform compensation,
- perform manual intervention.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Optional, Tuple

from backend.server.coordination.stage_handoff.stage_result_processor import (
    ProcessedStageResult,
    StageResultDisposition,
)

from backend.server.coordination.coordination_recovery.failure_policy import (
    WorkflowFailurePolicyDecision,
    evaluate_failure_policy,
)

from backend.server.runtime.reliability.failure_classification_containment import (
    FailureContainmentDecision,
)

from backend.server.runtime.reliability.retry_governance import (
    RetryGovernanceDecision,
)

from backend.server.runtime.reliability.recovery_coordination import (
    RecoveryCoordinationDecision,
)


TERMINAL_FAILURE_HANDLING_VERSION = (
    "terminal_failure_handling_v9.2.0"
)

TERMINAL_FAILURE_HANDLING_SCHEMA_VERSION = (
    "terminal_failure_handling_schema_v1"
)


class TerminalFailureHandlingError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class TerminalFailureHandlingResult:

    result_id: str
    workflow_id: str
    correlation_id: str
    workspace_id: str

    stage_id: str
    stage_version: str

    job_id: str
    job_type: str

    failure_code: str
    failure_message: str

    failure_details: Mapping[
        str,
        Any,
    ]

    policy_decision: WorkflowFailurePolicyDecision

    source_processor_version: str

    handling_version: str = (
        TERMINAL_FAILURE_HANDLING_VERSION
    )

    schema_version: str = (
        TERMINAL_FAILURE_HANDLING_SCHEMA_VERSION
    )

    def to_dict(
        self,
    ) -> Mapping[str, Any]:

        return MappingProxyType({
            "result_id":
                self.result_id,

            "workflow_id":
                self.workflow_id,

            "correlation_id":
                self.correlation_id,

            "workspace_id":
                self.workspace_id,

            "stage_id":
                self.stage_id,

            "stage_version":
                self.stage_version,

            "job_id":
                self.job_id,

            "job_type":
                self.job_type,

            "failure_code":
                self.failure_code,

            "failure_message":
                self.failure_message,

            "failure_details":
                dict(
                    self.failure_details
                ),

            "policy_decision":
                dict(
                    self.policy_decision.to_dict()
                ),

            "source_processor_version":
                self.source_processor_version,

            "handling_version":
                self.handling_version,

            "schema_version":
                self.schema_version,
        })


def handle_terminal_failure(
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
) -> TerminalFailureHandlingResult:

    if not isinstance(
        source,
        ProcessedStageResult,
    ):
        raise TerminalFailureHandlingError(
            "source must be ProcessedStageResult"
        )

    if not source.terminal:
        raise TerminalFailureHandlingError(
            "source must be terminal"
        )

    if (
        source.disposition
        is not StageResultDisposition.FAILED
    ):
        raise TerminalFailureHandlingError(
            "source must have FAILED disposition"
        )

    decision = evaluate_failure_policy(
        source,
        containment_decision=
            containment_decision,

        retry_decision=
            retry_decision,

        recovery_decision=
            recovery_decision,
    )

    if (
        decision.workflow_id
        != source.workflow_id
        or decision.correlation_id
        != source.correlation_id
        or decision.stage_id
        != source.stage_id
        or decision.job_id
        != source.job_id
    ):
        raise TerminalFailureHandlingError(
            "Phase 9.1 decision identity mismatch"
        )

    return TerminalFailureHandlingResult(
        result_id=
            source.result_id,

        workflow_id=
            source.workflow_id,

        correlation_id=
            source.correlation_id,

        workspace_id=
            source.workspace_id,

        stage_id=
            source.stage_id,

        stage_version=
            source.stage_version,

        job_id=
            source.job_id,

        job_type=
            source.job_type,

        failure_code=
            source.failure_code,

        failure_message=
            source.failure_message,

        failure_details=
            source.failure_details,

        policy_decision=
            decision,

        source_processor_version=
            source.processor_version,
    )


__all__ = [
    "TERMINAL_FAILURE_HANDLING_VERSION",
    "TERMINAL_FAILURE_HANDLING_SCHEMA_VERSION",
    "TerminalFailureHandlingError",
    "TerminalFailureHandlingResult",
    "handle_terminal_failure",
]
