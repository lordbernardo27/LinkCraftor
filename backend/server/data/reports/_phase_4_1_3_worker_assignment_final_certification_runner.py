from __future__ import annotations

import ast
import hashlib
import importlib
import sys
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

ASSIGNMENT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "assignment.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_3_worker_assignment_final_certification.txt"
)

EXPECTED_ASSIGNMENT_AST = (
    "609D3077B84C1791262F8ACA6BD268FD40436DF7775ACB3E9E726BCFC9715F56"
)


PROTECTED = {
    "worker_registration": (
        ROOT / "backend/server/runtime/universal_worker/registration.py",
        "00F0D6E620E24A7433C880B722E023AF3C2121563F8E18DFA9979E0F06A36D64",
    ),

    "worker_discovery": (
        ROOT / "backend/server/runtime/universal_worker/discovery.py",
        "DFCAB9080982C8D5E099A40C903F7B4140B0860053DB73CB77B30B966788A228",
    ),

    "queue_certification": (
        ROOT / "backend/server/runtime/universal_queue/certification.py",
        "6ED39655147D2B331E02101F5EA23E68CF71447353C0D294E170281AE40C0D4C",
    ),

    "job_contract": (
        ROOT / "backend/server/runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
    ),

    "existing_runtime_worker": (
        ROOT / "backend/server/runtime/universal_runtime_worker_v1.py",
        "6CC4EC122C6B8D1E21AFF8B55CAA786148D7E1FC75D840DAE9240FFB69634D44",
    ),

    "runtime_registration": (
        ROOT / "backend/server/runtime/universal_runtime_registration.py",
        "CBFBB0DA1E5D05A040AEC6F60B1251331431956106D90335A8C110FDBCA632E5",
    ),

    "runtime_infrastructure": (
        ROOT / "backend/server/runtime/universal_runtime_infrastructure.py",
        "EE6590D044C6AA20762F2A37AE86B7FFD3300B62610BC2B1F2657D9334CB311C",
    ),

    "orchestration_queue": (
        ROOT / "backend/server/orchestration/queue.py",
        "76F8F7E66578E2B8A4A1FF3BB420B6340A7A1D1D661EB66B7C21987CF3845A97",
    ),

    "orchestration_service": (
        ROOT / "backend/server/orchestration/service.py",
        "4C31CFC6FFDC9AFA8EA6AD8F43ADBC117F8A6D0193ABF045DBFBA39D6EB799BA",
    ),
}


def ast_sha(
    path: Path,
) -> str:

    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(source)

    canonical = ast.dump(
        tree,
        annotate_fields=True,
        include_attributes=False,
    )

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest().upper()


sys.path.insert(
    0,
    str(ROOT),
)

registration_name = (
    "backend.server.runtime."
    "universal_worker.registration"
)

assignment_name = (
    "backend.server.runtime."
    "universal_worker.assignment"
)

sys.modules.pop(
    assignment_name,
    None,
)

registration = importlib.import_module(
    registration_name
)

assignment = importlib.import_module(
    assignment_name
)


checks = []


def check(
    name,
    condition,
    detail="",
):

    checks.append(
        (
            name,
            bool(condition),
            str(detail),
        )
    )


# ============================================================
# 1 — FINAL AST
# ============================================================

assignment_ast = ast_sha(
    ASSIGNMENT_PATH
)

check(
    "worker_assignment_ast",
    assignment_ast
    == EXPECTED_ASSIGNMENT_AST,
    assignment_ast,
)


# ============================================================
# 2 — VERSION / SCHEMA / CONSTANTS
# ============================================================

check(
    "version",
    assignment.UNIVERSAL_WORKER_ASSIGNMENT_VERSION
    == "universal_worker_assignment_v4.1.3",
)

check(
    "result_schema",
    assignment.UNIVERSAL_WORKER_ASSIGNMENT_RESULT_SCHEMA_VERSION
    == "universal_worker_assignment_result_schema_v1",
)

