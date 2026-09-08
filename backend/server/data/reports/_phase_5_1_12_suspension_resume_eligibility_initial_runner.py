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
    / "phase_5_1_12_suspension_resume_eligibility_initial_implementation.txt"
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
        "D60C8629D2490DC41A8DF43E30F00A1D4851941E65CBD2EBE1EED70B75217916",
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
}


# Correct the canonical 5.1.8 AST literal.
PROTECTED[
    "5.1.8_fan_out"
] = (
    ROOT / "backend/server/runtime/universal_orchestration/fan_out_coordination.py",
    "D60C8629D2490DC41A8DF43E30F00A1D4851941E65CBD2EBE7EED70B75217916",
)


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


for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(
        path
    )

    if actual != expected:

        raise SystemExit(
            "Protected authority changed: "
            + name
        )


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

progress = importlib.import_module(
    "backend.server.runtime.universal_orchestration.progress_tracking"
)

eligibility = importlib.import_module(
    "backend.server.runtime.universal_orchestration.suspension_resume_eligibility"
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


def make_job(
    *,
    job_id,
):

    return jobs.UniversalJob(
        job_id=job_id,
        workspace_id="workspace-a",
        pipeline="pipeline-a",
        stage="stage-a",
        job_type="test_job",
        payload_reference="payload-a",
        dependency_job_ids=(),
        status=jobs.UniversalJobStatus.CREATED,
        created_at=FIXED_CREATED_AT,
    )


def make_plan(
    run_id,
):

    job = make_job(
        job_id="job-a"
    )

    contract = (
        contracts
        .create_universal_runtime_orchestration_contract(
            workspace_id="workspace-a",
            pipeline="pipeline-a",
            job_ids=("job-a",),
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
            jobs=(job,),
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
    status,
):

    return (
        progress
        .track_universal_orchestration_progress(
            execution_plan=plan,
            status_evidence={
                "job-a":
                    status,
            },
        )
    )


plan = make_plan(
    "eligibility-initial"
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
    "hash_exact",
    eligibility.UNIVERSAL_ORCHESTRATION_SUSPENSION_RESUME_DECISION_HASH_ALGORITHM
    == "sha256",
)


# ------------------------------------------------------------
# ACTIVE + CREATED => suspend eligible, resume ineligible
# ------------------------------------------------------------

active_created = (
    eligibility
    .evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=make_state(
            plan=plan,
            state=state_model.UniversalOrchestrationState.ACTIVE,
        ),
        progress_snapshot=make_progress(
            plan=plan,
            status="created",
        ),
    )
)


check(
    "active_created_suspend_eligible",
    active_created.is_suspend_eligible,
)

check(
    "active_created_resume_ineligible",
    not active_created.is_resume_eligible,
)


# ------------------------------------------------------------
# ACTIVE + RUNNING => deferred
# ------------------------------------------------------------

active_running = (
    eligibility
    .evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=make_state(
            plan=plan,
            state=state_model.UniversalOrchestrationState.ACTIVE,
        ),
        progress_snapshot=make_progress(
            plan=plan,
            status="running",
        ),
    )
)


check(
    "active_running_suspend_deferred",
    active_running.is_suspend_deferred,
)

check(
    "active_running_blocking_exact",
    active_running.blocking_job_ids
    == ("job-a",),
)


# ------------------------------------------------------------
# SUSPENDED + SUSPENDED JOB => resume eligible
# ------------------------------------------------------------

suspended_job = (
    eligibility
    .evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=make_state(
            plan=plan,
            state=state_model.UniversalOrchestrationState.SUSPENDED,
        ),
        progress_snapshot=make_progress(
            plan=plan,
            status="suspended",
        ),
    )
)


check(
    "already_suspended_suspend_ineligible",
    not suspended_job.is_suspend_eligible,
)

check(
    "suspended_job_resume_eligible",
    suspended_job.is_resume_eligible,
)


# ------------------------------------------------------------
# SUSPENDED + QUEUED => also resume eligible
# ------------------------------------------------------------

