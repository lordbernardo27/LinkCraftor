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

REPORT_ROOT = (
    SERVER_ROOT
    / "data"
    / "runtime"
    / "udare_runtime_phase_2_scan"
)

REPORT_PATH = (
    REPORT_ROOT
    / "udare_runtime_phase_2_scan.json"
)


TARGET_FUNCTIONS = {
    "create_universal_knowledge_job",
    "create_pipeline_batch_jobs_v1",
    "update_job_status",
    "read_job_status",
    "read_queue",
    "record_job_failure",
    "run_universal_knowledge_queue_v1",
    "execute_universal_knowledge_job_v1",
    "inspect_queue",
    "inspect_workers",
    "retry_job",
    "move_to_dead_letter",
    "create_batch",
    "inspect_batch",
    "workspace_concurrency_decision",
}


REQUIRED_JOB_CONTRACT_FIELDS = (
    "job_id",
    "workspace_id",
    "user_id",
    "product_id",
    "pipeline",
    "stage",
    "payload",
    "payload_ref",
    "payload_reference",
    "priority",
    "status",
    "attempts",
    "attempt_count",
    "lease_owner",
    "progress",
    "au_usage",
    "cost_usage",
    "created_at",
    "started_at",
    "completed_at",
    "error",
    "error_info",
)


UDARE_TOKENS = (
    "udare_reconstruction",
    "udare_store",
    "universal_dom_article_reconstruction_engine_v1_7",
    "UDARE",
)


REGISTRY_NAME_PATTERNS = (
    "stage",
    "pipeline",
    "registry",
    "supported",
    "allowed",
    "canonical",
    "handler",
    "dispatcher",
    "route",
)


RUNTIME_PATH_HINTS = (
    "runtime",
    "orchestration",
    "orchestrator",
    "queue",
    "worker",
    "job",
    "batch",
    "pipeline",
)


EXCLUDED_NAME_FRAGMENTS = (
    ".before_",
    ".backup",
    "_backup_",
    ".phase1_backup_",
    "__pycache__",
)


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(
        value
    ).hexdigest()


def is_source_file(path: Path) -> bool:
    if path.suffix.casefold() != ".py":
        return False

    normalized = path.as_posix().casefold()

    return not any(
        fragment.casefold() in normalized
        for fragment in EXCLUDED_NAME_FRAGMENTS
    )


def source_files() -> List[Path]:
    return sorted(
        path
        for path in SERVER_ROOT.rglob("*.py")
        if is_source_file(path)
    )


def source_snapshot(
    paths: Iterable[Path],
) -> Dict[str, str]:
    return {
        path.relative_to(ROOT).as_posix():
            sha256_bytes(
                path.read_bytes()
            )

        for path in paths
    }


def relative(path: Path) -> str:
    return path.relative_to(
        ROOT
    ).as_posix()


