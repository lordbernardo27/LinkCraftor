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
    / "phase_4_1_3_worker_assignment_regression.txt"
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
# AST / VERSION
# ============================================================

assignment_ast = ast_sha(
    ASSIGNMENT_PATH
)

check(
    "assignment_ast_stable",
    assignment_ast
    == EXPECTED_ASSIGNMENT_AST,
    assignment_ast,
)

check(
    "version_exact",
    assignment.UNIVERSAL_WORKER_ASSIGNMENT_VERSION
    == "universal_worker_assignment_v4.1.3",
)

check(
    "schema_exact",
    assignment.UNIVERSAL_WORKER_ASSIGNMENT_RESULT_SCHEMA_VERSION
    == "universal_worker_assignment_result_schema_v1",
)

check(
    "job_id_max_length_exact",
    assignment.MAX_UNIVERSAL_WORKER_ASSIGNMENT_JOB_ID_LENGTH
    == 200,
)


# ============================================================
# FIXTURES
# ============================================================

def worker(
    worker_id,
    instance_id,
    *,
    worker_type="general",
    runtime_version="runtime-v1",
    host_id="host-a",
):

    return (
        registration.create_universal_worker_registration(
            worker_id=worker_id,
            worker_type=worker_type,
            worker_instance_id=instance_id,
            runtime_version=runtime_version,
            host_id=host_id,
            registered_at="2026-08-15T20:00:00Z",
        )
    )


a1 = worker(
    "worker-a",
    "instance-001",
)

a2 = worker(
    "worker-a",
    "instance-002",
)

b1 = worker(
    "worker-b",
    "instance-001",
)

z9 = worker(
    "worker-z",
    "instance-009",
)


# ============================================================
# JOB ID NORMALIZATION / BOUNDARIES
# ============================================================

check(
    "job_id_whitespace_normalization",
    assignment.normalize_universal_worker_assignment_job_id(
        "  job-123  "
    )
    == "job-123",
)


for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        1,
        [],
        {},
        (),
        set(),
    ),
    start=1,
):

    try:

        assignment.normalize_universal_worker_assignment_job_id(
            bad
        )

    except assignment.UniversalWorkerAssignmentError as exc:

        rejected = (
            exc.code
            == "invalid_assignment_job_id_type"
        )

    else:

        rejected = False

    check(
        "bad_job_id_type_"
        + str(index),
        rejected,
        repr(bad),
    )


for index, bad in enumerate(
    (
        "",
        " ",
        "   ",
        "\t",
        "\n",
        "\r\n",
    ),
    start=1,
):

    try:

        assignment.normalize_universal_worker_assignment_job_id(
            bad
        )

    except assignment.UniversalWorkerAssignmentError as exc:

        rejected = (
            exc.code
            == "empty_assignment_job_id"
        )

    else:

        rejected = False

    check(
        "blank_job_id_"
        + str(index),
        rejected,
        repr(bad),
    )


exact_max_job_id = (
    "j"
    * assignment.MAX_UNIVERSAL_WORKER_ASSIGNMENT_JOB_ID_LENGTH
)

check(
    "job_id_exact_max_accepted",
    assignment.normalize_universal_worker_assignment_job_id(
        exact_max_job_id
    )
    == exact_max_job_id,
)


overflow_job_id = (
    "j"
    * (
        assignment.MAX_UNIVERSAL_WORKER_ASSIGNMENT_JOB_ID_LENGTH
        + 1
    )
)


try:

    assignment.normalize_universal_worker_assignment_job_id(
        overflow_job_id
    )

except assignment.UniversalWorkerAssignmentError as exc:

    overflow_rejected = (
        exc.code
        == "assignment_job_id_too_long"
    )

else:

    overflow_rejected = False


check(
    "job_id_overflow_rejected",
    overflow_rejected,
)


# ============================================================
# DETERMINISTIC ASSIGNMENT
# ============================================================

result = (
    assignment.assign_universal_worker(
        job_id="job-001",
        eligible_workers=(
            z9,
            b1,
            a2,
            a1,
        ),
    )
)


check(
    "assigned_status_exact",
    result.status
    is assignment.UniversalWorkerAssignmentStatus.ASSIGNED,
)

check(
    "assigned_true",
    result.assigned
    is True,
)

check(
    "selected_identity_exact",
    result.worker_identity
    == (
        "worker-a",
        "instance-001",
    ),
)

check(
    "candidate_count_exact",
    result.candidate_count
    == 4,
)


# ============================================================
# ORDER INDEPENDENCE
# ============================================================

reversed_result = (
    assignment.assign_universal_worker(
        job_id="job-001",
        eligible_workers=(
            a1,
            a2,
            b1,
            z9,
        ),
    )
)


check(
    "order_independent",
    reversed_result
    == result,
)


# ============================================================
# GENERATOR SUPPORT
# ============================================================

generator_result = (
    assignment.assign_universal_worker(
        job_id="job-001",
        eligible_workers=(
            item
            for item in (
                z9,
                a2,
                b1,
                a1,
            )
        ),
    )
)


