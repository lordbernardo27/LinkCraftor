from __future__ import annotations

import hashlib
from pathlib import Path

from backend.server.coordination.runtime_integration.runtime_job_mapping import (
    RuntimeJobMapping,
)

from backend.server.coordination.runtime_integration.workflow_job_correlation import (
    WORKFLOW_JOB_CORRELATION_VERSION,
    WORKFLOW_JOB_CORRELATION_SCHEMA_VERSION,
    WorkflowJobCorrelationRegistry,
    WorkflowJobCorrelationValidationError,
    correlate_submitted_job,
)

from backend.server.runtime.universal_jobs.creation_engine import (
    UniversalJobCreationRequest,
)


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

REPORT = (
    ROOT
    / "workflow_job_correlation_phase_5_3_corrective_focused_verification.txt"
)


EXPECTED_TARGET_SHA = (
    "13B007B1F74A131250476432B14381CC"
    "81C916F48CE121B44877964A18A73AB6"
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


def expect_rejected(name, submitted_job):
    registry = WorkflowJobCorrelationRegistry()

    try:
        correlate_submitted_job(
            mapping=mapping,
            submitted_job=submitted_job,
            registry=registry,
        )

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
            (
                "Unexpected exception: "
                + type(exc).__name__
                + ": "
                + str(exc)
            ),
        )
        return

    check(
        name,
        False,
        "Invalid submitted job was accepted.",
    )


print()
print("=" * 120)
print("LINKCRAFTOR")
print("PHASE 5.3 — WORKFLOW/JOB CORRELATION")
print("CORRECTIVE FOCUSED VERIFICATION")
print("=" * 120)


# =========================================================================
# 1. Candidate + historical evidence integrity
# =========================================================================

check(
    "Corrective candidate SHA exact",
    sha256(TARGET)
    == EXPECTED_TARGET_SHA,
    sha256(TARGET),
)

check(
    "Historical freeze manifest unchanged",
    sha256(OLD_MANIFEST)
    == EXPECTED_OLD_MANIFEST_SHA,
    sha256(OLD_MANIFEST),
)

check(
    "Invalidation record unchanged",
    sha256(INVALIDATION)
    == EXPECTED_INVALIDATION_SHA,
    sha256(INVALIDATION),
)

check(
    "Corrective version exact",
    WORKFLOW_JOB_CORRELATION_VERSION
    == "workflow_job_correlation_v5.3.1",
)

check(
    "Schema unchanged",
    WORKFLOW_JOB_CORRELATION_SCHEMA_VERSION
    == "workflow_job_correlation_schema_v1",
)


# =========================================================================
# 2. Certified-shape mapping
# =========================================================================

