from __future__ import annotations

import enum
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Final, Mapping

from backend.server.runtime.universal_orchestration.run_identity import (
    UniversalOrchestrationRunIdentity,
)


UNIVERSAL_ORCHESTRATION_STATE_MODEL_VERSION = (
    "universal_orchestration_state_model_v5.1.3"
)

UNIVERSAL_ORCHESTRATION_STATE_MODEL_SCHEMA_VERSION = (
    "universal_orchestration_state_model_schema_v1"
)


class UniversalOrchestrationStateModelError(
    ValueError
):

    def __init__(
        self,
        message: str,
        *,
        code: str,
        value: Any = None,
    ) -> None:

        super().__init__(
            message
        )

        self.code = str(
            code
        )

        self.value = value


class UniversalOrchestrationState(
    str,
    enum.Enum,
):

    CREATED = "created"

    ACTIVE = "active"

    WAITING = "waiting"

    SUSPENDED = "suspended"

    RECOVERING = "recovering"

    SUCCEEDED = "succeeded"

    FAILED = "failed"

    CANCELLED = "cancelled"


TERMINAL_UNIVERSAL_ORCHESTRATION_STATES: Final[
    frozenset[UniversalOrchestrationState]
] = frozenset(
    {
        UniversalOrchestrationState.SUCCEEDED,
        UniversalOrchestrationState.FAILED,
        UniversalOrchestrationState.CANCELLED,
    }
)


NON_TERMINAL_UNIVERSAL_ORCHESTRATION_STATES: Final[
    frozenset[UniversalOrchestrationState]
] = frozenset(
    state
    for state in UniversalOrchestrationState
    if state
    not in TERMINAL_UNIVERSAL_ORCHESTRATION_STATES
)


UNIVERSAL_ORCHESTRATION_STATE_TRANSITIONS: Final[
    Mapping[
        UniversalOrchestrationState,
        frozenset[UniversalOrchestrationState],
    ]
] = MappingProxyType(
    {
        UniversalOrchestrationState.CREATED:
            frozenset(
                {
                    UniversalOrchestrationState.ACTIVE,
                    UniversalOrchestrationState.WAITING,
                    UniversalOrchestrationState.SUSPENDED,
                    UniversalOrchestrationState.SUCCEEDED,
                    UniversalOrchestrationState.FAILED,
                    UniversalOrchestrationState.CANCELLED,
                }
            ),

        UniversalOrchestrationState.ACTIVE:
            frozenset(
                {
                    UniversalOrchestrationState.WAITING,
                    UniversalOrchestrationState.SUSPENDED,
                    UniversalOrchestrationState.RECOVERING,
                    UniversalOrchestrationState.SUCCEEDED,
                    UniversalOrchestrationState.FAILED,
                    UniversalOrchestrationState.CANCELLED,
                }
            ),

        UniversalOrchestrationState.WAITING:
            frozenset(
                {
                    UniversalOrchestrationState.ACTIVE,
                    UniversalOrchestrationState.SUSPENDED,
                    UniversalOrchestrationState.RECOVERING,
                    UniversalOrchestrationState.SUCCEEDED,
                    UniversalOrchestrationState.FAILED,
                    UniversalOrchestrationState.CANCELLED,
                }
            ),

        UniversalOrchestrationState.SUSPENDED:
            frozenset(
                {
                    UniversalOrchestrationState.ACTIVE,
                    UniversalOrchestrationState.WAITING,
                    UniversalOrchestrationState.RECOVERING,
                    UniversalOrchestrationState.SUCCEEDED,
                    UniversalOrchestrationState.FAILED,
                    UniversalOrchestrationState.CANCELLED,
                }
            ),

        UniversalOrchestrationState.RECOVERING:
            frozenset(
                {
                    UniversalOrchestrationState.ACTIVE,
                    UniversalOrchestrationState.WAITING,
                    UniversalOrchestrationState.SUSPENDED,
                    UniversalOrchestrationState.SUCCEEDED,
                    UniversalOrchestrationState.FAILED,
                    UniversalOrchestrationState.CANCELLED,
                }
            ),

        UniversalOrchestrationState.SUCCEEDED:
            frozenset(),

        UniversalOrchestrationState.FAILED:
            frozenset(),

        UniversalOrchestrationState.CANCELLED:
            frozenset(),
    }
)


