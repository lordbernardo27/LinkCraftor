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

COMPLETION_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_orchestration"
    / "completion_resolution.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_1_15_orchestration_completion_regression.txt"
)

EXPECTED_COMPLETION_AST = (
    "1311EEBEB9622AF5D4CF6F4D7CB14FF83B169C748A01DDD144A8000301A5CBD4"
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
    "5.1.13_recovery": (
        ROOT / "backend/server/runtime/universal_orchestration/recovery.py",
        "4465A7AF795512594023D19E27A175CA060ACD2845BB4530B77FF8D69C40B16F",
    ),
    "5.1.14_persistence": (
        ROOT / "backend/server/runtime/universal_orchestration/persistence_interface.py",
        "5B7F640250498B4B5320C3702112D163E16B6878C412447623E5C0FF93608CCA",
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


def ast_sha(path: Path) -> str:
    source = path.read_text(encoding="utf-8-sig")
    tree = ast.parse(source)
    canonical = ast.dump(
        tree,
        annotate_fields=True,
        include_attributes=False,
    )
    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest().upper()


if ast_sha(COMPLETION_PATH) != EXPECTED_COMPLETION_AST:
    raise SystemExit(
        "5.1.15 AST changed before adversarial regression."
    )


for name, (path, expected) in PROTECTED.items():
    actual = ast_sha(path)
    if actual != expected:
        raise SystemExit(
            "Protected authority mismatch before regression: "
            + name
        )


sys.path.insert(0, str(ROOT))


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
    "universal_orchestration.completion_resolution"
)

sys.modules.pop(module_name, None)

completion = importlib.import_module(
    module_name
)


checks = []


def check(name, condition, detail=""):
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
        dependency_job_ids=tuple(dependencies),
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


def resolve(
    *,
    plan,
    state,
    statuses,
    decisions=(),
):
    return (
        completion
        .resolve_universal_orchestration_completion(
            state_snapshot=make_state(
                plan=plan,
                state=state,
            ),
            progress_snapshot=make_progress(
                plan=plan,
                statuses=statuses,
                decisions=decisions,
            ),
        )
    )


# ============================================================
# 1. EXACTNESS
# ============================================================

check(
    "ast_initial_exact",
    ast_sha(COMPLETION_PATH)
    == EXPECTED_COMPLETION_AST,
)

check(
    "version_exact",
    completion.UNIVERSAL_ORCHESTRATION_COMPLETION_RESOLUTION_VERSION
    ==
    "universal_orchestration_completion_resolution_v5.1.15",
)

check(
    "schema_exact",
    completion.UNIVERSAL_ORCHESTRATION_COMPLETION_RESOLUTION_SCHEMA_VERSION
    ==
    "universal_orchestration_completion_resolution_schema_v1",
)

check(
    "hash_exact",
    completion.UNIVERSAL_ORCHESTRATION_COMPLETION_DECISION_HASH_ALGORITHM
    == "sha256",
)

check(
    "dispositions_exact",
    tuple(
        item.value
        for item
        in completion.UniversalOrchestrationCompletionDisposition
    )
    == (
        "not_ready",
        "succeeded",
        "failed",
        "unresolved",
        "deferred_to_termination",
    ),
)

check(
    "reasons_exact",
    tuple(
        item.value
        for item
        in completion.UniversalOrchestrationCompletionReason
    )
    == (
        "terminal_orchestration_succeeded",
        "terminal_orchestration_failed",
        "terminal_orchestration_cancelled",
        "missing_status_evidence",
        "unresolved_branch_activity",
        "no_effective_work",
        "cancelled_effective_work",
        "nonterminal_effective_work",
        "all_effective_work_succeeded",
        "terminal_unsuccessful_effective_work",
    ),
)


# ============================================================
# 2. INVALID INPUTS
# ============================================================

base_plan = make_plan(
    run_id="completion-invalid-input",
    jobs_tuple=(
        make_job(job_id="job-a"),
    ),
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
        completion.resolve_universal_orchestration_completion(
            state_snapshot=bad,
            progress_snapshot=base_progress,
        )
    except completion.UniversalOrchestrationCompletionError as exc:
        rejected = (
            exc.code
            == "invalid_completion_state_snapshot"
        )
    else:
        rejected = False

    check(
        "invalid_state_snapshot_" + str(index),
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
        completion.resolve_universal_orchestration_completion(
            state_snapshot=base_state,
            progress_snapshot=bad,
        )
    except completion.UniversalOrchestrationCompletionError as exc:
        rejected = (
            exc.code
            == "invalid_completion_progress_snapshot"
        )
    else:
        rejected = False

    check(
        "invalid_progress_snapshot_" + str(index),
        rejected,
    )


# ============================================================
# 3. CROSS IDENTITY
# ============================================================

other_plan = make_plan(
    run_id="completion-other",
    jobs_tuple=(
        make_job(job_id="job-a"),
    ),
)


try:
    completion.resolve_universal_orchestration_completion(
        state_snapshot=make_state(
            plan=other_plan,
            state=state_model.UniversalOrchestrationState.ACTIVE,
        ),
        progress_snapshot=base_progress,
    )
except completion.UniversalOrchestrationCompletionError as exc:
    cross_identity_rejected = (
        exc.code
        == "completion_identity_mismatch"
    )
else:
    cross_identity_rejected = False


check(
    "cross_identity_rejected",
    cross_identity_rejected,
)


# ============================================================
# 4. STORED FIELDS
# ============================================================

field_names = tuple(
    field.name
    for field
    in fields(
        completion.UniversalOrchestrationCompletionDecision
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
    "target_terminal_state",
    "completion_decision_id",
    "may_transition_to_target",
    "created_at",
    "updated_at",
    "timestamp",
    "retry_policy",
    "attempt_count",
):
    check(
        "forbidden_stored_" + forbidden,
        forbidden not in field_names,
    )


# ============================================================
# 5. EVERY NONTERMINAL JOB STATUS
# ============================================================

nonterminal_plan = make_plan(
    run_id="completion-nonterminal",
    jobs_tuple=(
        make_job(job_id="job-a"),
    ),
)


for status in (
    "created",
    "queued",
    "scheduled",
    "leased",
    "running",
    "suspended",
):
    result = resolve(
        plan=nonterminal_plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "job-a": status,
        },
    )

    check(
        "nonterminal_not_ready_" + status,
        result.disposition
        is
        completion.UniversalOrchestrationCompletionDisposition.NOT_READY,
    )

    check(
        "nonterminal_reason_" + status,
        result.reason
        is
        completion.UniversalOrchestrationCompletionReason.NONTERMINAL_EFFECTIVE_WORK,
    )

    check(
        "nonterminal_target_none_" + status,
        result.target_terminal_state
        is None,
    )


# ============================================================
# 6. TERMINAL JOB STATUS MATRIX
# ============================================================

terminal_plan = make_plan(
    run_id="completion-terminal-job-matrix",
    jobs_tuple=(
        make_job(job_id="job-a"),
    ),
)


matrix = {
    "succeeded": (
        completion.UniversalOrchestrationCompletionDisposition.SUCCEEDED,
        state_model.UniversalOrchestrationState.SUCCEEDED,
    ),
    "failed": (
        completion.UniversalOrchestrationCompletionDisposition.FAILED,
        state_model.UniversalOrchestrationState.FAILED,
    ),
    "dead_letter": (
        completion.UniversalOrchestrationCompletionDisposition.FAILED,
        state_model.UniversalOrchestrationState.FAILED,
    ),
    "expired": (
        completion.UniversalOrchestrationCompletionDisposition.FAILED,
        state_model.UniversalOrchestrationState.FAILED,
    ),
    "cancelled": (
        completion.UniversalOrchestrationCompletionDisposition.DEFERRED_TO_TERMINATION,
        None,
    ),
}


for status, (
    expected_disposition,
    expected_target,
) in matrix.items():

    result = resolve(
        plan=terminal_plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "job-a": status,
        },
    )

    check(
        "terminal_job_disposition_" + status,
        result.disposition
        is expected_disposition,
    )

    check(
        "terminal_job_target_" + status,
        result.target_terminal_state
        is expected_target,
    )


# ============================================================
# 7. MIXED TERMINAL POPULATIONS
# ============================================================

mixed_plan = make_plan(
    run_id="completion-mixed",
    jobs_tuple=(
        make_job(job_id="a"),
        make_job(job_id="b"),
        make_job(job_id="c"),
    ),
)


mixed_cases = (
    (
        "all_success",
        {
            "a": "succeeded",
            "b": "succeeded",
            "c": "succeeded",
        },
        completion.UniversalOrchestrationCompletionDisposition.SUCCEEDED,
    ),
    (
        "success_failed",
        {
            "a": "succeeded",
            "b": "failed",
            "c": "succeeded",
        },
        completion.UniversalOrchestrationCompletionDisposition.FAILED,
    ),
    (
        "success_dead_letter",
        {
            "a": "succeeded",
            "b": "dead_letter",
            "c": "succeeded",
        },
        completion.UniversalOrchestrationCompletionDisposition.FAILED,
    ),
    (
        "success_expired",
        {
            "a": "succeeded",
            "b": "expired",
            "c": "succeeded",
        },
        completion.UniversalOrchestrationCompletionDisposition.FAILED,
    ),
    (
        "failed_dead_expired",
        {
            "a": "failed",
            "b": "dead_letter",
            "c": "expired",
        },
        completion.UniversalOrchestrationCompletionDisposition.FAILED,
    ),
    (
        "cancelled_plus_failed",
        {
            "a": "cancelled",
            "b": "failed",
            "c": "succeeded",
        },
        completion.UniversalOrchestrationCompletionDisposition.DEFERRED_TO_TERMINATION,
    ),
)


for name, statuses, expected in mixed_cases:
    result = resolve(
        plan=mixed_plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses=statuses,
    )

    check(
        "mixed_" + name,
        result.disposition
        is expected,
    )


# ============================================================
# 8. NONTERMINAL BLOCKS FAILURE COMPLETION
# ============================================================

for nonterminal_status in (
    "created",
    "queued",
    "scheduled",
    "leased",
    "running",
    "suspended",
):
    result = resolve(
        plan=mixed_plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "a": "failed",
            "b": nonterminal_status,
            "c": "succeeded",
        },
    )

    check(
        "mixed_failure_nonterminal_not_ready_"
        + nonterminal_status,
        result.disposition
        is
        completion.UniversalOrchestrationCompletionDisposition.NOT_READY,
    )


# ============================================================
# 9. TERMINAL ORCHESTRATION OVERRIDES
# ============================================================

for state in (
    state_model.UniversalOrchestrationState.SUCCEEDED,
    state_model.UniversalOrchestrationState.FAILED,
    state_model.UniversalOrchestrationState.CANCELLED,
):
    for status in (
        "created",
        "running",
        "failed",
        "cancelled",
        "dead_letter",
        "expired",
        None,
    ):
        result = resolve(
            plan=terminal_plan,
            state=state,
            statuses={
                "job-a": status,
            },
        )

        if state is state_model.UniversalOrchestrationState.SUCCEEDED:
            expected = (
                completion
                .UniversalOrchestrationCompletionDisposition
                .SUCCEEDED
            )
        elif state is state_model.UniversalOrchestrationState.FAILED:
            expected = (
                completion
                .UniversalOrchestrationCompletionDisposition
                .FAILED
            )
        else:
            expected = (
                completion
                .UniversalOrchestrationCompletionDisposition
                .DEFERRED_TO_TERMINATION
            )

        suffix = (
            state.value
            + "_"
            + (
                "missing"
                if status is None
                else status
            )
        )

        check(
            "terminal_override_" + suffix,
            result.disposition
            is expected,
        )


# ============================================================
# 10. MISSING STATUS PRECEDENCE
# ============================================================

missing_result = resolve(
    plan=mixed_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": None,
        "b": "failed",
        "c": "cancelled",
    },
)


