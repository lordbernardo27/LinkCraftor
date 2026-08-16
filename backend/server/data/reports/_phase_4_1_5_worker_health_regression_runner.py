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

HEALTH_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "health.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_5_worker_health_regression.txt"
)

EXPECTED_HEALTH_AST = (
    "DCC43E77BDC12188DFD15044DA4DA41022B3CEF40F9C4ED06371EE66AA4E5F65"
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


sys.path.insert(
    0,
    str(ROOT),
)

registration = importlib.import_module(
    "backend.server.runtime.universal_worker.registration"
)

health_name = (
    "backend.server.runtime."
    "universal_worker.health"
)

sys.modules.pop(
    health_name,
    None,
)

health = importlib.import_module(
    health_name
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
# 1 — AST / VERSION / SCHEMAS / STATES
# ============================================================

health_ast = ast_sha(
    HEALTH_PATH
)

check(
    "health_ast_stable",
    health_ast
    == EXPECTED_HEALTH_AST,
    health_ast,
)

check(
    "version_exact",
    health.UNIVERSAL_WORKER_HEALTH_VERSION
    == "universal_worker_health_v4.1.5",
)

check(
    "evidence_schema_exact",
    health.UNIVERSAL_WORKER_HEALTH_EVIDENCE_SCHEMA_VERSION
    == "universal_worker_health_evidence_schema_v1",
)

check(
    "result_schema_exact",
    health.UNIVERSAL_WORKER_HEALTH_RESULT_SCHEMA_VERSION
    == "universal_worker_health_result_schema_v1",
)

check(
    "state_values_exact",
    tuple(
        state.value
        for state in health.UniversalWorkerHealthState
    )
    == (
        "HEALTHY",
        "DEGRADED",
        "UNHEALTHY",
        "UNKNOWN",
    ),
)


# ============================================================
# 2 — WORKER FIXTURES
# ============================================================

def worker(
    worker_id="worker-a",
    instance_id="instance-001",
):

    return (
        registration.create_universal_worker_registration(
            worker_id=worker_id,
            worker_type="general",
            worker_instance_id=instance_id,
            runtime_version="runtime-v1",
            host_id="host-a",
            registered_at="2026-08-15T20:00:00Z",
        )
    )


worker_a = worker()


# ============================================================
# 3 — COMPLETE TRISTATE CLASSIFICATION MATRIX
# ============================================================

values = (
    None,
    False,
    True,
)


def expected_state(
    health_check_passed,
    critical_failure_present,
    degraded_condition_present,
):

    if critical_failure_present is True:
        return health.UniversalWorkerHealthState.UNHEALTHY

    if health_check_passed is False:
        return health.UniversalWorkerHealthState.UNHEALTHY

    if degraded_condition_present is True:
        return health.UniversalWorkerHealthState.DEGRADED

    if health_check_passed is True:
        return health.UniversalWorkerHealthState.HEALTHY

    return health.UniversalWorkerHealthState.UNKNOWN


for index, (
    passed_signal,
    critical_signal,
    degraded_signal,
) in enumerate(
    itertools.product(
        values,
        values,
        values,
    ),
    start=1,
):

    evidence = (
        health.create_universal_worker_health_evidence(
            health_check_passed=passed_signal,
            critical_failure_present=critical_signal,
            degraded_condition_present=degraded_signal,
        )
    )

    actual = (
        health.classify_universal_worker_health_evidence(
            evidence
        )
    )

    expected = (
        expected_state(
            passed_signal,
            critical_signal,
            degraded_signal,
        )
    )

    check(
        "classification_matrix_"
        + str(index),
        actual is expected,
        (
            f"signals=({passed_signal!r}, "
            f"{critical_signal!r}, "
            f"{degraded_signal!r}) "
            f"expected={expected.value} "
            f"actual={actual.value}"
        ),
    )


# ============================================================
# 4 — PRECEDENCE ATTACKS
# ============================================================

critical_over_everything = (
    health.create_universal_worker_health_evidence(
        health_check_passed=True,
        critical_failure_present=True,
        degraded_condition_present=True,
    )
)


check(
    "critical_beats_pass_and_degraded",
    health.classify_universal_worker_health_evidence(
        critical_over_everything
    )
    is health.UniversalWorkerHealthState.UNHEALTHY,
)


failed_over_degraded = (
    health.create_universal_worker_health_evidence(
        health_check_passed=False,
        critical_failure_present=False,
        degraded_condition_present=True,
    )
)


check(
    "failed_check_beats_degraded",
    health.classify_universal_worker_health_evidence(
        failed_over_degraded
    )
    is health.UniversalWorkerHealthState.UNHEALTHY,
)


degraded_over_pass = (
    health.create_universal_worker_health_evidence(
        health_check_passed=True,
        critical_failure_present=False,
        degraded_condition_present=True,
    )
)


check(
    "degraded_beats_pass",
    health.classify_universal_worker_health_evidence(
        degraded_over_pass
    )
    is health.UniversalWorkerHealthState.DEGRADED,
)


# ============================================================
# 5 — UNKNOWN SEMANTICS
# ============================================================

unknown_cases = (
    (
        None,
        None,
        None,
    ),
    (
        None,
        False,
        None,
    ),
    (
        None,
        None,
        False,
    ),
    (
        None,
        False,
        False,
    ),
)


for index, (
    passed_signal,
    critical_signal,
    degraded_signal,
) in enumerate(
    unknown_cases,
    start=1,
):

    evidence = (
        health.create_universal_worker_health_evidence(
            health_check_passed=passed_signal,
            critical_failure_present=critical_signal,
            degraded_condition_present=degraded_signal,
        )
    )

    check(
        "unknown_case_"
        + str(index),
        health.classify_universal_worker_health_evidence(
            evidence
        )
        is health.UniversalWorkerHealthState.UNKNOWN,
    )


# ============================================================
# 6 — SUPPLIED SIGNAL COUNT
# ============================================================

for expected_count, kwargs in (
    (
        0,
        {},
    ),
    (
        1,
        {
            "health_check_passed":
                True,
        },
    ),
    (
        2,
        {
            "critical_failure_present":
                False,

            "degraded_condition_present":
                False,
        },
    ),
    (
        3,
        {
            "health_check_passed":
                False,

            "critical_failure_present":
                False,

            "degraded_condition_present":
                True,
        },
    ),
):

    evidence = (
        health.create_universal_worker_health_evidence(
            **kwargs
        )
    )

    check(
        "signal_count_"
        + str(expected_count),
        evidence.supplied_signal_count
        == expected_count,
        evidence.supplied_signal_count,
    )


# ============================================================
# 7 — STRICT BOOL ATTACKS
# ============================================================

bad_signal_values = (
    0,
    1,
    -1,
    1.0,
    0.0,
    "",
    "true",
    "false",
    [],
    {},
    (),
    set(),
    object(),
)


for field_name in (
    "health_check_passed",
    "critical_failure_present",
    "degraded_condition_present",
):

    for index, bad in enumerate(
        bad_signal_values,
        start=1,
    ):

        kwargs = {
            "health_check_passed":
                None,

            "critical_failure_present":
                None,

            "degraded_condition_present":
                None,
        }

        kwargs[
            field_name
        ] = bad

        try:

            health.create_universal_worker_health_evidence(
                **kwargs
            )

        except health.UniversalWorkerHealthError as exc:

            rejected = (
                exc.code
                == "invalid_worker_health_signal"
            )

        else:

            rejected = False

        check(
            (
                "strict_"
                + field_name
                + "_"
                + str(index)
            ),
            rejected,
            repr(bad),
        )


# ============================================================
# 8 — BOOL / NONE ACCEPTANCE
# ============================================================

for field_name in (
    "health_check_passed",
    "critical_failure_present",
    "degraded_condition_present",
):

    for value in (
        None,
        False,
        True,
    ):

        kwargs = {
            "health_check_passed":
                None,

            "critical_failure_present":
                None,

            "degraded_condition_present":
                None,
        }

        kwargs[
            field_name
        ] = value

        try:

            evidence = (
                health.create_universal_worker_health_evidence(
                    **kwargs
                )
            )

        except Exception as exc:

            accepted = False
            detail = repr(exc)

        else:

            accepted = (
                getattr(
                    evidence,
                    field_name,
                )
                is value
            )

            detail = repr(
                getattr(
                    evidence,
                    field_name,
                )
            )

        check(
            (
                "accepted_"
                + field_name
                + "_"
                + repr(value)
            ),
            accepted,
            detail,
        )


# ============================================================
# 9 — INVALID WORKER ATTACKS
# ============================================================

valid_evidence = (
    health.create_universal_worker_health_evidence(
        health_check_passed=True,
    )
)


for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        1,
        "",
        "worker-a",
        {},
        [],
        (),
    ),
    start=1,
):

    try:

        health.evaluate_universal_worker_health(
            worker=bad,
            evidence=valid_evidence,
        )

    except health.UniversalWorkerHealthError as exc:

        rejected = (
            exc.code
            == "invalid_worker_registration"
        )

    else:

        rejected = False

    check(
        "invalid_worker_"
        + str(index),
        rejected,
        repr(bad),
    )


