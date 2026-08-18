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
    / "phase_5_1_11_progress_tracking_initial_implementation.txt"
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

    "job_contract": (
        ROOT / "backend/server/runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
    ),

    "queue_certification": (
        ROOT / "backend/server/runtime/universal_queue/certification.py",
        "6ED39655147D2B331E02101F5EA23E68CF71447353C0D294E170281AE40C0D4C",
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

    tree = ast.parse(source)

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
            "Protected authority changed before 5.1.11: "
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

fanout = importlib.import_module(
    "backend.server.runtime.universal_orchestration.fan_out_coordination"
)

conditional = importlib.import_module(
    "backend.server.runtime.universal_orchestration.conditional_branching"
)

progress = importlib.import_module(
    "backend.server.runtime.universal_orchestration.progress_tracking"
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
# AUTHORITY CONSTANTS
# ============================================================

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
    "hash_exact",
    progress.UNIVERSAL_ORCHESTRATION_PROGRESS_SNAPSHOT_HASH_ALGORITHM
    == "sha256",
)


# ============================================================
# STATUS PARTITION
# ============================================================

check(
    "not_started_exact",
    progress.NOT_STARTED_UNIVERSAL_JOB_STATUSES
    == frozenset(
        {
            jobs.UniversalJobStatus.CREATED,
        }
    ),
)

check(
    "pending_exact",
    progress.PENDING_UNIVERSAL_JOB_STATUSES
    == frozenset(
        {
            jobs.UniversalJobStatus.QUEUED,
            jobs.UniversalJobStatus.SCHEDULED,
        }
    ),
)

check(
    "in_progress_exact",
    progress.IN_PROGRESS_UNIVERSAL_JOB_STATUSES
    == frozenset(
        {
            jobs.UniversalJobStatus.LEASED,
            jobs.UniversalJobStatus.RUNNING,
        }
    ),
)

check(
    "suspended_exact",
    progress.SUSPENDED_UNIVERSAL_JOB_STATUSES
    == frozenset(
        {
            jobs.UniversalJobStatus.SUSPENDED,
        }
    ),
)

check(
    "terminal_success_exact",
    progress.TERMINAL_SUCCESS_UNIVERSAL_JOB_STATUSES
    == frozenset(
        {
            jobs.UniversalJobStatus.SUCCEEDED,
        }
    ),
)

check(
    "terminal_unsuccessful_exact",
    progress.TERMINAL_UNSUCCESSFUL_UNIVERSAL_JOB_STATUSES
    == frozenset(
        {
            jobs.UniversalJobStatus.FAILED,
            jobs.UniversalJobStatus.CANCELLED,
            jobs.UniversalJobStatus.DEAD_LETTER,
            jobs.UniversalJobStatus.EXPIRED,
        }
    ),
)

check(
    "terminal_progress_exact",
    progress.TERMINAL_PROGRESS_UNIVERSAL_JOB_STATUSES
    == frozenset(
        {
            jobs.UniversalJobStatus.SUCCEEDED,
            jobs.UniversalJobStatus.FAILED,
            jobs.UniversalJobStatus.CANCELLED,
            jobs.UniversalJobStatus.DEAD_LETTER,
            jobs.UniversalJobStatus.EXPIRED,
        }
    ),
)


# ============================================================
# BASIC PLAN — NO CONDITIONAL DECISIONS
# ============================================================

simple_plan = make_plan(
    jobs_tuple=(
        make_job(job_id="a"),

        make_job(
            job_id="b",
            dependencies=("a",),
        ),

        make_job(
            job_id="c",
            dependencies=("b",),
        ),
    ),
    run_id="progress-simple",
)


simple = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=simple_plan,
        status_evidence={
            "a": "succeeded",
            "b": "running",
        },
    )
)


check(
    "structural_ids_exact",
    simple.structural_job_ids
    == simple_plan.job_ids,
)

check(
    "structural_count_exact",
    simple.structural_total_job_count
    == 3,
)

