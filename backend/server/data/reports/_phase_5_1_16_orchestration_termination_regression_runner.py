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

TERMINATION_PATH = (
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
    / "phase_5_1_16_orchestration_termination_regression.txt"
)

EXPECTED_TERMINATION_AST = (
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
        canonical.encode("utf-8")
    ).hexdigest().upper()


if ast_sha(TERMINATION_PATH) != EXPECTED_TERMINATION_AST:
    raise SystemExit(
        "5.1.16 AST changed before adversarial regression."
    )


for name, (path, expected) in PROTECTED.items():
    actual = ast_sha(path)

    if actual != expected:
        raise SystemExit(
            "Protected authority mismatch before regression: "
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


def make_request(
    *,
    request_id="cancel-001",
    request_source="user",
    reason="Requested cancellation.",
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
    decisions=(),
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
                decisions=decisions,
            ),
            cancellation_request_snapshot=request,
        )
    )


request = make_request()


# ============================================================
# 1. AUTHORITY EXACTNESS
# ============================================================

check(
    "ast_initial_exact",
    ast_sha(
        TERMINATION_PATH
    )
    == EXPECTED_TERMINATION_AST,
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
    "hash_exact",
    termination.UNIVERSAL_ORCHESTRATION_CANCELLATION_HASH_ALGORITHM
    ==
    "sha256",
)

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

check(
    "reasons_exact",
    tuple(
        item.value
        for item
        in termination.UniversalOrchestrationCancellationReason
    )
    ==
    (
        "already_cancelled",
        "terminal_succeeded",
        "terminal_failed",
        "no_cancellation_request",
        "missing_status_evidence",
        "unresolved_branch_activity",
        "no_effective_work",
        "nonterminal_effective_work",
        "cancelled_effective_work",
        "terminal_work_without_cancellation_evidence",
    ),
)


# ============================================================
# 2. REQUEST VALIDATION
# ============================================================

bad_text_values = (
    None,
    True,
    False,
    0,
    1,
    1.0,
    "",
    "   ",
    (),
    [],
    {},
    object(),
)


for index, bad in enumerate(
    bad_text_values,
    start=1,
):
    try:
        termination.create_universal_orchestration_cancellation_request(
            request_id=bad,
            request_source="user",
            reason="reason",
        )
    except termination.UniversalOrchestrationCancellationTerminationError as exc:
        rejected = (
            exc.code
            ==
            "invalid_cancellation_request_id"
        )
    else:
        rejected = False

    check(
        "invalid_request_id_" + str(index),
        rejected,
    )


for index, bad in enumerate(
    bad_text_values,
    start=1,
):
    try:
        termination.create_universal_orchestration_cancellation_request(
            request_id="request",
            request_source=bad,
            reason="reason",
        )
    except termination.UniversalOrchestrationCancellationTerminationError as exc:
        rejected = (
            exc.code
            ==
            "invalid_cancellation_request_source"
        )
    else:
        rejected = False

    check(
        "invalid_request_source_" + str(index),
        rejected,
    )


for index, bad in enumerate(
    bad_text_values,
    start=1,
):
    try:
        termination.create_universal_orchestration_cancellation_request(
            request_id="request",
            request_source="user",
            reason=bad,
        )
    except termination.UniversalOrchestrationCancellationTerminationError as exc:
        rejected = (
            exc.code
            ==
            "invalid_cancellation_request_reason"
        )
    else:
        rejected = False

    check(
        "invalid_request_reason_" + str(index),
        rejected,
    )


normalized_request = (
    termination
    .create_universal_orchestration_cancellation_request(
        request_id="  request-1  ",
        request_source="  owner  ",
        reason="  stop orchestration  ",
    )
)


check(
    "request_id_trimmed",
    normalized_request.request_id
    ==
    "request-1",
)

check(
    "request_source_trimmed",
    normalized_request.request_source
    ==
    "owner",
)

check(
    "request_reason_trimmed",
    normalized_request.reason
    ==
    "stop orchestration",
)


# ============================================================
# 3. REQUEST FINGERPRINT
# ============================================================

request_fingerprints = tuple(
    make_request().request_fingerprint
    for _
    in range(20)
)


check(
    "request_fingerprint_deterministic",
    len(
        set(
            request_fingerprints
        )
    )
    == 1,
)

check(
    "request_fingerprint_length",
    len(
        request_fingerprints[0]
    )
    == 64,
    request_fingerprints[0],
)