def normalize_universal_orchestration_state(
    value: Any,
) -> UniversalOrchestrationState:

    if isinstance(
        value,
        UniversalOrchestrationState,
    ):

        return value

    if not isinstance(
        value,
        str,
    ):

        raise UniversalOrchestrationStateModelError(
            "Orchestration state must be a string or UniversalOrchestrationState.",
            code="invalid_orchestration_state",
            value=value,
        )

    normalized = (
        value.strip().lower()
    )

    if not normalized:

        raise UniversalOrchestrationStateModelError(
            "Orchestration state must not be empty.",
            code="invalid_orchestration_state",
            value=value,
        )

    try:

        return UniversalOrchestrationState(
            normalized
        )

    except ValueError as exc:

        raise UniversalOrchestrationStateModelError(
            "Unknown Runtime Orchestration state.",
            code="invalid_orchestration_state",
            value=value,
        ) from exc


def initial_universal_orchestration_state(
) -> UniversalOrchestrationState:

    return UniversalOrchestrationState.CREATED


def is_terminal_universal_orchestration_state(
    value: Any,
) -> bool:

    state = (
        normalize_universal_orchestration_state(
            value
        )
    )

    return (
        state
        in TERMINAL_UNIVERSAL_ORCHESTRATION_STATES
    )


def is_non_terminal_universal_orchestration_state(
    value: Any,
) -> bool:

    state = (
        normalize_universal_orchestration_state(
            value
        )
    )

    return (
        state
        in NON_TERMINAL_UNIVERSAL_ORCHESTRATION_STATES
    )


def allowed_universal_orchestration_transitions(
    value: Any,
) -> frozenset[UniversalOrchestrationState]:

    state = (
        normalize_universal_orchestration_state(
            value
        )
    )

    return (
        UNIVERSAL_ORCHESTRATION_STATE_TRANSITIONS[
            state
        ]
    )


def can_transition_universal_orchestration_state(
    *,
    current_state: Any,
    target_state: Any,
) -> bool:

    current = (
        normalize_universal_orchestration_state(
            current_state
        )
    )

    target = (
        normalize_universal_orchestration_state(
            target_state
        )
    )

    if current is target:

        return False

    return (
        target
        in UNIVERSAL_ORCHESTRATION_STATE_TRANSITIONS[
            current
        ]
    )


def validate_universal_orchestration_state_transition(
    *,
    current_state: Any,
    target_state: Any,
) -> tuple[
    UniversalOrchestrationState,
    UniversalOrchestrationState,
]:

    current = (
        normalize_universal_orchestration_state(
            current_state
        )
    )

    target = (
        normalize_universal_orchestration_state(
            target_state
        )
    )

    if current is target:

        raise UniversalOrchestrationStateModelError(
            "Runtime Orchestration self-transition is not allowed.",
            code="orchestration_self_transition_not_allowed",
            value=(
                current.value,
                target.value,
            ),
        )

    if (
        current
        in TERMINAL_UNIVERSAL_ORCHESTRATION_STATES
    ):

        raise UniversalOrchestrationStateModelError(
            "Terminal Runtime Orchestration state is immutable.",
            code="terminal_orchestration_state_immutable",
            value=(
                current.value,
                target.value,
            ),
        )

    if (
        target
        not in UNIVERSAL_ORCHESTRATION_STATE_TRANSITIONS[
            current
        ]
    ):

        raise UniversalOrchestrationStateModelError(
            "Illegal Runtime Orchestration state transition.",
            code="illegal_orchestration_state_transition",
            value=(
                current.value,
                target.value,
            ),
        )

    return (
        current,
        target,
    )


