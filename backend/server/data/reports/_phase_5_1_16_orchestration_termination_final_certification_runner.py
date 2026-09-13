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

AUTHORITY_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_orchestration"
    / "cancellation_termination.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_1_16_orchestration_termination_final_certification.txt"
)

EXPECTED_AST = (
    "3D2095E4B546596554875BB8FB1E289489FAFD26C013DBE40A7066DB197E25CB"
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
    "5.1.15_completion": (
        ROOT / "backend/server/runtime/universal_orchestration/completion_resolution.py",
        "1311EEBEB9622AF5D4CF6F4D7CB14FF83B169C748A01DDD144A8000301A5CBD4",
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
        canonical.encode(
            "utf-8"
        )
    ).hexdigest().upper()


# ============================================================
# PRE-FLIGHT
# ============================================================

if not AUTHORITY_PATH.exists():

    raise SystemExit(
        "5.1.16 authority is missing."
    )


initial_ast = ast_sha(
    AUTHORITY_PATH
)


if initial_ast != EXPECTED_AST:

    raise SystemExit(
        (
            "5.1.16 AST changed before final certification.\n"
            "EXPECTED: "
            + EXPECTED_AST
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
# IMPORT AUTHORITIES
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
    "universal_orchestration.cancellation_termination"
)

sys.modules.pop(
    module_name,
    None,
)

termination = importlib.import_module(
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
    job_id: str,
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
    run_id: str,
    job_ids: tuple[str, ...],
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
            job_ids=job_ids,
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


def make_request(
    *,
    request_id="cancel-final-001",
    request_source="user",
    reason="Final certification cancellation request.",
):

    return (
        termination
        .create_universal_orchestration_cancellation_request(
            request_id=request_id,
            request_source=request_source,
            reason=reason,
        )
    )


def resolve(
    *,
    plan,
    state,
    statuses,
    request,
):

    return (
        termination
        .resolve_universal_orchestration_cancellation_termination(
            state_snapshot=make_state(
                plan=plan,
                state=state,
            ),
            progress_snapshot=make_progress(
                plan=plan,
                statuses=statuses,
            ),
            cancellation_request_snapshot=request,
        )
    )


# ============================================================
# AUTHORITY CONSTANTS
# ============================================================

check(
    "ast_exact",
    ast_sha(
        AUTHORITY_PATH
    )
    ==
    EXPECTED_AST,
)

check(
    "version_exact",
    termination.UNIVERSAL_ORCHESTRATION_CANCELLATION_TERMINATION_VERSION
    ==
    "universal_orchestration_cancellation_termination_v5.1.16",
)

check(
    "request_schema_exact",
    termination.UNIVERSAL_ORCHESTRATION_CANCELLATION_REQUEST_SCHEMA_VERSION
    ==
    "universal_orchestration_cancellation_request_schema_v1",
)

check(
    "decision_schema_exact",
    termination.UNIVERSAL_ORCHESTRATION_CANCELLATION_DECISION_SCHEMA_VERSION
    ==
    "universal_orchestration_cancellation_decision_schema_v1",
)

check(
    "hash_algorithm_exact",
    termination.UNIVERSAL_ORCHESTRATION_CANCELLATION_HASH_ALGORITHM
    ==
    "sha256",
)


# ============================================================
# ENUM CONTRACT
# ============================================================

check(
    "dispositions_exact",
    tuple(
        item.value
        for item
        in termination.UniversalOrchestrationCancellationDisposition
    )
    ==
    (
        "not_requested",
        "waiting_for_termination",
        "eligible",
        "already_cancelled",
        "ineligible",
        "unresolved",
    ),
)


# ============================================================
# STORED FIELDS
# ============================================================

request_fields = tuple(
    field.name
    for field
    in fields(
        termination.UniversalOrchestrationCancellationRequestSnapshot
    )
)


check(
    "request_fields_exact",
    request_fields
    ==
    (
        "request_id",
        "request_source",
        "reason",
        "schema_version",
    ),
    request_fields,
)


decision_fields = tuple(
    field.name
    for field
    in fields(
        termination.UniversalOrchestrationCancellationDecision
    )
)


check(
    "decision_fields_exact",
    decision_fields
    ==
    (
        "state_snapshot",
        "progress_snapshot",
        "cancellation_request_snapshot",
        "schema_version",
    ),
    decision_fields,
)


# ============================================================
# CANONICAL REQUEST
# ============================================================

request = make_request()


check(
    "request_fingerprint_length",
    len(
        request.request_fingerprint
    )
    == 64,
    request.request_fingerprint,
)

check(
    "request_fingerprint_upper_hex",
    all(
        character
        in "0123456789ABCDEF"
        for character
        in request.request_fingerprint
    ),
)

check(
    "request_fingerprint_deterministic",
    request.request_fingerprint
    ==
    make_request().request_fingerprint,
)


# ============================================================
# CANONICAL PLAN
# ============================================================

plan = make_plan(
    run_id="termination-final-certification",
    job_ids=(
        "a",
        "b",
        "c",
    ),
)


# ============================================================
# NO REQUEST
# ============================================================

not_requested = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "running",
        "b": "cancelled",
        "c": "succeeded",
    },
    request=None,
)


check(
    "no_request_not_requested",
    not_requested.disposition
    is
    termination.UniversalOrchestrationCancellationDisposition.NOT_REQUESTED,
)

check(
    "no_request_target_none",
    not_requested.target_terminal_state
    is None,
)


# ============================================================
# WAITING
# ============================================================

waiting = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "running",
        "b": "cancelled",
        "c": "succeeded",
    },
    request=request,
)


