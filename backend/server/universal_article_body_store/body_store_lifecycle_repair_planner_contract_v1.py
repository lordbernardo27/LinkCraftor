from __future__ import annotations

import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping


BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_SCHEMA = (
    "body_store_lifecycle_repair_planner_contract.v1"
)

BODY_STORE_LIFECYCLE_REPAIR_PLANNER_REQUEST_SCHEMA = (
    "body_store_lifecycle_repair_planner_request.v1"
)

BODY_STORE_LIFECYCLE_REPAIR_PLAN_SCHEMA = (
    "body_store_lifecycle_repair_plan.v1"
)

BODY_STORE_LIFECYCLE_REPAIR_ACTION_SCHEMA = (
    "body_store_lifecycle_repair_action.v1"
)

BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_VERSION = "1.0"


SUPPORTED_REPAIR_SCOPES = (
    "WORKSPACE",
    "FINDING_SET",
)


SUPPORTED_FINDING_TYPES = (
    "DUPLICATE_LIFECYCLE_IDENTITY",
    "INVALID_JSON_RECORD",
    "RETENTION_STATE_INCONSISTENCY",
    "TOMBSTONE_CONTENT_BOUNDARY_VIOLATION",
    "UNSUPPORTED_LIFECYCLE_STATE",
)


SUPPORTED_FINDING_SEVERITIES = (
    "WARNING",
    "ERROR",
    "CRITICAL",
)


SUPPORTED_REPAIR_ACTION_TYPES = (
    "REBUILD_LIFECYCLE_RECORD",
    "REBUILD_ARCHIVE_METADATA",
    "REBUILD_TOMBSTONE_INDEX",
    "REPAIR_REFERENCE_METADATA",
    "NORMALIZE_LIFECYCLE_STATE",
    "RESOLVE_DUPLICATE_IDENTITY",
    "QUARANTINE_INVALID_RECORD",
    "REMOVE_TOMBSTONE_CONTENT_REFERENCE",
    "REVIEW_RETENTION_STATE",
    "MANUAL_REVIEW_REQUIRED",
)


AUTOMATICALLY_PLANNABLE_FINDING_TYPES = (
    "DUPLICATE_LIFECYCLE_IDENTITY",
    "INVALID_JSON_RECORD",
    "RETENTION_STATE_INCONSISTENCY",
    "TOMBSTONE_CONTENT_BOUNDARY_VIOLATION",
    "UNSUPPORTED_LIFECYCLE_STATE",
)


PROHIBITED_REPAIR_ACTION_TYPES = (
    "DELETE_ARTICLE_BODY",
    "PERMANENT_DELETE_BODY",
    "EXECUTE_ARCHIVE",
    "EXECUTE_RESTORE",
    "EXECUTE_REPAIR",
    "MODIFY_PRODUCTION_BODY",
    "MODIFY_PRODUCTION_LIFECYCLE",
    "MODIFY_PRODUCTION_ARCHIVE",
    "MODIFY_PRODUCTION_TOMBSTONE",
)


class LifecycleRepairPlannerContractError(
    ValueError
):
    """Raised when a Lifecycle Repair Planner contract is invalid."""


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