check(
    "missing_precedence_unresolved",
    missing_result.disposition
    is
    completion.UniversalOrchestrationCompletionDisposition.UNRESOLVED,
)

check(
    "missing_reason_exact",
    missing_result.reason
    is
    completion.UniversalOrchestrationCompletionReason.MISSING_STATUS_EVIDENCE,
)


# ============================================================
# 11. UNRESOLVED BRANCH PRECEDENCE
# ============================================================

branch_plan = make_plan(
    run_id="completion-branch",
    jobs_tuple=(
        make_job(job_id="root"),
        make_job(
            job_id="a",
            dependencies=("root",),
        ),
        make_job(
            job_id="b",
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
        },
    )
)


branch_result = resolve(
    plan=branch_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "root": "succeeded",
        "a": "succeeded",
        "b": "failed",
    },
    decisions=(
        unresolved_decision,
    ),
)


check(
    "unresolved_branch_unresolved",
    branch_result.disposition
    is
    completion.UniversalOrchestrationCompletionDisposition.UNRESOLVED,
)

check(
    "unresolved_branch_reason",
    branch_result.reason
    is
    completion.UniversalOrchestrationCompletionReason.UNRESOLVED_BRANCH_ACTIVITY,
)


# ============================================================
# 12. EXCLUDED WORK DOES NOT BLOCK COMPLETION
# ============================================================

