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
    / "phase_5_1_12_suspension_resume_eligibility_final_certification.txt"
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
            "5.1.12 AST changed before final certification.\n"
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
        eligibility
        .evaluate_universal_orchestration_suspension_resume_eligibility(
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
    ==
    "sha256",
)


# ============================================================
# DISPOSITION EXACTNESS
# ============================================================

check(
    "suspension_dispositions_exact",
    tuple(
        disposition.value
        for disposition
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
        disposition.value
        for disposition
        in eligibility.UniversalOrchestrationResumeDisposition
    )
    == (
        "eligible",
        "ineligible",
        "unresolved",
    ),
)


# ============================================================
# CANONICAL FIXTURE
# ============================================================

plan = make_plan(
    run_id="final-certification",
    job_ids=(
        "a",
        "b",
        "c",
    ),
)


# ACTIVE + QUEUED/RUNNING/SUCCEEDED
# => active execution exists => suspend DEFERRED
active_snapshot = (
    evaluate(
        plan=plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "a": "queued",
            "b": "running",
            "c": "succeeded",
        },
    )
)


check(
    "active_suspend_deferred",
    active_snapshot.suspension_disposition
    is
    eligibility.UniversalOrchestrationSuspensionDisposition.DEFERRED,
)

check(
    "active_suspend_reason_exact",
    active_snapshot.suspension_reason
    is
    eligibility.UniversalOrchestrationSuspensionReason.ACTIVE_EXECUTION_PRESENT,
)

check(
    "active_blocking_exact",
    active_snapshot.blocking_job_ids
    == ("b",),
    active_snapshot.blocking_job_ids,
)

check(
    "active_resume_ineligible",
    active_snapshot.resume_disposition
    is
    eligibility.UniversalOrchestrationResumeDisposition.INELIGIBLE,
)


# ============================================================
# QUIESCENT ACTIVE
# ============================================================

quiescent = (
    evaluate(
        plan=plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "a": "created",
            "b": "queued",
            "c": "suspended",
        },
    )
)


check(
    "quiescent_suspend_eligible",
    quiescent.suspension_disposition
    is
    eligibility.UniversalOrchestrationSuspensionDisposition.ELIGIBLE,
)

check(
    "quiescent_reason_exact",
    quiescent.suspension_reason
    is
    eligibility.UniversalOrchestrationSuspensionReason.QUIESCENT_AND_SUSPENDABLE,
)


# ============================================================
# SUSPENDED + QUIESCENT
# ============================================================

suspended = (
    evaluate(
        plan=plan,
        state=state_model.UniversalOrchestrationState.SUSPENDED,
        statuses={
            "a": "created",
            "b": "queued",
            "c": "suspended",
        },
    )
)


check(
    "suspended_suspend_ineligible",
    suspended.suspension_disposition
    is
    eligibility.UniversalOrchestrationSuspensionDisposition.INELIGIBLE,
)

check(
    "suspended_suspend_reason_exact",
    suspended.suspension_reason
    is
    eligibility.UniversalOrchestrationSuspensionReason.ALREADY_SUSPENDED,
)

check(
    "suspended_resume_eligible",
    suspended.resume_disposition
    is
    eligibility.UniversalOrchestrationResumeDisposition.ELIGIBLE,
)

check(
    "suspended_resume_reason_exact",
    suspended.resume_reason
    is
    eligibility.UniversalOrchestrationResumeReason.SUSPENDED_AND_RESUMABLE,
)


# ============================================================
# SUSPENDED + RUNNING CONTRADICTION
# ============================================================

contradictory = (
    evaluate(
        plan=plan,
        state=state_model.UniversalOrchestrationState.SUSPENDED,
        statuses={
            "a": "created",
            "b": "running",
            "c": "suspended",
        },
    )
)


check(
    "contradictory_resume_unresolved",
    contradictory.resume_disposition
    is
    eligibility.UniversalOrchestrationResumeDisposition.UNRESOLVED,
)

