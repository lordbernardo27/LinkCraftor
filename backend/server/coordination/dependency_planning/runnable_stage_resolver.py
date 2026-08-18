"""
LinkCraftor
Universal Coordination Framework

Phase 4.4 — Runnable Stage Resolver

Canonical responsibility
------------------------
Resolve which workflow stages are runnable now by combining:

- frozen Phase 4.1 dependency topology,
- frozen Phase 4.2 dependency validity,
- frozen Phase 4.3 acyclic topology,
- an immutable projection of workflow stage-progress state.

Phase 4.4 owns:
- deterministic runnable-stage resolution,
- blocked-stage prerequisite evidence,
- workflow/graph identity validation,
- base prerequisite-satisfaction semantics,
- immutable runnability results and snapshots.

Base Phase 4.4 prerequisite rule:
- COMPLETED satisfies a prerequisite.
- FAILED does not satisfy a prerequisite.
- SKIPPED does not satisfy a prerequisite.

Advanced skip semantics belong to Phase 7.7 and must not be invented here.

Phase 4.4 intentionally does NOT own:
- dependency graph construction (Phase 4.1),
- dependency semantic validation (Phase 4.2),
- cycle detection (Phase 4.3),
- execution ordering/planning (Phase 4.5),
- planning certification (Phase 4.6),
- Runtime dispatch/execution (Phase 5),
- stage handoff (Phase 6),
- fan-out/fan-in or advanced skip policy (Phase 7),
- persistence/checkpointing (Phase 8),
- recovery policy (Phase 9).
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
    stage_prerequisites,
)

from backend.server.coordination.dependency_planning.dependency_validation import (
    DEPENDENCY_VALIDATION_VERSION,
)

from backend.server.coordination.dependency_planning.cycle_detection import (
    CYCLE_DETECTION_VERSION,
    require_acyclic_dependency_graph,
)


# =============================================================================
# 1. Canonical identity
# =============================================================================

RUNNABLE_STAGE_RESOLVER_VERSION: Final[str] = (
    "runnable_stage_resolver_v4.4.0"
)

RUNNABLE_STAGE_RESOLVER_SCHEMA_VERSION: Final[str] = (
    "runnable_stage_resolver_schema_v1"
)

RUNNABLE_STAGE_STATE_FIELD_COUNT: Final[int] = 6

STAGE_RUNNABILITY_EVIDENCE_FIELD_COUNT: Final[int] = 6

RUNNABLE_STAGE_RESOLUTION_FIELD_COUNT: Final[int] = 8


# =============================================================================
# 2. Errors
# =============================================================================

class RunnableStageResolverError(
    ValueError
):
    """Base Phase 4.4 runnable-stage resolution error."""


class InvalidRunnableStageStateError(
    RunnableStageResolverError
):
    """Workflow stage-progress projection is invalid."""


class WorkflowGraphIdentityMismatchError(
    RunnableStageResolverError
):
    """Workflow progress state does not belong to the supplied graph."""


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
# 4. Canonical identity helper
# =============================================================================

def _canonical_stage_id(
    value: str,
    *,
    field_name: str,
) -> str:
    if not isinstance(
        value,
        str,
    ):
        raise InvalidRunnableStageStateError(
            f"{field_name} must contain stage_id strings."
        )

    if not value:
        raise InvalidRunnableStageStateError(
            f"{field_name} must not contain empty stage_id."
        )

    if value != value.strip():
        raise InvalidRunnableStageStateError(
            f"{field_name} stage_id must be canonical."
        )

    return value


def _canonical_stage_tuple(
    values: tuple[str, ...] | list[str] | set[str],
    *,
    field_name: str,
) -> tuple[str, ...]:
    if not isinstance(
        values,
        (
            tuple,
            list,
            set,
            frozenset,
        ),
    ):
        raise InvalidRunnableStageStateError(
            f"{field_name} must be a stage-id collection."
        )

    canonical = tuple(
        sorted(
            {
                _canonical_stage_id(
                    value,
                    field_name=field_name,
                )
                for value
                in values
            }
        )
    )

    return canonical


# =============================================================================
# 5. Immutable workflow progress projection
# =============================================================================

@dataclass(
    frozen=True,
    slots=True,
)
class RunnableStageState:
    """
    Narrow immutable projection of the frozen Workflow Contract.

    This is not a replacement workflow contract.
    It exposes only the fields required by Phase 4.4.
    """

    workflow_id: str
    current_stage_id: str | None
    completed_stage_ids: tuple[str, ...]
    pending_stage_ids: tuple[str, ...]
    failed_stage_ids: tuple[str, ...]
    skipped_stage_ids: tuple[str, ...]

    def to_dict(
        self,
    ) -> Mapping[str, Any]:
        return MappingProxyType(
            {
                "workflow_id":
                    self.workflow_id,

                "current_stage_id":
                    self.current_stage_id,

                "completed_stage_ids":
                    self.completed_stage_ids,

                "pending_stage_ids":
                    self.pending_stage_ids,

                "failed_stage_ids":
                    self.failed_stage_ids,

                "skipped_stage_ids":
                    self.skipped_stage_ids,
            }
        )


def create_runnable_stage_state(
    *,
    workflow_id: str,
    current_stage_id: str | None = None,
    completed_stage_ids: tuple[str, ...] | list[str] | set[str] = (),
    pending_stage_ids: tuple[str, ...] | list[str] | set[str] = (),
    failed_stage_ids: tuple[str, ...] | list[str] | set[str] = (),
    skipped_stage_ids: tuple[str, ...] | list[str] | set[str] = (),
) -> RunnableStageState:
    if not isinstance(
        workflow_id,
        str,
    ):
        raise InvalidRunnableStageStateError(
            "workflow_id must be a string."
        )

    if (
        not workflow_id
        or workflow_id
        != workflow_id.strip()
    ):
        raise InvalidRunnableStageStateError(
            "workflow_id must be canonical and non-empty."
        )

    if current_stage_id is not None:
        current_stage_id = _canonical_stage_id(
            current_stage_id,
            field_name="current_stage_id",
        )

    completed = _canonical_stage_tuple(
        completed_stage_ids,
        field_name="completed_stage_ids",
    )

    pending = _canonical_stage_tuple(
        pending_stage_ids,
        field_name="pending_stage_ids",
    )

    failed = _canonical_stage_tuple(
        failed_stage_ids,
        field_name="failed_stage_ids",
    )

    skipped = _canonical_stage_tuple(
        skipped_stage_ids,
        field_name="skipped_stage_ids",
    )

    state_sets = (
        ("completed", set(completed)),
        ("pending", set(pending)),
        ("failed", set(failed)),
        ("skipped", set(skipped)),
    )

    for index, (
        left_name,
        left_values,
    ) in enumerate(
        state_sets
    ):
        for (
            right_name,
            right_values,
        ) in state_sets[
            index + 1:
        ]:
            overlap = (
                left_values
                & right_values
            )

            if overlap:
                raise InvalidRunnableStageStateError(
                    "Workflow stage-state collections "
                    "must be disjoint: "
                    f"{left_name} overlaps {right_name}: "
                    f"{tuple(sorted(overlap))!r}"
                )

    return RunnableStageState(
        workflow_id=workflow_id,
        current_stage_id=current_stage_id,
        completed_stage_ids=completed,
        pending_stage_ids=pending,
        failed_stage_ids=failed,
        skipped_stage_ids=skipped,
    )


# =============================================================================
# 6. Per-stage immutable evidence
# =============================================================================

@dataclass(
    frozen=True,
    slots=True,
    order=True,
)
class StageRunnabilityEvidence:
    stage_id: str
    is_runnable: bool
    prerequisite_stage_ids: tuple[str, ...]
    satisfied_prerequisite_stage_ids: tuple[str, ...]
    unsatisfied_prerequisite_stage_ids: tuple[str, ...]
    reason: str

    def to_dict(
        self,
    ) -> Mapping[str, Any]:
        return MappingProxyType(
            {
                "stage_id":
                    self.stage_id,

                "is_runnable":
                    self.is_runnable,

                "prerequisite_stage_ids":
                    self.prerequisite_stage_ids,

                "satisfied_prerequisite_stage_ids":
                    self.satisfied_prerequisite_stage_ids,

                "unsatisfied_prerequisite_stage_ids":
                    self.unsatisfied_prerequisite_stage_ids,

                "reason":
                    self.reason,
            }
        )


# =============================================================================
# 7. Immutable resolution result
# =============================================================================

@dataclass(
    frozen=True,
    slots=True,
)
class RunnableStageResolution:
    workflow_id: str
    runnable_stage_ids: tuple[str, ...]
    blocked_stage_ids: tuple[str, ...]
    untracked_stage_ids: tuple[str, ...]
    evidence: tuple[
        StageRunnabilityEvidence,
        ...,
    ]
    graph_version: str
    cycle_detection_version: str
    resolver_version: str

    def to_dict(
        self,
    ) -> Mapping[str, Any]:
        return _freeze(
            {
                "workflow_id":
                    self.workflow_id,

                "runnable_stage_ids":
                    self.runnable_stage_ids,

                "blocked_stage_ids":
                    self.blocked_stage_ids,

                "untracked_stage_ids":
                    self.untracked_stage_ids,

                "evidence":
                    tuple(
                        item.to_dict()
                        for item
                        in self.evidence
                    ),

                "graph_version":
                    self.graph_version,

                "cycle_detection_version":
                    self.cycle_detection_version,

                "resolver_version":
                    self.resolver_version,
            }
        )


# =============================================================================
# 8. State/graph validation
# =============================================================================

def _validate_state_against_graph(
    graph: DependencyGraph,
    state: RunnableStageState,
) -> None:
    if not isinstance(
        state,
        RunnableStageState,
    ):
        raise InvalidRunnableStageStateError(
            "state must be RunnableStageState."
        )

    if state.workflow_id != graph.workflow_id:
        raise WorkflowGraphIdentityMismatchError(
            "Runnable stage state workflow_id must match "
            "DependencyGraph workflow_id."
        )

    graph_nodes = set(
        graph.node_ids
    )

    state_ids = set(
        state.completed_stage_ids
    ) | set(
        state.pending_stage_ids
    ) | set(
        state.failed_stage_ids
    ) | set(
        state.skipped_stage_ids
    )

    if state.current_stage_id is not None:
        state_ids.add(
            state.current_stage_id
        )

    unknown = (
        state_ids
        - graph_nodes
    )

    if unknown:
        raise InvalidRunnableStageStateError(
            "Workflow stage state references stage IDs "
            "outside DependencyGraph: "
            f"{tuple(sorted(unknown))!r}"
        )


# =============================================================================
# 9. Runnable-stage resolution
# =============================================================================

def resolve_runnable_stages(
    graph: DependencyGraph,
    state: RunnableStageState,
) -> RunnableStageResolution:
    """
    Resolve pending stages whose direct prerequisites are all completed.

    Phase 4.3 enforces both:
    - frozen 4.2 semantic graph validity,
    - frozen 4.3 acyclicity.

    No execution order is produced.
    """

    if not isinstance(
        graph,
        DependencyGraph,
    ):
        raise RunnableStageResolverError(
            "graph must be a Phase 4.1 DependencyGraph."
        )

    # Includes frozen Phase 4.2 validation.
    require_acyclic_dependency_graph(
        graph
    )

    _validate_state_against_graph(
        graph,
        state,
    )

    completed = set(
        state.completed_stage_ids
    )

    pending = set(
        state.pending_stage_ids
    )

    tracked = (
        completed
        | pending
        | set(
            state.failed_stage_ids
        )
        | set(
            state.skipped_stage_ids
        )
    )

    if state.current_stage_id is not None:
        tracked.add(
            state.current_stage_id
        )

    untracked = tuple(
        sorted(
            set(
                graph.node_ids
            )
            - tracked
        )
    )

    runnable: list[str] = []
    blocked: list[str] = []

    evidence: list[
        StageRunnabilityEvidence
    ] = []

    for stage_id in sorted(
        pending
    ):
        prerequisites = stage_prerequisites(
            graph,
            stage_id,
        )

        satisfied = tuple(
            prerequisite
            for prerequisite
            in prerequisites
            if prerequisite
            in completed
        )

        unsatisfied = tuple(
            prerequisite
            for prerequisite
            in prerequisites
            if prerequisite
            not in completed
        )

        if (
            state.current_stage_id
            is not None
            and stage_id
            == state.current_stage_id
        ):
            is_runnable = False
            reason = (
                "current_stage_not_runnable"
            )

        elif unsatisfied:
            is_runnable = False
            reason = (
                "prerequisites_incomplete"
            )

        else:
            is_runnable = True

            if prerequisites:
                reason = (
                    "all_prerequisites_completed"
                )
            else:
                reason = (
                    "no_prerequisites"
                )

        if is_runnable:
            runnable.append(
                stage_id
            )
        else:
            blocked.append(
                stage_id
            )

        evidence.append(
            StageRunnabilityEvidence(
                stage_id=stage_id,
                is_runnable=is_runnable,
                prerequisite_stage_ids=prerequisites,
                satisfied_prerequisite_stage_ids=satisfied,
                unsatisfied_prerequisite_stage_ids=unsatisfied,
                reason=reason,
            )
        )

    return RunnableStageResolution(
        workflow_id=state.workflow_id,
        runnable_stage_ids=tuple(
            runnable
        ),
        blocked_stage_ids=tuple(
            blocked
        ),
        untracked_stage_ids=untracked,
        evidence=tuple(
            evidence
        ),
        graph_version=graph.graph_version,
        cycle_detection_version=(
            CYCLE_DETECTION_VERSION
        ),
        resolver_version=(
            RUNNABLE_STAGE_RESOLVER_VERSION
        ),
    )


# =============================================================================
# 10. Snapshot
# =============================================================================

def runnable_stage_resolution_snapshot(
    graph: DependencyGraph,
    state: RunnableStageState,
) -> Mapping[str, Any]:
    result = resolve_runnable_stages(
        graph,
        state,
    )

    return _freeze(
        {
            "resolver_version":
                RUNNABLE_STAGE_RESOLVER_VERSION,

            "schema_version":
                RUNNABLE_STAGE_RESOLVER_SCHEMA_VERSION,

            "workflow_id":
                result.workflow_id,

            "graph_version":
                result.graph_version,

            "cycle_detection_version":
                result.cycle_detection_version,

            "runnable_stage_ids":
                result.runnable_stage_ids,

            "blocked_stage_ids":
                result.blocked_stage_ids,

            "untracked_stage_ids":
                result.untracked_stage_ids,

            "evidence":
                tuple(
                    item.to_dict()
                    for item
                    in result.evidence
                ),
        }
    )


# =============================================================================
# 11. Architecture evidence
# =============================================================================

def explain_runnable_stage_resolver_v4_4(
) -> Mapping[str, Any]:
    return _freeze(
        {
            "phase":
                "4.4",

            "component":
                "Runnable Stage Resolver",

            "version":
                RUNNABLE_STAGE_RESOLVER_VERSION,

            "schema_version":
                RUNNABLE_STAGE_RESOLVER_SCHEMA_VERSION,

            "topology_authority":
                "Phase 4.1 DependencyGraph",

            "validation_precondition":
                "Phase 4.2 Dependency Validation",

            "acyclic_precondition":
                "Phase 4.3 Cycle Detection",

            "workflow_progress_authority":
                (
                    "immutable projection of frozen "
                    "Universal Workflow Contract"
                ),

            "upstream_versions": {
                "4.1":
                    DEPENDENCY_GRAPH_VERSION,

                "4.2":
                    DEPENDENCY_VALIDATION_VERSION,

                "4.3":
                    CYCLE_DETECTION_VERSION,
            },

            "candidate_semantics": {
                "candidate_universe":
                    "pending stages within graph.node_ids",

                "completed_stage":
                    "not runnable",

                "failed_stage":
                    "not runnable",

                "skipped_stage":
                    "not runnable",

                "current_stage":
                    "not runnable",

                "untracked_graph_node":
                    "not runnable",

                "root_stage":
                    "runnable when pending and not current",

                "isolated_stage":
                    "runnable when pending and not current",
            },

            "prerequisite_semantics": {
                "completed":
                    "satisfied",

                "failed":
                    "unsatisfied",

                "skipped":
                    (
                        "unsatisfied in base Phase 4.4; "
                        "advanced Skip Semantics belong to Phase 7.7"
                    ),

                "all_direct_prerequisites_completed":
                    "runnable",

                "any_direct_prerequisite_not_completed":
                    "blocked",
            },

            "result_semantics": {
                "runnable_stage_ids":
                    "lexically ordered",

                "blocked_stage_ids":
                    "lexically ordered",

                "evidence":
                    "one entry per pending stage",

                "execution_order":
                    "not produced",
            },

            "owns": (
                "runnable-stage resolution",
                "base prerequisite satisfaction",
                "blocked-stage prerequisite evidence",
                "workflow/graph identity validation",
                "deterministic runnability result",
            ),

            "does_not_own": (
                "dependency graph construction",
                "dependency semantic validation",
                "cycle detection",
                "execution ordering",
                "execution planning",
                "planning certification",
                "Runtime Registration",
                "Runtime jobs",
                "Runtime dispatch",
                "business handler execution",
                "stage result handoff",
                "fan-out/fan-in policy",
                "advanced skip semantics",
                "workflow persistence",
                "workflow recovery",
            ),

            "future_authority": {
                "4.5":
                    "Execution Planner",

                "4.6":
                    "Planning Certification",

                "7.7":
                    "Skip Semantics",
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

                "workflow_mutation":
                    False,

                "runtime_execution":
                    False,

                "persistence":
                    False,
            },
        }
    )


__all__ = [
    "RUNNABLE_STAGE_RESOLVER_VERSION",
    "RUNNABLE_STAGE_RESOLVER_SCHEMA_VERSION",
    "RUNNABLE_STAGE_STATE_FIELD_COUNT",
    "STAGE_RUNNABILITY_EVIDENCE_FIELD_COUNT",
    "RUNNABLE_STAGE_RESOLUTION_FIELD_COUNT",
    "RunnableStageResolverError",
    "InvalidRunnableStageStateError",
    "WorkflowGraphIdentityMismatchError",
    "RunnableStageState",
    "StageRunnabilityEvidence",
    "RunnableStageResolution",
    "create_runnable_stage_state",
    "resolve_runnable_stages",
    "runnable_stage_resolution_snapshot",
    "explain_runnable_stage_resolver_v4_4",
]
