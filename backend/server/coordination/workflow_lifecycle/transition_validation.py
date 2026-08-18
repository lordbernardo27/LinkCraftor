"""
LinkCraftor Universal Coordination Framework
Phase 3.2 - Transition Validation
============================================

Pure validation of requested workflow lifecycle transitions against the
frozen Phase 3.1 Workflow State Machine.

This component does NOT:
- define lifecycle graph edges;
- define workflow statuses;
- mutate workflow state;
- record lifecycle history;
- enforce terminal-state protection;
- persist lifecycle state;
- execute coordinators or Runtime jobs;
- perform recovery.
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
    has_transition_edge,
)


# ============================================================================
# 1. Component identity
# ============================================================================

TRANSITION_VALIDATION_VERSION: Final[str] = (
    "transition_validation_v3.2.0"
)

TRANSITION_VALIDATION_SCHEMA_VERSION: Final[str] = (
    "transition_validation_schema_v1"
)


# ============================================================================
# 2. Violation codes
# ============================================================================

VIOLATION_CURRENT_STATE_INVALID: Final[str] = (
    "current_state_invalid"
)

VIOLATION_REQUESTED_STATE_INVALID: Final[str] = (
    "requested_state_invalid"
)

VIOLATION_TRANSITION_NOT_DECLARED: Final[str] = (
    "transition_not_declared"
)


# ============================================================================
# 3. Errors
# ============================================================================

class TransitionValidationError(
    ValueError
):
    """Base error for Transition Validation."""


class InvalidWorkflowTransitionError(
    TransitionValidationError
):
    """Raised when a required workflow transition is invalid."""

    def __init__(
        self,
        result: "TransitionValidationResult",
    ) -> None:

        self.result = result

        super().__init__(
            (
                "invalid workflow transition: "
                f"{result.current_state!r} -> "
                f"{result.requested_state!r}"
            )
        )


# ============================================================================
# 4. Immutable helpers
# ============================================================================

def _freeze(
    value: Any,
) -> Any:

    if isinstance(
        value,
        Mapping,
    ):

        return MappingProxyType(
            {
                str(key): _freeze(item)
                for key, item
                in value.items()
            }
        )

    if isinstance(
        value,
        list,
    ):

        return tuple(
            _freeze(item)
            for item
            in value
        )

    if isinstance(
        value,
        tuple,
    ):

        return tuple(
            _freeze(item)
            for item
            in value
        )

    return value


def _raw_state_evidence(
    value: Any,
) -> Any:

    if isinstance(
        value,
        UniversalWorkflowStatus,
    ):

        return value.value

    if isinstance(
        value,
        str,
    ):

        return value

    return repr(
        value
    )


def _violation(
    *,
    code: str,
    message: str,
    field: str,
    current_state: Any,
    requested_state: Any,
) -> Mapping[
    str,
    Any,
]:

    return MappingProxyType(
        {
            "code": code,
            "message": message,
            "field": field,
            "current_state": (
                _raw_state_evidence(
                    current_state
                )
            ),
            "requested_state": (
                _raw_state_evidence(
                    requested_state
                )
            ),
        }
    )


# ============================================================================
# 5. Immutable validation result
# ============================================================================

@dataclass(
    frozen=True,
    slots=True,
)
class TransitionValidationResult:

    current_state: Optional[
        UniversalWorkflowStatus
    ]

    requested_state: Optional[
        UniversalWorkflowStatus
    ]

    is_valid: bool

    violations: Tuple[
        Mapping[
            str,
            Any,
        ],
        ...,
    ]

    checked_rule_count: int

    validation_version: str = (
        TRANSITION_VALIDATION_VERSION
    )

    def __post_init__(
        self,
    ) -> None:

        object.__setattr__(
            self,
            "violations",
            tuple(
                _freeze(item)
                for item
                in self.violations
            ),
        )

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
                "is_valid":
                    self.is_valid,
                "violations":
                    self.violations,
                "checked_rule_count":
                    self.checked_rule_count,
                "validation_version":
                    self.validation_version,
            }
        )


# ============================================================================
# 6. Transition validation
# ============================================================================

def validate_workflow_transition(
    current_state: Any,
    requested_state: Any,
) -> TransitionValidationResult:
    """
    Validate one requested lifecycle transition.

    Rules:

    1. current_state must resolve to UniversalWorkflowStatus.
    2. requested_state must resolve to UniversalWorkflowStatus.
    3. current_state -> requested_state must exist in frozen Phase 3.1.

    This function does not mutate workflow state.
    """

    violations = []

    normalized_current: Optional[
        UniversalWorkflowStatus
    ] = None

    normalized_requested: Optional[
        UniversalWorkflowStatus
    ] = None

    checked_rule_count = 0


    # ------------------------------------------------------------------------
    # Rule 1 - current state
    # ------------------------------------------------------------------------

    checked_rule_count += 1

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

        violations.append(
            _violation(
                code=(
                    VIOLATION_CURRENT_STATE_INVALID
                ),
                message=(
                    "current_state does not resolve "
                    "to UniversalWorkflowStatus"
                ),
                field="current_state",
                current_state=current_state,
                requested_state=requested_state,
            )
        )

        return TransitionValidationResult(
            current_state=None,
            requested_state=None,
            is_valid=False,
            violations=tuple(
                violations
            ),
            checked_rule_count=(
                checked_rule_count
            ),
        )


    # ------------------------------------------------------------------------
    # Rule 2 - requested state
    # ------------------------------------------------------------------------

    checked_rule_count += 1

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

        violations.append(
            _violation(
                code=(
                    VIOLATION_REQUESTED_STATE_INVALID
                ),
                message=(
                    "requested_state does not resolve "
                    "to UniversalWorkflowStatus"
                ),
                field="requested_state",
                current_state=(
                    normalized_current
                ),
                requested_state=(
                    requested_state
                ),
            )
        )

        return TransitionValidationResult(
            current_state=(
                normalized_current
            ),
            requested_state=None,
            is_valid=False,
            violations=tuple(
                violations
            ),
            checked_rule_count=(
                checked_rule_count
            ),
        )


    # ------------------------------------------------------------------------
    # Rule 3 - canonical edge
    # ------------------------------------------------------------------------

    checked_rule_count += 1

    if not has_transition_edge(
        normalized_current,
        normalized_requested,
    ):

        violations.append(
            _violation(
                code=(
                    VIOLATION_TRANSITION_NOT_DECLARED
                ),
                message=(
                    "requested lifecycle transition "
                    "is not declared by the frozen "
                    "Phase 3.1 Workflow State Machine"
                ),
                field="transition",
                current_state=(
                    normalized_current
                ),
                requested_state=(
                    normalized_requested
                ),
            )
        )


    return TransitionValidationResult(
        current_state=(
            normalized_current
        ),
        requested_state=(
            normalized_requested
        ),
        is_valid=(
            not violations
        ),
        violations=tuple(
            violations
        ),
        checked_rule_count=(
            checked_rule_count
        ),
    )


# ============================================================================
# 7. Require-style API
# ============================================================================

def require_valid_workflow_transition(
    current_state: Any,
    requested_state: Any,
) -> TransitionValidationResult:
    """
    Require a valid workflow lifecycle transition.

    Returns the immutable validation result when valid.

    Raises InvalidWorkflowTransitionError when invalid.
    """

    result = (
        validate_workflow_transition(
            current_state,
            requested_state,
        )
    )

    if not result.is_valid:

        raise InvalidWorkflowTransitionError(
            result
        )

    return result


# ============================================================================
# 8. Architecture declaration
# ============================================================================

def explain_transition_validation_v3_2(
) -> Mapping[
    str,
    Any,
]:

    return MappingProxyType(
        {
            "phase":
                "3.2",

            "component":
                "Transition Validation",

            "version":
                TRANSITION_VALIDATION_VERSION,

            "schema_version":
                TRANSITION_VALIDATION_SCHEMA_VERSION,

            "state_machine_version":
                WORKFLOW_STATE_MACHINE_VERSION,

            "validation_direction":
                "current_state_to_requested_state",

            "validation_rules": (
                (
                    "current_state resolves to "
                    "UniversalWorkflowStatus"
                ),
                (
                    "requested_state resolves to "
                    "UniversalWorkflowStatus"
                ),
                (
                    "transition edge exists in "
                    "frozen Phase 3.1"
                ),
            ),

            "violation_codes": (
                VIOLATION_CURRENT_STATE_INVALID,
                VIOLATION_REQUESTED_STATE_INVALID,
                VIOLATION_TRANSITION_NOT_DECLARED,
            ),

            "owns": (
                "requested workflow transition validation",
                (
                    "current/requested lifecycle "
                    "state normalization"
                ),
                (
                    "exact edge validation against "
                    "frozen Phase 3.1"
                ),
                (
                    "deterministic transition-validation "
                    "result"
                ),
                (
                    "immutable validation "
                    "violations/evidence"
                ),
                (
                    "canonical invalid-transition error "
                    "for require-style API"
                ),
                "validation inspection/explanation",
            ),

            "does_not_own": (
                "workflow lifecycle graph definition",
                "workflow status vocabulary",
                "workflow status mutation",
                "workflow object reconstruction",
                "lifecycle history",
                "transition timestamp generation",
                "terminal-state protection enforcement",
                "workflow persistence",
                "checkpointing",
                "pause execution behavior",
                "resume execution behavior",
                "recovery execution",
                "recovery policy",
                "coordinator execution",
                "Runtime Registration",
                "Runtime jobs",
                "dependency planning",
                "stage result handoff",
            ),

            "future_authority": {
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
    "TRANSITION_VALIDATION_VERSION",
    "TRANSITION_VALIDATION_SCHEMA_VERSION",
    "VIOLATION_CURRENT_STATE_INVALID",
    "VIOLATION_REQUESTED_STATE_INVALID",
    "VIOLATION_TRANSITION_NOT_DECLARED",
    "TransitionValidationError",
    "InvalidWorkflowTransitionError",
    "TransitionValidationResult",
    "validate_workflow_transition",
    "require_valid_workflow_transition",
    "explain_transition_validation_v3_2",
]
