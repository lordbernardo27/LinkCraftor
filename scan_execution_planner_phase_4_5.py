from __future__ import annotations

import ast
import hashlib
from pathlib import Path


ROOT = Path.cwd()

PHASE_41 = ROOT / (
    "backend/server/coordination/"
    "dependency_planning/dependency_graph.py"
)

PHASE_42 = ROOT / (
    "backend/server/coordination/"
    "dependency_planning/dependency_validation.py"
)

PHASE_43 = ROOT / (
    "backend/server/coordination/"
    "dependency_planning/cycle_detection.py"
)

PHASE_44 = ROOT / (
    "backend/server/coordination/"
    "dependency_planning/runnable_stage_resolver.py"
)

DEPENDENCY_DIR = ROOT / (
    "backend/server/coordination/"
    "dependency_planning"
)

REPORT = ROOT / (
    "execution_planner_phase_4_5_discovery_scan.txt"
)


EXPECTED_41_SHA = (
    "4F6BA62D011C31D9D851FBBABC37C12B"
    "7DDAA1FD9A91E34788EBCE25741A1F70"
)

EXPECTED_42_SHA = (
    "1D053C0036EA9F7A8AEDFAFC36F6EB82"
    "A681EDC7EF206409E9FFB8C7F212852D"
)

EXPECTED_43_SHA = (
    "BC4A40999FEE0540D2254D9F99E12C1D"
    "97D25662953026ADDDABC429B42212B1"
)

EXPECTED_44_SHA = (
    "2779D432A2F3337F3557C61664499669"
    "CC852773AB74447297E98D6188289483"
)


MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_MATCHES_PER_TERM = 60


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def read_source(path: Path) -> str:
    return path.read_text(
        encoding="utf-8-sig"
    )


lines: list[str] = []


def section(title: str) -> None:
    lines.append("")
    lines.append("=" * 104)
    lines.append(title)
    lines.append("=" * 104)


lines.extend(
    [
        "LINKCRAFTOR",
        "UNIVERSAL COORDINATION FRAMEWORK",
        "PHASE 4.5 — EXECUTION PLANNER DISCOVERY SCAN",
        "=" * 104,
    ]
)


# =============================================================================
# 1. Frozen upstream integrity
# =============================================================================

section(
    "1. FROZEN UPSTREAM INTEGRITY"
)

actual_41 = (
    sha256(PHASE_41)
    if PHASE_41.exists()
    else "MISSING"
)

actual_42 = (
    sha256(PHASE_42)
    if PHASE_42.exists()
    else "MISSING"
)

actual_43 = (
    sha256(PHASE_43)
    if PHASE_43.exists()
    else "MISSING"
)

actual_44 = (
    sha256(PHASE_44)
    if PHASE_44.exists()
    else "MISSING"
)

for phase, actual, expected in (
    ("4.1", actual_41, EXPECTED_41_SHA),
    ("4.2", actual_42, EXPECTED_42_SHA),
    ("4.3", actual_43, EXPECTED_43_SHA),
    ("4.4", actual_44, EXPECTED_44_SHA),
):
    lines.append(
        f"Phase {phase} SHA256: {actual}"
    )
    lines.append(
        f"Phase {phase} SHA matches frozen value: "
        f"{actual == expected}"
    )


# =============================================================================
# 2. Current dependency-planning package
# =============================================================================

section(
    "2. CURRENT DEPENDENCY-PLANNING PACKAGE"
)

if DEPENDENCY_DIR.exists():

    for path in sorted(
        item
        for item
        in DEPENDENCY_DIR.rglob("*")
        if item.is_file()
        and "__pycache__"
        not in item.parts
    ):
        lines.append(
            str(
                path.relative_to(ROOT)
            )
        )

else:
    lines.append(
        "DEPENDENCY-PLANNING DIRECTORY MISSING"
    )


# =============================================================================
# 3. Safe repository search
# =============================================================================

section(
    "3. EXISTING EXECUTION-PLANNING AUTHORITY"
)

search_terms = (
    "execution plan",
    "execution_plan",
    "execution planner",
    "execution_planner",
    "plan execution",
    "plan_execution",
    "topological order",
    "topological_order",
    "topological sort",
    "topological_sort",
    "execution batch",
    "execution_batch",
    "execution wave",
    "execution_wave",
    "ready batch",
    "ready_batch",
    "stage order",
    "stage_order",
    "runnable_stage_ids",
    "dispatch plan",
    "dispatch_plan",
    "schedule stage",
    "schedule_stage",
)

extensions = {
    ".py",
    ".md",
    ".txt",
}

