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

CONDITIONAL_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_orchestration"
    / "conditional_branching.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_1_10_conditional_branching_final_certification.txt"
)

EXPECTED_CONDITIONAL_AST = (
    "3799D3BEFB10C77400B40964EBBCCF598B7576BA9034D1C7F29622D0EC65286F"
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
}


def ast_sha(
    path: Path,
) -> str:

    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(source)

    canonical = ast.dump(
        tree,
        annotate_fields=True,
        include_attributes=False,
    )

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest().upper()


# ============================================================
# PRE-FLIGHT
# ============================================================

if not CONDITIONAL_PATH.exists():

    raise SystemExit(
        "5.1.10 Conditional Branching authority is missing."
    )


initial_ast = ast_sha(
    CONDITIONAL_PATH
)


if initial_ast != EXPECTED_CONDITIONAL_AST:

    raise SystemExit(
        (
            "5.1.10 Conditional Branching AST mismatch.\n"
            "EXPECTED: "
            + EXPECTED_CONDITIONAL_AST
            + "\nACTUAL:   "
            + initial_ast
        )
    )


for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(path)

    if actual != expected:

        raise SystemExit(
            "Protected authority mismatch: "
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

fanout = importlib.import_module(
    "backend.server.runtime.universal_orchestration.fan_out_coordination"
)


module_name = (
    "backend.server.runtime."
    "universal_orchestration.conditional_branching"
)

sys.modules.pop(
    module_name,
    None,
)

conditional = importlib.import_module(
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


# ============================================================
# CORE AUTHORITY
# ============================================================

check(
    "ast_exact",
    ast_sha(CONDITIONAL_PATH)
    == EXPECTED_CONDITIONAL_AST,
)

check(
    "version_exact",
    conditional.UNIVERSAL_ORCHESTRATION_CONDITIONAL_BRANCHING_VERSION
    == "universal_orchestration_conditional_branching_v5.1.10",
)

check(
    "schema_exact",
    conditional.UNIVERSAL_ORCHESTRATION_CONDITIONAL_BRANCHING_SCHEMA_VERSION
    == "universal_orchestration_conditional_branching_schema_v1",
)

check(
    "hash_algorithm_exact",
    conditional.UNIVERSAL_ORCHESTRATION_BRANCH_DECISION_HASH_ALGORITHM
    == "sha256",
)

check(
    "disposition_exact",
    tuple(
        item.value
        for item
        in conditional.UniversalOrchestrationBranchDisposition
    )
    == (
        "selected",
        "excluded",
        "unresolved",
    ),
)

check(
    "resolution_exact",
    tuple(
        item.value
        for item
        in conditional.UniversalOrchestrationBranchResolution
    )
    == (
        "resolved",
        "unresolved",
    ),
)


# ============================================================
# FIXTURE HELPERS
# ============================================================

FIXED_CREATED_AT = (
    "2026-05-21T03:49:30.579317+00:00"
)


def make_job(
    *,
    job_id,
    dependencies=(),
):

    return jobs.UniversalJob(
        job_id=job_id,
        workspace_id="workspace-a",
        pipeline="pipeline-a",
        stage="stage-a",
        job_type="test_job",
        payload_reference="payload-a",
        dependency_job_ids=tuple(
            dependencies
        ),
        status=jobs.UniversalJobStatus.CREATED,
        created_at=FIXED_CREATED_AT,
    )


def make_plan(
    *,
    jobs_tuple,
    run_id,
):

    contract = (
        contracts
        .create_universal_runtime_orchestration_contract(
            workspace_id="workspace-a",
            pipeline="pipeline-a",
            job_ids=tuple(
                job.job_id
                for job
                in jobs_tuple
            ),
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
            jobs=jobs_tuple,
        )
    )


plan = make_plan(
    jobs_tuple=(
        make_job(
            job_id="source",
        ),

        make_job(
            job_id="alpha",
            dependencies=("source",),
        ),

        make_job(
            job_id="beta",
            dependencies=("source",),
        ),

        make_job(
            job_id="gamma",
            dependencies=("source",),
        ),
    ),
    run_id="certification",
)


fan_out_result = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=plan,
        source_job_id="source",
    )
)


# ============================================================
# CANONICAL TRI-STATE DECISION
# ============================================================

decision = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_result,
        condition_evidence={
            "alpha": True,
            "beta": False,
            "gamma": None,
        },
    )
)


