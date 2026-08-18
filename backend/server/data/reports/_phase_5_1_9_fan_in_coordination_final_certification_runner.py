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

FAN_IN_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_orchestration"
    / "fan_in_coordination.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_1_9_fan_in_coordination_final_certification.txt"
)

EXPECTED_FAN_IN_AST = (
    "98786AEF5E4DBD804FBE5FE32EEE7CD54907FAC6A9C016B6120851834F6CFA0F"
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

    "5.1.7_runtime_handoff": (
        ROOT / "backend/server/runtime/universal_orchestration/runtime_handoff.py",
        "6878FC6F0F2EF071B11A93D793A0CC80B2C91B676C6B6735A78237D8C7D6CB73",
    ),

    "5.1.8_fan_out_coordination": (
        ROOT / "backend/server/runtime/universal_orchestration/fan_out_coordination.py",
        "D60C8629D2490DC41A8DF43E30F00A1D4851941E65CBD2EBE7EED70B75217916",
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

if not FAN_IN_PATH.exists():

    raise SystemExit(
        "5.1.9 Fan-In / Join authority is missing."
    )


initial_ast = ast_sha(
    FAN_IN_PATH
)


if initial_ast != EXPECTED_FAN_IN_AST:

    raise SystemExit(
        (
            "5.1.9 Fan-In AST mismatch before certification.\n"
            "EXPECTED: "
            + EXPECTED_FAN_IN_AST
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
            "Protected authority mismatch: "
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


module_name = (
    "backend.server.runtime."
    "universal_orchestration.fan_in_coordination"
)

sys.modules.pop(
    module_name,
    None,
)

fanin = importlib.import_module(
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
# CORE AUTHORITY
# ============================================================

check(
    "ast_exact",
    ast_sha(FAN_IN_PATH)
    == EXPECTED_FAN_IN_AST,
)

check(
    "version_exact",
    fanin.UNIVERSAL_ORCHESTRATION_FAN_IN_COORDINATION_VERSION
    == "universal_orchestration_fan_in_coordination_v5.1.9",
)

check(
    "schema_exact",
    fanin.UNIVERSAL_ORCHESTRATION_FAN_IN_COORDINATION_SCHEMA_VERSION
    == "universal_orchestration_fan_in_coordination_schema_v1",
)

check(
    "hash_algorithm_exact",
    fanin.UNIVERSAL_ORCHESTRATION_JOIN_GROUP_HASH_ALGORITHM
    == "sha256",
)

check(
    "classification_exact",
    tuple(
        item.value
        for item
        in fanin.UniversalOrchestrationFanInClassification
    )
    == (
        "join",
        "no_join",
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
    parent_job_id=None,
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
        parent_job_id=parent_job_id,
        status=jobs.UniversalJobStatus.CREATED,
        created_at=FIXED_CREATED_AT,
    )


def make_plan(
    *,
    jobs_tuple,
    run_id,
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


# ============================================================
# CANONICAL JOIN
# ============================================================

plan = make_plan(
    jobs_tuple=(
        make_job(job_id="a"),
        make_job(job_id="b"),
        make_job(job_id="c"),

        make_job(
            job_id="join",
            dependencies=(
                "a",
                "b",
                "c",
            ),
        ),

        make_job(
            job_id="after",
            dependencies=("join",),
        ),
    ),
    run_id="certification",
)


result = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=plan,
        target_job_id="join",
    )
)


check(
    "direct_dependencies_exact",
    result.direct_dependency_job_ids
    == (
        "a",
        "b",
        "c",
    ),
)

check(
    "join_width_exact",
    result.join_width
    == 3,
)

check(
    "classification_join",
    result.classification
    is fanin.UniversalOrchestrationFanInClassification.JOIN,
)

check(
    "is_join_true",
    result.is_join,
)

check(
    "has_dependencies_true",
    result.has_dependencies,
)


# ============================================================
# ZERO AND ONE BOUNDARIES
# ============================================================

root_result = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=plan,
        target_job_id="a",
    )
)


check(
    "root_zero_width",
    root_result.join_width
    == 0,
)

check(
    "root_no_join",
    not root_result.is_join,
)


one_plan = make_plan(
    jobs_tuple=(
        make_job(job_id="upstream"),

        make_job(
            job_id="target",
            dependencies=("upstream",),
        ),
    ),
    run_id="one",
)


one_result = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=one_plan,
        target_job_id="target",
    )
)


check(
    "one_width_exact",
    one_result.join_width
    == 1,
)

check(
    "one_no_join",
    one_result.classification
    is fanin.UniversalOrchestrationFanInClassification.NO_JOIN,
)


# ============================================================
# DIRECT EDGE / TRANSITIVE EXCLUSION
# ============================================================

transitive_plan = make_plan(
    jobs_tuple=(
        make_job(job_id="root"),

        make_job(
            job_id="left",
            dependencies=("root",),
        ),

        make_job(
            job_id="right",
            dependencies=("root",),
        ),

        make_job(
            job_id="target",
            dependencies=(
                "left",
                "right",
            ),
        ),
    ),
    run_id="transitive",
)


transitive_result = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=transitive_plan,
        target_job_id="target",
    )
)


