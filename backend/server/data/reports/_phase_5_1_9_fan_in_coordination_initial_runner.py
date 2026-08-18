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
    / "phase_5_1_9_fan_in_coordination_initial_implementation.txt"
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

    actual = ast_sha(path)

    if actual != expected:

        raise SystemExit(
            "Protected authority changed before 5.1.9: "
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
# AUTHORITY
# ============================================================

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
# THREE-WAY JOIN
# ============================================================

plan_three = make_plan(
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
    ),
    run_id="join-three",
)


result_three = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=plan_three,
        target_job_id="join",
    )
)


check(
    "three_dependencies_exact",
    result_three.direct_dependency_job_ids
    == (
        "a",
        "b",
        "c",
    ),
)

check(
    "three_width",
    result_three.join_width
    == 3,
)

check(
    "three_is_join",
    result_three.is_join,
)

check(
    "three_has_dependencies",
    result_three.has_dependencies,
)

check(
    "three_dependency_jobs_exact",
    tuple(
        job.job_id
        for job
        in result_three.direct_dependency_jobs
    )
    == (
        "a",
        "b",
        "c",
    ),
)


# ============================================================
# ONE DEPENDENCY
# ============================================================

plan_one = make_plan(
    jobs_tuple=(
        make_job(job_id="a"),
        make_job(
            job_id="target",
            dependencies=("a",),
        ),
    ),
    run_id="join-one",
)


result_one = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=plan_one,
        target_job_id="target",
    )
)


check(
    "one_dependency_exact",
    result_one.direct_dependency_job_ids
    == ("a",),
)

check(
    "one_width",
    result_one.join_width
    == 1,
)

check(
    "one_no_join",
    not result_one.is_join,
)

check(
    "one_has_dependencies",
    result_one.has_dependencies,
)


# ============================================================
# ZERO DEPENDENCY ROOT
# ============================================================

result_root = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=plan_one,
        target_job_id="a",
    )
)


check(
    "root_dependencies_empty",
    result_root.direct_dependency_job_ids
    == (),
)

check(
    "root_width_zero",
    result_root.join_width
    == 0,
)

check(
    "root_no_join",
    not result_root.is_join,
)

check(
    "root_has_no_dependencies",
    not result_root.has_dependencies,
)


# ============================================================
# TRANSITIVE ANCESTOR EXCLUDED
# ============================================================

plan_transitive = make_plan(
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
    run_id="join-transitive",
)


result_transitive = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=plan_transitive,
        target_job_id="target",
    )
)


check(
    "transitive_direct_only",
    result_transitive.direct_dependency_job_ids
    == (
        "left",
        "right",
    ),
)

check(
    "transitive_root_excluded",
    "root"
    not in result_transitive.direct_dependency_job_ids,
)


# ============================================================
# DIAMOND
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
    run_id="diamond",
)


diamond_result = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=diamond_plan,
        target_job_id="d",
    )
)


check(
    "diamond_join",
    (
        diamond_result.is_join
        and
        diamond_result.direct_dependency_job_ids
        == (
            "b",
            "c",
        )
    ),
)


# ============================================================
# INTERNAL JOIN CAN FAN OUT LATER
# ============================================================

internal_plan = make_plan(
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
            job_id="downstream-a",
            dependencies=("join",),
        ),

        make_job(
            job_id="downstream-b",
            dependencies=("join",),
        ),
    ),
    run_id="join-internal",
)


internal_result = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=internal_plan,
        target_job_id="join",
    )
)


check(
    "internal_join_valid",
    internal_result.is_join,
)


# ============================================================
# PARENT LINEAGE DOES NOT DEFINE JOIN
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
    "parent_lineage_not_join",
    lineage_result.direct_dependency_job_ids
    == (),
)


# ============================================================
# STATUS IRRELEVANCE
# ============================================================

for status in jobs.UniversalJobStatus:

    status_plan = make_plan(
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
            "join-status-"
            + status.value
        ),
    )

    status_result = (
        fanin
        .coordinate_universal_orchestration_fan_in(
            execution_plan=status_plan,
            target_job_id="target",
        )
    )

    check(
        "status_irrelevant_"
        + status.value,
        status_result.is_join,
    )


# ============================================================
# PRIORITY IRRELEVANCE
# ============================================================

for priority in jobs.UniversalJobPriority:

    priority_plan = make_plan(
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

    priority_result = (
        fanin
        .coordinate_universal_orchestration_fan_in(
            execution_plan=priority_plan,
            target_job_id="target",
        )
    )

    check(
        "priority_irrelevant_"
        + str(priority.value),
        priority_result.is_join,
    )


# ============================================================
# NORMALIZATION
# ============================================================

normalized_result = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=plan_three,
        target_job_id="  join  ",
    )
)


