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
    / "phase_5_1_3_orchestration_state_model_regression.txt"
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
            "5.1.3 State Model AST changed before regression.\n"
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
                "Protected authority changed before "
                "5.1.3 adversarial regression: "
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


# ============================================================
# 1 — AST / VERSION
# ============================================================

check(
    "state_ast_initial",
    ast_sha(
        STATE_PATH
    )
    == EXPECTED_STATE_AST,
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
# 2 — EXACT STATE VOCABULARY
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
    "state_vocabulary_exact",
    actual_states
    == expected_states,
    actual_states,
)


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
    "draining",
    "stopped",
):

    check(
        "forbidden_state_absent_"
        + forbidden,
        forbidden
        not in actual_states,
    )


# ============================================================
# 3 — INITIAL / TERMINAL SETS
# ============================================================

check(
    "initial_exact",
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
    "terminal_set_exact",
    state.TERMINAL_UNIVERSAL_ORCHESTRATION_STATES
    == expected_terminal,
)

check(
    "non_terminal_set_exact",
    state.NON_TERMINAL_UNIVERSAL_ORCHESTRATION_STATES
    == expected_non_terminal,
)

check(
    "terminal_nonterminal_disjoint",
    not (
        state.TERMINAL_UNIVERSAL_ORCHESTRATION_STATES
        &
        state.NON_TERMINAL_UNIVERSAL_ORCHESTRATION_STATES
    ),
)

check(
    "terminal_nonterminal_cover_all",
    (
        state.TERMINAL_UNIVERSAL_ORCHESTRATION_STATES
        |
        state.NON_TERMINAL_UNIVERSAL_ORCHESTRATION_STATES
    )
    == frozenset(
        state.UniversalOrchestrationState
    ),
)


# ============================================================
# 4 — STATE NORMALIZATION ATTACKS
# ============================================================

for raw, expected in (
    ("created", state.UniversalOrchestrationState.CREATED),
    ("CREATED", state.UniversalOrchestrationState.CREATED),
    (" Created ", state.UniversalOrchestrationState.CREATED),

    ("active", state.UniversalOrchestrationState.ACTIVE),
    ("ACTIVE", state.UniversalOrchestrationState.ACTIVE),

    ("waiting", state.UniversalOrchestrationState.WAITING),
    ("WAITING", state.UniversalOrchestrationState.WAITING),

    ("suspended", state.UniversalOrchestrationState.SUSPENDED),
    ("SUSPENDED", state.UniversalOrchestrationState.SUSPENDED),

    ("recovering", state.UniversalOrchestrationState.RECOVERING),
    ("RECOVERING", state.UniversalOrchestrationState.RECOVERING),

    ("succeeded", state.UniversalOrchestrationState.SUCCEEDED),
    ("SUCCEEDED", state.UniversalOrchestrationState.SUCCEEDED),

    ("failed", state.UniversalOrchestrationState.FAILED),
    ("FAILED", state.UniversalOrchestrationState.FAILED),

    ("cancelled", state.UniversalOrchestrationState.CANCELLED),
    ("CANCELLED", state.UniversalOrchestrationState.CANCELLED),
):

    check(
        "normalize_"
        + raw.strip().replace(" ", "_"),
        state.normalize_universal_orchestration_state(
            raw
        )
        is expected,
    )


invalid_states = (
    None,
    True,
    False,
    0,
    1,
    -1,
    1.0,
    b"active",
    bytearray(b"active"),
    "",
    " ",
    "\t",
    "\n",

    "queued",
    "scheduled",
    "leased",
    "running",

    "ready",
    "blocked",

    "dead_letter",
    "dead-letter",
    "expired",

    "completing",
    "completed",

    "paused",
    "resume",
    "resumed",

    "recover",
    "recovered",

    "abort",
    "aborted",

    "active now",
    "waiting state",

    [],
    {},
    (),
    set(),
    object(),
)


for index, bad in enumerate(
    invalid_states,
    start=1,
):

    try:

        state.normalize_universal_orchestration_state(
            bad
        )

    except state.UniversalOrchestrationStateModelError as exc:

        rejected = (
            exc.code
            == "invalid_orchestration_state"
        )

    else:

        rejected = False

    check(
        "invalid_state_attack_"
        + str(index),
        rejected,
        repr(bad),
    )


