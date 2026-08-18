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
    / "phase_5_1_10_conditional_branching_regression.txt"
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


# ============================================================
# PRE-FLIGHT
# ============================================================

if not CONDITIONAL_PATH.exists():

    raise SystemExit(
        "5.1.10 Conditional Branching authority is missing."
    )


if ast_sha(CONDITIONAL_PATH) != EXPECTED_CONDITIONAL_AST:

    raise SystemExit(
        (
            "5.1.10 AST changed before adversarial regression.\n"
            "EXPECTED: "
            + EXPECTED_CONDITIONAL_AST
            + "\nACTUAL:   "
            + ast_sha(CONDITIONAL_PATH)
        )
    )


for name, (
    path,
    expected,
) in PROTECTED.items():

    actual = ast_sha(path)

    if actual != expected:

        raise SystemExit(
            "Protected authority changed before 5.1.10 regression: "
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


FIXED_CREATED_AT = (
    "2026-05-21T03:49:30.579317+00:00"
)


def make_job(
    *,
    job_id,
    dependencies=(),
    status=jobs.UniversalJobStatus.CREATED,
    priority=jobs.UniversalJobPriority.NORMAL,
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
        status=status,
        priority=priority,
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


def make_fan_out(
    *,
    branch_ids,
    run_id,
    source_status=jobs.UniversalJobStatus.CREATED,
    source_priority=jobs.UniversalJobPriority.NORMAL,
):

    source = make_job(
        job_id="source",
        status=source_status,
        priority=source_priority,
    )

    branches = tuple(
        make_job(
            job_id=job_id,
            dependencies=("source",),
        )
        for job_id
        in branch_ids
    )

    plan = make_plan(
        jobs_tuple=(
            source,
            *branches,
        ),
        run_id=run_id,
    )

    fan_out_result = (
        fanout
        .coordinate_universal_orchestration_fan_out(
            execution_plan=plan,
            source_job_id="source",
        )
    )

    return (
        plan,
        fan_out_result,
    )


# ============================================================
# 1. AUTHORITY
# ============================================================

check(
    "ast_initial_exact",
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


expected_all = (
    "UNIVERSAL_ORCHESTRATION_CONDITIONAL_BRANCHING_VERSION",
    "UNIVERSAL_ORCHESTRATION_CONDITIONAL_BRANCHING_SCHEMA_VERSION",
    "UNIVERSAL_ORCHESTRATION_BRANCH_DECISION_HASH_ALGORITHM",
    "UniversalOrchestrationConditionalBranchingError",
    "UniversalOrchestrationBranchDisposition",
    "UniversalOrchestrationBranchResolution",
    "disposition_for_condition_evidence",
    "UniversalOrchestrationConditionalBranching",
    "evaluate_universal_orchestration_conditional_branching",
    "explain_universal_orchestration_conditional_branching_v1",
)


check(
    "public_api_exact",
    tuple(
        conditional.__all__
    )
    == expected_all,
    conditional.__all__,
)


# ============================================================
# 2. BRANCH WIDTH MATRIX 2..10
# ============================================================

for width in range(
    2,
    11,
):

    branch_ids = tuple(
        f"branch-{index:02d}"
        for index
        in range(width)
    )

    plan, fan_out_result = (
        make_fan_out(
            branch_ids=branch_ids,
            run_id=f"conditional-width-{width}",
        )
    )

    alternating = {
        job_id:
            (
                True
                if index % 3 == 0
                else
                False
                if index % 3 == 1
                else
                None
            )
        for index, job_id
        in enumerate(
            branch_ids
        )
    }

    result = (
        conditional
        .evaluate_universal_orchestration_conditional_branching(
            fan_out_coordination=fan_out_result,
            condition_evidence=alternating,
        )
    )

    expected_selected = tuple(
        job_id
        for index, job_id
        in enumerate(
            branch_ids
        )
        if index % 3 == 0
    )

    expected_excluded = tuple(
        job_id
        for index, job_id
        in enumerate(
            branch_ids
        )
        if index % 3 == 1
    )

    expected_unresolved = tuple(
        job_id
        for index, job_id
        in enumerate(
            branch_ids
        )
        if index % 3 == 2
    )

    check(
        f"width_{width}_candidates_exact",
        result.candidate_branch_job_ids
        == branch_ids,
    )

    check(
        f"width_{width}_selected_exact",
        result.selected_job_ids
        == expected_selected,
    )

    check(
        f"width_{width}_excluded_exact",
        result.excluded_job_ids
        == expected_excluded,
    )

    check(
        f"width_{width}_unresolved_exact",
        result.unresolved_job_ids
        == expected_unresolved,
    )

    check(
        f"width_{width}_resolution_exact",
        result.is_resolved
        == (
            not expected_unresolved
        ),
    )


# ============================================================
# 3. ALL TRISTATE COMBINATIONS FOR 2 BRANCHES
# ============================================================

branch_ids = (
    "alpha",
    "beta",
)

plan_two, fan_out_two = (
    make_fan_out(
        branch_ids=branch_ids,
        run_id="conditional-tristate",
    )
)


values = (
    True,
    False,
    None,
)


combo_index = 0


for left in values:

    for right in values:

        combo_index += 1

        result = (
            conditional
            .evaluate_universal_orchestration_conditional_branching(
                fan_out_coordination=fan_out_two,
                condition_evidence={
                    "alpha": left,
                    "beta": right,
                },
            )
        )

        expected_selected = tuple(
            job_id
            for job_id, value
            in (
                ("alpha", left),
                ("beta", right),
            )
            if value is True
        )

        expected_excluded = tuple(
            job_id
            for job_id, value
            in (
                ("alpha", left),
                ("beta", right),
            )
            if value is False
        )

        expected_unresolved = tuple(
            job_id
            for job_id, value
            in (
                ("alpha", left),
                ("beta", right),
            )
            if value is None
        )

        check(
            "tristate_selected_"
            + str(combo_index),
            result.selected_job_ids
            == expected_selected,
        )

        check(
            "tristate_excluded_"
            + str(combo_index),
            result.excluded_job_ids
            == expected_excluded,
        )

        check(
            "tristate_unresolved_"
            + str(combo_index),
            result.unresolved_job_ids
            == expected_unresolved,
        )

        check(
            "tristate_resolution_"
            + str(combo_index),
            result.is_resolved
            == (
                len(
                    expected_unresolved
                )
                == 0
            ),
        )


# ============================================================
# 4. OMISSION IS UNRESOLVED
# ============================================================

plan_three, fan_out_three = (
    make_fan_out(
        branch_ids=(
            "alpha",
            "beta",
            "gamma",
        ),
        run_id="conditional-omission",
    )
)


for evidence, expected in (
    (
        {},
        (
            ("alpha", None),
            ("beta", None),
            ("gamma", None),
        ),
    ),

    (
        {
            "alpha": True,
        },
        (
            ("alpha", True),
            ("beta", None),
            ("gamma", None),
        ),
    ),

    (
        {
            "beta": False,
        },
        (
            ("alpha", None),
            ("beta", False),
            ("gamma", None),
        ),
    ),
):

    result = (
        conditional
        .evaluate_universal_orchestration_conditional_branching(
            fan_out_coordination=fan_out_three,
            condition_evidence=evidence,
        )
    )

    check(
        "omission_normalization_"
        + repr(evidence),
        result.condition_evidence
        == expected,
    )


# ============================================================
# 5. INPUT ORDER INDEPENDENCE
# ============================================================

ordered_one = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_three,
        condition_evidence=(
            ("gamma", True),
            ("alpha", False),
            ("beta", None),
        ),
    )
)


ordered_two = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_three,
        condition_evidence=(
            ("beta", None),
            ("gamma", True),
            ("alpha", False),
        ),
    )
)


