"""
LinkCraftor Universal Coordination Framework
Phase 3.1 - Workflow State Machine
============================================

Canonical workflow lifecycle MODEL.

This component reuses the frozen UniversalWorkflowStatus vocabulary from
the Universal Workflow Contract.

It defines:
- canonical state classification;
- canonical terminal/non-terminal classification;
- canonical lifecycle transition edges;
- deterministic immutable lifecycle-model inspection.

It does NOT:
- validate a requested workflow transition;
- mutate workflow status;
- record lifecycle history;
- enforce terminal-state protection;
- persist lifecycle state;
- execute workflows/coordinators;
- create Runtime jobs;
- perform recovery.

Those authorities belong to later UCF phases.
"""

from __future__ import annotations

from types import MappingProxyType

from typing import (
    Any,
    Final,
    Mapping,
    Tuple,
)

from backend.server.coordination.universal_workflows.contract import (
    UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
    TERMINAL_WORKFLOW_STATUSES,
    UniversalWorkflowStatus,
)


# ============================================================================
# 1. Component identity
# ============================================================================

WORKFLOW_STATE_MACHINE_VERSION: Final[str] = (
    "workflow_state_machine_v3.1.0"
)

WORKFLOW_STATE_MACHINE_SCHEMA_VERSION: Final[str] = (
    "workflow_state_machine_schema_v1"
)


# ============================================================================
# 2. Canonical state sets
# ============================================================================

_CANONICAL_WORKFLOW_STATES: Final[
    Tuple[
        UniversalWorkflowStatus,
        ...,
    ]
] = (
    UniversalWorkflowStatus.CREATED,
    UniversalWorkflowStatus.READY,
    UniversalWorkflowStatus.RUNNING,
    UniversalWorkflowStatus.WAITING,
    UniversalWorkflowStatus.PAUSED,
    UniversalWorkflowStatus.RECOVERING,
    UniversalWorkflowStatus.COMPLETED,
    UniversalWorkflowStatus.FAILED,
    UniversalWorkflowStatus.CANCELLED,
    UniversalWorkflowStatus.ABORTED,
)


_CANONICAL_TERMINAL_STATES: Final[
    Tuple[
        UniversalWorkflowStatus,
        ...,
    ]
] = tuple(
    state
    for state
    in _CANONICAL_WORKFLOW_STATES
    if state
    in TERMINAL_WORKFLOW_STATUSES
)


_CANONICAL_NON_TERMINAL_STATES: Final[
    Tuple[
        UniversalWorkflowStatus,
        ...,
    ]
] = tuple(
    state
    for state
    in _CANONICAL_WORKFLOW_STATES
    if state
    not in TERMINAL_WORKFLOW_STATUSES
)


# ============================================================================
# 3. Canonical lifecycle transition graph
# ============================================================================

_WORKFLOW_TRANSITION_GRAPH: Final[
    Mapping[
        UniversalWorkflowStatus,
        Tuple[
            UniversalWorkflowStatus,
            ...,
        ],
    ]
] = MappingProxyType(
    {
        UniversalWorkflowStatus.CREATED: (
            UniversalWorkflowStatus.READY,
            UniversalWorkflowStatus.CANCELLED,
            UniversalWorkflowStatus.ABORTED,
        ),

        UniversalWorkflowStatus.READY: (
            UniversalWorkflowStatus.RUNNING,
            UniversalWorkflowStatus.PAUSED,
            UniversalWorkflowStatus.CANCELLED,
            UniversalWorkflowStatus.ABORTED,
        ),

        UniversalWorkflowStatus.RUNNING: (
            UniversalWorkflowStatus.WAITING,
            UniversalWorkflowStatus.PAUSED,
            UniversalWorkflowStatus.RECOVERING,
            UniversalWorkflowStatus.COMPLETED,
            UniversalWorkflowStatus.FAILED,
            UniversalWorkflowStatus.CANCELLED,
            UniversalWorkflowStatus.ABORTED,
        ),

        UniversalWorkflowStatus.WAITING: (
            UniversalWorkflowStatus.RUNNING,
            UniversalWorkflowStatus.PAUSED,
            UniversalWorkflowStatus.RECOVERING,
            UniversalWorkflowStatus.FAILED,
            UniversalWorkflowStatus.CANCELLED,
            UniversalWorkflowStatus.ABORTED,
        ),

        UniversalWorkflowStatus.PAUSED: (
            UniversalWorkflowStatus.READY,
            UniversalWorkflowStatus.RUNNING,
            UniversalWorkflowStatus.RECOVERING,
            UniversalWorkflowStatus.FAILED,
            UniversalWorkflowStatus.CANCELLED,
            UniversalWorkflowStatus.ABORTED,
        ),

        UniversalWorkflowStatus.RECOVERING: (
            UniversalWorkflowStatus.READY,
            UniversalWorkflowStatus.RUNNING,
            UniversalWorkflowStatus.WAITING,
            UniversalWorkflowStatus.FAILED,
            UniversalWorkflowStatus.CANCELLED,
            UniversalWorkflowStatus.ABORTED,
        ),

        UniversalWorkflowStatus.COMPLETED: (),
        UniversalWorkflowStatus.FAILED: (),
        UniversalWorkflowStatus.CANCELLED: (),
        UniversalWorkflowStatus.ABORTED: (),
    }
)


