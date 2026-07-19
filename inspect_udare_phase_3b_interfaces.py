from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parent

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "udare_phase_3b_interface_inspection"
    / "udare_phase_3b_interface_inspection.json"
)


TARGETS = {
    "universal_worker": {
        "path":
            ROOT
            / "backend"
            / "server"
            / "workers"
            / "universal_knowledge_worker.py",

        "functions": (
            "execute_universal_knowledge_job_v1",
            "_run_website_raw_html_acquisition_job",
        ),
    },

    "queue_runner": {
        "path":
            ROOT
            / "backend"
            / "server"
            / "workers"
            / "universal_knowledge_queue_runner.py",

        "functions": (
            "run_universal_knowledge_queue_v1",
        ),
    },

    "raw_html_store": {
        "path":
            ROOT
            / "backend"
            / "server"
            / "stores"
            / "raw_website_html_store.py",

        "functions": (
            "load_raw_website_html_store_v1",
            "get_raw_website_html_v1",
        ),
    },

    "udare_engine": {
        "path":
            ROOT
            / "backend"
            / "server"
            / "stores"
            / "universal_dom_article_reconstruction_engine.py",

        "functions": (
            "reconstruct_universal_dom_article_v1",
            "explain_universal_dom_article_reconstruction_v1",
        ),
    },

    "udare_store": {
        "path":
            ROOT
            / "backend"
            / "server"
            / "stores"
            / "udare_store.py",

        "functions": (
            "persist_udare_article_document_v1",
            "refresh_udare_store_manifest_v1",
            "verify_udare_store_v1",
        ),
    },

    "orchestrator": {
        "path":
            ROOT
            / "backend"
            / "server"
            / "jobs"
            / "universal_knowledge_orchestrator.py",

        "functions": (
            "create_universal_knowledge_job",
            "update_job_status",
            "update_job_progress",
            "read_job_status",
            "read_job_progress",
            "read_queue",
            "record_job_failure",
        ),
    },

    "runtime_infrastructure": {
        "path":
            ROOT
            / "backend"
            / "server"
            / "runtime"
            / "universal_runtime_infrastructure.py",

        "functions": (
            "move_to_dead_letter",
            "retry_job",
            "workspace_concurrency_decision",
        ),
    },
}


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def relative(
    path: Path,
) -> str:
    return path.relative_to(
        ROOT
    ).as_posix()


def extract_imports(
    source: str,
    tree: ast.Module,
) -> List[str]:
    imports: List[str] = []

    for node in tree.body:
        if isinstance(
            node,
            (
                ast.Import,
                ast.ImportFrom,
            ),
        ):
            segment = ast.get_source_segment(
                source,
                node,
            )

            if segment:
                imports.append(
                    segment
                )

    return imports


