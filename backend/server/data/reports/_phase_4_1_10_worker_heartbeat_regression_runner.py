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

HEARTBEAT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "heartbeat.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_10_worker_heartbeat_regression.txt"
)


EXPECTED_HEARTBEAT_AST = (
    "A58BDEE660CA903453DA6D968A2B02FBFBE3920E9BBE6C64BC75A597DB7C11EE"
)

EXPECTED_ORCHESTRATION_MODELS_AST = (
    "5C9FE5E4F84FA1C369CB45F74B0CB12B7E730ADA3C7CBC95B4F50EC75DC5E92D"
)

EXPECTED_TMS_ORCHESTRATION_GOVERNANCE_AST = (
    "2AAA15B7283C6F0B4BB67A47FE58F1FD0EF2815A09CA048EA0CFE7DEF232B4E1"
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

    "orchestration_models": (
        ROOT / "backend/server/orchestration/models.py",
        EXPECTED_ORCHESTRATION_MODELS_AST,
    ),

    "tms_orchestration_governance": (
        ROOT / "backend/server/tms/orchestration_governance.py",
        EXPECTED_TMS_ORCHESTRATION_GOVERNANCE_AST,
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
# PRECONDITIONS
# ============================================================

if not HEARTBEAT_PATH.exists():

    raise SystemExit(
        "Worker Heartbeat authority missing."
    )


initial_ast = ast_sha(
    HEARTBEAT_PATH
)


if initial_ast != EXPECTED_HEARTBEAT_AST:

    raise SystemExit(
        (
            "Worker Heartbeat AST changed before regression.\n"
            "EXPECTED: "
            + EXPECTED_HEARTBEAT_AST
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
                "Protected authority changed before "
                "Worker Heartbeat regression: "
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
    "universal_worker.heartbeat"
)

sys.modules.pop(
    module_name,
    None,
)

heartbeat = importlib.import_module(
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
    worker_id="worker-a",
    instance_id="instance-1",
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
# 1 — AST / CONSTANT CONTRACT
# ============================================================

check(
    "heartbeat_ast_stable",
    ast_sha(
        HEARTBEAT_PATH
    )
    == EXPECTED_HEARTBEAT_AST,
    ast_sha(
        HEARTBEAT_PATH
    ),
)

check(
    "version_exact",
    heartbeat.UNIVERSAL_WORKER_HEARTBEAT_VERSION
    == "universal_worker_heartbeat_v4.1.10",
)

check(
    "schema_exact",
    heartbeat.UNIVERSAL_WORKER_HEARTBEAT_SCHEMA_VERSION
    == "universal_worker_heartbeat_schema_v1",
)

check(
    "sequence_max_exact",
    heartbeat.MAX_UNIVERSAL_WORKER_HEARTBEAT_SEQUENCE
    == 2_147_483_647,
)

check(
    "identity_separator_exact",
    heartbeat.UNIVERSAL_WORKER_HEARTBEAT_IDENTITY_SEPARATOR
    == "::",
)


# ============================================================
# 2 — TIMESTAMP NORMALIZATION MATRIX
# ============================================================

valid_timestamps = (
    (
        "2026-08-17T00:00:00Z",
        "2026-08-17T00:00:00+00:00",
    ),
    (
        "2026-08-17T00:00:00+00:00",
        "2026-08-17T00:00:00+00:00",
    ),
    (
        " 2026-08-17T00:00:00Z ",
        "2026-08-17T00:00:00+00:00",
    ),
    (
        "2026-08-17T00:00:00.123456Z",
        "2026-08-17T00:00:00.123456+00:00",
    ),
)


for index, (
    raw,
    expected,
) in enumerate(
    valid_timestamps,
    start=1,
):

    actual = (
        heartbeat.normalize_universal_worker_heartbeat_timestamp(
            raw
        )
    )

    check(
        "valid_timestamp_"
        + str(index),
        actual
        == expected,
        actual,
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

        heartbeat.normalize_universal_worker_heartbeat_timestamp(
            bad
        )

    except heartbeat.UniversalWorkerHeartbeatError as exc:

        rejected = (
            exc.code
            == "invalid_worker_heartbeat_timestamp_type"
        )

    else:

        rejected = False

    check(
        "timestamp_type_attack_"
        + str(index),
        rejected,
        type(
            bad
        ).__name__,
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

        heartbeat.normalize_universal_worker_heartbeat_timestamp(
            bad
        )

    except heartbeat.UniversalWorkerHeartbeatError as exc:

        rejected = (
            exc.code
            == "empty_worker_heartbeat_timestamp"
        )

    else:

        rejected = False

    check(
        "blank_timestamp_"
        + str(index),
        rejected,
        repr(
            bad
        ),
    )


for index, bad in enumerate(
    (
        "invalid",
        "yesterday",
        "2026-13-01T00:00:00Z",
        "2026-08-32T00:00:00Z",
        "2026-08-17T25:00:00Z",
    ),
    start=1,
):

    try:

        heartbeat.normalize_universal_worker_heartbeat_timestamp(
            bad
        )

    except heartbeat.UniversalWorkerHeartbeatError as exc:

        rejected = (
            exc.code
            == "invalid_worker_heartbeat_timestamp"
        )

    else:

        rejected = False

    check(
        "malformed_timestamp_"
        + str(index),
        rejected,
        bad,
    )


for index, bad in enumerate(
    (
        "2026-08-17T00:00:00",
        "2026-08-17 00:00:00",
    ),
    start=1,
):

    try:

        heartbeat.normalize_universal_worker_heartbeat_timestamp(
            bad
        )

    except heartbeat.UniversalWorkerHeartbeatError as exc:

        rejected = (
            exc.code
            == "naive_worker_heartbeat_timestamp"
        )

    else:

        rejected = False

    check(
        "naive_timestamp_"
        + str(index),
        rejected,
    )


for index, bad in enumerate(
    (
        "2026-08-17T01:00:00+01:00",
        "2026-08-16T19:00:00-05:00",
        "2026-08-17T05:30:00+05:30",
    ),
    start=1,
):

    try:

        heartbeat.normalize_universal_worker_heartbeat_timestamp(
            bad
        )

    except heartbeat.UniversalWorkerHeartbeatError as exc:

        rejected = (
            exc.code
            == "non_utc_worker_heartbeat_timestamp"
        )

    else:

        rejected = False

    check(
        "non_utc_timestamp_"
        + str(index),
        rejected,
        bad,
    )


# ============================================================
# 3 — SEQUENCE ATTACK MATRIX
# ============================================================

for value in (
    1,
    2,
    999,
    heartbeat.MAX_UNIVERSAL_WORKER_HEARTBEAT_SEQUENCE,
):

    check(
        "valid_sequence_"
        + str(
            value
        ),
        heartbeat.normalize_universal_worker_heartbeat_sequence(
            value
        )
        == value,
    )


for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        -1,
        -2,
        1.0,
        2.5,
        "",
        "1",
        [],
        {},
        (),
        set(),
    ),
    start=1,
):

    try:

        heartbeat.normalize_universal_worker_heartbeat_sequence(
            bad
        )

    except heartbeat.UniversalWorkerHeartbeatError as exc:

        rejected = (
            exc.code
            == "invalid_worker_heartbeat_sequence"
        )

    else:

        rejected = False

    check(
        "invalid_sequence_"
        + str(index),
        rejected,
        repr(
            bad
        ),
    )


for overflow in (
    heartbeat.MAX_UNIVERSAL_WORKER_HEARTBEAT_SEQUENCE
    + 1,
    heartbeat.MAX_UNIVERSAL_WORKER_HEARTBEAT_SEQUENCE
    + 100,
):

    try:

        heartbeat.normalize_universal_worker_heartbeat_sequence(
            overflow
        )

    except heartbeat.UniversalWorkerHeartbeatError as exc:

        rejected = (
            exc.code
            == "worker_heartbeat_sequence_too_large"
        )

    else:

        rejected = False

    check(
        "sequence_overflow_"
        + str(
            overflow
        ),
        rejected,
    )


# ============================================================
# 4 — REGISTRATION IDENTITY
# ============================================================

reg_a1 = make_registration(
    "worker-a",
    "instance-1",
)

reg_a2 = make_registration(
    "worker-a",
    "instance-2",
)

reg_b1 = make_registration(
    "worker-b",
    "instance-1",
)

reg_type_b = make_registration(
    "worker-a",
    "instance-1",
    "other_worker",
)


hb_a1_1 = (
    heartbeat.create_universal_worker_heartbeat(
        registration=reg_a1,
        heartbeat_at="2026-08-17T00:00:01Z",
        sequence=1,
    )
)


check(
    "canonical_worker_identity",
    hb_a1_1.worker_identity
    == "worker-a::instance-1",
)

check(
    "worker_id_from_registration",
    hb_a1_1.worker_id
    == reg_a1.worker_id,
)

check(
    "instance_from_registration",
    hb_a1_1.worker_instance_id
    == reg_a1.worker_instance_id,
)

check(
    "worker_type_from_registration",
    hb_a1_1.worker_type
    == reg_a1.worker_type,
)


# ============================================================
# 5 — INVALID REGISTRATION MATRIX
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
        object(),
    ),
    start=1,
):

    try:

        heartbeat.create_universal_worker_heartbeat(
            registration=bad,
            heartbeat_at="2026-08-17T00:00:01Z",
            sequence=1,
        )

    except heartbeat.UniversalWorkerHeartbeatError as exc:

        rejected = (
            exc.code
            == "invalid_worker_heartbeat_registration"
        )

    else:

        rejected = False

    check(
        "registration_attack_"
        + str(index),
        rejected,
    )


# ============================================================
# 6 — NORMAL PROGRESSION MATRIX
# ============================================================

hb_a1_2 = (
    heartbeat.create_universal_worker_heartbeat(
        registration=reg_a1,
        heartbeat_at="2026-08-17T00:00:02Z",
        sequence=2,
        previous_heartbeat=hb_a1_1,
    )
)

check(
    "progression_1_to_2",
    hb_a1_2.sequence
    == 2,
)


hb_a1_100 = (
    heartbeat.create_universal_worker_heartbeat(
        registration=reg_a1,
        heartbeat_at="2026-08-17T00:01:40Z",
        sequence=100,
        previous_heartbeat=hb_a1_2,
    )
)

check(
    "non_contiguous_sequence_allowed",
    hb_a1_100.sequence
    == 100,
)


# ============================================================
# 7 — DUPLICATE SEQUENCE PRECEDENCE
# ============================================================

candidate_duplicate_later_time = (
    heartbeat.UniversalWorkerHeartbeat(
        worker_id=reg_a1.worker_id,
        worker_instance_id=reg_a1.worker_instance_id,
        worker_type=reg_a1.worker_type,
        heartbeat_at="2026-08-17T00:00:03Z",
        sequence=1,
    )
)


try:

    heartbeat.validate_universal_worker_heartbeat_progression(
        previous=hb_a1_1,
        current=candidate_duplicate_later_time,
    )

except heartbeat.UniversalWorkerHeartbeatError as exc:

    rejected = (
        exc.code
        == "duplicate_worker_heartbeat_sequence"
    )

else:

    rejected = False


check(
    "duplicate_sequence_precedes_timestamp",
    rejected,
)


# ============================================================
# 8 — OUT-OF-ORDER SEQUENCE PRECEDENCE
# ============================================================

hb_sequence_10 = (
    heartbeat.create_universal_worker_heartbeat(
        registration=reg_a1,
        heartbeat_at="2026-08-17T00:00:10Z",
        sequence=10,
    )
)

candidate_sequence_9 = (
    heartbeat.UniversalWorkerHeartbeat(
        worker_id=reg_a1.worker_id,
        worker_instance_id=reg_a1.worker_instance_id,
        worker_type=reg_a1.worker_type,
        heartbeat_at="2026-08-17T00:00:11Z",
        sequence=9,
    )
)


try:

    heartbeat.validate_universal_worker_heartbeat_progression(
        previous=hb_sequence_10,
        current=candidate_sequence_9,
    )

except heartbeat.UniversalWorkerHeartbeatError as exc:

    rejected = (
        exc.code
        == "out_of_order_worker_heartbeat_sequence"
    )

else:

    rejected = False


check(
    "out_of_order_sequence_rejected",
    rejected,
)


# ============================================================
# 9 — TIMESTAMP ORDERING ATTACKS
# ============================================================

for index, current_time in enumerate(
    (
        "2026-08-17T00:00:01Z",
        "2026-08-17T00:00:00.999999Z",
        "2026-08-16T23:59:59Z",
    ),
    start=1,
):

    candidate = (
        heartbeat.UniversalWorkerHeartbeat(
            worker_id=reg_a1.worker_id,
            worker_instance_id=reg_a1.worker_instance_id,
            worker_type=reg_a1.worker_type,
            heartbeat_at=current_time,
            sequence=2,
        )
    )

    try:

        heartbeat.validate_universal_worker_heartbeat_progression(
            previous=hb_a1_1,
            current=candidate,
        )

    except heartbeat.UniversalWorkerHeartbeatError as exc:

        rejected = (
            exc.code
            == "non_increasing_worker_heartbeat_timestamp"
        )

    else:

        rejected = False

    check(
        "timestamp_progression_attack_"
        + str(index),
        rejected,
        current_time,
    )


microsecond_valid = (
    heartbeat.create_universal_worker_heartbeat(
        registration=reg_a1,
        heartbeat_at="2026-08-17T00:00:01.000001Z",
        sequence=2,
        previous_heartbeat=hb_a1_1,
    )
)

check(
    "microsecond_progression_allowed",
    microsecond_valid.sequence
    == 2,
)


# ============================================================
# 10 — WORKER IDENTITY MISMATCH
# ============================================================

hb_a2 = (
    heartbeat.create_universal_worker_heartbeat(
        registration=reg_a2,
        heartbeat_at="2026-08-17T00:00:02Z",
        sequence=2,
    )
)

hb_b1 = (
    heartbeat.create_universal_worker_heartbeat(
        registration=reg_b1,
        heartbeat_at="2026-08-17T00:00:02Z",
        sequence=2,
    )
)


for name, candidate in (
    (
        "same_worker_different_instance",
        hb_a2,
    ),
    (
        "different_worker_same_instance",
        hb_b1,
    ),
):

    try:

        heartbeat.validate_universal_worker_heartbeat_progression(
            previous=hb_a1_1,
            current=candidate,
        )

    except heartbeat.UniversalWorkerHeartbeatError as exc:

        rejected = (
            exc.code
            == "worker_heartbeat_identity_mismatch"
        )

    else:

        rejected = False

    check(
        name
        + "_rejected",
        rejected,
    )


# ============================================================
# 11 — TYPE CONTRADICTION
# ============================================================

type_contradiction = (
    heartbeat.create_universal_worker_heartbeat(
        registration=reg_type_b,
        heartbeat_at="2026-08-17T00:00:02Z",
        sequence=2,
    )
)


try:

    heartbeat.validate_universal_worker_heartbeat_progression(
        previous=hb_a1_1,
        current=type_contradiction,
    )

except heartbeat.UniversalWorkerHeartbeatError as exc:

    rejected = (
        exc.code
        == "worker_heartbeat_type_mismatch"
    )

else:

    rejected = False


check(
    "worker_type_contradiction_rejected",
    rejected,
)


# ============================================================
# 12 — INVALID PRIOR/CURRENT OBJECTS
# ============================================================

for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        "",
        [],
        {},
        (),
        object(),
    ),
    start=1,
):

    try:

        heartbeat.validate_universal_worker_heartbeat_progression(
            previous=bad,
            current=hb_a1_1,
        )

    except heartbeat.UniversalWorkerHeartbeatError as exc:

        rejected = (
            exc.code
            == "invalid_previous_worker_heartbeat"
        )

    else:

        rejected = False

    check(
        "invalid_previous_object_"
        + str(index),
        rejected,
    )


