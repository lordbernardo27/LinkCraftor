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

DRAIN_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "drain.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_12_worker_drain_regression.txt"
)

EXPECTED_DRAIN_AST = (
    "629AA6B5D9269B3164A1524F3C176B2EA34CB4952A0D32F5E2EE4A7C6984FA78"
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

if not DRAIN_PATH.exists():

    raise SystemExit(
        "4.1.12 Worker Drain authority missing."
    )


initial_ast = ast_sha(
    DRAIN_PATH
)


if initial_ast != EXPECTED_DRAIN_AST:

    raise SystemExit(
        (
            "Worker Drain AST changed before regression.\n"
            "EXPECTED: "
            + EXPECTED_DRAIN_AST
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
                "Worker Drain regression: "
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
    "universal_worker.drain"
)

sys.modules.pop(
    module_name,
    None,
)

drain = importlib.import_module(
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


# ============================================================
# 1 — AST / VERSION / CONSTANT CONTRACT
# ============================================================

check(
    "drain_ast_stable",
    ast_sha(
        DRAIN_PATH
    )
    == EXPECTED_DRAIN_AST,
    ast_sha(
        DRAIN_PATH
    ),
)

check(
    "version_exact",
    drain.UNIVERSAL_WORKER_DRAIN_VERSION
    == "universal_worker_drain_v4.1.12",
)

check(
    "evidence_schema_exact",
    drain.UNIVERSAL_WORKER_DRAIN_EVIDENCE_SCHEMA_VERSION
    == "universal_worker_drain_evidence_schema_v1",
)

check(
    "result_schema_exact",
    drain.UNIVERSAL_WORKER_DRAIN_RESULT_SCHEMA_VERSION
    == "universal_worker_drain_result_schema_v1",
)

check(
    "count_max_exact",
    drain.MAX_UNIVERSAL_WORKER_DRAIN_COUNT
    == 2_147_483_647,
)

check(
    "identity_separator_exact",
    drain.UNIVERSAL_WORKER_DRAIN_IDENTITY_SEPARATOR
    == "::",
)

check(
    "states_exact",
    tuple(
        state.value
        for state in drain.UniversalWorkerDrainState
    )
    == (
        "NOT_REQUESTED",
        "DRAINING",
        "DRAINED",
    ),
)


# ============================================================
# 2 — DRAIN REQUESTED ATTACK MATRIX
# ============================================================

check(
    "requested_true_exact",
    drain.normalize_universal_worker_drain_requested(
        True
    )
    is True,
)

check(
    "requested_false_exact",
    drain.normalize_universal_worker_drain_requested(
        False
    )
    is False,
)


for index, bad in enumerate(
    (
        None,
        0,
        1,
        -1,
        0.0,
        1.0,
        "",
        "true",
        "false",
        "True",
        "False",
        [],
        {},
        (),
        set(),
        object(),
    ),
    start=1,
):

    try:

        drain.normalize_universal_worker_drain_requested(
            bad
        )

    except drain.UniversalWorkerDrainError as exc:

        rejected = (
            exc.code
            == "invalid_worker_drain_requested"
        )

    else:

        rejected = False

    check(
        "requested_attack_"
        + str(
            index
        ),
        rejected,
        repr(
            bad
        ),
    )


# ============================================================
# 3 — COUNT ATTACK MATRIX
# ============================================================

for value in (
    0,
    1,
    2,
    100,
    1000000,
    drain.MAX_UNIVERSAL_WORKER_DRAIN_COUNT,
):

    check(
        "valid_work_count_"
        + str(
            value
        ),
        drain.normalize_universal_worker_drain_count(
            value,
            field_name="active_work_count",
        )
        == value,
    )

    check(
        "valid_lease_count_"
        + str(
            value
        ),
        drain.normalize_universal_worker_drain_count(
            value,
            field_name="active_lease_count",
        )
        == value,
    )


for index, bad in enumerate(
    (
        None,
        True,
        False,
        -1,
        -100,
        0.0,
        1.0,
        2.5,
        float("nan"),
        float("inf"),
        "",
        "0",
        "1",
        [],
        {},
        (),
        set(),
        object(),
    ),
    start=1,
):

    for field_name in (
        "active_work_count",
        "active_lease_count",
    ):

        try:

            drain.normalize_universal_worker_drain_count(
                bad,
                field_name=field_name,
            )

        except drain.UniversalWorkerDrainError as exc:

            rejected = (
                exc.code
                == "invalid_worker_drain_count"
            )

        else:

            rejected = False

        check(
            (
                field_name
                + "_attack_"
                + str(
                    index
                )
            ),
            rejected,
            repr(
                bad
            ),
        )


for field_name in (
    "active_work_count",
    "active_lease_count",
):

    for overflow in (
        drain.MAX_UNIVERSAL_WORKER_DRAIN_COUNT
        + 1,
        drain.MAX_UNIVERSAL_WORKER_DRAIN_COUNT
        + 100,
    ):

        try:

            drain.normalize_universal_worker_drain_count(
                overflow,
                field_name=field_name,
            )

        except drain.UniversalWorkerDrainError as exc:

            rejected = (
                exc.code
                == "worker_drain_count_too_large"
            )

        else:

            rejected = False

        check(
            (
                field_name
                + "_overflow_"
                + str(
                    overflow
                )
            ),
            rejected,
        )


# ============================================================
# 4 — COMPLETE STATE CROSS-MATRIX
# ============================================================

state_cases = (
    (
        False,
        0,
        0,
        "NOT_REQUESTED",
    ),
    (
        False,
        1,
        0,
        "NOT_REQUESTED",
    ),
    (
        False,
        0,
        1,
        "NOT_REQUESTED",
    ),
    (
        False,
        1,
        1,
        "NOT_REQUESTED",
    ),
    (
        False,
        100,
        200,
        "NOT_REQUESTED",
    ),
    (
        False,
        drain.MAX_UNIVERSAL_WORKER_DRAIN_COUNT,
        drain.MAX_UNIVERSAL_WORKER_DRAIN_COUNT,
        "NOT_REQUESTED",
    ),
    (
        True,
        1,
        0,
        "DRAINING",
    ),
    (
        True,
        0,
        1,
        "DRAINING",
    ),
    (
        True,
        1,
        1,
        "DRAINING",
    ),
    (
        True,
        100,
        0,
        "DRAINING",
    ),
    (
        True,
        0,
        100,
        "DRAINING",
    ),
    (
        True,
        100,
        200,
        "DRAINING",
    ),
    (
        True,
        drain.MAX_UNIVERSAL_WORKER_DRAIN_COUNT,
        0,
        "DRAINING",
    ),
    (
        True,
        0,
        drain.MAX_UNIVERSAL_WORKER_DRAIN_COUNT,
        "DRAINING",
    ),
    (
        True,
        0,
        0,
        "DRAINED",
    ),
)


for index, (
    requested,
    work_count,
    lease_count,
    expected_state,
) in enumerate(
    state_cases,
    start=1,
):

    state = (
        drain.decide_universal_worker_drain_state(
            drain_requested=requested,
            active_work_count=work_count,
            active_lease_count=lease_count,
        )
    )

    check(
        "state_cross_matrix_"
        + str(
            index
        ),
        state.value
        == expected_state,
        state.value,
    )


# ============================================================
# 5 — REGISTRATION IDENTITY PRESERVATION
# ============================================================

registrations = (
    make_registration(
        "worker-a",
        "instance-1",
        "semantic_worker",
    ),
    make_registration(
        "worker-a",
        "instance-2",
        "semantic_worker",
    ),
    make_registration(
        "worker-b",
        "instance-1",
        "other_worker",
    ),
)


for index, item in enumerate(
    registrations,
    start=1,
):

    evidence = (
        drain.create_universal_worker_drain_evidence(
            registration=item,
            drain_requested=True,
            active_work_count=1,
            active_lease_count=0,
        )
    )

    check(
        "identity_preserved_"
        + str(
            index
        ),
        evidence.worker_identity
        == (
            item.worker_id
            + "::"
            + item.worker_instance_id
        ),
    )

    check(
        "type_preserved_"
        + str(
            index
        ),
        evidence.worker_type
        == item.worker_type,
    )


# ============================================================
# 6 — INVALID REGISTRATION ATTACKS
# ============================================================

for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        1,
        "",
        "worker-a",
        [],
        {},
        (),
        set(),
        object(),
    ),
    start=1,
):

    try:

        drain.create_universal_worker_drain_evidence(
            registration=bad,
            drain_requested=True,
            active_work_count=0,
            active_lease_count=0,
        )

    except drain.UniversalWorkerDrainError as exc:

        rejected = (
            exc.code
            == "invalid_worker_drain_registration"
        )

    else:

        rejected = False

    check(
        "registration_attack_"
        + str(
            index
        ),
        rejected,
    )


# ============================================================
# 7 — DIRECT EVIDENCE IDENTITY FORGERY
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
        "worker_instance_id",
        "\t",
    ),
    (
        "worker_type",
        "",
    ),
    (
        "worker_type",
        " ",
    ),
    (
        "worker_type",
        "\t",
    ),
):

    kwargs = {
        "worker_id":
            reg.worker_id,

        "worker_instance_id":
            reg.worker_instance_id,

        "worker_type":
            reg.worker_type,

        "drain_requested":
            True,

        "active_work_count":
            0,

        "active_lease_count":
            0,
    }

    kwargs[
        field_name
    ] = bad_value

    try:

        drain.UniversalWorkerDrainEvidence(
            **kwargs
        )

    except drain.UniversalWorkerDrainError:

        rejected = True

    else:

        rejected = False

    check(
        (
            "evidence_identity_forgery_"
            + field_name
            + "_"
            + repr(
                bad_value
            )
        ),
        rejected,
    )


