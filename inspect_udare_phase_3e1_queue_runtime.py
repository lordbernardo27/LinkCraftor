from __future__ import annotations

import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parent
SERVER_ROOT = ROOT / "backend" / "server"

REPORT_PATH = (
    SERVER_ROOT
    / "data"
    / "runtime"
    / "udare_phase_3e1_queue_runtime_inspection"
    / "udare_phase_3e1_queue_runtime_inspection.json"
)


FILES = {
    "queue_runner":
        SERVER_ROOT
        / "workers"
        / "universal_knowledge_queue_runner.py",

    "universal_worker":
        SERVER_ROOT
        / "workers"
        / "universal_knowledge_worker.py",

    "udare_worker":
        SERVER_ROOT
        / "workers"
        / "udare_reconstruction_worker.py",

    "orchestrator":
        SERVER_ROOT
        / "jobs"
        / "universal_knowledge_orchestrator.py",

    "runtime":
        SERVER_ROOT
        / "runtime"
        / "universal_runtime_infrastructure.py",

    "udare_contract":
        SERVER_ROOT
        / "runtime"
        / "udare_runtime_contract.py",
}


TARGET_FUNCTIONS = {
    "queue_runner": (
        "run_universal_knowledge_queue_v1",
    ),

    "universal_worker": (
        "execute_universal_knowledge_job_v1",
        "_execute_universal_knowledge_job_without_udare_v1",
    ),

    "udare_worker": (
        "run_udare_reconstruction_job_v1",
    ),

    "orchestrator": (
        "create_universal_knowledge_job",
        "update_job_status",
        "update_job_progress",
        "read_job_status",
        "read_job_progress",
        "read_queue",
        "record_job_failure",
    ),

    "runtime": (
        "retry_job",
        "move_to_dead_letter",
        "workspace_concurrency_decision",
    ),

    "udare_contract": (
        "create_udare_reconstruction_job_v1",
        "build_udare_runtime_payload_v1",
    ),
}


CAPABILITY_TOKENS = {
    "queue_reads_persisted_queue": (
        "read_queue",
        "queue_path",
    ),

    "queue_calls_universal_worker": (
        "execute_universal_knowledge_job_v1",
    ),

    "priority_handling": (
        "priority",
        "sorted",
    ),

    "lease_owner_handling": (
        "lease_owner",
        "lease",
    ),

    "attempt_tracking": (
        "attempt_count",
        "attempts",
    ),

    "max_attempt_enforcement": (
        "max_attempts",
    ),

    "retry_integration": (
        "retry_job",
    ),

    "dead_letter_integration": (
        "move_to_dead_letter",
        "dead_letter",
    ),

    "workspace_concurrency": (
        "workspace_concurrency_decision",
        "max_running",
    ),

    "resume_or_recovery": (
        "resume",
        "recover",
        "requeue",
        "stale",
        "interrupted",
    ),

    "running_status": (
        '"running"',
        "'running'",
    ),

    "completed_status": (
        '"completed"',
        "'completed'",
    ),

    "failed_status": (
        '"failed"',
        "'failed'",
    ),

    "progress_updates": (
        "update_job_progress",
    ),
}