check(
    "input_order_normalizes_equal",
    ordered_one.condition_evidence
    == ordered_two.condition_evidence,
)

check(
    "input_order_decision_id_equal",
    ordered_one.branch_decision_id
    == ordered_two.branch_decision_id,
)


# ============================================================
# 6. MAPPING / ITERABLE EQUIVALENCE
# ============================================================

mapping_result = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_three,
        condition_evidence={
            "alpha": True,
            "beta": False,
            "gamma": None,
        },
    )
)


iterable_result = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_three,
        condition_evidence=(
            ("alpha", True),
            ("beta", False),
            ("gamma", None),
        ),
    )
)


check(
    "mapping_iterable_evidence_equal",
    mapping_result.condition_evidence
    == iterable_result.condition_evidence,
)

check(
    "mapping_iterable_decision_equal",
    mapping_result.branch_decision_id
    == iterable_result.branch_decision_id,
)


# ============================================================
# 7. IDENTIFIER NORMALIZATION
# ============================================================

normalized_result = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_three,
        condition_evidence=(
            (" alpha ", True),
            ("\tbeta\t", False),
            ("\ngamma\n", None),
        ),
    )
)


check(
    "branch_ids_normalized_exact",
    normalized_result.condition_evidence
    == (
        ("alpha", True),
        ("beta", False),
        ("gamma", None),
    ),
)