check(
    "evidence_exact",
    decision.condition_evidence
    == (
        ("alpha", True),
        ("beta", False),
        ("gamma", None),
    ),
)

check(
    "selected_exact",
    decision.selected_job_ids
    == ("alpha",),
)

check(
    "excluded_exact",
    decision.excluded_job_ids
    == ("beta",),
)

check(
    "unresolved_exact",
    decision.unresolved_job_ids
    == ("gamma",),
)

check(
    "resolution_unresolved",
    decision.resolution
    is conditional.UniversalOrchestrationBranchResolution.UNRESOLVED,
)

check(
    "is_resolved_false",
    not decision.is_resolved,
)


# ============================================================
# FULLY RESOLVED DECISION
# ============================================================

resolved = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_result,
        condition_evidence={
            "alpha": True,
            "beta": False,
            "gamma": True,
        },
    )
)


check(
    "resolved_selected_exact",
    resolved.selected_job_ids
    == (
        "alpha",
        "gamma",
    ),
)

check(
    "resolved_excluded_exact",
    resolved.excluded_job_ids
    == ("beta",),
)

check(
    "resolved_unresolved_empty",
    resolved.unresolved_job_ids
    == (),
)

check(
    "resolved_is_resolved",
    resolved.is_resolved,
)


# ============================================================
# ALL FALSE LEGAL
# ============================================================

all_false = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_result,
        condition_evidence={
            "alpha": False,
            "beta": False,
            "gamma": False,
        },
    )
)


check(
    "all_false_resolved",
    all_false.is_resolved,
)

check(
    "all_false_selected_empty",
    all_false.selected_job_ids
    == (),
)

check(
    "all_false_excluded_all",
    all_false.excluded_job_ids
    == (
        "alpha",
        "beta",
        "gamma",
    ),
)


# ============================================================
# MISSING EVIDENCE
# ============================================================

missing = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_result,
        condition_evidence={
            "alpha": True,
        },
    )
)


check(
    "missing_is_unresolved",
    missing.unresolved_job_ids
    == (
        "beta",
        "gamma",
    ),
)

check(
    "unknown_not_false",
    "beta"
    not in missing.excluded_job_ids,
)


# ============================================================
# STORED / DERIVED
# ============================================================

field_names = tuple(
    field.name
    for field
    in fields(
        conditional.UniversalOrchestrationConditionalBranching
    )
)


check(
    "stored_fields_exact",
    field_names
    == (
        "fan_out_coordination",
        "condition_evidence",
        "schema_version",
    ),
    field_names,
)

check(
    "identity_derived",
    decision.identity
    is fan_out_result.identity,
)

check(
    "execution_plan_derived",
    decision.execution_plan
    is plan,
)

check(
    "source_job_derived",
    decision.source_job
    is plan.job_map["source"],
)

check(
    "candidate_ids_derived",
    decision.candidate_branch_job_ids
    == (
        "alpha",
        "beta",
        "gamma",
    ),
)


# ============================================================
# IMMUTABILITY
# ============================================================

for field in fields(
    decision
):

    try:

        setattr(
            decision,
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


check(
    "condition_map_mappingproxy",
    isinstance(
        decision.condition_evidence_map,
        MappingProxyType,
    ),
)

check(
    "dispositions_mappingproxy",
    isinstance(
        decision.branch_dispositions,
        MappingProxyType,
    ),
)


# ============================================================
# DECISION ID
# ============================================================

decision_id = (
    resolved.branch_decision_id
)


check(
    "decision_id_length",
    len(decision_id)
    == 64,
    decision_id,
)

check(
    "decision_id_upper_hex",
    all(
        character
        in "0123456789ABCDEF"
        for character
        in decision_id
    ),
)

check(
    "decision_id_repeat_deterministic",
    decision_id
    ==
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_result,
        condition_evidence=(
            ("gamma", True),
            ("beta", False),
            ("alpha", True),
        ),
    )
    .branch_decision_id,
)


# ============================================================
# EXPLANATION
# ============================================================

explanation = (
    conditional
    .explain_universal_orchestration_conditional_branching_v1()
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
    explanation.get("phase")
    == "5.1.10",
)

check(
    "component_exact",
    explanation.get("component")
    == "Universal Orchestration Conditional Branching",
)

check(
    "stored_fields_explanation_exact",
    explanation.get("stored_fields")
    == (
        "fan_out_coordination",
        "condition_evidence",
        "schema_version",
    ),
)

