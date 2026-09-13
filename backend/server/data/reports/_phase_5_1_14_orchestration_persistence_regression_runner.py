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
    / "phase_5_1_14_orchestration_persistence_regression.txt"
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
            "5.1.14 AST changed before adversarial regression.\n"
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
            "Protected authority mismatch before regression: "
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
# FIXTURE HELPERS
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
    job_ids=("job-a",),
):

    job_tuple = tuple(
        make_job(
            job_id=job_id
        )
        for job_id
        in job_ids
    )

    contract = (
        contracts
        .create_universal_runtime_orchestration_contract(
            workspace_id="workspace-a",
            pipeline="pipeline-a",
            job_ids=job_ids,
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
            jobs=job_tuple,
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
    statuses,
):

    return (
        progress
        .track_universal_orchestration_progress(
            execution_plan=plan,
            status_evidence=statuses,
        )
    )


def make_record(
    *,
    plan,
    state,
    statuses,
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
                statuses=statuses,
            ),
            previous_record_id=previous_record_id,
        )
    )


# ============================================================
# 1. AUTHORITY EXACTNESS
# ============================================================

check(
    "ast_initial_exact",
    ast_sha(
        PERSISTENCE_PATH
    )
    == EXPECTED_PERSISTENCE_AST,
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


expected_all = (
    "UNIVERSAL_ORCHESTRATION_PERSISTENCE_INTERFACE_VERSION",
    "UNIVERSAL_ORCHESTRATION_PERSISTENCE_RECORD_SCHEMA_VERSION",
    "UNIVERSAL_ORCHESTRATION_PERSISTENCE_RECORD_HASH_ALGORITHM",
    "UniversalOrchestrationPersistenceError",
    "UniversalOrchestrationPersistenceRecord",
    "UniversalOrchestrationPersistencePort",
    "create_universal_orchestration_persistence_record",
    "validate_universal_orchestration_persistence_successor",
    "explain_universal_orchestration_persistence_interface_v1",
)


check(
    "public_api_exact",
    tuple(
        persistence.__all__
    )
    == expected_all,
    persistence.__all__,
)


# ============================================================
# 2. INVALID TOP-LEVEL INPUTS
# ============================================================

base_plan = make_plan(
    run_id="invalid-inputs"
)

base_state = make_state(
    plan=base_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
)

base_progress = make_progress(
    plan=base_plan,
    statuses={
        "job-a": "created",
    },
)


for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        1,
        1.0,
        "",
        (),
        [],
        {},
        set(),
        object(),
    ),
    start=1,
):

    try:

        persistence.create_universal_orchestration_persistence_record(
            state_snapshot=bad,
            progress_snapshot=base_progress,
        )

    except persistence.UniversalOrchestrationPersistenceError as exc:

        rejected = (
            exc.code
            ==
            "invalid_persistence_state_snapshot"
        )

    else:

        rejected = False

    check(
        "invalid_state_snapshot_"
        + str(index),
        rejected,
    )


for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        1,
        1.0,
        "",
        (),
        [],
        {},
        set(),
        object(),
    ),
    start=1,
):

    try:

        persistence.create_universal_orchestration_persistence_record(
            state_snapshot=base_state,
            progress_snapshot=bad,
        )

    except persistence.UniversalOrchestrationPersistenceError as exc:

        rejected = (
            exc.code
            ==
            "invalid_persistence_progress_snapshot"
        )

    else:

        rejected = False

    check(
        "invalid_progress_snapshot_"
        + str(index),
        rejected,
    )


# ============================================================
# 3. STORED FIELDS EXACTNESS
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
    == (
        "state_snapshot",
        "progress_snapshot",
        "previous_record_id",
        "schema_version",
    ),
    field_names,
)


for forbidden in (
    "identity",
    "identity_fingerprint",
    "orchestration_state",
    "progress_snapshot_id",
    "persistence_record_id",
    "is_root_record",
    "manifest",

    "created_at",
    "updated_at",
    "timestamp",

    "revision",
    "generation",
    "etag",
    "expected_revision",

    "queue_id",
    "worker_id",
    "lease_id",
):

    check(
        "forbidden_stored_"
        + forbidden,
        forbidden
        not in field_names,
    )


# ============================================================
# 4. INVALID SCHEMA VERSION
# ============================================================