check(
    "request_fingerprint_upper_hex",
    all(
        character
        in "0123456789ABCDEF"
        for character
        in request_fingerprints[0]
    ),
)


request_id_changed = make_request(
    request_id="cancel-002"
)

source_changed = make_request(
    request_source="system"
)

reason_changed = make_request(
    reason="Different reason."
)


check(
    "request_fingerprint_id_sensitive",
    request.request_fingerprint
    !=
    request_id_changed.request_fingerprint,
)

check(
    "request_fingerprint_source_sensitive",
    request.request_fingerprint
    !=
    source_changed.request_fingerprint,
)

check(
    "request_fingerprint_reason_sensitive",
    request.request_fingerprint
    !=
    reason_changed.request_fingerprint,
)


# ============================================================
# 4. INVALID RESOLUTION INPUTS
# ============================================================

base_plan = make_plan(
    run_id="termination-invalid",
    jobs_tuple=(
        make_job(
            job_id="job-a"
        ),
    ),
)

base_state = make_state(
    plan=base_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
)

base_progress = make_progress(
    plan=base_plan,
    statuses={
        "job-a": "running",
    },
)


for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        1,
        "",
        (),
        [],
        {},
        object(),
    ),
    start=1,
):
    try:
        termination.resolve_universal_orchestration_cancellation_termination(
            state_snapshot=bad,
            progress_snapshot=base_progress,
            cancellation_request_snapshot=request,
        )
    except termination.UniversalOrchestrationCancellationTerminationError as exc:
        rejected = (
            exc.code
            ==
            "invalid_cancellation_state_snapshot"
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
        "",
        (),
        [],
        {},
        object(),
    ),
    start=1,
):
    try:
        termination.resolve_universal_orchestration_cancellation_termination(
            state_snapshot=base_state,
            progress_snapshot=bad,
            cancellation_request_snapshot=request,
        )
    except termination.UniversalOrchestrationCancellationTerminationError as exc:
        rejected = (
            exc.code
            ==
            "invalid_cancellation_progress_snapshot"
        )
    else:
        rejected = False

    check(
        "invalid_progress_snapshot_" + str(index),
        rejected,
    )


for index, bad in enumerate(
    (
        True,
        False,
        0,
        1,
        "",
        (),
        [],
        {},
        object(),
    ),
    start=1,
):
    try:
        termination.resolve_universal_orchestration_cancellation_termination(
            state_snapshot=base_state,
            progress_snapshot=base_progress,
            cancellation_request_snapshot=bad,
        )
    except termination.UniversalOrchestrationCancellationTerminationError as exc:
        rejected = (
            exc.code
            ==
            "invalid_cancellation_request_snapshot"
        )
    else:
        rejected = False

    check(
        "invalid_request_snapshot_" + str(index),
        rejected,
    )


# ============================================================
# 5. CROSS-IDENTITY REJECTION
# ============================================================

other_plan = make_plan(
    run_id="termination-other",
    jobs_tuple=(
        make_job(
            job_id="job-a"
        ),
    ),
)


try:
    termination.resolve_universal_orchestration_cancellation_termination(
        state_snapshot=make_state(
            plan=other_plan,
            state=state_model.UniversalOrchestrationState.ACTIVE,
        ),
        progress_snapshot=base_progress,
        cancellation_request_snapshot=request,
    )
except termination.UniversalOrchestrationCancellationTerminationError as exc:
    cross_identity_rejected = (
        exc.code
        ==
        "cancellation_identity_mismatch"
    )
else:
    cross_identity_rejected = False


check(
    "cross_identity_rejected",
    cross_identity_rejected,
)


# ============================================================
# 6. STORED FIELDS
# ============================================================

request_fields = tuple(
    field.name
    for field
    in fields(
        termination.UniversalOrchestrationCancellationRequestSnapshot
    )
)


