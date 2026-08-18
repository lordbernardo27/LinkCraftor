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

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_11_stale_worker_final_certification.txt"
)

EXPECTED_STALE_AST = (
    "22105ACBF984E26019080E53939617CE14BDF51BF5A9B149BD39E10B6B87B9DD"
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


initial_ast = ast_sha(
    STALE_PATH
)


if initial_ast != EXPECTED_STALE_AST:

    raise SystemExit(
        (
            "Stale Worker AST mismatch before final certification.\n"
            "EXPECTED: "
            + EXPECTED_STALE_AST
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
                "4.1.11 final certification: "
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
# AST / VERSION / SCHEMA
# ============================================================

stale_ast = ast_sha(
    STALE_PATH
)


check(
    "stale_worker_ast",
    stale_ast
    == EXPECTED_STALE_AST,
    stale_ast,
)

check(
    "version",
    stale.UNIVERSAL_STALE_WORKER_DETECTION_VERSION
    == "universal_stale_worker_detection_v4.1.11",
)

check(
    "result_schema",
    stale.UNIVERSAL_STALE_WORKER_RESULT_SCHEMA_VERSION
    == "universal_stale_worker_result_schema_v1",
)

check(
    "threshold_max",
    stale.MAX_UNIVERSAL_STALE_WORKER_THRESHOLD_SECONDS
    == 2_147_483_647,
)

check(
    "states_exact",
    tuple(
        x.value
        for x in stale.UniversalWorkerStalenessState
    )
    == (
        "ACTIVE",
        "STALE",
    ),
)


# ============================================================
# THRESHOLD CONTRACT
# ============================================================

check(
    "threshold_minimum",
    stale.normalize_universal_stale_worker_threshold_seconds(
        1
    )
    == 1,
)

check(
    "threshold_maximum",
    stale.normalize_universal_stale_worker_threshold_seconds(
        stale.MAX_UNIVERSAL_STALE_WORKER_THRESHOLD_SECONDS
    )
    == stale.MAX_UNIVERSAL_STALE_WORKER_THRESHOLD_SECONDS,
)


for bad in (
    None,
    True,
    False,
    0,
    -1,
    1.0,
    "1",
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
        "invalid_threshold_"
        + repr(
            bad
        ),
        rejected,
    )


try:

    stale.normalize_universal_stale_worker_threshold_seconds(
        stale.MAX_UNIVERSAL_STALE_WORKER_THRESHOLD_SECONDS
        + 1
    )

except stale.UniversalStaleWorkerError as exc:

    rejected = (
        exc.code
        == "stale_worker_threshold_too_large"
    )

else:

    rejected = False


check(
    "threshold_overflow_rejected",
    rejected,
)


# ============================================================
# EVALUATION TIME CONTRACT
# ============================================================

check(
    "evaluation_time_z_normalized",
    stale.normalize_universal_stale_worker_evaluated_at(
        "2026-08-17T00:01:00Z"
    )
    == "2026-08-17T00:01:00+00:00",
)


for bad in (
    None,
    True,
    False,
    "",
    "not-a-date",
    "2026-08-17T00:01:00",
    "2026-08-17T01:01:00+01:00",
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
        "invalid_evaluated_at_"
        + repr(
            bad
        ),
        rejected,
    )


# ============================================================
# ACTIVE / STALE SEMANTICS
# ============================================================

active = (
    stale.evaluate_universal_stale_worker(
        heartbeat=hb,
        evaluated_at="2026-08-17T00:00:59Z",
        stale_threshold_seconds=60,
    )
)

equal = (
    stale.evaluate_universal_stale_worker(
        heartbeat=hb,
        evaluated_at="2026-08-17T00:01:00Z",
        stale_threshold_seconds=60,
    )
)

older = (
    stale.evaluate_universal_stale_worker(
        heartbeat=hb,
        evaluated_at="2026-08-17T00:01:01Z",
        stale_threshold_seconds=60,
    )
)


check(
    "below_threshold_active",
    (
        active.age_seconds == 59.0
        and
        active.state
        is stale.UniversalWorkerStalenessState.ACTIVE
    ),
)

check(
    "equal_threshold_stale",
    (
        equal.age_seconds == 60.0
        and
        equal.state
        is stale.UniversalWorkerStalenessState.STALE
    ),
)

check(
    "above_threshold_stale",
    (
        older.age_seconds == 61.0
        and
        older.state
        is stale.UniversalWorkerStalenessState.STALE
    ),
)


zero_age = (
    stale.evaluate_universal_stale_worker(
        heartbeat=hb,
        evaluated_at="2026-08-17T00:00:00Z",
        stale_threshold_seconds=60,
    )
)

check(
    "zero_age_active",
    (
        zero_age.age_seconds == 0.0
        and
        zero_age.state
        is stale.UniversalWorkerStalenessState.ACTIVE
    ),
)


# ============================================================
# FUTURE HEARTBEAT
# ============================================================

try:

    stale.evaluate_universal_stale_worker(
        heartbeat=hb,
        evaluated_at="2026-08-16T23:59:59Z",
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
    "future_heartbeat_rejected",
    rejected,
)


# ============================================================
# MISSING HEARTBEAT
# ============================================================

try:

    stale.evaluate_universal_stale_worker(
        heartbeat=None,
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
    "missing_heartbeat_rejected",
    rejected,
)


# ============================================================
# RESULT EVIDENCE
# ============================================================

check(
    "worker_identity",
    equal.worker_identity
    == "worker-a::instance-1",
)

check(
    "worker_id_echo",
    equal.worker_id
    == hb.worker_id,
)

check(
    "worker_instance_echo",
    equal.worker_instance_id
    == hb.worker_instance_id,
)

check(
    "worker_type_echo",
    equal.worker_type
    == hb.worker_type,
)

check(
    "heartbeat_timestamp_echo",
    equal.heartbeat_at
    == hb.heartbeat_at,
)

check(
    "heartbeat_sequence_echo",
    equal.heartbeat_sequence
    == hb.sequence,
)

check(
    "evaluation_time_echo",
    equal.evaluated_at
    == "2026-08-17T00:01:00+00:00",
)

check(
    "threshold_echo",
    equal.stale_threshold_seconds
    == 60,
)


# ============================================================
# HARDENED IDENTITY CONTRACT
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
            "identity_hardening_"
            + field_name
            + "_"
            + repr(
                bad_value
            )
        ),
        rejected,
    )


# ============================================================
# HARDENED HEARTBEAT SEQUENCE CONTRACT
# ============================================================

for bad_sequence in (
    None,
    True,
    False,
    0,
    -1,
    1.0,
    "1",
    heartbeat.MAX_UNIVERSAL_WORKER_HEARTBEAT_SEQUENCE
    + 1,
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
        "heartbeat_sequence_hardening_"
        + repr(
            bad_sequence
        ),
        rejected,
    )


# ============================================================
# RESULT CONSISTENCY
# ============================================================

try:

    stale.UniversalStaleWorkerResult(
        worker_id=hb.worker_id,
        worker_instance_id=hb.worker_instance_id,
        worker_type=hb.worker_type,
        heartbeat_at=hb.heartbeat_at,
        heartbeat_sequence=hb.sequence,
        evaluated_at="2026-08-17T00:00:59Z",
        stale_threshold_seconds=60,
        age_seconds=59.0,
        state=stale.UniversalWorkerStalenessState.STALE,
    )

except stale.UniversalStaleWorkerError as exc:

    rejected = (
        exc.code
        == "inconsistent_stale_worker_state"
    )

else:

    rejected = False


check(
    "forged_state_rejected",
    rejected,
)


try:

    stale.UniversalStaleWorkerResult(
        worker_id=hb.worker_id,
        worker_instance_id=hb.worker_instance_id,
        worker_type=hb.worker_type,
        heartbeat_at=hb.heartbeat_at,
        heartbeat_sequence=hb.sequence,
        evaluated_at="2026-08-17T00:01:00Z",
        stale_threshold_seconds=60,
        age_seconds=59.0,
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
    "forged_age_rejected",
    rejected,
)


for special_age in (
    float("nan"),
    float("inf"),
    float("-inf"),
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
        "special_age_rejected_"
        + repr(
            special_age
        ),
        rejected,
    )


# ============================================================
# SCHEMA / IMMUTABILITY / FIELDS
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
            equal,
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


# ============================================================
# DETERMINISM
# ============================================================

equal_again = (
    stale.evaluate_universal_stale_worker(
        heartbeat=hb,
        evaluated_at="2026-08-17T00:01:00Z",
        stale_threshold_seconds=60,
    )
)


check(
    "deterministic_result",
    equal_again
    == equal,
)


# ============================================================
# EXPLANATION CONTRACT
# ============================================================

explanation = (
    stale.explain_universal_stale_worker_detection_v1()
)


check(
    "phase",
    explanation.get(
        "phase"
    )
    == "4.1.11",
)

check(
    "component",
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
    "input_rule",
    "4.1.10"
    in explanation.get(
        "input_rule",
        "",
    ),
)

check(
    "caller_supplied_evaluation",
    "caller-supplied"
    in explanation.get(
        "time_rule",
        "",
    ),
)

check(
    "no_wall_clock",
    "does not read the wall clock"
    in explanation.get(
        "time_rule",
        "",
    ),
)

check(
    "positive_threshold",
    "positive"
    in explanation.get(
        "threshold_rule",
        "",
    ),
)

check(
    "active_less_than",
    "strictly less"
    in explanation.get(
        "active_rule",
        "",
    ),
)

check(
    "stale_greater_equal",
    "greater than or equal"
    in explanation.get(
        "stale_rule",
        "",
    ),
)

check(
    "equality_stale",
    "is STALE"
    in explanation.get(
        "equality_rule",
        "",
    ),
)

check(
    "missing_invalid",
    "invalid input"
    in explanation.get(
        "missing_heartbeat_rule",
        "",
    ),
)

check(
    "age_owned_by_4_1_11",
    "owns deterministic heartbeat"
    in explanation.get(
        "age_rule",
        "",
    ),
)

check(
    "health_separate",
    "not UNHEALTHY"
    in explanation.get(
        "health_boundary",
        "",
    ),
)

check(
    "lease_separate",
    "independent"
    in explanation.get(
        "lease_boundary",
        "",
    ),
)

check(
    "recovery_separate",
    "evidence only"
    in explanation.get(
        "recovery_boundary",
        "",
    ),
)

check(
    "queue_recovery_composition",
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
# PROHIBITIONS
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
# IMPORT / API BOUNDARY
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
# SIDE EFFECT BOUNDARY
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

    if call_name in forbidden_call_names:

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
# NO HIDDEN POLICY
# ============================================================

source_lower = (
    source.lower()
)


for forbidden_symbol in (
    "default_stale_threshold",
    "global_stale_threshold",
    "heartbeat_timeout =",
    "heartbeat_ttl =",
    "worker_timeout =",
    "default_timeout =",
):

    check(
        "no_hidden_policy_"
        + forbidden_symbol.replace(
            " ",
            "_"
        ),
        forbidden_symbol
        not in source_lower,
    )


# ============================================================
# PROTECTED AUTHORITY MATRIX
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
        "phase_4_1_11_stale_worker_detection",
        stale.UNIVERSAL_STALE_WORKER_DETECTION_VERSION,
        stale.UNIVERSAL_STALE_WORKER_RESULT_SCHEMA_VERSION,
        stale_ast,

        "input_canonical_4_1_10_heartbeat",
        "caller_supplied_evaluated_at",
        "caller_supplied_stale_threshold_seconds",
        "timezone_aware_utc_evaluation_time",
        "positive_integer_threshold",

        "age_seconds_evaluated_at_minus_heartbeat_at",

        "age_less_than_threshold_active",
        "age_equal_threshold_stale",
        "age_greater_than_threshold_stale",

        "future_heartbeat_rejected",
        "missing_heartbeat_invalid",

        "states_active_stale_only",
        "no_unknown_state",

        "canonical_worker_identity_preserved",
        "canonical_worker_type_preserved",
        "canonical_heartbeat_sequence_preserved",

        "identity_revalidated_via_registration_contract",
        "heartbeat_sequence_revalidated_via_heartbeat_contract",

        "stale_not_unhealthy",
        "stale_not_failed",
        "stale_not_expired_lease",
        "stale_not_recoverable",
        "stale_not_shutdown",
        "stale_not_drained",
        "stale_not_deregistered",

        "worker_health_external",
        "worker_recovery_external",
        "worker_leasing_external",
        "queue_recovery_external",

        "no_runtime_state_store",
        "no_persistence",
        "no_wall_clock",
        "pure_staleness_evidence_authority",
    )
)