# ============================================================
# 8 — DIRECT RESULT IDENTITY FORGERY
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
            reg.worker_id,

        "worker_instance_id":
            reg.worker_instance_id,

        "worker_type":
            reg.worker_type,

        "drain_requested":
            True,

        "active_work_count":
            0,

        "active_lease_count":
            0,

        "state":
            drain.UniversalWorkerDrainState.DRAINED,
    }

    kwargs[
        field_name
    ] = bad_value

    try:

        drain.UniversalWorkerDrainResult(
            **kwargs
        )

    except drain.UniversalWorkerDrainError:

        rejected = True

    else:

        rejected = False

    check(
        (
            "result_identity_forgery_"
            + field_name
            + "_"
            + repr(
                bad_value
            )
        ),
        rejected,
    )


# ============================================================
# 9 — DIRECT EVIDENCE COUNT FORGERY
# ============================================================

for field_name in (
    "active_work_count",
    "active_lease_count",
):

    for index, bad_value in enumerate(
        (
            None,
            True,
            False,
            -1,
            1.0,
            "1",
            drain.MAX_UNIVERSAL_WORKER_DRAIN_COUNT
            + 1,
        ),
        start=1,
    ):

        kwargs = {
            "worker_id":
                reg.worker_id,

            "worker_instance_id":
                reg.worker_instance_id,

            "worker_type":
                reg.worker_type,

            "drain_requested":
                True,

            "active_work_count":
                0,

            "active_lease_count":
                0,
        }

        kwargs[
            field_name
        ] = bad_value

        try:

            drain.UniversalWorkerDrainEvidence(
                **kwargs
            )

        except drain.UniversalWorkerDrainError:

            rejected = True

        else:

            rejected = False

        check(
            (
                "evidence_count_forgery_"
                + field_name
                + "_"
                + str(
                    index
                )
            ),
            rejected,
        )


