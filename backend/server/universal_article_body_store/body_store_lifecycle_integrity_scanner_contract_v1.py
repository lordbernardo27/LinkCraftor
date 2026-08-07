from __future__ import annotations

import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping


BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CONTRACT_VERSION = "1.0"

BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CONTRACT_SCHEMA = (
    "body_store_lifecycle_integrity_scanner_contract.v1"
)

SUPPORTED_SCOPES = (
    "WORKSPACE",
)

SUPPORTED_STATES = (
    "ACTIVE",
    "ARCHIVED",
    "RESTORED",
    "PERMANENTLY_DELETED",
)

SUPPORTED_CHECKS = (
    "STATE_CONSISTENCY",
    "ARCHIVE_INTEGRITY",
    "TOMBSTONE_INTEGRITY",
    "REFERENCE_INTEGRITY",
    "RETENTION_INTEGRITY",
    "CHECKSUM_INTEGRITY",
)


class LifecycleIntegrityScannerContractError(
    ValueError,
):
    """Raised when an integrity scanner request is invalid."""


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
                    _freeze(item)

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
            for item in value
        )

    if isinstance(
        value,
        tuple,
    ):
        return tuple(
            _freeze(item)
            for item in value
        )

    return value


def _require_mapping(
    value: Any,
    *,
    field_name: str,
) -> Mapping[str, Any]:

    if not isinstance(
        value,
        Mapping,
    ):
        raise LifecycleIntegrityScannerContractError(
            field_name
            + " must be a mapping."
        )

    return value


def _json_ready(
    value: Any,
) -> Any:

    if isinstance(
        value,
        Mapping,
    ):
        return {
            str(key):
                _json_ready(item)

            for key, item
            in value.items()
        }

    if isinstance(
        value,
        (
            tuple,
            list,
        ),
    ):
        return [
            _json_ready(item)
            for item in value
        ]

    return value


def calculate_lifecycle_integrity_scanner_request_checksum_v1(
    *,
    payload: Mapping[str, Any],
) -> str:

    _require_mapping(
        payload,
        field_name="payload",
    )

    serialized = json.dumps(
        _json_ready(payload),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )

    return hashlib.sha256(
        serialized.encode(
            "utf-8"
        )
    ).hexdigest()
def _require_string(
    value: Any,
    *,
    field_name: str,
) -> str:

    if not isinstance(
        value,
        str,
    ):
        raise LifecycleIntegrityScannerContractError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise LifecycleIntegrityScannerContractError(
            field_name
            + " must not be empty."
        )

    return normalized


def _require_boolean(
    value: Any,
    *,
    field_name: str,
) -> bool:

    if not isinstance(
        value,
        bool,
    ):
        raise LifecycleIntegrityScannerContractError(
            field_name
            + " must be a boolean."
        )

    return value


