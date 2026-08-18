"""
LinkCraftor
Universal Coordination Framework

Phase 4.5 — Execution Planner

Canonical responsibility
------------------------
Convert a frozen Phase 4.4 RunnableStageResolution into a deterministic
immediate execution wave.

Phase 4.5 plans only work that is runnable NOW.

It does NOT:
- predict future workflow stages,
- build a full remaining-workflow topological plan,
- invent dependencies between simultaneously runnable stages,
- dispatch jobs,
- create Runtime jobs,
- select workers,
- inspect Runtime queue state,
- apply Runtime capacity/priority/retry/resource policy,
- persist planning state.

Lexical ordering inside an execution wave is deterministic serialization
and evidence only. It does not imply forced serial execution.

Authority boundaries:
- graph construction -> Phase 4.1
- dependency validation -> Phase 4.2
- cycle detection -> Phase 4.3
- runnable-stage eligibility -> Phase 4.4
- planning certification -> Phase 4.6
- Runtime execution -> Phase 5
- handoff -> Phase 6
- advanced orchestration -> Phase 7
- persistence -> Phase 8
- recovery -> Phase 9
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import (
    Any,
    Final,
    Mapping,
)

from backend.server.coordination.dependency_planning.dependency_graph import (
    DEPENDENCY_GRAPH_VERSION,
    DependencyGraph,
)

from backend.server.coordination.dependency_planning.dependency_validation import (
    DEPENDENCY_VALIDATION_VERSION,
)

from backend.server.coordination.dependency_planning.cycle_detection import (
    CYCLE_DETECTION_VERSION,
    require_acyclic_dependency_graph,
)

from backend.server.coordination.dependency_planning.runnable_stage_resolver import (
    RUNNABLE_STAGE_RESOLVER_VERSION,
    RunnableStageResolution,
)


# =============================================================================
# 1. Canonical identity
# =============================================================================

EXECUTION_PLANNER_VERSION: Final[str] = (
    "execution_planner_v4.5.0"
)

EXECUTION_PLANNER_SCHEMA_VERSION: Final[str] = (
    "execution_planner_schema_v1"
)

EXECUTION_WAVE_FIELD_COUNT: Final[int] = 3

EXECUTION_PLAN_FIELD_COUNT: Final[int] = 8


# =============================================================================
# 2. Errors
# =============================================================================

class ExecutionPlannerError(
    ValueError
):
    """Base Phase 4.5 execution-planning error."""


class InvalidExecutionPlanningRequestError(
    ExecutionPlannerError
):
    """Planner input is not canonical."""


class ExecutionPlanWorkflowMismatchError(
    ExecutionPlannerError
):
    """Graph and runnability result belong to different workflows."""


class ExecutionPlanRunnabilityMismatchError(
    ExecutionPlannerError
):
    """Runnability result contains stages not valid for this graph."""


# =============================================================================
# 3. Immutable helper
# =============================================================================

def _freeze(
    value: Any,
) -> Any:
    if isinstance(
        value,
        Mapping,
    ):
        return MappingProxyType(
            {
                key: _freeze(item)
                for key, item
                in value.items()
            }
        )

    if isinstance(
        value,
        (list, tuple),
    ):
        return tuple(
            _freeze(item)
            for item
            in value
        )

    if isinstance(
        value,
        set,
    ):
        return frozenset(
            _freeze(item)
            for item
            in value
        )

    return value


# =============================================================================
# 4. Execution wave
# =============================================================================

@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionWave:
    wave_index: int
    stage_ids: tuple[str, ...]
    execution_semantics: str

    def to_dict(
        self,
    ) -> Mapping[str, Any]:
        return MappingProxyType(
            {
                "wave_index":
                    self.wave_index,

                "stage_ids":
                    self.stage_ids,

                "execution_semantics":
                    self.execution_semantics,
            }
        )


# =============================================================================
# 5. Execution plan
# =============================================================================

@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionPlan:
    workflow_id: str
    wave_count: int
    waves: tuple[
        ExecutionWave,
        ...,
    ]
    planned_stage_ids: tuple[str, ...]
    graph_version: str
    cycle_detection_version: str
    runnable_stage_resolver_version: str
    planner_version: str

    def to_dict(
        self,
    ) -> Mapping[str, Any]:
        return _freeze(
            {
                "workflow_id":
                    self.workflow_id,

                "wave_count":
                    self.wave_count,

                "waves":
                    tuple(
                        wave.to_dict()
                        for wave
                        in self.waves
                    ),

                "planned_stage_ids":
                    self.planned_stage_ids,

                "graph_version":
                    self.graph_version,

                "cycle_detection_version":
                    self.cycle_detection_version,

                "runnable_stage_resolver_version":
                    self.runnable_stage_resolver_version,

                "planner_version":
                    self.planner_version,
            }
        )


# =============================================================================
# 6. Planning-input validation
# =============================================================================

def _validate_planning_inputs(
    graph: DependencyGraph,
    resolution: RunnableStageResolution,
) -> None:
    """
    Validate the canonical Phase 4.1 + Phase 4.4 planning boundary.

    Phase 4.5 accepts only a canonical RunnableStageResolution produced
    against the same frozen dependency-planning versions and graph.

    This validator is intentionally read-only and performs no Runtime,
    persistence, dispatch, scheduling, or workflow mutation.
    """

    if not isinstance(
        graph,
        DependencyGraph,
    ):
        raise InvalidExecutionPlanningRequestError(
            "graph must be a Phase 4.1 DependencyGraph."
        )

    if not isinstance(
        resolution,
        RunnableStageResolution,
    ):
        raise InvalidExecutionPlanningRequestError(
            "resolution must be a Phase 4.4 "
            "RunnableStageResolution."
        )

    # Includes:
    # - frozen Phase 4.2 dependency validation,
    # - frozen Phase 4.3 acyclic validation.
    require_acyclic_dependency_graph(
        graph
    )

    # -------------------------------------------------------------------------
    # Workflow identity
    # -------------------------------------------------------------------------

    if (
        resolution.workflow_id
        != graph.workflow_id
    ):
        raise ExecutionPlanWorkflowMismatchError(
            "RunnableStageResolution workflow_id "
            "must match DependencyGraph workflow_id."
        )

    # -------------------------------------------------------------------------
    # Frozen upstream version integrity
    # -------------------------------------------------------------------------

    if (
        resolution.graph_version
        != graph.graph_version
    ):
        raise ExecutionPlanRunnabilityMismatchError(
            "RunnableStageResolution graph_version "
            "must match DependencyGraph graph_version."
        )

    if (
        resolution.graph_version
        != DEPENDENCY_GRAPH_VERSION
    ):
        raise ExecutionPlanRunnabilityMismatchError(
            "RunnableStageResolution graph_version "
            "must equal the frozen Phase 4.1 version."
        )

    if (
        resolution.cycle_detection_version
        != CYCLE_DETECTION_VERSION
    ):
        raise ExecutionPlanRunnabilityMismatchError(
            "RunnableStageResolution cycle_detection_version "
            "must equal the frozen Phase 4.3 version."
        )

    if (
        resolution.resolver_version
        != RUNNABLE_STAGE_RESOLVER_VERSION
    ):
        raise ExecutionPlanRunnabilityMismatchError(
            "RunnableStageResolution resolver_version "
            "must equal the frozen Phase 4.4 version."
        )

    # -------------------------------------------------------------------------
    # Canonical tuple integrity
    # -------------------------------------------------------------------------

    stage_collections = (
        (
            "runnable_stage_ids",
            resolution.runnable_stage_ids,
        ),
        (
            "blocked_stage_ids",
            resolution.blocked_stage_ids,
        ),
        (
            "untracked_stage_ids",
            resolution.untracked_stage_ids,
        ),
    )

    for (
        field_name,
        stage_ids,
    ) in stage_collections:

        if not isinstance(
            stage_ids,
            tuple,
        ):
            raise ExecutionPlanRunnabilityMismatchError(
                f"{field_name} must be a canonical tuple."
            )

        for stage_id in stage_ids:

            if not isinstance(
                stage_id,
                str,
            ):
                raise ExecutionPlanRunnabilityMismatchError(
                    f"{field_name} must contain stage_id strings."
                )

            if (
                not stage_id
                or stage_id
                != stage_id.strip()
            ):
                raise ExecutionPlanRunnabilityMismatchError(
                    f"{field_name} contains a non-canonical stage_id."
                )

        canonical = tuple(
            sorted(
                set(
                    stage_ids
                )
            )
        )

        if stage_ids != canonical:
            raise ExecutionPlanRunnabilityMismatchError(
                f"{field_name} must be lexical, unique, "
                "and canonical."
            )

    # -------------------------------------------------------------------------
    # Graph membership
    # -------------------------------------------------------------------------

    graph_nodes = set(
        graph.node_ids
    )

    runnable = set(
        resolution.runnable_stage_ids
    )

    blocked = set(
        resolution.blocked_stage_ids
    )

    untracked = set(
        resolution.untracked_stage_ids
    )

    unknown_runnable = (
        runnable
        - graph_nodes
    )

    if unknown_runnable:
        raise ExecutionPlanRunnabilityMismatchError(
            "RunnableStageResolution contains runnable "
            "stage IDs outside DependencyGraph: "
            f"{tuple(sorted(unknown_runnable))!r}"
        )

    unknown_blocked = (
        blocked
        - graph_nodes
    )

    if unknown_blocked:
        raise ExecutionPlanRunnabilityMismatchError(
            "RunnableStageResolution contains blocked "
            "stage IDs outside DependencyGraph: "
            f"{tuple(sorted(unknown_blocked))!r}"
        )

    unknown_untracked = (
        untracked
        - graph_nodes
    )

    if unknown_untracked:
        raise ExecutionPlanRunnabilityMismatchError(
            "RunnableStageResolution contains untracked "
            "stage IDs outside DependencyGraph: "
            f"{tuple(sorted(unknown_untracked))!r}"
        )

    # -------------------------------------------------------------------------
    # State-set disjointness
    # -------------------------------------------------------------------------

    runnable_blocked_overlap = (
        runnable
        & blocked
    )

    if runnable_blocked_overlap:
        raise ExecutionPlanRunnabilityMismatchError(
            "Runnable and blocked stage IDs must be disjoint: "
            f"{tuple(sorted(runnable_blocked_overlap))!r}"
        )

    runnable_untracked_overlap = (
        runnable
        & untracked
    )

    if runnable_untracked_overlap:
        raise ExecutionPlanRunnabilityMismatchError(
            "Runnable and untracked stage IDs must be disjoint: "
            f"{tuple(sorted(runnable_untracked_overlap))!r}"
        )

    blocked_untracked_overlap = (
        blocked
        & untracked
    )

    if blocked_untracked_overlap:
        raise ExecutionPlanRunnabilityMismatchError(
            "Blocked and untracked stage IDs must be disjoint: "
            f"{tuple(sorted(blocked_untracked_overlap))!r}"
        )

# =============================================================================
# 7. Immediate execution planning
# =============================================================================

def create_execution_plan(
    graph: DependencyGraph,
    resolution: RunnableStageResolution,
) -> ExecutionPlan:
    """
    Create one immediate execution wave from Phase 4.4 runnable stages.

    All currently runnable stages remain in the same wave.

    Lexical ordering inside the wave is deterministic representation only.
    It does not impose serial execution.
    """

    _validate_planning_inputs(
        graph,
        resolution,
    )

    planned_stage_ids = tuple(
        sorted(
            resolution.runnable_stage_ids
        )
    )

    if planned_stage_ids:
        waves = (
            ExecutionWave(
                wave_index=1,
                stage_ids=planned_stage_ids,
                execution_semantics=(
                    "parallel_eligible"
                ),
            ),
        )

    else:
        waves = ()

    return ExecutionPlan(
        workflow_id=resolution.workflow_id,
        wave_count=len(
            waves
        ),
        waves=waves,
        planned_stage_ids=planned_stage_ids,
        graph_version=graph.graph_version,
        cycle_detection_version=(
            CYCLE_DETECTION_VERSION
        ),
        runnable_stage_resolver_version=(
            RUNNABLE_STAGE_RESOLVER_VERSION
        ),
        planner_version=(
            EXECUTION_PLANNER_VERSION
        ),
    )


# =============================================================================
# 8. Snapshot
# =============================================================================

def execution_plan_snapshot(
    graph: DependencyGraph,
    resolution: RunnableStageResolution,
) -> Mapping[str, Any]:
    plan = create_execution_plan(
        graph,
        resolution,
    )

    return _freeze(
        {
            "planner_version":
                EXECUTION_PLANNER_VERSION,

            "schema_version":
                EXECUTION_PLANNER_SCHEMA_VERSION,

            "workflow_id":
                plan.workflow_id,

            "graph_version":
                plan.graph_version,

            "cycle_detection_version":
                plan.cycle_detection_version,

            "runnable_stage_resolver_version":
                plan.runnable_stage_resolver_version,

            "wave_count":
                plan.wave_count,

            "waves":
                tuple(
                    wave.to_dict()
                    for wave
                    in plan.waves
                ),

            "planned_stage_ids":
                plan.planned_stage_ids,
        }
    )


# =============================================================================
# 9. Architecture evidence
# =============================================================================

def explain_execution_planner_v4_5(
) -> Mapping[str, Any]:
    return _freeze(
        {
            "phase":
                "4.5",

            "component":
                "Execution Planner",

            "version":
                EXECUTION_PLANNER_VERSION,

            "schema_version":
                EXECUTION_PLANNER_SCHEMA_VERSION,

            "topology_authority":
                "Phase 4.1 DependencyGraph",

            "validation_authority":
                "Phase 4.2 Dependency Validation",

            "acyclic_authority":
                "Phase 4.3 Cycle Detection",

            "runnability_authority":
                "Phase 4.4 RunnableStageResolution",

            "upstream_versions": {
                "4.1":
                    DEPENDENCY_GRAPH_VERSION,

                "4.2":
                    DEPENDENCY_VALIDATION_VERSION,

                "4.3":
                    CYCLE_DETECTION_VERSION,

                "4.4":
                    RUNNABLE_STAGE_RESOLVER_VERSION,
            },

            "planning_scope": {
                "mode":
                    "immediate_current_execution_wave",

                "future_stage_prediction":
                    False,

                "full_remaining_workflow_topological_plan":
                    False,

                "only_currently_runnable_stages":
                    True,
            },

            "wave_semantics": {
                "simultaneously_runnable_stages":
                    "one execution wave",

                "within_wave_order":
                    "lexical deterministic",

                "lexical_order_meaning":
                    "serialization and evidence only",

                "forced_serial_execution":
                    False,

                "artificial_dependencies":
                    False,

                "empty_runnable_set":
                    "valid empty plan",
            },

            "exclusions": {
                "blocked_stages":
                    "excluded",

                "untracked_stages":
                    "excluded",
            },

            "runtime_policy": {
                "worker_capacity":
                    "not considered",

                "queue_state":
                    "not considered",

                "priority":
                    "not considered",

                "retries":
                    "not considered",

                "cost":
                    "not considered",

                "resource_availability":
                    "not considered",

                "job_creation":
                    False,

                "dispatch":
                    False,
            },

            "owns": (
                "immediate execution-wave construction",
                "deterministic execution-plan representation",
                "parallel eligibility preservation",
                "planning input identity validation",
                "immutable execution-plan evidence",
            ),

            "does_not_own": (
                "dependency graph construction",
                "dependency semantic validation",
                "cycle detection",
                "runnable-stage eligibility",
                "future workflow prediction",
                "full remaining-workflow topological planning",
                "planning certification",
                "Runtime Registration",
                "Runtime job creation",
                "Runtime dispatch",
                "worker selection",
                "queue scheduling",
                "priority scheduling",
                "stage handoff",
                "fan-out/fan-in policy",
                "conditional execution",
                "skip semantics",
                "workflow persistence",
                "workflow recovery",
            ),

            "future_authority": {
                "4.6":
                    "Planning Certification",

                "5":
                    "Runtime Integration",

                "7":
                    "Advanced Orchestration",
            },

            "execution_properties": {
                "read_only":
                    True,

                "deterministic":
                    True,

                "side_effect_free":
                    True,

                "graph_mutation":
                    False,

                "resolution_mutation":
                    False,

                "runtime_execution":
                    False,

                "runtime_job_creation":
                    False,

                "persistence":
                    False,
            },
        }
    )


__all__ = [
    "EXECUTION_PLANNER_VERSION",
    "EXECUTION_PLANNER_SCHEMA_VERSION",
    "EXECUTION_WAVE_FIELD_COUNT",
    "EXECUTION_PLAN_FIELD_COUNT",
    "ExecutionPlannerError",
    "InvalidExecutionPlanningRequestError",
    "ExecutionPlanWorkflowMismatchError",
    "ExecutionPlanRunnabilityMismatchError",
    "ExecutionWave",
    "ExecutionPlan",
    "create_execution_plan",
    "execution_plan_snapshot",
    "explain_execution_planner_v4_5",
]
