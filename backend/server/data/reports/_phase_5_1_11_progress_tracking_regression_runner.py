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

PROGRESS_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_orchestration"
    / "progress_tracking.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_1_11_progress_tracking_regression.txt"
)

EXPECTED_PROGRESS_AST = (
    "92C100E0682F975488F78ED5F0D38CB1F4C6E18F6FEA08D1A8D81BE98A4D8309"
)


PROTECTED = {
    "5.1.1_contract": (
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

    "5.1.8_fan_out": (
        ROOT / "backend/server/runtime/universal_orchestration/fan_out_coordination.py",
        "D60C8629D2490DC41A8DF43E30F00A1D4851941E65CBD2EBE7EED70B75217916",
    ),

    "5.1.9_fan_in": (
        ROOT / "backend/server/runtime/universal_orchestration/fan_in_coordination.py",
        "98786AEF5E4DBD804FBE5FE32EEE7CD54907FAC6A9C016B6120851834F6CFA0F",
    ),

    "5.1.10_conditional_branching": (
        ROOT / "backend/server/runtime/universal_orchestration/conditional_branching.py",
        "3799D3BEFB10C77400B40964EBBCCF598B7576BA9034D1C7F29622D0EC65286F",
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
        canonical.encode(
            "utf-8"
        )
    ).hexdigest().upper()


# ============================================================
# PRE-FLIGHT
# ============================================================

if not PROGRESS_PATH.exists():

    raise SystemExit(
        "5.1.11 progress_tracking.py is missing."
    )


actual_progress_ast = ast_sha(
    PROGRESS_PATH
)


if actual_progress_ast != EXPECTED_PROGRESS_AST:

    raise SystemExit(
        (
            "5.1.11 AST changed before adversarial regression.\n"
            "EXPECTED: "
            + EXPECTED_PROGRESS_AST
            + "\nACTUAL:   "
            + actual_progress_ast
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
            "Protected authority changed before 5.1.11 regression: "
            + name
        )


# ============================================================
# IMPORTS
# ============================================================

sys.path.insert(
    0,
    str(
        ROOT
    ),
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

fanout = importlib.import_module(
    "backend.server.runtime.universal_orchestration.fan_out_coordination"
)

conditional = importlib.import_module(
    "backend.server.runtime.universal_orchestration.conditional_branching"
)


module_name = (
    "backend.server.runtime."
    "universal_orchestration.progress_tracking"
)

sys.modules.pop(
    module_name,
    None,
)

progress = importlib.import_module(
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
            bool(
                condition
            ),
            str(
                detail
            ),
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


def decision_for(
    *,
    plan,
    source_job_id,
    evidence,
):

    fan_out = (
        fanout
        .coordinate_universal_orchestration_fan_out(
            execution_plan=plan,
            source_job_id=source_job_id,
        )
    )

    return (
        conditional
        .evaluate_universal_orchestration_conditional_branching(
            fan_out_coordination=fan_out,
            condition_evidence=evidence,
        )
    )


# ============================================================
# 1. AUTHORITY EXACTNESS
# ============================================================

check(
    "ast_initial_exact",
    ast_sha(PROGRESS_PATH)
    == EXPECTED_PROGRESS_AST,
)

check(
    "version_exact",
    progress.UNIVERSAL_ORCHESTRATION_PROGRESS_TRACKING_VERSION
    == "universal_orchestration_progress_tracking_v5.1.11",
)

check(
    "schema_exact",
    progress.UNIVERSAL_ORCHESTRATION_PROGRESS_TRACKING_SCHEMA_VERSION
    == "universal_orchestration_progress_tracking_schema_v1",
)

check(
    "hash_algorithm_exact",
    progress.UNIVERSAL_ORCHESTRATION_PROGRESS_SNAPSHOT_HASH_ALGORITHM
    == "sha256",
)


expected_all = (
    "UNIVERSAL_ORCHESTRATION_PROGRESS_TRACKING_VERSION",
    "UNIVERSAL_ORCHESTRATION_PROGRESS_TRACKING_SCHEMA_VERSION",
    "UNIVERSAL_ORCHESTRATION_PROGRESS_SNAPSHOT_HASH_ALGORITHM",
    "NOT_STARTED_UNIVERSAL_JOB_STATUSES",
    "PENDING_UNIVERSAL_JOB_STATUSES",
    "IN_PROGRESS_UNIVERSAL_JOB_STATUSES",
    "SUSPENDED_UNIVERSAL_JOB_STATUSES",
    "TERMINAL_SUCCESS_UNIVERSAL_JOB_STATUSES",
    "TERMINAL_UNSUCCESSFUL_UNIVERSAL_JOB_STATUSES",
    "TERMINAL_PROGRESS_UNIVERSAL_JOB_STATUSES",
    "UniversalOrchestrationProgressTrackingError",
    "UniversalOrchestrationProgressSnapshot",
    "track_universal_orchestration_progress",
    "explain_universal_orchestration_progress_tracking_v1",
)


check(
    "public_api_exact",
    tuple(
        progress.__all__
    )
    == expected_all,
    progress.__all__,
)


# ============================================================
# 2. STATUS PARTITION COMPLETENESS / DISJOINTNESS
# ============================================================

partition_sets = (
    progress.NOT_STARTED_UNIVERSAL_JOB_STATUSES,
    progress.PENDING_UNIVERSAL_JOB_STATUSES,
    progress.IN_PROGRESS_UNIVERSAL_JOB_STATUSES,
    progress.SUSPENDED_UNIVERSAL_JOB_STATUSES,
    progress.TERMINAL_SUCCESS_UNIVERSAL_JOB_STATUSES,
    progress.TERMINAL_UNSUCCESSFUL_UNIVERSAL_JOB_STATUSES,
)


union = frozenset().union(
    *partition_sets
)


check(
    "status_partition_complete",
    union
    == frozenset(
        jobs.UniversalJobStatus
    ),
)


for left_index in range(
    len(
        partition_sets
    )
):

    for right_index in range(
        left_index + 1,
        len(
            partition_sets
        ),
    ):

        check(
            (
                "status_partition_disjoint_"
                + str(left_index)
                + "_"
                + str(right_index)
            ),
            not (
                partition_sets[
                    left_index
                ]
                &
                partition_sets[
                    right_index
                ]
            ),
        )


check(
    "terminal_progress_union_exact",
    progress.TERMINAL_PROGRESS_UNIVERSAL_JOB_STATUSES
    ==
    (
        progress.TERMINAL_SUCCESS_UNIVERSAL_JOB_STATUSES
        |
        progress.TERMINAL_UNSUCCESSFUL_UNIVERSAL_JOB_STATUSES
    ),
)


# ============================================================
# 3. EVERY STATUS / STRING COERCION
# ============================================================

for status in jobs.UniversalJobStatus:

    plan = make_plan(
        jobs_tuple=(
            make_job(
                job_id="only",
            ),
        ),
        run_id=(
            "status-object-"
            + status.value
        ),
    )

    object_result = (
        progress
        .track_universal_orchestration_progress(
            execution_plan=plan,
            status_evidence={
                "only":
                    status,
            },
        )
    )

    string_result = (
        progress
        .track_universal_orchestration_progress(
            execution_plan=plan,
            status_evidence={
                "only":
                    status.value,
            },
        )
    )

    check(
        "status_object_accepted_"
        + status.value,
        object_result.status_evidence_map[
            "only"
        ]
        is status,
    )

    check(
        "status_string_accepted_"
        + status.value,
        string_result.status_evidence_map[
            "only"
        ]
        is status,
    )


# ============================================================
# 4. STATUS BUCKET SEMANTICS
# ============================================================

status_jobs = tuple(
    make_job(
        job_id=status.value,
    )
    for status
    in jobs.UniversalJobStatus
)

status_plan = make_plan(
    jobs_tuple=status_jobs,
    run_id="all-status-buckets",
)


status_snapshot = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=status_plan,
        status_evidence={
            status.value:
                status
            for status
            in jobs.UniversalJobStatus
        },
    )
)


check(
    "not_started_created_only",
    status_snapshot.not_started_job_ids
    == ("created",),
)

check(
    "pending_queued_scheduled",
    status_snapshot.pending_job_ids
    == (
        "queued",
        "scheduled",
    ),
)

check(
    "in_progress_leased_running",
    status_snapshot.in_progress_job_ids
    == (
        "leased",
        "running",
    ),
)

check(
    "suspended_only",
    status_snapshot.suspended_job_ids
    == ("suspended",),
)

check(
    "success_only_succeeded",
    status_snapshot.successful_job_ids
    == ("succeeded",),
)

check(
    "terminal_unsuccessful_exact_ids",
    status_snapshot.terminal_unsuccessful_job_ids
    == (
        "cancelled",
        "dead_letter",
        "expired",
        "failed",
    ),
    status_snapshot.terminal_unsuccessful_job_ids,
)

check(
    "terminal_all_exact_ids",
    status_snapshot.terminal_job_ids
    == (
        "cancelled",
        "dead_letter",
        "expired",
        "failed",
        "succeeded",
    ),
    status_snapshot.terminal_job_ids,
)


# ============================================================
# 5. STATUS EVIDENCE INPUT ORDER
# ============================================================

order_plan = make_plan(
    jobs_tuple=(
        make_job(
            job_id="a",
        ),
        make_job(
            job_id="b",
        ),
        make_job(
            job_id="c",
        ),
    ),
    run_id="status-order",
)


ordered_one = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=order_plan,
        status_evidence=(
            ("c", "running"),
            ("a", "succeeded"),
            ("b", "queued"),
        ),
    )
)


ordered_two = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=order_plan,
        status_evidence=(
            ("b", "queued"),
            ("c", "running"),
            ("a", "succeeded"),
        ),
    )
)


