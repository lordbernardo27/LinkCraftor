from __future__ import annotations

import ast
import hashlib
import importlib
import json
from dataclasses import fields
from pathlib import Path

from backend.server.coordination.workflow_lifecycle.lifecycle_history import (
    LIFECYCLE_HISTORY_VERSION,
    LIFECYCLE_HISTORY_SCHEMA_VERSION,
    LIFECYCLE_HISTORY_ENTRY_FIELD_COUNT,
    LifecycleHistoryError,
    InvalidLifecycleHistoryEntryError,
    DuplicateLifecycleHistoryEventError,
    LifecycleHistorySequenceError,
    LifecycleHistoryEntry,
    LifecycleHistoryValidationResult,
    create_lifecycle_history_entry,
    validate_lifecycle_history,
    append_lifecycle_history,
    sort_lifecycle_history,
    lifecycle_history_snapshot,
    explain_lifecycle_history_v3_3,
)

from backend.server.coordination.workflow_lifecycle.transition_validation import (
    TRANSITION_VALIDATION_VERSION,
)

from backend.server.coordination.workflow_lifecycle.state_machine import (
    WORKFLOW_STATE_MACHINE_VERSION,
    transition_edges,
)

from backend.server.coordination.universal_workflows.contract import (
    UniversalWorkflowStatus,
)


TARGET = Path(
    "backend/server/coordination/"
    "workflow_lifecycle/lifecycle_history.py"
)

TRANSITION_VALIDATION_FILE = Path(
    "backend/server/coordination/"
    "workflow_lifecycle/transition_validation.py"
)

STATE_MACHINE_FILE = Path(
    "backend/server/coordination/"
    "workflow_lifecycle/state_machine.py"
)

REPORT = Path(
    "lifecycle_history_phase_3_3_certification.txt"
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
            f"       {detail}"
        )

    return ok


print()
print("=" * 88)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 3.3 LIFECYCLE HISTORY CERTIFICATION")
print("=" * 88)


# ============================================================================
# 1. File / syntax / import
# ============================================================================

check(
    "Canonical Lifecycle History file exists",
    TARGET.exists(),
    str(TARGET),
)

source = TARGET.read_text(
    encoding="utf-8-sig"
)

try:
    ast.parse(source)
    syntax_ok = True
except SyntaxError as exc:
    syntax_ok = False
    print(exc)

check(
    "Python syntax parses successfully",
    syntax_ok,
)


try:
    importlib.import_module(
        "backend.server.coordination."
        "workflow_lifecycle.lifecycle_history"
    )
    import_ok = True
except Exception as exc:
    import_ok = False
    print(repr(exc))

check(
    "Lifecycle History imports successfully",
    import_ok,
)


# ============================================================================
# 2. Identity
# ============================================================================

check(
    "Lifecycle History version is canonical",
    LIFECYCLE_HISTORY_VERSION
    == "lifecycle_history_v3.3.0",
)

check(
    "Lifecycle History schema is canonical",
    LIFECYCLE_HISTORY_SCHEMA_VERSION
    == "lifecycle_history_schema_v1",
)

check(
    "Lifecycle History entry field count constant is 13",
    LIFECYCLE_HISTORY_ENTRY_FIELD_COUNT
    == 13,
)

check(
    "Frozen Transition Validation version is canonical",
    TRANSITION_VALIDATION_VERSION
    == "transition_validation_v3.2.0",
)

check(
    "Frozen Workflow State Machine version is canonical",
    WORKFLOW_STATE_MACHINE_VERSION
    == "workflow_state_machine_v3.1.0",
)


# ============================================================================
# 3. Exact entry schema
# ============================================================================

expected_fields = (
    "event_id",
    "workflow_id",
    "correlation_id",
    "from_state",
    "to_state",
    "occurred_at",
    "reason",
    "source",
    "actor_id",
    "metadata",
    "transition_validation_version",
    "state_machine_version",
    "history_version",
)

actual_fields = tuple(
    field.name
    for field
    in fields(
        LifecycleHistoryEntry
    )
)

check(
    "LifecycleHistoryEntry has exactly 13 fields",
    len(actual_fields) == 13,
)

check(
    "LifecycleHistoryEntry field order is exact",
    actual_fields == expected_fields,
)


