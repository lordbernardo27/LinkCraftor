from __future__ import annotations

import enum
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Final, Mapping

from backend.server.runtime.universal_jobs.contract import (
    UniversalJobStatus,
)

from backend.server.runtime.universal_orchestration.stage_readiness import (
    UniversalOrchestrationStageReadiness,
    UniversalOrchestrationStageReadinessClassification,
)


UNIVERSAL_ORCHESTRATION_RUNTIME_HANDOFF_VERSION: Final[str] = (
    "universal_orchestration_runtime_handoff_v5.1.7"
)

UNIVERSAL_ORCHESTRATION_RUNTIME_HANDOFF_SCHEMA_VERSION: Final[str] = (
    "universal_orchestration_runtime_handoff_schema_v1"
)


class UniversalOrchestrationRuntimeHandoffError(
    ValueError
):

    def __init__(
        self,
        message: str,
        *,
        code: str,
        value: Any = None,
    ) -> None:

        super().__init__(
            message
        )

        self.code = str(
            code
        )

        self.value = value


class UniversalOrchestrationRuntimeHandoffClassification(
    str,
    enum.Enum,
):

    ELIGIBLE = "eligible"

    DEFERRED = "deferred"

    INELIGIBLE = "ineligible"


class UniversalOrchestrationRuntimeHandoffReason(
    str,
    enum.Enum,
):

    READY_FOR_RUNTIME_HANDOFF = (
        "ready_for_runtime_handoff"
    )

    READINESS_WAITING = (
        "readiness_waiting"
    )

    READINESS_BLOCKED = (
        "readiness_blocked"
    )

    TARGET_ALREADY_IN_RUNTIME = (
        "target_already_in_runtime"
    )

    TARGET_SUSPENDED = (
        "target_suspended"
    )

    TARGET_TERMINAL = (
        "target_terminal"
    )


HANDOFF_ENTRY_UNIVERSAL_JOB_STATUSES: Final[
    frozenset[UniversalJobStatus]
] = frozenset(
    {
        UniversalJobStatus.CREATED,
    }
)


ALREADY_IN_RUNTIME_UNIVERSAL_JOB_STATUSES: Final[
    frozenset[UniversalJobStatus]
] = frozenset(
    {
        UniversalJobStatus.QUEUED,
        UniversalJobStatus.SCHEDULED,
        UniversalJobStatus.LEASED,
        UniversalJobStatus.RUNNING,
    }
)


TERMINAL_HANDOFF_INELIGIBLE_UNIVERSAL_JOB_STATUSES: Final[
    frozenset[UniversalJobStatus]
] = frozenset(
    {
        UniversalJobStatus.SUCCEEDED,
        UniversalJobStatus.FAILED,
        UniversalJobStatus.CANCELLED,
        UniversalJobStatus.DEAD_LETTER,
        UniversalJobStatus.EXPIRED,
    }
)


def _require_stage_readiness(
    value: Any,
) -> UniversalOrchestrationStageReadiness:

    if not isinstance(
        value,
        UniversalOrchestrationStageReadiness,
    ):

        raise UniversalOrchestrationRuntimeHandoffError(
            (
                "stage_readiness must be a "
                "UniversalOrchestrationStageReadiness."
            ),
            code="invalid_runtime_handoff_stage_readiness",
            value=value,
        )

    return value