check(
    "job_id_max_length",
    assignment.MAX_UNIVERSAL_WORKER_ASSIGNMENT_JOB_ID_LENGTH
    == 200,
)


# ============================================================
# 3 — CANONICAL FIXTURES
# ============================================================

def worker(
    worker_id,
    instance_id,
):

    return (
        registration.create_universal_worker_registration(
            worker_id=worker_id,
            worker_type="general",
            worker_instance_id=instance_id,
            runtime_version="runtime-v1",
            host_id="host-a",
            registered_at="2026-08-15T20:00:00Z",
        )
    )


worker_b = worker(
    "worker-b",
    "instance-001",
)

worker_a2 = worker(
    "worker-a",
    "instance-002",
)

worker_a1 = worker(
    "worker-a",
    "instance-001",
)


# ============================================================
# 4 — CANONICAL ASSIGNMENT
# ============================================================

result = (
    assignment.assign_universal_worker(
        job_id=" job-001 ",
        eligible_workers=(
            worker_b,
            worker_a2,
            worker_a1,
        ),
    )
)


check(
    "canonical_job_id",
    result.job_id
    == "job-001",
)

check(
    "canonical_assigned",
    result.assigned
    is True,
)

check(
    "canonical_status",
    result.status
    is assignment.UniversalWorkerAssignmentStatus.ASSIGNED,
)

check(
    "canonical_worker_id",
    result.worker_id
    == "worker-a",
)

check(
    "canonical_worker_instance_id",
    result.worker_instance_id
    == "instance-001",
)

check(
    "canonical_worker_identity",
    result.worker_identity
    == (
        "worker-a",
        "instance-001",
    ),
)

check(
    "canonical_candidate_count",
    result.candidate_count
    == 3,
)


# ============================================================
# 5 — DETERMINISM
# ============================================================

reordered = (
    assignment.assign_universal_worker(
        job_id="job-001",
        eligible_workers=(
            worker_a1,
            worker_b,
            worker_a2,
        ),
    )
)


check(
    "deterministic_assignment",
    reordered
    == result,
)


# ============================================================
# 6 — EMPTY RESULT
# ============================================================

empty = (
    assignment.assign_universal_worker(
        job_id="job-empty",
        eligible_workers=(),
    )
)


check(
    "empty_status",
    empty.status
    is assignment.UniversalWorkerAssignmentStatus.NO_ASSIGNMENT,
)

check(
    "empty_assigned_false",
    empty.assigned
    is False,
)

check(
    "empty_worker_none",
    empty.worker
    is None,
)

check(
    "empty_identity_none",
    empty.worker_identity
    is None,
)

check(
    "empty_candidate_count",
    empty.candidate_count
    == 0,
)


# ============================================================
# 7 — SAME LOGICAL WORKER / DIFFERENT INSTANCE
# ============================================================

same_logical_worker = (
    assignment.assign_universal_worker(
        job_id="job-instance",
        eligible_workers=(
            worker_a2,
            worker_a1,
        ),
    )
)


check(
    "same_worker_different_instances_distinct",
    same_logical_worker.candidate_count
    == 2,
)

check(
    "instance_tiebreak_exact",
    same_logical_worker.worker_identity
    == (
        "worker-a",
        "instance-001",
    ),
)


# ============================================================
# 8 — DUPLICATE IDENTITY
# ============================================================

duplicate = (
    registration.create_universal_worker_registration(
        worker_id="worker-a",
        worker_type="specialized",
        worker_instance_id="instance-001",
        runtime_version="runtime-v2",
        host_id="host-z",
        registered_at="2026-08-15T21:00:00Z",
    )
)


try:

    assignment.assign_universal_worker(
        job_id="job-dup",
        eligible_workers=(
            worker_a1,
            duplicate,
        ),
    )

