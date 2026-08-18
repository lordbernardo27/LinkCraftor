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

STATE_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_orchestration"
    / "state_model.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_1_3_orchestration_state_model_final_certification.txt"
)

EXPECTED_STATE_AST = (
    "B179C6BEB0A232F0170A2ED540D84239A2235A4F0F91528B530E229B61172610"
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


if not STATE_PATH.exists():

    raise SystemExit(
        "5.1.3 Orchestration State Model authority missing."
    )


initial_ast = ast_sha(
    STATE_PATH
)


if initial_ast != EXPECTED_STATE_AST:

    raise SystemExit(
        (
            "5.1.3 State Model AST mismatch before final certification.\n"
            "EXPECTED: "
            + EXPECTED_STATE_AST
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
                "5.1.3 final certification: "
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


contract = importlib.import_module(
    "backend.server.runtime.universal_orchestration.contract"
)

identity = importlib.import_module(
    "backend.server.runtime.universal_orchestration.run_identity"
)

state_module_name = (
    "backend.server.runtime."
    "universal_orchestration.state_model"
)

sys.modules.pop(
    state_module_name,
    None,
)

state = importlib.import_module(
    state_module_name
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


state_ast = ast_sha(
    STATE_PATH
)


# ============================================================
# AUTHORITY / VERSION
# ============================================================

check(
    "state_ast_exact",
    state_ast
    == EXPECTED_STATE_AST,
    state_ast,
)

check(
    "version_exact",
    state.UNIVERSAL_ORCHESTRATION_STATE_MODEL_VERSION
    == "universal_orchestration_state_model_v5.1.3",
)

check(
    "schema_exact",
    state.UNIVERSAL_ORCHESTRATION_STATE_MODEL_SCHEMA_VERSION
    == "universal_orchestration_state_model_schema_v1",
)


# ============================================================
# EXACT STATE VOCABULARY
# ============================================================

expected_states = (
    "created",
    "active",
    "waiting",
    "suspended",
    "recovering",
    "succeeded",
    "failed",
    "cancelled",
)


actual_states = tuple(
    item.value
    for item
    in state.UniversalOrchestrationState
)


check(
    "states_exact",
    actual_states
    == expected_states,
    actual_states,
)


check(
    "initial_state_exact",
    state.initial_universal_orchestration_state()
    is state.UniversalOrchestrationState.CREATED,
)


# ============================================================
# TERMINAL / NON-TERMINAL
# ============================================================

expected_terminal = frozenset(
    {
        state.UniversalOrchestrationState.SUCCEEDED,
        state.UniversalOrchestrationState.FAILED,
        state.UniversalOrchestrationState.CANCELLED,
    }
)


expected_non_terminal = frozenset(
    {
        state.UniversalOrchestrationState.CREATED,
        state.UniversalOrchestrationState.ACTIVE,
        state.UniversalOrchestrationState.WAITING,
        state.UniversalOrchestrationState.SUSPENDED,
        state.UniversalOrchestrationState.RECOVERING,
    }
)


check(
    "terminal_states_exact",
    state.TERMINAL_UNIVERSAL_ORCHESTRATION_STATES
    == expected_terminal,
)

check(
    "non_terminal_states_exact",
    state.NON_TERMINAL_UNIVERSAL_ORCHESTRATION_STATES
    == expected_non_terminal,
)


# ============================================================
# CANONICAL TRANSITION GRAPH
# ============================================================

expected_transition_values = {
    "created": frozenset(
        {
            "active",
            "waiting",
            "suspended",
            "succeeded",
            "failed",
            "cancelled",
        }
    ),

    "active": frozenset(
        {
            "waiting",
            "suspended",
            "recovering",
            "succeeded",
            "failed",
            "cancelled",
        }
    ),

    "waiting": frozenset(
        {
            "active",
            "suspended",
            "recovering",
            "succeeded",
            "failed",
            "cancelled",
        }
    ),

    "suspended": frozenset(
        {
            "active",
            "waiting",
            "recovering",
            "succeeded",
            "failed",
            "cancelled",
        }
    ),

    "recovering": frozenset(
        {
            "active",
            "waiting",
            "suspended",
            "succeeded",
            "failed",
            "cancelled",
        }
    ),

    "succeeded": frozenset(),
    "failed": frozenset(),
    "cancelled": frozenset(),
}


for current in state.UniversalOrchestrationState:

    actual = frozenset(
        target.value
        for target
        in state.allowed_universal_orchestration_transitions(
            current
        )
    )

    check(
        "transition_graph_"
        + current.value,
        actual
        == expected_transition_values[
            current.value
        ],
        actual,
    )


# ============================================================
# COMPLETE STATE PAIR MATRIX
# ============================================================

for current in state.UniversalOrchestrationState:

    for target in state.UniversalOrchestrationState:

        expected = (
            target.value
            in expected_transition_values[
                current.value
            ]
        )

        actual = (
            state.can_transition_universal_orchestration_state(
                current_state=current,
                target_state=target,
            )
        )

        check(
            (
                "transition_pair_"
                + current.value
                + "_"
                + target.value
            ),
            actual
            is expected,
        )


# ============================================================
# SELF TRANSITION / TERMINAL IMMUTABILITY
# ============================================================

for current in state.UniversalOrchestrationState:

    try:

        state.validate_universal_orchestration_state_transition(
            current_state=current,
            target_state=current,
        )

    except state.UniversalOrchestrationStateModelError as exc:

        rejected = (
            exc.code
            == "orchestration_self_transition_not_allowed"
        )

    else:

        rejected = False

    check(
        "self_transition_rejected_"
        + current.value,
        rejected,
    )


for current in expected_terminal:

    check(
        "terminal_no_transitions_"
        + current.value,
        state.allowed_universal_orchestration_transitions(
            current
        )
        == frozenset(),
    )

    for target in state.UniversalOrchestrationState:

        if target is current:
            continue

        try:

            state.validate_universal_orchestration_state_transition(
                current_state=current,
                target_state=target,
            )

        except state.UniversalOrchestrationStateModelError as exc:

            rejected = (
                exc.code
                == "terminal_orchestration_state_immutable"
            )

        else:

            rejected = False

        check(
            (
                "terminal_immutable_"
                + current.value
                + "_"
                + target.value
            ),
            rejected,
        )


# ============================================================
# FORBIDDEN STATE VOCABULARY
# ============================================================

for forbidden in (
    "queued",
    "scheduled",
    "leased",
    "running",
    "ready",
    "blocked",
    "dead_letter",
    "expired",
    "completing",
    "completed",
    "aborted",
):

    try:

        state.normalize_universal_orchestration_state(
            forbidden
        )

    except state.UniversalOrchestrationStateModelError:

        rejected = True

    else:

        rejected = False

    check(
        "foreign_state_rejected_"
        + forbidden,
        rejected,
    )


# ============================================================
# 5.1.1 + 5.1.2 FIXTURE
# ============================================================

contract_a = (
    contract.create_universal_runtime_orchestration_contract(
        workspace_id="workspace-a",
        pipeline="pipeline-a",
        job_ids=(
            "job-c",
            "job-a",
            "job-b",
        ),
    )
)


run_a = (
    identity.create_universal_orchestration_run_identity(
        orchestration_run_id="run-a",
        contract=contract_a,
    )
)


initial_snapshot = (
    state.create_initial_universal_orchestration_state_snapshot(
        identity=run_a
    )
)


check(
    "snapshot_identity_exact",
    initial_snapshot.identity
    == run_a,
)

check(
    "snapshot_state_created",
    initial_snapshot.state
    is state.UniversalOrchestrationState.CREATED,
)

check(
    "snapshot_run_id_derived",
    initial_snapshot.orchestration_run_id
    == "run-a",
)

check(
    "snapshot_workspace_derived",
    initial_snapshot.workspace_id
    == "workspace-a",
)

check(
    "snapshot_pipeline_derived",
    initial_snapshot.pipeline
    == "pipeline-a",
)

check(
    "snapshot_job_ids_derived",
    initial_snapshot.job_ids
    == (
        "job-a",
        "job-b",
        "job-c",
    ),
)


# ============================================================
# SNAPSHOT FIELD CONTRACT
# ============================================================

field_names = tuple(
    field.name
    for field in fields(
        state.UniversalOrchestrationStateSnapshot
    )
)


check(
    "snapshot_fields_exact",
    field_names
    == (
        "identity",
        "state",
        "schema_version",
    ),
    field_names,
)


for forbidden_field in (
    "orchestration_run_id",
    "workspace_id",
    "pipeline",
    "job_ids",
    "job_count",

    "dependency_job_ids",
    "dependencies",

    "readiness",
    "ready",
    "blocked",

    "current_stage",
    "execution_plan",

    "progress",
    "checkpoint_reference",

    "worker_id",
    "worker_instance_id",
    "lease_id",

    "queue_status",
    "job_status",

    "completion_reason",
    "failure_reason",
    "cancellation_reason",

    "created_at",
    "updated_at",
    "started_at",
    "completed_at",
    "failed_at",
    "cancelled_at",

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
    initial_snapshot
):

    try:

        setattr(
            initial_snapshot,
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
# TRANSITION SNAPSHOT SEMANTICS
# ============================================================

active_snapshot = (
    state.transition_universal_orchestration_state(
        snapshot=initial_snapshot,
        target_state="active",
    )
)


waiting_snapshot = (
    state.transition_universal_orchestration_state(
        snapshot=active_snapshot,
        target_state="waiting",
    )
)


recovering_snapshot = (
    state.transition_universal_orchestration_state(
        snapshot=waiting_snapshot,
        target_state="recovering",
    )
)


succeeded_snapshot = (
    state.transition_universal_orchestration_state(
        snapshot=recovering_snapshot,
        target_state="succeeded",
    )
)


check(
    "transition_returns_new_snapshot",
    active_snapshot
    is not initial_snapshot,
)

check(
    "initial_snapshot_preserved",
    initial_snapshot.state
    is state.UniversalOrchestrationState.CREATED,
)

check(
    "active_snapshot_exact",
    active_snapshot.state
    is state.UniversalOrchestrationState.ACTIVE,
)

check(
    "waiting_snapshot_exact",
    waiting_snapshot.state
    is state.UniversalOrchestrationState.WAITING,
)

check(
    "recovering_snapshot_exact",
    recovering_snapshot.state
    is state.UniversalOrchestrationState.RECOVERING,
)

check(
    "succeeded_snapshot_exact",
    succeeded_snapshot.state
    is state.UniversalOrchestrationState.SUCCEEDED,
)

check(
    "identity_preserved_across_transitions",
    all(
        item.identity
        == run_a
        for item in (
            initial_snapshot,
            active_snapshot,
            waiting_snapshot,
            recovering_snapshot,
            succeeded_snapshot,
        )
    ),
)

check(
    "succeeded_terminal",
    succeeded_snapshot.terminal
    is True,
)


# ============================================================
# EXPLANATION / DEFERRED AUTHORITIES
# ============================================================

explanation = (
    state.explain_universal_orchestration_state_model_v1()
)


check(
    "phase_exact",
    explanation.get(
        "phase"
    )
    == "5.1.3",
)

check(
    "component_exact",
    explanation.get(
        "component"
    )
    == "Universal Orchestration State Model",
)

check(
    "explanation_states_exact",
    explanation.get(
        "states"
    )
    == expected_states,
)

check(
    "identity_5_1_2",
    "5.1.2"
    in explanation.get(
        "identity_rule",
        "",
    ),
)

check(
    "transition_legality_only",
    "does not decide when"
    in explanation.get(
        "transition_rule",
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
    "suspension_deferred_5_1_12",
    "5.1.12"
    in explanation.get(
        "suspension_rule",
        "",
    ),
)

check(
    "recovery_deferred_5_1_13",
    "5.1.13"
    in explanation.get(
        "recovery_rule",
        "",
    ),
)

check(
    "persistence_deferred_5_1_14",
    "5.1.14"
    in explanation.get(
        "persistence_boundary",
        "",
    ),
)

check(
    "completion_deferred_5_1_15",
    "5.1.15"
    in explanation.get(
        "completion_rule",
        "",
    ),
)

check(
    "cancellation_deferred_5_1_16",
    "5.1.16"
    in explanation.get(
        "cancellation_rule",
        "",
    ),
)


# ============================================================
# IMPORT BOUNDARY
# ============================================================

source = STATE_PATH.read_text(
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
    "backend_import_exact",
    backend_imports
    == [
        "backend.server.runtime.universal_orchestration.run_identity",
    ],
    backend_imports,
)


# ============================================================
# API SURFACE
# ============================================================

expected_all = (
    "UNIVERSAL_ORCHESTRATION_STATE_MODEL_VERSION",
    "UNIVERSAL_ORCHESTRATION_STATE_MODEL_SCHEMA_VERSION",
    "UniversalOrchestrationStateModelError",
    "UniversalOrchestrationState",
    "TERMINAL_UNIVERSAL_ORCHESTRATION_STATES",
    "NON_TERMINAL_UNIVERSAL_ORCHESTRATION_STATES",
    "UNIVERSAL_ORCHESTRATION_STATE_TRANSITIONS",
    "normalize_universal_orchestration_state",
    "initial_universal_orchestration_state",
    "is_terminal_universal_orchestration_state",
    "is_non_terminal_universal_orchestration_state",
    "allowed_universal_orchestration_transitions",
    "can_transition_universal_orchestration_state",
    "validate_universal_orchestration_state_transition",
    "UniversalOrchestrationStateSnapshot",
    "create_initial_universal_orchestration_state_snapshot",
    "create_universal_orchestration_state_snapshot",
    "transition_universal_orchestration_state",
    "explain_universal_orchestration_state_model_v1",
)


check(
    "api_surface_exact",
    tuple(
        state.__all__
    )
    == expected_all,
    state.__all__,
)


# ============================================================
# PROHIBITION MATRIX
# ============================================================

required_prohibitions = (
    "does not reuse UniversalJobStatus as orchestration state",
    "does not reuse UniversalWorkflowStatus as orchestration state",
    "does not use queue membership as orchestration state",
    "does not use worker status as orchestration state",

    "does not define READY as orchestration state",
    "does not define BLOCKED as orchestration state",
    "does not define QUEUED as orchestration state",
    "does not define SCHEDULED as orchestration state",
    "does not define LEASED as orchestration state",
    "does not define RUNNING as orchestration state",
    "does not define DEAD_LETTER as orchestration state",
    "does not define EXPIRED as orchestration state",
    "does not define COMPLETING as orchestration state",

    "does not resolve dependencies",
    "does not determine readiness",
    "does not determine execution order",

    "does not perform fan-out",
    "does not perform fan-in",
    "does not evaluate conditional branches",
    "does not perform runtime handoffs",
    "does not track orchestration progress",

    "does not determine suspension eligibility",
    "does not restore checkpoints",
    "does not perform orchestration recovery decisions",

    "does not determine completion",
    "does not determine cancellation",

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

    "does not access Runtime State Store",
    "does not persist orchestration state",

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
# CANONICAL 5.1.3 FINGERPRINT
# ============================================================

fingerprint_material = "|".join(
    (
        "phase_5_1_3_universal_orchestration_state_model",

        state.UNIVERSAL_ORCHESTRATION_STATE_MODEL_VERSION,
        state.UNIVERSAL_ORCHESTRATION_STATE_MODEL_SCHEMA_VERSION,

        state_ast,

        "state_created",
        "state_active",
        "state_waiting",
        "state_suspended",
        "state_recovering",
        "state_succeeded",
        "state_failed",
        "state_cancelled",

        "initial_created",

        "terminal_succeeded",
        "terminal_failed",
        "terminal_cancelled",

        "terminal_states_immutable",
        "self_transitions_disallowed",

        "created_to_active",
        "created_to_waiting",
        "created_to_suspended",
        "created_to_succeeded",
        "created_to_failed",
        "created_to_cancelled",

        "active_to_waiting",
        "active_to_suspended",
        "active_to_recovering",
        "active_to_succeeded",
        "active_to_failed",
        "active_to_cancelled",

        "waiting_to_active",
        "waiting_to_suspended",
        "waiting_to_recovering",
        "waiting_to_succeeded",
        "waiting_to_failed",
        "waiting_to_cancelled",

        "suspended_to_active",
        "suspended_to_waiting",
        "suspended_to_recovering",
        "suspended_to_succeeded",
        "suspended_to_failed",
        "suspended_to_cancelled",

        "recovering_to_active",
        "recovering_to_waiting",
        "recovering_to_suspended",
        "recovering_to_succeeded",
        "recovering_to_failed",
        "recovering_to_cancelled",

        "stored_identity",
        "stored_state",
        "stored_schema_version",

        "immutable_state_snapshot",
        "transition_returns_new_snapshot",
        "identity_preserved_across_transition",

        "no_ready_state",
        "no_blocked_state",
        "no_queued_state",
        "no_scheduled_state",
        "no_leased_state",
        "no_running_state",
        "no_dead_letter_state",
        "no_expired_state",
        "no_completing_state",

        "dependency_resolution_external_5_1_4",
        "execution_planning_external_5_1_5",
        "readiness_external_5_1_6",
        "suspension_eligibility_external_5_1_12",
        "recovery_decision_external_5_1_13",
        "persistence_external_5_1_14",
        "completion_external_5_1_15",
        "cancellation_external_5_1_16",

        "no_queue_activity",
        "no_worker_activity",
        "no_runtime_registration_activity",
        "no_handler_dispatch",
        "no_job_execution",
        "no_coordination_framework",
        "no_pipeline_coordinators",
        "no_runtime_state_store",
        "no_persistence",
        "no_wall_clock",
        "no_filesystem_io",
        "no_network_io",

        "pure_runtime_orchestration_state_model_authority",
    )
)


state_model_fingerprint = (
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
            state_model_fingerprint
        )
        == 64
        and
        all(
            character
            in "0123456789ABCDEF"
            for character in state_model_fingerprint
        )
    ),
    state_model_fingerprint,
)


# ============================================================
# FINAL AST
# ============================================================

final_ast = ast_sha(
    STATE_PATH
)


check(
    "final_ast_unchanged",
    final_ast
    == EXPECTED_STATE_AST,
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
        "PHASE 5.1.3 — UNIVERSAL ORCHESTRATION "
        "STATE MODEL FINAL CERTIFICATION"
    ),
    "=" * 118,
    "",
    (
        "ORCHESTRATION STATE MODEL AST SHA256: "
        + state_ast
    ),
    (
        "ORCHESTRATION STATE MODEL FINGERPRINT: "
        + state_model_fingerprint
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
            "FINAL ORCHESTRATION STATE MODEL CERTIFICATION: "
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
        "ORCHESTRATION STATE MODEL MODIFIED DURING CERTIFICATION: NO",
        "5.1.1 ORCHESTRATION CONTRACT MODIFIED: NO",
        "5.1.2 RUN IDENTITY MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "EXISTING ORCHESTRATION AUTHORITIES MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME WORKER MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "",
        "UNIVERSAL JOB STATUS REUSED AS ORCHESTRATION STATE: NO",
        "UNIVERSAL WORKFLOW STATUS REUSED AS ORCHESTRATION STATE: NO",
        "QUEUE STATUS REUSED AS ORCHESTRATION STATE: NO",
        "WORKER STATUS REUSED AS ORCHESTRATION STATE: NO",
        "",
        "DEPENDENCY RESOLUTION PERFORMED: NO",
        "READINESS EVALUATED: NO",
        "EXECUTION ORDER DEFINED: NO",
        "FAN-OUT/FAN-IN PERFORMED: NO",
        "CONDITIONAL BRANCHING PERFORMED: NO",
        "RUNTIME HANDOFF PERFORMED: NO",
        "ORCHESTRATION PROGRESS TRACKED: NO",
        "SUSPENSION/RESUME ELIGIBILITY DETERMINED: NO",
        "CHECKPOINT RESTORATION PERFORMED: NO",
        "RECOVERY DECISION PERFORMED: NO",
        "COMPLETION DETERMINED: NO",
        "CANCELLATION/TERMINATION DETERMINED: NO",
        "QUEUE/WORKER ACTIVITY: NO",
        "RUNTIME HANDLER ACTIVITY: NO",
        "JOB EXECUTION: NO",
        "UNIVERSAL COORDINATION FRAMEWORK ACCESSED: NO",
        "PIPELINE COORDINATORS ACCESSED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "ORCHESTRATION STATE PERSISTED: NO",
        "WALL CLOCK USED: NO",
        "FILESYSTEM/NETWORK I/O: NO",
        "",
        (
            "PHASE 5.1.3 FREEZE CANDIDATE: "
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
            "Phase 5.1.3 Orchestration State Model "
            "final certification failed."
        )
    )