skip_parts = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
}

matches = {
    term: []
    for term
    in search_terms
}

files_examined = 0
files_skipped_large = 0
files_read_error = 0


def search_file_linewise(
    path: Path,
) -> None:
    global files_examined
    global files_skipped_large
    global files_read_error

    try:
        size = path.stat().st_size
    except OSError:
        files_read_error += 1
        return

    if size > MAX_FILE_BYTES:
        files_skipped_large += 1
        return

    relative = str(
        path.relative_to(ROOT)
    )

    found_in_file: set[str] = set()

    try:
        with path.open(
            "r",
            encoding="utf-8",
            errors="ignore",
        ) as handle:

            for raw_line in handle:
                lowered = raw_line.lower()

                for term in search_terms:

                    if term in found_in_file:
                        continue

                    if (
                        len(matches[term])
                        >= MAX_MATCHES_PER_TERM
                    ):
                        continue

                    if term.lower() in lowered:
                        matches[term].append(
                            relative
                        )
                        found_in_file.add(
                            term
                        )

    except Exception:
        files_read_error += 1
        return

    files_examined += 1


for path in ROOT.rglob("*"):

    if not path.is_file():
        continue

    if path.suffix.lower() not in extensions:
        continue

    if any(
        part in skip_parts
        for part
        in path.parts
    ):
        continue

    search_file_linewise(
        path
    )


lines.append(
    f"Files examined safely: {files_examined}"
)

lines.append(
    (
        "Oversized files skipped "
        f"(> {MAX_FILE_BYTES} bytes): "
        f"{files_skipped_large}"
    )
)

lines.append(
    f"Files skipped due to read error: {files_read_error}"
)


for term in search_terms:

    lines.append("")
    lines.append(
        f"[{term}]"
    )

    found = sorted(
        set(
            matches[term]
        )
    )

    if found:
        for item in found:
            lines.append(
                f"  {item}"
            )
    else:
        lines.append(
            "  NONE"
        )


# =============================================================================
# 4. Phase 4.1 topology surface
# =============================================================================

section(
    "4. FROZEN PHASE 4.1 TOPOLOGY SURFACE"
)

source_41 = read_source(
    PHASE_41
)

for marker in (
    "DependencyGraph",
    "stage_prerequisites",
    "stage_dependents",
    "dependency_roots",
    "dependency_leaves",
    "topological",
):
    lines.append(
        f"{marker}: "
        + str(
            marker in source_41
        )
    )


# =============================================================================
# 5. Phase 4.3 cycle/topology boundary
# =============================================================================

section(
    "5. FROZEN PHASE 4.3 PLANNING BOUNDARY"
)

source_43 = read_source(
    PHASE_43
)

for marker in (
    "require_acyclic_dependency_graph",
    "execution ordering/planning (Phase 4.5)",
    "topological execution ordering",
    "runnable-stage resolution",
):
    lines.append(
        f"{marker}: "
        + str(
            marker in source_43
        )
    )


# =============================================================================
# 6. Phase 4.4 planner input surface
# =============================================================================

section(
    "6. FROZEN PHASE 4.4 PLANNER INPUT SURFACE"
)

source_44 = read_source(
    PHASE_44
)

tree_44 = ast.parse(
    source_44
)

public_44 = []

for node in tree_44.body:

    if isinstance(
        node,
        (
            ast.ClassDef,
            ast.FunctionDef,
        ),
    ):
        if not node.name.startswith("_"):
            public_44.append(
                node.name
            )

for name in public_44:
    lines.append(
        name
    )

lines.append("")

for marker in (
    "runnable_stage_ids",
    "blocked_stage_ids",
    "untracked_stage_ids",
    "execution_order",
    "not produced",
):
    lines.append(
        f"{marker}: "
        + str(
            marker in source_44
        )
    )


# =============================================================================
# 7. Candidate planner semantics
# =============================================================================

section(
    "7. PHASE 4.5 CANDIDATE PLANNER SEMANTICS"
)

candidate_semantics = (
    (
        "input",
        (
            "validated acyclic DependencyGraph plus "
            "Phase 4.4 RunnableStageResolution"
        ),
    ),
    (
        "workflow_identity",
        (
            "4.4 resolution workflow_id must match "
            "DependencyGraph workflow_id"
        ),
    ),
    (
        "eligible_now",
        (
            "only 4.4 runnable_stage_ids may appear "
            "in immediate execution plan"
        ),
    ),
    (
        "blocked_stage",
        "must not appear in immediate execution plan",
    ),
    (
        "untracked_stage",
        "must not appear in immediate execution plan",
    ),
    (
        "ordering",
        "deterministic",
    ),
    (
        "parallel_runnable_stages",
        (
            "must remain simultaneously eligible; "
            "planner must not fabricate dependencies"
        ),
    ),
    (
        "empty_runnable_set",
        "valid empty execution plan",
    ),
    (
        "dispatch",
        "not performed",
    ),
    (
        "runtime_job_creation",
        "not performed",
    ),
)


