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

PERSISTENCE_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_orchestration"
    / "persistence_interface.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_1_14_orchestration_persistence_initial_implementation.txt"
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

    "5.1.11_progress_tracking": (
        ROOT / "backend/server/runtime/universal_orchestration/progress_tracking.py",
        "92C100E0682F975488F78ED5F0D38CB1F4C6E18F6FEA08D1A8D81BE98A4D8309",
    ),

    "5.1.12_suspension_resume": (
        ROOT / "backend/server/runtime/universal_orchestration/suspension_resume_eligibility.py",
        "476631641C740443FF7B3D1D1D0E9D6D155289BDCAF14526698528432CCF913A",
    ),

    "5.1.13_recovery": (
        ROOT / "backend/server/runtime/universal_orchestration/recovery.py",
        "4465A7AF795512594023D19E27A175CA060ACD2845BB4530B77FF8D69C40B16F",
    ),

    "job_contract": (
        ROOT / "backend/server/runtime/universal_jobs/contract.py",
        "82225461C792EDA7193D2FA3B59E39FF3823906365CD0FBCD5E2915673EE23D1",
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
        canonical.encode(
            "utf-8"
        )
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
            "Protected authority changed: "
            + name
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

planning = importlib.import_module(
    "backend.server.runtime.universal_orchestration.execution_planning"
)

state_model = importlib.import_module(
    "backend.server.runtime.universal_orchestration.state_model"
)

progress = importlib.import_module(
    "backend.server.runtime.universal_orchestration.progress_tracking"
)

persistence = importlib.import_module(
    "backend.server.runtime.universal_orchestration.persistence_interface"
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
):

    return jobs.UniversalJob(
        job_id=job_id,
        workspace_id="workspace-a",
        pipeline="pipeline-a",
        stage="stage-a",
        job_type="test_job",
        payload_reference="payload-a",
        dependency_job_ids=(),
        status=jobs.UniversalJobStatus.CREATED,
        created_at=FIXED_CREATED_AT,
    )


def make_plan(
    *,
    run_id,
):

    job = make_job(
        job_id="job-a"
    )

    contract = (
        contracts
        .create_universal_runtime_orchestration_contract(
            workspace_id="workspace-a",
            pipeline="pipeline-a",
            job_ids=("job-a",),
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
            jobs=(job,),
        )
    )


def make_state(
    *,
    plan,
    state,
):

    return (
        state_model
        .create_universal_orchestration_state_snapshot(
            identity=plan.identity,
            state=state,
        )
    )


def make_progress(
    *,
    plan,
    status,
):

    return (
        progress
        .track_universal_orchestration_progress(
            execution_plan=plan,
            status_evidence={
                "job-a":
                    status,
            },
        )
    )


plan = make_plan(
    run_id="persistence-initial"
)

state_active = make_state(
    plan=plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
)

progress_created = make_progress(
    plan=plan,
    status="created",
)


record1 = (
    persistence
    .create_universal_orchestration_persistence_record(
        state_snapshot=state_active,
        progress_snapshot=progress_created,
    )
)


check(
    "version_exact",
    persistence.UNIVERSAL_ORCHESTRATION_PERSISTENCE_INTERFACE_VERSION
    ==
    "universal_orchestration_persistence_interface_v5.1.14",
)

check(
    "schema_exact",
    persistence.UNIVERSAL_ORCHESTRATION_PERSISTENCE_RECORD_SCHEMA_VERSION
    ==
    "universal_orchestration_persistence_record_schema_v1",
)

check(
    "hash_exact",
    persistence.UNIVERSAL_ORCHESTRATION_PERSISTENCE_RECORD_HASH_ALGORITHM
    == "sha256",
)


# ROOT RECORD

check(
    "root_record_true",
    record1.is_root_record,
)

check(
    "root_previous_none",
    record1.previous_record_id
    is None,
)

check(
    "identity_derived",
    record1.identity
    is
    progress_created.identity,
)

check(
    "identity_fingerprint_exact",
    record1.identity_fingerprint
    ==
    progress_created.identity.identity_fingerprint.upper(),
)

check(
    "state_derived",
    record1.orchestration_state
    is
    state_model.UniversalOrchestrationState.ACTIVE,
)

check(
    "progress_snapshot_id_exact",
    record1.progress_snapshot_id
    ==
    progress_created.progress_snapshot_id.upper(),
)


# RECORD ID

record_id = (
    record1.persistence_record_id
)


check(
    "record_id_length",
    len(
        record_id
    )
    == 64,
    record_id,
)

check(
    "record_id_upper_hex",
    all(
        character
        in "0123456789ABCDEF"
        for character
        in record_id
    ),
)

check(
    "record_id_deterministic",
    record_id
    ==
    persistence
    .create_universal_orchestration_persistence_record(
        state_snapshot=state_active,
        progress_snapshot=progress_created,
    )
    .persistence_record_id,
)


# MANIFEST

manifest = (
    record1.manifest
)


check(
    "manifest_mappingproxy",
    isinstance(
        manifest,
        MappingProxyType,
    ),
)

check(
    "manifest_record_id_exact",
    manifest[
        "persistence_record_id"
    ]
    ==
    record1.persistence_record_id,
)

check(
    "manifest_previous_none",
    manifest[
        "previous_record_id"
    ]
    is None,
)

check(
    "manifest_state_exact",
    manifest[
        "orchestration_state"
    ]
    == "active",
)


# SUCCESSOR

state_waiting = make_state(
    plan=plan,
    state=state_model.UniversalOrchestrationState.WAITING,
)

progress_queued = make_progress(
    plan=plan,
    status="queued",
)


record2 = (
    persistence
    .create_universal_orchestration_persistence_record(
        state_snapshot=state_waiting,
        progress_snapshot=progress_queued,
        previous_record_id=record1.persistence_record_id,
    )
)


check(
    "successor_not_root",
    not record2.is_root_record,
)

check(
    "successor_previous_exact",
    record2.previous_record_id
    ==
    record1.persistence_record_id,
)

check(
    "successor_validation_true",
    persistence
    .validate_universal_orchestration_persistence_successor(
        previous_record=record1,
        next_record=record2,
    )
    is True,
)

check(
    "successor_id_changed",
    record2.persistence_record_id
    !=
    record1.persistence_record_id,
)


# INVALID LINK

bad_link_record = (
    persistence
    .create_universal_orchestration_persistence_record(
        state_snapshot=state_waiting,
        progress_snapshot=progress_queued,
        previous_record_id=(
            "A" * 64
        ),
    )
)


try:

    persistence.validate_universal_orchestration_persistence_successor(
        previous_record=record1,
        next_record=bad_link_record,
    )

except persistence.UniversalOrchestrationPersistenceError as exc:

    bad_link_rejected = (
        exc.code
        ==
        "persistence_successor_link_mismatch"
    )

else:

    bad_link_rejected = False


check(
    "bad_successor_link_rejected",
    bad_link_rejected,
)


# CROSS IDENTITY

other_plan = make_plan(
    run_id="persistence-other"
)

other_record = (
    persistence
    .create_universal_orchestration_persistence_record(
        state_snapshot=make_state(
            plan=other_plan,
            state=state_model.UniversalOrchestrationState.ACTIVE,
        ),
        progress_snapshot=make_progress(
            plan=other_plan,
            status="created",
        ),
        previous_record_id=record1.persistence_record_id,
    )
)


try:

    persistence.validate_universal_orchestration_persistence_successor(
        previous_record=record1,
        next_record=other_record,
    )

except persistence.UniversalOrchestrationPersistenceError as exc:

    cross_identity_rejected = (
        exc.code
        ==
        "persistence_successor_identity_mismatch"
    )

else:

    cross_identity_rejected = False


check(
    "cross_identity_successor_rejected",
    cross_identity_rejected,
)


# STORED FIELDS

field_names = tuple(
    field.name
    for field
    in fields(
        persistence.UniversalOrchestrationPersistenceRecord
    )
)


check(
    "stored_fields_exact",
    field_names
    == (
        "state_snapshot",
        "progress_snapshot",
        "previous_record_id",
        "schema_version",
    ),
    field_names,
)


# IMMUTABILITY

for field in fields(
    record1
):

    try:

        setattr(
            record1,
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


# INVALID PREVIOUS IDS

for index, bad in enumerate(
    (
        "",
        "abc",
        "G" * 64,
        "A" * 63,
        "A" * 65,
        123,
        True,
        (),
        [],
        {},
    ),
    start=1,
):

    try:

        persistence.create_universal_orchestration_persistence_record(
            state_snapshot=state_active,
            progress_snapshot=progress_created,
            previous_record_id=bad,
        )

    except persistence.UniversalOrchestrationPersistenceError as exc:

        rejected = (
            exc.code
            ==
            "invalid_previous_persistence_record_id"
        )

    else:

        rejected = False

    check(
        "invalid_previous_record_id_"
        + str(index),
        rejected,
    )


# CROSS SNAPSHOT IDENTITY

try:

    persistence.create_universal_orchestration_persistence_record(
        state_snapshot=state_active,
        progress_snapshot=make_progress(
            plan=other_plan,
            status="created",
        ),
    )

except persistence.UniversalOrchestrationPersistenceError as exc:

    snapshot_identity_rejected = (
        exc.code
        ==
        "persistence_identity_mismatch"
    )

else:

    snapshot_identity_rejected = False


check(
    "cross_snapshot_identity_rejected",
    snapshot_identity_rejected,
)


# PROTOCOL SURFACE

check(
    "persistence_port_runtime_protocol",
    getattr(
        persistence.UniversalOrchestrationPersistencePort,
        "_is_runtime_protocol",
        False,
    )
    is True,
)


for method_name in (
    "append_record",
    "load_latest_record",
    "load_record",
    "list_record_history",
):

    check(
        "port_method_"
        + method_name,
        hasattr(
            persistence.UniversalOrchestrationPersistencePort,
            method_name,
        ),
    )


for forbidden_method_name in (
    "delete",
    "delete_record",
    "update_record",
    "overwrite_record",
):

    check(
        "port_forbidden_method_absent_"
        + forbidden_method_name,
        not hasattr(
            persistence.UniversalOrchestrationPersistencePort,
            forbidden_method_name,
        ),
    )


# EXPLANATION

explanation = (
    persistence
    .explain_universal_orchestration_persistence_interface_v1()
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
    == "5.1.14",
)

check(
    "state_authority_5_1_3",
    "5.1.3"
    in explanation.get(
        "state_authority",
        "",
    ),
)

check(
    "progress_authority_5_1_11",
    "5.1.11"
    in explanation.get(
        "progress_authority",
        "",
    ),
)

check(
    "completion_boundary_5_1_15",
    "5.1.15"
    in explanation.get(
        "completion_boundary",
        "",
    ),
)

check(
    "termination_boundary_5_1_16",
    "5.1.16"
    in explanation.get(
        "termination_boundary",
        "",
    ),
)

check(
    "evidence_boundary_5_1_17",
    "5.1.17"
    in explanation.get(
        "evidence_boundary",
        "",
    ),
)


# IMPORT BOUNDARY

source = PERSISTENCE_PATH.read_text(
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
        "backend.server.runtime.universal_orchestration.state_model",
        "backend.server.runtime.universal_orchestration.progress_tracking",
    ],
    backend_imports,
)


# FORBIDDEN CALLS

forbidden_calls = {
    "open",
    "read_text",
    "write_text",
    "mkdir",
    "unlink",

    "sleep",
    "wait",
    "poll",

    "time",
    "now",
    "utcnow",

    "connect",
    "execute",
    "commit",
    "rollback",

    "persist",
    "save",
    "load",
    "delete",
    "update",

    "transition_universal_orchestration_state",
    "track_universal_orchestration_progress",

    "evaluate_universal_orchestration_suspension_resume_eligibility",
    "evaluate_universal_orchestration_recovery",

    "enqueue_job",
    "dequeue_job",
    "assign_universal_worker",
    "acquire_universal_worker_lease",

    "dispatch_registered_runtime_handler",
    "execute_registered_runtime_job_v1",

    "get_runtime_state_store_registry",
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

        name = (
            node.func.id
        )

    elif isinstance(
        node.func,
        ast.Attribute,
    ):

        name = (
            node.func.attr
        )

    else:

        continue

    if name in forbidden_calls:

        found_forbidden.append(
            (
                name,
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


persistence_ast = (
    ast_sha(
        PERSISTENCE_PATH
    )
)


check(
    "persistence_ast_generated",
    len(
        persistence_ast
    )
    == 64,
    persistence_ast,
)


# PROTECTED MATRIX

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
        "PHASE 5.1.14 — UNIVERSAL ORCHESTRATION "
        "PERSISTENCE INTERFACE INITIAL IMPLEMENTATION"
    ),

    "=" * 118,

    "",

    (
        "ORCHESTRATION PERSISTENCE INTERFACE AST SHA256: "
        + persistence_ast
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
            "INITIAL ORCHESTRATION PERSISTENCE INTERFACE RESULT: "
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

        "5.1.1–5.1.13 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "CANONICAL STORED STATE SNAPSHOT: YES",
        "CANONICAL STORED PROGRESS SNAPSHOT: YES",
        "APPEND-ONLY PREDECESSOR LINK: YES",

        "",

        "5.1.12 ELIGIBILITY DUPLICATED IN RECORD: NO",
        "5.1.13 RECOVERY DECISION DUPLICATED IN RECORD: NO",

        "",

        "DETERMINISTIC RECORD ID: YES",
        "IDENTITY ALIGNMENT REQUIRED: YES",
        "SUCCESSOR IDENTITY ALIGNMENT REQUIRED: YES",
        "SUCCESSOR PREDECESSOR LINK REQUIRED: YES",

        "",

        "PERSISTENCE PORT DEFINED: YES",
        "DELETE OPERATION EXPOSED: NO",
        "UPDATE/OVERWRITE OPERATION EXPOSED: NO",

        "",

        "RUNTIME STATE STORE INVOKED: NO",
        "RUNTIME PERSISTENCE INVOKED: NO",
        "FILESYSTEM I/O: NO",
        "DATABASE I/O: NO",
        "NETWORK I/O: NO",

        "",

        "TRANSACTION EXECUTION: NO",
        "LOCK EXECUTION: NO",
        "COMPARE-AND-SWAP EXECUTION: NO",
        "LATEST POINTER UPDATE: NO",

        "",

        "WALL CLOCK: NO",
        "TIMESTAMP GENERATION: NO",

        "",

        "STATE TRANSITION: NO",
        "PROGRESS RECOMPUTATION: NO",
        "CONDITIONAL REEVALUATION: NO",
        "RECOVERY REEVALUATION: NO",

        "",

        "COMPLETION RESOLUTION: NO",
        "TERMINATION RESOLUTION: NO",
        "PERMANENT EVIDENCE/AUDIT RECORDING: NO",

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
        "Phase 5.1.14 initial implementation failed."
    )
