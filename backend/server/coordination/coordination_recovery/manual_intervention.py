"""
LinkCraftor — Universal Coordination Framework

Phase 9.5 — Manual Intervention.

Creates immutable operator-intervention evidence when Failure Policy
returns MANUAL_INTERVENTION.

This component does NOT send alerts, invoke staff tooling, mutate workflow
state or execute recovery.
"""

from __future__ import annotations

import hashlib

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Tuple

from backend.server.coordination.coordination_recovery.failure_policy import (
    WorkflowFailurePolicyOutcome,
)

from backend.server.coordination.coordination_recovery.terminal_failure_handling import (
    TerminalFailureHandlingResult,
)


MANUAL_INTERVENTION_VERSION = (
    "manual_intervention_v9.5.0"
)

MANUAL_INTERVENTION_SCHEMA_VERSION = (
    "manual_intervention_schema_v1"
)


class ManualInterventionError(
    ValueError
):
    pass


class ManualInterventionStatus(
    str,
    Enum,
):
    REQUIRED = "REQUIRED"


@dataclass(
    frozen=True,
    slots=True,
)
class ManualInterventionRequest:

    intervention_id: str

    workflow_id: str
    correlation_id: str
    workspace_id: str

    stage_id: str
    job_id: str

    failure_code: str
    failure_message: str

    reason_codes: Tuple[
        str,
        ...
    ]

    status: ManualInterventionStatus

    operator_action_executed: bool = False
    notification_emitted: bool = False

    intervention_version: str = (
        MANUAL_INTERVENTION_VERSION
    )

    schema_version: str = (
        MANUAL_INTERVENTION_SCHEMA_VERSION
    )

    def to_dict(
        self,
    ) -> Mapping[str, Any]:

        return MappingProxyType({
            "intervention_id":
                self.intervention_id,

            "workflow_id":
                self.workflow_id,

            "correlation_id":
                self.correlation_id,

            "workspace_id":
                self.workspace_id,

            "stage_id":
                self.stage_id,

            "job_id":
                self.job_id,

            "failure_code":
                self.failure_code,

            "failure_message":
                self.failure_message,

            "reason_codes":
                self.reason_codes,

            "status":
                self.status.value,

            "operator_action_executed":
                self.operator_action_executed,

            "notification_emitted":
                self.notification_emitted,

            "intervention_version":
                self.intervention_version,

            "schema_version":
                self.schema_version,
        })


def create_manual_intervention_request(
    terminal_failure: TerminalFailureHandlingResult,
) -> ManualInterventionRequest:

    if not isinstance(
        terminal_failure,
        TerminalFailureHandlingResult,
    ):
        raise ManualInterventionError(
            "terminal_failure must be TerminalFailureHandlingResult"
        )

    if (
        terminal_failure.policy_decision.outcome
        is not WorkflowFailurePolicyOutcome.MANUAL_INTERVENTION
    ):
        raise ManualInterventionError(
            "Failure Policy does not require MANUAL_INTERVENTION"
        )

    intervention_id = hashlib.sha256(
        (
            "ucf_manual_intervention_v1"
            + "\0"
            + terminal_failure.workflow_id
            + "\0"
            + terminal_failure.stage_id
            + "\0"
            + terminal_failure.job_id
            + "\0"
            + terminal_failure.failure_code
        ).encode(
            "utf-8"
        )
    ).hexdigest().upper()

    return ManualInterventionRequest(
        intervention_id=
            intervention_id,

        workflow_id=
            terminal_failure.workflow_id,

        correlation_id=
            terminal_failure.correlation_id,

        workspace_id=
            terminal_failure.workspace_id,

        stage_id=
            terminal_failure.stage_id,

        job_id=
            terminal_failure.job_id,

        failure_code=
            terminal_failure.failure_code,

        failure_message=
            terminal_failure.failure_message,

        reason_codes=
            terminal_failure.policy_decision.reason_codes,

        status=
            ManualInterventionStatus.REQUIRED,

        operator_action_executed=
            False,

        notification_emitted=
            False,
    )


__all__ = [
    "MANUAL_INTERVENTION_VERSION",
    "MANUAL_INTERVENTION_SCHEMA_VERSION",
    "ManualInterventionError",
    "ManualInterventionStatus",
    "ManualInterventionRequest",
    "create_manual_intervention_request",
]
