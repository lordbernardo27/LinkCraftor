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
    / "phase_4_1_9_worker_pool_regression.txt"
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
        "Worker Pool authority is missing."
    )


initial_ast = ast_sha(
    POOL_PATH
)

if initial_ast != EXPECTED_POOL_AST:
    raise SystemExit(
        (
            "Worker Pool AST changed before regression.\n"
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
                "Protected authority changed before regression: "
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
# 1 — AST / VERSION / SCHEMAS / CONSTANTS
# ============================================================

check(
    "pool_ast_stable",
    ast_sha(POOL_PATH)
    == EXPECTED_POOL_AST,
    ast_sha(POOL_PATH),
)

check(
    "version_exact",
    pool.UNIVERSAL_WORKER_POOL_VERSION
    == "universal_worker_pool_v4.1.9",
)

check(
    "member_schema_exact",
    pool.UNIVERSAL_WORKER_POOL_MEMBER_SCHEMA_VERSION
    == "universal_worker_pool_member_schema_v1",
)

check(
    "snapshot_schema_exact",
    pool.UNIVERSAL_WORKER_POOL_SNAPSHOT_SCHEMA_VERSION
    == "universal_worker_pool_snapshot_schema_v1",
)

check(
    "max_pool_id_length_exact",
    pool.MAX_UNIVERSAL_WORKER_POOL_ID_LENGTH
    == 200,
)

check(
    "identity_separator_exact",
    pool.UNIVERSAL_WORKER_POOL_IDENTITY_SEPARATOR
    == "::",
)


# ============================================================
# 2 — POOL ID NORMALIZATION ATTACKS
# ============================================================

for raw, expected in (
    ("pool-a", "pool-a"),
    (" pool-a ", "pool-a"),
    ("\tpool-a\n", "pool-a"),
    ("POOL-A", "POOL-A"),
    ("a", "a"),
):

    result = (
        pool.normalize_universal_worker_pool_id(
            raw
        )
    )

    check(
        "pool_id_normalization_"
        + repr(raw),
        result == expected,
        result,
    )


for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        1,
        -1,
        0.0,
        1.0,
        [],
        {},
        (),
        set(),
        object(),
    ),
    start=1,
):

    try:
        pool.normalize_universal_worker_pool_id(
            bad
        )

    except pool.UniversalWorkerPoolError as exc:
        rejected = (
            exc.code
            == "invalid_worker_pool_id_type"
        )

    else:
        rejected = False

    check(
        "pool_id_bad_type_"
        + str(index),
        rejected,
        type(bad).__name__,
    )


for index, bad in enumerate(
    (
        "",
        " ",
        "\t",
        "\n",
        "\r\n",
        "   \t   ",
    ),
    start=1,
):

    try:
        pool.normalize_universal_worker_pool_id(
            bad
        )

    except pool.UniversalWorkerPoolError as exc:
        rejected = (
            exc.code
            == "empty_worker_pool_id"
        )

    else:
        rejected = False

    check(
        "pool_id_blank_"
        + str(index),
        rejected,
        repr(bad),
    )


exact_max = (
    "p"
    * pool.MAX_UNIVERSAL_WORKER_POOL_ID_LENGTH
)

check(
    "pool_id_exact_max",
    pool.normalize_universal_worker_pool_id(
        exact_max
    )
    == exact_max,
)


for overflow in (
    exact_max + "x",
    " " + exact_max + "x ",
):

    try:
        pool.normalize_universal_worker_pool_id(
            overflow
        )

    except pool.UniversalWorkerPoolError as exc:
        rejected = (
            exc.code
            == "worker_pool_id_too_long"
        )

    else:
        rejected = False

    check(
        "pool_id_overflow_"
        + str(len(overflow)),
        rejected,
    )


for bad in (
    "a::b",
    "::",
    "pool::",
    "::pool",
    " pool::one ",
):

    try:
        pool.normalize_universal_worker_pool_id(
            bad
        )

    except pool.UniversalWorkerPoolError as exc:
        rejected = (
            exc.code
            == "reserved_worker_pool_id_separator"
        )

    else:
        rejected = False

    check(
        "reserved_separator_"
        + repr(bad),
        rejected,
    )