excluded_decision = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=branch_fanout,
        condition_evidence={
            "a": True,
            "b": False,
        },
    )
)


excluded_failure = resolve(
    plan=branch_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "root": "succeeded",
        "a": "succeeded",
        "b": "failed",
    },
    decisions=(
        excluded_decision,
    ),
)


check(
    "excluded_failed_does_not_block",
    excluded_failure.disposition
    is
    completion.UniversalOrchestrationCompletionDisposition.SUCCEEDED,
)


excluded_cancelled = resolve(
    plan=branch_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "root": "succeeded",
        "a": "succeeded",
        "b": "cancelled",
    },
    decisions=(
        excluded_decision,
    ),
)


check(
    "excluded_cancelled_does_not_defer",
    excluded_cancelled.disposition
    is
    completion.UniversalOrchestrationCompletionDisposition.SUCCEEDED,
)


# ============================================================
# 13. ALL NONTERMINAL ORCHESTRATION STATES CAN RESOLVE SUCCESS
# ============================================================

for state in (
    state_model.UniversalOrchestrationState.CREATED,
    state_model.UniversalOrchestrationState.ACTIVE,
    state_model.UniversalOrchestrationState.WAITING,
    state_model.UniversalOrchestrationState.SUSPENDED,
    state_model.UniversalOrchestrationState.RECOVERING,
):
    result = resolve(
        plan=terminal_plan,
        state=state,
        statuses={
            "job-a": "succeeded",
        },
    )

    check(
        "success_resolution_state_" + state.value,
        result.disposition
        is
        completion.UniversalOrchestrationCompletionDisposition.SUCCEEDED,
    )

    expected_legality = (
        state_model
        .can_transition_universal_orchestration_state(
            current_state=state,
            target_state=state_model.UniversalOrchestrationState.SUCCEEDED,
        )
    )

    check(
        "success_transition_legality_" + state.value,
        result.may_transition_to_target
        == expected_legality,
    )


