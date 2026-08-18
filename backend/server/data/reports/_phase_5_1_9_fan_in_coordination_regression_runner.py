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
    / "phase_5_1_9_fan_in_coordination_regression.txt"
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
        "5.1.9 Fan-In authority is missing."
    )


if ast_sha(FAN_IN_PATH) != EXPECTED_FAN_IN_AST:

    raise SystemExit(
        (
            "5.1.9 AST changed before adversarial regression.\n"
            "EXPECTED: "
            + EXPECTED_FAN_IN_AST
            + "\nACTUAL:   "
            + ast_sha(FAN_IN_PATH)
        )
    )


for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(path)

    if actual != expected:

        raise SystemExit(
            "Protected authority changed before 5.1.9 regression: "
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
        parent_job_id=parent_job_id,
        status=status,
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
# 1. AUTHORITY / PUBLIC API
# ============================================================

check(
    "ast_initial_exact",
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


expected_all = (
    "UNIVERSAL_ORCHESTRATION_FAN_IN_COORDINATION_VERSION",
    "UNIVERSAL_ORCHESTRATION_FAN_IN_COORDINATION_SCHEMA_VERSION",
    "UNIVERSAL_ORCHESTRATION_JOIN_GROUP_HASH_ALGORITHM",
    "UniversalOrchestrationFanInCoordinationError",
    "UniversalOrchestrationFanInClassification",
    "classify_universal_orchestration_fan_in",
    "calculate_universal_orchestration_join_group_id",
    "UniversalOrchestrationFanInCoordination",
    "coordinate_universal_orchestration_fan_in",
    "explain_universal_orchestration_fan_in_coordination_v1",
)


check(
    "public_api_exact",
    tuple(fanin.__all__)
    == expected_all,
    fanin.__all__,
)


# ============================================================
# 2. JOIN WIDTH MATRIX 0..10
# ============================================================

for width in range(
    0,
    11,
):

    upstream = tuple(
        make_job(
            job_id=f"upstream-{index:02d}",
        )
        for index
        in range(width)
    )

    target = make_job(
        job_id="target",
        dependencies=tuple(
            job.job_id
            for job
            in upstream
        ),
    )

    plan = make_plan(
        jobs_tuple=(
            *upstream,
            target,
        ),
        run_id=f"join-width-{width}",
    )

    result = (
        fanin
        .coordinate_universal_orchestration_fan_in(
            execution_plan=plan,
            target_job_id="target",
        )
    )

    expected_ids = tuple(
        f"upstream-{index:02d}"
        for index
        in range(width)
    )

    check(
        f"width_{width}_members_exact",
        result.direct_dependency_job_ids
        == expected_ids,
    )

    check(
        f"width_{width}_count_exact",
        result.join_width
        == width,
    )

    check(
        f"width_{width}_classification_exact",
        result.is_join
        == (width >= 2),
    )

    check(
        f"width_{width}_has_dependencies_exact",
        result.has_dependencies
        == (width > 0),
    )


# ============================================================
# 3. LEXICAL ORDERING
# ============================================================

lexical_plan = make_plan(
    jobs_tuple=(
        make_job(job_id="zeta"),
        make_job(job_id="alpha"),
        make_job(job_id="middle"),

        make_job(
            job_id="target",
            dependencies=(
                "zeta",
                "alpha",
                "middle",
            ),
        ),
    ),
    run_id="join-lexical",
)


lexical_result = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=lexical_plan,
        target_job_id="target",
    )
)


check(
    "lexical_dependencies_exact",
    lexical_result.direct_dependency_job_ids
    == (
        "alpha",
        "middle",
        "zeta",
    ),
)


# ============================================================
# 4. TRANSITIVE ANCESTORS MUST NOT APPEAR
# ============================================================

deep_plan = make_plan(
    jobs_tuple=(
        make_job(
            job_id="root",
        ),

        make_job(
            job_id="left-parent",
            dependencies=("root",),
        ),

        make_job(
            job_id="right-parent",
            dependencies=("root",),
        ),

        make_job(
            job_id="left",
            dependencies=("left-parent",),
        ),

        make_job(
            job_id="right",
            dependencies=("right-parent",),
        ),

        make_job(
            job_id="target",
            dependencies=(
                "left",
                "right",
            ),
        ),
    ),
    run_id="join-deep",
)


deep_result = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=deep_plan,
        target_job_id="target",
    )
)