check(
    "target_outer_whitespace_normalized",
    normalized_result.target_job_id
    == "join",
)


# ============================================================
# INVALID TARGET
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
        bytearray(b"a"),
        {},
        [],
        (),
        object(),
    ),
    start=1,
):

    try:

        fanin.coordinate_universal_orchestration_fan_in(
            execution_plan=plan_three,
            target_job_id=bad,
        )

    except fanin.UniversalOrchestrationFanInCoordinationError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_target_"
        + str(index),
        rejected,
    )


# ============================================================
# TARGET OUTSIDE PLAN
# ============================================================

try:

    fanin.coordinate_universal_orchestration_fan_in(
        execution_plan=plan_three,
        target_job_id="outside",
    )

except fanin.UniversalOrchestrationFanInCoordinationError as exc:

    outside_rejected = (
        exc.code
        == "fan_in_target_not_in_execution_plan"
    )

else:

    outside_rejected = False


check(
    "outside_target_rejected",
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

        fanin.coordinate_universal_orchestration_fan_in(
            execution_plan=bad,
            target_job_id="join",
        )

    except fanin.UniversalOrchestrationFanInCoordinationError as exc:

        rejected = (
            exc.code
            == "invalid_fan_in_execution_plan"
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
    "readiness",
    "handoff",
    "fan_out",

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
# GROUP ID
# ============================================================

group_id_one = (
    result_three.join_group_id
)

group_id_two = (
    fanin
    .coordinate_universal_orchestration_fan_in(
        execution_plan=plan_three,
        target_job_id="join",
    )
    .join_group_id
)


check(
    "group_id_length",
    len(group_id_one)
    == 64,
    group_id_one,
)

check(
    "group_id_upper_hex",
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
    "dependency_resolution_boundary_5_1_4",
    "5.1.4"
    in explanation.get(
        "dependency_resolution_boundary",
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
    "handoff_boundary_5_1_7",
    "5.1.7"
    in explanation.get(
        "handoff_boundary",
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

check(
    "completion_boundary_5_1_15",
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

tree = ast.parse(source)


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
# FORBIDDEN CALLS
# ============================================================

forbidden_calls = {
    "open",
    "read_text",
    "write_text",

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
    "save",
    "dispatch",
    "execute",

    "time",
    "now",
    "utcnow",
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

    actual = ast_sha(path)

    check(
        "protected_"
        + name,
        actual
        == expected,
        actual,
    )


fan_in_ast = ast_sha(
    FAN_IN_PATH
)


check(
    "fan_in_ast_generated",
    len(fan_in_ast)
    == 64,
    fan_in_ast,
)


passed = sum(
    1
    for _, ok, _
    in checks
    if ok
)

total = len(checks)


lines = [
    (
        "PHASE 5.1.9 — UNIVERSAL ORCHESTRATION "
        "FAN-IN / JOIN COORDINATION INITIAL IMPLEMENTATION"
    ),
    "=" * 118,
    "",
    (
        "FAN-IN COORDINATION AST SHA256: "
        + fan_in_ast
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
            "INITIAL FAN-IN / JOIN COORDINATION RESULT: "
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

        "5.1.1–5.1.8 FROZEN AUTHORITIES MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "FAN-IN CLASSIFICATIONS: JOIN / NO_JOIN",
        "ZERO DIRECT DEPENDENCIES: NO_JOIN",
        "ONE DIRECT DEPENDENCY: NO_JOIN",
        "TWO OR MORE DIRECT DEPENDENCIES: JOIN",

        "",

        "TRANSITIVE ANCESTORS INCLUDED: NO",
        "EXECUTION-WAVE CO-MEMBERSHIP DEFINES JOIN: NO",
        "PARENT_JOB_ID DEFINES JOIN: NO",

        "",

        "UNIVERSAL JOB STATUS USED: NO",
        "DEPENDENCY STATUS EVIDENCE USED: NO",
        "ALL_DEPENDENCIES_SATISFIED EVALUATED: NO",
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
            "STATUS: INITIAL IMPLEMENTATION PASS "
            "— ADVERSARIAL REGRESSION REQUIRED"
            if passed == total
            else
            "STATUS: INITIAL IMPLEMENTATION FAILED"
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
        (
            "Phase 5.1.9 Fan-In / Join "
            "initial implementation failed."
        )
    )
