from __future__ import annotations

import ast
import hashlib
import importlib
from pathlib import Path


ROOT = Path.cwd()

REPORT = (
    ROOT
    / "runtime_integration_phase_5_6_discovery_scan.txt"
)


PATHS = {
    "phase_5_1":
        ROOT
        / "backend/server/coordination/runtime_integration/"
          "coordination_runtime_bridge.py",

    "phase_5_1_manifest":
        ROOT
        / "backend/server/coordination/runtime_integration/"
          "coordination_runtime_bridge.freeze.json",

    "phase_5_2":
        ROOT
        / "backend/server/coordination/runtime_integration/"
          "runtime_job_mapping.py",

    "phase_5_2_manifest":
        ROOT
        / "backend/server/coordination/runtime_integration/"
          "runtime_job_mapping.freeze.json",

    "phase_5_3":
        ROOT
        / "backend/server/coordination/runtime_integration/"
          "workflow_job_correlation.py",

    "phase_5_3_manifest":
        ROOT
        / "backend/server/coordination/runtime_integration/"
          "workflow_job_correlation.freeze.json",

    "phase_5_4":
        ROOT
        / "backend/server/coordination/runtime_integration/"
          "runtime_completion_intake.py",

    "phase_5_4_manifest":
        ROOT
        / "backend/server/coordination/runtime_integration/"
          "runtime_completion_intake.freeze.json",

    "phase_5_5":
        ROOT
        / "backend/server/coordination/runtime_integration/"
          "runtime_failure_intake.py",

    "phase_5_5_manifest":
        ROOT
        / "backend/server/coordination/runtime_integration/"
          "runtime_failure_intake.freeze.json",

    "universal_job_submission":
        ROOT
        / "backend/server/runtime/"
          "universal_job_submission.py",

    "universal_job_contract":
        ROOT
        / "backend/server/runtime/universal_jobs/"
          "contract.py",

    "creation_engine":
        ROOT
        / "backend/server/runtime/universal_jobs/"
          "creation_engine.py",

    "runtime_registration":
        ROOT
        / "backend/server/runtime/"
          "universal_runtime_registration.py",

    "runtime_worker":
        ROOT
        / "backend/server/runtime/"
          "universal_runtime_worker_v1.py",

    "orchestration_service":
        ROOT
        / "backend/server/orchestration/service.py",

    "orchestration_store":
        ROOT
        / "backend/server/orchestration/job_store.py",

    "stage_result":
        ROOT
        / "backend/server/coordination/universal_stages/"
          "result_contract.py",

    "planner":
        ROOT
        / "backend/server/coordination/planning/"
          "execution_planner.py",
}


EXPECTED = {
    "phase_5_1":
        "2DD7AF262C879B4DD58A484AB7470D9E"
        "A9883A80DDE3C77F1DC1ACDFD35CD0E2",

    "phase_5_1_manifest":
        "9F0B93D046E1CF3A76ED3D55CD29E185"
        "7F63872A1CF052C8F5B9FA41AE27122C",

    "phase_5_2":
        "49227B0686DED28418DE7DEF211016431"
        "8DDCA3858469A05F5A596388BA84E6A",

    "phase_5_2_manifest":
        "F3084E6EB9F5D32A963300742091D8EC"
        "327B8D1DB5C86D0BF7A59106D139D8A1",

    "phase_5_3":
        "C0D88ECC69680106B6833DF8CB3113FC"
        "9ABD23C1EE8B7D413BA4AAE3375648FA",

    "phase_5_3_manifest":
        "53F2B149EF904CE5692D85F349038CEA"
        "B901E00B06C6C273CA5B74EB31ACE8E5",

    "phase_5_4":
        "A9F2A8E4242A08A2BDBE6AF0B96DC104"
        "2A53DDD3B2F72BB355259FA0E5D2E6FB",

    "phase_5_4_manifest":
        "CCAC1624848FA623F59DF92C9D70773C"
        "6532E6D48C956C243AD06B35FF8166DD",

    "phase_5_5":
        "CDEE8D641AC045956E2A203BF0A62DE7"
        "0933F0755B946D63310EFBABE7DFE241",

    "phase_5_5_manifest":
        "D926A411FCD494DD201B4A61A8750451"
        "FE146509B891F61739323350D1F0AC9E",

    "universal_job_submission":
        "07BA2DA8C0A2CFA899DE696D7892652A"
        "0AA6D56939B364C8C6B7F0B741B05704",

    "universal_job_contract":
        "E5BE8421D72627AB5DEC93C3CD45E4A3"
        "14E956ACDA751C8A93ECD160CDACEE13",

    "runtime_registration":
        "2D41F0DEEEA6875C3AAF1626613034BF2"
        "787A05E7C542CB87C9D4E71E4D86B46",

    "runtime_worker":
        "ED6B415C5FEDF3F4CB62451F3E23D182"
        "F9DA937D9CB09FD33262C506B9BEF699",

    "stage_result":
        "B3469B10BB2F8F9372E4336784D09A14"
        "3C78FABE45BF039B61B76F4A2DC33B24",
}


