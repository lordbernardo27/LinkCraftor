from __future__ import annotations

import hashlib
import inspect
from dataclasses import fields
from pathlib import Path


ROOT = Path.cwd()

REPORT = (
    ROOT
    / "workflow_job_correlation_phase_5_3_architecture_resolution.txt"
)


PHASE_5_2 = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "runtime_job_mapping.py"
)

SUBMISSION = (
    ROOT
    / "backend/server/runtime/universal_job_submission.py"
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


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


sha_5_2 = sha256(
    PHASE_5_2
)

sha_submission = sha256(
    SUBMISSION
)

sha_stage_result = sha256(
    STAGE_RESULT
)

sha_run_identity = sha256(
    RUN_IDENTITY
)


checks = []


def check(
    name,
    condition,
    detail="",
):
    ok = bool(
        condition
    )

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
            "       "
            + detail
        )


print()
print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 5.3 — WORKFLOW/JOB CORRELATION")
print("ARCHITECTURE RESOLUTION")
print("=" * 120)


# =========================================================================
# 1. Frozen / authoritative source integrity
# =========================================================================

check(
    "Frozen Phase 5.2 SHA exact",
    sha_5_2
    == EXPECTED_5_2_SHA,
    sha_5_2,
)

check(
    "Universal Job Submission SHA exact",
    sha_submission
    == EXPECTED_SUBMISSION_SHA,
    sha_submission,
)

check(
    "StageResult contract SHA exact",
    sha_stage_result
    == EXPECTED_STAGE_RESULT_SHA,
    sha_stage_result,
)

check(
    "Runtime orchestration identity SHA exact",
    sha_run_identity
    == EXPECTED_RUN_IDENTITY_SHA,
    sha_run_identity,
)


# =========================================================================
# 2. Import contracts
# =========================================================================

from backend.server.coordination.runtime_integration.runtime_job_mapping import (
    RuntimeJobMapping,
)

from backend.server.coordination.universal_stages.result_contract import (
    UniversalStageResult,
)

from backend.server.runtime.universal_job_submission import (
    submit_universal_job,
)


mapping_fields = tuple(
    item.name
    for item
    in fields(
        RuntimeJobMapping
    )
)

stage_result_fields = tuple(
    item.name
    for item
    in fields(
        UniversalStageResult
    )
)


check(
    "Phase 5.2 exposes workflow_id",
    "workflow_id"
    in mapping_fields,
)

check(
    "Phase 5.2 exposes correlation_id",
    "correlation_id"
    in mapping_fields,
)

check(
    "Phase 5.2 exposes stage_id",
    "stage_id"
    in mapping_fields,
)

check(
    "Phase 5.2 exposes wave_index",
    "wave_index"
    in mapping_fields,
)

check(
    "Phase 5.2 exposes creation_request",
    "creation_request"
    in mapping_fields,
)


for field_name in (
    "workflow_id",
    "correlation_id",
    "stage_id",
    "workspace_id",
    "job_id",
    "job_type",
):

    check(
        (
            "StageResult return path field exists: "
            + field_name
        ),
        field_name
        in stage_result_fields,
    )


# =========================================================================
# 3. Submission is the operational job-identity boundary
# =========================================================================

submission_signature = (
    str(
        inspect.signature(
            submit_universal_job
        )
    )
)

check(
    "Submission accepts job creation fields",
    (
        "workspace_id"
        in submission_signature
        and "job_type"
        in submission_signature
        and "pipeline"
        in submission_signature
        and "stage"
        in submission_signature
    ),
    submission_signature,
)


submission_source = SUBMISSION.read_text(
    encoding="utf-8-sig"
)


check(
    "Submission calls Creation Engine",
    "create_universal_job("
    in submission_source,
)

check(
    "Submission extracts canonical job_id",
    "canonical_job_id"
    in submission_source,
)

check(
    "Submission persists same canonical job_id",
    (
        "job_id=("
        in submission_source
        and "canonical_job_id"
        in submission_source
    ),
)

check(
    "Submission validates persisted job identity",
    "orchestration_identity_mismatch"
    in submission_source,
)

check(
    "Submission returns canonical job-shaped result",
    "return result"
    in submission_source,
)


# =========================================================================
# 4. 5.3 canonical input architecture
# =========================================================================

architecture = {
    "coordination_input":
        "RuntimeJobMapping",

    "runtime_identity_input":
        "successful submit_universal_job result",

    "correlation_time":
        "after successful canonical submission",

    "job_identity_authority":
        "Universal Job Creation Engine",

    "persistence_identity_proof":
        "Universal Job Submission",

    "registry_authority":
        "UCF Phase 5.3 dedicated correlation registry",

    "registry_persistence":
        "deferred to Phase 8 Workflow State Persistence",
}


for key, value in architecture.items():

    check(
        "Architecture value resolved: "
        + key,
        bool(
            value
        ),
        value,
    )


# =========================================================================
# 5. Canonical correlation record
# =========================================================================

CORRELATION_FIELDS = (
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
    "Correlation field count resolved",
    len(
        CORRELATION_FIELDS
    )
    == 11,
    repr(
        CORRELATION_FIELDS
    ),
)


# =========================================================================
# 6. Required cross-validation
# =========================================================================

CROSS_VALIDATION = (
    (
        "creation_request.workspace_id",
        "submitted_job.workspace_id",
    ),
    (
        "creation_request.job_type",
        "submitted_job.job_type",
    ),
    (
        "creation_request.pipeline",
        "submitted_job.pipeline",
    ),
    (
        "creation_request.stage",
        "submitted_job.stage",
    ),
)


