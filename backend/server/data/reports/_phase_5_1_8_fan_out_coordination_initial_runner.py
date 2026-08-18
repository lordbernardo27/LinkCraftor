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

FAN_OUT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_orchestration"
    / "fan_out_coordination.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_1_8_fan_out_coordination_initial_implementation.txt"
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
                "5.1.8 implementation: "
                + name
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

planning = importlib.import_module(
    "backend.server.runtime.universal_orchestration.execution_planning"
)


module_name = (
    "backend.server.runtime."
    "universal_orchestration.fan_out_coordination"
)

sys.modules.pop(
    module_name,
    None,
)

fanout = importlib.import_module(
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
    status=jobs.UniversalJobStatus.CREATED,
    parent_job_id=None,
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
        parent_job_id=parent_job_id,
        priority=priority,
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
# AUTHORITY
# ============================================================

check(
    "version_exact",
    fanout.UNIVERSAL_ORCHESTRATION_FAN_OUT_COORDINATION_VERSION
    == "universal_orchestration_fan_out_coordination_v5.1.8",
)

check(
    "schema_exact",
    fanout.UNIVERSAL_ORCHESTRATION_FAN_OUT_COORDINATION_SCHEMA_VERSION
    == "universal_orchestration_fan_out_coordination_schema_v1",
)

check(
    "hash_algorithm_exact",
    fanout.UNIVERSAL_ORCHESTRATION_FAN_OUT_GROUP_HASH_ALGORITHM
    == "sha256",
)

check(
    "classification_exact",
    tuple(
        item.value
        for item
        in fanout.UniversalOrchestrationFanOutClassification
    )
    == (
        "fan_out",
        "no_fan_out",
    ),
)


# ============================================================
# THREE-WAY FAN-OUT
# ============================================================

jobs_three = (
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
            "a",
        ),
    ),
)


plan_three = make_plan(
    jobs_tuple=jobs_three,
    run_id="fan-three",
)


result_three = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=plan_three,
        source_job_id="a",
    )
)


check(
    "three_direct_dependents_exact",
    result_three.direct_dependent_job_ids
    == (
        "b",
        "c",
        "d",
    ),
)

check(
    "three_width",
    result_three.fan_out_width
    == 3,
)

check(
    "three_is_fan_out",
    result_three.is_fan_out,
)

check(
    "three_classification",
    result_three.classification
    is fanout.UniversalOrchestrationFanOutClassification.FAN_OUT,
)

check(
    "three_has_dependents",
    result_three.has_dependents,
)

check(
    "three_jobs_exact",
    tuple(
        job.job_id
        for job
        in result_three.direct_dependent_jobs
    )
    == (
        "b",
        "c",
        "d",
    ),
)


# ============================================================
# ONE DEPENDENT
# ============================================================

jobs_one = (
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


plan_one = make_plan(
    jobs_tuple=jobs_one,
    run_id="fan-one",
)


result_one = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=plan_one,
        source_job_id="a",
    )
)


check(
    "one_dependent_exact",
    result_one.direct_dependent_job_ids
    == (
        "b",
    ),
)

check(
    "one_width",
    result_one.fan_out_width
    == 1,
)

check(
    "one_no_fan_out",
    not result_one.is_fan_out,
)

check(
    "one_classification",
    result_one.classification
    is fanout.UniversalOrchestrationFanOutClassification.NO_FAN_OUT,
)

check(
    "one_has_dependents",
    result_one.has_dependents,
)


# ============================================================
# ZERO DEPENDENTS / LEAF
# ============================================================

result_leaf = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=plan_one,
        source_job_id="b",
    )
)


check(
    "leaf_dependents_empty",
    result_leaf.direct_dependent_job_ids
    == (),
)

check(
    "leaf_width_zero",
    result_leaf.fan_out_width
    == 0,
)

check(
    "leaf_no_fan_out",
    not result_leaf.is_fan_out,
)

check(
    "leaf_has_no_dependents",
    not result_leaf.has_dependents,
)


# ============================================================
# TRANSITIVE DESCENDANT EXCLUDED
# ============================================================

