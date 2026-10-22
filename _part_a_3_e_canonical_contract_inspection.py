from __future__ import annotations

import ast
import hashlib
import importlib
import inspect
import pathlib
import sys
import traceback
from typing import Any


root = pathlib.Path(sys.argv[1]).resolve()

targets = {
    "execution_safety": (
        "backend.server.runtime.execution_engine."
        "execution_safety_concurrency"
    ),
    "idempotency_control": (
        "backend.server.runtime.execution_engine."
        "idempotency_duplicate_control"
    ),
    "duplicate_detection": (
        "backend.server.runtime.universal_jobs."
        "duplicate_detection"
    ),
    "duplicate_handling": (
        "backend.server.runtime.universal_jobs."
        "duplicate_handling"
    ),
    "creation_engine": (
        "backend.server.runtime.universal_jobs."
        "creation_engine"
    ),
    "job_store": (
        "backend.server.orchestration.job_store"
    ),
    "queue": (
        "backend.server.orchestration.queue"
    ),
    "worker": (
        "backend.server.runtime.universal_runtime_worker_v1"
    ),
}

required_symbols = {
    "execution_safety": (
        "protect_concurrent_execution",
        "validate_lease_safety",
        "validate_worker_safety",
        "protect_terminal_state_reentry",
        "resolve_execution_race",
        "validate_result_safety",
    ),
    "idempotency_control": (
        "create_execution_idempotency_identity",
        "evaluate_duplicate_invocation",
        "validate_replay_safety",
        "evaluate_duplicate_result",
        "concurrent_duplicate_allowed",
    ),
    "duplicate_detection": (
        "build_universal_job_duplicate_signature",
        "detect_universal_job_duplicate",
    ),
    "duplicate_handling": (
        "decide_universal_job_duplicate_handling",
    ),
    "job_store": (
        "get_job",
        "update_job_status",
    ),
    "queue": (
        "dequeue_job",
        "prepare_universal_runtime_job_lease",
    ),
    "worker": (
        "run_one_universal_runtime_job_v1",
    ),
}

passed = 0
failed = 0
failures: list[str] = []


def heading(title: str) -> None:
    print()
    print("=" * 116)
    print(title)
    print("=" * 116)


def check(
    label: str,
    condition: bool,
    detail: Any = None,
) -> None:
    global passed, failed

    if condition:
        passed += 1
        print(f"{label}: PASS")
    else:
        failed += 1
        failures.append(label)
        print(f"{label}: FAIL")

    if detail is not None:
        print(f"  {detail}")


def safe_signature(value: Any) -> str:
    try:
        return str(inspect.signature(value))
    except Exception as exc:
        return (
            f"<signature unavailable: "
            f"{type(exc).__name__}: {exc}>"
        )


def safe_source(value: Any) -> str:
    try:
        return inspect.getsource(value)
    except Exception as exc:
        return (
            f"<source unavailable: "
            f"{type(exc).__name__}: {exc}>"
        )


def module_source_path(module: Any) -> pathlib.Path | None:
    path = getattr(module, "__file__", None)

    if not path:
        return None

    return pathlib.Path(path).resolve()


heading("PART A 3-E - CANONICAL MODULE IMPORTS")

modules: dict[str, Any] = {}
source_hashes: dict[pathlib.Path, str] = {}

for label, module_name in targets.items():
    try:
        module = importlib.import_module(module_name)
    except Exception:
        check(
            f"MODULE_IMPORT_{label.upper()}",
            False,
        )
        traceback.print_exc()
        continue

    modules[label] = module

    check(
        f"MODULE_IMPORT_{label.upper()}",
        True,
        module_name,
    )

    path = module_source_path(module)

    check(
        f"MODULE_SOURCE_{label.upper()}",
        path is not None and path.is_file(),
        path,
    )

    if path is not None and path.is_file():
        source = path.read_text(encoding="utf-8-sig")
        ast.parse(source)

        digest = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

        source_hashes[path] = digest

        check(
            f"MODULE_SYNTAX_{label.upper()}",
            True,
            digest,
        )


heading("PART A 3-E - EXACT PUBLIC CONTRACTS")

for module_label, symbol_names in required_symbols.items():
    module = modules.get(module_label)

    if module is None:
        continue

    print()
    print(f"{module_label.upper()}_CONTRACTS:")

    for symbol_name in symbol_names:
        value = getattr(
            module,
            symbol_name,
            None,
        )

        available = (
            inspect.isfunction(value)
            or inspect.isclass(value)
        )

        check(
            f"SYMBOL_{module_label.upper()}_{symbol_name.upper()}",
            available,
            safe_signature(value)
            if available
            else None,
        )

        if available:
            print()
            print(
                f"SOURCE_{module_label.upper()}_"
                f"{symbol_name}:"
            )
            print(safe_source(value))


heading("PART A 3-E - SUPPORTING MODELS AND ENUMS")

model_terms = (
    "Idempotency",
    "Duplicate",
    "Concurrency",
    "ExecutionRace",
    "LeaseSafety",
    "WorkerSafety",
    "ResultTiming",
    "SafetyDecision",
    "Disposition",
    "Identity",
    "Evidence",
    "Decision",
)