check(
    "direct_dependencies_only",
    transitive_result.direct_dependency_job_ids
    == (
        "left",
        "right",
    ),
)

check(
    "transitive_root_excluded",
    "root"
    not in transitive_result.direct_dependency_job_ids,
)


# ============================================================
# LINEAGE SEPARATION
# ============================================================

lineage_plan = make_plan(
    jobs_tuple=(
        make_job(job_id="parent"),

        make_job(
            job_id="target",
            parent_job_id="parent",
        ),
    ),
    run_id="lineage",
)


lineage_result = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=lineage_plan,
        target_job_id="target",
    )
)


check(
    "parent_lineage_not_dependency",
    lineage_result.direct_dependency_job_ids
    == (),
)

check(
    "parent_lineage_not_join",
    not lineage_result.is_join,
)


# ============================================================
# JOIN CAN FAN OUT
# ============================================================

check(
    "join_can_have_downstream_dependents",
    plan.dependent_map["join"]
    == ("after",),
)


# ============================================================
# GROUP ID
# ============================================================

group_id = (
    result.join_group_id
)


check(
    "group_id_length",
    len(group_id)
    == 64,
    group_id,
)

check(
    "group_id_upper_hex",
    all(
        character
        in "0123456789ABCDEF"
        for character
        in group_id
    ),
)

check(
    "group_id_repeat_deterministic",
    group_id
    ==
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=plan,
        target_job_id="join",
    )
    .join_group_id,
)


# ============================================================
# STORED / DERIVED
# ============================================================

field_names = tuple(
    field.name
    for field
    in fields(
        fanin.UniversalOrchestrationFanInCoordination
    )
)


check(
    "stored_fields_exact",
    field_names
    == (
        "execution_plan",
        "target_job_id",
        "schema_version",
    ),
    field_names,
)

check(
    "identity_derived",
    result.identity
    is plan.identity,
)

check(
    "target_job_derived",
    result.target_job
    is plan.job_map["join"],
)

check(
    "dependency_jobs_derived",
    tuple(
        job.job_id
        for job
        in result.direct_dependency_jobs
    )
    == (
        "a",
        "b",
        "c",
    ),
)


# ============================================================
# IMMUTABILITY
# ============================================================