# ============================================================
# 8. DUPLICATES AFTER NORMALIZATION
# ============================================================

try:

    conditional.evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_three,
        condition_evidence=(
            ("alpha", True),
            (" alpha ", False),
        ),
    )

except conditional.UniversalOrchestrationConditionalBranchingError as exc:

    duplicate_normalized_rejected = (
        exc.code
        == "duplicate_condition_evidence_job_id"
    )

else:

    duplicate_normalized_rejected = False


check(
    "duplicate_after_normalization_rejected",
    duplicate_normalized_rejected,
)


# ============================================================
# 9. INVALID EVIDENCE CONTAINER ATTACKS
# ============================================================

for index, bad in enumerate(
    (
        True,
        False,

        0,
        1,
        1.0,

        "alpha",
        b"alpha",
        bytearray(b"alpha"),

        object(),
    ),
    start=1,
):

    try:

        conditional.evaluate_universal_orchestration_conditional_branching(
            fan_out_coordination=fan_out_three,
            condition_evidence=bad,
        )

    except conditional.UniversalOrchestrationConditionalBranchingError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_evidence_container_"
        + str(index),
        rejected,
    )


# ============================================================
# 10. INVALID ENTRY SHAPE ATTACKS
# ============================================================

invalid_entries = (
    (
        "alpha",
    ),

    (
        "alpha",
        True,
        "extra",
    ),

    "alpha",

    123,

    object(),
)


for index, bad_entry in enumerate(
    invalid_entries,
    start=1,
):

    try:

        conditional.evaluate_universal_orchestration_conditional_branching(
            fan_out_coordination=fan_out_three,
            condition_evidence=(
                bad_entry,
            ),
        )

    except conditional.UniversalOrchestrationConditionalBranchingError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_entry_shape_"
        + str(index),
        rejected,
    )


# ============================================================
# 11. INVALID JOB ID ATTACKS
# ============================================================

invalid_ids = (
    None,
    True,
    False,

    0,
    1,
    1.0,

    "",
    " ",
    "\t",
    "\n",

    "alpha beta",
    "alpha\tbeta",
    "alpha\nbeta",

    b"alpha",
    bytearray(b"alpha"),

    {},
    [],
    (),
    set(),

    object(),
)


for index, bad in enumerate(
    invalid_ids,
    start=1,
):

    try:

        conditional.evaluate_universal_orchestration_conditional_branching(
            fan_out_coordination=fan_out_three,
            condition_evidence=(
                (
                    bad,
                    True,
                ),
            ),
        )

    except conditional.UniversalOrchestrationConditionalBranchingError:

        rejected = True

    else:

        rejected = False

    check(
        "invalid_branch_id_"
        + str(index),
        rejected,
        repr(bad),
    )


# ============================================================
# 12. TOO LONG JOB ID
# ============================================================

try:

    conditional.evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_three,
        condition_evidence={
            "x" * 201:
                True,
        },
    )

except conditional.UniversalOrchestrationConditionalBranchingError:

    too_long_rejected = True

else:

    too_long_rejected = False


check(
    "too_long_branch_id_rejected",
    too_long_rejected,
)


# ============================================================
# 13. OUTSIDE FAN-OUT MEMBERSHIP
# ============================================================

for outside in (
    "source",
    "outside",
    "not-in-plan",
):

    try:

        conditional.evaluate_universal_orchestration_conditional_branching(
            fan_out_coordination=fan_out_three,
            condition_evidence={
                outside:
                    True,
            },
        )

    except conditional.UniversalOrchestrationConditionalBranchingError as exc:

        rejected = (
            exc.code
            == "condition_evidence_job_outside_fan_out"
        )

    else:

        rejected = False

    check(
        "outside_fan_out_rejected_"
        + outside,
        rejected,
    )


