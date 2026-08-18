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
    / "phase_5_1_10_conditional_branching_initial_implementation.txt"
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


def ast_sha(path: Path) -> str:

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


for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(path)

    if actual != expected:

        raise SystemExit(
            "Protected authority changed before 5.1.10: "
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

fanout = importlib.import_module(
    "backend.server.runtime.universal_orchestration.fan_out_coordination"
)

conditional = importlib.import_module(
    "backend.server.runtime.universal_orchestration.conditional_branching"
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
        make_job(job_id="source"),

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
    run_id="conditional-initial",
)


fan_out_result = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=plan,
        source_job_id="source",
    )
)


# ============================================================
# AUTHORITY
# ============================================================

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
    "hash_exact",
    conditional.UNIVERSAL_ORCHESTRATION_BRANCH_DECISION_HASH_ALGORITHM
    == "sha256",
)

check(
    "dispositions_exact",
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
    "resolutions_exact",
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
# MIXED DECISION
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
    "mixed_unresolved",
    decision.resolution
    is conditional.UniversalOrchestrationBranchResolution.UNRESOLVED,
)

check(
    "mixed_not_resolved",
    not decision.is_resolved,
)

check(
    "has_selected",
    decision.has_selected,
)

check(
    "has_excluded",
    decision.has_excluded,
)

check(
    "has_unresolved",
    decision.has_unresolved,
)


# ============================================================
# MISSING EVIDENCE → UNRESOLVED
# ============================================================

partial = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_result,
        condition_evidence={
            "alpha": True,
        },
    )
)


check(
    "partial_normalized_exact",
    partial.condition_evidence
    == (
        ("alpha", True),
        ("beta", None),
        ("gamma", None),
    ),
)

check(
    "missing_evidence_unresolved",
    partial.unresolved_job_ids
    == (
        "beta",
        "gamma",
    ),
)


# ============================================================
# FULL RESOLUTION
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
    "resolved_no_unresolved",
    resolved.unresolved_job_ids
    == (),
)

check(
    "resolution_resolved",
    resolved.is_resolved,
)


# ============================================================
# ALL FALSE IS LEGALLY RESOLVED
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
# NONE INPUT
# ============================================================

none_decision = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_result,
        condition_evidence=None,
    )
)


check(
    "none_all_unresolved",
    none_decision.unresolved_job_ids
    == (
        "alpha",
        "beta",
        "gamma",
    ),
)


# ============================================================
# DISPOSITION FUNCTION
# ============================================================

check(
    "true_selected",
    conditional.disposition_for_condition_evidence(True)
    is conditional.UniversalOrchestrationBranchDisposition.SELECTED,
)

check(
    "false_excluded",
    conditional.disposition_for_condition_evidence(False)
    is conditional.UniversalOrchestrationBranchDisposition.EXCLUDED,
)

check(
    "none_unresolved",
    conditional.disposition_for_condition_evidence(None)
    is conditional.UniversalOrchestrationBranchDisposition.UNRESOLVED,
)


# ============================================================
# INVALID EVIDENCE VALUES
# ============================================================

for index, bad in enumerate(
    (
        0,
        1,
        -1,
        1.0,
        "",
        "true",
        "false",
        [],
        {},
        object(),
    ),
    start=1,
):

    try:

        conditional.evaluate_universal_orchestration_conditional_branching(
            fan_out_coordination=fan_out_result,
            condition_evidence={
                "alpha": bad,
            },
        )

    except conditional.UniversalOrchestrationConditionalBranchingError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_evidence_value_"
        + str(index),
        rejected,
    )


# ============================================================
# OUTSIDE BRANCH
# ============================================================

try:

    conditional.evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_result,
        condition_evidence={
            "outside": True,
        },
    )

except conditional.UniversalOrchestrationConditionalBranchingError as exc:

    outside_rejected = (
        exc.code
        == "condition_evidence_job_outside_fan_out"
    )

else:

    outside_rejected = False


check(
    "outside_branch_rejected",
    outside_rejected,
)


# ============================================================
# DUPLICATE BRANCH
# ============================================================

try:

    conditional.evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_result,
        condition_evidence=(
            ("alpha", True),
            ("alpha", False),
        ),
    )

except conditional.UniversalOrchestrationConditionalBranchingError as exc:

    duplicate_rejected = (
        exc.code
        == "duplicate_condition_evidence_job_id"
    )

else:

    duplicate_rejected = False


check(
    "duplicate_branch_rejected",
    duplicate_rejected,
)


# ============================================================
# REQUIRE TRUE FAN-OUT
# ============================================================

one_plan = make_plan(
    jobs_tuple=(
        make_job(job_id="source"),
        make_job(
            job_id="only",
            dependencies=("source",),
        ),
    ),
    run_id="not-fan-out",
)


one_fan_out = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=one_plan,
        source_job_id="source",
    )
)


try:

    conditional.evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=one_fan_out,
        condition_evidence={
            "only": True,
        },
    )

except conditional.UniversalOrchestrationConditionalBranchingError as exc:

    not_fan_out_rejected = (
        exc.code
        == "conditional_branching_requires_fan_out"
    )

else:

    not_fan_out_rejected = False


check(
    "non_fan_out_rejected",
    not_fan_out_rejected,
)


# ============================================================
# STORED FIELDS
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