# ============================================================
# 5 — COMPLETE TRANSITION MATRIX
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
        item.value
        for item
        in state.allowed_universal_orchestration_transitions(
            current
        )
    )

    expected = (
        expected_transition_values[
            current.value
        ]
    )

    check(
        "transition_set_exact_"
        + current.value,
        actual
        == expected,
        actual,
    )


# ============================================================
# 6 — ALL 64 STATE PAIRS
# ============================================================

for current in state.UniversalOrchestrationState:

    for target in state.UniversalOrchestrationState:

        expected_allowed = (
            target.value
            in expected_transition_values[
                current.value
            ]
        )

        actual_allowed = (
            state.can_transition_universal_orchestration_state(
                current_state=current,
                target_state=target,
            )
        )

        check(
            (
                "pair_"
                + current.value
                + "_to_"
                + target.value
            ),
            actual_allowed
            is expected_allowed,
            (
                "expected="
                + repr(expected_allowed)
                + " actual="
                + repr(actual_allowed)
            ),
        )


# ============================================================
# 7 — SELF TRANSITIONS
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


# ============================================================
# 8 — TERMINAL IMMUTABILITY
# ============================================================

for current in expected_terminal:

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
                + "_to_"
                + target.value
            ),
            rejected,
        )


# ============================================================
# 9 — ALLOWED TRANSITIONS VALIDATE
# ============================================================

for current in expected_non_terminal:

    for target in state.UniversalOrchestrationState:

        expected_allowed = (
            target.value
            in expected_transition_values[
                current.value
            ]
        )

        if not expected_allowed:
            continue

        validated = (
            state.validate_universal_orchestration_state_transition(
                current_state=current,
                target_state=target,
            )
        )

        check(
            (
                "validate_allowed_"
                + current.value
                + "_to_"
                + target.value
            ),
            validated
            == (
                current,
                target,
            ),
            validated,
        )


# ============================================================
# 10 — FORBIDDEN NONTERMINAL TRANSITIONS
# ============================================================

for current in expected_non_terminal:

    for target in state.UniversalOrchestrationState:

        if current is target:
            continue

        if (
            target.value
            in expected_transition_values[
                current.value
            ]
        ):
            continue

        try:

            state.validate_universal_orchestration_state_transition(
                current_state=current,
                target_state=target,
            )

        except state.UniversalOrchestrationStateModelError as exc:

            rejected = (
                exc.code
                == "illegal_orchestration_state_transition"
            )

        else:

            rejected = False

        check(
            (
                "illegal_transition_"
                + current.value
                + "_to_"
                + target.value
            ),
            rejected,
        )


# ============================================================
# 11 — CONTRACT / IDENTITY FIXTURES
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


check(
    "contract_fixture_jobs_canonical",
    contract_a.job_ids
    == (
        "job-a",
        "job-b",
        "job-c",
    ),
)


# ============================================================
# 12 — SNAPSHOT IDENTITY TYPE ATTACKS
# ============================================================

invalid_identities = (
    None,
    True,
    False,
    0,
    1,
    1.0,
    "",
    "run-a",
    [],
    {},
    (),
    set(),
    object(),
)


for index, bad in enumerate(
    invalid_identities,
    start=1,
):

    try:

        state.create_initial_universal_orchestration_state_snapshot(
            identity=bad
        )

    except state.UniversalOrchestrationStateModelError as exc:

        rejected = (
            exc.code
            == "invalid_orchestration_state_identity"
        )

    else:

        rejected = False

    check(
        "invalid_identity_attack_"
        + str(index),
        rejected,
        repr(bad),
    )


# ============================================================
# 13 — SNAPSHOT STATE ATTACKS
# ============================================================

for index, bad_state in enumerate(
    invalid_states,
    start=1,
):

    try:

        state.create_universal_orchestration_state_snapshot(
            identity=run_a,
            state=bad_state,
        )

    except state.UniversalOrchestrationStateModelError:

        rejected = True

    else:

        rejected = False

    check(
        "snapshot_invalid_state_"
        + str(index),
        rejected,
    )


# ============================================================
# 14 — INITIAL SNAPSHOT EXACT
# ============================================================

initial = (
    state.create_initial_universal_orchestration_state_snapshot(
        identity=run_a
    )
)


check(
    "initial_snapshot_identity_exact",
    initial.identity
    == run_a,
)

check(
    "initial_snapshot_state_created",
    initial.state
    is state.UniversalOrchestrationState.CREATED,
)