check(
    "status_input_order_normalized",
    ordered_one.status_evidence
    == ordered_two.status_evidence,
)

check(
    "status_input_order_snapshot_equal",
    ordered_one.progress_snapshot_id
    == ordered_two.progress_snapshot_id,
)


# ============================================================
# 6. MISSING EVIDENCE MATRIX
# ============================================================

none_status = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=order_plan,
        status_evidence=None,
    )
)


check(
    "none_status_all_missing",
    none_status.missing_status_job_ids
    == order_plan.job_ids,
)

check(
    "none_status_not_started_zero",
    none_status.not_started_job_count
    == 0,
)

check(
    "none_status_pending_zero",
    none_status.pending_job_count
    == 0,
)

check(
    "none_status_running_zero",
    none_status.in_progress_job_count
    == 0,
)

check(
    "none_status_terminal_zero",
    none_status.terminal_job_count
    == 0,
)

check(
    "none_status_ratio_zero_over_three",
    none_status.terminal_progress_ratio
    == (
        0,
        3,
    ),
)


# ============================================================
# 7. INVALID STATUS CONTAINER ATTACKS
# ============================================================

for index, bad in enumerate(
    (
        True,
        False,

        0,
        1,
        -1,
        1.0,

        "a",
        b"a",
        bytearray(b"a"),

        object(),
    ),
    start=1,
):

    try:

        progress.track_universal_orchestration_progress(
            execution_plan=order_plan,
            status_evidence=bad,
        )

    except progress.UniversalOrchestrationProgressTrackingError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_status_container_"
        + str(index),
        rejected,
    )


# ============================================================
# 8. INVALID STATUS ENTRY SHAPES
# ============================================================

invalid_entries = (
    ("a",),

    (
        "a",
        "running",
        "extra",
    ),

    "a",

    123,

    object(),
)


for index, bad_entry in enumerate(
    invalid_entries,
    start=1,
):

    try:

        progress.track_universal_orchestration_progress(
            execution_plan=order_plan,
            status_evidence=(
                bad_entry,
            ),
        )

    except progress.UniversalOrchestrationProgressTrackingError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_status_entry_shape_"
        + str(index),
        rejected,
    )


# ============================================================
# 9. INVALID JOB IDs
# ============================================================

invalid_job_ids = (
    None,
    True,
    False,

    0,
    1,
    1.0,

    "",
    " ",
    "\t",
    "\n",

    "a b",
    "a\tb",
    "a\nb",

    b"a",
    bytearray(b"a"),

    (),
    [],
    {},
    set(),

    object(),
)


for index, bad in enumerate(
    invalid_job_ids,
    start=1,
):

    try:

        progress.track_universal_orchestration_progress(
            execution_plan=order_plan,
            status_evidence=(
                (
                    bad,
                    "running",
                ),
            ),
        )

    except progress.UniversalOrchestrationProgressTrackingError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_status_job_id_"
        + str(index),
        rejected,
        repr(
            bad
        ),
    )


# ============================================================
# 10. TOO-LONG JOB ID
# ============================================================