# ============================================================
# 14. ALL NONTERMINAL ORCHESTRATION STATES CAN RESOLVE FAILURE
# ============================================================

for state in (
    state_model.UniversalOrchestrationState.CREATED,
    state_model.UniversalOrchestrationState.ACTIVE,
    state_model.UniversalOrchestrationState.WAITING,
    state_model.UniversalOrchestrationState.SUSPENDED,
    state_model.UniversalOrchestrationState.RECOVERING,
):
    result = resolve(
        plan=terminal_plan,
        state=state,
        statuses={
            "job-a": "failed",
        },
    )

    check(
        "failure_resolution_state_" + state.value,
        result.disposition
        is
        completion.UniversalOrchestrationCompletionDisposition.FAILED,
    )

    expected_legality = (
        state_model
        .can_transition_universal_orchestration_state(
            current_state=state,
            target_state=state_model.UniversalOrchestrationState.FAILED,
        )
    )

    check(
        "failure_transition_legality_" + state.value,
        result.may_transition_to_target
        == expected_legality,
    )


# ============================================================
# 15. TARGET ALREADY REALIZED
# ============================================================

terminal_success = resolve(
    plan=terminal_plan,
    state=state_model.UniversalOrchestrationState.SUCCEEDED,
    statuses={
        "job-a": "running",
    },
)


check(
    "terminal_success_realized",
    terminal_success.is_target_state_already_realized,
)

check(
    "terminal_success_may_transition_false",
    not terminal_success.may_transition_to_target,
)


terminal_failed = resolve(
    plan=terminal_plan,
    state=state_model.UniversalOrchestrationState.FAILED,
    statuses={
        "job-a": "succeeded",
    },
)


check(
    "terminal_failed_realized",
    terminal_failed.is_target_state_already_realized,
)

check(
    "terminal_failed_may_transition_false",
    not terminal_failed.may_transition_to_target,
)


# ============================================================
# 16. DERIVED JOB-ID BUCKETS
# ============================================================

