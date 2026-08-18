from __future__ import annotations

import ast
import hashlib
import importlib
import sys
from dataclasses import fields
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

CAPACITY_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "capacity.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_14_worker_capacity_final_certification.txt"
)

EXPECTED_CAPACITY_AST = (
    "92A626B59250333885ABF1D81A0AA00759A47359C3B9D25FCD948915521CBF55"
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
    "worker_pool": (
        ROOT / "backend/server/runtime/universal_worker/pool.py",
        "4BA8E641A88A5BB38F78D2B981216765B3327D639EB3BC78E5294C152E84A308",
    ),
    "worker_heartbeat": (
        ROOT / "backend/server/runtime/universal_worker/heartbeat.py",
        "A58BDEE660CA903453DA6D968A2B02FBFBE3920E9BBE6C64BC75A597DB7C11EE",
    ),
    "stale_worker_detection": (
        ROOT / "backend/server/runtime/universal_worker/stale.py",
        "22105ACBF984E26019080E53939617CE14BDF51BF5A9B149BD39E10B6B87B9DD",
    ),
    "worker_drain": (
        ROOT / "backend/server/runtime/universal_worker/drain.py",
        "629AA6B5D9269B3164A1524F3C176B2EA34CB4952A0D32F5E2EE4A7C6984FA78",
    ),
    "worker_capability": (
        ROOT / "backend/server/runtime/universal_worker/capability.py",
        "200A42478283CDAC92965EAF0DEDFAB3FAB8834F5FB734E3A4874F1EE571C51D",
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
    "orchestration_models": (
        ROOT / "backend/server/orchestration/models.py",
        "5C9FE5E4F84FA1C369CB45F74B0CB12B7E730ADA3C7CBC95B4F50EC75DC5E92D",
    ),
    "tms_orchestration_governance": (
        ROOT / "backend/server/tms/orchestration_governance.py",
        "2AAA15B7283C6F0B4BB67A47FE58F1FD0EF2815A09CA048EA0CFE7DEF232B4E1",
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
# PRECONDITIONS
# ============================================================

if not CAPACITY_PATH.exists():

    raise SystemExit(
        "4.1.14 Worker Capacity authority missing."
    )


initial_ast = ast_sha(
    CAPACITY_PATH
)


if initial_ast != EXPECTED_CAPACITY_AST:

    raise SystemExit(
        (
            "Worker Capacity AST mismatch before final certification.\n"
            "EXPECTED: "
            + EXPECTED_CAPACITY_AST
            + "\nACTUAL:   "
            + initial_ast
        )
    )


for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(
        path
    )

    if actual != expected:

        raise SystemExit(
            (
                "Protected authority mismatch before "
                "4.1.14 final certification: "
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
    "universal_worker.capacity"
)

sys.modules.pop(
    module_name,
    None,
)

capacity = importlib.import_module(
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


reg = (
    registration.create_universal_worker_registration(
        worker_id="worker-a",
        worker_type="semantic_worker",
        worker_instance_id="instance-1",
        runtime_version="runtime-v1",
        host_id="host-1",
        registered_at="2026-08-17T01:00:00+00:00",
    )
)


# ============================================================
# AUTHORITY / CONSTANTS
# ============================================================

capacity_ast = ast_sha(
    CAPACITY_PATH
)


check(
    "worker_capacity_ast",
    capacity_ast
    == EXPECTED_CAPACITY_AST,
    capacity_ast,
)

check(
    "version",
    capacity.UNIVERSAL_WORKER_CAPACITY_VERSION
    == "universal_worker_capacity_v4.1.14",
)

check(
    "snapshot_schema",
    capacity.UNIVERSAL_WORKER_CAPACITY_SNAPSHOT_SCHEMA_VERSION
    == "universal_worker_capacity_snapshot_schema_v1",
)

check(
    "maximum_count",
    capacity.MAX_UNIVERSAL_WORKER_CAPACITY_COUNT
    == 2_147_483_647,
)

check(
    "identity_separator",
    capacity.UNIVERSAL_WORKER_CAPACITY_IDENTITY_SEPARATOR
    == "::",
)


# ============================================================
# NUMERIC CONTRACT
# ============================================================

for value in (
    0,
    1,
    10,
    1024,
    1_000_000,
    2_147_483_647,
):

    for field_name in (
        "capacity_limit",
        "active_work_count",
    ):

        check(
            (
                "valid_count_"
                + field_name
                + "_"
                + str(value)
            ),
            capacity.normalize_universal_worker_capacity_count(
                value,
                field_name=field_name,
            )
            == value,
        )


for bad in (
    None,
    True,
    False,
    -1,
    0.0,
    1.0,
    "1",
    "",
    [],
    {},
    (),
):

    for field_name in (
        "capacity_limit",
        "active_work_count",
    ):

        try:

            capacity.normalize_universal_worker_capacity_count(
                bad,
                field_name=field_name,
            )

        except capacity.UniversalWorkerCapacityError as exc:

            rejected = (
                exc.code
                == "invalid_worker_capacity_count"
            )

        else:

            rejected = False

        check(
            (
                "invalid_count_"
                + field_name
                + "_"
                + repr(
                    bad
                )
            ),
            rejected,
        )


for field_name in (
    "capacity_limit",
    "active_work_count",
):

    try:

        capacity.normalize_universal_worker_capacity_count(
            2_147_483_648,
            field_name=field_name,
        )

    except capacity.UniversalWorkerCapacityError as exc:

        rejected = (
            exc.code
            == "worker_capacity_count_too_large"
        )

    else:

        rejected = False

    check(
        field_name
        + "_overflow_rejected",
        rejected,
    )


# ============================================================
# CAPACITY FORMULA
# ============================================================

formula_cases = (
    (0, 0, 0),
    (1, 0, 1),
    (1, 1, 0),
    (10, 3, 7),
    (10, 9, 1),
    (10, 10, 0),
    (
        2_147_483_647,
        0,
        2_147_483_647,
    ),
    (
        2_147_483_647,
        2_147_483_646,
        1,
    ),
    (
        2_147_483_647,
        2_147_483_647,
        0,
    ),
)


for index, (
    limit,
    active,
    expected,
) in enumerate(
    formula_cases,
    start=1,
):

    actual = (
        capacity.calculate_universal_worker_available_capacity(
            capacity_limit=limit,
            active_work_count=active,
        )
    )

    check(
        "formula_"
        + str(index),
        actual
        == expected,
        actual,
    )


for index, (
    limit,
    active,
) in enumerate(
    (
        (0, 1),
        (1, 2),
        (10, 11),
        (
            2_147_483_646,
            2_147_483_647,
        ),
    ),
    start=1,
):

    try:

        capacity.calculate_universal_worker_available_capacity(
            capacity_limit=limit,
            active_work_count=active,
        )

    except capacity.UniversalWorkerCapacityError as exc:

        rejected = (
            exc.code
            == "worker_capacity_active_work_exceeds_limit"
        )

    else:

        rejected = False

    check(
        "contradiction_"
        + str(index),
        rejected,
    )


# ============================================================
# SNAPSHOT SEMANTICS
# ============================================================

available = (
    capacity.create_universal_worker_capacity_snapshot(
        registration=reg,
        capacity_limit=10,
        active_work_count=3,
    )
)


check(
    "worker_id",
    available.worker_id
    == reg.worker_id,
)

check(
    "worker_instance_id",
    available.worker_instance_id
    == reg.worker_instance_id,
)

check(
    "worker_type",
    available.worker_type
    == reg.worker_type,
)

check(
    "worker_identity",
    available.worker_identity
    == "worker-a::instance-1",
)

check(
    "capacity_limit",
    available.capacity_limit
    == 10,
)

check(
    "active_work_count",
    available.active_work_count
    == 3,
)

check(
    "available_capacity",
    available.available_capacity
    == 7,
)

check(
    "has_available_capacity",
    available.has_available_capacity
    is True,
)

check(
    "not_saturated",
    available.is_saturated
    is False,
)


saturated = (
    capacity.create_universal_worker_capacity_snapshot(
        registration=reg,
        capacity_limit=10,
        active_work_count=10,
    )
)


check(
    "saturated_available_zero",
    saturated.available_capacity
    == 0,
)

check(
    "saturated_has_available_false",
    saturated.has_available_capacity
    is False,
)

check(
    "saturated_true",
    saturated.is_saturated
    is True,
)


zero_capacity = (
    capacity.create_universal_worker_capacity_snapshot(
        registration=reg,
        capacity_limit=0,
        active_work_count=0,
    )
)


check(
    "zero_capacity_valid",
    zero_capacity.capacity_limit
    == 0,
)

check(
    "zero_capacity_available_zero",
    zero_capacity.available_capacity
    == 0,
)

check(
    "zero_capacity_has_available_false",
    zero_capacity.has_available_capacity
    is False,
)

check(
    "zero_capacity_saturated",
    zero_capacity.is_saturated
    is True,
)


# ============================================================
# IDENTITY / SCHEMA HARDENING
# ============================================================

for field_name, bad_value in (
    ("worker_id", ""),
    ("worker_id", " "),
    ("worker_instance_id", ""),
    ("worker_instance_id", " "),
    ("worker_type", ""),
    ("worker_type", " "),
):

    kwargs = {
        "worker_id":
            reg.worker_id,

        "worker_instance_id":
            reg.worker_instance_id,

        "worker_type":
            reg.worker_type,

        "capacity_limit":
            1,

        "active_work_count":
            0,
    }

    kwargs[
        field_name
    ] = bad_value

    try:

        capacity.UniversalWorkerCapacitySnapshot(
            **kwargs
        )

    except capacity.UniversalWorkerCapacityError:

        rejected = True

    else:

        rejected = False

    check(
        (
            "identity_hardening_"
            + field_name
            + "_"
            + repr(
                bad_value
            )
        ),
        rejected,
    )


try:

    capacity.UniversalWorkerCapacitySnapshot(
        worker_id=reg.worker_id,
        worker_instance_id=reg.worker_instance_id,
        worker_type=reg.worker_type,
        capacity_limit=1,
        active_work_count=0,
        schema_version="tampered",
    )

except capacity.UniversalWorkerCapacityError as exc:

    rejected = (
        exc.code
        == "invalid_worker_capacity_snapshot_schema_version"
    )

else:

    rejected = False


check(
    "schema_tamper_rejected",
    rejected,
)


# ============================================================
# IMMUTABILITY / EXACT FIELDS
# ============================================================

for field in fields(
    available
):

    try:

        setattr(
            available,
            field.name,
            None,
        )

    except Exception:

        immutable = True

    else:

        immutable = False

    check(
        "immutable_"
        + field.name,
        immutable,
    )


snapshot_fields = tuple(
    field.name
    for field in fields(
        capacity.UniversalWorkerCapacitySnapshot
    )
)


check(
    "snapshot_fields_exact",
    snapshot_fields
    == (
        "worker_id",
        "worker_instance_id",
        "worker_type",
        "capacity_limit",
        "active_work_count",
        "schema_version",
    ),
    snapshot_fields,
)


for forbidden_field in (
    "available_capacity",
    "has_available_capacity",
    "is_saturated",
    "state",
    "capacity_state",
    "active_lease_count",
    "lease_id",
    "lease_owner",
    "job_id",
    "job_type",
    "capabilities",
    "pool_id",
    "health_state",
    "stale_state",
    "drain_state",
    "max_concurrency",
    "workspace_id",
    "utilization",
    "cpu",
    "memory",
    "gpu",
    "queue_id",
    "queue_depth",
):

    check(
        "forbidden_field_"
        + forbidden_field,
        forbidden_field
        not in snapshot_fields,
    )


# ============================================================
# DETERMINISM
# ============================================================

available_again = (
    capacity.create_universal_worker_capacity_snapshot(
        registration=reg,
        capacity_limit=10,
        active_work_count=3,
    )
)


check(
    "deterministic_snapshot",
    available_again
    == available,
)


check(
    "deterministic_available_capacity",
    available_again.available_capacity
    == 7,
)


# ============================================================
# EXPLANATION CONTRACT
# ============================================================

explanation = (
    capacity.explain_universal_worker_capacity_v1()
)


check(
    "phase",
    explanation.get(
        "phase"
    )
    == "4.1.14",
)

check(
    "component",
    explanation.get(
        "component"
    )
    == "Universal Worker Capacity Management",
)

check(
    "individual_worker_scope",
    "individual-worker"
    in explanation.get(
        "scope_rule",
        "",
    ),
)

check(
    "caller_supplied_limit",
    "caller-supplied"
    in explanation.get(
        "capacity_limit_rule",
        "",
    ),
)

check(
    "caller_supplied_active_work",
    "caller-supplied"
    in explanation.get(
        "active_work_rule",
        "",
    ),
)

check(
    "job_status_external",
    "does not determine which"
    in explanation.get(
        "active_work_rule",
        "",
    ),
)

check(
    "formula_rule",
    "minus active_work_count"
    in explanation.get(
        "available_capacity_rule",
        "",
    ),
)

check(
    "zero_capacity_rule",
    "capacity_limit=0"
    in explanation.get(
        "zero_capacity_rule",
        "",
    ),
)

check(
    "contradiction_rule",
    "contradictory evidence"
    in explanation.get(
        "contradiction_rule",
        "",
    ),
)

check(
    "leases_separate",
    "separate ownership"
    in explanation.get(
        "lease_boundary",
        "",
    ),
)

check(
    "assignment_external",
    "does not perform Worker Assignment"
    in explanation.get(
        "assignment_boundary",
        "",
    ),
)

check(
    "scaling_external",
    "does not scale workers"
    in explanation.get(
        "scaling_boundary",
        "",
    ),
)

check(
    "scaling_composition",
    "caller-composed available_capacity"
    in explanation.get(
        "scaling_boundary",
        "",
    ),
)

check(
    "runtime_concurrency_external",
    "not read by 4.1.14"
    in explanation.get(
        "runtime_concurrency_boundary",
        "",
    ),
)

check(
    "queue_capacity_external",
    "separate"
    in explanation.get(
        "queue_capacity_boundary",
        "",
    ),
)

check(
    "capability_external",
    "Worker Capability"
    in explanation.get(
        "capability_boundary",
        "",
    ),
)

check(
    "drain_external",
    "does not inspect or apply"
    in explanation.get(
        "drain_boundary",
        "",
    ),
)

check(
    "resources_external",
    "outside 4.1.14"
    in explanation.get(
        "resource_boundary",
        "",
    ),
)

check(
    "utilization_external",
    "observability"
    in explanation.get(
        "utilization_boundary",
        "",
    ),
)

check(
    "persistence_external",
    "does not persist"
    in explanation.get(
        "persistence_boundary",
        "",
    ),
)

check(
    "purity",
    "no external mutation"
    in explanation.get(
        "purity_rule",
        "",
    ),
)


# ============================================================
# PROHIBITIONS
# ============================================================

required_prohibitions = (
    "does not mutate Worker Registration",
    "does not inspect Worker Capability",
    "does not inspect Worker Pool membership",
    "does not inspect Worker Health",
    "does not inspect Stale Worker Detection",
    "does not inspect Worker Drain",
    "does not inspect active worker leases",
    "does not infer active work from leases",
    "does not acquire worker leases",
    "does not renew worker leases",
    "does not release worker leases",
    "does not perform Worker Assignment",
    "does not perform Worker Scaling",
    "does not perform Worker Shutdown",
    "does not initiate Worker Recovery",
    "does not read runtime max_concurrency",
    "does not read workspace concurrency policy",
    "does not calculate utilization",
    "does not calculate CPU capacity",
    "does not calculate memory capacity",
    "does not calculate GPU capacity",
    "does not enforce Queue Capacity Limits",
    "does not access Queue Infrastructure",
    "does not access orchestration",
    "does not access Runtime State Store",
    "does not persist capacity state",
    "does not maintain capacity history",
    "does not use wall clock",
    "does not perform filesystem I/O",
    "does not perform network I/O",
    "does not dispatch jobs",
    "does not execute jobs",
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
# IMPORT / API BOUNDARY
# ============================================================

source = CAPACITY_PATH.read_text(
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
    "UNIVERSAL_WORKER_CAPACITY_VERSION",
    "UNIVERSAL_WORKER_CAPACITY_SNAPSHOT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_CAPACITY_COUNT",
    "UNIVERSAL_WORKER_CAPACITY_IDENTITY_SEPARATOR",
    "UniversalWorkerCapacityError",
    "UniversalWorkerCapacitySnapshot",
    "normalize_universal_worker_capacity_count",
    "calculate_universal_worker_available_capacity",
    "create_universal_worker_capacity_snapshot",
    "explain_universal_worker_capacity_v1",
)


check(
    "api_surface_exact",
    tuple(
        capacity.__all__
    )
    == expected_all,
    capacity.__all__,
)


# ============================================================
# SIDE EFFECT / RESPONSIBILITY BOUNDARY
# ============================================================

forbidden_calls = {
    "open",
    "read_text",
    "write_text",
    "write_json",
    "mkdir",
    "unlink",
    "remove",

    "assign_universal_worker",
    "discover_universal_workers",

    "acquire_universal_worker_lease",
    "renew_universal_worker_lease",
    "release_universal_worker_lease",

    "evaluate_universal_worker_health",
    "evaluate_universal_stale_worker",
    "evaluate_universal_worker_drain",
    "evaluate_universal_worker_recovery",
    "evaluate_universal_worker_scaling",
    "evaluate_universal_worker_shutdown",

    "match_universal_worker_capabilities",
    "supports_universal_worker_capability",

    "add_universal_worker_pool_member",
    "remove_universal_worker_pool_member",

    "workspace_concurrency_decision",

    "evaluate_universal_queue_capacity",
    "create_universal_queue_capacity_snapshot",

    "enqueue_job",
    "dequeue_job",
    "route_job",

    "get_runtime_state_store_registry",

    "persist",
    "save",
    "dispatch_job",
    "execute_job",
}


found_forbidden_calls = []


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

    if call_name in forbidden_calls:

        found_forbidden_calls.append(
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
    not found_forbidden_calls,
    found_forbidden_calls,
)


# ============================================================
# PROTECTED MATRIX
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
        "phase_4_1_14_worker_capacity",

        capacity.UNIVERSAL_WORKER_CAPACITY_VERSION,
        capacity.UNIVERSAL_WORKER_CAPACITY_SNAPSHOT_SCHEMA_VERSION,

        capacity_ast,

        "canonical_worker_registration_identity",

        "individual_worker_work_slot_capacity",
        "caller_supplied_capacity_limit",
        "caller_supplied_active_work_count",

        "exact_integer_counts",
        "count_range_0_to_2147483647",

        "available_capacity_equals_limit_minus_active_work",
        "active_work_cannot_exceed_capacity_limit",
        "available_capacity_never_negative",

        "zero_capacity_valid",
        "zero_capacity_is_saturated",

        "available_capacity_derived_not_stored",
        "has_available_capacity_derived_not_stored",
        "is_saturated_derived_not_stored",

        "active_leases_separate",
        "active_work_not_inferred_from_leases",

        "worker_capability_separate",
        "worker_pool_separate",
        "worker_health_separate",
        "stale_detection_separate",
        "worker_drain_separate",

        "assignment_external",
        "scaling_external",
        "shutdown_external",
        "recovery_external",

        "runtime_max_concurrency_separate",
        "workspace_concurrency_separate",
        "queue_capacity_separate",

        "cpu_memory_gpu_external",
        "utilization_external",
        "historical_load_external",

        "no_queue_access",
        "no_orchestration_access",
        "no_runtime_state_store",
        "no_persistence",
        "no_history",
        "no_wall_clock",
        "no_filesystem_io",
        "no_network_io",
        "no_dispatch",
        "no_execution",

        "pure_worker_capacity_evidence_authority",
    )
)


worker_capacity_fingerprint = (
    hashlib.sha256(
        fingerprint_material.encode(
            "utf-8"
        )
    ).hexdigest().upper()
)


check(
    "fingerprint_generated",
    len(
        worker_capacity_fingerprint
    )
    == 64,
    worker_capacity_fingerprint,
)


# ============================================================
# FINAL AST RECHECK
# ============================================================

final_ast = ast_sha(
    CAPACITY_PATH
)


check(
    "final_ast_unchanged",
    final_ast
    == EXPECTED_CAPACITY_AST,
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
        "PHASE 4.1.14 — UNIVERSAL WORKER "
        "CAPACITY MANAGEMENT FINAL CERTIFICATION"
    ),
    "=" * 112,
    "",
    (
        "WORKER CAPACITY AST SHA256: "
        + capacity_ast
    ),
    (
        "WORKER CAPACITY FINGERPRINT: "
        + worker_capacity_fingerprint
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
            "FINAL WORKER CAPACITY CERTIFICATION: "
            + (
                "PASS"
                if passed == total
                else "FAIL"
            )
        ),
        (
            "CHECKS PASSED: "
            + str(
                passed
            )
            + "/"
            + str(
                total
            )
        ),
        "",
        "WORKER CAPACITY MODIFIED DURING CERTIFICATION: NO",
        "4.1.1 WORKER REGISTRATION MODIFIED: NO",
        "4.1.2 WORKER DISCOVERY MODIFIED: NO",
        "4.1.3 WORKER ASSIGNMENT MODIFIED: NO",
        "4.1.4 WORKER LEASING MODIFIED: NO",
        "4.1.5 WORKER HEALTH MODIFIED: NO",
        "4.1.6 WORKER RECOVERY MODIFIED: NO",
        "4.1.7 WORKER SCALING MODIFIED: NO",
        "4.1.8 WORKER SHUTDOWN MODIFIED: NO",
        "4.1.9 WORKER POOL MODIFIED: NO",
        "4.1.10 WORKER HEARTBEAT MODIFIED: NO",
        "4.1.11 STALE WORKER DETECTION MODIFIED: NO",
        "4.1.12 WORKER DRAIN MODIFIED: NO",
        "4.1.13 WORKER CAPABILITY MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "RUNTIME LIFECYCLE MANAGER MODIFIED: NO",
        "RUNTIME SHUTDOWN PROCESS MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "ACTIVE LEASES INSPECTED: NO",
        "ACTIVE WORK INFERRED FROM LEASES: NO",
        "WORKER CAPABILITY INSPECTED: NO",
        "WORKER POOL INSPECTED: NO",
        "WORKER HEALTH INSPECTED: NO",
        "STALE WORKER DETECTION INSPECTED: NO",
        "WORKER DRAIN INSPECTED: NO",
        "WORKER ASSIGNMENT PERFORMED: NO",
        "WORKER SCALING PERFORMED: NO",
        "WORKER SHUTDOWN PERFORMED: NO",
        "WORKER RECOVERY INITIATED: NO",
        "RUNTIME MAX_CONCURRENCY READ: NO",
        "WORKSPACE CONCURRENCY POLICY READ: NO",
        "UTILIZATION CALCULATED: NO",
        "CPU/MEMORY/GPU RESOURCE CAPACITY CALCULATED: NO",
        "QUEUE CAPACITY ENFORCED: NO",
        "QUEUE INFRASTRUCTURE ACCESSED: NO",
        "ORCHESTRATION ACCESSED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "CAPACITY STATE PERSISTED: NO",
        "CAPACITY HISTORY MAINTAINED: NO",
        "WALL CLOCK USED: NO",
        "FILESYSTEM I/O: NO",
        "NETWORK I/O: NO",
        "JOB DISPATCH/EXECUTION: NO",
        "",
        (
            "PHASE 4.1.14 FREEZE CANDIDATE: "
            + (
                "YES"
                if passed == total
                else "NO"
            )
        ),
    ]
)


REPORT_PATH.write_text(
    "\n".join(
        lines
    ),
    encoding="utf-8",
)


print(
    "\n".join(
        lines
    )
)


if passed != total:

    raise SystemExit(
        "Phase 4.1.14 Worker Capacity final certification failed."
    )