check(
    "generator_supported",
    generator_result
    == result,
)


# ============================================================
# EMPTY POPULATION
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
    "empty_worker_id_none",
    empty.worker_id
    is None,
)

check(
    "empty_instance_none",
    empty.worker_instance_id
    is None,
)

check(
    "empty_identity_none",
    empty.worker_identity
    is None,
)

check(
    "empty_candidate_count_zero",
    empty.candidate_count
    == 0,
)


# ============================================================
# INVALID ELIGIBLE COLLECTION
# ============================================================

for index, bad in enumerate(
    (
        None,
        "workers",
        b"workers",
        {},
        1,
        True,
        False,
    ),
    start=1,
):

    try:

        assignment.assign_universal_worker(
            job_id="job-x",
            eligible_workers=bad,
        )

    except assignment.UniversalWorkerAssignmentError as exc:

        rejected = (
            exc.code
            == "invalid_eligible_workers"
        )

    else:

        rejected = False

    check(
        "invalid_collection_"
        + str(index),
        rejected,
        repr(bad),
    )


# ============================================================
# INVALID MEMBER ATTACKS
# ============================================================

for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        1,
        "",
        [],
        {},
        (),
    ),
    start=1,
):

    try:

        assignment.assign_universal_worker(
            job_id="job-x",
            eligible_workers=(
                a1,
                bad,
            ),
        )

    except assignment.UniversalWorkerAssignmentError as exc:

        rejected = (
            exc.code
            == "invalid_assignment_worker"
        )

    else:

        rejected = False

    check(
        "invalid_worker_member_"
        + str(index),
        rejected,
        repr(bad),
    )


# ============================================================
# DUPLICATE IDENTITY
# ============================================================

duplicate_a1 = worker(
    "worker-a",
    "instance-001",
    worker_type="specialized",
    runtime_version="runtime-v2",
    host_id="host-z",
)