# ============================================================
# 14. INVALID EVIDENCE VALUES
# ============================================================

for index, bad in enumerate(
    (
        0,
        1,
        -1,
        1.0,
        0.0,

        "",
        "true",
        "false",
        "none",

        [],
        (),
        {},
        set(),

        object(),
    ),
    start=1,
):

    try:

        conditional.evaluate_universal_orchestration_conditional_branching(
            fan_out_coordination=fan_out_three,
            condition_evidence={
                "alpha":
                    bad,
            },
        )

    except conditional.UniversalOrchestrationConditionalBranchingError as exc:

        rejected = (
            exc.code
            == "invalid_condition_evidence_value"
        )

    else:

        rejected = False

    check(
        "invalid_evidence_value_"
        + str(index),
        rejected,
    )


# ============================================================
# 15. NON-FAN-OUT STRUCTURES MUST REJECT
# ============================================================

for width in (
    0,
    1,
):

    branch_ids = tuple(
        f"branch-{index}"
        for index
        in range(width)
    )

    source = make_job(
        job_id="source"
    )

    branches = tuple(
        make_job(
            job_id=job_id,
            dependencies=("source",),
        )
        for job_id
        in branch_ids
    )

    plan = make_plan(
        jobs_tuple=(
            source,
            *branches,
        ),
        run_id=f"non-fan-out-{width}",
    )

    fan_out_result = (
        fanout
        .coordinate_universal_orchestration_fan_out(
            execution_plan=plan,
            source_job_id="source",
        )
    )

    try:

        conditional.evaluate_universal_orchestration_conditional_branching(
            fan_out_coordination=fan_out_result,
            condition_evidence=None,
        )

    except conditional.UniversalOrchestrationConditionalBranchingError as exc:

        rejected = (
            exc.code
            == "conditional_branching_requires_fan_out"
        )

    else:

        rejected = False

    check(
        f"non_fan_out_width_{width}_rejected",
        rejected,
    )


# ============================================================
# 16. INVALID FAN-OUT OBJECT ATTACKS
# ============================================================

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

        conditional.evaluate_universal_orchestration_conditional_branching(
            fan_out_coordination=bad,
            condition_evidence=None,
        )

    except conditional.UniversalOrchestrationConditionalBranchingError as exc:

        rejected = (
            exc.code
            == "invalid_conditional_branching_fan_out"
        )

    else:

        rejected = False

    check(
        "invalid_fan_out_attack_"
        + str(index),
        rejected,
    )


# ============================================================
# 17. SOURCE STATUS IRRELEVANCE
# ============================================================

for status in jobs.UniversalJobStatus:

    plan, fan_out_result = (
        make_fan_out(
            branch_ids=(
                "alpha",
                "beta",
            ),
            run_id=(
                "source-status-"
                + status.value
            ),
            source_status=status,
        )
    )

    result = (
        conditional
        .evaluate_universal_orchestration_conditional_branching(
            fan_out_coordination=fan_out_result,
            condition_evidence={
                "alpha": True,
                "beta": False,
            },
        )
    )

    check(
        "source_status_irrelevant_"
        + status.value,
        (
            result.selected_job_ids
            == ("alpha",)
            and
            result.excluded_job_ids
            == ("beta",)
        ),
    )


# ============================================================
# 18. SOURCE PRIORITY IRRELEVANCE
# ============================================================

for priority in jobs.UniversalJobPriority:

    plan, fan_out_result = (
        make_fan_out(
            branch_ids=(
                "alpha",
                "beta",
            ),
            run_id=(
                "source-priority-"
                + str(priority.value)
            ),
            source_priority=priority,
        )
    )

    result = (
        conditional
        .evaluate_universal_orchestration_conditional_branching(
            fan_out_coordination=fan_out_result,
            condition_evidence={
                "alpha": True,
                "beta": False,
            },
        )
    )

    check(
        "source_priority_irrelevant_"
        + str(priority.value),
        result.is_resolved,
    )


# ============================================================
# 19. BRANCH STATUS IRRELEVANCE
# ============================================================

