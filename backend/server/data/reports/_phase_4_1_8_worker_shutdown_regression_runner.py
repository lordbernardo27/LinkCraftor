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

SHUTDOWN_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "shutdown.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_8_worker_shutdown_regression.txt"
)


EXPECTED_SHUTDOWN_AST = (
    "DB2197CA791988B01C73CE426ED29891C8BD9FE46DFEC1AC5AE79D1D131C34DD"
)

EXPECTED_RUNTIME_SHUTDOWN_AST = (
    "7A159E206C73157064B70D15A1CE4A97AB3D77EBBC77B01A2554BC34224EB272"
)

EXPECTED_RUNTIME_LIFECYCLE_AST = (
    "E6200CA0938B5D578954024D6E76E343FB39D9329CFD3ABE4B3AEF86E8204034"
)


# ============================================================
# PROTECTED FROZEN / INTEGRATION AUTHORITIES
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

    "worker_scaling": (
        ROOT / "backend/server/runtime/universal_worker/scaling.py",
        "8EC818E4EF4CA7DBCADCFCB93FD99BC80AAD4CE8AEBE1CDE63CCC44FA8488FF6",
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
        EXPECTED_RUNTIME_SHUTDOWN_AST,
    ),

    "runtime_lifecycle_manager": (
        ROOT / "backend/server/runtime/runtime_lifecycle_manager.py",
        EXPECTED_RUNTIME_LIFECYCLE_AST,
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

if not SHUTDOWN_PATH.exists():

    raise SystemExit(
        "Worker Shutdown authority missing."
    )


initial_shutdown_ast = ast_sha(
    SHUTDOWN_PATH
)


if initial_shutdown_ast != EXPECTED_SHUTDOWN_AST:

    raise SystemExit(
        (
            "Worker Shutdown AST changed before regression.\n"
            "EXPECTED: "
            + EXPECTED_SHUTDOWN_AST
            + "\nACTUAL:   "
            + initial_shutdown_ast
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
                "Protected authority mismatch before regression: "
                + name
                + "\nEXPECTED: "
                + expected
                + "\nACTUAL:   "
                + actual
            )
        )


# ============================================================
# IMPORT AUTHORITY
# ============================================================

sys.path.insert(
    0,
    str(ROOT),
)

module_name = (
    "backend.server.runtime."
    "universal_worker.shutdown"
)

sys.modules.pop(
    module_name,
    None,
)

shutdown = importlib.import_module(
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
# 1 — AST / CONSTANT / ENUM SURFACE
# ============================================================

check(
    "shutdown_ast_stable",
    ast_sha(SHUTDOWN_PATH)
    == EXPECTED_SHUTDOWN_AST,
    ast_sha(SHUTDOWN_PATH),
)

check(
    "version_exact",
    shutdown.UNIVERSAL_WORKER_SHUTDOWN_VERSION
    == "universal_worker_shutdown_v4.1.8",
)

check(
    "evidence_schema_exact",
    shutdown.UNIVERSAL_WORKER_SHUTDOWN_EVIDENCE_SCHEMA_VERSION
    == "universal_worker_shutdown_evidence_schema_v1",
)

check(
    "result_schema_exact",
    shutdown.UNIVERSAL_WORKER_SHUTDOWN_RESULT_SCHEMA_VERSION
    == "universal_worker_shutdown_result_schema_v1",
)

check(
    "max_active_count_exact",
    shutdown.MAX_UNIVERSAL_WORKER_SHUTDOWN_ACTIVE_COUNT
    == 2_147_483_647,
)

check(
    "decisions_exact",
    tuple(
        x.value
        for x in shutdown.UniversalWorkerShutdownDecision
    )
    == (
        "NOT_REQUESTED",
        "BLOCKED",
        "READY",
    ),
)

check(
    "reasons_exact",
    tuple(
        x.value
        for x in shutdown.UniversalWorkerShutdownReason
    )
    == (
        "SHUTDOWN_NOT_REQUESTED",
        "ACTIVE_WORK_PRESENT",
        "ACTIVE_LEASES_PRESENT",
        "DRAIN_INCOMPLETE",
        "SHUTDOWN_READY",
    ),
)


# ============================================================
# 2 — COMPLETE VALID STATE MATRIX
# ============================================================

case_number = 0


for (
    shutdown_requested,
    drain_complete,
    active_work_count,
    active_lease_count,
) in itertools.product(
    (False, True),
    (False, True),
    (0, 1, 2),
    (0, 1, 2),
):

    case_number += 1

    contradiction = (
        drain_complete
        and
        (
            active_work_count > 0
            or
            active_lease_count > 0
        )
    )

    try:

        evidence = (
            shutdown.create_universal_worker_shutdown_evidence(
                shutdown_requested=shutdown_requested,
                drain_complete=drain_complete,
                active_work_count=active_work_count,
                active_lease_count=active_lease_count,
            )
        )

    except shutdown.UniversalWorkerShutdownError as exc:

        accepted = False
        error_code = exc.code

    else:

        accepted = True
        error_code = None

    if contradiction:

        expected_codes = {
            "drain_complete_active_work_contradiction",
            "drain_complete_active_lease_contradiction",
        }

        check(
            "matrix_"
            + str(case_number)
            + "_contradiction_rejected",
            (
                not accepted
                and
                error_code in expected_codes
            ),
            error_code,
        )

        continue

    check(
        "matrix_"
        + str(case_number)
        + "_accepted",
        accepted,
    )

    if not accepted:

        continue

    result = (
        shutdown.evaluate_universal_worker_shutdown(
            evidence
        )
    )

    if not shutdown_requested:

        expected_decision = (
            shutdown.UniversalWorkerShutdownDecision.NOT_REQUESTED
        )

        expected_reason = (
            shutdown.UniversalWorkerShutdownReason.SHUTDOWN_NOT_REQUESTED
        )

    elif active_work_count > 0:

        expected_decision = (
            shutdown.UniversalWorkerShutdownDecision.BLOCKED
        )

        expected_reason = (
            shutdown.UniversalWorkerShutdownReason.ACTIVE_WORK_PRESENT
        )

    elif active_lease_count > 0:

        expected_decision = (
            shutdown.UniversalWorkerShutdownDecision.BLOCKED
        )

        expected_reason = (
            shutdown.UniversalWorkerShutdownReason.ACTIVE_LEASES_PRESENT
        )

    elif not drain_complete:

        expected_decision = (
            shutdown.UniversalWorkerShutdownDecision.BLOCKED
        )

        expected_reason = (
            shutdown.UniversalWorkerShutdownReason.DRAIN_INCOMPLETE
        )

    else:

        expected_decision = (
            shutdown.UniversalWorkerShutdownDecision.READY
        )

        expected_reason = (
            shutdown.UniversalWorkerShutdownReason.SHUTDOWN_READY
        )

    check(
        "matrix_"
        + str(case_number)
        + "_decision",
        result.decision
        is expected_decision,
    )

    check(
        "matrix_"
        + str(case_number)
        + "_reason",
        result.reason
        is expected_reason,
    )


# ============================================================
# 3 — NOT_REQUESTED PRECEDENCE
# ============================================================

for active_work_count, active_lease_count in (
    itertools.product(
        (0, 1, 100),
        (0, 1, 100),
    )
):

    evidence = (
        shutdown.create_universal_worker_shutdown_evidence(
            shutdown_requested=False,
            drain_complete=False,
            active_work_count=active_work_count,
            active_lease_count=active_lease_count,
        )
    )

    result = (
        shutdown.evaluate_universal_worker_shutdown(
            evidence
        )
    )

    check(
        (
            "not_requested_precedence_"
            + str(active_work_count)
            + "_"
            + str(active_lease_count)
        ),
        (
            result.decision
            is shutdown.UniversalWorkerShutdownDecision.NOT_REQUESTED
            and
            result.reason
            is (
                shutdown.UniversalWorkerShutdownReason
                .SHUTDOWN_NOT_REQUESTED
            )
        ),
    )


# ============================================================
# 4 — ACTIVE WORK PRECEDENCE
# ============================================================

for active_work_count, active_lease_count in (
    itertools.product(
        (1, 2, 100),
        (0, 1, 100),
    )
):

    evidence = (
        shutdown.create_universal_worker_shutdown_evidence(
            shutdown_requested=True,
            drain_complete=False,
            active_work_count=active_work_count,
            active_lease_count=active_lease_count,
        )
    )

    result = (
        shutdown.evaluate_universal_worker_shutdown(
            evidence
        )
    )

    check(
        (
            "active_work_precedence_"
            + str(active_work_count)
            + "_"
            + str(active_lease_count)
        ),
        (
            result.decision
            is shutdown.UniversalWorkerShutdownDecision.BLOCKED
            and
            result.reason
            is (
                shutdown.UniversalWorkerShutdownReason
                .ACTIVE_WORK_PRESENT
            )
        ),
    )


# ============================================================
# 5 — ACTIVE LEASE PRECEDENCE
# ============================================================

for active_lease_count in (
    1,
    2,
    100,
):

    evidence = (
        shutdown.create_universal_worker_shutdown_evidence(
            shutdown_requested=True,
            drain_complete=False,
            active_work_count=0,
            active_lease_count=active_lease_count,
        )
    )

    result = (
        shutdown.evaluate_universal_worker_shutdown(
            evidence
        )
    )

    check(
        "active_lease_precedence_"
        + str(active_lease_count),
        (
            result.decision
            is shutdown.UniversalWorkerShutdownDecision.BLOCKED
            and
            result.reason
            is (
                shutdown.UniversalWorkerShutdownReason
                .ACTIVE_LEASES_PRESENT
            )
        ),
    )


# ============================================================
# 6 — READY REQUIRES ALL FOUR CONDITIONS
# ============================================================

ready = (
    shutdown.create_universal_worker_shutdown_evidence(
        shutdown_requested=True,
        drain_complete=True,
        active_work_count=0,
        active_lease_count=0,
    )
)

ready_result = (
    shutdown.evaluate_universal_worker_shutdown(
        ready
    )
)


check(
    "ready_exact_decision",
    ready_result.decision
    is shutdown.UniversalWorkerShutdownDecision.READY,
)

check(
    "ready_exact_reason",
    ready_result.reason
    is shutdown.UniversalWorkerShutdownReason.SHUTDOWN_READY,
)

check(
    "ready_property_true",
    ready_result.shutdown_ready
    is True,
)

check(
    "ready_blocked_false",
    ready_result.shutdown_blocked
    is False,
)


# ============================================================
# 7 — BLOCKED PROPERTIES
# ============================================================

for evidence in (
    shutdown.create_universal_worker_shutdown_evidence(
        shutdown_requested=True,
        drain_complete=False,
        active_work_count=1,
        active_lease_count=0,
    ),

    shutdown.create_universal_worker_shutdown_evidence(
        shutdown_requested=True,
        drain_complete=False,
        active_work_count=0,
        active_lease_count=1,
    ),

    shutdown.create_universal_worker_shutdown_evidence(
        shutdown_requested=True,
        drain_complete=False,
        active_work_count=0,
        active_lease_count=0,
    ),
):

    result = (
        shutdown.evaluate_universal_worker_shutdown(
            evidence
        )
    )

    check(
        "blocked_ready_false_"
        + result.reason.value,
        result.shutdown_ready
        is False,
    )

    check(
        "blocked_property_true_"
        + result.reason.value,
        result.shutdown_blocked
        is True,
    )


not_requested_result = (
    shutdown.evaluate_universal_worker_shutdown(
        shutdown.create_universal_worker_shutdown_evidence(
            shutdown_requested=False,
            drain_complete=False,
            active_work_count=0,
            active_lease_count=0,
        )
    )
)


check(
    "not_requested_ready_false",
    not_requested_result.shutdown_ready
    is False,
)

check(
    "not_requested_blocked_false",
    not_requested_result.shutdown_blocked
    is False,
)


# ============================================================
# 8 — STRICT BOOLEAN ATTACKS
# ============================================================

bad_boolean_values = (
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
)


for field_name in (
    "shutdown_requested",
    "drain_complete",
):

    for index, bad in enumerate(
        bad_boolean_values,
        start=1,
    ):

        kwargs = {
            "shutdown_requested": False,
            "drain_complete": False,
            "active_work_count": 0,
            "active_lease_count": 0,
        }

        kwargs[
            field_name
        ] = bad

        try:

            shutdown.create_universal_worker_shutdown_evidence(
                **kwargs
            )

        except shutdown.UniversalWorkerShutdownError as exc:

            rejected = (
                exc.code
                == "invalid_worker_shutdown_boolean"
            )

        else:

            rejected = False

        check(
            (
                "strict_bool_"
                + field_name
                + "_"
                + str(index)
            ),
            rejected,
            repr(bad),
        )


# ============================================================
# 9 — STRICT COUNT ATTACKS
# ============================================================

bad_count_values = (
    None,
    True,
    False,
    -1,
    -999,
    0.0,
    1.0,
    "",
    "0",
    "1",
    [],
    {},
    (),
    set(),
)


for field_name in (
    "active_work_count",
    "active_lease_count",
):

    for index, bad in enumerate(
        bad_count_values,
        start=1,
    ):

        kwargs = {
            "shutdown_requested": False,
            "drain_complete": False,
            "active_work_count": 0,
            "active_lease_count": 0,
        }

        kwargs[
            field_name
        ] = bad

        try:

            shutdown.create_universal_worker_shutdown_evidence(
                **kwargs
            )

        except shutdown.UniversalWorkerShutdownError as exc:

            rejected = (
                exc.code
                == "invalid_worker_shutdown_count"
            )

        else:

            rejected = False

        check(
            (
                "strict_count_"
                + field_name
                + "_"
                + str(index)
            ),
            rejected,
            repr(bad),
        )


# ============================================================
# 10 — MAXIMUM COUNT BOUNDARIES
# ============================================================

maximum = (
    shutdown.MAX_UNIVERSAL_WORKER_SHUTDOWN_ACTIVE_COUNT
)


for field_name in (
    "active_work_count",
    "active_lease_count",
):

    kwargs = {
        "shutdown_requested": False,
        "drain_complete": False,
        "active_work_count": 0,
        "active_lease_count": 0,
    }

    kwargs[
        field_name
    ] = maximum

    try:

        evidence = (
            shutdown.create_universal_worker_shutdown_evidence(
                **kwargs
            )
        )

    except shutdown.UniversalWorkerShutdownError:

        accepted = False

    else:

        accepted = (
            getattr(
                evidence,
                field_name,
            )
            == maximum
        )

    check(
        "exact_max_"
        + field_name,
        accepted,
    )


for field_name in (
    "active_work_count",
    "active_lease_count",
):

    kwargs = {
        "shutdown_requested": False,
        "drain_complete": False,
        "active_work_count": 0,
        "active_lease_count": 0,
    }

    kwargs[
        field_name
    ] = maximum + 1

    try:

        shutdown.create_universal_worker_shutdown_evidence(
            **kwargs
        )

    except shutdown.UniversalWorkerShutdownError as exc:

        rejected = (
            exc.code
            == "worker_shutdown_count_too_large"
        )

    else:

        rejected = False

    check(
        "overflow_"
        + field_name,
        rejected,
    )


# ============================================================
# 11 — CONTRADICTION ATTACKS
# ============================================================

for shutdown_requested in (
    False,
    True,
):

    for work_count in (
        1,
        2,
        100,
    ):

        try:

            shutdown.create_universal_worker_shutdown_evidence(
                shutdown_requested=shutdown_requested,
                drain_complete=True,
                active_work_count=work_count,
                active_lease_count=0,
            )

        except shutdown.UniversalWorkerShutdownError as exc:

            rejected = (
                exc.code
                == "drain_complete_active_work_contradiction"
            )

        else:

            rejected = False

        check(
            (
                "active_work_contradiction_"
                + str(shutdown_requested)
                + "_"
                + str(work_count)
            ),
            rejected,
        )


for shutdown_requested in (
    False,
    True,
):

    for lease_count in (
        1,
        2,
        100,
    ):

        try:

            shutdown.create_universal_worker_shutdown_evidence(
                shutdown_requested=shutdown_requested,
                drain_complete=True,
                active_work_count=0,
                active_lease_count=lease_count,
            )

        except shutdown.UniversalWorkerShutdownError as exc:

            rejected = (
                exc.code
                == "drain_complete_active_lease_contradiction"
            )

        else:

            rejected = False

        check(
            (
                "active_lease_contradiction_"
                + str(shutdown_requested)
                + "_"
                + str(lease_count)
            ),
            rejected,
        )


# ============================================================
# 12 — CONTRADICTION PRECEDENCE
# ============================================================

try:

    shutdown.create_universal_worker_shutdown_evidence(
        shutdown_requested=True,
        drain_complete=True,
        active_work_count=1,
        active_lease_count=1,
    )

except shutdown.UniversalWorkerShutdownError as exc:

    check(
        "work_contradiction_precedes_lease_contradiction",
        exc.code
        == "drain_complete_active_work_contradiction",
        exc.code,
    )

else:

    check(
        "work_contradiction_precedes_lease_contradiction",
        False,
        "not rejected",
    )


# ============================================================
# 13 — INVALID EVIDENCE OBJECTS
# ============================================================

invalid_objects = (
    None,
    True,
    False,
    0,
    1,
    "",
    "READY",
    {},
    [],
    (),
    set(),
)


for index, bad in enumerate(
    invalid_objects,
    start=1,
):

    try:

        shutdown.decide_universal_worker_shutdown(
            bad
        )

    except shutdown.UniversalWorkerShutdownError as exc:

        rejected = (
            exc.code
            == "invalid_worker_shutdown_evidence"
        )

    else:

        rejected = False

    check(
        "invalid_decide_evidence_"
        + str(index),
        rejected,
        repr(bad),
    )


for index, bad in enumerate(
    invalid_objects,
    start=1,
):

    try:

        shutdown.evaluate_universal_worker_shutdown(
            bad
        )

    except shutdown.UniversalWorkerShutdownError as exc:

        rejected = (
            exc.code
            == "invalid_worker_shutdown_evidence"
        )

    else:

        rejected = False

    check(
        "invalid_evaluate_evidence_"
        + str(index),
        rejected,
        repr(bad),
    )


# ============================================================
# 14 — SCHEMA TAMPERING
# ============================================================

try:

    shutdown.UniversalWorkerShutdownEvidence(
        shutdown_requested=False,
        drain_complete=False,
        active_work_count=0,
        active_lease_count=0,
        schema_version="tampered",
    )

except shutdown.UniversalWorkerShutdownError as exc:

    rejected = (
        exc.code
        == "invalid_worker_shutdown_evidence_schema_version"
    )

else:

    rejected = False


check(
    "evidence_schema_tamper",
    rejected,
)


canonical_result = (
    shutdown.evaluate_universal_worker_shutdown(
        ready
    )
)


try:

    shutdown.UniversalWorkerShutdownResult(
        decision=canonical_result.decision,
        reason=canonical_result.reason,
        shutdown_requested=canonical_result.shutdown_requested,
        drain_complete=canonical_result.drain_complete,
        active_work_count=canonical_result.active_work_count,
        active_lease_count=canonical_result.active_lease_count,
        schema_version="tampered",
    )

except shutdown.UniversalWorkerShutdownError as exc:

    rejected = (
        exc.code
        == "invalid_worker_shutdown_result_schema_version"
    )

else:

    rejected = False


check(
    "result_schema_tamper",
    rejected,
)


# ============================================================
# 15 — RAW ENUM ATTACKS
# ============================================================

try:

    shutdown.UniversalWorkerShutdownResult(
        decision="READY",
        reason=(
            shutdown.UniversalWorkerShutdownReason.SHUTDOWN_READY
        ),
        shutdown_requested=True,
        drain_complete=True,
        active_work_count=0,
        active_lease_count=0,
    )

except shutdown.UniversalWorkerShutdownError as exc:

    rejected = (
        exc.code
        == "invalid_worker_shutdown_decision"
    )

else:

    rejected = False


check(
    "raw_decision_rejected",
    rejected,
)


try:

    shutdown.UniversalWorkerShutdownResult(
        decision=(
            shutdown.UniversalWorkerShutdownDecision.READY
        ),
        reason="SHUTDOWN_READY",
        shutdown_requested=True,
        drain_complete=True,
        active_work_count=0,
        active_lease_count=0,
    )

except shutdown.UniversalWorkerShutdownError as exc:

    rejected = (
        exc.code
        == "invalid_worker_shutdown_reason"
    )

else:

    rejected = False


check(
    "raw_reason_rejected",
    rejected,
)


# ============================================================
# 16 — RESULT FORGERY MATRIX
# ============================================================

canonical_cases = (
    shutdown.create_universal_worker_shutdown_evidence(
        shutdown_requested=False,
        drain_complete=False,
        active_work_count=0,
        active_lease_count=0,
    ),

    shutdown.create_universal_worker_shutdown_evidence(
        shutdown_requested=True,
        drain_complete=False,
        active_work_count=1,
        active_lease_count=0,
    ),

    shutdown.create_universal_worker_shutdown_evidence(
        shutdown_requested=True,
        drain_complete=False,
        active_work_count=0,
        active_lease_count=1,
    ),

    shutdown.create_universal_worker_shutdown_evidence(
        shutdown_requested=True,
        drain_complete=False,
        active_work_count=0,
        active_lease_count=0,
    ),

    shutdown.create_universal_worker_shutdown_evidence(
        shutdown_requested=True,
        drain_complete=True,
        active_work_count=0,
        active_lease_count=0,
    ),
)


for case_index, evidence in enumerate(
    canonical_cases,
    start=1,
):

    expected = (
        shutdown.evaluate_universal_worker_shutdown(
            evidence
        )
    )

    for decision in (
        shutdown.UniversalWorkerShutdownDecision
    ):

        for reason in (
            shutdown.UniversalWorkerShutdownReason
        ):

            should_accept = (
                decision
                is expected.decision
                and
                reason
                is expected.reason
            )

            try:

                shutdown.UniversalWorkerShutdownResult(
                    decision=decision,
                    reason=reason,
                    shutdown_requested=(
                        evidence.shutdown_requested
                    ),
                    drain_complete=(
                        evidence.drain_complete
                    ),
                    active_work_count=(
                        evidence.active_work_count
                    ),
                    active_lease_count=(
                        evidence.active_lease_count
                    ),
                )

            except shutdown.UniversalWorkerShutdownError as exc:

                accepted = False

                correct_rejection = (
                    exc.code
                    == "inconsistent_worker_shutdown_result"
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
# 17 — IMMUTABILITY
# ============================================================

for obj, field_name in (
    (ready, "shutdown_requested"),
    (ready, "drain_complete"),
    (ready, "active_work_count"),
    (ready, "active_lease_count"),
    (ready, "schema_version"),
    (ready_result, "decision"),
    (ready_result, "reason"),
    (ready_result, "shutdown_requested"),
    (ready_result, "drain_complete"),
    (ready_result, "active_work_count"),
    (ready_result, "active_lease_count"),
    (ready_result, "schema_version"),
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
    shutdown.decide_universal_worker_shutdown(
        ready
    )
    ==
    shutdown.decide_universal_worker_shutdown(
        ready
    ),
)

check(
    "deterministic_result",
    shutdown.evaluate_universal_worker_shutdown(
        ready
    )
    ==
    shutdown.evaluate_universal_worker_shutdown(
        ready
    ),
)


# ============================================================
# 19 — EXPLANATION CONTRACT
# ============================================================

explanation = (
    shutdown.explain_universal_worker_shutdown_v1()
)


check(
    "explanation_phase",
    explanation.get(
        "phase"
    )
    == "4.1.8",
)

check(
    "explanation_component",
    explanation.get(
        "component"
    )
    == "Universal Worker Shutdown",
)

check(
    "explanation_version",
    explanation.get(
        "version"
    )
    == shutdown.UNIVERSAL_WORKER_SHUTDOWN_VERSION,
)

check(
    "evidence_schema_explained",
    explanation.get(
        "evidence_schema_version"
    )
    == shutdown.UNIVERSAL_WORKER_SHUTDOWN_EVIDENCE_SCHEMA_VERSION,
)

check(
    "result_schema_explained",
    explanation.get(
        "result_schema_version"
    )
    == shutdown.UNIVERSAL_WORKER_SHUTDOWN_RESULT_SCHEMA_VERSION,
)

check(
    "decisions_explained_exact",
    tuple(
        explanation.get(
            "decisions"
        )
    )
    == (
        "NOT_REQUESTED",
        "BLOCKED",
        "READY",
    ),
)

check(
    "caller_input_rule",
    "caller-supplied"
    in explanation.get(
        "input_rule",
        "",
    ),
)

check(
    "shutdown_request_explicit",
    "explicit shutdown request"
    in explanation.get(
        "not_requested_rule",
        "",
    ),
)

check(
    "active_work_blocks",
    "active work remains"
    in explanation.get(
        "active_work_rule",
        "",
    ),
)

check(
    "active_lease_blocks",
    "active lease ownership remains"
    in explanation.get(
        "active_lease_rule",
        "",
    ),
)

check(
    "drain_completion_required",
    "drain_complete"
    in explanation.get(
        "drain_rule",
        "",
    ),
)

check(
    "ready_four_conditions",
    (
        "shutdown requested"
        in explanation.get(
            "ready_rule",
            "",
        )
        and
        "drain complete"
        in explanation.get(
            "ready_rule",
            "",
        )
        and
        "zero active work"
        in explanation.get(
            "ready_rule",
            "",
        )
        and
        "zero active leases"
        in explanation.get(
            "ready_rule",
            "",
        )
    ),
)

check(
    "drain_boundary_exact",
    "4.1.12 Worker Drain"
    in explanation.get(
        "drain_boundary",
        "",
    ),
)

check(
    "runtime_shutdown_separate",
    "whole-runtime shutdown process"
    in explanation.get(
        "runtime_shutdown_boundary",
        "",
    ),
)

check(
    "ready_permission_only",
    "permission"
    in explanation.get(
        "termination_boundary",
        "",
    ),
)

check(
    "lease_caller_owned",
    "caller-supplied"
    in explanation.get(
        "lease_boundary",
        "",
    ),
)

check(
    "work_caller_owned",
    "caller-supplied"
    in explanation.get(
        "work_boundary",
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
    "heartbeat_boundary",
    "does not emit"
    in explanation.get(
        "heartbeat_boundary",
        "",
    ),
)

check(
    "health_scaling_not_automatic",
    "do not automatically imply shutdown"
    in explanation.get(
        "health_scaling_boundary",
        "",
    ),
)

check(
    "forced_shutdown_outside",
    "outside"
    in explanation.get(
        "forced_shutdown_boundary",
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
    "does not stop worker processes",
    "does not kill workers",
    "does not terminate workers",
    "does not send operating-system signals",
    "does not invoke whole-runtime shutdown",
    "does not drain workers",
    "does not determine drain state",
    "does not inspect active jobs",
    "does not inspect active leases",
    "does not acquire leases",
    "does not renew leases",
    "does not release leases",
    "does not cancel jobs",
    "does not fail jobs",
    "does not requeue jobs",
    "does not recover jobs",
    "does not recover workers",
    "does not deregister workers",
    "does not delete worker registrations",
    "does not modify Worker Pool membership",
    "does not emit worker heartbeats",
    "does not delete worker heartbeats",
    "does not inspect worker heartbeats",
    "does not determine Worker Health",
    "does not perform Worker Scaling",
    "does not assign workers",
    "does not provision replacement workers",
    "does not mutate Queue Infrastructure",
    "does not access Runtime State Store",
    "does not access orchestration",
    "does not persist shutdown results",
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

source = SHUTDOWN_PATH.read_text(
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
    "UNIVERSAL_WORKER_SHUTDOWN_VERSION",
    "UNIVERSAL_WORKER_SHUTDOWN_EVIDENCE_SCHEMA_VERSION",
    "UNIVERSAL_WORKER_SHUTDOWN_RESULT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_SHUTDOWN_ACTIVE_COUNT",
    "UniversalWorkerShutdownError",
    "UniversalWorkerShutdownDecision",
    "UniversalWorkerShutdownReason",
    "UniversalWorkerShutdownEvidence",
    "UniversalWorkerShutdownResult",
    "create_universal_worker_shutdown_evidence",
    "decide_universal_worker_shutdown",
    "evaluate_universal_worker_shutdown",
    "explain_universal_worker_shutdown_v1",
)


check(
    "api_surface_exact",
    tuple(
        shutdown.__all__
    )
    == expected_all,
    shutdown.__all__,
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

    "shutdown_runtime",
    "shutdown",
    "stop",
    "terminate",
    "kill",
    "signal",
    "send_signal",

    "drain",
    "drain_worker",

    "release_universal_worker_lease",
    "renew_universal_worker_lease",
    "acquire_universal_worker_lease",
    "evaluate_universal_worker_lease_state",

    "dequeue_job",
    "enqueue_job",
    "requeue_job",
    "cancel_job",
    "mark_job_failed",
    "mark_job_completed",

    "evaluate_universal_worker_recovery",
    "evaluate_universal_worker_scaling",
    "evaluate_universal_worker_health",

    "worker_heartbeat",
    "get_latest_worker_statuses",

    "get_runtime_state_store_registry",

    "assign_universal_worker",

    "dispatch_job",
    "execute_job",

    "unregister",
    "deregister",
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
    "terminate_worker",
    "kill_worker",
    "stop_worker",
    "signal_worker",
    "send_signal",
    "shutdown_runtime",
    "drain_worker",
    "drain_state",
    "inspect_job",
    "inspect_lease",
    "acquire_lease",
    "renew_lease",
    "release_lease",
    "cancel_job",
    "fail_job",
    "requeue_job",
    "recover_job",
    "recover_worker",
    "deregister_worker",
    "delete_registration",
    "pool_membership",
    "heartbeat",
    "worker_health",
    "worker_scaling",
    "assign_worker",
    "provision",
    "queue_mutation",
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

        if not isinstance(
            target,
            ast.Attribute,
        ):

            continue

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
            "heartbeat",
            "heartbeat_at",
            "draining",
            "shutdown",
            "shutdown_requested",
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
# 26 — NO WALL-CLOCK / THREAD / PROCESS / SIGNAL OWNERSHIP
# ============================================================

source_lower = source.lower()


for token in (
    "datetime.now",
    "datetime.utcnow",
    "time.time",
    "time.sleep",
    "threading.",
    "multiprocessing.",
    "subprocess.",
    "signal.sigterm",
    "signal.sigint",
    "os.kill",
    "os._exit",
    "sys.exit",
    "systemexit",
):

    check(
        "no_runtime_mechanism_"
        + token.replace(
            ".",
            "_",
        ),
        token
        not in source_lower,
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
        actual
        == expected,
        actual,
    )


# ============================================================
# 28 — FINAL SHUTDOWN AST RECHECK
# ============================================================

final_shutdown_ast = ast_sha(
    SHUTDOWN_PATH
)


check(
    "shutdown_ast_final",
    final_shutdown_ast
    == EXPECTED_SHUTDOWN_AST,
    final_shutdown_ast,
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
        "PHASE 4.1.8 — UNIVERSAL WORKER "
        "SHUTDOWN ADVERSARIAL REGRESSION"
    ),
    "=" * 112,
    "",
    (
        "WORKER SHUTDOWN AST SHA256: "
        + final_shutdown_ast
    ),
    (
        "RUNTIME SHUTDOWN PROCESS AST: "
        + ast_sha(
            PROTECTED[
                "runtime_shutdown_process"
            ][0]
        )
    ),
    (
        "RUNTIME LIFECYCLE MANAGER AST: "
        + ast_sha(
            PROTECTED[
                "runtime_lifecycle_manager"
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
            "ADVERSARIAL WORKER SHUTDOWN REGRESSION: "
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
        "WORKER SHUTDOWN AST MODIFIED: NO",
        "4.1.1 WORKER REGISTRATION MODIFIED: NO",
        "4.1.2 WORKER DISCOVERY MODIFIED: NO",
        "4.1.3 WORKER ASSIGNMENT MODIFIED: NO",
        "4.1.4 WORKER LEASING MODIFIED: NO",
        "4.1.5 WORKER HEALTH MODIFIED: NO",
        "4.1.6 WORKER RECOVERY MODIFIED: NO",
        "4.1.7 WORKER SCALING MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "EXISTING UNIVERSAL RUNTIME WORKER MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "WHOLE-RUNTIME SHUTDOWN PROCESS MODIFIED: NO",
        "RUNTIME LIFECYCLE MANAGER MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "WORKER PROCESS STOPPED: NO",
        "WORKER PROCESS KILLED: NO",
        "WORKER PROCESS TERMINATED: NO",
        "OPERATING-SYSTEM SIGNAL SENT: NO",
        "WHOLE-RUNTIME SHUTDOWN INVOKED: NO",
        "WORKER DRAINED: NO",
        "DRAIN STATE DETERMINED: NO",
        "ACTIVE JOBS INSPECTED: NO",
        "ACTIVE LEASES INSPECTED: NO",
        "LEASE ACQUIRED/RENEWED/RELEASED: NO",
        "JOB CANCELLED: NO",
        "JOB FAILED: NO",
        "JOB REQUEUED: NO",
        "JOB/WORKER RECOVERY PERFORMED: NO",
        "WORKER DEREGISTERED: NO",
        "WORKER REGISTRATION DELETED: NO",
        "WORKER POOL MEMBERSHIP MODIFIED: NO",
        "WORKER HEARTBEAT EMITTED/DELETED/READ: NO",
        "WORKER HEALTH DECIDED: NO",
        "WORKER SCALING PERFORMED: NO",
        "WORKER ASSIGNED: NO",
        "REPLACEMENT WORKER PROVISIONED: NO",
        "QUEUE MUTATED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "SHUTDOWN RESULT PERSISTED: NO",
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
        "Phase 4.1.8 Worker Shutdown adversarial regression failed."
    )
