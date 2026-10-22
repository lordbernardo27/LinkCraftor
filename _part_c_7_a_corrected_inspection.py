from __future__ import annotations

import ast
import hashlib
import json
import sys
import tokenize
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(sys.argv[1]).resolve()
REPORT = Path(sys.argv[2]).resolve()
SERVER = ROOT / "backend" / "server"

SCAN_ROOTS = (
    SERVER / "coordination",
    SERVER / "orchestration",
    SERVER / "runtime" / "universal_jobs",
    SERVER / "runtime" / "universal_queue",
    SERVER / "runtime" / "universal_worker",
)

EXPLICIT_SOURCES = (
    SERVER / "runtime" / "universal_runtime_worker_v1.py",
    SERVER / "runtime" / "universal_runtime_registration.py",
    SERVER / "runtime" / "runtime_registration_dependency_policy.py",
    SERVER / "runtime" / "runtime_registration_execution_policy.py",
    SERVER / "runtime" / "runtime_registration_gateway.py",
    SERVER / "runtime" / "runtime_application_lifecycle.py",
    SERVER / "jobs" / "universal_knowledge_orchestrator.py",
)

REQUIRED_BOUNDARIES = (
    SERVER / "coordination" / "dependency_planning" / "cycle_detection.py",
    SERVER / "coordination" / "dependency_planning" / "execution_planner.py",
    SERVER / "coordination" / "dependency_planning" / "planning_certification.py",
    SERVER / "coordination" / "runtime_integration" / "coordination_runtime_bridge.py",
    SERVER / "coordination" / "runtime_integration" / "runtime_completion_intake.py",
    SERVER / "coordination" / "runtime_integration" / "runtime_failure_intake.py",
    SERVER / "coordination" / "runtime_integration" / "workflow_job_correlation.py",
    SERVER / "coordination" / "stage_handoff" / "handoff_validation.py",
    SERVER / "coordination" / "stage_handoff" / "stage_result_processor.py",
    SERVER / "orchestration" / "queue.py",
    SERVER / "runtime" / "universal_runtime_worker_v1.py",
    SERVER / "runtime" / "universal_runtime_registration.py",
    SERVER / "runtime" / "runtime_registration_dependency_policy.py",
    SERVER / "runtime" / "universal_jobs" / "creation_engine.py",
)

EXCLUDED_DIRECTORY_NAMES = {
    ".git",
    ".venv",
    "__pycache__",
    "backups",
    "runtime_backups",
    "reports",
}

EXCLUDED_FILENAME_MARKERS = (
    "_before_",
    ".before_",
    "_backup",
    ".backup",
    ".candidate",
    "_candidate",
    "_old.",
    "_copy.",
)