check(
    "deep_direct_dependencies_exact",
    deep_result.direct_dependency_job_ids
    == (
        "left",
        "right",
    ),
)


for transitive in (
    "root",
    "left-parent",
    "right-parent",
):

    check(
        "transitive_ancestor_excluded_"
        + transitive,
        transitive
        not in deep_result.direct_dependency_job_ids,
    )


# ============================================================
# 5. SAME EXECUTION WAVE DOES NOT DEFINE JOIN
# ============================================================

wave_plan = make_plan(
    jobs_tuple=(
        make_job(job_id="a"),
        make_job(job_id="x"),

        make_job(
            job_id="b",
            dependencies=("a",),
        ),

        make_job(
            job_id="y",
            dependencies=("x",),
        ),

        make_job(
            job_id="target-a",
            dependencies=("b",),
        ),

        make_job(
            job_id="target-x",
            dependencies=("y",),
        ),
    ),
    run_id="join-wave",
)


check(
    "wave_structure_expected",
    wave_plan.execution_waves
    == (
        ("a", "x"),
        ("b", "y"),
        ("target-a", "target-x"),
    ),
    wave_plan.execution_waves,
)


target_a_result = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=wave_plan,
        target_job_id="target-a",
    )
)


check(
    "same_wave_not_join_membership",
    target_a_result.direct_dependency_job_ids
    == ("b",),
)

check(
    "unrelated_same_wave_dependency_excluded",
    "y"
    not in target_a_result.direct_dependency_job_ids,
)


# ============================================================
# 6. PARENT_JOB_ID DOES NOT DEFINE JOIN
# ============================================================

lineage_plan = make_plan(
    jobs_tuple=(
        make_job(job_id="a"),
        make_job(job_id="b"),

        make_job(
            job_id="target",
            parent_job_id="a",
        ),
    ),
    run_id="join-lineage",
)


lineage_result = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=lineage_plan,
        target_job_id="target",
    )
)


check(
    "parent_lineage_zero_dependencies",
    lineage_result.direct_dependency_job_ids
    == (),
)

check(
    "parent_lineage_no_join",
    not lineage_result.is_join,
)


# ============================================================
# 7. DIAMOND FAN-OUT / FAN-IN
# ============================================================

diamond_plan = make_plan(
    jobs_tuple=(
        make_job(job_id="a"),

        make_job(
            job_id="b",
            dependencies=("a",),
        ),

        make_job(
            job_id="c",
            dependencies=("a",),
        ),

        make_job(
            job_id="d",
            dependencies=(
                "b",
                "c",
            ),
        ),
    ),
    run_id="join-diamond",
)


diamond_result = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=diamond_plan,
        target_job_id="d",
    )
)


check(
    "diamond_join_exact",
    (
        diamond_result.is_join
        and
        diamond_result.join_width == 2
        and
        diamond_result.direct_dependency_job_ids
        == (
            "b",
            "c",
        )
    ),
)


# ============================================================
# 8. INTERNAL JOIN THAT FANS OUT AGAIN
# ============================================================

join_then_fan_plan = make_plan(
    jobs_tuple=(
        make_job(job_id="a"),
        make_job(job_id="b"),

        make_job(
            job_id="join",
            dependencies=(
                "a",
                "b",
            ),
        ),

        make_job(
            job_id="left",
            dependencies=("join",),
        ),

        make_job(
            job_id="right",
            dependencies=("join",),
        ),
    ),
    run_id="join-then-fan",
)


join_then_fan = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=join_then_fan_plan,
        target_job_id="join",
    )
)


check(
    "join_can_have_dependents",
    join_then_fan.is_join,
)

check(
    "join_target_can_fan_out_later",
    join_then_fan_plan.dependent_map["join"]
    == (
        "left",
        "right",
    ),
)


# ============================================================
# 9. TARGET STATUS IRRELEVANCE
# ============================================================

for status in jobs.UniversalJobStatus:

    plan = make_plan(
        jobs_tuple=(
            make_job(job_id="a"),
            make_job(job_id="b"),

            make_job(
                job_id="target",
                dependencies=(
                    "a",
                    "b",
                ),
                status=status,
            ),
        ),
        run_id=(
            "target-status-"
            + status.value
        ),
    )

    result = (
        fanin
        .coordinate_universal_orchestration_fan_in(
            execution_plan=plan,
            target_job_id="target",
        )
    )

    check(
        "target_status_irrelevant_"
        + status.value,
        (
            result.is_join
            and
            result.join_width == 2
        ),
    )