# ============================================================
# 3 — MEMBER CREATION / IDENTITY
# ============================================================

r_a1 = make_registration(
    "worker-a",
    "instance-1",
)

r_a2 = make_registration(
    "worker-a",
    "instance-2",
)

r_b1 = make_registration(
    "worker-b",
    "instance-1",
)

r_c1_other = make_registration(
    "worker-c",
    "instance-1",
    "other_worker",
)


m_a1 = (
    pool.create_universal_worker_pool_member(
        r_a1
    )
)

m_a2 = (
    pool.create_universal_worker_pool_member(
        r_a2
    )
)


check(
    "member_identity_a1",
    m_a1.worker_identity
    == "worker-a::instance-1",
)

check(
    "member_identity_a2",
    m_a2.worker_identity
    == "worker-a::instance-2",
)

check(
    "same_worker_different_instances_distinct",
    m_a1.worker_identity
    != m_a2.worker_identity,
)


for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        "",
        {},
        [],
        (),
    ),
    start=1,
):

    try:
        pool.create_universal_worker_pool_member(
            bad
        )

    except pool.UniversalWorkerPoolError as exc:
        rejected = (
            exc.code
            == "invalid_worker_pool_registration"
        )

    else:
        rejected = False

    check(
        "invalid_registration_"
        + str(index),
        rejected,
        repr(bad),
    )


# ============================================================
# 4 — EMPTY POOL / SNAPSHOT NORMALIZATION
# ============================================================

empty = (
    pool.create_universal_worker_pool_snapshot(
        pool_id=" semantic-pool ",
        worker_type=" semantic_worker ",
    )
)

check(
    "empty_snapshot_pool_id_normalized",
    empty.pool_id
    == "semantic-pool",
)

check(
    "empty_snapshot_worker_type_normalized",
    empty.worker_type
    == "semantic_worker",
)

check(
    "empty_snapshot_member_count",
    empty.member_count
    == 0,
)

check(
    "empty_snapshot_identities",
    empty.worker_identities
    == (),
)


# ============================================================
# 5 — DETERMINISTIC ORDERING PERMUTATION MATRIX
# ============================================================

registrations = (
    r_b1,
    r_a2,
    r_a1,
)

expected_identities = (
    "worker-a::instance-1",
    "worker-a::instance-2",
    "worker-b::instance-1",
)


for index, permutation in enumerate(
    itertools.permutations(
        registrations
    ),
    start=1,
):

    snapshot = (
        pool.create_universal_worker_pool_from_registrations(
            pool_id="semantic-pool",
            worker_type="semantic_worker",
            registrations=permutation,
        )
    )

    check(
        "ordering_permutation_"
        + str(index),
        snapshot.worker_identities
        == expected_identities,
        snapshot.worker_identities,
    )


# ============================================================
# 6 — MEMBERS ITERABLE ATTACKS
# ============================================================

for index, bad in enumerate(
    (
        None,
        1,
        True,
        False,
        1.0,
        object(),
    ),
    start=1,
):

    try:
        pool.create_universal_worker_pool_snapshot(
            pool_id="p",
            worker_type="semantic_worker",
            members=bad,
        )

    except (
        pool.UniversalWorkerPoolError,
        TypeError,
    ) as exc:
        rejected = True
        detail = (
            getattr(
                exc,
                "code",
                type(exc).__name__,
            )
        )

    else:
        rejected = False
        detail = "accepted"

    check(
        "invalid_members_iterable_"
        + str(index),
        rejected,
        detail,
    )


