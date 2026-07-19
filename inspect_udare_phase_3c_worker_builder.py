from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parent
SERVER_ROOT = ROOT / "backend" / "server"

REPORT_PATH = (
    SERVER_ROOT
    / "data"
    / "runtime"
    / "udare_phase_3c_worker_builder_inspection"
    / "udare_phase_3c_worker_builder_inspection.json"
)


EXACT_FUNCTIONS = {
    (
        SERVER_ROOT
        / "workers"
        / "universal_knowledge_worker.py"
    ): (
        "execute_universal_knowledge_job_v1",
    ),

    (
        SERVER_ROOT
        / "workers"
        / "universal_knowledge_queue_runner.py"
    ): (
        "run_universal_knowledge_queue_v1",
    ),

    (
        SERVER_ROOT
        / "stores"
        / "raw_website_html_store.py"
    ): (
        "load_raw_website_html_store_v1",
        "get_raw_website_html_v1",
    ),

    (
        SERVER_ROOT
        / "stores"
        / "udare_store.py"
    ): (
        "validate_udare_article_document_v1",
    ),
}


SEARCH_TOKENS = (
    "udare_article_reader_document_v1",
    "ARTICLE_DOCUMENT_FORMAT",
    "build_udare_article",
    "render_udare_article",
    "create_udare_article",
    "article_document",
    "reader_document",
)


EXCLUDED_DIRECTORY_NAMES = {
    "__pycache__",
    "_quarantine",
    "runtime_backups",
    "backups",
    "backup",
    "data",
    ".git",
    ".pytest_cache",
}


EXCLUDED_FILENAME_FRAGMENTS = (
    ".before_",
    ".backup",
    "_backup_",
    ".before_phase",
)


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


def active_source(
    path: Path,
) -> bool:
    if path.suffix.casefold() != ".py":
        return False

    try:
        parts = path.relative_to(
            SERVER_ROOT
        ).parts

    except ValueError:
        return False

    if any(
        part.casefold()
        in EXCLUDED_DIRECTORY_NAMES
        for part in parts[:-1]
    ):
        return False

    filename = path.name.casefold()

    if any(
        fragment.casefold()
        in filename
        for fragment in EXCLUDED_FILENAME_FRAGMENTS
    ):
        return False

    return True


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

    rendered = (
        f"{prefix} {node.name}"
        f"({ast.unparse(node.args)})"
    )

    if node.returns is not None:
        rendered += (
            " -> "
            + ast.unparse(
                node.returns
            )
        )

    return rendered


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

        target = child.func

        if isinstance(
            target,
            ast.Name,
        ):
            calls.add(
                target.id
            )

        elif isinstance(
            target,
            ast.Attribute,
        ):
            calls.add(
                target.attr
            )

    return sorted(
        calls
    )


report: Dict[str, Any] = {
    "schema_version":
        "udare_phase_3c_worker_builder_inspection_v1",

    "generated_at_utc":
        utc_now(),

    "exact_functions":
        {},

    "builder_candidates":
        [],

    "syntax_errors":
        [],

    "missing_functions":
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


# =====================================================================
# 1. EXTRACT EXACT WORKER, QUEUE, RAW STORE AND VALIDATOR FUNCTIONS
# =====================================================================

for path, requested_functions in (
    EXACT_FUNCTIONS.items()
):
    if not path.is_file():
        report[
            "missing_functions"
        ].append({
            "path":
                relative(
                    path
                ),

            "function":
                "<file missing>",
        })

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

            "message":
                exc.msg,
        })

        continue

    functions = {
        node.name:
            node

        for node in tree.body

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
    }

    for function_name in requested_functions:
        node = functions.get(
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

        report[
            "exact_functions"
        ][
            function_name
        ] = {
            "path":
                relative(
                    path
                ),

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

            "source":
                (
                    ast.get_source_segment(
                        source,
                        node,
                    )
                    or ""
                ),
        }


# =====================================================================
# 2. SEARCH ACTIVE SOURCE FOR THE CERTIFIED ARTICLE-DOCUMENT BUILDER
# =====================================================================

for path in sorted(
    SERVER_ROOT.rglob(
        "*.py"
    )
):
    if not active_source(
        path
    ):
        continue

    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    source_lower = source.casefold()

    if not any(
        token.casefold()
        in source_lower
        for token in SEARCH_TOKENS
    ):
        continue

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

            "message":
                exc.msg,
        })

        continue

    for node in tree.body:
        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        segment = (
            ast.get_source_segment(
                source,
                node,
            )
            or ""
        )

        segment_lower = (
            segment.casefold()
        )

        matched_tokens = [
            token

            for token
            in SEARCH_TOKENS

            if token.casefold()
            in segment_lower
        ]

        name_lower = (
            node.name.casefold()
        )

        name_signal = any(
            token in name_lower
            for token in (
                "build",
                "render",
                "create",
                "document",
                "reader",
                "article",
                "udare",
            )
        )

        if (
            not matched_tokens
            and not name_signal
        ):
            continue

        if not any(
            token in segment_lower
            for token in (
                "udare",
                "article_document",
                "reader_document",
            )
        ):
            continue

        report[
            "builder_candidates"
        ].append({
            "path":
                relative(
                    path
                ),

            "name":
                node.name,

            "line":
                node.lineno,

            "end_line":
                node.end_lineno,

            "signature":
                function_signature(
                    node
                ),

            "matched_tokens":
                matched_tokens,

            "calls":
                function_calls(
                    node
                ),

            "source":
                segment,
        })