CATEGORY_KEYWORDS = {
    "planning_and_dag": (
        "plan",
        "planner",
        "dependency_graph",
        "cycle",
        "acyclic",
        "manifest",
    ),
    "dependency_readiness": (
        "dependency",
        "readiness",
        "runnable",
        "handoff",
        "predecessor",
        "successor",
    ),
    "runtime_integration": (
        "runtime",
        "bridge",
        "dispatch",
        "worker",
        "submit",
        "enqueue",
        "claim",
        "lease",
    ),
    "state_and_recovery": (
        "complete",
        "failure",
        "failed",
        "cancel",
        "recover",
        "retry",
        "transition",
        "finaliz",
    ),
    "persistence_and_evidence": (
        "persist",
        "save",
        "load",
        "snapshot",
        "evidence",
        "certif",
        "correlat",
    ),
}


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def excluded(path: Path) -> bool:
    relative_parts = path.relative_to(ROOT).parts

    if any(
        part.lower() in EXCLUDED_DIRECTORY_NAMES
        for part in relative_parts[:-1]
    ):
        return True

    lowered_name = path.name.lower()

    return any(
        marker in lowered_name
        for marker in EXCLUDED_FILENAME_MARKERS
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def read_python_source(path: Path) -> str:
    # tokenize.open() is PEP-263 and UTF-8-BOM aware.
    with tokenize.open(path) as stream:
        return stream.read()


def dotted_call_name(node: ast.AST) -> str:
    parts: list[str] = []
    current = node

    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value

    if isinstance(current, ast.Name):
        parts.append(current.id)

    return ".".join(reversed(parts))


candidate_paths: set[Path] = set()

for scan_root in SCAN_ROOTS:
    if scan_root.is_dir():
        for candidate in scan_root.rglob("*.py"):
            if candidate.is_file() and not excluded(candidate):
                candidate_paths.add(candidate.resolve())

for candidate in EXPLICIT_SOURCES:
    if candidate.is_file() and not excluded(candidate):
        candidate_paths.add(candidate.resolve())

candidate_sources = sorted(
    candidate_paths,
    key=lambda item: relative(item).lower(),
)

if not candidate_sources:
    raise RuntimeError(
        "No canonical coordination sources were discovered."
    )

before_hashes = {
    path: sha256(path)
    for path in candidate_sources
}

syntax_failures: list[dict[str, object]] = []
source_inventory: list[dict[str, object]] = []
authority_records: list[dict[str, object]] = []
category_authorities: dict[str, set[str]] = {
    category: set()
    for category in CATEGORY_KEYWORDS
}

for path in candidate_sources:
    source = read_python_source(path)
    path_text = relative(path)

    try:
        tree = ast.parse(
            source,
            filename=str(path),
        )
    except SyntaxError as error:
        syntax_failures.append(
            {
                "path": path_text,
                "line": error.lineno,
                "offset": error.offset,
                "message": error.msg,
            }
        )
        source_inventory.append(
            {
                "path": path_text,
                "sha256": before_hashes[path],
                "syntax": "FAIL",
            }
        )
        continue

    declarations: list[str] = []
    calls: list[str] = []

    for node in ast.walk(tree):
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
            ),
        ):
            identity = f"{path_text}:{node.name}"
            declarations.append(node.name)

            authority_records.append(
                {
                    "identity": identity,
                    "line": node.lineno,
                    "kind": (
                        "class"
                        if isinstance(node, ast.ClassDef)
                        else "function"
                    ),
                }
            )

            lowered_identity = identity.lower()

            for category, keywords in CATEGORY_KEYWORDS.items():
                if any(
                    keyword in lowered_identity
                    for keyword in keywords
                ):
                    category_authorities[category].add(identity)

        elif isinstance(node, ast.Call):
            name = dotted_call_name(node.func)

            if name:
                calls.append(name)

                lowered_call = name.lower()
                call_identity = f"{path_text}:{name}"

                for category, keywords in CATEGORY_KEYWORDS.items():
                    if any(
                        keyword in lowered_call
                        for keyword in keywords
                    ):
                        category_authorities[category].add(
                            call_identity
                        )

    source_inventory.append(
        {
            "path": path_text,
            "sha256": before_hashes[path],
            "syntax": "PASS",
            "declaration_count": len(declarations),
            "call_count": len(calls),
        }
    )

missing_boundaries = [
    relative(path)
    for path in REQUIRED_BOUNDARIES
    if not path.is_file()
]

boundary_evidence = {
    relative(path): {
        "exists": path.is_file(),
        "included": path.resolve() in candidate_paths
        if path.is_file()
        else False,
    }
    for path in REQUIRED_BOUNDARIES
}

after_hashes = {
    path: sha256(path)
    for path in candidate_sources
}

changed_sources = [
    relative(path)
    for path in candidate_sources
    if before_hashes[path] != after_hashes[path]
]

category_summary = {
    category: {
        "authority_count": len(authorities),
        "authorities": sorted(authorities),
    }
    for category, authorities in category_authorities.items()
}

checks = {
    "canonical_sources_discovered": bool(candidate_sources),
    "backup_directories_excluded": not any(
        "backups" in {
            part.lower()
            for part in path.relative_to(ROOT).parts
        }
        for path in candidate_sources
    ),
    "before_snapshots_excluded": not any(
        "_before_" in path.name.lower()
        or ".before_" in path.name.lower()
        for path in candidate_sources
    ),
    "all_canonical_sources_pass_syntax": (
        not syntax_failures
    ),
    "all_required_boundaries_exist": (
        not missing_boundaries
    ),
    "planning_authority_discovered": bool(
        category_authorities["planning_and_dag"]
    ),
    "dependency_authority_discovered": bool(
        category_authorities["dependency_readiness"]
    ),
    "runtime_integration_discovered": bool(
        category_authorities["runtime_integration"]
    ),
    "state_and_recovery_discovered": bool(
        category_authorities["state_and_recovery"]
    ),
    "persistence_and_evidence_discovered": bool(
        category_authorities["persistence_and_evidence"]
    ),
    "production_sources_unchanged": (
        not changed_sources
    ),
}

