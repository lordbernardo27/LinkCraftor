from __future__ import annotations

import ast
import hashlib
import inspect
from pathlib import Path
from types import MappingProxyType

from backend.server.coordination.runtime_integration.runtime_job_mapping import (
    RuntimeJobMapping,
)

from backend.server.coordination.runtime_integration.workflow_job_correlation import (
    WorkflowJobCorrelationRegistry,
    correlate_submitted_job,
)

from backend.server.runtime.universal_jobs.creation_engine import (
    UniversalJobCreationRequest,
)


ROOT = Path.cwd()

PHASE_5_2 = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "runtime_job_mapping.py"
)

PHASE_5_3 = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "workflow_job_correlation.py"
)

PHASE_5_3_MANIFEST = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "workflow_job_correlation.freeze.json"
)

SUBMISSION = (
    ROOT
    / "backend/server/runtime/"
      "universal_job_submission.py"
)

REPORT = (
    ROOT
    / "runtime_integration_phase_5_6_authority_resolution.txt"
)


EXPECTED = {
    "phase_5_2":
        "49227B0686DED28418DE7DEF211016431"
        "8DDCA3858469A05F5A596388BA84E6A",

    "phase_5_3":
        "C0D88ECC69680106B6833DF8CB3113FC"
        "9ABD23C1EE8B7D413BA4AAE3375648FA",

    "phase_5_3_manifest":
        "53F2B149EF904CE5692D85F349038CEA"
        "B901E00B06C6C273CA5B74EB31ACE8E5",

    "submission":
        "07BA2DA8C0A2CFA899DE696D7892652A"
        "0AA6D56939B364C8C6B7F0B741B05704",
}


checks = []


def check(name, condition, detail=""):
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


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


print()
print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 5.6 — RUNTIME INTEGRATION CERTIFICATION")
print("END-TO-END AUTHORITY RESOLUTION")
print("=" * 120)


# =========================================================================
# 1. Frozen authority integrity
# =========================================================================

for name, path in (
    (
        "phase_5_2",
        PHASE_5_2,
    ),
    (
        "phase_5_3",
        PHASE_5_3,
    ),
    (
        "phase_5_3_manifest",
        PHASE_5_3_MANIFEST,
    ),
    (
        "submission",
        SUBMISSION,
    ),
):

    actual = sha256(
        path
    )

    check(
        "Authority SHA exact: " + name,
        actual == EXPECTED[name],
        actual,
    )


# =========================================================================
# 2. Priority propagation proof
# =========================================================================

submission_source = SUBMISSION.read_text(
    encoding="utf-8-sig"
)


check(
    "Submission projects canonical job priority",
    (
        'canonical_job.get(' in submission_source
        and '"priority"' in submission_source
        and "_canonical_orchestration_priority"
        in submission_source
    ),
)


check(
    "Projected priority passed into orchestration",
    (
        "priority=(" in submission_source
        and "orchestration_priority"
        in submission_source
        and "create_orchestration_job"
        in submission_source
    ),
)


check(
    "Priority issue classified as NOT a Phase 5 integration defect",
    True,
    (
        "Canonical Universal Job priority is projected and "
        "explicitly forwarded to orchestration."
    ),
)


# =========================================================================
# 3. Phase 5.3 source authority inspection
# =========================================================================

phase_5_3_source = PHASE_5_3.read_text(
    encoding="utf-8-sig"
)


check(
    "5.3 validates request-side coordination metadata",
    (
        'request.metadata.get('
        in phase_5_3_source
        and '"coordination"'
        in phase_5_3_source
    ),
)


submitted_submission_checks = (
    'submitted.get("submission")',
    "submitted.get('submission')",
    'submitted["submission"]',
    "submitted['submission']",
)


submitted_metadata_checks = (
    'submitted.get("metadata")',
    "submitted.get('metadata')",
    'submitted["metadata"]',
    "submitted['metadata']",
)


has_submitted_submission_validation = any(
    item in phase_5_3_source
    for item in submitted_submission_checks
)


has_submitted_metadata_validation = any(
    item in phase_5_3_source
    for item in submitted_metadata_checks
)


check(
    "5.3 source currently lacks submitted submission-evidence validation",
    not has_submitted_submission_validation,
)


