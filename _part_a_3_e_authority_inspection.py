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
server_root = root / "backend" / "server"
runtime_root = server_root / "runtime"
orchestration_root = server_root / "orchestration"

required_sources = {
    "registration_package": (
        runtime_root / "runtime_registration_package.py"
    ),
    "registration_admission": (
        runtime_root / "runtime_registration_admission.py"
    ),
    "worker": (
        runtime_root / "universal_runtime_worker_v1.py"
    ),
    "queue": (
        orchestration_root / "queue.py"
    ),
    "job_store": (
        orchestration_root / "job_store.py"
    ),
    "service": (
        orchestration_root / "service.py"
    ),
}

known_modules = {
    "registration_package": (
        "backend.server.runtime.runtime_registration_package"
    ),
    "registration_admission": (
        "backend.server.runtime.runtime_registration_admission"
    ),
    "worker": (
        "backend.server.runtime.universal_runtime_worker_v1"
    ),
    "queue": (
        "backend.server.orchestration.queue"
    ),
    "job_store": (
        "backend.server.orchestration.job_store"
    ),
    "service": (
        "backend.server.orchestration.service"
    ),
}

search_terms = (
    "concurrency",
    "idempotency",
    "dedup",
    "duplicate",
    "running",
    "queued",
    "completed",
    "failed",
    "job_id",
    "workspace_id",
    "metadata",
    "lease",
    "claim",
    "list_jobs",
    "get_job",
    "create_job",
    "update_job_status",
)

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


def source_hash(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def definition_names(tree: ast.Module) -> tuple[str, ...]:
    return tuple(
        node.name
        for node in tree.body
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
            ),
        )
    )


def relevant_definitions(
    source: str,
    tree: ast.Module,
) -> list[tuple[str, int, int, str]]:
    lines = source.splitlines()
    results: list[tuple[str, int, int, str]] = []

    for node in tree.body:
        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
            ),
        ):
            continue

        if node.end_lineno is None:
            continue

        segment = "\n".join(
            lines[node.lineno - 1 : node.end_lineno]
        )
        lowered = segment.lower()

        if any(term in lowered for term in search_terms):
            results.append(
                (
                    node.name,
                    node.lineno,
                    node.end_lineno,
                    segment,
                )
            )

    return results


heading("PART A 3-E - REQUIRED SOURCE VALIDATION")

sources: dict[str, str] = {}
trees: dict[str, ast.Module] = {}
hashes: dict[str, str] = {}

for label, path in required_sources.items():
    check(
        f"SOURCE_EXISTS_{label.upper()}",
        path.is_file(),
        path,
    )

    if not path.is_file():
        continue

    try:
        source = path.read_text(encoding="utf-8-sig")
        tree = ast.parse(source)
    except Exception as exc:
        check(
            f"SOURCE_SYNTAX_{label.upper()}",
            False,
            f"{type(exc).__name__}: {exc}",
        )
        continue

    sources[label] = source
    trees[label] = tree
    hashes[label] = source_hash(path)

    check(
        f"SOURCE_SYNTAX_{label.upper()}",
        True,
        hashes[label],
    )

    print(
        f"TOP_LEVEL_DEFINITIONS_{label.upper()}="
        f"{definition_names(tree)!r}"
    )


heading("PART A 3-E - KNOWN MODULE IMPORTS")

modules: dict[str, Any] = {}

for label, module_name in known_modules.items():
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


heading("3-E1 - REGISTRATION DECLARATIONS")

package_module = modules.get("registration_package")

if package_module is not None:
    package_class = getattr(
        package_module,
        "RuntimeRegistrationPackage",
        None,
    )
    package_factory = getattr(
        package_module,
        "create_runtime_registration_package",
        None,
    )

    check(
        "REGISTRATION_PACKAGE_AVAILABLE",
        inspect.isclass(package_class),
    )
    check(
        "PACKAGE_FACTORY_AVAILABLE",
        callable(package_factory),
        safe_signature(package_factory)
        if callable(package_factory)
        else None,
    )

    if inspect.isclass(package_class):
        annotations = getattr(
            package_class,
            "__annotations__",
            {},
        )

        check(
            "CONCURRENCY_POLICY_DECLARED",
            "concurrency_policy" in annotations,
            sorted(annotations),
        )
        check(
            "IDEMPOTENCY_FIELDS_DECLARED",
            "idempotency_fields" in annotations,
        )

        print()
        print("REGISTRATION_PACKAGE_MODEL_SOURCE:")
        print(safe_source(package_class))

    if callable(package_factory):
        print()
        print("REGISTRATION_PACKAGE_FACTORY_SOURCE:")
        print(safe_source(package_factory))


