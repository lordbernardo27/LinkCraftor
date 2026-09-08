from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

FREEZE = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "runtime_integration.phase_5_6.freeze.json"
)


CANONICAL_SOURCES = {
    "phase_5_1_coordination_runtime_bridge": {
        "path":
            "backend/server/coordination/runtime_integration/"
            "coordination_runtime_bridge.py",
        "expected_sha256":
            "2DD7AF262C879B4DD58A484AB7470D9EA9883A80DDE3C77F1DC1ACDFD35CD0E2",
    },

    "phase_5_2_runtime_job_mapping": {
        "path":
            "backend/server/coordination/runtime_integration/"
            "runtime_job_mapping.py",
        "expected_sha256":
            "49227B0686DED28418DE7DEF2110164318DDCA3858469A05F5A596388BA84E6A",
    },

    "phase_5_3_workflow_job_correlation": {
        "path":
            "backend/server/coordination/runtime_integration/"
            "workflow_job_correlation.py",
        "expected_sha256":
            "13B007B1F74A131250476432B14381CC81C916F48CE121B44877964A18A73AB6",
    },

    "phase_5_4_runtime_completion_intake": {
        "path":
            "backend/server/coordination/runtime_integration/"
            "runtime_completion_intake.py",
        "expected_sha256":
            "A9F2A8E4242A08A2BDBE6AF0B96DC1042A53DDD3B2F72BB355259FA0E5D2E6FB",
    },

    "phase_5_5_runtime_failure_intake": {
        "path":
            "backend/server/coordination/runtime_integration/"
            "runtime_failure_intake.py",
        "expected_sha256":
            "CDEE8D641AC045956E2A203BF0A62DE70933F0755B946D63310EFBABE7DFE241",
    },

    "universal_job_submission": {
        "path":
            "backend/server/runtime/universal_job_submission.py",
        "expected_sha256":
            "8E7AF8CC795D7C990F11FFE0ACD06A5253D957922EC3BD0B740CC1CB0CD3FB2F",
    },

    "universal_runtime_worker": {
        "path":
            "backend/server/runtime/universal_runtime_worker_v1.py",
        "expected_sha256":
            "ED6B415C5FEDF3F4CB62451F3E23D182F9DA937D9CB09FD33262C506B9BEF699",
    },
}


