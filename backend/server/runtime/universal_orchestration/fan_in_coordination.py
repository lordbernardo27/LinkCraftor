from __future__ import annotations

import enum
import hashlib
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Final, Mapping

from backend.server.runtime.universal_orchestration.contract import (
    normalize_universal_orchestration_identifier,
)

from backend.server.runtime.universal_orchestration.execution_planning import (
    UniversalOrchestrationExecutionPlan,
)


UNIVERSAL_ORCHESTRATION_FAN_IN_COORDINATION_VERSION: Final[str] = (
    "universal_orchestration_fan_in_coordination_v5.1.9"
)

UNIVERSAL_ORCHESTRATION_FAN_IN_COORDINATION_SCHEMA_VERSION: Final[str] = (
    "universal_orchestration_fan_in_coordination_schema_v1"
)

UNIVERSAL_ORCHESTRATION_JOIN_GROUP_HASH_ALGORITHM: Final[str] = (
    "sha256"
)


class UniversalOrchestrationFanInCoordinationError(
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


class UniversalOrchestrationFanInClassification(
    str,
    enum.Enum,
):

    JOIN = "join"

    NO_JOIN = "no_join"


def _require_execution_plan(
    value: Any,
) -> UniversalOrchestrationExecutionPlan:

    if not isinstance(
        value,
        UniversalOrchestrationExecutionPlan,
    ):

        raise UniversalOrchestrationFanInCoordinationError(
            (
                "execution_plan must be a "
                "UniversalOrchestrationExecutionPlan."
            ),
            code="invalid_fan_in_execution_plan",
            value=value,
        )

    return value


def _normalize_target_job_id(
    value: Any,
) -> str:

    try:

        normalized = (
            normalize_universal_orchestration_identifier(
                value,
                field_name="target_job_id",
            )
        )

    except Exception as exc:

        raise UniversalOrchestrationFanInCoordinationError(
            (
                "target_job_id must satisfy the canonical "
                "Universal Orchestration identifier contract."
            ),
            code="invalid_fan_in_target_job_id",
            value=value,
        ) from exc

    return normalized


def _require_target_membership(
    *,
    execution_plan: UniversalOrchestrationExecutionPlan,
    target_job_id: str,
) -> None:

    if (
        target_job_id
        not in execution_plan.job_map
    ):

        raise UniversalOrchestrationFanInCoordinationError(
            (
                "target_job_id must belong to the "
                "Universal Orchestration Execution Plan."
            ),
            code="fan_in_target_not_in_execution_plan",
            value=target_job_id,
        )


def _direct_dependency_job_ids(
    *,
    execution_plan: UniversalOrchestrationExecutionPlan,
    target_job_id: str,
) -> tuple[str, ...]:

    dependencies = (
        execution_plan.dependency_map[
            target_job_id
        ]
    )

    if not isinstance(
        dependencies,
        tuple,
    ):

        raise UniversalOrchestrationFanInCoordinationError(
            (
                "Execution Plan dependency_map must expose "
                "canonical immutable tuples."
            ),
            code="invalid_fan_in_dependency_map",
            value=target_job_id,
        )

    return dependencies


def classify_universal_orchestration_fan_in(
    *,
    execution_plan: Any,
    target_job_id: Any,
) -> UniversalOrchestrationFanInClassification:

    plan = (
        _require_execution_plan(
            execution_plan
        )
    )

    target = (
        _normalize_target_job_id(
            target_job_id
        )
    )

    _require_target_membership(
        execution_plan=plan,
        target_job_id=target,
    )

    dependencies = (
        _direct_dependency_job_ids(
            execution_plan=plan,
            target_job_id=target,
        )
    )

    if len(
        dependencies
    ) >= 2:

        return (
            UniversalOrchestrationFanInClassification
            .JOIN
        )

    return (
        UniversalOrchestrationFanInClassification
        .NO_JOIN
    )


def calculate_universal_orchestration_join_group_id(
    *,
    execution_plan: Any,
    target_job_id: Any,
) -> str:

    plan = (
        _require_execution_plan(
            execution_plan
        )
    )

    target = (
        _normalize_target_job_id(
            target_job_id
        )
    )

    _require_target_membership(
        execution_plan=plan,
        target_job_id=target,
    )

    dependencies = (
        _direct_dependency_job_ids(
            execution_plan=plan,
            target_job_id=target,
        )
    )

    material = "|".join(
        (
            "universal_orchestration_join_group_v1",
            plan.identity.identity_fingerprint,
            target,
            *dependencies,
        )
    )

    return hashlib.sha256(
        material.encode(
            "utf-8"
        )
    ).hexdigest().upper()


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalOrchestrationFanInCoordination:

    execution_plan: UniversalOrchestrationExecutionPlan

    target_job_id: str

    schema_version: str = (
        UNIVERSAL_ORCHESTRATION_FAN_IN_COORDINATION_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        plan = (
            _require_execution_plan(
                self.execution_plan
            )
        )

        target = (
            _normalize_target_job_id(
                self.target_job_id
            )
        )

        if (
            self.schema_version
            !=
            UNIVERSAL_ORCHESTRATION_FAN_IN_COORDINATION_SCHEMA_VERSION
        ):

            raise UniversalOrchestrationFanInCoordinationError(
                "Invalid Fan-In Coordination schema_version.",
                code="invalid_fan_in_schema_version",
                value=self.schema_version,
            )

        _require_target_membership(
            execution_plan=plan,
            target_job_id=target,
        )

        _direct_dependency_job_ids(
            execution_plan=plan,
            target_job_id=target,
        )

        object.__setattr__(
            self,
            "execution_plan",
            plan,
        )

        object.__setattr__(
            self,
            "target_job_id",
            target,
        )

    @property
    def identity(
        self,
    ):

        return self.execution_plan.identity

    @property
    def target_job(
        self,
    ):

        return (
            self.execution_plan.job_map[
                self.target_job_id
            ]
        )

    @property
    def direct_dependency_job_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            _direct_dependency_job_ids(
                execution_plan=self.execution_plan,
                target_job_id=self.target_job_id,
            )
        )

    @property
    def direct_dependency_jobs(
        self,
    ) -> tuple[Any, ...]:

        return tuple(
            self.execution_plan.job_map[
                job_id
            ]
            for job_id
            in self.direct_dependency_job_ids
        )

    @property
    def join_width(
        self,
    ) -> int:

        return len(
            self.direct_dependency_job_ids
        )

    @property
    def classification(
        self,
    ) -> UniversalOrchestrationFanInClassification:

        return (
            classify_universal_orchestration_fan_in(
                execution_plan=self.execution_plan,
                target_job_id=self.target_job_id,
            )
        )

    @property
    def is_join(
        self,
    ) -> bool:

        return (
            self.classification
            is UniversalOrchestrationFanInClassification.JOIN
        )

    @property
    def has_dependencies(
        self,
    ) -> bool:

        return (
            self.join_width
            > 0
        )

    @property
    def join_group_id(
        self,
    ) -> str:

        return (
            calculate_universal_orchestration_join_group_id(
                execution_plan=self.execution_plan,
                target_job_id=self.target_job_id,
            )
        )


def coordinate_universal_orchestration_fan_in(
    *,
    execution_plan: Any,
    target_job_id: Any,
) -> UniversalOrchestrationFanInCoordination:

    return UniversalOrchestrationFanInCoordination(
        execution_plan=(
            _require_execution_plan(
                execution_plan
            )
        ),
        target_job_id=(
            _normalize_target_job_id(
                target_job_id
            )
        ),
    )


def explain_universal_orchestration_fan_in_coordination_v1(
) -> Mapping[
    str,
    Any,
]:

    return MappingProxyType(
        {
            "phase":
                "5.1.9",

            "component":
                "Universal Orchestration Fan-In / Join Coordination",

            "version":
                UNIVERSAL_ORCHESTRATION_FAN_IN_COORDINATION_VERSION,

            "schema_version":
                UNIVERSAL_ORCHESTRATION_FAN_IN_COORDINATION_SCHEMA_VERSION,

            "stored_fields": (
                "execution_plan",
                "target_job_id",
                "schema_version",
            ),

            "classifications": (
                "join",
                "no_join",
            ),

            "join_rule": (
                "A target with two or more direct dependencies "
                "in frozen 5.1.5 dependency_map is JOIN."
            ),

            "no_join_rule": (
                "A target with zero or one direct dependency "
                "is NO_JOIN."
            ),

            "direct_edge_rule": (
                "Only direct incoming dependency edges from "
                "frozen 5.1.5 dependency_map define join "
                "membership; transitive ancestors are excluded."
            ),

            "wave_boundary": (
                "Execution-wave co-membership does not define "
                "fan-in or join membership."
            ),

            "lineage_boundary": (
                "parent_job_id, batch_id, and pipeline_run_id "
                "do not create join membership."
            ),

            "dependency_resolution_boundary": (
                "5.1.9 does not evaluate dependency-status "
                "evidence; 5.1.4 owns Dependency Resolution."
            ),

            "readiness_boundary": (
                "5.1.9 does not classify READY, WAITING, or "
                "BLOCKED; 5.1.6 owns Stage Readiness."
            ),

            "handoff_boundary": (
                "5.1.9 does not evaluate runtime handoff "
                "eligibility; 5.1.7 owns Runtime Handoff."
            ),

            "fan_out_boundary": (
                "5.1.8 and 5.1.9 are independent structural "
                "views derived from frozen 5.1.5."
            ),

            "condition_boundary": (
                "Conditional branch activation belongs to 5.1.10."
            ),

            "completion_boundary": (
                "Overall orchestration completion resolution "
                "belongs to 5.1.15."
            ),

            "persistence_boundary": (
                "Fan-in/join persistence belongs to 5.1.14."
            ),

            "group_identity_rule": (
                "join_group_id is deterministic SHA-256 over "
                "orchestration identity, target job, and ordered "
                "direct dependency job IDs."
            ),

            "prohibitions": (
                "does not evaluate UniversalJob.status",
                "does not evaluate job priority",
                "does not evaluate created_at",
                "does not evaluate scheduled_at",
                "does not evaluate dependency statuses",
                "does not evaluate all_dependencies_satisfied",
                "does not evaluate stage readiness",
                "does not evaluate runtime handoff eligibility",
                "does not consume fan-out coordination objects",
                "does not treat parent_job_id as join",
                "does not treat batch_id as join",
                "does not treat pipeline_run_id as join",
                "does not treat execution-wave co-membership as join",
                "does not include transitive ancestors",
                "does not evaluate conditional branches",
                "does not determine orchestration completion",
                "does not wait for dependencies",
                "does not sleep or poll",
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
                "does not dispatch runtime handlers",
                "does not execute runtime handlers",
                "does not execute jobs",
                "does not create threads",
                "does not create processes",
                "does not create async tasks",
                "does not mutate UniversalJob.status",
                "does not transition orchestration state",
                "does not access Runtime State Store",
                "does not persist fan-in decisions",
                "does not import Universal Coordination Framework",
                "does not invoke pipeline coordinators",
                "does not use wall clock",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_ORCHESTRATION_FAN_IN_COORDINATION_VERSION",
    "UNIVERSAL_ORCHESTRATION_FAN_IN_COORDINATION_SCHEMA_VERSION",
    "UNIVERSAL_ORCHESTRATION_JOIN_GROUP_HASH_ALGORITHM",
    "UniversalOrchestrationFanInCoordinationError",
    "UniversalOrchestrationFanInClassification",
    "classify_universal_orchestration_fan_in",
    "calculate_universal_orchestration_join_group_id",
    "UniversalOrchestrationFanInCoordination",
    "coordinate_universal_orchestration_fan_in",
    "explain_universal_orchestration_fan_in_coordination_v1",
]
