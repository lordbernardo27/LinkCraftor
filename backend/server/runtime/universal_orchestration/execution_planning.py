from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Final, Iterable, Mapping

from backend.server.runtime.universal_jobs.contract import (
    UniversalJob,
)

from backend.server.runtime.universal_orchestration.run_identity import (
    UniversalOrchestrationRunIdentity,
)


UNIVERSAL_ORCHESTRATION_EXECUTION_PLANNING_VERSION: Final[str] = (
    "universal_orchestration_execution_planning_v5.1.5"
)

UNIVERSAL_ORCHESTRATION_EXECUTION_PLANNING_SCHEMA_VERSION: Final[str] = (
    "universal_orchestration_execution_planning_schema_v1"
)


class UniversalOrchestrationExecutionPlanningError(
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


def _require_orchestration_run_identity(
    value: Any,
) -> UniversalOrchestrationRunIdentity:

    if not isinstance(
        value,
        UniversalOrchestrationRunIdentity,
    ):

        raise UniversalOrchestrationExecutionPlanningError(
            (
                "identity must be a "
                "UniversalOrchestrationRunIdentity."
            ),
            code="invalid_execution_plan_identity",
            value=value,
        )

    return value


def _normalize_execution_plan_jobs(
    value: Any,
) -> tuple[
    UniversalJob,
    ...,
]:

    if isinstance(
        value,
        (
            str,
            bytes,
            bytearray,
            Mapping,
        ),
    ):

        raise UniversalOrchestrationExecutionPlanningError(
            "jobs must be an iterable of UniversalJob objects.",
            code="invalid_execution_plan_jobs",
            value=value,
        )

    try:

        raw_jobs = tuple(
            value
        )

    except TypeError as exc:

        raise UniversalOrchestrationExecutionPlanningError(
            "jobs must be an iterable of UniversalJob objects.",
            code="invalid_execution_plan_jobs",
            value=value,
        ) from exc

    normalized = []

    seen_job_ids = set()

    for raw_job in raw_jobs:

        if not isinstance(
            raw_job,
            UniversalJob,
        ):

            raise UniversalOrchestrationExecutionPlanningError(
                "Every execution-plan job must be a UniversalJob.",
                code="invalid_execution_plan_job",
                value=raw_job,
            )

        if raw_job.job_id in seen_job_ids:

            raise UniversalOrchestrationExecutionPlanningError(
                "Duplicate UniversalJob supplied to execution plan.",
                code="duplicate_execution_plan_job",
                value=raw_job.job_id,
            )

        seen_job_ids.add(
            raw_job.job_id
        )

        normalized.append(
            raw_job
        )

    return tuple(
        sorted(
            normalized,
            key=lambda job: job.job_id,
        )
    )


def _validate_execution_plan_membership(
    *,
    identity: UniversalOrchestrationRunIdentity,
    jobs: tuple[
        UniversalJob,
        ...,
    ],
) -> None:

    contract_job_ids = frozenset(
        identity.job_ids
    )

    supplied_job_ids = frozenset(
        job.job_id
        for job in jobs
    )

    missing_job_ids = tuple(
        sorted(
            contract_job_ids
            - supplied_job_ids
        )
    )

    if missing_job_ids:

        raise UniversalOrchestrationExecutionPlanningError(
            (
                "Execution plan requires one UniversalJob "
                "for every orchestration contract job_id."
            ),
            code="missing_execution_plan_jobs",
            value=missing_job_ids,
        )

    extra_job_ids = tuple(
        sorted(
            supplied_job_ids
            - contract_job_ids
        )
    )

    if extra_job_ids:

        raise UniversalOrchestrationExecutionPlanningError(
            (
                "Execution plan contains jobs outside the "
                "orchestration contract."
            ),
            code="execution_plan_job_outside_contract",
            value=extra_job_ids,
        )

    for job in jobs:

        if (
            job.workspace_id
            != identity.workspace_id
        ):

            raise UniversalOrchestrationExecutionPlanningError(
                (
                    "Execution-plan job workspace_id does not "
                    "match orchestration identity."
                ),
                code="execution_plan_workspace_mismatch",
                value=job.job_id,
            )

        if (
            job.pipeline
            != identity.pipeline
        ):

            raise UniversalOrchestrationExecutionPlanningError(
                (
                    "Execution-plan job pipeline does not "
                    "match orchestration identity."
                ),
                code="execution_plan_pipeline_mismatch",
                value=job.job_id,
            )

        outside_dependencies = tuple(
            dependency_job_id
            for dependency_job_id
            in job.dependency_job_ids
            if dependency_job_id
            not in contract_job_ids
        )

        if outside_dependencies:

            raise UniversalOrchestrationExecutionPlanningError(
                (
                    "Execution-plan dependency is outside the "
                    "orchestration contract."
                ),
                code="execution_plan_dependency_outside_contract",
                value=(
                    job.job_id,
                    outside_dependencies,
                ),
            )


def _build_dependency_map(
    jobs: tuple[
        UniversalJob,
        ...,
    ],
) -> dict[
    str,
    tuple[
        str,
        ...,
    ],
]:

    return {
        job.job_id: tuple(
            job.dependency_job_ids
        )
        for job in jobs
    }


def _build_dependent_map(
    *,
    job_ids: tuple[
        str,
        ...,
    ],
    dependency_map: Mapping[
        str,
        tuple[
            str,
            ...,
        ],
    ],
) -> dict[
    str,
    tuple[
        str,
        ...,
    ],
]:

    mutable = {
        job_id: []
        for job_id in job_ids
    }

    for dependent_job_id in job_ids:

        for dependency_job_id in (
            dependency_map[
                dependent_job_id
            ]
        ):

            mutable[
                dependency_job_id
            ].append(
                dependent_job_id
            )

    return {
        job_id: tuple(
            sorted(
                dependent_ids
            )
        )
        for job_id, dependent_ids
        in mutable.items()
    }


def _build_execution_waves(
    *,
    job_ids: tuple[
        str,
        ...,
    ],
    dependency_map: Mapping[
        str,
        tuple[
            str,
            ...,
        ],
    ],
    dependent_map: Mapping[
        str,
        tuple[
            str,
            ...,
        ],
    ],
) -> tuple[
    tuple[
        str,
        ...,
    ],
    ...,
]:

    remaining_indegree = {
        job_id: len(
            dependency_map[
                job_id
            ]
        )
        for job_id in job_ids
    }

    frontier = tuple(
        sorted(
            job_id
            for job_id
            in job_ids
            if remaining_indegree[
                job_id
            ] == 0
        )
    )

    waves = []

    processed_count = 0

    while frontier:

        waves.append(
            frontier
        )

        processed_count += len(
            frontier
        )

        next_candidates = set()

        for completed_job_id in frontier:

            for dependent_job_id in (
                dependent_map[
                    completed_job_id
                ]
            ):

                remaining_indegree[
                    dependent_job_id
                ] -= 1

                if (
                    remaining_indegree[
                        dependent_job_id
                    ]
                    == 0
                ):

                    next_candidates.add(
                        dependent_job_id
                    )

        frontier = tuple(
            sorted(
                next_candidates
            )
        )

    if (
        processed_count
        != len(
            job_ids
        )
    ):

        cyclic_job_ids = tuple(
            sorted(
                job_id
                for job_id, indegree
                in remaining_indegree.items()
                if indegree > 0
            )
        )

        raise UniversalOrchestrationExecutionPlanningError(
            (
                "Universal Orchestration execution graph "
                "contains a dependency cycle."
            ),
            code="execution_plan_dependency_cycle",
            value=cyclic_job_ids,
        )

    return tuple(
        waves
    )


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalOrchestrationExecutionPlan:

    identity: UniversalOrchestrationRunIdentity

    jobs: tuple[
        UniversalJob,
        ...,
    ]

    schema_version: str = (
        UNIVERSAL_ORCHESTRATION_EXECUTION_PLANNING_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        identity = (
            _require_orchestration_run_identity(
                self.identity
            )
        )

        jobs = (
            _normalize_execution_plan_jobs(
                self.jobs
            )
        )

        if (
            self.schema_version
            != UNIVERSAL_ORCHESTRATION_EXECUTION_PLANNING_SCHEMA_VERSION
        ):

            raise UniversalOrchestrationExecutionPlanningError(
                "Invalid Execution Planning schema_version.",
                code="invalid_execution_plan_schema_version",
                value=self.schema_version,
            )

        _validate_execution_plan_membership(
            identity=identity,
            jobs=jobs,
        )

        dependency_map = (
            _build_dependency_map(
                jobs
            )
        )

        dependent_map = (
            _build_dependent_map(
                job_ids=tuple(
                    job.job_id
                    for job in jobs
                ),
                dependency_map=dependency_map,
            )
        )

        _build_execution_waves(
            job_ids=tuple(
                job.job_id
                for job in jobs
            ),
            dependency_map=dependency_map,
            dependent_map=dependent_map,
        )

        object.__setattr__(
            self,
            "identity",
            identity,
        )

        object.__setattr__(
            self,
            "jobs",
            jobs,
        )

    @property
    def job_ids(
        self,
    ) -> tuple[
        str,
        ...,
    ]:

        return tuple(
            job.job_id
            for job in self.jobs
        )

    @property
    def job_count(
        self,
    ) -> int:

        return len(
            self.jobs
        )

    @property
    def job_map(
        self,
    ) -> Mapping[
        str,
        UniversalJob,
    ]:

        return MappingProxyType(
            {
                job.job_id: job
                for job in self.jobs
            }
        )

    @property
    def dependency_map(
        self,
    ) -> Mapping[
        str,
        tuple[
            str,
            ...,
        ],
    ]:

        return MappingProxyType(
            _build_dependency_map(
                self.jobs
            )
        )

    @property
    def dependent_map(
        self,
    ) -> Mapping[
        str,
        tuple[
            str,
            ...,
        ],
    ]:

        return MappingProxyType(
            _build_dependent_map(
                job_ids=self.job_ids,
                dependency_map=self.dependency_map,
            )
        )

    @property
    def root_job_ids(
        self,
    ) -> tuple[
        str,
        ...,
    ]:

        return tuple(
            job_id
            for job_id
            in self.job_ids
            if not self.dependency_map[
                job_id
            ]
        )

    @property
    def leaf_job_ids(
        self,
    ) -> tuple[
        str,
        ...,
    ]:

        return tuple(
            job_id
            for job_id
            in self.job_ids
            if not self.dependent_map[
                job_id
            ]
        )

    @property
    def edge_count(
        self,
    ) -> int:

        return sum(
            len(
                dependencies
            )
            for dependencies
            in self.dependency_map.values()
        )

    @property
    def execution_waves(
        self,
    ) -> tuple[
        tuple[
            str,
            ...,
        ],
        ...,
    ]:

        return _build_execution_waves(
            job_ids=self.job_ids,
            dependency_map=self.dependency_map,
            dependent_map=self.dependent_map,
        )

    @property
    def wave_count(
        self,
    ) -> int:

        return len(
            self.execution_waves
        )

    @property
    def topological_order(
        self,
    ) -> tuple[
        str,
        ...,
    ]:

        return tuple(
            job_id
            for wave
            in self.execution_waves
            for job_id
            in wave
        )

    @property
    def max_parallel_width(
        self,
    ) -> int:

        if not self.execution_waves:

            return 0

        return max(
            len(
                wave
            )
            for wave
            in self.execution_waves
        )

    @property
    def graph_depth(
        self,
    ) -> int:

        return self.wave_count


def create_universal_orchestration_execution_plan(
    *,
    identity: Any,
    jobs: Any,
) -> UniversalOrchestrationExecutionPlan:

    return UniversalOrchestrationExecutionPlan(
        identity=(
            _require_orchestration_run_identity(
                identity
            )
        ),
        jobs=(
            _normalize_execution_plan_jobs(
                jobs
            )
        ),
    )


def explain_universal_orchestration_execution_planning_v1(
) -> Mapping[
    str,
    Any,
]:

    return MappingProxyType(
        {
            "phase":
                "5.1.5",

            "component":
                "Universal Orchestration Execution Planning",

            "version":
                UNIVERSAL_ORCHESTRATION_EXECUTION_PLANNING_VERSION,

            "schema_version":
                UNIVERSAL_ORCHESTRATION_EXECUTION_PLANNING_SCHEMA_VERSION,

            "stored_fields": (
                "identity",
                "jobs",
                "schema_version",
            ),

            "graph_rule": (
                "Each dependency_job_id creates a directed edge "
                "from dependency job to dependent job."
            ),

            "complete_plan_rule": (
                "A canonical execution plan requires exactly one "
                "UniversalJob for every 5.1.1 contract job_id."
            ),

            "cycle_rule": (
                "Cross-job dependency cycles are rejected by 5.1.5."
            ),

            "determinism_rule": (
                "Structurally parallel jobs are ordered lexically by "
                "job_id only for deterministic execution-plan output."
            ),

            "priority_boundary": (
                "Universal Job priority, queue priority, created_at, "
                "and queue order do not determine 5.1.5 topology."
            ),

            "parent_boundary": (
                "parent_job_id is lineage evidence and does not create "
                "an execution-plan graph edge unless also explicitly "
                "present in dependency_job_ids."
            ),

            "disconnected_rule": (
                "Disconnected acyclic graph components are valid within "
                "one orchestration contract."
            ),

            "root_rule": (
                "A root job has zero dependency_job_ids."
            ),

            "leaf_rule": (
                "A leaf job has no dependent jobs."
            ),

            "isolated_rule": (
                "An isolated job is both a root and a leaf."
            ),

            "wave_rule": (
                "Execution waves represent structural dependency levels "
                "only; they do not perform execution or readiness decisions."
            ),

            "dependency_status_boundary": (
                "Dependency status evidence belongs to 5.1.4 "
                "Dependency Resolution and is not evaluated by 5.1.5."
            ),

            "readiness_boundary": (
                "READY/BLOCKED/WAITING evaluation belongs to "
                "5.1.6 Stage Readiness Evaluation."
            ),

            "fan_out_boundary": (
                "5.1.5 may expose structural parallelism but actual "
                "fan-out coordination belongs to 5.1.8."
            ),

            "fan_in_boundary": (
                "5.1.5 may expose structural joins but actual "
                "fan-in/join coordination belongs to 5.1.9."
            ),

            "condition_boundary": (
                "Conditional branch evaluation belongs to 5.1.10."
            ),

            "persistence_boundary": (
                "5.1.5 performs no plan persistence; orchestration "
                "persistence belongs to 5.1.14."
            ),

            "prohibitions": (
                "does not evaluate dependency statuses",
                "does not determine READY",
                "does not determine BLOCKED",
                "does not determine WAITING",
                "does not transition orchestration state",
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
                "does not import Universal Coordination Framework",
                "does not invoke pipeline coordinators",
                "does not access Runtime State Store",
                "does not persist execution plans",
                "does not use wall clock",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_ORCHESTRATION_EXECUTION_PLANNING_VERSION",
    "UNIVERSAL_ORCHESTRATION_EXECUTION_PLANNING_SCHEMA_VERSION",
    "UniversalOrchestrationExecutionPlanningError",
    "UniversalOrchestrationExecutionPlan",
    "create_universal_orchestration_execution_plan",
    "explain_universal_orchestration_execution_planning_v1",
]
