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

ELIGIBILITY_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_orchestration"
    / "suspension_resume_eligibility.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_1_12_suspension_resume_eligibility_regression.txt"
)

EXPECTED_ELIGIBILITY_AST = (
    "476631641C740443FF7B3D1D1D0E9D6D155289BDCAF14526698528432CCF913A"
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

    "runtime_shutdown_process": (
        ROOT / "backend/server/runtime/runtime_shutdown_process.py",
        "7A159E206C73157064B70D15A1CE4A97AB3D77EBBC77B01A2554BC34224EB272",
    ),

    "runtime_lifecycle_manager": (
        ROOT / "backend/server/runtime/runtime_lifecycle_manager.py",
        "E6200CA0938B5D578954024D6E76E343FB39D9329CFD3ABE4B3AEF86E8204034",
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
        canonical.encode(
            "utf-8"
        )
    ).hexdigest().upper()


# ============================================================
# PRE-FLIGHT
# ============================================================

if not ELIGIBILITY_PATH.exists():

    raise SystemExit(
        "5.1.12 Suspension/Resume Eligibility authority is missing."
    )


initial_ast = ast_sha(
    ELIGIBILITY_PATH
)


if initial_ast != EXPECTED_ELIGIBILITY_AST:

    raise SystemExit(
        (
            "5.1.12 AST changed before adversarial regression.\n"
            "EXPECTED: "
            + EXPECTED_ELIGIBILITY_AST
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
    "universal_orchestration.suspension_resume_eligibility"
)

sys.modules.pop(
    module_name,
    None,
)

eligibility = importlib.import_module(
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
                job_id="job-a",
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
    status,
):

    evidence = (
        None
        if status is _MISSING
        else
        {
            "job-a":
                status,
        }
    )

    return (
        progress
        .track_universal_orchestration_progress(
            execution_plan=plan,
            status_evidence=evidence,
        )
    )


def evaluate(
    *,
    plan,
    orchestration_state,
    job_status,
):

    return (
        eligibility
        .evaluate_universal_orchestration_suspension_resume_eligibility(
            state_snapshot=make_state(
                plan=plan,
                state=orchestration_state,
            ),
            progress_snapshot=make_progress(
                plan=plan,
                status=job_status,
            ),
        )
    )


_MISSING = object()


# ============================================================
# 1. AUTHORITY EXACTNESS
# ============================================================

check(
    "ast_initial_exact",
    ast_sha(
        ELIGIBILITY_PATH
    )
    == EXPECTED_ELIGIBILITY_AST,
)

check(
    "version_exact",
    eligibility.UNIVERSAL_ORCHESTRATION_SUSPENSION_RESUME_ELIGIBILITY_VERSION
    ==
    "universal_orchestration_suspension_resume_eligibility_v5.1.12",
)

check(
    "schema_exact",
    eligibility.UNIVERSAL_ORCHESTRATION_SUSPENSION_RESUME_ELIGIBILITY_SCHEMA_VERSION
    ==
    "universal_orchestration_suspension_resume_eligibility_schema_v1",
)

check(
    "hash_algorithm_exact",
    eligibility.UNIVERSAL_ORCHESTRATION_SUSPENSION_RESUME_DECISION_HASH_ALGORITHM
    == "sha256",
)


expected_all = (
    "UNIVERSAL_ORCHESTRATION_SUSPENSION_RESUME_ELIGIBILITY_VERSION",
    "UNIVERSAL_ORCHESTRATION_SUSPENSION_RESUME_ELIGIBILITY_SCHEMA_VERSION",
    "UNIVERSAL_ORCHESTRATION_SUSPENSION_RESUME_DECISION_HASH_ALGORITHM",
    "UniversalOrchestrationSuspensionResumeEligibilityError",
    "UniversalOrchestrationSuspensionDisposition",
    "UniversalOrchestrationResumeDisposition",
    "UniversalOrchestrationSuspensionReason",
    "UniversalOrchestrationResumeReason",
    "UniversalOrchestrationSuspensionResumeEligibility",
    "evaluate_universal_orchestration_suspension_resume_eligibility",
    "explain_universal_orchestration_suspension_resume_eligibility_v1",
)


check(
    "public_api_exact",
    tuple(
        eligibility.__all__
    )
    == expected_all,
    eligibility.__all__,
)


# ============================================================
# 2. ENUM EXACTNESS
# ============================================================

check(
    "suspension_dispositions_exact",
    tuple(
        item.value
        for item
        in eligibility.UniversalOrchestrationSuspensionDisposition
    )
    == (
        "eligible",
        "deferred",
        "ineligible",
        "unresolved",
    ),
)

check(
    "resume_dispositions_exact",
    tuple(
        item.value
        for item
        in eligibility.UniversalOrchestrationResumeDisposition
    )
    == (
        "eligible",
        "ineligible",
        "unresolved",
    ),
)


check(
    "suspension_reasons_exact",
    tuple(
        item.value
        for item
        in eligibility.UniversalOrchestrationSuspensionReason
    )
    == (
        "terminal_orchestration",
        "already_suspended",
        "state_cannot_suspend",
        "no_effective_work",
        "all_effective_work_terminal",
        "missing_status_evidence",
        "unresolved_branch_activity",
        "active_execution_present",
        "quiescent_and_suspendable",
    ),
)


check(
    "resume_reasons_exact",
    tuple(
        item.value
        for item
        in eligibility.UniversalOrchestrationResumeReason
    )
    == (
        "terminal_orchestration",
        "orchestration_not_suspended",
        "no_effective_work",
        "all_effective_work_terminal",
        "missing_status_evidence",
        "unresolved_branch_activity",
        "active_execution_contradiction",
        "suspended_and_resumable",
    ),
)


# ============================================================
# 3. INVALID TOP-LEVEL INPUTS
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
    status="created",
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

        eligibility.evaluate_universal_orchestration_suspension_resume_eligibility(
            state_snapshot=bad,
            progress_snapshot=base_progress,
        )

    except eligibility.UniversalOrchestrationSuspensionResumeEligibilityError as exc:

        rejected = (
            exc.code
            == "invalid_suspension_resume_state_snapshot"
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

        eligibility.evaluate_universal_orchestration_suspension_resume_eligibility(
            state_snapshot=base_state,
            progress_snapshot=bad,
        )

    except eligibility.UniversalOrchestrationSuspensionResumeEligibilityError as exc:

        rejected = (
            exc.code
            == "invalid_suspension_resume_progress_snapshot"
        )

    else:

        rejected = False

    check(
        "invalid_progress_snapshot_"
        + str(index),
        rejected,
    )


# ============================================================
# 4. STORED FIELDS EXACT
# ============================================================

field_names = tuple(
    field.name
    for field
    in fields(
        eligibility.UniversalOrchestrationSuspensionResumeEligibility
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

    "suspension_disposition",
    "suspension_reason",
    "resume_disposition",
    "resume_reason",

    "blocking_job_ids",
    "missing_status_job_ids",
    "unresolved_effective_job_ids",
    "in_progress_job_ids",
    "suspended_job_ids",

    "eligibility_decision_id",

    "created_at",
    "updated_at",
    "timestamp",

    "checkpoint_reference",
    "queue_id",
    "worker_id",
    "lease_id",
):

    check(
        "forbidden_stored_"
        + forbidden,
        forbidden
        not in field_names,
    )


# ============================================================
# 5. INVALID SCHEMA VERSION
# ============================================================

try:

    eligibility.UniversalOrchestrationSuspensionResumeEligibility(
        state_snapshot=base_state,
        progress_snapshot=base_progress,
        schema_version="wrong",
    )

except eligibility.UniversalOrchestrationSuspensionResumeEligibilityError as exc:

    bad_schema_rejected = (
        exc.code
        == "invalid_suspension_resume_schema_version"
    )

else:

    bad_schema_rejected = False


check(
    "invalid_schema_rejected",
    bad_schema_rejected,
)


# ============================================================
# 6. CROSS-IDENTITY ATTACKS
# ============================================================

other_plan = make_single_plan(
    "other-run"
)


try:

    eligibility.evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=make_state(
            plan=other_plan,
            state=state_model.UniversalOrchestrationState.ACTIVE,
        ),
        progress_snapshot=base_progress,
    )

except eligibility.UniversalOrchestrationSuspensionResumeEligibilityError as exc:

    mismatch_rejected = (
        exc.code
        == "suspension_resume_identity_mismatch"
    )

else:

    mismatch_rejected = False


check(
    "cross_identity_rejected",
    mismatch_rejected,
)


# ============================================================
# 7. TERMINAL ORCHESTRATION OVERRIDE
# ============================================================

terminal_plan = make_single_plan(
    "terminal-states"
)


for orchestration_state in (
    state_model.UniversalOrchestrationState.SUCCEEDED,
    state_model.UniversalOrchestrationState.FAILED,
    state_model.UniversalOrchestrationState.CANCELLED,
):

    for job_status in (
        "created",
        "queued",
        "scheduled",
        "leased",
        "running",
        "suspended",
        "succeeded",
        "failed",
        "cancelled",
        "dead_letter",
        "expired",
        _MISSING,
    ):

        result = evaluate(
            plan=terminal_plan,
            orchestration_state=orchestration_state,
            job_status=job_status,
        )

        suffix = (
            orchestration_state.value
            + "_"
            + (
                "missing"
                if job_status is _MISSING
                else str(job_status)
            )
        )

        check(
            "terminal_suspend_ineligible_"
            + suffix,
            result.suspension_disposition
            is
            eligibility.UniversalOrchestrationSuspensionDisposition.INELIGIBLE,
        )

        check(
            "terminal_suspend_reason_"
            + suffix,
            result.suspension_reason
            is
            eligibility.UniversalOrchestrationSuspensionReason.TERMINAL_ORCHESTRATION,
        )

        check(
            "terminal_resume_ineligible_"
            + suffix,
            result.resume_disposition
            is
            eligibility.UniversalOrchestrationResumeDisposition.INELIGIBLE,
        )

        check(
            "terminal_resume_reason_"
            + suffix,
            result.resume_reason
            is
            eligibility.UniversalOrchestrationResumeReason.TERMINAL_ORCHESTRATION,
        )


# ============================================================
# 8. ACTIVE SUSPENSION STATUS MATRIX
# ============================================================

active_plan = make_single_plan(
    "active-status-matrix"
)


eligible_suspend_statuses = (
    "created",
    "queued",
    "scheduled",
    "suspended",
)


for status in eligible_suspend_statuses:

    result = evaluate(
        plan=active_plan,
        orchestration_state=state_model.UniversalOrchestrationState.ACTIVE,
        job_status=status,
    )

    check(
        "active_suspend_eligible_"
        + status,
        result.suspension_disposition
        is
        eligibility.UniversalOrchestrationSuspensionDisposition.ELIGIBLE,
    )

    check(
        "active_suspend_quiescent_reason_"
        + status,
        result.suspension_reason
        is
        eligibility.UniversalOrchestrationSuspensionReason.QUIESCENT_AND_SUSPENDABLE,
    )


for status in (
    "leased",
    "running",
):

    result = evaluate(
        plan=active_plan,
        orchestration_state=state_model.UniversalOrchestrationState.ACTIVE,
        job_status=status,
    )

    check(
        "active_suspend_deferred_"
        + status,
        result.suspension_disposition
        is
        eligibility.UniversalOrchestrationSuspensionDisposition.DEFERRED,
    )

    check(
        "active_suspend_active_reason_"
        + status,
        result.suspension_reason
        is
        eligibility.UniversalOrchestrationSuspensionReason.ACTIVE_EXECUTION_PRESENT,
    )

    check(
        "active_suspend_blocking_"
        + status,
        result.blocking_job_ids
        == ("job-a",),
    )


for status in (
    "succeeded",
    "failed",
    "cancelled",
    "dead_letter",
    "expired",
):

    result = evaluate(
        plan=active_plan,
        orchestration_state=state_model.UniversalOrchestrationState.ACTIVE,
        job_status=status,
    )

    check(
        "active_all_terminal_ineligible_"
        + status,
        result.suspension_disposition
        is
        eligibility.UniversalOrchestrationSuspensionDisposition.INELIGIBLE,
    )

    check(
        "active_all_terminal_reason_"
        + status,
        result.suspension_reason
        is
        eligibility.UniversalOrchestrationSuspensionReason.ALL_EFFECTIVE_WORK_TERMINAL,
    )


active_missing = evaluate(
    plan=active_plan,
    orchestration_state=state_model.UniversalOrchestrationState.ACTIVE,
    job_status=_MISSING,
)


check(
    "active_missing_suspend_unresolved",
    active_missing.suspension_disposition
    is
    eligibility.UniversalOrchestrationSuspensionDisposition.UNRESOLVED,
)

check(
    "active_missing_suspend_reason",
    active_missing.suspension_reason
    is
    eligibility.UniversalOrchestrationSuspensionReason.MISSING_STATUS_EVIDENCE,
)


# ============================================================
# 9. SUSPENDED RESUME STATUS MATRIX
# ============================================================

suspended_plan = make_single_plan(
    "suspended-status-matrix"
)


for status in (
    "created",
    "queued",
    "scheduled",
    "suspended",
):

    result = evaluate(
        plan=suspended_plan,
        orchestration_state=state_model.UniversalOrchestrationState.SUSPENDED,
        job_status=status,
    )

    check(
        "suspended_resume_eligible_"
        + status,
        result.resume_disposition
        is
        eligibility.UniversalOrchestrationResumeDisposition.ELIGIBLE,
    )

    check(
        "suspended_resume_reason_"
        + status,
        result.resume_reason
        is
        eligibility.UniversalOrchestrationResumeReason.SUSPENDED_AND_RESUMABLE,
    )

    check(
        "already_suspended_suspend_ineligible_"
        + status,
        result.suspension_disposition
        is
        eligibility.UniversalOrchestrationSuspensionDisposition.INELIGIBLE,
    )

    check(
        "already_suspended_reason_"
        + status,
        result.suspension_reason
        is
        eligibility.UniversalOrchestrationSuspensionReason.ALREADY_SUSPENDED,
    )


for status in (
    "leased",
    "running",
):

    result = evaluate(
        plan=suspended_plan,
        orchestration_state=state_model.UniversalOrchestrationState.SUSPENDED,
        job_status=status,
    )

    check(
        "suspended_active_resume_unresolved_"
        + status,
        result.resume_disposition
        is
        eligibility.UniversalOrchestrationResumeDisposition.UNRESOLVED,
    )

    check(
        "suspended_active_resume_reason_"
        + status,
        result.resume_reason
        is
        eligibility.UniversalOrchestrationResumeReason.ACTIVE_EXECUTION_CONTRADICTION,
    )

    check(
        "suspended_active_blocking_"
        + status,
        result.blocking_job_ids
        == ("job-a",),
    )


for status in (
    "succeeded",
    "failed",
    "cancelled",
    "dead_letter",
    "expired",
):

    result = evaluate(
        plan=suspended_plan,
        orchestration_state=state_model.UniversalOrchestrationState.SUSPENDED,
        job_status=status,
    )

    check(
        "suspended_terminal_resume_ineligible_"
        + status,
        result.resume_disposition
        is
        eligibility.UniversalOrchestrationResumeDisposition.INELIGIBLE,
    )

    check(
        "suspended_terminal_resume_reason_"
        + status,
        result.resume_reason
        is
        eligibility.UniversalOrchestrationResumeReason.ALL_EFFECTIVE_WORK_TERMINAL,
    )


suspended_missing = evaluate(
    plan=suspended_plan,
    orchestration_state=state_model.UniversalOrchestrationState.SUSPENDED,
    job_status=_MISSING,
)


check(
    "suspended_missing_resume_unresolved",
    suspended_missing.resume_disposition
    is
    eligibility.UniversalOrchestrationResumeDisposition.UNRESOLVED,
)

check(
    "suspended_missing_resume_reason",
    suspended_missing.resume_reason
    is
    eligibility.UniversalOrchestrationResumeReason.MISSING_STATUS_EVIDENCE,
)


# ============================================================
# 10. NON-SUSPENDED STATES NEVER RESUME
# ============================================================

for orchestration_state in (
    state_model.UniversalOrchestrationState.CREATED,
    state_model.UniversalOrchestrationState.ACTIVE,
    state_model.UniversalOrchestrationState.WAITING,
    state_model.UniversalOrchestrationState.RECOVERING,
):

    plan = make_single_plan(
        "non-suspended-resume-"
        + orchestration_state.value
    )

    for status in (
        "created",
        "queued",
        "scheduled",
        "leased",
        "running",
        "suspended",
    ):

        result = evaluate(
            plan=plan,
            orchestration_state=orchestration_state,
            job_status=status,
        )

        check(
            "non_suspended_resume_ineligible_"
            + orchestration_state.value
            + "_"
            + status,
            result.resume_disposition
            is
            eligibility.UniversalOrchestrationResumeDisposition.INELIGIBLE,
        )

        check(
            "non_suspended_resume_reason_"
            + orchestration_state.value
            + "_"
            + status,
            result.resume_reason
            is
            eligibility.UniversalOrchestrationResumeReason.ORCHESTRATION_NOT_SUSPENDED,
        )


# ============================================================
# 11. STATE LEGALITY GOVERNS SUSPENSION
# ============================================================

for orchestration_state in (
    state_model.UniversalOrchestrationState.CREATED,
    state_model.UniversalOrchestrationState.ACTIVE,
    state_model.UniversalOrchestrationState.WAITING,
    state_model.UniversalOrchestrationState.RECOVERING,
):

    plan = make_single_plan(
        "state-legality-"
        + orchestration_state.value
    )

    result = evaluate(
        plan=plan,
        orchestration_state=orchestration_state,
        job_status="created",
    )

    legal = (
        state_model
        .can_transition_universal_orchestration_state(
            current_state=orchestration_state,
            target_state=state_model.UniversalOrchestrationState.SUSPENDED,
        )
    )

    if legal:

        check(
            "legal_state_suspend_eligible_"
            + orchestration_state.value,
            result.suspension_disposition
            is
            eligibility.UniversalOrchestrationSuspensionDisposition.ELIGIBLE,
        )

    else:

        check(
            "illegal_state_suspend_ineligible_"
            + orchestration_state.value,
            result.suspension_disposition
            is
            eligibility.UniversalOrchestrationSuspensionDisposition.INELIGIBLE,
        )

        check(
            "illegal_state_suspend_reason_"
            + orchestration_state.value,
            result.suspension_reason
            is
            eligibility.UniversalOrchestrationSuspensionReason.STATE_CANNOT_SUSPEND,
        )


# ============================================================
# 12. UNRESOLVED CONDITIONAL ACTIVITY
#
# root -> a
# root -> b
# b remains unresolved
# ============================================================

branch_plan = make_plan(
    run_id="unresolved-branch",
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
    ),
)


branch_fanout = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=branch_plan,
        source_job_id="root",
    )
)