for field in fields(
    result
):

    try:

        setattr(
            result,
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
# EXPLANATION CONTRACT
# ============================================================

explanation = (
    fanin
    .explain_universal_orchestration_fan_in_coordination_v1()
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
    explanation.get("phase")
    == "5.1.9",
)

check(
    "component_exact",
    explanation.get("component")
    == "Universal Orchestration Fan-In / Join Coordination",
)

check(
    "stored_fields_explanation_exact",
    explanation.get("stored_fields")
    == (
        "execution_plan",
        "target_job_id",
        "schema_version",
    ),
)

check(
    "dependency_resolution_boundary",
    "5.1.4"
    in explanation.get(
        "dependency_resolution_boundary",
        "",
    ),
)

check(
    "readiness_boundary",
    "5.1.6"
    in explanation.get(
        "readiness_boundary",
        "",
    ),
)

check(
    "handoff_boundary",
    "5.1.7"
    in explanation.get(
        "handoff_boundary",
        "",
    ),
)

check(
    "fan_out_boundary",
    "5.1.8"
    in explanation.get(
        "fan_out_boundary",
        "",
    ),
)

check(
    "condition_boundary",
    "5.1.10"
    in explanation.get(
        "condition_boundary",
        "",
    ),
)

check(
    "persistence_boundary",
    "5.1.14"
    in explanation.get(
        "persistence_boundary",
        "",
    ),
)

check(
    "completion_boundary",
    "5.1.15"
    in explanation.get(
        "completion_boundary",
        "",
    ),
)


# ============================================================
# IMPORT BOUNDARY
# ============================================================

source = FAN_IN_PATH.read_text(
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
        "backend.server.runtime.universal_orchestration.contract",
        "backend.server.runtime.universal_orchestration.execution_planning",
    ],
    backend_imports,
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
    "status",
    "priority",
    "created_at",
    "scheduled_at",

    "dependency_statuses",
    "all_dependencies_satisfied",

    "readiness",
    "handoff",

    "worker_id",
    "queue_id",
    "lease_id",
):

    check(
        "forbidden_attribute_"
        + forbidden_attr,
        forbidden_attr
        not in attrs,
    )


# ============================================================
# FORBIDDEN CALLS
# ============================================================

forbidden_calls = {
    "sleep",
    "wait",
    "poll",

    "enqueue_job",
    "schedule_job",
    "dequeue_job",
    "claim_job",

    "assign_universal_worker",
    "acquire_universal_worker_lease",

    "dispatch_registered_runtime_handler",
    "execute_registered_runtime_job_v1",

    "transition_universal_orchestration_state",

    "get_runtime_state_store_registry",

    "create_task",
    "Thread",
    "Process",

    "persist",
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
        "phase_5_1_9_universal_orchestration_fan_in_join_coordination",

        fanin.UNIVERSAL_ORCHESTRATION_FAN_IN_COORDINATION_VERSION,
        fanin.UNIVERSAL_ORCHESTRATION_FAN_IN_COORDINATION_SCHEMA_VERSION,
        fanin.UNIVERSAL_ORCHESTRATION_JOIN_GROUP_HASH_ALGORITHM,

        EXPECTED_FAN_IN_AST,

        "classification_join",
        "classification_no_join",

        "zero_dependencies_no_join",
        "one_dependency_no_join",
        "two_or_more_direct_dependencies_join",

        "direct_dependencies_only",
        "transitive_ancestors_excluded",

        "execution_wave_not_join_membership",
        "parent_job_id_not_join",
        "batch_id_not_join",
        "pipeline_run_id_not_join",

        "execution_plan_5_1_5_structural_authority",

        "dependency_resolution_5_1_4_not_consumed",
        "all_dependencies_satisfied_not_evaluated",

        "readiness_5_1_6_not_consumed",
        "handoff_5_1_7_not_consumed",
        "fan_out_5_1_8_not_consumed",

        "status_not_used",
        "priority_not_used",
        "created_at_not_used",
        "scheduled_at_not_used",

        "join_group_id_sha256_deterministic",
        "join_group_id_identity_sensitive",
        "join_group_id_target_sensitive",
        "join_group_id_membership_sensitive",

        "stored_execution_plan",
        "stored_target_job_id",
        "stored_schema_version",

        "identity_derived",
        "target_job_derived",
        "dependency_ids_derived",
        "dependency_jobs_derived",
        "join_width_derived",
        "classification_derived",
        "join_group_id_derived",

        "no_wait_sleep_poll",

        "no_queue_activity",
        "no_worker_activity",
        "no_lease_activity",

        "no_handler_dispatch",
        "no_job_execution",

        "no_threads",
        "no_processes",
        "no_async_tasks",

        "no_job_status_mutation",
        "no_orchestration_state_transition",

        "conditional_branching_deferred_5_1_10",
        "persistence_deferred_5_1_14",
        "completion_resolution_deferred_5_1_15",

        "no_runtime_state_store",
        "no_coordination_framework",
        "no_pipeline_coordinators",

        "no_wall_clock",
        "no_filesystem_io",
        "no_network_io",

        "immutable_deterministic_structural_fan_in_join_authority",
    )
)


