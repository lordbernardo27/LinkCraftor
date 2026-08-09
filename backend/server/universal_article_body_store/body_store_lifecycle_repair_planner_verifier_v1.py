from __future__ import annotations

import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping


from backend.server.universal_article_body_store.body_store_lifecycle_repair_planner_contract_v1 import (
    BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_VERSION,
    PROHIBITED_REPAIR_ACTION_TYPES,
    SUPPORTED_FINDING_SEVERITIES,
    SUPPORTED_FINDING_TYPES,
    SUPPORTED_REPAIR_ACTION_TYPES,
    validate_lifecycle_repair_planner_request_v1,
)

from backend.server.universal_article_body_store.body_store_lifecycle_repair_planner_engine_v1 import (
    BODY_STORE_LIFECYCLE_REPAIR_PLANNER_ENGINE_VERSION,
    FINDING_TO_REPAIR_ACTION,
    REPAIR_ACTION_RISK_CLASS,
    build_lifecycle_repair_plan_v1,
    validate_lifecycle_repair_plan_v1,
)


BODY_STORE_LIFECYCLE_REPAIR_PLANNER_VERIFIER_SCHEMA = (
    "body_store_lifecycle_repair_planner_verifier.v1"
)

BODY_STORE_LIFECYCLE_REPAIR_PLANNER_VERIFIER_VERSION = "1.0"

BODY_STORE_LIFECYCLE_REPAIR_PLANNER_VERIFICATION_SCHEMA = (
    "body_store_lifecycle_repair_planner_verification.v1"
)