jobs_transitive = (
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
        job_id="z",
        dependencies=(
            "b",
            "c",
        ),
    ),
)


plan_transitive = make_plan(
    jobs_tuple=jobs_transitive,
    run_id="fan-transitive",
)


result_transitive = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=plan_transitive,
        source_job_id="a",
    )
)


check(
    "transitive_direct_only",
    result_transitive.direct_dependent_job_ids
    == (
        "b",
        "c",
    ),
)

check(
    "transitive_descendant_excluded",
    "z"
    not in result_transitive.direct_dependent_job_ids,
)


# ============================================================
# SAME WAVE DOES NOT CREATE GROUP
# ============================================================

jobs_wave = (
    make_job(
        job_id="a",
    ),
    make_job(
        job_id="x",
    ),
    make_job(
        job_id="b",
        dependencies=(
            "a",
        ),
    ),
    make_job(
        job_id="y",
        dependencies=(
            "x",
        ),
    ),
)


plan_wave = make_plan(
    jobs_tuple=jobs_wave,
    run_id="fan-wave",
)


check(
    "wave_has_unrelated_parallel_jobs",
    plan_wave.execution_waves
    == (
        (
            "a",
            "x",
        ),
        (
            "b",
            "y",
        ),
    ),
    plan_wave.execution_waves,
)


result_wave_a = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=plan_wave,
        source_job_id="a",
    )
)


check(
    "same_wave_not_fan_out",
    result_wave_a.direct_dependent_job_ids
    == (
        "b",
    ),
)

check(
    "unrelated_wave_member_excluded",
    "y"
    not in result_wave_a.direct_dependent_job_ids,
)


# ============================================================
# INTERNAL NODE CAN FAN OUT
# ============================================================

jobs_internal = (
    make_job(
        job_id="root",
    ),
    make_job(
        job_id="middle",
        dependencies=(
            "root",
        ),
    ),
    make_job(
        job_id="left",
        dependencies=(
            "middle",
        ),
    ),
    make_job(
        job_id="right",
        dependencies=(
            "middle",
        ),
    ),
)


plan_internal = make_plan(
    jobs_tuple=jobs_internal,
    run_id="fan-internal",
)


result_internal = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=plan_internal,
        source_job_id="middle",
    )
)


check(
    "internal_node_fan_out",
    (
        result_internal.is_fan_out
        and
        result_internal.direct_dependent_job_ids
        == (
            "left",
            "right",
        )
    ),
)


# ============================================================
# PARENT_JOB_ID DOES NOT CREATE FAN-OUT
# ============================================================

jobs_parent = (
    make_job(
        job_id="a",
    ),
    make_job(
        job_id="b",
        parent_job_id="a",
    ),
    make_job(
        job_id="c",
        parent_job_id="a",
    ),
)


plan_parent = make_plan(
    jobs_tuple=jobs_parent,
    run_id="fan-parent",
)


result_parent = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=plan_parent,
        source_job_id="a",
    )
)


check(
    "parent_lineage_not_fan_out",
    result_parent.direct_dependent_job_ids
    == (),
)

check(
    "parent_lineage_class_no_fan_out",
    not result_parent.is_fan_out,
)


# ============================================================
# STATUS DOES NOT AFFECT STRUCTURE
# ============================================================

for status in jobs.UniversalJobStatus:

    status_jobs = (
        make_job(
            job_id="a",
            status=status,
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
    )

    status_plan = make_plan(
        jobs_tuple=status_jobs,
        run_id=(
            "fan-status-"
            + status.value
        ),
    )

    status_result = (
        fanout
        .coordinate_universal_orchestration_fan_out(
            execution_plan=status_plan,
            source_job_id="a",
        )
    )

    check(
        "status_does_not_change_fan_out_"
        + status.value,
        (
            status_result.is_fan_out
            and
            status_result.direct_dependent_job_ids
            == (
                "b",
                "c",
            )
        ),
    )


# ============================================================
# PRIORITY DOES NOT AFFECT STRUCTURE
# ============================================================

for priority in (
    jobs.UniversalJobPriority.CRITICAL,
    jobs.UniversalJobPriority.HIGH,
    jobs.UniversalJobPriority.NORMAL,
    jobs.UniversalJobPriority.LOW,
    jobs.UniversalJobPriority.BACKGROUND,
):

    priority_jobs = (
        make_job(
            job_id="a",
            priority=priority,
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
    )

    priority_plan = make_plan(
        jobs_tuple=priority_jobs,
        run_id=(
            "fan-priority-"
            + str(
                priority.value
            )
        ),
    )

    priority_result = (
        fanout
        .coordinate_universal_orchestration_fan_out(
            execution_plan=priority_plan,
            source_job_id="a",
        )
    )

    check(
        "priority_does_not_change_fan_out_"
        + str(
            priority.value
        ),
        priority_result.is_fan_out,
    )


# ============================================================
# SOURCE NORMALIZATION
# ============================================================

normalized_result = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=plan_three,
        source_job_id="  a  ",
    )
)


