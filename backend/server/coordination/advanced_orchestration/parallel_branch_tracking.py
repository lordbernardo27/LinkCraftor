"""
LinkCraftor — Universal Coordination Framework

Phase 7.2 — Parallel Branch Tracking

Tracks lifecycle-state evidence for the direct branches of one frozen
Phase 7.1 Fan-Out group.

It does not create a second workflow lifecycle state machine.
It consumes the established Phase-3 lifecycle vocabulary.

SKIPPED is intentionally excluded here. Advanced skip semantics belong
to Phase 7.7.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Final, Mapping

from backend.server.coordination.advanced_orchestration.fan_out import (
    FAN_OUT_VERSION,
    FanOutCoordination,
)


PARALLEL_BRANCH_TRACKING_VERSION: Final[str] = (
    "parallel_branch_tracking_v7.2.0"
)

PARALLEL_BRANCH_TRACKING_SCHEMA_VERSION: Final[str] = (
    "parallel_branch_tracking_schema_v1"
)


class ParallelBranchTrackingError(
    ValueError
):
    pass


class ParallelBranchState(
    str,
    Enum,
):
    CREATED = "CREATED"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    PAUSED = "PAUSED"
    RECOVERING = "RECOVERING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    ABORTED = "ABORTED"


TERMINAL_BRANCH_STATES: Final[
    frozenset[ParallelBranchState]
] = frozenset(
    (
        ParallelBranchState.COMPLETED,
        ParallelBranchState.FAILED,
        ParallelBranchState.CANCELLED,
        ParallelBranchState.ABORTED,
    )
)


def normalize_branch_state(
    value: Any,
) -> ParallelBranchState:

    if isinstance(
        value,
        ParallelBranchState,
    ):
        return value

    if not isinstance(
        value,
        str,
    ):
        raise ParallelBranchTrackingError(
            "branch state must be ParallelBranchState or canonical string"
        )

    try:
        return ParallelBranchState(
            value.strip().upper()
        )
    except Exception as exc:
        raise ParallelBranchTrackingError(
            f"unsupported branch lifecycle state: {value!r}"
        ) from exc


@dataclass(
    frozen=True,
    slots=True,
)
class ParallelBranchSnapshot:

    workflow_id: str
    source_stage_id: str
    fan_out_group_id: str

    branch_stage_ids: tuple[str, ...]

    branch_states: tuple[
        tuple[
            str,
            ParallelBranchState,
        ],
        ...
    ]

    fan_out_version: str

    tracking_version: str = (
        PARALLEL_BRANCH_TRACKING_VERSION
    )

    schema_version: str = (
        PARALLEL_BRANCH_TRACKING_SCHEMA_VERSION
    )

    @property
    def branch_count(
        self,
    ) -> int:

        return len(
            self.branch_stage_ids
        )

    @property
    def state_map(
        self,
    ) -> dict[
        str,
        ParallelBranchState,
    ]:

        return dict(
            self.branch_states
        )

    @property
    def completed_branch_ids(
        self,
    ) -> tuple[str, ...]:

        states = self.state_map

        return tuple(
            stage_id
            for stage_id
            in self.branch_stage_ids
            if states[
                stage_id
            ]
            is ParallelBranchState.COMPLETED
        )

    @property
    def terminal_branch_ids(
        self,
    ) -> tuple[str, ...]:

        states = self.state_map

        return tuple(
            stage_id
            for stage_id
            in self.branch_stage_ids
            if states[
                stage_id
            ]
            in TERMINAL_BRANCH_STATES
        )

    @property
    def active_branch_ids(
        self,
    ) -> tuple[str, ...]:

        states = self.state_map

        return tuple(
            stage_id
            for stage_id
            in self.branch_stage_ids
            if states[
                stage_id
            ]
            not in TERMINAL_BRANCH_STATES
        )

    @property
    def failed_branch_ids(
        self,
    ) -> tuple[str, ...]:

        states = self.state_map

        failure_states = {
            ParallelBranchState.FAILED,
            ParallelBranchState.CANCELLED,
            ParallelBranchState.ABORTED,
        }

        return tuple(
            stage_id
            for stage_id
            in self.branch_stage_ids
            if states[
                stage_id
            ]
            in failure_states
        )

    @property
    def all_completed(
        self,
    ) -> bool:

        return (
            self.branch_count
            > 0
            and len(
                self.completed_branch_ids
            )
            == self.branch_count
        )

    @property
    def all_terminal(
        self,
    ) -> bool:

        return (
            self.branch_count
            > 0
            and len(
                self.terminal_branch_ids
            )
            == self.branch_count
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

            "branch_states": {
                stage_id:
                    state.value
                for stage_id, state
                in self.branch_states
            },

            "branch_count":
                self.branch_count,

            "completed_branch_ids":
                list(
                    self.completed_branch_ids
                ),

            "terminal_branch_ids":
                list(
                    self.terminal_branch_ids
                ),

            "active_branch_ids":
                list(
                    self.active_branch_ids
                ),

            "failed_branch_ids":
                list(
                    self.failed_branch_ids
                ),

            "all_completed":
                self.all_completed,

            "all_terminal":
                self.all_terminal,

            "fan_out_version":
                self.fan_out_version,

            "tracking_version":
                self.tracking_version,

            "schema_version":
                self.schema_version,
        }


def track_parallel_branches(
    *,
    fan_out: FanOutCoordination,
    branch_states: Mapping[str, Any],
) -> ParallelBranchSnapshot:

    if not isinstance(
        fan_out,
        FanOutCoordination,
    ):
        raise ParallelBranchTrackingError(
            "fan_out must be FanOutCoordination"
        )

    if (
        fan_out.fan_out_version
        != FAN_OUT_VERSION
    ):
        raise ParallelBranchTrackingError(
            "fan_out version mismatch"
        )

    if not fan_out.is_fan_out:
        raise ParallelBranchTrackingError(
            "parallel branch tracking requires a structural Fan-Out group"
        )

    if not isinstance(
        branch_states,
        Mapping,
    ):
        raise ParallelBranchTrackingError(
            "branch_states must be a mapping"
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
            in branch_states.keys()
        )
    )

    if supplied != expected:
        raise ParallelBranchTrackingError(
            "branch state membership must exactly match "
            "the direct Phase 7.1 Fan-Out membership"
        )

    normalized = tuple(
        (
            stage_id,
            normalize_branch_state(
                branch_states[
                    stage_id
                ]
            ),
        )
        for stage_id
        in expected
    )

    return ParallelBranchSnapshot(
        workflow_id=
            fan_out.workflow_id,

        source_stage_id=
            fan_out.source_stage_id,

        fan_out_group_id=
            fan_out.fan_out_group_id,

        branch_stage_ids=
            expected,

        branch_states=
            normalized,

        fan_out_version=
            fan_out.fan_out_version,
    )


__all__ = [
    "PARALLEL_BRANCH_TRACKING_VERSION",
    "PARALLEL_BRANCH_TRACKING_SCHEMA_VERSION",
    "ParallelBranchTrackingError",
    "ParallelBranchState",
    "TERMINAL_BRANCH_STATES",
    "ParallelBranchSnapshot",
    "normalize_branch_state",
    "track_parallel_branches",
]