check(
    "request_stored_fields_exact",
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
    "decision_stored_fields_exact",
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


for forbidden in (
    "identity",
    "orchestration_state",
    "disposition",
    "target_terminal_state",
    "cancellation_decision_id",
    "created_at",
    "updated_at",
    "timestamp",
    "force_requested",
    "timeout",
    "deadline",
    "grace_period",
    "worker_id",
    "lease_id",
):
    check(
        "forbidden_decision_stored_"
        + forbidden,
        forbidden
        not in decision_fields,
    )


# ============================================================
# 7. NO REQUEST MEANS NOT REQUESTED
# ============================================================

status_values = (
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
)


for status in status_values:

    result = resolve(
        plan=base_plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "job-a": status,
        },
        request=None,
    )

    check(
        "no_request_not_requested_"
        + status,
        result.disposition
        is
        termination.UniversalOrchestrationCancellationDisposition.NOT_REQUESTED,
    )

    check(
        "no_request_reason_"
        + status,
        result.reason
        is
        termination.UniversalOrchestrationCancellationReason.NO_CANCELLATION_REQUEST,
    )

    check(
        "no_request_target_none_"
        + status,
        result.target_terminal_state
        is None,
    )


# ============================================================
# 8. EVERY NONTERMINAL STATUS WAITS
# ============================================================

for status in (
    "created",
    "queued",
    "scheduled",
    "leased",
    "running",
    "suspended",
):

    result = resolve(
        plan=base_plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "job-a": status,
        },
        request=request,
    )

    check(
        "nonterminal_waiting_"
        + status,
        result.disposition
        is
        termination.UniversalOrchestrationCancellationDisposition.WAITING_FOR_TERMINATION,
    )

    check(
        "nonterminal_reason_"
        + status,
        result.reason
        is
        termination.UniversalOrchestrationCancellationReason.NONTERMINAL_EFFECTIVE_WORK,
    )

    check(
        "nonterminal_target_none_"
        + status,
        result.target_terminal_state
        is None,
    )


# ============================================================
# 9. TERMINAL SINGLE-STATUS MATRIX
# ============================================================

terminal_matrix = {
    "succeeded":
        termination.UniversalOrchestrationCancellationDisposition.INELIGIBLE,

    "failed":
        termination.UniversalOrchestrationCancellationDisposition.INELIGIBLE,

    "dead_letter":
        termination.UniversalOrchestrationCancellationDisposition.INELIGIBLE,

    "expired":
        termination.UniversalOrchestrationCancellationDisposition.INELIGIBLE,

    "cancelled":
        termination.UniversalOrchestrationCancellationDisposition.ELIGIBLE,
}


for status, expected in terminal_matrix.items():

    result = resolve(
        plan=base_plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "job-a": status,
        },
        request=request,
    )

    check(
        "terminal_matrix_"
        + status,
        result.disposition
        is expected,
    )


# ============================================================
# 10. MIXED POPULATIONS
# ============================================================

mixed_plan = make_plan(
    run_id="termination-mixed",
    jobs_tuple=(
        make_job(job_id="a"),
        make_job(job_id="b"),
        make_job(job_id="c"),
    ),
)


mixed_cases = (
    (
        "succeeded_cancelled_cancelled",
        {
            "a": "succeeded",
            "b": "cancelled",
            "c": "cancelled",
        },
        termination.UniversalOrchestrationCancellationDisposition.ELIGIBLE,
    ),
    (
        "failed_cancelled_succeeded",
        {
            "a": "failed",
            "b": "cancelled",
            "c": "succeeded",
        },
        termination.UniversalOrchestrationCancellationDisposition.ELIGIBLE,
    ),
    (
        "dead_cancelled_expired",
        {
            "a": "dead_letter",
            "b": "cancelled",
            "c": "expired",
        },
        termination.UniversalOrchestrationCancellationDisposition.ELIGIBLE,
    ),
    (
        "all_succeeded",
        {
            "a": "succeeded",
            "b": "succeeded",
            "c": "succeeded",
        },
        termination.UniversalOrchestrationCancellationDisposition.INELIGIBLE,
    ),
    (
        "success_failed_expired",
        {
            "a": "succeeded",
            "b": "failed",
            "c": "expired",
        },
        termination.UniversalOrchestrationCancellationDisposition.INELIGIBLE,
    ),
)


for name, statuses, expected in mixed_cases:

    result = resolve(
        plan=mixed_plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses=statuses,
        request=request,
    )

    check(
        "mixed_"
        + name,
        result.disposition
        is expected,
    )


# ============================================================
# 11. ANY NONTERMINAL EFFECTIVE WORK BLOCKS ELIGIBILITY
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
            "a": "cancelled",
            "b": nonterminal_status,
            "c": "succeeded",
        },
        request=request,
    )

    check(
        "mixed_nonterminal_waiting_"
        + nonterminal_status,
        result.disposition
        is
        termination.UniversalOrchestrationCancellationDisposition.WAITING_FOR_TERMINATION,
    )