def _require_orchestration_run_identity(
    value: Any,
) -> UniversalOrchestrationRunIdentity:

    if not isinstance(
        value,
        UniversalOrchestrationRunIdentity,
    ):

        raise UniversalOrchestrationStateModelError(
            (
                "identity must be a "
                "UniversalOrchestrationRunIdentity."
            ),
            code="invalid_orchestration_state_identity",
            value=value,
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class UniversalOrchestrationStateSnapshot:

    identity: UniversalOrchestrationRunIdentity

    state: UniversalOrchestrationState = (
        UniversalOrchestrationState.CREATED
    )

    schema_version: str = (
        UNIVERSAL_ORCHESTRATION_STATE_MODEL_SCHEMA_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        identity = (
            _require_orchestration_run_identity(
                self.identity
            )
        )

        state = (
            normalize_universal_orchestration_state(
                self.state
            )
        )

        if (
            self.schema_version
            != UNIVERSAL_ORCHESTRATION_STATE_MODEL_SCHEMA_VERSION
        ):

            raise UniversalOrchestrationStateModelError(
                "Invalid Orchestration State Model schema_version.",
                code="invalid_orchestration_state_schema_version",
                value=self.schema_version,
            )

        object.__setattr__(
            self,
            "identity",
            identity,
        )

        object.__setattr__(
            self,
            "state",
            state,
        )

    @property
    def orchestration_run_id(
        self,
    ) -> str:

        return (
            self.identity.orchestration_run_id
        )

    @property
    def workspace_id(
        self,
    ) -> str:

        return (
            self.identity.workspace_id
        )

    @property
    def pipeline(
        self,
    ) -> str:

        return (
            self.identity.pipeline
        )

    @property
    def job_ids(
        self,
    ) -> tuple[str, ...]:

        return (
            self.identity.job_ids
        )

    @property
    def terminal(
        self,
    ) -> bool:

        return (
            self.state
            in TERMINAL_UNIVERSAL_ORCHESTRATION_STATES
        )

    @property
    def non_terminal(
        self,
    ) -> bool:

        return not self.terminal

    @property
    def allowed_transitions(
        self,
    ) -> frozenset[UniversalOrchestrationState]:

        return (
            UNIVERSAL_ORCHESTRATION_STATE_TRANSITIONS[
                self.state
            ]
        )


def create_initial_universal_orchestration_state_snapshot(
    *,
    identity: Any,
) -> UniversalOrchestrationStateSnapshot:

    return UniversalOrchestrationStateSnapshot(
        identity=_require_orchestration_run_identity(
            identity
        ),
        state=UniversalOrchestrationState.CREATED,
    )


def create_universal_orchestration_state_snapshot(
    *,
    identity: Any,
    state: Any,
) -> UniversalOrchestrationStateSnapshot:

    return UniversalOrchestrationStateSnapshot(
        identity=_require_orchestration_run_identity(
            identity
        ),
        state=normalize_universal_orchestration_state(
            state
        ),
    )


def transition_universal_orchestration_state(
    *,
    snapshot: Any,
    target_state: Any,
) -> UniversalOrchestrationStateSnapshot:

    if not isinstance(
        snapshot,
        UniversalOrchestrationStateSnapshot,
    ):

        raise UniversalOrchestrationStateModelError(
            (
                "snapshot must be a "
                "UniversalOrchestrationStateSnapshot."
            ),
            code="invalid_orchestration_state_snapshot",
            value=snapshot,
        )

    (
        _,
        target,
    ) = (
        validate_universal_orchestration_state_transition(
            current_state=snapshot.state,
            target_state=target_state,
        )
    )

    return UniversalOrchestrationStateSnapshot(
        identity=snapshot.identity,
        state=target,
    )


def explain_universal_orchestration_state_model_v1(
) -> Mapping[str, Any]:

    return MappingProxyType(
        {
            "phase":
                "5.1.3",

            "component":
                "Universal Orchestration State Model",

            "version":
                UNIVERSAL_ORCHESTRATION_STATE_MODEL_VERSION,

            "schema_version":
                UNIVERSAL_ORCHESTRATION_STATE_MODEL_SCHEMA_VERSION,

            "states":
                tuple(
                    state.value
                    for state
                    in UniversalOrchestrationState
                ),

            "initial_state":
                UniversalOrchestrationState.CREATED.value,

            "terminal_states":
                tuple(
                    sorted(
                        state.value
                        for state
                        in TERMINAL_UNIVERSAL_ORCHESTRATION_STATES
                    )
                ),

            "stored_fields": (
                "identity",
                "state",
                "schema_version",
            ),

            "identity_rule": (
                "Each immutable orchestration state snapshot binds "
                "to exactly one frozen 5.1.2 "
                "UniversalOrchestrationRunIdentity."
            ),

            "transition_rule": (
                "5.1.3 validates lifecycle transition legality and "
                "returns a new immutable state snapshot; it does not "
                "decide when a transition should occur."
            ),

            "self_transition_rule": (
                "Self-transitions are not legal Runtime "
                "Orchestration lifecycle transitions."
            ),

            "terminal_rule": (
                "SUCCEEDED, FAILED, and CANCELLED are terminal and "
                "cannot transition to another orchestration state."
            ),

            "waiting_rule": (
                "WAITING is generic orchestration lifecycle evidence "
                "and does not itself resolve dependencies or readiness."
            ),

            "suspension_rule": (
                "SUSPENDED represents orchestration lifecycle state; "
                "suspension and resume eligibility belongs to 5.1.12."
            ),

            "recovery_rule": (
                "RECOVERING represents orchestration lifecycle state; "
                "recovery decisions belong to 5.1.13."
            ),

            "completion_rule": (
                "SUCCEEDED is a terminal state representation; "
                "completion determination belongs to 5.1.15."
            ),

            "cancellation_rule": (
                "CANCELLED is a terminal state representation; "
                "cancellation or termination determination belongs "
                "to 5.1.16."
            ),

            "readiness_boundary": (
                "READY and BLOCKED are not orchestration lifecycle "
                "states; readiness evaluation belongs to 5.1.6."
            ),

            "job_status_boundary": (
                "QUEUED, SCHEDULED, LEASED, RUNNING, DEAD_LETTER, "
                "and EXPIRED remain Universal Job or queue lifecycle "
                "semantics and are not 5.1.3 orchestration states."
            ),

            "coordination_boundary": (
                "UniversalWorkflowStatus remains a higher-layer "
                "Universal Coordination Framework authority and is "
                "not reused by Runtime Orchestration."
            ),

            "persistence_boundary": (
                "5.1.3 performs no persistence; orchestration state "
                "persistence belongs to 5.1.14."
            ),

            "prohibitions": (
                "does not reuse UniversalJobStatus as orchestration state",
                "does not reuse UniversalWorkflowStatus as orchestration state",
                "does not use queue membership as orchestration state",
                "does not use worker status as orchestration state",
                "does not define READY as orchestration state",
                "does not define BLOCKED as orchestration state",
                "does not define QUEUED as orchestration state",
                "does not define SCHEDULED as orchestration state",
                "does not define LEASED as orchestration state",
                "does not define RUNNING as orchestration state",
                "does not define DEAD_LETTER as orchestration state",
                "does not define EXPIRED as orchestration state",
                "does not define COMPLETING as orchestration state",
                "does not resolve dependencies",
                "does not determine readiness",
                "does not determine execution order",
                "does not perform fan-out",
                "does not perform fan-in",
                "does not evaluate conditional branches",
                "does not perform runtime handoffs",
                "does not track orchestration progress",
                "does not determine suspension eligibility",
                "does not restore checkpoints",
                "does not perform orchestration recovery decisions",
                "does not determine completion",
                "does not determine cancellation",
                "does not enqueue jobs",
                "does not claim jobs",
                "does not assign workers",
                "does not acquire worker leases",
                "does not register runtime handlers",
                "does not dispatch runtime handlers",
                "does not execute runtime handlers",
                "does not execute jobs",
                "does not import Universal Coordination Framework",
                "does not invoke pipeline coordinators",
                "does not access Runtime State Store",
                "does not persist orchestration state",
                "does not use wall clock",
                "does not perform filesystem I/O",
                "does not perform network I/O",
            ),
        }
    )


__all__ = [
    "UNIVERSAL_ORCHESTRATION_STATE_MODEL_VERSION",
    "UNIVERSAL_ORCHESTRATION_STATE_MODEL_SCHEMA_VERSION",
    "UniversalOrchestrationStateModelError",
    "UniversalOrchestrationState",
    "TERMINAL_UNIVERSAL_ORCHESTRATION_STATES",
    "NON_TERMINAL_UNIVERSAL_ORCHESTRATION_STATES",
    "UNIVERSAL_ORCHESTRATION_STATE_TRANSITIONS",
    "normalize_universal_orchestration_state",
    "initial_universal_orchestration_state",
    "is_terminal_universal_orchestration_state",
    "is_non_terminal_universal_orchestration_state",
    "allowed_universal_orchestration_transitions",
    "can_transition_universal_orchestration_state",
    "validate_universal_orchestration_state_transition",
    "UniversalOrchestrationStateSnapshot",
    "create_initial_universal_orchestration_state_snapshot",
    "create_universal_orchestration_state_snapshot",
    "transition_universal_orchestration_state",
    "explain_universal_orchestration_state_model_v1",
]
