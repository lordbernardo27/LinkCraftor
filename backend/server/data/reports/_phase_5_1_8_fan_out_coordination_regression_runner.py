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
    / "phase_5_1_8_fan_out_coordination_regression.txt"
)

EXPECTED_FAN_OUT_AST = (
    "D60C8629D2490DC41A8DF43E30F00A1D4851941E65CBD2EBE7EED70B75217916"
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


# ============================================================
# PRE-FLIGHT
# ============================================================

if ast_sha(FAN_OUT_PATH) != EXPECTED_FAN_OUT_AST:
    raise SystemExit(
        "5.1.8 AST changed before regression."
    )


for name, (path, expected) in PROTECTED.items():

    actual = ast_sha(path)

    if actual != expected:

        raise SystemExit(
            "Protected authority changed: "
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
# 1. PUBLIC API / VERSION
# ============================================================

check(
    "ast_initial_exact",
    ast_sha(FAN_OUT_PATH)
    == EXPECTED_FAN_OUT_AST,
)

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


expected_all = (
    "UNIVERSAL_ORCHESTRATION_FAN_OUT_COORDINATION_VERSION",
    "UNIVERSAL_ORCHESTRATION_FAN_OUT_COORDINATION_SCHEMA_VERSION",
    "UNIVERSAL_ORCHESTRATION_FAN_OUT_GROUP_HASH_ALGORITHM",
    "UniversalOrchestrationFanOutCoordinationError",
    "UniversalOrchestrationFanOutClassification",
    "classify_universal_orchestration_fan_out",
    "calculate_universal_orchestration_fan_out_group_id",
    "UniversalOrchestrationFanOutCoordination",
    "coordinate_universal_orchestration_fan_out",
    "explain_universal_orchestration_fan_out_coordination_v1",
)


check(
    "public_api_exact",
    tuple(fanout.__all__)
    == expected_all,
    fanout.__all__,
)


# ============================================================
# 2. WIDTH MATRIX 0..10
# ============================================================

for width in range(0, 11):

    source = make_job(
        job_id="source"
    )

    children = tuple(
        make_job(
            job_id=f"child-{index:02d}",
            dependencies=("source",),
        )
        for index
        in range(width)
    )

    plan = make_plan(
        jobs_tuple=(
            source,
            *children,
        ),
        run_id=f"width-{width}",
    )

    result = (
        fanout
        .coordinate_universal_orchestration_fan_out(
            execution_plan=plan,
            source_job_id="source",
        )
    )

    expected_ids = tuple(
        f"child-{index:02d}"
        for index
        in range(width)
    )

    check(
        f"width_{width}_members_exact",
        result.direct_dependent_job_ids
        == expected_ids,
    )

    check(
        f"width_{width}_count_exact",
        result.fan_out_width
        == width,
    )

    check(
        f"width_{width}_classification_exact",
        result.is_fan_out
        == (width >= 2),
    )

    check(
        f"width_{width}_has_dependents_exact",
        result.has_dependents
        == (width > 0),
    )


# ============================================================
# 3. LEXICAL ORDER
# ============================================================

lexical_jobs = (
    make_job(job_id="source"),
    make_job(
        job_id="zeta",
        dependencies=("source",),
    ),
    make_job(
        job_id="alpha",
        dependencies=("source",),
    ),
    make_job(
        job_id="middle",
        dependencies=("source",),
    ),
)


lexical_plan = make_plan(
    jobs_tuple=lexical_jobs,
    run_id="lexical",
)


lexical_result = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=lexical_plan,
        source_job_id="source",
    )
)


check(
    "lexical_dependents_exact",
    lexical_result.direct_dependent_job_ids
    == (
        "alpha",
        "middle",
        "zeta",
    ),
)


# ============================================================
# 4. TRANSITIVE DESCENDANTS EXCLUDED
# ============================================================

deep_jobs = (
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
        dependencies=("b",),
    ),
    make_job(
        job_id="e",
        dependencies=("c",),
    ),
    make_job(
        job_id="f",
        dependencies=("d", "e"),
    ),
)


deep_plan = make_plan(
    jobs_tuple=deep_jobs,
    run_id="deep",
)


deep_result = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=deep_plan,
        source_job_id="a",
    )
)