def _json_ready(
    value: Any,
) -> Any:

    if isinstance(
        value,
        Mapping,
    ):
        return {
            str(
                key
            ):
                _json_ready(
                    item
                )

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
            _json_ready(
                item
            )

            for item
            in value
        ]

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
        raise LifecycleRepairPlannerContractError(
            field_name
            + " must be a mapping."
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
        raise LifecycleRepairPlannerContractError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise LifecycleRepairPlannerContractError(
            field_name
            + " must not be empty."
        )

    return normalized


def calculate_lifecycle_repair_planner_checksum_v1(
    *,
    payload: Mapping[str, Any],
) -> str:

    _require_mapping(
        payload,
        field_name="payload",
    )

    serialized = json.dumps(
        _json_ready(
            payload
        ),
        ensure_ascii=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    )

    return hashlib.sha256(
        serialized.encode(
            "utf-8"
        )
    ).hexdigest()
def _require_boolean(
    value: Any,
    *,
    field_name: str,
) -> bool:

    if not isinstance(
        value,
        bool,
    ):
        raise LifecycleRepairPlannerContractError(
            field_name
            + " must be a boolean."
        )

    return value


def _normalize_finding_ids(
    value: Any,
) -> tuple[str, ...]:

    if value is None:
        return ()

    if not isinstance(
        value,
        (
            tuple,
            list,
        ),
    ):
        raise LifecycleRepairPlannerContractError(
            "finding_ids must be a tuple or list."
        )

    normalized: list[str] = []

    for item in value:
        normalized.append(
            _require_string(
                item,
                field_name="finding_id",
            )
        )

    if len(
        normalized
    ) != len(
        set(
            normalized
        )
    ):
        raise LifecycleRepairPlannerContractError(
            "finding_ids must not contain duplicates."
        )

    return tuple(
        normalized
    )


def create_lifecycle_repair_planner_request_v1(
    *,
    repair_plan_request_id: str,
    workspace_id: str,
    repair_scope: str,
    finding_ids: tuple[str, ...] | list[str] | None,
    allow_automatic_planning: bool = True,
    require_manual_review_for_critical: bool = True,
) -> Mapping[str, Any]:

    normalized_request_id = _require_string(
        repair_plan_request_id,
        field_name="repair_plan_request_id",
    )

    normalized_workspace_id = _require_string(
        workspace_id,
        field_name="workspace_id",
    )

    normalized_scope = _require_string(
        repair_scope,
        field_name="repair_scope",
    ).upper()

    if (
        normalized_scope
        not in SUPPORTED_REPAIR_SCOPES
    ):
        raise LifecycleRepairPlannerContractError(
            "Unsupported repair_scope: "
            + normalized_scope
        )

    normalized_finding_ids = (
        _normalize_finding_ids(
            finding_ids
        )
    )

    if (
        normalized_scope
        == "FINDING_SET"
        and not normalized_finding_ids
    ):
        raise LifecycleRepairPlannerContractError(
            "FINDING_SET scope requires at least one finding_id."
        )

    if (
        normalized_scope
        == "WORKSPACE"
        and normalized_finding_ids
    ):
        raise LifecycleRepairPlannerContractError(
            "WORKSPACE scope must not include explicit finding_ids."
        )

    request = {
        "schema":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_REQUEST_SCHEMA,

        "contract_schema":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_SCHEMA,

        "contract_version":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_VERSION,

        "repair_plan_request_id":
            normalized_request_id,

        "workspace_id":
            normalized_workspace_id,

        "repair_scope":
            normalized_scope,

        "finding_ids":
            normalized_finding_ids,

        "allow_automatic_planning":
            _require_boolean(
                allow_automatic_planning,
                field_name="allow_automatic_planning",
            ),

        "require_manual_review_for_critical":
            _require_boolean(
                require_manual_review_for_critical,
                field_name="require_manual_review_for_critical",
            ),

        "supported_finding_types":
            SUPPORTED_FINDING_TYPES,

        "supported_finding_severities":
            SUPPORTED_FINDING_SEVERITIES,

        "supported_repair_action_types":
            SUPPORTED_REPAIR_ACTION_TYPES,

        "prohibited_repair_action_types":
            PROHIBITED_REPAIR_ACTION_TYPES,

        "planner_mode":
            "PLAN_ONLY",

        "read_only":
            True,

        "repair_planned":
            False,

        "repair_executed":
            False,

        "production_mutation_allowed":
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

    request[
        "request_checksum"
    ] = (
        calculate_lifecycle_repair_planner_checksum_v1(
            payload=request,
        )
    )

    return _freeze(
        request
    )
def validate_lifecycle_repair_planner_request_v1(
    *,
    planner_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        planner_request,
        field_name="planner_request",
    )

    required_fields = (
        "schema",
        "contract_schema",
        "contract_version",
        "repair_plan_request_id",
        "workspace_id",
        "repair_scope",
        "finding_ids",
        "allow_automatic_planning",
        "require_manual_review_for_critical",
        "supported_finding_types",
        "supported_finding_severities",
        "supported_repair_action_types",
        "prohibited_repair_action_types",
        "planner_mode",
        "read_only",
        "repair_planned",
        "repair_executed",
        "production_mutation_allowed",
        "lifecycle_modified",
        "archive_modified",
        "tombstone_modified",
        "body_store_modified",
        "runtime_job_created",
        "queue_job_created",
        "request_checksum",
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
        == BODY_STORE_LIFECYCLE_REPAIR_PLANNER_REQUEST_SCHEMA
    )

    contract_schema_valid = (
        request.get(
            "contract_schema"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_SCHEMA
    )

    contract_version_valid = (
        request.get(
            "contract_version"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_VERSION
    )

    repair_plan_request_id = request.get(
        "repair_plan_request_id"
    )

    request_id_valid = (
        isinstance(
            repair_plan_request_id,
            str,
        )
        and bool(
            repair_plan_request_id.strip()
        )
    )

    workspace_id = request.get(
        "workspace_id"
    )

    workspace_id_valid = (
        isinstance(
            workspace_id,
            str,
        )
        and bool(
            workspace_id.strip()
        )
    )

    repair_scope = request.get(
        "repair_scope"
    )

    repair_scope_valid = (
        repair_scope
        in SUPPORTED_REPAIR_SCOPES
    )

    finding_ids = request.get(
        "finding_ids"
    )

    finding_ids_collection_valid = (
        isinstance(
            finding_ids,
            (
                tuple,
                list,
            ),
        )
    )

    finding_ids_values_valid = (
        finding_ids_collection_valid
        and all(
            isinstance(
                finding_id,
                str,
            )
            and bool(
                finding_id.strip()
            )

            for finding_id in finding_ids
        )
    )

    finding_ids_unique = (
        finding_ids_collection_valid
        and len(
            finding_ids
        )
        == len(
            set(
                finding_ids
            )
        )
    )

    repair_scope_finding_ids_valid = (
        (
            repair_scope == "WORKSPACE"
            and finding_ids_collection_valid
            and len(
                finding_ids
            )
            == 0
        )
        or (
            repair_scope == "FINDING_SET"
            and finding_ids_collection_valid
            and len(
                finding_ids
            )
            > 0
        )
    )

    planning_flags_valid = all(
        (
            isinstance(
                request.get(
                    "allow_automatic_planning"
                ),
                bool,
            ),

            isinstance(
                request.get(
                    "require_manual_review_for_critical"
                ),
                bool,
            ),
        )
    )

    supported_finding_types_valid = (
        tuple(
            request.get(
                "supported_finding_types",
                (),
            )
        )
        == SUPPORTED_FINDING_TYPES
    )

    supported_finding_severities_valid = (
        tuple(
            request.get(
                "supported_finding_severities",
                (),
            )
        )
        == SUPPORTED_FINDING_SEVERITIES
    )

    supported_repair_action_types_valid = (
        tuple(
            request.get(
                "supported_repair_action_types",
                (),
            )
        )
        == SUPPORTED_REPAIR_ACTION_TYPES
    )

    prohibited_repair_action_types_valid = (
        tuple(
            request.get(
                "prohibited_repair_action_types",
                (),
            )
        )
        == PROHIBITED_REPAIR_ACTION_TYPES
    )

    action_boundaries_disjoint = (
        not set(
            SUPPORTED_REPAIR_ACTION_TYPES
        ).intersection(
            PROHIBITED_REPAIR_ACTION_TYPES
        )
    )

    planner_mode_valid = (
        request.get(
            "planner_mode"
        )
        == "PLAN_ONLY"
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
                "production_mutation_allowed"
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

        if key != "request_checksum"
    }

    calculated_checksum = (
        calculate_lifecycle_repair_planner_checksum_v1(
            payload=checksum_source,
        )
    )

    checksum_valid = (
        calculated_checksum
        == request.get(
            "request_checksum"
        )
    )

    request_valid = all(
        (
            not missing_fields,
            schema_valid,
            contract_schema_valid,
            contract_version_valid,
            request_id_valid,
            workspace_id_valid,
            repair_scope_valid,
            finding_ids_collection_valid,
            finding_ids_values_valid,
            finding_ids_unique,
            repair_scope_finding_ids_valid,
            planning_flags_valid,
            supported_finding_types_valid,
            supported_finding_severities_valid,
            supported_repair_action_types_valid,
            prohibited_repair_action_types_valid,
            action_boundaries_disjoint,
            planner_mode_valid,
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

        "contract_schema_valid":
            contract_schema_valid,

        "contract_version_valid":
            contract_version_valid,

        "request_id_valid":
            request_id_valid,

        "workspace_id_valid":
            workspace_id_valid,

        "repair_scope_valid":
            repair_scope_valid,

        "finding_ids_collection_valid":
            finding_ids_collection_valid,

        "finding_ids_values_valid":
            finding_ids_values_valid,

        "finding_ids_unique":
            finding_ids_unique,

        "repair_scope_finding_ids_valid":
            repair_scope_finding_ids_valid,

        "planning_flags_valid":
            planning_flags_valid,

        "supported_finding_types_valid":
            supported_finding_types_valid,

        "supported_finding_severities_valid":
            supported_finding_severities_valid,

        "supported_repair_action_types_valid":
            supported_repair_action_types_valid,

        "prohibited_repair_action_types_valid":
            prohibited_repair_action_types_valid,

        "action_boundaries_disjoint":
            action_boundaries_disjoint,

        "planner_mode_valid":
            planner_mode_valid,

        "safety_boundaries_valid":
            safety_boundaries_valid,

        "checksum_valid":
            checksum_valid,

        "calculated_checksum":
            calculated_checksum,

        "stored_checksum":
            request.get(
                "request_checksum"
            ),

        "read_only":
            True,

        "repair_executed":
            False,

        "production_mutation_allowed":
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
def certify_lifecycle_repair_planner_request_v1(
    *,
    planner_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        planner_request,
        field_name="planner_request",
    )

    validation = (
        validate_lifecycle_repair_planner_request_v1(
            planner_request=request,
        )
    )

    certification = {
        "schema":
            "body_store_lifecycle_repair_planner_contract_certification.v1",

        "contract_version":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_VERSION,

        "repair_plan_request_id":
            request[
                "repair_plan_request_id"
            ],

        "workspace_id":
            request[
                "workspace_id"
            ],

        "repair_scope":
            request[
                "repair_scope"
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
                "request_checksum"
            ],

        "planner_mode":
            "PLAN_ONLY",

        "read_only":
            True,

        "repair_plan_generated":
            False,

        "repair_actions_generated":
            0,

        "repair_executed":
            False,

        "production_mutation_allowed":
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


def summarize_lifecycle_repair_planner_request_v1(
    *,
    planner_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        planner_request,
        field_name="planner_request",
    )

    finding_ids = request[
        "finding_ids"
    ]

    summary = {
        "repair_plan_request_id":
            request[
                "repair_plan_request_id"
            ],

        "workspace_id":
            request[
                "workspace_id"
            ],

        "repair_scope":
            request[
                "repair_scope"
            ],

        "finding_ids":
            finding_ids,

        "finding_id_count":
            len(
                finding_ids
            ),

        "allow_automatic_planning":
            request[
                "allow_automatic_planning"
            ],

        "require_manual_review_for_critical":
            request[
                "require_manual_review_for_critical"
            ],

        "supported_finding_type_count":
            len(
                request[
                    "supported_finding_types"
                ]
            ),

        "supported_repair_action_type_count":
            len(
                request[
                    "supported_repair_action_types"
                ]
            ),

        "prohibited_repair_action_type_count":
            len(
                request[
                    "prohibited_repair_action_types"
                ]
            ),

        "planner_mode":
            request[
                "planner_mode"
            ],

        "read_only":
            True,

        "repair_plan_generated":
            False,

        "repair_executed":
            False,

        "production_mutation_allowed":
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
    "BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_SCHEMA",
    "BODY_STORE_LIFECYCLE_REPAIR_PLANNER_REQUEST_SCHEMA",
    "BODY_STORE_LIFECYCLE_REPAIR_PLAN_SCHEMA",
    "BODY_STORE_LIFECYCLE_REPAIR_ACTION_SCHEMA",
    "BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_VERSION",
    "SUPPORTED_REPAIR_SCOPES",
    "SUPPORTED_FINDING_TYPES",
    "SUPPORTED_FINDING_SEVERITIES",
    "SUPPORTED_REPAIR_ACTION_TYPES",
    "AUTOMATICALLY_PLANNABLE_FINDING_TYPES",
    "PROHIBITED_REPAIR_ACTION_TYPES",
    "LifecycleRepairPlannerContractError",
    "calculate_lifecycle_repair_planner_checksum_v1",
    "create_lifecycle_repair_planner_request_v1",
    "validate_lifecycle_repair_planner_request_v1",
    "certify_lifecycle_repair_planner_request_v1",
    "summarize_lifecycle_repair_planner_request_v1",
]