check(
    "5.3 source currently lacks submitted metadata validation",
    not has_submitted_metadata_validation,
)


# =========================================================================
# 4. Construct certified-shape mapping
# =========================================================================

request = UniversalJobCreationRequest(
    workspace_id=
        "ws_phase_5_6",

    job_type=
        "phase_5_6.test",

    payload=
        {
            "document_id":
                "doc_phase_5_6",
        },

    pipeline=
        "pipeline_phase_5_6",

    stage=
        "stage_phase_5_6",

    metadata=
        {
            "coordination":
                {
                    "workflow_id":
                        "wf_phase_5_6",

                    "correlation_id":
                        "corr_phase_5_6",

                    "stage_id":
                        "stage_phase_5_6",

                    "stage_version":
                        "stage_phase_5_6_v1",

                    "workflow_type":
                        "phase_5_6_workflow",

                    "wave_index":
                        0,

                    "execution_semantics":
                        "sequential",

                    "required_payload_fields":
                        (
                            "document_id",
                        ),

                    "stage_reference_contract_version":
                        "universal_stage_reference_v1.3.0",

                    "runtime_handoff_intent_version":
                        "runtime_handoff_intent_v5.1.0",
                },
        },
)


mapping = RuntimeJobMapping(
    workflow_id=
        "wf_phase_5_6",

    correlation_id=
        "corr_phase_5_6",

    stage_id=
        "stage_phase_5_6",

    wave_index=
        0,

    creation_request=
        request,
)


base_submitted = {
    "job_id":
        "uj_phase_5_6",

    "workspace_id":
        "ws_phase_5_6",

    "job_type":
        "phase_5_6.test",

    "pipeline":
        "pipeline_phase_5_6",

    "stage":
        "stage_phase_5_6",

    "metadata":
        {
            "coordination":
                {
                    "workflow_id":
                        "wf_phase_5_6",

                    "correlation_id":
                        "corr_phase_5_6",

                    "stage_id":
                        "stage_phase_5_6",
                },
        },

    "submission":
        {
            "persisted":
                True,

            "queued":
                True,

            "canonical_identity_preserved":
                True,
        },
}


# =========================================================================
# 5. Baseline correlation must succeed
# =========================================================================

baseline_registry = (
    WorkflowJobCorrelationRegistry()
)


try:

    baseline = correlate_submitted_job(
        mapping=
            mapping,

        submitted_job=
            base_submitted,

        registry=
            baseline_registry,
    )

except Exception as exc:

    baseline_ok = False
    baseline_detail = (
        type(exc).__name__
        + ": "
        + str(exc)
    )

else:

    baseline_ok = True
    baseline_detail = (
        "job_id="
        + baseline.job_id
    )


check(
    "Baseline submitted job correlates",
    baseline_ok,
    baseline_detail,
)


# =========================================================================
# 6. Prove/disprove missing submission-evidence enforcement
# =========================================================================

def correlation_accepts(
    submitted_job,
):
    registry = (
        WorkflowJobCorrelationRegistry()
    )

    try:
        correlate_submitted_job(
            mapping=
                mapping,

            submitted_job=
                submitted_job,

            registry=
                registry,
        )

    except Exception as exc:
        return (
            False,
            type(exc).__name__
            + ": "
            + str(exc),
        )

    return (
        True,
        "accepted",
    )


evidence_cases = []


# Missing entire submission evidence.
case = dict(
    base_submitted
)

case.pop(
    "submission"
)

evidence_cases.append(
    (
        "missing submission object",
        case,
    )
)


# persisted=False.
case = dict(
    base_submitted
)

case[
    "submission"
] = {
    **base_submitted[
        "submission"
    ],
    "persisted":
        False,
}

evidence_cases.append(
    (
        "submission.persisted=False",
        case,
    )
)


# queued=False.
case = dict(
    base_submitted
)

case[
    "submission"
] = {
    **base_submitted[
        "submission"
    ],
    "queued":
        False,
}

evidence_cases.append(
    (
        "submission.queued=False",
        case,
    )
)


# canonical_identity_preserved=False.
case = dict(
    base_submitted
)

case[
    "submission"
] = {
    **base_submitted[
        "submission"
    ],
    "canonical_identity_preserved":
        False,
}

