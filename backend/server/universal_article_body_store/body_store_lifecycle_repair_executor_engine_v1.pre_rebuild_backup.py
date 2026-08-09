from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping


from backend.server.universal_article_body_store.body_store_lifecycle_repair_executor_contract_v1 import (
    BODY_STORE_LIFECYCLE_REPAIR_ACTION_RESULT_SCHEMA,
    BODY_STORE_LIFECYCLE_REPAIR_EXECUTION_RESULT_SCHEMA,
    BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_VERSION,
    NON_EXECUTABLE_PLANNER_ACTION_TYPES,
    PROHIBITED_DIRECT_EXECUTION_ACTION_TYPES,
    SUPPORTED_EXECUTOR_ACTION_TYPES,
    certify_lifecycle_repair_executor_contract_v1,
    validate_lifecycle_repair_execution_authorization_v1,
    validate_lifecycle_repair_execution_request_v1,
)

from backend.server.universal_article_body_store.body_store_lifecycle_repair_planner_engine_v1 import (
    calculate_lifecycle_repair_plan_checksum_v1,
    validate_lifecycle_repair_plan_v1,
)

from backend.server.universal_article_body_store.body_store_lifecycle_repair_planner_certification_v1 import (
    validate_lifecycle_repair_planner_certification_v1,
)


BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_SCHEMA = (
    "body_store_lifecycle_repair_executor_engine.v1"
)

BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_VERSION = "1.0"


ENGINE_REQUIRED_SAFETY_GATES = (
    "EXECUTOR_CONTRACT_CERTIFIED",
    "EXECUTION_REQUEST_VALID",
    "EXECUTION_AUTHORIZATION_VALID",
    "REPAIR_PLAN_VALID",
    "PLANNER_CERTIFICATION_VALID",
    "WORKSPACE_ID_MATCH",
    "REPAIR_PLAN_ID_MATCH",
    "REPAIR_PLAN_CHECKSUM_MATCH",
    "PLANNER_CERTIFICATION_ID_MATCH",
    "PLANNER_CERTIFICATION_CHECKSUM_MATCH",
    "EXECUTION_AUTHORIZATION_ID_MATCH",
    "EXECUTION_AUTHORIZATION_CHECKSUM_MATCH",
    "REQUESTED_ACTION_IDS_AUTHORIZED",
    "REQUESTED_ACTION_IDS_EXIST_IN_PLAN",
    "SOURCE_FINDING_EVIDENCE_MATCH",
    "ACTION_IDENTITY_MATCH",
    "NO_NON_EXECUTABLE_ACTION",
    "NO_PROHIBITED_ACTION",
)


SUPPORTED_TARGET_STORES = (
    "LIFECYCLE",
    "ARCHIVE",
    "TOMBSTONE",
    "BODY_STORE",
)


EXECUTOR_STORE_DIRECTORY_NAMES = MappingProxyType(
    {
        "LIFECYCLE":
            "universal_article_body_store_lifecycle",

        "ARCHIVE":
            "universal_article_body_store_archive",

        "TOMBSTONE":
            "universal_article_body_store_tombstones",

        "BODY_STORE":
            "universal_article_body_store",
    }
)


ACTION_TARGET_STORE = MappingProxyType(
    {
        "REBUILD_LIFECYCLE_RECORD":
            "LIFECYCLE",

        "REBUILD_ARCHIVE_METADATA":
            "ARCHIVE",

        "REBUILD_TOMBSTONE_INDEX":
            "TOMBSTONE",

        "REPAIR_REFERENCE_METADATA":
            "LIFECYCLE",

        "NORMALIZE_LIFECYCLE_STATE":
            "LIFECYCLE",

        "RESOLVE_DUPLICATE_IDENTITY":
            "LIFECYCLE",

        "QUARANTINE_INVALID_RECORD":
            "BODY_STORE",

        "REMOVE_TOMBSTONE_CONTENT_REFERENCE":
            "TOMBSTONE",
    }
)


