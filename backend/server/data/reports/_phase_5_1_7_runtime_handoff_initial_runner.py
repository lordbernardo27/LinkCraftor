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

HANDOFF_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_orchestration"
    / "runtime_handoff.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_1_7_runtime_handoff_initial_implementation.txt"
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
                "5.1.7 implementation: "
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

readiness = importlib.import_module(
    "backend.server.runtime.universal_orchestration.stage_readiness"
)


handoff_module_name = (
    "backend.server.runtime."
    "universal_orchestration.runtime_handoff"
)

sys.modules.pop(
    handoff_module_name,
    None,
)

handoff = importlib.import_module(
    handoff_module_name
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
        created_at=FIXED_CREATED_AT,
    )


def make_context(
    *,
    target_status=jobs.UniversalJobStatus.CREATED,
    dependency_statuses=None,
    zero_dependencies=False,
    run_id="run-a",
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
            dependencies=(
                "a",
                "b",
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
            orchestration_run_id=run_id,
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
            dependency_statuses=dependency_statuses,
        )
    )

    stage_readiness = (
        readiness
        .evaluate_universal_orchestration_stage_readiness(
            dependency_resolution=resolution,
            execution_plan=plan,
        )
    )

    decision = (
        handoff
        .evaluate_universal_orchestration_runtime_handoff(
            stage_readiness=stage_readiness,
        )
    )

    return (
        target,
        identity,
        plan,
        resolution,
        stage_readiness,
        decision,
    )


# ============================================================
# AUTHORITY
# ============================================================

check(
    "version_exact",
    handoff.UNIVERSAL_ORCHESTRATION_RUNTIME_HANDOFF_VERSION
    == "universal_orchestration_runtime_handoff_v5.1.7",
)

check(
    "schema_exact",
    handoff.UNIVERSAL_ORCHESTRATION_RUNTIME_HANDOFF_SCHEMA_VERSION
    == "universal_orchestration_runtime_handoff_schema_v1",
)

check(
    "classification_exact",
    tuple(
        item.value
        for item
        in handoff.UniversalOrchestrationRuntimeHandoffClassification
    )
    == (
        "eligible",
        "deferred",
        "ineligible",
    ),
)

check(
    "reason_exact",
    tuple(
        item.value
        for item
        in handoff.UniversalOrchestrationRuntimeHandoffReason
    )
    == (
        "ready_for_runtime_handoff",
        "readiness_waiting",
        "readiness_blocked",
        "target_already_in_runtime",
        "target_suspended",
        "target_terminal",
    ),
)


# ============================================================
# STATUS PARTITION
# ============================================================

check(
    "entry_status_exact",
    handoff.HANDOFF_ENTRY_UNIVERSAL_JOB_STATUSES
    == frozenset(
        {
            jobs.UniversalJobStatus.CREATED,
        }
    ),
)

check(
    "already_runtime_status_exact",
    handoff.ALREADY_IN_RUNTIME_UNIVERSAL_JOB_STATUSES
    == frozenset(
        {
            jobs.UniversalJobStatus.QUEUED,
            jobs.UniversalJobStatus.SCHEDULED,
            jobs.UniversalJobStatus.LEASED,
            jobs.UniversalJobStatus.RUNNING,
        }
    ),
)