def create_lifecycle_integrity_scanner_request_v1(
    *,
    scan_request_id: str,
    scope: str,
    workspace_id: str,
    include_state_consistency: bool,
    include_archive_integrity: bool,
    include_tombstone_integrity: bool,
    include_reference_integrity: bool,
    include_retention_integrity: bool,
    include_checksum_integrity: bool,
) -> Mapping[str, Any]:

    normalized_request_id = _require_string(
        scan_request_id,
        field_name="scan_request_id",
    )

    normalized_scope = _require_string(
        scope,
        field_name="scope",
    ).upper()

    if normalized_scope not in SUPPORTED_SCOPES:
        raise LifecycleIntegrityScannerContractError(
            "scope must be WORKSPACE."
        )

    normalized_workspace_id = _require_string(
        workspace_id,
        field_name="workspace_id",
    )

    checks = {
        "include_state_consistency":
            _require_boolean(
                include_state_consistency,
                field_name="include_state_consistency",
            ),

        "include_archive_integrity":
            _require_boolean(
                include_archive_integrity,
                field_name="include_archive_integrity",
            ),

        "include_tombstone_integrity":
            _require_boolean(
                include_tombstone_integrity,
                field_name="include_tombstone_integrity",
            ),

        "include_reference_integrity":
            _require_boolean(
                include_reference_integrity,
                field_name="include_reference_integrity",
            ),

        "include_retention_integrity":
            _require_boolean(
                include_retention_integrity,
                field_name="include_retention_integrity",
            ),

        "include_checksum_integrity":
            _require_boolean(
                include_checksum_integrity,
                field_name="include_checksum_integrity",
            ),
    }

    if not any(
        selected is True
        for selected in checks.values()
    ):
        raise LifecycleIntegrityScannerContractError(
            "At least one integrity check must be selected."
        )

    request = {
        "schema":
            BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CONTRACT_SCHEMA,

        "contract_version":
            BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CONTRACT_VERSION,

        "scan_request_id":
            normalized_request_id,

        "scope":
            normalized_scope,

        "workspace_id":
            normalized_workspace_id,

        "checks":
            checks,

        "supported_states":
            SUPPORTED_STATES,

        "supported_checks":
            SUPPORTED_CHECKS,

        "read_only":
            True,

        "repair_planned":
            False,

        "repair_executed":
            False,

        "lifecycle_modified":
            False,

        "archive_modified":
            False,

        "tombstone_modified":
            False,

        "body_store_modified":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    request["checksum"] = (
        calculate_lifecycle_integrity_scanner_request_checksum_v1(
            payload=request,
        )
    )

    return _freeze(
        request
    )
def validate_lifecycle_integrity_scanner_request_v1(
    *,
    scan_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        scan_request,
        field_name="scan_request",
    )

    required_fields = (
        "schema",
        "contract_version",
        "scan_request_id",
        "scope",
        "workspace_id",
        "checks",
        "supported_states",
        "supported_checks",
        "read_only",
        "repair_planned",
        "repair_executed",
        "lifecycle_modified",
        "archive_modified",
        "tombstone_modified",
        "body_store_modified",
        "runtime_job_created",
        "queue_job_created",
        "checksum",
    )

    missing_fields = tuple(
        field_name
        for field_name in required_fields
        if field_name not in request
    )

    schema_valid = (
        request.get(
            "schema"
        )
        == BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CONTRACT_SCHEMA
    )

    contract_version_valid = (
        request.get(
            "contract_version"
        )
        == BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CONTRACT_VERSION
    )

    scope_valid = (
        request.get(
            "scope"
        )
        in SUPPORTED_SCOPES
    )

    workspace_id = request.get(
        "workspace_id"
    )

    workspace_valid = (
        isinstance(
            workspace_id,
            str,
        )
        and bool(
            workspace_id.strip()
        )
    )

    checks = request.get(
        "checks"
    )

    checks_mapping_valid = isinstance(
        checks,
        Mapping,
    )

    required_checks = (
        "include_state_consistency",
        "include_archive_integrity",
        "include_tombstone_integrity",
        "include_reference_integrity",
        "include_retention_integrity",
        "include_checksum_integrity",
    )

    missing_checks = tuple(
        check_name
        for check_name in required_checks
        if (
            not checks_mapping_valid
            or check_name not in checks
        )
    )

    check_flags_valid = (
        checks_mapping_valid
        and not missing_checks
        and all(
            isinstance(
                checks[
                    check_name
                ],
                bool,
            )
            for check_name in required_checks
        )
    )

    at_least_one_check_selected = (
        check_flags_valid
        and any(
            checks[
                check_name
            ]
            is True
            for check_name in required_checks
        )
    )

    supported_states_valid = (
        tuple(
            request.get(
                "supported_states",
                (),
            )
        )
        == SUPPORTED_STATES
    )

    supported_checks_valid = (
        tuple(
            request.get(
                "supported_checks",
                (),
            )
        )
        == SUPPORTED_CHECKS
    )

    safety_boundaries_valid = all(
        (
            request.get(
                "read_only"
            )
            is True,

            request.get(
                "repair_planned"
            )
            is False,

            request.get(
                "repair_executed"
            )
            is False,

            request.get(
                "lifecycle_modified"
            )
            is False,

            request.get(
                "archive_modified"
            )
            is False,

            request.get(
                "tombstone_modified"
            )
            is False,

            request.get(
                "body_store_modified"
            )
            is False,

            request.get(
                "runtime_job_created"
            )
            is False,

            request.get(
                "queue_job_created"
            )
            is False,
        )
    )

    checksum_source = {
        key:
            value

        for key, value
        in request.items()

        if key != "checksum"
    }

    calculated_checksum = (
        calculate_lifecycle_integrity_scanner_request_checksum_v1(
            payload=checksum_source,
        )
    )

    checksum_valid = (
        calculated_checksum
        == request.get(
            "checksum"
        )
    )

    request_valid = all(
        (
            not missing_fields,
            schema_valid,
            contract_version_valid,
            scope_valid,
            workspace_valid,
            checks_mapping_valid,
            not missing_checks,
            check_flags_valid,
            at_least_one_check_selected,
            supported_states_valid,
            supported_checks_valid,
            safety_boundaries_valid,
            checksum_valid,
        )
    )

    validation = {
        "request_valid":
            request_valid,

        "missing_fields":
            missing_fields,

        "schema_valid":
            schema_valid,

        "contract_version_valid":
            contract_version_valid,

        "scope_valid":
            scope_valid,

        "workspace_valid":
            workspace_valid,

        "checks_mapping_valid":
            checks_mapping_valid,

        "missing_checks":
            missing_checks,

        "check_flags_valid":
            check_flags_valid,

        "at_least_one_check_selected":
            at_least_one_check_selected,

        "supported_states_valid":
            supported_states_valid,

        "supported_checks_valid":
            supported_checks_valid,

        "safety_boundaries_valid":
            safety_boundaries_valid,

        "checksum_valid":
            checksum_valid,

        "calculated_checksum":
            calculated_checksum,

        "stored_checksum":
            request.get(
                "checksum"
            ),

        "read_only":
            True,

        "repair_planned":
            False,

        "repair_executed":
            False,

        "lifecycle_modified":
            False,

        "archive_modified":
            False,

        "tombstone_modified":
            False,

        "body_store_modified":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    return _freeze(
        validation
    )
def certify_lifecycle_integrity_scanner_request_v1(
    *,
    scan_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        scan_request,
        field_name="scan_request",
    )

    validation = (
        validate_lifecycle_integrity_scanner_request_v1(
            scan_request=request,
        )
    )

    certification = {
        "schema":
            "body_store_lifecycle_integrity_scanner_contract_certification.v1",

        "contract_version":
            BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CONTRACT_VERSION,

        "scan_request_id":
            request[
                "scan_request_id"
            ],

        "scope":
            request[
                "scope"
            ],

        "workspace_id":
            request[
                "workspace_id"
            ],

        "certified":
            validation[
                "request_valid"
            ]
            is True,

        "request_valid":
            validation[
                "request_valid"
            ],

        "validation":
            validation,

        "request_checksum":
            request[
                "checksum"
            ],

        "read_only":
            True,

        "scan_executed":
            False,

        "findings_generated":
            False,

        "repair_planned":
            False,

        "repair_executed":
            False,

        "lifecycle_modified":
            False,

        "archive_modified":
            False,

        "tombstone_modified":
            False,

        "body_store_modified":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    return _freeze(
        certification
    )


def summarize_lifecycle_integrity_scanner_request_v1(
    *,
    scan_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        scan_request,
        field_name="scan_request",
    )

    checks = _require_mapping(
        request[
            "checks"
        ],
        field_name="checks",
    )

    selected_checks = tuple(
        check_name
        for check_name, selected
        in checks.items()
        if selected is True
    )

    summary = {
        "scan_request_id":
            request[
                "scan_request_id"
            ],

        "scope":
            request[
                "scope"
            ],

        "workspace_id":
            request[
                "workspace_id"
            ],

        "selected_checks":
            selected_checks,

        "selected_check_count":
            len(
                selected_checks
            ),

        "supported_states":
            request[
                "supported_states"
            ],

        "supported_checks":
            request[
                "supported_checks"
            ],

        "read_only":
            True,

        "scan_executed":
            False,

        "findings_generated":
            False,

        "repair_planned":
            False,

        "repair_executed":
            False,

        "lifecycle_modified":
            False,

        "archive_modified":
            False,

        "tombstone_modified":
            False,

        "body_store_modified":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    return _freeze(
        summary
    )


__all__ = [
    "BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CONTRACT_VERSION",
    "BODY_STORE_LIFECYCLE_INTEGRITY_SCANNER_CONTRACT_SCHEMA",
    "SUPPORTED_SCOPES",
    "SUPPORTED_STATES",
    "SUPPORTED_CHECKS",
    "LifecycleIntegrityScannerContractError",
    "calculate_lifecycle_integrity_scanner_request_checksum_v1",
    "create_lifecycle_integrity_scanner_request_v1",
    "validate_lifecycle_integrity_scanner_request_v1",
    "certify_lifecycle_integrity_scanner_request_v1",
    "summarize_lifecycle_integrity_scanner_request_v1",
]