# ============================================================
# 12. MISSING EVIDENCE PRECEDENCE
# ============================================================

missing_result = resolve(
    plan=mixed_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": None,
        "b": "cancelled",
        "c": "running",
    },
    request=request,
)


check(
    "missing_precedence_unresolved",
    missing_result.disposition
    is
    termination.UniversalOrchestrationCancellationDisposition.UNRESOLVED,
)

check(
    "missing_reason_exact",
    missing_result.reason
    is
    termination.UniversalOrchestrationCancellationReason.MISSING_STATUS_EVIDENCE,
)


# ============================================================
# 13. UNRESOLVED BRANCH PRECEDENCE
# ============================================================

branch_plan = make_plan(
    run_id="termination-branch",
    jobs_tuple=(
        make_job(
            job_id="root"
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


unresolved_branch = (
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
        "a": "cancelled",
        "b": "cancelled",
    },
    request=request,
    decisions=(
        unresolved_branch,
    ),
)


check(
    "unresolved_branch_unresolved",
    branch_result.disposition
    is
    termination.UniversalOrchestrationCancellationDisposition.UNRESOLVED,
)

check(
    "unresolved_branch_reason",
    branch_result.reason
    is
    termination.UniversalOrchestrationCancellationReason.UNRESOLVED_BRANCH_ACTIVITY,
)


# ============================================================
# 14. EXCLUDED WORK IS IGNORED
# ============================================================

resolved_branch = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=branch_fanout,
        condition_evidence={
            "a": True,
            "b": False,
        },
    )
)


excluded_running = resolve(
    plan=branch_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "root": "succeeded",
        "a": "cancelled",
        "b": "running",
    },
    request=request,
    decisions=(
        resolved_branch,
    ),
)


check(
    "excluded_running_does_not_block",
    excluded_running.disposition
    is
    termination.UniversalOrchestrationCancellationDisposition.ELIGIBLE,
)


excluded_cancelled = resolve(
    plan=branch_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "root": "succeeded",
        "a": "succeeded",
        "b": "cancelled",
    },
    request=request,
    decisions=(
        resolved_branch,
    ),
)


check(
    "excluded_cancelled_does_not_create_eligibility",
    excluded_cancelled.disposition
    is
    termination.UniversalOrchestrationCancellationDisposition.INELIGIBLE,
)


# ============================================================
# 15. TERMINAL ORCHESTRATION PRECEDENCE
# ============================================================

for status in (
    "created",
    "running",
    "succeeded",
    "failed",
    "cancelled",
    "dead_letter",
    "expired",
    None,
):

    already = resolve(
        plan=base_plan,
        state=state_model.UniversalOrchestrationState.CANCELLED,
        statuses={
            "job-a": status,
        },
        request=None,
    )

    check(
        "terminal_cancelled_override_"
        + (
            "missing"
            if status is None
            else status
        ),
        already.disposition
        is
        termination.UniversalOrchestrationCancellationDisposition.ALREADY_CANCELLED,
    )

    check(
        "terminal_cancelled_target_"
        + (
            "missing"
            if status is None
            else status
        ),
        already.target_terminal_state
        is
        state_model.UniversalOrchestrationState.CANCELLED,
    )


for terminal_state in (
    state_model.UniversalOrchestrationState.SUCCEEDED,
    state_model.UniversalOrchestrationState.FAILED,
):

    for status in (
        "created",
        "running",
        "cancelled",
        None,
    ):

        result = resolve(
            plan=base_plan,
            state=terminal_state,
            statuses={
                "job-a": status,
            },
            request=request,
        )

        check(
            "terminal_ineligible_"
            + terminal_state.value
            + "_"
            + (
                "missing"
                if status is None
                else status
            ),
            result.disposition
            is
            termination.UniversalOrchestrationCancellationDisposition.INELIGIBLE,
        )

        check(
            "terminal_target_none_"
            + terminal_state.value
            + "_"
            + (
                "missing"
                if status is None
                else status
            ),
            result.target_terminal_state
            is None,
        )


# ============================================================
# 16. NONTERMINAL ORCHESTRATION STATES
# ============================================================

