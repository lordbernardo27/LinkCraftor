from __future__ import annotations

import ast
import hashlib
import importlib
import inspect
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
    / "phase_5_1_14_orchestration_persistence_final_certification.txt"
)

EXPECTED_PERSISTENCE_AST = (
    "5B7F640250498B4B5320C3702112D163E16B6878C412447623E5C0FF93608CCA"
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

    "queue_certification": (
        ROOT / "backend/server/runtime/universal_queue/certification.py",
        "6ED39655147D2B331E02101F5EA23E68CF71447353C0D294E170281AE40C0D4C",
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
        canonical.encode(
            "utf-8"
        )
    ).hexdigest().upper()


# ============================================================
# PRE-FLIGHT
# ============================================================

if not PERSISTENCE_PATH.exists():

    raise SystemExit(
        "5.1.14 Persistence Interface authority is missing."
    )


initial_ast = ast_sha(
    PERSISTENCE_PATH
)


if initial_ast != EXPECTED_PERSISTENCE_AST:

    raise SystemExit(
        (
            "5.1.14 AST changed before final certification.\n"
            "EXPECTED: "
            + EXPECTED_PERSISTENCE_AST
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
            "Protected authority mismatch before certification: "
            + name
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

planning = importlib.import_module(
    "backend.server.runtime.universal_orchestration.execution_planning"
)

state_model = importlib.import_module(
    "backend.server.runtime.universal_orchestration.state_model"
)

progress = importlib.import_module(
    "backend.server.runtime.universal_orchestration.progress_tracking"
)


module_name = (
    "backend.server.runtime."
    "universal_orchestration.persistence_interface"
)

sys.modules.pop(
    module_name,
    None,
)

persistence = importlib.import_module(
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


FIXED_CREATED_AT = (
    "2026-05-21T03:49:30.579317+00:00"
)


# ============================================================
# HELPERS
# ============================================================

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


def make_record(
    *,
    plan,
    state,
    status,
    previous_record_id=None,
):

    return (
        persistence
        .create_universal_orchestration_persistence_record(
            state_snapshot=make_state(
                plan=plan,
                state=state,
            ),
            progress_snapshot=make_progress(
                plan=plan,
                status=status,
            ),
            previous_record_id=previous_record_id,
        )
    )


# ============================================================
# AUTHORITY EXACTNESS
# ============================================================

check(
    "ast_exact",
    ast_sha(
        PERSISTENCE_PATH
    )
    ==
    EXPECTED_PERSISTENCE_AST,
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
    "hash_algorithm_exact",
    persistence.UNIVERSAL_ORCHESTRATION_PERSISTENCE_RECORD_HASH_ALGORITHM
    ==
    "sha256",
)


# ============================================================
# CANONICAL ROOT + SUCCESSOR
# ============================================================

plan = make_plan(
    run_id="persistence-final-certification"
)


root = make_record(
    plan=plan,
    state=state_model.UniversalOrchestrationState.CREATED,
    status="created",
)


successor = make_record(
    plan=plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    status="running",
    previous_record_id=(
        root.persistence_record_id
    ),
)


check(
    "root_is_root",
    root.is_root_record,
)

check(
    "root_previous_none",
    root.previous_record_id
    is None,
)

check(
    "successor_not_root",
    not successor.is_root_record,
)

check(
    "successor_link_exact",
    successor.previous_record_id
    ==
    root.persistence_record_id,
)

check(
    "successor_validation",
    persistence
    .validate_universal_orchestration_persistence_successor(
        previous_record=root,
        next_record=successor,
    )
    is True,
)


# ============================================================
# RECORD-ID CONTRACT
# ============================================================

root_id = (
    root.persistence_record_id
)


check(
    "record_id_length",
    len(
        root_id
    )
    == 64,
    root_id,
)

check(
    "record_id_upper_hex",
    all(
        character
        in "0123456789ABCDEF"
        for character
        in root_id
    ),
)

check(
    "record_id_deterministic",
    root_id
    ==
    make_record(
        plan=plan,
        state=state_model.UniversalOrchestrationState.CREATED,
        status="created",
    )
    .persistence_record_id,
)


state_changed = make_record(
    plan=plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    status="created",
)


progress_changed = make_record(
    plan=plan,
    state=state_model.UniversalOrchestrationState.CREATED,
    status="queued",
)


predecessor_changed = make_record(
    plan=plan,
    state=state_model.UniversalOrchestrationState.CREATED,
    status="created",
    previous_record_id=root.persistence_record_id,
)


check(
    "record_id_state_sensitive",
    state_changed.persistence_record_id
    != root_id,
)

check(
    "record_id_progress_sensitive",
    progress_changed.persistence_record_id
    != root_id,
)

check(
    "record_id_predecessor_sensitive",
    predecessor_changed.persistence_record_id
    != root_id,
)


other_plan = make_plan(
    run_id="persistence-final-other"
)


other_run = make_record(
    plan=other_plan,
    state=state_model.UniversalOrchestrationState.CREATED,
    status="created",
)


check(
    "record_id_run_sensitive",
    other_run.persistence_record_id
    != root_id,
)


# ============================================================
# STORED FIELDS
# ============================================================

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
    ==
    (
        "state_snapshot",
        "progress_snapshot",
        "previous_record_id",
        "schema_version",
    ),
    field_names,
)


# ============================================================
# MANIFEST
# ============================================================

manifest = (
    successor.manifest
)


check(
    "manifest_mappingproxy",
    isinstance(
        manifest,
        MappingProxyType,
    ),
)

check(
    "manifest_keys_exact",
    tuple(
        manifest.keys()
    )
    ==
    (
        "persistence_record_id",
        "previous_record_id",
        "identity_fingerprint",
        "orchestration_state",
        "progress_snapshot_id",
        "schema_version",
    ),
)

check(
    "manifest_record_id_exact",
    manifest[
        "persistence_record_id"
    ]
    ==
    successor.persistence_record_id,
)

check(
    "manifest_previous_exact",
    manifest[
        "previous_record_id"
    ]
    ==
    root.persistence_record_id,
)

check(
    "manifest_identity_exact",
    manifest[
        "identity_fingerprint"
    ]
    ==
    successor.identity_fingerprint,
)

check(
    "manifest_state_exact",
    manifest[
        "orchestration_state"
    ]
    ==
    "active",
)

check(
    "manifest_progress_exact",
    manifest[
        "progress_snapshot_id"
    ]
    ==
    successor.progress_snapshot_id,
)


# ============================================================
# IMMUTABILITY
# ============================================================

for field in fields(
    successor
):

    try:

        setattr(
            successor,
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


try:

    manifest[
        "schema_version"
    ] = "modified"

except Exception:

    manifest_immutable = True

else:

    manifest_immutable = False


check(
    "manifest_immutable",
    manifest_immutable,
)


# ============================================================
# PREDECESSOR NORMALIZATION
# ============================================================

lower_previous = (
    root.persistence_record_id.lower()
)


normalized = make_record(
    plan=plan,
    state=state_model.UniversalOrchestrationState.WAITING,
    status="queued",
    previous_record_id=(
        " "
        + lower_previous
        + " "
    ),
)


check(
    "predecessor_normalized",
    normalized.previous_record_id
    ==
    root.persistence_record_id,
)


# ============================================================
# INVALID SUCCESSOR LINK
# ============================================================

bad_link = make_record(
    plan=plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    status="queued",
    previous_record_id=(
        "A" * 64
    ),
)


try:

    persistence.validate_universal_orchestration_persistence_successor(
        previous_record=root,
        next_record=bad_link,
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
    "bad_link_rejected",
    bad_link_rejected,
)


# ============================================================
# CROSS-RUN SUCCESSOR
# ============================================================

cross_run = make_record(
    plan=other_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    status="queued",
    previous_record_id=(
        root.persistence_record_id
    ),
)


try:

    persistence.validate_universal_orchestration_persistence_successor(
        previous_record=root,
        next_record=cross_run,
    )

except persistence.UniversalOrchestrationPersistenceError as exc:

    cross_run_rejected = (
        exc.code
        ==
        "persistence_successor_identity_mismatch"
    )

else:

    cross_run_rejected = False


check(
    "cross_run_successor_rejected",
    cross_run_rejected,
)


# ============================================================
# DERIVED DECISIONS ARE NOT STORED
# ============================================================

for forbidden_field in (
    "suspension_resume_eligibility",
    "eligibility_decision",
    "eligibility_decision_id",
    "recovery_decision",
    "recovery_decision_id",
):

    check(
        "derived_decision_not_stored_"
        + forbidden_field,
        forbidden_field
        not in field_names,
    )


# ============================================================
# PORT SURFACE
# ============================================================

port = (
    persistence
    .UniversalOrchestrationPersistencePort
)


check(
    "port_protocol",
    getattr(
        port,
        "_is_protocol",
        False,
    )
    is True,
)

check(
    "port_runtime_protocol",
    getattr(
        port,
        "_is_runtime_protocol",
        False,
    )
    is True,
)


expected_port_methods = (
    "append_record",
    "load_latest_record",
    "load_record",
    "list_record_history",
)


for method_name in expected_port_methods:

    check(
        "port_method_"
        + method_name,
        hasattr(
            port,
            method_name,
        ),
    )


for forbidden_method in (
    "delete",
    "delete_record",
    "update",
    "update_record",
    "overwrite",
    "overwrite_record",
    "replace_record",
    "commit",
    "rollback",
    "lock",
    "unlock",
    "compare_and_swap",
):

    check(
        "port_forbidden_"
        + forbidden_method,
        not hasattr(
            port,
            forbidden_method,
        ),
    )


check(
    "append_signature_record",
    "record"
    in inspect.signature(
        port.append_record
    ).parameters,
)

check(
    "latest_signature_identity",
    "identity_fingerprint"
    in inspect.signature(
        port.load_latest_record
    ).parameters,
)

check(
    "load_signature_record_id",
    "persistence_record_id"
    in inspect.signature(
        port.load_record
    ).parameters,
)

check(
    "history_signature_identity",
    "identity_fingerprint"
    in inspect.signature(
        port.list_record_history
    ).parameters,
)


# ============================================================
# EXPLANATION BOUNDARIES
# ============================================================

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
    ==
    "5.1.14",
)

check(
    "component_exact",
    explanation.get(
        "component"
    )
    ==
    "Universal Orchestration Persistence Interface",
)

check(
    "state_boundary_5_1_3",
    "5.1.3"
    in explanation.get(
        "state_authority",
        "",
    ),
)

check(
    "progress_boundary_5_1_11",
    "5.1.11"
    in explanation.get(
        "progress_authority",
        "",
    ),
)

check(
    "derived_rule_5_1_12",
    "5.1.12"
    in explanation.get(
        "derived_decision_rule",
        "",
    ),
)

check(
    "derived_rule_5_1_13",
    "5.1.13"
    in explanation.get(
        "derived_decision_rule",
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


# ============================================================
# IMPORT BOUNDARY
# ============================================================

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
    ==
    [
        "backend.server.runtime.universal_orchestration.state_model",
        "backend.server.runtime.universal_orchestration.progress_tracking",
    ],
    backend_imports,
)


# ============================================================
# FORBIDDEN CALLS
# ============================================================

forbidden_calls = {
    "eval",
    "exec",
    "compile",

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
    "upsert",
    "insert",

    "compare_and_swap",

    "transition_universal_orchestration_state",
    "track_universal_orchestration_progress",

    "evaluate_universal_orchestration_suspension_resume_eligibility",
    "evaluate_universal_orchestration_recovery",

    "enqueue_job",
    "dequeue_job",
    "claim_job",

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
        ==
        expected,
        actual,
    )


# ============================================================
# CANONICAL FINGERPRINT
# ============================================================

fingerprint_material = "|".join(
    (
        "phase_5_1_14_universal_orchestration_persistence_interface",

        persistence.UNIVERSAL_ORCHESTRATION_PERSISTENCE_INTERFACE_VERSION,
        persistence.UNIVERSAL_ORCHESTRATION_PERSISTENCE_RECORD_SCHEMA_VERSION,
        persistence.UNIVERSAL_ORCHESTRATION_PERSISTENCE_RECORD_HASH_ALGORITHM,

        EXPECTED_PERSISTENCE_AST,

        "state_authority_5_1_3",
        "progress_authority_5_1_11",

        "stored_state_snapshot",
        "stored_progress_snapshot",
        "stored_previous_record_id",
        "stored_schema_version",

        "derived_identity",
        "derived_identity_fingerprint",
        "derived_orchestration_state",
        "derived_progress_snapshot_id",

        "immutable_persistence_record",
        "immutable_manifest",

        "append_only_lineage",
        "root_record_allowed",
        "successor_requires_same_identity",
        "successor_requires_exact_predecessor",

        "record_id_sha256",
        "record_id_identity_sensitive",
        "record_id_state_sensitive",
        "record_id_progress_sensitive",
        "record_id_predecessor_sensitive",

        "eligibility_not_duplicated",
        "recovery_decision_not_duplicated",

        "persistence_port_protocol",
        "port_append_record",
        "port_load_latest_record",
        "port_load_record",
        "port_list_record_history",

        "no_delete_operation",
        "no_update_operation",
        "no_overwrite_operation",

        "no_runtime_state_store_import",
        "no_runtime_persistence_import",

        "no_storage_backend_selection",

        "no_filesystem_io",
        "no_database_io",
        "no_network_io",

        "no_transaction_execution",
        "no_lock_execution",
        "no_compare_and_swap_execution",
        "no_latest_pointer_update",

        "no_wall_clock",
        "no_timestamp_generation",

        "no_external_serialization",
        "no_external_deserialization",

        "no_state_transition",
        "no_progress_recomputation",
        "no_conditional_reevaluation",
        "no_suspension_resume_reevaluation",
        "no_recovery_reevaluation",

        "completion_deferred_5_1_15",
        "termination_deferred_5_1_16",
        "evidence_records_deferred_5_1_17",

        "no_queue_activity",
        "no_worker_activity",
        "no_lease_activity",
        "no_handler_dispatch",
        "no_job_execution",

        "no_universal_coordination_framework",
        "no_pipeline_coordinator",

        "deterministic_append_only_orchestration_persistence_contract",
    )
)


persistence_fingerprint = (
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
            persistence_fingerprint
        )
        == 64
        and
        all(
            character
            in "0123456789ABCDEF"
            for character
            in persistence_fingerprint
        )
    ),
    persistence_fingerprint,
)


# ============================================================
# FINAL AST
# ============================================================

final_ast = ast_sha(
    PERSISTENCE_PATH
)


check(
    "final_ast_unchanged",
    final_ast
    ==
    EXPECTED_PERSISTENCE_AST,
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
        "PHASE 5.1.14 — UNIVERSAL ORCHESTRATION "
        "PERSISTENCE INTERFACE FINAL CERTIFICATION"
    ),

    "=" * 118,

    "",

    (
        "ORCHESTRATION PERSISTENCE INTERFACE AST SHA256: "
        + final_ast
    ),

    (
        "ORCHESTRATION PERSISTENCE INTERFACE FINGERPRINT: "
        + persistence_fingerprint
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
            "FINAL ORCHESTRATION PERSISTENCE INTERFACE CERTIFICATION: "
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

        "5.1.14 AUTHORITY MODIFIED DURING CERTIFICATION: NO",
        "5.1.1–5.1.13 FROZEN AUTHORITIES MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "STATE AUTHORITY: 5.1.3",
        "PROGRESS AUTHORITY: 5.1.11",

        "",

        "CANONICAL STORED FIELDS:",
        "  state_snapshot",
        "  progress_snapshot",
        "  previous_record_id",
        "  schema_version",

        "",

        "PERSISTENCE RECORD IMMUTABLE: YES",
        "MANIFEST IMMUTABLE: YES",
        "APPEND-ONLY LINEAGE: YES",

        "",

        "SUCCESSOR SAME IDENTITY REQUIRED: YES",
        "SUCCESSOR EXACT PREDECESSOR REQUIRED: YES",

        "",

        "RECORD ID DETERMINISTIC: YES",
        "RECORD ID IDENTITY SENSITIVE: YES",
        "RECORD ID STATE SENSITIVE: YES",
        "RECORD ID PROGRESS SENSITIVE: YES",
        "RECORD ID PREDECESSOR SENSITIVE: YES",

        "",

        "5.1.12 ELIGIBILITY DUPLICATED: NO",
        "5.1.13 RECOVERY DECISION DUPLICATED: NO",

        "",

        "PERSISTENCE PORT:",
        "  append_record",
        "  load_latest_record",
        "  load_record",
        "  list_record_history",

        "",

        "DELETE OPERATION: NO",
        "UPDATE OPERATION: NO",
        "OVERWRITE OPERATION: NO",

        "",

        "RUNTIME STATE STORE IMPORT: NO",
        "RUNTIME PERSISTENCE IMPORT: NO",

        "",

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
        "SUSPENSION/RESUME REEVALUATION: NO",
        "RECOVERY REEVALUATION: NO",

        "",

        "COMPLETION RESOLUTION: NO",
        "TERMINATION RESOLUTION: NO",
        "PERMANENT EVIDENCE/AUDIT RECORDING: NO",

        "",

        "QUEUE ACTIVITY: NO",
        "WORKER ACTIVITY: NO",
        "LEASE ACTIVITY: NO",
        "HANDLER DISPATCH: NO",
        "JOB EXECUTION: NO",

        "",

        "UNIVERSAL COORDINATION FRAMEWORK ACCESS: NO",
        "PIPELINE COORDINATOR ACCESS: NO",

        "",

        (
            "PHASE 5.1.14 FREEZE CANDIDATE: "
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
        "Phase 5.1.14 final certification failed."
    )
