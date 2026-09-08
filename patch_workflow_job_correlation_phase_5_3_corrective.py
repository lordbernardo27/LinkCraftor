from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path.cwd()

TARGET = (
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


EXPECTED_OLD_SHA = (
    "C0D88ECC69680106B6833DF8CB3113FC"
    "9ABD23C1EE8B7D413BA4AAE3375648FA"
)

EXPECTED_MANIFEST_SHA = (
    "53F2B149EF904CE5692D85F349038CEA"
    "B901E00B06C6C273CA5B74EB31ACE8E5"
)

EXPECTED_INVALIDATION_SHA = (
    "80176F8807C1E399FAC4F74FB2D6CDAD"
    "B899F3C44643B268B6FC62694F103F65"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


actual_old_sha = sha256(
    TARGET
)

actual_manifest_sha = sha256(
    OLD_MANIFEST
)

actual_invalidation_sha = sha256(
    INVALIDATION
)


if actual_old_sha != EXPECTED_OLD_SHA:
    raise SystemExit(
        (
            "PATCH REFUSED: Phase 5.3 production no longer "
            "matches invalidated canonical source.\n"
            f"Expected: {EXPECTED_OLD_SHA}\n"
            f"Actual:   {actual_old_sha}"
        )
    )


if actual_manifest_sha != EXPECTED_MANIFEST_SHA:
    raise SystemExit(
        (
            "PATCH REFUSED: historical Phase 5.3 freeze "
            "manifest changed."
        )
    )


if actual_invalidation_sha != EXPECTED_INVALIDATION_SHA:
    raise SystemExit(
        (
            "PATCH REFUSED: controlled invalidation "
            "record changed."
        )
    )


source = TARGET.read_text(
    encoding="utf-8"
)


# =========================================================================
# 1. Version increment
# =========================================================================

old_version = (
    '"workflow_job_correlation_v5.3.0"'
)

new_version = (
    '"workflow_job_correlation_v5.3.1"'
)


version_count = source.count(
    old_version
)


if version_count != 1:
    raise SystemExit(
        (
            "PATCH REFUSED: expected exactly one "
            "workflow_job_correlation_v5.3.0 literal; "
            f"found {version_count}."
        )
    )


source = source.replace(
    old_version,
    new_version,
    1,
)


# =========================================================================
# 2. Insert successful-submission and submitted-metadata validation
# =========================================================================

anchor = '''    request = mapping.creation_request

    submitted_job_id = _clean_required_text(
'''


replacement = '''    request = mapping.creation_request

    # ---------------------------------------------------------------------
    # Phase 5.3.1 corrective validation
    #
    # Correlation may only be created from a canonically submitted Runtime
    # job. Request-side coordination evidence alone is insufficient.
    # ---------------------------------------------------------------------

    submission = submitted.get(
        "submission"
    )

    if not isinstance(
        submission,
        Mapping,
    ):
        raise WorkflowJobCorrelationValidationError(
            (
                "Submitted Runtime job is missing "
                "canonical submission evidence."
            ),
            violations=(
                "submitted_job.submission must be a mapping",
            ),
        )

    if (
        submission.get(
            "persisted"
        )
        is not True
    ):
        raise WorkflowJobCorrelationValidationError(
            (
                "Submitted Runtime job does not prove "
                "canonical persistence."
            ),
            violations=(
                "submission.persisted must be literal True",
            ),
        )

    if (
        submission.get(
            "queued"
        )
        is not True
    ):
        raise WorkflowJobCorrelationValidationError(
            (
                "Submitted Runtime job does not prove "
                "canonical queue ingress."
            ),
            violations=(
                "submission.queued must be literal True",
            ),
        )

    if (
        submission.get(
            "canonical_identity_preserved"
        )
        is not True
    ):
        raise WorkflowJobCorrelationValidationError(
            (
                "Submitted Runtime job does not prove "
                "canonical identity preservation."
            ),
            violations=(
                (
                    "submission.canonical_identity_preserved "
                    "must be literal True"
                ),
            ),
        )

    submitted_metadata = submitted.get(
        "metadata"
    )

    if not isinstance(
        submitted_metadata,
        Mapping,
    ):
        raise WorkflowJobCorrelationValidationError(
            (
                "Submitted Runtime job is missing "
                "canonical metadata."
            ),
            violations=(
                "submitted_job.metadata must be a mapping",
            ),
        )

    submitted_coordination = (
        submitted_metadata.get(
            "coordination"
        )
    )

    if not isinstance(
        submitted_coordination,
        Mapping,
    ):
        raise WorkflowJobCorrelationValidationError(
            (
                "Submitted Runtime job is missing "
                "coordination identity evidence."
            ),
            violations=(
                (
                    "submitted_job.metadata.coordination "
                    "must be a mapping"
                ),
            ),
        )

    submitted_job_id = _clean_required_text(
'''


if anchor not in source:
    raise SystemExit(
        (
            "PATCH REFUSED: certified insertion anchor "
            "was not found."
        )
    )


source = source.replace(
    anchor,
    replacement,
    1,
)


# =========================================================================
# 3. Cross-check submitted coordination against mapping/request authority
# =========================================================================

anchor = '''    if metadata_stage_id != stage_id:
        raise WorkflowJobCorrelationValidationError(
            (
                "Phase 5.2 stage identity evidence "
                "does not match RuntimeJobMapping."
            ),
            violations=(
                "stage_id evidence mismatch",
            ),
        )

    correlation = WorkflowJobCorrelation(
'''


replacement = '''    if metadata_stage_id != stage_id:
        raise WorkflowJobCorrelationValidationError(
            (
                "Phase 5.2 stage identity evidence "
                "does not match RuntimeJobMapping."
            ),
            violations=(
                "stage_id evidence mismatch",
            ),
        )

    submitted_workflow_id = _clean_required_text(
        submitted_coordination.get(
            "workflow_id"
        ),
        field_name=(
            "submitted coordination.workflow_id"
        ),
    )

    submitted_correlation_id = _clean_required_text(
        submitted_coordination.get(
            "correlation_id"
        ),
        field_name=(
            "submitted coordination.correlation_id"
        ),
    )

    submitted_stage_id = _clean_required_text(
        submitted_coordination.get(
            "stage_id"
        ),
        field_name=(
            "submitted coordination.stage_id"
        ),
    )

    submitted_stage_version = _clean_required_text(
        submitted_coordination.get(
            "stage_version"
        ),
        field_name=(
            "submitted coordination.stage_version"
        ),
    )

    submitted_workflow_type = _clean_required_text(
        submitted_coordination.get(
            "workflow_type"
        ),
        field_name=(
            "submitted coordination.workflow_type"
        ),
    )

    submitted_wave_index = _clean_wave_index(
        submitted_coordination.get(
            "wave_index"
        )
    )

    expected_stage_version = _clean_required_text(
        coordination.get(
            "stage_version"
        ),
        field_name=(
            "coordination.stage_version"
        ),
    )

    expected_workflow_type = _clean_required_text(
        coordination.get(
            "workflow_type"
        ),
        field_name=(
            "coordination.workflow_type"
        ),
    )

    expected_wave_index = _clean_wave_index(
        mapping.wave_index
    )

    submitted_identity_mismatches = []

    if submitted_workflow_id != workflow_id:
        submitted_identity_mismatches.append(
            "submitted workflow_id mismatch"
        )

    if submitted_correlation_id != correlation_id:
        submitted_identity_mismatches.append(
            "submitted correlation_id mismatch"
        )

    if submitted_stage_id != stage_id:
        submitted_identity_mismatches.append(
            "submitted stage_id mismatch"
        )

    if (
        submitted_stage_version
        != expected_stage_version
    ):
        submitted_identity_mismatches.append(
            "submitted stage_version mismatch"
        )

    if (
        submitted_workflow_type
        != expected_workflow_type
    ):
        submitted_identity_mismatches.append(
            "submitted workflow_type mismatch"
        )

    if (
        submitted_wave_index
        != expected_wave_index
    ):
        submitted_identity_mismatches.append(
            "submitted wave_index mismatch"
        )

    if submitted_identity_mismatches:
        raise WorkflowJobCorrelationValidationError(
            (
                "Submitted Runtime coordination evidence "
                "does not match certified Coordination "
                "identity authority."
            ),
            violations=tuple(
                submitted_identity_mismatches
            ),
        )

    correlation = WorkflowJobCorrelation(
'''


if anchor not in source:
    raise SystemExit(
        (
            "PATCH REFUSED: certified identity-validation "
            "anchor was not found."
        )
    )


source = source.replace(
    anchor,
    replacement,
    1,
)


# =========================================================================
# 4. Use already-validated authority values for correlation construction
# =========================================================================

source = source.replace(
    '''        stage_version=_clean_required_text(
            coordination.get("stage_version"),
            field_name="coordination.stage_version",
        ),
''',
    '''        stage_version=expected_stage_version,
''',
    1,
)


source = source.replace(
    '''        workflow_type=_clean_required_text(
            coordination.get("workflow_type"),
            field_name="coordination.workflow_type",
        ),
''',
    '''        workflow_type=expected_workflow_type,
''',
    1,
)


# =========================================================================
# 5. Write corrective candidate
# =========================================================================

TARGET.write_text(
    source,
    encoding="utf-8",
)


new_sha = sha256(
    TARGET
)


if new_sha == EXPECTED_OLD_SHA:
    raise SystemExit(
        "PATCH FAILED: production SHA did not change."
    )


# Historical evidence MUST remain unchanged.
if sha256(
    OLD_MANIFEST
) != EXPECTED_MANIFEST_SHA:
    raise SystemExit(
        "PATCH FAILED: historical freeze manifest changed."
    )


if sha256(
    INVALIDATION
) != EXPECTED_INVALIDATION_SHA:
    raise SystemExit(
        "PATCH FAILED: invalidation record changed."
    )


print()
print("=" * 120)
print("PHASE 5.3 — CORRECTIVE PATCH INSTALLED")
print("=" * 120)
print(
    "Production:",
    str(
        TARGET.relative_to(ROOT)
    ).replace(
        "\\",
        "/",
    ),
)
print(
    "Old SHA256:",
    EXPECTED_OLD_SHA,
)
print(
    "New candidate SHA256:",
    new_sha,
)
print(
    "Version:",
    "workflow_job_correlation_v5.3.1",
)
print(
    "Schema:",
    "workflow_job_correlation_schema_v1",
)
print()
print("Added:")
print("  submitted submission evidence validation")
print("  submitted metadata.coordination validation")
print("  submitted workflow identity cross-check")
print("  submitted stage/version/type/wave cross-check")
print()
print("Historical freeze manifest modified: False")
print("Invalidation record modified: False")
print("Runtime modified: False")
print("Orchestration modified: False")
print("StageResult modified: False")
print()
print(
    "NEXT:",
    "Corrective Phase 5.3 Focused Verification",
)
print("=" * 120)