try:

    persistence.UniversalOrchestrationPersistenceRecord(
        state_snapshot=base_state,
        progress_snapshot=base_progress,
        schema_version="wrong",
    )

except persistence.UniversalOrchestrationPersistenceError as exc:

    bad_schema_rejected = (
        exc.code
        ==
        "invalid_persistence_schema_version"
    )

else:

    bad_schema_rejected = False


check(
    "invalid_schema_rejected",
    bad_schema_rejected,
)


# ============================================================
# 5. PREDECESSOR NORMALIZATION
# ============================================================

valid_lower = (
    "abcdef0123456789"
    * 4
)


normalized_record = (
    persistence
    .create_universal_orchestration_persistence_record(
        state_snapshot=base_state,
        progress_snapshot=base_progress,
        previous_record_id=(
            "   "
            + valid_lower
            + "   "
        ),
    )
)


check(
    "previous_id_trimmed",
    normalized_record.previous_record_id
    ==
    valid_lower.upper(),
)

check(
    "previous_id_uppercased",
    normalized_record.previous_record_id
    ==
    normalized_record.previous_record_id.upper(),
)


# ============================================================
# 6. INVALID PREDECESSOR IDS
# ============================================================

invalid_previous_values = (
    "",
    " ",
    "abc",
    "A" * 63,
    "A" * 65,
    "G" * 64,
    "Z" * 64,
    "-1",
    0,
    1,
    True,
    False,
    1.0,
    (),
    [],
    {},
    set(),
    object(),
)


for index, bad in enumerate(
    invalid_previous_values,
    start=1,
):

    try:

        persistence.create_universal_orchestration_persistence_record(
            state_snapshot=base_state,
            progress_snapshot=base_progress,
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


# ============================================================
# 7. ROOT RECORD DETERMINISM
# ============================================================

root_ids = tuple(
    persistence
    .create_universal_orchestration_persistence_record(
        state_snapshot=base_state,
        progress_snapshot=base_progress,
    )
    .persistence_record_id
    for _
    in range(
        25
    )
)


check(
    "root_record_id_deterministic",
    len(
        set(
            root_ids
        )
    )
    == 1,
)

check(
    "root_record_id_length",
    len(
        root_ids[0]
    )
    == 64,
    root_ids[0],
)

check(
    "root_record_id_upper_hex",
    all(
        character
        in "0123456789ABCDEF"
        for character
        in root_ids[0]
    ),
)


# ============================================================
# 8. RECORD-ID STATE SENSITIVITY
# ============================================================

active_record = make_record(
    plan=base_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "job-a": "created",
    },
)

waiting_record = make_record(
    plan=base_plan,
    state=state_model.UniversalOrchestrationState.WAITING,
    statuses={
        "job-a": "created",
    },
)


check(
    "record_id_state_sensitive",
    active_record.persistence_record_id
    != waiting_record.persistence_record_id,
)


# ============================================================
# 9. RECORD-ID PROGRESS SENSITIVITY
# ============================================================

created_record = make_record(
    plan=base_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "job-a": "created",
    },
)

running_record = make_record(
    plan=base_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "job-a": "running",
    },
)


check(
    "record_id_progress_sensitive",
    created_record.persistence_record_id
    != running_record.persistence_record_id,
)


# ============================================================
# 10. RECORD-ID PREDECESSOR SENSITIVITY
# ============================================================

same_evidence_root = make_record(
    plan=base_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "job-a": "created",
    },
)


same_evidence_successor = make_record(
    plan=base_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "job-a": "created",
    },
    previous_record_id=(
        same_evidence_root.persistence_record_id
    ),
)


check(
    "record_id_predecessor_sensitive",
    same_evidence_root.persistence_record_id
    !=
    same_evidence_successor.persistence_record_id,
)


# ============================================================
# 11. RECORD-ID RUN SENSITIVITY
# ============================================================

other_plan = make_plan(
    run_id="run-sensitive-other"
)

other_run_record = make_record(
    plan=other_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "job-a": "created",
    },
)


check(
    "record_id_run_sensitive",
    active_record.persistence_record_id
    !=
    other_run_record.persistence_record_id,
)


# ============================================================
# 12. LONG APPEND-ONLY CHAIN
# ============================================================

chain_plan = make_plan(
    run_id="long-chain"
)