branch_decision = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=branch_fanout,
        condition_evidence={
            "a": True,
            "b": None,
        },
    )
)


branch_progress = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=branch_plan,
        status_evidence={
            "root": "succeeded",
            "a": "created",
            "b": "created",
        },
        conditional_branching_decisions=(
            branch_decision,
        ),
    )
)


branch_active = (
    eligibility
    .evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=make_state(
            plan=branch_plan,
            state=state_model.UniversalOrchestrationState.ACTIVE,
        ),
        progress_snapshot=branch_progress,
    )
)


check(
    "unresolved_branch_suspend_unresolved",
    branch_active.suspension_disposition
    is
    eligibility.UniversalOrchestrationSuspensionDisposition.UNRESOLVED,
)

check(
    "unresolved_branch_suspend_reason",
    branch_active.suspension_reason
    is
    eligibility.UniversalOrchestrationSuspensionReason.UNRESOLVED_BRANCH_ACTIVITY,
)

check(
    "unresolved_branch_ids_exposed",
    branch_active.unresolved_effective_job_ids
    == ("b",),
    branch_active.unresolved_effective_job_ids,
)


branch_suspended = (
    eligibility
    .evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=make_state(
            plan=branch_plan,
            state=state_model.UniversalOrchestrationState.SUSPENDED,
        ),
        progress_snapshot=branch_progress,
    )
)


