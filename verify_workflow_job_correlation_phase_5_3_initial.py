from __future__ import annotations

import ast
import hashlib
import inspect
from dataclasses import FrozenInstanceError, fields, replace
from pathlib import Path
from types import MappingProxyType

from backend.server.coordination.runtime_integration.coordination_runtime_bridge import (
    RuntimeHandoffIntent,
)

from backend.server.coordination.runtime_integration.runtime_job_mapping import (
    RuntimeJobMapping,
    map_runtime_handoff_intent_to_creation_request,
)

from backend.server.coordination.runtime_integration.workflow_job_correlation import (
    WORKFLOW_JOB_CORRELATION_VERSION,
    WORKFLOW_JOB_CORRELATION_SCHEMA_VERSION,
    WORKFLOW_JOB_CORRELATION_FIELD_COUNT,
    WorkflowJobCorrelation,
    WorkflowJobCorrelationRegistry,
    WorkflowJobCorrelationError,
    WorkflowJobCorrelationValidationError,
    WorkflowJobCorrelationConflictError,
    correlate_submitted_job,
    register_workflow_job_correlation,
    resolve_workflow_job_correlation,
    get_workflow_job_correlation_registry,
    workflow_job_correlation_snapshot,
    explain_workflow_job_correlation_v5_3,
)


ROOT = Path.cwd()

TARGET = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "workflow_job_correlation.py"
)

PHASE_5_2 = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "runtime_job_mapping.py"
)

SUBMISSION = (
    ROOT
    / "backend/server/runtime/"
      "universal_job_submission.py"
)

REPORT = (
    ROOT
    / "workflow_job_correlation_phase_5_3_initial_verification.txt"
)


EXPECTED_TARGET_SHA = (
    "C0D88ECC69680106B6833DF8CB3113FC"
    "9ABD23C1EE8B7D413BA4AAE3375648FA"
)

EXPECTED_5_2_SHA = (
    "49227B0686DED28418DE7DEF21101643"
    "18DDCA3858469A05F5A596388BA84E6A"
)

EXPECTED_SUBMISSION_SHA = (
    "07BA2DA8C0A2CFA899DE696D7892652"
    "A0AA6D56939B364C8C6B7F0B741B05704"
)


checks = []


