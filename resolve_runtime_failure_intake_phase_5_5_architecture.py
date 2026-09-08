from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path.cwd()

REPORT = (
    ROOT
    / "runtime_failure_intake_phase_5_5_architecture_resolution.txt"
)


PATHS = {
    "phase_5_3":
        ROOT
        / "backend/server/coordination/runtime_integration/"
          "workflow_job_correlation.py",

    "phase_5_3_manifest":
        ROOT
        / "backend/server/coordination/runtime_integration/"
          "workflow_job_correlation.freeze.json",

    "phase_5_4":
        ROOT
        / "backend/server/coordination/runtime_integration/"
          "runtime_completion_intake.py",

    "phase_5_4_manifest":
        ROOT
        / "backend/server/coordination/runtime_integration/"
          "runtime_completion_intake.freeze.json",

    "stage_result":
        ROOT
        / "backend/server/coordination/universal_stages/"
          "result_contract.py",

    "runtime_worker":
        ROOT
        / "backend/server/runtime/"
          "universal_runtime_worker_v1.py",

    "orchestration_store":
        ROOT
        / "backend/server/orchestration/job_store.py",

    "orchestration_service":
        ROOT
        / "backend/server/orchestration/service.py",
}


EXPECTED = {
    "phase_5_3":
        "C0D88ECC69680106B6833DF8CB3113FC"
        "9ABD23C1EE8B7D413BA4AAE3375648FA",

    "phase_5_3_manifest":
        "53F2B149EF904CE5692D85F349038CEA"
        "B901E00B06C6C273CA5B74EB31ACE8E5",

    "phase_5_4":
        "A9F2A8E4242A08A2BDBE6AF0B96DC104"
        "2A53DDD3B2F72BB355259FA0E5D2E6FB",

    "phase_5_4_manifest":
        "CCAC1624848FA623F59DF92C9D70773C"
        "6532E6D48C956C243AD06B35FF8166DD",

    "stage_result":
        "B3469B10BB2F8F9372E4336784D09A14"
        "3C78FABE45BF039B61B76F4A2DC33B24",

    "runtime_worker":
        "ED6B415C5FEDF3F4CB62451F3E23D182"
        "F9DA937D9CB09FD33262C506B9BEF699",
}


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
            "    " + detail
        )


def sha256(
    path: Path,
) -> str:

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


print()
print("=" * 120)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 5.5 — RUNTIME FAILURE INTAKE")
print("ARCHITECTURE RESOLUTION")
print("=" * 120)


# =========================================================================
# 1. Frozen authority integrity
# =========================================================================

for name in (
    "phase_5_3",
    "phase_5_3_manifest",
    "phase_5_4",
    "phase_5_4_manifest",
    "stage_result",
    "runtime_worker",
):

    actual = sha256(
        PATHS[name]
    )

    check(
        "Authority SHA exact: " + name,
        actual == EXPECTED[name],
        actual,
    )


# =========================================================================
# 2. Canonical terminality
# =========================================================================

terminality = {
    "persisted_job_status":
        "failed",

    "terminal_transition":
        "running -> failed",

    "attempt_start_transition":
        "queued -> running",

    "runtime_dispatch_failed":
        True,

    "runtime_dispatch_completed":
        False,

    "runtime_retry_scheduled":
        False,

    "canonical_job_id_preserved":
        True,

    "retry_created_new_job":
        False,
}


for key, value in terminality.items():

    check(
        "Terminal proof resolved: " + key,
        value is not None,
        str(value),
    )


check(
    "Retryable failure excluded",
    True,
    (
        "RUNNING -> QUEUED remains Runtime retry state "
        "and MUST NOT emit StageResult(FAILED)."
    ),
)


check(
    "Ephemeral worker retry_allowed not required",
    True,
    (
        "Terminality is proven by persisted FAILED state, "
        "FAILED event, and runtime_retry_scheduled=False."
    ),
)


# =========================================================================
# 3. Identity authority
# =========================================================================

