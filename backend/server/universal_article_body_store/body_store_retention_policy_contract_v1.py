"""Universal Article Body Store Retention Policy Contract.

Phase 9.1.3.1 responsibility:

- define canonical Body Store retention classes;
- define canonical retention statuses;
- define canonical hold types;
- validate retention-policy records;
- build deterministic retention-policy records;
- prevent article body content from entering retention metadata.

This contract does not:

- calculate current expiration;
- transition lifecycle state;
- archive, restore, clean up, or delete bodies;
- call the Body Store Writer, Manager, Repository, Runtime, Worker, or Queue;
- register runtime handlers;
- modify persisted lifecycle records.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Mapping


BODY_STORE_RETENTION_POLICY_CONTRACT_ID = (
    "urn:linkcraftor:universal-article-body-store:"
    "retention-policy-contract"
)

BODY_STORE_RETENTION_POLICY_CONTRACT_VERSION = (
    "universal_article_body_store_retention_policy_contract_v1"
)

BODY_STORE_RETENTION_POLICY_SCHEMA_VERSION = (
    "body_store_retention_policy_record_v1"
)


BODY_STORE_RETENTION_CLASSES = (
    "STANDARD",
    "EXTENDED",
    "INDEFINITE",
    "LEGAL_HOLD",
    "OPERATIONAL_HOLD",
    "CUSTOM",
)

BODY_STORE_RETENTION_STATUSES = (
    "ACTIVE",
    "RETAINED",
    "ON_HOLD",
    "EXPIRED",
    "ELIGIBLE_FOR_DELETION",
)

BODY_STORE_RETENTION_HOLD_TYPES = (
    "LEGAL",
    "OPERATIONAL",
    "MANUAL",
    "SYSTEM",
)

BODY_STORE_RETENTION_NON_HOLD_CLASSES = (
    "STANDARD",
    "EXTENDED",
    "INDEFINITE",
    "CUSTOM",
)

BODY_STORE_RETENTION_HOLD_CLASSES = (
    "LEGAL_HOLD",
    "OPERATIONAL_HOLD",
)

BODY_STORE_RETENTION_DEFAULT_PERIODS = {
    "STANDARD": 365,
    "EXTENDED": 730,
}

_FORBIDDEN_BODY_FIELDS = {
    "content_body",
    "article_body",
    "body_payload",
    "raw_body",
    "full_text",
}


class BodyStoreRetentionPolicyError(
    ValueError
):
    """Base error for invalid Body Store retention policies."""


def _require_string(
    value: Any,
    *,
    field_name: str,
) -> str:
    if not isinstance(
        value,
        str,
    ):
        raise BodyStoreRetentionPolicyError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise BodyStoreRetentionPolicyError(
            field_name
            + " must not be empty."
        )

    return normalized


def _require_optional_string(
    value: Any,
    *,
    field_name: str,
) -> str | None:
    if value is None:
        return None

    return _require_string(
        value,
        field_name=field_name,
    )


def _require_mapping(
    value: Any,
    *,
    field_name: str,
) -> Mapping[str, Any]:
    if not isinstance(
        value,
        Mapping,
    ):
        raise BodyStoreRetentionPolicyError(
            field_name
            + " must be a mapping."
        )

    return value


def _contains_forbidden_body_content(
    value: Any,
) -> bool:
    if isinstance(
        value,
        Mapping,
    ):
        for key, item in value.items():
            if str(
                key
            ).casefold() in _FORBIDDEN_BODY_FIELDS:
                return True

            if _contains_forbidden_body_content(
                item
            ):
                return True

        return False

    if isinstance(
        value,
        (
            list,
            tuple,
            set,
        ),
    ):
        return any(
            _contains_forbidden_body_content(
                item
            )
            for item in value
        )

    return False


def _parse_timestamp(
    value: Any,
    *,
    field_name: str,
    required: bool = True,
) -> tuple[str | None, datetime | None]:
    if value is None:
        if required:
            raise BodyStoreRetentionPolicyError(
                field_name
                + " is required."
            )

        return None, None

    normalized = _require_string(
        value,
        field_name=field_name,
    )

    try:
        parsed = datetime.fromisoformat(
            normalized
        )

    except ValueError as exc:
        raise BodyStoreRetentionPolicyError(
            field_name
            + " must be a valid ISO-8601 timestamp."
        ) from exc

    if parsed.tzinfo is None:
        raise BodyStoreRetentionPolicyError(
            field_name
            + " must include timezone information."
        )

    return normalized, parsed


def _normalize_retention_class(
    value: Any,
) -> str:
    normalized = _require_string(
        value,
        field_name="retention_class",
    ).upper()

    if normalized not in BODY_STORE_RETENTION_CLASSES:
        raise BodyStoreRetentionPolicyError(
            "Unsupported retention class: "
            + normalized
        )

    return normalized


def _normalize_retention_status(
    value: Any,
) -> str:
    normalized = _require_string(
        value,
        field_name="retention_status",
    ).upper()

    if normalized not in BODY_STORE_RETENTION_STATUSES:
        raise BodyStoreRetentionPolicyError(
            "Unsupported retention status: "
            + normalized
        )

    return normalized


def _normalize_hold_type(
    value: Any,
) -> str | None:
    if value is None:
        return None

    normalized = _require_string(
        value,
        field_name="hold_type",
    ).upper()

    if normalized not in BODY_STORE_RETENTION_HOLD_TYPES:
        raise BodyStoreRetentionPolicyError(
            "Unsupported hold type: "
            + normalized
        )

    return normalized


def _normalize_period_days(
    value: Any,
    *,
    retention_class: str,
) -> int | None:
    if value is None:
        if retention_class in (
            "INDEFINITE",
            "LEGAL_HOLD",
            "OPERATIONAL_HOLD",
        ):
            return None

        if retention_class in BODY_STORE_RETENTION_DEFAULT_PERIODS:
            return BODY_STORE_RETENTION_DEFAULT_PERIODS[
                retention_class
            ]

        raise BodyStoreRetentionPolicyError(
            "retention_period_days is required for "
            + retention_class
            + "."
        )

    if (
        not isinstance(
            value,
            int,
        )
        or isinstance(
            value,
            bool,
        )
        or value < 0
    ):
        raise BodyStoreRetentionPolicyError(
            "retention_period_days must be a non-negative integer."
        )

    if retention_class in (
        "INDEFINITE",
        "LEGAL_HOLD",
        "OPERATIONAL_HOLD",
    ):
        raise BodyStoreRetentionPolicyError(
            retention_class
            + " must not define retention_period_days."
        )

    return value


def calculate_retain_until_v1(
    *,
    retention_started_at: str,
    retention_class: str,
    retention_period_days: int | None,
) -> str | None:
    """Calculate the canonical retain-until timestamp."""

    normalized_class = _normalize_retention_class(
        retention_class
    )

    _, started_at = _parse_timestamp(
        retention_started_at,
        field_name="retention_started_at",
    )

    normalized_days = _normalize_period_days(
        retention_period_days,
        retention_class=normalized_class,
    )

    if normalized_days is None:
        return None

    assert started_at is not None

    return (
        started_at
        + timedelta(
            days=normalized_days
        )
    ).isoformat()


def validate_body_store_retention_policy_v1(
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate and normalize one Body Store retention-policy record."""

    mapping = dict(
        _require_mapping(
            policy,
            field_name="policy",
        )
    )

    if _contains_forbidden_body_content(
        mapping
    ):
        raise BodyStoreRetentionPolicyError(
            "Retention policies must not contain article body content."
        )

    contract_id = _require_string(
        mapping.get(
            "contract_id"
        ),
        field_name="contract_id",
    )

    if contract_id != BODY_STORE_RETENTION_POLICY_CONTRACT_ID:
        raise BodyStoreRetentionPolicyError(
            "Unsupported retention contract ID."
        )

    contract_version = _require_string(
        mapping.get(
            "contract_version"
        ),
        field_name="contract_version",
    )

    if (
        contract_version
        != BODY_STORE_RETENTION_POLICY_CONTRACT_VERSION
    ):
        raise BodyStoreRetentionPolicyError(
            "Unsupported retention contract version."
        )

    schema_version = _require_string(
        mapping.get(
            "schema_version"
        ),
        field_name="schema_version",
    )

    if (
        schema_version
        != BODY_STORE_RETENTION_POLICY_SCHEMA_VERSION
    ):
        raise BodyStoreRetentionPolicyError(
            "Unsupported retention-policy schema version."
        )

    policy_id = _require_string(
        mapping.get(
            "retention_policy_id"
        ),
        field_name="retention_policy_id",
    )

    policy_name = _require_string(
        mapping.get(
            "retention_policy_name"
        ),
        field_name="retention_policy_name",
    )

    lifecycle_record_id = _require_string(
        mapping.get(
            "lifecycle_record_id"
        ),
        field_name="lifecycle_record_id",
    )

    workspace_id = _require_string(
        mapping.get(
            "workspace_id"
        ),
        field_name="workspace_id",
    )

    retention_class = _normalize_retention_class(
        mapping.get(
            "retention_class"
        )
    )

    retention_status = _normalize_retention_status(
        mapping.get(
            "retention_status"
        )
    )

    retention_started_at, started_at = _parse_timestamp(
        mapping.get(
            "retention_started_at"
        ),
        field_name="retention_started_at",
    )

    retention_period_days = _normalize_period_days(
        mapping.get(
            "retention_period_days"
        ),
        retention_class=retention_class,
    )

    calculated_retain_until = calculate_retain_until_v1(
        retention_started_at=retention_started_at,
        retention_class=retention_class,
        retention_period_days=retention_period_days,
    )

    retain_until, retain_until_dt = _parse_timestamp(
        mapping.get(
            "retain_until"
        ),
        field_name="retain_until",
        required=False,
    )

    if retain_until != calculated_retain_until:
        raise BodyStoreRetentionPolicyError(
            "retain_until does not match the canonical retention calculation."
        )

    is_on_hold = mapping.get(
        "is_on_hold"
    )

    if not isinstance(
        is_on_hold,
        bool,
    ):
        raise BodyStoreRetentionPolicyError(
            "is_on_hold must be a boolean."
        )

    hold_type = _normalize_hold_type(
        mapping.get(
            "hold_type"
        )
    )

    hold_reason = _require_optional_string(
        mapping.get(
            "hold_reason"
        ),
        field_name="hold_reason",
    )

    hold_started_at, hold_started_dt = _parse_timestamp(
        mapping.get(
            "hold_started_at"
        ),
        field_name="hold_started_at",
        required=False,
    )

    hold_expires_at, hold_expires_dt = _parse_timestamp(
        mapping.get(
            "hold_expires_at"
        ),
        field_name="hold_expires_at",
        required=False,
    )

    if retention_class == "LEGAL_HOLD":
        if (
            not is_on_hold
            or hold_type != "LEGAL"
        ):
            raise BodyStoreRetentionPolicyError(
                "LEGAL_HOLD requires an active LEGAL hold."
            )

    if retention_class == "OPERATIONAL_HOLD":
        if (
            not is_on_hold
            or hold_type != "OPERATIONAL"
        ):
            raise BodyStoreRetentionPolicyError(
                "OPERATIONAL_HOLD requires an active OPERATIONAL hold."
            )

    if is_on_hold:
        if hold_type is None:
            raise BodyStoreRetentionPolicyError(
                "Active holds require hold_type."
            )

        if hold_reason is None:
            raise BodyStoreRetentionPolicyError(
                "Active holds require hold_reason."
            )

        if hold_started_at is None:
            raise BodyStoreRetentionPolicyError(
                "Active holds require hold_started_at."
            )

        if retention_status != "ON_HOLD":
            raise BodyStoreRetentionPolicyError(
                "Active holds require retention_status ON_HOLD."
            )

    else:
        if any(
            item is not None
            for item in (
                hold_type,
                hold_reason,
                hold_started_at,
                hold_expires_at,
            )
        ):
            raise BodyStoreRetentionPolicyError(
                "Inactive holds must not contain hold metadata."
            )

        if retention_status == "ON_HOLD":
            raise BodyStoreRetentionPolicyError(
                "ON_HOLD status requires is_on_hold=True."
            )

    if (
        hold_started_dt is not None
        and hold_expires_dt is not None
        and hold_expires_dt < hold_started_dt
    ):
        raise BodyStoreRetentionPolicyError(
            "hold_expires_at must not precede hold_started_at."
        )

    retention_satisfied = mapping.get(
        "retention_satisfied"
    )

    deletion_eligible = mapping.get(
        "deletion_eligible"
    )

    if not isinstance(
        retention_satisfied,
        bool,
    ):
        raise BodyStoreRetentionPolicyError(
            "retention_satisfied must be a boolean."
        )

    if not isinstance(
        deletion_eligible,
        bool,
    ):
        raise BodyStoreRetentionPolicyError(
            "deletion_eligible must be a boolean."
        )

    eligibility_reason = _require_string(
        mapping.get(
            "eligibility_reason"
        ),
        field_name="eligibility_reason",
    )

    evaluated_at, _ = _parse_timestamp(
        mapping.get(
            "evaluated_at"
        ),
        field_name="evaluated_at",
    )

    if is_on_hold:
        if retention_satisfied:
            raise BodyStoreRetentionPolicyError(
                "Retention cannot be satisfied while a hold is active."
            )

        if deletion_eligible:
            raise BodyStoreRetentionPolicyError(
                "Deletion cannot be eligible while a hold is active."
            )

    if retention_class == "INDEFINITE":
        if retention_satisfied:
            raise BodyStoreRetentionPolicyError(
                "INDEFINITE retention cannot be satisfied."
            )

        if deletion_eligible:
            raise BodyStoreRetentionPolicyError(
                "INDEFINITE retention cannot be deletion eligible."
            )

    if deletion_eligible and not retention_satisfied:
        raise BodyStoreRetentionPolicyError(
            "Deletion eligibility requires retention_satisfied=True."
        )

    if deletion_eligible and retention_status != "ELIGIBLE_FOR_DELETION":
        raise BodyStoreRetentionPolicyError(
            "Deletion eligibility requires status ELIGIBLE_FOR_DELETION."
        )

    if retention_status == "ELIGIBLE_FOR_DELETION" and not deletion_eligible:
        raise BodyStoreRetentionPolicyError(
            "ELIGIBLE_FOR_DELETION status requires deletion_eligible=True."
        )

    if retention_status == "EXPIRED" and not retention_satisfied:
        raise BodyStoreRetentionPolicyError(
            "EXPIRED status requires retention_satisfied=True."
        )

    if (
        retain_until_dt is not None
        and started_at is not None
        and retain_until_dt < started_at
    ):
        raise BodyStoreRetentionPolicyError(
            "retain_until must not precede retention_started_at."
        )

    metadata = dict(
        _require_mapping(
            mapping.get(
                "metadata",
                {},
            ),
            field_name="metadata",
        )
    )

    if _contains_forbidden_body_content(
        metadata
    ):
        raise BodyStoreRetentionPolicyError(
            "Retention metadata must not contain article body content."
        )

    return {
        "contract_id":
            contract_id,

        "contract_version":
            contract_version,

        "schema_version":
            schema_version,

        "retention_policy_id":
            policy_id,

        "retention_policy_name":
            policy_name,

        "lifecycle_record_id":
            lifecycle_record_id,

        "workspace_id":
            workspace_id,

        "retention_class":
            retention_class,

        "retention_status":
            retention_status,

        "retention_started_at":
            retention_started_at,

        "retention_period_days":
            retention_period_days,

        "retain_until":
            retain_until,

        "is_on_hold":
            is_on_hold,

        "hold_type":
            hold_type,

        "hold_reason":
            hold_reason,

        "hold_started_at":
            hold_started_at,

        "hold_expires_at":
            hold_expires_at,

        "retention_satisfied":
            retention_satisfied,

        "deletion_eligible":
            deletion_eligible,

        "eligibility_reason":
            eligibility_reason,

        "evaluated_at":
            evaluated_at,

        "metadata":
            metadata,

        "content_body_included":
            False,
    }