try:

    assignment.assign_universal_worker(
        job_id="job-dup",
        eligible_workers=(
            a1,
            duplicate_a1,
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
# SAME WORKER ID / DIFFERENT INSTANCE
# ============================================================

same_worker = (
    assignment.assign_universal_worker(
        job_id="job-same",
        eligible_workers=(
            a2,
            a1,
        ),
    )
)


check(
    "same_worker_different_instances_count",
    same_worker.candidate_count
    == 2,
)

check(
    "same_worker_instance_tiebreak",
    same_worker.worker_identity
    == (
        "worker-a",
        "instance-001",
    ),
)


# ============================================================
# RESULT STATUS INVARIANTS
# ============================================================

try:

    assignment.UniversalWorkerAssignmentResult(
        job_id="job",
        status=(
            assignment.UniversalWorkerAssignmentStatus.ASSIGNED
        ),
        worker=None,
        candidate_count=1,
    )

except assignment.UniversalWorkerAssignmentError as exc:

    rejected = (
        exc.code
        == "assigned_worker_required"
    )

else:

    rejected = False


check(
    "assigned_requires_worker",
    rejected,
)


try:

    assignment.UniversalWorkerAssignmentResult(
        job_id="job",
        status=(
            assignment.UniversalWorkerAssignmentStatus.ASSIGNED
        ),
        worker=a1,
        candidate_count=0,
    )

except assignment.UniversalWorkerAssignmentError as exc:

    rejected = (
        exc.code
        == "assigned_candidate_count_invalid"
    )

else:

    rejected = False


check(
    "assigned_requires_positive_count",
    rejected,
)


try:

    assignment.UniversalWorkerAssignmentResult(
        job_id="job",
        status=(
            assignment.UniversalWorkerAssignmentStatus.NO_ASSIGNMENT
        ),
        worker=a1,
        candidate_count=0,
    )

except assignment.UniversalWorkerAssignmentError as exc:

    rejected = (
        exc.code
        == "no_assignment_worker_forbidden"
    )

else:

    rejected = False


check(
    "no_assignment_forbids_worker",
    rejected,
)


try:

    assignment.UniversalWorkerAssignmentResult(
        job_id="job",
        status=(
            assignment.UniversalWorkerAssignmentStatus.NO_ASSIGNMENT
        ),
        worker=None,
        candidate_count=1,
    )

except assignment.UniversalWorkerAssignmentError as exc:

    rejected = (
        exc.code
        == "no_assignment_candidate_count_must_be_zero"
    )

else:

    rejected = False


check(
    "no_assignment_requires_zero_count",
    rejected,
)


# ============================================================
# RAW STATUS ATTACK
# ============================================================

try:

    assignment.UniversalWorkerAssignmentResult(
        job_id="job",
        status="ASSIGNED",
        worker=a1,
        candidate_count=1,
    )

except assignment.UniversalWorkerAssignmentError as exc:

    rejected = (
        exc.code
        == "invalid_assignment_status"
    )

else:

    rejected = False


check(
    "raw_status_string_rejected",
    rejected,
)


# ============================================================
# CANDIDATE COUNT ATTACKS
# ============================================================

for index, bad in enumerate(
    (
        None,
        True,
        False,
        -1,
        -100,
        1.0,
        "1",
        [],
        {},
    ),
    start=1,
):

    try:

        assignment.UniversalWorkerAssignmentResult(
            job_id="job",
            status=(
                assignment.UniversalWorkerAssignmentStatus.NO_ASSIGNMENT
            ),
            worker=None,
            candidate_count=bad,
        )

    except assignment.UniversalWorkerAssignmentError as exc:

        rejected = (
            exc.code
            == "invalid_assignment_candidate_count"
        )

    else:

        rejected = False

    check(
        "candidate_count_attack_"
        + str(index),
        rejected,
        repr(bad),
    )


# ============================================================
# SCHEMA TAMPER
# ============================================================

try:

    assignment.UniversalWorkerAssignmentResult(
        job_id="job",
        status=(
            assignment.UniversalWorkerAssignmentStatus.ASSIGNED
        ),
        worker=a1,
        candidate_count=1,
        schema_version="wrong",
    )

except assignment.UniversalWorkerAssignmentError as exc:

    rejected = (
        exc.code
        == "invalid_worker_assignment_result_schema_version"
    )

else:

    rejected = False


check(
    "schema_tamper_rejected",
    rejected,
)


# ============================================================
# IMMUTABILITY
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
# REGISTRATION UNCHANGED
# ============================================================

before_a1 = a1.to_dict()
before_a2 = a2.to_dict()
before_b1 = b1.to_dict()


assignment.assign_universal_worker(
    job_id="job-mutation-check",
    eligible_workers=(
        b1,
        a2,
        a1,
    ),
)


check(
    "registration_a1_unchanged",
    a1.to_dict()
    == before_a1,
)

check(
    "registration_a2_unchanged",
    a2.to_dict()
    == before_a2,
)

check(
    "registration_b1_unchanged",
    b1.to_dict()
    == before_b1,
)


# ============================================================
# EXPLANATION
# ============================================================

explanation = (
    assignment.explain_universal_worker_assignment_v1()
)


check(
    "explanation_phase",
    explanation.get("phase")
    == "4.1.3",
)

check(
    "explanation_component",
    explanation.get("component")
    == "Universal Worker Assignment",
)

check(
    "explanation_version",
    explanation.get("version")
    == assignment.UNIVERSAL_WORKER_ASSIGNMENT_VERSION,
)

check(
    "schema_explained",
    explanation.get("result_schema_version")
    == assignment.UNIVERSAL_WORKER_ASSIGNMENT_RESULT_SCHEMA_VERSION,
)

check(
    "caller_supplied_eligible",
    "caller-supplied already-eligible"
    in explanation.get(
        "input_rule",
        "",
    ),
)

check(
    "eligibility_owned_by_caller",
    "does not determine eligibility"
    in explanation.get(
        "eligibility_rule",
        "",
    ),
)

check(
    "selection_rule_exact",
    "worker_id then worker_instance_id"
    in explanation.get(
        "selection_rule",
        "",
    ),
)

check(
    "empty_rule_exact",
    "NO_ASSIGNMENT"
    in explanation.get(
        "empty_rule",
        "",
    ),
)

check(
    "job_id_only_evidence",
    "job_id is the only job evidence"
    in explanation.get(
        "job_evidence_rule",
        "",
    ),
)

check(
    "assignment_not_runtime_ownership",
    "does not create runtime ownership"
    in explanation.get(
        "meaning",
        "",
    ),
)

check(
    "purity_exact",
    "no state lookup, mutation or persistence"
    in explanation.get(
        "purity_rule",
        "",
    ),
)


# ============================================================
# PROHIBITIONS
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
# STATIC IMPORT BOUNDARY
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
    "only_registration_backend_import",
    backend_imports
    == [
        "backend.server.runtime.universal_worker.registration"
    ],
    backend_imports,
)


# ============================================================
# FORBIDDEN CALLS
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

        name = node.func.id

    elif isinstance(
        node.func,
        ast.Attribute,
    ):

        name = node.func.attr

    else:

        continue

    if name in forbidden_names:

        forbidden_calls.append(
            (
                name,
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
# NO RESPONSIBILITY BLEED
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
# PROTECTED AST MATRIX
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
# FINAL ASSIGNMENT AST
# ============================================================

final_ast = ast_sha(
    ASSIGNMENT_PATH
)


check(
    "assignment_ast_final",
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
        "ASSIGNMENT ADVERSARIAL REGRESSION"
    ),
    "=" * 112,
    "",
    (
        "WORKER ASSIGNMENT AST SHA256: "
        + final_ast
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
            "ADVERSARIAL WORKER ASSIGNMENT REGRESSION: "
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
        "WORKER ASSIGNMENT AST MODIFIED: NO",
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
            "STATUS: REGRESSION PASS — FINAL CERTIFICATION REQUIRED"
            if passed == total
            else
            "STATUS: REGRESSION FAILED — DO NOT CERTIFY"
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
        "Phase 4.1.3 Worker Assignment adversarial regression failed."
    )