bucket_result = resolve(
    plan=make_plan(
        run_id="completion-buckets",
        jobs_tuple=(
            make_job(job_id="a"),
            make_job(job_id="b"),
            make_job(job_id="c"),
            make_job(job_id="d"),
        ),
    ),
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "running",
        "b": "succeeded",
        "c": "failed",
        "d": "cancelled",
    },
)


check(
    "bucket_nonterminal_exact",
    bucket_result.nonterminal_effective_job_ids
    == ("a",),
)

check(
    "bucket_success_exact",
    bucket_result.succeeded_effective_job_ids
    == ("b",),
)

check(
    "bucket_failure_exact",
    bucket_result.failed_effective_job_ids
    == ("c",),
)

check(
    "bucket_cancelled_exact",
    bucket_result.cancelled_effective_job_ids
    == ("d",),
)


# ============================================================
# 17. HELPER CONSISTENCY
# ============================================================

samples = (
    resolve(
        plan=terminal_plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={"job-a": "succeeded"},
    ),
    resolve(
        plan=terminal_plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={"job-a": "failed"},
    ),
    resolve(
        plan=terminal_plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={"job-a": "running"},
    ),
    resolve(
        plan=terminal_plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={"job-a": None},
    ),
    resolve(
        plan=terminal_plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={"job-a": "cancelled"},
    ),
)


for index, result in enumerate(samples, start=1):
    check(
        "helper_complete_" + str(index),
        result.is_complete
        ==
        (
            result.disposition
            in (
                completion.UniversalOrchestrationCompletionDisposition.SUCCEEDED,
                completion.UniversalOrchestrationCompletionDisposition.FAILED,
            )
        ),
    )

    check(
        "helper_success_" + str(index),
        result.is_successful
        ==
        (
            result.disposition
            is
            completion.UniversalOrchestrationCompletionDisposition.SUCCEEDED
        ),
    )

    check(
        "helper_failed_" + str(index),
        result.is_failed
        ==
        (
            result.disposition
            is
            completion.UniversalOrchestrationCompletionDisposition.FAILED
        ),
    )

    check(
        "helper_unresolved_" + str(index),
        result.is_unresolved
        ==
        (
            result.disposition
            is
            completion.UniversalOrchestrationCompletionDisposition.UNRESOLVED
        ),
    )

    check(
        "helper_deferred_" + str(index),
        result.is_deferred_to_termination
        ==
        (
            result.disposition
            is
            completion.UniversalOrchestrationCompletionDisposition.DEFERRED_TO_TERMINATION
        ),
    )


# ============================================================
# 18. IMMUTABILITY
# ============================================================

immutable_sample = samples[0]


for field in fields(immutable_sample):
    try:
        setattr(
            immutable_sample,
            field.name,
            None,
        )
    except Exception:
        immutable = True
    else:
        immutable = False

    check(
        "immutable_" + field.name,
        immutable,
    )


# ============================================================
# 19. DECISION-ID DETERMINISM + SENSITIVITY
# ============================================================

same_ids = tuple(
    resolve(
        plan=terminal_plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "job-a": "succeeded",
        },
    ).completion_decision_id
    for _
    in range(20)
)


check(
    "decision_id_deterministic",
    len(set(same_ids)) == 1,
)

check(
    "decision_id_length",
    len(same_ids[0]) == 64,
    same_ids[0],
)

check(
    "decision_id_upper_hex",
    all(
        character in "0123456789ABCDEF"
        for character
        in same_ids[0]
    ),
)


different_state_id = resolve(
    plan=terminal_plan,
    state=state_model.UniversalOrchestrationState.WAITING,
    statuses={
        "job-a": "succeeded",
    },
).completion_decision_id


check(
    "decision_id_state_sensitive",
    same_ids[0] != different_state_id,
)


different_progress_id = resolve(
    plan=terminal_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "job-a": "failed",
    },
).completion_decision_id


check(
    "decision_id_progress_sensitive",
    same_ids[0] != different_progress_id,
)


other_run_plan = make_plan(
    run_id="completion-run-sensitive",
    jobs_tuple=(
        make_job(job_id="job-a"),
    ),
)


other_run_id = resolve(
    plan=other_run_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "job-a": "succeeded",
    },
).completion_decision_id


check(
    "decision_id_run_sensitive",
    same_ids[0] != other_run_id,
)


# ============================================================
# 20. EXPLANATION CONTRACT
# ============================================================