try:

    progress.track_universal_orchestration_progress(
        execution_plan=order_plan,
        status_evidence={
            "x" * 201:
                "running",
        },
    )

except progress.UniversalOrchestrationProgressTrackingError:

    too_long_rejected = True

else:

    too_long_rejected = False


check(
    "too_long_status_job_id_rejected",
    too_long_rejected,
)


# ============================================================
# 11. DUPLICATE NORMALIZED JOB IDS
# ============================================================

try:

    progress.track_universal_orchestration_progress(
        execution_plan=order_plan,
        status_evidence=(
            (
                "a",
                "queued",
            ),
            (
                " a ",
                "running",
            ),
        ),
    )

except progress.UniversalOrchestrationProgressTrackingError as exc:

    duplicate_rejected = (
        exc.code
        == "duplicate_progress_status_evidence_job_id"
    )

else:

    duplicate_rejected = False


check(
    "duplicate_normalized_status_job_rejected",
    duplicate_rejected,
)


# ============================================================
# 12. INVALID STATUS VALUES
# ============================================================

for index, bad in enumerate(
    (
        True,
        False,

        0,
        1,
        -1,
        1.0,
        0.0,

        "",
        "completed",
        "complete",
        "success",
        "error",
        "unknown",
        "skipped",

        [],
        (),
        {},
        set(),

        object(),
    ),
    start=1,
):

    try:

        progress.track_universal_orchestration_progress(
            execution_plan=order_plan,
            status_evidence={
                "a":
                    bad,
            },
        )

    except progress.UniversalOrchestrationProgressTrackingError as exc:

        rejected = (
            exc.code
            == "invalid_progress_status_evidence_value"
        )

    else:

        rejected = False

    check(
        "invalid_status_value_"
        + str(index),
        rejected,
    )


# ============================================================
# 13. OUTSIDE PLAN
# ============================================================

for outside in (
    "outside",
    "not-in-plan",
    "source",
):

    try:

        progress.track_universal_orchestration_progress(
            execution_plan=order_plan,
            status_evidence={
                outside:
                    "running",
            },
        )

    except progress.UniversalOrchestrationProgressTrackingError as exc:

        rejected = (
            exc.code
            == "progress_status_evidence_job_outside_plan"
        )

    else:

        rejected = False

    check(
        "outside_status_rejected_"
        + outside,
        rejected,
    )


# ============================================================
# 14. INVALID EXECUTION PLAN
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

        progress.track_universal_orchestration_progress(
            execution_plan=bad,
            status_evidence=None,
        )

    except progress.UniversalOrchestrationProgressTrackingError as exc:

        rejected = (
            exc.code
            == "invalid_progress_execution_plan"
        )

    else:

        rejected = False

    check(
        "invalid_execution_plan_"
        + str(index),
        rejected,
    )


# ============================================================
# 15. CONDITIONAL CONTAINER ATTACKS
# ============================================================

conditional_plan = make_plan(
    jobs_tuple=(
        make_job(
            job_id="source",
        ),

        make_job(
            job_id="a",
            dependencies=("source",),
        ),

        make_job(
            job_id="b",
            dependencies=("source",),
        ),
    ),
    run_id="conditional-container",
)


conditional_decision = decision_for(
    plan=conditional_plan,
    source_job_id="source",
    evidence={
        "a": True,
        "b": False,
    },
)


for index, bad in enumerate(
    (
        True,
        False,

        0,
        1,
        1.0,

        "decision",
        b"decision",
        bytearray(b"decision"),

        {},
        object(),
    ),
    start=1,
):

    try:

        progress.track_universal_orchestration_progress(
            execution_plan=conditional_plan,
            conditional_branching_decisions=bad,
        )

    except progress.UniversalOrchestrationProgressTrackingError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_conditional_container_"
        + str(index),
        rejected,
    )


# ============================================================
# 16. INVALID CONDITIONAL MEMBERS
# ============================================================

for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
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

        progress.track_universal_orchestration_progress(
            execution_plan=conditional_plan,
            conditional_branching_decisions=(
                bad,
            ),
        )

    except progress.UniversalOrchestrationProgressTrackingError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_conditional_member_"
        + str(index),
        rejected,
    )


# ============================================================
# 17. MULTIPLE CONDITIONAL LOCI
#
# root
#  ├─ a
#  │  ├─ a1
#  │  └─ a2
#  └─ b
#     ├─ b1
#     └─ b2
#
# root: a selected, b selected
# a: a1 selected, a2 excluded
# b: b1 unresolved, b2 selected
# ============================================================

multi_plan = make_plan(
    jobs_tuple=(
        make_job(
            job_id="root",
        ),

        make_job(
            job_id="a",
            dependencies=("root",),
        ),

        make_job(
            job_id="b",
            dependencies=("root",),
        ),

        make_job(
            job_id="a1",
            dependencies=("a",),
        ),

        make_job(
            job_id="a2",
            dependencies=("a",),
        ),

        make_job(
            job_id="b1",
            dependencies=("b",),
        ),

        make_job(
            job_id="b2",
            dependencies=("b",),
        ),
    ),
    run_id="multiple-loci",
)


root_decision = decision_for(
    plan=multi_plan,
    source_job_id="root",
    evidence={
        "a": True,
        "b": True,
    },
)


a_decision = decision_for(
    plan=multi_plan,
    source_job_id="a",
    evidence={
        "a1": True,
        "a2": False,
    },
)


b_decision = decision_for(
    plan=multi_plan,
    source_job_id="b",
    evidence={
        "b1": None,
        "b2": True,
    },
)


multi = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=multi_plan,
        conditional_branching_decisions=(
            b_decision,
            root_decision,
            a_decision,
        ),
    )
)


check(
    "conditional_decisions_sorted_by_source",
    tuple(
        decision.source_job_id
        for decision
        in multi.conditional_branching_decisions
    )
    == (
        "a",
        "b",
        "root",
    ),
)

check(
    "multi_definite_exact",
    multi.definite_effective_job_ids
    == (
        "a",
        "a1",
        "b",
        "b2",
        "root",
    ),
    multi.definite_effective_job_ids,
)

check(
    "multi_possible_exact",
    multi.possible_effective_job_ids
    == (
        "a",
        "a1",
        "b",
        "b1",
        "b2",
        "root",
    ),
    multi.possible_effective_job_ids,
)

check(
    "multi_unresolved_exact",
    multi.unresolved_effective_job_ids
    == ("b1",),
)

check(
    "multi_excluded_exact",
    multi.excluded_effective_job_ids
    == ("a2",),
)


