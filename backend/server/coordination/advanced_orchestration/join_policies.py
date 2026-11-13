"""
LinkCraftor — Universal Coordination Framework

Phase 7.4 — Join Policies

Evaluates whether one structural Phase 7.3 Fan-In join is READY,
WAITING, or UNSATISFIABLE from caller-supplied canonical lifecycle
state evidence.

Policies:
- ALL_SUCCESS
- ALL_TERMINAL
- ANY_SUCCESS

SKIPPED remains outside this component because Phase 7.7 owns advanced
skip semantics.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Final, Mapping

from backend.server.coordination.advanced_orchestration.fan_in import (
    FAN_IN_VERSION,
    FanInCoordination,
)

from backend.server.coordination.advanced_orchestration.parallel_branch_tracking import (
    ParallelBranchState,
    TERMINAL_BRANCH_STATES,
    normalize_branch_state,
)


JOIN_POLICIES_VERSION: Final[str] = (
    "join_policies_v7.4.0"
)

JOIN_POLICIES_SCHEMA_VERSION: Final[str] = (
    "join_policies_schema_v1"
)


class JoinPolicyError(
    ValueError
):
    pass


class JoinPolicy(
    str,
    Enum,
):
    ALL_SUCCESS = "all_success"
    ALL_TERMINAL = "all_terminal"
    ANY_SUCCESS = "any_success"


class JoinDisposition(
    str,
    Enum,
):
    READY = "ready"
    WAITING = "waiting"
    UNSATISFIABLE = "unsatisfiable"


@dataclass(
    frozen=True,
    slots=True,
)
class JoinPolicyEvaluation:

    workflow_id: str
    target_stage_id: str
    fan_in_group_id: str

    prerequisite_stage_ids: tuple[str, ...]

    prerequisite_states: tuple[
        tuple[
            str,
            ParallelBranchState,
        ],
        ...
    ]

    policy: JoinPolicy
    disposition: JoinDisposition

    fan_in_version: str

    join_policies_version: str = (
        JOIN_POLICIES_VERSION
    )

    schema_version: str = (
        JOIN_POLICIES_SCHEMA_VERSION
    )

    @property
    def is_ready(
        self,
    ) -> bool:

        return (
            self.disposition
            is JoinDisposition.READY
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "workflow_id":
                self.workflow_id,

            "target_stage_id":
                self.target_stage_id,

            "fan_in_group_id":
                self.fan_in_group_id,

            "prerequisite_stage_ids":
                list(
                    self.prerequisite_stage_ids
                ),

            "prerequisite_states": {
                stage_id:
                    state.value
                for stage_id, state
                in self.prerequisite_states
            },

            "policy":
                self.policy.value,

            "disposition":
                self.disposition.value,

            "is_ready":
                self.is_ready,

            "fan_in_version":
                self.fan_in_version,

            "join_policies_version":
                self.join_policies_version,

            "schema_version":
                self.schema_version,
        }


def evaluate_join_policy(
    *,
    fan_in: FanInCoordination,
    prerequisite_states: Mapping[str, Any],
    policy: JoinPolicy | str,
) -> JoinPolicyEvaluation:

    if not isinstance(
        fan_in,
        FanInCoordination,
    ):
        raise JoinPolicyError(
            "fan_in must be FanInCoordination"
        )

    if (
        fan_in.fan_in_version
        != FAN_IN_VERSION
    ):
        raise JoinPolicyError(
            "fan_in version mismatch"
        )

    if not fan_in.is_fan_in:
        raise JoinPolicyError(
            "join policy requires a structural Fan-In target"
        )

    if not isinstance(
        prerequisite_states,
        Mapping,
    ):
        raise JoinPolicyError(
            "prerequisite_states must be a mapping"
        )

    expected = (
        fan_in.direct_prerequisite_stage_ids
    )

    supplied = tuple(
        sorted(
            str(
                key
            ).strip()
            for key
            in prerequisite_states.keys()
        )
    )

    if supplied != expected:
        raise JoinPolicyError(
            "prerequisite state membership must exactly match "
            "the Phase 7.3 Fan-In membership"
        )

    try:
        canonical_policy = (
            policy
            if isinstance(
                policy,
                JoinPolicy,
            )
            else JoinPolicy(
                str(
                    policy
                ).strip().lower()
            )
        )
    except Exception as exc:
        raise JoinPolicyError(
            "unsupported join policy"
        ) from exc

    states = tuple(
        (
            stage_id,
            normalize_branch_state(
                prerequisite_states[
                    stage_id
                ]
            ),
        )
        for stage_id
        in expected
    )

    values = tuple(
        state
        for _stage_id, state
        in states
    )

    terminal = tuple(
        state
        in TERMINAL_BRANCH_STATES
        for state
        in values
    )

    completed = tuple(
        state
        is ParallelBranchState.COMPLETED
        for state
        in values
    )

    if (
        canonical_policy
        is JoinPolicy.ALL_SUCCESS
    ):

        if all(
            completed
        ):
            disposition = (
                JoinDisposition.READY
            )

        elif any(
            is_terminal
            and not is_completed
            for is_terminal, is_completed
            in zip(
                terminal,
                completed,
            )
        ):
            disposition = (
                JoinDisposition.UNSATISFIABLE
            )

        else:
            disposition = (
                JoinDisposition.WAITING
            )

    elif (
        canonical_policy
        is JoinPolicy.ALL_TERMINAL
    ):

        disposition = (
            JoinDisposition.READY
            if all(
                terminal
            )
            else JoinDisposition.WAITING
        )

    else:

        if any(
            completed
        ):
            disposition = (
                JoinDisposition.READY
            )

        elif all(
            terminal
        ):
            disposition = (
                JoinDisposition.UNSATISFIABLE
            )

        else:
            disposition = (
                JoinDisposition.WAITING
            )

    return JoinPolicyEvaluation(
        workflow_id=
            fan_in.workflow_id,

        target_stage_id=
            fan_in.target_stage_id,

        fan_in_group_id=
            fan_in.fan_in_group_id,

        prerequisite_stage_ids=
            expected,

        prerequisite_states=
            states,

        policy=
            canonical_policy,

        disposition=
            disposition,

        fan_in_version=
            fan_in.fan_in_version,
    )


__all__ = [
    "JOIN_POLICIES_VERSION",
    "JOIN_POLICIES_SCHEMA_VERSION",
    "JoinPolicyError",
    "JoinPolicy",
    "JoinDisposition",
    "JoinPolicyEvaluation",
    "evaluate_join_policy",
]