explanation = (
    completion
    .explain_universal_orchestration_completion_resolution_v1()
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
    explanation.get("phase")
    == "5.1.15",
)

check(
    "component_exact",
    explanation.get("component")
    == "Universal Orchestration Completion Resolution",
)

check(
    "stored_fields_explanation_exact",
    explanation.get("stored_fields")
    == (
        "state_snapshot",
        "progress_snapshot",
        "schema_version",
    ),
)

check(
    "state_boundary_5_1_3",
    "5.1.3"
    in explanation.get(
        "state_authority",
        "",
    ),
)

check(
    "progress_boundary_5_1_11",
    "5.1.11"
    in explanation.get(
        "progress_authority",
        "",
    ),
)

check(
    "recovery_boundary_5_1_13",
    "5.1.13"
    in explanation.get(
        "recovery_boundary",
        "",
    ),
)

check(
    "persistence_boundary_5_1_14",
    "5.1.14"
    in explanation.get(
        "persistence_boundary",
        "",
    ),
)

check(
    "termination_boundary_5_1_16",
    "5.1.16"
    in explanation.get(
        "termination_boundary",
        "",
    ),
)

check(
    "evidence_boundary_5_1_17",
    "5.1.17"
    in explanation.get(
        "evidence_boundary",
        "",
    ),
)


# ============================================================
# 21. REQUIRED PROHIBITIONS
# ============================================================

required_prohibitions = (
    "does not transition orchestration state",
    "does not target CANCELLED",
    "does not reopen terminal orchestration states",
    "does not import orchestration recovery",
    "does not reevaluate orchestration recovery",
    "does not execute recovery",
    "does not inspect retry attempts",
    "does not inspect retry policy",
    "does not calculate retry backoff",
    "does not recompute conditional branches",
    "does not recompute progress",
    "does not invoke persistence port",
    "does not access Runtime State Store",
    "does not persist completion decisions",
    "does not record permanent audit evidence",
    "does not cancel orchestration",
    "does not terminate orchestration",
    "does not enqueue jobs",
    "does not dequeue jobs",
    "does not claim jobs",
    "does not assign workers",
    "does not manipulate leases",
    "does not dispatch runtime handlers",
    "does not execute jobs",
    "does not use wall clock",
    "does not perform filesystem I/O",
    "does not perform database I/O",
    "does not perform network I/O",
    "does not import Universal Coordination Framework",
    "does not invoke pipeline coordinators",
)


prohibitions = tuple(
    explanation.get("prohibitions")
    or ()
)


for index, item in enumerate(
    required_prohibitions,
    start=1,
):
    check(
        "prohibition_" + str(index),
        item in prohibitions,
        item,
    )


# ============================================================
# 22. IMPORT BOUNDARY
# ============================================================

source = COMPLETION_PATH.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(source)


backend_imports = []


for node in ast.walk(tree):
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
# 23. FORBIDDEN IMPORTS
# ============================================================

all_imports = []


for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            all_imports.append(
                alias.name
            )

    elif isinstance(node, ast.ImportFrom):
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
    "backend.server.runtime.runtime_persistence",

    "backend.server.runtime.universal_queue",
    "backend.server.runtime.universal_worker",

    "backend.server.runtime.universal_orchestration.recovery",
    "backend.server.runtime.universal_orchestration.persistence_interface",
    "backend.server.runtime.universal_orchestration.suspension_resume_eligibility",
    "backend.server.runtime.universal_orchestration.conditional_branching",

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
            imported == forbidden_module
            or
            imported.startswith(
                forbidden_module + "."
            )
        )
    )

    check(
        "forbidden_import_absent_"
        + forbidden_module.replace(".", "_"),
        not matches,
        matches,
    )


# ============================================================
# 24. FORBIDDEN CALLS
# ============================================================

forbidden_calls = {
    "transition_universal_orchestration_state",

    "evaluate_universal_orchestration_recovery",
    "evaluate_universal_orchestration_suspension_resume_eligibility",

    "track_universal_orchestration_progress",

    "append_record",
    "load_latest_record",
    "load_record",
    "list_record_history",

    "enqueue_job",
    "dequeue_job",
    "claim_job",
    "schedule_job",
    "requeue_job",

    "assign_universal_worker",
    "acquire_universal_worker_lease",

    "dispatch_registered_runtime_handler",
    "execute_registered_runtime_job_v1",

    "get_runtime_state_store_registry",

    "open",
    "read_text",
    "write_text",

    "time",
    "time_ns",
    "now",
    "utcnow",

    "persist",
    "save",
    "execute",
    "delete",
    "cancel",
    "terminate",
}


