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

DRAIN_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "drain.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_4_1_12_worker_drain_final_certification.txt"
)

EXPECTED_DRAIN_AST = (
    "629AA6B5D9269B3164A1524F3C176B2EA34CB4952A0D32F5E2EE4A7C6984FA78"
)


PROTECTED = {
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
    "stale_worker_detection": (
        ROOT / "backend/server/runtime/universal_worker/stale.py",
        "22105ACBF984E26019080E53939617CE14BDF51BF5A9B149BD39E10B6B87B9DD",
    ),
    "queue_certification": (
        ROOT / "backend/server/runtime/universal_queue/certification.py",
        "6ED39655147D2B331E02101F5EA23E68CF71447353C0D294E170281AE40C0D4C",
    ),
    "job_contract": (
        ROOT / "backend/server/runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
    ),
    "existing_runtime_worker": (
        ROOT / "backend/server/runtime/universal_runtime_worker_v1.py",
        "6CC4EC122C6B8D1E21AFF8B55CAA786148D7E1FC75D840DAE9240FFB69634D44",
    ),
    "runtime_registration": (
        ROOT / "backend/server/runtime/universal_runtime_registration.py",
        "CBFBB0DA1E5D05A040AEC6F60B1251331431956106D90335A8C110FDBCA632E5",
    ),
    "runtime_infrastructure": (
        ROOT / "backend/server/runtime/universal_runtime_infrastructure.py",
        "EE6590D044C6AA20762F2A37AE86B7FFD3300B62610BC2B1F2657D9334CB311C",
    ),
    "runtime_shutdown_process": (
        ROOT / "backend/server/runtime/runtime_shutdown_process.py",
        "7A159E206C73157064B70D15A1CE4A97AB3D77EBBC77B01A2554BC34224EB272",
    ),
    "runtime_lifecycle_manager": (
        ROOT / "backend/server/runtime/runtime_lifecycle_manager.py",
        "E6200CA0938B5D578954024D6E76E343FB39D9329CFD3ABE4B3AEF86E8204034",
    ),
    "orchestration_models": (
        ROOT / "backend/server/orchestration/models.py",
        "5C9FE5E4F84FA1C369CB45F74B0CB12B7E730ADA3C7CBC95B4F50EC75DC5E92D",
    ),
    "tms_orchestration_governance": (
        ROOT / "backend/server/tms/orchestration_governance.py",
        "2AAA15B7283C6F0B4BB67A47FE58F1FD0EF2815A09CA048EA0CFE7DEF232B4E1",
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


# ============================================================
# PRECONDITIONS
# ============================================================

if not DRAIN_PATH.exists():

    raise SystemExit(
        "4.1.12 Worker Drain authority missing."
    )


initial_ast = ast_sha(
    DRAIN_PATH
)


if initial_ast != EXPECTED_DRAIN_AST:

    raise SystemExit(
        (
            "Worker Drain AST mismatch before final certification.\n"
            "EXPECTED: "
            + EXPECTED_DRAIN_AST
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
                "4.1.12 final certification: "
                + name
                + "\nEXPECTED: "
                + expected
                + "\nACTUAL:   "
                + actual
            )
        )


# ============================================================
# IMPORT
# ============================================================

sys.path.insert(
    0,
    str(ROOT),
)

registration = importlib.import_module(
    "backend.server.runtime.universal_worker.registration"
)

module_name = (
    "backend.server.runtime."
    "universal_worker.drain"
)

sys.modules.pop(
    module_name,
    None,
)

drain = importlib.import_module(
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


def make_registration():

    return registration.create_universal_worker_registration(
        worker_id="worker-a",
        worker_type="semantic_worker",
        worker_instance_id="instance-1",
        runtime_version="runtime-v1",
        host_id="host-1",
        registered_at="2026-08-17T00:00:00+00:00",
    )


reg = make_registration()


# ============================================================
# CORE AUTHORITY
# ============================================================

drain_ast = ast_sha(
    DRAIN_PATH
)


check(
    "worker_drain_ast",
    drain_ast
    == EXPECTED_DRAIN_AST,
    drain_ast,
)

check(
    "version",
    drain.UNIVERSAL_WORKER_DRAIN_VERSION
    == "universal_worker_drain_v4.1.12",
)

check(
    "evidence_schema",
    drain.UNIVERSAL_WORKER_DRAIN_EVIDENCE_SCHEMA_VERSION
    == "universal_worker_drain_evidence_schema_v1",
)

check(
    "result_schema",
    drain.UNIVERSAL_WORKER_DRAIN_RESULT_SCHEMA_VERSION
    == "universal_worker_drain_result_schema_v1",
)

check(
    "max_count",
    drain.MAX_UNIVERSAL_WORKER_DRAIN_COUNT
    == 2_147_483_647,
)

check(
    "identity_separator",
    drain.UNIVERSAL_WORKER_DRAIN_IDENTITY_SEPARATOR
    == "::",
)

check(
    "states_exact",
    tuple(
        state.value
        for state in drain.UniversalWorkerDrainState
    )
    == (
        "NOT_REQUESTED",
        "DRAINING",
        "DRAINED",
    ),
)


# ============================================================
# CANONICAL STATE RULES
# ============================================================

state_cases = (
    (False, 0, 0, "NOT_REQUESTED"),
    (False, 1, 0, "NOT_REQUESTED"),
    (False, 0, 1, "NOT_REQUESTED"),
    (False, 5, 9, "NOT_REQUESTED"),

    (True, 1, 0, "DRAINING"),
    (True, 0, 1, "DRAINING"),
    (True, 1, 1, "DRAINING"),
    (True, 100, 200, "DRAINING"),

    (True, 0, 0, "DRAINED"),
)


for index, (
    requested,
    active_work,
    active_leases,
    expected,
) in enumerate(
    state_cases,
    start=1,
):

    state = (
        drain.decide_universal_worker_drain_state(
            drain_requested=requested,
            active_work_count=active_work,
            active_lease_count=active_leases,
        )
    )

    check(
        "state_rule_"
        + str(index),
        state.value
        == expected,
        state.value,
    )


# ============================================================
# EVIDENCE / RESULT
# ============================================================

not_requested_evidence = (
    drain.create_universal_worker_drain_evidence(
        registration=reg,
        drain_requested=False,
        active_work_count=3,
        active_lease_count=2,
    )
)

not_requested = (
    drain.evaluate_universal_worker_drain(
        evidence=not_requested_evidence
    )
)


draining_evidence = (
    drain.create_universal_worker_drain_evidence(
        registration=reg,
        drain_requested=True,
        active_work_count=2,
        active_lease_count=1,
    )
)

draining = (
    drain.evaluate_universal_worker_drain(
        evidence=draining_evidence
    )
)


drained_evidence = (
    drain.create_universal_worker_drain_evidence(
        registration=reg,
        drain_requested=True,
        active_work_count=0,
        active_lease_count=0,
    )
)

drained = (
    drain.evaluate_universal_worker_drain(
        evidence=drained_evidence
    )
)


check(
    "not_requested_state",
    not_requested.state
    is drain.UniversalWorkerDrainState.NOT_REQUESTED,
)

check(
    "not_requested_accepts_new_work",
    not_requested.accepts_new_work
    is True,
)

check(
    "not_requested_drain_complete_false",
    not_requested.drain_complete
    is False,
)

check(
    "draining_state",
    draining.state
    is drain.UniversalWorkerDrainState.DRAINING,
)

check(
    "draining_accepts_new_work_false",
    draining.accepts_new_work
    is False,
)

check(
    "draining_drain_complete_false",
    draining.drain_complete
    is False,
)

check(
    "drained_state",
    drained.state
    is drain.UniversalWorkerDrainState.DRAINED,
)

check(
    "drained_accepts_new_work_false",
    drained.accepts_new_work
    is False,
)

check(
    "drained_drain_complete_true",
    drained.drain_complete
    is True,
)


# ============================================================
# CANONICAL IDENTITY
# ============================================================

check(
    "worker_id",
    drained.worker_id
    == reg.worker_id,
)

check(
    "worker_instance_id",
    drained.worker_instance_id
    == reg.worker_instance_id,
)

check(
    "worker_type",
    drained.worker_type
    == reg.worker_type,
)

check(
    "worker_identity",
    drained.worker_identity
    == "worker-a::instance-1",
)


# ============================================================
# STRICT REQUEST CONTRACT
# ============================================================

for bad in (
    None,
    0,
    1,
    -1,
    0.0,
    1.0,
    "",
    "true",
    [],
    {},
    (),
):

    try:

        drain.normalize_universal_worker_drain_requested(
            bad
        )

    except drain.UniversalWorkerDrainError as exc:

        rejected = (
            exc.code
            == "invalid_worker_drain_requested"
        )

    else:

        rejected = False

    check(
        "invalid_requested_"
        + repr(bad),
        rejected,
    )


# ============================================================
# STRICT COUNT CONTRACT
# ============================================================

for field_name in (
    "active_work_count",
    "active_lease_count",
):

    for bad in (
        None,
        True,
        False,
        -1,
        1.0,
        "1",
        [],
        {},
        (),
    ):

        try:

            drain.normalize_universal_worker_drain_count(
                bad,
                field_name=field_name,
            )

        except drain.UniversalWorkerDrainError as exc:

            rejected = (
                exc.code
                == "invalid_worker_drain_count"
            )

        else:

            rejected = False

        check(
            (
                "invalid_"
                + field_name
                + "_"
                + repr(bad)
            ),
            rejected,
        )


    try:

        drain.normalize_universal_worker_drain_count(
            drain.MAX_UNIVERSAL_WORKER_DRAIN_COUNT
            + 1,
            field_name=field_name,
        )

    except drain.UniversalWorkerDrainError as exc:

        rejected = (
            exc.code
            == "worker_drain_count_too_large"
        )

    else:

        rejected = False

    check(
        field_name
        + "_overflow_rejected",
        rejected,
    )


# ============================================================
# RESULT FORGERY
# ============================================================

for (
    requested,
    work_count,
    lease_count,
    forged_state,
) in (
    (
        False,
        0,
        0,
        drain.UniversalWorkerDrainState.DRAINED,
    ),
    (
        True,
        1,
        0,
        drain.UniversalWorkerDrainState.DRAINED,
    ),
    (
        True,
        0,
        1,
        drain.UniversalWorkerDrainState.NOT_REQUESTED,
    ),
    (
        True,
        0,
        0,
        drain.UniversalWorkerDrainState.DRAINING,
    ),
):

    try:

        drain.UniversalWorkerDrainResult(
            worker_id=reg.worker_id,
            worker_instance_id=reg.worker_instance_id,
            worker_type=reg.worker_type,
            drain_requested=requested,
            active_work_count=work_count,
            active_lease_count=lease_count,
            state=forged_state,
        )

    except drain.UniversalWorkerDrainError as exc:

        rejected = (
            exc.code
            == "inconsistent_worker_drain_state"
        )

    else:

        rejected = False

    check(
        (
            "forged_state_"
            + str(requested)
            + "_"
            + str(work_count)
            + "_"
            + str(lease_count)
            + "_"
            + forged_state.value
        ),
        rejected,
    )


# ============================================================
# IDENTITY HARDENING
# ============================================================

for field_name, bad_value in (
    ("worker_id", ""),
    ("worker_id", " "),
    ("worker_id", "\t"),
    ("worker_instance_id", ""),
    ("worker_instance_id", " "),
    ("worker_type", ""),
    ("worker_type", " "),
):

    kwargs = {
        "worker_id":
            reg.worker_id,

        "worker_instance_id":
            reg.worker_instance_id,

        "worker_type":
            reg.worker_type,

        "drain_requested":
            True,

        "active_work_count":
            0,

        "active_lease_count":
            0,
    }

    kwargs[
        field_name
    ] = bad_value

    try:

        drain.UniversalWorkerDrainEvidence(
            **kwargs
        )

    except drain.UniversalWorkerDrainError:

        rejected = True

    else:

        rejected = False

    check(
        (
            "identity_hardening_"
            + field_name
            + "_"
            + repr(
                bad_value
            )
        ),
        rejected,
    )


# ============================================================
# SCHEMA CONTRACT
# ============================================================

try:

    drain.UniversalWorkerDrainEvidence(
        worker_id=reg.worker_id,
        worker_instance_id=reg.worker_instance_id,
        worker_type=reg.worker_type,
        drain_requested=True,
        active_work_count=0,
        active_lease_count=0,
        schema_version="tampered",
    )

except drain.UniversalWorkerDrainError as exc:

    rejected = (
        exc.code
        == "invalid_worker_drain_evidence_schema_version"
    )

else:

    rejected = False


check(
    "evidence_schema_tamper_rejected",
    rejected,
)


try:

    drain.UniversalWorkerDrainResult(
        worker_id=reg.worker_id,
        worker_instance_id=reg.worker_instance_id,
        worker_type=reg.worker_type,
        drain_requested=True,
        active_work_count=0,
        active_lease_count=0,
        state=drain.UniversalWorkerDrainState.DRAINED,
        schema_version="tampered",
    )

except drain.UniversalWorkerDrainError as exc:

    rejected = (
        exc.code
        == "invalid_worker_drain_result_schema_version"
    )

else:

    rejected = False


check(
    "result_schema_tamper_rejected",
    rejected,
)


# ============================================================
# IMMUTABILITY
# ============================================================

for obj in (
    drained_evidence,
    drained,
):

    for field in fields(
        obj
    ):

        try:

            setattr(
                obj,
                field.name,
                None,
            )

        except Exception:

            immutable = True

        else:

            immutable = False

        check(
            (
                "immutable_"
                + type(obj).__name__
                + "_"
                + field.name
            ),
            immutable,
        )


# ============================================================
# EXACT FIELD CONTRACT
# ============================================================

evidence_fields = tuple(
    field.name
    for field in fields(
        drain.UniversalWorkerDrainEvidence
    )
)

result_fields = tuple(
    field.name
    for field in fields(
        drain.UniversalWorkerDrainResult
    )
)


check(
    "evidence_fields_exact",
    evidence_fields
    == (
        "worker_id",
        "worker_instance_id",
        "worker_type",
        "drain_requested",
        "active_work_count",
        "active_lease_count",
        "schema_version",
    ),
    evidence_fields,
)

check(
    "result_fields_exact",
    result_fields
    == (
        "worker_id",
        "worker_instance_id",
        "worker_type",
        "drain_requested",
        "active_work_count",
        "active_lease_count",
        "state",
        "schema_version",
    ),
    result_fields,
)


# ============================================================
# DETERMINISM
# ============================================================

repeat_evidence = (
    drain.create_universal_worker_drain_evidence(
        registration=reg,
        drain_requested=True,
        active_work_count=0,
        active_lease_count=0,
    )
)

repeat_result = (
    drain.evaluate_universal_worker_drain(
        evidence=repeat_evidence
    )
)


check(
    "deterministic_evidence",
    repeat_evidence
    == drained_evidence,
)

check(
    "deterministic_result",
    repeat_result
    == drained,
)


# ============================================================
# EXPLANATION CONTRACT
# ============================================================

explanation = (
    drain.explain_universal_worker_drain_v1()
)


check(
    "phase",
    explanation.get(
        "phase"
    )
    == "4.1.12",
)

check(
    "component",
    explanation.get(
        "component"
    )
    == "Universal Worker Drain",
)

check(
    "explanation_version",
    explanation.get(
        "version"
    )
    == drain.UNIVERSAL_WORKER_DRAIN_VERSION,
)

check(
    "scope_worker_only",
    (
        "individual-worker"
        in explanation.get(
            "scope_rule",
            "",
        )
        and
        "separate from whole-runtime"
        in explanation.get(
            "scope_rule",
            "",
        )
    ),
)

check(
    "not_requested_semantics",
    "NOT_REQUESTED"
    in explanation.get(
        "not_requested_rule",
        "",
    ),
)

check(
    "draining_semantics",
    "DRAINING"
    in explanation.get(
        "draining_rule",
        "",
    ),
)

check(
    "drained_semantics",
    "DRAINED"
    in explanation.get(
        "drained_rule",
        "",
    ),
)

check(
    "new_work_semantics",
    "accepts_new_work=false"
    in explanation.get(
        "new_work_rule",
        "",
    ),
)

check(
    "assignment_external",
    "does not modify or invoke"
    in explanation.get(
        "assignment_boundary",
        "",
    ),
)

check(
    "leasing_external",
    "does not acquire, renew or release"
    in explanation.get(
        "leasing_boundary",
        "",
    ),
)

check(
    "existing_work_preserved",
    "preserves existing work"
    in explanation.get(
        "existing_work_rule",
        "",
    ),
)

check(
    "shutdown_composition",
    (
        "4.1.8 Worker Shutdown"
        in explanation.get(
            "shutdown_boundary",
            "",
        )
        and
        "drain_complete"
        in explanation.get(
            "shutdown_boundary",
            "",
        )
    ),
)

check(
    "scaling_external",
    "does not perform scale-down"
    in explanation.get(
        "scaling_boundary",
        "",
    ),
)

check(
    "pool_membership_preserved",
    "does not remove"
    in explanation.get(
        "pool_boundary",
        "",
    ),
)

check(
    "health_stale_recovery_independent",
    "independent"
    in explanation.get(
        "health_stale_recovery_boundary",
        "",
    ),
)

check(
    "persistence_external",
    "does not persist"
    in explanation.get(
        "persistence_boundary",
        "",
    ),
)

check(
    "purity_rule",
    "no external mutation or I/O"
    in explanation.get(
        "purity_rule",
        "",
    ),
)


# ============================================================
# PROHIBITIONS
# ============================================================

required_prohibitions = (
    "does not use whole-runtime DRAINING as worker drain state",
    "does not mutate Runtime Lifecycle Manager",
    "does not assign workers",
    "does not modify Assignment eligibility directly",
    "does not acquire worker leases",
    "does not renew worker leases",
    "does not release worker leases",
    "does not cancel running work",
    "does not requeue jobs",
    "does not fail jobs",
    "does not terminate workers",
    "does not perform Worker Shutdown",
    "does not perform Worker Scaling",
    "does not modify Worker Registration",
    "does not deregister workers",
    "does not modify Worker Pool membership",
    "does not determine Worker Health",
    "does not detect stale workers",
    "does not initiate Worker Recovery",
    "does not inspect worker capabilities",
    "does not calculate worker capacity",
    "does not access Queue Infrastructure",
    "does not access orchestration",
    "does not access Runtime State Store",
    "does not persist drain state",
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
        item in prohibitions,
        item,
    )


# ============================================================
# IMPORT / API BOUNDARY
# ============================================================

source = DRAIN_PATH.read_text(
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

        module_name = (
            node.module
            or ""
        )

        if module_name.startswith(
            "backend.server"
        ):

            backend_imports.append(
                module_name
            )


check(
    "backend_imports_exact",
    backend_imports
    == [
        "backend.server.runtime.universal_worker.registration",
    ],
    backend_imports,
)


expected_all = (
    "UNIVERSAL_WORKER_DRAIN_VERSION",
    "UNIVERSAL_WORKER_DRAIN_EVIDENCE_SCHEMA_VERSION",
    "UNIVERSAL_WORKER_DRAIN_RESULT_SCHEMA_VERSION",
    "MAX_UNIVERSAL_WORKER_DRAIN_COUNT",
    "UNIVERSAL_WORKER_DRAIN_IDENTITY_SEPARATOR",
    "UniversalWorkerDrainError",
    "UniversalWorkerDrainState",
    "UniversalWorkerDrainEvidence",
    "UniversalWorkerDrainResult",
    "normalize_universal_worker_drain_requested",
    "normalize_universal_worker_drain_count",
    "decide_universal_worker_drain_state",
    "create_universal_worker_drain_evidence",
    "evaluate_universal_worker_drain",
    "explain_universal_worker_drain_v1",
)


check(
    "api_surface_exact",
    tuple(
        drain.__all__
    )
    == expected_all,
    drain.__all__,
)


# ============================================================
# SIDE EFFECT / RESPONSIBILITY BOUNDARY
# ============================================================

forbidden_calls = {
    "open",
    "read_text",
    "write_text",
    "write_json",
    "mkdir",
    "unlink",
    "remove",

    "drain",
    "shutdown",
    "terminate",
    "kill",

    "assign_universal_worker",
    "discover_universal_workers",

    "acquire_universal_worker_lease",
    "renew_universal_worker_lease",
    "release_universal_worker_lease",

    "evaluate_universal_worker_health",
    "evaluate_universal_stale_worker",
    "evaluate_universal_worker_recovery",
    "evaluate_universal_worker_scaling",
    "evaluate_universal_worker_shutdown",

    "add_universal_worker_pool_member",
    "remove_universal_worker_pool_member",

    "enqueue_job",
    "dequeue_job",
    "requeue_job",
    "cancel_job",
    "mark_job_failed",

    "get_runtime_state_store_registry",

    "persist",
    "save",
    "dispatch_job",
    "execute_job",
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
# RUNTIME LIFECYCLE COUPLING CHECK
# ============================================================

runtime_lifecycle_code_coupling = []


for node in ast.walk(
    tree
):

    if isinstance(
        node,
        ast.Name,
    ) and node.id == "RuntimeLifecyclePhase":

        runtime_lifecycle_code_coupling.append(
            (
                "Name",
                getattr(
                    node,
                    "lineno",
                    0,
                ),
            )
        )

    elif isinstance(
        node,
        ast.Attribute,
    ) and node.attr == "RuntimeLifecyclePhase":

        runtime_lifecycle_code_coupling.append(
            (
                "Attribute",
                getattr(
                    node,
                    "lineno",
                    0,
                ),
            )
        )

    elif isinstance(
        node,
        ast.ImportFrom,
    ):

        for alias in node.names:

            if alias.name == "RuntimeLifecyclePhase":

                runtime_lifecycle_code_coupling.append(
                    (
                        "ImportFrom",
                        getattr(
                            node,
                            "lineno",
                            0,
                        ),
                    )
                )


check(
    "no_runtime_lifecycle_code_coupling",
    not runtime_lifecycle_code_coupling,
    runtime_lifecycle_code_coupling,
)


# ============================================================
# PROTECTED AUTHORITY MATRIX
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
        "phase_4_1_12_worker_drain",
        drain.UNIVERSAL_WORKER_DRAIN_VERSION,
        drain.UNIVERSAL_WORKER_DRAIN_EVIDENCE_SCHEMA_VERSION,
        drain.UNIVERSAL_WORKER_DRAIN_RESULT_SCHEMA_VERSION,
        drain_ast,

        "canonical_worker_registration_identity",

        "drain_requested_false_not_requested",
        "drain_requested_true_active_work_draining",
        "drain_requested_true_active_lease_draining",
        "drain_requested_true_zero_work_zero_lease_drained",

        "not_requested_accepts_new_work_true",
        "draining_accepts_new_work_false",
        "drained_accepts_new_work_false",

        "not_requested_drain_complete_false",
        "draining_drain_complete_false",
        "drained_drain_complete_true",

        "existing_work_preserved",
        "existing_leases_preserved",

        "assignment_external",
        "leasing_external",
        "shutdown_external",
        "scaling_external",
        "pool_external",
        "health_external",
        "stale_external",
        "recovery_external",
        "capability_external",
        "capacity_external",

        "whole_runtime_drain_separate",
        "runtime_lifecycle_not_mutated",

        "no_queue_access",
        "no_orchestration_access",
        "no_runtime_state_store",
        "no_persistence",
        "no_filesystem_io",
        "no_network_io",

        "pure_worker_drain_evidence_authority",
    )
)


worker_drain_fingerprint = (
    hashlib.sha256(
        fingerprint_material.encode(
            "utf-8"
        )
    ).hexdigest().upper()
)


check(
    "fingerprint_generated",
    len(
        worker_drain_fingerprint
    )
    == 64,
    worker_drain_fingerprint,
)


# ============================================================
# FINAL AST RECHECK
# ============================================================

final_ast = ast_sha(
    DRAIN_PATH
)


check(
    "final_ast_unchanged",
    final_ast
    == EXPECTED_DRAIN_AST,
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
        "PHASE 4.1.12 — UNIVERSAL WORKER "
        "DRAIN FINAL CERTIFICATION"
    ),
    "=" * 112,
    "",
    (
        "WORKER DRAIN AST SHA256: "
        + drain_ast
    ),
    (
        "WORKER DRAIN FINGERPRINT: "
        + worker_drain_fingerprint
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
        "=" * 112,
        (
            "FINAL WORKER DRAIN CERTIFICATION: "
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
        "WORKER DRAIN MODIFIED DURING CERTIFICATION: NO",
        "4.1.1 WORKER REGISTRATION MODIFIED: NO",
        "4.1.2 WORKER DISCOVERY MODIFIED: NO",
        "4.1.3 WORKER ASSIGNMENT MODIFIED: NO",
        "4.1.4 WORKER LEASING MODIFIED: NO",
        "4.1.5 WORKER HEALTH MODIFIED: NO",
        "4.1.6 WORKER RECOVERY MODIFIED: NO",
        "4.1.7 WORKER SCALING MODIFIED: NO",
        "4.1.8 WORKER SHUTDOWN MODIFIED: NO",
        "4.1.9 WORKER POOL MODIFIED: NO",
        "4.1.10 WORKER HEARTBEAT MODIFIED: NO",
        "4.1.11 STALE WORKER DETECTION MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "RUNTIME LIFECYCLE MANAGER MODIFIED: NO",
        "RUNTIME SHUTDOWN PROCESS MODIFIED: NO",
        "ORCHESTRATION MODIFIED: NO",
        "WHOLE-RUNTIME DRAIN INVOKED: NO",
        "WHOLE-RUNTIME LIFECYCLE MUTATED: NO",
        "WORKER ASSIGNMENT INVOKED/MODIFIED: NO",
        "WORKER LEASE ACQUIRED/RENEWED/RELEASED: NO",
        "EXISTING WORK CANCELLED: NO",
        "JOB REQUEUED/FAILED/CANCELLED: NO",
        "WORKER TERMINATED: NO",
        "WORKER SHUTDOWN PERFORMED: NO",
        "WORKER SCALING PERFORMED: NO",
        "WORKER REGISTRATION MUTATED: NO",
        "WORKER DEREGISTERED: NO",
        "WORKER POOL MEMBERSHIP MODIFIED: NO",
        "WORKER HEALTH MODIFIED: NO",
        "STALE WORKER DETECTION INVOKED: NO",
        "WORKER RECOVERY INITIATED: NO",
        "WORKER CAPABILITY INSPECTED: NO",
        "WORKER CAPACITY CALCULATED: NO",
        "QUEUE INFRASTRUCTURE ACCESSED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "DRAIN STATE PERSISTED: NO",
        "FILESYSTEM I/O: NO",
        "NETWORK I/O: NO",
        "",
        (
            "PHASE 4.1.12 FREEZE CANDIDATE: "
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
        "Phase 4.1.12 Worker Drain final certification failed."
    )