def check(
    name,
    condition,
    detail="",
):
    ok = bool(condition)

    checks.append(
        (
            name,
            ok,
            detail,
        )
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if detail:
        print(
            "    "
            + detail
        )


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def expect_validation_error(
    name,
    fn,
    *,
    expected_fragment=None,
):

    try:
        fn()

    except WorkflowJobCorrelationValidationError as exc:

        ok = (
            expected_fragment is None
            or expected_fragment
            in str(exc)
            or any(
                expected_fragment
                in item
                for item
                in exc.violations
            )
        )

        check(
            name,
            ok,
            str(exc),
        )

        return

    except Exception as exc:

        check(
            name,
            False,
            "Unexpected exception: "
            + repr(exc),
        )

        return

    check(
        name,
        False,
        "Expected WorkflowJobCorrelationValidationError.",
    )


def make_mapping(
    *,
    workflow_id="wf_initial_5_3",
    correlation_id="corr_initial_5_3",
    stage_id="stage_a",
    stage_version="stage_a_v1",
    workflow_type="initial_workflow",
    workspace_id="ws_initial_5_3",
    pipeline_id="pipeline_initial",
    job_type="initial.stage_a",
    runtime_stage="runtime_stage_a",
    wave_index=0,
):

    intent = RuntimeHandoffIntent(
        workflow_id=workflow_id,
        workspace_id=workspace_id,
        correlation_id=correlation_id,
        stage_id=stage_id,
        stage_version=stage_version,
        pipeline_id=pipeline_id,
        workflow_type=workflow_type,
        job_type=job_type,
        runtime_stage=runtime_stage,
        required_payload_fields=(
            "document_id",
        ),
        wave_index=wave_index,
        execution_semantics="parallel_eligible",
        payload={
            "document_id":
                "doc_initial_5_3",

            "nested": {
                "source":
                    "initial_verification",
            },
        },
        metadata={
            "source":
                "phase_5_3_initial_verification",
        },
        stage_reference_contract_version=(
            "universal_stage_reference_contract_v1.3.0"
        ),
    )

    return map_runtime_handoff_intent_to_creation_request(
        intent=intent
    )


def make_submitted_job(
    mapping,
    *,
    job_id,
):

    request = mapping.creation_request

    return {
        "job_id":
            job_id,

        "workspace_id":
            request.workspace_id,

        "job_type":
            request.job_type,

        "pipeline":
            request.pipeline,

        "stage":
            request.stage,

        "pipeline_run_id":
            None,

        "submission": {
            "persisted":
                True,

            "queued":
                True,

            "canonical_identity_preserved":
                True,
        },
    }


print()
print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 5.3 — WORKFLOW/JOB CORRELATION")
print("INITIAL VERIFICATION")
print("=" * 120)


# =========================================================================
# 1. Exact artifact integrity
# =========================================================================

target_sha = sha256(
    TARGET
)

check(
    "Phase 5.3 candidate SHA exact",
    target_sha
    == EXPECTED_TARGET_SHA,
    target_sha,
)

check(
    "Frozen Phase 5.2 SHA exact",
    sha256(
        PHASE_5_2
    )
    == EXPECTED_5_2_SHA,
    sha256(
        PHASE_5_2
    ),
)

check(
    "Universal Job Submission SHA exact",
    sha256(
        SUBMISSION
    )
    == EXPECTED_SUBMISSION_SHA,
    sha256(
        SUBMISSION
    ),
)


# =========================================================================
# 2. Contract identity
# =========================================================================

check(
    "Version exact",
    WORKFLOW_JOB_CORRELATION_VERSION
    == "workflow_job_correlation_v5.3.0",
)

check(
    "Schema exact",
    WORKFLOW_JOB_CORRELATION_SCHEMA_VERSION
    == "workflow_job_correlation_schema_v1",
)

expected_fields = (
    "workflow_id",
    "correlation_id",
    "stage_id",
    "stage_version",
    "workflow_type",
    "workspace_id",
    "job_id",
    "job_type",
    "pipeline_id",
    "runtime_stage",
    "wave_index",
)

actual_fields = tuple(
    item.name
    for item
    in fields(
        WorkflowJobCorrelation
    )
)

check(
    "Correlation field order exact",
    actual_fields
    == expected_fields,
    repr(
        actual_fields
    ),
)

check(
    "Correlation field count constant exact",
    WORKFLOW_JOB_CORRELATION_FIELD_COUNT
    == len(
        expected_fields
    )
    == 11,
)


# =========================================================================
# 3. End-to-end binding
# =========================================================================

registry = WorkflowJobCorrelationRegistry()

mapping_a = make_mapping(
    stage_id="stage_a",
    stage_version="stage_a_v1",
    job_type="initial.stage_a",
    runtime_stage="runtime_stage_a",
    wave_index=0,
)

submitted_a = make_submitted_job(
    mapping_a,
    job_id="uj_initial_a",
)

binding_a = register_workflow_job_correlation(
    mapping=mapping_a,
    submitted_job=submitted_a,
    registry=registry,
)

check(
    "Binding result type exact",
    isinstance(
        binding_a,
        WorkflowJobCorrelation,
    ),
)

check(
    "Canonical job_id exact",
    binding_a.job_id
    == "uj_initial_a",
)

check(
    "Workflow identity exact",
    binding_a.workflow_id
    == "wf_initial_5_3",
)

check(
    "Correlation identity exact",
    binding_a.correlation_id
    == "corr_initial_5_3",
)

check(
    "Coordination stage identity exact",
    binding_a.stage_id
    == "stage_a",
)

check(
    "Runtime stage identity exact",
    binding_a.runtime_stage
    == "runtime_stage_a",
)


# =========================================================================
# 4. Deterministic reverse lookup
# =========================================================================

resolved_a = resolve_workflow_job_correlation(
    job_id="uj_initial_a",
    registry=registry,
)

check(
    "Reverse lookup deterministic",
    resolved_a
    == binding_a,
)

check(
    "Repeated reverse lookup deterministic",
    resolve_workflow_job_correlation(
        job_id="uj_initial_a",
        registry=registry,
    )
    == binding_a,
)

snapshot_a = workflow_job_correlation_snapshot(
    binding_a
)

snapshot_b = workflow_job_correlation_snapshot(
    resolved_a
)

check(
    "Repeated snapshots deterministic",
    dict(
        snapshot_a
    )
    == dict(
        snapshot_b
    ),
)


# =========================================================================
# 5. Idempotency
# =========================================================================

repeat_binding = register_workflow_job_correlation(
    mapping=mapping_a,
    submitted_job=submitted_a,
    registry=registry,
)

check(
    "Exact repeat registration is idempotent",
    repeat_binding
    == binding_a,
)

check(
    "Exact repeat preserves registry cardinality",
    registry.count()
    == 1,
)


# =========================================================================
# 6. Conflicting duplicate protection
# =========================================================================

conflicting_record = replace(
    binding_a,
    correlation_id="corr_conflict",
)

conflict_seen = False

try:
    registry.register(
        conflicting_record
    )

except WorkflowJobCorrelationConflictError as exc:

    conflict_seen = (
        exc.job_id
        == binding_a.job_id
    )


check(
    "Conflicting duplicate rejected",
    conflict_seen,
)

check(
    "Conflicting duplicate leaves registry unchanged",
    registry.count()
    == 1
    and registry.require_by_job_id(
        "uj_initial_a"
    )
    == binding_a,
)


# =========================================================================
# 7. Multiple job support
# =========================================================================

mapping_b = make_mapping(
    stage_id="stage_b",
    stage_version="stage_b_v1",
    job_type="initial.stage_b",
    runtime_stage="runtime_stage_b",
    wave_index=1,
)

submitted_b = make_submitted_job(
    mapping_b,
    job_id="uj_initial_b",
)

binding_b = register_workflow_job_correlation(
    mapping=mapping_b,
    submitted_job=submitted_b,
    registry=registry,
)

check(
    "Second stage/job binding accepted",
    binding_b.job_id
    == "uj_initial_b",
)

check(
    "One workflow can own multiple jobs",
    registry.count()
    == 2,
)

workflow_bindings = registry.all_for_workflow(
    "wf_initial_5_3"
)

check(
    "Workflow lookup returns all jobs",
    tuple(
        item.job_id
        for item
        in workflow_bindings
    )
    == (
        "uj_initial_a",
        "uj_initial_b",
    ),
)


# =========================================================================
# 8. Same stage may own historical multiple jobs
# =========================================================================

mapping_retry = make_mapping(
    stage_id="stage_a",
    stage_version="stage_a_v1",
    job_type="initial.stage_a",
    runtime_stage="runtime_stage_a",
    wave_index=2,
)

submitted_retry = make_submitted_job(
    mapping_retry,
    job_id="uj_initial_a_retry",
)

binding_retry = register_workflow_job_correlation(
    mapping=mapping_retry,
    submitted_job=submitted_retry,
    registry=registry,
)

check(
    "Same workflow stage may bind another canonical job",
    binding_retry.stage_id
    == "stage_a"
    and binding_retry.job_id
    == "uj_initial_a_retry",
)

check(
    "Stage/job history does not enforce stage uniqueness",
    registry.count()
    == 3,
)


# =========================================================================
# 9. Exact Runtime cross-validation failures
# =========================================================================

for (
    field_name,
    wrong_value,
    expected_fragment,
) in (
    (
        "workspace_id",
        "wrong_workspace",
        "workspace_id mismatch",
    ),
    (
        "job_type",
        "wrong.job_type",
        "job_type mismatch",
    ),
    (
        "pipeline",
        "wrong_pipeline",
        "pipeline mismatch",
    ),
    (
        "stage",
        "wrong_stage",
        "stage mismatch",
    ),
):

    candidate = dict(
        submitted_a
    )

    candidate[
        field_name
    ] = wrong_value

    expect_validation_error(
        (
            "Cross-validation rejects "
            + field_name
        ),
        lambda candidate=candidate:
            correlate_submitted_job(
                mapping=mapping_a,
                submitted_job=candidate,
                registry=WorkflowJobCorrelationRegistry(),
            ),
        expected_fragment=expected_fragment,
    )


# =========================================================================
# 10. Required submitted identity
# =========================================================================

for field_name in (
    "job_id",
    "workspace_id",
    "job_type",
    "pipeline",
    "stage",
):

    candidate = dict(
        submitted_a
    )

    candidate.pop(
        field_name
    )

    expect_validation_error(
        (
            "Missing submitted field rejected: "
            + field_name
        ),
        lambda candidate=candidate:
            correlate_submitted_job(
                mapping=mapping_a,
                submitted_job=candidate,
                registry=WorkflowJobCorrelationRegistry(),
            ),
    )


# =========================================================================
# 11. Type protection
# =========================================================================

expect_validation_error(
    "Non-RuntimeJobMapping rejected",
    lambda:
        correlate_submitted_job(
            mapping={},
            submitted_job=submitted_a,
            registry=WorkflowJobCorrelationRegistry(),
        ),
)

expect_validation_error(
    "Non-mapping submitted job rejected",
    lambda:
        correlate_submitted_job(
            mapping=mapping_a,
            submitted_job=[],
            registry=WorkflowJobCorrelationRegistry(),
        ),
)

expect_validation_error(
    "Wrong registry rejected",
    lambda:
        correlate_submitted_job(
            mapping=mapping_a,
            submitted_job=submitted_a,
            registry={},
        ),
)


# =========================================================================
# 12. Immutability
# =========================================================================

frozen = False

try:
    binding_a.workflow_id = "mutated"

except (
    FrozenInstanceError,
    AttributeError,
):
    frozen = True


check(
    "Correlation record immutable",
    frozen,
)

check(
    "Correlation snapshot immutable",
    isinstance(
        snapshot_a,
        MappingProxyType,
    ),
)


# =========================================================================
# 13. Architecture declaration exactness
# =========================================================================

architecture = explain_workflow_job_correlation_v5_3()

check(
    "Architecture declaration immutable",
    isinstance(
        architecture,
        MappingProxyType,
    ),
)

check(
    "Coordination input exact",
    architecture[
        "coordination_input"
    ]
    == "RuntimeJobMapping",
)

check(
    "Runtime identity input exact",
    architecture[
        "runtime_identity_input"
    ]
    == "successful submitted canonical job",
)

check(
    "Binding time exact",
    architecture[
        "binding_time"
    ]
    == "after successful canonical submission",
)

check(
    "Primary reverse lookup exact",
    architecture[
        "primary_reverse_lookup"
    ]
    == "job_id",
)

check(
    "Cross-validation set exact",
    architecture[
        "cross_validation"
    ]
    == (
        "workspace_id",
        "job_type",
        "pipeline",
        "stage",
    ),
)

check(
    "Persistence owner exact",
    architecture[
        "persistence_owner"
    ]
    == "Phase 8 Workflow State Persistence",
)


# =========================================================================
# 14. Authority boundaries
# =========================================================================

for key in (
    "job_id_generation",
    "job_id_rewrite",
    "workflow_id_to_pipeline_run_id",
    "correlation_id_to_pipeline_run_id",
    "orchestration_run_id_generation",
):

    check(
        "Identity boundary false: "
        + key,
        architecture[
            "identity_boundaries"
        ][
            key
        ]
        is False,
    )


for key in (
    "universal_job_creation",
    "runtime_registration_lookup",
    "submission",
    "runtime_persistence",
    "queue_write",
    "dispatch",
    "business_execution",
    "workflow_lifecycle_transition",
    "completion_processing",
    "failure_processing",
    "persistent_correlation_storage",
):

    check(
        "Execution authority false: "
        + key,
        architecture[
            "execution_properties"
        ][
            key
        ]
        is False,
    )


# =========================================================================
# 15. Public API shape
# =========================================================================

check(
    "Correlation function keyword-only",
    str(
        inspect.signature(
            correlate_submitted_job
        )
    ).startswith(
        "(*,"
    ),
)

check(
    "Registration wrapper keyword-only",
    str(
        inspect.signature(
            register_workflow_job_correlation
        )
    ).startswith(
        "(*,"
    ),
)

check(
    "Resolution wrapper keyword-only",
    str(
        inspect.signature(
            resolve_workflow_job_correlation
        )
    ).startswith(
        "(*,"
    ),
)

check(
    "Validation error subclasses Phase 5.3 error",
    issubclass(
        WorkflowJobCorrelationValidationError,
        WorkflowJobCorrelationError,
    ),
)

check(
    "Conflict error subclasses Phase 5.3 error",
    issubclass(
        WorkflowJobCorrelationConflictError,
        WorkflowJobCorrelationError,
    ),
)


# =========================================================================
# 16. Default registry authority
# =========================================================================

default_a = get_workflow_job_correlation_registry()
default_b = get_workflow_job_correlation_registry()

check(
    "Default registry singleton stable",
    default_a
    is default_b,
)

check(
    "Default registry correct type",
    isinstance(
        default_a,
        WorkflowJobCorrelationRegistry,
    ),
)


# =========================================================================
# 17. Static Runtime isolation
# =========================================================================

source = TARGET.read_text(
    encoding="utf-8"
)

tree = ast.parse(
    source
)

runtime_imports = []

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
            "backend.server.runtime"
        ):

            runtime_imports.append(
                module
            )

    elif isinstance(
        node,
        ast.Import,
    ):

        for alias in node.names:

            if alias.name.startswith(
                "backend.server.runtime"
            ):

                runtime_imports.append(
                    alias.name
                )


