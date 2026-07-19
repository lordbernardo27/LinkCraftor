from __future__ import annotations

import ast
import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List


ROOT = Path(__file__).resolve().parent
SERVER_ROOT = ROOT / "backend" / "server"

REPORT_PATH = (
    SERVER_ROOT
    / "data"
    / "runtime"
    / "udare_phase_3_queue_worker_scan"
    / "udare_phase_3_queue_worker_scan.json"
)


CORE_FILES = {
    "orchestrator":
        SERVER_ROOT
        / "jobs"
        / "universal_knowledge_orchestrator.py",

    "queue_runner":
        SERVER_ROOT
        / "workers"
        / "universal_knowledge_queue_runner.py",

    "worker":
        SERVER_ROOT
        / "workers"
        / "universal_knowledge_worker.py",

    "job_store":
        SERVER_ROOT
        / "orchestration"
        / "job_store.py",

    "runtime_contract":
        SERVER_ROOT
        / "runtime"
        / "udare_runtime_contract.py",

    "udare_store":
        SERVER_ROOT
        / "stores"
        / "udare_store.py",
}


TARGET_FUNCTIONS = {
    "execute_universal_knowledge_job_v1",
    "run_universal_knowledge_queue_v1",
    "create_universal_knowledge_job",
    "update_job_status",
    "read_job_status",
    "read_queue",
    "record_job_failure",
    "retry_job",
    "move_to_dead_letter",
    "inspect_queue",
    "inspect_workers",
    "create_batch",
    "inspect_batch",
    "workspace_concurrency_decision",
    "persist_udare_article_document_v1",
    "create_udare_store_v1",
    "refresh_udare_store_manifest_v1",
    "verify_udare_store_v1",
}


UDARE_ENGINE_TOKENS = (
    "universal_dom_article_reconstruction_engine_v1_7",
    "udare_v1_7",
    "reconstruct_article",
    "reconstruct",
)


RAW_HTML_TOKENS = (
    "raw_website_html_store_v1",
    "raw_html_store",
    "load_raw_html",
    "read_raw_html",
    "get_raw_html",
    "html_id",
)


RUNTIME_CONTROL_TOKENS = (
    "lease_owner",
    "dead_letter",
    "retry",
    "attempt_count",
    "max_attempts",
    "workspace_concurrency",
    "progress",
)


EXCLUDED_DIRECTORY_NAMES = {
    "__pycache__",
    "_quarantine",
    "runtime_backups",
    "backups",
    "backup",
    ".git",
    ".pytest_cache",
    "node_modules",
}


EXCLUDED_FILENAME_FRAGMENTS = (
    ".before_",
    ".backup",
    "_backup_",
    ".phase1_backup_",
    ".before_format_fix_",
    ".before_line76_repair_",
    ".before_phase2_",
    ".before_phase2c_",
)


