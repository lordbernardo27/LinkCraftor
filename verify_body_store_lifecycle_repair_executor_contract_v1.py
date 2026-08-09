from __future__ import annotations

import hashlib
import sys
from pathlib import Path


PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

if str(
    PROJECT_ROOT
) not in sys.path:
    sys.path.insert(
        0,
        str(
            PROJECT_ROOT
        ),
    )


from backend.server.universal_article_body_store.body_store_lifecycle_repair_executor_contract_v1 import (
    BODY_STORE_LIFECYCLE_REPAIR_ACTION_RESULT_SCHEMA,
    BODY_STORE_LIFECYCLE_REPAIR_EXECUTION_AUTHORIZATION_SCHEMA,
    BODY_STORE_LIFECYCLE_REPAIR_EXECUTION_REQUEST_SCHEMA,
    BODY_STORE_LIFECYCLE_REPAIR_EXECUTION_RESULT_SCHEMA,
    BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_SCHEMA,
    BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_VERSION,
    NON_EXECUTABLE_PLANNER_ACTION_TYPES,
    PROHIBITED_DIRECT_EXECUTION_ACTION_TYPES,
    REQUIRED_EXECUTION_SAFETY_GATES,
    SUPPORTED_ACTION_EXECUTION_STATUSES,
    SUPPORTED_AUTHORIZATION_STATES,
    SUPPORTED_EXECUTION_MODES,
    SUPPORTED_EXECUTOR_ACTION_TYPES,
    LifecycleRepairExecutorContractError,
    calculate_lifecycle_repair_executor_checksum_v1,
    certify_lifecycle_repair_executor_contract_v1,
    create_lifecycle_repair_execution_authorization_v1,
    create_lifecycle_repair_execution_request_v1,
    summarize_lifecycle_repair_executor_contract_v1,
    validate_lifecycle_repair_execution_authorization_v1,
    validate_lifecycle_repair_execution_request_v1,
)


DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)


PROTECTED = {
    "body_store":
        DATA_ROOT
        / "universal_article_body_store",

    "queue":
        DATA_ROOT
        / "universal_knowledge_queue",

    "lifecycle":
        DATA_ROOT
        / "universal_article_body_store_lifecycle",

    "archive_store":
        DATA_ROOT
        / "universal_article_body_store_archive",

    "tombstone_store":
        DATA_ROOT
        / "universal_article_body_store_tombstones",

    "uucd":
        DATA_ROOT
        / "universal_unified_content_document",

    "wuc":
        DATA_ROOT
        / "website_unified_content",
}


def fingerprint(
    path: Path,
) -> str:

    if not path.exists():
        return "ABSENT"

    digest = hashlib.sha256()

    if path.is_file():
        digest.update(
            path.name.encode(
                "utf-8"
            )
        )

        digest.update(
            path.read_bytes()
        )

        return digest.hexdigest()

    files = sorted(
        item
        for item in path.rglob(
            "*"
        )
        if item.is_file()
    )

    for file_path in files:
        relative_path = file_path.relative_to(
            path
        )

        digest.update(
            str(
                relative_path
            ).replace(
                "\\",
                "/",
            ).encode(
                "utf-8"
            )
        )

        digest.update(
            file_path.read_bytes()
        )

    return digest.hexdigest()


before = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED.items()
}


REPAIR_PLAN_ID = (
    "repair_plan_executor_contract_verify_v1"
)

REPAIR_PLAN_CHECKSUM = (
    "7a8660eb8e734732865f189cf5f3380d"
    "cb0fc79ade578f4597acecf51ce5ec89"
)

PLANNER_CERTIFICATION_ID = (
    "repair_planner_certification_executor_verify_v1"
)

PLANNER_CERTIFICATION_CHECKSUM = (
    "52b40e55873c46199c953988caad5fa4"
    "78988e64f1fd14a1f25736ef095cd926"
)

ACTION_ID_1 = (
    "repair_action_executor_verify_001"
)

ACTION_ID_2 = (
    "repair_action_executor_verify_002"
)