# ============================================================================
# 4. Every frozen 3.1 transition can become history evidence
# ============================================================================

declared_edges = transition_edges()

check(
    "Frozen Phase 3.1 exposes 32 transition edges",
    len(declared_edges) == 32,
)


for index, (
    from_state,
    to_state,
) in enumerate(
    declared_edges,
    start=1,
):

    entry = create_lifecycle_history_entry(
        event_id=f"edge-{index:03d}",
        workflow_id="workflow-edge-test",
        correlation_id="correlation-edge-test",
        from_state=from_state,
        to_state=to_state,
        occurred_at=(
            f"2026-08-17T18:"
            f"{index // 60:02d}:"
            f"{index % 60:02d}+00:00"
        ),
    )

    check(
        (
            "Declared transition becomes history evidence: "
            f"{from_state.value}->{to_state.value}"
        ),
        (
            isinstance(
                entry,
                LifecycleHistoryEntry,
            )
            and entry.from_state == from_state
            and entry.to_state == to_state
            and entry.transition_validation_version
            == TRANSITION_VALIDATION_VERSION
            and entry.state_machine_version
            == WORKFLOW_STATE_MACHINE_VERSION
            and entry.history_version
            == LIFECYCLE_HISTORY_VERSION
        ),
    )


# ============================================================================
# 5. Invalid transitions cannot become history
# ============================================================================

invalid_transition_cases = (
    ("CREATED", "CREATED"),
    ("CREATED", "RUNNING"),
    ("READY", "READY"),
    ("WAITING", "READY"),
    ("WAITING", "COMPLETED"),
    ("PAUSED", "COMPLETED"),
    ("RECOVERING", "COMPLETED"),
    ("COMPLETED", "RUNNING"),
    ("FAILED", "RECOVERING"),
    ("CANCELLED", "READY"),
    ("ABORTED", "READY"),
)

for index, (
    from_state,
    to_state,
) in enumerate(
    invalid_transition_cases,
    start=1,
):

    rejected = False

    try:
        create_lifecycle_history_entry(
            event_id=f"invalid-{index:03d}",
            workflow_id="workflow-invalid",
            correlation_id="correlation-invalid",
            from_state=from_state,
            to_state=to_state,
            occurred_at=(
                "2026-08-17T18:10:00+00:00"
            ),
        )
    except InvalidLifecycleHistoryEntryError:
        rejected = True

    check(
        (
            "Invalid transition cannot become history: "
            f"{from_state}->{to_state}"
        ),
        rejected,
    )


# ============================================================================
# 6. Identity normalization / validation
# ============================================================================

normalized_entry = create_lifecycle_history_entry(
    event_id=" event-001 ",
    workflow_id=" workflow-001 ",
    correlation_id=" correlation-001 ",
    from_state=" created ",
    to_state=" ready ",
    occurred_at="2026-08-17T18:00:00Z",
    reason=" started ",
    source=" coordinator ",
    actor_id=" actor-001 ",
)

check(
    "Required identifiers normalize by trimming",
    (
        normalized_entry.event_id
        == "event-001"
        and normalized_entry.workflow_id
        == "workflow-001"
        and normalized_entry.correlation_id
        == "correlation-001"
    ),
)

check(
    "Optional provenance strings normalize by trimming",
    (
        normalized_entry.reason
        == "started"
        and normalized_entry.source
        == "coordinator"
        and normalized_entry.actor_id
        == "actor-001"
    ),
)

check(
    "Workflow states normalize through frozen lifecycle authority",
    (
        normalized_entry.from_state
        == UniversalWorkflowStatus.CREATED
        and normalized_entry.to_state
        == UniversalWorkflowStatus.READY
    ),
)

check(
    "Z timestamp normalizes to explicit UTC offset",
    normalized_entry.occurred_at
    == "2026-08-17T18:00:00+00:00",
)


