from __future__ import annotations

import ast
import dataclasses
import hashlib
import importlib
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

PERSIST = (
    ROOT
    / "backend/server/coordination/workflow_persistence"
)

P81 = PERSIST / "repository.py"
P82 = PERSIST / "stage_state_store.py"
P83 = PERSIST / "checkpointing.py"

P84 = PERSIST / "workflow_pause.py"
P85 = PERSIST / "workflow_resume.py"
P86 = PERSIST / "restart_recovery.py"
P87 = PERSIST / "persistence_certification.py"

F81 = PERSIST / "workflow_store.phase_8_1.freeze.json"
F82 = PERSIST / "stage_state_store.phase_8_2.freeze.json"
F83 = PERSIST / "checkpointing.phase_8_3.freeze.json"

F84 = PERSIST / "workflow_pause.phase_8_4.freeze.json"
F85 = PERSIST / "workflow_resume.phase_8_5.freeze.json"
F86 = PERSIST / "restart_recovery.phase_8_6.freeze.json"
F87 = PERSIST / "persistence_certification.phase_8_7.freeze.json"

REPORT = (
    ROOT
    / "phase_8_persistence_final_certification.txt"
)

PHASE8_MASTER_FREEZE = (
    PERSIST
    / "phase_8_workflow_state_persistence.freeze.json"
)

WORKFLOW_CONTRACT = (
    ROOT
    / "backend/server/coordination/universal_workflows/contract.py"
)

STATE_MACHINE = (
    ROOT
    / "backend/server/coordination/workflow_lifecycle/state_machine.py"
)

TRANSITION_VALIDATION = (
    ROOT
    / "backend/server/coordination/workflow_lifecycle/transition_validation.py"
)

TERMINAL_PROTECTION = (
    ROOT
    / "backend/server/coordination/workflow_lifecycle/terminal_state_protection.py"
)

LIFECYCLE_HISTORY = (
    ROOT
    / "backend/server/coordination/workflow_lifecycle/lifecycle_history.py"
)


EXPECTED = {
    P81:
        "E7A8379FABF9047F150E24DF4B2B9F138F4CE285C1B3D3EC43DD2F1A454C69DB",

    F81:
        "700DF28A15294D2868794CEF7477082658027345185FEA8BD9EC3D7183D20AC7",

    P82:
        "D7EA771B1461C10166697CF1DCA4B9B90B1D0ECEA7573555204B329EF5E32016",

    F82:
        "B0067C4525475B2390869BEC5973339AE2E9DAF3735A3586DDF0D5C960B1B421",

    P83:
        "DB79D0B23BE69387B116EEC470047350F070C5EAC669B97C83E93F6349A19669",

    F83:
        "57CE9CBD368698C27F01E22FE315A301AE8015B8427F1FC42650395031CA163A",

    WORKFLOW_CONTRACT:
        "9094A98D2B9DBD9CCED73514648BF5D4115C5092E547D19446AB0FE18FBE7089",

    STATE_MACHINE:
        "144327A4E9C8989FCF0F4DBD10BCF6D7203F503930D81CB8E24644D86D2BB662",

    TRANSITION_VALIDATION:
        "69A952141E920E63B32B12AF1E9FB79D6296961FED40BCB94F007123BF9BD746",

    TERMINAL_PROTECTION:
        "7632A838D9CEAD7ED95DB0099D08FB20D01B4E2BD25BFF48D68CBEB89065A7B7",

    LIFECYCLE_HISTORY:
        "D89F1D4FBC54307C7B8155E670CDD3C6C8771185DC8AFBE382A87BB34EDA8464",
}


def sha256(
    path: Path,
) -> str:

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def section(
    title: str,
) -> None:

    print()
    print("=" * 120)
    print(title)
    print("=" * 120)


checks = []


def check(
    name: str,
    condition,
) -> None:

    ok = bool(
        condition
    )

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


def write_json(
    path: Path,
    data,
) -> None:

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

    prefixes = (
        "backend.server.coordination.workflow_persistence",
        "backend.server.coordination.workflow_lifecycle",
        "backend.server.coordination.universal_workflows",
    )

    for name in tuple(
        sys.modules
    ):
        if name.startswith(
            prefixes
        ):
            sys.modules.pop(
                name,
                None,
            )

    importlib.invalidate_caches()


section(
    "LINKCRAFTOR — UCF PHASE 8.4–8.7 FINAL PERSISTENCE BATCH"
)


# ==================================================================
# 0 — FROZEN AUTHORITY GUARD
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
    P84,
    P85,
    P86,
    P87,
    F84,
    F85,
    F86,
    F87,
    PHASE8_MASTER_FREEZE,
):

    check(
        f"not already installed: {path.name}",
        not path.exists(),
    )


# Preserve Phase 7 before touching Phase 8.

phase7_root = (
    ROOT
    / "backend/server/coordination/advanced_orchestration"
)

phase7_before = {}

if phase7_root.exists():

    for path in phase7_root.rglob("*"):

        if path.is_file():
            phase7_before[
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
    / f"ucf_phase8_final_{stamp}"
)

backup.mkdir(
    parents=True,
    exist_ok=False,
)


