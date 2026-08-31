from __future__ import annotations

import ast
import hashlib
from pathlib import Path


ROOT = Path.cwd()

REPORT = ROOT / (
    "coordination_runtime_bridge_phase_5_1_discovery_scan.txt"
)


# =============================================================================
# Candidate locations
# =============================================================================

targets = {
    "universal_job_contract":
        ROOT
        / "backend/server/runtime/universal_jobs/contract.py",

    "stage_reference":
        ROOT
        / "backend/server/coordination/universal_stages/contract.py",

    "stage_result":
        ROOT
        / "backend/server/coordination/universal_stages/result_contract.py",

    "pipeline_coordinator_contract":
        ROOT
        / "backend/server/coordination/pipeline_coordinators/contract.py",

    "workflow_contract":
        ROOT
        / "backend/server/coordination/universal_workflows/contract.py",

    "execution_planner":
        ROOT
        / (
            "backend/server/coordination/"
            "dependency_planning/execution_planner.py"
        ),

    "planning_certification":
        ROOT
        / (
            "backend/server/coordination/"
            "dependency_planning/planning_certification.py"
        ),

    "universal_runtime_infrastructure":
        ROOT
        / "backend/server/runtime/universal_runtime_infrastructure.py",
}


expected_frozen_shas = {
    "universal_job_contract":
        "E5BE8421D72627AB5DEC93C3CD45E4A314E956ACDA751C8A93ECD160CDACEE13",

    "stage_reference":
        "EAECFC26666CDE338ED2D3988A312B3812AB85B82F588EACD0D97633F656D00F",

    "stage_result":
        "B3469B10BB2F8F9372E4336784D09A143C78FABE45BF039B61B76F4A2DC33B24",

    "pipeline_coordinator_contract":
        "90E36C7DFC9B819EA3DCCDAB31E44CB5EA04F3A3ABEBF504C85AF83821944331",

    "workflow_contract":
        "9094A98D2B9DBD9CCED73514648BF5D5092E547D19446AB0FE18FBE7089",

    "execution_planner":
        "808743F566978530B2FC774DBD70A5FFA820F0EFE431512E882E0CF0F7B81958",

    "planning_certification":
        "8DB96F931C4C3B4F35C308400D838D18BA67E22ACAC08D5597394D29B9FD5723",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def section(lines, title):
    lines.extend(
        (
            "",
            "=" * 116,
            title,
            "=" * 116,
        )
    )


def public_api(path: Path):
    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(
        source
    )

    functions = []
    classes = []
    constants = []
    imports = []

    for node in tree.body:

        if isinstance(
            node,
            ast.FunctionDef,
        ):
            if not node.name.startswith("_"):
                functions.append(
                    (
                        node.name,
                        node.lineno,
                        node.end_lineno,
                    )
                )

        elif isinstance(
            node,
            ast.ClassDef,
        ):
            classes.append(
                (
                    node.name,
                    node.lineno,
                    node.end_lineno,
                )
            )

        elif isinstance(
            node,
            ast.Assign,
        ):
            for target in node.targets:
                if isinstance(
                    target,
                    ast.Name,
                ):
                    if target.id.isupper():
                        constants.append(
                            target.id
                        )

        elif isinstance(
            node,
            ast.AnnAssign,
        ):
            if isinstance(
                node.target,
                ast.Name,
            ):
                if node.target.id.isupper():
                    constants.append(
                        node.target.id
                    )

    for node in ast.walk(
        tree
    ):

        if isinstance(
            node,
            ast.ImportFrom,
        ):
            imports.append(
                node.module or ""
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

    return {
        "source": source,
        "tree": tree,
        "functions": functions,
        "classes": classes,
        "constants": constants,
        "imports": sorted(
            set(
                imports
            )
        ),
    }


lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.1 — COORDINATION → RUNTIME BRIDGE",
    "DISCOVERY SCAN",
]


# =============================================================================
# 1. Frozen upstream integrity
# =============================================================================

section(
    lines,
    "1. FROZEN UPSTREAM INTEGRITY",
)


for name, path in targets.items():

    lines.append("")
    lines.append(
        f"{name}"
    )

    lines.append(
        f"exists: {path.exists()}"
    )

    lines.append(
        f"path: {path.relative_to(ROOT)}"
    )

    if not path.exists():
        continue

    actual = sha256(
        path
    )

    lines.append(
        f"SHA256: {actual}"
    )

    expected = expected_frozen_shas.get(
        name
    )

    if expected is not None:
        lines.append(
            f"frozen SHA exact: "
            f"{actual == expected}"
        )


# =============================================================================
# 2. Universal Job Contract
# =============================================================================

section(
    lines,
    "2. UNIVERSAL JOB CONTRACT — RUNTIME INPUT AUTHORITY",
)


path = targets[
    "universal_job_contract"
]

if path.exists():

    info = public_api(
        path
    )

    lines.append(
        "Classes:"
    )

    for item in info[
        "classes"
    ]:
        lines.append(
            f"  {item}"
        )

    lines.append(
        "Public functions:"
    )

    for item in info[
        "functions"
    ]:
        lines.append(
            f"  {item}"
        )

    lines.append(
        "Constants:"
    )

    for item in info[
        "constants"
    ]:
        lines.append(
            f"  {item}"
        )

    lines.append("")
    lines.append(
        "Dataclass / annotated field candidates:"
    )

    for node in info[
        "tree"
    ].body:

        if not isinstance(
            node,
            ast.ClassDef,
        ):
            continue

        class_fields = []

        for child in node.body:

            if isinstance(
                child,
                ast.AnnAssign,
            ):

                if isinstance(
                    child.target,
                    ast.Name,
                ):
                    class_fields.append(
                        child.target.id
                    )

        if class_fields:
            lines.append(
                f"  {node.name}: "
                + repr(
                    class_fields
                )
            )


# =============================================================================
# 3. Runtime Registration discovery
# =============================================================================

section(
    lines,
    "3. UNIVERSAL RUNTIME REGISTRATION DISCOVERY",
)


registration_candidates = []

for path in ROOT.rglob(
    "*.py"
):

    parts = set(
        path.parts
    )

    if (
        ".venv" in parts
        or ".git" in parts
        or "node_modules" in parts
        or "__pycache__" in parts
        or "backups" in parts
        or "runtime_backups" in parts
    ):
        continue

    lower_name = (
        path.name.lower()
    )

    if (
        "registration" in lower_name
        or "registry" in lower_name
        or "handler_registry" in lower_name
    ):

        try:
            source = path.read_text(
                encoding="utf-8-sig"
            )

        except Exception:
            continue

        lower = source.lower()

        if (
            "job_type" in lower
            and (
                "handler" in lower
                or "registry" in lower
            )
        ):
            registration_candidates.append(
                path
            )


for path in sorted(
    set(
        registration_candidates
    )
):

    lines.append("")
    lines.append(
        str(
            path.relative_to(ROOT)
        )
    )

    try:
        info = public_api(
            path
        )

    except Exception as exc:
        lines.append(
            f"PARSE ERROR: {exc}"
        )
        continue

    lines.append(
        "  public functions:"
    )

    for item in info[
        "functions"
    ]:
        lines.append(
            f"    {item}"
        )

    lines.append(
        "  classes:"
    )

    for item in info[
        "classes"
    ]:
        lines.append(
            f"    {item}"
        )


if not registration_candidates:
    lines.append(
        "NO CANDIDATES FOUND"
    )


# =============================================================================
# 4. Universal Runtime entry-point discovery
# =============================================================================

section(
    lines,
    "4. UNIVERSAL RUNTIME ENTRY-POINT DISCOVERY",
)


runtime_candidates = []


for path in ROOT.rglob(
    "*.py"
):

    parts = set(
        path.parts
    )

    if (
        ".venv" in parts
        or ".git" in parts
        or "node_modules" in parts
        or "__pycache__" in parts
        or "backups" in parts
        or "runtime_backups" in parts
    ):
        continue

    path_lower = str(
        path
    ).lower()

    if (
        "runtime" not in path_lower
    ):
        continue

    try:
        source = path.read_text(
            encoding="utf-8-sig"
        )

    except Exception:
        continue

    lower = source.lower()

    runtime_terms = (
        "dispatch",
        "submit",
        "enqueue",
        "execute",
        "worker",
        "job_type",
        "handler",
        "create_job",
    )

    score = sum(
        1
        for term
        in runtime_terms
        if term in lower
    )

    if score >= 3:
        runtime_candidates.append(
            (
                score,
                path,
            )
        )


for score, path in sorted(
    runtime_candidates,
    key=lambda item: (
        -item[0],
        str(
            item[1]
        ),
    ),
)[:40]:

    lines.append("")
    lines.append(
        f"[score={score}] "
        + str(
            path.relative_to(ROOT)
        )
    )

    try:
        info = public_api(
            path
        )

    except Exception as exc:
        lines.append(
            f"  PARSE ERROR: {exc}"
        )
        continue

    lines.append(
        "  public functions:"
    )

    for item in info[
        "functions"
    ]:
        lines.append(
            f"    {item}"
        )

    lines.append(
        "  classes:"
    )

    for item in info[
        "classes"
    ]:
        lines.append(
            f"    {item}"
        )


# =============================================================================
# 5. Stage Reference Runtime fields
# =============================================================================

section(
    lines,
    "5. PHASE 1.3 STAGE REFERENCE — RUNTIME FIELDS",
)


path = targets[
    "stage_reference"
]

if path.exists():

    info = public_api(
        path
    )

    for node in info[
        "tree"
    ].body:

        if not isinstance(
            node,
            ast.ClassDef,
        ):
            continue

        class_fields = []

        for child in node.body:

            if isinstance(
                child,
                ast.AnnAssign,
            ):

                if isinstance(
                    child.target,
                    ast.Name,
                ):
                    class_fields.append(
                        child.target.id
                    )

        if class_fields:

            lines.append(
                f"{node.name}:"
            )

            for field_name in class_fields:
                lines.append(
                    f"  - {field_name}"
                )


# =============================================================================
# 6. Stage Result contract
# =============================================================================

section(
    lines,
    "6. PHASE 1.4 STAGE RESULT — RETURN CONTRACT",
)


path = targets[
    "stage_result"
]

if path.exists():

    info = public_api(
        path
    )

    for node in info[
        "tree"
    ].body:

        if not isinstance(
            node,
            ast.ClassDef,
        ):
            continue

        class_fields = []

        for child in node.body:

            if isinstance(
                child,
                ast.AnnAssign,
            ):

                if isinstance(
                    child.target,
                    ast.Name,
                ):
                    class_fields.append(
                        child.target.id
                    )

        if class_fields:

            lines.append(
                f"{node.name}:"
            )

            for field_name in class_fields:
                lines.append(
                    f"  - {field_name}"
                )


# =============================================================================
# 7. Coordinator Contract Runtime-related API
# =============================================================================

section(
    lines,
    "7. PIPELINE COORDINATOR CONTRACT — EXECUTION BOUNDARY",
)


path = targets[
    "pipeline_coordinator_contract"
]

if path.exists():

    info = public_api(
        path
    )

    lines.append(
        "Classes:"
    )

    for item in info[
        "classes"
    ]:
        lines.append(
            f"  {item}"
        )

    lines.append(
        "Public functions:"
    )

    for item in info[
        "functions"
    ]:
        lines.append(
            f"  {item}"
        )

    source_lower = (
        info[
            "source"
        ].lower()
    )

    for term in (
        "runtime",
        "dispatch",
        "job",
        "handler",
        "advance",
        "stage_completed",
        "stage_failed",
    ):
        lines.append(
            f"{term}: "
            f"{term in source_lower}"
        )


# =============================================================================
# 8. Phase 4.5 output contract
# =============================================================================

section(
    lines,
    "8. PHASE 4.5 EXECUTION PLAN — OUTBOUND PLANNING CONTRACT",
)


path = targets[
    "execution_planner"
]

if path.exists():

    info = public_api(
        path
    )

    for node in info[
        "tree"
    ].body:

        if not isinstance(
            node,
            ast.ClassDef,
        ):
            continue

        fields = []

        for child in node.body:

            if isinstance(
                child,
                ast.AnnAssign,
            ):

                if isinstance(
                    child.target,
                    ast.Name,
                ):
                    fields.append(
                        child.target.id
                    )

        if fields:
            lines.append(
                f"{node.name}:"
            )

            for field_name in fields:
                lines.append(
                    f"  - {field_name}"
                )


# =============================================================================
# 9. Existing coordination/runtime bridge candidates
# =============================================================================

section(
    lines,
    "9. EXISTING COORDINATION ↔ RUNTIME BRIDGE CANDIDATES",
)


bridge_hits = []


search_terms = (
    "coordination_runtime",
    "runtime_bridge",
    "coordination bridge",
    "workflow_job",
    "workflow job correlation",
    "runtime completion",
    "runtime failure",
)


for path in ROOT.rglob(
    "*.py"
):

    parts = set(
        path.parts
    )

    if (
        ".venv" in parts
        or ".git" in parts
        or "node_modules" in parts
        or "__pycache__" in parts
        or "backups" in parts
        or "runtime_backups" in parts
    ):
        continue

    try:
        source = path.read_text(
            encoding="utf-8-sig"
        )

    except Exception:
        continue

    lower = source.lower()

    matched = tuple(
        term
        for term
        in search_terms
        if term in lower
    )

    if matched:
        bridge_hits.append(
            (
                path,
                matched,
            )
        )


for path, matched in sorted(
    bridge_hits,
    key=lambda item:
        str(
            item[0]
        ),
):

    lines.append(
        str(
            path.relative_to(ROOT)
        )
        + " :: "
        + repr(
            matched
        )
    )


if not bridge_hits:
    lines.append(
        "NONE"
    )


# =============================================================================
# 10. Cross-layer imports
# =============================================================================

section(
    lines,
    "10. CURRENT COORDINATION ↔ RUNTIME CROSS-LAYER IMPORTS",
)


coord_root = (
    ROOT
    / "backend/server/coordination"
)

runtime_root = (
    ROOT
    / "backend/server/runtime"
)


def scan_cross_imports(
    base: Path,
    target_prefix: str,
):

    results = []

    if not base.exists():
        return results

    for path in base.rglob(
        "*.py"
    ):

        if "__pycache__" in path.parts:
            continue

        try:
            info = public_api(
                path
            )

        except Exception:
            continue

        matched = tuple(
            module
            for module
            in info[
                "imports"
            ]
            if module.startswith(
                target_prefix
            )
        )

        if matched:
            results.append(
                (
                    path,
                    matched,
                )
            )

    return results


coord_to_runtime = (
    scan_cross_imports(
        coord_root,
        "backend.server.runtime",
    )
)

runtime_to_coord = (
    scan_cross_imports(
        runtime_root,
        "backend.server.coordination",
    )
)


lines.append(
    "COORDINATION → RUNTIME:"
)

for path, imports in coord_to_runtime:
    lines.append(
        str(
            path.relative_to(ROOT)
        )
        + " :: "
        + repr(
            imports
        )
    )

if not coord_to_runtime:
    lines.append(
        "NONE"
    )


lines.append("")
lines.append(
    "RUNTIME → COORDINATION:"
)

for path, imports in runtime_to_coord:
    lines.append(
        str(
            path.relative_to(ROOT)
        )
        + " :: "
        + repr(
            imports
        )
    )

if not runtime_to_coord:
    lines.append(
        "NONE"
    )


# =============================================================================
# 11. Existing job identity / correlation fields
# =============================================================================

section(
    lines,
    "11. JOB / WORKFLOW / STAGE CORRELATION FIELD DISCOVERY",
)


identity_terms = (
    "job_id",
    "workflow_id",
    "stage_id",
    "attempt_id",
    "correlation_id",
    "parent_job_id",
    "workspace_id",
)


for name in (
    "universal_job_contract",
    "stage_reference",
    "stage_result",
    "workflow_contract",
):

    path = targets[
        name
    ]

    if not path.exists():
        continue

    source = path.read_text(
        encoding="utf-8-sig"
    )

    lines.append("")
    lines.append(
        name
    )

    for term in identity_terms:

        count = source.count(
            term
        )

        lines.append(
            f"  {term}: {count}"
        )


# =============================================================================
# 12. Phase 5.1 architecture questions
# =============================================================================

section(
    lines,
    "12. PHASE 5.1 ARCHITECTURE QUESTIONS",
)


questions = (
    "What is the canonical Runtime work-submission entry point?",
    "Does Runtime accept a Universal Job object, mapping, job_id, or queue record?",
    "Does Runtime Registration resolve handlers before or during dispatch?",
    "Which component creates the runtime job identity?",
    "Which fields can be mapped directly from StageReference?",
    "Which fields must come from workflow/coordinator execution context?",
    "Should 5.1 submit exactly one Phase 4.5 execution wave?",
    "Should 5.1 remain read-only with respect to workflow state?",
    "Should 5.1 perform no handler lookup itself?",
    "Should 5.1 perform no business-stage execution itself?",
    "Should job creation semantics belong to 5.2 rather than 5.1?",
    "Should workflow/job persistent correlation be deferred to 5.3?",
    "Should completion/failure handling be excluded from 5.1?",
    "Does a bridge component already exist that can be reused?",
)


for question in questions:
    lines.append(
        "- "
        + question
    )


REPORT.write_text(
    "\n".join(
        lines
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 116)
print("PHASE 5.1 COORDINATION → RUNTIME BRIDGE DISCOVERY SCAN COMPLETE")
print("=" * 116)
print(
    "REPORT:",
    REPORT.name,
)

print()

for name, path in targets.items():

    if path.exists():

        print(
            name,
            sha256(
                path
            ),
        )

print("=" * 116)
