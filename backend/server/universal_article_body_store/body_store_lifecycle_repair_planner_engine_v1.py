from __future__ import annotations

import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping


from backend.server.universal_article_body_store.body_store_lifecycle_repair_planner_contract_v1 import (
    AUTOMATICALLY_PLANNABLE_FINDING_TYPES,
    BODY_STORE_LIFECYCLE_REPAIR_ACTION_SCHEMA,
    BODY_STORE_LIFECYCLE_REPAIR_PLAN_SCHEMA,
    BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_VERSION,
    PROHIBITED_REPAIR_ACTION_TYPES,
    SUPPORTED_FINDING_SEVERITIES,
    SUPPORTED_FINDING_TYPES,
    SUPPORTED_REPAIR_ACTION_TYPES,
    calculate_lifecycle_repair_planner_checksum_v1,
    validate_lifecycle_repair_planner_request_v1,
)


BODY_STORE_LIFECYCLE_REPAIR_PLANNER_ENGINE_SCHEMA = (
    "body_store_lifecycle_repair_planner_engine.v1"
)

BODY_STORE_LIFECYCLE_REPAIR_PLANNER_ENGINE_VERSION = "1.0"


FINDING_TO_REPAIR_ACTION = MappingProxyType(
    {
        "DUPLICATE_LIFECYCLE_IDENTITY":
            "RESOLVE_DUPLICATE_IDENTITY",

        "INVALID_JSON_RECORD":
            "QUARANTINE_INVALID_RECORD",

        "RETENTION_STATE_INCONSISTENCY":
            "REVIEW_RETENTION_STATE",

        "TOMBSTONE_CONTENT_BOUNDARY_VIOLATION":
            "REMOVE_TOMBSTONE_CONTENT_REFERENCE",

        "UNSUPPORTED_LIFECYCLE_STATE":
            "NORMALIZE_LIFECYCLE_STATE",
    }
)


REPAIR_ACTION_RISK_CLASS = MappingProxyType(
    {
        "REBUILD_LIFECYCLE_RECORD":
            "CONTROLLED",

        "REBUILD_ARCHIVE_METADATA":
            "CONTROLLED",

        "REBUILD_TOMBSTONE_INDEX":
            "CONTROLLED",

        "REPAIR_REFERENCE_METADATA":
            "CONTROLLED",

        "NORMALIZE_LIFECYCLE_STATE":
            "REVIEW_REQUIRED",

        "RESOLVE_DUPLICATE_IDENTITY":
            "REVIEW_REQUIRED",

        "QUARANTINE_INVALID_RECORD":
            "REVIEW_REQUIRED",

        "REMOVE_TOMBSTONE_CONTENT_REFERENCE":
            "REVIEW_REQUIRED",

        "REVIEW_RETENTION_STATE":
            "MANUAL",

        "MANUAL_REVIEW_REQUIRED":
            "MANUAL",
    }
)


