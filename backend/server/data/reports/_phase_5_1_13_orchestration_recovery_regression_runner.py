from __future__ import annotations

import ast
import hashlib
import importlib
import sys

from dataclasses import fields
from pathlib import Path
from types import MappingProxyType


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

RECOVERY_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_orchestration"
    / "recovery.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_1_13_orchestration_recovery_regression.txt"
)

EXPECTED_RECOVERY_AST = (
    "4465A7AF795512594023D19E27A175CA060ACD2845BB4530B77FF8D69C40B16F"
)


PROTECTED = {
    "5.1.1_contract": (
        ROOT / "backend/server/runtime/universal_orchestration/contract.py",
        "8CC241284B8AF87809A41134FF0FDEB402D5DE49A117D931920CC17346271FD9",
    ),

    "5.1.2_run_identity": (
        ROOT / "backend/server/runtime/universal_orchestration/run_identity.py",
        "A582564C7D45D96DAB2D6DAF38E8C63B9EA281251F41B02D12DE17F1D68CAFBC",
    ),

    "5.1.3_state_model": (
        ROOT / "backend/server/runtime/universal_orchestration/state_model.py",
        "B179C6BEB0A232F0170A2ED540D84239A2235A4F0F91528B530E229B61172610",
    ),

    "5.1.4_dependency_resolution": (
        ROOT / "backend/server/runtime/universal_orchestration/dependency_resolution.py",
        "CF4CE73A8683BFDA1464730F2079058898B2660275C786FA6EBD0816AE574A8E",
    ),

    "5.1.5_execution_planning": (
        ROOT / "backend/server/runtime/universal_orchestration/execution_planning.py",
        "78F7945AD5592370C21BF919328D6C29627EF209F37A5E864C0588CD40DC7465",
    ),

    "5.1.6_stage_readiness": (
        ROOT / "backend/server/runtime/universal_orchestration/stage_readiness.py",
        "9BF16440AD057B1C6A89DD9AEEDEADBE32F711EAE2D4FCD8730EB796BF603D6D",
    ),

    "5.1.7_runtime_handoff": (
        ROOT / "backend/server/runtime/universal_orchestration/runtime_handoff.py",
        "6878FC6F0F2EF071B11A93D793A0CC80B2C91B676C6B6735A78237D8C7D6CB73",
    ),

    "5.1.8_fan_out": (
        ROOT / "backend/server/runtime/universal_orchestration/fan_out_coordination.py",
        "D60C8629D2490DC41A8DF43E30F00A1D4851941E65CBD2EBE7EED70B75217916",
    ),

    "5.1.9_fan_in": (
        ROOT / "backend/server/runtime/universal_orchestration/fan_in_coordination.py",
        "98786AEF5E4DBD804FBE5FE32EEE7CD54907FAC6A9C016B6120851834F6CFA0F",
    ),

    "5.1.10_conditional_branching": (
        ROOT / "backend/server/runtime/universal_orchestration/conditional_branching.py",
        "3799D3BEFB10C77400B40964EBBCCF598B7576BA9034D1C7F29622D0EC65286F",
    ),

    "5.1.11_progress_tracking": (
        ROOT / "backend/server/runtime/universal_orchestration/progress_tracking.py",
        "92C100E0682F975488F78ED5F0D38CB1F4C6E18F6FEA08D1A8D81BE98A4D8309",
    ),

    "5.1.12_suspension_resume": (
        ROOT / "backend/server/runtime/universal_orchestration/suspension_resume_eligibility.py",
        "476631641C740443FF7B3D1D1D0E9D6D155289BDCAF14526698528432CCF913A",
    ),

    "worker_recovery": (
        ROOT / "backend/server/runtime/universal_worker/recovery.py",
        "C3EF5DBD81205F0087E05F43F6A67A1E0762930DAAD256F957AABC57296D19A5",
    ),

    "job_contract": (
        ROOT / "backend/server/runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
    ),

    "queue_certification": (
        ROOT / "backend/server/runtime/universal_queue/certification.py",
        "6ED39655147D2B331E02101F5EA23E68CF71447353C0D294E170281AE40C0D4C",
    ),

    "runtime_registration": (
        ROOT / "backend/server/runtime/universal_runtime_registration.py",
        "CBFBB0DA1E5D05A040AEC6F60B1251331431956106D90335A8C110FDBCA632E5",
    ),

    "runtime_worker": (
        ROOT / "backend/server/runtime/universal_runtime_worker_v1.py",
        "6CC4EC122C6B8D1E21AFF8B55CAA786148D7E1FC75D840DAE9240FFB69634D44",
    ),

    "runtime_infrastructure": (
        ROOT / "backend/server/runtime/universal_runtime_infrastructure.py",
        "EE6590D044C6AA20762F2A37AE86B7FFD3300B62610BC2B1F2657D9334CB311C",
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
# PRE-FLIGHT
# ============================================================

if not RECOVERY_PATH.exists():

    raise SystemExit(
        "5.1.13 Orchestration Recovery authority is missing."
    )


initial_ast = ast_sha(
    RECOVERY_PATH
)


if initial_ast != EXPECTED_RECOVERY_AST:

    raise SystemExit(
        (
            "5.1.13 AST changed before adversarial regression.\n"
            "EXPECTED: "
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
            "Protected authority mismatch before regression: "
            + name
        )


# ============================================================
# IMPORTS
# ============================================================

sys.path.insert(
    0,
    str(ROOT),
)


jobs = importlib.import_module(
    "backend.server.runtime.universal_jobs.contract"
)

contracts = importlib.import_module(
    "backend.server.runtime.universal_orchestration.contract"
)

identities = importlib.import_module(
    "backend.server.runtime.universal_orchestration.run_identity"
)

planning = importlib.import_module(
    "backend.server.runtime.universal_orchestration.execution_planning"
)

state_model = importlib.import_module(
    "backend.server.runtime.universal_orchestration.state_model"
)

fanout = importlib.import_module(
    "backend.server.runtime.universal_orchestration.fan_out_coordination"
)

conditional = importlib.import_module(
    "backend.server.runtime.universal_orchestration.conditional_branching"
)

progress = importlib.import_module(
    "backend.server.runtime.universal_orchestration.progress_tracking"
)


module_name = (
    "backend.server.runtime."
    "universal_orchestration.recovery"
)

sys.modules.pop(
    module_name,
    None,
)

recovery = importlib.import_module(
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


FIXED_CREATED_AT = (
    "2026-05-21T03:49:30.579317+00:00"
)


# ============================================================
# FIXTURE HELPERS
# ============================================================

def make_job(
    *,
    job_id,
    dependencies=(),
):

    return jobs.UniversalJob(
        job_id=job_id,
        workspace_id="workspace-a",
        pipeline="pipeline-a",
        stage="stage-a",
        job_type="test_job",
        payload_reference="payload-a",
        dependency_job_ids=tuple(
            dependencies
        ),
        status=jobs.UniversalJobStatus.CREATED,
        created_at=FIXED_CREATED_AT,
    )


def make_plan(
    *,
    run_id,
    jobs_tuple,
):

    contract = (
        contracts
        .create_universal_runtime_orchestration_contract(
            workspace_id="workspace-a",
            pipeline="pipeline-a",
            job_ids=tuple(
                job.job_id
                for job
                in jobs_tuple
            ),
        )
    )

    identity = (
        identities
        .create_universal_orchestration_run_identity(
            orchestration_run_id=run_id,
            contract=contract,
        )
    )

    return (
        planning
        .create_universal_orchestration_execution_plan(
            identity=identity,
            jobs=jobs_tuple,
        )
    )


def make_single_plan(
    run_id,
):

    return make_plan(
        run_id=run_id,
        jobs_tuple=(
            make_job(
                job_id="job-a"
            ),
        ),
    )


def make_state(
    *,
    plan,
    state,
):

    return (
        state_model
        .create_universal_orchestration_state_snapshot(
            identity=plan.identity,
            state=state,
        )
    )


def make_progress(
    *,
    plan,
    statuses,
    decisions=(),
):

    return (
        progress
        .track_universal_orchestration_progress(
            execution_plan=plan,
            status_evidence=statuses,
            conditional_branching_decisions=decisions,
        )
    )


def evaluate(
    *,
    plan,
    orchestration_state,
    statuses,
    decisions=(),
):

    return (
        recovery
        .evaluate_universal_orchestration_recovery(
            state_snapshot=make_state(
                plan=plan,
                state=orchestration_state,
            ),
            progress_snapshot=make_progress(
                plan=plan,
                statuses=statuses,
                decisions=decisions,
            ),
        )
    )


# ============================================================
# 1. AUTHORITY EXACTNESS
# ============================================================

check(
    "ast_initial_exact",
    ast_sha(
        RECOVERY_PATH
    )
    == EXPECTED_RECOVERY_AST,
)

check(
    "version_exact",
    recovery.UNIVERSAL_ORCHESTRATION_RECOVERY_VERSION
    ==
    "universal_orchestration_recovery_v5.1.13",
)

check(
    "schema_exact",
    recovery.UNIVERSAL_ORCHESTRATION_RECOVERY_SCHEMA_VERSION
    ==
    "universal_orchestration_recovery_schema_v1",
)

check(
    "hash_algorithm_exact",
    recovery.UNIVERSAL_ORCHESTRATION_RECOVERY_DECISION_HASH_ALGORITHM
    == "sha256",
)


expected_all = (
    "UNIVERSAL_ORCHESTRATION_RECOVERY_VERSION",
    "UNIVERSAL_ORCHESTRATION_RECOVERY_SCHEMA_VERSION",
    "UNIVERSAL_ORCHESTRATION_RECOVERY_DECISION_HASH_ALGORITHM",
    "UniversalOrchestrationRecoveryError",
    "UniversalOrchestrationRecoveryDisposition",
    "UniversalOrchestrationRecoveryReason",
    "UniversalOrchestrationRecoveryDecision",
    "evaluate_universal_orchestration_recovery",
    "explain_universal_orchestration_recovery_v1",
)


check(
    "public_api_exact",
    tuple(
        recovery.__all__
    )
    == expected_all,
    recovery.__all__,
)


# ============================================================
# 2. ENUM EXACTNESS
# ============================================================

check(
    "dispositions_exact",
    tuple(
        item.value
        for item
        in recovery.UniversalOrchestrationRecoveryDisposition
    )
    == (
        "not_required",
        "recoverable",
        "unrecoverable",
        "unresolved",
    ),
)


check(
    "reasons_exact",
    tuple(
        item.value
        for item
        in recovery.UniversalOrchestrationRecoveryReason
    )
    == (
        "terminal_orchestration",
        "missing_status_evidence",
        "unresolved_branch_activity",
        "cancelled_effective_work",
        "policy_dependent_terminal_work",
        "failed_effective_work",
        "no_recovery_required",
    ),
)


# ============================================================
# 3. INVALID INPUTS
# ============================================================

base_plan = make_single_plan(
    "invalid-inputs"
)

base_state = make_state(
    plan=base_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
)

base_progress = make_progress(
    plan=base_plan,
    statuses={
        "job-a": "created",
    },
)


for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        1,
        1.0,
        "",
        (),
        [],
        {},
        set(),
        object(),
    ),
    start=1,
):

    try:

        recovery.evaluate_universal_orchestration_recovery(
            state_snapshot=bad,
            progress_snapshot=base_progress,
        )

    except recovery.UniversalOrchestrationRecoveryError as exc:

        rejected = (
            exc.code
            == "invalid_orchestration_recovery_state_snapshot"
        )

    else:

        rejected = False

    check(
        "invalid_state_snapshot_"
        + str(index),
        rejected,
    )


for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        1,
        1.0,
        "",
        (),
        [],
        {},
        set(),
        object(),
    ),
    start=1,
):

    try:

        recovery.evaluate_universal_orchestration_recovery(
            state_snapshot=base_state,
            progress_snapshot=bad,
        )

    except recovery.UniversalOrchestrationRecoveryError as exc:

        rejected = (
            exc.code
            == "invalid_orchestration_recovery_progress_snapshot"
        )

    else:

        rejected = False

    check(
        "invalid_progress_snapshot_"
        + str(index),
        rejected,
    )


