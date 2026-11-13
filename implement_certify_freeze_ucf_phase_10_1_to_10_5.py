from __future__ import annotations

import hashlib
import importlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

OBS_ROOT = (
    ROOT
    / "backend/server/coordination/coordination_observability"
)

OBS_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)

INIT = OBS_ROOT / "__init__.py"

P101 = OBS_ROOT / "workflow_progress.py"
P102 = OBS_ROOT / "workflow_metrics.py"
P103 = OBS_ROOT / "stage_metrics.py"
P104 = OBS_ROOT / "workflow_evidence.py"
P105 = OBS_ROOT / "audit_trail.py"

F101 = OBS_ROOT / "workflow_progress.phase_10_1.freeze.json"
F102 = OBS_ROOT / "workflow_metrics.phase_10_2.freeze.json"
F103 = OBS_ROOT / "stage_metrics.phase_10_3.freeze.json"
F104 = OBS_ROOT / "workflow_evidence.phase_10_4.freeze.json"
F105 = OBS_ROOT / "audit_trail.phase_10_5.freeze.json"

BATCH_FREEZE = (
    OBS_ROOT
    / "coordination_observability.phase_10_1_to_10_5.freeze.json"
)

REPORT = (
    ROOT
    / "ucf_phase_10_1_to_10_5_certification_report.txt"
)

WORKFLOW_CONTRACT = (
    ROOT
    / "backend/server/coordination/universal_workflows/contract.py"
)

LIFECYCLE_HISTORY = (
    ROOT
    / "backend/server/coordination/workflow_lifecycle/lifecycle_history.py"
)

STAGE_STATE_STORE = (
    ROOT
    / "backend/server/coordination/workflow_persistence/stage_state_store.py"
)

WORKFLOW_STORE = (
    ROOT
    / "backend/server/coordination/workflow_persistence/repository.py"
)

CHECKPOINTING = (
    ROOT
    / "backend/server/coordination/workflow_persistence/checkpointing.py"
)

PHASE9_MASTER = (
    ROOT
    / "backend/server/coordination/coordination_recovery/"
    "phase_9_coordination_recovery.freeze.json"
)


