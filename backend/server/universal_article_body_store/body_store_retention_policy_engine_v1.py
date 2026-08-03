"""Universal Article Body Store Retention Policy Engine.

Phase 9.1.3.2 responsibility:

- consume a certified Body Store retention-policy record;
- evaluate retention expiration at a supplied timestamp;
- evaluate whether a hold is active;
- evaluate whether retention has been satisfied;
- evaluate deletion eligibility;
- return a deterministic, immutable decision mapping.

This engine is read-only.

It does not:

- persist retention decisions;
- modify lifecycle records;
- transition lifecycle states;
- read, write, archive, restore, or delete article bodies;
- call the Body Store Writer, Manager, Repository, Runtime, Worker, or Queue;
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


BODY_STORE_RETENTION_POLICY_ENGINE_VERSION = (
    "universal_article_body_store_retention_policy_engine_v1"
)

BODY_STORE_RETENTION_EVALUATION_SCHEMA_VERSION = (
    "body_store_retention_evaluation_v1"
)


class BodyStoreRetentionPolicyEngineError(
    ValueError
):
    """Raised when retention evaluation input is invalid."""


def _require_timestamp(
    value: Any,
    *,
    field_name: str,
) -> tuple[str, datetime]:
    if not isinstance(
        value,
        str,
    ):
        raise BodyStoreRetentionPolicyEngineError(
            field_name
            + " must be an ISO-8601 string."
        )

    normalized = value.strip()

    if not normalized:
        raise BodyStoreRetentionPolicyEngineError(
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
        raise BodyStoreRetentionPolicyEngineError(
            field_name
            + " must be a valid ISO-8601 timestamp."
        ) from exc

    if parsed.tzinfo is None:
        raise BodyStoreRetentionPolicyEngineError(
            field_name
            + " must include timezone information."
        )

    return (
        parsed.astimezone(
            timezone.utc
        ).isoformat(),
        parsed.astimezone(
            timezone.utc
        ),
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


def _evaluation_id(
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
        "body_store_retention_evaluation_"
        + hashlib.sha256(
            material.encode(
                "utf-8"
            )
        ).hexdigest()
    )


def evaluate_body_store_hold_status_v1(
    *,
    policy: Mapping[str, Any],
    evaluated_at: str,
) -> dict[str, Any]:
    """Evaluate whether the policy has an active hold."""

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

    hold_started_at, hold_started_dt = (
        _optional_timestamp(
            validated_policy.get(
                "hold_started_at"
            ),
            field_name="hold_started_at",
        )
    )

    hold_expires_at, hold_expires_dt = (
        _optional_timestamp(
            validated_policy.get(
                "hold_expires_at"
            ),
            field_name="hold_expires_at",
        )
    )

    declared_hold = (
        validated_policy[
            "is_on_hold"
        ]
        is True
    )

    hold_started = (
        hold_started_dt is None
        or evaluated_at_dt
        >= hold_started_dt
    )

    hold_not_expired = (
        hold_expires_dt is None
        or evaluated_at_dt
        < hold_expires_dt
    )

    hold_active = (
        declared_hold
        and hold_started
        and hold_not_expired
    )

    if hold_active:
        reason = (
            "An active "
            + str(
                validated_policy[
                    "hold_type"
                ]
            )
            + " hold blocks retention satisfaction "
            "and deletion eligibility."
        )

    elif declared_hold and not hold_started:
        reason = (
            "The declared hold has not started at the "
            "evaluation timestamp."
        )

    elif declared_hold and not hold_not_expired:
        reason = (
            "The declared hold expired before or at the "
            "evaluation timestamp."
        )

    else:
        reason = (
            "No active retention hold applies."
        )

    return {
        "evaluated_at":
            normalized_evaluated_at,

        "hold_declared":
            declared_hold,

        "hold_active":
            hold_active,

        "hold_type":
            validated_policy.get(
                "hold_type"
            ),

        "hold_reason":
            validated_policy.get(
                "hold_reason"
            ),

        "hold_started_at":
            hold_started_at,

        "hold_expires_at":
            hold_expires_at,

        "reason":
            reason,
    }


def calculate_body_store_retention_result_v1(
    *,
    policy: Mapping[str, Any],
    evaluated_at: str,
) -> dict[str, Any]:
    """Calculate retention status without mutating the policy."""

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

    hold_result = (
        evaluate_body_store_hold_status_v1(
            policy=validated_policy,
            evaluated_at=normalized_evaluated_at,
        )
    )

    retention_class = (
        validated_policy[
            "retention_class"
        ]
    )

    hold_active = (
        hold_result[
            "hold_active"
        ]
    )

    if retention_class == "INDEFINITE":
        retention_expired = False
        retention_satisfied = False
        retention_status = "RETAINED"
        reason = (
            "Indefinite retention does not expire."
        )

    elif hold_active:
        retention_expired = (
            retain_until_dt is not None
            and evaluated_at_dt
            >= retain_until_dt
        )

        retention_satisfied = False
        retention_status = "ON_HOLD"
        reason = hold_result[
            "reason"
        ]

    elif retain_until_dt is None:
        retention_expired = False
        retention_satisfied = False
        retention_status = "ACTIVE"
        reason = (
            "No finite retain-until timestamp exists."
        )

    elif evaluated_at_dt >= retain_until_dt:
        retention_expired = True
        retention_satisfied = True
        retention_status = "EXPIRED"
        reason = (
            "The retention period has expired and no active hold applies."
        )

    else:
        retention_expired = False
        retention_satisfied = False
        retention_status = "ACTIVE"
        reason = (
            "The retention period remains active."
        )

    return {
        "evaluated_at":
            normalized_evaluated_at,

        "retention_class":
            retention_class,

        "retention_status":
            retention_status,

        "retain_until":
            retain_until,

        "retention_expired":
            retention_expired,

        "retention_satisfied":
            retention_satisfied,

        "hold_active":
            hold_active,

        "hold_type":
            hold_result[
                "hold_type"
            ],

        "reason":
            reason,
    }


def evaluate_body_store_deletion_eligibility_v1(
    *,
    policy: Mapping[str, Any],
    evaluated_at: str,
) -> dict[str, Any]:
    """Evaluate advisory deletion eligibility."""

    validated_policy = (
        validate_body_store_retention_policy_v1(
            policy
        )
    )

    retention_result = (
        calculate_body_store_retention_result_v1(
            policy=validated_policy,
            evaluated_at=evaluated_at,
        )
    )

    retention_class = (
        validated_policy[
            "retention_class"
        ]
    )

    if retention_result[
        "hold_active"
    ]:
        deletion_eligible = False
        reason = (
            "Deletion is blocked by an active hold."
        )

    elif retention_class == "INDEFINITE":
        deletion_eligible = False
        reason = (
            "Deletion is blocked by indefinite retention."
        )

    elif not retention_result[
        "retention_satisfied"
    ]:
        deletion_eligible = False
        reason = (
            "Deletion is blocked because retention is not satisfied."
        )

    else:
        deletion_eligible = True
        reason = (
            "Retention is satisfied and no active hold blocks deletion."
        )

    return {
        **retention_result,

        "deletion_eligible":
            deletion_eligible,

        "eligibility_reason":
            reason,
    }


def evaluate_body_store_retention_policy_v1(
    *,
    policy: Mapping[str, Any],
    evaluated_at: str,
) -> Mapping[str, Any]:
    """Return one immutable canonical retention evaluation."""

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

    eligibility_result = (
        evaluate_body_store_deletion_eligibility_v1(
            policy=validated_policy,
            evaluated_at=normalized_evaluated_at,
        )
    )

    result = {
        "schema_version":
            BODY_STORE_RETENTION_EVALUATION_SCHEMA_VERSION,

        "engine_version":
            BODY_STORE_RETENTION_POLICY_ENGINE_VERSION,

        "success":
            True,

        "evaluation_id":
            _evaluation_id(
                policy=validated_policy,
                evaluated_at=normalized_evaluated_at,
            ),

        "lifecycle_record_id":
            validated_policy[
                "lifecycle_record_id"
            ],

        "workspace_id":
            validated_policy[
                "workspace_id"
            ],

        "retention_policy_id":
            validated_policy[
                "retention_policy_id"
            ],

        "retention_class":
            eligibility_result[
                "retention_class"
            ],

        "retention_status":
            eligibility_result[
                "retention_status"
            ],

        "retain_until":
            eligibility_result[
                "retain_until"
            ],

        "retention_expired":
            eligibility_result[
                "retention_expired"
            ],

        "hold_active":
            eligibility_result[
                "hold_active"
            ],

        "hold_type":
            eligibility_result[
                "hold_type"
            ],

        "retention_satisfied":
            eligibility_result[
                "retention_satisfied"
            ],

        "deletion_eligible":
            eligibility_result[
                "deletion_eligible"
            ],

        "reason":
            eligibility_result[
                "eligibility_reason"
            ],

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
        raise BodyStoreRetentionPolicyEngineError(
            "Retention policy input was mutated during evaluation."
        )

    return MappingProxyType(
        result
    )