authorized_apply_authorization = (
    create_lifecycle_repair_execution_authorization_v1(
        authorization_id=(
            "executor_contract_authorization_apply_v1"
        ),
        workspace_id="ws_verify",
        repair_plan_id=REPAIR_PLAN_ID,
        repair_plan_checksum=REPAIR_PLAN_CHECKSUM,
        planner_certification_id=(
            PLANNER_CERTIFICATION_ID
        ),
        planner_certification_checksum=(
            PLANNER_CERTIFICATION_CHECKSUM
        ),
        authorization_state="AUTHORIZED",
        authorized_action_ids=(
            ACTION_ID_1,
            ACTION_ID_2,
        ),
        authorized_by=(
            "contract_verification_authority"
        ),
        authorization_reason=(
            "Controlled Executor Contract verification."
        ),
    )
)


authorized_apply_request = (
    create_lifecycle_repair_execution_request_v1(
        execution_request_id=(
            "executor_contract_apply_request_v1"
        ),
        workspace_id="ws_verify",
        repair_plan_id=REPAIR_PLAN_ID,
        repair_plan_checksum=REPAIR_PLAN_CHECKSUM,
        planner_certification_id=(
            PLANNER_CERTIFICATION_ID
        ),
        planner_certification_checksum=(
            PLANNER_CERTIFICATION_CHECKSUM
        ),
        authorization_id=(
            authorized_apply_authorization[
                "authorization_id"
            ]
        ),
        authorization_checksum=(
            authorized_apply_authorization[
                "authorization_checksum"
            ]
        ),
        execution_mode="AUTHORIZED_APPLY",
        requested_action_ids=(
            ACTION_ID_1,
            ACTION_ID_2,
        ),

        require_all_actions_authorized=True,
    )
)


dry_run_authorization = (
    create_lifecycle_repair_execution_authorization_v1(
        authorization_id=(
            "executor_contract_authorization_dry_run_v1"
        ),
        workspace_id="ws_verify",
        repair_plan_id=REPAIR_PLAN_ID,
        repair_plan_checksum=REPAIR_PLAN_CHECKSUM,
        planner_certification_id=(
            PLANNER_CERTIFICATION_ID
        ),
        planner_certification_checksum=(
            PLANNER_CERTIFICATION_CHECKSUM
        ),
        authorization_state="AUTHORIZED",
        authorized_action_ids=(
            ACTION_ID_1,
        ),
        authorized_by=(
            "contract_verification_authority"
        ),
        authorization_reason=(
            "Controlled dry-run verification."
        ),
    )
)


dry_run_request = (
    create_lifecycle_repair_execution_request_v1(
        execution_request_id=(
            "executor_contract_dry_run_request_v1"
        ),
        workspace_id="ws_verify",
        repair_plan_id=REPAIR_PLAN_ID,
        repair_plan_checksum=REPAIR_PLAN_CHECKSUM,
        planner_certification_id=(
            PLANNER_CERTIFICATION_ID
        ),
        planner_certification_checksum=(
            PLANNER_CERTIFICATION_CHECKSUM
        ),
        authorization_id=(
            dry_run_authorization[
                "authorization_id"
            ]
        ),
        authorization_checksum=(
            dry_run_authorization[
                "authorization_checksum"
            ]
        ),
        execution_mode="DRY_RUN",
        requested_action_ids=(
            ACTION_ID_1,
        ),
        require_all_actions_authorized=True,
    )
)


rejected_authorization = (
    create_lifecycle_repair_execution_authorization_v1(
        authorization_id=(
            "executor_contract_authorization_rejected_v1"
        ),
        workspace_id="ws_verify",
        repair_plan_id=REPAIR_PLAN_ID,
        repair_plan_checksum=REPAIR_PLAN_CHECKSUM,
        planner_certification_id=(
            PLANNER_CERTIFICATION_ID
        ),
        planner_certification_checksum=(
            PLANNER_CERTIFICATION_CHECKSUM
        ),
        authorization_state="REJECTED",
        authorized_action_ids=(),
        authorized_by=(
            "contract_verification_authority"
        ),
        authorization_reason=(
            "Negative authorization verification."
        ),
    )
)


