from __future__ import annotations

import ast
import hashlib
import importlib
import sys
from dataclasses import fields
from pathlib import Path


ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

READINESS_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_orchestration"
    / "stage_readiness.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_1_6_stage_readiness_initial_implementation.txt"
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
                "5.1.6 implementation: "
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

dependencies = importlib.import_module(
    "backend.server.runtime.universal_orchestration.dependency_resolution"
)

planning = importlib.import_module(
    "backend.server.runtime.universal_orchestration.execution_planning"
)

readiness_name = (
    "backend.server.runtime."
    "universal_orchestration.stage_readiness"
)

sys.modules.pop(
    readiness_name,
    None,
)

readiness = importlib.import_module(
    readiness_name
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
    dependency_job_ids=(),
    status=jobs.UniversalJobStatus.CREATED,
):

    return jobs.UniversalJob(
        job_id=job_id,
        workspace_id="workspace-a",
        pipeline="pipeline-a",
        stage="stage-a",
        job_type="test_job",
        payload_reference="payload-a",
        dependency_job_ids=tuple(
            dependency_job_ids
        ),
        status=status,
        created_at=FIXED_CREATED_AT,
    )


def make_context(
    *,
    target_status=jobs.UniversalJobStatus.CREATED,
    dependency_statuses=None,
    zero_dependencies=False,
):

    if zero_dependencies:

        target = make_job(
            job_id="target",
            status=target_status,
        )

        all_jobs = (
            target,
        )

    else:

        target = make_job(
            job_id="target",
            dependency_job_ids=(
                "a",
                "b",
                "c",
            ),
            status=target_status,
        )

        all_jobs = (
            make_job(
                job_id="a",
            ),
            make_job(
                job_id="b",
            ),
            make_job(
                job_id="c",
            ),
            target,
        )

    contract = (
        contracts
        .create_universal_runtime_orchestration_contract(
            workspace_id="workspace-a",
            pipeline="pipeline-a",
            job_ids=tuple(
                job.job_id
                for job
                in all_jobs
            ),
        )
    )

    identity = (
        identities
        .create_universal_orchestration_run_identity(
            orchestration_run_id="run-a",
            contract=contract,
        )
    )

    plan = (
        planning
        .create_universal_orchestration_execution_plan(
            identity=identity,
            jobs=all_jobs,
        )
    )

    resolution = (
        dependencies
        .resolve_universal_orchestration_dependencies(
            identity=identity,
            target_job=target,
            dependency_statuses=(
                dependency_statuses
                if dependency_statuses is not None
                else {}
            ),
        )
    )

    result = (
        readiness
        .evaluate_universal_orchestration_stage_readiness(
            dependency_resolution=resolution,
            execution_plan=plan,
        )
    )

    return (
        target,
        identity,
        plan,
        resolution,
        result,
    )


# ============================================================
# VERSION / ENUMS
# ============================================================

check(
    "version_exact",
    readiness.UNIVERSAL_ORCHESTRATION_STAGE_READINESS_VERSION
    == "universal_orchestration_stage_readiness_v5.1.6",
)

check(
    "schema_exact",
    readiness.UNIVERSAL_ORCHESTRATION_STAGE_READINESS_SCHEMA_VERSION
    == "universal_orchestration_stage_readiness_schema_v1",
)

check(
    "classification_exact",
    tuple(
        member.value
        for member
        in readiness.UniversalOrchestrationStageReadinessClassification
    )
    == (
        "ready",
        "waiting",
        "blocked",
    ),
)

check(
    "reason_exact",
    tuple(
        member.value
        for member
        in readiness.UniversalOrchestrationStageReadinessReason
    )
    == (
        "all_dependencies_satisfied",
        "dependency_evidence_pending",
        "terminal_dependency_failure",
    ),
)


# ============================================================
# READY
# ============================================================

_, _, _, ready_resolution, ready_result = make_context(
    dependency_statuses={
        "a": "succeeded",
        "b": "succeeded",
        "c": "succeeded",
    },
)


check(
    "ready_classification",
    ready_result.classification
    is readiness.UniversalOrchestrationStageReadinessClassification.READY,
)

check(
    "ready_reason",
    ready_result.reason_code
    == "all_dependencies_satisfied",
)

check(
    "ready_boolean",
    ready_result.is_ready
    is True,
)

check(
    "ready_not_waiting",
    ready_result.is_waiting
    is False,
)

check(
    "ready_not_blocked",
    ready_result.is_blocked
    is False,
)


# ============================================================
# WAITING — UNRESOLVED
# ============================================================

_, _, _, unresolved_resolution, unresolved_result = make_context(
    dependency_statuses={
        "a": "succeeded",
        "b": "running",
        "c": "queued",
    },
)


check(
    "unresolved_waiting",
    unresolved_result.classification
    is readiness.UniversalOrchestrationStageReadinessClassification.WAITING,
)

check(
    "unresolved_waiting_reason",
    unresolved_result.reason_code
    == "dependency_evidence_pending",
)