for field_name, kwargs in (
    (
        "event_id",
        {
            "event_id": "",
            "workflow_id": "workflow",
            "correlation_id": "correlation",
        },
    ),
    (
        "workflow_id",
        {
            "event_id": "event",
            "workflow_id": "",
            "correlation_id": "correlation",
        },
    ),
    (
        "correlation_id",
        {
            "event_id": "event",
            "workflow_id": "workflow",
            "correlation_id": "",
        },
    ),
):

    rejected = False

    try:
        create_lifecycle_history_entry(
            **kwargs,
            from_state="CREATED",
            to_state="READY",
            occurred_at=(
                "2026-08-17T18:00:00+00:00"
            ),
        )
    except InvalidLifecycleHistoryEntryError:
        rejected = True

    check(
        f"Empty {field_name} is rejected",
        rejected,
    )


# ============================================================================
# 7. Timestamp contract
# ============================================================================

valid_timestamp_cases = (
    "2026-08-17T18:00:00+00:00",
    "2026-08-17T18:00:00Z",
    "2026-08-17T20:00:00+02:00",
)

for index, timestamp in enumerate(
    valid_timestamp_cases,
    start=1,
):

    entry = create_lifecycle_history_entry(
        event_id=f"time-valid-{index}",
        workflow_id="workflow-time",
        correlation_id="correlation-time",
        from_state="CREATED",
        to_state="READY",
        occurred_at=timestamp,
    )

    check(
        f"Timezone-aware timestamp accepted: {timestamp}",
        bool(entry.occurred_at),
    )


invalid_timestamp_cases = (
    "2026-08-17T18:00:00",
    "",
    "not-a-timestamp",
    None,
    123,
)

for index, timestamp in enumerate(
    invalid_timestamp_cases,
    start=1,
):

    rejected = False

    try:
        create_lifecycle_history_entry(
            event_id=f"time-invalid-{index}",
            workflow_id="workflow-time",
            correlation_id="correlation-time",
            from_state="CREATED",
            to_state="READY",
            occurred_at=timestamp,
        )
    except InvalidLifecycleHistoryEntryError:
        rejected = True

    check(
        f"Invalid timestamp rejected: {timestamp!r}",
        rejected,
    )


# ============================================================================
# 8. Immutability
# ============================================================================

immutable_entry = create_lifecycle_history_entry(
    event_id="immutable-001",
    workflow_id="workflow-immutable",
    correlation_id="correlation-immutable",
    from_state="CREATED",
    to_state="READY",
    occurred_at="2026-08-17T18:00:00+00:00",
    metadata={
        "level1": {
            "level2": [
                "a",
                "b",
            ]
        }
    },
)

entry_immutable = False

try:
    immutable_entry.event_id = "changed"
except Exception:
    entry_immutable = True

check(
    "LifecycleHistoryEntry is immutable",
    entry_immutable,
)


nested_metadata_immutable = False

try:
    immutable_entry.metadata[
        "level1"
    ][
        "level2"
    ] = ()
except Exception:
    nested_metadata_immutable = True

check(
    "Nested metadata is deeply immutable",
    nested_metadata_immutable,
)


entry_mapping = immutable_entry.to_dict()

entry_mapping_immutable = False

try:
    entry_mapping[
        "event_id"
    ] = "changed"
except Exception:
    entry_mapping_immutable = True

check(
    "Entry mapping is immutable",
    entry_mapping_immutable,
)


check(
    "Entry mapping contains exactly 13 fields",
    len(entry_mapping) == 13,
)


# ============================================================================
# 9. Canonical valid lifecycle chain
# ============================================================================

def make_entry(
    event_id,
    from_state,
    to_state,
    occurred_at,
    *,
    workflow_id="workflow-main",
    correlation_id="correlation-main",
):
    return create_lifecycle_history_entry(
        event_id=event_id,
        workflow_id=workflow_id,
        correlation_id=correlation_id,
        from_state=from_state,
        to_state=to_state,
        occurred_at=occurred_at,
    )


history = (
    make_entry(
        "event-001",
        "CREATED",
        "READY",
        "2026-08-17T18:00:00+00:00",
    ),
    make_entry(
        "event-002",
        "READY",
        "RUNNING",
        "2026-08-17T18:00:01+00:00",
    ),
    make_entry(
        "event-003",
        "RUNNING",
        "WAITING",
        "2026-08-17T18:00:02+00:00",
    ),
    make_entry(
        "event-004",
        "WAITING",
        "RUNNING",
        "2026-08-17T18:00:03+00:00",
    ),
    make_entry(
        "event-005",
        "RUNNING",
        "COMPLETED",
        "2026-08-17T18:00:04+00:00",
    ),
)

