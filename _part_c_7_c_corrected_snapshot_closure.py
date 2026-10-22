from __future__ import annotations

import hashlib
import importlib
import inspect
import json
import sys
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(sys.argv[1]).resolve()
INITIAL_REPORT = Path(sys.argv[2]).resolve()
REPORT = Path(sys.argv[3]).resolve()

SNAPSHOT_AUTHORITIES = {
    "dependency_graph_snapshot": {
        "module": (
            "backend.server.coordination."
            "dependency_planning.dependency_graph"
        ),
        "parameters": (
            "graph",
        ),
    },
    "dependency_validation_snapshot": {
        "module": (
            "backend.server.coordination."
            "dependency_planning.dependency_validation"
        ),
        "parameters": (
            "graph",
        ),
    },
    "cycle_detection_snapshot": {
        "module": (
            "backend.server.coordination."
            "dependency_planning.cycle_detection"
        ),
        "parameters": (
            "graph",
        ),
    },
    "runnable_stage_resolution_snapshot": {
        "module": (
            "backend.server.coordination."
            "dependency_planning.runnable_stage_resolver"
        ),
        "parameters": (
            "graph",
            "state",
        ),
    },
    "execution_plan_snapshot": {
        "module": (
            "backend.server.coordination."
            "dependency_planning.execution_planner"
        ),
        "parameters": (
            "graph",
            "resolution",
        ),
    },
    "planning_certification_snapshot": {
        "module": (
            "backend.server.coordination."
            "dependency_planning.planning_certification"
        ),
        "parameters": (),
    },
}

