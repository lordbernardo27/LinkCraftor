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
    / "phase_5_1_15_orchestration_completion_initial_implementation.txt"
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

completion = importlib.import_module(
    "backend.server.runtime.universal_orchestration.completion_resolution"
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
    job_ids,
):

    job_tuple = tuple(
        make_job(
            job_id
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
                job_ids
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


def resolve(
    *,
    plan,
    state,
    statuses,
):

    state_snapshot = (
        state_model
        .create_universal_orchestration_state_snapshot(
            identity=plan.identity,
            state=state,
        )
    )

    progress_snapshot = (
        progress
        .track_universal_orchestration_progress(
            execution_plan=plan,
            status_evidence=statuses,
        )
    )

    return (
        completion
        .resolve_universal_orchestration_completion(
            state_snapshot=state_snapshot,
            progress_snapshot=progress_snapshot,
        )
    )


plan = make_plan(
    "completion-initial",
    (
        "a",
        "b",
    ),
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
    ==
    "sha256",
)


# SUCCESS

success = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "succeeded",
        "b": "succeeded",
    },
)


check(
    "all_success_succeeded",
    success.disposition
    is
    completion.UniversalOrchestrationCompletionDisposition.SUCCEEDED,
)

check(
    "success_target_succeeded",
    success.target_terminal_state
    is
    state_model.UniversalOrchestrationState.SUCCEEDED,
)

check(
    "success_complete",
    success.is_complete,
)

check(
    "success_successful",
    success.is_successful,
)


# NONTERMINAL

running = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "succeeded",
        "b": "running",
    },
)


check(
    "running_not_ready",
    running.disposition
    is
    completion.UniversalOrchestrationCompletionDisposition.NOT_READY,
)

check(
    "running_ids_exact",
    running.nonterminal_effective_job_ids
    == ("b",),
)


# FAILED

failed = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "succeeded",
        "b": "failed",
    },
)


check(
    "failed_resolves_failed",
    failed.disposition
    is
    completion.UniversalOrchestrationCompletionDisposition.FAILED,
)

check(
    "failed_target_exact",
    failed.target_terminal_state
    is
    state_model.UniversalOrchestrationState.FAILED,
)

check(
    "failed_ids_exact",
    failed.failed_effective_job_ids
    == ("b",),
)


# DEAD LETTER

dead_letter = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "succeeded",
        "b": "dead_letter",
    },
)


check(
    "dead_letter_failed",
    dead_letter.disposition
    is
    completion.UniversalOrchestrationCompletionDisposition.FAILED,
)


# EXPIRED

expired = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "succeeded",
        "b": "expired",
    },
)


check(
    "expired_failed",
    expired.disposition
    is
    completion.UniversalOrchestrationCompletionDisposition.FAILED,
)


# CANCELLED

cancelled = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "succeeded",
        "b": "cancelled",
    },
)


check(
    "cancelled_deferred",
    cancelled.disposition
    is
    completion.UniversalOrchestrationCompletionDisposition.DEFERRED_TO_TERMINATION,
)

check(
    "cancelled_target_none",
    cancelled.target_terminal_state
    is None,
)


# MISSING

missing = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "succeeded",
        "b": None,
    },
)


check(
    "missing_unresolved",
    missing.disposition
    is
    completion.UniversalOrchestrationCompletionDisposition.UNRESOLVED,
)


# TERMINAL STATE OVERRIDES

terminal_success = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.SUCCEEDED,
    statuses={
        "a": "failed",
        "b": None,
    },
)


check(
    "terminal_success_override",
    terminal_success.disposition
    is
    completion.UniversalOrchestrationCompletionDisposition.SUCCEEDED,
)

check(
    "terminal_success_already_realized",
    terminal_success.is_target_state_already_realized,
)


terminal_failed = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.FAILED,
    statuses={
        "a": "succeeded",
        "b": "succeeded",
    },
)


check(
    "terminal_failed_override",
    terminal_failed.disposition
    is
    completion.UniversalOrchestrationCompletionDisposition.FAILED,
)

check(
    "terminal_failed_already_realized",
    terminal_failed.is_target_state_already_realized,
)


