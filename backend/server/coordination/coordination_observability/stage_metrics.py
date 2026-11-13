"""
LinkCraftor — Universal Coordination Framework

Phase 10.3 — Stage Metrics.

Pure aggregation over persisted StageStateRecord evidence.

No Runtime metric emission or persistence mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Tuple

from backend.server.coordination.workflow_persistence.stage_state_store import (
    StageStateRecord,
)


STAGE_METRICS_VERSION = (
    "stage_metrics_v10.3.0"
)

STAGE_METRICS_SCHEMA_VERSION = (
    "stage_metrics_schema_v1"
)


class StageMetricsError(
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
class StageMetric:

    stage_id: str
    status: str

    duration_seconds: float | None

    failure_code: str | None
    artifact_count: int

    terminal: bool


@dataclass(
    frozen=True,
    slots=True,
)
class StageMetricsSnapshot:

    workflow_id: str

    stage_count: int
    completed_count: int
    failed_count: int
    skipped_count: int
    other_count: int

    total_duration_seconds: float
    average_duration_seconds: float | None

    stages: Tuple[
        StageMetric,
        ...
    ]

    metrics_version: str = (
        STAGE_METRICS_VERSION
    )

    schema_version: str = (
        STAGE_METRICS_SCHEMA_VERSION
    )

    def to_dict(
        self,
    ) -> Mapping[str, Any]:

        return MappingProxyType({
            "workflow_id":
                self.workflow_id,

            "stage_count":
                self.stage_count,

            "completed_count":
                self.completed_count,

            "failed_count":
                self.failed_count,

            "skipped_count":
                self.skipped_count,

            "other_count":
                self.other_count,

            "total_duration_seconds":
                self.total_duration_seconds,

            "average_duration_seconds":
                self.average_duration_seconds,

            "stages":
                tuple(
                    {
                        "stage_id":
                            item.stage_id,

                        "status":
                            item.status,

                        "duration_seconds":
                            item.duration_seconds,

                        "failure_code":
                            item.failure_code,

                        "artifact_count":
                            item.artifact_count,

                        "terminal":
                            item.terminal,
                    }
                    for item
                    in self.stages
                ),

            "metrics_version":
                self.metrics_version,

            "schema_version":
                self.schema_version,
        })


def build_stage_metrics(
    stage_states: Iterable[
        StageStateRecord
    ],
) -> StageMetricsSnapshot:

    records = tuple(
        stage_states
    )

    if not records:
        return StageMetricsSnapshot(
            workflow_id=
                "",

            stage_count=
                0,

            completed_count=
                0,

            failed_count=
                0,

            skipped_count=
                0,

            other_count=
                0,

            total_duration_seconds=
                0.0,

            average_duration_seconds=
                None,

            stages=(),
        )

    for record in records:

        if not isinstance(
            record,
            StageStateRecord,
        ):
            raise StageMetricsError(
                "all records must be StageStateRecord"
            )

    workflow_ids = {
        record.workflow_id
        for record
        in records
    }

    if len(workflow_ids) != 1:
        raise StageMetricsError(
            "all stage-state records must belong to one workflow"
        )

    metrics = []
    durations = []

    completed = 0
    failed = 0
    skipped = 0
    other = 0

    for record in records:

        status = str(
            record.status
        ).upper()

        start = _parse(
            record.started_at
        )

        end = _parse(
            record.finished_at
        )

        duration = None

        if (
            start is not None
            and end is not None
        ):
            duration = max(
                0.0,
                (
                    end - start
                ).total_seconds(),
            )

            durations.append(
                duration
            )

        terminal = status in {
            "COMPLETED",
            "FAILED",
            "SKIPPED",
        }

        if status == "COMPLETED":
            completed += 1

        elif status == "FAILED":
            failed += 1

        elif status == "SKIPPED":
            skipped += 1

        else:
            other += 1

        metrics.append(
            StageMetric(
                stage_id=
                    record.stage_id,

                status=
                    status,

                duration_seconds=
                    duration,

                failure_code=
                    record.failure_code,

                artifact_count=
                    len(
                        record.artifact_references
                    ),

                terminal=
                    terminal,
            )
        )

    total_duration = sum(
        durations
    )

    average = (
        total_duration
        / len(durations)
        if durations
        else None
    )

    return StageMetricsSnapshot(
        workflow_id=
            records[0].workflow_id,

        stage_count=
            len(records),

        completed_count=
            completed,

        failed_count=
            failed,

        skipped_count=
            skipped,

        other_count=
            other,

        total_duration_seconds=
            total_duration,

        average_duration_seconds=
            average,

        stages=
            tuple(
                metrics
            ),
    )


__all__ = [
    "STAGE_METRICS_VERSION",
    "STAGE_METRICS_SCHEMA_VERSION",
    "StageMetricsError",
    "StageMetric",
    "StageMetricsSnapshot",
    "build_stage_metrics",
]
