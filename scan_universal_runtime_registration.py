from __future__ import annotations

import ast
import inspect
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent

BACKEND_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
)

ORCHESTRATOR_PATH = (
    BACKEND_ROOT
    / "jobs"
    / "universal_knowledge_orchestrator.py"
)

WORKER_PATH = (
    BACKEND_ROOT
    / "workers"
    / "universal_knowledge_worker.py"
)

RUNTIME_PATH = (
    BACKEND_ROOT
    / "runtime"
    / "universal_runtime_infrastructure.py"
)

REPORT_ROOT = (
    BACKEND_ROOT
    / "data"
    / "runtime"
    / "universal_runtime_registration_scan"
)

REPORT_PATH = (
    REPORT_ROOT
    / "universal_runtime_registration_scan.json"
)

EXCLUDED_DIRECTORY_NAMES = {
    "__pycache__",
    "data",
    "backups",
    "runtime_backups",
    "_quarantine",
    ".venv",
    "node_modules",
}

WEBSITE_INTEGRITY_JOB_TYPES = {
    "website_article_structure_validation",
    "website_article_component_validation",
    "website_article_corruption_truncation",
    "website_integrity_report_generation",
    "website_article_quarantine",
    "website_article_integrity_certification",
}

REGISTRATION_NAME_PATTERN = re.compile(
    r"(register|registration|registry|handler|dispatcher|dispatch)",
    flags=re.IGNORECASE,
)

GENERIC_REGISTER_FUNCTION_PATTERN = re.compile(
    r"register.*(job|handler|stage|pipeline|runtime)"
    r"|"
    r"(job|handler|stage|pipeline|runtime).*register",
    flags=re.IGNORECASE,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def relative(path: Path) -> str:
    try:
        return path.relative_to(
            PROJECT_ROOT
        ).as_posix()
    except ValueError:
        return str(path)


def active_python_files() -> list[Path]:
    paths: list[Path] = []

    for path in BACKEND_ROOT.rglob("*.py"):
        relative_parts = path.relative_to(
            BACKEND_ROOT
        ).parts

        if any(
            part in EXCLUDED_DIRECTORY_NAMES
            for part in relative_parts
        ):
            continue

        paths.append(path)

    return sorted(paths)


def read_source(path: Path) -> str:
    return path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )


def parse_source(path: Path) -> tuple[str, ast.Module]:
    source = read_source(path)

    tree = ast.parse(
        source,
        filename=str(path),
    )

    return source, tree


def literal_string_values(
    node: ast.AST,
) -> list[str]:
    if not isinstance(
        node,
        (
            ast.Set,
            ast.List,
            ast.Tuple,
        ),
    ):
        return []

    values: list[str] = []

    for element in node.elts:
        if (
            isinstance(element, ast.Constant)
            and isinstance(element.value, str)
        ):
            values.append(element.value)

    return values


def assignment_names(
    node: ast.Assign | ast.AnnAssign,
) -> list[str]:
    targets: list[ast.AST]

    if isinstance(node, ast.Assign):
        targets = list(node.targets)
    else:
        targets = [node.target]

    names: list[str] = []

    for target in targets:
        if isinstance(target, ast.Name):
            names.append(target.id)

    return names