for state in (
    state_model.UniversalOrchestrationState.CREATED,
    state_model.UniversalOrchestrationState.ACTIVE,
    state_model.UniversalOrchestrationState.WAITING,
    state_model.UniversalOrchestrationState.SUSPENDED,
    state_model.UniversalOrchestrationState.RECOVERING,
):

    result = resolve(
        plan=base_plan,
        state=state,
        statuses={
            "job-a": "cancelled",
        },
        request=request,
    )

    check(
        "eligible_state_"
        + state.value,
        result.disposition
        is
        termination.UniversalOrchestrationCancellationDisposition.ELIGIBLE,
    )

    expected = (
        state_model
        .can_transition_universal_orchestration_state(
            current_state=state,
            target_state=state_model.UniversalOrchestrationState.CANCELLED,
        )
    )

    check(
        "legality_state_"
        + state.value,
        result.may_transition_to_cancelled
        ==
        expected,
    )


# ============================================================
# 17. TARGET SEMANTICS
# ============================================================

eligible = resolve(
    plan=base_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "job-a": "cancelled",
    },
    request=request,
)


check(
    "eligible_target_cancelled",
    eligible.target_terminal_state
    is
    state_model.UniversalOrchestrationState.CANCELLED,
)

check(
    "eligible_not_already_realized",
    not eligible.is_target_state_already_realized,
)


already = resolve(
    plan=base_plan,
    state=state_model.UniversalOrchestrationState.CANCELLED,
    statuses={
        "job-a": "running",
    },
    request=None,
)


check(
    "already_target_realized",
    already.is_target_state_already_realized,
)

check(
    "already_may_transition_false",
    not already.may_transition_to_cancelled,
)


# ============================================================
# 18. DERIVED BUCKETS
# ============================================================

bucket_plan = make_plan(
    run_id="termination-buckets",
    jobs_tuple=(
        make_job(job_id="a"),
        make_job(job_id="b"),
        make_job(job_id="c"),
        make_job(job_id="d"),
    ),
)


bucket_result = resolve(
    plan=bucket_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "a": "running",
        "b": "cancelled",
        "c": "succeeded",
        "d": "failed",
    },
    request=request,
)


check(
    "bucket_nonterminal_exact",
    bucket_result.nonterminal_effective_job_ids
    ==
    ("a",),
)

check(
    "bucket_cancelled_exact",
    bucket_result.cancelled_effective_job_ids
    ==
    ("b",),
)


# ============================================================
# 19. HELPER CONSISTENCY
# ============================================================

samples = (
    resolve(
        plan=base_plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={"job-a": "running"},
        request=None,
    ),
    resolve(
        plan=base_plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={"job-a": "running"},
        request=request,
    ),
    resolve(
        plan=base_plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={"job-a": "cancelled"},
        request=request,
    ),
    resolve(
        plan=base_plan,
        state=state_model.UniversalOrchestrationState.CANCELLED,
        statuses={"job-a": "running"},
        request=None,
    ),
    resolve(
        plan=base_plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={"job-a": None},
        request=request,
    ),
)


for index, result in enumerate(
    samples,
    start=1,
):

    check(
        "helper_requested_"
        + str(index),
        result.is_cancellation_requested
        ==
        (
            result.cancellation_request_snapshot
            is not None
        ),
    )

    check(
        "helper_waiting_"
        + str(index),
        result.is_waiting_for_termination
        ==
        (
            result.disposition
            is
            termination.UniversalOrchestrationCancellationDisposition.WAITING_FOR_TERMINATION
        ),
    )

    check(
        "helper_eligible_"
        + str(index),
        result.is_eligible
        ==
        (
            result.disposition
            is
            termination.UniversalOrchestrationCancellationDisposition.ELIGIBLE
        ),
    )

    check(
        "helper_already_"
        + str(index),
        result.is_already_cancelled
        ==
        (
            result.disposition
            is
            termination.UniversalOrchestrationCancellationDisposition.ALREADY_CANCELLED
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
            termination.UniversalOrchestrationCancellationDisposition.UNRESOLVED
        ),
    )


# ============================================================
# 20. IMMUTABILITY
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
# 21. DECISION-ID DETERMINISM + SENSITIVITY
# ============================================================

same_ids = tuple(
    resolve(
        plan=base_plan,
        state=state_model.UniversalOrchestrationState.ACTIVE,
        statuses={
            "job-a": "cancelled",
        },
        request=request,
    ).cancellation_decision_id
    for _
    in range(20)
)