terminal_cancelled = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.CANCELLED,
    statuses={
        "a": "succeeded",
        "b": "succeeded",
    },
)


check(
    "terminal_cancelled_deferred",
    terminal_cancelled.disposition
    is
    completion.UniversalOrchestrationCompletionDisposition.DEFERRED_TO_TERMINATION,
)


# STORED FIELDS

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
    ==
    (
        "state_snapshot",
        "progress_snapshot",
        "schema_version",
    ),
    field_names,
)


# IMMUTABILITY

for field in fields(
    success
):

    try:

        setattr(
            success,
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


# DECISION ID

decision_id = (
    success.completion_decision_id
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
    resolve(
        plan=plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "a": "succeeded",
            "b": "succeeded",
        },
    )
    .completion_decision_id,
)


# TRANSITION LEGALITY

expected_legal = (
    state_model
    .can_transition_universal_orchestration_state(
        current_state=state_model.UniversalOrchestrationState.ACTIVE,
        target_state=state_model.UniversalOrchestrationState.SUCCEEDED,
    )
)


check(
    "may_transition_matches_5_1_3",
    success.may_transition_to_target
    ==
    expected_legal,
)


# EXPLANATION

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
    explanation.get(
        "phase"
    )
    ==
    "5.1.15",
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


# IMPORT BOUNDARY

source = COMPLETION_PATH.read_text(
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
    ==
    [
        "backend.server.runtime.universal_orchestration.state_model",
        "backend.server.runtime.universal_orchestration.progress_tracking",
    ],
    backend_imports,
)


# FORBIDDEN CALLS

forbidden_calls = {
    "transition_universal_orchestration_state",

    "evaluate_universal_orchestration_recovery",
    "evaluate_universal_orchestration_suspension_resume_eligibility",

    "track_universal_orchestration_progress",

    "append_record",
    "load_latest_record",
    "load_record",

    "enqueue_job",
    "dequeue_job",
    "claim_job",

    "assign_universal_worker",
    "acquire_universal_worker_lease",

    "dispatch_registered_runtime_handler",
    "execute_registered_runtime_job_v1",

    "get_runtime_state_store_registry",

    "open",
    "read_text",
    "write_text",

    "time",
    "now",
    "utcnow",

    "persist",
    "save",
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


completion_ast = (
    ast_sha(
        COMPLETION_PATH
    )
)


check(
    "completion_ast_generated",
    len(
        completion_ast
    )
    == 64,
    completion_ast,
)


# PROTECTED MATRIX

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
        ==
        expected,
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
        "PHASE 5.1.15 — UNIVERSAL ORCHESTRATION "
        "COMPLETION RESOLUTION INITIAL IMPLEMENTATION"
    ),

    "=" * 118,

    "",

    (
        "ORCHESTRATION COMPLETION RESOLUTION AST SHA256: "
        + completion_ast
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
            "INITIAL ORCHESTRATION COMPLETION RESOLUTION RESULT: "
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

        "5.1.1–5.1.14 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "ALL EFFECTIVE SUCCEEDED => SUCCEEDED",
        "TERMINAL UNSUCCESSFUL EFFECTIVE WORK => FAILED",
        "NONTERMINAL EFFECTIVE WORK => NOT_READY",
        "MISSING/UNRESOLVED EVIDENCE => UNRESOLVED",
        "CANCELLED EFFECTIVE WORK => DEFERRED_TO_TERMINATION",

        "",

        "FAILED RECOVERY RECOMPUTED: NO",
        "5.1.13 IMPORTED: NO",

        "",

        "TARGET CANCELLED: NO",
        "STATE TRANSITION PERFORMED: NO",

        "",

        "PERSISTENCE: NO",
        "TERMINATION RESOLUTION: NO",
        "PERMANENT EVIDENCE RECORDING: NO",

        "",

        "QUEUE ACTIVITY: NO",
        "WORKER ACTIVITY: NO",
        "LEASE ACTIVITY: NO",
        "JOB EXECUTION: NO",

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
        "Phase 5.1.15 initial implementation failed."
    )
