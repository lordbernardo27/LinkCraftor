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

DEPENDENCY_PATH = (
    ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_orchestration"
    / "dependency_resolution.py"
)

REPORT_PATH = (
    ROOT
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "phase_5_1_4_dependency_resolution_regression.txt"
)

EXPECTED_DEPENDENCY_AST = (
    "CF4CE73A8683BFDA1464730F2079058898B2660275C786FA6EBD0816AE574A8E"
)


PROTECTED = {
    "5.1.1_orchestration_contract": (
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
        canonical.encode("utf-8")
    ).hexdigest().upper()


# ============================================================
# PRE-FLIGHT AST PROTECTION
# ============================================================

if not DEPENDENCY_PATH.exists():

    raise SystemExit(
        "5.1.4 Dependency Resolution authority missing."
    )


initial_ast = ast_sha(
    DEPENDENCY_PATH
)


if initial_ast != EXPECTED_DEPENDENCY_AST:

    raise SystemExit(
        (
            "5.1.4 Dependency Resolution AST changed before "
            "adversarial regression.\n"
            "EXPECTED: "
            + EXPECTED_DEPENDENCY_AST
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
                "5.1.4 adversarial regression: "
                + name
                + "\nEXPECTED: "
                + expected
                + "\nACTUAL:   "
                + actual
            )
        )


# ============================================================
# IMPORTS
# ============================================================

sys.path.insert(
    0,
    str(ROOT),
)


job_contract = importlib.import_module(
    "backend.server.runtime.universal_jobs.contract"
)

job_status = importlib.import_module(
    "backend.server.runtime.universal_jobs.status"
)

orchestration_contract = importlib.import_module(
    "backend.server.runtime.universal_orchestration.contract"
)

run_identity = importlib.import_module(
    "backend.server.runtime.universal_orchestration.run_identity"
)

dependency_module_name = (
    "backend.server.runtime."
    "universal_orchestration.dependency_resolution"
)

sys.modules.pop(
    dependency_module_name,
    None,
)

dependency = importlib.import_module(
    dependency_module_name
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
# 1 — VERSION / SCHEMA / ENUM
# ============================================================

check(
    "dependency_ast_initial",
    ast_sha(
        DEPENDENCY_PATH
    )
    == EXPECTED_DEPENDENCY_AST,
)

check(
    "version_exact",
    dependency.UNIVERSAL_ORCHESTRATION_DEPENDENCY_RESOLUTION_VERSION
    == "universal_orchestration_dependency_resolution_v5.1.4",
)

check(
    "schema_exact",
    dependency.UNIVERSAL_ORCHESTRATION_DEPENDENCY_RESOLUTION_SCHEMA_VERSION
    == "universal_orchestration_dependency_resolution_schema_v1",
)


expected_classifications = (
    "satisfied",
    "unresolved",
    "terminal_unsatisfied",
    "missing",
)


check(
    "classification_enum_exact",
    tuple(
        member.value
        for member
        in dependency.UniversalOrchestrationDependencyClassification
    )
    == expected_classifications,
)


# ============================================================
# 2 — STATUS PARTITION MUST COVER ALL JOB STATUSES EXACTLY
# ============================================================

all_job_statuses = frozenset(
    job_contract.UniversalJobStatus
)


expected_satisfied = frozenset(
    {
        job_contract.UniversalJobStatus.SUCCEEDED,
    }
)


expected_terminal_unsatisfied = frozenset(
    {
        job_contract.UniversalJobStatus.FAILED,
        job_contract.UniversalJobStatus.CANCELLED,
        job_contract.UniversalJobStatus.DEAD_LETTER,
        job_contract.UniversalJobStatus.EXPIRED,
    }
)


expected_unresolved = frozenset(
    {
        job_contract.UniversalJobStatus.CREATED,
        job_contract.UniversalJobStatus.QUEUED,
        job_contract.UniversalJobStatus.SCHEDULED,
        job_contract.UniversalJobStatus.LEASED,
        job_contract.UniversalJobStatus.RUNNING,
        job_contract.UniversalJobStatus.SUSPENDED,
    }
)


check(
    "satisfied_status_set_exact",
    dependency.SATISFIED_UNIVERSAL_JOB_STATUSES
    == expected_satisfied,
)

check(
    "terminal_unsatisfied_status_set_exact",
    dependency.TERMINAL_UNSATISFIED_UNIVERSAL_JOB_STATUSES
    == expected_terminal_unsatisfied,
)

check(
    "unresolved_status_set_exact",
    dependency.UNRESOLVED_UNIVERSAL_JOB_STATUSES
    == expected_unresolved,
)

check(
    "status_sets_pairwise_disjoint_1",
    not (
        dependency.SATISFIED_UNIVERSAL_JOB_STATUSES
        &
        dependency.TERMINAL_UNSATISFIED_UNIVERSAL_JOB_STATUSES
    ),
)

check(
    "status_sets_pairwise_disjoint_2",
    not (
        dependency.SATISFIED_UNIVERSAL_JOB_STATUSES
        &
        dependency.UNRESOLVED_UNIVERSAL_JOB_STATUSES
    ),
)

check(
    "status_sets_pairwise_disjoint_3",
    not (
        dependency.TERMINAL_UNSATISFIED_UNIVERSAL_JOB_STATUSES
        &
        dependency.UNRESOLVED_UNIVERSAL_JOB_STATUSES
    ),
)

check(
    "status_partition_covers_all_job_statuses",
    (
        dependency.SATISFIED_UNIVERSAL_JOB_STATUSES
        |
        dependency.TERMINAL_UNSATISFIED_UNIVERSAL_JOB_STATUSES
        |
        dependency.UNRESOLVED_UNIVERSAL_JOB_STATUSES
    )
    == all_job_statuses,
)


# ============================================================
# 3 — STATUS SET IMMUTABILITY
# ============================================================

for name, status_set in (
    (
        "satisfied",
        dependency.SATISFIED_UNIVERSAL_JOB_STATUSES,
    ),
    (
        "terminal_unsatisfied",
        dependency.TERMINAL_UNSATISFIED_UNIVERSAL_JOB_STATUSES,
    ),
    (
        "unresolved",
        dependency.UNRESOLVED_UNIVERSAL_JOB_STATUSES,
    ),
):

    check(
        "status_set_frozenset_"
        + name,
        isinstance(
            status_set,
            frozenset,
        ),
    )

    try:

        status_set.add(
            job_contract.UniversalJobStatus.CREATED
        )

    except Exception:

        immutable = True

    else:

        immutable = False

    check(
        "status_set_immutable_"
        + name,
        immutable,
    )


# ============================================================
# 4 — CLASSIFICATION MATRIX: ENUM VALUES
# ============================================================

expected_status_classification = {
    job_contract.UniversalJobStatus.SUCCEEDED:
        dependency.UniversalOrchestrationDependencyClassification.SATISFIED,

    job_contract.UniversalJobStatus.CREATED:
        dependency.UniversalOrchestrationDependencyClassification.UNRESOLVED,

    job_contract.UniversalJobStatus.QUEUED:
        dependency.UniversalOrchestrationDependencyClassification.UNRESOLVED,

    job_contract.UniversalJobStatus.SCHEDULED:
        dependency.UniversalOrchestrationDependencyClassification.UNRESOLVED,

    job_contract.UniversalJobStatus.LEASED:
        dependency.UniversalOrchestrationDependencyClassification.UNRESOLVED,

    job_contract.UniversalJobStatus.RUNNING:
        dependency.UniversalOrchestrationDependencyClassification.UNRESOLVED,

    job_contract.UniversalJobStatus.SUSPENDED:
        dependency.UniversalOrchestrationDependencyClassification.UNRESOLVED,

    job_contract.UniversalJobStatus.FAILED:
        dependency.UniversalOrchestrationDependencyClassification
        .TERMINAL_UNSATISFIED,

    job_contract.UniversalJobStatus.CANCELLED:
        dependency.UniversalOrchestrationDependencyClassification
        .TERMINAL_UNSATISFIED,

    job_contract.UniversalJobStatus.DEAD_LETTER:
        dependency.UniversalOrchestrationDependencyClassification
        .TERMINAL_UNSATISFIED,

    job_contract.UniversalJobStatus.EXPIRED:
        dependency.UniversalOrchestrationDependencyClassification
        .TERMINAL_UNSATISFIED,
}


for status, expected in (
    expected_status_classification.items()
):

    actual = (
        dependency
        .classify_universal_orchestration_dependency_status(
            status
        )
    )

    check(
        "classification_enum_"
        + status.value,
        actual
        is expected,
        actual,
    )


# ============================================================
# 5 — CLASSIFICATION MATRIX: STRING NORMALIZATION
# ============================================================

for status, expected in (
    expected_status_classification.items()
):

    for raw in (
        status.value,
        status.value.upper(),
        "  " + status.value + "  ",
    ):

        actual = (
            dependency
            .classify_universal_orchestration_dependency_status(
                raw
            )
        )

        check(
            (
                "classification_string_"
                + status.value
                + "_"
                + repr(raw)
            ),
            actual
            is expected,
            actual,
        )


# ============================================================
# 6 — INVALID STATUS ATTACKS
# ============================================================

invalid_statuses = (
    None,
    True,
    False,
    0,
    1,
    -1,
    1.0,
    b"succeeded",
    bytearray(b"succeeded"),
    "",
    " ",
    "success",
    "complete",
    "completed",
    "cancel",
    "canceled",
    "dead-letter",
    "unknown",
    [],
    {},
    (),
    set(),
    object(),
)


for index, bad in enumerate(
    invalid_statuses,
    start=1,
):

    try:

        dependency.classify_universal_orchestration_dependency_status(
            bad
        )

    except dependency.UniversalOrchestrationDependencyResolutionError as exc:

        rejected = (
            exc.code
            == "invalid_dependency_job_status"
        )

    else:

        rejected = False

    check(
        "invalid_status_attack_"
        + str(index),
        rejected,
        repr(bad),
    )


# ============================================================
# 7 — DETERMINISTIC FIXTURE HELPERS
# ============================================================

FIXED_CREATED_AT = (
    "2026-05-21T03:49:30.579317+00:00"
)


def make_job(
    *,
    job_id,
    dependencies=(),
    status=job_contract.UniversalJobStatus.CREATED,
    workspace_id="workspace-a",
    pipeline="pipeline-a",
    parent_job_id=None,
):

    return job_contract.UniversalJob(
        job_id=job_id,
        workspace_id=workspace_id,
        pipeline=pipeline,
        stage="stage-a",
        job_type="test_job",
        payload_reference="payload-a",
        status=status,
        parent_job_id=parent_job_id,
        dependency_job_ids=tuple(
            dependencies
        ),
        created_at=FIXED_CREATED_AT,
    )


def make_identity(
    *,
    run_id,
    job_ids,
    workspace_id="workspace-a",
    pipeline="pipeline-a",
):

    contract = (
        orchestration_contract
        .create_universal_runtime_orchestration_contract(
            workspace_id=workspace_id,
            pipeline=pipeline,
            job_ids=job_ids,
        )
    )

    identity = (
        run_identity
        .create_universal_orchestration_run_identity(
            orchestration_run_id=run_id,
            contract=contract,
        )
    )

    return (
        contract,
        identity,
    )


# ============================================================
# 8 — PRIMARY MIXED DEPENDENCY RESOLUTION
# ============================================================

target = make_job(
    job_id="job-target",
    dependencies=(
        "job-a",
        "job-b",
        "job-c",
        "job-d",
    ),
)


contract_a, identity_a = make_identity(
    run_id="run-a",
    job_ids=(
        "job-target",
        "job-d",
        "job-b",
        "job-a",
        "job-c",
    ),
)


resolution = (
    dependency.resolve_universal_orchestration_dependencies(
        identity=identity_a,
        target_job=target,
        dependency_statuses={
            "job-a": "succeeded",
            "job-b": "running",
            "job-c": "failed",
        },
    )
)


check(
    "primary_job_id",
    resolution.job_id
    == "job-target",
)

check(
    "primary_dependencies_canonical",
    resolution.dependency_job_ids
    == (
        "job-a",
        "job-b",
        "job-c",
        "job-d",
    ),
)

check(
    "primary_dependency_count",
    resolution.dependency_count
    == 4,
)

check(
    "primary_satisfied",
    resolution.satisfied_dependency_ids
    == (
        "job-a",
    ),
)

check(
    "primary_unresolved",
    resolution.unresolved_dependency_ids
    == (
        "job-b",
    ),
)

check(
    "primary_terminal_unsatisfied",
    resolution.terminal_unsatisfied_dependency_ids
    == (
        "job-c",
    ),
)

check(
    "primary_missing",
    resolution.missing_dependency_ids
    == (
        "job-d",
    ),
)

check(
    "primary_all_satisfied_false",
    resolution.all_dependencies_satisfied
    is False,
)

check(
    "primary_has_unresolved",
    resolution.has_unresolved_dependencies
    is True,
)

check(
    "primary_has_terminal_failure",
    resolution.has_terminal_dependency_failure
    is True,
)

check(
    "primary_has_missing",
    resolution.has_missing_dependency_evidence
    is True,
)


# ============================================================
# 9 — STATUS MAP CANONICALIZATION / IMMUTABILITY
# ============================================================

check(
    "dependency_statuses_sorted",
    resolution.dependency_statuses
    == (
        (
            "job-a",
            job_contract.UniversalJobStatus.SUCCEEDED,
        ),
        (
            "job-b",
            job_contract.UniversalJobStatus.RUNNING,
        ),
        (
            "job-c",
            job_contract.UniversalJobStatus.FAILED,
        ),
    ),
    resolution.dependency_statuses,
)


status_map = (
    resolution.dependency_status_map
)


check(
    "status_map_mappingproxy",
    isinstance(
        status_map,
        MappingProxyType,
    ),
)


try:

    status_map[
        "job-a"
    ] = job_contract.UniversalJobStatus.FAILED

except Exception:

    immutable = True

else:

    immutable = False


check(
    "status_map_immutable",
    immutable,
)


# ============================================================
# 10 — ALL SATISFIED
# ============================================================

all_satisfied_resolution = (
    dependency.resolve_universal_orchestration_dependencies(
        identity=identity_a,
        target_job=target,
        dependency_statuses={
            "job-d": "succeeded",
            "job-b": "succeeded",
            "job-a": "succeeded",
            "job-c": "succeeded",
        },
    )
)


check(
    "all_satisfied_ids",
    all_satisfied_resolution.satisfied_dependency_ids
    == (
        "job-a",
        "job-b",
        "job-c",
        "job-d",
    ),
)

check(
    "all_satisfied_boolean_true",
    all_satisfied_resolution.all_dependencies_satisfied
    is True,
)

check(
    "all_satisfied_no_unresolved",
    all_satisfied_resolution.has_unresolved_dependencies
    is False,
)

check(
    "all_satisfied_no_terminal_failure",
    all_satisfied_resolution.has_terminal_dependency_failure
    is False,
)

check(
    "all_satisfied_no_missing",
    all_satisfied_resolution.has_missing_dependency_evidence
    is False,
)


# ============================================================
# 11 — ALL UNRESOLVED STATUS VARIANTS
# ============================================================

for status in (
    job_contract.UniversalJobStatus.CREATED,
    job_contract.UniversalJobStatus.QUEUED,
    job_contract.UniversalJobStatus.SCHEDULED,
    job_contract.UniversalJobStatus.LEASED,
    job_contract.UniversalJobStatus.RUNNING,
    job_contract.UniversalJobStatus.SUSPENDED,
):

    one_target = make_job(
        job_id="target-" + status.value,
        dependencies=(
            "dep-" + status.value,
        ),
    )

    _, one_identity = make_identity(
        run_id="run-" + status.value,
        job_ids=(
            one_target.job_id,
            "dep-" + status.value,
        ),
    )

    one_resolution = (
        dependency.resolve_universal_orchestration_dependencies(
            identity=one_identity,
            target_job=one_target,
            dependency_statuses={
                "dep-" + status.value:
                    status,
            },
        )
    )

    check(
        "unresolved_variant_"
        + status.value,
        one_resolution.unresolved_dependency_ids
        == (
            "dep-" + status.value,
        ),
    )

    check(
        "unresolved_variant_not_all_satisfied_"
        + status.value,
        one_resolution.all_dependencies_satisfied
        is False,
    )

    check(
        "unresolved_variant_not_terminal_"
        + status.value,
        one_resolution.has_terminal_dependency_failure
        is False,
    )


# ============================================================
# 12 — TERMINAL UNSATISFIED VARIANTS
# ============================================================

for status in (
    job_contract.UniversalJobStatus.FAILED,
    job_contract.UniversalJobStatus.CANCELLED,
    job_contract.UniversalJobStatus.DEAD_LETTER,
    job_contract.UniversalJobStatus.EXPIRED,
):

    one_target = make_job(
        job_id="target-" + status.value,
        dependencies=(
            "dep-" + status.value,
        ),
    )

    _, one_identity = make_identity(
        run_id="terminal-run-" + status.value,
        job_ids=(
            one_target.job_id,
            "dep-" + status.value,
        ),
    )

    one_resolution = (
        dependency.resolve_universal_orchestration_dependencies(
            identity=one_identity,
            target_job=one_target,
            dependency_statuses={
                "dep-" + status.value:
                    status,
            },
        )
    )

    check(
        "terminal_variant_"
        + status.value,
        one_resolution.terminal_unsatisfied_dependency_ids
        == (
            "dep-" + status.value,
        ),
    )

    check(
        "terminal_variant_has_failure_"
        + status.value,
        one_resolution.has_terminal_dependency_failure
        is True,
    )

    check(
        "terminal_variant_not_unresolved_"
        + status.value,
        one_resolution.has_unresolved_dependencies
        is False,
    )


# ============================================================
# 13 — ZERO DEPENDENCY SEMANTICS
# ============================================================

zero_target = make_job(
    job_id="zero-target",
    dependencies=(),
)


zero_contract, zero_identity = make_identity(
    run_id="zero-run",
    job_ids=(
        "zero-target",
    ),
)


zero_resolution = (
    dependency.resolve_universal_orchestration_dependencies(
        identity=zero_identity,
        target_job=zero_target,
    )
)


check(
    "zero_dependency_count",
    zero_resolution.dependency_count
    == 0,
)

check(
    "zero_dependency_ids",
    zero_resolution.dependency_job_ids
    == (),
)

check(
    "zero_satisfied_ids",
    zero_resolution.satisfied_dependency_ids
    == (),
)

check(
    "zero_unresolved_ids",
    zero_resolution.unresolved_dependency_ids
    == (),
)

check(
    "zero_terminal_unsatisfied_ids",
    zero_resolution.terminal_unsatisfied_dependency_ids
    == (),
)

check(
    "zero_missing_ids",
    zero_resolution.missing_dependency_ids
    == (),
)

check(
    "zero_all_satisfied_true",
    zero_resolution.all_dependencies_satisfied
    is True,
)

check(
    "zero_has_unresolved_false",
    zero_resolution.has_unresolved_dependencies
    is False,
)

check(
    "zero_has_terminal_failure_false",
    zero_resolution.has_terminal_dependency_failure
    is False,
)

check(
    "zero_has_missing_false",
    zero_resolution.has_missing_dependency_evidence
    is False,
)


# ============================================================
# 14 — ZERO DEPENDENCY EXTRANEOUS EVIDENCE
# ============================================================

try:

    dependency.resolve_universal_orchestration_dependencies(
        identity=zero_identity,
        target_job=zero_target,
        dependency_statuses={
            "ghost-job": "succeeded",
        },
    )

except dependency.UniversalOrchestrationDependencyResolutionError as exc:

    rejected = (
        exc.code
        == "extraneous_dependency_status_evidence"
    )

else:

    rejected = False


check(
    "zero_dependency_extraneous_evidence_rejected",
    rejected,
)


# ============================================================
# 15 — MISSING EVIDENCE IS DISTINCT
# ============================================================

missing_target = make_job(
    job_id="missing-target",
    dependencies=(
        "dep-a",
        "dep-b",
        "dep-c",
    ),
)


_, missing_identity = make_identity(
    run_id="missing-run",
    job_ids=(
        "missing-target",
        "dep-a",
        "dep-b",
        "dep-c",
    ),
)


missing_resolution = (
    dependency.resolve_universal_orchestration_dependencies(
        identity=missing_identity,
        target_job=missing_target,
        dependency_statuses={},
    )
)


check(
    "all_missing_ids",
    missing_resolution.missing_dependency_ids
    == (
        "dep-a",
        "dep-b",
        "dep-c",
    ),
)

check(
    "all_missing_not_unresolved",
    missing_resolution.unresolved_dependency_ids
    == (),
)

check(
    "all_missing_not_terminal_unsatisfied",
    missing_resolution.terminal_unsatisfied_dependency_ids
    == (),
)

check(
    "all_missing_not_satisfied",
    missing_resolution.satisfied_dependency_ids
    == (),
)

check(
    "all_missing_boolean",
    missing_resolution.has_missing_dependency_evidence
    is True,
)

check(
    "all_missing_not_terminal_failure",
    missing_resolution.has_terminal_dependency_failure
    is False,
)


# ============================================================
# 16 — CLASSIFICATION LOOKUPS
# ============================================================

for dependency_id, expected in (
    (
        "job-a",
        dependency.UniversalOrchestrationDependencyClassification.SATISFIED,
    ),
    (
        "job-b",
        dependency.UniversalOrchestrationDependencyClassification.UNRESOLVED,
    ),
    (
        "job-c",
        dependency.UniversalOrchestrationDependencyClassification
        .TERMINAL_UNSATISFIED,
    ),
    (
        "job-d",
        dependency.UniversalOrchestrationDependencyClassification.MISSING,
    ),
):

    actual = (
        resolution.classification_for_dependency(
            dependency_id
        )
    )

    check(
        "classification_lookup_"
        + dependency_id,
        actual
        is expected,
        actual,
    )


# ============================================================
# 17 — CLASSIFICATION LOOKUP ATTACKS
# ============================================================

for index, bad in enumerate(
    (
        None,
        True,
        False,
        0,
        1,
        1.0,
        b"job-a",
        [],
        {},
        (),
        object(),
    ),
    start=1,
):

    try:

        resolution.classification_for_dependency(
            bad
        )

    except dependency.UniversalOrchestrationDependencyResolutionError as exc:

        rejected = (
            exc.code
            == "invalid_dependency_lookup_job_id"
        )

    else:

        rejected = False

    check(
        "invalid_lookup_id_"
        + str(index),
        rejected,
        repr(bad),
    )


for unknown in (
    "",
    " ",
    "job-z",
    "job-target",
):

    try:

        resolution.classification_for_dependency(
            unknown
        )

    except dependency.UniversalOrchestrationDependencyResolutionError as exc:

        rejected = (
            exc.code
            == "unknown_dependency_lookup_job_id"
        )

    else:

        rejected = False

    check(
        "unknown_lookup_"
        + repr(unknown),
        rejected,
    )


# ============================================================
# 18 — LOOKUP SURROUNDING WHITESPACE NORMALIZATION
# ============================================================

check(
    "lookup_trim",
    resolution.classification_for_dependency(
        "  job-a  "
    )
    is (
        dependency.UniversalOrchestrationDependencyClassification.SATISFIED
    ),
)


# ============================================================
# 19 — IDENTITY TYPE SPOOFING
# ============================================================

for index, bad_identity in enumerate(
    (
        None,
        True,
        False,
        0,
        1,
        "",
        {},
        [],
        contract_a,
        target,
        object(),
    ),
    start=1,
):

    try:

        dependency.resolve_universal_orchestration_dependencies(
            identity=bad_identity,
            target_job=target,
        )

    except dependency.UniversalOrchestrationDependencyResolutionError as exc:

        rejected = (
            exc.code
            == "invalid_dependency_resolution_identity"
        )

    else:

        rejected = False

    check(
        "identity_spoof_"
        + str(index),
        rejected,
    )


# ============================================================
# 20 — TARGET JOB TYPE SPOOFING
# ============================================================

for index, bad_target in enumerate(
    (
        None,
        True,
        False,
        0,
        1,
        "",
        {},
        [],
        identity_a,
        contract_a,
        object(),
    ),
    start=1,
):

    try:

        dependency.resolve_universal_orchestration_dependencies(
            identity=identity_a,
            target_job=bad_target,
        )

    except dependency.UniversalOrchestrationDependencyResolutionError as exc:

        rejected = (
            exc.code
            == "invalid_dependency_resolution_target_job"
        )

    else:

        rejected = False

    check(
        "target_job_spoof_"
        + str(index),
        rejected,
    )


# ============================================================
# 21 — TARGET MUST BELONG TO CONTRACT
# ============================================================

outside_target = make_job(
    job_id="outside-target",
)


try:

    dependency.resolve_universal_orchestration_dependencies(
        identity=identity_a,
        target_job=outside_target,
    )

except dependency.UniversalOrchestrationDependencyResolutionError as exc:

    rejected = (
        exc.code
        == "target_job_outside_orchestration_contract"
    )

else:

    rejected = False


check(
    "outside_target_rejected",
    rejected,
)


# ============================================================
# 22 — EVERY DEPENDENCY MUST BELONG TO CONTRACT
# ============================================================

outside_dependency_target = make_job(
    job_id="job-target",
    dependencies=(
        "job-a",
        "outside-dependency",
    ),
)


try:

    dependency.resolve_universal_orchestration_dependencies(
        identity=identity_a,
        target_job=outside_dependency_target,
    )

except dependency.UniversalOrchestrationDependencyResolutionError as exc:

    rejected = (
        exc.code
        == "dependency_outside_orchestration_contract"
    )

else:

    rejected = False


check(
    "outside_dependency_rejected",
    rejected,
)


# ============================================================
# 23 — WORKSPACE BINDING
# ============================================================

workspace_mismatch_target = make_job(
    job_id="job-target",
    workspace_id="workspace-b",
)


try:

    dependency.resolve_universal_orchestration_dependencies(
        identity=identity_a,
        target_job=workspace_mismatch_target,
    )

except dependency.UniversalOrchestrationDependencyResolutionError as exc:

    rejected = (
        exc.code
        == "dependency_target_workspace_mismatch"
    )

else:

    rejected = False


check(
    "workspace_mismatch_rejected",
    rejected,
)


# ============================================================
# 24 — PIPELINE BINDING
# ============================================================

pipeline_mismatch_target = make_job(
    job_id="job-target",
    pipeline="pipeline-b",
)


try:

    dependency.resolve_universal_orchestration_dependencies(
        identity=identity_a,
        target_job=pipeline_mismatch_target,
    )

except dependency.UniversalOrchestrationDependencyResolutionError as exc:

    rejected = (
        exc.code
        == "dependency_target_pipeline_mismatch"
    )

else:

    rejected = False


check(
    "pipeline_mismatch_rejected",
    rejected,
)


# ============================================================
# 25 — PARENT_JOB_ID MUST NOT BECOME DEPENDENCY
# ============================================================

parent_target = make_job(
    job_id="child-job",
    dependencies=(),
    parent_job_id="parent-job",
)


_, parent_identity = make_identity(
    run_id="parent-run",
    job_ids=(
        "child-job",
    ),
)


parent_resolution = (
    dependency.resolve_universal_orchestration_dependencies(
        identity=parent_identity,
        target_job=parent_target,
    )
)


check(
    "parent_not_dependency",
    parent_resolution.dependency_job_ids
    == (),
)

check(
    "parent_not_counted",
    parent_resolution.dependency_count
    == 0,
)

check(
    "parent_zero_dependencies_satisfied",
    parent_resolution.all_dependencies_satisfied
    is True,
)


# ============================================================
# 26 — DEPENDENCY STATUS MAPPING TYPE ATTACKS
# ============================================================

for index, bad_mapping in enumerate(
    (
        True,
        False,
        0,
        1,
        1.0,
        "",
        "job-a",
        [],
        (),
        set(),
        object(),
    ),
    start=1,
):

    try:

        dependency.resolve_universal_orchestration_dependencies(
            identity=identity_a,
            target_job=target,
            dependency_statuses=bad_mapping,
        )

    except dependency.UniversalOrchestrationDependencyResolutionError as exc:

        rejected = (
            exc.code
            == "invalid_dependency_status_mapping"
        )

    else:

        rejected = False

    check(
        "invalid_mapping_"
        + str(index),
        rejected,
        repr(bad_mapping),
    )


# ============================================================
# 27 — NONE STATUS MAPPING MEANS NO EVIDENCE
# ============================================================

none_evidence_resolution = (
    dependency.resolve_universal_orchestration_dependencies(
        identity=identity_a,
        target_job=target,
        dependency_statuses=None,
    )
)


check(
    "none_evidence_all_missing",
    none_evidence_resolution.missing_dependency_ids
    == target.dependency_job_ids,
)

check(
    "none_evidence_has_missing",
    none_evidence_resolution.has_missing_dependency_evidence
    is True,
)


# ============================================================
# 28 — MAPPING KEY ATTACKS
# ============================================================

bad_key_cases = (
    (
        None,
        "invalid_dependency_status_job_id",
    ),
    (
        True,
        "invalid_dependency_status_job_id",
    ),
    (
        1,
        "invalid_dependency_status_job_id",
    ),
    (
        "",
        "invalid_dependency_status_job_id",
    ),
    (
        " ",
        "invalid_dependency_status_job_id",
    ),
    (
        "job a",
        "invalid_dependency_status_job_id",
    ),
    (
        "job\ta",
        "invalid_dependency_status_job_id",
    ),
)


for index, (
    bad_key,
    expected_code,
) in enumerate(
    bad_key_cases,
    start=1,
):

    try:

        dependency.resolve_universal_orchestration_dependencies(
            identity=identity_a,
            target_job=target,
            dependency_statuses={
                bad_key: "succeeded",
            },
        )

    except dependency.UniversalOrchestrationDependencyResolutionError as exc:

        rejected = (
            exc.code
            == expected_code
        )

    else:

        rejected = False

    check(
        "bad_mapping_key_"
        + str(index),
        rejected,
        repr(bad_key),
    )


# ============================================================
# 29 — KEY SURROUNDING WHITESPACE IS NORMALIZED
# ============================================================

trimmed_key_resolution = (
    dependency.resolve_universal_orchestration_dependencies(
        identity=identity_a,
        target_job=target,
        dependency_statuses={
            " job-a ": "SUCCEEDED",
        },
    )
)


check(
    "status_key_trimmed",
    trimmed_key_resolution.dependency_statuses
    == (
        (
            "job-a",
            job_contract.UniversalJobStatus.SUCCEEDED,
        ),
    ),
)


# ============================================================
# 30 — EXTRANEOUS STATUS EVIDENCE
# ============================================================

for extraneous_id in (
    "job-target",
    "job-z",
    "outside-job",
):

    try:

        dependency.resolve_universal_orchestration_dependencies(
            identity=identity_a,
            target_job=target,
            dependency_statuses={
                extraneous_id:
                    "succeeded",
            },
        )

    except dependency.UniversalOrchestrationDependencyResolutionError as exc:

        rejected = (
            exc.code
            == "extraneous_dependency_status_evidence"
        )

    else:

        rejected = False

    check(
        "extraneous_evidence_"
        + extraneous_id,
        rejected,
    )


# ============================================================
# 31 — INVALID STATUS VALUES IN EVIDENCE
# ============================================================

for index, bad_status in enumerate(
    invalid_statuses,
    start=1,
):

    try:

        dependency.resolve_universal_orchestration_dependencies(
            identity=identity_a,
            target_job=target,
            dependency_statuses={
                "job-a":
                    bad_status,
            },
        )

    except dependency.UniversalOrchestrationDependencyResolutionError as exc:

        rejected = (
            exc.code
            == "invalid_dependency_job_status"
        )

    else:

        rejected = False

    check(
        "invalid_evidence_status_"
        + str(index),
        rejected,
    )


# ============================================================
# 32 — DETERMINISM UNDER INPUT MAPPING ORDER
# ============================================================

ordered_a = (
    dependency.resolve_universal_orchestration_dependencies(
        identity=identity_a,
        target_job=target,
        dependency_statuses={
            "job-a": "succeeded",
            "job-b": "running",
            "job-c": "failed",
            "job-d": "queued",
        },
    )
)


ordered_b = (
    dependency.resolve_universal_orchestration_dependencies(
        identity=identity_a,
        target_job=target,
        dependency_statuses={
            "job-d": "queued",
            "job-c": "failed",
            "job-b": "running",
            "job-a": "succeeded",
        },
    )
)


check(
    "input_mapping_order_deterministic_object",
    ordered_a
    == ordered_b,
)

check(
    "input_mapping_order_deterministic_tuple",
    ordered_a.dependency_statuses
    == ordered_b.dependency_statuses,
)


# ============================================================
# 33 — DIRECT CONSTRUCTOR NORMALIZATION
# ============================================================

direct = (
    dependency.UniversalOrchestrationDependencyResolution(
        identity=identity_a,
        target_job=target,
        dependency_statuses=(
            (
                "job-c",
                job_contract.UniversalJobStatus.FAILED,
            ),
            (
                "job-a",
                job_contract.UniversalJobStatus.SUCCEEDED,
            ),
        ),
    )
)


check(
    "direct_constructor_statuses_canonical",
    direct.dependency_statuses
    == (
        (
            "job-a",
            job_contract.UniversalJobStatus.SUCCEEDED,
        ),
        (
            "job-c",
            job_contract.UniversalJobStatus.FAILED,
        ),
    ),
)


# ============================================================
# 34 — DIRECT CONSTRUCTOR IDENTITY SPOOF
# ============================================================

try:

    dependency.UniversalOrchestrationDependencyResolution(
        identity=None,
        target_job=target,
    )

except dependency.UniversalOrchestrationDependencyResolutionError as exc:

    rejected = (
        exc.code
        == "invalid_dependency_resolution_identity"
    )

else:

    rejected = False


check(
    "direct_identity_spoof_rejected",
    rejected,
)


# ============================================================
# 35 — DIRECT CONSTRUCTOR TARGET SPOOF
# ============================================================

try:

    dependency.UniversalOrchestrationDependencyResolution(
        identity=identity_a,
        target_job=None,
    )

except dependency.UniversalOrchestrationDependencyResolutionError as exc:

    rejected = (
        exc.code
        == "invalid_dependency_resolution_target_job"
    )

else:

    rejected = False


check(
    "direct_target_spoof_rejected",
    rejected,
)


# ============================================================
# 36 — SCHEMA FORGERY
# ============================================================

for bad_schema in (
    "",
    " ",
    "v1",
    "wrong",
    "universal_orchestration_dependency_resolution_schema_v2",
):

    try:

        dependency.UniversalOrchestrationDependencyResolution(
            identity=identity_a,
            target_job=target,
            dependency_statuses=(),
            schema_version=bad_schema,
        )

    except dependency.UniversalOrchestrationDependencyResolutionError as exc:

        rejected = (
            exc.code
            == "invalid_dependency_resolution_schema_version"
        )

    else:

        rejected = False

    check(
        "schema_attack_"
        + repr(bad_schema),
        rejected,
    )


# ============================================================
# 37 — EXACT STORED FIELD CONTRACT
# ============================================================

field_names = tuple(
    field.name
    for field in fields(
        dependency.UniversalOrchestrationDependencyResolution
    )
)


check(
    "stored_fields_exact",
    field_names
    == (
        "identity",
        "target_job",
        "dependency_statuses",
        "schema_version",
    ),
    field_names,
)


for forbidden_field in (
    "job_id",
    "dependency_job_ids",
    "dependency_count",

    "satisfied_dependency_ids",
    "unresolved_dependency_ids",
    "terminal_unsatisfied_dependency_ids",
    "missing_dependency_ids",

    "all_dependencies_satisfied",
    "has_unresolved_dependencies",
    "has_terminal_dependency_failure",
    "has_missing_dependency_evidence",

    "parent_job_id",

    "ready",
    "blocked",
    "waiting",

    "execution_order",
    "execution_plan",

    "cycle",
    "cycle_detected",

    "orchestration_state",

    "created_at",
    "updated_at",

    "worker_id",
    "lease_id",
    "queue_id",

    "metadata",
):

    check(
        "forbidden_stored_field_"
        + forbidden_field,
        forbidden_field
        not in field_names,
    )


# ============================================================
# 38 — IMMUTABILITY
# ============================================================

for field in fields(
    resolution
):

    try:

        setattr(
            resolution,
            field.name,
            None,
        )

    except Exception:

        immutable = True

    else:

        immutable = False

    check(
        "immutable_field_"
        + field.name,
        immutable,
    )


# ============================================================
# 39 — ORIGINAL TARGET JOB NOT MUTATED
# ============================================================

check(
    "target_dependencies_unchanged",
    target.dependency_job_ids
    == (
        "job-a",
        "job-b",
        "job-c",
        "job-d",
    ),
)

check(
    "target_status_unchanged",
    target.status
    is job_contract.UniversalJobStatus.CREATED,
)


# ============================================================
# 40 — RESOLUTION DOES NOT CHANGE ORCHESTRATION IDENTITY
# ============================================================

check(
    "identity_reference_preserved",
    resolution.identity
    == identity_a,
)

check(
    "identity_run_id_unchanged",
    resolution.identity.orchestration_run_id
    == "run-a",
)

check(
    "identity_contract_unchanged",
    resolution.identity.contract
    == contract_a,
)


# ============================================================
# 41 — EXPLANATION CONTRACT
# ============================================================

explanation = (
    dependency
    .explain_universal_orchestration_dependency_resolution_v1()
)


check(
    "explanation_phase",
    explanation.get(
        "phase"
    )
    == "5.1.4",
)

check(
    "explanation_component",
    explanation.get(
        "component"
    )
    == "Universal Orchestration Dependency Resolution",
)

check(
    "explanation_version",
    explanation.get(
        "version"
    )
    == dependency.UNIVERSAL_ORCHESTRATION_DEPENDENCY_RESOLUTION_VERSION,
)

check(
    "explanation_schema",
    explanation.get(
        "schema_version"
    )
    == dependency.UNIVERSAL_ORCHESTRATION_DEPENDENCY_RESOLUTION_SCHEMA_VERSION,
)

check(
    "explanation_stored_fields",
    explanation.get(
        "stored_fields"
    )
    == (
        "identity",
        "target_job",
        "dependency_statuses",
        "schema_version",
    ),
)

check(
    "dependency_source_rule",
    "Universal Job"
    in explanation.get(
        "dependency_source_rule",
        "",
    ),
)

check(
    "membership_rule",
    "5.1.1"
    in explanation.get(
        "membership_rule",
        "",
    ),
)

check(
    "parent_rule_separate",
    "not implicitly treated as a dependency"
    in explanation.get(
        "parent_rule",
        "",
    ),
)

check(
    "caller_supplied_rule",
    "caller supplied"
    in explanation.get(
        "evidence_rule",
        "",
    ),
)

check(
    "missing_rule_distinct",
    "MISSING"
    in explanation.get(
        "missing_rule",
        "",
    ),
)

check(
    "zero_dependency_rule",
    "all_dependencies_satisfied=True"
    in explanation.get(
        "zero_dependency_rule",
        "",
    ),
)

check(
    "cycle_deferred_5_1_5",
    "5.1.5"
    in explanation.get(
        "cycle_boundary",
        "",
    ),
)

check(
    "planning_deferred_5_1_5",
    "5.1.5"
    in explanation.get(
        "planning_boundary",
        "",
    ),
)

check(
    "readiness_deferred_5_1_6",
    "5.1.6"
    in explanation.get(
        "readiness_boundary",
        "",
    ),
)

check(
    "state_not_transitioned",
    "does not transition"
    in explanation.get(
        "state_boundary",
        "",
    ),
)


# ============================================================
# 42 — EXPLANATION CLASSIFICATION EXACTNESS
# ============================================================

classification_explanation = (
    explanation.get(
        "classification"
    )
)


check(
    "classification_explanation_mapping",
    isinstance(
        classification_explanation,
        MappingProxyType,
    ),
)

check(
    "classification_explanation_satisfied",
    classification_explanation.get(
        "satisfied"
    )
    == (
        "succeeded",
    ),
)

check(
    "classification_explanation_unresolved",
    classification_explanation.get(
        "unresolved"
    )
    == (
        "created",
        "queued",
        "scheduled",
        "leased",
        "running",
        "suspended",
    ),
)

check(
    "classification_explanation_terminal_unsatisfied",
    classification_explanation.get(
        "terminal_unsatisfied"
    )
    == (
        "failed",
        "cancelled",
        "dead_letter",
        "expired",
    ),
)


# ============================================================
# 43 — PROHIBITION MATRIX
# ============================================================

required_prohibitions = (
    "does not redefine dependency_job_ids",
    "does not mutate Universal Job lineage",
    "does not treat parent_job_id as an implicit dependency",
    "does not perform cross-job cycle detection",

    "does not read Runtime State Store",
    "does not query job persistence",
    "does not mutate Universal Jobs",
    "does not transition orchestration state",

    "does not determine execution order",
    "does not create execution plans",

    "does not determine READY",
    "does not determine BLOCKED",

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

    "does not persist dependency resolution",

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
        + str(index),
        item
        in prohibitions,
        item,
    )


# ============================================================
# 44 — IMPORT BOUNDARY
# ============================================================

source = DEPENDENCY_PATH.read_text(
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
    "backend_imports_exact",
    backend_imports
    == [
        "backend.server.runtime.universal_jobs.contract",
        "backend.server.runtime.universal_jobs.status",
        "backend.server.runtime.universal_orchestration.run_identity",
    ],
    backend_imports,
)


# ============================================================
# 45 — FORBIDDEN IMPORTS
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

    "backend.server.runtime.universal_queue",
    "backend.server.runtime.universal_worker",

    "backend.server.runtime.universal_runtime_registration",
    "backend.server.runtime.runtime_state_store",

    "backend.server.runtime.universal_orchestration.state_model",

    "backend.server.orchestration",
    "backend.server.coordination",

    "backend.server.jobs.universal_knowledge_orchestrator",

    "backend.server.pipelines.connect_domain.coordinator",
):

    matches = tuple(
        module
        for module in all_imports
        if (
            module
            == forbidden_module
            or
            module.startswith(
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
# 46 — FORBIDDEN CALLS
# ============================================================

forbidden_calls = {
    "open",
    "read_text",
    "write_text",
    "mkdir",
    "unlink",
    "remove",

    "time",
    "time_ns",
    "now",
    "utcnow",

    "uuid4",
    "uuid5",
    "random",
    "randint",
    "choice",

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

    "transition_universal_orchestration_state",

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
# 47 — NO RESPONSIBILITY BLEED
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
    "cycle_detect",
    "topological",
    "execution_order",
    "execution_plan",
    "readiness",
    "ready_job",
    "blocked_job",
    "transition_state",

    "enqueue",
    "dequeue",
    "claim",

    "assign_worker",
    "lease_worker",

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
# 48 — NO HIDDEN DECISION/PERSISTENCE FIELDS
# ============================================================

source_lower = source.lower()


for forbidden_symbol in (
    "execution_order:",
    "execution_plan:",
    "topological_order:",

    "ready:",
    "blocked:",
    "readiness:",

    "cycle_detected:",

    "orchestration_state:",

    "queue_id:",
    "worker_id:",
    "lease_id:",

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
# 49 — API SURFACE
# ============================================================

expected_all = (
    "UNIVERSAL_ORCHESTRATION_DEPENDENCY_RESOLUTION_VERSION",
    "UNIVERSAL_ORCHESTRATION_DEPENDENCY_RESOLUTION_SCHEMA_VERSION",
    "UniversalOrchestrationDependencyResolutionError",
    "UniversalOrchestrationDependencyClassification",
    "SATISFIED_UNIVERSAL_JOB_STATUSES",
    "TERMINAL_UNSATISFIED_UNIVERSAL_JOB_STATUSES",
    "UNRESOLVED_UNIVERSAL_JOB_STATUSES",
    "classify_universal_orchestration_dependency_status",
    "UniversalOrchestrationDependencyResolution",
    "resolve_universal_orchestration_dependencies",
    "explain_universal_orchestration_dependency_resolution_v1",
)


check(
    "api_surface_exact",
    tuple(
        dependency.__all__
    )
    == expected_all,
    dependency.__all__,
)


# ============================================================
# 50 — PROTECTED AUTHORITY MATRIX
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
# 51 — FINAL PRODUCTION AST
# ============================================================

final_ast = ast_sha(
    DEPENDENCY_PATH
)


check(
    "dependency_ast_final",
    final_ast
    == EXPECTED_DEPENDENCY_AST,
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
        "PHASE 5.1.4 — UNIVERSAL ORCHESTRATION "
        "DEPENDENCY RESOLUTION ADVERSARIAL REGRESSION"
    ),
    "=" * 118,
    "",
    (
        "DEPENDENCY RESOLUTION AST SHA256: "
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
            "ADVERSARIAL DEPENDENCY RESOLUTION REGRESSION: "
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
        "DEPENDENCY RESOLUTION AST MODIFIED: NO",
        "5.1.1 ORCHESTRATION CONTRACT MODIFIED: NO",
        "5.1.2 RUN IDENTITY MODIFIED: NO",
        "5.1.3 STATE MODEL MODIFIED: NO",
        "PHASE 1–4 FROZEN AUTHORITIES MODIFIED: NO",
        "UNIVERSAL JOB CONTRACT MODIFIED: NO",
        "UNIVERSAL JOB LINEAGE MODIFIED: NO",
        "UNIVERSAL JOB STATUS MODIFIED: NO",
        "QUEUE INFRASTRUCTURE MODIFIED: NO",
        "RUNTIME REGISTRATION MODIFIED: NO",
        "RUNTIME WORKER MODIFIED: NO",
        "RUNTIME INFRASTRUCTURE MODIFIED: NO",
        "",
        "DEPENDENCY_JOB_IDS REDEFINED: NO",
        "PARENT_JOB_ID TREATED AS IMPLICIT DEPENDENCY: NO",
        "MISSING EVIDENCE TREATED AS FAILURE: NO",
        "NONTERMINAL STATUS TREATED AS FAILURE: NO",
        "TERMINAL FAILURE TREATED AS UNRESOLVED: NO",
        "",
        "CROSS-JOB CYCLE DETECTION PERFORMED: NO",
        "EXECUTION ORDER DEFINED: NO",
        "EXECUTION PLAN CREATED: NO",
        "READINESS DETERMINED: NO",
        "READY/BLOCKED DETERMINED: NO",
        "ORCHESTRATION STATE TRANSITIONED: NO",
        "",
        "QUEUE/WORKER ACTIVITY: NO",
        "RUNTIME HANDLER ACTIVITY: NO",
        "JOB EXECUTION: NO",
        "UNIVERSAL COORDINATION FRAMEWORK ACCESSED: NO",
        "PIPELINE COORDINATORS ACCESSED: NO",
        "RUNTIME STATE STORE ACCESSED: NO",
        "JOB PERSISTENCE QUERIED: NO",
        "DEPENDENCY RESOLUTION PERSISTED: NO",
        "WALL CLOCK USED: NO",
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
            "Phase 5.1.4 Dependency Resolution "
            "adversarial regression failed."
        )
    )