# ============================================================
# 18. SHARED DESCENDANT VIA ALTERNATE SELECTED PATH
# ============================================================

shared_plan = make_plan(
    jobs_tuple=(
        make_job(
            job_id="root",
        ),

        make_job(
            job_id="a",
            dependencies=("root",),
        ),

        make_job(
            job_id="b",
            dependencies=("root",),
        ),

        make_job(
            job_id="x",
            dependencies=(
                "a",
                "b",
            ),
        ),

        make_job(
            job_id="a_only",
            dependencies=("a",),
        ),

        make_job(
            job_id="b_only",
            dependencies=("b",),
        ),
    ),
    run_id="shared-alt-path",
)


shared_decision = decision_for(
    plan=shared_plan,
    source_job_id="root",
    evidence={
        "a": False,
        "b": True,
    },
)


shared_snapshot = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=shared_plan,
        conditional_branching_decisions=(
            shared_decision,
        ),
    )
)


check(
    "shared_alt_x_effective",
    "x"
    in shared_snapshot.definite_effective_job_ids,
)

check(
    "shared_alt_a_only_excluded",
    "a_only"
    in shared_snapshot.excluded_effective_job_ids,
)

check(
    "shared_alt_b_only_effective",
    "b_only"
    in shared_snapshot.definite_effective_job_ids,
)


# ============================================================
# 19. SHARED DESCENDANT VIA UNRESOLVED PATH
# ============================================================

shared_unresolved = decision_for(
    plan=shared_plan,
    source_job_id="root",
    evidence={
        "a": False,
        "b": None,
    },
)


shared_unresolved_snapshot = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=shared_plan,
        conditional_branching_decisions=(
            shared_unresolved,
        ),
    )
)


check(
    "shared_unresolved_x_possible",
    "x"
    in shared_unresolved_snapshot.possible_effective_job_ids,
)

check(
    "shared_unresolved_x_not_definite",
    "x"
    not in shared_unresolved_snapshot.definite_effective_job_ids,
)

check(
    "shared_unresolved_x_unresolved",
    "x"
    in shared_unresolved_snapshot.unresolved_effective_job_ids,
)


# ============================================================
# 20. EXCLUSION PROPAGATION THROUGH DEEP CHAIN
# ============================================================

deep_plan = make_plan(
    jobs_tuple=(
        make_job(
            job_id="root",
        ),

        make_job(
            job_id="a",
            dependencies=("root",),
        ),

        make_job(
            job_id="b",
            dependencies=("root",),
        ),

        make_job(
            job_id="a1",
            dependencies=("a",),
        ),

        make_job(
            job_id="a2",
            dependencies=("a1",),
        ),

        make_job(
            job_id="a3",
            dependencies=("a2",),
        ),

        make_job(
            job_id="b1",
            dependencies=("b",),
        ),
    ),
    run_id="deep-exclusion",
)


deep_decision = decision_for(
    plan=deep_plan,
    source_job_id="root",
    evidence={
        "a": False,
        "b": True,
    },
)


deep_snapshot = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=deep_plan,
        conditional_branching_decisions=(
            deep_decision,
        ),
    )
)


for job_id in (
    "a",
    "a1",
    "a2",
    "a3",
):

    check(
        "deep_excluded_"
        + job_id,
        job_id
        in deep_snapshot.excluded_effective_job_ids,
    )


check(
    "deep_b_effective",
    "b"
    in deep_snapshot.definite_effective_job_ids,
)

check(
    "deep_b1_effective",
    "b1"
    in deep_snapshot.definite_effective_job_ids,
)


# ============================================================
# 21. DISCONNECTED COMPONENTS REMAIN EFFECTIVE
# ============================================================

disconnected_plan = make_plan(
    jobs_tuple=(
        make_job(
            job_id="r1",
        ),

        make_job(
            job_id="a",
            dependencies=("r1",),
        ),

        make_job(
            job_id="b",
            dependencies=("r1",),
        ),

        make_job(
            job_id="r2",
        ),

        make_job(
            job_id="z",
            dependencies=("r2",),
        ),
    ),
    run_id="disconnected",
)


disconnected_decision = decision_for(
    plan=disconnected_plan,
    source_job_id="r1",
    evidence={
        "a": False,
        "b": True,
    },
)


disconnected = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=disconnected_plan,
        conditional_branching_decisions=(
            disconnected_decision,
        ),
    )
)


check(
    "disconnected_r2_survives",
    "r2"
    in disconnected.definite_effective_job_ids,
)

check(
    "disconnected_z_survives",
    "z"
    in disconnected.definite_effective_job_ids,
)


# ============================================================
# 22. ALL FALSE BRANCH LOCUS
# ============================================================

all_false_plan = make_plan(
    jobs_tuple=(
        make_job(
            job_id="root",
        ),

        make_job(
            job_id="a",
            dependencies=("root",),
        ),

        make_job(
            job_id="b",
            dependencies=("root",),
        ),

        make_job(
            job_id="a1",
            dependencies=("a",),
        ),

        make_job(
            job_id="b1",
            dependencies=("b",),
        ),
    ),
    run_id="all-false",
)


all_false_decision = decision_for(
    plan=all_false_plan,
    source_job_id="root",
    evidence={
        "a": False,
        "b": False,
    },
)


all_false = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=all_false_plan,
        conditional_branching_decisions=(
            all_false_decision,
        ),
    )
)


check(
    "all_false_root_definite",
    all_false.definite_effective_job_ids
    == ("root",),
)

check(
    "all_false_root_possible",
    all_false.possible_effective_job_ids
    == ("root",),
)

check(
    "all_false_descendants_excluded",
    all_false.excluded_effective_job_ids
    == (
        "a",
        "a1",
        "b",
        "b1",
    ),
    all_false.excluded_effective_job_ids,
)


# ============================================================
# 23. ALL UNRESOLVED BRANCH LOCUS
# ============================================================

all_unresolved_decision = decision_for(
    plan=all_false_plan,
    source_job_id="root",
    evidence={
        "a": None,
        "b": None,
    },
)


all_unresolved = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=all_false_plan,
        conditional_branching_decisions=(
            all_unresolved_decision,
        ),
    )
)


check(
    "all_unresolved_root_only_definite",
    all_unresolved.definite_effective_job_ids
    == ("root",),
)

check(
    "all_unresolved_all_possible",
    all_unresolved.possible_effective_job_ids
    == all_false_plan.job_ids,
)

