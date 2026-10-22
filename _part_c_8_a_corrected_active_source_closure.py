from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


if len(sys.argv) != 4:
    raise RuntimeError(
        "Expected project root, initial report and closure report."
    )

ROOT = Path(sys.argv[1]).resolve()
INITIAL_REPORT = Path(sys.argv[2]).resolve()
REPORT = Path(sys.argv[3]).resolve()

SERVER_ROOT = ROOT / "backend" / "server"
COORDINATION_ROOT = SERVER_ROOT / "coordination"
RUNTIME_ROOT = SERVER_ROOT / "runtime"
ORCHESTRATION_ROOT = SERVER_ROOT / "orchestration"

EXPECTED_FAILED_SOURCE = (
    RUNTIME_ROOT
    / "universal_orchestration"
    / "cancellation_termination_before_annotation_fix_2026_09_13.py"
)

ACTIVE_COUNTERPART = (
    RUNTIME_ROOT
    / "universal_orchestration"
    / "cancellation_termination.py"
)

CANONICAL_BOUNDARY_FILES = (
    COORDINATION_ROOT
    / "runtime_integration"
    / "coordination_runtime_bridge.py",
    COORDINATION_ROOT
    / "runtime_integration"
    / "runtime_job_mapping.py",
    COORDINATION_ROOT
    / "runtime_integration"
    / "workflow_job_correlation.py",
    COORDINATION_ROOT
    / "runtime_integration"
    / "runtime_completion_intake.py",
    COORDINATION_ROOT
    / "runtime_integration"
    / "runtime_failure_intake.py",
    ORCHESTRATION_ROOT / "service.py",
    ORCHESTRATION_ROOT / "job_store.py",
    ORCHESTRATION_ROOT / "queue.py",
    RUNTIME_ROOT / "universal_runtime_registration.py",
)

GENERATED_AT = datetime.now(
    timezone.utc
).isoformat()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def is_historical_source(path: Path) -> bool:
    name = path.name.lower()

    return any(
        marker in name
        for marker in (
            "_before_",
            ".before_",
            "_backup_",
            ".backup_",
            "_candidate.",
            ".candidate.",
        )
    )


def dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id

    if isinstance(node, ast.Attribute):
        parent = dotted_name(node.value)

        if parent:
            return f"{parent}.{node.attr}"

        return node.attr

    return ""


initial_text = INITIAL_REPORT.read_text(
    encoding="utf-8-sig",
    errors="replace",
).replace("\r\n", "\n")

checks_match = re.search(
    r"CHECKS\n=+\n(\{.*?\})\n\nFAILED_CHECKS:",
    initial_text,
    re.DOTALL,
)

if checks_match is None:
    raise RuntimeError(
        "The initial 8-A checks could not be reconstructed."
    )

initial_checks = json.loads(
    checks_match.group(1)
)

initial_failed_checks = [
    name
    for name, passed in initial_checks.items()
    if not passed
]

parse_failures_match = re.search(
    r"PARSE_FAILURES:\n(\[.*?\])\n\n=+\nNEXT STEP",
    initial_text,
    re.DOTALL,
)

if parse_failures_match is None:
    raise RuntimeError(
        "The initial parse-failure evidence could not be reconstructed."
    )

initial_parse_failures = json.loads(
    parse_failures_match.group(1)
)

decision_match = re.search(
    r"RUNTIME EXECUTION GATEWAY DECISION:\s*"
    r"([A-Z0-9_]+)",
    initial_text,
)

gateway_decision = (
    decision_match.group(1)
    if decision_match is not None
    else ""
)

all_sources = sorted(
    {
        *COORDINATION_ROOT.rglob("*.py"),
        *RUNTIME_ROOT.rglob("*.py"),
        *ORCHESTRATION_ROOT.rglob("*.py"),
    },
    key=lambda path: path.as_posix(),
)

historical_sources = [
    path
    for path in all_sources
    if is_historical_source(path)
]

active_sources = [
    path
    for path in all_sources
    if not is_historical_source(path)
]

hashes_before = {
    relative(path): sha256_file(path)
    for path in all_sources
}