# ============================================================
# 4. STORED FIELDS
# ============================================================

field_names = tuple(
    field.name
    for field
    in fields(
        recovery.UniversalOrchestrationRecoveryDecision
    )
)


check(
    "stored_fields_exact",
    field_names
    == (
        "state_snapshot",
        "progress_snapshot",
        "schema_version",
    ),
    field_names,
)


for forbidden in (
    "identity",
    "orchestration_state",
    "disposition",
    "reason",

    "recovery_candidate_job_ids",
    "cancelled_effective_job_ids",
    "policy_dependent_job_ids",
    "missing_status_job_ids",
    "unresolved_effective_job_ids",

    "recovery_decision_id",

    "attempt_count",
    "max_attempts",
    "retry_policy",
    "backoff",

    "queue_id",
    "worker_id",
    "lease_id",

    "checkpoint_reference",

    "created_at",
    "updated_at",
    "timestamp",
):

    check(
        "forbidden_stored_"
        + forbidden,
        forbidden
        not in field_names,
    )


# ============================================================
# 5. INVALID SCHEMA
# ============================================================

try:

    recovery.UniversalOrchestrationRecoveryDecision(
        state_snapshot=base_state,
        progress_snapshot=base_progress,
        schema_version="wrong",
    )

except recovery.UniversalOrchestrationRecoveryError as exc:

    bad_schema_rejected = (
        exc.code
        == "invalid_orchestration_recovery_schema_version"
    )

