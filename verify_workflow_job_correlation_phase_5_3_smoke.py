from __future__ import annotations

import ast
import hashlib
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
    WorkflowJobCorrelationValidationError,
    WorkflowJobCorrelationConflictError,
    correlate_submitted_job,
    register_workflow_job_correlation,
    resolve_workflow_job_correlation,
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
    / "workflow_job_correlation_phase_5_3_installation_smoke.txt"
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


def sha256(
    path: Path,
) -> str:

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def expect_validation_error(
    name,
    fn,
):

    try:
        fn()

    except WorkflowJobCorrelationValidationError as exc:
        check(
            name,
            True,
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
    workflow_id="wf_smoke_5_3",
    correlation_id="corr_smoke_5_3",
    stage_id="stage_a",
    stage_version="stage_a_v1",
    workflow_type="smoke_workflow",
    workspace_id="ws_smoke_5_3",
    pipeline_id="pipeline_smoke",
    job_type="smoke.stage_a",
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
            "document_id": "doc_smoke",
        },
        metadata={
            "source":
                "phase_5_3_installation_smoke",
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
    job_id="uj_smoke_5_3",
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
print("PHASE 5.3 — WORKFLOW/JOB CORRELATION INSTALLATION SMOKE")
print("=" * 120)


# =========================================================================
# 1. Installation integrity
# =========================================================================

check(
    "Phase 5.3 production file exists",
    TARGET.exists(),
)

source = TARGET.read_text(
    encoding="utf-8"
)

try:
    tree = ast.parse(
        source
    )

    syntax_ok = True

except SyntaxError:
    tree = None
    syntax_ok = False


check(
    "Phase 5.3 Python syntax parses",
    syntax_ok,
)


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

check(
    "Correlation field count constant exact",
    WORKFLOW_JOB_CORRELATION_FIELD_COUNT
    == 11,
)

check(
    "Correlation dataclass field count exact",
    len(
        fields(
            WorkflowJobCorrelation
        )
    )
    == 11,
)


# =========================================================================
# 2. Frozen authority integrity
# =========================================================================

phase_5_2_sha = sha256(
    PHASE_5_2
)

submission_sha = sha256(
    SUBMISSION
)

check(
    "Frozen Phase 5.2 SHA exact",
    phase_5_2_sha
    == EXPECTED_5_2_SHA,
    phase_5_2_sha,
)

check(
    "Universal Job Submission SHA exact",
    submission_sha
    == EXPECTED_SUBMISSION_SHA,
    submission_sha,
)


# =========================================================================
# 3. Happy-path correlation
# =========================================================================

mapping = make_mapping()

submitted = make_submitted_job(
    mapping
)

registry = WorkflowJobCorrelationRegistry()

correlation = correlate_submitted_job(
    mapping=mapping,
    submitted_job=submitted,
    registry=registry,
)


check(
    "Correlation result type exact",
    isinstance(
        correlation,
        WorkflowJobCorrelation,
    ),
)

check(
    "workflow_id preserved",
    correlation.workflow_id
    == "wf_smoke_5_3",
)

check(
    "correlation_id preserved",
    correlation.correlation_id
    == "corr_smoke_5_3",
)

check(
    "stage_id preserved",
    correlation.stage_id
    == "stage_a",
)

check(
    "stage_version preserved",
    correlation.stage_version
    == "stage_a_v1",
)

check(
    "workflow_type preserved",
    correlation.workflow_type
    == "smoke_workflow",
)

check(
    "workspace_id cross-bound correctly",
    correlation.workspace_id
    == "ws_smoke_5_3",
)

check(
    "canonical job_id preserved",
    correlation.job_id
    == "uj_smoke_5_3",
)

check(
    "job_type preserved",
    correlation.job_type
    == "smoke.stage_a",
)

check(
    "pipeline_id preserved",
    correlation.pipeline_id
    == "pipeline_smoke",
)

check(
    "runtime_stage preserved",
    correlation.runtime_stage
    == "runtime_stage_a",
)

check(
    "wave_index preserved",
    correlation.wave_index
    == 0,
)


# =========================================================================
# 4. Reverse lookup
# =========================================================================

check(
    "Registry count exact after registration",
    registry.count()
    == 1,
)

resolved = registry.require_by_job_id(
    "uj_smoke_5_3"
)

check(
    "Reverse lookup returns exact binding",
    resolved
    == correlation,
)

check(
    "get_by_job_id returns exact binding",
    registry.get_by_job_id(
        "uj_smoke_5_3"
    )
    == correlation,
)

check(
    "Unknown job lookup returns None",
    registry.get_by_job_id(
        "uj_unknown"
    )
    is None,
)

expect_validation_error(
    "Unknown required job lookup fails closed",
    lambda:
        registry.require_by_job_id(
            "uj_unknown"
        ),
)


# =========================================================================
# 5. Idempotent duplicate
# =========================================================================

same = correlate_submitted_job(
    mapping=mapping,
    submitted_job=submitted,
    registry=registry,
)

check(
    "Exact duplicate returns same binding",
    same
    == correlation,
)

check(
    "Exact duplicate does not increase count",
    registry.count()
    == 1,
)


# =========================================================================
# 6. Conflicting duplicate
# =========================================================================

conflicting = replace(
    correlation,
    workflow_id="wf_conflict",
)

conflict_blocked = False

try:
    registry.register(
        conflicting
    )

except WorkflowJobCorrelationConflictError as exc:

    conflict_blocked = (
        exc.job_id
        == "uj_smoke_5_3"
    )


check(
    "Conflicting duplicate fails closed",
    conflict_blocked,
)

check(
    "Conflict does not alter original binding",
    registry.require_by_job_id(
        "uj_smoke_5_3"
    )
    == correlation,
)


# =========================================================================
# 7. Runtime cross-validation
# =========================================================================

bad_workspace = dict(
    submitted
)

bad_workspace[
    "workspace_id"
] = "ws_wrong"

expect_validation_error(
    "workspace_id mismatch rejected",
    lambda:
        correlate_submitted_job(
            mapping=mapping,
            submitted_job=bad_workspace,
            registry=WorkflowJobCorrelationRegistry(),
        ),
)


bad_job_type = dict(
    submitted
)

bad_job_type[
    "job_type"
] = "wrong.job"

expect_validation_error(
    "job_type mismatch rejected",
    lambda:
        correlate_submitted_job(
            mapping=mapping,
            submitted_job=bad_job_type,
            registry=WorkflowJobCorrelationRegistry(),
        ),
)


bad_pipeline = dict(
    submitted
)

bad_pipeline[
    "pipeline"
] = "wrong_pipeline"

expect_validation_error(
    "pipeline mismatch rejected",
    lambda:
        correlate_submitted_job(
            mapping=mapping,
            submitted_job=bad_pipeline,
            registry=WorkflowJobCorrelationRegistry(),
        ),
)


bad_stage = dict(
    submitted
)

bad_stage[
    "stage"
] = "wrong_runtime_stage"

expect_validation_error(
    "runtime stage mismatch rejected",
    lambda:
        correlate_submitted_job(
            mapping=mapping,
            submitted_job=bad_stage,
            registry=WorkflowJobCorrelationRegistry(),
        ),
)


# =========================================================================
# 8. Missing canonical identity protection
# =========================================================================

missing_job_id = dict(
    submitted
)

missing_job_id.pop(
    "job_id"
)

expect_validation_error(
    "Missing canonical job_id rejected",
    lambda:
        correlate_submitted_job(
            mapping=mapping,
            submitted_job=missing_job_id,
            registry=WorkflowJobCorrelationRegistry(),
        ),
)


expect_validation_error(
    "Non-mapping submitted job rejected",
    lambda:
        correlate_submitted_job(
            mapping=mapping,
            submitted_job=None,
            registry=WorkflowJobCorrelationRegistry(),
        ),
)


expect_validation_error(
    "Wrong registry type rejected",
    lambda:
        correlate_submitted_job(
            mapping=mapping,
            submitted_job=submitted,
            registry=None,
        ),
)


# =========================================================================
# 9. Workflow multi-job semantics
# =========================================================================

mapping_b = make_mapping(
    stage_id="stage_b",
    stage_version="stage_b_v1",
    job_type="smoke.stage_b",
    runtime_stage="runtime_stage_b",
    wave_index=1,
)

submitted_b = make_submitted_job(
    mapping_b,
    job_id="uj_smoke_5_3_b",
)

correlation_b = correlate_submitted_job(
    mapping=mapping_b,
    submitted_job=submitted_b,
    registry=registry,
)

check(
    "One workflow may own multiple jobs",
    registry.count()
    == 2,
)

workflow_bindings = registry.all_for_workflow(
    "wf_smoke_5_3"
)

check(
    "Workflow lookup returns two bindings",
    len(
        workflow_bindings
    )
    == 2,
)

check(
    "Workflow lookup preserves insertion order",
    tuple(
        item.job_id
        for item
        in workflow_bindings
    )
    == (
        "uj_smoke_5_3",
        "uj_smoke_5_3_b",
    ),
)


# =========================================================================
# 10. Immutability
# =========================================================================

frozen = False

try:
    correlation.job_id = "changed"

except (
    FrozenInstanceError,
    AttributeError,
):
    frozen = True


check(
    "WorkflowJobCorrelation immutable",
    frozen,
)


snapshot = workflow_job_correlation_snapshot(
    correlation
)

check(
    "Snapshot immutable mapping",
    isinstance(
        snapshot,
        MappingProxyType,
    ),
)

check(
    "Snapshot job_id exact",
    snapshot[
        "job_id"
    ]
    == "uj_smoke_5_3",
)

check(
    "Snapshot version exact",
    snapshot[
        "version"
    ]
    == WORKFLOW_JOB_CORRELATION_VERSION,
)


# =========================================================================
# 11. Public wrapper behavior
# =========================================================================

wrapper_registry = WorkflowJobCorrelationRegistry()

wrapper_record = register_workflow_job_correlation(
    mapping=mapping,
    submitted_job=submitted,
    registry=wrapper_registry,
)

check(
    "Public registration wrapper succeeds",
    wrapper_record
    == correlation,
)

wrapper_resolved = resolve_workflow_job_correlation(
    job_id="uj_smoke_5_3",
    registry=wrapper_registry,
)

check(
    "Public reverse lookup wrapper succeeds",
    wrapper_resolved
    == correlation,
)


# =========================================================================
# 12. Architecture declaration
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
    "Architecture phase exact",
    architecture[
        "phase"
    ]
    == "5.3",
)

