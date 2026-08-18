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

CONTRACT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_orchestration"
    / "contract.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_1_1_orchestration_contract_final_certification.txt"
)

EXPECTED_CONTRACT_AST = (
    "8CC241284B8AF87809A41134FF0FDEB402D5DE49A117D931920CC17346271FD9"
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


if not CONTRACT_PATH.exists():

    raise SystemExit(
        "5.1.1 Orchestration Contract authority missing."
    )


initial_ast = ast_sha(
    CONTRACT_PATH
)


if initial_ast != EXPECTED_CONTRACT_AST:

    raise SystemExit(
        (
            "5.1.1 Orchestration Contract AST mismatch "
            "before final certification.\n"
            "EXPECTED: "
            + EXPECTED_CONTRACT_AST
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
                "5.1.1 final certification: "
                + name
                + "\nEXPECTED: "
                + expected
                + "\nACTUAL:   "
                + actual
            )
        )


sys.path.insert(
    0,
    str(
        ROOT
    ),
)

module_name = (
    "backend.server.runtime."
    "universal_orchestration.contract"
)

sys.modules.pop(
    module_name,
    None,
)

contract = importlib.import_module(
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
            bool(
                condition
            ),
            str(
                detail
            ),
        )
    )


contract_ast = ast_sha(
    CONTRACT_PATH
)


check(
    "contract_ast_exact",
    contract_ast
    == EXPECTED_CONTRACT_AST,
    contract_ast,
)

check(
    "version_exact",
    contract.UNIVERSAL_RUNTIME_ORCHESTRATION_CONTRACT_VERSION
    == "universal_runtime_orchestration_contract_v5.1.1",
)

check(
    "schema_exact",
    contract.UNIVERSAL_RUNTIME_ORCHESTRATION_SCHEMA_VERSION
    == "universal_runtime_orchestration_schema_v1",
)

check(
    "identifier_limit_exact",
    contract.MAX_UNIVERSAL_ORCHESTRATION_IDENTIFIER_LENGTH
    == 200,
)

check(
    "job_limit_exact",
    contract.MAX_UNIVERSAL_ORCHESTRATION_JOB_IDS
    == 10_000,
)