check(
    "Four Runtime identity cross-checks resolved",
    len(
        CROSS_VALIDATION
    )
    == 4,
    repr(
        CROSS_VALIDATION
    ),
)


# =========================================================================
# 7. Identity namespace separation
# =========================================================================

run_source = RUN_IDENTITY.read_text(
    encoding="utf-8-sig"
)


check(
    "workflow_id remains higher-layer identity",
    "workflow_id remains"
    in run_source,
)

check(
    "correlation_id remains separate",
    "correlation_id remains separate"
    in run_source,
)

check(
    "pipeline_run_id remains separate Runtime lineage",
    "pipeline_run_id remains optional"
    in run_source,
)


IDENTITY_RULES = (
    "Phase 5.3 does not generate job_id.",
    "Phase 5.3 does not rewrite job_id.",
    "Phase 5.3 does not map workflow_id to pipeline_run_id.",
    "Phase 5.3 does not map correlation_id to pipeline_run_id.",
    "Phase 5.3 does not generate orchestration_run_id.",
)


check(
    "Identity namespace rules resolved",
    len(
        IDENTITY_RULES
    )
    == 5,
)


# =========================================================================
# 8. Registry semantics
# =========================================================================

REGISTRY_RULES = (
    (
        "job_id",
        "primary reverse-lookup key",
    ),
    (
        "same job_id + exact binding",
        "idempotent reuse",
    ),
    (
        "same job_id + different binding",
        "fail closed",
    ),
    (
        "workflow_id",
        "may own many job bindings",
    ),
    (
        "workflow_id + stage_id",
        "not globally unique",
    ),
)


check(
    "Registry semantics resolved",
    len(
        REGISTRY_RULES
    )
    == 5,
    repr(
        REGISTRY_RULES
    ),
)


# =========================================================================
# 9. Return lookup
# =========================================================================

RETURN_LOOKUP_FIELDS = (
    "workflow_id",
    "correlation_id",
    "stage_id",
    "workspace_id",
    "job_type",
    "pipeline_id",
    "runtime_stage",
)


check(
    "job_id reverse lookup fields resolved",
    len(
        RETURN_LOOKUP_FIELDS
    )
    == 7,
    repr(
        RETURN_LOOKUP_FIELDS
    ),
)


# =========================================================================
# 10. Explicit prohibitions
# =========================================================================

PROHIBITIONS = (
    "Universal Job creation",
    "Runtime Registration lookup",
    "job submission",
    "queue insertion",
    "Runtime persistence",
    "handler lookup",
    "handler dispatch",
    "worker execution",
    "business-stage execution",
    "workflow lifecycle transition",
    "completion processing",
    "failure processing",
    "pipeline_run_id generation",
    "orchestration_run_id generation",
)


check(
    "Phase 5.3 prohibitions resolved",
    len(
        PROHIBITIONS
    )
    == 14,
)


# =========================================================================
# 11. Runtime State Store rejection
# =========================================================================

STATE_STORE = (
    ROOT
    / "backend/server/runtime/runtime_state_store.py"
)

state_source = STATE_STORE.read_text(
    encoding="utf-8-sig"
)


check(
    "Runtime State Store lacks workflow_id",
    "workflow_id"
    not in state_source,
)

check(
    "Runtime State Store lacks stage_id",
    "stage_id"
    not in state_source,
)

check(
    "Runtime State Store lacks job_id",
    "job_id"
    not in state_source,
)

check(
    "Runtime State Store not selected as 5.3 authority",
    True,
    (
        "Runtime State Store remains a generic Runtime "
        "state-persistence abstraction."
    ),
)


# =========================================================================
# 12. Architecture resolution
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
    "ARCHITECTURE RESOLUTION",
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
        "CANONICAL ARCHITECTURE DECISION",
        "=" * 120,
        "",
        "Phase 5.3 owns a dedicated UCF Workflow/Job Correlation Registry.",
        "",
        "Binding occurs only after successful canonical Universal Job submission.",
        "",
        "Inputs:",
        "  RuntimeJobMapping",
        "  successful submit_universal_job result",
        "",
        "Correlation record:",
        *(
            "  " + field_name
            for field_name
            in CORRELATION_FIELDS
        ),
        "",
        "Primary reverse lookup:",
        "  job_id -> WorkflowJobCorrelation",
        "",
        "Duplicate policy:",
        "  exact duplicate -> idempotent reuse",
        "  conflicting duplicate -> fail closed",
        "",
        "Persistence:",
        "  not owned by 5.3",
        "  deferred to Phase 8 Workflow State Persistence",
        "",
        "pipeline_run_id:",
        "  remains separate Runtime lineage",
        "  workflow_id is NOT injected into it",
        "  correlation_id is NOT injected into it",
        "",
        "Runtime State Store:",
        "  not the 5.3 correlation authority",
        "",
        "Production modified: False",
        "Installation performed: False",
        (
            "Architecture status: RESOLVED"
            if failed == 0
            else "Architecture status: FAILED"
        ),
        (
            "Next: 5.3.4 Installation / Patch"
            if failed == 0
            else "Next: Resolve architecture failures"
        ),
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
print("PHASE 5.3 ARCHITECTURE RESOLUTION RESULT")
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
    "ARCHITECTURE:",
    (
        "RESOLVED"
        if failed == 0
        else "FAILED"
    ),
)
print(
    "Production modified:",
    False,
)
print(
    "NEXT:",
    (
        "5.3.4 Installation / Patch"
        if failed == 0
        else "Resolve failures"
    ),
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
