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

DEPENDENCY_DIR = ROOT / (
    "backend/server/coordination/"
    "dependency_planning"
)

REPORT = ROOT / (
    "cycle_detection_phase_4_3_discovery_scan.txt"
)


EXPECTED_41_SHA = (
    "4F6BA62D011C31D9D851FBBABC37C12B"
    "7DDAA1FD9A91E34788EBCE25741A1F70"
)

EXPECTED_42_SHA = (
    "1D053C0036EA9F7A8AEDFAFC36F6EB82"
    "A681EDC7EF206409E9FFB8C7F212852D"
)


# Keep repository discovery bounded.
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
        "PHASE 4.3 — CYCLE DETECTION DISCOVERY SCAN",
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

lines.append(
    f"Phase 4.1 SHA256: {actual_41}"
)

lines.append(
    "Phase 4.1 SHA matches frozen value: "
    + str(
        actual_41 == EXPECTED_41_SHA
    )
)

lines.append(
    f"Phase 4.2 SHA256: {actual_42}"
)

lines.append(
    "Phase 4.2 SHA matches frozen value: "
    + str(
        actual_42 == EXPECTED_42_SHA
    )
)


# =============================================================================
# 2. Current dependency-planning package
# =============================================================================

section(
    "2. CURRENT DEPENDENCY-PLANNING PACKAGE"
)

if DEPENDENCY_DIR.exists():

    found_files = sorted(
        path
        for path
        in DEPENDENCY_DIR.rglob("*")
        if path.is_file()
        and "__pycache__"
        not in path.parts
    )

    if found_files:

        for path in found_files:
            lines.append(
                str(
                    path.relative_to(ROOT)
                )
            )

    else:
        lines.append(
            "NO FILES FOUND"
        )

else:
    lines.append(
        "DEPENDENCY-PLANNING DIRECTORY MISSING"
    )


# =============================================================================
# 3. Safe repository search for existing cycle authority
# =============================================================================

section(
    "3. EXISTING CYCLE / TOPOLOGICAL AUTHORITY"
)