authorized_apply_authorization_validation = (
    validate_lifecycle_repair_execution_authorization_v1(
        authorization=authorized_apply_authorization,
    )
)


authorized_apply_request_validation = (
    validate_lifecycle_repair_execution_request_v1(
        execution_request=authorized_apply_request,
    )
)


dry_run_authorization_validation = (
    validate_lifecycle_repair_execution_authorization_v1(
        authorization=dry_run_authorization,
    )
)


dry_run_request_validation = (
    validate_lifecycle_repair_execution_request_v1(
        execution_request=dry_run_request,
    )
)


rejected_authorization_validation = (
    validate_lifecycle_repair_execution_authorization_v1(
        authorization=rejected_authorization,
    )
)


authorized_apply_certification = (
    certify_lifecycle_repair_executor_contract_v1(
        authorization=authorized_apply_authorization,
        execution_request=authorized_apply_request,
    )
)


dry_run_certification = (
    certify_lifecycle_repair_executor_contract_v1(
        authorization=dry_run_authorization,
        execution_request=dry_run_request,
    )
)


authorized_apply_summary = (
    summarize_lifecycle_repair_executor_contract_v1(
        certification=authorized_apply_certification,
    )
)


dry_run_summary = (
    summarize_lifecycle_repair_executor_contract_v1(
        certification=dry_run_certification,
    )
)
authorized_apply_authorization_checksum_source = {
    key:
        value

    for key, value
    in authorized_apply_authorization.items()

    if key != "authorization_checksum"
}


calculated_authorized_apply_authorization_checksum = (
    calculate_lifecycle_repair_executor_checksum_v1(
        payload=(
            authorized_apply_authorization_checksum_source
        ),
    )
)


authorized_apply_request_checksum_source = {
    key:
        value

    for key, value
    in authorized_apply_request.items()

    if key != "execution_request_checksum"
}


calculated_authorized_apply_request_checksum = (
    calculate_lifecycle_repair_executor_checksum_v1(
        payload=(
            authorized_apply_request_checksum_source
        ),
    )
)


authorized_apply_certification_checksum_source = {
    key:
        value

    for key, value
    in authorized_apply_certification.items()

    if key != "certification_checksum"
}


calculated_authorized_apply_certification_checksum = (
    calculate_lifecycle_repair_executor_checksum_v1(
        payload=(
            authorized_apply_certification_checksum_source
        ),
    )
)


dry_run_certification_checksum_source = {
    key:
        value

    for key, value
    in dry_run_certification.items()

    if key != "certification_checksum"
}


calculated_dry_run_certification_checksum = (
    calculate_lifecycle_repair_executor_checksum_v1(
        payload=dry_run_certification_checksum_source,
    )
)


unsupported_execution_mode_rejected = False

try:
    create_lifecycle_repair_execution_request_v1(
        execution_request_id=(
            "executor_contract_invalid_mode_request_v1"
        ),
        workspace_id="ws_verify",
        repair_plan_id=REPAIR_PLAN_ID,
        repair_plan_checksum=REPAIR_PLAN_CHECKSUM,
        planner_certification_id=(
            PLANNER_CERTIFICATION_ID
        ),
        planner_certification_checksum=(
            PLANNER_CERTIFICATION_CHECKSUM
        ),
        authorization_id=(
            authorized_apply_authorization[
                "authorization_id"
            ]
        ),
        authorization_checksum=(
            authorized_apply_authorization[
                "authorization_checksum"
            ]
        ),
        execution_mode="UNSAFE_MODE",
        requested_action_ids=(
            ACTION_ID_1,
        ),
        require_all_actions_authorized=True,
    )

except LifecycleRepairExecutorContractError:
    unsupported_execution_mode_rejected = True


duplicate_authorized_action_ids_rejected = False