# ============================================================
# 10. UPSTREAM STATUS IRRELEVANCE
# ============================================================

for status in jobs.UniversalJobStatus:

    plan = make_plan(
        jobs_tuple=(
            make_job(
                job_id="a",
                status=status,
            ),

            make_job(
                job_id="b",
                status=status,
            ),

            make_job(
                job_id="target",
                dependencies=(
                    "a",
                    "b",
                ),
            ),
        ),
        run_id=(
            "upstream-status-"
            + status.value
        ),
    )

    result = (
        fanin
        .coordinate_universal_orchestration_fan_in(
            execution_plan=plan,
            target_job_id="target",
        )
    )

    check(
        "upstream_status_irrelevant_"
        + status.value,
        result.is_join,
    )


# ============================================================
# 11. PRIORITY IRRELEVANCE
# ============================================================

for priority in jobs.UniversalJobPriority:

    plan = make_plan(
        jobs_tuple=(
            make_job(job_id="a"),
            make_job(job_id="b"),

            make_job(
                job_id="target",
                dependencies=(
                    "a",
                    "b",
                ),
                priority=priority,
            ),
        ),
        run_id=(
            "join-priority-"
            + str(priority.value)
        ),
    )

    result = (
        fanin
        .coordinate_universal_orchestration_fan_in(
            execution_plan=plan,
            target_job_id="target",
        )
    )

    check(
        "priority_irrelevant_"
        + str(priority.value),
        result.is_join,
    )


# ============================================================
# 12. TARGET IDENTIFIER NORMALIZATION
# ============================================================

normalization_plan = make_plan(
    jobs_tuple=(
        make_job(job_id="a"),
        make_job(job_id="b"),

        make_job(
            job_id="target",
            dependencies=(
                "a",
                "b",
            ),
        ),
    ),
    run_id="join-normalization",
)


for raw in (
    "target",
    " target",
    "target ",
    "  target  ",
    "\ttarget\t",
    "\ntarget\n",
):

    result = (
        fanin
        .coordinate_universal_orchestration_fan_in(
            execution_plan=normalization_plan,
            target_job_id=raw,
        )
    )

    check(
        "normalized_target_"
        + repr(raw),
        result.target_job_id
        == "target",
    )


# ============================================================
# 13. INVALID TARGET ATTACKS
# ============================================================

invalid_targets = (
    None,
    True,
    False,

    0,
    1,
    -1,
    1.0,

    float("inf"),

    "",
    " ",
    "\t",
    "\n",

    "target other",
    "target\tother",
    "target\nother",

    b"target",
    bytearray(b"target"),

    {},
    [],
    (),
    set(),

    object(),
)


for index, bad in enumerate(
    invalid_targets,
    start=1,
):

    try:

        fanin.coordinate_universal_orchestration_fan_in(
            execution_plan=normalization_plan,
            target_job_id=bad,
        )

    except fanin.UniversalOrchestrationFanInCoordinationError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_target_attack_"
        + str(index),
        rejected,
        repr(bad),
    )


# ============================================================
# 14. TOO-LONG TARGET
# ============================================================

too_long = (
    "x" * 201
)


try:

    fanin.coordinate_universal_orchestration_fan_in(
        execution_plan=normalization_plan,
        target_job_id=too_long,
    )

except fanin.UniversalOrchestrationFanInCoordinationError:

    too_long_rejected = True

else:

    too_long_rejected = False


check(
    "too_long_target_rejected",
    too_long_rejected,
)


# ============================================================
# 15. TARGET OUTSIDE PLAN
# ============================================================

for outside in (
    "outside",
    "missing",
    "not-in-plan",
):

    try:

        fanin.coordinate_universal_orchestration_fan_in(
            execution_plan=normalization_plan,
            target_job_id=outside,
        )

    except fanin.UniversalOrchestrationFanInCoordinationError as exc:

        rejected = (
            exc.code
            == "fan_in_target_not_in_execution_plan"
        )

    else:

        rejected = False

    check(
        "outside_target_rejected_"
        + outside,
        rejected,
    )


