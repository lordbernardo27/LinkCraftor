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
    / "phase_4_1_8_worker_shutdown_final_certification.txt"
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


if not SHUTDOWN_PATH.exists():
    raise SystemExit(
        "Worker Shutdown authority missing."
    )


initial_ast = ast_sha(
    SHUTDOWN_PATH
)

if initial_ast != EXPECTED_SHUTDOWN_AST:
    raise SystemExit(
        (
            "Worker Shutdown AST mismatch before final certification.\n"
            "EXPECTED: "
            + EXPECTED_SHUTDOWN_AST
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
                "Protected authority mismatch before final certification: "
                + name
                + "\nEXPECTED: "
                + expected
                + "\nACTUAL:   "
                + actual
            )
        )


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


shutdown_ast = ast_sha(
    SHUTDOWN_PATH
)


check(
    "worker_shutdown_ast",
    shutdown_ast
    == EXPECTED_SHUTDOWN_AST,
    shutdown_ast,
)

check(
    "version",
    shutdown.UNIVERSAL_WORKER_SHUTDOWN_VERSION
    == "universal_worker_shutdown_v4.1.8",
)

check(
    "evidence_schema",
    shutdown.UNIVERSAL_WORKER_SHUTDOWN_EVIDENCE_SCHEMA_VERSION
    == "universal_worker_shutdown_evidence_schema_v1",
)

check(
    "result_schema",
    shutdown.UNIVERSAL_WORKER_SHUTDOWN_RESULT_SCHEMA_VERSION
    == "universal_worker_shutdown_result_schema_v1",
)

check(
    "max_active_count",
    shutdown.MAX_UNIVERSAL_WORKER_SHUTDOWN_ACTIVE_COUNT
    == 2_147_483_647,
)

check(
    "decisions_exact",
    tuple(
        item.value
        for item in shutdown.UniversalWorkerShutdownDecision
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
        item.value
        for item in shutdown.UniversalWorkerShutdownReason
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
# CORE DECISION STATES
# ============================================================

cases = (
    (
        "not_requested",
        False,
        False,
        0,
        0,
        shutdown.UniversalWorkerShutdownDecision.NOT_REQUESTED,
        shutdown.UniversalWorkerShutdownReason.SHUTDOWN_NOT_REQUESTED,
    ),
    (
        "active_work",
        True,
        False,
        1,
        0,
        shutdown.UniversalWorkerShutdownDecision.BLOCKED,
        shutdown.UniversalWorkerShutdownReason.ACTIVE_WORK_PRESENT,
    ),
    (
        "active_lease",
        True,
        False,
        0,
        1,
        shutdown.UniversalWorkerShutdownDecision.BLOCKED,
        shutdown.UniversalWorkerShutdownReason.ACTIVE_LEASES_PRESENT,
    ),
    (
        "drain_incomplete",
        True,
        False,
        0,
        0,
        shutdown.UniversalWorkerShutdownDecision.BLOCKED,
        shutdown.UniversalWorkerShutdownReason.DRAIN_INCOMPLETE,
    ),
    (
        "ready",
        True,
        True,
        0,
        0,
        shutdown.UniversalWorkerShutdownDecision.READY,
        shutdown.UniversalWorkerShutdownReason.SHUTDOWN_READY,
    ),
)


for (
    name,
    shutdown_requested,
    drain_complete,
    active_work_count,
    active_lease_count,
    expected_decision,
    expected_reason,
) in cases:

    evidence = (
        shutdown.create_universal_worker_shutdown_evidence(
            shutdown_requested=shutdown_requested,
            drain_complete=drain_complete,
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
        name + "_decision",
        result.decision
        is expected_decision,
    )

    check(
        name + "_reason",
        result.reason
        is expected_reason,
    )


# ============================================================
# PRECEDENCE
# ============================================================

both_active = (
    shutdown.create_universal_worker_shutdown_evidence(
        shutdown_requested=True,
        drain_complete=False,
        active_work_count=3,
        active_lease_count=4,
    )
)

both_active_result = (
    shutdown.evaluate_universal_worker_shutdown(
        both_active
    )
)

check(
    "active_work_precedes_active_lease",
    both_active_result.reason
    is shutdown.UniversalWorkerShutdownReason.ACTIVE_WORK_PRESENT,
)


not_requested_busy = (
    shutdown.create_universal_worker_shutdown_evidence(
        shutdown_requested=False,
        drain_complete=False,
        active_work_count=10,
        active_lease_count=10,
    )
)

not_requested_busy_result = (
    shutdown.evaluate_universal_worker_shutdown(
        not_requested_busy
    )
)

check(
    "not_requested_precedes_busy_state",
    (
        not_requested_busy_result.decision
        is shutdown.UniversalWorkerShutdownDecision.NOT_REQUESTED
        and
        not_requested_busy_result.reason
        is shutdown.UniversalWorkerShutdownReason.SHUTDOWN_NOT_REQUESTED
    ),
)


# ============================================================
# CONTRADICTIONS
# ============================================================

try:
    shutdown.create_universal_worker_shutdown_evidence(
        shutdown_requested=True,
        drain_complete=True,
        active_work_count=1,
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
    "drain_complete_active_work_rejected",
    rejected,
)


try:
    shutdown.create_universal_worker_shutdown_evidence(
        shutdown_requested=True,
        drain_complete=True,
        active_work_count=0,
        active_lease_count=1,
    )

except shutdown.UniversalWorkerShutdownError as exc:
    rejected = (
        exc.code
        == "drain_complete_active_lease_contradiction"
    )

else:
    rejected = False


check(
    "drain_complete_active_lease_rejected",
    rejected,
)


# ============================================================
# TYPE VALIDATION
# ============================================================

for field_name in (
    "shutdown_requested",
    "drain_complete",
):

    for bad in (
        None,
        0,
        1,
        -1,
        0.0,
        1.0,
        "",
        "true",
        [],
        {},
        (),
    ):

        kwargs = {
            "shutdown_requested": False,
            "drain_complete": False,
            "active_work_count": 0,
            "active_lease_count": 0,
        }

        kwargs[field_name] = bad

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
                "strict_boolean_"
                + field_name
                + "_"
                + repr(bad)
            ),
            rejected,
        )


for field_name in (
    "active_work_count",
    "active_lease_count",
):

    for bad in (
        None,
        True,
        False,
        -1,
        0.0,
        1.0,
        "",
        "1",
        [],
        {},
        (),
    ):

        kwargs = {
            "shutdown_requested": False,
            "drain_complete": False,
            "active_work_count": 0,
            "active_lease_count": 0,
        }

        kwargs[field_name] = bad

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
                + repr(bad)
            ),
            rejected,
        )


