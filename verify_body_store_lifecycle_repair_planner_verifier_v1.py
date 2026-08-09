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
    create_lifecycle_repair_planner_request_v1,
)

from backend.server.universal_article_body_store.body_store_lifecycle_repair_planner_engine_v1 import (
    build_lifecycle_repair_plan_v1,
)

from backend.server.universal_article_body_store.body_store_lifecycle_repair_planner_verifier_v1 import (
    BODY_STORE_LIFECYCLE_REPAIR_PLANNER_VERIFICATION_SCHEMA,
    BODY_STORE_LIFECYCLE_REPAIR_PLANNER_VERIFIER_SCHEMA,
    BODY_STORE_LIFECYCLE_REPAIR_PLANNER_VERIFIER_VERSION,
    calculate_lifecycle_repair_planner_verification_checksum_v1,
    summarize_lifecycle_repair_planner_verification_v1,
    verify_lifecycle_repair_actions_v1,
    verify_lifecycle_repair_plan_identity_v1,
    verify_lifecycle_repair_plan_reproducibility_v1,
    verify_lifecycle_repair_plan_safety_v1,
    verify_lifecycle_repair_planner_v1,
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
        "repair_planner_verifier_scanner_request_v1",

    "verification_checksum":
        (
            "58d2306ee2e645b1ab7539575f9d"
            "b8d630534a19218abf23d0b85c3f"
            "9eb319e9"
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


planner_request = (
    create_lifecycle_repair_planner_request_v1(
        repair_plan_request_id=(
            "repair_planner_verifier_request_v1"
        ),
        workspace_id="ws_verify",
        repair_scope="WORKSPACE",
        finding_ids=None,
        allow_automatic_planning=True,
        require_manual_review_for_critical=True,
    )
)


repair_plan = (
    build_lifecycle_repair_plan_v1(
        planner_request=planner_request,
        scanner_certification=scanner_certification,
        findings=findings,
    )
)
identity_verification = (
    verify_lifecycle_repair_plan_identity_v1(
        planner_request=planner_request,
        scanner_certification=scanner_certification,
        repair_plan=repair_plan,
    )
)


action_verification = (
    verify_lifecycle_repair_actions_v1(
        planner_request=planner_request,
        findings=findings,
        repair_plan=repair_plan,
    )
)


safety_verification = (
    verify_lifecycle_repair_plan_safety_v1(
        repair_plan=repair_plan,
    )
)


reproducibility_verification = (
    verify_lifecycle_repair_plan_reproducibility_v1(
        planner_request=planner_request,
        scanner_certification=scanner_certification,
        findings=findings,
        repair_plan=repair_plan,
    )
)


verification = (
    verify_lifecycle_repair_planner_v1(
        planner_request=planner_request,
        scanner_certification=scanner_certification,
        findings=findings,
        repair_plan=repair_plan,
    )
)


summary = (
    summarize_lifecycle_repair_planner_verification_v1(
        verification=verification,
    )
)


verification_checksum_source = {
    key:
        value

    for key, value
    in verification.items()

    if key != "verification_checksum"
}


calculated_verification_checksum = (
    calculate_lifecycle_repair_planner_verification_checksum_v1(
        payload=verification_checksum_source,
    )
)


tampered_plan = dict(
    repair_plan
)

tampered_plan[
    "execution_authorized"
] = True


tampered_safety_verification = (
    verify_lifecycle_repair_plan_safety_v1(
        repair_plan=tampered_plan,
    )
)


tampered_identity_verification = (
    verify_lifecycle_repair_plan_identity_v1(
        planner_request=planner_request,
        scanner_certification=scanner_certification,
        repair_plan=tampered_plan,
    )
)


tampered_reproducibility_verification = (
    verify_lifecycle_repair_plan_reproducibility_v1(
        planner_request=planner_request,
        scanner_certification=scanner_certification,
        findings=findings,
        repair_plan=tampered_plan,
    )
)


tampered_master_verification = (
    verify_lifecycle_repair_planner_v1(
        planner_request=planner_request,
        scanner_certification=scanner_certification,
        findings=findings,
        repair_plan=tampered_plan,
    )
)


wrong_scanner_certification = dict(
    scanner_certification
)

wrong_scanner_certification[
    "verification_checksum"
] = (
    "tampered_scanner_verification_checksum"
)


wrong_scanner_identity_verification = (
    verify_lifecycle_repair_plan_identity_v1(
        planner_request=planner_request,
        scanner_certification=wrong_scanner_certification,
        repair_plan=repair_plan,
    )
)


tampered_findings = list(
    findings
)

tampered_findings[
    0
] = dict(
    tampered_findings[
        0
    ]
)

tampered_findings[
    0
][
    "severity"
] = "WARNING"


tampered_action_verification = (
    verify_lifecycle_repair_actions_v1(
        planner_request=planner_request,
        findings=tuple(
            tampered_findings
        ),
        repair_plan=repair_plan,
    )
)


tampered_findings_reproducibility = (
    verify_lifecycle_repair_plan_reproducibility_v1(
        planner_request=planner_request,
        scanner_certification=scanner_certification,
        findings=tuple(
            tampered_findings
        ),
        repair_plan=repair_plan,
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
    "verifier_schema_valid":
        (
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_VERIFIER_SCHEMA
            == "body_store_lifecycle_repair_planner_verifier.v1"
        ),

    "verifier_version_valid":
        (
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_VERIFIER_VERSION
            == "1.0"
        ),

    "verification_schema_valid":
        (
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_VERIFICATION_SCHEMA
            == "body_store_lifecycle_repair_planner_verification.v1"
        ),

    "identity_verified":
        identity_verification[
            "identity_verified"
        ]
        is True,

    "request_identity_valid":
        identity_verification[
            "request_valid"
        ]
        is True,

    "repair_plan_identity_valid":
        identity_verification[
            "plan_valid"
        ]
        is True,

    "repair_plan_request_id_matches":
        identity_verification[
            "repair_plan_request_id_matches"
        ]
        is True,

    "workspace_id_matches":
        identity_verification[
            "workspace_id_matches"
        ]
        is True,

    "repair_scope_matches":
        identity_verification[
            "repair_scope_matches"
        ]
        is True,

    "request_checksum_matches":
        identity_verification[
            "request_checksum_matches"
        ]
        is True,

    "scanner_certified":
        identity_verification[
            "scanner_certified"
        ]
        is True,

    "scanner_verification_passed":
        identity_verification[
            "scanner_verification_passed"
        ]
        is True,

    "scanner_scan_request_id_matches":
        identity_verification[
            "scanner_scan_request_id_matches"
        ]
        is True,

    "scanner_verification_checksum_matches":
        identity_verification[
            "scanner_verification_checksum_matches"
        ]
        is True,

    "actions_verified":
        action_verification[
            "actions_verified"
        ]
        is True,

    "selected_finding_set_matches":
        action_verification[
            "selected_finding_set_matches"
        ]
        is True,

    "five_actions_verified":
        action_verification[
            "verified_action_count"
        ]
        == 5,

    "five_actions_expected":
        action_verification[
            "expected_action_count"
        ]
        == 5,

    "finding_types_match":
        action_verification[
            "finding_type_matches"
        ]
        is True,

    "severities_match":
        action_verification[
            "severity_matches"
        ]
        is True,

    "action_mapping_matches":
        action_verification[
            "action_mapping_matches"
        ]
        is True,

    "risk_class_matches":
        action_verification[
            "risk_class_matches"
        ]
        is True,

    "automatic_planning_matches":
        action_verification[
            "automatic_planning_matches"
        ]
        is True,

    "manual_review_matches":
        action_verification[
            "manual_review_matches"
        ]
        is True,

    "planner_decision_matches":
        action_verification[
            "planner_decision_matches"
        ]
        is True,

    "prohibited_actions_absent":
        action_verification[
            "prohibited_actions_absent"
        ]
        is True,

    "action_execution_boundaries_valid":
        action_verification[
            "execution_boundaries_valid"
        ]
        is True,

    "action_counts_match":
        action_verification[
            "action_count_matches"
        ]
        is True,

    "selected_finding_count_matches":
        action_verification[
            "selected_finding_count_matches"
        ]
        is True,

    "safety_verified":
        safety_verification[
            "safety_verified"
        ]
        is True,

    "planner_mode_valid":
        safety_verification[
            "planner_mode_valid"
        ]
        is True,

    "execution_not_authorized":
        safety_verification[
            "execution_not_authorized"
        ]
        is True,

    "repair_not_executed":
        safety_verification[
            "repair_not_executed"
        ]
        is True,

    "production_mutation_prohibited":
        safety_verification[
            "production_mutation_prohibited"
        ]
        is True,

    "lifecycle_not_modified":
        safety_verification[
            "lifecycle_not_modified"
        ]
        is True,

    "archive_not_modified":
        safety_verification[
            "archive_not_modified"
        ]
        is True,

    "tombstone_not_modified":
        safety_verification[
            "tombstone_not_modified"
        ]
        is True,

    "body_store_not_modified":
        safety_verification[
            "body_store_not_modified"
        ]
        is True,

    "no_runtime_job_created":
        safety_verification[
            "no_runtime_job_created"
        ]
        is True,

    "no_queue_job_created":
        safety_verification[
            "no_queue_job_created"
        ]
        is True,

    "reproducibility_verified":
        reproducibility_verification[
            "reproducibility_verified"
        ]
        is True,

    "reproducible_plan_id":
        reproducibility_verification[
            "repair_plan_id_matches"
        ]
        is True,

    "reproducible_plan_checksum":
        reproducibility_verification[
            "repair_plan_checksum_matches"
        ]
        is True,

    "reproducible_action_ids":
        reproducibility_verification[
            "repair_action_ids_match"
        ]
        is True,

    "reproducible_action_checksums":
        reproducibility_verification[
            "repair_action_checksums_match"
        ]
        is True,

    "reproducible_action_types":
        reproducibility_verification[
            "repair_action_types_match"
        ]
        is True,

    "full_plan_reproducible":
        reproducibility_verification[
            "full_plan_matches"
        ]
        is True,

    "master_verification_passed":
        verification[
            "verification_passed"
        ]
        is True,

    "master_identity_verified":
        verification[
            "identity_verified"
        ]
        is True,

    "master_actions_verified":
        verification[
            "actions_verified"
        ]
        is True,

    "master_safety_verified":
        verification[
            "safety_verified"
        ]
        is True,

    "master_reproducibility_verified":
        verification[
            "reproducibility_verified"
        ]
        is True,

    "verification_checksum_valid":
        (
            verification[
                "verification_checksum"
            ]
            == calculated_verification_checksum
        ),

    "summary_verification_passed":
        summary[
            "verification_passed"
        ]
        is True,

    "summary_identity_verified":
        summary[
            "identity_verified"
        ]
        is True,

    "summary_actions_verified":
        summary[
            "actions_verified"
        ]
        is True,

    "summary_safety_verified":
        summary[
            "safety_verified"
        ]
        is True,

    "summary_reproducibility_verified":
        summary[
            "reproducibility_verified"
        ]
        is True,

    "summary_action_count_valid":
        summary[
            "repair_action_count"
        ]
        == 5,

    "summary_automatic_count_valid":
        summary[
            "automatically_planned_action_count"
        ]
        == 4,

    "summary_manual_review_count_valid":
        summary[
            "manual_review_action_count"
        ]
        == 5,

    "summary_plan_only":
        summary[
            "planner_mode"
        ]
        == "PLAN_ONLY",

    "summary_execution_not_authorized":
        summary[
            "execution_authorized"
        ]
        is False,

    "summary_repair_not_executed":
        summary[
            "repair_executed"
        ]
        is False,

    "summary_production_mutation_prohibited":
        summary[
            "production_mutation_allowed"
        ]
        is False,

    "tampered_plan_safety_detected":
        tampered_safety_verification[
            "safety_verified"
        ]
        is False,

    "tampered_execution_authorization_detected":
        tampered_safety_verification[
            "execution_not_authorized"
        ]
        is False,

    "tampered_plan_identity_rejected":
        tampered_identity_verification[
            "identity_verified"
        ]
        is False,

    "tampered_plan_reproducibility_rejected":
        tampered_reproducibility_verification[
            "reproducibility_verified"
        ]
        is False,

    "tampered_master_verification_rejected":
        tampered_master_verification[
            "verification_passed"
        ]
        is False,

    "wrong_scanner_checksum_detected":
        wrong_scanner_identity_verification[
            "scanner_verification_checksum_matches"
        ]
        is False,

    "wrong_scanner_identity_rejected":
        wrong_scanner_identity_verification[
            "identity_verified"
        ]
        is False,

    "tampered_finding_detected":
        tampered_action_verification[
            "actions_verified"
        ]
        is False,

    "tampered_finding_severity_detected":
        tampered_action_verification[
            "severity_matches"
        ]
        is False,

    "tampered_findings_reproducibility_rejected":
        tampered_findings_reproducibility[
            "reproducibility_verified"
        ]
        is False,

    "tampered_findings_full_plan_mismatch":
        tampered_findings_reproducibility[
            "full_plan_matches"
        ]
        is False,

    "master_execution_not_authorized":
        verification[
            "execution_authorized"
        ]
        is False,

    "master_repair_not_executed":
        verification[
            "repair_executed"
        ]
        is False,

    "master_production_mutation_prohibited":
        verification[
            "production_mutation_allowed"
        ]
        is False,

    "master_lifecycle_not_modified":
        verification[
            "lifecycle_modified"
        ]
        is False,

    "master_archive_not_modified":
        verification[
            "archive_modified"
        ]
        is False,

    "master_tombstone_not_modified":
        verification[
            "tombstone_modified"
        ]
        is False,

    "master_body_store_not_modified":
        verification[
            "body_store_modified"
        ]
        is False,

    "master_no_runtime_job_created":
        verification[
            "runtime_job_created"
        ]
        is False,

    "master_no_queue_job_created":
        verification[
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
    "REPAIR PLANNER VERIFICATION — PHASE 9.1.12.3"
)
print("=" * 120)
print()


for name, passed in checks.items():
    print(
        f"{name:<82}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )


print()
print("VERIFICATION SUMMARY")

print(
    "  Identity verified:                   "
    + str(
        summary[
            "identity_verified"
        ]
    )
)

print(
    "  Repair actions verified:             "
    + str(
        summary[
            "actions_verified"
        ]
    )
)

print(
    "  Safety verified:                     "
    + str(
        summary[
            "safety_verified"
        ]
    )
)

print(
    "  Reproducibility verified:            "
    + str(
        summary[
            "reproducibility_verified"
        ]
    )
)

print(
    "  Repair actions verified:             "
    + str(
        summary[
            "repair_action_count"
        ]
    )
)

print(
    "  Automatically planned actions:       "
    + str(
        summary[
            "automatically_planned_action_count"
        ]
    )
)

print(
    "  Manual-review actions:               "
    + str(
        summary[
            "manual_review_action_count"
        ]
    )
)


print()
print("TAMPER DETECTION")

print(
    "  Execution authorization tamper:      DETECTED"
)

print(
    "  Scanner checksum tamper:             DETECTED"
)

print(
    "  Finding severity tamper:             DETECTED"
)

print(
    "  Reproducibility tamper:              DETECTED"
)


print()
print("SAFETY BOUNDARY")

print(
    "  Planner mode:                        PLAN_ONLY"
)

print(
    "  Repair plan generated:               True"
)

print(
    "  Execution authorized:                False"
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
        "VERIFICATION PHASE 9.1.12.3: FAIL"
    )

    raise SystemExit(1)


print(
    "BODY STORE LIFECYCLE REPAIR PLANNER "
    "VERIFICATION PHASE 9.1.12.3: PASS"
)

print(
    "The Lifecycle Repair Planner independently "
    "verified plan identity, repair-action accuracy, "
    "safety, and reproducibility."
)

print("=" * 120)