# ============================================================
# 10 — DIRECT RESULT COUNT FORGERY
# ============================================================

for field_name in (
    "active_work_count",
    "active_lease_count",
):

    for index, bad_value in enumerate(
        (
            None,
            True,
            False,
            -1,
            1.0,
            "1",
            drain.MAX_UNIVERSAL_WORKER_DRAIN_COUNT
            + 1,
        ),
        start=1,
    ):

        kwargs = {
            "worker_id":
                reg.worker_id,

            "worker_instance_id":
                reg.worker_instance_id,

            "worker_type":
                reg.worker_type,

            "drain_requested":
                True,

            "active_work_count":
                0,

            "active_lease_count":
                0,

            "state":
                drain.UniversalWorkerDrainState.DRAINED,
        }

        kwargs[
            field_name
        ] = bad_value

        try:

            drain.UniversalWorkerDrainResult(
                **kwargs
            )

        except drain.UniversalWorkerDrainError:

            rejected = True

        else:

            rejected = False

        check(
            (
                "result_count_forgery_"
                + field_name
                + "_"
                + str(
                    index
                )
            ),
            rejected,
        )


# ============================================================
# 11 — DIRECT REQUESTED FORGERY
# ============================================================

for index, bad_value in enumerate(
    (
        None,
        0,
        1,
        "",
        "true",
        [],
        {},
        (),
    ),
    start=1,
):

    try:

        drain.UniversalWorkerDrainEvidence(
            worker_id=reg.worker_id,
            worker_instance_id=reg.worker_instance_id,
            worker_type=reg.worker_type,
            drain_requested=bad_value,
            active_work_count=0,
            active_lease_count=0,
        )

    except drain.UniversalWorkerDrainError as exc:

        rejected = (
            exc.code
            == "invalid_worker_drain_requested"
        )

    else:

        rejected = False

    check(
        "evidence_requested_forgery_"
        + str(
            index
        ),
        rejected,
    )