try:
    create_lifecycle_repair_execution_authorization_v1(
        authorization_id=(
            "executor_contract_duplicate_authorization_v1"
        ),
        workspace_id="ws_verify",
        repair_plan_id=REPAIR_PLAN_ID,
        repair_plan_checksum=REPAIR_PLAN_CHECKSUM,
        planner_certification_id=(
            PLANNER_CERTIFICATION_ID
        ),
        planner_certification_checksum=(
            PLANNER_CERTIFICATION_CHECKSUM
        ),
        authorization_state="AUTHORIZED",
        authorized_action_ids=(
            ACTION_ID_1,
            ACTION_ID_1,
        ),
        authorized_by=(
            "contract_verification_authority"
        ),
        authorization_reason=(
            "Duplicate authorization negative test."
        ),
    )

except LifecycleRepairExecutorContractError:
    duplicate_authorized_action_ids_rejected = True


rejected_authorization_with_actions_rejected = False

try:
    create_lifecycle_repair_execution_authorization_v1(
        authorization_id=(
            "executor_contract_invalid_rejected_auth_v1"
        ),
        workspace_id="ws_verify",
        repair_plan_id=REPAIR_PLAN_ID,
        repair_plan_checksum=REPAIR_PLAN_CHECKSUM,
        planner_certification_id=(
            PLANNER_CERTIFICATION_ID
        ),
        planner_certification_checksum=(
            PLANNER_CERTIFICATION_CHECKSUM
        ),
        authorization_state="REJECTED",
        authorized_action_ids=(
            ACTION_ID_1,
        ),
        authorized_by=(
            "contract_verification_authority"
        ),
        authorization_reason=(
            "Rejected authorization must not "
            "authorize actions."
        ),
    )

except LifecycleRepairExecutorContractError:
    rejected_authorization_with_actions_rejected = True


empty_authorized_action_ids_rejected = False

try:
    create_lifecycle_repair_execution_authorization_v1(
        authorization_id=(
            "executor_contract_empty_authorization_v1"
        ),
        workspace_id="ws_verify",
        repair_plan_id=REPAIR_PLAN_ID,
        repair_plan_checksum=REPAIR_PLAN_CHECKSUM,
        planner_certification_id=(
            PLANNER_CERTIFICATION_ID
        ),
        planner_certification_checksum=(
            PLANNER_CERTIFICATION_CHECKSUM
        ),
        authorization_state="AUTHORIZED",
        authorized_action_ids=(),
        authorized_by=(
            "contract_verification_authority"
        ),
        authorization_reason=(
            "Empty authorization negative test."
        ),
    )

except LifecycleRepairExecutorContractError:
    empty_authorized_action_ids_rejected = True


tampered_authorization = dict(
    authorized_apply_authorization
)

tampered_authorization[
    "workspace_id"
] = "ws_tampered"


tampered_authorization_validation = (
    validate_lifecycle_repair_execution_authorization_v1(
        authorization=tampered_authorization,
    )
)


tampered_request = dict(
    authorized_apply_request
)

tampered_request[
    "repair_plan_checksum"
] = (
    "tampered_repair_plan_checksum"
)


tampered_request_validation = (
    validate_lifecycle_repair_execution_request_v1(
        execution_request=tampered_request,
    )
)


unauthorized_action_request = (
    create_lifecycle_repair_execution_request_v1(
        execution_request_id=(
            "executor_contract_unauthorized_action_request_v1"
        ),
        workspace_id="ws_verify",
        repair_plan_id=REPAIR_PLAN_ID,
        repair_plan_checksum=REPAIR_PLAN_CHECKSUM,
        planner_certification_id=(
            PLANNER_CERTIFICATION_ID
        ),
        planner_certification_checksum=(
            PLANNER_CERTIFICATION_CHECKSUM
        ),
        authorization_id=(
            authorized_apply_authorization[
                "authorization_id"
            ]
        ),
        authorization_checksum=(
            authorized_apply_authorization[
                "authorization_checksum"
            ]
        ),
        execution_mode="AUTHORIZED_APPLY",
        requested_action_ids=(
            "repair_action_not_authorized",
        ),
        require_all_actions_authorized=True,
    )
)


unauthorized_action_certification = (
    certify_lifecycle_repair_executor_contract_v1(
        authorization=authorized_apply_authorization,
        execution_request=unauthorized_action_request,
    )
)


