"""
LinkCraftor
Universal Coordination Framework

PHASE 7.1 — Fan-Out

Purpose
-------
Identify structural stage-level fan-out loci from the frozen Phase 4.1
DependencyGraph.

Canonical rule
--------------
A source stage is FAN_OUT when it has two or more direct dependent stages.

A source stage with zero or one direct dependent stage is NO_FAN_OUT.

Only direct outgoing dependency edges define fan-out membership.

Execution-wave co-membership does not define fan-out. Phase 4.5 execution
waves express immediate parallel eligibility only.

Boundaries
----------
Phase 7.1:
- does not determine branch readiness,
- does not dispatch Runtime jobs,
- does not use Runtime job IDs,
- does not track branch progress (Phase 7.2),
- does not coordinate fan-in (Phase 7.3),
- does not apply join policy (Phase 7.4),
- does not evaluate conditional execution (Phase 7.5),
- does not own optional stages (Phase 7.6),
- does not own skip semantics (Phase 7.7),
- does not persist orchestration state,
- does not mutate the dependency graph,
- does not mutate workflow lifecycle state.
"""

from __future__ import annotations

import hashlib

from dataclasses import dataclass
from enum import Enum
from typing import Any, Final

from backend.server.coordination.dependency_planning.dependency_graph import (
    DEPENDENCY_GRAPH_VERSION,
    DependencyGraph,
    dependency_edges,
    has_dependency_node,
)


FAN_OUT_VERSION: Final[str] = (
    "fan_out_v7.1.0"
)

FAN_OUT_SCHEMA_VERSION: Final[str] = (
    "fan_out_schema_v1"
)

FAN_OUT_GROUP_HASH_ALGORITHM: Final[str] = (
    "SHA256"
)


class FanOutError(
    ValueError
):
    """Base Phase 7.1 Fan-Out error."""


class InvalidFanOutRequestError(
    FanOutError
):
    """Fan-Out request is not canonical."""


class FanOutClassification(
    str,
    Enum,
):
    FAN_OUT = "fan_out"
    NO_FAN_OUT = "no_fan_out"


def _normalize_stage_id(
    value: Any,
) -> str:

    if not isinstance(
        value,
        str,
    ):
        raise InvalidFanOutRequestError(
            "source_stage_id must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise InvalidFanOutRequestError(
            "source_stage_id must not be empty."
        )

    return normalized


def _require_graph(
    graph: Any,
) -> DependencyGraph:

    if not isinstance(
        graph,
        DependencyGraph,
    ):
        raise InvalidFanOutRequestError(
            "graph must be a Phase 4.1 DependencyGraph."
        )

    if (
        graph.graph_version
        != DEPENDENCY_GRAPH_VERSION
    ):
        raise InvalidFanOutRequestError(
            "graph version does not match frozen Phase 4.1 authority."
        )

    return graph


def direct_dependent_stage_ids(
    *,
    graph: DependencyGraph,
    source_stage_id: str,
) -> tuple[str, ...]:

    canonical_graph = _require_graph(
        graph
    )

    source = _normalize_stage_id(
        source_stage_id
    )

    if not has_dependency_node(
        canonical_graph,
        source,
    ):
        raise InvalidFanOutRequestError(
            "source_stage_id is not present in DependencyGraph."
        )

    dependents = tuple(
        sorted(
            edge.dependent_stage_id
            for edge
            in dependency_edges(
                canonical_graph
            )
            if (
                edge.prerequisite_stage_id
                == source
            )
        )
    )

    return dependents


def classify_fan_out(
    *,
    graph: DependencyGraph,
    source_stage_id: str,
) -> FanOutClassification:

    dependents = (
        direct_dependent_stage_ids(
            graph=graph,
            source_stage_id=source_stage_id,
        )
    )

    if len(
        dependents
    ) >= 2:

        return (
            FanOutClassification.FAN_OUT
        )

    return (
        FanOutClassification.NO_FAN_OUT
    )


def calculate_fan_out_group_id(
    *,
    graph: DependencyGraph,
    source_stage_id: str,
) -> str:

    canonical_graph = _require_graph(
        graph
    )

    source = _normalize_stage_id(
        source_stage_id
    )

    dependents = (
        direct_dependent_stage_ids(
            graph=canonical_graph,
            source_stage_id=source,
        )
    )

    material = "|".join(
        (
            "ucf_fan_out_group_v1",
            canonical_graph.workflow_id,
            canonical_graph.graph_version,
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
class FanOutCoordination:

    workflow_id: str
    source_stage_id: str

    direct_dependent_stage_ids: tuple[
        str,
        ...
    ]

    fan_out_width: int

    classification: FanOutClassification

    fan_out_group_id: str

    dependency_graph_version: str

    fan_out_version: str = (
        FAN_OUT_VERSION
    )

    schema_version: str = (
        FAN_OUT_SCHEMA_VERSION
    )

    @property
    def is_fan_out(
        self,
    ) -> bool:

        return (
            self.classification
            is FanOutClassification.FAN_OUT
        )

    @property
    def has_dependents(
        self,
    ) -> bool:

        return (
            self.fan_out_width
            > 0
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "workflow_id":
                self.workflow_id,

            "source_stage_id":
                self.source_stage_id,

            "direct_dependent_stage_ids":
                list(
                    self.direct_dependent_stage_ids
                ),

            "fan_out_width":
                self.fan_out_width,

            "classification":
                self.classification.value,

            "is_fan_out":
                self.is_fan_out,

            "has_dependents":
                self.has_dependents,

            "fan_out_group_id":
                self.fan_out_group_id,

            "dependency_graph_version":
                self.dependency_graph_version,

            "fan_out_version":
                self.fan_out_version,

            "schema_version":
                self.schema_version,
        }


def coordinate_fan_out(
    *,
    graph: DependencyGraph,
    source_stage_id: str,
) -> FanOutCoordination:

    canonical_graph = _require_graph(
        graph
    )

    source = _normalize_stage_id(
        source_stage_id
    )

    dependents = (
        direct_dependent_stage_ids(
            graph=canonical_graph,
            source_stage_id=source,
        )
    )

    classification = (
        FanOutClassification.FAN_OUT
        if len(
            dependents
        ) >= 2
        else FanOutClassification.NO_FAN_OUT
    )

    return FanOutCoordination(
        workflow_id=
            canonical_graph.workflow_id,

        source_stage_id=
            source,

        direct_dependent_stage_ids=
            dependents,

        fan_out_width=
            len(
                dependents
            ),

        classification=
            classification,

        fan_out_group_id=
            calculate_fan_out_group_id(
                graph=canonical_graph,
                source_stage_id=source,
            ),

        dependency_graph_version=
            canonical_graph.graph_version,
    )


__all__ = [
    "FAN_OUT_VERSION",
    "FAN_OUT_SCHEMA_VERSION",
    "FAN_OUT_GROUP_HASH_ALGORITHM",
    "FanOutError",
    "InvalidFanOutRequestError",
    "FanOutClassification",
    "FanOutCoordination",
    "direct_dependent_stage_ids",
    "classify_fan_out",
    "calculate_fan_out_group_id",
    "coordinate_fan_out",
]
