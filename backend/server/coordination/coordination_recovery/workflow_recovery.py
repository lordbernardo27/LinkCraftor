"""
LinkCraftor — Universal Coordination Framework

Phase 9.3 — Workflow Recovery.

Transitions an eligible persisted UCF workflow into RECOVERING when the
frozen Phase 9.1/9.2 evidence authorizes workflow recovery.

This component does NOT:
- retry/requeue Runtime jobs,
- execute Runtime recovery,
- restart workers,
- mutate Runtime orchestration,
- perform compensation,
- perform manual intervention.
"""

from __future__ import annotations

import dataclasses
import hashlib

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Optional, Tuple

from backend.server.coordination.universal_workflows.contract import (
    UniversalWorkflow,
    UniversalWorkflowStatus,
)

from backend.server.coordination.workflow_lifecycle.transition_validation import (
    require_valid_workflow_transition,
)

from backend.server.coordination.workflow_lifecycle.terminal_state_protection import (
    require_terminal_state_mutation_allowed,
)

from backend.server.coordination.workflow_lifecycle.lifecycle_history import (
    LifecycleHistoryEntry,
    append_lifecycle_history,
    create_lifecycle_history_entry,
)

from backend.server.coordination.workflow_persistence.repository import (
    WorkflowPersistenceEvidence,
    WorkflowRepository,
)

from backend.server.coordination.coordination_recovery.failure_policy import (
    WorkflowFailurePolicyOutcome,
)

from backend.server.coordination.coordination_recovery.terminal_failure_handling import (
    TerminalFailureHandlingResult,
)


WORKFLOW_RECOVERY_VERSION = (
    "workflow_recovery_v9.3.0"
)

WORKFLOW_RECOVERY_SCHEMA_VERSION = (
    "workflow_recovery_schema_v1"
)


class WorkflowRecoveryError(
    RuntimeError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class WorkflowRecoveryResult:

    workflow: UniversalWorkflow

    history: Tuple[
        LifecycleHistoryEntry,
        ...
    ]

    recovery_entry: LifecycleHistoryEntry

    terminal_failure: TerminalFailureHandlingResult

    persistence_evidence: WorkflowPersistenceEvidence

    runtime_recovery_executed: bool = False

    recovery_version: str = (
        WORKFLOW_RECOVERY_VERSION
    )

    schema_version: str = (
        WORKFLOW_RECOVERY_SCHEMA_VERSION
    )


def _utc_now() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()


def _event_id(
    workflow_id: str,
    correlation_id: str,
    stage_id: str,
    job_id: str,
    occurred_at: str,
) -> str:

    return hashlib.sha256(
        (
            "ucf_phase_9_3_recovery_v1"
            + "\0"
            + workflow_id
            + "\0"
            + correlation_id
            + "\0"
            + stage_id
            + "\0"
            + job_id
            + "\0"
            + occurred_at
        ).encode(
            "utf-8"
        )
    ).hexdigest().upper()


def begin_workflow_recovery(
    *,
    workflow_repository: WorkflowRepository,
    terminal_failure: TerminalFailureHandlingResult,
    lifecycle_history: Iterable[
        LifecycleHistoryEntry
    ] = (),
    reason: Optional[str] = None,
    actor_id: Optional[str] = None,
    occurred_at: Optional[str] = None,
) -> WorkflowRecoveryResult:

    if not isinstance(
        workflow_repository,
        WorkflowRepository,
    ):
        raise TypeError(
            "workflow_repository must be WorkflowRepository"
        )

    if not isinstance(
        terminal_failure,
        TerminalFailureHandlingResult,
    ):
        raise TypeError(
            "terminal_failure must be TerminalFailureHandlingResult"
        )

    if (
        terminal_failure.policy_decision.outcome
        is not WorkflowFailurePolicyOutcome.RECOVER
    ):
        raise WorkflowRecoveryError(
            "Failure policy does not authorize RECOVER"
        )

    record = (
        workflow_repository.load_workflow_record(
            terminal_failure.workflow_id
        )
    )

    workflow = record.workflow

    if (
        workflow.correlation_id
        != terminal_failure.correlation_id
    ):
        raise WorkflowRecoveryError(
            "workflow correlation identity mismatch"
        )

    require_terminal_state_mutation_allowed(
        workflow.status,
        UniversalWorkflowStatus.RECOVERING,
    )

    require_valid_workflow_transition(
        workflow.status,
        UniversalWorkflowStatus.RECOVERING,
    )

    when = str(
        occurred_at
        or _utc_now()
    ).strip()

    recovering = dataclasses.replace(
        workflow,

        status=
            UniversalWorkflowStatus.RECOVERING,

        updated_at=
            when,
    )

    validation = recovering.validate()

    if not validation.is_valid:
        raise WorkflowRecoveryError(
            "Recovering UniversalWorkflow invalid: "
            + "; ".join(
                validation.violations
            )
        )

    entry = create_lifecycle_history_entry(
        event_id=
            _event_id(
                workflow.workflow_id,
                workflow.correlation_id,
                terminal_failure.stage_id,
                terminal_failure.job_id,
                when,
            ),

        workflow_id=
            workflow.workflow_id,

        correlation_id=
            workflow.correlation_id,

        from_state=
            workflow.status,

        to_state=
            UniversalWorkflowStatus.RECOVERING,

        occurred_at=
            when,

        reason=
            reason
            or "terminal failure authorized workflow recovery",

        source=
            "ucf_phase_9_3_workflow_recovery",

        actor_id=
            actor_id,

        metadata={
            "stage_id":
                terminal_failure.stage_id,

            "job_id":
                terminal_failure.job_id,

            "failure_code":
                terminal_failure.failure_code,

            "failure_policy_outcome":
                terminal_failure.policy_decision.outcome.value,

            "runtime_recovery_executed":
                False,
        },
    )

    history = append_lifecycle_history(
        tuple(
            lifecycle_history
        ),
        entry,
    )

    persistence_evidence = (
        workflow_repository.save_workflow(
            recovering,

            expected_current_fingerprint=
                record.evidence.workflow_content_fingerprint,
        )
    )

    return WorkflowRecoveryResult(
        workflow=
            recovering,

        history=
            history,

        recovery_entry=
            entry,

        terminal_failure=
            terminal_failure,

        persistence_evidence=
            persistence_evidence,

        runtime_recovery_executed=
            False,
    )


__all__ = [
    "WORKFLOW_RECOVERY_VERSION",
    "WORKFLOW_RECOVERY_SCHEMA_VERSION",
    "WorkflowRecoveryError",
    "WorkflowRecoveryResult",
    "begin_workflow_recovery",
]
