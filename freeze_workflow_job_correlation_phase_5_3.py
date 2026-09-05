from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

PRODUCTION = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "workflow_job_correlation.py"
)

FREEZE_MANIFEST = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "workflow_job_correlation.freeze.json"
)

REPORT = (
    ROOT
    / "workflow_job_correlation_phase_5_3_sha256_freeze.txt"
)


EXPECTED_SHA = (
    "C0D88ECC69680106B6833DF8CB3113FC"
    "9ABD23C1EE8B7D413BA4AAE3375648FA"
)

EXPECTED_5_2_SHA = (
    "49227B0686DED28418DE7DEF21101643"
    "18DDCA3858469A05F5A596388BA84E6A"
)

EXPECTED_SUBMISSION_SHA = (
    "07BA2DA8C0A2CFA899DE696D7892652"
    "A0AA6D56939B364C8C6B7F0B741B05704"
)

EXPECTED_STAGE_RESULT_SHA = (
    "B3469B10BB2F8F9372E4336784D09A14"
    "3C78FABE45BF039B61B76F4A2DC33B24"
)

EXPECTED_RUN_IDENTITY_SHA = (
    "B43C2C86B07F06FA3B89C4BF2B14E68"
    "DC82DEA1E23112AE44E35139266AA6626"
)


PHASE_5_2 = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "runtime_job_mapping.py"
)

SUBMISSION = (
    ROOT
    / "backend/server/runtime/"
      "universal_job_submission.py"
)

STAGE_RESULT = (
    ROOT
    / "backend/server/coordination/universal_stages/"
      "result_contract.py"
)