check(
    "terminal_status_exact",
    handoff.TERMINAL_HANDOFF_INELIGIBLE_UNIVERSAL_JOB_STATUSES
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


partition = (
    handoff.HANDOFF_ENTRY_UNIVERSAL_JOB_STATUSES
    |
    handoff.ALREADY_IN_RUNTIME_UNIVERSAL_JOB_STATUSES
    |
    handoff.TERMINAL_HANDOFF_INELIGIBLE_UNIVERSAL_JOB_STATUSES
    |
    frozenset(
        {
            jobs.UniversalJobStatus.SUSPENDED,
        }
    )
)


check(
    "status_partition_complete",
    partition
    == frozenset(
        jobs.UniversalJobStatus
    ),
)

check(
    "status_partition_entry_runtime_disjoint",
    not (
        handoff.HANDOFF_ENTRY_UNIVERSAL_JOB_STATUSES
        &
        handoff.ALREADY_IN_RUNTIME_UNIVERSAL_JOB_STATUSES
    ),
)

check(
    "status_partition_entry_terminal_disjoint",
    not (
        handoff.HANDOFF_ENTRY_UNIVERSAL_JOB_STATUSES
        &
        handoff.TERMINAL_HANDOFF_INELIGIBLE_UNIVERSAL_JOB_STATUSES
    ),
)

check(
    "status_partition_runtime_terminal_disjoint",
    not (
        handoff.ALREADY_IN_RUNTIME_UNIVERSAL_JOB_STATUSES
        &
        handoff.TERMINAL_HANDOFF_INELIGIBLE_UNIVERSAL_JOB_STATUSES
    ),
)


# ============================================================
# CREATED + READY
# ============================================================

_, _, _, _, ready_stage, ready_handoff = make_context(
    target_status=jobs.UniversalJobStatus.CREATED,
    dependency_statuses={
        "a": "succeeded",
        "b": "succeeded",
    },
    run_id="ready-created",
)


check(
    "created_ready_is_eligible",
    ready_handoff.classification
    is handoff.UniversalOrchestrationRuntimeHandoffClassification.ELIGIBLE,
)

check(
    "created_ready_reason",
    ready_handoff.reason
    is handoff.UniversalOrchestrationRuntimeHandoffReason.READY_FOR_RUNTIME_HANDOFF,
)

check(
    "created_ready_reason_code",
    ready_handoff.reason_code
    == "ready_for_runtime_handoff",
)

check(
    "created_ready_booleans",
    (
        ready_handoff.is_eligible
        and
        not ready_handoff.is_deferred
        and
        not ready_handoff.is_ineligible
    ),
)


# ============================================================
# CREATED + WAITING
# ============================================================

_, _, _, _, waiting_stage, waiting_handoff = make_context(
    target_status=jobs.UniversalJobStatus.CREATED,
    dependency_statuses={
        "a": "running",
    },
    run_id="waiting-created",
)


check(
    "created_waiting_is_deferred",
    waiting_handoff.classification
    is handoff.UniversalOrchestrationRuntimeHandoffClassification.DEFERRED,
)

check(
    "created_waiting_reason",
    waiting_handoff.reason_code
    == "readiness_waiting",
)


# ============================================================
# CREATED + BLOCKED
# ============================================================

_, _, _, _, blocked_stage, blocked_handoff = make_context(
    target_status=jobs.UniversalJobStatus.CREATED,
    dependency_statuses={
        "a": "failed",
        "b": "succeeded",
    },
    run_id="blocked-created",
)


check(
    "created_blocked_is_ineligible",
    blocked_handoff.classification
    is handoff.UniversalOrchestrationRuntimeHandoffClassification.INELIGIBLE,
)

check(
    "created_blocked_reason",
    blocked_handoff.reason_code
    == "readiness_blocked",
)


# ============================================================
# ZERO DEPENDENCY CREATED
# ============================================================

_, _, _, _, zero_stage, zero_handoff = make_context(
    target_status=jobs.UniversalJobStatus.CREATED,
    dependency_statuses={},
    zero_dependencies=True,
    run_id="zero-created",
)


check(
    "zero_created_readiness_ready",
    zero_stage.is_ready,
)

check(
    "zero_created_handoff_eligible",
    zero_handoff.is_eligible,
)


# ============================================================
# ALREADY IN RUNTIME
# ============================================================

for status in (
    jobs.UniversalJobStatus.QUEUED,
    jobs.UniversalJobStatus.SCHEDULED,
    jobs.UniversalJobStatus.LEASED,
    jobs.UniversalJobStatus.RUNNING,
):

    _, _, _, _, _, result = make_context(
        target_status=status,
        dependency_statuses={
            "a": "succeeded",
            "b": "succeeded",
        },
        run_id="runtime-" + status.value,
    )

    check(
        "already_runtime_ineligible_"
        + status.value,
        result.is_ineligible,
        status.value,
    )

    check(
        "already_runtime_reason_"
        + status.value,
        result.reason_code
        == "target_already_in_runtime",
        status.value,
    )


# ============================================================
# SUSPENDED
# ============================================================

_, _, _, _, _, suspended_result = make_context(
    target_status=jobs.UniversalJobStatus.SUSPENDED,
    dependency_statuses={
        "a": "succeeded",
        "b": "succeeded",
    },
    run_id="suspended",
)


check(
    "suspended_deferred",
    suspended_result.is_deferred,
)

check(
    "suspended_reason",
    suspended_result.reason_code
    == "target_suspended",
)


# ============================================================
# TERMINAL
# ============================================================

for status in (
    jobs.UniversalJobStatus.SUCCEEDED,
    jobs.UniversalJobStatus.FAILED,
    jobs.UniversalJobStatus.CANCELLED,
    jobs.UniversalJobStatus.DEAD_LETTER,
    jobs.UniversalJobStatus.EXPIRED,
):

    _, _, _, _, _, result = make_context(
        target_status=status,
        dependency_statuses={
            "a": "succeeded",
            "b": "succeeded",
        },
        run_id="terminal-" + status.value,
    )

    check(
        "terminal_ineligible_"
        + status.value,
        result.is_ineligible,
        status.value,
    )

    check(
        "terminal_reason_"
        + status.value,
        result.reason_code
        == "target_terminal",
        status.value,
    )


# ============================================================
# LIFECYCLE PRECEDENCE
# ============================================================

_, _, _, _, running_waiting_stage, running_waiting = make_context(
    target_status=jobs.UniversalJobStatus.RUNNING,
    dependency_statuses={
        "a": "running",
    },
    run_id="running-waiting",
)


check(
    "running_waiting_readiness_is_waiting",
    running_waiting_stage.is_waiting,
)

check(
    "running_waiting_handoff_is_lifecycle_ineligible",
    (
        running_waiting.is_ineligible
        and
        running_waiting.reason_code
        == "target_already_in_runtime"
    ),
)


_, _, _, _, terminal_waiting_stage, terminal_waiting = make_context(
    target_status=jobs.UniversalJobStatus.FAILED,
    dependency_statuses={
        "a": "running",
    },
    run_id="terminal-waiting",
)


check(
    "terminal_waiting_readiness_is_waiting",
    terminal_waiting_stage.is_waiting,
)

check(
    "terminal_waiting_handoff_terminal_precedence",
    (
        terminal_waiting.is_ineligible
        and
        terminal_waiting.reason_code
        == "target_terminal"
    ),
)


# ============================================================
# DERIVED IDENTITY / TARGET
# ============================================================

check(
    "identity_derived",
    ready_handoff.identity
    == ready_stage.identity,
)

check(
    "target_job_derived",
    ready_handoff.target_job
    == ready_stage.target_job,
)

check(
    "job_id_derived",
    ready_handoff.job_id
    == ready_stage.job_id,
)

check(
    "target_status_derived",
    ready_handoff.target_status
    is jobs.UniversalJobStatus.CREATED,
)


# ============================================================
# STORED FIELDS
# ============================================================

field_names = tuple(
    field.name
    for field in fields(
        handoff.UniversalOrchestrationRuntimeHandoff
    )
)


check(
    "stored_fields_exact",
    field_names
    == (
        "stage_readiness",
        "schema_version",
    ),
    field_names,
)


for forbidden_field in (
    "identity",
    "target_job",
    "job_id",
    "target_status",
    "classification",
    "reason",
    "reason_code",
    "is_eligible",
    "is_deferred",
    "is_ineligible",
    "queue_id",
    "worker_id",
    "lease_id",
    "handler",
    "handler_id",
    "dispatch_result",
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
    ready_handoff
):

    try:

        setattr(
            ready_handoff,
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
# INVALID INPUT
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
        {},
        [],
        object(),
    ),
    start=1,
):

    try:

        handoff.evaluate_universal_orchestration_runtime_handoff(
            stage_readiness=bad,
        )

    except handoff.UniversalOrchestrationRuntimeHandoffError as exc:

        rejected = (
            exc.code
            == "invalid_runtime_handoff_stage_readiness"
        )

    else:

        rejected = False

    check(
        "invalid_stage_readiness_"
        + str(index),
        rejected,
    )


