from __future__ import annotations

import ast
import hashlib
import inspect
import importlib
from pathlib import Path


ROOT = Path.cwd()

REPORT = (
    ROOT
    / "workflow_job_correlation_phase_5_3_authority_resolution.txt"
)


FILES = (
    ROOT / "backend/server/runtime/runtime_state_store.py",
    ROOT / "backend/server/runtime/universal_job_submission.py",
    ROOT / "backend/server/runtime/universal_jobs/creation_engine.py",
    ROOT / "backend/server/runtime/universal_jobs/lineage.py",
    ROOT / "backend/server/runtime/universal_orchestration/run_identity.py",
    ROOT / "backend/server/coordination/universal_stages/result_contract.py",
    ROOT / "backend/server/coordination/runtime_integration/runtime_job_mapping.py",
)


SEARCH_ROOTS = (
    ROOT / "backend/server/coordination",
    ROOT / "backend/server/runtime",
    ROOT / "backend/server/orchestration",
    ROOT / "backend/server/jobs",
)


TERMS = (
    "workflow_id",
    "correlation_id",
    "stage_id",
    "job_id",
    "workspace_id",
    "pipeline_run_id",
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
        for i in range(
            lo,
            hi,
        )
    )


report = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.3 — WORKFLOW/JOB CORRELATION",
    "CORRELATION AUTHORITY RESOLUTION",
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
                path.relative_to(
                    ROOT
                )
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
        + sha256(
            path
        )
    )

    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(
        source
    )


    report.append("")
    report.append(
        "IDENTITY COUNTS"
    )

    for term in TERMS:

        report.append(
            f"  {term}: "
            + str(
                source.count(
                    term
                )
            )
        )


    # ---------------------------------------------------------------------
    # Imports
    # ---------------------------------------------------------------------

    report.append("")
    report.append(
        "IMPORTS"
    )

    imports = []

    for node in ast.walk(
        tree
    ):

        if isinstance(
            node,
            ast.ImportFrom,
        ):

            imports.append(
                node.module
                or ""
            )

        elif isinstance(
            node,
            ast.Import,
        ):

            imports.extend(
                alias.name
                for alias
                in node.names
            )

    for item in sorted(
        set(
            imports
        )
    ):
        report.append(
            "  -> "
            + item
        )


    # ---------------------------------------------------------------------
    # Relevant classes
    # ---------------------------------------------------------------------

    report.append("")
    report.append(
        "RELEVANT CLASSES"
    )

    found = False

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

        if not any(
            term in block
            for term
            in TERMS
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


    # ---------------------------------------------------------------------
    # Relevant functions
    # ---------------------------------------------------------------------

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

        interesting_name = any(
            key in node.name.lower()
            for key
            in (
                "correl",
                "job",
                "state",
                "bind",
                "register",
                "lookup",
                "resolve",
                "create",
                "submit",
            )
        )

        interesting_body = (
            sum(
                1
                for term
                in TERMS
                if term in block
            )
            >= 2
        )

        if not (
            interesting_name
            or interesting_body
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
# 2. Dedicated repository search for an existing correlation authority
# =========================================================================

report.extend(
    (
        "=" * 120,
        "2. EXISTING CORRELATION AUTHORITY SEARCH",
        "=" * 120,
        "",
    )
)


candidate_rows = []

for root in SEARCH_ROOTS:

    if not root.exists():
        continue

    for path in root.rglob(
        "*.py"
    ):

        try:
            source = path.read_text(
                encoding="utf-8-sig"
            )

        except Exception:
            continue

        identity_set = {
            term
            for term
            in TERMS
            if term in source
        }

        semantic_hits = tuple(
            term
            for term
            in (
                "workflow_job_correlation",
                "job_correlation",
                "correlation_registry",
                "correlation_store",
                "bind_workflow",
                "bind_job",
                "resolve_job",
                "lookup_job",
                "job_to_workflow",
                "workflow_to_job",
            )
            if term in source.lower()
        )

        if (
            len(
                identity_set
            )
            >= 4
            or semantic_hits
        ):

            candidate_rows.append(
                (
                    path,
                    tuple(
                        sorted(
                            identity_set
                        )
                    ),
                    semantic_hits,
                )
            )


candidate_rows.sort(
    key=lambda item: str(
        item[0]
    )
)


for (
    path,
    identity_set,
    semantic_hits,
) in candidate_rows:

    report.append(
        str(
            path.relative_to(
                ROOT
            )
        )
    )

    report.append(
        "  identities: "
        + ", ".join(
            identity_set
        )
    )

    report.append(
        "  correlation semantics: "
        + (
            ", ".join(
                semantic_hits
            )
            if semantic_hits
            else "NONE"
        )
    )


if not candidate_rows:
    report.append(
        "NONE"
    )


# =========================================================================
# 3. Runtime State Store dependency check
# =========================================================================

state_store = (
    ROOT
    / "backend/server/runtime/runtime_state_store.py"
)

report.extend(
    (
        "",
        "=" * 120,
        "3. RUNTIME STATE STORE AUTHORITY CHECK",
        "=" * 120,
        "",
    )
)


if state_store.exists():

    source = state_store.read_text(
        encoding="utf-8-sig"
    )

    report.append(
        "runtime_state_store.py exists: True"
    )

    report.append(
        (
            "References runtime_persistence: "
            + str(
                "runtime_persistence"
                in source
            )
        )
    )

    report.append(
        (
            "Contains workflow_id: "
            + str(
                "workflow_id"
                in source
            )
        )
    )

    report.append(
        (
            "Contains correlation_id: "
            + str(
                "correlation_id"
                in source
            )
        )
    )

    report.append(
        (
            "Contains stage_id: "
            + str(
                "stage_id"
                in source
            )
        )
    )

    report.append(
        (
            "Contains job_id: "
            + str(
                "job_id"
                in source
            )
        )
    )

else:

    report.append(
        "runtime_state_store.py exists: False"
    )


# =========================================================================
# 4. Canonical job identity creation point
# =========================================================================

report.extend(
    (
        "",
        "=" * 120,
        "4. CANONICAL JOB ID CREATION POINT",
        "=" * 120,
        "",
        "Expected authority:",
        "  Universal Job Creation Engine",
        "",
        "Expected sequence:",
        "  UniversalJobCreationRequest",
        "    -> normalize request",
        "    -> resolve_universal_job_id",
        "    -> construct UniversalJob",
        "    -> validate UniversalJob",
        "    -> UniversalJobCreationResult",
        "",
        "Phase 5.3 must consume an ACTUAL created canonical job identity,",
        "not infer or generate job_id itself.",
        "",
    )
)


# =========================================================================
# 5. Correlation binding candidate
# =========================================================================

report.extend(
    (
        "=" * 120,
        "5. CORRELATION BINDING CANDIDATE",
        "=" * 120,
        "",
        "Candidate binding fields:",
        "  workflow_id",
        "  correlation_id",
        "  stage_id",
        "  stage_version",
        "  workflow_type",
        "  workspace_id",
        "  job_id",
        "  job_type",
        "  pipeline_id",
        "  runtime_stage",
        "  wave_index",
        "",
        "Source of Coordination fields:",
        "  Phase 5.2 RuntimeJobMapping",
        "",
        "Source of Runtime identity:",
        "  UniversalJobCreationResult.job",
        "",
        "Required cross-validation:",
        "  workspace_id must match",
        "  job_type must match",
        "  pipeline must match pipeline_id",
        "  stage must match runtime_stage",
        "",
        "Phase 5.3 MUST NOT create or rewrite job_id.",
        "",
    )
)


# =========================================================================
# 6. Pipeline run boundary
# =========================================================================

report.extend(
    (
        "=" * 120,
        "6. PIPELINE RUN ID BOUNDARY",
        "=" * 120,
        "",
        "Current evidence:",
        "  pipeline_run_id belongs to Universal Job lineage.",
        "  It is optional.",
        "  It is not Coordination workflow_id.",
        "  It is not Coordination correlation_id.",
        "  It is not Runtime orchestration_run_id.",
        "",
        "Provisional rule:",
        "  Phase 5.3 must not mutate the already-created UniversalJob",
        "  merely to inject workflow_id into pipeline_run_id.",
        "",
        "NOT YET FROZEN.",
        "",
    )
)


# =========================================================================
# 7. Return path requirement
# =========================================================================

report.extend(
    (
        "=" * 120,
        "7. RETURN PATH REQUIREMENT",
        "=" * 120,
        "",
        "5.4 Completion Intake and 5.5 Failure Intake need:",
        "",
        "  job_id",
        "      -> workflow_id",
        "      -> correlation_id",
        "      -> stage_id",
        "      -> workspace_id",
        "      -> job_type",
        "      -> pipeline_id",
        "      -> runtime_stage",
        "",
        "Therefore Phase 5.3 needs a deterministic reverse lookup by job_id.",
        "",
    )
)


# =========================================================================
# 8. Authority resolution questions
# =========================================================================

report.extend(
    (
        "=" * 120,
        "8. AUTHORITY RESOLUTION QUESTIONS",
        "=" * 120,
        "",
        "1. Does a real existing workflow/job correlation store already exist?",
        "2. If not, should Phase 5.3 own a dedicated UCF correlation registry?",
        "3. Should the 5.3 registry be initially in-memory/read-write only,",
        "   with persistence deferred to Phase 8 Workflow State Persistence?",
        "4. Should duplicate registration be:",
        "     same exact binding -> idempotent reuse",
        "     conflicting binding -> fail closed",
        "5. Should job_id be globally unique inside the 5.3 registry?",
        "6. Should stage_id permit more than one job over workflow lifetime?",
        "7. Should reverse lookup by job_id be mandatory for 5.4/5.5?",
        "",
        "Production modified: False",
        "Architecture frozen: False",
        "Installation performed: False",
        "Next: 5.3 Architecture Resolution",
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
print("PHASE 5.3 — CORRELATION AUTHORITY RESOLUTION COMPLETE")
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
    "Candidate correlation files:",
    len(
        candidate_rows
    ),
)
print(
    "REPORT:",
    REPORT.name,
)
print(
    "NEXT:",
    "5.3 Architecture Resolution",
)
print("=" * 120)