class LifecycleRepairPlannerEngineError(
    ValueError
):
    """Raised when Lifecycle Repair Planner Engine input is invalid."""


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
        raise LifecycleRepairPlannerEngineError(
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
        raise LifecycleRepairPlannerEngineError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise LifecycleRepairPlannerEngineError(
            field_name
            + " must not be empty."
        )

    return normalized


def calculate_lifecycle_repair_plan_checksum_v1(
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


def _normalize_finding_type(
    finding: Mapping[str, Any],
) -> str:

    finding_type = _require_string(
        finding.get(
            "finding_type"
        ),
        field_name="finding_type",
    ).upper()

    if finding_type not in SUPPORTED_FINDING_TYPES:
        raise LifecycleRepairPlannerEngineError(
            "Unsupported finding_type: "
            + finding_type
        )

    return finding_type


def _normalize_finding_severity(
    finding: Mapping[str, Any],
) -> str:

    severity = _require_string(
        finding.get(
            "severity"
        ),
        field_name="severity",
    ).upper()

    if severity not in SUPPORTED_FINDING_SEVERITIES:
        raise LifecycleRepairPlannerEngineError(
            "Unsupported finding severity: "
            + severity
        )

    return severity


def _resolve_repair_action_type_v1(
    *,
    finding_type: str,
    severity: str,
    allow_automatic_planning: bool,
    require_manual_review_for_critical: bool,
) -> str:

    if (
        severity == "CRITICAL"
        and require_manual_review_for_critical
    ):
        return "MANUAL_REVIEW_REQUIRED"

    if not allow_automatic_planning:
        return "MANUAL_REVIEW_REQUIRED"

    if (
        finding_type
        not in AUTOMATICALLY_PLANNABLE_FINDING_TYPES
    ):
        return "MANUAL_REVIEW_REQUIRED"

    action_type = FINDING_TO_REPAIR_ACTION.get(
        finding_type
    )

    if action_type is None:
        return "MANUAL_REVIEW_REQUIRED"

    if action_type in PROHIBITED_REPAIR_ACTION_TYPES:
        raise LifecycleRepairPlannerEngineError(
            "Planner attempted to select a prohibited "
            "repair action: "
            + action_type
        )

    if action_type not in SUPPORTED_REPAIR_ACTION_TYPES:
        raise LifecycleRepairPlannerEngineError(
            "Planner selected an unsupported repair action: "
            + action_type
        )

    return action_type
def _create_repair_action_v1(
    *,
    finding: Mapping[str, Any],
    workspace_id: str,
    allow_automatic_planning: bool,
    require_manual_review_for_critical: bool,
) -> Mapping[str, Any]:

    source_finding = _require_mapping(
        finding,
        field_name="finding",
    )

    finding_id = _require_string(
        source_finding.get(
            "finding_id"
        ),
        field_name="finding_id",
    )

    finding_type = _normalize_finding_type(
        source_finding
    )

    severity = _normalize_finding_severity(
        source_finding
    )

    finding_workspace_id = _require_string(
        source_finding.get(
            "workspace_id"
        ),
        field_name="finding.workspace_id",
    )

    if finding_workspace_id != workspace_id:
        raise LifecycleRepairPlannerEngineError(
            "Finding workspace_id does not match "
            "Repair Planner request workspace_id."
        )

    action_type = _resolve_repair_action_type_v1(
        finding_type=finding_type,
        severity=severity,
        allow_automatic_planning=(
            allow_automatic_planning
        ),
        require_manual_review_for_critical=(
            require_manual_review_for_critical
        ),
    )

    if action_type in PROHIBITED_REPAIR_ACTION_TYPES:
        raise LifecycleRepairPlannerEngineError(
            "Prohibited repair action selected: "
            + action_type
        )

    if action_type not in SUPPORTED_REPAIR_ACTION_TYPES:
        raise LifecycleRepairPlannerEngineError(
            "Unsupported repair action selected: "
            + action_type
        )

    risk_class = REPAIR_ACTION_RISK_CLASS.get(
        action_type,
        "MANUAL",
    )

    requires_manual_review = (
        action_type
        == "MANUAL_REVIEW_REQUIRED"
        or severity
        == "CRITICAL"
        or risk_class
        in (
            "REVIEW_REQUIRED",
            "MANUAL",
        )
    )

    automatically_planned = (
        action_type
        != "MANUAL_REVIEW_REQUIRED"
        and allow_automatic_planning
        and finding_type
        in AUTOMATICALLY_PLANNABLE_FINDING_TYPES
    )

    source_finding_checksum = (
        calculate_lifecycle_repair_plan_checksum_v1(
            payload=source_finding,
        )
    )

    action_identity_source = {
        "workspace_id":
            workspace_id,

        "finding_id":
            finding_id,

        "finding_type":
            finding_type,

        "severity":
            severity,

        "action_type":
            action_type,

        "source_finding_checksum":
            source_finding_checksum,
    }

    action_identity_checksum = (
        calculate_lifecycle_repair_plan_checksum_v1(
            payload=action_identity_source,
        )
    )

    repair_action_id = (
        "repair_action_"
        + action_identity_checksum[
            :24
        ]
    )

    repair_action = {
        "schema":
            BODY_STORE_LIFECYCLE_REPAIR_ACTION_SCHEMA,

        "engine_schema":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_ENGINE_SCHEMA,

        "engine_version":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_ENGINE_VERSION,

        "contract_version":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_VERSION,

        "repair_action_id":
            repair_action_id,

        "workspace_id":
            workspace_id,

        "source_finding_id":
            finding_id,

        "source_finding_type":
            finding_type,

        "source_finding_severity":
            severity,

        "source_finding_checksum":
            source_finding_checksum,

        "repair_action_type":
            action_type,

        "risk_class":
            risk_class,

        "automatically_planned":
            automatically_planned,

        "requires_manual_review":
            requires_manual_review,

        "planner_decision":
            (
                "MANUAL_REVIEW"
                if requires_manual_review
                else "PLANNED"
            ),

        "execution_authorized":
            False,

        "execution_status":
            "NOT_EXECUTED",

        "planner_mode":
            "PLAN_ONLY",

        "read_only":
            True,

        "repair_planned":
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

    checksum_source = dict(
        repair_action
    )

    repair_action[
        "repair_action_checksum"
    ] = (
        calculate_lifecycle_repair_plan_checksum_v1(
            payload=checksum_source,
        )
    )

    return _freeze(
        repair_action
    )


def _select_findings_for_request_v1(
    *,
    planner_request: Mapping[str, Any],
    findings: tuple[Mapping[str, Any], ...],
) -> tuple[Mapping[str, Any], ...]:

    repair_scope = planner_request[
        "repair_scope"
    ]

    workspace_id = planner_request[
        "workspace_id"
    ]

    workspace_findings = tuple(
        finding

        for finding in findings

        if finding.get(
            "workspace_id"
        )
        == workspace_id
    )

    if repair_scope == "WORKSPACE":
        return workspace_findings

    requested_finding_ids = set(
        planner_request[
            "finding_ids"
        ]
    )

    selected_findings = tuple(
        finding

        for finding in workspace_findings

        if finding.get(
            "finding_id"
        )
        in requested_finding_ids
    )

    selected_ids = {
        finding.get(
            "finding_id"
        )

        for finding in selected_findings
    }

    missing_finding_ids = (
        requested_finding_ids
        - selected_ids
    )

    if missing_finding_ids:
        raise LifecycleRepairPlannerEngineError(
            "Requested finding_ids were not present "
            "in the supplied certified findings: "
            + ", ".join(
                sorted(
                    str(
                        finding_id
                    )

                    for finding_id
                    in missing_finding_ids
                )
            )
        )

    return selected_findings
def _normalize_findings_collection_v1(
    *,
    findings: Any,
) -> tuple[Mapping[str, Any], ...]:

    if not isinstance(
        findings,
        (
            tuple,
            list,
        ),
    ):
        raise LifecycleRepairPlannerEngineError(
            "findings must be a tuple or list."
        )

    normalized: list[Mapping[str, Any]] = []

    finding_ids: set[str] = set()

    for item in findings:
        finding = _require_mapping(
            item,
            field_name="finding",
        )

        finding_id = _require_string(
            finding.get(
                "finding_id"
            ),
            field_name="finding_id",
        )

        if finding_id in finding_ids:
            raise LifecycleRepairPlannerEngineError(
                "Duplicate finding_id supplied to "
                "Repair Planner Engine: "
                + finding_id
            )

        finding_ids.add(
            finding_id
        )

        normalized.append(
            finding
        )

    return tuple(
        sorted(
            normalized,
            key=lambda finding: str(
                finding.get(
                    "finding_id"
                )
            ),
        )
    )


def _validate_scanner_certification_v1(
    *,
    scanner_certification: Mapping[str, Any],
    workspace_id: str,
) -> Mapping[str, Any]:

    certification = _require_mapping(
        scanner_certification,
        field_name="scanner_certification",
    )

    certified = (
        certification.get(
            "certified"
        )
        is True
    )

    verification_passed = (
        certification.get(
            "verification_passed"
        )
        is True
    )

    certification_workspace_id = (
        certification.get(
            "workspace_id"
        )
    )

    workspace_matches = (
        certification_workspace_id
        == workspace_id
    )

    scan_request_id = _require_string(
        certification.get(
            "scan_request_id"
        ),
        field_name="scanner_certification.scan_request_id",
    )

    verification_checksum = _require_string(
        certification.get(
            "verification_checksum"
        ),
        field_name=(
            "scanner_certification."
            "verification_checksum"
        ),
    )

    scanner_certification_valid = all(
        (
            certified,
            verification_passed,
            workspace_matches,
        )
    )

    if not scanner_certification_valid:
        raise LifecycleRepairPlannerEngineError(
            "Lifecycle Integrity Scanner certification "
            "is not valid for this Repair Planner request."
        )

    return _freeze(
        {
            "scanner_certification_valid":
                True,

            "scanner_certified":
                certified,

            "scanner_verification_passed":
                verification_passed,

            "workspace_matches":
                workspace_matches,

            "scan_request_id":
                scan_request_id,

            "verification_checksum":
                verification_checksum,
        }
    )


def build_lifecycle_repair_plan_v1(
    *,
    planner_request: Mapping[str, Any],
    scanner_certification: Mapping[str, Any],
    findings: tuple[Mapping[str, Any], ...]
    | list[Mapping[str, Any]],
) -> Mapping[str, Any]:

    request = _require_mapping(
        planner_request,
        field_name="planner_request",
    )

    request_validation = (
        validate_lifecycle_repair_planner_request_v1(
            planner_request=request,
        )
    )

    if (
        request_validation[
            "request_valid"
        ]
        is not True
    ):
        raise LifecycleRepairPlannerEngineError(
            "Lifecycle Repair Planner request "
            "failed contract validation."
        )

    workspace_id = _require_string(
        request[
            "workspace_id"
        ],
        field_name="workspace_id",
    )

    scanner_validation = (
        _validate_scanner_certification_v1(
            scanner_certification=(
                scanner_certification
            ),
            workspace_id=workspace_id,
        )
    )

    normalized_findings = (
        _normalize_findings_collection_v1(
            findings=findings,
        )
    )

    selected_findings = (
        _select_findings_for_request_v1(
            planner_request=request,
            findings=normalized_findings,
        )
    )

    repair_actions = tuple(
        _create_repair_action_v1(
            finding=finding,
            workspace_id=workspace_id,
            allow_automatic_planning=(
                request[
                    "allow_automatic_planning"
                ]
            ),
            require_manual_review_for_critical=(
                request[
                    "require_manual_review_for_critical"
                ]
            ),
        )

        for finding in selected_findings
    )

    repair_actions = tuple(
        sorted(
            repair_actions,
            key=lambda action: str(
                action[
                    "repair_action_id"
                ]
            ),
        )
    )

    manual_review_action_count = sum(
        1

        for action in repair_actions

        if action[
            "requires_manual_review"
        ]
        is True
    )

    automatically_planned_action_count = sum(
        1

        for action in repair_actions

        if action[
            "automatically_planned"
        ]
        is True
    )

    finding_type_counts: dict[str, int] = {}

    severity_counts: dict[str, int] = {}

    repair_action_type_counts: dict[str, int] = {}

    for action in repair_actions:
        finding_type = action[
            "source_finding_type"
        ]

        severity = action[
            "source_finding_severity"
        ]

        action_type = action[
            "repair_action_type"
        ]

        finding_type_counts[
            finding_type
        ] = (
            finding_type_counts.get(
                finding_type,
                0,
            )
            + 1
        )

        severity_counts[
            severity
        ] = (
            severity_counts.get(
                severity,
                0,
            )
            + 1
        )

        repair_action_type_counts[
            action_type
        ] = (
            repair_action_type_counts.get(
                action_type,
                0,
            )
            + 1
        )

    plan_identity_source = {
        "repair_plan_request_id":
            request[
                "repair_plan_request_id"
            ],

        "workspace_id":
            workspace_id,

        "repair_scope":
            request[
                "repair_scope"
            ],

        "request_checksum":
            request[
                "request_checksum"
            ],

        "scanner_scan_request_id":
            scanner_validation[
                "scan_request_id"
            ],

        "scanner_verification_checksum":
            scanner_validation[
                "verification_checksum"
            ],

        "repair_action_ids":
            tuple(
                action[
                    "repair_action_id"
                ]

                for action in repair_actions
            ),
    }

    plan_identity_checksum = (
        calculate_lifecycle_repair_plan_checksum_v1(
            payload=plan_identity_source,
        )
    )

    repair_plan_id = (
        "repair_plan_"
        + plan_identity_checksum[
            :24
        ]
    )

    repair_plan = {
        "schema":
            BODY_STORE_LIFECYCLE_REPAIR_PLAN_SCHEMA,

        "engine_schema":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_ENGINE_SCHEMA,

        "engine_version":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_ENGINE_VERSION,

        "contract_version":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_VERSION,

        "repair_plan_id":
            repair_plan_id,

        "repair_plan_request_id":
            request[
                "repair_plan_request_id"
            ],

        "workspace_id":
            workspace_id,

        "repair_scope":
            request[
                "repair_scope"
            ],

        "request_checksum":
            request[
                "request_checksum"
            ],

        "scanner_scan_request_id":
            scanner_validation[
                "scan_request_id"
            ],

        "scanner_verification_checksum":
            scanner_validation[
                "verification_checksum"
            ],

        "scanner_certification_valid":
            scanner_validation[
                "scanner_certification_valid"
            ],

        "scanner_verification_passed":
            scanner_validation[
                "scanner_verification_passed"
            ],

        "selected_finding_count":
            len(
                selected_findings
            ),

        "repair_action_count":
            len(
                repair_actions
            ),

        "automatically_planned_action_count":
            automatically_planned_action_count,

        "manual_review_action_count":
            manual_review_action_count,

        "finding_type_counts":
            finding_type_counts,

        "severity_counts":
            severity_counts,

        "repair_action_type_counts":
            repair_action_type_counts,

        "repair_actions":
            repair_actions,

        "planner_mode":
            "PLAN_ONLY",

        "plan_generated":
            True,

        "repair_planned":
            True,

        "execution_authorized":
            False,

        "execution_status":
            "NOT_EXECUTED",

        "repair_executed":
            False,

        "read_only":
            True,

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

    checksum_source = dict(
        repair_plan
    )

    repair_plan[
        "repair_plan_checksum"
    ] = (
        calculate_lifecycle_repair_plan_checksum_v1(
            payload=checksum_source,
        )
    )

    return _freeze(
        repair_plan
    )
def _validate_repair_action_v1(
    *,
    repair_action: Mapping[str, Any],
    workspace_id: str,
) -> Mapping[str, Any]:

    action = _require_mapping(
        repair_action,
        field_name="repair_action",
    )

    required_fields = (
        "schema",
        "engine_schema",
        "engine_version",
        "contract_version",
        "repair_action_id",
        "workspace_id",
        "source_finding_id",
        "source_finding_type",
        "source_finding_severity",
        "source_finding_checksum",
        "repair_action_type",
        "risk_class",
        "automatically_planned",
        "requires_manual_review",
        "planner_decision",
        "execution_authorized",
        "execution_status",
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
        "repair_action_checksum",
    )

    missing_fields = tuple(
        field_name
        for field_name in required_fields
        if field_name not in action
    )

    schema_valid = (
        action.get(
            "schema"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_ACTION_SCHEMA
    )

    engine_schema_valid = (
        action.get(
            "engine_schema"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_PLANNER_ENGINE_SCHEMA
    )

    engine_version_valid = (
        action.get(
            "engine_version"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_PLANNER_ENGINE_VERSION
    )

    contract_version_valid = (
        action.get(
            "contract_version"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_VERSION
    )

    workspace_matches = (
        action.get(
            "workspace_id"
        )
        == workspace_id
    )

    finding_type_valid = (
        action.get(
            "source_finding_type"
        )
        in SUPPORTED_FINDING_TYPES
    )

    severity_valid = (
        action.get(
            "source_finding_severity"
        )
        in SUPPORTED_FINDING_SEVERITIES
    )

    action_type = action.get(
        "repair_action_type"
    )

    action_type_valid = (
        action_type
        in SUPPORTED_REPAIR_ACTION_TYPES
    )

    prohibited_action_absent = (
        action_type
        not in PROHIBITED_REPAIR_ACTION_TYPES
    )

    risk_class_valid = (
        action.get(
            "risk_class"
        )
        in (
            "CONTROLLED",
            "REVIEW_REQUIRED",
            "MANUAL",
        )
    )

    planning_flags_valid = all(
        (
            isinstance(
                action.get(
                    "automatically_planned"
                ),
                bool,
            ),

            isinstance(
                action.get(
                    "requires_manual_review"
                ),
                bool,
            ),
        )
    )

    planner_decision_valid = (
        action.get(
            "planner_decision"
        )
        in (
            "PLANNED",
            "MANUAL_REVIEW",
        )
    )

    safety_boundaries_valid = all(
        (
            action.get(
                "execution_authorized"
            )
            is False,

            action.get(
                "execution_status"
            )
            == "NOT_EXECUTED",

            action.get(
                "planner_mode"
            )
            == "PLAN_ONLY",

            action.get(
                "read_only"
            )
            is True,

            action.get(
                "repair_planned"
            )
            is True,

            action.get(
                "repair_executed"
            )
            is False,

            action.get(
                "production_mutation_allowed"
            )
            is False,

            action.get(
                "lifecycle_modified"
            )
            is False,

            action.get(
                "archive_modified"
            )
            is False,

            action.get(
                "tombstone_modified"
            )
            is False,

            action.get(
                "body_store_modified"
            )
            is False,

            action.get(
                "runtime_job_created"
            )
            is False,

            action.get(
                "queue_job_created"
            )
            is False,
        )
    )

    checksum_source = {
        key:
            value

        for key, value
        in action.items()

        if key != "repair_action_checksum"
    }

    calculated_checksum = (
        calculate_lifecycle_repair_plan_checksum_v1(
            payload=checksum_source,
        )
    )

    checksum_valid = (
        calculated_checksum
        == action.get(
            "repair_action_checksum"
        )
    )

    action_valid = all(
        (
            not missing_fields,
            schema_valid,
            engine_schema_valid,
            engine_version_valid,
            contract_version_valid,
            workspace_matches,
            finding_type_valid,
            severity_valid,
            action_type_valid,
            prohibited_action_absent,
            risk_class_valid,
            planning_flags_valid,
            planner_decision_valid,
            safety_boundaries_valid,
            checksum_valid,
        )
    )

    return _freeze(
        {
            "action_valid":
                action_valid,

            "repair_action_id":
                action.get(
                    "repair_action_id"
                ),

            "repair_action_type":
                action_type,

            "missing_fields":
                missing_fields,

            "schema_valid":
                schema_valid,

            "engine_schema_valid":
                engine_schema_valid,

            "engine_version_valid":
                engine_version_valid,

            "contract_version_valid":
                contract_version_valid,

            "workspace_matches":
                workspace_matches,

            "finding_type_valid":
                finding_type_valid,

            "severity_valid":
                severity_valid,

            "action_type_valid":
                action_type_valid,

            "prohibited_action_absent":
                prohibited_action_absent,

            "risk_class_valid":
                risk_class_valid,

            "planning_flags_valid":
                planning_flags_valid,

            "planner_decision_valid":
                planner_decision_valid,

            "safety_boundaries_valid":
                safety_boundaries_valid,

            "checksum_valid":
                checksum_valid,

            "calculated_checksum":
                calculated_checksum,

            "stored_checksum":
                action.get(
                    "repair_action_checksum"
                ),
        }
    )


def validate_lifecycle_repair_plan_v1(
    *,
    repair_plan: Mapping[str, Any],
) -> Mapping[str, Any]:

    plan = _require_mapping(
        repair_plan,
        field_name="repair_plan",
    )

    required_fields = (
        "schema",
        "engine_schema",
        "engine_version",
        "contract_version",
        "repair_plan_id",
        "repair_plan_request_id",
        "workspace_id",
        "repair_scope",
        "request_checksum",
        "scanner_scan_request_id",
        "scanner_verification_checksum",
        "scanner_certification_valid",
        "scanner_verification_passed",
        "selected_finding_count",
        "repair_action_count",
        "automatically_planned_action_count",
        "manual_review_action_count",
        "finding_type_counts",
        "severity_counts",
        "repair_action_type_counts",
        "repair_actions",
        "planner_mode",
        "plan_generated",
        "repair_planned",
        "execution_authorized",
        "execution_status",
        "repair_executed",
        "read_only",
        "production_mutation_allowed",
        "lifecycle_modified",
        "archive_modified",
        "tombstone_modified",
        "body_store_modified",
        "runtime_job_created",
        "queue_job_created",
        "repair_plan_checksum",
    )

    missing_fields = tuple(
        field_name
        for field_name in required_fields
        if field_name not in plan
    )

    schema_valid = (
        plan.get(
            "schema"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_PLAN_SCHEMA
    )

    engine_schema_valid = (
        plan.get(
            "engine_schema"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_PLANNER_ENGINE_SCHEMA
    )

    engine_version_valid = (
        plan.get(
            "engine_version"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_PLANNER_ENGINE_VERSION
    )

    contract_version_valid = (
        plan.get(
            "contract_version"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_VERSION
    )

    workspace_id = plan.get(
        "workspace_id"
    )

    identity_fields_valid = all(
        (
            isinstance(
                plan.get(
                    "repair_plan_id"
                ),
                str,
            ),
            bool(
                str(
                    plan.get(
                        "repair_plan_id",
                        ""
                    )
                ).strip()
            ),

            isinstance(
                plan.get(
                    "repair_plan_request_id"
                ),
                str,
            ),
            bool(
                str(
                    plan.get(
                        "repair_plan_request_id",
                        ""
                    )
                ).strip()
            ),

            isinstance(
                workspace_id,
                str,
            ),
            bool(
                str(
                    workspace_id
                ).strip()
            ),

            isinstance(
                plan.get(
                    "scanner_scan_request_id"
                ),
                str,
            ),

            isinstance(
                plan.get(
                    "scanner_verification_checksum"
                ),
                str,
            ),
        )
    )

    scanner_boundary_valid = all(
        (
            plan.get(
                "scanner_certification_valid"
            )
            is True,

            plan.get(
                "scanner_verification_passed"
            )
            is True,
        )
    )

    repair_actions = plan.get(
        "repair_actions",
        (),
    )

    repair_actions_collection_valid = (
        isinstance(
            repair_actions,
            (
                tuple,
                list,
            ),
        )
    )

    action_validations = tuple(
        _validate_repair_action_v1(
            repair_action=action,
            workspace_id=workspace_id,
        )

        for action in repair_actions

        if repair_actions_collection_valid
    )

    repair_actions_valid = (
        repair_actions_collection_valid
        and len(
            action_validations
        )
        == len(
            repair_actions
        )
        and all(
            validation[
                "action_valid"
            ]
            is True

            for validation
            in action_validations
        )
    )

    repair_action_ids = tuple(
        action.get(
            "repair_action_id"
        )

        for action in repair_actions

        if isinstance(
            action,
            Mapping,
        )
    )

    repair_action_ids_unique = (
        len(
            repair_action_ids
        )
        == len(
            set(
                repair_action_ids
            )
        )
    )

    count_consistency_valid = all(
        (
            plan.get(
                "selected_finding_count"
            )
            == len(
                repair_actions
            ),

            plan.get(
                "repair_action_count"
            )
            == len(
                repair_actions
            ),

            plan.get(
                "automatically_planned_action_count"
            )
            == sum(
                1
                for action in repair_actions
                if action.get(
                    "automatically_planned"
                )
                is True
            ),

            plan.get(
                "manual_review_action_count"
            )
            == sum(
                1
                for action in repair_actions
                if action.get(
                    "requires_manual_review"
                )
                is True
            ),
        )
    )

    prohibited_action_absent = all(
        action.get(
            "repair_action_type"
        )
        not in PROHIBITED_REPAIR_ACTION_TYPES

        for action in repair_actions
    )

    safety_boundaries_valid = all(
        (
            plan.get(
                "planner_mode"
            )
            == "PLAN_ONLY",

            plan.get(
                "plan_generated"
            )
            is True,

            plan.get(
                "repair_planned"
            )
            is True,

            plan.get(
                "execution_authorized"
            )
            is False,

            plan.get(
                "execution_status"
            )
            == "NOT_EXECUTED",

            plan.get(
                "repair_executed"
            )
            is False,

            plan.get(
                "read_only"
            )
            is True,

            plan.get(
                "production_mutation_allowed"
            )
            is False,

            plan.get(
                "lifecycle_modified"
            )
            is False,

            plan.get(
                "archive_modified"
            )
            is False,

            plan.get(
                "tombstone_modified"
            )
            is False,

            plan.get(
                "body_store_modified"
            )
            is False,

            plan.get(
                "runtime_job_created"
            )
            is False,

            plan.get(
                "queue_job_created"
            )
            is False,
        )
    )

    checksum_source = {
        key:
            value

        for key, value
        in plan.items()

        if key != "repair_plan_checksum"
    }

    calculated_checksum = (
        calculate_lifecycle_repair_plan_checksum_v1(
            payload=checksum_source,
        )
    )

    checksum_valid = (
        calculated_checksum
        == plan.get(
            "repair_plan_checksum"
        )
    )

    plan_valid = all(
        (
            not missing_fields,
            schema_valid,
            engine_schema_valid,
            engine_version_valid,
            contract_version_valid,
            identity_fields_valid,
            scanner_boundary_valid,
            repair_actions_collection_valid,
            repair_actions_valid,
            repair_action_ids_unique,
            count_consistency_valid,
            prohibited_action_absent,
            safety_boundaries_valid,
            checksum_valid,
        )
    )

    return _freeze(
        {
            "plan_valid":
                plan_valid,

            "repair_plan_id":
                plan.get(
                    "repair_plan_id"
                ),

            "repair_plan_request_id":
                plan.get(
                    "repair_plan_request_id"
                ),

            "workspace_id":
                workspace_id,

            "missing_fields":
                missing_fields,

            "schema_valid":
                schema_valid,

            "engine_schema_valid":
                engine_schema_valid,

            "engine_version_valid":
                engine_version_valid,

            "contract_version_valid":
                contract_version_valid,

            "identity_fields_valid":
                identity_fields_valid,

            "scanner_boundary_valid":
                scanner_boundary_valid,

            "repair_actions_collection_valid":
                repair_actions_collection_valid,

            "repair_actions_valid":
                repair_actions_valid,

            "repair_action_ids_unique":
                repair_action_ids_unique,

            "count_consistency_valid":
                count_consistency_valid,

            "prohibited_action_absent":
                prohibited_action_absent,

            "safety_boundaries_valid":
                safety_boundaries_valid,

            "checksum_valid":
                checksum_valid,

            "action_validations":
                action_validations,

            "calculated_checksum":
                calculated_checksum,

            "stored_checksum":
                plan.get(
                    "repair_plan_checksum"
                ),

            "repair_executed":
                False,

            "production_mutation_allowed":
                False,

            "runtime_job_created":
                False,

            "queue_job_created":
                False,
        }
    )


def summarize_lifecycle_repair_plan_v1(
    *,
    repair_plan: Mapping[str, Any],
) -> Mapping[str, Any]:

    plan = _require_mapping(
        repair_plan,
        field_name="repair_plan",
    )

    return _freeze(
        {
            "repair_plan_id":
                plan[
                    "repair_plan_id"
                ],

            "repair_plan_request_id":
                plan[
                    "repair_plan_request_id"
                ],

            "workspace_id":
                plan[
                    "workspace_id"
                ],

            "repair_scope":
                plan[
                    "repair_scope"
                ],

            "selected_finding_count":
                plan[
                    "selected_finding_count"
                ],

            "repair_action_count":
                plan[
                    "repair_action_count"
                ],

            "automatically_planned_action_count":
                plan[
                    "automatically_planned_action_count"
                ],

            "manual_review_action_count":
                plan[
                    "manual_review_action_count"
                ],

            "finding_type_counts":
                plan[
                    "finding_type_counts"
                ],

            "severity_counts":
                plan[
                    "severity_counts"
                ],

            "repair_action_type_counts":
                plan[
                    "repair_action_type_counts"
                ],

            "scanner_certification_valid":
                plan[
                    "scanner_certification_valid"
                ],

            "scanner_verification_passed":
                plan[
                    "scanner_verification_passed"
                ],

            "planner_mode":
                plan[
                    "planner_mode"
                ],

            "plan_generated":
                plan[
                    "plan_generated"
                ],

            "repair_planned":
                plan[
                    "repair_planned"
                ],

            "execution_authorized":
                plan[
                    "execution_authorized"
                ],

            "execution_status":
                plan[
                    "execution_status"
                ],

            "repair_executed":
                plan[
                    "repair_executed"
                ],

            "read_only":
                plan[
                    "read_only"
                ],

            "production_mutation_allowed":
                plan[
                    "production_mutation_allowed"
                ],

            "runtime_job_created":
                plan[
                    "runtime_job_created"
                ],

            "queue_job_created":
                plan[
                    "queue_job_created"
                ],
        }
    )


__all__ = [
    "BODY_STORE_LIFECYCLE_REPAIR_PLANNER_ENGINE_SCHEMA",
    "BODY_STORE_LIFECYCLE_REPAIR_PLANNER_ENGINE_VERSION",
    "FINDING_TO_REPAIR_ACTION",
    "REPAIR_ACTION_RISK_CLASS",
    "LifecycleRepairPlannerEngineError",
    "calculate_lifecycle_repair_plan_checksum_v1",
    "build_lifecycle_repair_plan_v1",
    "validate_lifecycle_repair_plan_v1",
    "summarize_lifecycle_repair_plan_v1",
]
