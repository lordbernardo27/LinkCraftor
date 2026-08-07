from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping


BODY_STORE_PERMANENT_DELETION_CONTRACT_VERSION = "1.0"

BODY_STORE_PERMANENT_DELETION_CONTRACT_SCHEMA = (
    "body_store_permanent_deletion_contract.v1"
)

BODY_STORE_PERMANENT_DELETION_SOURCE_STATE = (
    "ARCHIVED"
)

BODY_STORE_PERMANENT_DELETION_TARGET_STATE = (
    "PERMANENTLY_DELETED"
)

BODY_STORE_PERMANENT_DELETION_STATUSES = (
    "READY",
    "BLOCKED",
    "DELETED",
    "FAILED",
)


class PermanentDeletionContractError(
    ValueError
):
    """Raised when a permanent deletion contract is invalid."""


def _freeze(
    value: Any,
) -> Any:

    if isinstance(
        value,
        MappingProxyType,
    ):
        return value

    if isinstance(
        value,
        dict,
    ):
        return MappingProxyType(
            {
                key:
                    _freeze(
                        item
                    )

                for key, item
                in value.items()
            }
        )

    if isinstance(
        value,
        list,
    ):
        return tuple(
            _freeze(
                item
            )

            for item
            in value
        )

    if isinstance(
        value,
        tuple,
    ):
        return tuple(
            _freeze(
                item
            )

            for item
            in value
        )

    return value


def _require_string(
    value: Any,
    *,
    field_name: str,
) -> str:

    if not isinstance(
        value,
        str,
    ):
        raise PermanentDeletionContractError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise PermanentDeletionContractError(
            field_name
            + " must not be empty."
        )

    return normalized


def _utc_now() -> str:

    return (
        datetime.now(
            timezone.utc
        ).isoformat()
    )


def calculate_permanent_deletion_contract_checksum_v1(
    *,
    payload: Mapping[str, Any],
) -> str:

    if not isinstance(
        payload,
        Mapping,
    ):
        raise PermanentDeletionContractError(
            "payload must be a mapping."
        )

    serialized = json.dumps(
        dict(
            payload
        ),
        ensure_ascii=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        default=str,
    )

    return hashlib.sha256(
        serialized.encode(
            "utf-8"
        )
    ).hexdigest()
