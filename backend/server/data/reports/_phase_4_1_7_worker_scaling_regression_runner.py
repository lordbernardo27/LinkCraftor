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

SCALING_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "scaling.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_7_worker_scaling_regression.txt"
)

EXPECTED_SCALING_AST = (
    "8EC818E4EF4CA7DBCADCFCB93FD99BC80AAD4CE8AEBE1CDE63CCC44FA8488FF6"
)


# ============================================================
# PROTECTED AUTHORITIES
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

if not SCALING_PATH.exists():

    raise SystemExit(
        "Worker Scaling authority does not exist."
    )


initial_ast = ast_sha(
    SCALING_PATH
)


if initial_ast != EXPECTED_SCALING_AST:

    raise SystemExit(
        (
            "Worker Scaling AST changed before regression.\n"
            "EXPECTED: "
            + EXPECTED_SCALING_AST
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

module_name = (
    "backend.server.runtime."
    "universal_worker.scaling"
)

sys.modules.pop(
    module_name,
    None,
)

scaling = importlib.import_module(
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


# ============================================================
# 1 — AST / CONSTANTS / ENUMS
# ============================================================

check(
    "scaling_ast_stable",
    ast_sha(SCALING_PATH)
    == EXPECTED_SCALING_AST,
    ast_sha(SCALING_PATH),
)

check(
    "version_exact",
    scaling.UNIVERSAL_WORKER_SCALING_VERSION
    == "universal_worker_scaling_v4.1.7",
)

check(
    "evidence_schema_exact",
    scaling.UNIVERSAL_WORKER_SCALING_EVIDENCE_SCHEMA_VERSION
    == "universal_worker_scaling_evidence_schema_v1",
)

check(
    "result_schema_exact",
    scaling.UNIVERSAL_WORKER_SCALING_RESULT_SCHEMA_VERSION
    == "universal_worker_scaling_result_schema_v1",
)

check(
    "max_worker_count_exact",
    scaling.MAX_UNIVERSAL_WORKER_COUNT
    == 1_000_000,
)

check(
    "max_work_count_exact",
    scaling.MAX_UNIVERSAL_WORKER_SCALING_WORK_COUNT
    == 2_147_483_647,
)

check(
    "decisions_exact",
    tuple(
        x.value
        for x in scaling.UniversalWorkerScalingDecision
    )
    == (
        "SCALE_UP",
        "HOLD",
        "SCALE_DOWN",
    ),
)

check(
    "reasons_exact",
    tuple(
        x.value
        for x in scaling.UniversalWorkerScalingReason
    )
    == (
        "BELOW_MINIMUM",
        "ABOVE_MAXIMUM",
        "ABOVE_MAXIMUM_BUT_SCALE_DOWN_UNSAFE",
        "DEMAND_EXCEEDS_AVAILABLE_CAPACITY",
        "MAXIMUM_REACHED",
        "ZERO_DEMAND_SCALE_DOWN_SAFE",
        "ZERO_DEMAND_SCALE_DOWN_UNSAFE",
        "MINIMUM_REACHED",
        "AVAILABLE_CAPACITY_SUFFICIENT",
    ),
)


# ============================================================
# 2 — PRECEDENCE: BELOW MINIMUM
# ============================================================

for pending_work, available_capacity, safe in (
    itertools.product(
        (0, 1, 100),
        (0, 1, 100),
        (False, True),
    )
):

    evidence = (
        scaling.create_universal_worker_scaling_evidence(
            current_worker_count=1,
            minimum_worker_count=3,
            maximum_worker_count=10,
            pending_work=pending_work,
            available_capacity=available_capacity,
            scale_down_safe=safe,
        )
    )

    result = (
        scaling.evaluate_universal_worker_scaling(
            evidence
        )
    )

    check(
        (
            "below_min_precedence_"
            + str(pending_work)
            + "_"
            + str(available_capacity)
            + "_"
            + str(safe)
        ),
        (
            result.decision
            is scaling.UniversalWorkerScalingDecision.SCALE_UP
            and
            result.reason
            is scaling.UniversalWorkerScalingReason.BELOW_MINIMUM
            and
            result.desired_worker_count
            == 3
            and
            result.delta
            == 2
        ),
    )


# ============================================================
# 3 — PRECEDENCE: ABOVE MAXIMUM
# ============================================================

for pending_work, available_capacity in (
    itertools.product(
        (0, 1, 100),
        (0, 1, 100),
    )
):

    safe = (
        scaling.create_universal_worker_scaling_evidence(
            current_worker_count=12,
            minimum_worker_count=2,
            maximum_worker_count=10,
            pending_work=pending_work,
            available_capacity=available_capacity,
            scale_down_safe=True,
        )
    )

    safe_result = (
        scaling.evaluate_universal_worker_scaling(
            safe
        )
    )

    check(
        (
            "above_max_safe_"
            + str(pending_work)
            + "_"
            + str(available_capacity)
        ),
        (
            safe_result.decision
            is scaling.UniversalWorkerScalingDecision.SCALE_DOWN
            and
            safe_result.reason
            is scaling.UniversalWorkerScalingReason.ABOVE_MAXIMUM
            and
            safe_result.desired_worker_count
            == 10
            and
            safe_result.delta
            == -2
        ),
    )

    unsafe = (
        scaling.create_universal_worker_scaling_evidence(
            current_worker_count=12,
            minimum_worker_count=2,
            maximum_worker_count=10,
            pending_work=pending_work,
            available_capacity=available_capacity,
            scale_down_safe=False,
        )
    )

    unsafe_result = (
        scaling.evaluate_universal_worker_scaling(
            unsafe
        )
    )

    check(
        (
            "above_max_unsafe_"
            + str(pending_work)
            + "_"
            + str(available_capacity)
        ),
        (
            unsafe_result.decision
            is scaling.UniversalWorkerScalingDecision.HOLD
            and
            unsafe_result.reason
            is (
                scaling.UniversalWorkerScalingReason
                .ABOVE_MAXIMUM_BUT_SCALE_DOWN_UNSAFE
            )
            and
            unsafe_result.desired_worker_count
            == 12
            and
            unsafe_result.delta
            == 0
        ),
    )


# ============================================================
# 4 — DEMAND / CAPACITY BOUNDARIES
# ============================================================

for current in (
    0,
    1,
    4,
    9,
):

    evidence = (
        scaling.create_universal_worker_scaling_evidence(
            current_worker_count=current,
            minimum_worker_count=0,
            maximum_worker_count=10,
            pending_work=11,
            available_capacity=10,
            scale_down_safe=False,
        )
    )

    result = (
        scaling.evaluate_universal_worker_scaling(
            evidence
        )
    )

    check(
        "demand_exceeds_capacity_"
        + str(current),
        (
            result.decision
            is scaling.UniversalWorkerScalingDecision.SCALE_UP
            and
            result.reason
            is (
                scaling.UniversalWorkerScalingReason
                .DEMAND_EXCEEDS_AVAILABLE_CAPACITY
            )
            and
            result.desired_worker_count
            == current + 1
            and
            result.delta
            == 1
        ),
    )


equal_capacity = (
    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=5,
        minimum_worker_count=1,
        maximum_worker_count=10,
        pending_work=10,
        available_capacity=10,
        scale_down_safe=True,
    )
)

equal_capacity_result = (
    scaling.evaluate_universal_worker_scaling(
        equal_capacity
    )
)

check(
    "pending_equal_capacity_holds",
    (
        equal_capacity_result.decision
        is scaling.UniversalWorkerScalingDecision.HOLD
        and
        equal_capacity_result.reason
        is (
            scaling.UniversalWorkerScalingReason
            .AVAILABLE_CAPACITY_SUFFICIENT
        )
        and
        equal_capacity_result.desired_worker_count
        == 5
    ),
)


maximum_demand = (
    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=10,
        minimum_worker_count=0,
        maximum_worker_count=10,
        pending_work=101,
        available_capacity=100,
        scale_down_safe=True,
    )
)

maximum_demand_result = (
    scaling.evaluate_universal_worker_scaling(
        maximum_demand
    )
)

check(
    "maximum_blocks_scale_up",
    (
        maximum_demand_result.decision
        is scaling.UniversalWorkerScalingDecision.HOLD
        and
        maximum_demand_result.reason
        is scaling.UniversalWorkerScalingReason.MAXIMUM_REACHED
        and
        maximum_demand_result.desired_worker_count
        == 10
    ),
)


zero_maximum_demand = (
    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=0,
        minimum_worker_count=0,
        maximum_worker_count=0,
        pending_work=1,
        available_capacity=0,
        scale_down_safe=False,
    )
)

