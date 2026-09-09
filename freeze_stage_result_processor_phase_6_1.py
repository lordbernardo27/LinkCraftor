from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

PROCESSOR = (
    ROOT
    / "backend/server/coordination/stage_handoff/stage_result_processor.py"
)

REPORT = (
    ROOT
    / "stage_result_processor_phase_6_1_final_certification.txt"
)

FREEZE = (
    ROOT
    / "backend/server/coordination/stage_handoff/"
      "stage_result_processor.phase_6_1.freeze.json"
)

EXPECTED_PROCESSOR_SHA = (
    "8106D844B0B4D1C4D4E3A07A6232F4796010C604F538ED0F8E45F823D2C64456"
)

EXPECTED_REPORT_SHA = (
    "35D0E6F8E6283CCB2702570C8EFC72ACA9B80B9276CC31A8E1877E6CB74A19BB"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


if FREEZE.exists():
    raise SystemExit(
        "FREEZE REFUSED: Phase 6.1 freeze already exists.\n"
        + str(FREEZE)
    )


if not PROCESSOR.exists():
    raise SystemExit(
        "FREEZE REFUSED: processor source missing"
    )


if not REPORT.exists():
    raise SystemExit(
        "FREEZE REFUSED: final certification report missing"
    )


processor_sha = sha256(
    PROCESSOR
)

report_sha = sha256(
    REPORT
)


if processor_sha != EXPECTED_PROCESSOR_SHA:
    raise SystemExit(
        "FREEZE REFUSED: processor SHA mismatch\n"
        f"Expected: {EXPECTED_PROCESSOR_SHA}\n"
        f"Actual:   {processor_sha}"
    )


if report_sha != EXPECTED_REPORT_SHA:
    raise SystemExit(
        "FREEZE REFUSED: certification report SHA mismatch\n"
        f"Expected: {EXPECTED_REPORT_SHA}\n"
        f"Actual:   {report_sha}"
    )


report_text = REPORT.read_text(
    encoding="utf-8"
)


required_report_markers = (
    "Checks: 87",
    "Passed: 87",
    "Failed: 0",
    "FINAL CERTIFIED: True",
    f"Processor SHA256: {EXPECTED_PROCESSOR_SHA}",
)


for marker in required_report_markers:
    if marker not in report_text:
        raise SystemExit(
            "FREEZE REFUSED: missing certification marker: "
            + marker
        )


freeze_document = {
    "component":
        "Stage Result Processor",

    "framework":
        "Universal Coordination Framework",

    "phase":
        "6.1",

    "freeze_version":
        "stage_result_processor_phase_6_1_freeze_v1",

    "certification_status":
        "certified",

    "certified":
        True,

    "processor": {
        "path":
            "backend/server/coordination/stage_handoff/"
            "stage_result_processor.py",

        "version":
            "stage_result_processor_v6.1.0",

        "schema_version":
            "stage_result_processor_schema_v1",

        "sha256":
            processor_sha,
    },

    "verification": {
        "smoke":
            {
                "passed":
                    52,
                "failed":
                    0,
            },

        "initial":
            {
                "passed":
                    112,
                "failed":
                    0,
            },

        "final":
            {
                "passed":
                    87,
                "failed":
                    0,
            },

        "total_formal_checks":
            251,
    },

    "final_certification_report": {
        "path":
            "stage_result_processor_phase_6_1_final_certification.txt",

        "sha256":
            report_sha,
    },

    "canonical_input":
        "UniversalStageResult",

    "canonical_dispositions": {
        "completed": {
            "normal_handoff_allowed":
                True,
            "prerequisite_satisfied":
                True,
        },

        "failed": {
            "normal_handoff_allowed":
                False,
            "prerequisite_satisfied":
                False,
        },

        "skipped": {
            "normal_handoff_allowed":
                False,
            "prerequisite_satisfied":
                False,
            "advanced_skip_semantics_owner":
                "Phase 7.7",
        },

        "cancelled": {
            "normal_handoff_allowed":
                False,
            "prerequisite_satisfied":
                False,
            "workflow_cancellation_owner":
                "workflow lifecycle subsystem",
        },
    },

    "certified_boundaries": [
        "no Runtime submission",
        "no Runtime worker execution",
        "no orchestration job mutation",
        "no coordinator invocation",
        "no workflow lifecycle mutation",
        "no output-to-input mapping",
        "no context propagation",
        "no artifact handoff",
        "no advanced skip semantics",
    ],

    "freeze_created_at":
        datetime.now(
            timezone.utc
        ).isoformat(),

    "next":
        "6.2 Output -> Input Mapping",
}


FREEZE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

FREEZE.write_text(
    json.dumps(
        freeze_document,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)


freeze_sha = sha256(
    FREEZE
)


print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 6.1 — STAGE RESULT PROCESSOR SHA256 FREEZE")
print("=" * 120)
print("Smoke Verification: 52/52")
print("Initial Verification: 112/112")
print("Final Certification: 87/87")
print("Total Formal Checks: 251 PASS")
print("PHASE 6.1 CERTIFIED: TRUE")
print("PHASE 6.1 FROZEN: TRUE")
print("PROCESSOR SHA256:", processor_sha)
print("REPORT SHA256:", report_sha)
print("FREEZE FILE:", FREEZE)
print("FREEZE SHA256:", freeze_sha)
print("Production processor modified: FALSE")
print("NEXT: 6.2 Output -> Input Mapping")
print("=" * 120)