check(
    "unresolved_branch_resume_unresolved",
    branch_suspended.resume_disposition
    is
    eligibility.UniversalOrchestrationResumeDisposition.UNRESOLVED,
)

check(
    "unresolved_branch_resume_reason",
    branch_suspended.resume_reason
    is
    eligibility.UniversalOrchestrationResumeReason.UNRESOLVED_BRANCH_ACTIVITY,
)


# ============================================================
# 13. MISSING STATUS PRECEDENCE OVER UNRESOLVED BRANCH
# ============================================================

branch_missing_progress = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=branch_plan,
        status_evidence={
            "root": "succeeded",
            "a": None,
            "b": None,
        },
        conditional_branching_decisions=(
            branch_decision,
        ),
    )
)


branch_missing_active = (
    eligibility
    .evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=make_state(
            plan=branch_plan,
            state=state_model.UniversalOrchestrationState.ACTIVE,
        ),
        progress_snapshot=branch_missing_progress,
    )
)


check(
    "missing_precedes_unresolved_suspend",
    branch_missing_active.suspension_reason
    is
    eligibility.UniversalOrchestrationSuspensionReason.MISSING_STATUS_EVIDENCE,
)


branch_missing_suspended = (
    eligibility
    .evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=make_state(
            plan=branch_plan,
            state=state_model.UniversalOrchestrationState.SUSPENDED,
        ),
        progress_snapshot=branch_missing_progress,
    )
)