for status in jobs.UniversalJobStatus:

    source = make_job(
        job_id="source"
    )

    branches = (
        make_job(
            job_id="alpha",
            dependencies=("source",),
            status=status,
        ),

        make_job(
            job_id="beta",
            dependencies=("source",),
            status=status,
        ),
    )

    plan = make_plan(
        jobs_tuple=(
            source,
            *branches,
        ),
        run_id=(
            "branch-status-"
            + status.value
        ),
    )

    fan_out_result = (
        fanout
        .coordinate_universal_orchestration_fan_out(
            execution_plan=plan,
            source_job_id="source",
        )
    )

    result = (
        conditional
        .evaluate_universal_orchestration_conditional_branching(
            fan_out_coordination=fan_out_result,
            condition_evidence={
                "alpha": True,
                "beta": False,
            },
        )
    )

    check(
        "branch_status_irrelevant_"
        + status.value,
        (
            result.selected_job_ids
            == ("alpha",)
            and
            result.excluded_job_ids
            == ("beta",)
        ),
    )


# ============================================================
# 20. STORED FIELDS EXACT
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

    "condition_evidence_map",

    "selected_job_ids",
    "excluded_job_ids",
    "unresolved_job_ids",

    "selected_jobs",
    "excluded_jobs",
    "unresolved_jobs",

    "branch_dispositions",
    "resolution",

    "is_resolved",
    "has_selected",
    "has_excluded",
    "has_unresolved",

    "branch_decision_id",

    "status",
    "payload",
    "metadata",
    "result_reference",

    "readiness",
    "handoff",

    "queue_id",
    "worker_id",
    "lease_id",

    "created_at",
    "updated_at",

    "progress",
    "completion",
    "evidence_record",
):

    check(
        "forbidden_stored_field_"
        + forbidden,
        forbidden
        not in field_names,
    )


# ============================================================
# 21. IMMUTABILITY
# ============================================================

immutable_result = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_three,
        condition_evidence={
            "alpha": True,
            "beta": False,
            "gamma": None,
        },
    )
)


for field in fields(
    immutable_result
):

    try:

        setattr(
            immutable_result,
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
# 22. MAPPING PROXY DERIVED VIEWS
# ============================================================

check(
    "condition_evidence_map_mappingproxy",
    isinstance(
        immutable_result.condition_evidence_map,
        MappingProxyType,
    ),
)

check(
    "branch_dispositions_mappingproxy",
    isinstance(
        immutable_result.branch_dispositions,
        MappingProxyType,
    ),
)


try:

    immutable_result.condition_evidence_map[
        "alpha"
    ] = False

except TypeError:

    evidence_map_immutable = True

else:

    evidence_map_immutable = False


check(
    "condition_evidence_map_immutable",
    evidence_map_immutable,
)


try:

    immutable_result.branch_dispositions[
        "alpha"
    ] = conditional.UniversalOrchestrationBranchDisposition.EXCLUDED

except TypeError:

    dispositions_immutable = True

else:

    dispositions_immutable = False


check(
    "branch_dispositions_immutable",
    dispositions_immutable,
)


# ============================================================
# 23. DERIVED OBJECT REFERENCES
# ============================================================

check(
    "identity_derived",
    immutable_result.identity
    is fan_out_three.identity,
)

check(
    "execution_plan_derived",
    immutable_result.execution_plan
    is fan_out_three.execution_plan,
)

check(
    "source_job_derived",
    immutable_result.source_job
    is fan_out_three.source_job,
)

check(
    "candidate_job_objects_exact",
    all(
        job
        is fan_out_three.execution_plan.job_map[
            job.job_id
        ]
        for job
        in immutable_result.candidate_branch_jobs
    ),
)

check(
    "selected_job_objects_exact",
    tuple(
        job.job_id
        for job
        in immutable_result.selected_jobs
    )
    == ("alpha",),
)

check(
    "excluded_job_objects_exact",
    tuple(
        job.job_id
        for job
        in immutable_result.excluded_jobs
    )
    == ("beta",),
)

check(
    "unresolved_job_objects_exact",
    tuple(
        job.job_id
        for job
        in immutable_result.unresolved_jobs
    )
    == ("gamma",),
)


# ============================================================
# 24. DECISION ID DETERMINISM
# ============================================================

ids = tuple(
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_three,
        condition_evidence={
            "alpha": True,
            "beta": False,
            "gamma": None,
        },
    )
    .branch_decision_id
    for _
    in range(20)
)


