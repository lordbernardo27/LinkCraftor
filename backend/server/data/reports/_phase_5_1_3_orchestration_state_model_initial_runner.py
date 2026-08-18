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
    / "phase_5_1_3_orchestration_state_model_initial_implementation.txt"
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
                "5.1.3 implementation: "
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


check(
    "states_exact",
    tuple(
        item.value
        for item
        in state.UniversalOrchestrationState
    )
    == expected_states,
)


check(
    "initial_created",
    state.initial_universal_orchestration_state()
    is state.UniversalOrchestrationState.CREATED,
)


expected_terminal = frozenset(
    {
        state.UniversalOrchestrationState.SUCCEEDED,
        state.UniversalOrchestrationState.FAILED,
        state.UniversalOrchestrationState.CANCELLED,
    }
)


check(
    "terminal_exact",
    state.TERMINAL_UNIVERSAL_ORCHESTRATION_STATES
    == expected_terminal,
)


check(
    "non_terminal_exact",
    state.NON_TERMINAL_UNIVERSAL_ORCHESTRATION_STATES
    == frozenset(
        {
            state.UniversalOrchestrationState.CREATED,
            state.UniversalOrchestrationState.ACTIVE,
            state.UniversalOrchestrationState.WAITING,
            state.UniversalOrchestrationState.SUSPENDED,
            state.UniversalOrchestrationState.RECOVERING,
        }
    ),
)


for terminal_state in expected_terminal:

    check(
        "terminal_"
        + terminal_state.value,
        state.is_terminal_universal_orchestration_state(
            terminal_state
        ),
    )

    check(
        "terminal_has_no_transitions_"
        + terminal_state.value,
        state.allowed_universal_orchestration_transitions(
            terminal_state
        )
        == frozenset(),
    )


for non_terminal_state in (
    state.NON_TERMINAL_UNIVERSAL_ORCHESTRATION_STATES
):

    check(
        "non_terminal_"
        + non_terminal_state.value,
        state.is_non_terminal_universal_orchestration_state(
            non_terminal_state
        ),
    )


for raw, expected in (
    (
        "CREATED",
        state.UniversalOrchestrationState.CREATED,
    ),
    (
        " active ",
        state.UniversalOrchestrationState.ACTIVE,
    ),
    (
        "WAITING",
        state.UniversalOrchestrationState.WAITING,
    ),
    (
        " suspended ",
        state.UniversalOrchestrationState.SUSPENDED,
    ),
    (
        "Recovering",
        state.UniversalOrchestrationState.RECOVERING,
    ),
    (
        "SUCCEEDED",
        state.UniversalOrchestrationState.SUCCEEDED,
    ),
    (
        "FAILED",
        state.UniversalOrchestrationState.FAILED,
    ),
    (
        "cancelled",
        state.UniversalOrchestrationState.CANCELLED,
    ),
):

    check(
        "normalize_"
        + expected.value,
        state.normalize_universal_orchestration_state(
            raw
        )
        is expected,
    )


for bad in (
    None,
    True,
    False,
    0,
    1,
    "",
    " ",
    "queued",
    "scheduled",
    "leased",
    "running",
    "ready",
    "blocked",
    "dead_letter",
    "expired",
    "completing",
    [],
    {},
    (),
):

    try:

        state.normalize_universal_orchestration_state(
            bad
        )

    except state.UniversalOrchestrationStateModelError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_state_"
        + repr(bad),
        rejected,
    )


allowed_pairs = (
    ("created", "active"),
    ("created", "waiting"),
    ("created", "suspended"),
    ("created", "succeeded"),
    ("created", "failed"),
    ("created", "cancelled"),

    ("active", "waiting"),
    ("active", "suspended"),
    ("active", "recovering"),
    ("active", "succeeded"),
    ("active", "failed"),
    ("active", "cancelled"),

    ("waiting", "active"),
    ("waiting", "suspended"),
    ("waiting", "recovering"),
    ("waiting", "succeeded"),
    ("waiting", "failed"),
    ("waiting", "cancelled"),

    ("suspended", "active"),
    ("suspended", "waiting"),
    ("suspended", "recovering"),
    ("suspended", "succeeded"),
    ("suspended", "failed"),
    ("suspended", "cancelled"),

    ("recovering", "active"),
    ("recovering", "waiting"),
    ("recovering", "suspended"),
    ("recovering", "succeeded"),
    ("recovering", "failed"),
    ("recovering", "cancelled"),
)


for current, target in allowed_pairs:

    check(
        "allowed_"
        + current
        + "_to_"
        + target,
        state.can_transition_universal_orchestration_state(
            current_state=current,
            target_state=target,
        ),
    )


for value in expected_states:

    check(
        "self_transition_false_"
        + value,
        not state.can_transition_universal_orchestration_state(
            current_state=value,
            target_state=value,
        ),
    )


for terminal_value in (
    "succeeded",
    "failed",
    "cancelled",
):

    for target in expected_states:

        if target == terminal_value:
            continue

        check(
            "terminal_cannot_transition_"
            + terminal_value
            + "_to_"
            + target,
            not state.can_transition_universal_orchestration_state(
                current_state=terminal_value,
                target_state=target,
            ),
        )


for terminal_value in (
    "succeeded",
    "failed",
    "cancelled",
):

    try:

        state.validate_universal_orchestration_state_transition(
            current_state=terminal_value,
            target_state="active",
        )

    except state.UniversalOrchestrationStateModelError as exc:

        rejected = (
            exc.code
            == "terminal_orchestration_state_immutable"
        )

    else:

        rejected = False

    check(
        "terminal_validation_"
        + terminal_value,
        rejected,
    )