check(
    "deep_direct_only",
    deep_result.direct_dependent_job_ids
    == ("b", "c"),
)

for transitive in (
    "d",
    "e",
    "f",
):

    check(
        "transitive_excluded_" + transitive,
        transitive
        not in deep_result.direct_dependent_job_ids,
    )


# ============================================================
# 5. SAME WAVE IS NOT FAN-OUT
# ============================================================

wave_jobs = (
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
        job_id="c",
        dependencies=("b",),
    ),
    make_job(
        job_id="z",
        dependencies=("y",),
    ),
)


wave_plan = make_plan(
    jobs_tuple=wave_jobs,
    run_id="wave-separation",
)


check(
    "wave_structure_expected",
    wave_plan.execution_waves
    == (
        ("a", "x"),
        ("b", "y"),
        ("c", "z"),
    ),
    wave_plan.execution_waves,
)


for source_job_id, expected in (
    ("a", ("b",)),
    ("x", ("y",)),
    ("b", ("c",)),
    ("y", ("z",)),
):

    result = (
        fanout
        .coordinate_universal_orchestration_fan_out(
            execution_plan=wave_plan,
            source_job_id=source_job_id,
        )
    )

    check(
        "wave_not_group_" + source_job_id,
        result.direct_dependent_job_ids
        == expected,
    )


# ============================================================
# 6. PARENT LINEAGE MUST NOT CREATE FAN-OUT
# ============================================================

lineage_jobs = (
    make_job(
        job_id="parent",
    ),
    make_job(
        job_id="child-a",
        parent_job_id="parent",
    ),
    make_job(
        job_id="child-b",
        parent_job_id="parent",
    ),
    make_job(
        job_id="child-c",
        parent_job_id="parent",
    ),
)


lineage_plan = make_plan(
    jobs_tuple=lineage_jobs,
    run_id="lineage-only",
)


lineage_result = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=lineage_plan,
        source_job_id="parent",
    )
)


check(
    "lineage_only_zero_direct_dependents",
    lineage_result.direct_dependent_job_ids
    == (),
)

check(
    "lineage_only_no_fan_out",
    not lineage_result.is_fan_out,
)


# ============================================================
# 7. INTERNAL NODE FAN-OUT
# ============================================================

internal_jobs = (
    make_job(job_id="root"),
    make_job(
        job_id="middle",
        dependencies=("root",),
    ),
    make_job(
        job_id="left",
        dependencies=("middle",),
    ),
    make_job(
        job_id="right",
        dependencies=("middle",),
    ),
    make_job(
        job_id="join",
        dependencies=("left", "right"),
    ),
)


internal_plan = make_plan(
    jobs_tuple=internal_jobs,
    run_id="internal",
)


internal_result = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=internal_plan,
        source_job_id="middle",
    )
)


check(
    "internal_fan_out_exact",
    (
        internal_result.is_fan_out
        and
        internal_result.direct_dependent_job_ids
        == ("left", "right")
    ),
)


# ============================================================
# 8. STATUS IRRELEVANCE
# ============================================================

for status in jobs.UniversalJobStatus:

    status_plan = make_plan(
        jobs_tuple=(
            make_job(
                job_id="a",
                status=status,
            ),
            make_job(
                job_id="b",
                dependencies=("a",),
            ),
            make_job(
                job_id="c",
                dependencies=("a",),
            ),
        ),
        run_id="status-" + status.value,
    )

    result = (
        fanout
        .coordinate_universal_orchestration_fan_out(
            execution_plan=status_plan,
            source_job_id="a",
        )
    )

    check(
        "status_irrelevant_" + status.value,
        (
            result.is_fan_out
            and
            result.fan_out_width == 2
        ),
    )


# ============================================================
# 9. PRIORITY IRRELEVANCE
# ============================================================

for priority in jobs.UniversalJobPriority:

    priority_plan = make_plan(
        jobs_tuple=(
            make_job(
                job_id="a",
                priority=priority,
            ),
            make_job(
                job_id="b",
                dependencies=("a",),
            ),
            make_job(
                job_id="c",
                dependencies=("a",),
            ),
        ),
        run_id=(
            "priority-"
            + str(priority.value)
        ),
    )

    result = (
        fanout
        .coordinate_universal_orchestration_fan_out(
            execution_plan=priority_plan,
            source_job_id="a",
        )
    )

    check(
        "priority_irrelevant_"
        + str(priority.value),
        result.is_fan_out,
    )