zero_max_result = (
    scaling.evaluate_universal_worker_scaling(
        zero_maximum_demand
    )
)

check(
    "zero_maximum_blocks_scale_up",
    (
        zero_max_result.decision
        is scaling.UniversalWorkerScalingDecision.HOLD
        and
        zero_max_result.reason
        is scaling.UniversalWorkerScalingReason.MAXIMUM_REACHED
        and
        zero_max_result.desired_worker_count
        == 0
    ),
)


# ============================================================
# 5 — ZERO DEMAND SCALE-DOWN MATRIX
# ============================================================

for current in (
    2,
    3,
    10,
):

    evidence = (
        scaling.create_universal_worker_scaling_evidence(
            current_worker_count=current,
            minimum_worker_count=1,
            maximum_worker_count=10,
            pending_work=0,
            available_capacity=0,
            scale_down_safe=True,
        )
    )

    result = (
        scaling.evaluate_universal_worker_scaling(
            evidence
        )
    )

    check(
        "zero_demand_safe_"
        + str(current),
        (
            result.decision
            is scaling.UniversalWorkerScalingDecision.SCALE_DOWN
            and
            result.reason
            is (
                scaling.UniversalWorkerScalingReason
                .ZERO_DEMAND_SCALE_DOWN_SAFE
            )
            and
            result.desired_worker_count
            == current - 1
            and
            result.delta
            == -1
        ),
    )