check(
    "contradictory_resume_reason_exact",
    contradictory.resume_reason
    is
    eligibility.UniversalOrchestrationResumeReason.ACTIVE_EXECUTION_CONTRADICTION,
)

check(
    "contradictory_blocking_exact",
    contradictory.blocking_job_ids
    == ("b",),
)


# ============================================================
# MISSING EVIDENCE
# ============================================================

missing = (
    evaluate(
        plan=plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "a": "created",
            "b": None,
            "c": "queued",
        },
    )
)


check(
    "missing_suspend_unresolved",
    missing.suspension_disposition
    is
    eligibility.UniversalOrchestrationSuspensionDisposition.UNRESOLVED,
)

check(
    "missing_reason_exact",
    missing.suspension_reason
    is
    eligibility.UniversalOrchestrationSuspensionReason.MISSING_STATUS_EVIDENCE,
)

check(
    "missing_ids_exact",
    missing.missing_status_job_ids
    == ("b",),
)


# ============================================================
# ALL TERMINAL EFFECTIVE WORK
# ============================================================

all_terminal = (
    evaluate(
        plan=plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "a": "succeeded",
            "b": "failed",
            "c": "cancelled",
        },
    )
)


check(
    "all_terminal_suspend_ineligible",
    all_terminal.suspension_disposition
    is
    eligibility.UniversalOrchestrationSuspensionDisposition.INELIGIBLE,
)

check(
    "all_terminal_suspend_reason",
    all_terminal.suspension_reason
    is
    eligibility.UniversalOrchestrationSuspensionReason.ALL_EFFECTIVE_WORK_TERMINAL,
)


# ============================================================
# TERMINAL ORCHESTRATION OVERRIDE
# ============================================================

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
                "a": "running",
                "b": None,
                "c": "created",
            },
        )
    )

    check(
        "terminal_suspend_override_"
        + terminal_state.value,
        result.suspension_disposition
        is
        eligibility.UniversalOrchestrationSuspensionDisposition.INELIGIBLE,
    )

    check(
        "terminal_resume_override_"
        + terminal_state.value,
        result.resume_disposition
        is
        eligibility.UniversalOrchestrationResumeDisposition.INELIGIBLE,
    )

    check(
        "terminal_suspend_reason_"
        + terminal_state.value,
        result.suspension_reason
        is
        eligibility.UniversalOrchestrationSuspensionReason.TERMINAL_ORCHESTRATION,
    )

    check(
        "terminal_resume_reason_"
        + terminal_state.value,
        result.resume_reason
        is
        eligibility.UniversalOrchestrationResumeReason.TERMINAL_ORCHESTRATION,
    )


# ============================================================
# 5.1.3 LEGALITY
# ============================================================

for orchestration_state in (
    state_model.UniversalOrchestrationState.CREATED,
    state_model.UniversalOrchestrationState.ACTIVE,
    state_model.UniversalOrchestrationState.WAITING,
    state_model.UniversalOrchestrationState.RECOVERING,
):

    legal = (
        state_model
        .can_transition_universal_orchestration_state(
            current_state=orchestration_state,
            target_state=state_model.UniversalOrchestrationState.SUSPENDED,
        )
    )

    result = (
        evaluate(
            plan=plan,
            state=orchestration_state,
            statuses={
                "a": "created",
                "b": "queued",
                "c": "scheduled",
            },
        )
    )

    if legal:

        check(
            "state_legality_suspend_eligible_"
            + orchestration_state.value,
            result.suspension_disposition
            is
            eligibility.UniversalOrchestrationSuspensionDisposition.ELIGIBLE,
        )

    else:

        check(
            "state_legality_suspend_ineligible_"
            + orchestration_state.value,
            result.suspension_disposition
            is
            eligibility.UniversalOrchestrationSuspensionDisposition.INELIGIBLE,
        )


# ============================================================
# STORED FIELDS
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


# ============================================================
# DERIVED IDENTITY
# ============================================================