# ============================================================================
# 4. State semantics
# ============================================================================

_WORKFLOW_STATE_SEMANTICS: Final[
    Mapping[
        UniversalWorkflowStatus,
        str,
    ]
] = MappingProxyType(
    {
        UniversalWorkflowStatus.CREATED:
            "Workflow instance exists but has not yet reached readiness.",

        UniversalWorkflowStatus.READY:
            "Workflow prerequisites are satisfied and execution may begin.",

        UniversalWorkflowStatus.RUNNING:
            "Workflow is actively progressing through coordinated work.",

        UniversalWorkflowStatus.WAITING:
            "Workflow cannot currently advance because required coordination "
            "evidence, dependency completion, branch/join completion, or an "
            "external event is pending.",

        UniversalWorkflowStatus.PAUSED:
            "Workflow has been deliberately suspended.",

        UniversalWorkflowStatus.RECOVERING:
            "Workflow is in non-terminal recovery handling before either "
            "returning to an executable/waiting state or reaching terminal "
            "failure.",

        UniversalWorkflowStatus.COMPLETED:
            "Workflow completed successfully.",

        UniversalWorkflowStatus.FAILED:
            "Workflow reached terminal failure.",

        UniversalWorkflowStatus.CANCELLED:
            "Workflow was terminated through controlled cancellation.",

        UniversalWorkflowStatus.ABORTED:
            "Workflow was terminated outside normal controlled completion "
            "or cancellation progression.",
    }
)


# ============================================================================
# 5. Normalization
# ============================================================================

def coerce_workflow_state(
    state: Any,
) -> UniversalWorkflowStatus:
    """
    Convert a status value into the frozen canonical workflow status enum.

    This performs status normalization only.

    It does not validate any lifecycle transition.
    """

    return UniversalWorkflowStatus.coerce(
        state
    )


# ============================================================================
# 6. State inspection
# ============================================================================

def workflow_states(
) -> Tuple[
    UniversalWorkflowStatus,
    ...,
]:
    """Return every canonical workflow lifecycle state."""

    return _CANONICAL_WORKFLOW_STATES


def terminal_workflow_states(
) -> Tuple[
    UniversalWorkflowStatus,
    ...,
]:
    """Return canonical terminal states."""

    return _CANONICAL_TERMINAL_STATES


def non_terminal_workflow_states(
) -> Tuple[
    UniversalWorkflowStatus,
    ...,
]:
    """Return canonical non-terminal states."""

    return _CANONICAL_NON_TERMINAL_STATES


def is_terminal_workflow_state(
    state: Any,
) -> bool:
    """
    Return whether a state is terminal according to the frozen contract.

    Classification only; this does not enforce terminal-state protection.
    """

    normalized = coerce_workflow_state(
        state
    )

    return (
        normalized
        in TERMINAL_WORKFLOW_STATUSES
    )


def is_non_terminal_workflow_state(
    state: Any,
) -> bool:

    return not is_terminal_workflow_state(
        state
    )


def workflow_state_semantics(
    state: Any,
) -> str:

    normalized = coerce_workflow_state(
        state
    )

    return _WORKFLOW_STATE_SEMANTICS[
        normalized
    ]


# ============================================================================
# 7. Transition-model inspection
# ============================================================================

def allowed_next_states(
    state: Any,
) -> Tuple[
    UniversalWorkflowStatus,
    ...,
]:
    """
    Return lifecycle edges declared by the canonical state-machine model.

    MODEL INSPECTION ONLY.

    This function is not Phase 3.2 Transition Validation.
    """

    normalized = coerce_workflow_state(
        state
    )

    return _WORKFLOW_TRANSITION_GRAPH[
        normalized
    ]


def has_transition_edge(
    from_state: Any,
    to_state: Any,
) -> bool:
    """
    Return whether one edge exists in the canonical lifecycle graph.

    MODEL INSPECTION ONLY.

    This does not authorize, perform, or persist a workflow transition.
    """

    normalized_from = (
        coerce_workflow_state(
            from_state
        )
    )

    normalized_to = (
        coerce_workflow_state(
            to_state
        )
    )

    return (
        normalized_to
        in _WORKFLOW_TRANSITION_GRAPH[
            normalized_from
        ]
    )