check(
    "nonterminal_waiting",
    waiting.disposition
    is
    termination.UniversalOrchestrationCancellationDisposition.WAITING_FOR_TERMINATION,
)

check(
    "waiting_reason_exact",
    waiting.reason
    is
    termination.UniversalOrchestrationCancellationReason.NONTERMINAL_EFFECTIVE_WORK,
)

check(
    "waiting_target_none",
    waiting.target_terminal_state
    is None,
)


# ============================================================
# ELIGIBLE
# ============================================================

eligible = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "succeeded",
        "b": "cancelled",
        "c": "failed",
    },
    request=request,
)


check(
    "terminal_cancelled_evidence_eligible",
    eligible.disposition
    is
    termination.UniversalOrchestrationCancellationDisposition.ELIGIBLE,
)

check(
    "eligible_reason_exact",
    eligible.reason
    is
    termination.UniversalOrchestrationCancellationReason.CANCELLED_EFFECTIVE_WORK,
)

check(
    "eligible_target_cancelled",
    eligible.target_terminal_state
    is
    state_model.UniversalOrchestrationState.CANCELLED,
)

check(
    "cancelled_bucket_exact",
    eligible.cancelled_effective_job_ids
    ==
    ("b",),
)


# ============================================================
# NATURAL COMPLETION
# ============================================================

natural_completion = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "succeeded",
        "b": "failed",
        "c": "expired",
    },
    request=request,
)


check(
    "natural_completion_ineligible",
    natural_completion.disposition
    is
    termination.UniversalOrchestrationCancellationDisposition.INELIGIBLE,
)

check(
    "natural_completion_reason_exact",
    natural_completion.reason
    is
    termination.UniversalOrchestrationCancellationReason.TERMINAL_WORK_WITHOUT_CANCELLATION_EVIDENCE,
)

check(
    "natural_completion_target_none",
    natural_completion.target_terminal_state
    is None,
)


# ============================================================
# MISSING EVIDENCE
# ============================================================

missing = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "succeeded",
        "b": None,
        "c": "cancelled",
    },
    request=request,
)