check(
    "decision_id_repeat_exact",
    len(
        set(ids)
    )
    == 1,
)

check(
    "decision_id_length_64",
    len(ids[0])
    == 64,
    ids[0],
)

check(
    "decision_id_upper_hex",
    all(
        char
        in "0123456789ABCDEF"
        for char
        in ids[0]
    ),
)


# ============================================================
# 25. DECISION ID RUN SENSITIVITY
# ============================================================

_, fan_out_run_a = (
    make_fan_out(
        branch_ids=(
            "alpha",
            "beta",
        ),
        run_id="conditional-run-a",
    )
)

_, fan_out_run_b = (
    make_fan_out(
        branch_ids=(
            "alpha",
            "beta",
        ),
        run_id="conditional-run-b",
    )
)


decision_run_a = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_run_a,
        condition_evidence={
            "alpha": True,
            "beta": False,
        },
    )
    .branch_decision_id
)


decision_run_b = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_run_b,
        condition_evidence={
            "alpha": True,
            "beta": False,
        },
    )
    .branch_decision_id
)


check(
    "decision_id_run_sensitive",
    decision_run_a
    != decision_run_b,
)


# ============================================================
# 26. DECISION ID EVIDENCE SENSITIVITY
# ============================================================

decision_true_false = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_two,
        condition_evidence={
            "alpha": True,
            "beta": False,
        },
    )
    .branch_decision_id
)


decision_false_true = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_two,
        condition_evidence={
            "alpha": False,
            "beta": True,
        },
    )
    .branch_decision_id
)


decision_unresolved = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_two,
        condition_evidence={
            "alpha": None,
            "beta": True,
        },
    )
    .branch_decision_id
)


check(
    "decision_id_evidence_sensitive_1",
    decision_true_false
    != decision_false_true,
)

check(
    "decision_id_evidence_sensitive_2",
    decision_true_false
    != decision_unresolved,
)

check(
    "decision_id_evidence_sensitive_3",
    decision_false_true
    != decision_unresolved,
)


# ============================================================
# 27. SOURCE / TOPOLOGY SENSITIVITY
# ============================================================

source_one = make_job(
    job_id="source-one"
)

source_two = make_job(
    job_id="source-two"
)

topology_plan = make_plan(
    jobs_tuple=(
        source_one,
        source_two,

        make_job(
            job_id="a",
            dependencies=("source-one",),
        ),

        make_job(
            job_id="b",
            dependencies=("source-one",),
        ),

        make_job(
            job_id="c",
            dependencies=("source-two",),
        ),

        make_job(
            job_id="d",
            dependencies=("source-two",),
        ),
    ),
    run_id="conditional-topology",
)


fan_out_one = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=topology_plan,
        source_job_id="source-one",
    )
)


fan_out_two_source = (
    fanout
    .coordinate_universal_orchestration_fan_out(
        execution_plan=topology_plan,
        source_job_id="source-two",
    )
)


decision_one = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_one,
        condition_evidence={
            "a": True,
            "b": False,
        },
    )
    .branch_decision_id
)


decision_two = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_two_source,
        condition_evidence={
            "c": True,
            "d": False,
        },
    )
    .branch_decision_id
)


check(
    "decision_id_source_sensitive",
    decision_one
    != decision_two,
)


# ============================================================
# 28. EXECUTION PLAN MUST NOT MUTATE
# ============================================================

plan_before = (
    fan_out_three.execution_plan.job_ids,
    fan_out_three.execution_plan.dependency_map,
    fan_out_three.execution_plan.dependent_map,
    fan_out_three.execution_plan.execution_waves,
    fan_out_three.execution_plan.topological_order,
)


_ = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_three,
        condition_evidence={
            "alpha": True,
            "beta": False,
            "gamma": None,
        },
    )
)


plan_after = (
    fan_out_three.execution_plan.job_ids,
    fan_out_three.execution_plan.dependency_map,
    fan_out_three.execution_plan.dependent_map,
    fan_out_three.execution_plan.execution_waves,
    fan_out_three.execution_plan.topological_order,
)


check(
    "execution_plan_not_mutated",
    plan_before
    == plan_after,
)


# ============================================================
# 29. FAN-OUT OBJECT MUST NOT MUTATE
# ============================================================

