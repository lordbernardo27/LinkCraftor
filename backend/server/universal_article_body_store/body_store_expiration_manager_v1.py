"""Universal Article Body Store Expiration Manager.

Phase 9.1.4.1 responsibility:

- evaluate expiration from certified retention-policy decisions;
- classify finite, indefinite, held, active, and expired records;
- calculate remaining retention time;
- produce deterministic and immutable expiration results.

This manager is read-only.

It does not:

- modify lifecycle records;
- transition lifecycle states;
- archive, restore, clean up, or delete article bodies;
- call the Body Store Writer, Repository, Runtime, Worker, or Queue;
- register runtime handlers.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping

from backend.server.universal_article_body_store.body_store_retention_policy_contract_v1 import (
    validate_body_store_retention_policy_v1,
)

from backend.server.universal_article_body_store.body_store_retention_policy_engine_v1 import (
    evaluate_body_store_retention_policy_v1,
)


BODY_STORE_EXPIRATION_MANAGER_VERSION = (
    "universal_article_body_store_expiration_manager_v1"
)

BODY_STORE_EXPIRATION_RESULT_SCHEMA_VERSION = (
    "body_store_expiration_result_v1"
)

BODY_STORE_EXPIRATION_STATUSES = (
    "ACTIVE",
    "EXPIRED",
    "ON_HOLD",
    "INDEFINITE",
)


class BodyStoreExpirationManagerError(
    ValueError
):
    """Raised when expiration evaluation input is invalid."""


def _require_timestamp(
    value: Any,
    *,
    field_name: str,
) -> tuple[str, datetime]:
    if not isinstance(
        value,
        str,
    ):
        raise BodyStoreExpirationManagerError(
            field_name
            + " must be an ISO-8601 string."
        )

    normalized = value.strip()

    if not normalized:
        raise BodyStoreExpirationManagerError(
            field_name
            + " must not be empty."
        )

    try:
        parsed = datetime.fromisoformat(
            normalized.replace(
                "Z",
                "+00:00",
            )
        )

    except ValueError as exc:
        raise BodyStoreExpirationManagerError(
            field_name
            + " must be a valid ISO-8601 timestamp."
        ) from exc

    if parsed.tzinfo is None:
        raise BodyStoreExpirationManagerError(
            field_name
            + " must include timezone information."
        )

    normalized_datetime = parsed.astimezone(
        timezone.utc
    )

    return (
        normalized_datetime.isoformat(),
        normalized_datetime,
    )


def _optional_timestamp(
    value: Any,
    *,
    field_name: str,
) -> tuple[str | None, datetime | None]:
    if value is None:
        return None, None

    return _require_timestamp(
        value,
        field_name=field_name,
    )


def _build_expiration_evaluation_id(
    *,
    policy: Mapping[str, Any],
    evaluated_at: str,
) -> str:
    material = json.dumps(
        {
            "retention_policy_id":
                policy[
                    "retention_policy_id"
                ],

            "lifecycle_record_id":
                policy[
                    "lifecycle_record_id"
                ],

            "workspace_id":
                policy[
                    "workspace_id"
                ],

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
        "body_store_expiration_evaluation_"
        + hashlib.sha256(
            material.encode(
                "utf-8"
            )
        ).hexdigest()
    )


def calculate_body_store_expiration_window_v1(
    *,
    policy: Mapping[str, Any],
    evaluated_at: str,
) -> dict[str, Any]:
    """Calculate remaining or elapsed retention time."""

    validated_policy = (
        validate_body_store_retention_policy_v1(
            policy
        )
    )

    normalized_evaluated_at, evaluated_at_dt = (
        _require_timestamp(
            evaluated_at,
            field_name="evaluated_at",
        )
    )

    retain_until, retain_until_dt = (
        _optional_timestamp(
            validated_policy.get(
                "retain_until"
            ),
            field_name="retain_until",
        )
    )

    if retain_until_dt is None:
        remaining_seconds = None
        elapsed_seconds = None

    elif evaluated_at_dt < retain_until_dt:
        remaining_seconds = int(
            (
                retain_until_dt
                - evaluated_at_dt
            ).total_seconds()
        )

        elapsed_seconds = 0

    else:
        remaining_seconds = 0

        elapsed_seconds = int(
            (
                evaluated_at_dt
                - retain_until_dt
            ).total_seconds()
        )

    return {
        "evaluated_at":
            normalized_evaluated_at,

        "retain_until":
            retain_until,

        "remaining_seconds":
            remaining_seconds,

        "elapsed_since_expiration_seconds":
            elapsed_seconds,
    }


def evaluate_body_store_expiration_v1(
    *,
    policy: Mapping[str, Any],
    evaluated_at: str,
) -> Mapping[str, Any]:
    """Produce one immutable expiration evaluation."""

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

    normalized_evaluated_at, _ = (
        _require_timestamp(
            evaluated_at,
            field_name="evaluated_at",
        )
    )

    retention_result = (
        evaluate_body_store_retention_policy_v1(
            policy=validated_policy,
            evaluated_at=normalized_evaluated_at,
        )
    )

    expiration_window = (
        calculate_body_store_expiration_window_v1(
            policy=validated_policy,
            evaluated_at=normalized_evaluated_at,
        )
    )

    if retention_result[
        "hold_active"
    ]:
        expiration_status = "ON_HOLD"
        expiration_effective = False
        reason = (
            "Expiration is not effective while an active hold applies."
        )

    elif (
        retention_result[
            "retention_class"
        ]
        == "INDEFINITE"
    ):
        expiration_status = "INDEFINITE"
        expiration_effective = False
        reason = (
            "Indefinite retention has no expiration timestamp."
        )

    elif retention_result[
        "retention_expired"
    ]:
        expiration_status = "EXPIRED"
        expiration_effective = True
        reason = (
            "The retention deadline has passed and no active hold applies."
        )

    else:
        expiration_status = "ACTIVE"
        expiration_effective = False
        reason = (
            "The retention deadline has not been reached."
        )

    result = {
        "schema_version":
            BODY_STORE_EXPIRATION_RESULT_SCHEMA_VERSION,

        "manager_version":
            BODY_STORE_EXPIRATION_MANAGER_VERSION,

        "success":
            True,

        "expiration_evaluation_id":
            _build_expiration_evaluation_id(
                policy=validated_policy,
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

        "retention_class":
            validated_policy[
                "retention_class"
            ],

        "expiration_status":
            expiration_status,

        "expiration_effective":
            expiration_effective,

        "retention_expired":
            retention_result[
                "retention_expired"
            ],

        "retention_satisfied":
            retention_result[
                "retention_satisfied"
            ],

        "hold_active":
            retention_result[
                "hold_active"
            ],

        "retain_until":
            expiration_window[
                "retain_until"
            ],

        "remaining_seconds":
            expiration_window[
                "remaining_seconds"
            ],

        "elapsed_since_expiration_seconds":
            expiration_window[
                "elapsed_since_expiration_seconds"
            ],

        "deletion_eligible":
            retention_result[
                "deletion_eligible"
            ],

        "reason":
            reason,

        "evaluated_at":
            normalized_evaluated_at,

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
        raise BodyStoreExpirationManagerError(
            "Retention policy input was mutated during expiration evaluation."
        )

    return MappingProxyType(
        result
    )