# ============================================================
# 16. INVALID EXECUTION PLAN ATTACKS
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
        (),
        [],
        {},
        set(),

        object(),
    ),
    start=1,
):

    try:

        fanin.coordinate_universal_orchestration_fan_in(
            execution_plan=bad,
            target_job_id="target",
        )

    except fanin.UniversalOrchestrationFanInCoordinationError as exc:

        rejected = (
            exc.code
            == "invalid_fan_in_execution_plan"
        )

    else:

        rejected = False

    check(
        "invalid_plan_attack_"
        + str(index),
        rejected,
    )


# ============================================================
# 17. STORED FIELD CONTRACT
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


for forbidden in (
    "identity",
    "target_job",

    "direct_dependency_job_ids",
    "direct_dependency_jobs",

    "join_width",
    "classification",
    "is_join",
    "has_dependencies",

    "join_group_id",

    "dependency_resolution",
    "dependency_statuses",
    "all_dependencies_satisfied",

    "readiness",
    "handoff",
    "fan_out",

    "status",
    "priority",

    "queue_id",
    "worker_id",
    "lease_id",

    "handler",
    "dispatch_result",
    "execution_result",

    "condition",
    "completion",

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
# 18. IMMUTABILITY
# ============================================================

immutable_result = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=normalization_plan,
        target_job_id="target",
    )
)


for field in fields(
    immutable_result
):

    try:

        setattr(
            immutable_result,
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
# 19. DERIVED PROPERTIES
# ============================================================

check(
    "identity_derived",
    immutable_result.identity
    is normalization_plan.identity,
)

check(
    "target_job_derived",
    immutable_result.target_job
    is normalization_plan.job_map["target"],
)

check(
    "dependency_jobs_derived",
    tuple(
        job.job_id
        for job
        in immutable_result.direct_dependency_jobs
    )
    == (
        "a",
        "b",
    ),
)

check(
    "dependency_objects_are_plan_objects",
    all(
        job
        is normalization_plan.job_map[
            job.job_id
        ]
        for job
        in immutable_result.direct_dependency_jobs
    ),
)


# ============================================================
# 20. GROUP ID REPEAT DETERMINISM
# ============================================================

group_ids = tuple(
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=normalization_plan,
        target_job_id="target",
    )
    .join_group_id
    for _
    in range(20)
)


check(
    "join_group_id_repeat_exact",
    len(
        set(group_ids)
    )
    == 1,
)

check(
    "join_group_id_length_64",
    len(group_ids[0])
    == 64,
    group_ids[0],
)

check(
    "join_group_id_upper_hex",
    all(
        character
        in "0123456789ABCDEF"
        for character
        in group_ids[0]
    ),
)


# ============================================================
# 21. GROUP ID RUN IDENTITY SENSITIVITY
# ============================================================

run_plan_a = make_plan(
    jobs_tuple=(
        make_job(job_id="a"),
        make_job(job_id="b"),

        make_job(
            job_id="target",
            dependencies=(
                "a",
                "b",
            ),
        ),
    ),
    run_id="join-run-a",
)


run_plan_b = make_plan(
    jobs_tuple=(
        make_job(job_id="a"),
        make_job(job_id="b"),

        make_job(
            job_id="target",
            dependencies=(
                "a",
                "b",
            ),
        ),
    ),
    run_id="join-run-b",
)


run_id_a = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=run_plan_a,
        target_job_id="target",
    )
    .join_group_id
)


run_id_b = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=run_plan_b,
        target_job_id="target",
    )
    .join_group_id
)


check(
    "join_group_id_run_sensitive",
    run_id_a
    != run_id_b,
)


# ============================================================
# 22. GROUP ID TARGET SENSITIVITY
# ============================================================

multi_target_plan = make_plan(
    jobs_tuple=(
        make_job(job_id="a"),
        make_job(job_id="b"),

        make_job(
            job_id="target-one",
            dependencies=(
                "a",
                "b",
            ),
        ),

        make_job(
            job_id="target-two",
            dependencies=(
                "a",
                "b",
            ),
        ),
    ),
    run_id="join-multi-target",
)


target_one_group = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=multi_target_plan,
        target_job_id="target-one",
    )
    .join_group_id
)


target_two_group = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=multi_target_plan,
        target_job_id="target-two",
    )
    .join_group_id
)


check(
    "join_group_id_target_sensitive",
    target_one_group
    != target_two_group,
)


# ============================================================
# 23. GROUP ID DEPENDENCY MEMBERSHIP SENSITIVITY
# ============================================================

