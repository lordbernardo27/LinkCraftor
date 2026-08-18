from __future__ import annotations

import ast
import hashlib
import importlib
from dataclasses import fields
from pathlib import Path
from types import MappingProxyType

from backend.server.coordination.workflow_lifecycle.state_machine import (
    WORKFLOW_STATE_MACHINE_VERSION,
    workflow_states,
    transition_edges,
)

from backend.server.coordination.workflow_lifecycle.transition_validation import (
    TRANSITION_VALIDATION_VERSION,
    validate_workflow_transition,
)

from backend.server.coordination.workflow_lifecycle.lifecycle_history import (
    LIFECYCLE_HISTORY_VERSION,
    LIFECYCLE_HISTORY_SCHEMA_VERSION,
    LIFECYCLE_HISTORY_ENTRY_FIELD_COUNT,
    LifecycleHistoryEntry,
    LifecycleHistoryValidationResult,
    InvalidLifecycleHistoryEntryError,
    create_lifecycle_history_entry,
    validate_lifecycle_history,
    append_lifecycle_history,
    sort_lifecycle_history,
    lifecycle_history_snapshot,
    explain_lifecycle_history_v3_3,
)


ROOT = Path.cwd()

PHASE_31 = ROOT / (
    "backend/server/coordination/"
    "workflow_lifecycle/state_machine.py"
)

PHASE_32 = ROOT / (
    "backend/server/coordination/"
    "workflow_lifecycle/transition_validation.py"
)

PHASE_33 = ROOT / (
    "backend/server/coordination/"
    "workflow_lifecycle/lifecycle_history.py"
)

REPORT = ROOT / (
    "workflow_lifecycle_phase_3_3_recertification.txt"
)


EXPECTED_31_SHA = (
    "144327A4E9C8989FCF0F4DBD10BCF6D"
    "7203F503930D81CB8E24644D86D2BB662"
)

EXPECTED_32_SHA = (
    "69A952141E920E63B32B12AF1E9FB79D"
    "6296961FED40BCB94F007123BF9BD746"
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


def sha256_file(path):
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


print()
print("=" * 96)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 3.3 — LIFECYCLE HISTORY FINAL RE-CERTIFICATION")
print("=" * 96)


# ============================================================================
# 1. Files / syntax / import
# ============================================================================

for phase, path in (
    ("3.1", PHASE_31),
    ("3.2", PHASE_32),
    ("3.3", PHASE_33),
):

    check(
        f"Phase {phase} canonical file exists",
        path.exists(),
        str(path.relative_to(ROOT)),
    )


source = PHASE_33.read_text(
    encoding="utf-8-sig"
)

try:
    tree = ast.parse(source)
    syntax_ok = True
except SyntaxError:
    tree = None
    syntax_ok = False

check(
    "Phase 3.3 Python syntax parses",
    syntax_ok,
)


try:
    importlib.import_module(
        "backend.server.coordination."
        "workflow_lifecycle.lifecycle_history"
    )
    import_ok = True
except Exception:
    import_ok = False

check(
    "Phase 3.3 imports successfully",
    import_ok,
)


# ============================================================================
# 2. Upstream frozen integrity
# ============================================================================

actual_31 = sha256_file(PHASE_31)
actual_32 = sha256_file(PHASE_32)

check(
    "Frozen Phase 3.1 SHA unchanged",
    actual_31 == EXPECTED_31_SHA,
    actual_31,
)

check(
    "Frozen Phase 3.2 SHA unchanged",
    actual_32 == EXPECTED_32_SHA,
    actual_32,
)


# ============================================================================
# 3. Identity
# ============================================================================

check(
    "3.1 version exact",
    WORKFLOW_STATE_MACHINE_VERSION
    == "workflow_state_machine_v3.1.0",
)

check(
    "3.2 version exact",
    TRANSITION_VALIDATION_VERSION
    == "transition_validation_v3.2.0",
)

check(
    "3.3 version exact",
    LIFECYCLE_HISTORY_VERSION
    == "lifecycle_history_v3.3.0",
)

check(
    "3.3 schema exact",
    LIFECYCLE_HISTORY_SCHEMA_VERSION
    == "lifecycle_history_schema_v1",
)

check(
    "Lifecycle History entry field count constant is 13",
    LIFECYCLE_HISTORY_ENTRY_FIELD_COUNT
    == 13,
)


# ============================================================================
# 4. Exact entry contract
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
    item.name
    for item
    in fields(
        LifecycleHistoryEntry
    )
)

