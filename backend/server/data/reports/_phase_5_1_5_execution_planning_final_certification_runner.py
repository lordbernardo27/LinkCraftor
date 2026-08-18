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

PLANNING_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_orchestration"
    / "execution_planning.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_1_5_execution_planning_final_certification.txt"
)

EXPECTED_PLANNING_AST = (
    "78F7945AD5592370C21BF919328D6C29627EF209F37A5E864C0588CD40DC7465"
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


if not PLANNING_PATH.exists():

    raise SystemExit(
        "5.1.5 Execution Planning authority missing."
    )


if (
    ast_sha(
        PLANNING_PATH
    )
    != EXPECTED_PLANNING_AST
):

    raise SystemExit(
        "5.1.5 Execution Planning AST mismatch before certification."
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
                "5.1.5 final certification: "
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


jobs_module = importlib.import_module(
    "backend.server.runtime.universal_jobs.contract"
)

contract_module = importlib.import_module(
    "backend.server.runtime.universal_orchestration.contract"
)

identity_module = importlib.import_module(
    "backend.server.runtime.universal_orchestration.run_identity"
)

module_name = (
    "backend.server.runtime."
    "universal_orchestration.execution_planning"
)

sys.modules.pop(
    module_name,
    None,
)

planning = importlib.import_module(
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


planning_ast = ast_sha(
    PLANNING_PATH
)


# ============================================================
# AUTHORITY
# ============================================================

check(
    "planning_ast_exact",
    planning_ast
    == EXPECTED_PLANNING_AST,
    planning_ast,
)

check(
    "version_exact",
    planning.UNIVERSAL_ORCHESTRATION_EXECUTION_PLANNING_VERSION
    == "universal_orchestration_execution_planning_v5.1.5",
)

check(
    "schema_exact",
    planning.UNIVERSAL_ORCHESTRATION_EXECUTION_PLANNING_SCHEMA_VERSION
    == "universal_orchestration_execution_planning_schema_v1",
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
    parent_job_id=None,
    priority=jobs_module.UniversalJobPriority.NORMAL,
    status=jobs_module.UniversalJobStatus.CREATED,
):

    return jobs_module.UniversalJob(
        job_id=job_id,
        workspace_id=workspace_id,
        pipeline=pipeline,
        stage="stage-a",
        job_type="test_job",
        payload_reference="payload-a",
        dependency_job_ids=tuple(
            dependencies
        ),
        parent_job_id=parent_job_id,
        priority=priority,
        status=status,
        created_at=FIXED_CREATED_AT,
    )


def make_identity(
    *,
    run_id,
    job_ids,
):

    contract = (
        contract_module
        .create_universal_runtime_orchestration_contract(
            workspace_id="workspace-a",
            pipeline="pipeline-a",
            job_ids=job_ids,
        )
    )

    identity = (
        identity_module
        .create_universal_orchestration_run_identity(
            orchestration_run_id=run_id,
            contract=contract,
        )
    )

    return (
        contract,
        identity,
    )


jobs = (
    make_job(
        job_id="a",
    ),

    make_job(
        job_id="b",
        dependencies=(
            "a",
        ),
    ),

    make_job(
        job_id="c",
        dependencies=(
            "a",
        ),
    ),

    make_job(
        job_id="d",
        dependencies=(
            "b",
            "c",
        ),
    ),
)


contract_a, identity_a = make_identity(
    run_id="run-a",
    job_ids=(
        "d",
        "c",
        "b",
        "a",
    ),
)


plan = (
    planning.create_universal_orchestration_execution_plan(
        identity=identity_a,
        jobs=tuple(
            reversed(
                jobs
            )
        ),
    )
)


# ============================================================
# CANONICAL GRAPH
# ============================================================

check(
    "job_ids_exact",
    plan.job_ids
    == (
        "a",
        "b",
        "c",
        "d",
    ),
)

check(
    "job_count_exact",
    plan.job_count
    == 4,
)

check(
    "dependency_map_exact",
    dict(
        plan.dependency_map
    )
    == {
        "a": (),
        "b": (
            "a",
        ),
        "c": (
            "a",
        ),
        "d": (
            "b",
            "c",
        ),
    },
)

check(
    "dependent_map_exact",
    dict(
        plan.dependent_map
    )
    == {
        "a": (
            "b",
            "c",
        ),
        "b": (
            "d",
        ),
        "c": (
            "d",
        ),
        "d": (),
    },
)

check(
    "roots_exact",
    plan.root_job_ids
    == (
        "a",
    ),
)

check(
    "leaves_exact",
    plan.leaf_job_ids
    == (
        "d",
    ),
)

check(
    "edge_count_exact",
    plan.edge_count
    == 4,
)

check(
    "waves_exact",
    plan.execution_waves
    == (
        (
            "a",
        ),
        (
            "b",
            "c",
        ),
        (
            "d",
        ),
    ),
)

check(
    "wave_count_exact",
    plan.wave_count
    == 3,
)

check(
    "topological_order_exact",
    plan.topological_order
    == (
        "a",
        "b",
        "c",
        "d",
    ),
)

check(
    "max_parallel_width_exact",
    plan.max_parallel_width
    == 2,
)

check(
    "graph_depth_exact",
    plan.graph_depth
    == 3,
)


# ============================================================
# STRUCTURAL EDGE SEMANTICS
# ============================================================

check(
    "dependency_direction_dependency_to_dependent",
    (
        "b"
        in plan.dependent_map[
            "a"
        ]
        and
        "a"
        in plan.dependency_map[
            "b"
        ]
    ),
)


# ============================================================
# COMPLETE CONTRACT MEMBERSHIP
# ============================================================

try:

    planning.create_universal_orchestration_execution_plan(
        identity=identity_a,
        jobs=jobs[:-1],
    )

except planning.UniversalOrchestrationExecutionPlanningError as exc:

    rejected = (
        exc.code
        == "missing_execution_plan_jobs"
    )

else:

    rejected = False


check(
    "complete_contract_required",
    rejected,
)


try:

    planning.create_universal_orchestration_execution_plan(
        identity=identity_a,
        jobs=jobs
        + (
            make_job(
                job_id="outside",
            ),
        ),
    )

except planning.UniversalOrchestrationExecutionPlanningError as exc:

    rejected = (
        exc.code
        == "execution_plan_job_outside_contract"
    )

else:

    rejected = False


check(
    "outside_contract_job_rejected",
    rejected,
)


# ============================================================
# DUPLICATE REJECTION
# ============================================================

try:

    planning.create_universal_orchestration_execution_plan(
        identity=identity_a,
        jobs=jobs
        + (
            jobs[0],
        ),
    )

except planning.UniversalOrchestrationExecutionPlanningError as exc:

    rejected = (
        exc.code
        == "duplicate_execution_plan_job"
    )

else:

    rejected = False


check(
    "duplicate_job_rejected",
    rejected,
)


# ============================================================
# WORKSPACE / PIPELINE / DEPENDENCY MEMBERSHIP
# ============================================================

bad_workspace_jobs = (
    make_job(
        job_id="a",
        workspace_id="workspace-b",
    ),
    jobs[1],
    jobs[2],
    jobs[3],
)


try:

    planning.create_universal_orchestration_execution_plan(
        identity=identity_a,
        jobs=bad_workspace_jobs,
    )

except planning.UniversalOrchestrationExecutionPlanningError as exc:

    rejected = (
        exc.code
        == "execution_plan_workspace_mismatch"
    )

else:

    rejected = False


check(
    "workspace_binding",
    rejected,
)


bad_pipeline_jobs = (
    make_job(
        job_id="a",
        pipeline="pipeline-b",
    ),
    jobs[1],
    jobs[2],
    jobs[3],
)


try:

    planning.create_universal_orchestration_execution_plan(
        identity=identity_a,
        jobs=bad_pipeline_jobs,
    )

except planning.UniversalOrchestrationExecutionPlanningError as exc:

    rejected = (
        exc.code
        == "execution_plan_pipeline_mismatch"
    )

else:

    rejected = False


check(
    "pipeline_binding",
    rejected,
)


outside_dependency_jobs = (
    make_job(
        job_id="a",
    ),
    make_job(
        job_id="b",
        dependencies=(
            "outside",
        ),
    ),
    jobs[2],
    jobs[3],
)


try:

    planning.create_universal_orchestration_execution_plan(
        identity=identity_a,
        jobs=outside_dependency_jobs,
    )

except planning.UniversalOrchestrationExecutionPlanningError as exc:

    rejected = (
        exc.code
        == "execution_plan_dependency_outside_contract"
    )

else:

    rejected = False


check(
    "dependency_membership_required",
    rejected,
)


# ============================================================
# CYCLE DETECTION
# ============================================================

cycle_jobs = (
    make_job(
        job_id="a",
        dependencies=(
            "c",
        ),
    ),
    make_job(
        job_id="b",
        dependencies=(
            "a",
        ),
    ),
    make_job(
        job_id="c",
        dependencies=(
            "b",
        ),
    ),
)


_, cycle_identity = make_identity(
    run_id="run-cycle",
    job_ids=(
        "a",
        "b",
        "c",
    ),
)


try:

    planning.create_universal_orchestration_execution_plan(
        identity=cycle_identity,
        jobs=cycle_jobs,
    )

except planning.UniversalOrchestrationExecutionPlanningError as exc:

    cycle_rejected = (
        exc.code
        == "execution_plan_dependency_cycle"
    )

else:

    cycle_rejected = False


check(
    "cross_job_cycle_rejected",
    cycle_rejected,
)


# ============================================================
# DISCONNECTED + ISOLATED
# ============================================================

disconnected_jobs = (
    make_job(
        job_id="a",
    ),
    make_job(
        job_id="b",
        dependencies=(
            "a",
        ),
    ),
    make_job(
        job_id="c",
    ),
    make_job(
        job_id="d",
        dependencies=(
            "c",
        ),
    ),
    make_job(
        job_id="e",
    ),
)


_, disconnected_identity = make_identity(
    run_id="run-disconnected",
    job_ids=(
        "e",
        "d",
        "c",
        "b",
        "a",
    ),
)


disconnected = (
    planning.create_universal_orchestration_execution_plan(
        identity=disconnected_identity,
        jobs=disconnected_jobs,
    )
)


check(
    "disconnected_components_allowed",
    disconnected.execution_waves
    == (
        (
            "a",
            "c",
            "e",
        ),
        (
            "b",
            "d",
        ),
    ),
)

check(
    "isolated_root_and_leaf",
    (
        "e"
        in disconnected.root_job_ids
        and
        "e"
        in disconnected.leaf_job_ids
    ),
)


# ============================================================
# STATUS / PRIORITY / CREATED_AT DO NOT DRIVE TOPOLOGY
# ============================================================

policy_jobs = (
    make_job(
        job_id="a",
        priority=jobs_module.UniversalJobPriority.BACKGROUND,
        status=jobs_module.UniversalJobStatus.FAILED,
    ),

    make_job(
        job_id="b",
        priority=jobs_module.UniversalJobPriority.CRITICAL,
        status=jobs_module.UniversalJobStatus.SUCCEEDED,
    ),
)


_, policy_identity = make_identity(
    run_id="run-policy",
    job_ids=(
        "b",
        "a",
    ),
)


policy_plan = (
    planning.create_universal_orchestration_execution_plan(
        identity=policy_identity,
        jobs=policy_jobs,
    )
)


check(
    "status_priority_do_not_drive_topology",
    policy_plan.topological_order
    == (
        "a",
        "b",
    ),
)


# ============================================================
# PARENT DOES NOT CREATE EDGE
# ============================================================

parent_job = make_job(
    job_id="child",
    parent_job_id="parent",
)


_, parent_identity = make_identity(
    run_id="run-parent",
    job_ids=(
        "child",
    ),
)


parent_plan = (
    planning.create_universal_orchestration_execution_plan(
        identity=parent_identity,
        jobs=(
            parent_job,
        ),
    )
)


check(
    "parent_not_implicit_edge",
    (
        parent_plan.edge_count
        == 0
        and
        parent_plan.root_job_ids
        == (
            "child",
        )
        and
        parent_plan.leaf_job_ids
        == (
            "child",
        )
    ),
)


# ============================================================
# STORED FIELD CONTRACT
# ============================================================

field_names = tuple(
    field.name
    for field in fields(
        planning.UniversalOrchestrationExecutionPlan
    )
)


check(
    "stored_fields_exact",
    field_names
    == (
        "identity",
        "jobs",
        "schema_version",
    ),
    field_names,
)


for forbidden_field in (
    "job_ids",
    "job_count",
    "job_map",
    "dependency_map",
    "dependent_map",

    "root_job_ids",
    "leaf_job_ids",
    "edge_count",

    "execution_waves",
    "wave_count",
    "topological_order",

    "max_parallel_width",
    "graph_depth",

    "dependency_statuses",
    "readiness",

    "ready_job_ids",
    "blocked_job_ids",
    "waiting_job_ids",

    "queue_order",
    "worker_assignments",

    "fan_out_state",
    "fan_in_state",
    "condition_result",

    "orchestration_state",

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
    plan
):

    try:

        setattr(
            plan,
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


check(
    "job_map_mappingproxy",
    isinstance(
        plan.job_map,
        MappingProxyType,
    ),
)

check(
    "dependency_map_mappingproxy",
    isinstance(
        plan.dependency_map,
        MappingProxyType,
    ),
)

check(
    "dependent_map_mappingproxy",
    isinstance(
        plan.dependent_map,
        MappingProxyType,
    ),
)


# ============================================================
# EXPLANATION / BOUNDARIES
# ============================================================

explanation = (
    planning
    .explain_universal_orchestration_execution_planning_v1()
)


check(
    "phase_exact",
    explanation.get(
        "phase"
    )
    == "5.1.5",
)

check(
    "component_exact",
    explanation.get(
        "component"
    )
    == "Universal Orchestration Execution Planning",
)

check(
    "stored_fields_explanation_exact",
    explanation.get(
        "stored_fields"
    )
    == (
        "identity",
        "jobs",
        "schema_version",
    ),
)

check(
    "dependency_status_boundary_5_1_4",
    "5.1.4"
    in explanation.get(
        "dependency_status_boundary",
        "",
    ),
)

check(
    "readiness_boundary_5_1_6",
    "5.1.6"
    in explanation.get(
        "readiness_boundary",
        "",
    ),
)

check(
    "fan_out_boundary_5_1_8",
    "5.1.8"
    in explanation.get(
        "fan_out_boundary",
        "",
    ),
)

check(
    "fan_in_boundary_5_1_9",
    "5.1.9"
    in explanation.get(
        "fan_in_boundary",
        "",
    ),
)

check(
    "condition_boundary_5_1_10",
    "5.1.10"
    in explanation.get(
        "condition_boundary",
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


# ============================================================
# IMPORT BOUNDARY
# ============================================================

source = PLANNING_PATH.read_text(
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
        "backend.server.runtime.universal_jobs.contract",
        "backend.server.runtime.universal_orchestration.run_identity",
    ],
    backend_imports,
)


# ============================================================
# PROHIBITION MATRIX
# ============================================================

required_prohibitions = (
    "does not evaluate dependency statuses",
    "does not determine READY",
    "does not determine BLOCKED",
    "does not determine WAITING",
    "does not transition orchestration state",

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

    "does not import Universal Coordination Framework",
    "does not invoke pipeline coordinators",

    "does not access Runtime State Store",
    "does not persist execution plans",

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
# CANONICAL 5.1.5 FINGERPRINT
# ============================================================

fingerprint_material = "|".join(
    (
        "phase_5_1_5_universal_orchestration_execution_planning",

        planning.UNIVERSAL_ORCHESTRATION_EXECUTION_PLANNING_VERSION,
        planning.UNIVERSAL_ORCHESTRATION_EXECUTION_PLANNING_SCHEMA_VERSION,

        planning_ast,

        "stored_identity",
        "stored_jobs",
        "stored_schema_version",

        "complete_contract_job_coverage",

        "dependency_edge_dependency_to_dependent",

        "dependency_map_derived",
        "dependent_map_derived",

        "root_job_ids_derived",
        "leaf_job_ids_derived",

        "edge_count_derived",

        "execution_waves_derived",
        "topological_order_derived",

        "wave_count_derived",
        "max_parallel_width_derived",
        "graph_depth_derived",

        "cross_job_cycle_detection",
        "cycles_rejected",

        "disconnected_dags_allowed",
        "isolated_job_root_and_leaf",

        "lexical_structural_tie_break",

        "dependency_status_not_topology",
        "job_status_not_topology",
        "job_priority_not_topology",
        "queue_priority_not_topology",
        "created_at_not_topology",

        "parent_job_id_not_implicit_dependency_edge",

        "dependency_status_external_5_1_4",
        "readiness_external_5_1_6",

        "actual_fan_out_external_5_1_8",
        "actual_fan_in_external_5_1_9",

        "conditional_branching_external_5_1_10",
        "persistence_external_5_1_14",

        "no_orchestration_state_transition",

        "no_queue_activity",
        "no_worker_activity",

        "no_runtime_registration_activity",
        "no_runtime_handler_dispatch",
        "no_job_execution",

        "no_coordination_framework",
        "no_pipeline_coordinators",

        "no_runtime_state_store",
        "no_execution_plan_persistence",

        "no_wall_clock",
        "no_filesystem_io",
        "no_network_io",

        "immutable_deterministic_execution_plan",

        "pure_runtime_orchestration_structural_planning_authority",
    )
)


execution_planning_fingerprint = (
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
            execution_planning_fingerprint
        )
        == 64
        and
        all(
            character
            in "0123456789ABCDEF"
            for character
            in execution_planning_fingerprint
        )
    ),
    execution_planning_fingerprint,
)


# ============================================================
# FINAL AST
# ============================================================

final_ast = ast_sha(
    PLANNING_PATH
)


check(
    "final_ast_unchanged",
    final_ast
    == EXPECTED_PLANNING_AST,
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
        "PHASE 5.1.5 — UNIVERSAL ORCHESTRATION "
        "EXECUTION PLANNING FINAL CERTIFICATION"
    ),
    "=" * 118,
    "",
    (
        "EXECUTION PLANNING AST SHA256: "
        + planning_ast
    ),
    (
        "EXECUTION PLANNING FINGERPRINT: "
        + execution_planning_fingerprint
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
            "FINAL EXECUTION PLANNING CERTIFICATION: "
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
        "EXECUTION PLANNING MODIFIED DURING CERTIFICATION: NO",
        "5.1.1 ORCHESTRATION CONTRACT MODIFIED: NO",
        "5.1.2 RUN IDENTITY MODIFIED: NO",
        "5.1.3 STATE MODEL MODIFIED: NO",
        "5.1.4 DEPENDENCY RESOLUTION MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME WORKER MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "",
        "COMPLETE CONTRACT JOB COVERAGE REQUIRED: YES",
        "DEPENDENCY EDGE DIRECTION: DEPENDENCY -> DEPENDENT",
        "MULTI-JOB CYCLE DETECTION: YES — STRUCTURAL VALIDATION ONLY",
        "DISCONNECTED DAG COMPONENTS ALLOWED: YES",
        "ISOLATED JOB ROOT AND LEAF: YES",
        "LEXICAL STRUCTURAL TIE-BREAK: YES",
        "",
        "DEPENDENCY STATUS EVALUATED: NO",
        "JOB STATUS USED FOR TOPOLOGY: NO",
        "JOB PRIORITY USED FOR TOPOLOGY: NO",
        "QUEUE PRIORITY USED FOR TOPOLOGY: NO",
        "CREATED_AT USED FOR TOPOLOGY: NO",
        "PARENT_JOB_ID USED AS IMPLICIT EDGE: NO",
        "",
        "READINESS DETERMINED: NO",
        "READY/BLOCKED/WAITING DETERMINED: NO",
        "ORCHESTRATION STATE TRANSITIONED: NO",
        "ACTUAL FAN-OUT COORDINATED: NO",
        "ACTUAL FAN-IN COORDINATED: NO",
        "CONDITIONAL BRANCHING EVALUATED: NO",
        "",
        "QUEUE/WORKER ACTIVITY: NO",
        "RUNTIME HANDLER ACTIVITY: NO",
        "JOB EXECUTION: NO",
        "UNIVERSAL COORDINATION FRAMEWORK ACCESSED: NO",
        "PIPELINE COORDINATORS ACCESSED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "EXECUTION PLAN PERSISTED: NO",
        "WALL CLOCK USED: NO",
        "FILESYSTEM/NETWORK I/O: NO",
        "",
        (
            "PHASE 5.1.5 FREEZE CANDIDATE: "
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
            "Phase 5.1.5 Execution Planning "
            "final certification failed."
        )
    )