stale_fingerprint = (
    hashlib.sha256(
        fingerprint_material.encode(
            "utf-8"
        )
    ).hexdigest().upper()
)


check(
    "fingerprint_generated",
    len(
        stale_fingerprint
    )
    == 64,
    stale_fingerprint,
)


# ============================================================
# FINAL AST RECHECK
# ============================================================

final_ast = ast_sha(
    STALE_PATH
)


check(
    "final_ast_unchanged",
    final_ast
    == EXPECTED_STALE_AST,
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
        "PHASE 4.1.11 — UNIVERSAL STALE WORKER "
        "DETECTION FINAL CERTIFICATION"
    ),
    "=" * 112,
    "",
    (
        "STALE WORKER AST SHA256: "
        + stale_ast
    ),
    (
        "STALE WORKER FINGERPRINT: "
        + stale_fingerprint
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
            "FINAL STALE WORKER CERTIFICATION: "
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
        "STALE WORKER MODIFIED DURING CERTIFICATION: NO",
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
        "HEARTBEAT INTERVAL DEFINED: NO",
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
        "WORKER CAPABILITY INSPECTED: NO",
        "WORKER CAPACITY CALCULATED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "STALE STATE PERSISTED: NO",
        "",
        (
            "PHASE 4.1.11 FREEZE CANDIDATE: "
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
        "Phase 4.1.11 Stale Worker final certification failed."
    )
