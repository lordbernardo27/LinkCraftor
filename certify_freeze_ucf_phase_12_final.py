from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path.cwd()

P12 = (
    ROOT
    / "backend/server/coordination/framework_certification"
)

FINAL_REPORT = (
    ROOT
    / "ucf_phase_12_final_certification_report.txt"
)

ROLLBACK_DIR = (
    P12
    / "phase_12_rollback_package"
)

ROLLBACK_MANIFEST = (
    ROLLBACK_DIR
    / "rollback_manifest.json"
)

ROLLBACK_SCRIPT = (
    ROLLBACK_DIR
    / "rollback_phase_12_to_phase_11.py"
)

MASTER_FREEZE = (
    P12
    / "phase_12_framework_certification.freeze.json"
)

FINAL_EVIDENCE = (
    P12
    / "phase_12_final_certification.json"
)


PHASE11_MASTER = (
    ROOT
    / "backend/server/coordination/coordination_governance/"
    "phase_11_governance.freeze.json"
)

EXPECTED_PHASE11_MASTER_SHA = (
    "80A3023D866DC302E08B2F060A4FA448AA612F6C6FF41B1975044131DBF8AF6C"
)

PRE_BATCH = (
    P12
    / "phase_12_1_to_12_5_and_12_7.freeze.json"
)

EXPECTED_PRE_BATCH_SHA = (
    "9A398B3E0B71A7B471599A08DAD852F9E60E2BD005A6AEF2527C7ABA981F3BD1"
)

P126_EVIDENCE = (
    P12
    / "real_pipeline_verification.phase_12_6.json"
)

EXPECTED_126_EVIDENCE_SHA = (
    "D96453AEF5F4A53269D4790CDC19F11A5B583950C4890819499359F29B4E4032"
)

P126_FREEZE = (
    P12
    / "real_pipeline_verification.phase_12_6.freeze.json"
)

EXPECTED_126_FREEZE_SHA = (
    "E4CC585371FE3CC2FED47CE4E9CB7C199A2A9466E81711B017C1AC671C020CCB"
)

P126_REPORT = (
    ROOT
    / "ucf_phase_12_6_real_pipeline_verification_report.txt"
)

EXPECTED_126_REPORT_SHA = (
    "CF8E81894999F3A03535FC9B78E3632072A5EB7DFCB547200C18EC8B7A67BE2E"
)


