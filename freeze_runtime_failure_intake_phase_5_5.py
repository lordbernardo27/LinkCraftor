from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

PRODUCTION = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "runtime_failure_intake.py"
)

MANIFEST = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "runtime_failure_intake.freeze.json"
)

EXPECTED_PRODUCTION_SHA = (
    "CDEE8D641AC045956E2A203BF0A62DE7"
    "0933F0755B946D63310EFBABE7DFE241"
)

VERSION = (
    "runtime_failure_intake_v5.5.0"
)

SCHEMA = (
    "runtime_failure_intake_schema_v1"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


actual_sha = sha256(
    PRODUCTION
)


if actual_sha != EXPECTED_PRODUCTION_SHA:
    raise SystemExit(
        (
            "FREEZE REFUSED: production SHA changed.\n"
            f"Expected: {EXPECTED_PRODUCTION_SHA}\n"
            f"Actual:   {actual_sha}"
        )
    )


if MANIFEST.exists():
    raise SystemExit(
        (
            "FREEZE REFUSED: manifest already exists: "
            + str(
                MANIFEST.relative_to(ROOT)
            )
        )
    )


manifest = {
    "component":
        "Runtime Failure Intake",

    "phase":
        "5.5",

    "canonical":
        True,

    "frozen":
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
        actual_sha,

    "certification": {
        "architecture_resolution": {
            "passed": 93,
            "failed": 0,
        },

        "installation_smoke": {
            "passed": 79,
            "failed": 0,
        },

        "initial_verification": {
            "passed": 75,
            "failed": 0,
        },

        "final_certification": {
            "passed": 101,
            "failed": 0,
        },
    },

    "authorities": {
        "coordination_identity":
            "Phase 5.3 WorkflowJobCorrelation",

        "terminal_status":
            "canonical orchestration persisted job.status == failed",

        "terminal_event":
            "RUNNING -> FAILED JobStatusEvent",

        "attempt_start":
            "QUEUED -> RUNNING JobStatusEvent",

        "result_id":
            "FAILED JobStatusEvent.event_id",

        "started_at":
            (
                "final attempt QUEUED -> RUNNING "
                "JobStatusEvent.created_at"
            ),

        "finished_at":
            (
                "RUNNING -> FAILED JobStatusEvent.created_at"
            ),

        "failure_code":
            "runtime_dispatch_error_type",

        "failure_message":
            "persisted orchestration job.error_message",

        "failure_details":
            "canonical persisted Runtime failure evidence",
    },

    "terminal_proof": {
        "job_status":
            "failed",

        "runtime_dispatch_failed":
            True,

        "runtime_dispatch_completed":
            False,

        "runtime_retry_scheduled":
            False,

        "canonical_job_id_preserved":
            True,

        "retry_created_new_job":
            False,
    },

    "required_failure_details": [
        "runtime_dispatch_completed",
        "runtime_dispatch_failed",
        "runtime_retry_scheduled",
        "runtime_failure_attempt_count",
        "runtime_maximum_attempts",
        "runtime_retry_type_allowed",
        "runtime_retry_exhausted",
        "runtime_contract_error",
        "runtime_dispatch_error_type",
        "canonical_job_id_preserved",
        "retry_created_new_job",
        "runtime_worker_version",
    ],

    "boundaries": {
        "runtime_job_creation":
            False,

        "runtime_submission":
            False,

        "runtime_status_mutation":
            False,

        "runtime_requeue":
            False,

        "retry_policy_decision":
            False,

        "retry_policy_recalculation":
            False,

        "attempt_count_mutation":
            False,

        "runtime_dispatch":
            False,

        "handler_execution":
            False,

        "failure_persistence":
            False,

        "success_processing":
            False,

        "workflow_recovery":
            False,

        "workflow_compensation":
            False,

        "correlation_creation":
            False,

        "random_result_id_generation":
            False,

        "wall_clock_timestamp_generation":
            False,
    },

    "retry_semantics": {
        "retryable_transition":
            "RUNNING -> QUEUED",

        "retryable_stage_result_failed":
            False,

        "terminal_transition":
            "RUNNING -> FAILED",
    },

    "workflow_recovery_owner":
        "Phase 9 Coordination Recovery",

    "next_phase":
        "5.6 Runtime Integration Certification",

    "frozen_at_utc":
        datetime.now(
            timezone.utc
        ).isoformat(),
}


MANIFEST.write_text(
    json.dumps(
        manifest,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


manifest_sha = sha256(
    MANIFEST
)


print()
print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 5.5 — RUNTIME FAILURE INTAKE")
print("SHA256 FREEZE")
print("=" * 120)
print()
print(
    "Production file:",
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
    actual_sha,
)
print(
    "Freeze manifest:",
    str(
        MANIFEST.relative_to(ROOT)
    ).replace(
        "\\",
        "/",
    ),
)
print(
    "Freeze manifest SHA256:",
    manifest_sha,
)
print()
print("Certification:")
print("  Architecture Resolution: 93/93")
print("  Installation Smoke: 79/79")
print("  Initial Verification: 75/75")
print("  Final Certification: 101/101")
print()
print("Canonical: TRUE")
print("Frozen: TRUE")
print("Status: PHASE 5.5 COMPLETE")
print()
print("NEXT: Phase 5.6 — Runtime Integration Certification")
print("=" * 120)