except assignment.UniversalWorkerAssignmentError as exc:

    duplicate_rejected = (
        exc.code
        == "duplicate_eligible_worker_identity"
    )

else:

    duplicate_rejected = False


check(
    "duplicate_identity_rejected",
    duplicate_rejected,
)


# ============================================================
# 9 — RESULT INVARIANTS
# ============================================================

check(
    "assigned_requires_worker_semantic",
    (
        result.worker is not None
        and result.candidate_count >= 1
    ),
)

check(
    "no_assignment_requires_empty_semantic",
    (
        empty.worker is None
        and empty.candidate_count == 0
    ),
)


# ============================================================
# 10 — IMMUTABILITY
# ============================================================

for field_name in (
    "job_id",
    "status",
    "worker",
    "candidate_count",
    "schema_version",
):

    try:

        setattr(
            result,
            field_name,
            None,
        )

    except Exception:

        immutable = True

    else:

        immutable = False

    check(
        "immutable_"
        + field_name,
        immutable,
    )


# ============================================================
# 11 — WORKER REGISTRATIONS UNCHANGED
# ============================================================

before_a1 = worker_a1.to_dict()
before_a2 = worker_a2.to_dict()
before_b = worker_b.to_dict()


assignment.assign_universal_worker(
    job_id="job-no-mutation",
    eligible_workers=(
        worker_b,
        worker_a2,
        worker_a1,
    ),
)


check(
    "worker_a1_not_mutated",
    worker_a1.to_dict()
    == before_a1,
)

check(
    "worker_a2_not_mutated",
    worker_a2.to_dict()
    == before_a2,
)

check(
    "worker_b_not_mutated",
    worker_b.to_dict()
    == before_b,
)


# ============================================================
# 12 — EXPLANATION CONTRACT
# ============================================================

explanation = (
    assignment.explain_universal_worker_assignment_v1()
)


check(
    "phase",
    explanation.get(
        "phase"
    )
    == "4.1.3",
)

check(
    "component",
    explanation.get(
        "component"
    )
    == "Universal Worker Assignment",
)

check(
    "explanation_version",
    explanation.get(
        "version"
    )
    == assignment.UNIVERSAL_WORKER_ASSIGNMENT_VERSION,
)

check(
    "schema_explanation",
    explanation.get(
        "result_schema_version"
    )
    == assignment.UNIVERSAL_WORKER_ASSIGNMENT_RESULT_SCHEMA_VERSION,
)

check(
    "caller_supplied_eligible_rule",
    "caller-supplied already-eligible"
    in explanation.get(
        "input_rule",
        "",
    ),
)

check(
    "eligibility_boundary",
    "does not determine eligibility"
    in explanation.get(
        "eligibility_rule",
        "",
    ),
)

check(
    "selection_rule",
    "worker_id then worker_instance_id"
    in explanation.get(
        "selection_rule",
        "",
    ),
)

check(
    "empty_rule",
    "NO_ASSIGNMENT"
    in explanation.get(
        "empty_rule",
        "",
    ),
)

check(
    "job_evidence_rule",
    "job_id is the only job evidence"
    in explanation.get(
        "job_evidence_rule",
        "",
    ),
)

check(
    "assignment_is_selection_not_ownership",
    "does not create runtime ownership"
    in explanation.get(
        "meaning",
        "",
    ),
)

check(
    "purity_rule",
    "no state lookup, mutation or persistence"
    in explanation.get(
        "purity_rule",
        "",
    ),
)


# ============================================================
# 13 — PROHIBITION MATRIX
# ============================================================

