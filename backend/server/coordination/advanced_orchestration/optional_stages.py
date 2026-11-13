"""
LinkCraftor — Universal Coordination Framework

Phase 7.6 — Optional Stages

Defines explicit workflow-stage optionality and evaluates an explicit
include/omit decision for each optional stage.

Important boundaries
--------------------
- Optionality is never inferred merely from dependency topology.
- Required stages are every graph node not explicitly declared optional.
- OMIT is decision evidence; it does not itself create SKIPPED state.
- Phase 7.7 owns conversion of authorized omission into Skip Semantics.
- No lifecycle mutation, Runtime submission, execution, or persistence.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Final, Iterable, Mapping

from backend.server.coordination.dependency_planning.dependency_graph import (
    DEPENDENCY_GRAPH_VERSION,
    DependencyGraph,
)


OPTIONAL_STAGES_VERSION: Final[str] = (
    "optional_stages_v7.6.0"
)

OPTIONAL_STAGES_SCHEMA_VERSION: Final[str] = (
    "optional_stages_schema_v1"
)


class OptionalStagesError(ValueError):
    pass


class OptionalStageDisposition(str, Enum):
    INCLUDE = "include"
    OMIT = "omit"


def _canonical_stage_ids(
    values: Iterable[Any],
) -> tuple[str, ...]:

    if isinstance(values, (str, bytes)):
        raise OptionalStagesError(
            "stage IDs must be an iterable of identifiers, not a scalar string"
        )

    normalized = []

    for raw in values:
        if not isinstance(raw, str):
            raise OptionalStagesError(
                "every optional stage ID must be a string"
            )

        value = raw.strip()

        if not value:
            raise OptionalStagesError(
                "optional stage IDs must not be empty"
            )

        normalized.append(value)

    if len(normalized) != len(set(normalized)):
        raise OptionalStagesError(
            "optional stage IDs must be unique"
        )

    return tuple(sorted(normalized))


@dataclass(frozen=True, slots=True)
class OptionalStageEvaluation:

    workflow_id: str

    optional_stage_ids: tuple[str, ...]
    required_stage_ids: tuple[str, ...]

    decisions: tuple[
        tuple[
            str,
            OptionalStageDisposition,
        ],
        ...
    ]

    included_optional_stage_ids: tuple[str, ...]
    omitted_optional_stage_ids: tuple[str, ...]

    dependency_graph_version: str

    optional_stages_version: str = OPTIONAL_STAGES_VERSION
    schema_version: str = OPTIONAL_STAGES_SCHEMA_VERSION

    def disposition_for(
        self,
        stage_id: str,
    ) -> OptionalStageDisposition:

        for candidate, disposition in self.decisions:
            if candidate == stage_id:
                return disposition

        raise OptionalStagesError(
            "stage_id is not an optional stage"
        )

    def to_dict(self) -> dict[str, Any]:

        return {
            "workflow_id": self.workflow_id,

            "optional_stage_ids":
                list(self.optional_stage_ids),

            "required_stage_ids":
                list(self.required_stage_ids),

            "decisions": {
                stage_id: disposition.value
                for stage_id, disposition
                in self.decisions
            },

            "included_optional_stage_ids":
                list(self.included_optional_stage_ids),

            "omitted_optional_stage_ids":
                list(self.omitted_optional_stage_ids),

            "dependency_graph_version":
                self.dependency_graph_version,

            "optional_stages_version":
                self.optional_stages_version,

            "schema_version":
                self.schema_version,
        }


def evaluate_optional_stages(
    *,
    graph: DependencyGraph,
    optional_stage_ids: Iterable[str],
    decisions: Mapping[str, OptionalStageDisposition | str],
) -> OptionalStageEvaluation:

    if not isinstance(graph, DependencyGraph):
        raise OptionalStagesError(
            "graph must be a Phase 4.1 DependencyGraph"
        )

    if graph.graph_version != DEPENDENCY_GRAPH_VERSION:
        raise OptionalStagesError(
            "DependencyGraph version mismatch"
        )

    optional_ids = _canonical_stage_ids(
        optional_stage_ids
    )

    graph_nodes = tuple(
        sorted(graph.node_ids)
    )

    unknown = tuple(
        stage_id
        for stage_id
        in optional_ids
        if stage_id not in graph_nodes
    )

    if unknown:
        raise OptionalStagesError(
            "optional stage IDs must belong to the DependencyGraph"
        )

    if not isinstance(decisions, Mapping):
        raise OptionalStagesError(
            "decisions must be a mapping"
        )

    supplied = tuple(
        sorted(
            str(key).strip()
            for key
            in decisions.keys()
        )
    )

    if supplied != optional_ids:
        raise OptionalStagesError(
            "decision membership must exactly match optional_stage_ids"
        )

    canonical_decisions = []

    for stage_id in optional_ids:

        raw = decisions[stage_id]

        try:
            disposition = (
                raw
                if isinstance(
                    raw,
                    OptionalStageDisposition,
                )
                else OptionalStageDisposition(
                    str(raw).strip().lower()
                )
            )
        except Exception as exc:
            raise OptionalStagesError(
                "optional-stage decision must be INCLUDE or OMIT"
            ) from exc

        canonical_decisions.append(
            (
                stage_id,
                disposition,
            )
        )

    canonical_decisions = tuple(
        canonical_decisions
    )

    included = tuple(
        stage_id
        for stage_id, disposition
        in canonical_decisions
        if disposition
        is OptionalStageDisposition.INCLUDE
    )

    omitted = tuple(
        stage_id
        for stage_id, disposition
        in canonical_decisions
        if disposition
        is OptionalStageDisposition.OMIT
    )

    required = tuple(
        stage_id
        for stage_id
        in graph_nodes
        if stage_id not in optional_ids
    )

    return OptionalStageEvaluation(
        workflow_id=
            graph.workflow_id,

        optional_stage_ids=
            optional_ids,

        required_stage_ids=
            required,

        decisions=
            canonical_decisions,

        included_optional_stage_ids=
            included,

        omitted_optional_stage_ids=
            omitted,

        dependency_graph_version=
            graph.graph_version,
    )


__all__ = [
    "OPTIONAL_STAGES_VERSION",
    "OPTIONAL_STAGES_SCHEMA_VERSION",
    "OptionalStagesError",
    "OptionalStageDisposition",
    "OptionalStageEvaluation",
    "evaluate_optional_stages",
]