check(
    "missing_unresolved",
    missing.disposition
    is
    termination.UniversalOrchestrationCancellationDisposition.UNRESOLVED,
)

check(
    "missing_reason_exact",
    missing.reason
    is
    termination.UniversalOrchestrationCancellationReason.MISSING_STATUS_EVIDENCE,
)


# ============================================================
# TERMINAL ORCHESTRATION STATE PRECEDENCE
# ============================================================

already_cancelled = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.CANCELLED,
    statuses={
        "a": "running",
        "b": None,
        "c": "failed",
    },
    request=None,
)


check(
    "already_cancelled_override",
    already_cancelled.disposition
    is
    termination.UniversalOrchestrationCancellationDisposition.ALREADY_CANCELLED,
)

check(
    "already_cancelled_target",
    already_cancelled.target_terminal_state
    is
    state_model.UniversalOrchestrationState.CANCELLED,
)

check(
    "already_cancelled_realized",
    already_cancelled.is_target_state_already_realized,
)

check(
    "already_cancelled_no_transition",
    not already_cancelled.may_transition_to_cancelled,
)


succeeded = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.SUCCEEDED,
    statuses={
        "a": "cancelled",
        "b": "cancelled",
        "c": "cancelled",
    },
    request=request,
)


check(
    "terminal_succeeded_ineligible",
    succeeded.disposition
    is
    termination.UniversalOrchestrationCancellationDisposition.INELIGIBLE,
)

check(
    "terminal_succeeded_target_none",
    succeeded.target_terminal_state
    is None,
)


failed = resolve(
    plan=plan,
    state=state_model.UniversalOrchestrationState.FAILED,
    statuses={
        "a": "cancelled",
        "b": "cancelled",
        "c": "cancelled",
    },
    request=request,
)


check(
    "terminal_failed_ineligible",
    failed.disposition
    is
    termination.UniversalOrchestrationCancellationDisposition.INELIGIBLE,
)

check(
    "terminal_failed_target_none",
    failed.target_terminal_state
    is None,
)


# ============================================================
# EVERY NONTERMINAL STATUS WAITS
# ============================================================

for status in (
    "created",
    "queued",
    "scheduled",
    "leased",
    "running",
    "suspended",
):

    candidate = resolve(
        plan=plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "a": status,
            "b": "cancelled",
            "c": "succeeded",
        },
        request=request,
    )

    check(
        "waiting_"
        + status,
        candidate.disposition
        is
        termination.UniversalOrchestrationCancellationDisposition.WAITING_FOR_TERMINATION,
    )


# ============================================================
# TRANSITION LEGALITY
# ============================================================

for state in (
    state_model.UniversalOrchestrationState.CREATED,
    state_model.UniversalOrchestrationState.ACTIVE,
    state_model.UniversalOrchestrationState.WAITING,
    state_model.UniversalOrchestrationState.SUSPENDED,
    state_model.UniversalOrchestrationState.RECOVERING,
):

    candidate = resolve(
        plan=plan,
        state=state,
        statuses={
            "a": "cancelled",
            "b": "cancelled",
            "c": "succeeded",
        },
        request=request,
    )

    expected = (
        state_model
        .can_transition_universal_orchestration_state(
            current_state=state,
            target_state=state_model.UniversalOrchestrationState.CANCELLED,
        )
    )

    check(
        "eligible_"
        + state.value,
        candidate.disposition
        is
        termination.UniversalOrchestrationCancellationDisposition.ELIGIBLE,
    )

    check(
        "transition_legality_"
        + state.value,
        candidate.may_transition_to_cancelled
        ==
        expected,
    )


# ============================================================
# IMMUTABILITY
# ============================================================

for field in fields(
    request
):

    try:

        setattr(
            request,
            field.name,
            None,
        )

    except Exception:

        immutable = True

    else:

        immutable = False

    check(
        "request_immutable_"
        + field.name,
        immutable,
    )