check(
    "decision_id_deterministic",
    len(
        set(
            same_ids
        )
    )
    == 1,
)

check(
    "decision_id_length",
    len(
        same_ids[0]
    )
    == 64,
    same_ids[0],
)

check(
    "decision_id_upper_hex",
    all(
        character
        in "0123456789ABCDEF"
        for character
        in same_ids[0]
    ),
)


changed_state_id = resolve(
    plan=base_plan,
    state=state_model.UniversalOrchestrationState.WAITING,
    statuses={
        "job-a": "cancelled",
    },
    request=request,
).cancellation_decision_id


check(
    "decision_id_state_sensitive",
    same_ids[0]
    !=
    changed_state_id,
)


changed_progress_id = resolve(
    plan=base_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "job-a": "running",
    },
    request=request,
).cancellation_decision_id


check(
    "decision_id_progress_sensitive",
    same_ids[0]
    !=
    changed_progress_id,
)


changed_request_id = resolve(
    plan=base_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "job-a": "cancelled",
    },
    request=make_request(
        request_id="cancel-different"
    ),
).cancellation_decision_id


check(
    "decision_id_request_sensitive",
    same_ids[0]
    !=
    changed_request_id,
)


no_request_id = resolve(
    plan=base_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "job-a": "cancelled",
    },
    request=None,
).cancellation_decision_id


check(
    "decision_id_request_presence_sensitive",
    same_ids[0]
    !=
    no_request_id,
)


run_plan = make_plan(
    run_id="termination-run-sensitive",
    jobs_tuple=(
        make_job(
            job_id="job-a"
        ),
    ),
)


changed_run_id = resolve(
    plan=run_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "job-a": "cancelled",
    },
    request=request,
).cancellation_decision_id


check(
    "decision_id_run_sensitive",
    same_ids[0]
    !=
    changed_run_id,
)


# ============================================================
# 22. EXPLANATION CONTRACT
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
# 23. REQUIRED PROHIBITIONS
# ============================================================

required_prohibitions = (
    "does not infer orchestration cancellation from one cancelled job",
    "does not transition orchestration state",
    "does not mutate UniversalJob status",
    "does not cancel jobs",
    "does not enqueue jobs",
    "does not dequeue jobs",
    "does not purge queues",
    "does not interrupt workers",
    "does not terminate workers",
    "does not drain workers",
    "does not release leases",
    "does not revoke leases",
    "does not inspect worker health",
    "does not inspect live lease state",
    "does not implement grace periods",
    "does not implement timeouts",
    "does not implement forced termination",
    "does not use wall clock",
    "does not recompute progress",
    "does not reevaluate completion",
    "does not reevaluate recovery",
    "does not invoke persistence port",
    "does not access Runtime State Store",
    "does not persist cancellation decisions",
    "does not record permanent audit evidence",
    "does not dispatch runtime handlers",
    "does not execute jobs",
    "does not perform filesystem I/O",
    "does not perform database I/O",
    "does not perform network I/O",
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
# 24. IMPORT BOUNDARY
# ============================================================

source = TERMINATION_PATH.read_text(
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
# 25. FORBIDDEN IMPORTS
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
    "backend.server.runtime.runtime_persistence",

    "backend.server.runtime.universal_queue",
    "backend.server.runtime.universal_worker",

    "backend.server.runtime.universal_orchestration.completion_resolution",
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
            imported
            ==
            forbidden_module
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
            "_",
        ),
        not matches,
        matches,
    )


# ============================================================
# 26. FORBIDDEN CALLS
# ============================================================

forbidden_calls = {
    "transition_universal_orchestration_state",
    "track_universal_orchestration_progress",

    "resolve_universal_orchestration_completion",
    "evaluate_universal_orchestration_recovery",
    "evaluate_universal_orchestration_suspension_resume_eligibility",

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

    "open",
    "read_text",
    "write_text",

    "time",
    "time_ns",
    "now",
    "utcnow",
    "sleep",

    "cancel",
    "terminate",
    "kill",
    "shutdown",
    "drain",

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
# 27. FORBIDDEN ATTRIBUTES
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
    "worker_id",
    "lease_id",
    "lease_owner",
    "created_at",
    "updated_at",
    "scheduled_at",
    "deadline",
    "timeout",
    "grace_period",
    "force_requested",
):

    check(
        "forbidden_attribute_absent_"
        + forbidden_attr,
        forbidden_attr
        not in attrs,
    )


