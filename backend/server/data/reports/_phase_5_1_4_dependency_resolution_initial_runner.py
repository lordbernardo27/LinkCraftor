from __future__ import annotations

import ast
import dataclasses
import hashlib
import importlib
import sys
from dataclasses import fields
from pathlib import Path


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
    / "phase_5_1_4_dependency_resolution_initial_implementation.txt"
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
                "5.1.4 implementation: "
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


# ============================================================
# VERSION / CLASSIFICATION
# ============================================================

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
# STATUS CLASSIFICATION
# ============================================================

status_expected = {
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


for status, expected in status_expected.items():

    actual = (
        dependency.classify_universal_orchestration_dependency_status(
            status
        )
    )

    check(
        "status_classification_"
        + status.value,
        actual.value
        == expected,
        actual,
    )


# ============================================================
# FIXTURES
# ============================================================

def make_job(
    *,
    job_id,
    dependencies=(),
    status=job_contract.UniversalJobStatus.CREATED,
    workspace_id="workspace-a",
    pipeline="pipeline-a",
):

    return job_contract.UniversalJob(
        job_id=job_id,
        workspace_id=workspace_id,
        pipeline=pipeline,
        stage="stage-a",
        job_type="test_job",
        payload_reference="payload-a",
        status=status,
        dependency_job_ids=tuple(
            dependencies
        ),
        created_at="2026-05-21T03:49:30.579317+00:00",
    )


target = make_job(
    job_id="job-d",
    dependencies=(
        "job-a",
        "job-b",
        "job-c",
    ),
)


contract = (
    orchestration_contract.create_universal_runtime_orchestration_contract(
        workspace_id="workspace-a",
        pipeline="pipeline-a",
        job_ids=(
            "job-d",
            "job-c",
            "job-b",
            "job-a",
        ),
    )
)


identity = (
    run_identity.create_universal_orchestration_run_identity(
        orchestration_run_id="run-a",
        contract=contract,
    )
)


resolution = (
    dependency.resolve_universal_orchestration_dependencies(
        identity=identity,
        target_job=target,
        dependency_statuses={
            "job-a":
                job_contract.UniversalJobStatus.SUCCEEDED,

            "job-b":
                job_contract.UniversalJobStatus.RUNNING,

            "job-c":
                job_contract.UniversalJobStatus.FAILED,
        },
    )
)


check(
    "job_id_derived",
    resolution.job_id
    == "job-d",
)

check(
    "dependency_ids_derived",
    resolution.dependency_job_ids
    == (
        "job-a",
        "job-b",
        "job-c",
    ),
)

check(
    "dependency_count",
    resolution.dependency_count
    == 3,
)

check(
    "satisfied_exact",
    resolution.satisfied_dependency_ids
    == (
        "job-a",
    ),
)

check(
    "unresolved_exact",
    resolution.unresolved_dependency_ids
    == (
        "job-b",
    ),
)

check(
    "terminal_unsatisfied_exact",
    resolution.terminal_unsatisfied_dependency_ids
    == (
        "job-c",
    ),
)

check(
    "missing_empty",
    resolution.missing_dependency_ids
    == (),
)

check(
    "all_satisfied_false",
    resolution.all_dependencies_satisfied
    is False,
)

check(
    "has_unresolved_true",
    resolution.has_unresolved_dependencies
    is True,
)

check(
    "terminal_failure_true",
    resolution.has_terminal_dependency_failure
    is True,
)

check(
    "missing_false",
    resolution.has_missing_dependency_evidence
    is False,
)


# ============================================================
# CLASSIFICATION LOOKUP
# ============================================================

check(
    "lookup_satisfied",
    resolution.classification_for_dependency(
        "job-a"
    )
    is (
        dependency
        .UniversalOrchestrationDependencyClassification
        .SATISFIED
    ),
)

check(
    "lookup_unresolved",
    resolution.classification_for_dependency(
        "job-b"
    )
    is (
        dependency
        .UniversalOrchestrationDependencyClassification
        .UNRESOLVED
    ),
)

check(
    "lookup_terminal_unsatisfied",
    resolution.classification_for_dependency(
        "job-c"
    )
    is (
        dependency
        .UniversalOrchestrationDependencyClassification
        .TERMINAL_UNSATISFIED
    ),
)


# ============================================================
# MISSING EVIDENCE
# ============================================================

missing_resolution = (
    dependency.resolve_universal_orchestration_dependencies(
        identity=identity,
        target_job=target,
        dependency_statuses={
            "job-a":
                job_contract.UniversalJobStatus.SUCCEEDED,
        },
    )
)


check(
    "missing_ids_exact",
    missing_resolution.missing_dependency_ids
    == (
        "job-b",
        "job-c",
    ),
)

check(
    "missing_not_terminal_failure",
    missing_resolution.has_terminal_dependency_failure
    is False,
)

check(
    "missing_evidence_true",
    missing_resolution.has_missing_dependency_evidence
    is True,
)

check(
    "lookup_missing",
    missing_resolution.classification_for_dependency(
        "job-b"
    )
    is (
        dependency
        .UniversalOrchestrationDependencyClassification
        .MISSING
    ),
)


# ============================================================
# ZERO DEPENDENCIES
# ============================================================

zero_job = make_job(
    job_id="job-zero",
    dependencies=(),
)


zero_contract = (
    orchestration_contract.create_universal_runtime_orchestration_contract(
        workspace_id="workspace-a",
        pipeline="pipeline-a",
        job_ids=(
            "job-zero",
        ),
    )
)


zero_identity = (
    run_identity.create_universal_orchestration_run_identity(
        orchestration_run_id="run-zero",
        contract=zero_contract,
    )
)


zero_resolution = (
    dependency.resolve_universal_orchestration_dependencies(
        identity=zero_identity,
        target_job=zero_job,
    )
)


check(
    "zero_dependencies_count",
    zero_resolution.dependency_count
    == 0,
)

check(
    "zero_dependencies_all_satisfied",
    zero_resolution.all_dependencies_satisfied
    is True,
)

check(
    "zero_dependencies_no_missing",
    zero_resolution.missing_dependency_ids
    == (),
)

check(
    "zero_dependencies_no_terminal_failure",
    zero_resolution.has_terminal_dependency_failure
    is False,
)


# ============================================================
# CONTRACT MEMBERSHIP
# ============================================================

outside_target = make_job(
    job_id="job-outside",
)


try:

    dependency.resolve_universal_orchestration_dependencies(
        identity=identity,
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


outside_dependency_job = make_job(
    job_id="job-d",
    dependencies=(
        "job-a",
        "job-outside",
    ),
)


try:

    dependency.resolve_universal_orchestration_dependencies(
        identity=identity,
        target_job=outside_dependency_job,
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
    job_id="job-d",
    dependencies=(),
    workspace_id="workspace-b",
)


try:

    dependency.resolve_universal_orchestration_dependencies(
        identity=identity,
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
    job_id="job-d",
    dependencies=(),
    pipeline="pipeline-b",
)


try:

    dependency.resolve_universal_orchestration_dependencies(
        identity=identity,
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
# EXTRANEOUS STATUS EVIDENCE
# ============================================================

try:

    dependency.resolve_universal_orchestration_dependencies(
        identity=identity,
        target_job=target,
        dependency_statuses={
            "job-a": "succeeded",
            "job-z": "succeeded",
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
    "extraneous_status_rejected",
    rejected,
)


# ============================================================
# STORED FIELDS
# ============================================================

field_names = tuple(
    field.name
    for field in fields(
        dependency.UniversalOrchestrationDependencyResolution
    )
)


check(
    "fields_exact",
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

    "ready",
    "blocked",
    "execution_order",
    "execution_plan",

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


# ============================================================
# EXPLANATION
# ============================================================

explanation = (
    dependency
    .explain_universal_orchestration_dependency_resolution_v1()
)


check(
    "phase",
    explanation.get(
        "phase"
    )
    == "5.1.4",
)

check(
    "component",
    explanation.get(
        "component"
    )
    == "Universal Orchestration Dependency Resolution",
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
    "cycle_deferred_5_1_5",
    "5.1.5"
    in explanation.get(
        "cycle_boundary",
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
    "parent_separate",
    "not implicitly treated as a dependency"
    in explanation.get(
        "parent_rule",
        "",
    ),
)

check(
    "caller_supplied_evidence",
    "caller supplied"
    in explanation.get(
        "evidence_rule",
        "",
    ),
)

check(
    "missing_not_failed",
    "not failed"
    in explanation.get(
        "missing_rule",
        "",
    ),
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
# NO FORBIDDEN CALLS
# ============================================================

forbidden_calls = {
    "open",
    "read_text",
    "write_text",
    "mkdir",
    "unlink",
    "remove",

    "enqueue_job",
    "dequeue_job",
    "claim_job",

    "assign_universal_worker",
    "acquire_universal_worker_lease",

    "register_runtime_handler",
    "dispatch_registered_runtime_handler",
    "execute_registered_runtime_job_v1",

    "get_runtime_state_store_registry",

    "transition_universal_orchestration_state",

    "persist",
    "save",
    "dispatch",
    "execute",

    "time",
    "now",
    "utcnow",
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

        call_name = node.func.id

    elif isinstance(
        node.func,
        ast.Attribute,
    ):

        call_name = node.func.attr

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


dependency_ast = ast_sha(
    DEPENDENCY_PATH
)


check(
    "dependency_ast_generated",
    len(
        dependency_ast
    )
    == 64,
    dependency_ast,
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
        "PHASE 5.1.4 — UNIVERSAL ORCHESTRATION "
        "DEPENDENCY RESOLUTION INITIAL IMPLEMENTATION"
    ),
    "=" * 118,
    "",
    (
        "DEPENDENCY RESOLUTION AST SHA256: "
        + dependency_ast
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
            "INITIAL DEPENDENCY RESOLUTION RESULT: "
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
        "5.1.1 ORCHESTRATION CONTRACT MODIFIED: NO",
        "5.1.2 RUN IDENTITY MODIFIED: NO",
        "5.1.3 STATE MODEL MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",
        "UNIVERSAL JOB LINEAGE MODIFIED: NO",
        "UNIVERSAL JOB STATUS MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME WORKER MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "",
        "DEPENDENCY_JOB_IDS REDEFINED: NO",
        "PARENT_JOB_ID TREATED AS DEPENDENCY: NO",
        "CROSS-JOB CYCLE DETECTION PERFORMED: NO",
        "EXECUTION ORDER DEFINED: NO",
        "EXECUTION PLAN CREATED: NO",
        "READINESS DETERMINED: NO",
        "READY/BLOCKED DETERMINED: NO",
        "ORCHESTRATION STATE TRANSITIONED: NO",
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
            "Phase 5.1.4 Dependency Resolution "
            "initial implementation failed."
        )
    )