check(
    "missing_precedes_unresolved_resume",
    branch_missing_suspended.resume_reason
    is
    eligibility.UniversalOrchestrationResumeReason.MISSING_STATUS_EVIDENCE,
)


# ============================================================
# 14. EXCLUDED JOBS DO NOT BLOCK ELIGIBILITY
#
# root -> a EXCLUDED
# root -> b SELECTED
#
# a may say RUNNING but it is outside possible-effective population.
# ============================================================

excluded_decision = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=branch_fanout,
        condition_evidence={
            "a": False,
            "b": True,
        },
    )
)


excluded_progress = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=branch_plan,
        status_evidence={
            "root": "succeeded",
            "a": "running",
            "b": "created",
        },
        conditional_branching_decisions=(
            excluded_decision,
        ),
    )
)


excluded_active = (
    eligibility
    .evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=make_state(
            plan=branch_plan,
            state=state_model.UniversalOrchestrationState.ACTIVE,
        ),
        progress_snapshot=excluded_progress,
    )
)


check(
    "excluded_running_job_not_blocking",
    excluded_active.suspension_disposition
    is
    eligibility.UniversalOrchestrationSuspensionDisposition.ELIGIBLE,
)

check(
    "excluded_running_job_not_in_blockers",
    excluded_active.blocking_job_ids
    == (),
)