EXPECTED = {
    WORKFLOW_CONTRACT:
        "9094A98D2B9DBD9CCED73514648BF5D4115C5092E547D19446AB0FE18FBE7089",

    LIFECYCLE_HISTORY:
        "D89F1D4FBC54307C7B8155E670CDD3C6C8771185DC8AFBE382A87BB34EDA8464",

    STAGE_STATE_STORE:
        "D7EA771B1461C10166697CF1DCA4B9B90B1D0ECEA7573555204B329EF5E32016",

    WORKFLOW_STORE:
        "E7A8379FABF9047F150E24DF4B2B9F138F4CE285C1B3D3EC43DD2F1A454C69DB",

    CHECKPOINTING:
        "DB79D0B23BE69387B116EEC470047350F070C5EAC669B97C83E93F6349A19669",

    PHASE9_MASTER:
        "49499305D5CCBF98C7C9E26D0606D9D1F7F2E528110B04DF8E14369E20C68E0C",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def section(title: str) -> None:
    print()
    print("=" * 120)
    print(title)
    print("=" * 120)


checks = []


def check(name: str, condition) -> None:
    ok = bool(condition)

    checks.append(
        (
            name,
            ok,
        )
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if not ok:
        raise RuntimeError(
            f"CHECK FAILED: {name}"
        )


def write_json(path: Path, data) -> None:
    path.write_text(
        json.dumps(
            data,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def purge() -> None:
    prefix = (
        "backend.server.coordination.coordination_observability"
    )

    for name in tuple(
        sys.modules
    ):
        if name.startswith(
            prefix
        ):
            sys.modules.pop(
                name,
                None,
            )

    importlib.invalidate_caches()


section(
    "LINKCRAFTOR — UCF PHASE 10.1–10.5 OBSERVABILITY BATCH"
)


# ==================================================================
# 0 — AUTHORITY GUARD
# ==================================================================

section(
    "0 — FROZEN AUTHORITY GUARD"
)


for path, expected in EXPECTED.items():

    check(
        f"exact authority: {path.name}",
        path.exists()
        and sha256(path)
        == expected,
    )


for path in (
    P101,
    P102,
    P103,
    P104,
    P105,
    F101,
    F102,
    F103,
    F104,
    F105,
    BATCH_FREEZE,
):

    check(
        f"not already installed: {path.name}",
        not path.exists(),
    )


coord_root = (
    ROOT
    / "backend/server/coordination"
)

runtime_root = (
    ROOT
    / "backend/server/runtime"
)


coord_before = {}

for path in coord_root.rglob("*"):

    if (
        path.is_file()
        and OBS_ROOT
        not in path.parents
    ):
        coord_before[
            path.resolve()
        ] = sha256(
            path
        )


runtime_before = {}

for path in runtime_root.rglob("*"):

    if path.is_file():
        runtime_before[
            path.resolve()
        ] = sha256(
            path
        )


# ==================================================================
# 1 — BACKUP
# ==================================================================

section(
    "1 — PRE-INSTALL BACKUP"
)


stamp = datetime.now(
    timezone.utc
).strftime(
    "%Y%m%dT%H%M%SZ"
)

backup = (
    ROOT
    / "backend/server/data/runtime_backups"
    / f"ucf_phase10_1_to_10_5_{stamp}"
)

backup.mkdir(
    parents=True,
    exist_ok=False,
)

print(
    "BACKUP:",
    backup,
)


created = [
    P101,
    P102,
    P103,
    P104,
    P105,
    F101,
    F102,
    F103,
    F104,
    F105,
    BATCH_FREEZE,
    REPORT,
]

init_created = False

if not INIT.exists():
    INIT.write_text(
        "",
        encoding="utf-8",
    )
    init_created = True


try:

    # ==============================================================
    # 2 — 10.1 WORKFLOW PROGRESS
    # ==============================================================

    section(
        "2 — INSTALL 10.1 WORKFLOW PROGRESS"
    )


    P101.write_text(
r'''"""
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
''',
        encoding="utf-8",
    )


    SHA101 = sha256(
        P101
    )


    # ==============================================================
    # 3 — 10.2 WORKFLOW METRICS
    # ==============================================================

    section(
        "3 — INSTALL 10.2 WORKFLOW METRICS"
    )


    P102.write_text(
r'''"""
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
''',
        encoding="utf-8",
    )


    SHA102 = sha256(
        P102
    )


    # ==============================================================
    # 4 — 10.3 STAGE METRICS
    # ==============================================================

    section(
        "4 — INSTALL 10.3 STAGE METRICS"
    )


    P103.write_text(
r'''"""
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
''',
        encoding="utf-8",
    )


    SHA103 = sha256(
        P103
    )


    # ==============================================================
    # 5 — 10.4 WORKFLOW EVIDENCE
    # ==============================================================

    section(
        "5 — INSTALL 10.4 WORKFLOW EVIDENCE"
    )


    P104.write_text(
r'''"""
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
''',
        encoding="utf-8",
    )


    SHA104 = sha256(
        P104
    )


    # ==============================================================
    # 6 — 10.5 AUDIT TRAIL
    # ==============================================================

    section(
        "6 — INSTALL 10.5 AUDIT TRAIL"
    )


    P105.write_text(
r'''"""
LinkCraftor — Universal Coordination Framework

Phase 10.5 — Audit Trail.

Deterministic read-only audit projection of existing lifecycle and
stage-state evidence.

It does not replace Phase 3 lifecycle history, mutate records, persist an
audit database or reuse Runtime Schema audit authority.
"""

from __future__ import annotations

import hashlib
import json

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Tuple

from backend.server.coordination.workflow_lifecycle.lifecycle_history import (
    LifecycleHistoryEntry,
    sort_lifecycle_history,
    validate_lifecycle_history,
)

from backend.server.coordination.workflow_persistence.stage_state_store import (
    StageStateRecord,
)


AUDIT_TRAIL_VERSION = (
    "audit_trail_v10.5.0"
)

AUDIT_TRAIL_SCHEMA_VERSION = (
    "audit_trail_schema_v1"
)


class AuditTrailError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class WorkflowAuditEntry:

    audit_id: str

    workflow_id: str
    correlation_id: str

    event_type: str
    occurred_at: str

    subject_id: str
    status: str

    source: str | None

    details: Mapping[
        str,
        Any,
    ]


@dataclass(
    frozen=True,
    slots=True,
)
class WorkflowAuditTrail:

    workflow_id: str
    entries: Tuple[
        WorkflowAuditEntry,
        ...
    ]

    trail_fingerprint: str

    audit_version: str = (
        AUDIT_TRAIL_VERSION
    )

    schema_version: str = (
        AUDIT_TRAIL_SCHEMA_VERSION
    )

    def to_dict(
        self,
    ) -> Mapping[str, Any]:

        return MappingProxyType({
            "workflow_id":
                self.workflow_id,

            "entries":
                tuple(
                    {
                        "audit_id":
                            entry.audit_id,

                        "workflow_id":
                            entry.workflow_id,

                        "correlation_id":
                            entry.correlation_id,

                        "event_type":
                            entry.event_type,

                        "occurred_at":
                            entry.occurred_at,

                        "subject_id":
                            entry.subject_id,

                        "status":
                            entry.status,

                        "source":
                            entry.source,

                        "details":
                            dict(
                                entry.details
                            ),
                    }
                    for entry
                    in self.entries
                ),

            "trail_fingerprint":
                self.trail_fingerprint,

            "audit_version":
                self.audit_version,

            "schema_version":
                self.schema_version,
        })


def _audit_id(
    payload: Mapping[
        str,
        Any,
    ],
) -> str:

    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        default=str,
    )

    return hashlib.sha256(
        canonical.encode(
            "utf-8"
        )
    ).hexdigest().upper()


def build_workflow_audit_trail(
    *,
    lifecycle_history: Iterable[
        LifecycleHistoryEntry
    ] = (),
    stage_states: Iterable[
        StageStateRecord
    ] = (),
) -> WorkflowAuditTrail:

    history = tuple(
        lifecycle_history
    )

    states = tuple(
        stage_states
    )

    validation = validate_lifecycle_history(
        history
    )

    if not validation.is_valid:
        raise AuditTrailError(
            "Lifecycle history invalid: "
            + "; ".join(
                validation.violations
            )
        )

    workflow_ids = {
        entry.workflow_id
        for entry
        in history
    } | {
        state.workflow_id
        for state
        in states
    }

    if len(workflow_ids) > 1:
        raise AuditTrailError(
            "audit sources span multiple workflows"
        )

    workflow_id = (
        next(
            iter(
                workflow_ids
            )
        )
        if workflow_ids
        else ""
    )

    entries = []

    for entry in sort_lifecycle_history(
        history
    ):

        payload = {
            "workflow_id":
                entry.workflow_id,

            "correlation_id":
                entry.correlation_id,

            "event_type":
                "WORKFLOW_TRANSITION",

            "occurred_at":
                entry.occurred_at,

            "subject_id":
                entry.workflow_id,

            "status":
                entry.to_state.value,

            "source":
                entry.source,

            "details": {
                "event_id":
                    entry.event_id,

                "from_state":
                    entry.from_state.value,

                "to_state":
                    entry.to_state.value,

                "reason":
                    entry.reason,

                "actor_id":
                    entry.actor_id,
            },
        }

        entries.append(
            WorkflowAuditEntry(
                audit_id=
                    _audit_id(
                        payload
                    ),

                workflow_id=
                    entry.workflow_id,

                correlation_id=
                    entry.correlation_id,

                event_type=
                    "WORKFLOW_TRANSITION",

                occurred_at=
                    entry.occurred_at,

                subject_id=
                    entry.workflow_id,

                status=
                    entry.to_state.value,

                source=
                    entry.source,

                details=
                    payload[
                        "details"
                    ],
            )
        )

    for state in sorted(
        states,
        key=lambda item: (
            item.recorded_at,
            item.stage_id,
        ),
    ):

        payload = {
            "workflow_id":
                state.workflow_id,

            "correlation_id":
                state.correlation_id,

            "event_type":
                "STAGE_STATE",

            "occurred_at":
                state.recorded_at,

            "subject_id":
                state.stage_id,

            "status":
                state.status,

            "source":
                "stage_state_store",

            "details": {
                "stage_version":
                    state.stage_version,

                "result_id":
                    state.result_id,

                "result_reference":
                    state.result_reference,

                "failure_code":
                    state.failure_code,

                "record_fingerprint":
                    state.record_fingerprint,
            },
        }

        entries.append(
            WorkflowAuditEntry(
                audit_id=
                    _audit_id(
                        payload
                    ),

                workflow_id=
                    state.workflow_id,

                correlation_id=
                    state.correlation_id,

                event_type=
                    "STAGE_STATE",

                occurred_at=
                    state.recorded_at,

                subject_id=
                    state.stage_id,

                status=
                    state.status,

                source=
                    "stage_state_store",

                details=
                    payload[
                        "details"
                    ],
            )
        )

    entries = tuple(
        sorted(
            entries,
            key=lambda item: (
                item.occurred_at,
                item.event_type,
                item.subject_id,
                item.audit_id,
            ),
        )
    )

    canonical = json.dumps(
        [
            {
                "audit_id":
                    item.audit_id,

                "occurred_at":
                    item.occurred_at,

                "event_type":
                    item.event_type,

                "subject_id":
                    item.subject_id,

                "status":
                    item.status,
            }
            for item
            in entries
        ],
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    )

    fingerprint = hashlib.sha256(
        canonical.encode(
            "utf-8"
        )
    ).hexdigest().upper()

    return WorkflowAuditTrail(
        workflow_id=
            workflow_id,

        entries=
            entries,

        trail_fingerprint=
            fingerprint,
    )


__all__ = [
    "AUDIT_TRAIL_VERSION",
    "AUDIT_TRAIL_SCHEMA_VERSION",
    "AuditTrailError",
    "WorkflowAuditEntry",
    "WorkflowAuditTrail",
    "build_workflow_audit_trail",
]
''',
        encoding="utf-8",
    )


    SHA105 = sha256(
        P105
    )


    # ==============================================================
    # 7 — IMPORT / VERSION VERIFICATION
    # ==============================================================

    section(
        "7 — IMPORT / CONTRACT VERIFICATION"
    )


    purge()


    m101 = importlib.import_module(
        "backend.server.coordination.coordination_observability."
        "workflow_progress"
    )

    m102 = importlib.import_module(
        "backend.server.coordination.coordination_observability."
        "workflow_metrics"
    )

    m103 = importlib.import_module(
        "backend.server.coordination.coordination_observability."
        "stage_metrics"
    )

    m104 = importlib.import_module(
        "backend.server.coordination.coordination_observability."
        "workflow_evidence"
    )

    m105 = importlib.import_module(
        "backend.server.coordination.coordination_observability."
        "audit_trail"
    )


    check(
        "10.1 version exact",
        m101.WORKFLOW_PROGRESS_VERSION
        == "workflow_progress_v10.1.0",
    )

    check(
        "10.2 version exact",
        m102.WORKFLOW_METRICS_VERSION
        == "workflow_metrics_v10.2.0",
    )

    check(
        "10.3 version exact",
        m103.STAGE_METRICS_VERSION
        == "stage_metrics_v10.3.0",
    )

    check(
        "10.4 version exact",
        m104.WORKFLOW_EVIDENCE_VERSION
        == "workflow_evidence_v10.4.0",
    )

    check(
        "10.5 version exact",
        m105.AUDIT_TRAIL_VERSION
        == "audit_trail_v10.5.0",
    )


    # ==============================================================
    # 8 — STATIC READ-ONLY BOUNDARY
    # ==============================================================

    section(
        "8 — STATIC READ-ONLY BOUNDARY"
    )


    forbidden = (
        "save_workflow",
        "submit_universal_job",
        "enqueue",
        "requeue",
        "claim_job",
        "run_one_universal_runtime_job_v1",
        "emit_metric",
        "emit_log",
        "send_alert",
    )


    for phase, path in (
        (
            "10.1",
            P101,
        ),
        (
            "10.2",
            P102,
        ),
        (
            "10.3",
            P103,
        ),
        (
            "10.4",
            P104,
        ),
        (
            "10.5",
            P105,
        ),
    ):

        text = path.read_text(
            encoding="utf-8"
        )

        for symbol in forbidden:

            check(
                f"{phase} mutation/emission authority absent: {symbol}",
                symbol
                not in text,
            )


    # ==============================================================
    # 9 — FUNCTIONAL VERIFICATION
    # ==============================================================

    section(
        "9 — FUNCTIONAL OBSERVABILITY VERIFICATION"
    )


    from backend.server.coordination.universal_workflows.contract import (
        UniversalWorkflow,
        UniversalWorkflowStatus,
    )

    from backend.server.coordination.workflow_lifecycle.lifecycle_history import (
        create_lifecycle_history_entry,
    )

    from backend.server.coordination.workflow_persistence.stage_state_store import (
        StageStateRecord,
    )


    workflow = UniversalWorkflow(
        workflow_id=
            "workflow-10",

        workflow_type=
            "observability-test",

        workflow_version=
            "1.0.0",

        workspace_id=
            "workspace-10",

        coordinator_id=
            "coordinator-10",

        coordinator_version=
            "1.0.0",

        correlation_id=
            "correlation-10",

        parent_workflow_id=
            None,

        root_workflow_id=
            "workflow-10",

        status=
            UniversalWorkflowStatus.RUNNING,

        input_reference=
            None,

        context={},

        metadata={},

        current_stage=
            "stage-3",

        completed_stages=(
            "stage-1",
            "stage-2",
        ),

        pending_stages=(
            "stage-3",
            "stage-4",
        ),

        failed_stages=(),

        skipped_stages=(),

        result_reference=
            None,

        artifact_references=(),

        idempotency_key=
            "observability-test-10",

        created_at=
            "2026-11-08T00:00:00+00:00",

        started_at=
            "2026-11-08T00:00:10+00:00",

        updated_at=
            "2026-11-08T00:01:10+00:00",

        completed_at=
            None,

        failed_at=
            None,

        cancelled_at=
            None,

        failure_code=
            None,

        failure_message=
            None,

        failure_details={},
    )


    check(
        "test workflow valid",
        workflow.validate().is_valid,
    )


    history_entry = (
        create_lifecycle_history_entry(
            event_id=
                "event-10-1",

            workflow_id=
                "workflow-10",

            correlation_id=
                "correlation-10",

            from_state=
                UniversalWorkflowStatus.READY,

            to_state=
                UniversalWorkflowStatus.RUNNING,

            occurred_at=
                "2026-11-08T00:00:10+00:00",

            reason=
                "test start",

            source=
                "phase10-test",
        )
    )


    stage1 = StageStateRecord(
        workflow_id=
            "workflow-10",

        correlation_id=
            "correlation-10",

        stage_id=
            "stage-1",

        stage_version=
            "1.0.0",

        status=
            "COMPLETED",

        result_id=
            "result-1",

        result_reference=
            "result://1",

        artifact_references=(),

        started_at=
            "2026-11-08T00:00:10+00:00",

        finished_at=
            "2026-11-08T00:00:30+00:00",

        failure_code=
            None,

        failure_message=
            None,

        failure_details={},

        metadata={},

        source_result_contract_version=
            "universal_stage_result_v1.4.0",

        recorded_at=
            "2026-11-08T00:00:31+00:00",

        record_fingerprint=
            "fingerprint-stage-1",
    )


    stage2 = StageStateRecord(
        workflow_id=
            "workflow-10",

        correlation_id=
            "correlation-10",

        stage_id=
            "stage-2",

        stage_version=
            "1.0.0",

        status=
            "COMPLETED",

        result_id=
            "result-2",

        result_reference=
            "result://2",

        artifact_references=(
            "artifact://2",
        ),

        started_at=
            "2026-11-08T00:00:31+00:00",

        finished_at=
            "2026-11-08T00:00:51+00:00",

        failure_code=
            None,

        failure_message=
            None,

        failure_details={},

        metadata={},

        source_result_contract_version=
            "universal_stage_result_v1.4.0",

        recorded_at=
            "2026-11-08T00:00:52+00:00",

        record_fingerprint=
            "fingerprint-stage-2",
    )


    progress = m101.build_workflow_progress(
        workflow
    )


    check(
        "10.1 known stage count exact",
        progress.known_stage_count
        == 4,
    )

    check(
        "10.1 terminal stage count exact",
        progress.terminal_stage_count
        == 2,
    )

    check(
        "10.1 completion ratio exact",
        progress.completion_ratio
        == 0.5,
    )


    workflow_metrics = (
        m102.build_workflow_metrics(
            workflow,
            lifecycle_history=(
                history_entry,
            ),
        )
    )


    check(
        "10.2 elapsed seconds exact",
        workflow_metrics.elapsed_seconds
        == 60.0,
    )

    check(
        "10.2 lifecycle transition count exact",
        workflow_metrics.lifecycle_transition_count
        == 1,
    )


    stage_metrics = (
        m103.build_stage_metrics(
            (
                stage1,
                stage2,
            )
        )
    )


    check(
        "10.3 stage count exact",
        stage_metrics.stage_count
        == 2,
    )

    check(
        "10.3 completed count exact",
        stage_metrics.completed_count
        == 2,
    )

    check(
        "10.3 duration aggregation exact",
        stage_metrics.total_duration_seconds
        == 40.0,
    )


    evidence = (
        m104.build_workflow_evidence(
            workflow,
            stage_states=(
                stage1,
                stage2,
            ),
            lifecycle_history=(
                history_entry,
            ),
            persistence_reference=
                "workflow-store://workflow-10",
            checkpoint_reference=
                "checkpoint://workflow-10",
        )
    )


    check(
        "10.4 evidence identity preserved",
        evidence.workflow_id
        == "workflow-10"
        and evidence.correlation_id
        == "correlation-10",
    )

    check(
        "10.4 evidence fingerprint present",
        len(
            evidence.evidence_id
        )
        == 64,
    )


    audit = (
        m105.build_workflow_audit_trail(
            lifecycle_history=(
                history_entry,
            ),
            stage_states=(
                stage1,
                stage2,
            ),
        )
    )


    check(
        "10.5 audit workflow identity exact",
        audit.workflow_id
        == "workflow-10",
    )

    check(
        "10.5 audit contains lifecycle plus stage events",
        len(
            audit.entries
        )
        == 3,
    )

    check(
        "10.5 audit fingerprint present",
        len(
            audit.trail_fingerprint
        )
        == 64,
    )


    # ==============================================================
    # 10 — FREEZE 10.1–10.5
    # ==============================================================

    section(
        "10 — FREEZE PHASE 10.1–10.5"
    )


    source_hashes = {
        "10.1":
            SHA101,

        "10.2":
            SHA102,

        "10.3":
            SHA103,

        "10.4":
            SHA104,

        "10.5":
            SHA105,
    }


    specs = (
        (
            F101,
            "10.1",
            "Workflow Progress",
            P101,
            "workflow_progress_v10.1.0",
            "workflow_progress_schema_v1",
        ),
        (
            F102,
            "10.2",
            "Workflow Metrics",
            P102,
            "workflow_metrics_v10.2.0",
            "workflow_metrics_schema_v1",
        ),
        (
            F103,
            "10.3",
            "Stage Metrics",
            P103,
            "stage_metrics_v10.3.0",
            "stage_metrics_schema_v1",
        ),
        (
            F104,
            "10.4",
            "Workflow Evidence",
            P104,
            "workflow_evidence_v10.4.0",
            "workflow_evidence_schema_v1",
        ),
        (
            F105,
            "10.5",
            "Audit Trail",
            P105,
            "audit_trail_v10.5.0",
            "audit_trail_schema_v1",
        ),
    )


    freeze_hashes = {}


    for (
        freeze_path,
        phase,
        component,
        source_path,
        version,
        schema,
    ) in specs:

        write_json(
            freeze_path,
            {
                "framework":
                    "Universal Coordination Framework",

                "phase":
                    phase,

                "component":
                    component,

                "certified":
                    True,

                "frozen":
                    True,

                "production": {
                    "path":
                        str(
                            source_path.relative_to(
                                ROOT
                            )
                        ).replace(
                            "\\",
                            "/",
                        ),

                    "version":
                        version,

                    "schema_version":
                        schema,

                    "sha256":
                        sha256(
                            source_path
                        ),
                },

                "input_authorities": {
                    "workflow_contract":
                        sha256(
                            WORKFLOW_CONTRACT
                        ),

                    "lifecycle_history":
                        sha256(
                            LIFECYCLE_HISTORY
                        ),

                    "stage_state_store":
                        sha256(
                            STAGE_STATE_STORE
                        ),

                    "workflow_store":
                        sha256(
                            WORKFLOW_STORE
                        ),

                    "checkpointing":
                        sha256(
                            CHECKPOINTING
                        ),

                    "phase_9_master":
                        sha256(
                            PHASE9_MASTER
                        ),
                },

                "read_only":
                    True,

                "runtime_observability_owned":
                    False,

                "freeze_created_at":
                    datetime.now(
                        timezone.utc
                    ).isoformat(),
            },
        )

        freeze_hashes[
            phase
        ] = sha256(
            freeze_path
        )


    # ==============================================================
    # 11 — BATCH CERTIFICATION
    # ==============================================================

    section(
        "11 — BATCH CERTIFICATION"
    )


    canonical = "\n".join(
        f"{phase}:{source_hashes[phase]}"
        for phase
        in (
            "10.1",
            "10.2",
            "10.3",
            "10.4",
            "10.5",
        )
    )


    COMPOSITE = hashlib.sha256(
        canonical.encode(
            "utf-8"
        )
    ).hexdigest().upper()


    passed_before_final = sum(
        1
        for _name, ok
        in checks
        if ok
    )


    REPORT.write_text(
        "\n".join(
            (
                "LINKCRAFTOR",
                "UNIVERSAL COORDINATION FRAMEWORK",
                "PHASE 10.1–10.5 OBSERVABILITY CERTIFICATION",
                "",
                "10.1 Workflow Progress: CERTIFIED + FROZEN",
                "10.2 Workflow Metrics: CERTIFIED + FROZEN",
                "10.3 Stage Metrics: CERTIFIED + FROZEN",
                "10.4 Workflow Evidence: CERTIFIED + FROZEN",
                "10.5 Audit Trail: CERTIFIED + FROZEN",
                "",
                f"10.1 SHA256: {SHA101}",
                f"10.2 SHA256: {SHA102}",
                f"10.3 SHA256: {SHA103}",
                f"10.4 SHA256: {SHA104}",
                f"10.5 SHA256: {SHA105}",
                "",
                f"10.1–10.5 COMPOSITE SHA256: {COMPOSITE}",
                "",
                "Architecture:",
                "- UCF observability is read-only aggregation",
                "- no workflow mutation",
                "- no Runtime mutation",
                "- no Runtime metric/log/telemetry emission",
                "- Runtime observability remains separately owned",
                "- Phase 3 lifecycle history remains canonical transition evidence",
                "- Phase 8 persistence remains canonical durable state",
                "- Phase 9 recovery remains canonical recovery authority",
                "",
                f"Formal checks passed before final immutability: {passed_before_final}",
                "Formal failures: 0",
                "",
                "STATUS: CERTIFIED + FROZEN",
            )
        )
        + "\n",
        encoding="utf-8",
    )


    REPORT_SHA = sha256(
        REPORT
    )


    write_json(
        BATCH_FREEZE,
        {
            "framework":
                "Universal Coordination Framework",

            "scope":
                "10.1 through 10.5",

            "certified":
                True,

            "frozen":
                True,

            "source_sha256":
                source_hashes,

            "freeze_sha256":
                freeze_hashes,

            "composite_sha256":
                COMPOSITE,

            "phase_9_master_sha256":
                sha256(
                    PHASE9_MASTER
                ),

            "report": {
                "path":
                    REPORT.name,

                "sha256":
                    REPORT_SHA,
            },

            "next":
                "10.6 Observability Certification",

            "freeze_created_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),
        },
    )


    BATCH_FREEZE_SHA = sha256(
        BATCH_FREEZE
    )


    # ==============================================================
    # 12 — FINAL IMMUTABILITY
    # ==============================================================

    section(
        "12 — FINAL IMMUTABILITY VERIFICATION"
    )


    for path, expected in EXPECTED.items():

        check(
            f"frozen predecessor unchanged: {path.name}",
            sha256(path)
            == expected,
        )


    coord_after = {}

    for path in coord_root.rglob("*"):

        if (
            path.is_file()
            and OBS_ROOT
            not in path.parents
        ):
            coord_after[
                path.resolve()
            ] = sha256(
                path
            )


    check(
        "existing Coordination inventory unchanged",
        set(
            coord_after
        )
        == set(
            coord_before
        ),
    )


    check(
        "existing Coordination hashes unchanged",
        coord_after
        == coord_before,
    )


    runtime_after = {}

    for path in runtime_root.rglob("*"):

        if path.is_file():
            runtime_after[
                path.resolve()
            ] = sha256(
                path
            )


    check(
        "Runtime inventory unchanged",
        set(
            runtime_after
        )
        == set(
            runtime_before
        ),
    )


    check(
        "Runtime hashes unchanged",
        runtime_after
        == runtime_before,
    )


    purge()


    for module_name, version_name, expected_version in (
        (
            "backend.server.coordination.coordination_observability.workflow_progress",
            "WORKFLOW_PROGRESS_VERSION",
            "workflow_progress_v10.1.0",
        ),
        (
            "backend.server.coordination.coordination_observability.workflow_metrics",
            "WORKFLOW_METRICS_VERSION",
            "workflow_metrics_v10.2.0",
        ),
        (
            "backend.server.coordination.coordination_observability.stage_metrics",
            "STAGE_METRICS_VERSION",
            "stage_metrics_v10.3.0",
        ),
        (
            "backend.server.coordination.coordination_observability.workflow_evidence",
            "WORKFLOW_EVIDENCE_VERSION",
            "workflow_evidence_v10.4.0",
        ),
        (
            "backend.server.coordination.coordination_observability.audit_trail",
            "AUDIT_TRAIL_VERSION",
            "audit_trail_v10.5.0",
        ),
    ):

        module = importlib.import_module(
            module_name
        )

        check(
            f"final import/version exact: {expected_version}",
            getattr(
                module,
                version_name,
            )
            == expected_version,
        )


    # ==============================================================
    # 13 — FINAL STATUS
    # ==============================================================

    section(
        "13 — PHASE 10.1–10.5 FINAL STATUS"
    )


    total = sum(
        1
        for _name, ok
        in checks
        if ok
    )


    print(
        "TOTAL FORMAL CHECKS:",
        total,
        "PASS",
    )

    print()

    print(
        "PHASE 10.1 WORKFLOW PROGRESS: CERTIFIED + FROZEN"
    )

    print(
        "PHASE 10.2 WORKFLOW METRICS: CERTIFIED + FROZEN"
    )

    print(
        "PHASE 10.3 STAGE METRICS: CERTIFIED + FROZEN"
    )

    print(
        "PHASE 10.4 WORKFLOW EVIDENCE: CERTIFIED + FROZEN"
    )

    print(
        "PHASE 10.5 AUDIT TRAIL: CERTIFIED + FROZEN"
    )

    print()

    print(
        "10.1 SOURCE SHA256:",
        SHA101,
    )

    print(
        "10.1 FREEZE SHA256:",
        freeze_hashes["10.1"],
    )

    print(
        "10.2 SOURCE SHA256:",
        SHA102,
    )

    print(
        "10.2 FREEZE SHA256:",
        freeze_hashes["10.2"],
    )

    print(
        "10.3 SOURCE SHA256:",
        SHA103,
    )

    print(
        "10.3 FREEZE SHA256:",
        freeze_hashes["10.3"],
    )

    print(
        "10.4 SOURCE SHA256:",
        SHA104,
    )

    print(
        "10.4 FREEZE SHA256:",
        freeze_hashes["10.4"],
    )

    print(
        "10.5 SOURCE SHA256:",
        SHA105,
    )

    print(
        "10.5 FREEZE SHA256:",
        freeze_hashes["10.5"],
    )

    print()

    print(
        "PHASE 10.1–10.5 COMPOSITE SHA256:",
        COMPOSITE,
    )

    print(
        "10.1–10.5 BATCH FREEZE SHA256:",
        BATCH_FREEZE_SHA,
    )

    print(
        "CERTIFICATION REPORT SHA256:",
        REPORT_SHA,
    )

    print()

    print(
        "PHASE 9 MODIFIED: FALSE"
    )

    print(
        "EXISTING COORDINATION COMPONENTS MODIFIED: FALSE"
    )

    print(
        "UNIVERSAL RUNTIME MODIFIED: FALSE"
    )

    print()

    print(
        "NEXT: PHASE 10.6 — OBSERVABILITY CERTIFICATION"
    )

    print("=" * 120)


except Exception:

    print()
    print("=" * 120)
    print("PHASE 10.1–10.5 BATCH FAILED — ROLLING BACK NEW FILES")
    print("=" * 120)

    for path in created:

        if path.exists():
            path.unlink()

    if (
        init_created
        and INIT.exists()
    ):
        INIT.unlink()

    try:
        if (
            OBS_ROOT.exists()
            and not any(
                OBS_ROOT.iterdir()
            )
        ):
            OBS_ROOT.rmdir()
    except Exception:
        pass

    print(
        "ROLLBACK COMPLETE."
    )

    raise
