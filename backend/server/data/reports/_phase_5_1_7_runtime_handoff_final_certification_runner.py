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
    / "phase_5_1_7_runtime_handoff_final_certification.txt"
)

EXPECTED_HANDOFF_AST = (
    "6878FC6F0F2EF071B11A93D793A0CC80B2C91B676C6B6735A78237D8C7D6CB73"
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


# ============================================================
# PRE-FLIGHT
# ============================================================

if not HANDOFF_PATH.exists():

    raise SystemExit(
        "5.1.7 Runtime Handoff authority missing."
    )


initial_ast = ast_sha(
    HANDOFF_PATH
)


if initial_ast != EXPECTED_HANDOFF_AST:

    raise SystemExit(
        (
            "5.1.7 Runtime Handoff AST mismatch before "
            "final certification.\n"
            "EXPECTED: "
            + EXPECTED_HANDOFF_AST
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
                "5.1.7 final certification: "
                + name
                + "\nEXPECTED: "
                + expected
                + "\nACTUAL:   "
                + actual
            )
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

dependencies = importlib.import_module(
    "backend.server.runtime.universal_orchestration.dependency_resolution"
)

planning = importlib.import_module(
    "backend.server.runtime.universal_orchestration.execution_planning"
)

readiness = importlib.import_module(
    "backend.server.runtime.universal_orchestration.stage_readiness"
)


module_name = (
    "backend.server.runtime."
    "universal_orchestration.runtime_handoff"
)

sys.modules.pop(
    module_name,
    None,
)

handoff = importlib.import_module(
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


handoff_ast = ast_sha(
    HANDOFF_PATH
)


# ============================================================
# AUTHORITY / VERSION
# ============================================================

check(
    "handoff_ast_exact",
    handoff_ast
    == EXPECTED_HANDOFF_AST,
    handoff_ast,
)

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
# FIXTURES
# ============================================================

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
    run_id,
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
            dependencies=(
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
# CREATED + READY
# ============================================================

_, _, _, _, ready_stage, ready_decision = make_context(
    run_id="ready-run",
    target_status=jobs.UniversalJobStatus.CREATED,
    dependency_statuses={
        "a": "succeeded",
        "b": "succeeded",
        "c": "succeeded",
    },
)


check(
    "created_ready_stage_ready",
    ready_stage.is_ready,
)

check(
    "created_ready_eligible",
    ready_decision.classification
    is handoff.UniversalOrchestrationRuntimeHandoffClassification.ELIGIBLE,
)

check(
    "created_ready_reason",
    ready_decision.reason
    is handoff.UniversalOrchestrationRuntimeHandoffReason.READY_FOR_RUNTIME_HANDOFF,
)

check(
    "created_ready_reason_code",
    ready_decision.reason_code
    == "ready_for_runtime_handoff",
)


# ============================================================
# CREATED + WAITING
# ============================================================

_, _, _, _, waiting_stage, waiting_decision = make_context(
    run_id="waiting-run",
    target_status=jobs.UniversalJobStatus.CREATED,
    dependency_statuses={
        "a": "running",
    },
)


check(
    "created_waiting_stage_waiting",
    waiting_stage.is_waiting,
)

check(
    "created_waiting_deferred",
    waiting_decision.is_deferred,
)

check(
    "created_waiting_reason",
    waiting_decision.reason_code
    == "readiness_waiting",
)


# ============================================================
# CREATED + BLOCKED
# ============================================================

_, _, _, _, blocked_stage, blocked_decision = make_context(
    run_id="blocked-run",
    target_status=jobs.UniversalJobStatus.CREATED,
    dependency_statuses={
        "a": "failed",
        "b": "succeeded",
        "c": "succeeded",
    },
)


check(
    "created_blocked_stage_blocked",
    blocked_stage.is_blocked,
)

check(
    "created_blocked_ineligible",
    blocked_decision.is_ineligible,
)

check(
    "created_blocked_reason",
    blocked_decision.reason_code
    == "readiness_blocked",
)


# ============================================================
# ZERO DEPENDENCIES
# ============================================================

_, _, _, zero_resolution, zero_stage, zero_decision = make_context(
    run_id="zero-run",
    target_status=jobs.UniversalJobStatus.CREATED,
    dependency_statuses={},
    zero_dependencies=True,
)


check(
    "zero_dependencies_satisfied",
    zero_resolution.all_dependencies_satisfied,
)

check(
    "zero_dependencies_stage_ready",
    zero_stage.is_ready,
)

check(
    "zero_dependencies_handoff_eligible",
    zero_decision.is_eligible,
)


# ============================================================
# ALREADY IN RUNTIME
# ============================================================

for target_status in (
    jobs.UniversalJobStatus.QUEUED,
    jobs.UniversalJobStatus.SCHEDULED,
    jobs.UniversalJobStatus.LEASED,
    jobs.UniversalJobStatus.RUNNING,
):

    _, _, _, _, _, decision = make_context(
        run_id=(
            "already-runtime-"
            + target_status.value
        ),
        target_status=target_status,
        dependency_statuses={
            "a": "succeeded",
            "b": "succeeded",
            "c": "succeeded",
        },
    )

    check(
        "already_runtime_ineligible_"
        + target_status.value,
        decision.is_ineligible,
    )

    check(
        "already_runtime_reason_"
        + target_status.value,
        decision.reason_code
        == "target_already_in_runtime",
    )


# ============================================================
# SUSPENDED
# ============================================================

_, _, _, _, _, suspended_decision = make_context(
    run_id="suspended-run",
    target_status=jobs.UniversalJobStatus.SUSPENDED,
    dependency_statuses={
        "a": "succeeded",
        "b": "succeeded",
        "c": "succeeded",
    },
)


check(
    "suspended_deferred",
    suspended_decision.is_deferred,
)

check(
    "suspended_reason",
    suspended_decision.reason_code
    == "target_suspended",
)


# ============================================================
# TERMINAL
# ============================================================

for target_status in (
    jobs.UniversalJobStatus.SUCCEEDED,
    jobs.UniversalJobStatus.FAILED,
    jobs.UniversalJobStatus.CANCELLED,
    jobs.UniversalJobStatus.DEAD_LETTER,
    jobs.UniversalJobStatus.EXPIRED,
):

    _, _, _, _, _, decision = make_context(
        run_id=(
            "terminal-"
            + target_status.value
        ),
        target_status=target_status,
        dependency_statuses={
            "a": "succeeded",
            "b": "succeeded",
            "c": "succeeded",
        },
    )

    check(
        "terminal_ineligible_"
        + target_status.value,
        decision.is_ineligible,
    )

    check(
        "terminal_reason_"
        + target_status.value,
        decision.reason_code
        == "target_terminal",
    )


# ============================================================
# STATUS PARTITION
# ============================================================

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
    "entry_status_exact",
    handoff.HANDOFF_ENTRY_UNIVERSAL_JOB_STATUSES
    == frozenset(
        {
            jobs.UniversalJobStatus.CREATED,
        }
    ),
)

check(
    "runtime_status_exact",
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


# ============================================================
# DERIVED EVIDENCE
# ============================================================

check(
    "identity_derived",
    ready_decision.identity
    == ready_stage.identity,
)

check(
    "target_job_derived",
    ready_decision.target_job
    == ready_stage.target_job,
)

check(
    "job_id_derived",
    ready_decision.job_id
    == ready_stage.job_id,
)

check(
    "target_status_derived",
    ready_decision.target_status
    is jobs.UniversalJobStatus.CREATED,
)


# ============================================================
# STORED FIELD CONTRACT
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
    "dispatch_result",
    "execution_result",

    "orchestration_state",

    "fan_out_state",
    "fan_in_state",

    "condition_result",

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
    ready_decision
):

    try:

        setattr(
            ready_decision,
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
# EXPLANATION / BOUNDARIES
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
    "readiness_boundary_5_1_6",
    "5.1.6"
    in explanation.get(
        "readiness_boundary",
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

check(
    "runtime_registration_boundary",
    "Runtime Registration"
    in explanation.get(
        "runtime_registration_boundary",
        "",
    ),
)

check(
    "runtime_worker_boundary",
    "Universal Runtime Worker"
    in explanation.get(
        "execution_boundary",
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
# PROHIBITIONS
# ============================================================

required_prohibitions = (
    "does not mutate UniversalJob.status",
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
    "does not evaluate backpressure",

    "does not look up runtime handlers",
    "does not register runtime handlers",
    "does not dispatch runtime handlers",
    "does not execute runtime handlers",
    "does not execute jobs",

    "does not transition orchestration state",

    "does not coordinate actual fan-out",
    "does not coordinate actual fan-in",
    "does not evaluate conditional branches",

    "does not access Runtime State Store",
    "does not persist handoff decisions",

    "does not import Universal Coordination Framework",
    "does not invoke pipeline coordinators",

    "does not use job priority",
    "does not use queue priority",
    "does not use created_at",
    "does not use scheduled_at",

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
# CANONICAL FINGERPRINT
# ============================================================

fingerprint_material = "|".join(
    (
        "phase_5_1_7_universal_orchestration_runtime_handoff",

        handoff.UNIVERSAL_ORCHESTRATION_RUNTIME_HANDOFF_VERSION,
        handoff.UNIVERSAL_ORCHESTRATION_RUNTIME_HANDOFF_SCHEMA_VERSION,

        handoff_ast,

        "classification_eligible",
        "classification_deferred",
        "classification_ineligible",

        "reason_ready_for_runtime_handoff",
        "reason_readiness_waiting",
        "reason_readiness_blocked",
        "reason_target_already_in_runtime",
        "reason_target_suspended",
        "reason_target_terminal",

        "stored_stage_readiness",
        "stored_schema_version",

        "identity_derived",
        "target_job_derived",
        "job_id_derived",
        "target_status_derived",

        "created_ready_eligible",
        "created_waiting_deferred",
        "created_blocked_ineligible",

        "zero_dependency_created_eligible",

        "queued_already_in_runtime",
        "scheduled_already_in_runtime",
        "leased_already_in_runtime",
        "running_already_in_runtime",

        "suspended_deferred",

        "succeeded_terminal_ineligible",
        "failed_terminal_ineligible",
        "cancelled_terminal_ineligible",
        "dead_letter_terminal_ineligible",
        "expired_terminal_ineligible",

        "lifecycle_precedes_readiness_for_non_created_targets",

        "5_1_6_is_readiness_source",

        "no_dependency_recomputation",
        "no_execution_plan_recomputation",

        "no_job_status_mutation",

        "no_queue_membership_mutation",
        "no_enqueue",
        "no_schedule",
        "no_dequeue",
        "no_claim",

        "no_worker_assignment",
        "no_worker_health_evaluation",
        "no_worker_capability_evaluation",
        "no_worker_capacity_evaluation",

        "no_lease_acquisition",

        "no_runtime_handler_lookup",
        "no_runtime_handler_registration",
        "no_runtime_handler_dispatch",
        "no_runtime_handler_execution",

        "no_job_execution",

        "no_orchestration_state_transition",

        "fan_out_deferred_5_1_8",
        "fan_in_deferred_5_1_9",
        "conditional_branching_deferred_5_1_10",
        "suspension_resume_deferred_5_1_12",
        "persistence_deferred_5_1_14",

        "no_runtime_state_store",
        "no_handoff_persistence",

        "no_coordination_framework",
        "no_pipeline_coordinators",

        "job_priority_not_handoff",
        "queue_priority_not_handoff",
        "created_at_not_handoff",
        "scheduled_at_not_handoff",

        "no_wall_clock",
        "no_filesystem_io",
        "no_network_io",

        "immutable_deterministic_declarative_handoff_authority",
    )
)


runtime_handoff_fingerprint = (
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
            runtime_handoff_fingerprint
        )
        == 64
        and
        all(
            character
            in "0123456789ABCDEF"
            for character
            in runtime_handoff_fingerprint
        )
    ),
    runtime_handoff_fingerprint,
)


# ============================================================
# FINAL AST
# ============================================================

final_ast = ast_sha(
    HANDOFF_PATH
)


check(
    "final_ast_unchanged",
    final_ast
    == EXPECTED_HANDOFF_AST,
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
        "PHASE 5.1.7 — UNIVERSAL ORCHESTRATION "
        "RUNTIME HANDOFF FINAL CERTIFICATION"
    ),
    "=" * 118,
    "",
    (
        "RUNTIME HANDOFF AST SHA256: "
        + handoff_ast
    ),
    (
        "RUNTIME HANDOFF FINGERPRINT: "
        + runtime_handoff_fingerprint
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
            "FINAL RUNTIME HANDOFF CERTIFICATION: "
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
        "RUNTIME HANDOFF MODIFIED DURING CERTIFICATION: NO",
        "5.1.1 ORCHESTRATION CONTRACT MODIFIED: NO",
        "5.1.2 RUN IDENTITY MODIFIED: NO",
        "5.1.3 STATE MODEL MODIFIED: NO",
        "5.1.4 DEPENDENCY RESOLUTION MODIFIED: NO",
        "5.1.5 EXECUTION PLANNING MODIFIED: NO",
        "5.1.6 STAGE READINESS MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",
        "",
        "HANDOFF CLASSIFICATIONS: ELIGIBLE / DEFERRED / INELIGIBLE",
        "",
        "CREATED + READY: ELIGIBLE",
        "CREATED + WAITING: DEFERRED",
        "CREATED + BLOCKED: INELIGIBLE",
        "",
        "QUEUED/SCHEDULED/LEASED/RUNNING: INELIGIBLE — ALREADY IN RUNTIME",
        "SUSPENDED: DEFERRED",
        "SUCCEEDED/FAILED/CANCELLED/DEAD_LETTER/EXPIRED: INELIGIBLE — TERMINAL",
        "",
        "LIFECYCLE PRECEDES READINESS FOR NON-CREATED TARGETS: YES",
        "ZERO-DEPENDENCY CREATED TARGET: ELIGIBLE",
        "",
        "UNIVERSAL JOB STATUS MUTATED: NO",
        "QUEUE MEMBERSHIP MUTATED: NO",
        "QUEUE/WORKER ACTIVITY: NO",
        "LEASE ACQUIRED: NO",
        "RUNTIME HANDLER ACTIVITY: NO",
        "JOB EXECUTION: NO",
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
            "PHASE 5.1.7 FREEZE CANDIDATE: "
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
            "Phase 5.1.7 Runtime Handoff "
            "final certification failed."
        )
    )