# ============================================================
# 28. PROTECTED AUTHORITIES
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
# 29. FINAL AST
# ============================================================

final_ast = ast_sha(
    TERMINATION_PATH
)


check(
    "termination_ast_final",
    final_ast
    ==
    EXPECTED_TERMINATION_AST,
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
        "PHASE 5.1.16 — UNIVERSAL ORCHESTRATION "
        "CANCELLATION / TERMINATION RESOLUTION ADVERSARIAL REGRESSION"
    ),

    "=" * 118,

    "",

    (
        "ORCHESTRATION CANCELLATION / TERMINATION AST SHA256: "
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
            "ADVERSARIAL ORCHESTRATION CANCELLATION / TERMINATION REGRESSION: "
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

        "5.1.16 AUTHORITY MODIFIED DURING REGRESSION: NO",
        "5.1.1–5.1.15 FROZEN AUTHORITIES MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "EXPLICIT ORCHESTRATION CANCELLATION REQUEST REQUIRED: YES",
        "JOB-LEVEL CANCELLED AUTO-CANCELS ORCHESTRATION: NO",

        "",

        "NO REQUEST => NOT_REQUESTED",

        "",

        "NONTERMINAL EFFECTIVE WORK:",
        "  CREATED => WAITING_FOR_TERMINATION",
        "  QUEUED => WAITING_FOR_TERMINATION",
        "  SCHEDULED => WAITING_FOR_TERMINATION",
        "  LEASED => WAITING_FOR_TERMINATION",
        "  RUNNING => WAITING_FOR_TERMINATION",
        "  SUSPENDED => WAITING_FOR_TERMINATION",

        "",

        "TERMINAL EFFECTIVE WORK WITH CANCELLED EVIDENCE => ELIGIBLE",
        "TERMINAL EFFECTIVE WORK WITHOUT CANCELLED EVIDENCE => INELIGIBLE",

        "",

        "MISSING STATUS => UNRESOLVED",
        "UNRESOLVED BRANCH => UNRESOLVED",

        "",

        "EXCLUDED NONTERMINAL WORK BLOCKS CANCELLATION: NO",
        "EXCLUDED CANCELLED WORK CREATES CANCELLATION ELIGIBILITY: NO",

        "",

        "ORCHESTRATION CANCELLED => ALREADY_CANCELLED",
        "ORCHESTRATION SUCCEEDED => INELIGIBLE",
        "ORCHESTRATION FAILED => INELIGIBLE",

        "",

        "TARGET CANCELLED DERIVED: YES",
        "5.1.3 TRANSITION LEGALITY CONSUMED: YES",
        "ACTUAL STATE TRANSITION: NO",

        "",

        "5.1.15 COMPLETION IMPORTED: NO",
        "COMPLETION REEVALUATION: NO",

        "",

        "5.1.13 RECOVERY IMPORTED: NO",
        "RECOVERY REEVALUATION: NO",

        "",

        "PERSISTENCE PORT INVOKED: NO",
        "RUNTIME STATE STORE ACCESS: NO",

        "",

        "JOB STATUS MUTATION: NO",
        "JOB CANCELLATION EXECUTION: NO",
        "QUEUE PURGE: NO",
        "WORKER INTERRUPTION: NO",
        "WORKER TERMINATION: NO",
        "LEASE RELEASE/REVOCATION: NO",
        "FORCED TERMINATION: NO",
        "GRACE PERIOD/TIMEOUT POLICY: NO",

        "",

        "DECISION ID DETERMINISTIC: YES",
        "DECISION ID STATE SENSITIVE: YES",
        "DECISION ID PROGRESS SENSITIVE: YES",
        "DECISION ID REQUEST SENSITIVE: YES",
        "DECISION ID RUN SENSITIVE: YES",

        "",

        "PERMANENT EVIDENCE RECORDING: NO",
        "UNIVERSAL COORDINATION FRAMEWORK ACCESS: NO",
        "PIPELINE COORDINATOR ACCESS: NO",

        "",

        (
            "STATUS: REGRESSION PASS "
            "— FINAL CERTIFICATION REQUIRED"
            if passed == total
            else
            "STATUS: REGRESSION FAILED "
            "— INVESTIGATE BEFORE PATCHING PRODUCTION"
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
        "Phase 5.1.16 adversarial regression failed."
    )