check(
    "No Runtime production imports",
    runtime_imports
    == [],
    repr(
        runtime_imports
    ),
)


# =========================================================================
# 18. Forbidden calls
# =========================================================================

forbidden_calls = {
    "create_universal_job",
    "submit_universal_job",
    "get_runtime_registration",
    "create_orchestration_job",
    "dispatch_registered_runtime_handler",
    "execute_registered_runtime_job_v1",
    "write_text",
    "write_bytes",
    "mkdir",
    "unlink",
    "open",
}

called = set()

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
        called.add(
            node.func.id
        )

    elif isinstance(
        node.func,
        ast.Attribute,
    ):
        called.add(
            node.func.attr
        )


hits = (
    called
    & forbidden_calls
)

check(
    "No forbidden Runtime/filesystem calls",
    hits
    == set(),
    repr(
        sorted(
            hits
        )
    ),
)


# =========================================================================
# 19. No pipeline_run_id mutation semantics
# =========================================================================

check(
    "No pipeline_run_id assignment in Phase 5.3 source",
    "pipeline_run_id="
    not in source,
)

check(
    "No orchestration_run_id assignment in Phase 5.3 source",
    "orchestration_run_id="
    not in source,
)


# =========================================================================
# Final
# =========================================================================

passed = sum(
    1
    for _, ok, _
    in checks
    if ok
)

