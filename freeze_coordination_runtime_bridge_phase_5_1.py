from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

BRIDGE = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "coordination_runtime_bridge.py"
)

FREEZE = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "coordination_runtime_bridge.freeze.json"
)

REPORT = (
    ROOT
    / "coordination_runtime_bridge_phase_5_1_sha256_freeze.txt"
)

EXPECTED_SHA = (
    "2DD7AF262C879B4DD58A484AB7470D9E"
    "A9883A80DDE3C77F1DC1ACDFD35CD0E2"
)

VERSION = (
    "coordination_runtime_bridge_v5.1.0"
)

SCHEMA = (
    "coordination_runtime_bridge_schema_v1"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


actual_sha = sha256(
    BRIDGE
)

if actual_sha != EXPECTED_SHA:
    raise SystemExit(
        "FREEZE REFUSED: Phase 5.1 production SHA changed.\n"
        f"Expected: {EXPECTED_SHA}\n"
        f"Actual:   {actual_sha}"
    )


payload = {
    "phase": "5.1",
    "component": "Coordination -> Runtime Bridge",
    "version": VERSION,
    "schema_version": SCHEMA,
    "production_file": (
        "backend/server/coordination/runtime_integration/"
        "coordination_runtime_bridge.py"
    ),
    "sha256": actual_sha,
    "certification": {
        "installation_smoke": {
            "passed": 57,
            "failed": 0,
        },
        "initial_verification": {
            "passed": 76,
            "failed": 0,
        },
        "final_certification": {
            "passed": 61,
            "failed": 0,
            "certified": True,
        },
    },
    "architectural_boundary": {
        "upstream": "Phase 4.5 ExecutionPlan",
        "downstream": "Phase 5.2 Runtime Job Mapping",
        "read_only": True,
        "deterministic": True,
        "fail_closed": True,
        "creates_universal_jobs": False,
        "performs_runtime_registration_lookup": False,
        "dispatches_handlers": False,
        "executes_business_stages": False,
        "persists_state": False,
        "writes_queue": False,
        "processes_completion": False,
        "processes_failure": False,
    },
    "frozen_at": datetime.now(
        timezone.utc
    ).isoformat(),
    "canonical": True,
}


FREEZE.write_text(
    json.dumps(
        payload,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


freeze_sha = sha256(
    FREEZE
)


lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.1 — COORDINATION -> RUNTIME BRIDGE",
    "SHA256 FREEZE",
    "=" * 112,
    "",
    f"Production file: {payload['production_file']}",
    f"Version: {VERSION}",
    f"Schema: {SCHEMA}",
    f"Production SHA256: {actual_sha}",
    f"Freeze manifest: {FREEZE.relative_to(ROOT)}",
    f"Freeze manifest SHA256: {freeze_sha}",
    "",
    "Certification:",
    "  Installation Smoke: 57/57",
    "  Initial Verification: 76/76",
    "  Final Certification: 61/61",
    "",
    "Canonical: TRUE",
    "Frozen: TRUE",
    "Status: PHASE 5.1 COMPLETE",
    "",
    "NEXT: Phase 5.2 — Runtime Job Mapping",
]


REPORT.write_text(
    "\n".join(
        lines
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 112)
print("PHASE 5.1 SHA256 FREEZE COMPLETE")
print("=" * 112)
print("VERSION:", VERSION)
print("SCHEMA:", SCHEMA)
print("PRODUCTION SHA256:", actual_sha)
print("FREEZE MANIFEST SHA256:", freeze_sha)
print("CANONICAL: TRUE")
print("FROZEN: TRUE")
print("STATUS: PHASE 5.1 COMPLETE")
print("NEXT: Phase 5.2 — Runtime Job Mapping")
print("REPORT:", REPORT.name)
print("=" * 112)
