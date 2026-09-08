from __future__ import annotations

import ast
import hashlib
import inspect
from pathlib import Path


ROOT = Path.cwd()

REPORT = (
    ROOT
    / "runtime_completion_intake_phase_5_4_authority_resolution.txt"
)


FILES = (
    ROOT / "backend/server/orchestration/models.py",
    ROOT / "backend/server/orchestration/job_store.py",
    ROOT / "backend/server/orchestration/service.py",
    ROOT / "backend/server/runtime/universal_runtime_worker_v1.py",
    ROOT / "backend/server/runtime/universal_runtime_infrastructure.py",
    ROOT / "backend/server/runtime/universal_runtime_registration.py",
    ROOT / "backend/server/jobs/universal_knowledge_orchestrator.py",
    ROOT / "backend/server/runtime/universal_jobs/contract.py",
    ROOT / "backend/server/runtime/universal_jobs/result_reference.py",
    ROOT / "backend/server/coordination/universal_stages/result_contract.py",
)


TERMS = (
    "job_id",
    "status",
    "completed",
    "completed_at",
    "started_at",
    "result",
    "result_reference",
    "artifact_references",
    "metadata",
    "error_message",
)


def sha256(path: Path) -> str:
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
    "COMPLETION AUTHORITY RESOLUTION",
    "=" * 120,
    "",
]


# =========================================================================
# 1. Source-level inspection
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

    report.append(
        "EXISTS: True"
    )

    report.append(
        "SHA256: "
        + sha256(path)
    )

    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(source)

    report.append("")
    report.append(
        "COMPLETION FIELD COUNTS"
    )

    for term in TERMS:

        report.append(
            f"  {term}: "
            + str(
                source.count(term)
            )
        )

    # ---------------------------------------------------------------------
    # Relevant classes
    # ---------------------------------------------------------------------

    report.append("")
    report.append(
        "RELEVANT CLASSES"
    )

    found_class = False

    for node in tree.body:

        if not isinstance(
            node,
            ast.ClassDef,
        ):
            continue

        block = source_block(
            source,
            node.lineno,
            node.end_lineno,
            pad=0,
        )

        hit_count = sum(
            1
            for term in TERMS
            if term in block
        )

        if hit_count < 2:
            continue

        found_class = True

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

    if not found_class:
        report.append(
            "  NONE"
        )

    # ---------------------------------------------------------------------
    # Relevant functions
    # ---------------------------------------------------------------------

    report.append("")
    report.append(
        "RELEVANT FUNCTIONS"
    )

    found_fn = False

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

        lowered_name = node.name.lower()

        name_hit = any(
            fragment in lowered_name
            for fragment in (
                "complete",
                "status",
                "result",
                "job",
                "worker",
                "run",
                "execute",
                "lookup",
                "get",
                "update",
            )
        )

        body_hit_count = sum(
            1
            for term in TERMS
            if term in block
        )

        if not (
            name_hit
            and body_hit_count >= 2
        ):
            continue

        found_fn = True

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

    if not found_fn:
        report.append(
            "  NONE"
        )

    report.append("")


# =========================================================================
# 2. Canonical orchestration questions
# =========================================================================

report.extend(
    (
        "=" * 120,
        "2. CANONICAL ORCHESTRATION COMPLETION QUESTIONS",
        "=" * 120,
        "",
        "Determine:",
        "",
        "1. Does OrchestrationJob store:",
        "   status",
        "   result",
        "   result_reference",
        "   artifact_references",
        "   started_at",
        "   completed_at",
        "?",
        "",
        "2. Does job_store.update_job_status automatically stamp:",
        "   started_at when RUNNING",
        "   completed_at when COMPLETED",
        "?",
        "",
        "3. Can get_job(job_id) deterministically recover",
        "   the persisted terminal completion state?",
        "",
        "4. Does mark_job_completed accept or preserve handler result?",
        "",
        "5. Does orchestration metadata contain the Runtime handler result",
        "   when mark_job_completed is called?",
        "",
    )
)


# =========================================================================
# 3. Universal Runtime worker questions
# =========================================================================

report.extend(
    (
        "=" * 120,
        "3. UNIVERSAL RUNTIME WORKER QUESTIONS",
        "=" * 120,
        "",
        "Determine:",
        "",
        "1. Which execution function does the canonical worker call?",
        "",
        "2. After handler success, does the worker call:",
        "   orchestration.service.mark_job_completed",
        "   universal_knowledge_orchestrator.update_job_status",
        "   both",
        "   or neither?",
        "",
        "3. Is the handler result passed into orchestration completion?",
        "",
        "4. Is the same canonical job_id preserved across:",
        "   queue claim",
        "   Runtime execution",
        "   completion persistence",
        "?",
        "",
        "5. Is completion emitted as a return document/event",
        "   separate from persisted orchestration state?",
        "",
    )
)