chain = []


state_sequence = (
    state_model.UniversalOrchestrationState.CREATED,
    state_model.UniversalOrchestrationState.ACTIVE,
    state_model.UniversalOrchestrationState.WAITING,
    state_model.UniversalOrchestrationState.ACTIVE,
    state_model.UniversalOrchestrationState.SUSPENDED,
    state_model.UniversalOrchestrationState.ACTIVE,
    state_model.UniversalOrchestrationState.RECOVERING,
    state_model.UniversalOrchestrationState.ACTIVE,
)


status_sequence = (
    "created",
    "queued",
    "scheduled",
    "running",
    "suspended",
    "queued",
    "failed",
    "created",
)


previous_id = None


for state, status in zip(
    state_sequence,
    status_sequence,
):

    record = make_record(
        plan=chain_plan,
        state=state,
        statuses={
            "job-a": status,
        },
        previous_record_id=previous_id,
    )

    chain.append(
        record
    )

    previous_id = (
        record.persistence_record_id
    )


check(
    "long_chain_length",
    len(
        chain
    )
    == 8,
)


for index, record in enumerate(
    chain
):

    if index == 0:

        check(
            "chain_root_0",
            record.is_root_record,
        )

    else:

        check(
            "chain_link_"
            + str(index),
            record.previous_record_id
            ==
            chain[
                index - 1
            ].persistence_record_id,
        )

        check(
            "chain_validate_"
            + str(index),
            persistence
            .validate_universal_orchestration_persistence_successor(
                previous_record=chain[
                    index - 1
                ],
                next_record=record,
            )
            is True,
        )


check(
    "chain_ids_all_unique",
    len(
        {
            record.persistence_record_id
            for record
            in chain
        }
    )
    ==
    len(
        chain
    ),
)


# ============================================================
# 13. SKIPPED PREDECESSOR ATTACK
# ============================================================

skip_record = make_record(
    plan=chain_plan,
    state=state_model.UniversalOrchestrationState.WAITING,
    statuses={
        "job-a": "queued",
    },
    previous_record_id=(
        chain[0].persistence_record_id
    ),
)


try:

    persistence.validate_universal_orchestration_persistence_successor(
        previous_record=chain[1],
        next_record=skip_record,
    )

except persistence.UniversalOrchestrationPersistenceError as exc:

    skipped_link_rejected = (
        exc.code
        ==
        "persistence_successor_link_mismatch"
    )

else:

    skipped_link_rejected = False


check(
    "skipped_predecessor_rejected",
    skipped_link_rejected,
)


# ============================================================
# 14. CROSS-RUN LINEAGE ATTACK
# ============================================================

cross_plan = make_plan(
    run_id="cross-run-lineage"
)


cross_record = make_record(
    plan=cross_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
    statuses={
        "job-a": "created",
    },
    previous_record_id=(
        chain[-1].persistence_record_id
    ),
)


try:

    persistence.validate_universal_orchestration_persistence_successor(
        previous_record=chain[-1],
        next_record=cross_record,
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
    "cross_run_lineage_rejected",
    cross_run_rejected,
)


# ============================================================
# 15. INVALID SUCCESSOR INPUT TYPES
# ============================================================

for index, bad in enumerate(
    (
        None,
        True,
        0,
        "",
        (),
        [],
        {},
        object(),
    ),
    start=1,
):

    try:

        persistence.validate_universal_orchestration_persistence_successor(
            previous_record=bad,
            next_record=chain[1],
        )

    except persistence.UniversalOrchestrationPersistenceError as exc:

        rejected = (
            exc.code
            ==
            "invalid_previous_persistence_record"
        )

    else:

        rejected = False

    check(
        "invalid_previous_record_object_"
        + str(index),
        rejected,
    )


for index, bad in enumerate(
    (
        None,
        True,
        0,
        "",
        (),
        [],
        {},
        object(),
    ),
    start=1,
):

    try:

        persistence.validate_universal_orchestration_persistence_successor(
            previous_record=chain[0],
            next_record=bad,
        )

    except persistence.UniversalOrchestrationPersistenceError as exc:

        rejected = (
            exc.code
            ==
            "invalid_next_persistence_record"
        )

    else:

        rejected = False

    check(
        "invalid_next_record_object_"
        + str(index),
        rejected,
    )


