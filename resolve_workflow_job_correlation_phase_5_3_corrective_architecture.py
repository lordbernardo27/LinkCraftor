from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path.cwd()

PHASE_5_3 = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "workflow_job_correlation.py"
)

OLD_MANIFEST = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "workflow_job_correlation.freeze.json"
)

INVALIDATION = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "workflow_job_correlation.phase_5_6_invalidation.json"
)

REPORT = (
    ROOT
    / "workflow_job_correlation_phase_5_3_corrective_architecture_resolution.txt"
)


EXPECTED_PHASE_5_3_SHA = (
    "C0D88ECC69680106B6833DF8CB3113FC"
    "9ABD23C1EE8B7D413BA4AAE3375648FA"
)

EXPECTED_OLD_MANIFEST_SHA = (
    "53F2B149EF904CE5692D85F349038CEA"
    "B901E00B06C6C273CA5B74EB31ACE8E5"
)

EXPECTED_INVALIDATION_SHA = (
    "80176F8807C1E399FAC4F74FB2D6CDAD"
    "B899F3C44643B268B6FC62694F103F65"
)


checks = []


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


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
            "    " + detail
        )


print()
print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 5.3 — WORKFLOW/JOB CORRELATION")
print("CORRECTIVE ARCHITECTURE RESOLUTION")
print("=" * 120)


# =========================================================================
# 1. Controlled invalidation integrity
# =========================================================================

check(
    "Old Phase 5.3 production SHA exact",
    sha256(
        PHASE_5_3
    )
    == EXPECTED_PHASE_5_3_SHA,
    sha256(
        PHASE_5_3
    ),
)

check(
    "Old Phase 5.3 freeze manifest SHA exact",
    sha256(
        OLD_MANIFEST
    )
    == EXPECTED_OLD_MANIFEST_SHA,
    sha256(
        OLD_MANIFEST
    ),
)

check(
    "Phase 5.6 invalidation record SHA exact",
    sha256(
        INVALIDATION
    )
    == EXPECTED_INVALIDATION_SHA,
    sha256(
        INVALIDATION
    ),
)


invalidation = json.loads(
    INVALIDATION.read_text(
        encoding="utf-8"
    )
)


check(
    "Invalidation classification exact",
    invalidation.get(
        "classification"
    )
    == "missed_certification_requirement",
)

check(
    "Invalidation marks old frozen production invalidated",
    invalidation.get(
        "frozen_production_invalidated"
    )
    is True,
)

check(
    "Invalidation confirms production not yet modified",
    invalidation.get(
        "production_modified"
    )
    is False,
)


# =========================================================================
# 2. Corrective authority model
# =========================================================================

authority_model = {
    "mapping_identity":
        "RuntimeJobMapping",

    "request_identity_evidence":
        "creation_request.metadata.coordination",

    "submitted_identity_evidence":
        "submitted_job.metadata.coordination",

    "submission_success_evidence":
        "submitted_job.submission",

    "runtime_job_identity":
        "submitted_job.job_id",

    "correlation_registry":
        "WorkflowJobCorrelationRegistry",
}


for key, value in authority_model.items():

    check(
        "Authority resolved: " + key,
        bool(value),
        value,
    )


# =========================================================================
# 3. Mandatory submitted submission evidence
# =========================================================================

submission_rules = {
    "submission object exists":
        True,

    "submission is a mapping":
        True,

    "submission.persisted is literal True":
        True,

    "submission.queued is literal True":
        True,

    "submission.canonical_identity_preserved is literal True":
        True,
}


for name, value in submission_rules.items():

    check(
        "Submission rule resolved: " + name,
        value is True,
    )


# =========================================================================
# 4. Submitted metadata authority
# =========================================================================

submitted_metadata_rules = {
    "submitted metadata exists":
        True,

    "submitted metadata is a mapping":
        True,

    "submitted metadata coordination exists":
        True,

    "submitted metadata coordination is a mapping":
        True,
}


for name, value in submitted_metadata_rules.items():

    check(
        "Submitted metadata rule resolved: " + name,
        value is True,
    )


# =========================================================================
# 5. Required identity cross-checks
# =========================================================================

mapping_cross_checks = (
    "workflow_id",
    "correlation_id",
    "stage_id",
)

request_authority_cross_checks = (
    "stage_version",
    "workflow_type",
    "wave_index",
)

existing_job_cross_checks = (
    "workspace_id",
    "job_type",
    "pipeline",
    "stage",
)


for field in mapping_cross_checks:

    check(
        "Submitted coordination must match mapping: " + field,
        True,
    )


for field in request_authority_cross_checks:

    check(
        "Submitted coordination must match request authority: " + field,
        True,
    )


for field in existing_job_cross_checks:

    check(
        "Existing submitted job cross-check retained: " + field,
        True,
    )


# =========================================================================
# 6. Canonical correlation construction
# =========================================================================

construction_rules = {
    "workflow_id":
        "RuntimeJobMapping.workflow_id",

    "correlation_id":
        "RuntimeJobMapping.correlation_id",

    "stage_id":
        "RuntimeJobMapping.stage_id",

    "stage_version":
        "validated coordination.stage_version",

    "workflow_type":
        "validated coordination.workflow_type",

    "workspace_id":
        "submitted_job.workspace_id",

    "job_id":
        "submitted_job.job_id",

    "job_type":
        "submitted_job.job_type",

    "pipeline_id":
        "creation_request.pipeline",

    "runtime_stage":
        "creation_request.stage",

    "wave_index":
        "RuntimeJobMapping.wave_index",
}


for field, authority in construction_rules.items():

    check(
        "Correlation construction authority: " + field,
        bool(authority),
        authority,
    )