def function_signature(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> str:
    prefix = (
        "async def"
        if isinstance(
            node,
            ast.AsyncFunctionDef,
        )
        else "def"
    )

    arguments = ast.unparse(
        node.args
    )

    returns = (
        ast.unparse(
            node.returns
        )
        if node.returns is not None
        else ""
    )

    signature = (
        f"{prefix} {node.name}({arguments})"
    )

    if returns:
        signature += (
            f" -> {returns}"
        )

    return signature


def function_calls(
    node: ast.AST,
) -> List[str]:
    calls: set[str] = set()

    for child in ast.walk(
        node
    ):
        if not isinstance(
            child,
            ast.Call,
        ):
            continue

        function = child.func

        if isinstance(
            function,
            ast.Name,
        ):
            calls.add(
                function.id
            )

        elif isinstance(
            function,
            ast.Attribute,
        ):
            parts = [
                function.attr
            ]

            value = function.value

            while isinstance(
                value,
                ast.Attribute,
            ):
                parts.append(
                    value.attr
                )

                value = value.value

            if isinstance(
                value,
                ast.Name,
            ):
                parts.append(
                    value.id
                )

            calls.add(
                ".".join(
                    reversed(
                        parts
                    )
                )
            )

    return sorted(
        calls
    )


def return_expressions(
    node: ast.AST,
) -> List[str]:
    results: List[str] = []

    for child in ast.walk(
        node
    ):
        if not isinstance(
            child,
            ast.Return,
        ):
            continue

        if child.value is None:
            results.append(
                "None"
            )
        else:
            results.append(
                ast.unparse(
                    child.value
                )
            )

    return results


report: Dict[str, Any] = {
    "schema_version":
        "udare_phase_3b_interface_inspection_v1",

    "generated_at_utc":
        utc_now(),

    "phase":
        "Phase 3B — Exact UDARE Worker Interface Inspection",

    "files":
        {},

    "missing_files":
        [],

    "missing_functions":
        [],

    "syntax_errors":
        [],

    "phase_boundaries": {
        "source_modified":
            False,

        "job_created":
            False,

        "queue_invoked":
            False,

        "worker_invoked":
            False,

        "article_reconstructed":
            False,

        "udare_store_populated":
            False,
    },
}


for target_name, configuration in (
    TARGETS.items()
):
    path = configuration[
        "path"
    ]

    if not path.is_file():
        report[
            "missing_files"
        ].append(
            relative(
                path
            )
        )

        continue

    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    try:
        tree = ast.parse(
            source,
            filename=str(
                path
            ),
        )

    except SyntaxError as exc:
        report[
            "syntax_errors"
        ].append({
            "path":
                relative(
                    path
                ),

            "line":
                exc.lineno,

            "offset":
                exc.offset,

            "message":
                exc.msg,
        })

        continue

    file_result: Dict[str, Any] = {
        "path":
            relative(
                path
            ),

        "imports":
            extract_imports(
                source,
                tree,
            ),

        "functions":
            {},
    }

    top_level_functions = {
        node.name:
            node

        for node
        in tree.body

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
    }

    for function_name in configuration[
        "functions"
    ]:
        node = top_level_functions.get(
            function_name
        )

        if node is None:
            report[
                "missing_functions"
            ].append({
                "path":
                    relative(
                        path
                    ),

                "function":
                    function_name,
            })

            continue

        source_segment = (
            ast.get_source_segment(
                source,
                node,
            )
            or ""
        )

        file_result[
            "functions"
        ][
            function_name
        ] = {
            "line":
                node.lineno,

            "end_line":
                node.end_lineno,

            "signature":
                function_signature(
                    node
                ),

            "calls":
                function_calls(
                    node
                ),

            "returns":
                return_expressions(
                    node
                ),

            "source":
                source_segment,
        }

    report[
        "files"
    ][
        target_name
    ] = file_result


blocking_failures = []

if report[
    "missing_files"
]:
    blocking_failures.append(
        "missing_files"
    )

if report[
    "missing_functions"
]:
    blocking_failures.append(
        "missing_functions"
    )

if report[
    "syntax_errors"
]:
    blocking_failures.append(
        "syntax_errors"
    )


report[
    "blocking_failures"
] = blocking_failures

report[
    "decision"
] = (
    "READY_FOR_PHASE_3_WORKER_PATCH"
    if not blocking_failures
    else "BLOCKED"
)

report[
    "next_action"
] = (
    "Implement the UDARE queue-safe worker adapter and "
    "register udare_reconstruction in the active worker dispatcher."
    if report[
        "decision"
    ]
    == "READY_FOR_PHASE_3_WORKER_PATCH"
    else
    "Resolve the missing interface or syntax conditions."
)


REPORT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT_PATH.write_text(
    json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 112)
print(
    "PHASE 3B — EXACT UDARE "
    "WORKER INTERFACE INSPECTION"
)
print("=" * 112)


for target_name, file_result in (
    report[
        "files"
    ].items()
):
    print()
    print(
        target_name.upper()
    )

    print(
        "  Path:",
        file_result[
            "path"
        ],
    )

    for function_name, function_result in (
        file_result[
            "functions"
        ].items()
    ):
        print(
            "  -",
            function_result[
                "signature"
            ],
        )

        print(
            "    Lines:",
            (
                f"{function_result['line']}"
                f"-{function_result['end_line']}"
            ),
        )

        print(
            "    Calls:",
            ", ".join(
                function_result[
                    "calls"
                ]
            ),
        )


print()
print("MISSING FILES")

if report[
    "missing_files"
]:
    for value in report[
        "missing_files"
    ]:
        print(
            "  -",
            value,
        )
else:
    print(
        "  None"
    )


print()
print("MISSING FUNCTIONS")

if report[
    "missing_functions"
]:
    for value in report[
        "missing_functions"
    ]:
        print(
            "  -",
            (
                f"{value['path']} :: "
                f"{value['function']}"
            ),
        )
else:
    print(
        "  None"
    )


print()
print("SYNTAX ERRORS")

if report[
    "syntax_errors"
]:
    for value in report[
        "syntax_errors"
    ]:
        print(
            "  -",
            value,
        )
else:
    print(
        "  None"
    )


print()
print(
    "Report:",
    REPORT_PATH,
)

print()
print("=" * 112)
print(
    "PHASE 3B DECISION:",
    report[
        "decision"
    ],
)
print("=" * 112)

print(
    "No source files were modified."
)

print(
    "No jobs were created or queued."
)

print(
    "No worker or engine was invoked."
)

print(
    "No article was reconstructed or stored."
)

raise SystemExit(
    0
    if report[
        "decision"
    ]
    == "READY_FOR_PHASE_3_WORKER_PATCH"
    else 1
)