check(
    "all_unresolved_descendants_unresolved",
    all_unresolved.unresolved_effective_job_ids
    == (
        "a",
        "a1",
        "b",
        "b1",
    ),
)


# ============================================================
# 24. STATUS COUNTS USE POSSIBLE EFFECTIVE POPULATION
# ============================================================

population_snapshot = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=all_false_plan,
        status_evidence={
            "root": "succeeded",
            "a": "succeeded",
            "a1": "succeeded",
            "b": "failed",
            "b1": "running",
        },
        conditional_branching_decisions=(
            all_false_decision,
        ),
    )
)


check(
    "excluded_statuses_not_counted",
    population_snapshot.successful_job_count
    == 1,
)

check(
    "excluded_failure_not_counted",
    population_snapshot.terminal_unsuccessful_job_count
    == 0,
)

check(
    "possible_denominator_one",
    population_snapshot.terminal_progress_denominator
    == 1,
)

check(
    "possible_numerator_one",
    population_snapshot.terminal_progress_numerator
    == 1,
)


# ============================================================
# 25. UNRESOLVED JOBS REMAIN IN DENOMINATOR
# ============================================================

unresolved_population = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=all_false_plan,
        status_evidence={
            "root": "succeeded",
            "a": "created",
            "a1": "created",
            "b": "created",
            "b1": "created",
        },
        conditional_branching_decisions=(
            all_unresolved_decision,
        ),
    )
)


check(
    "unresolved_denominator_all_jobs",
    unresolved_population.terminal_progress_denominator
    == 5,
)

check(
    "unresolved_numerator_root_only",
    unresolved_population.terminal_progress_numerator
    == 1,
)

check(
    "unresolved_activity_true",
    unresolved_population.has_unresolved_branch_activity,
)


# ============================================================
# 26. ZERO-DEPENDENCY SINGLE JOB
# ============================================================

single_plan = make_plan(
    jobs_tuple=(
        make_job(
            job_id="only",
        ),
    ),
    run_id="single-job",
)


single = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=single_plan,
        status_evidence={
            "only":
                "succeeded",
        },
    )
)


check(
    "single_definite",
    single.definite_effective_job_ids
    == ("only",),
)

check(
    "single_possible",
    single.possible_effective_job_ids
    == ("only",),
)

check(
    "single_ratio_one_one",
    single.terminal_progress_ratio
    == (
        1,
        1,
    ),
)


# ============================================================
# 27. TERMINAL UNSUCCESSFUL MATRIX
# ============================================================

for status in (
    jobs.UniversalJobStatus.FAILED,
    jobs.UniversalJobStatus.CANCELLED,
    jobs.UniversalJobStatus.DEAD_LETTER,
    jobs.UniversalJobStatus.EXPIRED,
):

    snapshot = (
        progress
        .track_universal_orchestration_progress(
            execution_plan=single_plan,
            status_evidence={
                "only":
                    status,
            },
        )
    )

    check(
        "terminal_unsuccessful_counts_terminal_"
        + status.value,
        snapshot.terminal_job_count
        == 1,
    )

    check(
        "terminal_unsuccessful_not_success_"
        + status.value,
        snapshot.successful_job_count
        == 0,
    )

    check(
        "terminal_unsuccessful_bucket_"
        + status.value,
        snapshot.terminal_unsuccessful_job_count
        == 1,
    )


# ============================================================
# 28. SOURCE/BRANCH JOB STATUS IRRELEVANCE TO TOPOLOGY
# ============================================================

for status in jobs.UniversalJobStatus:

    status_topology_plan = make_plan(
        jobs_tuple=(
            make_job(
                job_id="root",
                status=status,
            ),

            make_job(
                job_id="a",
                dependencies=("root",),
                status=status,
            ),

            make_job(
                job_id="b",
                dependencies=("root",),
                status=status,
            ),
        ),
        run_id=(
            "topology-status-"
            + status.value
        ),
    )

    status_decision = decision_for(
        plan=status_topology_plan,
        source_job_id="root",
        evidence={
            "a": False,
            "b": True,
        },
    )

    topology_snapshot = (
        progress
        .track_universal_orchestration_progress(
            execution_plan=status_topology_plan,
            conditional_branching_decisions=(
                status_decision,
            ),
        )
    )

    check(
        "plan_job_status_irrelevant_to_effective_topology_"
        + status.value,
        topology_snapshot.definite_effective_job_ids
        == (
            "b",
            "root",
        ),
    )


# ============================================================
# 29. PRIORITY IRRELEVANCE
# ============================================================

for priority in jobs.UniversalJobPriority:

    priority_plan = make_plan(
        jobs_tuple=(
            make_job(
                job_id="root",
                priority=priority,
            ),

            make_job(
                job_id="a",
                dependencies=("root",),
                priority=priority,
            ),

            make_job(
                job_id="b",
                dependencies=("root",),
                priority=priority,
            ),
        ),
        run_id=(
            "priority-"
            + str(
                priority.value
            )
        ),
    )

    priority_decision = decision_for(
        plan=priority_plan,
        source_job_id="root",
        evidence={
            "a": False,
            "b": True,
        },
    )

    priority_snapshot = (
        progress
        .track_universal_orchestration_progress(
            execution_plan=priority_plan,
            conditional_branching_decisions=(
                priority_decision,
            ),
        )
    )

    check(
        "priority_irrelevant_"
        + str(
            priority.value
        ),
        priority_snapshot.definite_effective_job_ids
        == (
            "b",
            "root",
        ),
    )


# ============================================================
# 30. CROSS-PLAN / CROSS-RUN DECISION REJECT
# ============================================================

same_shape_other_run = make_plan(
    jobs_tuple=(
        make_job(
            job_id="source",
        ),
        make_job(
            job_id="a",
            dependencies=("source",),
        ),
        make_job(
            job_id="b",
            dependencies=("source",),
        ),
    ),
    run_id="same-shape-other-run",
)


other_decision = decision_for(
    plan=same_shape_other_run,
    source_job_id="source",
    evidence={
        "a": True,
        "b": False,
    },
)


try:

    progress.track_universal_orchestration_progress(
        execution_plan=conditional_plan,
        conditional_branching_decisions=(
            other_decision,
        ),
    )

except progress.UniversalOrchestrationProgressTrackingError as exc:

    cross_run_rejected = (
        exc.code
        == "progress_conditional_decision_plan_mismatch"
    )

else:

    cross_run_rejected = False