failed = (
    len(
        checks
    )
    - passed
)


lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.3 — WORKFLOW/JOB CORRELATION",
    "INITIAL VERIFICATION",
    "=" * 120,
    "",
]


for (
    name,
    ok,
    detail,
) in checks:

    lines.append(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if detail:
        lines.append(
            "    "
            + detail
        )


lines.extend(
    (
        "",
        "=" * 120,
        "INITIAL VERIFICATION RESULT",
        "=" * 120,
        f"Checks: {len(checks)}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        (
            "STATUS: INITIAL VERIFICATION PASSED"
            if failed == 0
            else "STATUS: INITIAL VERIFICATION FAILED"
        ),
        f"PHASE 5.3 SHA256: {target_sha}",
    )
)


REPORT.write_text(
    "\n".join(
        lines
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 120)
print("INITIAL VERIFICATION RESULT")
print("=" * 120)
print(
    "Checks:",
    len(
        checks
    ),
)
print(
    "Passed:",
    passed,
)
print(
    "Failed:",
    failed,
)
print(
    "STATUS:",
    (
        "INITIAL VERIFICATION PASSED"
        if failed == 0
        else "INITIAL VERIFICATION FAILED"
    ),
)
print(
    "PHASE 5.3 SHA256:",
    target_sha,
)
print(
    "REPORT:",
    REPORT.name,
)
print("=" * 120)

raise SystemExit(
    0
    if failed == 0
    else 1
)
