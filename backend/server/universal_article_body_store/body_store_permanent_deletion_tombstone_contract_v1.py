from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping


BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CONTRACT_VERSION = "1.0"

BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CONTRACT_SCHEMA = (
    "body_store_permanent_deletion_tombstone_contract.v1"
)

BODY_STORE_PERMANENT_DELETION_TOMBSTONE_STATUS = (
    "PERMANENTLY_DELETED"
)


class PermanentDeletionTombstoneContractError(
    ValueError
):
    """Raised when a permanent deletion tombstone contract is invalid."""


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
        raise PermanentDeletionTombstoneContractError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise PermanentDeletionTombstoneContractError(
            field_name
            + " must not be empty."
        )

    return normalized


def _require_true(
    value: Any,
    *,
    field_name: str,
) -> bool:

    if value is not True:
        raise PermanentDeletionTombstoneContractError(
            field_name
            + " must be True."
        )

    return True


def _require_false(
    value: Any,
    *,
    field_name: str,
) -> bool:

    if value is not False:
        raise PermanentDeletionTombstoneContractError(
            field_name
            + " must be False."
        )

    return False


def _utc_now() -> str:

    return (
        datetime.now(
            timezone.utc
        ).isoformat()
    )


def calculate_permanent_deletion_tombstone_checksum_v1(
    *,
    payload: Mapping[str, Any],
) -> str:

    if not isinstance(
        payload,
        Mapping,
    ):
        raise PermanentDeletionTombstoneContractError(
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
def create_permanent_deletion_tombstone_contract_v1(
    *,
    tombstone_id: str,
    body_id: str,
    workspace_id: str,
    archive_id: str,
    lifecycle_record_id: str,
    deletion_request_id: str,
    deletion_execution_id: str,
    deletion_reason: str,
    retention_verified: bool,
    archive_verified: bool,
    recovery_closed: bool,
    legal_hold_verified: bool,
    verification_id: str,
    certification_id: str,
    deletion_manager_version: str,
) -> Mapping[str, Any]:

    contract = {
        "schema": (
            BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CONTRACT_SCHEMA
        ),
        "contract_version": (
            BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CONTRACT_VERSION
        ),
        "status": (
            BODY_STORE_PERMANENT_DELETION_TOMBSTONE_STATUS
        ),
        "tombstone_id": _require_string(
            tombstone_id,
            field_name="tombstone_id",
        ),
        "body_id": _require_string(
            body_id,
            field_name="body_id",
        ),
        "workspace_id": _require_string(
            workspace_id,
            field_name="workspace_id",
        ),
        "archive_id": _require_string(
            archive_id,
            field_name="archive_id",
        ),
        "lifecycle_record_id": _require_string(
            lifecycle_record_id,
            field_name="lifecycle_record_id",
        ),
        "deletion_request_id": _require_string(
            deletion_request_id,
            field_name="deletion_request_id",
        ),
        "deletion_execution_id": _require_string(
            deletion_execution_id,
            field_name="deletion_execution_id",
        ),
        "deletion_reason": _require_string(
            deletion_reason,
            field_name="deletion_reason",
        ),
        "retention_verified": _require_true(
            retention_verified,
            field_name="retention_verified",
        ),
        "archive_verified": _require_true(
            archive_verified,
            field_name="archive_verified",
        ),
        "recovery_closed": _require_true(
            recovery_closed,
            field_name="recovery_closed",
        ),
        "legal_hold_verified": _require_true(
            legal_hold_verified,
            field_name="legal_hold_verified",
        ),
        "verification_id": _require_string(
            verification_id,
            field_name="verification_id",
        ),
        "certification_id": _require_string(
            certification_id,
            field_name="certification_id",
        ),
        "deletion_manager_version": _require_string(
            deletion_manager_version,
            field_name="deletion_manager_version",
        ),
        "immutable": _require_true(
            True,
            field_name="immutable",
        ),
        "read_only": _require_true(
            True,
            field_name="read_only",
        ),
        "contains_article_body": _require_false(
            False,
            field_name="contains_article_body",
        ),
        "created_at": _utc_now(),
    }

    checksum = (
        calculate_permanent_deletion_tombstone_checksum_v1(
            payload=contract,
        )
    )

    contract["checksum"] = checksum

    return _freeze(contract)
def validate_permanent_deletion_tombstone_contract_v1(
    *,
    tombstone_contract: Mapping[str, Any],
) -> Mapping[str, Any]:

    if not isinstance(
        tombstone_contract,
        Mapping,
    ):
        raise PermanentDeletionTombstoneContractError(
            "tombstone_contract must be a mapping."
        )

    required_fields = (
        "schema",
        "contract_version",
        "status",
        "tombstone_id",
        "body_id",
        "workspace_id",
        "archive_id",
        "lifecycle_record_id",
        "deletion_request_id",
        "deletion_execution_id",
        "deletion_reason",
        "retention_verified",
        "archive_verified",
        "recovery_closed",
        "legal_hold_verified",
        "verification_id",
        "certification_id",
        "deletion_manager_version",
        "immutable",
        "read_only",
        "contains_article_body",
        "created_at",
        "checksum",
    )

    missing_fields = tuple(
        field_name
        for field_name in required_fields
        if field_name not in tombstone_contract
    )

    schema_valid = (
        tombstone_contract.get(
            "schema"
        )
        == BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CONTRACT_SCHEMA
    )

    contract_version_valid = (
        tombstone_contract.get(
            "contract_version"
        )
        == BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CONTRACT_VERSION
    )

    status_valid = (
        tombstone_contract.get(
            "status"
        )
        == BODY_STORE_PERMANENT_DELETION_TOMBSTONE_STATUS
    )

    evidence_valid = all(
        (
            tombstone_contract.get(
                "retention_verified"
            )
            is True,
            tombstone_contract.get(
                "archive_verified"
            )
            is True,
            tombstone_contract.get(
                "recovery_closed"
            )
            is True,
            tombstone_contract.get(
                "legal_hold_verified"
            )
            is True,
        )
    )

    safety_boundaries_valid = all(
        (
            tombstone_contract.get(
                "immutable"
            )
            is True,
            tombstone_contract.get(
                "read_only"
            )
            is True,
            tombstone_contract.get(
                "contains_article_body"
            )
            is False,
        )
    )

    checksum_source = {
        key:
            value

        for key, value
        in tombstone_contract.items()

        if key != "checksum"
    }

    calculated_checksum = (
        calculate_permanent_deletion_tombstone_checksum_v1(
            payload=checksum_source,
        )
    )

    checksum_valid = (
        calculated_checksum
        == tombstone_contract.get(
            "checksum"
        )
    )

    validation = {
        "contract_valid":
            all(
                (
                    not missing_fields,
                    schema_valid,
                    contract_version_valid,
                    status_valid,
                    evidence_valid,
                    safety_boundaries_valid,
                    checksum_valid,
                )
            ),

        "missing_fields":
            missing_fields,

        "schema_valid":
            schema_valid,

        "contract_version_valid":
            contract_version_valid,

        "status_valid":
            status_valid,

        "evidence_valid":
            evidence_valid,

        "safety_boundaries_valid":
            safety_boundaries_valid,

        "checksum_valid":
            checksum_valid,

        "calculated_checksum":
            calculated_checksum,

        "stored_checksum":
            tombstone_contract.get(
                "checksum"
            ),

        "article_body_exposed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,

        "lifecycle_modified":
            False,

        "archive_modified":
            False,

        "body_store_modified":
            False,
    }

    return _freeze(
        validation
    )


def certify_permanent_deletion_tombstone_contract_v1(
    *,
    tombstone_contract: Mapping[str, Any],
) -> Mapping[str, Any]:

    validation = (
        validate_permanent_deletion_tombstone_contract_v1(
            tombstone_contract=tombstone_contract,
        )
    )

    certification = {
        "schema":
            "body_store_permanent_deletion_tombstone_contract_certification.v1",

        "contract_version":
            BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CONTRACT_VERSION,

        "tombstone_id":
            tombstone_contract[
                "tombstone_id"
            ],

        "body_id":
            tombstone_contract[
                "body_id"
            ],

        "workspace_id":
            tombstone_contract[
                "workspace_id"
            ],

        "certified":
            validation[
                "contract_valid"
            ]
            is True,

        "validation":
            validation,

        "checksum":
            tombstone_contract[
                "checksum"
            ],

        "immutable":
            True,

        "read_only":
            True,

        "article_body_exposed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,

        "lifecycle_modified":
            False,

        "archive_modified":
            False,

        "body_store_modified":
            False,
    }

    return _freeze(
        certification
    )


__all__ = [
    "BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CONTRACT_VERSION",
    "BODY_STORE_PERMANENT_DELETION_TOMBSTONE_CONTRACT_SCHEMA",
    "BODY_STORE_PERMANENT_DELETION_TOMBSTONE_STATUS",
    "PermanentDeletionTombstoneContractError",
    "calculate_permanent_deletion_tombstone_checksum_v1",
    "create_permanent_deletion_tombstone_contract_v1",
    "validate_permanent_deletion_tombstone_contract_v1",
    "certify_permanent_deletion_tombstone_contract_v1",
]
