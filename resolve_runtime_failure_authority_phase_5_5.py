from __future__ import annotations

import ast
import hashlib
from pathlib import Path


ROOT = Path.cwd()

REPORT = (
    ROOT
    / "runtime_failure_intake_phase_5_5_authority_resolution.txt"
)


FILES = {
    "runtime_worker":
        ROOT
        / "backend/server/runtime/"
          "universal_runtime_worker_v1.py",

    "orchestration_store":
        ROOT
        / "backend/server/orchestration/job_store.py",

    "orchestration_service":
        ROOT
        / "backend/server/orchestration/service.py",

    "orchestration_models":
        ROOT
        / "backend/server/orchestration/models.py",

    "stage_result":
        ROOT
        / "backend/server/coordination/universal_stages/"
          "result_contract.py",

    "phase_5_3":
        ROOT
        / "backend/server/coordination/runtime_integration/"
          "workflow_job_correlation.py",

    "phase_5_4":
        ROOT
        / "backend/server/coordination/runtime_integration/"
          "runtime_completion_intake.py",
}


EXPECTED = {
    "runtime_worker":
        "ED6B415C5FEDF3F4CB62451F3E23D182"
        "F9DA937D9CB09FD33262C506B9BEF699",

    "stage_result":
        "B3469B10BB2F8F9372E4336784D09A14"
        "3C78FABE45BF039B61B76F4A2DC33B24",

    "phase_5_3":
        "C0D88ECC69680106B6833DF8CB3113FC"
        "9ABD23C1EE8B7D413BA4AAE3375648FA",

    "phase_5_4":
        "A9F2A8E4242A08A2BDBE6AF0B96DC104"
        "2A53DDD3B2F72BB355259FA0E5D2E6FB",
}


TARGET_FUNCTIONS = {
    "runtime_worker": (
        "_runtime_failure_attempt_number_v1",
        "_runtime_failure_is_contract_error_v1",
        "_runtime_retry_policy_v1",
        "_requeue_same_runtime_job_v1",
        "run_one_universal_runtime_job_v1",
    ),

    "orchestration_store": (
        "update_job_status",
        "append_job_event",
        "list_job_events",
    ),

    "orchestration_service": (
        "mark_job_failed",
        "get_orchestration_job",
    ),
}


SEARCH_PHRASES = (
    "runtime_dispatch_failed",
    "runtime_dispatch_error_type",
    "runtime_dispatch_error",
    "runtime_contract_error",
    "runtime_failure_attempt_count",
    "runtime_maximum_attempts",
    "runtime_retry_scheduled",
    "runtime_retry_exhausted",
    "retry_allowed",
    "retry_scheduled",
    "retry_exhausted",
    "dispatch_error_type",
    "dispatch_error",
    "contract_error",
    "attempt_number",
    "maximum_attempts",
    "terminal_status",
    "canonical_job_id_preserved",
    "failure_code",
    "failure_message",
    "failure_details",
    "UniversalStageResultStatus.FAILED",
)


def sha256(
    path: Path,
) -> str:

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def block(
    source: str,
    start: int,
    end: int,
    pad: int = 3,
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
        for index
        in range(
            lo,
            hi,
        )
    )


report = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.5 — RUNTIME FAILURE INTAKE",
    "FAILURE AUTHORITY RESOLUTION",
    "=" * 120,
    "",
]


# =========================================================================
# 1. Authority integrity
# =========================================================================

report.extend(
    (
        "=" * 120,
        "1. AUTHORITY INTEGRITY",
        "=" * 120,
        "",
    )
)