check(
    "cross_run_same_shape_decision_rejected",
    cross_run_rejected,
)


# ============================================================
# 31. DUPLICATE CONDITIONAL LOCUS
# ============================================================

conditional_decision_reverse = decision_for(
    plan=conditional_plan,
    source_job_id="source",
    evidence={
        "a": False,
        "b": True,
    },
)


try:

    progress.track_universal_orchestration_progress(
        execution_plan=conditional_plan,
        conditional_branching_decisions=(
            conditional_decision,
            conditional_decision_reverse,
        ),
    )

except progress.UniversalOrchestrationProgressTrackingError as exc:

    duplicate_source_rejected = (
        exc.code
        == "duplicate_progress_conditional_source"
    )

else:

    duplicate_source_rejected = False


check(
    "duplicate_conditional_locus_rejected",
    duplicate_source_rejected,
)


# ============================================================
# 32. STORED FIELDS EXACT
# ============================================================

field_names = tuple(
    field.name
    for field
    in fields(
        progress.UniversalOrchestrationProgressSnapshot
    )
)


check(
    "stored_fields_exact",
    field_names
    == (
        "execution_plan",
        "status_evidence",
        "conditional_branching_decisions",
        "schema_version",
    ),
    field_names,
)


for forbidden in (
    "identity",

    "structural_job_ids",
    "structural_total_job_count",

    "status_evidence_map",
    "branch_edge_dispositions",

    "definite_effective_job_ids",
    "possible_effective_job_ids",
    "unresolved_effective_job_ids",
    "excluded_effective_job_ids",

    "definite_effective_job_count",
    "possible_effective_job_count",
    "unresolved_effective_job_count",
    "excluded_effective_job_count",

    "structural_status_buckets",
    "effective_status_buckets",

    "not_started_job_ids",
    "pending_job_ids",
    "in_progress_job_ids",
    "suspended_job_ids",

    "successful_job_ids",
    "terminal_unsuccessful_job_ids",
    "terminal_job_ids",
    "missing_status_job_ids",

    "terminal_progress_numerator",
    "terminal_progress_denominator",
    "terminal_progress_ratio",

    "has_unresolved_branch_activity",
    "has_missing_status_evidence",

    "progress_snapshot_id",

    "state",
    "completion",
    "success",
    "failure",

    "queue_id",
    "worker_id",
    "lease_id",

    "created_at",
    "updated_at",
):

    check(
        "forbidden_stored_"
        + forbidden,
        forbidden
        not in field_names,
    )


# ============================================================
# 33. IMMUTABILITY
# ============================================================

immutability_snapshot = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=conditional_plan,
        status_evidence={
            "source": "succeeded",
            "a": "running",
            "b": None,
        },
        conditional_branching_decisions=(
            conditional_decision,
        ),
    )
)


for field in fields(
    immutability_snapshot
):

    try:

        setattr(
            immutability_snapshot,
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
# 34. MAPPING PROXY IMMUTABILITY
# ============================================================

mapping_properties = (
    (
        "status_evidence_map",
        immutability_snapshot.status_evidence_map,
    ),

    (
        "branch_edge_dispositions",
        immutability_snapshot.branch_edge_dispositions,
    ),

    (
        "structural_status_buckets",
        immutability_snapshot.structural_status_buckets,
    ),

    (
        "effective_status_buckets",
        immutability_snapshot.effective_status_buckets,
    ),
)


for name, mapping in mapping_properties:

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
            "__attack__"
        ] = "x"

    except TypeError:

        immutable = True

    else:

        immutable = False

    check(
        name
        + "_immutable",
        immutable,
    )


# ============================================================
# 35. SNAPSHOT ID DETERMINISM
# ============================================================

snapshot_ids = tuple(
    progress
    .track_universal_orchestration_progress(
        execution_plan=conditional_plan,
        status_evidence={
            "source": "succeeded",
            "a": "running",
            "b": None,
        },
        conditional_branching_decisions=(
            conditional_decision,
        ),
    )
    .progress_snapshot_id
    for _
    in range(
        20
    )
)


check(
    "snapshot_id_repeat_deterministic",
    len(
        set(
            snapshot_ids
        )
    )
    == 1,
)

check(
    "snapshot_id_length_64",
    len(
        snapshot_ids[
            0
        ]
    )
    == 64,
    snapshot_ids[
        0
    ],
)

check(
    "snapshot_id_upper_hex",
    all(
        character
        in "0123456789ABCDEF"
        for character
        in snapshot_ids[
            0
        ]
    ),
)


# ============================================================
# 36. SNAPSHOT ID STATUS SENSITIVITY
# ============================================================

status_a = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=conditional_plan,
        status_evidence={
            "source": "succeeded",
            "a": "running",
            "b": None,
        },
        conditional_branching_decisions=(
            conditional_decision,
        ),
    )
    .progress_snapshot_id
)


status_b = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=conditional_plan,
        status_evidence={
            "source": "succeeded",
            "a": "succeeded",
            "b": None,
        },
        conditional_branching_decisions=(
            conditional_decision,
        ),
    )
    .progress_snapshot_id
)


check(
    "snapshot_id_status_sensitive",
    status_a
    != status_b,
)


# ============================================================
# 37. SNAPSHOT ID BRANCH SENSITIVITY
# ============================================================

branch_a = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=conditional_plan,
        conditional_branching_decisions=(
            conditional_decision,
        ),
    )
    .progress_snapshot_id
)


branch_b = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=conditional_plan,
        conditional_branching_decisions=(
            conditional_decision_reverse,
        ),
    )
    .progress_snapshot_id
)


check(
    "snapshot_id_branch_sensitive",
    branch_a
    != branch_b,
)


# ============================================================
# 38. SNAPSHOT ID RUN IDENTITY SENSITIVITY
# ============================================================

run_a_plan = make_plan(
    jobs_tuple=(
        make_job(
            job_id="x",
        ),
    ),
    run_id="run-a",
)

run_b_plan = make_plan(
    jobs_tuple=(
        make_job(
            job_id="x",
        ),
    ),
    run_id="run-b",
)


run_a_id = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=run_a_plan,
        status_evidence={
            "x": "running",
        },
    )
    .progress_snapshot_id
)


run_b_id = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=run_b_plan,
        status_evidence={
            "x": "running",
        },
    )
    .progress_snapshot_id
)


check(
    "snapshot_id_run_sensitive",
    run_a_id
    != run_b_id,
)


# ============================================================
# 39. INPUT DECISION ORDER INDEPENDENCE
# ============================================================

