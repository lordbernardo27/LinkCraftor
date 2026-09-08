from __future__ import annotations

import ast
import hashlib
import importlib
import inspect
from pathlib import Path


ROOT = Path.cwd()

REPORT = (
    ROOT
    / "runtime_completion_intake_phase_5_4_timestamp_result_id_resolution.txt"
)


FILES = (
    ROOT / "backend/server/orchestration/queue.py",
    ROOT / "backend/server/orchestration/job_store.py",
    ROOT / "backend/server/orchestration/models.py",
    ROOT / "backend/server/orchestration/service.py",
    ROOT / "backend/server/runtime/universal_runtime_worker_v1.py",
    ROOT / "backend/server/runtime/universal_jobs/contract.py",
    ROOT / "backend/server/coordination/universal_stages/result_contract.py",
)


SEARCH_TERMS = (
    "started_at",
    "completed_at",
    "updated_at",
    "result_id",
    "uuid",
    "uuid4",
    "fingerprint",
    "runtime_dispatch_result",
    "mark_job_completed",
    "dequeue_job",
    "JOB_STATUS_RUNNING",
    "JOB_STATUS_COMPLETED",
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
        f"{i + 1:05d}: {lines[i]}"
        for i
        in range(
            lo,
            hi,
        )
    )


report = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.4 — RUNTIME COMPLETION INTAKE",
    "TIMESTAMP + RESULT_ID AUTHORITY RESOLUTION",
    "=" * 120,
    "",
]


# =========================================================================
# 1. Exact source inspection
# =========================================================================

for path in FILES:

    report.extend(
        (
            "=" * 120,
            "FILE: "
            + str(
                path.relative_to(ROOT)
            ),
            "=" * 120,
        )
    )

    if not path.exists():

        report.append(
            "EXISTS: False"
        )

        report.append("")
        continue

    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(
        source
    )

    report.append(
        "EXISTS: True"
    )

    report.append(
        "SHA256: "
        + sha256(
            path
        )
    )

    report.append("")
    report.append(
        "TERM COUNTS"
    )

    for term in SEARCH_TERMS:

        report.append(
            f"  {term}: "
            + str(
                source.count(
                    term
                )
            )
        )

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

        lowered = (
            node.name
            + "\n"
            + block
        ).lower()

        if not any(
            term.lower()
            in lowered
            for term
            in SEARCH_TERMS
        ):
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
# 2. Assignment scan
# =========================================================================

report.extend(
    (
        "=" * 120,
        "2. TIMESTAMP ASSIGNMENT SCAN",
        "=" * 120,
        "",
    )
)


for path in FILES:

    if not path.exists():
        continue

    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(
        source
    )

    assignments = []

    for node in ast.walk(
        tree
    ):

        targets = []

        if isinstance(
            node,
            ast.Assign,
        ):

            targets.extend(
                node.targets
            )

        elif isinstance(
            node,
            ast.AnnAssign,
        ):

            targets.append(
                node.target
            )

        elif isinstance(
            node,
            ast.AugAssign,
        ):

            targets.append(
                node.target
            )

        else:
            continue

        for target in targets:

            target_name = None

            if isinstance(
                target,
                ast.Name,
            ):

                target_name = (
                    target.id
                )

            elif isinstance(
                target,
                ast.Attribute,
            ):

                target_name = (
                    target.attr
                )

            if target_name in (
                "started_at",
                "completed_at",
                "updated_at",
                "result_id",
            ):

                assignments.append(
                    (
                        target_name,
                        getattr(
                            node,
                            "lineno",
                            0,
                        ),
                    )
                )

    report.append(
        str(
            path.relative_to(ROOT)
        )
    )

    if assignments:

        for name, line in assignments:

            report.append(
                f"  {name} assignment at line {line}"
            )

    else:

        report.append(
            "  NO TARGET ASSIGNMENTS"
        )

    report.append("")


# =========================================================================
# 3. StageResult timestamp rules
# =========================================================================

stage_result_path = (
    ROOT
    / "backend/server/coordination/universal_stages/"
      "result_contract.py"
)

stage_source = stage_result_path.read_text(
    encoding="utf-8-sig"
)

stage_tree = ast.parse(
    stage_source
)