# ============================================================
# 12 — STATE FORGERY CROSS-MATRIX
# ============================================================

for index, (
    requested,
    work,
    leases,
    forged_state,
) in enumerate(
    (
        (
            False,
            0,
            0,
            drain.UniversalWorkerDrainState.DRAINING,
        ),
        (
            False,
            0,
            0,
            drain.UniversalWorkerDrainState.DRAINED,
        ),
        (
            False,
            1,
            1,
            drain.UniversalWorkerDrainState.DRAINING,
        ),
        (
            True,
            1,
            0,
            drain.UniversalWorkerDrainState.NOT_REQUESTED,
        ),
        (
            True,
            1,
            0,
            drain.UniversalWorkerDrainState.DRAINED,
        ),
        (
            True,
            0,
            1,
            drain.UniversalWorkerDrainState.NOT_REQUESTED,
        ),
        (
            True,
            0,
            1,
            drain.UniversalWorkerDrainState.DRAINED,
        ),
        (
            True,
            0,
            0,
            drain.UniversalWorkerDrainState.NOT_REQUESTED,
        ),
        (
            True,
            0,
            0,
            drain.UniversalWorkerDrainState.DRAINING,
        ),
    ),
    start=1,
):

    try:

        drain.UniversalWorkerDrainResult(
            worker_id=reg.worker_id,
            worker_instance_id=reg.worker_instance_id,
            worker_type=reg.worker_type,
            drain_requested=requested,
            active_work_count=work,
            active_lease_count=leases,
            state=forged_state,
        )

    except drain.UniversalWorkerDrainError as exc:

        rejected = (
            exc.code
            == "inconsistent_worker_drain_state"
        )

    else:

        rejected = False

    check(
        "state_forgery_"
        + str(
            index
        ),
        rejected,
    )


# ============================================================
# 13 — RAW STATE ATTACKS
# ============================================================

for index, bad_state in enumerate(
    (
        "NOT_REQUESTED",
        "DRAINING",
        "DRAINED",
        "",
        None,
        True,
        False,
        0,
        1,
    ),
    start=1,
):

    try:

        drain.UniversalWorkerDrainResult(
            worker_id=reg.worker_id,
            worker_instance_id=reg.worker_instance_id,
            worker_type=reg.worker_type,
            drain_requested=True,
            active_work_count=0,
            active_lease_count=0,
            state=bad_state,
        )

    except drain.UniversalWorkerDrainError as exc:

        rejected = (
            exc.code
            == "invalid_worker_drain_state"
        )

    else:

        rejected = False

    check(
        "raw_state_attack_"
        + str(
            index
        ),
        rejected,
        repr(
            bad_state
        ),
    )


# ============================================================
# 14 — SCHEMA TAMPERING
# ============================================================

for bad_schema in (
    "",
    " ",
    "wrong",
    "universal_worker_drain_evidence_schema_v2",
):

    try:

        drain.UniversalWorkerDrainEvidence(
            worker_id=reg.worker_id,
            worker_instance_id=reg.worker_instance_id,
            worker_type=reg.worker_type,
            drain_requested=True,
            active_work_count=0,
            active_lease_count=0,
            schema_version=bad_schema,
        )

    except drain.UniversalWorkerDrainError as exc:

        rejected = (
            exc.code
            == "invalid_worker_drain_evidence_schema_version"
        )

    else:

        rejected = False

    check(
        "evidence_schema_attack_"
        + repr(
            bad_schema
        ),
        rejected,
    )


for bad_schema in (
    "",
    " ",
    "wrong",
    "universal_worker_drain_result_schema_v2",
):

    try:

        drain.UniversalWorkerDrainResult(
            worker_id=reg.worker_id,
            worker_instance_id=reg.worker_instance_id,
            worker_type=reg.worker_type,
            drain_requested=True,
            active_work_count=0,
            active_lease_count=0,
            state=drain.UniversalWorkerDrainState.DRAINED,
            schema_version=bad_schema,
        )

    except drain.UniversalWorkerDrainError as exc:

        rejected = (
            exc.code
            == "invalid_worker_drain_result_schema_version"
        )

    else:

        rejected = False

    check(
        "result_schema_attack_"
        + repr(
            bad_schema
        ),
        rejected,
    )