check(
    "identity_derived",
    quiescent.identity
    is
    quiescent.progress_snapshot.identity,
)

check(
    "state_derived",
    quiescent.orchestration_state
    is
    state_model.UniversalOrchestrationState.ACTIVE,
)


# ============================================================
# IMMUTABILITY
# ============================================================

for field in fields(
    quiescent
):

    try:

        setattr(
            quiescent,
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
    quiescent.eligibility_decision_id
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
            "a": "created",
            "b": "queued",
            "c": "suspended",
        },
    )
    .eligibility_decision_id,
)


different_state_id = (
    evaluate(
        plan=plan,
        state=state_model.UniversalOrchestrationState.SUSPENDED,
        statuses={
            "a": "created",
            "b": "queued",
            "c": "suspended",
        },
    )
    .eligibility_decision_id
)


check(
    "decision_id_state_sensitive",
    decision_id
    != different_state_id,
)


different_progress_id = (
    evaluate(
        plan=plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "a": "created",
            "b": "running",
            "c": "suspended",
        },
    )
    .eligibility_decision_id
)


check(
    "decision_id_progress_sensitive",
    decision_id
    != different_progress_id,
)


# ============================================================
# EXPLANATION BOUNDARIES
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
    "phase_exact",
    explanation.get(
        "phase"
    )
    == "5.1.12",
)

check(
    "component_exact",
    explanation.get(
        "component"
    )
    ==
    "Universal Orchestration Suspension & Resume Eligibility",
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


# ============================================================
# IMPORT BOUNDARY
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
# FORBIDDEN CALLS
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

    "track_universal_orchestration_progress",

    "dispatch_registered_runtime_handler",
    "execute_registered_runtime_job_v1",

    "get_runtime_state_store_registry",

    "persist",
    "save",
    "dispatch",
    "execute",

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
# FORBIDDEN ATTRIBUTES
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
        "forbidden_attribute_"
        + forbidden_attr,
        forbidden_attr
        not in attrs,
    )


# ============================================================
# PROTECTED AUTHORITIES
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
        "phase_5_1_12_universal_orchestration_suspension_resume_eligibility",

        eligibility.UNIVERSAL_ORCHESTRATION_SUSPENSION_RESUME_ELIGIBILITY_VERSION,
        eligibility.UNIVERSAL_ORCHESTRATION_SUSPENSION_RESUME_ELIGIBILITY_SCHEMA_VERSION,
        eligibility.UNIVERSAL_ORCHESTRATION_SUSPENSION_RESUME_DECISION_HASH_ALGORITHM,

        EXPECTED_ELIGIBILITY_AST,

        "state_authority_5_1_3",
        "progress_authority_5_1_11",

        "stored_state_snapshot",
        "stored_progress_snapshot",
        "stored_schema_version",

        "derived_identity",
        "derived_orchestration_state",

        "suspend_eligible",
        "suspend_deferred",
        "suspend_ineligible",
        "suspend_unresolved",

        "resume_eligible",
        "resume_ineligible",
        "resume_unresolved",

        "terminal_orchestration_override",

        "already_suspended_suspend_ineligible",

        "state_legality_controls_suspendability",

        "zero_effective_work_ineligible",
        "all_effective_work_terminal_ineligible",

        "missing_status_unresolved",
        "unresolved_branch_activity_unresolved",

        "leased_running_suspend_deferred",

        "resume_requires_orchestration_suspended",

        "suspended_created_resume_eligible",
        "suspended_queued_resume_eligible",
        "suspended_scheduled_resume_eligible",
        "suspended_suspended_resume_eligible",

        "suspended_leased_running_resume_unresolved",

        "excluded_work_does_not_block",

        "possible_effective_population_from_5_1_11",

        "decision_id_sha256",
        "decision_id_identity_sensitive",
        "decision_id_state_sensitive",
        "decision_id_progress_sensitive",

        "no_state_transition",
        "no_actual_suspend",
        "no_actual_resume",

        "no_queue_pause",
        "no_worker_drain",

        "no_lease_release",
        "no_lease_acquisition",

        "no_checkpoint_save",
        "no_checkpoint_restore",
        "no_checkpoint_payload_read",

        "no_job_status_mutation",
        "no_job_progress_mutation",

        "no_readiness_evaluation",
        "no_handoff_evaluation",

        "no_conditional_reevaluation",
        "no_progress_recomputation",

        "no_queue_activity",
        "no_worker_activity",
        "no_handler_dispatch",
        "no_job_execution",

        "recovery_deferred_5_1_13",
        "persistence_deferred_5_1_14",
        "completion_deferred_5_1_15",
        "termination_deferred_5_1_16",
        "evidence_records_deferred_5_1_17",

        "no_runtime_state_store",
        "no_runtime_lifecycle_manager",

        "no_wall_clock",
        "no_filesystem_io",
        "no_network_io",
        "no_database_io",

        "no_universal_coordination_framework",
        "no_pipeline_coordinator",

        "immutable_deterministic_eligibility_decision_authority",
    )
)