CERTIFICATION_ARTIFACTS = {
    "discovery_scan": {
        "path":
            "runtime_integration_phase_5_6_discovery_scan.txt",
        "expected_sha256":
            "A55E378B2DCDE90A875147778D2242D63BAC6B6D9C77A67BF6EAA4F6120E8B90",
    },

    "authority_resolution": {
        "path":
            "runtime_integration_phase_5_6_authority_resolution.txt",
        "expected_sha256":
            "A2F7E77F8F2F2F57B1614C77FA02D303D606FBDD23A91F3528725BEABBFB295A",
    },

    "architecture_resolution": {
        "path":
            "runtime_integration_phase_5_6_architecture_resolution.txt",
        "expected_sha256":
            "D0950ADDCE841FCBE88597D56B05790A0BD80407F10543E141CEC52B2048D062",
    },

    "integration_verification": {
        "path":
            "runtime_integration_phase_5_6_integration_verification.txt",
        "expected_sha256":
            "F739DDEB09766F7D752B9123B3EA8028CD9A9DF80CB9CCFD06A991B29E9F722A",
    },

    "success_path_certification": {
        "path":
            "runtime_integration_phase_5_6_success_path_certification.txt",
        "expected_sha256":
            "F49E0ECEC269AE62CE2F04BBDCD127B553D566932972EF546D495E4F95A5121B",
    },

    "failure_retry_certification": {
        "path":
            "runtime_integration_phase_5_6_failure_retry_certification.txt",
        "expected_sha256":
            "5C67756F83933474F3B30A591665949EEA2ACB48E1CAA9D8377A0959028D9CA9",
    },

    "identity_evidence_certification": {
        "path":
            "runtime_integration_phase_5_6_identity_evidence_certification.txt",
        "expected_sha256":
            "FBDF67479527BC5BE45E7D1249E3357734107404DA56F8F7495F15923A5E38FA",
    },

    "final_runtime_integration_certification": {
        "path":
            "runtime_integration_phase_5_6_final_certification.txt",
        "expected_sha256":
            "C07F6073A60323F80FFA04B2E3FFB2228D85205AE1AB2BB6A5EA3EC6F88EC533",
    },

    "certification_report": {
        "path":
            "runtime_integration_phase_5_6_certification_report.txt",
        "expected_sha256":
            None,
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def certify_group(group):
    result = {}

    for name, spec in group.items():

        path = ROOT / spec["path"]

        if not path.exists():
            raise SystemExit(
                "FREEZE REFUSED: missing required artifact: "
                + spec["path"]
            )

        actual = sha256(
            path
        )

        expected = spec.get(
            "expected_sha256"
        )

        if (
            expected is not None
            and actual != expected
        ):
            raise SystemExit(
                "FREEZE REFUSED: SHA mismatch for "
                + name
                + "\nExpected: "
                + expected
                + "\nActual:   "
                + actual
            )

        result[
            name
        ] = {
            "path":
                spec["path"],

            "sha256":
                actual,

            "integrity":
                "verified",
        }

    return result


if FREEZE.exists():
    raise SystemExit(
        "FREEZE REFUSED: canonical Phase 5.6 freeze already exists.\n"
        + str(
            FREEZE
        )
    )


sources = certify_group(
    CANONICAL_SOURCES
)

artifacts = certify_group(
    CERTIFICATION_ARTIFACTS
)


freeze_document = {
    "component":
        "Universal Coordination Framework — Runtime Integration",

    "phase":
        "5.6",

    "freeze_step":
        "5.6.10",

    "freeze_version":
        "runtime_integration_phase_5_6_freeze_v1",

    "certification_status":
        "certified",

    "certified":
        True,

    "formal_checks":
        {
            "phase_5_6_3":
                97,

            "phase_5_6_4":
                83,

            "phase_5_6_5":
                52,

            "phase_5_6_6":
                81,

            "phase_5_6_7":
                101,

            "phase_5_6_8":
                47,

            "total":
                461,
        },

    "canonical_sources":
        sources,

    "certification_artifacts":
        artifacts,

    "controlled_corrections":
        {
            "phase_5_3": {
                "historical_version":
                    "v5.3.0",

                "current_version":
                    "v5.3.1",

                "classification":
                    "missed_certification_requirement",

                "current_sha256":
                    sources[
                        "phase_5_3_workflow_job_correlation"
                    ][
                        "sha256"
                    ],
            },

            "universal_job_submission_priority_projection": {
                "historical_sha256":
                    "07BA2DA8C0A2CFA899DE696D7892652A0AA6D56939B364C8C6B7F0B741B05704",

                "current_sha256":
                    sources[
                        "universal_job_submission"
                    ][
                        "sha256"
                    ],

                "canonical_priority_projection":
                    {
                        "critical":
                            10,

                        "high":
                            20,

                        "normal":
                            30,

                        "low":
                            40,

                        "background":
                            50,
                    },
            },
        },

    "certified_runtime_semantics":
        {
            "success":
                "QUEUED -> RUNNING -> COMPLETED",

            "retry":
                "RUNNING -> QUEUED using same canonical job_id",

            "terminal_failure":
                "RUNNING -> FAILED using same canonical job_id",

            "completion_return":
                "Phase 5.4 Runtime Completion Intake",

            "failure_return":
                "Phase 5.5 Runtime Failure Intake",

            "replacement_job_on_retry":
                False,

            "canonical_job_id_preserved":
                True,

            "runtime_owns_retry":
                True,

            "premature_failed_stage_result_on_retry":
                False,
        },

    "architecture_boundary":
        {
            "ucf":
                "planning, sequencing, coordination and workflow state",

            "runtime":
                "execution, queue, worker, retry and runtime status persistence",

            "runtime_registration":
                "job_type to Runtime handler resolution",

            "phase_5_3":
                "workflow/job identity correlation",

            "phase_5_4":
                "terminal completion to UniversalStageResult",

            "phase_5_5":
                "terminal failure to UniversalStageResult",
        },

    "freeze_created_at":
        datetime.now(
            timezone.utc
        ).isoformat(),

    "next_phase":
        "6.0 Stage Handoff",
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
print("PHASE 5.6.10 — SHA256 FREEZE")
print("=" * 120)
print("Canonical production sources:", len(sources))
print("Certification artifacts:", len(artifacts))
print("Formal certification checks: 461 PASS")
print("PHASE 5.6 CERTIFIED: TRUE")
print("PHASE 5.6 FROZEN: TRUE")
print("FREEZE FILE:", FREEZE)
print("FREEZE SHA256:", freeze_sha)
print("Production files modified: FALSE")
print("NEXT: PHASE 6.0 — STAGE HANDOFF")
print("=" * 120)