check(
    "initial_snapshot_non_terminal",
    initial.non_terminal
    is True,
)

check(
    "initial_snapshot_terminal_false",
    initial.terminal
    is False,
)


# ============================================================
# 15 — DERIVED IDENTITY SURFACE
# ============================================================

check(
    "derived_run_id_exact",
    initial.orchestration_run_id
    == run_a.orchestration_run_id,
)

check(
    "derived_workspace_exact",
    initial.workspace_id
    == run_a.workspace_id,
)

check(
    "derived_pipeline_exact",
    initial.pipeline
    == run_a.pipeline,
)

check(
    "derived_jobs_exact",
    initial.job_ids
    == run_a.job_ids,
)


# ============================================================
# 16 — NEW SNAPSHOT PER TRANSITION
# ============================================================

active = (
    state.transition_universal_orchestration_state(
        snapshot=initial,
        target_state="active",
    )
)

waiting = (
    state.transition_universal_orchestration_state(
        snapshot=active,
        target_state="waiting",
    )
)

suspended = (
    state.transition_universal_orchestration_state(
        snapshot=waiting,
        target_state="suspended",
    )
)

recovering = (
    state.transition_universal_orchestration_state(
        snapshot=suspended,
        target_state="recovering",
    )
)

recovered_active = (
    state.transition_universal_orchestration_state(
        snapshot=recovering,
        target_state="active",
    )
)

succeeded = (
    state.transition_universal_orchestration_state(
        snapshot=recovered_active,
        target_state="succeeded",
    )
)


chain = (
    initial,
    active,
    waiting,
    suspended,
    recovering,
    recovered_active,
    succeeded,
)


check(
    "transition_chain_all_unique_objects",
    len(
        {
            id(item)
            for item in chain
        }
    )
    == len(chain),
)

check(
    "transition_chain_states_exact",
    tuple(
        item.state.value
        for item in chain
    )
    == (
        "created",
        "active",
        "waiting",
        "suspended",
        "recovering",
        "active",
        "succeeded",
    ),
)

check(
    "transition_chain_identity_preserved",
    all(
        item.identity
        == run_a
        for item in chain
    ),
)

check(
    "terminal_snapshot_terminal_true",
    succeeded.terminal
    is True,
)

check(
    "terminal_snapshot_nonterminal_false",
    succeeded.non_terminal
    is False,
)


# ============================================================
# 17 — ORIGINAL SNAPSHOTS NEVER MUTATED
# ============================================================

expected_chain_states = (
    "created",
    "active",
    "waiting",
    "suspended",
    "recovering",
    "active",
    "succeeded",
)


for index, (
    snapshot,
    expected_value,
) in enumerate(
    zip(
        chain,
        expected_chain_states,
    ),
    start=1,
):

    check(
        "snapshot_still_original_state_"
        + str(index),
        snapshot.state.value
        == expected_value,
    )


# ============================================================
# 18 — TERMINAL SNAPSHOT CANNOT REOPEN
# ============================================================

for terminal_state in (
    "succeeded",
    "failed",
    "cancelled",
):

    terminal_snapshot = (
        state.create_universal_orchestration_state_snapshot(
            identity=run_a,
            state=terminal_state,
        )
    )

    for target in (
        "created",
        "active",
        "waiting",
        "suspended",
        "recovering",
    ):

        try:

            state.transition_universal_orchestration_state(
                snapshot=terminal_snapshot,
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
                "terminal_snapshot_"
                + terminal_state
                + "_cannot_reopen_"
                + target
            ),
            rejected,
        )


# ============================================================
# 19 — SNAPSHOT TYPE SPOOFING
# ============================================================

for index, bad_snapshot in enumerate(
    (
        None,
        True,
        False,
        0,
        "",
        [],
        {},
        (),
        run_a,
        contract_a,
        object(),
    ),
    start=1,
):

    try:

        state.transition_universal_orchestration_state(
            snapshot=bad_snapshot,
            target_state="active",
        )

    except state.UniversalOrchestrationStateModelError as exc:

        rejected = (
            exc.code
            == "invalid_orchestration_state_snapshot"
        )

    else:

        rejected = False

    check(
        "snapshot_spoof_attack_"
        + str(index),
        rejected,
    )


# ============================================================
# 20 — EXACT STORED FIELDS
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
        "forbidden_stored_field_"
        + forbidden_field,
        forbidden_field
        not in field_names,
    )