def function_signature_from_ast(
    source: str,
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> str:
    segment = ast.get_source_segment(
        source,
        node,
    )

    if not segment:
        return node.name

    first_line = segment.splitlines()[0]

    if first_line.rstrip().endswith(":"):
        return first_line.rstrip()[:-1]

    lines = segment.splitlines()
    signature_lines: list[str] = []

    for line in lines:
        signature_lines.append(line)

        if line.rstrip().endswith("):"):
            break

    return "\n".join(signature_lines)


def inspect_orchestrator() -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": relative(ORCHESTRATOR_PATH),
        "exists": ORCHESTRATOR_PATH.is_file(),
        "syntax_valid": False,
        "supported_job_types_found": False,
        "supported_job_types": [],
        "creator_found": False,
        "creator_signature": None,
        "creator_accepts_pipeline": False,
        "creator_accepts_stage": False,
        "creator_accepts_enqueue": False,
        "creator_rejects_unsupported_job_types": False,
        "generic_registration_functions": [],
        "registry_assignments": [],
    }

    if not ORCHESTRATOR_PATH.is_file():
        return result

    source, tree = parse_source(
        ORCHESTRATOR_PATH
    )

    result["syntax_valid"] = True

    for node in tree.body:
        if isinstance(
            node,
            (
                ast.Assign,
                ast.AnnAssign,
            ),
        ):
            names = assignment_names(node)

            value_node = node.value

            for name in names:
                if name == "SUPPORTED_JOB_TYPES":
                    result[
                        "supported_job_types_found"
                    ] = True

                    result[
                        "supported_job_types"
                    ] = sorted(
                        literal_string_values(
                            value_node
                        )
                    )

                if REGISTRATION_NAME_PATTERN.search(name):
                    result[
                        "registry_assignments"
                    ].append(
                        {
                            "name": name,
                            "line": node.lineno,
                            "value_type": (
                                type(value_node).__name__
                            ),
                        }
                    )

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            if node.name == "create_universal_knowledge_job":
                result["creator_found"] = True
                result["creator_signature"] = (
                    function_signature_from_ast(
                        source,
                        node,
                    )
                )

                argument_names = {
                    argument.arg
                    for argument in (
                        list(node.args.args)
                        + list(node.args.kwonlyargs)
                    )
                }

                result[
                    "creator_accepts_pipeline"
                ] = "pipeline" in argument_names

                result[
                    "creator_accepts_stage"
                ] = "stage" in argument_names

                result[
                    "creator_accepts_enqueue"
                ] = "enqueue" in argument_names

                function_source = (
                    ast.get_source_segment(
                        source,
                        node,
                    )
                    or ""
                )

                result[
                    "creator_rejects_unsupported_job_types"
                ] = (
                    "SUPPORTED_JOB_TYPES"
                    in function_source
                    and "Unsupported"
                    in function_source
                )

            if GENERIC_REGISTER_FUNCTION_PATTERN.search(
                node.name
            ):
                result[
                    "generic_registration_functions"
                ].append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "signature": (
                            function_signature_from_ast(
                                source,
                                node,
                            )
                        ),
                    }
                )

    return result


def inspect_worker() -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": relative(WORKER_PATH),
        "exists": WORKER_PATH.is_file(),
        "syntax_valid": False,
        "executor_found": False,
        "hardcoded_job_type_branch_count": 0,
        "hardcoded_job_type_branches": [],
        "handler_registry_assignments": [],
        "generic_registration_functions": [],
        "mapping_dispatch_detected": False,
    }

    if not WORKER_PATH.is_file():
        return result

    source, tree = parse_source(
        WORKER_PATH
    )

    result["syntax_valid"] = True

    hardcoded_patterns = [
        re.compile(
            r"\bjob_type\s*==\s*[\"']([^\"']+)[\"']"
        ),
        re.compile(
            r"\bjob_type\s+in\s+\{([^}]+)\}",
            flags=re.DOTALL,
        ),
    ]

    hardcoded_values: list[str] = []

    for pattern in hardcoded_patterns:
        for match in pattern.finditer(source):
            matched_text = match.group(0)

            hardcoded_values.append(
                " ".join(
                    matched_text.split()
                )
            )

    result[
        "hardcoded_job_type_branches"
    ] = hardcoded_values

    result[
        "hardcoded_job_type_branch_count"
    ] = len(hardcoded_values)

    for node in tree.body:
        if isinstance(
            node,
            (
                ast.Assign,
                ast.AnnAssign,
            ),
        ):
            names = assignment_names(node)
            value_node = node.value

            for name in names:
                uppercase_name = name.upper()

                if (
                    "HANDLER" in uppercase_name
                    or "DISPATCH" in uppercase_name
                    or "REGISTRY" in uppercase_name
                    or "ROUTE" in uppercase_name
                ):
                    result[
                        "handler_registry_assignments"
                    ].append(
                        {
                            "name": name,
                            "line": node.lineno,
                            "value_type": (
                                type(value_node).__name__
                            ),
                            "is_mapping": isinstance(
                                value_node,
                                ast.Dict,
                            ),
                        }
                    )

                    if isinstance(
                        value_node,
                        ast.Dict,
                    ):
                        result[
                            "mapping_dispatch_detected"
                        ] = True

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            if node.name == "execute_universal_knowledge_job_v1":
                result["executor_found"] = True

            if GENERIC_REGISTER_FUNCTION_PATTERN.search(
                node.name
            ):
                result[
                    "generic_registration_functions"
                ].append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "signature": (
                            function_signature_from_ast(
                                source,
                                node,
                            )
                        ),
                    }
                )

    return result


