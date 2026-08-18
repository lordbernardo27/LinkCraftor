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


UNIVERSAL_ORCHESTRATION_FAN_OUT_COORDINATION_VERSION: Final[str] = (
    "universal_orchestration_fan_out_coordination_v5.1.8"
)

UNIVERSAL_ORCHESTRATION_FAN_OUT_COORDINATION_SCHEMA_VERSION: Final[str] = (
    "universal_orchestration_fan_out_coordination_schema_v1"
)

UNIVERSAL_ORCHESTRATION_FAN_OUT_GROUP_HASH_ALGORITHM: Final[str] = (
    "sha256"
)


class UniversalOrchestrationFanOutCoordinationError(
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


class UniversalOrchestrationFanOutClassification(
    str,
    enum.Enum,
):

    FAN_OUT = "fan_out"

    NO_FAN_OUT = "no_fan_out"


def _require_execution_plan(
    value: Any,
) -> UniversalOrchestrationExecutionPlan:

    if not isinstance(
        value,
        UniversalOrchestrationExecutionPlan,
    ):

        raise UniversalOrchestrationFanOutCoordinationError(
            (
                "execution_plan must be a "
                "UniversalOrchestrationExecutionPlan."
            ),
            code="invalid_fan_out_execution_plan",
            value=value,
        )

    return value


def _normalize_source_job_id(
    value: Any,
) -> str:

    try:

        normalized = (
            normalize_universal_orchestration_identifier(
                value,
                field_name="source_job_id",
            )
        )

    except Exception as exc:

        raise UniversalOrchestrationFanOutCoordinationError(
            (
                "source_job_id must satisfy the canonical "
                "Universal Orchestration identifier contract."
            ),
            code="invalid_fan_out_source_job_id",
            value=value,
        ) from exc

    return normalized
def _require_source_membership(
    *,
    execution_plan: UniversalOrchestrationExecutionPlan,
    source_job_id: str,
) -> None:

    if (
        source_job_id
        not in execution_plan.job_map
    ):

        raise UniversalOrchestrationFanOutCoordinationError(
            (
                "source_job_id must belong to the "
                "Universal Orchestration Execution Plan."
            ),
            code="fan_out_source_not_in_execution_plan",
            value=source_job_id,
        )


def _direct_dependent_job_ids(
    *,
    execution_plan: UniversalOrchestrationExecutionPlan,
    source_job_id: str,
) -> tuple[str, ...]:

    dependents = (
        execution_plan.dependent_map[
            source_job_id
        ]
    )

    if not isinstance(
        dependents,
        tuple,
    ):

        raise UniversalOrchestrationFanOutCoordinationError(
            (
                "Execution Plan dependent_map must expose "
                "canonical immutable tuples."
            ),
            code="invalid_fan_out_dependent_map",
            value=source_job_id,
        )

    return dependents


def classify_universal_orchestration_fan_out(
    *,
    execution_plan: Any,
    source_job_id: Any,
) -> UniversalOrchestrationFanOutClassification:

    plan = (
        _require_execution_plan(
            execution_plan
        )
    )

    source = (
        _normalize_source_job_id(
            source_job_id
        )
    )

    _require_source_membership(
        execution_plan=plan,
        source_job_id=source,
    )

    dependents = (
        _direct_dependent_job_ids(
            execution_plan=plan,
            source_job_id=source,
        )
    )

    if len(
        dependents
    ) >= 2:

        return (
            UniversalOrchestrationFanOutClassification
            .FAN_OUT
        )

    return (
        UniversalOrchestrationFanOutClassification
        .NO_FAN_OUT
    )


def calculate_universal_orchestration_fan_out_group_id(
    *,
    execution_plan: Any,
    source_job_id: Any,
) -> str:

    plan = (
        _require_execution_plan(
            execution_plan
        )
    )

    source = (
        _normalize_source_job_id(
            source_job_id
        )
    )

    _require_source_membership(
        execution_plan=plan,
        source_job_id=source,
    )

    dependents = (
        _direct_dependent_job_ids(
            execution_plan=plan,
            source_job_id=source,
        )
    )

    material = "|".join(
        (
            "universal_orchestration_fan_out_group_v1",
            plan.identity.identity_fingerprint,
            source,
            *dependents,
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
class UniversalOrchestrationFanOutCoordination:

    execution_plan: UniversalOrchestrationExecutionPlan

    source_job_id: str

    schema_version: str = (
        UNIVERSAL_ORCHESTRATION_FAN_OUT_COORDINATION_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        plan = (
            _require_execution_plan(
                self.execution_plan
            )
        )

        source = (
            _normalize_source_job_id(
                self.source_job_id
            )
        )

        if (
            self.schema_version
            !=
            UNIVERSAL_ORCHESTRATION_FAN_OUT_COORDINATION_SCHEMA_VERSION
        ):

            raise UniversalOrchestrationFanOutCoordinationError(
                "Invalid Fan-Out Coordination schema_version.",
                code="invalid_fan_out_schema_version",
                value=self.schema_version,
            )

        _require_source_membership(
            execution_plan=plan,
            source_job_id=source,
        )

        _direct_dependent_job_ids(
            execution_plan=plan,
            source_job_id=source,
        )

        object.__setattr__(
            self,
            "execution_plan",
            plan,
        )

        object.__setattr__(
            self,
            "source_job_id",
            source,
        )

    @property
    def identity(
        self,
    ):

        return self.execution_plan.identity

    @property
    def source_job(
        self,
    ):

        return (
            self.execution_plan.job_map[
                self.source_job_id
            ]
        )

    @property
    def direct_dependent_job_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            _direct_dependent_job_ids(
                execution_plan=self.execution_plan,
                source_job_id=self.source_job_id,
            )
        )

    @property
    def direct_dependent_jobs(
        self,
    ) -> tuple[Any, ...]:

        return tuple(
            self.execution_plan.job_map[
                job_id
            ]
            for job_id
            in self.direct_dependent_job_ids
        )

    @property
    def fan_out_width(
        self,
    ) -> int:

        return len(
            self.direct_dependent_job_ids
        )

    @property
    def classification(
        self,
    ) -> UniversalOrchestrationFanOutClassification:

        return (
            classify_universal_orchestration_fan_out(
                execution_plan=self.execution_plan,
                source_job_id=self.source_job_id,
            )
        )

    @property
    def is_fan_out(
        self,
    ) -> bool:

        return (
            self.classification
            is UniversalOrchestrationFanOutClassification.FAN_OUT
        )

    @property
    def has_dependents(
        self,
    ) -> bool:

        return (
            self.fan_out_width
            > 0
        )

    @property
    def fan_out_group_id(
        self,
    ) -> str:

        return (
            calculate_universal_orchestration_fan_out_group_id(
                execution_plan=self.execution_plan,
                source_job_id=self.source_job_id,
            )
        )


def coordinate_universal_orchestration_fan_out(
    *,
    execution_plan: Any,
    source_job_id: Any,
) -> UniversalOrchestrationFanOutCoordination:

    return UniversalOrchestrationFanOutCoordination(
        execution_plan=(
            _require_execution_plan(
                execution_plan
            )
        ),
        source_job_id=(
            _normalize_source_job_id(
                source_job_id
            )
        ),
    )


def explain_universal_orchestration_fan_out_coordination_v1(
) -> Mapping[
    str,
    Any,
]:

    return MappingProxyType(
        {
            "phase":
                "5.1.8",

            "component":
                "Universal Orchestration Fan-Out Coordination",

            "version":
                UNIVERSAL_ORCHESTRATION_FAN_OUT_COORDINATION_VERSION,

            "schema_version":
                UNIVERSAL_ORCHESTRATION_FAN_OUT_COORDINATION_SCHEMA_VERSION,

            "stored_fields": (
                "execution_plan",
                "source_job_id",
                "schema_version",
            ),

            "classifications": (
                "fan_out",
                "no_fan_out",
            ),

            "fan_out_rule": (
                "A source with two or more direct dependents "
                "in frozen 5.1.5 dependent_map is FAN_OUT."
            ),

            "no_fan_out_rule": (
                "A source with zero or one direct dependent "
                "is NO_FAN_OUT."
            ),

            "direct_edge_rule": (
                "Only direct dependent edges from frozen 5.1.5 "
                "dependent_map define fan-out membership; "
                "transitive descendants are excluded."
            ),

            "wave_boundary": (
                "Jobs sharing a 5.1.5 execution wave are not "
                "implicitly one fan-out group."
            ),

            "lineage_boundary": (
                "parent_job_id, batch_id, and pipeline_run_id "
                "do not create fan-out membership."
            ),

            "readiness_boundary": (
                "5.1.8 does not evaluate 5.1.6 readiness; "
                "fan-out is structural."
            ),

            "handoff_boundary": (
                "5.1.8 does not evaluate 5.1.7 runtime handoff "
                "eligibility; fan-out is structural."
            ),

            "fan_in_boundary": (
                "Fan-in/join coordination belongs to 5.1.9."
            ),

            "condition_boundary": (
                "Conditional branch activation belongs to 5.1.10."
            ),

            "persistence_boundary": (
                "Fan-out persistence belongs to 5.1.14."
            ),

            "group_identity_rule": (
                "fan_out_group_id is deterministic SHA-256 over "
                "orchestration identity, source job, and ordered "
                "direct dependent job IDs."
            ),

            "prohibitions": (
                "does not evaluate UniversalJob.status",
                "does not evaluate job priority",
                "does not evaluate created_at",
                "does not evaluate scheduled_at",
                "does not evaluate stage readiness",
                "does not evaluate runtime handoff eligibility",
                "does not treat parent_job_id as fan-out",
                "does not treat batch_id as fan-out",
                "does not treat pipeline_run_id as fan-out",
                "does not treat execution-wave co-membership as fan-out",
                "does not include transitive descendants",
                "does not coordinate fan-in or joins",
                "does not evaluate conditional branches",
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
                "does not persist fan-out decisions",
                "does not import Universal Coordination Framework",
                "does not invoke pipeline coordinators",
                "does not use wall clock",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_ORCHESTRATION_FAN_OUT_COORDINATION_VERSION",
    "UNIVERSAL_ORCHESTRATION_FAN_OUT_COORDINATION_SCHEMA_VERSION",
    "UNIVERSAL_ORCHESTRATION_FAN_OUT_GROUP_HASH_ALGORITHM",
    "UniversalOrchestrationFanOutCoordinationError",
    "UniversalOrchestrationFanOutClassification",
    "classify_universal_orchestration_fan_out",
    "calculate_universal_orchestration_fan_out_group_id",
    "UniversalOrchestrationFanOutCoordination",
    "coordinate_universal_orchestration_fan_out",
    "explain_universal_orchestration_fan_out_coordination_v1",
]




