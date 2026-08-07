from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping


BODY_STORE_ARCHIVE_RECOVERY_CONTRACT_VERSION = "1.0"

BODY_STORE_ARCHIVE_RECOVERY_CONTRACT_SCHEMA = (
    "body_store_archive_recovery_contract.v1"
)

BODY_STORE_ARCHIVE_RECOVERY_TARGET_STATE = (
    "ACTIVE"
)

BODY_STORE_ARCHIVE_RECOVERY_ALLOWED_SOURCE_STATES = (
    "ARCHIVED",
)

BODY_STORE_ARCHIVE_RECOVERY_STATUSES = (
    "READY",
    "RECOVERED",
    "BLOCKED",
    "FAILED",
)


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
                key: _freeze(item)
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


def _required_string(
    value: Any,
    *,
    field_name: str,
) -> str:

    if not isinstance(
        value,
        str,
    ):
        raise TypeError(
            f"{field_name} must be a string."
        )

    value = value.strip()

    if not value:
        raise ValueError(
            f"{field_name} must not be empty."
        )

    return value


def _checksum(
    payload: Mapping[str, Any],
) -> str:

    serialized = json.dumps(
        dict(payload),
        sort_keys=True,
        default=str,
    )

    return hashlib.sha256(
        serialized.encode(
            "utf-8"
        )
    ).hexdigest()


def _utc_now() -> str:

    return (
        datetime.now(
            timezone.utc
        ).isoformat()
    )
def build_archive_recovery_request_v1(
    *,
    archive_id: str,
    workspace_id: str,
    body_id: str,
    lifecycle_record_id: str,
    source_state: str,
    recovery_reason: str,
    requested_by_type: str,
    requested_by_id: str,
    requested_at: str | None = None,
) -> Mapping[str, Any]:

    normalized_archive_id = _required_string(
        archive_id,
        field_name="archive_id",
    )

    normalized_workspace_id = _required_string(
        workspace_id,
        field_name="workspace_id",
    )

    normalized_body_id = _required_string(
        body_id,
        field_name="body_id",
    )

    normalized_lifecycle_record_id = _required_string(
        lifecycle_record_id,
        field_name="lifecycle_record_id",
    )

    normalized_source_state = _required_string(
        source_state,
        field_name="source_state",
    ).upper()

    if (
        normalized_source_state
        not in BODY_STORE_ARCHIVE_RECOVERY_ALLOWED_SOURCE_STATES
    ):
        raise ValueError(
            "Archive recovery source state must be ARCHIVED."
        )

    normalized_recovery_reason = _required_string(
        recovery_reason,
        field_name="recovery_reason",
    )

    normalized_requested_by_type = _required_string(
        requested_by_type,
        field_name="requested_by_type",
    )

    normalized_requested_by_id = _required_string(
        requested_by_id,
        field_name="requested_by_id",
    )

    normalized_requested_at = (
        _required_string(
            requested_at,
            field_name="requested_at",
        )
        if requested_at is not None
        else _utc_now()
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

    recovery_request_id = (
        "body_store_archive_recovery_request_"
        + _checksum(
            identity_material
        )
    )

    request = {
        "schema_version":
            BODY_STORE_ARCHIVE_RECOVERY_CONTRACT_SCHEMA,

        "contract_version":
            BODY_STORE_ARCHIVE_RECOVERY_CONTRACT_VERSION,

        "recovery_request_id":
            recovery_request_id,

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
            BODY_STORE_ARCHIVE_RECOVERY_TARGET_STATE,

        "recovery_status":
            "READY",

        "recovery_reason":
            normalized_recovery_reason,

        "requested_by_type":
            normalized_requested_by_type,

        "requested_by_id":
            normalized_requested_by_id,

        "requested_at":
            normalized_requested_at,

        "archive_read_required":
            True,

        "archive_verification_required":
            True,

        "body_store_write_required":
            True,

        "lifecycle_transition_required":
            True,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,

        "recovery_executed":
            False,

        "content_body_included":
            False,
    }

    return _freeze(
        request
    )


def validate_archive_recovery_request_v1(
    *,
    recovery_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    if not isinstance(
        recovery_request,
        Mapping,
    ):
        raise TypeError(
            "recovery_request must be a mapping."
        )

    required_fields = (
        "recovery_request_id",
        "archive_id",
        "workspace_id",
        "body_id",
        "lifecycle_record_id",
        "source_state",
        "target_state",
        "recovery_status",
        "requested_at",
    )

    missing_fields = tuple(
        field
        for field in required_fields
        if field not in recovery_request
    )

    source_state_valid = (
        recovery_request.get(
            "source_state"
        )
        in BODY_STORE_ARCHIVE_RECOVERY_ALLOWED_SOURCE_STATES
    )

    target_state_valid = (
        recovery_request.get(
            "target_state"
        )
        == BODY_STORE_ARCHIVE_RECOVERY_TARGET_STATE
    )

    status_valid = (
        recovery_request.get(
            "recovery_status"
        )
        in BODY_STORE_ARCHIVE_RECOVERY_STATUSES
    )

    result = {
        "request_valid":
            (
                not missing_fields
                and source_state_valid
                and target_state_valid
                and status_valid
            ),

        "missing_fields":
            missing_fields,

        "source_state_valid":
            source_state_valid,

        "target_state_valid":
            target_state_valid,

        "status_valid":
            status_valid,

        "recovery_executed":
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
def certify_archive_recovery_request_v1(
    *,
    recovery_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    validation = (
        validate_archive_recovery_request_v1(
            recovery_request=recovery_request,
        )
    )

    certification = {
        "schema_version":
            "body_store_archive_recovery_certification.v1",

        "contract_version":
            BODY_STORE_ARCHIVE_RECOVERY_CONTRACT_VERSION,

        "certified":
            validation[
                "request_valid"
            ],

        "validation":
            validation,

        "summary": {
            "archive_id":
                recovery_request[
                    "archive_id"
                ],

            "workspace_id":
                recovery_request[
                    "workspace_id"
                ],

            "body_id":
                recovery_request[
                    "body_id"
                ],

            "source_state":
                recovery_request[
                    "source_state"
                ],

            "target_state":
                recovery_request[
                    "target_state"
                ],

            "recovery_status":
                recovery_request[
                    "recovery_status"
                ],
        },

        "runtime_job_created":
            False,

        "queue_job_created":
            False,

        "recovery_executed":
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
    "BODY_STORE_ARCHIVE_RECOVERY_CONTRACT_VERSION",
    "BODY_STORE_ARCHIVE_RECOVERY_CONTRACT_SCHEMA",
    "BODY_STORE_ARCHIVE_RECOVERY_TARGET_STATE",
    "BODY_STORE_ARCHIVE_RECOVERY_ALLOWED_SOURCE_STATES",
    "BODY_STORE_ARCHIVE_RECOVERY_STATUSES",
    "build_archive_recovery_request_v1",
    "validate_archive_recovery_request_v1",
    "certify_archive_recovery_request_v1",
]
