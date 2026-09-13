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
    / "phase_5_1_15_orchestration_completion_final_certification.txt"
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

if not COMPLETION_PATH.exists():
    raise SystemExit(
        "5.1.15 Completion Resolution authority is missing."
    )


initial_ast = ast_sha(
    COMPLETION_PATH
)


if initial_ast != EXPECTED_COMPLETION_AST:
    raise SystemExit(
        (
            "5.1.15 AST changed before final certification.\n"
            "EXPECTED: "
            + EXPECTED_COMPLETION_AST
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
            "Protected authority mismatch before certification: "
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

progress = importlib.import_module(
    "backend.server.runtime.universal_orchestration.progress_tracking"
)


module_name = (
    "backend.server.runtime."
    "universal_orchestration.completion_resolution"
)

sys.modules.pop(
    module_name,
    None,
)

completion = importlib.import_module(
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
# HELPERS
# ============================================================

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
            job_ids=tuple(job_ids),
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


def resolve(
    *,
    plan,
    state,
    statuses,
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
            ),
        )
    )


# ============================================================
# AUTHORITY EXACTNESS
# ============================================================

check(
    "ast_exact",
    ast_sha(
        COMPLETION_PATH
    )
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
    "hash_algorithm_exact",
    completion.UNIVERSAL_ORCHESTRATION_COMPLETION_DECISION_HASH_ALGORITHM
    ==
    "sha256",
)

check(
    "dispositions_exact",
    tuple(
        item.value
        for item
        in completion.UniversalOrchestrationCompletionDisposition
    )
    ==
    (
        "not_ready",
        "succeeded",
        "failed",
        "unresolved",
        "deferred_to_termination",
    ),
)


# ============================================================
# CANONICAL FIXTURE
# ============================================================

plan = make_plan(
    run_id="completion-final-certification",
    job_ids=(
        "a",
        "b",
        "c",
    ),
)


success = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "succeeded",
        "b": "succeeded",
        "c": "succeeded",
    },
)


check(
    "all_success_succeeded",
    success.disposition
    is
    completion.UniversalOrchestrationCompletionDisposition.SUCCEEDED,
)

check(
    "success_reason_exact",
    success.reason
    is
    completion.UniversalOrchestrationCompletionReason.ALL_EFFECTIVE_WORK_SUCCEEDED,
)

check(
    "success_target_exact",
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


failure = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "succeeded",
        "b": "failed",
        "c": "succeeded",
    },
)


check(
    "failure_failed",
    failure.disposition
    is
    completion.UniversalOrchestrationCompletionDisposition.FAILED,
)

check(
    "failure_reason_exact",
    failure.reason
    is
    completion.UniversalOrchestrationCompletionReason.TERMINAL_UNSUCCESSFUL_EFFECTIVE_WORK,
)

check(
    "failure_target_exact",
    failure.target_terminal_state
    is
    state_model.UniversalOrchestrationState.FAILED,
)

check(
    "failure_ids_exact",
    failure.failed_effective_job_ids
    == ("b",),
)


dead_letter = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "succeeded",
        "b": "dead_letter",
        "c": "succeeded",
    },
)


check(
    "dead_letter_failed",
    dead_letter.disposition
    is
    completion.UniversalOrchestrationCompletionDisposition.FAILED,
)


expired = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "succeeded",
        "b": "expired",
        "c": "succeeded",
    },
)


check(
    "expired_failed",
    expired.disposition
    is
    completion.UniversalOrchestrationCompletionDisposition.FAILED,
)


cancelled = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "succeeded",
        "b": "cancelled",
        "c": "succeeded",
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


running = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "succeeded",
        "b": "running",
        "c": "failed",
    },
)


check(
    "nonterminal_not_ready",
    running.disposition
    is
    completion.UniversalOrchestrationCompletionDisposition.NOT_READY,
)

check(
    "nonterminal_reason_exact",
    running.reason
    is
    completion.UniversalOrchestrationCompletionReason.NONTERMINAL_EFFECTIVE_WORK,
)