def transition_edges(
) -> Tuple[
    Tuple[
        UniversalWorkflowStatus,
        UniversalWorkflowStatus,
    ],
    ...,
]:
    """Return all canonical transition edges deterministically."""

    return tuple(
        (
            from_state,
            to_state,
        )
        for from_state
        in _CANONICAL_WORKFLOW_STATES
        for to_state
        in _WORKFLOW_TRANSITION_GRAPH[
            from_state
        ]
    )


# ============================================================================
# 8. State-machine snapshot
# ============================================================================

def workflow_state_machine_snapshot(
) -> Mapping[
    str,
    Any,
]:
    """
    Return deterministic immutable lifecycle-model evidence.
    """

    transition_model = tuple(
        (
            state.value,
            tuple(
                next_state.value
                for next_state
                in _WORKFLOW_TRANSITION_GRAPH[
                    state
                ]
            ),
        )
        for state
        in _CANONICAL_WORKFLOW_STATES
    )

    semantics = tuple(
        (
            state.value,
            _WORKFLOW_STATE_SEMANTICS[
                state
            ],
        )
        for state
        in _CANONICAL_WORKFLOW_STATES
    )

    return MappingProxyType(
        {
            "state_machine_version":
                WORKFLOW_STATE_MACHINE_VERSION,

            "schema_version":
                WORKFLOW_STATE_MACHINE_SCHEMA_VERSION,

            "workflow_contract_version":
                UNIVERSAL_WORKFLOW_CONTRACT_VERSION,

            "state_count":
                len(
                    _CANONICAL_WORKFLOW_STATES
                ),

            "terminal_state_count":
                len(
                    _CANONICAL_TERMINAL_STATES
                ),

            "non_terminal_state_count":
                len(
                    _CANONICAL_NON_TERMINAL_STATES
                ),

            "transition_edge_count":
                len(
                    transition_edges()
                ),

            "states":
                tuple(
                    state.value
                    for state
                    in _CANONICAL_WORKFLOW_STATES
                ),

            "terminal_states":
                tuple(
                    state.value
                    for state
                    in _CANONICAL_TERMINAL_STATES
                ),

            "non_terminal_states":
                tuple(
                    state.value
                    for state
                    in _CANONICAL_NON_TERMINAL_STATES
                ),

            "transition_model":
                transition_model,

            "state_semantics":
                semantics,

            "transition_validation":
                False,

            "workflow_mutation":
                False,

            "history_recording":
                False,

            "terminal_protection_enforcement":
                False,

            "persistence":
                False,

            "runtime_execution":
                False,

            "recovery_execution":
                False,
        }
    )


# ============================================================================
# 9. Architecture declaration
# ============================================================================

def explain_workflow_state_machine_v3_1(
) -> Mapping[
    str,
    Any,
]:

    return MappingProxyType(
        {
            "phase":
                "3.1",

            "component":
                "Workflow State Machine",

            "version":
                WORKFLOW_STATE_MACHINE_VERSION,

            "model_authority":
                "canonical_lifecycle_graph",

            "status_authority":
                (
                    "UniversalWorkflowStatus "
                    "from frozen Universal Workflow Contract"
                ),

            "owns": (
                "canonical workflow lifecycle state reference",
                "canonical terminal-state classification",
                "canonical non-terminal-state classification",
                "canonical lifecycle transition graph",
                "immutable transition-model declaration",
                "deterministic state inspection",
                "deterministic transition inspection",
                "state classification helpers",
                "state semantics",
                "allowed-next-state model inspection",
            ),

            "does_not_own": (
                "runtime transition request validation",
                "transition rejection policy",
                "workflow status mutation",
                "lifecycle history recording",
                "transition timestamps",
                "terminal-state protection enforcement",
                "workflow persistence",
                "checkpoints",
                "pause execution behavior",
                "resume execution behavior",
                "recovery execution",
                "failure recovery policy",
                "coordinator invocation",
                "workflow execution",
                "Runtime Registration",
                "Runtime jobs",
                "stage dependency planning",
                "stage result handoff",
            ),

            "future_authority": {
                "3.2":
                    "Transition Validation",

                "3.3":
                    "Lifecycle History",

                "3.4":
                    "Terminal-State Protection",

                "8.0":
                    "Workflow State Persistence",

                "9.0":
                    "Coordination Recovery",
            },
        }
    )


__all__ = [
    "WORKFLOW_STATE_MACHINE_VERSION",
    "WORKFLOW_STATE_MACHINE_SCHEMA_VERSION",
    "coerce_workflow_state",
    "workflow_states",
    "terminal_workflow_states",
    "non_terminal_workflow_states",
    "is_terminal_workflow_state",
    "is_non_terminal_workflow_state",
    "workflow_state_semantics",
    "allowed_next_states",
    "has_transition_edge",
    "transition_edges",
    "workflow_state_machine_snapshot",
    "explain_workflow_state_machine_v3_1",
]
