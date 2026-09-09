from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

MAPPER = (
    ROOT
    / "backend/server/coordination/stage_handoff/output_input_mapping.py"
)

REPORT = (
    ROOT
    / "output_input_mapping_phase_6_2_final_certification.txt"
)

FREEZE = (
    ROOT
    / "backend/server/coordination/stage_handoff/"
      "output_input_mapping.phase_6_2.freeze.json"
)

EXPECTED_MAPPER_SHA = (
    "ADEB1AC79CD14EDD55706FB119B30D72EC9D22CC4E1C555FED03BC8112C4A744"
)

EXPECTED_REPORT_SHA = (
    "3758EE7A83CB528B16F1415BA230F170D22B25072C127377E273C7C642CB862D"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


if FREEZE.exists():
    raise SystemExit(
        "FREEZE REFUSED: Phase 6.2 freeze already exists.\n"
        + str(FREEZE)
    )


if not MAPPER.exists():
    raise SystemExit(
        "FREEZE REFUSED: mapper source missing"
    )


if not REPORT.exists():
    raise SystemExit(
        "FREEZE REFUSED: final certification report missing"
    )


mapper_sha = sha256(
    MAPPER
)

report_sha = sha256(
    REPORT
)


if mapper_sha != EXPECTED_MAPPER_SHA:
    raise SystemExit(
        "FREEZE REFUSED: mapper SHA mismatch\n"
        f"Expected: {EXPECTED_MAPPER_SHA}\n"
        f"Actual:   {mapper_sha}"
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
    "Checks: 49",
    "Passed: 49",
    "Failed: 0",
    "FINAL CERTIFIED: True",
    f"Mapper SHA256: {EXPECTED_MAPPER_SHA}",
)


for marker in required_report_markers:
    if marker not in report_text:
        raise SystemExit(
            "FREEZE REFUSED: missing certification marker: "
            + marker
        )


freeze_document = {
    "component":
        "Output -> Input Mapping",

    "framework":
        "Universal Coordination Framework",

    "phase":
        "6.2",

    "freeze_version":
        "output_input_mapping_phase_6_2_freeze_v1",

    "certification_status":
        "certified",

    "certified":
        True,

    "mapper": {
        "path":
            "backend/server/coordination/stage_handoff/"
            "output_input_mapping.py",

        "version":
            "output_input_mapping_v6.2.0",

        "schema_version":
            "output_input_mapping_schema_v1",

        "sha256":
            mapper_sha,
    },

    "verification": {
        "architecture":
            {
                "passed":
                    25,
                "failed":
                    0,
            },

        "smoke":
            {
                "passed":
                    40,
                "failed":
                    0,
            },

        "initial":
            {
                "passed":
                    84,
                "failed":
                    0,
            },

        "final":
            {
                "passed":
                    49,
                "failed":
                    0,
            },

        "total_formal_checks":
            198,
    },

    "final_certification_report": {
        "path":
            "output_input_mapping_phase_6_2_final_certification.txt",

        "sha256":
            report_sha,
    },

    "canonical_mapping_model": {
        "source":
            "ProcessedStageResult.output",

        "target_requirement_authority":
            "UniversalStageReference.required_payload_fields",

        "projection":
            "exact top-level field-name projection",

        "missing_when": [
            "key absent",
            "value is None",
            "value is empty string",
        ],

        "valid_falsey_values": [
            "0",
            "False",
            "[]",
            "{}",
        ],

        "extra_source_fields_projected":
            False,

        "rename_mapping_supported":
            False,

        "nested_path_mapping_supported":
            False,

        "runtime_final_enforcement":
            True,
    },

    "certified_boundaries": [
        "no Runtime submission",
        "no Runtime worker execution",
        "no orchestration job mutation",
        "no coordinator invocation",
        "no workflow lifecycle mutation",
        "no context propagation",
        "no artifact-reference handoff",
        "no rename mapping",
        "no nested-path mapping",
    ],

    "source_disposition_policy": {
        "completed":
            "normal mapping allowed",

        "failed":
            "normal mapping rejected",

        "skipped":
            "normal mapping rejected",

        "cancelled":
            "normal mapping rejected",
    },

    "freeze_created_at":
        datetime.now(
            timezone.utc
        ).isoformat(),

    "next":
        "6.3 Context Propagation",
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
print("PHASE 6.2 — OUTPUT -> INPUT MAPPING SHA256 FREEZE")
print("=" * 120)
print("Architecture Resolution: 25/25")
print("Smoke Verification: 40/40")
print("Initial Verification: 84/84")
print("Final Certification: 49/49")
print("Total Formal Checks: 198 PASS")
print("PHASE 6.2 CERTIFIED: TRUE")
print("PHASE 6.2 FROZEN: TRUE")
print("MAPPER SHA256:", mapper_sha)
print("REPORT SHA256:", report_sha)
print("FREEZE FILE:", FREEZE)
print("FREEZE SHA256:", freeze_sha)
print("Production mapper modified: FALSE")
print("NEXT: 6.3 Context Propagation")
print("=" * 120)