ACTIVE_SEARCH_DIRECTORIES = (
    "jobs",
    "workers",
    "orchestration",
    "runtime",
    "stores",
    "engine",
    "services",
    "pipelines",
)


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def sha256_file(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def relative(
    path: Path,
) -> str:
    return path.relative_to(
        ROOT
    ).as_posix()


def is_active_source(
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
        fragment.casefold() in filename
        for fragment in EXCLUDED_FILENAME_FRAGMENTS
    ):
        return False

    return True


def active_source_files() -> List[Path]:
    files: set[Path] = set()

    for directory_name in ACTIVE_SEARCH_DIRECTORIES:
        directory = (
            SERVER_ROOT
            / directory_name
        )

        if not directory.exists():
            continue

        for path in directory.rglob(
            "*.py"
        ):
            if is_active_source(
                path
            ):
                files.add(
                    path
                )

    for path in CORE_FILES.values():
        if (
            path.is_file()
            and is_active_source(
                path
            )
        ):
            files.add(
                path
            )

    return sorted(
        files
    )


def line_text(
    source: str,
    line_number: int,
) -> str:
    lines = source.splitlines()

    if (
        line_number < 1
        or line_number > len(lines)
    ):
        return ""

    return lines[
        line_number - 1
    ].strip()


def literal_strings(
    node: ast.AST,
) -> List[str]:
    results: List[str] = []

    for child in ast.walk(
        node
    ):
        if (
            isinstance(
                child,
                ast.Constant,
            )
            and isinstance(
                child.value,
                str,
            )
        ):
            results.append(
                child.value
            )

    return results


def function_source(
    source: str,
    node: ast.AST,
) -> str:
    return (
        ast.get_source_segment(
            source,
            node,
        )
        or ""
    )


def assignment_names(
    node: ast.AST,
) -> List[str]:
    targets: List[ast.expr] = []

    if isinstance(
        node,
        ast.Assign,
    ):
        targets.extend(
            node.targets
        )

    elif isinstance(
        node,
        ast.AnnAssign,
    ):
        targets.append(
            node.target
        )

    results: List[str] = []

    for target in targets:
        if isinstance(
            target,
            ast.Name,
        ):
            results.append(
                target.id
            )

        elif isinstance(
            target,
            ast.Attribute,
        ):
            results.append(
                target.attr
            )

    return results


files = active_source_files()

before_hashes = {
    relative(
        path
    ):
        sha256_file(
            path
        )

    for path
    in files
}


core_file_checks = {
    name: {
        "path":
            relative(
                path
            )
            if path.exists()
            else str(
                path
            ),

        "exists":
            path.is_file(),
    }

    for name, path
    in CORE_FILES.items()
}


syntax_errors: List[Dict[str, Any]] = []

function_locations: Dict[
    str,
    List[Dict[str, Any]],
] = defaultdict(
    list
)

dispatch_candidates: List[
    Dict[str, Any]
] = []

registry_candidates: List[
    Dict[str, Any]
] = []

udare_engine_candidates: List[
    Dict[str, Any]
] = []

raw_html_candidates: List[
    Dict[str, Any]
] = []

runtime_control_candidates: List[
    Dict[str, Any]
] = []

worker_source = ""
queue_runner_source = ""
orchestrator_source = ""


for path in files:
    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    path_text = relative(
        path
    )

    if (
        path
        == CORE_FILES[
            "worker"
        ]
    ):
        worker_source = source

    elif (
        path
        == CORE_FILES[
            "queue_runner"
        ]
    ):
        queue_runner_source = source

    elif (
        path
        == CORE_FILES[
            "orchestrator"
        ]
    ):
        orchestrator_source = source

    try:
        tree = ast.parse(
            source,
            filename=str(
                path
            ),
        )

    except SyntaxError as exc:
        syntax_errors.append({
            "path":
                path_text,

            "line":
                exc.lineno,

            "offset":
                exc.offset,

            "message":
                exc.msg,

            "text":
                (
                    exc.text.strip()
                    if exc.text
                    else ""
                ),
        })

        continue

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            if node.name in TARGET_FUNCTIONS:
                function_locations[
                    node.name
                ].append({
                    "path":
                        path_text,

                    "line":
                        node.lineno,

                    "async":
                        isinstance(
                            node,
                            ast.AsyncFunctionDef,
                        ),

                    "signature":
                        line_text(
                            source,
                            node.lineno,
                        ),
                })

            lowered_name = (
                node.name.casefold()
            )

            node_strings = literal_strings(
                node
            )

            if any(
                token in lowered_name
                for token in (
                    "execute",
                    "dispatch",
                    "route",
                    "handler",
                    "worker",
                    "queue",
                )
            ):
                dispatch_candidates.append({
                    "path":
                        path_text,

                    "function":
                        node.name,

                    "line":
                        node.lineno,

                    "job_type_strings": [
                        value

                        for value
                        in node_strings

                        if any(
                            token in value.casefold()

                            for token in (
                                "raw_html",
                                "article",
                                "website",
                                "udare",
                                "reconstruction",
                                "upload",
                                "semantic",
                            )
                        )
                    ][:50],
                })

            node_source = function_source(
                source,
                node,
            )

            node_source_lower = (
                node_source.casefold()
            )

            if any(
                token.casefold()
                in node_source_lower

                for token
                in UDARE_ENGINE_TOKENS
            ):
                udare_engine_candidates.append({
                    "path":
                        path_text,

                    "symbol_type":
                        "function",

                    "name":
                        node.name,

                    "line":
                        node.lineno,

                    "matched_tokens": [
                        token

                        for token
                        in UDARE_ENGINE_TOKENS

                        if token.casefold()
                        in node_source_lower
                    ],
                })

            if any(
                token.casefold()
                in node_source_lower

                for token
                in RAW_HTML_TOKENS
            ):
                raw_html_candidates.append({
                    "path":
                        path_text,

                    "symbol_type":
                        "function",

                    "name":
                        node.name,

                    "line":
                        node.lineno,

                    "matched_tokens": [
                        token

                        for token
                        in RAW_HTML_TOKENS

                        if token.casefold()
                        in node_source_lower
                    ],
                })

            if any(
                token.casefold()
                in node_source_lower

                for token
                in RUNTIME_CONTROL_TOKENS
            ):
                runtime_control_candidates.append({
                    "path":
                        path_text,

                    "symbol_type":
                        "function",

                    "name":
                        node.name,

                    "line":
                        node.lineno,

                    "matched_tokens": [
                        token

                        for token
                        in RUNTIME_CONTROL_TOKENS

                        if token.casefold()
                        in node_source_lower
                    ],
                })

        elif isinstance(
            node,
            ast.ClassDef,
        ):
            node_source = function_source(
                source,
                node,
            )

            node_source_lower = (
                node_source.casefold()
            )

            if any(
                token.casefold()
                in node_source_lower

                for token
                in UDARE_ENGINE_TOKENS
            ):
                udare_engine_candidates.append({
                    "path":
                        path_text,

                    "symbol_type":
                        "class",

                    "name":
                        node.name,

                    "line":
                        node.lineno,

                    "matched_tokens": [
                        token

                        for token
                        in UDARE_ENGINE_TOKENS

                        if token.casefold()
                        in node_source_lower
                    ],
                })

            if any(
                token.casefold()
                in node_source_lower

                for token
                in RAW_HTML_TOKENS
            ):
                raw_html_candidates.append({
                    "path":
                        path_text,

                    "symbol_type":
                        "class",

                    "name":
                        node.name,

                    "line":
                        node.lineno,

                    "matched_tokens": [
                        token

                        for token
                        in RAW_HTML_TOKENS

                        if token.casefold()
                        in node_source_lower
                    ],
                })

        elif isinstance(
            node,
            (
                ast.Assign,
                ast.AnnAssign,
            ),
        ):
            names = assignment_names(
                node
            )

            strings = literal_strings(
                node
            )

            for name in names:
                lowered_name = (
                    name.casefold()
                )

                if any(
                    token in lowered_name

                    for token in (
                        "handler",
                        "dispatch",
                        "route",
                        "stage",
                        "job_type",
                        "supported",
                        "registry",
                        "queue",
                    )
                ):
                    registry_candidates.append({
                        "path":
                            path_text,

                        "name":
                            name,

                        "line":
                            node.lineno,

                        "literal_strings":
                            strings[:100],
                    })


worker_dispatch_source = ""

if worker_source:
    worker_tree = ast.parse(
        worker_source,
        filename=str(
            CORE_FILES[
                "worker"
            ]
        ),
    )

    for node in worker_tree.body:
        if (
            isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
            and node.name
            == "execute_universal_knowledge_job_v1"
        ):
            worker_dispatch_source = (
                function_source(
                    worker_source,
                    node,
                )
            )

            break


queue_runner_function_source = ""

if queue_runner_source:
    runner_tree = ast.parse(
        queue_runner_source,
        filename=str(
            CORE_FILES[
                "queue_runner"
            ]
        ),
    )

    for node in runner_tree.body:
        if (
            isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
            and node.name
            == "run_universal_knowledge_queue_v1"
        ):
            queue_runner_function_source = (
                function_source(
                    queue_runner_source,
                    node,
                )
            )

            break


supported_job_types: List[str] = []

if orchestrator_source:
    orchestrator_tree = ast.parse(
        orchestrator_source,
        filename=str(
            CORE_FILES[
                "orchestrator"
            ]
        ),
    )

    for node in orchestrator_tree.body:
        if not isinstance(
            node,
            (
                ast.Assign,
                ast.AnnAssign,
            ),
        ):
            continue

        names = assignment_names(
            node
        )

        if (
            "SUPPORTED_JOB_TYPES"
            not in names
        ):
            continue

        value_node = node.value

        if isinstance(
            value_node,
            (
                ast.Set,
                ast.List,
                ast.Tuple,
            ),
        ):
            supported_job_types = sorted(
                str(
                    element.value
                )

                for element
                in value_node.elts

                if (
                    isinstance(
                        element,
                        ast.Constant,
                    )
                    and isinstance(
                        element.value,
                        str,
                    )
                )
            )

        break


worker_has_udare_dispatch = bool(
    re.search(
        r"""(?ix)
        ["']
        udare_reconstruction
        ["']
        """,
        worker_dispatch_source,
    )
)


runner_calls_worker = bool(
    re.search(
        r"\bexecute_universal_knowledge_job_v1\s*\(",
        queue_runner_function_source,
    )
)


runner_reads_queue = any(
    token in queue_runner_function_source

    for token in (
        "read_queue(",
        "queue_path(",
    )
)


udare_engine_candidates = sorted(
    udare_engine_candidates,
    key=lambda item: (
        item[
            "path"
        ],
        item[
            "line"
        ],
        item[
            "name"
        ],
    ),
)


raw_html_candidates = sorted(
    raw_html_candidates,
    key=lambda item: (
        item[
            "path"
        ],
        item[
            "line"
        ],
        item[
            "name"
        ],
    ),
)


runtime_control_candidates = sorted(
    runtime_control_candidates,
    key=lambda item: (
        item[
            "path"
        ],
        item[
            "line"
        ],
        item[
            "name"
        ],
    ),
)


after_hashes = {
    relative(
        path
    ):
        sha256_file(
            path
        )

    for path
    in files
}


modified_sources = sorted(
    path

    for path
    in set(
        before_hashes
    )
    | set(
        after_hashes
    )

    if before_hashes.get(
        path
    )
    != after_hashes.get(
        path
    )
)


checks = {
    "active_orchestrator_exists":
        core_file_checks[
            "orchestrator"
        ][
            "exists"
        ],

    "active_queue_runner_exists":
        core_file_checks[
            "queue_runner"
        ][
            "exists"
        ],

    "active_worker_exists":
        core_file_checks[
            "worker"
        ][
            "exists"
        ],

    "active_job_store_exists":
        core_file_checks[
            "job_store"
        ][
            "exists"
        ],

    "udare_runtime_contract_exists":
        core_file_checks[
            "runtime_contract"
        ][
            "exists"
        ],

    "udare_store_exists":
        core_file_checks[
            "udare_store"
        ][
            "exists"
        ],

    "core_scanned_sources_syntax_clean":
        not syntax_errors,

    "udare_job_type_registered":
        "udare_reconstruction"
        in supported_job_types,

    "queue_runner_function_found":
        bool(
            function_locations.get(
                "run_universal_knowledge_queue_v1"
            )
        ),

    "worker_executor_function_found":
        bool(
            function_locations.get(
                "execute_universal_knowledge_job_v1"
            )
        ),

    "queue_runner_calls_worker":
        runner_calls_worker,

    "queue_runner_reads_queue":
        runner_reads_queue,

    "udare_store_persistence_found":
        bool(
            function_locations.get(
                "persist_udare_article_document_v1"
            )
        ),

    "udare_engine_candidate_found":
        bool(
            udare_engine_candidates
        ),

    "raw_html_reader_candidate_found":
        bool(
            raw_html_candidates
        ),

    "scan_modified_no_active_sources":
        not modified_sources,
}


blocking_checks = (
    "active_orchestrator_exists",
    "active_queue_runner_exists",
    "active_worker_exists",
    "active_job_store_exists",
    "udare_runtime_contract_exists",
    "udare_store_exists",
    "core_scanned_sources_syntax_clean",
    "udare_job_type_registered",
    "queue_runner_function_found",
    "worker_executor_function_found",
    "queue_runner_calls_worker",
    "queue_runner_reads_queue",
    "udare_store_persistence_found",
    "udare_engine_candidate_found",
    "raw_html_reader_candidate_found",
    "scan_modified_no_active_sources",
)


blocking_failures = [
    name

    for name
    in blocking_checks

    if not checks[
        name
    ]
]


decision = (
    "READY_FOR_PHASE_3_QUEUE_WORKER_PATCH"
    if not blocking_failures
    else "BLOCKED"
)


report = {
    "schema_version":
        "udare_phase_3_queue_worker_scan_v1",

    "generated_at_utc":
        utc_now(),

    "workspace_id":
        "ws_whattoexpect_com",

    "pipeline":
        "website_reconstruction",

    "stage":
        "udare_reconstruction",

    "scope":
        "Phase 3 queue and worker integration discovery only",

    "decision":
        decision,

    "blocking_failures":
        blocking_failures,

    "counts": {
        "active_python_files_scanned":
            len(
                files
            ),

        "syntax_errors":
            len(
                syntax_errors
            ),

        "dispatch_candidates":
            len(
                dispatch_candidates
            ),

        "registry_candidates":
            len(
                registry_candidates
            ),

        "udare_engine_candidates":
            len(
                udare_engine_candidates
            ),

        "raw_html_candidates":
            len(
                raw_html_candidates
            ),

        "runtime_control_candidates":
            len(
                runtime_control_candidates
            ),

        "modified_active_sources":
            len(
                modified_sources
            ),
    },

    "checks":
        checks,

    "core_files":
        core_file_checks,

    "target_functions": {
        name:
            function_locations.get(
                name,
                [],
            )

        for name
        in sorted(
            TARGET_FUNCTIONS
        )
    },

    "supported_job_types":
        supported_job_types,

    "worker_dispatch": {
        "udare_handler_present":
            worker_has_udare_dispatch,

        "source":
            worker_dispatch_source,
    },

    "queue_runner": {
        "calls_worker":
            runner_calls_worker,

        "reads_queue":
            runner_reads_queue,

        "source":
            queue_runner_function_source,
    },

    "dispatch_candidates":
        dispatch_candidates[:100],

    "registry_candidates":
        registry_candidates[:100],

    "udare_engine_candidates":
        udare_engine_candidates[:100],

    "raw_html_candidates":
        raw_html_candidates[:100],

    "runtime_control_candidates":
        runtime_control_candidates[:150],

    "syntax_errors":
        syntax_errors,

    "source_integrity": {
        "modified_active_sources":
            modified_sources,

        "active_sources_unchanged":
            not modified_sources,
    },

    "phase_boundaries": {
        "runtime_source_modified":
            False,

        "queue_job_created":
            False,

        "queue_runner_invoked":
            False,

        "worker_invoked":
            False,

        "article_reconstructed":
            False,

        "udare_store_populated":
            False,

        "integrity_validation_started":
            False,

        "article_validation_started":
            False,
    },

    "next_action":
        (
            "Add the UDARE worker handler and queue-safe "
            "execution adapter using the exact discovered "
            "engine and Raw HTML interfaces."
            if decision
            == "READY_FOR_PHASE_3_QUEUE_WORKER_PATCH"
            else
            "Resolve the listed Phase 3 integration blockers."
        ),
}


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
    "PHASE 3A — UDARE QUEUE AND "
    "WORKER INTEGRATION SCAN"
)
print("=" * 112)