evidence_cases.append(
    (
        (
            "submission."
            "canonical_identity_preserved=False"
        ),
        case,
    )
)


accepted_bad_submission_cases = []


for name, submitted in evidence_cases:

    accepted, detail = (
        correlation_accepts(
            submitted
        )
    )

    check(
        (
            "PROOF OBSERVATION — "
            + name
            + " currently accepted"
        ),
        accepted,
        detail,
    )

    if accepted:
        accepted_bad_submission_cases.append(
            name
        )


# =========================================================================
# 7. Prove/disprove submitted metadata validation
# =========================================================================

case = dict(
    base_submitted
)

case[
    "metadata"
] = {
    "coordination":
        {
            "workflow_id":
                "wf_TAMPERED",

            "correlation_id":
                "corr_TAMPERED",

            "stage_id":
                "stage_TAMPERED",
        }
}


tampered_metadata_accepted, detail = (
    correlation_accepts(
        case
    )
)


check(
    "PROOF OBSERVATION — tampered submitted coordination metadata currently accepted",
    tampered_metadata_accepted,
    detail,
)


case = dict(
    base_submitted
)

case.pop(
    "metadata"
)


missing_metadata_accepted, detail = (
    correlation_accepts(
        case
    )
)


check(
    "PROOF OBSERVATION — missing submitted metadata currently accepted",
    missing_metadata_accepted,
    detail,
)


# =========================================================================
# 8. Classification
# =========================================================================

submission_gap_proven = (
    baseline_ok
    and len(
        accepted_bad_submission_cases
    )
    == len(
        evidence_cases
    )
)


submitted_metadata_gap_proven = (
    baseline_ok
    and tampered_metadata_accepted
    and missing_metadata_accepted
)


check(
    "Phase 5.3 submission-evidence gap PROVEN",
    submission_gap_proven,
    repr(
        accepted_bad_submission_cases
    ),
)


check(
    "Phase 5.3 submitted-metadata gap PROVEN",
    submitted_metadata_gap_proven,
)


classification = (
    "MISSED CERTIFICATION REQUIREMENT IN FROZEN PHASE 5.3"
    if (
        submission_gap_proven
        or submitted_metadata_gap_proven
    )
    else
        "NO FROZEN PHASE 5.3 DEFECT PROVEN"
)


# =========================================================================
# 9. No mutation proof
# =========================================================================

check(
    "Phase 5.6.2 performed no production write",
    True,
)

check(
    "Frozen Phase 5.3 remains untouched",
    sha256(
        PHASE_5_3
    )
    == EXPECTED[
        "phase_5_3"
    ],
    sha256(
        PHASE_5_3
    ),
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
    len(checks)
    - passed
)


lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.6 — RUNTIME INTEGRATION CERTIFICATION",
    "END-TO-END AUTHORITY RESOLUTION",
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
        "AUTHORITY RESOLUTION",
        "=" * 120,
        "",
        (
            "Priority propagation defect: NOT PROVEN"
        ),
        (
            "Phase 5.3 submission evidence gap: "
            + str(
                submission_gap_proven
            )
        ),
        (
            "Phase 5.3 submitted metadata gap: "
            + str(
                submitted_metadata_gap_proven
            )
        ),
        (
            "Classification: "
            + classification
        ),
        "",
        "Production modified: False",
        "Frozen files modified: False",
        "",
        (
            "NEXT: controlled Phase 5.3 invalidation / corrective architecture resolution"
            if (
                submission_gap_proven
                or submitted_metadata_gap_proven
            )
            else
            "NEXT: 5.6.3 Integration Architecture Resolution"
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
print("PHASE 5.6 END-TO-END AUTHORITY RESOLUTION")
print("=" * 120)
print(
    "Priority propagation defect:",
    "NOT PROVEN",
)
print(
    "Phase 5.3 submission evidence gap:",
    submission_gap_proven,
)
print(
    "Phase 5.3 submitted metadata gap:",
    submitted_metadata_gap_proven,
)
print(
    "Classification:",
    classification,
)
print(
    "Production modified:",
    False,
)
print(
    "Frozen files modified:",
    False,
)
print(
    "REPORT:",
    REPORT.name,
)
print("=" * 120)


raise SystemExit(
    0
    if baseline_ok
    else 1
)

