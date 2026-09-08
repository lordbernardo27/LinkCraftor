from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

PRODUCTION = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "workflow_job_correlation.py"
)

HISTORICAL_MANIFEST = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "workflow_job_correlation.freeze.json"
)

INVALIDATION = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "workflow_job_correlation.phase_5_6_invalidation.json"
)

NEW_MANIFEST = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "workflow_job_correlation.freeze.v5.3.1.json"
)


EXPECTED_PRODUCTION_SHA = (
    "13B007B1F74A131250476432B14381CC"
    "81C916F48CE121B44877964A18A73AB6"
)

EXPECTED_HISTORICAL_MANIFEST_SHA = (
    "53F2B149EF904CE5692D85F349038CEA"
    "B901E00B06C6C273CA5B74EB31ACE8E5"
)

EXPECTED_INVALIDATION_SHA = (
    "80176F8807C1E399FAC4F74FB2D6CDAD"
    "B899F3C44643B268B6FC62694F103F65"
)

VERSION = (
    "workflow_job_correlation_v5.3.1"
)

SCHEMA = (
    "workflow_job_correlation_schema_v1"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


production_sha = sha256(
    PRODUCTION
)

historical_manifest_sha = sha256(
    HISTORICAL_MANIFEST
)

invalidation_sha = sha256(
    INVALIDATION
)


# =========================================================================
# 1. Freeze preconditions
# =========================================================================

if production_sha != EXPECTED_PRODUCTION_SHA:
    raise SystemExit(
        (
            "FREEZE REFUSED: corrective Phase 5.3 "
            "production SHA changed.\n"
            f"Expected: {EXPECTED_PRODUCTION_SHA}\n"
            f"Actual:   {production_sha}"
        )
    )


if (
    historical_manifest_sha
    != EXPECTED_HISTORICAL_MANIFEST_SHA
):
    raise SystemExit(
        (
            "FREEZE REFUSED: historical v5.3.0 "
            "freeze manifest changed."
        )
    )


if invalidation_sha != EXPECTED_INVALIDATION_SHA:
    raise SystemExit(
        (
            "FREEZE REFUSED: Phase 5.6 invalidation "
            "record changed."
        )
    )


if NEW_MANIFEST.exists():
    raise SystemExit(
        (
            "FREEZE REFUSED: replacement manifest "
            "already exists: "
            + str(
                NEW_MANIFEST.relative_to(ROOT)
            )
        )
    )


# =========================================================================
# 2. Replacement canonical freeze manifest
# =========================================================================

manifest = {
    "component":
        "Workflow/Job Correlation",

    "phase":
        "5.3",

    "canonical":
        True,

    "frozen":
        True,

    "replacement_freeze":
        True,

    "version":
        VERSION,

    "schema_version":
        SCHEMA,

    "production_file":
        str(
            PRODUCTION.relative_to(ROOT)
        ).replace(
            "\\",
            "/",
        ),

    "production_sha256":
        production_sha,

    "corrective_history": {
        "previous_version":
            "workflow_job_correlation_v5.3.0",

        "previous_production_sha256":
            (
                "C0D88ECC69680106B6833DF8CB3113FC"
                "9ABD23C1EE8B7D413BA4AAE3375648FA"
            ),

        "historical_freeze_manifest":
            (
                "backend/server/coordination/runtime_integration/"
                "workflow_job_correlation.freeze.json"
            ),

        "historical_freeze_manifest_sha256":
            historical_manifest_sha,

        "invalidation_record":
            (
                "backend/server/coordination/runtime_integration/"
                "workflow_job_correlation."
                "phase_5_6_invalidation.json"
            ),

        "invalidation_record_sha256":
            invalidation_sha,

        "invalidation_reason":
            "missed_certification_requirement",

        "trigger_phase":
            "5.6 Runtime Integration Certification",
    },

    "corrective_requirements": {
        "submitted_submission_required":
            True,

        "submission_persisted_literal_true":
            True,

        "submission_queued_literal_true":
            True,

        "submission_canonical_identity_preserved_literal_true":
            True,

        "submitted_metadata_required":
            True,

        "submitted_coordination_required":
            True,

        "submitted_coordination_mapping_cross_checks": [
            "workflow_id",
            "correlation_id",
            "stage_id",
        ],

        "submitted_coordination_request_cross_checks": [
            "stage_version",
            "workflow_type",
            "wave_index",
        ],
    },

    "retained_guarantees": {
        "primary_reverse_lookup":
            "job_id",

        "exact_duplicate":
            "idempotent_reuse",

        "conflicting_duplicate":
            "fail_closed",

        "job_identity_cross_checks": [
            "workspace_id",
            "job_type",
            "pipeline",
            "stage",
        ],

        "persistent_correlation_store":
            False,

        "runtime_execution_authority":
            False,

        "runtime_submission_authority":
            False,

        "runtime_persistence_authority":
            False,
    },

    "certification": {
        "corrective_architecture_resolution": {
            "passed":
                94,

            "failed":
                0,
        },

        "focused_corrective_verification": {
            "passed":
                40,

            "failed":
                0,
        },

        "full_recertification": {
            "passed":
                71,

            "failed":
                0,
        },
    },

    "historical_manifest_status":
        "retained_as_invalidated_v5.3.0_evidence",

    "next_phase":
        "5.6 Runtime Integration Certification",

    "frozen_at_utc":
        datetime.now(
            timezone.utc
        ).isoformat(),
}


NEW_MANIFEST.write_text(
    json.dumps(
        manifest,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


new_manifest_sha = sha256(
    NEW_MANIFEST
)


# =========================================================================
# 3. Post-write immutability checks
# =========================================================================

if sha256(
    PRODUCTION
) != EXPECTED_PRODUCTION_SHA:
    raise SystemExit(
        (
            "FREEZE FAILED: production changed "
            "during manifest creation."
        )
    )


if (
    sha256(
        HISTORICAL_MANIFEST
    )
    != EXPECTED_HISTORICAL_MANIFEST_SHA
):
    raise SystemExit(
        (
            "FREEZE FAILED: historical manifest "
            "was modified."
        )
    )


if (
    sha256(
        INVALIDATION
    )
    != EXPECTED_INVALIDATION_SHA
):
    raise SystemExit(
        (
            "FREEZE FAILED: invalidation record "
            "was modified."
        )
    )


print()
print("=" * 120)
print("LINKCRAFTOR")
print("PHASE 5.3 — WORKFLOW/JOB CORRELATION")
print("CORRECTIVE REPLACEMENT SHA256 FREEZE")
print("=" * 120)
print()
print(
    "Production:",
    str(
        PRODUCTION.relative_to(ROOT)
    ).replace(
        "\\",
        "/",
    ),
)
print(
    "Version:",
    VERSION,
)
print(
    "Schema:",
    SCHEMA,
)
print(
    "Production SHA256:",
    production_sha,
)
print()
print(
    "Replacement freeze manifest:",
    str(
        NEW_MANIFEST.relative_to(ROOT)
    ).replace(
        "\\",
        "/",
    ),
)
print(
    "Replacement manifest SHA256:",
    new_manifest_sha,
)
print()
print(
    "Historical v5.3.0 manifest SHA256:",
    historical_manifest_sha,
)
print(
    "Invalidation record SHA256:",
    invalidation_sha,
)
print()
print("Certification:")
print("  Corrective Architecture: 94/94")
print("  Focused Verification: 40/40")
print("  Full Recertification: 71/71")
print()
print("Canonical: TRUE")
print("Frozen: TRUE")
print("Historical freeze overwritten: FALSE")
print("Corrective Phase 5.3: COMPLETE")
print()
print(
    "NEXT:",
    "Resume Phase 5.6 Runtime Integration Certification",
)
print("=" * 120)
