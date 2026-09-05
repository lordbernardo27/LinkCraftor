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
      "runtime_job_mapping.py"
)

FREEZE_MANIFEST = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "runtime_job_mapping.freeze.json"
)

REPORT = (
    ROOT
    / "runtime_job_mapping_phase_5_2_sha256_freeze.txt"
)


EXPECTED_SHA = (
    "49227B0686DED28418DE7DEF21101643"
    "18DDCA3858469A05F5A596388BA84E6A"
)

EXPECTED_5_1_SHA = (
    "2DD7AF262C879B4DD58A484AB7470D9E"
    "A9883A80DDE3C77F1DC1ACDFD35CD0E2"
)

EXPECTED_CREATION_ENGINE_SHA = (
    "7BFDC36731B7AD48885258BCBA833718"
    "6430EC1C6A7C2E876ACA223E6E05D63F"
)


FROZEN_5_1 = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "coordination_runtime_bridge.py"
)

CREATION_ENGINE = (
    ROOT
    / "backend/server/runtime/universal_jobs/"
      "creation_engine.py"
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
        "FREEZE REFUSED: Phase 5.2 production SHA changed.\n"
        f"Expected: {EXPECTED_SHA}\n"
        f"Actual:   {production_sha}"
    )


phase_5_1_sha = sha256(
    FROZEN_5_1
)

if phase_5_1_sha != EXPECTED_5_1_SHA:
    raise SystemExit(
        "FREEZE REFUSED: frozen Phase 5.1 SHA changed."
    )


creation_engine_sha = sha256(
    CREATION_ENGINE
)

if (
    creation_engine_sha
    != EXPECTED_CREATION_ENGINE_SHA
):
    raise SystemExit(
        "FREEZE REFUSED: Universal Job Creation Engine SHA changed."
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


manifest = {
    "framework":
        "LinkCraftor Universal Coordination Framework",

    "phase":
        "5.2",

    "component":
        "Runtime Job Mapping",

    "version":
        "runtime_job_mapping_v5.2.0",

    "schema":
        "runtime_job_mapping_schema_v1",

    "production_file":
        (
            "backend/server/coordination/runtime_integration/"
            "runtime_job_mapping.py"
        ),

    "production_sha256":
        production_sha,

    "upstream_phase_5_1_file":
        (
            "backend/server/coordination/runtime_integration/"
            "coordination_runtime_bridge.py"
        ),

    "upstream_phase_5_1_sha256":
        phase_5_1_sha,

    "runtime_creation_engine_file":
        (
            "backend/server/runtime/universal_jobs/"
            "creation_engine.py"
        ),

    "runtime_creation_engine_sha256":
        creation_engine_sha,

    "certification": {
        "installation_smoke": {
            "passed": 80,
            "failed": 0,
        },

        "initial_verification": {
            "passed": 33,
            "failed": 0,
        },

        "final_certification": {
            "passed": 70,
            "failed": 0,
        },
    },

    "architectural_boundary": {
        "input":
            "Phase 5.1 CoordinationRuntimeBridgeResult",

        "output":
            "Immutable RuntimeJobMappingResult containing "
            "UniversalJobCreationRequest",

        "universal_job_creation":
            False,

        "runtime_registration_lookup":
            False,

        "submission":
            False,

        "persistence":
            False,

        "queue_write":
            False,

        "handler_dispatch":
            False,

        "business_execution":
            False,

        "workflow_job_correlation":
            False,

        "pipeline_run_id_generation":
            False,

        "job_id_generation":
            False,

        "idempotency_key_generation":
            False,

        "phase_5_3_owns_correlation":
            True,
    },

    "direct_mapping": {
        "workspace_id":
            "workspace_id",

        "job_type":
            "job_type",

        "payload":
            "payload",

        "pipeline_id":
            "pipeline",

        "runtime_stage":
            "stage",
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
    "PHASE 5.2 — RUNTIME JOB MAPPING",
    "SHA256 FREEZE",
    "=" * 120,
    "",
    (
        "Production file: "
        "backend/server/coordination/runtime_integration/"
        "runtime_job_mapping.py"
    ),
    "Version: runtime_job_mapping_v5.2.0",
    "Schema: runtime_job_mapping_schema_v1",
    f"Production SHA256: {production_sha}",
    (
        "Freeze manifest: "
        "backend/server/coordination/runtime_integration/"
        "runtime_job_mapping.freeze.json"
    ),
    f"Freeze manifest SHA256: {manifest_sha}",
    "",
    "Certification:",
    "  Installation Smoke: 80/80",
    "  Initial Verification: 33/33",
    "  Final Certification: 70/70",
    "",
    "Canonical: TRUE",
    "Frozen: TRUE",
    "Status: PHASE 5.2 COMPLETE",
    "",
    "NEXT: Phase 5.3 — Workflow/Job Correlation",
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
print("PHASE 5.2 SHA256 FREEZE COMPLETE")
print("=" * 120)
print(
    "VERSION:",
    "runtime_job_mapping_v5.2.0",
)
print(
    "SCHEMA:",
    "runtime_job_mapping_schema_v1",
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
    "PHASE 5.2 COMPLETE",
)
print(
    "NEXT:",
    "Phase 5.3 — Workflow/Job Correlation",
)
print("=" * 120)