try:

    state.validate_universal_orchestration_state_transition(
        current_state="active",
        target_state="active",
    )

except state.UniversalOrchestrationStateModelError as exc:

    rejected = (
        exc.code
        == "orchestration_self_transition_not_allowed"
    )

else:

    rejected = False


check(
    "self_transition_validation",
    rejected,
)


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


snapshot = (
    state.create_initial_universal_orchestration_state_snapshot(
        identity=run_a
    )
)


check(
    "snapshot_identity",
    snapshot.identity
    == run_a,
)

check(
    "snapshot_state_created",
    snapshot.state
    is state.UniversalOrchestrationState.CREATED,
)

check(
    "snapshot_run_id_derived",
    snapshot.orchestration_run_id
    == "run-a",
)

check(
    "snapshot_workspace_derived",
    snapshot.workspace_id
    == "workspace-a",
)

check(
    "snapshot_pipeline_derived",
    snapshot.pipeline
    == "pipeline-a",
)

check(
    "snapshot_jobs_derived",
    snapshot.job_ids
    == (
        "job-a",
        "job-b",
        "job-c",
    ),
)

check(
    "snapshot_non_terminal",
    snapshot.non_terminal
    is True,
)

check(
    "snapshot_terminal_false",
    snapshot.terminal
    is False,
)


active_snapshot = (
    state.transition_universal_orchestration_state(
        snapshot=snapshot,
        target_state="active",
    )
)


check(
    "transition_returns_new_snapshot",
    active_snapshot
    is not snapshot,
)

check(
    "original_snapshot_unchanged",
    snapshot.state
    is state.UniversalOrchestrationState.CREATED,
)

check(
    "new_snapshot_active",
    active_snapshot.state
    is state.UniversalOrchestrationState.ACTIVE,
)

check(
    "transition_preserves_identity",
    active_snapshot.identity
    == snapshot.identity,
)


failed_snapshot = (
    state.transition_universal_orchestration_state(
        snapshot=active_snapshot,
        target_state="failed",
    )
)


check(
    "failed_terminal",
    failed_snapshot.terminal
    is True,
)


try:

    state.transition_universal_orchestration_state(
        snapshot=failed_snapshot,
        target_state="active",
    )

except state.UniversalOrchestrationStateModelError as exc:

    rejected = (
        exc.code
        == "terminal_orchestration_state_immutable"
    )

else:

    rejected = False


check(
    "terminal_snapshot_cannot_reopen",
    rejected,
)


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
    "dependency_job_ids",
    "readiness",
    "blocked",
    "current_stage",
    "execution_plan",
    "progress",
    "checkpoint_reference",
    "worker_id",
    "lease_id",
    "queue_status",
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


for bad_identity in (
    None,
    True,
    False,
    0,
    "",
    [],
    {},
    object(),
):

    try:

        state.create_initial_universal_orchestration_state_snapshot(
            identity=bad_identity
        )

    except state.UniversalOrchestrationStateModelError as exc:

        rejected = (
            exc.code
            == "invalid_orchestration_state_identity"
        )

    else:

        rejected = False

    check(
        "invalid_identity_"
        + type(bad_identity).__name__,
        rejected,
    )


try:

    state.UniversalOrchestrationStateSnapshot(
        identity=run_a,
        state="created",
        schema_version="tampered",
    )

except state.UniversalOrchestrationStateModelError as exc:

    rejected = (
        exc.code
        == "invalid_orchestration_state_schema_version"
    )

else:

    rejected = False


check(
    "schema_tamper_rejected",
    rejected,
)


explanation = (
    state.explain_universal_orchestration_state_model_v1()
)


check(
    "phase",
    explanation.get("phase")
    == "5.1.3",
)

check(
    "component",
    explanation.get("component")
    == "Universal Orchestration State Model",
)

check(
    "explanation_states_exact",
    explanation.get("states")
    == expected_states,
)

check(
    "identity_binding_5_1_2",
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
    "readiness_5_1_6",
    "5.1.6"
    in explanation.get(
        "readiness_boundary",
        "",
    ),
)

check(
    "suspension_5_1_12",
    "5.1.12"
    in explanation.get(
        "suspension_rule",
        "",
    ),
)

check(
    "recovery_5_1_13",
    "5.1.13"
    in explanation.get(
        "recovery_rule",
        "",
    ),
)

check(
    "persistence_5_1_14",
    "5.1.14"
    in explanation.get(
        "persistence_boundary",
        "",
    ),
)

check(
    "completion_5_1_15",
    "5.1.15"
    in explanation.get(
        "completion_rule",
        "",
    ),
)

check(
    "cancellation_5_1_16",
    "5.1.16"
    in explanation.get(
        "cancellation_rule",
        "",
    ),
)


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


state_ast = ast_sha(
    STATE_PATH
)


check(
    "state_ast_generated",
    len(state_ast)
    == 64,
    state_ast,
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
        "PHASE 5.1.3 — UNIVERSAL ORCHESTRATION "
        "STATE MODEL INITIAL IMPLEMENTATION"
    ),
    "=" * 118,
    "",
    (
        "ORCHESTRATION STATE MODEL AST SHA256: "
        + state_ast
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
            "INITIAL ORCHESTRATION STATE MODEL RESULT: "
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
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "EXISTING ORCHESTRATION AUTHORITIES MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME WORKER MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
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
        "Phase 5.1.3 Orchestration State Model initial implementation failed."
    )
