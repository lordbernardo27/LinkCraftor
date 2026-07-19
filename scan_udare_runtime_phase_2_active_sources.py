from __future__ import annotations

import ast
import hashlib
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
    / "udare_runtime_phase_2_scan"
    / "udare_runtime_phase_2_active_source_scan.json"
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
    ".phase1_backup_",
    ".before_format_fix_",
    ".before_line76_repair_",
)


CORE_RUNTIME_FILES = (
    "backend/server/jobs/universal_knowledge_orchestrator.py",
    "backend/server/workers/universal_knowledge_queue_runner.py",
    "backend/server/workers/universal_knowledge_worker.py",
    "backend/server/orchestration/job_store.py",
    "backend/server/stores/udare_store.py",
)


CORE_FUNCTIONS = {
    "create_universal_knowledge_job",
    "update_job_status",
    "read_job_status",
    "create_pipeline_batch_jobs_v1",
    "run_universal_knowledge_queue_v1",
    "execute_universal_knowledge_job_v1",
}


REQUIRED_STORE_FUNCTIONS = {
    "create_udare_store_v1",
    "persist_udare_article_document_v1",
    "load_udare_article_document_v1",
    "refresh_udare_store_manifest_v1",
    "verify_udare_store_v1",
}


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(
        value
    ).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(
        ROOT
    ).as_posix()


def is_active_source(path: Path) -> bool:
    if path.suffix.casefold() != ".py":
        return False

    try:
        relative_parts = path.relative_to(
            SERVER_ROOT
        ).parts
    except ValueError:
        return False

    if any(
        part.casefold()
        in EXCLUDED_DIRECTORY_NAMES
        for part in relative_parts[:-1]
    ):
        return False

    filename = path.name.casefold()

    if any(
        fragment.casefold() in filename
        for fragment in EXCLUDED_FILENAME_FRAGMENTS
    ):
        return False

    return True


active_files = sorted(
    path
    for path in SERVER_ROOT.rglob("*.py")
    if is_active_source(path)
)


before_hashes = {
    relative(path):
        sha256_bytes(
            path.read_bytes()
        )
    for path in active_files
}


syntax_errors: List[Dict[str, Any]] = []
function_locations: Dict[
    str,
    List[Dict[str, Any]],
] = {
    name: []
    for name in (
        CORE_FUNCTIONS
        | REQUIRED_STORE_FUNCTIONS
    )
}


