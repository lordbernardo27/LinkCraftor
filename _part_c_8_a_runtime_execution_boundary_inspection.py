from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


if len(sys.argv) != 3:
    raise RuntimeError(
        "Expected project root and report path arguments."
    )

ROOT = Path(sys.argv[1]).resolve()
REPORT = Path(sys.argv[2]).resolve()

SERVER_ROOT = ROOT / "backend" / "server"
COORDINATION_ROOT = SERVER_ROOT / "coordination"
RUNTIME_ROOT = SERVER_ROOT / "runtime"
ORCHESTRATION_ROOT = SERVER_ROOT / "orchestration"
REPORT_ROOT = SERVER_ROOT / "data" / "reports"

GENERATED_AT = datetime.now(
    timezone.utc
).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id

    if isinstance(node, ast.Attribute):
        parent = dotted_name(node.value)

        if parent:
            return f"{parent}.{node.attr}"

        return node.attr

    return ""


def parameter_names(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[str]:
    parameters: list[str] = []

    for argument in (
        list(node.args.posonlyargs)
        + list(node.args.args)
    ):
        parameters.append(argument.arg)

    if node.args.vararg is not None:
        parameters.append(
            "*" + node.args.vararg.arg
        )

    for argument in node.args.kwonlyargs:
        parameters.append(argument.arg)

    if node.args.kwarg is not None:
        parameters.append(
            "**" + node.args.kwarg.arg
        )

    return parameters


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


source_files = sorted(
    {
        *(
            COORDINATION_ROOT.rglob("*.py")
            if COORDINATION_ROOT.exists()
            else []
        ),
        *(
            RUNTIME_ROOT.rglob("*.py")
            if RUNTIME_ROOT.exists()
            else []
        ),
        *(
            ORCHESTRATION_ROOT.rglob("*.py")
            if ORCHESTRATION_ROOT.exists()
            else []
        ),
    },
    key=lambda item: item.as_posix(),
)

source_hashes_before = {
    relative(path): sha256_file(path)
    for path in source_files
}

analyses: list[dict[str, Any]] = []
source_texts: dict[str, str] = {}
parse_failures: list[dict[str, str]] = []
function_records: list[dict[str, Any]] = []
class_records: list[dict[str, Any]] = []

for path in source_files:
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
        parse_failures.append(
            {
                "source": path_key,
                "error_type": type(error).__name__,
                "error_message": str(error),
            }
        )
        continue

    source_texts[path_key] = source

    functions: list[dict[str, Any]] = []
    classes: list[dict[str, Any]] = []
    calls: set[str] = set()
    imports: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            function_calls = sorted(
                {
                    dotted_name(child.func)
                    for child in ast.walk(node)
                    if isinstance(child, ast.Call)
                    and dotted_name(child.func)
                }
            )

            segment = (
                ast.get_source_segment(
                    source,
                    node,
                )
                or ""
            )

            record = {
                "source": path_key,
                "name": node.name,
                "line": int(
                    getattr(node, "lineno", 0)
                ),
                "async": isinstance(
                    node,
                    ast.AsyncFunctionDef,
                ),
                "parameters": parameter_names(node),
                "calls": function_calls,
                "segment_lower": segment.lower(),
            }

            functions.append(
                {
                    key: value
                    for key, value in record.items()
                    if key != "segment_lower"
                }
            )
            function_records.append(record)

        elif isinstance(node, ast.ClassDef):
            record = {
                "source": path_key,
                "name": node.name,
                "line": int(
                    getattr(node, "lineno", 0)
                ),
            }

            classes.append(record)
            class_records.append(record)

        elif isinstance(node, ast.Call):
            name = dotted_name(node.func)

            if name:
                calls.add(name)

        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""

            for alias in node.names:
                imports.add(
                    f"{module}:{alias.name}"
                )

    analyses.append(
        {
            "source": path_key,
            "functions": sorted(
                functions,
                key=lambda item: (
                    item["line"],
                    item["name"],
                ),
            ),
            "classes": sorted(
                classes,
                key=lambda item: (
                    item["line"],
                    item["name"],
                ),
            ),
            "calls": sorted(calls),
            "imports": sorted(imports),
        }
    )


def public_function(
    record: dict[str, Any],
) -> bool:
    return not str(
        record["name"]
    ).startswith("_")


creation_pattern = re.compile(
    r"(create|submit|enqueue|schedule|persist).*job"
    r"|job.*(create|submit|enqueue|schedule|persist)",
    re.IGNORECASE,
)

creation_candidates: list[dict[str, Any]] = []

for record in function_records:
    path_lower = str(
        record["source"]
    ).lower()

    is_creation_engine = (
        "creation_engine" in path_lower
    )

    is_job_creation_name = bool(
        creation_pattern.search(
            str(record["name"])
        )
    )

    if (
        public_function(record)
        and (
            is_creation_engine
            or is_job_creation_name
        )
    ):
        creation_candidates.append(
            {
                key: value
                for key, value in record.items()
                if key != "segment_lower"
            }
        )

creation_candidates = sorted(
    creation_candidates,
    key=lambda item: (
        item["source"],
        item["line"],
        item["name"],
    ),
)

queue_sources = [
    item
    for item in analyses
    if item["source"].endswith(
        "orchestration/queue.py"
    )
]

queue_functions = [
    {
        key: value
        for key, value in record.items()
        if key != "segment_lower"
    }
    for record in function_records
    if record["source"].endswith(
        "orchestration/queue.py"
    )
    and public_function(record)
]

creation_names = {
    str(item["name"])
    for item in creation_candidates
}

queue_submission_names = {
    str(item["name"])
    for item in queue_functions
    if any(
        token in str(
            item["name"]
        ).lower()
        for token in (
            "create",
            "submit",
            "enqueue",
            "add",
            "push",
            "persist",
        )
    )
}

gateway_candidates: list[dict[str, Any]] = []

for record in function_records:
    source_path = str(record["source"])

    if not source_path.startswith(
        "backend/server/coordination/"
    ):
        continue

    name_lower = str(
        record["name"]
    ).lower()
    segment_lower = str(
        record["segment_lower"]
    )
    call_names = {
        str(call).split(".")[-1]
        for call in record["calls"]
    }

    identity_fields = [
        field
        for field in (
            "workflow_id",
            "workspace_id",
            "correlation_id",
            "stage_id",
            "job_id",
            "dependency_job_ids",
            "idempotency_key",
        )
        if re.search(
            rf"\b{re.escape(field)}\b",
            segment_lower,
        )
    ]

    creator_call = bool(
        call_names.intersection(
            creation_names
        )
    ) or any(
        token in call_name.lower()
        for call_name in call_names
        for token in (
            "job_creator",
            "job_submitter",
            "create_job",
            "submit_job",
            "enqueue_job",
        )
    )

    queue_submission_call = bool(
        call_names.intersection(
            queue_submission_names
        )
    )

    registration_lookup = any(
        "get_runtime_registration"
        in call
        for call in record["calls"]
    )

    score = 0

    if any(
        token in name_lower
        for token in (
            "gateway",
            "submit",
            "enqueue",
            "launch",
            "dispatch",
        )
    ):
        score += 2

    if "job" in name_lower:
        score += 1

    if creator_call:
        score += 3

    if queue_submission_call:
        score += 2

    if registration_lookup:
        score += 1

    if "workflow_id" in identity_fields:
        score += 1

    if "stage_id" in identity_fields:
        score += 1

    if "job_id" in identity_fields:
        score += 1

    if (
        score >= 3
        and (
            "runtime" in segment_lower
            or "job" in segment_lower
        )
    ):
        gateway_candidates.append(
            {
                "source": source_path,
                "function": record["name"],
                "line": record["line"],
                "parameters": record["parameters"],
                "calls": record["calls"],
                "identity_fields": identity_fields,
                "creator_call": creator_call,
                "queue_submission_call": (
                    queue_submission_call
                ),
                "registration_lookup": (
                    registration_lookup
                ),
                "confidence_score": score,
            }
        )

gateway_candidates.sort(
    key=lambda item: (
        -int(item["confidence_score"]),
        item["source"],
        int(item["line"]),
    )
)

integrated_gateway_candidates = [
    item
    for item in gateway_candidates
    if (
        item["creator_call"]
        and "workflow_id"
        in item["identity_fields"]
        and "stage_id"
        in item["identity_fields"]
    )
]

direct_handler_dispatch_candidates = [
    {
        "source": record["source"],
        "function": record["name"],
        "line": record["line"],
        "calls": [
            call
            for call in record["calls"]
            if (
                "dispatch_registered_runtime_handler"
                in call
            )
        ],
    }
    for record in function_records
    if str(record["source"]).startswith(
        "backend/server/coordination/"
    )
    and any(
        "dispatch_registered_runtime_handler"
        in call
        for call in record["calls"]
    )
]

coordination_runtime_modules = []

for item in analyses:
    source_path = str(item["source"])
    source_lower = source_path.lower()

    if (
        "/runtime_integration/" in source_lower
        or any(
            candidate["source"] == source_path
            for candidate in gateway_candidates
        )
    ):
        coordination_runtime_modules.append(
            {
                "source": source_path,
                "functions": [
                    function["name"]
                    for function in item["functions"]
                    if not str(
                        function["name"]
                    ).startswith("_")
                ],
                "classes": [
                    class_record["name"]
                    for class_record in item["classes"]
                    if not str(
                        class_record["name"]
                    ).startswith("_")
                ],
                "relevant_calls": [
                    call
                    for call in item["calls"]
                    if any(
                        token in call.lower()
                        for token in (
                            "runtime",
                            "job",
                            "queue",
                            "completion",
                            "failure",
                        )
                    )
                ],
            }
        )

completion_intake_sources = sorted(
    {
        item["source"]
        for item in analyses
        if (
            "completion_intake"
            in str(item["source"]).lower()
            or any(
                "completion" in str(
                    function["name"]
                ).lower()
                for function in item["functions"]
            )
        )
        and str(item["source"]).startswith(
            "backend/server/coordination/"
        )
    }
)

failure_intake_sources = sorted(
    {
        item["source"]
        for item in analyses
        if (
            "failure_intake"
            in str(item["source"]).lower()
            or any(
                "failure" in str(
                    function["name"]
                ).lower()
                for function in item["functions"]
            )
        )
        and str(item["source"]).startswith(
            "backend/server/coordination/"
        )
    }
)

identity_fields = (
    "workflow_id",
    "workflow_type",
    "workspace_id",
    "correlation_id",
    "stage_id",
    "runtime_stage",
    "job_type",
    "job_id",
    "dependency_job_ids",
    "idempotency_key",
    "payload",
    "metadata",
)

identity_coverage: dict[str, Any] = {}

for field in identity_fields:
    matching_sources = sorted(
        source_path
        for source_path, source
        in source_texts.items()
        if re.search(
            rf"\b{re.escape(field)}\b",
            source,
        )
    )

    identity_coverage[field] = {
        "present": bool(matching_sources),
        "source_count": len(
            matching_sources
        ),
        "sample_sources": (
            matching_sources[:10]
        ),
    }

class_locations: dict[str, list[str]] = {}

for class_record in class_records:
    class_locations.setdefault(
        str(class_record["name"]),
        [],
    ).append(
        str(class_record["source"])
    )

registration_lookup_locations = [
    {
        "source": record["source"],
        "line": record["line"],
        "parameters": record["parameters"],
    }
    for record in function_records
    if record["name"]
    == "get_runtime_registration"
]

step_7_reports: list[str] = []

if REPORT_ROOT.exists():
    for report_path in sorted(
        REPORT_ROOT.glob("*.txt")
    ):
        if report_path.resolve() == REPORT:
            continue

        try:
            report_text = report_path.read_text(
                encoding="utf-8-sig",
                errors="replace",
            ).upper()
        except Exception:
            continue

        if (
            "PART C STEP 7 UNIVERSAL COORDINATION "
            "FRAMEWORK CERTIFIED"
            in report_text
            or (
                "PART_C_7_G"
                in report_text
                and "CERTIFIED"
                in report_text
            )
            or (
                "PART C 7-G"
                in report_text
                and "CERTIFIED"
                in report_text
            )
        ):
            step_7_reports.append(
                relative(report_path)
            )

if integrated_gateway_candidates:
    gateway_decision = (
        "EXISTING_SUBMISSION_AUTHORITY_AVAILABLE"
    )
elif gateway_candidates:
    gateway_decision = (
        "PARTIAL_BOUNDARY_AVAILABLE_"
        "IMPLEMENTATION_OR_ADAPTER_REQUIRED"
    )
else:
    gateway_decision = "IMPLEMENTATION_REQUIRED"

source_hashes_after = {
    relative(path): sha256_file(path)
    for path in source_files
}

sources_unchanged = (
    source_hashes_before
    == source_hashes_after
)

combined_source_fingerprint = hashlib.sha256(
    json.dumps(
        source_hashes_after,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
).hexdigest()

checks = {
    "project_root_exists": ROOT.exists(),
    "server_root_exists": SERVER_ROOT.exists(),
    "coordination_root_exists": (
        COORDINATION_ROOT.exists()
    ),
    "runtime_root_exists": (
        RUNTIME_ROOT.exists()
    ),
    "orchestration_root_exists": (
        ORCHESTRATION_ROOT.exists()
    ),
    "step_7_certification_evidence_found": (
        bool(step_7_reports)
    ),
    "coordination_sources_found": any(
        str(item["source"]).startswith(
            "backend/server/coordination/"
        )
        for item in analyses
    ),
    "runtime_sources_found": any(
        str(item["source"]).startswith(
            "backend/server/runtime/"
        )
        for item in analyses
    ),
    "all_scanned_sources_pass_syntax": (
        bool(source_files)
        and not parse_failures
    ),
    "universal_workflow_contract_found": (
        "UniversalWorkflow"
        in class_locations
    ),
    "universal_stage_contract_found": (
        "UniversalStageReference"
        in class_locations
    ),
    "runtime_registration_lookup_found": (
        bool(registration_lookup_locations)
    ),
    "universal_job_creation_surface_inspected": (
        bool(creation_candidates)
    ),
    "canonical_queue_surface_inspected": (
        bool(queue_sources)
    ),
    "completion_intake_boundary_found": (
        bool(completion_intake_sources)
    ),
    "failure_intake_boundary_found": (
        bool(failure_intake_sources)
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

inspection_complete = not failed_checks

report_lines = [
    "LINKCRAFTER UNIVERSAL COORDINATION",
    "PART C 8-A RUNTIME EXECUTION BOUNDARY INSPECTION",
    "",
    f"Generated: {GENERATED_AT}",
    "Mode: READ-ONLY EXECUTION BOUNDARY DISCOVERY",
    "Production source changes: NONE",
    "Runtime registrations created: NO",
    "Registry persistence executed: NO",
    "Universal jobs created: NO",
    "Queue claims executed: NO",
    "Handlers executed: NO",
    "Live network requests executed: NO",
    (
        "INSPECTION STATUS: COMPLETE"
        if inspection_complete
        else "INSPECTION STATUS: NOT_COMPLETE"
    ),
    "",
    "=" * 110,
    "INSPECTION DECISION",
    "=" * 110,
    (
        "Part C Step 7 certification evidence was found."
        if step_7_reports
        else
        "Part C Step 7 certification evidence was not found."
    ),
    "",
    (
        "RUNTIME EXECUTION GATEWAY DECISION: "
        + gateway_decision
    ),
    "",
    (
        "This inspection identifies the canonical Universal Job "
        "creation surface, queue boundary, coordination runtime "
        "integration modules, completion and failure intake, and "
        "identity fields that Step 8 must preserve."
    ),
    "",
    (
        "No production source was patched. No Universal Job was "
        "created or claimed, and no registered handler was executed."
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
    "STEP 7 PREREQUISITE EVIDENCE",
    "=" * 110,
    json.dumps(
        step_7_reports,
        indent=2,
    ),
    "",
    "=" * 110,
    "UNIVERSAL JOB CREATION SURFACE",
    "=" * 110,
    json.dumps(
        creation_candidates,
        indent=2,
        sort_keys=True,
    ),
    "",
    "=" * 110,
    "CANONICAL QUEUE SURFACE",
    "=" * 110,
    json.dumps(
        {
            "sources": [
                item["source"]
                for item in queue_sources
            ],
            "public_functions": queue_functions,
            "submission_function_names": sorted(
                queue_submission_names
            ),
        },
        indent=2,
        sort_keys=True,
    ),
    "",
    "=" * 110,
    "COORDINATION RUNTIME-INTEGRATION MODULES",
    "=" * 110,
    json.dumps(
        coordination_runtime_modules,
        indent=2,
        sort_keys=True,
    ),
    "",
    "=" * 110,
    "RUNTIME EXECUTION GATEWAY CANDIDATES",
    "=" * 110,
    json.dumps(
        gateway_candidates,
        indent=2,
        sort_keys=True,
    ),
    "",
    "HIGH-CONFIDENCE INTEGRATED CANDIDATES:",
    json.dumps(
        integrated_gateway_candidates,
        indent=2,
        sort_keys=True,
    ),
    "",
    "=" * 110,
    "DIRECT HANDLER-DISPATCH CHECK",
    "=" * 110,
    json.dumps(
        {
            "direct_dispatch_candidates": (
                direct_handler_dispatch_candidates
            ),
            "required_step_8_behavior": (
                "Coordination must submit Universal Jobs; "
                "the gateway must not execute registered "
                "handlers directly."
            ),
        },
        indent=2,
        sort_keys=True,
    ),
    "",
    "=" * 110,
    "COMPLETION AND FAILURE INTAKE",
    "=" * 110,
    json.dumps(
        {
            "completion_intake_sources": (
                completion_intake_sources
            ),
            "failure_intake_sources": (
                failure_intake_sources
            ),
        },
        indent=2,
        sort_keys=True,
    ),
    "",
    "=" * 110,
    "IDENTITY AND DEPENDENCY FIELD COVERAGE",
    "=" * 110,
    json.dumps(
        identity_coverage,
        indent=2,
        sort_keys=True,
    ),
    "",
    "=" * 110,
    "CONTRACT AND REGISTRATION EVIDENCE",
    "=" * 110,
    json.dumps(
        {
            "class_locations": {
                key: sorted(value)
                for key, value
                in sorted(
                    class_locations.items()
                )
                if key in {
                    "UniversalWorkflow",
                    "UniversalStageReference",
                    "UniversalStageResult",
                }
            },
            "runtime_registration_lookup": (
                registration_lookup_locations
            ),
        },
        indent=2,
        sort_keys=True,
    ),
    "",
    "=" * 110,
    "SOURCE STABILITY",
    "=" * 110,
    f"SCANNED_SOURCE_COUNT={len(source_files)}",
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
    "PARSE_FAILURES:",
    json.dumps(
        parse_failures,
        indent=2,
        sort_keys=True,
    ),
    "",
    "=" * 110,
    "NEXT STEP",
    "=" * 110,
    (
        "Part C 8-B will freeze the Runtime Execution Gateway "
        "request and result contract using the actual authorities "
        "identified by this inspection."
    ),
    "",
    (
        "If an existing submission authority is available, 8-B "
        "will preserve and adapt it rather than create a duplicate."
    ),
    "",
    (
        "If implementation is required, 8-B will define one "
        "canonical gateway contract before any production patch."
    ),
    "",
    "=" * 110,
    "FINAL RESULT",
    "=" * 110,
    (
        "PART C 8-A COMPLETE"
        if inspection_complete
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
print("PART C 8-A RUNTIME EXECUTION BOUNDARY INSPECTION")
print("=" * 100)

for name, passed in checks.items():
    print(
        f"{name.upper()}: "
        + ("PASS" if passed else "FAIL")
    )

print()
print(
    "GATEWAY_DECISION="
    + gateway_decision
)
print(
    "GATEWAY_CANDIDATE_COUNT="
    + str(len(gateway_candidates))
)
print(
    "HIGH_CONFIDENCE_GATEWAY_COUNT="
    + str(
        len(integrated_gateway_candidates)
    )
)
print(
    "DIRECT_HANDLER_DISPATCH_COUNT="
    + str(
        len(
            direct_handler_dispatch_candidates
        )
    )
)
print(
    "FAILED_CHECK_COUNT="
    + str(len(failed_checks))
)
print("REPORT=" + str(REPORT))

if not inspection_complete:
    print("PART_C_8_A_STATUS=NOT_COMPLETE")
    raise SystemExit(1)

print("PART_C_8_A_STATUS=COMPLETE")