# ============================================================
# 10. SOURCE NORMALIZATION
# ============================================================

normalization_plan = make_plan(
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
    ),
    run_id="normalization",
)


for raw in (
    "a",
    " a",
    "a ",
    "  a  ",
    "\ta\t",
    "\na\n",
):

    result = (
        fanout
        .coordinate_universal_orchestration_fan_out(
            execution_plan=normalization_plan,
            source_job_id=raw,
        )
    )

    check(
        "normalized_source_" + repr(raw),
        result.source_job_id
        == "a",
    )


# ============================================================
# 11. INVALID SOURCE ATTACKS
# ============================================================

invalid_source_values = (
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
    "a b",
    "a\tb",
    "a\nb",
    b"a",
    bytearray(b"a"),
    {},
    [],
    (),
    set(),
    object(),
)


for index, bad in enumerate(
    invalid_source_values,
    start=1,
):

    try:

        fanout.coordinate_universal_orchestration_fan_out(
            execution_plan=normalization_plan,
            source_job_id=bad,
        )

    except fanout.UniversalOrchestrationFanOutCoordinationError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_source_attack_"
        + str(index),
        rejected,
        repr(bad),
    )


# ============================================================
# 12. TOO-LONG SOURCE
# ============================================================

too_long = (
    "x" * 201
)

try:

    fanout.coordinate_universal_orchestration_fan_out(
        execution_plan=normalization_plan,
        source_job_id=too_long,
    )

except fanout.UniversalOrchestrationFanOutCoordinationError:

    too_long_rejected = True

else:

    too_long_rejected = False


check(
    "too_long_source_rejected",
    too_long_rejected,
)


# ============================================================
# 13. SOURCE OUTSIDE PLAN
# ============================================================

for outside in (
    "outside",
    "missing-job",
    "not-in-plan",
):

    try:

        fanout.coordinate_universal_orchestration_fan_out(
            execution_plan=normalization_plan,
            source_job_id=outside,
        )

    except fanout.UniversalOrchestrationFanOutCoordinationError as exc:

        rejected = (
            exc.code
            == "fan_out_source_not_in_execution_plan"
        )

    else:

        rejected = False

    check(
        "outside_source_rejected_"
        + outside,
        rejected,
    )


# ============================================================
# 14. INVALID EXECUTION PLAN ATTACKS
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
        "invalid_plan_attack_"
        + str(index),
        rejected,
    )


# ============================================================
# 15. STORED FIELDS EXACT
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

    "status",
    "priority",

    "queue_id",
    "worker_id",
    "lease_id",

    "handler",
    "dispatch_result",
    "execution_result",

    "fan_in",
    "join",
    "condition",

    "created_at",
    "updated_at",
    "metadata",
):

    check(
        "forbidden_field_" + forbidden,
        forbidden
        not in field_names,
    )


# ============================================================
# 16. IMMUTABILITY
# ============================================================

immutable_result = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=normalization_plan,
        source_job_id="a",
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
        "immutable_" + field.name,
        immutable,
    )


# ============================================================
# 17. GROUP ID DETERMINISM
# ============================================================

ids = tuple(
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=normalization_plan,
        source_job_id="a",
    )
    .fan_out_group_id
    for _
    in range(20)
)


check(
    "group_ids_repeat_exact",
    len(set(ids))
    == 1,
)

check(
    "group_id_length_64",
    len(ids[0])
    == 64,
)

check(
    "group_id_upper_hex",
    all(
        char
        in "0123456789ABCDEF"
        for char
        in ids[0]
    ),
)


# ============================================================
# 18. GROUP ID CHANGES WITH RUN ID
# ============================================================

run_plan_a = make_plan(
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
    ),
    run_id="run-a",
)


run_plan_b = make_plan(
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
    ),
    run_id="run-b",
)


run_group_a = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=run_plan_a,
        source_job_id="a",
    )
    .fan_out_group_id
)


run_group_b = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=run_plan_b,
        source_job_id="a",
    )
    .fan_out_group_id
)


check(
    "group_id_run_identity_sensitive",
    run_group_a
    != run_group_b,
)