report[
    "builder_candidates"
] = sorted(
    report[
        "builder_candidates"
    ],
    key=lambda item: (
        item[
            "path"
        ],
        item[
            "line"
        ],
    ),
)


builder_candidates = [
    item

    for item
    in report[
        "builder_candidates"
    ]

    if item[
        "name"
    ]
    not in {
        "persist_udare_article_document_v1",
        "validate_udare_article_document_v1",
        "load_udare_article_document_v1",
        "verify_udare_store_v1",
    }
]


report[
    "usable_builder_candidates"
] = (
    builder_candidates
)


blocking_failures = []

if report[
    "syntax_errors"
]:
    blocking_failures.append(
        "syntax_errors"
    )

if report[
    "missing_functions"
]:
    blocking_failures.append(
        "missing_exact_functions"
    )

if not builder_candidates:
    blocking_failures.append(
        "certified_article_document_builder_not_found"
    )


report[
    "blocking_failures"
] = blocking_failures

report[
    "decision"
] = (
    "READY_FOR_PHASE_3C_WORKER_PATCH"
    if not blocking_failures
    else "BUILDER_INTERFACE_REQUIRED"
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
    "PHASE 3C — UDARE WORKER AND "
    "ARTICLE-DOCUMENT BUILDER INSPECTION"
)
print("=" * 112)

print()
print("EXACT FUNCTIONS")

for name, result in (
    report[
        "exact_functions"
    ].items()
):
    print(
        "  -",
        result[
            "signature"
        ],
    )

    print(
        "    Path:",
        (
            f"{result['path']}:"
            f"{result['line']}"
        ),
    )

    print(
        "    Calls:",
        ", ".join(
            result[
                "calls"
            ]
        ),
    )


print()
print("USABLE ARTICLE-DOCUMENT BUILDERS")

if builder_candidates:
    for candidate in builder_candidates:
        print(
            "  -",
            candidate[
                "signature"
            ],
        )

        print(
            "    Path:",
            (
                f"{candidate['path']}:"
                f"{candidate['line']}"
            ),
        )

        print(
            "    Matched:",
            candidate[
                "matched_tokens"
            ],
        )

else:
    print(
        "  NONE FOUND"
    )


print()
print("MISSING FUNCTIONS")

if report[
    "missing_functions"
]:
    for item in report[
        "missing_functions"
    ]:
        print(
            "  -",
            (
                f"{item['path']} :: "
                f"{item['function']}"
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
    for item in report[
        "syntax_errors"
    ]:
        print(
            "  -",
            item,
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
    "PHASE 3C DECISION:",
    report[
        "decision"
    ],
)
print("=" * 112)

print(
    "No source files were modified."
)

print(
    "No job, queue runner, worker or "
    "reconstruction engine was invoked."
)

print(
    "No article was written to the UDARE Store."
)

raise SystemExit(
    0
    if report[
        "decision"
    ]
    == "READY_FOR_PHASE_3C_WORKER_PATCH"
    else 2
)