def _classify_runtime_handoff(
    stage_readiness: UniversalOrchestrationStageReadiness,
) -> tuple[
    UniversalOrchestrationRuntimeHandoffClassification,
    UniversalOrchestrationRuntimeHandoffReason,
]:

    status = (
        stage_readiness.target_job.status
    )

    if (
        status
        in TERMINAL_HANDOFF_INELIGIBLE_UNIVERSAL_JOB_STATUSES
    ):

        return (
            UniversalOrchestrationRuntimeHandoffClassification
            .INELIGIBLE,
            UniversalOrchestrationRuntimeHandoffReason
            .TARGET_TERMINAL,
        )

    if (
        status
        is UniversalJobStatus.SUSPENDED
    ):

        return (
            UniversalOrchestrationRuntimeHandoffClassification
            .DEFERRED,
            UniversalOrchestrationRuntimeHandoffReason
            .TARGET_SUSPENDED,
        )

    if (
        status
        in ALREADY_IN_RUNTIME_UNIVERSAL_JOB_STATUSES
    ):

        return (
            UniversalOrchestrationRuntimeHandoffClassification
            .INELIGIBLE,
            UniversalOrchestrationRuntimeHandoffReason
            .TARGET_ALREADY_IN_RUNTIME,
        )

    if (
        status
        not in HANDOFF_ENTRY_UNIVERSAL_JOB_STATUSES
    ):

        raise UniversalOrchestrationRuntimeHandoffError(
            (
                "Target UniversalJob.status is not covered by "
                "the canonical 5.1.7 handoff lifecycle partition."
            ),
            code="unsupported_runtime_handoff_target_status",
            value=status,
        )

    readiness = (
        stage_readiness.classification
    )

    if (
        readiness
        is UniversalOrchestrationStageReadinessClassification.READY
    ):

        return (
            UniversalOrchestrationRuntimeHandoffClassification
            .ELIGIBLE,
            UniversalOrchestrationRuntimeHandoffReason
            .READY_FOR_RUNTIME_HANDOFF,
        )

    if (
        readiness
        is UniversalOrchestrationStageReadinessClassification.WAITING
    ):

        return (
            UniversalOrchestrationRuntimeHandoffClassification
            .DEFERRED,
            UniversalOrchestrationRuntimeHandoffReason
            .READINESS_WAITING,
        )

    if (
        readiness
        is UniversalOrchestrationStageReadinessClassification.BLOCKED
    ):

        return (
            UniversalOrchestrationRuntimeHandoffClassification
            .INELIGIBLE,
            UniversalOrchestrationRuntimeHandoffReason
            .READINESS_BLOCKED,
        )

    raise UniversalOrchestrationRuntimeHandoffError(
        (
            "Stage Readiness classification is not covered by "
            "the canonical 5.1.7 handoff decision."
        ),
        code="unsupported_runtime_handoff_readiness",
        value=readiness,
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalOrchestrationRuntimeHandoff:

    stage_readiness: (
        UniversalOrchestrationStageReadiness
    )

    schema_version: str = (
        UNIVERSAL_ORCHESTRATION_RUNTIME_HANDOFF_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        stage_readiness = (
            _require_stage_readiness(
                self.stage_readiness
            )
        )

        if (
            self.schema_version
            != UNIVERSAL_ORCHESTRATION_RUNTIME_HANDOFF_SCHEMA_VERSION
        ):

            raise UniversalOrchestrationRuntimeHandoffError(
                "Invalid Runtime Handoff schema_version.",
                code="invalid_runtime_handoff_schema_version",
                value=self.schema_version,
            )

        _classify_runtime_handoff(
            stage_readiness
        )

        object.__setattr__(
            self,
            "stage_readiness",
            stage_readiness,
        )

    @property
    def identity(
        self,
    ):

        return (
            self.stage_readiness.identity
        )

    @property
    def target_job(
        self,
    ):

        return (
            self.stage_readiness.target_job
        )

    @property
    def job_id(
        self,
    ) -> str:

        return (
            self.stage_readiness.job_id
        )

    @property
    def target_status(
        self,
    ) -> UniversalJobStatus:

        return (
            self.target_job.status
        )

    @property
    def classification(
        self,
    ) -> UniversalOrchestrationRuntimeHandoffClassification:

        classification, _ = (
            _classify_runtime_handoff(
                self.stage_readiness
            )
        )

        return classification

    @property
    def reason(
        self,
    ) -> UniversalOrchestrationRuntimeHandoffReason:

        _, reason = (
            _classify_runtime_handoff(
                self.stage_readiness
            )
        )

        return reason

    @property
    def reason_code(
        self,
    ) -> str:

        return self.reason.value

    @property
    def is_eligible(
        self,
    ) -> bool:

        return (
            self.classification
            is UniversalOrchestrationRuntimeHandoffClassification.ELIGIBLE
        )

    @property
    def is_deferred(
        self,
    ) -> bool:

        return (
            self.classification
            is UniversalOrchestrationRuntimeHandoffClassification.DEFERRED
        )

    @property
    def is_ineligible(
        self,
    ) -> bool:

        return (
            self.classification
            is UniversalOrchestrationRuntimeHandoffClassification.INELIGIBLE
        )


def evaluate_universal_orchestration_runtime_handoff(
    *,
    stage_readiness: Any,
) -> UniversalOrchestrationRuntimeHandoff:

    return UniversalOrchestrationRuntimeHandoff(
        stage_readiness=(
            _require_stage_readiness(
                stage_readiness
            )
        ),
    )


def explain_universal_orchestration_runtime_handoff_v1(
) -> Mapping[
    str,
    Any,
]:

    return MappingProxyType(
        {
            "phase":
                "5.1.7",

            "component":
                "Universal Orchestration Runtime Handoff Management",

            "version":
                UNIVERSAL_ORCHESTRATION_RUNTIME_HANDOFF_VERSION,

            "schema_version":
                UNIVERSAL_ORCHESTRATION_RUNTIME_HANDOFF_SCHEMA_VERSION,

            "stored_fields": (
                "stage_readiness",
                "schema_version",
            ),

            "classifications": (
                "eligible",
                "deferred",
                "ineligible",
            ),

            "eligible_rule": (
                "Only a CREATED target with 5.1.6 READY "
                "dependency readiness is eligible for a new "
                "runtime handoff."
            ),

            "waiting_rule": (
                "A CREATED target with 5.1.6 WAITING readiness "
                "is DEFERRED."
            ),

            "blocked_rule": (
                "A CREATED target with 5.1.6 BLOCKED readiness "
                "is INELIGIBLE."
            ),

            "already_runtime_rule": (
                "QUEUED, SCHEDULED, LEASED, and RUNNING targets "
                "are already beyond the new-handoff boundary and "
                "are INELIGIBLE for another handoff."
            ),

            "suspended_rule": (
                "A SUSPENDED target is DEFERRED; suspension/resume "
                "eligibility belongs to 5.1.12."
            ),

            "terminal_rule": (
                "SUCCEEDED, FAILED, CANCELLED, DEAD_LETTER, and "
                "EXPIRED targets are terminally INELIGIBLE for "
                "a new runtime handoff."
            ),

            "readiness_boundary": (
                "Dependency readiness belongs to frozen 5.1.6; "
                "5.1.7 consumes that result rather than recomputing it."
            ),

            "queue_boundary": (
                "5.1.7 does not enqueue, schedule, dequeue, claim, "
                "or mutate queue membership."
            ),

            "worker_boundary": (
                "Worker discovery, assignment, capacity, capability, "
                "health, and leasing remain Worker Infrastructure."
            ),

            "runtime_registration_boundary": (
                "Runtime Registration owns handler registration and "
                "handler dispatch; 5.1.7 performs no handler lookup "
                "or dispatch."
            ),

            "execution_boundary": (
                "The Universal Runtime Worker and downstream execution "
                "authorities own claim/dispatch/execution after handoff."
            ),

            "fan_out_boundary": (
                "Actual fan-out coordination belongs to 5.1.8."
            ),

            "fan_in_boundary": (
                "Actual fan-in/join coordination belongs to 5.1.9."
            ),

            "condition_boundary": (
                "Conditional branching belongs to 5.1.10."
            ),

            "suspension_boundary": (
                "Suspension and resume eligibility belongs to 5.1.12."
            ),

            "persistence_boundary": (
                "Handoff persistence belongs to the later "
                "orchestration persistence authority in 5.1.14."
            ),

            "prohibitions": (
                "does not mutate UniversalJob.status",
                "does not enqueue jobs",
                "does not schedule jobs",
                "does not dequeue jobs",
                "does not claim jobs",
                "does not assign workers",
                "does not acquire worker leases",
                "does not evaluate worker health",
                "does not evaluate worker capability",
                "does not evaluate worker capacity",
                "does not evaluate queue capacity",
                "does not evaluate backpressure",
                "does not look up runtime handlers",
                "does not register runtime handlers",
                "does not dispatch runtime handlers",
                "does not execute runtime handlers",
                "does not execute jobs",
                "does not transition orchestration state",
                "does not coordinate actual fan-out",
                "does not coordinate actual fan-in",
                "does not evaluate conditional branches",
                "does not access Runtime State Store",
                "does not persist handoff decisions",
                "does not import Universal Coordination Framework",
                "does not invoke pipeline coordinators",
                "does not use job priority",
                "does not use queue priority",
                "does not use created_at",
                "does not use scheduled_at",
                "does not use wall clock",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_ORCHESTRATION_RUNTIME_HANDOFF_VERSION",
    "UNIVERSAL_ORCHESTRATION_RUNTIME_HANDOFF_SCHEMA_VERSION",
    "UniversalOrchestrationRuntimeHandoffError",
    "UniversalOrchestrationRuntimeHandoffClassification",
    "UniversalOrchestrationRuntimeHandoffReason",
    "HANDOFF_ENTRY_UNIVERSAL_JOB_STATUSES",
    "ALREADY_IN_RUNTIME_UNIVERSAL_JOB_STATUSES",
    "TERMINAL_HANDOFF_INELIGIBLE_UNIVERSAL_JOB_STATUSES",
    "UniversalOrchestrationRuntimeHandoff",
    "evaluate_universal_orchestration_runtime_handoff",
    "explain_universal_orchestration_runtime_handoff_v1",
]
