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

HANDOFF_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_orchestration"
    / "runtime_handoff.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_1_7_runtime_handoff_regression.txt"
)

EXPECTED_HANDOFF_AST = (
    "6878FC6F0F2EF071B11A93D793A0CC80B2C91B676C6B6735A78237D8C7D6CB73"
)


PROTECTED = {
    "5.1.1_orchestration_contract": (
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

    "worker_registration": (
        ROOT / "backend/server/runtime/universal_worker/registration.py",
        "00F0D6E620E24A7433C880B722E023AF3C2121563F8E18DFA9979E0F06A36D64",
    ),

    "worker_discovery": (
        ROOT / "backend/server/runtime/universal_worker/discovery.py",
        "DFCAB9080982C8D5E099A40C903F7B4140B0860053DB73CB77B30B966788A228",
    ),

    "worker_assignment": (
        ROOT / "backend/server/runtime/universal_worker/assignment.py",
        "609D3077B84C1791262F8ACA6BD268FD40436DF7775ACB3E9E726BCFC9715F56",
    ),

    "worker_leasing": (
        ROOT / "backend/server/runtime/universal_worker/leasing.py",
        "413B8081D7802211D64B7B811299F9A8A2C54DBAEAB0FC537B1603A3BE397932",
    ),

    "worker_health": (
        ROOT / "backend/server/runtime/universal_worker/health.py",
        "DCC43E77BDC12188DFD15044DA4DA41022B3CEF40F9C4ED06371EE66AA4E5F65",
    ),

    "worker_recovery": (
        ROOT / "backend/server/runtime/universal_worker/recovery.py",
        "C3EF5DBD81205F0087E05F43F6A67A1E0762930DAAD256F957AABC57296D19A5",
    ),

    "worker_scaling": (
        ROOT / "backend/server/runtime/universal_worker/scaling.py",
        "8EC818E4EF4CA7DBCADCFCB93FD99BC80AAD4CE8AEBE1CDE63CCC44FA8488FF6",
    ),

    "worker_shutdown": (
        ROOT / "backend/server/runtime/universal_worker/shutdown.py",
        "DB2197CA791988B01C73CE426ED29891C8BD9FE46DFEC1AC5AE79D1D131C34DD",
    ),

    "worker_pool": (
        ROOT / "backend/server/runtime/universal_worker/pool.py",
        "4BA8E641A88A5BB38F78D2B981216765B3327D639EB3BC78E5294C152E84A308",
    ),

    "worker_heartbeat": (
        ROOT / "backend/server/runtime/universal_worker/heartbeat.py",
        "A58BDEE660CA903453DA6D968A2B02FBFBE3920E9BBE6C64BC75A597DB7C11EE",
    ),

    "worker_stale": (
        ROOT / "backend/server/runtime/universal_worker/stale.py",
        "22105ACBF984E26019080E53939617CE14BDF51BF5A9B149BD39E10B6B87B9DD",
    ),

    "worker_drain": (
        ROOT / "backend/server/runtime/universal_worker/drain.py",
        "629AA6B5D9269B3164A1524F3C176B2EA34CB4952A0D32F5E2EE4A7C6984FA78",
    ),

    "worker_capability": (
        ROOT / "backend/server/runtime/universal_worker/capability.py",
        "200A42478283CDAC92965EAF0DEDFAB3FAB8834F5FB734E3A4874F1EE571C51D",
    ),

    "worker_capacity": (
        ROOT / "backend/server/runtime/universal_worker/capacity.py",
        "92A626B59250333885ABF1D81A0AA00759A47359C3B9D25FCD948915521CBF55",
    ),

    "queue_certification": (
        ROOT / "backend/server/runtime/universal_queue/certification.py",
        "6ED39655147D2B331E02101F5EA23E68CF71447353C0D294E170281AE40C0D4C",
    ),

    "job_contract": (
        ROOT / "backend/server/runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
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

    "orchestration_models": (
        ROOT / "backend/server/orchestration/models.py",
        "5C9FE5E4F84FA1C369CB45F74B0CB12B7E730ADA3C7CBC95B4F50EC75DC5E92D",
    ),

    "orchestration_queue": (
        ROOT / "backend/server/orchestration/queue.py",
        "76F8F7E66578E2B8A4A1FF3BB420B6340A7A1D1D661EB66B7C21987CF3845A97",
    ),

    "orchestration_service": (
        ROOT / "backend/server/orchestration/service.py",
        "4C31CFC6FFDC9AFA8EA6AD8F43ADBC117F8A6D0193ABF045DBFBA39D6EB799BA",
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

if not HANDOFF_PATH.exists():

    raise SystemExit(
        "5.1.7 Runtime Handoff authority missing."
    )


initial_ast = ast_sha(
    HANDOFF_PATH
)


if initial_ast != EXPECTED_HANDOFF_AST:

    raise SystemExit(
        (
            "5.1.7 Runtime Handoff AST changed before "
            "adversarial regression.\n"
            "EXPECTED: "
            + EXPECTED_HANDOFF_AST
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
            (
                "Protected authority changed before "
                "5.1.7 adversarial regression: "
                + name
                + "\nEXPECTED: "
                + expected
                + "\nACTUAL:   "
                + actual
            )
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

dependencies = importlib.import_module(
    "backend.server.runtime.universal_orchestration.dependency_resolution"
)

planning = importlib.import_module(
    "backend.server.runtime.universal_orchestration.execution_planning"
)

readiness = importlib.import_module(
    "backend.server.runtime.universal_orchestration.stage_readiness"
)


module_name = (
    "backend.server.runtime."
    "universal_orchestration.runtime_handoff"
)

sys.modules.pop(
    module_name,
    None,
)

handoff = importlib.import_module(
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


# ============================================================
# FIXTURES
# ============================================================

FIXED_CREATED_AT = (
    "2026-05-21T03:49:30.579317+00:00"
)


def make_job(
    *,
    job_id,
    dependencies=(),
    status=jobs.UniversalJobStatus.CREATED,
    priority=jobs.UniversalJobPriority.NORMAL,
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
        status=status,
        priority=priority,
        created_at=FIXED_CREATED_AT,
    )


def make_context(
    *,
    run_id,
    target_status=jobs.UniversalJobStatus.CREATED,
    target_priority=jobs.UniversalJobPriority.NORMAL,
    dependency_statuses=None,
    dependency_ids=(
        "a",
        "b",
        "c",
    ),
):

    target = make_job(
        job_id="target",
        dependencies=dependency_ids,
        status=target_status,
        priority=target_priority,
    )

    dependency_jobs = tuple(
        make_job(
            job_id=dependency_job_id,
        )
        for dependency_job_id
        in dependency_ids
    )

    all_jobs = (
        dependency_jobs
        + (
            target,
        )
    )

    contract = (
        contracts
        .create_universal_runtime_orchestration_contract(
            workspace_id="workspace-a",
            pipeline="pipeline-a",
            job_ids=tuple(
                job.job_id
                for job
                in all_jobs
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

    plan = (
        planning
        .create_universal_orchestration_execution_plan(
            identity=identity,
            jobs=all_jobs,
        )
    )

    resolution = (
        dependencies
        .resolve_universal_orchestration_dependencies(
            identity=identity,
            target_job=target,
            dependency_statuses=dependency_statuses,
        )
    )

    stage_readiness = (
        readiness
        .evaluate_universal_orchestration_stage_readiness(
            dependency_resolution=resolution,
            execution_plan=plan,
        )
    )

    decision = (
        handoff
        .evaluate_universal_orchestration_runtime_handoff(
            stage_readiness=stage_readiness,
        )
    )

    return (
        target,
        identity,
        plan,
        resolution,
        stage_readiness,
        decision,
    )


# ============================================================
# 1 — AUTHORITY / PUBLIC API
# ============================================================

check(
    "handoff_ast_initial",
    ast_sha(
        HANDOFF_PATH
    )
    == EXPECTED_HANDOFF_AST,
)

check(
    "version_exact",
    handoff.UNIVERSAL_ORCHESTRATION_RUNTIME_HANDOFF_VERSION
    == "universal_orchestration_runtime_handoff_v5.1.7",
)

check(
    "schema_exact",
    handoff.UNIVERSAL_ORCHESTRATION_RUNTIME_HANDOFF_SCHEMA_VERSION
    == "universal_orchestration_runtime_handoff_schema_v1",
)


expected_all = (
    "UNIVERSAL_ORCHESTRATION_RUNTIME_HANDOFF_VERSION",
    "UNIVERSAL_ORCHESTRATION_RUNTIME_HANDOFF_SCHEMA_VERSION",
    "UniversalOrchestrationRuntimeHandoffError",
    "UniversalOrchestrationRuntimeHandoffClassification",
    "UniversalOrchestrationRuntimeHandoffReason",
    "HANDOFF_ENTRY_UNIVERSAL_JOB_STATUSES",
    "ALREADY_IN_RUNTIME_UNIVERSAL_JOB_STATUSES",
    "TERMINAL_HANDOFF_INELIGIBLE_UNIVERSAL_JOB_STATUSES",
    "UniversalOrchestrationRuntimeHandoff",
    "evaluate_universal_orchestration_runtime_handoff",
    "explain_universal_orchestration_runtime_handoff_v1",
)


check(
    "api_surface_exact",
    tuple(
        handoff.__all__
    )
    == expected_all,
    handoff.__all__,
)


check(
    "classification_values_exact",
    tuple(
        item.value
        for item
        in handoff.UniversalOrchestrationRuntimeHandoffClassification
    )
    == (
        "eligible",
        "deferred",
        "ineligible",
    ),
)


check(
    "reason_values_exact",
    tuple(
        item.value
        for item
        in handoff.UniversalOrchestrationRuntimeHandoffReason
    )
    == (
        "ready_for_runtime_handoff",
        "readiness_waiting",
        "readiness_blocked",
        "target_already_in_runtime",
        "target_suspended",
        "target_terminal",
    ),
)


# ============================================================
# 2 — STATUS PARTITION EXACT / COMPLETE / IMMUTABLE
# ============================================================

check(
    "entry_status_set_frozenset",
    isinstance(
        handoff.HANDOFF_ENTRY_UNIVERSAL_JOB_STATUSES,
        frozenset,
    ),
)

check(
    "runtime_status_set_frozenset",
    isinstance(
        handoff.ALREADY_IN_RUNTIME_UNIVERSAL_JOB_STATUSES,
        frozenset,
    ),
)

check(
    "terminal_status_set_frozenset",
    isinstance(
        handoff.TERMINAL_HANDOFF_INELIGIBLE_UNIVERSAL_JOB_STATUSES,
        frozenset,
    ),
)

check(
    "entry_status_exact",
    handoff.HANDOFF_ENTRY_UNIVERSAL_JOB_STATUSES
    == frozenset(
        {
            jobs.UniversalJobStatus.CREATED,
        }
    ),
)

check(
    "runtime_status_exact",
    handoff.ALREADY_IN_RUNTIME_UNIVERSAL_JOB_STATUSES
    == frozenset(
        {
            jobs.UniversalJobStatus.QUEUED,
            jobs.UniversalJobStatus.SCHEDULED,
            jobs.UniversalJobStatus.LEASED,
            jobs.UniversalJobStatus.RUNNING,
        }
    ),
)

check(
    "terminal_status_exact",
    handoff.TERMINAL_HANDOFF_INELIGIBLE_UNIVERSAL_JOB_STATUSES
    == frozenset(
        {
            jobs.UniversalJobStatus.SUCCEEDED,
            jobs.UniversalJobStatus.FAILED,
            jobs.UniversalJobStatus.CANCELLED,
            jobs.UniversalJobStatus.DEAD_LETTER,
            jobs.UniversalJobStatus.EXPIRED,
        }
    ),
)


all_partitioned = (
    handoff.HANDOFF_ENTRY_UNIVERSAL_JOB_STATUSES
    |
    handoff.ALREADY_IN_RUNTIME_UNIVERSAL_JOB_STATUSES
    |
    handoff.TERMINAL_HANDOFF_INELIGIBLE_UNIVERSAL_JOB_STATUSES
    |
    frozenset(
        {
            jobs.UniversalJobStatus.SUSPENDED,
        }
    )
)


check(
    "status_partition_complete",
    all_partitioned
    == frozenset(
        jobs.UniversalJobStatus
    ),
)

check(
    "entry_runtime_disjoint",
    not (
        handoff.HANDOFF_ENTRY_UNIVERSAL_JOB_STATUSES
        &
        handoff.ALREADY_IN_RUNTIME_UNIVERSAL_JOB_STATUSES
    ),
)

check(
    "entry_terminal_disjoint",
    not (
        handoff.HANDOFF_ENTRY_UNIVERSAL_JOB_STATUSES
        &
        handoff.TERMINAL_HANDOFF_INELIGIBLE_UNIVERSAL_JOB_STATUSES
    ),
)

check(
    "runtime_terminal_disjoint",
    not (
        handoff.ALREADY_IN_RUNTIME_UNIVERSAL_JOB_STATUSES
        &
        handoff.TERMINAL_HANDOFF_INELIGIBLE_UNIVERSAL_JOB_STATUSES
    ),
)


# ============================================================
# 3 — CREATED + READY MATRIX
# ============================================================

_, _, _, resolution, stage, decision = make_context(
    run_id="created-ready",
    target_status=jobs.UniversalJobStatus.CREATED,
    dependency_statuses={
        "a": "succeeded",
        "b": "succeeded",
        "c": "succeeded",
    },
)


check(
    "created_ready_readiness",
    stage.is_ready,
)

check(
    "created_ready_eligible",
    decision.classification
    is handoff.UniversalOrchestrationRuntimeHandoffClassification.ELIGIBLE,
)

check(
    "created_ready_reason",
    decision.reason
    is handoff.UniversalOrchestrationRuntimeHandoffReason.READY_FOR_RUNTIME_HANDOFF,
)

check(
    "created_ready_reason_code",
    decision.reason_code
    == "ready_for_runtime_handoff",
)

check(
    "created_ready_boolean_partition",
    (
        decision.is_eligible
        and
        not decision.is_deferred
        and
        not decision.is_ineligible
    ),
)


# ============================================================
# 4 — CREATED + WAITING FROM EVERY UNRESOLVED STATUS
# ============================================================

for dependency_status in (
    jobs.UniversalJobStatus.CREATED,
    jobs.UniversalJobStatus.QUEUED,
    jobs.UniversalJobStatus.SCHEDULED,
    jobs.UniversalJobStatus.LEASED,
    jobs.UniversalJobStatus.RUNNING,
    jobs.UniversalJobStatus.SUSPENDED,
):

    _, _, _, _, stage, decision = make_context(
        run_id=(
            "created-waiting-"
            + dependency_status.value
        ),
        target_status=jobs.UniversalJobStatus.CREATED,
        dependency_statuses={
            "a": "succeeded",
            "b": dependency_status,
            "c": "succeeded",
        },
    )

    check(
        "created_waiting_readiness_"
        + dependency_status.value,
        stage.is_waiting,
    )

    check(
        "created_waiting_deferred_"
        + dependency_status.value,
        decision.is_deferred,
    )

    check(
        "created_waiting_reason_"
        + dependency_status.value,
        decision.reason_code
        == "readiness_waiting",
    )


# ============================================================
# 5 — CREATED + MISSING → DEFERRED
# ============================================================

_, _, _, _, missing_stage, missing_decision = make_context(
    run_id="created-missing",
    target_status=jobs.UniversalJobStatus.CREATED,
    dependency_statuses={
        "a": "succeeded",
    },
)


check(
    "created_missing_stage_waiting",
    missing_stage.is_waiting,
)

check(
    "created_missing_deferred",
    missing_decision.is_deferred,
)

check(
    "created_missing_reason",
    missing_decision.reason_code
    == "readiness_waiting",
)


# ============================================================
# 6 — CREATED + EVERY TERMINAL DEPENDENCY FAILURE → INELIGIBLE
# ============================================================

for dependency_status in (
    jobs.UniversalJobStatus.FAILED,
    jobs.UniversalJobStatus.CANCELLED,
    jobs.UniversalJobStatus.DEAD_LETTER,
    jobs.UniversalJobStatus.EXPIRED,
):

    _, _, _, _, stage, decision = make_context(
        run_id=(
            "created-blocked-"
            + dependency_status.value
        ),
        target_status=jobs.UniversalJobStatus.CREATED,
        dependency_statuses={
            "a": "succeeded",
            "b": dependency_status,
            "c": "succeeded",
        },
    )

    check(
        "created_blocked_readiness_"
        + dependency_status.value,
        stage.is_blocked,
    )

    check(
        "created_blocked_ineligible_"
        + dependency_status.value,
        decision.is_ineligible,
    )

    check(
        "created_blocked_reason_"
        + dependency_status.value,
        decision.reason_code
        == "readiness_blocked",
    )


# ============================================================
# 7 — ZERO DEPENDENCY CREATED → ELIGIBLE
# ============================================================

_, _, zero_plan, zero_resolution, zero_stage, zero_decision = make_context(
    run_id="zero-dependencies",
    target_status=jobs.UniversalJobStatus.CREATED,
    dependency_ids=(),
    dependency_statuses={},
)


check(
    "zero_dependency_plan_empty",
    zero_plan.dependency_map[
        "target"
    ]
    == (),
)

check(
    "zero_dependency_resolution_satisfied",
    zero_resolution.all_dependencies_satisfied,
)

check(
    "zero_dependency_stage_ready",
    zero_stage.is_ready,
)

check(
    "zero_dependency_handoff_eligible",
    zero_decision.is_eligible,
)

check(
    "zero_dependency_handoff_reason",
    zero_decision.reason_code
    == "ready_for_runtime_handoff",
)


# ============================================================
# 8 — QUEUED / SCHEDULED / LEASED / RUNNING ALWAYS LIFECYCLE-INELIGIBLE
# ============================================================

already_runtime_statuses = (
    jobs.UniversalJobStatus.QUEUED,
    jobs.UniversalJobStatus.SCHEDULED,
    jobs.UniversalJobStatus.LEASED,
    jobs.UniversalJobStatus.RUNNING,
)


readiness_evidence_sets = (
    (
        "ready",
        {
            "a": "succeeded",
            "b": "succeeded",
            "c": "succeeded",
        },
    ),
    (
        "waiting",
        {
            "a": "running",
            "b": "succeeded",
        },
    ),
    (
        "blocked",
        {
            "a": "failed",
            "b": "succeeded",
            "c": "succeeded",
        },
    ),
)


for target_status in already_runtime_statuses:

    for readiness_label, dependency_statuses in readiness_evidence_sets:

        _, _, _, _, stage, decision = make_context(
            run_id=(
                "already-runtime-"
                + target_status.value
                + "-"
                + readiness_label
            ),
            target_status=target_status,
            dependency_statuses=dependency_statuses,
        )

        check(
            (
                "already_runtime_ineligible_"
                + target_status.value
                + "_"
                + readiness_label
            ),
            decision.is_ineligible,
        )

        check(
            (
                "already_runtime_reason_"
                + target_status.value
                + "_"
                + readiness_label
            ),
            decision.reason_code
            == "target_already_in_runtime",
        )


# ============================================================
# 9 — SUSPENDED ALWAYS DEFERRED, REGARDLESS OF READINESS
# ============================================================

for readiness_label, dependency_statuses in readiness_evidence_sets:

    _, _, _, _, stage, decision = make_context(
        run_id=(
            "suspended-"
            + readiness_label
        ),
        target_status=jobs.UniversalJobStatus.SUSPENDED,
        dependency_statuses=dependency_statuses,
    )

    check(
        "suspended_deferred_"
        + readiness_label,
        decision.is_deferred,
    )

    check(
        "suspended_reason_"
        + readiness_label,
        decision.reason_code
        == "target_suspended",
    )


# ============================================================
# 10 — TERMINAL TARGET ALWAYS INELIGIBLE, REGARDLESS OF READINESS
# ============================================================

terminal_target_statuses = (
    jobs.UniversalJobStatus.SUCCEEDED,
    jobs.UniversalJobStatus.FAILED,
    jobs.UniversalJobStatus.CANCELLED,
    jobs.UniversalJobStatus.DEAD_LETTER,
    jobs.UniversalJobStatus.EXPIRED,
)


for target_status in terminal_target_statuses:

    for readiness_label, dependency_statuses in readiness_evidence_sets:

        _, _, _, _, stage, decision = make_context(
            run_id=(
                "terminal-target-"
                + target_status.value
                + "-"
                + readiness_label
            ),
            target_status=target_status,
            dependency_statuses=dependency_statuses,
        )

        check(
            (
                "terminal_target_ineligible_"
                + target_status.value
                + "_"
                + readiness_label
            ),
            decision.is_ineligible,
        )

        check(
            (
                "terminal_target_reason_"
                + target_status.value
                + "_"
                + readiness_label
            ),
            decision.reason_code
            == "target_terminal",
        )


# ============================================================
# 11 — LIFECYCLE PRECEDENCE OVER 5.1.6 CLASSIFICATION
# ============================================================

_, _, _, _, queued_blocked_stage, queued_blocked_decision = make_context(
    run_id="queued-blocked-precedence",
    target_status=jobs.UniversalJobStatus.QUEUED,
    dependency_statuses={
        "a": "failed",
    },
)


check(
    "queued_blocked_stage_is_blocked",
    queued_blocked_stage.is_blocked,
)

check(
    "queued_blocked_handoff_reason_is_lifecycle",
    queued_blocked_decision.reason_code
    == "target_already_in_runtime",
)


_, _, _, _, suspended_blocked_stage, suspended_blocked_decision = make_context(
    run_id="suspended-blocked-precedence",
    target_status=jobs.UniversalJobStatus.SUSPENDED,
    dependency_statuses={
        "a": "failed",
    },
)


check(
    "suspended_blocked_stage_is_blocked",
    suspended_blocked_stage.is_blocked,
)

check(
    "suspended_blocked_handoff_remains_deferred",
    suspended_blocked_decision.is_deferred,
)

check(
    "suspended_blocked_handoff_reason_is_suspended",
    suspended_blocked_decision.reason_code
    == "target_suspended",
)


_, _, _, _, failed_ready_stage, failed_ready_decision = make_context(
    run_id="failed-ready-precedence",
    target_status=jobs.UniversalJobStatus.FAILED,
    dependency_statuses={
        "a": "succeeded",
        "b": "succeeded",
        "c": "succeeded",
    },
)


check(
    "failed_ready_stage_is_ready",
    failed_ready_stage.is_ready,
)

check(
    "failed_ready_handoff_terminal_ineligible",
    failed_ready_decision.is_ineligible,
)

check(
    "failed_ready_handoff_reason_terminal",
    failed_ready_decision.reason_code
    == "target_terminal",
)


# ============================================================
# 12 — PRIORITY MUST NOT CHANGE HANDOFF
# ============================================================

for priority in (
    jobs.UniversalJobPriority.CRITICAL,
    jobs.UniversalJobPriority.HIGH,
    jobs.UniversalJobPriority.NORMAL,
    jobs.UniversalJobPriority.LOW,
    jobs.UniversalJobPriority.BACKGROUND,
):

    _, _, _, _, _, decision = make_context(
        run_id=(
            "priority-"
            + str(
                priority.value
            )
        ),
        target_status=jobs.UniversalJobStatus.CREATED,
        target_priority=priority,
        dependency_statuses={
            "a": "succeeded",
            "b": "succeeded",
            "c": "succeeded",
        },
    )

    check(
        (
            "priority_does_not_change_eligibility_"
            + str(
                priority.value
            )
        ),
        decision.is_eligible,
    )


# ============================================================
# 13 — DERIVED IDENTITY / JOB / STATUS
# ============================================================

target, identity, plan, resolution, stage, decision = make_context(
    run_id="derived-evidence",
    target_status=jobs.UniversalJobStatus.CREATED,
    dependency_statuses={
        "a": "succeeded",
        "b": "succeeded",
        "c": "succeeded",
    },
)


check(
    "identity_derived",
    decision.identity
    == stage.identity,
)

check(
    "target_job_derived",
    decision.target_job
    == stage.target_job,
)

check(
    "job_id_derived",
    decision.job_id
    == stage.job_id,
)

check(
    "target_status_derived",
    decision.target_status
    is jobs.UniversalJobStatus.CREATED,
)


# ============================================================
# 14 — STORED FIELDS EXACT
# ============================================================

field_names = tuple(
    field.name
    for field in fields(
        handoff.UniversalOrchestrationRuntimeHandoff
    )
)


check(
    "stored_fields_exact",
    field_names
    == (
        "stage_readiness",
        "schema_version",
    ),
    field_names,
)


for forbidden_field in (
    "identity",
    "target_job",
    "job_id",
    "target_status",

    "classification",
    "reason",
    "reason_code",

    "is_eligible",
    "is_deferred",
    "is_ineligible",

    "queue_id",
    "queue_name",
    "queue_priority",

    "worker_id",
    "worker_assignment",
    "worker_health",
    "worker_capacity",
    "worker_capability",

    "lease_id",
    "lease_owner",

    "handler",
    "handler_id",
    "handler_reference",

    "dispatch_result",
    "execution_result",

    "orchestration_state",

    "fan_out_state",
    "fan_in_state",

    "condition_result",

    "created_at",
    "updated_at",

    "metadata",
):

    check(
        "forbidden_stored_field_"
        + forbidden_field,
        forbidden_field
        not in field_names,
    )


# ============================================================
# 15 — IMMUTABILITY
# ============================================================

for field in fields(
    decision
):

    try:

        setattr(
            decision,
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
# 16 — INVALID STAGE READINESS ATTACKS
# ============================================================

invalid_stage_readiness_values = (
    None,
    True,
    False,
    0,
    1,
    1.0,
    "",
    "ready",
    b"ready",
    bytearray(
        b"ready"
    ),
    {},
    [],
    (),
    target,
    identity,
    plan,
    resolution,
    object(),
)


for index, bad_value in enumerate(
    invalid_stage_readiness_values,
    start=1,
):

    try:

        handoff.evaluate_universal_orchestration_runtime_handoff(
            stage_readiness=bad_value,
        )

    except handoff.UniversalOrchestrationRuntimeHandoffError as exc:

        rejected = (
            exc.code
            == "invalid_runtime_handoff_stage_readiness"
        )

    else:

        rejected = False

    check(
        "invalid_stage_readiness_"
        + str(index),
        rejected,
        repr(
            bad_value
        ),
    )


# ============================================================
# 17 — DIRECT CONSTRUCTOR TYPE ATTACKS
# ============================================================

for index, bad_value in enumerate(
    invalid_stage_readiness_values,
    start=1,
):

    try:

        handoff.UniversalOrchestrationRuntimeHandoff(
            stage_readiness=bad_value,
        )

    except handoff.UniversalOrchestrationRuntimeHandoffError as exc:

        rejected = (
            exc.code
            == "invalid_runtime_handoff_stage_readiness"
        )

    else:

        rejected = False

    check(
        "direct_constructor_invalid_readiness_"
        + str(index),
        rejected,
    )


# ============================================================
# 18 — SCHEMA FORGERY
# ============================================================

for bad_schema in (
    "",
    " ",
    "v1",
    "schema-v1",
    "wrong",
    "universal_orchestration_runtime_handoff_schema_v2",
    None,
    True,
    1,
):

    try:

        handoff.UniversalOrchestrationRuntimeHandoff(
            stage_readiness=stage,
            schema_version=bad_schema,
        )

    except handoff.UniversalOrchestrationRuntimeHandoffError as exc:

        rejected = (
            exc.code
            == "invalid_runtime_handoff_schema_version"
        )

    else:

        rejected = False

    check(
        "schema_forgery_"
        + repr(
            bad_schema
        ),
        rejected,
    )


# ============================================================
# 19 — REPEATED EVALUATION DETERMINISTIC
# ============================================================

repeat_one = (
    handoff
    .evaluate_universal_orchestration_runtime_handoff(
        stage_readiness=stage,
    )
)

repeat_two = (
    handoff
    .evaluate_universal_orchestration_runtime_handoff(
        stage_readiness=stage,
    )
)


check(
    "repeat_objects_equal",
    repeat_one
    == repeat_two,
)

check(
    "repeat_classification_equal",
    repeat_one.classification
    is repeat_two.classification,
)

check(
    "repeat_reason_equal",
    repeat_one.reason
    is repeat_two.reason,
)

check(
    "repeat_reason_code_equal",
    repeat_one.reason_code
    == repeat_two.reason_code,
)


# ============================================================
# 20 — STAGE READINESS MUST REMAIN UNCHANGED
# ============================================================

stage_before = (
    stage.classification,
    stage.reason_code,
    stage.job_id,
    stage.target_job,
    stage.schema_version,
)


_ = (
    handoff
    .evaluate_universal_orchestration_runtime_handoff(
        stage_readiness=stage,
    )
)


stage_after = (
    stage.classification,
    stage.reason_code,
    stage.job_id,
    stage.target_job,
    stage.schema_version,
)


check(
    "stage_readiness_not_mutated",
    stage_before
    == stage_after,
)


# ============================================================
# 21 — TARGET UNIVERSAL JOB MUST REMAIN UNCHANGED
# ============================================================

job_before = (
    target.status,
    target.priority,
    target.job_id,
    target.dependency_job_ids,
)


_ = (
    handoff
    .evaluate_universal_orchestration_runtime_handoff(
        stage_readiness=stage,
    )
)


job_after = (
    target.status,
    target.priority,
    target.job_id,
    target.dependency_job_ids,
)


check(
    "target_job_not_mutated",
    job_before
    == job_after,
)


# ============================================================
# 22 — EXPLANATION CONTRACT
# ============================================================

explanation = (
    handoff
    .explain_universal_orchestration_runtime_handoff_v1()
)


check(
    "explanation_mappingproxy",
    isinstance(
        explanation,
        MappingProxyType,
    ),
)

check(
    "explanation_phase",
    explanation.get(
        "phase"
    )
    == "5.1.7",
)

check(
    "explanation_component",
    explanation.get(
        "component"
    )
    == "Universal Orchestration Runtime Handoff Management",
)

check(
    "explanation_version",
    explanation.get(
        "version"
    )
    == handoff.UNIVERSAL_ORCHESTRATION_RUNTIME_HANDOFF_VERSION,
)

check(
    "explanation_schema",
    explanation.get(
        "schema_version"
    )
    == handoff.UNIVERSAL_ORCHESTRATION_RUNTIME_HANDOFF_SCHEMA_VERSION,
)

check(
    "explanation_stored_fields",
    explanation.get(
        "stored_fields"
    )
    == (
        "stage_readiness",
        "schema_version",
    ),
)

check(
    "explanation_classifications",
    explanation.get(
        "classifications"
    )
    == (
        "eligible",
        "deferred",
        "ineligible",
    ),
)

check(
    "explanation_created_ready_rule",
    (
        "CREATED"
        in explanation.get(
            "eligible_rule",
            ""
        )
        and
        "READY"
        in explanation.get(
            "eligible_rule",
            ""
        )
    ),
)

check(
    "explanation_waiting_rule",
    (
        "WAITING"
        in explanation.get(
            "waiting_rule",
            ""
        )
        and
        "DEFERRED"
        in explanation.get(
            "waiting_rule",
            ""
        )
    ),
)

check(
    "explanation_blocked_rule",
    (
        "BLOCKED"
        in explanation.get(
            "blocked_rule",
            ""
        )
        and
        "INELIGIBLE"
        in explanation.get(
            "blocked_rule",
            ""
        )
    ),
)

check(
    "explanation_runtime_status_rule",
    (
        "QUEUED"
        in explanation.get(
            "already_runtime_rule",
            ""
        )
        and
        "RUNNING"
        in explanation.get(
            "already_runtime_rule",
            ""
        )
    ),
)

check(
    "explanation_suspended_rule",
    "5.1.12"
    in explanation.get(
        "suspended_rule",
        "",
    ),
)

check(
    "explanation_terminal_rule",
    (
        "SUCCEEDED"
        in explanation.get(
            "terminal_rule",
            ""
        )
        and
        "EXPIRED"
        in explanation.get(
            "terminal_rule",
            ""
        )
    ),
)

check(
    "explanation_readiness_boundary",
    "5.1.6"
    in explanation.get(
        "readiness_boundary",
        "",
    ),
)

check(
    "explanation_runtime_registration_boundary",
    "Runtime Registration"
    in explanation.get(
        "runtime_registration_boundary",
        "",
    ),
)

check(
    "explanation_execution_boundary",
    "Universal Runtime Worker"
    in explanation.get(
        "execution_boundary",
        "",
    ),
)

check(
    "explanation_fan_out_boundary",
    "5.1.8"
    in explanation.get(
        "fan_out_boundary",
        "",
    ),
)

check(
    "explanation_fan_in_boundary",
    "5.1.9"
    in explanation.get(
        "fan_in_boundary",
        "",
    ),
)

check(
    "explanation_condition_boundary",
    "5.1.10"
    in explanation.get(
        "condition_boundary",
        "",
    ),
)

check(
    "explanation_suspension_boundary",
    "5.1.12"
    in explanation.get(
        "suspension_boundary",
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


# ============================================================
# 23 — PROHIBITION MATRIX
# ============================================================

required_prohibitions = (
    "does not mutate UniversalJob.status",
    "does not enqueue jobs",
    "does not schedule jobs",
    "does not dequeue jobs",
    "does not claim jobs",

    "does not assign workers",
    "does not acquire worker leases",

    "does not evaluate worker health",
    "does not evaluate worker capability",
    "does not evaluate worker capacity",

    "does not evaluate queue capacity",
    "does not evaluate backpressure",

    "does not look up runtime handlers",
    "does not register runtime handlers",
    "does not dispatch runtime handlers",
    "does not execute runtime handlers",
    "does not execute jobs",

    "does not transition orchestration state",

    "does not coordinate actual fan-out",
    "does not coordinate actual fan-in",
    "does not evaluate conditional branches",

    "does not access Runtime State Store",
    "does not persist handoff decisions",

    "does not import Universal Coordination Framework",
    "does not invoke pipeline coordinators",

    "does not use job priority",
    "does not use queue priority",
    "does not use created_at",
    "does not use scheduled_at",

    "does not use wall clock",
    "does not perform filesystem I/O",
    "does not perform network I/O",
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
# 24 — IMPORT BOUNDARY
# ============================================================

source = HANDOFF_PATH.read_text(
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

    elif isinstance(
        node,
        ast.Import,
    ):

        for alias in node.names:

            if alias.name.startswith(
                "backend.server"
            ):

                backend_imports.append(
                    alias.name
                )


check(
    "backend_imports_exact",
    backend_imports
    == [
        "backend.server.runtime.universal_jobs.contract",
        "backend.server.runtime.universal_orchestration.stage_readiness",
    ],
    backend_imports,
)


# ============================================================
# 25 — FORBIDDEN IMPORTS
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

    "backend.server.runtime.universal_queue",
    "backend.server.runtime.universal_worker",

    "backend.server.runtime.universal_runtime_registration",
    "backend.server.runtime.universal_runtime_worker_v1",
    "backend.server.runtime.universal_runtime_infrastructure",

    "backend.server.runtime.universal_orchestration.state_model",

    "backend.server.runtime.runtime_state_store",

    "backend.server.orchestration",
    "backend.server.coordination",

    "backend.server.jobs.universal_knowledge_orchestrator",
    "backend.server.pipelines.connect_domain.coordinator",
):

    matches = tuple(
        module
        for module
        in all_imports
        if (
            module
            == forbidden_module
            or
            module.startswith(
                forbidden_module
                + "."
            )
        )
    )

    check(
        "no_forbidden_import_"
        + forbidden_module.replace(
            ".",
            "_"
        ),
        not matches,
        matches,
    )


# ============================================================
# 26 — FORBIDDEN CALLS
# ============================================================

forbidden_calls = {
    "open",
    "read_text",
    "write_text",
    "mkdir",
    "unlink",
    "remove",

    "time",
    "time_ns",
    "now",
    "utcnow",

    "uuid4",
    "uuid5",
    "random",
    "randint",
    "choice",

    "enqueue_job",
    "schedule_job",
    "dequeue_job",
    "claim_job",

    "discover_universal_workers",
    "assign_universal_worker",

    "acquire_universal_worker_lease",
    "renew_universal_worker_lease",
    "release_universal_worker_lease",

    "register_runtime_handler",
    "unregister_runtime_handler",
    "dispatch_registered_runtime_handler",
    "execute_registered_runtime_job_v1",

    "transition_universal_orchestration_state",

    "get_runtime_state_store_registry",
    "register_runtime_state_store",

    "persist",
    "save",
    "dispatch",
    "execute",
}


found_forbidden_calls = []


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

        found_forbidden_calls.append(
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
    not found_forbidden_calls,
    found_forbidden_calls,
)


# ============================================================
# 27 — ONLY TARGET STATUS MAY BE LIFECYCLE INPUT
# ============================================================

attributes = tuple(
    node.attr
    for node in ast.walk(
        tree
    )
    if isinstance(
        node,
        ast.Attribute,
    )
)


check(
    "status_attribute_used",
    "status"
    in attributes,
)

check(
    "priority_attribute_not_used",
    "priority"
    not in attributes,
    attributes,
)

check(
    "created_at_attribute_not_used",
    "created_at"
    not in attributes,
)

check(
    "scheduled_at_attribute_not_used",
    "scheduled_at"
    not in attributes,
)

check(
    "attempt_count_attribute_not_used",
    "attempt_count"
    not in attributes,
)

check(
    "maximum_attempts_attribute_not_used",
    "maximum_attempts"
    not in attributes,
)

check(
    "lease_owner_attribute_not_used",
    "lease_owner"
    not in attributes,
)

check(
    "queue_id_attribute_not_used",
    "queue_id"
    not in attributes,
)

check(
    "worker_id_attribute_not_used",
    "worker_id"
    not in attributes,
)


# ============================================================
# 28 — NO RESPONSIBILITY BLEED FUNCTIONS
# ============================================================

function_names = tuple(
    node.name.lower()
    for node in ast.walk(
        tree
    )
    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    )
)


for forbidden_token in (
    "enqueue",
    "dequeue",
    "claim",
    "schedule_job",

    "assign_worker",
    "lease_worker",

    "register_handler",
    "lookup_handler",
    "dispatch",
    "execute",

    "transition_state",

    "fan_out",
    "fan_in",
    "branch",

    "persist",
    "save_handoff",

    "worker_capacity",
    "worker_health",
    "worker_capability",
    "queue_capacity",
):

    matches = tuple(
        function_name
        for function_name
        in function_names
        if forbidden_token
        in function_name
    )

    check(
        "no_function_bleed_"
        + forbidden_token,
        not matches,
        matches,
    )


# ============================================================
# 29 — NO HIDDEN STORED AUTHORITIES
# ============================================================

source_lower = source.lower()


for forbidden_symbol in (
    "queue_id:",
    "queue_name:",
    "queue_priority:",

    "worker_id:",
    "worker_assignment:",
    "worker_health:",
    "worker_capacity:",
    "worker_capability:",

    "lease_id:",
    "lease_owner:",

    "handler:",
    "handler_id:",
    "handler_reference:",

    "dispatch_result:",
    "execution_result:",

    "orchestration_state:",

    "fan_out_state:",
    "fan_in_state:",

    "condition_result:",

    "created_at:",
    "updated_at:",

    "metadata:",
):

    check(
        "no_hidden_field_"
        + forbidden_symbol.replace(
            ":",
            ""
        ),
        forbidden_symbol
        not in source_lower,
    )


# ============================================================
# 30 — 5.1.6 MUST BE DIRECT READINESS SOURCE
# ============================================================

check(
    "stage_readiness_direct_input",
    (
        "UniversalOrchestrationStageReadiness"
        in source
    ),
)

check(
    "readiness_classification_direct_input",
    (
        "UniversalOrchestrationStageReadinessClassification"
        in source
    ),
)


# ============================================================
# 31 — NO DIRECT DEPENDENCY RECOMPUTATION
# ============================================================

check(
    "no_dependency_resolution_import",
    not any(
        module
        == "backend.server.runtime.universal_orchestration.dependency_resolution"
        for module
        in all_imports
    ),
)

check(
    "no_execution_planning_import",
    not any(
        module
        == "backend.server.runtime.universal_orchestration.execution_planning"
        for module
        in all_imports
    ),
)


# ============================================================
# 32 — PROTECTED MATRIX
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
# 33 — FINAL AST
# ============================================================

final_ast = ast_sha(
    HANDOFF_PATH
)


check(
    "handoff_ast_final",
    final_ast
    == EXPECTED_HANDOFF_AST,
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
        "PHASE 5.1.7 — UNIVERSAL ORCHESTRATION "
        "RUNTIME HANDOFF ADVERSARIAL REGRESSION"
    ),
    "=" * 118,
    "",
    (
        "RUNTIME HANDOFF AST SHA256: "
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
            "ADVERSARIAL RUNTIME HANDOFF REGRESSION: "
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
        "RUNTIME HANDOFF AST MODIFIED: NO",
        "5.1.1 ORCHESTRATION CONTRACT MODIFIED: NO",
        "5.1.2 RUN IDENTITY MODIFIED: NO",
        "5.1.3 STATE MODEL MODIFIED: NO",
        "5.1.4 DEPENDENCY RESOLUTION MODIFIED: NO",
        "5.1.5 EXECUTION PLANNING MODIFIED: NO",
        "5.1.6 STAGE READINESS MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",
        "",
        "HANDOFF CLASSIFICATIONS: ELIGIBLE / DEFERRED / INELIGIBLE",
        "",
        "CREATED + READY: ELIGIBLE",
        "CREATED + WAITING: DEFERRED",
        "CREATED + BLOCKED: INELIGIBLE",
        "",
        "QUEUED/SCHEDULED/LEASED/RUNNING: INELIGIBLE — ALREADY IN RUNTIME",
        "SUSPENDED: DEFERRED",
        "SUCCEEDED/FAILED/CANCELLED/DEAD_LETTER/EXPIRED: INELIGIBLE — TERMINAL",
        "",
        "LIFECYCLE CLASSIFICATION PRECEDES READINESS FOR NON-CREATED TARGETS: YES",
        "ZERO-DEPENDENCY CREATED TARGET: ELIGIBLE",
        "",
        "UNIVERSAL JOB STATUS MUTATED: NO",
        "STAGE READINESS MUTATED: NO",
        "",
        "JOB PRIORITY USED: NO",
        "QUEUE PRIORITY USED: NO",
        "CREATED_AT USED: NO",
        "SCHEDULED_AT USED: NO",
        "RETRY/ATTEMPT COUNTS USED: NO",
        "",
        "QUEUE MEMBERSHIP MUTATED: NO",
        "JOB ENQUEUED/SCHEDULED/DEQUEUED/CLAIMED: NO",
        "",
        "WORKER DISCOVERY/ASSIGNMENT: NO",
        "WORKER HEALTH/CAPABILITY/CAPACITY EVALUATED: NO",
        "LEASE ACQUIRED: NO",
        "",
        "RUNTIME HANDLER LOOKED UP: NO",
        "RUNTIME HANDLER REGISTERED: NO",
        "RUNTIME HANDLER DISPATCHED: NO",
        "RUNTIME HANDLER EXECUTED: NO",
        "JOB EXECUTED: NO",
        "",
        "ORCHESTRATION STATE TRANSITIONED: NO",
        "ACTUAL FAN-OUT COORDINATED: NO",
        "ACTUAL FAN-IN COORDINATED: NO",
        "CONDITIONAL BRANCHING EVALUATED: NO",
        "",
        "RUNTIME STATE STORE ACCESSED: NO",
        "HANDOFF DECISION PERSISTED: NO",
        "UNIVERSAL COORDINATION FRAMEWORK ACCESSED: NO",
        "PIPELINE COORDINATORS ACCESSED: NO",
        "",
        "WALL CLOCK USED: NO",
        "FILESYSTEM/NETWORK I/O: NO",
        "",
        (
            "STATUS: REGRESSION PASS "
            "— FINAL CERTIFICATION REQUIRED"
            if passed == total
            else
            "STATUS: REGRESSION FAILED "
            "— PATCH REQUIRED BEFORE CERTIFICATION"
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
        (
            "Phase 5.1.7 Runtime Handoff "
            "adversarial regression failed."
        )
    )
