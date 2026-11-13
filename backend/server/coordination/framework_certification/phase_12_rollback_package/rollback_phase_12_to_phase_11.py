"""
LinkCraftor UCF Phase 12 rollback helper.

Purpose:
    Remove only Phase-12 certification artifacts and return the repository's
    UCF certification layer to the already-frozen Phase-11 boundary.

This script does NOT modify:
    - UCF Phases 1-11,
    - Universal Runtime,
    - pipeline business logic,
    - Connect Domain production authorities,
    - queues, jobs, workers, or workflow data.

Manual execution is required. Merely creating this file performs no rollback.
"""

from pathlib import Path


ROOT = Path.cwd()

P12 = ROOT / "backend/server/coordination/framework_certification"

TARGETS = (
    P12 / "unit_verification.phase_12_1.json",
    P12 / "integration_verification.phase_12_2.json",
    P12 / "runtime_integration_verification.phase_12_3.json",
    P12 / "recovery_verification.phase_12_4.json",
    P12 / "restart_verification.phase_12_5.json",
    P12 / "real_pipeline_verification.phase_12_6.gate.json",
    P12 / "real_pipeline_verification.phase_12_6.json",
    P12 / "real_pipeline_verification.phase_12_6.freeze.json",
    P12 / "performance_verification.phase_12_7.json",
    P12 / "phase_12_1_to_12_5_and_12_7.freeze.json",
    P12 / "phase_12_final_certification.json",
    P12 / "phase_12_framework_certification.freeze.json",
    ROOT / "ucf_phase_12_pre_real_pipeline_verification_report.txt",
    ROOT / "ucf_phase_12_6_real_pipeline_verification_report.txt",
    ROOT / "ucf_phase_12_final_certification_report.txt",
)


def main() -> None:

    print(
        "PHASE 12 ROLLBACK — CERTIFICATION ARTIFACTS ONLY"
    )

    for path in TARGETS:

        if path.exists():

            path.unlink()

            print(
                "REMOVED:",
                path,
            )

    print(
        "ROLLBACK COMPLETE — PHASES 1-11 AND UNIVERSAL RUNTIME UNCHANGED"
    )


if __name__ == "__main__":
    main()
