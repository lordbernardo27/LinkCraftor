from __future__ import annotations

import ast
import hashlib
import importlib
import itertools
import sys
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

POOL_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "pool.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_9_worker_pool_final_certification.txt"
)

EXPECTED_POOL_AST = (
    "4BA8E641A88A5BB38F78D2B981216765B3327D639EB3BC78E5294C152E84A308"
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
    "worker_assignment": (
        ROOT / "backend/server/runtime/universal_worker/assignment.py",
        "609D3077B84C1791262F8ACA6BD268FD40436DF7775ACB3E9E726BCFC9715F56",
    ),
    "worker_leasing": (
        ROOT / "backend/server/runtime/universal_worker/leasing.py",
        "413B8081D7802211D64B7B811299F9A8A2C54DBAEAB0FC537B1603A3BE397932",
    ),
    "worker_health": (
        ROOT / "backend/server/runtime/universal_worker/health.py",
        "DCC43E77BDC12188DFD15044DA4DA41022B3CEF40F9C4ED06371EE66AA4E5F65",
    ),
    "worker_recovery": (
        ROOT / "backend/server/runtime/universal_worker/recovery.py",
        "C3EF5DBD81205F0087E05F43F6A67A1E0762930DAAD256F957AABC57296D19A5",
    ),
    "worker_scaling": (
        ROOT / "backend/server/runtime/universal_worker/scaling.py",
        "8EC818E4EF4CA7DBCADCFCB93FD99BC80AAD4CE8AEBE1CDE63CCC44FA8488FF6",
    ),
    "worker_shutdown": (
        ROOT / "backend/server/runtime/universal_worker/shutdown.py",
        "DB2197CA791988B01C73CE426ED29891C8BD9FE46DFEC1AC5AE79D1D131C34DD",
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
    "runtime_shutdown_process": (
        ROOT / "backend/server/runtime/runtime_shutdown_process.py",
        "7A159E206C73157064B70D15A1CE4A97AB3D77EBBC77B01A2554BC34224EB272",
    ),
    "runtime_lifecycle_manager": (
        ROOT / "backend/server/runtime/runtime_lifecycle_manager.py",
        "E6200CA0938B5D578954024D6E76E343FB39D9329CFD3ABE4B3AEF86E8204034",
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


def ast_sha(path: Path) -> str:
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


# ============================================================
# PRECONDITIONS
# ============================================================

if not POOL_PATH.exists():
    raise SystemExit(
        "Worker Pool authority missing."
    )


initial_ast = ast_sha(
    POOL_PATH
)

if initial_ast != EXPECTED_POOL_AST:
    raise SystemExit(
        (
            "Worker Pool AST mismatch before final certification.\n"
            "EXPECTED: "
            + EXPECTED_POOL_AST
            + "\nACTUAL:   "
            + initial_ast
        )
    )


for name, (path, expected) in PROTECTED.items():

    actual = ast_sha(
        path
    )

    if actual != expected:
        raise SystemExit(
            (
                "Protected authority mismatch before final certification: "
                + name
                + "\nEXPECTED: "
                + expected
                + "\nACTUAL:   "
                + actual
            )
        )


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

module_name = (
    "backend.server.runtime."
    "universal_worker.pool"
)

sys.modules.pop(
    module_name,
    None,
)

pool = importlib.import_module(
    module_name
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


def make_registration(
    worker_id,
    instance_id,
    worker_type="semantic_worker",
):
    return registration.create_universal_worker_registration(
        worker_id=worker_id,
        worker_type=worker_type,
        worker_instance_id=instance_id,
        runtime_version="runtime-v1",
        host_id="host-1",
        registered_at="2026-08-17T00:00:00+00:00",
    )


# ============================================================
# AST / VERSION / SCHEMA
# ============================================================

pool_ast = ast_sha(
    POOL_PATH
)

check(
    "worker_pool_ast",
    pool_ast
    == EXPECTED_POOL_AST,
    pool_ast,
)

check(
    "version",
    pool.UNIVERSAL_WORKER_POOL_VERSION
    == "universal_worker_pool_v4.1.9",
)

check(
    "member_schema",
    pool.UNIVERSAL_WORKER_POOL_MEMBER_SCHEMA_VERSION
    == "universal_worker_pool_member_schema_v1",
)

check(
    "snapshot_schema",
    pool.UNIVERSAL_WORKER_POOL_SNAPSHOT_SCHEMA_VERSION
    == "universal_worker_pool_snapshot_schema_v1",
)

check(
    "max_pool_id_length",
    pool.MAX_UNIVERSAL_WORKER_POOL_ID_LENGTH
    == 200,
)

check(
    "identity_separator",
    pool.UNIVERSAL_WORKER_POOL_IDENTITY_SEPARATOR
    == "::",
)


# ============================================================
# POOL ID CONTRACT
# ============================================================

check(
    "normalized_pool_id",
    pool.normalize_universal_worker_pool_id(
        "  semantic-main  "
    )
    == "semantic-main",
)

exact_max = (
    "p"
    * pool.MAX_UNIVERSAL_WORKER_POOL_ID_LENGTH
)

check(
    "exact_max_pool_id",
    pool.normalize_universal_worker_pool_id(
        exact_max
    )
    == exact_max,
)


try:
    pool.normalize_universal_worker_pool_id(
        exact_max + "x"
    )

except pool.UniversalWorkerPoolError as exc:
    rejected = (
        exc.code
        == "worker_pool_id_too_long"
    )

else:
    rejected = False

check(
    "pool_id_overflow_rejected",
    rejected,
)


try:
    pool.normalize_universal_worker_pool_id(
        "semantic::main"
    )

except pool.UniversalWorkerPoolError as exc:
    rejected = (
        exc.code
        == "reserved_worker_pool_id_separator"
    )

else:
    rejected = False

check(
    "reserved_separator_rejected",
    rejected,
)


# ============================================================
# MEMBER IDENTITY
# ============================================================

r1 = make_registration(
    "worker-a",
    "instance-1",
)

r2 = make_registration(
    "worker-a",
    "instance-2",
)

r3 = make_registration(
    "worker-b",
    "instance-1",
)

other = make_registration(
    "worker-c",
    "instance-1",
    "other_worker",
)


m1 = (
    pool.create_universal_worker_pool_member(
        r1
    )
)

m2 = (
    pool.create_universal_worker_pool_member(
        r2
    )
)

check(
    "member_identity_1",
    m1.worker_identity
    == "worker-a::instance-1",
)

check(
    "member_identity_2",
    m2.worker_identity
    == "worker-a::instance-2",
)

check(
    "worker_instances_distinct",
    m1.worker_identity
    != m2.worker_identity,
)


# ============================================================
# SNAPSHOT / ORDERING
# ============================================================

snapshot = (
    pool.create_universal_worker_pool_from_registrations(
        pool_id="semantic-main",
        worker_type="semantic_worker",
        registrations=(
            r3,
            r2,
            r1,
        ),
    )
)

check(
    "snapshot_pool_id",
    snapshot.pool_id
    == "semantic-main",
)

check(
    "snapshot_worker_type",
    snapshot.worker_type
    == "semantic_worker",
)

check(
    "snapshot_member_count",
    snapshot.member_count
    == 3,
)

check(
    "deterministic_member_order",
    snapshot.worker_identities
    == (
        "worker-a::instance-1",
        "worker-a::instance-2",
        "worker-b::instance-1",
    ),
)


snapshot_again = (
    pool.create_universal_worker_pool_from_registrations(
        pool_id="semantic-main",
        worker_type="semantic_worker",
        registrations=(
            r1,
            r3,
            r2,
        ),
    )
)

check(
    "snapshot_input_order_independent",
    snapshot
    == snapshot_again,
)


# ============================================================
# EXPLICIT MEMBERSHIP
# ============================================================

same_type_outsider = make_registration(
    "worker-z",
    "instance-1",
    "semantic_worker",
)

check(
    "explicit_membership_true",
    pool.is_universal_worker_pool_member(
        snapshot,
        r1,
    )
    is True,
)

check(
    "same_type_not_implicitly_member",
    pool.is_universal_worker_pool_member(
        snapshot,
        same_type_outsider,
    )
    is False,
)

check(
    "different_type_not_member",
    pool.is_universal_worker_pool_member(
        snapshot,
        other,
    )
    is False,
)


# ============================================================
# ONE WORKER TYPE PER POOL
# ============================================================

try:
    pool.create_universal_worker_pool_from_registrations(
        pool_id="mixed",
        worker_type="semantic_worker",
        registrations=(
            r1,
            other,
        ),
    )

except pool.UniversalWorkerPoolError as exc:
    rejected = (
        exc.code
        == "worker_pool_type_mismatch"
    )

else:
    rejected = False

check(
    "mixed_types_rejected",
    rejected,
)


# ============================================================
# DUPLICATE MEMBERSHIP
# ============================================================

try:
    pool.create_universal_worker_pool_from_registrations(
        pool_id="dup",
        worker_type="semantic_worker",
        registrations=(
            r1,
            r1,
        ),
    )

except pool.UniversalWorkerPoolError as exc:
    rejected = (
        exc.code
        == "duplicate_worker_pool_member"
    )

else:
    rejected = False

check(
    "duplicate_member_rejected",
    rejected,
)


# ============================================================
# IMMUTABLE ADD / REMOVE
# ============================================================

base = (
    pool.create_universal_worker_pool_from_registrations(
        pool_id="semantic-main",
        worker_type="semantic_worker",
        registrations=(
            r2,
        ),
    )
)

added = (
    pool.add_universal_worker_pool_member(
        base,
        r1,
    )
)

check(
    "add_returns_new_snapshot",
    added is not base,
)

check(
    "add_source_unchanged",
    base.worker_identities
    == (
        "worker-a::instance-2",
    ),
)

check(
    "add_result_exact",
    added.worker_identities
    == (
        "worker-a::instance-1",
        "worker-a::instance-2",
    ),
)


removed = (
    pool.remove_universal_worker_pool_member(
        added,
        r1,
    )
)

check(
    "remove_returns_new_snapshot",
    removed is not added,
)

check(
    "remove_source_unchanged",
    added.worker_identities
    == (
        "worker-a::instance-1",
        "worker-a::instance-2",
    ),
)

check(
    "remove_result_exact",
    removed.worker_identities
    == (
        "worker-a::instance-2",
    ),
)


# ============================================================
# MULTI-POOL SNAPSHOT BOUNDARY
# ============================================================

pool_one = (
    pool.create_universal_worker_pool_from_registrations(
        pool_id="one",
        worker_type="semantic_worker",
        registrations=(
            r1,
        ),
    )
)

pool_two = (
    pool.create_universal_worker_pool_from_registrations(
        pool_id="two",
        worker_type="semantic_worker",
        registrations=(
            r1,
        ),
    )
)

check(
    "no_global_exclusivity_claim",
    (
        pool.is_universal_worker_pool_member(
            pool_one,
            r1,
        )
        and
        pool.is_universal_worker_pool_member(
            pool_two,
            r1,
        )
    ),
)


# ============================================================
# IMMUTABILITY
# ============================================================

for obj, field_name in (
    (m1, "worker_id"),
    (m1, "worker_instance_id"),
    (m1, "worker_type"),
    (m1, "schema_version"),
    (snapshot, "pool_id"),
    (snapshot, "worker_type"),
    (snapshot, "members"),
    (snapshot, "schema_version"),
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
        (
            "immutable_"
            + type(obj).__name__
            + "_"
            + field_name
        ),
        immutable,
    )


# ============================================================
# SCHEMA TAMPERING
# ============================================================

try:
    pool.UniversalWorkerPoolMember(
        worker_id="worker-a",
        worker_instance_id="instance-1",
        worker_type="semantic_worker",
        schema_version="wrong",
    )

except pool.UniversalWorkerPoolError as exc:
    rejected = (
        exc.code
        == "invalid_worker_pool_member_schema_version"
    )

else:
    rejected = False

check(
    "member_schema_tamper_rejected",
    rejected,
)


try:
    pool.UniversalWorkerPoolSnapshot(
        pool_id="semantic-main",
        worker_type="semantic_worker",
        members=(),
        schema_version="wrong",
    )

except pool.UniversalWorkerPoolError as exc:
    rejected = (
        exc.code
        == "invalid_worker_pool_snapshot_schema_version"
    )

else:
    rejected = False

check(
    "snapshot_schema_tamper_rejected",
    rejected,
)


# ============================================================
# EXPLANATION CONTRACT
# ============================================================

explanation = (
    pool.explain_universal_worker_pool_v1()
)

check(
    "phase",
    explanation.get(
        "phase"
    )
    == "4.1.9",
)

check(
    "component",
    explanation.get(
        "component"
    )
    == "Universal Worker Pool Infrastructure",
)

check(
    "explanation_version",
    explanation.get(
        "version"
    )
    == pool.UNIVERSAL_WORKER_POOL_VERSION,
)

check(
    "member_schema_explanation",
    explanation.get(
        "member_schema_version"
    )
    == pool.UNIVERSAL_WORKER_POOL_MEMBER_SCHEMA_VERSION,
)

check(
    "snapshot_schema_explanation",
    explanation.get(
        "snapshot_schema_version"
    )
    == pool.UNIVERSAL_WORKER_POOL_SNAPSHOT_SCHEMA_VERSION,
)

check(
    "explicit_membership_rule",
    (
        "explicit"
        in explanation.get(
            "membership_rule",
            "",
        )
        and
        "never inferred"
        in explanation.get(
            "membership_rule",
            "",
        )
    ),
)

check(
    "worker_type_rule",
    "one worker_type"
    in explanation.get(
        "worker_type_rule",
        "",
    ),
)

check(
    "snapshot_rule",
    "new immutable"
    in explanation.get(
        "snapshot_rule",
        "",
    ),
)

check(
    "global_exclusivity_boundary",
    "does not claim global"
    in explanation.get(
        "global_exclusivity_rule",
        "",
    ),
)

check(
    "default_pool_boundary",
    "no implicit default pool"
    in explanation.get(
        "default_pool_rule",
        "",
    ),
)

check(
    "taxonomy_boundary",
    "not invented"
    in explanation.get(
        "taxonomy_rule",
        "",
    ),
)

check(
    "workspace_product_boundary",
    "outside"
    in explanation.get(
        "workspace_product_boundary",
        "",
    ),
)

check(
    "registration_boundary",
    "does not create"
    in explanation.get(
        "registration_boundary",
        "",
    ),
)

check(
    "discovery_assignment_boundary",
    "does not discover or assign"
    in explanation.get(
        "discovery_assignment_boundary",
        "",
    ),
)

check(
    "scaling_boundary",
    "does not perform scaling"
    in explanation.get(
        "scaling_boundary",
        "",
    ),
)

check(
    "shutdown_drain_boundary",
    "do not implicitly"
    in explanation.get(
        "shutdown_drain_boundary",
        "",
    ),
)

check(
    "capability_capacity_boundary",
    "independent authorities"
    in explanation.get(
        "capability_capacity_boundary",
        "",
    ),
)

check(
    "persistence_boundary",
    "does not persist"
    in explanation.get(
        "persistence_boundary",
        "",
    ),
)

check(
    "purity_rule",
    "no external state mutation"
    in explanation.get(
        "purity_rule",
        "",
    ),
)


# ============================================================
# PROHIBITION MATRIX
# ============================================================

required_prohibitions = (
    "does not infer membership from worker_type",
    "does not create an implicit default pool",
    "does not invent shared pool policy",
    "does not invent dedicated pool policy",
    "does not enforce workspace isolation policy",
    "does not enforce product isolation policy",
    "does not create worker registrations",
    "does not modify worker registrations",
    "does not delete worker registrations",
    "does not discover workers",
    "does not assign workers",
    "does not lease workers",
    "does not inspect worker health",
    "does not inspect worker heartbeats",
    "does not detect stale workers",
    "does not recover workers",
    "does not scale workers",
    "does not shut down workers",
    "does not drain workers",
    "does not inspect worker capabilities",
    "does not calculate worker capacity",
    "does not provision workers",
    "does not terminate workers",
    "does not mutate Queue Infrastructure",
    "does not access Runtime State Store",
    "does not access orchestration",
    "does not persist pool state",
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
# STATIC IMPORT / API SURFACE
# ============================================================

source = POOL_PATH.read_text(
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
    "backend_imports_exact",
    backend_imports
    == [
        "backend.server.runtime.universal_worker.registration",
    ],
    backend_imports,
)


expected_all = (
    "UNIVERSAL_WORKER_POOL_VERSION",
    "UNIVERSAL_WORKER_POOL_MEMBER_SCHEMA_VERSION",
    "UNIVERSAL_WORKER_POOL_SNAPSHOT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_POOL_ID_LENGTH",
    "UNIVERSAL_WORKER_POOL_IDENTITY_SEPARATOR",
    "UniversalWorkerPoolError",
    "UniversalWorkerPoolMember",
    "UniversalWorkerPoolSnapshot",
    "normalize_universal_worker_pool_id",
    "create_universal_worker_pool_member",
    "create_universal_worker_pool_snapshot",
    "create_universal_worker_pool_from_registrations",
    "is_universal_worker_pool_member",
    "add_universal_worker_pool_member",
    "remove_universal_worker_pool_member",
    "explain_universal_worker_pool_v1",
)


check(
    "api_surface_exact",
    tuple(
        pool.__all__
    )
    == expected_all,
    pool.__all__,
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
    "now",
    "utcnow",
    "time",
    "sleep",
    "worker_heartbeat",
    "inspect_workers",
    "discover_universal_workers",
    "assign_universal_worker",
    "acquire_universal_worker_lease",
    "renew_universal_worker_lease",
    "release_universal_worker_lease",
    "evaluate_universal_worker_health",
    "evaluate_universal_worker_recovery",
    "evaluate_universal_worker_scaling",
    "evaluate_universal_worker_shutdown",
    "get_runtime_state_store_registry",
    "enqueue_job",
    "dequeue_job",
    "requeue_job",
    "dispatch_job",
    "execute_job",
    "shutdown",
    "terminate",
    "kill",
    "provision",
    "save",
    "persist",
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
        call_name = node.func.id

    elif isinstance(
        node.func,
        ast.Attribute,
    ):
        call_name = node.func.attr

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
# CANONICAL FINGERPRINT
# ============================================================

fingerprint_material = "|".join(
    (
        "phase_4_1_9_worker_pool",
        pool.UNIVERSAL_WORKER_POOL_VERSION,
        pool.UNIVERSAL_WORKER_POOL_MEMBER_SCHEMA_VERSION,
        pool.UNIVERSAL_WORKER_POOL_SNAPSHOT_SCHEMA_VERSION,
        pool_ast,
        "pool_id",
        "worker_type",
        "worker_id",
        "worker_instance_id",
        "explicit_membership",
        "membership_not_inferred_from_worker_type",
        "one_worker_type_per_pool",
        "worker_identity_worker_id_instance_id",
        "deterministic_member_order",
        "immutable_pool_snapshot",
        "add_returns_new_snapshot",
        "remove_returns_new_snapshot",
        "no_implicit_default_pool",
        "no_shared_dedicated_system_taxonomy",
        "no_global_one_pool_per_worker_claim",
        "workspace_product_policy_external",
        "registration_identity_consumed_not_mutated",
        "discovery_assignment_external",
        "scaling_external",
        "shutdown_drain_do_not_remove_membership",
        "capability_capacity_external",
        "pool_state_not_persisted",
        "pure_logical_membership_authority",
    )
)


pool_fingerprint = (
    hashlib.sha256(
        fingerprint_material.encode(
            "utf-8"
        )
    ).hexdigest().upper()
)


check(
    "fingerprint_generated",
    len(
        pool_fingerprint
    )
    == 64,
    pool_fingerprint,
)


# ============================================================
# FINAL AST RECHECK
# ============================================================

final_ast = ast_sha(
    POOL_PATH
)

check(
    "final_ast_unchanged",
    final_ast
    == EXPECTED_POOL_AST,
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
        "PHASE 4.1.9 — UNIVERSAL WORKER POOL "
        "INFRASTRUCTURE FINAL CERTIFICATION"
    ),
    "=" * 112,
    "",
    (
        "WORKER POOL AST SHA256: "
        + pool_ast
    ),
    (
        "WORKER POOL FINGERPRINT: "
        + pool_fingerprint
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
            "FINAL WORKER POOL CERTIFICATION: "
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
        "WORKER POOL MODIFIED DURING CERTIFICATION: NO",
        "4.1.1 WORKER REGISTRATION MODIFIED: NO",
        "4.1.2 WORKER DISCOVERY MODIFIED: NO",
        "4.1.3 WORKER ASSIGNMENT MODIFIED: NO",
        "4.1.4 WORKER LEASING MODIFIED: NO",
        "4.1.5 WORKER HEALTH MODIFIED: NO",
        "4.1.6 WORKER RECOVERY MODIFIED: NO",
        "4.1.7 WORKER SCALING MODIFIED: NO",
        "4.1.8 WORKER SHUTDOWN MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "RUNTIME SHUTDOWN PROCESS MODIFIED: NO",
        "RUNTIME LIFECYCLE MANAGER MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "IMPLICIT DEFAULT POOL CREATED: NO",
        "SHARED/DEDICATED/SYSTEM TAXONOMY INVENTED: NO",
        "GLOBAL ONE-POOL-PER-WORKER POLICY INVENTED: NO",
        "MEMBERSHIP INFERRED FROM WORKER TYPE: NO",
        "WORKER REGISTRATION MUTATED: NO",
        "WORKER DISCOVERED: NO",
        "WORKER ASSIGNED: NO",
        "WORKER LEASED: NO",
        "WORKER HEALTH INSPECTED: NO",
        "WORKER HEARTBEAT INSPECTED: NO",
        "STALE WORKER DETECTED: NO",
        "WORKER RECOVERY PERFORMED: NO",
        "WORKER SCALING PERFORMED: NO",
        "WORKER SHUTDOWN PERFORMED: NO",
        "WORKER DRAIN PERFORMED: NO",
        "WORKER CAPABILITY INSPECTED: NO",
        "WORKER CAPACITY CALCULATED: NO",
        "WORKER PROVISIONED/TERMINATED: NO",
        "QUEUE MUTATED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "POOL STATE PERSISTED: NO",
        "",
        (
            "PHASE 4.1.9 FREEZE CANDIDATE: "
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
        "Phase 4.1.9 Worker Pool final certification failed."
    )