for name, meaning in candidate_semantics:
    lines.append(
        f"{name}: {meaning}"
    )


# =============================================================================
# 8. Critical question: what does execution plan mean?
# =============================================================================

section(
    "8. EXECUTION-PLAN SHAPE DECISION"
)

lines.extend(
    [
        (
            "Question: Should Phase 4.5 plan only the stages "
            "that are runnable NOW?"
        ),
        "",
        (
            "Candidate A: Immediate plan"
        ),
        (
            "  plan only Phase 4.4 runnable_stage_ids"
        ),
        (
            "  preserve parallel eligibility"
        ),
        (
            "  no future-stage prediction"
        ),
        "",
        (
            "Candidate B: Full future topological plan"
        ),
        (
            "  compute ordering for all remaining graph nodes"
        ),
        (
            "  predicts stages that are not currently runnable"
        ),
        "",
        (
            "Discovery should determine whether Phase 4.5 "
            "is an immediate execution planner or full "
            "workflow topological planner."
        ),
    ]
)


# =============================================================================
# 9. Critical question: sequence vs batches/waves
# =============================================================================

section(
    "9. SEQUENCE VS PARALLEL-BATCH DECISION"
)

lines.extend(
    [
        (
            "If multiple stages are simultaneously runnable, "
            "should Phase 4.5:"
        ),
        "",
        (
            "A. return one lexical sequence?"
        ),
        (
            "B. return one execution batch/wave containing "
            "all simultaneously runnable stages?"
        ),
        "",
        (
            "Important:"
        ),
        (
            "A lexical tuple may be deterministic evidence "
            "without implying serial execution."
        ),
        "",
        (
            "Phase 4.5 must not convert independent runnable "
            "stages into artificial dependencies."
        ),
    ]
)


# =============================================================================
# 10. Critical question: priority/resources
# =============================================================================

section(
    "10. PRIORITY / RESOURCE POLICY DECISION"
)

lines.extend(
    [
        (
            "Question: Should 4.5 consider priority, worker capacity, "
            "queue state, concurrency limits, cost, retries, "
            "or Runtime availability?"
        ),
        "",
        "Preliminary answer: NO.",
        "",
        (
            "Those are Runtime/scheduling concerns unless a later "
            "UCF contract explicitly introduces planning policy."
        ),
        "",
        (
            "Phase 4.5 should remain coordination-topology planning, "
            "not infrastructure scheduling."
        ),
    ]
)


# =============================================================================
# 11. Critical question: full topological order ownership
# =============================================================================

section(
    "11. TOPOLOGICAL ORDER OWNERSHIP"
)

lines.extend(
    [
        (
            "Phase 4.3 explicitly refused authoritative "
            "execution ordering."
        ),
        "",
        (
            "Phase 4.4 explicitly returns runnable stages "
            "without execution ordering."
        ),
        "",
        (
            "Therefore 4.5 is the first Phase 4 component "
            "allowed to own authoritative execution-plan order."
        ),
        "",
        (
            "Discovery must determine scope:"
        ),
        (
            "  immediate runnable-plan order only"
        ),
        (
            "  OR full remaining-workflow topological order"
        ),
    ]
)


# =============================================================================
# 12. Candidate implementation identity
# =============================================================================

section(
    "12. CANDIDATE PHASE 4.5 IMPLEMENTATION IDENTITY"
)

lines.extend(
    [
        (
            "Candidate file: "
            "backend/server/coordination/"
            "dependency_planning/execution_planner.py"
        ),
        (
            "Candidate version: "
            "execution_planner_v4.5.0"
        ),
        (
            "Candidate schema: "
            "execution_planner_schema_v1"
        ),
        (
            "Primary topology input: "
            "frozen Phase 4.1 DependencyGraph"
        ),
        (
            "Required cycle precondition: "
            "frozen Phase 4.3"
        ),
        (
            "Primary runnability input: "
            "frozen Phase 4.4 RunnableStageResolution"
        ),
        (
            "Candidate result: "
            "immutable ExecutionPlan"
        ),
    ]
)


# =============================================================================
# 13. Explicit non-authority
# =============================================================================

section(
    "13. PHASE 4.5 EXPLICIT NON-AUTHORITY"
)

