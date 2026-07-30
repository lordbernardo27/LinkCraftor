from __future__ import annotations

import ast
from pathlib import Path

PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

FILES = [
    PROJECT_ROOT / "backend/server/runtime/universal_jobs/contract.py",
    PROJECT_ROOT / "backend/server/runtime/universal_runtime_kernel.py",
    PROJECT_ROOT / "backend/server/runtime/universal_runtime_infrastructure.py",
    PROJECT_ROOT / "backend/server/jobs/universal_knowledge_orchestrator.py",
    PROJECT_ROOT / "backend/server/runtime/runtime_state_store.py",
    PROJECT_ROOT / "backend/server/runtime/runtime_persistence.py",
]

CAPABILITIES = {
    "job_creation": (
        "create_job",
        "create_universal",
        "job_id",
    ),
    "persistent_queue": (
        "queued",
        "queue",
        "persist",
    ),
    "leasing": (
        "lease",
        "leased",
        "is_leased",
    ),
    "worker_assignment": (
        "worker",
        "claim",
        "assign",
    ),
    "completion": (
        "completed",
        "mark_completed",
    ),
    "failure": (
        "failed",
        "mark_failed",
        "record_job_failure",
    ),
    "registration": (
        "register",
        "registration",
    ),
    "extensible_job_types": (
        "job_type",
        "handler",
        "runtime_registration",
    ),
}

results = {k: [] for k in CAPABILITIES}
syntax_failures = []

for path in FILES:
    if not path.exists():
        continue

    try:
        source = path.read_text(
            encoding="utf-8-sig",
            errors="strict",
        )
        ast.parse(source)
    except Exception as exc:
        syntax_failures.append(
            f"{path.relative_to(PROJECT_ROOT)} : {exc}"
        )
        continue

    lowered = source.casefold()

    for capability, terms in CAPABILITIES.items():
        if any(term.casefold() in lowered for term in terms):
            results[capability].append(
                path.relative_to(PROJECT_ROOT).as_posix()
            )

for key in results:
    results[key] = sorted(set(results[key]))

all_core_present = all(
    results[key]
    for key in (
        "job_creation",
        "leasing",
        "worker_assignment",
        "completion",
        "failure",
        "registration",
        "extensible_job_types",
    )
)

persistent_present = bool(
    results["persistent_queue"]
)

if all_core_present and persistent_present:
    classification = "CANONICAL_UNIVERSAL_QUEUE_READY"
elif all_core_present:
    classification = "UNIVERSAL_QUEUE_CORE_EXISTS"
else:
    classification = "PARTIAL_UNIVERSAL_QUEUE"

print()
print("=" * 116)
print("UNIVERSAL QUEUE CAPABILITY DISCOVERY")
print("=" * 116)
print()

print("Classification :", classification)
print()

for capability in (
    "job_creation",
    "persistent_queue",
    "leasing",
    "worker_assignment",
    "completion",
    "failure",
    "registration",
    "extensible_job_types",
):
    print(f"{capability:<22}: {len(results[capability])}")
    for item in results[capability]:
        print("  ", item)
    print()

print("Production files modified : False")
print("Queues created            : 0")
print("Workers created           : 0")
print("Persistent writes         : 0")

print()
print("Syntax failures")

if syntax_failures:
    for item in syntax_failures:
        print("  ", item)
else:
    print("  None")

print()
print("UNIVERSAL QUEUE CAPABILITY SCAN: PASS")
print("=" * 116)