else:

    bad_schema_rejected = False


check(
    "invalid_schema_rejected",
    bad_schema_rejected,
)


# ============================================================
# 6. CROSS-IDENTITY
# ============================================================

other_plan = make_single_plan(
    "cross-identity-other"
)


try:

    recovery.evaluate_universal_orchestration_recovery(
        state_snapshot=make_state(
            plan=other_plan,
            state=state_model.UniversalOrchestrationState.ACTIVE,
        ),
        progress_snapshot=base_progress,
    )

except recovery.UniversalOrchestrationRecoveryError as exc:

    cross_identity_rejected = (
        exc.code
        == "orchestration_recovery_identity_mismatch"
    )

else:

    cross_identity_rejected = False


check(
    "cross_identity_rejected",
    cross_identity_rejected,
)


# ============================================================
# 7. HEALTHY STATUS MATRIX
# ============================================================

healthy_plan = make_single_plan(
    "healthy-status-matrix"
)


for status in (
    "created",
    "queued",
    "scheduled",
    "leased",
    "running",
    "suspended",
    "succeeded",
):

    result = evaluate(
        plan=healthy_plan,
        orchestration_state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "job-a": status,
        },
    )

    check(
        "healthy_not_required_"
        + status,
        result.disposition
        is
        recovery.UniversalOrchestrationRecoveryDisposition.NOT_REQUIRED,
    )

    check(
        "healthy_reason_"
        + status,
        result.reason
        is
        recovery.UniversalOrchestrationRecoveryReason.NO_RECOVERY_REQUIRED,
    )


# ============================================================
# 8. FAILED MATRIX
# ============================================================

for orchestration_state in (
    state_model.UniversalOrchestrationState.CREATED,
    state_model.UniversalOrchestrationState.ACTIVE,
    state_model.UniversalOrchestrationState.WAITING,
    state_model.UniversalOrchestrationState.SUSPENDED,
    state_model.UniversalOrchestrationState.RECOVERING,
):

    plan = make_single_plan(
        "failed-"
        + orchestration_state.value
    )

    result = evaluate(
        plan=plan,
        orchestration_state=orchestration_state,
        statuses={
            "job-a": "failed",
        },
    )

    check(
        "failed_recoverable_"
        + orchestration_state.value,
        result.disposition
        is
        recovery.UniversalOrchestrationRecoveryDisposition.RECOVERABLE,
    )

    check(
        "failed_reason_"
        + orchestration_state.value,
        result.reason
        is
        recovery.UniversalOrchestrationRecoveryReason.FAILED_EFFECTIVE_WORK,
    )

    check(
        "failed_candidate_"
        + orchestration_state.value,
        result.recovery_candidate_job_ids
        == ("job-a",),
    )


# ============================================================
# 9. TERMINAL ORCHESTRATION OVERRIDE
# ============================================================