print(
    "Active Python files scanned:",
    report[
        "counts"
    ][
        "active_python_files_scanned"
    ],
)

print(
    "Syntax errors in scanned runtime sources:",
    report[
        "counts"
    ][
        "syntax_errors"
    ],
)

print()
print("CORE FILES")

for name, result in (
    core_file_checks.items()
):
    print(
        f"  {name}:",
        (
            "FOUND"
            if result[
                "exists"
            ]
            else "MISSING"
        ),
    )

print()
print("QUEUE AND WORKER")

print(
    "  UDARE job type registered:",
    (
        "PASS"
        if checks[
            "udare_job_type_registered"
        ]
        else "FAIL"
    ),
)

print(
    "  Queue runner function:",
    (
        "FOUND"
        if checks[
            "queue_runner_function_found"
        ]
        else "NOT FOUND"
    ),
)

print(
    "  Worker executor function:",
    (
        "FOUND"
        if checks[
            "worker_executor_function_found"
        ]
        else "NOT FOUND"
    ),
)

print(
    "  Queue runner calls worker:",
    (
        "PASS"
        if checks[
            "queue_runner_calls_worker"
        ]
        else "FAIL"
    ),
)

print(
    "  Existing UDARE worker dispatch:",
    (
        "FOUND"
        if worker_has_udare_dispatch
        else "NOT FOUND"
    ),
)