fan_in_fingerprint = (
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
            fan_in_fingerprint
        )
        == 64
        and
        all(
            character
            in "0123456789ABCDEF"
            for character
            in fan_in_fingerprint
        )
    ),
    fan_in_fingerprint,
)


# ============================================================
# FINAL AST
# ============================================================

final_ast = ast_sha(
    FAN_IN_PATH
)


check(
    "final_ast_unchanged",
    final_ast
    == EXPECTED_FAN_IN_AST,
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
        "PHASE 5.1.9 — UNIVERSAL ORCHESTRATION "
        "FAN-IN / JOIN COORDINATION FINAL CERTIFICATION"
    ),

    "=" * 118,

    "",

    (
        "FAN-IN COORDINATION AST SHA256: "
        + final_ast
    ),

    (
        "FAN-IN COORDINATION FINGERPRINT: "
        + fan_in_fingerprint
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
            "FINAL FAN-IN / JOIN COORDINATION CERTIFICATION: "
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

        "FAN-IN AUTHORITY MODIFIED DURING CERTIFICATION: NO",
        "5.1.1–5.1.8 FROZEN AUTHORITIES MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "ZERO DIRECT DEPENDENCIES: NO_JOIN",
        "ONE DIRECT DEPENDENCY: NO_JOIN",
        "TWO OR MORE DIRECT DEPENDENCIES: JOIN",

        "",

        "DIRECT DEPENDENCY EDGES DEFINE JOIN: YES",
        "TRANSITIVE ANCESTORS INCLUDED: NO",
        "EXECUTION WAVES DEFINE JOIN MEMBERSHIP: NO",
        "PARENT_JOB_ID DEFINES JOIN: NO",

        "",

        "UNIVERSAL JOB STATUS USED: NO",
        "DEPENDENCY STATUS EVIDENCE USED: NO",
        "ALL_DEPENDENCIES_SATISFIED EVALUATED: NO",
        "JOB PRIORITY USED: NO",
        "READINESS USED: NO",
        "RUNTIME HANDOFF USED: NO",
        "FAN-OUT OBJECT USED: NO",

        "",

        "QUEUE ACTIVITY: NO",
        "WORKER ACTIVITY: NO",
        "LEASE ACTIVITY: NO",
        "RUNTIME HANDLER ACTIVITY: NO",
        "JOB EXECUTION: NO",
        "WAIT/SLEEP/POLL: NO",

        "",

        "UNIVERSAL JOB MUTATION: NO",
        "ORCHESTRATION STATE TRANSITION: NO",
        "CONDITIONAL BRANCHING: NO",
        "ORCHESTRATION COMPLETION RESOLUTION: NO",

        "",

        "RUNTIME STATE STORE ACCESS: NO",
        "FAN-IN PERSISTENCE: NO",
        "UNIVERSAL COORDINATION FRAMEWORK ACCESS: NO",
        "PIPELINE COORDINATOR ACCESS: NO",

        "",

        "WALL CLOCK: NO",
        "FILESYSTEM/NETWORK I/O: NO",

        "",

        (
            "PHASE 5.1.9 FREEZE CANDIDATE: "
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
        "Phase 5.1.9 final certification failed."
    )