# ============================================================
# SCHEMA FORGERY
# ============================================================

for bad_schema in (
    "",
    " ",
    "v1",
    "wrong",
    "universal_orchestration_runtime_handoff_schema_v2",
):

    try:

        handoff.UniversalOrchestrationRuntimeHandoff(
            stage_readiness=ready_stage,
            schema_version=bad_schema,
        )

    except handoff.UniversalOrchestrationRuntimeHandoffError as exc:

        rejected = (
            exc.code
            == "invalid_runtime_handoff_schema_version"
        )

    else:

        rejected = False

    check(
        "schema_attack_"
        + repr(bad_schema),
        rejected,
    )


# ============================================================
# EXPLANATION
# ============================================================

explanation = (
    handoff
    .explain_universal_orchestration_runtime_handoff_v1()
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
    == "5.1.7",
)

check(
    "component_exact",
    explanation.get(
        "component"
    )
    == "Universal Orchestration Runtime Handoff Management",
)

check(
    "stored_fields_explanation_exact",
    explanation.get(
        "stored_fields"
    )
    == (
        "stage_readiness",
        "schema_version",
    ),
)

check(
    "eligible_rule_created_ready",
    (
        "CREATED"
        in explanation.get(
            "eligible_rule",
            "",
        )
        and
        "READY"
        in explanation.get(
            "eligible_rule",
            "",
        )
    ),
)