def build_body_store_retention_policy_v1(
    *,
    retention_policy_id: str,
    retention_policy_name: str,
    lifecycle_record_id: str,
    workspace_id: str,
    retention_class: str,
    retention_started_at: str,
    retention_period_days: int | None = None,
    retention_status: str = "ACTIVE",
    is_on_hold: bool = False,
    hold_type: str | None = None,
    hold_reason: str | None = None,
    hold_started_at: str | None = None,
    hold_expires_at: str | None = None,
    retention_satisfied: bool = False,
    deletion_eligible: bool = False,
    eligibility_reason: str = "Retention has not yet been evaluated.",
    evaluated_at: str | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one validated canonical retention-policy record."""

    normalized_class = _normalize_retention_class(
        retention_class
    )

    normalized_days = _normalize_period_days(
        retention_period_days,
        retention_class=normalized_class,
    )

    retain_until = calculate_retain_until_v1(
        retention_started_at=retention_started_at,
        retention_class=normalized_class,
        retention_period_days=normalized_days,
    )

    normalized_evaluated_at = (
        evaluated_at
        if evaluated_at is not None
        else datetime.now(
            timezone.utc
        ).isoformat()
    )

    return validate_body_store_retention_policy_v1(
        {
            "contract_id":
                BODY_STORE_RETENTION_POLICY_CONTRACT_ID,

            "contract_version":
                BODY_STORE_RETENTION_POLICY_CONTRACT_VERSION,

            "schema_version":
                BODY_STORE_RETENTION_POLICY_SCHEMA_VERSION,

            "retention_policy_id":
                retention_policy_id,

            "retention_policy_name":
                retention_policy_name,

            "lifecycle_record_id":
                lifecycle_record_id,

            "workspace_id":
                workspace_id,

            "retention_class":
                normalized_class,

            "retention_status":
                retention_status,

            "retention_started_at":
                retention_started_at,

            "retention_period_days":
                normalized_days,

            "retain_until":
                retain_until,

            "is_on_hold":
                is_on_hold,

            "hold_type":
                hold_type,

            "hold_reason":
                hold_reason,

            "hold_started_at":
                hold_started_at,

            "hold_expires_at":
                hold_expires_at,

            "retention_satisfied":
                retention_satisfied,

            "deletion_eligible":
                deletion_eligible,

            "eligibility_reason":
                eligibility_reason,

            "evaluated_at":
                normalized_evaluated_at,

            "metadata":
                {}
                if metadata is None
                else dict(
                    metadata
                ),
        }
    )