check(
    "unresolved_ids",
    unresolved_result.unresolved_dependency_ids
    == (
        "b",
        "c",
    ),
)

check(
    "unresolved_waiting_ids",
    unresolved_result.waiting_dependency_ids
    == (
        "b",
        "c",
    ),
)


# ============================================================
# WAITING — MISSING
# ============================================================

_, _, _, missing_resolution, missing_result = make_context(
    dependency_statuses={
        "a": "succeeded",
    },
)


check(
    "missing_waiting",
    missing_result.classification
    is readiness.UniversalOrchestrationStageReadinessClassification.WAITING,
)

check(
    "missing_ids",
    missing_result.missing_dependency_ids
    == (
        "b",
        "c",
    ),
)

check(
    "missing_waiting_ids",
    missing_result.waiting_dependency_ids
    == (
        "b",
        "c",
    ),
)


# ============================================================
# BLOCKED
# ============================================================

_, _, _, blocked_resolution, blocked_result = make_context(
    dependency_statuses={
        "a": "succeeded",
        "b": "failed",
        "c": "running",
    },
)


check(
    "blocked_classification",
    blocked_result.classification
    is readiness.UniversalOrchestrationStageReadinessClassification.BLOCKED,
)

check(
    "blocked_reason",
    blocked_result.reason_code
    == "terminal_dependency_failure",
)

check(
    "blocked_ids",
    blocked_result.blocking_dependency_ids
    == (
        "b",
    ),
)

check(
    "blocked_precedence_over_waiting",
    (
        blocked_resolution.has_terminal_dependency_failure
        and
        blocked_resolution.has_unresolved_dependencies
        and
        blocked_result.is_blocked
    ),
)


# ============================================================
# TERMINAL + MISSING → BLOCKED
# ============================================================

_, _, _, _, blocked_missing_result = make_context(
    dependency_statuses={
        "a": "failed",
    },
)


check(
    "blocked_precedence_over_missing",
    blocked_missing_result.is_blocked
    is True,
)


# ============================================================
# UNRESOLVED + MISSING → WAITING
# ============================================================

_, _, _, _, waiting_mixed_result = make_context(
    dependency_statuses={
        "a": "running",
    },
)


check(
    "waiting_unresolved_plus_missing",
    waiting_mixed_result.is_waiting
    is True,
)


# ============================================================
# ZERO DEPENDENCIES
# ============================================================

_, _, _, zero_resolution, zero_result = make_context(
    zero_dependencies=True,
)


check(
    "zero_dependencies_resolution_satisfied",
    zero_resolution.all_dependencies_satisfied
    is True,
)

check(
    "zero_dependencies_ready",
    zero_result.is_ready
    is True,
)

check(
    "zero_dependencies_reason",
    zero_result.reason_code
    == "all_dependencies_satisfied",
)


# ============================================================
# TARGET STATUS DOES NOT ALTER DEPENDENCY READINESS
# ============================================================

for status in (
    jobs.UniversalJobStatus.CREATED,
    jobs.UniversalJobStatus.QUEUED,
    jobs.UniversalJobStatus.SCHEDULED,
    jobs.UniversalJobStatus.LEASED,
    jobs.UniversalJobStatus.RUNNING,
    jobs.UniversalJobStatus.SUSPENDED,
    jobs.UniversalJobStatus.SUCCEEDED,
    jobs.UniversalJobStatus.FAILED,
    jobs.UniversalJobStatus.CANCELLED,
    jobs.UniversalJobStatus.DEAD_LETTER,
    jobs.UniversalJobStatus.EXPIRED,
):

    _, _, _, _, result = make_context(
        target_status=status,
        dependency_statuses={
            "a": "succeeded",
            "b": "succeeded",
            "c": "succeeded",
        },
    )

    check(
        "target_status_not_readiness_"
        + status.value,
        result.is_ready
        is True,
        status.value,
    )


# ============================================================
# STORED FIELDS
# ============================================================

field_names = tuple(
    field.name
    for field in fields(
        readiness.UniversalOrchestrationStageReadiness
    )
)


check(
    "stored_fields_exact",
    field_names
    == (
        "dependency_resolution",
        "execution_plan",
        "schema_version",
    ),
    field_names,
)