print()
print("UDARE ENGINE CANDIDATES")

for candidate in (
    udare_engine_candidates[:30]
):
    print(
        "  -",
        (
            f"{candidate['path']}:"
            f"{candidate['line']} "
            f"{candidate['symbol_type']} "
            f"{candidate['name']}"
        ),
    )

print()
print("RAW HTML READER CANDIDATES")

for candidate in (
    raw_html_candidates[:30]
):
    print(
        "  -",
        (
            f"{candidate['path']}:"
            f"{candidate['line']} "
            f"{candidate['symbol_type']} "
            f"{candidate['name']}"
        ),
    )

print()
print("RUNTIME CONTROL CANDIDATES")

for candidate in (
    runtime_control_candidates[:40]
):
    print(
        "  -",
        (
            f"{candidate['path']}:"
            f"{candidate['line']} "
            f"{candidate['symbol_type']} "
            f"{candidate['name']} "
            f"{candidate['matched_tokens']}"
        ),
    )

print()
print("CHECKS")

for name, result in (
    checks.items()
):
    print(
        f"  {name}:",
        (
            "PASS"
            if result
            else "FAIL"
        ),
    )

print()
print(
    "Active source files modified:",
    len(
        modified_sources
    ),
)

print(
    "Report:",
    REPORT_PATH,
)

print()
print("=" * 112)
print(
    "PHASE 3A DECISION:",
    decision,
)
print("=" * 112)

if blocking_failures:
    print(
        "Blocking checks:",
        ", ".join(
            blocking_failures
        ),
    )

print(
    "No jobs were created or queued."
)

print(
    "No queue runner or worker was invoked."
)

print(
    "No article was reconstructed or stored."
)

raise SystemExit(
    0
    if decision
    == "READY_FOR_PHASE_3_QUEUE_WORKER_PATCH"
    else 1
)
