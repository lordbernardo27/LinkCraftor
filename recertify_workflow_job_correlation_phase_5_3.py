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
    WORKFLOW_JOB_CORRELATION_VERSION,
    WORKFLOW_JOB_CORRELATION_SCHEMA_VERSION,
    WorkflowJobCorrelation,
    WorkflowJobCorrelationRegistry,
    WorkflowJobCorrelationError,
    WorkflowJobCorrelationValidationError,
    WorkflowJobCorrelationConflictError,
    correlate_submitted_job,
    workflow_job_correlation_snapshot,
    explain_workflow_job_correlation_v5_3,
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

PHASE_5_2 = (
    ROOT
    / "backend/server/coordination/runtime_integration/"
      "runtime_job_mapping.py"
)

REPORT = (
    ROOT
    / "workflow_job_correlation_phase_5_3_full_recertification.txt"
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

EXPECTED_PHASE_5_2_SHA = (
    "49227B0686DED28418DE7DEF211016431"
    "8DDCA3858469A05F5A596388BA84E6A"
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
        "Expected WorkflowJobCorrelationValidationError.",
    )


def expect_conflict(name, fn):
    try:
        fn()

    except WorkflowJobCorrelationConflictError as exc:
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
        "Expected WorkflowJobCorrelationConflictError.",
    )


def make_request():
    return UniversalJobCreationRequest(
        workspace_id="ws_recert_5_3",
        job_type="recert.test",
        payload={
            "document_id":
                "doc_recert",
        },
        pipeline="pipeline_recert",
        stage="stage_recert",
        metadata={
            "coordination":
                {
                    "workflow_id":
                        "wf_recert",

                    "correlation_id":
                        "corr_recert",

                    "stage_id":
                        "stage_recert",

                    "stage_version":
                        "stage_recert_v1",

                    "workflow_type":
                        "recert_workflow",

                    "wave_index":
                        2,

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
                }
        },
    )


def make_mapping():
    return RuntimeJobMapping(
        workflow_id="wf_recert",
        correlation_id="corr_recert",
        stage_id="stage_recert",
        wave_index=2,
        creation_request=make_request(),
    )


def make_submitted(
    *,
    job_id="uj_recert",
    workspace_id="ws_recert_5_3",
    job_type="recert.test",
    pipeline="pipeline_recert",
    stage="stage_recert",
    metadata=None,
    submission=None,
):
    if metadata is None:
        metadata = {
            "coordination":
                {
                    "workflow_id":
                        "wf_recert",

                    "correlation_id":
                        "corr_recert",

                    "stage_id":
                        "stage_recert",

                    "stage_version":
                        "stage_recert_v1",

                    "workflow_type":
                        "recert_workflow",

                    "wave_index":
                        2,
                }
        }

    if submission is None:
        submission = {
            "persisted":
                True,

            "queued":
                True,

            "canonical_identity_preserved":
                True,
        }

    return {
        "job_id":
            job_id,

        "workspace_id":
            workspace_id,

        "job_type":
            job_type,

        "pipeline":
            pipeline,

        "stage":
            stage,

        "metadata":
            metadata,

        "submission":
            submission,
    }


print()
print("=" * 120)
print("LINKCRAFTOR")
print("PHASE 5.3 — WORKFLOW/JOB CORRELATION")
print("FULL RECERTIFICATION")
print("=" * 120)


# =========================================================================
# 1. Candidate / historical integrity
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
    "Phase 5.2 authority unchanged",
    sha256(PHASE_5_2)
    == EXPECTED_PHASE_5_2_SHA,
    sha256(PHASE_5_2),
)


# =========================================================================
# 2. Public contract identity
# =========================================================================

check(
    "Version exact",
    WORKFLOW_JOB_CORRELATION_VERSION
    == "workflow_job_correlation_v5.3.1",
)

check(
    "Schema exact",
    WORKFLOW_JOB_CORRELATION_SCHEMA_VERSION
    == "workflow_job_correlation_schema_v1",
)

check(
    "Validation error inheritance",
    issubclass(
        WorkflowJobCorrelationValidationError,
        WorkflowJobCorrelationError,
    ),
)

check(
    "Conflict error inheritance",
    issubclass(
        WorkflowJobCorrelationConflictError,
        WorkflowJobCorrelationError,
    ),
)

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


# =========================================================================
# 3. Canonical correlation construction
# =========================================================================

mapping = make_mapping()
submitted = make_submitted()
registry = WorkflowJobCorrelationRegistry()


correlation = correlate_submitted_job(
    mapping=mapping,
    submitted_job=submitted,
    registry=registry,
)


check(
    "Correlation type exact",
    isinstance(
        correlation,
        WorkflowJobCorrelation,
    ),
)

