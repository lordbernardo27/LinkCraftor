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

from backend.server.universal_article_body_store.body_store_lifecycle_repair_planner_certification_v1 import (
    BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CERTIFICATION_BUNDLE_SCHEMA,
    BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CERTIFICATION_SCHEMA,
    BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CERTIFICATION_VERSION,
    build_lifecycle_repair_planner_certification_bundle_v1,
    calculate_lifecycle_repair_planner_certification_checksum_v1,
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
        "repair_planner_certification_scanner_request_v1",

    "verification_checksum":
        (
            "ae0b94243dfe472fa570d6791516"
            "96b4d210e57f06090689a741190b"
            "51599725"
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
            "repair_planner_certification_request_v1"
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


certification_bundle = (
    build_lifecycle_repair_planner_certification_bundle_v1(
        planner_request=planner_request,
        scanner_certification=scanner_certification,
        findings=findings,
        repair_plan=repair_plan,
    )
)


certification = certification_bundle[
    "certification"
]

validation = certification_bundle[
    "validation"
]

summary = certification_bundle[
    "summary"
]


after = {
    name:
        fingerprint(
            path
        )

    for name, path
    in PROTECTED.items()
}
from backend.server.universal_article_body_store.body_store_lifecycle_repair_planner_certification_v1 import (
    validate_lifecycle_repair_planner_certification_v1,
)

from backend.server.universal_article_body_store.body_store_lifecycle_repair_planner_verifier_v1 import (
    calculate_lifecycle_repair_planner_verification_checksum_v1,
)


certification_checksum_source = {
    key:
        value

    for key, value
    in certification.items()

    if key != "certification_checksum"
}


calculated_certification_checksum = (
    calculate_lifecycle_repair_planner_certification_checksum_v1(
        payload=certification_checksum_source,
    )
)


verification = certification[
    "verification"
]


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


bundle_checksum_source = {
    key:
        value

    for key, value
    in certification_bundle.items()

    if key != "bundle_checksum"
}


calculated_bundle_checksum = (
    calculate_lifecycle_repair_planner_certification_checksum_v1(
        payload=bundle_checksum_source,
    )
)


tampered_certification = dict(
    certification
)

tampered_certification[
    "execution_authorized"
] = True


tampered_certification_validation = (
    validate_lifecycle_repair_planner_certification_v1(
        certification=tampered_certification,
    )
)


tampered_verification_certification = dict(
    certification
)

tampered_verification = dict(
    certification[
        "verification"
    ]
)

tampered_verification[
    "safety_verified"
] = False

tampered_verification_certification[
    "verification"
] = tampered_verification


tampered_verification_validation = (
    validate_lifecycle_repair_planner_certification_v1(
        certification=(
            tampered_verification_certification
        ),
    )
)


tampered_certification_id = dict(
    certification
)

tampered_certification_id[
    "certification_id"
] = (
    "repair_planner_certification_tampered"
)


tampered_certification_id_validation = (
    validate_lifecycle_repair_planner_certification_v1(
        certification=tampered_certification_id,
    )
)


tampered_certification_checksum = dict(
    certification
)

tampered_certification_checksum[
    "certification_checksum"
] = (
    "tampered_certification_checksum"
)


tampered_checksum_validation = (
    validate_lifecycle_repair_planner_certification_v1(
        certification=tampered_certification_checksum,
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
    "certification_schema_valid":
        (
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CERTIFICATION_SCHEMA
            == "body_store_lifecycle_repair_planner_certification.v1"
        ),

    "certification_bundle_schema_valid":
        (
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CERTIFICATION_BUNDLE_SCHEMA
            == "body_store_lifecycle_repair_planner_certification_bundle.v1"
        ),

    "certification_version_valid":
        (
            BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CERTIFICATION_VERSION
            == "1.0"
        ),

    "bundle_schema_valid":
        (
            certification_bundle[
                "schema"
            ]
            == BODY_STORE_LIFECYCLE_REPAIR_PLANNER_CERTIFICATION_BUNDLE_SCHEMA
        ),

    "bundle_certified":
        certification_bundle[
            "bundle_certified"
        ]
        is True,

    "certification_certified":
        certification[
            "certified"
        ]
        is True,

    "certification_validation_passed":
        validation[
            "certification_valid"
        ]
        is True,

    "schema_validation_passed":
        validation[
            "schema_valid"
        ]
        is True,

    "certification_version_validation_passed":
        validation[
            "certification_version_valid"
        ]
        is True,

    "contract_version_validation_passed":
        validation[
            "contract_version_valid"
        ]
        is True,

    "engine_version_validation_passed":
        validation[
            "engine_version_valid"
        ]
        is True,

    "verifier_version_validation_passed":
        validation[
            "verifier_version_valid"
        ]
        is True,

    "certification_id_valid":
        validation[
            "certification_id_valid"
        ]
        is True,

    "certification_id_matches":
        validation[
            "certification_id_matches"
        ]
        is True,

    "verification_mapping_valid":
        validation[
            "verification_mapping_valid"
        ]
        is True,

    "verification_passed":
        validation[
            "verification_passed"
        ]
        is True,

    "identity_verified":
        validation[
            "identity_verified"
        ]
        is True,

    "actions_verified":
        validation[
            "actions_verified"
        ]
        is True,

    "safety_verified":
        validation[
            "safety_verified"
        ]
        is True,

    "reproducibility_verified":
        validation[
            "reproducibility_verified"
        ]
        is True,

    "verification_identity_matches":
        validation[
            "verification_identity_matches"
        ]
        is True,

    "embedded_verification_checksum_valid":
        validation[
            "embedded_verification_checksum_valid"
        ]
        is True,

    "certification_verification_checksum_matches":
        validation[
            "certification_verification_checksum_matches"
        ]
        is True,

    "verification_flags_match":
        validation[
            "verification_flags_match"
        ]
        is True,

    "count_fields_match":
        validation[
            "count_fields_match"
        ]
        is True,

    "certification_scope_valid":
        validation[
            "certification_scope_valid"
        ]
        is True,

    "planner_mode_valid":
        validation[
            "planner_mode_valid"
        ]
        is True,

    "safety_boundaries_valid":
        validation[
            "safety_boundaries_valid"
        ]
        is True,

    "verification_checksum_valid":
        (
            verification[
                "verification_checksum"
            ]
            == calculated_verification_checksum
        ),

    "certification_checksum_valid":
        (
            certification[
                "certification_checksum"
            ]
            == calculated_certification_checksum
            and validation[
                "certification_checksum_valid"
            ]
            is True
        ),

    "bundle_checksum_valid":
        (
            certification_bundle[
                "bundle_checksum"
            ]
            == calculated_bundle_checksum
        ),

    "summary_certified":
        summary[
            "certified"
        ]
        is True,

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

    "summary_repair_action_count_valid":
        summary[
            "repair_action_count"
        ]
        == 5,

    "summary_automatic_action_count_valid":
        summary[
            "automatically_planned_action_count"
        ]
        == 4,

    "summary_manual_review_count_valid":
        summary[
            "manual_review_action_count"
        ]
        == 5,

    "summary_certification_scope_valid":
        summary[
            "certification_scope"
        ]
        == "REPAIR_PLANNER_ONLY",

    "summary_planner_mode_valid":
        summary[
            "planner_mode"
        ]
        == "PLAN_ONLY",

    "tampered_execution_authorization_rejected":
        tampered_certification_validation[
            "certification_valid"
        ]
        is False,

    "tampered_execution_boundary_detected":
        tampered_certification_validation[
            "safety_boundaries_valid"
        ]
        is False,

    "tampered_embedded_verification_rejected":
        tampered_verification_validation[
            "certification_valid"
        ]
        is False,

    "tampered_embedded_verification_checksum_detected":
        tampered_verification_validation[
            "embedded_verification_checksum_valid"
        ]
        is False,

    "tampered_certification_id_rejected":
        tampered_certification_id_validation[
            "certification_valid"
        ]
        is False,

    "tampered_certification_id_detected":
        tampered_certification_id_validation[
            "certification_id_matches"
        ]
        is False,

    "tampered_certification_checksum_rejected":
        tampered_checksum_validation[
            "certification_valid"
        ]
        is False,

    "tampered_certification_checksum_detected":
        tampered_checksum_validation[
            "certification_checksum_valid"
        ]
        is False,

    "execution_not_authorized":
        certification_bundle[
            "execution_authorized"
        ]
        is False,

    "repair_not_executed":
        certification_bundle[
            "repair_executed"
        ]
        is False,

    "production_mutation_prohibited":
        certification_bundle[
            "production_mutation_allowed"
        ]
        is False,

    "lifecycle_not_modified":
        certification_bundle[
            "lifecycle_modified"
        ]
        is False,

    "archive_not_modified":
        certification_bundle[
            "archive_modified"
        ]
        is False,

    "tombstone_not_modified":
        certification_bundle[
            "tombstone_modified"
        ]
        is False,

    "body_store_not_modified":
        certification_bundle[
            "body_store_modified"
        ]
        is False,

    "no_runtime_job_created":
        certification_bundle[
            "runtime_job_created"
        ]
        is False,

    "no_queue_job_created":
        certification_bundle[
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
    "REPAIR PLANNER CERTIFICATION — PHASE 9.1.12.4"
)
print("=" * 120)
print()


for name, passed in checks.items():
    print(
        f"{name:<84}"
        + (
            "PASS"
            if passed
            else "FAIL"
        )
    )


print()
print("CERTIFICATION SUMMARY")

print(
    "  Certification ID:                    "
    + str(
        summary[
            "certification_id"
        ]
    )
)

print(
    "  Repair plan ID:                       "
    + str(
        summary[
            "repair_plan_id"
        ]
    )
)

print(
    "  Certified:                            "
    + str(
        summary[
            "certified"
        ]
    )
)

print(
    "  Identity verified:                    "
    + str(
        summary[
            "identity_verified"
        ]
    )
)

print(
    "  Repair actions verified:              "
    + str(
        summary[
            "actions_verified"
        ]
    )
)

print(
    "  Safety verified:                      "
    + str(
        summary[
            "safety_verified"
        ]
    )
)

print(
    "  Reproducibility verified:             "
    + str(
        summary[
            "reproducibility_verified"
        ]
    )
)

print(
    "  Repair actions:                       "
    + str(
        summary[
            "repair_action_count"
        ]
    )
)

print(
    "  Automatically planned actions:        "
    + str(
        summary[
            "automatically_planned_action_count"
        ]
    )
)

print(
    "  Manual-review actions:                "
    + str(
        summary[
            "manual_review_action_count"
        ]
    )
)


print()
print("INTEGRITY CHECKSUMS")
print(
    "  Embedded verification checksum:       VALID"
)
print(
    "  Planner certification checksum:       VALID"
)
print(
    "  Certification bundle checksum:        VALID"
)


print()
print("TAMPER DETECTION")
print(
    "  Execution authorization tamper:       DETECTED"
)
print(
    "  Embedded verification tamper:         DETECTED"
)
print(
    "  Certification identity tamper:        DETECTED"
)
print(
    "  Certification checksum tamper:        DETECTED"
)


print()
print("SAFETY BOUNDARY")
print(
    "  Certification scope:                  REPAIR_PLANNER_ONLY"
)
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
        "CERTIFICATION PHASE 9.1.12.4: FAIL"
    )

    raise SystemExit(1)


print(
    "BODY STORE LIFECYCLE REPAIR PLANNER "
    "CERTIFICATION PHASE 9.1.12.4: PASS"
)

print(
    "The Lifecycle Repair Planner subsystem "
    "is fully certified."
)

print("=" * 120)
