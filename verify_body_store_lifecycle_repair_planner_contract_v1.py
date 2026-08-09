from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping


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
    AUTOMATICALLY_PLANNABLE_FINDING_TYPES,
    BODY_STORE_LIFECYCLE_REPAIR_ACTION_SCHEMA,
    BODY_STORE_LIFECYCLE_REPAIR_PLAN_SCHEMA,
    BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_SCHEMA,
    BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_VERSION,
    BODY_STORE_LIFECYCLE_REPAIR_PLANNER_REQUEST_SCHEMA,
    PROHIBITED_REPAIR_ACTION_TYPES,
    SUPPORTED_FINDING_SEVERITIES,
    SUPPORTED_FINDING_TYPES,
    SUPPORTED_REPAIR_ACTION_TYPES,
    SUPPORTED_REPAIR_SCOPES,
    LifecycleRepairPlannerContractError,
    calculate_lifecycle_repair_planner_checksum_v1,
    certify_lifecycle_repair_planner_request_v1,
    create_lifecycle_repair_planner_request_v1,
    summarize_lifecycle_repair_planner_request_v1,
    validate_lifecycle_repair_planner_request_v1,
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


def json_ready(
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
                json_ready(
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
            json_ready(
                item
            )

            for item
            in value
        ]

    return value


before = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED.items()
}


workspace_request = (
    create_lifecycle_repair_planner_request_v1(
        repair_plan_request_id=(
            "repair_planner_contract_workspace_request_v1"
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
            "repair_planner_contract_finding_set_request_v1"
        ),
        workspace_id="ws_verify",
        repair_scope="FINDING_SET",
        finding_ids=(
            "finding_001",
            "finding_002",
            "finding_003",
        ),
        allow_automatic_planning=True,
        require_manual_review_for_critical=True,
    )
)


workspace_validation = (
    validate_lifecycle_repair_planner_request_v1(
        planner_request=workspace_request,
    )
)


finding_set_validation = (
    validate_lifecycle_repair_planner_request_v1(
        planner_request=finding_set_request,
    )
)


workspace_certification = (
    certify_lifecycle_repair_planner_request_v1(
        planner_request=workspace_request,
    )
)


finding_set_certification = (
    certify_lifecycle_repair_planner_request_v1(
        planner_request=finding_set_request,
    )
)


workspace_summary = (
    summarize_lifecycle_repair_planner_request_v1(
        planner_request=workspace_request,
    )
)


finding_set_summary = (
    summarize_lifecycle_repair_planner_request_v1(
        planner_request=finding_set_request,
    )
)
workspace_checksum_source = {
    key:
        value

    for key, value
    in workspace_request.items()

    if key != "request_checksum"
}


calculated_workspace_checksum = (
    calculate_lifecycle_repair_planner_checksum_v1(
        payload=workspace_checksum_source,
    )
)


finding_set_checksum_source = {
    key:
        value

    for key, value
    in finding_set_request.items()

    if key != "request_checksum"
}


calculated_finding_set_checksum = (
    calculate_lifecycle_repair_planner_checksum_v1(
        payload=finding_set_checksum_source,
    )
)


unsupported_scope_rejected = False

try:
    create_lifecycle_repair_planner_request_v1(
        repair_plan_request_id=(
            "invalid_scope_request"
        ),
        workspace_id="ws_verify",
        repair_scope="INVALID_SCOPE",
        finding_ids=None,
    )

except LifecycleRepairPlannerContractError:
    unsupported_scope_rejected = True


empty_finding_set_rejected = False

try:
    create_lifecycle_repair_planner_request_v1(
        repair_plan_request_id=(
            "empty_finding_set_request"
        ),
        workspace_id="ws_verify",
        repair_scope="FINDING_SET",
        finding_ids=(),
    )

except LifecycleRepairPlannerContractError:
    empty_finding_set_rejected = True


workspace_with_finding_ids_rejected = False

try:
    create_lifecycle_repair_planner_request_v1(
        repair_plan_request_id=(
            "invalid_workspace_request"
        ),
        workspace_id="ws_verify",
        repair_scope="WORKSPACE",
        finding_ids=(
            "finding_001",
        ),
    )

except LifecycleRepairPlannerContractError:
    workspace_with_finding_ids_rejected = True


duplicate_finding_ids_rejected = False

try:
    create_lifecycle_repair_planner_request_v1(
        repair_plan_request_id=(
            "duplicate_findings_request"
        ),
        workspace_id="ws_verify",
        repair_scope="FINDING_SET",
        finding_ids=(
            "finding_001",
            "finding_001",
        ),
    )