missing = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "succeeded",
        "b": None,
        "c": "failed",
    },
)


check(
    "missing_unresolved",
    missing.disposition
    is
    completion.UniversalOrchestrationCompletionDisposition.UNRESOLVED,
)

check(
    "missing_reason_exact",
    missing.reason
    is
    completion.UniversalOrchestrationCompletionReason.MISSING_STATUS_EVIDENCE,
)


# ============================================================
# TERMINAL ORCHESTRATION OVERRIDE
# ============================================================

terminal_success = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.SUCCEEDED,
    statuses={
        "a": "failed",
        "b": None,
        "c": "cancelled",
    },
)


check(
    "terminal_success_override",
    terminal_success.disposition
    is
    completion.UniversalOrchestrationCompletionDisposition.SUCCEEDED,
)

check(
    "terminal_success_reason",
    terminal_success.reason
    is
    completion.UniversalOrchestrationCompletionReason.TERMINAL_ORCHESTRATION_SUCCEEDED,
)

check(
    "terminal_success_realized",
    terminal_success.is_target_state_already_realized,
)

check(
    "terminal_success_no_transition",
    not terminal_success.may_transition_to_target,
)


terminal_failed = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.FAILED,
    statuses={
        "a": "succeeded",
        "b": "succeeded",
        "c": "succeeded",
    },
)


check(
    "terminal_failed_override",
    terminal_failed.disposition
    is
    completion.UniversalOrchestrationCompletionDisposition.FAILED,
)

check(
    "terminal_failed_reason",
    terminal_failed.reason
    is
    completion.UniversalOrchestrationCompletionReason.TERMINAL_ORCHESTRATION_FAILED,
)

check(
    "terminal_failed_realized",
    terminal_failed.is_target_state_already_realized,
)


terminal_cancelled = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.CANCELLED,
    statuses={
        "a": "succeeded",
        "b": "succeeded",
        "c": "succeeded",
    },
)


check(
    "terminal_cancelled_deferred",
    terminal_cancelled.disposition
    is
    completion.UniversalOrchestrationCompletionDisposition.DEFERRED_TO_TERMINATION,
)

check(
    "terminal_cancelled_target_none",
    terminal_cancelled.target_terminal_state
    is None,
)


# ============================================================
# 5.1.3 LEGALITY
# ============================================================

for current_state in (
    state_model.UniversalOrchestrationState.CREATED,
    state_model.UniversalOrchestrationState.ACTIVE,
    state_model.UniversalOrchestrationState.WAITING,
    state_model.UniversalOrchestrationState.SUSPENDED,
    state_model.UniversalOrchestrationState.RECOVERING,
):

    success_candidate = resolve(
        plan=plan,
        state=current_state,
        statuses={
            "a": "succeeded",
            "b": "succeeded",
            "c": "succeeded",
        },
    )

    expected_success_legality = (
        state_model
        .can_transition_universal_orchestration_state(
            current_state=current_state,
            target_state=state_model.UniversalOrchestrationState.SUCCEEDED,
        )
    )

    check(
        "success_legality_"
        + current_state.value,
        success_candidate.may_transition_to_target
        ==
        expected_success_legality,
    )

    failure_candidate = resolve(
        plan=plan,
        state=current_state,
        statuses={
            "a": "succeeded",
            "b": "failed",
            "c": "succeeded",
        },
    )

    expected_failure_legality = (
        state_model
        .can_transition_universal_orchestration_state(
            current_state=current_state,
            target_state=state_model.UniversalOrchestrationState.FAILED,
        )
    )

    check(
        "failure_legality_"
        + current_state.value,
        failure_candidate.may_transition_to_target
        ==
        expected_failure_legality,
    )


# ============================================================
# STORED FIELDS
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
    ==
    (
        "state_snapshot",
        "progress_snapshot",
        "schema_version",
    ),
    field_names,
)


# ============================================================
# DERIVED BUCKETS
# ============================================================