class LifecycleRepairExecutorEngineError(
    ValueError
):
    """Raised when Lifecycle Repair Executor Engine safety validation fails."""


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
        raise LifecycleRepairExecutorEngineError(
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
        raise LifecycleRepairExecutorEngineError(
            field_name
            + " must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise LifecycleRepairExecutorEngineError(
            field_name
            + " must not be empty."
        )

    return normalized


def calculate_lifecycle_repair_executor_engine_checksum_v1(
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


def _resolve_data_root_v1(
    *,
    project_root: str | Path,
) -> Path:

    root = Path(
        project_root
    ).resolve()

    return (
        root
        / "backend"
        / "server"
        / "data"
    )


def _resolve_workspace_store_root_v1(
    *,
    project_root: str | Path,
    workspace_id: str,
    store_name: str,
) -> Path:

    normalized_workspace_id = _require_string(
        workspace_id,
        field_name="workspace_id",
    )

    normalized_store_name = _require_string(
        store_name,
        field_name="store_name",
    ).upper()

    if (
        normalized_store_name
        not in SUPPORTED_TARGET_STORES
    ):
        raise LifecycleRepairExecutorEngineError(
            "Unsupported target store: "
            + normalized_store_name
        )

    directory_name = (
        EXECUTOR_STORE_DIRECTORY_NAMES[
            normalized_store_name
        ]
    )

    return (
        _resolve_data_root_v1(
            project_root=project_root,
        )
        / directory_name
        / normalized_workspace_id
    )


def _load_json_mapping_v1(
    *,
    path: Path,
) -> Mapping[str, Any]:

    if not path.exists():
        raise LifecycleRepairExecutorEngineError(
            "Required JSON record does not exist: "
            + str(
                path
            )
        )

    if not path.is_file():
        raise LifecycleRepairExecutorEngineError(
            "Expected JSON record is not a file: "
            + str(
                path
            )
        )

    try:
        value = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    except Exception as exc:
        raise LifecycleRepairExecutorEngineError(
            "Unable to read JSON record: "
            + str(
                path
            )
        ) from exc

    return _require_mapping(
        value,
        field_name=(
            "JSON record "
            + str(
                path
            )
        ),
    )


def _write_json_atomic_v1(
    *,
    path: Path,
    payload: Mapping[str, Any],
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = path.with_suffix(
        path.suffix
        + ".repair_tmp"
    )

    serialized = json.dumps(
        _json_ready(
            payload
        ),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )

    temporary_path.write_text(
        serialized
        + "\n",
        encoding="utf-8",
    )

    temporary_path.replace(
        path
    )
def _normalize_source_findings_v1(
    *,
    findings: tuple[Mapping[str, Any], ...]
    | list[Mapping[str, Any]],
) -> Mapping[str, Mapping[str, Any]]:

    if not isinstance(
        findings,
        (
            tuple,
            list,
        ),
    ):
        raise LifecycleRepairExecutorEngineError(
            "findings must be a tuple or list."
        )

    indexed: dict[
        str,
        Mapping[str, Any],
    ] = {}

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

        if finding_id in indexed:
            raise LifecycleRepairExecutorEngineError(
                "Duplicate finding_id supplied to Executor: "
                + finding_id
            )

        indexed[
            finding_id
        ] = finding

    return MappingProxyType(
        indexed
    )


def _index_repair_actions_v1(
    *,
    repair_plan: Mapping[str, Any],
) -> Mapping[str, Mapping[str, Any]]:

    plan = _require_mapping(
        repair_plan,
        field_name="repair_plan",
    )

    repair_actions = plan.get(
        "repair_actions"
    )

    if not isinstance(
        repair_actions,
        (
            tuple,
            list,
        ),
    ):
        raise LifecycleRepairExecutorEngineError(
            "repair_plan.repair_actions must be "
            "a tuple or list."
        )

    indexed: dict[
        str,
        Mapping[str, Any],
    ] = {}

    for raw_action in repair_actions:
        action = _require_mapping(
            raw_action,
            field_name="repair_action",
        )

        repair_action_id = _require_string(
            action.get(
                "repair_action_id"
            ),
            field_name=(
                "repair_action.repair_action_id"
            ),
        )

        if repair_action_id in indexed:
            raise LifecycleRepairExecutorEngineError(
                "Duplicate repair_action_id in Repair Plan: "
                + repair_action_id
            )

        indexed[
            repair_action_id
        ] = action

    return MappingProxyType(
        indexed
    )


def _verify_action_source_identity_v1(
    *,
    workspace_id: str,
    repair_action: Mapping[str, Any],
    source_finding: Mapping[str, Any],
) -> Mapping[str, Any]:

    action = _require_mapping(
        repair_action,
        field_name="repair_action",
    )

    finding = _require_mapping(
        source_finding,
        field_name="source_finding",
    )

    finding_id = _require_string(
        finding.get(
            "finding_id"
        ),
        field_name="source_finding.finding_id",
    )

    finding_type = _require_string(
        finding.get(
            "finding_type"
        ),
        field_name="source_finding.finding_type",
    ).upper()

    severity = _require_string(
        finding.get(
            "severity"
        ),
        field_name="source_finding.severity",
    ).upper()

    finding_workspace_id = _require_string(
        finding.get(
            "workspace_id"
        ),
        field_name="source_finding.workspace_id",
    )

    action_type = _require_string(
        action.get(
            "repair_action_type"
        ),
        field_name=(
            "repair_action.repair_action_type"
        ),
    ).upper()

    source_finding_checksum = (
        calculate_lifecycle_repair_plan_checksum_v1(
            payload=finding,
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

    calculated_action_identity_checksum = (
        calculate_lifecycle_repair_plan_checksum_v1(
            payload=action_identity_source,
        )
    )

    expected_repair_action_id = (
        "repair_action_"
        + calculated_action_identity_checksum[
            :24
        ]
    )

    workspace_matches = (
        finding_workspace_id
        == workspace_id
        == action.get(
            "workspace_id"
        )
    )

    source_finding_id_matches = (
        action.get(
            "source_finding_id"
        )
        == finding_id
    )

    source_finding_type_matches = (
        action.get(
            "source_finding_type"
        )
        == finding_type
    )

    source_finding_severity_matches = (
        action.get(
            "source_finding_severity"
        )
        == severity
    )

    source_finding_checksum_matches = (
        action.get(
            "source_finding_checksum"
        )
        == source_finding_checksum
    )

    action_identity_matches = (
        action.get(
            "repair_action_id"
        )
        == expected_repair_action_id
    )

    action_supported = (
        action_type
        in SUPPORTED_EXECUTOR_ACTION_TYPES
    )

    non_executable_action_absent = (
        action_type
        not in NON_EXECUTABLE_PLANNER_ACTION_TYPES
    )

    prohibited_action_absent = (
        action_type
        not in PROHIBITED_DIRECT_EXECUTION_ACTION_TYPES
    )

    identity_verified = all(
        (
            workspace_matches,
            source_finding_id_matches,
            source_finding_type_matches,
            source_finding_severity_matches,
            source_finding_checksum_matches,
            action_identity_matches,
            action_supported,
            non_executable_action_absent,
            prohibited_action_absent,
        )
    )

    return _freeze(
        {
            "identity_verified":
                identity_verified,

            "repair_action_id":
                action.get(
                    "repair_action_id"
                ),

            "source_finding_id":
                finding_id,

            "repair_action_type":
                action_type,

            "workspace_matches":
                workspace_matches,

            "source_finding_id_matches":
                source_finding_id_matches,

            "source_finding_type_matches":
                source_finding_type_matches,

            "source_finding_severity_matches":
                source_finding_severity_matches,

            "source_finding_checksum_matches":
                source_finding_checksum_matches,

            "action_identity_matches":
                action_identity_matches,

            "action_supported":
                action_supported,

            "non_executable_action_absent":
                non_executable_action_absent,

            "prohibited_action_absent":
                prohibited_action_absent,

            "calculated_source_finding_checksum":
                source_finding_checksum,

            "expected_repair_action_id":
                expected_repair_action_id,
        }
    )


def validate_lifecycle_repair_execution_context_v1(
    *,
    repair_plan: Mapping[str, Any],
    planner_certification: Mapping[str, Any],
    authorization: Mapping[str, Any],
    execution_request: Mapping[str, Any],
    findings: tuple[Mapping[str, Any], ...]
    | list[Mapping[str, Any]],
) -> Mapping[str, Any]:

    plan = _require_mapping(
        repair_plan,
        field_name="repair_plan",
    )

    planner_certificate = _require_mapping(
        planner_certification,
        field_name="planner_certification",
    )

    authorization_item = _require_mapping(
        authorization,
        field_name="authorization",
    )

    request = _require_mapping(
        execution_request,
        field_name="execution_request",
    )

    plan_validation = (
        validate_lifecycle_repair_plan_v1(
            repair_plan=plan,
        )
    )

    planner_certification_validation = (
        validate_lifecycle_repair_planner_certification_v1(
            certification=planner_certificate,
        )
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

    contract_certification = (
        certify_lifecycle_repair_executor_contract_v1(
            authorization=authorization_item,
            execution_request=request,
        )
    )

    repair_plan_valid = (
        plan_validation[
            "plan_valid"
        ]
        is True
    )

    planner_certification_valid = (
        planner_certification_validation[
            "certification_valid"
        ]
        is True
    )

    execution_authorization_valid = (
        authorization_validation[
            "authorization_valid"
        ]
        is True
    )

    execution_request_valid = (
        request_validation[
            "request_valid"
        ]
        is True
    )

    executor_contract_certified = (
        contract_certification[
            "contract_certified"
        ]
        is True
    )

    workspace_id = _require_string(
        request.get(
            "workspace_id"
        ),
        field_name="execution_request.workspace_id",
    )

    workspace_id_matches = all(
        (
            plan.get(
                "workspace_id"
            )
            == workspace_id,

            planner_certificate.get(
                "workspace_id"
            )
            == workspace_id,

            authorization_item.get(
                "workspace_id"
            )
            == workspace_id,
        )
    )

    repair_plan_id_matches = all(
        (
            request.get(
                "repair_plan_id"
            )
            == plan.get(
                "repair_plan_id"
            ),

            authorization_item.get(
                "repair_plan_id"
            )
            == plan.get(
                "repair_plan_id"
            ),

            planner_certificate.get(
                "repair_plan_id"
            )
            == plan.get(
                "repair_plan_id"
            ),
        )
    )

    repair_plan_checksum_matches = all(
        (
            request.get(
                "repair_plan_checksum"
            )
            == plan.get(
                "repair_plan_checksum"
            ),

            authorization_item.get(
                "repair_plan_checksum"
            )
            == plan.get(
                "repair_plan_checksum"
            ),
        )
    )

    planner_certification_id_matches = all(
        (
            request.get(
                "planner_certification_id"
            )
            == planner_certificate.get(
                "certification_id"
            ),

            authorization_item.get(
                "planner_certification_id"
            )
            == planner_certificate.get(
                "certification_id"
            ),
        )
    )

    planner_certification_checksum_matches = all(
        (
            request.get(
                "planner_certification_checksum"
            )
            == planner_certificate.get(
                "certification_checksum"
            ),

            authorization_item.get(
                "planner_certification_checksum"
            )
            == planner_certificate.get(
                "certification_checksum"
            ),
        )
    )

    execution_authorization_id_matches = (
        request.get(
            "authorization_id"
        )
        == authorization_item.get(
            "authorization_id"
        )
    )

    execution_authorization_checksum_matches = (
        request.get(
            "authorization_checksum"
        )
        == authorization_item.get(
            "authorization_checksum"
        )
    )

    requested_action_ids = tuple(
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

    requested_action_ids_authorized = (
        bool(
            requested_action_ids
        )
        and all(
            action_id
            in authorized_action_ids

            for action_id
            in requested_action_ids
        )
    )

    indexed_actions = (
        _index_repair_actions_v1(
            repair_plan=plan,
        )
    )

    requested_action_ids_exist_in_plan = (
        bool(
            requested_action_ids
        )
        and all(
            action_id
            in indexed_actions

            for action_id
            in requested_action_ids
        )
    )

    indexed_findings = (
        _normalize_source_findings_v1(
            findings=findings,
        )
    )

    action_identity_verifications: list[
        Mapping[str, Any]
    ] = []

    source_finding_evidence_match = True
    action_identity_match = True
    no_non_executable_action = True
    no_prohibited_action = True

    for action_id in requested_action_ids:
        action = indexed_actions.get(
            action_id
        )

        if action is None:
            source_finding_evidence_match = False
            action_identity_match = False
            continue

        source_finding_id = action.get(
            "source_finding_id"
        )

        source_finding = indexed_findings.get(
            source_finding_id
        )

        if source_finding is None:
            source_finding_evidence_match = False
            action_identity_match = False
            continue

        identity_verification = (
            _verify_action_source_identity_v1(
                workspace_id=workspace_id,
                repair_action=action,
                source_finding=source_finding,
            )
        )

        action_identity_verifications.append(
            identity_verification
        )

        if (
            identity_verification[
                "source_finding_checksum_matches"
            ]
            is not True
        ):
            source_finding_evidence_match = False

        if (
            identity_verification[
                "identity_verified"
            ]
            is not True
        ):
            action_identity_match = False

        if (
            identity_verification[
                "non_executable_action_absent"
            ]
            is not True
        ):
            no_non_executable_action = False

        if (
            identity_verification[
                "prohibited_action_absent"
            ]
            is not True
        ):
            no_prohibited_action = False

    all_requested_actions_verified = (
        len(
            action_identity_verifications
        )
        == len(
            requested_action_ids
        )
    )

    safety_gates = {
        "EXECUTOR_CONTRACT_CERTIFIED":
            executor_contract_certified,

        "EXECUTION_REQUEST_VALID":
            execution_request_valid,

        "EXECUTION_AUTHORIZATION_VALID":
            execution_authorization_valid,

        "REPAIR_PLAN_VALID":
            repair_plan_valid,

        "PLANNER_CERTIFICATION_VALID":
            planner_certification_valid,

        "WORKSPACE_ID_MATCH":
            workspace_id_matches,

        "REPAIR_PLAN_ID_MATCH":
            repair_plan_id_matches,

        "REPAIR_PLAN_CHECKSUM_MATCH":
            repair_plan_checksum_matches,

        "PLANNER_CERTIFICATION_ID_MATCH":
            planner_certification_id_matches,

        "PLANNER_CERTIFICATION_CHECKSUM_MATCH":
            planner_certification_checksum_matches,

        "EXECUTION_AUTHORIZATION_ID_MATCH":
            execution_authorization_id_matches,

        "EXECUTION_AUTHORIZATION_CHECKSUM_MATCH":
            execution_authorization_checksum_matches,

        "REQUESTED_ACTION_IDS_AUTHORIZED":
            requested_action_ids_authorized,

        "REQUESTED_ACTION_IDS_EXIST_IN_PLAN":
            requested_action_ids_exist_in_plan,

        "SOURCE_FINDING_EVIDENCE_MATCH":
            (
                source_finding_evidence_match
                and all_requested_actions_verified
            ),

        "ACTION_IDENTITY_MATCH":
            (
                action_identity_match
                and all_requested_actions_verified
            ),

        "NO_NON_EXECUTABLE_ACTION":
            no_non_executable_action,

        "NO_PROHIBITED_ACTION":
            no_prohibited_action,
    }

    all_required_safety_gates_present = (
        tuple(
            safety_gates
        )
        == ENGINE_REQUIRED_SAFETY_GATES
    )

    all_safety_gates_passed = (
        all_required_safety_gates_present
        and all(
            passed
            is True

            for passed
            in safety_gates.values()
        )
    )

    execution_mode = request.get(
        "execution_mode"
    )

    dry_run_eligible = (
        all_safety_gates_passed
        and execution_mode
        == "DRY_RUN"
    )

    authorized_apply_eligible = (
        all_safety_gates_passed
        and execution_mode
        == "AUTHORIZED_APPLY"
        and authorization_item.get(
            "authorization_state"
        )
        == "AUTHORIZED"
        and authorization_item.get(
            "explicitly_authorized"
        )
        is True
    )

    return _freeze(
        {
            "context_valid":
                all_safety_gates_passed,

            "workspace_id":
                workspace_id,

            "execution_mode":
                execution_mode,

            "requested_action_ids":
                requested_action_ids,

            "requested_action_count":
                len(
                    requested_action_ids
                ),

            "repair_plan_valid":
                repair_plan_valid,

            "planner_certification_valid":
                planner_certification_valid,

            "execution_authorization_valid":
                execution_authorization_valid,

            "execution_request_valid":
                execution_request_valid,

            "executor_contract_certified":
                executor_contract_certified,

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

            "execution_authorization_id_matches":
                execution_authorization_id_matches,

            "execution_authorization_checksum_matches":
                execution_authorization_checksum_matches,

            "requested_action_ids_authorized":
                requested_action_ids_authorized,

            "requested_action_ids_exist_in_plan":
                requested_action_ids_exist_in_plan,

            "source_finding_evidence_match":
                source_finding_evidence_match,

            "action_identity_match":
                action_identity_match,

            "all_requested_actions_verified":
                all_requested_actions_verified,

            "no_non_executable_action":
                no_non_executable_action,

            "no_prohibited_action":
                no_prohibited_action,

            "required_safety_gates":
                ENGINE_REQUIRED_SAFETY_GATES,

            "safety_gates":
                safety_gates,

            "all_required_safety_gates_present":
                all_required_safety_gates_present,

            "all_safety_gates_passed":
                all_safety_gates_passed,

            "dry_run_eligible":
                dry_run_eligible,

            "authorized_apply_eligible":
                authorized_apply_eligible,

            "action_identity_verifications":
                tuple(
                    action_identity_verifications
                ),

            "repair_executed":
                False,

            "production_mutation_performed":
                False,

            "runtime_job_created":
                False,

            "queue_job_created":
                False,
        }
    )
def _assert_path_within_root_v1(
    *,
    candidate_path: Path,
    allowed_root: Path,
) -> Path:

    resolved_candidate = candidate_path.resolve()
    resolved_root = allowed_root.resolve()

    try:
        resolved_candidate.relative_to(
            resolved_root
        )

    except ValueError as exc:
        raise LifecycleRepairExecutorEngineError(
            "Executor target path escapes its "
            "authorized store boundary: "
            + str(
                resolved_candidate
            )
        ) from exc

    return resolved_candidate


def _resolve_safe_relative_record_path_v1(
    *,
    workspace_store_root: Path,
    relative_path: str,
) -> Path:

    normalized_relative_path = _require_string(
        relative_path,
        field_name="relative_path",
    )

    relative = Path(
        normalized_relative_path
    )

    if relative.is_absolute():
        raise LifecycleRepairExecutorEngineError(
            "Executor record path must be relative."
        )

    candidate = (
        workspace_store_root
        / relative
    )

    return _assert_path_within_root_v1(
        candidate_path=candidate,
        allowed_root=workspace_store_root,
    )


def _resolve_quarantine_root_v1(
    *,
    project_root: str | Path,
    workspace_id: str,
) -> Path:

    body_store_root = (
        _resolve_workspace_store_root_v1(
            project_root=project_root,
            workspace_id=workspace_id,
            store_name="BODY_STORE",
        )
    )

    return _assert_path_within_root_v1(
        candidate_path=(
            body_store_root
            / "_repair_quarantine"
        ),
        allowed_root=body_store_root,
    )


def _resolve_executor_backup_root_v1(
    *,
    project_root: str | Path,
    workspace_id: str,
    execution_request_id: str,
) -> Path:

    data_root = _resolve_data_root_v1(
        project_root=project_root,
    )

    normalized_workspace_id = _require_string(
        workspace_id,
        field_name="workspace_id",
    )

    normalized_execution_request_id = _require_string(
        execution_request_id,
        field_name="execution_request_id",
    )

    backup_root = (
        data_root
        / "universal_article_body_store_repair_backups"
        / normalized_workspace_id
        / normalized_execution_request_id
    )

    return _assert_path_within_root_v1(
        candidate_path=backup_root,
        allowed_root=(
            data_root
            / "universal_article_body_store_repair_backups"
        ),
    )


def _calculate_file_checksum_v1(
    *,
    path: Path,
) -> str:

    if not path.exists():
        return "ABSENT"

    if not path.is_file():
        raise LifecycleRepairExecutorEngineError(
            "Checksum target is not a file: "
            + str(
                path
            )
        )

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _create_file_backup_v1(
    *,
    source_path: Path,
    backup_root: Path,
    workspace_store_root: Path,
) -> Mapping[str, Any]:

    safe_source_path = _assert_path_within_root_v1(
        candidate_path=source_path,
        allowed_root=workspace_store_root,
    )

    if not safe_source_path.exists():
        return _freeze(
            {
                "source_path":
                    str(
                        safe_source_path
                    ),

                "source_existed":
                    False,

                "source_checksum_before":
                    "ABSENT",

                "backup_created":
                    False,

                "backup_path":
                    None,

                "backup_checksum":
                    None,
            }
        )

    if not safe_source_path.is_file():
        raise LifecycleRepairExecutorEngineError(
            "Repair target is not a file: "
            + str(
                safe_source_path
            )
        )

    relative_path = safe_source_path.relative_to(
        workspace_store_root.resolve()
    )

    backup_path = (
        backup_root
        / relative_path
    )

    safe_backup_path = _assert_path_within_root_v1(
        candidate_path=backup_path,
        allowed_root=backup_root,
    )

    safe_backup_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        safe_source_path,
        safe_backup_path,
    )

    source_checksum = (
        _calculate_file_checksum_v1(
            path=safe_source_path,
        )
    )

    backup_checksum = (
        _calculate_file_checksum_v1(
            path=safe_backup_path,
        )
    )

    if source_checksum != backup_checksum:
        raise LifecycleRepairExecutorEngineError(
            "Repair backup checksum mismatch."
        )

    return _freeze(
        {
            "source_path":
                str(
                    safe_source_path
                ),

            "source_existed":
                True,

            "source_checksum_before":
                source_checksum,

            "backup_created":
                True,

            "backup_path":
                str(
                    safe_backup_path
                ),

            "backup_checksum":
                backup_checksum,
        }
    )


def _restore_file_backup_v1(
    *,
    backup_record: Mapping[str, Any],
) -> Mapping[str, Any]:

    record = _require_mapping(
        backup_record,
        field_name="backup_record",
    )

    source_path = Path(
        _require_string(
            record.get(
                "source_path"
            ),
            field_name="backup_record.source_path",
        )
    )

    source_existed = (
        record.get(
            "source_existed"
        )
        is True
    )

    backup_created = (
        record.get(
            "backup_created"
        )
        is True
    )

    if source_existed:
        backup_path_value = record.get(
            "backup_path"
        )

        if (
            not backup_created
            or not isinstance(
                backup_path_value,
                str,
            )
            or not backup_path_value.strip()
        ):
            raise LifecycleRepairExecutorEngineError(
                "Rollback backup is missing."
            )

        backup_path = Path(
            backup_path_value
        )

        if not backup_path.exists():
            raise LifecycleRepairExecutorEngineError(
                "Rollback backup file does not exist: "
                + str(
                    backup_path
                )
            )

        source_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            backup_path,
            source_path,
        )

        restored_checksum = (
            _calculate_file_checksum_v1(
                path=source_path,
            )
        )

        expected_checksum = record.get(
            "source_checksum_before"
        )

        rollback_verified = (
            restored_checksum
            == expected_checksum
        )

    else:
        if source_path.exists():
            if not source_path.is_file():
                raise LifecycleRepairExecutorEngineError(
                    "Rollback target unexpectedly became "
                    "a non-file path."
                )

            source_path.unlink()

        restored_checksum = "ABSENT"

        rollback_verified = (
            not source_path.exists()
        )

    return _freeze(
        {
            "source_path":
                str(
                    source_path
                ),

            "rollback_performed":
                True,

            "rollback_verified":
                rollback_verified,

            "restored_checksum":
                restored_checksum,
        }
    )


def _build_dry_run_action_result_v1(
    *,
    repair_action: Mapping[str, Any],
    source_finding: Mapping[str, Any],
    target_store: str,
    target_path: str | None,
) -> Mapping[str, Any]:

    action = _require_mapping(
        repair_action,
        field_name="repair_action",
    )

    finding = _require_mapping(
        source_finding,
        field_name="source_finding",
    )

    result = {
        "schema":
            BODY_STORE_LIFECYCLE_REPAIR_ACTION_RESULT_SCHEMA,

        "executor_engine_schema":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_SCHEMA,

        "executor_engine_version":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_VERSION,

        "repair_action_id":
            action[
                "repair_action_id"
            ],

        "source_finding_id":
            finding[
                "finding_id"
            ],

        "repair_action_type":
            action[
                "repair_action_type"
            ],

        "target_store":
            target_store,

        "target_path":
            target_path,

        "execution_mode":
            "DRY_RUN",

        "execution_status":
            "DRY_RUN_VALIDATED",

        "execution_authorized":
            False,

        "mutation_attempted":
            False,

        "mutation_performed":
            False,

        "backup_created":
            False,

        "rollback_required":
            False,

        "rollback_performed":
            False,

        "repair_executed":
            False,
    }

    result[
        "action_result_checksum"
    ] = (
        calculate_lifecycle_repair_executor_engine_checksum_v1(
            payload=result,
        )
    )

    return _freeze(
        result
    )
CANONICAL_LIFECYCLE_STATES = (
    "ACTIVE",
    "ARCHIVED",
    "RESTORED",
    "PERMANENTLY_DELETED",
)


ACTION_EXECUTION_STRATEGIES = MappingProxyType(
    {
        "REBUILD_LIFECYCLE_RECORD":
            "CONTROLLED_JSON_REBUILD",

        "REBUILD_ARCHIVE_METADATA":
            "CONTROLLED_JSON_REBUILD",

        "REBUILD_TOMBSTONE_INDEX":
            "CONTROLLED_JSON_REBUILD",

        "REPAIR_REFERENCE_METADATA":
            "CONTROLLED_JSON_REBUILD",

        "NORMALIZE_LIFECYCLE_STATE":
            "NORMALIZE_STATE",

        "RESOLVE_DUPLICATE_IDENTITY":
            "CONTROLLED_JSON_REBUILD",

        "QUARANTINE_INVALID_RECORD":
            "QUARANTINE_FILE",

        "REMOVE_TOMBSTONE_CONTENT_REFERENCE":
            "REMOVE_TOMBSTONE_CONTENT",
    }
)


TOMBSTONE_PROHIBITED_CONTENT_FIELDS = (
    "content_body",
    "article_body",
    "body_text",
    "raw_body",
    "raw_content",
    "full_text",
    "document_text",
)


TARGET_PATH_FIELD_NAMES = (
    "target_relative_path",
    "record_relative_path",
    "relative_path",
    "target_path",
    "record_path",
    "file_path",
    "source_path",
)


NESTED_EVIDENCE_FIELD_NAMES = (
    "evidence",
    "details",
    "context",
    "metadata",
    "target",
    "record",
    "repair_evidence",
)


def _collect_candidate_evidence_mappings_v1(
    *,
    source_finding: Mapping[str, Any],
) -> tuple[Mapping[str, Any], ...]:

    root = _require_mapping(
        source_finding,
        field_name="source_finding",
    )

    collected: list[
        Mapping[str, Any]
    ] = []

    seen: set[int] = set()

    def visit(
        value: Mapping[str, Any],
    ) -> None:

        identity = id(
            value
        )

        if identity in seen:
            return

        seen.add(
            identity
        )

        collected.append(
            value
        )

        for field_name in NESTED_EVIDENCE_FIELD_NAMES:
            nested = value.get(
                field_name
            )

            if isinstance(
                nested,
                Mapping,
            ):
                visit(
                    nested
                )

    visit(
        root
    )

    return tuple(
        collected
    )


def _find_first_evidence_value_v1(
    *,
    source_finding: Mapping[str, Any],
    field_names: tuple[str, ...],
) -> Any:

    candidates = (
        _collect_candidate_evidence_mappings_v1(
            source_finding=source_finding,
        )
    )

    for candidate in candidates:
        for field_name in field_names:
            if field_name not in candidate:
                continue

            value = candidate.get(
                field_name
            )

            if value is not None:
                return value

    return None


def _normalize_evidence_path_v1(
    *,
    raw_path: str,
    workspace_store_root: Path,
) -> Path:

    normalized = _require_string(
        raw_path,
        field_name="evidence target path",
    )

    supplied_path = Path(
        normalized
    )

    if supplied_path.is_absolute():
        return _assert_path_within_root_v1(
            candidate_path=supplied_path,
            allowed_root=workspace_store_root,
        )

    return _resolve_safe_relative_record_path_v1(
        workspace_store_root=workspace_store_root,
        relative_path=normalized,
    )


def _resolve_repair_target_descriptor_v1(
    *,
    project_root: str | Path,
    workspace_id: str,
    repair_action: Mapping[str, Any],
    source_finding: Mapping[str, Any],
) -> Mapping[str, Any]:

    action = _require_mapping(
        repair_action,
        field_name="repair_action",
    )

    finding = _require_mapping(
        source_finding,
        field_name="source_finding",
    )

    action_type = _require_string(
        action.get(
            "repair_action_type"
        ),
        field_name="repair_action.repair_action_type",
    ).upper()

    if (
        action_type
        not in SUPPORTED_EXECUTOR_ACTION_TYPES
    ):
        raise LifecycleRepairExecutorEngineError(
            "Unsupported Executor repair action type: "
            + action_type
        )

    target_store = ACTION_TARGET_STORE.get(
        action_type
    )

    if target_store is None:
        raise LifecycleRepairExecutorEngineError(
            "Repair action has no target-store mapping: "
            + action_type
        )

    workspace_store_root = (
        _resolve_workspace_store_root_v1(
            project_root=project_root,
            workspace_id=workspace_id,
            store_name=target_store,
        )
    )

    raw_target_path = (
        _find_first_evidence_value_v1(
            source_finding=finding,
            field_names=TARGET_PATH_FIELD_NAMES,
        )
    )

    target_path: Path | None = None
    target_path_resolved = False
    target_path_error: str | None = None

    if isinstance(
        raw_target_path,
        str,
    ) and raw_target_path.strip():

        try:
            target_path = (
                _normalize_evidence_path_v1(
                    raw_path=raw_target_path,
                    workspace_store_root=(
                        workspace_store_root
                    ),
                )
            )

            target_path_resolved = True

        except LifecycleRepairExecutorEngineError as exc:
            target_path_error = str(
                exc
            )

    target_exists = (
        target_path is not None
        and target_path.exists()
    )

    target_is_file = (
        target_path is not None
        and target_path.is_file()
    )

    if (
        target_path is not None
        and target_exists
        and target_is_file
    ):
        target_checksum_before = (
            _calculate_file_checksum_v1(
                path=target_path,
            )
        )

    elif target_path is not None:
        target_checksum_before = "ABSENT"

    else:
        target_checksum_before = None

    return _freeze(
        {
            "repair_action_id":
                action.get(
                    "repair_action_id"
                ),

            "source_finding_id":
                finding.get(
                    "finding_id"
                ),

            "repair_action_type":
                action_type,

            "target_store":
                target_store,

            "workspace_store_root":
                str(
                    workspace_store_root
                ),

            "raw_target_path":
                raw_target_path,

            "target_path":
                (
                    str(
                        target_path
                    )
                    if target_path is not None
                    else None
                ),

            "target_path_resolved":
                target_path_resolved,

            "target_path_error":
                target_path_error,

            "target_exists":
                target_exists,

            "target_is_file":
                target_is_file,

            "target_checksum_before":
                target_checksum_before,

            "mutation_performed":
                False,
        }
    )


def _extract_normalized_lifecycle_state_v1(
    *,
    source_finding: Mapping[str, Any],
) -> str | None:

    value = _find_first_evidence_value_v1(
        source_finding=source_finding,
        field_names=(
            "normalized_state",
            "expected_state",
            "recommended_state",
            "target_state",
        ),
    )

    if not isinstance(
        value,
        str,
    ):
        return None

    normalized = value.strip().upper()

    if normalized not in CANONICAL_LIFECYCLE_STATES:
        return None

    return normalized


def _extract_controlled_replacement_record_v1(
    *,
    source_finding: Mapping[str, Any],
) -> Mapping[str, Any] | None:

    value = _find_first_evidence_value_v1(
        source_finding=source_finding,
        field_names=(
            "replacement_record",
            "repaired_record",
            "normalized_record",
            "expected_record",
        ),
    )

    if not isinstance(
        value,
        Mapping,
    ):
        return None

    return value


def _build_repair_mutation_intent_v1(
    *,
    project_root: str | Path,
    workspace_id: str,
    repair_action: Mapping[str, Any],
    source_finding: Mapping[str, Any],
) -> Mapping[str, Any]:

    action = _require_mapping(
        repair_action,
        field_name="repair_action",
    )

    finding = _require_mapping(
        source_finding,
        field_name="source_finding",
    )

    action_type = _require_string(
        action.get(
            "repair_action_type"
        ),
        field_name="repair_action.repair_action_type",
    ).upper()

    strategy = ACTION_EXECUTION_STRATEGIES.get(
        action_type
    )

    if strategy is None:
        raise LifecycleRepairExecutorEngineError(
            "No execution strategy exists for action type: "
            + action_type
        )

    target = _resolve_repair_target_descriptor_v1(
        project_root=project_root,
        workspace_id=workspace_id,
        repair_action=action,
        source_finding=finding,
    )

    normalized_state = None
    replacement_record = None

    sufficient_repair_evidence = False
    evidence_reason = ""

    if strategy == "NORMALIZE_STATE":

        normalized_state = (
            _extract_normalized_lifecycle_state_v1(
                source_finding=finding,
            )
        )

        sufficient_repair_evidence = all(
            (
                target[
                    "target_path_resolved"
                ]
                is True,

                target[
                    "target_exists"
                ]
                is True,

                target[
                    "target_is_file"
                ]
                is True,

                normalized_state
                is not None,
            )
        )

        evidence_reason = (
            "Target lifecycle record and canonical "
            "normalized state are required."
        )

    elif strategy == "REMOVE_TOMBSTONE_CONTENT":

        sufficient_repair_evidence = all(
            (
                target[
                    "target_path_resolved"
                ]
                is True,

                target[
                    "target_exists"
                ]
                is True,

                target[
                    "target_is_file"
                ]
                is True,
            )
        )

        evidence_reason = (
            "Existing tombstone JSON record is required."
        )

    elif strategy == "QUARANTINE_FILE":

        sufficient_repair_evidence = all(
            (
                target[
                    "target_path_resolved"
                ]
                is True,

                target[
                    "target_exists"
                ]
                is True,

                target[
                    "target_is_file"
                ]
                is True,
            )
        )

        evidence_reason = (
            "Existing invalid record path is required."
        )

    elif strategy == "CONTROLLED_JSON_REBUILD":

        replacement_record = (
            _extract_controlled_replacement_record_v1(
                source_finding=finding,
            )
        )

        sufficient_repair_evidence = all(
            (
                target[
                    "target_path_resolved"
                ]
                is True,

                replacement_record
                is not None,
            )
        )

        evidence_reason = (
            "Bound target path and explicit replacement "
            "record evidence are required."
        )

    else:
        raise LifecycleRepairExecutorEngineError(
            "Unhandled execution strategy: "
            + strategy
        )

    intent = {
        "repair_action_id":
            action.get(
                "repair_action_id"
            ),

        "source_finding_id":
            finding.get(
                "finding_id"
            ),

        "repair_action_type":
            action_type,

        "execution_strategy":
            strategy,

        "target_store":
            target[
                "target_store"
            ],

        "target_path":
            target[
                "target_path"
            ],

        "target_path_resolved":
            target[
                "target_path_resolved"
            ],

        "target_exists":
            target[
                "target_exists"
            ],

        "target_is_file":
            target[
                "target_is_file"
            ],

        "target_checksum_before":
            target[
                "target_checksum_before"
            ],

        "normalized_lifecycle_state":
            normalized_state,

        "replacement_record":
            replacement_record,

        "sufficient_repair_evidence":
            sufficient_repair_evidence,

        "evidence_requirement":
            evidence_reason,

        "mutation_authorized":
            False,

        "mutation_attempted":
            False,

        "mutation_performed":
            False,

        "repair_executed":
            False,
    }

    intent[
        "mutation_intent_checksum"
    ] = (
        calculate_lifecycle_repair_executor_engine_checksum_v1(
            payload=intent,
        )
    )

    return _freeze(
        intent
    )
DYNAMIC_TARGET_STORE_ACTION_TYPES = (
    "QUARANTINE_INVALID_RECORD",
    "REPAIR_REFERENCE_METADATA",
)


TARGET_STORE_FIELD_NAMES = (
    "target_store",
    "store_name",
    "source_store",
    "record_store",
)


def _resolve_action_target_store_v1(
    *,
    repair_action: Mapping[str, Any],
    source_finding: Mapping[str, Any],
) -> str:

    action = _require_mapping(
        repair_action,
        field_name="repair_action",
    )

    finding = _require_mapping(
        source_finding,
        field_name="source_finding",
    )

    action_type = _require_string(
        action.get(
            "repair_action_type"
        ),
        field_name="repair_action.repair_action_type",
    ).upper()

    evidence_store = (
        _find_first_evidence_value_v1(
            source_finding=finding,
            field_names=TARGET_STORE_FIELD_NAMES,
        )
    )

    if (
        action_type
        in DYNAMIC_TARGET_STORE_ACTION_TYPES
    ):
        if not isinstance(
            evidence_store,
            str,
        ):
            raise LifecycleRepairExecutorEngineError(
                "Repair action "
                + action_type
                + " requires explicit target-store evidence."
            )

        normalized_store = (
            evidence_store
            .strip()
            .upper()
        )

        aliases = {
            "LIFECYCLE_STORE":
                "LIFECYCLE",

            "ARCHIVE_STORE":
                "ARCHIVE",

            "TOMBSTONE_STORE":
                "TOMBSTONE",

            "BODY":
                "BODY_STORE",

            "ARTICLE_BODY_STORE":
                "BODY_STORE",
        }

        normalized_store = aliases.get(
            normalized_store,
            normalized_store,
        )

        if (
            normalized_store
            not in SUPPORTED_TARGET_STORES
        ):
            raise LifecycleRepairExecutorEngineError(
                "Unsupported target-store evidence: "
                + normalized_store
            )

        return normalized_store

    target_store = ACTION_TARGET_STORE.get(
        action_type
    )

    if target_store is None:
        raise LifecycleRepairExecutorEngineError(
            "Repair action has no target-store mapping: "
            + action_type
        )

    return target_store


def _resolve_repair_target_descriptor_v2(
    *,
    project_root: str | Path,
    workspace_id: str,
    repair_action: Mapping[str, Any],
    source_finding: Mapping[str, Any],
) -> Mapping[str, Any]:

    action = _require_mapping(
        repair_action,
        field_name="repair_action",
    )

    finding = _require_mapping(
        source_finding,
        field_name="source_finding",
    )

    action_type = _require_string(
        action.get(
            "repair_action_type"
        ),
        field_name="repair_action.repair_action_type",
    ).upper()

    target_store = (
        _resolve_action_target_store_v1(
            repair_action=action,
            source_finding=finding,
        )
    )

    workspace_store_root = (
        _resolve_workspace_store_root_v1(
            project_root=project_root,
            workspace_id=workspace_id,
            store_name=target_store,
        )
    )

    raw_target_path = (
        _find_first_evidence_value_v1(
            source_finding=finding,
            field_names=TARGET_PATH_FIELD_NAMES,
        )
    )

    target_path: Path | None = None
    target_path_resolved = False
    target_path_error: str | None = None

    if isinstance(
        raw_target_path,
        str,
    ) and raw_target_path.strip():

        try:
            target_path = (
                _normalize_evidence_path_v1(
                    raw_path=raw_target_path,
                    workspace_store_root=(
                        workspace_store_root
                    ),
                )
            )

            target_path_resolved = True

        except LifecycleRepairExecutorEngineError as exc:
            target_path_error = str(
                exc
            )

    target_exists = (
        target_path is not None
        and target_path.exists()
    )

    target_is_file = (
        target_path is not None
        and target_path.is_file()
    )

    if (
        target_path is not None
        and target_exists
        and target_is_file
    ):
        target_checksum_before = (
            _calculate_file_checksum_v1(
                path=target_path,
            )
        )

    elif target_path is not None:
        target_checksum_before = "ABSENT"

    else:
        target_checksum_before = None

    return _freeze(
        {
            "repair_action_id":
                action.get(
                    "repair_action_id"
                ),

            "source_finding_id":
                finding.get(
                    "finding_id"
                ),

            "repair_action_type":
                action_type,

            "target_store":
                target_store,

            "workspace_store_root":
                str(
                    workspace_store_root
                ),

            "raw_target_path":
                raw_target_path,

            "target_path":
                (
                    str(
                        target_path
                    )
                    if target_path is not None
                    else None
                ),

            "target_path_resolved":
                target_path_resolved,

            "target_path_error":
                target_path_error,

            "target_exists":
                target_exists,

            "target_is_file":
                target_is_file,

            "target_checksum_before":
                target_checksum_before,

            "mutation_performed":
                False,
        }
    )


def _build_repair_mutation_intent_v2(
    *,
    project_root: str | Path,
    workspace_id: str,
    repair_action: Mapping[str, Any],
    source_finding: Mapping[str, Any],
) -> Mapping[str, Any]:

    action = _require_mapping(
        repair_action,
        field_name="repair_action",
    )

    finding = _require_mapping(
        source_finding,
        field_name="source_finding",
    )

    action_type = _require_string(
        action.get(
            "repair_action_type"
        ),
        field_name="repair_action.repair_action_type",
    ).upper()

    strategy = ACTION_EXECUTION_STRATEGIES.get(
        action_type
    )

    if strategy is None:
        raise LifecycleRepairExecutorEngineError(
            "No execution strategy exists for action type: "
            + action_type
        )

    target = (
        _resolve_repair_target_descriptor_v2(
            project_root=project_root,
            workspace_id=workspace_id,
            repair_action=action,
            source_finding=finding,
        )
    )

    normalized_state = None
    replacement_record = None

    sufficient_repair_evidence = False
    evidence_reason = ""

    if strategy == "NORMALIZE_STATE":

        normalized_state = (
            _extract_normalized_lifecycle_state_v1(
                source_finding=finding,
            )
        )

        sufficient_repair_evidence = all(
            (
                target[
                    "target_path_resolved"
                ]
                is True,

                target[
                    "target_exists"
                ]
                is True,

                target[
                    "target_is_file"
                ]
                is True,

                normalized_state
                is not None,
            )
        )

        evidence_reason = (
            "Existing lifecycle record and canonical "
            "normalized state are required."
        )

    elif strategy == "REMOVE_TOMBSTONE_CONTENT":

        sufficient_repair_evidence = all(
            (
                target[
                    "target_path_resolved"
                ]
                is True,

                target[
                    "target_exists"
                ]
                is True,

                target[
                    "target_is_file"
                ]
                is True,
            )
        )

        evidence_reason = (
            "Existing tombstone JSON record is required."
        )

    elif strategy == "QUARANTINE_FILE":

        sufficient_repair_evidence = all(
            (
                target[
                    "target_path_resolved"
                ]
                is True,

                target[
                    "target_exists"
                ]
                is True,

                target[
                    "target_is_file"
                ]
                is True,
            )
        )

        evidence_reason = (
            "Existing invalid record and explicit "
            "target-store evidence are required."
        )

    elif strategy == "CONTROLLED_JSON_REBUILD":

        replacement_record = (
            _extract_controlled_replacement_record_v1(
                source_finding=finding,
            )
        )

        sufficient_repair_evidence = all(
            (
                target[
                    "target_path_resolved"
                ]
                is True,

                replacement_record
                is not None,
            )
        )

        evidence_reason = (
            "Bound target path and explicit replacement "
            "record evidence are required."
        )

    else:
        raise LifecycleRepairExecutorEngineError(
            "Unhandled execution strategy: "
            + strategy
        )

    intent = {
        "repair_action_id":
            action.get(
                "repair_action_id"
            ),

        "source_finding_id":
            finding.get(
                "finding_id"
            ),

        "repair_action_type":
            action_type,

        "execution_strategy":
            strategy,

        "target_store":
            target[
                "target_store"
            ],

        "workspace_store_root":
            target[
                "workspace_store_root"
            ],

        "target_path":
            target[
                "target_path"
            ],

        "target_path_resolved":
            target[
                "target_path_resolved"
            ],

        "target_exists":
            target[
                "target_exists"
            ],

        "target_is_file":
            target[
                "target_is_file"
            ],

        "target_checksum_before":
            target[
                "target_checksum_before"
            ],

        "normalized_lifecycle_state":
            normalized_state,

        "replacement_record":
            replacement_record,

        "sufficient_repair_evidence":
            sufficient_repair_evidence,

        "evidence_requirement":
            evidence_reason,

        "mutation_authorized":
            False,

        "mutation_attempted":
            False,

        "mutation_performed":
            False,

        "repair_executed":
            False,
    }

    intent[
        "mutation_intent_checksum"
    ] = (
        calculate_lifecycle_repair_executor_engine_checksum_v1(
            payload=intent,
        )
    )

    return _freeze(
        intent
    )


def _remove_prohibited_tombstone_content_v1(
    *,
    payload: Mapping[str, Any],
) -> tuple[
    Mapping[str, Any],
    tuple[str, ...],
]:

    removed_fields: list[str] = []

    def clean(
        value: Any,
        path: str,
    ) -> Any:

        if isinstance(
            value,
            Mapping,
        ):
            cleaned: dict[
                str,
                Any,
            ] = {}

            for key, item in value.items():
                normalized_key = str(
                    key
                )

                field_path = (
                    normalized_key
                    if not path
                    else path
                    + "."
                    + normalized_key
                )

                if (
                    normalized_key
                    in TOMBSTONE_PROHIBITED_CONTENT_FIELDS
                ):
                    removed_fields.append(
                        field_path
                    )

                    continue

                cleaned[
                    normalized_key
                ] = clean(
                    item,
                    field_path,
                )

            return cleaned

        if isinstance(
            value,
            (
                tuple,
                list,
            ),
        ):
            return [
                clean(
                    item,
                    path,
                )

                for item in value
            ]

        return value

    cleaned_payload = clean(
        payload,
        "",
    )

    return (
        _freeze(
            cleaned_payload
        ),
        tuple(
            removed_fields
        ),
    )


def _validate_replacement_record_boundary_v1(
    *,
    replacement_record: Mapping[str, Any],
    workspace_id: str,
) -> None:

    replacement = _require_mapping(
        replacement_record,
        field_name="replacement_record",
    )

    replacement_workspace_id = (
        replacement.get(
            "workspace_id"
        )
    )

    if (
        replacement_workspace_id
        is not None
        and replacement_workspace_id
        != workspace_id
    ):
        raise LifecycleRepairExecutorEngineError(
            "Replacement record workspace_id does not "
            "match the authorized workspace."
        )


def _execute_json_rebuild_v1(
    *,
    target_path: Path,
    replacement_record: Mapping[str, Any],
    workspace_id: str,
) -> Mapping[str, Any]:

    _validate_replacement_record_boundary_v1(
        replacement_record=replacement_record,
        workspace_id=workspace_id,
    )

    _write_json_atomic_v1(
        path=target_path,
        payload=replacement_record,
    )

    checksum_after = (
        _calculate_file_checksum_v1(
            path=target_path,
        )
    )

    return _freeze(
        {
            "mutation_performed":
                True,

            "target_checksum_after":
                checksum_after,

            "removed_fields":
                (),
        }
    )


def _execute_normalize_state_v1(
    *,
    target_path: Path,
    normalized_state: str,
) -> Mapping[str, Any]:

    record = dict(
        _load_json_mapping_v1(
            path=target_path,
        )
    )

    if (
        normalized_state
        not in CANONICAL_LIFECYCLE_STATES
    ):
        raise LifecycleRepairExecutorEngineError(
            "Refusing non-canonical lifecycle state."
        )

    if "lifecycle_state" in record:
        state_field = "lifecycle_state"

    elif "state" in record:
        state_field = "state"

    else:
        raise LifecycleRepairExecutorEngineError(
            "Lifecycle record does not expose an existing "
            "lifecycle_state or state field."
        )

    previous_state = record.get(
        state_field
    )

    record[
        state_field
    ] = normalized_state

    _write_json_atomic_v1(
        path=target_path,
        payload=record,
    )

    checksum_after = (
        _calculate_file_checksum_v1(
            path=target_path,
        )
    )

    return _freeze(
        {
            "mutation_performed":
                True,

            "state_field":
                state_field,

            "previous_state":
                previous_state,

            "normalized_state":
                normalized_state,

            "target_checksum_after":
                checksum_after,

            "removed_fields":
                (),
        }
    )


def _execute_remove_tombstone_content_v1(
    *,
    target_path: Path,
) -> Mapping[str, Any]:

    record = _load_json_mapping_v1(
        path=target_path,
    )

    (
        cleaned_record,
        removed_fields,
    ) = (
        _remove_prohibited_tombstone_content_v1(
            payload=record,
        )
    )

    if not removed_fields:
        return _freeze(
            {
                "mutation_performed":
                    False,

                "target_checksum_after":
                    _calculate_file_checksum_v1(
                        path=target_path,
                    ),

                "removed_fields":
                    (),
            }
        )

    _write_json_atomic_v1(
        path=target_path,
        payload=cleaned_record,
    )

    checksum_after = (
        _calculate_file_checksum_v1(
            path=target_path,
        )
    )

    return _freeze(
        {
            "mutation_performed":
                True,

            "target_checksum_after":
                checksum_after,

            "removed_fields":
                removed_fields,
        }
    )


def _execute_quarantine_file_v1(
    *,
    project_root: str | Path,
    workspace_id: str,
    source_path: Path,
) -> Mapping[str, Any]:

    data_root = _resolve_data_root_v1(
        project_root=project_root,
    )

    quarantine_root = (
        data_root
        / "universal_article_body_store_repair_quarantine"
        / workspace_id
    ).resolve()

    allowed_quarantine_root = (
        data_root
        / "universal_article_body_store_repair_quarantine"
    ).resolve()

    _assert_path_within_root_v1(
        candidate_path=quarantine_root,
        allowed_root=allowed_quarantine_root,
    )

    source_checksum = (
        _calculate_file_checksum_v1(
            path=source_path,
        )
    )

    quarantine_name = (
        source_path.name
        + "."
        + source_checksum[
            :16
        ]
        + ".quarantine"
    )

    quarantine_path = (
        quarantine_root
        / quarantine_name
    )

    safe_quarantine_path = (
        _assert_path_within_root_v1(
            candidate_path=quarantine_path,
            allowed_root=quarantine_root,
        )
    )

    safe_quarantine_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if safe_quarantine_path.exists():
        raise LifecycleRepairExecutorEngineError(
            "Quarantine destination already exists: "
            + str(
                safe_quarantine_path
            )
        )

    try:
        shutil.copy2(
            source_path,
            safe_quarantine_path,
        )

        quarantine_checksum = (
            _calculate_file_checksum_v1(
                path=safe_quarantine_path,
            )
        )

        if quarantine_checksum != source_checksum:
            raise LifecycleRepairExecutorEngineError(
                "Quarantined record checksum changed."
            )

        source_path.unlink()

        if source_path.exists():
            raise LifecycleRepairExecutorEngineError(
                "Original record still exists after "
                "quarantine commit."
            )

    except Exception:

        if (
            safe_quarantine_path.exists()
            and source_path.exists()
        ):
            if safe_quarantine_path.is_file():
                safe_quarantine_path.unlink()

        raise

    return _freeze(
        {
            "mutation_performed":
                True,

            "source_removed":
                not source_path.exists(),

            "quarantine_path":
                str(
                    safe_quarantine_path
                ),

            "quarantine_checksum":
                quarantine_checksum,

            "target_checksum_after":
                "ABSENT",

            "removed_fields":
                (),
        }
    )


def _dispatch_authorized_mutation_v1(
    *,
    project_root: str | Path,
    workspace_id: str,
    mutation_intent: Mapping[str, Any],
) -> Mapping[str, Any]:

    intent = _require_mapping(
        mutation_intent,
        field_name="mutation_intent",
    )

    if (
        intent.get(
            "sufficient_repair_evidence"
        )
        is not True
    ):
        raise LifecycleRepairExecutorEngineError(
            "Repair evidence is insufficient for mutation."
        )

    strategy = _require_string(
        intent.get(
            "execution_strategy"
        ),
        field_name="mutation_intent.execution_strategy",
    )

    target_path_value = _require_string(
        intent.get(
            "target_path"
        ),
        field_name="mutation_intent.target_path",
    )

    target_path = Path(
        target_path_value
    )

    workspace_store_root = Path(
        _require_string(
            intent.get(
                "workspace_store_root"
            ),
            field_name=(
                "mutation_intent.workspace_store_root"
            ),
        )
    )

    target_path = _assert_path_within_root_v1(
        candidate_path=target_path,
        allowed_root=workspace_store_root,
    )

    if strategy == "CONTROLLED_JSON_REBUILD":

        replacement_record = (
            intent.get(
                "replacement_record"
            )
        )

        if not isinstance(
            replacement_record,
            Mapping,
        ):
            raise LifecycleRepairExecutorEngineError(
                "JSON rebuild requires replacement_record."
            )

        return _execute_json_rebuild_v1(
            target_path=target_path,
            replacement_record=replacement_record,
            workspace_id=workspace_id,
        )

    if strategy == "NORMALIZE_STATE":

        normalized_state = (
            intent.get(
                "normalized_lifecycle_state"
            )
        )

        if not isinstance(
            normalized_state,
            str,
        ):
            raise LifecycleRepairExecutorEngineError(
                "Normalize-state action requires "
                "normalized lifecycle state."
            )

        return _execute_normalize_state_v1(
            target_path=target_path,
            normalized_state=normalized_state,
        )

    if strategy == "REMOVE_TOMBSTONE_CONTENT":

        return _execute_remove_tombstone_content_v1(
            target_path=target_path,
        )

    if strategy == "QUARANTINE_FILE":

        return _execute_quarantine_file_v1(
            project_root=project_root,
            workspace_id=workspace_id,
            source_path=target_path,
        )

    raise LifecycleRepairExecutorEngineError(
        "Unsupported authorized mutation strategy: "
        + strategy
    )
METADATA_ONLY_REPAIR_ACTION_TYPES = (
    "REBUILD_LIFECYCLE_RECORD",
    "REBUILD_ARCHIVE_METADATA",
    "REBUILD_TOMBSTONE_INDEX",
    "REPAIR_REFERENCE_METADATA",
    "RESOLVE_DUPLICATE_IDENTITY",
)


ACTION_ALLOWED_TARGET_STORES = MappingProxyType(
    {
        "REBUILD_LIFECYCLE_RECORD":
            (
                "LIFECYCLE",
            ),

        "REBUILD_ARCHIVE_METADATA":
            (
                "ARCHIVE",
            ),

        "REBUILD_TOMBSTONE_INDEX":
            (
                "TOMBSTONE",
            ),

        "REPAIR_REFERENCE_METADATA":
            (
                "LIFECYCLE",
                "ARCHIVE",
                "TOMBSTONE",
            ),

        "NORMALIZE_LIFECYCLE_STATE":
            (
                "LIFECYCLE",
            ),

        "RESOLVE_DUPLICATE_IDENTITY":
            (
                "LIFECYCLE",
            ),

        "QUARANTINE_INVALID_RECORD":
            (
                "LIFECYCLE",
                "ARCHIVE",
                "TOMBSTONE",
                "BODY_STORE",
            ),

        "REMOVE_TOMBSTONE_CONTENT_REFERENCE":
            (
                "TOMBSTONE",
            ),
    }
)


def _find_prohibited_content_field_paths_v1(
    *,
    payload: Mapping[str, Any],
) -> tuple[str, ...]:

    item = _require_mapping(
        payload,
        field_name="payload",
    )

    discovered: list[str] = []

    def visit(
        value: Any,
        prefix: str,
    ) -> None:

        if isinstance(
            value,
            Mapping,
        ):
            for key, nested in value.items():

                normalized_key = str(
                    key
                )

                path = (
                    normalized_key
                    if not prefix
                    else prefix
                    + "."
                    + normalized_key
                )

                if (
                    normalized_key
                    in TOMBSTONE_PROHIBITED_CONTENT_FIELDS
                ):
                    discovered.append(
                        path
                    )

                visit(
                    nested,
                    path,
                )

        elif isinstance(
            value,
            (
                tuple,
                list,
            ),
        ):
            for index, nested in enumerate(
                value
            ):
                path = (
                    prefix
                    + "["
                    + str(
                        index
                    )
                    + "]"
                )

                visit(
                    nested,
                    path,
                )

    visit(
        item,
        "",
    )

    return tuple(
        discovered
    )


def _validate_action_target_store_boundary_v1(
    *,
    repair_action_type: str,
    target_store: str,
) -> None:

    normalized_action_type = _require_string(
        repair_action_type,
        field_name="repair_action_type",
    ).upper()

    normalized_target_store = _require_string(
        target_store,
        field_name="target_store",
    ).upper()

    allowed_stores = (
        ACTION_ALLOWED_TARGET_STORES.get(
            normalized_action_type
        )
    )

    if allowed_stores is None:
        raise LifecycleRepairExecutorEngineError(
            "Repair action has no authorized "
            "target-store boundary: "
            + normalized_action_type
        )

    if (
        normalized_target_store
        not in allowed_stores
    ):
        raise LifecycleRepairExecutorEngineError(
            "Repair action "
            + normalized_action_type
            + " is not authorized for target store "
            + normalized_target_store
            + "."
        )


def _validate_controlled_replacement_record_v1(
    *,
    repair_action_type: str,
    target_store: str,
    replacement_record: Mapping[str, Any],
    workspace_id: str,
) -> Mapping[str, Any]:

    normalized_action_type = _require_string(
        repair_action_type,
        field_name="repair_action_type",
    ).upper()

    normalized_target_store = _require_string(
        target_store,
        field_name="target_store",
    ).upper()

    replacement = _require_mapping(
        replacement_record,
        field_name="replacement_record",
    )

    _validate_action_target_store_boundary_v1(
        repair_action_type=(
            normalized_action_type
        ),
        target_store=(
            normalized_target_store
        ),
    )

    _validate_replacement_record_boundary_v1(
        replacement_record=replacement,
        workspace_id=workspace_id,
    )

    prohibited_content_fields = (
        _find_prohibited_content_field_paths_v1(
            payload=replacement,
        )
    )

    metadata_only_action = (
        normalized_action_type
        in METADATA_ONLY_REPAIR_ACTION_TYPES
    )

    content_boundary_valid = (
        not metadata_only_action
        or not prohibited_content_fields
    )

    if not content_boundary_valid:
        raise LifecycleRepairExecutorEngineError(
            "Metadata repair replacement record contains "
            "prohibited article-body content fields: "
            + ", ".join(
                prohibited_content_fields
            )
        )

    return _freeze(
        {
            "replacement_record_valid":
                True,

            "repair_action_type":
                normalized_action_type,

            "target_store":
                normalized_target_store,

            "workspace_id":
                workspace_id,

            "metadata_only_action":
                metadata_only_action,

            "prohibited_content_fields":
                prohibited_content_fields,

            "content_boundary_valid":
                content_boundary_valid,
        }
    )


def _validate_mutation_intent_checksum_v1(
    *,
    mutation_intent: Mapping[str, Any],
) -> bool:

    intent = _require_mapping(
        mutation_intent,
        field_name="mutation_intent",
    )

    stored_checksum = intent.get(
        "mutation_intent_checksum"
    )

    if not isinstance(
        stored_checksum,
        str,
    ):
        return False

    checksum_source = {
        key:
            value

        for key, value
        in intent.items()

        if key
        != "mutation_intent_checksum"
    }

    calculated_checksum = (
        calculate_lifecycle_repair_executor_engine_checksum_v1(
            payload=checksum_source,
        )
    )

    return (
        stored_checksum
        == calculated_checksum
    )


def prepare_lifecycle_repair_execution_v1(
    *,
    project_root: str | Path,
    repair_plan: Mapping[str, Any],
    execution_request: Mapping[str, Any],
    findings: tuple[Mapping[str, Any], ...]
    | list[Mapping[str, Any]],
) -> Mapping[str, Any]:

    plan = _require_mapping(
        repair_plan,
        field_name="repair_plan",
    )

    request = _require_mapping(
        execution_request,
        field_name="execution_request",
    )

    workspace_id = _require_string(
        request.get(
            "workspace_id"
        ),
        field_name="execution_request.workspace_id",
    )

    requested_action_ids = tuple(
        request.get(
            "requested_action_ids",
            (),
        )
    )

    if not requested_action_ids:
        raise LifecycleRepairExecutorEngineError(
            "Execution preparation requires at least "
            "one requested repair action."
        )

    indexed_actions = (
        _index_repair_actions_v1(
            repair_plan=plan,
        )
    )

    indexed_findings = (
        _normalize_source_findings_v1(
            findings=findings,
        )
    )

    prepared_actions: list[
        Mapping[str, Any]
    ] = []

    for action_id in requested_action_ids:

        action = indexed_actions.get(
            action_id
        )

        if action is None:
            raise LifecycleRepairExecutorEngineError(
                "Requested action is absent from "
                "the certified Repair Plan: "
                + str(
                    action_id
                )
            )

        source_finding_id = _require_string(
            action.get(
                "source_finding_id"
            ),
            field_name=(
                "repair_action.source_finding_id"
            ),
        )

        source_finding = indexed_findings.get(
            source_finding_id
        )

        if source_finding is None:
            raise LifecycleRepairExecutorEngineError(
                "Original source finding is missing: "
                + source_finding_id
            )

        action_type = _require_string(
            action.get(
                "repair_action_type"
            ),
            field_name=(
                "repair_action.repair_action_type"
            ),
        ).upper()

        if (
            action_type
            in NON_EXECUTABLE_PLANNER_ACTION_TYPES
        ):
            raise LifecycleRepairExecutorEngineError(
                "Planner action remains non-executable: "
                + action_type
            )

        if (
            action_type
            in PROHIBITED_DIRECT_EXECUTION_ACTION_TYPES
        ):
            raise LifecycleRepairExecutorEngineError(
                "Prohibited direct execution action: "
                + action_type
            )

        mutation_intent = (
            _build_repair_mutation_intent_v2(
                project_root=project_root,
                workspace_id=workspace_id,
                repair_action=action,
                source_finding=source_finding,
            )
        )

        mutation_intent_checksum_valid = (
            _validate_mutation_intent_checksum_v1(
                mutation_intent=mutation_intent,
            )
        )

        if not mutation_intent_checksum_valid:
            raise LifecycleRepairExecutorEngineError(
                "Mutation intent checksum verification failed."
            )

        target_store = _require_string(
            mutation_intent.get(
                "target_store"
            ),
            field_name="mutation_intent.target_store",
        ).upper()

        _validate_action_target_store_boundary_v1(
            repair_action_type=action_type,
            target_store=target_store,
        )

        replacement_boundary_valid = True
        replacement_validation = None

        if (
            mutation_intent.get(
                "execution_strategy"
            )
            == "CONTROLLED_JSON_REBUILD"
        ):

            replacement_record = (
                mutation_intent.get(
                    "replacement_record"
                )
            )

            if not isinstance(
                replacement_record,
                Mapping,
            ):
                replacement_boundary_valid = False

            else:
                replacement_validation = (
                    _validate_controlled_replacement_record_v1(
                        repair_action_type=action_type,
                        target_store=target_store,
                        replacement_record=(
                            replacement_record
                        ),
                        workspace_id=workspace_id,
                    )
                )

                replacement_boundary_valid = (
                    replacement_validation[
                        "replacement_record_valid"
                    ]
                    is True
                )

        sufficient_repair_evidence = (
            mutation_intent[
                "sufficient_repair_evidence"
            ]
            is True
        )

        preflight_passed = all(
            (
                mutation_intent_checksum_valid,
                sufficient_repair_evidence,
                replacement_boundary_valid,
            )
        )

        prepared_actions.append(
            _freeze(
                {
                    "repair_action_id":
                        action_id,

                    "source_finding_id":
                        source_finding_id,

                    "repair_action_type":
                        action_type,

                    "target_store":
                        target_store,

                    "execution_strategy":
                        mutation_intent[
                            "execution_strategy"
                        ],

                    "mutation_intent":
                        mutation_intent,

                    "mutation_intent_checksum_valid":
                        mutation_intent_checksum_valid,

                    "sufficient_repair_evidence":
                        sufficient_repair_evidence,

                    "replacement_boundary_valid":
                        replacement_boundary_valid,

                    "replacement_validation":
                        replacement_validation,

                    "preflight_passed":
                        preflight_passed,

                    "mutation_authorized":
                        False,

                    "mutation_attempted":
                        False,

                    "mutation_performed":
                        False,
                }
            )
        )

    all_requested_actions_preflighted = (
        len(
            prepared_actions
        )
        == len(
            requested_action_ids
        )
    )

    all_preflight_checks_passed = (
        all_requested_actions_preflighted
        and all(
            action[
                "preflight_passed"
            ]
            is True

            for action
            in prepared_actions
        )
    )

    result = {
        "executor_engine_schema":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_SCHEMA,

        "executor_engine_version":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_VERSION,

        "workspace_id":
            workspace_id,

        "repair_plan_id":
            plan.get(
                "repair_plan_id"
            ),

        "execution_request_id":
            request.get(
                "execution_request_id"
            ),

        "execution_mode":
            request.get(
                "execution_mode"
            ),

        "requested_action_ids":
            requested_action_ids,

        "requested_action_count":
            len(
                requested_action_ids
            ),

        "prepared_action_count":
            len(
                prepared_actions
            ),

        "all_requested_actions_preflighted":
            all_requested_actions_preflighted,

        "all_preflight_checks_passed":
            all_preflight_checks_passed,

        "prepared_actions":
            tuple(
                prepared_actions
            ),

        "execution_started":
            False,

        "execution_completed":
            False,

        "repair_executed":
            False,

        "mutation_performed":
            False,
    }

    result[
        "preflight_checksum"
    ] = (
        calculate_lifecycle_repair_executor_engine_checksum_v1(
            payload=result,
        )
    )

    return _freeze(
        result
    )


def _execute_json_rebuild_v2(
    *,
    target_path: Path,
    replacement_record: Mapping[str, Any],
    repair_action_type: str,
    target_store: str,
    workspace_id: str,
) -> Mapping[str, Any]:

    _validate_controlled_replacement_record_v1(
        repair_action_type=repair_action_type,
        target_store=target_store,
        replacement_record=replacement_record,
        workspace_id=workspace_id,
    )

    _write_json_atomic_v1(
        path=target_path,
        payload=replacement_record,
    )

    return _freeze(
        {
            "mutation_performed":
                True,

            "target_checksum_after":
                _calculate_file_checksum_v1(
                    path=target_path,
                ),

            "removed_fields":
                (),
        }
    )


def _dispatch_authorized_mutation_v2(
    *,
    project_root: str | Path,
    workspace_id: str,
    mutation_intent: Mapping[str, Any],
) -> Mapping[str, Any]:

    intent = _require_mapping(
        mutation_intent,
        field_name="mutation_intent",
    )

    if not _validate_mutation_intent_checksum_v1(
        mutation_intent=intent,
    ):
        raise LifecycleRepairExecutorEngineError(
            "Refusing mutation with invalid "
            "mutation-intent checksum."
        )

    if (
        intent.get(
            "sufficient_repair_evidence"
        )
        is not True
    ):
        raise LifecycleRepairExecutorEngineError(
            "Repair evidence is insufficient for mutation."
        )

    action_type = _require_string(
        intent.get(
            "repair_action_type"
        ),
        field_name="mutation_intent.repair_action_type",
    ).upper()

    target_store = _require_string(
        intent.get(
            "target_store"
        ),
        field_name="mutation_intent.target_store",
    ).upper()

    _validate_action_target_store_boundary_v1(
        repair_action_type=action_type,
        target_store=target_store,
    )

    strategy = _require_string(
        intent.get(
            "execution_strategy"
        ),
        field_name="mutation_intent.execution_strategy",
    )

    target_path = Path(
        _require_string(
            intent.get(
                "target_path"
            ),
            field_name="mutation_intent.target_path",
        )
    )

    workspace_store_root = Path(
        _require_string(
            intent.get(
                "workspace_store_root"
            ),
            field_name=(
                "mutation_intent.workspace_store_root"
            ),
        )
    )

    target_path = _assert_path_within_root_v1(
        candidate_path=target_path,
        allowed_root=workspace_store_root,
    )

    if strategy == "CONTROLLED_JSON_REBUILD":

        replacement_record = (
            intent.get(
                "replacement_record"
            )
        )

        if not isinstance(
            replacement_record,
            Mapping,
        ):
            raise LifecycleRepairExecutorEngineError(
                "JSON rebuild requires replacement_record."
            )

        return _execute_json_rebuild_v2(
            target_path=target_path,
            replacement_record=replacement_record,
            repair_action_type=action_type,
            target_store=target_store,
            workspace_id=workspace_id,
        )

    if strategy == "NORMALIZE_STATE":

        normalized_state = (
            intent.get(
                "normalized_lifecycle_state"
            )
        )

        if not isinstance(
            normalized_state,
            str,
        ):
            raise LifecycleRepairExecutorEngineError(
                "Normalize-state repair requires "
                "a canonical state."
            )

        return _execute_normalize_state_v1(
            target_path=target_path,
            normalized_state=normalized_state,
        )

    if strategy == "REMOVE_TOMBSTONE_CONTENT":

        return _execute_remove_tombstone_content_v1(
            target_path=target_path,
        )

    if strategy == "QUARANTINE_FILE":

        return _execute_quarantine_file_v1(
            project_root=project_root,
            workspace_id=workspace_id,
            source_path=target_path,
        )

    raise LifecycleRepairExecutorEngineError(
        "Unsupported authorized mutation strategy: "
        + strategy
    )
def _validate_preflight_checksum_v1(
    *,
    preflight: Mapping[str, Any],
) -> bool:

    item = _require_mapping(
        preflight,
        field_name="preflight",
    )

    stored_checksum = item.get(
        "preflight_checksum"
    )

    if not isinstance(
        stored_checksum,
        str,
    ):
        return False

    checksum_source = {
        key:
            value

        for key, value
        in item.items()

        if key != "preflight_checksum"
    }

    calculated_checksum = (
        calculate_lifecycle_repair_executor_engine_checksum_v1(
            payload=checksum_source,
        )
    )

    return (
        stored_checksum
        == calculated_checksum
    )


def _verify_target_unchanged_since_preflight_v1(
    *,
    mutation_intent: Mapping[str, Any],
) -> Mapping[str, Any]:

    intent = _require_mapping(
        mutation_intent,
        field_name="mutation_intent",
    )

    target_path = Path(
        _require_string(
            intent.get(
                "target_path"
            ),
            field_name="mutation_intent.target_path",
        )
    )

    workspace_store_root = Path(
        _require_string(
            intent.get(
                "workspace_store_root"
            ),
            field_name=(
                "mutation_intent.workspace_store_root"
            ),
        )
    )

    target_path = _assert_path_within_root_v1(
        candidate_path=target_path,
        allowed_root=workspace_store_root,
    )

    expected_checksum = intent.get(
        "target_checksum_before"
    )

    if target_path.exists():

        if not target_path.is_file():
            raise LifecycleRepairExecutorEngineError(
                "Repair target changed into a non-file "
                "after preflight."
            )

        actual_checksum = (
            _calculate_file_checksum_v1(
                path=target_path,
            )
        )

    else:
        actual_checksum = "ABSENT"

    unchanged = (
        actual_checksum
        == expected_checksum
    )

    return _freeze(
        {
            "target_path":
                str(
                    target_path
                ),

            "expected_checksum":
                expected_checksum,

            "actual_checksum":
                actual_checksum,

            "target_unchanged":
                unchanged,
        }
    )


def _remove_quarantine_artifact_for_rollback_v1(
    *,
    mutation_result: Mapping[str, Any],
) -> Mapping[str, Any]:

    result = _require_mapping(
        mutation_result,
        field_name="mutation_result",
    )

    quarantine_path_value = result.get(
        "quarantine_path"
    )

    if not isinstance(
        quarantine_path_value,
        str,
    ) or not quarantine_path_value.strip():

        return _freeze(
            {
                "quarantine_cleanup_required":
                    False,

                "quarantine_cleanup_performed":
                    False,

                "quarantine_cleanup_verified":
                    True,
            }
        )

    quarantine_path = Path(
        quarantine_path_value
    )

    cleanup_performed = False

    if quarantine_path.exists():

        if not quarantine_path.is_file():
            raise LifecycleRepairExecutorEngineError(
                "Quarantine rollback artifact is not a file."
            )

        quarantine_path.unlink()

        cleanup_performed = True

    cleanup_verified = (
        not quarantine_path.exists()
    )

    return _freeze(
        {
            "quarantine_cleanup_required":
                True,

            "quarantine_cleanup_performed":
                cleanup_performed,

            "quarantine_cleanup_verified":
                cleanup_verified,

            "quarantine_path":
                str(
                    quarantine_path
                ),
        }
    )


def _rollback_executed_action_v1(
    *,
    backup_record: Mapping[str, Any],
    mutation_result: Mapping[str, Any],
) -> Mapping[str, Any]:

    quarantine_cleanup = (
        _remove_quarantine_artifact_for_rollback_v1(
            mutation_result=mutation_result,
        )
    )

    backup_rollback = (
        _restore_file_backup_v1(
            backup_record=backup_record,
        )
    )

    rollback_verified = all(
        (
            quarantine_cleanup[
                "quarantine_cleanup_verified"
            ]
            is True,

            backup_rollback[
                "rollback_verified"
            ]
            is True,
        )
    )

    return _freeze(
        {
            "rollback_performed":
                True,

            "rollback_verified":
                rollback_verified,

            "quarantine_cleanup":
                quarantine_cleanup,

            "backup_rollback":
                backup_rollback,
        }
    )


def _build_executor_action_result_v1(
    *,
    repair_action_id: str,
    source_finding_id: str,
    repair_action_type: str,
    target_store: str,
    target_path: str | None,
    execution_mode: str,
    execution_status: str,
    execution_authorized: bool,
    mutation_attempted: bool,
    mutation_performed: bool,
    backup_record: Mapping[str, Any] | None = None,
    mutation_result: Mapping[str, Any] | None = None,
    rollback_result: Mapping[str, Any] | None = None,
    failure_reason: str | None = None,
) -> Mapping[str, Any]:

    result = {
        "schema":
            BODY_STORE_LIFECYCLE_REPAIR_ACTION_RESULT_SCHEMA,

        "executor_engine_schema":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_SCHEMA,

        "executor_engine_version":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_VERSION,

        "repair_action_id":
            repair_action_id,

        "source_finding_id":
            source_finding_id,

        "repair_action_type":
            repair_action_type,

        "target_store":
            target_store,

        "target_path":
            target_path,

        "execution_mode":
            execution_mode,

        "execution_status":
            execution_status,

        "execution_authorized":
            execution_authorized,

        "mutation_attempted":
            mutation_attempted,

        "mutation_performed":
            mutation_performed,

        "backup_created":
            (
                backup_record is not None
                and backup_record.get(
                    "backup_created"
                )
                is True
            ),

        "backup_record":
            backup_record,

        "mutation_result":
            mutation_result,

        "rollback_required":
            rollback_result is not None,

        "rollback_performed":
            (
                rollback_result is not None
                and rollback_result.get(
                    "rollback_performed"
                )
                is True
            ),

        "rollback_verified":
            (
                rollback_result.get(
                    "rollback_verified"
                )
                if rollback_result is not None
                else None
            ),

        "rollback_result":
            rollback_result,

        "failure_reason":
            failure_reason,

        "repair_executed":
            (
                mutation_performed
                and rollback_result is None
            ),
    }

    result[
        "action_result_checksum"
    ] = (
        calculate_lifecycle_repair_executor_engine_checksum_v1(
            payload=result,
        )
    )

    return _freeze(
        result
    )


def execute_lifecycle_repair_plan_v1(
    *,
    project_root: str | Path,
    repair_plan: Mapping[str, Any],
    planner_certification: Mapping[str, Any],
    authorization: Mapping[str, Any],
    execution_request: Mapping[str, Any],
    findings: tuple[Mapping[str, Any], ...]
    | list[Mapping[str, Any]],
) -> Mapping[str, Any]:

    request = _require_mapping(
        execution_request,
        field_name="execution_request",
    )

    context = (
        validate_lifecycle_repair_execution_context_v1(
            repair_plan=repair_plan,
            planner_certification=planner_certification,
            authorization=authorization,
            execution_request=request,
            findings=findings,
        )
    )

    if (
        context[
            "context_valid"
        ]
        is not True
    ):
        raise LifecycleRepairExecutorEngineError(
            "Lifecycle Repair Executor context failed "
            "one or more mandatory safety gates."
        )

    preflight = (
        prepare_lifecycle_repair_execution_v1(
            project_root=project_root,
            repair_plan=repair_plan,
            execution_request=request,
            findings=findings,
        )
    )

    if not _validate_preflight_checksum_v1(
        preflight=preflight,
    ):
        raise LifecycleRepairExecutorEngineError(
            "Executor preflight checksum validation failed."
        )

    if (
        preflight[
            "all_preflight_checks_passed"
        ]
        is not True
    ):
        raise LifecycleRepairExecutorEngineError(
            "One or more requested repair actions "
            "failed Executor preflight."
        )

    execution_mode = _require_string(
        request.get(
            "execution_mode"
        ),
        field_name="execution_request.execution_mode",
    ).upper()

    workspace_id = _require_string(
        request.get(
            "workspace_id"
        ),
        field_name="execution_request.workspace_id",
    )

    execution_request_id = _require_string(
        request.get(
            "execution_request_id"
        ),
        field_name=(
            "execution_request.execution_request_id"
        ),
    )

    prepared_actions = tuple(
        preflight[
            "prepared_actions"
        ]
    )

    if execution_mode == "DRY_RUN":

        if (
            context[
                "dry_run_eligible"
            ]
            is not True
        ):
            raise LifecycleRepairExecutorEngineError(
                "Execution context is not eligible "
                "for DRY_RUN."
            )

        dry_run_results: list[
            Mapping[str, Any]
        ] = []

        for prepared_action in prepared_actions:

            intent = prepared_action[
                "mutation_intent"
            ]

            dry_run_results.append(
                _build_dry_run_action_result_v1(
                    repair_action={
                        "repair_action_id":
                            prepared_action[
                                "repair_action_id"
                            ],

                        "repair_action_type":
                            prepared_action[
                                "repair_action_type"
                            ],
                    },
                    source_finding={
                        "finding_id":
                            prepared_action[
                                "source_finding_id"
                            ],
                    },
                    target_store=prepared_action[
                        "target_store"
                    ],
                    target_path=intent[
                        "target_path"
                    ],
                )
            )

        result = {
            "schema":
                BODY_STORE_LIFECYCLE_REPAIR_EXECUTION_RESULT_SCHEMA,

            "executor_engine_schema":
                BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_SCHEMA,

            "executor_engine_version":
                BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_VERSION,

            "executor_contract_version":
                BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_VERSION,

            "execution_request_id":
                execution_request_id,

            "workspace_id":
                workspace_id,

            "repair_plan_id":
                request[
                    "repair_plan_id"
                ],

            "execution_mode":
                "DRY_RUN",

            "context_valid":
                True,

            "preflight_valid":
                True,

            "execution_authorized":
                False,

            "execution_started":
                True,

            "execution_completed":
                True,

            "execution_succeeded":
                True,

            "requested_action_count":
                len(
                    prepared_actions
                ),

            "executed_action_count":
                0,

            "dry_run_validated_action_count":
                len(
                    dry_run_results
                ),

            "failed_action_count":
                0,

            "rolled_back_action_count":
                0,

            "action_results":
                tuple(
                    dry_run_results
                ),

            "repair_executed":
                False,

            "mutation_performed":
                False,

            "rollback_required":
                False,

            "rollback_performed":
                False,

            "rollback_verified":
                None,

            "runtime_job_created":
                False,

            "queue_job_created":
                False,
        }

        result[
            "execution_result_checksum"
        ] = (
            calculate_lifecycle_repair_executor_engine_checksum_v1(
                payload=result,
            )
        )

        return _freeze(
            result
        )

    if execution_mode != "AUTHORIZED_APPLY":
        raise LifecycleRepairExecutorEngineError(
            "Unsupported execution mode: "
            + execution_mode
        )

    if (
        context[
            "authorized_apply_eligible"
        ]
        is not True
    ):
        raise LifecycleRepairExecutorEngineError(
            "Execution context is not eligible "
            "for AUTHORIZED_APPLY."
        )

    backup_root = (
        _resolve_executor_backup_root_v1(
            project_root=project_root,
            workspace_id=workspace_id,
            execution_request_id=execution_request_id,
        )
    )

    action_results: list[
        Mapping[str, Any]
    ] = []

    executed_stack: list[
        dict[str, Any]
    ] = []

    failed_action_id: str | None = None
    failure_reason: str | None = None

    try:

        for prepared_action in prepared_actions:

            action_id = _require_string(
                prepared_action.get(
                    "repair_action_id"
                ),
                field_name=(
                    "prepared_action.repair_action_id"
                ),
            )

            source_finding_id = _require_string(
                prepared_action.get(
                    "source_finding_id"
                ),
                field_name=(
                    "prepared_action.source_finding_id"
                ),
            )

            action_type = _require_string(
                prepared_action.get(
                    "repair_action_type"
                ),
                field_name=(
                    "prepared_action.repair_action_type"
                ),
            ).upper()

            target_store = _require_string(
                prepared_action.get(
                    "target_store"
                ),
                field_name=(
                    "prepared_action.target_store"
                ),
            ).upper()

            mutation_intent = (
                prepared_action[
                    "mutation_intent"
                ]
            )

            if not _validate_mutation_intent_checksum_v1(
                mutation_intent=mutation_intent,
            ):
                raise LifecycleRepairExecutorEngineError(
                    "Mutation intent changed after preflight."
                )

            unchanged_check = (
                _verify_target_unchanged_since_preflight_v1(
                    mutation_intent=mutation_intent,
                )
            )

            if (
                unchanged_check[
                    "target_unchanged"
                ]
                is not True
            ):
                raise LifecycleRepairExecutorEngineError(
                    "Repair target changed after preflight; "
                    "execution aborted."
                )

            target_path = Path(
                _require_string(
                    mutation_intent.get(
                        "target_path"
                    ),
                    field_name=(
                        "mutation_intent.target_path"
                    ),
                )
            )

            workspace_store_root = Path(
                _require_string(
                    mutation_intent.get(
                        "workspace_store_root"
                    ),
                    field_name=(
                        "mutation_intent.workspace_store_root"
                    ),
                )
            )

            target_path = _assert_path_within_root_v1(
                candidate_path=target_path,
                allowed_root=workspace_store_root,
            )

            action_backup_root = (
                backup_root
                / target_store
            )

            action_backup_root = (
                _assert_path_within_root_v1(
                    candidate_path=action_backup_root,
                    allowed_root=backup_root,
                )
            )

            backup_record = (
                _create_file_backup_v1(
                    source_path=target_path,
                    backup_root=action_backup_root,
                    workspace_store_root=(
                        workspace_store_root
                    ),
                )
            )

            transaction_entry = {
                "repair_action_id":
                    action_id,

                "source_finding_id":
                    source_finding_id,

                "repair_action_type":
                    action_type,

                "target_store":
                    target_store,

                "target_path":
                    str(
                        target_path
                    ),

                "backup_record":
                    backup_record,

                "mutation_result":
                    {},
            }

            # Register the current action BEFORE mutation.
            # If mutation fails midway, the outer transaction
            # rollback will restore this action as well.
            executed_stack.append(
                transaction_entry
            )

            mutation_result = (
                _dispatch_authorized_mutation_v2(
                    project_root=project_root,
                    workspace_id=workspace_id,
                    mutation_intent=mutation_intent,
                )
            )

            transaction_entry[
                "mutation_result"
            ] = mutation_result

            mutation_performed = (
                mutation_result.get(
                    "mutation_performed"
                )
                is True
            )

            execution_status = (
                "EXECUTED"
                if mutation_performed
                else "SKIPPED"
            )

            action_result = (
                _build_executor_action_result_v1(
                    repair_action_id=action_id,
                    source_finding_id=source_finding_id,
                    repair_action_type=action_type,
                    target_store=target_store,
                    target_path=str(
                        target_path
                    ),
                    execution_mode="AUTHORIZED_APPLY",
                    execution_status=execution_status,
                    execution_authorized=True,
                    mutation_attempted=True,
                    mutation_performed=mutation_performed,
                    backup_record=backup_record,
                    mutation_result=mutation_result,
                )
            )

            action_results.append(
                action_result
            )

            # A no-op action does not belong in the rollback
            # transaction stack because it changed nothing.
            if not mutation_performed:
                executed_stack.pop()

    except Exception as exc:

        failure_reason = str(
            exc
        )

        if "action_id" in locals():
            failed_action_id = action_id

        rollback_results: list[
            Mapping[str, Any]
        ] = []

        rollback_failures: list[str] = []

        for executed in reversed(
            executed_stack
        ):

            try:
                rollback_result = (
                    _rollback_executed_action_v1(
                        backup_record=executed[
                            "backup_record"
                        ],
                        mutation_result=executed[
                            "mutation_result"
                        ],
                    )
                )

                rollback_results.append(
                    _freeze(
                        {
                            "repair_action_id":
                                executed[
                                    "repair_action_id"
                                ],

                            "rollback_result":
                                rollback_result,
                        }
                    )
                )

                if (
                    rollback_result[
                        "rollback_verified"
                    ]
                    is not True
                ):
                    rollback_failures.append(
                        executed[
                            "repair_action_id"
                        ]
                    )

            except Exception as rollback_exc:
                rollback_failures.append(
                    executed[
                        "repair_action_id"
                    ]
                    + ": "
                    + str(
                        rollback_exc
                    )
                )

        rollback_verified = (
            not rollback_failures
            and len(
                rollback_results
            )
            == len(
                executed_stack
            )
        )

        failed_result = {
            "schema":
                BODY_STORE_LIFECYCLE_REPAIR_EXECUTION_RESULT_SCHEMA,

            "executor_engine_schema":
                BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_SCHEMA,

            "executor_engine_version":
                BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_VERSION,

            "execution_request_id":
                execution_request_id,

            "workspace_id":
                workspace_id,

            "repair_plan_id":
                request[
                    "repair_plan_id"
                ],

            "execution_mode":
                "AUTHORIZED_APPLY",

            "context_valid":
                True,

            "preflight_valid":
                True,

            "execution_authorized":
                True,

            "execution_started":
                True,

            "execution_completed":
                True,

            "execution_succeeded":
                False,

            "failed_action_id":
                failed_action_id,

            "failure_reason":
                failure_reason,

            "requested_action_count":
                len(
                    prepared_actions
                ),

            "executed_action_count":
                len(
                    executed_stack
                ),

            "failed_action_count":
                1,

            "rolled_back_action_count":
                len(
                    rollback_results
                ),

            "action_results":
                tuple(
                    action_results
                ),

            "rollback_results":
                tuple(
                    rollback_results
                ),

            "rollback_failures":
                tuple(
                    rollback_failures
                ),

            "repair_executed":
                False,

            "mutation_performed":
                not rollback_verified,

            "rollback_required":
                bool(
                    executed_stack
                ),

            "rollback_performed":
                bool(
                    rollback_results
                ),

            "rollback_verified":
                rollback_verified,

            "runtime_job_created":
                False,

            "queue_job_created":
                False,
        }

        failed_result[
            "execution_result_checksum"
        ] = (
            calculate_lifecycle_repair_executor_engine_checksum_v1(
                payload=failed_result,
            )
        )

        return _freeze(
            failed_result
        )

    committed_mutations = sum(
        1
        for action_result
        in action_results
        if action_result[
            "mutation_performed"
        ]
        is True
    )

    successful_result = {
        "schema":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTION_RESULT_SCHEMA,

        "executor_engine_schema":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_SCHEMA,

        "executor_engine_version":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_VERSION,

        "execution_request_id":
            execution_request_id,

        "workspace_id":
            workspace_id,

        "repair_plan_id":
            request[
                "repair_plan_id"
            ],

        "execution_mode":
            "AUTHORIZED_APPLY",

        "context_valid":
            True,

        "preflight_valid":
            True,

        "execution_authorized":
            True,

        "execution_started":
            True,

        "execution_completed":
            True,

        "execution_succeeded":
            True,

        "requested_action_count":
            len(
                prepared_actions
            ),

        "executed_action_count":
            len(
                action_results
            ),

        "committed_mutation_count":
            committed_mutations,

        "failed_action_count":
            0,

        "rolled_back_action_count":
            0,

        "action_results":
            tuple(
                action_results
            ),

        "repair_executed":
            committed_mutations
            > 0,

        "mutation_performed":
            committed_mutations
            > 0,

        "rollback_required":
            False,

        "rollback_performed":
            False,

        "rollback_verified":
            None,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }

    successful_result[
        "execution_result_checksum"
    ] = (
        calculate_lifecycle_repair_executor_engine_checksum_v1(
            payload=successful_result,
        )
    )

    return _freeze(
        successful_result
    )
