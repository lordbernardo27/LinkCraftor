from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

PHASE_5_3 = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "workflow_job_correlation.py"
)

PHASE_5_3_MANIFEST = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "workflow_job_correlation.freeze.json"
)

INVALIDATION = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "workflow_job_correlation.phase_5_6_invalidation.json"
)


EXPECTED_PHASE_5_3_SHA = (
    "C0D88ECC69680106B6833DF8CB3113FC"
    "9ABD23C1EE8B7D413BA4AAE3375648FA"
)

EXPECTED_MANIFEST_SHA = (
    "53F2B149EF904CE5692D85F349038CEA"
    "B901E00B06C6C273CA5B74EB31ACE8E5"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


actual_phase_5_3_sha = sha256(
    PHASE_5_3
)

actual_manifest_sha = sha256(
    PHASE_5_3_MANIFEST
)


if actual_phase_5_3_sha != EXPECTED_PHASE_5_3_SHA:
    raise SystemExit(
        (
            "INVALIDATION REFUSED: frozen Phase 5.3 production "
            "SHA is no longer canonical.\n"
            f"Expected: {EXPECTED_PHASE_5_3_SHA}\n"
            f"Actual:   {actual_phase_5_3_sha}"
        )
    )


if actual_manifest_sha != EXPECTED_MANIFEST_SHA:
    raise SystemExit(
        (
            "INVALIDATION REFUSED: frozen Phase 5.3 manifest "
            "SHA is no longer canonical.\n"
            f"Expected: {EXPECTED_MANIFEST_SHA}\n"
            f"Actual:   {actual_manifest_sha}"
        )
    )


if INVALIDATION.exists():
    raise SystemExit(
        (
            "INVALIDATION REFUSED: record already exists: "
            + str(
                INVALIDATION.relative_to(ROOT)
            )
        )
    )


record = {
    "component":
        "Workflow/Job Correlation",

    "phase":
        "5.3",

    "trigger_phase":
        "5.6 Runtime Integration Certification",

    "classification":
        "missed_certification_requirement",

    "frozen_production_invalidated":
        True,

    "production_modified":
        False,

    "manifest_modified":
        False,

    "previous_version":
        "workflow_job_correlation_v5.3.0",

    "previous_schema_version":
        "workflow_job_correlation_schema_v1",

    "previous_production_sha256":
        EXPECTED_PHASE_5_3_SHA,

    "previous_freeze_manifest_sha256":
        EXPECTED_MANIFEST_SHA,

    "proof": {
        "baseline_valid_submission_correlated":
            True,

        "invalid_cases_currently_accepted": [
            "missing submission object",
            "submission.persisted=False",
            "submission.queued=False",
            "submission.canonical_identity_preserved=False",
            "tampered submitted metadata.coordination",
            "missing submitted metadata",
        ],

        "priority_propagation_defect":
            False,
    },

    "required_corrective_rules": {
        "submitted_submission_object_required":
            True,

        "submission_persisted_must_be_literal_true":
            True,

        "submission_queued_must_be_literal_true":
            True,

        "submission_canonical_identity_preserved_must_be_literal_true":
            True,

        "submitted_metadata_required":
            True,

        "submitted_metadata_coordination_required":
            True,

        "submitted_metadata_coordination_must_match_mapping": [
            "workflow_id",
            "correlation_id",
            "stage_id",
        ],

        "submitted_metadata_coordination_should_match_request_authority": [
            "stage_version",
            "workflow_type",
            "wave_index",
        ],

        "job_identity_cross_checks_remain_required": [
            "workspace_id",
            "job_type",
            "pipeline",
            "stage",
        ],

        "job_id_generation":
            False,

        "job_id_rewrite":
            False,

        "runtime_submission_authority":
            False,

        "runtime_persistence_authority":
            False,

        "queue_authority":
            False,

        "business_execution_authority":
            False,
    },

    "patch_scope": {
        "allowed_production_file":
            (
                "backend/server/coordination/runtime_integration/"
                "workflow_job_correlation.py"
            ),

        "other_phase_5_files_may_change":
            False,

        "runtime_files_may_change":
            False,

        "orchestration_files_may_change":
            False,

        "stage_result_contract_may_change":
            False,
    },

    "recertification_required": [
        "Phase 5.3 focused corrective verification",
        "Phase 5.3 full recertification",
        "new Phase 5.3 SHA256",
        "replacement Phase 5.3 freeze manifest",
        "Phase 5.6 integration certification",
    ],

    "invalidated_at_utc":
        datetime.now(
            timezone.utc
        ).isoformat(),
}


INVALIDATION.write_text(
    json.dumps(
        record,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 120)
print("PHASE 5.3 — CONTROLLED INVALIDATION RECORDED")
print("=" * 120)
print(
    "Frozen production SHA:",
    actual_phase_5_3_sha,
)
print(
    "Frozen manifest SHA:",
    actual_manifest_sha,
)
print(
    "Invalidation record:",
    str(
        INVALIDATION.relative_to(ROOT)
    ).replace(
        "\\",
        "/",
    ),
)
print(
    "Invalidation record SHA256:",
    sha256(
        INVALIDATION
    ),
)
print()
print("Production modified: False")
print("Frozen manifest modified: False")
print("Classification: MISSED CERTIFICATION REQUIREMENT")
print()
print("NEXT: Corrective Phase 5.3 Architecture Resolution")
print("=" * 120)