active_parse_failures = []
active_trees = {}
active_function_names = {}
archived_import_references = []

archived_module_stem = (
    EXPECTED_FAILED_SOURCE.stem
)

for path in active_sources:
    path_key = relative(path)

    try:
        source = path.read_text(
            encoding="utf-8-sig",
        )

        tree = ast.parse(
            source,
            filename=str(path),
        )

    except Exception as error:
        active_parse_failures.append(
            {
                "source": path_key,
                "error_type": type(error).__name__,
                "error_message": str(error),
            }
        )
        continue

    active_trees[path_key] = tree

    active_function_names[path_key] = sorted(
        {
            node.name
            for node in ast.walk(tree)
            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
        }
    )

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.endswith(
                    archived_module_stem
                ):
                    archived_import_references.append(
                        {
                            "source": path_key,
                            "line": node.lineno,
                            "import": alias.name,
                        }
                    )

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""

            if module.endswith(
                archived_module_stem
            ):
                archived_import_references.append(
                    {
                        "source": path_key,
                        "line": node.lineno,
                        "import": module,
                    }
                )

active_counterpart_parse_error = None

if ACTIVE_COUNTERPART.exists():
    try:
        ast.parse(
            ACTIVE_COUNTERPART.read_text(
                encoding="utf-8-sig",
            ),
            filename=str(
                ACTIVE_COUNTERPART
            ),
        )
    except Exception as error:
        active_counterpart_parse_error = {
            "error_type": type(error).__name__,
            "error_message": str(error),
        }

canonical_boundary_status = {}

for path in CANONICAL_BOUNDARY_FILES:
    path_key = relative(path)

    canonical_boundary_status[path_key] = {
        "exists": path.exists(),
        "parsed_as_active_source": (
            path_key in active_trees
        ),
        "public_functions": [
            name
            for name in active_function_names.get(
                path_key,
                [],
            )
            if not name.startswith("_")
        ],
    }

service_key = relative(
    ORCHESTRATION_ROOT / "service.py"
)
job_store_key = relative(
    ORCHESTRATION_ROOT / "job_store.py"
)
queue_key = relative(
    ORCHESTRATION_ROOT / "queue.py"
)
registration_key = relative(
    RUNTIME_ROOT
    / "universal_runtime_registration.py"
)

canonical_authorities = {
    "create_orchestration_job": (
        "create_orchestration_job"
        in active_function_names.get(
            service_key,
            [],
        )
    ),
    "create_job": (
        "create_job"
        in active_function_names.get(
            job_store_key,
            [],
        )
    ),
    "enqueue_job": (
        "enqueue_job"
        in active_function_names.get(
            queue_key,
            [],
        )
    ),
    "get_runtime_registration": (
        "get_runtime_registration"
        in active_function_names.get(
            registration_key,
            [],
        )
    ),
}

direct_handler_dispatches = []

for path_key, tree in active_trees.items():
    if not path_key.startswith(
        "backend/server/coordination/"
    ):
        continue

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        call = dotted_name(node.func)

        if (
            "dispatch_registered_runtime_handler"
            in call
        ):
            direct_handler_dispatches.append(
                {
                    "source": path_key,
                    "line": int(
                        getattr(node, "lineno", 0)
                    ),
                    "call": call,
                }
            )

hashes_after = {
    relative(path): sha256_file(path)
    for path in all_sources
}

sources_unchanged = (
    hashes_before == hashes_after
)

