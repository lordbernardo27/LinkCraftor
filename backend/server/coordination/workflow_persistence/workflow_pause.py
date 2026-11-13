"""
LinkCraftor — Universal Coordination Framework

Phase 8.4 — Pause

Coordination-level workflow pause persistence.

This module:
- validates the canonical lifecycle transition,
- enforces terminal-state protection,
- creates lifecycle evidence,
- creates a durable UCF workflow checkpoint,
- persists the PAUSED UniversalWorkflow using optimistic concurrency.

It does NOT:
- pause Runtime workers,
- suspend Runtime execution,
- mutate UniversalJob,
- requeue jobs,
- acquire or release Runtime leases,
- create a second Runtime pause subsystem.
"""

from __future__ import annotations

import dataclasses
import hashlib

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Optional, Tuple

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

from backend.server.coordination.workflow_persistence.stage_state_store import (
    StageStateRecord,
)

from backend.server.coordination.workflow_persistence.checkpointing import (
    WorkflowCheckpoint,
    WorkflowCheckpointRepository,
    create_workflow_checkpoint,
)


WORKFLOW_PAUSE_VERSION = "workflow_pause_v8.4.0"
WORKFLOW_PAUSE_SCHEMA_VERSION = "workflow_pause_schema_v1"


class WorkflowPauseError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class WorkflowPauseResult:

    workflow: UniversalWorkflow
    history: Tuple[LifecycleHistoryEntry, ...]
    pause_entry: LifecycleHistoryEntry

    checkpoint: WorkflowCheckpoint
    persistence_evidence: WorkflowPersistenceEvidence

    pause_version: str = WORKFLOW_PAUSE_VERSION
    schema_version: str = WORKFLOW_PAUSE_SCHEMA_VERSION


def _utc_now() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()


def _event_id(
    workflow_id: str,
    correlation_id: str,
    occurred_at: str,
) -> str:

    return hashlib.sha256(
        (
            "ucf_pause_v1"
            + "\0"
            + workflow_id
            + "\0"
            + correlation_id
            + "\0"
            + occurred_at
        ).encode(
            "utf-8"
        )
    ).hexdigest().upper()


def pause_workflow(
    *,
    workflow_repository: WorkflowRepository,
    checkpoint_repository: WorkflowCheckpointRepository,
    workflow_id: str,
    stage_states: Iterable[StageStateRecord] = (),
    lifecycle_history: Iterable[LifecycleHistoryEntry] = (),
    reason: Optional[str] = None,
    actor_id: Optional[str] = None,
    occurred_at: Optional[str] = None,
) -> WorkflowPauseResult:

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

    record = workflow_repository.load_workflow_record(
        workflow_id
    )

    workflow = record.workflow

    require_terminal_state_mutation_allowed(
        workflow.status,
        UniversalWorkflowStatus.PAUSED,
    )

    require_valid_workflow_transition(
        workflow.status,
        UniversalWorkflowStatus.PAUSED,
    )

    when = (
        str(
            occurred_at
            or _utc_now()
        ).strip()
    )

    if not when:
        raise WorkflowPauseError(
            "occurred_at must be non-empty"
        )

    paused = dataclasses.replace(
        workflow,
        status=
            UniversalWorkflowStatus.PAUSED,

        updated_at=
            when,
    )

    validation = paused.validate()

    if not validation.is_valid:
        raise WorkflowPauseError(
            "Paused UniversalWorkflow is invalid: "
            + "; ".join(
                validation.violations
            )
        )

    entry = create_lifecycle_history_entry(
        event_id=
            _event_id(
                workflow.workflow_id,
                workflow.correlation_id,
                when,
            ),

        workflow_id=
            workflow.workflow_id,

        correlation_id=
            workflow.correlation_id,

        from_state=
            workflow.status,

        to_state=
            UniversalWorkflowStatus.PAUSED,

        occurred_at=
            when,

        reason=
            reason,

        source=
            "ucf_phase_8_4_pause",

        actor_id=
            actor_id,

        metadata={
            "pause_version":
                WORKFLOW_PAUSE_VERSION,
        },
    )

    history = append_lifecycle_history(
        tuple(
            lifecycle_history
        ),
        entry,
    )

    checkpoint = create_workflow_checkpoint(
        workflow=
            paused,

        stage_states=
            tuple(
                stage_states
            ),

        lifecycle_history=
            history,
    )

    checkpoint_repository.save(
        checkpoint
    )

    evidence = workflow_repository.save_workflow(
        paused,

        expected_current_fingerprint=
            record.evidence.workflow_content_fingerprint,
    )

    return WorkflowPauseResult(
        workflow=
            paused,

        history=
            history,

        pause_entry=
            entry,

        checkpoint=
            checkpoint,

        persistence_evidence=
            evidence,
    )


__all__ = [
    "WORKFLOW_PAUSE_VERSION",
    "WORKFLOW_PAUSE_SCHEMA_VERSION",
    "WorkflowPauseError",
    "WorkflowPauseResult",
    "pause_workflow",
]
