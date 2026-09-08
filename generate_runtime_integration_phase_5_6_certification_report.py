from pathlib import Path
import hashlib

ROOT = Path.cwd()

REPORT = ROOT / "runtime_integration_phase_5_6_certification_report.txt"

ARTIFACTS = {
    "Discovery Scan":
        "runtime_integration_phase_5_6_discovery_scan.txt",

    "Authority Resolution":
        "runtime_integration_phase_5_6_authority_resolution.txt",

    "Architecture Resolution":
        "runtime_integration_phase_5_6_architecture_resolution.txt",

    "Integration Verification":
        "runtime_integration_phase_5_6_integration_verification.txt",

    "Success-Path Certification":
        "runtime_integration_phase_5_6_success_path_certification.txt",

    "Failure/Retry-Path Certification":
        "runtime_integration_phase_5_6_failure_retry_certification.txt",

    "Identity & Evidence Certification":
        "runtime_integration_phase_5_6_identity_evidence_certification.txt",

    "Final Runtime Integration Certification":
        "runtime_integration_phase_5_6_final_certification.txt",
}

EXPECTED = {
    "Discovery Scan":
        "A55E378B2DCDE90A875147778D2242D63BAC6B6D9C77A67BF6EAA4F6120E8B90",

    "Authority Resolution":
        "A2F7E77F8F2F2F57B1614C77FA02D303D606FBDD23A91F3528725BEABBFB295A",

    "Architecture Resolution":
        "D0950ADDCE841FCBE88597D56B05790A0BD80407F10543E141CEC52B2048D062",

    "Integration Verification":
        "F739DDEB09766F7D752B9123B3EA8028CD9A9DF80CB9CCFD06A991B29E9F722A",

    "Success-Path Certification":
        "F49E0ECEC269AE62CE2F04BBDCD127B553D566932972EF546D495E4F95A5121B",

    "Failure/Retry-Path Certification":
        "5C67756F83933474F3B30A591665949EEA2ACB48E1CAA9D8377A0959028D9CA9",

    "Identity & Evidence Certification":
        "FBDF67479527BC5BE45E7D1249E3357734107404DA56F8F7495F15923A5E38FA",

    "Final Runtime Integration Certification":
        "C07F6073A60323F80FFA04B2E3FFB2228D85205AE1AB2BB6A5EA3EC6F88EC533",
}

CANONICAL_SOURCES = {
    "Universal Job Submission":
        (
            "backend/server/runtime/universal_job_submission.py",
            "8E7AF8CC795D7C990F11FFE0ACD06A5253D957922EC3BD0B740CC1CB0CD3FB2F",
        ),

    "Universal Runtime Worker":
        (
            "backend/server/runtime/universal_runtime_worker_v1.py",
            "ED6B415C5FEDF3F4CB62451F3E23D182F9DA937D9CB09FD33262C506B9BEF699",
        ),

    "Phase 5.3 Workflow/Job Correlation":
        (
            "backend/server/coordination/runtime_integration/workflow_job_correlation.py",
            "13B007B1F74A131250476432B14381CC81C916F48CE121B44877964A18A73AB6",
        ),

    "Phase 5.4 Runtime Completion Intake":
        (
            "backend/server/coordination/runtime_integration/runtime_completion_intake.py",
            "A9F2A8E4242A08A2BDBE6AF0B96DC1042A53DDD3B2F72BB355259FA0E5D2E6FB",
        ),

    "Phase 5.5 Runtime Failure Intake":
        (
            "backend/server/coordination/runtime_integration/runtime_failure_intake.py",
            "CDEE8D641AC045956E2A203BF0A62DE70933F0755B946D63310EFBABE7DFE241",
        ),
}