workspace_mismatch_request = (
    create_lifecycle_repair_execution_request_v1(
        execution_request_id=(
            "executor_contract_workspace_mismatch_v1"
        ),
        workspace_id="ws_other",
        repair_plan_id=REPAIR_PLAN_ID,
        repair_plan_checksum=REPAIR_PLAN_CHECKSUM,
        planner_certification_id=(
            PLANNER_CERTIFICATION_ID
        ),
        planner_certification_checksum=(
            PLANNER_CERTIFICATION_CHECKSUM
        ),
        authorization_id=(
            authorized_apply_authorization[
                "authorization_id"
            ]
        ),
        authorization_checksum=(
            authorized_apply_authorization[
                "authorization_checksum"
            ]
        ),
        execution_mode="AUTHORIZED_APPLY",
        requested_action_ids=(
            ACTION_ID_1,
        ),
        require_all_actions_authorized=True,
    )
)


workspace_mismatch_certification = (
    certify_lifecycle_repair_executor_contract_v1(
        authorization=authorized_apply_authorization,
        execution_request=workspace_mismatch_request,
    )
)


partial_authorization_opt_out_request = (
    create_lifecycle_repair_execution_request_v1(
        execution_request_id=(
            "executor_contract_partial_authorization_opt_out_v1"
        ),
        workspace_id="ws_verify",
        repair_plan_id=REPAIR_PLAN_ID,
        repair_plan_checksum=REPAIR_PLAN_CHECKSUM,
        planner_certification_id=(
            PLANNER_CERTIFICATION_ID
        ),
        planner_certification_checksum=(
            PLANNER_CERTIFICATION_CHECKSUM
        ),
        authorization_id=(
            authorized_apply_authorization[
                "authorization_id"
            ]
        ),
        authorization_checksum=(
            authorized_apply_authorization[
                "authorization_checksum"
            ]
        ),
        execution_mode="AUTHORIZED_APPLY",
        requested_action_ids=(
            ACTION_ID_1,
        ),
        require_all_actions_authorized=False,
    )
)


partial_authorization_opt_out_validation = (
    validate_lifecycle_repair_execution_request_v1(
        execution_request=(
            partial_authorization_opt_out_request
        ),
    )
)


partial_authorization_opt_out_certification = (
    certify_lifecycle_repair_executor_contract_v1(
        authorization=(
            authorized_apply_authorization
        ),
        execution_request=(
            partial_authorization_opt_out_request
        ),
    )
)


after = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED.items()
}
checks = {
    "contract_schema_valid":
        (
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_SCHEMA
            == "body_store_lifecycle_repair_executor_contract.v1"
        ),

    "authorization_schema_valid":
        (
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTION_AUTHORIZATION_SCHEMA
            == "body_store_lifecycle_repair_execution_authorization.v1"
        ),

    "execution_request_schema_valid":
        (
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTION_REQUEST_SCHEMA
            == "body_store_lifecycle_repair_execution_request.v1"
        ),

    "execution_result_schema_valid":
        (
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTION_RESULT_SCHEMA
            == "body_store_lifecycle_repair_execution_result.v1"
        ),

    "action_result_schema_valid":
        (
            BODY_STORE_LIFECYCLE_REPAIR_ACTION_RESULT_SCHEMA
            == "body_store_lifecycle_repair_action_result.v1"
        ),

    "contract_version_valid":
        (
            BODY_STORE_LIFECYCLE_REPAIR_EXECUTOR_CONTRACT_VERSION
            == "1.0"
        ),

    "execution_modes_valid":
        SUPPORTED_EXECUTION_MODES
        == (
            "DRY_RUN",
            "AUTHORIZED_APPLY",
        ),

    "authorization_states_valid":
        SUPPORTED_AUTHORIZATION_STATES
        == (
            "AUTHORIZED",
            "REJECTED",
        ),

    "executor_action_types_present":
        len(
            SUPPORTED_EXECUTOR_ACTION_TYPES
        )
        == 8,

    "non_executable_planner_actions_present":
        NON_EXECUTABLE_PLANNER_ACTION_TYPES
        == (
            "REVIEW_RETENTION_STATE",
            "MANUAL_REVIEW_REQUIRED",
        ),

    "non_executable_actions_not_executor_actions":
        not set(
            NON_EXECUTABLE_PLANNER_ACTION_TYPES
        ).intersection(
            SUPPORTED_EXECUTOR_ACTION_TYPES
        ),

    "prohibited_actions_present":
        len(
            PROHIBITED_DIRECT_EXECUTION_ACTION_TYPES
        )
        > 0,

    "prohibited_actions_not_executor_actions":
        not set(
            PROHIBITED_DIRECT_EXECUTION_ACTION_TYPES
        ).intersection(
            SUPPORTED_EXECUTOR_ACTION_TYPES
        ),

    "required_safety_gates_complete":
        len(
            REQUIRED_EXECUTION_SAFETY_GATES
        )
        == 9,

    "execution_statuses_present":
        len(
            SUPPORTED_ACTION_EXECUTION_STATUSES
        )
        == 6,

    "authorized_apply_authorization_valid":
        authorized_apply_authorization_validation[
            "authorization_valid"
        ]
        is True,

    "authorized_apply_request_valid":
        authorized_apply_request_validation[
            "request_valid"
        ]
        is True,

    "dry_run_authorization_valid":
        dry_run_authorization_validation[
            "authorization_valid"
        ]
        is True,

    "dry_run_request_valid":
        dry_run_request_validation[
            "request_valid"
        ]
        is True,

    "rejected_authorization_record_valid":
        rejected_authorization_validation[
            "authorization_valid"
        ]
        is True,

    "rejected_authorization_not_explicit":
        rejected_authorization[
            "explicitly_authorized"
        ]
        is False,

    "rejected_authorization_has_zero_actions":
        rejected_authorization[
            "authorized_action_count"
        ]
        == 0,

    "authorized_apply_authorization_checksum_valid":
        (
            authorized_apply_authorization[
                "authorization_checksum"
            ]
            == calculated_authorized_apply_authorization_checksum
        ),

    "authorized_apply_request_checksum_valid":
        (
            authorized_apply_request[
                "execution_request_checksum"
            ]
            == calculated_authorized_apply_request_checksum
        ),

    "authorized_apply_certification_checksum_valid":
        (
            authorized_apply_certification[
                "certification_checksum"
            ]
            == calculated_authorized_apply_certification_checksum
        ),

    "dry_run_certification_checksum_valid":
        (
            dry_run_certification[
                "certification_checksum"
            ]
            == calculated_dry_run_certification_checksum
        ),

    "authorized_apply_contract_certified":
        authorized_apply_certification[
            "contract_certified"
        ]
        is True,

    "authorized_apply_explicit_authorization_present":
        authorized_apply_certification[
            "explicit_authorization_present"
        ]
        is True,

    "authorized_apply_requested_actions_authorized":
        authorized_apply_certification[
            "requested_actions_authorized"
        ]
        is True,

    "authorized_apply_all_actions_requirement_satisfied":
        authorized_apply_certification[
            "all_actions_authorized_requirement_satisfied"
        ]
        is True,

    "authorized_apply_mode_detected":
        authorized_apply_certification[
            "authorized_apply_requested"
        ]
        is True,

    "authorized_apply_contractual_eligibility_possible":
        authorized_apply_certification[
            "apply_eligibility_contractually_possible"
        ]
        is True,

    "dry_run_contract_certified":
        dry_run_certification[
            "contract_certified"
        ]
        is True,

    "dry_run_mode_detected":
        dry_run_certification[
            "dry_run_requested"
        ]
        is True,

    "dry_run_not_authorized_apply":
        dry_run_certification[
            "authorized_apply_requested"
        ]
        is False,

    "dry_run_apply_eligibility_false":
        dry_run_certification[
            "apply_eligibility_contractually_possible"
        ]
        is False,

    "authorized_apply_summary_certified":
        authorized_apply_summary[
            "contract_certified"
        ]
        is True,

    "authorized_apply_summary_apply_possible":
        authorized_apply_summary[
            "apply_eligibility_contractually_possible"
        ]
        is True,

    "dry_run_summary_certified":
        dry_run_summary[
            "contract_certified"
        ]
        is True,

    "dry_run_summary_apply_not_possible":
        dry_run_summary[
            "apply_eligibility_contractually_possible"
        ]
        is False,

    "partial_authorization_opt_out_request_rejected":
        partial_authorization_opt_out_validation[
            "request_valid"
        ]
        is False,

    "partial_authorization_opt_out_gate_detected":
        partial_authorization_opt_out_validation[
            "require_all_actions_authorized_valid"
        ]
        is False,

    "partial_authorization_opt_out_not_contract_certified":
        partial_authorization_opt_out_certification[
            "contract_certified"
        ]
        is False,

    "partial_authorization_opt_out_apply_eligibility_false":
        partial_authorization_opt_out_certification[
            "apply_eligibility_contractually_possible"
        ]
        is False,

    "unsupported_execution_mode_rejected":
        unsupported_execution_mode_rejected
        is True,

    "duplicate_authorized_action_ids_rejected":
        duplicate_authorized_action_ids_rejected
        is True,

    "rejected_authorization_with_actions_rejected":
        rejected_authorization_with_actions_rejected
        is True,

    "empty_authorized_action_ids_rejected":
        empty_authorized_action_ids_rejected
        is True,

    "tampered_authorization_rejected":
        tampered_authorization_validation[
            "authorization_valid"
        ]
        is False,

    "tampered_authorization_checksum_detected":
        tampered_authorization_validation[
            "checksum_valid"
        ]
        is False,

    "tampered_request_rejected":
        tampered_request_validation[
            "request_valid"
        ]
        is False,

    "tampered_request_checksum_detected":
        tampered_request_validation[
            "checksum_valid"
        ]
        is False,

    "unauthorized_action_not_contract_certified":
        unauthorized_action_certification[
            "contract_certified"
        ]
        is False,

    "unauthorized_action_detected":
        unauthorized_action_certification[
            "requested_actions_authorized"
        ]
        is False,

    "unauthorized_action_apply_eligibility_false":
        unauthorized_action_certification[
            "apply_eligibility_contractually_possible"
        ]
        is False,

    "workspace_mismatch_not_contract_certified":
        workspace_mismatch_certification[
            "contract_certified"
        ]
        is False,

    "workspace_mismatch_detected":
        workspace_mismatch_certification[
            "workspace_id_matches"
        ]
        is False,

    "workspace_mismatch_apply_eligibility_false":
        workspace_mismatch_certification[
            "apply_eligibility_contractually_possible"
        ]
        is False,

    "contract_phase_execution_eligible_false":
        authorized_apply_certification[
            "execution_eligible"
        ]
        is False,

    "contract_phase_execution_authorized_false":
        authorized_apply_certification[
            "execution_authorized"
        ]
        is False,

    "contract_phase_execution_not_started":
        authorized_apply_certification[
            "execution_started"
        ]
        is False,

    "contract_phase_execution_not_completed":
        authorized_apply_certification[
            "execution_completed"
        ]
        is False,

    "contract_phase_repair_not_executed":
        authorized_apply_certification[
            "repair_executed"
        ]
        is False,

    "production_mutation_not_performed":
        authorized_apply_certification[
            "production_mutation_performed"
        ]
        is False,

    "lifecycle_not_modified":
        authorized_apply_certification[
            "lifecycle_modified"
        ]
        is False,

    "archive_not_modified":
        authorized_apply_certification[
            "archive_modified"
        ]
        is False,

    "tombstone_not_modified":
        authorized_apply_certification[
            "tombstone_modified"
        ]
        is False,

    "body_store_not_modified":
        authorized_apply_certification[
            "body_store_modified"
        ]
        is False,

    "no_runtime_job_created":
        authorized_apply_certification[
            "runtime_job_created"
        ]
        is False,

    "no_queue_job_created":
        authorized_apply_certification[
            "queue_job_created"
        ]
        is False,

    "production_outputs_unchanged":
        all(
            before[
                name
            ]
            == after[
                name
            ]

            for name in before
        ),
}