validation = validate_lifecycle_history(
    history
)

check(
    "Canonical lifecycle chain validates",
    validation.is_valid,
)

check(
    "Canonical lifecycle chain evaluates all nine rules",
    validation.checked_rule_count == 9,
)

check(
    "Canonical lifecycle chain entry count is exact",
    validation.entry_count == 5,
)

check(
    "Canonical lifecycle chain has no violations",
    validation.violations == (),
)


# ============================================================================
# 10. Empty lifecycle history
# ============================================================================

empty_result = validate_lifecycle_history(
    ()
)

check(
    "Empty history is structurally valid",
    (
        empty_result.is_valid
        and empty_result.entry_count == 0
        and empty_result.checked_rule_count == 9
    ),
)


# ============================================================================
# 11. Rule 1 - item type
# ============================================================================

bad_type = validate_lifecycle_history(
    (
        history[0],
        "bad-item",
    )
)

check(
    "Rule 1 rejects non-history-entry item",
    (
        not bad_type.is_valid
        and bad_type.checked_rule_count == 1
    ),
)


# ============================================================================
# 12. Rule 2 - unique event_id
# ============================================================================

duplicate_event_result = validate_lifecycle_history(
    (
        history[0],
        history[1],
        history[1],
    )
)

check(
    "Rule 2 detects duplicate event_id",
    (
        not duplicate_event_result.is_valid
        and any(
            "event_id"
            in violation
            for violation
            in duplicate_event_result.violations
        )
    ),
)


# ============================================================================
# 13. Rule 3 - workflow consistency
# ============================================================================

other_workflow = make_entry(
    "workflow-other",
    "READY",
    "RUNNING",
    "2026-08-17T18:00:01+00:00",
    workflow_id="workflow-other",
)

workflow_result = validate_lifecycle_history(
    (
        history[0],
        other_workflow,
    )
)

check(
    "Rule 3 detects workflow_id mismatch",
    (
        not workflow_result.is_valid
        and any(
            "workflow_id"
            in violation
            for violation
            in workflow_result.violations
        )
    ),
)


# ============================================================================
# 14. Rule 4 - correlation consistency
# ============================================================================

other_correlation = make_entry(
    "correlation-other",
    "READY",
    "RUNNING",
    "2026-08-17T18:00:01+00:00",
    correlation_id="correlation-other",
)

correlation_result = validate_lifecycle_history(
    (
        history[0],
        other_correlation,
    )
)

check(
    "Rule 4 detects correlation_id mismatch",
    (
        not correlation_result.is_valid
        and any(
            "correlation_id"
            in violation
            for violation
            in correlation_result.violations
        )
    ),
)


# ============================================================================
# 15. Rule 5 - chronology
# ============================================================================

reverse_time = make_entry(
    "reverse-time",
    "READY",
    "RUNNING",
    "2026-08-17T17:59:59+00:00",
)

chronology_result = validate_lifecycle_history(
    (
        history[0],
        reverse_time,
    )
)

check(
    "Rule 5 rejects chronology reversal",
    (
        not chronology_result.is_valid
        and any(
            "non-decreasing"
            in violation
            for violation
            in chronology_result.violations
        )
    ),
)


equal_time = make_entry(
    "equal-time",
    "READY",
    "RUNNING",
    "2026-08-17T18:00:00+00:00",
)

equal_time_result = validate_lifecycle_history(
    (
        history[0],
        equal_time,
    )
)

check(
    "Equal timestamps are allowed",
    equal_time_result.is_valid,
)


# ============================================================================
# 16. Rule 6 - continuity
# ============================================================================

broken_continuity = make_entry(
    "broken-continuity",
    "RUNNING",
    "COMPLETED",
    "2026-08-17T18:00:01+00:00",
)

continuity_result = validate_lifecycle_history(
    (
        history[0],
        broken_continuity,
    )
)

check(
    "Rule 6 rejects broken adjacent-state continuity",
    (
        not continuity_result.is_valid
        and any(
            "not continuous"
            in violation
            for violation
            in continuity_result.violations
        )
    ),
)


