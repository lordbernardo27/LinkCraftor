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


from backend.server.universal_article_body_store.body_store_lifecycle_repair_planner_contract_v1 import (
    BODY_STORE_LIFECYCLE_REPAIR_ACTION_SCHEMA,
    BODY_STORE_LIFECYCLE_REPAIR_PLAN_SCHEMA,
    create_lifecycle_repair_planner_request_v1,
)

from backend.server.universal_article_body_store.body_store_lifecycle_repair_planner_engine_v1 import (
    BODY_STORE_LIFECYCLE_REPAIR_PLANNER_ENGINE_SCHEMA,
    BODY_STORE_LIFECYCLE_REPAIR_PLANNER_ENGINE_VERSION,
    FINDING_TO_REPAIR_ACTION,
    REPAIR_ACTION_RISK_CLASS,
    LifecycleRepairPlannerEngineError,
    build_lifecycle_repair_plan_v1,
    calculate_lifecycle_repair_plan_checksum_v1,
    summarize_lifecycle_repair_plan_v1,
    validate_lifecycle_repair_plan_v1,
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


scanner_certification = {
    "certified":
        True,

    "verification_passed":
        True,

    "workspace_id":
        "ws_verify",

    "scan_request_id":
        "scanner_engine_verification_request_v1",

    "verification_checksum":
        (
            "9f0fcdba66f34061a6fa55e5320d"
            "91d1f584bd6d0c2c8e49d83e54e2"
            "1736d301"
        ),
}


findings = (
    {
        "finding_id":
            "finding_duplicate_identity",

        "finding_type":
            "DUPLICATE_LIFECYCLE_IDENTITY",

        "severity":
            "ERROR",

        "workspace_id":
            "ws_verify",

        "body_id":
            "body_duplicate",
    },

    {
        "finding_id":
            "finding_invalid_json",

        "finding_type":
            "INVALID_JSON_RECORD",

        "severity":
            "WARNING",

        "workspace_id":
            "ws_verify",

        "record_path":
            "broken_body.json",
    },

    {
        "finding_id":
            "finding_retention_state",

        "finding_type":
            "RETENTION_STATE_INCONSISTENCY",

        "severity":
            "ERROR",

        "workspace_id":
            "ws_verify",

        "body_id":
            "body_retention",
    },

    {
        "finding_id":
            "finding_tombstone_content",

        "finding_type":
            "TOMBSTONE_CONTENT_BOUNDARY_VIOLATION",

        "severity":
            "CRITICAL",

        "workspace_id":
            "ws_verify",

        "body_id":
            "body_deleted",
    },

    {
        "finding_id":
            "finding_unsupported_state",

        "finding_type":
            "UNSUPPORTED_LIFECYCLE_STATE",

        "severity":
            "ERROR",

        "workspace_id":
            "ws_verify",

        "body_id":
            "body_unknown_state",
    },
)


workspace_request = (
    create_lifecycle_repair_planner_request_v1(
        repair_plan_request_id=(
            "repair_planner_engine_workspace_request_v1"
        ),
        workspace_id="ws_verify",
        repair_scope="WORKSPACE",
        finding_ids=None,
        allow_automatic_planning=True,
        require_manual_review_for_critical=True,
    )
)


finding_set_request = (
    create_lifecycle_repair_planner_request_v1(
        repair_plan_request_id=(
            "repair_planner_engine_finding_set_request_v1"
        ),
        workspace_id="ws_verify",
        repair_scope="FINDING_SET",
        finding_ids=(
            "finding_duplicate_identity",
            "finding_invalid_json",
            "finding_unsupported_state",
        ),
        allow_automatic_planning=True,
        require_manual_review_for_critical=True,
    )
)


manual_only_request = (
    create_lifecycle_repair_planner_request_v1(
        repair_plan_request_id=(
            "repair_planner_engine_manual_only_request_v1"
        ),
        workspace_id="ws_verify",
        repair_scope="WORKSPACE",
        finding_ids=None,
        allow_automatic_planning=False,
        require_manual_review_for_critical=True,
    )
)
workspace_plan = (
    build_lifecycle_repair_plan_v1(
        planner_request=workspace_request,
        scanner_certification=scanner_certification,
        findings=findings,
    )
)


finding_set_plan = (
    build_lifecycle_repair_plan_v1(
        planner_request=finding_set_request,
        scanner_certification=scanner_certification,
        findings=findings,
    )
)


manual_only_plan = (
    build_lifecycle_repair_plan_v1(
        planner_request=manual_only_request,
        scanner_certification=scanner_certification,
        findings=findings,
    )
)


workspace_validation = (
    validate_lifecycle_repair_plan_v1(
        repair_plan=workspace_plan,
    )
)


finding_set_validation = (
    validate_lifecycle_repair_plan_v1(
        repair_plan=finding_set_plan,
    )
)


manual_only_validation = (
    validate_lifecycle_repair_plan_v1(
        repair_plan=manual_only_plan,
    )
)


workspace_summary = (
    summarize_lifecycle_repair_plan_v1(
        repair_plan=workspace_plan,
    )
)


finding_set_summary = (
    summarize_lifecycle_repair_plan_v1(
        repair_plan=finding_set_plan,
    )
)


manual_only_summary = (
    summarize_lifecycle_repair_plan_v1(
        repair_plan=manual_only_plan,
    )
)


workspace_actions_by_finding = {
    action[
        "source_finding_id"
    ]:
        action

    for action in workspace_plan[
        "repair_actions"
    ]
}


finding_set_actions_by_finding = {
    action[
        "source_finding_id"
    ]:
        action

    for action in finding_set_plan[
        "repair_actions"
    ]
}


manual_only_actions_by_finding = {
    action[
        "source_finding_id"
    ]:
        action

    for action in manual_only_plan[
        "repair_actions"
    ]
}


workspace_checksum_source = {
    key:
        value

    for key, value
    in workspace_plan.items()

    if key != "repair_plan_checksum"
}


calculated_workspace_checksum = (
    calculate_lifecycle_repair_plan_checksum_v1(
        payload=workspace_checksum_source,
    )
)


finding_set_checksum_source = {
    key:
        value

    for key, value
    in finding_set_plan.items()

    if key != "repair_plan_checksum"
}


calculated_finding_set_checksum = (
    calculate_lifecycle_repair_plan_checksum_v1(
        payload=finding_set_checksum_source,
    )
)


manual_only_checksum_source = {
    key:
        value

    for key, value
    in manual_only_plan.items()

    if key != "repair_plan_checksum"
}


calculated_manual_only_checksum = (
    calculate_lifecycle_repair_plan_checksum_v1(
        payload=manual_only_checksum_source,
    )
)


invalid_scanner_certification_rejected = False

try:
    build_lifecycle_repair_plan_v1(
        planner_request=workspace_request,
        scanner_certification={
            "certified":
                False,

            "verification_passed":
                True,

            "workspace_id":
                "ws_verify",

            "scan_request_id":
                "invalid_scanner_request",

            "verification_checksum":
                "invalid_verification_checksum",
        },
        findings=findings,
    )

except LifecycleRepairPlannerEngineError:
    invalid_scanner_certification_rejected = True


scanner_workspace_mismatch_rejected = False

try:
    build_lifecycle_repair_plan_v1(
        planner_request=workspace_request,
        scanner_certification={
            "certified":
                True,

            "verification_passed":
                True,

            "workspace_id":
                "ws_wrong",

            "scan_request_id":
                "scanner_wrong_workspace",

            "verification_checksum":
                "wrong_workspace_checksum",
        },
        findings=findings,
    )

except LifecycleRepairPlannerEngineError:
    scanner_workspace_mismatch_rejected = True


missing_requested_finding_rejected = False

missing_finding_request = (
    create_lifecycle_repair_planner_request_v1(
        repair_plan_request_id=(
            "repair_planner_missing_finding_request_v1"
        ),
        workspace_id="ws_verify",
        repair_scope="FINDING_SET",
        finding_ids=(
            "finding_duplicate_identity",
            "finding_does_not_exist",
        ),
        allow_automatic_planning=True,
        require_manual_review_for_critical=True,
    )
)

try:
    build_lifecycle_repair_plan_v1(
        planner_request=missing_finding_request,
        scanner_certification=scanner_certification,
        findings=findings,
    )

except LifecycleRepairPlannerEngineError:
    missing_requested_finding_rejected = True


duplicate_input_finding_rejected = False

duplicate_findings = (
    findings[
        0
    ],
    findings[
        0
    ],
)

try:
    build_lifecycle_repair_plan_v1(
        planner_request=workspace_request,
        scanner_certification=scanner_certification,
        findings=duplicate_findings,
    )

except LifecycleRepairPlannerEngineError:
    duplicate_input_finding_rejected = True


unsupported_finding_type_rejected = False

unsupported_findings = (
    {
        "finding_id":
            "finding_unsupported_type",

        "finding_type":
            "UNRECOGNIZED_FINDING_TYPE",

        "severity":
            "ERROR",

        "workspace_id":
            "ws_verify",
    },
)

try:
    build_lifecycle_repair_plan_v1(
        planner_request=workspace_request,
        scanner_certification=scanner_certification,
        findings=unsupported_findings,
    )

except LifecycleRepairPlannerEngineError:
    unsupported_finding_type_rejected = True


tampered_plan = dict(
    workspace_plan
)

tampered_plan[
    "execution_authorized"
] = True


tampered_plan_validation = (
    validate_lifecycle_repair_plan_v1(
        repair_plan=tampered_plan,
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
    "engine_schema_valid":
        (
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_ENGINE_SCHEMA
            == "body_store_lifecycle_repair_planner_engine.v1"
        ),

    "engine_version_valid":
        (
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_ENGINE_VERSION
            == "1.0"
        ),

    "repair_plan_schema_valid":
        (
            workspace_plan[
                "schema"
            ]
            == BODY_STORE_LIFECYCLE_REPAIR_PLAN_SCHEMA
        ),

    "repair_action_schema_valid":
        all(
            action[
                "schema"
            ]
            == BODY_STORE_LIFECYCLE_REPAIR_ACTION_SCHEMA

            for action in workspace_plan[
                "repair_actions"
            ]
        ),

    "finding_action_mapping_complete":
        len(
            FINDING_TO_REPAIR_ACTION
        )
        == 5,

    "risk_classification_present":
        len(
            REPAIR_ACTION_RISK_CLASS
        )
        > 0,

    "workspace_plan_valid":
        workspace_validation[
            "plan_valid"
        ]
        is True,

    "finding_set_plan_valid":
        finding_set_validation[
            "plan_valid"
        ]
        is True,

    "manual_only_plan_valid":
        manual_only_validation[
            "plan_valid"
        ]
        is True,

    "workspace_plan_generated":
        workspace_plan[
            "plan_generated"
        ]
        is True,

    "finding_set_plan_generated":
        finding_set_plan[
            "plan_generated"
        ]
        is True,

    "manual_only_plan_generated":
        manual_only_plan[
            "plan_generated"
        ]
        is True,

    "workspace_selected_five_findings":
        workspace_summary[
            "selected_finding_count"
        ]
        == 5,

    "workspace_generated_five_actions":
        workspace_summary[
            "repair_action_count"
        ]
        == 5,

    "finding_set_selected_three_findings":
        finding_set_summary[
            "selected_finding_count"
        ]
        == 3,

    "finding_set_generated_three_actions":
        finding_set_summary[
            "repair_action_count"
        ]
        == 3,

    "manual_only_selected_five_findings":
        manual_only_summary[
            "selected_finding_count"
        ]
        == 5,

    "manual_only_generated_five_actions":
        manual_only_summary[
            "repair_action_count"
        ]
        == 5,

    "duplicate_identity_action_correct":
        (
            workspace_actions_by_finding[
                "finding_duplicate_identity"
            ][
                "repair_action_type"
            ]
            == "RESOLVE_DUPLICATE_IDENTITY"
        ),

    "invalid_json_action_correct":
        (
            workspace_actions_by_finding[
                "finding_invalid_json"
            ][
                "repair_action_type"
            ]
            == "QUARANTINE_INVALID_RECORD"
        ),

    "retention_state_action_correct":
        (
            workspace_actions_by_finding[
                "finding_retention_state"
            ][
                "repair_action_type"
            ]
            == "REVIEW_RETENTION_STATE"
        ),

    "critical_tombstone_requires_manual_review":
        (
            workspace_actions_by_finding[
                "finding_tombstone_content"
            ][
                "repair_action_type"
            ]
            == "MANUAL_REVIEW_REQUIRED"
        ),

    "unsupported_state_action_correct":
        (
            workspace_actions_by_finding[
                "finding_unsupported_state"
            ][
                "repair_action_type"
            ]
            == "NORMALIZE_LIFECYCLE_STATE"
        ),

    "critical_action_not_automatically_planned":
        (
            workspace_actions_by_finding[
                "finding_tombstone_content"
            ][
                "automatically_planned"
            ]
            is False
        ),

    "critical_action_manual_review_required":
        (
            workspace_actions_by_finding[
                "finding_tombstone_content"
            ][
                "requires_manual_review"
            ]
            is True
        ),

    "workspace_automatic_action_count_valid":
        workspace_summary[
            "automatically_planned_action_count"
        ]
        == 4,

    "workspace_manual_review_count_valid":
        workspace_summary[
            "manual_review_action_count"
        ]
        == 5,

    "finding_set_contains_only_requested_findings":
        (
            set(
                finding_set_actions_by_finding
            )
            == {
                "finding_duplicate_identity",
                "finding_invalid_json",
                "finding_unsupported_state",
            }
        ),

    "finding_set_automatic_action_count_valid":
        finding_set_summary[
            "automatically_planned_action_count"
        ]
        == 3,

    "finding_set_manual_review_count_valid":
        finding_set_summary[
            "manual_review_action_count"
        ]
        == 3,

    "manual_only_all_actions_manual":
        all(
            action[
                "repair_action_type"
            ]
            == "MANUAL_REVIEW_REQUIRED"

            for action in manual_only_plan[
                "repair_actions"
            ]
        ),

    "manual_only_zero_automatic_actions":
        manual_only_summary[
            "automatically_planned_action_count"
        ]
        == 0,

    "manual_only_all_require_review":
        manual_only_summary[
            "manual_review_action_count"
        ]
        == 5,

    "workspace_checksum_valid":
        (
            workspace_plan[
                "repair_plan_checksum"
            ]
            == calculated_workspace_checksum
        ),

    "finding_set_checksum_valid":
        (
            finding_set_plan[
                "repair_plan_checksum"
            ]
            == calculated_finding_set_checksum
        ),

    "manual_only_checksum_valid":
        (
            manual_only_plan[
                "repair_plan_checksum"
            ]
            == calculated_manual_only_checksum
        ),

    "repair_action_checksums_valid":
        all(
            validation[
                "checksum_valid"
            ]
            is True

            for validation in workspace_validation[
                "action_validations"
            ]
        ),

    "repair_action_ids_unique":
        workspace_validation[
            "repair_action_ids_unique"
        ]
        is True,

    "repair_action_counts_consistent":
        workspace_validation[
            "count_consistency_valid"
        ]
        is True,

    "prohibited_actions_absent":
        workspace_validation[
            "prohibited_action_absent"
        ]
        is True,

    "scanner_certification_required":
        workspace_validation[
            "scanner_boundary_valid"
        ]
        is True,

    "invalid_scanner_certification_rejected":
        invalid_scanner_certification_rejected
        is True,

    "scanner_workspace_mismatch_rejected":
        scanner_workspace_mismatch_rejected
        is True,

    "missing_requested_finding_rejected":
        missing_requested_finding_rejected
        is True,

    "duplicate_input_finding_rejected":
        duplicate_input_finding_rejected
        is True,

    "unsupported_finding_type_rejected":
        unsupported_finding_type_rejected
        is True,

    "tampered_plan_rejected":
        tampered_plan_validation[
            "plan_valid"
        ]
        is False,

    "tampered_safety_boundary_detected":
        tampered_plan_validation[
            "safety_boundaries_valid"
        ]
        is False,

    "tampered_checksum_detected":
        tampered_plan_validation[
            "checksum_valid"
        ]
        is False,

    "workspace_execution_not_authorized":
        workspace_plan[
            "execution_authorized"
        ]
        is False,

    "all_actions_execution_not_authorized":
        all(
            action[
                "execution_authorized"
            ]
            is False

            for action in workspace_plan[
                "repair_actions"
            ]
        ),

    "workspace_repairs_not_executed":
        workspace_plan[
            "repair_executed"
        ]
        is False,

    "all_actions_not_executed":
        all(
            action[
                "repair_executed"
            ]
            is False

            for action in workspace_plan[
                "repair_actions"
            ]
        ),

    "planner_mode_plan_only":
        workspace_plan[
            "planner_mode"
        ]
        == "PLAN_ONLY",

    "production_mutation_prohibited":
        workspace_plan[
            "production_mutation_allowed"
        ]
        is False,

    "lifecycle_not_modified":
        workspace_plan[
            "lifecycle_modified"
        ]
        is False,

    "archive_not_modified":
        workspace_plan[
            "archive_modified"
        ]
        is False,

    "tombstone_not_modified":
        workspace_plan[
            "tombstone_modified"
        ]
        is False,

    "body_store_not_modified":
        workspace_plan[
            "body_store_modified"
        ]
        is False,

    "no_runtime_job_created":
        workspace_plan[
            "runtime_job_created"
        ]
        is False,

    "no_queue_job_created":
        workspace_plan[
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
    "REPAIR PLANNER ENGINE — PHASE 9.1.12.2"
)
print("=" * 120)
print()


for name, passed in checks.items():
    print(
        f"{name:<78}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )


print()
print("WORKSPACE REPAIR PLAN")

print(
    "  Selected findings:                   "
    + str(
        workspace_summary[
            "selected_finding_count"
        ]
    )
)

print(
    "  Repair actions generated:            "
    + str(
        workspace_summary[
            "repair_action_count"
        ]
    )
)

print(
    "  Automatically planned actions:       "
    + str(
        workspace_summary[
            "automatically_planned_action_count"
        ]
    )
)

print(
    "  Manual-review actions:               "
    + str(
        workspace_summary[
            "manual_review_action_count"
        ]
    )
)


print()
print("REPAIR ACTIONS")

for finding_id in sorted(
    workspace_actions_by_finding
):
    action = workspace_actions_by_finding[
        finding_id
    ]

    print(
        "  "
        + f"{finding_id:<36}"
        + " -> "
        + str(
            action[
                "repair_action_type"
            ]
        )
    )


print()
print("SAFETY BOUNDARY")
print(
    "  Planner mode:                         PLAN_ONLY"
)
print(
    "  Repair plan generated:                True"
)
print(
    "  Repair actions generated:             5"
)
print(
    "  Execution authorized:                 False"
)
print(
    "  Repairs executed:                     0"
)
print(
    "  Production mutation allowed:          False"
)
print(
    "  Production lifecycle modified:        0"
)
print(
    "  Production archive modified:          0"
)
print(
    "  Production tombstones modified:       0"
)
print(
    "  Production Body Store modified:       0"
)
print(
    "  Production queue jobs created:        0"
)
print(
    "  Runtime registrations modified:       0"
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
        "BODY STORE LIFECYCLE REPAIR PLANNER "
        "ENGINE PHASE 9.1.12.2: FAIL"
    )

    raise SystemExit(1)


print(
    "BODY STORE LIFECYCLE REPAIR PLANNER "
    "ENGINE PHASE 9.1.12.2: PASS"
)

print(
    "The Lifecycle Repair Planner Engine generated "
    "validated repair plans without executing repairs."
)

print("=" * 120)