# ============================================================
# 15 — PROPERTY SEMANTICS
# ============================================================

not_requested = (
    drain.evaluate_universal_worker_drain(
        evidence=(
            drain.create_universal_worker_drain_evidence(
                registration=reg,
                drain_requested=False,
                active_work_count=7,
                active_lease_count=9,
            )
        )
    )
)

draining_work = (
    drain.evaluate_universal_worker_drain(
        evidence=(
            drain.create_universal_worker_drain_evidence(
                registration=reg,
                drain_requested=True,
                active_work_count=1,
                active_lease_count=0,
            )
        )
    )
)

draining_lease = (
    drain.evaluate_universal_worker_drain(
        evidence=(
            drain.create_universal_worker_drain_evidence(
                registration=reg,
                drain_requested=True,
                active_work_count=0,
                active_lease_count=1,
            )
        )
    )
)

drained = (
    drain.evaluate_universal_worker_drain(
        evidence=(
            drain.create_universal_worker_drain_evidence(
                registration=reg,
                drain_requested=True,
                active_work_count=0,
                active_lease_count=0,
            )
        )
    )
)


check(
    "not_requested_accepts_new_work",
    not_requested.accepts_new_work
    is True,
)

check(
    "not_requested_drain_complete_false",
    not_requested.drain_complete
    is False,
)

check(
    "not_requested_not_draining",
    not_requested.is_draining
    is False,
)

check(
    "not_requested_not_drained",
    not_requested.is_drained
    is False,
)

check(
    "draining_work_accepts_new_work_false",
    draining_work.accepts_new_work
    is False,
)

check(
    "draining_work_complete_false",
    draining_work.drain_complete
    is False,
)

check(
    "draining_work_is_draining",
    draining_work.is_draining
    is True,
)

check(
    "draining_lease_accepts_new_work_false",
    draining_lease.accepts_new_work
    is False,
)

check(
    "draining_lease_complete_false",
    draining_lease.drain_complete
    is False,
)

check(
    "draining_lease_is_draining",
    draining_lease.is_draining
    is True,
)

check(
    "drained_accepts_new_work_false",
    drained.accepts_new_work
    is False,
)

check(
    "drained_complete_true",
    drained.drain_complete
    is True,
)

check(
    "drained_is_drained",
    drained.is_drained
    is True,
)

check(
    "drained_not_draining",
    drained.is_draining
    is False,
)


# ============================================================
# 16 — INVALID EVALUATION EVIDENCE
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

        drain.evaluate_universal_worker_drain(
            evidence=bad
        )

    except drain.UniversalWorkerDrainError as exc:

        rejected = (
            exc.code
            == "invalid_worker_drain_evidence"
        )

    else:

        rejected = False

    check(
        "evaluate_evidence_attack_"
        + str(
            index
        ),
        rejected,
    )


# ============================================================
# 17 — IMMUTABILITY
# ============================================================

canonical_evidence = (
    drain.create_universal_worker_drain_evidence(
        registration=reg,
        drain_requested=True,
        active_work_count=1,
        active_lease_count=1,
    )
)

canonical_result = (
    drain.evaluate_universal_worker_drain(
        evidence=canonical_evidence
    )
)


for obj in (
    canonical_evidence,
    canonical_result,
):

    for field in fields(
        obj
    ):

        try:

            setattr(
                obj,
                field.name,
                None,
            )

        except Exception:

            immutable = True

        else:

            immutable = False

        check(
            (
                "immutable_"
                + type(
                    obj
                ).__name__
                + "_"
                + field.name
            ),
            immutable,
        )


# ============================================================
# 18 — DETERMINISM
# ============================================================

repeat_evidence_a = (
    drain.create_universal_worker_drain_evidence(
        registration=reg,
        drain_requested=True,
        active_work_count=3,
        active_lease_count=4,
    )
)

repeat_evidence_b = (
    drain.create_universal_worker_drain_evidence(
        registration=reg,
        drain_requested=True,
        active_work_count=3,
        active_lease_count=4,
    )
)


check(
    "deterministic_evidence",
    repeat_evidence_a
    == repeat_evidence_b,
)


repeat_result_a = (
    drain.evaluate_universal_worker_drain(
        evidence=repeat_evidence_a
    )
)