search_terms = (
    "cycle detection",
    "detect_cycle",
    "find_cycle",
    "has_cycle",
    "cyclic",
    "topological sort",
    "topological_sort",
    "kahn",
    "strongly connected",
    "strongly_connected",
    "dependency cycle",
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

matches: dict[str, list[str]] = {
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

    # Stop reading a file once every still-needed term
    # has already matched in it.
    found_in_file: set[str] = set()

    try:
        with path.open(
            "r",
            encoding="utf-8",
            errors="ignore",
        ) as handle:

            for raw_line in handle:

                lowered_line = raw_line.lower()

                for term in search_terms:

                    if term in found_in_file:
                        continue

                    if (
                        len(matches[term])
                        >= MAX_MATCHES_PER_TERM
                    ):
                        continue

                    if term.lower() in lowered_line:

                        matches[term].append(
                            relative
                        )

                        found_in_file.add(
                            term
                        )

                if all(
                    (
                        term in found_in_file
                        or len(matches[term])
                        >= MAX_MATCHES_PER_TERM
                    )
                    for term in search_terms
                ):
                    break

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
    f"Oversized files skipped (> {MAX_FILE_BYTES} bytes): "
    f"{files_skipped_large}"
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
# 4. Frozen 4.1 topology authority
# =============================================================================

section(
    "4. FROZEN PHASE 4.1 TOPOLOGY AUTHORITY"
)

source_41 = read_source(
    PHASE_41
)

markers_41 = (
    "self_edges",
    "cycles",
    "Phase 4.3 owns detection",
    "dependency_roots",
    "dependency_leaves",
    "stage_prerequisites",
    "stage_dependents",
)

for marker in markers_41:

    lines.append(
        f"{marker}: "
        + str(
            marker in source_41
        )
    )


# =============================================================================
# 5. Frozen 4.2 validation boundary
# =============================================================================

section(
    "5. FROZEN PHASE 4.2 VALIDATION BOUNDARY"
)

source_42 = read_source(
    PHASE_42
)

markers_42 = (
    "cycle detection (Phase 4.3)",
    (
        "A cyclic graph without a self-dependency "
        "remains valid at Phase 4.2."
    ),
    "self_dependency",
    "prohibited",
    "Phase 4.3 owns cycle detection",
)

for marker in markers_42:

    lines.append(
        f"{marker}: "
        + str(
            marker in source_42
        )
    )


# =============================================================================
# 6. Public upstream APIs
# =============================================================================

section(
    "6. AVAILABLE PHASE 4.3 INPUT SURFACES"
)

for phase_name, path in (
    ("4.1", PHASE_41),
    ("4.2", PHASE_42),
):

    source = read_source(
        path
    )

    tree = ast.parse(
        source
    )

    public = []

    for node in tree.body:

        if isinstance(
            node,
            (
                ast.ClassDef,
                ast.FunctionDef,
            ),
        ):

            if not node.name.startswith(
                "_"
            ):

                public.append(
                    node.name
                )

    lines.append("")
    lines.append(
        f"Phase {phase_name} public classes/functions:"
    )

    for name in public:
        lines.append(
            f"  {name}"
        )


# =============================================================================
# 7. Candidate cycle semantics
# =============================================================================

section(
    "7. PHASE 4.3 CANDIDATE CYCLE SEMANTICS"
)

candidate_semantics = (
    (
        "input_validation",
        (
            "graph must pass frozen Phase 4.2 "
            "before cycle analysis"
        ),
    ),
    (
        "self_edge",
        (
            "normally rejected upstream by "
            "Phase 4.2"
        ),
    ),
    (
        "cycle_definition",
        (
            "directed dependency path returning "
            "to an already-active stage"
        ),
    ),
    (
        "two_node_cycle",
        "cyclic",
    ),
    (
        "multi_node_cycle",
        "cyclic",
    ),
    (
        "acyclic_chain",
        "acyclic",
    ),
    (
        "branch_join_without_back_edge",
        "acyclic",
    ),
    (
        "isolated_nodes",
        "acyclic",
    ),
    (
        "empty_graph",
        "acyclic",
    ),
    (
        "multiple_cycles",
        (
            "must produce deterministic "
            "cycle evidence"
        ),
    ),
    (
        "cycle_evidence",
        (
            "canonical deterministic stage-id "
            "cycle path(s)"
        ),
    ),
)

for name, meaning in candidate_semantics:

    lines.append(
        f"{name}: {meaning}"
    )


# =============================================================================
# 8. Algorithm options
# =============================================================================

section(
    "8. CYCLE-DETECTION ALGORITHM OPTIONS"
)

lines.extend(
    [
        "Option A: deterministic DFS active-stack detection",
        "  - directly produces cycle-path evidence",
        "  - nodes traversed lexically",
        "  - dependents traversed lexically",
        "",
        "Option B: Kahn indegree elimination",
        "  - excellent cyclic/acyclic determination",
        "  - does not naturally expose exact cycle path",
        "",
        "Architecture recommendation:",
        "  deterministic DFS for Phase 4.3",
        "  cycle detection/evidence only",
        "  NO authoritative execution ordering",
    ]
)


# =============================================================================
# 9. Candidate implementation
# =============================================================================

section(
    "9. CANDIDATE PHASE 4.3 IMPLEMENTATION IDENTITY"
)

lines.extend(
    [
        (
            "Candidate file: "
            "backend/server/coordination/"
            "dependency_planning/cycle_detection.py"
        ),
        (
            "Candidate version: "
            "cycle_detection_v4.3.0"
        ),
        (
            "Candidate schema: "
            "cycle_detection_schema_v1"
        ),
        (
            "Primary input: "
            "frozen Phase 4.1 DependencyGraph"
        ),
        (
            "Required precondition: "
            "frozen Phase 4.2 validation passes"
        ),
        (
            "Candidate result: "
            "immutable CycleDetectionResult"
        ),
        (
            "Candidate APIs: "
            "detect_dependency_cycles, "
            "require_acyclic_dependency_graph, "
            "cycle_detection_snapshot, "
            "explain_cycle_detection_v4_3"
        ),
    ]
)


# =============================================================================
# 10. Explicit non-authority
# =============================================================================

section(
    "10. PHASE 4.3 EXPLICIT NON-AUTHORITY"
)

for item in (
    "dependency graph construction -> Phase 4.1",
    "dependency semantic validation -> Phase 4.2",
    "runnable-stage resolution -> Phase 4.4",
    "execution planning -> Phase 4.5",
    "planning certification -> Phase 4.6",
    "Runtime execution -> Phase 5",
    "stage handoff -> Phase 6",
    "persistence -> Phase 8",
    "recovery -> Phase 9",
):
    lines.append(
        item
    )


# =============================================================================
# 11. Topological-sort ownership
# =============================================================================

section(
    "11. TOPOLOGICAL SORT OWNERSHIP DECISION"
)

lines.extend(
    [
        (
            "Should Phase 4.3 return an authoritative "
            "topological execution order?"
        ),
        "",
        "NO.",
        "",
        (
            "Phase 4.3 may use traversal order internally "
            "for cycle analysis."
        ),
        (
            "It must not publish execution ordering, "
            "runnable ordering, or an execution plan."
        ),
        "",
        (
            "Runnable-stage authority remains Phase 4.4."
        ),
        (
            "Execution-planning authority remains Phase 4.5."
        ),
    ]
)


# =============================================================================
# 12. Runtime separation
# =============================================================================

section(
    "12. RUNTIME SEPARATION"
)

runtime_hits = sorted(
    set(
        matches[
            "cycle detection"
        ]
        + matches[
            "cyclic"
        ]
        + matches[
            "dependency cycle"
        ]
    )
)

runtime_hits = tuple(
    item
    for item
    in runtime_hits
    if (
        "\\runtime\\"
        in item.lower()
        or "/runtime/"
        in item.lower()
    )
)

if runtime_hits:

    lines.append(
        "Runtime cycle/dependency-related evidence found:"
    )

    for item in runtime_hits:
        lines.append(
            f"  {item}"
        )

else:
    lines.append(
        "No Runtime cycle/dependency search hits found."
    )

lines.append("")
lines.append(
    (
        "Any Runtime dependency/cycle subsystem is "
        "separate Runtime authority and must not be "
        "imported into UCF Phase 4.3."
    )
)


# =============================================================================
# 13. Discovery decision gate
# =============================================================================

section(
    "13. DISCOVERY DECISION GATE"
)

lines.extend(
    [
        "NO PRODUCTION FILE MODIFIED BY THIS SCAN",
        "",
        "Decision questions:",
        (
            "1. Are frozen 4.1 and 4.2 SHA values intact?"
        ),
        (
            "2. Is there an existing UCF Phase 4.3 "
            "Cycle Detection component?"
        ),
        (
            "3. Is Runtime dependency/cycle logic "
            "architecturally separate?"
        ),
        (
            "4. Should 4.3 consume only graphs that "
            "pass Phase 4.2 validation?"
        ),
        (
            "5. Are self-dependencies expected to be "
            "rejected before 4.3?"
        ),
        (
            "6. Should 4.3 return deterministic cycle "
            "path evidence?"
        ),
        (
            "7. Should execution/topological ordering "
            "remain outside 4.3?"
        ),
        (
            "8. Can 4.3 remain deterministic, read-only, "
            "side-effect-free, and Runtime-independent?"
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
print("PHASE 4.3 CYCLE DETECTION DISCOVERY SCAN COMPLETE")
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
    actual_41
    == EXPECTED_41_SHA,
)
print(
    "PHASE 4.2 SHA:",
    actual_42,
)
print(
    "PHASE 4.2 SHA MATCH:",
    actual_42
    == EXPECTED_42_SHA,
)
print("=" * 100)