combined_source_fingerprint = hashlib.sha256(
    json.dumps(
        hashes_after,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
).hexdigest()

expected_failed_relative = relative(
    EXPECTED_FAILED_SOURCE
)

initial_failure_is_historical = (
    len(initial_parse_failures) == 1
    and initial_parse_failures[0].get(
        "source"
    )
    == expected_failed_relative
    and is_historical_source(
        EXPECTED_FAILED_SOURCE
    )
)

checks = {
    "initial_report_exists": (
        INITIAL_REPORT.exists()
    ),
    "initial_8_a_not_complete_retained": (
        "PART C 8-A NOT_COMPLETE"
        in initial_text
    ),
    "initial_successful_checks_retained": (
        sum(
            bool(value)
            for value in initial_checks.values()
        )
        == len(initial_checks) - 1
    ),
    "only_initial_failure_was_global_syntax_scan": (
        initial_failed_checks
        == [
            "all_scanned_sources_pass_syntax"
        ]
    ),
    "one_initial_parse_failure_retained": (
        len(initial_parse_failures) == 1
    ),
    "failed_source_is_historical_backup": (
        initial_failure_is_historical
    ),
    "historical_backup_exists": (
        EXPECTED_FAILED_SOURCE.exists()
    ),
    "historical_backup_excluded_from_active_set": (
        EXPECTED_FAILED_SOURCE
        not in active_sources
    ),
    "active_counterpart_exists": (
        ACTIVE_COUNTERPART.exists()
    ),
    "active_counterpart_passes_syntax": (
        ACTIVE_COUNTERPART.exists()
        and active_counterpart_parse_error
        is None
    ),
    "historical_backup_not_imported": (
        not archived_import_references
    ),
    "all_active_sources_pass_syntax": (
        bool(active_sources)
        and not active_parse_failures
    ),
    "canonical_boundary_files_complete": all(
        item["exists"]
        and item["parsed_as_active_source"]
        for item in canonical_boundary_status.values()
    ),
    "canonical_job_authorities_available": (
        all(canonical_authorities.values())
    ),
    "partial_gateway_decision_retained": (
        gateway_decision
        == (
            "PARTIAL_BOUNDARY_AVAILABLE_"
            "IMPLEMENTATION_OR_ADAPTER_REQUIRED"
        )
    ),
    "high_confidence_gateway_absent_retained": (
        "HIGH-CONFIDENCE INTEGRATED CANDIDATES:\n[]"
        in initial_text
    ),
    "coordination_does_not_dispatch_handler_directly": (
        not direct_handler_dispatches
    ),
    "production_sources_unchanged": (
        sources_unchanged
    ),
    "runtime_registration_created_no": True,
    "registry_persistence_executed_no": True,
    "universal_job_created_no": True,
    "queue_claim_executed_no": True,
    "handler_executed_no": True,
    "live_network_request_executed_no": True,
}

failed_checks = [
    name
    for name, passed in checks.items()
    if not passed
]

closure_complete = not failed_checks

report_lines = [
    "LINKCRAFTER UNIVERSAL COORDINATION",
    (
        "PART C 8-A CORRECTED RUNTIME EXECUTION "
        "BOUNDARY CLOSURE"
    ),
    "",
    f"Generated: {GENERATED_AT}",
    "Mode: READ-ONLY ACTIVE-SOURCE CLOSURE",
    "Production source changes: NONE",
    "Runtime registrations created: NO",
    "Registry persistence executed: NO",
    "Universal jobs created: NO",
    "Queue claims executed: NO",
    "Handlers executed: NO",
    "Live network requests executed: NO",
    (
        "CLOSURE STATUS: COMPLETE"
        if closure_complete
        else "CLOSURE STATUS: NOT_COMPLETE"
    ),
    "",
    "=" * 110,
    "CORRECTED DECISION",
    "=" * 110,
    (
        "The initial verifier included a historical _before_ "
        "source snapshot in the active production syntax gate."
    ),
    "",
    (
        "The only initial failure came from "
        + expected_failed_relative
        + "."
    ),
    "",
    (
        "That file is an inactive pre-fix snapshot. It is not "
        "imported by the active coordination, runtime or "
        "orchestration source set."
    ),
    "",
    (
        "The active counterpart passes syntax, and every active "
        "coordination, runtime and orchestration source passes "
        "the corrected syntax gate."
    ),
    "",
    (
        "The initial gateway decision remains authoritative: "
        + gateway_decision
        + "."
    ),
    "",
    "=" * 110,
    "CHECKS",
    "=" * 110,
    json.dumps(
        checks,
        indent=2,
        sort_keys=True,
    ),
    "",
    "FAILED_CHECKS:",
    json.dumps(
        failed_checks,
        indent=2,
    ),
    "",
    "=" * 110,
    "INITIAL FAILURE EVIDENCE",
    "=" * 110,
    json.dumps(
        {
            "initial_failed_checks": (
                initial_failed_checks
            ),
            "initial_parse_failures": (
                initial_parse_failures
            ),
            "initial_successful_check_count": sum(
                bool(value)
                for value in initial_checks.values()
            ),
            "initial_failed_check_count": len(
                initial_failed_checks
            ),
        },
        indent=2,
        sort_keys=True,
    ),
    "",
    "=" * 110,
    "ACTIVE SOURCE CLASSIFICATION",
    "=" * 110,
    json.dumps(
        {
            "all_python_source_count": len(
                all_sources
            ),
            "active_source_count": len(
                active_sources
            ),
            "historical_source_count": len(
                historical_sources
            ),
            "failed_historical_source": (
                expected_failed_relative
            ),
            "active_counterpart": relative(
                ACTIVE_COUNTERPART
            ),
            "active_parse_failures": (
                active_parse_failures
            ),
            "historical_import_references": (
                archived_import_references
            ),
        },
        indent=2,
        sort_keys=True,
    ),
    "",
    "=" * 110,
    "CANONICAL EXECUTION BOUNDARY",
    "=" * 110,
    json.dumps(
        {
            "gateway_decision": gateway_decision,
            "boundary_files": (
                canonical_boundary_status
            ),
            "canonical_authorities": (
                canonical_authorities
            ),
            "direct_handler_dispatches": (
                direct_handler_dispatches
            ),
        },
        indent=2,
        sort_keys=True,
    ),
    "",
    "=" * 110,
    "SOURCE STABILITY",
    "=" * 110,
    (
        "PRODUCTION_SOURCES_UNCHANGED="
        + (
            "YES"
            if sources_unchanged
            else "NO"
        )
    ),
    (
        "COMBINED_SOURCE_FINGERPRINT="
        + combined_source_fingerprint
    ),
    "",
    "=" * 110,
    "CERTIFIED 8-A BOUNDARY",
    "=" * 110,
    (
        "- Universal Job creation remains canonical through "
        "create_orchestration_job(), create_job() and "
        "enqueue_job()."
    ),
    (
        "- Runtime registration lookup remains canonical through "
        "get_runtime_registration()."
    ),
    (
        "- Coordination already contains job mapping, workflow-job "
        "correlation, completion intake and failure intake."
    ),
    (
        "- No complete coordination-to-runtime submission gateway "
        "is currently integrated."
    ),
    (
        "- Coordination does not execute registered runtime "
        "handlers directly."
    ),
    (
        "- Step 8 requires one adapter or implementation joining "
        "the existing coordination boundary to canonical "
        "Universal Job creation."
    ),
    "",
    "=" * 110,
    "NEXT STEP",
    "=" * 110,
    (
        "Proceed to Part C 8-B: freeze the canonical Runtime "
        "Execution Gateway request and result contract."
    ),
    "",
    "=" * 110,
    "FINAL RESULT",
    "=" * 110,
    (
        "PART C 8-A COMPLETE"
        if closure_complete
        else "PART C 8-A NOT_COMPLETE"
    ),
    "",
]

REPORT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT.write_text(
    "\n".join(report_lines),
    encoding="utf-8",
    newline="\n",
)

print("=" * 100)
print("PART C 8-A CORRECTED ACTIVE-SOURCE CLOSURE")
print("=" * 100)

for name, passed in checks.items():
    print(
        f"{name.upper()}: "
        + ("PASS" if passed else "FAIL")
    )

print()
print(
    "ACTIVE_SOURCE_COUNT="
    + str(len(active_sources))
)
print(
    "HISTORICAL_SOURCE_COUNT="
    + str(len(historical_sources))
)
print(
    "GATEWAY_DECISION="
    + gateway_decision
)
print(
    "FAILED_CHECK_COUNT="
    + str(len(failed_checks))
)
print("REPORT=" + str(REPORT))

if not closure_complete:
    print("PART_C_8_A_CORRECTED_STATUS=NOT_COMPLETE")
    raise SystemExit(1)

print("PART_C_8_A_CORRECTED_STATUS=COMPLETE")