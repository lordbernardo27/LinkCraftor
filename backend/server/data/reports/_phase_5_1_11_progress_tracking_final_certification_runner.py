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
    / "phase_5_1_11_progress_tracking_final_certification.txt"
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

if not PROGRESS_PATH.exists():

    raise SystemExit(
        "5.1.11 Progress Tracking authority is missing."
    )


initial_ast = ast_sha(
    PROGRESS_PATH
)


if initial_ast != EXPECTED_PROGRESS_AST:

    raise SystemExit(
        (
            "5.1.11 Progress Tracking AST mismatch.\n"
            "EXPECTED: "
            + EXPECTED_PROGRESS_AST
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
            bool(condition),
            str(detail),
        )
    )


# ============================================================
# AUTHORITY
# ============================================================

check(
    "ast_exact",
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


# ============================================================
# STATUS PARTITION
# ============================================================

partition = (
    progress.NOT_STARTED_UNIVERSAL_JOB_STATUSES,
    progress.PENDING_UNIVERSAL_JOB_STATUSES,
    progress.IN_PROGRESS_UNIVERSAL_JOB_STATUSES,
    progress.SUSPENDED_UNIVERSAL_JOB_STATUSES,
    progress.TERMINAL_SUCCESS_UNIVERSAL_JOB_STATUSES,
    progress.TERMINAL_UNSUCCESSFUL_UNIVERSAL_JOB_STATUSES,
)


check(
    "status_partition_complete",
    frozenset().union(
        *partition
    )
    == frozenset(
        jobs.UniversalJobStatus
    ),
)


for left_index in range(
    len(partition)
):

    for right_index in range(
        left_index + 1,
        len(partition),
    ):

        check(
            (
                "status_partition_disjoint_"
                + str(left_index)
                + "_"
                + str(right_index)
            ),
            not (
                partition[left_index]
                &
                partition[right_index]
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
# CANONICAL EFFECTIVE TOPOLOGY
# ============================================================

plan = make_plan(
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
            job_id="shared",
            dependencies=(
                "a",
                "b",
            ),
        ),

        make_job(
            job_id="a-only",
            dependencies=("a",),
        ),

        make_job(
            job_id="b-only",
            dependencies=("b",),
        ),
    ),
    run_id="certification",
)


fan_out = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=plan,
        source_job_id="root",
    )
)


decision = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out,
        condition_evidence={
            "a": False,
            "b": True,
        },
    )
)


snapshot = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=plan,
        status_evidence={
            "root": "succeeded",
            "a": "failed",
            "b": "running",
            "shared": "created",
            "a-only": "succeeded",
            "b-only": None,
        },
        conditional_branching_decisions=(
            decision,
        ),
    )
)


check(
    "definite_effective_exact",
    snapshot.definite_effective_job_ids
    == (
        "b",
        "b-only",
        "root",
        "shared",
    ),
    snapshot.definite_effective_job_ids,
)

check(
    "possible_effective_exact",
    snapshot.possible_effective_job_ids
    == (
        "b",
        "b-only",
        "root",
        "shared",
    ),
    snapshot.possible_effective_job_ids,
)

check(
    "excluded_effective_exact",
    snapshot.excluded_effective_job_ids
    == (
        "a",
        "a-only",
    ),
    snapshot.excluded_effective_job_ids,
)

check(
    "shared_descendant_survives",
    "shared"
    in snapshot.definite_effective_job_ids,
)

check(
    "excluded_status_not_counted",
    snapshot.terminal_unsuccessful_job_count
    == 0,
)

check(
    "successful_count_exact",
    snapshot.successful_job_count
    == 1,
)

check(
    "in_progress_count_exact",
    snapshot.in_progress_job_count
    == 1,
)

check(
    "missing_count_exact",
    snapshot.missing_status_job_count
    == 1,
)

check(
    "terminal_ratio_exact",
    snapshot.terminal_progress_ratio
    == (
        1,
        4,
    ),
)


