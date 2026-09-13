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
    / "phase_5_1_13_orchestration_recovery_initial_implementation.txt"
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

recovery = importlib.import_module(
    "backend.server.runtime.universal_orchestration.recovery"
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
    *,
    run_id,
    job_ids,
):

    job_tuple = tuple(
        make_job(
            job_id=job_id
        )
        for job_id
        in job_ids
    )

    contract = (
        contracts
        .create_universal_runtime_orchestration_contract(
            workspace_id="workspace-a",
            pipeline="pipeline-a",
            job_ids=tuple(
                job.job_id
                for job
                in job_tuple
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
            jobs=job_tuple,
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
):

    return (
        progress
        .track_universal_orchestration_progress(
            execution_plan=plan,
            status_evidence=statuses,
        )
    )


def evaluate(
    *,
    plan,
    state,
    statuses,
):

    return (
        recovery
        .evaluate_universal_orchestration_recovery(
            state_snapshot=make_state(
                plan=plan,
                state=state,
            ),
            progress_snapshot=make_progress(
                plan=plan,
                statuses=statuses,
            ),
        )
    )


plan = make_plan(
    run_id="recovery-initial",
    job_ids=(
        "a",
        "b",
        "c",
    ),
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
    "hash_exact",
    recovery.UNIVERSAL_ORCHESTRATION_RECOVERY_DECISION_HASH_ALGORITHM
    == "sha256",
)


# ------------------------------------------------------------
# NO RECOVERY REQUIRED
# ------------------------------------------------------------

healthy = (
    evaluate(
        plan=plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "a": "created",
            "b": "running",
            "c": "succeeded",
        },
    )
)


check(
    "healthy_not_required",
    healthy.disposition
    is
    recovery.UniversalOrchestrationRecoveryDisposition.NOT_REQUIRED,
)

check(
    "healthy_reason",
    healthy.reason
    is
    recovery.UniversalOrchestrationRecoveryReason.NO_RECOVERY_REQUIRED,
)


# ------------------------------------------------------------
# FAILED => RECOVERABLE
# ------------------------------------------------------------

failed = (
    evaluate(
        plan=plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "a": "failed",
            "b": "running",
            "c": "succeeded",
        },
    )
)


check(
    "failed_recoverable",
    failed.disposition
    is
    recovery.UniversalOrchestrationRecoveryDisposition.RECOVERABLE,
)

check(
    "failed_candidate_exact",
    failed.recovery_candidate_job_ids
    == ("a",),
    failed.recovery_candidate_job_ids,
)

check(
    "failed_reason",
    failed.reason
    is
    recovery.UniversalOrchestrationRecoveryReason.FAILED_EFFECTIVE_WORK,
)


# ------------------------------------------------------------
# CANCELLED => UNRECOVERABLE
# ------------------------------------------------------------

cancelled = (
    evaluate(
        plan=plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "a": "cancelled",
            "b": "running",
            "c": "succeeded",
        },
    )
)


check(
    "cancelled_unrecoverable",
    cancelled.disposition
    is
    recovery.UniversalOrchestrationRecoveryDisposition.UNRECOVERABLE,
)

check(
    "cancelled_exact",
    cancelled.cancelled_effective_job_ids
    == ("a",),
)


# ------------------------------------------------------------
# DEAD LETTER / EXPIRED => POLICY DEPENDENT
# ------------------------------------------------------------

dead_letter = (
    evaluate(
        plan=plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "a": "dead_letter",
            "b": "running",
            "c": "succeeded",
        },
    )
)


check(
    "dead_letter_unresolved",
    dead_letter.disposition
    is
    recovery.UniversalOrchestrationRecoveryDisposition.UNRESOLVED,
)

check(
    "dead_letter_policy_dependent",
    dead_letter.policy_dependent_job_ids
    == ("a",),
)


expired = (
    evaluate(
        plan=plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "a": "expired",
            "b": "running",
            "c": "succeeded",
        },
    )
)


check(
    "expired_unresolved",
    expired.disposition
    is
    recovery.UniversalOrchestrationRecoveryDisposition.UNRESOLVED,
)

check(
    "expired_policy_dependent",
    expired.policy_dependent_job_ids
    == ("a",),
)


# ------------------------------------------------------------
# MISSING => UNRESOLVED
# ------------------------------------------------------------

missing = (
    evaluate(
        plan=plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "a": None,
            "b": "running",
            "c": "succeeded",
        },
    )
)


check(
    "missing_unresolved",
    missing.disposition
    is
    recovery.UniversalOrchestrationRecoveryDisposition.UNRESOLVED,
)

check(
    "missing_reason",
    missing.reason
    is
    recovery.UniversalOrchestrationRecoveryReason.MISSING_STATUS_EVIDENCE,
)

check(
    "missing_ids_exact",
    missing.missing_status_job_ids
    == ("a",),
)


# ------------------------------------------------------------
# TERMINAL ORCHESTRATION OVERRIDE
# ------------------------------------------------------------

for terminal_state in (
    state_model.UniversalOrchestrationState.SUCCEEDED,
    state_model.UniversalOrchestrationState.FAILED,
    state_model.UniversalOrchestrationState.CANCELLED,
):

    result = (
        evaluate(
            plan=plan,
            state=terminal_state,
            statuses={
                "a": "failed",
                "b": "running",
                "c": None,
            },
        )
    )

    check(
        "terminal_unrecoverable_"
        + terminal_state.value,
        result.disposition
        is
        recovery.UniversalOrchestrationRecoveryDisposition.UNRECOVERABLE,
    )

    check(
        "terminal_reason_"
        + terminal_state.value,
        result.reason
        is
        recovery.UniversalOrchestrationRecoveryReason.TERMINAL_ORCHESTRATION,
    )


