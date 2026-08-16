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
    / "phase_4_1_5_worker_health_final_certification.txt"
)

EXPECTED_HEALTH_AST = (
    "DCC43E77BDC12188DFD15044DA4DA41022B3CEF40F9C4ED06371EE66AA4E5F65"
)


# ============================================================
# PROTECTED FROZEN AUTHORITIES
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


# ============================================================
# IMPORT AUTHORITIES
# ============================================================

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
# 1 — AST
# ============================================================

health_ast = ast_sha(
    HEALTH_PATH
)

check(
    "worker_health_ast",
    health_ast
    == EXPECTED_HEALTH_AST,
    health_ast,
)


# ============================================================
# 2 — VERSION / SCHEMAS / STATES
# ============================================================

check(
    "version",
    health.UNIVERSAL_WORKER_HEALTH_VERSION
    == "universal_worker_health_v4.1.5",
)

check(
    "evidence_schema",
    health.UNIVERSAL_WORKER_HEALTH_EVIDENCE_SCHEMA_VERSION
    == "universal_worker_health_evidence_schema_v1",
)

check(
    "result_schema",
    health.UNIVERSAL_WORKER_HEALTH_RESULT_SCHEMA_VERSION
    == "universal_worker_health_result_schema_v1",
)

check(
    "states_exact",
    tuple(
        item.value
        for item in health.UniversalWorkerHealthState
    )
    == (
        "HEALTHY",
        "DEGRADED",
        "UNHEALTHY",
        "UNKNOWN",
    ),
)


# ============================================================
# 3 — CANONICAL WORKER
# ============================================================

worker = (
    registration.create_universal_worker_registration(
        worker_id="worker-a",
        worker_type="general",
        worker_instance_id="instance-001",
        runtime_version="runtime-v1",
        host_id="host-a",
        registered_at="2026-08-15T20:00:00Z",
    )
)


# ============================================================
# 4 — CANONICAL EVIDENCE
# ============================================================

healthy_evidence = (
    health.create_universal_worker_health_evidence(
        health_check_passed=True,
    )
)

degraded_evidence = (
    health.create_universal_worker_health_evidence(
        health_check_passed=True,
        degraded_condition_present=True,
    )
)

unhealthy_critical_evidence = (
    health.create_universal_worker_health_evidence(
        health_check_passed=True,
        critical_failure_present=True,
        degraded_condition_present=True,
    )
)

unhealthy_failed_check = (
    health.create_universal_worker_health_evidence(
        health_check_passed=False,
    )
)

unknown_evidence = (
    health.create_universal_worker_health_evidence()
)


check(
    "healthy_state",
    health.classify_universal_worker_health_evidence(
        healthy_evidence
    )
    is health.UniversalWorkerHealthState.HEALTHY,
)

check(
    "degraded_state",
    health.classify_universal_worker_health_evidence(
        degraded_evidence
    )
    is health.UniversalWorkerHealthState.DEGRADED,
)

check(
    "critical_unhealthy_state",
    health.classify_universal_worker_health_evidence(
        unhealthy_critical_evidence
    )
    is health.UniversalWorkerHealthState.UNHEALTHY,
)

check(
    "failed_check_unhealthy_state",
    health.classify_universal_worker_health_evidence(
        unhealthy_failed_check
    )
    is health.UniversalWorkerHealthState.UNHEALTHY,
)

check(
    "unknown_state",
    health.classify_universal_worker_health_evidence(
        unknown_evidence
    )
    is health.UniversalWorkerHealthState.UNKNOWN,
)


# ============================================================
# 5 — COMPLETE 27-COMBINATION PRECEDENCE MATRIX
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
            f"{passed_signal!r},"
            f"{critical_signal!r},"
            f"{degraded_signal!r}"
            f" -> {actual.value}"
        ),
    )


# ============================================================
# 6 — UNKNOWN MUST NOT BE PROMOTED
# ============================================================

negative_only = (
    health.create_universal_worker_health_evidence(
        critical_failure_present=False,
        degraded_condition_present=False,
    )
)


check(
    "negative_only_is_unknown",
    health.classify_universal_worker_health_evidence(
        negative_only
    )
    is health.UniversalWorkerHealthState.UNKNOWN,
)


check(
    "empty_signal_count_zero",
    unknown_evidence.supplied_signal_count
    == 0,
)

check(
    "negative_only_signal_count_two",
    negative_only.supplied_signal_count
    == 2,
)


# ============================================================
# 7 — CANONICAL RESULT
# ============================================================

result = (
    health.evaluate_universal_worker_health(
        worker=worker,
        evidence=degraded_evidence,
    )
)


check(
    "result_worker_identity",
    result.worker_identity
    == (
        "worker-a",
        "instance-001",
    ),
)

check(
    "result_state",
    result.state
    is health.UniversalWorkerHealthState.DEGRADED,
)

check(
    "result_evidence",
    result.evidence
    is degraded_evidence,
)

check(
    "degraded_not_healthy",
    result.healthy
    is False,
)