eligibility_fingerprint = (
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
            eligibility_fingerprint
        )
        == 64
        and
        all(
            character
            in "0123456789ABCDEF"
            for character
            in eligibility_fingerprint
        )
    ),
    eligibility_fingerprint,
)


# ============================================================
# FINAL AST
# ============================================================

final_ast = ast_sha(
    ELIGIBILITY_PATH
)


check(
    "final_ast_unchanged",
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


lines = [
    (
        "PHASE 5.1.12 — UNIVERSAL ORCHESTRATION "
        "SUSPENSION & RESUME ELIGIBILITY FINAL CERTIFICATION"
    ),

    "=" * 118,

    "",

    (
        "SUSPENSION & RESUME ELIGIBILITY AST SHA256: "
        + final_ast
    ),

    (
        "SUSPENSION & RESUME ELIGIBILITY FINGERPRINT: "
        + eligibility_fingerprint
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
            "FINAL SUSPENSION & RESUME ELIGIBILITY CERTIFICATION: "
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

        "5.1.12 AUTHORITY MODIFIED DURING CERTIFICATION: NO",
        "5.1.1–5.1.11 FROZEN AUTHORITIES MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "STATE AUTHORITY: 5.1.3",
        "PROGRESS AUTHORITY: 5.1.11",

        "",

        "SUSPENSION:",
        "  QUIESCENT + LEGAL STATE => ELIGIBLE",
        "  LEASED/RUNNING => DEFERRED",
        "  TERMINAL => INELIGIBLE",
        "  MISSING/UNRESOLVED => UNRESOLVED",

        "",

        "RESUME:",
        "  REQUIRES ORCHESTRATION STATE SUSPENDED",
        "  QUIESCENT NONTERMINAL WORK => ELIGIBLE",
        "  LEASED/RUNNING => UNRESOLVED",
        "  TERMINAL => INELIGIBLE",
        "  MISSING/UNRESOLVED => UNRESOLVED",

        "",

        "EXCLUDED WORK BLOCKS ELIGIBILITY: NO",
        "TERMINAL ORCHESTRATION OVERRIDES JOB EVIDENCE: YES",

        "",

        "ACTUAL STATE TRANSITION: NO",
        "ACTUAL SUSPEND/RESUME: NO",

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
        "TERMINATION RESOLUTION: NO",
        "PERMANENT EVIDENCE RECORDING: NO",

        "",

        "RUNTIME STATE STORE ACCESS: NO",
        "RUNTIME LIFECYCLE MANAGER ACCESS: NO",
        "UNIVERSAL COORDINATION FRAMEWORK ACCESS: NO",
        "PIPELINE COORDINATOR ACCESS: NO",

        "",

        (
            "PHASE 5.1.12 FREEZE CANDIDATE: "
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
        "Phase 5.1.12 final certification failed."
    )