check(
    "no_condition_definite_all",
    simple.definite_effective_job_ids
    == simple_plan.job_ids,
)

check(
    "no_condition_possible_all",
    simple.possible_effective_job_ids
    == simple_plan.job_ids,
)

check(
    "no_condition_unresolved_empty",
    simple.unresolved_effective_job_ids
    == (),
)

check(
    "no_condition_excluded_empty",
    simple.excluded_effective_job_ids
    == (),
)

check(
    "status_normalization_exact",
    simple.status_evidence
    == (
        (
            "a",
            jobs.UniversalJobStatus.SUCCEEDED,
        ),
        (
            "b",
            jobs.UniversalJobStatus.RUNNING,
        ),
        (
            "c",
            None,
        ),
    ),
)

check(
    "successful_exact",
    simple.successful_job_ids
    == ("a",),
)

check(
    "in_progress_exact_ids",
    simple.in_progress_job_ids
    == ("b",),
)

check(
    "missing_exact",
    simple.missing_status_job_ids
    == ("c",),
)

check(
    "terminal_ratio_simple",
    simple.terminal_progress_ratio
    == (
        1,
        3,
    ),
)


# ============================================================
# SHARED DESCENDANT
#
# source -> b
# source -> c
# b,c -> x
# b -> y
#
# b EXCLUDED
# c SELECTED
#
# x remains effective through c
# y is excluded
# ============================================================

shared_plan = make_plan(
    jobs_tuple=(
        make_job(
            job_id="source",
        ),

        make_job(
            job_id="b",
            dependencies=("source",),
        ),

        make_job(
            job_id="c",
            dependencies=("source",),
        ),

        make_job(
            job_id="x",
            dependencies=(
                "b",
                "c",
            ),
        ),

        make_job(
            job_id="y",
            dependencies=("b",),
        ),
    ),
    run_id="progress-shared",
)


shared_fanout = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=shared_plan,
        source_job_id="source",
    )
)


shared_decision = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=shared_fanout,
        condition_evidence={
            "b": False,
            "c": True,
        },
    )
)


shared = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=shared_plan,
        status_evidence={
            "source": "succeeded",
            "b": "created",
            "c": "running",
            "x": "created",
            "y": "created",
        },
        conditional_branching_decisions=(
            shared_decision,
        ),
    )
)


check(
    "shared_definite_exact",
    shared.definite_effective_job_ids
    == (
        "c",
        "source",
        "x",
    ),
    shared.definite_effective_job_ids,
)

check(
    "shared_possible_exact",
    shared.possible_effective_job_ids
    == (
        "c",
        "source",
        "x",
    ),
    shared.possible_effective_job_ids,
)

check(
    "shared_excluded_exact",
    shared.excluded_effective_job_ids
    == (
        "b",
        "y",
    ),
    shared.excluded_effective_job_ids,
)

check(
    "shared_descendant_survives",
    "x"
    in shared.definite_effective_job_ids,
)

check(
    "exclusive_descendant_excluded",
    "y"
    in shared.excluded_effective_job_ids,
)


# ============================================================
# UNRESOLVED BRANCH
# ============================================================

unresolved_decision = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=shared_fanout,
        condition_evidence={
            "b": False,
            "c": None,
        },
    )
)


unresolved = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=shared_plan,
        conditional_branching_decisions=(
            unresolved_decision,
        ),
    )
)


check(
    "unresolved_definite_source_only",
    unresolved.definite_effective_job_ids
    == ("source",),
    unresolved.definite_effective_job_ids,
)

check(
    "unresolved_possible_contains_c",
    "c"
    in unresolved.possible_effective_job_ids,
)

check(
    "unresolved_possible_contains_x",
    "x"
    in unresolved.possible_effective_job_ids,
)

check(
    "unresolved_effective_contains_c",
    "c"
    in unresolved.unresolved_effective_job_ids,
)

check(
    "unresolved_effective_contains_x",
    "x"
    in unresolved.unresolved_effective_job_ids,
)

