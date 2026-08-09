from __future__ import annotations

import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping


BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_SCHEMA = (
    "body_store_lifecycle_repair_executor_contract.v1"
)

BODY_STORE_LIFECYCLE_REPAIR_EXECUTION_REQUEST_SCHEMA = (
    "body_store_lifecycle_repair_execution_request.v1"
)

BODY_STORE_LIFECYCLE_REPAIR_EXECUTION_AUTHORIZATION_SCHEMA = (
    "body_store_lifecycle_repair_execution_authorization.v1"
)

BODY_STORE_LIFECYCLE_REPAIR_EXECUTION_RESULT_SCHEMA = (
    "body_store_lifecycle_repair_execution_result.v1"
)

BODY_STORE_LIFECYCLE_REPAIR_ACTION_RESULT_SCHEMA = (
    "body_store_lifecycle_repair_action_result.v1"
)

BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_VERSION = "1.0"


SUPPORTED_EXECUTION_MODES = (
    "DRY_RUN",
    "AUTHORIZED_APPLY",
)


SUPPORTED_EXECUTOR_ACTION_TYPES = (
    "REBUILD_LIFECYCLE_RECORD",
    "REBUILD_ARCHIVE_METADATA",
    "REBUILD_TOMBSTONE_INDEX",
    "REPAIR_REFERENCE_METADATA",
    "NORMALIZE_LIFECYCLE_STATE",
    "RESOLVE_DUPLICATE_IDENTITY",
    "QUARANTINE_INVALID_RECORD",
    "REMOVE_TOMBSTONE_CONTENT_REFERENCE",
)


NON_EXECUTABLE_PLANNER_ACTION_TYPES = (
    "REVIEW_RETENTION_STATE",
    "MANUAL_REVIEW_REQUIRED",
)


SUPPORTED_AUTHORIZATION_STATES = (
    "AUTHORIZED",
    "REJECTED",
)


SUPPORTED_ACTION_EXECUTION_STATUSES = (
    "NOT_EXECUTED",
    "DRY_RUN_VALIDATED",
    "EXECUTED",
    "SKIPPED",
    "REJECTED",
    "FAILED",
)


PROHIBITED_DIRECT_EXECUTION_ACTION_TYPES = (
    "DELETE_ARTICLE_BODY",
    "PERMANENT_DELETE_BODY",
    "EXECUTE_ARCHIVE",
    "EXECUTE_RESTORE",
    "BYPASS_RETENTION_POLICY",
    "BYPASS_LEGAL_HOLD",
    "BYPASS_TOMBSTONE_POLICY",
    "BYPASS_PLAN_CERTIFICATION",
    "BYPASS_EXECUTION_AUTHORIZATION",
)


REQUIRED_EXECUTION_SAFETY_GATES = (
    "CERTIFIED_REPAIR_PLAN",
    "VALID_PLANNER_CERTIFICATION",
    "PLAN_IDENTITY_MATCH",
    "PLAN_CHECKSUM_MATCH",
    "CERTIFICATION_CHECKSUM_MATCH",
    "EXPLICIT_AUTHORIZATION",
    "AUTHORIZED_ACTION_IDS",
    "WORKSPACE_ID_MATCH",
    "NO_PROHIBITED_ACTION",
)