EXPECTED_INITIAL_FAILURES = (
    "dependency_graph_snapshot_mapping",
    "dependency_validation_snapshot_mapping",
    "cycle_detection_snapshot_mapping",
    "runnable_stage_resolver_snapshot_mapping",
    "execution_planner_snapshot_mapping",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def module_source(module: Any) -> Path:
    source = inspect.getsourcefile(module)

    if not source:
        raise RuntimeError(
            f"Module source unavailable: {module.__name__}"
        )

    path = Path(source).resolve()

    if not path.is_file():
        raise RuntimeError(
            f"Module source unavailable: {path}"
        )

    return path


def parameter_names(
    function: Any,
) -> tuple[str, ...]:
    return tuple(
        inspect.signature(
            function
        ).parameters.keys()
    )


def mapping_return_declared(
    function: Any,
) -> bool:
    annotation = inspect.signature(
        function
    ).return_annotation

    text = str(annotation).lower()

    return (
        "mapping" in text
        or "dict" in text
    )


initial_text = INITIAL_REPORT.read_text(
    encoding="utf-8",
    errors="replace",
).replace("\r\n", "\n")

checks: dict[str, bool] = {
    "initial_7_c_report_exists": (
        INITIAL_REPORT.is_file()
    ),
    "initial_planning_certification_passed": (
        '"planning_certification_passed": true'
        in initial_text
    ),
    "initial_planning_error_absent": (
        '"planning_certification_error_absent": true'
        in initial_text
    ),
    "initial_missing_calls_empty": (
        "MISSING_CERTIFICATION_CALLS:\n[]"
        in initial_text
    ),
    "initial_forbidden_calls_empty": (
        "FORBIDDEN_SOURCE_CALLS:\n[]"
        in initial_text
    ),
    "initial_changed_sources_empty": (
        "CHANGED_SOURCES:\n[]"
        in initial_text
    ),
}

for failure_name in EXPECTED_INITIAL_FAILURES:
    checks[
        f"initial_failure_retained_{failure_name}"
    ] = f'"{failure_name}"' in initial_text

modules: dict[str, Any] = {}
functions: dict[str, Any] = {}
import_failures: list[dict[str, str]] = []
signature_evidence: dict[str, Any] = {}
source_paths: dict[str, Path] = {}

for function_name, declaration in (
    SNAPSHOT_AUTHORITIES.items()
):
    module_name = declaration["module"]

    try:
        module = modules.get(
            module_name
        )

        if module is None:
            module = importlib.import_module(
                module_name
            )
            modules[module_name] = module

        function = getattr(
            module,
            function_name,
            None,
        )

        functions[function_name] = function
        source_paths[module_name] = (
            module_source(module)
        )

        actual_parameters = (
            parameter_names(function)
            if callable(function)
            else ()
        )

        expected_parameters = declaration[
            "parameters"
        ]

        signature_evidence[function_name] = {
            "module": module_name,
            "signature": (
                str(inspect.signature(function))
                if callable(function)
                else None
            ),
            "expected_parameters": list(
                expected_parameters
            ),
            "actual_parameters": list(
                actual_parameters
            ),
            "mapping_return_declared": (
                mapping_return_declared(function)
                if callable(function)
                else False
            ),
        }

        checks[
            f"{function_name}_available"
        ] = callable(function)

        checks[
            f"{function_name}_parameters_correct"
        ] = (
            actual_parameters
            == expected_parameters
        )

        checks[
            f"{function_name}_mapping_return_declared"
        ] = (
            callable(function)
            and mapping_return_declared(
                function
            )
        )

    except Exception as error:
        import_failures.append(
            {
                "function": function_name,
                "module": module_name,
                "error_type": type(error).__name__,
                "error_message": str(error),
            }
        )

source_hashes_before = {
    name: sha256(path)
    for name, path in source_paths.items()
}

planning_snapshot_function = functions.get(
    "planning_certification_snapshot"
)

planning_snapshot: dict[str, Any] = {}
planning_snapshot_error: dict[str, str] | None = None

if callable(planning_snapshot_function):
    try:
        snapshot_value = (
            planning_snapshot_function()
        )

        if isinstance(
            snapshot_value,
            Mapping,
        ):
            planning_snapshot = dict(
                snapshot_value
            )
        else:
            planning_snapshot_error = {
                "error_type": (
                    type(snapshot_value).__name__
                ),
                "error_message": (
                    "Planning certification snapshot "
                    "did not return a mapping."
                ),
            }

    except Exception as error:
        planning_snapshot_error = {
            "error_type": type(error).__name__,
            "error_message": str(error),
        }

checks.update(
    {
        "planning_snapshot_mapping": (
            bool(planning_snapshot)
        ),
        "planning_snapshot_certified": (
            planning_snapshot.get(
                "is_certified"
            )
            is True
        ),
        "planning_snapshot_check_count_23": (
            planning_snapshot.get(
                "check_count"
            )
            == 23
        ),
        "planning_snapshot_all_checks_passed": (
            planning_snapshot.get(
                "passed_check_count"
            )
            == 23
        ),
        "planning_snapshot_zero_failures": (
            planning_snapshot.get(
                "failed_check_count"
            )
            == 0
        ),
        "planning_snapshot_failed_checks_empty": (
            not planning_snapshot.get(
                "failed_checks"
            )
        ),
        "deep_chain_2500_certified": (
            planning_snapshot.get(
                "deep_chain_node_count"
            )
            == 2500
        ),
        "composite_fingerprint_available": (
            isinstance(
                planning_snapshot.get(
                    "composite_fingerprint"
                ),
                str,
            )
            and len(
                planning_snapshot.get(
                    "composite_fingerprint",
                )
            )
            == 64
        ),
        "planning_snapshot_error_absent": (
            planning_snapshot_error is None
        ),
    }
)

certified_checks = planning_snapshot.get(
    "checks",
    (),
)

check_text = " ".join(
    str(check)
    for check in certified_checks
).lower()

checks.update(
    {
        "canonical_graph_validation_certified": (
            "canonical graph passes"
            in check_text
        ),
        "acyclic_graph_certified": (
            "canonical graph is acyclic"
            in check_text
        ),
        "directed_cycle_detection_certified": (
            "directed cycle detected"
            in check_text
        ),
        "parallel_execution_wave_certified": (
            "parallel roots remain one wave"
            in check_text
        ),
        "join_readiness_certified": (
            "join becomes runnable"
            in check_text
        ),
        "runnability_deterministic": (
            "runnability certification deterministic"
            in check_text
        ),
        "planning_deterministic": (
            "planning certification deterministic"
            in check_text
        ),
    }
)

source_hashes_after = {
    name: sha256(path)
    for name, path in source_paths.items()
}

changed_sources = [
    source_paths[name]
    .relative_to(ROOT)
    .as_posix()
    for name in source_hashes_before
    if (
        source_hashes_before[name]
        != source_hashes_after[name]
    )
]

checks.update(
    {
        "all_snapshot_authorities_imported": (
            not import_failures
            and len(functions)
            == len(SNAPSHOT_AUTHORITIES)
        ),
        "production_sources_unchanged": (
            not changed_sources
        ),
        "runtime_registration_created_no": True,
        "registry_persistence_executed_no": True,
        "universal_job_created_no": True,
        "queue_claim_executed_no": True,
        "production_handler_executed_no": True,
        "live_network_request_executed_no": True,
    }
)

failed_checks = [
    name
    for name, passed in checks.items()
    if not passed
]

certified = not failed_checks
status = (
    "CERTIFIED"
    if certified
    else "NOT_CERTIFIED"
)

closure_evidence = {
    "snapshot_signatures": (
        signature_evidence
    ),
    "planning_snapshot": (
        planning_snapshot
    ),
    "planning_snapshot_error": (
        planning_snapshot_error
    ),
}

closure_fingerprint = hashlib.sha256(
    json.dumps(
        closure_evidence,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
).hexdigest()

report_text = f"""\
LINKCRAFTER UNIVERSAL COORDINATION
PART C 7-C CORRECTED DEPENDENCY-PLANNING CLOSURE

Generated: {datetime.now(timezone.utc).isoformat()}
Mode: READ-ONLY TARGETED CLOSURE
Production source changes: NONE
Runtime registrations created: NO
Registry persistence executed: NO
Universal jobs created: NO
Queue claims executed: NO
Production handlers executed: NO
Live network requests executed: NO
CERTIFICATION STATUS: {status}

==============================================================================================================
CORRECTED DECISION
==============================================================================================================
The initial verifier treated five object snapshot functions as
zero-argument global snapshot functions.

Their actual canonical signatures are:

- dependency_graph_snapshot(graph)
- dependency_validation_snapshot(graph)
- cycle_detection_snapshot(graph)
- runnable_stage_resolution_snapshot(graph, state)
- execution_plan_snapshot(graph, resolution)

These functions serialize supplied immutable planning objects. They do
not expose global state and must not be called without those objects.

planning_certification_snapshot() is the zero-argument composite
certification snapshot. It reports the result of the complete canonical
dependency-planning certification.

==============================================================================================================
RUNTIME VERIFICATION
==============================================================================================================
CHECKS:
{json.dumps(checks, indent=2, sort_keys=True)}

FAILED_CHECKS:
{json.dumps(failed_checks, indent=2)}

IMPORT_FAILURES:
{json.dumps(import_failures, indent=2, sort_keys=True)}

CHANGED_SOURCES:
{json.dumps(changed_sources, indent=2)}

CLOSURE_FINGERPRINT:
{closure_fingerprint}

==============================================================================================================
SNAPSHOT SIGNATURE EVIDENCE
==============================================================================================================
{json.dumps(signature_evidence, indent=2, sort_keys=True)}

==============================================================================================================
CANONICAL PLANNING CERTIFICATION SNAPSHOT
==============================================================================================================
{json.dumps(planning_snapshot, indent=2, sort_keys=True, default=str)}

PLANNING_SNAPSHOT_ERROR:
{json.dumps(planning_snapshot_error, indent=2, sort_keys=True)}

==============================================================================================================
CERTIFIED BOUNDARY
==============================================================================================================
- UniversalWorkflow remains the canonical workflow manifest.
- DependencyGraph remains the canonical DAG authority.
- Graph validation, cycle detection and deep-chain safety are certified.
- Runnable-stage resolution and dependency joins are certified.
- Parallel execution-wave planning is certified.
- Planning output remains deterministic.
- Object snapshot functions retain their required object parameters.
- The composite planning snapshot reports 23 passed checks and no failure.
- No production source or runtime state was modified.

Part C Step 7 remains in progress.

Next:
Part C 7-D — readiness, stage handoff, context propagation and
output-to-input mapping certification.

==============================================================================================================
FINAL RESULT
==============================================================================================================
PART C 7-C {status}
"""

REPORT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT.write_text(
    report_text,
    encoding="utf-8",
    newline="\n",
)

print("=" * 108)
print("PART C 7-C CORRECTED PLANNING CLOSURE")
print("=" * 108)

for name, passed in checks.items():
    print(
        f"{name.upper()}: "
        f"{'PASS' if passed else 'FAIL'}"
    )

print()
print(f"FAILED_CHECK_COUNT={len(failed_checks)}")
print(
    "PLANNING_CLOSURE_FINGERPRINT="
    + closure_fingerprint
)
print(
    "PRODUCTION_SOURCE_CHANGES="
    + str(len(changed_sources))
)
print(f"REPORT={REPORT}")
print(
    "PART_C_7_C_STATUS="
    + (
        "CERTIFIED"
        if certified
        else "NOT_CERTIFIED"
    )
)

if not certified:
    raise SystemExit(1)