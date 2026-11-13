from __future__ import annotations

import ast
import dataclasses
import hashlib
import importlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

RECOVERY_ROOT = (
    ROOT
    / "backend/server/coordination/coordination_recovery"
)

RECOVERY_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)

P91 = RECOVERY_ROOT / "failure_policy.py"
F91 = RECOVERY_ROOT / "failure_policy.phase_9_1.freeze.json"

P92 = RECOVERY_ROOT / "terminal_failure_handling.py"
P93 = RECOVERY_ROOT / "workflow_recovery.py"
P94 = RECOVERY_ROOT / "compensation.py"
P95 = RECOVERY_ROOT / "manual_intervention.py"
P96 = RECOVERY_ROOT / "recovery_loop_protection.py"

F92 = RECOVERY_ROOT / "terminal_failure_handling.phase_9_2.freeze.json"
F93 = RECOVERY_ROOT / "workflow_recovery.phase_9_3.freeze.json"
F94 = RECOVERY_ROOT / "compensation.phase_9_4.freeze.json"
F95 = RECOVERY_ROOT / "manual_intervention.phase_9_5.freeze.json"
F96 = RECOVERY_ROOT / "recovery_loop_protection.phase_9_6.freeze.json"

REPORT = (
    ROOT
    / "ucf_phase_9_2_to_9_6_certification_report.txt"
)

BATCH_FREEZE = (
    RECOVERY_ROOT
    / "coordination_recovery.phase_9_2_to_9_6.freeze.json"
)

PHASE8_MASTER = (
    ROOT
    / "backend/server/coordination/workflow_persistence/"
    "phase_8_workflow_state_persistence.freeze.json"
)

PROCESSED_RESULT = (
    ROOT
    / "backend/server/coordination/stage_handoff/"
    "stage_result_processor.py"
)

WORKFLOW_STORE = (
    ROOT
    / "backend/server/coordination/workflow_persistence/"
    "repository.py"
)

STATE_MACHINE = (
    ROOT
    / "backend/server/coordination/workflow_lifecycle/"
    "state_machine.py"
)

TRANSITION_VALIDATION = (
    ROOT
    / "backend/server/coordination/workflow_lifecycle/"
    "transition_validation.py"
)

TERMINAL_PROTECTION = (
    ROOT
    / "backend/server/coordination/workflow_lifecycle/"
    "terminal_state_protection.py"
)

LIFECYCLE_HISTORY = (
    ROOT
    / "backend/server/coordination/workflow_lifecycle/"
    "lifecycle_history.py"
)


EXPECTED = {
    PHASE8_MASTER:
        "C50FC64AB7CEB3443B5C15CEF9AEAB406644152434B181559E4F40E05F8DF6C3",

    P91:
        "23FE473EA7EF314238FA8F1DC4256EE329FED6CC59ED31E6724D1173E74688C0",

    F91:
        "D77CE26006DA43749073D2C67A3104FBF5F337F219A43B6EF5410E59450AAD6C",

    PROCESSED_RESULT:
        "6028FED380B0E4E970F7DB30179EE2ED48C81CE00313314FF8449DA9C6A6480E",

    WORKFLOW_STORE:
        "E7A8379FABF9047F150E24DF4B2B9F138F4CE285C1B3D3EC43DD2F1A454C69DB",

    STATE_MACHINE:
        "144327A4E9C8989FCF0F4DBD10BCF6D7203F503930D81CB8E24644D86D2BB662",

    TRANSITION_VALIDATION:
        "69A952141E920E63B32B12AF1E9FB79D6296961FED40BCB94F007123BF9BD746",

    TERMINAL_PROTECTION:
        "7632A838D9CEAD7ED95DB0099D08FB20D01B4E2BD25BFF48D68CBEB89065A7B7",

    LIFECYCLE_HISTORY:
        "D89F1D4FBC54307C7B8155E670CDD3C6C8771185DC8AFBE382A87BB34EDA8464",
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
        "backend.server.coordination.coordination_recovery"
    )

    for name in tuple(
        sys.modules
    ):
        if name.startswith(prefix):
            sys.modules.pop(
                name,
                None,
            )

    importlib.invalidate_caches()


section(
    "LINKCRAFTOR — UCF PHASE 9.2–9.6 COORDINATION RECOVERY BATCH"
)


# ==================================================================
# 0 — AUTHORITY GUARD
# ==================================================================

section(
    "0 — FROZEN AUTHORITY GUARD"
)


for path, expected in EXPECTED.items():

    check(
        f"exact frozen authority: {path.name}",
        path.exists()
        and sha256(path)
        == expected,
    )


for path in (
    P92,
    P93,
    P94,
    P95,
    P96,
    F92,
    F93,
    F94,
    F95,
    F96,
    BATCH_FREEZE,
):

    check(
        f"not already installed: {path.name}",
        not path.exists(),
    )


# Protect all existing Coordination and Runtime files.

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
        and RECOVERY_ROOT
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
    / f"ucf_phase9_2_to_9_6_{stamp}"
)

backup.mkdir(
    parents=True,
    exist_ok=False,
)

shutil.copy2(
    P91,
    backup
    / P91.name,
)

shutil.copy2(
    F91,
    backup
    / F91.name,
)


print(
    "BACKUP:",
    backup,
)


created = [
    P92,
    P93,
    P94,
    P95,
    P96,
    F92,
    F93,
    F94,
    F95,
    F96,
    REPORT,
    BATCH_FREEZE,
]