for item in (
    "dependency graph construction -> 4.1",
    "dependency semantic validation -> 4.2",
    "cycle detection -> 4.3",
    "runnable-stage eligibility -> 4.4",
    "planning certification -> 4.6",
    "Runtime dispatch/execution -> Phase 5",
    "Runtime worker selection -> Phase 5",
    "Runtime queue scheduling -> Runtime",
    "stage handoff -> Phase 6",
    "fan-out/fan-in policy -> Phase 7",
    "conditional execution -> Phase 7",
    "skip semantics -> Phase 7.7",
    "persistence/checkpointing -> Phase 8",
    "failure/recovery policy -> Phase 9",
):
    lines.append(
        item
    )


# =============================================================================
# 14. Runtime separation
# =============================================================================

section(
    "14. RUNTIME SEPARATION"
)

runtime_hits = []

for term in (
    "execution plan",
    "execution_plan",
    "schedule stage",
    "schedule_stage",
    "dispatch plan",
    "dispatch_plan",
):
    runtime_hits.extend(
        matches[term]
    )

runtime_hits = sorted(
    {
        item
        for item
        in runtime_hits
        if (
            "\\runtime\\"
            in item.lower()
            or "/runtime/"
            in item.lower()
        )
    }
)

if runtime_hits:

    lines.append(
        "Runtime execution-planning/scheduling evidence found:"
    )

    for item in runtime_hits:
        lines.append(
            f"  {item}"
        )

else:
    lines.append(
        "No Runtime execution-planning search hits found."
    )

lines.append("")
lines.append(
    (
        "Any Runtime queue/worker/scheduling plan is separate "
        "from UCF Phase 4.5 workflow execution planning."
    )
)


# =============================================================================
# 15. Discovery decision gate
# =============================================================================

section(
    "15. DISCOVERY DECISION GATE"
)

lines.extend(
    [
        "NO PRODUCTION FILE MODIFIED BY THIS SCAN",
        "",
        "Decision questions:",
        (
            "1. Are frozen 4.1 through 4.4 SHA values intact?"
        ),
        (
            "2. Is there already a UCF Phase 4.5 Execution Planner?"
        ),
        (
            "3. Should 4.5 consume Phase 4.4 "
            "RunnableStageResolution directly?"
        ),
        (
            "4. Should 4.5 plan only stages runnable NOW?"
        ),
        (
            "5. Or should 4.5 compute full remaining-workflow "
            "topological order?"
        ),
        (
            "6. Should simultaneously runnable stages remain "
            "one parallel execution batch/wave?"
        ),
        (
            "7. Does lexical ordering represent deterministic "
            "evidence rather than forced serial execution?"
        ),
        (
            "8. Should blocked/untracked stages be excluded "
            "from the immediate plan?"
        ),
        (
            "9. Should Runtime capacity, priority, queue state, "
            "workers, retries, or resource availability be excluded?"
        ),
        (
            "10. Should 4.5 return planning evidence but perform "
            "no dispatch/job creation?"
        ),
        (
            "11. Can 4.5 remain deterministic, read-only, "
            "side-effect-free, Runtime-independent, "
            "and persistence-free?"
        ),
        (
            "12. Does Phase 4.6 remain the sole certification "
            "authority for the completed planning subsystem?"
        ),
    ]
)


REPORT.write_text(
    "\n".join(
        lines
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 104)
print("PHASE 4.5 EXECUTION PLANNER DISCOVERY SCAN COMPLETE")
print("=" * 104)
print(
    "REPORT:",
    REPORT.name,
)
print(
    "FILES EXAMINED:",
    files_examined,
)
print(
    "OVERSIZED FILES SKIPPED:",
    files_skipped_large,
)
print(
    "READ ERRORS:",
    files_read_error,
)
print(
    "PHASE 4.1 SHA:",
    actual_41,
)
print(
    "PHASE 4.1 SHA MATCH:",
    actual_41 == EXPECTED_41_SHA,
)
print(
    "PHASE 4.2 SHA:",
    actual_42,
)
print(
    "PHASE 4.2 SHA MATCH:",
    actual_42 == EXPECTED_42_SHA,
)
print(
    "PHASE 4.3 SHA:",
    actual_43,
)
print(
    "PHASE 4.3 SHA MATCH:",
    actual_43 == EXPECTED_43_SHA,
)
print(
    "PHASE 4.4 SHA:",
    actual_44,
)
print(
    "PHASE 4.4 SHA MATCH:",
    actual_44 == EXPECTED_44_SHA,
)
print("=" * 104)