# ============================================================
# 21 — IMMUTABILITY
# ============================================================

for field in fields(
    initial
):

    try:

        setattr(
            initial,
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
# 22 — SCHEMA FORGERY
# ============================================================

for bad_schema in (
    "",
    " ",
    "v1",
    "wrong",
    "universal_orchestration_state_model_schema_v2",
):

    try:

        state.UniversalOrchestrationStateSnapshot(
            identity=run_a,
            state="created",
            schema_version=bad_schema,
        )

    except state.UniversalOrchestrationStateModelError as exc:

        rejected = (
            exc.code
            == "invalid_orchestration_state_schema_version"
        )

    else:

        rejected = False

    check(
        "schema_attack_"
        + repr(bad_schema),
        rejected,
    )


# ============================================================
# 23 — ALLOWED TRANSITIONS ARE IMMUTABLE
# ============================================================

for current in state.UniversalOrchestrationState:

    allowed = (
        state.allowed_universal_orchestration_transitions(
            current
        )
    )

    check(
        "allowed_transition_type_frozenset_"
        + current.value,
        isinstance(
            allowed,
            frozenset,
        ),
    )

    try:

        allowed.add(
            state.UniversalOrchestrationState.CREATED
        )

    except Exception:

        immutable = True

    else:

        immutable = False

    check(
        "allowed_transition_immutable_"
        + current.value,
        immutable,
    )


try:

    state.UNIVERSAL_ORCHESTRATION_STATE_TRANSITIONS[
        state.UniversalOrchestrationState.CREATED
    ] = frozenset()

except Exception:

    transition_map_immutable = True

else:

    transition_map_immutable = False


check(
    "transition_map_immutable",
    transition_map_immutable,
)


# ============================================================
# 24 — STATE SET IMMUTABILITY
# ============================================================

for name, value in (
    (
        "terminal",
        state.TERMINAL_UNIVERSAL_ORCHESTRATION_STATES,
    ),
    (
        "non_terminal",
        state.NON_TERMINAL_UNIVERSAL_ORCHESTRATION_STATES,
    ),
):

    try:

        value.add(
            state.UniversalOrchestrationState.CREATED
        )

    except Exception:

        immutable = True

    else:

        immutable = False

    check(
        name
        + "_state_set_immutable",
        immutable,
    )


# ============================================================
# 25 — EXPLANATION BOUNDARIES
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
    "states_explanation_exact",
    explanation.get(
        "states"
    )
    == expected_states,
)

check(
    "initial_explanation_created",
    explanation.get(
        "initial_state"
    )
    == "created",
)

check(
    "terminal_explanation_exact",
    set(
        explanation.get(
            "terminal_states",
            (),
        )
    )
    == {
        "succeeded",
        "failed",
        "cancelled",
    },
)

check(
    "identity_boundary_5_1_2",
    "5.1.2"
    in explanation.get(
        "identity_rule",
        "",
    ),
)

check(
    "transition_legality_not_decision",
    "does not decide when"
    in explanation.get(
        "transition_rule",
        "",
    ),
)

check(
    "self_transition_rule",
    "not legal"
    in explanation.get(
        "self_transition_rule",
        "",
    ),
)

check(
    "terminal_rule",
    "cannot transition"
    in explanation.get(
        "terminal_rule",
        "",
    ),
)