class LifecycleRepairExecutorContractError(
    ValueError
):
    """Raised when a Lifecycle Repair Executor contract is invalid."""


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
        Mapping,
    ):
        return MappingProxyType(
            {
                str(
                    key
                ):
                    _freeze(
                        item
                    )

                for key, item
                in value.items()
            }
        )

    if isinstance(
        value,
        (
            tuple,
            list,
        ),
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
        raise LifecycleRepairExecutorContractError(
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
        raise LifecycleRepairExecutorContractError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise LifecycleRepairExecutorContractError(
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
        raise LifecycleRepairExecutorContractError(
            field_name
            + " must be a boolean."
        )

    return value


def calculate_lifecycle_repair_executor_checksum_v1(
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
def _normalize_action_ids(
    value: Any,
    *,
    field_name: str,
    allow_empty: bool = False,
) -> tuple[str, ...]:

    if not isinstance(
        value,
        (
            tuple,
            list,
        ),
    ):
        raise LifecycleRepairExecutorContractError(
            field_name
            + " must be a tuple or list."
        )

    normalized: list[str] = []

    for item in value:
        normalized.append(
            _require_string(
                item,
                field_name=(
                    field_name
                    + " item"
                ),
            )
        )

    if (
        not allow_empty
        and not normalized
    ):
        raise LifecycleRepairExecutorContractError(
            field_name
            + " must contain at least one action ID."
        )

    if len(
        normalized
    ) != len(
        set(
            normalized
        )
    ):
        raise LifecycleRepairExecutorContractError(
            field_name
            + " must not contain duplicate action IDs."
        )

    return tuple(
        normalized
    )


def create_lifecycle_repair_execution_authorization_v1(
    *,
    authorization_id: str,
    workspace_id: str,
    repair_plan_id: str,
    repair_plan_checksum: str,
    planner_certification_id: str,
    planner_certification_checksum: str,
    authorization_state: str,
    authorized_action_ids: tuple[str, ...]
    | list[str],
    authorized_by: str,
    authorization_reason: str,
) -> Mapping[str, Any]:

    normalized_authorization_id = (
        _require_string(
            authorization_id,
            field_name="authorization_id",
        )
    )

    normalized_workspace_id = (
        _require_string(
            workspace_id,
            field_name="workspace_id",
        )
    )

    normalized_repair_plan_id = (
        _require_string(
            repair_plan_id,
            field_name="repair_plan_id",
        )
    )

    normalized_repair_plan_checksum = (
        _require_string(
            repair_plan_checksum,
            field_name="repair_plan_checksum",
        )
    )

    normalized_certification_id = (
        _require_string(
            planner_certification_id,
            field_name="planner_certification_id",
        )
    )

    normalized_certification_checksum = (
        _require_string(
            planner_certification_checksum,
            field_name=(
                "planner_certification_checksum"
            ),
        )
    )

    normalized_authorization_state = (
        _require_string(
            authorization_state,
            field_name="authorization_state",
        ).upper()
    )

    if (
        normalized_authorization_state
        not in SUPPORTED_AUTHORIZATION_STATES
    ):
        raise LifecycleRepairExecutorContractError(
            "Unsupported authorization_state: "
            + normalized_authorization_state
        )

    normalized_authorized_by = (
        _require_string(
            authorized_by,
            field_name="authorized_by",
        )
    )

    normalized_authorization_reason = (
        _require_string(
            authorization_reason,
            field_name="authorization_reason",
        )
    )

    normalized_action_ids = (
        _normalize_action_ids(
            authorized_action_ids,
            field_name="authorized_action_ids",
            allow_empty=(
                normalized_authorization_state
                == "REJECTED"
            ),
        )
    )

    if (
        normalized_authorization_state
        == "REJECTED"
        and normalized_action_ids
    ):
        raise LifecycleRepairExecutorContractError(
            "REJECTED authorization must not "
            "contain authorized_action_ids."
        )

    explicitly_authorized = (
        normalized_authorization_state
        == "AUTHORIZED"
        and bool(
            normalized_action_ids
        )
    )

    authorization = {
        "schema":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTION_AUTHORIZATION_SCHEMA,

        "contract_schema":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_SCHEMA,

        "contract_version":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_VERSION,

        "authorization_id":
            normalized_authorization_id,

        "workspace_id":
            normalized_workspace_id,

        "repair_plan_id":
            normalized_repair_plan_id,

        "repair_plan_checksum":
            normalized_repair_plan_checksum,

        "planner_certification_id":
            normalized_certification_id,

        "planner_certification_checksum":
            normalized_certification_checksum,

        "authorization_state":
            normalized_authorization_state,

        "authorized_action_ids":
            normalized_action_ids,

        "authorized_action_count":
            len(
                normalized_action_ids
            ),

        "authorized_by":
            normalized_authorized_by,

        "authorization_reason":
            normalized_authorization_reason,

        "explicitly_authorized":
            explicitly_authorized,

        "authorization_grants_execution_eligibility":
            explicitly_authorized,

        "authorization_grants_direct_store_access":
            False,

        "authorization_bypasses_safety_gates":
            False,

        "authorization_bypasses_plan_validation":
            False,

        "authorization_bypasses_certification_validation":
            False,

        "contract_phase_only":
            True,

        "repair_executed":
            False,

        "production_mutation_performed":
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

    authorization[
        "authorization_checksum"
    ] = (
        calculate_lifecycle_repair_executor_checksum_v1(
            payload=authorization,
        )
    )

    return _freeze(
        authorization
    )
def create_lifecycle_repair_execution_request_v1(
    *,
    execution_request_id: str,
    workspace_id: str,
    repair_plan_id: str,
    repair_plan_checksum: str,
    planner_certification_id: str,
    planner_certification_checksum: str,
    authorization_id: str,
    authorization_checksum: str,
    execution_mode: str,
    requested_action_ids: tuple[str, ...]
    | list[str],
    require_all_actions_authorized: bool = True,
) -> Mapping[str, Any]:

    normalized_execution_request_id = (
        _require_string(
            execution_request_id,
            field_name="execution_request_id",
        )
    )

    normalized_workspace_id = (
        _require_string(
            workspace_id,
            field_name="workspace_id",
        )
    )

    normalized_repair_plan_id = (
        _require_string(
            repair_plan_id,
            field_name="repair_plan_id",
        )
    )

    normalized_repair_plan_checksum = (
        _require_string(
            repair_plan_checksum,
            field_name="repair_plan_checksum",
        )
    )

    normalized_certification_id = (
        _require_string(
            planner_certification_id,
            field_name="planner_certification_id",
        )
    )

    normalized_certification_checksum = (
        _require_string(
            planner_certification_checksum,
            field_name=(
                "planner_certification_checksum"
            ),
        )
    )

    normalized_authorization_id = (
        _require_string(
            authorization_id,
            field_name="authorization_id",
        )
    )

    normalized_authorization_checksum = (
        _require_string(
            authorization_checksum,
            field_name="authorization_checksum",
        )
    )

    normalized_execution_mode = (
        _require_string(
            execution_mode,
            field_name="execution_mode",
        ).upper()
    )

    if (
        normalized_execution_mode
        not in SUPPORTED_EXECUTION_MODES
    ):
        raise LifecycleRepairExecutorContractError(
            "Unsupported execution_mode: "
            + normalized_execution_mode
        )

    normalized_action_ids = (
        _normalize_action_ids(
            requested_action_ids,
            field_name="requested_action_ids",
            allow_empty=False,
        )
    )

    normalized_require_all_actions_authorized = (
        _require_boolean(
            require_all_actions_authorized,
            field_name=(
                "require_all_actions_authorized"
            ),
        )
    )

    request = {
        "schema":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTION_REQUEST_SCHEMA,

        "contract_schema":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_SCHEMA,

        "contract_version":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_VERSION,

        "execution_request_id":
            normalized_execution_request_id,

        "workspace_id":
            normalized_workspace_id,

        "repair_plan_id":
            normalized_repair_plan_id,

        "repair_plan_checksum":
            normalized_repair_plan_checksum,

        "planner_certification_id":
            normalized_certification_id,

        "planner_certification_checksum":
            normalized_certification_checksum,

        "authorization_id":
            normalized_authorization_id,

        "authorization_checksum":
            normalized_authorization_checksum,

        "execution_mode":
            normalized_execution_mode,

        "requested_action_ids":
            normalized_action_ids,

        "requested_action_count":
            len(
                normalized_action_ids
            ),

        "require_all_actions_authorized":
            normalized_require_all_actions_authorized,

        "required_safety_gates":
            REQUIRED_EXECUTION_SAFETY_GATES,

        "execution_eligible":
            False,

        "execution_authorized":
            False,

        "execution_started":
            False,

        "execution_completed":
            False,

        "repair_executed":
            False,

        "production_mutation_performed":
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

        "contract_phase_only":
            True,
    }

    request[
        "execution_request_checksum"
    ] = (
        calculate_lifecycle_repair_executor_checksum_v1(
            payload=request,
        )
    )

    return _freeze(
        request
    )


def validate_lifecycle_repair_execution_authorization_v1(
    *,
    authorization: Mapping[str, Any],
) -> Mapping[str, Any]:

    item = _require_mapping(
        authorization,
        field_name="authorization",
    )

    required_fields = (
        "schema",
        "contract_schema",
        "contract_version",
        "authorization_id",
        "workspace_id",
        "repair_plan_id",
        "repair_plan_checksum",
        "planner_certification_id",
        "planner_certification_checksum",
        "authorization_state",
        "authorized_action_ids",
        "authorized_action_count",
        "authorized_by",
        "authorization_reason",
        "explicitly_authorized",
        "authorization_grants_execution_eligibility",
        "authorization_grants_direct_store_access",
        "authorization_bypasses_safety_gates",
        "authorization_bypasses_plan_validation",
        "authorization_bypasses_certification_validation",
        "contract_phase_only",
        "repair_executed",
        "production_mutation_performed",
        "lifecycle_modified",
        "archive_modified",
        "tombstone_modified",
        "body_store_modified",
        "runtime_job_created",
        "queue_job_created",
        "authorization_checksum",
    )

    missing_fields = tuple(
        field_name
        for field_name in required_fields
        if field_name not in item
    )

    schema_valid = (
        item.get(
            "schema"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_EXECUTION_AUTHORIZATION_SCHEMA
    )

    contract_schema_valid = (
        item.get(
            "contract_schema"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_SCHEMA
    )

    contract_version_valid = (
        item.get(
            "contract_version"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_VERSION
    )

    authorization_state = item.get(
        "authorization_state"
    )

    authorization_state_valid = (
        authorization_state
        in SUPPORTED_AUTHORIZATION_STATES
    )

    action_ids = item.get(
        "authorized_action_ids",
        (),
    )

    action_ids_valid = (
        isinstance(
            action_ids,
            (
                tuple,
                list,
            ),
        )
        and len(
            action_ids
        )
        == len(
            set(
                action_ids
            )
        )
        and all(
            isinstance(
                action_id,
                str,
            )
            and bool(
                action_id.strip()
            )

            for action_id in action_ids
        )
    )

    count_matches = (
        item.get(
            "authorized_action_count"
        )
        == len(
            action_ids
        )
    )

    state_action_consistency_valid = (
        (
            authorization_state
            == "AUTHORIZED"
            and bool(
                action_ids
            )
            and item.get(
                "explicitly_authorized"
            )
            is True
        )
        or (
            authorization_state
            == "REJECTED"
            and not action_ids
            and item.get(
                "explicitly_authorized"
            )
            is False
        )
    )

    safety_boundaries_valid = all(
        (
            item.get(
                "authorization_grants_direct_store_access"
            )
            is False,

            item.get(
                "authorization_bypasses_safety_gates"
            )
            is False,

            item.get(
                "authorization_bypasses_plan_validation"
            )
            is False,

            item.get(
                "authorization_bypasses_certification_validation"
            )
            is False,

            item.get(
                "contract_phase_only"
            )
            is True,

            item.get(
                "repair_executed"
            )
            is False,

            item.get(
                "production_mutation_performed"
            )
            is False,

            item.get(
                "lifecycle_modified"
            )
            is False,

            item.get(
                "archive_modified"
            )
            is False,

            item.get(
                "tombstone_modified"
            )
            is False,

            item.get(
                "body_store_modified"
            )
            is False,

            item.get(
                "runtime_job_created"
            )
            is False,

            item.get(
                "queue_job_created"
            )
            is False,
        )
    )

    checksum_source = {
        key:
            value

        for key, value
        in item.items()

        if key != "authorization_checksum"
    }

    calculated_checksum = (
        calculate_lifecycle_repair_executor_checksum_v1(
            payload=checksum_source,
        )
    )

    checksum_valid = (
        calculated_checksum
        == item.get(
            "authorization_checksum"
        )
    )

    authorization_valid = all(
        (
            not missing_fields,
            schema_valid,
            contract_schema_valid,
            contract_version_valid,
            authorization_state_valid,
            action_ids_valid,
            count_matches,
            state_action_consistency_valid,
            safety_boundaries_valid,
            checksum_valid,
        )
    )

    return _freeze(
        {
            "authorization_valid":
                authorization_valid,

            "missing_fields":
                missing_fields,

            "schema_valid":
                schema_valid,

            "contract_schema_valid":
                contract_schema_valid,

            "contract_version_valid":
                contract_version_valid,

            "authorization_state_valid":
                authorization_state_valid,

            "action_ids_valid":
                action_ids_valid,

            "count_matches":
                count_matches,

            "state_action_consistency_valid":
                state_action_consistency_valid,

            "safety_boundaries_valid":
                safety_boundaries_valid,

            "checksum_valid":
                checksum_valid,

            "calculated_checksum":
                calculated_checksum,

            "stored_checksum":
                item.get(
                    "authorization_checksum"
                ),
        }
    )
def validate_lifecycle_repair_execution_request_v1(
    *,
    execution_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        execution_request,
        field_name="execution_request",
    )

    required_fields = (
        "schema",
        "contract_schema",
        "contract_version",
        "execution_request_id",
        "workspace_id",
        "repair_plan_id",
        "repair_plan_checksum",
        "planner_certification_id",
        "planner_certification_checksum",
        "authorization_id",
        "authorization_checksum",
        "execution_mode",
        "requested_action_ids",
        "requested_action_count",
        "require_all_actions_authorized",
        "required_safety_gates",
        "execution_eligible",
        "execution_authorized",
        "execution_started",
        "execution_completed",
        "repair_executed",
        "production_mutation_performed",
        "lifecycle_modified",
        "archive_modified",
        "tombstone_modified",
        "body_store_modified",
        "runtime_job_created",
        "queue_job_created",
        "contract_phase_only",
        "execution_request_checksum",
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
        == BODY_STORE_LIFECYCLE_REPAIR_EXECUTION_REQUEST_SCHEMA
    )

    contract_schema_valid = (
        request.get(
            "contract_schema"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_SCHEMA
    )

    contract_version_valid = (
        request.get(
            "contract_version"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_VERSION
    )

    identity_fields_valid = all(
        (
            isinstance(
                request.get(
                    "execution_request_id"
                ),
                str,
            )
            and bool(
                request.get(
                    "execution_request_id",
                    "",
                ).strip()
            ),

            isinstance(
                request.get(
                    "workspace_id"
                ),
                str,
            )
            and bool(
                request.get(
                    "workspace_id",
                    "",
                ).strip()
            ),

            isinstance(
                request.get(
                    "repair_plan_id"
                ),
                str,
            )
            and bool(
                request.get(
                    "repair_plan_id",
                    "",
                ).strip()
            ),

            isinstance(
                request.get(
                    "repair_plan_checksum"
                ),
                str,
            )
            and bool(
                request.get(
                    "repair_plan_checksum",
                    "",
                ).strip()
            ),

            isinstance(
                request.get(
                    "planner_certification_id"
                ),
                str,
            )
            and bool(
                request.get(
                    "planner_certification_id",
                    "",
                ).strip()
            ),

            isinstance(
                request.get(
                    "planner_certification_checksum"
                ),
                str,
            )
            and bool(
                request.get(
                    "planner_certification_checksum",
                    "",
                ).strip()
            ),

            isinstance(
                request.get(
                    "authorization_id"
                ),
                str,
            )
            and bool(
                request.get(
                    "authorization_id",
                    "",
                ).strip()
            ),

            isinstance(
                request.get(
                    "authorization_checksum"
                ),
                str,
            )
            and bool(
                request.get(
                    "authorization_checksum",
                    "",
                ).strip()
            ),
        )
    )

    execution_mode_valid = (
        request.get(
            "execution_mode"
        )
        in SUPPORTED_EXECUTION_MODES
    )

    requested_action_ids = request.get(
        "requested_action_ids",
        (),
    )

    requested_action_ids_valid = (
        isinstance(
            requested_action_ids,
            (
                tuple,
                list,
            ),
        )
        and bool(
            requested_action_ids
        )
        and len(
            requested_action_ids
        )
        == len(
            set(
                requested_action_ids
            )
        )
        and all(
            isinstance(
                action_id,
                str,
            )
            and bool(
                action_id.strip()
            )

            for action_id in requested_action_ids
        )
    )

    requested_action_count_matches = (
        request.get(
            "requested_action_count"
        )
        == len(
            requested_action_ids
        )
    )

    require_all_actions_authorized_valid = (
        request.get(
            "require_all_actions_authorized"
        )
        is True
    )

    required_safety_gates_valid = (
        tuple(
            request.get(
                "required_safety_gates",
                (),
            )
        )
        == REQUIRED_EXECUTION_SAFETY_GATES
    )

    contract_phase_boundary_valid = all(
        (
            request.get(
                "execution_eligible"
            )
            is False,

            request.get(
                "execution_authorized"
            )
            is False,

            request.get(
                "execution_started"
            )
            is False,

            request.get(
                "execution_completed"
            )
            is False,

            request.get(
                "repair_executed"
            )
            is False,

            request.get(
                "production_mutation_performed"
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

            request.get(
                "contract_phase_only"
            )
            is True,
        )
    )

    checksum_source = {
        key:
            value

        for key, value
        in request.items()

        if key != "execution_request_checksum"
    }

    calculated_checksum = (
        calculate_lifecycle_repair_executor_checksum_v1(
            payload=checksum_source,
        )
    )

    checksum_valid = (
        calculated_checksum
        == request.get(
            "execution_request_checksum"
        )
    )

    request_valid = all(
        (
            not missing_fields,
            schema_valid,
            contract_schema_valid,
            contract_version_valid,
            identity_fields_valid,
            execution_mode_valid,
            requested_action_ids_valid,
            requested_action_count_matches,
            require_all_actions_authorized_valid,
            required_safety_gates_valid,
            contract_phase_boundary_valid,
            checksum_valid,
        )
    )

    return _freeze(
        {
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

            "identity_fields_valid":
                identity_fields_valid,

            "execution_mode_valid":
                execution_mode_valid,

            "requested_action_ids_valid":
                requested_action_ids_valid,

            "requested_action_count_matches":
                requested_action_count_matches,

            "require_all_actions_authorized_valid":
                require_all_actions_authorized_valid,

            "required_safety_gates_valid":
                required_safety_gates_valid,

            "contract_phase_boundary_valid":
                contract_phase_boundary_valid,

            "checksum_valid":
                checksum_valid,

            "calculated_checksum":
                calculated_checksum,

            "stored_checksum":
                request.get(
                    "execution_request_checksum"
                ),
        }
    )


def certify_lifecycle_repair_executor_contract_v1(
    *,
    authorization: Mapping[str, Any],
    execution_request: Mapping[str, Any],
) -> Mapping[str, Any]:

    authorization_item = _require_mapping(
        authorization,
        field_name="authorization",
    )

    request = _require_mapping(
        execution_request,
        field_name="execution_request",
    )

    authorization_validation = (
        validate_lifecycle_repair_execution_authorization_v1(
            authorization=authorization_item,
        )
    )

    request_validation = (
        validate_lifecycle_repair_execution_request_v1(
            execution_request=request,
        )
    )

    authorization_valid = (
        authorization_validation[
            "authorization_valid"
        ]
        is True
    )

    request_valid = (
        request_validation[
            "request_valid"
        ]
        is True
    )

    workspace_id_matches = (
        authorization_item.get(
            "workspace_id"
        )
        == request.get(
            "workspace_id"
        )
    )

    repair_plan_id_matches = (
        authorization_item.get(
            "repair_plan_id"
        )
        == request.get(
            "repair_plan_id"
        )
    )

    repair_plan_checksum_matches = (
        authorization_item.get(
            "repair_plan_checksum"
        )
        == request.get(
            "repair_plan_checksum"
        )
    )

    planner_certification_id_matches = (
        authorization_item.get(
            "planner_certification_id"
        )
        == request.get(
            "planner_certification_id"
        )
    )

    planner_certification_checksum_matches = (
        authorization_item.get(
            "planner_certification_checksum"
        )
        == request.get(
            "planner_certification_checksum"
        )
    )

    authorization_id_matches = (
        authorization_item.get(
            "authorization_id"
        )
        == request.get(
            "authorization_id"
        )
    )

    authorization_checksum_matches = (
        authorization_item.get(
            "authorization_checksum"
        )
        == request.get(
            "authorization_checksum"
        )
    )

    requested_action_ids = set(
        request.get(
            "requested_action_ids",
            (),
        )
    )

    authorized_action_ids = set(
        authorization_item.get(
            "authorized_action_ids",
            (),
        )
    )

    requested_actions_authorized = (
        bool(
            requested_action_ids
        )
        and requested_action_ids.issubset(
            authorized_action_ids
        )
    )

    all_actions_authorized_requirement_satisfied = (
        request.get(
            "require_all_actions_authorized"
        )
        is True
        and requested_actions_authorized
    )

    explicit_authorization_present = (
        authorization_item.get(
            "authorization_state"
        )
        == "AUTHORIZED"
        and authorization_item.get(
            "explicitly_authorized"
        )
        is True
    )

    dry_run_requested = (
        request.get(
            "execution_mode"
        )
        == "DRY_RUN"
    )

    authorized_apply_requested = (
        request.get(
            "execution_mode"
        )
        == "AUTHORIZED_APPLY"
    )

    apply_eligibility_contractually_possible = all(
        (
            authorization_valid,
            request_valid,
            workspace_id_matches,
            repair_plan_id_matches,
            repair_plan_checksum_matches,
            planner_certification_id_matches,
            planner_certification_checksum_matches,
            authorization_id_matches,
            authorization_checksum_matches,
            explicit_authorization_present,
            requested_actions_authorized,
            all_actions_authorized_requirement_satisfied,
            authorized_apply_requested,
        )
    )

    contract_certified = all(
        (
            authorization_valid,
            request_valid,
            workspace_id_matches,
            repair_plan_id_matches,
            repair_plan_checksum_matches,
            planner_certification_id_matches,
            planner_certification_checksum_matches,
            authorization_id_matches,
            authorization_checksum_matches,
            explicit_authorization_present,
            requested_actions_authorized,
            all_actions_authorized_requirement_satisfied,
        )
    )

    certification = {
        "schema":
            "body_store_lifecycle_repair_executor_contract_certification.v1",

        "contract_version":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_VERSION,

        "execution_request_id":
            request.get(
                "execution_request_id"
            ),

        "authorization_id":
            authorization_item.get(
                "authorization_id"
            ),

        "workspace_id":
            request.get(
                "workspace_id"
            ),

        "repair_plan_id":
            request.get(
                "repair_plan_id"
            ),

        "planner_certification_id":
            request.get(
                "planner_certification_id"
            ),

        "execution_mode":
            request.get(
                "execution_mode"
            ),

        "contract_certified":
            contract_certified,

        "authorization_valid":
            authorization_valid,

        "request_valid":
            request_valid,

        "workspace_id_matches":
            workspace_id_matches,

        "repair_plan_id_matches":
            repair_plan_id_matches,

        "repair_plan_checksum_matches":
            repair_plan_checksum_matches,

        "planner_certification_id_matches":
            planner_certification_id_matches,

        "planner_certification_checksum_matches":
            planner_certification_checksum_matches,

        "authorization_id_matches":
            authorization_id_matches,

        "authorization_checksum_matches":
            authorization_checksum_matches,

        "requested_actions_authorized":
            requested_actions_authorized,

        "all_actions_authorized_requirement_satisfied":
            all_actions_authorized_requirement_satisfied,

        "explicit_authorization_present":
            explicit_authorization_present,

        "dry_run_requested":
            dry_run_requested,

        "authorized_apply_requested":
            authorized_apply_requested,

        "apply_eligibility_contractually_possible":
            apply_eligibility_contractually_possible,

        "authorization_validation":
            authorization_validation,

        "request_validation":
            request_validation,

        "contract_phase_only":
            True,

        "execution_eligible":
            False,

        "execution_authorized":
            False,

        "execution_started":
            False,

        "execution_completed":
            False,

        "repair_executed":
            False,

        "production_mutation_performed":
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

    certification[
        "certification_checksum"
    ] = (
        calculate_lifecycle_repair_executor_checksum_v1(
            payload=certification,
        )
    )

    return _freeze(
        certification
    )


def summarize_lifecycle_repair_executor_contract_v1(
    *,
    certification: Mapping[str, Any],
) -> Mapping[str, Any]:

    item = _require_mapping(
        certification,
        field_name="certification",
    )

    return _freeze(
        {
            "execution_request_id":
                item.get(
                    "execution_request_id"
                ),

            "authorization_id":
                item.get(
                    "authorization_id"
                ),

            "workspace_id":
                item.get(
                    "workspace_id"
                ),

            "repair_plan_id":
                item.get(
                    "repair_plan_id"
                ),

            "execution_mode":
                item.get(
                    "execution_mode"
                ),

            "contract_certified":
                item.get(
                    "contract_certified"
                )
                is True,

            "authorization_valid":
                item.get(
                    "authorization_valid"
                )
                is True,

            "request_valid":
                item.get(
                    "request_valid"
                )
                is True,

            "requested_actions_authorized":
                item.get(
                    "requested_actions_authorized"
                )
                is True,

            "explicit_authorization_present":
                item.get(
                    "explicit_authorization_present"
                )
                is True,

            "apply_eligibility_contractually_possible":
                item.get(
                    "apply_eligibility_contractually_possible"
                )
                is True,

            "contract_phase_only":
                True,

            "execution_eligible":
                False,

            "execution_authorized":
                False,

            "execution_started":
                False,

            "execution_completed":
                False,

            "repair_executed":
                False,

            "production_mutation_performed":
                False,

            "runtime_job_created":
                False,

            "queue_job_created":
                False,

            "certification_checksum":
                item.get(
                    "certification_checksum"
                ),
        }
    )


__all__ = [
    "BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_SCHEMA",
    "BODY_STORE_LIFECYCLE_REPAIR_EXECUTION_REQUEST_SCHEMA",
    "BODY_STORE_LIFECYCLE_REPAIR_EXECUTION_AUTHORIZATION_SCHEMA",
    "BODY_STORE_LIFECYCLE_REPAIR_EXECUTION_RESULT_SCHEMA",
    "BODY_STORE_LIFECYCLE_REPAIR_ACTION_RESULT_SCHEMA",
    "BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_VERSION",
    "SUPPORTED_EXECUTION_MODES",
    "SUPPORTED_EXECUTOR_ACTION_TYPES",
    "NON_EXECUTABLE_PLANNER_ACTION_TYPES",
    "SUPPORTED_AUTHORIZATION_STATES",
    "SUPPORTED_ACTION_EXECUTION_STATUSES",
    "PROHIBITED_DIRECT_EXECUTION_ACTION_TYPES",
    "REQUIRED_EXECUTION_SAFETY_GATES",
    "LifecycleRepairExecutorContractError",
    "calculate_lifecycle_repair_executor_checksum_v1",
    "create_lifecycle_repair_execution_authorization_v1",
    "create_lifecycle_repair_execution_request_v1",
    "validate_lifecycle_repair_execution_authorization_v1",
    "validate_lifecycle_repair_execution_request_v1",
    "certify_lifecycle_repair_executor_contract_v1",
    "summarize_lifecycle_repair_executor_contract_v1",
]