membership_plan_one = make_plan(
    jobs_tuple=(
        make_job(job_id="a"),
        make_job(job_id="b"),

        make_job(
            job_id="target",
            dependencies=(
                "a",
                "b",
            ),
        ),
    ),
    run_id="join-membership",
)


membership_plan_two = make_plan(
    jobs_tuple=(
        make_job(job_id="a"),
        make_job(job_id="b"),
        make_job(job_id="c"),

        make_job(
            job_id="target",
            dependencies=(
                "a",
                "b",
                "c",
            ),
        ),
    ),
    run_id="join-membership",
)


membership_group_one = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=membership_plan_one,
        target_job_id="target",
    )
    .join_group_id
)


membership_group_two = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=membership_plan_two,
        target_job_id="target",
    )
    .join_group_id
)


check(
    "join_group_id_membership_sensitive",
    membership_group_one
    != membership_group_two,
)


# ============================================================
# 24. REPEATED EVALUATION EQUALITY
# ============================================================

repeat_one = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=normalization_plan,
        target_job_id="target",
    )
)

repeat_two = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=normalization_plan,
        target_job_id="target",
    )
)


check(
    "repeat_objects_equal",
    repeat_one
    == repeat_two,
)

check(
    "repeat_width_equal",
    repeat_one.join_width
    == repeat_two.join_width,
)

check(
    "repeat_classification_equal",
    repeat_one.classification
    is repeat_two.classification,
)

check(
    "repeat_group_id_equal",
    repeat_one.join_group_id
    == repeat_two.join_group_id,
)


# ============================================================
# 25. EXECUTION PLAN MUST NOT MUTATE
# ============================================================

plan_before = (
    normalization_plan.job_ids,
    normalization_plan.dependency_map,
    normalization_plan.dependent_map,
    normalization_plan.execution_waves,
    normalization_plan.topological_order,
)


_ = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=normalization_plan,
        target_job_id="target",
    )
)


plan_after = (
    normalization_plan.job_ids,
    normalization_plan.dependency_map,
    normalization_plan.dependent_map,
    normalization_plan.execution_waves,
    normalization_plan.topological_order,
)


check(
    "execution_plan_not_mutated",
    plan_before
    == plan_after,
)


# ============================================================
# 26. EXPLANATION CONTRACT
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
    "explanation_phase_exact",
    explanation.get("phase")
    == "5.1.9",
)

check(
    "explanation_component_exact",
    explanation.get("component")
    == "Universal Orchestration Fan-In / Join Coordination",
)

check(
    "explanation_stored_fields_exact",
    explanation.get("stored_fields")
    == (
        "execution_plan",
        "target_job_id",
        "schema_version",
    ),
)

check(
    "explanation_join_rule",
    "two or more direct dependencies"
    in explanation.get(
        "join_rule",
        "",
    ),
)

check(
    "explanation_no_join_rule",
    "zero or one direct dependency"
    in explanation.get(
        "no_join_rule",
        "",
    ),
)

check(
    "explanation_direct_edge_rule",
    "transitive ancestors are excluded"
    in explanation.get(
        "direct_edge_rule",
        "",
    ),
)

check(
    "explanation_wave_separation",
    "does not define"
    in explanation.get(
        "wave_boundary",
        "",
    ),
)

check(
    "explanation_lineage_separation",
    "parent_job_id"
    in explanation.get(
        "lineage_boundary",
        "",
    ),
)

check(
    "explanation_dependency_resolution_5_1_4",
    "5.1.4"
    in explanation.get(
        "dependency_resolution_boundary",
        "",
    ),
)