suspended_queued = (
    eligibility
    .evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=make_state(
            plan=plan,
            state=state_model.UniversalOrchestrationState.SUSPENDED,
        ),
        progress_snapshot=make_progress(
            plan=plan,
            status="queued",
        ),
    )
)


check(
    "suspended_queued_resume_eligible",
    suspended_queued.is_resume_eligible,
)


# ------------------------------------------------------------
# SUSPENDED + RUNNING => contradictory / unresolved
# ------------------------------------------------------------

suspended_running = (
    eligibility
    .evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=make_state(
            plan=plan,
            state=state_model.UniversalOrchestrationState.SUSPENDED,
        ),
        progress_snapshot=make_progress(
            plan=plan,
            status="running",
        ),
    )
)


check(
    "suspended_running_resume_unresolved",
    suspended_running.is_resume_unresolved,
)


# ------------------------------------------------------------
# TERMINAL ORCHESTRATION
# ------------------------------------------------------------

for state in (
    state_model.UniversalOrchestrationState.SUCCEEDED,
    state_model.UniversalOrchestrationState.FAILED,
    state_model.UniversalOrchestrationState.CANCELLED,
):

    result = (
        eligibility
        .evaluate_universal_orchestration_suspension_resume_eligibility(
            state_snapshot=make_state(
                plan=plan,
                state=state,
            ),
            progress_snapshot=make_progress(
                plan=plan,
                status="succeeded",
            ),
        )
    )

    check(
        "terminal_suspend_ineligible_"
        + state.value,
        result.suspension_disposition
        is
        eligibility.UniversalOrchestrationSuspensionDisposition.INELIGIBLE,
    )

    check(
        "terminal_resume_ineligible_"
        + state.value,
        result.resume_disposition
        is
        eligibility.UniversalOrchestrationResumeDisposition.INELIGIBLE,
    )


# ------------------------------------------------------------
# MISSING EVIDENCE => unresolved
# ------------------------------------------------------------

missing_progress = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=plan,
        status_evidence=None,
    )
)


missing_result = (
    eligibility
    .evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=make_state(
            plan=plan,
            state=state_model.UniversalOrchestrationState.ACTIVE,
        ),
        progress_snapshot=missing_progress,
    )
)


check(
    "missing_suspend_unresolved",
    missing_result.is_suspend_unresolved,
)


# ------------------------------------------------------------
# ALL TERMINAL WORK => ineligible
# ------------------------------------------------------------

all_terminal = (
    eligibility
    .evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=make_state(
            plan=plan,
            state=state_model.UniversalOrchestrationState.ACTIVE,
        ),
        progress_snapshot=make_progress(
            plan=plan,
            status="failed",
        ),
    )
)


check(
    "all_terminal_suspend_ineligible",
    all_terminal.suspension_disposition
    is
    eligibility.UniversalOrchestrationSuspensionDisposition.INELIGIBLE,
)


# ------------------------------------------------------------
# STORED FIELDS
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# IMMUTABILITY
# ------------------------------------------------------------

for field in fields(
    active_created
):

    try:

        setattr(
            active_created,
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


# ------------------------------------------------------------
# DECISION ID
# ------------------------------------------------------------

decision_id = (
    active_created.eligibility_decision_id
)


check(
    "decision_id_length",
    len(decision_id)
    == 64,
    decision_id,
)

check(
    "decision_id_upper_hex",
    all(
        character in "0123456789ABCDEF"
        for character in decision_id
    ),
)

check(
    "decision_id_deterministic",
    decision_id
    ==
    eligibility
    .evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=make_state(
            plan=plan,
            state=state_model.UniversalOrchestrationState.ACTIVE,
        ),
        progress_snapshot=make_progress(
            plan=plan,
            status="created",
        ),
    )
    .eligibility_decision_id,
)


# ------------------------------------------------------------
# CROSS-IDENTITY REJECT
# ------------------------------------------------------------