# ============================================================================
# 17. Provenance is exact at construction
# ============================================================================

check(
    "Entry carries exact Phase 3.2 validation provenance",
    history[0].transition_validation_version
    == TRANSITION_VALIDATION_VERSION,
)

check(
    "Entry carries exact Phase 3.1 state-machine provenance",
    history[0].state_machine_version
    == WORKFLOW_STATE_MACHINE_VERSION,
)

check(
    "Entry carries exact Phase 3.3 history provenance",
    history[0].history_version
    == LIFECYCLE_HISTORY_VERSION,
)


# ============================================================================
# 18. Immutable append
# ============================================================================

original = (
    history[0],
)

appended = append_lifecycle_history(
    original,
    history[1],
)

check(
    "Append returns immutable tuple",
    (
        isinstance(
            appended,
            tuple,
        )
        and appended
        == (
            history[0],
            history[1],
        )
    ),
)

check(
    "Append leaves original sequence untouched",
    original
    == (
        history[0],
    ),
)


duplicate_rejected = False

try:
    append_lifecycle_history(
        appended,
        history[1],
    )
except DuplicateLifecycleHistoryEventError:
    duplicate_rejected = True

check(
    "Append rejects duplicate event_id",
    duplicate_rejected,
)


workflow_append_rejected = False

try:
    append_lifecycle_history(
        original,
        other_workflow,
    )
except LifecycleHistorySequenceError:
    workflow_append_rejected = True

check(
    "Append rejects workflow mismatch",
    workflow_append_rejected,
)


correlation_append_rejected = False

try:
    append_lifecycle_history(
        original,
        other_correlation,
    )
except LifecycleHistorySequenceError:
    correlation_append_rejected = True

check(
    "Append rejects correlation mismatch",
    correlation_append_rejected,
)


chronology_append_rejected = False

try:
    append_lifecycle_history(
        original,
        reverse_time,
    )
except LifecycleHistorySequenceError:
    chronology_append_rejected = True

check(
    "Append rejects chronology reversal",
    chronology_append_rejected,
)


continuity_append_rejected = False

try:
    append_lifecycle_history(
        original,
        broken_continuity,
    )
except LifecycleHistorySequenceError:
    continuity_append_rejected = True

check(
    "Append rejects continuity mismatch",
    continuity_append_rejected,
)


# ============================================================================
# 19. Explicit deterministic sorting
# ============================================================================

sort_1 = make_entry(
    "event-b",
    "READY",
    "RUNNING",
    "2026-08-17T18:00:01+00:00",
    workflow_id="workflow-sort",
    correlation_id="correlation-sort",
)

sort_2 = make_entry(
    "event-a",
    "CREATED",
    "READY",
    "2026-08-17T18:00:00+00:00",
    workflow_id="workflow-sort",
    correlation_id="correlation-sort",
)

sorted_result = sort_lifecycle_history(
    (
        sort_1,
        sort_2,
    )
)

check(
    "Explicit sort orders by occurred_at then event_id",
    tuple(
        entry.event_id
        for entry
        in sorted_result
    )
    == (
        "event-a",
        "event-b",
    ),
)


# ============================================================================
# 20. Snapshot
# ============================================================================

snapshot = lifecycle_history_snapshot(
    history
)

check(
    "Snapshot history version is canonical",
    snapshot[
        "history_version"
    ]
    == LIFECYCLE_HISTORY_VERSION,
)

check(
    "Snapshot schema is canonical",
    snapshot[
        "schema_version"
    ]
    == LIFECYCLE_HISTORY_SCHEMA_VERSION,
)

check(
    "Snapshot field count is 13",
    snapshot[
        "entry_field_count"
    ]
    == 13,
)

check(
    "Snapshot references frozen 3.2",
    snapshot[
        "transition_validation_version"
    ]
    == TRANSITION_VALIDATION_VERSION,
)

check(
    "Snapshot references frozen 3.1",
    snapshot[
        "state_machine_version"
    ]
    == WORKFLOW_STATE_MACHINE_VERSION,
)

check(
    "Snapshot reports exact entry count",
    snapshot[
        "entry_count"
    ]
    == 5,
)

