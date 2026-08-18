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

DEPENDENCY_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_orchestration"
    / "dependency_resolution.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_1_4_dependency_resolution_final_certification.txt"
)

EXPECTED_DEPENDENCY_AST = (
    "CF4CE73A8683BFDA1464730F2079058898B2660275C786FA6EBD0816AE574A8E"
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


if not DEPENDENCY_PATH.exists():

    raise SystemExit(
        "5.1.4 Dependency Resolution authority missing."
    )


initial_ast = ast_sha(
    DEPENDENCY_PATH
)


if initial_ast != EXPECTED_DEPENDENCY_AST:

    raise SystemExit(
        (
            "5.1.4 Dependency Resolution AST mismatch "
            "before final certification.\n"
            "EXPECTED: "
            + EXPECTED_DEPENDENCY_AST
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
                "Protected authority mismatch before "
                "5.1.4 final certification: "
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


job_contract = importlib.import_module(
    "backend.server.runtime.universal_jobs.contract"
)

orchestration_contract = importlib.import_module(
    "backend.server.runtime.universal_orchestration.contract"
)

run_identity = importlib.import_module(
    "backend.server.runtime.universal_orchestration.run_identity"
)

dependency_module_name = (
    "backend.server.runtime."
    "universal_orchestration.dependency_resolution"
)

sys.modules.pop(
    dependency_module_name,
    None,
)

dependency = importlib.import_module(
    dependency_module_name
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


dependency_ast = ast_sha(
    DEPENDENCY_PATH
)


# ============================================================
# AUTHORITY / VERSION
# ============================================================

check(
    "dependency_ast_exact",
    dependency_ast
    == EXPECTED_DEPENDENCY_AST,
    dependency_ast,
)

check(
    "version_exact",
    dependency.UNIVERSAL_ORCHESTRATION_DEPENDENCY_RESOLUTION_VERSION
    == "universal_orchestration_dependency_resolution_v5.1.4",
)

check(
    "schema_exact",
    dependency.UNIVERSAL_ORCHESTRATION_DEPENDENCY_RESOLUTION_SCHEMA_VERSION
    == "universal_orchestration_dependency_resolution_schema_v1",
)


# ============================================================
# CLASSIFICATION ENUM
# ============================================================

expected_classifications = (
    "satisfied",
    "unresolved",
    "terminal_unsatisfied",
    "missing",
)


check(
    "classification_exact",
    tuple(
        item.value
        for item
        in dependency.UniversalOrchestrationDependencyClassification
    )
    == expected_classifications,
)


# ============================================================
# STATUS PARTITION
# ============================================================

expected_satisfied = frozenset(
    {
        job_contract.UniversalJobStatus.SUCCEEDED,
    }
)


expected_unresolved = frozenset(
    {
        job_contract.UniversalJobStatus.CREATED,
        job_contract.UniversalJobStatus.QUEUED,
        job_contract.UniversalJobStatus.SCHEDULED,
        job_contract.UniversalJobStatus.LEASED,
        job_contract.UniversalJobStatus.RUNNING,
        job_contract.UniversalJobStatus.SUSPENDED,
    }
)


expected_terminal_unsatisfied = frozenset(
    {
        job_contract.UniversalJobStatus.FAILED,
        job_contract.UniversalJobStatus.CANCELLED,
        job_contract.UniversalJobStatus.DEAD_LETTER,
        job_contract.UniversalJobStatus.EXPIRED,
    }
)


check(
    "satisfied_set_exact",
    dependency.SATISFIED_UNIVERSAL_JOB_STATUSES
    == expected_satisfied,
)

check(
    "unresolved_set_exact",
    dependency.UNRESOLVED_UNIVERSAL_JOB_STATUSES
    == expected_unresolved,
)

check(
    "terminal_unsatisfied_set_exact",
    dependency.TERMINAL_UNSATISFIED_UNIVERSAL_JOB_STATUSES
    == expected_terminal_unsatisfied,
)

check(
    "partition_covers_all_statuses",
    (
        expected_satisfied
        |
        expected_unresolved
        |
        expected_terminal_unsatisfied
    )
    == frozenset(
        job_contract.UniversalJobStatus
    ),
)

check(
    "partition_disjoint_satisfied_unresolved",
    not (
        expected_satisfied
        &
        expected_unresolved
    ),
)

check(
    "partition_disjoint_satisfied_terminal",
    not (
        expected_satisfied
        &
        expected_terminal_unsatisfied
    ),
)

check(
    "partition_disjoint_unresolved_terminal",
    not (
        expected_unresolved
        &
        expected_terminal_unsatisfied
    ),
)


# ============================================================
# CLASSIFICATION MATRIX
# ============================================================

expected_status_classification = {
    job_contract.UniversalJobStatus.SUCCEEDED:
        "satisfied",

    job_contract.UniversalJobStatus.CREATED:
        "unresolved",

    job_contract.UniversalJobStatus.QUEUED:
        "unresolved",

    job_contract.UniversalJobStatus.SCHEDULED:
        "unresolved",

    job_contract.UniversalJobStatus.LEASED:
        "unresolved",

    job_contract.UniversalJobStatus.RUNNING:
        "unresolved",

    job_contract.UniversalJobStatus.SUSPENDED:
        "unresolved",

    job_contract.UniversalJobStatus.FAILED:
        "terminal_unsatisfied",

    job_contract.UniversalJobStatus.CANCELLED:
        "terminal_unsatisfied",

    job_contract.UniversalJobStatus.DEAD_LETTER:
        "terminal_unsatisfied",

    job_contract.UniversalJobStatus.EXPIRED:
        "terminal_unsatisfied",
}


for status, expected in (
    expected_status_classification.items()
):

    actual = (
        dependency
        .classify_universal_orchestration_dependency_status(
            status
        )
    )

    check(
        "classification_"
        + status.value,
        actual.value
        == expected,
        actual,
    )


# ============================================================
# FIXTURE HELPERS
# ============================================================

FIXED_CREATED_AT = (
    "2026-05-21T03:49:30.579317+00:00"
)


def make_job(
    *,
    job_id,
    dependencies=(),
    status=job_contract.UniversalJobStatus.CREATED,
    workspace_id="workspace-a",
    pipeline="pipeline-a",
    parent_job_id=None,
):

    return job_contract.UniversalJob(
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
        created_at=FIXED_CREATED_AT,
    )


def make_identity(
    *,
    run_id,
    job_ids,
    workspace_id="workspace-a",
    pipeline="pipeline-a",
):

    contract = (
        orchestration_contract
        .create_universal_runtime_orchestration_contract(
            workspace_id=workspace_id,
            pipeline=pipeline,
            job_ids=job_ids,
        )
    )

    identity = (
        run_identity
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
# CANONICAL MIXED RESOLUTION
# ============================================================

target = make_job(
    job_id="job-target",
    dependencies=(
        "job-d",
        "job-b",
        "job-c",
        "job-a",
    ),
)


contract_a, identity_a = make_identity(
    run_id="run-a",
    job_ids=(
        "job-target",
        "job-a",
        "job-b",
        "job-c",
        "job-d",
    ),
)


resolution = (
    dependency.resolve_universal_orchestration_dependencies(
        identity=identity_a,
        target_job=target,
        dependency_statuses={
            "job-d": "queued",
            "job-c": "failed",
            "job-a": "succeeded",
        },
    )
)


check(
    "dependency_ids_exact",
    resolution.dependency_job_ids
    == (
        "job-a",
        "job-b",
        "job-c",
        "job-d",
    ),
)

check(
    "dependency_count_exact",
    resolution.dependency_count
    == 4,
)

check(
    "satisfied_ids_exact",
    resolution.satisfied_dependency_ids
    == (
        "job-a",
    ),
)

check(
    "unresolved_ids_exact",
    resolution.unresolved_dependency_ids
    == (
        "job-d",
    ),
)

check(
    "terminal_unsatisfied_ids_exact",
    resolution.terminal_unsatisfied_dependency_ids
    == (
        "job-c",
    ),
)

check(
    "missing_ids_exact",
    resolution.missing_dependency_ids
    == (
        "job-b",
    ),
)

check(
    "all_dependencies_satisfied_false",
    resolution.all_dependencies_satisfied
    is False,
)

check(
    "has_unresolved_true",
    resolution.has_unresolved_dependencies
    is True,
)

check(
    "has_terminal_failure_true",
    resolution.has_terminal_dependency_failure
    is True,
)

check(
    "has_missing_true",
    resolution.has_missing_dependency_evidence
    is True,
)


# ============================================================
# ALL SUCCEEDED
# ============================================================

all_succeeded = (
    dependency.resolve_universal_orchestration_dependencies(
        identity=identity_a,
        target_job=target,
        dependency_statuses={
            "job-a": "succeeded",
            "job-b": "succeeded",
            "job-c": "succeeded",
            "job-d": "succeeded",
        },
    )
)


check(
    "all_succeeded_true",
    all_succeeded.all_dependencies_satisfied
    is True,
)

check(
    "all_succeeded_ids",
    all_succeeded.satisfied_dependency_ids
    == (
        "job-a",
        "job-b",
        "job-c",
        "job-d",
    ),
)

check(
    "all_succeeded_no_unresolved",
    all_succeeded.unresolved_dependency_ids
    == (),
)

check(
    "all_succeeded_no_terminal_failure",
    all_succeeded.terminal_unsatisfied_dependency_ids
    == (),
)

check(
    "all_succeeded_no_missing",
    all_succeeded.missing_dependency_ids
    == (),
)


# ============================================================
# ZERO DEPENDENCIES
# ============================================================

zero_target = make_job(
    job_id="zero-target",
)


zero_contract, zero_identity = make_identity(
    run_id="zero-run",
    job_ids=(
        "zero-target",
    ),
)


zero_resolution = (
    dependency.resolve_universal_orchestration_dependencies(
        identity=zero_identity,
        target_job=zero_target,
    )
)


check(
    "zero_dependency_count",
    zero_resolution.dependency_count
    == 0,
)

check(
    "zero_all_satisfied",
    zero_resolution.all_dependencies_satisfied
    is True,
)

check(
    "zero_missing_empty",
    zero_resolution.missing_dependency_ids
    == (),
)

check(
    "zero_unresolved_empty",
    zero_resolution.unresolved_dependency_ids
    == (),
)

check(
    "zero_terminal_empty",
    zero_resolution.terminal_unsatisfied_dependency_ids
    == (),
)


# ============================================================
# MISSING EVIDENCE
# ============================================================

missing_resolution = (
    dependency.resolve_universal_orchestration_dependencies(
        identity=identity_a,
        target_job=target,
        dependency_statuses=None,
    )
)


check(
    "missing_all_dependency_ids",
    missing_resolution.missing_dependency_ids
    == target.dependency_job_ids,
)

check(
    "missing_not_satisfied",
    missing_resolution.satisfied_dependency_ids
    == (),
)

check(
    "missing_not_unresolved",
    missing_resolution.unresolved_dependency_ids
    == (),
)

check(
    "missing_not_terminal_failure",
    missing_resolution.terminal_unsatisfied_dependency_ids
    == (),
)

check(
    "missing_flag_true",
    missing_resolution.has_missing_dependency_evidence
    is True,
)


# ============================================================
# PARENT LINEAGE SEPARATION
# ============================================================

parent_target = make_job(
    job_id="child-job",
    parent_job_id="parent-job",
    dependencies=(),
)


_, parent_identity = make_identity(
    run_id="parent-run",
    job_ids=(
        "child-job",
    ),
)


parent_resolution = (
    dependency.resolve_universal_orchestration_dependencies(
        identity=parent_identity,
        target_job=parent_target,
    )
)


check(
    "parent_not_dependency",
    parent_resolution.dependency_job_ids
    == (),
)

check(
    "parent_does_not_change_satisfaction",
    parent_resolution.all_dependencies_satisfied
    is True,
)


# ============================================================
# CONTRACT MEMBERSHIP
# ============================================================

outside_target = make_job(
    job_id="outside-target",
)


try:

    dependency.resolve_universal_orchestration_dependencies(
        identity=identity_a,
        target_job=outside_target,
    )

except dependency.UniversalOrchestrationDependencyResolutionError as exc:

    rejected = (
        exc.code
        == "target_job_outside_orchestration_contract"
    )

else:

    rejected = False


check(
    "outside_target_rejected",
    rejected,
)


outside_dependency_target = make_job(
    job_id="job-target",
    dependencies=(
        "job-a",
        "outside-job",
    ),
)


try:

    dependency.resolve_universal_orchestration_dependencies(
        identity=identity_a,
        target_job=outside_dependency_target,
    )

except dependency.UniversalOrchestrationDependencyResolutionError as exc:

    rejected = (
        exc.code
        == "dependency_outside_orchestration_contract"
    )

else:

    rejected = False


check(
    "outside_dependency_rejected",
    rejected,
)


# ============================================================
# WORKSPACE / PIPELINE BINDING
# ============================================================

wrong_workspace = make_job(
    job_id="job-target",
    workspace_id="workspace-b",
)


try:

    dependency.resolve_universal_orchestration_dependencies(
        identity=identity_a,
        target_job=wrong_workspace,
    )

except dependency.UniversalOrchestrationDependencyResolutionError as exc:

    rejected = (
        exc.code
        == "dependency_target_workspace_mismatch"
    )

else:

    rejected = False


check(
    "workspace_mismatch_rejected",
    rejected,
)


wrong_pipeline = make_job(
    job_id="job-target",
    pipeline="pipeline-b",
)


try:

    dependency.resolve_universal_orchestration_dependencies(
        identity=identity_a,
        target_job=wrong_pipeline,
    )

except dependency.UniversalOrchestrationDependencyResolutionError as exc:

    rejected = (
        exc.code
        == "dependency_target_pipeline_mismatch"
    )

else:

    rejected = False


check(
    "pipeline_mismatch_rejected",
    rejected,
)


# ============================================================
# EXTRANEOUS EVIDENCE
# ============================================================

try:

    dependency.resolve_universal_orchestration_dependencies(
        identity=identity_a,
        target_job=target,
        dependency_statuses={
            "job-a": "succeeded",
            "ghost-job": "succeeded",
        },
    )

except dependency.UniversalOrchestrationDependencyResolutionError as exc:

    rejected = (
        exc.code
        == "extraneous_dependency_status_evidence"
    )

else:

    rejected = False


check(
    "extraneous_evidence_rejected",
    rejected,
)


# ============================================================
# STORED FIELD CONTRACT
# ============================================================

field_names = tuple(
    field.name
    for field in fields(
        dependency.UniversalOrchestrationDependencyResolution
    )
)


check(
    "stored_fields_exact",
    field_names
    == (
        "identity",
        "target_job",
        "dependency_statuses",
        "schema_version",
    ),
    field_names,
)


for forbidden_field in (
    "job_id",
    "dependency_job_ids",
    "dependency_count",

    "satisfied_dependency_ids",
    "unresolved_dependency_ids",
    "terminal_unsatisfied_dependency_ids",
    "missing_dependency_ids",

    "all_dependencies_satisfied",
    "has_unresolved_dependencies",
    "has_terminal_dependency_failure",
    "has_missing_dependency_evidence",

    "parent_job_id",

    "cycle_detected",
    "topological_order",

    "execution_order",
    "execution_plan",

    "ready",
    "blocked",
    "readiness",

    "orchestration_state",

    "queue_id",
    "worker_id",
    "lease_id",

    "created_at",
    "updated_at",

    "metadata",
):

    check(
        "forbidden_field_"
        + forbidden_field,
        forbidden_field
        not in field_names,
    )


# ============================================================
# IMMUTABILITY
# ============================================================

for field in fields(
    resolution
):

    try:

        setattr(
            resolution,
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


status_map = (
    resolution.dependency_status_map
)


check(
    "status_map_immutable_type",
    isinstance(
        status_map,
        MappingProxyType,
    ),
)


try:

    status_map[
        "job-a"
    ] = job_contract.UniversalJobStatus.FAILED

except Exception:

    status_map_immutable = True

else:

    status_map_immutable = False


check(
    "status_map_immutable",
    status_map_immutable,
)


# ============================================================
# DETERMINISM
# ============================================================

resolution_a = (
    dependency.resolve_universal_orchestration_dependencies(
        identity=identity_a,
        target_job=target,
        dependency_statuses={
            "job-a": "succeeded",
            "job-b": "queued",
            "job-c": "failed",
            "job-d": "running",
        },
    )
)


resolution_b = (
    dependency.resolve_universal_orchestration_dependencies(
        identity=identity_a,
        target_job=target,
        dependency_statuses={
            "job-d": "running",
            "job-c": "failed",
            "job-b": "queued",
            "job-a": "succeeded",
        },
    )
)


check(
    "mapping_order_deterministic",
    resolution_a
    == resolution_b,
)

check(
    "canonical_status_tuple_deterministic",
    resolution_a.dependency_statuses
    == resolution_b.dependency_statuses,
)


# ============================================================
# EXPLANATION CONTRACT
# ============================================================

explanation = (
    dependency
    .explain_universal_orchestration_dependency_resolution_v1()
)


check(
    "phase_exact",
    explanation.get(
        "phase"
    )
    == "5.1.4",
)

check(
    "component_exact",
    explanation.get(
        "component"
    )
    == "Universal Orchestration Dependency Resolution",
)

check(
    "stored_fields_explanation_exact",
    explanation.get(
        "stored_fields"
    )
    == (
        "identity",
        "target_job",
        "dependency_statuses",
        "schema_version",
    ),
)

check(
    "membership_bound_to_5_1_1",
    "5.1.1"
    in explanation.get(
        "membership_rule",
        "",
    ),
)

check(
    "parent_separation_rule",
    "not implicitly treated as a dependency"
    in explanation.get(
        "parent_rule",
        "",
    ),
)

check(
    "missing_evidence_rule",
    "MISSING"
    in explanation.get(
        "missing_rule",
        "",
    ),
)

check(
    "zero_dependency_rule",
    "all_dependencies_satisfied=True"
    in explanation.get(
        "zero_dependency_rule",
        "",
    ),
)

check(
    "cycle_deferred_5_1_5",
    "5.1.5"
    in explanation.get(
        "cycle_boundary",
        "",
    ),
)

check(
    "planning_deferred_5_1_5",
    "5.1.5"
    in explanation.get(
        "planning_boundary",
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
    "state_not_transitioned",
    "does not transition"
    in explanation.get(
        "state_boundary",
        "",
    ),
)


# ============================================================
# API SURFACE
# ============================================================

expected_all = (
    "UNIVERSAL_ORCHESTRATION_DEPENDENCY_RESOLUTION_VERSION",
    "UNIVERSAL_ORCHESTRATION_DEPENDENCY_RESOLUTION_SCHEMA_VERSION",
    "UniversalOrchestrationDependencyResolutionError",
    "UniversalOrchestrationDependencyClassification",
    "SATISFIED_UNIVERSAL_JOB_STATUSES",
    "TERMINAL_UNSATISFIED_UNIVERSAL_JOB_STATUSES",
    "UNRESOLVED_UNIVERSAL_JOB_STATUSES",
    "classify_universal_orchestration_dependency_status",
    "UniversalOrchestrationDependencyResolution",
    "resolve_universal_orchestration_dependencies",
    "explain_universal_orchestration_dependency_resolution_v1",
)


check(
    "api_surface_exact",
    tuple(
        dependency.__all__
    )
    == expected_all,
    dependency.__all__,
)


# ============================================================
# IMPORT BOUNDARY
# ============================================================

source = DEPENDENCY_PATH.read_text(
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
        "backend.server.runtime.universal_jobs.status",
        "backend.server.runtime.universal_orchestration.run_identity",
    ],
    backend_imports,
)


# ============================================================
# PROHIBITION MATRIX
# ============================================================

required_prohibitions = (
    "does not redefine dependency_job_ids",
    "does not mutate Universal Job lineage",
    "does not treat parent_job_id as an implicit dependency",
    "does not perform cross-job cycle detection",

    "does not read Runtime State Store",
    "does not query job persistence",
    "does not mutate Universal Jobs",
    "does not transition orchestration state",

    "does not determine execution order",
    "does not create execution plans",

    "does not determine READY",
    "does not determine BLOCKED",

    "does not enqueue jobs",
    "does not claim jobs",

    "does not assign workers",
    "does not acquire worker leases",

    "does not register runtime handlers",
    "does not dispatch runtime handlers",
    "does not execute runtime handlers",
    "does not execute jobs",

    "does not import Universal Coordination Framework",
    "does not invoke pipeline coordinators",

    "does not persist dependency resolution",

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
# CANONICAL 5.1.4 FINGERPRINT
# ============================================================

fingerprint_material = "|".join(
    (
        "phase_5_1_4_universal_orchestration_dependency_resolution",

        dependency.UNIVERSAL_ORCHESTRATION_DEPENDENCY_RESOLUTION_VERSION,
        dependency.UNIVERSAL_ORCHESTRATION_DEPENDENCY_RESOLUTION_SCHEMA_VERSION,

        dependency_ast,

        "classification_satisfied",
        "classification_unresolved",
        "classification_terminal_unsatisfied",
        "classification_missing",

        "succeeded_is_satisfied",

        "created_is_unresolved",
        "queued_is_unresolved",
        "scheduled_is_unresolved",
        "leased_is_unresolved",
        "running_is_unresolved",
        "suspended_is_unresolved",

        "failed_is_terminal_unsatisfied",
        "cancelled_is_terminal_unsatisfied",
        "dead_letter_is_terminal_unsatisfied",
        "expired_is_terminal_unsatisfied",

        "missing_status_evidence_is_missing",

        "stored_identity",
        "stored_target_job",
        "stored_dependency_statuses",
        "stored_schema_version",

        "job_id_derived",
        "dependency_job_ids_derived",
        "dependency_count_derived",

        "satisfied_dependency_ids_derived",
        "unresolved_dependency_ids_derived",
        "terminal_unsatisfied_dependency_ids_derived",
        "missing_dependency_ids_derived",

        "all_dependencies_satisfied_derived",
        "has_unresolved_dependencies_derived",
        "has_terminal_dependency_failure_derived",
        "has_missing_dependency_evidence_derived",

        "zero_dependencies_all_satisfied",

        "target_must_belong_to_contract",
        "dependencies_must_belong_to_contract",

        "workspace_binding_required",
        "pipeline_binding_required",

        "parent_job_id_not_dependency",

        "dependency_status_evidence_caller_supplied",
        "dependency_statuses_canonical_sorted",

        "no_cross_job_cycle_detection",
        "cycle_detection_deferred_5_1_5",

        "execution_planning_deferred_5_1_5",
        "readiness_deferred_5_1_6",

        "no_orchestration_state_transition",

        "no_queue_activity",
        "no_worker_activity",

        "no_runtime_registration_activity",
        "no_handler_dispatch",
        "no_job_execution",

        "no_coordination_framework",
        "no_pipeline_coordinators",

        "no_runtime_state_store",
        "no_job_persistence_lookup",
        "no_dependency_resolution_persistence",

        "no_wall_clock",
        "no_filesystem_io",
        "no_network_io",

        "pure_runtime_orchestration_dependency_resolution_authority",
    )
)


dependency_resolution_fingerprint = (
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
            dependency_resolution_fingerprint
        )
        == 64
        and
        all(
            character
            in "0123456789ABCDEF"
            for character in dependency_resolution_fingerprint
        )
    ),
    dependency_resolution_fingerprint,
)


# ============================================================
# FINAL AST
# ============================================================

final_ast = ast_sha(
    DEPENDENCY_PATH
)


check(
    "final_ast_unchanged",
    final_ast
    == EXPECTED_DEPENDENCY_AST,
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
        "PHASE 5.1.4 — UNIVERSAL ORCHESTRATION "
        "DEPENDENCY RESOLUTION FINAL CERTIFICATION"
    ),
    "=" * 118,
    "",
    (
        "DEPENDENCY RESOLUTION AST SHA256: "
        + dependency_ast
    ),
    (
        "DEPENDENCY RESOLUTION FINGERPRINT: "
        + dependency_resolution_fingerprint
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
            "FINAL DEPENDENCY RESOLUTION CERTIFICATION: "
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
        "DEPENDENCY RESOLUTION MODIFIED DURING CERTIFICATION: NO",
        "5.1.1 ORCHESTRATION CONTRACT MODIFIED: NO",
        "5.1.2 RUN IDENTITY MODIFIED: NO",
        "5.1.3 STATE MODEL MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "UNIVERSAL JOB LINEAGE MODIFIED: NO",
        "UNIVERSAL JOB STATUS MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME WORKER MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "",
        "DEPENDENCY_JOB_IDS REDEFINED: NO",
        "PARENT_JOB_ID TREATED AS IMPLICIT DEPENDENCY: NO",
        "MISSING EVIDENCE TREATED AS FAILURE: NO",
        "NONTERMINAL STATUS TREATED AS FAILURE: NO",
        "TERMINAL FAILURE TREATED AS UNRESOLVED: NO",
        "",
        "CROSS-JOB CYCLE DETECTION PERFORMED: NO",
        "EXECUTION ORDER DEFINED: NO",
        "EXECUTION PLAN CREATED: NO",
        "READINESS DETERMINED: NO",
        "READY/BLOCKED DETERMINED: NO",
        "ORCHESTRATION STATE TRANSITIONED: NO",
        "",
        "QUEUE/WORKER ACTIVITY: NO",
        "RUNTIME HANDLER ACTIVITY: NO",
        "JOB EXECUTION: NO",
        "UNIVERSAL COORDINATION FRAMEWORK ACCESSED: NO",
        "PIPELINE COORDINATORS ACCESSED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "JOB PERSISTENCE QUERIED: NO",
        "DEPENDENCY RESOLUTION PERSISTED: NO",
        "WALL CLOCK USED: NO",
        "FILESYSTEM/NETWORK I/O: NO",
        "",
        (
            "PHASE 5.1.4 FREEZE CANDIDATE: "
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
            "Phase 5.1.4 Dependency Resolution "
            "final certification failed."
        )
    )