# ============================================================
# 10 — INVALID EVIDENCE ATTACKS
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

        health.classify_universal_worker_health_evidence(
            bad
        )

    except health.UniversalWorkerHealthError as exc:

        rejected = (
            exc.code
            == "invalid_worker_health_evidence"
        )

    else:

        rejected = False

    check(
        "invalid_classifier_evidence_"
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

        health.evaluate_universal_worker_health(
            worker=worker_a,
            evidence=bad,
        )

    except health.UniversalWorkerHealthError as exc:

        rejected = (
            exc.code
            == "invalid_worker_health_evidence"
        )

    else:

        rejected = False

    check(
        "invalid_evaluator_evidence_"
        + str(index),
        rejected,
        repr(bad),
    )


# ============================================================
# 11 — RESULT IDENTITY / HEALTHY PROPERTY
# ============================================================

for state_expected, evidence in (
    (
        health.UniversalWorkerHealthState.HEALTHY,
        health.create_universal_worker_health_evidence(
            health_check_passed=True,
        ),
    ),
    (
        health.UniversalWorkerHealthState.DEGRADED,
        health.create_universal_worker_health_evidence(
            degraded_condition_present=True,
        ),
    ),
    (
        health.UniversalWorkerHealthState.UNHEALTHY,
        health.create_universal_worker_health_evidence(
            critical_failure_present=True,
        ),
    ),
    (
        health.UniversalWorkerHealthState.UNKNOWN,
        health.create_universal_worker_health_evidence(),
    ),
):

    result = (
        health.evaluate_universal_worker_health(
            worker=worker_a,
            evidence=evidence,
        )
    )

    check(
        "result_state_"
        + state_expected.value,
        result.state
        is state_expected,
    )

    check(
        "result_identity_"
        + state_expected.value,
        result.worker_identity
        == (
            "worker-a",
            "instance-001",
        ),
    )

    check(
        "healthy_property_"
        + state_expected.value,
        result.healthy
        is (
            state_expected
            is health.UniversalWorkerHealthState.HEALTHY
        ),
    )


# ============================================================
# 12 — RAW STRING STATE REJECTED
# ============================================================

try:

    health.UniversalWorkerHealthResult(
        worker_id="worker-a",
        worker_instance_id="instance-001",
        state="HEALTHY",
        evidence=valid_evidence,
    )

except health.UniversalWorkerHealthError as exc:

    rejected = (
        exc.code
        == "invalid_worker_health_state"
    )

else:

    rejected = False


check(
    "raw_health_state_string_rejected",
    rejected,
)


# ============================================================
# 13 — RESULT ID ATTACKS
# ============================================================

for field_name in (
    "worker_id",
    "worker_instance_id",
):

    for index, bad in enumerate(
        (
            None,
            True,
            0,
            "",
        ),
        start=1,
    ):

        kwargs = {
            "worker_id":
                "worker-a",

            "worker_instance_id":
                "instance-001",

            "state":
                health.UniversalWorkerHealthState.HEALTHY,

            "evidence":
                valid_evidence,
        }

        kwargs[
            field_name
        ] = bad

        try:

            health.UniversalWorkerHealthResult(
                **kwargs
            )

        except health.UniversalWorkerHealthError:

            rejected = True

        else:

            rejected = False

        check(
            (
                "result_id_attack_"
                + field_name
                + "_"
                + str(index)
            ),
            rejected,
            repr(bad),
        )


# ============================================================
# 14 — INCONSISTENT RESULT ATTACK MATRIX
# ============================================================

evidence_by_expected_state = {
    health.UniversalWorkerHealthState.HEALTHY:
        health.create_universal_worker_health_evidence(
            health_check_passed=True,
        ),

    health.UniversalWorkerHealthState.DEGRADED:
        health.create_universal_worker_health_evidence(
            degraded_condition_present=True,
        ),

    health.UniversalWorkerHealthState.UNHEALTHY:
        health.create_universal_worker_health_evidence(
            critical_failure_present=True,
        ),

    health.UniversalWorkerHealthState.UNKNOWN:
        health.create_universal_worker_health_evidence(),
}


for expected_state_value, evidence in (
    evidence_by_expected_state.items()
):

    for supplied_state in (
        health.UniversalWorkerHealthState
    ):

        should_accept = (
            supplied_state
            is expected_state_value
        )

        try:

            health.UniversalWorkerHealthResult(
                worker_id="worker-a",
                worker_instance_id="instance-001",
                state=supplied_state,
                evidence=evidence,
            )

        except health.UniversalWorkerHealthError as exc:

            accepted = False

            correct_rejection = (
                exc.code
                == "inconsistent_worker_health_result"
            )

        else:

            accepted = True
            correct_rejection = False

        check(
            (
                "result_consistency_"
                + expected_state_value.value
                + "_supplied_"
                + supplied_state.value
            ),
            (
                accepted
                if should_accept
                else correct_rejection
            ),
        )


# ============================================================
# 15 — SCHEMA TAMPERING
# ============================================================

try:

    health.UniversalWorkerHealthEvidence(
        health_check_passed=True,
        schema_version="wrong",
    )

except health.UniversalWorkerHealthError as exc:

    rejected = (
        exc.code
        == "invalid_worker_health_evidence_schema_version"
    )

else:

    rejected = False


check(
    "evidence_schema_tamper_rejected",
    rejected,
)


try:

    health.UniversalWorkerHealthResult(
        worker_id="worker-a",
        worker_instance_id="instance-001",
        state=(
            health.UniversalWorkerHealthState.HEALTHY
        ),
        evidence=valid_evidence,
        schema_version="wrong",
    )

except health.UniversalWorkerHealthError as exc:

    rejected = (
        exc.code
        == "invalid_worker_health_result_schema_version"
    )

else:

    rejected = False


check(
    "result_schema_tamper_rejected",
    rejected,
)


# ============================================================
# 16 — IMMUTABILITY
# ============================================================

immutable_evidence = (
    health.create_universal_worker_health_evidence(
        health_check_passed=True,
    )
)

immutable_result = (
    health.evaluate_universal_worker_health(
        worker=worker_a,
        evidence=immutable_evidence,
    )
)


for obj, field_name in (
    (
        immutable_evidence,
        "health_check_passed",
    ),
    (
        immutable_evidence,
        "critical_failure_present",
    ),
    (
        immutable_evidence,
        "degraded_condition_present",
    ),
    (
        immutable_evidence,
        "schema_version",
    ),
    (
        immutable_result,
        "worker_id",
    ),
    (
        immutable_result,
        "worker_instance_id",
    ),
    (
        immutable_result,
        "state",
    ),
    (
        immutable_result,
        "evidence",
    ),
    (
        immutable_result,
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
# 17 — WORKER REGISTRATION NOT MUTATED
# ============================================================

worker_before = (
    worker_a.to_dict()
)


for evidence in (
    health.create_universal_worker_health_evidence(),
    health.create_universal_worker_health_evidence(
        health_check_passed=True,
    ),
    health.create_universal_worker_health_evidence(
        degraded_condition_present=True,
    ),
    health.create_universal_worker_health_evidence(
        critical_failure_present=True,
    ),
):

    health.evaluate_universal_worker_health(
        worker=worker_a,
        evidence=evidence,
    )


check(
    "worker_registration_not_mutated",
    worker_a.to_dict()
    == worker_before,
)


# ============================================================
# 18 — DETERMINISM
# ============================================================

deterministic_evidence = (
    health.create_universal_worker_health_evidence(
        health_check_passed=True,
        critical_failure_present=False,
        degraded_condition_present=True,
    )
)


result_1 = (
    health.evaluate_universal_worker_health(
        worker=worker_a,
        evidence=deterministic_evidence,
    )
)

result_2 = (
    health.evaluate_universal_worker_health(
        worker=worker_a,
        evidence=deterministic_evidence,
    )
)


check(
    "deterministic_result",
    result_1
    == result_2,
)


# ============================================================
# 19 — EXPLANATION CONTRACT
# ============================================================

explanation = (
    health.explain_universal_worker_health_v1()
)


check(
    "explanation_phase",
    explanation.get("phase")
    == "4.1.5",
)

check(
    "explanation_component",
    explanation.get("component")
    == "Universal Worker Health",
)

check(
    "explanation_version",
    explanation.get("version")
    == health.UNIVERSAL_WORKER_HEALTH_VERSION,
)

check(
    "evidence_schema_explained",
    explanation.get(
        "evidence_schema_version"
    )
    == health.UNIVERSAL_WORKER_HEALTH_EVIDENCE_SCHEMA_VERSION,
)

check(
    "result_schema_explained",
    explanation.get(
        "result_schema_version"
    )
    == health.UNIVERSAL_WORKER_HEALTH_RESULT_SCHEMA_VERSION,
)

check(
    "states_explained_exact",
    tuple(
        explanation.get("states")
    )
    == (
        "HEALTHY",
        "DEGRADED",
        "UNHEALTHY",
        "UNKNOWN",
    ),
)

check(
    "caller_supplied_rule",
    "caller-supplied health evidence"
    in explanation.get(
        "input_rule",
        "",
    ),
)

check(
    "none_is_unsupplied",
    "None means evidence not supplied"
    in explanation.get(
        "evidence_rule",
        "",
    ),
)

check(
    "critical_precedence_explained",
    "critical failure -> UNHEALTHY"
    in explanation.get(
        "precedence_rule",
        "",
    ),
)

check(
    "failed_check_precedence_explained",
    "failed health check -> UNHEALTHY"
    in explanation.get(
        "precedence_rule",
        "",
    ),
)

check(
    "degraded_precedence_explained",
    "degraded condition -> DEGRADED"
    in explanation.get(
        "precedence_rule",
        "",
    ),
)

check(
    "healthy_precedence_explained",
    "passed health check -> HEALTHY"
    in explanation.get(
        "precedence_rule",
        "",
    ),
)

check(
    "unknown_precedence_explained",
    "otherwise -> UNKNOWN"
    in explanation.get(
        "precedence_rule",
        "",
    ),
)

check(
    "unknown_rule_exact",
    "must not be interpreted as HEALTHY"
    in explanation.get(
        "unknown_rule",
        "",
    ),
)

check(
    "operational_status_boundary",
    "not Worker Health states"
    in explanation.get(
        "operational_status_boundary",
        "",
    ),
)

check(
    "heartbeat_boundary",
    "outside 4.1.5"
    in explanation.get(
        "heartbeat_boundary",
        "",
    ),
)

check(
    "availability_boundary",
    (
        "available"
        in explanation.get(
            "availability_boundary",
            "",
        )
        and
        "eligible"
        in explanation.get(
            "availability_boundary",
            "",
        )
        and
        "assignable"
        in explanation.get(
            "availability_boundary",
            "",
        )
    ),
)

check(
    "telemetry_boundary",
    (
        "CPU"
        in explanation.get(
            "telemetry_boundary",
            "",
        )
        and
        "latency"
        in explanation.get(
            "telemetry_boundary",
            "",
        )
        and
        "error-rate"
        in explanation.get(
            "telemetry_boundary",
            "",
        )
    ),
)

check(
    "recovery_boundary",
    (
        "restart"
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
        "drain"
        in explanation.get(
            "recovery_boundary",
            "",
        )
        and
        "shut down"
        in explanation.get(
            "recovery_boundary",
            "",
        )
    ),
)

check(
    "purity_boundary",
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
    "does not emit worker heartbeats",
    "does not read worker heartbeats",
    "does not calculate heartbeat freshness",
    "does not detect stale workers",
    "does not determine worker liveness",
    "does not determine worker readiness",
    "does not inspect ACTIVE IDLE BUSY OFFLINE FAILED operational status",
    "does not determine worker availability",
    "does not determine assignment eligibility",
    "does not assign workers",
    "does not acquire leases",
    "does not renew leases",
    "does not release leases",
    "does not inspect worker capacity",
    "does not inspect worker capabilities",
    "does not inspect worker pools",
    "does not invent CPU thresholds",
    "does not invent memory thresholds",
    "does not invent latency thresholds",
    "does not invent error-rate thresholds",
    "does not restart workers",
    "does not recover workers",
    "does not scale workers",
    "does not drain workers",
    "does not shut down workers",
    "does not access Runtime State Store",
    "does not access orchestration",
    "does not mutate Queue Infrastructure",
    "does not persist health results",
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

source = HEALTH_PATH.read_text(
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
    "only_registration_backend_import",
    backend_imports
    == [
        "backend.server.runtime.universal_worker.registration"
    ],
    backend_imports,
)


# ============================================================
# 22 — FORBIDDEN CALLS
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
    "get_latest_worker_statuses",
    "get_runtime_state_store_registry",
    "assign_universal_worker",
    "acquire_universal_worker_lease",
    "renew_universal_worker_lease",
    "release_universal_worker_lease",
    "dispatch_job",
    "execute_job",
    "recover_worker",
    "restart_worker",
    "scale_worker",
    "drain_worker",
    "shutdown_worker",
    "save_job",
    "get_job",
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
# 23 — NO RESPONSIBILITY BLEED
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
    "heartbeat",
    "freshness",
    "stale",
    "liveness",
    "readiness",
    "availability",
    "eligible",
    "assign",
    "lease",
    "capacity",
    "capability",
    "pool",
    "restart",
    "recover",
    "scale",
    "drain",
    "shutdown",
    "persist",
    "state_store",
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
# 24 — NO TELEMETRY THRESHOLD CONSTANTS
# ============================================================

constant_assignments = []


for node in tree.body:

    if isinstance(
        node,
        ast.Assign,
    ):

        for target in node.targets:

            if isinstance(
                target,
                ast.Name,
            ):

                name = (
                    target.id.upper()
                )

                if any(
                    token in name
                    for token in (
                        "CPU",
                        "MEMORY",
                        "LATENCY",
                        "ERROR_RATE",
                        "FAILURE_RATE",
                        "THRESHOLD",
                    )
                ):

                    constant_assignments.append(
                        (
                            target.id,
                            node.lineno,
                        )
                    )


check(
    "no_telemetry_threshold_constants",
    not constant_assignments,
    constant_assignments,
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
# 26 — FINAL HEALTH AST
# ============================================================

final_ast = ast_sha(
    HEALTH_PATH
)


check(
    "health_ast_final",
    final_ast
    == EXPECTED_HEALTH_AST,
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
        "PHASE 4.1.5 — UNIVERSAL WORKER "
        "HEALTH ADVERSARIAL REGRESSION"
    ),
    "=" * 112,
    "",
    (
        "WORKER HEALTH AST SHA256: "
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
            "ADVERSARIAL WORKER HEALTH REGRESSION: "
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
        "WORKER HEALTH AST MODIFIED: NO",
        "4.1.1 WORKER REGISTRATION MODIFIED: NO",
        "4.1.2 WORKER DISCOVERY MODIFIED: NO",
        "4.1.3 WORKER ASSIGNMENT MODIFIED: NO",
        "4.1.4 WORKER LEASING MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "EXISTING UNIVERSAL RUNTIME WORKER MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "WORKER HEARTBEAT READ OR WRITTEN: NO",
        "HEARTBEAT FRESHNESS CALCULATED: NO",
        "STALE WORKER DETECTION PERFORMED: NO",
        "WORKER LIVENESS DECIDED: NO",
        "WORKER READINESS DECIDED: NO",
        "WORKER AVAILABILITY DECIDED: NO",
        "WORKER ASSIGNMENT ELIGIBILITY DECIDED: NO",
        "WORKER CAPACITY INSPECTED: NO",
        "WORKER CAPABILITY INSPECTED: NO",
        "WORKER POOL INSPECTED: NO",
        "TELEMETRY THRESHOLDS INVENTED: NO",
        "WORKER RECOVERY PERFORMED: NO",
        "WORKER RESTARTED: NO",
        "WORKER SCALED: NO",
        "WORKER DRAINED: NO",
        "WORKER SHUT DOWN: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "HEALTH RESULT PERSISTED: NO",
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
        "Phase 4.1.5 Worker Health adversarial regression failed."
    )
