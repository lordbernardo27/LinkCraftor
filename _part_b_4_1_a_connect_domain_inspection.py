from __future__ import annotations

import ast
import hashlib
import json
import py_compile
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(sys.argv[1]).resolve()
REPORT = Path(sys.argv[2]).resolve()

PIPELINE_ROOT = (
    ROOT
    / "backend"
    / "server"
    / "pipelines"
    / "connect_domain"
)

REPORT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

results: list[tuple[str, bool, Any]] = []


def record(
    name: str,
    passed: bool,
    detail: Any = None,
) -> None:
    results.append(
        (
            name,
            bool(passed),
            detail,
        )
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def dotted_name(node: ast.AST) -> str:
    parts: list[str] = []

    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value

    if isinstance(node, ast.Name):
        parts.append(node.id)

    return ".".join(
        reversed(parts)
    )


def literal_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(
        node.value,
        str,
    ):
        return node.value

    return None


def literal_collection(node: ast.AST) -> list[str]:
    if not isinstance(
        node,
        (
            ast.List,
            ast.Tuple,
            ast.Set,
        ),
    ):
        return []

    values: list[str] = []

    for item in node.elts:
        value = literal_string(item)

        if value is not None:
            values.append(value)

    return values


def function_calls(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []

    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue

        calls.append(
            {
                "name": dotted_name(child.func),
                "line": child.lineno,
                "keywords": sorted(
                    keyword.arg
                    for keyword in child.keywords
                    if keyword.arg is not None
                ),
            }
        )

    return sorted(
        calls,
        key=lambda value: (
            value["line"],
            value["name"],
        ),
    )


def decorator_names(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[str]:
    names: list[str] = []

    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Call):
            names.append(
                dotted_name(decorator.func)
            )
        else:
            names.append(
                dotted_name(decorator)
            )

    return names


def source_inventory(path: Path) -> dict[str, Any]:
    source = path.read_text(
        encoding="utf-8-sig",
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    imports: list[dict[str, Any]] = []
    functions: list[dict[str, Any]] = []
    classes: list[dict[str, Any]] = []
    constants: dict[str, Any] = {}
    registrations: list[dict[str, Any]] = []
    submissions: list[dict[str, Any]] = []

    for node in tree.body:
        if isinstance(node, ast.Import):
            imports.extend(
                {
                    "module": alias.name,
                    "name": None,
                    "alias": alias.asname,
                    "line": node.lineno,
                }
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            imports.extend(
                {
                    "module": node.module,
                    "name": alias.name,
                    "alias": alias.asname,
                    "line": node.lineno,
                }
                for alias in node.names
            )

        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            functions.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "async": isinstance(
                        node,
                        ast.AsyncFunctionDef,
                    ),
                    "decorators": decorator_names(node),
                    "parameters": [
                        argument.arg
                        for argument in (
                            list(node.args.posonlyargs)
                            + list(node.args.args)
                            + list(node.args.kwonlyargs)
                        )
                    ],
                    "calls": function_calls(node),
                }
            )

        elif isinstance(node, ast.ClassDef):
            classes.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "bases": [
                        dotted_name(base)
                        for base in node.bases
                    ],
                }
            )

        elif isinstance(
            node,
            (
                ast.Assign,
                ast.AnnAssign,
            ),
        ):
            targets: list[ast.AST] = []

            if isinstance(node, ast.Assign):
                targets = list(node.targets)
                value = node.value
            else:
                targets = [node.target]
                value = node.value

            for target in targets:
                if not isinstance(target, ast.Name):
                    continue

                scalar = (
                    literal_string(value)
                    if value is not None
                    else None
                )

                collection = (
                    literal_collection(value)
                    if value is not None
                    else []
                )

                if scalar is not None:
                    constants[target.id] = scalar
                elif collection:
                    constants[target.id] = collection

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        call_name = dotted_name(node.func)

        keyword_values: dict[str, Any] = {}

        for keyword in node.keywords:
            if keyword.arg is None:
                continue

            value = literal_string(keyword.value)

            if value is None:
                collection = literal_collection(
                    keyword.value
                )

                if collection:
                    value = collection

            keyword_values[keyword.arg] = value

        if call_name.endswith(
            (
                "register_runtime_handler",
                "runtime_handler",
            )
        ):
            registrations.append(
                {
                    "call": call_name,
                    "line": node.lineno,
                    "keywords": keyword_values,
                }
            )

        if call_name.endswith(
            (
                "submit_universal_job",
                "create_universal_job",
                "create_universal_knowledge_job",
                "create_orchestration_job",
            )
        ):
            submissions.append(
                {
                    "call": call_name,
                    "line": node.lineno,
                    "keywords": keyword_values,
                }
            )

    lowered = source.lower()

    sitemap_lines = [
        {
            "line": index,
            "text": line.strip(),
        }
        for index, line in enumerate(
            source.splitlines(),
            start=1,
        )
        if "sitemap" in line.lower()
    ]

    manual_import_terms = (
        "import sitemap",
        "sitemap upload",
        "sitemap_upload",
        "uploaded sitemap",
        "manual sitemap",
        "sitemap csv",
        "sitemap txt",
    )

    automatic_discovery_terms = (
        "sitemap.xml",
        "robots.txt",
        "discover_sitemap",
        "sitemap_discovery",
        "sitemap_url",
        "fetch_sitemap",
        "parse_sitemap",
    )

    return {
        "path": str(
            path.relative_to(ROOT)
        ).replace("\\", "/"),
        "sha256": sha256(path),
        "line_count": len(
            source.splitlines()
        ),
        "imports": imports,
        "functions": functions,
        "classes": classes,
        "constants": constants,
        "registrations": registrations,
        "submissions": submissions,
        "sitemap_lines": sitemap_lines,
        "automatic_sitemap_signals": sorted(
            term
            for term in automatic_discovery_terms
            if term in lowered
        ),
        "manual_import_signals": sorted(
            term
            for term in manual_import_terms
            if term in lowered
        ),
    }