healthy_result = (
    health.evaluate_universal_worker_health(
        worker=worker,
        evidence=healthy_evidence,
    )
)


check(
    "healthy_property_true_only_for_healthy",
    healthy_result.healthy
    is True,
)


# ============================================================
# 8 — STRICT SIGNAL VALIDATION
# ============================================================

for field_name in (
    "health_check_passed",
    "critical_failure_present",
    "degraded_condition_present",
):

    for bad in (
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
    ):

        kwargs = {
            "health_check_passed": None,
            "critical_failure_present": None,
            "degraded_condition_present": None,
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
                "strict_signal_"
                + field_name
                + "_"
                + type(bad).__name__
                + "_"
                + repr(bad)
            ),
            rejected,
        )


# ============================================================
# 9 — SCHEMA TAMPERING
# ============================================================

try:

    health.UniversalWorkerHealthEvidence(
        health_check_passed=True,
        schema_version="tampered",
    )

except health.UniversalWorkerHealthError as exc:

    evidence_schema_rejected = (
        exc.code
        == "invalid_worker_health_evidence_schema_version"
    )

else:

    evidence_schema_rejected = False


check(
    "evidence_schema_tampering_rejected",
    evidence_schema_rejected,
)


try:

    health.UniversalWorkerHealthResult(
        worker_id="worker-a",
        worker_instance_id="instance-001",
        state=(
            health.UniversalWorkerHealthState.HEALTHY
        ),
        evidence=healthy_evidence,
        schema_version="tampered",
    )

except health.UniversalWorkerHealthError as exc:

    result_schema_rejected = (
        exc.code
        == "invalid_worker_health_result_schema_version"
    )

else:

    result_schema_rejected = False


check(
    "result_schema_tampering_rejected",
    result_schema_rejected,
)


# ============================================================
# 10 — RESULT FORGERY PROTECTION
# ============================================================

try:

    health.UniversalWorkerHealthResult(
        worker_id="worker-a",
        worker_instance_id="instance-001",
        state=(
            health.UniversalWorkerHealthState.HEALTHY
        ),
        evidence=unhealthy_critical_evidence,
    )

except health.UniversalWorkerHealthError as exc:

    forged_result_rejected = (
        exc.code
        == "inconsistent_worker_health_result"
    )

else:

    forged_result_rejected = False


check(
    "forged_result_rejected",
    forged_result_rejected,
)


try:

    health.UniversalWorkerHealthResult(
        worker_id="worker-a",
        worker_instance_id="instance-001",
        state="HEALTHY",
        evidence=healthy_evidence,
    )

except health.UniversalWorkerHealthError as exc:

    raw_state_rejected = (
        exc.code
        == "invalid_worker_health_state"
    )

else:

    raw_state_rejected = False


check(
    "raw_state_rejected",
    raw_state_rejected,
)


# ============================================================
# 11 — IMMUTABILITY
# ============================================================