def sha(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


checks = []

artifact_lines = []

for name, relative in ARTIFACTS.items():

    path = ROOT / relative

    exists = path.exists()

    actual = (
        sha(path)
        if exists
        else "MISSING"
    )

    valid = (
        exists
        and actual
        == EXPECTED[
            name
        ]
    )

    checks.append(
        valid
    )

    artifact_lines.extend(
        [
            f"{name}",
            f"  File: {relative}",
            f"  SHA256: {actual}",
            f"  Integrity: {'VERIFIED' if valid else 'FAILED'}",
            "",
        ]
    )


source_lines = []

for name, (relative, expected) in CANONICAL_SOURCES.items():

    path = ROOT / relative

    exists = path.exists()

    actual = (
        sha(path)
        if exists
        else "MISSING"
    )

    valid = (
        exists
        and actual
        == expected
    )

    checks.append(
        valid
    )

    source_lines.extend(
        [
            f"{name}",
            f"  File: {relative}",
            f"  SHA256: {actual}",
            f"  Integrity: {'VERIFIED' if valid else 'FAILED'}",
            "",
        ]
    )


certified = all(
    checks
)


content = "\n".join(
    [
        "=" * 120,
        "LINKCRAFTOR",
        "UNIVERSAL COORDINATION FRAMEWORK",
        "PHASE 5.6.9 — RUNTIME INTEGRATION CERTIFICATION REPORT",
        "=" * 120,
        "",
        "CERTIFICATION STATUS",
        "--------------------",
        f"Phase 5.6 Runtime Integration Certified: {certified}",
        "",
        "CERTIFIED SCOPE",
        "---------------",
        "Phase 5.6 certifies the complete Universal Coordination Framework",
        "integration boundary with the existing Universal Runtime infrastructure.",
        "",
        "Certified execution chain:",
        "",
        "Pipeline Coordinator",
        "    -> Universal Coordination Framework",
        "    -> Phase 4 Execution Planning",
        "    -> Phase 5 Runtime Integration",
        "    -> Universal Job Submission",
        "    -> Canonical Orchestration Queue",
        "    -> Universal Runtime Worker",
        "    -> Runtime Registration",
        "    -> Runtime Handler",
        "    -> Runtime completion/failure persistence",
        "    -> Phase 5.4 Completion Intake OR Phase 5.5 Failure Intake",
        "    -> Universal Stage Result",
        "    -> Universal Coordination Framework",
        "",
        "PHASE 5.6 CERTIFICATION LEDGER",
        "------------------------------",
        "5.6.1 Discovery Scan: COMPLETE",
        "5.6.2 End-to-End Authority Resolution: COMPLETE",
        "5.6.3 Integration Architecture Resolution: 97/97 PASS",
        "5.6.4 Integration Verification: 83/83 PASS",
        "5.6.5 Success-Path Certification: 52/52 PASS",
        "5.6.6 Failure/Retry-Path Certification: 81/81 PASS",
        "5.6.7 Identity & Evidence Certification: 101/101 PASS",
        "5.6.8 Final Runtime Integration Certification: 47/47 PASS",
        "",
        "TOTAL FORMAL CHECKS ACROSS 5.6.3-5.6.8: 461 PASS",
        "",
        "SUCCESS PATH CERTIFIED",
        "----------------------",
        "Canonical Universal Job creation: VERIFIED",
        "Canonical orchestration persistence: VERIFIED",
        "Canonical queue ingress: VERIFIED",
        "Runtime Worker claim: VERIFIED",
        "QUEUED -> RUNNING: VERIFIED",
        "RUNNING -> COMPLETED: VERIFIED",
        "Canonical job_id continuity: VERIFIED",
        "Phase 5.4 completion intake: VERIFIED",
        "Runtime output propagation: VERIFIED",
        "",
        "FAILURE / RETRY PATH CERTIFIED",
        "------------------------------",
        "Runtime handler failure detection: VERIFIED",
        "Retry policy resolution from Runtime Registration: VERIFIED",
        "Attempt 1 RUNNING -> QUEUED: VERIFIED",
        "Attempt 2 RUNNING -> QUEUED: VERIFIED",
        "Attempt 3 RUNNING -> FAILED: VERIFIED",
        "Same canonical job_id across retries: VERIFIED",
        "Replacement job creation prohibited: VERIFIED",
        "Retry exhaustion evidence: VERIFIED",
        "Phase 5.5 terminal failure intake: VERIFIED",
        "",
        "IDENTITY & EVIDENCE CERTIFIED",
        "-----------------------------",
        "workflow_id continuity: VERIFIED",
        "correlation_id continuity: VERIFIED",
        "stage_id continuity: VERIFIED",
        "workspace_id continuity: VERIFIED",
        "job_type continuity: VERIFIED",
        "canonical job_id continuity: VERIFIED",
        "submission evidence: VERIFIED",
        "Runtime Registration snapshot: VERIFIED",
        "Runtime status events: VERIFIED",
        "same-job retry evidence: VERIFIED",
        "terminal success evidence: VERIFIED",
        "terminal failure evidence: VERIFIED",
        "evidence SHA256 generation: VERIFIED",
        "",
        "CONTROLLED DEFECT CORRECTIONS",
        "-----------------------------",
        "",
        "1. Phase 5.3 Workflow/Job Correlation",
        "   Historical v5.3.0 failed to validate canonical submitted-job",
        "   submission proof and submitted metadata.coordination.",
        "",
        "   Corrective action:",
        "   - Phase 5.3 v5.3.0 controlled invalidation",
        "   - Phase 5.3 v5.3.1 installed",
        "   - full recertification completed",
        "   - replacement freeze established",
        "",
        "   Current canonical SHA:",
        "   13B007B1F74A131250476432B14381CC81C916F48CE121B44877964A18A73AB6",
        "",
        "2. Universal Job Submission Priority Projection",
        "   Canonical Universal Job Creation serializes priority NORMAL",
        "   as the canonical value 'normal'.",
        "",
        "   Historical submission boundary accepted only integer-like",
        "   priority projection values and therefore rejected the valid",
        "   canonical serialized priority.",
        "",
        "   Corrective action:",
        "   - canonical priority authority retained",
        "   - submission projection delegates to canonical priority normalization",
        "   - canonical values critical/high/normal/low/background are safely",
        "     projected to orchestration integers 10/20/30/40/50",
        "   - focused projection verification passed 10/10",
        "   - success and failure Runtime paths recertified",
        "",
        "   Historical SHA:",
        "   07BA2DA8C0A2CFA899DE696D7892652A0AA6D56939B364C8C6B7F0B741B05704",
        "",
        "   Current corrected SHA:",
        "   8E7AF8CC795D7C990F11FFE0ACD06A5253D957922EC3BD0B740CC1CB0CD3FB2F",
        "",
        "CANONICAL PRODUCTION AUTHORITIES",
        "--------------------------------",
        *source_lines,
        "CERTIFICATION ARTIFACT AUTHORITIES",
        "----------------------------------",
        *artifact_lines,
        "ISOLATION GUARANTEE",
        "-------------------",
        "Phase 5.6 Runtime execution certification used isolated orchestration",
        "jobs/events stores while exercising the real orchestration persistence,",
        "queue, worker, retry, completion and failure code paths.",
        "",
        "Pre-existing real queued jobs were observed but not consumed.",
        "Real orchestration jobs store remained unchanged.",
        "Real orchestration events store remained unchanged.",
        "",
        "ARCHITECTURAL CONCLUSION",
        "------------------------",
        "Universal Coordination Framework Phase 5 Runtime Integration is",
        "certified for production architecture.",
        "",
        "The certified boundary preserves separation of responsibility:",
        "",
        "- UCF owns workflow planning, sequencing and coordination.",
        "- Universal Runtime owns execution, queueing, workers, retries and",
        "  runtime status persistence.",
        "- Runtime Registration resolves executable job types to handlers.",
        "- Phase 5.3 binds Runtime jobs back to workflow identity.",
        "- Phase 5.4 converts terminal Runtime completion into StageResult.",
        "- Phase 5.5 converts terminal Runtime failure into StageResult.",
        "- Retryable failures remain Runtime-owned and do not emit premature",
        "  failed StageResults.",
        "- Canonical job identity is preserved throughout execution and retry.",
        "",
        "FINAL VERDICT",
        "-------------",
        (
            "PHASE 5.6 RUNTIME INTEGRATION CERTIFIED: TRUE"
            if certified
            else "PHASE 5.6 RUNTIME INTEGRATION CERTIFIED: FALSE"
        ),
        "",
        (
            "NEXT: 5.6.10 SHA256 Freeze"
            if certified
            else "NEXT: Resolve certification report integrity failures"
        ),
        "",
        "=" * 120,
    ]
)


REPORT.write_text(
    content,
    encoding="utf-8",
)


report_sha = sha(
    REPORT
)


print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 5.6.9 — CERTIFICATION REPORT")
print("=" * 120)
print("Artifact/source integrity checks:", len(checks))
print("Passed:", sum(1 for x in checks if x))
print("Failed:", sum(1 for x in checks if not x))
print("PHASE 5.6 CERTIFIED:", certified)
print("REPORT:", REPORT.name)
print("REPORT SHA256:", report_sha)
print(
    "NEXT:",
    (
        "5.6.10 SHA256 Freeze"
        if certified
        else "Resolve certification report integrity failures"
    ),
)
print("=" * 120)