decision_order_one = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=multi_plan,
        conditional_branching_decisions=(
            root_decision,
            a_decision,
            b_decision,
        ),
    )
)


decision_order_two = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=multi_plan,
        conditional_branching_decisions=(
            b_decision,
            a_decision,
            root_decision,
        ),
    )
)


check(
    "decision_order_normalized_equal",
    decision_order_one.conditional_branching_decisions
    ==
    decision_order_two.conditional_branching_decisions,
)

check(
    "decision_order_snapshot_equal",
    decision_order_one.progress_snapshot_id
    ==
    decision_order_two.progress_snapshot_id,
)


# ============================================================
# 40. EXECUTION PLAN NOT MUTATED
# ============================================================

plan_before = (
    multi_plan.job_ids,
    multi_plan.dependency_map,
    multi_plan.dependent_map,
    multi_plan.execution_waves,
    multi_plan.topological_order,
)


_ = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=multi_plan,
        status_evidence=None,
        conditional_branching_decisions=(
            root_decision,
            a_decision,
            b_decision,
        ),
    )
)


plan_after = (
    multi_plan.job_ids,
    multi_plan.dependency_map,
    multi_plan.dependent_map,
    multi_plan.execution_waves,
    multi_plan.topological_order,
)


check(
    "execution_plan_not_mutated",
    plan_before
    == plan_after,
)


# ============================================================
# 41. CONDITIONAL DECISIONS NOT MUTATED
# ============================================================

decision_before = tuple(
    (
        decision.source_job_id,
        decision.condition_evidence,
        decision.branch_decision_id,
    )
    for decision
    in (
        root_decision,
        a_decision,
        b_decision,
    )
)


_ = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=multi_plan,
        conditional_branching_decisions=(
            root_decision,
            a_decision,
            b_decision,
        ),
    )
)


decision_after = tuple(
    (
        decision.source_job_id,
        decision.condition_evidence,
        decision.branch_decision_id,
    )
    for decision
    in (
        root_decision,
        a_decision,
        b_decision,
    )
)


check(
    "conditional_decisions_not_mutated",
    decision_before
    == decision_after,
)


# ============================================================
# 42. EXPLANATION CONTRACT
# ============================================================

explanation = (
    progress
    .explain_universal_orchestration_progress_tracking_v1()
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
    explanation.get(
        "phase"
    )
    == "5.1.11",
)

check(
    "explanation_component_exact",
    explanation.get(
        "component"
    )
    == "Universal Orchestration Progress Tracking",
)

check(
    "explanation_stored_fields_exact",
    explanation.get(
        "stored_fields"
    )
    == (
        "execution_plan",
        "status_evidence",
        "conditional_branching_decisions",
        "schema_version",
    ),
)

check(
    "explanation_terminal_rule",
    "FAILED"
    in explanation.get(
        "terminal_progress_rule",
        "",
    ),
)

check(
    "explanation_shared_descendant_rule",
    "another non-excluded path"
    in explanation.get(
        "shared_descendant_rule",
        "",
    ),
)

check(
    "explanation_dag_boundary",
    "5.1.5"
    in explanation.get(
        "dag_boundary",
        "",
    ),
)

check(
    "explanation_conditional_boundary",
    "5.1.10"
    in explanation.get(
        "conditional_boundary",
        "",
    ),
)