def inspect_runtime_modules(
    paths: list[Path],
) -> dict[str, Any]:
    generic_registration_functions: list[
        dict[str, Any]
    ] = []

    registry_assignments: list[
        dict[str, Any]
    ] = []

    syntax_errors: list[
        dict[str, Any]
    ] = []

    candidate_files: set[str] = set()

    for path in paths:
        source = read_source(path)

        if not REGISTRATION_NAME_PATTERN.search(source):
            continue

        candidate_files.add(
            relative(path)
        )

        try:
            tree = ast.parse(
                source,
                filename=str(path),
            )
        except SyntaxError as exc:
            syntax_errors.append(
                {
                    "path": relative(path),
                    "line": exc.lineno,
                    "error": str(exc),
                }
            )
            continue

        for node in tree.body:
            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            ):
                if GENERIC_REGISTER_FUNCTION_PATTERN.search(
                    node.name
                ):
                    generic_registration_functions.append(
                        {
                            "path": relative(path),
                            "name": node.name,
                            "line": node.lineno,
                            "signature": (
                                function_signature_from_ast(
                                    source,
                                    node,
                                )
                            ),
                        }
                    )

            if isinstance(
                node,
                (
                    ast.Assign,
                    ast.AnnAssign,
                ),
            ):
                for name in assignment_names(node):
                    uppercase_name = name.upper()

                    if (
                        "REGISTRY" in uppercase_name
                        or "HANDLER" in uppercase_name
                        or "DISPATCH" in uppercase_name
                    ):
                        registry_assignments.append(
                            {
                                "path": relative(path),
                                "name": name,
                                "line": node.lineno,
                                "value_type": (
                                    type(node.value).__name__
                                ),
                                "is_mapping": isinstance(
                                    node.value,
                                    ast.Dict,
                                ),
                            }
                        )

    return {
        "candidate_file_count": len(
            candidate_files
        ),
        "candidate_files": sorted(
            candidate_files
        ),
        "generic_registration_functions": (
            generic_registration_functions
        ),
        "registry_assignments": (
            registry_assignments
        ),
        "syntax_errors": syntax_errors,
    }