check(
    "LifecycleHistoryEntry has exactly 13 fields",
    len(actual_fields) == 13,
)

check(
    "LifecycleHistoryEntry field order exact",
    actual_fields == expected_fields,
)


# ============================================================================
# 5. Every legal Phase 3.1 edge recordable
# ============================================================================

edges = transition_edges()

check(
    "Canonical transition edge count is 32",
    len(edges) == 32,
)


legal_entries = []

for index, (
    current,
    requested,
) in enumerate(
    edges,
    start=1,
):

    try:
        entry = create_lifecycle_history_entry(
            event_id=f"recert-legal-{index:03d}",
            workflow_id="phase-3-3-recert",
            correlation_id="phase-3-3-recert",
            from_state=current,
            to_state=requested,
            occurred_at=(
                f"2026-08-17T00:{index // 60:02d}:{index % 60:02d}+00:00"
            ),
        )

        valid = (
            entry.from_state == current
            and entry.to_state == requested
            and entry.transition_validation_version
                == TRANSITION_VALIDATION_VERSION
            and entry.state_machine_version
                == WORKFLOW_STATE_MACHINE_VERSION
            and entry.history_version
                == LIFECYCLE_HISTORY_VERSION
        )

    except Exception:
        valid = False

    check(
        (
            "Legal history edge recordable: "
            f"{current.value}->{requested.value}"
        ),
        valid,
    )

    if valid:
        legal_entries.append(entry)


check(
    "All 32 legal edges recordable",
    len(legal_entries) == 32,
)


# ============================================================================
# 6. Every undeclared pair rejected
# ============================================================================

states = workflow_states()
declared = set(edges)

invalid_total = 0
invalid_rejected = 0

for current in states:

    for requested in states:

        if (
            current,
            requested,
        ) in declared:
            continue

        invalid_total += 1

        try:
            create_lifecycle_history_entry(
                event_id=(
                    f"recert-invalid-"
                    f"{current.value}-"
                    f"{requested.value}"
                ),
                workflow_id="phase-3-3-recert",
                correlation_id="phase-3-3-recert",
                from_state=current,
                to_state=requested,
                occurred_at="2026-08-17T01:00:00+00:00",
            )

            rejected = False

        except InvalidLifecycleHistoryEntryError:
            rejected = True

        except Exception:
            rejected = False

        if rejected:
            invalid_rejected += 1


check(
    "Exactly 68 undeclared state pairs tested",
    invalid_total == 68,
)

check(
    "All 68 undeclared state pairs rejected",
    invalid_rejected == 68,
)


# ============================================================================
# 7. Valid continuous history
# ============================================================================

e1 = create_lifecycle_history_entry(
    event_id="chain-001",
    workflow_id="chain-workflow",
    correlation_id="chain-correlation",
    from_state="CREATED",
    to_state="READY",
    occurred_at="2026-08-17T02:00:00+00:00",
)

e2 = create_lifecycle_history_entry(
    event_id="chain-002",
    workflow_id="chain-workflow",
    correlation_id="chain-correlation",
    from_state="READY",
    to_state="RUNNING",
    occurred_at="2026-08-17T02:00:01+00:00",
)

e3 = create_lifecycle_history_entry(
    event_id="chain-003",
    workflow_id="chain-workflow",
    correlation_id="chain-correlation",
    from_state="RUNNING",
    to_state="COMPLETED",
    occurred_at="2026-08-17T02:00:02+00:00",
)

