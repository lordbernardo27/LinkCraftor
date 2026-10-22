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

BACKEND_ROOT = ROOT / "backend" / "server"

CONNECT_ROOT = (
    BACKEND_ROOT
    / "pipelines"
    / "connect_domain"
)

LINKING_COORDINATOR = (
    CONNECT_ROOT
    / "linking_target_pipeline"
    / "coordinator.py"
)

SITE_SOURCES_ROOT = (
    CONNECT_ROOT
    / "linking_target_pipeline"
    / "site_sources"
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

    print(
        f"{name}: {'PASS' if passed else 'FAIL'}"
    )

    if detail is not None:
        rendered = json.dumps(
            detail,
            indent=2,
            sort_keys=True,
            default=str,
        )

        for line in rendered.splitlines():
            print("  " + line)


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


def function_record(
    path: Path,
    source: str,
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> dict[str, Any]:
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

    return {
        "source": str(
            path.relative_to(ROOT)
        ).replace("\\", "/"),
        "name": node.name,
        "line": node.lineno,
        "end_line": getattr(
            node,
            "end_lineno",
            node.lineno,
        ),
        "async": isinstance(
            node,
            ast.AsyncFunctionDef,
        ),
        "parameters": [
            argument.arg
            for argument in (
                list(node.args.posonlyargs)
                + list(node.args.args)
                + list(node.args.kwonlyargs)
            )
        ],
        "calls": sorted(
            calls,
            key=lambda value: (
                value["line"],
                value["name"],
            ),
        ),
        "source_text": ast.get_source_segment(
            source,
            node,
        ),
    }


def import_records(
    tree: ast.Module,
) -> list[dict[str, Any]]:
    imports: list[dict[str, Any]] = []

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

    return imports


print("=" * 112)
print("PART B 4.2-A - SITE SOURCES BOUNDARY INSPECTION")
print("=" * 112)

record(
    "PROJECT_ROOT_EXISTS",
    ROOT.is_dir(),
    str(ROOT),
)

record(
    "BACKEND_ROOT_EXISTS",
    BACKEND_ROOT.is_dir(),
    str(BACKEND_ROOT),
)

record(
    "CONNECT_DOMAIN_ROOT_EXISTS",
    CONNECT_ROOT.is_dir(),
    str(CONNECT_ROOT),
)

record(
    "LINKING_COORDINATOR_EXISTS",
    LINKING_COORDINATOR.is_file(),
    str(LINKING_COORDINATOR),
)

if not LINKING_COORDINATOR.is_file():
    raise RuntimeError(
        "Linking Target coordinator was not found."
    )

py_compile.compile(
    str(LINKING_COORDINATOR),
    doraise=True,
)

record(
    "LINKING_COORDINATOR_SYNTAX",
    True,
)

linking_source = LINKING_COORDINATOR.read_text(
    encoding="utf-8-sig",
)

linking_tree = ast.parse(
    linking_source,
    filename=str(LINKING_COORDINATOR),
)

linking_imports = import_records(
    linking_tree
)

record(
    "LINKING_COORDINATOR_IMPORTS_DISCOVERED",
    bool(linking_imports),
    linking_imports,
)

linking_functions = [
    function_record(
        LINKING_COORDINATOR,
        linking_source,
        node,
    )
    for node in linking_tree.body
    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    )
]

run_functions = [
    function
    for function in linking_functions
    if function["name"]
    == "run_linking_target_pipeline"
]

record(
    "LINKING_TARGET_EXECUTION_FUNCTION_DISCOVERED",
    len(run_functions) == 1,
    run_functions,
)

automatic_signals = {
    "robots.txt": "robots.txt" in linking_source.lower(),
    "sitemap.xml": "sitemap.xml" in linking_source.lower(),
    "sitemap_index.xml": (
        "sitemap_index.xml"
        in linking_source.lower()
    ),
    "wp-sitemap.xml": (
        "wp-sitemap.xml"
        in linking_source.lower()
    ),
    "_fetch_and_expand_sitemaps": (
        "_fetch_and_expand_sitemaps"
        in linking_source
    ),
}

record(
    "AUTOMATIC_SITEMAP_DISCOVERY_PRESENT",
    all(automatic_signals.values()),
    automatic_signals,
)

record(
    "SITE_SOURCES_STAGE_CURRENTLY_ISOLATED",
    SITE_SOURCES_ROOT.is_dir(),
    str(SITE_SOURCES_ROOT),
)

candidate_files: list[Path] = []

for path in sorted(
    BACKEND_ROOT.rglob("*.py")
):
    try:
        text = path.read_text(
            encoding="utf-8-sig",
        )
    except Exception:
        continue

    lowered = text.lower()

    if (
        "_fetch_and_expand_sitemaps" in text
        or "def fetch_and_expand_sitemaps" in lowered
        or "sitemap.xml" in lowered
        or (
            "robots.txt" in lowered
            and "sitemap" in lowered
        )
    ):
        candidate_files.append(path)

record(
    "AUTOMATIC_SOURCE_CANDIDATES_DISCOVERED",
    bool(candidate_files),
    [
        str(
            path.relative_to(ROOT)
        ).replace("\\", "/")
        for path in candidate_files
    ],
)

authority_definitions: list[dict[str, Any]] = []
authority_references: list[dict[str, Any]] = []
candidate_syntax_failures: list[str] = []

target_function_names = {
    "_fetch_and_expand_sitemaps",
    "fetch_and_expand_sitemaps",
    "_fetch_sitemap",
    "fetch_sitemap",
    "_parse_sitemap",
    "parse_sitemap",
    "_fetch_url",
    "fetch_url",
}

for path in candidate_files:
    try:
        source = path.read_text(
            encoding="utf-8-sig",
        )

        tree = ast.parse(
            source,
            filename=str(path),
        )
    except SyntaxError as exc:
        candidate_syntax_failures.append(
            f"{path}: SyntaxError: {exc}"
        )
        continue

    for node in ast.walk(tree):
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            if (
                node.name in target_function_names
                or "sitemap" in node.name.lower()
                or (
                    "robots" in node.name.lower()
                    and "discover" in node.name.lower()
                )
            ):
                authority_definitions.append(
                    function_record(
                        path,
                        source,
                        node,
                    )
                )

        elif isinstance(node, ast.Call):
            call_name = dotted_name(
                node.func
            )

            if (
                "sitemap" in call_name.lower()
                or call_name.endswith(
                    (
                        "urlopen",
                        "requests.get",
                        "httpx.get",
                    )
                )
            ):
                authority_references.append(
                    {
                        "source": str(
                            path.relative_to(ROOT)
                        ).replace("\\", "/"),
                        "line": node.lineno,
                        "call": call_name,
                    }
                )

record(
    "CANDIDATE_PARSE_COMPLETED",
    True,
    candidate_syntax_failures,
)

fetch_authorities = [
    definition
    for definition in authority_definitions
    if definition["name"]
    in {
        "_fetch_and_expand_sitemaps",
        "fetch_and_expand_sitemaps",
    }
]

record(
    "CANONICAL_SITEMAP_EXPANSION_AUTHORITY_FOUND",
    bool(fetch_authorities),
    fetch_authorities,
)

record(
    "SITEMAP_AUTHORITY_DEFINITIONS_CAPTURED",
    bool(authority_definitions),
    authority_definitions,
)

record(
    "SITEMAP_AND_NETWORK_CALL_REFERENCES_CAPTURED",
    bool(authority_references),
    authority_references,
)

linking_calls = (
    run_functions[0]["calls"]
    if run_functions
    else []
)

sitemap_calls_in_linking = [
    call
    for call in linking_calls
    if (
        "sitemap" in call["name"].lower()
        or "robots" in call["name"].lower()
    )
]

record(
    "LINKING_PIPELINE_USES_SITEMAP_AUTHORITY",
    bool(sitemap_calls_in_linking),
    sitemap_calls_in_linking,
)

output_key_lines = [
    {
        "line": line_number,
        "text": line.strip(),
    }
    for line_number, line in enumerate(
        linking_source.splitlines(),
        start=1,
    )
    if any(
        token in line
        for token in (
            '"sitemap_url"',
            '"sitemap_urls"',
            '"sitemap_urls_count"',
            '"sitemap_used"',
            '"sitemap_url_count"',
            '"source"',
            '"errors"',
        )
    )
]

record(
    "SITE_SOURCE_OUTPUT_FIELDS_DISCOVERED",
    bool(output_key_lines),
    output_key_lines,
)

persistence_calls = [
    call
    for call in linking_calls
    if any(
        token in call["name"].lower()
        for token in (
            "write",
            "save",
            "persist",
            "repository",
        )
    )
]

record(
    "LINKING_PIPELINE_PERSISTENCE_CALLS_CAPTURED",
    True,
    persistence_calls,
)

manual_import_terms = (
    "import sitemap",
    "upload sitemap",
    "uploaded sitemap",
    "sitemap upload",
    "sitemap_upload",
)

manual_import_matches = [
    {
        "source": str(
            path.relative_to(ROOT)
        ).replace("\\", "/"),
        "terms": [
            term
            for term in manual_import_terms
            if term
            in path.read_text(
                encoding="utf-8-sig",
            ).lower()
        ],
    }
    for path in candidate_files
    if any(
        term
        in path.read_text(
            encoding="utf-8-sig",
        ).lower()
        for term in manual_import_terms
    )
]

record(
    "MANUAL_IMPORT_PATH_NOT_PART_OF_SITE_SOURCES",
    not manual_import_matches,
    manual_import_matches,
)

record(
    "LIVE_NETWORK_REQUEST_EXECUTED_NO",
    True,
)

record(
    "PRODUCTION_SOURCE_MODIFIED_NO",
    True,
)

record(
    "RUNTIME_REGISTRATION_CREATED_NO",
    True,
)

record(
    "UNIVERSAL_JOB_CREATED_NO",
    True,
)

record(
    "HANDLER_EXECUTED_NO",
    True,
)

passed_count = sum(
    1
    for _, passed, _ in results
    if passed
)

failed_checks = [
    name
    for name, passed, _ in results
    if not passed
]

required_checks = {
    "PROJECT_ROOT_EXISTS",
    "BACKEND_ROOT_EXISTS",
    "CONNECT_DOMAIN_ROOT_EXISTS",
    "LINKING_COORDINATOR_EXISTS",
    "LINKING_COORDINATOR_SYNTAX",
    "LINKING_TARGET_EXECUTION_FUNCTION_DISCOVERED",
    "AUTOMATIC_SITEMAP_DISCOVERY_PRESENT",
    "AUTOMATIC_SOURCE_CANDIDATES_DISCOVERED",
    "CANONICAL_SITEMAP_EXPANSION_AUTHORITY_FOUND",
    "SITEMAP_AUTHORITY_DEFINITIONS_CAPTURED",
    "LINKING_PIPELINE_USES_SITEMAP_AUTHORITY",
    "SITE_SOURCE_OUTPUT_FIELDS_DISCOVERED",
}

required_failures = [
    name
    for name, passed, _ in results
    if name in required_checks
    and not passed
]

status = (
    "COMPLETE"
    if not required_failures
    else "NOT_COMPLETE"
)

report_lines = [
    "LINKCRAFTER PIPELINE REGISTRATION",
    "PART B 4.2-A SITE SOURCES BOUNDARY INSPECTION",
    "",
    "Generated: "
    + datetime.now(timezone.utc).isoformat(),
    "Mode: READ-ONLY PRODUCTION BOUNDARY INSPECTION",
    "Production source changes: NONE",
    "Runtime registrations created: NO",
    "Registry persistence executed: NO",
    "Universal jobs created: NO",
    "Queue claims executed: NO",
    "Handlers executed: NO",
    "Live website requests executed: NO",
    f"Project root: {ROOT}",
    f"INSPECTION STATUS: {status}",
    "",
    "=" * 112,
    "RUNTIME VERIFICATION",
    "=" * 112,
]

for name, passed, detail in results:
    report_lines.append(
        f"{name}: "
        f"{'PASS' if passed else 'FAIL'}"
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
        "BOUNDARY DECISION",
        "=" * 112,
        (
            "Site Sources is the automatic website-source acquisition "
            "stage. It may use robots.txt and website-provided sitemap "
            "documents as discovery sources."
        ),
        "",
        (
            "The inspection does not remove automatic sitemap discovery "
            "and does not restore manual frontend/ATS sitemap import."
        ),
        "",
        (
            "If Site Sources is currently embedded inside the Linking "
            "Target coordinator, Part B 4.2-B will isolate that work "
            "without duplicating its network authority."
        ),
        "",
        (
            "The isolated Site Sources stage must not register itself, "
            "submit another job or execute downstream stages."
        ),
        "",
        "=" * 112,
        "FINAL RESULT",
        "=" * 112,
        f"CHECKS_PASSED={passed_count}",
        f"CHECKS_FAILED={len(failed_checks)}",
        "FAILED_CHECKS="
        + json.dumps(failed_checks),
    ]
)

if status == "COMPLETE":
    report_lines.append(
        "FINAL RESULT: PART B 4.2-A SITE SOURCES INSPECTION COMPLETE"
    )
else:
    report_lines.append(
        "FINAL RESULT: PART B 4.2-A SITE SOURCES INSPECTION NOT_COMPLETE"
    )

REPORT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT.write_text(
    "\n".join(report_lines) + "\n",
    encoding="utf-8",
    newline="\n",
)

print("")
print("\n".join(report_lines[-20:]))

raise SystemExit(
    0 if status == "COMPLETE" else 1
)