RUN_IDENTITY = (
    ROOT
    / "backend/server/runtime/universal_orchestration/"
      "run_identity.py"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


production_sha = sha256(
    PRODUCTION
)

if production_sha != EXPECTED_SHA:
    raise SystemExit(
        "FREEZE REFUSED: Phase 5.3 production SHA changed.\n"
        f"Expected: {EXPECTED_SHA}\n"
        f"Actual:   {production_sha}"
    )


phase_5_2_sha = sha256(
    PHASE_5_2
)

if phase_5_2_sha != EXPECTED_5_2_SHA:
    raise SystemExit(
        "FREEZE REFUSED: frozen Phase 5.2 SHA changed."
    )


submission_sha = sha256(
    SUBMISSION
)

if submission_sha != EXPECTED_SUBMISSION_SHA:
    raise SystemExit(
        "FREEZE REFUSED: Universal Job Submission SHA changed."
    )


stage_result_sha = sha256(
    STAGE_RESULT
)

if stage_result_sha != EXPECTED_STAGE_RESULT_SHA:
    raise SystemExit(
        "FREEZE REFUSED: StageResult contract SHA changed."
    )


run_identity_sha = sha256(
    RUN_IDENTITY
)

if run_identity_sha != EXPECTED_RUN_IDENTITY_SHA:
    raise SystemExit(
        "FREEZE REFUSED: Runtime orchestration identity SHA changed."
    )


git_status = subprocess.run(
    [
        "git",
        "status",
        "--short",
        "--",
        "backend/server/coordination/runtime_integration",
        "backend/server/runtime",
    ],
    cwd=ROOT,
    capture_output=True,
    text=True,
    check=True,
).stdout.strip()


status_lines = tuple(
    line
    for line
    in git_status.splitlines()
    if line.strip()
)


runtime_modified = any(
    "backend/server/runtime/"
    in line.replace(
        "\\",
        "/",
    )
    for line
    in status_lines
)

if runtime_modified:
    raise SystemExit(
        "FREEZE REFUSED: backend/server/runtime production changed."
    )


scope_ok = all(
    "backend/server/coordination/runtime_integration/"
    in line.replace(
        "\\",
        "/",
    )
    for line
    in status_lines
) if status_lines else False


if not scope_ok:
    raise SystemExit(
        "FREEZE REFUSED: changes exist outside runtime_integration scope."
    )


manifest = {
    "framework":
        "LinkCraftor Universal Coordination Framework",

    "phase":
        "5.3",

    "component":
        "Workflow/Job Correlation",

    "version":
        "workflow_job_correlation_v5.3.0",

    "schema":
        "workflow_job_correlation_schema_v1",

    "production_file":
        (
            "backend/server/coordination/runtime_integration/"
            "workflow_job_correlation.py"
        ),

    "production_sha256":
        production_sha,

    "authoritative_inputs": {
        "phase_5_2_file":
            (
                "backend/server/coordination/runtime_integration/"
                "runtime_job_mapping.py"
            ),

        "phase_5_2_sha256":
            phase_5_2_sha,

        "submission_file":
            (
                "backend/server/runtime/"
                "universal_job_submission.py"
            ),

        "submission_sha256":
            submission_sha,

        "stage_result_file":
            (
                "backend/server/coordination/universal_stages/"
                "result_contract.py"
            ),

        "stage_result_sha256":
            stage_result_sha,

        "runtime_orchestration_identity_file":
            (
                "backend/server/runtime/universal_orchestration/"
                "run_identity.py"
            ),

        "runtime_orchestration_identity_sha256":
            run_identity_sha,
    },

    "certification": {
        "installation_smoke": {
            "passed": 71,
            "failed": 0,
        },

        "initial_verification": {
            "passed": 73,
            "failed": 0,
        },

        "final_certification": {
            "passed": 81,
            "failed": 0,
        },
    },

    "correlation_record_fields": [
        "workflow_id",
        "correlation_id",
        "stage_id",
        "stage_version",
        "workflow_type",
        "workspace_id",
        "job_id",
        "job_type",
        "pipeline_id",
        "runtime_stage",
        "wave_index",
    ],

    "canonical_rules": {
        "binding_time":
            "after successful canonical Universal Job submission",

        "primary_reverse_lookup":
            "job_id",

        "exact_duplicate":
            "idempotent_reuse",

        "conflicting_duplicate":
            "fail_closed",

        "workflow_may_have_multiple_jobs":
            True,

        "stage_may_have_historical_multiple_jobs":
            True,

        "job_id_generation":
            False,

        "job_id_rewrite":
            False,

        "workflow_id_to_pipeline_run_id":
            False,

        "correlation_id_to_pipeline_run_id":
            False,

        "orchestration_run_id_generation":
            False,

        "persistent_correlation_storage":
            False,

        "persistence_owner":
            "Phase 8 Workflow State Persistence",
    },

    "execution_authority": {
        "universal_job_creation":
            False,

        "runtime_registration_lookup":
            False,

        "submission":
            False,

        "runtime_persistence":
            False,

        "queue_write":
            False,

        "dispatch":
            False,

        "business_execution":
            False,

        "workflow_lifecycle_transition":
            False,

        "completion_processing":
            False,

        "failure_processing":
            False,
    },

    "canonical":
        True,

    "frozen":
        True,

    "frozen_at":
        datetime.now(
            timezone.utc
        ).isoformat(),

    "git_status_at_freeze":
        git_status,
}


FREEZE_MANIFEST.write_text(
    json.dumps(
        manifest,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


manifest_sha = sha256(
    FREEZE_MANIFEST
)


report_lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.3 — WORKFLOW/JOB CORRELATION",
    "SHA256 FREEZE",
    "=" * 120,
    "",
    (
        "Production file: "
        "backend/server/coordination/runtime_integration/"
        "workflow_job_correlation.py"
    ),
    "Version: workflow_job_correlation_v5.3.0",
    "Schema: workflow_job_correlation_schema_v1",
    f"Production SHA256: {production_sha}",
    (
        "Freeze manifest: "
        "backend/server/coordination/runtime_integration/"
        "workflow_job_correlation.freeze.json"
    ),
    f"Freeze manifest SHA256: {manifest_sha}",
    "",
    "Certification:",
    "  Installation Smoke: 71/71",
    "  Initial Verification: 73/73",
    "  Final Certification: 81/81",
    "",
    "Canonical: TRUE",
    "Frozen: TRUE",
    "Status: PHASE 5.3 COMPLETE",
    "",
    "NEXT: Phase 5.4 — Runtime Completion Intake",
]


REPORT.write_text(
    "\n".join(
        report_lines
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 120)
print("PHASE 5.3 SHA256 FREEZE COMPLETE")
print("=" * 120)
print(
    "VERSION:",
    "workflow_job_correlation_v5.3.0",
)
print(
    "SCHEMA:",
    "workflow_job_correlation_schema_v1",
)
print(
    "PRODUCTION SHA256:",
    production_sha,
)
print(
    "FREEZE MANIFEST SHA256:",
    manifest_sha,
)
print(
    "CANONICAL:",
    True,
)
print(
    "FROZEN:",
    True,
)
print(
    "STATUS:",
    "PHASE 5.3 COMPLETE",
)
print(
    "NEXT:",
    "Phase 5.4 — Runtime Completion Intake",
)
print("=" * 120)