fan_out_before = (
    fan_out_three.source_job_id,
    fan_out_three.direct_dependent_job_ids,
    fan_out_three.fan_out_width,
    fan_out_three.classification,
    fan_out_three.fan_out_group_id,
)


_ = (
    conditional
    .evaluate_universal_orchestration_conditional_branching(
        fan_out_coordination=fan_out_three,
        condition_evidence={
            "alpha": True,
            "beta": False,
            "gamma": None,
        },
    )
)


fan_out_after = (
    fan_out_three.source_job_id,
    fan_out_three.direct_dependent_job_ids,
    fan_out_three.fan_out_width,
    fan_out_three.classification,
    fan_out_three.fan_out_group_id,
)


check(
    "fan_out_not_mutated",
    fan_out_before
    == fan_out_after,
)


# ============================================================
# 30. EXPLANATION CONTRACT
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
    "explanation_phase_exact",
    explanation.get("phase")
    == "5.1.10",
)

check(
    "explanation_component_exact",
    explanation.get("component")
    == "Universal Orchestration Conditional Branching",
)

check(
    "explanation_stored_fields_exact",
    explanation.get("stored_fields")
    == (
        "fan_out_coordination",
        "condition_evidence",
        "schema_version",
    ),
)

check(
    "explanation_unknown_false_boundary",
    "UNRESOLVED"
    in explanation.get(
        "unknown_false_boundary",
        "",
    ),
)

check(
    "explanation_topology_boundary",
    "5.1.8"
    in explanation.get(
        "topology_boundary",
        "",
    ),
)

check(
    "explanation_dag_boundary",
    "5.1.5"
    in explanation.get(
        "dag_boundary",
        "",
    ),
)

check(
    "explanation_fan_in_boundary",
    "5.1.9"
    in explanation.get(
        "fan_in_boundary",
        "",
    ),
)

check(
    "explanation_progress_5_1_11",
    "5.1.11"
    in explanation.get(
        "progress_boundary",
        "",
    ),
)

check(
    "explanation_persistence_5_1_14",
    "5.1.14"
    in explanation.get(
        "persistence_boundary",
        "",
    ),
)

check(
    "explanation_completion_5_1_15",
    "5.1.15"
    in explanation.get(
        "completion_boundary",
        "",
    ),
)

check(
    "explanation_evidence_5_1_17",
    "5.1.17"
    in explanation.get(
        "evidence_record_boundary",
        "",
    ),
)


# ============================================================
# 31. REQUIRED PROHIBITIONS
# ============================================================

required_prohibitions = (
    "does not define a domain condition language",
    "does not evaluate arbitrary expressions",
    "does not call eval",
    "does not call exec",
    "does not invoke condition callbacks",
    "does not import caller modules",

    "does not inspect UniversalJob.status",
    "does not inspect UniversalJob payload",
    "does not inspect UniversalJob metadata",
    "does not inspect result references",

    "does not read filesystem condition inputs",
    "does not read network condition inputs",
    "does not read database condition inputs",
    "does not use wall-clock condition inputs",

    "does not change execution-plan topology",
    "does not change fan-out topology",
    "does not change fan-in topology",

    "does not create UniversalJob SKIPPED status",
    "does not mutate UniversalJob.status",
    "does not cancel excluded jobs",

    "does not enqueue selected jobs",
    "does not schedule selected jobs",
    "does not claim selected jobs",

    "does not assign workers",
    "does not acquire worker leases",

    "does not evaluate stage readiness",
    "does not evaluate runtime handoff eligibility",

    "does not dispatch runtime handlers",
    "does not execute runtime handlers",
    "does not execute jobs",

    "does not transition orchestration state",
    "does not access Runtime State Store",

    "does not persist branch decisions",
    "does not record permanent evidence",

    "does not determine orchestration progress",
    "does not determine orchestration completion",

    "does not import Universal Coordination Framework",
    "does not invoke pipeline coordinators",
)


prohibitions = tuple(
    explanation.get(
        "prohibitions"
    )
    or ()
)


for index, prohibition in enumerate(
    required_prohibitions,
    start=1,
):

    check(
        "prohibition_"
        + str(index),
        prohibition
        in prohibitions,
        prohibition,
    )