for orchestration_state in (
    state_model.UniversalOrchestrationState.SUCCEEDED,
    state_model.UniversalOrchestrationState.FAILED,
    state_model.UniversalOrchestrationState.CANCELLED,
):

    plan = make_single_plan(
        "terminal-override-"
        + orchestration_state.value
    )

    for job_status in (
        "created",
        "running",
        "failed",
        "cancelled",
        "dead_letter",
        "expired",
        None,
    ):

        result = evaluate(
            plan=plan,
            orchestration_state=orchestration_state,
            statuses={
                "job-a": job_status,
            },
        )

        suffix = (
            orchestration_state.value
            + "_"
            + (
                "missing"
                if job_status is None
                else str(job_status)
            )
        )

        check(
            "terminal_unrecoverable_"
            + suffix,
            result.disposition
            is
            recovery.UniversalOrchestrationRecoveryDisposition.UNRECOVERABLE,
        )

        check(
            "terminal_reason_"
            + suffix,
            result.reason
            is
            recovery.UniversalOrchestrationRecoveryReason.TERMINAL_ORCHESTRATION,
        )


# ============================================================
# 10. CANCELLED EFFECTIVE WORK
# ============================================================

cancelled_plan = make_single_plan(
    "cancelled-effective"
)


cancelled_result = evaluate(
    plan=cancelled_plan,
    orchestration_state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "job-a": "cancelled",
    },
)


check(
    "cancelled_unrecoverable",
    cancelled_result.disposition
    is
    recovery.UniversalOrchestrationRecoveryDisposition.UNRECOVERABLE,
)

check(
    "cancelled_reason_exact",
    cancelled_result.reason
    is
    recovery.UniversalOrchestrationRecoveryReason.CANCELLED_EFFECTIVE_WORK,
)

check(
    "cancelled_ids_exact",
    cancelled_result.cancelled_effective_job_ids
    == ("job-a",),
)


# ============================================================
# 11. POLICY-DEPENDENT TERMINALS
# ============================================================

for status in (
    "dead_letter",
    "expired",
):

    plan = make_single_plan(
        "policy-dependent-"
        + status
    )

    result = evaluate(
        plan=plan,
        orchestration_state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "job-a": status,
        },
    )

    check(
        "policy_dependent_unresolved_"
        + status,
        result.disposition
        is
        recovery.UniversalOrchestrationRecoveryDisposition.UNRESOLVED,
    )

    check(
        "policy_dependent_reason_"
        + status,
        result.reason
        is
        recovery.UniversalOrchestrationRecoveryReason.POLICY_DEPENDENT_TERMINAL_WORK,
    )

    check(
        "policy_dependent_ids_"
        + status,
        result.policy_dependent_job_ids
        == ("job-a",),
    )


# ============================================================
# 12. MISSING EVIDENCE
# ============================================================

missing_plan = make_single_plan(
    "missing-status"
)


missing_result = evaluate(
    plan=missing_plan,
    orchestration_state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "job-a": None,
    },
)


check(
    "missing_unresolved",
    missing_result.disposition
    is
    recovery.UniversalOrchestrationRecoveryDisposition.UNRESOLVED,
)

check(
    "missing_reason_exact",
    missing_result.reason
    is
    recovery.UniversalOrchestrationRecoveryReason.MISSING_STATUS_EVIDENCE,
)

check(
    "missing_ids_exact",
    missing_result.missing_status_job_ids
    == ("job-a",),
)


# ============================================================
# 13. PRECEDENCE:
# MISSING > UNRESOLVED BRANCH > CANCELLED > POLICY > FAILED
# ============================================================

branch_plan = make_plan(
    run_id="precedence-branch",
    jobs_tuple=(
        make_job(
            job_id="root",
        ),
        make_job(
            job_id="a",
            dependencies=("root",),
        ),
        make_job(
            job_id="b",
            dependencies=("root",),
        ),
        make_job(
            job_id="c",
            dependencies=("root",),
        ),
    ),
)


branch_fanout = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=branch_plan,
        source_job_id="root",
    )
)


unresolved_decision = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=branch_fanout,
        condition_evidence={
            "a": True,
            "b": None,
            "c": True,
        },
    )
)


precedence_missing = evaluate(
    plan=branch_plan,
    orchestration_state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "root": "succeeded",
        "a": None,
        "b": "failed",
        "c": "cancelled",
    },
    decisions=(
        unresolved_decision,
    ),
)


check(
    "precedence_missing_first",
    precedence_missing.reason
    is
    recovery.UniversalOrchestrationRecoveryReason.MISSING_STATUS_EVIDENCE,
)


precedence_branch = evaluate(
    plan=branch_plan,
    orchestration_state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "root": "succeeded",
        "a": "failed",
        "b": "created",
        "c": "cancelled",
    },
    decisions=(
        unresolved_decision,
    ),
)


check(
    "precedence_unresolved_branch_second",
    precedence_branch.reason
    is
    recovery.UniversalOrchestrationRecoveryReason.UNRESOLVED_BRANCH_ACTIVITY,
)


resolved_decision = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=branch_fanout,
        condition_evidence={
            "a": True,
            "b": True,
            "c": True,
        },
    )
)


precedence_cancelled = evaluate(
    plan=branch_plan,
    orchestration_state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "root": "succeeded",
        "a": "failed",
        "b": "dead_letter",
        "c": "cancelled",
    },
    decisions=(
        resolved_decision,
    ),
)


check(
    "precedence_cancelled_third",
    precedence_cancelled.reason
    is
    recovery.UniversalOrchestrationRecoveryReason.CANCELLED_EFFECTIVE_WORK,
)


precedence_policy = evaluate(
    plan=branch_plan,
    orchestration_state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "root": "succeeded",
        "a": "failed",
        "b": "dead_letter",
        "c": "created",
    },
    decisions=(
        resolved_decision,
    ),
)