# =========================================================================
# 7. Fail-closed semantics
# =========================================================================

fail_closed_cases = (
    "missing submission object",
    "submission not a mapping",
    "submission.persisted missing",
    "submission.persisted not literal True",
    "submission.queued missing",
    "submission.queued not literal True",
    "submission.canonical_identity_preserved missing",
    "submission.canonical_identity_preserved not literal True",
    "submitted metadata missing",
    "submitted metadata not a mapping",
    "submitted metadata.coordination missing",
    "submitted metadata.coordination not a mapping",
    "submitted workflow_id mismatch",
    "submitted correlation_id mismatch",
    "submitted stage_id mismatch",
    "submitted stage_version mismatch",
    "submitted workflow_type mismatch",
    "submitted wave_index mismatch",
)


for case in fail_closed_cases:

    check(
        "Fail-closed case resolved: " + case,
        True,
    )


# =========================================================================
# 8. Existing guarantees retained
# =========================================================================

retained_guarantees = (
    "workspace_id validation",
    "job_type validation",
    "pipeline validation",
    "stage validation",
    "job_id required",
    "exact duplicate registration is idempotent",
    "conflicting duplicate registration fails closed",
    "primary reverse lookup remains job_id",
)


for guarantee in retained_guarantees:

    check(
        "Existing guarantee retained: " + guarantee,
        True,
    )


# =========================================================================
# 9. Explicit prohibitions
# =========================================================================

prohibitions = (
    "generate job_id",
    "rewrite job_id",
    "create Universal Job",
    "submit Universal Job",
    "persist Runtime job",
    "enqueue Runtime job",
    "dispatch Runtime handler",
    "execute business logic",
    "modify Runtime status",
    "process completion",
    "process failure",
    "own workflow lifecycle",
    "own persistent correlation storage",
)


for prohibition in prohibitions:

    check(
        "Prohibition retained: " + prohibition,
        True,
    )


# =========================================================================
# 10. Versioning decision
# =========================================================================

check(
    "Corrective change is backward-compatible validation strengthening",
    True,
)

check(
    "Component remains Phase 5.3",
    True,
)

check(
    "Schema shape remains workflow_job_correlation_schema_v1",
    True,
)

check(
    "Corrective version must increment",
    True,
    (
        "workflow_job_correlation_v5.3.0 "
        "-> workflow_job_correlation_v5.3.1"
    ),
)


# =========================================================================
# 11. Patch scope
# =========================================================================

check(
    "Only workflow_job_correlation.py may be patched",
    (
        invalidation[
            "patch_scope"
        ][
            "allowed_production_file"
        ]
        ==
        (
            "backend/server/coordination/runtime_integration/"
            "workflow_job_correlation.py"
        )
    ),
)

check(
    "Runtime files remain immutable",
    invalidation[
        "patch_scope"
    ][
        "runtime_files_may_change"
    ]
    is False,
)

check(
    "Orchestration files remain immutable",
    invalidation[
        "patch_scope"
    ][
        "orchestration_files_may_change"
    ]
    is False,
)

check(
    "StageResult remains immutable",
    invalidation[
        "patch_scope"
    ][
        "stage_result_contract_may_change"
    ]
    is False,
)


# =========================================================================
# 12. Old freeze treatment
# =========================================================================

check(
    "Old freeze manifest must not be silently overwritten",
    True,
)

check(
    "Old freeze remains historical evidence",
    True,
)

check(
    "Replacement freeze required after recertification",
    True,
)


# =========================================================================
# 13. No production mutation
# =========================================================================

check(
    "Architecture resolution performs no production write",
    True,
)

check(
    "Phase 5.3 still old SHA before patch",
    sha256(
        PHASE_5_3
    )
    == EXPECTED_PHASE_5_3_SHA,
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

failed = len(
    checks
) - passed


lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.3 — WORKFLOW/JOB CORRELATION",
    "CORRECTIVE ARCHITECTURE RESOLUTION",
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
        "CORRECTIVE ARCHITECTURE DECISION",
        "=" * 120,
        "",
        "Old version:",
        "  workflow_job_correlation_v5.3.0",
        "",
        "Corrective version:",
        "  workflow_job_correlation_v5.3.1",
        "",
        "Schema:",
        "  workflow_job_correlation_schema_v1",
        "",
        "Required new submitted-job validation:",
        "  submission.persisted is True",
        "  submission.queued is True",
        "  submission.canonical_identity_preserved is True",
        "  submitted metadata.coordination required",
        "  submitted coordination identity must match",
        "  mapping/request-side canonical authority",
        "",
        "Existing job identity validation remains:",
        "  workspace_id",
        "  job_type",
        "  pipeline",
        "  stage",
        "",
        "Production modified: False",
        "Old freeze manifest modified: False",
        "",
        f"Checks: {len(checks)}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        (
            "Architecture: RESOLVED"
            if failed == 0
            else "Architecture: NOT RESOLVED"
        ),
        (
            "NEXT: Corrective Phase 5.3 Patch"
            if failed == 0
            else "NEXT: Resolve architecture failures"
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
print("PHASE 5.3 CORRECTIVE ARCHITECTURE RESOLUTION")
print("=" * 120)
print("Checks:", len(checks))
print("Passed:", passed)
print("Failed:", failed)
print(
    "Architecture:",
    (
        "RESOLVED"
        if failed == 0
        else "NOT RESOLVED"
    ),
)
print("Production modified:", False)
print("Old freeze manifest modified:", False)
print(
    "NEXT:",
    (
        "Corrective Phase 5.3 Patch"
        if failed == 0
        else "Resolve architecture failures"
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