for current in (
    2,
    3,
    10,
):

    evidence = (
        scaling.create_universal_worker_scaling_evidence(
            current_worker_count=current,
            minimum_worker_count=1,
            maximum_worker_count=10,
            pending_work=0,
            available_capacity=500,
            scale_down_safe=False,
        )
    )

    result = (
        scaling.evaluate_universal_worker_scaling(
            evidence
        )
    )

    check(
        "zero_demand_unsafe_"
        + str(current),
        (
            result.decision
            is scaling.UniversalWorkerScalingDecision.HOLD
            and
            result.reason
            is (
                scaling.UniversalWorkerScalingReason
                .ZERO_DEMAND_SCALE_DOWN_UNSAFE
            )
            and
            result.desired_worker_count
            == current
        ),
    )


for minimum in (
    0,
    1,
    5,
):

    evidence = (
        scaling.create_universal_worker_scaling_evidence(
            current_worker_count=minimum,
            minimum_worker_count=minimum,
            maximum_worker_count=10,
            pending_work=0,
            available_capacity=100,
            scale_down_safe=True,
        )
    )

    result = (
        scaling.evaluate_universal_worker_scaling(
            evidence
        )
    )

    check(
        "minimum_floor_"
        + str(minimum),
        (
            result.decision
            is scaling.UniversalWorkerScalingDecision.HOLD
            and
            result.reason
            is scaling.UniversalWorkerScalingReason.MINIMUM_REACHED
            and
            result.desired_worker_count
            == minimum
        ),
    )


# ============================================================
# 6 — POSITIVE DEMAND MUST NOT CAUSE SCALE-DOWN
# ============================================================

for pending_work, available_capacity in (
    (
        (1, 1),
        (1, 2),
        (1, 1000),
        (50, 50),
        (50, 1000),
    )
):

    evidence = (
        scaling.create_universal_worker_scaling_evidence(
            current_worker_count=8,
            minimum_worker_count=1,
            maximum_worker_count=10,
            pending_work=pending_work,
            available_capacity=available_capacity,
            scale_down_safe=True,
        )
    )

    result = (
        scaling.evaluate_universal_worker_scaling(
            evidence
        )
    )

    check(
        (
            "positive_demand_never_scale_down_"
            + str(pending_work)
            + "_"
            + str(available_capacity)
        ),
        (
            result.decision
            is scaling.UniversalWorkerScalingDecision.HOLD
            and
            result.reason
            is (
                scaling.UniversalWorkerScalingReason
                .AVAILABLE_CAPACITY_SUFFICIENT
            )
            and
            result.delta
            == 0
        ),
    )


# ============================================================
# 7 — STRICT INTEGER ATTACKS
# ============================================================

bad_integer_values = (
    None,
    True,
    False,
    -1,
    -100,
    0.0,
    1.0,
    "",
    "1",
    [],
    {},
    (),
    set(),
)


for field_name in (
    "current_worker_count",
    "minimum_worker_count",
    "maximum_worker_count",
    "pending_work",
    "available_capacity",
):

    for index, bad in enumerate(
        bad_integer_values,
        start=1,
    ):

        kwargs = {
            "current_worker_count": 2,
            "minimum_worker_count": 1,
            "maximum_worker_count": 5,
            "pending_work": 1,
            "available_capacity": 1,
            "scale_down_safe": True,
        }

        kwargs[
            field_name
        ] = bad

        try:

            scaling.create_universal_worker_scaling_evidence(
                **kwargs
            )

        except scaling.UniversalWorkerScalingError as exc:

            rejected = (
                exc.code
                == "invalid_worker_scaling_integer"
            )

        else:

            rejected = False

        check(
            (
                "strict_integer_"
                + field_name
                + "_"
                + str(index)
            ),
            rejected,
            repr(bad),
        )


# ============================================================
# 8 — MAXIMUM INTEGER BOUNDARIES
# ============================================================

for field_name in (
    "current_worker_count",
    "minimum_worker_count",
    "maximum_worker_count",
):

    kwargs = {
        "current_worker_count": 0,
        "minimum_worker_count": 0,
        "maximum_worker_count": (
            scaling.MAX_UNIVERSAL_WORKER_COUNT
        ),
        "pending_work": 0,
        "available_capacity": 0,
        "scale_down_safe": False,
    }

    kwargs[
        field_name
    ] = scaling.MAX_UNIVERSAL_WORKER_COUNT

    try:

        scaling.create_universal_worker_scaling_evidence(
            **kwargs
        )

    except scaling.UniversalWorkerScalingError:

        accepted = False

    else:

        accepted = True

    check(
        "worker_count_exact_max_"
        + field_name,
        accepted,
    )