SEARCH_TERMS = (
    "submit_universal_job",
    "create_universal_job",
    "create_orchestration_job",
    "priority",
    "submission",
    "persisted",
    "queued",
    "canonical_identity_preserved",
    "canonical_job_id_preserved",
    "coordination",
    "correlate_submitted_job",
    "job_id",
    "pipeline_run_id",
    "correlation_id",
    "runtime_dispatch_completed",
    "runtime_dispatch_failed",
    "runtime_retry_scheduled",
    "runtime_failure_attempt_count",
    "runtime_maximum_attempts",
    "intake_runtime_completion",
    "intake_runtime_failure",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def block(source, start, end, pad=2):
    lines = source.splitlines()

    lo = max(
        0,
        start - 1 - pad,
    )

    hi = min(
        len(lines),
        end + pad,
    )

    return "\n".join(
        f"{i + 1:05d}: {lines[i]}"
        for i in range(
            lo,
            hi,
        )
    )


report = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.6 — RUNTIME INTEGRATION CERTIFICATION",
    "DISCOVERY SCAN",
    "=" * 120,
    "",
]


# =========================================================================
# 1. Frozen Phase 5 authority integrity
# =========================================================================

report.extend(
    (
        "=" * 120,
        "1. PHASE 5 FROZEN AUTHORITY INTEGRITY",
        "=" * 120,
        "",
    )
)


for name in (
    "phase_5_1",
    "phase_5_1_manifest",
    "phase_5_2",
    "phase_5_2_manifest",
    "phase_5_3",
    "phase_5_3_manifest",
    "phase_5_4",
    "phase_5_4_manifest",
    "phase_5_5",
    "phase_5_5_manifest",
    "universal_job_submission",
    "universal_job_contract",
    "runtime_registration",
    "runtime_worker",
    "stage_result",
):

    path = PATHS[
        name
    ]

    actual = sha256(
        path
    )

    expected = EXPECTED[
        name
    ]

    report.append(
        f"{name}:"
    )

    report.append(
        f"  expected: {expected}"
    )

    report.append(
        f"  actual:   {actual}"
    )

    report.append(
        f"  exact:    {actual == expected}"
    )

    report.append("")


# =========================================================================
# 2. Import discovery
# =========================================================================

report.extend(
    (
        "=" * 120,
        "2. IMPORT DISCOVERY",
        "=" * 120,
        "",
    )
)


modules = (
    "backend.server.coordination.runtime_integration.coordination_runtime_bridge",
    "backend.server.coordination.runtime_integration.runtime_job_mapping",
    "backend.server.coordination.runtime_integration.workflow_job_correlation",
    "backend.server.coordination.runtime_integration.runtime_completion_intake",
    "backend.server.coordination.runtime_integration.runtime_failure_intake",
    "backend.server.runtime.universal_job_submission",
    "backend.server.runtime.universal_runtime_registration",
    "backend.server.runtime.universal_runtime_worker_v1",
)


for module_name in modules:

    try:
        module = importlib.import_module(
            module_name
        )

    except Exception as exc:

        report.append(
            f"[IMPORT FAIL] {module_name}"
        )

        report.append(
            "  "
            + type(exc).__name__
            + ": "
            + str(exc)
        )

    else:

        report.append(
            f"[IMPORT OK] {module_name}"
        )

    report.append("")


# =========================================================================
# 3. Relevant source functions and terms
# =========================================================================

report.extend(
    (
        "=" * 120,
        "3. END-TO-END SOURCE DISCOVERY",
        "=" * 120,
        "",
    )
)


for name, path in PATHS.items():

    if not path.exists():
        continue

    source = path.read_text(
        encoding="utf-8-sig"
    )

    report.extend(
        (
            "-" * 120,
            "FILE: "
            + str(
                path.relative_to(ROOT)
            ),
            "SHA256: "
            + sha256(path),
            "-" * 120,
        )
    )

    for term in SEARCH_TERMS:

        count = source.count(
            term
        )

        if count:
            report.append(
                f"{term}: {count}"
            )

    try:
        tree = ast.parse(
            source
        )

    except SyntaxError as exc:

        report.append(
            "AST ERROR: "
            + str(exc)
        )

        report.append("")
        continue

    for node in tree.body:

        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        text = block(
            source,
            node.lineno,
            node.end_lineno,
            pad=0,
        )

        lowered = (
            node.name
            + "\n"
            + text
        ).lower()

        hits = sum(
            1
            for term
            in SEARCH_TERMS
            if term.lower()
            in lowered
        )

        if hits < 2:
            continue

        report.append("")
        report.append(
            "FUNCTION: "
            + node.name
        )

        report.append(
            f"LINES: {node.lineno}-{node.end_lineno}"
        )

        report.append(
            block(
                source,
                node.lineno,
                node.end_lineno,
            )
        )

    report.append("")


