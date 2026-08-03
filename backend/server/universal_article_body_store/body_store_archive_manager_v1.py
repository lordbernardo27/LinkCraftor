"""Universal Article Body Store Archive Manager.

Phase 9.1.5.1 responsibility:

- evaluate whether a lifecycle record is eligible for archival;
- consume certified retention and expiration decisions;
- validate source lifecycle state;
- produce a deterministic and immutable archive decision;
- preserve the required transition target: ARCHIVED.

This manager is advisory and read-only.

It does not:

- move or copy article-body files;
- modify lifecycle records;
- invoke the State Transition Engine;
- call the Writer, Repository, Runtime, Worker, or Queue;
- register runtime handlers;
- perform restore or cleanup operations.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.universal_article_body_store.body_store_expiration_manager_v1 import (
    evaluate_body_store_expiration_v1,
)

from backend.server.universal_article_body_store.body_store_retention_policy_contract_v1 import (
    validate_body_store_retention_policy_v1,
)


BODY_STORE_ARCHIVE_MANAGER_VERSION = (
    "universal_article_body_store_archive_manager_v1"
)

BODY_STORE_ARCHIVE_DECISION_SCHEMA_VERSION = (
    "body_store_archive_decision_v1"
)

BODY_STORE_ARCHIVE_ELIGIBLE_STATES = (
    "ACTIVE",
    "SUPERSEDED",
    "RETAINED",
)

BODY_STORE_ARCHIVE_INELIGIBLE_STATES = (
    "ARCHIVED",
    "QUARANTINED",
    "PENDING_DELETION",
    "DELETED",
    "RESTORED",
)

BODY_STORE_ARCHIVE_DECISION_STATUSES = (
    "ELIGIBLE",
    "BLOCKED",
    "ALREADY_ARCHIVED",
)


class BodyStoreArchiveManagerError(
    ValueError
):
    """Raised when an archive decision request is invalid."""


def _require_string(
    value: Any,
    *,
    field_name: str,
) -> str:
    if not isinstance(
        value,
        str,
    ):
        raise BodyStoreArchiveManagerError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise BodyStoreArchiveManagerError(
            field_name
            + " must not be empty."
        )

    return normalized


def _require_timestamp(
    value: Any,
    *,
    field_name: str,
) -> str:
    normalized = _require_string(
        value,
        field_name=field_name,
    )

    try:
        parsed = datetime.fromisoformat(
            normalized.replace(
                "Z",
                "+00:00",
            )
        )

    except ValueError as exc:
        raise BodyStoreArchiveManagerError(
            field_name
            + " must be a valid ISO-8601 timestamp."
        ) from exc

    if parsed.tzinfo is None:
        raise BodyStoreArchiveManagerError(
            field_name
            + " must include timezone information."
        )

    return parsed.astimezone(
        timezone.utc
    ).isoformat()


def _normalize_lifecycle_state(
    value: Any,
) -> str:
    normalized = _require_string(
        value,
        field_name="lifecycle_state",
    ).upper()

    supported = {
        *BODY_STORE_ARCHIVE_ELIGIBLE_STATES,
        *BODY_STORE_ARCHIVE_INELIGIBLE_STATES,
    }

    if normalized not in supported:
        raise BodyStoreArchiveManagerError(
            "Unsupported lifecycle state: "
            + normalized
        )

    return normalized


def _build_archive_decision_id(
    *,
    retention_policy_id: str,
    lifecycle_record_id: str,
    lifecycle_state: str,
    evaluated_at: str,
) -> str:
    material = json.dumps(
        {
            "retention_policy_id":
                retention_policy_id,

            "lifecycle_record_id":
                lifecycle_record_id,

            "lifecycle_state":
                lifecycle_state,

            "evaluated_at":
                evaluated_at,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    )

    return (
        "body_store_archive_decision_"
        + hashlib.sha256(
            material.encode(
                "utf-8"
            )
        ).hexdigest()
    )


def evaluate_body_store_archive_eligibility_v1(
    *,
    policy: Mapping[str, Any],
    lifecycle_state: str,
    evaluated_at: str,
    archive_reason: str,
    actor_type: str,
    actor_id: str,
    source: str,
) -> Mapping[str, Any]:
    """Return one immutable advisory archive decision."""

    policy_before = json.dumps(
        dict(
            policy
        ),
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )

    validated_policy = (
        validate_body_store_retention_policy_v1(
            policy
        )
    )

    normalized_state = (
        _normalize_lifecycle_state(
            lifecycle_state
        )
    )

    normalized_evaluated_at = (
        _require_timestamp(
            evaluated_at,
            field_name="evaluated_at",
        )
    )

    normalized_reason = _require_string(
        archive_reason,
        field_name="archive_reason",
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

    expiration_result = (
        evaluate_body_store_expiration_v1(
            policy=validated_policy,
            evaluated_at=normalized_evaluated_at,
        )
    )

    hold_active = expiration_result[
        "hold_active"
    ]

    if normalized_state == "ARCHIVED":
        archive_status = "ALREADY_ARCHIVED"
        archive_eligible = False
        blocking_reason = (
            "The lifecycle record is already archived."
        )

    elif normalized_state not in (
        BODY_STORE_ARCHIVE_ELIGIBLE_STATES
    ):
        archive_status = "BLOCKED"
        archive_eligible = False
        blocking_reason = (
            "Lifecycle state "
            + normalized_state
            + " is not eligible for archival."
        )

    elif hold_active:
        archive_status = "BLOCKED"
        archive_eligible = False
        blocking_reason = (
            "An active retention hold blocks archival."
        )

    else:
        archive_status = "ELIGIBLE"
        archive_eligible = True
        blocking_reason = None

    result = {
        "schema_version":
            BODY_STORE_ARCHIVE_DECISION_SCHEMA_VERSION,

        "manager_version":
            BODY_STORE_ARCHIVE_MANAGER_VERSION,

        "success":
            True,

        "archive_decision_id":
            _build_archive_decision_id(
                retention_policy_id=validated_policy[
                    "retention_policy_id"
                ],
                lifecycle_record_id=validated_policy[
                    "lifecycle_record_id"
                ],
                lifecycle_state=normalized_state,
                evaluated_at=normalized_evaluated_at,
            ),

        "retention_policy_id":
            validated_policy[
                "retention_policy_id"
            ],

        "lifecycle_record_id":
            validated_policy[
                "lifecycle_record_id"
            ],

        "workspace_id":
            validated_policy[
                "workspace_id"
            ],

        "current_lifecycle_state":
            normalized_state,

        "required_target_state":
            "ARCHIVED",

        "archive_status":
            archive_status,

        "archive_eligible":
            archive_eligible,

        "archive_reason":
            normalized_reason,

        "blocking_reason":
            blocking_reason,

        "hold_active":
            hold_active,

        "retention_expired":
            expiration_result[
                "retention_expired"
            ],

        "expiration_status":
            expiration_result[
                "expiration_status"
            ],

        "actor_type":
            normalized_actor_type,

        "actor_id":
            normalized_actor_id,

        "source":
            normalized_source,

        "evaluated_at":
            normalized_evaluated_at,

        "physical_archive_performed":
            False,

        "lifecycle_transition_performed":
            False,

        "input_policy_mutated":
            False,

        "content_body_included":
            False,
    }

    policy_after = json.dumps(
        dict(
            policy
        ),
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )

    if policy_before != policy_after:
        raise BodyStoreArchiveManagerError(
            "Retention policy input was mutated during archive evaluation."
        )

    return MappingProxyType(
        result
    )
