from __future__ import annotations

import ast
import hashlib
import json
import py_compile
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path.cwd().resolve()

BACKEND_DIR = PROJECT_ROOT / "backend"
SERVER_DIR = BACKEND_DIR / "server"
RUNTIME_DIR = SERVER_DIR / "runtime"

TIMESTAMP = datetime.now(timezone.utc).strftime(
    "%Y%m%dT%H%M%SZ"
)

EVIDENCE_DIR = (
    SERVER_DIR
    / "data"
    / "runtime"
    / "uri_phase_1"
    / "1_1_10_to_1_1_15_combined_scan"
)

EVIDENCE_JSON = (
    EVIDENCE_DIR
    / f"combined_foundation_scan_{TIMESTAMP}.json"
)

EVIDENCE_TEXT = (
    EVIDENCE_DIR
    / f"combined_foundation_scan_{TIMESTAMP}.txt"
)


PHASE_1_EXPECTED_MODULES = {
    "1.1.1": "runtime_kernel.py",
    "1.1.2": "runtime_configuration.py",
    "1.1.3": "runtime_environment.py",
    "1.1.4": "runtime_service_registry.py",
    "1.1.5": "runtime_lifecycle.py",
    "1.1.6": "runtime_boot.py",
    "1.1.7": "runtime_shutdown.py",
    "1.1.8": "runtime_versioning.py",
    "1.1.9": "runtime_compatibility.py",
}


SCAN_COMPONENTS = {
    "1.1.10_runtime_feature_flags": {
        "title": "Runtime Feature Flags",
        "keywords": {
            "feature_flag",
            "feature flags",
            "flag_registry",
            "flag_evaluator",
            "rollout",
            "kill_switch",
            "kill switch",
            "percentage_rollout",
            "workspace_flag",
            "plan_flag",
            "environment_flag",
            "flag_override",
            "flag_snapshot",
        },
    },
    "1.1.11_runtime_capability_negotiation": {
        "title": "Runtime Capability Negotiation",
        "keywords": {
            "capability",
            "capabilities",
            "capability_manifest",
            "capability negotiation",
            "required_capabilities",
            "optional_capabilities",
            "supported_capabilities",
            "deprecated_capabilities",
            "protocol_version",
            "contract_version",
            "serialization_format",
        },
    },
    "1.1.12_runtime_persistence_interface": {
        "title": "Runtime Persistence Interface",
        "keywords": {
            "persistence",
            "repository",
            "transaction",
            "unit_of_work",
            "unit of work",
            "save",
            "load",
            "delete",
            "commit",
            "rollback",
            "atomic",
            "durable",
            "persistence_adapter",
        },
    },
    "1.1.13_runtime_state_store_abstraction": {
        "title": "Runtime State Store Abstraction",
        "keywords": {
            "state_store",
            "state store",
            "state_backend",
            "state backend",
            "state_repository",
            "compare_and_set",
            "compare-and-set",
            "revision",
            "generation",
            "snapshot",
            "state_key",
            "namespace",
            "optimistic",
            "concurrency token",
        },
    },
    "1.1.14_runtime_schema_management": {
        "title": "Runtime Schema Management",
        "keywords": {
            "schema",
            "schema_version",
            "migration",
            "migrate",
            "migration_plan",
            "schema_registry",
            "schema fingerprint",
            "schema_fingerprint",
            "upgrade",
            "downgrade",
            "compatibility",
            "contract schema",
        },
    },
    "1.1.15_runtime_foundation_certification": {
        "title": "Runtime Foundation Certification",
        "keywords": {
            "certification",
            "certificate",
            "acceptance criteria",
            "evidence",
            "foundation certification",
            "certification report",
            "certification status",
            "certified",
            "verification manifest",
            "build evidence",
        },
    },
}


ARCHITECTURAL_CONSTRUCTS = {
    "Protocol",
    "ABC",
    "ABCMeta",
    "abstractmethod",
    "dataclass",
    "Enum",
    "IntEnum",
    "StrEnum",
    "TypedDict",
    "NamedTuple",
}


