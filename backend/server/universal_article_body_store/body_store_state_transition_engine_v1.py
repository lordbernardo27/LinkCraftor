"""Universal Article Body Store State Transition Engine.

Phase 9.1.2 responsibility:

- define legal Body Store lifecycle transitions;
- validate requested transitions;
- enforce optimistic transition-count checks;
- update lifecycle-state records atomically;
- preserve immutable body identity;
- record the most recent transition event.

This engine changes lifecycle metadata only.

It does not:

- read, write, archive, restore, quarantine, or delete article bodies;
- call the Body Store Writer, Manager, Repository, Runtime, Worker, or Queue;
- enforce retention, expiration, archive, restore, or cleanup policies;
- register runtime handlers.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from backend.server.universal_article_body_store.body_store_lifecycle_state_manager_v1 import (
    BODY_STORE_LIFECYCLE_STATES,
    BodyStoreLifecycleStateError,
    _contains_forbidden_body_content,
    _record_path,
    _require_mapping,
    _require_string,
    _write_json_atomic,
    read_body_store_lifecycle_state_v1,
    validate_body_store_lifecycle_record_v1,
)


BODY_STORE_STATE_TRANSITION_ENGINE_VERSION = (
    "universal_article_body_store_state_transition_engine_v1"
)

BODY_STORE_LEGAL_STATE_TRANSITIONS = {
    "ACTIVE": (
        "SUPERSEDED",
        "RETAINED",
        "ARCHIVED",
        "QUARANTINED",
        "PENDING_DELETION",
    ),

    "SUPERSEDED": (
        "RETAINED",
        "ARCHIVED",
        "PENDING_DELETION",
        "QUARANTINED",
    ),

    "RETAINED": (
        "ACTIVE",
        "ARCHIVED",
        "PENDING_DELETION",
        "QUARANTINED",
    ),

    "ARCHIVED": (
        "RESTORED",
        "PENDING_DELETION",
        "QUARANTINED",
    ),

    "QUARANTINED": (
        "RESTORED",
        "RETAINED",
        "PENDING_DELETION",
    ),

    "RESTORED": (
        "ACTIVE",
        "RETAINED",
        "QUARANTINED",
    ),

    "PENDING_DELETION": (
        "RETAINED",
        "DELETED",
    ),

    "DELETED": (),
}


class BodyStoreStateTransitionError(
    BodyStoreLifecycleStateError
):
    """Base error for invalid Body Store state transitions."""


class BodyStoreStateTransitionConflictError(
    BodyStoreStateTransitionError
):
    """Raised when optimistic transition state does not match."""


class BodyStoreIllegalStateTransitionError(
    BodyStoreStateTransitionError
):
    """Raised when a requested lifecycle transition is illegal."""


def _now_iso() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _normalize_state(
    value: Any,
    *,
    field_name: str,
) -> str:
    normalized = _require_string(
        value,
        field_name=field_name,
    ).upper()

    if normalized not in BODY_STORE_LIFECYCLE_STATES:
        raise BodyStoreStateTransitionError(
            "Unsupported lifecycle state: "
            + normalized
        )

    return normalized


def list_allowed_body_store_transitions_v1(
    current_state: str,
) -> tuple[str, ...]:
    """Return the legal next states for one lifecycle state."""

    normalized_state = _normalize_state(
        current_state,
        field_name="current_state",
    )

    return BODY_STORE_LEGAL_STATE_TRANSITIONS[
        normalized_state
    ]


def can_transition_body_store_state_v1(
    *,
    current_state: str,
    target_state: str,
) -> bool:
    """Return whether a requested lifecycle transition is legal."""

    normalized_current = _normalize_state(
        current_state,
        field_name="current_state",
    )

    normalized_target = _normalize_state(
        target_state,
        field_name="target_state",
    )

    return normalized_target in (
        BODY_STORE_LEGAL_STATE_TRANSITIONS[
            normalized_current
        ]
    )


def validate_body_store_state_transition_v1(
    *,
    current_state: str,
    target_state: str,
) -> dict[str, Any]:
    """Validate one requested lifecycle transition."""

    normalized_current = _normalize_state(
        current_state,
        field_name="current_state",
    )

    normalized_target = _normalize_state(
        target_state,
        field_name="target_state",
    )

    if normalized_current == normalized_target:
        raise BodyStoreIllegalStateTransitionError(
            "Lifecycle state must change during a transition."
        )

    allowed_targets = (
        BODY_STORE_LEGAL_STATE_TRANSITIONS[
            normalized_current
        ]
    )

    if normalized_target not in allowed_targets:
        raise BodyStoreIllegalStateTransitionError(
            "Illegal Body Store lifecycle transition: "
            + normalized_current
            + " -> "
            + normalized_target
        )

    return {
        "transition_engine_version":
            BODY_STORE_STATE_TRANSITION_ENGINE_VERSION,

        "current_state":
            normalized_current,

        "target_state":
            normalized_target,

        "allowed":
            True,

        "allowed_targets":
            list(
                allowed_targets
            ),
    }


def transition_body_store_lifecycle_state_v1(
    *,
    project_root: str | Path,
    workspace_id: str,
    lifecycle_record_id: str,
    target_state: str,
    transition_reason: str,
    actor_type: str,
    actor_id: str,
    source: str,
    expected_current_state: str | None = None,
    expected_transition_count: int | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Atomically transition one persisted lifecycle-state record."""

    current_record = (
        read_body_store_lifecycle_state_v1(
            project_root=project_root,
            workspace_id=workspace_id,
            lifecycle_record_id=lifecycle_record_id,
        )
    )

    current_state = current_record[
        "lifecycle_state"
    ]

    current_transition_count = int(
        current_record.get(
            "transition_count",
            0,
        )
    )

    if expected_current_state is not None:
        normalized_expected_state = _normalize_state(
            expected_current_state,
            field_name="expected_current_state",
        )

        if normalized_expected_state != current_state:
            raise BodyStoreStateTransitionConflictError(
                "Lifecycle current-state check failed. Expected "
                + normalized_expected_state
                + " but found "
                + current_state
                + "."
            )

    if expected_transition_count is not None:
        if (
            not isinstance(
                expected_transition_count,
                int,
            )
            or isinstance(
                expected_transition_count,
                bool,
            )
            or expected_transition_count < 0
        ):
            raise BodyStoreStateTransitionError(
                "expected_transition_count must be a non-negative integer."
            )

        if (
            expected_transition_count
            != current_transition_count
        ):
            raise BodyStoreStateTransitionConflictError(
                "Lifecycle transition-count check failed. Expected "
                + str(
                    expected_transition_count
                )
                + " but found "
                + str(
                    current_transition_count
                )
                + "."
            )

    transition_contract = (
        validate_body_store_state_transition_v1(
            current_state=current_state,
            target_state=target_state,
        )
    )

    normalized_reason = _require_string(
        transition_reason,
        field_name="transition_reason",
    )

    normalized_actor_type = _require_string(
        actor_type,
        field_name="actor_type",
    )

    normalized_actor_id = _require_string(
        actor_id,
        field_name="actor_id",
    )

    normalized_source = _require_string(
        source,
        field_name="source",
    )

    transition_metadata = (
        {}
        if metadata is None
        else dict(
            _require_mapping(
                metadata,
                field_name="metadata",
            )
        )
    )

    if _contains_forbidden_body_content(
        transition_metadata
    ):
        raise BodyStoreStateTransitionError(
            "Transition metadata must not contain article body content."
        )

    transitioned_at = _now_iso()

    transition_event = {
        "event_id":
            (
                "body_store_transition_"
                + uuid4().hex
            ),

        "engine_version":
            BODY_STORE_STATE_TRANSITION_ENGINE_VERSION,

        "from_state":
            current_state,

        "to_state":
            transition_contract[
                "target_state"
            ],

        "transition_reason":
            normalized_reason,

        "actor_type":
            normalized_actor_type,

        "actor_id":
            normalized_actor_id,

        "source":
            normalized_source,

        "transitioned_at":
            transitioned_at,

        "transition_number":
            current_transition_count
            + 1,

        "metadata":
            transition_metadata,

        "content_body_included":
            False,
    }

    updated_record = {
        **current_record,

        "lifecycle_state":
            transition_contract[
                "target_state"
            ],

        "previous_state":
            current_state,

        "state_reason":
            normalized_reason,

        "actor_type":
            normalized_actor_type,

        "actor_id":
            normalized_actor_id,

        "source":
            normalized_source,

        "updated_at":
            transitioned_at,

        "transition_count":
            current_transition_count
            + 1,

        "last_transition":
            transition_event,
    }

    validated_record = (
        validate_body_store_lifecycle_record_v1(
            updated_record
        )
    )

    path = _record_path(
        project_root=project_root,
        workspace_id=validated_record[
            "workspace_id"
        ],
        lifecycle_record_id=validated_record[
            "lifecycle_record_id"
        ],
    )

    _write_json_atomic(
        path,
        validated_record,
    )

    return {
        "transition_engine_version":
            BODY_STORE_STATE_TRANSITION_ENGINE_VERSION,

        "transition_applied":
            True,

        "event":
            transition_event,

        "record":
            validated_record,
    }