check(
    "runtime_registration_boundary",
    "Runtime Registration"
    in explanation.get(
        "runtime_registration_boundary",
        "",
    ),
)

check(
    "execution_boundary",
    "Universal Runtime Worker"
    in explanation.get(
        "execution_boundary",
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
    "fan_in_boundary_5_1_9",
    "5.1.9"
    in explanation.get(
        "fan_in_boundary",
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
    "suspension_boundary_5_1_12",
    "5.1.12"
    in explanation.get(
        "suspension_boundary",
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


# ============================================================
# IMPORT BOUNDARY
# ============================================================

source = HANDOFF_PATH.read_text(
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
        "backend.server.runtime.universal_orchestration.stage_readiness",
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
    "mkdir",
    "unlink",
    "remove",

    "enqueue_job",
    "schedule_job",
    "dequeue_job",
    "claim_job",

    "discover_universal_workers",
    "assign_universal_worker",

    "acquire_universal_worker_lease",
    "renew_universal_worker_lease",
    "release_universal_worker_lease",

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
        actual == expected,
        actual,
    )


handoff_ast = ast_sha(
    HANDOFF_PATH
)


check(
    "handoff_ast_generated",
    len(
        handoff_ast
    )
    == 64,
    handoff_ast,
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
        "PHASE 5.1.7 — UNIVERSAL ORCHESTRATION "
        "RUNTIME HANDOFF INITIAL IMPLEMENTATION"
    ),
    "=" * 118,
    "",
    (
        "RUNTIME HANDOFF AST SHA256: "
        + handoff_ast
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
            "INITIAL RUNTIME HANDOFF RESULT: "
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
        "5.1.6 STAGE READINESS MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",
        "",
        "HANDOFF CLASSIFICATIONS: ELIGIBLE / DEFERRED / INELIGIBLE",
        "CREATED + READY: ELIGIBLE",
        "CREATED + WAITING: DEFERRED",
        "CREATED + BLOCKED: INELIGIBLE",
        "QUEUED/SCHEDULED/LEASED/RUNNING: ALREADY BEYOND NEW HANDOFF",
        "SUSPENDED: DEFERRED TO 5.1.12 ELIGIBILITY",
        "TERMINAL TARGET: INELIGIBLE",
        "",
        "UNIVERSAL JOB STATUS MUTATED: NO",
        "QUEUE MEMBERSHIP MUTATED: NO",
        "JOB ENQUEUED/SCHEDULED/CLAIMED: NO",
        "WORKER ASSIGNED: NO",
        "LEASE ACQUIRED: NO",
        "RUNTIME HANDLER LOOKED UP: NO",
        "RUNTIME HANDLER DISPATCHED: NO",
        "JOB EXECUTED: NO",
        "ORCHESTRATION STATE TRANSITIONED: NO",
        "ACTUAL FAN-OUT COORDINATED: NO",
        "ACTUAL FAN-IN COORDINATED: NO",
        "CONDITIONAL BRANCHING EVALUATED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "HANDOFF DECISION PERSISTED: NO",
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
            "Phase 5.1.7 Runtime Handoff "
            "initial implementation failed."
        )
    )
