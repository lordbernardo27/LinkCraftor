"""
LinkCraftor — Universal Coordination Framework

Phase 7.3 — Fan-In

Identifies structural stage-level fan-in loci using only direct incoming
edges from the frozen Phase 4.1 DependencyGraph.

Two or more direct prerequisites = FAN_IN.
Zero or one direct prerequisite = NO_FAN_IN.

This component does not evaluate prerequisite statuses or join policy.
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


FAN_IN_VERSION: Final[str] = (
    "fan_in_v7.3.0"
)

FAN_IN_SCHEMA_VERSION: Final[str] = (
    "fan_in_schema_v1"
)

FAN_IN_GROUP_HASH_ALGORITHM: Final[str] = (
    "SHA256"
)


class FanInError(
    ValueError
):
    pass


class FanInClassification(
    str,
    Enum,
):
    FAN_IN = "fan_in"
    NO_FAN_IN = "no_fan_in"


def _require_graph(
    graph: Any,
) -> DependencyGraph:

    if not isinstance(
        graph,
        DependencyGraph,
    ):
        raise FanInError(
            "graph must be DependencyGraph"
        )

    if (
        graph.graph_version
        != DEPENDENCY_GRAPH_VERSION
    ):
        raise FanInError(
            "graph version mismatch"
        )

    return graph


def _stage_id(
    value: Any,
) -> str:

    if not isinstance(
        value,
        str,
    ):
        raise FanInError(
            "target_stage_id must be a string"
        )

    value = value.strip()

    if not value:
        raise FanInError(
            "target_stage_id must not be empty"
        )

    return value


def direct_prerequisite_stage_ids(
    *,
    graph: DependencyGraph,
    target_stage_id: str,
) -> tuple[str, ...]:

    graph = _require_graph(
        graph
    )

    target = _stage_id(
        target_stage_id
    )

    if not has_dependency_node(
        graph,
        target,
    ):
        raise FanInError(
            "target_stage_id is not present in DependencyGraph"
        )

    return tuple(
        sorted(
            edge.prerequisite_stage_id
            for edge
            in dependency_edges(
                graph
            )
            if (
                edge.dependent_stage_id
                == target
            )
        )
    )


def calculate_fan_in_group_id(
    *,
    graph: DependencyGraph,
    target_stage_id: str,
) -> str:

    graph = _require_graph(
        graph
    )

    target = _stage_id(
        target_stage_id
    )

    prerequisites = (
        direct_prerequisite_stage_ids(
            graph=graph,
            target_stage_id=target,
        )
    )

    material = "|".join(
        (
            "ucf_fan_in_group_v1",
            graph.workflow_id,
            graph.graph_version,
            target,
            *prerequisites,
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
class FanInCoordination:

    workflow_id: str
    target_stage_id: str

    direct_prerequisite_stage_ids: tuple[
        str,
        ...
    ]

    fan_in_width: int

    classification: FanInClassification

    fan_in_group_id: str

    dependency_graph_version: str

    fan_in_version: str = (
        FAN_IN_VERSION
    )

    schema_version: str = (
        FAN_IN_SCHEMA_VERSION
    )

    @property
    def is_fan_in(
        self,
    ) -> bool:

        return (
            self.classification
            is FanInClassification.FAN_IN
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "workflow_id":
                self.workflow_id,

            "target_stage_id":
                self.target_stage_id,

            "direct_prerequisite_stage_ids":
                list(
                    self.direct_prerequisite_stage_ids
                ),

            "fan_in_width":
                self.fan_in_width,

            "classification":
                self.classification.value,

            "is_fan_in":
                self.is_fan_in,

            "fan_in_group_id":
                self.fan_in_group_id,

            "dependency_graph_version":
                self.dependency_graph_version,

            "fan_in_version":
                self.fan_in_version,

            "schema_version":
                self.schema_version,
        }


def coordinate_fan_in(
    *,
    graph: DependencyGraph,
    target_stage_id: str,
) -> FanInCoordination:

    graph = _require_graph(
        graph
    )

    target = _stage_id(
        target_stage_id
    )

    prerequisites = (
        direct_prerequisite_stage_ids(
            graph=graph,
            target_stage_id=target,
        )
    )

    classification = (
        FanInClassification.FAN_IN
        if len(
            prerequisites
        ) >= 2
        else FanInClassification.NO_FAN_IN
    )

    return FanInCoordination(
        workflow_id=
            graph.workflow_id,

        target_stage_id=
            target,

        direct_prerequisite_stage_ids=
            prerequisites,

        fan_in_width=
            len(
                prerequisites
            ),

        classification=
            classification,

        fan_in_group_id=
            calculate_fan_in_group_id(
                graph=graph,
                target_stage_id=target,
            ),

        dependency_graph_version=
            graph.graph_version,
    )


__all__ = [
    "FAN_IN_VERSION",
    "FAN_IN_SCHEMA_VERSION",
    "FAN_IN_GROUP_HASH_ALGORITHM",
    "FanInError",
    "FanInClassification",
    "FanInCoordination",
    "direct_prerequisite_stage_ids",
    "calculate_fan_in_group_id",
    "coordinate_fan_in",
]
