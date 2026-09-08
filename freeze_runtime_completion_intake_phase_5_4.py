from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

PRODUCTION = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "runtime_completion_intake.py"
)

MANIFEST = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "runtime_completion_intake.freeze.json"
)

EXPECTED_PRODUCTION_SHA = (
    "A9F2A8E4242A08A2BDBE6AF0B96DC104"
    "2A53DDD3B2F72BB355259FA0E5D2E6FB"
)

VERSION = (
    "runtime_completion_intake_v5.4.0"
)

SCHEMA = (
    "runtime_completion_intake_schema_v1"
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
        "Runtime Completion Intake",

    "phase":
        "5.4",

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
            "passed":
                81,

            "failed":
                0,
        },

        "installation_smoke": {
            "passed":
                79,

            "failed":
                0,
        },

        "initial_verification": {
            "passed":
                46,

            "failed":
                0,
        },

        "final_certification": {
            "passed":
                57,

            "failed":
                0,
        },
    },

    "authorities": {
        "coordination_identity":
            "Phase 5.3 WorkflowJobCorrelation",

        "completion_status":
            "canonical orchestration persisted job",

        "completion_timing":
            "orchestration JobStatusEvent trail",

        "result_id":
            "RUNNING->COMPLETED JobStatusEvent.event_id",

        "started_at":
            (
                "QUEUED->RUNNING JobStatusEvent.created_at "
                "for completed attempt"
            ),

        "finished_at":
            (
                "RUNNING->COMPLETED JobStatusEvent.created_at"
            ),

        "output":
            "runtime_dispatch_result",
    },

    "boundaries": {
        "runtime_job_creation":
            False,

        "runtime_submission":
            False,

        "runtime_status_mutation":
            False,

        "runtime_progress_mutation":
            False,

        "runtime_dispatch":
            False,

        "handler_execution":
            False,

        "completion_persistence":
            False,

        "failure_processing":
            False,

        "random_result_id_generation":
            False,

        "wall_clock_timestamp_generation":
            False,

        "correlation_creation":
            False,
    },

    "next_phase":
        "5.5 Runtime Failure Intake",

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
print("PHASE 5.4 — RUNTIME COMPLETION INTAKE")
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
print("  Architecture Resolution: 81/81")
print("  Installation Smoke: 79/79")
print("  Initial Verification: 46/46")
print("  Final Certification: 57/57")
print()
print("Canonical: TRUE")
print("Frozen: TRUE")
print("Status: PHASE 5.4 COMPLETE")
print()
print("NEXT: Phase 5.5 — Runtime Failure Intake")
print("=" * 120)
