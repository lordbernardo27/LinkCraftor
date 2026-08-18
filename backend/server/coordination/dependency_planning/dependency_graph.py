"""
LinkCraftor
Universal Coordination Framework

Phase 4.1 — Dependency Graph

Canonical responsibility
------------------------
Represent immutable, deterministic, workflow-scoped dependency topology.

This module owns:
- dependency nodes identified by canonical stage_id strings,
- directed dependency edges,
- prerequisite/dependent topology inspection,
- deterministic graph canonicalization,
- isolated-node representation,
- immutable snapshots and architecture evidence.

Canonical edge direction:
    prerequisite_stage_id -> dependent_stage_id

This module intentionally does NOT own:
- semantic dependency validity (Phase 4.2),
- self-dependency rejection (Phase 4.2),
- cycle detection (Phase 4.3),
- topological sorting (Phase 4.3/4.5),
- runnable-stage resolution (Phase 4.4),
- execution planning (Phase 4.5),
- Runtime dispatch or job execution (Phase 5),
- stage handoff (Phase 6),
- workflow persistence (Phase 8),
- recovery (Phase 9).

Phase 4.1 is structural topology only.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import (
    Any,
    Final,
    Iterable,
    Mapping,
    Sequence,
)


# =============================================================================
# 1. Canonical identity
# =============================================================================

DEPENDENCY_GRAPH_VERSION: Final[str] = (
    "dependency_graph_v4.1.0"
)

DEPENDENCY_GRAPH_SCHEMA_VERSION: Final[str] = (
    "dependency_graph_schema_v1"
)

DEPENDENCY_EDGE_FIELD_COUNT: Final[int] = 2
DEPENDENCY_GRAPH_FIELD_COUNT: Final[int] = 4


# =============================================================================
# 2. Errors
# =============================================================================

class DependencyGraphError(ValueError):
    """Base Phase 4.1 dependency-graph error."""


class InvalidWorkflowIdError(
    DependencyGraphError
):
    """workflow_id is not a non-empty canonical string."""


class InvalidDependencyStageIdError(
    DependencyGraphError
):
    """A dependency node/stage identifier is invalid."""


class InvalidDependencyEdgeError(
    DependencyGraphError
):
    """A dependency edge representation is invalid."""


# =============================================================================
# 3. Immutable helpers
# =============================================================================

def _require_non_empty_string(
    value: Any,
    *,
    field_name: str,
    error_type: type[DependencyGraphError],
) -> str:
    if not isinstance(
        value,
        str,
    ):
        raise error_type(
            f"{field_name} must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise error_type(
            f"{field_name} must not be empty."
        )

    return normalized


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
# 4. Canonical dependency edge
# =============================================================================

@dataclass(
    frozen=True,
    slots=True,
    order=True,
)
class DependencyEdge:
    """
    One directed dependency relation.

    Direction:
        prerequisite_stage_id -> dependent_stage_id

    Phase 4.1 deliberately allows a self-edge structurally.
    Whether that edge is valid belongs to Phase 4.2.
    """

    prerequisite_stage_id: str
    dependent_stage_id: str

    def __post_init__(
        self,
    ) -> None:
        prerequisite = _require_non_empty_string(
            self.prerequisite_stage_id,
            field_name="prerequisite_stage_id",
            error_type=InvalidDependencyStageIdError,
        )

        dependent = _require_non_empty_string(
            self.dependent_stage_id,
            field_name="dependent_stage_id",
            error_type=InvalidDependencyStageIdError,
        )

        object.__setattr__(
            self,
            "prerequisite_stage_id",
            prerequisite,
        )

        object.__setattr__(
            self,
            "dependent_stage_id",
            dependent,
        )

    def to_tuple(
        self,
    ) -> tuple[str, str]:
        return (
            self.prerequisite_stage_id,
            self.dependent_stage_id,
        )

    def to_dict(
        self,
    ) -> Mapping[str, str]:
        return MappingProxyType(
            {
                "prerequisite_stage_id":
                    self.prerequisite_stage_id,
                "dependent_stage_id":
                    self.dependent_stage_id,
            }
        )


# =============================================================================
# 5. Edge normalization
# =============================================================================

DependencyEdgeInput = (
    DependencyEdge
    | Sequence[str]
)


def _coerce_dependency_edge(
    value: DependencyEdgeInput,
) -> DependencyEdge:
    if isinstance(
        value,
        DependencyEdge,
    ):
        return value

    if isinstance(
        value,
        (str, bytes),
    ):
        raise InvalidDependencyEdgeError(
            "Dependency edge must not be a scalar string."
        )

    if not isinstance(
        value,
        Sequence,
    ):
        raise InvalidDependencyEdgeError(
            "Dependency edge must be DependencyEdge "
            "or a two-item sequence."
        )

    if len(value) != 2:
        raise InvalidDependencyEdgeError(
            "Dependency edge sequence must contain "
            "exactly two stage IDs."
        )

    return DependencyEdge(
        prerequisite_stage_id=value[0],
        dependent_stage_id=value[1],
    )


def _canonicalize_edges(
    edges: Iterable[DependencyEdgeInput],
) -> tuple[DependencyEdge, ...]:
    canonical = {
        _coerce_dependency_edge(
            edge
        )
        for edge
        in edges
    }

    return tuple(
        sorted(
            canonical,
            key=lambda edge: (
                edge.prerequisite_stage_id,
                edge.dependent_stage_id,
            ),
        )
    )


def _canonicalize_node_ids(
    node_ids: Iterable[str],
    edges: Iterable[DependencyEdge],
) -> tuple[str, ...]:
    canonical_nodes: set[str] = set()

    for node_id in node_ids:
        canonical_nodes.add(
            _require_non_empty_string(
                node_id,
                field_name="stage_id",
                error_type=InvalidDependencyStageIdError,
            )
        )

    for edge in edges:
        canonical_nodes.add(
            edge.prerequisite_stage_id
        )
        canonical_nodes.add(
            edge.dependent_stage_id
        )

    return tuple(
        sorted(
            canonical_nodes
        )
    )


# =============================================================================
# 6. Immutable dependency graph
# =============================================================================

@dataclass(
    frozen=True,
    slots=True,
)
class DependencyGraph:
    """
    Immutable workflow-scoped dependency topology.

    node_ids:
        Canonical lexical tuple of unique stage_id values.

    edges:
        Canonical lexical tuple of unique directed DependencyEdge objects.

    Edge endpoints are always present in node_ids.

    Structural self-edges and cycles are representable here intentionally.
    Their semantic treatment belongs to later Phase-4 components.
    """

    workflow_id: str
    node_ids: tuple[str, ...]
    edges: tuple[DependencyEdge, ...]
    graph_version: str = (
        DEPENDENCY_GRAPH_VERSION
    )

    def __post_init__(
        self,
    ) -> None:
        workflow_id = _require_non_empty_string(
            self.workflow_id,
            field_name="workflow_id",
            error_type=InvalidWorkflowIdError,
        )

        canonical_edges = _canonicalize_edges(
            self.edges
        )

        canonical_nodes = _canonicalize_node_ids(
            self.node_ids,
            canonical_edges,
        )

        if (
            self.graph_version
            != DEPENDENCY_GRAPH_VERSION
        ):
            raise DependencyGraphError(
                "graph_version must equal "
                f"{DEPENDENCY_GRAPH_VERSION!r}."
            )

        object.__setattr__(
            self,
            "workflow_id",
            workflow_id,
        )

        object.__setattr__(
            self,
            "node_ids",
            canonical_nodes,
        )

        object.__setattr__(
            self,
            "edges",
            canonical_edges,
        )


# =============================================================================
# 7. Graph construction
# =============================================================================

def create_dependency_graph(
    *,
    workflow_id: str,
    node_ids: Iterable[str] = (),
    edges: Iterable[DependencyEdgeInput] = (),
) -> DependencyGraph:
    """
    Create one canonical workflow-scoped dependency graph.

    Explicit node_ids may contain isolated nodes.

    Any stage referenced by an edge is automatically included in the
    canonical node set.

    Exact duplicate edges are canonicalized to one edge.
    """

    canonical_edges = _canonicalize_edges(
        edges
    )

    canonical_nodes = _canonicalize_node_ids(
        node_ids,
        canonical_edges,
    )

    return DependencyGraph(
        workflow_id=workflow_id,
        node_ids=canonical_nodes,
        edges=canonical_edges,
        graph_version=DEPENDENCY_GRAPH_VERSION,
    )


# =============================================================================
# 8. Structural inspection APIs
# =============================================================================

def dependency_nodes(
    graph: DependencyGraph,
) -> tuple[str, ...]:
    return graph.node_ids


def dependency_edges(
    graph: DependencyGraph,
) -> tuple[DependencyEdge, ...]:
    return graph.edges


def has_dependency_node(
    graph: DependencyGraph,
    stage_id: str,
) -> bool:
    normalized = _require_non_empty_string(
        stage_id,
        field_name="stage_id",
        error_type=InvalidDependencyStageIdError,
    )

    return normalized in graph.node_ids


def has_dependency_edge(
    graph: DependencyGraph,
    prerequisite_stage_id: str,
    dependent_stage_id: str,
) -> bool:
    candidate = DependencyEdge(
        prerequisite_stage_id=prerequisite_stage_id,
        dependent_stage_id=dependent_stage_id,
    )

    return candidate in graph.edges


def stage_prerequisites(
    graph: DependencyGraph,
    stage_id: str,
) -> tuple[str, ...]:
    normalized = _require_non_empty_string(
        stage_id,
        field_name="stage_id",
        error_type=InvalidDependencyStageIdError,
    )

    return tuple(
        edge.prerequisite_stage_id
        for edge
        in graph.edges
        if edge.dependent_stage_id
        == normalized
    )


def stage_dependents(
    graph: DependencyGraph,
    stage_id: str,
) -> tuple[str, ...]:
    normalized = _require_non_empty_string(
        stage_id,
        field_name="stage_id",
        error_type=InvalidDependencyStageIdError,
    )

    return tuple(
        edge.dependent_stage_id
        for edge
        in graph.edges
        if edge.prerequisite_stage_id
        == normalized
    )


def dependency_roots(
    graph: DependencyGraph,
) -> tuple[str, ...]:
    """
    Structural roots: nodes with no incoming dependency edge.

    This is not runnable-stage resolution.
    """

    dependent_nodes = {
        edge.dependent_stage_id
        for edge
        in graph.edges
    }

    return tuple(
        node_id
        for node_id
        in graph.node_ids
        if node_id
        not in dependent_nodes
    )


def dependency_leaves(
    graph: DependencyGraph,
) -> tuple[str, ...]:
    """
    Structural leaves: nodes with no outgoing dependency edge.

    This is not completion or execution planning.
    """

    prerequisite_nodes = {
        edge.prerequisite_stage_id
        for edge
        in graph.edges
    }

    return tuple(
        node_id
        for node_id
        in graph.node_ids
        if node_id
        not in prerequisite_nodes
    )


# =============================================================================
# 9. Immutable snapshot
# =============================================================================

def dependency_graph_snapshot(
    graph: DependencyGraph,
) -> Mapping[str, Any]:
    return _freeze(
        {
            "workflow_id":
                graph.workflow_id,

            "graph_version":
                graph.graph_version,

            "schema_version":
                DEPENDENCY_GRAPH_SCHEMA_VERSION,

            "node_count":
                len(
                    graph.node_ids
                ),

            "edge_count":
                len(
                    graph.edges
                ),

            "node_ids":
                graph.node_ids,

            "edges":
                tuple(
                    edge.to_tuple()
                    for edge
                    in graph.edges
                ),

            "roots":
                dependency_roots(
                    graph
                ),

            "leaves":
                dependency_leaves(
                    graph
                ),
        }
    )


# =============================================================================
# 10. Architecture evidence
# =============================================================================

def explain_dependency_graph_v4_1(
) -> Mapping[str, Any]:
    return _freeze(
        {
            "phase":
                "4.1",

            "component":
                "Dependency Graph",

            "version":
                DEPENDENCY_GRAPH_VERSION,

            "schema_version":
                DEPENDENCY_GRAPH_SCHEMA_VERSION,

            "edge_direction":
                (
                    "prerequisite_stage_id"
                    " -> "
                    "dependent_stage_id"
                ),

            "graph_scope":
                "workflow",

            "graph_identity":
                "workflow_id",

            "node_identity":
                "stage_id",

            "owns": (
                "immutable dependency topology",
                "workflow-scoped dependency graph representation",
                "canonical dependency node representation",
                "canonical directed dependency edge representation",
                "isolated node representation",
                "edge-endpoint node inference",
                "exact duplicate-edge canonicalization",
                "deterministic lexical node ordering",
                "deterministic lexical edge ordering",
                "prerequisite inspection",
                "dependent inspection",
                "structural root inspection",
                "structural leaf inspection",
                "immutable graph snapshot",
            ),

            "does_not_own": (
                "dependency semantic validation",
                "self-dependency rejection",
                "cycle detection",
                "topological sorting",
                "runnable-stage resolution",
                "execution planning",
                "Runtime Registration",
                "Runtime jobs",
                "Runtime dispatch",
                "business handler execution",
                "stage result handoff",
                "workflow persistence",
                "workflow recovery",
            ),

            "structural_rules": {
                "exact_duplicate_edges":
                    "canonicalize_to_one",

                "isolated_nodes":
                    "supported",

                "edge_endpoint_nodes":
                    "inferred_into_node_set",

                "self_edges":
                    "representable; Phase 4.2 owns validity",

                "cycles":
                    "representable; Phase 4.3 owns detection",

                "node_order":
                    "lexical",

                "edge_order":
                    "lexical",
            },

            "future_authority": {
                "4.2":
                    "Dependency Validation",

                "4.3":
                    "Cycle Detection",

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

                "runtime_execution":
                    False,

                "workflow_mutation":
                    False,

                "persistence":
                    False,
            },
        }
    )


__all__ = [
    "DEPENDENCY_GRAPH_VERSION",
    "DEPENDENCY_GRAPH_SCHEMA_VERSION",
    "DEPENDENCY_EDGE_FIELD_COUNT",
    "DEPENDENCY_GRAPH_FIELD_COUNT",
    "DependencyGraphError",
    "InvalidWorkflowIdError",
    "InvalidDependencyStageIdError",
    "InvalidDependencyEdgeError",
    "DependencyEdge",
    "DependencyGraph",
    "create_dependency_graph",
    "dependency_nodes",
    "dependency_edges",
    "has_dependency_node",
    "has_dependency_edge",
    "stage_prerequisites",
    "stage_dependents",
    "dependency_roots",
    "dependency_leaves",
    "dependency_graph_snapshot",
    "explain_dependency_graph_v4_1",
]