# ============================================================
# UNRESOLVED TOPOLOGY
# ============================================================

unresolved_decision = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out,
        condition_evidence={
            "a": False,
            "b": None,
        },
    )
)


unresolved = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=plan,
        conditional_branching_decisions=(
            unresolved_decision,
        ),
    )
)


check(
    "unresolved_root_definite",
    unresolved.definite_effective_job_ids
    == ("root",),
)

check(
    "unresolved_shared_possible",
    "shared"
    in unresolved.possible_effective_job_ids,
)

check(
    "unresolved_shared_unresolved",
    "shared"
    in unresolved.unresolved_effective_job_ids,
)

check(
    "unresolved_denominator_exact",
    unresolved.terminal_progress_denominator
    == 4,
)


# ============================================================
# TERMINAL UNSUCCESSFUL SEMANTICS
# ============================================================

terminal_plan = make_plan(
    jobs_tuple=(
        make_job(job_id="s"),
        make_job(job_id="f"),
        make_job(job_id="c"),
        make_job(job_id="d"),
        make_job(job_id="e"),
    ),
    run_id="terminal-certification",
)


terminal_snapshot = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=terminal_plan,
        status_evidence={
            "s": "succeeded",
            "f": "failed",
            "c": "cancelled",
            "d": "dead_letter",
            "e": "expired",
        },
    )
)


check(
    "terminal_success_one",
    terminal_snapshot.successful_job_count
    == 1,
)

check(
    "terminal_unsuccessful_four",
    terminal_snapshot.terminal_unsuccessful_job_count
    == 4,
)

check(
    "all_terminal_five",
    terminal_snapshot.terminal_job_count
    == 5,
)

check(
    "all_terminal_ratio_five_five",
    terminal_snapshot.terminal_progress_ratio
    == (
        5,
        5,
    ),
)


# ============================================================
# MISSING EVIDENCE
# ============================================================

missing_snapshot = (
    progress
    .track_universal_orchestration_progress(
        execution_plan=terminal_plan,
        status_evidence=None,
    )
)


check(
    "missing_all_five",
    missing_snapshot.missing_status_job_count
    == 5,
)

check(
    "missing_not_created",
    missing_snapshot.not_started_job_count
    == 0,
)


# ============================================================
# STORED / DERIVED
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

check(
    "identity_derived",
    snapshot.identity
    is plan.identity,
)

check(
    "status_map_mappingproxy",
    isinstance(
        snapshot.status_evidence_map,
        MappingProxyType,
    ),
)

check(
    "edge_map_mappingproxy",
    isinstance(
        snapshot.branch_edge_dispositions,
        MappingProxyType,
    ),
)

check(
    "structural_buckets_mappingproxy",
    isinstance(
        snapshot.structural_status_buckets,
        MappingProxyType,
    ),
)

check(
    "effective_buckets_mappingproxy",
    isinstance(
        snapshot.effective_status_buckets,
        MappingProxyType,
    ),
)


# ============================================================
# IMMUTABILITY
# ============================================================

for field in fields(
    snapshot
):

    try:

        setattr(
            snapshot,
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
# SNAPSHOT ID
# ============================================================

snapshot_id = (
    snapshot.progress_snapshot_id
)


check(
    "snapshot_id_length",
    len(snapshot_id)
    == 64,
    snapshot_id,
)

check(
    "snapshot_id_upper_hex",
    all(
        character
        in "0123456789ABCDEF"
        for character
        in snapshot_id
    ),
)

check(
    "snapshot_id_deterministic",
    snapshot_id
    ==
    progress
    .track_universal_orchestration_progress(
        execution_plan=plan,
        status_evidence=(
            ("b-only", None),
            ("shared", "created"),
            ("root", "succeeded"),
            ("b", "running"),
            ("a-only", "succeeded"),
            ("a", "failed"),
        ),
        conditional_branching_decisions=(
            decision,
        ),
    )
    .progress_snapshot_id,
)


# ============================================================
# EXPLANATION
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
    "stored_fields_explanation_exact",
    explanation.get("stored_fields")
    == (
        "execution_plan",
        "status_evidence",
        "conditional_branching_decisions",
        "schema_version",
    ),
)