check(
    "Snapshot reports history valid",
    snapshot[
        "is_valid"
    ]
    is True,
)

check(
    "Snapshot reports nine validation rules",
    snapshot[
        "validation_rule_count"
    ]
    == 9,
)


snapshot_immutable = False

try:
    snapshot[
        "entry_count"
    ] = 100
except Exception:
    snapshot_immutable = True

check(
    "Snapshot mapping is immutable",
    snapshot_immutable,
)


for flag in (
    "workflow_mutation",
    "transition_execution",
    "terminal_protection_enforcement",
    "durable_persistence",
    "runtime_execution",
    "recovery_execution",
    "security_audit_trail",
):

    check(
        f"Snapshot declares {flag}=False",
        snapshot[
            flag
        ]
        is False,
    )


# ============================================================================
# 21. Validation-result contract
# ============================================================================

check(
    "Validation result object is canonical type",
    isinstance(
        validation,
        LifecycleHistoryValidationResult,
    ),
)


validation_immutable = False

try:
    validation.is_valid = False
except Exception:
    validation_immutable = True

check(
    "Validation result is immutable",
    validation_immutable,
)


validation_mapping = validation.to_dict()

validation_mapping_immutable = False

try:
    validation_mapping[
        "entry_count"
    ] = 999
except Exception:
    validation_mapping_immutable = True

check(
    "Validation result mapping is immutable",
    validation_mapping_immutable,
)


# ============================================================================
# 22. Architecture declaration
# ============================================================================

explanation = explain_lifecycle_history_v3_3()

check(
    "Architecture identifies Phase 3.3",
    explanation[
        "phase"
    ]
    == "3.3",
)

check(
    "Architecture identifies Lifecycle History",
    explanation[
        "component"
    ]
    == "Lifecycle History",
)

check(
    "Architecture field count is 13",
    explanation[
        "entry_field_count"
    ]
    == 13,
)

check(
    "Architecture sequence rule count is 9",
    explanation[
        "sequence_rule_count"
    ]
    == 9,
)

check(
    "Architecture references exact 3.2",
    explanation[
        "transition_validation_version"
    ]
    == TRANSITION_VALIDATION_VERSION,
)

check(
    "Architecture references exact 3.1",
    explanation[
        "state_machine_version"
    ]
    == WORKFLOW_STATE_MACHINE_VERSION,
)


required_owns = (
    "canonical lifecycle history-entry contract",
    "immutable transition-history evidence",
    "valid-transition provenance",
    "history event identity validation",
    "workflow identity consistency",
    "correlation identity consistency",
    "chronology validation",
    "adjacent-state continuity validation",
    "deterministic history inspection",
    "immutable append semantics",
    "immutable history snapshot/evidence",
    "Lifecycle History architecture explanation",
)

for item in required_owns:

    check(
        f"Lifecycle History owns: {item}",
        item
        in explanation[
            "owns"
        ],
    )


required_exclusions = (
    "workflow lifecycle graph",
    "workflow status vocabulary",
    "requested-transition legality",
    "workflow status mutation",
    "transition execution",
    "terminal-state protection enforcement",
    "durable persistence",
    "checkpoints",
    "pause execution",
    "resume execution",
    "recovery execution",
    "recovery policy",
    "Runtime Registration",
    "Runtime jobs",
    "coordinator execution",
    "dependency planning",
    "stage result handoff",
    "security audit trail",
)

for item in required_exclusions:

    check(
        f"Lifecycle History excludes: {item}",
        item
        in explanation[
            "does_not_own"
        ],
    )


check(
    "3.4 remains Terminal-State Protection authority",
    explanation[
        "future_authority"
    ][
        "3.4"
    ]
    == "Terminal-State Protection",
)

check(
    "Phase 8 remains persistence authority",
    explanation[
        "future_authority"
    ][
        "8.0"
    ]
    == "Workflow State Persistence",
)

check(
    "Phase 9 remains recovery authority",
    explanation[
        "future_authority"
    ][
        "9.0"
    ]
    == "Coordination Recovery",
)

check(
    "10.5 remains Audit Trail authority",
    explanation[
        "future_authority"
    ][
        "10.5"
    ]
    == "Audit Trail",
)


# ============================================================================
# 23. Error hierarchy
# ============================================================================