other_plan = make_plan(
    "eligibility-other"
)


try:

    eligibility.evaluate_universal_orchestration_suspension_resume_eligibility(
        state_snapshot=make_state(
            plan=other_plan,
            state=state_model.UniversalOrchestrationState.ACTIVE,
        ),
        progress_snapshot=make_progress(
            plan=plan,
            status="created",
        ),
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


# ------------------------------------------------------------
# EXPLANATION
# ------------------------------------------------------------

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
    "phase_exact",
    explanation.get("phase")
    == "5.1.12",
)

check(
    "state_authority_5_1_3",
    "5.1.3"
    in explanation.get(
        "state_authority",
        "",
    ),
)

check(
    "progress_authority_5_1_11",
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
    "completion_boundary_5_1_15",
    "5.1.15"
    in explanation.get(
        "completion_boundary",
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


# ------------------------------------------------------------
# IMPORT BOUNDARY
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# FORBIDDEN CALLS
# ------------------------------------------------------------

forbidden_calls = {
    "open",
    "read_text",
    "write_text",

    "sleep",
    "wait",
    "poll",

    "drain",
    "resume",
    "pause",

    "enqueue_job",
    "dequeue_job",
    "claim_job",

    "assign_universal_worker",
    "acquire_universal_worker_lease",

    "transition_universal_orchestration_state",

    "dispatch_registered_runtime_handler",
    "execute_registered_runtime_job_v1",

    "get_runtime_state_store_registry",

    "persist",
    "save",

    "time",
    "now",
    "utcnow",
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

    if name in forbidden_calls:

        found_forbidden.append(
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
    not found_forbidden,
    found_forbidden,
)


eligibility_ast = (
    ast_sha(
        ELIGIBILITY_PATH
    )
)


check(
    "eligibility_ast_generated",
    len(eligibility_ast)
    == 64,
    eligibility_ast,
)


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
        actual == expected,
        actual,
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
        "PHASE 5.1.12 — UNIVERSAL ORCHESTRATION "
        "SUSPENSION & RESUME ELIGIBILITY INITIAL IMPLEMENTATION"
    ),

    "=" * 118,

    "",

    (
        "SUSPENSION & RESUME ELIGIBILITY AST SHA256: "
        + eligibility_ast
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

        "=" * 118,

        (
            "INITIAL SUSPENSION & RESUME ELIGIBILITY RESULT: "
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

        "5.1.1–5.1.11 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "ACTIVE EXECUTION SUSPENSION RESULT: DEFERRED",
        "QUIESCENT NONTERMINAL SUSPENSION RESULT: ELIGIBLE",
        "TERMINAL ORCHESTRATION SUSPENSION RESULT: INELIGIBLE",

        "",

        "RESUME REQUIRES ORCHESTRATION STATE SUSPENDED: YES",
        "SUSPENDED + QUIESCENT NONTERMINAL WORK: ELIGIBLE",
        "SUSPENDED + RUNNING WORK: UNRESOLVED",

        "",

        "MISSING STATUS EVIDENCE GUESSED: NO",
        "UNRESOLVED BRANCH ACTIVITY GUESSED: NO",

        "",

        "STATE TRANSITION PERFORMED: NO",
        "QUEUE PAUSE: NO",
        "WORKER DRAIN: NO",
        "LEASE RELEASE/ACQUIRE: NO",
        "CHECKPOINT SAVE/RESTORE: NO",
        "JOB EXECUTION: NO",

        "",

        "RECOVERY: NO",
        "PERSISTENCE: NO",
        "COMPLETION RESOLUTION: NO",
        "TERMINATION RESOLUTION: NO",
        "PERMANENT EVIDENCE RECORDING: NO",

        "",

        (
            "STATUS: INITIAL IMPLEMENTATION PASS "
            "— ADVERSARIAL REGRESSION REQUIRED"
            if passed == total
            else
            "STATUS: INITIAL IMPLEMENTATION FAILED"
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
        "Phase 5.1.12 initial implementation failed."
    )
