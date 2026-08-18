from __future__ import annotations

import enum
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Final, Mapping

from backend.server.runtime.universal_orchestration.dependency_resolution import (
    UniversalOrchestrationDependencyResolution,
)

from backend.server.runtime.universal_orchestration.execution_planning import (
    UniversalOrchestrationExecutionPlan,
)


UNIVERSAL_ORCHESTRATION_STAGE_READINESS_VERSION: Final[str] = (
    "universal_orchestration_stage_readiness_v5.1.6"
)

UNIVERSAL_ORCHESTRATION_STAGE_READINESS_SCHEMA_VERSION: Final[str] = (
    "universal_orchestration_stage_readiness_schema_v1"
)


class UniversalOrchestrationStageReadinessError(
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


class UniversalOrchestrationStageReadinessClassification(
    str,
    enum.Enum,
):

    READY = "ready"

    WAITING = "waiting"

    BLOCKED = "blocked"


class UniversalOrchestrationStageReadinessReason(
    str,
    enum.Enum,
):

    ALL_DEPENDENCIES_SATISFIED = (
        "all_dependencies_satisfied"
    )

    DEPENDENCY_EVIDENCE_PENDING = (
        "dependency_evidence_pending"
    )

    TERMINAL_DEPENDENCY_FAILURE = (
        "terminal_dependency_failure"
    )


def _require_dependency_resolution(
    value: Any,
) -> UniversalOrchestrationDependencyResolution:

    if not isinstance(
        value,
        UniversalOrchestrationDependencyResolution,
    ):

        raise UniversalOrchestrationStageReadinessError(
            (
                "dependency_resolution must be a "
                "UniversalOrchestrationDependencyResolution."
            ),
            code="invalid_stage_readiness_dependency_resolution",
            value=value,
        )

    return value


def _require_execution_plan(
    value: Any,
) -> UniversalOrchestrationExecutionPlan:

    if not isinstance(
        value,
        UniversalOrchestrationExecutionPlan,
    ):

        raise UniversalOrchestrationStageReadinessError(
            (
                "execution_plan must be a "
                "UniversalOrchestrationExecutionPlan."
            ),
            code="invalid_stage_readiness_execution_plan",
            value=value,
        )

    return value


def _validate_stage_readiness_alignment(
    *,
    dependency_resolution: (
        UniversalOrchestrationDependencyResolution
    ),
    execution_plan: UniversalOrchestrationExecutionPlan,
) -> None:

    if (
        dependency_resolution.identity
        != execution_plan.identity
    ):

        raise UniversalOrchestrationStageReadinessError(
            (
                "Dependency Resolution and Execution Plan "
                "must belong to the same orchestration identity."
            ),
            code="stage_readiness_identity_mismatch",
            value=(
                dependency_resolution.identity.orchestration_run_id,
                execution_plan.identity.orchestration_run_id,
            ),
        )

    job_id = (
        dependency_resolution.job_id
    )

    if (
        job_id
        not in execution_plan.job_map
    ):

        raise UniversalOrchestrationStageReadinessError(
            (
                "Dependency Resolution target job must "
                "exist in the Execution Plan."
            ),
            code="stage_readiness_target_not_in_execution_plan",
            value=job_id,
        )

    planned_job = (
        execution_plan.job_map[
            job_id
        ]
    )

    if (
        planned_job
        != dependency_resolution.target_job
    ):

        raise UniversalOrchestrationStageReadinessError(
            (
                "Dependency Resolution target_job must "
                "exactly match the planned UniversalJob."
            ),
            code="stage_readiness_target_job_mismatch",
            value=job_id,
        )

    planned_dependencies = (
        execution_plan.dependency_map[
            job_id
        ]
    )

    if (
        planned_dependencies
        != dependency_resolution.dependency_job_ids
    ):

        raise UniversalOrchestrationStageReadinessError(
            (
                "Dependency Resolution dependency structure "
                "must match the Execution Plan."
            ),
            code="stage_readiness_dependency_structure_mismatch",
            value=job_id,
        )


def classify_universal_orchestration_stage_readiness(
    dependency_resolution: Any,
) -> UniversalOrchestrationStageReadinessClassification:

    resolution = (
        _require_dependency_resolution(
            dependency_resolution
        )
    )

    if (
        resolution.has_terminal_dependency_failure
    ):

        return (
            UniversalOrchestrationStageReadinessClassification
            .BLOCKED
        )

    if (
        resolution.has_unresolved_dependencies
        or
        resolution.has_missing_dependency_evidence
    ):

        return (
            UniversalOrchestrationStageReadinessClassification
            .WAITING
        )

    if (
        resolution.all_dependencies_satisfied
    ):

        return (
            UniversalOrchestrationStageReadinessClassification
            .READY
        )

    raise UniversalOrchestrationStageReadinessError(
        (
            "Dependency Resolution evidence does not map "
            "to a canonical readiness classification."
        ),
        code="inconsistent_stage_readiness_evidence",
        value=resolution.job_id,
    )


def reason_for_universal_orchestration_stage_readiness(
    dependency_resolution: Any,
) -> UniversalOrchestrationStageReadinessReason:

    classification = (
        classify_universal_orchestration_stage_readiness(
            dependency_resolution
        )
    )

    if (
        classification
        is UniversalOrchestrationStageReadinessClassification.BLOCKED
    ):

        return (
            UniversalOrchestrationStageReadinessReason
            .TERMINAL_DEPENDENCY_FAILURE
        )

    if (
        classification
        is UniversalOrchestrationStageReadinessClassification.WAITING
    ):

        return (
            UniversalOrchestrationStageReadinessReason
            .DEPENDENCY_EVIDENCE_PENDING
        )

    return (
        UniversalOrchestrationStageReadinessReason
        .ALL_DEPENDENCIES_SATISFIED
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalOrchestrationStageReadiness:

    dependency_resolution: (
        UniversalOrchestrationDependencyResolution
    )

    execution_plan: (
        UniversalOrchestrationExecutionPlan
    )

    schema_version: str = (
        UNIVERSAL_ORCHESTRATION_STAGE_READINESS_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        dependency_resolution = (
            _require_dependency_resolution(
                self.dependency_resolution
            )
        )

        execution_plan = (
            _require_execution_plan(
                self.execution_plan
            )
        )

        if (
            self.schema_version
            !=
            UNIVERSAL_ORCHESTRATION_STAGE_READINESS_SCHEMA_VERSION
        ):

            raise UniversalOrchestrationStageReadinessError(
                "Invalid Stage Readiness schema_version.",
                code="invalid_stage_readiness_schema_version",
                value=self.schema_version,
            )

        _validate_stage_readiness_alignment(
            dependency_resolution=dependency_resolution,
            execution_plan=execution_plan,
        )

        object.__setattr__(
            self,
            "dependency_resolution",
            dependency_resolution,
        )

        object.__setattr__(
            self,
            "execution_plan",
            execution_plan,
        )

    @property
    def identity(
        self,
    ):

        return (
            self.dependency_resolution.identity
        )

    @property
    def target_job(
        self,
    ):

        return (
            self.dependency_resolution.target_job
        )

    @property
    def job_id(
        self,
    ) -> str:

        return (
            self.dependency_resolution.job_id
        )

    @property
    def classification(
        self,
    ) -> UniversalOrchestrationStageReadinessClassification:

        return (
            classify_universal_orchestration_stage_readiness(
                self.dependency_resolution
            )
        )

    @property
    def reason(
        self,
    ) -> UniversalOrchestrationStageReadinessReason:

        return (
            reason_for_universal_orchestration_stage_readiness(
                self.dependency_resolution
            )
        )

    @property
    def reason_code(
        self,
    ) -> str:

        return self.reason.value

    @property
    def is_ready(
        self,
    ) -> bool:

        return (
            self.classification
            is UniversalOrchestrationStageReadinessClassification.READY
        )

    @property
    def is_waiting(
        self,
    ) -> bool:

        return (
            self.classification
            is UniversalOrchestrationStageReadinessClassification.WAITING
        )

    @property
    def is_blocked(
        self,
    ) -> bool:

        return (
            self.classification
            is UniversalOrchestrationStageReadinessClassification.BLOCKED
        )

    @property
    def satisfied_dependency_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            self.dependency_resolution.satisfied_dependency_ids
        )

    @property
    def unresolved_dependency_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            self.dependency_resolution.unresolved_dependency_ids
        )

    @property
    def terminal_unsatisfied_dependency_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            self.dependency_resolution
            .terminal_unsatisfied_dependency_ids
        )

    @property
    def missing_dependency_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            self.dependency_resolution.missing_dependency_ids
        )

    @property
    def blocking_dependency_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            self.terminal_unsatisfied_dependency_ids
        )

    @property
    def waiting_dependency_ids(
        self,
    ) -> tuple[str, ...]:

        unresolved = frozenset(
            self.unresolved_dependency_ids
        )

        missing = frozenset(
            self.missing_dependency_ids
        )

        return tuple(
            dependency_job_id
            for dependency_job_id
            in self.dependency_resolution.dependency_job_ids
            if (
                dependency_job_id
                in unresolved
                or
                dependency_job_id
                in missing
            )
        )