for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        "",
        [],
        {},
        (),
        object(),
    ),
    start=1,
):

    try:

        heartbeat.validate_universal_worker_heartbeat_progression(
            previous=hb_a1_1,
            current=bad,
        )

    except heartbeat.UniversalWorkerHeartbeatError as exc:

        rejected = (
            exc.code
            == "invalid_current_worker_heartbeat"
        )

    else:

        rejected = False

    check(
        "invalid_current_object_"
        + str(index),
        rejected,
    )


# ============================================================
# 13 — PREVIOUS OPTIONALITY
# ============================================================

isolated_high_sequence = (
    heartbeat.create_universal_worker_heartbeat(
        registration=reg_a1,
        heartbeat_at="2026-08-17T00:10:00Z",
        sequence=50,
        previous_heartbeat=None,
    )
)

check(
    "prior_heartbeat_optional",
    isolated_high_sequence.sequence
    == 50,
)


# ============================================================
# 14 — SCHEMA TAMPER
# ============================================================

try:

    heartbeat.UniversalWorkerHeartbeat(
        worker_id="worker-a",
        worker_instance_id="instance-1",
        worker_type="semantic_worker",
        heartbeat_at="2026-08-17T00:00:01Z",
        sequence=1,
        schema_version="bad-schema",
    )