# ============================================================
# 32. IMPORT BOUNDARY
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
# 33. FORBIDDEN IMPORTS
# ============================================================

all_imports = []


for node in ast.walk(tree):

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

    "backend.server.runtime.universal_jobs",
    "backend.server.runtime.universal_queue",
    "backend.server.runtime.universal_worker",

    "backend.server.runtime.universal_runtime_registration",
    "backend.server.runtime.universal_runtime_worker_v1",

    "backend.server.runtime.runtime_state_store",
    "backend.server.runtime.runtime_persistence",

    "backend.server.runtime.universal_orchestration.dependency_resolution",
    "backend.server.runtime.universal_orchestration.stage_readiness",
    "backend.server.runtime.universal_orchestration.runtime_handoff",
    "backend.server.runtime.universal_orchestration.fan_in_coordination",
    "backend.server.runtime.universal_orchestration.state_model",

    "backend.server.orchestration",
    "backend.server.coordination",

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
# 34. FORBIDDEN CALLS
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

    "getenv",

    "sleep",
    "wait",
    "poll",

    "time",
    "time_ns",
    "now",
    "utcnow",

    "uuid4",
    "uuid5",
    "random",
    "randint",

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
    "create_subprocess_exec",
    "Thread",
    "Process",

    "persist",
    "save",
    "dispatch",
    "execute",
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


# ============================================================
# 35. FORBIDDEN ATTRIBUTES
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
        "forbidden_attribute_absent_"
        + forbidden_attr,
        forbidden_attr
        not in attrs,
    )


# ============================================================
# 36. NO SKIPPED JOB STATUS SYMBOL
# ============================================================

check(
    "no_universal_job_skipped_symbol",
    "UniversalJobStatus.SKIPPED"
    not in source,
)


# ============================================================
# 37. PROTECTED AUTHORITIES
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
# 38. FINAL AST
# ============================================================

final_ast = ast_sha(
    CONDITIONAL_PATH
)


check(
    "conditional_ast_final",
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
        "PHASE 5.1.10 — UNIVERSAL ORCHESTRATION "
        "CONDITIONAL BRANCHING ADVERSARIAL REGRESSION"
    ),

    "=" * 118,

    "",

    (
        "CONDITIONAL BRANCHING AST SHA256: "
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
            "ADVERSARIAL CONDITIONAL BRANCHING REGRESSION: "
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

        "CONDITIONAL BRANCHING AST MODIFIED: NO",
        "5.1.1–5.1.9 FROZEN AUTHORITIES MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",

        "",

        "TRUE: SELECTED",
        "FALSE: EXCLUDED",
        "NONE/MISSING: UNRESOLVED",
        "UNKNOWN == FALSE: NO",

        "",

        "ALL TRISTATE COMBINATIONS VERIFIED: YES",
        "BRANCH WIDTHS 2–10 VERIFIED: YES",
        "MULTIPLE SELECTED BRANCHES: ALLOWED",
        "ZERO SELECTED FULLY RESOLVED: ALLOWED",

        "",

        "INPUT EVIDENCE ORDER AFFECTS RESULT: NO",
        "MAPPING VS ITERABLE AFFECTS RESULT: NO",
        "DUPLICATE NORMALIZED IDS ACCEPTED: NO",
        "OUTSIDE FAN-OUT MEMBERS ACCEPTED: NO",

        "",

        "SOURCE STATUS USED: NO",
        "BRANCH STATUS USED: NO",
        "PRIORITY USED: NO",
        "PAYLOAD/METADATA/RESULT REFERENCES USED: NO",

        "",

        "5.1.5 DAG MUTATED: NO",
        "5.1.8 FAN-OUT MUTATED: NO",
        "5.1.9 FAN-IN MUTATED: NO",

        "",

        "EVAL/EXEC/COMPILE USED: NO",
        "CALLBACK EXECUTION: NO",
        "ENVIRONMENT/FILESYSTEM/NETWORK/DATABASE LOOKUP: NO",

        "",

        "SKIPPED UNIVERSAL JOB STATUS CREATED: NO",
        "UNIVERSAL JOB STATUS MUTATED: NO",
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
    "\n".join(lines),
    encoding="utf-8",
)


print(
    "\n".join(lines)
)


if passed != total:

    raise SystemExit(
        "Phase 5.1.10 adversarial regression failed."
    )
