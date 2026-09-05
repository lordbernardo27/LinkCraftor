from __future__ import annotations

import ast
import hashlib
import inspect
import subprocess
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

STAGE_RESULT = (
    ROOT
    / "backend/server/coordination/universal_stages/"
      "result_contract.py"
)

RUN_IDENTITY = (
    ROOT
    / "backend/server/runtime/universal_orchestration/"
      "run_identity.py"
)

REPORT = (
    ROOT
    / "workflow_job_correlation_phase_5_3_final_certification.txt"
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

EXPECTED_STAGE_RESULT_SHA = (
    "B3469B10BB2F8F9372E4336784D09A14"
    "3C78FABE45BF039B61B76F4A2DC33B24"
)

EXPECTED_RUN_IDENTITY_SHA = (
    "B43C2C86B07F06FA3B89C4BF2B14E68"
    "DC82DEA1E23112AE44E35139266AA6626"
)


checks = []


def check(name, condition, detail=""):
    ok = bool(condition)
    checks.append((name, ok, detail))

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if detail:
        print(
            "    " + detail
        )


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


def expect_validation_error(name, fn):
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
            "Unexpected exception: " + repr(exc),
        )
        return

    check(
        name,
        False,
        "Expected WorkflowJobCorrelationValidationError.",
    )


def make_mapping(
    *,
    workflow_id="wf_final_5_3",
    correlation_id="corr_final_5_3",
    stage_id="stage_a",
    stage_version="stage_a_v1",
    workflow_type="final_workflow",
    workspace_id="ws_final_5_3",
    pipeline_id="pipeline_final",
    job_type="final.stage_a",
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
            "document_id": "doc_final_5_3",
        },
        metadata={
            "source":
                "phase_5_3_final_certification",
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
        "job_id": job_id,
        "workspace_id": request.workspace_id,
        "job_type": request.job_type,
        "pipeline": request.pipeline,
        "stage": request.stage,
        "pipeline_run_id": None,
        "submission": {
            "persisted": True,
            "queued": True,
            "canonical_identity_preserved": True,
        },
    }


print()
print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 5.3 — WORKFLOW/JOB CORRELATION")
print("FINAL CERTIFICATION")
print("=" * 120)


# =========================================================================
# 1. Artifact integrity
# =========================================================================

target_sha = sha256(TARGET)

check(
    "Phase 5.3 candidate SHA exact",
    target_sha == EXPECTED_TARGET_SHA,
    target_sha,
)

check(
    "Frozen Phase 5.2 SHA exact",
    sha256(PHASE_5_2) == EXPECTED_5_2_SHA,
    sha256(PHASE_5_2),
)

check(
    "Universal Job Submission SHA exact",
    sha256(SUBMISSION) == EXPECTED_SUBMISSION_SHA,
    sha256(SUBMISSION),
)

check(
    "StageResult contract SHA exact",
    sha256(STAGE_RESULT) == EXPECTED_STAGE_RESULT_SHA,
    sha256(STAGE_RESULT),
)