request = UniversalJobCreationRequest(
    workspace_id=
        "ws_corrective_5_3",

    job_type=
        "corrective.test",

    payload=
        {
            "document_id":
                "doc_corrective",
        },

    pipeline=
        "pipeline_corrective",

    stage=
        "stage_corrective",

    metadata=
        {
            "coordination":
                {
                    "workflow_id":
                        "wf_corrective",

                    "correlation_id":
                        "corr_corrective",

                    "stage_id":
                        "stage_corrective",

                    "stage_version":
                        "stage_corrective_v1",

                    "workflow_type":
                        "corrective_workflow",

                    "wave_index":
                        4,

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
        "wf_corrective",

    correlation_id=
        "corr_corrective",

    stage_id=
        "stage_corrective",

    wave_index=
        4,

    creation_request=
        request,
)


base_submitted = {
    "job_id":
        "uj_corrective",

    "workspace_id":
        "ws_corrective_5_3",

    "job_type":
        "corrective.test",

    "pipeline":
        "pipeline_corrective",

    "stage":
        "stage_corrective",

    "metadata":
        {
            "coordination":
                {
                    "workflow_id":
                        "wf_corrective",

                    "correlation_id":
                        "corr_corrective",

                    "stage_id":
                        "stage_corrective",

                    "stage_version":
                        "stage_corrective_v1",

                    "workflow_type":
                        "corrective_workflow",

                    "wave_index":
                        4,
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
# 3. Valid baseline must still correlate
# =========================================================================

registry = WorkflowJobCorrelationRegistry()

baseline = correlate_submitted_job(
    mapping=mapping,
    submitted_job=base_submitted,
    registry=registry,
)


check(
    "Valid canonical submission correlates",
    baseline.job_id
    == "uj_corrective",
)

check(
    "Baseline workflow_id exact",
    baseline.workflow_id
    == "wf_corrective",
)

check(
    "Baseline correlation_id exact",
    baseline.correlation_id
    == "corr_corrective",
)

check(
    "Baseline stage_id exact",
    baseline.stage_id
    == "stage_corrective",
)

check(
    "Baseline stage_version exact",
    baseline.stage_version
    == "stage_corrective_v1",
)

check(
    "Baseline workflow_type exact",
    baseline.workflow_type
    == "corrective_workflow",
)

check(
    "Baseline wave_index exact",
    baseline.wave_index
    == 4,
)


# =========================================================================
# 4. Original escaped submission defects must now fail
# =========================================================================

case = dict(base_submitted)
case.pop("submission")

expect_rejected(
    "Missing submission object rejected",
    case,
)


case = dict(base_submitted)
case["submission"] = {
    **base_submitted["submission"],
    "persisted": False,
}

expect_rejected(
    "submission.persisted=False rejected",
    case,
)


case = dict(base_submitted)
case["submission"] = {
    **base_submitted["submission"],
    "queued": False,
}

expect_rejected(
    "submission.queued=False rejected",
    case,
)


case = dict(base_submitted)
case["submission"] = {
    **base_submitted["submission"],
    "canonical_identity_preserved": False,
}

expect_rejected(
    "submission.canonical_identity_preserved=False rejected",
    case,
)


# =========================================================================
# 5. Literal-True enforcement
# =========================================================================

for key in (
    "persisted",
    "queued",
    "canonical_identity_preserved",
):
    case = dict(base_submitted)

    case["submission"] = {
        **base_submitted["submission"],
        key:
            1,
    }

    expect_rejected(
        (
            "submission."
            + key
            + " requires literal True"
        ),
        case,
    )


# =========================================================================
# 6. Original escaped submitted-metadata defects
# =========================================================================

case = dict(base_submitted)
case.pop("metadata")

expect_rejected(
    "Missing submitted metadata rejected",
    case,
)


case = dict(base_submitted)
case["metadata"] = {}

expect_rejected(
    "Missing submitted metadata.coordination rejected",
    case,
)


case = dict(base_submitted)

case["metadata"] = {
    "coordination":
        {
            **base_submitted[
                "metadata"
            ][
                "coordination"
            ],
            "workflow_id":
                "wf_TAMPERED",
        }
}

expect_rejected(
    "Tampered submitted workflow_id rejected",
    case,
)


case = dict(base_submitted)

case["metadata"] = {
    "coordination":
        {
            **base_submitted[
                "metadata"
            ][
                "coordination"
            ],
            "correlation_id":
                "corr_TAMPERED",
        }
}

expect_rejected(
    "Tampered submitted correlation_id rejected",
    case,
)


case = dict(base_submitted)

case["metadata"] = {
    "coordination":
        {
            **base_submitted[
                "metadata"
            ][
                "coordination"
            ],
            "stage_id":
                "stage_TAMPERED",
        }
}

expect_rejected(
    "Tampered submitted stage_id rejected",
    case,
)


case = dict(base_submitted)

case["metadata"] = {
    "coordination":
        {
            **base_submitted[
                "metadata"
            ][
                "coordination"
            ],
            "stage_version":
                "stage_TAMPERED_v9",
        }
}

expect_rejected(
    "Tampered submitted stage_version rejected",
    case,
)


case = dict(base_submitted)

case["metadata"] = {
    "coordination":
        {
            **base_submitted[
                "metadata"
            ][
                "coordination"
            ],
            "workflow_type":
                "tampered_workflow",
        }
}

expect_rejected(
    "Tampered submitted workflow_type rejected",
    case,
)


case = dict(base_submitted)

case["metadata"] = {
    "coordination":
        {
            **base_submitted[
                "metadata"
            ][
                "coordination"
            ],
            "wave_index":
                99,
        }
}

expect_rejected(
    "Tampered submitted wave_index rejected",
    case,
)


# =========================================================================
# 7. Missing submitted coordination fields fail closed
# =========================================================================

for field in (
    "workflow_id",
    "correlation_id",
    "stage_id",
    "stage_version",
    "workflow_type",
    "wave_index",
):

    coordination = dict(
        base_submitted[
            "metadata"
        ][
            "coordination"
        ]
    )

    coordination.pop(
        field
    )

    case = dict(
        base_submitted
    )

    case[
        "metadata"
    ] = {
        "coordination":
            coordination
    }

    expect_rejected(
        (
            "Missing submitted coordination."
            + field
            + " rejected"
        ),
        case,
    )


# =========================================================================
# 8. Existing job identity guarantees remain
# =========================================================================

for field, value in (
    (
        "workspace_id",
        "ws_wrong",
    ),
    (
        "job_type",
        "wrong.type",
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

    case = dict(
        base_submitted
    )

    case[
        field
    ] = value

    expect_rejected(
        (
            "Existing "
            + field
            + " mismatch still rejected"
        ),
        case,
    )


# =========================================================================
# 9. Exact duplicate behavior remains idempotent
# =========================================================================

duplicate_registry = (
    WorkflowJobCorrelationRegistry()
)


first = correlate_submitted_job(
    mapping=mapping,
    submitted_job=base_submitted,
    registry=duplicate_registry,
)

second = correlate_submitted_job(
    mapping=mapping,
    submitted_job=base_submitted,
    registry=duplicate_registry,
)


check(
    "Exact duplicate remains idempotent",
    first == second,
)


# =========================================================================
# 10. Historical artifacts remain untouched
# =========================================================================

check(
    "Old freeze remains historical evidence",
    sha256(OLD_MANIFEST)
    == EXPECTED_OLD_MANIFEST_SHA,
)

check(
    "Invalidation record remains immutable",
    sha256(INVALIDATION)
    == EXPECTED_INVALIDATION_SHA,
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
    "PHASE 5.3 — WORKFLOW/JOB CORRELATION",
    "CORRECTIVE FOCUSED VERIFICATION",
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
        "FOCUSED CORRECTIVE VERIFICATION RESULT",
        "=" * 120,
        f"Checks: {len(checks)}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        (
            "CORRECTIVE DEFECT FIXED: TRUE"
            if failed == 0
            else "CORRECTIVE DEFECT FIXED: FALSE"
        ),
        (
            "STATUS: PASSED"
            if failed == 0
            else "STATUS: FAILED"
        ),
        (
            "CANDIDATE SHA256: "
            + sha256(TARGET)
        ),
        (
            "NEXT: Full Phase 5.3 Recertification"
            if failed == 0
            else "NEXT: Resolve corrective failures"
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
print("PHASE 5.3 CORRECTIVE FOCUSED VERIFICATION")
print("=" * 120)
print("Checks:", len(checks))
print("Passed:", passed)
print("Failed:", failed)
print(
    "CORRECTIVE DEFECT FIXED:",
    failed == 0,
)
print(
    "CANDIDATE SHA256:",
    sha256(TARGET),
)
print(
    "NEXT:",
    (
        "Full Phase 5.3 Recertification"
        if failed == 0
        else "Resolve corrective failures"
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