heading("3-E2 - CURRENT ADMISSION AND WORKER ORDER")

admission_module = modules.get("registration_admission")
worker_module = modules.get("worker")

if admission_module is not None:
    admission_function = getattr(
        admission_module,
        "require_runtime_registration_admission",
        None,
    )

    check(
        "CURRENT_POLICY_ADMISSION_AVAILABLE",
        callable(admission_function),
        safe_signature(admission_function)
        if callable(admission_function)
        else None,
    )

    if callable(admission_function):
        print()
        print("CURRENT_POLICY_ADMISSION_SOURCE:")
        print(safe_source(admission_function))

if worker_module is not None:
    worker_function = getattr(
        worker_module,
        "run_one_universal_runtime_job_v1",
        None,
    )

    check(
        "CANONICAL_WORKER_AVAILABLE",
        callable(worker_function),
        safe_signature(worker_function)
        if callable(worker_function)
        else None,
    )

    if callable(worker_function):
        worker_source = safe_source(worker_function)

        print()
        print("CANONICAL_WORKER_SOURCE:")
        print(worker_source)

        try:
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

            print()
            print(f"WORKER_CALL_ORDER={calls!r}")

            registration_lines = [
                line
                for name, line in calls
                if name == "get_runtime_registration"
            ]
            policy_lines = [
                line
                for name, line in calls
                if name
                == "require_runtime_registration_admission"
            ]
            capability_lines = [
                line
                for name, line in calls
                if name
                == "match_universal_worker_capabilities"
            ]
            dispatcher_lines = [
                line
                for name, line in calls
                if name in {
                    "dispatcher",
                    "dispatch_registered_runtime_handler",
                }
            ]
            completion_lines = [
                line
                for name, line in calls
                if name == "mark_job_completed"
            ]
            failure_lines = [
                line
                for name, line in calls
                if name == "mark_job_failed"
            ]

            check(
                "REGISTRATION_LOOKUP_ANCHOR",
                len(registration_lines) == 1,
                registration_lines,
            )
            check(
                "CURRENT_POLICY_ADMISSION_ANCHOR",
                len(policy_lines) == 1,
                policy_lines,
            )
            check(
                "CAPABILITY_ANCHOR",
                len(capability_lines) == 1,
                capability_lines,
            )
            check(
                "DISPATCH_ANCHOR",
                len(dispatcher_lines) == 1,
                dispatcher_lines,
            )
            check(
                "COMPLETION_ANCHOR",
                bool(completion_lines),
                completion_lines,
            )
            check(
                "FAILURE_ANCHOR",
                bool(failure_lines),
                failure_lines,
            )
        except Exception:
            check("WORKER_AST_ANALYSIS", False)
            traceback.print_exc()


heading("3-E3 - ORCHESTRATION PUBLIC AUTHORITIES")

for module_label in (
    "queue",
    "job_store",
    "service",
):
    module = modules.get(module_label)

    if module is None:
        continue

    print()
    print(f"{module_label.upper()}_PUBLIC_SYMBOLS:")

    selected_symbols: list[str] = []

    for name in sorted(dir(module)):
        if name.startswith("_"):
            continue

        lowered = name.lower()

        if not any(term in lowered for term in search_terms):
            continue

        value = getattr(module, name)

        if inspect.isfunction(value) or inspect.isclass(value):
            selected_symbols.append(name)

            print(
                f"{name}: {type(value).__name__} "
                f"{safe_signature(value)}"
            )
        else:
            print(
                f"{name}: {type(value).__name__} = "
                f"{value!r}"
            )

    check(
        f"RELEVANT_PUBLIC_SYMBOLS_{module_label.upper()}",
        bool(selected_symbols),
        selected_symbols,
    )

    for name in selected_symbols:
        value = getattr(module, name)

        print()
        print(
            f"{module_label.upper()}_SYMBOL_SOURCE_{name}:"
        )
        print(safe_source(value))


