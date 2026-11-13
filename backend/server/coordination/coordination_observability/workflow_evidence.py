"""
LinkCraftor — Universal Coordination Framework

Phase 10.4 — Workflow Evidence.

Immutable aggregate evidence envelope over existing UCF authorities.

This module does not create a new evidence database and does not persist.
"""

from __future__ import annotations

import hashlib
import json

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Tuple

from backend.server.coordination.universal_workflows.contract import (
    UniversalWorkflow,
)

from backend.server.coordination.workflow_lifecycle.lifecycle_history import (
    LifecycleHistoryEntry,
)

from backend.server.coordination.workflow_persistence.stage_state_store import (
    StageStateRecord,
)

from backend.server.coordination.coordination_observability.workflow_progress import (
    WorkflowProgressSnapshot,
    build_workflow_progress,
)

from backend.server.coordination.coordination_observability.workflow_metrics import (
    WorkflowMetricsSnapshot,
    build_workflow_metrics,
)

from backend.server.coordination.coordination_observability.stage_metrics import (
    StageMetricsSnapshot,
    build_stage_metrics,
)


WORKFLOW_EVIDENCE_VERSION = (
    "workflow_evidence_v10.4.0"
)

WORKFLOW_EVIDENCE_SCHEMA_VERSION = (
    "workflow_evidence_schema_v1"
)


@dataclass(
    frozen=True,
    slots=True,
)
class WorkflowEvidenceEnvelope:

    evidence_id: str

    workflow_id: str
    correlation_id: str
    workspace_id: str

    status: str

    progress: WorkflowProgressSnapshot
    workflow_metrics: WorkflowMetricsSnapshot
    stage_metrics: StageMetricsSnapshot

    lifecycle_event_count: int

    persistence_reference: str | None
    checkpoint_reference: str | None

    evidence_version: str = (
        WORKFLOW_EVIDENCE_VERSION
    )

    schema_version: str = (
        WORKFLOW_EVIDENCE_SCHEMA_VERSION
    )

    def to_dict(
        self,
    ) -> Mapping[str, Any]:

        return MappingProxyType({
            "evidence_id":
                self.evidence_id,

            "workflow_id":
                self.workflow_id,

            "correlation_id":
                self.correlation_id,

            "workspace_id":
                self.workspace_id,

            "status":
                self.status,

            "progress":
                dict(
                    self.progress.to_dict()
                ),

            "workflow_metrics":
                dict(
                    self.workflow_metrics.to_dict()
                ),

            "stage_metrics":
                dict(
                    self.stage_metrics.to_dict()
                ),

            "lifecycle_event_count":
                self.lifecycle_event_count,

            "persistence_reference":
                self.persistence_reference,

            "checkpoint_reference":
                self.checkpoint_reference,

            "evidence_version":
                self.evidence_version,

            "schema_version":
                self.schema_version,
        })


def build_workflow_evidence(
    workflow: UniversalWorkflow,
    *,
    stage_states: Iterable[
        StageStateRecord
    ] = (),
    lifecycle_history: Iterable[
        LifecycleHistoryEntry
    ] = (),
    persistence_reference: str | None = None,
    checkpoint_reference: str | None = None,
) -> WorkflowEvidenceEnvelope:

    stage_states_tuple = tuple(
        stage_states
    )

    history_tuple = tuple(
        lifecycle_history
    )

    progress = build_workflow_progress(
        workflow
    )

    workflow_metrics = build_workflow_metrics(
        workflow,
        lifecycle_history=
            history_tuple,
    )

    stage_metrics = build_stage_metrics(
        stage_states_tuple
    )

    if (
        stage_metrics.workflow_id
        and stage_metrics.workflow_id
        != workflow.workflow_id
    ):
        raise ValueError(
            "stage metrics workflow identity mismatch"
        )

    canonical = json.dumps(
        {
            "workflow_id":
                workflow.workflow_id,

            "correlation_id":
                workflow.correlation_id,

            "status":
                workflow.status.value,

            "progress":
                dict(
                    progress.to_dict()
                ),

            "workflow_metrics":
                dict(
                    workflow_metrics.to_dict()
                ),

            "stage_metrics":
                dict(
                    stage_metrics.to_dict()
                ),

            "lifecycle_event_count":
                len(
                    history_tuple
                ),

            "persistence_reference":
                persistence_reference,

            "checkpoint_reference":
                checkpoint_reference,
        },
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        default=str,
    )

    evidence_id = hashlib.sha256(
        canonical.encode(
            "utf-8"
        )
    ).hexdigest().upper()

    return WorkflowEvidenceEnvelope(
        evidence_id=
            evidence_id,

        workflow_id=
            workflow.workflow_id,

        correlation_id=
            workflow.correlation_id,

        workspace_id=
            workflow.workspace_id,

        status=
            workflow.status.value,

        progress=
            progress,

        workflow_metrics=
            workflow_metrics,

        stage_metrics=
            stage_metrics,

        lifecycle_event_count=
            len(
                history_tuple
            ),

        persistence_reference=
            persistence_reference,

        checkpoint_reference=
            checkpoint_reference,
    )


__all__ = [
    "WORKFLOW_EVIDENCE_VERSION",
    "WORKFLOW_EVIDENCE_SCHEMA_VERSION",
    "WorkflowEvidenceEnvelope",
    "build_workflow_evidence",
]