check(
    "Architecture primary lookup exact",
    architecture[
        "primary_reverse_lookup"
    ]
    == "job_id",
)

check(
    "Binding occurs after submission",
    architecture[
        "binding_time"
    ]
    == "after successful canonical submission",
)

check(
    "Exact duplicate policy exact",
    architecture[
        "duplicate_policy"
    ][
        "exact_duplicate"
    ]
    == "idempotent_reuse",
)

check(
    "Conflicting duplicate policy exact",
    architecture[
        "duplicate_policy"
    ][
        "conflicting_duplicate"
    ]
    == "fail_closed",
)

check(
    "Persistence owner deferred to Phase 8",
    architecture[
        "persistence_owner"
    ]
    == "Phase 8 Workflow State Persistence",
)


for key in (
    "job_id_generation",
    "job_id_rewrite",
    "workflow_id_to_pipeline_run_id",
    "correlation_id_to_pipeline_run_id",
    "orchestration_run_id_generation",
):

    check(
        "Identity authority disabled: "
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
        "Execution authority disabled: "
        + key,
        architecture[
            "execution_properties"
        ][
            key
        ]
        is False,
    )


# =========================================================================
# 13. Static import boundary
# =========================================================================

runtime_imports = []

if tree is not None:

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
    "Phase 5.3 imports no Runtime production module",
    runtime_imports
    == [],
    repr(
        runtime_imports
    ),
)