BUSINESS_LOGIC_MARKERS = {
    "udare",
    "website_article",
    "article_validation",
    "semantic_link",
    "internal_link",
    "external_link",
    "uucd",
    "wuc",
    "uduc",
    "article_body",
    "keyword",
    "seo",
    "publishing",
}


def relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path.resolve())


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def safe_read(path: Path) -> str:
    try:
        return path.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )
    except OSError:
        return ""


def run_command(
    command: list[str],
) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        return {
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }
    except OSError as exc:
        return {
            "command": command,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
        }


def discover_python_files() -> list[Path]:
    discovered: set[Path] = set()

    if RUNTIME_DIR.exists():
        discovered.update(
            path
            for path in RUNTIME_DIR.rglob("*.py")
            if "__pycache__" not in path.parts
        )

    important_names = {
        "main.py",
        "config.py",
        "configuration.py",
        "settings.py",
        "state.py",
        "state_store.py",
        "persistence.py",
        "repository.py",
        "schemas.py",
        "schema.py",
        "migrations.py",
        "runtime.py",
        "runtime_registry.py",
        "runtime_jobs.py",
        "runtime_queue.py",
        "runtime_worker.py",
        "runtime_orchestrator.py",
    }

    relevant_name_markers = {
        "runtime",
        "state",
        "store",
        "persist",
        "repository",
        "schema",
        "migration",
        "config",
        "setting",
        "feature",
        "capability",
        "certif",
        "evidence",
    }

    if SERVER_DIR.exists():
        for path in SERVER_DIR.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue

            lowered_name = path.name.lower()

            if lowered_name in important_names:
                discovered.add(path)
                continue

            if any(
                marker in lowered_name
                for marker in relevant_name_markers
            ):
                discovered.add(path)

    for path in PROJECT_ROOT.glob(
        "build_uri_phase_1_*.py"
    ):
        discovered.add(path)

    for path in PROJECT_ROOT.glob(
        "verify_uri_phase_1_*.py"
    ):
        discovered.add(path)

    return sorted(
        discovered,
        key=lambda item: relative(item).lower(),
    )


def production_scope_files() -> list[Path]:
    protected: set[Path] = set()

    if RUNTIME_DIR.exists():
        protected.update(
            path
            for path in RUNTIME_DIR.rglob("*.py")
            if "__pycache__" not in path.parts
        )

    possible_main_files = {
        SERVER_DIR / "main.py",
        BACKEND_DIR / "main.py",
        PROJECT_ROOT / "main.py",
    }

    protected.update(
        path
        for path in possible_main_files
        if path.exists()
    )

    return sorted(
        protected,
        key=lambda item: relative(item).lower(),
    )


def snapshot_hashes(
    paths: list[Path],
) -> dict[str, str]:
    return {
        relative(path): sha256_file(path)
        for path in paths
        if path.exists() and path.is_file()
    }


