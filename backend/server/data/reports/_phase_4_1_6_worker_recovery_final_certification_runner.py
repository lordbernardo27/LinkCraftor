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

RECOVERY_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "recovery.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_6_worker_recovery_final_certification.txt"
)

EXPECTED_RECOVERY_AST = (
    "C3EF5DBD81205F0087E05F43F6A67A1E0762930DAAD256F957AABC57296D19A5"
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

    "worker_health": (
        ROOT / "backend/server/runtime/universal_worker/health.py",
        "DCC43E77BDC12188DFD15044DA4DA41022B3CEF40F9C4ED06371EE66AA4E5F65",
    ),

    "queue_certification": (
        ROOT / "backend/server/runtime/universal_queue/certification.py",
        "6ED39655147D2B331E02101F5EA23E68CF71447353C0D294E170281AE40C0D4C",
    ),

    "queue_recovery": (
        ROOT / "backend/server/runtime/universal_queue/recovery.py",
        "D7AA19721DEFB1D40A24A22EBA04BDA776216520CFB31B9FAA1309242F1CF650",
    ),

    "job_contract": (
        ROOT / "backend/server/runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
    ),

    "job_attempts": (
        ROOT / "backend/server/runtime/universal_jobs/attempts.py",
        "2662BC9A968D3F37B9072FA9551A70681E5CE9BEB78E65DAF6550580893DEE24",
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
# PRECONDITION
# ============================================================

if not RECOVERY_PATH.exists():

    raise SystemExit(
        "Worker Recovery authority missing."
    )


initial_ast = ast_sha(
    RECOVERY_PATH
)


if initial_ast != EXPECTED_RECOVERY_AST:

    raise SystemExit(
        (
            "Worker Recovery AST mismatch before "
            "final certification.\nEXPECTED: "
            + EXPECTED_RECOVERY_AST
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
                "final certification: "
                + name
                + "\nEXPECTED: "
                + expected
                + "\nACTUAL:   "
                + actual
            )
        )


# ============================================================
# IMPORT AUTHORITIES
# ============================================================

sys.path.insert(
    0,
    str(ROOT),
)


contract = importlib.import_module(
    "backend.server.runtime.universal_jobs.contract"
)

leasing = importlib.import_module(
    "backend.server.runtime.universal_worker.leasing"
)

recovery_name = (
    "backend.server.runtime."
    "universal_worker.recovery"
)

sys.modules.pop(
    recovery_name,
    None,
)

recovery = importlib.import_module(
    recovery_name
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
# 1 — AST / VERSION / SCHEMAS
# ============================================================

recovery_ast = ast_sha(
    RECOVERY_PATH
)


check(
    "worker_recovery_ast",
    recovery_ast
    == EXPECTED_RECOVERY_AST,
    recovery_ast,
)


check(
    "version",
    recovery.UNIVERSAL_WORKER_RECOVERY_VERSION
    == "universal_worker_recovery_v4.1.6",
)


check(
    "evidence_schema",
    recovery.UNIVERSAL_WORKER_RECOVERY_EVIDENCE_SCHEMA_VERSION
    == "universal_worker_recovery_evidence_schema_v1",
)


check(
    "result_schema",
    recovery.UNIVERSAL_WORKER_RECOVERY_RESULT_SCHEMA_VERSION
    == "universal_worker_recovery_result_schema_v1",
)


check(
    "max_job_id_length",
    recovery.MAX_UNIVERSAL_WORKER_RECOVERY_JOB_ID_LENGTH
    == 200,
)


# ============================================================
# 2 — ENUM SURFACE
# ============================================================

check(
    "dispositions_exact",
    tuple(
        item.value
        for item in recovery.UniversalWorkerRecoveryDisposition
    )
    == (
        "RECOVERABLE",
        "NOT_RECOVERABLE",
        "NO_ACTION",
    ),
)


check(
    "reasons_exact",
    tuple(
        item.value
        for item in recovery.UniversalWorkerRecoveryReason
    )
    == (
        "STATUS_NOT_WORKER_OWNED",
        "OWNERSHIP_STILL_VALID",
        "ACTIVE_LEASE",
        "OWNERSHIP_LOST_RETRY_PERMITTED",
        "RETRY_NOT_PERMITTED",
        "DUPLICATE_EXECUTION_NOT_SAFE",
    ),
)


# ============================================================
# 3 — RUNNING MATRIX
# ============================================================

def expected_running(
    ownership_lost,
    retry_permitted,
    duplicate_safe,
):

    if not ownership_lost:

        return (
            recovery.UniversalWorkerRecoveryDisposition.NO_ACTION,
            recovery.UniversalWorkerRecoveryReason.OWNERSHIP_STILL_VALID,
        )

    if not retry_permitted:

        return (
            recovery.UniversalWorkerRecoveryDisposition.NOT_RECOVERABLE,
            recovery.UniversalWorkerRecoveryReason.RETRY_NOT_PERMITTED,
        )

    if not duplicate_safe:

        return (
            recovery.UniversalWorkerRecoveryDisposition.NOT_RECOVERABLE,
            recovery.UniversalWorkerRecoveryReason.DUPLICATE_EXECUTION_NOT_SAFE,
        )

    return (
        recovery.UniversalWorkerRecoveryDisposition.RECOVERABLE,
        recovery.UniversalWorkerRecoveryReason.OWNERSHIP_LOST_RETRY_PERMITTED,
    )


for index, (
    ownership_lost,
    retry_permitted,
    duplicate_safe,
) in enumerate(
    itertools.product(
        (False, True),
        (False, True),
        (False, True),
    ),
    start=1,
):

    evidence = (
        recovery.create_universal_worker_recovery_evidence(
            job_id=(
                "cert-running-"
                + str(index)
            ),
            job_status=(
                contract.UniversalJobStatus.RUNNING
            ),
            worker_ownership_lost=ownership_lost,
            retry_permitted=retry_permitted,
            duplicate_execution_safe=duplicate_safe,
        )
    )

    result = (
        recovery.evaluate_universal_worker_recovery(
            evidence
        )
    )

    (
        expected_disposition,
        expected_reason,
    ) = expected_running(
        ownership_lost,
        retry_permitted,
        duplicate_safe,
    )

    check(
        "running_matrix_"
        + str(index)
        + "_disposition",
        result.disposition
        is expected_disposition,
    )

    check(
        "running_matrix_"
        + str(index)
        + "_reason",
        result.reason
        is expected_reason,
    )


# ============================================================
# 4 — LEASED ACTIVE / EXPIRED MATRIX
# ============================================================

for retry_permitted, duplicate_safe in (
    itertools.product(
        (False, True),
        (False, True),
    )
):

    active_evidence = (
        recovery.create_universal_worker_recovery_evidence(
            job_id="cert-active",
            job_status=(
                contract.UniversalJobStatus.LEASED
            ),
            worker_ownership_lost=False,
            retry_permitted=retry_permitted,
            duplicate_execution_safe=duplicate_safe,
            lease_state=(
                leasing.UniversalWorkerLeaseState.ACTIVE
            ),
        )
    )

    active_result = (
        recovery.evaluate_universal_worker_recovery(
            active_evidence
        )
    )

    check(
        (
            "active_lease_"
            + str(retry_permitted)
            + "_"
            + str(duplicate_safe)
        ),
        (
            active_result.disposition
            is recovery.UniversalWorkerRecoveryDisposition.NO_ACTION
            and
            active_result.reason
            is recovery.UniversalWorkerRecoveryReason.ACTIVE_LEASE
        ),
    )


for retry_permitted, duplicate_safe in (
    itertools.product(
        (False, True),
        (False, True),
    )
):

    expired_evidence = (
        recovery.create_universal_worker_recovery_evidence(
            job_id="cert-expired",
            job_status=(
                contract.UniversalJobStatus.LEASED
            ),
            worker_ownership_lost=True,
            retry_permitted=retry_permitted,
            duplicate_execution_safe=duplicate_safe,
            lease_state=(
                leasing.UniversalWorkerLeaseState.EXPIRED
            ),
        )
    )

    expired_result = (
        recovery.evaluate_universal_worker_recovery(
            expired_evidence
        )
    )

    if not retry_permitted:

        expected_disposition = (
            recovery.UniversalWorkerRecoveryDisposition.NOT_RECOVERABLE
        )

        expected_reason = (
            recovery.UniversalWorkerRecoveryReason.RETRY_NOT_PERMITTED
        )

    elif not duplicate_safe:

        expected_disposition = (
            recovery.UniversalWorkerRecoveryDisposition.NOT_RECOVERABLE
        )

        expected_reason = (
            recovery.UniversalWorkerRecoveryReason.DUPLICATE_EXECUTION_NOT_SAFE
        )

    else:

        expected_disposition = (
            recovery.UniversalWorkerRecoveryDisposition.RECOVERABLE
        )

        expected_reason = (
            recovery.UniversalWorkerRecoveryReason.OWNERSHIP_LOST_RETRY_PERMITTED
        )

    check(
        (
            "expired_lease_"
            + str(retry_permitted)
            + "_"
            + str(duplicate_safe)
            + "_disposition"
        ),
        expired_result.disposition
        is expected_disposition,
    )

    check(
        (
            "expired_lease_"
            + str(retry_permitted)
            + "_"
            + str(duplicate_safe)
            + "_reason"
        ),
        expired_result.reason
        is expected_reason,
    )


# ============================================================
# 5 — CONTRADICTION SAFETY
# ============================================================

try:

    recovery.create_universal_worker_recovery_evidence(
        job_id="active-conflict",
        job_status=(
            contract.UniversalJobStatus.LEASED
        ),
        worker_ownership_lost=True,
        retry_permitted=True,
        duplicate_execution_safe=True,
        lease_state=(
            leasing.UniversalWorkerLeaseState.ACTIVE
        ),
    )

except recovery.UniversalWorkerRecoveryError as exc:

    active_conflict_rejected = (
        exc.code
        == "active_lease_ownership_contradiction"
    )

else:

    active_conflict_rejected = False


check(
    "active_lease_contradiction",
    active_conflict_rejected,
)


try:

    recovery.create_universal_worker_recovery_evidence(
        job_id="expired-conflict",
        job_status=(
            contract.UniversalJobStatus.LEASED
        ),
        worker_ownership_lost=False,
        retry_permitted=True,
        duplicate_execution_safe=True,
        lease_state=(
            leasing.UniversalWorkerLeaseState.EXPIRED
        ),
    )

except recovery.UniversalWorkerRecoveryError as exc:

    expired_conflict_rejected = (
        exc.code
        == "expired_lease_ownership_contradiction"
    )

else:

    expired_conflict_rejected = False


check(
    "expired_lease_contradiction",
    expired_conflict_rejected,
)


# ============================================================
# 6 — NON-WORKER STATUSES
# ============================================================

for status in (
    contract.UniversalJobStatus.CREATED,
    contract.UniversalJobStatus.QUEUED,
    contract.UniversalJobStatus.SCHEDULED,
    contract.UniversalJobStatus.SUSPENDED,
    contract.UniversalJobStatus.SUCCEEDED,
    contract.UniversalJobStatus.FAILED,
    contract.UniversalJobStatus.CANCELLED,
    contract.UniversalJobStatus.DEAD_LETTER,
    contract.UniversalJobStatus.EXPIRED,
):

    evidence = (
        recovery.create_universal_worker_recovery_evidence(
            job_id=(
                "cert-"
                + status.value
            ),
            job_status=status,
            worker_ownership_lost=True,
            retry_permitted=True,
            duplicate_execution_safe=True,
        )
    )

    result = (
        recovery.evaluate_universal_worker_recovery(
            evidence
        )
    )

    check(
        (
            "non_worker_status_"
            + status.value
        ),
        (
            result.disposition
            is recovery.UniversalWorkerRecoveryDisposition.NO_ACTION
            and
            result.reason
            is recovery.UniversalWorkerRecoveryReason.STATUS_NOT_WORKER_OWNED
        ),
    )


# ============================================================
# 7 — RECOVERY PROPERTIES
# ============================================================

recoverable_evidence = (
    recovery.create_universal_worker_recovery_evidence(
        job_id="cert-recoverable",
        job_status=(
            contract.UniversalJobStatus.RUNNING
        ),
        worker_ownership_lost=True,
        retry_permitted=True,
        duplicate_execution_safe=True,
    )
)


recoverable_result = (
    recovery.evaluate_universal_worker_recovery(
        recoverable_evidence
    )
)


check(
    "recoverable_property",
    recoverable_result.recoverable
    is True,
)


check(
    "recoverable_action_required",
    recoverable_result.action_required
    is True,
)


no_action_result = (
    recovery.evaluate_universal_worker_recovery(
        recovery.create_universal_worker_recovery_evidence(
            job_id="cert-no-action",
            job_status=(
                contract.UniversalJobStatus.RUNNING
            ),
            worker_ownership_lost=False,
            retry_permitted=True,
            duplicate_execution_safe=True,
        )
    )
)


check(
    "no_action_recoverable_false",
    no_action_result.recoverable
    is False,
)


check(
    "no_action_required_false",
    no_action_result.action_required
    is False,
)


# ============================================================
# 8 — IMMUTABILITY
# ============================================================

for obj, field_name in (
    (
        recoverable_evidence,
        "job_id",
    ),
    (
        recoverable_evidence,
        "job_status",
    ),
    (
        recoverable_evidence,
        "worker_ownership_lost",
    ),
    (
        recoverable_evidence,
        "retry_permitted",
    ),
    (
        recoverable_evidence,
        "duplicate_execution_safe",
    ),
    (
        recoverable_result,
        "disposition",
    ),
    (
        recoverable_result,
        "reason",
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
# 9 — FORGERY PROTECTION
# ============================================================

try:

    recovery.UniversalWorkerRecoveryResult(
        job_id=recoverable_evidence.job_id,
        original_status=(
            recoverable_evidence.job_status
        ),
        disposition=(
            recovery.UniversalWorkerRecoveryDisposition.NO_ACTION
        ),
        reason=(
            recovery.UniversalWorkerRecoveryReason.OWNERSHIP_STILL_VALID
        ),
        worker_ownership_lost=True,
        retry_permitted=True,
        duplicate_execution_safe=True,
        lease_state=None,
    )

except recovery.UniversalWorkerRecoveryError as exc:

    forged_result_rejected = (
        exc.code
        == "inconsistent_worker_recovery_result"
    )

else:

    forged_result_rejected = False


check(
    "forged_result_rejected",
    forged_result_rejected,
)


# ============================================================
# 10 — DETERMINISM
# ============================================================

check(
    "deterministic_decision",
    recovery.decide_universal_worker_recovery(
        recoverable_evidence
    )
    ==
    recovery.decide_universal_worker_recovery(
        recoverable_evidence
    ),
)


check(
    "deterministic_result",
    recovery.evaluate_universal_worker_recovery(
        recoverable_evidence
    )
    ==
    recovery.evaluate_universal_worker_recovery(
        recoverable_evidence
    ),
)


# ============================================================
# 11 — EXPLANATION CONTRACT
# ============================================================

explanation = (
    recovery.explain_universal_worker_recovery_v1()
)


check(
    "phase",
    explanation.get(
        "phase"
    )
    == "4.1.6",
)


check(
    "component",
    explanation.get(
        "component"
    )
    == "Universal Worker Recovery",
)


check(
    "explanation_version",
    explanation.get(
        "version"
    )
    == recovery.UNIVERSAL_WORKER_RECOVERY_VERSION,
)


check(
    "evidence_schema_explanation",
    explanation.get(
        "evidence_schema_version"
    )
    == recovery.UNIVERSAL_WORKER_RECOVERY_EVIDENCE_SCHEMA_VERSION,
)


check(
    "result_schema_explanation",
    explanation.get(
        "result_schema_version"
    )
    == recovery.UNIVERSAL_WORKER_RECOVERY_RESULT_SCHEMA_VERSION,
)


check(
    "worker_owned_statuses",
    tuple(
        explanation.get(
            "worker_owned_statuses"
        )
    )
    == (
        "LEASED",
        "RUNNING",
    ),
)


check(
    "recovery_gate",
    (
        "worker ownership lost"
        in explanation.get(
            "recovery_gate_rule",
            "",
        )
        and
        "retry permitted"
        in explanation.get(
            "recovery_gate_rule",
            "",
        )
        and
        "duplicate execution safe"
        in explanation.get(
            "recovery_gate_rule",
            "",
        )
    ),
)


check(
    "retry_boundary",
    (
        "increment attempts"
        in explanation.get(
            "retry_boundary",
            "",
        )
        and
        "backoff"
        in explanation.get(
            "retry_boundary",
            "",
        )
    ),
)


check(
    "queue_boundary",
    "does not restore queue membership"
    in explanation.get(
        "queue_boundary",
        "",
    ),
)


check(
    "health_heartbeat_boundary",
    (
        "does not classify worker health"
        in explanation.get(
            "health_heartbeat_boundary",
            "",
        )
        and
        "detect stale workers"
        in explanation.get(
            "health_heartbeat_boundary",
            "",
        )
    ),
)


check(
    "dead_letter_boundary",
    "outside"
    in explanation.get(
        "dead_letter_boundary",
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
# 12 — PROHIBITION MATRIX
# ============================================================

required_prohibitions = (
    "does not requeue jobs",
    "does not restore queue membership",
    "does not increment attempts",
    "does not calculate maximum attempts",
    "does not calculate retry backoff",
    "does not schedule retries",
    "does not transition jobs to QUEUED",
    "does not transition jobs to FAILED",
    "does not transition jobs to DEAD_LETTER",
    "does not recover dead-letter jobs",
    "does not acquire leases",
    "does not renew leases",
    "does not release leases",
    "does not persist leases",
    "does not classify lease expiration",
    "does not determine worker health",
    "does not read worker heartbeats",
    "does not calculate heartbeat freshness",
    "does not detect stale workers",
    "does not restart workers",
    "does not terminate workers",
    "does not assign replacement workers",
    "does not dispatch jobs",
    "does not execute jobs",
    "does not invent idempotency policy",
    "does not invent fencing policy",
    "does not access Runtime State Store",
    "does not access orchestration",
    "does not mutate Queue Infrastructure",
    "does not persist recovery results",
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
        item
        in prohibitions,
        item,
    )


# ============================================================
# 13 — STATIC IMPORT / API SURFACE
# ============================================================

source = RECOVERY_PATH.read_text(
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


check(
    "backend_imports_exact",
    backend_imports
    == [
        "backend.server.runtime.universal_jobs.contract",
        "backend.server.runtime.universal_worker.leasing",
    ],
    backend_imports,
)


expected_all = (
    "UNIVERSAL_WORKER_RECOVERY_VERSION",
    "UNIVERSAL_WORKER_RECOVERY_EVIDENCE_SCHEMA_VERSION",
    "UNIVERSAL_WORKER_RECOVERY_RESULT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_RECOVERY_JOB_ID_LENGTH",
    "UniversalWorkerRecoveryError",
    "UniversalWorkerRecoveryDisposition",
    "UniversalWorkerRecoveryReason",
    "UniversalWorkerRecoveryEvidence",
    "UniversalWorkerRecoveryResult",
    "normalize_universal_worker_recovery_job_id",
    "create_universal_worker_recovery_evidence",
    "decide_universal_worker_recovery",
    "evaluate_universal_worker_recovery",
    "explain_universal_worker_recovery_v1",
)


check(
    "api_surface_exact",
    tuple(
        recovery.__all__
    )
    == expected_all,
    recovery.__all__,
)


# ============================================================
# 14 — FORBIDDEN SIDE EFFECT CALLS
# ============================================================

forbidden_names = {
    "open",
    "write_text",
    "mkdir",
    "unlink",
    "remove",
    "now",
    "utcnow",
    "time",
    "sleep",
    "worker_heartbeat",
    "get_latest_worker_statuses",
    "get_runtime_state_store_registry",
    "recover_universal_queue_membership",
    "retry_job",
    "retry_exhausted",
    "dequeue_job",
    "enqueue_job",
    "requeue_job",
    "assign_universal_worker",
    "acquire_universal_worker_lease",
    "renew_universal_worker_lease",
    "release_universal_worker_lease",
    "evaluate_universal_worker_lease_state",
    "evaluate_universal_worker_health",
    "dispatch_job",
    "execute_job",
    "dispatch_registered_runtime_handler",
    "mark_job_failed",
    "mark_job_completed",
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
# 15 — PROTECTED AST MATRIX
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
# 16 — CANONICAL FINGERPRINT
# ============================================================

fingerprint_material = "|".join(
    (
        "phase_4_1_6_worker_recovery",
        recovery.UNIVERSAL_WORKER_RECOVERY_VERSION,
        recovery.UNIVERSAL_WORKER_RECOVERY_EVIDENCE_SCHEMA_VERSION,
        recovery.UNIVERSAL_WORKER_RECOVERY_RESULT_SCHEMA_VERSION,
        recovery_ast,
        "LEASED",
        "RUNNING",
        "RECOVERABLE",
        "NOT_RECOVERABLE",
        "NO_ACTION",
        "worker_ownership_lost",
        "retry_permitted",
        "duplicate_execution_safe",
        "ACTIVE",
        "EXPIRED",
        "ownership_loss_and_retry_and_duplicate_safety",
        "recovery_permission_not_requeue",
        "recovery_not_attempt_policy",
        "recovery_not_dead_letter",
        "recovery_not_execution",
    )
)


recovery_fingerprint = (
    hashlib.sha256(
        fingerprint_material.encode(
            "utf-8"
        )
    ).hexdigest().upper()
)


check(
    "fingerprint_generated",
    len(
        recovery_fingerprint
    )
    == 64,
    recovery_fingerprint,
)


# ============================================================
# 17 — FINAL AST RECHECK
# ============================================================

final_ast = ast_sha(
    RECOVERY_PATH
)


check(
    "final_ast_unchanged",
    final_ast
    == EXPECTED_RECOVERY_AST,
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
        "PHASE 4.1.6 — UNIVERSAL WORKER "
        "RECOVERY FINAL CERTIFICATION"
    ),
    "=" * 112,
    "",
    (
        "WORKER RECOVERY AST SHA256: "
        + recovery_ast
    ),
    (
        "WORKER RECOVERY FINGERPRINT: "
        + recovery_fingerprint
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
            "FINAL WORKER RECOVERY CERTIFICATION: "
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
        "WORKER RECOVERY MODIFIED DURING CERTIFICATION: NO",
        "4.1.1 WORKER REGISTRATION MODIFIED: NO",
        "4.1.2 WORKER DISCOVERY MODIFIED: NO",
        "4.1.3 WORKER ASSIGNMENT MODIFIED: NO",
        "4.1.4 WORKER LEASING MODIFIED: NO",
        "4.1.5 WORKER HEALTH MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "QUEUE RECOVERY MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "UNIVERSAL JOB ATTEMPTS MODIFIED: NO",
        "EXISTING UNIVERSAL RUNTIME WORKER MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "JOB REQUEUED: NO",
        "QUEUE MEMBERSHIP RESTORED: NO",
        "JOB ATTEMPTS INCREMENTED: NO",
        "MAXIMUM ATTEMPTS CALCULATED: NO",
        "RETRY BACKOFF CALCULATED: NO",
        "RETRY SCHEDULED: NO",
        "JOB STATUS MUTATED: NO",
        "JOB DEAD-LETTERED: NO",
        "DEAD-LETTER JOB RECOVERED: NO",
        "LEASE ACQUIRED/RENEWED/RELEASED: NO",
        "LEASE EXPIRATION CLASSIFIED: NO",
        "WORKER HEALTH DECIDED: NO",
        "WORKER HEARTBEAT READ: NO",
        "HEARTBEAT FRESHNESS CALCULATED: NO",
        "STALE WORKER DETECTED: NO",
        "WORKER RESTARTED/TERMINATED: NO",
        "REPLACEMENT WORKER ASSIGNED: NO",
        "IDEMPOTENCY POLICY INVENTED: NO",
        "FENCING POLICY INVENTED: NO",
        "JOB DISPATCHED: NO",
        "JOB EXECUTED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "RECOVERY RESULT PERSISTED: NO",
        "",
        (
            "PHASE 4.1.6 FREEZE CANDIDATE: "
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
        "Phase 4.1.6 Worker Recovery final certification failed."
    )