def evaluate_universal_orchestration_stage_readiness(
    *,
    dependency_resolution: Any,
    execution_plan: Any,
) -> UniversalOrchestrationStageReadiness:

    return UniversalOrchestrationStageReadiness(
        dependency_resolution=(
            _require_dependency_resolution(
                dependency_resolution
            )
        ),
        execution_plan=(
            _require_execution_plan(
                execution_plan
            )
        ),
    )


def explain_universal_orchestration_stage_readiness_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "5.1.6",

            "component":
                "Universal Orchestration Stage Readiness Evaluation",

            "version":
                UNIVERSAL_ORCHESTRATION_STAGE_READINESS_VERSION,

            "schema_version":
                UNIVERSAL_ORCHESTRATION_STAGE_READINESS_SCHEMA_VERSION,

            "stored_fields": (
                "dependency_resolution",
                "execution_plan",
                "schema_version",
            ),

            "classifications": (
                "ready",
                "waiting",
                "blocked",
            ),

            "precedence_rule": (
                "BLOCKED outranks WAITING; WAITING outranks READY."
            ),

            "blocked_rule": (
                "Any terminally-unsatisfied dependency evidence "
                "classifies the target as BLOCKED."
            ),

            "waiting_rule": (
                "Without terminal dependency failure, unresolved "
                "or missing dependency evidence classifies the "
                "target as WAITING."
            ),

            "ready_rule": (
                "Without terminal failure, unresolved dependencies, "
                "or missing evidence, all dependencies satisfied "
                "classifies the target as READY."
            ),

            "zero_dependency_rule": (
                "A zero-dependency target is READY because its "
                "dependency prerequisites are vacuously satisfied."
            ),

            "target_status_boundary": (
                "5.1.6 does not inspect target UniversalJob.status; "
                "readiness is dependency-prerequisite evidence, not "
                "job lifecycle or runtime-handoff eligibility."
            ),

            "handoff_boundary": (
                "Whether a READY target may actually proceed to "
                "runtime handoff belongs to 5.1.7."
            ),

            "suspension_boundary": (
                "Suspension/resume eligibility belongs to 5.1.12."
            ),

            "dependency_boundary": (
                "Dependency status interpretation belongs to frozen "
                "5.1.4 Dependency Resolution."
            ),

            "planning_boundary": (
                "Dependency graph topology belongs to frozen "
                "5.1.5 Execution Planning."
            ),

            "alignment_rule": (
                "Dependency Resolution and Execution Plan must share "
                "the same orchestration identity and exact target "
                "UniversalJob/dependency structure."
            ),

            "prohibitions": (
                "does not inspect target UniversalJob.status",
                "does not use job priority",
                "does not use queue priority",
                "does not use created_at",
                "does not use scheduled_at",
                "does not use retry or attempt counts",
                "does not evaluate worker health",
                "does not evaluate worker capability",
                "does not evaluate worker capacity",
                "does not evaluate worker availability",
                "does not evaluate queue capacity",
                "does not evaluate backpressure",
                "does not evaluate lease availability",
                "does not transition orchestration state",
                "does not perform runtime handoff",
                "does not coordinate actual fan-out",
                "does not coordinate actual fan-in",
                "does not evaluate conditional branches",
                "does not enqueue jobs",
                "does not dequeue jobs",
                "does not claim jobs",
                "does not assign workers",
                "does not acquire worker leases",
                "does not register runtime handlers",
                "does not dispatch runtime handlers",
                "does not execute runtime handlers",
                "does not execute jobs",
                "does not access Runtime State Store",
                "does not persist readiness",
                "does not import Universal Coordination Framework",
                "does not invoke pipeline coordinators",
                "does not use wall clock",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_ORCHESTRATION_STAGE_READINESS_VERSION",
    "UNIVERSAL_ORCHESTRATION_STAGE_READINESS_SCHEMA_VERSION",
    "UniversalOrchestrationStageReadinessError",
    "UniversalOrchestrationStageReadinessClassification",
    "UniversalOrchestrationStageReadinessReason",
    "classify_universal_orchestration_stage_readiness",
    "reason_for_universal_orchestration_stage_readiness",
    "UniversalOrchestrationStageReadiness",
    "evaluate_universal_orchestration_stage_readiness",
    "explain_universal_orchestration_stage_readiness_v1",
]
