"""
LinkCraftor
Universal Coordination Framework

Phase 4.3 — Cycle Detection

Canonical responsibility
------------------------
Detect directed dependency cycles in a DependencyGraph that has already
passed frozen Phase 4.2 Dependency Validation.

Phase 4.3 owns:
- deterministic directed-cycle detection,
- canonical cycle-witness evidence,
- acyclic/cyclic result,
- require-acyclic guard,
- immutable cycle-detection snapshots.

Phase 4.3 intentionally does NOT own:
- dependency graph construction (Phase 4.1),
- dependency semantic validation (Phase 4.2),
- self-dependency validation (Phase 4.2),
- runnable-stage resolution (Phase 4.4),
- execution ordering/planning (Phase 4.5),
- planning certification (Phase 4.6),
- Runtime execution (Phase 5),
- stage handoff (Phase 6),
- persistence (Phase 8),
- recovery (Phase 9).

Important:
Phase 4.3 returns deterministic cycle witnesses. It does not attempt
exhaustive enumeration of every possible simple cycle in a graph.
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
    stage_dependents,
)

from backend.server.coordination.dependency_planning.dependency_validation import (
    DEPENDENCY_VALIDATION_VERSION,
    DependencyGraphValidationFailedError,
    require_valid_dependency_graph,
)


# =============================================================================
# 1. Canonical identity
# =============================================================================

CYCLE_DETECTION_VERSION: Final[str] = (
    "cycle_detection_v4.3.0"
)

CYCLE_DETECTION_SCHEMA_VERSION: Final[str] = (
    "cycle_detection_schema_v1"
)

CYCLE_DETECTION_RESULT_FIELD_COUNT: Final[int] = 8


# =============================================================================
# 2. Errors
# =============================================================================

class CycleDetectionError(
    ValueError
):
    """Base Phase 4.3 cycle-detection error."""


class InvalidCycleDetectionRequestError(
    CycleDetectionError
):
    """Input is not a Phase 4.1 DependencyGraph."""


class CyclicDependencyGraphError(
    CycleDetectionError
):
    """Raised when require_acyclic_dependency_graph finds a cycle."""

    def __init__(
        self,
        result: "CycleDetectionResult",
    ) -> None:
        self.result = result

        super().__init__(
            "Dependency graph contains "
            f"{result.cycle_witness_count} "
            "cycle witness(es)."
        )


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
# 4. Canonical cycle witness
# =============================================================================

@dataclass(
    frozen=True,
    slots=True,
    order=True,
)
class CycleWitness:
    """
    One canonical directed cycle witness.

    stage_ids is a closed path.

    Example:
        ("a", "b", "c", "a")
    """

    stage_ids: tuple[str, ...]

    def __post_init__(
        self,
    ) -> None:
        if len(
            self.stage_ids
        ) < 3:
            raise CycleDetectionError(
                "Cycle witness must contain at least "
                "two distinct stages plus the closing stage."
            )

        if (
            self.stage_ids[0]
            != self.stage_ids[-1]
        ):
            raise CycleDetectionError(
                "Cycle witness must be a closed path."
            )

    @property
    def edge_count(
        self,
    ) -> int:
        return (
            len(
                self.stage_ids
            )
            - 1
        )

    def to_dict(
        self,
    ) -> Mapping[str, Any]:
        return MappingProxyType(
            {
                "stage_ids":
                    self.stage_ids,

                "edge_count":
                    self.edge_count,
            }
        )


# =============================================================================
# 5. Immutable detection result
# =============================================================================

@dataclass(
    frozen=True,
    slots=True,
)
class CycleDetectionResult:
    is_acyclic: bool
    has_cycle: bool
    node_count: int
    edge_count: int
    cycle_witness_count: int
    cycle_witnesses: tuple[
        CycleWitness,
        ...,
    ]
    graph_version: str
    detection_version: str

    def to_dict(
        self,
    ) -> Mapping[str, Any]:
        return _freeze(
            {
                "is_acyclic":
                    self.is_acyclic,

                "has_cycle":
                    self.has_cycle,

                "node_count":
                    self.node_count,

                "edge_count":
                    self.edge_count,

                "cycle_witness_count":
                    self.cycle_witness_count,

                "cycle_witnesses":
                    tuple(
                        witness.to_dict()
                        for witness
                        in self.cycle_witnesses
                    ),

                "graph_version":
                    self.graph_version,

                "detection_version":
                    self.detection_version,
            }
        )


# =============================================================================
# 6. Cycle witness canonicalization
# =============================================================================

def _canonicalize_cycle_path(
    path: tuple[str, ...],
) -> tuple[str, ...]:
    """
    Canonicalize one closed directed cycle path.

    Direction is preserved.
    Only rotation is canonicalized.

    Example:
        b -> c -> a -> b

    becomes:
        a -> b -> c -> a
    """

    if len(
        path
    ) < 3:
        raise CycleDetectionError(
            "Cycle path is too short."
        )

    if path[0] != path[-1]:
        raise CycleDetectionError(
            "Cycle path must be closed."
        )

    open_cycle = path[:-1]

    rotations = tuple(
        open_cycle[index:]
        + open_cycle[:index]
        for index
        in range(
            len(
                open_cycle
            )
        )
    )

    canonical_open = min(
        rotations
    )

    return (
        canonical_open
        + (
            canonical_open[0],
        )
    )


# =============================================================================
# 7. Deterministic cycle detection
# =============================================================================

def detect_dependency_cycles(
    graph: DependencyGraph,
) -> CycleDetectionResult:
    """
    Detect directed cycles after enforcing frozen Phase 4.2 validity.

    Uses deterministic lexical DFS with an explicit active traversal stack.

    Returns canonical cycle witnesses rather than an exhaustive enumeration
    of every mathematically possible simple cycle.
    """

    if not isinstance(
        graph,
        DependencyGraph,
    ):
        raise InvalidCycleDetectionRequestError(
            "graph must be a Phase 4.1 DependencyGraph."
        )

    # Phase 4.2 owns semantic validity and self-dependency rejection.
    require_valid_dependency_graph(
        graph
    )

    WHITE = 0
    GRAY = 1
    BLACK = 2

    state = {
        node_id: WHITE
        for node_id
        in graph.node_ids
    }

    active_stack: list[str] = []

    active_index: dict[
        str,
        int,
    ] = {}

    witnesses: set[
        tuple[str, ...]
    ] = set()


    def visit_iterative(
        start_node_id: str,
    ) -> None:
        """
        Deterministic iterative DFS.

        This preserves the previous recursive DFS semantics while avoiding
        dependence on Python's interpreter recursion limit.

        Each traversal frame stores:
        - current node_id,
        - the node's deterministic dependent tuple,
        - the next dependent index to inspect.

        active_stack and active_index retain exactly the same role they had
        in the recursive implementation for canonical back-edge witnesses.
        """

        state[
            start_node_id
        ] = GRAY

        active_index[
            start_node_id
        ] = len(
            active_stack
        )

        active_stack.append(
            start_node_id
        )

        traversal_stack: list[
            tuple[
                str,
                tuple[str, ...],
                int,
            ]
        ] = [
            (
                start_node_id,
                tuple(
                    stage_dependents(
                        graph,
                        start_node_id,
                    )
                ),
                0,
            )
        ]

        while traversal_stack:
            (
                node_id,
                dependents,
                next_index,
            ) = traversal_stack[
                -1
            ]

            if next_index >= len(
                dependents
            ):
                traversal_stack.pop()

                active_stack.pop()

                active_index.pop(
                    node_id,
                    None,
                )

                state[
                    node_id
                ] = BLACK

                continue

            dependent = dependents[
                next_index
            ]

            traversal_stack[
                -1
            ] = (
                node_id,
                dependents,
                next_index + 1,
            )

            dependent_state = state[
                dependent
            ]

            if dependent_state == WHITE:
                state[
                    dependent
                ] = GRAY

                active_index[
                    dependent
                ] = len(
                    active_stack
                )

                active_stack.append(
                    dependent
                )

                traversal_stack.append(
                    (
                        dependent,
                        tuple(
                            stage_dependents(
                                graph,
                                dependent,
                            )
                        ),
                        0,
                    )
                )

            elif dependent_state == GRAY:
                start = active_index[
                    dependent
                ]

                raw_cycle = tuple(
                    active_stack[
                        start:
                    ]
                ) + (
                    dependent,
                )

                witnesses.add(
                    _canonicalize_cycle_path(
                        raw_cycle
                    )
                )


    for node_id in graph.node_ids:
        if state[
            node_id
        ] == WHITE:
            visit_iterative(
                node_id
            )


    canonical_witnesses = tuple(
        CycleWitness(
            stage_ids=path
        )
        for path
        in sorted(
            witnesses
        )
    )

    has_cycle = bool(
        canonical_witnesses
    )

    return CycleDetectionResult(
        is_acyclic=(
            not has_cycle
        ),
        has_cycle=has_cycle,
        node_count=len(
            graph.node_ids
        ),
        edge_count=len(
            graph.edges
        ),
        cycle_witness_count=len(
            canonical_witnesses
        ),
        cycle_witnesses=canonical_witnesses,
        graph_version=graph.graph_version,
        detection_version=(
            CYCLE_DETECTION_VERSION
        ),
    )


# =============================================================================
# 8. Require-acyclic guard
# =============================================================================

def require_acyclic_dependency_graph(
    graph: DependencyGraph,
) -> CycleDetectionResult:
    result = detect_dependency_cycles(
        graph
    )

    if result.has_cycle:
        raise CyclicDependencyGraphError(
            result
        )

    return result


# =============================================================================
# 9. Snapshot
# =============================================================================

def cycle_detection_snapshot(
    graph: DependencyGraph,
) -> Mapping[str, Any]:
    result = detect_dependency_cycles(
        graph
    )

    return _freeze(
        {
            "detection_version":
                CYCLE_DETECTION_VERSION,

            "schema_version":
                CYCLE_DETECTION_SCHEMA_VERSION,

            "graph_version":
                result.graph_version,

            "is_acyclic":
                result.is_acyclic,

            "has_cycle":
                result.has_cycle,

            "node_count":
                result.node_count,

            "edge_count":
                result.edge_count,

            "cycle_witness_count":
                result.cycle_witness_count,

            "cycle_witnesses":
                tuple(
                    witness.to_dict()
                    for witness
                    in result.cycle_witnesses
                ),
        }
    )


# =============================================================================
# 10. Architecture evidence
# =============================================================================

def explain_cycle_detection_v4_3(
) -> Mapping[str, Any]:
    return _freeze(
        {
            "phase":
                "4.3",

            "component":
                "Cycle Detection",

            "version":
                CYCLE_DETECTION_VERSION,

            "schema_version":
                CYCLE_DETECTION_SCHEMA_VERSION,

            "input_authority":
                "Phase 4.1 DependencyGraph",

            "validation_precondition":
                "Phase 4.2 Dependency Validation",

            "upstream_versions": {
                "4.1":
                    DEPENDENCY_GRAPH_VERSION,

                "4.2":
                    DEPENDENCY_VALIDATION_VERSION,
            },

            "algorithm": {
                "family":
                    "deterministic DFS active-stack",

                "node_order":
                    "lexical",

                "dependent_order":
                    "lexical",

                "evidence":
                    "canonical cycle witnesses",

                "exhaustive_simple_cycle_enumeration":
                    False,
            },

            "owns": (
                "directed dependency cycle detection",
                "acyclic/cyclic determination",
                "deterministic cycle witness evidence",
                "require-acyclic dependency graph guard",
                "immutable cycle detection snapshot",
            ),

            "does_not_own": (
                "dependency graph construction",
                "dependency semantic validation",
                "self-dependency validation",
                "topological execution ordering",
                "runnable-stage resolution",
                "execution planning",
                "planning certification",
                "Runtime Registration",
                "Runtime jobs",
                "Runtime dispatch",
                "business handler execution",
                "stage result handoff",
                "workflow persistence",
                "workflow recovery",
            ),

            "graph_semantics": {
                "empty_graph":
                    "acyclic",

                "isolated_nodes":
                    "acyclic",

                "acyclic_chain":
                    "acyclic",

                "branch_join_without_back_edge":
                    "acyclic",

                "two_node_cycle":
                    "cyclic",

                "multi_node_cycle":
                    "cyclic",

                "self_dependency":
                    (
                        "invalid upstream; "
                        "Phase 4.2 owns rejection"
                    ),
            },

            "future_authority": {
                "4.4":
                    "Runnable Stage Resolver",

                "4.5":
                    "Execution Planner",

                "4.6":
                    "Planning Certification",
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

                "runtime_execution":
                    False,

                "persistence":
                    False,
            },
        }
    )


__all__ = [
    "CYCLE_DETECTION_VERSION",
    "CYCLE_DETECTION_SCHEMA_VERSION",
    "CYCLE_DETECTION_RESULT_FIELD_COUNT",
    "CycleDetectionError",
    "InvalidCycleDetectionRequestError",
    "CyclicDependencyGraphError",
    "CycleWitness",
    "CycleDetectionResult",
    "detect_dependency_cycles",
    "require_acyclic_dependency_graph",
    "cycle_detection_snapshot",
    "explain_cycle_detection_v4_3",
]
