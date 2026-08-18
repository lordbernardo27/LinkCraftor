from __future__ import annotations

import ast
import hashlib
from pathlib import Path


ROOT = Path.cwd()

PACKAGE = ROOT / (
    "backend/server/coordination/"
    "dependency_planning"
)

REPORT = ROOT / (
    "planning_certification_phase_4_6_discovery_scan.txt"
)


canonical_files = {
    "4.1": PACKAGE / "dependency_graph.py",
    "4.2": PACKAGE / "dependency_validation.py",
    "4.3": PACKAGE / "cycle_detection.py",
    "4.4": PACKAGE / "runnable_stage_resolver.py",
    "4.5": PACKAGE / "execution_planner.py",
}

expected_shas = {
    "4.1":
        "4F6BA62D011C31D9D851FBBABC37C12B"
        "7DDAA1FD9A91E34788EBCE25741A1F70",

    "4.2":
        "1D053C0036EA9F7A8AEDFAFC36F6EB82"
        "A681EDC7EF206409E9FFB8C7F212852D",

    "4.3":
        "E77BF605724F991E85C7FE2E5329051E"
        "16ECB2F30ACDAEA8AA40A2FD47487CEA",

    "4.4":
        "2779D432A2F3337F3557C61664499669"
        "CC852773AB74447297E98D6188289483",

    "4.5":
        "808743F566978530B2FC774DBD70A5FFA"
        "820F0EFE431512E882E0CF0F7B81958",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def section(lines, title):
    lines.extend(
        (
            "",
            "=" * 108,
            title,
            "=" * 108,
        )
    )


lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 4.6 — PLANNING CERTIFICATION DISCOVERY SCAN",
    "=" * 108,
]


# =============================================================================
# 1. Canonical Phase 4 integrity
# =============================================================================

section(
    lines,
    "1. CANONICAL PHASE 4 SOURCE INTEGRITY",
)

for phase, path in canonical_files.items():

    exists = path.exists()

    lines.append(
        f"{phase} exists: {exists}"
    )

    lines.append(
        f"{phase} file: "
        f"{path.relative_to(ROOT)}"
    )

    if exists:
        actual = sha256(path)

        lines.append(
            f"{phase} SHA256: {actual}"
        )

        lines.append(
            f"{phase} SHA exact: "
            f"{actual == expected_shas[phase]}"
        )


# =============================================================================
# 2. Package inventory
# =============================================================================

section(
    lines,
    "2. DEPENDENCY_PLANNING PACKAGE INVENTORY",
)

if PACKAGE.exists():

    for path in sorted(
        PACKAGE.rglob("*")
    ):

        if not path.is_file():
            continue

        if "__pycache__" in path.parts:
            continue

        lines.append(
            str(
                path.relative_to(ROOT)
            )
        )

else:
    lines.append(
        "PACKAGE NOT FOUND"
    )


# =============================================================================
# 3. Existing Phase 4.6 / planning certification candidates
# =============================================================================

section(
    lines,
    "3. EXISTING PLANNING CERTIFICATION CANDIDATES",
)

candidate_terms = (
    "planning_certification",
    "planning certification",
    "phase 4.6",
    "phase_4_6",
    "4.6",
)

candidate_hits = []

for path in ROOT.rglob("*.py"):

    parts = set(path.parts)

    if (
        ".venv" in parts
        or "node_modules" in parts
        or "__pycache__" in parts
        or ".git" in parts
    ):
        continue

    try:
        text = path.read_text(
            encoding="utf-8-sig"
        )

    except Exception:
        continue

    lower = text.lower()

    if any(
        term.lower() in lower
        for term in candidate_terms
    ):
        candidate_hits.append(
            path
        )

for path in sorted(
    set(candidate_hits)
):
    lines.append(
        str(
            path.relative_to(ROOT)
        )
    )

if not candidate_hits:
    lines.append(
        "NONE"
    )


# =============================================================================
# 4. Existing certification components
# =============================================================================

section(
    lines,
    "4. EXISTING COORDINATION CERTIFICATION COMPONENTS",
)

certification_files = []

coord_root = ROOT / (
    "backend/server/coordination"
)

if coord_root.exists():

    for path in coord_root.rglob(
        "*certification*.py"
    ):

        if "__pycache__" in path.parts:
            continue

        certification_files.append(
            path
        )

for path in sorted(
    certification_files
):

    lines.append("")
    lines.append(
        "-" * 108
    )

    lines.append(
        str(
            path.relative_to(ROOT)
        )
    )

    try:
        source = path.read_text(
            encoding="utf-8-sig"
        )

        tree = ast.parse(
            source
        )

    except Exception as exc:
        lines.append(
            f"PARSE ERROR: {exc}"
        )
        continue

    constants = []

    classes = []

    functions = []

    for node in tree.body:

        if isinstance(
            node,
            ast.Assign,
        ):

            for target in node.targets:

                if isinstance(
                    target,
                    ast.Name,
                ):
                    if (
                        "VERSION"
                        in target.id
                        or "SCHEMA"
                        in target.id
                        or "FIELD_COUNT"
                        in target.id
                    ):
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
                name = node.target.id

                if (
                    "VERSION" in name
                    or "SCHEMA" in name
                    or "FIELD_COUNT" in name
                ):
                    constants.append(
                        name
                    )

        elif isinstance(
            node,
            ast.ClassDef,
        ):
            classes.append(
                node.name
            )

        elif isinstance(
            node,
            ast.FunctionDef,
        ):
            if not node.name.startswith(
                "_"
            ):
                functions.append(
                    node.name
                )

    lines.append(
        "Constants: "
        + repr(
            constants
        )
    )

    lines.append(
        "Classes: "
        + repr(
            classes
        )
    )

    lines.append(
        "Public functions: "
        + repr(
            functions
        )
    )