def classify(
    orchestrator: dict[str, Any],
    worker: dict[str, Any],
    runtime_scan: dict[str, Any],
) -> tuple[str, list[str]]:
    reasons: list[str] = []

    supported_job_types = set(
        orchestrator.get(
            "supported_job_types",
            [],
        )
    )

    basic_static_registration = all(
        (
            orchestrator.get(
                "supported_job_types_found"
            ),
            orchestrator.get(
                "creator_found"
            ),
            orchestrator.get(
                "creator_accepts_pipeline"
            ),
            orchestrator.get(
                "creator_accepts_stage"
            ),
            orchestrator.get(
                "creator_rejects_unsupported_job_types"
            ),
        )
    )

    generic_functions = [
        *orchestrator.get(
            "generic_registration_functions",
            [],
        ),
        *worker.get(
            "generic_registration_functions",
            [],
        ),
        *runtime_scan.get(
            "generic_registration_functions",
            [],
        ),
    ]

    mapping_registries = [
        record
        for record in (
            [
                *orchestrator.get(
                    "registry_assignments",
                    [],
                ),
                *worker.get(
                    "handler_registry_assignments",
                    [],
                ),
                *runtime_scan.get(
                    "registry_assignments",
                    [],
                ),
            ]
        )
        if record.get("is_mapping")
    ]

    reusable_registration = bool(
        generic_functions
        and mapping_registries
        and worker.get(
            "mapping_dispatch_detected"
        )
    )

    if reusable_registration:
        decision = (
            "FORMAL_REUSABLE_UNIVERSAL_RUNTIME_"
            "REGISTRATION_EXISTS"
        )

        reasons.append(
            "Generic registration functions were found."
        )

        reasons.append(
            "A mapping-based handler or dispatch registry was found."
        )

        reasons.append(
            "The universal worker appears to use registry-driven dispatch."
        )

    elif basic_static_registration:
        decision = (
            "BASIC_STATIC_RUNTIME_REGISTRATION_EXISTS_"
            "FORMAL_REUSABLE_REGISTRY_NOT_CONFIRMED"
        )

        reasons.append(
            "SUPPORTED_JOB_TYPES exists."
        )

        reasons.append(
            "create_universal_knowledge_job accepts pipeline and stage."
        )

        reasons.append(
            "Unsupported job types are rejected."
        )

        if worker.get(
            "hardcoded_job_type_branch_count",
            0,
        ) > 0:
            reasons.append(
                "The worker still contains hard-coded job_type branches."
            )

        if not generic_functions:
            reasons.append(
                "No generic register-handler/register-stage API was found."
            )

        if not mapping_registries:
            reasons.append(
                "No confirmed mapping-based universal handler registry "
                "was found."
            )

    else:
        decision = (
            "UNIVERSAL_RUNTIME_REGISTRATION_NOT_FOUND"
        )

        reasons.append(
            "The required static or reusable registration components "
            "were not found."
        )

    if "udare_reconstruction" in supported_job_types:
        reasons.append(
            "udare_reconstruction is already registered as a "
            "supported universal job type."
        )

    integrity_registered = sorted(
        WEBSITE_INTEGRITY_JOB_TYPES
        & supported_job_types
    )

    if integrity_registered:
        reasons.append(
            "Some Website Article Integrity job types are already "
            "registered."
        )
    else:
        reasons.append(
            "No Website Article Integrity job types were found in "
            "SUPPORTED_JOB_TYPES."
        )

    return decision, reasons