# =========================================================================
# 4. Known Phase 5.6 certification questions
# =========================================================================

report.extend(
    (
        "=" * 120,
        "4. PHASE 5.6 CERTIFICATION QUESTIONS",
        "=" * 120,
        "",
        "A. 5.1 -> 5.2",
        "   - Does the bridge preserve planner stage order?",
        "   - Does 5.2 preserve workflow/correlation/stage identity?",
        "",
        "B. 5.2 -> Universal Job Submission",
        "   - Is creation_request.priority propagated exactly?",
        "   - Does any wrapper default override mapped priority?",
        "",
        "C. Universal Job Submission -> 5.3",
        "   - Does 5.3 require submission.persisted is True?",
        "   - Does 5.3 require submission.queued is True?",
        "   - Does 5.3 require submission.canonical_identity_preserved is True?",
        "   - Does 5.3 validate submitted metadata.coordination?",
        "",
        "D. Runtime identity",
        "   - Is one canonical job_id preserved across creation,",
        "     orchestration persistence, queue, worker, completion/failure?",
        "",
        "E. Runtime success return",
        "   - COMPLETED persisted before 5.4 intake?",
        "   - 5.4 uses frozen 5.3 correlation?",
        "   - 5.4 emits exactly one canonical StageResult(COMPLETED)?",
        "",
        "F. Runtime retry/failure return",
        "   - retry RUNNING -> QUEUED remains Runtime-owned?",
        "   - terminal RUNNING -> FAILED reaches 5.5 only?",
        "   - 5.5 emits exactly one canonical StageResult(FAILED)?",
        "",
        "G. Ownership",
        "   - no coordination component executes business logic?",
        "   - no intake component mutates Runtime?",
        "",
    )
)


# =========================================================================
# 5. Known latent issues requiring proof
# =========================================================================

report.extend(
    (
        "=" * 120,
        "5. KNOWN LATENT ISSUES TO PROVE OR DISPROVE",
        "=" * 120,
        "",
        "ISSUE 1 — Phase 5.3 submission evidence",
        "",
        "Earlier certification established correlation after intended",
        "successful canonical submission, but current Phase 5.3 may not",
        "explicitly require all canonical submission evidence:",
        "",
        "  submission.persisted == True",
        "  submission.queued == True",
        "  submission.canonical_identity_preserved == True",
        "  metadata.coordination identity",
        "",
        "Phase 5.6 must prove whether this is a real missed certification",
        "requirement before any frozen-file invalidation or patch.",
        "",
        "ISSUE 2 — Submission priority propagation",
        "",
        "Earlier discovery observed a possible mismatch between:",
        "",
        "  UniversalJobCreationRequest priority default",
        "and",
        "  submit_universal_job wrapper priority default",
        "",
        "Phase 5.6 must prove whether mapped request.priority is actually",
        "forwarded end-to-end or silently replaced by a wrapper default.",
        "",
        "No production file is modified by this discovery scan.",
        "",
    )
)


# =========================================================================
# 6. Phase 5.6 boundary
# =========================================================================

report.extend(
    (
        "=" * 120,
        "6. PHASE 5.6 BOUNDARY",
        "=" * 120,
        "",
        "Phase 5.6 is certification of Runtime Integration.",
        "",
        "It must NOT add new execution authority.",
        "",
        "Any defect discovered must be classified as:",
        "",
        "  - verifier defect",
        "  - integration defect in unfrozen component",
        "  - missed certification requirement in frozen component",
        "  - deferred non-Phase-5 concern",
        "",
        "Frozen production must not be modified without concrete proof.",
        "",
    )
)


# =========================================================================
# Final
# =========================================================================

all_exact = all(
    sha256(
        PATHS[name]
    )
    == EXPECTED[name]
    for name
    in EXPECTED
)


report.extend(
    (
        "=" * 120,
        "7. DISCOVERY STATUS",
        "=" * 120,
        "",
        f"All tracked canonical hashes exact: {all_exact}",
        "Production modified: False",
        "Frozen files modified: False",
        "Certification performed: False",
        "NEXT: 5.6.2 End-to-End Authority Resolution",
    )
)


REPORT.write_text(
    "\n".join(
        report
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 120)
print("PHASE 5.6 — RUNTIME INTEGRATION CERTIFICATION")
print("DISCOVERY SCAN COMPLETE")
print("=" * 120)
print(
    "All tracked canonical hashes exact:",
    all_exact,
)
print(
    "Production modified:",
    False,
)
print(
    "Frozen files modified:",
    False,
)
print(
    "NEXT:",
    "5.6.2 End-to-End Authority Resolution",
)
print(
    "REPORT:",
    REPORT.name,
)
print("=" * 120)