report.extend(
    (
        "=" * 120,
        "3. STAGERESULT TIMESTAMP / RESULT_ID RULES",
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

    block = source_block(
        stage_source,
        node.lineno,
        node.end_lineno,
        pad=0,
    )

    if any(
        term
        in block
        for term
        in (
            "result_id",
            "started_at",
            "finished_at",
        )
    ):

        report.append(
            node.name
        )

        report.append(
            f"lines: {node.lineno}-{node.end_lineno}"
        )

        report.append(
            source_block(
                stage_source,
                node.lineno,
                node.end_lineno,
            )
        )

        report.append("")


# =========================================================================
# 4. Identity/fingerprint inspection
# =========================================================================

report.extend(
    (
        "=" * 120,
        "4. RESULT_ID IDENTITY OPTIONS",
        "=" * 120,
        "",
        "Inspect whether the StageResult contract already:",
        "",
        "- generates result_id",
        "- derives result_id",
        "- exposes a deterministic identity fingerprint",
        "- expects caller-supplied result_id",
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

    name = node.name.lower()

    if any(
        token in name
        for token
        in (
            "fingerprint",
            "result",
            "identity",
        )
    ):

        report.append(
            f"{node.name}: lines {node.lineno}-{node.end_lineno}"
        )


# =========================================================================
# 5. Canonical worker terminal evidence
# =========================================================================

worker_path = (
    ROOT
    / "backend/server/runtime/"
      "universal_runtime_worker_v1.py"
)

worker_source = worker_path.read_text(
    encoding="utf-8-sig"
)

worker_tree = ast.parse(
    worker_source
)


report.extend(
    (
        "",
        "=" * 120,
        "5. CANONICAL WORKER COMPLETION EVIDENCE",
        "=" * 120,
        "",
    )
)


for node in worker_tree.body:

    if not isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    ):
        continue

    if node.name != (
        "run_one_universal_runtime_job_v1"
    ):
        continue

    report.append(
        source_block(
            worker_source,
            node.lineno,
            node.end_lineno,
        )
    )


# =========================================================================
# 6. Required decisions
# =========================================================================

report.extend(
    (
        "",
        "=" * 120,
        "6. REQUIRED FINAL AUTHORITY DECISIONS",
        "=" * 120,
        "",
        "TIMESTAMP AUTHORITY",
        "",
        "Resolve exactly:",
        "",
        "A. Where RUNNING started_at is written.",
        "B. Where COMPLETED completed_at is written.",
        "C. Whether updated_at may be used as terminal completion time.",
        "D. Whether worker terminal return itself carries timestamps.",
        "E. Whether missing persisted timestamps are an existing Runtime",
        "   integration defect rather than a Phase 5.4 responsibility.",
        "",
        "RESULT_ID AUTHORITY",
        "",
        "Resolve exactly:",
        "",
        "A. Whether result_id already exists before Phase 5.4.",
        "B. Whether StageResult requires caller-supplied result_id.",
        "C. Whether result_id may deterministically derive from:",
        "      workflow_id",
        "      stage_id",
        "      job_id",
        "      completion status",
        "   without random UUID generation.",
        "D. Whether Phase 5.4 should own that deterministic derivation.",
        "",
    )
)


# =========================================================================
# 7. Proposed fail-closed rules
# =========================================================================

report.extend(
    (
        "=" * 120,
        "7. PROPOSED FAIL-CLOSED RULES",
        "=" * 120,
        "",
        "Phase 5.4 must not:",
        "",
        "- fabricate Runtime started_at",
        "- fabricate Runtime completed_at",
        "- silently substitute current wall-clock time",
        "- generate a random result_id without authority",
        "- mutate canonical Runtime completion records",
        "- mark Runtime jobs completed",
        "- update Runtime progress",
        "- execute handlers",
        "- process failures",
        "",
        "If authoritative completion timestamps are genuinely absent,",
        "classify that separately as a Runtime completion persistence gap.",
        "",
        "Production modified: False",
        "Installation performed: False",
        "Next if resolved: 5.4.3 Architecture Resolution",
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
print("PHASE 5.4 — TIMESTAMP + RESULT_ID AUTHORITY SCAN COMPLETE")
print("=" * 120)
print(
    "Production modified:",
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
    "5.4.3 Architecture Resolution",
)
print("=" * 120)