def parse_python_file(
    path: Path,
) -> dict[str, Any]:
    text = safe_read(path)

    record: dict[str, Any] = {
        "path": relative(path),
        "size_bytes": (
            path.stat().st_size
            if path.exists()
            else 0
        ),
        "sha256": (
            sha256_file(path)
            if path.exists()
            else None
        ),
        "parse_status": "NOT_PARSED",
        "syntax_error": None,
        "classes": [],
        "functions": [],
        "async_functions": [],
        "imports": [],
        "decorators": [],
        "constructs": [],
        "business_logic_markers": [],
        "component_keyword_hits": {},
    }

    lowered = text.lower()

    record["business_logic_markers"] = sorted(
        marker
        for marker in BUSINESS_LOGIC_MARKERS
        if marker in lowered
    )

    for component_id, definition in SCAN_COMPONENTS.items():
        hits = sorted(
            keyword
            for keyword in definition["keywords"]
            if keyword.lower() in lowered
        )

        if hits:
            record["component_keyword_hits"][
                component_id
            ] = hits

    try:
        tree = ast.parse(
            text,
            filename=str(path),
        )
    except SyntaxError as exc:
        record["parse_status"] = "SYNTAX_ERROR"
        record["syntax_error"] = {
            "message": exc.msg,
            "line": exc.lineno,
            "offset": exc.offset,
        }
        return record

    record["parse_status"] = "PASS"

    imports: set[str] = set()
    decorators: set[str] = set()
    constructs: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            record["classes"].append(node.name)

            for base in node.bases:
                if isinstance(base, ast.Name):
                    constructs.add(base.id)
                elif isinstance(base, ast.Attribute):
                    constructs.add(base.attr)

            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name):
                    decorators.add(decorator.id)
                elif isinstance(
                    decorator,
                    ast.Attribute,
                ):
                    decorators.add(decorator.attr)

        elif isinstance(node, ast.FunctionDef):
            record["functions"].append(node.name)

            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name):
                    decorators.add(decorator.id)
                elif isinstance(
                    decorator,
                    ast.Attribute,
                ):
                    decorators.add(decorator.attr)

        elif isinstance(node, ast.AsyncFunctionDef):
            record["async_functions"].append(
                node.name
            )

        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""

            for alias in node.names:
                imports.add(
                    f"{module}.{alias.name}".strip(".")
                )

        elif isinstance(node, ast.Name):
            if node.id in ARCHITECTURAL_CONSTRUCTS:
                constructs.add(node.id)

        elif isinstance(node, ast.Attribute):
            if node.attr in ARCHITECTURAL_CONSTRUCTS:
                constructs.add(node.attr)

    record["classes"] = sorted(
        set(record["classes"])
    )
    record["functions"] = sorted(
        set(record["functions"])
    )
    record["async_functions"] = sorted(
        set(record["async_functions"])
    )
    record["imports"] = sorted(imports)
    record["decorators"] = sorted(decorators)
    record["constructs"] = sorted(
        construct
        for construct in constructs
        if construct in ARCHITECTURAL_CONSTRUCTS
    )

    return record


def compile_file(
    path: Path,
) -> dict[str, Any]:
    try:
        py_compile.compile(
            str(path),
            doraise=True,
        )

        return {
            "path": relative(path),
            "status": "PASS",
            "error": None,
        }
    except Exception as exc:
        return {
            "path": relative(path),
            "status": "FAIL",
            "error": (
                f"{type(exc).__name__}: {exc}"
            ),
        }


def phase_1_inventory() -> dict[str, Any]:
    inventory: dict[str, Any] = {}

    for item_id, filename in (
        PHASE_1_EXPECTED_MODULES.items()
    ):
        path = RUNTIME_DIR / filename

        inventory[item_id] = {
            "filename": filename,
            "path": relative(path),
            "exists": path.exists(),
            "sha256": (
                sha256_file(path)
                if path.exists()
                else None
            ),
        }

    return inventory


def summarize_components(
    file_records: list[dict[str, Any]],
) -> dict[str, Any]:
    summary: dict[str, Any] = {}

    for component_id, definition in (
        SCAN_COMPONENTS.items()
    ):
        matching_files = []

        for record in file_records:
            hits = record[
                "component_keyword_hits"
            ].get(component_id)

            if not hits:
                continue

            matching_files.append(
                {
                    "path": record["path"],
                    "keyword_hits": hits,
                    "classes": record["classes"],
                    "functions": record["functions"],
                    "constructs": record[
                        "constructs"
                    ],
                }
            )

        summary[component_id] = {
            "title": definition["title"],
            "matching_file_count": len(
                matching_files
            ),
            "matching_files": matching_files,
            "assessment": (
                "EXISTING_FOUNDATION_DETECTED"
                if matching_files
                else "NO_CLEAR_FOUNDATION_DETECTED"
            ),
        }

    return summary


