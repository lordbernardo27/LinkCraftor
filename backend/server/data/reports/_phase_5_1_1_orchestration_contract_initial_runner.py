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
    / "phase_5_1_1_orchestration_contract_initial_implementation.txt"
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
                "5.1.1 initial implementation: "
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


# ============================================================
# CONSTANTS
# ============================================================

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
    "identifier_max_exact",
    contract.MAX_UNIVERSAL_ORCHESTRATION_IDENTIFIER_LENGTH
    == 200,
)

check(
    "job_max_exact",
    contract.MAX_UNIVERSAL_ORCHESTRATION_JOB_IDS
    == 10_000,
)


# ============================================================
# BASIC CONTRACT
# ============================================================

sample = (
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
    "workspace",
    sample.workspace_id
    == "workspace-a",
)

check(
    "pipeline",
    sample.pipeline
    == "semantic_pipeline",
)

check(
    "job_order_canonical",
    sample.job_ids
    == (
        "job-a",
        "job-b",
        "job-c",
    ),
    sample.job_ids,
)

check(
    "job_count",
    sample.job_count
    == 3,
)

check(
    "contains_job_true",
    sample.contains_job(
        "job-b"
    )
    is True,
)

check(
    "contains_job_false",
    sample.contains_job(
        "job-z"
    )
    is False,
)


# ============================================================
# IDENTIFIER NORMALIZATION
# ============================================================

check(
    "identifier_strip",
    contract.normalize_universal_orchestration_identifier(
        "  worker-job-1  ",
        field_name="job_id",
    )
    == "worker-job-1",
)


invalid_identifiers = (
    None,
    True,
    False,
    0,
    1,
    "",
    " ",
    "\t",
    "\n",
    "job id",
    "job\tid",
    "job\nid",
    [],
    {},
    (),
)


for index, bad in enumerate(
    invalid_identifiers,
    start=1,
):

    try:

        contract.normalize_universal_orchestration_identifier(
            bad,
            field_name="job_id",
        )

    except contract.UniversalRuntimeOrchestrationContractError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_identifier_"
        + str(
            index
        ),
        rejected,
        repr(
            bad
        ),
    )


too_long = (
    "x"
    * 201
)


try:

    contract.normalize_universal_orchestration_identifier(
        too_long,
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
    "identifier_too_long",
    rejected,
)


# ============================================================
# JOB COLLECTION
# ============================================================

for bad in (
    None,
    "job-a",
    b"job-a",
    bytearray(
        b"job-a"
    ),
):

    try:

        contract.normalize_universal_orchestration_job_ids(
            bad
        )

    except contract.UniversalRuntimeOrchestrationContractError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_collection_"
        + type(
            bad
        ).__name__,
        rejected,
    )


for empty in (
    (),
    [],
    set(),
):

    try:

        contract.normalize_universal_orchestration_job_ids(
            empty
        )

    except contract.UniversalRuntimeOrchestrationContractError as exc:

        rejected = (
            exc.code
            == "orchestration_job_ids_empty"
        )

    else:

        rejected = False

    check(
        "empty_collection_"
        + type(
            empty
        ).__name__,
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


# ============================================================
# DIRECT CONSTRUCTOR HARDENING
# ============================================================

direct = (
    contract.UniversalRuntimeOrchestrationContract(
        workspace_id=" workspace-a ",
        pipeline=" pipeline-a ",
        job_ids=(
            "job-2",
            "job-1",
        ),
    )
)


check(
    "direct_workspace_canonical",
    direct.workspace_id
    == "workspace-a",
)

check(
    "direct_pipeline_canonical",
    direct.pipeline
    == "pipeline-a",
)

check(
    "direct_jobs_canonical",
    direct.job_ids
    == (
        "job-1",
        "job-2",
    ),
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


# ============================================================
# EXACT FIELD CONTRACT
# ============================================================

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


for forbidden in (
    "orchestration_run_id",
    "run_id",
    "workflow_id",
    "status",
    "state",
    "current_stage",
    "parent_job_id",
    "dependency_job_ids",
    "batch_id",
    "pipeline_run_id",
    "checkpoint_reference",
    "progress",
    "worker_id",
    "assigned_worker_id",
    "lease_id",
    "handler",
    "result",
    "result_reference",
    "artifact_references",
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
        + forbidden,
        forbidden
        not in field_names,
    )


# ============================================================
# IMMUTABILITY
# ============================================================

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


# ============================================================
# DETERMINISM
# ============================================================

variant = (
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
    "deterministic_contract",
    variant
    == sample,
)


# ============================================================
# EXPLANATION
# ============================================================

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
    "coordination_separate",
    "not imported"
    in explanation.get(
        "coordination_boundary",
        "",
    ),
)

check(
    "no_execution",
    "not performed"
    in explanation.get(
        "execution_boundary",
        "",
    ),
)

check(
    "no_persistence",
    "no persistence"
    in explanation.get(
        "persistence_boundary",
        "",
    ),
)


# ============================================================
# IMPORT BOUNDARY
# ============================================================

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


# ============================================================
# API SURFACE
# ============================================================

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
    "api_exact",
    tuple(
        contract.__all__
    )
    == expected_all,
    contract.__all__,
)


# ============================================================
# FORBIDDEN CALLS
# ============================================================

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
    "renew_universal_worker_lease",
    "release_universal_worker_lease",

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


contract_ast = ast_sha(
    CONTRACT_PATH
)


check(
    "contract_ast_generated",
    (
        len(
            contract_ast
        )
        == 64
    ),
    contract_ast,
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
        "ORCHESTRATION CONTRACT INITIAL IMPLEMENTATION"
    ),
    "=" * 118,
    "",
    (
        "ORCHESTRATION CONTRACT AST SHA256: "
        + contract_ast
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
            "INITIAL ORCHESTRATION CONTRACT RESULT: "
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
        "JOBS ENQUEUED/CLAIMED: NO",
        "WORKERS ASSIGNED/LEASED: NO",
        "RUNTIME HANDLERS REGISTERED: NO",
        "RUNTIME HANDLERS DISPATCHED: NO",
        "JOBS EXECUTED: NO",
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
        "Phase 5.1.1 Orchestration Contract initial implementation failed."
    )