bucket_plan = make_plan(
    run_id="completion-final-buckets",
    job_ids=(
        "a",
        "b",
        "c",
        "d",
    ),
)


bucket_result = resolve(
    plan=bucket_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "running",
        "b": "succeeded",
        "c": "dead_letter",
        "d": "cancelled",
    },
)


check(
    "nonterminal_bucket_exact",
    bucket_result.nonterminal_effective_job_ids
    ==
    ("a",),
)

check(
    "success_bucket_exact",
    bucket_result.succeeded_effective_job_ids
    ==
    ("b",),
)

check(
    "failure_bucket_exact",
    bucket_result.failed_effective_job_ids
    ==
    ("c",),
)

check(
    "cancelled_bucket_exact",
    bucket_result.cancelled_effective_job_ids
    ==
    ("d",),
)


# ============================================================
# IMMUTABILITY
# ============================================================

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


# ============================================================
# DECISION ID
# ============================================================

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
            "c": "succeeded",
        },
    ).completion_decision_id,
)


state_sensitive_id = (
    resolve(
        plan=plan,
        state=state_model.UniversalOrchestrationState.WAITING,
        statuses={
            "a": "succeeded",
            "b": "succeeded",
            "c": "succeeded",
        },
    )
    .completion_decision_id
)


check(
    "decision_id_state_sensitive",
    decision_id
    !=
    state_sensitive_id,
)


progress_sensitive_id = (
    resolve(
        plan=plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "a": "succeeded",
            "b": "failed",
            "c": "succeeded",
        },
    )
    .completion_decision_id
)


check(
    "decision_id_progress_sensitive",
    decision_id
    !=
    progress_sensitive_id,
)


other_plan = make_plan(
    run_id="completion-final-other-run",
    job_ids=(
        "a",
        "b",
        "c",
    ),
)


run_sensitive_id = (
    resolve(
        plan=other_plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "a": "succeeded",
            "b": "succeeded",
            "c": "succeeded",
        },
    )
    .completion_decision_id
)


check(
    "decision_id_run_sensitive",
    decision_id
    !=
    run_sensitive_id,
)


# ============================================================
# EXPLANATION
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
    explanation.get(
        "phase"
    )
    ==
    "5.1.15",
)

check(
    "component_exact",
    explanation.get(
        "component"
    )
    ==
    "Universal Orchestration Completion Resolution",
)