check(
    "source_outer_whitespace_normalized",
    normalized_result.source_job_id
    == "a",
)


# ============================================================
# INVALID SOURCE
# ============================================================

for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        1,
        1.0,
        "",
        " ",
        "a b",
        b"a",
        bytearray(
            b"a"
        ),
        {},
        [],
        (),
        object(),
    ),
    start=1,
):

    try:

        fanout.coordinate_universal_orchestration_fan_out(
            execution_plan=plan_three,
            source_job_id=bad,
        )

    except fanout.UniversalOrchestrationFanOutCoordinationError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_source_"
        + str(index),
        rejected,
    )


# ============================================================
# OUTSIDE PLAN
# ============================================================

try:

    fanout.coordinate_universal_orchestration_fan_out(
        execution_plan=plan_three,
        source_job_id="outside",
    )

except fanout.UniversalOrchestrationFanOutCoordinationError as exc:

    outside_rejected = (
        exc.code
        == "fan_out_source_not_in_execution_plan"
    )

else:

    outside_rejected = False


check(
    "outside_plan_source_rejected",
    outside_rejected,
)


# ============================================================
# INVALID PLAN
# ============================================================

for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        "",
        {},
        [],
        object(),
    ),
    start=1,
):

    try:

        fanout.coordinate_universal_orchestration_fan_out(
            execution_plan=bad,
            source_job_id="a",
        )

    except fanout.UniversalOrchestrationFanOutCoordinationError as exc:

        rejected = (
            exc.code
            == "invalid_fan_out_execution_plan"
        )

    else:

        rejected = False

    check(
        "invalid_plan_"
        + str(index),
        rejected,
    )


# ============================================================
# STORED FIELDS
# ============================================================

field_names = tuple(
    field.name
    for field in fields(
        fanout.UniversalOrchestrationFanOutCoordination
    )
)


check(
    "stored_fields_exact",
    field_names
    == (
        "execution_plan",
        "source_job_id",
        "schema_version",
    ),
    field_names,
)


for forbidden in (
    "identity",
    "source_job",
    "direct_dependent_job_ids",
    "direct_dependent_jobs",
    "fan_out_width",
    "classification",
    "is_fan_out",
    "has_dependents",
    "fan_out_group_id",
    "readiness",
    "handoff",
    "queue_id",
    "worker_id",
    "lease_id",
    "created_at",
    "updated_at",
    "metadata",
):

    check(
        "forbidden_stored_field_"
        + forbidden,
        forbidden
        not in field_names,
    )


# ============================================================
# IMMUTABILITY
# ============================================================

for field in fields(
    result_three
):

    try:

        setattr(
            result_three,
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
# GROUP ID DETERMINISM
# ============================================================

group_id_one = (
    result_three.fan_out_group_id
)

group_id_two = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=plan_three,
        source_job_id="a",
    )
    .fan_out_group_id
)


check(
    "group_id_length",
    len(
        group_id_one
    )
    == 64,
    group_id_one,
)

check(
    "group_id_hex",
    all(
        character
        in "0123456789ABCDEF"
        for character
        in group_id_one
    ),
)

check(
    "group_id_deterministic",
    group_id_one
    == group_id_two,
)


# ============================================================
# EXPLANATION
# ============================================================