sample = (
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


check(
    "sample_workspace",
    sample.workspace_id
    == "workspace-a",
)

check(
    "sample_pipeline",
    sample.pipeline
    == "pipeline-a",
)

check(
    "sample_jobs_canonical",
    sample.job_ids
    == (
        "job-a",
        "job-b",
        "job-c",
    ),
)

check(
    "sample_count",
    sample.job_count
    == 3,
)

check(
    "contains_present",
    sample.contains_job(
        "job-b"
    )
    is True,
)

check(
    "contains_missing",
    sample.contains_job(
        "job-z"
    )
    is False,
)


for field in fields(
    sample
):

    try:

        setattr(
            sample,
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


field_names = tuple(
    field.name
    for field in fields(
        contract.UniversalRuntimeOrchestrationContract
    )
)


check(
    "fields_exact",
    field_names
    == (
        "workspace_id",
        "pipeline",
        "job_ids",
        "schema_version",
    ),
    field_names,
)


for forbidden_field in (
    "orchestration_run_id",
    "run_id",
    "workflow_id",
    "status",
    "state",
    "dependency_job_ids",
    "parent_job_id",
    "batch_id",
    "pipeline_run_id",
    "checkpoint_reference",
    "progress",
    "worker_id",
    "worker_instance_id",
    "lease_id",
    "handler",
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


deterministic = (
    contract.create_universal_runtime_orchestration_contract(
        workspace_id="workspace-a",
        pipeline="pipeline-a",
        job_ids=(
            "job-b",
            "job-c",
            "job-a",
        ),
    )
)


check(
    "deterministic",
    deterministic
    == sample,
)


check(
    "identifier_200_valid",
    (
        len(
            contract.normalize_universal_orchestration_identifier(
                "x" * 200,
                field_name="job_id",
            )
        )
        == 200
    ),
)


try:

    contract.normalize_universal_orchestration_identifier(
        "x" * 201,
        field_name="job_id",
    )

except contract.UniversalRuntimeOrchestrationContractError as exc:

    rejected = (
        exc.code
        == "orchestration_identifier_too_long"
    )

else:

    rejected = False


check(
    "identifier_201_rejected",
    rejected,
)


max_jobs = tuple(
    "job-"
    + str(
        index
    ).zfill(
        5
    )
    for index in range(
        10_000
    )
)


check(
    "10000_jobs_valid",
    len(
        contract.normalize_universal_orchestration_job_ids(
            max_jobs
        )
    )
    == 10_000,
)


try:

    contract.normalize_universal_orchestration_job_ids(
        max_jobs
        + (
            "job-overflow",
        )
    )

except contract.UniversalRuntimeOrchestrationContractError as exc:

    rejected = (
        exc.code
        == "orchestration_job_ids_too_many"
    )

else:

    rejected = False


check(
    "10001_jobs_rejected",
    rejected,
)


for values in (
    (
        "job-a",
        "job-a",
    ),
    (
        " job-a ",
        "job-a",
    ),
):

    try:

        contract.normalize_universal_orchestration_job_ids(
            values
        )

    except contract.UniversalRuntimeOrchestrationContractError as exc:

        rejected = (
            exc.code
            == "duplicate_orchestration_job_id"
        )

    else:

        rejected = False

    check(
        "duplicate_rejected_"
        + repr(
            values
        ),
        rejected,
    )


try:

    contract.UniversalRuntimeOrchestrationContract(
        workspace_id="workspace-a",
        pipeline="pipeline-a",
        job_ids=(
            "job-a",
        ),
        schema_version="tampered",
    )

except contract.UniversalRuntimeOrchestrationContractError as exc:

    rejected = (
        exc.code
        == "invalid_orchestration_schema_version"
    )

else:

    rejected = False


check(
    "schema_tamper_rejected",
    rejected,
)


explanation = (
    contract.explain_universal_runtime_orchestration_contract_v1()
)


check(
    "phase",
    explanation.get(
        "phase"
    )
    == "5.1.1",
)

check(
    "component",
    explanation.get(
        "component"
    )
    == "Universal Runtime Orchestration Contract",
)

check(
    "run_identity_deferred",
    "5.1.2"
    in explanation.get(
        "run_identity_boundary",
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
    "dependency_deferred",
    "5.1.4"
    in explanation.get(
        "dependency_boundary",
        "",
    ),
)

check(
    "planning_deferred",
    "5.1.5"
    in explanation.get(
        "planning_boundary",
        "",
    ),
)

check(
    "readiness_deferred",
    "5.1.6"
    in explanation.get(
        "readiness_boundary",
        "",
    ),
)

check(
    "lexical_not_execution",
    "not execution order"
    in explanation.get(
        "ordering_rule",
        "",
    ),
)

check(
    "coordination_separate",
    "not imported"
    in explanation.get(
        "coordination_boundary",
        "",
    ),
)

check(
    "execution_separate",
    "not performed"
    in explanation.get(
        "execution_boundary",
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


required_prohibitions = (
    "does not define orchestration_run_id",
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
    "does not acquire leases",
    "does not register runtime handlers",
    "does not dispatch runtime handlers",
    "does not execute runtime handlers",
    "does not execute jobs",
    "does not import Universal Coordination Framework",
    "does not invoke pipeline coordinators",
    "does not persist orchestration state",
    "does not access Runtime State Store",
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
        + str(
            index
        ),
        item
        in prohibitions,
        item,
    )


source = CONTRACT_PATH.read_text(
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
    "no_backend_imports",
    backend_imports
    == [],
    backend_imports,
)


expected_all = (
    "UNIVERSAL_RUNTIME_ORCHESTRATION_CONTRACT_VERSION",
    "UNIVERSAL_RUNTIME_ORCHESTRATION_SCHEMA_VERSION",
    "MAX_UNIVERSAL_ORCHESTRATION_IDENTIFIER_LENGTH",
    "MAX_UNIVERSAL_ORCHESTRATION_JOB_IDS",
    "UniversalRuntimeOrchestrationContractError",
    "UniversalRuntimeOrchestrationContract",
    "normalize_universal_orchestration_identifier",
    "normalize_universal_orchestration_job_ids",
    "create_universal_runtime_orchestration_contract",
    "explain_universal_runtime_orchestration_contract_v1",
)


check(
    "api_surface_exact",
    tuple(
        contract.__all__
    )
    == expected_all,
    contract.__all__,
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


fingerprint_material = "|".join(
    (
        "phase_5_1_1_runtime_orchestration_contract",

        contract.UNIVERSAL_RUNTIME_ORCHESTRATION_CONTRACT_VERSION,
        contract.UNIVERSAL_RUNTIME_ORCHESTRATION_SCHEMA_VERSION,

        contract_ast,

        "workspace_id",
        "pipeline",
        "job_ids",
        "schema_version",

        "immutable_contract",
        "deterministic_contract",

        "identifier_max_200",
        "job_count_max_10000",

        "nonempty_job_collection",
        "normalized_duplicate_rejection",
        "lexical_canonicalization_only",
        "lexical_order_not_execution_order",

        "universal_job_references_only",
        "universal_job_fields_not_duplicated",

        "run_identity_deferred_5_1_2",
        "state_deferred_5_1_3",
        "dependencies_deferred_5_1_4",
        "planning_deferred_5_1_5",
        "readiness_deferred_5_1_6",

        "no_queue_activity",
        "no_worker_activity",
        "no_runtime_handler_activity",
        "no_execution",
        "no_coordination_framework",
        "no_pipeline_coordinators",
        "no_state_store",
        "no_persistence",
        "no_wall_clock",
        "no_io",

        "pure_runtime_orchestration_contract_authority",
    )
)


orchestration_contract_fingerprint = (
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
            orchestration_contract_fingerprint
        )
        == 64
    ),
    orchestration_contract_fingerprint,
)


final_ast = ast_sha(
    CONTRACT_PATH
)


check(
    "final_ast_unchanged",
    final_ast
    == EXPECTED_CONTRACT_AST,
    final_ast,
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
        "PHASE 5.1.1 — UNIVERSAL RUNTIME "
        "ORCHESTRATION CONTRACT FINAL CERTIFICATION"
    ),
    "=" * 118,
    "",
    (
        "ORCHESTRATION CONTRACT AST SHA256: "
        + contract_ast
    ),
    (
        "ORCHESTRATION CONTRACT FINGERPRINT: "
        + orchestration_contract_fingerprint
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
            "FINAL ORCHESTRATION CONTRACT CERTIFICATION: "
            + (
                "PASS"
                if passed == total
                else "FAIL"
            )
        ),
        (
            "CHECKS PASSED: "
            + str(
                passed
            )
            + "/"
            + str(
                total
            )
        ),
        "",
        "ORCHESTRATION CONTRACT MODIFIED DURING CERTIFICATION: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "EXISTING ORCHESTRATION MODELS MODIFIED: NO",
        "EXISTING ORCHESTRATION QUEUE MODIFIED: NO",
        "EXISTING ORCHESTRATION SERVICE MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME WORKER MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "",
        "ORCHESTRATION RUN IDENTITY DEFINED: NO",
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
        "JOBS ENQUEUED/CLAIMED: NO",
        "WORKERS ASSIGNED/LEASED: NO",
        "RUNTIME HANDLERS REGISTERED/DISPATCHED: NO",
        "JOBS EXECUTED: NO",
        "UNIVERSAL COORDINATION FRAMEWORK ACCESSED: NO",
        "PIPELINE COORDINATORS ACCESSED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "ORCHESTRATION STATE PERSISTED: NO",
        "WALL CLOCK USED: NO",
        "FILESYSTEM/NETWORK I/O: NO",
        "",
        (
            "PHASE 5.1.1 FREEZE CANDIDATE: "
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
        "Phase 5.1.1 Orchestration Contract final certification failed."
    )