def build_permanent_deletion_request_v1(
    *,
    archive_id: str,
    workspace_id: str,
    body_id: str,
    lifecycle_record_id: str,
    source_state: str,
    deletion_reason: str,
    requested_by_type: str,
    requested_by_id: str,
    retention_expired: bool,
    deletion_eligible: bool,
    legal_hold_active: bool,
    archive_verified: bool,
    recovery_closed: bool,
    requested_at: str | None = None,
) -> Mapping[str, Any]:

    normalized_archive_id = _require_string(
        archive_id,
        field_name="archive_id",
    )

    normalized_workspace_id = _require_string(
        workspace_id,
        field_name="workspace_id",
    )

    normalized_body_id = _require_string(
        body_id,
        field_name="body_id",
    )

    normalized_lifecycle_record_id = _require_string(
        lifecycle_record_id,
        field_name="lifecycle_record_id",
    )

    normalized_source_state = _require_string(
        source_state,
        field_name="source_state",
    ).upper()

    if (
        normalized_source_state
        != BODY_STORE_PERMANENT_DELETION_SOURCE_STATE
    ):
        raise PermanentDeletionContractError(
            "Permanent deletion source state must be ARCHIVED."
        )

    normalized_deletion_reason = _require_string(
        deletion_reason,
        field_name="deletion_reason",
    )

    normalized_requested_by_type = _require_string(
        requested_by_type,
        field_name="requested_by_type",
    )

    normalized_requested_by_id = _require_string(
        requested_by_id,
        field_name="requested_by_id",
    )

    normalized_requested_at = (
        _require_string(
            requested_at,
            field_name="requested_at",
        )
        if requested_at is not None
        else _utc_now()
    )

    blocked_reasons = []

    if retention_expired is not True:
        blocked_reasons.append(
            "RETENTION_NOT_EXPIRED"
        )

    if deletion_eligible is not True:
        blocked_reasons.append(
            "DELETION_NOT_ELIGIBLE"
        )

    if legal_hold_active is True:
        blocked_reasons.append(
            "LEGAL_HOLD_ACTIVE"
        )

    if archive_verified is not True:
        blocked_reasons.append(
            "ARCHIVE_NOT_VERIFIED"
        )

    if recovery_closed is not True:
        blocked_reasons.append(
            "RECOVERY_NOT_CLOSED"
        )

    deletion_ready = (
        len(
            blocked_reasons
        )
        == 0
    )

    identity_material = {
        "archive_id":
            normalized_archive_id,

        "workspace_id":
            normalized_workspace_id,

        "body_id":
            normalized_body_id,

        "lifecycle_record_id":
            normalized_lifecycle_record_id,

        "requested_at":
            normalized_requested_at,
    }

    deletion_request_id = (
        "body_store_permanent_deletion_request_"
        + calculate_permanent_deletion_contract_checksum_v1(
            payload=identity_material,
        )
    )

    request = {
        "schema_version":
            BODY_STORE_PERMANENT_DELETION_CONTRACT_SCHEMA,

        "contract_version":
            BODY_STORE_PERMANENT_DELETION_CONTRACT_VERSION,

        "deletion_request_id":
            deletion_request_id,

        "archive_id":
            normalized_archive_id,

        "workspace_id":
            normalized_workspace_id,

        "body_id":
            normalized_body_id,

        "lifecycle_record_id":
            normalized_lifecycle_record_id,

        "source_state":
            normalized_source_state,

        "target_state":
            BODY_STORE_PERMANENT_DELETION_TARGET_STATE,

        "deletion_status":
            (
                "READY"
                if deletion_ready
                else "BLOCKED"
            ),

        "deletion_ready":
            deletion_ready,

        "blocked_reasons":
            tuple(
                blocked_reasons
            ),

        "deletion_reason":
            normalized_deletion_reason,

        "requested_by_type":
            normalized_requested_by_type,

        "requested_by_id":
            normalized_requested_by_id,

        "requested_at":
            normalized_requested_at,

        "retention_expired":
            retention_expired is True,

        "deletion_eligible":
            deletion_eligible is True,

        "legal_hold_active":
            legal_hold_active is True,

        "archive_verified":
            archive_verified is True,

        "recovery_closed":
            recovery_closed is True,

        "archive_delete_required":
            True,

        "body_store_delete_required":
            True,

        "lifecycle_transition_required":
            True,

        "deletion_executed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,

        "content_body_included":
            False,
    }

    return _freeze(
        request
    )