# ============================================================
# 16. MANIFEST EXACTNESS
# ============================================================

manifest_record = chain[3]

manifest = (
    manifest_record.manifest
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
    == (
        "persistence_record_id",
        "previous_record_id",
        "identity_fingerprint",
        "orchestration_state",
        "progress_snapshot_id",
        "schema_version",
    ),
    tuple(
        manifest.keys()
    ),
)

check(
    "manifest_record_id_exact",
    manifest[
        "persistence_record_id"
    ]
    ==
    manifest_record.persistence_record_id,
)

check(
    "manifest_previous_exact",
    manifest[
        "previous_record_id"
    ]
    ==
    manifest_record.previous_record_id,
)

check(
    "manifest_identity_exact",
    manifest[
        "identity_fingerprint"
    ]
    ==
    manifest_record.identity_fingerprint,
)

check(
    "manifest_state_exact",
    manifest[
        "orchestration_state"
    ]
    ==
    manifest_record.orchestration_state.value,
)

check(
    "manifest_progress_exact",
    manifest[
        "progress_snapshot_id"
    ]
    ==
    manifest_record.progress_snapshot_id,
)

check(
    "manifest_schema_exact",
    manifest[
        "schema_version"
    ]
    ==
    persistence.UNIVERSAL_ORCHESTRATION_PERSISTENCE_RECORD_SCHEMA_VERSION,
)


try:

    manifest[
        "schema_version"
    ] = "changed"

except Exception:

    manifest_immutable = True

else:

    manifest_immutable = False


check(
    "manifest_immutable",
    manifest_immutable,
)


# ============================================================
# 17. DATACLASS IMMUTABILITY
# ============================================================

for field in fields(
    manifest_record
):

    try:

        setattr(
            manifest_record,
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
# 18. SOURCE SNAPSHOTS NOT MUTATED
# ============================================================

snapshot_state = make_state(
    plan=base_plan,
    state=state_model.UniversalOrchestrationState.ACTIVE,
)

snapshot_progress = make_progress(
    plan=base_plan,
    statuses={
        "job-a": "running",
    },
)


state_before = (
    snapshot_state.identity,
    snapshot_state.state,
    snapshot_state.schema_version,
)

progress_before = (
    snapshot_progress.execution_plan,
    snapshot_progress.status_evidence,
    snapshot_progress.conditional_branching_decisions,
    snapshot_progress.schema_version,
    snapshot_progress.progress_snapshot_id,
)


_ = (
    persistence
    .create_universal_orchestration_persistence_record(
        state_snapshot=snapshot_state,
        progress_snapshot=snapshot_progress,
    )
)


state_after = (
    snapshot_state.identity,
    snapshot_state.state,
    snapshot_state.schema_version,
)

progress_after = (
    snapshot_progress.execution_plan,
    snapshot_progress.status_evidence,
    snapshot_progress.conditional_branching_decisions,
    snapshot_progress.schema_version,
    snapshot_progress.progress_snapshot_id,
)


check(
    "state_snapshot_not_mutated",
    state_before
    ==
    state_after,
)

check(
    "progress_snapshot_not_mutated",
    progress_before
    ==
    progress_after,
)


# ============================================================
# 19. PROTOCOL SURFACE
# ============================================================

port = (
    persistence
    .UniversalOrchestrationPersistencePort
)


check(
    "port_is_protocol",
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
        "port_method_present_"
        + method_name,
        hasattr(
            port,
            method_name,
        ),
    )


for forbidden_method in (
    "delete",
    "delete_record",
    "delete_history",

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
        "port_forbidden_method_absent_"
        + forbidden_method,
        not hasattr(
            port,
            forbidden_method,
        ),
    )


# ============================================================
# 20. PROTOCOL METHOD SIGNATURES
# ============================================================

append_sig = inspect.signature(
    port.append_record
)

latest_sig = inspect.signature(
    port.load_latest_record
)

load_sig = inspect.signature(
    port.load_record
)

history_sig = inspect.signature(
    port.list_record_history
)


check(
    "append_signature_has_record",
    "record"
    in append_sig.parameters,
)

check(
    "latest_signature_has_identity",
    "identity_fingerprint"
    in latest_sig.parameters,
)

check(
    "load_signature_has_record_id",
    "persistence_record_id"
    in load_sig.parameters,
)

check(
    "history_signature_has_identity",
    "identity_fingerprint"
    in history_sig.parameters,
)


# ============================================================
# 21. NO 5.1.12 / 5.1.13 STORED DUPLICATION
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
# 22. EXPLANATION CONTRACT
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
    "stored_fields_explanation_exact",
    explanation.get(
        "stored_fields"
    )
    == (
        "state_snapshot",
        "progress_snapshot",
        "previous_record_id",
        "schema_version",
    ),
)