valid_chain = (
    e1,
    e2,
    e3,
)

chain_validation = validate_lifecycle_history(
    valid_chain
)

check(
    "validate_lifecycle_history returns canonical result",
    isinstance(
        chain_validation,
        LifecycleHistoryValidationResult,
    ),
)

check(
    "Valid continuous lifecycle history accepted",
    chain_validation.is_valid is True,
)

check(
    "Valid continuous history has no violations",
    chain_validation.violations == (),
)


# ============================================================================
# 8. Empty history
# ============================================================================

empty_validation = validate_lifecycle_history(
    ()
)

check(
    "Empty lifecycle history remains valid",
    empty_validation.is_valid is True,
)


# ============================================================================
# 9. Duplicate event_id protection
# ============================================================================

duplicate_event = create_lifecycle_history_entry(
    event_id="chain-001",
    workflow_id="chain-workflow",
    correlation_id="chain-correlation",
    from_state="READY",
    to_state="RUNNING",
    occurred_at="2026-08-17T02:00:01+00:00",
)

duplicate_result = validate_lifecycle_history(
    (
        e1,
        duplicate_event,
    )
)

check(
    "Duplicate event_id history rejected",
    duplicate_result.is_valid is False,
)


# ============================================================================
# 10. Workflow identity consistency
# ============================================================================

different_workflow = create_lifecycle_history_entry(
    event_id="other-workflow",
    workflow_id="different-workflow",
    correlation_id="chain-correlation",
    from_state="READY",
    to_state="RUNNING",
    occurred_at="2026-08-17T02:00:01+00:00",
)

workflow_result = validate_lifecycle_history(
    (
        e1,
        different_workflow,
    )
)

check(
    "Mixed workflow_id history rejected",
    workflow_result.is_valid is False,
)


# ============================================================================
# 11. Correlation consistency
# ============================================================================

different_correlation = create_lifecycle_history_entry(
    event_id="other-correlation",
    workflow_id="chain-workflow",
    correlation_id="different-correlation",
    from_state="READY",
    to_state="RUNNING",
    occurred_at="2026-08-17T02:00:01+00:00",
)

correlation_result = validate_lifecycle_history(
    (
        e1,
        different_correlation,
    )
)

check(
    "Mixed correlation_id history rejected",
    correlation_result.is_valid is False,
)


# ============================================================================
# 12. Continuity
# ============================================================================

broken_continuity = create_lifecycle_history_entry(
    event_id="broken-continuity",
    workflow_id="chain-workflow",
    correlation_id="chain-correlation",
    from_state="PAUSED",
    to_state="RUNNING",
    occurred_at="2026-08-17T02:00:01+00:00",
)

continuity_result = validate_lifecycle_history(
    (
        e1,
        broken_continuity,
    )
)

check(
    "Broken from_state/to_state continuity rejected",
    continuity_result.is_valid is False,
)


# ============================================================================
# 13. Time ordering
# ============================================================================

earlier_entry = create_lifecycle_history_entry(
    event_id="earlier-entry",
    workflow_id="chain-workflow",
    correlation_id="chain-correlation",
    from_state="READY",
    to_state="RUNNING",
    occurred_at="2026-08-17T01:59:59+00:00",
)

time_result = validate_lifecycle_history(
    (
        e1,
        earlier_entry,
    )
)

check(
    "Decreasing occurred_at ordering rejected",
    time_result.is_valid is False,
)


equal_time_entry = create_lifecycle_history_entry(
    event_id="equal-time-entry",
    workflow_id="chain-workflow",
    correlation_id="chain-correlation",
    from_state="READY",
    to_state="RUNNING",
    occurred_at="2026-08-17T02:00:00+00:00",
)

equal_time_result = validate_lifecycle_history(
    (
        e1,
        equal_time_entry,
    )
)

check(
    "Equal occurred_at timestamps remain permitted",
    equal_time_result.is_valid is True,
)


# ============================================================================
# 14. Append behavior
# ============================================================================