try:

    # ==============================================================
    # 2 — PHASE 9.2
    # ==============================================================

    section(
        "2 — INSTALL 9.2 TERMINAL RUNTIME FAILURE HANDLING"
    )


    P92.write_text(
r'''"""
LinkCraftor — Universal Coordination Framework

Phase 9.2 — Terminal Runtime Failure Handling.

Consumes one terminal FAILED ProcessedStageResult and frozen Phase 9.1
Failure Policy.

This component:
- validates terminal failure evidence,
- invokes Phase 9.1 policy classification,
- preserves workflow/stage/job identity,
- returns immutable coordination recovery evidence.

It does NOT:
- re-read Runtime jobs,
- create a second Runtime failure intake path,
- retry/requeue Runtime work,
- mutate workflow lifecycle,
- persist workflow state,
- perform compensation,
- perform manual intervention.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Optional, Tuple

from backend.server.coordination.stage_handoff.stage_result_processor import (
    ProcessedStageResult,
    StageResultDisposition,
)

from backend.server.coordination.coordination_recovery.failure_policy import (
    WorkflowFailurePolicyDecision,
    evaluate_failure_policy,
)

from backend.server.runtime.reliability.failure_classification_containment import (
    FailureContainmentDecision,
)

from backend.server.runtime.reliability.retry_governance import (
    RetryGovernanceDecision,
)

from backend.server.runtime.reliability.recovery_coordination import (
    RecoveryCoordinationDecision,
)


TERMINAL_FAILURE_HANDLING_VERSION = (
    "terminal_failure_handling_v9.2.0"
)

TERMINAL_FAILURE_HANDLING_SCHEMA_VERSION = (
    "terminal_failure_handling_schema_v1"
)


class TerminalFailureHandlingError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class TerminalFailureHandlingResult:

    result_id: str
    workflow_id: str
    correlation_id: str
    workspace_id: str

    stage_id: str
    stage_version: str

    job_id: str
    job_type: str

    failure_code: str
    failure_message: str

    failure_details: Mapping[
        str,
        Any,
    ]

    policy_decision: WorkflowFailurePolicyDecision

    source_processor_version: str

    handling_version: str = (
        TERMINAL_FAILURE_HANDLING_VERSION
    )

    schema_version: str = (
        TERMINAL_FAILURE_HANDLING_SCHEMA_VERSION
    )

    def to_dict(
        self,
    ) -> Mapping[str, Any]:

        return MappingProxyType({
            "result_id":
                self.result_id,

            "workflow_id":
                self.workflow_id,

            "correlation_id":
                self.correlation_id,

            "workspace_id":
                self.workspace_id,

            "stage_id":
                self.stage_id,

            "stage_version":
                self.stage_version,

            "job_id":
                self.job_id,

            "job_type":
                self.job_type,

            "failure_code":
                self.failure_code,

            "failure_message":
                self.failure_message,

            "failure_details":
                dict(
                    self.failure_details
                ),

            "policy_decision":
                dict(
                    self.policy_decision.to_dict()
                ),

            "source_processor_version":
                self.source_processor_version,

            "handling_version":
                self.handling_version,

            "schema_version":
                self.schema_version,
        })


def handle_terminal_failure(
    source: ProcessedStageResult,
    *,
    containment_decision: Optional[
        FailureContainmentDecision
    ] = None,
    retry_decision: Optional[
        RetryGovernanceDecision
    ] = None,
    recovery_decision: Optional[
        RecoveryCoordinationDecision
    ] = None,
) -> TerminalFailureHandlingResult:

    if not isinstance(
        source,
        ProcessedStageResult,
    ):
        raise TerminalFailureHandlingError(
            "source must be ProcessedStageResult"
        )

    if not source.terminal:
        raise TerminalFailureHandlingError(
            "source must be terminal"
        )

    if (
        source.disposition
        is not StageResultDisposition.FAILED
    ):
        raise TerminalFailureHandlingError(
            "source must have FAILED disposition"
        )

    decision = evaluate_failure_policy(
        source,
        containment_decision=
            containment_decision,

        retry_decision=
            retry_decision,

        recovery_decision=
            recovery_decision,
    )

    if (
        decision.workflow_id
        != source.workflow_id
        or decision.correlation_id
        != source.correlation_id
        or decision.stage_id
        != source.stage_id
        or decision.job_id
        != source.job_id
    ):
        raise TerminalFailureHandlingError(
            "Phase 9.1 decision identity mismatch"
        )

    return TerminalFailureHandlingResult(
        result_id=
            source.result_id,

        workflow_id=
            source.workflow_id,

        correlation_id=
            source.correlation_id,

        workspace_id=
            source.workspace_id,

        stage_id=
            source.stage_id,

        stage_version=
            source.stage_version,

        job_id=
            source.job_id,

        job_type=
            source.job_type,

        failure_code=
            source.failure_code,

        failure_message=
            source.failure_message,

        failure_details=
            source.failure_details,

        policy_decision=
            decision,

        source_processor_version=
            source.processor_version,
    )


__all__ = [
    "TERMINAL_FAILURE_HANDLING_VERSION",
    "TERMINAL_FAILURE_HANDLING_SCHEMA_VERSION",
    "TerminalFailureHandlingError",
    "TerminalFailureHandlingResult",
    "handle_terminal_failure",
]
''',
        encoding="utf-8",
    )


    SHA92 = sha256(
        P92
    )


    # ==============================================================
    # 3 — PHASE 9.3
    # ==============================================================

    section(
        "3 — INSTALL 9.3 WORKFLOW RECOVERY"
    )


    P93.write_text(
r'''"""
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
''',
        encoding="utf-8",
    )


    SHA93 = sha256(
        P93
    )


    # ==============================================================
    # 4 — PHASE 9.4
    # ==============================================================

    section(
        "4 — INSTALL 9.4 COMPENSATION"
    )


    P94.write_text(
r'''"""
LinkCraftor — Universal Coordination Framework

Phase 9.4 — Compensation.

Creates immutable compensation instructions when frozen Failure Policy
returns COMPENSATE.

This component does NOT execute compensating business logic.
"""

from __future__ import annotations

import hashlib

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Tuple

from backend.server.coordination.coordination_recovery.failure_policy import (
    WorkflowFailurePolicyOutcome,
)

from backend.server.coordination.coordination_recovery.terminal_failure_handling import (
    TerminalFailureHandlingResult,
)


COMPENSATION_VERSION = (
    "compensation_v9.4.0"
)

COMPENSATION_SCHEMA_VERSION = (
    "compensation_schema_v1"
)


class CompensationError(
    ValueError
):
    pass


class CompensationDisposition(
    str,
    Enum,
):
    REQUIRED = "REQUIRED"


@dataclass(
    frozen=True,
    slots=True,
)
class CompensationInstruction:

    compensation_id: str

    workflow_id: str
    correlation_id: str
    workspace_id: str

    stage_id: str
    job_id: str

    failure_code: str

    disposition: CompensationDisposition

    reason_codes: Tuple[
        str,
        ...
    ]

    business_compensation_executed: bool = False

    compensation_version: str = (
        COMPENSATION_VERSION
    )

    schema_version: str = (
        COMPENSATION_SCHEMA_VERSION
    )

    def to_dict(
        self,
    ) -> Mapping[str, Any]:

        return MappingProxyType({
            "compensation_id":
                self.compensation_id,

            "workflow_id":
                self.workflow_id,

            "correlation_id":
                self.correlation_id,

            "workspace_id":
                self.workspace_id,

            "stage_id":
                self.stage_id,

            "job_id":
                self.job_id,

            "failure_code":
                self.failure_code,

            "disposition":
                self.disposition.value,

            "reason_codes":
                self.reason_codes,

            "business_compensation_executed":
                self.business_compensation_executed,

            "compensation_version":
                self.compensation_version,

            "schema_version":
                self.schema_version,
        })


def create_compensation_instruction(
    terminal_failure: TerminalFailureHandlingResult,
) -> CompensationInstruction:

    if not isinstance(
        terminal_failure,
        TerminalFailureHandlingResult,
    ):
        raise CompensationError(
            "terminal_failure must be TerminalFailureHandlingResult"
        )

    if (
        terminal_failure.policy_decision.outcome
        is not WorkflowFailurePolicyOutcome.COMPENSATE
    ):
        raise CompensationError(
            "Failure Policy does not require COMPENSATE"
        )

    compensation_id = hashlib.sha256(
        (
            "ucf_compensation_v1"
            + "\0"
            + terminal_failure.workflow_id
            + "\0"
            + terminal_failure.stage_id
            + "\0"
            + terminal_failure.job_id
            + "\0"
            + terminal_failure.failure_code
        ).encode(
            "utf-8"
        )
    ).hexdigest().upper()

    return CompensationInstruction(
        compensation_id=
            compensation_id,

        workflow_id=
            terminal_failure.workflow_id,

        correlation_id=
            terminal_failure.correlation_id,

        workspace_id=
            terminal_failure.workspace_id,

        stage_id=
            terminal_failure.stage_id,

        job_id=
            terminal_failure.job_id,

        failure_code=
            terminal_failure.failure_code,

        disposition=
            CompensationDisposition.REQUIRED,

        reason_codes=
            terminal_failure.policy_decision.reason_codes,

        business_compensation_executed=
            False,
    )


__all__ = [
    "COMPENSATION_VERSION",
    "COMPENSATION_SCHEMA_VERSION",
    "CompensationError",
    "CompensationDisposition",
    "CompensationInstruction",
    "create_compensation_instruction",
]
''',
        encoding="utf-8",
    )


    SHA94 = sha256(
        P94
    )


    # ==============================================================
    # 5 — PHASE 9.5
    # ==============================================================

    section(
        "5 — INSTALL 9.5 MANUAL INTERVENTION"
    )


    P95.write_text(
r'''"""
LinkCraftor — Universal Coordination Framework

Phase 9.5 — Manual Intervention.

Creates immutable operator-intervention evidence when Failure Policy
returns MANUAL_INTERVENTION.

This component does NOT send alerts, invoke staff tooling, mutate workflow
state or execute recovery.
"""

from __future__ import annotations

import hashlib

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Tuple

from backend.server.coordination.coordination_recovery.failure_policy import (
    WorkflowFailurePolicyOutcome,
)

from backend.server.coordination.coordination_recovery.terminal_failure_handling import (
    TerminalFailureHandlingResult,
)


MANUAL_INTERVENTION_VERSION = (
    "manual_intervention_v9.5.0"
)

MANUAL_INTERVENTION_SCHEMA_VERSION = (
    "manual_intervention_schema_v1"
)


class ManualInterventionError(
    ValueError
):
    pass


class ManualInterventionStatus(
    str,
    Enum,
):
    REQUIRED = "REQUIRED"


@dataclass(
    frozen=True,
    slots=True,
)
class ManualInterventionRequest:

    intervention_id: str

    workflow_id: str
    correlation_id: str
    workspace_id: str

    stage_id: str
    job_id: str

    failure_code: str
    failure_message: str

    reason_codes: Tuple[
        str,
        ...
    ]

    status: ManualInterventionStatus

    operator_action_executed: bool = False
    notification_emitted: bool = False

    intervention_version: str = (
        MANUAL_INTERVENTION_VERSION
    )

    schema_version: str = (
        MANUAL_INTERVENTION_SCHEMA_VERSION
    )

    def to_dict(
        self,
    ) -> Mapping[str, Any]:

        return MappingProxyType({
            "intervention_id":
                self.intervention_id,

            "workflow_id":
                self.workflow_id,

            "correlation_id":
                self.correlation_id,

            "workspace_id":
                self.workspace_id,

            "stage_id":
                self.stage_id,

            "job_id":
                self.job_id,

            "failure_code":
                self.failure_code,

            "failure_message":
                self.failure_message,

            "reason_codes":
                self.reason_codes,

            "status":
                self.status.value,

            "operator_action_executed":
                self.operator_action_executed,

            "notification_emitted":
                self.notification_emitted,

            "intervention_version":
                self.intervention_version,

            "schema_version":
                self.schema_version,
        })


def create_manual_intervention_request(
    terminal_failure: TerminalFailureHandlingResult,
) -> ManualInterventionRequest:

    if not isinstance(
        terminal_failure,
        TerminalFailureHandlingResult,
    ):
        raise ManualInterventionError(
            "terminal_failure must be TerminalFailureHandlingResult"
        )

    if (
        terminal_failure.policy_decision.outcome
        is not WorkflowFailurePolicyOutcome.MANUAL_INTERVENTION
    ):
        raise ManualInterventionError(
            "Failure Policy does not require MANUAL_INTERVENTION"
        )

    intervention_id = hashlib.sha256(
        (
            "ucf_manual_intervention_v1"
            + "\0"
            + terminal_failure.workflow_id
            + "\0"
            + terminal_failure.stage_id
            + "\0"
            + terminal_failure.job_id
            + "\0"
            + terminal_failure.failure_code
        ).encode(
            "utf-8"
        )
    ).hexdigest().upper()

    return ManualInterventionRequest(
        intervention_id=
            intervention_id,

        workflow_id=
            terminal_failure.workflow_id,

        correlation_id=
            terminal_failure.correlation_id,

        workspace_id=
            terminal_failure.workspace_id,

        stage_id=
            terminal_failure.stage_id,

        job_id=
            terminal_failure.job_id,

        failure_code=
            terminal_failure.failure_code,

        failure_message=
            terminal_failure.failure_message,

        reason_codes=
            terminal_failure.policy_decision.reason_codes,

        status=
            ManualInterventionStatus.REQUIRED,

        operator_action_executed=
            False,

        notification_emitted=
            False,
    )


__all__ = [
    "MANUAL_INTERVENTION_VERSION",
    "MANUAL_INTERVENTION_SCHEMA_VERSION",
    "ManualInterventionError",
    "ManualInterventionStatus",
    "ManualInterventionRequest",
    "create_manual_intervention_request",
]
''',
        encoding="utf-8",
    )


    SHA95 = sha256(
        P95
    )


    # ==============================================================
    # 6 — PHASE 9.6
    # ==============================================================

    section(
        "6 — INSTALL 9.6 RECOVERY LOOP PROTECTION"
    )


    P96.write_text(
r'''"""
LinkCraftor — Universal Coordination Framework

Phase 9.6 — Recovery Loop Protection.

Pure workflow-level recovery-loop governance.

It determines whether another UCF recovery cycle is permitted.

It does NOT:
- retry/requeue Runtime jobs,
- mutate workflow lifecycle,
- persist attempts,
- execute compensation,
- invoke manual intervention.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Tuple


RECOVERY_LOOP_PROTECTION_VERSION = (
    "recovery_loop_protection_v9.6.0"
)

RECOVERY_LOOP_PROTECTION_SCHEMA_VERSION = (
    "recovery_loop_protection_schema_v1"
)


class RecoveryLoopProtectionError(
    ValueError
):
    pass


class RecoveryLoopDisposition(
    str,
    Enum,
):
    ALLOW_RECOVERY = "ALLOW_RECOVERY"
    MANUAL_INTERVENTION = "MANUAL_INTERVENTION"
    FAIL_WORKFLOW = "FAIL_WORKFLOW"


@dataclass(
    frozen=True,
    slots=True,
)
class RecoveryLoopEvidence:

    workflow_id: str
    stage_id: str
    failure_code: str

    total_recovery_attempts: int
    same_failure_recovery_attempts: int

    max_total_recovery_attempts: int = 3
    max_same_failure_attempts: int = 2

    prior_recovery_succeeded: bool = False


@dataclass(
    frozen=True,
    slots=True,
)
class RecoveryLoopDecision:

    disposition: RecoveryLoopDisposition

    next_recovery_attempt: int | None

    reason_codes: Tuple[
        str,
        ...
    ]

    loop_detected: bool

    protection_version: str = (
        RECOVERY_LOOP_PROTECTION_VERSION
    )

    schema_version: str = (
        RECOVERY_LOOP_PROTECTION_SCHEMA_VERSION
    )

    def to_dict(
        self,
    ) -> Mapping[str, Any]:

        return MappingProxyType({
            "disposition":
                self.disposition.value,

            "next_recovery_attempt":
                self.next_recovery_attempt,

            "reason_codes":
                self.reason_codes,

            "loop_detected":
                self.loop_detected,

            "protection_version":
                self.protection_version,

            "schema_version":
                self.schema_version,
        })


def evaluate_recovery_loop(
    evidence: RecoveryLoopEvidence,
) -> RecoveryLoopDecision:

    if not isinstance(
        evidence,
        RecoveryLoopEvidence,
    ):
        raise RecoveryLoopProtectionError(
            "evidence must be RecoveryLoopEvidence"
        )

    if evidence.total_recovery_attempts < 0:
        raise RecoveryLoopProtectionError(
            "total_recovery_attempts cannot be negative"
        )

    if evidence.same_failure_recovery_attempts < 0:
        raise RecoveryLoopProtectionError(
            "same_failure_recovery_attempts cannot be negative"
        )

    if evidence.max_total_recovery_attempts < 1:
        raise RecoveryLoopProtectionError(
            "max_total_recovery_attempts must be >= 1"
        )

    if evidence.max_same_failure_attempts < 1:
        raise RecoveryLoopProtectionError(
            "max_same_failure_attempts must be >= 1"
        )

    if evidence.prior_recovery_succeeded:
        return RecoveryLoopDecision(
            disposition=
                RecoveryLoopDisposition.ALLOW_RECOVERY,

            next_recovery_attempt=
                evidence.total_recovery_attempts
                + 1,

            reason_codes=(
                "prior_recovery_succeeded",
            ),

            loop_detected=
                False,
        )

    if (
        evidence.same_failure_recovery_attempts
        >= evidence.max_same_failure_attempts
    ):
        return RecoveryLoopDecision(
            disposition=
                RecoveryLoopDisposition.MANUAL_INTERVENTION,

            next_recovery_attempt=
                None,

            reason_codes=(
                "same_failure_recovery_loop_detected",
            ),

            loop_detected=
                True,
        )

    if (
        evidence.total_recovery_attempts
        >= evidence.max_total_recovery_attempts
    ):
        return RecoveryLoopDecision(
            disposition=
                RecoveryLoopDisposition.FAIL_WORKFLOW,

            next_recovery_attempt=
                None,

            reason_codes=(
                "total_recovery_attempt_limit_reached",
            ),

            loop_detected=
                True,
        )

    return RecoveryLoopDecision(
        disposition=
            RecoveryLoopDisposition.ALLOW_RECOVERY,

        next_recovery_attempt=
            evidence.total_recovery_attempts
            + 1,

        reason_codes=(
            "recovery_attempt_within_limits",
        ),

        loop_detected=
            False,
    )


__all__ = [
    "RECOVERY_LOOP_PROTECTION_VERSION",
    "RECOVERY_LOOP_PROTECTION_SCHEMA_VERSION",
    "RecoveryLoopProtectionError",
    "RecoveryLoopDisposition",
    "RecoveryLoopEvidence",
    "RecoveryLoopDecision",
    "evaluate_recovery_loop",
]
''',
        encoding="utf-8",
    )


    SHA96 = sha256(
        P96
    )


    # ==============================================================
    # 7 — STATIC ARCHITECTURE VERIFICATION
    # ==============================================================

    section(
        "7 — STATIC ARCHITECTURE VERIFICATION"
    )


    forbidden_runtime_actions = (
        "submit_universal_job",
        "enqueue",
        "requeue",
        "claim_job",
        "run_one_universal_runtime_job_v1",
        "execute_handler",
        "worker_loop",
    )


    for phase, path in (
        (
            "9.2",
            P92,
        ),
        (
            "9.3",
            P93,
        ),
        (
            "9.4",
            P94,
        ),
        (
            "9.5",
            P95,
        ),
        (
            "9.6",
            P96,
        ),
    ):

        tree = ast.parse(
            path.read_text(
                encoding="utf-8"
            )
        )

        calls = set()

        for node in ast.walk(
            tree
        ):

            if isinstance(
                node,
                ast.Call,
            ):

                if isinstance(
                    node.func,
                    ast.Name,
                ):
                    calls.add(
                        node.func.id
                    )

                elif isinstance(
                    node.func,
                    ast.Attribute,
                ):
                    calls.add(
                        node.func.attr
                    )

        for symbol in forbidden_runtime_actions:

            check(
                f"{phase} Runtime execution authority absent: {symbol}",
                symbol
                not in calls,
            )


    check(
        "9.3 is the only new module using save_workflow",
        "save_workflow"
        in P93.read_text(
            encoding="utf-8"
        )
        and "save_workflow"
        not in P92.read_text(
            encoding="utf-8"
        )
        and "save_workflow"
        not in P94.read_text(
            encoding="utf-8"
        )
        and "save_workflow"
        not in P95.read_text(
            encoding="utf-8"
        )
        and "save_workflow"
        not in P96.read_text(
            encoding="utf-8"
        ),
    )


    # ==============================================================
    # 8 — IMPORT / CONTRACT VERIFICATION
    # ==============================================================

    section(
        "8 — IMPORT / CONTRACT VERIFICATION"
    )


    purge()


    m92 = importlib.import_module(
        "backend.server.coordination.coordination_recovery."
        "terminal_failure_handling"
    )

    m93 = importlib.import_module(
        "backend.server.coordination.coordination_recovery."
        "workflow_recovery"
    )

    m94 = importlib.import_module(
        "backend.server.coordination.coordination_recovery."
        "compensation"
    )

    m95 = importlib.import_module(
        "backend.server.coordination.coordination_recovery."
        "manual_intervention"
    )

    m96 = importlib.import_module(
        "backend.server.coordination.coordination_recovery."
        "recovery_loop_protection"
    )


    check(
        "9.2 version exact",
        m92.TERMINAL_FAILURE_HANDLING_VERSION
        == "terminal_failure_handling_v9.2.0",
    )

    check(
        "9.3 version exact",
        m93.WORKFLOW_RECOVERY_VERSION
        == "workflow_recovery_v9.3.0",
    )

    check(
        "9.4 version exact",
        m94.COMPENSATION_VERSION
        == "compensation_v9.4.0",
    )

    check(
        "9.5 version exact",
        m95.MANUAL_INTERVENTION_VERSION
        == "manual_intervention_v9.5.0",
    )

    check(
        "9.6 version exact",
        m96.RECOVERY_LOOP_PROTECTION_VERSION
        == "recovery_loop_protection_v9.6.0",
    )


    # ==============================================================
    # 9 — FUNCTIONAL TEST FIXTURES
    # ==============================================================

    section(
        "9 — FUNCTIONAL VERIFICATION"
    )


    from backend.server.coordination.stage_handoff.stage_result_processor import (
        ProcessedStageResult,
        StageResultDisposition,
    )

    from backend.server.coordination.universal_stages.contract import (
        StageExecutionTarget,
    )

    from backend.server.coordination.coordination_recovery.failure_policy import (
        WorkflowFailurePolicyOutcome,
    )

    from backend.server.runtime.reliability.recovery_coordination import (
        RecoveryCoordinationDecision,
        RecoveryRoute,
    )


    def failed_source(
        *,
        failure_details=None,
        metadata=None,
    ):

        return ProcessedStageResult(
            result_id=
                "result-92",

            workflow_id=
                "workflow-92",

            correlation_id=
                "correlation-92",

            stage_id=
                "stage-92",

            stage_version=
                "1.0.0",

            pipeline_id=
                "pipeline-92",

            workflow_type=
                "recovery-test",

            workspace_id=
                "workspace-92",

            execution_target=
                StageExecutionTarget.UNIVERSAL_RUNTIME,

            job_id=
                "job-92",

            job_type=
                "test-job",

            disposition=
                StageResultDisposition.FAILED,

            normal_handoff_allowed=
                False,

            prerequisite_satisfied=
                False,

            output={},

            result_reference=
                "result://92",

            artifact_references=(),

            started_at=
                "2026-11-08T00:00:00+00:00",

            finished_at=
                "2026-11-08T00:00:01+00:00",

            failure_code=
                "TEST_FAILURE",

            failure_message=
                "terminal test failure",

            failure_details=
                failure_details
                or {},

            metadata=
                metadata
                or {},

            workflow_contract_version=
                "universal_workflow_contract_v1.1.0",

            stage_reference_contract_version=
                "universal_stage_reference_v1.3.0",

            source_result_contract_version=
                "universal_stage_result_v1.4.0",
        )


    runtime_recovery = RecoveryCoordinationDecision(
        primary_route=
            RecoveryRoute.EXECUTION_RECOVERY,

        secondary_routes=(),

        reason_codes=(
            "execution_recovery",
        ),

        source_reference=
            "runtime-92",
    )


    handled_recover = m92.handle_terminal_failure(
        failed_source(),
        recovery_decision=
            runtime_recovery,
    )


    check(
        "9.2 maps terminal failure into frozen 9.1 RECOVER policy",
        handled_recover.policy_decision.outcome
        is WorkflowFailurePolicyOutcome.RECOVER,
    )


    check(
        "9.2 preserves workflow/stage/job identity",
        handled_recover.workflow_id
        == "workflow-92"
        and handled_recover.stage_id
        == "stage-92"
        and handled_recover.job_id
        == "job-92",
    )


    handled_compensation = (
        m92.handle_terminal_failure(
            failed_source(
                failure_details={
                    "compensation_required":
                        True,
                }
            )
        )
    )


    compensation = (
        m94.create_compensation_instruction(
            handled_compensation
        )
    )


    check(
        "9.4 compensation instruction created",
        compensation.disposition.value
        == "REQUIRED",
    )


    check(
        "9.4 does not execute business compensation",
        compensation.business_compensation_executed
        is False,
    )


    handled_manual = (
        m92.handle_terminal_failure(
            failed_source(
                failure_details={
                    "manual_intervention_required":
                        True,
                }
            )
        )
    )


    manual = (
        m95.create_manual_intervention_request(
            handled_manual
        )
    )


    check(
        "9.5 manual intervention request created",
        manual.status.value
        == "REQUIRED",
    )


    check(
        "9.5 performs no operator action",
        manual.operator_action_executed
        is False,
    )


    check(
        "9.5 emits no notification",
        manual.notification_emitted
        is False,
    )


    loop_allow = m96.evaluate_recovery_loop(
        m96.RecoveryLoopEvidence(
            workflow_id=
                "workflow-92",

            stage_id=
                "stage-92",

            failure_code=
                "TEST_FAILURE",

            total_recovery_attempts=
                0,

            same_failure_recovery_attempts=
                0,
        )
    )


    check(
        "9.6 permits first recovery attempt",
        loop_allow.disposition.value
        == "ALLOW_RECOVERY"
        and loop_allow.next_recovery_attempt
        == 1,
    )


    loop_same_failure = (
        m96.evaluate_recovery_loop(
            m96.RecoveryLoopEvidence(
                workflow_id=
                    "workflow-92",

                stage_id=
                    "stage-92",

                failure_code=
                    "TEST_FAILURE",

                total_recovery_attempts=
                    2,

                same_failure_recovery_attempts=
                    2,
            )
        )
    )


    check(
        "9.6 detects repeated same-failure loop",
        loop_same_failure.disposition.value
        == "MANUAL_INTERVENTION"
        and loop_same_failure.loop_detected,
    )


    loop_total = (
        m96.evaluate_recovery_loop(
            m96.RecoveryLoopEvidence(
                workflow_id=
                    "workflow-92",

                stage_id=
                    "different-stage",

                failure_code=
                    "DIFFERENT_FAILURE",

                total_recovery_attempts=
                    3,

                same_failure_recovery_attempts=
                    0,
            )
        )
    )


    check(
        "9.6 enforces total workflow recovery ceiling",
        loop_total.disposition.value
        == "FAIL_WORKFLOW"
        and loop_total.loop_detected,
    )


    # ==============================================================
    # 10 — 9.3 REAL PERSISTENCE/LIFECYCLE TEST
    # ==============================================================

    section(
        "10 — PHASE 9.3 REAL WORKFLOW RECOVERY TEST"
    )


    import tempfile

    from backend.server.coordination.universal_workflows.contract import (
        UniversalWorkflow,
        UniversalWorkflowStatus,
    )

    from backend.server.coordination.workflow_persistence.repository import (
        WorkflowRepository,
    )

    from backend.server.coordination.workflow_lifecycle.lifecycle_history import (
        create_lifecycle_history_entry,
    )


    with tempfile.TemporaryDirectory() as td:

        repo = WorkflowRepository(
            root=
                Path(td)
                / "workflows"
        )


        workflow = UniversalWorkflow(
            workflow_id=
                "workflow-92",

            workflow_type=
                "recovery-test",

            workflow_version=
                "1.0.0",

            workspace_id=
                "workspace-92",

            coordinator_id=
                "coordinator-92",

            coordinator_version=
                "1.0.0",

            correlation_id=
                "correlation-92",

            parent_workflow_id=
                None,

            root_workflow_id=
                "workflow-92",

            status=
                UniversalWorkflowStatus.RUNNING,

            input_reference=
                None,

            context={},

            metadata={},

            current_stage=
                "stage-92",

            completed_stages=(),

            pending_stages=(
                "stage-92",
            ),

            failed_stages=(),

            skipped_stages=(),

            result_reference=
                None,

            artifact_references=(),

            idempotency_key=
                "workflow-92-idempotency",

            created_at=
                "2026-11-08T00:00:00+00:00",

            started_at=
                "2026-11-08T00:00:01+00:00",

            updated_at=
                "2026-11-08T00:00:02+00:00",

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
            "9.3 test workflow validates",
            workflow.validate().is_valid,
        )


        repo.save_workflow(
            workflow
        )


        recovery = m93.begin_workflow_recovery(
            workflow_repository=
                repo,

            terminal_failure=
                handled_recover,

            lifecycle_history=(),

            occurred_at=
                "2026-11-08T00:00:03+00:00",
        )


        check(
            "9.3 transitions RUNNING -> RECOVERING",
            recovery.workflow.status
            is UniversalWorkflowStatus.RECOVERING,
        )


        check(
            "9.3 persists RECOVERING state",
            repo.load_workflow(
                "workflow-92"
            ).status
            is UniversalWorkflowStatus.RECOVERING,
        )


        check(
            "9.3 creates lifecycle recovery evidence",
            recovery.recovery_entry.to_state
            is UniversalWorkflowStatus.RECOVERING,
        )


        check(
            "9.3 performs no Runtime recovery",
            recovery.runtime_recovery_executed
            is False,
        )


    # ==============================================================
    # 11 — FREEZE 9.2–9.6
    # ==============================================================

    section(
        "11 — CERTIFICATION + FREEZE 9.2–9.6"
    )


    source_hashes = {
        "9.1":
            sha256(
                P91
            ),

        "9.2":
            SHA92,

        "9.3":
            SHA93,

        "9.4":
            SHA94,

        "9.5":
            SHA95,

        "9.6":
            SHA96,
    }


    freeze_specs = (
        (
            F92,
            "9.2",
            "Terminal Runtime Failure Handling",
            P92,
            "terminal_failure_handling_v9.2.0",
            "terminal_failure_handling_schema_v1",
        ),
        (
            F93,
            "9.3",
            "Workflow Recovery",
            P93,
            "workflow_recovery_v9.3.0",
            "workflow_recovery_schema_v1",
        ),
        (
            F94,
            "9.4",
            "Compensation",
            P94,
            "compensation_v9.4.0",
            "compensation_schema_v1",
        ),
        (
            F95,
            "9.5",
            "Manual Intervention",
            P95,
            "manual_intervention_v9.5.0",
            "manual_intervention_schema_v1",
        ),
        (
            F96,
            "9.6",
            "Recovery Loop Protection",
            P96,
            "recovery_loop_protection_v9.6.0",
            "recovery_loop_protection_schema_v1",
        ),
    )


    freeze_hashes = {}


    for (
        freeze_path,
        phase,
        component,
        source_path,
        version,
        schema_version,
    ) in freeze_specs:

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
                        schema_version,

                    "sha256":
                        sha256(
                            source_path
                        ),
                },

                "authorities": {
                    "phase_9_1_source_sha256":
                        sha256(
                            P91
                        ),

                    "phase_9_1_freeze_sha256":
                        sha256(
                            F91
                        ),

                    "phase_8_master_freeze_sha256":
                        sha256(
                            PHASE8_MASTER
                        ),

                    "processed_stage_result_sha256":
                        sha256(
                            PROCESSED_RESULT
                        ),
                },

                "runtime_boundary": {
                    "retry_execution":
                        False,

                    "requeue":
                        False,

                    "worker_recovery":
                        False,

                    "queue_recovery":
                        False,

                    "runtime_execution_recovery":
                        False,
                },

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
    # 12 — BATCH CERTIFICATION
    # ==============================================================

    section(
        "12 — BATCH CERTIFICATION"
    )


    canonical = "\n".join(
        f"{phase}:{source_hashes[phase]}"
        for phase
        in (
            "9.1",
            "9.2",
            "9.3",
            "9.4",
            "9.5",
            "9.6",
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
                "PHASE 9.2–9.6 COORDINATION RECOVERY CERTIFICATION",
                "",
                "9.1 Failure Policy: FROZEN PREDECESSOR",
                "9.2 Terminal Runtime Failure Handling: CERTIFIED + FROZEN",
                "9.3 Workflow Recovery: CERTIFIED + FROZEN",
                "9.4 Compensation: CERTIFIED + FROZEN",
                "9.5 Manual Intervention: CERTIFIED + FROZEN",
                "9.6 Recovery Loop Protection: CERTIFIED + FROZEN",
                "",
                f"9.2 SHA256: {SHA92}",
                f"9.3 SHA256: {SHA93}",
                f"9.4 SHA256: {SHA94}",
                f"9.5 SHA256: {SHA95}",
                f"9.6 SHA256: {SHA96}",
                "",
                f"Composite 9.1–9.6 SHA256: {COMPOSITE}",
                "",
                "Architecture boundaries:",
                "- Runtime terminal failure intake remains Phase 5.5",
                "- Phase 6.1 remains processed-result authority",
                "- Phase 9.1 remains workflow failure-policy authority",
                "- Phase 9.2 creates terminal recovery evidence",
                "- Phase 9.3 alone performs UCF lifecycle mutation into RECOVERING",
                "- Phase 9.4 creates compensation instruction only",
                "- Phase 9.5 creates manual-intervention evidence only",
                "- Phase 9.6 governs recovery-loop ceilings only",
                "- no Runtime retry/requeue/worker/queue mechanics created",
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
                "9.2 through 9.6",

            "certified":
                True,

            "frozen":
                True,

            "source_sha256":
                source_hashes,

            "freeze_sha256":
                freeze_hashes,

            "composite_9_1_to_9_6_sha256":
                COMPOSITE,

            "report": {
                "path":
                    REPORT.name,

                "sha256":
                    REPORT_SHA,
            },

            "phase_8_master_sha256":
                sha256(
                    PHASE8_MASTER
                ),

            "phase_9_1_freeze_sha256":
                sha256(
                    F91
                ),

            "next":
                "9.7 Recovery Certification",

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
    # 13 — FINAL IMMUTABILITY
    # ==============================================================

    section(
        "13 — FINAL IMMUTABILITY VERIFICATION"
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
            and RECOVERY_ROOT
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
            "backend.server.coordination.coordination_recovery."
            "terminal_failure_handling",

            "TERMINAL_FAILURE_HANDLING_VERSION",

            "terminal_failure_handling_v9.2.0",
        ),
        (
            "backend.server.coordination.coordination_recovery."
            "workflow_recovery",

            "WORKFLOW_RECOVERY_VERSION",

            "workflow_recovery_v9.3.0",
        ),
        (
            "backend.server.coordination.coordination_recovery."
            "compensation",

            "COMPENSATION_VERSION",

            "compensation_v9.4.0",
        ),
        (
            "backend.server.coordination.coordination_recovery."
            "manual_intervention",

            "MANUAL_INTERVENTION_VERSION",

            "manual_intervention_v9.5.0",
        ),
        (
            "backend.server.coordination.coordination_recovery."
            "recovery_loop_protection",

            "RECOVERY_LOOP_PROTECTION_VERSION",

            "recovery_loop_protection_v9.6.0",
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
    # 14 — FINAL STATUS
    # ==============================================================

    section(
        "14 — PHASE 9.2–9.6 FINAL STATUS"
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
        "PHASE 9.2 TERMINAL RUNTIME FAILURE HANDLING: CERTIFIED + FROZEN"
    )

    print(
        "PHASE 9.3 WORKFLOW RECOVERY: CERTIFIED + FROZEN"
    )

    print(
        "PHASE 9.4 COMPENSATION: CERTIFIED + FROZEN"
    )

    print(
        "PHASE 9.5 MANUAL INTERVENTION: CERTIFIED + FROZEN"
    )

    print(
        "PHASE 9.6 RECOVERY LOOP PROTECTION: CERTIFIED + FROZEN"
    )

    print()

    print(
        "9.2 SOURCE SHA256:",
        SHA92,
    )

    print(
        "9.2 FREEZE SHA256:",
        freeze_hashes["9.2"],
    )

    print(
        "9.3 SOURCE SHA256:",
        SHA93,
    )

    print(
        "9.3 FREEZE SHA256:",
        freeze_hashes["9.3"],
    )

    print(
        "9.4 SOURCE SHA256:",
        SHA94,
    )

    print(
        "9.4 FREEZE SHA256:",
        freeze_hashes["9.4"],
    )

    print(
        "9.5 SOURCE SHA256:",
        SHA95,
    )

    print(
        "9.5 FREEZE SHA256:",
        freeze_hashes["9.5"],
    )

    print(
        "9.6 SOURCE SHA256:",
        SHA96,
    )

    print(
        "9.6 FREEZE SHA256:",
        freeze_hashes["9.6"],
    )

    print()

    print(
        "PHASE 9.1–9.6 COMPOSITE SHA256:",
        COMPOSITE,
    )

    print(
        "9.2–9.6 BATCH FREEZE SHA256:",
        BATCH_FREEZE_SHA,
    )

    print(
        "CERTIFICATION REPORT SHA256:",
        REPORT_SHA,
    )

    print()

    print(
        "PHASE 8 MODIFIED: FALSE"
    )

    print(
        "PHASE 9.1 MODIFIED: FALSE"
    )

    print(
        "EXISTING COORDINATION COMPONENTS MODIFIED: FALSE"
    )

    print(
        "UNIVERSAL RUNTIME MODIFIED: FALSE"
    )

    print()

    print(
        "NEXT: PHASE 9.7 — RECOVERY CERTIFICATION"
    )

    print("=" * 120)


except Exception:

    print()
    print("=" * 120)
    print("PHASE 9.2–9.6 BATCH FAILED — ROLLING BACK NEW FILES")
    print("=" * 120)

    for path in created:

        if path.exists():
            path.unlink()

    print(
        "ROLLBACK COMPLETE."
    )

    raise