found_forbidden = []


for node in ast.walk(tree):
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
# 25. FORBIDDEN ATTRIBUTES
# ============================================================

attrs = tuple(
    node.attr
    for node
    in ast.walk(tree)
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
        forbidden_attr not in attrs,
    )


# ============================================================
# 26. PROTECTED AUTHORITIES
# ============================================================

for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(path)

    check(
        "protected_" + name,
        actual == expected,
        actual,
    )


# ============================================================
# 27. FINAL AST
# ============================================================

final_ast = ast_sha(
    COMPLETION_PATH
)


check(
    "completion_ast_final",
    final_ast
    == EXPECTED_COMPLETION_AST,
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

total = len(checks)


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
        "PHASE 5.1.15 — UNIVERSAL ORCHESTRATION "
        "COMPLETION RESOLUTION ADVERSARIAL REGRESSION"
    ),
    "=" * 118,
    "",
    (
        "ORCHESTRATION COMPLETION RESOLUTION AST SHA256: "
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
            "   " + detail
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
            "FAIL: " + name
        )

        if detail:
            lines.append(
                "   " + detail
            )


lines.extend(
    [
        "",
        "=" * 118,

        (
            "ADVERSARIAL ORCHESTRATION COMPLETION RESOLUTION REGRESSION: "
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

        "5.1.15 AUTHORITY MODIFIED DURING REGRESSION: NO",
        "5.1.1–5.1.14 FROZEN AUTHORITIES MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "NONTERMINAL EFFECTIVE WORK:",
        "  CREATED => NOT_READY",
        "  QUEUED => NOT_READY",
        "  SCHEDULED => NOT_READY",
        "  LEASED => NOT_READY",
        "  RUNNING => NOT_READY",
        "  SUSPENDED => NOT_READY",

        "",

        "TERMINAL EFFECTIVE WORK:",
        "  SUCCEEDED => SUCCEEDED",
        "  FAILED => FAILED",
        "  DEAD_LETTER => FAILED",
        "  EXPIRED => FAILED",
        "  CANCELLED => DEFERRED_TO_TERMINATION",

        "",

        "MISSING STATUS => UNRESOLVED",
        "UNRESOLVED BRANCH => UNRESOLVED",

        "",

        "EXCLUDED FAILED WORK BLOCKS SUCCESS: NO",
        "EXCLUDED CANCELLED WORK DEFERS TERMINATION: NO",

        "",

        "TERMINAL ORCHESTRATION OVERRIDES PROGRESS: YES",

        "",

        "SUCCEEDED TARGET DERIVED: YES",
        "FAILED TARGET DERIVED: YES",
        "CANCELLED TARGET DERIVED: NO",

        "",

        "5.1.3 TRANSITION LEGALITY CONSUMED: YES",
        "ACTUAL STATE TRANSITION: NO",

        "",

        "5.1.13 RECOVERY IMPORTED: NO",
        "RECOVERY REEVALUATION: NO",
        "RECOVERY EXECUTION: NO",

        "",

        "RETRY ATTEMPTS INSPECTED: NO",
        "RETRY POLICY INSPECTED: NO",
        "RETRY BACKOFF: NO",

        "",

        "PERSISTENCE PORT INVOKED: NO",
        "RUNTIME STATE STORE ACCESS: NO",

        "",

        "CANCELLATION RESOLUTION: NO",
        "TERMINATION EXECUTION: NO",

        "",

        "PERMANENT EVIDENCE RECORDING: NO",

        "",

        "QUEUE ACTIVITY: NO",
        "WORKER ACTIVITY: NO",
        "LEASE ACTIVITY: NO",
        "HANDLER DISPATCH: NO",
        "JOB EXECUTION: NO",

        "",

        "DECISION ID DETERMINISTIC: YES",
        "DECISION ID STATE SENSITIVE: YES",
        "DECISION ID PROGRESS SENSITIVE: YES",
        "DECISION ID RUN SENSITIVE: YES",

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
    "\n".join(lines),
    encoding="utf-8",
)


print(
    "\n".join(lines)
)


if passed != total:
    raise SystemExit(
        "Phase 5.1.15 adversarial regression failed."
    )
