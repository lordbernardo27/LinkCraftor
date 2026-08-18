"""
LinkCraftor Universal Coordination Framework
Phase 3.4 - Terminal-State Protection
=============================================

Explicit lifecycle-finality protection for canonical terminal workflow states.

This component does not define workflow statuses or lifecycle edges.

Authority:
- Phase 3.1 owns terminal classification and lifecycle graph.
- Phase 3.2 owns requested-transition legality.
- Phase 3.3 owns lifecycle-history evidence.
- Phase 3.4 owns explicit terminal-state mutation protection.

No workflow object is mutated here.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import (
    Any,
    Final,
    Mapping,
    Optional,
    Tuple,
)

from backend.server.coordination.universal_workflows.contract import (
    UniversalWorkflowContractError,
    UniversalWorkflowStatus,
)

from backend.server.coordination.workflow_lifecycle.state_machine import (
    WORKFLOW_STATE_MACHINE_VERSION,
    coerce_workflow_state,
    is_terminal_workflow_state,
    terminal_workflow_states,
)

from backend.server.coordination.workflow_lifecycle.transition_validation import (
    TRANSITION_VALIDATION_VERSION,
    VIOLATION_CURRENT_STATE_INVALID,
    VIOLATION_REQUESTED_STATE_INVALID,
    VIOLATION_TRANSITION_NOT_DECLARED,
    validate_workflow_transition,
)


# ============================================================================
# 1. Component identity
# ============================================================================

TERMINAL_STATE_PROTECTION_VERSION: Final[str] = (
    "terminal_state_protection_v3.4.0"
)

TERMINAL_STATE_PROTECTION_SCHEMA_VERSION: Final[str] = (
    "terminal_state_protection_schema_v1"
)

TERMINAL_STATE_PROTECTION_RESULT_FIELD_COUNT: Final[int] = 10


# ============================================================================
# 2. Canonical protection code
# ============================================================================

TERMINAL_STATE_MUTATION_PROHIBITED: Final[str] = (
    "terminal_state_mutation_prohibited"
)


# ============================================================================
# 3. Errors
# ============================================================================

class TerminalStateProtectionError(
    ValueError
):
    """Base error for Terminal-State Protection."""


class TerminalStateMutationProhibitedError(
    TerminalStateProtectionError
):
    """Raised when mutation is requested from a terminal workflow state."""

    def __init__(
        self,
        result: "TerminalStateProtectionResult",
    ) -> None:

        self.result = result

        super().__init__(
            (
                "workflow lifecycle mutation is prohibited "
                f"from terminal state "
                f"{result.current_state!r}"
            )
        )


class InvalidTerminalStateProtectionRequestError(
    TerminalStateProtectionError
):
    """Raised when a required mutation request cannot be allowed."""

    def __init__(
        self,
        result: "TerminalStateProtectionResult",
    ) -> None:

        self.result = result

        super().__init__(
            (
                "workflow lifecycle mutation request "
                f"is invalid: {result.code!r}"
            )
        )


# ============================================================================
# 4. Immutable protection result
# ============================================================================

@dataclass(
    frozen=True,
    slots=True,
)
class TerminalStateProtectionResult:

    current_state: Optional[
        UniversalWorkflowStatus
    ]

    requested_state: Optional[
        UniversalWorkflowStatus
    ]

    current_state_is_terminal: bool

    mutation_allowed: bool

    protection_triggered: bool

    code: Optional[str]

    reason: Optional[str]

    transition_validation_version: str

    state_machine_version: str

    protection_version: str

    def to_dict(
        self,
    ) -> Mapping[
        str,
        Any,
    ]:

        return MappingProxyType(
            {
                "current_state": (
                    self.current_state.value
                    if self.current_state
                    is not None
                    else None
                ),

                "requested_state": (
                    self.requested_state.value
                    if self.requested_state
                    is not None
                    else None
                ),

                "current_state_is_terminal":
                    self.current_state_is_terminal,

                "mutation_allowed":
                    self.mutation_allowed,

                "protection_triggered":
                    self.protection_triggered,

                "code":
                    self.code,

                "reason":
                    self.reason,

                "transition_validation_version":
                    self.transition_validation_version,

                "state_machine_version":
                    self.state_machine_version,

                "protection_version":
                    self.protection_version,
            }
        )


# ============================================================================
# 5. Result constructor
# ============================================================================

def _result(
    *,
    current_state: Optional[
        UniversalWorkflowStatus
    ],
    requested_state: Optional[
        UniversalWorkflowStatus
    ],
    current_state_is_terminal: bool,
    mutation_allowed: bool,
    protection_triggered: bool,
    code: Optional[str],
    reason: Optional[str],
) -> TerminalStateProtectionResult:

    return TerminalStateProtectionResult(
        current_state=current_state,
        requested_state=requested_state,
        current_state_is_terminal=(
            current_state_is_terminal
        ),
        mutation_allowed=(
            mutation_allowed
        ),
        protection_triggered=(
            protection_triggered
        ),
        code=code,
        reason=reason,
        transition_validation_version=(
            TRANSITION_VALIDATION_VERSION
        ),
        state_machine_version=(
            WORKFLOW_STATE_MACHINE_VERSION
        ),
        protection_version=(
            TERMINAL_STATE_PROTECTION_VERSION
        ),
    )


# ============================================================================
# 6. Terminal-state inspection
# ============================================================================

def inspect_terminal_state_protection(
    current_state: Any,
) -> TerminalStateProtectionResult:
    """
    Inspect whether one workflow lifecycle state is terminal-protected.

    This API does not require a requested target state.
    """

    try:

        normalized = (
            coerce_workflow_state(
                current_state
            )
        )

    except (
        UniversalWorkflowContractError,
        ValueError,
        TypeError,
    ):

        return _result(
            current_state=None,
            requested_state=None,
            current_state_is_terminal=False,
            mutation_allowed=False,
            protection_triggered=False,
            code=(
                VIOLATION_CURRENT_STATE_INVALID
            ),
            reason=(
                "current_state does not resolve "
                "to UniversalWorkflowStatus"
            ),
        )

    terminal = (
        is_terminal_workflow_state(
            normalized
        )
    )

    if terminal:

        return _result(
            current_state=normalized,
            requested_state=None,
            current_state_is_terminal=True,
            mutation_allowed=False,
            protection_triggered=True,
            code=(
                TERMINAL_STATE_MUTATION_PROHIBITED
            ),
            reason=(
                "workflow state is terminal and "
                "lifecycle mutation is prohibited"
            ),
        )

    return _result(
        current_state=normalized,
        requested_state=None,
        current_state_is_terminal=False,
        mutation_allowed=True,
        protection_triggered=False,
        code=None,
        reason=(
            "workflow state is non-terminal; "
            "terminal-state protection is not triggered"
        ),
    )


# ============================================================================
# 7. Mutation validation
# ============================================================================

def validate_terminal_state_mutation(
    current_state: Any,
    requested_state: Any,
) -> TerminalStateProtectionResult:
    """
    Validate a requested lifecycle mutation through the terminal guard.

    Processing order:

    1. Normalize current state.
    2. Normalize requested state.
    3. If current state is terminal, prohibit mutation immediately.
    4. Otherwise delegate edge legality to frozen Phase 3.2.

    No workflow mutation occurs here.
    """

    # ------------------------------------------------------------------------
    # Rule 1 - current-state normalization
    # ------------------------------------------------------------------------

    try:

        normalized_current = (
            coerce_workflow_state(
                current_state
            )
        )

    except (
        UniversalWorkflowContractError,
        ValueError,
        TypeError,
    ):

        return _result(
            current_state=None,
            requested_state=None,
            current_state_is_terminal=False,
            mutation_allowed=False,
            protection_triggered=False,
            code=(
                VIOLATION_CURRENT_STATE_INVALID
            ),
            reason=(
                "current_state does not resolve "
                "to UniversalWorkflowStatus"
            ),
        )


    # ------------------------------------------------------------------------
    # Rule 2 - explicit terminal-state protection
    # ------------------------------------------------------------------------

    if is_terminal_workflow_state(
        normalized_current
    ):

        normalized_requested = None

        try:

            normalized_requested = (
                coerce_workflow_state(
                    requested_state
                )
            )

        except (
            UniversalWorkflowContractError,
            ValueError,
            TypeError,
        ):

            pass

        return _result(
            current_state=(
                normalized_current
            ),
            requested_state=(
                normalized_requested
            ),
            current_state_is_terminal=True,
            mutation_allowed=False,
            protection_triggered=True,
            code=(
                TERMINAL_STATE_MUTATION_PROHIBITED
            ),
            reason=(
                "workflow has reached a canonical "
                "terminal state; lifecycle mutation "
                "is prohibited"
            ),
        )


    # ------------------------------------------------------------------------
    # Rule 3 - requested-state normalization
    # ------------------------------------------------------------------------

    try:

        normalized_requested = (
            coerce_workflow_state(
                requested_state
            )
        )

    except (
        UniversalWorkflowContractError,
        ValueError,
        TypeError,
    ):

        return _result(
            current_state=(
                normalized_current
            ),
            requested_state=None,
            current_state_is_terminal=False,
            mutation_allowed=False,
            protection_triggered=False,
            code=(
                VIOLATION_REQUESTED_STATE_INVALID
            ),
            reason=(
                "requested_state does not resolve "
                "to UniversalWorkflowStatus"
            ),
        )


    # ------------------------------------------------------------------------
    # Rule 4 - delegate edge legality to frozen Phase 3.2
    # ------------------------------------------------------------------------

    validation = (
        validate_workflow_transition(
            normalized_current,
            normalized_requested,
        )
    )

    if not validation.is_valid:

        violation = (
            validation.violations[
                0
            ]
            if validation.violations
            else None
        )

        code = (
            violation[
                "code"
            ]
            if violation
            is not None
            else VIOLATION_TRANSITION_NOT_DECLARED
        )

        reason = (
            violation[
                "message"
            ]
            if violation
            is not None
            else (
                "requested lifecycle transition "
                "is invalid under frozen Phase 3.2"
            )
        )

        return _result(
            current_state=(
                normalized_current
            ),
            requested_state=(
                normalized_requested
            ),
            current_state_is_terminal=False,
            mutation_allowed=False,
            protection_triggered=False,
            code=code,
            reason=reason,
        )

    return _result(
        current_state=(
            normalized_current
        ),
        requested_state=(
            normalized_requested
        ),
        current_state_is_terminal=False,
        mutation_allowed=True,
        protection_triggered=False,
        code=None,
        reason=(
            "current state is non-terminal and "
            "requested transition is valid under "
            "frozen Phase 3.2"
        ),
    )


# ============================================================================
# 8. Require-style guard
# ============================================================================

def require_terminal_state_mutation_allowed(
    current_state: Any,
    requested_state: Any,
) -> TerminalStateProtectionResult:
    """
    Require a lifecycle mutation request to pass Terminal-State Protection.

    Returns the immutable result when allowed.

    Raises:
    - TerminalStateMutationProhibitedError for a terminal-state mutation.
    - InvalidTerminalStateProtectionRequestError for invalid input or
      ordinary Phase-3.2 transition rejection.
    """

    result = (
        validate_terminal_state_mutation(
            current_state,
            requested_state,
        )
    )

    if result.mutation_allowed:

        return result

    if (
        result.protection_triggered
        and result.code
        == TERMINAL_STATE_MUTATION_PROHIBITED
    ):

        raise TerminalStateMutationProhibitedError(
            result
        )

    raise InvalidTerminalStateProtectionRequestError(
        result
    )


# ============================================================================
# 9. Snapshot
# ============================================================================

def terminal_state_protection_snapshot(
) -> Mapping[
    str,
    Any,
]:

    terminal_states = (
        terminal_workflow_states()
    )

    return MappingProxyType(
        {
            "protection_version":
                TERMINAL_STATE_PROTECTION_VERSION,

            "schema_version":
                TERMINAL_STATE_PROTECTION_SCHEMA_VERSION,

            "result_field_count":
                TERMINAL_STATE_PROTECTION_RESULT_FIELD_COUNT,

            "state_machine_version":
                WORKFLOW_STATE_MACHINE_VERSION,

            "transition_validation_version":
                TRANSITION_VALIDATION_VERSION,

            "terminal_states":
                tuple(
                    state.value
                    for state
                    in terminal_states
                ),

            "terminal_state_count":
                len(
                    terminal_states
                ),

            "protection_code":
                TERMINAL_STATE_MUTATION_PROHIBITED,

            "terminal_states_protected":
                True,

            "workflow_mutation":
                False,

            "transition_execution":
                False,

            "history_recording":
                False,

            "durable_persistence":
                False,

            "runtime_execution":
                False,

            "recovery_execution":
                False,

            "security_audit_trail":
                False,
        }
    )


# ============================================================================
# 10. Architecture declaration
# ============================================================================

_FUTURE_AUTHORITY: Final[
    Mapping[
        str,
        str,
    ]
] = MappingProxyType(
    {
        "3.5":
            "Lifecycle Certification",

        "8.0":
            "Workflow State Persistence",

        "9.0":
            "Coordination Recovery",

        "10.5":
            "Audit Trail",
    }
)


def explain_terminal_state_protection_v3_4(
) -> Mapping[
    str,
    Any,
]:

    return MappingProxyType(
        {
            "phase":
                "3.4",

            "component":
                "Terminal-State Protection",

            "version":
                TERMINAL_STATE_PROTECTION_VERSION,

            "schema_version":
                TERMINAL_STATE_PROTECTION_SCHEMA_VERSION,

            "result_field_count":
                TERMINAL_STATE_PROTECTION_RESULT_FIELD_COUNT,

            "state_machine_version":
                WORKFLOW_STATE_MACHINE_VERSION,

            "transition_validation_version":
                TRANSITION_VALIDATION_VERSION,

            "terminal_states":
                tuple(
                    state.value
                    for state
                    in terminal_workflow_states()
                ),

            "protection_code":
                TERMINAL_STATE_MUTATION_PROHIBITED,

            "protection_rules": (
                (
                    "current_state resolves to "
                    "UniversalWorkflowStatus"
                ),
                (
                    "requested_state resolves to "
                    "UniversalWorkflowStatus"
                ),
                (
                    "terminal current state prohibits "
                    "all lifecycle mutation"
                ),
                (
                    "non-terminal requested mutation "
                    "delegates edge legality to frozen "
                    "Phase 3.2"
                ),
            ),

            "owns": (
                (
                    "canonical terminal-state "
                    "immutability policy"
                ),
                (
                    "terminal lifecycle mutation "
                    "prohibition"
                ),
                "terminal protection inspection",
                (
                    "deterministic terminal "
                    "protection evidence"
                ),
                "terminal-state mutation guard",
                (
                    "canonical terminal protection "
                    "code/error"
                ),
                (
                    "composition with frozen Phase 3.2 "
                    "for non-terminal requests"
                ),
                (
                    "terminal protection "
                    "architecture explanation"
                ),
            ),

            "does_not_own": (
                "terminal-state vocabulary",
                "lifecycle graph",
                (
                    "requested-transition "
                    "edge legality"
                ),
                "workflow object mutation",
                "lifecycle history recording",
                "transition timestamp generation",
                "durable persistence",
                "checkpoints",
                "pause execution",
                "resume execution",
                "recovery execution",
                "recovery policy",
                "Runtime Registration",
                "Runtime jobs",
                "coordinator execution",
                "dependency planning",
                "stage result handoff",
                "security audit trail",
            ),

            "future_authority":
                _FUTURE_AUTHORITY,
        }
    )


__all__ = [
    "TERMINAL_STATE_PROTECTION_VERSION",
    "TERMINAL_STATE_PROTECTION_SCHEMA_VERSION",
    "TERMINAL_STATE_PROTECTION_RESULT_FIELD_COUNT",
    "TERMINAL_STATE_MUTATION_PROHIBITED",
    "TerminalStateProtectionError",
    "TerminalStateMutationProhibitedError",
    "InvalidTerminalStateProtectionRequestError",
    "TerminalStateProtectionResult",
    "inspect_terminal_state_protection",
    "validate_terminal_state_mutation",
    "require_terminal_state_mutation_allowed",
    "terminal_state_protection_snapshot",
    "explain_terminal_state_protection_v3_4",
]