PHASE_ARTIFACTS = {
    "12.1":
        P12 / "unit_verification.phase_12_1.json",

    "12.2":
        P12 / "integration_verification.phase_12_2.json",

    "12.3":
        P12 / "runtime_integration_verification.phase_12_3.json",

    "12.4":
        P12 / "recovery_verification.phase_12_4.json",

    "12.5":
        P12 / "restart_verification.phase_12_5.json",

    "12.6":
        P126_EVIDENCE,

    "12.6_freeze":
        P126_FREEZE,

    "12.7":
        P12 / "performance_verification.phase_12_7.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def write_json(path: Path, value) -> None:
    path.write_text(
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )


def section(title: str) -> None:
    print()
    print("=" * 120)
    print(title)
    print("=" * 120)


checks = []


def check(name: str, condition) -> None:
    ok = bool(condition)

    checks.append(
        (
            name,
            ok,
        )
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if not ok:
        raise RuntimeError(
            f"CHECK FAILED: {name}"
        )


section(
    "LINKCRAFTOR — UCF PHASE 12.8–12.10 FINAL FRAMEWORK CERTIFICATION"
)


# =============================================================================
# 0 — AUTHORITY GUARD
# =============================================================================

section(
    "0 — FINAL AUTHORITY GUARD"
)


check(
    "Phase 11 master exact",
    PHASE11_MASTER.exists()
    and sha256(
        PHASE11_MASTER
    )
    == EXPECTED_PHASE11_MASTER_SHA,
)


check(
    "Phase 12 pre-12.6 batch exact",
    PRE_BATCH.exists()
    and sha256(
        PRE_BATCH
    )
    == EXPECTED_PRE_BATCH_SHA,
)


check(
    "Phase 12.6 evidence exact",
    P126_EVIDENCE.exists()
    and sha256(
        P126_EVIDENCE
    )
    == EXPECTED_126_EVIDENCE_SHA,
)


check(
    "Phase 12.6 freeze exact",
    P126_FREEZE.exists()
    and sha256(
        P126_FREEZE
    )
    == EXPECTED_126_FREEZE_SHA,
)


check(
    "Phase 12.6 report exact",
    P126_REPORT.exists()
    and sha256(
        P126_REPORT
    )
    == EXPECTED_126_REPORT_SHA,
)


for phase, path in PHASE_ARTIFACTS.items():

    check(
        f"Phase {phase} artifact exists",
        path.exists(),
    )


check(
    "final Phase 12 master not already installed",
    not MASTER_FREEZE.exists(),
)


check(
    "final Phase 12 evidence not already installed",
    not FINAL_EVIDENCE.exists(),
)


check(
    "final Phase 12 report not already installed",
    not FINAL_REPORT.exists(),
)


check(
    "rollback package not already installed",
    not ROLLBACK_DIR.exists(),
)


# =============================================================================
# 1 — BUILD FINAL PHASE 12 ARTIFACT MAP
# =============================================================================

section(
    "1 — BUILD FINAL PHASE 12 ARTIFACT MAP"
)


artifact_hashes = {
    phase:
        sha256(
            path
        )
    for phase, path
    in PHASE_ARTIFACTS.items()
}


for phase, value in artifact_hashes.items():

    check(
        f"SHA256 available for {phase}",
        len(value)
        == 64,
    )


canonical_lines = [
    f"{phase}:{artifact_hashes[phase]}"
    for phase
    in (
        "12.1",
        "12.2",
        "12.3",
        "12.4",
        "12.5",
        "12.6",
        "12.6_freeze",
        "12.7",
    )
]


PHASE12_COMPONENT_COMPOSITE = hashlib.sha256(
    "\n".join(
        canonical_lines
    ).encode(
        "utf-8"
    )
).hexdigest().upper()


print(
    "PHASE 12 COMPONENT COMPOSITE:",
    PHASE12_COMPONENT_COMPOSITE,
)


# =============================================================================
# 2 — PHASE 12.8 FINAL CERTIFICATION REPORT
# =============================================================================

section(
    "2 — PHASE 12.8 CERTIFICATION REPORT"
)


FINAL_REPORT.write_text(
    "\n".join(
        (
            "LINKCRAFTOR",
            "UNIVERSAL COORDINATION FRAMEWORK",
            "PHASE 12 — FRAMEWORK CERTIFICATION",
            "",
            "12.1 Unit Verification: CERTIFIED + FROZEN",
            "12.2 Integration Verification: CERTIFIED + FROZEN",
            "12.3 Runtime Integration Verification: CERTIFIED + FROZEN",
            "12.4 Recovery Verification: CERTIFIED + FROZEN",
            "12.5 Restart Verification: CERTIFIED + FROZEN",
            "12.6 Real Pipeline Verification: CERTIFIED + FROZEN",
            "12.7 Performance Verification: CERTIFIED + FROZEN",
            "12.8 Certification Report: CERTIFIED",
            "",
            "REAL PIPELINE CERTIFIED:",
            "Pipeline ID: connect_domain",
            "Workflow: connect_domain v1.0.0",
            "Coordinator: connect_domain_pipeline_coordinator v1.0.0",
            "",
            "Canonical Connect Domain stages:",
            "- connect_domain",
            "- site_sources",
            "- url_cleaner",
            "- site_pages",
            "- live_domain_target_pool",
            "- active_target_set",
            "",
            "Phase-2 registration validation:",
            "- genuine workflow registered in isolated certification registry",
            "- genuine coordinator registered in isolated certification registry",
            "- 7/7 registration validation rules passed",
            "- zero violations",
            "",
            "Production safety:",
            "- production jobs created: NO",
            "- production worker executed: NO",
            "- production recovery executed: NO",
            "- protected Connect Domain jobs touched: NO",
            "- live worker activation remains separately gated",
            "",
            f"Phase 11 master SHA256: {EXPECTED_PHASE11_MASTER_SHA}",
            f"Pre-12.6 batch SHA256: {EXPECTED_PRE_BATCH_SHA}",
            f"12.6 evidence SHA256: {EXPECTED_126_EVIDENCE_SHA}",
            f"12.6 freeze SHA256: {EXPECTED_126_FREEZE_SHA}",
            f"Phase 12 component composite SHA256: {PHASE12_COMPONENT_COMPOSITE}",
            "",
            "STATUS: PHASE 12 VERIFICATION COMPLETE",
        )
    )
    + "\n",
    encoding="utf-8",
)


FINAL_REPORT_SHA = sha256(
    FINAL_REPORT
)


check(
    "12.8 final report created",
    FINAL_REPORT.exists(),
)


# =============================================================================
# 3 — FINAL CERTIFICATION EVIDENCE
# =============================================================================

section(
    "3 — FINAL PHASE 12 CERTIFICATION EVIDENCE"
)


write_json(
    FINAL_EVIDENCE,
    {
        "framework":
            "Universal Coordination Framework",

        "phase":
            "12",

        "component":
            "Framework Certification",

        "certified":
            True,

        "components": {
            "12.1":
                "Unit Verification",

            "12.2":
                "Integration Verification",

            "12.3":
                "Runtime Integration Verification",

            "12.4":
                "Recovery Verification",

            "12.5":
                "Restart Verification",

            "12.6":
                "Real Pipeline Verification",

            "12.7":
                "Performance Verification",

            "12.8":
                "Certification Report",
        },

        "artifact_sha256":
            artifact_hashes,

        "component_composite_sha256":
            PHASE12_COMPONENT_COMPOSITE,

        "phase_11_master_sha256":
            EXPECTED_PHASE11_MASTER_SHA,

        "pre_12_6_batch_sha256":
            EXPECTED_PRE_BATCH_SHA,

        "final_report_sha256":
            FINAL_REPORT_SHA,

        "real_pipeline": {
            "pipeline_id":
                "connect_domain",

            "workflow_type":
                "connect_domain",

            "workflow_version":
                "1.0.0",

            "coordinator_id":
                "connect_domain_pipeline_coordinator",

            "coordinator_version":
                "1.0.0",

            "canonical_stage_ids": (
                "connect_domain",
                "site_sources",
                "url_cleaner",
                "site_pages",
                "live_domain_target_pool",
                "active_target_set",
            ),
        },

        "production_runtime_execution":
            False,

        "protected_jobs_touched":
            False,

        "certified_at":
            datetime.now(
                timezone.utc
            ).isoformat(),
    },
)


FINAL_EVIDENCE_SHA = sha256(
    FINAL_EVIDENCE
)


# =============================================================================
# 4 — PHASE 12.9 ROLLBACK PACKAGE
# =============================================================================

section(
    "4 — PHASE 12.9 ROLLBACK PACKAGE"
)


ROLLBACK_DIR.mkdir(
    parents=True,
    exist_ok=False,
)


rollback_snapshot_files = {
    "unit_verification.phase_12_1.json":
        PHASE_ARTIFACTS[
            "12.1"
        ],

    "integration_verification.phase_12_2.json":
        PHASE_ARTIFACTS[
            "12.2"
        ],

    "runtime_integration_verification.phase_12_3.json":
        PHASE_ARTIFACTS[
            "12.3"
        ],

    "recovery_verification.phase_12_4.json":
        PHASE_ARTIFACTS[
            "12.4"
        ],

    "restart_verification.phase_12_5.json":
        PHASE_ARTIFACTS[
            "12.5"
        ],

    "real_pipeline_verification.phase_12_6.json":
        P126_EVIDENCE,

    "real_pipeline_verification.phase_12_6.freeze.json":
        P126_FREEZE,

    "performance_verification.phase_12_7.json":
        PHASE_ARTIFACTS[
            "12.7"
        ],

    "phase_12_1_to_12_5_and_12_7.freeze.json":
        PRE_BATCH,

    "ucf_phase_12_final_certification_report.txt":
        FINAL_REPORT,

    "phase_12_final_certification.json":
        FINAL_EVIDENCE,
}


snapshot_hashes = {}


for filename, source in rollback_snapshot_files.items():

    target = (
        ROLLBACK_DIR
        / filename
    )

    shutil.copy2(
        source,
        target,
    )

    check(
        f"rollback snapshot copied: {filename}",
        target.exists()
        and sha256(
            target
        )
        == sha256(
            source
        ),
    )

    snapshot_hashes[
        filename
    ] = sha256(
        target
    )


ROLLBACK_SCRIPT.write_text(
'''"""
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
''',
    encoding="utf-8",
)


ROLLBACK_SCRIPT_SHA = sha256(
    ROLLBACK_SCRIPT
)


write_json(
    ROLLBACK_MANIFEST,
    {
        "framework":
            "Universal Coordination Framework",

        "phase":
            "12.9",

        "component":
            "Rollback Package",

        "certified":
            True,

        "rollback_target":
            "Phase 11 frozen boundary",

        "snapshot_sha256":
            snapshot_hashes,

        "rollback_script": {
            "path":
                str(
                    ROLLBACK_SCRIPT.relative_to(
                        ROOT
                    )
                ),

            "sha256":
                ROLLBACK_SCRIPT_SHA,

            "automatic_execution":
                False,
        },

        "protected_scope": (
            "UCF Phases 1-11",
            "Universal Runtime",
            "Connect Domain production pipeline",
            "production queues/jobs/workers",
        ),

        "created_at":
            datetime.now(
                timezone.utc
            ).isoformat(),
    },
)


ROLLBACK_MANIFEST_SHA = sha256(
    ROLLBACK_MANIFEST
)


check(
    "12.9 rollback manifest created",
    ROLLBACK_MANIFEST.exists(),
)


check(
    "12.9 rollback helper created",
    ROLLBACK_SCRIPT.exists(),
)


# =============================================================================
# 5 — PHASE 12.10 CANONICAL FREEZE
# =============================================================================

section(
    "5 — PHASE 12.10 CANONICAL FREEZE"
)


canonical_final = "\n".join(
    (
        f"phase11:{EXPECTED_PHASE11_MASTER_SHA}",
        f"pre12_6:{EXPECTED_PRE_BATCH_SHA}",
        f"12.6:{EXPECTED_126_FREEZE_SHA}",
        f"components:{PHASE12_COMPONENT_COMPOSITE}",
        f"report:{FINAL_REPORT_SHA}",
        f"evidence:{FINAL_EVIDENCE_SHA}",
        f"rollback:{ROLLBACK_MANIFEST_SHA}",
    )
)


PHASE12_FULL_COMPOSITE = hashlib.sha256(
    canonical_final.encode(
        "utf-8"
    )
).hexdigest().upper()


write_json(
    MASTER_FREEZE,
    {
        "framework":
            "Universal Coordination Framework",

        "phase":
            "12",

        "component":
            "Framework Certification",

        "certified":
            True,

        "frozen":
            True,

        "phase_status": {
            "12.1":
                "CERTIFIED + FROZEN",

            "12.2":
                "CERTIFIED + FROZEN",

            "12.3":
                "CERTIFIED + FROZEN",

            "12.4":
                "CERTIFIED + FROZEN",

            "12.5":
                "CERTIFIED + FROZEN",

            "12.6":
                "CERTIFIED + FROZEN",

            "12.7":
                "CERTIFIED + FROZEN",

            "12.8":
                "CERTIFIED + FROZEN",

            "12.9":
                "CERTIFIED + FROZEN",

            "12.10":
                "CERTIFIED + FROZEN",
        },

        "phase_11_master_sha256":
            EXPECTED_PHASE11_MASTER_SHA,

        "pre_12_6_batch_sha256":
            EXPECTED_PRE_BATCH_SHA,

        "phase_12_6_freeze_sha256":
            EXPECTED_126_FREEZE_SHA,

        "component_artifact_sha256":
            artifact_hashes,

        "component_composite_sha256":
            PHASE12_COMPONENT_COMPOSITE,

        "final_certification_evidence_sha256":
            FINAL_EVIDENCE_SHA,

        "final_certification_report_sha256":
            FINAL_REPORT_SHA,

        "rollback_manifest_sha256":
            ROLLBACK_MANIFEST_SHA,

        "rollback_script_sha256":
            ROLLBACK_SCRIPT_SHA,

        "phase_12_full_composite_sha256":
            PHASE12_FULL_COMPOSITE,

        "production_jobs_created":
            False,

        "production_worker_executed":
            False,

        "protected_connect_domain_jobs_touched":
            False,

        "live_runtime_activation_certified":
            False,

        "live_runtime_activation_note":
            (
                "Live Universal Runtime worker activation remains "
                "separately gated by production trust/workload identity."
            ),

        "freeze_created_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "next":
            "Phase 13 — Owner Control Tower Integration",
    },
)


MASTER_SHA = sha256(
    MASTER_FREEZE
)


# =============================================================================
# 6 — POST-FREEZE VERIFICATION
# =============================================================================

section(
    "6 — FINAL POST-FREEZE VERIFICATION"
)


check(
    "Phase 11 master remained unchanged",
    sha256(
        PHASE11_MASTER
    )
    == EXPECTED_PHASE11_MASTER_SHA,
)


check(
    "pre-12.6 batch remained unchanged",
    sha256(
        PRE_BATCH
    )
    == EXPECTED_PRE_BATCH_SHA,
)


check(
    "12.6 evidence remained unchanged",
    sha256(
        P126_EVIDENCE
    )
    == EXPECTED_126_EVIDENCE_SHA,
)


check(
    "12.6 freeze remained unchanged",
    sha256(
        P126_FREEZE
    )
    == EXPECTED_126_FREEZE_SHA,
)


check(
    "final evidence exists",
    FINAL_EVIDENCE.exists(),
)


check(
    "final report exists",
    FINAL_REPORT.exists(),
)


check(
    "rollback package exists",
    ROLLBACK_MANIFEST.exists()
    and ROLLBACK_SCRIPT.exists(),
)


check(
    "Phase 12 master freeze exists",
    MASTER_FREEZE.exists(),
)


# =============================================================================
# 7 — FINAL STATUS
# =============================================================================

section(
    "7 — PHASE 12 FINAL STATUS"
)


total = sum(
    1
    for _name, ok
    in checks
    if ok
)


print(
    "TOTAL FORMAL CHECKS:",
    total,
    "PASS",
)

print()

for phase in (
    "12.1",
    "12.2",
    "12.3",
    "12.4",
    "12.5",
    "12.6",
    "12.7",
    "12.8",
    "12.9",
    "12.10",
):
    print(
        f"PHASE {phase}: CERTIFIED + FROZEN"
    )


print()

print(
    "PHASE 12 COMPONENT COMPOSITE SHA256:",
    PHASE12_COMPONENT_COMPOSITE,
)

print(
    "FINAL CERTIFICATION EVIDENCE SHA256:",
    FINAL_EVIDENCE_SHA,
)

print(
    "FINAL CERTIFICATION REPORT SHA256:",
    FINAL_REPORT_SHA,
)

print(
    "ROLLBACK MANIFEST SHA256:",
    ROLLBACK_MANIFEST_SHA,
)

print(
    "ROLLBACK SCRIPT SHA256:",
    ROLLBACK_SCRIPT_SHA,
)

print(
    "PHASE 12 FULL COMPOSITE SHA256:",
    PHASE12_FULL_COMPOSITE,
)

print(
    "PHASE 12 MASTER FREEZE SHA256:",
    MASTER_SHA,
)

print()

print(
    "PRODUCTION JOBS CREATED: NO"
)

print(
    "PRODUCTION WORKER EXECUTED: NO"
)

print(
    "PROTECTED CONNECT DOMAIN JOBS TOUCHED: NO"
)

print(
    "LIVE RUNTIME ACTIVATION CERTIFIED: NO — SEPARATE TRUST GATE"
)

print()

print(
    "PHASE 12 — FRAMEWORK CERTIFICATION: CERTIFIED + FROZEN"
)

print(
    "NEXT: PHASE 13 — OWNER CONTROL TOWER INTEGRATION"
)

print("=" * 120)