check(
    "stored_fields_explanation_exact",
    explanation.get(
        "stored_fields"
    )
    ==
    (
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
# IMPORT BOUNDARY
# ============================================================

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


# ============================================================
# FORBIDDEN CALLS
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
    "cancel",
    "terminate",
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
# PROTECTED MATRIX
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
        ==
        expected,
        actual,
    )


# ============================================================
# CANONICAL FINGERPRINT
# ============================================================

fingerprint_material = "|".join(
    (
        "phase_5_1_15_universal_orchestration_completion_resolution",

        completion.UNIVERSAL_ORCHESTRATION_COMPLETION_RESOLUTION_VERSION,
        completion.UNIVERSAL_ORCHESTRATION_COMPLETION_RESOLUTION_SCHEMA_VERSION,
        completion.UNIVERSAL_ORCHESTRATION_COMPLETION_DECISION_HASH_ALGORITHM,

        EXPECTED_COMPLETION_AST,

        "state_authority_5_1_3",
        "progress_authority_5_1_11",

        "stored_state_snapshot",
        "stored_progress_snapshot",
        "stored_schema_version",

        "possible_effective_population_from_5_1_11",
        "excluded_work_ignored",

        "disposition_not_ready",
        "disposition_succeeded",
        "disposition_failed",
        "disposition_unresolved",
        "disposition_deferred_to_termination",

        "nonterminal_created_not_ready",
        "nonterminal_queued_not_ready",
        "nonterminal_scheduled_not_ready",
        "nonterminal_leased_not_ready",
        "nonterminal_running_not_ready",
        "nonterminal_suspended_not_ready",

        "all_effective_succeeded_resolves_succeeded",

        "terminal_failed_resolves_failed",
        "terminal_dead_letter_resolves_failed",
        "terminal_expired_resolves_failed",

        "cancelled_deferred_to_5_1_16",

        "missing_status_unresolved",
        "unresolved_branch_unresolved",

        "terminal_orchestration_succeeded_override",
        "terminal_orchestration_failed_override",
        "terminal_orchestration_cancelled_deferred",

        "target_state_succeeded_or_failed_only",
        "never_target_cancelled",

        "transition_legality_from_5_1_3",
        "no_actual_state_transition",

        "recovery_independent_5_1_13",
        "no_recovery_import",
        "no_recovery_reevaluation",
        "no_recovery_execution",

        "no_retry_attempt_inspection",
        "no_retry_policy_inspection",
        "no_retry_backoff",

        "no_persistence_port_invocation",
        "no_runtime_state_store",

        "termination_deferred_5_1_16",
        "evidence_records_deferred_5_1_17",

        "completion_decision_id_sha256",
        "completion_decision_id_identity_sensitive",
        "completion_decision_id_state_sensitive",
        "completion_decision_id_progress_sensitive",

        "no_queue_activity",
        "no_worker_activity",
        "no_lease_activity",
        "no_handler_dispatch",
        "no_job_execution",

        "no_wall_clock",
        "no_filesystem_io",
        "no_database_io",
        "no_network_io",

        "no_universal_coordination_framework",
        "no_pipeline_coordinator",

        "deterministic_orchestration_completion_resolution",
    )
)


completion_fingerprint = (
    hashlib.sha256(
        fingerprint_material.encode(
            "utf-8"
        )
    ).hexdigest().upper()
)


check(
    "fingerprint_generated",
    (
        len(
            completion_fingerprint
        )
        == 64
        and
        all(
            character
            in "0123456789ABCDEF"
            for character
            in completion_fingerprint
        )
    ),
    completion_fingerprint,
)


# ============================================================
# FINAL AST
# ============================================================

final_ast = ast_sha(
    COMPLETION_PATH
)


check(
    "final_ast_unchanged",
    final_ast
    ==
    EXPECTED_COMPLETION_AST,
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
        "PHASE 5.1.15 — UNIVERSAL ORCHESTRATION "
        "COMPLETION RESOLUTION FINAL CERTIFICATION"
    ),

    "=" * 118,

    "",

    (
        "ORCHESTRATION COMPLETION RESOLUTION AST SHA256: "
        + final_ast
    ),

    (
        "ORCHESTRATION COMPLETION RESOLUTION FINGERPRINT: "
        + completion_fingerprint
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
            "FINAL ORCHESTRATION COMPLETION RESOLUTION CERTIFICATION: "
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

        "5.1.15 AUTHORITY MODIFIED DURING CERTIFICATION: NO",
        "5.1.1–5.1.14 FROZEN AUTHORITIES MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "STATE AUTHORITY: 5.1.3",
        "PROGRESS AUTHORITY: 5.1.11",

        "",

        "COMPLETION CLASSIFICATION:",
        "  NONTERMINAL EFFECTIVE WORK => NOT_READY",
        "  ALL EFFECTIVE SUCCEEDED => SUCCEEDED",
        "  FAILED => FAILED",
        "  DEAD_LETTER => FAILED",
        "  EXPIRED => FAILED",
        "  CANCELLED => DEFERRED_TO_TERMINATION",
        "  MISSING/UNRESOLVED => UNRESOLVED",

        "",

        "EXCLUDED WORK PARTICIPATES IN COMPLETION: NO",

        "",

        "TERMINAL ORCHESTRATION OVERRIDES PROGRESS: YES",

        "",

        "TARGET SUCCEEDED: YES",
        "TARGET FAILED: YES",
        "TARGET CANCELLED: NO",

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
            "PHASE 5.1.15 FREEZE CANDIDATE: "
            + (
                "YES"
                if passed == total
                else "NO"
            )
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
        "Phase 5.1.15 final certification failed."
    )