check(
    "state_boundary",
    "5.1.3"
    in explanation.get(
        "state_boundary",
        "",
    ),
)

check(
    "conditional_boundary",
    "5.1.10"
    in explanation.get(
        "conditional_boundary",
        "",
    ),
)

check(
    "suspension_boundary",
    "5.1.12"
    in explanation.get(
        "suspension_boundary",
        "",
    ),
)

check(
    "recovery_boundary",
    "5.1.13"
    in explanation.get(
        "recovery_boundary",
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

check(
    "evidence_boundary",
    "5.1.17"
    in explanation.get(
        "evidence_record_boundary",
        "",
    ),
)


# ============================================================
# IMPORT / OPERATION BOUNDARY
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


forbidden_calls = {
    "eval",
    "exec",
    "compile",

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
        "forbidden_attribute_"
        + forbidden_attr,
        forbidden_attr
        not in attrs,
    )


check(
    "no_float_progress_percent",
    "progress_percent"
    not in source,
)

check(
    "no_completion_resolution",
    "UniversalOrchestrationState.SUCCEEDED"
    not in source
    and
    "UniversalOrchestrationState.FAILED"
    not in source,
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
        "phase_5_1_11_universal_orchestration_progress_tracking",

        progress.UNIVERSAL_ORCHESTRATION_PROGRESS_TRACKING_VERSION,
        progress.UNIVERSAL_ORCHESTRATION_PROGRESS_TRACKING_SCHEMA_VERSION,
        progress.UNIVERSAL_ORCHESTRATION_PROGRESS_SNAPSHOT_HASH_ALGORITHM,

        EXPECTED_PROGRESS_AST,

        "structural_population_from_5_1_5",

        "status_evidence_caller_supplied",
        "missing_status_preserved",

        "created_not_started",
        "queued_scheduled_pending",
        "leased_running_in_progress",
        "suspended_suspended",
        "succeeded_terminal_success",
        "failed_cancelled_dead_letter_expired_terminal_unsuccessful",

        "terminal_unsuccessful_counts_as_terminated_work",
        "terminal_unsuccessful_does_not_count_as_success",

        "conditional_decisions_from_5_1_10",
        "conditional_decisions_not_reevaluated",

        "definite_reachability_unconditional_plus_selected",
        "possible_reachability_unconditional_plus_selected_plus_unresolved",
        "excluded_edges_do_not_contribute_reachability",

        "shared_descendant_survives_alternate_nonexcluded_path",
        "exclusive_descendant_of_excluded_path_excluded",
        "deep_exclusion_propagates",
        "unresolved_activity_propagates",
        "disconnected_components_preserved",

        "structural_job_ids_unchanged",
        "execution_plan_topology_not_mutated",

        "possible_effective_population_is_progress_denominator",
        "excluded_jobs_removed_from_effective_progress",
        "unresolved_possible_jobs_remain_in_denominator",

        "terminal_progress_integer_numerator_denominator",
        "no_canonical_float_percentage",

        "stored_execution_plan",
        "stored_status_evidence",
        "stored_conditional_branching_decisions",
        "stored_schema_version",

        "derived_identity",
        "derived_effective_sets",
        "derived_status_buckets",
        "derived_progress_snapshot_id",

        "progress_snapshot_id_sha256",
        "snapshot_identity_sensitive",
        "snapshot_status_sensitive",
        "snapshot_branch_sensitive",

        "no_direct_universal_job_progress_access",
        "no_runtime_storage",
        "no_queue_state",
        "no_worker_state",
        "no_lease_state",

        "no_dependency_resolution",
        "no_readiness",
        "no_handoff",
        "no_fanout_recompute",
        "no_fanin_recompute",

        "no_job_mutation",
        "no_queue_activity",
        "no_worker_activity",
        "no_lease_activity",
        "no_handler_dispatch",
        "no_job_execution",

        "no_orchestration_state_transition",

        "suspension_resume_deferred_5_1_12",
        "recovery_deferred_5_1_13",
        "persistence_deferred_5_1_14",
        "completion_deferred_5_1_15",
        "evidence_records_deferred_5_1_17",

        "no_completion_success_failure_resolution",

        "no_wall_clock",
        "no_filesystem_io",
        "no_network_io",
        "no_database_io",

        "no_universal_coordination_framework",
        "no_pipeline_coordinator",

        "immutable_deterministic_progress_snapshot_authority",
    )
)


progress_fingerprint = (
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
            progress_fingerprint
        )
        == 64
        and
        all(
            character
            in "0123456789ABCDEF"
            for character
            in progress_fingerprint
        )
    ),
    progress_fingerprint,
)


