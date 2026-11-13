"""
LinkCraftor — Universal Coordination Framework

Phase 7.5 — Conditional Execution

Evaluates condition evidence for the direct branches of one structural
Phase 7.1 Fan-Out group.

True  -> SELECTED
False -> EXCLUDED
None  -> UNRESOLVED

EXCLUDED is branch-decision evidence only. It is not automatically
converted to SKIPPED; Phase 7.7 owns advanced skip semantics.
"""

from __future__ import annotations

import hashlib

from dataclasses import dataclass
from enum import Enum
from typing import Any, Final, Mapping

from backend.server.coordination.advanced_orchestration.fan_out import (
    FAN_OUT_VERSION,
    FanOutCoordination,
)


CONDITIONAL_EXECUTION_VERSION: Final[str] = (
    "conditional_execution_v7.5.0"
)

CONDITIONAL_EXECUTION_SCHEMA_VERSION: Final[str] = (
    "conditional_execution_schema_v1"
)

CONDITIONAL_DECISION_HASH_ALGORITHM: Final[str] = (
    "SHA256"
)


class ConditionalExecutionError(
    ValueError
):
    pass


class BranchDisposition(
    str,
    Enum,
):
    SELECTED = "selected"
    EXCLUDED = "excluded"
    UNRESOLVED = "unresolved"


@dataclass(
    frozen=True,
    slots=True,
)
class ConditionalExecutionDecision:

    workflow_id: str
    source_stage_id: str
    fan_out_group_id: str

    branch_stage_ids: tuple[str, ...]

    branch_dispositions: tuple[
        tuple[
            str,
            BranchDisposition,
        ],
        ...
    ]

    decision_id: str

    fan_out_version: str

    conditional_execution_version: str = (
        CONDITIONAL_EXECUTION_VERSION
    )

    schema_version: str = (
        CONDITIONAL_EXECUTION_SCHEMA_VERSION
    )

    @property
    def selected_branch_ids(
        self,
    ) -> tuple[str, ...]:

        return tuple(
            stage_id
            for stage_id, disposition
            in self.branch_dispositions
            if (
                disposition
                is BranchDisposition.SELECTED
            )
        )

    @property
    def excluded_branch_ids(
        self,
    ) -> tuple[str, ...]:

        return tuple(
            stage_id
            for stage_id, disposition
            in self.branch_dispositions
            if (
                disposition
                is BranchDisposition.EXCLUDED
            )
        )

    @property
    def unresolved_branch_ids(
        self,
    ) -> tuple[str, ...]:

        return tuple(
            stage_id
            for stage_id, disposition
            in self.branch_dispositions
            if (
                disposition
                is BranchDisposition.UNRESOLVED
            )
        )

    @property
    def fully_resolved(
        self,
    ) -> bool:

        return not bool(
            self.unresolved_branch_ids
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "workflow_id":
                self.workflow_id,

            "source_stage_id":
                self.source_stage_id,

            "fan_out_group_id":
                self.fan_out_group_id,

            "branch_stage_ids":
                list(
                    self.branch_stage_ids
                ),

            "branch_dispositions": {
                stage_id:
                    disposition.value
                for stage_id, disposition
                in self.branch_dispositions
            },

            "selected_branch_ids":
                list(
                    self.selected_branch_ids
                ),

            "excluded_branch_ids":
                list(
                    self.excluded_branch_ids
                ),

            "unresolved_branch_ids":
                list(
                    self.unresolved_branch_ids
                ),

            "fully_resolved":
                self.fully_resolved,

            "decision_id":
                self.decision_id,

            "fan_out_version":
                self.fan_out_version,

            "conditional_execution_version":
                self.conditional_execution_version,

            "schema_version":
                self.schema_version,
        }


def evaluate_conditional_execution(
    *,
    fan_out: FanOutCoordination,
    condition_evidence: Mapping[str, bool | None],
) -> ConditionalExecutionDecision:

    if not isinstance(
        fan_out,
        FanOutCoordination,
    ):
        raise ConditionalExecutionError(
            "fan_out must be FanOutCoordination"
        )

    if (
        fan_out.fan_out_version
        != FAN_OUT_VERSION
    ):
        raise ConditionalExecutionError(
            "fan_out version mismatch"
        )

    if not fan_out.is_fan_out:
        raise ConditionalExecutionError(
            "conditional execution requires a structural Fan-Out group"
        )

    if not isinstance(
        condition_evidence,
        Mapping,
    ):
        raise ConditionalExecutionError(
            "condition_evidence must be a mapping"
        )

    expected = (
        fan_out.direct_dependent_stage_ids
    )

    supplied = tuple(
        sorted(
            str(
                key
            ).strip()
            for key
            in condition_evidence.keys()
        )
    )

    if supplied != expected:
        raise ConditionalExecutionError(
            "condition evidence membership must exactly match "
            "the Phase 7.1 Fan-Out membership"
        )

    dispositions = []

    for stage_id in expected:

        value = (
            condition_evidence[
                stage_id
            ]
        )

        if value is True:
            disposition = (
                BranchDisposition.SELECTED
            )

        elif value is False:
            disposition = (
                BranchDisposition.EXCLUDED
            )

        elif value is None:
            disposition = (
                BranchDisposition.UNRESOLVED
            )

        else:
            raise ConditionalExecutionError(
                "condition evidence must contain only True, False, or None"
            )

        dispositions.append(
            (
                stage_id,
                disposition,
            )
        )

    canonical = tuple(
        dispositions
    )

    material = "|".join(
        (
            "ucf_conditional_execution_decision_v1",
            fan_out.workflow_id,
            fan_out.source_stage_id,
            fan_out.fan_out_group_id,
            *(
                f"{stage_id}:{disposition.value}"
                for stage_id, disposition
                in canonical
            ),
        )
    )

    decision_id = hashlib.sha256(
        material.encode(
            "utf-8"
        )
    ).hexdigest().upper()

    return ConditionalExecutionDecision(
        workflow_id=
            fan_out.workflow_id,

        source_stage_id=
            fan_out.source_stage_id,

        fan_out_group_id=
            fan_out.fan_out_group_id,

        branch_stage_ids=
            expected,

        branch_dispositions=
            canonical,

        decision_id=
            decision_id,

        fan_out_version=
            fan_out.fan_out_version,
    )


__all__ = [
    "CONDITIONAL_EXECUTION_VERSION",
    "CONDITIONAL_EXECUTION_SCHEMA_VERSION",
    "CONDITIONAL_DECISION_HASH_ALGORITHM",
    "ConditionalExecutionError",
    "BranchDisposition",
    "ConditionalExecutionDecision",
    "evaluate_conditional_execution",
]