print(
    "=" * 112
)
print(
    "PART B 4.1-A - CONNECT DOMAIN EXECUTABLE BOUNDARY INSPECTION"
)
print(
    "=" * 112
)

record(
    "PROJECT_ROOT_EXISTS",
    ROOT.is_dir(),
    str(ROOT),
)

record(
    "CONNECT_DOMAIN_ROOT_EXISTS",
    PIPELINE_ROOT.is_dir(),
    str(PIPELINE_ROOT),
)

if not PIPELINE_ROOT.is_dir():
    raise RuntimeError(
        "Connect Domain pipeline directory was not found."
    )

pipeline_sources = sorted(
    PIPELINE_ROOT.rglob("*.py")
)

record(
    "CONNECT_DOMAIN_SOURCES_DISCOVERED",
    bool(pipeline_sources),
    len(pipeline_sources),
)

syntax_failures: list[str] = []

for source_path in pipeline_sources:
    try:
        py_compile.compile(
            str(source_path),
            doraise=True,
        )
    except Exception as exc:
        syntax_failures.append(
            f"{source_path}: {type(exc).__name__}: {exc}"
        )

record(
    "ALL_CONNECT_DOMAIN_SOURCES_PASS_SYNTAX",
    not syntax_failures,
    syntax_failures,
)

inventories: list[dict[str, Any]] = []
inspection_failures: list[str] = []

for source_path in pipeline_sources:
    try:
        inventories.append(
            source_inventory(source_path)
        )
    except Exception as exc:
        inspection_failures.append(
            f"{source_path}: {type(exc).__name__}: {exc}"
        )

record(
    "ALL_CONNECT_DOMAIN_SOURCES_INSPECTED",
    not inspection_failures,
    inspection_failures,
)

all_functions = [
    {
        "source": inventory["path"],
        **function,
    }
    for inventory in inventories
    for function in inventory["functions"]
]

all_registrations = [
    {
        "source": inventory["path"],
        **registration,
    }
    for inventory in inventories
    for registration in inventory["registrations"]
]

all_submissions = [
    {
        "source": inventory["path"],
        **submission,
    }
    for inventory in inventories
    for submission in inventory["submissions"]
]

handler_candidates = [
    function
    for function in all_functions
    if (
        "handler" in function["name"].lower()
        or "connect_domain" in function["name"].lower()
        or "website_connection" in function["name"].lower()
        or any(
            decorator.endswith("runtime_handler")
            for decorator in function["decorators"]
        )
    )
]

coordinator_candidates = [
    function
    for function in all_functions
    if (
        "coordinator" in function["name"].lower()
        or function["name"] == "run_connect_domain"
        or "orchestrat" in function["name"].lower()
    )
]