for obj, field_name in (
    (
        healthy_evidence,
        "health_check_passed",
    ),
    (
        healthy_evidence,
        "critical_failure_present",
    ),
    (
        healthy_evidence,
        "degraded_condition_present",
    ),
    (
        healthy_evidence,
        "schema_version",
    ),
    (
        result,
        "worker_id",
    ),
    (
        result,
        "worker_instance_id",
    ),
    (
        result,
        "state",
    ),
    (
        result,
        "evidence",
    ),
    (
        result,
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
# 12 — REGISTRATION NOT MUTATED
# ============================================================

worker_before = (
    worker.to_dict()
)


for evidence in (
    healthy_evidence,
    degraded_evidence,
    unhealthy_critical_evidence,
    unhealthy_failed_check,
    unknown_evidence,
):

    health.evaluate_universal_worker_health(
        worker=worker,
        evidence=evidence,
    )


check(
    "worker_registration_not_mutated",
    worker.to_dict()
    == worker_before,
)


# ============================================================
# 13 — DETERMINISM
# ============================================================

deterministic_evidence = (
    health.create_universal_worker_health_evidence(
        health_check_passed=True,
        critical_failure_present=False,
        degraded_condition_present=True,
    )
)


first = (
    health.evaluate_universal_worker_health(
        worker=worker,
        evidence=deterministic_evidence,
    )
)

second = (
    health.evaluate_universal_worker_health(
        worker=worker,
        evidence=deterministic_evidence,
    )
)


check(
    "deterministic_result",
    first
    == second,
)


# ============================================================
# 14 — EXPLANATION CONTRACT
# ============================================================

explanation = (
    health.explain_universal_worker_health_v1()
)


check(
    "phase",
    explanation.get("phase")
    == "4.1.5",
)

check(
    "component",
    explanation.get("component")
    == "Universal Worker Health",
)

check(
    "explanation_version",
    explanation.get("version")
    == health.UNIVERSAL_WORKER_HEALTH_VERSION,
)

check(
    "evidence_schema_explanation",
    explanation.get(
        "evidence_schema_version"
    )
    == health.UNIVERSAL_WORKER_HEALTH_EVIDENCE_SCHEMA_VERSION,
)

check(
    "result_schema_explanation",
    explanation.get(
        "result_schema_version"
    )
    == health.UNIVERSAL_WORKER_HEALTH_RESULT_SCHEMA_VERSION,
)

check(
    "states_explanation",
    tuple(
        explanation.get(
            "states"
        )
    )
    == (
        "HEALTHY",
        "DEGRADED",
        "UNHEALTHY",
        "UNKNOWN",
    ),
)

check(
    "caller_evidence_rule",
    "caller-supplied health evidence"
    in explanation.get(
        "input_rule",
        "",
    ),
)

check(
    "optional_signal_rule",
    "None means evidence not supplied"
    in explanation.get(
        "evidence_rule",
        "",
    ),
)

check(
    "critical_precedence",
    "critical failure -> UNHEALTHY"
    in explanation.get(
        "precedence_rule",
        "",
    ),
)

check(
    "failed_check_precedence",
    "failed health check -> UNHEALTHY"
    in explanation.get(
        "precedence_rule",
        "",
    ),
)

check(
    "degraded_precedence",
    "degraded condition -> DEGRADED"
    in explanation.get(
        "precedence_rule",
        "",
    ),
)

check(
    "healthy_precedence",
    "passed health check -> HEALTHY"
    in explanation.get(
        "precedence_rule",
        "",
    ),
)

check(
    "unknown_precedence",
    "otherwise -> UNKNOWN"
    in explanation.get(
        "precedence_rule",
        "",
    ),
)

check(
    "unknown_is_not_healthy_rule",
    "must not be interpreted as HEALTHY"
    in explanation.get(
        "unknown_rule",
        "",
    ),
)

check(
    "operational_state_boundary",
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
    "telemetry_threshold_boundary",
    "does not invent"
    in explanation.get(
        "telemetry_boundary",
        "",
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
        "replace"
        in explanation.get(
            "recovery_boundary",
            "",
        )
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
# 15 — PROHIBITIONS
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
# 16 — STATIC IMPORT BOUNDARY
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
    "only_worker_registration_imported",
    backend_imports
    == [
        "backend.server.runtime.universal_worker.registration"
    ],
    backend_imports,
)


# ============================================================
# 17 — FORBIDDEN CALL BOUNDARY
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
# 18 — LATER RESPONSIBILITY EXCLUSION
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
# 19 — NO TELEMETRY POLICY INVENTION
# ============================================================

telemetry_constants = []


for node in tree.body:

    if not isinstance(
        node,
        ast.Assign,
    ):

        continue

    for target in node.targets:

        if not isinstance(
            target,
            ast.Name,
        ):

            continue

        upper = (
            target.id.upper()
        )

        if any(
            token in upper
            for token in (
                "CPU",
                "MEMORY",
                "LATENCY",
                "ERROR_RATE",
                "FAILURE_RATE",
                "THRESHOLD",
            )
        ):

            telemetry_constants.append(
                (
                    target.id,
                    node.lineno,
                )
            )


check(
    "no_telemetry_threshold_constants",
    not telemetry_constants,
    telemetry_constants,
)


# ============================================================
# 20 — PROTECTED AST MATRIX
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
# 21 — CANONICAL FINGERPRINT
# ============================================================

fingerprint_material = "|".join(
    (
        "phase_4_1_5_worker_health",
        health.UNIVERSAL_WORKER_HEALTH_VERSION,
        health.UNIVERSAL_WORKER_HEALTH_EVIDENCE_SCHEMA_VERSION,
        health.UNIVERSAL_WORKER_HEALTH_RESULT_SCHEMA_VERSION,
        health_ast,
        "health_check_passed",
        "critical_failure_present",
        "degraded_condition_present",
        "HEALTHY",
        "DEGRADED",
        "UNHEALTHY",
        "UNKNOWN",
        "critical_failure_then_failed_check_then_degraded_then_pass_then_unknown",
        "health_not_liveness",
        "health_not_availability",
        "health_not_recovery",
    )
)


health_fingerprint = (
    hashlib.sha256(
        fingerprint_material.encode(
            "utf-8"
        )
    ).hexdigest().upper()
)


check(
    "fingerprint_generated",
    len(
        health_fingerprint
    )
    == 64,
    health_fingerprint,
)


# ============================================================
# 22 — FINAL AST RECHECK
# ============================================================

final_ast = ast_sha(
    HEALTH_PATH
)


check(
    "final_ast_unchanged",
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
        "HEALTH FINAL CERTIFICATION"
    ),
    "=" * 112,
    "",
    (
        "WORKER HEALTH AST SHA256: "
        + health_ast
    ),
    (
        "WORKER HEALTH FINGERPRINT: "
        + health_fingerprint
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
            "FINAL WORKER HEALTH CERTIFICATION: "
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
        "WORKER HEALTH MODIFIED DURING CERTIFICATION: NO",
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
            "PHASE 4.1.5 FREEZE CANDIDATE: "
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
        "Phase 4.1.5 Worker Health final certification failed."
    )
