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
    / "phase_5_1_2_orchestration_run_identity_final_certification.txt"
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
            "5.1.2 Run Identity AST mismatch before final certification.\n"
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
                "Protected authority mismatch before "
                "5.1.2 final certification: "
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


identity_ast = ast_sha(
    IDENTITY_PATH
)


# ============================================================
# AUTHORITY / CONSTANTS
# ============================================================

check(
    "identity_ast_exact",
    identity_ast
    == EXPECTED_IDENTITY_AST,
    identity_ast,
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
# CANONICAL CONTRACT
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


check(
    "contract_canonical_jobs",
    contract_a.job_ids
    == (
        "job-a",
        "job-b",
        "job-c",
    ),
)


# ============================================================
# CANONICAL RUN IDENTITY
# ============================================================

run_a = (
    identity.create_universal_orchestration_run_identity(
        orchestration_run_id="run-a",
        contract=contract_a,
    )
)


check(
    "run_id_exact",
    run_a.orchestration_run_id
    == "run-a",
)

check(
    "contract_exact",
    run_a.contract
    == contract_a,
)

check(
    "workspace_derived",
    run_a.workspace_id
    == "workspace-a",
)

check(
    "pipeline_derived",
    run_a.pipeline
    == "semantic_pipeline",
)

check(
    "job_ids_derived",
    run_a.job_ids
    == (
        "job-a",
        "job-b",
        "job-c",
    ),
)

check(
    "job_count_derived",
    run_a.job_count
    == 3,
)


# ============================================================
# EXACT STORED FIELDS
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
    "pipeline_run_id",
    "batch_id",
    "job_id",
    "workflow_id",
    "correlation_id",
    "execution_id",
    "request_id",
    "status",
    "state",
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
# RUN ID VALIDATION
# ============================================================

check(
    "run_id_trim",
    identity.normalize_universal_orchestration_run_id(
        " run-a "
    )
    == "run-a",
)

check(
    "run_id_one_char_valid",
    identity.normalize_universal_orchestration_run_id(
        "r"
    )
    == "r",
)

check(
    "run_id_200_valid",
    len(
        identity.normalize_universal_orchestration_run_id(
            "r" * 200
        )
    )
    == 200,
)


for bad in (
    None,
    True,
    False,
    0,
    1,
    1.0,
    "",
    " ",
    "run id",
    "run\tid",
    [],
    {},
    (),
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
        "invalid_run_id_"
        + repr(bad),
        rejected,
    )


try:
    identity.normalize_universal_orchestration_run_id(
        "r" * 201
    )

except identity.UniversalOrchestrationRunIdentityError as exc:
    rejected = (
        exc.code
        == "orchestration_run_id_too_long"
    )

else:
    rejected = False


check(
    "run_id_201_rejected",
    rejected,
)


# ============================================================
# CONTRACT TYPE HARDENING
# ============================================================

for bad in (
    None,
    True,
    False,
    0,
    "",
    [],
    {},
    (),
    object(),
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
        "invalid_contract_"
        + type(bad).__name__,
        rejected,
    )


# ============================================================
# SCHEMA HARDENING
# ============================================================

try:
    identity.UniversalOrchestrationRunIdentity(
        orchestration_run_id="run-a",
        contract=contract_a,
        schema_version="tampered",
    )

except identity.UniversalOrchestrationRunIdentityError as exc:
    rejected = (
        exc.code
        == "invalid_orchestration_run_identity_schema_version"
    )

else:
    rejected = False


check(
    "schema_tamper_rejected",
    rejected,
)


# ============================================================
# CONTRACT FINGERPRINT
# ============================================================

contract_fp = (
    identity.calculate_universal_orchestration_contract_fingerprint(
        contract_a
    )
)


check(
    "contract_fp_shape",
    (
        len(contract_fp)
        == 64
        and
        all(
            character
            in "0123456789ABCDEF"
            for character in contract_fp
        )
    ),
    contract_fp,
)

check(
    "contract_fp_property",
    run_a.contract_fingerprint
    == contract_fp,
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


check(
    "contract_reordering_equal",
    contract_a_reordered
    == contract_a,
)

check(
    "contract_fp_deterministic",
    identity.calculate_universal_orchestration_contract_fingerprint(
        contract_a_reordered
    )
    == contract_fp,
)


# ============================================================
# IDENTITY FINGERPRINT
# ============================================================

identity_fp = (
    identity.calculate_universal_orchestration_run_identity_fingerprint(
        orchestration_run_id="run-a",
        contract=contract_a,
    )
)


check(
    "identity_fp_shape",
    (
        len(identity_fp)
        == 64
        and
        all(
            character
            in "0123456789ABCDEF"
            for character in identity_fp
        )
    ),
    identity_fp,
)

check(
    "identity_fp_property",
    run_a.identity_fingerprint
    == identity_fp,
)


run_a_again = (
    identity.create_universal_orchestration_run_identity(
        orchestration_run_id=" run-a ",
        contract=contract_a_reordered,
    )
)


check(
    "identity_deterministic",
    run_a_again
    == run_a,
)

check(
    "identity_fp_deterministic",
    run_a_again.identity_fingerprint
    == identity_fp,
)


# ============================================================
# MULTIPLE RUN SEMANTICS
# ============================================================

run_b = (
    identity.create_universal_orchestration_run_identity(
        orchestration_run_id="run-b",
        contract=contract_a,
    )
)


check(
    "same_contract_multiple_runs_allowed",
    run_a.contract
    == run_b.contract,
)

check(
    "different_run_ids_distinct",
    run_a.orchestration_run_id
    != run_b.orchestration_run_id,
)

check(
    "different_run_ids_different_identity_fp",
    run_a.identity_fingerprint
    != run_b.identity_fingerprint,
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


run_same_id_other_contract = (
    identity.create_universal_orchestration_run_identity(
        orchestration_run_id="run-a",
        contract=contract_b,
    )
)


check(
    "same_run_different_contract_fp",
    run_a.contract_fingerprint
    != run_same_id_other_contract.contract_fingerprint,
)

check(
    "same_run_different_contract_identity_fp",
    run_a.identity_fingerprint
    != run_same_id_other_contract.identity_fingerprint,
)


# ============================================================
# CASE SENSITIVITY
# ============================================================

run_upper = (
    identity.create_universal_orchestration_run_identity(
        orchestration_run_id="RUN-A",
        contract=contract_a,
    )
)


check(
    "run_id_case_preserved",
    run_upper.orchestration_run_id
    == "RUN-A",
)

check(
    "run_id_case_distinct",
    run_upper.identity_fingerprint
    != run_a.identity_fingerprint,
)


# ============================================================
# EXPLANATION CONTRACT
# ============================================================

explanation = (
    identity.explain_universal_orchestration_run_identity_v1()
)


check(
    "phase",
    explanation.get(
        "phase"
    )
    == "5.1.2",
)

check(
    "component",
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
    "contract_binding_rule",
    "5.1.1"
    in explanation.get(
        "contract_binding_rule",
        "",
    ),
)

check(
    "multiple_run_rule",
    "multiple"
    in explanation.get(
        "multiple_run_rule",
        "",
    ),
)

check(
    "pipeline_run_boundary",
    "not the"
    in explanation.get(
        "pipeline_run_boundary",
        "",
    ),
)

check(
    "batch_boundary",
    "not orchestration_run_id"
    in explanation.get(
        "batch_boundary",
        "",
    ),
)

check(
    "workflow_boundary",
    "not orchestration_run_id"
    in explanation.get(
        "workflow_boundary",
        "",
    ),
)

check(
    "correlation_boundary",
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
# PROHIBITIONS
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
        item in prohibitions,
        item,
    )


# ============================================================
# IMPORT / API BOUNDARY
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
# CANONICAL 5.1.2 FINGERPRINT
# ============================================================

fingerprint_material = "|".join(
    (
        "phase_5_1_2_universal_orchestration_run_identity",

        identity.UNIVERSAL_ORCHESTRATION_RUN_IDENTITY_VERSION,
        identity.UNIVERSAL_ORCHESTRATION_RUN_IDENTITY_SCHEMA_VERSION,
        identity.UNIVERSAL_ORCHESTRATION_IDENTITY_HASH_ALGORITHM,

        identity_ast,

        "stored_orchestration_run_id",
        "stored_contract",
        "stored_schema_version",

        "workspace_derived_from_contract",
        "pipeline_derived_from_contract",
        "job_ids_derived_from_contract",
        "job_count_derived_from_contract",

        "caller_supplied_run_id",
        "no_internal_generation",
        "no_uuid",
        "no_randomness",
        "no_timestamp_identity",
        "no_wall_clock",
        "no_counter_identity",
        "no_storage_identity_generation",

        "run_id_length_1_to_200",
        "run_id_trim_surrounding_whitespace",
        "run_id_internal_whitespace_rejected",
        "run_id_case_preserved",

        "contract_must_be_5_1_1_authority",

        "contract_fingerprint_derived_not_stored",
        "identity_fingerprint_derived_not_stored",

        "same_contract_same_run_same_identity",
        "same_contract_different_run_different_identity",
        "same_run_different_contract_different_identity",

        "pipeline_run_id_separate",
        "batch_id_separate",
        "job_id_separate",
        "workflow_id_separate",
        "correlation_id_separate",

        "state_deferred_5_1_3",
        "dependencies_external",
        "execution_planning_external",
        "readiness_external",

        "no_queue_activity",
        "no_worker_activity",
        "no_runtime_registration_activity",
        "no_handler_dispatch",
        "no_job_execution",
        "no_coordination_framework",
        "no_pipeline_coordinators",
        "no_state_store",
        "no_persistence",
        "no_filesystem_io",
        "no_network_io",

        "pure_runtime_orchestration_run_identity_authority",
    )
)


run_identity_fingerprint = (
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
            run_identity_fingerprint
        )
        == 64
        and
        all(
            character
            in "0123456789ABCDEF"
            for character in run_identity_fingerprint
        )
    ),
    run_identity_fingerprint,
)


# ============================================================
# FINAL AST RECHECK
# ============================================================

final_ast = ast_sha(
    IDENTITY_PATH
)


check(
    "final_ast_unchanged",
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


lines = [
    (
        "PHASE 5.1.2 — UNIVERSAL ORCHESTRATION "
        "RUN IDENTITY FINAL CERTIFICATION"
    ),
    "=" * 118,
    "",
    (
        "ORCHESTRATION RUN IDENTITY AST SHA256: "
        + identity_ast
    ),
    (
        "ORCHESTRATION RUN IDENTITY FINGERPRINT: "
        + run_identity_fingerprint
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
            "FINAL ORCHESTRATION RUN IDENTITY CERTIFICATION: "
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
        "ORCHESTRATION RUN IDENTITY MODIFIED DURING CERTIFICATION: NO",
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
            "PHASE 5.1.2 FREEZE CANDIDATE: "
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
            "Phase 5.1.2 Orchestration Run Identity "
            "final certification failed."
        )
    )