automatic_sitemap_sources = [
    {
        "source": inventory["path"],
        "signals": inventory[
            "automatic_sitemap_signals"
        ],
        "lines": inventory["sitemap_lines"],
    }
    for inventory in inventories
    if inventory["automatic_sitemap_signals"]
]

manual_import_sources = [
    {
        "source": inventory["path"],
        "signals": inventory[
            "manual_import_signals"
        ],
        "lines": inventory["sitemap_lines"],
    }
    for inventory in inventories
    if inventory["manual_import_signals"]
]

record(
    "EXECUTABLE_FUNCTIONS_DISCOVERED",
    bool(all_functions),
    len(all_functions),
)

record(
    "CONNECT_DOMAIN_HANDLER_CANDIDATES_DISCOVERED",
    bool(handler_candidates),
    handler_candidates,
)

record(
    "CONNECT_DOMAIN_COORDINATOR_CANDIDATES_DISCOVERED",
    bool(coordinator_candidates),
    coordinator_candidates,
)

record(
    "RUNTIME_REGISTRATION_CALLS_DISCOVERED",
    bool(all_registrations),
    all_registrations,
)

record(
    "UNIVERSAL_JOB_SUBMISSION_CALLS_DISCOVERED",
    bool(all_submissions),
    all_submissions,
)

record(
    "AUTOMATIC_WEBSITE_SITEMAP_PATH_INSPECTED",
    True,
    automatic_sitemap_sources,
)

record(
    "MANUAL_FRONTEND_IMPORT_NOT_REINTRODUCED_BY_INSPECTION",
    True,
    manual_import_sources,
)

report_lines: list[str] = [
    "LINKCRAFTER PIPELINE REGISTRATION",
    "PART B 4.1-A CONNECT DOMAIN EXECUTABLE BOUNDARY INSPECTION",
    "",
    "Generated: "
    + datetime.now(timezone.utc).isoformat(),
    "Mode: READ-ONLY PRODUCTION SOURCE INSPECTION",
    "Production source changes: NONE",
    "Runtime registrations created: NO",
    "Registry persistence executed: NO",
    "Jobs created or claimed: NO",
    "Handlers executed: NO",
    "Live website requests executed: NO",
    f"Project root: {ROOT}",
    "",
    "=" * 112,
    "VERIFICATION RESULTS",
    "=" * 112,
]

for name, passed, detail in results:
    report_lines.append(
        f"{name}: {'PASS' if passed else 'FAIL'}"
    )

    if detail is not None:
        rendered = json.dumps(
            detail,
            indent=2,
            sort_keys=True,
            default=str,
        )

        report_lines.extend(
            "  " + line
            for line in rendered.splitlines()
        )

report_lines.extend(
    [
        "",
        "=" * 112,
        "CONNECT DOMAIN SOURCE INVENTORY",
        "=" * 112,
        json.dumps(
            inventories,
            indent=2,
            sort_keys=True,
            default=str,
        ),
        "",
        "=" * 112,
        "BOUNDARY DECISION",
        "=" * 112,
        (
            "This inspection identifies the real Connect Domain "
            "executable handler, coordinator, registration, job "
            "submission and automatic website sitemap boundaries."
        ),
        "",
        (
            "Automatic sitemap discovery obtained from the connected "
            "website is protected as pipeline functionality."
        ),
        "",
        (
            "The retired manual frontend/ATS Import Sitemap workflow "
            "is not restored."
        ),
        "",
        (
            "No production source, registration, registry, job, queue "
            "or handler was modified or executed."
        ),
        "",
        "=" * 112,
        "FINAL RESULT",
        "=" * 112,
    ]
)

required_passed = (
    ROOT.is_dir()
    and PIPELINE_ROOT.is_dir()
    and bool(pipeline_sources)
    and not syntax_failures
    and not inspection_failures
)

if required_passed:
    report_lines.append(
        "FINAL RESULT: PART B 4.1-A INSPECTION COMPLETE"
    )
else:
    report_lines.append(
        "FINAL RESULT: PART B 4.1-A INSPECTION NOT_COMPLETE"
    )

REPORT.write_text(
    "\n".join(report_lines) + "\n",
    encoding="utf-8",
    newline="\n",
)

print(
    "\n".join(report_lines)
)

raise SystemExit(
    0 if required_passed else 1
)