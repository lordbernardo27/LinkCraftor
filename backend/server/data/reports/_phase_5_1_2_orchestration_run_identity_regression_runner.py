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

IDENTITY_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_orchestration"
    / "run_identity.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_1_2_orchestration_run_identity_regression.txt"
)

EXPECTED_IDENTITY_AST = (
    "A582564C7D45D96DAB2D6DAF38E8C63B9EA281251F41B02D12DE17F1D68CAFBC"
)


PROTECTED = {
    "5.1.1_orchestration_contract": (
        ROOT / "backend/server/runtime/universal_orchestration/contract.py",
        "8CC241284B8AF87809A41134FF0FDEB402D5DE49A117D931920CC17346271FD9",
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


if not IDENTITY_PATH.exists():

    raise SystemExit(
        "5.1.2 Orchestration Run Identity authority missing."
    )


initial_ast = ast_sha(
    IDENTITY_PATH
)


if initial_ast != EXPECTED_IDENTITY_AST:

    raise SystemExit(
        (
            "5.1.2 Run Identity AST changed before regression.\n"
            "EXPECTED: "
            + EXPECTED_IDENTITY_AST
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
                "5.1.2 adversarial regression: "
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

identity_module_name = (
    "backend.server.runtime."
    "universal_orchestration.run_identity"
)

sys.modules.pop(
    identity_module_name,
    None,
)

identity = importlib.import_module(
    identity_module_name
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
# 1 — AST / CONSTANTS
# ============================================================

check(
    "identity_ast_initial",
    ast_sha(
        IDENTITY_PATH
    )
    == EXPECTED_IDENTITY_AST,
)

check(
    "version_exact",
    identity.UNIVERSAL_ORCHESTRATION_RUN_IDENTITY_VERSION
    == "universal_orchestration_run_identity_v5.1.2",
)

check(
    "schema_exact",
    identity.UNIVERSAL_ORCHESTRATION_RUN_IDENTITY_SCHEMA_VERSION
    == "universal_orchestration_run_identity_schema_v1",
)

check(
    "hash_algorithm_exact",
    identity.UNIVERSAL_ORCHESTRATION_IDENTITY_HASH_ALGORITHM
    == "sha256",
)


# ============================================================
# 2 — CANONICAL CONTRACT FIXTURES
# ============================================================

contract_a = (
    contract.create_universal_runtime_orchestration_contract(
        workspace_id="workspace-a",
        pipeline="semantic_pipeline",
        job_ids=(
            "job-c",
            "job-a",
            "job-b",
        ),
    )
)

contract_a_reordered = (
    contract.create_universal_runtime_orchestration_contract(
        workspace_id="workspace-a",
        pipeline="semantic_pipeline",
        job_ids=(
            "job-b",
            "job-c",
            "job-a",
        ),
    )
)

contract_b = (
    contract.create_universal_runtime_orchestration_contract(
        workspace_id="workspace-b",
        pipeline="semantic_pipeline",
        job_ids=(
            "job-a",
            "job-b",
            "job-c",
        ),
    )
)

contract_c = (
    contract.create_universal_runtime_orchestration_contract(
        workspace_id="workspace-a",
        pipeline="different_pipeline",
        job_ids=(
            "job-a",
            "job-b",
            "job-c",
        ),
    )
)

contract_d = (
    contract.create_universal_runtime_orchestration_contract(
        workspace_id="workspace-a",
        pipeline="semantic_pipeline",
        job_ids=(
            "job-a",
            "job-b",
            "job-x",
        ),
    )
)


check(
    "contract_reorder_equal",
    contract_a
    == contract_a_reordered,
)

check(
    "workspace_difference_contract_differs",
    contract_a
    != contract_b,
)

check(
    "pipeline_difference_contract_differs",
    contract_a
    != contract_c,
)

check(
    "jobs_difference_contract_differs",
    contract_a
    != contract_d,
)


# ============================================================
# 3 — RUN ID TYPE ATTACKS
# ============================================================

invalid_run_ids = (
    None,
    True,
    False,
    0,
    1,
    -1,
    1.0,
    b"run-a",
    bytearray(b"run-a"),
    [],
    {},
    (),
    set(),
    object(),
)


for index, bad in enumerate(
    invalid_run_ids,
    start=1,
):

    try:

        identity.normalize_universal_orchestration_run_id(
            bad
        )

    except identity.UniversalOrchestrationRunIdentityError as exc:

        rejected = (
            exc.code
            == "invalid_orchestration_run_id"
        )

    else:

        rejected = False

    check(
        "invalid_run_id_type_"
        + str(index),
        rejected,
        repr(bad),
    )


# ============================================================
# 4 — WHITESPACE ATTACKS
# ============================================================

for index, bad in enumerate(
    (
        "",
        " ",
        "\t",
        "\n",
        "\r",
        "run id",
        "run\tid",
        "run\nid",
        "run\rid",
        "run\u00a0id",
    ),
    start=1,
):

    try:

        identity.normalize_universal_orchestration_run_id(
            bad
        )

    except identity.UniversalOrchestrationRunIdentityError:

        rejected = True

    else:

        rejected = False

    check(
        "run_id_whitespace_attack_"
        + str(index),
        rejected,
        repr(bad),
    )


# ============================================================
# 5 — SURROUNDING WHITESPACE NORMALIZATION
# ============================================================

for index, (
    raw,
    expected,
) in enumerate(
    (
        (
            " run-a ",
            "run-a",
        ),
        (
            "\trun-a\t",
            "run-a",
        ),
        (
            "\nrun-a\n",
            "run-a",
        ),
    ),
    start=1,
):

    check(
        "run_id_trim_"
        + str(index),
        identity.normalize_universal_orchestration_run_id(
            raw
        )
        == expected,
    )


# ============================================================
# 6 — LENGTH BOUNDARIES
# ============================================================

check(
    "run_id_length_1_valid",
    identity.normalize_universal_orchestration_run_id(
        "r"
    )
    == "r",
)

check(
    "run_id_length_200_valid",
    len(
        identity.normalize_universal_orchestration_run_id(
            "r" * 200
        )
    )
    == 200,
)


for length in (
    201,
    500,
    10_000,
):

    try:

        identity.normalize_universal_orchestration_run_id(
            "r" * length
        )

    except identity.UniversalOrchestrationRunIdentityError as exc:

        rejected = (
            exc.code
            == "orchestration_run_id_too_long"
        )

    else:

        rejected = False

    check(
        "run_id_overflow_"
        + str(length),
        rejected,
    )


# ============================================================
# 7 — CONTRACT TYPE SPOOFING
# ============================================================

for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        1,
        "",
        "contract",
        [],
        {},
        (),
        set(),
        object(),
    ),
    start=1,
):

    try:

        identity.create_universal_orchestration_run_identity(
            orchestration_run_id="run-a",
            contract=bad,
        )

    except identity.UniversalOrchestrationRunIdentityError as exc:

        rejected = (
            exc.code
            == "invalid_orchestration_run_contract"
        )

    else:

        rejected = False

    check(
        "contract_spoof_"
        + str(index),
        rejected,
        repr(bad),
    )


# ============================================================
# 8 — DIRECT CONSTRUCTOR HARDENING
# ============================================================

for index, bad_run_id in enumerate(
    (
        None,
        True,
        False,
        0,
        "",
        " ",
        "run id",
    ),
    start=1,
):

    try:

        identity.UniversalOrchestrationRunIdentity(
            orchestration_run_id=bad_run_id,
            contract=contract_a,
        )

    except identity.UniversalOrchestrationRunIdentityError:

        rejected = True

    else:

        rejected = False

    check(
        "direct_run_id_attack_"
        + str(index),
        rejected,
    )


for index, bad_contract in enumerate(
    (
        None,
        True,
        0,
        "",
        {},
        object(),
    ),
    start=1,
):

    try:

        identity.UniversalOrchestrationRunIdentity(
            orchestration_run_id="run-a",
            contract=bad_contract,
        )

    except identity.UniversalOrchestrationRunIdentityError as exc:

        rejected = (
            exc.code
            == "invalid_orchestration_run_contract"
        )

    else:

        rejected = False

    check(
        "direct_contract_attack_"
        + str(index),
        rejected,
    )


# ============================================================
# 9 — SCHEMA FORGERY
# ============================================================

for bad_schema in (
    "",
    " ",
    "v1",
    "wrong",
    "universal_orchestration_run_identity_schema_v2",
):

    try:

        identity.UniversalOrchestrationRunIdentity(
            orchestration_run_id="run-a",
            contract=contract_a,
            schema_version=bad_schema,
        )

    except identity.UniversalOrchestrationRunIdentityError as exc:

        rejected = (
            exc.code
            == "invalid_orchestration_run_identity_schema_version"
        )

    else:

        rejected = False

    check(
        "schema_attack_"
        + repr(bad_schema),
        rejected,
    )


# ============================================================
# 10 — CONTRACT FINGERPRINT DETERMINISM
# ============================================================

contract_fp_a = (
    identity.calculate_universal_orchestration_contract_fingerprint(
        contract_a
    )
)

contract_fp_a_again = (
    identity.calculate_universal_orchestration_contract_fingerprint(
        contract_a_reordered
    )
)


check(
    "contract_fp_length",
    len(
        contract_fp_a
    )
    == 64,
)

check(
    "contract_fp_upper_hex",
    all(
        character
        in "0123456789ABCDEF"
        for character in contract_fp_a
    ),
)

check(
    "contract_fp_reorder_stable",
    contract_fp_a
    == contract_fp_a_again,
)


for index, candidate in enumerate(
    (
        contract_b,
        contract_c,
        contract_d,
    ),
    start=1,
):

    check(
        "contract_fp_change_"
        + str(index),
        identity.calculate_universal_orchestration_contract_fingerprint(
            candidate
        )
        != contract_fp_a,
    )


# ============================================================
# 11 — CONTRACT FP TYPE ATTACKS
# ============================================================

for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        "",
        [],
        {},
        object(),
    ),
    start=1,
):

    try:

        identity.calculate_universal_orchestration_contract_fingerprint(
            bad
        )

    except identity.UniversalOrchestrationRunIdentityError as exc:

        rejected = (
            exc.code
            == "invalid_orchestration_run_contract"
        )

    else:

        rejected = False

    check(
        "contract_fp_type_attack_"
        + str(index),
        rejected,
    )


# ============================================================
# 12 — RUN IDENTITY FP DETERMINISM
# ============================================================

run_a = (
    identity.create_universal_orchestration_run_identity(
        orchestration_run_id="run-a",
        contract=contract_a,
    )
)

run_a_reordered = (
    identity.create_universal_orchestration_run_identity(
        orchestration_run_id=" run-a ",
        contract=contract_a_reordered,
    )
)


check(
    "run_identity_equal_after_normalization",
    run_a
    == run_a_reordered,
)

check(
    "run_identity_fp_stable",
    run_a.identity_fingerprint
    == run_a_reordered.identity_fingerprint,
)

check(
    "contract_fp_property_stable",
    run_a.contract_fingerprint
    == contract_fp_a,
)


# ============================================================
# 13 — RUN ID CHANGES IDENTITY
# ============================================================

for other_run_id in (
    "run-b",
    "run-c",
    "run-001",
    "RUN-A",
):

    other = (
        identity.create_universal_orchestration_run_identity(
            orchestration_run_id=other_run_id,
            contract=contract_a,
        )
    )

    check(
        "run_id_changes_identity_"
        + other_run_id,
        other.identity_fingerprint
        != run_a.identity_fingerprint,
    )


# ============================================================
# 14 — CONTRACT CHANGES IDENTITY
# ============================================================

for index, other_contract in enumerate(
    (
        contract_b,
        contract_c,
        contract_d,
    ),
    start=1,
):

    other = (
        identity.create_universal_orchestration_run_identity(
            orchestration_run_id="run-a",
            contract=other_contract,
        )
    )

    check(
        "contract_changes_identity_"
        + str(index),
        other.identity_fingerprint
        != run_a.identity_fingerprint,
    )


# ============================================================
# 15 — SAME CONTRACT MAY HAVE MANY RUNS
# ============================================================

runs = tuple(
    identity.create_universal_orchestration_run_identity(
        orchestration_run_id=(
            "run-"
            + str(index)
        ),
        contract=contract_a,
    )
    for index in range(
        1,
        101,
    )
)


check(
    "hundred_runs_same_contract",
    len(
        runs
    )
    == 100,
)

check(
    "hundred_run_ids_unique",
    len(
        {
            item.orchestration_run_id
            for item in runs
        }
    )
    == 100,
)

check(
    "hundred_identity_fps_unique",
    len(
        {
            item.identity_fingerprint
            for item in runs
        }
    )
    == 100,
)

check(
    "hundred_contract_fps_same",
    len(
        {
            item.contract_fingerprint
            for item in runs
        }
    )
    == 1,
)


# ============================================================
# 16 — CASE SENSITIVITY
# ============================================================

lower = (
    identity.create_universal_orchestration_run_identity(
        orchestration_run_id="run-a",
        contract=contract_a,
    )
)

upper = (
    identity.create_universal_orchestration_run_identity(
        orchestration_run_id="RUN-A",
        contract=contract_a,
    )
)


check(
    "run_id_case_preserved_lower",
    lower.orchestration_run_id
    == "run-a",
)

check(
    "run_id_case_preserved_upper",
    upper.orchestration_run_id
    == "RUN-A",
)

check(
    "run_id_case_distinct_identity",
    lower.identity_fingerprint
    != upper.identity_fingerprint,
)


# ============================================================
# 17 — DERIVED FIELDS EXACT
# ============================================================

check(
    "workspace_derived_exact",
    run_a.workspace_id
    == contract_a.workspace_id,
)

check(
    "pipeline_derived_exact",
    run_a.pipeline
    == contract_a.pipeline,
)

check(
    "job_ids_derived_exact",
    run_a.job_ids
    == contract_a.job_ids,
)

check(
    "job_count_derived_exact",
    run_a.job_count
    == contract_a.job_count,
)


# ============================================================
# 18 — EXACT STORED FIELD CONTRACT
# ============================================================

field_names = tuple(
    field.name
    for field in fields(
        identity.UniversalOrchestrationRunIdentity
    )
)


check(
    "fields_exact",
    field_names
    == (
        "orchestration_run_id",
        "contract",
        "schema_version",
    ),
    field_names,
)


for forbidden_field in (
    "workspace_id",
    "pipeline",
    "job_ids",
    "job_count",
    "contract_fingerprint",
    "identity_fingerprint",

    "job_id",
    "pipeline_run_id",
    "batch_id",

    "workflow_id",
    "correlation_id",

    "run_id",
    "execution_id",
    "request_id",

    "status",
    "state",
    "current_stage",

    "dependency_job_ids",
    "parent_job_id",

    "progress",
    "checkpoint_reference",

    "worker_id",
    "worker_instance_id",
    "lease_id",

    "handler",
    "result",
    "result_reference",

    "created_at",
    "updated_at",
    "started_at",
    "completed_at",

    "metadata",
):

    check(
        "forbidden_field_"
        + forbidden_field,
        forbidden_field
        not in field_names,
    )


# ============================================================
# 19 — IMMUTABILITY
# ============================================================

for field in fields(
    run_a
):

    try:

        setattr(
            run_a,
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
# 20 — FINGERPRINT PROPERTIES ARE NOT STORED/FORGEABLE
# ============================================================

check(
    "contract_fp_not_stored",
    "contract_fingerprint"
    not in field_names,
)

check(
    "identity_fp_not_stored",
    "identity_fingerprint"
    not in field_names,
)


try:

    setattr(
        run_a,
        "identity_fingerprint",
        "0" * 64,
    )

except Exception:

    forged_identity_fp = False

else:

    forged_identity_fp = True


check(
    "identity_fp_not_forgeable",
    forged_identity_fp
    is False,
)


try:

    setattr(
        run_a,
        "contract_fingerprint",
        "0" * 64,
    )

except Exception:

    forged_contract_fp = False

else:

    forged_contract_fp = True


check(
    "contract_fp_not_forgeable",
    forged_contract_fp
    is False,
)


# ============================================================
# 21 — EXPLANATION BOUNDARIES
# ============================================================

explanation = (
    identity.explain_universal_orchestration_run_identity_v1()
)


check(
    "phase_exact",
    explanation.get(
        "phase"
    )
    == "5.1.2",
)

check(
    "component_exact",
    explanation.get(
        "component"
    )
    == "Universal Orchestration Run Identity",
)

check(
    "caller_supplied_rule",
    "caller-supplied"
    in explanation.get(
        "identity_rule",
        "",
    ),
)

check(
    "no_generation_rule",
    "does not generate"
    in explanation.get(
        "generation_rule",
        "",
    ),
)

check(
    "uuid_absent_rule",
    "UUIDs"
    in explanation.get(
        "generation_rule",
        "",
    ),
)

check(
    "contract_binding_rule",
    "5.1.1"
    in explanation.get(
        "contract_binding_rule",
        "",
    ),
)

check(
    "multiple_runs_rule",
    "multiple"
    in explanation.get(
        "multiple_run_rule",
        "",
    ),
)

check(
    "pipeline_run_separate",
    "not the"
    in explanation.get(
        "pipeline_run_boundary",
        "",
    ),
)

check(
    "batch_separate",
    "not orchestration_run_id"
    in explanation.get(
        "batch_boundary",
        "",
    ),
)

check(
    "job_separate",
    "not"
    in explanation.get(
        "job_boundary",
        "",
    ),
)

check(
    "workflow_separate",
    "not"
    in explanation.get(
        "workflow_boundary",
        "",
    ),
)

check(
    "correlation_separate",
    "separate"
    in explanation.get(
        "correlation_boundary",
        "",
    ),
)

check(
    "state_deferred",
    "5.1.3"
    in explanation.get(
        "state_boundary",
        "",
    ),
)

check(
    "persistence_separate",
    "no persistence"
    in explanation.get(
        "persistence_boundary",
        "",
    ),
)

check(
    "execution_separate",
    "no queue"
    in explanation.get(
        "execution_boundary",
        "",
    ),
)


# ============================================================
# 22 — PROHIBITION MATRIX
# ============================================================

required_prohibitions = (
    "does not generate orchestration_run_id",
    "does not use UUID generation",
    "does not use randomness",
    "does not use timestamps for identity",
    "does not use wall clock",
    "does not use counters for identity",
    "does not use storage for identity generation",
    "does not redefine Universal Job job_id",
    "does not redefine Universal Job pipeline_run_id",
    "does not redefine Universal Job batch_id",
    "does not redefine Coordination workflow_id",
    "does not redefine Coordination correlation_id",
    "does not define orchestration lifecycle state",
    "does not transition orchestration state",
    "does not resolve dependencies",
    "does not determine execution order",
    "does not determine readiness",
    "does not perform fan-out",
    "does not perform fan-in",
    "does not evaluate conditional branches",
    "does not perform runtime handoffs",
    "does not track orchestration progress",
    "does not restore checkpoints",
    "does not perform orchestration recovery",
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
    "does not persist orchestration identity",
    "does not access Runtime State Store",
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
# 23 — IMPORT BOUNDARY
# ============================================================

source = IDENTITY_PATH.read_text(
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
        "backend.server.runtime.universal_orchestration.contract",
    ],
    backend_imports,
)


# ============================================================
# 24 — FORBIDDEN IMPORTS
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
    "uuid",
    "random",
    "time",
    "datetime",

    "backend.server.runtime.universal_jobs",
    "backend.server.runtime.universal_worker",
    "backend.server.runtime.universal_queue",
    "backend.server.runtime.universal_runtime_registration",
    "backend.server.runtime.runtime_state_store",

    "backend.server.orchestration",
    "backend.server.coordination",

    "backend.server.jobs.universal_knowledge_orchestrator",
    "backend.server.pipelines.connect_domain.coordinator",
):

    matches = tuple(
        item
        for item in all_imports
        if (
            item
            == forbidden_module
            or
            item.startswith(
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
# 25 — API SURFACE
# ============================================================

expected_all = (
    "UNIVERSAL_ORCHESTRATION_RUN_IDENTITY_VERSION",
    "UNIVERSAL_ORCHESTRATION_RUN_IDENTITY_SCHEMA_VERSION",
    "UNIVERSAL_ORCHESTRATION_IDENTITY_HASH_ALGORITHM",
    "UniversalOrchestrationRunIdentityError",
    "UniversalOrchestrationRunIdentity",
    "normalize_universal_orchestration_run_id",
    "calculate_universal_orchestration_contract_fingerprint",
    "calculate_universal_orchestration_run_identity_fingerprint",
    "create_universal_orchestration_run_identity",
    "explain_universal_orchestration_run_identity_v1",
)


check(
    "api_surface_exact",
    tuple(
        identity.__all__
    )
    == expected_all,
    identity.__all__,
)


# ============================================================
# 26 — FORBIDDEN CALLS
# ============================================================

forbidden_calls = {
    "uuid4",
    "uuid5",
    "random",
    "randint",
    "choice",
    "time",
    "time_ns",
    "now",
    "utcnow",

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
# 27 — NO RESPONSIBILITY BLEED
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
    "transition",
    "state_model",
    "dependency_resol",
    "execution_plan",
    "readiness",
    "fan_out",
    "fan_in",
    "branch",
    "handoff",
    "progress",
    "resume",
    "recover",
    "complete",
    "cancel",
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
# 28 — NO HIDDEN POLICY FIELDS
# ============================================================

source_lower = source.lower()


for forbidden_symbol in (
    "pipeline_run_id:",
    "batch_id:",
    "job_id:",
    "workflow_id:",
    "correlation_id:",
    "execution_id:",
    "request_id:",
    "status:",
    "state:",
    "dependency_job_ids:",
    "parent_job_id:",
    "progress:",
    "checkpoint_reference:",
    "worker_id:",
    "lease_id:",
    "handler:",
    "created_at:",
    "updated_at:",
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
# 29 — PROTECTED AUTHORITY MATRIX
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
# 30 — FINAL AST
# ============================================================

final_ast = ast_sha(
    IDENTITY_PATH
)


check(
    "identity_ast_final",
    final_ast
    == EXPECTED_IDENTITY_AST,
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
        "PHASE 5.1.2 — UNIVERSAL ORCHESTRATION "
        "RUN IDENTITY ADVERSARIAL REGRESSION"
    ),
    "=" * 118,
    "",
    (
        "ORCHESTRATION RUN IDENTITY AST SHA256: "
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
            "ADVERSARIAL ORCHESTRATION RUN IDENTITY REGRESSION: "
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
        "ORCHESTRATION RUN IDENTITY AST MODIFIED: NO",
        "5.1.1 ORCHESTRATION CONTRACT MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "EXISTING ORCHESTRATION AUTHORITIES MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME WORKER MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "",
        "ORCHESTRATION RUN ID GENERATED INTERNALLY: NO",
        "UUID/RANDOMNESS USED: NO",
        "TIMESTAMP/WALL CLOCK USED FOR IDENTITY: NO",
        "GLOBAL COUNTER USED FOR IDENTITY: NO",
        "STORAGE USED FOR IDENTITY GENERATION: NO",
        "PIPELINE_RUN_ID REDEFINED: NO",
        "BATCH_ID REDEFINED: NO",
        "JOB_ID REDEFINED: NO",
        "WORKFLOW_ID REDEFINED: NO",
        "CORRELATION_ID REDEFINED: NO",
        "ORCHESTRATION STATE DEFINED: NO",
        "DEPENDENCY RESOLUTION PERFORMED: NO",
        "EXECUTION ORDER DEFINED: NO",
        "READINESS EVALUATED: NO",
        "FAN-OUT/FAN-IN PERFORMED: NO",
        "CONDITIONAL BRANCHING PERFORMED: NO",
        "RUNTIME HANDOFF PERFORMED: NO",
        "ORCHESTRATION PROGRESS TRACKED: NO",
        "CHECKPOINT RESTORATION PERFORMED: NO",
        "ORCHESTRATION RECOVERY PERFORMED: NO",
        "COMPLETION/CANCELLATION RESOLVED: NO",
        "QUEUE/WORKER ACTIVITY: NO",
        "RUNTIME HANDLER ACTIVITY: NO",
        "JOB EXECUTION: NO",
        "UNIVERSAL COORDINATION FRAMEWORK ACCESSED: NO",
        "PIPELINE COORDINATORS ACCESSED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "IDENTITY PERSISTED: NO",
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
            "Phase 5.1.2 Orchestration Run Identity "
            "adversarial regression failed."
        )
    )