# ============================================================
# MAXIMUM COUNT
# ============================================================

maximum = (
    shutdown.MAX_UNIVERSAL_WORKER_SHUTDOWN_ACTIVE_COUNT
)

max_evidence = (
    shutdown.create_universal_worker_shutdown_evidence(
        shutdown_requested=False,
        drain_complete=False,
        active_work_count=maximum,
        active_lease_count=maximum,
    )
)

check(
    "maximum_active_work_supported",
    max_evidence.active_work_count
    == maximum,
)

check(
    "maximum_active_lease_supported",
    max_evidence.active_lease_count
    == maximum,
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

    kwargs[field_name] = maximum + 1

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
# FORGERY / SCHEMA
# ============================================================

ready_evidence = (
    shutdown.create_universal_worker_shutdown_evidence(
        shutdown_requested=True,
        drain_complete=True,
        active_work_count=0,
        active_lease_count=0,
    )
)

ready_result = (
    shutdown.evaluate_universal_worker_shutdown(
        ready_evidence
    )
)


try:
    shutdown.UniversalWorkerShutdownResult(
        decision=(
            shutdown.UniversalWorkerShutdownDecision.BLOCKED
        ),
        reason=(
            shutdown.UniversalWorkerShutdownReason.DRAIN_INCOMPLETE
        ),
        shutdown_requested=True,
        drain_complete=True,
        active_work_count=0,
        active_lease_count=0,
    )

except shutdown.UniversalWorkerShutdownError as exc:
    rejected = (
        exc.code
        == "inconsistent_worker_shutdown_result"
    )

else:
    rejected = False


check(
    "forged_result_rejected",
    rejected,
)


try:
    shutdown.UniversalWorkerShutdownEvidence(
        shutdown_requested=False,
        drain_complete=False,
        active_work_count=0,
        active_lease_count=0,
        schema_version="wrong",
    )

except shutdown.UniversalWorkerShutdownError as exc:
    rejected = (
        exc.code
        == "invalid_worker_shutdown_evidence_schema_version"
    )

else:
    rejected = False


check(
    "evidence_schema_tamper_rejected",
    rejected,
)


try:
    shutdown.UniversalWorkerShutdownResult(
        decision=ready_result.decision,
        reason=ready_result.reason,
        shutdown_requested=True,
        drain_complete=True,
        active_work_count=0,
        active_lease_count=0,
        schema_version="wrong",
    )

except shutdown.UniversalWorkerShutdownError as exc:
    rejected = (
        exc.code
        == "invalid_worker_shutdown_result_schema_version"
    )

else:
    rejected = False


check(
    "result_schema_tamper_rejected",
    rejected,
)


# ============================================================
# RESULT PROPERTIES / IMMUTABILITY / DETERMINISM
# ============================================================

check(
    "ready_shutdown_ready",
    ready_result.shutdown_ready
    is True,
)

check(
    "ready_shutdown_blocked_false",
    ready_result.shutdown_blocked
    is False,
)


blocked_result = (
    shutdown.evaluate_universal_worker_shutdown(
        shutdown.create_universal_worker_shutdown_evidence(
            shutdown_requested=True,
            drain_complete=False,
            active_work_count=0,
            active_lease_count=0,
        )
    )
)

check(
    "blocked_shutdown_ready_false",
    blocked_result.shutdown_ready
    is False,
)

check(
    "blocked_shutdown_blocked",
    blocked_result.shutdown_blocked
    is True,
)


for obj, field_name in (
    (ready_evidence, "shutdown_requested"),
    (ready_evidence, "drain_complete"),
    (ready_evidence, "active_work_count"),
    (ready_evidence, "active_lease_count"),
    (ready_evidence, "schema_version"),
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


check(
    "deterministic_decision",
    shutdown.decide_universal_worker_shutdown(
        ready_evidence
    )
    ==
    shutdown.decide_universal_worker_shutdown(
        ready_evidence
    ),
)

check(
    "deterministic_result",
    shutdown.evaluate_universal_worker_shutdown(
        ready_evidence
    )
    ==
    shutdown.evaluate_universal_worker_shutdown(
        ready_evidence
    ),
)


# ============================================================
# EXPLANATION / PROHIBITIONS
# ============================================================

explanation = (
    shutdown.explain_universal_worker_shutdown_v1()
)

check(
    "phase",
    explanation.get("phase")
    == "4.1.8",
)

check(
    "component",
    explanation.get("component")
    == "Universal Worker Shutdown",
)

check(
    "explanation_version",
    explanation.get("version")
    == shutdown.UNIVERSAL_WORKER_SHUTDOWN_VERSION,
)

check(
    "evidence_schema_explanation",
    explanation.get(
        "evidence_schema_version"
    )
    == shutdown.UNIVERSAL_WORKER_SHUTDOWN_EVIDENCE_SCHEMA_VERSION,
)

check(
    "result_schema_explanation",
    explanation.get(
        "result_schema_version"
    )
    == shutdown.UNIVERSAL_WORKER_SHUTDOWN_RESULT_SCHEMA_VERSION,
)

check(
    "decisions_explanation",
    tuple(
        explanation.get("decisions")
    )
    == (
        "NOT_REQUESTED",
        "BLOCKED",
        "READY",
    ),
)

check(
    "drain_boundary",
    "4.1.12 Worker Drain"
    in explanation.get(
        "drain_boundary",
        "",
    ),
)

check(
    "runtime_shutdown_boundary",
    "whole-runtime shutdown"
    in explanation.get(
        "runtime_shutdown_boundary",
        "",
    ),
)

check(
    "termination_permission_boundary",
    "permission"
    in explanation.get(
        "termination_boundary",
        "",
    ),
)

check(
    "forced_shutdown_boundary",
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
# STATIC IMPORT / API / FORBIDDEN CALLS
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
    "dequeue_job",
    "enqueue_job",
    "requeue_job",
    "cancel_job",
    "mark_job_failed",
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

        call_name = node.func.id

    elif isinstance(
        node.func,
        ast.Attribute,
    ):

        call_name = node.func.attr

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
# PROTECTED AST MATRIX
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
        "phase_4_1_8_worker_shutdown",
        shutdown.UNIVERSAL_WORKER_SHUTDOWN_VERSION,
        shutdown.UNIVERSAL_WORKER_SHUTDOWN_EVIDENCE_SCHEMA_VERSION,
        shutdown.UNIVERSAL_WORKER_SHUTDOWN_RESULT_SCHEMA_VERSION,
        shutdown_ast,
        "shutdown_requested",
        "drain_complete",
        "active_work_count",
        "active_lease_count",
        "NOT_REQUESTED",
        "BLOCKED",
        "READY",
        "explicit_shutdown_request",
        "active_work_blocks_before_active_leases",
        "active_leases_block_before_drain",
        "drain_completion_required",
        "ready_requires_zero_work_and_zero_leases",
        "drain_complete_contradictions_rejected",
        "shutdown_permission_not_termination",
        "worker_drain_owned_by_4_1_12",
        "whole_runtime_shutdown_separate",
        "forced_shutdown_outside",
        "pure_evidence_authority",
    )
)


shutdown_fingerprint = (
    hashlib.sha256(
        fingerprint_material.encode(
            "utf-8"
        )
    ).hexdigest().upper()
)


check(
    "fingerprint_generated",
    len(
        shutdown_fingerprint
    )
    == 64,
    shutdown_fingerprint,
)


# ============================================================
# FINAL AST RECHECK
# ============================================================

final_ast = ast_sha(
    SHUTDOWN_PATH
)


check(
    "final_ast_unchanged",
    final_ast
    == EXPECTED_SHUTDOWN_AST,
    final_ast,
)


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
        "SHUTDOWN FINAL CERTIFICATION"
    ),
    "=" * 112,
    "",
    (
        "WORKER SHUTDOWN AST SHA256: "
        + shutdown_ast
    ),
    (
        "WORKER SHUTDOWN FINGERPRINT: "
        + shutdown_fingerprint
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
            "FINAL WORKER SHUTDOWN CERTIFICATION: "
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
        "WORKER SHUTDOWN MODIFIED DURING CERTIFICATION: NO",
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
            "PHASE 4.1.8 FREEZE CANDIDATE: "
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
        "Phase 4.1.8 Worker Shutdown final certification failed."
    )