except LifecycleRepairPlannerContractError:
    duplicate_finding_ids_rejected = True


empty_request_id_rejected = False

try:
    create_lifecycle_repair_planner_request_v1(
        repair_plan_request_id="",
        workspace_id="ws_verify",
        repair_scope="WORKSPACE",
        finding_ids=None,
    )

except LifecycleRepairPlannerContractError:
    empty_request_id_rejected = True


empty_workspace_id_rejected = False

try:
    create_lifecycle_repair_planner_request_v1(
        repair_plan_request_id=(
            "empty_workspace_request"
        ),
        workspace_id="",
        repair_scope="WORKSPACE",
        finding_ids=None,
    )

except LifecycleRepairPlannerContractError:
    empty_workspace_id_rejected = True


tampered_request = dict(
    json_ready(
        workspace_request
    )
)

tampered_request[
    "workspace_id"
] = "ws_tampered"


tampered_validation = (
    validate_lifecycle_repair_planner_request_v1(
        planner_request=tampered_request,
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
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_SCHEMA
            == "body_store_lifecycle_repair_planner_contract.v1"
        ),

    "request_schema_valid":
        (
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_REQUEST_SCHEMA
            == "body_store_lifecycle_repair_planner_request.v1"
        ),

    "repair_plan_schema_valid":
        (
            BODY_STORE_LIFECYCLE_REPAIR_PLAN_SCHEMA
            == "body_store_lifecycle_repair_plan.v1"
        ),

    "repair_action_schema_valid":
        (
            BODY_STORE_LIFECYCLE_REPAIR_ACTION_SCHEMA
            == "body_store_lifecycle_repair_action.v1"
        ),

    "contract_version_valid":
        (
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CONTRACT_VERSION
            == "1.0"
        ),

    "workspace_scope_supported":
        "WORKSPACE"
        in SUPPORTED_REPAIR_SCOPES,

    "finding_set_scope_supported":
        "FINDING_SET"
        in SUPPORTED_REPAIR_SCOPES,

    "supported_finding_types_present":
        len(
            SUPPORTED_FINDING_TYPES
        )
        == 5,

    "supported_finding_severities_valid":
        SUPPORTED_FINDING_SEVERITIES
        == (
            "WARNING",
            "ERROR",
            "CRITICAL",
        ),

    "supported_repair_actions_present":
        len(
            SUPPORTED_REPAIR_ACTION_TYPES
        )
        > 0,

    "automatic_planning_types_present":
        len(
            AUTOMATICALLY_PLANNABLE_FINDING_TYPES
        )
        == 5,

    "prohibited_repair_actions_present":
        len(
            PROHIBITED_REPAIR_ACTION_TYPES
        )
        > 0,

    "supported_and_prohibited_actions_disjoint":
        not set(
            SUPPORTED_REPAIR_ACTION_TYPES
        ).intersection(
            PROHIBITED_REPAIR_ACTION_TYPES
        ),

    "workspace_request_valid":
        workspace_validation[
            "request_valid"
        ]
        is True,

    "finding_set_request_valid":
        finding_set_validation[
            "request_valid"
        ]
        is True,

    "workspace_checksum_valid":
        (
            workspace_request[
                "request_checksum"
            ]
            == calculated_workspace_checksum
        ),

    "finding_set_checksum_valid":
        (
            finding_set_request[
                "request_checksum"
            ]
            == calculated_finding_set_checksum
        ),

    "workspace_scope_has_no_finding_ids":
        (
            workspace_summary[
                "finding_id_count"
            ]
            == 0
        ),

    "finding_set_has_three_finding_ids":
        (
            finding_set_summary[
                "finding_id_count"
            ]
            == 3
        ),

    "workspace_certified":
        workspace_certification[
            "certified"
        ]
        is True,

    "finding_set_certified":
        finding_set_certification[
            "certified"
        ]
        is True,

    "workspace_planner_mode_valid":
        workspace_request[
            "planner_mode"
        ]
        == "PLAN_ONLY",

    "finding_set_planner_mode_valid":
        finding_set_request[
            "planner_mode"
        ]
        == "PLAN_ONLY",

    "unsupported_scope_rejected":
        unsupported_scope_rejected
        is True,

    "empty_finding_set_rejected":
        empty_finding_set_rejected
        is True,

    "workspace_with_finding_ids_rejected":
        workspace_with_finding_ids_rejected
        is True,

    "duplicate_finding_ids_rejected":
        duplicate_finding_ids_rejected
        is True,

    "empty_request_id_rejected":
        empty_request_id_rejected
        is True,

    "empty_workspace_id_rejected":
        empty_workspace_id_rejected
        is True,

    "tampered_request_rejected":
        tampered_validation[
            "request_valid"
        ]
        is False,

    "tampered_checksum_detected":
        tampered_validation[
            "checksum_valid"
        ]
        is False,

    "workspace_read_only":
        workspace_request[
            "read_only"
        ]
        is True,

    "finding_set_read_only":
        finding_set_request[
            "read_only"
        ]
        is True,

    "workspace_repair_not_planned":
        workspace_request[
            "repair_planned"
        ]
        is False,

    "finding_set_repair_not_planned":
        finding_set_request[
            "repair_planned"
        ]
        is False,

    "workspace_repair_not_executed":
        workspace_request[
            "repair_executed"
        ]
        is False,

    "finding_set_repair_not_executed":
        finding_set_request[
            "repair_executed"
        ]
        is False,

    "workspace_certification_generated_no_plan":
        workspace_certification[
            "repair_plan_generated"
        ]
        is False,

    "finding_set_certification_generated_no_plan":
        finding_set_certification[
            "repair_plan_generated"
        ]
        is False,

    "workspace_certification_generated_zero_actions":
        workspace_certification[
            "repair_actions_generated"
        ]
        == 0,

    "finding_set_certification_generated_zero_actions":
        finding_set_certification[
            "repair_actions_generated"
        ]
        == 0,

    "production_mutation_prohibited":
        (
            workspace_request[
                "production_mutation_allowed"
            ]
            is False
            and finding_set_request[
                "production_mutation_allowed"
            ]
            is False
        ),

    "lifecycle_not_modified":
        (
            workspace_request[
                "lifecycle_modified"
            ]
            is False
            and finding_set_request[
                "lifecycle_modified"
            ]
            is False
        ),

    "archive_not_modified":
        (
            workspace_request[
                "archive_modified"
            ]
            is False
            and finding_set_request[
                "archive_modified"
            ]
            is False
        ),

    "tombstone_not_modified":
        (
            workspace_request[
                "tombstone_modified"
            ]
            is False
            and finding_set_request[
                "tombstone_modified"
            ]
            is False
        ),

    "body_store_not_modified":
        (
            workspace_request[
                "body_store_modified"
            ]
            is False
            and finding_set_request[
                "body_store_modified"
            ]
            is False
        ),

    "no_runtime_job_created":
        (
            workspace_request[
                "runtime_job_created"
            ]
            is False
            and finding_set_request[
                "runtime_job_created"
            ]
            is False
        ),

    "no_queue_job_created":
        (
            workspace_request[
                "queue_job_created"
            ]
            is False
            and finding_set_request[
                "queue_job_created"
            ]
            is False
        ),

    "production_outputs_unchanged":
        all(
            before[
                name
            ]
            == after[
                name
            ]

            for name
            in before
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
    "REPAIR PLANNER CONTRACT — PHASE 9.1.12.1"
)
print("=" * 120)
print()


for name, passed in checks.items():
    print(
        f"{name:<76}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )


print()
print("CONTRACT BOUNDARIES")
print(
    "  Planner mode:                         PLAN_ONLY"
)
print(
    "  Supported repair scopes:             "
    + str(
        len(
            SUPPORTED_REPAIR_SCOPES
        )
    )
)
print(
    "  Supported finding types:             "
    + str(
        len(
            SUPPORTED_FINDING_TYPES
        )
    )
)
print(
    "  Supported repair action types:       "
    + str(
        len(
            SUPPORTED_REPAIR_ACTION_TYPES
        )
    )
)
print(
    "  Prohibited repair action types:      "
    + str(
        len(
            PROHIBITED_REPAIR_ACTION_TYPES
        )
    )
)


print()
print("SAFETY RESULTS")
print(
    "  Repair plans generated:              0"
)
print(
    "  Repair actions generated:            0"
)
print(
    "  Repairs executed:                    0"
)
print(
    "  Production mutation allowed:         False"
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
        "BODY STORE LIFECYCLE REPAIR PLANNER "
        "CONTRACT PHASE 9.1.12.1: FAIL"
    )

    raise SystemExit(1)


print(
    "BODY STORE LIFECYCLE REPAIR PLANNER "
    "CONTRACT PHASE 9.1.12.1: PASS"
)

print(
    "The Lifecycle Repair Planner Contract "
    "is verified and remains planning-only."
)

print("=" * 120)