check(
    "InvalidLifecycleHistoryEntryError derives from LifecycleHistoryError",
    issubclass(
        InvalidLifecycleHistoryEntryError,
        LifecycleHistoryError,
    ),
)

check(
    "DuplicateLifecycleHistoryEventError derives from LifecycleHistoryError",
    issubclass(
        DuplicateLifecycleHistoryEventError,
        LifecycleHistoryError,
    ),
)

check(
    "LifecycleHistorySequenceError derives from LifecycleHistoryError",
    issubclass(
        LifecycleHistorySequenceError,
        LifecycleHistoryError,
    ),
)


# ============================================================================
# 24. Static import boundary
# ============================================================================

tree = ast.parse(
    source
)

backend_imports = []

for node in ast.walk(
    tree
):

    if isinstance(
        node,
        ast.Import,
    ):

        for alias in node.names:

            if alias.name.startswith(
                "backend."
            ):
                backend_imports.append(
                    alias.name
                )

    elif isinstance(
        node,
        ast.ImportFrom,
    ):

        module = (
            node.module
            or ""
        )

        if module.startswith(
            "backend."
        ):
            backend_imports.append(
                module
            )


allowed_backend_imports = {
    (
        "backend.server.coordination."
        "universal_workflows.contract"
    ),
    (
        "backend.server.coordination."
        "workflow_lifecycle.state_machine"
    ),
    (
        "backend.server.coordination."
        "workflow_lifecycle.transition_validation"
    ),
}

check(
    "Lifecycle History imports only canonical lifecycle dependencies",
    set(
        backend_imports
    ).issubset(
        allowed_backend_imports
    ),
    json.dumps(
        backend_imports
    ),
)


forbidden_import_fragments = (
    "backend.server.runtime",
    "backend.server.workers",
    "backend.server.jobs",
    "backend.server.pipelines",
    "backend.server.routes",
    "backend.server.coordination.workflow_registry",
    "backend.server.coordination.coordinator_registry",
    "backend.server.coordination.registration_validation",
    "backend.server.coordination.version_management",
)

violating_imports = [
    item
    for item
    in backend_imports
    if any(
        fragment
        in item
        for fragment
        in forbidden_import_fragments
    )
]

check(
    "Lifecycle History has no runtime/registry/execution imports",
    not violating_imports,
    json.dumps(
        violating_imports
    ),
)


# ============================================================================
# 25. Static mutation / persistence boundary
# ============================================================================

forbidden_markers = (
    "datetime.now(",
    "datetime.utcnow(",
    "uuid.uuid",
    "random.",
    "transition_universal_orchestration_state",
    "dispatch(",
    "execute(",
    "run_coordinator(",
    "invoke_coordinator(",
    "register_workflow",
    "register_coordinator",
    "set_preferred_",
    "write_text(",
    "write_bytes(",
    "sqlite",
    "boto3",
    "requests.",
    "redis.",
    "s3.",
)

marker_violations = [
    marker
    for marker
    in forbidden_markers
    if marker
    in source
]

check(
    "Lifecycle History performs no hidden execution/persistence/ID-time generation",
    not marker_violations,
    json.dumps(
        marker_violations
    ),
)


# ============================================================================
# 26. No second lifecycle graph / validator
# ============================================================================

duplicate_authority_markers = (
    "_WORKFLOW_TRANSITION_GRAPH",
    "_ALLOWED_TRANSITIONS",
    "allowed_transitions = {",
    "transition_graph = {",
    "def validate_workflow_transition(",
)

duplicate_authority = [
    marker
    for marker
    in duplicate_authority_markers
    if marker
    in source
]

check(
    "Lifecycle History defines no duplicate lifecycle graph or 3.2 validator",
    not duplicate_authority,
    json.dumps(
        duplicate_authority
    ),
)

check(
    "Lifecycle History consumes frozen validate_workflow_transition",
    "validate_workflow_transition("
    in source,
)


# ============================================================================
# 27. Frozen upstream hash integrity
# ============================================================================