check(
    "Runtime orchestration identity SHA exact",
    sha256(RUN_IDENTITY) == EXPECTED_RUN_IDENTITY_SHA,
    sha256(RUN_IDENTITY),
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

check(
    "Field order exact",
    tuple(
        item.name
        for item
        in fields(
            WorkflowJobCorrelation
        )
    )
    == expected_fields,
)

check(
    "Field count exact",
    WORKFLOW_JOB_CORRELATION_FIELD_COUNT
    == 11,
)


# =========================================================================
# 3. Canonical binding
# =========================================================================

registry = WorkflowJobCorrelationRegistry()

mapping = make_mapping()

submitted = make_submitted_job(
    mapping,
    job_id="uj_final_5_3",
)

binding = register_workflow_job_correlation(
    mapping=mapping,
    submitted_job=submitted,
    registry=registry,
)

check(
    "Binding result type exact",
    isinstance(
        binding,
        WorkflowJobCorrelation,
    ),
)

check(
    "workflow_id exact",
    binding.workflow_id
    == "wf_final_5_3",
)

check(
    "correlation_id exact",
    binding.correlation_id
    == "corr_final_5_3",
)

check(
    "stage_id exact",
    binding.stage_id
    == "stage_a",
)

check(
    "stage_version exact",
    binding.stage_version
    == "stage_a_v1",
)

check(
    "workflow_type exact",
    binding.workflow_type
    == "final_workflow",
)

check(
    "workspace_id exact",
    binding.workspace_id
    == "ws_final_5_3",
)

check(
    "job_id exact",
    binding.job_id
    == "uj_final_5_3",
)

check(
    "job_type exact",
    binding.job_type
    == "final.stage_a",
)

check(
    "pipeline_id exact",
    binding.pipeline_id
    == "pipeline_final",
)

check(
    "runtime_stage exact",
    binding.runtime_stage
    == "runtime_stage_a",
)

check(
    "wave_index exact",
    binding.wave_index
    == 0,
)


# =========================================================================
# 4. Reverse lookup authority
# =========================================================================

resolved = resolve_workflow_job_correlation(
    job_id="uj_final_5_3",
    registry=registry,
)

check(
    "Reverse lookup exact",
    resolved == binding,
)

check(
    "Reverse lookup deterministic",
    resolve_workflow_job_correlation(
        job_id="uj_final_5_3",
        registry=registry,
    )
    == binding,
)


# =========================================================================
# 5. Idempotency and conflict protection
# =========================================================================

repeat = register_workflow_job_correlation(
    mapping=mapping,
    submitted_job=submitted,
    registry=registry,
)

check(
    "Exact duplicate idempotent",
    repeat == binding,
)

check(
    "Exact duplicate count stable",
    registry.count() == 1,
)

conflict = replace(
    binding,
    workflow_id="wf_conflict",
)

conflict_seen = False

try:
    registry.register(conflict)

except WorkflowJobCorrelationConflictError as exc:
    conflict_seen = (
        exc.job_id
        == "uj_final_5_3"
    )

check(
    "Conflicting duplicate fail-closed",
    conflict_seen,
)

check(
    "Conflict preserves original binding",
    registry.require_by_job_id(
        "uj_final_5_3"
    )
    == binding,
)


# =========================================================================
# 6. Multi-job workflow semantics
# =========================================================================

mapping_b = make_mapping(
    stage_id="stage_b",
    stage_version="stage_b_v1",
    job_type="final.stage_b",
    runtime_stage="runtime_stage_b",
    wave_index=1,
)

submitted_b = make_submitted_job(
    mapping_b,
    job_id="uj_final_5_3_b",
)

binding_b = register_workflow_job_correlation(
    mapping=mapping_b,
    submitted_job=submitted_b,
    registry=registry,
)

check(
    "Second job accepted",
    binding_b.job_id
    == "uj_final_5_3_b",
)

check(
    "Workflow supports multiple jobs",
    registry.count()
    == 2,
)

check(
    "Workflow lookup preserves both jobs",
    tuple(
        item.job_id
        for item
        in registry.all_for_workflow(
            "wf_final_5_3"
        )
    )
    == (
        "uj_final_5_3",
        "uj_final_5_3_b",
    ),
)


# =========================================================================
# 7. Same stage historical job semantics
# =========================================================================

mapping_retry = make_mapping(
    stage_id="stage_a",
    stage_version="stage_a_v1",
    job_type="final.stage_a",
    runtime_stage="runtime_stage_a",
    wave_index=2,
)

submitted_retry = make_submitted_job(
    mapping_retry,
    job_id="uj_final_5_3_retry",
)

retry_binding = register_workflow_job_correlation(
    mapping=mapping_retry,
    submitted_job=submitted_retry,
    registry=registry,
)

check(
    "Same stage can bind historical second job",
    retry_binding.stage_id == "stage_a"
    and retry_binding.job_id
    == "uj_final_5_3_retry",
)


# =========================================================================
# 8. Cross-validation
# =========================================================================

for field_name, wrong_value in (
    (
        "workspace_id",
        "wrong_workspace",
    ),
    (
        "job_type",
        "wrong.job",
    ),
    (
        "pipeline",
        "wrong_pipeline",
    ),
    (
        "stage",
        "wrong_stage",
    ),
):

    bad = dict(submitted)
    bad[field_name] = wrong_value

    expect_validation_error(
        "Cross-validation rejects "
        + field_name,
        lambda bad=bad:
            correlate_submitted_job(
                mapping=mapping,
                submitted_job=bad,
                registry=WorkflowJobCorrelationRegistry(),
            ),
    )


# =========================================================================
# 9. Required identity fields
# =========================================================================

for field_name in (
    "job_id",
    "workspace_id",
    "job_type",
    "pipeline",
    "stage",
):

    bad = dict(submitted)
    bad.pop(field_name)

    expect_validation_error(
        "Missing submitted identity rejected: "
        + field_name,
        lambda bad=bad:
            correlate_submitted_job(
                mapping=mapping,
                submitted_job=bad,
                registry=WorkflowJobCorrelationRegistry(),
            ),
    )


# =========================================================================
# 10. Immutability
# =========================================================================

frozen = False

try:
    binding.job_id = "mutated"

except (
    FrozenInstanceError,
    AttributeError,
):
    frozen = True

check(
    "Correlation record immutable",
    frozen,
)

snapshot = workflow_job_correlation_snapshot(
    binding
)

check(
    "Snapshot immutable",
    isinstance(
        snapshot,
        MappingProxyType,
    ),
)

check(
    "Snapshot identity exact",
    snapshot[
        "job_id"
    ]
    == "uj_final_5_3",
)


# =========================================================================
# 11. Architecture declaration
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
    architecture["phase"]
    == "5.3",
)

check(
    "Architecture component exact",
    architecture["component"]
    == "Workflow/Job Correlation",
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
    "Cross-validation exact",
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
# 12. Identity boundaries
# =========================================================================

for key in (
    "job_id_generation",
    "job_id_rewrite",
    "workflow_id_to_pipeline_run_id",
    "correlation_id_to_pipeline_run_id",
    "orchestration_run_id_generation",
):

    check(
        "Identity boundary disabled: "
        + key,
        architecture[
            "identity_boundaries"
        ][key]
        is False,
    )


# =========================================================================
# 13. Execution boundaries
# =========================================================================

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
        ][key]
        is False,
    )


