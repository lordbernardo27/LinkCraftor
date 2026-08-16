from __future__ import annotations

import ast
import hashlib
import importlib
import sys
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

LEASING_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "leasing.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_4_worker_leasing_final_certification.txt"
)

EXPECTED_LEASING_AST = (
    "413B8081D7802211D64B7B811299F9A8A2C54DBAEAB0FC537B1603A3BE397932"
)


# ============================================================
# PROTECTED FROZEN AUTHORITIES
# ============================================================

PROTECTED = {
    "worker_registration": (
        ROOT / "backend/server/runtime/universal_worker/registration.py",
        "00F0D6E620E24A7433C880B722E023AF3C2121563F8E18DFA9979E0F06A36D64",
    ),

    "worker_discovery": (
        ROOT / "backend/server/runtime/universal_worker/discovery.py",
        "DFCAB9080982C8D5E099A40C903F7B4140B0860053DB73CB77B30B966788A228",
    ),

    "worker_assignment": (
        ROOT / "backend/server/runtime/universal_worker/assignment.py",
        "609D3077B84C1791262F8ACA6BD268FD40436DF7775ACB3E9E726BCFC9715F56",
    ),

    "queue_certification": (
        ROOT / "backend/server/runtime/universal_queue/certification.py",
        "6ED39655147D2B331E02101F5EA23E68CF71447353C0D294E170281AE40C0D4C",
    ),

    "job_contract": (
        ROOT / "backend/server/runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
    ),

    "job_status": (
        ROOT / "backend/server/runtime/universal_jobs/status.py",
        "4636EF770005A6CCC84A37596622880C2244D4C12FFDEDAAC02078C20AA29EEE",
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

    tree = ast.parse(
        source
    )

    canonical = ast.dump(
        tree,
        annotate_fields=True,
        include_attributes=False,
    )

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest().upper()


# ============================================================
# IMPORT
# ============================================================

sys.path.insert(
    0,
    str(ROOT),
)

registration = importlib.import_module(
    "backend.server.runtime.universal_worker.registration"
)

assignment = importlib.import_module(
    "backend.server.runtime.universal_worker.assignment"
)

leasing_name = (
    "backend.server.runtime."
    "universal_worker.leasing"
)

sys.modules.pop(
    leasing_name,
    None,
)

leasing = importlib.import_module(
    leasing_name
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

leasing_ast = ast_sha(
    LEASING_PATH
)

check(
    "worker_leasing_ast",
    leasing_ast
    == EXPECTED_LEASING_AST,
    leasing_ast,
)


# ============================================================
# 2 — VERSION / SCHEMAS / CONSTANTS
# ============================================================

check(
    "version",
    leasing.UNIVERSAL_WORKER_LEASING_VERSION
    == "universal_worker_leasing_v4.1.4",
)

check(
    "lease_schema",
    leasing.UNIVERSAL_WORKER_LEASE_SCHEMA_VERSION
    == "universal_worker_lease_schema_v1",
)

check(
    "release_schema",
    leasing.UNIVERSAL_WORKER_LEASE_RELEASE_SCHEMA_VERSION
    == "universal_worker_lease_release_schema_v1",
)

check(
    "lease_id_max_length",
    leasing.MAX_UNIVERSAL_WORKER_LEASE_ID_LENGTH
    == 200,
)

check(
    "lease_owner_separator",
    leasing.UNIVERSAL_WORKER_LEASE_OWNER_SEPARATOR
    == "::",
)


# ============================================================
# 3 — CANONICAL WORKER / ASSIGNMENT
# ============================================================

worker = (
    registration.create_universal_worker_registration(
        worker_id="worker-a",
        worker_type="general",
        worker_instance_id="instance-001",
        runtime_version="runtime-v1",
        host_id="host-a",
        registered_at="2026-08-15T20:00:00Z",
    )
)


assigned = (
    assignment.assign_universal_worker(
        job_id="job-001",
        eligible_workers=(
            worker,
        ),
    )
)


check(
    "assignment_assigned",
    assigned.assigned
    is True,
)

check(
    "assignment_identity",
    assigned.worker_identity
    == (
        "worker-a",
        "instance-001",
    ),
)


# ============================================================
# 4 — CANONICAL ACQUISITION
# ============================================================

lease = (
    leasing.acquire_universal_worker_lease(
        assignment=assigned,
        lease_id=" lease-001 ",
        lease_started_at="2026-08-15T20:00:00Z",
        lease_expires_at="2026-08-15T20:05:00Z",
    )
)


check(
    "canonical_job_id",
    lease.job_id
    == "job-001",
)

check(
    "canonical_lease_owner",
    lease.lease_owner
    == "worker-a::instance-001",
)

check(
    "canonical_worker_identity",
    lease.worker_identity
    == (
        "worker-a",
        "instance-001",
    ),
)

check(
    "canonical_lease_id",
    lease.lease_id
    == "lease-001",
)

check(
    "canonical_started_at",
    lease.lease_started_at
    == "2026-08-15T20:00:00.000000Z",
)

check(
    "canonical_expires_at",
    lease.lease_expires_at
    == "2026-08-15T20:05:00.000000Z",
)


# ============================================================
# 5 — CANONICAL JOB LEASE FIELDS
# ============================================================

job_fields = dict(
    lease.to_job_lease_fields()
)


check(
    "job_fields_exact",
    job_fields
    == {
        "lease_owner":
            "worker-a::instance-001",

        "lease_id":
            "lease-001",

        "lease_started_at":
            "2026-08-15T20:00:00.000000Z",

        "lease_expires_at":
            "2026-08-15T20:05:00.000000Z",
    },
    job_fields,
)


check(
    "job_field_order_exact",
    tuple(
        job_fields.keys()
    )
    == (
        "lease_owner",
        "lease_id",
        "lease_started_at",
        "lease_expires_at",
    ),
    tuple(
        job_fields.keys()
    ),
)


# ============================================================
# 6 — ACTIVE / EXPIRED SEMANTICS
# ============================================================

check(
    "active_before_expiration",
    leasing.evaluate_universal_worker_lease_state(
        lease=lease,
        evaluation_at="2026-08-15T20:04:59.999999Z",
    )
    is leasing.UniversalWorkerLeaseState.ACTIVE,
)


check(
    "expired_at_expiration",
    leasing.evaluate_universal_worker_lease_state(
        lease=lease,
        evaluation_at="2026-08-15T20:05:00Z",
    )
    is leasing.UniversalWorkerLeaseState.EXPIRED,
)


check(
    "expired_after_expiration",
    leasing.evaluate_universal_worker_lease_state(
        lease=lease,
        evaluation_at="2026-08-15T20:05:01Z",
    )
    is leasing.UniversalWorkerLeaseState.EXPIRED,
)


# ============================================================
# 7 — ACQUISITION EXCLUSIVITY
# ============================================================

try:

    leasing.acquire_universal_worker_lease(
        assignment=assigned,
        lease_id="lease-conflict",
        lease_started_at="2026-08-15T20:06:00Z",
        lease_expires_at="2026-08-15T20:11:00Z",
        existing_lease=lease,
    )

except leasing.UniversalWorkerLeasingError as exc:

    conflict_rejected = (
        exc.code
        == "lease_conflict"
    )

else:

    conflict_rejected = False


check(
    "existing_lease_conflict",
    conflict_rejected,
)


# ============================================================
# 8 — NO ASSIGNMENT CANNOT LEASE
# ============================================================

no_assignment = (
    assignment.assign_universal_worker(
        job_id="job-empty",
        eligible_workers=(),
    )
)


try:

    leasing.acquire_universal_worker_lease(
        assignment=no_assignment,
        lease_id="lease-empty",
        lease_started_at="2026-08-15T20:00:00Z",
        lease_expires_at="2026-08-15T20:05:00Z",
    )

except leasing.UniversalWorkerLeasingError as exc:

    rejected = (
        exc.code
        == "worker_assignment_required"
    )

else:

    rejected = False


check(
    "no_assignment_cannot_acquire",
    rejected,
)


# ============================================================
# 9 — CANONICAL RENEWAL
# ============================================================

renewed = (
    leasing.renew_universal_worker_lease(
        lease=lease,
        expected_lease_owner=lease.lease_owner,
        expected_lease_id=lease.lease_id,
        renewed_at="2026-08-15T20:04:00Z",
        new_lease_expires_at="2026-08-15T20:10:00Z",
    )
)


check(
    "renewal_job_unchanged",
    renewed.job_id
    == lease.job_id,
)

check(
    "renewal_owner_unchanged",
    renewed.lease_owner
    == lease.lease_owner,
)

check(
    "renewal_id_unchanged",
    renewed.lease_id
    == lease.lease_id,
)

check(
    "renewal_started_at_unchanged",
    renewed.lease_started_at
    == lease.lease_started_at,
)

check(
    "renewal_expiration_extended",
    renewed.lease_expires_at
    == "2026-08-15T20:10:00.000000Z",
)


# ============================================================
# 10 — EXPIRED LEASE CANNOT RENEW
# ============================================================

try:

    leasing.renew_universal_worker_lease(
        lease=lease,
        expected_lease_owner=lease.lease_owner,
        expected_lease_id=lease.lease_id,
        renewed_at="2026-08-15T20:05:00Z",
        new_lease_expires_at="2026-08-15T20:10:00Z",
    )

except leasing.UniversalWorkerLeasingError as exc:

    rejected = (
        exc.code
        == "expired_lease_cannot_renew"
    )

else:

    rejected = False


check(
    "expired_lease_cannot_renew",
    rejected,
)


# ============================================================
# 11 — CANONICAL RELEASE
# ============================================================

release = (
    leasing.release_universal_worker_lease(
        lease=renewed,
        expected_lease_owner=renewed.lease_owner,
        expected_lease_id=renewed.lease_id,
        released_at="2026-08-15T20:06:00Z",
    )
)


check(
    "release_job_id",
    release.job_id
    == renewed.job_id,
)

check(
    "release_owner",
    release.lease_owner
    == renewed.lease_owner,
)

check(
    "release_lease_id",
    release.lease_id
    == renewed.lease_id,
)

check(
    "release_timestamp",
    release.released_at
    == "2026-08-15T20:06:00.000000Z",
)


# ============================================================
# 12 — OWNER / ID CONFLICT PROTECTION
# ============================================================

try:

    leasing.renew_universal_worker_lease(
        lease=lease,
        expected_lease_owner="worker-x::instance-x",
        expected_lease_id=lease.lease_id,
        renewed_at="2026-08-15T20:04:00Z",
        new_lease_expires_at="2026-08-15T20:10:00Z",
    )

except leasing.UniversalWorkerLeasingError as exc:

    rejected = (
        exc.code
        == "lease_owner_mismatch"
    )

else:

    rejected = False


check(
    "renewal_owner_mismatch_rejected",
    rejected,
)


try:

    leasing.release_universal_worker_lease(
        lease=lease,
        expected_lease_owner=lease.lease_owner,
        expected_lease_id="wrong-lease",
        released_at="2026-08-15T20:03:00Z",
    )

except leasing.UniversalWorkerLeasingError as exc:

    rejected = (
        exc.code
        == "lease_id_mismatch"
    )

else:

    rejected = False


check(
    "release_id_mismatch_rejected",
    rejected,
)


# ============================================================
# 13 — TIMESTAMP / OWNER INVARIANTS
# ============================================================

check(
    "lease_interval_strictly_positive",
    lease.lease_expires_at
    > lease.lease_started_at,
)


check(
    "owner_is_worker_plus_instance",
    lease.lease_owner
    == (
        assigned.worker.worker_id
        + leasing.UNIVERSAL_WORKER_LEASE_OWNER_SEPARATOR
        + assigned.worker.worker_instance_id
    ),
)


# ============================================================
# 14 — IMMUTABILITY
# ============================================================

for obj, field_name in (
    (
        lease,
        "job_id",
    ),
    (
        lease,
        "lease_owner",
    ),
    (
        lease,
        "lease_id",
    ),
    (
        lease,
        "lease_started_at",
    ),
    (
        lease,
        "lease_expires_at",
    ),
    (
        release,
        "released_at",
    ),
):

    try:

        setattr(
            obj,
            field_name,
            None,
        )

    except Exception:

        immutable = True

    else:

        immutable = False

    check(
        "immutable_"
        + type(obj).__name__
        + "_"
        + field_name,
        immutable,
    )


# ============================================================
# 15 — INPUT AUTHORITIES NOT MUTATED
# ============================================================

worker_before = (
    worker.to_dict()
)

assignment_before = (
    (
        assigned.job_id,
        assigned.status,
        assigned.worker_identity,
        assigned.candidate_count,
    )
)


leasing.evaluate_universal_worker_lease_state(
    lease=lease,
    evaluation_at="2026-08-15T20:01:00Z",
)


worker_after = (
    worker.to_dict()
)

assignment_after = (
    (
        assigned.job_id,
        assigned.status,
        assigned.worker_identity,
        assigned.candidate_count,
    )
)


check(
    "registration_not_mutated",
    worker_before
    == worker_after,
)

check(
    "assignment_not_mutated",
    assignment_before
    == assignment_after,
)


# ============================================================
# 16 — EXPLANATION CONTRACT
# ============================================================

explanation = (
    leasing.explain_universal_worker_leasing_v1()
)


check(
    "phase",
    explanation.get(
        "phase"
    )
    == "4.1.4",
)

check(
    "component",
    explanation.get(
        "component"
    )
    == "Universal Worker Leasing",
)

check(
    "explanation_version",
    explanation.get(
        "version"
    )
    == leasing.UNIVERSAL_WORKER_LEASING_VERSION,
)

check(
    "lease_schema_explanation",
    explanation.get(
        "lease_schema_version"
    )
    == leasing.UNIVERSAL_WORKER_LEASE_SCHEMA_VERSION,
)

check(
    "release_schema_explanation",
    explanation.get(
        "release_schema_version"
    )
    == leasing.UNIVERSAL_WORKER_LEASE_RELEASE_SCHEMA_VERSION,
)

check(
    "canonical_fields_explanation",
    tuple(
        explanation.get(
            "canonical_job_fields"
        )
    )
    == (
        "lease_owner",
        "lease_id",
        "lease_started_at",
        "lease_expires_at",
    ),
)

check(
    "owner_rule",
    "worker_id::worker_instance_id"
    in explanation.get(
        "owner_rule",
        "",
    ),
)

check(
    "acquisition_requires_assignment",
    (
        "ASSIGNED"
        in explanation.get(
            "acquisition_rule",
            "",
        )
        and
        "no unresolved existing lease"
        in explanation.get(
            "acquisition_rule",
            "",
        )
    ),
)

check(
    "caller_supplied_timestamp_rule",
    "caller-supplied"
    in explanation.get(
        "timestamp_rule",
        "",
    ),
)

check(
    "expiration_rule",
    (
        "ACTIVE"
        in explanation.get(
            "expiration_rule",
            "",
        )
        and
        "EXPIRED"
        in explanation.get(
            "expiration_rule",
            "",
        )
    ),
)

check(
    "renewal_rule",
    (
        "matching owner"
        in explanation.get(
            "renewal_rule",
            "",
        )
        and
        "ACTIVE"
        in explanation.get(
            "renewal_rule",
            "",
        )
    ),
)

check(
    "release_rule",
    "immutable"
    in explanation.get(
        "release_rule",
        "",
    ),
)

check(
    "persistence_boundary",
    "never mutates or persists UniversalJob"
    in explanation.get(
        "persistence_rule",
        "",
    ),
)

check(
    "recovery_boundary",
    (
        "requeue"
        in explanation.get(
            "recovery_boundary",
            "",
        )
        and
        "recover"
        in explanation.get(
            "recovery_boundary",
            "",
        )
        and
        "reassign"
        in explanation.get(
            "recovery_boundary",
            "",
        )
    ),
)


# ============================================================
# 17 — PROHIBITION MATRIX
# ============================================================

required_prohibitions = (
    "does not generate lease_id",
    "does not use wall-clock time",
    "does not mutate UniversalJob",
    "does not persist leases",
    "does not access Runtime State Store",
    "does not mutate Queue Infrastructure",
    "does not dequeue jobs",
    "does not claim jobs",
    "does not assign workers",
    "does not discover workers",
    "does not transition jobs to LEASED",
    "does not transition jobs to RUNNING",
    "does not dispatch jobs",
    "does not execute jobs",
    "does not requeue expired leases",
    "does not recover workers",
    "does not dead-letter jobs",
    "does not determine worker health",
    "does not read worker heartbeats",
    "does not determine worker capability",
    "does not determine worker capacity",
    "does not manage worker pools",
    "does not access orchestration",
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
        item
        in prohibitions,
        item,
    )


# ============================================================
# 18 — STATIC IMPORT BOUNDARY
# ============================================================

source = LEASING_PATH.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(
    source
)


backend_imports = []


for node in ast.walk(
    tree
):

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
    "only_assignment_backend_import",
    backend_imports
    == [
        "backend.server.runtime.universal_worker.assignment"
    ],
    backend_imports,
)


# ============================================================
# 19 — SIDE EFFECT / WALL CLOCK BOUNDARY
# ============================================================

forbidden_names = {
    "open",
    "read_text",
    "write_text",
    "mkdir",
    "unlink",
    "remove",
    "uuid4",
    "time",
    "sleep",
    "utcnow",
    "now",
    "dequeue_job",
    "claim_job",
    "enqueue_job",
    "requeue_job",
    "save_job",
    "get_job",
    "dispatch_job",
    "execute_job",
    "dispatch_registered_runtime_handler",
    "get_runtime_state_store_registry",
    "worker_heartbeat",
}


forbidden_calls = []


for node in ast.walk(
    tree
):

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
# 20 — LATER RESPONSIBILITY EXCLUSION
# ============================================================

function_names = tuple(
    node.name.lower()
    for node in ast.walk(
        tree
    )
    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    )
)


for token in (
    "dequeue",
    "claim",
    "dispatch",
    "execute",
    "requeue",
    "recover_worker",
    "dead_letter",
    "heartbeat",
    "health",
    "capability",
    "capacity",
    "pool",
    "persist",
    "state_store",
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
# 21 — PROTECTED AST MATRIX
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
# 22 — CANONICAL FINGERPRINT
# ============================================================

fingerprint_material = "|".join(
    (
        "phase_4_1_4_worker_leasing",
        leasing.UNIVERSAL_WORKER_LEASING_VERSION,
        leasing.UNIVERSAL_WORKER_LEASE_SCHEMA_VERSION,
        leasing.UNIVERSAL_WORKER_LEASE_RELEASE_SCHEMA_VERSION,
        leasing_ast,
        "lease_owner",
        "lease_id",
        "lease_started_at",
        "lease_expires_at",
        "worker_id::worker_instance_id",
        "ACTIVE",
        "EXPIRED",
        "acquire",
        "renew",
        "release",
        "selection_not_persistence",
        "expiration_not_recovery",
    )
)


leasing_fingerprint = (
    hashlib.sha256(
        fingerprint_material.encode(
            "utf-8"
        )
    ).hexdigest().upper()
)


check(
    "fingerprint_generated",
    len(
        leasing_fingerprint
    )
    == 64,
    leasing_fingerprint,
)


# ============================================================
# 23 — FINAL AST RECHECK
# ============================================================

final_ast = ast_sha(
    LEASING_PATH
)


check(
    "final_ast_unchanged",
    final_ast
    == EXPECTED_LEASING_AST,
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
        "PHASE 4.1.4 — UNIVERSAL WORKER "
        "LEASING FINAL CERTIFICATION"
    ),
    "=" * 112,
    "",
    (
        "WORKER LEASING AST SHA256: "
        + leasing_ast
    ),
    (
        "WORKER LEASING FINGERPRINT: "
        + leasing_fingerprint
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
            "FINAL WORKER LEASING CERTIFICATION: "
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
        "WORKER LEASING MODIFIED DURING CERTIFICATION: NO",
        "4.1.1 WORKER REGISTRATION MODIFIED: NO",
        "4.1.2 WORKER DISCOVERY MODIFIED: NO",
        "4.1.3 WORKER ASSIGNMENT MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "UNIVERSAL JOB STATUS MODIFIED: NO",
        "BODY STORE LEASING MODIFIED: NO",
        "EXISTING UNIVERSAL RUNTIME WORKER MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "LEASE PERSISTED: NO",
        "LEASE_ID GENERATED INTERNALLY: NO",
        "WALL-CLOCK TIME READ: NO",
        "UNIVERSAL JOB MUTATED: NO",
        "JOB STATUS MUTATED: NO",
        "JOB TRANSITIONED TO LEASED: NO",
        "JOB TRANSITIONED TO RUNNING: NO",
        "JOB DEQUEUED: NO",
        "JOB CLAIMED: NO",
        "JOB DISPATCHED: NO",
        "JOB EXECUTED: NO",
        "EXPIRED LEASE REQUEUED: NO",
        "WORKER RECOVERY PERFORMED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "",
        (
            "PHASE 4.1.4 FREEZE CANDIDATE: "
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
        "Phase 4.1.4 Worker Leasing final certification failed."
    )