check(
    "b_excluded_when_false",
    "b"
    in unresolved.excluded_effective_job_ids,
)

check(
    "y_excluded_through_b_only",
    "y"
    in unresolved.excluded_effective_job_ids,
)


# ============================================================
# TERMINAL UNSUCCESSFUL COUNTS AS TERMINATED WORK
# ============================================================

terminal_plan = make_plan(
    jobs_tuple=tuple(
        make_job(
            job_id=job_id,
        )
        for job_id
        in (
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
        )
    ),
    run_id="progress-terminal",
)


terminal = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=terminal_plan,
        status_evidence={
            "a": "succeeded",
            "b": "failed",
            "c": "cancelled",
            "d": "dead_letter",
            "e": "expired",
            "f": "running",
        },
    )
)


check(
    "terminal_success_count",
    terminal.successful_job_count
    == 1,
)

check(
    "terminal_unsuccessful_count",
    terminal.terminal_unsuccessful_job_count
    == 4,
)

check(
    "terminal_total_count",
    terminal.terminal_job_count
    == 5,
)

check(
    "terminal_ratio_exact",
    terminal.terminal_progress_ratio
    == (
        5,
        6,
    ),
)


# ============================================================
# MISSING ≠ CREATED
# ============================================================

missing = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=simple_plan,
        status_evidence=None,
    )
)


check(
    "all_missing",
    missing.missing_status_job_count
    == 3,
)

check(
    "missing_not_not_started",
    missing.not_started_job_count
    == 0,
)


# ============================================================
# EVERY STATUS ACCEPTED
# ============================================================

for status in jobs.UniversalJobStatus:

    one_plan = make_plan(
        jobs_tuple=(
            make_job(
                job_id="only",
            ),
        ),
        run_id=(
            "progress-status-"
            + status.value
        ),
    )

    snapshot = (
        progress
        .track_universal_orchestration_progress(
            execution_plan=one_plan,
            status_evidence={
                "only": status,
            },
        )
    )

    check(
        "status_accepted_"
        + status.value,
        snapshot.status_evidence_map[
            "only"
        ]
        is status,
    )


# ============================================================
# EXTRANEOUS STATUS REJECTED
# ============================================================

try:

    progress.track_universal_orchestration_progress(
        execution_plan=simple_plan,
        status_evidence={
            "outside": "running",
        },
    )

except progress.UniversalOrchestrationProgressTrackingError as exc:

    outside_rejected = (
        exc.code
        == "progress_status_evidence_job_outside_plan"
    )

else:

    outside_rejected = False


check(
    "outside_status_rejected",
    outside_rejected,
)


# ============================================================
# DUPLICATE STATUS AFTER NORMALIZATION
# ============================================================

try:

    progress.track_universal_orchestration_progress(
        execution_plan=simple_plan,
        status_evidence=(
            (
                "a",
                "running",
            ),
            (
                " a ",
                "succeeded",
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
    "duplicate_status_rejected",
    duplicate_rejected,
)


# ============================================================
# INVALID STATUS VALUES
# ============================================================

for index, bad in enumerate(
    (
        True,
        False,
        0,
        1,
        1.0,
        "",
        "completed",
        "unknown",
        [],
        {},
        object(),
    ),
    start=1,
):

    try:

        progress.track_universal_orchestration_progress(
            execution_plan=simple_plan,
            status_evidence={
                "a": bad,
            },
        )

    except progress.UniversalOrchestrationProgressTrackingError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_status_"
        + str(index),
        rejected,
    )


# ============================================================
# DUPLICATE CONDITIONAL SOURCE REJECTED
# ============================================================

shared_decision_two = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=shared_fanout,
        condition_evidence={
            "b": True,
            "c": False,
        },
    )
)