complete = all(checks.values())
status = "COMPLETE" if complete else "NOT_COMPLETE"

report_text = f"""\
LINKCRAFTER UNIVERSAL COORDINATION
PART C 7-A CORRECTED CANONICAL COORDINATION AUTHORITY INSPECTION

Generated: {datetime.now(timezone.utc).isoformat()}
Mode: READ-ONLY TARGETED CLOSURE
Production source changes: NONE
Runtime registrations created: NO
Registry persistence executed: NO
Universal jobs created: NO
Queue claims executed: NO
Handlers executed: NO
Live network requests executed: NO
INSPECTION STATUS: {status}

==============================================================================================================
CORRECTED DECISION
==============================================================================================================
The original broad inspection included backup directories and historical
_before_ source snapshots. It also decoded a valid UTF-8 BOM as an AST
syntax failure.

This corrected closure:
- scans canonical production coordination and runtime boundaries only;
- excludes backup, candidate and historical before-state snapshots;
- uses Python's encoding-aware source loader;
- performs syntax and AST inspection without importing or executing handlers;
- verifies that every inspected production source remains unchanged.

==============================================================================================================
RUNTIME VERIFICATION
==============================================================================================================
CHECKS:
{json.dumps(checks, indent=2, sort_keys=True)}

CANONICAL_SOURCE_COUNT:
{len(candidate_sources)}

AUTHORITY_COUNT:
{len(authority_records)}

SYNTAX_FAILURE_COUNT:
{len(syntax_failures)}

MISSING_BOUNDARY_COUNT:
{len(missing_boundaries)}

SYNTAX_FAILURES:
{json.dumps(syntax_failures, indent=2, sort_keys=True)}

MISSING_BOUNDARIES:
{json.dumps(missing_boundaries, indent=2)}

CHANGED_SOURCES:
{json.dumps(changed_sources, indent=2)}

==============================================================================================================
CANONICAL BOUNDARY EVIDENCE
==============================================================================================================
{json.dumps(boundary_evidence, indent=2, sort_keys=True)}

==============================================================================================================
AUTHORITY CATEGORY SUMMARY
==============================================================================================================
{json.dumps(category_summary, indent=2, sort_keys=True)}

==============================================================================================================
CANONICAL SOURCE INVENTORY
==============================================================================================================
{json.dumps(source_inventory, indent=2, sort_keys=True)}

==============================================================================================================
DECISION BOUNDARY
==============================================================================================================
7-A identifies and freezes the reusable production authorities.

It does not declare the complete Universal Coordination Framework
certified. Part C Step 7 remains in progress.

The discovered backend/server/coordination implementation must be reused
and certified. A second coordination framework must not be created.

Next:
Part C 7-B — certify and freeze the canonical universal coordination
contract exposed by the existing production coordination package.

==============================================================================================================
FINAL RESULT
==============================================================================================================
PART C 7-A {status}
"""

REPORT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT.write_text(
    report_text,
    encoding="utf-8",
    newline="\n",
)

print("=" * 108)
print("PART C 7-A CORRECTED CANONICAL INSPECTION")
print("=" * 108)

for name, passed in checks.items():
    print(
        f"{name.upper()}: "
        f"{'PASS' if passed else 'FAIL'}"
    )

print()
print(f"CANONICAL_SOURCE_COUNT={len(candidate_sources)}")
print(f"AUTHORITY_COUNT={len(authority_records)}")
print(f"SYNTAX_FAILURE_COUNT={len(syntax_failures)}")
print(f"MISSING_BOUNDARY_COUNT={len(missing_boundaries)}")
print(f"PRODUCTION_SOURCE_CHANGES={len(changed_sources)}")
print(f"REPORT={REPORT}")
print(f"PART_C_7_A_STATUS={status}")

if not complete:
    raise SystemExit(1)