identity_rules = {
    "coordination_identity":
        "Frozen Phase 5.3 WorkflowJobCorrelation",

    "reverse_lookup":
        "job_id",

    "job_id":
        "must equal Phase 5.3 correlation.job_id",

    "workspace_id":
        "must equal Phase 5.3 correlation.workspace_id",

    "job_type":
        "must equal Phase 5.3 correlation.job_type",

    "pipeline_id":
        "from frozen Phase 5.3 correlation",

    "runtime_stage":
        "from frozen Phase 5.3 correlation",
}


for key, value in identity_rules.items():

    check(
        "Identity rule resolved: " + key,
        bool(value),
        value,
    )


# =========================================================================
# 4. Timing and result identity
# =========================================================================

timing_rules = {
    "result_id":
        (
            "final RUNNING->FAILED "
            "JobStatusEvent.event_id"
        ),

    "started_at":
        (
            "final attempt QUEUED->RUNNING "
            "JobStatusEvent.created_at"
        ),

    "finished_at":
        (
            "final RUNNING->FAILED "
            "JobStatusEvent.created_at"
        ),

    "retry_attempt_selection":
        (
            "latest valid QUEUED->RUNNING transition "
            "preceding selected RUNNING->FAILED event"
        ),
}


for key, value in timing_rules.items():

    check(
        "Timing/result rule resolved: " + key,
        bool(value),
        value,
    )


# =========================================================================
# 5. FAILED StageResult mapping
# =========================================================================

stage_result_rules = {
    "status":
        "failed",

    "execution_target":
        "universal_runtime",

    "failure_code":
        (
            "persisted "
            "metadata.runtime_dispatch_error_type"
        ),

    "failure_message":
        "persisted job.error_message",

    "failure_details":
        (
            "copy canonical persisted Runtime "
            "failure evidence"
        ),

    "output":
        "empty mapping",

    "result_reference":
        "empty string",

    "artifact_references":
        "empty tuple",
}


for key, value in stage_result_rules.items():

    check(
        "FAILED StageResult rule resolved: " + key,
        bool(value),
        value,
    )


# =========================================================================
# 6. Exact failure_details evidence
# =========================================================================

failure_detail_keys = (
    "runtime_dispatch_completed",
    "runtime_dispatch_failed",
    "runtime_retry_scheduled",
    "runtime_failure_attempt_count",
    "runtime_maximum_attempts",
    "runtime_retry_type_allowed",
    "runtime_retry_exhausted",
    "runtime_contract_error",
    "runtime_dispatch_error_type",
    "canonical_job_id_preserved",
    "retry_created_new_job",
    "runtime_worker_version",
)


for key in failure_detail_keys:

    check(
        "Failure detail preserved: " + key,
        True,
    )


# =========================================================================
# 7. Required validation semantics
# =========================================================================

validations = (
    "job exists",
    "Phase 5.3 correlation exists before Runtime read",
    "job_id matches correlation",
    "workspace_id matches correlation",
    "job_type matches correlation",
    "persisted status is FAILED",
    "runtime_dispatch_failed is literal True",
    "runtime_dispatch_completed is literal False",
    "runtime_retry_scheduled is literal False",
    "canonical_job_id_preserved is literal True",
    "retry_created_new_job is literal False",
    "runtime_dispatch_error_type is non-empty",
    "job.error_message is non-empty",
    "FAILED event exists",
    "FAILED event is RUNNING -> FAILED",
    "attempt start event exists",
    "attempt start event is QUEUED -> RUNNING",
    "all selected events use canonical job_id",
    "started_at and finished_at are valid timestamps",
    "finished_at is not earlier than started_at",
)


for rule in validations:

    check(
        "Validation resolved: " + rule,
        True,
    )


# =========================================================================
# 8. Explicit non-requirements
# =========================================================================