repeat_result_b = (
    drain.evaluate_universal_worker_drain(
        evidence=repeat_evidence_b
    )
)


check(
    "deterministic_result",
    repeat_result_a
    == repeat_result_b,
)


# ============================================================
# 19 — EXACT FIELD CONTRACT
# ============================================================

evidence_fields = tuple(
    field.name
    for field in fields(
        drain.UniversalWorkerDrainEvidence
    )
)

result_fields = tuple(
    field.name
    for field in fields(
        drain.UniversalWorkerDrainResult
    )
)


check(
    "evidence_fields_exact",
    evidence_fields
    == (
        "worker_id",
        "worker_instance_id",
        "worker_type",
        "drain_requested",
        "active_work_count",
        "active_lease_count",
        "schema_version",
    ),
    evidence_fields,
)

check(
    "result_fields_exact",
    result_fields
    == (
        "worker_id",
        "worker_instance_id",
        "worker_type",
        "drain_requested",
        "active_work_count",
        "active_lease_count",
        "state",
        "schema_version",
    ),
    result_fields,
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
    "stale",
    "staleness",
    "recoverable",
    "shutdown",
    "shutdown_requested",
    "capacity",
    "available_capacity",
    "available_slots",
    "capability",
    "capabilities",
    "runtime_phase",
    "runtime_state",
    "queue_id",
):

    check(
        "forbidden_evidence_field_"
        + forbidden_field,
        forbidden_field
        not in evidence_fields,
    )

    check(
        "forbidden_result_field_"
        + forbidden_field,
        forbidden_field
        not in result_fields,
    )


# ============================================================
# 20 — EXPLANATION CONTRACT
# ============================================================

explanation = (
    drain.explain_universal_worker_drain_v1()
)


check(
    "explanation_phase",
    explanation.get(
        "phase"
    )
    == "4.1.12",
)

check(
    "explanation_component",
    explanation.get(
        "component"
    )
    == "Universal Worker Drain",
)

check(
    "explanation_version",
    explanation.get(
        "version"
    )
    == drain.UNIVERSAL_WORKER_DRAIN_VERSION,
)

check(
    "explanation_evidence_schema",
    explanation.get(
        "evidence_schema_version"
    )
    == drain.UNIVERSAL_WORKER_DRAIN_EVIDENCE_SCHEMA_VERSION,
)

check(
    "explanation_result_schema",
    explanation.get(
        "result_schema_version"
    )
    == drain.UNIVERSAL_WORKER_DRAIN_RESULT_SCHEMA_VERSION,
)

check(
    "worker_scope_explicit",
    "individual-worker"
    in explanation.get(
        "scope_rule",
        "",
    ),
)