for field_name in (
    "current_worker_count",
    "minimum_worker_count",
    "maximum_worker_count",
):

    kwargs = {
        "current_worker_count": 0,
        "minimum_worker_count": 0,
        "maximum_worker_count": 10,
        "pending_work": 0,
        "available_capacity": 0,
        "scale_down_safe": False,
    }

    kwargs[
        field_name
    ] = (
        scaling.MAX_UNIVERSAL_WORKER_COUNT
        + 1
    )

    try:

        scaling.create_universal_worker_scaling_evidence(
            **kwargs
        )

    except scaling.UniversalWorkerScalingError as exc:

        rejected = (
            exc.code
            == "worker_scaling_integer_too_large"
        )

    else:

        rejected = False

    check(
        "worker_count_overflow_"
        + field_name,
        rejected,
    )


for field_name in (
    "pending_work",
    "available_capacity",
):

    kwargs = {
        "current_worker_count": 1,
        "minimum_worker_count": 0,
        "maximum_worker_count": 10,
        "pending_work": 0,
        "available_capacity": 0,
        "scale_down_safe": False,
    }

    kwargs[
        field_name
    ] = (
        scaling.MAX_UNIVERSAL_WORKER_SCALING_WORK_COUNT
    )

    try:

        scaling.create_universal_worker_scaling_evidence(
            **kwargs
        )

    except scaling.UniversalWorkerScalingError:

        accepted = False

    else:

        accepted = True

    check(
        "work_exact_max_"
        + field_name,
        accepted,
    )

    kwargs[
        field_name
    ] = (
        scaling.MAX_UNIVERSAL_WORKER_SCALING_WORK_COUNT
        + 1
    )

    try:

        scaling.create_universal_worker_scaling_evidence(
            **kwargs
        )

    except scaling.UniversalWorkerScalingError as exc:

        rejected = (
            exc.code
            == "worker_scaling_integer_too_large"
        )

    else:

        rejected = False

    check(
        "work_overflow_"
        + field_name,
        rejected,
    )


# ============================================================
# 9 — MINIMUM / MAXIMUM RELATION ATTACKS
# ============================================================

for minimum, maximum in (
    (1, 0),
    (10, 9),
    (100, 1),
):

    try:

        scaling.create_universal_worker_scaling_evidence(
            current_worker_count=5,
            minimum_worker_count=minimum,
            maximum_worker_count=maximum,
            pending_work=0,
            available_capacity=0,
            scale_down_safe=True,
        )

    except scaling.UniversalWorkerScalingError as exc:

        rejected = (
            exc.code
            == "invalid_worker_scaling_bounds"
        )

    else:

        rejected = False

    check(
        (
            "invalid_bounds_"
            + str(minimum)
            + "_"
            + str(maximum)
        ),
        rejected,
    )


# ============================================================
# 10 — STRICT BOOL ATTACKS
# ============================================================

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
        [],
        {},
        (),
        set(),
    ),
    start=1,
):

    try:

        scaling.create_universal_worker_scaling_evidence(
            current_worker_count=2,
            minimum_worker_count=1,
            maximum_worker_count=5,
            pending_work=0,
            available_capacity=10,
            scale_down_safe=bad,
        )

    except scaling.UniversalWorkerScalingError as exc:

        rejected = (
            exc.code
            == "invalid_worker_scaling_boolean"
        )

    else:

        rejected = False

    check(
        "strict_scale_down_safe_"
        + str(index),
        rejected,
        repr(bad),
    )


# ============================================================
# 11 — INVALID EVIDENCE OBJECTS
# ============================================================

for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        1,
        "",
        {},
        [],
        (),
    ),
    start=1,
):

    try:

        scaling.decide_universal_worker_scaling(
            bad
        )

    except scaling.UniversalWorkerScalingError as exc:

        rejected = (
            exc.code
            == "invalid_worker_scaling_evidence"
        )

    else:

        rejected = False

    check(
        "invalid_decision_evidence_"
        + str(index),
        rejected,
        repr(bad),
    )


for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        1,
        "",
        {},
        [],
        (),
    ),
    start=1,
):

    try:

        scaling.evaluate_universal_worker_scaling(
            bad
        )

    except scaling.UniversalWorkerScalingError as exc:

        rejected = (
            exc.code
            == "invalid_worker_scaling_evidence"
        )

    else:

        rejected = False

    check(
        "invalid_evaluation_evidence_"
        + str(index),
        rejected,
        repr(bad),
    )


# ============================================================
# 12 — SCHEMA TAMPERING
# ============================================================

try:

    scaling.UniversalWorkerScalingEvidence(
        current_worker_count=2,
        minimum_worker_count=1,
        maximum_worker_count=5,
        pending_work=1,
        available_capacity=1,
        scale_down_safe=True,
        schema_version="tampered",
    )

except scaling.UniversalWorkerScalingError as exc:

    rejected = (
        exc.code
        == "invalid_worker_scaling_evidence_schema_version"
    )

else:

    rejected = False


check(
    "evidence_schema_tamper",
    rejected,
)


canonical_evidence = (
    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=4,
        minimum_worker_count=2,
        maximum_worker_count=10,
        pending_work=20,
        available_capacity=5,
        scale_down_safe=False,
    )
)