frozen_files = (
    (
        "Phase 3.2 Transition Validation",
        TRANSITION_VALIDATION_FILE,
        (
            "69A952141E920E63B32B12AF1E9FB79D"
            "6296961FED40BCB94F007123BF9BD746"
        ),
    ),
    (
        "Phase 3.1 Workflow State Machine",
        STATE_MACHINE_FILE,
        (
            "144327A4E9C8989FCF0F4DBD10BCF6D7"
            "203F503930D81CB8E24644D86D2BB662"
        ),
    ),
    (
        "Phase 2.1 Workflow Registry",
        Path(
            "backend/server/coordination/"
            "workflow_registry/registry.py"
        ),
        (
            "34786F74443BAC9049F3CD805CBF8BDB"
            "6275C6EF05B94C9BF42579E114CA4564"
        ),
    ),
    (
        "Phase 2.2 Coordinator Registration",
        Path(
            "backend/server/coordination/"
            "coordinator_registry/registry.py"
        ),
        (
            "C9E324DF0C4D5AEA8D1D0C91D8FB3A3"
            "B479BB9A0830B0C4494186C01C298F071"
        ),
    ),
    (
        "Phase 2.3 Registration Validation",
        Path(
            "backend/server/coordination/"
            "registration_validation/validator.py"
        ),
        (
            "30853E34C6F09B89A2C67D50D91C06EB"
            "4B2436A12918DC4E26197EB6159E8453"
        ),
    ),
    (
        "Phase 2.4 Version Management",
        Path(
            "backend/server/coordination/"
            "version_management/manager.py"
        ),
        (
            "118B628ABFCA7CF74B218520D6CF6E0AD"
            "4AF2CD6FFE9FB7FE711927A68412E25"
        ),
    ),
)


for (
    name,
    path,
    expected,
) in frozen_files:

    actual = hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()

    check(
        f"Frozen {name} hash unchanged",
        actual == expected,
        actual,
    )


# ============================================================================
# 28. Canonical Phase 3.3 SHA256
# ============================================================================

sha256 = hashlib.sha256(
    TARGET.read_bytes()
).hexdigest().upper()

print()
print("Canonical SHA256:")
print(
    sha256
)


# ============================================================================
# 29. Final result
# ============================================================================

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
    "PHASE 3.3 LIFECYCLE HISTORY CERTIFICATION",
    "=" * 88,
    "",
    (
        "Lifecycle History Version: "
        + LIFECYCLE_HISTORY_VERSION
    ),
    (
        "Lifecycle History Schema: "
        + LIFECYCLE_HISTORY_SCHEMA_VERSION
    ),
    (
        "Transition Validation Version: "
        + TRANSITION_VALIDATION_VERSION
    ),
    (
        "Workflow State Machine Version: "
        + WORKFLOW_STATE_MACHINE_VERSION
    ),
    "",
    "Lifecycle History Entry Fields: 13",
    "Lifecycle History Sequence Rules: 9",
    "Declared Phase-3.1 Edges Proven Recordable: 32",
    "",
    "Workflow Mutation Authority: NONE",
    "Transition Execution Authority: NONE",
    "Transition Legality Authority: NONE (Phase 3.2)",
    "Terminal Protection Authority: NONE (Phase 3.4)",
    "Durable Persistence Authority: NONE (Phase 8)",
    "Recovery Authority: NONE (Phase 9)",
    "Runtime Execution Authority: NONE",
    "Security Audit Trail Authority: NONE (Phase 10.5)",
    "",
    f"Checks: {len(checks)}",
    f"Passed: {passed}",
    f"Failed: {failed}",
    f"SHA256: {sha256}",
    "",
    (
        "STATUS: CERTIFICATION PASSED"
        if failed == 0
        else "STATUS: CERTIFICATION FAILED"
    ),
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
            f"    {detail}"
        )


REPORT.write_text(
    "\n".join(
        lines
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 88)
print("CERTIFICATION RESULT")
print("=" * 88)

print(
    f"Checks: {len(checks)}"
)

print(
    f"Passed: {passed}"
)

print(
    f"Failed: {failed}"
)

print()

print(
    "STATUS: CERTIFICATION PASSED"
    if failed == 0
    else "STATUS: CERTIFICATION FAILED"
)

print()

print(
    "REPORT:",
    REPORT,
)

print("=" * 88)

raise SystemExit(
    0
    if failed == 0
    else 1
)
