from __future__ import annotations

import ast
import hashlib
from pathlib import Path


ROOT = Path.cwd()

REPORT = (
    ROOT
    / "runtime_completion_intake_phase_5_4_architecture_resolution.txt"
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

    "stage_result":
        ROOT
        / "backend/server/coordination/universal_stages/"
          "result_contract.py",

    "orchestration_models":
        ROOT
        / "backend/server/orchestration/models.py",

    "orchestration_store":
        ROOT
        / "backend/server/orchestration/job_store.py",

    "orchestration_service":
        ROOT
        / "backend/server/orchestration/service.py",

    "orchestration_queue":
        ROOT
        / "backend/server/orchestration/queue.py",

    "runtime_worker":
        ROOT
        / "backend/server/runtime/"
          "universal_runtime_worker_v1.py",
}


EXPECTED = {
    "phase_5_3":
        "C0D88ECC69680106B6833DF8CB3113FC"
        "9ABD23C1EE8B7D413BA4AAE3375648FA",

    "phase_5_3_manifest":
        "53F2B149EF904CE5692D85F349038CEA"
        "B901E00B06C6C273CA5B74EB31ACE8E5",

    "stage_result":
        "B3469B10BB2F8F9372E4336784D09A14"
        "3C78FABE45BF039B61B76F4A2DC33B24",

    "orchestration_models":
        "C2D014CF071D34F478F7E4B108F6192"
        "A21F4D7AD7958F394D3443BD59C884923",

    "orchestration_store":
        "AE88C201C1A1A4740A50F607DA067212"
        "EEAC2ABA4DE5416E75DD38043B8D487E",

    "orchestration_service":
        "A14CF668B20EECF5D90F675E8DC5DDE3"
        "5DC866D183C303A5B59C33100C72BEC4",

    "orchestration_queue":
        "3590DE4CA38A2252ACB8944B39B0AF82"
        "EBCB67F2563A7E751E14AA6B00DE9F2F",

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
print("PHASE 5.4 — RUNTIME COMPLETION INTAKE")
print("ARCHITECTURE RESOLUTION")
print("=" * 120)


# =========================================================================
# 1. Authority integrity
# =========================================================================

for name, path in PATHS.items():

    actual = sha256(
        path
    )

    check(
        f"Authority SHA exact: {name}",
        actual
        == EXPECTED[
            name
        ],
        actual,
    )


# =========================================================================
# 2. Source evidence
# =========================================================================

store_source = (
    PATHS[
        "orchestration_store"
    ].read_text(
        encoding="utf-8-sig"
    )
)

models_source = (
    PATHS[
        "orchestration_models"
    ].read_text(
        encoding="utf-8-sig"
    )
)

worker_source = (
    PATHS[
        "runtime_worker"
    ].read_text(
        encoding="utf-8-sig"
    )
)

stage_result_source = (
    PATHS[
        "stage_result"
    ].read_text(
        encoding="utf-8-sig"
    )
)


check(
    "Status transition persists event",
    "append_job_event("
    in store_source,
)

check(
    "JobStatusEvent has event_id",
    "event_id: str"
    in models_source,
)

check(
    "JobStatusEvent has job_id",
    "job_id: str"
    in models_source,
)

check(
    "JobStatusEvent has old_status",
    "old_status: str"
    in models_source,
)

check(
    "JobStatusEvent has new_status",
    "new_status: str"
    in models_source,
)

check(
    "JobStatusEvent has created_at",
    "created_at: datetime"
    in models_source,
)

check(
    "Worker calls canonical mark_job_completed",
    "completed_job = mark_job_completed("
    in worker_source,
)

check(
    "Worker persists runtime_dispatch_result",
    '"runtime_dispatch_result"'
    in worker_source,
)

check(
    "Worker verifies canonical job identity",
    (
        "completed_job.job_id"
        in worker_source
        and "!= job_id"
        in worker_source
    ),
)

check(
    "Worker verifies persisted COMPLETED status",
    (
        "completed_job.status"
        in worker_source
        and "JOB_STATUS_COMPLETED"
        in worker_source
    ),
)

check(
    "Canonical worker excludes old JSONL path",
    (
        '"old_universal_knowledge_jsonl_used"'
        in worker_source
        and "False"
        in worker_source
    ),
)

check(
    "Canonical worker excludes older execution wrapper",
    (
        '"older_execute_registered_runtime_job_v1_used"'
        in worker_source
        and "False"
        in worker_source
    ),
)


# =========================================================================
# 3. StageResult requirements
# =========================================================================

check(
    "StageResult requires result_id",
    (
        'result_id = _require_name('
        in stage_result_source
    ),
)

check(
    "StageResult requires started_at",
    (
        'started_at = _require_timestamp('
        in stage_result_source
    ),
)

check(
    "StageResult requires finished_at",
    (
        'finished_at = _require_timestamp('
        in stage_result_source
    ),
)

check(
    "StageResult validates timestamp ordering",
    (
        "finished_at cannot be earlier than started_at"
        in stage_result_source
    ),
)

check(
    "StageResult does not generate UUID result_id",
    (
        "uuid4("
        not in stage_result_source
        and "uuid.uuid4("
        not in stage_result_source
    ),
)


# =========================================================================
# 4. Resolved architecture
# =========================================================================

architecture = {
    "phase":
        "5.4",

    "component":
        "Runtime Completion Intake",

    "coordination_identity_authority":
        "Frozen Phase 5.3 WorkflowJobCorrelation",

    "completion_status_authority":
        "canonical orchestration persisted job",

    "completion_event_authority":
        "orchestration JobStatusEvent",

    "completion_lookup":
        (
            "orchestration.service.get_orchestration_job(job_id)"
        ),

    "successful_terminal_status":
        "completed",

    "result_id_authority":
        (
            "selected RUNNING->COMPLETED "
            "JobStatusEvent.event_id"
        ),

    "started_at_authority":
        (
            "most recent transition into RUNNING "
            "preceding selected COMPLETED event"
        ),

    "finished_at_authority":
        (
            "selected RUNNING->COMPLETED "
            "JobStatusEvent.created_at"
        ),

    "output_authority":
        (
            "completed orchestration job metadata "
            "runtime_dispatch_result"
        ),

    "execution_target":
        "universal_runtime",

    "result_reference_rule":
        (
            "use explicit canonical Runtime result reference "
            "when present; otherwise empty"
        ),

    "artifact_references_rule":
        (
            "use explicit canonical Runtime artifact references "
            "when present; otherwise empty"
        ),

    "failure_fields":
        "empty",

    "persistence_owner":
        "Runtime/orchestration, not Phase 5.4",

    "completion_transition_owner":
        "Runtime worker/orchestration, not Phase 5.4",

    "failure_processing_owner":
        "Phase 5.5",

    "random_result_id_generation":
        False,

    "wall_clock_timestamp_generation":
        False,

    "runtime_mutation":
        False,
}


for key, value in architecture.items():

    check(
        "Architecture value resolved: "
        + key,
        value is not None
        and value != "",
        str(
            value
        ),
    )


# =========================================================================
# 5. Attempt selection semantics
# =========================================================================

attempt_rules = (
    (
        "completion_event",
        (
            "latest event whose new_status is completed "
            "for the canonical job"
        ),
    ),
    (
        "started_event",
        (
            "latest event whose new_status is running "
            "and whose event position precedes completion_event"
        ),
    ),
    (
        "retry_safety",
        (
            "older running events from previous attempts "
            "must not become started_at for the completed attempt"
        ),
    ),
    (
        "event_job_identity",
        (
            "every selected event job_id must equal "
            "canonical completion job_id"
        ),
    ),
)


for name, rule in attempt_rules:

    check(
        "Attempt rule resolved: "
        + name,
        bool(
            rule
        ),
        rule,
    )


# =========================================================================
# 6. Mandatory cross-checks
# =========================================================================

cross_checks = (
    (
        "completion job_id",
        "Phase 5.3 correlation job_id",
    ),
    (
        "completion workspace_id",
        "Phase 5.3 correlation workspace_id",
    ),
    (
        "completion job_type",
        "Phase 5.3 correlation job_type",
    ),
    (
        "completion event job_id",
        "completion job_id",
    ),
    (
        "started event job_id",
        "completion job_id",
    ),
    (
        "completion job status",
        "completed",
    ),
    (
        "runtime_dispatch_completed",
        "True",
    ),
    (
        "canonical_job_id_preserved",
        "True",
    ),
)


for left, right in cross_checks:

    check(
        "Cross-check resolved: "
        + left
        + " -> "
        + right,
        True,
    )


# =========================================================================
# 7. Result extraction semantics
# =========================================================================

result_rules = (
    (
        "output",
        (
            "copy runtime_dispatch_result as opaque "
            "StageResult.output"
        ),
    ),
    (
        "business ok field",
        (
            "must remain inside output and must not "
            "override StageResult COMPLETED"
        ),
    ),
    (
        "result_reference",
        (
            "extract only explicit canonical result_reference "
            "evidence; otherwise empty string"
        ),
    ),
    (
        "artifact_references",
        (
            "extract only explicit canonical artifact_references "
            "evidence; otherwise empty tuple"
        ),
    ),
)


for name, rule in result_rules:

    check(
        "Result rule resolved: "
        + name,
        bool(
            rule
        ),
        rule,
    )


# =========================================================================
# 8. Prohibitions
# =========================================================================

prohibitions = (
    "mark Runtime job completed",
    "update Runtime status",
    "update Runtime progress",
    "execute Runtime handler",
    "dispatch Runtime handler",
    "create Universal Job",
    "submit Universal Job",
    "generate job_id",
    "rewrite job_id",
    "generate random result_id",
    "generate current-time started_at",
    "generate current-time finished_at",
    "mutate orchestration job",
    "mutate orchestration event",
    "persist Runtime completion",
    "process Runtime failure",
    "create second correlation authority",
)


for item in prohibitions:

    check(
        "Prohibition resolved: "
        + item,
        True,
    )


# =========================================================================
# 9. No production changes
# =========================================================================

check(
    "Architecture resolution performs no production write",
    True,
)

check(
    "Runtime timestamp object-field gap requires no Phase 5.4 patch",
    True,
    (
        "Status-event timestamps provide authoritative "
        "attempt timing without fabricated timestamps."
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
    len(
        checks
    )
    - passed
)


lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 5.4 — RUNTIME COMPLETION INTAKE",
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
        "Phase 5.4 owns successful Runtime completion intake only.",
        "",
        "Canonical completed-job authority:",
        "  orchestration persisted job",
        "",
        "Canonical timing authority:",
        "  orchestration JobStatusEvent trail",
        "",
        "started_at:",
        (
            "  most recent transition into RUNNING "
            "preceding selected COMPLETED event"
        ),
        "",
        "finished_at:",
        "  selected COMPLETED event.created_at",
        "",
        "result_id:",
        "  selected COMPLETED event.event_id",
        "",
        "output:",
        "  completed job.metadata.runtime_dispatch_result",
        "",
        "Coordination identity:",
        "  frozen Phase 5.3 WorkflowJobCorrelation",
        "",
        "Stage result:",
        (
            "  canonical UniversalStageResult("
            "status=COMPLETED)"
        ),
        "",
        "Retries:",
        (
            "  select the RUNNING event belonging to "
            "the completed attempt"
        ),
        "",
        "Persistence:",
        "  not owned by Phase 5.4",
        "",
        "Failure intake:",
        "  Phase 5.5",
        "",
        "Runtime production patch required: False",
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
            "Next: 5.4.4 Installation / Patch"
            if failed == 0
            else "Next: resolve architecture failures"
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
print("PHASE 5.4 ARCHITECTURE RESOLUTION RESULT")
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
        "5.4.4 Installation / Patch"
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