appended = append_lifecycle_history(
    (
        e1,
        e2,
    ),
    e3,
)

check(
    "append_lifecycle_history returns tuple",
    isinstance(
        appended,
        tuple,
    ),
)

check(
    "append_lifecycle_history appends without mutation",
    appended == valid_chain,
)


# ============================================================================
# 15. Sort behavior
# ============================================================================

sorted_history = sort_lifecycle_history(
    (
        e3,
        e1,
        e2,
    )
)

check(
    "sort_lifecycle_history orders deterministically",
    sorted_history == valid_chain,
)


same_time_a = create_lifecycle_history_entry(
    event_id="a-event",
    workflow_id="sort-workflow",
    correlation_id="sort-correlation",
    from_state="CREATED",
    to_state="READY",
    occurred_at="2026-08-17T03:00:00+00:00",
)

same_time_b = create_lifecycle_history_entry(
    event_id="b-event",
    workflow_id="sort-workflow",
    correlation_id="sort-correlation",
    from_state="READY",
    to_state="RUNNING",
    occurred_at="2026-08-17T03:00:00+00:00",
)

same_time_sorted = sort_lifecycle_history(
    (
        same_time_b,
        same_time_a,
    )
)

check(
    "Equal-time sorting uses deterministic event_id tie-break",
    (
        same_time_sorted[0].event_id
        == "a-event"
        and same_time_sorted[1].event_id
        == "b-event"
    ),
)


# ============================================================================
# 16. Entry immutability
# ============================================================================

entry_immutable = False

try:
    e1.event_id = "changed"
except Exception:
    entry_immutable = True

check(
    "LifecycleHistoryEntry is immutable",
    entry_immutable,
)


metadata_entry = create_lifecycle_history_entry(
    event_id="metadata-entry",
    workflow_id="metadata-workflow",
    correlation_id="metadata-correlation",
    from_state="CREATED",
    to_state="READY",
    occurred_at="2026-08-17T04:00:00+00:00",
    metadata={
        "nested": {
            "values": [
                "one",
                "two",
            ]
        }
    },
)

metadata_immutable = False

try:
    metadata_entry.metadata[
        "nested"
    ][
        "values"
    ][0] = "changed"
except Exception:
    metadata_immutable = True

check(
    "Entry metadata is deeply immutable",
    metadata_immutable,
)


entry_mapping = metadata_entry.to_dict()

mapping_immutable = False

try:
    entry_mapping["event_id"] = "changed"
except Exception:
    mapping_immutable = True

check(
    "LifecycleHistoryEntry to_dict result immutable",
    mapping_immutable,
)


# ============================================================================
# 17. Snapshot
# ============================================================================

snapshot = lifecycle_history_snapshot(
    valid_chain
)

check(
    "Lifecycle history snapshot immutable mapping",
    isinstance(
        snapshot,
        MappingProxyType,
    ),
)


snapshot_mutation = False

try:
    snapshot[
        "history_version"
    ] = "changed"
except Exception:
    snapshot_mutation = True

check(
    "Lifecycle history snapshot mutation blocked",
    snapshot_mutation,
)


# ============================================================================
# 18. Architecture explanation
# ============================================================================

explanation = explain_lifecycle_history_v3_3()

check(
    "Lifecycle history explanation immutable",
    isinstance(
        explanation,
        MappingProxyType,
    ),
)

future = explanation[
    "future_authority"
]

check(
    "future_authority is MappingProxyType",
    isinstance(
        future,
        MappingProxyType,
    ),
)

check(
    "future_authority 3.4 exact",
    future[
        "3.4"
    ]
    == "Terminal-State Protection",
)

check(
    "future_authority 8.0 exact",
    future[
        "8.0"
    ]
    == "Workflow State Persistence",
)

check(
    "future_authority 9.0 exact",
    future[
        "9.0"
    ]
    == "Coordination Recovery",
)

check(
    "future_authority 10.5 exact",
    future[
        "10.5"
    ]
    == "Audit Trail",
)


