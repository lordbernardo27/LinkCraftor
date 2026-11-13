"""
LinkCraftor — Universal Coordination Framework

Phase 9.4 — Compensation.

Creates immutable compensation instructions when frozen Failure Policy
returns COMPENSATE.

This component does NOT execute compensating business logic.
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


COMPENSATION_VERSION = (
    "compensation_v9.4.0"
)

COMPENSATION_SCHEMA_VERSION = (
    "compensation_schema_v1"
)


class CompensationError(
    ValueError
):
    pass


class CompensationDisposition(
    str,
    Enum,
):
    REQUIRED = "REQUIRED"


@dataclass(
    frozen=True,
    slots=True,
)
class CompensationInstruction:

    compensation_id: str

    workflow_id: str
    correlation_id: str
    workspace_id: str

    stage_id: str
    job_id: str

    failure_code: str

    disposition: CompensationDisposition

    reason_codes: Tuple[
        str,
        ...
    ]

    business_compensation_executed: bool = False

    compensation_version: str = (
        COMPENSATION_VERSION
    )

    schema_version: str = (
        COMPENSATION_SCHEMA_VERSION
    )

    def to_dict(
        self,
    ) -> Mapping[str, Any]:

        return MappingProxyType({
            "compensation_id":
                self.compensation_id,

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

            "disposition":
                self.disposition.value,

            "reason_codes":
                self.reason_codes,

            "business_compensation_executed":
                self.business_compensation_executed,

            "compensation_version":
                self.compensation_version,

            "schema_version":
                self.schema_version,
        })


def create_compensation_instruction(
    terminal_failure: TerminalFailureHandlingResult,
) -> CompensationInstruction:

    if not isinstance(
        terminal_failure,
        TerminalFailureHandlingResult,
    ):
        raise CompensationError(
            "terminal_failure must be TerminalFailureHandlingResult"
        )

    if (
        terminal_failure.policy_decision.outcome
        is not WorkflowFailurePolicyOutcome.COMPENSATE
    ):
        raise CompensationError(
            "Failure Policy does not require COMPENSATE"
        )

    compensation_id = hashlib.sha256(
        (
            "ucf_compensation_v1"
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

    return CompensationInstruction(
        compensation_id=
            compensation_id,

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

        disposition=
            CompensationDisposition.REQUIRED,

        reason_codes=
            terminal_failure.policy_decision.reason_codes,

        business_compensation_executed=
            False,
    )


__all__ = [
    "COMPENSATION_VERSION",
    "COMPENSATION_SCHEMA_VERSION",
    "CompensationError",
    "CompensationDisposition",
    "CompensationInstruction",
    "create_compensation_instruction",
]
