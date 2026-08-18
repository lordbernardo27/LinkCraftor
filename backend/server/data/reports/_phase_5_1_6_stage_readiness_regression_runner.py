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

READINESS_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_orchestration"
    / "stage_readiness.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_1_6_stage_readiness_regression.txt"
)

EXPECTED_READINESS_AST = (
    "9BF16440AD057B1C6A89DD9AEEDEADBE32F711EAE2D4FCD8730EB796BF603D6D"
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

if not READINESS_PATH.exists():

    raise SystemExit(
        "5.1.6 Stage Readiness authority missing."
    )


initial_ast = ast_sha(
    READINESS_PATH
)


if initial_ast != EXPECTED_READINESS_AST:

    raise SystemExit(
        (
            "5.1.6 Stage Readiness AST changed before "
            "adversarial regression.\n"
            "EXPECTED: "
            + EXPECTED_READINESS_AST
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
                "5.1.6 adversarial regression: "
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


module_name = (
    "backend.server.runtime."
    "universal_orchestration.stage_readiness"
)

sys.modules.pop(
    module_name,
    None,
)

readiness = importlib.import_module(
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
    workspace_id="workspace-a",
    pipeline="pipeline-a",
    status=jobs.UniversalJobStatus.CREATED,
    priority=jobs.UniversalJobPriority.NORMAL,
    parent_job_id=None,
):

    return jobs.UniversalJob(
        job_id=job_id,
        workspace_id=workspace_id,
        pipeline=pipeline,
        stage="stage-a",
        job_type="test_job",
        payload_reference="payload-a",
        dependency_job_ids=tuple(
            dependencies
        ),
        status=status,
        priority=priority,
        parent_job_id=parent_job_id,
        created_at=FIXED_CREATED_AT,
    )


def make_identity(
    *,
    run_id,
    job_ids,
    workspace_id="workspace-a",
    pipeline="pipeline-a",
):

    contract = (
        contracts
        .create_universal_runtime_orchestration_contract(
            workspace_id=workspace_id,
            pipeline=pipeline,
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
        contract,
        identity,
    )


def make_context(
    *,
    run_id="run-a",
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
            job_id=job_id
        )
        for job_id
        in dependency_ids
    )

    all_jobs = (
        dependency_jobs
        + (
            target,
        )
    )

    _, identity = make_identity(
        run_id=run_id,
        job_ids=tuple(
            job.job_id
            for job
            in all_jobs
        ),
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

    result = (
        readiness
        .evaluate_universal_orchestration_stage_readiness(
            dependency_resolution=resolution,
            execution_plan=plan,
        )
    )

    return (
        target,
        identity,
        plan,
        resolution,
        result,
    )


# ============================================================
# 1 — AUTHORITY / API
# ============================================================

check(
    "readiness_ast_initial",
    ast_sha(
        READINESS_PATH
    )
    == EXPECTED_READINESS_AST,
)

check(
    "version_exact",
    readiness.UNIVERSAL_ORCHESTRATION_STAGE_READINESS_VERSION
    == "universal_orchestration_stage_readiness_v5.1.6",
)

check(
    "schema_exact",
    readiness.UNIVERSAL_ORCHESTRATION_STAGE_READINESS_SCHEMA_VERSION
    == "universal_orchestration_stage_readiness_schema_v1",
)


expected_all = (
    "UNIVERSAL_ORCHESTRATION_STAGE_READINESS_VERSION",
    "UNIVERSAL_ORCHESTRATION_STAGE_READINESS_SCHEMA_VERSION",
    "UniversalOrchestrationStageReadinessError",
    "UniversalOrchestrationStageReadinessClassification",
    "UniversalOrchestrationStageReadinessReason",
    "classify_universal_orchestration_stage_readiness",
    "reason_for_universal_orchestration_stage_readiness",
    "UniversalOrchestrationStageReadiness",
    "evaluate_universal_orchestration_stage_readiness",
    "explain_universal_orchestration_stage_readiness_v1",
)


check(
    "api_surface_exact",
    tuple(
        readiness.__all__
    )
    == expected_all,
    readiness.__all__,
)


check(
    "classification_values_exact",
    tuple(
        item.value
        for item
        in readiness.UniversalOrchestrationStageReadinessClassification
    )
    == (
        "ready",
        "waiting",
        "blocked",
    ),
)


check(
    "reason_values_exact",
    tuple(
        item.value
        for item
        in readiness.UniversalOrchestrationStageReadinessReason
    )
    == (
        "all_dependencies_satisfied",
        "dependency_evidence_pending",
        "terminal_dependency_failure",
    ),
)


# ============================================================
# 2 — READY MATRIX
# ============================================================

ready_status_variants = (
    "succeeded",
    jobs.UniversalJobStatus.SUCCEEDED,
)


for index, status_value in enumerate(
    ready_status_variants,
    start=1,
):

    _, _, _, resolution, result = make_context(
        run_id="ready-" + str(index),
        dependency_statuses={
            "a": status_value,
            "b": status_value,
            "c": status_value,
        },
    )

    check(
        "ready_variant_"
        + str(index),
        result.classification
        is readiness.UniversalOrchestrationStageReadinessClassification.READY,
    )

    check(
        "ready_reason_variant_"
        + str(index),
        result.reason
        is readiness.UniversalOrchestrationStageReadinessReason.ALL_DEPENDENCIES_SATISFIED,
    )

    check(
        "ready_reason_code_variant_"
        + str(index),
        result.reason_code
        == "all_dependencies_satisfied",
    )

    check(
        "ready_boolean_variant_"
        + str(index),
        (
            result.is_ready
            and
            not result.is_waiting
            and
            not result.is_blocked
        ),
    )

    check(
        "ready_resolution_clean_"
        + str(index),
        (
            resolution.all_dependencies_satisfied
            and
            not resolution.has_unresolved_dependencies
            and
            not resolution.has_missing_dependency_evidence
            and
            not resolution.has_terminal_dependency_failure
        ),
    )


# ============================================================
# 3 — ZERO DEPENDENCIES
# ============================================================

_, _, zero_plan, zero_resolution, zero_result = make_context(
    run_id="zero-run",
    dependency_ids=(),
    dependency_statuses={},
)


check(
    "zero_dependency_plan",
    zero_plan.dependency_map[
        "target"
    ]
    == (),
)

check(
    "zero_dependencies_satisfied",
    zero_resolution.all_dependencies_satisfied
    is True,
)

check(
    "zero_dependencies_ready",
    zero_result.classification
    is readiness.UniversalOrchestrationStageReadinessClassification.READY,
)

check(
    "zero_dependencies_reason",
    zero_result.reason_code
    == "all_dependencies_satisfied",
)

check(
    "zero_waiting_ids_empty",
    zero_result.waiting_dependency_ids
    == (),
)

check(
    "zero_blocking_ids_empty",
    zero_result.blocking_dependency_ids
    == (),
)


# ============================================================
# 4 — EVERY UNRESOLVED STATUS → WAITING
# ============================================================

unresolved_statuses = (
    jobs.UniversalJobStatus.CREATED,
    jobs.UniversalJobStatus.QUEUED,
    jobs.UniversalJobStatus.SCHEDULED,
    jobs.UniversalJobStatus.LEASED,
    jobs.UniversalJobStatus.RUNNING,
    jobs.UniversalJobStatus.SUSPENDED,
)


for status in unresolved_statuses:

    _, _, _, resolution, result = make_context(
        run_id="unresolved-" + status.value,
        dependency_statuses={
            "a": "succeeded",
            "b": status,
            "c": "succeeded",
        },
    )

    check(
        "unresolved_status_waiting_"
        + status.value,
        result.classification
        is readiness.UniversalOrchestrationStageReadinessClassification.WAITING,
    )

    check(
        "unresolved_reason_"
        + status.value,
        result.reason_code
        == "dependency_evidence_pending",
    )

    check(
        "unresolved_ids_"
        + status.value,
        result.unresolved_dependency_ids
        == (
            "b",
        ),
    )

    check(
        "unresolved_waiting_ids_"
        + status.value,
        result.waiting_dependency_ids
        == (
            "b",
        ),
    )

    check(
        "unresolved_not_blocked_"
        + status.value,
        not result.is_blocked,
    )


# ============================================================
# 5 — EVERY TERMINAL FAILURE STATUS → BLOCKED
# ============================================================

terminal_failure_statuses = (
    jobs.UniversalJobStatus.FAILED,
    jobs.UniversalJobStatus.CANCELLED,
    jobs.UniversalJobStatus.DEAD_LETTER,
    jobs.UniversalJobStatus.EXPIRED,
)


for status in terminal_failure_statuses:

    _, _, _, resolution, result = make_context(
        run_id="terminal-" + status.value,
        dependency_statuses={
            "a": "succeeded",
            "b": status,
            "c": "succeeded",
        },
    )

    check(
        "terminal_status_blocked_"
        + status.value,
        result.classification
        is readiness.UniversalOrchestrationStageReadinessClassification.BLOCKED,
    )

    check(
        "terminal_reason_"
        + status.value,
        result.reason_code
        == "terminal_dependency_failure",
    )

    check(
        "terminal_ids_"
        + status.value,
        result.terminal_unsatisfied_dependency_ids
        == (
            "b",
        ),
    )

    check(
        "blocking_ids_"
        + status.value,
        result.blocking_dependency_ids
        == (
            "b",
        ),
    )

    check(
        "terminal_failure_flag_"
        + status.value,
        resolution.has_terminal_dependency_failure,
    )


# ============================================================
# 6 — MISSING EVIDENCE → WAITING
# ============================================================

_, _, _, missing_resolution, missing_result = make_context(
    run_id="missing-all",
    dependency_statuses=None,
)


check(
    "all_missing_waiting",
    missing_result.is_waiting,
)

check(
    "all_missing_reason",
    missing_result.reason_code
    == "dependency_evidence_pending",
)

check(
    "all_missing_ids",
    missing_result.missing_dependency_ids
    == (
        "a",
        "b",
        "c",
    ),
)

check(
    "all_missing_waiting_ids",
    missing_result.waiting_dependency_ids
    == (
        "a",
        "b",
        "c",
    ),
)

check(
    "all_missing_not_failure",
    not missing_resolution.has_terminal_dependency_failure,
)


# ============================================================
# 7 — PARTIAL MISSING → WAITING
# ============================================================

_, _, _, _, partial_missing_result = make_context(
    run_id="partial-missing",
    dependency_statuses={
        "a": "succeeded",
        "c": "succeeded",
    },
)


check(
    "partial_missing_waiting",
    partial_missing_result.is_waiting,
)

check(
    "partial_missing_ids",
    partial_missing_result.missing_dependency_ids
    == (
        "b",
    ),
)

check(
    "partial_missing_waiting_ids",
    partial_missing_result.waiting_dependency_ids
    == (
        "b",
    ),
)


# ============================================================
# 8 — BLOCKED PRECEDENCE OVER UNRESOLVED
# ============================================================

_, _, _, mixed_resolution, mixed_result = make_context(
    run_id="blocked-over-unresolved",
    dependency_statuses={
        "a": "failed",
        "b": "running",
        "c": "succeeded",
    },
)


check(
    "blocked_over_unresolved_classification",
    mixed_result.is_blocked,
)

check(
    "blocked_over_unresolved_reason",
    mixed_result.reason_code
    == "terminal_dependency_failure",
)

check(
    "blocked_over_unresolved_has_both",
    (
        mixed_resolution.has_terminal_dependency_failure
        and
        mixed_resolution.has_unresolved_dependencies
    ),
)

check(
    "blocked_over_unresolved_blocking_ids",
    mixed_result.blocking_dependency_ids
    == (
        "a",
    ),
)

check(
    "blocked_over_unresolved_waiting_ids_still_derived",
    mixed_result.waiting_dependency_ids
    == (
        "b",
    ),
)


# ============================================================
# 9 — BLOCKED PRECEDENCE OVER MISSING
# ============================================================

_, _, _, blocked_missing_resolution, blocked_missing_result = make_context(
    run_id="blocked-over-missing",
    dependency_statuses={
        "a": "cancelled",
    },
)


check(
    "blocked_over_missing_classification",
    blocked_missing_result.is_blocked,
)

check(
    "blocked_over_missing_has_terminal",
    blocked_missing_resolution.has_terminal_dependency_failure,
)

check(
    "blocked_over_missing_has_missing",
    blocked_missing_resolution.has_missing_dependency_evidence,
)

check(
    "blocked_over_missing_blocking_ids",
    blocked_missing_result.blocking_dependency_ids
    == (
        "a",
    ),
)

check(
    "blocked_over_missing_waiting_ids",
    blocked_missing_result.waiting_dependency_ids
    == (
        "b",
        "c",
    ),
)


# ============================================================
# 10 — WAITING FOR UNRESOLVED + MISSING
# ============================================================

_, _, _, unresolved_missing_resolution, unresolved_missing_result = make_context(
    run_id="unresolved-plus-missing",
    dependency_statuses={
        "a": "running",
        "c": "succeeded",
    },
)


check(
    "unresolved_plus_missing_waiting",
    unresolved_missing_result.is_waiting,
)

check(
    "unresolved_plus_missing_no_terminal",
    not unresolved_missing_resolution.has_terminal_dependency_failure,
)

check(
    "unresolved_plus_missing_unresolved_ids",
    unresolved_missing_result.unresolved_dependency_ids
    == (
        "a",
    ),
)

check(
    "unresolved_plus_missing_missing_ids",
    unresolved_missing_result.missing_dependency_ids
    == (
        "b",
    ),
)

check(
    "unresolved_plus_missing_waiting_ids_canonical",
    unresolved_missing_result.waiting_dependency_ids
    == (
        "a",
        "b",
    ),
)


# ============================================================
# 11 — TARGET JOB STATUS MUST NEVER CHANGE DEPENDENCY READINESS
# ============================================================

all_target_statuses = tuple(
    jobs.UniversalJobStatus
)


for target_status in all_target_statuses:

    _, _, _, _, result = make_context(
        run_id="target-status-" + target_status.value,
        target_status=target_status,
        dependency_statuses={
            "a": "succeeded",
            "b": "succeeded",
            "c": "succeeded",
        },
    )

    check(
        "target_status_ready_"
        + target_status.value,
        result.is_ready,
        target_status.value,
    )


for target_status in all_target_statuses:

    _, _, _, _, result = make_context(
        run_id="target-status-waiting-" + target_status.value,
        target_status=target_status,
        dependency_statuses={
            "a": "succeeded",
            "b": "running",
            "c": "succeeded",
        },
    )

    check(
        "target_status_waiting_"
        + target_status.value,
        result.is_waiting,
        target_status.value,
    )


for target_status in all_target_statuses:

    _, _, _, _, result = make_context(
        run_id="target-status-blocked-" + target_status.value,
        target_status=target_status,
        dependency_statuses={
            "a": "failed",
            "b": "succeeded",
            "c": "succeeded",
        },
    )

    check(
        "target_status_blocked_"
        + target_status.value,
        result.is_blocked,
        target_status.value,
    )


# ============================================================
# 12 — PRIORITY MUST NOT CHANGE READINESS
# ============================================================

for priority in (
    jobs.UniversalJobPriority.CRITICAL,
    jobs.UniversalJobPriority.HIGH,
    jobs.UniversalJobPriority.NORMAL,
    jobs.UniversalJobPriority.LOW,
    jobs.UniversalJobPriority.BACKGROUND,
):

    _, _, _, _, result = make_context(
        run_id="priority-" + str(priority.value),
        target_priority=priority,
        dependency_statuses={
            "a": "succeeded",
            "b": "succeeded",
            "c": "succeeded",
        },
    )

    check(
        "priority_does_not_change_ready_"
        + str(priority.value),
        result.is_ready,
    )


# ============================================================
# 13 — DERIVED ID ORDER MUST FOLLOW CANONICAL DEPENDENCY ORDER
# ============================================================

_, _, _, order_resolution, order_result = make_context(
    run_id="dependency-id-order",
    dependency_ids=(
        "z",
        "a",
        "m",
        "b",
    ),
    dependency_statuses={
        "z": "running",
        "a": "failed",
    },
)


check(
    "canonical_dependency_ids",
    order_resolution.dependency_job_ids
    == (
        "a",
        "b",
        "m",
        "z",
    ),
)

check(
    "canonical_blocking_ids",
    order_result.blocking_dependency_ids
    == (
        "a",
    ),
)

check(
    "canonical_waiting_ids",
    order_result.waiting_dependency_ids
    == (
        "b",
        "m",
        "z",
    ),
)


# ============================================================
# 14 — SAME IDENTITY, DIFFERENT TARGET OBJECT MUST REJECT
# ============================================================

target, identity, plan, resolution, _ = make_context(
    run_id="target-mismatch",
    dependency_statuses={
        "a": "succeeded",
        "b": "succeeded",
        "c": "succeeded",
    },
)


mismatched_target = make_job(
    job_id="target",
    dependencies=(
        "a",
        "b",
        "c",
    ),
    priority=jobs.UniversalJobPriority.CRITICAL,
)


mismatched_resolution = (
    dependencies
    .resolve_universal_orchestration_dependencies(
        identity=identity,
        target_job=mismatched_target,
        dependency_statuses={
            "a": "succeeded",
            "b": "succeeded",
            "c": "succeeded",
        },
    )
)


try:

    readiness.evaluate_universal_orchestration_stage_readiness(
        dependency_resolution=mismatched_resolution,
        execution_plan=plan,
    )

except readiness.UniversalOrchestrationStageReadinessError as exc:

    rejected = (
        exc.code
        == "stage_readiness_target_job_mismatch"
    )

else:

    rejected = False


check(
    "same_id_different_target_object_rejected",
    rejected,
)


# ============================================================
# 15 — DIFFERENT ORCHESTRATION RUN ID MUST REJECT
# ============================================================

_, _, plan_a, resolution_a, _ = make_context(
    run_id="run-one",
    dependency_statuses={
        "a": "succeeded",
        "b": "succeeded",
        "c": "succeeded",
    },
)

_, _, plan_b, _, _ = make_context(
    run_id="run-two",
    dependency_statuses={
        "a": "succeeded",
        "b": "succeeded",
        "c": "succeeded",
    },
)


try:

    readiness.evaluate_universal_orchestration_stage_readiness(
        dependency_resolution=resolution_a,
        execution_plan=plan_b,
    )

except readiness.UniversalOrchestrationStageReadinessError as exc:

    rejected = (
        exc.code
        == "stage_readiness_identity_mismatch"
    )

else:

    rejected = False


check(
    "different_run_identity_rejected",
    rejected,
)


# ============================================================
# 16 — DIFFERENT CONTRACT IDENTITY MUST REJECT
# ============================================================

target_x = make_job(
    job_id="target",
    dependencies=(
        "a",
    ),
)

job_a = make_job(
    job_id="a",
)


_, identity_x = make_identity(
    run_id="same-run-id",
    job_ids=(
        "a",
        "target",
    ),
)

_, identity_y = make_identity(
    run_id="same-run-id",
    job_ids=(
        "target",
    ),
)


resolution_x = (
    dependencies
    .resolve_universal_orchestration_dependencies(
        identity=identity_x,
        target_job=target_x,
        dependency_statuses={
            "a": "succeeded",
        },
    )
)


target_y = make_job(
    job_id="target",
)


plan_y = (
    planning
    .create_universal_orchestration_execution_plan(
        identity=identity_y,
        jobs=(
            target_y,
        ),
    )
)


try:

    readiness.evaluate_universal_orchestration_stage_readiness(
        dependency_resolution=resolution_x,
        execution_plan=plan_y,
    )

except readiness.UniversalOrchestrationStageReadinessError as exc:

    rejected = (
        exc.code
        == "stage_readiness_identity_mismatch"
    )

else:

    rejected = False


check(
    "same_run_id_different_contract_rejected",
    rejected,
)


# ============================================================
# 17 — INVALID DEPENDENCY RESOLUTION ATTACKS
# ============================================================

valid_target, valid_identity, valid_plan, valid_resolution, valid_result = make_context(
    run_id="invalid-resolution-attacks",
    dependency_statuses={
        "a": "succeeded",
        "b": "succeeded",
        "c": "succeeded",
    },
)


invalid_resolution_values = (
    None,
    True,
    False,
    0,
    1,
    1.0,
    "",
    "resolution",
    b"resolution",
    bytearray(b"resolution"),
    {},
    [],
    (),
    valid_target,
    valid_identity,
    valid_plan,
    object(),
)


for index, bad_value in enumerate(
    invalid_resolution_values,
    start=1,
):

    try:

        readiness.evaluate_universal_orchestration_stage_readiness(
            dependency_resolution=bad_value,
            execution_plan=valid_plan,
        )

    except readiness.UniversalOrchestrationStageReadinessError as exc:

        rejected = (
            exc.code
            == "invalid_stage_readiness_dependency_resolution"
        )

    else:

        rejected = False

    check(
        "invalid_dependency_resolution_"
        + str(index),
        rejected,
        repr(bad_value),
    )


# ============================================================
# 18 — INVALID EXECUTION PLAN ATTACKS
# ============================================================

invalid_plan_values = (
    None,
    True,
    False,
    0,
    1,
    1.0,
    "",
    "plan",
    b"plan",
    bytearray(b"plan"),
    {},
    [],
    (),
    valid_target,
    valid_identity,
    valid_resolution,
    object(),
)


for index, bad_value in enumerate(
    invalid_plan_values,
    start=1,
):

    try:

        readiness.evaluate_universal_orchestration_stage_readiness(
            dependency_resolution=valid_resolution,
            execution_plan=bad_value,
        )

    except readiness.UniversalOrchestrationStageReadinessError as exc:

        rejected = (
            exc.code
            == "invalid_stage_readiness_execution_plan"
        )

    else:

        rejected = False

    check(
        "invalid_execution_plan_"
        + str(index),
        rejected,
        repr(bad_value),
    )


# ============================================================
# 19 — DIRECT CONSTRUCTOR TYPE ATTACKS
# ============================================================

try:

    readiness.UniversalOrchestrationStageReadiness(
        dependency_resolution=None,
        execution_plan=valid_plan,
    )

except readiness.UniversalOrchestrationStageReadinessError as exc:

    rejected = (
        exc.code
        == "invalid_stage_readiness_dependency_resolution"
    )

else:

    rejected = False


check(
    "direct_constructor_bad_resolution_rejected",
    rejected,
)


try:

    readiness.UniversalOrchestrationStageReadiness(
        dependency_resolution=valid_resolution,
        execution_plan=None,
    )

except readiness.UniversalOrchestrationStageReadinessError as exc:

    rejected = (
        exc.code
        == "invalid_stage_readiness_execution_plan"
    )

else:

    rejected = False


check(
    "direct_constructor_bad_plan_rejected",
    rejected,
)


# ============================================================
# 20 — SCHEMA FORGERY
# ============================================================

for bad_schema in (
    "",
    " ",
    "v1",
    "schema_v1",
    "wrong",
    "universal_orchestration_stage_readiness_schema_v2",
):

    try:

        readiness.UniversalOrchestrationStageReadiness(
            dependency_resolution=valid_resolution,
            execution_plan=valid_plan,
            schema_version=bad_schema,
        )

    except readiness.UniversalOrchestrationStageReadinessError as exc:

        rejected = (
            exc.code
            == "invalid_stage_readiness_schema_version"
        )

    else:

        rejected = False

    check(
        "schema_forgery_"
        + repr(bad_schema),
        rejected,
    )


# ============================================================
# 21 — CLASSIFIER TYPE ATTACKS
# ============================================================

for index, bad_value in enumerate(
    invalid_resolution_values,
    start=1,
):

    try:

        readiness.classify_universal_orchestration_stage_readiness(
            bad_value
        )

    except readiness.UniversalOrchestrationStageReadinessError as exc:

        rejected = (
            exc.code
            == "invalid_stage_readiness_dependency_resolution"
        )

    else:

        rejected = False

    check(
        "classifier_invalid_resolution_"
        + str(index),
        rejected,
    )


# ============================================================
# 22 — REASON FUNCTION TYPE ATTACKS
# ============================================================

for index, bad_value in enumerate(
    invalid_resolution_values,
    start=1,
):

    try:

        readiness.reason_for_universal_orchestration_stage_readiness(
            bad_value
        )

    except readiness.UniversalOrchestrationStageReadinessError as exc:

        rejected = (
            exc.code
            == "invalid_stage_readiness_dependency_resolution"
        )

    else:

        rejected = False

    check(
        "reason_invalid_resolution_"
        + str(index),
        rejected,
    )


# ============================================================
# 23 — EXACT STORED FIELDS
# ============================================================

field_names = tuple(
    field.name
    for field in fields(
        readiness.UniversalOrchestrationStageReadiness
    )
)


check(
    "stored_fields_exact",
    field_names
    == (
        "dependency_resolution",
        "execution_plan",
        "schema_version",
    ),
    field_names,
)


for forbidden_field in (
    "identity",
    "target_job",
    "job_id",

    "classification",
    "reason",
    "reason_code",

    "is_ready",
    "is_waiting",
    "is_blocked",

    "dependency_job_ids",

    "satisfied_dependency_ids",
    "unresolved_dependency_ids",
    "terminal_unsatisfied_dependency_ids",
    "missing_dependency_ids",

    "blocking_dependency_ids",
    "waiting_dependency_ids",

    "target_status",
    "job_status",

    "queue_id",
    "queue_status",
    "queue_priority",

    "worker_id",
    "worker_status",
    "worker_capacity",
    "worker_capability",

    "lease_id",

    "handoff",
    "handoff_status",

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
# 24 — OBJECT IMMUTABILITY
# ============================================================

for field in fields(
    valid_result
):

    try:

        setattr(
            valid_result,
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
# 25 — DERIVED PROPERTY TYPES
# ============================================================

check(
    "satisfied_ids_tuple",
    isinstance(
        valid_result.satisfied_dependency_ids,
        tuple,
    ),
)

check(
    "unresolved_ids_tuple",
    isinstance(
        valid_result.unresolved_dependency_ids,
        tuple,
    ),
)

check(
    "terminal_ids_tuple",
    isinstance(
        valid_result.terminal_unsatisfied_dependency_ids,
        tuple,
    ),
)

check(
    "missing_ids_tuple",
    isinstance(
        valid_result.missing_dependency_ids,
        tuple,
    ),
)

check(
    "blocking_ids_tuple",
    isinstance(
        valid_result.blocking_dependency_ids,
        tuple,
    ),
)

check(
    "waiting_ids_tuple",
    isinstance(
        valid_result.waiting_dependency_ids,
        tuple,
    ),
)


# ============================================================
# 26 — DERIVED ID EVIDENCE MUST MATCH 5.1.4 EXACTLY
# ============================================================

_, _, _, evidence_resolution, evidence_result = make_context(
    run_id="evidence-match",
    dependency_statuses={
        "a": "succeeded",
        "b": "running",
        "c": "failed",
    },
)


check(
    "satisfied_ids_passthrough",
    evidence_result.satisfied_dependency_ids
    == evidence_resolution.satisfied_dependency_ids,
)

check(
    "unresolved_ids_passthrough",
    evidence_result.unresolved_dependency_ids
    == evidence_resolution.unresolved_dependency_ids,
)

check(
    "terminal_ids_passthrough",
    evidence_result.terminal_unsatisfied_dependency_ids
    == evidence_resolution.terminal_unsatisfied_dependency_ids,
)

check(
    "missing_ids_passthrough",
    evidence_result.missing_dependency_ids
    == evidence_resolution.missing_dependency_ids,
)


# ============================================================
# 27 — IDENTITY / TARGET MUST BE DERIVED
# ============================================================

check(
    "identity_derived",
    valid_result.identity
    == valid_resolution.identity,
)

check(
    "target_job_derived",
    valid_result.target_job
    == valid_resolution.target_job,
)

check(
    "job_id_derived",
    valid_result.job_id
    == valid_resolution.job_id,
)


# ============================================================
# 28 — REPEATED EVALUATION DETERMINISTIC
# ============================================================

repeat_one = (
    readiness.evaluate_universal_orchestration_stage_readiness(
        dependency_resolution=valid_resolution,
        execution_plan=valid_plan,
    )
)

repeat_two = (
    readiness.evaluate_universal_orchestration_stage_readiness(
        dependency_resolution=valid_resolution,
        execution_plan=valid_plan,
    )
)


check(
    "repeated_evaluation_equal",
    repeat_one
    == repeat_two,
)

check(
    "repeated_classification_equal",
    repeat_one.classification
    is repeat_two.classification,
)

check(
    "repeated_reason_equal",
    repeat_one.reason
    is repeat_two.reason,
)


# ============================================================
# 29 — EXPLANATION CONTRACT
# ============================================================

explanation = (
    readiness
    .explain_universal_orchestration_stage_readiness_v1()
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
    == "5.1.6",
)

check(
    "explanation_component",
    explanation.get(
        "component"
    )
    == "Universal Orchestration Stage Readiness Evaluation",
)

check(
    "explanation_version",
    explanation.get(
        "version"
    )
    == readiness.UNIVERSAL_ORCHESTRATION_STAGE_READINESS_VERSION,
)

check(
    "explanation_schema",
    explanation.get(
        "schema_version"
    )
    == readiness.UNIVERSAL_ORCHESTRATION_STAGE_READINESS_SCHEMA_VERSION,
)

check(
    "explanation_stored_fields",
    explanation.get(
        "stored_fields"
    )
    == (
        "dependency_resolution",
        "execution_plan",
        "schema_version",
    ),
)

check(
    "explanation_classifications",
    explanation.get(
        "classifications"
    )
    == (
        "ready",
        "waiting",
        "blocked",
    ),
)

check(
    "explanation_precedence",
    explanation.get(
        "precedence_rule"
    )
    == "BLOCKED outranks WAITING; WAITING outranks READY.",
)

check(
    "explanation_blocked_rule",
    "terminally-unsatisfied"
    in explanation.get(
        "blocked_rule",
        "",
    ),
)

check(
    "explanation_waiting_rule",
    "unresolved"
    in explanation.get(
        "waiting_rule",
        "",
    )
    and
    "missing"
    in explanation.get(
        "waiting_rule",
        "",
    ),
)

check(
    "explanation_ready_rule",
    "all dependencies satisfied"
    in explanation.get(
        "ready_rule",
        "",
    ),
)

check(
    "explanation_zero_dependency_rule",
    "zero-dependency"
    in explanation.get(
        "zero_dependency_rule",
        "",
    ),
)

check(
    "explanation_target_status_boundary",
    "does not inspect target UniversalJob.status"
    in explanation.get(
        "target_status_boundary",
        "",
    ),
)

check(
    "explanation_handoff_5_1_7",
    "5.1.7"
    in explanation.get(
        "handoff_boundary",
        "",
    ),
)

check(
    "explanation_suspension_5_1_12",
    "5.1.12"
    in explanation.get(
        "suspension_boundary",
        "",
    ),
)

check(
    "explanation_dependency_5_1_4",
    "5.1.4"
    in explanation.get(
        "dependency_boundary",
        "",
    ),
)

check(
    "explanation_planning_5_1_5",
    "5.1.5"
    in explanation.get(
        "planning_boundary",
        "",
    ),
)

check(
    "explanation_alignment",
    "same orchestration identity"
    in explanation.get(
        "alignment_rule",
        "",
    ),
)


# ============================================================
# 30 — PROHIBITION MATRIX
# ============================================================

required_prohibitions = (
    "does not inspect target UniversalJob.status",
    "does not use job priority",
    "does not use queue priority",
    "does not use created_at",
    "does not use scheduled_at",
    "does not use retry or attempt counts",

    "does not evaluate worker health",
    "does not evaluate worker capability",
    "does not evaluate worker capacity",
    "does not evaluate worker availability",

    "does not evaluate queue capacity",
    "does not evaluate backpressure",
    "does not evaluate lease availability",

    "does not transition orchestration state",
    "does not perform runtime handoff",

    "does not coordinate actual fan-out",
    "does not coordinate actual fan-in",
    "does not evaluate conditional branches",

    "does not enqueue jobs",
    "does not dequeue jobs",
    "does not claim jobs",

    "does not assign workers",
    "does not acquire worker leases",

    "does not register runtime handlers",
    "does not dispatch runtime handlers",
    "does not execute runtime handlers",
    "does not execute jobs",

    "does not access Runtime State Store",
    "does not persist readiness",

    "does not import Universal Coordination Framework",
    "does not invoke pipeline coordinators",

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


for index, prohibition in enumerate(
    required_prohibitions,
    start=1,
):

    check(
        "prohibition_"
        + str(index),
        prohibition
        in prohibitions,
        prohibition,
    )


# ============================================================
# 31 — IMPORT BOUNDARY
# ============================================================

source = READINESS_PATH.read_text(
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
        "backend.server.runtime.universal_orchestration.dependency_resolution",
        "backend.server.runtime.universal_orchestration.execution_planning",
    ],
    backend_imports,
)


# ============================================================
# 32 — FORBIDDEN IMPORTS
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

    "backend.server.runtime.universal_jobs.status",
    "backend.server.runtime.universal_worker",
    "backend.server.runtime.universal_queue",

    "backend.server.runtime.universal_orchestration.state_model",

    "backend.server.runtime.universal_runtime_registration",
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
# 33 — FORBIDDEN CALLS
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

    "transition_universal_orchestration_state",

    "enqueue_job",
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
# 34 — TARGET JOB STATUS MUST NOT BE INSPECTED
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
    "no_status_attribute_access",
    "status"
    not in attributes,
    attributes,
)


check(
    "no_priority_attribute_access",
    "priority"
    not in attributes,
    attributes,
)


check(
    "no_created_at_attribute_access",
    "created_at"
    not in attributes,
    attributes,
)


check(
    "no_scheduled_at_attribute_access",
    "scheduled_at"
    not in attributes,
    attributes,
)


check(
    "no_attempt_count_attribute_access",
    "attempt_count"
    not in attributes,
    attributes,
)


check(
    "no_maximum_attempts_attribute_access",
    "maximum_attempts"
    not in attributes,
    attributes,
)


# ============================================================
# 35 — FUNCTION RESPONSIBILITY BLEED
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
    "assign_worker",
    "lease_worker",
    "handoff",
    "dispatch",
    "execute",
    "transition_state",
    "fan_out",
    "fan_in",
    "branch",
    "persist",
    "worker_capacity",
    "worker_health",
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
# 36 — NO HIDDEN STORED AUTHORITY FIELDS
# ============================================================

source_lower = source.lower()


for forbidden_symbol in (
    "target_status:",
    "job_status:",

    "queue_priority:",
    "queue_id:",

    "worker_id:",
    "worker_health:",
    "worker_capacity:",
    "worker_capability:",

    "lease_id:",

    "handoff_status:",

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
# 37 — 5.1.4 IS SOURCE OF DEPENDENCY INTERPRETATION
# ============================================================

check(
    "dependency_resolution_is_direct_input",
    (
        "UniversalOrchestrationDependencyResolution"
        in source
    ),
)


check(
    "no_universal_job_status_import",
    not any(
        (
            module
            == "backend.server.runtime.universal_jobs.status"
            or
            module.startswith(
                "backend.server.runtime.universal_jobs.status."
            )
        )
        for module
        in all_imports
    ),
)


# ============================================================
# 38 — 5.1.5 IS STRUCTURAL ALIGNMENT INPUT ONLY
# ============================================================

check(
    "execution_plan_is_direct_input",
    (
        "UniversalOrchestrationExecutionPlan"
        in source
    ),
)


# ============================================================
# 39 — PROTECTED MATRIX
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
# 40 — FINAL AST
# ============================================================

final_ast = ast_sha(
    READINESS_PATH
)


check(
    "readiness_ast_final",
    final_ast
    == EXPECTED_READINESS_AST,
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
        "PHASE 5.1.6 — UNIVERSAL ORCHESTRATION "
        "STAGE READINESS ADVERSARIAL REGRESSION"
    ),
    "=" * 118,
    "",
    (
        "STAGE READINESS AST SHA256: "
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
            "ADVERSARIAL STAGE READINESS REGRESSION: "
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
        "STAGE READINESS AST MODIFIED: NO",
        "5.1.1 ORCHESTRATION CONTRACT MODIFIED: NO",
        "5.1.2 RUN IDENTITY MODIFIED: NO",
        "5.1.3 STATE MODEL MODIFIED: NO",
        "5.1.4 DEPENDENCY RESOLUTION MODIFIED: NO",
        "5.1.5 EXECUTION PLANNING MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",
        "",
        "READINESS VOCABULARY: READY / WAITING / BLOCKED",
        "PRECEDENCE: BLOCKED > WAITING > READY",
        "ZERO DEPENDENCIES: READY",
        "TERMINAL DEPENDENCY FAILURE: BLOCKED",
        "UNRESOLVED DEPENDENCY: WAITING",
        "MISSING DEPENDENCY EVIDENCE: WAITING",
        "",
        "TARGET UNIVERSAL JOB STATUS INSPECTED: NO",
        "TARGET JOB PRIORITY USED: NO",
        "QUEUE PRIORITY USED: NO",
        "CREATED_AT USED: NO",
        "SCHEDULED_AT USED: NO",
        "RETRY/ATTEMPT COUNTS USED: NO",
        "",
        "WORKER HEALTH/CAPABILITY/CAPACITY USED: NO",
        "QUEUE CAPACITY/BACKPRESSURE USED: NO",
        "LEASE AVAILABILITY USED: NO",
        "",
        "RUNTIME HANDOFF PERFORMED: NO",
        "ORCHESTRATION STATE TRANSITIONED: NO",
        "ACTUAL FAN-OUT COORDINATED: NO",
        "ACTUAL FAN-IN COORDINATED: NO",
        "CONDITIONAL BRANCHING EVALUATED: NO",
        "",
        "QUEUE/WORKER ACTIVITY: NO",
        "RUNTIME HANDLER ACTIVITY: NO",
        "JOB EXECUTION: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "READINESS PERSISTED: NO",
        "UNIVERSAL COORDINATION FRAMEWORK ACCESSED: NO",
        "PIPELINE COORDINATORS ACCESSED: NO",
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
            "Phase 5.1.6 Stage Readiness "
            "adversarial regression failed."
        )
    )