for name in (
    "runtime_worker",
    "stage_result",
    "phase_5_3",
    "phase_5_4",
):

    path = FILES[
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
# 2. Exact Runtime failure functions
# =========================================================================

report.extend(
    (
        "=" * 120,
        "2. RUNTIME FAILURE FUNCTIONS",
        "=" * 120,
        "",
    )
)


for file_name, function_names in TARGET_FUNCTIONS.items():

    path = FILES[
        file_name
    ]

    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(
        source
    )

    report.append(
        "FILE: "
        + str(
            path.relative_to(
                ROOT
            )
        )
    )

    for wanted in function_names:

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

            if node.name != wanted:
                continue

            found = True

            report.append("")
            report.append(
                f"FUNCTION: {wanted}"
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

            break

        if not found:

            report.append("")
            report.append(
                f"FUNCTION NOT FOUND: {wanted}"
            )

    report.append("")


# =========================================================================
# 3. Runtime failure metadata discovery
# =========================================================================

worker_source = FILES[
    "runtime_worker"
].read_text(
    encoding="utf-8-sig"
)


report.extend(
    (
        "=" * 120,
        "3. RUNTIME FAILURE METADATA KEYS",
        "=" * 120,
        "",
    )
)


for phrase in SEARCH_PHRASES:

    positions = []

    start = 0

    while True:

        index = worker_source.find(
            phrase,
            start,
        )

        if index < 0:
            break

        line_number = (
            worker_source.count(
                "\n",
                0,
                index,
            )
            + 1
        )

        positions.append(
            line_number
        )

        start = (
            index
            + len(
                phrase
            )
        )

    if positions:

        report.append(
            f"{phrase}: {positions}"
        )


# =========================================================================
# 4. StageResult FAILED invariants
# =========================================================================

stage_source = FILES[
    "stage_result"
].read_text(
    encoding="utf-8-sig"
)

stage_tree = ast.parse(
    stage_source
)


report.extend(
    (
        "",
        "=" * 120,
        "4. UNIVERSAL STAGE RESULT FAILED INVARIANTS",
        "=" * 120,
        "",
    )
)


for node in ast.walk(
    stage_tree
):

    if not isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    ):
        continue

    node_block = block(
        stage_source,
        node.lineno,
        node.end_lineno,
        pad=0,
    )

    if (
        "UniversalStageResultStatus.FAILED"
        in node_block
        or (
            "failure_code"
            in node_block
            and "failure_message"
            in node_block
        )
    ):

        report.append(
            f"FUNCTION: {node.name}"
        )

        report.append(
            f"LINES: {node.lineno}-{node.end_lineno}"
        )

        report.append(
            block(
                stage_source,
                node.lineno,
                node.end_lineno,
            )
        )

        report.append("")


# =========================================================================
# 5. JobStatusEvent model
# =========================================================================

models_source = FILES[
    "orchestration_models"
].read_text(
    encoding="utf-8-sig"
)

models_tree = ast.parse(
    models_source
)


report.extend(
    (
        "=" * 120,
        "5. JOB STATUS EVENT AUTHORITY",
        "=" * 120,
        "",
    )
)


for node in models_tree.body:

    if not isinstance(
        node,
        ast.ClassDef,
    ):
        continue

    if node.name != "JobStatusEvent":
        continue

    report.append(
        f"LINES: {node.lineno}-{node.end_lineno}"
    )

    report.append(
        block(
            models_source,
            node.lineno,
            node.end_lineno,
        )
    )


# =========================================================================
# 6. Required authority decisions
# =========================================================================

report.extend(
    (
        "",
        "=" * 120,
        "6. REQUIRED FAILURE AUTHORITY DECISIONS",
        "=" * 120,
        "",
        "Resolve:",
        "",
        "TERMINAL FAILURE",
        "  persisted job.status must equal FAILED",
        "  final selected event must be RUNNING -> FAILED",
        "  retryable RUNNING -> QUEUED must not enter Phase 5.5",
        "",
        "ATTEMPT TIMING",
        "  started_at candidate:",
        "    final QUEUED -> RUNNING event.created_at",
        "",
        "  finished_at candidate:",
        "    final RUNNING -> FAILED event.created_at",
        "",
        "RESULT ID",
        "  candidate:",
        "    final FAILED JobStatusEvent.event_id",
        "",
        "FAILURE CODE",
        "  resolve whether canonical authority is:",
        "    runtime_dispatch_error_type",
        "    or normalized contract/runtime classification",
        "",
        "FAILURE MESSAGE",
        "  resolve whether canonical authority is:",
        "    persisted job.error_message",
        "    or runtime dispatch error text",
        "",
        "FAILURE DETAILS",
        "  determine exact retry/error evidence to preserve",
        "",
        "OUTPUT",
        "  determine whether FAILED output must be empty",
        "  or whether any Runtime failure payload belongs there",
        "",
        "RESULT/ARTIFACT REFERENCES",
        "  determine whether FAILED result must keep them empty",
        "",
    )
)


# =========================================================================
# 7. Fail-closed terminal proof
# =========================================================================

report.extend(
    (
        "=" * 120,
        "7. TERMINAL FAILURE PROOF REQUIREMENTS",
        "=" * 120,
        "",
        "Phase 5.5 should require evidence proving:",
        "",
        "- persisted job status == failed",
        "- selected terminal event is RUNNING -> FAILED",
        "- preceding attempt start is QUEUED -> RUNNING",
        "- canonical job_id preserved",
        "- retry_scheduled is False",
        "- retry_allowed is False for terminal result",
        "- same canonical job_id was retained",
        "",
        "If Runtime metadata does not persist enough evidence for these",
        "requirements, classify the missing evidence before implementation.",
        "",
    )
)


# =========================================================================
# 8. Prohibitions
# =========================================================================

report.extend(
    (
        "=" * 120,
        "8. PHASE 5.5 AUTHORITY BOUNDARY",
        "=" * 120,
        "",
        "Phase 5.5 must remain read-only.",
        "",
        "It must NOT:",
        "  mark job failed",
        "  requeue job",
        "  choose retry policy",
        "  alter attempt count",
        "  dispatch handler",
        "  execute handler",
        "  persist failure",
        "  mutate orchestration",
        "  create job",
        "  submit job",
        "  generate job_id",
        "  rewrite job_id",
        "  process successful completion",
        "  own workflow recovery",
        "",
    )
)


# =========================================================================
# 9. Status
# =========================================================================

report.extend(
    (
        "=" * 120,
        "9. AUTHORITY RESOLUTION STATUS",
        "=" * 120,
        "",
        "Production modified: False",
        "Architecture frozen: False",
        "Installation performed: False",
        "NEXT IF RESOLVED: 5.5.3 Architecture Resolution",
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
print("PHASE 5.5 — FAILURE AUTHORITY RESOLUTION COMPLETE")
print("=" * 120)
print(
    "Production modified:",
    False,
)
print(
    "Architecture frozen:",
    False,
)
print(
    "Installation performed:",
    False,
)
print(
    "REPORT:",
    REPORT.name,
)
print(
    "NEXT IF RESOLVED:",
    "5.5.3 Architecture Resolution",
)
print("=" * 120)