expected_identity = {
    "workflow_id":
        "wf_recert",

    "correlation_id":
        "corr_recert",

    "stage_id":
        "stage_recert",

    "stage_version":
        "stage_recert_v1",

    "workflow_type":
        "recert_workflow",

    "workspace_id":
        "ws_recert_5_3",

    "job_id":
        "uj_recert",

    "job_type":
        "recert.test",

    "pipeline_id":
        "pipeline_recert",

    "runtime_stage":
        "stage_recert",

    "wave_index":
        2,
}


for field, value in expected_identity.items():

    check(
        "Correlation identity exact: " + field,
        getattr(
            correlation,
            field
        )
        == value,
    )


# =========================================================================
# 4. Registry reverse lookup
# =========================================================================

resolved = registry.require_by_job_id(
    "uj_recert"
)


check(
    "Reverse lookup by job_id exact",
    resolved == correlation,
)


# =========================================================================
# 5. Snapshot contract
# =========================================================================

snapshot = workflow_job_correlation_snapshot(
    correlation
)


check(
    "Snapshot immutable",
    isinstance(
        snapshot,
        MappingProxyType,
    ),
)

for field, value in expected_identity.items():

    check(
        "Snapshot exact: " + field,
        snapshot[
            field
        ]
        == value,
    )


check(
    "Snapshot version exact",
    snapshot[
        "version"
    ]
    == WORKFLOW_JOB_CORRELATION_VERSION,
)

check(
    "Snapshot schema exact",
    snapshot[
        "schema_version"
    ]
    == WORKFLOW_JOB_CORRELATION_SCHEMA_VERSION,
)


# =========================================================================
# 6. Successful-submission evidence strictness
# =========================================================================

expect_validation_error(
    "Missing submission rejected",
    lambda:
        correlate_submitted_job(
            mapping=mapping,
            submitted_job={
                key:
                    value
                for key, value
                in submitted.items()
                if key != "submission"
            },
            registry=WorkflowJobCorrelationRegistry(),
        ),
)


for key, bad_value in (
    (
        "persisted",
        False,
    ),
    (
        "queued",
        False,
    ),
    (
        "canonical_identity_preserved",
        False,
    ),
    (
        "persisted",
        1,
    ),
    (
        "queued",
        1,
    ),
    (
        "canonical_identity_preserved",
        1,
    ),
):

    bad_submission = {
        **submitted["submission"],
        key:
            bad_value,
    }

    expect_validation_error(
        "Submission evidence rejected: "
        + key
        + "="
        + repr(
            bad_value
        ),
        lambda bad_submission=bad_submission:
            correlate_submitted_job(
                mapping=mapping,
                submitted_job=make_submitted(
                    submission=
                        bad_submission
                ),
                registry=
                    WorkflowJobCorrelationRegistry(),
            ),
    )


# =========================================================================
# 7. Submitted coordination identity strictness
# =========================================================================

coordination_fields = (
    "workflow_id",
    "correlation_id",
    "stage_id",
    "stage_version",
    "workflow_type",
    "wave_index",
)


for field in coordination_fields:

    tampered = dict(
        submitted[
            "metadata"
        ][
            "coordination"
        ]
    )

    if field == "wave_index":
        tampered[
            field
        ] = 999

    else:
        tampered[
            field
        ] = "tampered"

    expect_validation_error(
        "Tampered submitted coordination rejected: "
        + field,
        lambda tampered=tampered:
            correlate_submitted_job(
                mapping=mapping,
                submitted_job=make_submitted(
                    metadata={
                        "coordination":
                            tampered
                    }
                ),
                registry=
                    WorkflowJobCorrelationRegistry(),
            ),
    )


for field in coordination_fields:

    missing = dict(
        submitted[
            "metadata"
        ][
            "coordination"
        ]
    )

    missing.pop(
        field
    )

    expect_validation_error(
        "Missing submitted coordination rejected: "
        + field,
        lambda missing=missing:
            correlate_submitted_job(
                mapping=mapping,
                submitted_job=make_submitted(
                    metadata={
                        "coordination":
                            missing
                    }
                ),
                registry=
                    WorkflowJobCorrelationRegistry(),
            ),
    )


# =========================================================================
# 8. Existing submitted job identity strictness
# =========================================================================