class LifecycleRepairPlannerVerifierError(
    ValueError
):
    """Raised when Lifecycle Repair Planner verification input is invalid."""


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
        raise LifecycleRepairPlannerVerifierError(
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
        raise LifecycleRepairPlannerVerifierError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise LifecycleRepairPlannerVerifierError(
            field_name
            + " must not be empty."
        )

    return normalized


def calculate_lifecycle_repair_planner_verification_checksum_v1(
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


def verify_lifecycle_repair_plan_identity_v1(
    *,
    planner_request: Mapping[str, Any],
    scanner_certification: Mapping[str, Any],
    repair_plan: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        planner_request,
        field_name="planner_request",
    )

    certification = _require_mapping(
        scanner_certification,
        field_name="scanner_certification",
    )

    plan = _require_mapping(
        repair_plan,
        field_name="repair_plan",
    )

    request_validation = (
        validate_lifecycle_repair_planner_request_v1(
            planner_request=request,
        )
    )

    plan_validation = (
        validate_lifecycle_repair_plan_v1(
            repair_plan=plan,
        )
    )

    request_valid = (
        request_validation[
            "request_valid"
        ]
        is True
    )

    plan_valid = (
        plan_validation[
            "plan_valid"
        ]
        is True
    )

    repair_plan_request_id_matches = (
        plan.get(
            "repair_plan_request_id"
        )
        == request.get(
            "repair_plan_request_id"
        )
    )

    workspace_id_matches = (
        plan.get(
            "workspace_id"
        )
        == request.get(
            "workspace_id"
        )
        == certification.get(
            "workspace_id"
        )
    )

    repair_scope_matches = (
        plan.get(
            "repair_scope"
        )
        == request.get(
            "repair_scope"
        )
    )

    request_checksum_matches = (
        plan.get(
            "request_checksum"
        )
        == request.get(
            "request_checksum"
        )
    )

    scanner_certified = (
        certification.get(
            "certified"
        )
        is True
    )

    scanner_verification_passed = (
        certification.get(
            "verification_passed"
        )
        is True
    )

    scanner_scan_request_id_matches = (
        plan.get(
            "scanner_scan_request_id"
        )
        == certification.get(
            "scan_request_id"
        )
    )

    scanner_verification_checksum_matches = (
        plan.get(
            "scanner_verification_checksum"
        )
        == certification.get(
            "verification_checksum"
        )
    )

    contract_version_matches = (
        plan.get(
            "contract_version"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_VERSION
    )

    engine_version_matches = (
        plan.get(
            "engine_version"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_PLANNER_ENGINE_VERSION
    )

    identity_verified = all(
        (
            request_valid,
            plan_valid,
            repair_plan_request_id_matches,
            workspace_id_matches,
            repair_scope_matches,
            request_checksum_matches,
            scanner_certified,
            scanner_verification_passed,
            scanner_scan_request_id_matches,
            scanner_verification_checksum_matches,
            contract_version_matches,
            engine_version_matches,
        )
    )

    return _freeze(
        {
            "identity_verified":
                identity_verified,

            "request_valid":
                request_valid,

            "plan_valid":
                plan_valid,

            "repair_plan_request_id_matches":
                repair_plan_request_id_matches,

            "workspace_id_matches":
                workspace_id_matches,

            "repair_scope_matches":
                repair_scope_matches,

            "request_checksum_matches":
                request_checksum_matches,

            "scanner_certified":
                scanner_certified,

            "scanner_verification_passed":
                scanner_verification_passed,

            "scanner_scan_request_id_matches":
                scanner_scan_request_id_matches,

            "scanner_verification_checksum_matches":
                scanner_verification_checksum_matches,

            "contract_version_matches":
                contract_version_matches,

            "engine_version_matches":
                engine_version_matches,

            "repair_plan_id":
                plan.get(
                    "repair_plan_id"
                ),

            "repair_plan_request_id":
                plan.get(
                    "repair_plan_request_id"
                ),

            "workspace_id":
                plan.get(
                    "workspace_id"
                ),
        }
    )
def verify_lifecycle_repair_actions_v1(
    *,
    planner_request: Mapping[str, Any],
    findings: tuple[Mapping[str, Any], ...]
    | list[Mapping[str, Any]],
    repair_plan: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        planner_request,
        field_name="planner_request",
    )

    plan = _require_mapping(
        repair_plan,
        field_name="repair_plan",
    )

    if not isinstance(
        findings,
        (
            tuple,
            list,
        ),
    ):
        raise LifecycleRepairPlannerVerifierError(
            "findings must be a tuple or list."
        )

    workspace_id = _require_string(
        request.get(
            "workspace_id"
        ),
        field_name="planner_request.workspace_id",
    )

    repair_scope = _require_string(
        request.get(
            "repair_scope"
        ),
        field_name="planner_request.repair_scope",
    )

    supplied_findings: dict[
        str,
        Mapping[str, Any],
    ] = {}

    duplicate_supplied_finding_ids: list[str] = []

    for raw_finding in findings:
        finding = _require_mapping(
            raw_finding,
            field_name="finding",
        )

        finding_id = _require_string(
            finding.get(
                "finding_id"
            ),
            field_name="finding.finding_id",
        )

        if finding_id in supplied_findings:
            duplicate_supplied_finding_ids.append(
                finding_id
            )

        supplied_findings[
            finding_id
        ] = finding

    duplicate_supplied_finding_ids = sorted(
        set(
            duplicate_supplied_finding_ids
        )
    )

    workspace_findings = {
        finding_id:
            finding

        for finding_id, finding
        in supplied_findings.items()

        if finding.get(
            "workspace_id"
        )
        == workspace_id
    }

    if repair_scope == "WORKSPACE":
        expected_finding_ids = set(
            workspace_findings
        )

    elif repair_scope == "FINDING_SET":
        expected_finding_ids = set(
            request.get(
                "finding_ids",
                (),
            )
        )

    else:
        expected_finding_ids = set()

    repair_actions = plan.get(
        "repair_actions",
        (),
    )

    repair_actions_collection_valid = isinstance(
        repair_actions,
        (
            tuple,
            list,
        ),
    )

    action_by_finding: dict[
        str,
        Mapping[str, Any],
    ] = {}

    duplicate_action_finding_ids: list[str] = []

    if repair_actions_collection_valid:
        for raw_action in repair_actions:
            action = _require_mapping(
                raw_action,
                field_name="repair_action",
            )

            source_finding_id = _require_string(
                action.get(
                    "source_finding_id"
                ),
                field_name=(
                    "repair_action."
                    "source_finding_id"
                ),
            )

            if source_finding_id in action_by_finding:
                duplicate_action_finding_ids.append(
                    source_finding_id
                )

            action_by_finding[
                source_finding_id
            ] = action

    duplicate_action_finding_ids = sorted(
        set(
            duplicate_action_finding_ids
        )
    )

    actual_finding_ids = set(
        action_by_finding
    )

    selected_finding_set_matches = (
        actual_finding_ids
        == expected_finding_ids
    )

    missing_expected_finding_ids = tuple(
        sorted(
            expected_finding_ids
            - actual_finding_ids
        )
    )

    unexpected_action_finding_ids = tuple(
        sorted(
            actual_finding_ids
            - expected_finding_ids
        )
    )

    finding_type_matches = True
    severity_matches = True
    workspace_matches = True
    action_mapping_matches = True
    risk_class_matches = True
    automatic_planning_matches = True
    manual_review_matches = True
    planner_decision_matches = True
    prohibited_actions_absent = True
    execution_boundaries_valid = True

    verified_action_count = 0

    for finding_id in sorted(
        expected_finding_ids
    ):
        finding = workspace_findings.get(
            finding_id
        )

        action = action_by_finding.get(
            finding_id
        )

        if finding is None or action is None:
            continue

        verified_action_count += 1

        finding_type = str(
            finding.get(
                "finding_type",
                "",
            )
        ).strip().upper()

        severity = str(
            finding.get(
                "severity",
                "",
            )
        ).strip().upper()

        action_type = action.get(
            "repair_action_type"
        )

        if (
            finding_type
            not in SUPPORTED_FINDING_TYPES
        ):
            finding_type_matches = False

        if (
            severity
            not in SUPPORTED_FINDING_SEVERITIES
        ):
            severity_matches = False

        if (
            action.get(
                "source_finding_type"
            )
            != finding_type
        ):
            finding_type_matches = False

        if (
            action.get(
                "source_finding_severity"
            )
            != severity
        ):
            severity_matches = False

        if (
            action.get(
                "workspace_id"
            )
            != workspace_id
        ):
            workspace_matches = False

        manual_required_by_policy = (
            (
                severity == "CRITICAL"
                and request.get(
                    "require_manual_review_for_critical"
                )
                is True
            )
            or request.get(
                "allow_automatic_planning"
            )
            is False
        )

        if manual_required_by_policy:
            expected_action_type = (
                "MANUAL_REVIEW_REQUIRED"
            )

        else:
            expected_action_type = (
                FINDING_TO_REPAIR_ACTION.get(
                    finding_type,
                    "MANUAL_REVIEW_REQUIRED",
                )
            )

        if action_type != expected_action_type:
            action_mapping_matches = False

        if (
            action_type
            not in SUPPORTED_REPAIR_ACTION_TYPES
        ):
            action_mapping_matches = False

        if action_type in PROHIBITED_REPAIR_ACTION_TYPES:
            prohibited_actions_absent = False

        expected_risk_class = (
            REPAIR_ACTION_RISK_CLASS.get(
                action_type,
                "MANUAL",
            )
        )

        if (
            action.get(
                "risk_class"
            )
            != expected_risk_class
        ):
            risk_class_matches = False

        expected_automatically_planned = (
            action_type
            != "MANUAL_REVIEW_REQUIRED"
            and request.get(
                "allow_automatic_planning"
            )
            is True
            and finding_type
            in FINDING_TO_REPAIR_ACTION
        )

        if (
            action.get(
                "automatically_planned"
            )
            is not expected_automatically_planned
        ):
            automatic_planning_matches = False

        expected_manual_review = (
            action_type
            == "MANUAL_REVIEW_REQUIRED"
            or severity
            == "CRITICAL"
            or expected_risk_class
            in (
                "REVIEW_REQUIRED",
                "MANUAL",
            )
        )

        if (
            action.get(
                "requires_manual_review"
            )
            is not expected_manual_review
        ):
            manual_review_matches = False

        expected_planner_decision = (
            "MANUAL_REVIEW"
            if expected_manual_review
            else "PLANNED"
        )

        if (
            action.get(
                "planner_decision"
            )
            != expected_planner_decision
        ):
            planner_decision_matches = False

        if not all(
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
        ):
            execution_boundaries_valid = False

    supplied_finding_ids_unique = (
        not duplicate_supplied_finding_ids
    )

    repair_action_source_ids_unique = (
        not duplicate_action_finding_ids
    )

    action_count_matches = (
        plan.get(
            "repair_action_count"
        )
        == len(
            repair_actions
        )
        == len(
            expected_finding_ids
        )
    )

    selected_finding_count_matches = (
        plan.get(
            "selected_finding_count"
        )
        == len(
            expected_finding_ids
        )
    )

    actions_verified = all(
        (
            repair_actions_collection_valid,
            supplied_finding_ids_unique,
            repair_action_source_ids_unique,
            selected_finding_set_matches,
            not missing_expected_finding_ids,
            not unexpected_action_finding_ids,
            verified_action_count
            == len(
                expected_finding_ids
            ),
            finding_type_matches,
            severity_matches,
            workspace_matches,
            action_mapping_matches,
            risk_class_matches,
            automatic_planning_matches,
            manual_review_matches,
            planner_decision_matches,
            prohibited_actions_absent,
            execution_boundaries_valid,
            action_count_matches,
            selected_finding_count_matches,
        )
    )

    return _freeze(
        {
            "actions_verified":
                actions_verified,

            "repair_actions_collection_valid":
                repair_actions_collection_valid,

            "supplied_finding_ids_unique":
                supplied_finding_ids_unique,

            "repair_action_source_ids_unique":
                repair_action_source_ids_unique,

            "selected_finding_set_matches":
                selected_finding_set_matches,

            "missing_expected_finding_ids":
                missing_expected_finding_ids,

            "unexpected_action_finding_ids":
                unexpected_action_finding_ids,

            "verified_action_count":
                verified_action_count,

            "expected_action_count":
                len(
                    expected_finding_ids
                ),

            "finding_type_matches":
                finding_type_matches,

            "severity_matches":
                severity_matches,

            "workspace_matches":
                workspace_matches,

            "action_mapping_matches":
                action_mapping_matches,

            "risk_class_matches":
                risk_class_matches,

            "automatic_planning_matches":
                automatic_planning_matches,

            "manual_review_matches":
                manual_review_matches,

            "planner_decision_matches":
                planner_decision_matches,

            "prohibited_actions_absent":
                prohibited_actions_absent,

            "execution_boundaries_valid":
                execution_boundaries_valid,

            "action_count_matches":
                action_count_matches,

            "selected_finding_count_matches":
                selected_finding_count_matches,

            "duplicate_supplied_finding_ids":
                tuple(
                    duplicate_supplied_finding_ids
                ),

            "duplicate_action_finding_ids":
                tuple(
                    duplicate_action_finding_ids
                ),
        }
    )
def verify_lifecycle_repair_plan_safety_v1(
    *,
    repair_plan: Mapping[str, Any],
) -> Mapping[str, Any]:

    plan = _require_mapping(
        repair_plan,
        field_name="repair_plan",
    )

    repair_actions = plan.get(
        "repair_actions",
        (),
    )

    repair_actions_collection_valid = isinstance(
        repair_actions,
        (
            tuple,
            list,
        ),
    )

    planner_mode_valid = (
        plan.get(
            "planner_mode"
        )
        == "PLAN_ONLY"
    )

    plan_generated = (
        plan.get(
            "plan_generated"
        )
        is True
    )

    repair_planned = (
        plan.get(
            "repair_planned"
        )
        is True
    )

    execution_not_authorized = (
        plan.get(
            "execution_authorized"
        )
        is False
    )

    execution_status_valid = (
        plan.get(
            "execution_status"
        )
        == "NOT_EXECUTED"
    )

    repair_not_executed = (
        plan.get(
            "repair_executed"
        )
        is False
    )

    read_only = (
        plan.get(
            "read_only"
        )
        is True
    )

    production_mutation_prohibited = (
        plan.get(
            "production_mutation_allowed"
        )
        is False
    )

    lifecycle_not_modified = (
        plan.get(
            "lifecycle_modified"
        )
        is False
    )

    archive_not_modified = (
        plan.get(
            "archive_modified"
        )
        is False
    )

    tombstone_not_modified = (
        plan.get(
            "tombstone_modified"
        )
        is False
    )

    body_store_not_modified = (
        plan.get(
            "body_store_modified"
        )
        is False
    )

    no_runtime_job_created = (
        plan.get(
            "runtime_job_created"
        )
        is False
    )

    no_queue_job_created = (
        plan.get(
            "queue_job_created"
        )
        is False
    )

    prohibited_actions_absent = True
    action_execution_boundaries_valid = True

    if repair_actions_collection_valid:
        for raw_action in repair_actions:
            action = _require_mapping(
                raw_action,
                field_name="repair_action",
            )

            if (
                action.get(
                    "repair_action_type"
                )
                in PROHIBITED_REPAIR_ACTION_TYPES
            ):
                prohibited_actions_absent = False

            if not all(
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
            ):
                action_execution_boundaries_valid = False

    safety_verified = all(
        (
            repair_actions_collection_valid,
            planner_mode_valid,
            plan_generated,
            repair_planned,
            execution_not_authorized,
            execution_status_valid,
            repair_not_executed,
            read_only,
            production_mutation_prohibited,
            lifecycle_not_modified,
            archive_not_modified,
            tombstone_not_modified,
            body_store_not_modified,
            no_runtime_job_created,
            no_queue_job_created,
            prohibited_actions_absent,
            action_execution_boundaries_valid,
        )
    )

    return _freeze(
        {
            "safety_verified":
                safety_verified,

            "repair_actions_collection_valid":
                repair_actions_collection_valid,

            "planner_mode_valid":
                planner_mode_valid,

            "plan_generated":
                plan_generated,

            "repair_planned":
                repair_planned,

            "execution_not_authorized":
                execution_not_authorized,

            "execution_status_valid":
                execution_status_valid,

            "repair_not_executed":
                repair_not_executed,

            "read_only":
                read_only,

            "production_mutation_prohibited":
                production_mutation_prohibited,

            "lifecycle_not_modified":
                lifecycle_not_modified,

            "archive_not_modified":
                archive_not_modified,

            "tombstone_not_modified":
                tombstone_not_modified,

            "body_store_not_modified":
                body_store_not_modified,

            "no_runtime_job_created":
                no_runtime_job_created,

            "no_queue_job_created":
                no_queue_job_created,

            "prohibited_actions_absent":
                prohibited_actions_absent,

            "action_execution_boundaries_valid":
                action_execution_boundaries_valid,
        }
    )


def verify_lifecycle_repair_plan_reproducibility_v1(
    *,
    planner_request: Mapping[str, Any],
    scanner_certification: Mapping[str, Any],
    findings: tuple[Mapping[str, Any], ...]
    | list[Mapping[str, Any]],
    repair_plan: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        planner_request,
        field_name="planner_request",
    )

    certification = _require_mapping(
        scanner_certification,
        field_name="scanner_certification",
    )

    supplied_plan = _require_mapping(
        repair_plan,
        field_name="repair_plan",
    )

    rebuilt_plan = (
        build_lifecycle_repair_plan_v1(
            planner_request=request,
            scanner_certification=certification,
            findings=findings,
        )
    )

    repair_plan_id_matches = (
        rebuilt_plan.get(
            "repair_plan_id"
        )
        == supplied_plan.get(
            "repair_plan_id"
        )
    )

    repair_plan_checksum_matches = (
        rebuilt_plan.get(
            "repair_plan_checksum"
        )
        == supplied_plan.get(
            "repair_plan_checksum"
        )
    )

    selected_finding_count_matches = (
        rebuilt_plan.get(
            "selected_finding_count"
        )
        == supplied_plan.get(
            "selected_finding_count"
        )
    )

    repair_action_count_matches = (
        rebuilt_plan.get(
            "repair_action_count"
        )
        == supplied_plan.get(
            "repair_action_count"
        )
    )

    automatically_planned_count_matches = (
        rebuilt_plan.get(
            "automatically_planned_action_count"
        )
        == supplied_plan.get(
            "automatically_planned_action_count"
        )
    )

    manual_review_count_matches = (
        rebuilt_plan.get(
            "manual_review_action_count"
        )
        == supplied_plan.get(
            "manual_review_action_count"
        )
    )

    finding_type_counts_match = (
        _json_ready(
            rebuilt_plan.get(
                "finding_type_counts",
                {},
            )
        )
        == _json_ready(
            supplied_plan.get(
                "finding_type_counts",
                {},
            )
        )
    )

    severity_counts_match = (
        _json_ready(
            rebuilt_plan.get(
                "severity_counts",
                {},
            )
        )
        == _json_ready(
            supplied_plan.get(
                "severity_counts",
                {},
            )
        )
    )

    repair_action_type_counts_match = (
        _json_ready(
            rebuilt_plan.get(
                "repair_action_type_counts",
                {},
            )
        )
        == _json_ready(
            supplied_plan.get(
                "repair_action_type_counts",
                {},
            )
        )
    )

    rebuilt_actions = rebuilt_plan.get(
        "repair_actions",
        (),
    )

    supplied_actions = supplied_plan.get(
        "repair_actions",
        (),
    )

    repair_action_ids_match = (
        tuple(
            action.get(
                "repair_action_id"
            )

            for action in rebuilt_actions
        )
        == tuple(
            action.get(
                "repair_action_id"
            )

            for action in supplied_actions
        )
    )

    repair_action_checksums_match = (
        tuple(
            action.get(
                "repair_action_checksum"
            )

            for action in rebuilt_actions
        )
        == tuple(
            action.get(
                "repair_action_checksum"
            )

            for action in supplied_actions
        )
    )

    repair_action_types_match = (
        tuple(
            action.get(
                "repair_action_type"
            )

            for action in rebuilt_actions
        )
        == tuple(
            action.get(
                "repair_action_type"
            )

            for action in supplied_actions
        )
    )

    full_plan_matches = (
        _json_ready(
            rebuilt_plan
        )
        == _json_ready(
            supplied_plan
        )
    )

    reproducibility_verified = all(
        (
            repair_plan_id_matches,
            repair_plan_checksum_matches,
            selected_finding_count_matches,
            repair_action_count_matches,
            automatically_planned_count_matches,
            manual_review_count_matches,
            finding_type_counts_match,
            severity_counts_match,
            repair_action_type_counts_match,
            repair_action_ids_match,
            repair_action_checksums_match,
            repair_action_types_match,
            full_plan_matches,
        )
    )

    return _freeze(
        {
            "reproducibility_verified":
                reproducibility_verified,

            "repair_plan_id_matches":
                repair_plan_id_matches,

            "repair_plan_checksum_matches":
                repair_plan_checksum_matches,

            "selected_finding_count_matches":
                selected_finding_count_matches,

            "repair_action_count_matches":
                repair_action_count_matches,

            "automatically_planned_count_matches":
                automatically_planned_count_matches,

            "manual_review_count_matches":
                manual_review_count_matches,

            "finding_type_counts_match":
                finding_type_counts_match,

            "severity_counts_match":
                severity_counts_match,

            "repair_action_type_counts_match":
                repair_action_type_counts_match,

            "repair_action_ids_match":
                repair_action_ids_match,

            "repair_action_checksums_match":
                repair_action_checksums_match,

            "repair_action_types_match":
                repair_action_types_match,

            "full_plan_matches":
                full_plan_matches,

            "rebuilt_repair_plan_id":
                rebuilt_plan.get(
                    "repair_plan_id"
                ),

            "supplied_repair_plan_id":
                supplied_plan.get(
                    "repair_plan_id"
                ),
        }
    )
def verify_lifecycle_repair_planner_v1(
    *,
    planner_request: Mapping[str, Any],
    scanner_certification: Mapping[str, Any],
    findings: tuple[Mapping[str, Any], ...]
    | list[Mapping[str, Any]],
    repair_plan: Mapping[str, Any],
) -> Mapping[str, Any]:

    request = _require_mapping(
        planner_request,
        field_name="planner_request",
    )

    certification = _require_mapping(
        scanner_certification,
        field_name="scanner_certification",
    )

    plan = _require_mapping(
        repair_plan,
        field_name="repair_plan",
    )

    identity_verification = (
        verify_lifecycle_repair_plan_identity_v1(
            planner_request=request,
            scanner_certification=certification,
            repair_plan=plan,
        )
    )

    action_verification = (
        verify_lifecycle_repair_actions_v1(
            planner_request=request,
            findings=findings,
            repair_plan=plan,
        )
    )

    safety_verification = (
        verify_lifecycle_repair_plan_safety_v1(
            repair_plan=plan,
        )
    )

    reproducibility_verification = (
        verify_lifecycle_repair_plan_reproducibility_v1(
            planner_request=request,
            scanner_certification=certification,
            findings=findings,
            repair_plan=plan,
        )
    )

    identity_verified = (
        identity_verification[
            "identity_verified"
        ]
        is True
    )

    actions_verified = (
        action_verification[
            "actions_verified"
        ]
        is True
    )

    safety_verified = (
        safety_verification[
            "safety_verified"
        ]
        is True
    )

    reproducibility_verified = (
        reproducibility_verification[
            "reproducibility_verified"
        ]
        is True
    )

    repair_actions = plan.get(
        "repair_actions",
        (),
    )

    repair_action_count = (
        len(
            repair_actions
        )
        if isinstance(
            repair_actions,
            (
                tuple,
                list,
            ),
        )
        else 0
    )

    automatic_action_count = sum(
        1

        for action in repair_actions

        if isinstance(
            action,
            Mapping,
        )
        and action.get(
            "automatically_planned"
        )
        is True
    )

    manual_review_action_count = sum(
        1

        for action in repair_actions

        if isinstance(
            action,
            Mapping,
        )
        and action.get(
            "requires_manual_review"
        )
        is True
    )

    verification_passed = all(
        (
            identity_verified,
            actions_verified,
            safety_verified,
            reproducibility_verified,
        )
    )

    verification = {
        "schema":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_VERIFICATION_SCHEMA,

        "verifier_schema":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_VERIFIER_SCHEMA,

        "verifier_version":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_VERIFIER_VERSION,

        "contract_version":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_VERSION,

        "engine_version":
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_ENGINE_VERSION,

        "repair_plan_id":
            plan.get(
                "repair_plan_id"
            ),

        "repair_plan_request_id":
            plan.get(
                "repair_plan_request_id"
            ),

        "workspace_id":
            plan.get(
                "workspace_id"
            ),

        "scanner_scan_request_id":
            plan.get(
                "scanner_scan_request_id"
            ),

        "scanner_verification_checksum":
            plan.get(
                "scanner_verification_checksum"
            ),

        "verification_passed":
            verification_passed,

        "identity_verified":
            identity_verified,

        "actions_verified":
            actions_verified,

        "safety_verified":
            safety_verified,

        "reproducibility_verified":
            reproducibility_verified,

        "identity_verification":
            identity_verification,

        "action_verification":
            action_verification,

        "safety_verification":
            safety_verification,

        "reproducibility_verification":
            reproducibility_verification,

        "repair_action_count":
            repair_action_count,

        "automatically_planned_action_count":
            automatic_action_count,

        "manual_review_action_count":
            manual_review_action_count,

        "planner_mode":
            "PLAN_ONLY",

        "repair_plan_generated":
            plan.get(
                "plan_generated"
            )
            is True,

        "repair_planned":
            plan.get(
                "repair_planned"
            )
            is True,

        "execution_authorized":
            False,

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

    verification[
        "verification_checksum"
    ] = (
        calculate_lifecycle_repair_planner_verification_checksum_v1(
            payload=verification,
        )
    )

    return _freeze(
        verification
    )


def summarize_lifecycle_repair_planner_verification_v1(
    *,
    verification: Mapping[str, Any],
) -> Mapping[str, Any]:

    result = _require_mapping(
        verification,
        field_name="verification",
    )

    return _freeze(
        {
            "repair_plan_id":
                result.get(
                    "repair_plan_id"
                ),

            "repair_plan_request_id":
                result.get(
                    "repair_plan_request_id"
                ),

            "workspace_id":
                result.get(
                    "workspace_id"
                ),

            "verification_passed":
                result.get(
                    "verification_passed"
                )
                is True,

            "identity_verified":
                result.get(
                    "identity_verified"
                )
                is True,

            "actions_verified":
                result.get(
                    "actions_verified"
                )
                is True,

            "safety_verified":
                result.get(
                    "safety_verified"
                )
                is True,

            "reproducibility_verified":
                result.get(
                    "reproducibility_verified"
                )
                is True,

            "repair_action_count":
                result.get(
                    "repair_action_count",
                    0,
                ),

            "automatically_planned_action_count":
                result.get(
                    "automatically_planned_action_count",
                    0,
                ),

            "manual_review_action_count":
                result.get(
                    "manual_review_action_count",
                    0,
                ),

            "planner_mode":
                result.get(
                    "planner_mode"
                ),

            "repair_plan_generated":
                result.get(
                    "repair_plan_generated"
                )
                is True,

            "repair_planned":
                result.get(
                    "repair_planned"
                )
                is True,

            "execution_authorized":
                result.get(
                    "execution_authorized"
                ),

            "repair_executed":
                result.get(
                    "repair_executed"
                ),

            "production_mutation_allowed":
                result.get(
                    "production_mutation_allowed"
                ),

            "runtime_job_created":
                result.get(
                    "runtime_job_created"
                ),

            "queue_job_created":
                result.get(
                    "queue_job_created"
                ),

            "verification_checksum":
                result.get(
                    "verification_checksum"
                ),
        }
    )


__all__ = [
    "BODY_STORE_LIFECYCLE_REPAIR_PLANNER_VERIFIER_SCHEMA",
    "BODY_STORE_LIFECYCLE_REPAIR_PLANNER_VERIFIER_VERSION",
    "BODY_STORE_LIFECYCLE_REPAIR_PLANNER_VERIFICATION_SCHEMA",
    "LifecycleRepairPlannerVerifierError",
    "calculate_lifecycle_repair_planner_verification_checksum_v1",
    "verify_lifecycle_repair_plan_identity_v1",
    "verify_lifecycle_repair_actions_v1",
    "verify_lifecycle_repair_plan_safety_v1",
    "verify_lifecycle_repair_plan_reproducibility_v1",
    "verify_lifecycle_repair_planner_v1",
    "summarize_lifecycle_repair_planner_verification_v1",
]