check(
    "explanation_state_boundary",
    "5.1.3"
    in explanation.get(
        "state_boundary",
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
    "explanation_recovery_boundary",
    "5.1.13"
    in explanation.get(
        "recovery_boundary",
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

check(
    "explanation_completion_boundary",
    "5.1.15"
    in explanation.get(
        "completion_boundary",
        "",
    ),
)

check(
    "explanation_evidence_boundary",
    "5.1.17"
    in explanation.get(
        "evidence_record_boundary",
        "",
    ),
)


# ============================================================
# 43. REQUIRED PROHIBITIONS
# ============================================================

required_prohibitions = (
    "does not read runtime storage",
    "does not read queue state",
    "does not read worker state",
    "does not read lease state",
    "does not inspect UniversalJob.status directly",
    "does not inspect UniversalJob.progress directly",
    "does not mutate UniversalJob.status",
    "does not mutate UniversalJob.progress",
    "does not perform dependency resolution",
    "does not evaluate stage readiness",
    "does not evaluate runtime handoff",
    "does not recompute fan-out",
    "does not recompute fan-in",
    "does not reevaluate conditional evidence",
    "does not mutate execution-plan topology",
    "does not enqueue jobs",
    "does not schedule jobs",
    "does not dequeue jobs",
    "does not claim jobs",
    "does not assign workers",
    "does not acquire leases",
    "does not dispatch runtime handlers",
    "does not execute jobs",
    "does not transition orchestration state",
    "does not determine orchestration completion",
    "does not determine orchestration success",
    "does not determine orchestration failure",
    "does not suspend or resume orchestration",
    "does not initiate recovery",
    "does not access Runtime State Store",
    "does not persist progress",
    "does not record permanent evidence",
    "does not use wall clock",
    "does not perform filesystem I/O",
    "does not perform network I/O",
    "does not perform database I/O",
    "does not import Universal Coordination Framework",
    "does not invoke pipeline coordinators",
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
        + str(
            index
        ),
        item
        in prohibitions,
        item,
    )


# ============================================================
# 44. IMPORT BOUNDARY
# ============================================================

source = PROGRESS_PATH.read_text(
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
        "backend.server.runtime.universal_orchestration.contract",
        "backend.server.runtime.universal_orchestration.execution_planning",
        "backend.server.runtime.universal_orchestration.conditional_branching",
    ],
    backend_imports,
)


# ============================================================
# 45. FORBIDDEN IMPORTS
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

    "os",
    "subprocess",
    "socket",
    "sqlite3",

    "backend.server.runtime.universal_queue",
    "backend.server.runtime.universal_worker",

    "backend.server.runtime.universal_runtime_registration",
    "backend.server.runtime.universal_runtime_worker_v1",
    "backend.server.runtime.universal_runtime_infrastructure",

    "backend.server.runtime.universal_orchestration.state_model",
    "backend.server.runtime.universal_orchestration.dependency_resolution",
    "backend.server.runtime.universal_orchestration.stage_readiness",
    "backend.server.runtime.universal_orchestration.runtime_handoff",
    "backend.server.runtime.universal_orchestration.fan_out_coordination",
    "backend.server.runtime.universal_orchestration.fan_in_coordination",

    "backend.server.orchestration",
    "backend.server.coordination",

    "backend.server.jobs.universal_knowledge_orchestrator",
    "backend.server.pipelines.connect_domain.coordinator",
):

    matches = tuple(
        imported
        for imported
        in all_imports
        if (
            imported
            == forbidden_module
            or
            imported.startswith(
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
# 46. FORBIDDEN CALLS
# ============================================================

forbidden_calls = {
    "eval",
    "exec",
    "compile",

    "open",
    "read_text",
    "write_text",
    "mkdir",
    "unlink",
    "remove",

    "getenv",

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
# 47. FORBIDDEN DIRECT ATTRIBUTE ACCESS
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
    "progress",
    "payload",
    "payload_reference",
    "metadata",
    "result_reference",

    "priority",
    "created_at",
    "scheduled_at",

    "worker_id",
    "queue_id",
    "lease_id",

    "readiness",
    "handoff",
):

    check(
        "forbidden_attribute_absent_"
        + forbidden_attr,
        forbidden_attr
        not in attrs,
    )


# ============================================================
# 48. NO FLOAT PERCENTAGE / COMPLETION STATE SYMBOLS
# ============================================================

check(
    "no_progress_percent_symbol",
    "progress_percent"
    not in source,
)

check(
    "no_percentage_symbol",
    "percentage"
    not in source.lower(),
)

check(
    "no_orchestration_complete_classification",
    "UniversalOrchestrationState.SUCCEEDED"
    not in source,
)

check(
    "no_orchestration_failed_classification",
    "UniversalOrchestrationState.FAILED"
    not in source,
)


# ============================================================
# 49. PROTECTED AUTHORITY MATRIX
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
# 50. FINAL AST
# ============================================================

final_ast = ast_sha(
    PROGRESS_PATH
)


check(
    "progress_ast_final",
    final_ast
    == EXPECTED_PROGRESS_AST,
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
        "PHASE 5.1.11 — UNIVERSAL ORCHESTRATION "
        "PROGRESS TRACKING ADVERSARIAL REGRESSION"
    ),

    "=" * 118,

    "",

    (
        "PROGRESS TRACKING AST SHA256: "
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
            "ADVERSARIAL ORCHESTRATION PROGRESS TRACKING REGRESSION: "
            + (
                "PASS"
                if passed == total
                else "FAIL"
            )
        ),

        (
            "CHECKS PASSED: "
            + str(
                passed
            )
            + "/"
            + str(
                total
            )
        ),

        "",

        "PROGRESS TRACKING AUTHORITY MODIFIED: NO",
        "5.1.1–5.1.10 FROZEN AUTHORITIES MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "STATUS PARTITION COMPLETE: YES",
        "STATUS PARTITION DISJOINT: YES",
        "ALL UNIVERSAL JOB STATUSES VERIFIED: YES",

        "",

        "MISSING STATUS == CREATED: NO",
        "EXTRANEOUS STATUS EVIDENCE ACCEPTED: NO",
        "DUPLICATE NORMALIZED STATUS IDS ACCEPTED: NO",

        "",

        "ZERO CONDITIONAL LOCI SUPPORTED: YES",
        "ONE CONDITIONAL LOCUS SUPPORTED: YES",
        "MULTIPLE CONDITIONAL LOCI SUPPORTED: YES",
        "DUPLICATE CONDITIONAL SOURCE ACCEPTED: NO",
        "CROSS-RUN DECISION ACCEPTED: NO",

        "",

        "DEFINITE REACHABILITY:",
        "  UNCONDITIONAL + SELECTED",

        "POSSIBLE REACHABILITY:",
        "  UNCONDITIONAL + SELECTED + UNRESOLVED",

        "EXCLUDED EDGE CONTRIBUTES REACHABILITY: NO",

        "",

        "DEEP EXCLUSION PROPAGATION VERIFIED: YES",
        "SHARED DESCENDANT ALTERNATE-PATH SURVIVAL VERIFIED: YES",
        "UNRESOLVED DESCENDANT PROPAGATION VERIFIED: YES",
        "DISCONNECTED COMPONENT PRESERVATION VERIFIED: YES",

        "",

        "EXCLUDED JOB STATUS COUNTS TOWARD EFFECTIVE PROGRESS: NO",
        "UNRESOLVED POSSIBLE JOB COUNTS IN DENOMINATOR: YES",

        "",

        "FAILED/CANCELLED/DEAD_LETTER/EXPIRED COUNT AS TERMINATED WORK: YES",
        "FAILED/CANCELLED/DEAD_LETTER/EXPIRED COUNT AS SUCCESS: NO",

        "",

        "CANONICAL FLOAT PERCENTAGE STORED: NO",
        "TERMINATION PROGRESS: INTEGER NUMERATOR / DENOMINATOR",

        "",

        "EXECUTION PLAN MUTATED: NO",
        "CONDITIONAL DECISIONS MUTATED: NO",

        "",

        "SNAPSHOT ID DETERMINISTIC: YES",
        "SNAPSHOT ID STATUS SENSITIVE: YES",
        "SNAPSHOT ID BRANCH SENSITIVE: YES",
        "SNAPSHOT ID RUN SENSITIVE: YES",

        "",

        "DIRECT UniversalJob.progress ACCESS: NO",
        "RUNTIME STORAGE ACCESS: NO",
        "QUEUE/WORKER/LEASE ACCESS: NO",

        "",

        "DEPENDENCY RESOLUTION: NO",
        "READINESS EVALUATION: NO",
        "HANDOFF EVALUATION: NO",
        "CONDITIONS REEVALUATED: NO",

        "",

        "QUEUE ACTIVITY: NO",
        "WORKER ACTIVITY: NO",
        "LEASE ACTIVITY: NO",
        "HANDLER DISPATCH: NO",
        "JOB EXECUTION: NO",

        "",

        "UNIVERSAL JOB MUTATION: NO",
        "ORCHESTRATION STATE TRANSITION: NO",

        "",

        "SUSPENSION/RESUME: NO",
        "RECOVERY: NO",
        "PERSISTENCE: NO",
        "COMPLETION RESOLUTION: NO",
        "SUCCESS/FAILURE RESOLUTION: NO",
        "PERMANENT EVIDENCE RECORDING: NO",

        "",

        "WALL CLOCK: NO",
        "FILESYSTEM/NETWORK/DATABASE I/O: NO",

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
        "Phase 5.1.11 adversarial regression failed."
    )