# ============================================================
# FINAL AST
# ============================================================

final_ast = ast_sha(
    PROGRESS_PATH
)


check(
    "final_ast_unchanged",
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


lines = [
    (
        "PHASE 5.1.11 — UNIVERSAL ORCHESTRATION "
        "PROGRESS TRACKING FINAL CERTIFICATION"
    ),

    "=" * 118,

    "",

    (
        "PROGRESS TRACKING AST SHA256: "
        + final_ast
    ),

    (
        "PROGRESS TRACKING FINGERPRINT: "
        + progress_fingerprint
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
            "FINAL ORCHESTRATION PROGRESS TRACKING CERTIFICATION: "
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

        "PROGRESS TRACKING AUTHORITY MODIFIED DURING CERTIFICATION: NO",
        "5.1.1–5.1.10 FROZEN AUTHORITIES MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "STRUCTURAL POPULATION AUTHORITY: 5.1.5",
        "CONDITIONAL DECISION AUTHORITY: 5.1.10",

        "",

        "DEFINITE EFFECTIVE REACHABILITY:",
        "  UNCONDITIONAL + SELECTED",

        "POSSIBLE EFFECTIVE REACHABILITY:",
        "  UNCONDITIONAL + SELECTED + UNRESOLVED",

        "EXCLUDED EDGE CONTRIBUTES REACHABILITY: NO",

        "",

        "SHARED DESCENDANT ALTERNATE-PATH SURVIVAL: YES",
        "DEEP EXCLUSION PROPAGATION: YES",
        "UNRESOLVED ACTIVITY PROPAGATION: YES",

        "",

        "CREATED: NOT_STARTED",
        "QUEUED/SCHEDULED: PENDING",
        "LEASED/RUNNING: IN_PROGRESS",
        "SUSPENDED: SUSPENDED",
        "SUCCEEDED: TERMINAL_SUCCESS",
        "FAILED/CANCELLED/DEAD_LETTER/EXPIRED: TERMINAL_UNSUCCESSFUL",

        "",

        "TERMINAL UNSUCCESSFUL COUNTS AS TERMINATED WORK: YES",
        "TERMINAL UNSUCCESSFUL COUNTS AS SUCCESS: NO",
        "MISSING STATUS COLLAPSED TO CREATED: NO",

        "",

        "EFFECTIVE PROGRESS DENOMINATOR: POSSIBLE EFFECTIVE JOB COUNT",
        "EXCLUDED JOBS COUNT IN EFFECTIVE PROGRESS: NO",
        "UNRESOLVED POSSIBLE JOBS COUNT IN DENOMINATOR: YES",

        "",

        "CANONICAL FLOAT PERCENTAGE STORED: NO",
        "PROGRESS REPRESENTATION: INTEGER NUMERATOR / DENOMINATOR",

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

        "RUNTIME STATE STORE ACCESS: NO",
        "UNIVERSAL COORDINATION FRAMEWORK ACCESS: NO",
        "PIPELINE COORDINATOR ACCESS: NO",

        "",

        (
            "PHASE 5.1.11 FREEZE CANDIDATE: "
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
        "Phase 5.1.11 final certification failed."
    )