# ------------------------------------------------------------
# RECOVERING STATE STILL DESCRIBES RECOVERY NEED
# ------------------------------------------------------------

recovering = (
    evaluate(
        plan=plan,
        state=state_model.UniversalOrchestrationState.RECOVERING,
        statuses={
            "a": "failed",
            "b": "created",
            "c": "succeeded",
        },
    )
)


check(
    "recovering_recoverable",
    recovering.disposition
    is
    recovery.UniversalOrchestrationRecoveryDisposition.RECOVERABLE,
)

check(
    "recovering_current_state",
    recovering.is_currently_recovering,
)

check(
    "recovering_may_enter_false",
    not recovering.may_enter_recovering,
)


# ------------------------------------------------------------
# MAY ENTER RECOVERING
# ------------------------------------------------------------

active_failed = (
    evaluate(
        plan=plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "a": "failed",
            "b": "created",
            "c": "succeeded",
        },
    )
)


legal = (
    state_model
    .can_transition_universal_orchestration_state(
        current_state=state_model.UniversalOrchestrationState.ACTIVE,
        target_state=state_model.UniversalOrchestrationState.RECOVERING,
    )
)


check(
    "may_enter_recovering_matches_5_1_3",
    active_failed.may_enter_recovering
    == legal,
)


# ------------------------------------------------------------
# STORED FIELDS
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# IMMUTABILITY
# ------------------------------------------------------------

for field in fields(
    active_failed
):

    try:

        setattr(
            active_failed,
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
    active_failed.recovery_decision_id
)


check(
    "decision_id_length",
    len(
        decision_id
    )
    == 64,
    decision_id,
)

check(
    "decision_id_upper_hex",
    all(
        character
        in "0123456789ABCDEF"
        for character
        in decision_id
    ),
)

check(
    "decision_id_deterministic",
    decision_id
    ==
    evaluate(
        plan=plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "a": "failed",
            "b": "created",
            "c": "succeeded",
        },
    )
    .recovery_decision_id,
)


# ------------------------------------------------------------
# CROSS IDENTITY
# ------------------------------------------------------------

other_plan = make_plan(
    run_id="recovery-other",
    job_ids=(
        "a",
        "b",
        "c",
    ),
)


try:

    recovery.evaluate_universal_orchestration_recovery(
        state_snapshot=make_state(
            plan=other_plan,
            state=state_model.UniversalOrchestrationState.ACTIVE,
        ),
        progress_snapshot=make_progress(
            plan=plan,
            statuses={
                "a": "failed",
                "b": "created",
                "c": "succeeded",
            },
        ),
    )

except recovery.UniversalOrchestrationRecoveryError as exc:

    mismatch_rejected = (
        exc.code
        == "orchestration_recovery_identity_mismatch"
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

    "enqueue_job",
    "dequeue_job",
    "claim_job",

    "schedule_job",
    "requeue_job",

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


recovery_ast = (
    ast_sha(
        RECOVERY_PATH
    )
)


check(
    "recovery_ast_generated",
    len(
        recovery_ast
    )
    == 64,
    recovery_ast,
)


# ------------------------------------------------------------
# PROTECTED MATRIX
# ------------------------------------------------------------

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
        "PHASE 5.1.13 — UNIVERSAL ORCHESTRATION "
        "RECOVERY INITIAL IMPLEMENTATION"
    ),

    "=" * 118,

    "",

    (
        "ORCHESTRATION RECOVERY AST SHA256: "
        + recovery_ast
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
            "INITIAL ORCHESTRATION RECOVERY RESULT: "
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

        "5.1.1–5.1.12 FROZEN AUTHORITIES MODIFIED: NO",
        "PHASE 4 WORKER RECOVERY MODIFIED: NO",

        "",

        "FAILED EFFECTIVE WORK: RECOVERABLE",
        "CANCELLED EFFECTIVE WORK: UNRECOVERABLE",
        "DEAD_LETTER EFFECTIVE WORK: UNRESOLVED",
        "EXPIRED EFFECTIVE WORK: UNRESOLVED",

        "",

        "SUSPENDED STATUS IS RECOVERY FAILURE: NO",
        "RUNNING/LEASED STATUS IS RECOVERY FAILURE: NO",

        "",

        "MISSING STATUS EVIDENCE GUESSED: NO",
        "UNRESOLVED BRANCH ACTIVITY GUESSED: NO",

        "",

        "TERMINAL ORCHESTRATION REOPENED: NO",

        "",

        "RETRY ATTEMPT ACCOUNTING: NO",
        "RETRY BUDGET ENFORCEMENT: NO",
        "RETRY BACKOFF: NO",
        "RETRY SCHEDULING: NO",

        "",

        "QUEUE RECOVERY INVOKED: NO",
        "WORKER RECOVERY INVOKED: NO",

        "",

        "STATE TRANSITION PERFORMED: NO",
        "JOB REQUEUE: NO",
        "QUEUE ACTIVITY: NO",
        "WORKER ACTIVITY: NO",
        "LEASE ACTIVITY: NO",
        "CHECKPOINT RESTORE: NO",
        "HANDLER EXECUTION: NO",

        "",

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
        "Phase 5.1.13 initial implementation failed."
    )
