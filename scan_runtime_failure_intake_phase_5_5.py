from __future__ import annotations

import ast
import hashlib
import importlib
from pathlib import Path


ROOT = Path.cwd()

REPORT = (
    ROOT
    / "runtime_failure_intake_phase_5_5_discovery_scan.txt"
)


PATHS = {
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

    "stage_result":
        ROOT
        / "backend/server/coordination/universal_stages/"
          "result_contract.py",

    "runtime_worker":
        ROOT
        / "backend/server/runtime/"
          "universal_runtime_worker_v1.py",

    "orchestration_models":
        ROOT
        / "backend/server/orchestration/models.py",

    "orchestration_store":
        ROOT
        / "backend/server/orchestration/job_store.py",

    "orchestration_service":
        ROOT
        / "backend/server/orchestration/service.py",

    "runtime_registration":
        ROOT
        / "backend/server/runtime/"
          "universal_runtime_registration.py",

    "universal_job_contract":
        ROOT
        / "backend/server/runtime/universal_jobs/"
          "contract.py",
}


EXPECTED = {
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

    "stage_result":
        "B3469B10BB2F8F9372E4336784D09A14"
        "3C78FABE45BF039B61B76F4A2DC33B24",

    "runtime_worker":
        "ED6B415C5FEDF3F4CB62451F3E23D182"
        "F9DA937D9CB09FD33262C506B9BEF699",
}


SEARCH_TERMS = (
    "failed",
    "failure",
    "error",
    "error_message",
    "runtime_dispatch_failed",
    "runtime_dispatch_error_type",
    "runtime_failure_attempt_count",
    "runtime_maximum_attempts",
    "runtime_retry_exhausted",
    "runtime_retry_scheduled",
    "retry_allowed",
    "retry_scheduled",
    "retry_exhausted",
    "contract_error",
    "mark_job_failed",
    "JOB_STATUS_FAILED",
    "job_id",
    "workspace_id",
    "job_type",
    "created_at",
    "started_at",
    "completed_at",
    "result_reference",
    "artifact_references",
)


def sha256(
    path: Path,
) -> str:

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def source_block(
    source: str,
    start: int,
    end: int,
    pad: int = 2,
) -> str:

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
        f"{index + 1:05d}: {lines[index]}"
        for index in range(
            lo,
            hi,
        )
    )


report = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.5 — RUNTIME FAILURE INTAKE",
    "DISCOVERY SCAN",
    "=" * 120,
    "",
]


# =========================================================================
# 1. Frozen authority integrity
# =========================================================================

report.extend(
    (
        "=" * 120,
        "1. FROZEN / CANONICAL AUTHORITY INTEGRITY",
        "=" * 120,
        "",
    )
)


for name in (
    "phase_5_3",
    "phase_5_3_manifest",
    "phase_5_4",
    "phase_5_4_manifest",
    "stage_result",
    "runtime_worker",
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
# 2. Importability
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
    "backend.server.coordination.runtime_integration.workflow_job_correlation",
    "backend.server.coordination.runtime_integration.runtime_completion_intake",
    "backend.server.coordination.universal_stages.result_contract",
    "backend.server.runtime.universal_runtime_worker_v1",
    "backend.server.runtime.universal_runtime_registration",
    "backend.server.orchestration.models",
    "backend.server.orchestration.job_store",
    "backend.server.orchestration.service",
    "backend.server.runtime.universal_jobs.contract",
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
            + type(
                exc
            ).__name__
            + ": "
            + str(
                exc
            )
        )

    else:

        report.append(
            f"[IMPORT OK] {module_name}"
        )

        exports = tuple(
            sorted(
                name
                for name
                in dir(
                    module
                )
                if any(
                    token
                    in name.lower()
                    for token
                    in (
                        "fail",
                        "error",
                        "retry",
                        "job",
                        "event",
                        "result",
                    )
                )
            )
        )

        for export in exports[
            :80
        ]:
            report.append(
                "  "
                + export
            )

    report.append("")


# =========================================================================
# 3. Source-level failure discovery
# =========================================================================

report.extend(
    (
        "=" * 120,
        "3. SOURCE-LEVEL FAILURE DISCOVERY",
        "=" * 120,
        "",
    )
)