# ============================================================
# 15. MIXED TERMINAL + QUIESCENT WORK
# ============================================================

mixed_plan = make_plan(
    run_id="mixed-terminal-quiescent",
    jobs_tuple=(
        make_job(
            job_id="a",
        ),
        make_job(
            job_id="b",
        ),
        make_job(
            job_id="c",
        ),
    ),
)


mixed_progress = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=mixed_plan,
        status_evidence={
            "a": "succeeded",
            "b": "failed",
            "c": "queued",
        },
    )
)


mixed_active = (
    eligibility
    .evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=make_state(
            plan=mixed_plan,
            state=state_model.UniversalOrchestrationState.ACTIVE,
        ),
        progress_snapshot=mixed_progress,
    )
)


check(
    "mixed_terminal_quiescent_suspend_eligible",
    mixed_active.suspension_disposition
    is
    eligibility.UniversalOrchestrationSuspensionDisposition.ELIGIBLE,
)


mixed_suspended = (
    eligibility
    .evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=make_state(
            plan=mixed_plan,
            state=state_model.UniversalOrchestrationState.SUSPENDED,
        ),
        progress_snapshot=mixed_progress,
    )
)


check(
    "mixed_terminal_quiescent_resume_eligible",
    mixed_suspended.resume_disposition
    is
    eligibility.UniversalOrchestrationResumeDisposition.ELIGIBLE,
)


# ============================================================
# 16. MIXED TERMINAL + ACTIVE EXECUTION
# ============================================================

mixed_running_progress = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=mixed_plan,
        status_evidence={
            "a": "succeeded",
            "b": "failed",
            "c": "running",
        },
    )
)


mixed_running_active = (
    eligibility
    .evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=make_state(
            plan=mixed_plan,
            state=state_model.UniversalOrchestrationState.ACTIVE,
        ),
        progress_snapshot=mixed_running_progress,
    )
)


check(
    "mixed_active_suspend_deferred",
    mixed_running_active.suspension_disposition
    is
    eligibility.UniversalOrchestrationSuspensionDisposition.DEFERRED,
)


mixed_running_suspended = (
    eligibility
    .evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=make_state(
            plan=mixed_plan,
            state=state_model.UniversalOrchestrationState.SUSPENDED,
        ),
        progress_snapshot=mixed_running_progress,
    )
)


check(
    "mixed_suspended_resume_unresolved",
    mixed_running_suspended.resume_disposition
    is
    eligibility.UniversalOrchestrationResumeDisposition.UNRESOLVED,
)


# ============================================================
# 17. BOOLEAN HELPERS CONSISTENCY
# ============================================================