check(
    "state_authority_exact",
    "5.1.3"
    in explanation.get(
        "state_authority",
        "",
    ),
)

check(
    "progress_authority_exact",
    "5.1.11"
    in explanation.get(
        "progress_authority",
        "",
    ),
)

check(
    "derived_decision_rule_mentions_5_1_12",
    "5.1.12"
    in explanation.get(
        "derived_decision_rule",
        "",
    ),
)

check(
    "derived_decision_rule_mentions_5_1_13",
    "5.1.13"
    in explanation.get(
        "derived_decision_rule",
        "",
    ),
)

check(
    "completion_boundary_exact",
    "5.1.15"
    in explanation.get(
        "completion_boundary",
        "",
    ),
)

check(
    "termination_boundary_exact",
    "5.1.16"
    in explanation.get(
        "termination_boundary",
        "",
    ),
)

check(
    "evidence_boundary_exact",
    "5.1.17"
    in explanation.get(
        "evidence_boundary",
        "",
    ),
)


# ============================================================
# 23. REQUIRED PROHIBITIONS
# ============================================================

required_prohibitions = (
    "does not perform filesystem I/O",
    "does not perform database I/O",
    "does not perform network I/O",
    "does not choose a production storage backend",
    "does not import Runtime State Store",
    "does not import Runtime Persistence",
    "does not execute persistence transactions",
    "does not acquire persistence locks",
    "does not perform compare-and-swap",
    "does not update latest pointers",
    "does not delete orchestration history",
    "does not mutate previous persistence records",
    "does not use wall clock",
    "does not generate timestamps",
    "does not serialize external storage payloads",
    "does not deserialize external storage payloads",
    "does not transition orchestration state",
    "does not recompute progress",
    "does not reevaluate conditional branches",
    "does not reevaluate suspension/resume eligibility",
    "does not rerun orchestration recovery",
    "does not determine orchestration completion",
    "does not determine orchestration success",
    "does not determine orchestration failure",
    "does not cancel orchestration",
    "does not terminate orchestration",
    "does not record permanent audit evidence",
    "does not enqueue jobs",
    "does not dequeue jobs",
    "does not assign workers",
    "does not manipulate leases",
    "does not dispatch runtime handlers",
    "does not execute jobs",
    "does not import Universal Coordination Framework",
    "does not invoke pipeline coordinators",
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
# 24. IMPORT BOUNDARY
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
    == [
        "backend.server.runtime.universal_orchestration.state_model",
        "backend.server.runtime.universal_orchestration.progress_tracking",
    ],
    backend_imports,
)


# ============================================================
# 25. FORBIDDEN IMPORTS
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

    "asyncio",
    "threading",
    "multiprocessing",

    "os",
    "subprocess",
    "socket",
    "sqlite3",

    "backend.server.runtime.runtime_state_store",
    "backend.server.runtime.runtime_persistence",

    "backend.server.runtime.universal_queue",
    "backend.server.runtime.universal_worker",

    "backend.server.runtime.universal_runtime_registration",
    "backend.server.runtime.universal_runtime_worker_v1",
    "backend.server.runtime.universal_runtime_infrastructure",

    "backend.server.runtime.universal_orchestration.conditional_branching",
    "backend.server.runtime.universal_orchestration.suspension_resume_eligibility",
    "backend.server.runtime.universal_orchestration.recovery",

    "backend.server.coordination",
    "backend.server.orchestration",

    "backend.server.jobs.universal_knowledge_orchestrator",
    "backend.server.pipelines.connect_domain.coordinator",
):

    matches = tuple(
        imported
        for imported
        in all_imports
        if (
            imported
            == forbidden_module
            or
            imported.startswith(
                forbidden_module
                + "."
            )
        )
    )

    check(
        "forbidden_import_absent_"
        + forbidden_module.replace(
            ".",
            "_"
        ),
        not matches,
        matches,
    )


