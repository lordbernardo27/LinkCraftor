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

BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_VERSION = (
    "1.0"
)


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


EXECUTOR_STORE_DIRECTORY_NAMES = (
    MappingProxyType(
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
)


EXECUTOR_EXECUTION_MODES = (
    "DRY_RUN",
    "AUTHORIZED_APPLY",
)


EXECUTOR_MUTATION_POLICY = (
    MappingProxyType(
        {
            "DRY_RUN":
                MappingProxyType(
                    {
                        "may_mutate":
                            False,

                        "requires_authorization":
                            False,

                        "requires_certified_plan":
                            True,

                        "requires_preflight":
                            True,
                    }
                ),

            "AUTHORIZED_APPLY":
                MappingProxyType(
                    {
                        "may_mutate":
                            True,

                        "requires_authorization":
                            True,

                        "requires_certified_plan":
                            True,

                        "requires_preflight":
                            True,
                    }
                ),
        }
    )
)


class LifecycleRepairExecutorEngineError(
    ValueError
):
    """
    Raised when Lifecycle Repair Executor Engine
    validation or safety enforcement fails.
    """


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


def _require_boolean(
    value: Any,
    *,
    field_name: str,
) -> bool:

    if not isinstance(
        value,
        bool,
    ):
        raise LifecycleRepairExecutorEngineError(
            field_name
            + " must be a boolean."
        )

    return value


def calculate_lifecycle_repair_executor_engine_checksum_v1(
    *,
    payload: Mapping[str, Any],
) -> str:

    item = _require_mapping(
        payload,
        field_name="payload",
    )

    serialized = json.dumps(
        _json_ready(
            item
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


def _resolve_project_root_v1(
    *,
    project_root: str | Path,
) -> Path:

    if isinstance(
        project_root,
        str,
    ):
        normalized = project_root.strip()

        if not normalized:
            raise LifecycleRepairExecutorEngineError(
                "project_root must not be empty."
            )

        root = Path(
            normalized
        )

    elif isinstance(
        project_root,
        Path,
    ):
        root = project_root

    else:
        raise LifecycleRepairExecutorEngineError(
            "project_root must be a string or Path."
        )

    return root.resolve()


def _resolve_data_root_v1(
    *,
    project_root: str | Path,
) -> Path:

    root = _resolve_project_root_v1(
        project_root=project_root,
    )

    return (
        root
        / "backend"
        / "server"
        / "data"
    ).resolve()


def _resolve_workspace_store_root_v1(
    *,
    project_root: str | Path,
    workspace_id: str,
    target_store: str,
) -> Path:

    normalized_workspace_id = (
        _require_string(
            workspace_id,
            field_name="workspace_id",
        )
    )

    normalized_target_store = (
        _require_string(
            target_store,
            field_name="target_store",
        ).upper()
    )

    if (
        normalized_target_store
        not in SUPPORTED_TARGET_STORES
    ):
        raise LifecycleRepairExecutorEngineError(
            "Unsupported target_store: "
            + normalized_target_store
        )

    directory_name = (
        EXECUTOR_STORE_DIRECTORY_NAMES[
            normalized_target_store
        ]
    )

    data_root = _resolve_data_root_v1(
        project_root=project_root,
    )

    return (
        data_root
        / directory_name
        / normalized_workspace_id
    ).resolve()


def _normalize_execution_mode_v1(
    value: Any,
) -> str:

    mode = _require_string(
        value,
        field_name="execution_mode",
    ).upper()

    if mode not in EXECUTOR_EXECUTION_MODES:
        raise LifecycleRepairExecutorEngineError(
            "Unsupported execution_mode: "
            + mode
        )

    return mode


def _assert_supported_executor_action_type_v1(
    action_type: Any,
) -> str:

    normalized = _require_string(
        action_type,
        field_name="repair_action_type",
    ).upper()

    if (
        normalized
        in NON_EXECUTABLE_PLANNER_ACTION_TYPES
    ):
        raise LifecycleRepairExecutorEngineError(
            "Planner action is explicitly non-executable: "
            + normalized
        )

    if (
        normalized
        in PROHIBITED_DIRECT_EXECUTION_ACTION_TYPES
    ):
        raise LifecycleRepairExecutorEngineError(
            "Repair action is prohibited from direct execution: "
            + normalized
        )

    if (
        normalized
        not in SUPPORTED_EXECUTOR_ACTION_TYPES
    ):
        raise LifecycleRepairExecutorEngineError(
            "Unsupported Executor repair action: "
            + normalized
        )

    return normalized


def _normalize_action_ids_v1(
    value: Any,
    *,
    field_name: str,
) -> tuple[str, ...]:

    if not isinstance(
        value,
        (
            tuple,
            list,
        ),
    ):
        raise LifecycleRepairExecutorEngineError(
            field_name
            + " must be a tuple or list."
        )

    normalized: list[str] = []

    for raw_action_id in value:

        action_id = _require_string(
            raw_action_id,
            field_name=(
                field_name
                + " item"
            ),
        )

        normalized.append(
            action_id
        )

    if not normalized:
        raise LifecycleRepairExecutorEngineError(
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
        raise LifecycleRepairExecutorEngineError(
            field_name
            + " must not contain duplicate action IDs."
        )

    return tuple(
        normalized
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

    if not findings:
        raise LifecycleRepairExecutorEngineError(
            "findings must contain at least one finding."
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

        finding_type = _require_string(
            finding.get(
                "finding_type"
            ),
            field_name="finding.finding_type",
        ).upper()

        severity = _require_string(
            finding.get(
                "severity"
            ),
            field_name="finding.severity",
        ).upper()

        workspace_id = _require_string(
            finding.get(
                "workspace_id"
            ),
            field_name="finding.workspace_id",
        )

        if finding_id in indexed:
            raise LifecycleRepairExecutorEngineError(
                "Duplicate finding_id supplied to Executor: "
                + finding_id
            )

        normalized_finding = dict(
            finding
        )

        normalized_finding[
            "finding_id"
        ] = finding_id

        normalized_finding[
            "finding_type"
        ] = finding_type

        normalized_finding[
            "severity"
        ] = severity

        normalized_finding[
            "workspace_id"
        ] = workspace_id

        indexed[
            finding_id
        ] = _freeze(
            normalized_finding
        )

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

    if not repair_actions:
        raise LifecycleRepairExecutorEngineError(
            "repair_plan.repair_actions must "
            "contain at least one repair action."
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

        _require_string(
            action.get(
                "workspace_id"
            ),
            field_name=(
                "repair_action.workspace_id"
            ),
        )

        _require_string(
            action.get(
                "source_finding_id"
            ),
            field_name=(
                "repair_action.source_finding_id"
            ),
        )

        _require_string(
            action.get(
                "source_finding_type"
            ),
            field_name=(
                "repair_action.source_finding_type"
            ),
        )

        _require_string(
            action.get(
                "source_finding_severity"
            ),
            field_name=(
                "repair_action.source_finding_severity"
            ),
        )

        _require_string(
            action.get(
                "source_finding_checksum"
            ),
            field_name=(
                "repair_action.source_finding_checksum"
            ),
        )

        _require_string(
            action.get(
                "repair_action_type"
            ),
            field_name=(
                "repair_action.repair_action_type"
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

    normalized_workspace_id = (
        _require_string(
            workspace_id,
            field_name="workspace_id",
        )
    )

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
        field_name=(
            "source_finding.finding_id"
        ),
    )

    finding_type = _require_string(
        finding.get(
            "finding_type"
        ),
        field_name=(
            "source_finding.finding_type"
        ),
    ).upper()

    severity = _require_string(
        finding.get(
            "severity"
        ),
        field_name=(
            "source_finding.severity"
        ),
    ).upper()

    finding_workspace_id = (
        _require_string(
            finding.get(
                "workspace_id"
            ),
            field_name=(
                "source_finding.workspace_id"
            ),
        )
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
            normalized_workspace_id,

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
        == normalized_workspace_id
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

            "source_finding_type":
                finding_type,

            "source_finding_severity":
                severity,

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


    # ---------------------------------------------------------
    # 1. Independent upstream validation
    # ---------------------------------------------------------

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


    # ---------------------------------------------------------
    # 2. Workspace identity
    # ---------------------------------------------------------

    workspace_id = _require_string(
        request.get(
            "workspace_id"
        ),
        field_name=(
            "execution_request.workspace_id"
        ),
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


    # ---------------------------------------------------------
    # 3. Repair Plan identity
    # ---------------------------------------------------------

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


    # ---------------------------------------------------------
    # 4. Planner Certification identity
    # ---------------------------------------------------------

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


    # ---------------------------------------------------------
    # 5. Execution Authorization identity
    # ---------------------------------------------------------

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


    # ---------------------------------------------------------
    # 6. Requested actions
    # ---------------------------------------------------------

    requested_action_ids = (
        _normalize_action_ids_v1(
            request.get(
                "requested_action_ids",
                (),
            ),
            field_name=(
                "execution_request.requested_action_ids"
            ),
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


    # ---------------------------------------------------------
    # 7. Repair Plan action indexing
    # ---------------------------------------------------------

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


    # ---------------------------------------------------------
    # 8. Source findings
    # ---------------------------------------------------------

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


    # ---------------------------------------------------------
    # 9. Independently verify each requested action
    # ---------------------------------------------------------

    for action_id in requested_action_ids:

        action = indexed_actions.get(
            action_id
        )

        if action is None:

            source_finding_evidence_match = False

            action_identity_match = False

            no_non_executable_action = False

            no_prohibited_action = False

            continue


        source_finding_id = (
            action.get(
                "source_finding_id"
            )
        )


        source_finding = (
            indexed_findings.get(
                source_finding_id
            )
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


    # ---------------------------------------------------------
    # 10. Mandatory safety-gate matrix
    # ---------------------------------------------------------

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


    # ---------------------------------------------------------
    # 11. Mode eligibility
    # ---------------------------------------------------------

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


    # ---------------------------------------------------------
    # 12. Read-only context result
    # ---------------------------------------------------------

    result = {
        "schema":
            "body_store_lifecycle_repair_execution_context.v1",

        "executor_engine_schema":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_SCHEMA,

        "executor_engine_version":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_VERSION,

        "executor_contract_version":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_VERSION,

        "context_valid":
            all_safety_gates_passed,

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

        "authorization_id":
            authorization_item.get(
                "authorization_id"
            ),

        "planner_certification_id":
            planner_certificate.get(
                "certification_id"
            ),

        "execution_mode":
            execution_mode,

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

        "requested_action_ids":
            requested_action_ids,

        "requested_action_count":
            len(
                requested_action_ids
            ),

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
    }


    result[
        "execution_context_checksum"
    ] = (
        calculate_lifecycle_repair_executor_engine_checksum_v1(
            payload=result,
        )
    )


    return _freeze(
        result
    )
def _assert_path_within_root_v1(
    *,
    candidate_path: Path,
    allowed_root: Path,
) -> Path:

    if not isinstance(
        candidate_path,
        Path,
    ):
        raise LifecycleRepairExecutorEngineError(
            "candidate_path must be a Path."
        )

    if not isinstance(
        allowed_root,
        Path,
    ):
        raise LifecycleRepairExecutorEngineError(
            "allowed_root must be a Path."
        )

    resolved_candidate = (
        candidate_path.resolve(
            strict=False
        )
    )

    resolved_root = (
        allowed_root.resolve(
            strict=False
        )
    )

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

    if not isinstance(
        workspace_store_root,
        Path,
    ):
        raise LifecycleRepairExecutorEngineError(
            "workspace_store_root must be a Path."
        )

    normalized_relative_path = (
        _require_string(
            relative_path,
            field_name="relative_path",
        )
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

    safe_candidate = (
        _assert_path_within_root_v1(
            candidate_path=candidate,
            allowed_root=workspace_store_root,
        )
    )

    resolved_workspace_root = (
        workspace_store_root.resolve(
            strict=False
        )
    )

    if safe_candidate == resolved_workspace_root:
        raise LifecycleRepairExecutorEngineError(
            "Executor record path must identify "
            "a record beneath the workspace root."
        )

    return safe_candidate


def _resolve_quarantine_root_v1(
    *,
    project_root: str | Path,
    workspace_id: str,
) -> Path:

    normalized_workspace_id = (
        _require_string(
            workspace_id,
            field_name="workspace_id",
        )
    )

    data_root = _resolve_data_root_v1(
        project_root=project_root,
    )

    quarantine_base = (
        data_root
        / "universal_article_body_store_repair_quarantine"
    ).resolve(
        strict=False
    )

    quarantine_root = (
        quarantine_base
        / normalized_workspace_id
    )

    return _assert_path_within_root_v1(
        candidate_path=quarantine_root,
        allowed_root=quarantine_base,
    )


def _resolve_executor_backup_root_v1(
    *,
    project_root: str | Path,
    workspace_id: str,
    execution_request_id: str,
) -> Path:

    normalized_workspace_id = (
        _require_string(
            workspace_id,
            field_name="workspace_id",
        )
    )

    normalized_execution_request_id = (
        _require_string(
            execution_request_id,
            field_name="execution_request_id",
        )
    )

    data_root = _resolve_data_root_v1(
        project_root=project_root,
    )

    backup_base = (
        data_root
        / "universal_article_body_store_repair_backups"
    ).resolve(
        strict=False
    )

    workspace_backup_root = (
        backup_base
        / normalized_workspace_id
    )

    safe_workspace_backup_root = (
        _assert_path_within_root_v1(
            candidate_path=workspace_backup_root,
            allowed_root=backup_base,
        )
    )

    execution_backup_root = (
        safe_workspace_backup_root
        / normalized_execution_request_id
    )

    return _assert_path_within_root_v1(
        candidate_path=execution_backup_root,
        allowed_root=safe_workspace_backup_root,
    )


def _calculate_file_checksum_v1(
    *,
    path: Path,
) -> str:

    if not isinstance(
        path,
        Path,
    ):
        raise LifecycleRepairExecutorEngineError(
            "Checksum target must be a Path."
        )

    if not path.exists():
        return "ABSENT"

    if not path.is_file():
        raise LifecycleRepairExecutorEngineError(
            "Checksum target is not a file: "
            + str(
                path
            )
        )

    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as handle:

        while True:

            chunk = handle.read(
                1024 * 1024
            )

            if not chunk:
                break

            digest.update(
                chunk
            )

    return digest.hexdigest()


def _create_file_backup_v1(
    *,
    source_path: Path,
    backup_root: Path,
    workspace_store_root: Path,
) -> Mapping[str, Any]:

    safe_source_path = (
        _assert_path_within_root_v1(
            candidate_path=source_path,
            allowed_root=workspace_store_root,
        )
    )

    safe_backup_root = (
        backup_root.resolve(
            strict=False
        )
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

                "backup_verified":
                    True,
            }
        )

    if not safe_source_path.is_file():
        raise LifecycleRepairExecutorEngineError(
            "Repair target is not a file: "
            + str(
                safe_source_path
            )
        )

    resolved_workspace_root = (
        workspace_store_root.resolve(
            strict=False
        )
    )

    relative_path = (
        safe_source_path.relative_to(
            resolved_workspace_root
        )
    )

    backup_path = (
        safe_backup_root
        / relative_path
    )

    safe_backup_path = (
        _assert_path_within_root_v1(
            candidate_path=backup_path,
            allowed_root=safe_backup_root,
        )
    )

    if safe_backup_path.exists():
        raise LifecycleRepairExecutorEngineError(
            "Executor backup already exists for "
            "this repair target: "
            + str(
                safe_backup_path
            )
        )

    source_checksum = (
        _calculate_file_checksum_v1(
            path=safe_source_path,
        )
    )

    safe_backup_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        safe_source_path,
        safe_backup_path,
    )

    backup_checksum = (
        _calculate_file_checksum_v1(
            path=safe_backup_path,
        )
    )

    backup_verified = (
        source_checksum
        == backup_checksum
    )

    if not backup_verified:

        try:
            safe_backup_path.unlink(
                missing_ok=True
            )

        except Exception:
            pass

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

            "backup_verified":
                True,
        }
    )


def _restore_file_backup_v1(
    *,
    backup_record: Mapping[str, Any],
    backup_root: Path,
    workspace_store_root: Path,
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
            field_name=(
                "backup_record.source_path"
            ),
        )
    )

    safe_source_path = (
        _assert_path_within_root_v1(
            candidate_path=source_path,
            allowed_root=workspace_store_root,
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


    # ---------------------------------------------------------
    # Target existed before repair:
    # restore the certified backup.
    # ---------------------------------------------------------

    if source_existed:

        backup_path_value = (
            record.get(
                "backup_path"
            )
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

        safe_backup_path = (
            _assert_path_within_root_v1(
                candidate_path=backup_path,
                allowed_root=backup_root,
            )
        )

        if not safe_backup_path.exists():
            raise LifecycleRepairExecutorEngineError(
                "Rollback backup file does not exist: "
                + str(
                    safe_backup_path
                )
            )

        if not safe_backup_path.is_file():
            raise LifecycleRepairExecutorEngineError(
                "Rollback backup path is not a file."
            )

        expected_checksum = (
            _require_string(
                record.get(
                    "source_checksum_before"
                ),
                field_name=(
                    "backup_record."
                    "source_checksum_before"
                ),
            )
        )

        recorded_backup_checksum = (
            _require_string(
                record.get(
                    "backup_checksum"
                ),
                field_name=(
                    "backup_record.backup_checksum"
                ),
            )
        )

        actual_backup_checksum = (
            _calculate_file_checksum_v1(
                path=safe_backup_path,
            )
        )

        if (
            actual_backup_checksum
            != recorded_backup_checksum
        ):
            raise LifecycleRepairExecutorEngineError(
                "Rollback backup checksum validation failed."
            )

        if (
            actual_backup_checksum
            != expected_checksum
        ):
            raise LifecycleRepairExecutorEngineError(
                "Rollback backup does not match "
                "the original pre-repair checksum."
            )

        safe_source_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        restore_temp_path = (
            safe_source_path.with_name(
                safe_source_path.name
                + ".repair_restore_tmp"
            )
        )

        safe_restore_temp_path = (
            _assert_path_within_root_v1(
                candidate_path=restore_temp_path,
                allowed_root=workspace_store_root,
            )
        )

        if safe_restore_temp_path.exists():
            raise LifecycleRepairExecutorEngineError(
                "Rollback temporary path already exists: "
                + str(
                    safe_restore_temp_path
                )
            )

        try:
            shutil.copy2(
                safe_backup_path,
                safe_restore_temp_path,
            )

            temporary_checksum = (
                _calculate_file_checksum_v1(
                    path=safe_restore_temp_path,
                )
            )

            if (
                temporary_checksum
                != expected_checksum
            ):
                raise LifecycleRepairExecutorEngineError(
                    "Rollback temporary file checksum mismatch."
                )

            safe_restore_temp_path.replace(
                safe_source_path
            )

        finally:

            if safe_restore_temp_path.exists():

                try:
                    safe_restore_temp_path.unlink()

                except Exception:
                    pass

        restored_checksum = (
            _calculate_file_checksum_v1(
                path=safe_source_path,
            )
        )

        rollback_verified = (
            restored_checksum
            == expected_checksum
        )


    # ---------------------------------------------------------
    # Target did not exist before repair:
    # rollback means removing the newly created target.
    # ---------------------------------------------------------

    else:

        if safe_source_path.exists():

            if not safe_source_path.is_file():
                raise LifecycleRepairExecutorEngineError(
                    "Rollback target unexpectedly became "
                    "a non-file path."
                )

            safe_source_path.unlink()

        restored_checksum = "ABSENT"

        rollback_verified = (
            not safe_source_path.exists()
        )


    return _freeze(
        {
            "source_path":
                str(
                    safe_source_path
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

    repair_action_id = (
        _require_string(
            action.get(
                "repair_action_id"
            ),
            field_name=(
                "repair_action.repair_action_id"
            ),
        )
    )

    source_finding_id = (
        _require_string(
            finding.get(
                "finding_id"
            ),
            field_name=(
                "source_finding.finding_id"
            ),
        )
    )

    repair_action_type = (
        _assert_supported_executor_action_type_v1(
            action.get(
                "repair_action_type"
            )
        )
    )

    normalized_target_store = (
        _require_string(
            target_store,
            field_name="target_store",
        ).upper()
    )

    if (
        normalized_target_store
        not in SUPPORTED_TARGET_STORES
    ):
        raise LifecycleRepairExecutorEngineError(
            "Unsupported dry-run target store: "
            + normalized_target_store
        )

    normalized_target_path: str | None = None

    if target_path is not None:

        normalized_target_path = (
            _require_string(
                target_path,
                field_name="target_path",
            )
        )

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
            normalized_target_store,

        "target_path":
            normalized_target_path,

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

        "rollback_verified":
            None,

        "repair_executed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
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


DYNAMIC_TARGET_STORE_ACTION_TYPES = (
    "QUARANTINE_INVALID_RECORD",
    "REPAIR_REFERENCE_METADATA",
)


METADATA_ONLY_REPAIR_ACTION_TYPES = (
    "REBUILD_LIFECYCLE_RECORD",
    "REBUILD_ARCHIVE_METADATA",
    "REBUILD_TOMBSTONE_INDEX",
    "REPAIR_REFERENCE_METADATA",
    "RESOLVE_DUPLICATE_IDENTITY",
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


TARGET_STORE_FIELD_NAMES = (
    "target_store",
    "store_name",
    "source_store",
    "record_store",
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


TARGET_STORE_ALIASES = MappingProxyType(
    {
        "LIFECYCLE_STORE":
            "LIFECYCLE",

        "LIFECYCLE":
            "LIFECYCLE",

        "ARCHIVE_STORE":
            "ARCHIVE",

        "ARCHIVE":
            "ARCHIVE",

        "TOMBSTONE_STORE":
            "TOMBSTONE",

        "TOMBSTONE":
            "TOMBSTONE",

        "BODY":
            "BODY_STORE",

        "BODY_STORE":
            "BODY_STORE",

        "ARTICLE_BODY_STORE":
            "BODY_STORE",

        "UNIVERSAL_ARTICLE_BODY_STORE":
            "BODY_STORE",
    }
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

        for field_name in (
            NESTED_EVIDENCE_FIELD_NAMES
        ):

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

            elif isinstance(
                nested,
                (
                    tuple,
                    list,
                ),
            ):

                for nested_item in nested:

                    if isinstance(
                        nested_item,
                        Mapping,
                    ):
                        visit(
                            nested_item
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

    if not isinstance(
        field_names,
        tuple,
    ):
        raise LifecycleRepairExecutorEngineError(
            "field_names must be a tuple."
        )

    if not field_names:
        raise LifecycleRepairExecutorEngineError(
            "field_names must not be empty."
        )

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


def _normalize_target_store_evidence_v1(
    value: Any,
) -> str | None:

    if value is None:
        return None

    if not isinstance(
        value,
        str,
    ):
        raise LifecycleRepairExecutorEngineError(
            "Target-store evidence must be a string."
        )

    normalized = value.strip().upper()

    if not normalized:
        raise LifecycleRepairExecutorEngineError(
            "Target-store evidence must not be empty."
        )

    normalized = TARGET_STORE_ALIASES.get(
        normalized,
        normalized,
    )

    if (
        normalized
        not in SUPPORTED_TARGET_STORES
    ):
        raise LifecycleRepairExecutorEngineError(
            "Unsupported target-store evidence: "
            + normalized
        )

    return normalized


def _validate_action_target_store_boundary_v1(
    *,
    repair_action_type: str,
    target_store: str,
) -> None:

    action_type = (
        _assert_supported_executor_action_type_v1(
            repair_action_type
        )
    )

    normalized_target_store = (
        _require_string(
            target_store,
            field_name="target_store",
        ).upper()
    )

    allowed_stores = (
        ACTION_ALLOWED_TARGET_STORES.get(
            action_type
        )
    )

    if allowed_stores is None:
        raise LifecycleRepairExecutorEngineError(
            "Repair action has no authorized "
            "target-store boundary: "
            + action_type
        )

    if (
        normalized_target_store
        not in allowed_stores
    ):
        raise LifecycleRepairExecutorEngineError(
            "Repair action "
            + action_type
            + " is not authorized for target store "
            + normalized_target_store
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

    action_type = (
        _assert_supported_executor_action_type_v1(
            action.get(
                "repair_action_type"
            )
        )
    )

    evidence_store_raw = (
        _find_first_evidence_value_v1(
            source_finding=finding,
            field_names=TARGET_STORE_FIELD_NAMES,
        )
    )

    evidence_store = (
        _normalize_target_store_evidence_v1(
            evidence_store_raw
        )
    )


    # ---------------------------------------------------------
    # Dynamic actions must explicitly identify their store.
    # ---------------------------------------------------------

    if (
        action_type
        in DYNAMIC_TARGET_STORE_ACTION_TYPES
    ):

        if evidence_store is None:
            raise LifecycleRepairExecutorEngineError(
                "Repair action "
                + action_type
                + " requires explicit target-store evidence."
            )

        _validate_action_target_store_boundary_v1(
            repair_action_type=action_type,
            target_store=evidence_store,
        )

        return evidence_store


    # ---------------------------------------------------------
    # Fixed actions have a canonical target store.
    # ---------------------------------------------------------

    canonical_target_store = (
        ACTION_TARGET_STORE.get(
            action_type
        )
    )

    if canonical_target_store is None:
        raise LifecycleRepairExecutorEngineError(
            "Repair action has no target-store mapping: "
            + action_type
        )


    # If evidence also declares a target store, it must agree
    # with the canonical mapping. We do not silently ignore
    # conflicting evidence.
    if (
        evidence_store is not None
        and evidence_store
        != canonical_target_store
    ):
        raise LifecycleRepairExecutorEngineError(
            "Target-store evidence conflicts with "
            "the canonical repair-action store. "
            "Action="
            + action_type
            + ", expected="
            + canonical_target_store
            + ", supplied="
            + evidence_store
        )

    _validate_action_target_store_boundary_v1(
        repair_action_type=action_type,
        target_store=canonical_target_store,
    )

    return canonical_target_store


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

        safe_path = (
            _assert_path_within_root_v1(
                candidate_path=supplied_path,
                allowed_root=workspace_store_root,
            )
        )

        if (
            safe_path
            == workspace_store_root.resolve(
                strict=False
            )
        ):
            raise LifecycleRepairExecutorEngineError(
                "Evidence target path must identify "
                "a record beneath the workspace store."
            )

        return safe_path

    return _resolve_safe_relative_record_path_v1(
        workspace_store_root=workspace_store_root,
        relative_path=normalized,
    )


def _resolve_verified_workspace_store_root_v1(
    *,
    project_root: str | Path,
    workspace_id: str,
    target_store: str,
) -> Path:

    normalized_target_store = (
        _require_string(
            target_store,
            field_name="target_store",
        ).upper()
    )

    if (
        normalized_target_store
        not in SUPPORTED_TARGET_STORES
    ):
        raise LifecycleRepairExecutorEngineError(
            "Unsupported target store: "
            + normalized_target_store
        )

    data_root = _resolve_data_root_v1(
        project_root=project_root,
    )

    store_directory_name = (
        EXECUTOR_STORE_DIRECTORY_NAMES[
            normalized_target_store
        ]
    )

    authorized_store_base = (
        data_root
        / store_directory_name
    ).resolve(
        strict=False
    )

    workspace_store_root = (
        _resolve_workspace_store_root_v1(
            project_root=project_root,
            workspace_id=workspace_id,
            target_store=normalized_target_store,
        )
    )

    safe_workspace_store_root = (
        _assert_path_within_root_v1(
            candidate_path=workspace_store_root,
            allowed_root=authorized_store_base,
        )
    )

    if (
        safe_workspace_store_root
        == authorized_store_base
    ):
        raise LifecycleRepairExecutorEngineError(
            "Workspace store root must identify "
            "a workspace below the store root."
        )

    return safe_workspace_store_root


def _resolve_repair_target_descriptor_v1(
    *,
    project_root: str | Path,
    workspace_id: str,
    repair_action: Mapping[str, Any],
    source_finding: Mapping[str, Any],
) -> Mapping[str, Any]:

    normalized_workspace_id = (
        _require_string(
            workspace_id,
            field_name="workspace_id",
        )
    )

    action = _require_mapping(
        repair_action,
        field_name="repair_action",
    )

    finding = _require_mapping(
        source_finding,
        field_name="source_finding",
    )

    action_type = (
        _assert_supported_executor_action_type_v1(
            action.get(
                "repair_action_type"
            )
        )
    )

    target_store = (
        _resolve_action_target_store_v1(
            repair_action=action,
            source_finding=finding,
        )
    )

    workspace_store_root = (
        _resolve_verified_workspace_store_root_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
            target_store=target_store,
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

            target_path = None

            target_path_resolved = False

            target_path_error = str(
                exc
            )


    elif raw_target_path is not None:

        target_path_error = (
            "Target-path evidence must be a "
            "non-empty string."
        )


    target_exists = (
        target_path is not None
        and target_path.exists()
    )

    target_is_file = (
        target_path is not None
        and target_path.is_file()
    )


    if target_path is None:

        target_checksum_before = None

    elif not target_exists:

        target_checksum_before = "ABSENT"

    elif target_is_file:

        target_checksum_before = (
            _calculate_file_checksum_v1(
                path=target_path,
            )
        )

    else:

        target_checksum_before = "NON_FILE"


    descriptor = {
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

        "workspace_id":
            normalized_workspace_id,

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

        "mutation_authorized":
            False,

        "mutation_attempted":
            False,

        "mutation_performed":
            False,
    }

    descriptor[
        "target_descriptor_checksum"
    ] = (
        calculate_lifecycle_repair_executor_engine_checksum_v1(
            payload=descriptor,
        )
    )

    return _freeze(
        descriptor
    )


def _extract_normalized_lifecycle_state_v1(
    *,
    source_finding: Mapping[str, Any],
) -> str | None:

    value = (
        _find_first_evidence_value_v1(
            source_finding=source_finding,
            field_names=(
                "normalized_state",
                "expected_state",
                "recommended_state",
                "target_state",
            ),
        )
    )

    if not isinstance(
        value,
        str,
    ):
        return None

    normalized = value.strip().upper()

    if (
        normalized
        not in CANONICAL_LIFECYCLE_STATES
    ):
        return None

    return normalized


def _extract_controlled_replacement_record_v1(
    *,
    source_finding: Mapping[str, Any],
) -> Mapping[str, Any] | None:

    value = (
        _find_first_evidence_value_v1(
            source_finding=source_finding,
            field_names=(
                "replacement_record",
                "repaired_record",
                "normalized_record",
                "expected_record",
            ),
        )
    )

    if not isinstance(
        value,
        Mapping,
    ):
        return None

    return _freeze(
        dict(
            value
        )
    )
def _build_repair_mutation_intent_v1(
    *,
    project_root: str | Path,
    workspace_id: str,
    repair_action: Mapping[str, Any],
    source_finding: Mapping[str, Any],
) -> Mapping[str, Any]:

    normalized_workspace_id = (
        _require_string(
            workspace_id,
            field_name="workspace_id",
        )
    )

    action = _require_mapping(
        repair_action,
        field_name="repair_action",
    )

    finding = _require_mapping(
        source_finding,
        field_name="source_finding",
    )

    action_type = (
        _assert_supported_executor_action_type_v1(
            action.get(
                "repair_action_type"
            )
        )
    )

    strategy = (
        ACTION_EXECUTION_STRATEGIES.get(
            action_type
        )
    )

    if strategy is None:
        raise LifecycleRepairExecutorEngineError(
            "No execution strategy exists for action type: "
            + action_type
        )

    target = (
        _resolve_repair_target_descriptor_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
            repair_action=action,
            source_finding=finding,
        )
    )


    normalized_state: str | None = None

    replacement_record: Mapping[str, Any] | None = None

    sufficient_repair_evidence = False

    evidence_requirement = ""

    evidence_failures: list[str] = []


    # ---------------------------------------------------------
    # NORMALIZE_STATE
    # ---------------------------------------------------------

    if strategy == "NORMALIZE_STATE":

        normalized_state = (
            _extract_normalized_lifecycle_state_v1(
                source_finding=finding,
            )
        )

        if (
            target[
                "target_path_resolved"
            ]
            is not True
        ):
            evidence_failures.append(
                "TARGET_PATH_NOT_RESOLVED"
            )

        if (
            target[
                "target_exists"
            ]
            is not True
        ):
            evidence_failures.append(
                "TARGET_DOES_NOT_EXIST"
            )

        if (
            target[
                "target_is_file"
            ]
            is not True
        ):
            evidence_failures.append(
                "TARGET_IS_NOT_FILE"
            )

        if normalized_state is None:
            evidence_failures.append(
                "CANONICAL_LIFECYCLE_STATE_MISSING"
            )

        sufficient_repair_evidence = (
            not evidence_failures
        )

        evidence_requirement = (
            "An existing lifecycle record and a "
            "canonical normalized lifecycle state "
            "are required."
        )


    # ---------------------------------------------------------
    # REMOVE_TOMBSTONE_CONTENT
    # ---------------------------------------------------------

    elif strategy == "REMOVE_TOMBSTONE_CONTENT":

        if (
            target[
                "target_store"
            ]
            != "TOMBSTONE"
        ):
            evidence_failures.append(
                "TARGET_STORE_NOT_TOMBSTONE"
            )

        if (
            target[
                "target_path_resolved"
            ]
            is not True
        ):
            evidence_failures.append(
                "TARGET_PATH_NOT_RESOLVED"
            )

        if (
            target[
                "target_exists"
            ]
            is not True
        ):
            evidence_failures.append(
                "TARGET_DOES_NOT_EXIST"
            )

        if (
            target[
                "target_is_file"
            ]
            is not True
        ):
            evidence_failures.append(
                "TARGET_IS_NOT_FILE"
            )

        sufficient_repair_evidence = (
            not evidence_failures
        )

        evidence_requirement = (
            "An existing tombstone record inside "
            "the authorized Tombstone Store is required."
        )


    # ---------------------------------------------------------
    # QUARANTINE_FILE
    # ---------------------------------------------------------

    elif strategy == "QUARANTINE_FILE":

        if (
            target[
                "target_path_resolved"
            ]
            is not True
        ):
            evidence_failures.append(
                "TARGET_PATH_NOT_RESOLVED"
            )

        if (
            target[
                "target_exists"
            ]
            is not True
        ):
            evidence_failures.append(
                "TARGET_DOES_NOT_EXIST"
            )

        if (
            target[
                "target_is_file"
            ]
            is not True
        ):
            evidence_failures.append(
                "TARGET_IS_NOT_FILE"
            )

        sufficient_repair_evidence = (
            not evidence_failures
        )

        evidence_requirement = (
            "An existing invalid record and an "
            "authorized target store are required."
        )


    # ---------------------------------------------------------
    # CONTROLLED_JSON_REBUILD
    # ---------------------------------------------------------

    elif strategy == "CONTROLLED_JSON_REBUILD":

        replacement_record = (
            _extract_controlled_replacement_record_v1(
                source_finding=finding,
            )
        )

        if (
            target[
                "target_path_resolved"
            ]
            is not True
        ):
            evidence_failures.append(
                "TARGET_PATH_NOT_RESOLVED"
            )

        if replacement_record is None:
            evidence_failures.append(
                "REPLACEMENT_RECORD_MISSING"
            )

        sufficient_repair_evidence = (
            not evidence_failures
        )

        evidence_requirement = (
            "A workspace-bound target path and an "
            "explicit controlled replacement record "
            "are required."
        )


    else:
        raise LifecycleRepairExecutorEngineError(
            "Unhandled execution strategy: "
            + strategy
        )


    intent = {
        "schema":
            "body_store_lifecycle_repair_mutation_intent.v1",

        "executor_engine_schema":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_SCHEMA,

        "executor_engine_version":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_VERSION,

        "workspace_id":
            normalized_workspace_id,

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

        "target_descriptor_checksum":
            target[
                "target_descriptor_checksum"
            ],

        "normalized_lifecycle_state":
            normalized_state,

        "replacement_record":
            replacement_record,

        "sufficient_repair_evidence":
            sufficient_repair_evidence,

        "evidence_requirement":
            evidence_requirement,

        "evidence_failures":
            tuple(
                evidence_failures
            ),

        "mutation_authorized":
            False,

        "mutation_attempted":
            False,

        "mutation_performed":
            False,

        "repair_executed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
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


def _validate_mutation_intent_checksum_v1(
    *,
    mutation_intent: Mapping[str, Any],
) -> bool:

    intent = _require_mapping(
        mutation_intent,
        field_name="mutation_intent",
    )

    stored_checksum = (
        intent.get(
            "mutation_intent_checksum"
        )
    )

    if (
        not isinstance(
            stored_checksum,
            str,
        )
        or not stored_checksum.strip()
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
        calculated_checksum
        == stored_checksum
    )




def prepare_lifecycle_repair_execution_v1(
    *,
    project_root: str | Path,
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

    request = _require_mapping(
        execution_request,
        field_name="execution_request",
    )

    execution_mode = (
        _normalize_execution_mode_v1(
            request.get(
                "execution_mode"
            )
        )
    )


    # ---------------------------------------------------------
    # 1. Full execution-context validation
    # ---------------------------------------------------------

    context = (
        validate_lifecycle_repair_execution_context_v1(
            repair_plan=plan,
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
            "Lifecycle Repair Executor context "
            "failed mandatory safety gates."
        )


    # ---------------------------------------------------------
    # 2. Confirm requested mode eligibility
    # ---------------------------------------------------------

    if (
        execution_mode
        == "DRY_RUN"
        and context[
            "dry_run_eligible"
        ]
        is not True
    ):
        raise LifecycleRepairExecutorEngineError(
            "Execution context is not eligible "
            "for DRY_RUN."
        )


    if (
        execution_mode
        == "AUTHORIZED_APPLY"
        and context[
            "authorized_apply_eligible"
        ]
        is not True
    ):
        raise LifecycleRepairExecutorEngineError(
            "Execution context is not eligible "
            "for AUTHORIZED_APPLY."
        )


    workspace_id = _require_string(
        request.get(
            "workspace_id"
        ),
        field_name=(
            "execution_request.workspace_id"
        ),
    )

    requested_action_ids = (
        _normalize_action_ids_v1(
            request.get(
                "requested_action_ids",
                (),
            ),
            field_name=(
                "execution_request.requested_action_ids"
            ),
        )
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


    # ---------------------------------------------------------
    # 3. Build one immutable mutation intent per action
    # ---------------------------------------------------------

    for action_id in requested_action_ids:

        repair_action = (
            indexed_actions.get(
                action_id
            )
        )

        if repair_action is None:
            raise LifecycleRepairExecutorEngineError(
                "Requested repair action disappeared "
                "after context validation: "
                + action_id
            )

        source_finding_id = (
            _require_string(
                repair_action.get(
                    "source_finding_id"
                ),
                field_name=(
                    "repair_action.source_finding_id"
                ),
            )
        )

        source_finding = (
            indexed_findings.get(
                source_finding_id
            )
        )

        if source_finding is None:
            raise LifecycleRepairExecutorEngineError(
                "Source finding disappeared after "
                "context validation: "
                + source_finding_id
            )

        mutation_intent = (
            _build_repair_mutation_intent_v1(
                project_root=project_root,
                workspace_id=workspace_id,
                repair_action=repair_action,
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


        # -----------------------------------------------------
        # The next phases will add stronger content-specific
        # validation. At this point we only certify that the
        # evidence needed to formulate the intent exists.
        # -----------------------------------------------------

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
            )
        )


        prepared_action = {
            "repair_action_id":
                action_id,

            "source_finding_id":
                source_finding_id,

            "repair_action_type":
                repair_action.get(
                    "repair_action_type"
                ),

            "execution_mode":
                execution_mode,

            "target_store":
                mutation_intent[
                    "target_store"
                ],

            "target_path":
                mutation_intent[
                    "target_path"
                ],

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

            "evidence_failures":
                mutation_intent[
                    "evidence_failures"
                ],

            "preflight_passed":
                preflight_passed,

            "mutation_authorized":
                False,

            "mutation_attempted":
                False,

            "mutation_performed":
                False,

            "repair_executed":
                False,
        }

        prepared_action[
            "prepared_action_checksum"
        ] = (
            calculate_lifecycle_repair_executor_engine_checksum_v1(
                payload=prepared_action,
            )
        )

        prepared_actions.append(
            _freeze(
                prepared_action
            )
        )


    # ---------------------------------------------------------
    # 4. Aggregate preflight
    # ---------------------------------------------------------

    all_requested_actions_prepared = (
        len(
            prepared_actions
        )
        == len(
            requested_action_ids
        )
    )

    all_preflight_checks_passed = (
        all_requested_actions_prepared
        and all(
            prepared_action[
                "preflight_passed"
            ]
            is True

            for prepared_action
            in prepared_actions
        )
    )


    result = {
        "schema":
            "body_store_lifecycle_repair_execution_preflight.v1",

        "executor_engine_schema":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_SCHEMA,

        "executor_engine_version":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_VERSION,

        "executor_contract_version":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_VERSION,

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

        "authorization_id":
            request.get(
                "authorization_id"
            ),

        "execution_mode":
            execution_mode,

        "context_valid":
            context[
                "context_valid"
            ]
            is True,

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

        "all_requested_actions_prepared":
            all_requested_actions_prepared,

        "all_preflight_checks_passed":
            all_preflight_checks_passed,

        "prepared_actions":
            tuple(
                prepared_actions
            ),

        "execution_authorized":
            False,

        "execution_started":
            False,

        "execution_completed":
            False,

        "repair_executed":
            False,

        "mutation_performed":
            False,

        "runtime_job_created":
            False,

        "queue_job_created":
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
def _load_json_mapping_v1(
    *,
    path: Path,
    allowed_root: Path,
) -> Mapping[str, Any]:

    if not isinstance(
        path,
        Path,
    ):
        raise LifecycleRepairExecutorEngineError(
            "JSON record path must be a Path."
        )

    safe_path = (
        _assert_path_within_root_v1(
            candidate_path=path,
            allowed_root=allowed_root,
        )
    )

    if not safe_path.exists():
        raise LifecycleRepairExecutorEngineError(
            "JSON record does not exist: "
            + str(
                safe_path
            )
        )

    if not safe_path.is_file():
        raise LifecycleRepairExecutorEngineError(
            "JSON record path is not a file: "
            + str(
                safe_path
            )
        )

    try:

        value = json.loads(
            safe_path.read_text(
                encoding="utf-8"
            )
        )

    except Exception as exc:

        raise LifecycleRepairExecutorEngineError(
            "Unable to read JSON record: "
            + str(
                safe_path
            )
        ) from exc

    return _require_mapping(
        value,
        field_name=(
            "JSON record "
            + str(
                safe_path
            )
        ),
    )


def _write_json_atomic_v1(
    *,
    path: Path,
    payload: Mapping[str, Any],
    allowed_root: Path,
) -> Mapping[str, Any]:

    item = _require_mapping(
        payload,
        field_name="payload",
    )

    safe_path = (
        _assert_path_within_root_v1(
            candidate_path=path,
            allowed_root=allowed_root,
        )
    )

    resolved_allowed_root = (
        allowed_root.resolve(
            strict=False
        )
    )

    if safe_path == resolved_allowed_root:
        raise LifecycleRepairExecutorEngineError(
            "JSON mutation target must be a file "
            "beneath the authorized root."
        )


    # ---------------------------------------------------------
    # Serialize before touching the filesystem.
    # ---------------------------------------------------------

    try:

        serialized = json.dumps(
            _json_ready(
                item
            ),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )

    except Exception as exc:

        raise LifecycleRepairExecutorEngineError(
            "Replacement payload is not JSON serializable."
        ) from exc


    target_checksum_before = (
        _calculate_file_checksum_v1(
            path=safe_path,
        )
    )


    temporary_path = (
        safe_path.with_name(
            safe_path.name
            + ".repair_tmp"
        )
    )

    safe_temporary_path = (
        _assert_path_within_root_v1(
            candidate_path=temporary_path,
            allowed_root=resolved_allowed_root,
        )
    )


    if safe_temporary_path.exists():
        raise LifecycleRepairExecutorEngineError(
            "Atomic repair temporary file already exists: "
            + str(
                safe_temporary_path
            )
        )


    safe_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    try:

        safe_temporary_path.write_text(
            serialized
            + "\n",
            encoding="utf-8",
        )


        # -----------------------------------------------------
        # Re-read the temporary record before commit.
        # This confirms that what was written is valid JSON.
        # -----------------------------------------------------

        temporary_payload = (
            _load_json_mapping_v1(
                path=safe_temporary_path,
                allowed_root=resolved_allowed_root,
            )
        )


        expected_payload_checksum = (
            calculate_lifecycle_repair_executor_engine_checksum_v1(
                payload=item,
            )
        )


        temporary_payload_checksum = (
            calculate_lifecycle_repair_executor_engine_checksum_v1(
                payload=temporary_payload,
            )
        )


        if (
            temporary_payload_checksum
            != expected_payload_checksum
        ):
            raise LifecycleRepairExecutorEngineError(
                "Atomic JSON temporary payload "
                "verification failed."
            )


        temporary_file_checksum = (
            _calculate_file_checksum_v1(
                path=safe_temporary_path,
            )
        )


        # -----------------------------------------------------
        # Commit only after temporary-file verification.
        # Path.replace() performs the final replacement.
        # -----------------------------------------------------

        safe_temporary_path.replace(
            safe_path
        )


    except Exception:

        if safe_temporary_path.exists():

            try:
                safe_temporary_path.unlink()

            except Exception:
                pass

        raise


    if not safe_path.exists():
        raise LifecycleRepairExecutorEngineError(
            "Atomic JSON commit did not create "
            "the target record."
        )


    if not safe_path.is_file():
        raise LifecycleRepairExecutorEngineError(
            "Atomic JSON commit produced a non-file target."
        )


    committed_payload = (
        _load_json_mapping_v1(
            path=safe_path,
            allowed_root=resolved_allowed_root,
        )
    )


    committed_payload_checksum = (
        calculate_lifecycle_repair_executor_engine_checksum_v1(
            payload=committed_payload,
        )
    )


    if (
        committed_payload_checksum
        != expected_payload_checksum
    ):
        raise LifecycleRepairExecutorEngineError(
            "Committed JSON payload verification failed."
        )


    target_checksum_after = (
        _calculate_file_checksum_v1(
            path=safe_path,
        )
    )


    return _freeze(
        {
            "target_path":
                str(
                    safe_path
                ),

            "target_checksum_before":
                target_checksum_before,

            "temporary_file_checksum":
                temporary_file_checksum,

            "expected_payload_checksum":
                expected_payload_checksum,

            "committed_payload_checksum":
                committed_payload_checksum,

            "target_checksum_after":
                target_checksum_after,

            "atomic_write_verified":
                True,

            "mutation_performed":
                True,
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

                field_path = (
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
                        field_path
                    )

                visit(
                    nested,
                    field_path,
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

                field_path = (
                    prefix
                    + "["
                    + str(
                        index
                    )
                    + "]"
                )

                visit(
                    nested,
                    field_path,
                )


    visit(
        item,
        "",
    )

    return tuple(
        discovered
    )


def _remove_prohibited_tombstone_content_v1(
    *,
    payload: Mapping[str, Any],
) -> tuple[
    Mapping[str, Any],
    tuple[str, ...],
]:

    item = _require_mapping(
        payload,
        field_name="payload",
    )

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

            for key, nested in value.items():

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
                    nested,
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

            cleaned_items: list[Any] = []

            for index, nested in enumerate(
                value
            ):

                item_path = (
                    path
                    + "["
                    + str(
                        index
                    )
                    + "]"
                )

                cleaned_items.append(
                    clean(
                        nested,
                        item_path,
                    )
                )

            return cleaned_items


        return value


    cleaned_payload = clean(
        item,
        "",
    )


    if not isinstance(
        cleaned_payload,
        Mapping,
    ):
        raise LifecycleRepairExecutorEngineError(
            "Cleaned tombstone payload is not a mapping."
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
) -> Mapping[str, Any]:

    replacement = _require_mapping(
        replacement_record,
        field_name="replacement_record",
    )

    normalized_workspace_id = (
        _require_string(
            workspace_id,
            field_name="workspace_id",
        )
    )


    if not replacement:
        raise LifecycleRepairExecutorEngineError(
            "Replacement record must not be empty."
        )


    replacement_workspace_id = (
        replacement.get(
            "workspace_id"
        )
    )


    workspace_identity_present = (
        replacement_workspace_id
        is not None
    )


    workspace_identity_matches = True


    if replacement_workspace_id is not None:

        replacement_workspace_id = (
            _require_string(
                replacement_workspace_id,
                field_name=(
                    "replacement_record.workspace_id"
                ),
            )
        )

        workspace_identity_matches = (
            replacement_workspace_id
            == normalized_workspace_id
        )


        if not workspace_identity_matches:
            raise LifecycleRepairExecutorEngineError(
                "Replacement record workspace_id does not "
                "match the authorized workspace."
            )


    try:

        json.dumps(
            _json_ready(
                replacement
            ),
            ensure_ascii=False,
            sort_keys=True,
        )

    except Exception as exc:

        raise LifecycleRepairExecutorEngineError(
            "Replacement record is not JSON serializable."
        ) from exc


    replacement_checksum = (
        calculate_lifecycle_repair_executor_engine_checksum_v1(
            payload=replacement,
        )
    )


    return _freeze(
        {
            "replacement_boundary_valid":
                True,

            "workspace_id":
                normalized_workspace_id,

            "workspace_identity_present":
                workspace_identity_present,

            "workspace_identity_matches":
                workspace_identity_matches,

            "replacement_record_checksum":
                replacement_checksum,
        }
    )


def _validate_controlled_replacement_record_v1(
    *,
    repair_action_type: str,
    target_store: str,
    replacement_record: Mapping[str, Any],
    workspace_id: str,
) -> Mapping[str, Any]:

    action_type = (
        _assert_supported_executor_action_type_v1(
            repair_action_type
        )
    )

    normalized_target_store = (
        _require_string(
            target_store,
            field_name="target_store",
        ).upper()
    )

    replacement = _require_mapping(
        replacement_record,
        field_name="replacement_record",
    )


    # ---------------------------------------------------------
    # Action/store authorization boundary.
    # ---------------------------------------------------------

    _validate_action_target_store_boundary_v1(
        repair_action_type=action_type,
        target_store=normalized_target_store,
    )


    # ---------------------------------------------------------
    # Workspace and JSON boundary.
    # ---------------------------------------------------------

    replacement_boundary = (
        _validate_replacement_record_boundary_v1(
            replacement_record=replacement,
            workspace_id=workspace_id,
        )
    )


    prohibited_content_fields = (
        _find_prohibited_content_field_paths_v1(
            payload=replacement,
        )
    )


    metadata_only_action = (
        action_type
        in METADATA_ONLY_REPAIR_ACTION_TYPES
    )


    tombstone_target = (
        normalized_target_store
        == "TOMBSTONE"
    )


    # ---------------------------------------------------------
    # Metadata-only repair actions may never introduce
    # article body content.
    #
    # Tombstone records may never contain article body
    # content, regardless of repair action.
    # ---------------------------------------------------------

    content_boundary_valid = (
        not prohibited_content_fields
        if (
            metadata_only_action
            or tombstone_target
        )
        else True
    )


    if not content_boundary_valid:

        boundary_name = (
            "Tombstone"
            if tombstone_target
            else "Metadata repair"
        )

        raise LifecycleRepairExecutorEngineError(
            boundary_name
            + " replacement record contains prohibited "
            "article-body content fields: "
            + ", ".join(
                prohibited_content_fields
            )
        )


    return _freeze(
        {
            "replacement_record_valid":
                True,

            "repair_action_type":
                action_type,

            "target_store":
                normalized_target_store,

            "workspace_id":
                workspace_id,

            "replacement_boundary":
                replacement_boundary,

            "replacement_record_checksum":
                replacement_boundary[
                    "replacement_record_checksum"
                ],

            "metadata_only_action":
                metadata_only_action,

            "tombstone_target":
                tombstone_target,

            "prohibited_content_fields":
                prohibited_content_fields,

            "content_boundary_valid":
                content_boundary_valid,
        }
    )
def _execute_json_rebuild_v1(
    *,
    target_path: Path,
    workspace_store_root: Path,
    replacement_record: Mapping[str, Any],
    repair_action_type: str,
    target_store: str,
    workspace_id: str,
) -> Mapping[str, Any]:

    action_type = (
        _assert_supported_executor_action_type_v1(
            repair_action_type
        )
    )

    normalized_target_store = (
        _require_string(
            target_store,
            field_name="target_store",
        ).upper()
    )

    normalized_workspace_id = (
        _require_string(
            workspace_id,
            field_name="workspace_id",
        )
    )

    replacement = _require_mapping(
        replacement_record,
        field_name="replacement_record",
    )

    safe_target_path = (
        _assert_path_within_root_v1(
            candidate_path=target_path,
            allowed_root=workspace_store_root,
        )
    )


    # ---------------------------------------------------------
    # 1. Revalidate action/store/replacement boundaries
    # immediately before mutation.
    # ---------------------------------------------------------

    replacement_validation = (
        _validate_controlled_replacement_record_v1(
            repair_action_type=action_type,
            target_store=normalized_target_store,
            replacement_record=replacement,
            workspace_id=normalized_workspace_id,
        )
    )

    if (
        replacement_validation[
            "replacement_record_valid"
        ]
        is not True
    ):
        raise LifecycleRepairExecutorEngineError(
            "Controlled replacement record failed "
            "final validation."
        )


    target_checksum_before = (
        _calculate_file_checksum_v1(
            path=safe_target_path,
        )
    )


    replacement_payload_checksum = (
        calculate_lifecycle_repair_executor_engine_checksum_v1(
            payload=replacement,
        )
    )


    # ---------------------------------------------------------
    # 2. Detect structural no-op when an existing valid JSON
    # record already equals the replacement record.
    #
    # Invalid JSON is not treated as a no-op; a certified
    # rebuild may legitimately replace it.
    # ---------------------------------------------------------

    existing_payload_checksum: str | None = None

    if (
        safe_target_path.exists()
        and safe_target_path.is_file()
    ):

        try:

            current_record = (
                _load_json_mapping_v1(
                    path=safe_target_path,
                    allowed_root=workspace_store_root,
                )
            )

            existing_payload_checksum = (
                calculate_lifecycle_repair_executor_engine_checksum_v1(
                    payload=current_record,
                )
            )

        except LifecycleRepairExecutorEngineError:

            existing_payload_checksum = None


    if (
        existing_payload_checksum
        == replacement_payload_checksum
    ):

        return _freeze(
            {
                "repair_action_type":
                    action_type,

                "target_store":
                    normalized_target_store,

                "target_path":
                    str(
                        safe_target_path
                    ),

                "mutation_performed":
                    False,

                "no_op":
                    True,

                "no_op_reason":
                    "TARGET_ALREADY_MATCHES_REPLACEMENT",

                "target_checksum_before":
                    target_checksum_before,

                "target_checksum_after":
                    target_checksum_before,

                "replacement_record_checksum":
                    replacement_payload_checksum,

                "atomic_write_verified":
                    False,

                "removed_fields":
                    (),
            }
        )


    # ---------------------------------------------------------
    # 3. Atomic controlled rebuild.
    # ---------------------------------------------------------

    write_result = (
        _write_json_atomic_v1(
            path=safe_target_path,
            payload=replacement,
            allowed_root=workspace_store_root,
        )
    )


    # ---------------------------------------------------------
    # 4. Verify committed replacement again.
    # ---------------------------------------------------------

    committed_record = (
        _load_json_mapping_v1(
            path=safe_target_path,
            allowed_root=workspace_store_root,
        )
    )


    committed_payload_checksum = (
        calculate_lifecycle_repair_executor_engine_checksum_v1(
            payload=committed_record,
        )
    )


    if (
        committed_payload_checksum
        != replacement_payload_checksum
    ):
        raise LifecycleRepairExecutorEngineError(
            "Controlled JSON rebuild verification failed."
        )


    return _freeze(
        {
            "repair_action_type":
                action_type,

            "target_store":
                normalized_target_store,

            "target_path":
                str(
                    safe_target_path
                ),

            "mutation_performed":
                True,

            "no_op":
                False,

            "no_op_reason":
                None,

            "target_checksum_before":
                target_checksum_before,

            "target_checksum_after":
                write_result[
                    "target_checksum_after"
                ],

            "replacement_record_checksum":
                replacement_payload_checksum,

            "committed_payload_checksum":
                committed_payload_checksum,

            "atomic_write_verified":
                write_result[
                    "atomic_write_verified"
                ],

            "removed_fields":
                (),
        }
    )


def _execute_normalize_state_v1(
    *,
    target_path: Path,
    workspace_store_root: Path,
    workspace_id: str,
    normalized_state: str,
) -> Mapping[str, Any]:

    safe_target_path = (
        _assert_path_within_root_v1(
            candidate_path=target_path,
            allowed_root=workspace_store_root,
        )
    )

    normalized_workspace_id = (
        _require_string(
            workspace_id,
            field_name="workspace_id",
        )
    )

    canonical_state = (
        _require_string(
            normalized_state,
            field_name="normalized_state",
        ).upper()
    )


    if (
        canonical_state
        not in CANONICAL_LIFECYCLE_STATES
    ):
        raise LifecycleRepairExecutorEngineError(
            "Refusing non-canonical lifecycle state: "
            + canonical_state
        )


    record = dict(
        _load_json_mapping_v1(
            path=safe_target_path,
            allowed_root=workspace_store_root,
        )
    )


    # ---------------------------------------------------------
    # Workspace boundary.
    # ---------------------------------------------------------

    _validate_replacement_record_boundary_v1(
        replacement_record=record,
        workspace_id=normalized_workspace_id,
    )


    lifecycle_state_present = (
        "lifecycle_state"
        in record
    )

    state_present = (
        "state"
        in record
    )


    if (
        not lifecycle_state_present
        and not state_present
    ):
        raise LifecycleRepairExecutorEngineError(
            "Lifecycle record does not expose an existing "
            "lifecycle_state or state field."
        )


    # ---------------------------------------------------------
    # If both state fields exist, conflicting values are
    # ambiguous and must fail closed.
    # ---------------------------------------------------------

    if (
        lifecycle_state_present
        and state_present
    ):

        lifecycle_state_value = (
            record.get(
                "lifecycle_state"
            )
        )

        state_value = (
            record.get(
                "state"
            )
        )

        if (
            lifecycle_state_value
            != state_value
        ):
            raise LifecycleRepairExecutorEngineError(
                "Lifecycle record contains conflicting "
                "lifecycle_state and state values."
            )

        state_fields = (
            "lifecycle_state",
            "state",
        )

    elif lifecycle_state_present:

        state_fields = (
            "lifecycle_state",
        )

    else:

        state_fields = (
            "state",
        )


    previous_states = {
        field_name:
            record.get(
                field_name
            )

        for field_name
        in state_fields
    }


    already_normalized = all(
        (
            isinstance(
                previous_states[
                    field_name
                ],
                str,
            )
            and previous_states[
                field_name
            ].strip().upper()
            == canonical_state
        )

        for field_name
        in state_fields
    )


    target_checksum_before = (
        _calculate_file_checksum_v1(
            path=safe_target_path,
        )
    )


    if already_normalized:

        return _freeze(
            {
                "target_path":
                    str(
                        safe_target_path
                    ),

                "mutation_performed":
                    False,

                "no_op":
                    True,

                "no_op_reason":
                    "LIFECYCLE_STATE_ALREADY_NORMALIZED",

                "state_fields":
                    state_fields,

                "previous_states":
                    previous_states,

                "normalized_state":
                    canonical_state,

                "target_checksum_before":
                    target_checksum_before,

                "target_checksum_after":
                    target_checksum_before,

                "atomic_write_verified":
                    False,

                "removed_fields":
                    (),
            }
        )


    # ---------------------------------------------------------
    # Normalize all existing state aliases together.
    # ---------------------------------------------------------

    for field_name in state_fields:

        record[
            field_name
        ] = canonical_state


    write_result = (
        _write_json_atomic_v1(
            path=safe_target_path,
            payload=record,
            allowed_root=workspace_store_root,
        )
    )


    # ---------------------------------------------------------
    # Verify state after commit.
    # ---------------------------------------------------------

    verified_record = (
        _load_json_mapping_v1(
            path=safe_target_path,
            allowed_root=workspace_store_root,
        )
    )


    for field_name in state_fields:

        verified_value = (
            verified_record.get(
                field_name
            )
        )

        if (
            not isinstance(
                verified_value,
                str,
            )
            or verified_value.strip().upper()
            != canonical_state
        ):
            raise LifecycleRepairExecutorEngineError(
                "Lifecycle-state normalization "
                "verification failed for field: "
                + field_name
            )


    return _freeze(
        {
            "target_path":
                str(
                    safe_target_path
                ),

            "mutation_performed":
                True,

            "no_op":
                False,

            "no_op_reason":
                None,

            "state_fields":
                state_fields,

            "previous_states":
                previous_states,

            "normalized_state":
                canonical_state,

            "target_checksum_before":
                target_checksum_before,

            "target_checksum_after":
                write_result[
                    "target_checksum_after"
                ],

            "atomic_write_verified":
                write_result[
                    "atomic_write_verified"
                ],

            "removed_fields":
                (),
        }
    )


def _execute_remove_tombstone_content_v1(
    *,
    target_path: Path,
    workspace_store_root: Path,
    workspace_id: str,
) -> Mapping[str, Any]:

    normalized_workspace_id = (
        _require_string(
            workspace_id,
            field_name="workspace_id",
        )
    )

    safe_target_path = (
        _assert_path_within_root_v1(
            candidate_path=target_path,
            allowed_root=workspace_store_root,
        )
    )


    record = (
        _load_json_mapping_v1(
            path=safe_target_path,
            allowed_root=workspace_store_root,
        )
    )


    # ---------------------------------------------------------
    # Ensure this record cannot belong to another workspace.
    # ---------------------------------------------------------

    _validate_replacement_record_boundary_v1(
        replacement_record=record,
        workspace_id=normalized_workspace_id,
    )


    prohibited_fields_before = (
        _find_prohibited_content_field_paths_v1(
            payload=record,
        )
    )


    target_checksum_before = (
        _calculate_file_checksum_v1(
            path=safe_target_path,
        )
    )


    # ---------------------------------------------------------
    # Nothing prohibited exists: valid no-op.
    # ---------------------------------------------------------

    if not prohibited_fields_before:

        return _freeze(
            {
                "target_path":
                    str(
                        safe_target_path
                    ),

                "mutation_performed":
                    False,

                "no_op":
                    True,

                "no_op_reason":
                    "NO_PROHIBITED_TOMBSTONE_CONTENT",

                "target_checksum_before":
                    target_checksum_before,

                "target_checksum_after":
                    target_checksum_before,

                "prohibited_fields_before":
                    (),

                "removed_fields":
                    (),

                "removed_field_count":
                    0,

                "prohibited_fields_after":
                    (),

                "tombstone_content_boundary_verified":
                    True,

                "atomic_write_verified":
                    False,
            }
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
        raise LifecycleRepairExecutorEngineError(
            "Tombstone sanitizer detected prohibited "
            "content but removed nothing."
        )


    prohibited_fields_after_cleaning = (
        _find_prohibited_content_field_paths_v1(
            payload=cleaned_record,
        )
    )


    if prohibited_fields_after_cleaning:
        raise LifecycleRepairExecutorEngineError(
            "Tombstone sanitizer failed to remove all "
            "prohibited article-body content."
        )


    # ---------------------------------------------------------
    # Cleaned tombstone must still obey workspace boundary.
    # ---------------------------------------------------------

    _validate_replacement_record_boundary_v1(
        replacement_record=cleaned_record,
        workspace_id=normalized_workspace_id,
    )


    write_result = (
        _write_json_atomic_v1(
            path=safe_target_path,
            payload=cleaned_record,
            allowed_root=workspace_store_root,
        )
    )


    # ---------------------------------------------------------
    # Final post-commit Tombstone boundary verification.
    # ---------------------------------------------------------

    verified_record = (
        _load_json_mapping_v1(
            path=safe_target_path,
            allowed_root=workspace_store_root,
        )
    )


    prohibited_fields_after = (
        _find_prohibited_content_field_paths_v1(
            payload=verified_record,
        )
    )


    if prohibited_fields_after:
        raise LifecycleRepairExecutorEngineError(
            "Committed Tombstone record still contains "
            "prohibited article-body content."
        )


    return _freeze(
        {
            "target_path":
                str(
                    safe_target_path
                ),

            "mutation_performed":
                True,

            "no_op":
                False,

            "no_op_reason":
                None,

            "target_checksum_before":
                target_checksum_before,

            "target_checksum_after":
                write_result[
                    "target_checksum_after"
                ],

            "prohibited_fields_before":
                prohibited_fields_before,

            "removed_fields":
                removed_fields,

            "removed_field_count":
                len(
                    removed_fields
                ),

            "prohibited_fields_after":
                prohibited_fields_after,

            "tombstone_content_boundary_verified":
                True,

            "atomic_write_verified":
                write_result[
                    "atomic_write_verified"
                ],
        }
    )
def _execute_quarantine_file_v1(
    *,
    project_root: str | Path,
    workspace_id: str,
    target_store: str,
    source_path: Path,
    workspace_store_root: Path,
) -> Mapping[str, Any]:

    normalized_workspace_id = (
        _require_string(
            workspace_id,
            field_name="workspace_id",
        )
    )

    normalized_target_store = (
        _require_string(
            target_store,
            field_name="target_store",
        ).upper()
    )

    if (
        normalized_target_store
        not in SUPPORTED_TARGET_STORES
    ):
        raise LifecycleRepairExecutorEngineError(
            "Unsupported quarantine target store: "
            + normalized_target_store
        )


    # ---------------------------------------------------------
    # 1. Verify source is inside its authorized workspace store.
    # ---------------------------------------------------------

    safe_source_path = (
        _assert_path_within_root_v1(
            candidate_path=source_path,
            allowed_root=workspace_store_root,
        )
    )

    if not safe_source_path.exists():
        raise LifecycleRepairExecutorEngineError(
            "Quarantine source does not exist: "
            + str(
                safe_source_path
            )
        )

    if not safe_source_path.is_file():
        raise LifecycleRepairExecutorEngineError(
            "Quarantine source is not a file: "
            + str(
                safe_source_path
            )
        )


    # ---------------------------------------------------------
    # 2. Determine safe quarantine destination.
    # ---------------------------------------------------------

    quarantine_root = (
        _resolve_quarantine_root_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
        )
    )

    resolved_workspace_store_root = (
        workspace_store_root.resolve(
            strict=False
        )
    )

    relative_source_path = (
        safe_source_path.relative_to(
            resolved_workspace_store_root
        )
    )

    store_quarantine_root = (
        quarantine_root
        / normalized_target_store.lower()
    )

    safe_store_quarantine_root = (
        _assert_path_within_root_v1(
            candidate_path=store_quarantine_root,
            allowed_root=quarantine_root,
        )
    )

    quarantine_path = (
        safe_store_quarantine_root
        / relative_source_path
    )

    safe_quarantine_path = (
        _assert_path_within_root_v1(
            candidate_path=quarantine_path,
            allowed_root=safe_store_quarantine_root,
        )
    )


    if safe_quarantine_path.exists():
        raise LifecycleRepairExecutorEngineError(
            "Quarantine destination already exists: "
            + str(
                safe_quarantine_path
            )
        )


    source_checksum_before = (
        _calculate_file_checksum_v1(
            path=safe_source_path,
        )
    )


    # ---------------------------------------------------------
    # 3. Copy to temporary quarantine artifact first.
    # ---------------------------------------------------------

    quarantine_temp_path = (
        safe_quarantine_path.with_name(
            safe_quarantine_path.name
            + ".quarantine_tmp"
        )
    )

    safe_quarantine_temp_path = (
        _assert_path_within_root_v1(
            candidate_path=quarantine_temp_path,
            allowed_root=safe_store_quarantine_root,
        )
    )


    if safe_quarantine_temp_path.exists():
        raise LifecycleRepairExecutorEngineError(
            "Temporary quarantine artifact already exists: "
            + str(
                safe_quarantine_temp_path
            )
        )


    safe_quarantine_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    try:

        shutil.copy2(
            safe_source_path,
            safe_quarantine_temp_path,
        )


        temporary_checksum = (
            _calculate_file_checksum_v1(
                path=safe_quarantine_temp_path,
            )
        )


        if (
            temporary_checksum
            != source_checksum_before
        ):
            raise LifecycleRepairExecutorEngineError(
                "Temporary quarantine copy checksum mismatch."
            )


        # -----------------------------------------------------
        # 4. Commit quarantine copy.
        # -----------------------------------------------------

        safe_quarantine_temp_path.replace(
            safe_quarantine_path
        )


        quarantine_checksum = (
            _calculate_file_checksum_v1(
                path=safe_quarantine_path,
            )
        )


        if (
            quarantine_checksum
            != source_checksum_before
        ):
            raise LifecycleRepairExecutorEngineError(
                "Committed quarantine checksum mismatch."
            )


        # -----------------------------------------------------
        # 5. Only after verified quarantine copy exists may
        # the original record be removed.
        # -----------------------------------------------------

        safe_source_path.unlink()


        if safe_source_path.exists():
            raise LifecycleRepairExecutorEngineError(
                "Original record still exists after "
                "quarantine commit."
            )


    except Exception:

        # If the original is still intact, remove an incomplete
        # quarantine artifact so a retry starts cleanly.
        if safe_source_path.exists():

            if safe_quarantine_temp_path.exists():

                try:
                    safe_quarantine_temp_path.unlink()

                except Exception:
                    pass


            if safe_quarantine_path.exists():

                try:
                    safe_quarantine_path.unlink()

                except Exception:
                    pass

        raise


    return _freeze(
        {
            "target_store":
                normalized_target_store,

            "source_path":
                str(
                    safe_source_path
                ),

            "source_checksum_before":
                source_checksum_before,

            "source_removed":
                not safe_source_path.exists(),

            "quarantine_path":
                str(
                    safe_quarantine_path
                ),

            "quarantine_checksum":
                quarantine_checksum,

            "quarantine_verified":
                (
                    quarantine_checksum
                    == source_checksum_before
                ),

            "target_checksum_after":
                "ABSENT",

            "mutation_performed":
                True,

            "no_op":
                False,

            "removed_fields":
                (),
        }
    )


def _dispatch_authorized_mutation_v1(
    *,
    project_root: str | Path,
    workspace_id: str,
    mutation_intent: Mapping[str, Any],
    execution_authorized: bool,
) -> Mapping[str, Any]:

    intent = _require_mapping(
        mutation_intent,
        field_name="mutation_intent",
    )

    normalized_workspace_id = (
        _require_string(
            workspace_id,
            field_name="workspace_id",
        )
    )


    # ---------------------------------------------------------
    # 1. This dispatcher must never be callable as an
    # unauthorized mutation shortcut.
    # ---------------------------------------------------------

    if execution_authorized is not True:
        raise LifecycleRepairExecutorEngineError(
            "Authorized mutation dispatcher requires "
            "explicit execution authorization."
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


    # ---------------------------------------------------------
    # 2. Workspace identity.
    # ---------------------------------------------------------

    intent_workspace_id = (
        _require_string(
            intent.get(
                "workspace_id"
            ),
            field_name=(
                "mutation_intent.workspace_id"
            ),
        )
    )


    if (
        intent_workspace_id
        != normalized_workspace_id
    ):
        raise LifecycleRepairExecutorEngineError(
            "Mutation intent workspace does not match "
            "the authorized execution workspace."
        )


    # ---------------------------------------------------------
    # 3. Repair action and target-store boundaries.
    # ---------------------------------------------------------

    action_type = (
        _assert_supported_executor_action_type_v1(
            intent.get(
                "repair_action_type"
            )
        )
    )


    target_store = (
        _require_string(
            intent.get(
                "target_store"
            ),
            field_name=(
                "mutation_intent.target_store"
            ),
        ).upper()
    )


    _validate_action_target_store_boundary_v1(
        repair_action_type=action_type,
        target_store=target_store,
    )


    # ---------------------------------------------------------
    # 4. Strategy must exactly match the registered strategy
    # for the certified action type.
    # ---------------------------------------------------------

    strategy = (
        _require_string(
            intent.get(
                "execution_strategy"
            ),
            field_name=(
                "mutation_intent.execution_strategy"
            ),
        )
    )


    expected_strategy = (
        ACTION_EXECUTION_STRATEGIES.get(
            action_type
        )
    )


    if expected_strategy is None:
        raise LifecycleRepairExecutorEngineError(
            "No registered execution strategy for action: "
            + action_type
        )


    if strategy != expected_strategy:
        raise LifecycleRepairExecutorEngineError(
            "Mutation strategy does not match "
            "the registered repair-action strategy."
        )


    # ---------------------------------------------------------
    # 5. Independently reconstruct the authorized workspace
    # store root instead of trusting the mutation intent.
    # ---------------------------------------------------------

    verified_workspace_store_root = (
        _resolve_verified_workspace_store_root_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
            target_store=target_store,
        )
    )


    supplied_workspace_store_root = Path(
        _require_string(
            intent.get(
                "workspace_store_root"
            ),
            field_name=(
                "mutation_intent.workspace_store_root"
            ),
        )
    ).resolve(
        strict=False
    )


    if (
        supplied_workspace_store_root
        != verified_workspace_store_root
    ):
        raise LifecycleRepairExecutorEngineError(
            "Mutation intent workspace-store root "
            "does not match the independently "
            "resolved authorized store root."
        )


    # ---------------------------------------------------------
    # 6. Revalidate target path.
    # ---------------------------------------------------------

    target_path = Path(
        _require_string(
            intent.get(
                "target_path"
            ),
            field_name=(
                "mutation_intent.target_path"
            ),
        )
    )


    safe_target_path = (
        _assert_path_within_root_v1(
            candidate_path=target_path,
            allowed_root=verified_workspace_store_root,
        )
    )


    if (
        safe_target_path
        == verified_workspace_store_root
    ):
        raise LifecycleRepairExecutorEngineError(
            "Mutation target cannot be the workspace "
            "store root itself."
        )


    # ---------------------------------------------------------
    # 7. Dispatch only the four certified repair strategies.
    # No delete/archive/restore bypass exists here.
    # ---------------------------------------------------------

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
                "Controlled JSON rebuild requires "
                "replacement_record."
            )


        handler_result = (
            _execute_json_rebuild_v1(
                target_path=safe_target_path,
                workspace_store_root=(
                    verified_workspace_store_root
                ),
                replacement_record=replacement_record,
                repair_action_type=action_type,
                target_store=target_store,
                workspace_id=normalized_workspace_id,
            )
        )


    elif strategy == "NORMALIZE_STATE":

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
                "a canonical lifecycle state."
            )


        handler_result = (
            _execute_normalize_state_v1(
                target_path=safe_target_path,
                workspace_store_root=(
                    verified_workspace_store_root
                ),
                workspace_id=normalized_workspace_id,
                normalized_state=normalized_state,
            )
        )


    elif strategy == "REMOVE_TOMBSTONE_CONTENT":

        if target_store != "TOMBSTONE":
            raise LifecycleRepairExecutorEngineError(
                "Tombstone content removal may only "
                "operate on the Tombstone Store."
            )


        handler_result = (
            _execute_remove_tombstone_content_v1(
                target_path=safe_target_path,
                workspace_store_root=(
                    verified_workspace_store_root
                ),
                workspace_id=normalized_workspace_id,
            )
        )


    elif strategy == "QUARANTINE_FILE":

        handler_result = (
            _execute_quarantine_file_v1(
                project_root=project_root,
                workspace_id=normalized_workspace_id,
                target_store=target_store,
                source_path=safe_target_path,
                workspace_store_root=(
                    verified_workspace_store_root
                ),
            )
        )


    else:

        raise LifecycleRepairExecutorEngineError(
            "Unsupported authorized mutation strategy: "
            + strategy
        )


    # ---------------------------------------------------------
    # 8. Wrap mutation outcome in a deterministic dispatcher
    # result.
    # ---------------------------------------------------------

    mutation_performed = (
        handler_result.get(
            "mutation_performed"
        )
        is True
    )


    dispatch_result = {
        "schema":
            "body_store_lifecycle_repair_dispatch_result.v1",

        "executor_engine_schema":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_SCHEMA,

        "executor_engine_version":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_VERSION,

        "workspace_id":
            normalized_workspace_id,

        "repair_action_id":
            intent.get(
                "repair_action_id"
            ),

        "source_finding_id":
            intent.get(
                "source_finding_id"
            ),

        "repair_action_type":
            action_type,

        "execution_strategy":
            strategy,

        "target_store":
            target_store,

        "target_path":
            str(
                safe_target_path
            ),

        "execution_authorized":
            True,

        "mutation_attempted":
            True,

        "mutation_performed":
            mutation_performed,

        "no_op":
            handler_result.get(
                "no_op"
            )
            is True,

        "handler_result":
            handler_result,

        "runtime_job_created":
            False,

        "queue_job_created":
            False,
    }


    dispatch_result[
        "dispatch_result_checksum"
    ] = (
        calculate_lifecycle_repair_executor_engine_checksum_v1(
            payload=dispatch_result,
        )
    )


    return _freeze(
        dispatch_result
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

    if (
        not isinstance(
            stored_checksum,
            str,
        )
        or not stored_checksum.strip()
    ):
        return False

    checksum_source = {
        key:
            value

        for key, value
        in item.items()

        if key
        != "preflight_checksum"
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


def _validate_prepared_action_checksum_v1(
    *,
    prepared_action: Mapping[str, Any],
) -> bool:

    item = _require_mapping(
        prepared_action,
        field_name="prepared_action",
    )

    stored_checksum = item.get(
        "prepared_action_checksum"
    )

    if (
        not isinstance(
            stored_checksum,
            str,
        )
        or not stored_checksum.strip()
    ):
        return False

    checksum_source = {
        key:
            value

        for key, value
        in item.items()

        if key
        != "prepared_action_checksum"
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


def validate_lifecycle_repair_execution_preflight_v1(
    *,
    project_root: str | Path,
    preflight: Mapping[str, Any],
) -> Mapping[str, Any]:

    item = _require_mapping(
        preflight,
        field_name="preflight",
    )


    # ---------------------------------------------------------
    # 1. Preflight identity
    # ---------------------------------------------------------

    schema_valid = (
        item.get(
            "schema"
        )
        == "body_store_lifecycle_repair_execution_preflight.v1"
    )

    engine_schema_valid = (
        item.get(
            "executor_engine_schema"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_SCHEMA
    )

    engine_version_valid = (
        item.get(
            "executor_engine_version"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_VERSION
    )

    contract_version_valid = (
        item.get(
            "executor_contract_version"
        )
        == BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_VERSION
    )


    preflight_checksum_valid = (
        _validate_preflight_checksum_v1(
            preflight=item,
        )
    )


    workspace_id = _require_string(
        item.get(
            "workspace_id"
        ),
        field_name="preflight.workspace_id",
    )


    execution_mode = (
        _normalize_execution_mode_v1(
            item.get(
                "execution_mode"
            )
        )
    )


    # ---------------------------------------------------------
    # 2. Requested and prepared action collections
    # ---------------------------------------------------------

    requested_action_ids = (
        _normalize_action_ids_v1(
            item.get(
                "requested_action_ids",
                (),
            ),
            field_name=(
                "preflight.requested_action_ids"
            ),
        )
    )


    prepared_actions_raw = (
        item.get(
            "prepared_actions"
        )
    )


    if not isinstance(
        prepared_actions_raw,
        (
            tuple,
            list,
        ),
    ):
        raise LifecycleRepairExecutorEngineError(
            "preflight.prepared_actions must be "
            "a tuple or list."
        )


    prepared_actions = tuple(
        _require_mapping(
            prepared_action,
            field_name="prepared_action",
        )

        for prepared_action
        in prepared_actions_raw
    )


    requested_action_count_valid = (
        item.get(
            "requested_action_count"
        )
        == len(
            requested_action_ids
        )
    )


    prepared_action_count_valid = (
        item.get(
            "prepared_action_count"
        )
        == len(
            prepared_actions
        )
    )


    all_requested_actions_prepared_valid = (
        item.get(
            "all_requested_actions_prepared"
        )
        is True
        and len(
            requested_action_ids
        )
        == len(
            prepared_actions
        )
    )


    # ---------------------------------------------------------
    # 3. Validate every prepared action independently.
    # ---------------------------------------------------------

    prepared_action_ids: list[str] = []

    prepared_action_checks: list[
        Mapping[str, Any]
    ] = []


    for prepared_action in prepared_actions:

        repair_action_id = (
            _require_string(
                prepared_action.get(
                    "repair_action_id"
                ),
                field_name=(
                    "prepared_action.repair_action_id"
                ),
            )
        )


        prepared_action_ids.append(
            repair_action_id
        )


        action_checksum_valid = (
            _validate_prepared_action_checksum_v1(
                prepared_action=prepared_action,
            )
        )


        mutation_intent = (
            _require_mapping(
                prepared_action.get(
                    "mutation_intent"
                ),
                field_name=(
                    "prepared_action.mutation_intent"
                ),
            )
        )


        mutation_intent_checksum_valid = (
            _validate_mutation_intent_checksum_v1(
                mutation_intent=mutation_intent,
            )
        )


        action_type = (
            _assert_supported_executor_action_type_v1(
                prepared_action.get(
                    "repair_action_type"
                )
            )
        )


        intent_action_type = (
            _assert_supported_executor_action_type_v1(
                mutation_intent.get(
                    "repair_action_type"
                )
            )
        )


        action_type_matches = (
            action_type
            == intent_action_type
        )


        action_id_matches_intent = (
            mutation_intent.get(
                "repair_action_id"
            )
            == repair_action_id
        )


        source_finding_id_matches = (
            mutation_intent.get(
                "source_finding_id"
            )
            == prepared_action.get(
                "source_finding_id"
            )
        )


        execution_mode_matches = (
            prepared_action.get(
                "execution_mode"
            )
            == execution_mode
        )


        target_store = (
            _require_string(
                mutation_intent.get(
                    "target_store"
                ),
                field_name=(
                    "mutation_intent.target_store"
                ),
            ).upper()
        )


        _validate_action_target_store_boundary_v1(
            repair_action_type=action_type,
            target_store=target_store,
        )


        verified_workspace_store_root = (
            _resolve_verified_workspace_store_root_v1(
                project_root=project_root,
                workspace_id=workspace_id,
                target_store=target_store,
            )
        )


        supplied_workspace_store_root = Path(
            _require_string(
                mutation_intent.get(
                    "workspace_store_root"
                ),
                field_name=(
                    "mutation_intent.workspace_store_root"
                ),
            )
        ).resolve(
            strict=False
        )


        workspace_store_root_matches = (
            supplied_workspace_store_root
            == verified_workspace_store_root
        )


        target_path_value = (
            mutation_intent.get(
                "target_path"
            )
        )


        target_path_valid = False

        target_shape_valid = False


        if (
            isinstance(
                target_path_value,
                str,
            )
            and target_path_value.strip()
        ):

            try:

                safe_target_path = (
                    _assert_path_within_root_v1(
                        candidate_path=Path(
                            target_path_value
                        ),
                        allowed_root=(
                            verified_workspace_store_root
                        ),
                    )
                )


                target_path_valid = (
                    safe_target_path
                    != verified_workspace_store_root
                )


                # ---------------------------------------------
                # Existing directories or other non-file paths
                # are never legitimate repair record targets.
                #
                # Missing targets can be valid for controlled
                # rebuild actions.
                # ---------------------------------------------

                target_exists_at_preflight = (
                    mutation_intent.get(
                        "target_exists"
                    )
                    is True
                )


                target_is_file_at_preflight = (
                    mutation_intent.get(
                        "target_is_file"
                    )
                    is True
                )


                if target_exists_at_preflight:

                    target_shape_valid = (
                        target_is_file_at_preflight
                    )

                else:

                    target_shape_valid = (
                        mutation_intent.get(
                            "target_checksum_before"
                        )
                        == "ABSENT"
                    )


            except LifecycleRepairExecutorEngineError:

                target_path_valid = False

                target_shape_valid = False


        evidence_valid = (
            prepared_action.get(
                "sufficient_repair_evidence"
            )
            is True
            and mutation_intent.get(
                "sufficient_repair_evidence"
            )
            is True
        )


        pristine_execution_state = all(
            (
                prepared_action.get(
                    "mutation_authorized"
                )
                is False,

                prepared_action.get(
                    "mutation_attempted"
                )
                is False,

                prepared_action.get(
                    "mutation_performed"
                )
                is False,

                prepared_action.get(
                    "repair_executed"
                )
                is False,

                mutation_intent.get(
                    "mutation_authorized"
                )
                is False,

                mutation_intent.get(
                    "mutation_attempted"
                )
                is False,

                mutation_intent.get(
                    "mutation_performed"
                )
                is False,

                mutation_intent.get(
                    "repair_executed"
                )
                is False,
            )
        )


        prepared_action_valid = all(
            (
                action_checksum_valid,
                mutation_intent_checksum_valid,
                action_type_matches,
                action_id_matches_intent,
                source_finding_id_matches,
                execution_mode_matches,
                workspace_store_root_matches,
                target_path_valid,
                target_shape_valid,
                evidence_valid,
                pristine_execution_state,
                prepared_action.get(
                    "preflight_passed"
                )
                is True,
            )
        )


        prepared_action_checks.append(
            _freeze(
                {
                    "repair_action_id":
                        repair_action_id,

                    "prepared_action_valid":
                        prepared_action_valid,

                    "prepared_action_checksum_valid":
                        action_checksum_valid,

                    "mutation_intent_checksum_valid":
                        mutation_intent_checksum_valid,

                    "action_type_matches":
                        action_type_matches,

                    "action_id_matches_intent":
                        action_id_matches_intent,

                    "source_finding_id_matches":
                        source_finding_id_matches,

                    "execution_mode_matches":
                        execution_mode_matches,

                    "workspace_store_root_matches":
                        workspace_store_root_matches,

                    "target_path_valid":
                        target_path_valid,

                    "target_shape_valid":
                        target_shape_valid,

                    "evidence_valid":
                        evidence_valid,

                    "pristine_execution_state":
                        pristine_execution_state,
                }
            )
        )


    # ---------------------------------------------------------
    # 4. Exact action ordering and uniqueness.
    # ---------------------------------------------------------

    prepared_action_ids_tuple = tuple(
        prepared_action_ids
    )


    prepared_action_ids_unique = (
        len(
            prepared_action_ids_tuple
        )
        == len(
            set(
                prepared_action_ids_tuple
            )
        )
    )


    prepared_action_order_matches_request = (
        prepared_action_ids_tuple
        == requested_action_ids
    )


    every_prepared_action_valid = all(
        check[
            "prepared_action_valid"
        ]
        is True

        for check
        in prepared_action_checks
    )


    aggregate_preflight_flag_valid = (
        item.get(
            "all_preflight_checks_passed"
        )
        is True
    )


    # ---------------------------------------------------------
    # 5. Preflight artifact must still be entirely pre-execution.
    # ---------------------------------------------------------

    pre_execution_state_valid = all(
        (
            item.get(
                "execution_authorized"
            )
            is False,

            item.get(
                "execution_started"
            )
            is False,

            item.get(
                "execution_completed"
            )
            is False,

            item.get(
                "repair_executed"
            )
            is False,

            item.get(
                "mutation_performed"
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


    preflight_valid = all(
        (
            schema_valid,
            engine_schema_valid,
            engine_version_valid,
            contract_version_valid,
            preflight_checksum_valid,
            requested_action_count_valid,
            prepared_action_count_valid,
            all_requested_actions_prepared_valid,
            prepared_action_ids_unique,
            prepared_action_order_matches_request,
            every_prepared_action_valid,
            aggregate_preflight_flag_valid,
            pre_execution_state_valid,
        )
    )


    result = {
        "schema":
            "body_store_lifecycle_repair_preflight_validation.v1",

        "executor_engine_schema":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_SCHEMA,

        "executor_engine_version":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_VERSION,

        "workspace_id":
            workspace_id,

        "execution_mode":
            execution_mode,

        "preflight_valid":
            preflight_valid,

        "schema_valid":
            schema_valid,

        "engine_schema_valid":
            engine_schema_valid,

        "engine_version_valid":
            engine_version_valid,

        "contract_version_valid":
            contract_version_valid,

        "preflight_checksum_valid":
            preflight_checksum_valid,

        "requested_action_count_valid":
            requested_action_count_valid,

        "prepared_action_count_valid":
            prepared_action_count_valid,

        "all_requested_actions_prepared_valid":
            all_requested_actions_prepared_valid,

        "prepared_action_ids_unique":
            prepared_action_ids_unique,

        "prepared_action_order_matches_request":
            prepared_action_order_matches_request,

        "every_prepared_action_valid":
            every_prepared_action_valid,

        "aggregate_preflight_flag_valid":
            aggregate_preflight_flag_valid,

        "pre_execution_state_valid":
            pre_execution_state_valid,

        "prepared_action_checks":
            tuple(
                prepared_action_checks
            ),

        "mutation_performed":
            False,

        "repair_executed":
            False,
    }


    result[
        "preflight_validation_checksum"
    ] = (
        calculate_lifecycle_repair_executor_engine_checksum_v1(
            payload=result,
        )
    )


    return _freeze(
        result
    )


def _verify_target_unchanged_since_preflight_v1(
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
            "Cannot verify changed target from an "
            "invalid mutation intent."
        )


    normalized_workspace_id = (
        _require_string(
            workspace_id,
            field_name="workspace_id",
        )
    )


    if (
        intent.get(
            "workspace_id"
        )
        != normalized_workspace_id
    ):
        raise LifecycleRepairExecutorEngineError(
            "Mutation intent workspace mismatch "
            "during target-change verification."
        )


    target_store = (
        _require_string(
            intent.get(
                "target_store"
            ),
            field_name=(
                "mutation_intent.target_store"
            ),
        ).upper()
    )


    authorized_workspace_store_root = (
        _resolve_verified_workspace_store_root_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
            target_store=target_store,
        )
    )


    supplied_workspace_store_root = Path(
        _require_string(
            intent.get(
                "workspace_store_root"
            ),
            field_name=(
                "mutation_intent.workspace_store_root"
            ),
        )
    ).resolve(
        strict=False
    )


    workspace_store_root_matches = (
        supplied_workspace_store_root
        == authorized_workspace_store_root
    )


    if not workspace_store_root_matches:
        raise LifecycleRepairExecutorEngineError(
            "Workspace store root changed or was "
            "tampered with after preflight."
        )


    target_path = Path(
        _require_string(
            intent.get(
                "target_path"
            ),
            field_name=(
                "mutation_intent.target_path"
            ),
        )
    )


    safe_target_path = (
        _assert_path_within_root_v1(
            candidate_path=target_path,
            allowed_root=authorized_workspace_store_root,
        )
    )


    if (
        safe_target_path
        == authorized_workspace_store_root
    ):
        raise LifecycleRepairExecutorEngineError(
            "Repair target may not be the workspace "
            "store root."
        )


    expected_checksum = (
        intent.get(
            "target_checksum_before"
        )
    )


    if not isinstance(
        expected_checksum,
        str,
    ):
        raise LifecycleRepairExecutorEngineError(
            "Mutation intent does not contain a valid "
            "preflight target checksum."
        )


    # ---------------------------------------------------------
    # Determine current target state.
    # ---------------------------------------------------------

    if not safe_target_path.exists():

        actual_checksum = "ABSENT"

        current_target_exists = False

        current_target_is_file = False


    elif not safe_target_path.is_file():

        actual_checksum = "NON_FILE"

        current_target_exists = True

        current_target_is_file = False


    else:

        actual_checksum = (
            _calculate_file_checksum_v1(
                path=safe_target_path,
            )
        )

        current_target_exists = True

        current_target_is_file = True


    target_unchanged = (
        actual_checksum
        == expected_checksum
    )


    # A NON_FILE state is never an executable repair target,
    # even if it happened to be NON_FILE during preflight.
    executable_target_shape = (
        actual_checksum
        != "NON_FILE"
    )


    transaction_safe = all(
        (
            target_unchanged,
            executable_target_shape,
            workspace_store_root_matches,
        )
    )


    result = {
        "schema":
            "body_store_lifecycle_repair_target_change_check.v1",

        "workspace_id":
            normalized_workspace_id,

        "repair_action_id":
            intent.get(
                "repair_action_id"
            ),

        "target_store":
            target_store,

        "target_path":
            str(
                safe_target_path
            ),

        "expected_checksum":
            expected_checksum,

        "actual_checksum":
            actual_checksum,

        "current_target_exists":
            current_target_exists,

        "current_target_is_file":
            current_target_is_file,

        "workspace_store_root_matches":
            workspace_store_root_matches,

        "target_unchanged":
            target_unchanged,

        "executable_target_shape":
            executable_target_shape,

        "transaction_safe":
            transaction_safe,

        "mutation_performed":
            False,
    }


    result[
        "target_change_check_checksum"
    ] = (
        calculate_lifecycle_repair_executor_engine_checksum_v1(
            payload=result,
        )
    )


    return _freeze(
        result
    )


def _verify_prepared_action_transaction_gate_v1(
    *,
    project_root: str | Path,
    workspace_id: str,
    prepared_action: Mapping[str, Any],
) -> Mapping[str, Any]:

    action = _require_mapping(
        prepared_action,
        field_name="prepared_action",
    )


    prepared_action_checksum_valid = (
        _validate_prepared_action_checksum_v1(
            prepared_action=action,
        )
    )


    if not prepared_action_checksum_valid:
        raise LifecycleRepairExecutorEngineError(
            "Prepared repair action checksum is invalid."
        )


    mutation_intent = (
        _require_mapping(
            action.get(
                "mutation_intent"
            ),
            field_name=(
                "prepared_action.mutation_intent"
            ),
        )
    )


    mutation_intent_checksum_valid = (
        _validate_mutation_intent_checksum_v1(
            mutation_intent=mutation_intent,
        )
    )


    if not mutation_intent_checksum_valid:
        raise LifecycleRepairExecutorEngineError(
            "Prepared mutation intent checksum is invalid."
        )


    if (
        action.get(
            "preflight_passed"
        )
        is not True
    ):
        raise LifecycleRepairExecutorEngineError(
            "Prepared repair action did not pass preflight."
        )


    if (
        action.get(
            "sufficient_repair_evidence"
        )
        is not True
    ):
        raise LifecycleRepairExecutorEngineError(
            "Prepared repair action has insufficient evidence."
        )


    target_change_check = (
        _verify_target_unchanged_since_preflight_v1(
            project_root=project_root,
            workspace_id=workspace_id,
            mutation_intent=mutation_intent,
        )
    )


    target_unchanged = (
        target_change_check[
            "target_unchanged"
        ]
        is True
    )


    transaction_safe = (
        target_change_check[
            "transaction_safe"
        ]
        is True
    )


    gate_passed = all(
        (
            prepared_action_checksum_valid,
            mutation_intent_checksum_valid,
            target_unchanged,
            transaction_safe,
        )
    )


    result = {
        "schema":
            "body_store_lifecycle_repair_transaction_gate.v1",

        "executor_engine_schema":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_SCHEMA,

        "executor_engine_version":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_VERSION,

        "repair_action_id":
            action.get(
                "repair_action_id"
            ),

        "source_finding_id":
            action.get(
                "source_finding_id"
            ),

        "prepared_action_checksum_valid":
            prepared_action_checksum_valid,

        "mutation_intent_checksum_valid":
            mutation_intent_checksum_valid,

        "target_unchanged":
            target_unchanged,

        "transaction_safe":
            transaction_safe,

        "gate_passed":
            gate_passed,

        "target_change_check":
            target_change_check,

        "execution_authorized":
            False,

        "mutation_attempted":
            False,

        "mutation_performed":
            False,

        "repair_executed":
            False,
    }


    result[
        "transaction_gate_checksum"
    ] = (
        calculate_lifecycle_repair_executor_engine_checksum_v1(
            payload=result,
        )
    )


    return _freeze(
        result
    )
EXECUTOR_ACTION_RESULT_STATUSES = (
    "NOT_EXECUTED",
    "DRY_RUN_VALIDATED",
    "EXECUTED",
    "SKIPPED",
    "REJECTED",
    "FAILED",
)



def _cleanup_executor_backup_root_v1(
    *,
    project_root: str | Path,
    workspace_id: str,
    execution_request_id: str,
) -> Mapping[str, Any]:

    import os as _os
    import time as _time


    normalized_workspace_id = (
        _require_string(
            workspace_id,
            field_name="workspace_id",
        )
    )

    normalized_execution_request_id = (
        _require_string(
            execution_request_id,
            field_name="execution_request_id",
        )
    )


    safe_backup_root = (
        _resolve_executor_backup_root_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
            execution_request_id=(
                normalized_execution_request_id
            ),
        )
    )


    safe_workspace_backup_root = (
        safe_backup_root.parent.resolve(
            strict=False
        )
    )


    if (
        safe_backup_root
        == safe_workspace_backup_root
    ):

        raise LifecycleRepairExecutorEngineError(
            "Executor backup cleanup may not target "
            "the workspace backup root itself."
        )


    if not safe_backup_root.exists():

        return _freeze(
            {
                "backup_cleanup_required":
                    False,

                "backup_cleanup_performed":
                    False,

                "backup_cleanup_verified":
                    True,

                "backup_preserved_for_recovery":
                    False,

                "backup_root":
                    str(
                        safe_backup_root
                    ),

                "cleanup_failure_reason":
                    None,
            }
        )


    if not safe_backup_root.is_dir():

        return _freeze(
            {
                "backup_cleanup_required":
                    True,

                "backup_cleanup_performed":
                    False,

                "backup_cleanup_verified":
                    False,

                "backup_preserved_for_recovery":
                    True,

                "backup_root":
                    str(
                        safe_backup_root
                    ),

                "cleanup_failure_reason":
                    (
                        "Executor backup root is not "
                        "a directory."
                    ),
            }
        )


    # ========================================================
    # LEGACY STAGING GUARD
    #
    # The new cleanup path does not create or use staging.
    # If an old staging directory exists, fail closed.
    # ========================================================

    legacy_staging_path = (
        safe_backup_root.with_name(
            safe_backup_root.name
            + ".cleanup_pending"
        )
    )


    legacy_staging_path = (
        _assert_path_within_root_v1(
            candidate_path=(
                legacy_staging_path
            ),
            allowed_root=(
                safe_workspace_backup_root
            ),
        )
    )


    if legacy_staging_path.exists():

        return _freeze(
            {
                "backup_cleanup_required":
                    True,

                "backup_cleanup_performed":
                    False,

                "backup_cleanup_verified":
                    False,

                "backup_preserved_for_recovery":
                    True,

                "backup_root":
                    str(
                        safe_backup_root
                    ),

                "cleanup_failure_reason":
                    (
                        "Legacy backup cleanup staging "
                        "directory exists."
                    ),
            }
        )


    retry_attempts = 10

    retry_delay_seconds = 0.01


    # ========================================================
    # SAFE FILE DELETE
    # ========================================================

    def _remove_file(
        file_path: Path,
    ) -> None:

        last_error = None


        for attempt in range(
            retry_attempts
        ):

            try:

                file_path.unlink()

                return

            except FileNotFoundError:

                return

            except PermissionError as exc:

                last_error = exc

                try:

                    file_path.chmod(
                        0o600
                    )

                except Exception as chmod_exc:

                    last_error = (
                        chmod_exc
                    )

            except OSError as exc:

                last_error = exc


            if (
                attempt + 1
                < retry_attempts
            ):

                _time.sleep(
                    retry_delay_seconds
                )


        raise LifecycleRepairExecutorEngineError(
            "Executor backup cleanup could not "
            "remove file after bounded retry: "
            + str(
                file_path
            )
            + " :: "
            + str(
                last_error
            )
        )


    # ========================================================
    # SAFE DIRECTORY DELETE
    # ========================================================

    def _remove_directory(
        directory_path: Path,
    ) -> None:

        last_error = None


        for attempt in range(
            retry_attempts
        ):

            try:

                directory_path.rmdir()

                return

            except FileNotFoundError:

                return

            except OSError as exc:

                last_error = exc


            if (
                attempt + 1
                < retry_attempts
            ):

                _time.sleep(
                    retry_delay_seconds
                )


        raise LifecycleRepairExecutorEngineError(
            "Executor backup cleanup could not "
            "remove directory after bounded retry: "
            + str(
                directory_path
            )
            + " :: "
            + str(
                last_error
            )
        )


    cleanup_entries = []

    pending_directories = [
        safe_backup_root
    ]


    cleanup_failure_reason = None

    cleanup_performed = False


    try:

        # ====================================================
        # PREFLIGHT ENTIRE TREE BEFORE MUTATION
        # ====================================================

        while pending_directories:

            directory_path = (
                pending_directories.pop()
            )


            try:

                directory_path.relative_to(
                    safe_backup_root
                )

            except ValueError as exc:

                raise LifecycleRepairExecutorEngineError(
                    "Executor backup cleanup directory "
                    "escaped the transaction backup root: "
                    + str(
                        directory_path
                    )
                ) from exc


            with _os.scandir(
                directory_path
            ) as iterator:

                directory_entries = tuple(
                    iterator
                )


            for entry in directory_entries:

                child_path = Path(
                    entry.path
                )


                try:

                    child_path.relative_to(
                        safe_backup_root
                    )

                except ValueError as exc:

                    raise LifecycleRepairExecutorEngineError(
                        "Executor backup cleanup entry "
                        "escaped the transaction backup root: "
                        + str(
                            child_path
                        )
                    ) from exc


                if entry.is_symlink():

                    raise LifecycleRepairExecutorEngineError(
                        "Executor backup cleanup refuses "
                        "symbolic links: "
                        + str(
                            child_path
                        )
                    )


                if entry.is_file(
                    follow_symlinks=False
                ):

                    cleanup_entries.append(
                        (
                            child_path,
                            "FILE",
                        )
                    )


                elif entry.is_dir(
                    follow_symlinks=False
                ):

                    cleanup_entries.append(
                        (
                            child_path,
                            "DIRECTORY",
                        )
                    )

                    pending_directories.append(
                        child_path
                    )


                else:

                    raise LifecycleRepairExecutorEngineError(
                        "Executor backup cleanup found an "
                        "unsupported filesystem object: "
                        + str(
                            child_path
                        )
                    )


        # ====================================================
        # DELETE DEEPEST ENTRIES FIRST
        # ====================================================

        cleanup_entries.sort(
            key=lambda item: (
                len(
                    item[0].parts
                ),
                1
                if item[1] == "FILE"
                else 0,
            ),
            reverse=True,
        )


        for (
            cleanup_path,
            cleanup_type,
        ) in cleanup_entries:

            if cleanup_type == "FILE":

                _remove_file(
                    cleanup_path
                )

            else:

                _remove_directory(
                    cleanup_path
                )


        # ====================================================
        # TRANSACTION ROOT LAST
        # ====================================================

        _remove_directory(
            safe_backup_root
        )


        if safe_backup_root.exists():

            raise LifecycleRepairExecutorEngineError(
                "Executor backup cleanup could not "
                "verify backup-root removal."
            )


        if legacy_staging_path.exists():

            raise LifecycleRepairExecutorEngineError(
                "Executor backup cleanup unexpectedly "
                "created a staging directory."
            )


        cleanup_performed = True


    except Exception as exc:

        cleanup_failure_reason = str(
            exc
        )


    cleanup_verified = (
        cleanup_performed
        and not safe_backup_root.exists()
        and not legacy_staging_path.exists()
    )


    backup_preserved_for_recovery = (
        safe_backup_root.exists()
    )


    return _freeze(
        {
            "backup_cleanup_required":
                True,

            "backup_cleanup_performed":
                cleanup_performed,

            "backup_cleanup_verified":
                cleanup_verified,

            "backup_preserved_for_recovery":
                backup_preserved_for_recovery,

            "backup_root":
                str(
                    safe_backup_root
                ),

            "cleanup_failure_reason":
                cleanup_failure_reason,
        }
    )


def _remove_quarantine_artifact_for_rollback_v1(
    *,
    project_root: str | Path,
    workspace_id: str,
    mutation_result: Mapping[str, Any],
) -> Mapping[str, Any]:

    normalized_workspace_id = (
        _require_string(
            workspace_id,
            field_name="workspace_id",
        )
    )

    result = _require_mapping(
        mutation_result,
        field_name="mutation_result",
    )


    # ---------------------------------------------------------
    # Dispatcher results wrap the actual handler result.
    # Accept the wrapper but inspect the handler payload.
    # ---------------------------------------------------------

    handler_result_raw = result.get(
        "handler_result"
    )

    if isinstance(
        handler_result_raw,
        Mapping,
    ):
        handler_result = handler_result_raw

    else:
        handler_result = result


    quarantine_path_value = (
        handler_result.get(
            "quarantine_path"
        )
    )


    # ---------------------------------------------------------
    # Non-quarantine mutations require no quarantine cleanup.
    # ---------------------------------------------------------

    if (
        not isinstance(
            quarantine_path_value,
            str,
        )
        or not quarantine_path_value.strip()
    ):

        return _freeze(
            {
                "quarantine_cleanup_required":
                    False,

                "quarantine_cleanup_performed":
                    False,

                "quarantine_cleanup_verified":
                    True,

                "quarantine_path":
                    None,
            }
        )


    target_store = (
        _require_string(
            handler_result.get(
                "target_store",
                result.get(
                    "target_store"
                ),
            ),
            field_name=(
                "mutation_result.target_store"
            ),
        ).upper()
    )


    if (
        target_store
        not in SUPPORTED_TARGET_STORES
    ):
        raise LifecycleRepairExecutorEngineError(
            "Rollback quarantine result contains "
            "an unsupported target store: "
            + target_store
        )


    # ---------------------------------------------------------
    # Independently reconstruct quarantine boundary.
    # Never trust a stored quarantine path by itself.
    # ---------------------------------------------------------

    quarantine_root = (
        _resolve_quarantine_root_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
        )
    )


    store_quarantine_root = (
        quarantine_root
        / target_store.lower()
    )


    safe_store_quarantine_root = (
        _assert_path_within_root_v1(
            candidate_path=store_quarantine_root,
            allowed_root=quarantine_root,
        )
    )


    quarantine_path = Path(
        quarantine_path_value
    )


    safe_quarantine_path = (
        _assert_path_within_root_v1(
            candidate_path=quarantine_path,
            allowed_root=safe_store_quarantine_root,
        )
    )


    if (
        safe_quarantine_path
        == safe_store_quarantine_root
    ):
        raise LifecycleRepairExecutorEngineError(
            "Rollback quarantine target may not "
            "be the quarantine store root."
        )


    cleanup_performed = False


    if safe_quarantine_path.exists():

        if not safe_quarantine_path.is_file():
            raise LifecycleRepairExecutorEngineError(
                "Quarantine rollback artifact "
                "is not a file."
            )

        safe_quarantine_path.unlink()

        cleanup_performed = True


    cleanup_verified = (
        not safe_quarantine_path.exists()
    )


    if not cleanup_verified:
        raise LifecycleRepairExecutorEngineError(
            "Quarantine rollback cleanup could "
            "not be verified."
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
                    safe_quarantine_path
                ),

            "target_store":
                target_store,
        }
    )


def _rollback_executed_action_v1(
    *,
    project_root: str | Path,
    workspace_id: str,
    backup_record: Mapping[str, Any],
    mutation_result: Mapping[str, Any],
    backup_root: Path,
    workspace_store_root: Path,
) -> Mapping[str, Any]:

    normalized_workspace_id = (
        _require_string(
            workspace_id,
            field_name="workspace_id",
        )
    )

    record = _require_mapping(
        backup_record,
        field_name="backup_record",
    )

    result = _require_mapping(
        mutation_result,
        field_name="mutation_result",
    )


    # ---------------------------------------------------------
    # IMPORTANT ORDER:
    #
    # 1. Restore original target from backup first.
    # 2. Only then remove quarantine copy.
    #
    # If restoration fails, the quarantine artifact remains
    # available as an additional recovery copy.
    # ---------------------------------------------------------

    backup_rollback = (
        _restore_file_backup_v1(
            backup_record=record,
            backup_root=backup_root,
            workspace_store_root=workspace_store_root,
        )
    )


    if (
        backup_rollback[
            "rollback_verified"
        ]
        is not True
    ):
        raise LifecycleRepairExecutorEngineError(
            "Backup rollback could not be verified."
        )


    quarantine_cleanup = (
        _remove_quarantine_artifact_for_rollback_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
            mutation_result=result,
        )
    )


    rollback_verified = all(
        (
            backup_rollback[
                "rollback_verified"
            ]
            is True,

            quarantine_cleanup[
                "quarantine_cleanup_verified"
            ]
            is True,
        )
    )


    return _freeze(
        {
            "schema":
                "body_store_lifecycle_repair_rollback_result.v1",

            "workspace_id":
                normalized_workspace_id,

            "rollback_performed":
                True,

            "rollback_verified":
                rollback_verified,

            "backup_rollback":
                backup_rollback,

            "quarantine_cleanup":
                quarantine_cleanup,

            "mutation_performed":
                False,

            "repair_executed":
                False,
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

    normalized_repair_action_id = (
        _require_string(
            repair_action_id,
            field_name="repair_action_id",
        )
    )

    normalized_source_finding_id = (
        _require_string(
            source_finding_id,
            field_name="source_finding_id",
        )
    )

    normalized_action_type = (
        _assert_supported_executor_action_type_v1(
            repair_action_type
        )
    )

    normalized_target_store = (
        _require_string(
            target_store,
            field_name="target_store",
        ).upper()
    )

    _validate_action_target_store_boundary_v1(
        repair_action_type=normalized_action_type,
        target_store=normalized_target_store,
    )

    normalized_execution_mode = (
        _normalize_execution_mode_v1(
            execution_mode
        )
    )

    normalized_execution_status = (
        _require_string(
            execution_status,
            field_name="execution_status",
        ).upper()
    )


    if (
        normalized_execution_status
        not in EXECUTOR_ACTION_RESULT_STATUSES
    ):
        raise LifecycleRepairExecutorEngineError(
            "Unsupported Executor action result status: "
            + normalized_execution_status
        )


    if not isinstance(
        execution_authorized,
        bool,
    ):
        raise LifecycleRepairExecutorEngineError(
            "execution_authorized must be boolean."
        )


    if not isinstance(
        mutation_attempted,
        bool,
    ):
        raise LifecycleRepairExecutorEngineError(
            "mutation_attempted must be boolean."
        )


    if not isinstance(
        mutation_performed,
        bool,
    ):
        raise LifecycleRepairExecutorEngineError(
            "mutation_performed must be boolean."
        )


    normalized_target_path: str | None = None

    if target_path is not None:

        normalized_target_path = (
            _require_string(
                target_path,
                field_name="target_path",
            )
        )


    # ---------------------------------------------------------
    # Normalize optional records.
    # ---------------------------------------------------------

    normalized_backup_record = (
        _require_mapping(
            backup_record,
            field_name="backup_record",
        )
        if backup_record is not None
        else None
    )


    normalized_mutation_result = (
        _require_mapping(
            mutation_result,
            field_name="mutation_result",
        )
        if mutation_result is not None
        else None
    )


    normalized_rollback_result = (
        _require_mapping(
            rollback_result,
            field_name="rollback_result",
        )
        if rollback_result is not None
        else None
    )


    # ---------------------------------------------------------
    # Result-state consistency.
    # ---------------------------------------------------------

    rollback_performed = (
        normalized_rollback_result is not None
        and normalized_rollback_result.get(
            "rollback_performed"
        )
        is True
    )


    rollback_verified = (
        normalized_rollback_result.get(
            "rollback_verified"
        )
        if normalized_rollback_result is not None
        else None
    )


    backup_created = (
        normalized_backup_record is not None
        and normalized_backup_record.get(
            "backup_created"
        )
        is True
    )


    if (
        normalized_execution_status
        == "DRY_RUN_VALIDATED"
    ):

        if execution_authorized:
            raise LifecycleRepairExecutorEngineError(
                "DRY_RUN action result cannot be "
                "execution-authorized."
            )

        if (
            mutation_attempted
            or mutation_performed
        ):
            raise LifecycleRepairExecutorEngineError(
                "DRY_RUN action result cannot report "
                "a mutation attempt or mutation."
            )


    if (
        normalized_execution_status
        == "EXECUTED"
        and (
            execution_authorized is not True
            or mutation_attempted is not True
            or mutation_performed is not True
            or rollback_performed
        )
    ):
        raise LifecycleRepairExecutorEngineError(
            "EXECUTED action result has an "
            "inconsistent execution state."
        )


    if (
        normalized_execution_status
        == "SKIPPED"
        and mutation_performed
    ):
        raise LifecycleRepairExecutorEngineError(
            "SKIPPED action cannot report a mutation."
        )


    if (
        normalized_execution_status
        in (
            "NOT_EXECUTED",
            "REJECTED",
        )
        and mutation_performed
    ):
        raise LifecycleRepairExecutorEngineError(
            normalized_execution_status
            + " action cannot report a mutation."
        )


    if (
        rollback_performed
        and rollback_verified is not True
    ):
        # We still allow FAILED results to record an
        # unsuccessful rollback, but never describe the repair
        # itself as successfully executed.
        repair_executed = False

    else:

        repair_executed = all(
            (
                normalized_execution_status
                == "EXECUTED",

                execution_authorized,
                mutation_attempted,
                mutation_performed,

                not rollback_performed,
            )
        )


    normalized_failure_reason: str | None = None

    if failure_reason is not None:

        normalized_failure_reason = (
            _require_string(
                failure_reason,
                field_name="failure_reason",
            )
        )


    if (
        normalized_execution_status
        == "FAILED"
        and normalized_failure_reason is None
    ):
        raise LifecycleRepairExecutorEngineError(
            "FAILED action result requires "
            "a failure_reason."
        )


    result = {
        "schema":
            BODY_STORE_LIFECYCLE_REPAIR_ACTION_RESULT_SCHEMA,

        "executor_engine_schema":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_SCHEMA,

        "executor_engine_version":
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_VERSION,

        "repair_action_id":
            normalized_repair_action_id,

        "source_finding_id":
            normalized_source_finding_id,

        "repair_action_type":
            normalized_action_type,

        "target_store":
            normalized_target_store,

        "target_path":
            normalized_target_path,

        "execution_mode":
            normalized_execution_mode,

        "execution_status":
            normalized_execution_status,

        "execution_authorized":
            execution_authorized,

        "mutation_attempted":
            mutation_attempted,

        "mutation_performed":
            mutation_performed,

        "backup_created":
            backup_created,

        "backup_record":
            normalized_backup_record,

        "rollback_required":
            normalized_rollback_result
            is not None,

        "rollback_performed":
            rollback_performed,

        "rollback_verified":
            rollback_verified,

        "rollback_result":
            normalized_rollback_result,

        "mutation_result":
            normalized_mutation_result,

        "failure_reason":
            normalized_failure_reason,

        "repair_executed":
            repair_executed,

        "runtime_job_created":
            False,

        "queue_job_created":
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
def _build_expected_quarantine_rollback_stub_v1(
    *,
    project_root: str | Path,
    workspace_id: str,
    target_store: str,
    target_path: Path,
    workspace_store_root: Path,
) -> Mapping[str, Any]:

    normalized_workspace_id = (
        _require_string(
            workspace_id,
            field_name="workspace_id",
        )
    )

    normalized_target_store = (
        _require_string(
            target_store,
            field_name="target_store",
        ).upper()
    )

    if (
        normalized_target_store
        not in SUPPORTED_TARGET_STORES
    ):
        raise LifecycleRepairExecutorEngineError(
            "Unsupported target store for quarantine "
            "rollback preparation: "
            + normalized_target_store
        )

    safe_target_path = (
        _assert_path_within_root_v1(
            candidate_path=target_path,
            allowed_root=workspace_store_root,
        )
    )

    relative_target_path = (
        safe_target_path.relative_to(
            workspace_store_root.resolve(
                strict=False
            )
        )
    )

    quarantine_root = (
        _resolve_quarantine_root_v1(
            project_root=project_root,
            workspace_id=normalized_workspace_id,
        )
    )

    store_quarantine_root = (
        quarantine_root
        / normalized_target_store.lower()
    )

    safe_store_quarantine_root = (
        _assert_path_within_root_v1(
            candidate_path=store_quarantine_root,
            allowed_root=quarantine_root,
        )
    )

    quarantine_path = (
        safe_store_quarantine_root
        / relative_target_path
    )

    safe_quarantine_path = (
        _assert_path_within_root_v1(
            candidate_path=quarantine_path,
            allowed_root=safe_store_quarantine_root,
        )
    )

    return _freeze(
        {
            "target_store":
                normalized_target_store,

            "quarantine_path":
                str(
                    safe_quarantine_path
                ),

            "mutation_performed":
                False,

            "rollback_stub":
                True,
        }
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

    plan = _require_mapping(
        repair_plan,
        field_name="repair_plan",
    )

    request = _require_mapping(
        execution_request,
        field_name="execution_request",
    )

    execution_mode = (
        _normalize_execution_mode_v1(
            request.get(
                "execution_mode"
            )
        )
    )

    workspace_id = (
        _require_string(
            request.get(
                "workspace_id"
            ),
            field_name=(
                "execution_request.workspace_id"
            ),
        )
    )

    execution_request_id = (
        _require_string(
            request.get(
                "execution_request_id"
            ),
            field_name=(
                "execution_request.execution_request_id"
            ),
        )
    )


    # =========================================================
    # 1. PREPARE EXECUTION
    # =========================================================

    preflight = (
        prepare_lifecycle_repair_execution_v1(
            project_root=project_root,
            repair_plan=plan,
            planner_certification=planner_certification,
            authorization=authorization,
            execution_request=request,
            findings=findings,
        )
    )


    # =========================================================
    # 2. INDEPENDENT PREFLIGHT VALIDATION
    # =========================================================

    preflight_validation = (
        validate_lifecycle_repair_execution_preflight_v1(
            project_root=project_root,
            preflight=preflight,
        )
    )


    if (
        preflight_validation[
            "preflight_valid"
        ]
        is not True
    ):
        raise LifecycleRepairExecutorEngineError(
            "Lifecycle Repair Executor preflight "
            "validation failed."
        )


    if (
        _validate_preflight_checksum_v1(
            preflight=preflight,
        )
        is not True
    ):
        raise LifecycleRepairExecutorEngineError(
            "Lifecycle Repair Executor preflight "
            "checksum validation failed."
        )


    prepared_actions = tuple(
        preflight[
            "prepared_actions"
        ]
    )


    if not prepared_actions:
        raise LifecycleRepairExecutorEngineError(
            "Executor preflight produced no prepared actions."
        )


    # =========================================================
    # 3. DRY RUN
    # =========================================================

    if execution_mode == "DRY_RUN":

        dry_run_results: list[
            Mapping[str, Any]
        ] = []


        for prepared_action in prepared_actions:

            action = _require_mapping(
                prepared_action,
                field_name="prepared_action",
            )


            # -------------------------------------------------
            # Even a dry run must not report against a target
            # that changed after preflight.
            #
            # This remains fully read-only.
            # -------------------------------------------------

            transaction_gate = (
                _verify_prepared_action_transaction_gate_v1(
                    project_root=project_root,
                    workspace_id=workspace_id,
                    prepared_action=action,
                )
            )


            if (
                transaction_gate[
                    "gate_passed"
                ]
                is not True
            ):
                raise LifecycleRepairExecutorEngineError(
                    "DRY_RUN transaction gate failed for "
                    "repair action: "
                    + str(
                        action.get(
                            "repair_action_id"
                        )
                    )
                )


            mutation_intent = (
                _require_mapping(
                    action.get(
                        "mutation_intent"
                    ),
                    field_name=(
                        "prepared_action.mutation_intent"
                    ),
                )
            )


            dry_run_result = (
                _build_dry_run_action_result_v1(
                    repair_action={
                        "repair_action_id":
                            action[
                                "repair_action_id"
                            ],

                        "repair_action_type":
                            action[
                                "repair_action_type"
                            ],
                    },
                    source_finding={
                        "finding_id":
                            action[
                                "source_finding_id"
                            ],
                    },
                    target_store=(
                        mutation_intent[
                            "target_store"
                        ]
                    ),
                    target_path=(
                        mutation_intent[
                            "target_path"
                        ]
                    ),
                )
            )


            dry_run_results.append(
                dry_run_result
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
                plan.get(
                    "repair_plan_id"
                ),

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

            "committed_mutation_count":
                0,

            "dry_run_validated_action_count":
                len(
                    dry_run_results
                ),

            "skipped_action_count":
                0,

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

            "mutation_outcome_uncertain_action_ids":
                (),

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


    # =========================================================
    # 4. AUTHORIZED APPLY ONLY BEYOND THIS POINT
    # =========================================================

    if execution_mode != "AUTHORIZED_APPLY":

        raise LifecycleRepairExecutorEngineError(
            "Unsupported execution mode: "
            + execution_mode
        )


    authorization_item = (
        _require_mapping(
            authorization,
            field_name="authorization",
        )
    )


    if (
        authorization_item.get(
            "authorization_state"
        )
        != "AUTHORIZED"
    ):
        raise LifecycleRepairExecutorEngineError(
            "AUTHORIZED_APPLY requires an "
            "AUTHORIZED authorization state."
        )


    if (
        authorization_item.get(
            "explicitly_authorized"
        )
        is not True
    ):
        raise LifecycleRepairExecutorEngineError(
            "AUTHORIZED_APPLY requires explicit "
            "execution authorization."
        )


    # =========================================================
    # 5. TRANSACTION FOUNDATION
    # =========================================================

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


    transaction_stack: list[
        dict[str, Any]
    ] = []


    transaction_entries_by_action_id: dict[
        str,
        dict[str, Any],
    ] = {}


    failed_action_id: str | None = None

    failure_reason: str | None = None


    current_action_id: str | None = None

    current_source_finding_id: str | None = None

    current_action_type: str | None = None

    current_target_store: str | None = None

    current_target_path: str | None = None

    current_transaction_entry: (
        dict[str, Any]
        | None
    ) = None


    # =========================================================
    # 6. AUTHORIZED TRANSACTION LOOP
    # =========================================================

    try:

        for prepared_action in prepared_actions:

            action = _require_mapping(
                prepared_action,
                field_name="prepared_action",
            )


            current_action_id = (
                _require_string(
                    action.get(
                        "repair_action_id"
                    ),
                    field_name=(
                        "prepared_action.repair_action_id"
                    ),
                )
            )


            current_source_finding_id = (
                _require_string(
                    action.get(
                        "source_finding_id"
                    ),
                    field_name=(
                        "prepared_action.source_finding_id"
                    ),
                )
            )


            current_action_type = (
                _assert_supported_executor_action_type_v1(
                    action.get(
                        "repair_action_type"
                    )
                )
            )


            mutation_intent = (
                _require_mapping(
                    action.get(
                        "mutation_intent"
                    ),
                    field_name=(
                        "prepared_action.mutation_intent"
                    ),
                )
            )


            current_target_store = (
                _require_string(
                    mutation_intent.get(
                        "target_store"
                    ),
                    field_name=(
                        "mutation_intent.target_store"
                    ),
                ).upper()
            )


            current_target_path = (
                _require_string(
                    mutation_intent.get(
                        "target_path"
                    ),
                    field_name=(
                        "mutation_intent.target_path"
                    ),
                )
            )


            # -------------------------------------------------
            # 6A. Final transaction gate immediately before
            # backup/mutation.
            # -------------------------------------------------

            transaction_gate = (
                _verify_prepared_action_transaction_gate_v1(
                    project_root=project_root,
                    workspace_id=workspace_id,
                    prepared_action=action,
                )
            )


            if (
                transaction_gate[
                    "gate_passed"
                ]
                is not True
            ):
                raise LifecycleRepairExecutorEngineError(
                    "Final transaction gate failed "
                    "for repair action: "
                    + current_action_id
                )


            # -------------------------------------------------
            # 6A.1. Content-specific safety validation before backup.
            #
            # CONTROLLED_JSON_REBUILD replacement content must
            # cross its complete action/store/workspace/content
            # boundary BEFORE _create_file_backup_v1() is allowed.
            #
            # This prevents an invalid replacement action from
            # creating any transaction backup artifact before the
            # action itself is proven safe to execute.
            # -------------------------------------------------

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

                    raise LifecycleRepairExecutorEngineError(
                        "CONTROLLED_JSON_REBUILD failed "
                        "pre-backup content safety: "
                        "replacement_record is missing "
                        "or is not a mapping."
                    )


                replacement_validation = (
                    _validate_controlled_replacement_record_v1(
                        repair_action_type=(
                            current_action_type
                        ),
                        target_store=(
                            current_target_store
                        ),
                        replacement_record=(
                            replacement_record
                        ),
                        workspace_id=(
                            workspace_id
                        ),
                    )
                )


                if (
                    replacement_validation[
                        "replacement_record_valid"
                    ]
                    is not True
                ):

                    raise LifecycleRepairExecutorEngineError(
                        "CONTROLLED_JSON_REBUILD failed "
                        "pre-backup content safety."
                    )


            # -------------------------------------------------
            # 6B. Independently reconstruct store root again.
            # -------------------------------------------------

            workspace_store_root = (
                _resolve_verified_workspace_store_root_v1(
                    project_root=project_root,
                    workspace_id=workspace_id,
                    target_store=current_target_store,
                )
            )


            target_path = (
                _assert_path_within_root_v1(
                    candidate_path=Path(
                        current_target_path
                    ),
                    allowed_root=workspace_store_root,
                )
            )


            if target_path == workspace_store_root:

                raise LifecycleRepairExecutorEngineError(
                    "Repair action attempted to target "
                    "the workspace store root itself."
                )


            # -------------------------------------------------
            # 6C. Create per-store backup root.
            # -------------------------------------------------

            action_backup_root = (
                backup_root
                / current_target_store.lower()
            )


            action_backup_root = (
                _assert_path_within_root_v1(
                    candidate_path=action_backup_root,
                    allowed_root=backup_root,
                )
            )


            # -------------------------------------------------
            # 6D. Backup BEFORE any mutation attempt.
            #
            # Missing targets are recorded as source_existed
            # False so rollback can remove newly created files.
            # -------------------------------------------------

            backup_record = (
                _create_file_backup_v1(
                    source_path=target_path,
                    backup_root=action_backup_root,
                    workspace_store_root=workspace_store_root,
                )
            )


            # -------------------------------------------------
            # 6E. Prepare conservative rollback metadata.
            #
            # For quarantine, calculate the expected
            # quarantine path before mutation begins.
            # -------------------------------------------------

            expected_mutation_result: Mapping[
                str,
                Any,
            ] = _freeze(
                {
                    "target_store":
                        current_target_store,

                    "mutation_performed":
                        False,
                }
            )


            if (
                mutation_intent.get(
                    "execution_strategy"
                )
                == "QUARANTINE_FILE"
            ):

                expected_mutation_result = (
                    _build_expected_quarantine_rollback_stub_v1(
                        project_root=project_root,
                        workspace_id=workspace_id,
                        target_store=current_target_store,
                        target_path=target_path,
                        workspace_store_root=workspace_store_root,
                    )
                )


            # -------------------------------------------------
            # 6F. Register current action BEFORE mutation.
            #
            # This is critical:
            # if the handler throws halfway through mutation,
            # this action is already in the rollback stack.
            # -------------------------------------------------

            transaction_entry: dict[
                str,
                Any,
            ] = {
                "repair_action_id":
                    current_action_id,

                "source_finding_id":
                    current_source_finding_id,

                "repair_action_type":
                    current_action_type,

                "target_store":
                    current_target_store,

                "target_path":
                    str(
                        target_path
                    ),

                "workspace_store_root":
                    workspace_store_root,

                "backup_root":
                    action_backup_root,

                "backup_record":
                    backup_record,

                "mutation_result":
                    expected_mutation_result,

                "mutation_attempted":
                    False,

                "mutation_completed":
                    False,

                "mutation_performed":
                    False,
            }


            current_transaction_entry = (
                transaction_entry
            )


            transaction_stack.append(
                transaction_entry
            )


            transaction_entries_by_action_id[
                current_action_id
            ] = transaction_entry


            # -------------------------------------------------
            # 6G. Mutation begins.
            # -------------------------------------------------

            transaction_entry[
                "mutation_attempted"
            ] = True


            mutation_result = (
                _dispatch_authorized_mutation_v1(
                    project_root=project_root,
                    workspace_id=workspace_id,
                    mutation_intent=mutation_intent,
                    execution_authorized=True,
                )
            )


            transaction_entry[
                "mutation_result"
            ] = mutation_result


            transaction_entry[
                "mutation_completed"
            ] = True


            mutation_performed = (
                mutation_result.get(
                    "mutation_performed"
                )
                is True
            )


            transaction_entry[
                "mutation_performed"
            ] = mutation_performed


            execution_status = (
                "EXECUTED"
                if mutation_performed
                else "SKIPPED"
            )


            action_result = (
                _build_executor_action_result_v1(
                    repair_action_id=(
                        current_action_id
                    ),
                    source_finding_id=(
                        current_source_finding_id
                    ),
                    repair_action_type=(
                        current_action_type
                    ),
                    target_store=(
                        current_target_store
                    ),
                    target_path=(
                        str(
                            target_path
                        )
                    ),
                    execution_mode=(
                        "AUTHORIZED_APPLY"
                    ),
                    execution_status=(
                        execution_status
                    ),
                    execution_authorized=True,
                    mutation_attempted=True,
                    mutation_performed=(
                        mutation_performed
                    ),
                    backup_record=(
                        backup_record
                    ),
                    mutation_result=(
                        mutation_result
                    ),
                )
            )


            action_results.append(
                action_result
            )


            # -------------------------------------------------
            # No-op actions changed nothing.
            # They must not remain in rollback stack.
            # -------------------------------------------------

            if not mutation_performed:

                transaction_stack.pop()

                transaction_entries_by_action_id.pop(
                    current_action_id,
                    None,
                )


            current_transaction_entry = None


    # =========================================================
    # 7. FAILURE → TRANSACTION ROLLBACK
    # =========================================================

    except Exception as exc:

        failed_action_id = (
            current_action_id
        )


        failure_reason = str(
            exc
        )


        rollback_results: list[
            Mapping[str, Any]
        ] = []


        rollback_failures: list[
            str
        ] = []


        rollback_by_action_id: dict[
            str,
            Mapping[str, Any],
        ] = {}


        mutation_outcome_uncertain_action_ids: list[
            str
        ] = []


        # -----------------------------------------------------
        # If a mutation handler threw before returning,
        # mutation completion cannot be trusted.
        # -----------------------------------------------------

        for transaction_entry in (
            transaction_stack
        ):

            if (
                transaction_entry.get(
                    "mutation_attempted"
                )
                is True
                and transaction_entry.get(
                    "mutation_completed"
                )
                is not True
            ):

                mutation_outcome_uncertain_action_ids.append(
                    transaction_entry[
                        "repair_action_id"
                    ]
                )


        # -----------------------------------------------------
        # Roll back in reverse mutation order.
        # -----------------------------------------------------

        for transaction_entry in reversed(
            transaction_stack
        ):

            rollback_action_id = (
                transaction_entry[
                    "repair_action_id"
                ]
            )


            try:

                rollback_result = (
                    _rollback_executed_action_v1(
                        project_root=project_root,
                        workspace_id=workspace_id,
                        backup_record=(
                            transaction_entry[
                                "backup_record"
                            ]
                        ),
                        mutation_result=(
                            transaction_entry[
                                "mutation_result"
                            ]
                        ),
                        backup_root=(
                            transaction_entry[
                                "backup_root"
                            ]
                        ),
                        workspace_store_root=(
                            transaction_entry[
                                "workspace_store_root"
                            ]
                        ),
                    )
                )


                rollback_by_action_id[
                    rollback_action_id
                ] = rollback_result


                rollback_results.append(
                    _freeze(
                        {
                            "repair_action_id":
                                rollback_action_id,

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
                        rollback_action_id
                    )


            except Exception as rollback_exc:

                rollback_failures.append(
                    rollback_action_id
                    + ": "
                    + str(
                        rollback_exc
                    )
                )


        rollback_required = bool(
            transaction_stack
        )


        rollback_performed = bool(
            rollback_results
        )


        if rollback_required:

            rollback_verified: bool | None = (
                not rollback_failures
                and len(
                    rollback_results
                )
                == len(
                    transaction_stack
                )
                and all(
                    rollback_item[
                        "rollback_result"
                    ][
                        "rollback_verified"
                    ]
                    is True

                    for rollback_item
                    in rollback_results
                )
            )

        else:

            rollback_verified = None


        # =====================================================
        # 7A. TRANSACTION BACKUP LIFECYCLE
        #
        # Backups are disposable only when:
        #
        # - there was no rollback requirement, or
        # - every required rollback was verified.
        #
        # An unverified rollback MUST preserve backups.
        # =====================================================

        if (
            rollback_required
            and rollback_verified
            is not True
        ):

            backup_root_exists = (
                backup_root.exists()
            )

            backup_cleanup = _freeze(
                {
                    "backup_cleanup_required":
                        backup_root_exists,

                    "backup_cleanup_performed":
                        False,

                    "backup_cleanup_verified":
                        not backup_root_exists,

                    "backup_preserved_for_recovery":
                        backup_root_exists,

                    "backup_root":
                        str(
                            backup_root
                        ),

                    "cleanup_failure_reason":
                        (
                            "BACKUP_PRESERVED_DUE_TO_"
                            "UNVERIFIED_ROLLBACK"
                            if backup_root_exists
                            else None
                        ),
                }
            )

        else:

            backup_cleanup = (
                _cleanup_executor_backup_root_v1(
                    project_root=project_root,
                    workspace_id=workspace_id,
                    execution_request_id=(
                        execution_request_id
                    ),
                )
            )


        # =====================================================
        # 8. REBUILD PRIOR ACTION RESULTS THAT WERE ROLLED BACK
        # =====================================================

        rebuilt_action_results: list[
            Mapping[str, Any]
        ] = []


        existing_result_ids: set[
            str
        ] = set()


        for existing_result in action_results:

            existing_action_id = (
                existing_result[
                    "repair_action_id"
                ]
            )


            existing_result_ids.add(
                existing_action_id
            )


            rollback_result = (
                rollback_by_action_id.get(
                    existing_action_id
                )
            )


            if rollback_result is None:

                rebuilt_action_results.append(
                    existing_result
                )

                continue


            transaction_entry = (
                transaction_entries_by_action_id[
                    existing_action_id
                ]
            )


            rebuilt_action_results.append(
                _build_executor_action_result_v1(
                    repair_action_id=(
                        existing_action_id
                    ),
                    source_finding_id=(
                        transaction_entry[
                            "source_finding_id"
                        ]
                    ),
                    repair_action_type=(
                        transaction_entry[
                            "repair_action_type"
                        ]
                    ),
                    target_store=(
                        transaction_entry[
                            "target_store"
                        ]
                    ),
                    target_path=(
                        transaction_entry[
                            "target_path"
                        ]
                    ),
                    execution_mode=(
                        "AUTHORIZED_APPLY"
                    ),
                    execution_status="FAILED",
                    execution_authorized=True,
                    mutation_attempted=(
                        transaction_entry[
                            "mutation_attempted"
                        ]
                        is True
                    ),
                    mutation_performed=(
                        transaction_entry[
                            "mutation_performed"
                        ]
                        is True
                    ),
                    backup_record=(
                        transaction_entry[
                            "backup_record"
                        ]
                    ),
                    mutation_result=(
                        transaction_entry[
                            "mutation_result"
                        ]
                    ),
                    rollback_result=(
                        rollback_result
                    ),
                    failure_reason=(
                        "Transaction rolled back because "
                        "repair action "
                        + str(
                            failed_action_id
                        )
                        + " failed: "
                        + failure_reason
                    ),
                )
            )


        # =====================================================
        # 9. ADD FAILED CURRENT ACTION IF IT NEVER PRODUCED
        # AN ACTION RESULT
        # =====================================================

        if (
            failed_action_id is not None
            and failed_action_id
            not in existing_result_ids
            and current_source_finding_id
            is not None
            and current_action_type
            is not None
            and current_target_store
            is not None
        ):

            failed_transaction_entry = (
                transaction_entries_by_action_id.get(
                    failed_action_id
                )
            )


            if failed_transaction_entry is not None:

                failed_rollback_result = (
                    rollback_by_action_id.get(
                        failed_action_id
                    )
                )


                rebuilt_action_results.append(
                    _build_executor_action_result_v1(
                        repair_action_id=(
                            failed_action_id
                        ),
                        source_finding_id=(
                            current_source_finding_id
                        ),
                        repair_action_type=(
                            current_action_type
                        ),
                        target_store=(
                            current_target_store
                        ),
                        target_path=(
                            failed_transaction_entry[
                                "target_path"
                            ]
                        ),
                        execution_mode=(
                            "AUTHORIZED_APPLY"
                        ),
                        execution_status="FAILED",
                        execution_authorized=True,
                        mutation_attempted=(
                            failed_transaction_entry[
                                "mutation_attempted"
                            ]
                            is True
                        ),
                        mutation_performed=(
                            failed_transaction_entry[
                                "mutation_performed"
                            ]
                            is True
                        ),
                        backup_record=(
                            failed_transaction_entry[
                                "backup_record"
                            ]
                        ),
                        mutation_result=(
                            failed_transaction_entry[
                                "mutation_result"
                            ]
                        ),
                        rollback_result=(
                            failed_rollback_result
                        ),
                        failure_reason=(
                            failure_reason
                        ),
                    )
                )


            else:

                # Failure occurred before backup/mutation.
                rebuilt_action_results.append(
                    _build_executor_action_result_v1(
                        repair_action_id=(
                            failed_action_id
                        ),
                        source_finding_id=(
                            current_source_finding_id
                        ),
                        repair_action_type=(
                            current_action_type
                        ),
                        target_store=(
                            current_target_store
                        ),
                        target_path=(
                            current_target_path
                        ),
                        execution_mode=(
                            "AUTHORIZED_APPLY"
                        ),
                        execution_status="FAILED",
                        execution_authorized=True,
                        mutation_attempted=False,
                        mutation_performed=False,
                        failure_reason=(
                            failure_reason
                        ),
                    )
                )


        # =====================================================
        # 10. TRANSACTION FAILURE RESULT
        # =====================================================

        persistent_mutation_possible = (
            rollback_required
            and rollback_verified
            is not True
        )


        failed_result = {
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
                plan.get(
                    "repair_plan_id"
                ),

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

            "completed_action_result_count":
                len(
                    action_results
                ),

            "failed_action_count":
                1,

            "committed_mutation_count":
                0,

            "rolled_back_action_count":
                len(
                    rollback_results
                ),

            "action_results":
                tuple(
                    rebuilt_action_results
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

            # True here means an unverified mutation may still
            # remain after a rollback failure.
            "mutation_performed":
                persistent_mutation_possible,

            "rollback_required":
                rollback_required,

            "rollback_performed":
                rollback_performed,

            "rollback_verified":
                rollback_verified,

            "backup_cleanup":
                backup_cleanup,

            "backup_cleanup_verified":
                backup_cleanup[
                    "backup_cleanup_verified"
                ]
                is True,

            "backup_preserved_for_recovery":
                backup_cleanup[
                    "backup_preserved_for_recovery"
                ]
                is True,

            "mutation_outcome_uncertain_action_ids":
                tuple(
                    mutation_outcome_uncertain_action_ids
                ),

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


    # =========================================================
    # 11. SUCCESSFUL AUTHORIZED TRANSACTION
    # =========================================================

    committed_mutations = sum(
        1

        for action_result
        in action_results

        if action_result.get(
            "mutation_performed"
        )
        is True
    )


    skipped_actions = sum(
        1

        for action_result
        in action_results

        if action_result.get(
            "execution_status"
        )
        == "SKIPPED"
    )


    executed_actions = sum(
        1

        for action_result
        in action_results

        if action_result.get(
            "execution_status"
        )
        == "EXECUTED"
    )


    # =========================================================
    # 11A. SUCCESSFUL TRANSACTION BACKUP CLEANUP
    #
    # Transaction backups are no longer recovery-authoritative
    # after a fully successful authorized transaction.
    # =========================================================

    backup_cleanup = (
        _cleanup_executor_backup_root_v1(
            project_root=project_root,
            workspace_id=workspace_id,
            execution_request_id=(
                execution_request_id
            ),
        )
    )


    successful_result = {
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
            plan.get(
                "repair_plan_id"
            ),

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
            executed_actions,

        "skipped_action_count":
            skipped_actions,

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

        "backup_cleanup":
            backup_cleanup,

        "backup_cleanup_verified":
            backup_cleanup[
                "backup_cleanup_verified"
            ]
            is True,

        "backup_preserved_for_recovery":
            backup_cleanup[
                "backup_preserved_for_recovery"
            ]
            is True,

        "mutation_outcome_uncertain_action_ids":
            (),

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
def summarize_lifecycle_repair_executor_engine_v1(
) -> Mapping[str, Any]:

    return _freeze(
        {
            "schema":
                BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_SCHEMA,

            "version":
                BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_VERSION,

            "executor_contract_version":
                BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_VERSION,

            "execution_modes":
                EXECUTOR_EXECUTION_MODES,

            "supported_executor_action_types":
                tuple(
                    SUPPORTED_EXECUTOR_ACTION_TYPES
                ),

            "non_executable_planner_action_types":
                tuple(
                    NON_EXECUTABLE_PLANNER_ACTION_TYPES
                ),

            "prohibited_direct_execution_action_types":
                tuple(
                    PROHIBITED_DIRECT_EXECUTION_ACTION_TYPES
                ),

            "supported_target_stores":
                SUPPORTED_TARGET_STORES,

            "canonical_lifecycle_states":
                CANONICAL_LIFECYCLE_STATES,

            "required_safety_gates":
                ENGINE_REQUIRED_SAFETY_GATES,

            "repair_action_strategies":
                ACTION_EXECUTION_STRATEGIES,

            "action_allowed_target_stores":
                ACTION_ALLOWED_TARGET_STORES,

            "dry_run_supported":
                True,

            "authorized_apply_supported":
                True,

            "explicit_authorization_required_for_apply":
                True,

            "preflight_required":
                True,

            "target_change_detection_enabled":
                True,

            "backup_before_mutation":
                True,

            "transaction_rollback_supported":
                True,

            "quarantine_copy_before_source_removal":
                True,

            "tombstone_content_boundary_enforced":
                True,

            "metadata_body_boundary_enforced":
                True,

            "path_containment_enforced":
                True,

            "atomic_json_write_enabled":
                True,

            "runtime_job_creation":
                False,

            "queue_job_creation":
                False,
        }
    )


__all__ = (
    "BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_SCHEMA",
    "BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_ENGINE_VERSION",
    "ENGINE_REQUIRED_SAFETY_GATES",
    "SUPPORTED_TARGET_STORES",
    "EXECUTOR_STORE_DIRECTORY_NAMES",
    "EXECUTOR_EXECUTION_MODES",
    "EXECUTOR_MUTATION_POLICY",
    "CANONICAL_LIFECYCLE_STATES",
    "ACTION_EXECUTION_STRATEGIES",
    "ACTION_TARGET_STORE",
    "ACTION_ALLOWED_TARGET_STORES",
    "DYNAMIC_TARGET_STORE_ACTION_TYPES",
    "METADATA_ONLY_REPAIR_ACTION_TYPES",
    "TOMBSTONE_PROHIBITED_CONTENT_FIELDS",
    "LifecycleRepairExecutorEngineError",
    "calculate_lifecycle_repair_executor_engine_checksum_v1",
    "validate_lifecycle_repair_execution_context_v1",
    "prepare_lifecycle_repair_execution_v1",
    "validate_lifecycle_repair_execution_preflight_v1",
    "execute_lifecycle_repair_plan_v1",
    "summarize_lifecycle_repair_executor_engine_v1",
)