for forbidden in (
    "identity",
    "target_job",
    "job_id",
    "classification",
    "reason",
    "reason_code",
    "is_ready",
    "is_waiting",
    "is_blocked",
    "satisfied_dependency_ids",
    "unresolved_dependency_ids",
    "terminal_unsatisfied_dependency_ids",
    "missing_dependency_ids",
    "blocking_dependency_ids",
    "waiting_dependency_ids",
    "job_status",
    "queue_status",
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
    ready_result
):

    try:

        setattr(
            ready_result,
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
# ALIGNMENT
# ============================================================

other_contract = (
    contracts
    .create_universal_runtime_orchestration_contract(
        workspace_id="workspace-a",
        pipeline="pipeline-a",
        job_ids=(
            "target",
        ),
    )
)

other_identity = (
    identities
    .create_universal_orchestration_run_identity(
        orchestration_run_id="other-run",
        contract=other_contract,
    )
)

other_target = make_job(
    job_id="target",
)

other_plan = (
    planning
    .create_universal_orchestration_execution_plan(
        identity=other_identity,
        jobs=(
            other_target,
        ),
    )
)


try:

    readiness.evaluate_universal_orchestration_stage_readiness(
        dependency_resolution=ready_resolution,
        execution_plan=other_plan,
    )

except readiness.UniversalOrchestrationStageReadinessError as exc:

    rejected = (
        exc.code
        == "stage_readiness_identity_mismatch"
    )

else:

    rejected = False


check(
    "identity_mismatch_rejected",
    rejected,
)


# ============================================================
# TYPE ATTACKS
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

        readiness.evaluate_universal_orchestration_stage_readiness(
            dependency_resolution=bad,
            execution_plan=ready_result.execution_plan,
        )

    except readiness.UniversalOrchestrationStageReadinessError as exc:

        rejected = (
            exc.code
            == "invalid_stage_readiness_dependency_resolution"
        )

    else:

        rejected = False

    check(
        "bad_dependency_resolution_"
        + str(index),
        rejected,
    )


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

        readiness.evaluate_universal_orchestration_stage_readiness(
            dependency_resolution=ready_resolution,
            execution_plan=bad,
        )

    except readiness.UniversalOrchestrationStageReadinessError as exc:

        rejected = (
            exc.code
            == "invalid_stage_readiness_execution_plan"
        )

    else:

        rejected = False

    check(
        "bad_execution_plan_"
        + str(index),
        rejected,
    )


# ============================================================
# EXPLANATION
# ============================================================

explanation = (
    readiness
    .explain_universal_orchestration_stage_readiness_v1()
)


check(
    "phase",
    explanation.get(
        "phase"
    )
    == "5.1.6",
)

check(
    "component",
    explanation.get(
        "component"
    )
    == "Universal Orchestration Stage Readiness Evaluation",
)

check(
    "precedence",
    explanation.get(
        "precedence_rule"
    )
    == "BLOCKED outranks WAITING; WAITING outranks READY.",
)

check(
    "handoff_deferred_5_1_7",
    "5.1.7"
    in explanation.get(
        "handoff_boundary",
        "",
    ),
)

check(
    "suspension_deferred_5_1_12",
    "5.1.12"
    in explanation.get(
        "suspension_boundary",
        "",
    ),
)

check(
    "dependency_source_5_1_4",
    "5.1.4"
    in explanation.get(
        "dependency_boundary",
        "",
    ),
)

check(
    "planning_source_5_1_5",
    "5.1.5"
    in explanation.get(
        "planning_boundary",
        "",
    ),
)


# ============================================================
# IMPORT BOUNDARY
# ============================================================

source = READINESS_PATH.read_text(
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
        "backend.server.runtime.universal_orchestration.dependency_resolution",
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

        call_name = node.func.id

    elif isinstance(
        node.func,
        ast.Attribute,
    ):

        call_name = node.func.attr

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
# TARGET STATUS NOT INSPECTED BY SOURCE
# ============================================================

attributes = tuple(
    node.attr
    for node in ast.walk(
        tree
    )
    if isinstance(
        node,
        ast.Attribute,
    )
)


check(
    "target_job_status_not_inspected",
    "status"
    not in attributes,
    attributes,
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


readiness_ast = ast_sha(
    READINESS_PATH
)


check(
    "readiness_ast_generated",
    len(
        readiness_ast
    )
    == 64,
    readiness_ast,
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
        "PHASE 5.1.6 — UNIVERSAL ORCHESTRATION "
        "STAGE READINESS INITIAL IMPLEMENTATION"
    ),
    "=" * 118,
    "",
    (
        "STAGE READINESS AST SHA256: "
        + readiness_ast
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
            "INITIAL STAGE READINESS RESULT: "
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
        "5.1.4 DEPENDENCY RESOLUTION MODIFIED: NO",
        "5.1.5 EXECUTION PLANNING MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",
        "",
        "READINESS VOCABULARY: READY / WAITING / BLOCKED",
        "PRECEDENCE: BLOCKED > WAITING > READY",
        "TARGET UNIVERSAL JOB STATUS INSPECTED: NO",
        "WORKER/QUEUE ELIGIBILITY INSPECTED: NO",
        "RUNTIME HANDOFF PERFORMED: NO",
        "ORCHESTRATION STATE TRANSITIONED: NO",
        "ACTUAL FAN-OUT COORDINATED: NO",
        "ACTUAL FAN-IN COORDINATED: NO",
        "CONDITIONAL BRANCHING EVALUATED: NO",
        "QUEUE/WORKER ACTIVITY: NO",
        "RUNTIME HANDLER ACTIVITY: NO",
        "JOB EXECUTION: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "READINESS PERSISTED: NO",
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
            "Phase 5.1.6 Stage Readiness "
            "initial implementation failed."
        )
    )