check(
    "precedence_policy_fourth",
    precedence_policy.reason
    is
    recovery.UniversalOrchestrationRecoveryReason.POLICY_DEPENDENT_TERMINAL_WORK,
)


precedence_failed = evaluate(
    plan=branch_plan,
    orchestration_state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "root": "succeeded",
        "a": "failed",
        "b": "created",
        "c": "running",
    },
    decisions=(
        resolved_decision,
    ),
)


check(
    "precedence_failed_fifth",
    precedence_failed.reason
    is
    recovery.UniversalOrchestrationRecoveryReason.FAILED_EFFECTIVE_WORK,
)


# ============================================================
# 14. EXCLUDED FAILED/CANCELLED/POLICY WORK DOES NOT COUNT
# ============================================================

excluded_decision = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=branch_fanout,
        condition_evidence={
            "a": False,
            "b": False,
            "c": True,
        },
    )
)


excluded_failure = evaluate(
    plan=branch_plan,
    orchestration_state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "root": "succeeded",
        "a": "failed",
        "b": "cancelled",
        "c": "created",
    },
    decisions=(
        excluded_decision,
    ),
)


check(
    "excluded_failure_not_required",
    excluded_failure.disposition
    is
    recovery.UniversalOrchestrationRecoveryDisposition.NOT_REQUIRED,
)

check(
    "excluded_failure_candidate_empty",
    excluded_failure.recovery_candidate_job_ids
    == (),
)

check(
    "excluded_cancelled_empty",
    excluded_failure.cancelled_effective_job_ids
    == (),
)


# ============================================================
# 15. PARTIAL FAILURE WITH ACTIVE HEALTHY WORK
# ============================================================

mixed_plan = make_plan(
    run_id="mixed-work",
    jobs_tuple=(
        make_job(
            job_id="a"
        ),
        make_job(
            job_id="b"
        ),
        make_job(
            job_id="c"
        ),
        make_job(
            job_id="d"
        ),
    ),
)


mixed = evaluate(
    plan=mixed_plan,
    orchestration_state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "failed",
        "b": "running",
        "c": "queued",
        "d": "succeeded",
    },
)


check(
    "partial_failure_recoverable",
    mixed.disposition
    is
    recovery.UniversalOrchestrationRecoveryDisposition.RECOVERABLE,
)

check(
    "partial_failure_candidate_exact",
    mixed.recovery_candidate_job_ids
    == ("a",),
)


# ============================================================
# 16. SUSPENDED IS NOT FAILURE
# ============================================================

suspended_only = evaluate(
    plan=mixed_plan,
    orchestration_state=state_model.UniversalOrchestrationState.SUSPENDED,
    statuses={
        "a": "suspended",
        "b": "created",
        "c": "queued",
        "d": "succeeded",
    },
)


check(
    "suspended_not_recovery_failure",
    suspended_only.disposition
    is
    recovery.UniversalOrchestrationRecoveryDisposition.NOT_REQUIRED,
)


# ============================================================
# 17. RECOVERING STATE
# ============================================================

recovering_failed = evaluate(
    plan=mixed_plan,
    orchestration_state=state_model.UniversalOrchestrationState.RECOVERING,
    statuses={
        "a": "failed",
        "b": "created",
        "c": "running",
        "d": "succeeded",
    },
)


check(
    "recovering_failed_still_recoverable",
    recovering_failed.disposition
    is
    recovery.UniversalOrchestrationRecoveryDisposition.RECOVERABLE,
)

check(
    "recovering_flag_true",
    recovering_failed.is_currently_recovering,
)

check(
    "recovering_may_enter_false",
    not recovering_failed.may_enter_recovering,
)


# ============================================================
# 18. MAY ENTER RECOVERING MATCHES 5.1.3
# ============================================================

for orchestration_state in (
    state_model.UniversalOrchestrationState.CREATED,
    state_model.UniversalOrchestrationState.ACTIVE,
    state_model.UniversalOrchestrationState.WAITING,
    state_model.UniversalOrchestrationState.SUSPENDED,
):

    plan = make_single_plan(
        "enter-recovering-"
        + orchestration_state.value
    )

    result = evaluate(
        plan=plan,
        orchestration_state=orchestration_state,
        statuses={
            "job-a": "failed",
        },
    )

    legal = (
        state_model
        .can_transition_universal_orchestration_state(
            current_state=orchestration_state,
            target_state=state_model.UniversalOrchestrationState.RECOVERING,
        )
    )

    check(
        "may_enter_recovering_matches_"
        + orchestration_state.value,
        result.may_enter_recovering
        == legal,
    )


# ============================================================
# 19. NON-RECOVERY DECISIONS CANNOT ENTER RECOVERING
# ============================================================

for status in (
    "created",
    "running",
    "suspended",
    "succeeded",
    "cancelled",
    "dead_letter",
    "expired",
):

    plan = make_single_plan(
        "non-recovery-enter-"
        + status
    )

    result = evaluate(
        plan=plan,
        orchestration_state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "job-a": status,
        },
    )

    check(
        "non_recoverable_cannot_enter_"
        + status,
        not result.may_enter_recovering,
    )


# ============================================================
# 20. HELPER CONSISTENCY
# ============================================================

samples = (
    mixed,
    suspended_only,
    recovering_failed,
    cancelled_result,
    missing_result,
    precedence_policy,
)