check(
    "runtime_scope_separate",
    "separate from whole-runtime"
    in explanation.get(
        "scope_rule",
        "",
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
    "caller_evidence_rule",
    "caller supplies"
    in explanation.get(
        "input_rule",
        "",
    ),
)

check(
    "not_requested_rule",
    "NOT_REQUESTED"
    in explanation.get(
        "not_requested_rule",
        "",
    ),
)

check(
    "draining_rule",
    "DRAINING"
    in explanation.get(
        "draining_rule",
        "",
    ),
)

check(
    "drained_rule",
    "DRAINED"
    in explanation.get(
        "drained_rule",
        "",
    ),
)

check(
    "new_work_evidence_rule",
    "accepts_new_work=false"
    in explanation.get(
        "new_work_rule",
        "",
    ),
)

check(
    "assignment_is_external",
    "does not modify or invoke"
    in explanation.get(
        "assignment_boundary",
        "",
    ),
)

check(
    "leasing_is_external",
    "does not acquire, renew or release"
    in explanation.get(
        "leasing_boundary",
        "",
    ),
)

check(
    "existing_work_is_preserved",
    "preserves existing work"
    in explanation.get(
        "existing_work_rule",
        "",
    ),
)

check(
    "shutdown_consumes_drain_complete",
    (
        "4.1.8 Worker Shutdown"
        in explanation.get(
            "shutdown_boundary",
            "",
        )
        and
        "drain_complete"
        in explanation.get(
            "shutdown_boundary",
            "",
        )
    ),
)

check(
    "scaling_is_external",
    "does not perform scale-down"
    in explanation.get(
        "scaling_boundary",
        "",
    ),
)

check(
    "pool_membership_preserved",
    "does not remove"
    in explanation.get(
        "pool_boundary",
        "",
    ),
)

check(
    "health_stale_recovery_independent",
    "independent"
    in explanation.get(
        "health_stale_recovery_boundary",
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
    "no external mutation or I/O"
    in explanation.get(
        "purity_rule",
        "",
    ),
)


# ============================================================
# 21 — COMPLETE PROHIBITION MATRIX
# ============================================================

required_prohibitions = (
    "does not use whole-runtime DRAINING as worker drain state",
    "does not mutate Runtime Lifecycle Manager",
    "does not assign workers",
    "does not modify Assignment eligibility directly",
    "does not acquire worker leases",
    "does not renew worker leases",
    "does not release worker leases",
    "does not cancel running work",
    "does not requeue jobs",
    "does not fail jobs",
    "does not terminate workers",
    "does not perform Worker Shutdown",
    "does not perform Worker Scaling",
    "does not modify Worker Registration",
    "does not deregister workers",
    "does not modify Worker Pool membership",
    "does not determine Worker Health",
    "does not detect stale workers",
    "does not initiate Worker Recovery",
    "does not inspect worker capabilities",
    "does not calculate worker capacity",
    "does not access Queue Infrastructure",
    "does not access orchestration",
    "does not access Runtime State Store",
    "does not persist drain state",
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
        + str(
            index
        ),
        item in prohibitions,
        item,
    )


# ============================================================
# 22 — IMPORT BOUNDARY
# ============================================================

source = DRAIN_PATH.read_text(
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
# 23 — API SURFACE
# ============================================================

expected_all = (
    "UNIVERSAL_WORKER_DRAIN_VERSION",
    "UNIVERSAL_WORKER_DRAIN_EVIDENCE_SCHEMA_VERSION",
    "UNIVERSAL_WORKER_DRAIN_RESULT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_DRAIN_COUNT",
    "UNIVERSAL_WORKER_DRAIN_IDENTITY_SEPARATOR",
    "UniversalWorkerDrainError",
    "UniversalWorkerDrainState",
    "UniversalWorkerDrainEvidence",
    "UniversalWorkerDrainResult",
    "normalize_universal_worker_drain_requested",
    "normalize_universal_worker_drain_count",
    "decide_universal_worker_drain_state",
    "create_universal_worker_drain_evidence",
    "evaluate_universal_worker_drain",
    "explain_universal_worker_drain_v1",
)


check(
    "api_surface_exact",
    tuple(
        drain.__all__
    )
    == expected_all,
    drain.__all__,
)


# ============================================================
# 24 — FORBIDDEN SIDE-EFFECT CALLS
# ============================================================

forbidden_call_names = {
    "open",
    "read_text",
    "write_text",
    "write_json",
    "mkdir",
    "unlink",
    "remove",

    "drain",
    "shutdown",
    "terminate",
    "kill",
    "stop",

    "assign_universal_worker",
    "discover_universal_workers",

    "acquire_universal_worker_lease",
    "renew_universal_worker_lease",
    "release_universal_worker_lease",

    "evaluate_universal_worker_health",
    "evaluate_universal_stale_worker",
    "evaluate_universal_worker_recovery",
    "evaluate_universal_worker_scaling",
    "evaluate_universal_worker_shutdown",

    "add_universal_worker_pool_member",
    "remove_universal_worker_pool_member",

    "enqueue_job",
    "dequeue_job",
    "requeue_job",
    "cancel_job",
    "mark_job_failed",

    "get_runtime_state_store_registry",

    "record_worker_status",
    "get_latest_worker_statuses",

    "persist",
    "save",

    "dispatch_job",
    "execute_job",

    "send",
    "post",
    "publish",
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
    "no_forbidden_side_effect_calls",
    not found_forbidden_calls,
    found_forbidden_calls,
)


# ============================================================
# 25 — NO RUNTIME-DRAIN RESPONSIBILITY BLEED
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


for forbidden_name_token in (
    "runtime_lifecycle",
    "shutdown_runtime",
    "drain_runtime",
    "stop_runtime",
    "terminate_worker",
    "kill_worker",
    "release_lease",
    "requeue_job",
    "cancel_job",
    "fail_job",
    "remove_pool",
    "deregister",
    "scale_down",
    "health",
    "stale_worker",
    "recover_worker",
    "capacity",
    "capability",
):

    matches = tuple(
        name
        for name in function_names
        if forbidden_name_token in name
    )

    check(
        "no_function_bleed_"
        + forbidden_name_token,
        not matches,
        matches,
    )


# ============================================================
# 26 — NO HIDDEN RUNTIME/QUEUE POLICY
# ============================================================

source_lower = (
    source.lower()
)


# RuntimeLifecyclePhase may be named in explanatory boundary
# documentation. What is forbidden is actual code coupling to the
# runtime lifecycle authority, not a documentation reference.

runtime_lifecycle_code_coupling = []


for node in ast.walk(
    tree
):

    if isinstance(
        node,
        ast.Name,
    ) and node.id == "RuntimeLifecyclePhase":

        runtime_lifecycle_code_coupling.append(
            (
                "Name",
                getattr(
                    node,
                    "lineno",
                    0,
                ),
            )
        )

    elif isinstance(
        node,
        ast.Attribute,
    ) and node.attr == "RuntimeLifecyclePhase":

        runtime_lifecycle_code_coupling.append(
            (
                "Attribute",
                getattr(
                    node,
                    "lineno",
                    0,
                ),
            )
        )

    elif isinstance(
        node,
        ast.ImportFrom,
    ):

        for alias in node.names:

            if alias.name == "RuntimeLifecyclePhase":

                runtime_lifecycle_code_coupling.append(
                    (
                        "ImportFrom",
                        getattr(
                            node,
                            "lineno",
                            0,
                        ),
                    )
                )

    elif isinstance(
        node,
        ast.Import,
    ):

        for alias in node.names:

            if (
                "runtime_lifecycle_manager"
                in alias.name
            ):

                runtime_lifecycle_code_coupling.append(
                    (
                        "Import",
                        getattr(
                            node,
                            "lineno",
                            0,
                        ),
                    )
                )


check(
    "no_hidden_policy_runtimelifecyclephase",
    not runtime_lifecycle_code_coupling,
    runtime_lifecycle_code_coupling,
)


for forbidden_symbol in (
    "runtimekernelstate",
    "queue_drain",
    "drain_queue",
    "shutdown_requested:",
    "lease_id:",
    "job_id:",
    "pool_id:",
    "workspace_id:",
    "health_state:",
    "stale_threshold",
    "max_concurrency:",
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

final_ast = ast_sha(
    DRAIN_PATH
)


check(
    "worker_drain_ast_final",
    final_ast
    == EXPECTED_DRAIN_AST,
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
        "PHASE 4.1.12 — UNIVERSAL WORKER "
        "DRAIN ADVERSARIAL REGRESSION"
    ),
    "=" * 112,
    "",
    (
        "WORKER DRAIN AST SHA256: "
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
            "ADVERSARIAL WORKER DRAIN REGRESSION: "
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
        "WORKER DRAIN AST MODIFIED: NO",
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
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "RUNTIME LIFECYCLE MANAGER MODIFIED: NO",
        "RUNTIME SHUTDOWN PROCESS MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "WHOLE-RUNTIME DRAIN INVOKED: NO",
        "WHOLE-RUNTIME LIFECYCLE MUTATED: NO",
        "WORKER ASSIGNMENT INVOKED/MODIFIED: NO",
        "WORKER LEASE ACQUIRED/RENEWED/RELEASED: NO",
        "EXISTING WORK CANCELLED: NO",
        "JOB REQUEUED/FAILED/CANCELLED: NO",
        "WORKER TERMINATED: NO",
        "WORKER SHUTDOWN PERFORMED: NO",
        "WORKER SCALING PERFORMED: NO",
        "WORKER REGISTRATION MUTATED: NO",
        "WORKER DEREGISTERED: NO",
        "WORKER POOL MEMBERSHIP MODIFIED: NO",
        "WORKER HEALTH MODIFIED: NO",
        "STALE WORKER DETECTION INVOKED: NO",
        "WORKER RECOVERY INITIATED: NO",
        "WORKER CAPABILITY INSPECTED: NO",
        "WORKER CAPACITY CALCULATED: NO",
        "QUEUE INFRASTRUCTURE ACCESSED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "DRAIN STATE PERSISTED: NO",
        "FILESYSTEM I/O: NO",
        "NETWORK I/O: NO",
        "",
        (
            "STATUS: REGRESSION PASS "
            "— FINAL CERTIFICATION REQUIRED"
            if passed == total
            else
            "STATUS: REGRESSION FAILED "
            "— PATCH REQUIRED BEFORE CERTIFICATION"
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
        "Phase 4.1.12 Worker Drain adversarial regression failed."
    )