for index, bad_member in enumerate(
    (
        None,
        True,
        False,
        0,
        "",
        {},
        [],
        (),
    ),
    start=1,
):

    try:
        pool.create_universal_worker_pool_snapshot(
            pool_id="p",
            worker_type="semantic_worker",
            members=(
                bad_member,
            ),
        )

    except pool.UniversalWorkerPoolError as exc:
        rejected = (
            exc.code
            == "invalid_worker_pool_member"
        )

    else:
        rejected = False

    check(
        "invalid_member_element_"
        + str(index),
        rejected,
        repr(bad_member),
    )


# ============================================================
# 7 — REGISTRATIONS ITERABLE ATTACKS
# ============================================================

for index, bad in enumerate(
    (
        None,
        1,
        True,
        False,
        1.0,
        object(),
    ),
    start=1,
):

    try:
        pool.create_universal_worker_pool_from_registrations(
            pool_id="p",
            worker_type="semantic_worker",
            registrations=bad,
        )

    except pool.UniversalWorkerPoolError as exc:
        rejected = (
            exc.code
            == "invalid_worker_pool_registrations"
        )

    else:
        rejected = False

    check(
        "invalid_registrations_iterable_"
        + str(index),
        rejected,
        type(bad).__name__,
    )


for index, bad_registration in enumerate(
    (
        None,
        True,
        False,
        0,
        "",
        {},
        [],
        (),
    ),
    start=1,
):

    try:
        pool.create_universal_worker_pool_from_registrations(
            pool_id="p",
            worker_type="semantic_worker",
            registrations=(
                bad_registration,
            ),
        )

    except pool.UniversalWorkerPoolError as exc:
        rejected = (
            exc.code
            == "invalid_worker_pool_registration"
        )

    else:
        rejected = False

    check(
        "invalid_registration_element_"
        + str(index),
        rejected,
        repr(bad_registration),
    )


# ============================================================
# 8 — TYPE CONSTRAINT MATRIX
# ============================================================

semantic_pool = (
    pool.create_universal_worker_pool_from_registrations(
        pool_id="semantic",
        worker_type="semantic_worker",
        registrations=(
            r_a1,
            r_a2,
        ),
    )
)


check(
    "semantic_membership_a1",
    pool.is_universal_worker_pool_member(
        semantic_pool,
        r_a1,
    )
    is True,
)

check(
    "semantic_membership_a2",
    pool.is_universal_worker_pool_member(
        semantic_pool,
        r_a2,
    )
    is True,
)

check(
    "different_type_not_member",
    pool.is_universal_worker_pool_member(
        semantic_pool,
        r_c1_other,
    )
    is False,
)


