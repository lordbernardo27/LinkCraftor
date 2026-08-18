"""
LinkCraftor Universal Coordination Framework
Phase 3.3 - Lifecycle History
=============================================

Canonical immutable lifecycle transition-history evidence.

This component records representations of valid workflow lifecycle
transitions. It does not perform workflow transitions.

Authority boundaries:

- Phase 3.1 owns the lifecycle graph.
- Phase 3.2 owns requested-transition legality.
- Phase 3.3 owns immutable lifecycle history evidence and sequence integrity.
- Phase 3.4 owns terminal-state protection.
- Phase 8 owns durable persistence/checkpointing.
- Phase 9 owns recovery.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import (
    Any,
    Final,
    Iterable,
    Mapping,
    Optional,
    Tuple,
)

from backend.server.coordination.universal_workflows.contract import (
    UniversalWorkflowStatus,
)

from backend.server.coordination.workflow_lifecycle.state_machine import (
    WORKFLOW_STATE_MACHINE_VERSION,
)

from backend.server.coordination.workflow_lifecycle.transition_validation import (
    TRANSITION_VALIDATION_VERSION,
    validate_workflow_transition,
)


# ============================================================================
# 1. Component identity
# ============================================================================

LIFECYCLE_HISTORY_VERSION: Final[str] = (
    "lifecycle_history_v3.3.0"
)

LIFECYCLE_HISTORY_SCHEMA_VERSION: Final[str] = (
    "lifecycle_history_schema_v1"
)

LIFECYCLE_HISTORY_ENTRY_FIELD_COUNT: Final[int] = 13


# ============================================================================
# 2. Errors
# ============================================================================

class LifecycleHistoryError(
    ValueError
):
    """Base error for Lifecycle History."""


class InvalidLifecycleHistoryEntryError(
    LifecycleHistoryError
):
    """Raised when a lifecycle-history entry is invalid."""


class DuplicateLifecycleHistoryEventError(
    LifecycleHistoryError
):
    """Raised when event_id is duplicated within one history sequence."""


class LifecycleHistorySequenceError(
    LifecycleHistoryError
):
    """Raised when lifecycle-history sequence integrity is violated."""


# ============================================================================
# 3. Immutable helpers
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

    if isinstance(
        value,
        set,
    ):

        return frozenset(
            _freeze(item)
            for item
            in value
        )

    return value


def _require_nonempty_string(
    value: Any,
    *,
    field_name: str,
) -> str:

    if not isinstance(
        value,
        str,
    ):

        raise InvalidLifecycleHistoryEntryError(
            f"{field_name} must be a string"
        )

    normalized = value.strip()

    if not normalized:

        raise InvalidLifecycleHistoryEntryError(
            f"{field_name} must be non-empty"
        )

    return normalized


def _optional_string(
    value: Any,
    *,
    field_name: str,
) -> Optional[str]:

    if value is None:
        return None

    if not isinstance(
        value,
        str,
    ):

        raise InvalidLifecycleHistoryEntryError(
            (
                f"{field_name} must be "
                "a string or None"
            )
        )

    normalized = value.strip()

    if not normalized:
        return None

    return normalized


def _normalize_occurred_at(
    value: Any,
) -> str:

    if not isinstance(
        value,
        str,
    ):

        raise InvalidLifecycleHistoryEntryError(
            "occurred_at must be a string"
        )

    text = value.strip()

    if not text:

        raise InvalidLifecycleHistoryEntryError(
            "occurred_at must be non-empty"
        )

    candidate = text

    if candidate.endswith(
        "Z"
    ):

        candidate = (
            candidate[:-1]
            + "+00:00"
        )

    try:

        parsed = datetime.fromisoformat(
            candidate
        )

    except ValueError as exc:

        raise InvalidLifecycleHistoryEntryError(
            (
                "occurred_at must be a valid "
                "ISO-8601 timestamp"
            )
        ) from exc

    if (
        parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):

        raise InvalidLifecycleHistoryEntryError(
            "occurred_at must be timezone-aware"
        )

    return parsed.isoformat()


def _occurred_at_datetime(
    value: str,
) -> datetime:

    return datetime.fromisoformat(
        value
    )


# ============================================================================
# 4. Lifecycle history entry
# ============================================================================

@dataclass(
    frozen=True,
    slots=True,
)
class LifecycleHistoryEntry:

    event_id: str
    workflow_id: str
    correlation_id: str

    from_state: UniversalWorkflowStatus
    to_state: UniversalWorkflowStatus

    occurred_at: str

    reason: Optional[str]
    source: Optional[str]
    actor_id: Optional[str]

    metadata: Mapping[
        str,
        Any,
    ]

    transition_validation_version: str
    state_machine_version: str
    history_version: str

    def __post_init__(
        self,
    ) -> None:

        event_id = _require_nonempty_string(
            self.event_id,
            field_name="event_id",
        )

        workflow_id = _require_nonempty_string(
            self.workflow_id,
            field_name="workflow_id",
        )

        correlation_id = _require_nonempty_string(
            self.correlation_id,
            field_name="correlation_id",
        )

        if not isinstance(
            self.from_state,
            UniversalWorkflowStatus,
        ):

            raise InvalidLifecycleHistoryEntryError(
                (
                    "from_state must be "
                    "UniversalWorkflowStatus"
                )
            )

        if not isinstance(
            self.to_state,
            UniversalWorkflowStatus,
        ):

            raise InvalidLifecycleHistoryEntryError(
                (
                    "to_state must be "
                    "UniversalWorkflowStatus"
                )
            )

        occurred_at = _normalize_occurred_at(
            self.occurred_at
        )

        reason = _optional_string(
            self.reason,
            field_name="reason",
        )

        source = _optional_string(
            self.source,
            field_name="source",
        )

        actor_id = _optional_string(
            self.actor_id,
            field_name="actor_id",
        )

        if not isinstance(
            self.metadata,
            Mapping,
        ):

            raise InvalidLifecycleHistoryEntryError(
                "metadata must be a mapping"
            )

        if (
            self.transition_validation_version
            != TRANSITION_VALIDATION_VERSION
        ):

            raise InvalidLifecycleHistoryEntryError(
                (
                    "transition_validation_version "
                    "must match frozen Phase 3.2"
                )
            )

        if (
            self.state_machine_version
            != WORKFLOW_STATE_MACHINE_VERSION
        ):

            raise InvalidLifecycleHistoryEntryError(
                (
                    "state_machine_version must "
                    "match frozen Phase 3.1"
                )
            )

        if (
            self.history_version
            != LIFECYCLE_HISTORY_VERSION
        ):

            raise InvalidLifecycleHistoryEntryError(
                (
                    "history_version must match "
                    "canonical Phase 3.3"
                )
            )

        validation = (
            validate_workflow_transition(
                self.from_state,
                self.to_state,
            )
        )

        if not validation.is_valid:

            raise InvalidLifecycleHistoryEntryError(
                (
                    "history entry transition is "
                    "not valid under frozen "
                    "Phase 3.2 Transition Validation"
                )
            )

        object.__setattr__(
            self,
            "event_id",
            event_id,
        )

        object.__setattr__(
            self,
            "workflow_id",
            workflow_id,
        )

        object.__setattr__(
            self,
            "correlation_id",
            correlation_id,
        )

        object.__setattr__(
            self,
            "occurred_at",
            occurred_at,
        )

        object.__setattr__(
            self,
            "reason",
            reason,
        )

        object.__setattr__(
            self,
            "source",
            source,
        )

        object.__setattr__(
            self,
            "actor_id",
            actor_id,
        )

        object.__setattr__(
            self,
            "metadata",
            _freeze(
                self.metadata
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
                "event_id":
                    self.event_id,

                "workflow_id":
                    self.workflow_id,

                "correlation_id":
                    self.correlation_id,

                "from_state":
                    self.from_state.value,

                "to_state":
                    self.to_state.value,

                "occurred_at":
                    self.occurred_at,

                "reason":
                    self.reason,

                "source":
                    self.source,

                "actor_id":
                    self.actor_id,

                "metadata":
                    self.metadata,

                "transition_validation_version":
                    self.transition_validation_version,

                "state_machine_version":
                    self.state_machine_version,

                "history_version":
                    self.history_version,
            }
        )


# ============================================================================
# 5. Entry creation
# ============================================================================

def create_lifecycle_history_entry(
    *,
    event_id: Any,
    workflow_id: Any,
    correlation_id: Any,
    from_state: Any,
    to_state: Any,
    occurred_at: Any,
    reason: Any = None,
    source: Any = None,
    actor_id: Any = None,
    metadata: Optional[
        Mapping[
            str,
            Any,
        ]
    ] = None,
) -> LifecycleHistoryEntry:
    """
    Create one immutable valid lifecycle-history entry.

    Transition legality is delegated to frozen Phase 3.2.
    """

    validation = (
        validate_workflow_transition(
            from_state,
            to_state,
        )
    )

    if not validation.is_valid:

        codes = tuple(
            violation[
                "code"
            ]
            for violation
            in validation.violations
        )

        raise InvalidLifecycleHistoryEntryError(
            (
                "cannot record invalid workflow "
                "transition; violations="
                f"{codes!r}"
            )
        )

    assert (
        validation.current_state
        is not None
    )

    assert (
        validation.requested_state
        is not None
    )

    return LifecycleHistoryEntry(
        event_id=event_id,
        workflow_id=workflow_id,
        correlation_id=correlation_id,
        from_state=(
            validation.current_state
        ),
        to_state=(
            validation.requested_state
        ),
        occurred_at=occurred_at,
        reason=reason,
        source=source,
        actor_id=actor_id,
        metadata=(
            {}
            if metadata is None
            else metadata
        ),
        transition_validation_version=(
            TRANSITION_VALIDATION_VERSION
        ),
        state_machine_version=(
            WORKFLOW_STATE_MACHINE_VERSION
        ),
        history_version=(
            LIFECYCLE_HISTORY_VERSION
        ),
    )


# ============================================================================
# 6. History validation result
# ============================================================================

@dataclass(
    frozen=True,
    slots=True,
)
class LifecycleHistoryValidationResult:

    is_valid: bool

    violations: Tuple[
        str,
        ...,
    ]

    checked_rule_count: int

    entry_count: int

    history_version: str = (
        LIFECYCLE_HISTORY_VERSION
    )

    def to_dict(
        self,
    ) -> Mapping[
        str,
        Any,
    ]:

        return MappingProxyType(
            {
                "is_valid":
                    self.is_valid,

                "violations":
                    self.violations,

                "checked_rule_count":
                    self.checked_rule_count,

                "entry_count":
                    self.entry_count,

                "history_version":
                    self.history_version,
            }
        )


# ============================================================================
# 7. Sequence validation
# ============================================================================

def validate_lifecycle_history(
    history: Iterable[
        LifecycleHistoryEntry
    ],
) -> LifecycleHistoryValidationResult:
    """
    Validate one immutable lifecycle-history sequence.

    Nine canonical rules are evaluated.
    """

    try:

        entries = tuple(
            history
        )

    except TypeError:

        return LifecycleHistoryValidationResult(
            is_valid=False,
            violations=(
                (
                    "history must be "
                    "an iterable"
                ),
            ),
            checked_rule_count=1,
            entry_count=0,
        )

    violations = []

    checked_rule_count = 0


    # Rule 1 - entry type
    checked_rule_count += 1

    invalid_indexes = tuple(
        index
        for index, entry
        in enumerate(
            entries
        )
        if not isinstance(
            entry,
            LifecycleHistoryEntry,
        )
    )

    if invalid_indexes:

        violations.append(
            (
                "history contains non-"
                "LifecycleHistoryEntry items "
                f"at indexes {invalid_indexes!r}"
            )
        )

        return LifecycleHistoryValidationResult(
            is_valid=False,
            violations=tuple(
                violations
            ),
            checked_rule_count=(
                checked_rule_count
            ),
            entry_count=len(
                entries
            ),
        )


    # Rule 2 - unique event_id
    checked_rule_count += 1

    event_ids = tuple(
        entry.event_id
        for entry in entries
    )

    if (
        len(
            set(
                event_ids
            )
        )
        != len(
            event_ids
        )
    ):

        violations.append(
            "event_id values must be unique"
        )


    # Rule 3 - workflow consistency
    checked_rule_count += 1

    workflow_ids = {
        entry.workflow_id
        for entry in entries
    }

    if len(
        workflow_ids
    ) > 1:

        violations.append(
            (
                "workflow_id must remain "
                "identical across history"
            )
        )


    # Rule 4 - correlation consistency
    checked_rule_count += 1

    correlation_ids = {
        entry.correlation_id
        for entry in entries
    }

    if len(
        correlation_ids
    ) > 1:

        violations.append(
            (
                "correlation_id must remain "
                "identical across history"
            )
        )


    # Rule 5 - non-decreasing chronology
    checked_rule_count += 1

    for previous, current in zip(
        entries,
        entries[
            1:
        ],
    ):

        if (
            _occurred_at_datetime(
                current.occurred_at
            )
            <
            _occurred_at_datetime(
                previous.occurred_at
            )
        ):

            violations.append(
                (
                    "occurred_at must be "
                    "non-decreasing"
                )
            )

            break


    # Rule 6 - lifecycle continuity
    checked_rule_count += 1

    for previous, current in zip(
        entries,
        entries[
            1:
        ],
    ):

        if (
            previous.to_state
            != current.from_state
        ):

            violations.append(
                (
                    "adjacent lifecycle history "
                    "entries are not continuous: "
                    f"{previous.event_id!r} "
                    f"ends at "
                    f"{previous.to_state.value}, "
                    f"but {current.event_id!r} "
                    f"starts at "
                    f"{current.from_state.value}"
                )
            )

            break


    # Rule 7 - every transition remains valid under 3.2
    checked_rule_count += 1

    for entry in entries:

        validation = (
            validate_workflow_transition(
                entry.from_state,
                entry.to_state,
            )
        )

        if not validation.is_valid:

            violations.append(
                (
                    "history contains a transition "
                    "invalid under frozen Phase 3.2: "
                    f"{entry.event_id!r}"
                )
            )

            break


    # Rule 8 - exact 3.2 provenance
    checked_rule_count += 1

    if any(
        entry.transition_validation_version
        != TRANSITION_VALIDATION_VERSION
        for entry in entries
    ):

        violations.append(
            (
                "history contains non-canonical "
                "Transition Validation provenance"
            )
        )


    # Rule 9 - exact 3.1 provenance
    checked_rule_count += 1

    if any(
        entry.state_machine_version
        != WORKFLOW_STATE_MACHINE_VERSION
        for entry in entries
    ):

        violations.append(
            (
                "history contains non-canonical "
                "Workflow State Machine provenance"
            )
        )


    return LifecycleHistoryValidationResult(
        is_valid=(
            not violations
        ),
        violations=tuple(
            violations
        ),
        checked_rule_count=(
            checked_rule_count
        ),
        entry_count=len(
            entries
        ),
    )


# ============================================================================
# 8. Immutable append
# ============================================================================

def append_lifecycle_history(
    history: Iterable[
        LifecycleHistoryEntry
    ],
    entry: LifecycleHistoryEntry,
) -> Tuple[
    LifecycleHistoryEntry,
    ...,
]:
    """
    Append one entry by returning a new immutable tuple.

    The input history is never mutated.
    """

    if not isinstance(
        entry,
        LifecycleHistoryEntry,
    ):

        raise InvalidLifecycleHistoryEntryError(
            (
                "entry must be "
                "LifecycleHistoryEntry"
            )
        )

    entries = tuple(
        history
    )

    existing = (
        validate_lifecycle_history(
            entries
        )
    )

    if not existing.is_valid:

        raise LifecycleHistorySequenceError(
            (
                "existing lifecycle history "
                f"is invalid: "
                f"{existing.violations!r}"
            )
        )

    if any(
        existing_entry.event_id
        == entry.event_id
        for existing_entry
        in entries
    ):

        raise DuplicateLifecycleHistoryEventError(
            (
                "duplicate lifecycle-history "
                f"event_id: {entry.event_id!r}"
            )
        )

    if entries:

        last = entries[-1]

        if (
            last.workflow_id
            != entry.workflow_id
        ):

            raise LifecycleHistorySequenceError(
                (
                    "workflow_id mismatch between "
                    "history and appended entry"
                )
            )

        if (
            last.correlation_id
            != entry.correlation_id
        ):

            raise LifecycleHistorySequenceError(
                (
                    "correlation_id mismatch between "
                    "history and appended entry"
                )
            )

        if (
            _occurred_at_datetime(
                entry.occurred_at
            )
            <
            _occurred_at_datetime(
                last.occurred_at
            )
        ):

            raise LifecycleHistorySequenceError(
                (
                    "appended occurred_at cannot "
                    "precede the last history event"
                )
            )

        if (
            last.to_state
            != entry.from_state
        ):

            raise LifecycleHistorySequenceError(
                (
                    "appended lifecycle transition "
                    "does not continue from the "
                    "last recorded state"
                )
            )

    candidate = (
        entries
        + (
            entry,
        )
    )

    result = (
        validate_lifecycle_history(
            candidate
        )
    )

    if not result.is_valid:

        raise LifecycleHistorySequenceError(
            (
                "appended lifecycle history "
                f"is invalid: "
                f"{result.violations!r}"
            )
        )

    return candidate


# ============================================================================
# 9. Deterministic explicit sorting
# ============================================================================

def sort_lifecycle_history(
    history: Iterable[
        LifecycleHistoryEntry
    ],
) -> Tuple[
    LifecycleHistoryEntry,
    ...,
]:
    """
    Explicitly sort history by occurred_at then event_id.

    No other API silently reorders lifecycle history.
    """

    entries = tuple(
        history
    )

    if any(
        not isinstance(
            entry,
            LifecycleHistoryEntry,
        )
        for entry in entries
    ):

        raise LifecycleHistorySequenceError(
            (
                "history contains non-"
                "LifecycleHistoryEntry items"
            )
        )

    return tuple(
        sorted(
            entries,
            key=lambda entry: (
                _occurred_at_datetime(
                    entry.occurred_at
                ),
                entry.event_id,
            ),
        )
    )


# ============================================================================
# 10. Snapshot
# ============================================================================

def lifecycle_history_snapshot(
    history: Iterable[
        LifecycleHistoryEntry
    ],
) -> Mapping[
    str,
    Any,
]:

    entries = tuple(
        history
    )

    validation = (
        validate_lifecycle_history(
            entries
        )
    )

    return MappingProxyType(
        {
            "history_version":
                LIFECYCLE_HISTORY_VERSION,

            "schema_version":
                LIFECYCLE_HISTORY_SCHEMA_VERSION,

            "entry_field_count":
                LIFECYCLE_HISTORY_ENTRY_FIELD_COUNT,

            "transition_validation_version":
                TRANSITION_VALIDATION_VERSION,

            "state_machine_version":
                WORKFLOW_STATE_MACHINE_VERSION,

            "entry_count":
                len(
                    entries
                ),

            "is_valid":
                validation.is_valid,

            "validation_violations":
                validation.violations,

            "validation_rule_count":
                validation.checked_rule_count,

            "entries":
                tuple(
                    entry.to_dict()
                    for entry
                    in entries
                ),

            "workflow_mutation":
                False,

            "transition_execution":
                False,

            "terminal_protection_enforcement":
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
# 11. Architecture declaration
# ============================================================================

def explain_lifecycle_history_v3_3(
) -> Mapping[
    str,
    Any,
]:

    return MappingProxyType(
        {
            "phase":
                "3.3",

            "component":
                "Lifecycle History",

            "version":
                LIFECYCLE_HISTORY_VERSION,

            "schema_version":
                LIFECYCLE_HISTORY_SCHEMA_VERSION,

            "entry_field_count":
                LIFECYCLE_HISTORY_ENTRY_FIELD_COUNT,

            "transition_validation_version":
                TRANSITION_VALIDATION_VERSION,

            "state_machine_version":
                WORKFLOW_STATE_MACHINE_VERSION,

            "sequence_rule_count":
                9,

            "owns": (
                (
                    "canonical lifecycle "
                    "history-entry contract"
                ),
                (
                    "immutable transition-history "
                    "evidence"
                ),
                "valid-transition provenance",
                (
                    "history event identity "
                    "validation"
                ),
                (
                    "workflow identity "
                    "consistency"
                ),
                (
                    "correlation identity "
                    "consistency"
                ),
                "chronology validation",
                (
                    "adjacent-state continuity "
                    "validation"
                ),
                (
                    "deterministic history "
                    "inspection"
                ),
                "immutable append semantics",
                (
                    "immutable history "
                    "snapshot/evidence"
                ),
                (
                    "Lifecycle History "
                    "architecture explanation"
                ),
            ),

            "does_not_own": (
                "workflow lifecycle graph",
                "workflow status vocabulary",
                "requested-transition legality",
                "workflow status mutation",
                "transition execution",
                (
                    "terminal-state protection "
                    "enforcement"
                ),
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

            "future_authority": _freeze(
                {
                    "3.4":
                        "Terminal-State Protection",

                    "8.0":
                        "Workflow State Persistence",

                    "9.0":
                        "Coordination Recovery",

                    "10.5":
                        "Audit Trail",
                }
            ),
        }
    )


__all__ = [
    "LIFECYCLE_HISTORY_VERSION",
    "LIFECYCLE_HISTORY_SCHEMA_VERSION",
    "LIFECYCLE_HISTORY_ENTRY_FIELD_COUNT",
    "LifecycleHistoryError",
    "InvalidLifecycleHistoryEntryError",
    "DuplicateLifecycleHistoryEventError",
    "LifecycleHistorySequenceError",
    "LifecycleHistoryEntry",
    "LifecycleHistoryValidationResult",
    "create_lifecycle_history_entry",
    "validate_lifecycle_history",
    "append_lifecycle_history",
    "sort_lifecycle_history",
    "lifecycle_history_snapshot",
    "explain_lifecycle_history_v3_3",
]