for name, path in PATHS.items():

    report.extend(
        (
            "-" * 120,
            "FILE: "
            + str(
                path.relative_to(
                    ROOT
                )
            ),
            "-" * 120,
        )
    )

    if not path.exists():

        report.append(
            "EXISTS: False"
        )

        report.append("")
        continue

    report.append(
        "EXISTS: True"
    )

    report.append(
        "SHA256: "
        + sha256(
            path
        )
    )

    source = path.read_text(
        encoding="utf-8-sig"
    )

    report.append("")
    report.append(
        "TERM COUNTS"
    )

    for term in SEARCH_TERMS:

        count = source.count(
            term
        )

        if count:
            report.append(
                f"  {term}: {count}"
            )

    try:
        tree = ast.parse(
            source
        )

    except SyntaxError as exc:

        report.append("")
        report.append(
            "AST PARSE FAILED: "
            + str(
                exc
            )
        )

        report.append("")
        continue

    report.append("")
    report.append(
        "RELEVANT FUNCTIONS"
    )

    found = False

    for node in tree.body:

        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        block = source_block(
            source,
            node.lineno,
            node.end_lineno,
            pad=0,
        )

        searchable = (
            node.name
            + "\n"
            + block
        ).lower()

        hit_count = sum(
            1
            for term
            in SEARCH_TERMS
            if term.lower()
            in searchable
        )

        if hit_count < 2:
            continue

        found = True

        report.append("")
        report.append(
            node.name
        )

        report.append(
            f"  lines: {node.lineno}-{node.end_lineno}"
        )

        report.append(
            source_block(
                source,
                node.lineno,
                node.end_lineno,
            )
        )

    if not found:
        report.append(
            "  NONE"
        )

    report.append("")


# =========================================================================
# 4. Runtime worker failure path questions
# =========================================================================

report.extend(
    (
        "=" * 120,
        "4. RUNTIME WORKER FAILURE QUESTIONS",
        "=" * 120,
        "",
        "Determine exactly:",
        "",
        "1. How a Runtime handler exception is classified.",
        "",
        "2. How attempt_number is calculated.",
        "",
        "3. How maximum_attempts is obtained.",
        "",
        "4. How retry_allowed is decided.",
        "",
        "5. Which path represents NON-TERMINAL failure:",
        "   RUNNING -> QUEUED retry.",
        "",
        "6. Which path represents TERMINAL failure:",
        "   RUNNING -> FAILED.",
        "",
        "7. Which metadata keys are persisted on the FAILED job.",
        "",
        "8. Whether failed job identity remains the same canonical job_id.",
        "",
        "9. Whether terminal worker result returns:",
        "   dispatch_error_type",
        "   dispatch_error",
        "   contract_error",
        "   attempt_number",
        "   maximum_attempts",
        "   retry_exhausted.",
        "",
    )
)


# =========================================================================
# 5. Orchestration failure evidence questions
# =========================================================================

report.extend(
    (
        "=" * 120,
        "5. ORCHESTRATION FAILURE EVIDENCE QUESTIONS",
        "=" * 120,
        "",
        "Determine exactly:",
        "",
        "1. Does mark_job_failed persist FAILED status?",
        "",
        "2. Does mark_job_failed persist error_message?",
        "",
        "3. Does update_job_status append a FAILED JobStatusEvent?",
        "",
        "4. Does the FAILED event carry created_at?",
        "",
        "5. Can the event trail identify the final attempt's",
        "   QUEUED -> RUNNING transition preceding FAILED?",
        "",
        "6. Are previous retry attempts preserved in the event trail?",
        "",
        "7. Does the persisted job metadata contain enough evidence to",
        "   prove retry was not scheduled for the terminal failure?",
        "",
    )
)


# =========================================================================
# 6. StageResult FAILED contract questions
# =========================================================================

report.extend(
    (
        "=" * 120,
        "6. UNIVERSAL STAGE RESULT FAILED CONTRACT QUESTIONS",
        "=" * 120,
        "",
        "Resolve exact FAILED requirements for:",
        "",
        "status",
        "failure_code",
        "failure_message",
        "failure_details",
        "output",
        "result_reference",
        "artifact_references",
        "started_at",
        "finished_at",
        "result_id",
        "",
        "Determine whether:",
        "",
        "- output may be empty for FAILED",
        "- failure_code is mandatory",
        "- failure_message is mandatory",
        "- failure_details may carry Runtime retry/error evidence",
        "- result_reference/artifact_references must be empty on failure",
        "",
    )
)


# =========================================================================
# 7. Provisional Phase 5.5 architecture
# =========================================================================