RETRY_ENVELOPE_FIELDS = (
    "user_id",
    "product_id",
    "pipeline",
    "stage",
    "payload_ref",
    "priority",
    "parent_job_id",
    "batch_id",
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


def sha256_file(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


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


def extract_function(
    *,
    source: str,
    tree: ast.Module,
    name: str,
) -> Dict[str, Any] | None:
    for node in tree.body:
        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        if node.name != name:
            continue

        return {
            "name":
                name,

            "line":
                node.lineno,

            "end_line":
                node.end_lineno,

            "signature":
                function_signature(
                    node
                ),

            "source":
                ast.get_source_segment(
                    source,
                    node,
                )
                or "",
        }

    return None


before_hashes = {
    name:
        sha256_file(
            path
        )
        if path.is_file()
        else ""

    for name, path
    in FILES.items()
}


report: Dict[str, Any] = {
    "schema_version":
        "udare_phase_3e1_queue_runtime_inspection_v1",

    "generated_at_utc":
        utc_now(),

    "workspace_id":
        "ws_whattoexpect_com",

    "phase":
        "Phase 3E1",

    "files":
        {},

    "functions":
        {},

    "missing_files":
        [],

    "missing_functions":
        [],

    "syntax_errors":
        [],

    "capabilities":
        {},

    "gaps":
        [],

    "phase_boundaries": {
        "source_modified":
            False,

        "job_created":
            False,

        "job_queued":
            False,

        "queue_runner_invoked":
            False,

        "worker_invoked":
            False,

        "reconstruction_invoked":
            False,

        "udare_store_write":
            False,
    },
}


sources: Dict[str, str] = {}


for file_name, path in FILES.items():
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

    sources[
        file_name
    ] = source

    report[
        "files"
    ][
        file_name
    ] = {
        "path":
            relative(
                path
            ),

        "sha256":
            before_hashes[
                file_name
            ],

        "byte_length":
            len(
                path.read_bytes()
            ),
    }

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

    for function_name in TARGET_FUNCTIONS[
        file_name
    ]:
        function = extract_function(
            source=
                source,

            tree=
                tree,

            name=
                function_name,
        )

        key = (
            file_name
            + "."
            + function_name
        )

        if function is None:
            report[
                "missing_functions"
            ].append(
                key
            )

        else:
            report[
                "functions"
            ][
                key
            ] = function


queue_source = (
    report[
        "functions"
    ].get(
        "queue_runner."
        "run_universal_knowledge_queue_v1",
        {},
    ).get(
        "source",
        "",
    )
)


retry_source = (
    report[
        "functions"
    ].get(
        "runtime.retry_job",
        {},
    ).get(
        "source",
        "",
    )
)


dead_letter_source = (
    report[
        "functions"
    ].get(
        "runtime.move_to_dead_letter",
        {},
    ).get(
        "source",
        "",
    )
)


udare_worker_source = (
    report[
        "functions"
    ].get(
        "udare_worker."
        "run_udare_reconstruction_job_v1",
        {},
    ).get(
        "source",
        "",
    )
)


combined_runtime_source = "\n".join(
    (
        queue_source,
        retry_source,
        dead_letter_source,
        udare_worker_source,
    )
)


for capability, tokens in (
    CAPABILITY_TOKENS.items()
):
    matching_tokens = [
        token

        for token
        in tokens

        if token
        in combined_runtime_source
    ]

    report[
        "capabilities"
    ][
        capability
    ] = {
        "present":
            bool(
                matching_tokens
            ),

        "matched_tokens":
            matching_tokens,
    }


queue_specific_checks = {
    "reads_queue":
        any(
            token in queue_source
            for token in (
                "read_queue",
                "queue_path",
            )
        ),

    "calls_worker":
        "execute_universal_knowledge_job_v1"
        in queue_source,

    "checks_job_status":
        any(
            token in queue_source
            for token in (
                "read_job_status",
                'get("status")',
                "get('status')",
            )
        ),

    "skips_completed_jobs":
        (
            "completed"
            in queue_source
            and any(
                token in queue_source
                for token in (
                    "continue",
                    "skip",
                    "terminal",
                )
            )
        ),

    "sets_running_status":
        (
            "running"
            in queue_source
            and "update_job_status"
            in queue_source
        ),

    "handles_exceptions":
        (
            "except"
            in queue_source
        ),

    "integrates_retry":
        "retry_job"
        in queue_source,

    "integrates_dead_letter":
        (
            "move_to_dead_letter"
            in queue_source
            or "dead_letter"
            in queue_source
        ),

    "uses_workspace_concurrency":
        "workspace_concurrency_decision"
        in queue_source,

    "uses_lease_owner":
        "lease_owner"
        in queue_source,

    "sorts_by_priority":
        (
            "priority"
            in queue_source
            and "sorted"
            in queue_source
        ),

    "supports_resume":
        any(
            token in queue_source.casefold()
            for token in (
                "resume",
                "recover",
                "requeue",
                "stale",
                "interrupted",
            )
        ),
}


report[
    "queue_specific_checks"
] = queue_specific_checks


retry_field_checks = {
    field:
        field
        in retry_source

    for field
    in RETRY_ENVELOPE_FIELDS
}


retry_semantics = {
    "increments_attempts":
        (
            "attempts"
            in retry_source
            and "+ 1"
            in retry_source
        ),

    "enforces_max_attempts":
        "max_attempts"
        in retry_source,

    "calls_job_creator":
        "create_universal_knowledge_job"
        in retry_source,

    "moves_to_dead_letter":
        "move_to_dead_letter"
        in retry_source,

    "persists_retry_attempt_in_payload":
        (
            "retry_attempt"
            in retry_source
        ),

    "persists_attempt_count_in_created_job":
        (
            "attempt_count="
            in retry_source
            or '"attempt_count"'
            in retry_source
        ),

    "preserves_complete_envelope":
        all(
            retry_field_checks.values()
        ),
}


report[
    "retry_field_checks"
] = retry_field_checks

report[
    "retry_semantics"
] = retry_semantics


dead_letter_semantics = {
    "writes_dead_letter_record":
        (
            "write_json"
            in dead_letter_source
        ),

    "marks_job_dead_letter":
        (
            "dead_letter"
            in dead_letter_source
            and "update_job_status"
            in dead_letter_source
        ),

    "records_reason":
        "reason"
        in dead_letter_source,

    "preserves_original_job":
        '"job"'
        in dead_letter_source
        or "'job'"
        in dead_letter_source,
}


report[
    "dead_letter_semantics"
] = dead_letter_semantics


required_core_checks = {
    "all_files_exist":
        not report[
            "missing_files"
        ],

    "all_functions_found":
        not report[
            "missing_functions"
        ],

    "all_sources_syntax_clean":
        not report[
            "syntax_errors"
        ],

    "queue_reads_queue":
        queue_specific_checks[
            "reads_queue"
        ],

    "queue_calls_worker":
        queue_specific_checks[
            "calls_worker"
        ],

    "udare_worker_connected":
        "run_udare_reconstruction_job_v1"
        in sources.get(
            "universal_worker",
            "",
        ),

    "retry_function_available":
        bool(
            retry_source
        ),

    "dead_letter_function_available":
        bool(
            dead_letter_source
        ),
}


report[
    "required_core_checks"
] = required_core_checks


if not queue_specific_checks[
    "uses_lease_owner"
]:
    report[
        "gaps"
    ].append(
        "queue_runner_has_no_lease_owner_claim"
    )

if not queue_specific_checks[
    "sorts_by_priority"
]:
    report[
        "gaps"
    ].append(
        "queue_runner_has_no_verified_priority_ordering"
    )

if not queue_specific_checks[
    "uses_workspace_concurrency"
]:
    report[
        "gaps"
    ].append(
        "queue_runner_has_no_workspace_concurrency_gate"
    )

if not queue_specific_checks[
    "integrates_retry"
]:
    report[
        "gaps"
    ].append(
        "queue_runner_does_not_call_retry_manager"
    )

if not queue_specific_checks[
    "integrates_dead_letter"
]:
    report[
        "gaps"
    ].append(
        "queue_runner_does_not_call_dead_letter_manager"
    )

if not queue_specific_checks[
    "supports_resume"
]:
    report[
        "gaps"
    ].append(
        "queue_runner_has_no_verified_resume_or_stale_job_recovery"
    )

if not retry_semantics[
    "preserves_complete_envelope"
]:
    report[
        "gaps"
    ].append(
        "retry_job_does_not_preserve_complete_universal_envelope"
    )

if not retry_semantics[
    "persists_attempt_count_in_created_job"
]:
    report[
        "gaps"
    ].append(
        "retry_attempt_count_not_verified_in_persisted_retry_job"
    )


after_hashes = {
    name:
        sha256_file(
            path
        )
        if path.is_file()
        else ""

    for name, path
    in FILES.items()
}


modified_sources = [
    relative(
        FILES[
            name
        ]
    )

    for name
    in FILES

    if before_hashes.get(
        name
    )
    != after_hashes.get(
        name
    )
]


report[
    "source_integrity"
] = {
    "modified_sources":
        modified_sources,

    "all_sources_unchanged":
        not modified_sources,
}


core_failures = [
    name

    for name, passed
    in required_core_checks.items()

    if not passed
]


if modified_sources:
    core_failures.append(
        "source_integrity"
    )


report[
    "blocking_failures"
] = core_failures

report[
    "decision"
] = (
    "READY_FOR_PHASE_3E_RUNTIME_PATCH"
    if not core_failures
    else "BLOCKED"
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
    "PHASE 3E1 — QUEUE, RETRY, "
    "DLQ AND RESUME INSPECTION"
)
print("=" * 112)


print()
print("CORE CHECKS")

for name, passed in (
    required_core_checks.items()
):
    print(
        f"  {name}:",
        (
            "PASS"
            if passed
            else "FAIL"
        ),
    )


print()
print("QUEUE-RUNNER CHECKS")

for name, passed in (
    queue_specific_checks.items()
):
    print(
        f"  {name}:",
        (
            "FOUND"
            if passed
            else "NOT FOUND"
        ),
    )


print()
print("RETRY SEMANTICS")

for name, passed in (
    retry_semantics.items()
):
    print(
        f"  {name}:",
        (
            "FOUND"
            if passed
            else "NOT FOUND"
        ),
    )


print()
print("DEAD-LETTER SEMANTICS")

for name, passed in (
    dead_letter_semantics.items()
):
    print(
        f"  {name}:",
        (
            "FOUND"
            if passed
            else "NOT FOUND"
        ),
    )


print()
print("IDENTIFIED GAPS")

if report[
    "gaps"
]:
    for gap in report[
        "gaps"
    ]:
        print(
            "  -",
            gap,
        )

else:
    print(
        "  None"
    )


print()
print(
    "Source files modified:",
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
    "PHASE 3E1 DECISION:",
    report[
        "decision"
    ],
)
print("=" * 112)

print(
    "No job was created or queued."
)

print(
    "No queue runner or worker was invoked."
)

print(
    "No article was reconstructed or stored."
)

raise SystemExit(
    0
    if report[
        "decision"
    ]
    == "READY_FOR_PHASE_3E_RUNTIME_PATCH"
    else 1
)