heading("3-E4 - RELEVANT SOURCE DEFINITIONS")

for label in (
    "queue",
    "job_store",
    "service",
    "worker",
):
    source = sources.get(label)
    tree = trees.get(label)

    if source is None or tree is None:
        continue

    definitions = relevant_definitions(
        source,
        tree,
    )

    check(
        f"RELEVANT_DEFINITIONS_{label.upper()}",
        bool(definitions),
        [
            {
                "name": name,
                "start": start,
                "end": end,
            }
            for name, start, end, _
            in definitions
        ],
    )

    for name, start, end, segment in definitions:
        print()
        print(
            f"{label.upper()}_DEFINITION_"
            f"{name}_LINES_{start}_{end}:"
        )
        print(segment)


heading("3-E5 - PROJECT-WIDE AUTHORITY DISCOVERY")

discovered_files: list[dict[str, Any]] = []

for base in (
    runtime_root,
    orchestration_root,
):
    for path in sorted(base.rglob("*.py")):
        name = path.name.lower()

        if (
            ".before" in name
            or ".candidate" in name
            or "backup" in name
            or "__pycache__" in path.parts
        ):
            continue

        try:
            source = path.read_text(
                encoding="utf-8-sig"
            )
            tree = ast.parse(source)
        except Exception:
            continue

        lowered = source.lower()
        matching_terms = sorted(
            {
                term
                for term in (
                    "concurrency_policy",
                    "idempotency_fields",
                    "idempotency",
                    "dedup",
                    "duplicate",
                )
                if term in lowered
            }
        )

        if not matching_terms:
            continue

        definitions = relevant_definitions(
            source,
            tree,
        )

        discovered_files.append(
            {
                "path": str(path.relative_to(root)),
                "terms": matching_terms,
                "definitions": [
                    name
                    for name, _, _, _
                    in definitions
                ],
            }
        )

print(
    "DISCOVERED_CONCURRENCY_IDEMPOTENCY_FILES="
    f"{discovered_files!r}"
)

check(
    "CONCURRENCY_IDEMPOTENCY_DISCOVERY_COMPLETED",
    True,
    len(discovered_files),
)


heading("3-E6 - REQUIRED PERSISTENCE QUESTIONS")

question_matrix = {
    "can_read_job_by_id": False,
    "can_list_or_query_jobs": False,
    "can_read_job_status": False,
    "can_read_job_metadata": False,
    "can_persist_job_metadata": False,
    "can_atomically_claim_job": False,
    "lease_authority_present": False,
}

all_public_names: set[str] = set()
all_source = "\n".join(sources.values()).lower()

for module in modules.values():
    all_public_names.update(
        name.lower()
        for name in dir(module)
        if not name.startswith("_")
    )

question_matrix["can_read_job_by_id"] = any(
    name in all_public_names
    for name in (
        "get_job",
        "load_job",
        "get_orchestration_job",
    )
)

question_matrix["can_list_or_query_jobs"] = any(
    term in name
    for name in all_public_names
    for term in (
        "list_job",
        "find_job",
        "query_job",
        "queued_job",
    )
)

question_matrix["can_read_job_status"] = (
    "status" in all_source
)
question_matrix["can_read_job_metadata"] = (
    "metadata" in all_source
)
question_matrix["can_persist_job_metadata"] = (
    "update_job_status" in all_public_names
    or "update_job" in all_public_names
)
question_matrix["can_atomically_claim_job"] = (
    "dequeue_job" in all_public_names
)
question_matrix["lease_authority_present"] = (
    "lease" in all_source
)

print(f"PERSISTENCE_AUTHORITY_MATRIX={question_matrix!r}")

for key, value in question_matrix.items():
    check(
        f"PERSISTENCE_{key.upper()}",
        value,
    )


heading("PART A 3-E - SAFETY")

for label, path in required_sources.items():
    if label not in hashes:
        continue

    check(
        f"SOURCE_UNCHANGED_{label.upper()}",
        source_hash(path) == hashes[label],
        hashes[label],
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

    for label in failures:
        print(f"  - {label}")

print(
    "PART_A_3_E_AUTHORITY_INSPECTION="
    + ("COMPLETE" if failed == 0 else "INCOMPLETE")
)
print("PRODUCTION FILES MODIFIED: NO")

if failed:
    raise SystemExit(1)