# ============================================================
# 26. FORBIDDEN CALLS
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
    "remove",

    "sleep",
    "wait",
    "poll",

    "time",
    "time_ns",
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
    "acquire",
    "release",

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
# 27. FORBIDDEN ATTRIBUTES
# ============================================================

attrs = tuple(
    node.attr
    for node
    in ast.walk(
        tree
    )
    if isinstance(
        node,
        ast.Attribute,
    )
)


for forbidden_attr in (
    "created_at",
    "updated_at",
    "timestamp",

    "revision",
    "generation",
    "etag",
    "expected_revision",

    "queue_id",
    "worker_id",
    "lease_id",

    "checkpoint_reference",

    "retry_policy",
    "max_attempts",

    "readiness",
    "handoff",
):

    check(
        "forbidden_attribute_absent_"
        + forbidden_attr,
        forbidden_attr
        not in attrs,
    )


# ============================================================
# 28. NO STORAGE-BACKEND SYMBOLS
# ============================================================

for forbidden_text in (
    "RuntimeStateStore",
    "RuntimePersistence",
    "sqlite3",
    "redis",
    "dynamodb",
    "s3",
    "postgres",
    "mysql",
):

    check(
        "forbidden_symbol_absent_"
        + forbidden_text,
        forbidden_text
        not in source,
    )


# ============================================================
# 29. PROTECTED AUTHORITY MATRIX
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
# 30. FINAL AST
# ============================================================

final_ast = ast_sha(
    PERSISTENCE_PATH
)


check(
    "persistence_ast_final",
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
        "PHASE 5.1.14 — UNIVERSAL ORCHESTRATION "
        "PERSISTENCE INTERFACE ADVERSARIAL REGRESSION"
    ),

    "=" * 118,

    "",

    (
        "ORCHESTRATION PERSISTENCE INTERFACE AST SHA256: "
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
            "ADVERSARIAL ORCHESTRATION PERSISTENCE INTERFACE REGRESSION: "
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

        "5.1.14 AUTHORITY MODIFIED DURING REGRESSION: NO",
        "5.1.1–5.1.13 FROZEN AUTHORITIES MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "CANONICAL STORED FIELDS:",
        "  state_snapshot",
        "  progress_snapshot",
        "  previous_record_id",
        "  schema_version",

        "",

        "ROOT RECORD DETERMINISTIC: YES",
        "STATE-SENSITIVE RECORD ID: YES",
        "PROGRESS-SENSITIVE RECORD ID: YES",
        "PREDECESSOR-SENSITIVE RECORD ID: YES",
        "RUN-SENSITIVE RECORD ID: YES",

        "",

        "APPEND-ONLY LONG CHAIN VALIDATED: YES",
        "SKIPPED PREDECESSOR ACCEPTED: NO",
        "CROSS-RUN SUCCESSOR ACCEPTED: NO",

        "",

        "5.1.12 ELIGIBILITY DUPLICATED: NO",
        "5.1.13 RECOVERY DECISION DUPLICATED: NO",

        "",

        "MANIFEST IMMUTABLE: YES",
        "SOURCE STATE SNAPSHOT MUTATED: NO",
        "SOURCE PROGRESS SNAPSHOT MUTATED: NO",

        "",

        "PORT OPERATIONS:",
        "  append_record",
        "  load_latest_record",
        "  load_record",
        "  list_record_history",

        "",

        "PORT DELETE: NO",
        "PORT UPDATE: NO",
        "PORT OVERWRITE: NO",
        "PORT TRANSACTION EXECUTION: NO",
        "PORT LOCK EXECUTION: NO",
        "PORT COMPARE-AND-SWAP EXECUTION: NO",

        "",

        "RUNTIME STATE STORE IMPORT: NO",
        "RUNTIME PERSISTENCE IMPORT: NO",

        "",

        "FILESYSTEM I/O: NO",
        "DATABASE I/O: NO",
        "NETWORK I/O: NO",

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
            "STATUS: REGRESSION PASS "
            "— FINAL CERTIFICATION REQUIRED"
            if passed == total
            else
            "STATUS: REGRESSION FAILED "
            "— PATCH REQUIRED"
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
        "Phase 5.1.14 adversarial regression failed."
    )