explanation = (
    fanout
    .explain_universal_orchestration_fan_out_coordination_v1()
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
    == "5.1.8",
)

check(
    "component_exact",
    explanation.get(
        "component"
    )
    == "Universal Orchestration Fan-Out Coordination",
)

check(
    "stored_fields_explanation_exact",
    explanation.get(
        "stored_fields"
    )
    == (
        "execution_plan",
        "source_job_id",
        "schema_version",
    ),
)

check(
    "direct_edge_rule_present",
    "direct dependent edges"
    in explanation.get(
        "direct_edge_rule",
        "",
    ),
)

check(
    "wave_boundary_present",
    "execution wave"
    in explanation.get(
        "wave_boundary",
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
    "conditional_deferred_5_1_10",
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
# IMPORT BOUNDARY
# ============================================================

source = FAN_OUT_PATH.read_text(
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
# NO FORBIDDEN CALLS
# ============================================================

forbidden_calls = {
    "open",
    "read_text",
    "write_text",

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
    "create_subprocess_exec",
    "Thread",
    "Process",

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

        name = node.func.id

    elif isinstance(
        node.func,
        ast.Attribute,
    ):

        name = node.func.attr

    else:

        continue

    if name in forbidden_calls:

        found_forbidden.append(
            (
                name,
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


fan_out_ast = ast_sha(
    FAN_OUT_PATH
)


check(
    "fan_out_ast_generated",
    len(
        fan_out_ast
    )
    == 64,
    fan_out_ast,
)


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
        "PHASE 5.1.8 — UNIVERSAL ORCHESTRATION "
        "FAN-OUT COORDINATION INITIAL IMPLEMENTATION"
    ),
    "=" * 118,
    "",
    (
        "FAN-OUT COORDINATION AST SHA256: "
        + fan_out_ast
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
            "INITIAL FAN-OUT COORDINATION RESULT: "
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
        "5.1.1–5.1.7 FROZEN AUTHORITIES MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",
        "",
        "FAN-OUT CLASSIFICATIONS: FAN_OUT / NO_FAN_OUT",
        "ZERO DIRECT DEPENDENTS: NO_FAN_OUT",
        "ONE DIRECT DEPENDENT: NO_FAN_OUT",
        "TWO OR MORE DIRECT DEPENDENTS: FAN_OUT",
        "TRANSITIVE DESCENDANTS INCLUDED: NO",
        "EXECUTION-WAVE CO-MEMBERSHIP DEFINES FAN-OUT: NO",
        "PARENT_JOB_ID DEFINES FAN-OUT: NO",
        "",
        "UNIVERSAL JOB STATUS USED: NO",
        "READINESS USED: NO",
        "RUNTIME HANDOFF ELIGIBILITY USED: NO",
        "JOB PRIORITY USED: NO",
        "WORKER/QUEUE/LEASE ELIGIBILITY USED: NO",
        "",
        "CHILD JOBS ENQUEUED/SCHEDULED/CLAIMED: NO",
        "WORKERS ASSIGNED: NO",
        "LEASES ACQUIRED: NO",
        "HANDLERS DISPATCHED: NO",
        "JOBS EXECUTED IN PARALLEL: NO",
        "THREADS/PROCESSES/TASKS CREATED: NO",
        "UNIVERSAL JOB STATUS MUTATED: NO",
        "ORCHESTRATION STATE TRANSITIONED: NO",
        "FAN-IN/JOIN COORDINATED: NO",
        "CONDITIONAL BRANCHES EVALUATED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "FAN-OUT DECISION PERSISTED: NO",
        "UNIVERSAL COORDINATION FRAMEWORK ACCESSED: NO",
        "PIPELINE COORDINATORS ACCESSED: NO",
        "WALL CLOCK USED: NO",
        "FILESYSTEM/NETWORK I/O: NO",
        "",
        (
            "STATUS: INITIAL IMPLEMENTATION PASS "
            "— ADVERSARIAL REGRESSION REQUIRED"
            if passed == total
            else
            "STATUS: INITIAL IMPLEMENTATION FAILED"
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
            "Phase 5.1.8 Fan-Out Coordination "
            "initial implementation failed."
        )
    )