for index, result in enumerate(
    samples,
    start=1,
):

    check(
        "helper_recovery_required_"
        + str(index),
        result.is_recovery_required
        ==
        (
            result.disposition
            is
            recovery.UniversalOrchestrationRecoveryDisposition.RECOVERABLE
        ),
    )

    check(
        "helper_unrecoverable_"
        + str(index),
        result.is_unrecoverable
        ==
        (
            result.disposition
            is
            recovery.UniversalOrchestrationRecoveryDisposition.UNRECOVERABLE
        ),
    )

    check(
        "helper_unresolved_"
        + str(index),
        result.is_unresolved
        ==
        (
            result.disposition
            is
            recovery.UniversalOrchestrationRecoveryDisposition.UNRESOLVED
        ),
    )

    check(
        "helper_not_required_"
        + str(index),
        result.is_recovery_not_required
        ==
        (
            result.disposition
            is
            recovery.UniversalOrchestrationRecoveryDisposition.NOT_REQUIRED
        ),
    )


# ============================================================
# 21. DERIVED EVIDENCE
# ============================================================

check(
    "identity_derived",
    mixed.identity
    is
    mixed.progress_snapshot.identity,
)

check(
    "state_derived",
    mixed.orchestration_state
    is
    state_model.UniversalOrchestrationState.ACTIVE,
)

check(
    "failed_candidates_derived",
    mixed.recovery_candidate_job_ids
    == ("a",),
)

check(
    "missing_ids_derived",
    missing_result.missing_status_job_ids
    ==
    missing_result.progress_snapshot.missing_status_job_ids,
)


# ============================================================
# 22. IMMUTABILITY
# ============================================================

for field in fields(
    mixed
):

    try:

        setattr(
            mixed,
            field.name,
            None,
        )

    except Exception:

        immutable = True

    else:

        immutable = False

    check(
        "immutable_"
        + field.name,
        immutable,
    )


# ============================================================
# 23. DECISION ID DETERMINISM
# ============================================================

repeat_ids = tuple(
    evaluate(
        plan=mixed_plan,
        orchestration_state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "a": "failed",
            "b": "running",
            "c": "queued",
            "d": "succeeded",
        },
    )
    .recovery_decision_id
    for _
    in range(
        20
    )
)


check(
    "decision_id_deterministic",
    len(
        set(
            repeat_ids
        )
    )
    == 1,
)

check(
    "decision_id_length",
    len(
        repeat_ids[0]
    )
    == 64,
    repeat_ids[0],
)

check(
    "decision_id_upper_hex",
    all(
        character
        in "0123456789ABCDEF"
        for character
        in repeat_ids[0]
    ),
)


# ============================================================
# 24. DECISION ID SENSITIVITY
# ============================================================

active_id = mixed.recovery_decision_id


recovering_id = evaluate(
    plan=mixed_plan,
    orchestration_state=state_model.UniversalOrchestrationState.RECOVERING,
    statuses={
        "a": "failed",
        "b": "running",
        "c": "queued",
        "d": "succeeded",
    },
).recovery_decision_id


check(
    "decision_id_state_sensitive",
    active_id
    != recovering_id,
)


different_progress_id = evaluate(
    plan=mixed_plan,
    orchestration_state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "created",
        "b": "running",
        "c": "queued",
        "d": "succeeded",
    },
).recovery_decision_id


check(
    "decision_id_progress_sensitive",
    active_id
    != different_progress_id,
)


other_run_plan = make_plan(
    run_id="mixed-work-other-run",
    jobs_tuple=(
        make_job(
            job_id="a"
        ),
        make_job(
            job_id="b"
        ),
        make_job(
            job_id="c"
        ),
        make_job(
            job_id="d"
        ),
    ),
)


other_run_id = evaluate(
    plan=other_run_plan,
    orchestration_state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "failed",
        "b": "running",
        "c": "queued",
        "d": "succeeded",
    },
).recovery_decision_id


check(
    "decision_id_run_sensitive",
    active_id
    != other_run_id,
)


# ============================================================
# 25. SOURCE SNAPSHOTS NOT MUTATED
# ============================================================

state_snapshot = make_state(
    plan=mixed_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
)

progress_snapshot = make_progress(
    plan=mixed_plan,
    statuses={
        "a": "failed",
        "b": "running",
        "c": "queued",
        "d": "succeeded",
    },
)


state_before = (
    state_snapshot.identity,
    state_snapshot.state,
    state_snapshot.schema_version,
)

progress_before = (
    progress_snapshot.execution_plan,
    progress_snapshot.status_evidence,
    progress_snapshot.conditional_branching_decisions,
    progress_snapshot.schema_version,
    progress_snapshot.progress_snapshot_id,
)


_ = recovery.evaluate_universal_orchestration_recovery(
    state_snapshot=state_snapshot,
    progress_snapshot=progress_snapshot,
)


state_after = (
    state_snapshot.identity,
    state_snapshot.state,
    state_snapshot.schema_version,
)

progress_after = (
    progress_snapshot.execution_plan,
    progress_snapshot.status_evidence,
    progress_snapshot.conditional_branching_decisions,
    progress_snapshot.schema_version,
    progress_snapshot.progress_snapshot_id,
)


check(
    "state_snapshot_not_mutated",
    state_before
    == state_after,
)

check(
    "progress_snapshot_not_mutated",
    progress_before
    == progress_after,
)


# ============================================================
# 26. EXPLANATION CONTRACT
# ============================================================

explanation = (
    recovery
    .explain_universal_orchestration_recovery_v1()
)


check(
    "explanation_mappingproxy",
    isinstance(
        explanation,
        MappingProxyType,
    ),
)

check(
    "phase_exact",
    explanation.get(
        "phase"
    )
    == "5.1.13",
)

check(
    "component_exact",
    explanation.get(
        "component"
    )
    == "Universal Orchestration Recovery",
)