try:

    progress.track_universal_orchestration_progress(
        execution_plan=shared_plan,
        conditional_branching_decisions=(
            shared_decision,
            shared_decision_two,
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
    "duplicate_conditional_source_rejected",
    duplicate_source_rejected,
)


# ============================================================
# CROSS-PLAN DECISION REJECTED
# ============================================================

other_plan = make_plan(
    jobs_tuple=(
        make_job(job_id="source"),
        make_job(
            job_id="b",
            dependencies=("source",),
        ),
        make_job(
            job_id="c",
            dependencies=("source",),
        ),
    ),
    run_id="other-run",
)


other_fanout = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=other_plan,
        source_job_id="source",
    )
)


other_decision = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=other_fanout,
        condition_evidence={
            "b": True,
            "c": False,
        },
    )
)


try:

    progress.track_universal_orchestration_progress(
        execution_plan=shared_plan,
        conditional_branching_decisions=(
            other_decision,
        ),
    )

except progress.UniversalOrchestrationProgressTrackingError as exc:

    cross_plan_rejected = (
        exc.code
        == "progress_conditional_decision_plan_mismatch"
    )

else:

    cross_plan_rejected = False


check(
    "cross_plan_decision_rejected",
    cross_plan_rejected,
)


# ============================================================
# STORED FIELDS
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
    "definite_effective_job_ids",
    "possible_effective_job_ids",
    "unresolved_effective_job_ids",
    "excluded_effective_job_ids",

    "structural_status_buckets",
    "effective_status_buckets",

    "terminal_progress_numerator",
    "terminal_progress_denominator",
    "terminal_progress_ratio",

    "progress_snapshot_id",

    "state",
    "completion",
    "success",
    "failure",

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
# IMMUTABILITY
# ============================================================

for field in fields(
    shared
):

    try:

        setattr(
            shared,
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
    "status_map_mappingproxy",
    isinstance(
        shared.status_evidence_map,
        MappingProxyType,
    ),
)

check(
    "structural_buckets_mappingproxy",
    isinstance(
        shared.structural_status_buckets,
        MappingProxyType,
    ),
)

check(
    "effective_buckets_mappingproxy",
    isinstance(
        shared.effective_status_buckets,
        MappingProxyType,
    ),
)

check(
    "edge_dispositions_mappingproxy",
    isinstance(
        shared.branch_edge_dispositions,
        MappingProxyType,
    ),
)


# ============================================================
# SNAPSHOT ID DETERMINISM
# ============================================================

snapshot_id_one = (
    simple.progress_snapshot_id
)

snapshot_id_two = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=simple_plan,
        status_evidence=(
            (
                "b",
                "running",
            ),
            (
                "a",
                "succeeded",
            ),
        ),
    )
    .progress_snapshot_id
)


check(
    "snapshot_id_length",
    len(
        snapshot_id_one
    )
    == 64,
    snapshot_id_one,
)

check(
    "snapshot_id_upper_hex",
    all(
        character
        in "0123456789ABCDEF"
        for character
        in snapshot_id_one
    ),
)

check(
    "snapshot_id_input_order_independent",
    snapshot_id_one
    == snapshot_id_two,
)


changed_status_id = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=simple_plan,
        status_evidence={
            "a": "succeeded",
            "b": "succeeded",
        },
    )
    .progress_snapshot_id
)


check(
    "snapshot_id_status_sensitive",
    changed_status_id
    != snapshot_id_one,
)


selected_branch_id = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=shared_plan,
        conditional_branching_decisions=(
            shared_decision,
        ),
    )
    .progress_snapshot_id
)


changed_branch_id = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=shared_plan,
        conditional_branching_decisions=(
            shared_decision_two,
        ),
    )
    .progress_snapshot_id
)


check(
    "snapshot_id_branch_sensitive",
    selected_branch_id
    != changed_branch_id,
)


# ============================================================
# EXPLANATION BOUNDARIES
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
    "phase_exact",
    explanation.get("phase")
    == "5.1.11",
)

check(
    "component_exact",
    explanation.get("component")
    == "Universal Orchestration Progress Tracking",
)

check(
    "state_boundary_5_1_3",
    "5.1.3"
    in explanation.get(
        "state_boundary",
        "",
    ),
)