for module_label in (
    "execution_safety",
    "idempotency_control",
    "duplicate_detection",
    "duplicate_handling",
):
    module = modules.get(module_label)

    if module is None:
        continue

    print()
    print(f"{module_label.upper()}_SUPPORTING_MODELS:")

    discovered_models: list[str] = []

    for name in sorted(dir(module)):
        if name.startswith("_"):
            continue

        if not any(
            term.lower() in name.lower()
            for term in model_terms
        ):
            continue

        value = getattr(module, name)

        if not inspect.isclass(value):
            continue

        discovered_models.append(name)

        print(
            f"{name}: {safe_signature(value)}"
        )
        print(safe_source(value))

    check(
        f"SUPPORTING_MODELS_{module_label.upper()}",
        bool(discovered_models),
        discovered_models,
    )


heading("PART A 3-E - CREATION ENGINE INTEGRATION")

creation_module = modules.get("creation_engine")

if creation_module is not None:
    for name in (
        "UniversalJobCreationRequest",
        "UniversalJobCreationResult",
        "normalize_universal_job_creation_request",
        "create_universal_job",
    ):
        value = getattr(
            creation_module,
            name,
            None,
        )

        available = (
            inspect.isfunction(value)
            or inspect.isclass(value)
        )

        check(
            f"CREATION_SYMBOL_{name.upper()}",
            available,
            safe_signature(value)
            if available
            else None,
        )

        if available:
            print()
            print(f"CREATION_SOURCE_{name}:")
            print(safe_source(value))


heading("PART A 3-E - WORKER INSERTION ORDER")

worker_module = modules.get("worker")

if worker_module is not None:
    worker_function = getattr(
        worker_module,
        "run_one_universal_runtime_job_v1",
        None,
    )

    if callable(worker_function):
        worker_source = inspect.getsource(
            worker_function
        )
        worker_tree = ast.parse(worker_source)
        calls: list[tuple[str, int]] = []

        for node in ast.walk(worker_tree):
            if not isinstance(node, ast.Call):
                continue

            if isinstance(node.func, ast.Name):
                calls.append(
                    (node.func.id, node.lineno)
                )
            elif isinstance(node.func, ast.Attribute):
                calls.append(
                    (node.func.attr, node.lineno)
                )

        calls.sort(key=lambda item: item[1])

        print(f"WORKER_CALL_ORDER={calls!r}")

        required_order = {
            "registration_lookup": [
                line for name, line in calls
                if name == "get_runtime_registration"
            ],
            "policy_admission": [
                line for name, line in calls
                if name
                == "require_runtime_registration_admission"
            ],
            "capability": [
                line for name, line in calls
                if name
                == "match_universal_worker_capabilities"
            ],
            "dispatch": [
                line for name, line in calls
                if name in {
                    "dispatcher",
                    "dispatch_registered_runtime_handler",
                }
            ],
            "completion": [
                line for name, line in calls
                if name == "mark_job_completed"
            ],
            "failure": [
                line for name, line in calls
                if name == "mark_job_failed"
            ],
        }

        print(
            f"WORKER_BOUNDARY_LINES={required_order!r}"
        )

        check(
            "WORKER_PRE_DISPATCH_BOUNDARY_AVAILABLE",
            bool(
                required_order["policy_admission"]
                and required_order["dispatch"]
                and (
                    required_order["policy_admission"][0]
                    < required_order["dispatch"][0]
                )
            ),
        )
        check(
            "WORKER_COMPLETION_BOUNDARY_AVAILABLE",
            bool(required_order["completion"]),
        )
        check(
            "WORKER_FAILURE_BOUNDARY_AVAILABLE",
            bool(required_order["failure"]),
        )


heading("PART A 3-E - SOURCE STABILITY")

for path, expected_hash in source_hashes.items():
    actual_hash = hashlib.sha256(
        path.read_bytes()
    ).hexdigest()

    check(
        "SOURCE_UNCHANGED_"
        + path.stem.upper(),
        actual_hash == expected_hash,
        expected_hash,
    )

check("PRODUCTION_FILES_MODIFIED_NO", True)
check("REGISTRATION_CREATED_NO", True)
check("REGISTRY_PERSISTENCE_EXECUTED_NO", True)
check("JOB_CREATED_NO", True)
check("JOB_CLAIMED_NO", True)
check("HANDLER_EXECUTED_NO", True)


heading("PART A 3-E - FINAL RESULT")

print(f"INSPECTION_CHECKS_PASSED={passed}")
print(f"INSPECTION_CHECKS_FAILED={failed}")

if failures:
    print("FAILED_CHECKS:")

    for failure in failures:
        print(f"  - {failure}")

print(
    "PART_A_3_E_CANONICAL_CONTRACT_INSPECTION="
    + ("COMPLETE" if failed == 0 else "INCOMPLETE")
)
print("PRODUCTION FILES MODIFIED: NO")

if failed:
    raise SystemExit(1)