if not certification_files:
    lines.append(
        "NONE"
    )


# =============================================================================
# 5. Phase 2.5 / 3.5 exact architecture references
# =============================================================================

section(
    lines,
    "5. PRIOR CERTIFICATION ARCHITECTURE REFERENCES",
)

prior_targets = (
    coord_root
    / "workflow_registration"
    / "registration_certification.py",

    coord_root
    / "workflow_lifecycle"
    / "lifecycle_certification.py",
)

for path in prior_targets:

    lines.append("")
    lines.append(
        "-" * 108
    )

    lines.append(
        f"Target: "
        f"{path.relative_to(ROOT)}"
    )

    if not path.exists():
        lines.append(
            "NOT FOUND"
        )
        continue

    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(
        source
    )

    for node in tree.body:

        if isinstance(
            node,
            ast.ClassDef,
        ):
            lines.append(
                f"class {node.name} "
                f"lines {node.lineno}-{node.end_lineno}"
            )

        elif isinstance(
            node,
            ast.FunctionDef,
        ):
            if not node.name.startswith(
                "_"
            ):
                lines.append(
                    f"function {node.name} "
                    f"lines {node.lineno}-{node.end_lineno}"
                )


# =============================================================================
# 6. Current package __init__ exports
# =============================================================================

section(
    lines,
    "6. DEPENDENCY_PLANNING PACKAGE EXPORTS",
)

init_file = PACKAGE / "__init__.py"

if init_file.exists():

    init_source = init_file.read_text(
        encoding="utf-8-sig"
    )

    lines.append(
        init_source
    )

else:
    lines.append(
        "__init__.py NOT FOUND"
    )


# =============================================================================
# 7. Verification/certification scripts already present
# =============================================================================

section(
    lines,
    "7. ROOT PHASE 4 VERIFICATION/CERTIFICATION SCRIPTS",
)

patterns = (
    "verify_*phase_4_*.py",
    "*phase_4_*verification*.txt",
    "*phase_4_*certification*.txt",
)

seen = set()

for pattern in patterns:

    for path in ROOT.glob(
        pattern
    ):

        if path in seen:
            continue

        seen.add(
            path
        )

        lines.append(
            str(
                path.relative_to(ROOT)
            )
        )


# =============================================================================
# 8. Static Phase 4 dependency chain
# =============================================================================

section(
    lines,
    "8. PHASE 4 STATIC IMPORT CHAIN",
)

for phase, path in canonical_files.items():

    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(
        source
    )

    imports = []

    for node in ast.walk(
        tree
    ):

        if isinstance(
            node,
            ast.ImportFrom,
        ):

            module = node.module or ""

            if (
                "coordination."
                "dependency_planning"
                in module
            ):
                imports.append(
                    module
                )

        elif isinstance(
            node,
            ast.Import,
        ):

            for alias in node.names:

                if (
                    "coordination."
                    "dependency_planning"
                    in alias.name
                ):
                    imports.append(
                        alias.name
                    )

    lines.append(
        f"{phase}: "
        + repr(
            sorted(
                set(
                    imports
                )
            )
        )
    )


# =============================================================================
# 9. Architecture ownership markers
# =============================================================================

section(
    lines,
    "9. PHASE 4 OWNERSHIP / DEFERRED AUTHORITY MARKERS",
)

markers = (
    "planning certification",
    "runtime",
    "dispatch",
    "persistence",
    "handoff",
    "advanced orchestration",
    "execution order",
    "immediate execution wave",
    "cycle",
    "runnable",
)

for phase, path in canonical_files.items():

    source = path.read_text(
        encoding="utf-8-sig"
    ).lower()

    lines.append("")
    lines.append(
        f"PHASE {phase}"
    )

    for marker in markers:

        lines.append(
            f"{marker}: "
            f"{marker in source}"
        )


# =============================================================================
# 10. Discovery conclusion scaffold
# =============================================================================

section(
    lines,
    "10. DISCOVERY QUESTIONS TO RESOLVE BEFORE INSTALLATION",
)

questions = (
    "Does a canonical Phase 4.6 production file already exist?",
    "What naming convention do Phase 2.5 and 3.5 use?",
    "Should 4.6 be a pure certification/evidence component?",
    "Should 4.6 own no graph/runnability/planning execution semantics?",
    "Should 4.6 certify exact frozen SHAs for 4.1-4.5?",
    "Should 4.6 produce a composite Phase 4 fingerprint?",
    "Should 4.6 return an immutable certification result?",
    "Should 4.6 remain Runtime/dispatch/persistence free?",
    "Should certification failures be fail-closed?",
    "Should 4.6 become the canonical Phase 4 freeze authority?",
)

for question in questions:
    lines.append(
        "- " + question
    )


REPORT.write_text(
    "\n".join(
        lines
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 108)
print("PHASE 4.6 PLANNING CERTIFICATION DISCOVERY SCAN COMPLETE")
print("=" * 108)
print(
    "REPORT:",
    REPORT.name,
)

for phase, path in canonical_files.items():
    print(
        f"{phase}:",
        sha256(path),
    )

print("=" * 108)