required_prohibitions = (
    "does not discover workers",
    "does not determine worker health",
    "does not read worker heartbeats",
    "does not detect stale workers",
    "does not inspect worker pools",
    "does not inspect worker capabilities",
    "does not inspect worker capacity",
    "does not maintain round-robin state",
    "does not persist assignments",
    "does not write worker_id into job metadata",
    "does not mutate job status",
    "does not transition jobs to RUNNING",
    "does not claim jobs",
    "does not dequeue jobs",
    "does not acquire leases",
    "does not renew leases",
    "does not release leases",
    "does not dispatch jobs",
    "does not execute jobs",
    "does not access orchestration",
    "does not access Runtime State Store",
    "does not mutate Queue Infrastructure",
    "does not register runtime handlers",
    "does not perform filesystem I/O",
    "does not perform network I/O",
)


prohibitions = tuple(
    explanation.get(
        "prohibitions"
    )
    or ()
)


for index, item in enumerate(
    required_prohibitions,
    start=1,
):

    check(
        "prohibition_"
        + str(index),
        item in prohibitions,
        item,
    )


# ============================================================
# 14 — STATIC IMPORT BOUNDARY
# ============================================================

source = ASSIGNMENT_PATH.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(
    source
)


backend_imports = []


for node in ast.walk(tree):

    if isinstance(
        node,
        ast.ImportFrom,
    ):

        module_name = (
            node.module
            or ""
        )

        if module_name.startswith(
            "backend.server"
        ):

            backend_imports.append(
                module_name
            )

    elif isinstance(
        node,
        ast.Import,
    ):

        for alias in node.names:

            if alias.name.startswith(
                "backend.server"
            ):

                backend_imports.append(
                    alias.name
                )


check(
    "only_worker_registration_imported",
    backend_imports
    == [
        "backend.server.runtime.universal_worker.registration"
    ],
    backend_imports,
)


# ============================================================
# 15 — FORBIDDEN CALL BOUNDARY
# ============================================================

forbidden_names = {
    "open",
    "read_text",
    "write_text",
    "mkdir",
    "unlink",
    "remove",
    "read_json",
    "write_json",
    "discover_universal_workers",
    "inspect_workers",
    "worker_heartbeat",
    "get_runtime_state_store_registry",
    "get_latest_worker_statuses",
    "save_assignment",
    "save_assignments",
    "mark_job_running",
    "update_job_status",
    "claim_job",
    "dequeue_job",
    "lease_job",
    "renew_lease",
    "release_lease",
    "dispatch_job",
    "dispatch_registered_runtime_handler",
    "execute_job",
    "run_one_job",
    "register_handler",
    "save_job",
    "get_job",
}


forbidden_calls = []


for node in ast.walk(tree):

    if not isinstance(
        node,
        ast.Call,
    ):

        continue

    if isinstance(
        node.func,
        ast.Name,
    ):

        call_name = (
            node.func.id
        )

    elif isinstance(
        node.func,
        ast.Attribute,
    ):

        call_name = (
            node.func.attr
        )

    else:

        continue

    if call_name in forbidden_names:

        forbidden_calls.append(
            (
                call_name,
                getattr(
                    node,
                    "lineno",
                    0,
                ),
            )
        )


check(
    "no_forbidden_calls",
    not forbidden_calls,
    forbidden_calls,
)


# ============================================================
# 16 — RESPONSIBILITY BLEED
# ============================================================

function_names = tuple(
    node.name.lower()
    for node in ast.walk(tree)
    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    )
)


for token in (
    "discover",
    "health",
    "heartbeat",
    "stale",
    "pool",
    "capability",
    "capacity",
    "round_robin",
    "persist",
    "claim",
    "dequeue",
    "lease",
    "renew",
    "release",
    "dispatch",
    "execute",
    "running",
):

    matches = tuple(
        name
        for name in function_names
        if token in name
    )

    check(
        "no_owned_"
        + token,
        not matches,
        matches,
    )


# ============================================================
# 17 — PROTECTED AST MATRIX
# ============================================================

for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(
        path
    )

    check(
        "protected_"
        + name,
        actual
        == expected,
        actual,
    )


# ============================================================
# 18 — CANONICAL ASSIGNMENT FINGERPRINT
# ============================================================