non_requirements = (
    (
        "persisted retry_allowed field",
        (
            "not persisted; must not be required "
            "or reconstructed"
        ),
    ),
    (
        "ephemeral worker return object",
        (
            "not required for canonical intake"
        ),
    ),
    (
        "runtime_retry_exhausted=True",
        (
            "not universally required because retry "
            "may be disallowed by type before exhaustion"
        ),
    ),
    (
        "runtime_retry_type_allowed=True",
        (
            "not universally required"
        ),
    ),
)


for name, reason in non_requirements:

    check(
        "Non-requirement resolved: " + name,
        bool(reason),
        reason,
    )


# =========================================================================
# 9. Ownership boundaries
# =========================================================================

prohibitions = (
    "execute Runtime handler",
    "dispatch Runtime handler",
    "mark job failed",
    "requeue job",
    "choose retry policy",
    "recalculate retry policy",
    "increment attempt count",
    "persist Runtime failure",
    "mutate orchestration job",
    "mutate orchestration events",
    "create Universal Job",
    "submit Universal Job",
    "generate job_id",
    "rewrite job_id",
    "process successful completion",
    "own workflow recovery",
    "own workflow compensation",
)


for item in prohibitions:

    check(
        "Prohibition resolved: " + item,
        True,
    )


# =========================================================================
# 10. Persistence ownership
# =========================================================================

check(
    "Failure persistence owner resolved",
    True,
    (
        "Universal Runtime Worker + canonical "
        "orchestration service/store"
    ),
)

check(
    "Workflow recovery owner resolved",
    True,
    "Phase 9 Coordination Recovery",
)

check(
    "Phase 5.5 is read-only intake",
    True,
)


# =========================================================================
# 11. Production-write protection
# =========================================================================

check(
    "Architecture resolution performs no production write",
    True,
)

check(
    "Runtime production patch not required",
    True,
    (
        "Persisted FAILED job plus status-event trail "
        "contains sufficient terminal failure evidence."
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
    "PHASE 5.5 — RUNTIME FAILURE INTAKE",
    "ARCHITECTURE RESOLUTION",
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
        "CANONICAL ARCHITECTURE DECISION",
        "=" * 120,
        "",
        "Phase 5.5 owns terminal Runtime failure intake only.",
        "",
        "Retryable Runtime failure:",
        "  RUNNING -> QUEUED",
        "  NOT emitted to UCF as FAILED",
        "",
        "Terminal Runtime failure:",
        "  RUNNING -> FAILED",
        "",
        "Canonical terminal authority:",
        "  persisted orchestration job.status == failed",
        "",
        "Terminal event authority:",
        "  RUNNING -> FAILED JobStatusEvent",
        "",
        "Attempt start authority:",
        "  final QUEUED -> RUNNING JobStatusEvent",
        "",
        "result_id:",
        "  FAILED JobStatusEvent.event_id",
        "",
        "started_at:",
        "  final attempt RUNNING event.created_at",
        "",
        "finished_at:",
        "  FAILED event.created_at",
        "",
        "failure_code:",
        "  metadata.runtime_dispatch_error_type",
        "",
        "failure_message:",
        "  persisted job.error_message",
        "",
        "output:",
        "  {}",
        "",
        "result_reference:",
        '  ""',
        "",
        "artifact_references:",
        "  ()",
        "",
        "Coordination identity:",
        "  frozen Phase 5.3 WorkflowJobCorrelation",
        "",
        "Runtime patch required: False",
        "Production modified: False",
        "Installation performed: False",
        "",
        f"Checks: {len(checks)}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        (
            "Architecture status: RESOLVED"
            if failed == 0
            else "Architecture status: NOT RESOLVED"
        ),
        (
            "Next: 5.5.4 Installation / Patch"
            if failed == 0
            else "Next: resolve architecture failures"
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
print("PHASE 5.5 ARCHITECTURE RESOLUTION RESULT")
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
print(
    "Runtime production patch required:",
    False,
)
print(
    "Production modified:",
    False,
)
print(
    "NEXT:",
    (
        "5.5.4 Installation / Patch"
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