check(
    "stored_fields_explanation_exact",
    explanation.get(
        "stored_fields"
    )
    == (
        "state_snapshot",
        "progress_snapshot",
        "schema_version",
    ),
)

check(
    "state_authority_exact",
    "5.1.3"
    in explanation.get(
        "state_authority",
        "",
    ),
)

check(
    "progress_authority_exact",
    "5.1.11"
    in explanation.get(
        "progress_authority",
        "",
    ),
)

check(
    "persistence_boundary_exact",
    "5.1.14"
    in explanation.get(
        "persistence_boundary",
        "",
    ),
)

check(
    "completion_boundary_exact",
    "5.1.15"
    in explanation.get(
        "completion_boundary",
        "",
    ),
)

check(
    "termination_boundary_exact",
    "5.1.16"
    in explanation.get(
        "termination_boundary",
        "",
    ),
)

check(
    "evidence_boundary_exact",
    "5.1.17"
    in explanation.get(
        "evidence_boundary",
        "",
    ),
)


# ============================================================
# 27. REQUIRED PROHIBITIONS
# ============================================================

required_prohibitions = (
    "does not transition orchestration state",
    "does not reopen terminal orchestration states",
    "does not mutate UniversalJob.status",
    "does not mutate UniversalJob.progress",
    "does not calculate retry attempts",
    "does not enforce retry budgets",
    "does not calculate retry backoff",
    "does not schedule retries",
    "does not requeue jobs",
    "does not enqueue jobs",
    "does not dequeue jobs",
    "does not claim jobs",
    "does not invoke Queue Recovery",
    "does not invoke Worker Recovery",
    "does not restart workers",
    "does not assign workers",
    "does not acquire leases",
    "does not release leases",
    "does not restore checkpoints",
    "does not read checkpoint payloads",
    "does not dispatch runtime handlers",
    "does not execute jobs",
    "does not recompute dependency resolution",
    "does not evaluate stage readiness",
    "does not evaluate runtime handoff",
    "does not reevaluate conditional branches",
    "does not recompute progress topology",
    "does not access Runtime State Store",
    "does not persist recovery decisions",
    "does not determine orchestration completion",
    "does not determine orchestration success",
    "does not determine orchestration failure",
    "does not cancel orchestration",
    "does not terminate orchestration",
    "does not record permanent evidence",
    "does not use wall clock",
    "does not perform filesystem I/O",
    "does not perform network I/O",
    "does not perform database I/O",
    "does not import Universal Coordination Framework",
    "does not invoke pipeline coordinators",
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
# 28. IMPORT BOUNDARY
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

        module = (
            node.module
            or ""
        )

        if module.startswith(
            "backend.server"
        ):

            backend_imports.append(
                module
            )


check(
    "backend_imports_exact",
    backend_imports
    == [
        "backend.server.runtime.universal_orchestration.state_model",
        "backend.server.runtime.universal_orchestration.progress_tracking",
    ],
    backend_imports,
)


# ============================================================
# 29. FORBIDDEN IMPORTS
# ============================================================

all_imports = []


for node in ast.walk(
    tree
):

    if isinstance(
        node,
        ast.Import,
    ):

        for alias in node.names:

            all_imports.append(
                alias.name
            )

    elif isinstance(
        node,
        ast.ImportFrom,
    ):

        if node.module:

            all_imports.append(
                node.module
            )


for forbidden_module in (
    "time",
    "datetime",
    "uuid",
    "random",
    "asyncio",
    "threading",
    "multiprocessing",
    "os",
    "subprocess",
    "socket",
    "sqlite3",

    "backend.server.runtime.runtime_state_store",
    "backend.server.runtime.runtime_lifecycle_manager",

    "backend.server.runtime.universal_queue",
    "backend.server.runtime.universal_worker",

    "backend.server.runtime.universal_runtime_registration",
    "backend.server.runtime.universal_runtime_worker_v1",
    "backend.server.runtime.universal_runtime_infrastructure",

    "backend.server.runtime.universal_orchestration.stage_readiness",
    "backend.server.runtime.universal_orchestration.runtime_handoff",
    "backend.server.runtime.universal_orchestration.conditional_branching",
    "backend.server.runtime.universal_orchestration.suspension_resume_eligibility",

    "backend.server.coordination",
    "backend.server.orchestration",

    "backend.server.jobs.universal_knowledge_orchestrator",
    "backend.server.pipelines.connect_domain.coordinator",
):

    matches = tuple(
        imported
        for imported
        in all_imports
        if (
            imported
            == forbidden_module
            or
            imported.startswith(
                forbidden_module
                + "."
            )
        )
    )

    check(
        "forbidden_import_absent_"
        + forbidden_module.replace(
            ".",
            "_"
        ),
        not matches,
        matches,
    )


# ============================================================
# 30. FORBIDDEN CALLS
# ============================================================

forbidden_calls = {
    "eval",
    "exec",
    "compile",

    "open",
    "read_text",
    "write_text",

    "sleep",
    "wait",
    "poll",

    "time",
    "time_ns",
    "now",
    "utcnow",

    "enqueue_job",
    "schedule_job",
    "dequeue_job",
    "claim_job",
    "requeue_job",

    "assign_universal_worker",
    "acquire_universal_worker_lease",

    "transition_universal_orchestration_state",

    "track_universal_orchestration_progress",

    "dispatch_registered_runtime_handler",
    "execute_registered_runtime_job_v1",

    "get_runtime_state_store_registry",

    "persist",
    "save",
    "dispatch",
    "execute",

    "recover",
    "retry",
    "restart",
}


found_forbidden = []


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

        found_forbidden.append(
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
    not found_forbidden,
    found_forbidden,
)


# ============================================================
# 31. FORBIDDEN ATTRIBUTE ACCESS
# ============================================================

attrs = tuple(
    node.attr
    for node
    in ast.walk(
        tree
    )
    if isinstance(
        node,
        ast.Attribute,
    )
)


for forbidden_attr in (
    "attempt_count",
    "attempts",
    "max_attempts",
    "retry_policy",

    "checkpoint_reference",

    "payload",
    "payload_reference",
    "metadata",
    "result_reference",

    "queue_id",
    "worker_id",
    "lease_id",

    "created_at",
    "updated_at",
    "scheduled_at",

    "readiness",
    "handoff",
):

    check(
        "forbidden_attribute_absent_"
        + forbidden_attr,
        forbidden_attr
        not in attrs,
    )


# ============================================================
# 32. PROTECTED AUTHORITIES
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
# 33. FINAL AST
# ============================================================

final_ast = ast_sha(
    RECOVERY_PATH
)


check(
    "recovery_ast_final",
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


failures = tuple(
    (
        name,
        detail,
    )
    for name, ok, detail
    in checks
    if not ok
)


lines = [
    (
        "PHASE 5.1.13 — UNIVERSAL ORCHESTRATION "
        "RECOVERY ADVERSARIAL REGRESSION"
    ),

    "=" * 118,

    "",

    (
        "ORCHESTRATION RECOVERY AST SHA256: "
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
            "-" * 118,
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

        "=" * 118,

        (
            "ADVERSARIAL ORCHESTRATION RECOVERY REGRESSION: "
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

        "5.1.13 AUTHORITY MODIFIED DURING REGRESSION: NO",
        "5.1.1–5.1.12 FROZEN AUTHORITIES MODIFIED: NO",
        "PHASE 4 WORKER RECOVERY MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "RECOVERY DISPOSITIONS:",
        "  NOT_REQUIRED",
        "  RECOVERABLE",
        "  UNRECOVERABLE",
        "  UNRESOLVED",

        "",

        "FAILED EFFECTIVE WORK:",
        "  RECOVERABLE",

        "CANCELLED EFFECTIVE WORK:",
        "  UNRECOVERABLE",

        "DEAD_LETTER / EXPIRED EFFECTIVE WORK:",
        "  UNRESOLVED — RETRY POLICY DEPENDENT",

        "MISSING STATUS EVIDENCE:",
        "  UNRESOLVED",

        "UNRESOLVED BRANCH ACTIVITY:",
        "  UNRESOLVED",

        "",

        "SUSPENDED STATUS BY ITSELF IS RECOVERY FAILURE: NO",
        "LEASED/RUNNING STATUS BY ITSELF IS RECOVERY FAILURE: NO",

        "",

        "EXCLUDED FAILED/CANCELLED WORK AFFECTS RECOVERY: NO",

        "",

        "PARTIAL FAILED + ACTIVE HEALTHY WORK:",
        "  RECOVERABLE",

        "",

        "TERMINAL ORCHESTRATION OVERRIDES JOB EVIDENCE: YES",
        "TERMINAL ORCHESTRATION REOPENED: NO",

        "",

        "RECOVERING STATE MAY STILL DESCRIBE RECOVERY NEED: YES",
        "RECOVERING STATE MAY ENTER RECOVERING AGAIN: NO",

        "",

        "MAY_ENTER_RECOVERING USES 5.1.3 LEGALITY: YES",

        "",

        "DECISION ID DETERMINISTIC: YES",
        "DECISION ID STATE SENSITIVE: YES",
        "DECISION ID PROGRESS SENSITIVE: YES",
        "DECISION ID RUN SENSITIVE: YES",

        "",

        "STATE SNAPSHOT MUTATED: NO",
        "PROGRESS SNAPSHOT MUTATED: NO",

        "",

        "RETRY ATTEMPT ACCOUNTING: NO",
        "RETRY BUDGET ENFORCEMENT: NO",
        "RETRY BACKOFF: NO",
        "RETRY SCHEDULING: NO",

        "",

        "QUEUE RECOVERY INVOKED: NO",
        "WORKER RECOVERY INVOKED: NO",

        "",

        "STATE TRANSITION: NO",
        "JOB REQUEUE: NO",
        "QUEUE ACTIVITY: NO",
        "WORKER ACTIVITY: NO",
        "LEASE ACTIVITY: NO",

        "",

        "CHECKPOINT RESTORE: NO",
        "CHECKPOINT PAYLOAD READ: NO",

        "",

        "READINESS EVALUATION: NO",
        "HANDOFF EVALUATION: NO",
        "CONDITIONAL REEVALUATION: NO",
        "PROGRESS RECOMPUTATION: NO",

        "",

        "HANDLER DISPATCH: NO",
        "JOB EXECUTION: NO",

        "",

        "RUNTIME STATE STORE ACCESS: NO",
        "PERSISTENCE: NO",
        "COMPLETION RESOLUTION: NO",
        "SUCCESS/FAILURE RESOLUTION: NO",
        "TERMINATION RESOLUTION: NO",
        "PERMANENT EVIDENCE RECORDING: NO",

        "",

        "UNIVERSAL COORDINATION FRAMEWORK ACCESS: NO",
        "PIPELINE COORDINATOR ACCESS: NO",

        "",

        (
            "STATUS: REGRESSION PASS "
            "— FINAL CERTIFICATION REQUIRED"
            if passed == total
            else
            "STATUS: REGRESSION FAILED "
            "— PATCH REQUIRED"
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
        "Phase 5.1.13 adversarial regression failed."
    )