try:
    pool.create_universal_worker_pool_from_registrations(
        pool_id="mixed",
        worker_type="semantic_worker",
        registrations=(
            r_a1,
            r_c1_other,
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
    "mixed_registration_types_rejected",
    rejected,
)


other_member = (
    pool.create_universal_worker_pool_member(
        r_c1_other
    )
)


try:
    pool.create_universal_worker_pool_snapshot(
        pool_id="mixed",
        worker_type="semantic_worker",
        members=(
            m_a1,
            other_member,
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
    "mixed_member_types_rejected",
    rejected,
)


# ============================================================
# 9 — DUPLICATE IDENTITY ATTACKS
# ============================================================

try:
    pool.create_universal_worker_pool_snapshot(
        pool_id="dup",
        worker_type="semantic_worker",
        members=(
            m_a1,
            m_a1,
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
    "duplicate_member_object_rejected",
    rejected,
)


duplicate_member_equivalent = (
    pool.UniversalWorkerPoolMember(
        worker_id=m_a1.worker_id,
        worker_instance_id=m_a1.worker_instance_id,
        worker_type=m_a1.worker_type,
    )
)


try:
    pool.create_universal_worker_pool_snapshot(
        pool_id="dup",
        worker_type="semantic_worker",
        members=(
            m_a1,
            duplicate_member_equivalent,
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
    "duplicate_equivalent_identity_rejected",
    rejected,
)


# ============================================================
# 10 — ADD TRANSFORMATION
# ============================================================

base = (
    pool.create_universal_worker_pool_from_registrations(
        pool_id="semantic",
        worker_type="semantic_worker",
        registrations=(
            r_a2,
        ),
    )
)

added = (
    pool.add_universal_worker_pool_member(
        base,
        r_a1,
    )
)


check(
    "add_returns_new_object",
    added is not base,
)

check(
    "add_preserves_pool_id",
    added.pool_id
    == base.pool_id,
)

check(
    "add_preserves_worker_type",
    added.worker_type
    == base.worker_type,
)

check(
    "add_does_not_mutate_source",
    base.worker_identities
    == (
        "worker-a::instance-2",
    ),
)

check(
    "add_reorders_deterministically",
    added.worker_identities
    == (
        "worker-a::instance-1",
        "worker-a::instance-2",
    ),
)


try:
    pool.add_universal_worker_pool_member(
        added,
        r_a1,
    )

except pool.UniversalWorkerPoolError as exc:
    rejected = (
        exc.code
        == "duplicate_worker_pool_member"
    )

else:
    rejected = False


check(
    "duplicate_add_rejected",
    rejected,
)


try:
    pool.add_universal_worker_pool_member(
        added,
        r_c1_other,
    )

except pool.UniversalWorkerPoolError as exc:
    rejected = (
        exc.code
        == "worker_pool_type_mismatch"
    )

else:
    rejected = False


check(
    "wrong_type_add_rejected",
    rejected,
)


# ============================================================
# 11 — REMOVE TRANSFORMATION
# ============================================================

removed = (
    pool.remove_universal_worker_pool_member(
        added,
        r_a1,
    )
)


check(
    "remove_returns_new_object",
    removed is not added,
)

check(
    "remove_preserves_pool_id",
    removed.pool_id
    == added.pool_id,
)

check(
    "remove_preserves_worker_type",
    removed.worker_type
    == added.worker_type,
)

check(
    "remove_does_not_mutate_source",
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


try:
    pool.remove_universal_worker_pool_member(
        removed,
        r_a1,
    )

except pool.UniversalWorkerPoolError as exc:
    rejected = (
        exc.code
        == "worker_pool_member_not_found"
    )

else:
    rejected = False


check(
    "double_remove_rejected",
    rejected,
)


# ============================================================
# 12 — REMOVE WRONG-TYPE / IDENTITY EDGE
# ============================================================

try:
    pool.remove_universal_worker_pool_member(
        semantic_pool,
        r_c1_other,
    )

except pool.UniversalWorkerPoolError as exc:
    rejected = (
        exc.code
        == "worker_pool_member_not_found"
    )

else:
    rejected = False


check(
    "wrong_type_nonmember_remove_rejected",
    rejected,
)


# ============================================================
# 13 — INVALID POOL OBJECT ATTACKS
# ============================================================

for index, bad_pool in enumerate(
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
        pool.is_universal_worker_pool_member(
            bad_pool,
            r_a1,
        )

    except pool.UniversalWorkerPoolError as exc:
        rejected = (
            exc.code
            == "invalid_worker_pool_snapshot"
        )

    else:
        rejected = False

    check(
        "invalid_pool_membership_check_"
        + str(index),
        rejected,
    )


for index, bad_pool in enumerate(
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
        pool.add_universal_worker_pool_member(
            bad_pool,
            r_a1,
        )

    except pool.UniversalWorkerPoolError as exc:
        rejected = (
            exc.code
            == "invalid_worker_pool_snapshot"
        )

    else:
        rejected = False

    check(
        "invalid_pool_add_"
        + str(index),
        rejected,
    )


for index, bad_pool in enumerate(
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
        pool.remove_universal_worker_pool_member(
            bad_pool,
            r_a1,
        )

    except pool.UniversalWorkerPoolError as exc:
        rejected = (
            exc.code
            == "invalid_worker_pool_snapshot"
        )

    else:
        rejected = False

    check(
        "invalid_pool_remove_"
        + str(index),
        rejected,
    )


# ============================================================
# 14 — MEMBERSHIP IS NOT INFERRED BY TYPE
# ============================================================

same_type_outsider = make_registration(
    "worker-outsider",
    "instance-1",
    "semantic_worker",
)


check(
    "same_type_does_not_imply_membership",
    pool.is_universal_worker_pool_member(
        semantic_pool,
        same_type_outsider,
    )
    is False,
)


# ============================================================
# 15 — NO GLOBAL EXCLUSIVITY CLAIM
# ============================================================

pool_one = (
    pool.create_universal_worker_pool_from_registrations(
        pool_id="pool-one",
        worker_type="semantic_worker",
        registrations=(
            r_a1,
        ),
    )
)

pool_two = (
    pool.create_universal_worker_pool_from_registrations(
        pool_id="pool-two",
        worker_type="semantic_worker",
        registrations=(
            r_a1,
        ),
    )
)


check(
    "same_worker_can_exist_in_independent_snapshots",
    (
        pool.is_universal_worker_pool_member(
            pool_one,
            r_a1,
        )
        and
        pool.is_universal_worker_pool_member(
            pool_two,
            r_a1,
        )
    ),
)


# ============================================================
# 16 — SCHEMA TAMPERING
# ============================================================

try:
    pool.UniversalWorkerPoolMember(
        worker_id="worker-a",
        worker_instance_id="instance-1",
        worker_type="semantic_worker",
        schema_version="tampered",
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
        pool_id="semantic",
        worker_type="semantic_worker",
        members=(),
        schema_version="tampered",
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
# 17 — IMMUTABILITY
# ============================================================

for obj, field_name in (
    (m_a1, "worker_id"),
    (m_a1, "worker_instance_id"),
    (m_a1, "worker_type"),
    (m_a1, "schema_version"),
    (semantic_pool, "pool_id"),
    (semantic_pool, "worker_type"),
    (semantic_pool, "members"),
    (semantic_pool, "schema_version"),
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
# 18 — SNAPSHOT EQUALITY / DETERMINISM
# ============================================================

snapshot_a = (
    pool.create_universal_worker_pool_from_registrations(
        pool_id="deterministic",
        worker_type="semantic_worker",
        registrations=(
            r_a1,
            r_a2,
            r_b1,
        ),
    )
)

snapshot_b = (
    pool.create_universal_worker_pool_from_registrations(
        pool_id="deterministic",
        worker_type="semantic_worker",
        registrations=(
            r_b1,
            r_a1,
            r_a2,
        ),
    )
)


check(
    "deterministic_snapshot_equality",
    snapshot_a == snapshot_b,
)

check(
    "deterministic_identity_tuple",
    snapshot_a.worker_identities
    == snapshot_b.worker_identities,
)


# ============================================================
# 19 — EXPLANATION CONTRACT
# ============================================================

explanation = (
    pool.explain_universal_worker_pool_v1()
)


check(
    "explanation_phase",
    explanation.get(
        "phase"
    )
    == "4.1.9",
)

check(
    "explanation_component",
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
    "member_schema_explained",
    explanation.get(
        "member_schema_version"
    )
    == pool.UNIVERSAL_WORKER_POOL_MEMBER_SCHEMA_VERSION,
)

check(
    "snapshot_schema_explained",
    explanation.get(
        "snapshot_schema_version"
    )
    == pool.UNIVERSAL_WORKER_POOL_SNAPSHOT_SCHEMA_VERSION,
)

check(
    "identity_rule_caller_supplied",
    "caller-supplied"
    in explanation.get(
        "identity_rule",
        "",
    ),
)

check(
    "membership_explicit",
    "explicit"
    in explanation.get(
        "membership_rule",
        "",
    ),
)

check(
    "membership_not_inferred",
    "never inferred"
    in explanation.get(
        "membership_rule",
        "",
    ),
)

check(
    "one_worker_type_rule",
    "one worker_type"
    in explanation.get(
        "worker_type_rule",
        "",
    ),
)

check(
    "immutable_snapshot_rule",
    "new immutable"
    in explanation.get(
        "snapshot_rule",
        "",
    ),
)

check(
    "no_global_exclusivity",
    "does not claim global"
    in explanation.get(
        "global_exclusivity_rule",
        "",
    ),
)

check(
    "no_implicit_default_pool",
    "no implicit default pool"
    in explanation.get(
        "default_pool_rule",
        "",
    ),
)

check(
    "taxonomy_not_invented",
    "not invented"
    in explanation.get(
        "taxonomy_rule",
        "",
    ),
)

check(
    "workspace_product_external",
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
# 20 — PROHIBITION MATRIX
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
# 21 — STATIC IMPORT BOUNDARY
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


# ============================================================
# 22 — API SURFACE
# ============================================================

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
# 23 — FORBIDDEN SIDE-EFFECT CALLS
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
    "evaluate_universal_worker_lease_state",

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
# 24 — RESPONSIBILITY-BLEED FUNCTION NAMES
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
    "default_pool",
    "shared_pool",
    "dedicated_pool",
    "workspace_pool",
    "product_pool",
    "discover_worker",
    "assign_worker",
    "lease_worker",
    "worker_health",
    "heartbeat",
    "stale_worker",
    "recover_worker",
    "scale_worker",
    "shutdown_worker",
    "drain_worker",
    "worker_capability",
    "worker_capacity",
    "provision",
    "terminate",
    "queue_mutation",
    "state_store",
    "orchestration",
    "persist",
    "filesystem",
    "network",
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
# 25 — NO MUTATION OF REGISTRATION OBJECTS
# ============================================================

suspicious_assignments = []


for node in ast.walk(
    tree
):

    targets = []

    if isinstance(
        node,
        ast.Assign,
    ):
        targets.extend(
            node.targets
        )

    elif isinstance(
        node,
        ast.AnnAssign,
    ):
        targets.append(
            node.target
        )

    elif isinstance(
        node,
        ast.AugAssign,
    ):
        targets.append(
            node.target
        )

    else:
        continue

    for target in targets:

        if isinstance(
            target,
            ast.Attribute,
        ):

            attr = (
                target.attr.lower()
            )

            if attr in {
                "worker_id",
                "worker_instance_id",
                "worker_type",
                "runtime_version",
                "host_id",
                "registered_at",
                "pool_id",
                "members",
                "membership",
            }:

                suspicious_assignments.append(
                    (
                        attr,
                        getattr(
                            node,
                            "lineno",
                            0,
                        ),
                    )
                )


# object.__setattr__ is used only inside frozen dataclass
# normalization, so direct attribute-assignment nodes are what
# this check is intended to detect.
check(
    "no_direct_runtime_membership_state_assignment",
    not suspicious_assignments,
    suspicious_assignments,
)


# ============================================================
# 26 — NO IMPLICIT POLICY VOCABULARY
# ============================================================

source_lower = source.lower()


for token in (
    "default_pool_id",
    "shared_pool_id",
    "dedicated_pool_id",
    "system_pool_id",
    "workspace_pool_id",
    "product_pool_id",
    "primary_pool",
    "exclusive_pool",
):

    check(
        "no_implicit_policy_"
        + token,
        token not in source_lower,
    )


# ============================================================
# 27 — PROTECTED AST MATRIX
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
        actual == expected,
        actual,
    )


# ============================================================
# 28 — FINAL POOL AST RECHECK
# ============================================================

final_pool_ast = ast_sha(
    POOL_PATH
)


check(
    "pool_ast_final",
    final_pool_ast
    == EXPECTED_POOL_AST,
    final_pool_ast,
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
        "INFRASTRUCTURE ADVERSARIAL REGRESSION"
    ),
    "=" * 112,
    "",
    (
        "WORKER POOL AST SHA256: "
        + final_pool_ast
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
            "ADVERSARIAL WORKER POOL REGRESSION: "
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
        "WORKER POOL AST MODIFIED: NO",
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
        "Phase 4.1.9 Worker Pool adversarial regression failed."
    )