for result in (
    active_missing,
    suspended_missing,
    mixed_active,
    mixed_running_active,
    mixed_suspended,
    mixed_running_suspended,
    branch_active,
    branch_suspended,
):

    check(
        "helper_suspend_eligible_consistent_"
        + result.eligibility_decision_id[:12],
        result.is_suspend_eligible
        ==
        (
            result.suspension_disposition
            is
            eligibility.UniversalOrchestrationSuspensionDisposition.ELIGIBLE
        ),
    )

    check(
        "helper_suspend_deferred_consistent_"
        + result.eligibility_decision_id[:12],
        result.is_suspend_deferred
        ==
        (
            result.suspension_disposition
            is
            eligibility.UniversalOrchestrationSuspensionDisposition.DEFERRED
        ),
    )

    check(
        "helper_suspend_unresolved_consistent_"
        + result.eligibility_decision_id[:12],
        result.is_suspend_unresolved
        ==
        (
            result.suspension_disposition
            is
            eligibility.UniversalOrchestrationSuspensionDisposition.UNRESOLVED
        ),
    )

    check(
        "helper_resume_eligible_consistent_"
        + result.eligibility_decision_id[:12],
        result.is_resume_eligible
        ==
        (
            result.resume_disposition
            is
            eligibility.UniversalOrchestrationResumeDisposition.ELIGIBLE
        ),
    )

    check(
        "helper_resume_unresolved_consistent_"
        + result.eligibility_decision_id[:12],
        result.is_resume_unresolved
        ==
        (
            result.resume_disposition
            is
            eligibility.UniversalOrchestrationResumeDisposition.UNRESOLVED
        ),
    )


# ============================================================
# 18. DERIVED EVIDENCE EXACTNESS
# ============================================================

check(
    "identity_derived",
    mixed_active.identity
    is
    mixed_progress.identity,
)

check(
    "orchestration_state_derived",
    mixed_active.orchestration_state
    is
    state_model.UniversalOrchestrationState.ACTIVE,
)

check(
    "missing_ids_derived_exact",
    branch_missing_active.missing_status_job_ids
    ==
    branch_missing_progress.missing_status_job_ids,
)

check(
    "unresolved_ids_derived_exact",
    branch_active.unresolved_effective_job_ids
    ==
    branch_progress.unresolved_effective_job_ids,
)

check(
    "in_progress_ids_derived_exact",
    mixed_running_active.in_progress_job_ids
    ==
    mixed_running_progress.in_progress_job_ids,
)

check(
    "suspended_ids_derived_exact",
    suspended_plan is not None
    and
    evaluate(
        plan=suspended_plan,
        orchestration_state=state_model.UniversalOrchestrationState.SUSPENDED,
        job_status="suspended",
    ).suspended_job_ids
    == ("job-a",),
)


# ============================================================
# 19. DATACLASS IMMUTABILITY
# ============================================================

immutable_sample = mixed_running_active


for field in fields(
    immutable_sample
):

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
        "immutable_"
        + field.name,
        immutable,
    )


# ============================================================
# 20. DECISION ID DETERMINISM
# ============================================================

repeat_ids = tuple(
    eligibility
    .evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=make_state(
            plan=active_plan,
            state=state_model.UniversalOrchestrationState.ACTIVE,
        ),
        progress_snapshot=make_progress(
            plan=active_plan,
            status="created",
        ),
    )
    .eligibility_decision_id
    for _
    in range(
        20
    )
)


check(
    "decision_id_repeat_deterministic",
    len(
        set(
            repeat_ids
        )
    )
    == 1,
)

check(
    "decision_id_length_64",
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
# 21. DECISION ID STATE SENSITIVITY
# ============================================================

state_sensitive_active = (
    eligibility
    .evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=make_state(
            plan=active_plan,
            state=state_model.UniversalOrchestrationState.ACTIVE,
        ),
        progress_snapshot=make_progress(
            plan=active_plan,
            status="created",
        ),
    )
    .eligibility_decision_id
)


state_sensitive_suspended = (
    eligibility
    .evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=make_state(
            plan=active_plan,
            state=state_model.UniversalOrchestrationState.SUSPENDED,
        ),
        progress_snapshot=make_progress(
            plan=active_plan,
            status="created",
        ),
    )
    .eligibility_decision_id
)


check(
    "decision_id_state_sensitive",
    state_sensitive_active
    != state_sensitive_suspended,
)


# ============================================================
# 22. DECISION ID PROGRESS SENSITIVITY
# ============================================================

progress_created_id = (
    eligibility
    .evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=make_state(
            plan=active_plan,
            state=state_model.UniversalOrchestrationState.ACTIVE,
        ),
        progress_snapshot=make_progress(
            plan=active_plan,
            status="created",
        ),
    )
    .eligibility_decision_id
)


progress_running_id = (
    eligibility
    .evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=make_state(
            plan=active_plan,
            state=state_model.UniversalOrchestrationState.ACTIVE,
        ),
        progress_snapshot=make_progress(
            plan=active_plan,
            status="running",
        ),
    )
    .eligibility_decision_id
)


check(
    "decision_id_progress_sensitive",
    progress_created_id
    != progress_running_id,
)