for path in active_files:
    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    try:
        tree = ast.parse(
            source,
            filename=str(path),
        )

    except SyntaxError as exc:
        syntax_errors.append({
            "path":
                relative(path),

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

    for node in ast.walk(tree):
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            if node.name in function_locations:
                function_locations[
                    node.name
                ].append({
                    "path":
                        relative(path),

                    "line":
                        node.lineno,
                })


core_file_results: Dict[str, Any] = {}

for file_name in CORE_RUNTIME_FILES:
    path = ROOT / file_name

    core_file_results[
        file_name
    ] = {
        "exists":
            path.is_file(),

        "active_source":
            (
                path.is_file()
                and is_active_source(path)
            ),
    }


function_results = {
    name: {
        "found":
            bool(
                function_locations[
                    name
                ]
            ),

        "locations":
            function_locations[
                name
            ],
    }
    for name in sorted(
        function_locations
    )
}


required_checks = {
    "active_orchestrator_exists":
        core_file_results[
            "backend/server/jobs/universal_knowledge_orchestrator.py"
        ][
            "exists"
        ],

    "active_queue_runner_exists":
        core_file_results[
            "backend/server/workers/universal_knowledge_queue_runner.py"
        ][
            "exists"
        ],

    "active_worker_exists":
        core_file_results[
            "backend/server/workers/universal_knowledge_worker.py"
        ][
            "exists"
        ],

    "active_job_store_exists":
        core_file_results[
            "backend/server/orchestration/job_store.py"
        ][
            "exists"
        ],

    "udare_store_exists":
        core_file_results[
            "backend/server/stores/udare_store.py"
        ][
            "exists"
        ],

    "active_sources_syntax_clean":
        not syntax_errors,

    "universal_job_creator_found":
        function_results[
            "create_universal_knowledge_job"
        ][
            "found"
        ],

    "job_status_update_found":
        function_results[
            "update_job_status"
        ][
            "found"
        ],

    "job_status_reader_found":
        function_results[
            "read_job_status"
        ][
            "found"
        ],

    "batch_job_creator_found":
        function_results[
            "create_pipeline_batch_jobs_v1"
        ][
            "found"
        ],

    "queue_runner_found":
        function_results[
            "run_universal_knowledge_queue_v1"
        ][
            "found"
        ],

    "active_worker_executor_found":
        any(
            item[
                "path"
            ]
            == (
                "backend/server/workers/"
                "universal_knowledge_worker.py"
            )
            for item in function_results[
                "execute_universal_knowledge_job_v1"
            ][
                "locations"
            ]
        ),

    "udare_store_exports_complete":
        all(
            function_results[
                name
            ][
                "found"
            ]
            for name in REQUIRED_STORE_FUNCTIONS
        ),
}


after_hashes = {
    relative(path):
        sha256_bytes(
            path.read_bytes()
        )
    for path in active_files
}


changed_files = sorted(
    path
    for path in set(
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


required_checks[
    "scan_modified_no_active_sources"
] = not changed_files


passed = all(
    required_checks.values()
)


report = {
    "schema_version":
        "udare_runtime_phase_2_active_source_scan_v1",

    "generated_at_utc":
        utc_now(),

    "workspace_id":
        "ws_whattoexpect_com",

    "stage_to_register":
        "udare_reconstruction",

    "pipeline_to_register":
        "website_reconstruction",

    "scope":
        "Active production runtime source only",

    "excluded_locations": [
        "backend/server/data/**",
        "backend/server/_quarantine/**",
        "**/runtime_backups/**",
        "**/backups/**",
        "backup and before-edit Python files",
    ],

    "active_python_files_scanned":
        len(
            active_files
        ),

    "core_files":
        core_file_results,

    "functions":
        function_results,

    "syntax_errors":
        syntax_errors,

    "checks":
        required_checks,

    "active_source_files_modified":
        changed_files,

    "decision":
        (
            "READY_FOR_PHASE_2_RUNTIME_PATCH"
            if passed
            else "BLOCKED"
        ),

    "phase_boundaries": {
        "runtime_source_modified":
            False,

        "job_created":
            False,

        "queue_created":
            False,

        "worker_created":
            False,

        "batch_created":
            False,

        "udare_store_populated":
            False,
    },
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
    "PHASE 2A — ACTIVE RUNTIME "
    "SOURCE SCAN"
)
print("=" * 112)

print(
    "Active Python files scanned:",
    len(
        active_files
    ),
)

print(
    "Inactive data/backup/quarantine "
    "trees excluded: YES"
)

print(
    "Active-source syntax errors:",
    len(
        syntax_errors
    ),
)

for error in syntax_errors:
    print(
        "  -",
        (
            f"{error['path']}:"
            f"{error['line']}:"
            f"{error['offset']} "
            f"{error['message']}"
        ),
    )

print()
print("REQUIRED RUNTIME FUNCTIONS")

for function_name in sorted(
    CORE_FUNCTIONS
):
    result = function_results[
        function_name
    ]

    print(
        f"  {function_name}:",
        (
            "FOUND"
            if result[
                "found"
            ]
            else "NOT FOUND"
        ),
    )

    for location in result[
        "locations"
    ]:
        print(
            "    -",
            (
                f"{location['path']}:"
                f"{location['line']}"
            ),
        )

print()
print("UDARE STORE EXPORTS")

for function_name in sorted(
    REQUIRED_STORE_FUNCTIONS
):
    print(
        f"  {function_name}:",
        (
            "FOUND"
            if function_results[
                function_name
            ][
                "found"
            ]
            else "NOT FOUND"
        ),
    )

print()
print("CHECKS")

for name, result in (
    required_checks.items()
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
        changed_files
    ),
)

print(
    "Report:",
    REPORT_PATH,
)

print()
print("=" * 112)
print(
    "PHASE 2A DECISION:",
    report[
        "decision"
    ],
)
print("=" * 112)

print(
    "No runtime jobs, queues, workers, "
    "batches or article population were started."
)

raise SystemExit(
    0
    if passed
    else 1
)