canonical_result = (
    scaling.evaluate_universal_worker_scaling(
        canonical_evidence
    )
)


try:

    scaling.UniversalWorkerScalingResult(
        decision=canonical_result.decision,
        reason=canonical_result.reason,
        current_worker_count=(
            canonical_result.current_worker_count
        ),
        desired_worker_count=(
            canonical_result.desired_worker_count
        ),
        minimum_worker_count=(
            canonical_result.minimum_worker_count
        ),
        maximum_worker_count=(
            canonical_result.maximum_worker_count
        ),
        pending_work=(
            canonical_result.pending_work
        ),
        available_capacity=(
            canonical_result.available_capacity
        ),
        scale_down_safe=(
            canonical_result.scale_down_safe
        ),
        schema_version="tampered",
    )

except scaling.UniversalWorkerScalingError as exc:

    rejected = (
        exc.code
        == "invalid_worker_scaling_result_schema_version"
    )

else:

    rejected = False


check(
    "result_schema_tamper",
    rejected,
)


# ============================================================
# 13 — RAW ENUM ATTACKS
# ============================================================

try:

    scaling.UniversalWorkerScalingResult(
        decision="SCALE_UP",
        reason=canonical_result.reason,
        current_worker_count=4,
        desired_worker_count=5,
        minimum_worker_count=2,
        maximum_worker_count=10,
        pending_work=20,
        available_capacity=5,
        scale_down_safe=False,
    )

except scaling.UniversalWorkerScalingError as exc:

    rejected = (
        exc.code
        == "invalid_worker_scaling_decision"
    )

else:

    rejected = False


check(
    "raw_decision_rejected",
    rejected,
)


try:

    scaling.UniversalWorkerScalingResult(
        decision=canonical_result.decision,
        reason="DEMAND_EXCEEDS_AVAILABLE_CAPACITY",
        current_worker_count=4,
        desired_worker_count=5,
        minimum_worker_count=2,
        maximum_worker_count=10,
        pending_work=20,
        available_capacity=5,
        scale_down_safe=False,
    )

except scaling.UniversalWorkerScalingError as exc:

    rejected = (
        exc.code
        == "invalid_worker_scaling_reason"
    )

else:

    rejected = False


check(
    "raw_reason_rejected",
    rejected,
)


# ============================================================
# 14 — RESULT FORGERY MATRIX
# ============================================================

canonical_cases = (
    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=1,
        minimum_worker_count=3,
        maximum_worker_count=10,
        pending_work=0,
        available_capacity=100,
        scale_down_safe=False,
    ),

    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=12,
        minimum_worker_count=2,
        maximum_worker_count=10,
        pending_work=0,
        available_capacity=0,
        scale_down_safe=True,
    ),

    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=12,
        minimum_worker_count=2,
        maximum_worker_count=10,
        pending_work=0,
        available_capacity=0,
        scale_down_safe=False,
    ),

    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=4,
        minimum_worker_count=2,
        maximum_worker_count=10,
        pending_work=20,
        available_capacity=5,
        scale_down_safe=False,
    ),

    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=10,
        minimum_worker_count=2,
        maximum_worker_count=10,
        pending_work=20,
        available_capacity=5,
        scale_down_safe=False,
    ),

    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=5,
        minimum_worker_count=2,
        maximum_worker_count=10,
        pending_work=0,
        available_capacity=100,
        scale_down_safe=True,
    ),

    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=5,
        minimum_worker_count=2,
        maximum_worker_count=10,
        pending_work=0,
        available_capacity=100,
        scale_down_safe=False,
    ),

    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=2,
        minimum_worker_count=2,
        maximum_worker_count=10,
        pending_work=0,
        available_capacity=100,
        scale_down_safe=True,
    ),

    scaling.create_universal_worker_scaling_evidence(
        current_worker_count=5,
        minimum_worker_count=2,
        maximum_worker_count=10,
        pending_work=1,
        available_capacity=100,
        scale_down_safe=True,
    ),
)


for case_index, evidence in enumerate(
    canonical_cases,
    start=1,
):

    expected = (
        scaling.evaluate_universal_worker_scaling(
            evidence
        )
    )

    for decision in scaling.UniversalWorkerScalingDecision:

        for reason in scaling.UniversalWorkerScalingReason:

            should_accept = (
                decision
                is expected.decision
                and
                reason
                is expected.reason
            )

            try:

                scaling.UniversalWorkerScalingResult(
                    decision=decision,
                    reason=reason,
                    current_worker_count=(
                        evidence.current_worker_count
                    ),
                    desired_worker_count=(
                        expected.desired_worker_count
                    ),
                    minimum_worker_count=(
                        evidence.minimum_worker_count
                    ),
                    maximum_worker_count=(
                        evidence.maximum_worker_count
                    ),
                    pending_work=(
                        evidence.pending_work
                    ),
                    available_capacity=(
                        evidence.available_capacity
                    ),
                    scale_down_safe=(
                        evidence.scale_down_safe
                    ),
                )

            except scaling.UniversalWorkerScalingError as exc:

                accepted = False

                correct_rejection = (
                    exc.code
                    == "inconsistent_worker_scaling_result"
                )

            else:

                accepted = True
                correct_rejection = False

            check(
                (
                    "result_forgery_case_"
                    + str(case_index)
                    + "_"
                    + decision.value
                    + "_"
                    + reason.value
                ),
                (
                    accepted
                    if should_accept
                    else correct_rejection
                ),
            )