future_mutation = False

try:
    future[
        "3.4"
    ] = "MUTATED"
except Exception:
    future_mutation = True

check(
    "future_authority nested mutation blocked",
    future_mutation,
)


# ============================================================================
# 19. Determinism
# ============================================================================

explanation_again = explain_lifecycle_history_v3_3()

check(
    "Repeated architecture explanation deterministic",
    dict(
        explanation_again
    )
    == dict(
        explanation
    ),
)


snapshot_again = lifecycle_history_snapshot(
    valid_chain
)

check(
    "Repeated lifecycle snapshot deterministic",
    dict(
        snapshot_again
    )
    == dict(
        snapshot
    ),
)


# ============================================================================
# 20. Static authority boundary
# ============================================================================

backend_imports = []

if tree is not None:

    for node in ast.walk(tree):

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


allowed_imports = {
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
    "3.3 backend imports remain limited to frozen 3.1/3.2",
    set(
        backend_imports
    ).issubset(
        allowed_imports
    ),
    repr(
        backend_imports
    ),
)


forbidden_fragments = (
    "backend.server.runtime",
    "workflow_registry",
    "coordinator_registry",
    "registration_validation",
    "version_management",
    "persistence",
    "checkpoint",
    "recovery",
)

bad_imports = [
    item
    for item
    in backend_imports
    if any(
        fragment in item
        for fragment
        in forbidden_fragments
    )
]

check(
    "3.3 has no Runtime/registry/persistence/recovery imports",
    not bad_imports,
    repr(
        bad_imports
    ),
)


# ============================================================================
# 21. No generated IDs / timestamps / execution behavior
# ============================================================================

forbidden_calls = {
    "uuid4",
    "uuid1",
    "now",
    "utcnow",
    "dispatch",
    "enqueue",
    "execute",
    "commit",
    "save",
}

violations = []

if tree is not None:

    for node in ast.walk(tree):

        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        func = node.func

        if isinstance(
            func,
            ast.Name,
        ):
            name = func.id

        elif isinstance(
            func,
            ast.Attribute,
        ):
            name = func.attr

        else:
            continue

        if name in forbidden_calls:
            violations.append(
                name
            )


check(
    "3.3 generates no IDs/timestamps and performs no execution",
    not violations,
    repr(
        violations
    ),
)


# ============================================================================
# 22. New Phase 3.3 candidate SHA
# ============================================================================

phase_33_sha = sha256_file(
    PHASE_33
)

print()
print(
    "NEW PHASE 3.3 SHA256 CANDIDATE:"
)
print(
    phase_33_sha
)


# ============================================================================
# FINAL
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


report_lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 3.3 — LIFECYCLE HISTORY FINAL RE-CERTIFICATION",
    "=" * 96,
    "",
    (
        "Lifecycle History Version: "
        + LIFECYCLE_HISTORY_VERSION
    ),
    (
        "Lifecycle History Schema: "
        + LIFECYCLE_HISTORY_SCHEMA_VERSION
    ),
    "",
    (
        "Phase 3.1 SHA256: "
        + actual_31
    ),
    (
        "Phase 3.2 SHA256: "
        + actual_32
    ),
    (
        "Phase 3.3 SHA256: "
        + phase_33_sha
    ),
    "",
    f"Checks: {len(checks)}",
    f"Passed: {passed}",
    f"Failed: {failed}",
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

    report_lines.append(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if detail:
        report_lines.append(
            f"    {detail}"
        )


REPORT.write_text(
    "\n".join(
        report_lines
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 96)
print("PHASE 3.3 FINAL RE-CERTIFICATION RESULT")
print("=" * 96)
print(
    "Checks:",
    len(checks),
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
    "STATUS:",
    (
        "CERTIFICATION PASSED"
        if failed == 0
        else "CERTIFICATION FAILED"
    ),
)
print(
    "REPORT:",
    REPORT.name,
)
print("=" * 96)


raise SystemExit(
    0
    if failed == 0
    else 1
)