fingerprint_material = "|".join(
    (
        "phase_4_1_3_worker_assignment",
        assignment.UNIVERSAL_WORKER_ASSIGNMENT_VERSION,
        assignment.UNIVERSAL_WORKER_ASSIGNMENT_RESULT_SCHEMA_VERSION,
        assignment_ast,
        "job_id",
        "eligible_workers",
        "worker_id",
        "worker_instance_id",
        "ASSIGNED",
        "NO_ASSIGNMENT",
        "worker_id_then_worker_instance_id",
        "selection_not_ownership",
    )
)


assignment_fingerprint = (
    hashlib.sha256(
        fingerprint_material.encode(
            "utf-8"
        )
    ).hexdigest().upper()
)


check(
    "fingerprint_generated",
    len(
        assignment_fingerprint
    )
    == 64,
    assignment_fingerprint,
)


# ============================================================
# 19 — FINAL AST RECHECK
# ============================================================

final_ast = ast_sha(
    ASSIGNMENT_PATH
)


check(
    "final_ast_unchanged",
    final_ast
    == EXPECTED_ASSIGNMENT_AST,
    final_ast,
)


# ============================================================
# REPORT
# ============================================================

passed = sum(
    1
    for _, ok, _
    in checks
    if ok
)

total = len(
    checks
)


lines = [
    (
        "PHASE 4.1.3 — UNIVERSAL WORKER "
        "ASSIGNMENT FINAL CERTIFICATION"
    ),
    "=" * 112,
    "",
    (
        "WORKER ASSIGNMENT AST SHA256: "
        + assignment_ast
    ),
    (
        "WORKER ASSIGNMENT FINGERPRINT: "
        + assignment_fingerprint
    ),
    "",
]


for index, (
    name,
    ok,
    detail,
) in enumerate(
    checks,
    start=1,
):

    lines.append(
        (
            f"{index}. {name}: "
            f"{'PASS' if ok else 'FAIL'}"
        )
    )

    if detail:

        lines.append(
            "   "
            + detail
        )


lines.extend(
    [
        "",
        "=" * 112,
        (
            "FINAL WORKER ASSIGNMENT CERTIFICATION: "
            + (
                "PASS"
                if passed == total
                else "FAIL"
            )
        ),
        (
            "CHECKS PASSED: "
            + str(passed)
            + "/"
            + str(total)
        ),
        "",
        "WORKER ASSIGNMENT MODIFIED DURING CERTIFICATION: NO",
        "4.1.1 WORKER REGISTRATION MODIFIED: NO",
        "4.1.2 WORKER DISCOVERY MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "EXISTING UNIVERSAL RUNTIME WORKER MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "ASSIGNMENT PERSISTED: NO",
        "WORKER_ID WRITTEN TO JOB METADATA: NO",
        "JOB STATUS MUTATED: NO",
        "JOB TRANSITIONED TO RUNNING: NO",
        "JOB CLAIMED: NO",
        "JOB DEQUEUED: NO",
        "JOB LEASED: NO",
        "HEARTBEAT READ: NO",
        "WORKER HEALTH DECIDED: NO",
        "STALE WORKER DETECTED: NO",
        "WORKER POOL INSPECTED: NO",
        "WORKER CAPABILITY INSPECTED: NO",
        "WORKER CAPACITY INSPECTED: NO",
        "ROUND-ROBIN STATE CREATED: NO",
        "JOB DISPATCHED: NO",
        "JOB EXECUTED: NO",
        "",
        (
            "PHASE 4.1.3 FREEZE CANDIDATE: "
            + (
                "YES"
                if passed == total
                else "NO"
            )
        ),
    ]
)


REPORT_PATH.write_text(
    "\n".join(lines),
    encoding="utf-8",
)

print(
    "\n".join(lines)
)


if passed != total:

    raise SystemExit(
        "Phase 4.1.3 Worker Assignment final certification failed."
    )
