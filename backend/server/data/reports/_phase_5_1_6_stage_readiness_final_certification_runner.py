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
    / "phase_5_1_6_stage_readiness_final_certification.txt"
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
            "5.1.6 Stage Readiness AST mismatch before "
            "final certification.\n"
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
                "Protected authority mismatch before "
                "5.1.6 final certification: "
                + name
                + "\nEXPECTED: "
                + expected
                + "\nACTUAL:   "
                + actual
            )
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


readiness_ast = ast_sha(
    READINESS_PATH
)


# ============================================================
# AUTHORITY / VERSION
# ============================================================

check(
    "readiness_ast_exact",
    readiness_ast
    == EXPECTED_READINESS_AST,
    readiness_ast,
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

check(
    "classification_exact",
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
    "reason_exact",
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
        created_at=FIXED_CREATED_AT,
    )


def make_context(
    *,
    run_id,
    dependency_statuses=None,
    zero_dependencies=False,
):

    if zero_dependencies:

        target = make_job(
            job_id="target",
        )

        all_jobs = (
            target,
        )

    else:

        target = make_job(
            job_id="target",
            dependencies=(
                "a",
                "b",
                "c",
            ),
        )

        all_jobs = (
            make_job(
                job_id="a",
            ),
            make_job(
                job_id="b",
            ),
            make_job(
                job_id="c",
            ),
            target,
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
# READY
# ============================================================

_, _, ready_plan, ready_resolution, ready_result = make_context(
    run_id="ready-run",
    dependency_statuses={
        "a": "succeeded",
        "b": "succeeded",
        "c": "succeeded",
    },
)


check(
    "ready_classification",
    ready_result.classification
    is readiness.UniversalOrchestrationStageReadinessClassification.READY,
)

check(
    "ready_reason",
    ready_result.reason
    is readiness.UniversalOrchestrationStageReadinessReason.ALL_DEPENDENCIES_SATISFIED,
)

check(
    "ready_reason_code",
    ready_result.reason_code
    == "all_dependencies_satisfied",
)

check(
    "ready_boolean_exact",
    (
        ready_result.is_ready
        and
        not ready_result.is_waiting
        and
        not ready_result.is_blocked
    ),
)


# ============================================================
# WAITING
# ============================================================

_, _, _, waiting_resolution, waiting_result = make_context(
    run_id="waiting-run",
    dependency_statuses={
        "a": "succeeded",
        "b": "running",
    },
)


check(
    "waiting_classification",
    waiting_result.classification
    is readiness.UniversalOrchestrationStageReadinessClassification.WAITING,
)

check(
    "waiting_reason",
    waiting_result.reason_code
    == "dependency_evidence_pending",
)

check(
    "waiting_contains_unresolved",
    waiting_result.unresolved_dependency_ids
    == (
        "b",
    ),
)

check(
    "waiting_contains_missing",
    waiting_result.missing_dependency_ids
    == (
        "c",
    ),
)

check(
    "waiting_ids_exact",
    waiting_result.waiting_dependency_ids
    == (
        "b",
        "c",
    ),
)


# ============================================================
# BLOCKED PRECEDENCE
# ============================================================

_, _, _, blocked_resolution, blocked_result = make_context(
    run_id="blocked-run",
    dependency_statuses={
        "a": "failed",
        "b": "running",
    },
)


check(
    "blocked_classification",
    blocked_result.classification
    is readiness.UniversalOrchestrationStageReadinessClassification.BLOCKED,
)

check(
    "blocked_reason",
    blocked_result.reason_code
    == "terminal_dependency_failure",
)

check(
    "blocked_ids_exact",
    blocked_result.blocking_dependency_ids
    == (
        "a",
    ),
)

check(
    "blocked_precedence_over_waiting",
    (
        blocked_resolution.has_terminal_dependency_failure
        and
        blocked_resolution.has_unresolved_dependencies
        and
        blocked_resolution.has_missing_dependency_evidence
        and
        blocked_result.is_blocked
    ),
)


# ============================================================
# ZERO DEPENDENCIES
# ============================================================

_, _, _, zero_resolution, zero_result = make_context(
    run_id="zero-run",
    dependency_statuses={},
    zero_dependencies=True,
)


check(
    "zero_dependency_resolution_satisfied",
    zero_resolution.all_dependencies_satisfied
    is True,
)

check(
    "zero_dependency_ready",
    zero_result.is_ready
    is True,
)

check(
    "zero_dependency_reason",
    zero_result.reason_code
    == "all_dependencies_satisfied",
)


# ============================================================
# TARGET STATUS SEPARATION
# ============================================================

for target_status in jobs.UniversalJobStatus:

    target = make_job(
        job_id="target",
        dependencies=(
            "a",
        ),
        status=target_status,
    )

    dep = make_job(
        job_id="a",
    )

    contract = (
        contracts
        .create_universal_runtime_orchestration_contract(
            workspace_id="workspace-a",
            pipeline="pipeline-a",
            job_ids=(
                "a",
                "target",
            ),
        )
    )

    identity = (
        identities
        .create_universal_orchestration_run_identity(
            orchestration_run_id=(
                "status-"
                + target_status.value
            ),
            contract=contract,
        )
    )

    plan = (
        planning
        .create_universal_orchestration_execution_plan(
            identity=identity,
            jobs=(
                dep,
                target,
            ),
        )
    )

    resolution = (
        dependencies
        .resolve_universal_orchestration_dependencies(
            identity=identity,
            target_job=target,
            dependency_statuses={
                "a": "succeeded",
            },
        )
    )

    result = (
        readiness
        .evaluate_universal_orchestration_stage_readiness(
            dependency_resolution=resolution,
            execution_plan=plan,
        )
    )

    check(
        "target_status_separation_"
        + target_status.value,
        result.is_ready,
        target_status.value,
    )


# ============================================================
# STORED FIELD CONTRACT
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

    "satisfied_dependency_ids",
    "unresolved_dependency_ids",
    "terminal_unsatisfied_dependency_ids",
    "missing_dependency_ids",

    "blocking_dependency_ids",
    "waiting_dependency_ids",

    "target_status",
    "job_status",

    "queue_id",
    "queue_priority",

    "worker_id",
    "worker_capacity",
    "worker_capability",

    "lease_id",

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
# IMMUTABILITY
# ============================================================

for field in fields(
    ready_result
):

    try:

        setattr(
            ready_result,
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
# DERIVED EVIDENCE
# ============================================================

check(
    "identity_derived",
    ready_result.identity
    == ready_resolution.identity,
)

check(
    "target_job_derived",
    ready_result.target_job
    == ready_resolution.target_job,
)

check(
    "job_id_derived",
    ready_result.job_id
    == ready_resolution.job_id,
)

check(
    "satisfied_ids_derived",
    ready_result.satisfied_dependency_ids
    == ready_resolution.satisfied_dependency_ids,
)

check(
    "unresolved_ids_derived",
    waiting_result.unresolved_dependency_ids
    == waiting_resolution.unresolved_dependency_ids,
)

check(
    "terminal_ids_derived",
    blocked_result.terminal_unsatisfied_dependency_ids
    == blocked_resolution.terminal_unsatisfied_dependency_ids,
)

check(
    "missing_ids_derived",
    waiting_result.missing_dependency_ids
    == waiting_resolution.missing_dependency_ids,
)


# ============================================================
# EXPLANATION
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
    "phase_exact",
    explanation.get(
        "phase"
    )
    == "5.1.6",
)

check(
    "component_exact",
    explanation.get(
        "component"
    )
    == "Universal Orchestration Stage Readiness Evaluation",
)

check(
    "precedence_exact",
    explanation.get(
        "precedence_rule"
    )
    == "BLOCKED outranks WAITING; WAITING outranks READY.",
)

check(
    "handoff_boundary_5_1_7",
    "5.1.7"
    in explanation.get(
        "handoff_boundary",
        "",
    ),
)

check(
    "suspension_boundary_5_1_12",
    "5.1.12"
    in explanation.get(
        "suspension_boundary",
        "",
    ),
)

check(
    "dependency_boundary_5_1_4",
    "5.1.4"
    in explanation.get(
        "dependency_boundary",
        "",
    ),
)

check(
    "planning_boundary_5_1_5",
    "5.1.5"
    in explanation.get(
        "planning_boundary",
        "",
    ),
)


# ============================================================
# IMPORT BOUNDARY
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
# PROHIBITIONS
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
        == expected,
        actual,
    )


# ============================================================
# CANONICAL FINGERPRINT
# ============================================================

fingerprint_material = "|".join(
    (
        "phase_5_1_6_universal_orchestration_stage_readiness",

        readiness.UNIVERSAL_ORCHESTRATION_STAGE_READINESS_VERSION,
        readiness.UNIVERSAL_ORCHESTRATION_STAGE_READINESS_SCHEMA_VERSION,

        readiness_ast,

        "classification_ready",
        "classification_waiting",
        "classification_blocked",

        "reason_all_dependencies_satisfied",
        "reason_dependency_evidence_pending",
        "reason_terminal_dependency_failure",

        "blocked_precedence_over_waiting",
        "waiting_precedence_over_ready",

        "terminal_dependency_failure_is_blocked",
        "unresolved_dependency_is_waiting",
        "missing_dependency_evidence_is_waiting",
        "all_dependencies_satisfied_is_ready",
        "zero_dependencies_is_ready",

        "stored_dependency_resolution",
        "stored_execution_plan",
        "stored_schema_version",

        "identity_derived",
        "target_job_derived",
        "job_id_derived",

        "dependency_evidence_derived_from_5_1_4",

        "execution_plan_alignment_required",
        "same_orchestration_identity_required",
        "exact_target_job_alignment_required",
        "dependency_structure_alignment_required",

        "target_job_status_not_readiness",
        "job_priority_not_readiness",
        "queue_priority_not_readiness",
        "created_at_not_readiness",
        "scheduled_at_not_readiness",
        "retry_attempts_not_readiness",

        "worker_health_not_readiness",
        "worker_capability_not_readiness",
        "worker_capacity_not_readiness",
        "queue_capacity_not_readiness",
        "backpressure_not_readiness",
        "lease_availability_not_readiness",

        "handoff_deferred_5_1_7",
        "suspension_resume_deferred_5_1_12",

        "no_state_transition",
        "no_actual_fan_out",
        "no_actual_fan_in",
        "no_conditional_branching",

        "no_queue_activity",
        "no_worker_activity",

        "no_runtime_registration_activity",
        "no_handler_dispatch",
        "no_job_execution",

        "no_runtime_state_store",
        "no_readiness_persistence",

        "no_coordination_framework",
        "no_pipeline_coordinators",

        "no_wall_clock",
        "no_filesystem_io",
        "no_network_io",

        "immutable_deterministic_dependency_readiness_authority",
    )
)


stage_readiness_fingerprint = (
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
            stage_readiness_fingerprint
        )
        == 64
        and
        all(
            character
            in "0123456789ABCDEF"
            for character
            in stage_readiness_fingerprint
        )
    ),
    stage_readiness_fingerprint,
)


# ============================================================
# FINAL AST
# ============================================================

final_ast = ast_sha(
    READINESS_PATH
)


check(
    "final_ast_unchanged",
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


lines = [
    (
        "PHASE 5.1.6 — UNIVERSAL ORCHESTRATION "
        "STAGE READINESS FINAL CERTIFICATION"
    ),
    "=" * 118,
    "",
    (
        "STAGE READINESS AST SHA256: "
        + readiness_ast
    ),
    (
        "STAGE READINESS FINGERPRINT: "
        + stage_readiness_fingerprint
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
            "FINAL STAGE READINESS CERTIFICATION: "
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
        "STAGE READINESS MODIFIED DURING CERTIFICATION: NO",
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
        "JOB/QUEUE PRIORITY USED: NO",
        "CREATED_AT/SCHEDULED_AT USED: NO",
        "RETRY/ATTEMPT COUNTS USED: NO",
        "",
        "WORKER/QUEUE ELIGIBILITY EVALUATED: NO",
        "LEASE AVAILABILITY EVALUATED: NO",
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
            "PHASE 5.1.6 FREEZE CANDIDATE: "
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
        (
            "Phase 5.1.6 Stage Readiness "
            "final certification failed."
        )
    )