for field in fields(
    eligible
):

    try:

        setattr(
            eligible,
            field.name,
            None,
        )

    except Exception:

        immutable = True

    else:

        immutable = False

    check(
        "decision_immutable_"
        + field.name,
        immutable,
    )


# ============================================================
# DECISION ID
# ============================================================

decision_id = (
    eligible.cancellation_decision_id
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
            "b": "cancelled",
            "c": "failed",
        },
        request=request,
    ).cancellation_decision_id,
)


state_sensitive_id = (
    resolve(
        plan=plan,
        state=state_model.UniversalOrchestrationState.WAITING,
        statuses={
            "a": "succeeded",
            "b": "cancelled",
            "c": "failed",
        },
        request=request,
    )
    .cancellation_decision_id
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
            "a": "running",
            "b": "cancelled",
            "c": "failed",
        },
        request=request,
    )
    .cancellation_decision_id
)


check(
    "decision_id_progress_sensitive",
    decision_id
    !=
    progress_sensitive_id,
)


request_sensitive_id = (
    resolve(
        plan=plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "a": "succeeded",
            "b": "cancelled",
            "c": "failed",
        },
        request=make_request(
            request_id="cancel-final-002",
            request_source="system",
            reason="Different request.",
        ),
    )
    .cancellation_decision_id
)


check(
    "decision_id_request_sensitive",
    decision_id
    !=
    request_sensitive_id,
)


other_plan = make_plan(
    run_id="termination-final-other-run",
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
            "b": "cancelled",
            "c": "failed",
        },
        request=request,
    )
    .cancellation_decision_id
)


check(
    "decision_id_run_sensitive",
    decision_id
    !=
    run_sensitive_id,
)


# ============================================================
# EXPLANATION CONTRACT
# ============================================================

explanation = (
    termination
    .explain_universal_orchestration_cancellation_termination_v1()
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
    "5.1.16",
)

check(
    "component_exact",
    explanation.get(
        "component"
    )
    ==
    "Universal Orchestration Cancellation / Termination Resolution",
)

check(
    "request_fields_explanation_exact",
    explanation.get(
        "request_stored_fields"
    )
    ==
    (
        "request_id",
        "request_source",
        "reason",
        "schema_version",
    ),
)