# ============================================================
# 15 — DESIRED COUNT FORGERY
# ============================================================

for forged_desired in (
    0,
    1,
    4,
    6,
    10,
):

    should_accept = (
        forged_desired
        == canonical_result.desired_worker_count
    )

    try:

        scaling.UniversalWorkerScalingResult(
            decision=canonical_result.decision,
            reason=canonical_result.reason,
            current_worker_count=(
                canonical_result.current_worker_count
            ),
            desired_worker_count=forged_desired,
            minimum_worker_count=(
                canonical_result.minimum_worker_count
            ),
            maximum_worker_count=(
                canonical_result.maximum_worker_count
            ),
            pending_work=(
                canonical_result.pending_work
            ),
            available_capacity=(
                canonical_result.available_capacity
            ),
            scale_down_safe=(
                canonical_result.scale_down_safe
            ),
        )

    except scaling.UniversalWorkerScalingError as exc:

        accepted = False

        correct_rejection = (
            exc.code
            == "inconsistent_worker_scaling_result"
        )

    else:

        accepted = True
        correct_rejection = False

    check(
        "desired_count_forgery_"
        + str(forged_desired),
        (
            accepted
            if should_accept
            else correct_rejection
        ),
    )


# ============================================================
# 16 — RESULT PROPERTIES
# ============================================================

scale_up_result = (
    scaling.evaluate_universal_worker_scaling(
        scaling.create_universal_worker_scaling_evidence(
            current_worker_count=4,
            minimum_worker_count=1,
            maximum_worker_count=10,
            pending_work=10,
            available_capacity=0,
            scale_down_safe=False,
        )
    )
)

hold_result = (
    scaling.evaluate_universal_worker_scaling(
        scaling.create_universal_worker_scaling_evidence(
            current_worker_count=4,
            minimum_worker_count=1,
            maximum_worker_count=10,
            pending_work=1,
            available_capacity=100,
            scale_down_safe=True,
        )
    )
)

scale_down_result = (
    scaling.evaluate_universal_worker_scaling(
        scaling.create_universal_worker_scaling_evidence(
            current_worker_count=4,
            minimum_worker_count=1,
            maximum_worker_count=10,
            pending_work=0,
            available_capacity=100,
            scale_down_safe=True,
        )
    )
)


check(
    "scale_up_delta",
    scale_up_result.delta
    == 1,
)

check(
    "hold_delta",
    hold_result.delta
    == 0,
)

check(
    "scale_down_delta",
    scale_down_result.delta
    == -1,
)

check(
    "scale_up_required",
    scale_up_result.scaling_required
    is True,
)

check(
    "hold_not_required",
    hold_result.scaling_required
    is False,
)

check(
    "scale_down_required",
    scale_down_result.scaling_required
    is True,
)


# ============================================================
# 17 — IMMUTABILITY
# ============================================================