# ============================================================
# 19. GROUP ID CHANGES WITH SOURCE
# ============================================================

multi_source_plan = make_plan(
    jobs_tuple=(
        make_job(job_id="a"),
        make_job(job_id="x"),

        make_job(
            job_id="b",
            dependencies=("a",),
        ),
        make_job(
            job_id="c",
            dependencies=("a",),
        ),

        make_job(
            job_id="y",
            dependencies=("x",),
        ),
        make_job(
            job_id="z",
            dependencies=("x",),
        ),
    ),
    run_id="multi-source",
)


group_a = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=multi_source_plan,
        source_job_id="a",
    )
    .fan_out_group_id
)


group_x = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=multi_source_plan,
        source_job_id="x",
    )
    .fan_out_group_id
)


check(
    "group_id_source_sensitive",
    group_a
    != group_x,
)


# ============================================================
# 20. DIRECT DEPENDENT JOB OBJECTS EXACT
# ============================================================

result = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=normalization_plan,
        source_job_id="a",
    )
)


check(
    "dependent_job_object_count",
    len(result.direct_dependent_jobs)
    == 2,
)

check(
    "dependent_job_objects_match_plan",
    all(
        job
        is normalization_plan.job_map[job.job_id]
        for job
        in result.direct_dependent_jobs
    ),
)


# ============================================================
# 21. DERIVED IDENTITY / SOURCE
# ============================================================

check(
    "identity_derived",
    result.identity
    is normalization_plan.identity,
)

check(
    "source_job_derived",
    result.source_job
    is normalization_plan.job_map["a"],
)


# ============================================================
# 22. REPEATED EVALUATION EQUALITY
# ============================================================

repeat_one = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=normalization_plan,
        source_job_id="a",
    )
)

repeat_two = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=normalization_plan,
        source_job_id="a",
    )
)


check(
    "repeat_objects_equal",
    repeat_one
    == repeat_two,
)

check(
    "repeat_width_equal",
    repeat_one.fan_out_width
    == repeat_two.fan_out_width,
)

check(
    "repeat_classification_equal",
    repeat_one.classification
    is repeat_two.classification,
)

check(
    "repeat_group_id_equal",
    repeat_one.fan_out_group_id
    == repeat_two.fan_out_group_id,
)


# ============================================================
# 23. EXECUTION PLAN NOT MUTATED
# ============================================================

plan_before = (
    normalization_plan.job_ids,
    normalization_plan.dependency_map,
    normalization_plan.dependent_map,
    normalization_plan.execution_waves,
    normalization_plan.topological_order,
)


_ = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=normalization_plan,
        source_job_id="a",
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
# 24. EXPLANATION CONTRACT
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
    "explanation_phase_exact",
    explanation.get("phase")
    == "5.1.8",
)

check(
    "explanation_component_exact",
    explanation.get("component")
    == "Universal Orchestration Fan-Out Coordination",
)

check(
    "explanation_stored_fields_exact",
    explanation.get("stored_fields")
    == (
        "execution_plan",
        "source_job_id",
        "schema_version",
    ),
)

check(
    "explanation_fan_out_rule",
    "two or more direct dependents"
    in explanation.get(
        "fan_out_rule",
        "",
    ),
)

check(
    "explanation_no_fan_out_rule",
    "zero or one direct dependent"
    in explanation.get(
        "no_fan_out_rule",
        "",
    ),
)

check(
    "explanation_direct_edges",
    "transitive descendants are excluded"
    in explanation.get(
        "direct_edge_rule",
        "",
    ),
)

check(
    "explanation_wave_separation",
    "not implicitly one fan-out group"
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
    "explanation_readiness_separation",
    "5.1.6"
    in explanation.get(
        "readiness_boundary",
        "",
    ),
)

check(
    "explanation_handoff_separation",
    "5.1.7"
    in explanation.get(
        "handoff_boundary",
        "",
    ),
)