check(
    "conditional_boundary_5_1_10",
    "5.1.10"
    in explanation.get(
        "conditional_boundary",
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
    "recovery_boundary_5_1_13",
    "5.1.13"
    in explanation.get(
        "recovery_boundary",
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

check(
    "evidence_boundary_5_1_17",
    "5.1.17"
    in explanation.get(
        "evidence_record_boundary",
        "",
    ),
)


# ============================================================
# IMPORT BOUNDARY
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

        name = (
            node.func.id
        )

    elif isinstance(
        node.func,
        ast.Attribute,
    ):

        name = (
            node.func.attr
        )

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
# NO DIRECT JOB STATUS/PROGRESS ACCESS
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


check(
    "no_direct_job_progress_access",
    "progress"
    not in attrs,
)


# ============================================================
# PROTECTED AUTHORITIES
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


progress_ast = ast_sha(
    PROGRESS_PATH
)


check(
    "progress_ast_generated",
    len(
        progress_ast
    )
    == 64,
    progress_ast,
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
        "PHASE 5.1.11 — UNIVERSAL ORCHESTRATION "
        "PROGRESS TRACKING INITIAL IMPLEMENTATION"
    ),

    "=" * 118,

    "",

    (
        "PROGRESS TRACKING AST SHA256: "
        + progress_ast
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
            "INITIAL ORCHESTRATION PROGRESS TRACKING RESULT: "
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

        "5.1.1–5.1.10 FROZEN AUTHORITIES MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "STRUCTURAL POPULATION AUTHORITY: 5.1.5",
        "CONDITIONAL DECISION AUTHORITY: 5.1.10",

        "",

        "DEFINITE REACHABILITY:",
        "  UNCONDITIONAL + SELECTED EDGES",

        "POSSIBLE REACHABILITY:",
        "  UNCONDITIONAL + SELECTED + UNRESOLVED EDGES",

        "EXCLUDED EDGE CONTRIBUTES REACHABILITY: NO",

        "",

        "SHARED DESCENDANT SURVIVES AN ALTERNATE ACTIVE PATH: YES",
        "EXCLUSIVE DESCENDANT OF EXCLUDED PATH: EXCLUDED",

        "",

        "CREATED: NOT_STARTED",
        "QUEUED/SCHEDULED: PENDING",
        "LEASED/RUNNING: IN_PROGRESS",
        "SUSPENDED: SUSPENDED",
        "SUCCEEDED: TERMINAL_SUCCESS",
        "FAILED/CANCELLED/DEAD_LETTER/EXPIRED: TERMINAL_UNSUCCESSFUL",

        "",

        "TERMINAL UNSUCCESSFUL COUNTS AS TERMINATED EXECUTION WORK: YES",
        "TERMINAL UNSUCCESSFUL COUNTS AS SUCCESS: NO",
        "MISSING STATUS COLLAPSED TO CREATED: NO",

        "",

        "CANONICAL FLOAT PERCENTAGE STORED: NO",
        "TERMINAL PROGRESS REPRESENTATION: INTEGER NUMERATOR / DENOMINATOR",

        "",

        "ORCHESTRATION STATE CLASSIFICATION: NO",
        "COMPLETION RESOLUTION: NO",
        "SUCCESS/FAILURE RESOLUTION: NO",

        "",

        "READINESS EVALUATION: NO",
        "HANDOFF EVALUATION: NO",
        "CONDITIONS REEVALUATED: NO",

        "",

        "QUEUE/WORKER/LEASE ACTIVITY: NO",
        "HANDLER DISPATCH/JOB EXECUTION: NO",
        "UNIVERSAL JOB MUTATION: NO",
        "ORCHESTRATION STATE TRANSITION: NO",

        "",

        "SUSPENSION/RESUME: NO",
        "RECOVERY: NO",
        "PERSISTENCE: NO",
        "PERMANENT EVIDENCE RECORDING: NO",

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
        "Phase 5.1.11 initial implementation failed."
    )