for field, value in (
    (
        "workspace_id",
        "wrong_workspace",
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

    kwargs = {
        field:
            value
    }

    expect_validation_error(
        "Submitted job mismatch rejected: " + field,
        lambda kwargs=kwargs:
            correlate_submitted_job(
                mapping=mapping,
                submitted_job=make_submitted(
                    **kwargs
                ),
                registry=
                    WorkflowJobCorrelationRegistry(),
            ),
    )


# =========================================================================
# 9. Duplicate semantics
# =========================================================================

duplicate_registry = (
    WorkflowJobCorrelationRegistry()
)


first = correlate_submitted_job(
    mapping=mapping,
    submitted_job=submitted,
    registry=duplicate_registry,
)

second = correlate_submitted_job(
    mapping=mapping,
    submitted_job=submitted,
    registry=duplicate_registry,
)


check(
    "Exact duplicate idempotent",
    first == second,
)


conflicting_mapping = RuntimeJobMapping(
    workflow_id=
        "wf_other",

    correlation_id=
        "corr_other",

    stage_id=
        "stage_other",

    wave_index=
        2,

    creation_request=
        UniversalJobCreationRequest(
            workspace_id=
                "ws_recert_5_3",

            job_type=
                "recert.test",

            payload=
                {
                    "document_id":
                        "doc_recert",
                },

            pipeline=
                "pipeline_recert",

            stage=
                "stage_recert",

            metadata=
                {
                    "coordination":
                        {
                            "workflow_id":
                                "wf_other",

                            "correlation_id":
                                "corr_other",

                            "stage_id":
                                "stage_other",

                            "stage_version":
                                "stage_recert_v1",

                            "workflow_type":
                                "recert_workflow",

                            "wave_index":
                                2,
                        }
                },
        ),
)


conflicting_submitted = make_submitted(
    metadata={
        "coordination":
            {
                "workflow_id":
                    "wf_other",

                "correlation_id":
                    "corr_other",

                "stage_id":
                    "stage_other",

                "stage_version":
                    "stage_recert_v1",

                "workflow_type":
                    "recert_workflow",

                "wave_index":
                    2,
            }
    }
)


expect_conflict(
    "Conflicting duplicate job_id fails closed",
    lambda:
        correlate_submitted_job(
            mapping=
                conflicting_mapping,

            submitted_job=
                conflicting_submitted,

            registry=
                duplicate_registry,
        ),
)


# =========================================================================
# 10. Architecture declaration
# =========================================================================

architecture = (
    explain_workflow_job_correlation_v5_3()
)


check(
    "Architecture declaration immutable",
    isinstance(
        architecture,
        MappingProxyType,
    ),
)

check(
    "Architecture phase remains 5.3",
    architecture[
        "phase"
    ]
    == "5.3",
)

check(
    "Runtime identity input remains successful submitted canonical job",
    architecture[
        "runtime_identity_input"
    ]
    == "successful submitted canonical job",
)

check(
    "Binding time remains after successful canonical submission",
    architecture[
        "binding_time"
    ]
    == "after successful canonical submission",
)

check(
    "Primary reverse lookup remains job_id",
    architecture[
        "primary_reverse_lookup"
    ]
    == "job_id",
)

check(
    "Exact duplicate policy remains idempotent",
    architecture[
        "duplicate_policy"
    ][
        "exact_duplicate"
    ]
    == "idempotent_reuse",
)

check(
    "Conflict policy remains fail_closed",
    architecture[
        "duplicate_policy"
    ][
        "conflicting_duplicate"
    ]
    == "fail_closed",
)


# =========================================================================
# 11. Static authority boundary
# =========================================================================

source = TARGET.read_text(
    encoding="utf-8"
)

tree = ast.parse(
    source
)


forbidden_calls = {
    "create_universal_job",
    "submit_universal_job",
    "create_orchestration_job",
    "update_job_status",
    "mark_job_running",
    "mark_job_completed",
    "mark_job_failed",
    "dispatch_registered_runtime_handler",
    "run_one_universal_runtime_job_v1",
    "uuid4",
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
    "No forbidden execution/mutation calls",
    hits == set(),
    repr(
        sorted(
            hits
        )
    ),
)


# =========================================================================
# 12. Historical evidence protection
# =========================================================================

check(
    "Historical freeze still exact after recertification",
    sha256(
        OLD_MANIFEST
    )
    == EXPECTED_OLD_MANIFEST_SHA,
)

check(
    "Invalidation record still exact after recertification",
    sha256(
        INVALIDATION
    )
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
    "LINKCRAFTER",
    "PHASE 5.3 — WORKFLOW/JOB CORRELATION",
    "FULL RECERTIFICATION",
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
        "FULL RECERTIFICATION RESULT",
        "=" * 120,
        f"Checks: {len(checks)}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        (
            "RECERTIFIED: TRUE"
            if failed == 0
            else "RECERTIFIED: FALSE"
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
            + sha256(TARGET)
        ),
        (
            "NEXT: Replacement Phase 5.3 SHA256 Freeze"
            if failed == 0
            else "NEXT: Resolve recertification failures"
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
print("PHASE 5.3 FULL RECERTIFICATION RESULT")
print("=" * 120)
print("Checks:", len(checks))
print("Passed:", passed)
print("Failed:", failed)
print(
    "RECERTIFIED:",
    failed == 0,
)
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
    sha256(TARGET),
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
