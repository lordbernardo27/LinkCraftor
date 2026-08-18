from __future__ import annotations

import ast
import hashlib
import importlib
import math
import sys
from dataclasses import fields
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

STALE_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "stale.py"
)

EXPECTED_STALE_AST = (
    "22105ACBF984E26019080E53939617CE14BDF51BF5A9B149BD39E10B6B87B9DD"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_11_stale_worker_regression.txt"
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

if not STALE_PATH.exists():

    raise SystemExit(
        "4.1.11 Stale Worker authority is missing."
    )


initial_stale_ast = ast_sha(
    STALE_PATH
)


if initial_stale_ast != EXPECTED_STALE_AST:

    raise SystemExit(
        (
            "Stale Worker AST changed before regression.\n"
            "EXPECTED: "
            + EXPECTED_STALE_AST
            + "\nACTUAL:   "
            + initial_stale_ast
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
                "4.1.11 adversarial regression: "
                + name
                + "\nEXPECTED: "
                + expected
                + "\nACTUAL:   "
                + actual
            )
        )


# ============================================================
# IMPORTS
# ============================================================

sys.path.insert(
    0,
    str(ROOT),
)

registration = importlib.import_module(
    "backend.server.runtime.universal_worker.registration"
)

heartbeat = importlib.import_module(
    "backend.server.runtime.universal_worker.heartbeat"
)

module_name = (
    "backend.server.runtime."
    "universal_worker.stale"
)

sys.modules.pop(
    module_name,
    None,
)

stale = importlib.import_module(
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


reg = make_registration()

hb = (
    heartbeat.create_universal_worker_heartbeat(
        registration=reg,
        heartbeat_at="2026-08-17T00:00:00Z",
        sequence=10,
    )
)


# ============================================================
# 1 — AST / CONSTANTS / STATES
# ============================================================

check(
    "stale_ast_stable",
    ast_sha(
        STALE_PATH
    )
    == EXPECTED_STALE_AST,
    ast_sha(
        STALE_PATH
    ),
)

check(
    "version_exact",
    stale.UNIVERSAL_STALE_WORKER_DETECTION_VERSION
    == "universal_stale_worker_detection_v4.1.11",
)

check(
    "schema_exact",
    stale.UNIVERSAL_STALE_WORKER_RESULT_SCHEMA_VERSION
    == "universal_stale_worker_result_schema_v1",
)

check(
    "threshold_max_exact",
    stale.MAX_UNIVERSAL_STALE_WORKER_THRESHOLD_SECONDS
    == 2_147_483_647,
)

check(
    "states_exact",
    tuple(
        state.value
        for state in stale.UniversalWorkerStalenessState
    )
    == (
        "ACTIVE",
        "STALE",
    ),
)


# ============================================================
# 2 — THRESHOLD ATTACK MATRIX
# ============================================================

for value in (
    1,
    2,
    59,
    60,
    61,
    3600,
    stale.MAX_UNIVERSAL_STALE_WORKER_THRESHOLD_SECONDS,
):

    check(
        "threshold_valid_"
        + str(value),
        stale.normalize_universal_stale_worker_threshold_seconds(
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
        -100,
        1.0,
        60.0,
        float("nan"),
        float("inf"),
        "",
        "1",
        "60",
        [],
        {},
        (),
        set(),
        object(),
    ),
    start=1,
):

    try:

        stale.normalize_universal_stale_worker_threshold_seconds(
            bad
        )

    except stale.UniversalStaleWorkerError as exc:

        rejected = (
            exc.code
            == "invalid_stale_worker_threshold"
        )

    else:

        rejected = False

    check(
        "invalid_threshold_attack_"
        + str(index),
        rejected,
        type(
            bad
        ).__name__,
    )


for overflow in (
    stale.MAX_UNIVERSAL_STALE_WORKER_THRESHOLD_SECONDS
    + 1,
    stale.MAX_UNIVERSAL_STALE_WORKER_THRESHOLD_SECONDS
    + 100,
):

    try:

        stale.normalize_universal_stale_worker_threshold_seconds(
            overflow
        )

    except stale.UniversalStaleWorkerError as exc:

        rejected = (
            exc.code
            == "stale_worker_threshold_too_large"
        )

    else:

        rejected = False

    check(
        "threshold_overflow_"
        + str(overflow),
        rejected,
    )


# ============================================================
# 3 — EVALUATED_AT ATTACK MATRIX
# ============================================================

valid_evaluation_timestamps = (
    (
        "2026-08-17T00:01:00Z",
        "2026-08-17T00:01:00+00:00",
    ),
    (
        "2026-08-17T00:01:00+00:00",
        "2026-08-17T00:01:00+00:00",
    ),
    (
        " 2026-08-17T00:01:00Z ",
        "2026-08-17T00:01:00+00:00",
    ),
    (
        "2026-08-17T00:01:00.123456Z",
        "2026-08-17T00:01:00.123456+00:00",
    ),
)


for index, (
    raw,
    expected,
) in enumerate(
    valid_evaluation_timestamps,
    start=1,
):

    actual = (
        stale.normalize_universal_stale_worker_evaluated_at(
            raw
        )
    )

    check(
        "evaluation_timestamp_valid_"
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
        [],
        {},
        (),
        object(),
    ),
    start=1,
):

    try:

        stale.normalize_universal_stale_worker_evaluated_at(
            bad
        )

    except stale.UniversalStaleWorkerError:

        rejected = True

    else:

        rejected = False

    check(
        "evaluation_timestamp_type_attack_"
        + str(index),
        rejected,
    )


for index, bad in enumerate(
    (
        "",
        " ",
        "\t",
        "\n",
        "not-a-date",
        "2026-13-17T00:00:00Z",
        "2026-08-32T00:00:00Z",
        "2026-08-17T25:00:00Z",
        "2026-08-17T00:00:00",
        "2026-08-17 00:00:00",
        "2026-08-17T01:00:00+01:00",
        "2026-08-16T19:00:00-05:00",
    ),
    start=1,
):

    try:

        stale.normalize_universal_stale_worker_evaluated_at(
            bad
        )

    except stale.UniversalStaleWorkerError:

        rejected = True

    else:

        rejected = False

    check(
        "evaluation_timestamp_invalid_"
        + str(index),
        rejected,
        bad,
    )


# ============================================================
# 4 — THRESHOLD BOUNDARY MATRIX
# ============================================================

boundary_cases = (
    (
        "2026-08-17T00:00:00Z",
        60,
        0.0,
        "ACTIVE",
    ),
    (
        "2026-08-17T00:00:59Z",
        60,
        59.0,
        "ACTIVE",
    ),
    (
        "2026-08-17T00:00:59.999999Z",
        60,
        59.999999,
        "ACTIVE",
    ),
    (
        "2026-08-17T00:01:00Z",
        60,
        60.0,
        "STALE",
    ),
    (
        "2026-08-17T00:01:00.000001Z",
        60,
        60.000001,
        "STALE",
    ),
    (
        "2026-08-17T00:01:01Z",
        60,
        61.0,
        "STALE",
    ),
)


for index, (
    evaluated_at,
    threshold,
    expected_age,
    expected_state,
) in enumerate(
    boundary_cases,
    start=1,
):

    result = (
        stale.evaluate_universal_stale_worker(
            heartbeat=hb,
            evaluated_at=evaluated_at,
            stale_threshold_seconds=threshold,
        )
    )

    check(
        "boundary_age_"
        + str(index),
        math.isclose(
            result.age_seconds,
            expected_age,
            rel_tol=0.0,
            abs_tol=0.0000001,
        ),
        result.age_seconds,
    )

    check(
        "boundary_state_"
        + str(index),
        result.state.value
        == expected_state,
        result.state.value,
    )


# ============================================================
# 5 — ONE-SECOND THRESHOLD
# ============================================================

one_second_active = (
    stale.evaluate_universal_stale_worker(
        heartbeat=hb,
        evaluated_at="2026-08-17T00:00:00.999999Z",
        stale_threshold_seconds=1,
    )
)

check(
    "one_second_below_active",
    one_second_active.is_active
    is True,
)


one_second_equal = (
    stale.evaluate_universal_stale_worker(
        heartbeat=hb,
        evaluated_at="2026-08-17T00:00:01Z",
        stale_threshold_seconds=1,
    )
)

check(
    "one_second_equal_stale",
    one_second_equal.is_stale
    is True,
)


# ============================================================
# 6 — FUTURE HEARTBEAT CONTRADICTIONS
# ============================================================

for index, evaluated_at in enumerate(
    (
        "2026-08-16T23:59:59Z",
        "2026-08-16T23:59:59.999999Z",
    ),
    start=1,
):

    try:

        stale.evaluate_universal_stale_worker(
            heartbeat=hb,
            evaluated_at=evaluated_at,
            stale_threshold_seconds=60,
        )

    except stale.UniversalStaleWorkerError as exc:

        rejected = (
            exc.code
            == "future_worker_heartbeat"
        )

    else:

        rejected = False

    check(
        "future_heartbeat_attack_"
        + str(index),
        rejected,
    )


# ============================================================
# 7 — MISSING / NONCANONICAL HEARTBEAT
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

        stale.evaluate_universal_stale_worker(
            heartbeat=bad,
            evaluated_at="2026-08-17T00:01:00Z",
            stale_threshold_seconds=60,
        )

    except stale.UniversalStaleWorkerError as exc:

        rejected = (
            exc.code
            == "invalid_stale_worker_heartbeat"
        )

    else:

        rejected = False

    check(
        "heartbeat_object_attack_"
        + str(index),
        rejected,
    )


# ============================================================
# 8 — HEARTBEAT IDENTITY / SEQUENCE ECHO
# ============================================================

reg_instance_2 = make_registration(
    worker_id="worker-a",
    instance_id="instance-2",
)

hb_instance_2 = (
    heartbeat.create_universal_worker_heartbeat(
        registration=reg_instance_2,
        heartbeat_at="2026-08-17T00:00:00Z",
        sequence=27,
    )
)

instance_result = (
    stale.evaluate_universal_stale_worker(
        heartbeat=hb_instance_2,
        evaluated_at="2026-08-17T00:01:00Z",
        stale_threshold_seconds=60,
    )
)


check(
    "instance_identity_preserved",
    instance_result.worker_identity
    == "worker-a::instance-2",
)

check(
    "heartbeat_sequence_preserved",
    instance_result.heartbeat_sequence
    == 27,
)

check(
    "heartbeat_type_preserved",
    instance_result.worker_type
    == hb_instance_2.worker_type,
)


# ============================================================
# 9 — RESULT STATE FORGERY
# ============================================================

for name, (
    age,
    state,
) in {
    "active_as_stale": (
        59.0,
        stale.UniversalWorkerStalenessState.STALE,
    ),
    "stale_as_active": (
        60.0,
        stale.UniversalWorkerStalenessState.ACTIVE,
    ),
}.items():

    evaluated_at = (
        "2026-08-17T00:00:59Z"
        if age == 59.0
        else
        "2026-08-17T00:01:00Z"
    )

    try:

        stale.UniversalStaleWorkerResult(
            worker_id=hb.worker_id,
            worker_instance_id=hb.worker_instance_id,
            worker_type=hb.worker_type,
            heartbeat_at=hb.heartbeat_at,
            heartbeat_sequence=hb.sequence,
            evaluated_at=evaluated_at,
            stale_threshold_seconds=60,
            age_seconds=age,
            state=state,
        )

    except stale.UniversalStaleWorkerError as exc:

        rejected = (
            exc.code
            == "inconsistent_stale_worker_state"
        )

    else:

        rejected = False

    check(
        "forged_state_"
        + name,
        rejected,
    )


# ============================================================
# 10 — RESULT AGE FORGERY
# ============================================================

for index, forged_age in enumerate(
    (
        0.0,
        59.0,
        59.999999,
        61.0,
        1000.0,
    ),
    start=1,
):

    if forged_age == 60.0:
        continue

    try:

        stale.UniversalStaleWorkerResult(
            worker_id=hb.worker_id,
            worker_instance_id=hb.worker_instance_id,
            worker_type=hb.worker_type,
            heartbeat_at=hb.heartbeat_at,
            heartbeat_sequence=hb.sequence,
            evaluated_at="2026-08-17T00:01:00Z",
            stale_threshold_seconds=60,
            age_seconds=forged_age,
            state=stale.UniversalWorkerStalenessState.STALE,
        )

    except stale.UniversalStaleWorkerError as exc:

        rejected = (
            exc.code
            == "inconsistent_stale_worker_age"
        )

    else:

        rejected = False

    check(
        "forged_age_"
        + str(index),
        rejected,
        forged_age,
    )


# ============================================================
# 11 — RESULT AGE TYPE / SPECIAL FLOATS
# ============================================================

for index, bad_age in enumerate(
    (
        None,
        True,
        False,
        60,
        "60",
        [],
        {},
        (),
    ),
    start=1,
):

    try:

        stale.UniversalStaleWorkerResult(
            worker_id=hb.worker_id,
            worker_instance_id=hb.worker_instance_id,
            worker_type=hb.worker_type,
            heartbeat_at=hb.heartbeat_at,
            heartbeat_sequence=hb.sequence,
            evaluated_at="2026-08-17T00:01:00Z",
            stale_threshold_seconds=60,
            age_seconds=bad_age,
            state=stale.UniversalWorkerStalenessState.STALE,
        )

    except stale.UniversalStaleWorkerError:

        rejected = True

    else:

        rejected = False

    check(
        "age_type_attack_"
        + str(index),
        rejected,
    )


for name, special_age in (
    (
        "nan",
        float("nan"),
    ),
    (
        "positive_infinity",
        float("inf"),
    ),
    (
        "negative_infinity",
        float("-inf"),
    ),
):

    try:

        stale.UniversalStaleWorkerResult(
            worker_id=hb.worker_id,
            worker_instance_id=hb.worker_instance_id,
            worker_type=hb.worker_type,
            heartbeat_at=hb.heartbeat_at,
            heartbeat_sequence=hb.sequence,
            evaluated_at="2026-08-17T00:01:00Z",
            stale_threshold_seconds=60,
            age_seconds=special_age,
            state=stale.UniversalWorkerStalenessState.STALE,
        )

    except stale.UniversalStaleWorkerError:

        rejected = True

    else:

        rejected = False

    check(
        "special_age_"
        + name
        + "_rejected",
        rejected,
    )


# ============================================================
# 12 — RAW STATE ATTACKS
# ============================================================

for index, bad_state in enumerate(
    (
        "ACTIVE",
        "STALE",
        "",
        None,
        True,
        False,
        0,
    ),
    start=1,
):

    try:

        stale.UniversalStaleWorkerResult(
            worker_id=hb.worker_id,
            worker_instance_id=hb.worker_instance_id,
            worker_type=hb.worker_type,
            heartbeat_at=hb.heartbeat_at,
            heartbeat_sequence=hb.sequence,
            evaluated_at="2026-08-17T00:01:00Z",
            stale_threshold_seconds=60,
            age_seconds=60.0,
            state=bad_state,
        )

    except stale.UniversalStaleWorkerError as exc:

        rejected = (
            exc.code
            == "invalid_stale_worker_state"
        )

    else:

        rejected = False

    check(
        "raw_state_attack_"
        + str(index),
        rejected,
        repr(
            bad_state
        ),
    )


# ============================================================
# 13 — RESULT IDENTITY FORGERY
#
# A public evidence result should not silently admit identities
# that canonical Worker Heartbeat evidence could never contain.
# These checks may expose a hardening gap. If so, regression must
# FAIL and the production authority will be minimally patched.
# ============================================================

for field_name, bad_value in (
    (
        "worker_id",
        "",
    ),
    (
        "worker_id",
        " ",
    ),
    (
        "worker_id",
        "\t",
    ),
    (
        "worker_instance_id",
        "",
    ),
    (
        "worker_instance_id",
        " ",
    ),
    (
        "worker_type",
        "",
    ),
    (
        "worker_type",
        " ",
    ),
):

    kwargs = {
        "worker_id":
            hb.worker_id,

        "worker_instance_id":
            hb.worker_instance_id,

        "worker_type":
            hb.worker_type,

        "heartbeat_at":
            hb.heartbeat_at,

        "heartbeat_sequence":
            hb.sequence,

        "evaluated_at":
            "2026-08-17T00:01:00Z",

        "stale_threshold_seconds":
            60,

        "age_seconds":
            60.0,

        "state":
            stale.UniversalWorkerStalenessState.STALE,
    }

    kwargs[
        field_name
    ] = bad_value

    try:

        stale.UniversalStaleWorkerResult(
            **kwargs
        )

    except stale.UniversalStaleWorkerError:

        rejected = True

    else:

        rejected = False

    check(
        (
            "forged_identity_"
            + field_name
            + "_"
            + repr(
                bad_value
            )
        ),
        rejected,
    )


# ============================================================
# 14 — HEARTBEAT SEQUENCE FORGERY
#
# Result evidence must not admit heartbeat sequences impossible
# under the frozen 4.1.10 Heartbeat contract.
# ============================================================

for index, bad_sequence in enumerate(
    (
        None,
        True,
        False,
        0,
        -1,
        1.0,
        "1",
        heartbeat.MAX_UNIVERSAL_WORKER_HEARTBEAT_SEQUENCE
        + 1,
    ),
    start=1,
):

    try:

        stale.UniversalStaleWorkerResult(
            worker_id=hb.worker_id,
            worker_instance_id=hb.worker_instance_id,
            worker_type=hb.worker_type,
            heartbeat_at=hb.heartbeat_at,
            heartbeat_sequence=bad_sequence,
            evaluated_at="2026-08-17T00:01:00Z",
            stale_threshold_seconds=60,
            age_seconds=60.0,
            state=stale.UniversalWorkerStalenessState.STALE,
        )

    except stale.UniversalStaleWorkerError:

        rejected = True

    else:

        rejected = False

    check(
        "forged_heartbeat_sequence_"
        + str(index),
        rejected,
        repr(
            bad_sequence
        ),
    )


# ============================================================
# 15 — RESULT TIMESTAMP FORGERY
# ============================================================

for index, bad_timestamp in enumerate(
    (
        "",
        " ",
        "not-a-date",
        "2026-08-17T00:00:00",
        "2026-08-17T01:00:00+01:00",
    ),
    start=1,
):

    try:

        stale.UniversalStaleWorkerResult(
            worker_id=hb.worker_id,
            worker_instance_id=hb.worker_instance_id,
            worker_type=hb.worker_type,
            heartbeat_at=bad_timestamp,
            heartbeat_sequence=hb.sequence,
            evaluated_at="2026-08-17T00:01:00Z",
            stale_threshold_seconds=60,
            age_seconds=60.0,
            state=stale.UniversalWorkerStalenessState.STALE,
        )

    except Exception:

        rejected = True

    else:

        rejected = False

    check(
        "forged_heartbeat_at_"
        + str(index),
        rejected,
    )


for index, bad_timestamp in enumerate(
    (
        "",
        " ",
        "not-a-date",
        "2026-08-17T00:01:00",
        "2026-08-17T01:01:00+01:00",
    ),
    start=1,
):

    try:

        stale.UniversalStaleWorkerResult(
            worker_id=hb.worker_id,
            worker_instance_id=hb.worker_instance_id,
            worker_type=hb.worker_type,
            heartbeat_at=hb.heartbeat_at,
            heartbeat_sequence=hb.sequence,
            evaluated_at=bad_timestamp,
            stale_threshold_seconds=60,
            age_seconds=60.0,
            state=stale.UniversalWorkerStalenessState.STALE,
        )

    except Exception:

        rejected = True

    else:

        rejected = False

    check(
        "forged_evaluated_at_"
        + str(index),
        rejected,
    )


# ============================================================
# 16 — RESULT FUTURE-HEARTBEAT FORGERY
# ============================================================

try:

    stale.UniversalStaleWorkerResult(
        worker_id=hb.worker_id,
        worker_instance_id=hb.worker_instance_id,
        worker_type=hb.worker_type,
        heartbeat_at="2026-08-17T00:01:01Z",
        heartbeat_sequence=hb.sequence,
        evaluated_at="2026-08-17T00:01:00Z",
        stale_threshold_seconds=60,
        age_seconds=0.0,
        state=stale.UniversalWorkerStalenessState.ACTIVE,
    )

except stale.UniversalStaleWorkerError as exc:

    rejected = (
        exc.code
        == "future_worker_heartbeat"
    )

else:

    rejected = False


check(
    "forged_future_heartbeat_rejected",
    rejected,
)


# ============================================================
# 17 — SCHEMA TAMPERING
# ============================================================

try:

    stale.UniversalStaleWorkerResult(
        worker_id=hb.worker_id,
        worker_instance_id=hb.worker_instance_id,
        worker_type=hb.worker_type,
        heartbeat_at=hb.heartbeat_at,
        heartbeat_sequence=hb.sequence,
        evaluated_at="2026-08-17T00:01:00Z",
        stale_threshold_seconds=60,
        age_seconds=60.0,
        state=stale.UniversalWorkerStalenessState.STALE,
        schema_version="tampered",
    )

except stale.UniversalStaleWorkerError as exc:

    rejected = (
        exc.code
        == "invalid_stale_worker_result_schema_version"
    )

else:

    rejected = False


check(
    "schema_tamper_rejected",
    rejected,
)


# ============================================================
# 18 — IMMUTABILITY
# ============================================================

canonical_result = (
    stale.evaluate_universal_stale_worker(
        heartbeat=hb,
        evaluated_at="2026-08-17T00:01:00Z",
        stale_threshold_seconds=60,
    )
)


for field_name in (
    "worker_id",
    "worker_instance_id",
    "worker_type",
    "heartbeat_at",
    "heartbeat_sequence",
    "evaluated_at",
    "stale_threshold_seconds",
    "age_seconds",
    "state",
    "schema_version",
):

    try:

        setattr(
            canonical_result,
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
# 19 — DETERMINISM
# ============================================================

repeat_a = (
    stale.evaluate_universal_stale_worker(
        heartbeat=hb,
        evaluated_at="2026-08-17T00:01:00Z",
        stale_threshold_seconds=60,
    )
)

repeat_b = (
    stale.evaluate_universal_stale_worker(
        heartbeat=hb,
        evaluated_at="2026-08-17T00:01:00Z",
        stale_threshold_seconds=60,
    )
)


check(
    "deterministic_result",
    repeat_a
    == repeat_b,
)

check(
    "deterministic_age",
    repeat_a.age_seconds
    == repeat_b.age_seconds,
)

check(
    "deterministic_state",
    repeat_a.state
    is repeat_b.state,
)


# ============================================================
# 20 — EXACT RESULT FIELD CONTRACT
# ============================================================

actual_fields = tuple(
    field.name
    for field in fields(
        stale.UniversalStaleWorkerResult
    )
)


expected_fields = (
    "worker_id",
    "worker_instance_id",
    "worker_type",
    "heartbeat_at",
    "heartbeat_sequence",
    "evaluated_at",
    "stale_threshold_seconds",
    "age_seconds",
    "state",
    "schema_version",
)


check(
    "result_fields_exact",
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
    "recovery",
    "recoverable",
    "shutdown",
    "drain",
    "capability",
    "capabilities",
    "capacity",
    "available_slots",
    "registered",
    "discovered",
    "assigned",
):

    check(
        "forbidden_field_absent_"
        + forbidden_field,
        forbidden_field
        not in actual_fields,
    )


# ============================================================
# 21 — EXPLANATION CONTRACT
# ============================================================

explanation = (
    stale.explain_universal_stale_worker_detection_v1()
)


check(
    "explanation_phase",
    explanation.get(
        "phase"
    )
    == "4.1.11",
)

check(
    "explanation_component",
    explanation.get(
        "component"
    )
    == "Universal Stale Worker Detection",
)

check(
    "explanation_version",
    explanation.get(
        "version"
    )
    == stale.UNIVERSAL_STALE_WORKER_DETECTION_VERSION,
)

check(
    "explanation_schema",
    explanation.get(
        "result_schema_version"
    )
    == stale.UNIVERSAL_STALE_WORKER_RESULT_SCHEMA_VERSION,
)

check(
    "input_uses_4_1_10",
    "4.1.10"
    in explanation.get(
        "input_rule",
        "",
    ),
)

check(
    "evaluation_time_caller_supplied",
    "caller-supplied"
    in explanation.get(
        "time_rule",
        "",
    ),
)

check(
    "no_wall_clock_rule",
    "does not read the wall clock"
    in explanation.get(
        "time_rule",
        "",
    ),
)

check(
    "threshold_caller_supplied",
    "caller-supplied"
    in explanation.get(
        "threshold_rule",
        "",
    ),
)

check(
    "active_less_than_rule",
    "strictly less"
    in explanation.get(
        "active_rule",
        "",
    ),
)

check(
    "stale_greater_equal_rule",
    "greater than or equal"
    in explanation.get(
        "stale_rule",
        "",
    ),
)

check(
    "equality_rule",
    "is STALE"
    in explanation.get(
        "equality_rule",
        "",
    ),
)

check(
    "future_heartbeat_rule",
    "rejected"
    in explanation.get(
        "future_heartbeat_rule",
        "",
    ),
)

check(
    "missing_heartbeat_rule",
    "invalid input"
    in explanation.get(
        "missing_heartbeat_rule",
        "",
    ),
)

check(
    "age_owned_here",
    "owns deterministic heartbeat"
    in explanation.get(
        "age_rule",
        "",
    ),
)

check(
    "health_boundary",
    "not UNHEALTHY"
    in explanation.get(
        "health_boundary",
        "",
    ),
)

check(
    "lease_boundary",
    "independent"
    in explanation.get(
        "lease_boundary",
        "",
    ),
)

check(
    "recovery_boundary",
    "evidence only"
    in explanation.get(
        "recovery_boundary",
        "",
    ),
)

check(
    "queue_recovery_boundary",
    "may later consume"
    in explanation.get(
        "queue_recovery_boundary",
        "",
    ),
)

check(
    "registration_pool_boundary",
    "does not deregister"
    in explanation.get(
        "registration_pool_boundary",
        "",
    ),
)

check(
    "shutdown_drain_boundary",
    "does not automatically"
    in explanation.get(
        "shutdown_drain_boundary",
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
    "no external mutation or I/O"
    in explanation.get(
        "purity_rule",
        "",
    ),
)


# ============================================================
# 22 — PROHIBITION MATRIX
# ============================================================

required_prohibitions = (
    "does not read the wall clock",
    "does not generate evaluation timestamps",
    "does not define a global stale threshold",
    "does not define heartbeat interval",
    "does not accept missing heartbeat as STALE",
    "does not accept missing heartbeat as ACTIVE",
    "does not create UNKNOWN staleness",
    "does not determine Worker Health",
    "does not mark workers UNHEALTHY",
    "does not initiate Worker Recovery",
    "does not mark jobs FAILED",
    "does not requeue jobs",
    "does not cancel jobs",
    "does not acquire leases",
    "does not renew leases",
    "does not release leases",
    "does not equate stale worker with expired lease",
    "does not modify Worker Registration",
    "does not deregister workers",
    "does not modify Worker Pool membership",
    "does not discover workers",
    "does not assign workers",
    "does not scale workers",
    "does not shut down workers",
    "does not drain workers",
    "does not inspect worker capabilities",
    "does not calculate worker capacity",
    "does not access Runtime State Store",
    "does not access orchestration",
    "does not persist stale state",
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
# 23 — IMPORT BOUNDARY
# ============================================================

source = STALE_PATH.read_text(
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
        "backend.server.runtime.universal_worker.heartbeat",
        "backend.server.runtime.universal_worker.registration",
    ],
    backend_imports,
)


# ============================================================
# 24 — EXACT API SURFACE
# ============================================================

expected_all = (
    "UNIVERSAL_STALE_WORKER_DETECTION_VERSION",
    "UNIVERSAL_STALE_WORKER_RESULT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_STALE_WORKER_THRESHOLD_SECONDS",
    "UniversalStaleWorkerError",
    "UniversalWorkerStalenessState",
    "UniversalStaleWorkerResult",
    "normalize_universal_stale_worker_threshold_seconds",
    "normalize_universal_stale_worker_evaluated_at",
    "evaluate_universal_stale_worker",
    "explain_universal_stale_worker_detection_v1",
)


check(
    "api_surface_exact",
    tuple(
        stale.__all__
    )
    == expected_all,
    stale.__all__,
)


# ============================================================
# 25 — SIDE-EFFECT / RESPONSIBILITY BLEED
# ============================================================

forbidden_call_names = {
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

    "worker_heartbeat",

    "evaluate_universal_worker_health",
    "evaluate_universal_worker_recovery",
    "evaluate_universal_worker_scaling",
    "evaluate_universal_worker_shutdown",

    "acquire_universal_worker_lease",
    "renew_universal_worker_lease",
    "release_universal_worker_lease",

    "enqueue_job",
    "dequeue_job",
    "requeue_job",
    "cancel_job",
    "mark_job_failed",

    "assign_universal_worker",
    "discover_universal_workers",

    "add_universal_worker_pool_member",
    "remove_universal_worker_pool_member",

    "record_worker_status",
    "get_latest_worker_statuses",

    "get_runtime_state_store_registry",

    "dispatch_job",
    "execute_job",

    "persist",
    "save",
    "shutdown",
    "drain",
    "terminate",
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
        name = node.func.id

    elif isinstance(
        node.func,
        ast.Attribute,
    ):
        name = node.func.attr

    else:
        continue

    if name in forbidden_call_names:

        found_forbidden_calls.append(
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
    not found_forbidden_calls,
    found_forbidden_calls,
)


# ============================================================
# 26 — NO HIDDEN DEFAULT THRESHOLD
# ============================================================

source_lower = (
    source.lower()
)


for forbidden_symbol in (
    "default_stale_threshold",
    "global_stale_threshold",
    "stale_threshold =",
    "heartbeat_timeout =",
    "heartbeat_ttl =",
    "worker_timeout =",
    "default_timeout =",
):

    check(
        "no_hidden_threshold_"
        + forbidden_symbol.replace(
            " ",
            "_"
        ),
        forbidden_symbol
        not in source_lower,
    )


# ============================================================
# 27 — PROTECTED AUTHORITY MATRIX
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
# 28 — FINAL AST RECHECK
# ============================================================

final_stale_ast = ast_sha(
    STALE_PATH
)


check(
    "stale_ast_final",
    final_stale_ast
    == EXPECTED_STALE_AST,
    final_stale_ast,
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

failures = [
    (
        name,
        detail,
    )
    for name, ok, detail
    in checks
    if not ok
]


lines = [
    (
        "PHASE 4.1.11 — UNIVERSAL STALE WORKER "
        "DETECTION ADVERSARIAL REGRESSION"
    ),
    "=" * 112,
    "",
    (
        "STALE WORKER AST SHA256: "
        + final_stale_ast
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


if failures:

    lines.extend(
        [
            "",
            "FAILURE SUMMARY",
            "-" * 112,
        ]
    )

    for name, detail in failures:

        lines.append(
            "FAIL: "
            + name
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
            "ADVERSARIAL STALE WORKER REGRESSION: "
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
        "STALE WORKER AST MODIFIED: NO",
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
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "RUNTIME SHUTDOWN PROCESS MODIFIED: NO",
        "RUNTIME LIFECYCLE MANAGER MODIFIED: NO",
        "ORCHESTRATION MODELS MODIFIED: NO",
        "TMS ORCHESTRATION GOVERNANCE MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "WALL CLOCK READ: NO",
        "EVALUATION TIME GENERATED INTERNALLY: NO",
        "GLOBAL STALE THRESHOLD DEFINED: NO",
        "MISSING HEARTBEAT CLASSIFIED: NO",
        "UNKNOWN STALENESS CREATED: NO",
        "WORKER HEALTH MODIFIED: NO",
        "WORKER RECOVERY INITIATED: NO",
        "LEASE MUTATED: NO",
        "JOB FAILED/REQUEUED/CANCELLED: NO",
        "WORKER REGISTRATION MUTATED: NO",
        "WORKER DEREGISTERED: NO",
        "WORKER POOL MEMBERSHIP MODIFIED: NO",
        "WORKER DISCOVERED/ASSIGNED: NO",
        "WORKER SCALING PERFORMED: NO",
        "WORKER SHUTDOWN PERFORMED: NO",
        "WORKER DRAIN PERFORMED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "STALE STATE PERSISTED: NO",
        "",
        (
            "STATUS: REGRESSION PASS "
            "— FINAL CERTIFICATION REQUIRED"
            if passed == total
            else
            "STATUS: REGRESSION FAILED — PATCH REQUIRED BEFORE CERTIFICATION"
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
        "Phase 4.1.11 Stale Worker adversarial regression failed."
    )
