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

WORKFLOW_CONTRACT = ROOT / (
    "backend/server/coordination/"
    "universal_workflows/contract.py"
)

LIFECYCLE_STATE_MACHINE = ROOT / (
    "backend/server/coordination/"
    "workflow_lifecycle/state_machine.py"
)

DEPENDENCY_DIR = ROOT / (
    "backend/server/coordination/"
    "dependency_planning"
)

REPORT = ROOT / (
    "runnable_stage_resolver_phase_4_4_discovery_scan.txt"
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
    lines.append("=" * 100)
    lines.append(title)
    lines.append("=" * 100)


lines.extend(
    [
        "LINKCRAFTOR",
        "UNIVERSAL COORDINATION FRAMEWORK",
        "PHASE 4.4 — RUNNABLE STAGE RESOLVER DISCOVERY SCAN",
        "=" * 100,
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

lines.append(
    f"Phase 4.1 SHA256: {actual_41}"
)

lines.append(
    "Phase 4.1 SHA matches frozen value: "
    + str(actual_41 == EXPECTED_41_SHA)
)

lines.append(
    f"Phase 4.2 SHA256: {actual_42}"
)

lines.append(
    "Phase 4.2 SHA matches frozen value: "
    + str(actual_42 == EXPECTED_42_SHA)
)

lines.append(
    f"Phase 4.3 SHA256: {actual_43}"
)

lines.append(
    "Phase 4.3 SHA matches frozen value: "
    + str(actual_43 == EXPECTED_43_SHA)
)


# =============================================================================
# 2. Current dependency-planning package
# =============================================================================

section(
    "2. CURRENT DEPENDENCY-PLANNING PACKAGE"
)

if DEPENDENCY_DIR.exists():

    files = sorted(
        path
        for path
        in DEPENDENCY_DIR.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
    )

    for path in files:
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
    "3. EXISTING RUNNABILITY / READY-STAGE AUTHORITY"
)

search_terms = (
    "runnable stage",
    "runnable_stage",
    "resolve_runnable",
    "ready stage",
    "ready_stage",
    "pending stage",
    "pending_stage",
    "completed stage",
    "completed_stage",
    "blocked stage",
    "blocked_stage",
    "prerequisite",
    "dependency satisfied",
    "dependencies satisfied",
    "stage eligibility",
    "eligible stage",
    "next stage",
    "next_stage",
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
# 4. Frozen 4.1 dependency APIs available to 4.4
# =============================================================================

section(
    "4. FROZEN PHASE 4.1 DEPENDENCY SURFACE"
)

source_41 = read_source(
    PHASE_41
)

tree_41 = ast.parse(
    source_41
)

public_41 = []

for node in tree_41.body:

    if isinstance(
        node,
        (
            ast.ClassDef,
            ast.FunctionDef,
        ),
    ):
        if not node.name.startswith("_"):
            public_41.append(
                node.name
            )

for name in public_41:
    lines.append(
        name
    )


# =============================================================================
# 5. Frozen 4.2 validation precondition
# =============================================================================

section(
    "5. FROZEN PHASE 4.2 VALIDATION PRECONDITION"
)

source_42 = read_source(
    PHASE_42
)

for marker in (
    "require_valid_dependency_graph",
    "self_dependency",
    "prohibited",
    "cycle detection (Phase 4.3)",
):
    lines.append(
        f"{marker}: "
        + str(
            marker in source_42
        )
    )


# =============================================================================
# 6. Frozen 4.3 cycle precondition
# =============================================================================

section(
    "6. FROZEN PHASE 4.3 ACYCLIC PRECONDITION"
)

source_43 = read_source(
    PHASE_43
)

for marker in (
    "require_acyclic_dependency_graph",
    "has_cycle",
    "runnable-stage resolution (Phase 4.4)",
    "execution ordering/planning (Phase 4.5)",
):
    lines.append(
        f"{marker}: "
        + str(
            marker in source_43
        )
    )


# =============================================================================
# 7. Workflow contract stage-state surfaces
# =============================================================================

section(
    "7. WORKFLOW CONTRACT STAGE-STATE SURFACE"
)

if WORKFLOW_CONTRACT.exists():

    workflow_source = read_source(
        WORKFLOW_CONTRACT
    )

    workflow_tree = ast.parse(
        workflow_source
    )

    relevant_fields = []

    for node in ast.walk(
        workflow_tree
    ):

        if isinstance(
            node,
            ast.AnnAssign,
        ) and isinstance(
            node.target,
            ast.Name,
        ):

            name = node.target.id

            if any(
                token in name.lower()
                for token in (
                    "stage",
                    "completed",
                    "pending",
                    "failed",
                    "skipped",
                    "current",
                )
            ):
                if name not in relevant_fields:
                    relevant_fields.append(
                        name
                    )

    lines.append(
        "Relevant Workflow Contract fields:"
    )

    for name in relevant_fields:
        lines.append(
            f"  {name}"
        )

else:
    lines.append(
        "WORKFLOW CONTRACT FILE MISSING"
    )


# =============================================================================
# 8. Lifecycle state-machine relevance
# =============================================================================

section(
    "8. LIFECYCLE STATE-MACHINE RELEVANCE"
)

if LIFECYCLE_STATE_MACHINE.exists():

    lifecycle_source = read_source(
        LIFECYCLE_STATE_MACHINE
    )

    markers = (
        "CREATED",
        "READY",
        "RUNNING",
        "WAITING",
        "PAUSED",
        "RECOVERING",
        "COMPLETED",
        "FAILED",
        "CANCELLED",
        "ABORTED",
    )

    for marker in markers:
        lines.append(
            f"{marker}: "
            + str(
                marker in lifecycle_source
            )
        )

else:
    lines.append(
        "LIFECYCLE STATE MACHINE FILE MISSING"
    )


# =============================================================================
# 9. Candidate runnable semantics
# =============================================================================

section(
    "9. PHASE 4.4 CANDIDATE RUNNABILITY SEMANTICS"
)

candidate_semantics = (
    (
        "graph_precondition",
        (
            "graph must pass 4.2 validation "
            "and 4.3 acyclic guard"
        ),
    ),
    (
        "completed_stage",
        "never returned runnable",
    ),
    (
        "failed_stage",
        "not returned runnable",
    ),
    (
        "skipped_stage",
        "not returned runnable",
    ),
    (
        "pending_stage",
        (
            "candidate only; prerequisites "
            "must also be satisfied"
        ),
    ),
    (
        "root_stage",
        (
            "runnable when not terminalized "
            "and not already completed"
        ),
    ),
    (
        "dependent_stage",
        (
            "runnable only when all direct "
            "prerequisites are satisfied"
        ),
    ),
    (
        "all_prerequisites_completed",
        "candidate runnable",
    ),
    (
        "some_prerequisites_incomplete",
        "blocked",
    ),
    (
        "empty_graph",
        "no runnable stages",
    ),
    (
        "isolated_nodes",
        (
            "runnable when eligible by "
            "workflow stage-state input"
        ),
    ),
    (
        "result_order",
        "lexical deterministic",
    ),
)


for name, meaning in candidate_semantics:
    lines.append(
        f"{name}: {meaning}"
    )


# =============================================================================
# 10. Critical question: source of completion state
# =============================================================================

section(
    "10. COMPLETION-STATE AUTHORITY DECISION"
)

lines.extend(
    [
        (
            "Question: Where should Phase 4.4 obtain "
            "completed/failed/skipped/current stage state?"
        ),
        "",
        (
            "Candidate A: accept explicit immutable "
            "stage-state inputs into resolver."
        ),
        "",
        (
            "Candidate B: accept UniversalWorkflowContract "
            "instance directly."
        ),
        "",
        (
            "Discovery must determine the narrowest "
            "correct dependency boundary."
        ),
        "",
        (
            "Phase 4.4 must NOT read persistence stores "
            "or Runtime job state directly."
        ),
    ]
)


# =============================================================================
# 11. Critical question: pending stage membership
# =============================================================================

section(
    "11. STAGE-MEMBERSHIP DECISION"
)

lines.extend(
    [
        (
            "Question: Is graph.node_ids the complete "
            "candidate-stage universe?"
        ),
        "",
        (
            "Or should pending_stages/current_stage from "
            "the Workflow Contract restrict the candidate set?"
        ),
        "",
        (
            "Phase 4.4 must not silently invent workflow "
            "membership semantics."
        ),
    ]
)


# =============================================================================
# 12. Critical question: failed/skipped prerequisite semantics
# =============================================================================

section(
    "12. PREREQUISITE SATISFACTION DECISION"
)

lines.extend(
    [
        (
            "Question: Does only COMPLETED satisfy a prerequisite?"
        ),
        "",
        (
            "Should SKIPPED satisfy a prerequisite?"
        ),
        "",
        (
            "Should FAILED ever satisfy a prerequisite?"
        ),
        "",
        (
            "Preliminary boundary:"
        ),
        (
            "  COMPLETED = satisfied"
        ),
        (
            "  FAILED = not satisfied"
        ),
        (
            "  SKIPPED = unresolved until architecture "
            "evidence is reviewed"
        ),
        "",
        (
            "Do not freeze skipped semantics from assumption."
        ),
    ]
)


# =============================================================================
# 13. Candidate implementation identity
# =============================================================================

section(
    "13. CANDIDATE PHASE 4.4 IMPLEMENTATION IDENTITY"
)

lines.extend(
    [
        (
            "Candidate file: "
            "backend/server/coordination/"
            "dependency_planning/runnable_stage_resolver.py"
        ),
        (
            "Candidate version: "
            "runnable_stage_resolver_v4.4.0"
        ),
        (
            "Candidate schema: "
            "runnable_stage_resolver_schema_v1"
        ),
        (
            "Primary topology input: "
            "frozen Phase 4.1 DependencyGraph"
        ),
        (
            "Required validation precondition: "
            "frozen Phase 4.2"
        ),
        (
            "Required acyclic precondition: "
            "frozen Phase 4.3"
        ),
        (
            "Candidate result: "
            "immutable RunnableStageResolution"
        ),
    ]
)


# =============================================================================
# 14. Explicit non-authority
# =============================================================================

section(
    "14. PHASE 4.4 EXPLICIT NON-AUTHORITY"
)

for item in (
    "dependency graph construction -> 4.1",
    "dependency semantic validation -> 4.2",
    "cycle detection -> 4.3",
    "execution planning/order -> 4.5",
    "planning certification -> 4.6",
    "Runtime dispatch/execution -> Phase 5",
    "stage result handoff -> Phase 6",
    "fan-out/fan-in policy -> Phase 7",
    "persistence/checkpointing -> Phase 8",
    "failure/recovery policy -> Phase 9",
):
    lines.append(
        item
    )


# =============================================================================
# 15. Runtime separation
# =============================================================================

section(
    "15. RUNTIME SEPARATION"
)

runtime_hits = []

for term in (
    "runnable stage",
    "ready stage",
    "next stage",
    "stage eligibility",
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
        "Runtime runnability-related evidence found:"
    )

    for item in runtime_hits:
        lines.append(
            f"  {item}"
        )

else:
    lines.append(
        "No Runtime runnability search hits found."
    )

lines.append("")
lines.append(
    (
        "Any Runtime scheduling/ready-job semantics are "
        "separate from UCF workflow-stage runnability."
    )
)


# =============================================================================
# 16. Discovery decision gate
# =============================================================================

section(
    "16. DISCOVERY DECISION GATE"
)

lines.extend(
    [
        "NO PRODUCTION FILE MODIFIED BY THIS SCAN",
        "",
        "Decision questions:",
        (
            "1. Are frozen 4.1, 4.2, and 4.3 SHAs intact?"
        ),
        (
            "2. Is there already a UCF runnable-stage resolver?"
        ),
        (
            "3. What is the canonical source of stage completion state?"
        ),
        (
            "4. Is graph.node_ids the full candidate-stage universe?"
        ),
        (
            "5. Does only COMPLETED satisfy a dependency?"
        ),
        (
            "6. What should SKIPPED mean for dependency satisfaction?"
        ),
        (
            "7. Should FAILED always block dependents?"
        ),
        (
            "8. Should root/isolated stages be immediately runnable?"
        ),
        (
            "9. Should 4.4 return only runnable IDs or also blocked evidence?"
        ),
        (
            "10. Can 4.4 remain deterministic, read-only, "
            "side-effect-free, Runtime-independent, and persistence-free?"
        ),
        (
            "11. Does execution ordering remain strictly Phase 4.5?"
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
print("=" * 100)
print("PHASE 4.4 RUNNABLE STAGE RESOLVER DISCOVERY SCAN COMPLETE")
print("=" * 100)
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
print("=" * 100)
