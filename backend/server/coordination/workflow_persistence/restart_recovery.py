"""
LinkCraftor — Universal Coordination Framework

Phase 8.6 — Restart Recovery

Restores persisted UCF workflow coordination evidence after process restart.

The recovered workflow enters canonical RECOVERING state.

This module does NOT:
- restart services,
- restore Runtime workers,
- requeue jobs,
- invoke handlers,
- resume Runtime execution,
- perform Runtime crash-recovery actions.

Runtime recovery remains a separate authority.
"""

from __future__ import annotations

import dataclasses
import hashlib

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

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
    create_lifecycle_history_entry,
)

from backend.server.coordination.workflow_persistence.repository import (
    WorkflowPersistenceEvidence,
    WorkflowRepository,
)

from backend.server.coordination.workflow_persistence.checkpointing import (
    WorkflowCheckpoint,
    WorkflowCheckpointRepository,
)


RESTART_RECOVERY_VERSION = "restart_recovery_v8.6.0"
RESTART_RECOVERY_SCHEMA_VERSION = "restart_recovery_schema_v1"


class RestartRecoveryError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class RestartRecoveryResult:

    checkpoint: WorkflowCheckpoint

    source_workflow: UniversalWorkflow
    recovering_workflow: UniversalWorkflow

    recovery_entry: LifecycleHistoryEntry

    persisted_stage_state_count: int
    persisted_history_count: int

    persistence_evidence: WorkflowPersistenceEvidence

    runtime_recovery_executed: bool = False

    recovery_version: str = RESTART_RECOVERY_VERSION
    schema_version: str = RESTART_RECOVERY_SCHEMA_VERSION


def _utc_now() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()


def _event_id(
    workflow_id: str,
    correlation_id: str,
    checkpoint_id: str,
    occurred_at: str,
) -> str:

    return hashlib.sha256(
        (
            "ucf_restart_recovery_v1"
            + "\0"
            + workflow_id
            + "\0"
            + correlation_id
            + "\0"
            + checkpoint_id
            + "\0"
            + occurred_at
        ).encode(
            "utf-8"
        )
    ).hexdigest().upper()


def prepare_restart_recovery(
    *,
    workflow_repository: WorkflowRepository,
    checkpoint_repository: WorkflowCheckpointRepository,
    checkpoint_id: str,
    reason: Optional[str] = None,
    actor_id: Optional[str] = None,
    occurred_at: Optional[str] = None,
) -> RestartRecoveryResult:

    if not isinstance(
        workflow_repository,
        WorkflowRepository,
    ):
        raise TypeError(
            "workflow_repository must be WorkflowRepository"
        )

    if not isinstance(
        checkpoint_repository,
        WorkflowCheckpointRepository,
    ):
        raise TypeError(
            "checkpoint_repository must be WorkflowCheckpointRepository"
        )

    checkpoint = checkpoint_repository.load(
        checkpoint_id
    )

    source_workflow = UniversalWorkflow.from_dict(
        checkpoint.workflow_snapshot
    )

    source_validation = source_workflow.validate()

    if not source_validation.is_valid:
        raise RestartRecoveryError(
            "Checkpoint workflow snapshot is invalid: "
            + "; ".join(
                source_validation.violations
            )
        )

    current_record = workflow_repository.load_workflow_record(
        checkpoint.workflow_id
    )

    current = current_record.workflow

    if (
        current.workflow_id
        != source_workflow.workflow_id
        or current.correlation_id
        != source_workflow.correlation_id
    ):
        raise RestartRecoveryError(
            "Checkpoint identity does not match persisted workflow."
        )

    if (
        current.status
        != source_workflow.status
    ):
        raise RestartRecoveryError(
            "Persisted workflow state has diverged from checkpoint."
        )

    require_terminal_state_mutation_allowed(
        source_workflow.status,
        UniversalWorkflowStatus.RECOVERING,
    )

    require_valid_workflow_transition(
        source_workflow.status,
        UniversalWorkflowStatus.RECOVERING,
    )

    when = str(
        occurred_at
        or _utc_now()
    ).strip()

    recovering = dataclasses.replace(
        source_workflow,

        status=
            UniversalWorkflowStatus.RECOVERING,

        updated_at=
            when,
    )

    validation = recovering.validate()

    if not validation.is_valid:
        raise RestartRecoveryError(
            "Recovering UniversalWorkflow is invalid: "
            + "; ".join(
                validation.violations
            )
        )

    entry = create_lifecycle_history_entry(
        event_id=
            _event_id(
                source_workflow.workflow_id,
                source_workflow.correlation_id,
                checkpoint.checkpoint_id,
                when,
            ),

        workflow_id=
            source_workflow.workflow_id,

        correlation_id=
            source_workflow.correlation_id,

        from_state=
            source_workflow.status,

        to_state=
            UniversalWorkflowStatus.RECOVERING,

        occurred_at=
            when,

        reason=
            reason,

        source=
            "ucf_phase_8_6_restart_recovery",

        actor_id=
            actor_id,

        metadata={
            "checkpoint_id":
                checkpoint.checkpoint_id,

            "recovery_version":
                RESTART_RECOVERY_VERSION,

            "runtime_recovery_executed":
                False,
        },
    )

    evidence = workflow_repository.save_workflow(
        recovering,

        expected_current_fingerprint=
            current_record.evidence.workflow_content_fingerprint,
    )

    return RestartRecoveryResult(
        checkpoint=
            checkpoint,

        source_workflow=
            source_workflow,

        recovering_workflow=
            recovering,

        recovery_entry=
            entry,

        persisted_stage_state_count=
            len(
                checkpoint.stage_states
            ),

        persisted_history_count=
            len(
                checkpoint.lifecycle_history
            ),

        persistence_evidence=
            evidence,

        runtime_recovery_executed=
            False,
    )


__all__ = [
    "RESTART_RECOVERY_VERSION",
    "RESTART_RECOVERY_SCHEMA_VERSION",
    "RestartRecoveryError",
    "RestartRecoveryResult",
    "prepare_restart_recovery",
]