for path in (
    P81,
    P82,
    P83,
    F81,
    F82,
    F83,
):

    shutil.copy2(
        path,
        backup
        / path.name,
    )


print(
    "BACKUP:",
    backup,
)


created = [
    P84,
    P85,
    P86,
    P87,
    F84,
    F85,
    F86,
    F87,
    REPORT,
    PHASE8_MASTER_FREEZE,
]


try:

    # ==============================================================
    # 2 — INSTALL 8.4 PAUSE
    # ==============================================================

    section(
        "2 — INSTALL PHASE 8.4 PAUSE"
    )


    P84.write_text(
r'''"""
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
''',
        encoding="utf-8",
    )


    SHA84 = sha256(
        P84
    )


    print(
        "8.4 SHA256:",
        SHA84,
    )


    # ==============================================================
    # 3 — INSTALL 8.5 RESUME
    # ==============================================================

    section(
        "3 — INSTALL PHASE 8.5 RESUME"
    )


    P85.write_text(
r'''"""
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
''',
        encoding="utf-8",
    )


    SHA85 = sha256(
        P85
    )


    print(
        "8.5 SHA256:",
        SHA85,
    )


    # ==============================================================
    # 4 — INSTALL 8.6 RESTART RECOVERY
    # ==============================================================

    section(
        "4 — INSTALL PHASE 8.6 RESTART RECOVERY"
    )


    P86.write_text(
r'''"""
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
''',
        encoding="utf-8",
    )


    SHA86 = sha256(
        P86
    )


    print(
        "8.6 SHA256:",
        SHA86,
    )


    # ==============================================================
    # 5 — STATIC BOUNDARY VERIFICATION
    # ==============================================================

    section(
        "5 — STATIC BOUNDARY VERIFICATION"
    )


    forbidden_runtime_symbols = (
        "submit_universal_job",
        "run_one_universal_runtime_job_v1",
        "enqueue",
        "requeue",
        "claim_job",
        "worker_loop",
        "execute_handler",
    )


    for phase, path in (
        (
            "8.4",
            P84,
        ),
        (
            "8.5",
            P85,
        ),
        (
            "8.6",
            P86,
        ),
    ):

        source = path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(
            source
        )

        imported_modules = set()
        executable_symbols = set()

        for node in ast.walk(
            tree
        ):

            if isinstance(
                node,
                ast.Import,
            ):

                for alias in node.names:
                    imported_modules.add(
                        alias.name
                    )

            elif isinstance(
                node,
                ast.ImportFrom,
            ):

                if node.module:
                    imported_modules.add(
                        node.module
                    )

                for alias in node.names:
                    executable_symbols.add(
                        alias.name
                    )

            elif isinstance(
                node,
                ast.Call,
            ):

                if isinstance(
                    node.func,
                    ast.Name,
                ):
                    executable_symbols.add(
                        node.func.id
                    )

                elif isinstance(
                    node.func,
                    ast.Attribute,
                ):
                    executable_symbols.add(
                        node.func.attr
                    )

            elif isinstance(
                node,
                ast.Name,
            ):

                executable_symbols.add(
                    node.id
                )

            elif isinstance(
                node,
                ast.Attribute,
            ):

                executable_symbols.add(
                    node.attr
                )

        check(
            f"{phase} has no Universal Runtime import",
            not any(
                module == "backend.server.runtime"
                or module.startswith(
                    "backend.server.runtime."
                )
                for module
                in imported_modules
            ),
        )

        for term in forbidden_runtime_symbols:

            check(
                f"{phase} Runtime executable authority absent: {term}",
                term
                not in executable_symbols,
            )


    check(
        "8.4 uses transition validation",
        "require_valid_workflow_transition"
        in P84.read_text(
            encoding="utf-8"
        ),
    )

    check(
        "8.4 uses terminal protection",
        "require_terminal_state_mutation_allowed"
        in P84.read_text(
            encoding="utf-8"
        ),
    )

    check(
        "8.4 creates checkpoint",
        "create_workflow_checkpoint"
        in P84.read_text(
            encoding="utf-8"
        ),
    )

    check(
        "8.4 uses optimistic concurrency",
        "expected_current_fingerprint"
        in P84.read_text(
            encoding="utf-8"
        ),
    )

    check(
        "8.5 restricts resume targets",
        "READY or RUNNING"
        in P85.read_text(
            encoding="utf-8"
        ),
    )

    check(
        "8.6 enters RECOVERING",
        "UniversalWorkflowStatus.RECOVERING"
        in P86.read_text(
            encoding="utf-8"
        ),
    )

    check(
        "8.6 explicitly does not perform Runtime recovery",
        "runtime_recovery_executed"
        in P86.read_text(
            encoding="utf-8"
        ),
    )


    # ==============================================================
    # 6 — IMPORT / CONTRACT VERIFICATION
    # ==============================================================

    section(
        "6 — IMPORT / CONTRACT VERIFICATION"
    )


    purge()


    workflow_mod = importlib.import_module(
        "backend.server.coordination.universal_workflows.contract"
    )

    history_mod = importlib.import_module(
        "backend.server.coordination.workflow_lifecycle.lifecycle_history"
    )

    repo_mod = importlib.import_module(
        "backend.server.coordination.workflow_persistence.repository"
    )

    stage_store_mod = importlib.import_module(
        "backend.server.coordination.workflow_persistence.stage_state_store"
    )

    checkpoint_mod = importlib.import_module(
        "backend.server.coordination.workflow_persistence.checkpointing"
    )

    pause_mod = importlib.import_module(
        "backend.server.coordination.workflow_persistence.workflow_pause"
    )

    resume_mod = importlib.import_module(
        "backend.server.coordination.workflow_persistence.workflow_resume"
    )

    recovery_mod = importlib.import_module(
        "backend.server.coordination.workflow_persistence.restart_recovery"
    )


    check(
        "8.4 version exact",
        pause_mod.WORKFLOW_PAUSE_VERSION
        == "workflow_pause_v8.4.0",
    )

    check(
        "8.5 version exact",
        resume_mod.WORKFLOW_RESUME_VERSION
        == "workflow_resume_v8.5.0",
    )

    check(
        "8.6 version exact",
        recovery_mod.RESTART_RECOVERY_VERSION
        == "restart_recovery_v8.6.0",
    )


    # ==============================================================
    # 7 — REAL END-TO-END PERSISTENCE SMOKE
    # ==============================================================

    section(
        "7 — REAL END-TO-END PERSISTENCE SMOKE"
    )


    UniversalWorkflow = (
        workflow_mod.UniversalWorkflow
    )

    UniversalWorkflowStatus = (
        workflow_mod.UniversalWorkflowStatus
    )

    WorkflowRepository = (
        repo_mod.WorkflowRepository
    )

    WorkflowCheckpointRepository = (
        checkpoint_mod.WorkflowCheckpointRepository
    )


    with tempfile.TemporaryDirectory() as td:

        base = Path(
            td
        )

        workflow_repo = WorkflowRepository(
            root=
                base
                / "workflows"
        )

        checkpoint_repo = WorkflowCheckpointRepository(
            root=
                base
                / "checkpoints"
        )


        t0 = "2026-11-08T00:00:00+00:00"
        t1 = "2026-11-08T00:00:01+00:00"
        t2 = "2026-11-08T00:00:02+00:00"
        t3 = "2026-11-08T00:00:03+00:00"
        t4 = "2026-11-08T00:00:04+00:00"


        workflow = UniversalWorkflow(
            workflow_id=
                "wf_phase8_final_probe",

            workflow_type=
                "phase8_probe",

            workflow_version=
                "1.0.0",

            workspace_id=
                "workspace_phase8_probe",

            coordinator_id=
                "coordinator_phase8_probe",

            coordinator_version=
                "1.0.0",

            correlation_id=
                "correlation_phase8_probe",

            parent_workflow_id=
                None,

            root_workflow_id=
                "wf_phase8_final_probe",

            status=
                UniversalWorkflowStatus.READY,

            input_reference=
                None,

            context={},

            metadata={
                "probe":
                    True,
            },

            current_stage=
                None,

            completed_stages=(),

            pending_stages=(
                "stage_probe",
            ),

            failed_stages=(),

            skipped_stages=(),

            result_reference=
                None,

            artifact_references=(),

            idempotency_key=
                "phase8-final-probe",

            created_at=
                t0,

            started_at=
                None,

            updated_at=
                t1,

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


        validation = workflow.validate()

        check(
            "initial READY probe validates",
            validation.is_valid,
        )


        workflow_repo.save_workflow(
            workflow
        )


        ready_entry = (
            history_mod.create_lifecycle_history_entry(
                event_id=
                    "phase8_probe_created_ready",

                workflow_id=
                    workflow.workflow_id,

                correlation_id=
                    workflow.correlation_id,

                from_state=
                    UniversalWorkflowStatus.CREATED,

                to_state=
                    UniversalWorkflowStatus.READY,

                occurred_at=
                    t1,

                reason=
                    "phase8 certification probe",

                source=
                    "phase8_certification",

                actor_id=
                    None,

                metadata={},
            )
        )


        initial_history = (
            ready_entry,
        )


        pause_result = pause_mod.pause_workflow(
            workflow_repository=
                workflow_repo,

            checkpoint_repository=
                checkpoint_repo,

            workflow_id=
                workflow.workflow_id,

            stage_states=(),

            lifecycle_history=
                initial_history,

            reason=
                "certification pause",

            occurred_at=
                t2,
        )


        check(
            "8.4 transitioned READY -> PAUSED",
            pause_result.workflow.status
            is UniversalWorkflowStatus.PAUSED,
        )


        check(
            "8.4 persisted PAUSED workflow",
            workflow_repo.load_workflow(
                workflow.workflow_id
            ).status
            is UniversalWorkflowStatus.PAUSED,
        )


        check(
            "8.4 created durable checkpoint",
            checkpoint_repo.load(
                pause_result.checkpoint.checkpoint_id
            ).checkpoint_id
            == pause_result.checkpoint.checkpoint_id,
        )


        check(
            "8.4 checkpoint contains lifecycle history",
            len(
                pause_result.checkpoint.lifecycle_history
            )
            == 2,
        )


        # Restart recovery is tested from the persisted PAUSED checkpoint.
        recovery_result = (
            recovery_mod.prepare_restart_recovery(
                workflow_repository=
                    workflow_repo,

                checkpoint_repository=
                    checkpoint_repo,

                checkpoint_id=
                    pause_result.checkpoint.checkpoint_id,

                reason=
                    "restart recovery certification",

                occurred_at=
                    t3,
            )
        )


        check(
            "8.6 restored checkpoint source as PAUSED",
            recovery_result.source_workflow.status
            is UniversalWorkflowStatus.PAUSED,
        )


        check(
            "8.6 transitioned PAUSED -> RECOVERING",
            recovery_result.recovering_workflow.status
            is UniversalWorkflowStatus.RECOVERING,
        )


        check(
            "8.6 persisted RECOVERING workflow",
            workflow_repo.load_workflow(
                workflow.workflow_id
            ).status
            is UniversalWorkflowStatus.RECOVERING,
        )


        check(
            "8.6 performed no Runtime recovery",
            recovery_result.runtime_recovery_executed
            is False,
        )


        # Separate PAUSED workflow proves normal 8.5 resume because
        # restart recovery intentionally moved the first probe to RECOVERING.

        workflow2 = dataclasses.replace(
            workflow,

            workflow_id=
                "wf_phase8_resume_probe",

            root_workflow_id=
                "wf_phase8_resume_probe",

            correlation_id=
                "correlation_phase8_resume_probe",

            idempotency_key=
                "phase8-resume-probe",
        )


        check(
            "resume probe READY workflow validates",
            workflow2.validate().is_valid,
        )


        workflow_repo.save_workflow(
            workflow2
        )


        ready_entry2 = (
            history_mod.create_lifecycle_history_entry(
                event_id=
                    "phase8_resume_probe_created_ready",

                workflow_id=
                    workflow2.workflow_id,

                correlation_id=
                    workflow2.correlation_id,

                from_state=
                    UniversalWorkflowStatus.CREATED,

                to_state=
                    UniversalWorkflowStatus.READY,

                occurred_at=
                    t1,

                reason=
                    "phase8 resume certification",

                source=
                    "phase8_certification",

                actor_id=
                    None,

                metadata={},
            )
        )


        pause2 = pause_mod.pause_workflow(
            workflow_repository=
                workflow_repo,

            checkpoint_repository=
                checkpoint_repo,

            workflow_id=
                workflow2.workflow_id,

            lifecycle_history=(
                ready_entry2,
            ),

            reason=
                "resume probe pause",

            occurred_at=
                t2,
        )


        resume_result = resume_mod.resume_workflow(
            workflow_repository=
                workflow_repo,

            workflow_id=
                workflow2.workflow_id,

            target_state=
                UniversalWorkflowStatus.READY,

            lifecycle_history=
                pause2.history,

            reason=
                "certification resume",

            occurred_at=
                t4,
        )


        check(
            "8.5 transitioned PAUSED -> READY",
            resume_result.workflow.status
            is UniversalWorkflowStatus.READY,
        )


        check(
            "8.5 persisted READY workflow",
            workflow_repo.load_workflow(
                workflow2.workflow_id
            ).status
            is UniversalWorkflowStatus.READY,
        )


        history_validation = (
            history_mod.validate_lifecycle_history(
                resume_result.history
            )
        )


        check(
            "pause/resume lifecycle history valid",
            history_validation.is_valid,
        )


    # ==============================================================
    # 8 — FREEZE 8.4
    # ==============================================================

    section(
        "8 — FREEZE PHASE 8.4"
    )


    write_json(
        F84,
        {
            "framework":
                "Universal Coordination Framework",

            "phase":
                "8.4",

            "component":
                "Pause",

            "certified":
                True,

            "frozen":
                True,

            "production": {
                "path":
                    "backend/server/coordination/"
                    "workflow_persistence/workflow_pause.py",

                "version":
                    "workflow_pause_v8.4.0",

                "schema_version":
                    "workflow_pause_schema_v1",

                "sha256":
                    SHA84,
            },

            "authorities": {
                "workflow_store_sha256":
                    sha256(
                        P81
                    ),

                "checkpointing_sha256":
                    sha256(
                        P83
                    ),

                "state_machine_sha256":
                    sha256(
                        STATE_MACHINE
                    ),

                "transition_validation_sha256":
                    sha256(
                        TRANSITION_VALIDATION
                    ),

                "terminal_protection_sha256":
                    sha256(
                        TERMINAL_PROTECTION
                    ),
            },

            "semantics": {
                "allowed_source_states": [
                    "READY",
                    "RUNNING",
                    "WAITING",
                ],

                "target_state":
                    "PAUSED",

                "runtime_worker_pause":
                    False,

                "runtime_execution_pause":
                    False,
            },

            "freeze_created_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "next":
                "8.5 Resume",
        },
    )


    SHA_F84 = sha256(
        F84
    )


    # ==============================================================
    # 9 — FREEZE 8.5
    # ==============================================================

    section(
        "9 — FREEZE PHASE 8.5"
    )


    write_json(
        F85,
        {
            "framework":
                "Universal Coordination Framework",

            "phase":
                "8.5",

            "component":
                "Resume",

            "certified":
                True,

            "frozen":
                True,

            "production": {
                "path":
                    "backend/server/coordination/"
                    "workflow_persistence/workflow_resume.py",

                "version":
                    "workflow_resume_v8.5.0",

                "schema_version":
                    "workflow_resume_schema_v1",

                "sha256":
                    SHA85,
            },

            "authorities": {
                "workflow_store_sha256":
                    sha256(
                        P81
                    ),

                "state_machine_sha256":
                    sha256(
                        STATE_MACHINE
                    ),

                "transition_validation_sha256":
                    sha256(
                        TRANSITION_VALIDATION
                    ),

                "terminal_protection_sha256":
                    sha256(
                        TERMINAL_PROTECTION
                    ),
            },

            "semantics": {
                "source_state":
                    "PAUSED",

                "allowed_target_states": [
                    "READY",
                    "RUNNING",
                ],

                "runtime_worker_resume":
                    False,

                "runtime_execution_resume":
                    False,
            },

            "freeze_created_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "next":
                "8.6 Restart Recovery",
        },
    )


    SHA_F85 = sha256(
        F85
    )


    # ==============================================================
    # 10 — FREEZE 8.6
    # ==============================================================

    section(
        "10 — FREEZE PHASE 8.6"
    )


    write_json(
        F86,
        {
            "framework":
                "Universal Coordination Framework",

            "phase":
                "8.6",

            "component":
                "Restart Recovery",

            "certified":
                True,

            "frozen":
                True,

            "production": {
                "path":
                    "backend/server/coordination/"
                    "workflow_persistence/restart_recovery.py",

                "version":
                    "restart_recovery_v8.6.0",

                "schema_version":
                    "restart_recovery_schema_v1",

                "sha256":
                    SHA86,
            },

            "authorities": {
                "workflow_store_sha256":
                    sha256(
                        P81
                    ),

                "checkpointing_sha256":
                    sha256(
                        P83
                    ),

                "state_machine_sha256":
                    sha256(
                        STATE_MACHINE
                    ),

                "transition_validation_sha256":
                    sha256(
                        TRANSITION_VALIDATION
                    ),
            },

            "semantics": {
                "recovery_target_state":
                    "RECOVERING",

                "checkpoint_restore":
                    True,

                "workflow_state_persisted":
                    True,

                "runtime_service_restart":
                    False,

                "runtime_job_requeue":
                    False,

                "runtime_worker_reactivation":
                    False,

                "runtime_recovery_execution":
                    False,
            },

            "freeze_created_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "next":
                "8.7 Persistence Certification",
        },
    )


    SHA_F86 = sha256(
        F86
    )


    # ==============================================================
    # 11 — INSTALL PHASE 8.7 CERTIFICATION AUTHORITY
    # ==============================================================

    section(
        "11 — INSTALL PHASE 8.7 PERSISTENCE CERTIFICATION"
    )


    expected_source_hashes = {
        "8.1":
            sha256(
                P81
            ),

        "8.2":
            sha256(
                P82
            ),

        "8.3":
            sha256(
                P83
            ),

        "8.4":
            SHA84,

        "8.5":
            SHA85,

        "8.6":
            SHA86,
    }


    expected_freeze_hashes = {
        "8.1":
            sha256(
                F81
            ),

        "8.2":
            sha256(
                F82
            ),

        "8.3":
            sha256(
                F83
            ),

        "8.4":
            SHA_F84,

        "8.5":
            SHA_F85,

        "8.6":
            SHA_F86,
    }


    source_items = [
        (
            phase,
            value,
        )
        for phase, value
        in sorted(
            expected_source_hashes.items()
        )
    ]


    canonical_composite = "\n".join(
        f"{phase}:{value}"
        for phase, value
        in source_items
    )


    PHASE8_COMPOSITE = hashlib.sha256(
        canonical_composite.encode(
            "utf-8"
        )
    ).hexdigest().upper()


    source87 = f'''"""
LinkCraftor — Universal Coordination Framework

Phase 8.7 — Workflow State Persistence Certification.

Certifies frozen Phase 8.1 through 8.6 source and freeze authorities.
"""

from __future__ import annotations

import hashlib

from dataclasses import dataclass
from pathlib import Path
from typing import Final, Tuple


PERSISTENCE_CERTIFICATION_VERSION: Final[str] = (
    "persistence_certification_v8.7.0"
)

PERSISTENCE_CERTIFICATION_SCHEMA_VERSION: Final[str] = (
    "persistence_certification_schema_v1"
)


_EXPECTED_SOURCE_SHA256: Final[tuple[tuple[str, str, str], ...]] = (
    ("8.1", "repository.py", "{expected_source_hashes["8.1"]}"),
    ("8.2", "stage_state_store.py", "{expected_source_hashes["8.2"]}"),
    ("8.3", "checkpointing.py", "{expected_source_hashes["8.3"]}"),
    ("8.4", "workflow_pause.py", "{expected_source_hashes["8.4"]}"),
    ("8.5", "workflow_resume.py", "{expected_source_hashes["8.5"]}"),
    ("8.6", "restart_recovery.py", "{expected_source_hashes["8.6"]}"),
)


_EXPECTED_FREEZE_SHA256: Final[tuple[tuple[str, str, str], ...]] = (
    ("8.1", "workflow_store.phase_8_1.freeze.json", "{expected_freeze_hashes["8.1"]}"),
    ("8.2", "stage_state_store.phase_8_2.freeze.json", "{expected_freeze_hashes["8.2"]}"),
    ("8.3", "checkpointing.phase_8_3.freeze.json", "{expected_freeze_hashes["8.3"]}"),
    ("8.4", "workflow_pause.phase_8_4.freeze.json", "{expected_freeze_hashes["8.4"]}"),
    ("8.5", "workflow_resume.phase_8_5.freeze.json", "{expected_freeze_hashes["8.5"]}"),
    ("8.6", "restart_recovery.phase_8_6.freeze.json", "{expected_freeze_hashes["8.6"]}"),
)


EXPECTED_PHASE_8_COMPOSITE: Final[str] = (
    "{PHASE8_COMPOSITE}"
)


@dataclass(frozen=True, slots=True)
class PersistenceCertificationResult:

    is_certified: bool

    source_sha256: Tuple[
        Tuple[str, str],
        ...
    ]

    freeze_sha256: Tuple[
        Tuple[str, str],
        ...
    ]

    composite_fingerprint: str

    violations: Tuple[str, ...]

    certification_version: str = (
        PERSISTENCE_CERTIFICATION_VERSION
    )

    schema_version: str = (
        PERSISTENCE_CERTIFICATION_SCHEMA_VERSION
    )


def _root() -> Path:

    return Path(
        __file__
    ).resolve().parent


def _sha256(
    path: Path,
) -> str:

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def actual_source_hashes() -> Tuple[
    Tuple[str, str],
    ...
]:

    root = _root()

    return tuple(
        (
            phase,
            _sha256(
                root
                / filename
            ),
        )
        for phase, filename, _expected
        in _EXPECTED_SOURCE_SHA256
    )


def actual_freeze_hashes() -> Tuple[
    Tuple[str, str],
    ...
]:

    root = _root()

    return tuple(
        (
            phase,
            _sha256(
                root
                / filename
            ),
        )
        for phase, filename, _expected
        in _EXPECTED_FREEZE_SHA256
    )


def phase_8_composite(
    source_hashes: Tuple[
        Tuple[str, str],
        ...
    ],
) -> str:

    canonical = "\\n".join(
        f"{{phase}}:{{value}}"
        for phase, value
        in source_hashes
    )

    return hashlib.sha256(
        canonical.encode(
            "utf-8"
        )
    ).hexdigest().upper()


def evaluate_persistence_certification() -> PersistenceCertificationResult:

    violations = []

    actual_sources = (
        actual_source_hashes()
    )

    actual_freezes = (
        actual_freeze_hashes()
    )

    expected_sources = {{
        phase:
            expected
        for phase, _filename, expected
        in _EXPECTED_SOURCE_SHA256
    }}

    expected_freezes = {{
        phase:
            expected
        for phase, _filename, expected
        in _EXPECTED_FREEZE_SHA256
    }}

    for phase, actual in actual_sources:

        if (
            actual
            != expected_sources[
                phase
            ]
        ):
            violations.append(
                f"Phase {{phase}} production SHA256 mismatch"
            )

    for phase, actual in actual_freezes:

        if (
            actual
            != expected_freezes[
                phase
            ]
        ):
            violations.append(
                f"Phase {{phase}} freeze SHA256 mismatch"
            )

    composite = phase_8_composite(
        actual_sources
    )

    if (
        composite
        != EXPECTED_PHASE_8_COMPOSITE
    ):
        violations.append(
            "Phase 8 composite fingerprint mismatch"
        )

    canonical_violations = tuple(
        violations
    )

    return PersistenceCertificationResult(
        is_certified=
            not canonical_violations,

        source_sha256=
            actual_sources,

        freeze_sha256=
            actual_freezes,

        composite_fingerprint=
            composite,

        violations=
            canonical_violations,
    )


__all__ = [
    "PERSISTENCE_CERTIFICATION_VERSION",
    "PERSISTENCE_CERTIFICATION_SCHEMA_VERSION",
    "EXPECTED_PHASE_8_COMPOSITE",
    "PersistenceCertificationResult",
    "actual_source_hashes",
    "actual_freeze_hashes",
    "phase_8_composite",
    "evaluate_persistence_certification",
]
'''


    P87.write_text(
        source87,
        encoding="utf-8",
    )


    SHA87 = sha256(
        P87
    )


    print(
        "8.7 SHA256:",
        SHA87,
    )


    # ==============================================================
    # 12 — EXECUTE 8.7 CERTIFICATION
    # ==============================================================

    section(
        "12 — EXECUTE PHASE 8.7 CERTIFICATION"
    )


    purge()


    cert_mod = importlib.import_module(
        "backend.server.coordination.workflow_persistence.persistence_certification"
    )


    certification = (
        cert_mod.evaluate_persistence_certification()
    )


    check(
        "8.7 certification passes",
        certification.is_certified,
    )


    check(
        "8.7 has zero violations",
        certification.violations
        == (),
    )


    check(
        "Phase 8 composite exact",
        certification.composite_fingerprint
        == PHASE8_COMPOSITE,
    )


    for phase, actual in certification.source_sha256:

        check(
            f"8.7 source lineage exact: {phase}",
            actual
            == expected_source_hashes[
                phase
            ],
        )


    for phase, actual in certification.freeze_sha256:

        check(
            f"8.7 freeze lineage exact: {phase}",
            actual
            == expected_freeze_hashes[
                phase
            ],
        )


    # ==============================================================
    # 13 — FINAL REPORT
    # ==============================================================

    section(
        "13 — FINAL PHASE 8 CERTIFICATION REPORT"
    )


    passed_before_report = sum(
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
                "PHASE 8 — WORKFLOW STATE PERSISTENCE FINAL CERTIFICATION",
                "",
                "8.1 Workflow Store: CERTIFIED + FROZEN",
                "8.2 Stage State Store: CERTIFIED + FROZEN",
                "8.3 Checkpointing: CERTIFIED + FROZEN",
                "8.4 Pause: CERTIFIED + FROZEN",
                "8.5 Resume: CERTIFIED + FROZEN",
                "8.6 Restart Recovery: CERTIFIED + FROZEN",
                "8.7 Persistence Certification: CERTIFIED",
                "",
                f"8.1 SHA256: {sha256(P81)}",
                f"8.2 SHA256: {sha256(P82)}",
                f"8.3 SHA256: {sha256(P83)}",
                f"8.4 SHA256: {SHA84}",
                f"8.5 SHA256: {SHA85}",
                f"8.6 SHA256: {SHA86}",
                f"8.7 SHA256: {SHA87}",
                "",
                f"PHASE 8 COMPOSITE SHA256: {PHASE8_COMPOSITE}",
                "",
                "Architecture:",
                "- UCF owns canonical workflow persistence",
                "- UCF owns coordination stage-state persistence",
                "- UCF owns coordination checkpoints",
                "- UCF Pause persists PAUSED workflow state",
                "- UCF Resume persists READY/RUNNING state",
                "- UCF Restart Recovery restores checkpoint and enters RECOVERING",
                "- Runtime workers/jobs/queues/retries/recovery remain separate",
                "- no second Runtime system created",
                "",
                f"FORMAL CHECKS BEFORE FINAL FREEZE: {passed_before_report}",
                "FORMAL FAILURES: 0",
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


    # ==============================================================
    # 14 — FREEZE 8.7
    # ==============================================================

    section(
        "14 — FREEZE PHASE 8.7"
    )


    write_json(
        F87,
        {
            "framework":
                "Universal Coordination Framework",

            "phase":
                "8.7",

            "component":
                "Persistence Certification",

            "certified":
                True,

            "frozen":
                True,

            "production": {
                "path":
                    "backend/server/coordination/"
                    "workflow_persistence/persistence_certification.py",

                "version":
                    "persistence_certification_v8.7.0",

                "schema_version":
                    "persistence_certification_schema_v1",

                "sha256":
                    SHA87,
            },

            "phase_8_composite": {
                "algorithm":
                    "SHA256",

                "scope":
                    "frozen production sources 8.1 through 8.6",

                "sha256":
                    PHASE8_COMPOSITE,
            },

            "predecessor_sources":
                expected_source_hashes,

            "predecessor_freezes":
                expected_freeze_hashes,

            "final_certification_report": {
                "path":
                    REPORT.name,

                "sha256":
                    REPORT_SHA,
            },

            "freeze_created_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "next":
                "9.0 Coordination Recovery",
        },
    )


    SHA_F87 = sha256(
        F87
    )


    # ==============================================================
    # 15 — MASTER PHASE 8 FREEZE
    # ==============================================================

    section(
        "15 — MASTER PHASE 8 FREEZE"
    )


    write_json(
        PHASE8_MASTER_FREEZE,
        {
            "framework":
                "Universal Coordination Framework",

            "phase":
                "8",

            "component":
                "Workflow State Persistence",

            "certified":
                True,

            "frozen":
                True,

            "components": {
                "8.1": {
                    "name":
                        "Workflow Store",

                    "source_sha256":
                        sha256(
                            P81
                        ),

                    "freeze_sha256":
                        sha256(
                            F81
                        ),
                },

                "8.2": {
                    "name":
                        "Stage State Store",

                    "source_sha256":
                        sha256(
                            P82
                        ),

                    "freeze_sha256":
                        sha256(
                            F82
                        ),
                },

                "8.3": {
                    "name":
                        "Checkpointing",

                    "source_sha256":
                        sha256(
                            P83
                        ),

                    "freeze_sha256":
                        sha256(
                            F83
                        ),
                },

                "8.4": {
                    "name":
                        "Pause",

                    "source_sha256":
                        SHA84,

                    "freeze_sha256":
                        SHA_F84,
                },

                "8.5": {
                    "name":
                        "Resume",

                    "source_sha256":
                        SHA85,

                    "freeze_sha256":
                        SHA_F85,
                },

                "8.6": {
                    "name":
                        "Restart Recovery",

                    "source_sha256":
                        SHA86,

                    "freeze_sha256":
                        SHA_F86,
                },

                "8.7": {
                    "name":
                        "Persistence Certification",

                    "source_sha256":
                        SHA87,

                    "freeze_sha256":
                        SHA_F87,
                },
            },

            "phase_8_composite_sha256":
                PHASE8_COMPOSITE,

            "runtime_boundary": {
                "runtime_jobs_owned":
                    False,

                "runtime_queues_owned":
                    False,

                "runtime_workers_owned":
                    False,

                "runtime_retry_owned":
                    False,

                "runtime_recovery_owned":
                    False,

                "runtime_resume_execution_owned":
                    False,
            },

            "certification_report": {
                "path":
                    REPORT.name,

                "sha256":
                    REPORT_SHA,
            },

            "backup":
                str(
                    backup.relative_to(
                        ROOT
                    )
                ),

            "freeze_created_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "next":
                "9.0 Coordination Recovery",
        },
    )


    MASTER_SHA = sha256(
        PHASE8_MASTER_FREEZE
    )


    # ==============================================================
    # 16 — POST-FREEZE IMMUTABILITY
    # ==============================================================

    section(
        "16 — POST-FREEZE IMMUTABILITY"
    )


    for path, expected in EXPECTED.items():

        check(
            f"upstream authority unchanged: {path.name}",
            sha256(path)
            == expected,
        )


    phase7_after = {}

    if phase7_root.exists():

        for path in phase7_root.rglob("*"):

            if path.is_file():
                phase7_after[
                    path.resolve()
                ] = sha256(
                    path
                )


    check(
        "Phase 7 inventory unchanged",
        set(
            phase7_after
        )
        == set(
            phase7_before
        ),
    )


    check(
        "Phase 7 hashes unchanged",
        phase7_after
        == phase7_before,
    )


    # Re-run final 8.7 source certification after all freezes.
    purge()


    final_cert_mod = importlib.import_module(
        "backend.server.coordination.workflow_persistence.persistence_certification"
    )


    final_result = (
        final_cert_mod.evaluate_persistence_certification()
    )


    check(
        "final 8.7 certification still passes",
        final_result.is_certified,
    )


    check(
        "final Phase 8 composite stable",
        final_result.composite_fingerprint
        == PHASE8_COMPOSITE,
    )


    # ==============================================================
    # 17 — FINAL STATUS
    # ==============================================================

    section(
        "17 — PHASE 8 FINAL STATUS"
    )


    total_passed = sum(
        1
        for _name, ok
        in checks
        if ok
    )


    print(
        "TOTAL FORMAL CHECKS:",
        total_passed,
        "PASS",
    )

    print()

    print(
        "PHASE 8.1 WORKFLOW STORE: CERTIFIED + FROZEN"
    )

    print(
        "PHASE 8.2 STAGE STATE STORE: CERTIFIED + FROZEN"
    )

    print(
        "PHASE 8.3 CHECKPOINTING: CERTIFIED + FROZEN"
    )

    print(
        "PHASE 8.4 PAUSE: CERTIFIED + FROZEN"
    )

    print(
        "PHASE 8.5 RESUME: CERTIFIED + FROZEN"
    )

    print(
        "PHASE 8.6 RESTART RECOVERY: CERTIFIED + FROZEN"
    )

    print(
        "PHASE 8.7 PERSISTENCE CERTIFICATION: CERTIFIED + FROZEN"
    )

    print()

    print(
        "8.4 SHA256:",
        SHA84,
    )

    print(
        "8.4 FREEZE SHA256:",
        SHA_F84,
    )

    print(
        "8.5 SHA256:",
        SHA85,
    )

    print(
        "8.5 FREEZE SHA256:",
        SHA_F85,
    )

    print(
        "8.6 SHA256:",
        SHA86,
    )

    print(
        "8.6 FREEZE SHA256:",
        SHA_F86,
    )

    print(
        "8.7 SHA256:",
        SHA87,
    )

    print(
        "8.7 FREEZE SHA256:",
        SHA_F87,
    )

    print()

    print(
        "PHASE 8 COMPOSITE SHA256:",
        PHASE8_COMPOSITE,
    )

    print(
        "PHASE 8 MASTER FREEZE SHA256:",
        MASTER_SHA,
    )

    print(
        "FINAL CERTIFICATION REPORT SHA256:",
        REPORT_SHA,
    )

    print()

    print(
        "PHASE 7 MODIFIED: FALSE"
    )

    print(
        "PHASE 8.1–8.3 MODIFIED: FALSE"
    )

    print(
        "RUNTIME INFRASTRUCTURE MODIFIED: FALSE"
    )

    print()

    print(
        "NEXT: PHASE 9.0 — COORDINATION RECOVERY"
    )

    print("=" * 120)


except Exception:

    print()
    print("=" * 120)
    print("PHASE 8 FINAL BATCH FAILED — ROLLING BACK NEW 8.4–8.7 FILES")
    print("=" * 120)

    for path in created:

        if path.exists():
            path.unlink()

    print(
        "ROLLBACK COMPLETE."
    )

    raise