except heartbeat.UniversalWorkerHeartbeatError as exc:

    rejected = (
        exc.code
        == "invalid_worker_heartbeat_schema_version"
    )

else:

    rejected = False


check(
    "schema_tamper_rejected",
    rejected,
)


# ============================================================
# 15 — IMMUTABILITY
# ============================================================

for field_name in (
    "worker_id",
    "worker_instance_id",
    "worker_type",
    "heartbeat_at",
    "sequence",
    "schema_version",
):

    try:

        setattr(
            hb_a1_1,
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
# 16 — DETERMINISM
# ============================================================

repeat_a = (
    heartbeat.create_universal_worker_heartbeat(
        registration=reg_a1,
        heartbeat_at="2026-08-17T00:00:01Z",
        sequence=1,
    )
)

repeat_b = (
    heartbeat.create_universal_worker_heartbeat(
        registration=reg_a1,
        heartbeat_at="2026-08-17T00:00:01Z",
        sequence=1,
    )
)

check(
    "deterministic_creation",
    repeat_a
    == repeat_b,
)

check(
    "deterministic_identity",
    repeat_a.worker_identity
    == repeat_b.worker_identity,
)


# ============================================================
# 17 — EXACT FIELDS
# ============================================================

actual_fields = tuple(
    item.name
    for item in fields(
        heartbeat.UniversalWorkerHeartbeat
    )
)

expected_fields = (
    "worker_id",
    "worker_instance_id",
    "worker_type",
    "heartbeat_at",
    "sequence",
    "schema_version",
)

check(
    "fields_exact",
    actual_fields
    == expected_fields,
    actual_fields,
)


for forbidden_field in (
    "workspace_id",
    "pool_id",
    "job_id",
    "current_job_id",
    "lease_id",
    "lease_owner",
    "lease_state",
    "health",
    "health_state",
    "liveness",
    "stale",
    "fresh",
    "freshness",
    "age",
    "heartbeat_age",
    "heartbeat_interval",
    "capability",
    "capabilities",
    "capacity",
    "available_capacity",
    "available_slots",
    "state",
    "status",
):

    check(
        "forbidden_field_absent_"
        + forbidden_field,
        forbidden_field
        not in actual_fields,
    )


# ============================================================
# 18 — EXPLANATION CONTRACT
# ============================================================

explanation = (
    heartbeat.explain_universal_worker_heartbeat_v1()
)


expected_explanation = {
    "phase":
        "4.1.10",

    "component":
        "Universal Worker Heartbeats",

    "version":
        heartbeat.UNIVERSAL_WORKER_HEARTBEAT_VERSION,

    "schema_version":
        heartbeat.UNIVERSAL_WORKER_HEARTBEAT_SCHEMA_VERSION,
}


for key, expected in (
    expected_explanation.items()
):

    check(
        "explanation_"
        + key,
        explanation.get(
            key
        )
        == expected,
        explanation.get(
            key
        ),
    )


check(
    "identity_rule_complete",
    (
        "worker_id"
        in explanation.get(
            "identity_rule",
            "",
        )
        and
        "worker_instance_id"
        in explanation.get(
            "identity_rule",
            "",
        )
    ),
)

check(
    "timestamp_rule_caller_supplied",
    "caller-supplied"
    in explanation.get(
        "timestamp_rule",
        "",
    ),
)

check(
    "timestamp_rule_no_clock",
    "does not read the wall clock"
    in explanation.get(
        "timestamp_rule",
        "",
    ),
)

check(
    "sequence_rule_strict",
    "strictly increases"
    in explanation.get(
        "sequence_rule",
        "",
    ),
)

check(
    "duplicate_rule_explicit",
    "duplicate"
    in explanation.get(
        "duplicate_rule",
        "",
    ).lower(),
)

check(
    "ordering_rule_explicit",
    "lower sequence"
    in explanation.get(
        "ordering_rule",
        "",
    ),
)

check(
    "prior_evidence_boundary",
    "caller-supplied prior heartbeat"
    in explanation.get(
        "prior_evidence_rule",
        "",
    ),
)

check(
    "interval_external",
    "outside 4.1.10"
    in explanation.get(
        "interval_boundary",
        "",
    ),
)

check(
    "stale_owned_by_4_1_11",
    "4.1.11 Stale Worker Detection"
    in explanation.get(
        "freshness_boundary",
        "",
    ),
)

check(
    "health_owned_by_4_1_5",
    "4.1.5 Worker Health"
    in explanation.get(
        "health_boundary",
        "",
    ),
)

check(
    "recovery_owned_by_4_1_6",
    "4.1.6 Worker Recovery"
    in explanation.get(
        "recovery_boundary",
        "",
    ),
)

check(
    "legacy_runtime_preserved",
    "does not replace or invoke"
    in explanation.get(
        "legacy_runtime_boundary",
        "",
    ),
)

check(
    "orchestration_preserved",
    "does not replace or mutate"
    in explanation.get(
        "orchestration_boundary",
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
    "purity_complete",
    (
        "filesystem"
        in explanation.get(
            "purity_rule",
            "",
        )
        and
        "network"
        in explanation.get(
            "purity_rule",
            "",
        )
        and
        "clock"
        in explanation.get(
            "purity_rule",
            "",
        )
        and
        "thread"
        in explanation.get(
            "purity_rule",
            "",
        )
    ),
)


# ============================================================
# 19 — FULL PROHIBITION MATRIX
# ============================================================

required_prohibitions = (
    "does not generate heartbeat timestamps",
    "does not read the wall clock",
    "does not define heartbeat interval",
    "does not sleep between heartbeats",
    "does not run a heartbeat loop",
    "does not start heartbeat threads",
    "does not publish heartbeat over network",
    "does not write heartbeat files",
    "does not access Runtime State Store",
    "does not persist heartbeat evidence",
    "does not calculate heartbeat age",
    "does not calculate heartbeat freshness",
    "does not detect stale workers",
    "does not determine worker liveness",
    "does not determine worker health",
    "does not initiate worker recovery",
    "does not release worker leases",
    "does not requeue jobs",
    "does not cancel jobs",
    "does not mutate Worker Registration",
    "does not modify Worker Pool membership",
    "does not discover workers",
    "does not assign workers",
    "does not scale workers",
    "does not shut down workers",
    "does not drain workers",
    "does not inspect worker capabilities",
    "does not calculate worker capacity",
    "does not include current job state",
    "does not include workspace state",
    "does not invoke legacy runtime heartbeat publisher",
    "does not mutate orchestration heartbeat models",
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
# 20 — IMPORT BOUNDARY
# ============================================================

source = HEARTBEAT_PATH.read_text(
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
# 21 — API SURFACE
# ============================================================

expected_all = (
    "UNIVERSAL_WORKER_HEARTBEAT_VERSION",
    "UNIVERSAL_WORKER_HEARTBEAT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_HEARTBEAT_SEQUENCE",
    "UNIVERSAL_WORKER_HEARTBEAT_IDENTITY_SEPARATOR",
    "UniversalWorkerHeartbeatError",
    "UniversalWorkerHeartbeat",
    "normalize_universal_worker_heartbeat_timestamp",
    "normalize_universal_worker_heartbeat_sequence",
    "validate_universal_worker_heartbeat_progression",
    "create_universal_worker_heartbeat",
    "explain_universal_worker_heartbeat_v1",
)


check(
    "api_surface_exact",
    tuple(
        heartbeat.__all__
    )
    == expected_all,
    heartbeat.__all__,
)


# ============================================================
# 22 — FORBIDDEN SIDE-EFFECT CALLS
# ============================================================

forbidden_calls = {
    "open",
    "read_text",
    "write_text",
    "write_json",
    "mkdir",
    "unlink",
    "remove",

    "now",
    "utcnow",
    "now_iso",
    "time",
    "sleep",

    "Thread",
    "start",
    "create_task",

    "worker_heartbeat",
    "inspect_workers",

    "record_worker_status",
    "get_latest_worker_statuses",

    "get_runtime_state_store_registry",

    "evaluate_universal_worker_health",
    "evaluate_universal_worker_recovery",
    "evaluate_universal_worker_scaling",
    "evaluate_universal_worker_shutdown",

    "release_universal_worker_lease",
    "renew_universal_worker_lease",
    "acquire_universal_worker_lease",

    "enqueue_job",
    "dequeue_job",
    "requeue_job",
    "cancel_job",

    "assign_universal_worker",
    "discover_universal_workers",

    "add_universal_worker_pool_member",
    "remove_universal_worker_pool_member",

    "dispatch_job",
    "execute_job",

    "send",
    "post",
    "publish",
    "persist",
    "save",
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
    "no_forbidden_side_effect_calls",
    not found_forbidden_calls,
    found_forbidden_calls,
)


# ============================================================
# 23 — RESPONSIBILITY BLEED FUNCTION-NAME SCAN
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
    "stale_worker",
    "worker_liveness",
    "worker_health",
    "recover_worker",
    "release_lease",
    "requeue",
    "cancel_job",
    "assign_worker",
    "discover_worker",
    "scale_worker",
    "shutdown_worker",
    "drain_worker",
    "worker_capacity",
    "worker_capability",
    "heartbeat_loop",
    "heartbeat_thread",
    "heartbeat_publish",
    "heartbeat_persist",
    "heartbeat_age",
    "heartbeat_freshness",
):

    matches = tuple(
        name
        for name in function_names
        if token in name
    )

    check(
        "no_function_bleed_"
        + token,
        not matches,
        matches,
    )


# ============================================================
# 24 — SOURCE POLICY VOCABULARY
# ============================================================

source_lower = (
    source.lower()
)


for forbidden_symbol in (
    "heartbeat_interval =",
    "heartbeat_frequency =",
    "stale_threshold =",
    "freshness_threshold =",
    "worker_health =",
    "pool_id:",
    "workspace_id:",
    "current_job_id:",
    "lease_id:",
    "available_slots:",
):

    check(
        "no_policy_symbol_"
        + forbidden_symbol.replace(
            " ",
            "_"
        ),
        forbidden_symbol
        not in source_lower,
    )


# ============================================================
# 25 — PROTECTED AST MATRIX
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
# 26 — FINAL HEARTBEAT AST
# ============================================================

final_heartbeat_ast = ast_sha(
    HEARTBEAT_PATH
)


check(
    "heartbeat_ast_final",
    final_heartbeat_ast
    == EXPECTED_HEARTBEAT_AST,
    final_heartbeat_ast,
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
        "PHASE 4.1.10 — UNIVERSAL WORKER "
        "HEARTBEATS ADVERSARIAL REGRESSION"
    ),
    "=" * 112,
    "",
    (
        "WORKER HEARTBEAT AST SHA256: "
        + final_heartbeat_ast
    ),
    (
        "ORCHESTRATION MODELS AST: "
        + ast_sha(
            PROTECTED[
                "orchestration_models"
            ][0]
        )
    ),
    (
        "TMS ORCHESTRATION GOVERNANCE AST: "
        + ast_sha(
            PROTECTED[
                "tms_orchestration_governance"
            ][0]
        )
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
            "ADVERSARIAL WORKER HEARTBEAT REGRESSION: "
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
        "WORKER HEARTBEAT AST MODIFIED: NO",
        "4.1.1 WORKER REGISTRATION MODIFIED: NO",
        "4.1.2 WORKER DISCOVERY MODIFIED: NO",
        "4.1.3 WORKER ASSIGNMENT MODIFIED: NO",
        "4.1.4 WORKER LEASING MODIFIED: NO",
        "4.1.5 WORKER HEALTH MODIFIED: NO",
        "4.1.6 WORKER RECOVERY MODIFIED: NO",
        "4.1.7 WORKER SCALING MODIFIED: NO",
        "4.1.8 WORKER SHUTDOWN MODIFIED: NO",
        "4.1.9 WORKER POOL MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "EXISTING UNIVERSAL RUNTIME WORKER MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "RUNTIME SHUTDOWN PROCESS MODIFIED: NO",
        "RUNTIME LIFECYCLE MANAGER MODIFIED: NO",
        "ORCHESTRATION MODELS MODIFIED: NO",
        "TMS ORCHESTRATION GOVERNANCE MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "WALL CLOCK READ: NO",
        "TIMESTAMP GENERATED INTERNALLY: NO",
        "HEARTBEAT INTERVAL DEFINED: NO",
        "HEARTBEAT LOOP STARTED: NO",
        "BACKGROUND THREAD STARTED: NO",
        "NETWORK HEARTBEAT PUBLISHED: NO",
        "HEARTBEAT FILE WRITTEN: NO",
        "LEGACY RUNTIME HEARTBEAT INVOKED: NO",
        "ORCHESTRATION HEARTBEAT MODEL MUTATED: NO",
        "TMS WORKER STATUS MUTATED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "HEARTBEAT EVIDENCE PERSISTED: NO",
        "HEARTBEAT AGE CALCULATED: NO",
        "HEARTBEAT FRESHNESS CALCULATED: NO",
        "STALE WORKER DETECTED: NO",
        "WORKER LIVENESS DECIDED: NO",
        "WORKER HEALTH DECIDED: NO",
        "WORKER RECOVERY INITIATED: NO",
        "LEASE ACQUIRED/RENEWED/RELEASED: NO",
        "JOB REQUEUED/CANCELLED: NO",
        "WORKER REGISTRATION MUTATED: NO",
        "WORKER POOL MEMBERSHIP MODIFIED: NO",
        "WORKER DISCOVERED/ASSIGNED: NO",
        "WORKER SCALING PERFORMED: NO",
        "WORKER SHUTDOWN PERFORMED: NO",
        "WORKER DRAIN PERFORMED: NO",
        "WORKER CAPABILITY INSPECTED: NO",
        "WORKER CAPACITY CALCULATED: NO",
        "",
        (
            "STATUS: REGRESSION PASS "
            "— FINAL CERTIFICATION REQUIRED"
            if passed == total
            else
            "STATUS: REGRESSION FAILED — DO NOT CERTIFY"
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
        "Phase 4.1.10 Worker Heartbeat adversarial regression failed."
    )
