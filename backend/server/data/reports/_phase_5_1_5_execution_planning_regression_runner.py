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
    / "phase_5_1_5_execution_planning_regression.txt"
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


# ============================================================
# PRE-FLIGHT PROTECTION
# ============================================================

if not PLANNING_PATH.exists():

    raise SystemExit(
        "5.1.5 Execution Planning authority missing."
    )


initial_ast = ast_sha(
    PLANNING_PATH
)


if initial_ast != EXPECTED_PLANNING_AST:

    raise SystemExit(
        (
            "5.1.5 Execution Planning AST changed before "
            "adversarial regression.\n"
            "EXPECTED: "
            + EXPECTED_PLANNING_AST
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
                "5.1.5 adversarial regression: "
                + name
                + "\nEXPECTED: "
                + expected
                + "\nACTUAL:   "
                + actual
            )
        )


# ============================================================
# IMPORT AUTHORITIES
# ============================================================

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


planning_module_name = (
    "backend.server.runtime."
    "universal_orchestration.execution_planning"
)

sys.modules.pop(
    planning_module_name,
    None,
)

planning = importlib.import_module(
    planning_module_name
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
# FIXTURE HELPERS
# ============================================================

FIXED_CREATED_AT = (
    "2026-05-21T03:49:30.579317+00:00"
)

LATER_CREATED_AT = (
    "2026-05-22T03:49:30.579317+00:00"
)


def make_job(
    *,
    job_id,
    dependencies=(),
    workspace_id="workspace-a",
    pipeline="pipeline-a",
    parent_job_id=None,
    priority=jobs_module.UniversalJobPriority.NORMAL,
    created_at=FIXED_CREATED_AT,
    status=jobs_module.UniversalJobStatus.CREATED,
):

    return jobs_module.UniversalJob(
        job_id=job_id,
        workspace_id=workspace_id,
        pipeline=pipeline,
        stage="stage-a",
        job_type="test_job",
        payload_reference="payload-a",
        status=status,
        parent_job_id=parent_job_id,
        dependency_job_ids=tuple(
            dependencies
        ),
        priority=priority,
        created_at=created_at,
    )


def make_identity(
    *,
    run_id,
    job_ids,
    workspace_id="workspace-a",
    pipeline="pipeline-a",
):

    contract = (
        contract_module
        .create_universal_runtime_orchestration_contract(
            workspace_id=workspace_id,
            pipeline=pipeline,
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


# ============================================================
# 1 — AUTHORITY / VERSION / API
# ============================================================

check(
    "planning_ast_initial",
    ast_sha(
        PLANNING_PATH
    )
    == EXPECTED_PLANNING_AST,
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


expected_all = (
    "UNIVERSAL_ORCHESTRATION_EXECUTION_PLANNING_VERSION",
    "UNIVERSAL_ORCHESTRATION_EXECUTION_PLANNING_SCHEMA_VERSION",
    "UniversalOrchestrationExecutionPlanningError",
    "UniversalOrchestrationExecutionPlan",
    "create_universal_orchestration_execution_plan",
    "explain_universal_orchestration_execution_planning_v1",
)


check(
    "api_surface_exact",
    tuple(
        planning.__all__
    )
    == expected_all,
    planning.__all__,
)


# ============================================================
# 2 — PRIMARY DIAMOND DAG
# ============================================================

diamond_jobs = (
    make_job(
        job_id="d",
        dependencies=(
            "b",
            "c",
        ),
    ),
    make_job(
        job_id="c",
        dependencies=(
            "a",
        ),
    ),
    make_job(
        job_id="a",
    ),
    make_job(
        job_id="b",
        dependencies=(
            "a",
        ),
    ),
)


diamond_contract, diamond_identity = make_identity(
    run_id="run-diamond",
    job_ids=(
        "d",
        "a",
        "c",
        "b",
    ),
)


diamond = (
    planning.create_universal_orchestration_execution_plan(
        identity=diamond_identity,
        jobs=diamond_jobs,
    )
)


check(
    "diamond_job_ids",
    diamond.job_ids
    == (
        "a",
        "b",
        "c",
        "d",
    ),
)

check(
    "diamond_job_count",
    diamond.job_count
    == 4,
)

check(
    "diamond_dependency_map",
    dict(
        diamond.dependency_map
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
    "diamond_dependent_map",
    dict(
        diamond.dependent_map
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
    "diamond_roots",
    diamond.root_job_ids
    == (
        "a",
    ),
)

check(
    "diamond_leaves",
    diamond.leaf_job_ids
    == (
        "d",
    ),
)

check(
    "diamond_edges",
    diamond.edge_count
    == 4,
)

check(
    "diamond_waves",
    diamond.execution_waves
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
    "diamond_topological_order",
    diamond.topological_order
    == (
        "a",
        "b",
        "c",
        "d",
    ),
)

check(
    "diamond_wave_count",
    diamond.wave_count
    == 3,
)

check(
    "diamond_graph_depth",
    diamond.graph_depth
    == 3,
)

check(
    "diamond_parallel_width",
    diamond.max_parallel_width
    == 2,
)


# ============================================================
# 3 — INPUT ORDER MUST NOT MATTER
# ============================================================

diamond_reverse = (
    planning.create_universal_orchestration_execution_plan(
        identity=diamond_identity,
        jobs=tuple(
            reversed(
                diamond_jobs
            )
        ),
    )
)


check(
    "job_input_order_deterministic_object",
    diamond_reverse
    == diamond,
)

check(
    "job_input_order_deterministic_jobs",
    diamond_reverse.jobs
    == diamond.jobs,
)

check(
    "job_input_order_deterministic_waves",
    diamond_reverse.execution_waves
    == diamond.execution_waves,
)

check(
    "job_input_order_deterministic_topological",
    diamond_reverse.topological_order
    == diamond.topological_order,
)


# ============================================================
# 4 — GENERATOR INPUT
# ============================================================

generator_plan = (
    planning.create_universal_orchestration_execution_plan(
        identity=diamond_identity,
        jobs=(
            job
            for job
            in diamond_jobs
        ),
    )
)


check(
    "generator_input_supported",
    generator_plan
    == diamond,
)


# ============================================================
# 5 — LINEAR CHAIN
# ============================================================

chain_jobs = (
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
            "b",
        ),
    ),
    make_job(
        job_id="d",
        dependencies=(
            "c",
        ),
    ),
    make_job(
        job_id="e",
        dependencies=(
            "d",
        ),
    ),
)


_, chain_identity = make_identity(
    run_id="run-chain",
    job_ids=(
        "a",
        "b",
        "c",
        "d",
        "e",
    ),
)


chain_plan = (
    planning.create_universal_orchestration_execution_plan(
        identity=chain_identity,
        jobs=chain_jobs,
    )
)


check(
    "chain_root",
    chain_plan.root_job_ids
    == (
        "a",
    ),
)

check(
    "chain_leaf",
    chain_plan.leaf_job_ids
    == (
        "e",
    ),
)

check(
    "chain_edges",
    chain_plan.edge_count
    == 4,
)

check(
    "chain_waves",
    chain_plan.execution_waves
    == (
        ("a",),
        ("b",),
        ("c",),
        ("d",),
        ("e",),
    ),
)

check(
    "chain_depth",
    chain_plan.graph_depth
    == 5,
)

check(
    "chain_width",
    chain_plan.max_parallel_width
    == 1,
)


# ============================================================
# 6 — WIDE FAN-OUT STRUCTURE
# ============================================================

wide_jobs = (
    make_job(
        job_id="root",
    ),
    make_job(
        job_id="a",
        dependencies=(
            "root",
        ),
    ),
    make_job(
        job_id="b",
        dependencies=(
            "root",
        ),
    ),
    make_job(
        job_id="c",
        dependencies=(
            "root",
        ),
    ),
    make_job(
        job_id="d",
        dependencies=(
            "root",
        ),
    ),
    make_job(
        job_id="e",
        dependencies=(
            "root",
        ),
    ),
)


_, wide_identity = make_identity(
    run_id="run-wide",
    job_ids=(
        "root",
        "a",
        "b",
        "c",
        "d",
        "e",
    ),
)


wide_plan = (
    planning.create_universal_orchestration_execution_plan(
        identity=wide_identity,
        jobs=wide_jobs,
    )
)


check(
    "wide_root",
    wide_plan.root_job_ids
    == (
        "root",
    ),
)

check(
    "wide_leaves",
    wide_plan.leaf_job_ids
    == (
        "a",
        "b",
        "c",
        "d",
        "e",
    ),
)

check(
    "wide_waves",
    wide_plan.execution_waves
    == (
        (
            "root",
        ),
        (
            "a",
            "b",
            "c",
            "d",
            "e",
        ),
    ),
)

check(
    "wide_parallel_width",
    wide_plan.max_parallel_width
    == 5,
)

check(
    "wide_edge_count",
    wide_plan.edge_count
    == 5,
)


# ============================================================
# 7 — WIDE FAN-IN STRUCTURE
# ============================================================

join_jobs = (
    make_job(
        job_id="a",
    ),
    make_job(
        job_id="b",
    ),
    make_job(
        job_id="c",
    ),
    make_job(
        job_id="d",
    ),
    make_job(
        job_id="join",
        dependencies=(
            "a",
            "b",
            "c",
            "d",
        ),
    ),
)


_, join_identity = make_identity(
    run_id="run-join",
    job_ids=(
        "join",
        "d",
        "c",
        "b",
        "a",
    ),
)


join_plan = (
    planning.create_universal_orchestration_execution_plan(
        identity=join_identity,
        jobs=join_jobs,
    )
)


check(
    "join_roots",
    join_plan.root_job_ids
    == (
        "a",
        "b",
        "c",
        "d",
    ),
)

check(
    "join_leaf",
    join_plan.leaf_job_ids
    == (
        "join",
    ),
)

check(
    "join_waves",
    join_plan.execution_waves
    == (
        (
            "a",
            "b",
            "c",
            "d",
        ),
        (
            "join",
        ),
    ),
)

check(
    "join_edge_count",
    join_plan.edge_count
    == 4,
)


# ============================================================
# 8 — DISCONNECTED COMPONENTS + ISOLATED NODE
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
        "c",
        "a",
        "d",
        "b",
    ),
)


disconnected_plan = (
    planning.create_universal_orchestration_execution_plan(
        identity=disconnected_identity,
        jobs=disconnected_jobs,
    )
)


check(
    "disconnected_roots",
    disconnected_plan.root_job_ids
    == (
        "a",
        "c",
        "e",
    ),
)

check(
    "disconnected_leaves",
    disconnected_plan.leaf_job_ids
    == (
        "b",
        "d",
        "e",
    ),
)

check(
    "isolated_node_root_and_leaf",
    (
        "e"
        in disconnected_plan.root_job_ids
        and
        "e"
        in disconnected_plan.leaf_job_ids
    ),
)

check(
    "disconnected_waves",
    disconnected_plan.execution_waves
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
    "disconnected_topological",
    disconnected_plan.topological_order
    == (
        "a",
        "c",
        "e",
        "b",
        "d",
    ),
)


# ============================================================
# 9 — SINGLE JOB
# ============================================================

single_job = make_job(
    job_id="only",
)


_, single_identity = make_identity(
    run_id="run-single",
    job_ids=(
        "only",
    ),
)


single_plan = (
    planning.create_universal_orchestration_execution_plan(
        identity=single_identity,
        jobs=(
            single_job,
        ),
    )
)


check(
    "single_root",
    single_plan.root_job_ids
    == (
        "only",
    ),
)

check(
    "single_leaf",
    single_plan.leaf_job_ids
    == (
        "only",
    ),
)

check(
    "single_edge_count_zero",
    single_plan.edge_count
    == 0,
)

check(
    "single_wave",
    single_plan.execution_waves
    == (
        (
            "only",
        ),
    ),
)

check(
    "single_depth",
    single_plan.graph_depth
    == 1,
)

check(
    "single_width",
    single_plan.max_parallel_width
    == 1,
)


# ============================================================
# 10 — DEPENDENCY MUST OVERRIDE LEXICAL ORDER
# ============================================================

reverse_lexical_jobs = (
    make_job(
        job_id="z-root",
    ),
    make_job(
        job_id="a-dependent",
        dependencies=(
            "z-root",
        ),
    ),
)


_, reverse_lexical_identity = make_identity(
    run_id="run-reverse-lexical",
    job_ids=(
        "a-dependent",
        "z-root",
    ),
)


reverse_lexical_plan = (
    planning.create_universal_orchestration_execution_plan(
        identity=reverse_lexical_identity,
        jobs=reverse_lexical_jobs,
    )
)


check(
    "dependency_precedes_lexically_earlier_dependent",
    reverse_lexical_plan.topological_order
    == (
        "z-root",
        "a-dependent",
    ),
)


# ============================================================
# 11 — PRIORITY MUST NOT AFFECT STRUCTURAL TIE BREAK
# ============================================================

priority_jobs = (
    make_job(
        job_id="a",
        priority=jobs_module.UniversalJobPriority.BACKGROUND,
    ),
    make_job(
        job_id="b",
        priority=jobs_module.UniversalJobPriority.CRITICAL,
    ),
    make_job(
        job_id="c",
        priority=jobs_module.UniversalJobPriority.HIGH,
    ),
)


_, priority_identity = make_identity(
    run_id="run-priority",
    job_ids=(
        "c",
        "b",
        "a",
    ),
)


priority_plan = (
    planning.create_universal_orchestration_execution_plan(
        identity=priority_identity,
        jobs=priority_jobs,
    )
)


check(
    "priority_ignored_for_topology",
    priority_plan.topological_order
    == (
        "a",
        "b",
        "c",
    ),
)

check(
    "priority_ignored_for_wave",
    priority_plan.execution_waves
    == (
        (
            "a",
            "b",
            "c",
        ),
    ),
)


# ============================================================
# 12 — CREATED_AT MUST NOT AFFECT STRUCTURAL TIE BREAK
# ============================================================

time_jobs = (
    make_job(
        job_id="a",
        created_at=LATER_CREATED_AT,
    ),
    make_job(
        job_id="b",
        created_at=FIXED_CREATED_AT,
    ),
)


_, time_identity = make_identity(
    run_id="run-created-at",
    job_ids=(
        "b",
        "a",
    ),
)


time_plan = (
    planning.create_universal_orchestration_execution_plan(
        identity=time_identity,
        jobs=time_jobs,
    )
)


check(
    "created_at_ignored_for_topology",
    time_plan.topological_order
    == (
        "a",
        "b",
    ),
)


# ============================================================
# 13 — JOB STATUS MUST NOT AFFECT STRUCTURAL TOPOLOGY
# ============================================================

status_jobs = (
    make_job(
        job_id="a",
        status=jobs_module.UniversalJobStatus.FAILED,
    ),
    make_job(
        job_id="b",
        status=jobs_module.UniversalJobStatus.SUCCEEDED,
    ),
    make_job(
        job_id="c",
        dependencies=(
            "a",
            "b",
        ),
        status=jobs_module.UniversalJobStatus.RUNNING,
    ),
)


_, status_identity = make_identity(
    run_id="run-status",
    job_ids=(
        "c",
        "a",
        "b",
    ),
)


status_plan = (
    planning.create_universal_orchestration_execution_plan(
        identity=status_identity,
        jobs=status_jobs,
    )
)


check(
    "job_status_ignored_for_topology",
    status_plan.execution_waves
    == (
        (
            "a",
            "b",
        ),
        (
            "c",
        ),
    ),
)


# ============================================================
# 14 — PARENT_JOB_ID MUST NOT CREATE EDGE
# ============================================================

parent_jobs = (
    make_job(
        job_id="child",
        parent_job_id="parent",
    ),
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
        jobs=parent_jobs,
    )
)


check(
    "parent_not_dependency_edge",
    parent_plan.edge_count
    == 0,
)

check(
    "parent_not_dependency_map",
    dict(
        parent_plan.dependency_map
    )
    == {
        "child": (),
    },
)


# ============================================================
# 15 — MULTI-NODE CYCLE REJECTION
# ============================================================

cycle_cases = (
    (
        "two-node",
        (
            make_job(
                job_id="a",
                dependencies=(
                    "b",
                ),
            ),
            make_job(
                job_id="b",
                dependencies=(
                    "a",
                ),
            ),
        ),
    ),

    (
        "three-node",
        (
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
        ),
    ),

    (
        "cycle-with-independent-root",
        (
            make_job(
                job_id="root",
            ),
            make_job(
                job_id="a",
                dependencies=(
                    "b",
                ),
            ),
            make_job(
                job_id="b",
                dependencies=(
                    "a",
                ),
            ),
        ),
    ),

    (
        "cycle-with-downstream",
        (
            make_job(
                job_id="a",
                dependencies=(
                    "b",
                ),
            ),
            make_job(
                job_id="b",
                dependencies=(
                    "a",
                ),
            ),
            make_job(
                job_id="downstream",
                dependencies=(
                    "a",
                ),
            ),
        ),
    ),
)


for case_name, case_jobs in cycle_cases:

    _, case_identity = make_identity(
        run_id="run-" + case_name,
        job_ids=tuple(
            job.job_id
            for job in case_jobs
        ),
    )

    try:

        planning.create_universal_orchestration_execution_plan(
            identity=case_identity,
            jobs=case_jobs,
        )

    except planning.UniversalOrchestrationExecutionPlanningError as exc:

        rejected = (
            exc.code
            == "execution_plan_dependency_cycle"
        )

    else:

        rejected = False

    check(
        "cycle_rejected_"
        + case_name,
        rejected,
    )


# ============================================================
# 16 — TARGET CONTRACT COMPLETENESS
# ============================================================

try:

    planning.create_universal_orchestration_execution_plan(
        identity=diamond_identity,
        jobs=diamond_jobs[:-1],
    )

except planning.UniversalOrchestrationExecutionPlanningError as exc:

    rejected = (
        exc.code
        == "missing_execution_plan_jobs"
    )

else:

    rejected = False


check(
    "missing_contract_member_rejected",
    rejected,
)


extra_job = make_job(
    job_id="extra",
)


try:

    planning.create_universal_orchestration_execution_plan(
        identity=diamond_identity,
        jobs=diamond_jobs
        + (
            extra_job,
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
    "extra_contract_member_rejected",
    rejected,
)


# ============================================================
# 17 — DUPLICATE JOB OBJECT / ID
# ============================================================

try:

    planning.create_universal_orchestration_execution_plan(
        identity=diamond_identity,
        jobs=diamond_jobs
        + (
            diamond_jobs[0],
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


duplicate_different_object = make_job(
    job_id=diamond_jobs[0].job_id,
    dependencies=diamond_jobs[0].dependency_job_ids,
)


try:

    planning.create_universal_orchestration_execution_plan(
        identity=diamond_identity,
        jobs=diamond_jobs
        + (
            duplicate_different_object,
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
    "duplicate_job_id_different_object_rejected",
    rejected,
)


# ============================================================
# 18 — OUTSIDE DEPENDENCY REJECTION
# ============================================================

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
)


_, outside_dependency_identity = make_identity(
    run_id="run-outside-dependency",
    job_ids=(
        "a",
        "b",
    ),
)


try:

    planning.create_universal_orchestration_execution_plan(
        identity=outside_dependency_identity,
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
    "dependency_outside_contract_rejected",
    rejected,
)


# ============================================================
# 19 — WORKSPACE / PIPELINE BINDING
# ============================================================

workspace_bad_jobs = (
    make_job(
        job_id="a",
        workspace_id="workspace-b",
    ),
)


_, workspace_identity = make_identity(
    run_id="run-workspace",
    job_ids=(
        "a",
    ),
)


try:

    planning.create_universal_orchestration_execution_plan(
        identity=workspace_identity,
        jobs=workspace_bad_jobs,
    )

except planning.UniversalOrchestrationExecutionPlanningError as exc:

    rejected = (
        exc.code
        == "execution_plan_workspace_mismatch"
    )

else:

    rejected = False


check(
    "workspace_mismatch_rejected",
    rejected,
)


pipeline_bad_jobs = (
    make_job(
        job_id="a",
        pipeline="pipeline-b",
    ),
)


_, pipeline_identity = make_identity(
    run_id="run-pipeline",
    job_ids=(
        "a",
    ),
)


try:

    planning.create_universal_orchestration_execution_plan(
        identity=pipeline_identity,
        jobs=pipeline_bad_jobs,
    )

except planning.UniversalOrchestrationExecutionPlanningError as exc:

    rejected = (
        exc.code
        == "execution_plan_pipeline_mismatch"
    )

else:

    rejected = False


check(
    "pipeline_mismatch_rejected",
    rejected,
)


# ============================================================
# 20 — INVALID IDENTITY ATTACKS
# ============================================================

for index, bad_identity in enumerate(
    (
        None,
        True,
        False,
        0,
        1,
        1.0,
        "",
        {},
        [],
        diamond_contract,
        diamond_jobs[0],
        object(),
    ),
    start=1,
):

    try:

        planning.create_universal_orchestration_execution_plan(
            identity=bad_identity,
            jobs=diamond_jobs,
        )

    except planning.UniversalOrchestrationExecutionPlanningError as exc:

        rejected = (
            exc.code
            == "invalid_execution_plan_identity"
        )

    else:

        rejected = False

    check(
        "invalid_identity_attack_"
        + str(index),
        rejected,
        repr(bad_identity),
    )


# ============================================================
# 21 — INVALID JOB COLLECTION ATTACKS
# ============================================================

for index, bad_jobs in enumerate(
    (
        None,
        True,
        False,
        0,
        1,
        1.0,
        "",
        "abc",
        b"abc",
        bytearray(b"abc"),
        {},
        object(),
    ),
    start=1,
):

    try:

        planning.create_universal_orchestration_execution_plan(
            identity=diamond_identity,
            jobs=bad_jobs,
        )

    except planning.UniversalOrchestrationExecutionPlanningError as exc:

        rejected = (
            exc.code
            == "invalid_execution_plan_jobs"
        )

    else:

        rejected = False

    check(
        "invalid_jobs_collection_"
        + str(index),
        rejected,
        repr(bad_jobs),
    )


# ============================================================
# 22 — INVALID JOB MEMBER ATTACKS
# ============================================================

for index, bad_job in enumerate(
    (
        None,
        True,
        False,
        0,
        1,
        1.0,
        "",
        {},
        [],
        diamond_identity,
        diamond_contract,
        object(),
    ),
    start=1,
):

    try:

        planning.create_universal_orchestration_execution_plan(
            identity=single_identity,
            jobs=(
                bad_job,
            ),
        )

    except planning.UniversalOrchestrationExecutionPlanningError as exc:

        rejected = (
            exc.code
            == "invalid_execution_plan_job"
        )

    else:

        rejected = False

    check(
        "invalid_job_member_"
        + str(index),
        rejected,
        repr(bad_job),
    )


# ============================================================
# 23 — EMPTY JOB COLLECTION AGAINST NONEMPTY CONTRACT
# ============================================================

try:

    planning.create_universal_orchestration_execution_plan(
        identity=single_identity,
        jobs=(),
    )

except planning.UniversalOrchestrationExecutionPlanningError as exc:

    rejected = (
        exc.code
        == "missing_execution_plan_jobs"
    )

else:

    rejected = False


check(
    "empty_jobs_rejected_for_nonempty_contract",
    rejected,
)


# ============================================================
# 24 — DIRECT CONSTRUCTOR NORMALIZATION
# ============================================================

direct_plan = (
    planning.UniversalOrchestrationExecutionPlan(
        identity=diamond_identity,
        jobs=tuple(
            reversed(
                diamond_jobs
            )
        ),
    )
)


check(
    "direct_constructor_canonical_jobs",
    direct_plan.job_ids
    == (
        "a",
        "b",
        "c",
        "d",
    ),
)

check(
    "direct_constructor_same_plan",
    direct_plan
    == diamond,
)


# ============================================================
# 25 — DIRECT CONSTRUCTOR TYPE ATTACKS
# ============================================================

try:

    planning.UniversalOrchestrationExecutionPlan(
        identity=None,
        jobs=diamond_jobs,
    )

except planning.UniversalOrchestrationExecutionPlanningError as exc:

    rejected = (
        exc.code
        == "invalid_execution_plan_identity"
    )

else:

    rejected = False


check(
    "direct_identity_spoof_rejected",
    rejected,
)


try:

    planning.UniversalOrchestrationExecutionPlan(
        identity=diamond_identity,
        jobs=(
            None,
        ),
    )

except planning.UniversalOrchestrationExecutionPlanningError as exc:

    rejected = (
        exc.code
        == "invalid_execution_plan_job"
    )

else:

    rejected = False


check(
    "direct_job_spoof_rejected",
    rejected,
)


# ============================================================
# 26 — SCHEMA FORGERY
# ============================================================

for bad_schema in (
    "",
    " ",
    "v1",
    "wrong",
    "universal_orchestration_execution_planning_schema_v2",
):

    try:

        planning.UniversalOrchestrationExecutionPlan(
            identity=diamond_identity,
            jobs=diamond_jobs,
            schema_version=bad_schema,
        )

    except planning.UniversalOrchestrationExecutionPlanningError as exc:

        rejected = (
            exc.code
            == "invalid_execution_plan_schema_version"
        )

    else:

        rejected = False

    check(
        "schema_attack_"
        + repr(bad_schema),
        rejected,
    )


# ============================================================
# 27 — EXACT STORED FIELD CONTRACT
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
    "satisfied_dependency_ids",
    "unresolved_dependency_ids",
    "terminal_unsatisfied_dependency_ids",

    "ready_job_ids",
    "blocked_job_ids",
    "waiting_job_ids",
    "readiness",

    "queue_order",
    "queue_id",

    "worker_assignments",
    "worker_id",
    "lease_id",

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
# 28 — PLAN IMMUTABILITY
# ============================================================

for field in fields(
    diamond
):

    try:

        setattr(
            diamond,
            field.name,
            None,
        )

    except Exception:

        immutable = True

    else:

        immutable = False

    check(
        "immutable_field_"
        + field.name,
        immutable,
    )


# ============================================================
# 29 — MAP IMMUTABILITY
# ============================================================

for name, mapping in (
    (
        "job_map",
        diamond.job_map,
    ),
    (
        "dependency_map",
        diamond.dependency_map,
    ),
    (
        "dependent_map",
        diamond.dependent_map,
    ),
):

    check(
        name
        + "_mappingproxy",
        isinstance(
            mapping,
            MappingProxyType,
        ),
    )

    try:

        mapping[
            "a"
        ] = None

    except Exception:

        immutable = True

    else:

        immutable = False

    check(
        name
        + "_immutable",
        immutable,
    )


# ============================================================
# 30 — DERIVED TUPLES IMMUTABLE
# ============================================================

check(
    "job_ids_tuple",
    isinstance(
        diamond.job_ids,
        tuple,
    ),
)

check(
    "root_ids_tuple",
    isinstance(
        diamond.root_job_ids,
        tuple,
    ),
)

check(
    "leaf_ids_tuple",
    isinstance(
        diamond.leaf_job_ids,
        tuple,
    ),
)

check(
    "execution_waves_tuple",
    isinstance(
        diamond.execution_waves,
        tuple,
    ),
)

check(
    "every_wave_tuple",
    all(
        isinstance(
            wave,
            tuple,
        )
        for wave
        in diamond.execution_waves
    ),
)

check(
    "topological_order_tuple",
    isinstance(
        diamond.topological_order,
        tuple,
    ),
)


# ============================================================
# 31 — ORIGINAL JOBS MUST NOT BE MUTATED
# ============================================================

original_by_id = {
    job.job_id: job
    for job in diamond_jobs
}


check(
    "original_a_dependencies_unchanged",
    original_by_id[
        "a"
    ].dependency_job_ids
    == (),
)

check(
    "original_b_dependencies_unchanged",
    original_by_id[
        "b"
    ].dependency_job_ids
    == (
        "a",
    ),
)

check(
    "original_c_dependencies_unchanged",
    original_by_id[
        "c"
    ].dependency_job_ids
    == (
        "a",
    ),
)

check(
    "original_d_dependencies_unchanged",
    original_by_id[
        "d"
    ].dependency_job_ids
    == (
        "b",
        "c",
    ),
)


# ============================================================
# 32 — IDENTITY MUST BE PRESERVED
# ============================================================

check(
    "identity_preserved",
    diamond.identity
    == diamond_identity,
)

check(
    "identity_run_id_preserved",
    diamond.identity.orchestration_run_id
    == "run-diamond",
)

check(
    "identity_contract_preserved",
    diamond.identity.contract
    == diamond_contract,
)


# ============================================================
# 33 — EXPLANATION CONTRACT
# ============================================================

explanation = (
    planning
    .explain_universal_orchestration_execution_planning_v1()
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
    == "5.1.5",
)

check(
    "explanation_component",
    explanation.get(
        "component"
    )
    == "Universal Orchestration Execution Planning",
)

check(
    "explanation_version",
    explanation.get(
        "version"
    )
    == planning.UNIVERSAL_ORCHESTRATION_EXECUTION_PLANNING_VERSION,
)

check(
    "explanation_schema",
    explanation.get(
        "schema_version"
    )
    == planning.UNIVERSAL_ORCHESTRATION_EXECUTION_PLANNING_SCHEMA_VERSION,
)

check(
    "explanation_stored_fields",
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
    "graph_edge_rule",
    "dependency job to dependent job"
    in explanation.get(
        "graph_rule",
        "",
    ),
)

check(
    "complete_plan_rule",
    "exactly one"
    in explanation.get(
        "complete_plan_rule",
        "",
    ),
)

check(
    "cycle_rule",
    "rejected"
    in explanation.get(
        "cycle_rule",
        "",
    ),
)

check(
    "lexical_determinism_rule",
    "lexically"
    in explanation.get(
        "determinism_rule",
        "",
    ),
)

check(
    "priority_boundary",
    "do not determine"
    in explanation.get(
        "priority_boundary",
        "",
    ),
)

check(
    "parent_boundary",
    "does not create"
    in explanation.get(
        "parent_boundary",
        "",
    ),
)

check(
    "disconnected_allowed",
    "valid"
    in explanation.get(
        "disconnected_rule",
        "",
    ),
)

check(
    "root_definition",
    "zero dependency_job_ids"
    in explanation.get(
        "root_rule",
        "",
    ),
)

check(
    "leaf_definition",
    "no dependent jobs"
    in explanation.get(
        "leaf_rule",
        "",
    ),
)

check(
    "isolated_definition",
    "both a root and a leaf"
    in explanation.get(
        "isolated_rule",
        "",
    ),
)

check(
    "dependency_status_deferred_5_1_4",
    "5.1.4"
    in explanation.get(
        "dependency_status_boundary",
        "",
    ),
)

check(
    "readiness_deferred_5_1_6",
    "5.1.6"
    in explanation.get(
        "readiness_boundary",
        "",
    ),
)

check(
    "fan_out_deferred_5_1_8",
    "5.1.8"
    in explanation.get(
        "fan_out_boundary",
        "",
    ),
)

check(
    "fan_in_deferred_5_1_9",
    "5.1.9"
    in explanation.get(
        "fan_in_boundary",
        "",
    ),
)

check(
    "condition_deferred_5_1_10",
    "5.1.10"
    in explanation.get(
        "condition_boundary",
        "",
    ),
)

check(
    "persistence_deferred_5_1_14",
    "5.1.14"
    in explanation.get(
        "persistence_boundary",
        "",
    ),
)


# ============================================================
# 34 — PROHIBITION MATRIX
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
# 35 — IMPORT BOUNDARY
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
        "backend.server.runtime.universal_orchestration.run_identity",
    ],
    backend_imports,
)


# ============================================================
# 36 — FORBIDDEN IMPORTS
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

    "backend.server.runtime.universal_orchestration.dependency_resolution",
    "backend.server.runtime.universal_orchestration.state_model",

    "backend.server.runtime.universal_queue",
    "backend.server.runtime.universal_worker",

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
# 37 — FORBIDDEN CALLS
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

    "resolve_universal_orchestration_dependencies",
    "transition_universal_orchestration_state",

    "enqueue_job",
    "dequeue_job",
    "claim_job",

    "assign_universal_worker",
    "discover_universal_workers",

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
# 38 — NO RESPONSIBILITY BLEED IN FUNCTION NAMES
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
    "dependency_status",
    "resolve_dependency_status",

    "readiness",
    "ready_job",
    "blocked_job",
    "waiting_job",

    "transition_state",

    "coordinate_fan_out",
    "coordinate_fan_in",

    "conditional_branch",

    "enqueue",
    "dequeue",
    "claim",

    "assign_worker",
    "lease_worker",

    "register_runtime",
    "dispatch",
    "execute",

    "persist",
):

    matches = tuple(
        name
        for name
        in function_names
        if forbidden_token
        in name
    )

    check(
        "no_function_bleed_"
        + forbidden_token,
        not matches,
        matches,
    )


# ============================================================
# 39 — NO HIDDEN NON-PLANNING FIELDS
# ============================================================

source_lower = source.lower()


for forbidden_symbol in (
    "dependency_statuses:",
    "satisfied_dependency_ids:",
    "unresolved_dependency_ids:",
    "terminal_unsatisfied_dependency_ids:",

    "ready_job_ids:",
    "blocked_job_ids:",
    "waiting_job_ids:",
    "readiness:",

    "queue_order:",
    "queue_id:",

    "worker_id:",
    "lease_id:",

    "fan_out_state:",
    "fan_in_state:",

    "condition_result:",

    "orchestration_state:",

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
# 40 — STRUCTURAL PLANNER MUST NOT USE JOB PRIORITY/STATUS/TIME
# ============================================================

function_source_nodes = [
    node
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
]


structural_function_names = {
    "_build_dependency_map",
    "_build_dependent_map",
    "_build_execution_waves",
}


for function_node in function_source_nodes:

    if (
        function_node.name
        not in structural_function_names
    ):

        continue

    attributes = tuple(
        child.attr
        for child in ast.walk(
            function_node
        )
        if isinstance(
            child,
            ast.Attribute,
        )
    )

    check(
        "structural_function_no_priority_"
        + function_node.name,
        "priority"
        not in attributes,
        attributes,
    )

    check(
        "structural_function_no_status_"
        + function_node.name,
        "status"
        not in attributes,
        attributes,
    )

    check(
        "structural_function_no_created_at_"
        + function_node.name,
        "created_at"
        not in attributes,
        attributes,
    )


# ============================================================
# 41 — COMPLETE PLAN DOES NOT EVALUATE 5.1.4 STATUS AUTHORITY
# ============================================================

check(
    "dependency_resolution_module_not_imported",
    not any(
        (
            module
            == "backend.server.runtime.universal_orchestration.dependency_resolution"
            or
            module.startswith(
                "backend.server.runtime.universal_orchestration.dependency_resolution."
            )
        )
        for module
        in all_imports
    ),
)


# ============================================================
# 42 — PROTECTED MATRIX
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
# 43 — FINAL AST
# ============================================================

final_ast = ast_sha(
    PLANNING_PATH
)


check(
    "planning_ast_final",
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
        "PHASE 5.1.5 — UNIVERSAL ORCHESTRATION "
        "EXECUTION PLANNING ADVERSARIAL REGRESSION"
    ),
    "=" * 118,
    "",
    (
        "EXECUTION PLANNING AST SHA256: "
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
            "ADVERSARIAL EXECUTION PLANNING REGRESSION: "
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
        "EXECUTION PLANNING AST MODIFIED: NO",
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
        "LEXICAL TIE-BREAK DETERMINISTIC: YES",
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
            "Phase 5.1.5 Execution Planning "
            "adversarial regression failed."
        )
    )