for obj, field_name in (
    (
        canonical_evidence,
        "current_worker_count",
    ),
    (
        canonical_evidence,
        "minimum_worker_count",
    ),
    (
        canonical_evidence,
        "maximum_worker_count",
    ),
    (
        canonical_evidence,
        "pending_work",
    ),
    (
        canonical_evidence,
        "available_capacity",
    ),
    (
        canonical_evidence,
        "scale_down_safe",
    ),
    (
        canonical_evidence,
        "schema_version",
    ),
    (
        canonical_result,
        "decision",
    ),
    (
        canonical_result,
        "reason",
    ),
    (
        canonical_result,
        "current_worker_count",
    ),
    (
        canonical_result,
        "desired_worker_count",
    ),
    (
        canonical_result,
        "minimum_worker_count",
    ),
    (
        canonical_result,
        "maximum_worker_count",
    ),
    (
        canonical_result,
        "pending_work",
    ),
    (
        canonical_result,
        "available_capacity",
    ),
    (
        canonical_result,
        "scale_down_safe",
    ),
    (
        canonical_result,
        "schema_version",
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
        (
            "immutable_"
            + type(obj).__name__
            + "_"
            + field_name
        ),
        immutable,
    )


# ============================================================
# 18 — DETERMINISM
# ============================================================

check(
    "deterministic_decision",
    scaling.decide_universal_worker_scaling(
        canonical_evidence
    )
    ==
    scaling.decide_universal_worker_scaling(
        canonical_evidence
    ),
)

check(
    "deterministic_result",
    scaling.evaluate_universal_worker_scaling(
        canonical_evidence
    )
    ==
    scaling.evaluate_universal_worker_scaling(
        canonical_evidence
    ),
)


# ============================================================
# 19 — EXPLANATION CONTRACT
# ============================================================

explanation = (
    scaling.explain_universal_worker_scaling_v1()
)


check(
    "explanation_phase",
    explanation.get(
        "phase"
    )
    == "4.1.7",
)

check(
    "explanation_component",
    explanation.get(
        "component"
    )
    == "Universal Worker Scaling",
)

check(
    "explanation_version",
    explanation.get(
        "version"
    )
    == scaling.UNIVERSAL_WORKER_SCALING_VERSION,
)

check(
    "evidence_schema_explained",
    explanation.get(
        "evidence_schema_version"
    )
    == scaling.UNIVERSAL_WORKER_SCALING_EVIDENCE_SCHEMA_VERSION,
)

check(
    "result_schema_explained",
    explanation.get(
        "result_schema_version"
    )
    == scaling.UNIVERSAL_WORKER_SCALING_RESULT_SCHEMA_VERSION,
)

check(
    "decisions_explained_exact",
    tuple(
        explanation.get(
            "decisions"
        )
    )
    == (
        "SCALE_UP",
        "HOLD",
        "SCALE_DOWN",
    ),
)

check(
    "caller_evidence_rule",
    "caller-supplied"
    in explanation.get(
        "input_rule",
        "",
    ),
)

check(
    "minimum_rule",
    "directly to minimum"
    in explanation.get(
        "minimum_rule",
        "",
    ),
)

check(
    "maximum_rule",
    "scale_down_safe"
    in explanation.get(
        "maximum_rule",
        "",
    ),
)

check(
    "scale_up_one_rule",
    "exactly one worker"
    in explanation.get(
        "scale_up_rule",
        "",
    ),
)

check(
    "scale_down_one_rule",
    "exactly one worker"
    in explanation.get(
        "scale_down_rule",
        "",
    ),
)

check(
    "capacity_boundary",
    "does not calculate per-worker capacity"
    in explanation.get(
        "capacity_boundary",
        "",
    ),
)

check(
    "pool_boundary",
    "does not define worker pools"
    in explanation.get(
        "pool_boundary",
        "",
    ),
)

check(
    "drain_shutdown_boundary",
    "scale_down_safe is caller-supplied"
    in explanation.get(
        "drain_shutdown_boundary",
        "",
    ),
)

check(
    "provisioning_boundary",
    (
        "evidence only"
        in explanation.get(
            "provisioning_boundary",
            "",
        )
        and
        "does not"
        in explanation.get(
            "provisioning_boundary",
            "",
        )
    ),
)

check(
    "resource_governance_boundary",
    "outside 4.1.7"
    in explanation.get(
        "resource_governance_boundary",
        "",
    ),
)

check(
    "queue_boundary",
    "does not read or mutate queues"
    in explanation.get(
        "queue_boundary",
        "",
    ),
)

check(
    "health_boundary",
    "does not read or classify Worker Health"
    in explanation.get(
        "health_boundary",
        "",
    ),
)

check(
    "purity_rule",
    "no state lookup, persistence or mutation"
    in explanation.get(
        "purity_rule",
        "",
    ),
)


# ============================================================
# 20 — PROHIBITION MATRIX
# ============================================================

required_prohibitions = (
    "does not provision workers",
    "does not start worker processes",
    "does not stop worker processes",
    "does not terminate workers",
    "does not register workers",
    "does not discover workers",
    "does not assign workers",
    "does not select workers for removal",
    "does not drain workers",
    "does not shut down workers",
    "does not inspect active leases",
    "does not acquire leases",
    "does not release leases",
    "does not define worker pools",
    "does not modify worker pool membership",
    "does not calculate per-worker capacity",
    "does not calculate worker utilization",
    "does not calculate worker concurrency",
    "does not inspect worker capabilities",
    "does not determine worker health",
    "does not read worker heartbeats",
    "does not detect stale workers",
    "does not recover workers",
    "does not access cloud-provider APIs",
    "does not create containers",
    "does not create pods",
    "does not create virtual machines",
    "does not enforce CPU quotas",
    "does not enforce memory quotas",
    "does not enforce cost budgets",
    "does not mutate Queue Infrastructure",
    "does not apply Queue Backpressure",
    "does not apply Queue Rate Limiting",
    "does not access Runtime State Store",
    "does not access orchestration",
    "does not persist scaling results",
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

source = SCALING_PATH.read_text(
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
    "no_backend_imports",
    backend_imports
    == [],
    backend_imports,
)


# ============================================================
# 22 — API SURFACE
# ============================================================

expected_all = (
    "UNIVERSAL_WORKER_SCALING_VERSION",
    "UNIVERSAL_WORKER_SCALING_EVIDENCE_SCHEMA_VERSION",
    "UNIVERSAL_WORKER_SCALING_RESULT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_COUNT",
    "MAX_UNIVERSAL_WORKER_SCALING_WORK_COUNT",
    "UniversalWorkerScalingError",
    "UniversalWorkerScalingDecision",
    "UniversalWorkerScalingReason",
    "UniversalWorkerScalingEvidence",
    "UniversalWorkerScalingResult",
    "create_universal_worker_scaling_evidence",
    "decide_universal_worker_scaling",
    "evaluate_universal_worker_scaling",
    "explain_universal_worker_scaling_v1",
)


check(
    "api_surface_exact",
    tuple(
        scaling.__all__
    )
    == expected_all,
    scaling.__all__,
)


# ============================================================
# 23 — FORBIDDEN CALLS
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
    "assign_universal_worker",
    "acquire_universal_worker_lease",
    "renew_universal_worker_lease",
    "release_universal_worker_lease",
    "evaluate_universal_worker_lease_state",
    "evaluate_universal_worker_health",
    "evaluate_universal_worker_recovery",
    "get_latest_worker_statuses",
    "get_runtime_state_store_registry",
    "dequeue_job",
    "enqueue_job",
    "requeue_job",
    "dispatch_job",
    "execute_job",
    "shutdown",
    "terminate",
    "kill",
    "spawn",
    "provision",
    "create_container",
    "create_pod",
    "create_instance",
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

        name = (
            node.func.id
        )

    elif isinstance(
        node.func,
        ast.Attribute,
    ):

        name = (
            node.func.attr
        )

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
    "provision",
    "spawn",
    "start_worker",
    "stop_worker",
    "terminate",
    "kill",
    "register_worker",
    "discover_worker",
    "assign_worker",
    "remove_worker",
    "drain_worker",
    "shutdown_worker",
    "acquire_lease",
    "release_lease",
    "worker_pool",
    "pool_membership",
    "worker_capacity",
    "worker_utilization",
    "worker_concurrency",
    "worker_capability",
    "worker_health",
    "heartbeat",
    "stale",
    "recover_worker",
    "enqueue",
    "dequeue",
    "requeue",
    "backpressure",
    "rate_limit",
    "state_store",
    "persist",
    "dispatch",
    "execute",
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
# 25 — NO RUNTIME-MUTATION ASSIGNMENTS
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
                "status",
                "worker_id",
                "worker_instance_id",
                "lease_owner",
                "lease_id",
                "lease_started_at",
                "lease_expires_at",
                "pool_id",
                "capacity",
                "heartbeat",
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


check(
    "no_runtime_state_mutation_assignments",
    not suspicious_assignments,
    suspicious_assignments,
)


# ============================================================
# 26 — PROTECTED AST MATRIX
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
# 27 — FINAL AST RECHECK
# ============================================================

final_ast = ast_sha(
    SCALING_PATH
)


check(
    "scaling_ast_final",
    final_ast
    == EXPECTED_SCALING_AST,
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
        "PHASE 4.1.7 — UNIVERSAL WORKER "
        "SCALING ADVERSARIAL REGRESSION"
    ),
    "=" * 112,
    "",
    (
        "WORKER SCALING AST SHA256: "
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
            "ADVERSARIAL WORKER SCALING REGRESSION: "
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
        "WORKER SCALING AST MODIFIED: NO",
        "4.1.1 WORKER REGISTRATION MODIFIED: NO",
        "4.1.2 WORKER DISCOVERY MODIFIED: NO",
        "4.1.3 WORKER ASSIGNMENT MODIFIED: NO",
        "4.1.4 WORKER LEASING MODIFIED: NO",
        "4.1.5 WORKER HEALTH MODIFIED: NO",
        "4.1.6 WORKER RECOVERY MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "EXISTING UNIVERSAL RUNTIME WORKER MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "WORKER PROVISIONED: NO",
        "WORKER STARTED: NO",
        "WORKER STOPPED: NO",
        "WORKER TERMINATED: NO",
        "WORKER REGISTERED: NO",
        "WORKER DISCOVERED: NO",
        "WORKER ASSIGNED: NO",
        "WORKER SELECTED FOR REMOVAL: NO",
        "WORKER DRAINED: NO",
        "WORKER SHUT DOWN: NO",
        "LEASE INSPECTED OR MUTATED: NO",
        "WORKER POOL DEFINED OR MUTATED: NO",
        "PER-WORKER CAPACITY CALCULATED: NO",
        "WORKER UTILIZATION CALCULATED: NO",
        "WORKER CONCURRENCY CALCULATED: NO",
        "WORKER CAPABILITY INSPECTED: NO",
        "WORKER HEALTH DECIDED: NO",
        "WORKER HEARTBEAT READ: NO",
        "STALE WORKER DETECTED: NO",
        "WORKER RECOVERY PERFORMED: NO",
        "CLOUD PROVIDER ACCESSED: NO",
        "CONTAINER/POD/VM CREATED: NO",
        "CPU/MEMORY/COST GOVERNANCE APPLIED: NO",
        "QUEUE MUTATED: NO",
        "BACKPRESSURE APPLIED: NO",
        "RATE LIMIT APPLIED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "SCALING RESULT PERSISTED: NO",
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
        "Phase 4.1.7 Worker Scaling adversarial regression failed."
    )