check(
    "waiting_not_dependency_resolution",
    "does not itself resolve dependencies"
    in explanation.get(
        "waiting_rule",
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

check(
    "readiness_deferred_5_1_6",
    "5.1.6"
    in explanation.get(
        "readiness_boundary",
        "",
    ),
)


# ============================================================
# 26 — PROHIBITION MATRIX
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
# 27 — IMPORT BOUNDARY
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
# 28 — FORBIDDEN IMPORTS
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

    "backend.server.runtime.universal_jobs",
    "backend.server.runtime.universal_queue",
    "backend.server.runtime.universal_worker",
    "backend.server.runtime.universal_runtime_registration",
    "backend.server.runtime.runtime_state_store",

    "backend.server.orchestration",
    "backend.server.coordination",

    "backend.server.jobs.universal_knowledge_orchestrator",
    "backend.server.pipelines.connect_domain.coordinator",
):

    matches = tuple(
        module
        for module in all_imports
        if (
            module
            == forbidden_module
            or
            module.startswith(
                forbidden_module
                + "."
            )
        )
    )

    check(
        "no_forbidden_import_"
        + forbidden_module.replace(
            ".",
            "_"
        ),
        not matches,
        matches,
    )


# ============================================================
# 29 — API SURFACE
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
# 30 — FORBIDDEN CALLS
# ============================================================

forbidden_calls = {
    "open",
    "read_text",
    "write_text",
    "mkdir",
    "unlink",
    "remove",

    "time",
    "time_ns",
    "now",
    "utcnow",

    "uuid4",
    "uuid5",
    "random",
    "randint",
    "choice",

    "enqueue_job",
    "dequeue_job",
    "claim_job",

    "assign_universal_worker",
    "discover_universal_workers",

    "acquire_universal_worker_lease",
    "renew_universal_worker_lease",
    "release_universal_worker_lease",

    "register_runtime_handler",
    "unregister_runtime_handler",
    "dispatch_registered_runtime_handler",
    "execute_registered_runtime_job_v1",

    "get_runtime_state_store_registry",
    "register_runtime_state_store",

    "persist",
    "save",
    "dispatch",
    "execute",
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
# 31 — NO RESPONSIBILITY BLEED
# ============================================================

function_names = tuple(
    node.name.lower()
    for node in ast.walk(
        tree
    )
    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ),
    )
)


for forbidden_token in (
    "dependency_resol",
    "readiness",
    "execution_plan",

    "fan_out",
    "fan_in",
    "branch",
    "handoff",
    "progress",

    "resume_eligib",
    "checkpoint",
    "recover_decision",

    "completion_resol",
    "cancel_resol",

    "enqueue",
    "claim",
    "assign",
    "lease",

    "register_runtime",
    "dispatch",
    "execute",

    "persist",
):

    matches = tuple(
        name
        for name in function_names
        if forbidden_token
        in name
    )

    check(
        "no_function_bleed_"
        + forbidden_token,
        not matches,
        matches,
    )


# ============================================================
# 32 — NO HIDDEN POLICY FIELDS
# ============================================================

source_lower = source.lower()


for forbidden_symbol in (
    "dependency_job_ids:",
    "dependencies:",

    "readiness:",
    "ready:",
    "blocked:",

    "current_stage:",
    "execution_plan:",

    "progress:",
    "checkpoint_reference:",

    "worker_id:",
    "worker_instance_id:",
    "lease_id:",

    "queue_status:",
    "job_status:",

    "completion_reason:",
    "failure_reason:",
    "cancellation_reason:",

    "created_at:",
    "updated_at:",
    "started_at:",
    "completed_at:",
    "failed_at:",
    "cancelled_at:",

    "metadata:",
):

    check(
        "no_hidden_field_"
        + forbidden_symbol.replace(
            ":",
            ""
        ),
        forbidden_symbol
        not in source_lower,
    )


# ============================================================
# 33 — NO STATE DECISION EVIDENCE
# ============================================================

forbidden_policy_words = (
    "all_dependencies_satisfied",
    "dependency_satisfied",
    "ready_to_execute",
    "execution_ready",
    "worker_available",
    "queue_available",
    "completion_evidence",
    "cancellation_evidence",
    "failure_evidence",
    "resume_eligible",
    "recovery_required",
)


for word in forbidden_policy_words:

    check(
        "no_policy_symbol_"
        + word,
        word
        not in source_lower,
    )


# ============================================================
# 34 — PROTECTED MATRIX
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
# 35 — FINAL AST
# ============================================================

final_ast = ast_sha(
    STATE_PATH
)


check(
    "state_ast_final",
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
        "PHASE 5.1.3 — UNIVERSAL ORCHESTRATION "
        "STATE MODEL ADVERSARIAL REGRESSION"
    ),
    "=" * 118,
    "",
    (
        "ORCHESTRATION STATE MODEL AST SHA256: "
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
            "ADVERSARIAL ORCHESTRATION STATE MODEL REGRESSION: "
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
        "ORCHESTRATION STATE MODEL AST MODIFIED: NO",
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
            "STATUS: REGRESSION PASS "
            "— FINAL CERTIFICATION REQUIRED"
            if passed == total
            else
            "STATUS: REGRESSION FAILED "
            "— PATCH REQUIRED BEFORE CERTIFICATION"
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
            "adversarial regression failed."
        )
    )