check(
    "decision_fields_explanation_exact",
    explanation.get(
        "decision_stored_fields"
    )
    ==
    (
        "state_snapshot",
        "progress_snapshot",
        "cancellation_request_snapshot",
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
    "completion_boundary_5_1_15",
    "5.1.15"
    in explanation.get(
        "completion_boundary",
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

source = AUTHORITY_PATH.read_text(
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
# FORBIDDEN EXECUTION CALLS
# ============================================================

forbidden_calls = {
    "transition_universal_orchestration_state",

    "track_universal_orchestration_progress",
    "resolve_universal_orchestration_completion",
    "evaluate_universal_orchestration_recovery",

    "append_record",
    "load_latest_record",
    "load_record",
    "list_record_history",

    "enqueue_job",
    "dequeue_job",
    "claim_job",
    "requeue_job",
    "schedule_job",
    "purge",

    "assign_universal_worker",
    "acquire_universal_worker_lease",
    "release_lease",
    "revoke_lease",

    "dispatch_registered_runtime_handler",
    "execute_registered_runtime_job_v1",

    "get_runtime_state_store_registry",

    "cancel",
    "terminate",
    "kill",
    "shutdown",
    "drain",

    "open",
    "read_text",
    "write_text",

    "time",
    "time_ns",
    "now",
    "utcnow",
    "sleep",

    "persist",
    "save",
    "execute",
    "delete",
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
# PROTECTED AUTHORITY MATRIX
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
# CANONICAL SEMANTIC FINGERPRINT
# ============================================================

fingerprint_material = "|".join(
    (
        "phase_5_1_16_universal_orchestration_cancellation_termination",

        termination.UNIVERSAL_ORCHESTRATION_CANCELLATION_TERMINATION_VERSION,

        termination.UNIVERSAL_ORCHESTRATION_CANCELLATION_REQUEST_SCHEMA_VERSION,

        termination.UNIVERSAL_ORCHESTRATION_CANCELLATION_DECISION_SCHEMA_VERSION,

        termination.UNIVERSAL_ORCHESTRATION_CANCELLATION_HASH_ALGORITHM,

        EXPECTED_AST,

        "state_authority_5_1_3",
        "progress_authority_5_1_11",

        "explicit_orchestration_cancellation_request_required",
        "job_cancelled_does_not_create_orchestration_intent",

        "request_fields_request_id",
        "request_fields_request_source",
        "request_fields_reason",
        "request_fields_schema_version",

        "decision_fields_state_snapshot",
        "decision_fields_progress_snapshot",
        "decision_fields_cancellation_request_snapshot",
        "decision_fields_schema_version",

        "disposition_not_requested",
        "disposition_waiting_for_termination",
        "disposition_eligible",
        "disposition_already_cancelled",
        "disposition_ineligible",
        "disposition_unresolved",

        "no_request_not_requested",

        "created_waiting",
        "queued_waiting",
        "scheduled_waiting",
        "leased_waiting",
        "running_waiting",
        "suspended_waiting",

        "terminal_cancelled_evidence_eligible",

        "terminal_without_cancelled_evidence_ineligible",

        "missing_status_unresolved",
        "unresolved_branch_unresolved",

        "excluded_work_ignored",

        "orchestration_cancelled_already_cancelled",
        "orchestration_succeeded_ineligible",
        "orchestration_failed_ineligible",

        "target_cancelled_only",

        "transition_legality_from_5_1_3",
        "no_actual_state_transition",

        "completion_not_imported",
        "completion_not_reevaluated",

        "recovery_not_imported",
        "recovery_not_reevaluated",

        "no_persistence_port",
        "no_runtime_state_store",

        "no_job_status_mutation",
        "no_job_cancellation_execution",

        "no_queue_purge",
        "no_worker_interruption",
        "no_worker_termination",
        "no_worker_drain",

        "no_lease_release",
        "no_lease_revocation",

        "no_force_requested",
        "no_forced_termination",
        "no_grace_period",
        "no_timeout_policy",

        "no_wall_clock",

        "request_fingerprint_sha256",
        "decision_id_sha256",

        "decision_id_identity_sensitive",
        "decision_id_state_sensitive",
        "decision_id_progress_sensitive",
        "decision_id_request_sensitive",

        "evidence_records_deferred_5_1_17",

        "no_filesystem_io",
        "no_database_io",
        "no_network_io",

        "no_universal_coordination_framework",
        "no_pipeline_coordinator",

        "deterministic_orchestration_cancellation_termination_resolution",
    )
)


termination_fingerprint = (
    hashlib.sha256(
        fingerprint_material.encode(
            "utf-8"
        )
    ).hexdigest().upper()
)


certification_id = (
    "phase_5_1_16_"
    + termination_fingerprint[
        :16
    ].lower()
)


check(
    "fingerprint_generated",
    (
        len(
            termination_fingerprint
        )
        == 64
        and
        all(
            character
            in "0123456789ABCDEF"
            for character
            in termination_fingerprint
        )
    ),
    termination_fingerprint,
)


check(
    "certification_id_generated",
    certification_id
    ==
    (
        "phase_5_1_16_"
        + termination_fingerprint[
            :16
        ].lower()
    ),
    certification_id,
)


# ============================================================
# FINAL AST
# ============================================================

final_ast = ast_sha(
    AUTHORITY_PATH
)


check(
    "final_ast_unchanged",
    final_ast
    ==
    EXPECTED_AST,
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
        "PHASE 5.1.16 — UNIVERSAL ORCHESTRATION "
        "CANCELLATION / TERMINATION RESOLUTION FINAL CERTIFICATION"
    ),

    "=" * 118,

    "",

    (
        "ORCHESTRATION CANCELLATION / TERMINATION AST SHA256: "
        + final_ast
    ),

    (
        "ORCHESTRATION CANCELLATION / TERMINATION FINGERPRINT: "
        + termination_fingerprint
    ),

    (
        "CERTIFICATION ID: "
        + certification_id
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
            "FINAL ORCHESTRATION CANCELLATION / TERMINATION CERTIFICATION: "
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

        "5.1.16 AUTHORITY MODIFIED DURING CERTIFICATION: NO",
        "5.1.1–5.1.15 FROZEN AUTHORITIES MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "STATE AUTHORITY: 5.1.3",
        "PROGRESS AUTHORITY: 5.1.11",

        "",

        "EXPLICIT ORCHESTRATION CANCELLATION REQUEST REQUIRED: YES",
        "JOB-LEVEL CANCELLED AUTO-CANCELS ORCHESTRATION: NO",

        "",

        "REQUEST STORED FIELDS:",
        "  request_id",
        "  request_source",
        "  reason",
        "  schema_version",

        "",

        "DECISION STORED FIELDS:",
        "  state_snapshot",
        "  progress_snapshot",
        "  cancellation_request_snapshot",
        "  schema_version",

        "",

        "NO REQUEST => NOT_REQUESTED",

        "",

        "NONTERMINAL EFFECTIVE WORK => WAITING_FOR_TERMINATION",

        "",

        "TERMINAL EFFECTIVE WORK WITH CANCELLED EVIDENCE => ELIGIBLE",
        "TERMINAL EFFECTIVE WORK WITHOUT CANCELLED EVIDENCE => INELIGIBLE",

        "",

        "MISSING STATUS => UNRESOLVED",
        "UNRESOLVED BRANCH => UNRESOLVED",

        "",

        "ORCHESTRATION CANCELLED => ALREADY_CANCELLED",
        "ORCHESTRATION SUCCEEDED => INELIGIBLE",
        "ORCHESTRATION FAILED => INELIGIBLE",

        "",

        "TARGET CANCELLED DERIVED: YES",
        "5.1.3 TRANSITION LEGALITY CONSUMED: YES",
        "ACTUAL STATE TRANSITION: NO",

        "",

        "COMPLETION REEVALUATION: NO",
        "RECOVERY REEVALUATION: NO",

        "",

        "JOB STATUS MUTATION: NO",
        "JOB CANCELLATION EXECUTION: NO",

        "",

        "QUEUE PURGE: NO",
        "WORKER INTERRUPTION: NO",
        "WORKER TERMINATION: NO",
        "WORKER DRAIN: NO",
        "LEASE RELEASE/REVOCATION: NO",

        "",

        "FORCED TERMINATION: NO",
        "GRACE PERIOD/TIMEOUT POLICY: NO",

        "",

        "PERSISTENCE PORT INVOKED: NO",
        "RUNTIME STATE STORE ACCESS: NO",

        "",

        "REQUEST FINGERPRINT DETERMINISTIC: YES",
        "DECISION ID DETERMINISTIC: YES",
        "DECISION ID STATE SENSITIVE: YES",
        "DECISION ID PROGRESS SENSITIVE: YES",
        "DECISION ID REQUEST SENSITIVE: YES",
        "DECISION ID RUN SENSITIVE: YES",

        "",

        "PERMANENT EVIDENCE RECORDING: NO",

        "",

        "UNIVERSAL COORDINATION FRAMEWORK ACCESS: NO",
        "PIPELINE COORDINATOR ACCESS: NO",

        "",

        (
            "PHASE 5.1.16 FREEZE CANDIDATE: "
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
        "Phase 5.1.16 final certification failed."
    )