# =========================================================================
# 4. Legacy job-status path questions
# =========================================================================

report.extend(
    (
        "=" * 120,
        "4. LEGACY JOB-STATUS PATH QUESTIONS",
        "=" * 120,
        "",
        "Inspect universal_knowledge_orchestrator.update_job_status:",
        "",
        "1. Where does it persist status?",
        "2. Where does it persist result?",
        "3. Does it set completed_at?",
        "4. Is that store canonical for Universal Runtime jobs?",
        "5. Does the canonical orchestration worker still depend on it?",
        "",
        "IMPORTANT:",
        "Do not modify this path during Phase 5.4 authority resolution.",
        "",
    )
)


# =========================================================================
# 5. Universal Job result-reference boundary
# =========================================================================

report.extend(
    (
        "=" * 120,
        "5. UNIVERSAL JOB RESULT REFERENCE QUESTIONS",
        "=" * 120,
        "",
        "Determine whether:",
        "",
        "1. result_reference is merely a validated field/contract,",
        "   or is actually populated by Runtime completion.",
        "",
        "2. artifact_references are populated by Runtime completion.",
        "",
        "3. inline handler output and result_reference may coexist.",
        "",
        "4. Phase 5.4 may legitimately use empty values when Runtime",
        "   provides no result_reference/artifact references.",
        "",
    )
)


# =========================================================================
# 6. StageResult construction boundary
# =========================================================================

report.extend(
    (
        "=" * 120,
        "6. UNIVERSAL STAGE RESULT CONSTRUCTION QUESTIONS",
        "=" * 120,
        "",
        "Resolve sources for:",
        "",
        "workflow_id",
        "  -> frozen Phase 5.3 correlation",
        "",
        "correlation_id",
        "  -> frozen Phase 5.3 correlation",
        "",
        "stage_id",
        "  -> frozen Phase 5.3 correlation",
        "",
        "stage_version",
        "  -> frozen Phase 5.3 correlation",
        "",
        "pipeline_id",
        "  -> frozen Phase 5.3 correlation",
        "",
        "workflow_type",
        "  -> frozen Phase 5.3 correlation",
        "",
        "workspace_id",
        "  -> Runtime completion cross-checked against Phase 5.3",
        "",
        "job_id",
        "  -> Runtime completion + Phase 5.3 lookup key",
        "",
        "job_type",
        "  -> Runtime completion cross-checked against Phase 5.3",
        "",
        "execution_target",
        "  -> likely UNIVERSAL_RUNTIME",
        "",
        "status",
        "  -> COMPLETED only",
        "",
        "output",
        "  -> authoritative Runtime completion result",
        "",
        "result_reference",
        "  -> authoritative Runtime field if present, else contract-empty",
        "",
        "artifact_references",
        "  -> authoritative Runtime field if present, else contract-empty",
        "",
        "started_at",
        "  -> authoritative Runtime/orchestration timestamp",
        "",
        "finished_at",
        "  -> completed_at from authoritative Runtime/orchestration record",
        "",
        "failure fields",
        "  -> empty for successful completion",
        "",
        "result_id",
        "  -> must be resolved separately; Phase 5.4 must not invent",
        "     an ungoverned random identity.",
        "",
    )
)


# =========================================================================
# 7. Provisional authority rule
# =========================================================================

report.extend(
    (
        "=" * 120,
        "7. PROVISIONAL AUTHORITY RULE",
        "=" * 120,
        "",
        "Preferred architecture if source evidence supports it:",
        "",
        "Canonical completion authority:",
        "  orchestration.service / orchestration.job_store",
        "",
        "Canonical lookup:",
        "  get_orchestration_job(job_id) / get_job(job_id)",
        "",
        "Coordination identity authority:",
        "  frozen Phase 5.3 WorkflowJobCorrelation",
        "",
        "Stage result authority:",
        "  frozen UniversalStageResult contract",
        "",
        "Runtime handler output:",
        "  accepted only from authoritative completion evidence",
        "",
        "Legacy universal_knowledge_orchestrator:",
        "  must not become new UCF authority merely because",
        "  Runtime Registration currently calls it.",
        "",
        "NOT YET FROZEN.",
        "",
    )
)


# =========================================================================
# 8. Status
# =========================================================================

report.extend(
    (
        "=" * 120,
        "8. AUTHORITY RESOLUTION STATUS",
        "=" * 120,
        "",
        "Production modified: False",
        "Architecture frozen: False",
        "Installation performed: False",
        "Next: Phase 5.4 Architecture Resolution",
    )
)


REPORT.write_text(
    "\n".join(report)
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 120)
print("PHASE 5.4 — COMPLETION AUTHORITY RESOLUTION COMPLETE")
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
    "REPORT:",
    REPORT.name,
)
print(
    "NEXT:",
    "Phase 5.4 Architecture Resolution",
)
print("=" * 120)
