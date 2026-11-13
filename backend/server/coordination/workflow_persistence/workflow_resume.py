"""
LinkCraftor — Universal Coordination Framework

Phase 8.5 — Resume

Coordination-level resume of a persisted PAUSED UniversalWorkflow.

Allowed UCF resume destinations:
- READY
- RUNNING

This module does NOT resume Runtime workers or Runtime execution.
Runtime resume remains owned by Universal Runtime.
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


WORKFLOW_RESUME_VERSION = "workflow_resume_v8.5.0"
WORKFLOW_RESUME_SCHEMA_VERSION = "workflow_resume_schema_v1"


class WorkflowResumeError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class WorkflowResumeResult:

    workflow: UniversalWorkflow

    history: Tuple[
        LifecycleHistoryEntry,
        ...
    ]

    resume_entry: LifecycleHistoryEntry

    persistence_evidence: WorkflowPersistenceEvidence

    resume_version: str = WORKFLOW_RESUME_VERSION
    schema_version: str = WORKFLOW_RESUME_SCHEMA_VERSION


def _utc_now() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat()


def _event_id(
    workflow_id: str,
    correlation_id: str,
    target: UniversalWorkflowStatus,
    occurred_at: str,
) -> str:

    return hashlib.sha256(
        (
            "ucf_resume_v1"
            + "\0"
            + workflow_id
            + "\0"
            + correlation_id
            + "\0"
            + target.value
            + "\0"
            + occurred_at
        ).encode(
            "utf-8"
        )
    ).hexdigest().upper()


def resume_workflow(
    *,
    workflow_repository: WorkflowRepository,
    workflow_id: str,
    target_state: UniversalWorkflowStatus = UniversalWorkflowStatus.READY,
    lifecycle_history: Iterable[LifecycleHistoryEntry] = (),
    reason: Optional[str] = None,
    actor_id: Optional[str] = None,
    occurred_at: Optional[str] = None,
) -> WorkflowResumeResult:

    if not isinstance(
        workflow_repository,
        WorkflowRepository,
    ):
        raise TypeError(
            "workflow_repository must be WorkflowRepository"
        )

    if target_state not in (
        UniversalWorkflowStatus.READY,
        UniversalWorkflowStatus.RUNNING,
    ):
        raise WorkflowResumeError(
            "Resume target must be READY or RUNNING."
        )

    record = workflow_repository.load_workflow_record(
        workflow_id
    )

    workflow = record.workflow

    if (
        workflow.status
        is not UniversalWorkflowStatus.PAUSED
    ):
        raise WorkflowResumeError(
            "Only a PAUSED workflow may be resumed."
        )

    require_terminal_state_mutation_allowed(
        workflow.status,
        target_state,
    )

    require_valid_workflow_transition(
        workflow.status,
        target_state,
    )

    when = str(
        occurred_at
        or _utc_now()
    ).strip()

    replacements = {
        "status":
            target_state,

        "updated_at":
            when,
    }

    if (
        target_state
        is UniversalWorkflowStatus.RUNNING
        and not workflow.started_at
    ):
        replacements[
            "started_at"
        ] = when

    resumed = dataclasses.replace(
        workflow,
        **replacements,
    )

    validation = resumed.validate()

    if not validation.is_valid:
        raise WorkflowResumeError(
            "Resumed UniversalWorkflow is invalid: "
            + "; ".join(
                validation.violations
            )
        )

    entry = create_lifecycle_history_entry(
        event_id=
            _event_id(
                workflow.workflow_id,
                workflow.correlation_id,
                target_state,
                when,
            ),

        workflow_id=
            workflow.workflow_id,

        correlation_id=
            workflow.correlation_id,

        from_state=
            workflow.status,

        to_state=
            target_state,

        occurred_at=
            when,

        reason=
            reason,

        source=
            "ucf_phase_8_5_resume",

        actor_id=
            actor_id,

        metadata={
            "resume_version":
                WORKFLOW_RESUME_VERSION,

            "resume_target":
                target_state.value,
        },
    )

    history = append_lifecycle_history(
        tuple(
            lifecycle_history
        ),
        entry,
    )

    evidence = workflow_repository.save_workflow(
        resumed,

        expected_current_fingerprint=
            record.evidence.workflow_content_fingerprint,
    )

    return WorkflowResumeResult(
        workflow=
            resumed,

        history=
            history,

        resume_entry=
            entry,

        persistence_evidence=
            evidence,
    )


__all__ = [
    "WORKFLOW_RESUME_VERSION",
    "WORKFLOW_RESUME_SCHEMA_VERSION",
    "WorkflowResumeError",
    "WorkflowResumeResult",
    "resume_workflow",
]