def validate_permanent_deletion_request_v1(
    *,
    deletion_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    if not isinstance(
        deletion_request,
        Mapping,
    ):
        raise PermanentDeletionContractError(
            "deletion_request must be a mapping."
        )

    required_fields = (
        "deletion_request_id",
        "archive_id",
        "workspace_id",
        "body_id",
        "lifecycle_record_id",
        "source_state",
        "target_state",
        "deletion_status",
        "deletion_ready",
        "blocked_reasons",
        "retention_expired",
        "deletion_eligible",
        "legal_hold_active",
        "archive_verified",
        "recovery_closed",
    )

    missing_fields = tuple(
        field
        for field in required_fields
        if field not in deletion_request
    )

    source_state_valid = (
        deletion_request.get(
            "source_state"
        )
        == BODY_STORE_PERMANENT_DELETION_SOURCE_STATE
    )

    target_state_valid = (
        deletion_request.get(
            "target_state"
        )
        == BODY_STORE_PERMANENT_DELETION_TARGET_STATE
    )

    status_valid = (
        deletion_request.get(
            "deletion_status"
        )
        in BODY_STORE_PERMANENT_DELETION_STATUSES
    )

    eligibility_boundaries_valid = (
        deletion_request.get(
            "retention_expired"
        )
        is True
        and deletion_request.get(
            "deletion_eligible"
        )
        is True
        and deletion_request.get(
            "legal_hold_active"
        )
        is False
        and deletion_request.get(
            "archive_verified"
        )
        is True
        and deletion_request.get(
            "recovery_closed"
        )
        is True
    )

    ready_status_consistent = (
        (
            deletion_request.get(
                "deletion_ready"
            )
            is True
            and deletion_request.get(
                "deletion_status"
            )
            == "READY"
            and not deletion_request.get(
                "blocked_reasons"
            )
        )
        or (
            deletion_request.get(
                "deletion_ready"
            )
            is False
            and deletion_request.get(
                "deletion_status"
            )
            == "BLOCKED"
            and bool(
                deletion_request.get(
                    "blocked_reasons"
                )
            )
        )
    )

    request_valid = (
        not missing_fields
        and source_state_valid
        and target_state_valid
        and status_valid
        and ready_status_consistent
    )

    result = {
        "request_valid":
            request_valid,

        "deletion_ready":
            deletion_request.get(
                "deletion_ready"
            )
            is True,

        "missing_fields":
            missing_fields,

        "source_state_valid":
            source_state_valid,

        "target_state_valid":
            target_state_valid,

        "status_valid":
            status_valid,

        "eligibility_boundaries_valid":
            eligibility_boundaries_valid,

        "ready_status_consistent":
            ready_status_consistent,

        "deletion_executed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,

        "content_body_included":
            False,
    }

    return _freeze(
        result
    )


def certify_permanent_deletion_request_v1(
    *,
    deletion_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    validation = (
        validate_permanent_deletion_request_v1(
            deletion_request=deletion_request,
        )
    )

    certification = {
        "schema_version":
            "body_store_permanent_deletion_request_certification.v1",

        "contract_version":
            BODY_STORE_PERMANENT_DELETION_CONTRACT_VERSION,

        "certified":
            (
                validation[
                    "request_valid"
                ]
                is True
                and validation[
                    "deletion_ready"
                ]
                is True
                and validation[
                    "eligibility_boundaries_valid"
                ]
                is True
            ),

        "validation":
            validation,

        "summary": {
            "deletion_request_id":
                deletion_request[
                    "deletion_request_id"
                ],

            "archive_id":
                deletion_request[
                    "archive_id"
                ],

            "workspace_id":
                deletion_request[
                    "workspace_id"
                ],

            "body_id":
                deletion_request[
                    "body_id"
                ],

            "source_state":
                deletion_request[
                    "source_state"
                ],

            "target_state":
                deletion_request[
                    "target_state"
                ],

            "deletion_status":
                deletion_request[
                    "deletion_status"
                ],

            "deletion_ready":
                deletion_request[
                    "deletion_ready"
                ],

            "blocked_reasons":
                deletion_request[
                    "blocked_reasons"
                ],
        },

        "archive_delete_performed":
            False,

        "body_store_delete_performed":
            False,

        "lifecycle_transition_performed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,

        "content_body_included":
            False,

        "read_only":
            True,
    }

    return _freeze(
        certification
    )


__all__ = [
    "BODY_STORE_PERMANENT_DELETION_CONTRACT_VERSION",
    "BODY_STORE_PERMANENT_DELETION_CONTRACT_SCHEMA",
    "BODY_STORE_PERMANENT_DELETION_SOURCE_STATE",
    "BODY_STORE_PERMANENT_DELETION_TARGET_STATE",
    "BODY_STORE_PERMANENT_DELETION_STATUSES",
    "PermanentDeletionContractError",
    "calculate_permanent_deletion_contract_checksum_v1",
    "build_permanent_deletion_request_v1",
    "validate_permanent_deletion_request_v1",
    "certify_permanent_deletion_request_v1",
]
