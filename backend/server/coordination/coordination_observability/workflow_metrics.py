"""
LinkCraftor — Universal Coordination Framework

Phase 10.2 — Workflow Metrics.

Pure derived workflow metrics from canonical workflow + lifecycle history.

This does not emit Runtime metrics or create a metrics backend.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from backend.server.coordination.universal_workflows.contract import (
    UniversalWorkflow,
)

from backend.server.coordination.workflow_lifecycle.lifecycle_history import (
    LifecycleHistoryEntry,
    validate_lifecycle_history,
)

from backend.server.coordination.coordination_observability.workflow_progress import (
    WorkflowProgressSnapshot,
    build_workflow_progress,
)


WORKFLOW_METRICS_VERSION = (
    "workflow_metrics_v10.2.0"
)

WORKFLOW_METRICS_SCHEMA_VERSION = (
    "workflow_metrics_schema_v1"
)


class WorkflowMetricsError(
    ValueError
):
    pass


def _parse(
    value: str | None,
) -> datetime | None:

    if not value:
        return None

    return datetime.fromisoformat(
        value.replace(
            "Z",
            "+00:00",
        )
    )


@dataclass(
    frozen=True,
    slots=True,
)
class WorkflowMetricsSnapshot:

    workflow_id: str

    total_known_stages: int
    completed_stages: int
    failed_stages: int
    skipped_stages: int
    pending_stages: int

    completion_ratio: float
    failure_ratio: float

    lifecycle_transition_count: int

    elapsed_seconds: float | None

    metrics_version: str = (
        WORKFLOW_METRICS_VERSION
    )

    schema_version: str = (
        WORKFLOW_METRICS_SCHEMA_VERSION
    )

    def to_dict(
        self,
    ) -> Mapping[str, Any]:

        return MappingProxyType({
            "workflow_id":
                self.workflow_id,

            "total_known_stages":
                self.total_known_stages,

            "completed_stages":
                self.completed_stages,

            "failed_stages":
                self.failed_stages,

            "skipped_stages":
                self.skipped_stages,

            "pending_stages":
                self.pending_stages,

            "completion_ratio":
                self.completion_ratio,

            "failure_ratio":
                self.failure_ratio,

            "lifecycle_transition_count":
                self.lifecycle_transition_count,

            "elapsed_seconds":
                self.elapsed_seconds,

            "metrics_version":
                self.metrics_version,

            "schema_version":
                self.schema_version,
        })


def build_workflow_metrics(
    workflow: UniversalWorkflow,
    *,
    lifecycle_history: Iterable[
        LifecycleHistoryEntry
    ] = (),
) -> WorkflowMetricsSnapshot:

    progress = build_workflow_progress(
        workflow
    )

    history = tuple(
        lifecycle_history
    )

    history_validation = (
        validate_lifecycle_history(
            history
        )
    )

    if not history_validation.is_valid:
        raise WorkflowMetricsError(
            "Lifecycle history validation failed: "
            + "; ".join(
                history_validation.violations
            )
        )

    start = (
        _parse(
            workflow.started_at
        )
        or _parse(
            workflow.created_at
        )
    )

    end = (
        _parse(
            workflow.completed_at
        )
        or _parse(
            workflow.failed_at
        )
        or _parse(
            workflow.cancelled_at
        )
        or _parse(
            workflow.updated_at
        )
    )

    elapsed = None

    if (
        start is not None
        and end is not None
    ):
        elapsed = max(
            0.0,
            (
                end - start
            ).total_seconds(),
        )

    total = (
        progress.known_stage_count
    )

    failure_ratio = (
        progress.failed_stage_count
        / total
        if total
        else 0.0
    )

    return WorkflowMetricsSnapshot(
        workflow_id=
            workflow.workflow_id,

        total_known_stages=
            total,

        completed_stages=
            progress.completed_stage_count,

        failed_stages=
            progress.failed_stage_count,

        skipped_stages=
            progress.skipped_stage_count,

        pending_stages=
            progress.pending_stage_count,

        completion_ratio=
            progress.completion_ratio,

        failure_ratio=
            round(
                failure_ratio,
                6,
            ),

        lifecycle_transition_count=
            len(history),

        elapsed_seconds=
            elapsed,
    )


__all__ = [
    "WORKFLOW_METRICS_VERSION",
    "WORKFLOW_METRICS_SCHEMA_VERSION",
    "WorkflowMetricsError",
    "WorkflowMetricsSnapshot",
    "build_workflow_metrics",
]