# =========================================================================
# 14. Static forbidden-call boundary
# =========================================================================

forbidden = {
    "create_universal_job",
    "submit_universal_job",
    "get_runtime_registration",
    "create_orchestration_job",
    "dispatch_registered_runtime_handler",
    "execute_registered_runtime_job_v1",
    "open",
    "write_text",
    "write_bytes",
    "mkdir",
    "unlink",
}


called = set()

if tree is not None:

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


forbidden_hits = (
    called
    & forbidden
)


check(
    "No forbidden Runtime or filesystem calls",
    forbidden_hits
    == set(),
    repr(
        sorted(
            forbidden_hits
        )
    ),
)


# =========================================================================
# 15. Candidate SHA
# =========================================================================

candidate_sha = sha256(
    TARGET
)

check(
    "Candidate SHA256 structurally valid",
    len(
        candidate_sha
    )
    == 64
    and all(
        char
        in "0123456789ABCDEF"
        for char
        in candidate_sha
    ),
    candidate_sha,
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
    "INSTALLATION SMOKE",
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
        "PHASE 5.3 INSTALLATION SMOKE RESULT",
        "=" * 120,
        f"Checks: {len(checks)}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        (
            "STATUS: SMOKE PASSED"
            if failed == 0
            else "STATUS: SMOKE FAILED"
        ),
        f"PHASE 5.3 CANDIDATE SHA256: {candidate_sha}",
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
print("PHASE 5.3 INSTALLATION SMOKE RESULT")
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
        "SMOKE PASSED"
        if failed == 0
        else "SMOKE FAILED"
    ),
)
print(
    "PHASE 5.3 CANDIDATE SHA256:",
    candidate_sha,
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
