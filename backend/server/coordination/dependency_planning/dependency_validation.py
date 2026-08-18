"""
LinkCraftor
Universal Coordination Framework

Phase 4.2 — Dependency Validation

Canonical responsibility
------------------------
Perform deterministic semantic validation of a frozen Phase 4.1
DependencyGraph without executing, planning, persisting, or mutating anything.

Phase 4.2 owns:
- dependency-graph semantic validity,
- canonical graph invariant verification,
- self-dependency rejection,
- deterministic validation evidence,
- immutable validation result,
- require-valid guard.

Phase 4.2 intentionally does NOT own:
- dependency graph construction (Phase 4.1),
- cycle detection (Phase 4.3),
- topological sorting (Phase 4.3 / 4.5),
- runnable-stage resolution (Phase 4.4),
- execution planning (Phase 4.5),
- planning certification (Phase 4.6),
- Runtime execution (Phase 5),
- stage handoff (Phase 6),
- persistence (Phase 8),
- recovery (Phase 9).

A cyclic graph without a self-dependency remains valid at Phase 4.2.
Cycle status is determined only by Phase 4.3.
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
    DependencyEdge,
    DependencyGraph,
)


# =============================================================================
# 1. Canonical identity
# =============================================================================

DEPENDENCY_VALIDATION_VERSION: Final[str] = (
    "dependency_validation_v4.2.0"
)

DEPENDENCY_VALIDATION_SCHEMA_VERSION: Final[str] = (
    "dependency_validation_schema_v1"
)

DEPENDENCY_VALIDATION_RESULT_FIELD_COUNT: Final[int] = 10

SELF_DEPENDENCY_VIOLATION_CODE: Final[str] = (
    "self_dependency_prohibited"
)

GRAPH_INVARIANT_VIOLATION_CODE: Final[str] = (
    "dependency_graph_invariant_violation"
)


# =============================================================================
# 2. Errors
# =============================================================================

class DependencyValidationError(
    ValueError
):
    """Base Phase 4.2 dependency-validation error."""


class InvalidDependencyValidationRequestError(
    DependencyValidationError
):
    """Validation input is not a canonical Phase 4.1 DependencyGraph."""


class DependencyGraphValidationFailedError(
    DependencyValidationError
):
    """Raised by require_valid_dependency_graph for an invalid graph."""

    def __init__(
        self,
        result: "DependencyValidationResult",
    ) -> None:
        self.result = result

        codes = tuple(
            violation.code
            for violation
            in result.violations
        )

        super().__init__(
            "Dependency graph validation failed: "
            + ", ".join(
                codes
            )
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
# 4. Canonical violation evidence
# =============================================================================

@dataclass(
    frozen=True,
    slots=True,
    order=True,
)
class DependencyValidationViolation:
    code: str
    message: str
    prerequisite_stage_id: str | None = None
    dependent_stage_id: str | None = None

    def to_dict(
        self,
    ) -> Mapping[str, Any]:
        return MappingProxyType(
            {
                "code":
                    self.code,

                "message":
                    self.message,

                "prerequisite_stage_id":
                    self.prerequisite_stage_id,

                "dependent_stage_id":
                    self.dependent_stage_id,
            }
        )


# =============================================================================
# 5. Immutable validation result
# =============================================================================

@dataclass(
    frozen=True,
    slots=True,
)
class DependencyValidationResult:
    is_valid: bool
    checks_run: int
    checks_passed: int
    checks_failed: int
    node_count: int
    edge_count: int
    self_dependency_count: int
    violations: tuple[
        DependencyValidationViolation,
        ...,
    ]
    graph_version: str
    validation_version: str

    def to_dict(
        self,
    ) -> Mapping[str, Any]:
        return _freeze(
            {
                "is_valid":
                    self.is_valid,

                "checks_run":
                    self.checks_run,

                "checks_passed":
                    self.checks_passed,

                "checks_failed":
                    self.checks_failed,

                "node_count":
                    self.node_count,

                "edge_count":
                    self.edge_count,

                "self_dependency_count":
                    self.self_dependency_count,

                "violations":
                    tuple(
                        item.to_dict()
                        for item
                        in self.violations
                    ),

                "graph_version":
                    self.graph_version,

                "validation_version":
                    self.validation_version,
            }
        )


# =============================================================================
# 6. Canonical graph validation
# =============================================================================

def validate_dependency_graph(
    graph: DependencyGraph,
) -> DependencyValidationResult:
    """
    Validate one frozen Phase 4.1 DependencyGraph.

    This validator intentionally does not inspect graph cycles.
    """

    if not isinstance(
        graph,
        DependencyGraph,
    ):
        raise InvalidDependencyValidationRequestError(
            "graph must be a Phase 4.1 DependencyGraph."
        )

    violations: list[
        DependencyValidationViolation
    ] = []

    checks_run = 0
    checks_passed = 0


    def invariant(
        condition: bool,
        message: str,
    ) -> None:
        nonlocal checks_run
        nonlocal checks_passed

        checks_run += 1

        if condition:
            checks_passed += 1
            return

        violations.append(
            DependencyValidationViolation(
                code=GRAPH_INVARIANT_VIOLATION_CODE,
                message=message,
            )
        )


    # -------------------------------------------------------------------------
    # Frozen 4.1 identity/invariants
    # -------------------------------------------------------------------------

    invariant(
        graph.graph_version
        == DEPENDENCY_GRAPH_VERSION,
        (
            "graph_version does not match "
            "the frozen Phase 4.1 version."
        ),
    )

    invariant(
        isinstance(
            graph.workflow_id,
            str,
        )
        and bool(
            graph.workflow_id
        )
        and graph.workflow_id
        == graph.workflow_id.strip(),
        "workflow_id is not canonical.",
    )

    invariant(
        isinstance(
            graph.node_ids,
            tuple,
        ),
        "node_ids must be an immutable tuple.",
    )

    invariant(
        graph.node_ids
        == tuple(
            sorted(
                set(
                    graph.node_ids
                )
            )
        ),
        (
            "node_ids must be unique and "
            "lexically canonical."
        ),
    )

    node_identity_valid = all(
        isinstance(
            node_id,
            str,
        )
        and bool(
            node_id
        )
        and node_id
        == node_id.strip()
        for node_id
        in graph.node_ids
    )

    invariant(
        node_identity_valid,
        "Every dependency node must be a canonical stage_id.",
    )

    invariant(
        isinstance(
            graph.edges,
            tuple,
        ),
        "edges must be an immutable tuple.",
    )

    edge_identity_valid = all(
        isinstance(
            edge,
            DependencyEdge,
        )
        for edge
        in graph.edges
    )

    invariant(
        edge_identity_valid,
        "Every dependency edge must be DependencyEdge.",
    )

    canonical_edges = (
        tuple(
            sorted(
                set(
                    graph.edges
                ),
                key=lambda item: (
                    item.prerequisite_stage_id,
                    item.dependent_stage_id,
                ),
            )
        )
        if edge_identity_valid
        else ()
    )

    invariant(
        edge_identity_valid
        and graph.edges
        == canonical_edges,
        (
            "Dependency edges must be unique "
            "and lexically canonical."
        ),
    )

    endpoint_membership_valid = (
        edge_identity_valid
        and all(
            edge.prerequisite_stage_id
            in graph.node_ids
            and edge.dependent_stage_id
            in graph.node_ids
            for edge
            in graph.edges
        )
    )

    invariant(
        endpoint_membership_valid,
        (
            "Every dependency edge endpoint "
            "must exist in graph.node_ids."
        ),
    )


    # -------------------------------------------------------------------------
    # Phase 4.2 semantic rule: self-dependency prohibited
    # -------------------------------------------------------------------------

    self_edges = (
        tuple(
            edge
            for edge
            in graph.edges
            if isinstance(
                edge,
                DependencyEdge,
            )
            and edge.prerequisite_stage_id
            == edge.dependent_stage_id
        )
    )

    for edge in self_edges:
        checks_run += 1

        violations.append(
            DependencyValidationViolation(
                code=SELF_DEPENDENCY_VIOLATION_CODE,
                message=(
                    "A stage must not depend on itself."
                ),
                prerequisite_stage_id=(
                    edge.prerequisite_stage_id
                ),
                dependent_stage_id=(
                    edge.dependent_stage_id
                ),
            )
        )

    # One explicit semantic self-dependency check exists even for a graph
    # with zero self-edges so the result records that rule as evaluated.
    if not self_edges:
        checks_run += 1
        checks_passed += 1


    # -------------------------------------------------------------------------
    # Deterministic result
    # -------------------------------------------------------------------------

    canonical_violations = tuple(
        sorted(
            violations
        )
    )

    checks_failed = (
        checks_run
        - checks_passed
    )

    return DependencyValidationResult(
        is_valid=(
            checks_failed
            == 0
        ),
        checks_run=checks_run,
        checks_passed=checks_passed,
        checks_failed=checks_failed,
        node_count=len(
            graph.node_ids
        ),
        edge_count=len(
            graph.edges
        ),
        self_dependency_count=len(
            self_edges
        ),
        violations=canonical_violations,
        graph_version=graph.graph_version,
        validation_version=(
            DEPENDENCY_VALIDATION_VERSION
        ),
    )


# =============================================================================
# 7. Require-valid guard
# =============================================================================

def require_valid_dependency_graph(
    graph: DependencyGraph,
) -> DependencyValidationResult:
    result = validate_dependency_graph(
        graph
    )

    if not result.is_valid:
        raise DependencyGraphValidationFailedError(
            result
        )

    return result


# =============================================================================
# 8. Validation snapshot
# =============================================================================

def dependency_validation_snapshot(
    graph: DependencyGraph,
) -> Mapping[str, Any]:
    result = validate_dependency_graph(
        graph
    )

    return _freeze(
        {
            "validation_version":
                DEPENDENCY_VALIDATION_VERSION,

            "schema_version":
                DEPENDENCY_VALIDATION_SCHEMA_VERSION,

            "graph_version":
                result.graph_version,

            "is_valid":
                result.is_valid,

            "checks_run":
                result.checks_run,

            "checks_passed":
                result.checks_passed,

            "checks_failed":
                result.checks_failed,

            "node_count":
                result.node_count,

            "edge_count":
                result.edge_count,

            "self_dependency_count":
                result.self_dependency_count,

            "violations":
                tuple(
                    item.to_dict()
                    for item
                    in result.violations
                ),
        }
    )


# =============================================================================
# 9. Architecture evidence
# =============================================================================

def explain_dependency_validation_v4_2(
) -> Mapping[str, Any]:
    return _freeze(
        {
            "phase":
                "4.2",

            "component":
                "Dependency Validation",

            "version":
                DEPENDENCY_VALIDATION_VERSION,

            "schema_version":
                DEPENDENCY_VALIDATION_SCHEMA_VERSION,

            "input_authority":
                "Phase 4.1 DependencyGraph",

            "upstream_version":
                DEPENDENCY_GRAPH_VERSION,

            "owns": (
                "dependency graph semantic validity",
                "canonical graph invariant verification",
                "self-dependency rejection",
                "deterministic validation evidence",
                "immutable validation result",
                "require-valid dependency graph guard",
            ),

            "does_not_own": (
                "dependency graph construction",
                "cycle detection",
                "topological sorting",
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

            "validation_rules": {
                "graph_type":
                    "DependencyGraph",

                "graph_version":
                    DEPENDENCY_GRAPH_VERSION,

                "workflow_identity":
                    "canonical",

                "node_identity":
                    "canonical stage_id",

                "edge_identity":
                    "DependencyEdge",

                "edge_endpoint_membership":
                    "required",

                "self_dependency":
                    "prohibited",

                "isolated_nodes":
                    "valid",

                "cycles":
                    (
                        "not evaluated; "
                        "Phase 4.3 owns cycle detection"
                    ),
            },

            "future_authority": {
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
    "DEPENDENCY_VALIDATION_VERSION",
    "DEPENDENCY_VALIDATION_SCHEMA_VERSION",
    "DEPENDENCY_VALIDATION_RESULT_FIELD_COUNT",
    "SELF_DEPENDENCY_VIOLATION_CODE",
    "GRAPH_INVARIANT_VIOLATION_CODE",
    "DependencyValidationError",
    "InvalidDependencyValidationRequestError",
    "DependencyGraphValidationFailedError",
    "DependencyValidationViolation",
    "DependencyValidationResult",
    "validate_dependency_graph",
    "require_valid_dependency_graph",
    "dependency_validation_snapshot",
    "explain_dependency_validation_v4_2",
]