def main() -> int:
    print()
    print("=" * 86)
    print(
        "UNIVERSAL RUNTIME REGISTRATION — READ-ONLY SOURCE SCAN"
    )
    print("=" * 86)

    required_files = (
        ORCHESTRATOR_PATH,
        WORKER_PATH,
        RUNTIME_PATH,
    )

    missing_files = [
        relative(path)
        for path in required_files
        if not path.is_file()
    ]

    if missing_files:
        print()
        print("SCAN RESULT: BLOCKED")
        print("Required runtime files are missing:")

        for path in missing_files:
            print(f"  - {path}")

        return 1

    paths = active_python_files()

    syntax_errors: list[dict[str, Any]] = []

    for path in paths:
        try:
            ast.parse(
                read_source(path),
                filename=str(path),
            )
        except SyntaxError as exc:
            syntax_errors.append(
                {
                    "path": relative(path),
                    "line": exc.lineno,
                    "error": str(exc),
                }
            )

    orchestrator = inspect_orchestrator()
    worker = inspect_worker()
    runtime_scan = inspect_runtime_modules(
        paths
    )

    decision, reasons = classify(
        orchestrator,
        worker,
        runtime_scan,
    )

    supported_job_types = (
        orchestrator.get(
            "supported_job_types",
            [],
        )
    )

    registered_integrity_types = sorted(
        set(supported_job_types)
        & WEBSITE_INTEGRITY_JOB_TYPES
    )

    missing_integrity_types = sorted(
        WEBSITE_INTEGRITY_JOB_TYPES
        - set(supported_job_types)
    )

    report: dict[str, Any] = {
        "schema_version": (
            "universal_runtime_registration_scan_v1"
        ),
        "generated_at": utc_now(),
        "project_root": str(PROJECT_ROOT),
        "scan_mode": "READ_ONLY_SOURCE_SCAN",
        "python_files_scanned": len(paths),
        "syntax_error_count": len(
            syntax_errors
        ),
        "syntax_errors": syntax_errors,
        "decision": decision,
        "decision_reasons": reasons,
        "orchestrator": orchestrator,
        "worker": worker,
        "runtime_registration_candidates": runtime_scan,
        "website_article_integrity": {
            "required_job_types": sorted(
                WEBSITE_INTEGRITY_JOB_TYPES
            ),
            "registered_job_types": (
                registered_integrity_types
            ),
            "missing_job_types": (
                missing_integrity_types
            ),
            "fully_registered": (
                not missing_integrity_types
            ),
        },
        "source_files_modified": [],
        "important_distinction": {
            "basic_static_registration": (
                "A supported-job-type allow-list plus pipeline/stage "
                "fields in the universal job creator."
            ),
            "formal_reusable_registration": (
                "A generic API that registers pipeline stages and "
                "handler callables into a mapping used directly by "
                "the universal worker dispatcher."
            ),
        },
    }

    REPORT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print()
    print(f"Python files scanned:                 {len(paths)}")
    print(
        f"Syntax errors found:                 "
        f"{len(syntax_errors)}"
    )
    print(
        f"SUPPORTED_JOB_TYPES found:           "
        f"{orchestrator.get('supported_job_types_found')}"
    )
    print(
        f"Supported job-type count:            "
        f"{len(supported_job_types)}"
    )
    print(
        f"Universal job creator found:         "
        f"{orchestrator.get('creator_found')}"
    )
    print(
        f"Creator accepts pipeline:            "
        f"{orchestrator.get('creator_accepts_pipeline')}"
    )
    print(
        f"Creator accepts stage:               "
        f"{orchestrator.get('creator_accepts_stage')}"
    )
    print(
        f"Generic registration functions:      "
        f"{len(runtime_scan.get('generic_registration_functions', []))}"
    )
    print(
        f"Registry/handler assignments:        "
        f"{len(runtime_scan.get('registry_assignments', []))}"
    )
    print(
        f"Hard-coded worker dispatch branches: "
        f"{worker.get('hardcoded_job_type_branch_count')}"
    )
    print(
        f"UDARE job type registered:           "
        f"{'udare_reconstruction' in supported_job_types}"
    )
    print(
        f"Integrity job types registered:      "
        f"{len(registered_integrity_types)}"
    )
    print(
        f"Integrity job types missing:         "
        f"{len(missing_integrity_types)}"
    )

    if registered_integrity_types:
        print()
        print("REGISTERED WEBSITE INTEGRITY JOB TYPES")

        for job_type in registered_integrity_types:
            print(f"  - {job_type}")

    if missing_integrity_types:
        print()
        print("MISSING WEBSITE INTEGRITY JOB TYPES")

        for job_type in missing_integrity_types:
            print(f"  - {job_type}")

    if orchestrator.get(
        "generic_registration_functions"
    ):
        print()
        print("ORCHESTRATOR REGISTRATION FUNCTIONS")

        for item in orchestrator[
            "generic_registration_functions"
        ]:
            print(
                f"  - {item['name']} "
                f"(line {item['line']})"
            )

    if runtime_scan.get(
        "generic_registration_functions"
    ):
        print()
        print("GENERIC REGISTRATION FUNCTIONS")

        for item in runtime_scan[
            "generic_registration_functions"
        ]:
            print(
                f"  - {item['path']}:{item['line']} "
                f"{item['name']}"
            )

    if worker.get(
        "handler_registry_assignments"
    ):
        print()
        print("WORKER REGISTRY CANDIDATES")

        for item in worker[
            "handler_registry_assignments"
        ]:
            print(
                f"  - {item['name']} "
                f"(line {item['line']}, "
                f"type={item['value_type']})"
            )

    print()
    print("DECISION")
    print(f"  {decision}")

    print()
    print("REASONS")

    for reason in reasons:
        print(f"  - {reason}")

    print()
    print(f"Report: {REPORT_PATH}")
    print("Source files modified: 0")
    print("=" * 86)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
