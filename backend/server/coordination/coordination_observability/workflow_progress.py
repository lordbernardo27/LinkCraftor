"""
LinkCraftor — Universal Coordination Framework

Phase 10.1 — Workflow Progress.

Pure read-only projection of canonical UniversalWorkflow progress.

No persistence, lifecycle mutation, Runtime metrics or telemetry emission.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Tuple

from backend.server.coordination.universal_workflows.contract import (
    UniversalWorkflow,
)


WORKFLOW_PROGRESS_VERSION = (
    "workflow_progress_v10.1.0"
)

WORKFLOW_PROGRESS_SCHEMA_VERSION = (
    "workflow_progress_schema_v1"
)


class WorkflowProgressError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class WorkflowProgressSnapshot:

    workflow_id: str
    correlation_id: str
    workspace_id: str

    status: str
    current_stage: str | None

    completed_stage_count: int
    pending_stage_count: int
    failed_stage_count: int
    skipped_stage_count: int

    known_stage_count: int
    terminal_stage_count: int

    completion_ratio: float

    completed_stages: Tuple[str, ...]
    pending_stages: Tuple[str, ...]
    failed_stages: Tuple[str, ...]
    skipped_stages: Tuple[str, ...]

    progress_version: str = (
        WORKFLOW_PROGRESS_VERSION
    )

    schema_version: str = (
        WORKFLOW_PROGRESS_SCHEMA_VERSION
    )

    def to_dict(
        self,
    ) -> Mapping[str, Any]:

        return MappingProxyType({
            "workflow_id":
                self.workflow_id,

            "correlation_id":
                self.correlation_id,

            "workspace_id":
                self.workspace_id,

            "status":
                self.status,

            "current_stage":
                self.current_stage,

            "completed_stage_count":
                self.completed_stage_count,

            "pending_stage_count":
                self.pending_stage_count,

            "failed_stage_count":
                self.failed_stage_count,

            "skipped_stage_count":
                self.skipped_stage_count,

            "known_stage_count":
                self.known_stage_count,

            "terminal_stage_count":
                self.terminal_stage_count,

            "completion_ratio":
                self.completion_ratio,

            "completed_stages":
                self.completed_stages,

            "pending_stages":
                self.pending_stages,

            "failed_stages":
                self.failed_stages,

            "skipped_stages":
                self.skipped_stages,

            "progress_version":
                self.progress_version,

            "schema_version":
                self.schema_version,
        })


def build_workflow_progress(
    workflow: UniversalWorkflow,
) -> WorkflowProgressSnapshot:

    if not isinstance(
        workflow,
        UniversalWorkflow,
    ):
        raise WorkflowProgressError(
            "workflow must be UniversalWorkflow"
        )

    validation = workflow.validate()

    if not validation.is_valid:
        raise WorkflowProgressError(
            "UniversalWorkflow validation failed: "
            + "; ".join(
                validation.violations
            )
        )

    completed = tuple(
        workflow.completed_stages
    )

    pending = tuple(
        workflow.pending_stages
    )

    failed = tuple(
        workflow.failed_stages
    )

    skipped = tuple(
        workflow.skipped_stages
    )

    known = tuple(
        dict.fromkeys(
            completed
            + pending
            + failed
            + skipped
            + (
                (
                    workflow.current_stage,
                )
                if workflow.current_stage
                else ()
            )
        )
    )

    terminal_count = (
        len(completed)
        + len(failed)
        + len(skipped)
    )

    completion_ratio = (
        terminal_count
        / len(known)
        if known
        else 0.0
    )

    return WorkflowProgressSnapshot(
        workflow_id=
            workflow.workflow_id,

        correlation_id=
            workflow.correlation_id,

        workspace_id=
            workflow.workspace_id,

        status=
            workflow.status.value,

        current_stage=
            workflow.current_stage,

        completed_stage_count=
            len(completed),

        pending_stage_count=
            len(pending),

        failed_stage_count=
            len(failed),

        skipped_stage_count=
            len(skipped),

        known_stage_count=
            len(known),

        terminal_stage_count=
            terminal_count,

        completion_ratio=
            round(
                completion_ratio,
                6,
            ),

        completed_stages=
            completed,

        pending_stages=
            pending,

        failed_stages=
            failed,

        skipped_stages=
            skipped,
    )


__all__ = [
    "WORKFLOW_PROGRESS_VERSION",
    "WORKFLOW_PROGRESS_SCHEMA_VERSION",
    "WorkflowProgressError",
    "WorkflowProgressSnapshot",
    "build_workflow_progress",
]