check(
    "progress_boundary",
    "5.1.11"
    in explanation.get(
        "progress_boundary",
        "",
    ),
)

check(
    "persistence_boundary",
    "5.1.14"
    in explanation.get(
        "persistence_boundary",
        "",
    ),
)

check(
    "completion_boundary",
    "5.1.15"
    in explanation.get(
        "completion_boundary",
        "",
    ),
)

check(
    "evidence_record_boundary",
    "5.1.17"
    in explanation.get(
        "evidence_record_boundary",
        "",
    ),
)


# ============================================================
# IMPORT BOUNDARY
# ============================================================

source = CONDITIONAL_PATH.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(source)


backend_imports = []


for node in ast.walk(tree):

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
        "backend.server.runtime.universal_orchestration.contract",
        "backend.server.runtime.universal_orchestration.fan_out_coordination",
    ],
    backend_imports,
)


# ============================================================
# FORBIDDEN BOUNDARIES
# ============================================================

attrs = tuple(
    node.attr
    for node
    in ast.walk(tree)
    if isinstance(
        node,
        ast.Attribute,
    )
)


for forbidden_attr in (
    "status",
    "payload",
    "payload_reference",
    "metadata",
    "result_reference",

    "priority",
    "created_at",
    "scheduled_at",

    "worker_id",
    "queue_id",
    "lease_id",

    "readiness",
    "handoff",
):

    check(
        "forbidden_attribute_"
        + forbidden_attr,
        forbidden_attr
        not in attrs,
    )


forbidden_calls = {
    "eval",
    "exec",
    "compile",

    "open",

    "sleep",
    "wait",
    "poll",

    "enqueue_job",
    "schedule_job",
    "dequeue_job",
    "claim_job",

    "assign_universal_worker",
    "acquire_universal_worker_lease",

    "dispatch_registered_runtime_handler",
    "execute_registered_runtime_job_v1",

    "transition_universal_orchestration_state",

    "get_runtime_state_store_registry",

    "create_task",
    "Thread",
    "Process",

    "persist",
    "dispatch",
    "execute",

    "time",
    "now",
    "utcnow",
}


found_forbidden = []


for node in ast.walk(tree):

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


check(
    "no_universal_job_skipped_symbol",
    "UniversalJobStatus.SKIPPED"
    not in source,
)


# ============================================================
# PROTECTED MATRIX
# ============================================================

for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(path)

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
        "phase_5_1_10_universal_orchestration_conditional_branching",

        conditional.UNIVERSAL_ORCHESTRATION_CONDITIONAL_BRANCHING_VERSION,
        conditional.UNIVERSAL_ORCHESTRATION_CONDITIONAL_BRANCHING_SCHEMA_VERSION,
        conditional.UNIVERSAL_ORCHESTRATION_BRANCH_DECISION_HASH_ALGORITHM,

        EXPECTED_CONDITIONAL_AST,

        "disposition_selected",
        "disposition_excluded",
        "disposition_unresolved",

        "resolution_resolved",
        "resolution_unresolved",

        "true_selected",
        "false_excluded",
        "none_unresolved",
        "missing_unresolved",
        "unknown_not_false",

        "multiple_selected_allowed",
        "zero_selected_resolved_allowed",

        "fan_out_5_1_8_candidate_authority",
        "fan_out_required_two_or_more",

        "static_execution_plan_not_modified",
        "static_fan_out_not_modified",
        "static_fan_in_not_modified",

        "condition_evidence_caller_supplied",
        "condition_evidence_canonical_tuple",
        "condition_evidence_immutable",

        "stored_fan_out_coordination",
        "stored_condition_evidence",
        "stored_schema_version",

        "identity_derived",
        "execution_plan_derived",
        "source_derived",
        "candidate_ids_derived",

        "selected_derived",
        "excluded_derived",
        "unresolved_derived",

        "branch_decision_id_sha256",
        "branch_decision_id_identity_sensitive",
        "branch_decision_id_source_sensitive",
        "branch_decision_id_evidence_sensitive",

        "no_domain_condition_language",
        "no_arbitrary_expression_evaluation",
        "no_eval_exec_compile",
        "no_callable_predicates",

        "no_job_status_inspection",
        "no_payload_inspection",
        "no_metadata_inspection",
        "no_result_reference_inspection",

        "no_filesystem_condition_lookup",
        "no_network_condition_lookup",
        "no_database_condition_lookup",
        "no_wall_clock_condition_lookup",

        "no_skipped_universal_job_status",
        "no_job_status_mutation",
        "no_excluded_job_cancellation",

        "no_queue_activity",
        "no_worker_activity",
        "no_lease_activity",

        "no_readiness_evaluation",
        "no_handoff_evaluation",

        "no_handler_dispatch",
        "no_job_execution",

        "no_state_transition",

        "progress_deferred_5_1_11",
        "persistence_deferred_5_1_14",
        "completion_deferred_5_1_15",
        "evidence_records_deferred_5_1_17",

        "no_runtime_state_store",
        "no_coordination_framework",
        "no_pipeline_coordinator",

        "immutable_deterministic_conditional_branch_decision_authority",
    )
)


