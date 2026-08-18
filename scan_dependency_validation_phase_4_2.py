from __future__ import annotations

import ast
import hashlib
from pathlib import Path


ROOT = Path.cwd()

PHASE_41 = ROOT / (
    "backend/server/coordination/"
    "dependency_planning/dependency_graph.py"
)

STAGE_REFERENCE = ROOT / (
    "backend/server/coordination/"
    "universal_stages/contract.py"
)

WORKFLOW_CONTRACT = ROOT / (
    "backend/server/coordination/"
    "universal_workflows/contract.py"
)

DEPENDENCY_DIR = ROOT / (
    "backend/server/coordination/"
    "dependency_planning"
)

REPORT = ROOT / (
    "dependency_validation_phase_4_2_discovery_scan.txt"
)


EXPECTED_41_SHA = (
    "4F6BA62D011C31D9D851FBBABC37C12B"
    "7DDAA1FD9A91E34788EBCE25741A1F70"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def read_source(path: Path) -> str:
    return path.read_text(
        encoding="utf-8-sig"
    )


def section(title: str) -> None:
    lines.append("")
    lines.append("=" * 100)
    lines.append(title)
    lines.append("=" * 100)


lines: list[str] = []

lines.extend(
    [
        "LINKCRAFTOR",
        "UNIVERSAL COORDINATION FRAMEWORK",
        "PHASE 4.2 — DEPENDENCY VALIDATION DISCOVERY SCAN",
        "=" * 100,
    ]
)


# ============================================================================
# 1. Frozen Phase 4.1 integrity
# ============================================================================

section(
    "1. FROZEN PHASE 4.1 INTEGRITY"
)

lines.append(
    f"Phase 4.1 file exists: {PHASE_41.exists()}"
)

if PHASE_41.exists():
    actual_41_sha = sha256(
        PHASE_41
    )

    lines.append(
        f"Phase 4.1 SHA256: {actual_41_sha}"
    )

    lines.append(
        "Phase 4.1 SHA matches frozen value: "
        + str(
            actual_41_sha
            == EXPECTED_41_SHA
        )
    )

else:
    actual_41_sha = "MISSING"


# ============================================================================
# 2. Existing dependency-planning files
# ============================================================================

section(
    "2. EXISTING DEPENDENCY-PLANNING FILES"
)

if DEPENDENCY_DIR.exists():

    files = sorted(
        path
        for path
        in DEPENDENCY_DIR.rglob("*")
        if path.is_file()
    )

    if files:
        for path in files:
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


# ============================================================================
# 3. Search repository for existing dependency-validation authority
# ============================================================================

section(
    "3. EXISTING DEPENDENCY VALIDATION / CYCLE / RUNNABILITY AUTHORITY"
)

search_terms = (
    "dependency validation",
    "validate_dependency",
    "validate_dependencies",
    "dependency_validator",
    "self-dependency",
    "self dependency",
    "cycle detection",
    "detect_cycle",
    "topological_sort",
    "runnable stage",
    "resolve_runnable",
    "execution planner",
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

    try:
        text = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )
    except Exception:
        continue

    lowered = text.lower()

    for term in search_terms:
        if term.lower() in lowered:
            matches[
                term
            ].append(
                str(
                    path.relative_to(ROOT)
                )
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
        for item in found[:50]:
            lines.append(
                f"  {item}"
            )
    else:
        lines.append(
            "  NONE"
        )


# ============================================================================
# 4. Inspect frozen Phase 4.1 public contract
# ============================================================================

section(
    "4. PHASE 4.1 PUBLIC CONTRACT"
)

if PHASE_41.exists():

    source_41 = read_source(
        PHASE_41
    )

    tree_41 = ast.parse(
        source_41
    )

    public_names = []

    for node in tree_41.body:

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
                public_names.append(
                    node.name
                )

    lines.append(
        "Public classes/functions:"
    )

    for name in public_names:
        lines.append(
            f"  {name}"
        )

    lines.append("")
    lines.append(
        "Phase 4.1 authority markers:"
    )

    authority_markers = (
        "semantic dependency validity (Phase 4.2)",
        "self-dependency rejection (Phase 4.2)",
        "cycle detection (Phase 4.3)",
        "runnable-stage resolution (Phase 4.4)",
        "execution planning (Phase 4.5)",
        "Runtime dispatch or job execution (Phase 5)",
    )

    for marker in authority_markers:
        lines.append(
            f"{marker}: "
            + str(
                marker in source_41
            )
        )


# ============================================================================
# 5. Inspect stage-reference identity contract
# ============================================================================

section(
    "5. UNIVERSAL STAGE REFERENCE IDENTITY SURFACE"
)

if STAGE_REFERENCE.exists():

    stage_source = read_source(
        STAGE_REFERENCE
    )

    stage_tree = ast.parse(
        stage_source
    )

    stage_fields = []

    for node in ast.walk(
        stage_tree
    ):

        if isinstance(
            node,
            ast.ClassDef,
        ) and node.name == "UniversalStageReference":

            for child in node.body:

                if isinstance(
                    child,
                    ast.AnnAssign,
                ) and isinstance(
                    child.target,
                    ast.Name,
                ):
                    stage_fields.append(
                        child.target.id
                    )

    lines.append(
        "UniversalStageReference fields:"
    )

    for field in stage_fields:
        lines.append(
            f"  {field}"
        )

    lines.append("")
    lines.append(
        "stage_id present: "
        + str(
            "stage_id"
            in stage_fields
        )
    )

    dependency_named_fields = [
        field
        for field
        in stage_fields
        if (
            "depend"
            in field.lower()
            or "prereq"
            in field.lower()
        )
    ]

    lines.append(
        "dependency/prerequisite fields: "
        + repr(
            dependency_named_fields
        )
    )

else:
    lines.append(
        "Universal Stage Reference file missing"
    )


# ============================================================================
# 6. Inspect workflow contract for dependency authority
# ============================================================================

section(
    "6. UNIVERSAL WORKFLOW CONTRACT DEPENDENCY SURFACE"
)

if WORKFLOW_CONTRACT.exists():

    workflow_source = read_source(
        WORKFLOW_CONTRACT
    )

    workflow_tree = ast.parse(
        workflow_source
    )

    workflow_fields = []

    for node in ast.walk(
        workflow_tree
    ):

        if isinstance(
            node,
            ast.ClassDef,
        ):

            for child in node.body:

                if isinstance(
                    child,
                    ast.AnnAssign,
                ) and isinstance(
                    child.target,
                    ast.Name,
                ):

                    name = child.target.id

                    if name not in workflow_fields:
                        workflow_fields.append(
                            name
                        )

    relevant = [
        field
        for field
        in workflow_fields
        if any(
            token in field.lower()
            for token in (
                "workflow",
                "stage",
                "depend",
                "prereq",
                "completed",
                "pending",
                "failed",
            )
        )
    ]

    lines.append(
        "Relevant workflow contract fields:"
    )

    for field in relevant:
        lines.append(
            f"  {field}"
        )

    dependency_fields = [
        field
        for field
        in workflow_fields
        if (
            "depend"
            in field.lower()
            or "prereq"
            in field.lower()
        )
    ]

    lines.append("")
    lines.append(
        "dependency/prerequisite fields: "
        + repr(
            dependency_fields
        )
    )

else:
    lines.append(
        "Universal Workflow Contract file missing"
    )


# ============================================================================
# 7. Candidate Phase 4.2 validation surface
# ============================================================================

section(
    "7. PHASE 4.2 CANDIDATE VALIDATION SURFACE"
)

candidate_rules = (
    (
        "graph_type",
        "input must be DependencyGraph",
    ),
    (
        "workflow_identity",
        "workflow_id must already satisfy frozen 4.1 contract",
    ),
    (
        "node_identity",
        "every node must be canonical stage_id",
    ),
    (
        "edge_identity",
        "every edge must be canonical DependencyEdge",
    ),
    (
        "edge_endpoint_membership",
        "every edge endpoint must exist in canonical node set",
    ),
    (
        "self_dependency",
        "prerequisite_stage_id must not equal dependent_stage_id",
    ),
    (
        "graph_version",
        "graph_version must equal frozen 4.1 version",
    ),
    (
        "deterministic_validation",
        "same graph must produce same result/evidence",
    ),
)

for name, meaning in candidate_rules:
    lines.append(
        f"{name}: {meaning}"
    )


# ============================================================================
# 8. Explicit NON-authority
# ============================================================================

section(
    "8. PHASE 4.2 EXPLICIT NON-AUTHORITY"
)

non_authority = (
    "cycle detection -> Phase 4.3",
    "topological sorting -> Phase 4.3 / 4.5",
    "runnable-stage resolution -> Phase 4.4",
    "execution planning -> Phase 4.5",
    "planning certification -> Phase 4.6",
    "Runtime execution -> Phase 5",
    "stage handoff -> Phase 6",
    "persistence -> Phase 8",
    "recovery -> Phase 9",
)

for item in non_authority:
    lines.append(
        item
    )


# ============================================================================
# 9. Candidate implementation identity
# ============================================================================

section(
    "9. CANDIDATE PHASE 4.2 IMPLEMENTATION IDENTITY"
)

lines.extend(
    [
        (
            "Candidate file: "
            "backend/server/coordination/"
            "dependency_planning/dependency_validation.py"
        ),
        (
            "Candidate version: "
            "dependency_validation_v4.2.0"
        ),
        (
            "Candidate schema: "
            "dependency_validation_schema_v1"
        ),
        (
            "Primary input: "
            "frozen Phase 4.1 DependencyGraph"
        ),
        (
            "Primary result: "
            "immutable DependencyValidationResult"
        ),
        (
            "Candidate APIs: "
            "validate_dependency_graph, "
            "require_valid_dependency_graph, "
            "dependency_validation_snapshot, "
            "explain_dependency_validation_v4_2"
        ),
    ]
)


# ============================================================================
# 10. Discovery decision gate
# ============================================================================

section(
    "10. DISCOVERY DECISION GATE"
)

lines.extend(
    [
        "NO PRODUCTION FILE MODIFIED BY THIS SCAN",
        "",
        "Decision questions:",
        "1. Is frozen 4.1 SHA intact?",
        "2. Does any existing component already own dependency validation?",
        "3. Is stage_id still the canonical node identity?",
        "4. Does Phase 1.3 contain no dependency/prerequisite field?",
        "5. Does Phase 4.2 own self-dependency rejection?",
        "6. Does Phase 4.3 remain sole cycle-detection authority?",
        "7. Can 4.2 validate graph semantics without Runtime/planning coupling?",
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
print("PHASE 4.2 DEPENDENCY VALIDATION DISCOVERY SCAN COMPLETE")
print("=" * 100)
print(
    "REPORT:",
    REPORT.name,
)
print(
    "PHASE 4.1 SHA:",
    actual_41_sha,
)
print(
    "PHASE 4.1 SHA MATCH:",
    actual_41_sha
    == EXPECTED_41_SHA,
)
print("=" * 100)