check(
    "explanation_readiness_5_1_6",
    "5.1.6"
    in explanation.get(
        "readiness_boundary",
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
    "explanation_fan_out_5_1_8",
    "5.1.8"
    in explanation.get(
        "fan_out_boundary",
        "",
    ),
)

check(
    "explanation_condition_5_1_10",
    "5.1.10"
    in explanation.get(
        "condition_boundary",
        "",
    ),
)

check(
    "explanation_persistence_5_1_14",
    "5.1.14"
    in explanation.get(
        "persistence_boundary",
        "",
    ),
)

check(
    "explanation_completion_5_1_15",
    "5.1.15"
    in explanation.get(
        "completion_boundary",
        "",
    ),
)


# ============================================================
# 27. REQUIRED PROHIBITIONS
# ============================================================

required_prohibitions = (
    "does not evaluate UniversalJob.status",
    "does not evaluate job priority",
    "does not evaluate created_at",
    "does not evaluate scheduled_at",

    "does not evaluate dependency statuses",
    "does not evaluate all_dependencies_satisfied",

    "does not evaluate stage readiness",
    "does not evaluate runtime handoff eligibility",
    "does not consume fan-out coordination objects",

    "does not treat parent_job_id as join",
    "does not treat batch_id as join",
    "does not treat pipeline_run_id as join",
    "does not treat execution-wave co-membership as join",
    "does not include transitive ancestors",

    "does not evaluate conditional branches",
    "does not determine orchestration completion",

    "does not wait for dependencies",
    "does not sleep or poll",

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

    "does not dispatch runtime handlers",
    "does not execute runtime handlers",
    "does not execute jobs",

    "does not create threads",
    "does not create processes",
    "does not create async tasks",

    "does not mutate UniversalJob.status",
    "does not transition orchestration state",

    "does not access Runtime State Store",
    "does not persist fan-in decisions",

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
# 28. IMPORT BOUNDARY
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
# 29. FORBIDDEN IMPORTS
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

    "backend.server.runtime.universal_queue",
    "backend.server.runtime.universal_worker",

    "backend.server.runtime.universal_runtime_registration",
    "backend.server.runtime.universal_runtime_worker_v1",
    "backend.server.runtime.universal_runtime_infrastructure",

    "backend.server.runtime.universal_orchestration.dependency_resolution",
    "backend.server.runtime.universal_orchestration.stage_readiness",
    "backend.server.runtime.universal_orchestration.runtime_handoff",
    "backend.server.runtime.universal_orchestration.fan_out_coordination",
    "backend.server.runtime.universal_orchestration.state_model",

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
            module == forbidden_module
            or
            module.startswith(
                forbidden_module
                + "."
            )
        )
    )

    check(
        "forbidden_import_absent_"
        + forbidden_module.replace(
            ".",
            "_"
        ),
        not matches,
        matches,
    )


# ============================================================
# 30. FORBIDDEN CALLS
# ============================================================

forbidden_calls = {
    "open",
    "read_text",
    "write_text",
    "mkdir",
    "unlink",
    "remove",

    "sleep",
    "wait",
    "poll",

    "time",
    "time_ns",
    "now",
    "utcnow",

    "uuid4",
    "uuid5",
    "random",
    "randint",

    "enqueue_job",
    "schedule_job",
    "dequeue_job",
    "claim_job",

    "discover_universal_workers",
    "assign_universal_worker",

    "acquire_universal_worker_lease",
    "renew_universal_worker_lease",
    "release_universal_worker_lease",

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
# 31. FORBIDDEN ATTRIBUTES
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

    "attempts",
    "attempt_count",
):

    check(
        "forbidden_attribute_absent_"
        + forbidden_attr,
        forbidden_attr
        not in attrs,
    )


# ============================================================
# 32. PROTECTED AUTHORITIES
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
# 33. FINAL AST
# ============================================================

final_ast = ast_sha(
    FAN_IN_PATH
)


check(
    "fan_in_ast_final",
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
        "PHASE 5.1.9 — UNIVERSAL ORCHESTRATION "
        "FAN-IN / JOIN COORDINATION ADVERSARIAL REGRESSION"
    ),

    "=" * 118,

    "",

    (
        "FAN-IN COORDINATION AST SHA256: "
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
            "ADVERSARIAL FAN-IN / JOIN COORDINATION REGRESSION: "
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

        "FAN-IN AST MODIFIED: NO",
        "5.1.1–5.1.8 FROZEN AUTHORITIES MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "ZERO DIRECT DEPENDENCIES: NO_JOIN",
        "ONE DIRECT DEPENDENCY: NO_JOIN",
        "TWO OR MORE DIRECT DEPENDENCIES: JOIN",

        "",

        "TRANSITIVE ANCESTORS INCLUDED: NO",
        "EXECUTION WAVES DEFINE JOIN MEMBERSHIP: NO",
        "PARENT_JOB_ID DEFINES JOIN: NO",

        "",

        "TARGET STATUS USED: NO",
        "UPSTREAM STATUS USED: NO",
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
        "HANDLER DISPATCH: NO",
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
            "STATUS: REGRESSION PASS "
            "— FINAL CERTIFICATION REQUIRED"
            if passed == total
            else
            "STATUS: REGRESSION FAILED "
            "— PATCH REQUIRED"
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
        "Phase 5.1.9 adversarial regression failed."
    )