# ============================================================
# 23. DECISION ID RUN SENSITIVITY
# ============================================================

run_a = make_single_plan(
    "decision-run-a"
)

run_b = make_single_plan(
    "decision-run-b"
)


run_a_result = evaluate(
    plan=run_a,
    orchestration_state=state_model.UniversalOrchestrationState.ACTIVE,
    job_status="created",
)

run_b_result = evaluate(
    plan=run_b,
    orchestration_state=state_model.UniversalOrchestrationState.ACTIVE,
    job_status="created",
)


check(
    "decision_id_run_sensitive",
    run_a_result.eligibility_decision_id
    != run_b_result.eligibility_decision_id,
)


# ============================================================
# 24. SOURCE SNAPSHOTS NOT MUTATED
# ============================================================

state_before = (
    base_state.identity,
    base_state.state,
    base_state.schema_version,
)

progress_before = (
    base_progress.execution_plan,
    base_progress.status_evidence,
    base_progress.conditional_branching_decisions,
    base_progress.schema_version,
    base_progress.progress_snapshot_id,
)


_ = (
    eligibility
    .evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=base_state,
        progress_snapshot=base_progress,
    )
)


state_after = (
    base_state.identity,
    base_state.state,
    base_state.schema_version,
)

progress_after = (
    base_progress.execution_plan,
    base_progress.status_evidence,
    base_progress.conditional_branching_decisions,
    base_progress.schema_version,
    base_progress.progress_snapshot_id,
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
# 25. EXPLANATION CONTRACT
# ============================================================

explanation = (
    eligibility
    .explain_universal_orchestration_suspension_resume_eligibility_v1()
)


check(
    "explanation_mappingproxy",
    isinstance(
        explanation,
        MappingProxyType,
    ),
)

check(
    "explanation_phase_exact",
    explanation.get(
        "phase"
    )
    == "5.1.12",
)

check(
    "explanation_component_exact",
    explanation.get(
        "component"
    )
    ==
    "Universal Orchestration Suspension & Resume Eligibility",
)

check(
    "explanation_stored_fields_exact",
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
    "explanation_state_authority",
    "5.1.3"
    in explanation.get(
        "state_authority",
        "",
    ),
)

check(
    "explanation_progress_authority",
    "5.1.11"
    in explanation.get(
        "progress_authority",
        "",
    ),
)

check(
    "explanation_recovery_boundary",
    "5.1.13"
    in explanation.get(
        "recovery_boundary",
        "",
    ),
)

check(
    "explanation_persistence_boundary",
    "5.1.14"
    in explanation.get(
        "persistence_boundary",
        "",
    ),
)

check(
    "explanation_completion_boundary",
    "5.1.15"
    in explanation.get(
        "completion_boundary",
        "",
    ),
)

check(
    "explanation_termination_boundary",
    "5.1.16"
    in explanation.get(
        "termination_boundary",
        "",
    ),
)

check(
    "explanation_evidence_boundary",
    "5.1.17"
    in explanation.get(
        "evidence_boundary",
        "",
    ),
)


# ============================================================
# 26. REQUIRED PROHIBITIONS
# ============================================================

required_prohibitions = (
    "does not transition orchestration state",
    "does not suspend orchestration",
    "does not resume orchestration",
    "does not pause queues",
    "does not drain workers",
    "does not release leases",
    "does not acquire leases",
    "does not save checkpoints",
    "does not restore checkpoints",
    "does not read checkpoint payloads",
    "does not mutate UniversalJob.status",
    "does not mutate UniversalJob.progress",
    "does not evaluate stage readiness",
    "does not evaluate runtime handoff",
    "does not reevaluate conditional branches",
    "does not recompute progress topology",
    "does not enqueue jobs",
    "does not dequeue jobs",
    "does not claim jobs",
    "does not assign workers",
    "does not dispatch runtime handlers",
    "does not execute jobs",
    "does not initiate recovery",
    "does not access Runtime State Store",
    "does not persist eligibility decisions",
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
# 27. IMPORT BOUNDARY
# ============================================================

source = ELIGIBILITY_PATH.read_text(
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
# 28. FORBIDDEN IMPORTS
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
    "backend.server.runtime.runtime_shutdown_process",

    "backend.server.runtime.universal_queue",
    "backend.server.runtime.universal_worker",

    "backend.server.runtime.universal_runtime_registration",
    "backend.server.runtime.universal_runtime_worker_v1",
    "backend.server.runtime.universal_runtime_infrastructure",

    "backend.server.runtime.universal_orchestration.stage_readiness",
    "backend.server.runtime.universal_orchestration.runtime_handoff",
    "backend.server.runtime.universal_orchestration.fan_out_coordination",
    "backend.server.runtime.universal_orchestration.fan_in_coordination",
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
# 29. FORBIDDEN CALLS
# ============================================================

forbidden_calls = {
    "eval",
    "exec",
    "compile",

    "open",
    "read_text",
    "write_text",
    "mkdir",
    "unlink",
    "remove",

    "sleep",
    "wait",
    "poll",

    "time",
    "time_ns",
    "now",
    "utcnow",

    "drain",
    "resume",
    "pause",
    "shutdown",

    "enqueue_job",
    "schedule_job",
    "dequeue_job",
    "claim_job",

    "assign_universal_worker",
    "acquire_universal_worker_lease",

    "transition_universal_orchestration_state",

    "coordinate_universal_orchestration_fan_out",
    "coordinate_universal_orchestration_fan_in",
    "evaluate_universal_orchestration_conditional_branching",
    "track_universal_orchestration_progress",

    "dispatch_registered_runtime_handler",
    "execute_registered_runtime_job_v1",

    "get_runtime_state_store_registry",

    "create_task",
    "Thread",
    "Process",

    "persist",
    "save",
    "dispatch",
    "execute",
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
# 30. FORBIDDEN ATTRIBUTE ACCESS
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
# 31. NO DIRECT RUNTIME MECHANICS SYMBOLS
# ============================================================

for forbidden_text in (
    "RuntimeLifecycleManager",
    "RuntimeStateStore",
    "checkpoint_reference",
    "universal_runtime_worker_v1",
    "universal_runtime_infrastructure",
    "universal_runtime_registration",
):

    check(
        "forbidden_symbol_absent_"
        + forbidden_text,
        forbidden_text
        not in source,
    )


# ============================================================
# 32. PROTECTED AUTHORITY MATRIX
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
    ELIGIBILITY_PATH
)


check(
    "eligibility_ast_final",
    final_ast
    == EXPECTED_ELIGIBILITY_AST,
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
        "PHASE 5.1.12 — UNIVERSAL ORCHESTRATION "
        "SUSPENSION & RESUME ELIGIBILITY ADVERSARIAL REGRESSION"
    ),

    "=" * 118,

    "",

    (
        "SUSPENSION & RESUME ELIGIBILITY AST SHA256: "
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
            "ADVERSARIAL SUSPENSION & RESUME ELIGIBILITY REGRESSION: "
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

        "5.1.12 AUTHORITY MODIFIED DURING REGRESSION: NO",
        "5.1.1–5.1.11 FROZEN AUTHORITIES MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "SUSPEND DISPOSITIONS:",
        "  ELIGIBLE",
        "  DEFERRED",
        "  INELIGIBLE",
        "  UNRESOLVED",

        "",

        "RESUME DISPOSITIONS:",
        "  ELIGIBLE",
        "  INELIGIBLE",
        "  UNRESOLVED",

        "",

        "ACTIVE CREATED/QUEUED/SCHEDULED/SUSPENDED WORK:",
        "  SUSPEND ELIGIBLE WHEN 5.1.3 STATE LEGALITY PERMITS",

        "ACTIVE LEASED/RUNNING WORK:",
        "  SUSPEND DEFERRED",

        "ALL EFFECTIVE WORK TERMINAL:",
        "  SUSPEND/RESUME INELIGIBLE",

        "MISSING EFFECTIVE STATUS:",
        "  UNRESOLVED",

        "UNRESOLVED BRANCH ACTIVITY:",
        "  UNRESOLVED",

        "",

        "RESUME REQUIRES ORCHESTRATION STATE SUSPENDED: YES",

        "SUSPENDED CREATED/QUEUED/SCHEDULED/SUSPENDED WORK:",
        "  RESUME ELIGIBLE",

        "SUSPENDED LEASED/RUNNING WORK:",
        "  RESUME UNRESOLVED — ACTIVE EXECUTION CONTRADICTION",

        "",

        "EXCLUDED RUNNING JOB BLOCKS SUSPENSION: NO",

        "",

        "TERMINAL ORCHESTRATION OVERRIDES JOB EVIDENCE: YES",

        "",

        "DECISION ID DETERMINISTIC: YES",
        "DECISION ID STATE SENSITIVE: YES",
        "DECISION ID PROGRESS SENSITIVE: YES",
        "DECISION ID RUN SENSITIVE: YES",

        "",

        "STATE SNAPSHOT MUTATED: NO",
        "PROGRESS SNAPSHOT MUTATED: NO",

        "",

        "ORCHESTRATION STATE TRANSITION: NO",
        "QUEUE PAUSE: NO",
        "WORKER DRAIN: NO",
        "LEASE RELEASE/ACQUIRE: NO",
        "CHECKPOINT SAVE: NO",
        "CHECKPOINT RESTORE: NO",
        "CHECKPOINT PAYLOAD READ: NO",

        "",

        "READINESS EVALUATION: NO",
        "HANDOFF EVALUATION: NO",
        "CONDITIONAL REEVALUATION: NO",
        "PROGRESS RECOMPUTATION: NO",

        "",

        "QUEUE ACTIVITY: NO",
        "WORKER ACTIVITY: NO",
        "HANDLER DISPATCH: NO",
        "JOB EXECUTION: NO",

        "",

        "RECOVERY: NO",
        "PERSISTENCE: NO",
        "COMPLETION RESOLUTION: NO",
        "SUCCESS/FAILURE RESOLUTION: NO",
        "TERMINATION RESOLUTION: NO",
        "PERMANENT EVIDENCE RECORDING: NO",

        "",

        "RUNTIME STATE STORE ACCESS: NO",
        "RUNTIME LIFECYCLE MANAGER ACCESS: NO",
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
        "Phase 5.1.12 adversarial regression failed."
    )