failures = [
    name
    for name, passed
    in checks.items()
    if passed is not True
]


print()
print("=" * 120)
print(
    "UNIVERSAL ARTICLE BODY STORE LIFECYCLE "
    "REPAIR EXECUTOR CONTRACT — PHASE 9.1.13.1"
)
print("=" * 120)
print()


for name, passed in checks.items():
    print(
        f"{name:<86}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )


print()
print("AUTHORIZED APPLY CONTRACT")

print(
    "  Authorization valid:                 "
    + str(
        authorized_apply_certification[
            "authorization_valid"
        ]
    )
)

print(
    "  Execution request valid:             "
    + str(
        authorized_apply_certification[
            "request_valid"
        ]
    )
)

print(
    "  Requested actions authorized:        "
    + str(
        authorized_apply_certification[
            "requested_actions_authorized"
        ]
    )
)

print(
    "  Explicit authorization present:      "
    + str(
        authorized_apply_certification[
            "explicit_authorization_present"
        ]
    )
)

print(
    "  Contractual apply eligibility:       "
    + str(
        authorized_apply_certification[
            "apply_eligibility_contractually_possible"
        ]
    )
)


print()
print("DRY RUN CONTRACT")

print(
    "  Contract certified:                  "
    + str(
        dry_run_certification[
            "contract_certified"
        ]
    )
)

print(
    "  Dry run requested:                   "
    + str(
        dry_run_certification[
            "dry_run_requested"
        ]
    )
)

print(
    "  Contractual apply eligibility:       "
    + str(
        dry_run_certification[
            "apply_eligibility_contractually_possible"
        ]
    )
)


print()
print("NEGATIVE BOUNDARIES")
print(
    "  Partial-authorization opt-out:       REJECTED"
)
print(
    "  Unsupported execution mode:          REJECTED"
)
print(
    "  Duplicate authorized action IDs:     REJECTED"
)
print(
    "  Rejected auth containing actions:    REJECTED"
)
print(
    "  Empty authorized action set:         REJECTED"
)
print(
    "  Authorization tampering:             DETECTED"
)
print(
    "  Execution-request tampering:         DETECTED"
)
print(
    "  Unauthorized requested action:       NOT CERTIFIED"
)
print(
    "  Workspace mismatch:                  NOT CERTIFIED"
)


print()
print("CONTRACT SAFETY BOUNDARY")
print(
    "  Contract phase only:                 True"
)
print(
    "  Execution eligible:                  False"
)
print(
    "  Execution authorized:                False"
)
print(
    "  Execution started:                   False"
)
print(
    "  Execution completed:                 False"
)
print(
    "  Repairs executed:                    0"
)
print(
    "  Production mutations performed:      0"
)
print(
    "  Production lifecycle modified:       0"
)
print(
    "  Production archive modified:         0"
)
print(
    "  Production tombstones modified:      0"
)
print(
    "  Production Body Store modified:      0"
)
print(
    "  Production queue jobs created:       0"
)
print(
    "  Runtime registrations modified:      0"
)


print()
print("PROTECTED OUTPUTS")

for name in before:
    print(
        "  "
        + f"{name:<30}"
        + (
            "UNCHANGED"
            if before[
                name
            ]
            == after[
                name
            ]
            else "CHANGED"
        )
    )


print()
print("FAILURES")

if failures:
    for failure in failures:
        print(
            "  - "
            + failure
        )

else:
    print(
        "  None"
    )


print()

if failures:
    print(
        "BODY STORE LIFECYCLE REPAIR EXECUTOR "
        "CONTRACT PHASE 9.1.13.1: FAIL"
    )

    raise SystemExit(1)


print(
    "BODY STORE LIFECYCLE REPAIR EXECUTOR "
    "CONTRACT PHASE 9.1.13.1: PASS"
)

print(
    "The Lifecycle Repair Executor Contract is "
    "verified without executing any repair."
)

print("=" * 120)