# =========================================================================
# 14. API shape
# =========================================================================

check(
    "correlate_submitted_job keyword-only",
    str(
        inspect.signature(
            correlate_submitted_job
        )
    ).startswith(
        "(*,"
    ),
)

check(
    "register wrapper keyword-only",
    str(
        inspect.signature(
            register_workflow_job_correlation
        )
    ).startswith(
        "(*,"
    ),
)

check(
    "resolve wrapper keyword-only",
    str(
        inspect.signature(
            resolve_workflow_job_correlation
        )
    ).startswith(
        "(*,"
    ),
)

check(
    "Validation error inheritance exact",
    issubclass(
        WorkflowJobCorrelationValidationError,
        WorkflowJobCorrelationError,
    ),
)

check(
    "Conflict error inheritance exact",
    issubclass(
        WorkflowJobCorrelationConflictError,
        WorkflowJobCorrelationError,
    ),
)


# =========================================================================
# 15. Default registry
# =========================================================================

default_a = get_workflow_job_correlation_registry()
default_b = get_workflow_job_correlation_registry()

check(
    "Default registry stable singleton",
    default_a is default_b,
)

check(
    "Default registry type exact",
    isinstance(
        default_a,
        WorkflowJobCorrelationRegistry,
    ),
)


# =========================================================================
# 16. Static isolation
# =========================================================================

source = TARGET.read_text(
    encoding="utf-8"
)

tree = ast.parse(source)

runtime_imports = []

for node in ast.walk(tree):

    if isinstance(
        node,
        ast.ImportFrom,
    ):

        module = node.module or ""

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
    runtime_imports == [],
    repr(runtime_imports),
)


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


hits = called & forbidden_calls

check(
    "No forbidden Runtime/filesystem calls",
    hits == set(),
    repr(sorted(hits)),
)

check(
    "No pipeline_run_id assignment",
    "pipeline_run_id="
    not in source,
)

check(
    "No orchestration_run_id assignment",
    "orchestration_run_id="
    not in source,
)


# =========================================================================
# 17. Git scope
# =========================================================================

git_status = subprocess.run(
    [
        "git",
        "status",
        "--short",
        "--",
        "backend/server/coordination/runtime_integration",
        "backend/server/runtime",
    ],
    cwd=ROOT,
    capture_output=True,
    text=True,
    check=True,
).stdout.strip()


status_lines = tuple(
    line
    for line
    in git_status.splitlines()
    if line.strip()
)


check(
    "No Runtime production modification",
    not any(
        "backend/server/runtime/"
        in line.replace(
            "\\",
            "/",
        )
        for line
        in status_lines
    ),
    repr(status_lines),
)

check(
    "Changes confined to runtime_integration scope",
    all(
        "backend/server/coordination/runtime_integration/"
        in line.replace(
            "\\",
            "/",
        )
        for line
        in status_lines
    )
    if status_lines
    else False,
    repr(status_lines),
)


# =========================================================================
# Final result
# =========================================================================

passed = sum(
    1
    for _, ok, _
    in checks
    if ok
)

failed = (
    len(checks)
    - passed
)

certified = (
    failed == 0
)


lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.3 — WORKFLOW/JOB CORRELATION",
    "FINAL CERTIFICATION",
    "=" * 120,
    "",
]

for name, ok, detail in checks:

    lines.append(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if detail:
        lines.append(
            "    " + detail
        )


lines.extend(
    (
        "",
        "=" * 120,
        "FINAL CERTIFICATION RESULT",
        "=" * 120,
        f"Checks: {len(checks)}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        (
            "CERTIFIED: TRUE"
            if certified
            else "CERTIFIED: FALSE"
        ),
        (
            "STATUS: FINAL CERTIFICATION PASSED"
            if certified
            else "STATUS: FINAL CERTIFICATION FAILED"
        ),
        (
            "VERSION: "
            + WORKFLOW_JOB_CORRELATION_VERSION
        ),
        (
            "SCHEMA: "
            + WORKFLOW_JOB_CORRELATION_SCHEMA_VERSION
        ),
        (
            "SHA256: "
            + target_sha
        ),
        (
            "NEXT: 5.3.8 SHA256 Freeze"
            if certified
            else "NEXT: Resolve certification failures"
        ),
    )
)


REPORT.write_text(
    "\n".join(lines)
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 120)
print("PHASE 5.3 FINAL CERTIFICATION RESULT")
print("=" * 120)
print("Checks:", len(checks))
print("Passed:", passed)
print("Failed:", failed)
print("CERTIFIED:", certified)
print(
    "VERSION:",
    WORKFLOW_JOB_CORRELATION_VERSION,
)
print(
    "SCHEMA:",
    WORKFLOW_JOB_CORRELATION_SCHEMA_VERSION,
)
print(
    "SHA256:",
    target_sha,
)
print(
    "REPORT:",
    REPORT.name,
)
print("=" * 120)

raise SystemExit(
    0
    if certified
    else 1
)