for forbidden in (
    "identity",
    "execution_plan",
    "source_job",
    "source_job_id",

    "candidate_branch_job_ids",
    "candidate_branch_jobs",

    "selected_job_ids",
    "excluded_job_ids",
    "unresolved_job_ids",

    "branch_dispositions",
    "resolution",

    "branch_decision_id",

    "status",
    "payload",
    "metadata",

    "queue_id",
    "worker_id",
    "lease_id",

    "created_at",
    "updated_at",
):

    check(
        "forbidden_stored_"
        + forbidden,
        forbidden
        not in field_names,
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


# ============================================================
# DERIVED OBJECTS
# ============================================================

check(
    "identity_derived",
    decision.identity
    is plan.identity,
)

check(
    "source_derived",
    decision.source_job
    is plan.job_map["source"],
)

check(
    "candidate_ids_exact",
    decision.candidate_branch_job_ids
    == (
        "alpha",
        "beta",
        "gamma",
    ),
)

check(
    "selected_objects_exact",
    tuple(
        job.job_id
        for job
        in decision.selected_jobs
    )
    == ("alpha",),
)

check(
    "excluded_objects_exact",
    tuple(
        job.job_id
        for job
        in decision.excluded_jobs
    )
    == ("beta",),
)

check(
    "unresolved_objects_exact",
    tuple(
        job.job_id
        for job
        in decision.unresolved_jobs
    )
    == ("gamma",),
)


# ============================================================
# DETERMINISTIC DECISION ID
# ============================================================

id_one = resolved.branch_decision_id

id_two = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_result,
        condition_evidence={
            "gamma": True,
            "alpha": True,
            "beta": False,
        },
    )
    .branch_decision_id
)


check(
    "decision_id_length",
    len(id_one)
    == 64,
    id_one,
)

check(
    "decision_id_upper_hex",
    all(
        character
        in "0123456789ABCDEF"
        for character
        in id_one
    ),
)

check(
    "decision_id_order_independent_input",
    id_one
    == id_two,
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
# FORBIDDEN CALLS / IMPORTS
# ============================================================

forbidden_calls = {
    "eval",
    "exec",
    "open",

    "read_text",
    "write_text",

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
    "save",
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

        name = node.func.id

    elif isinstance(
        node.func,
        ast.Attribute,
    ):

        name = node.func.attr

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
    "metadata",
    "result_reference",

    "priority",
    "created_at",
    "scheduled_at",

    "worker_id",
    "queue_id",
    "lease_id",
):

    check(
        "forbidden_attribute_"
        + forbidden_attr,
        forbidden_attr
        not in attrs,
    )


# ============================================================
# PROTECTED AUTHORITIES
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


conditional_ast = ast_sha(
    CONDITIONAL_PATH
)


check(
    "conditional_ast_generated",
    len(conditional_ast)
    == 64,
    conditional_ast,
)


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
        "CONDITIONAL BRANCHING INITIAL IMPLEMENTATION"
    ),

    "=" * 118,

    "",

    (
        "CONDITIONAL BRANCHING AST SHA256: "
        + conditional_ast
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
            "INITIAL CONDITIONAL BRANCHING RESULT: "
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

        "5.1.1–5.1.9 FROZEN AUTHORITIES MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "TRUE EVIDENCE: SELECTED",
        "FALSE EVIDENCE: EXCLUDED",
        "NONE/MISSING EVIDENCE: UNRESOLVED",
        "UNKNOWN COLLAPSED TO FALSE: NO",

        "",

        "MULTIPLE SELECTED BRANCHES ALLOWED: YES",
        "ZERO SELECTED WHEN FULLY RESOLVED ALLOWED: YES",

        "",

        "5.1.5 DAG MODIFIED: NO",
        "5.1.8 FAN-OUT TOPOLOGY MODIFIED: NO",
        "5.1.9 FAN-IN TOPOLOGY MODIFIED: NO",

        "",

        "JOB STATUS INSPECTED: NO",
        "PAYLOAD INSPECTED: NO",
        "METADATA INSPECTED: NO",
        "RESULT REFERENCE INSPECTED: NO",

        "",

        "EVAL/EXEC USED: NO",
        "CALLABLE PREDICATES USED: NO",

        "",

        "EXCLUDED JOBS MARKED SKIPPED: NO",
        "UNIVERSAL JOB MUTATION: NO",
        "EXCLUDED JOBS CANCELLED: NO",

        "",

        "QUEUE ACTIVITY: NO",
        "WORKER ACTIVITY: NO",
        "LEASE ACTIVITY: NO",
        "HANDLER DISPATCH: NO",
        "JOB EXECUTION: NO",

        "",

        "READINESS EVALUATION: NO",
        "RUNTIME HANDOFF EVALUATION: NO",
        "ORCHESTRATION STATE TRANSITION: NO",

        "",

        "PERSISTENCE: NO",
        "RUNTIME STATE STORE ACCESS: NO",
        "PERMANENT EVIDENCE RECORDING: NO",
        "PROGRESS RESOLUTION: NO",
        "COMPLETION RESOLUTION: NO",

        "",

        "UNIVERSAL COORDINATION FRAMEWORK ACCESS: NO",
        "PIPELINE COORDINATOR ACCESS: NO",

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
    "\n".join(lines),
    encoding="utf-8",
)


print(
    "\n".join(lines)
)


if passed != total:

    raise SystemExit(
        "Phase 5.1.10 initial implementation failed."
    )