def source_line(
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
    values: List[str] = []

    for child in ast.walk(node):
        if (
            isinstance(child, ast.Constant)
            and isinstance(child.value, str)
        ):
            values.append(
                child.value
            )

    return values


def assignment_names(
    node: ast.AST,
) -> List[str]:
    names: List[str] = []

    targets: List[ast.expr] = []

    if isinstance(node, ast.Assign):
        targets.extend(
            node.targets
        )

    elif isinstance(node, ast.AnnAssign):
        targets.append(
            node.target
        )

    for target in targets:
        if isinstance(target, ast.Name):
            names.append(
                target.id
            )

        elif isinstance(target, ast.Attribute):
            names.append(
                target.attr
            )

    return names


files = source_files()
before_snapshot = source_snapshot(
    files
)

function_locations: Dict[
    str,
    List[Dict[str, Any]],
] = defaultdict(list)

class_locations: List[Dict[str, Any]] = []
registry_candidates: List[Dict[str, Any]] = []
dispatch_candidates: List[Dict[str, Any]] = []
job_contract_hits: Dict[
    str,
    List[Dict[str, Any]],
] = defaultdict(list)

udare_references: Dict[
    str,
    List[Dict[str, Any]],
] = defaultdict(list)

import_candidates: List[Dict[str, Any]] = []
syntax_errors: List[Dict[str, Any]] = []

runtime_files: set[str] = set()


for path in files:
    path_text = relative(
        path
    )

    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    path_lower = (
        path_text.casefold()
    )

    if any(
        hint in path_lower
        for hint in RUNTIME_PATH_HINTS
    ):
        runtime_files.add(
            path_text
        )

    try:
        tree = ast.parse(
            source,
            filename=str(path),
        )

    except SyntaxError as exc:
        syntax_errors.append({
            "path":
                path_text,

            "line":
                exc.lineno,

            "message":
                exc.msg,
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
            if node.name in TARGET_FUNCTIONS:
                function_locations[
                    node.name
                ].append({
                    "path":
                        path_text,

                    "line":
                        node.lineno,

                    "signature_line":
                        source_line(
                            source,
                            node.lineno,
                        ),

                    "async":
                        isinstance(
                            node,
                            ast.AsyncFunctionDef,
                        ),
                })

            function_name_lower = (
                node.name.casefold()
            )

            if any(
                token in function_name_lower
                for token in (
                    "dispatch",
                    "execute",
                    "route",
                    "handler",
                    "worker",
                    "queue",
                )
            ):
                strings = literal_strings(
                    node
                )

                dispatch_candidates.append({
                    "path":
                        path_text,

                    "function":
                        node.name,

                    "line":
                        node.lineno,

                    "relevant_strings": [
                        value
                        for value in strings
                        if any(
                            token in value.casefold()
                            for token in (
                                "stage",
                                "pipeline",
                                "queue",
                                "worker",
                                "job",
                            )
                        )
                    ][:30],
                })

        elif isinstance(
            node,
            ast.ClassDef,
        ):
            class_name_lower = (
                node.name.casefold()
            )

            if any(
                token in class_name_lower
                for token in (
                    "job",
                    "runtime",
                    "queue",
                    "worker",
                    "pipeline",
                    "stage",
                )
            ):
                class_locations.append({
                    "path":
                        path_text,

                    "class":
                        node.name,

                    "line":
                        node.lineno,
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
                name_lower = (
                    name.casefold()
                )

                if any(
                    pattern in name_lower
                    for pattern in REGISTRY_NAME_PATTERNS
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

        elif isinstance(
            node,
            (
                ast.Import,
                ast.ImportFrom,
            ),
        ):
            rendered = ast.unparse(
                node
            )

            rendered_lower = (
                rendered.casefold()
            )

            if any(
                token in rendered_lower
                for token in (
                    "runtime",
                    "orchestration",
                    "queue",
                    "worker",
                    "job",
                    "pipeline",
                    "udare",
                )
            ):
                import_candidates.append({
                    "path":
                        path_text,

                    "line":
                        node.lineno,

                    "import":
                        rendered,
                })

    source_lower = source.casefold()

    for field in REQUIRED_JOB_CONTRACT_FIELDS:
        pattern = re.compile(
            rf"""(?x)
            ["']
            {re.escape(field)}
            ["']
            """
        )

        for match in pattern.finditer(
            source
        ):
            line_number = (
                source.count(
                    "\n",
                    0,
                    match.start(),
                )
                + 1
            )

            job_contract_hits[
                field
            ].append({
                "path":
                    path_text,

                "line":
                    line_number,

                "text":
                    source_line(
                        source,
                        line_number,
                    ),
            })

    for token in UDARE_TOKENS:
        token_lower = (
            token.casefold()
        )

        start = 0

        while True:
            index = source_lower.find(
                token_lower,
                start,
            )

            if index < 0:
                break

            line_number = (
                source.count(
                    "\n",
                    0,
                    index,
                )
                + 1
            )

            udare_references[
                token
            ].append({
                "path":
                    path_text,

                "line":
                    line_number,

                "text":
                    source_line(
                        source,
                        line_number,
                    ),
            })

            start = (
                index
                + len(token_lower)
            )


store_module = (
    SERVER_ROOT
    / "stores"
    / "udare_store.py"
)

store_module_check: Dict[str, Any] = {
    "exists":
        store_module.is_file(),

    "path":
        relative(store_module)
        if store_module.exists()
        else None,

    "required_exports":
        {},
}


required_store_exports = (
    "create_udare_store_v1",
    "persist_udare_article_document_v1",
    "load_udare_article_document_v1",
    "refresh_udare_store_manifest_v1",
    "verify_udare_store_v1",
)


if store_module.is_file():
    store_source = (
        store_module.read_text(
            encoding="utf-8-sig",
            errors="replace",
        )
    )

    for export_name in required_store_exports:
        store_module_check[
            "required_exports"
        ][
            export_name
        ] = bool(
            re.search(
                rf"\bdef\s+{re.escape(export_name)}\s*\(",
                store_source,
            )
        )


function_summary = {
    function_name: {
        "found":
            bool(
                function_locations.get(
                    function_name
                )
            ),

        "count":
            len(
                function_locations.get(
                    function_name,
                    [],
                )
            ),

        "locations":
            function_locations.get(
                function_name,
                [],
            ),
    }

    for function_name
    in sorted(
        TARGET_FUNCTIONS
    )
}


contract_summary = {
    field: {
        "found":
            bool(
                job_contract_hits.get(
                    field
                )
            ),

        "occurrences":
            len(
                job_contract_hits.get(
                    field,
                    [],
                )
            ),

        "sample_locations":
            job_contract_hits.get(
                field,
                [],
            )[:12],
    }

    for field
    in REQUIRED_JOB_CONTRACT_FIELDS
}


canonical_contract_groups = {
    "identity": [
        "job_id",
        "workspace_id",
        "user_id",
        "product_id",
    ],

    "routing": [
        "pipeline",
        "stage",
        "priority",
        "status",
    ],

    "payload": [
        "payload",
        "payload_ref",
        "payload_reference",
    ],

    "execution": [
        "attempts",
        "attempt_count",
        "lease_owner",
        "progress",
    ],

    "usage": [
        "au_usage",
        "cost_usage",
    ],

    "timestamps": [
        "created_at",
        "started_at",
        "completed_at",
    ],

    "errors": [
        "error",
        "error_info",
    ],
}


contract_group_results: Dict[
    str,
    Dict[str, Any],
] = {}

for group_name, fields in (
    canonical_contract_groups.items()
):
    present_fields = [
        field
        for field in fields
        if contract_summary[
            field
        ][
            "found"
        ]
    ]

    contract_group_results[
        group_name
    ] = {
        "expected_fields":
            fields,

        "present_fields":
            present_fields,

        "any_present":
            bool(
                present_fields
            ),
    }


udare_reference_summary = {
    token: {
        "count":
            len(
                udare_references.get(
                    token,
                    [],
                )
            ),

        "locations":
            udare_references.get(
                token,
                [],
            )[:40],
    }

    for token
    in UDARE_TOKENS
}


create_job_found = (
    function_summary[
        "create_universal_knowledge_job"
    ][
        "found"
    ]
)

status_update_found = (
    function_summary[
        "update_job_status"
    ][
        "found"
    ]
)

status_read_found = (
    function_summary[
        "read_job_status"
    ][
        "found"
    ]
)

queue_runner_found = (
    function_summary[
        "run_universal_knowledge_queue_v1"
    ][
        "found"
    ]
)

worker_executor_found = (
    function_summary[
        "execute_universal_knowledge_job_v1"
    ][
        "found"
    ]
)

store_exports_complete = (
    store_module_check[
        "exists"
    ]
    and all(
        store_module_check[
            "required_exports"
        ].values()
    )
)

stage_registry_candidates_found = bool(
    registry_candidates
)

job_contract_routing_found = (
    contract_group_results[
        "routing"
    ][
        "any_present"
    ]
)

job_contract_identity_found = (
    contract_group_results[
        "identity"
    ][
        "any_present"
    ]
)


readiness_checks = {
    "universal_job_creator_found":
        create_job_found,

    "job_status_update_found":
        status_update_found,

    "job_status_read_found":
        status_read_found,

    "existing_queue_runner_found":
        queue_runner_found,

    "existing_worker_executor_found":
        worker_executor_found,

    "stage_or_pipeline_registry_candidates_found":
        stage_registry_candidates_found,

    "job_contract_identity_fields_found":
        job_contract_identity_found,

    "job_contract_routing_fields_found":
        job_contract_routing_found,

    "udare_store_module_exists":
        store_module_check[
            "exists"
        ],

    "udare_store_exports_complete":
        store_exports_complete,

    "python_source_syntax_clean":
        not syntax_errors,
}


blocking_checks = (
    "universal_job_creator_found",
    "job_status_update_found",
    "job_status_read_found",
    "job_contract_identity_fields_found",
    "job_contract_routing_fields_found",
    "udare_store_module_exists",
    "udare_store_exports_complete",
    "python_source_syntax_clean",
)


blocked_reasons = [
    check_name
    for check_name in blocking_checks
    if not readiness_checks[
        check_name
    ]
]


decision = (
    "READY_FOR_PHASE_2_RUNTIME_PATCH"
    if not blocked_reasons
    else "BLOCKED"
)


after_snapshot = source_snapshot(
    files
)

changed_source_files = sorted(
    path
    for path in set(
        before_snapshot
    )
    | set(
        after_snapshot
    )
    if before_snapshot.get(
        path
    )
    != after_snapshot.get(
        path
    )
)


report = {
    "schema_version":
        "udare_runtime_phase_2_scan_v1",

    "generated_at_utc":
        utc_now(),

    "workspace_id":
        "ws_whattoexpect_com",

    "requested_stage":
        "udare_reconstruction",

    "requested_pipeline":
        "website_reconstruction",

    "requested_engine":
        "universal_dom_article_reconstruction_engine_v1_7",

    "scope":
        "Phase 2 runtime integration discovery only",

    "decision":
        decision,

    "blocked_reasons":
        blocked_reasons,

    "counts": {
        "python_files_scanned":
            len(
                files
            ),

        "runtime_related_files":
            len(
                runtime_files
            ),

        "syntax_errors":
            len(
                syntax_errors
            ),

        "registry_candidates":
            len(
                registry_candidates
            ),

        "dispatch_candidates":
            len(
                dispatch_candidates
            ),

        "class_candidates":
            len(
                class_locations
            ),

        "changed_source_files":
            len(
                changed_source_files
            ),
    },

    "readiness_checks":
        readiness_checks,

    "target_functions":
        function_summary,

    "job_contract": {
        "fields":
            contract_summary,

        "groups":
            contract_group_results,
    },

    "stage_registry_candidates":
        registry_candidates[:100],

    "dispatch_candidates":
        dispatch_candidates[:100],

    "runtime_classes":
        class_locations[:100],

    "relevant_imports":
        import_candidates[:200],

    "udare_references":
        udare_reference_summary,

    "udare_store":
        store_module_check,

    "runtime_files":
        sorted(
            runtime_files
        ),

    "syntax_errors":
        syntax_errors,

    "source_integrity": {
        "source_files_modified":
            changed_source_files,

        "source_files_unchanged":
            not changed_source_files,
    },

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
            "Patch the exact discovered universal job contract "
            "and stage registry to register udare_reconstruction."
            if decision
            == "READY_FOR_PHASE_2_RUNTIME_PATCH"
            else
            "Resolve the listed blocking runtime integration points."
        ),
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
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 112)
print(
    "PHASE 2A — UDARE UNIVERSAL "
    "RUNTIME INTEGRATION SCAN"
)
print("=" * 112)

print(
    "Python files scanned:",
    report[
        "counts"
    ][
        "python_files_scanned"
    ],
)

print(
    "Runtime-related files:",
    report[
        "counts"
    ][
        "runtime_related_files"
    ],
)

print(
    "Syntax errors:",
    report[
        "counts"
    ][
        "syntax_errors"
    ],
)

print()
print("CORE RUNTIME FUNCTIONS")

for function_name in (
    "create_universal_knowledge_job",
    "update_job_status",
    "read_job_status",
    "run_universal_knowledge_queue_v1",
    "execute_universal_knowledge_job_v1",
    "create_pipeline_batch_jobs_v1",
):
    result = function_summary[
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
print("UDARE STORE")

print(
    "  Module exists:",
    (
        "PASS"
        if store_module_check[
            "exists"
        ]
        else "FAIL"
    ),
)

for export_name, found in (
    store_module_check[
        "required_exports"
    ].items()
):
    print(
        f"  {export_name}:",
        (
            "FOUND"
            if found
            else "NOT FOUND"
        ),
    )

print()
print(
    "Stage/pipeline registry candidates:",
    len(
        registry_candidates
    ),
)

for candidate in registry_candidates[:20]:
    print(
        "  -",
        (
            f"{candidate['path']}:"
            f"{candidate['line']} "
            f"{candidate['name']}"
        ),
    )

print()
print("EXISTING UDARE REFERENCES")

for token in UDARE_TOKENS:
    print(
        f"  {token}:",
        udare_reference_summary[
            token
        ][
            "count"
        ],
    )

print()
print("READINESS CHECKS")

for check_name, passed in (
    readiness_checks.items()
):
    print(
        f"  {check_name}:",
        (
            "PASS"
            if passed
            else "FAIL"
        ),
    )

print()
print(
    "Source files modified by scan:",
    len(
        changed_source_files
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
    decision,
)
print("=" * 112)

if blocked_reasons:
    print(
        "Blocking checks:",
        ", ".join(
            blocked_reasons
        ),
    )

print(
    "No runtime jobs, queues, workers, batches "
    "or article population were started."
)

raise SystemExit(
    0
    if decision
    == "READY_FOR_PHASE_2_RUNTIME_PATCH"
    else 1
)