report.extend(
    (
        "=" * 120,
        "7. PROVISIONAL PHASE 5.5 ARCHITECTURE",
        "=" * 120,
        "",
        "Expected flow:",
        "",
        "Runtime handler fails",
        "    ↓",
        "Runtime evaluates retry policy",
        "    ↓",
        "IF RETRY ALLOWED:",
        "    RUNNING -> QUEUED",
        "    Phase 5.5 MUST NOT emit FAILED StageResult",
        "",
        "IF TERMINAL FAILURE:",
        "    RUNNING -> FAILED",
        "    ↓",
        "canonical orchestration failed job persisted",
        "    ↓",
        "Phase 5.5 receives/reads failure evidence",
        "    ↓",
        "resolve frozen Phase 5.3 correlation by job_id",
        "    ↓",
        "cross-check job/workspace/type identity",
        "    ↓",
        "select final RUNNING -> FAILED event",
        "    ↓",
        "select preceding QUEUED -> RUNNING event",
        "    ↓",
        "construct UniversalStageResult(status=FAILED)",
        "    ↓",
        "return failure to UCF/coordinator",
        "",
        "NOT YET FROZEN.",
        "",
    )
)


# =========================================================================
# 8. Candidate failure-code sources
# =========================================================================

report.extend(
    (
        "=" * 120,
        "8. FAILURE CODE AUTHORITY TO RESOLVE",
        "=" * 120,
        "",
        "Do NOT invent the final failure_code yet.",
        "",
        "Candidate evidence may include:",
        "",
        "- runtime_dispatch_error_type",
        "- Runtime contract-error classification",
        "- persisted orchestration error_message",
        "- a future normalized Phase 5.5 failure-code namespace",
        "",
        "Authority must be resolved before implementation.",
        "",
    )
)


# =========================================================================
# 9. Phase boundary prohibitions
# =========================================================================

report.extend(
    (
        "=" * 120,
        "9. PHASE 5.5 PROHIBITIONS",
        "=" * 120,
        "",
        "Phase 5.5 must NOT:",
        "",
        "- execute Runtime handlers",
        "- mark jobs failed",
        "- requeue jobs",
        "- decide retry policy",
        "- increment attempt counters",
        "- persist Runtime failure",
        "- mutate Runtime/orchestration state",
        "- create or submit jobs",
        "- generate or rewrite job_id",
        "- process successful completion",
        "- own workflow recovery/compensation",
        "",
        "Runtime owns failure + retry mechanics.",
        "Phase 9 later owns workflow-level recovery policy.",
        "",
    )
)


# =========================================================================
# 10. Status
# =========================================================================

exact_5_3 = (
    sha256(
        PATHS[
            "phase_5_3"
        ]
    )
    == EXPECTED[
        "phase_5_3"
    ]
)

exact_5_4 = (
    sha256(
        PATHS[
            "phase_5_4"
        ]
    )
    == EXPECTED[
        "phase_5_4"
    ]
)

exact_stage_result = (
    sha256(
        PATHS[
            "stage_result"
        ]
    )
    == EXPECTED[
        "stage_result"
    ]
)

exact_worker = (
    sha256(
        PATHS[
            "runtime_worker"
        ]
    )
    == EXPECTED[
        "runtime_worker"
    ]
)


report.extend(
    (
        "=" * 120,
        "10. DISCOVERY STATUS",
        "=" * 120,
        "",
        f"Frozen 5.3 exact: {exact_5_3}",
        f"Frozen 5.4 exact: {exact_5_4}",
        f"StageResult exact: {exact_stage_result}",
        f"Runtime Worker exact: {exact_worker}",
        "Production modified: False",
        "Architecture frozen: False",
        "Installation performed: False",
        "NEXT: 5.5.2 Failure Authority Resolution",
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
print("PHASE 5.5 — RUNTIME FAILURE INTAKE")
print("DISCOVERY SCAN COMPLETE")
print("=" * 120)
print(
    "Frozen 5.3 exact:",
    exact_5_3,
)
print(
    "Frozen 5.4 exact:",
    exact_5_4,
)
print(
    "StageResult exact:",
    exact_stage_result,
)
print(
    "Runtime Worker exact:",
    exact_worker,
)
print(
    "Production modified:",
    False,
)
print(
    "Architecture frozen:",
    False,
)
print(
    "NEXT:",
    "5.5.2 Failure Authority Resolution",
)
print(
    "REPORT:",
    REPORT.name,
)
print("=" * 120)