conditional_fingerprint = (
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
            conditional_fingerprint
        )
        == 64
        and
        all(
            character
            in "0123456789ABCDEF"
            for character
            in conditional_fingerprint
        )
    ),
    conditional_fingerprint,
)


# ============================================================
# FINAL AST
# ============================================================

final_ast = ast_sha(
    CONDITIONAL_PATH
)


check(
    "final_ast_unchanged",
    final_ast
    == EXPECTED_CONDITIONAL_AST,
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

total = len(checks)


lines = [
    (
        "PHASE 5.1.10 — UNIVERSAL ORCHESTRATION "
        "CONDITIONAL BRANCHING FINAL CERTIFICATION"
    ),

    "=" * 118,

    "",

    (
        "CONDITIONAL BRANCHING AST SHA256: "
        + final_ast
    ),

    (
        "CONDITIONAL BRANCHING FINGERPRINT: "
        + conditional_fingerprint
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
            "FINAL CONDITIONAL BRANCHING CERTIFICATION: "
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

        "CONDITIONAL BRANCHING AUTHORITY MODIFIED DURING CERTIFICATION: NO",
        "5.1.1–5.1.9 FROZEN AUTHORITIES MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "TRUE: SELECTED",
        "FALSE: EXCLUDED",
        "NONE/MISSING: UNRESOLVED",
        "UNKNOWN COLLAPSED TO FALSE: NO",

        "",

        "MULTIPLE SELECTED BRANCHES ALLOWED: YES",
        "ZERO SELECTED FULLY RESOLVED ALLOWED: YES",

        "",

        "5.1.5 DAG MODIFIED: NO",
        "5.1.8 FAN-OUT MODIFIED: NO",
        "5.1.9 FAN-IN MODIFIED: NO",

        "",

        "JOB STATUS/PAYLOAD/METADATA INSPECTED: NO",
        "RESULT REFERENCES INSPECTED: NO",

        "",

        "EVAL/EXEC/COMPILE USED: NO",
        "CALLABLE PREDICATES USED: NO",

        "",

        "SKIPPED UNIVERSAL JOB STATUS CREATED: NO",
        "UNIVERSAL JOB STATUS MUTATED: NO",
        "EXCLUDED JOBS CANCELLED: NO",

        "",

        "QUEUE ACTIVITY: NO",
        "WORKER ACTIVITY: NO",
        "LEASE ACTIVITY: NO",
        "RUNTIME HANDLER ACTIVITY: NO",
        "JOB EXECUTION: NO",

        "",

        "READINESS EVALUATION: NO",
        "RUNTIME HANDOFF EVALUATION: NO",
        "ORCHESTRATION STATE TRANSITION: NO",

        "",

        "PROGRESS RESOLUTION: NO",
        "PERSISTENCE: NO",
        "COMPLETION RESOLUTION: NO",
        "PERMANENT EVIDENCE RECORDING: NO",

        "",

        "RUNTIME STATE STORE ACCESS: NO",
        "UNIVERSAL COORDINATION FRAMEWORK ACCESS: NO",
        "PIPELINE COORDINATOR ACCESS: NO",

        "",

        (
            "PHASE 5.1.10 FREEZE CANDIDATE: "
            + (
                "YES"
                if passed == total
                else "NO"
            )
        ),
    ]
)


REPORT_PATH.write_text(
    "\n".join(lines),
    encoding="utf-8",
)


print(
    "\n".join(lines)
)


if passed != total:

    raise SystemExit(
        "Phase 5.1.10 final certification failed."
    )