def find_import_relationships(
    file_records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    relationships = []

    runtime_names = {
        path.stem
        for path in RUNTIME_DIR.glob("*.py")
    } if RUNTIME_DIR.exists() else set()

    for record in file_records:
        runtime_imports = sorted(
            imported
            for imported in record["imports"]
            if any(
                runtime_name in imported
                for runtime_name in runtime_names
            )
        )

        if runtime_imports:
            relationships.append(
                {
                    "path": record["path"],
                    "runtime_imports": runtime_imports,
                }
            )

    return relationships


def build_risk_assessment(
    file_records: list[dict[str, Any]],
    component_summary: dict[str, Any],
) -> list[dict[str, str]]:
    risks: list[dict[str, str]] = []

    syntax_failures = [
        record["path"]
        for record in file_records
        if record["parse_status"] == "SYNTAX_ERROR"
    ]

    if syntax_failures:
        risks.append(
            {
                "severity": "HIGH",
                "risk": "Existing relevant Python files contain syntax errors.",
                "evidence": ", ".join(
                    syntax_failures
                ),
            }
        )

    runtime_business_logic = [
        {
            "path": record["path"],
            "markers": record[
                "business_logic_markers"
            ],
        }
        for record in file_records
        if (
            record["path"].replace("\\", "/").startswith(
                "backend/server/runtime/"
            )
            and record["business_logic_markers"]
        )
    ]

    if runtime_business_logic:
        risks.append(
            {
                "severity": "WARNING",
                "risk": (
                    "Possible pipeline-specific terminology "
                    "exists inside runtime modules."
                ),
                "evidence": json.dumps(
                    runtime_business_logic,
                    sort_keys=True,
                ),
            }
        )

    overlapping_files: dict[str, list[str]] = {}

    for record in file_records:
        matched_components = sorted(
            record["component_keyword_hits"]
        )

        if len(matched_components) >= 3:
            overlapping_files[record["path"]] = (
                matched_components
            )

    if overlapping_files:
        risks.append(
            {
                "severity": "INFORMATIONAL",
                "risk": (
                    "Some files contain concerns spanning "
                    "three or more remaining components. "
                    "The combined builder must preserve "
                    "clear contract boundaries."
                ),
                "evidence": json.dumps(
                    overlapping_files,
                    sort_keys=True,
                ),
            }
        )

    missing_foundations = [
        component_id
        for component_id, summary
        in component_summary.items()
        if (
            summary["assessment"]
            == "NO_CLEAR_FOUNDATION_DETECTED"
        )
    ]

    if missing_foundations:
        risks.append(
            {
                "severity": "INFORMATIONAL",
                "risk": (
                    "No obvious existing foundation was "
                    "detected for some components."
                ),
                "evidence": ", ".join(
                    missing_foundations
                ),
            }
        )

    if not risks:
        risks.append(
            {
                "severity": "NONE",
                "risk": (
                    "No immediate structural blocker was "
                    "detected by the static scan."
                ),
                "evidence": "Static scan completed.",
            }
        )

    return risks


def determine_recommended_actions(
    component_summary: dict[str, Any],
) -> dict[str, list[str]]:
    recommendations: dict[str, list[str]] = {}

    for component_id, summary in (
        component_summary.items()
    ):
        if (
            summary["assessment"]
            == "EXISTING_FOUNDATION_DETECTED"
        ):
            recommendations[component_id] = [
                "Review detected contracts for safe reuse.",
                "Avoid duplicating existing responsibilities.",
                "Strengthen incomplete contracts where required.",
                "Preserve backward compatibility.",
                "Add isolated and cross-component verification.",
            ]
        else:
            recommendations[component_id] = [
                "Create a new business-logic-agnostic runtime contract.",
                "Integrate with completed Phase 1 modules.",
                "Add immutable records and deterministic fingerprints where applicable.",
                "Add thread-safety and import-side-effect verification.",
                "Create persistent JSON and text evidence.",
            ]

    recommendations[
        "combined_build_strategy"
    ] = [
        "Use one transactional builder for 1.1.10 through 1.1.15.",
        "Back up every existing file before modification.",
        "Build each component in dependency order.",
        "Compile after each component is written.",
        "Run isolated verification for every checklist item.",
        "Run combined cross-component verification.",
        "Verify completed 1.1.1 through 1.1.9 files remain unchanged unless explicitly authorized.",
        "Roll back all files if any mandatory verification fails.",
        "Produce separate evidence sections for 1.1.10 through 1.1.15.",
        "Keep application boot integration status explicit.",
        "Do not certify Phase 1 unless all certification gates pass.",
    ]

    return recommendations


def text_report(
    report: dict[str, Any],
) -> str:
    lines: list[str] = []

    lines.append("=" * 78)
    lines.append("UNIVERSAL RUNTIME INFRASTRUCTURE")
    lines.append(
        "PHASE 1 — COMBINED PRE-BUILD SCAN"
    )
    lines.append(
        "1.1.10 THROUGH 1.1.15"
    )
    lines.append("=" * 78)
    lines.append("")

    lines.append(
        f"Project root: {report['project_root']}"
    )
    lines.append(
        f"Runtime dir:  {report['runtime_dir']}"
    )
    lines.append(
        f"Timestamp:    {report['timestamp_utc']}"
    )
    lines.append("")

    lines.append("FOUNDATION MODULE INVENTORY")
    lines.append("-" * 78)

    for item_id, record in (
        report["phase_1_inventory"].items()
    ):
        status = (
            "FOUND"
            if record["exists"]
            else "MISSING"
        )

        lines.append(
            f"{item_id:<8} {record['filename']:<36} {status}"
        )

    lines.append("")
    lines.append("STATIC AND COMPILATION SCAN")
    lines.append("-" * 78)
    lines.append(
        "Files scanned:        "
        f"{report['summary']['files_scanned']}"
    )
    lines.append(
        "AST parse PASS:       "
        f"{report['summary']['ast_pass']}"
    )
    lines.append(
        "AST parse FAIL:       "
        f"{report['summary']['ast_fail']}"
    )
    lines.append(
        "Compilation PASS:     "
        f"{report['summary']['compile_pass']}"
    )
    lines.append(
        "Compilation FAIL:     "
        f"{report['summary']['compile_fail']}"
    )
    lines.append("")

    lines.append("REMAINING COMPONENT FINDINGS")
    lines.append("-" * 78)

    for component_id, summary in (
        report["component_summary"].items()
    ):
        lines.append(
            f"{component_id}:"
        )
        lines.append(
            f"  Title:      {summary['title']}"
        )
        lines.append(
            f"  Assessment: {summary['assessment']}"
        )
        lines.append(
            "  Matching files: "
            f"{summary['matching_file_count']}"
        )

        for match in summary[
            "matching_files"
        ][:10]:
            lines.append(
                f"    - {match['path']}"
            )

    lines.append("")
    lines.append("RISK ASSESSMENT")
    lines.append("-" * 78)

    for risk in report["risks"]:
        lines.append(
            f"{risk['severity']}: {risk['risk']}"
        )
        lines.append(
            f"  Evidence: {risk['evidence']}"
        )

    lines.append("")
    lines.append("SOURCE-INTEGRITY CHECK")
    lines.append("-" * 78)
    lines.append(
        "Protected production files unchanged: "
        f"{report['source_integrity']['unchanged']}"
    )

    if report["source_integrity"][
        "changed_files"
    ]:
        for changed in report[
            "source_integrity"
        ]["changed_files"]:
            lines.append(
                f"  CHANGED: {changed}"
            )

    lines.append("")
    lines.append("SCAN RESULT")
    lines.append("-" * 78)
    lines.append(
        "READ-ONLY SOURCE SCAN: "
        f"{report['scan_status']}"
    )
    lines.append(
        "PRODUCTION SOURCE MODIFICATION: NONE"
    )
    lines.append(
        "COMBINED BUILDER GENERATION: PENDING SCAN REVIEW"
    )
    lines.append(
        "PHASE 1 CERTIFICATION: NOT CERTIFIED"
    )
    lines.append("")
    lines.append(
        f"Evidence JSON: {relative(EVIDENCE_JSON)}"
    )
    lines.append(
        f"Evidence text: {relative(EVIDENCE_TEXT)}"
    )

    return "\n".join(lines) + "\n"


def main() -> int:
    print("=" * 78)
    print("UNIVERSAL RUNTIME INFRASTRUCTURE")
    print("PHASE 1 — COMBINED PRE-BUILD SCAN")
    print("1.1.10 THROUGH 1.1.15")
    print("=" * 78)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Runtime dir:  {RUNTIME_DIR}")
    print()

    if not SERVER_DIR.exists():
        raise FileNotFoundError(
            f"Server directory does not exist: {SERVER_DIR}"
        )

    if not RUNTIME_DIR.exists():
        raise FileNotFoundError(
            f"Runtime directory does not exist: {RUNTIME_DIR}"
        )

    protected_files = production_scope_files()
    hashes_before = snapshot_hashes(
        protected_files
    )

    discovered_files = discover_python_files()

    file_records = [
        parse_python_file(path)
        for path in discovered_files
    ]

    compile_results = [
        compile_file(path)
        for path in discovered_files
    ]

    component_summary = summarize_components(
        file_records
    )

    inventory = phase_1_inventory()

    risks = build_risk_assessment(
        file_records,
        component_summary,
    )

    recommendations = determine_recommended_actions(
        component_summary
    )

    hashes_after = snapshot_hashes(
        protected_files
    )

    changed_files = sorted(
        path
        for path in (
            set(hashes_before)
            | set(hashes_after)
        )
        if (
            hashes_before.get(path)
            != hashes_after.get(path)
        )
    )

    ast_pass = sum(
        1
        for record in file_records
        if record["parse_status"] == "PASS"
    )

    ast_fail = sum(
        1
        for record in file_records
        if record["parse_status"] != "PASS"
    )

    compile_pass = sum(
        1
        for record in compile_results
        if record["status"] == "PASS"
    )

    compile_fail = sum(
        1
        for record in compile_results
        if record["status"] == "FAIL"
    )

    missing_completed_modules = [
        item_id
        for item_id, record
        in inventory.items()
        if not record["exists"]
    ]

    scan_status = (
        "PASS"
        if (
            ast_fail == 0
            and compile_fail == 0
            and not changed_files
            and not missing_completed_modules
        )
        else "PARTIAL"
    )

    git_status = run_command(
        ["git", "status", "--short"]
    )

    git_diff = run_command(
        ["git", "diff", "--name-only"]
    )

    report: dict[str, Any] = {
        "schema": (
            "linkcraftor.uri.phase1."
            "combined_scan.v1"
        ),
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "runtime_dir": str(RUNTIME_DIR),
        "scan_scope": [
            "1.1.10 Runtime Feature Flags",
            "1.1.11 Runtime Capability Negotiation",
            "1.1.12 Runtime Persistence Interface",
            "1.1.13 Runtime State Store Abstraction",
            "1.1.14 Runtime Schema Management",
            "1.1.15 Runtime Foundation Certification",
        ],
        "scan_status": scan_status,
        "phase_1_inventory": inventory,
        "missing_completed_modules": (
            missing_completed_modules
        ),
        "summary": {
            "files_scanned": len(
                discovered_files
            ),
            "ast_pass": ast_pass,
            "ast_fail": ast_fail,
            "compile_pass": compile_pass,
            "compile_fail": compile_fail,
        },
        "component_summary": component_summary,
        "file_records": file_records,
        "compile_results": compile_results,
        "runtime_import_relationships": (
            find_import_relationships(
                file_records
            )
        ),
        "risks": risks,
        "recommended_actions": recommendations,
        "source_integrity": {
            "protected_file_count": len(
                protected_files
            ),
            "unchanged": not changed_files,
            "changed_files": changed_files,
            "hashes_before": hashes_before,
            "hashes_after": hashes_after,
        },
        "git_status": git_status,
        "git_diff": git_diff,
        "production_data_modified": False,
        "production_source_intentionally_modified": False,
    }

    EVIDENCE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    EVIDENCE_JSON.write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    rendered_text = text_report(report)

    EVIDENCE_TEXT.write_text(
        rendered_text,
        encoding="utf-8",
        newline="\n",
    )

    print(rendered_text)

    if changed_files:
        print(
            "FAIL: Protected source files changed "
            "during the scan."
        )
        return 1

    if ast_fail or compile_fail:
        print(
            "PARTIAL: Existing relevant files "
            "contain parse or compilation failures."
        )
        return 2

    if missing_completed_modules:
        print(
            "PARTIAL: One or more completed Phase 1 "
            "foundation modules were not found."
        )
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