check(
    "explanation_fanin_5_1_9",
    "5.1.9"
    in explanation.get(
        "fan_in_boundary",
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


# ============================================================
# 25. REQUIRED PROHIBITIONS
# ============================================================

required_prohibitions = (
    "does not evaluate UniversalJob.status",
    "does not evaluate job priority",
    "does not evaluate created_at",
    "does not evaluate scheduled_at",
    "does not evaluate stage readiness",
    "does not evaluate runtime handoff eligibility",

    "does not treat parent_job_id as fan-out",
    "does not treat batch_id as fan-out",
    "does not treat pipeline_run_id as fan-out",
    "does not treat execution-wave co-membership as fan-out",
    "does not include transitive descendants",

    "does not coordinate fan-in or joins",
    "does not evaluate conditional branches",

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
    "does not persist fan-out decisions",

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
# 26. IMPORT BOUNDARY
# ============================================================

source = FAN_OUT_PATH.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(
    source
)


backend_imports = []


for node in ast.walk(tree):

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
# 27. FORBIDDEN IMPORTS
# ============================================================

all_imports = []


for node in ast.walk(tree):

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

    "backend.server.runtime.universal_orchestration.stage_readiness",
    "backend.server.runtime.universal_orchestration.runtime_handoff",
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
                forbidden_module + "."
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
# 28. FORBIDDEN CALLS
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


for node in ast.walk(tree):

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
# 29. NO STATUS / PRIORITY / TIMESTAMP ACCESS
# ============================================================

attrs = tuple(
    node.attr
    for node
    in ast.walk(tree)
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
    "attempts",
    "attempt_count",
    "worker_id",
    "queue_id",
    "lease_id",
):

    check(
        "attribute_not_used_"
        + forbidden_attr,
        forbidden_attr
        not in attrs,
    )


# ============================================================
# 30. PROTECTED AUTHORITIES
# ============================================================

for name, (path, expected) in PROTECTED.items():

    actual = ast_sha(path)

    check(
        "protected_" + name,
        actual == expected,
        actual,
    )


# ============================================================
# 31. FINAL AST
# ============================================================

final_ast = ast_sha(
    FAN_OUT_PATH
)


check(
    "fan_out_ast_final",
    final_ast
    == EXPECTED_FAN_OUT_AST,
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

total = len(checks)


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
        "PHASE 5.1.8 — UNIVERSAL ORCHESTRATION "
        "FAN-OUT COORDINATION ADVERSARIAL REGRESSION"
    ),
    "=" * 118,
    "",
    (
        "FAN-OUT COORDINATION AST SHA256: "
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
            "FAIL: " + name
        )

        if detail:

            lines.append(
                "   " + detail
            )


lines.extend(
    [
        "",
        "=" * 118,
        (
            "ADVERSARIAL FAN-OUT COORDINATION REGRESSION: "
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
        "FAN-OUT AST MODIFIED: NO",
        "5.1.1–5.1.7 FROZEN AUTHORITIES MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",
        "",
        "ZERO DEPENDENTS: NO_FAN_OUT",
        "ONE DEPENDENT: NO_FAN_OUT",
        "TWO OR MORE DIRECT DEPENDENTS: FAN_OUT",
        "",
        "TRANSITIVE DESCENDANTS INCLUDED: NO",
        "EXECUTION WAVES DEFINE GROUP MEMBERSHIP: NO",
        "PARENT_JOB_ID DEFINES FAN-OUT: NO",
        "",
        "UNIVERSAL JOB STATUS USED: NO",
        "JOB PRIORITY USED: NO",
        "CREATED_AT/SCHEDULED_AT USED: NO",
        "READINESS USED: NO",
        "RUNTIME HANDOFF USED: NO",
        "",
        "QUEUE ACTIVITY: NO",
        "WORKER ACTIVITY: NO",
        "LEASE ACTIVITY: NO",
        "HANDLER DISPATCH: NO",
        "JOB EXECUTION: NO",
        "THREAD/PROCESS/TASK CREATION: NO",
        "",
        "UNIVERSAL JOB MUTATION: NO",
        "ORCHESTRATION STATE TRANSITION: NO",
        "FAN-IN/JOIN COORDINATION: NO",
        "CONDITIONAL BRANCHING: NO",
        "PERSISTENCE: NO",
        "RUNTIME STATE STORE ACCESS: NO",
        "COORDINATION FRAMEWORK ACCESS: NO",
        "PIPELINE COORDINATOR ACCESS: NO",
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
    "\n".join(lines),
    encoding="utf-8",
)


print(
    "\n".join(lines)
)


if passed != total:

    raise SystemExit(
        "Phase 5.1.8 adversarial regression failed."
    )
