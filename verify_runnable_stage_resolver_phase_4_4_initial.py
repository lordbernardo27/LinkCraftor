from __future__ import annotations

import ast
import hashlib
import importlib
from dataclasses import fields
from pathlib import Path
from types import MappingProxyType

from backend.server.coordination.dependency_planning.dependency_graph import (
    DEPENDENCY_GRAPH_VERSION,
    create_dependency_graph,
)

from backend.server.coordination.dependency_planning.dependency_validation import (
    DEPENDENCY_VALIDATION_VERSION,
    DependencyGraphValidationFailedError,
)

from backend.server.coordination.dependency_planning.cycle_detection import (
    CYCLE_DETECTION_VERSION,
    CyclicDependencyGraphError,
)

from backend.server.coordination.dependency_planning.runnable_stage_resolver import (
    RUNNABLE_STAGE_RESOLVER_VERSION,
    RUNNABLE_STAGE_RESOLVER_SCHEMA_VERSION,
    RUNNABLE_STAGE_STATE_FIELD_COUNT,
    STAGE_RUNNABILITY_EVIDENCE_FIELD_COUNT,
    RUNNABLE_STAGE_RESOLUTION_FIELD_COUNT,
    RunnableStageResolverError,
    InvalidRunnableStageStateError,
    WorkflowGraphIdentityMismatchError,
    RunnableStageState,
    StageRunnabilityEvidence,
    RunnableStageResolution,
    create_runnable_stage_state,
    resolve_runnable_stages,
    runnable_stage_resolution_snapshot,
    explain_runnable_stage_resolver_v4_4,
)


ROOT = Path.cwd()

PHASE_41 = ROOT / (
    "backend/server/coordination/"
    "dependency_planning/dependency_graph.py"
)

PHASE_42 = ROOT / (
    "backend/server/coordination/"
    "dependency_planning/dependency_validation.py"
)

PHASE_43 = ROOT / (
    "backend/server/coordination/"
    "dependency_planning/cycle_detection.py"
)

PHASE_44 = ROOT / (
    "backend/server/coordination/"
    "dependency_planning/runnable_stage_resolver.py"
)

REPORT = ROOT / (
    "runnable_stage_resolver_phase_4_4_initial_verification.txt"
)


EXPECTED_41_SHA = (
    "4F6BA62D011C31D9D851FBBABC37C12B"
    "7DDAA1FD9A91E34788EBCE25741A1F70"
)

EXPECTED_42_SHA = (
    "1D053C0036EA9F7A8AEDFAFC36F6EB82"
    "A681EDC7EF206409E9FFB8C7F212852D"
)

EXPECTED_43_SHA = (
    "E77BF605724F991E85C7FE2E5329051E"
    "16ECB2F30ACDAEA8AA40A2FD47487CEA"
)

EXPECTED_44_CANDIDATE_SHA = (
    "2779D432A2F3337F3557C61664499669"
    "CC852773AB74447297E98D6188289483"
)


checks = []


def check(name, condition, detail=""):
    ok = bool(condition)
    checks.append((name, ok, detail))

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if detail:
        print(
            f"       {detail}"
        )


def expect_exception(
    name,
    exception_type,
    callable_,
):
    try:
        callable_()

    except exception_type:
        check(name, True)

    except Exception as exc:
        check(
            name,
            False,
            (
                f"unexpected {type(exc).__name__}: "
                f"{exc}"
            ),
        )

    else:
        check(
            name,
            False,
            "expected exception was not raised",
        )


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


print()
print("=" * 104)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 4.4 — RUNNABLE STAGE RESOLVER INITIAL VERIFICATION")
print("=" * 104)


# =============================================================================
# 1. Canonical file / syntax / import
# =============================================================================

check(
    "Canonical Phase 4.4 file exists",
    PHASE_44.exists(),
    str(
        PHASE_44.relative_to(ROOT)
    ),
)

source = PHASE_44.read_text(
    encoding="utf-8-sig"
)

try:
    tree = ast.parse(
        source
    )
    syntax_ok = True

except SyntaxError:
    tree = None
    syntax_ok = False

check(
    "Phase 4.4 Python syntax parses",
    syntax_ok,
)

try:
    importlib.import_module(
        "backend.server.coordination."
        "dependency_planning.runnable_stage_resolver"
    )
    import_ok = True
    import_detail = ""

except Exception as exc:
    import_ok = False
    import_detail = repr(exc)

check(
    "Phase 4.4 module imports successfully",
    import_ok,
    import_detail,
)


# =============================================================================
# 2. Frozen upstream integrity
# =============================================================================

actual_41_sha = sha256(PHASE_41)
actual_42_sha = sha256(PHASE_42)
actual_43_sha = sha256(PHASE_43)
actual_44_sha = sha256(PHASE_44)

check(
    "Frozen Phase 4.1 SHA exact",
    actual_41_sha == EXPECTED_41_SHA,
    actual_41_sha,
)

check(
    "Frozen Phase 4.2 SHA exact",
    actual_42_sha == EXPECTED_42_SHA,
    actual_42_sha,
)

check(
    "Frozen Phase 4.3 SHA exact",
    actual_43_sha == EXPECTED_43_SHA,
    actual_43_sha,
)

check(
    "Phase 4.4 candidate SHA unchanged",
    actual_44_sha == EXPECTED_44_CANDIDATE_SHA,
    actual_44_sha,
)


# =============================================================================
# 3. Canonical identity
# =============================================================================

check(
    "Resolver version exact",
    RUNNABLE_STAGE_RESOLVER_VERSION
    == "runnable_stage_resolver_v4.4.0",
)

check(
    "Resolver schema exact",
    RUNNABLE_STAGE_RESOLVER_SCHEMA_VERSION
    == "runnable_stage_resolver_schema_v1",
)

check(
    "RunnableStageState field-count constant exact",
    RUNNABLE_STAGE_STATE_FIELD_COUNT == 6,
)

check(
    "StageRunnabilityEvidence field-count constant exact",
    STAGE_RUNNABILITY_EVIDENCE_FIELD_COUNT == 6,
)

check(
    "RunnableStageResolution field-count constant exact",
    RUNNABLE_STAGE_RESOLUTION_FIELD_COUNT == 8,
)


# =============================================================================
# 4. Exact dataclass contracts
# =============================================================================

state_fields = tuple(
    field.name
    for field
    in fields(RunnableStageState)
)

evidence_fields = tuple(
    field.name
    for field
    in fields(StageRunnabilityEvidence)
)

resolution_fields = tuple(
    field.name
    for field
    in fields(RunnableStageResolution)
)

check(
    "RunnableStageState field count exact",
    len(state_fields) == 6,
)

check(
    "RunnableStageState field order exact",
    state_fields == (
        "workflow_id",
        "current_stage_id",
        "completed_stage_ids",
        "pending_stage_ids",
        "failed_stage_ids",
        "skipped_stage_ids",
    ),
)

check(
    "StageRunnabilityEvidence field count exact",
    len(evidence_fields) == 6,
)

check(
    "StageRunnabilityEvidence field order exact",
    evidence_fields == (
        "stage_id",
        "is_runnable",
        "prerequisite_stage_ids",
        "satisfied_prerequisite_stage_ids",
        "unsatisfied_prerequisite_stage_ids",
        "reason",
    ),
)

check(
    "RunnableStageResolution field count exact",
    len(resolution_fields) == 8,
)

check(
    "RunnableStageResolution field order exact",
    resolution_fields == (
        "workflow_id",
        "runnable_stage_ids",
        "blocked_stage_ids",
        "untracked_stage_ids",
        "evidence",
        "graph_version",
        "cycle_detection_version",
        "resolver_version",
    ),
)


# =============================================================================
# 5. Workflow ID validation
# =============================================================================

for label, value in (
    ("None", None),
    ("integer", 42),
    ("empty", ""),
    ("leading whitespace", " workflow"),
    ("trailing whitespace", "workflow "),
):
    expect_exception(
        f"Invalid workflow_id rejected: {label}",
        InvalidRunnableStageStateError,
        lambda value=value: create_runnable_stage_state(
            workflow_id=value
        ),
    )


# =============================================================================
# 6. Stage ID validation
# =============================================================================

expect_exception(
    "Non-string stage ID rejected",
    InvalidRunnableStageStateError,
    lambda: create_runnable_stage_state(
        workflow_id="wf",
        pending_stage_ids=(1,),
    ),
)

expect_exception(
    "Empty stage ID rejected",
    InvalidRunnableStageStateError,
    lambda: create_runnable_stage_state(
        workflow_id="wf",
        pending_stage_ids=("",),
    ),
)

expect_exception(
    "Whitespace stage ID rejected",
    InvalidRunnableStageStateError,
    lambda: create_runnable_stage_state(
        workflow_id="wf",
        pending_stage_ids=(" a",),
    ),
)

expect_exception(
    "Invalid stage collection rejected",
    InvalidRunnableStageStateError,
    lambda: create_runnable_stage_state(
        workflow_id="wf",
        pending_stage_ids="a",
    ),
)


# =============================================================================
# 7. Canonicalization / dedupe / lexical order
# =============================================================================

canonical_state = create_runnable_stage_state(
    workflow_id="canonical",
    completed_stage_ids=(
        "z",
        "a",
        "a",
        "m",
    ),
    pending_stage_ids=(
        "p3",
        "p1",
        "p2",
        "p1",
    ),
    failed_stage_ids=(
        "f2",
        "f1",
        "f2",
    ),
    skipped_stage_ids=(
        "s2",
        "s1",
        "s2",
    ),
)

check(
    "Completed stages canonicalized",
    canonical_state.completed_stage_ids
    == (
        "a",
        "m",
        "z",
    ),
)

check(
    "Pending stages canonicalized",
    canonical_state.pending_stage_ids
    == (
        "p1",
        "p2",
        "p3",
    ),
)

check(
    "Failed stages canonicalized",
    canonical_state.failed_stage_ids
    == (
        "f1",
        "f2",
    ),
)

check(
    "Skipped stages canonicalized",
    canonical_state.skipped_stage_ids
    == (
        "s1",
        "s2",
    ),
)


# =============================================================================
# 8. State collection overlap protection
# =============================================================================

overlap_cases = (
    (
        "completed/pending",
        dict(
            completed_stage_ids=("a",),
            pending_stage_ids=("a",),
        ),
    ),
    (
        "completed/failed",
        dict(
            completed_stage_ids=("a",),
            failed_stage_ids=("a",),
        ),
    ),
    (
        "completed/skipped",
        dict(
            completed_stage_ids=("a",),
            skipped_stage_ids=("a",),
        ),
    ),
    (
        "pending/failed",
        dict(
            pending_stage_ids=("a",),
            failed_stage_ids=("a",),
        ),
    ),
    (
        "pending/skipped",
        dict(
            pending_stage_ids=("a",),
            skipped_stage_ids=("a",),
        ),
    ),
    (
        "failed/skipped",
        dict(
            failed_stage_ids=("a",),
            skipped_stage_ids=("a",),
        ),
    ),
)

for label, kwargs in overlap_cases:
    expect_exception(
        f"Overlapping state rejected: {label}",
        InvalidRunnableStageStateError,
        lambda kwargs=kwargs: create_runnable_stage_state(
            workflow_id="overlap",
            **kwargs,
        ),
    )


# =============================================================================
# 9. Empty graph / empty state
# =============================================================================

empty_graph = create_dependency_graph(
    workflow_id="empty"
)

empty_state = create_runnable_stage_state(
    workflow_id="empty"
)

empty_result = resolve_runnable_stages(
    empty_graph,
    empty_state,
)

check(
    "Empty graph has no runnable stages",
    empty_result.runnable_stage_ids == (),
)

check(
    "Empty graph has no blocked stages",
    empty_result.blocked_stage_ids == (),
)

check(
    "Empty graph has no untracked stages",
    empty_result.untracked_stage_ids == (),
)

check(
    "Empty graph has no evidence",
    empty_result.evidence == (),
)


# =============================================================================
# 10. Isolated nodes
# =============================================================================

isolated_graph = create_dependency_graph(
    workflow_id="isolated",
    node_ids=(
        "c",
        "a",
        "b",
    ),
)

isolated_state = create_runnable_stage_state(
    workflow_id="isolated",
    pending_stage_ids=(
        "c",
        "a",
        "b",
    ),
)

isolated_result = resolve_runnable_stages(
    isolated_graph,
    isolated_state,
)

check(
    "All pending isolated nodes runnable",
    isolated_result.runnable_stage_ids
    == (
        "a",
        "b",
        "c",
    ),
)

check(
    "Isolated nodes produce no blocked stages",
    isolated_result.blocked_stage_ids == (),
)

check(
    "Isolated result ordering lexical",
    isolated_result.runnable_stage_ids
    == tuple(
        sorted(
            isolated_result.runnable_stage_ids
        )
    ),
)


# =============================================================================
# 11. Linear progression
# =============================================================================

chain_graph = create_dependency_graph(
    workflow_id="chain",
    edges=(
        ("a", "b"),
        ("b", "c"),
        ("c", "d"),
    ),
)

chain_initial = create_runnable_stage_state(
    workflow_id="chain",
    pending_stage_ids=(
        "a",
        "b",
        "c",
        "d",
    ),
)

chain_initial_result = resolve_runnable_stages(
    chain_graph,
    chain_initial,
)

check(
    "Chain initially exposes root only",
    chain_initial_result.runnable_stage_ids
    == ("a",),
)

check(
    "Chain initially blocks descendants",
    chain_initial_result.blocked_stage_ids
    == (
        "b",
        "c",
        "d",
    ),
)


chain_after_a = create_runnable_stage_state(
    workflow_id="chain",
    completed_stage_ids=("a",),
    pending_stage_ids=(
        "b",
        "c",
        "d",
    ),
)

chain_after_a_result = resolve_runnable_stages(
    chain_graph,
    chain_after_a,
)

check(
    "Chain exposes B after A completes",
    chain_after_a_result.runnable_stage_ids
    == ("b",),
)


chain_after_ab = create_runnable_stage_state(
    workflow_id="chain",
    completed_stage_ids=(
        "a",
        "b",
    ),
    pending_stage_ids=(
        "c",
        "d",
    ),
)

chain_after_ab_result = resolve_runnable_stages(
    chain_graph,
    chain_after_ab,
)

check(
    "Chain exposes C after A+B complete",
    chain_after_ab_result.runnable_stage_ids
    == ("c",),
)


# =============================================================================
# 12. Parallel root stages
# =============================================================================

parallel_graph = create_dependency_graph(
    workflow_id="parallel",
    edges=(
        ("a", "join"),
        ("b", "join"),
        ("c", "join"),
    ),
)

parallel_initial = create_runnable_stage_state(
    workflow_id="parallel",
    pending_stage_ids=(
        "join",
        "c",
        "a",
        "b",
    ),
)

parallel_initial_result = resolve_runnable_stages(
    parallel_graph,
    parallel_initial,
)

check(
    "Parallel roots all runnable",
    parallel_initial_result.runnable_stage_ids
    == (
        "a",
        "b",
        "c",
    ),
)

check(
    "Join blocked initially",
    parallel_initial_result.blocked_stage_ids
    == (
        "join",
    ),
)


parallel_partial = create_runnable_stage_state(
    workflow_id="parallel",
    completed_stage_ids=(
        "a",
        "b",
    ),
    pending_stage_ids=(
        "c",
        "join",
    ),
)

parallel_partial_result = resolve_runnable_stages(
    parallel_graph,
    parallel_partial,
)

check(
    "Remaining root C runnable",
    parallel_partial_result.runnable_stage_ids
    == (
        "c",
    ),
)

check(
    "Join remains blocked with one incomplete prerequisite",
    "join"
    in parallel_partial_result.blocked_stage_ids,
)


parallel_complete = create_runnable_stage_state(
    workflow_id="parallel",
    completed_stage_ids=(
        "a",
        "b",
        "c",
    ),
    pending_stage_ids=(
        "join",
    ),
)

parallel_complete_result = resolve_runnable_stages(
    parallel_graph,
    parallel_complete,
)

check(
    "Join runnable when all prerequisites complete",
    parallel_complete_result.runnable_stage_ids
    == (
        "join",
    ),
)


# =============================================================================
# 13. Current stage exclusion
# =============================================================================

current_graph = create_dependency_graph(
    workflow_id="current",
    node_ids=(
        "a",
        "b",
        "c",
    ),
)

current_state = create_runnable_stage_state(
    workflow_id="current",
    current_stage_id="b",
    pending_stage_ids=(
        "a",
        "b",
        "c",
    ),
)

current_result = resolve_runnable_stages(
    current_graph,
    current_state,
)

check(
    "Current stage excluded from runnable IDs",
    current_result.runnable_stage_ids
    == (
        "a",
        "c",
    ),
)

check(
    "Current pending stage appears blocked",
    current_result.blocked_stage_ids
    == (
        "b",
    ),
)

current_evidence = next(
    item
    for item
    in current_result.evidence
    if item.stage_id == "b"
)

check(
    "Current stage reason exact",
    current_evidence.reason
    == "current_stage_not_runnable",
)


# =============================================================================
# 14. Failed prerequisite semantics
# =============================================================================

failed_graph = create_dependency_graph(
    workflow_id="failed",
    edges=(
        ("a", "b"),
    ),
)

failed_state = create_runnable_stage_state(
    workflow_id="failed",
    failed_stage_ids=("a",),
    pending_stage_ids=("b",),
)

failed_result = resolve_runnable_stages(
    failed_graph,
    failed_state,
)

check(
    "Failed prerequisite blocks dependent",
    failed_result.runnable_stage_ids == (),
)

check(
    "Failed prerequisite dependent in blocked IDs",
    failed_result.blocked_stage_ids
    == ("b",),
)

check(
    "Failed prerequisite appears unsatisfied",
    failed_result.evidence[0]
    .unsatisfied_prerequisite_stage_ids
    == ("a",),
)


# =============================================================================
# 15. Skipped prerequisite semantics
# =============================================================================

skipped_state = create_runnable_stage_state(
    workflow_id="failed",
    skipped_stage_ids=("a",),
    pending_stage_ids=("b",),
)

skipped_result = resolve_runnable_stages(
    failed_graph,
    skipped_state,
)

check(
    "Skipped prerequisite blocks dependent in base 4.4",
    skipped_result.runnable_stage_ids == (),
)

check(
    "Skipped prerequisite remains unsatisfied",
    skipped_result.evidence[0]
    .unsatisfied_prerequisite_stage_ids
    == ("a",),
)


# =============================================================================
# 16. Completed prerequisite semantics
# =============================================================================

completed_state = create_runnable_stage_state(
    workflow_id="failed",
    completed_stage_ids=("a",),
    pending_stage_ids=("b",),
)

completed_result = resolve_runnable_stages(
    failed_graph,
    completed_state,
)

check(
    "Completed prerequisite releases dependent",
    completed_result.runnable_stage_ids
    == ("b",),
)

check(
    "Completed prerequisite appears satisfied",
    completed_result.evidence[0]
    .satisfied_prerequisite_stage_ids
    == ("a",),
)

check(
    "Completed-dependent reason exact",
    completed_result.evidence[0].reason
    == "all_prerequisites_completed",
)


# =============================================================================
# 17. Evidence for roots
# =============================================================================

root_evidence = next(
    item
    for item
    in chain_initial_result.evidence
    if item.stage_id == "a"
)

check(
    "Root evidence has no prerequisites",
    root_evidence.prerequisite_stage_ids == (),
)

check(
    "Root evidence has no unsatisfied prerequisites",
    root_evidence.unsatisfied_prerequisite_stage_ids
    == (),
)

check(
    "Root reason exact",
    root_evidence.reason
    == "no_prerequisites",
)


# =============================================================================
# 18. Workflow identity protection
# =============================================================================

expect_exception(
    "Workflow/graph identity mismatch rejected",
    WorkflowGraphIdentityMismatchError,
    lambda: resolve_runnable_stages(
        chain_graph,
        create_runnable_stage_state(
            workflow_id="different",
            pending_stage_ids=("a",),
        ),
    ),
)


# =============================================================================
# 19. State references outside graph
# =============================================================================

for label, kwargs in (
    (
        "completed",
        dict(
            completed_stage_ids=("outside",),
        ),
    ),
    (
        "pending",
        dict(
            pending_stage_ids=("outside",),
        ),
    ),
    (
        "failed",
        dict(
            failed_stage_ids=("outside",),
        ),
    ),
    (
        "skipped",
        dict(
            skipped_stage_ids=("outside",),
        ),
    ),
    (
        "current",
        dict(
            current_stage_id="outside",
        ),
    ),
):
    expect_exception(
        f"Out-of-graph state rejected: {label}",
        InvalidRunnableStageStateError,
        lambda kwargs=kwargs: resolve_runnable_stages(
            chain_graph,
            create_runnable_stage_state(
                workflow_id="chain",
                **kwargs,
            ),
        ),
    )


# =============================================================================
# 20. Cyclic graph protection
# =============================================================================

cyclic_graph = create_dependency_graph(
    workflow_id="cyclic",
    edges=(
        ("a", "b"),
        ("b", "a"),
    ),
)

cyclic_state = create_runnable_stage_state(
    workflow_id="cyclic",
    pending_stage_ids=(
        "a",
        "b",
    ),
)

expect_exception(
    "Cyclic graph rejected before runnability",
    CyclicDependencyGraphError,
    lambda: resolve_runnable_stages(
        cyclic_graph,
        cyclic_state,
    ),
)


# =============================================================================
# 21. Self-dependency protection still comes from upstream validation
# =============================================================================

self_graph = create_dependency_graph(
    workflow_id="self",
    edges=(
        ("a", "a"),
    ),
)

self_state = create_runnable_stage_state(
    workflow_id="self",
    pending_stage_ids=("a",),
)

expect_exception(
    "Self-dependency rejected by frozen upstream validation",
    DependencyGraphValidationFailedError,
    lambda: resolve_runnable_stages(
        self_graph,
        self_state,
    ),
)


# =============================================================================
# 22. Untracked graph nodes
# =============================================================================

untracked_graph = create_dependency_graph(
    workflow_id="untracked",
    node_ids=(
        "d",
        "a",
        "c",
        "b",
    ),
)

untracked_state = create_runnable_stage_state(
    workflow_id="untracked",
    completed_stage_ids=("a",),
    pending_stage_ids=("b",),
)

untracked_result = resolve_runnable_stages(
    untracked_graph,
    untracked_state,
)

check(
    "Untracked nodes exact",
    untracked_result.untracked_stage_ids
    == (
        "c",
        "d",
    ),
)

check(
    "Untracked nodes are not runnable",
    not any(
        stage_id
        in untracked_result.runnable_stage_ids
        for stage_id
        in untracked_result.untracked_stage_ids
    ),
)

check(
    "Evidence contains pending stages only",
    tuple(
        item.stage_id
        for item
        in untracked_result.evidence
    )
    == (
        "b",
    ),
)


# =============================================================================
# 23. Large runnability topology
# =============================================================================

large_edges = tuple(
    (
        f"s{i:03d}",
        f"s{i + 1:03d}",
    )
    for i in range(99)
)

large_graph = create_dependency_graph(
    workflow_id="large",
    edges=large_edges,
)

large_initial_state = create_runnable_stage_state(
    workflow_id="large",
    pending_stage_ids=tuple(
        f"s{i:03d}"
        for i in range(100)
    ),
)

large_initial_result = resolve_runnable_stages(
    large_graph,
    large_initial_state,
)

check(
    "100-stage chain initial root exact",
    large_initial_result.runnable_stage_ids
    == ("s000",),
)

check(
    "100-stage chain initial blocked count exact",
    len(
        large_initial_result.blocked_stage_ids
    ) == 99,
)


large_mid_state = create_runnable_stage_state(
    workflow_id="large",
    completed_stage_ids=tuple(
        f"s{i:03d}"
        for i in range(50)
    ),
    pending_stage_ids=tuple(
        f"s{i:03d}"
        for i in range(50, 100)
    ),
)

large_mid_result = resolve_runnable_stages(
    large_graph,
    large_mid_state,
)

check(
    "100-stage chain midpoint runnable exact",
    large_mid_result.runnable_stage_ids
    == ("s050",),
)


# =============================================================================
# 24. State immutability
# =============================================================================

blocked = False

try:
    canonical_state.pending_stage_ids = ()

except Exception:
    blocked = True

check(
    "RunnableStageState immutable",
    blocked,
)

state_dict = canonical_state.to_dict()

check(
    "RunnableStageState to_dict immutable",
    isinstance(
        state_dict,
        MappingProxyType,
    ),
)

blocked = False

try:
    state_dict[
        "pending_stage_ids"
    ] = ()

except Exception:
    blocked = True

check(
    "RunnableStageState to_dict mutation blocked",
    blocked,
)


# =============================================================================
# 25. Evidence immutability
# =============================================================================

sample_evidence = chain_initial_result.evidence[1]

blocked = False

try:
    sample_evidence.reason = "changed"

except Exception:
    blocked = True

check(
    "StageRunnabilityEvidence immutable",
    blocked,
)

evidence_dict = sample_evidence.to_dict()

check(
    "StageRunnabilityEvidence to_dict immutable",
    isinstance(
        evidence_dict,
        MappingProxyType,
    ),
)

blocked = False

try:
    evidence_dict[
        "reason"
    ] = "changed"

except Exception:
    blocked = True

check(
    "StageRunnabilityEvidence to_dict mutation blocked",
    blocked,
)


# =============================================================================
# 26. Resolution deep immutability
# =============================================================================

blocked = False

try:
    chain_initial_result.runnable_stage_ids = ()

except Exception:
    blocked = True

check(
    "RunnableStageResolution immutable",
    blocked,
)

resolution_dict = (
    chain_initial_result.to_dict()
)

check(
    "RunnableStageResolution to_dict immutable",
    isinstance(
        resolution_dict,
        MappingProxyType,
    ),
)

check(
    "Resolution evidence serialization tuple",
    isinstance(
        resolution_dict["evidence"],
        tuple,
    ),
)

check(
    "Resolution nested evidence mapping immutable",
    isinstance(
        resolution_dict["evidence"][0],
        MappingProxyType,
    ),
)

blocked = False

try:
    resolution_dict[
        "evidence"
    ][0][
        "reason"
    ] = "changed"

except Exception:
    blocked = True

check(
    "RunnableStageResolution deep mutation blocked",
    blocked,
)


# =============================================================================
# 27. Snapshot
# =============================================================================

snapshot = runnable_stage_resolution_snapshot(
    parallel_graph,
    parallel_initial,
)

check(
    "Snapshot MappingProxyType",
    isinstance(
        snapshot,
        MappingProxyType,
    ),
)

check(
    "Snapshot resolver version exact",
    snapshot[
        "resolver_version"
    ]
    == RUNNABLE_STAGE_RESOLVER_VERSION,
)

check(
    "Snapshot schema exact",
    snapshot[
        "schema_version"
    ]
    == RUNNABLE_STAGE_RESOLVER_SCHEMA_VERSION,
)

check(
    "Snapshot workflow ID exact",
    snapshot[
        "workflow_id"
    ]
    == "parallel",
)

check(
    "Snapshot graph version exact",
    snapshot[
        "graph_version"
    ]
    == DEPENDENCY_GRAPH_VERSION,
)

check(
    "Snapshot cycle version exact",
    snapshot[
        "cycle_detection_version"
    ]
    == CYCLE_DETECTION_VERSION,
)

check(
    "Snapshot runnable IDs exact",
    snapshot[
        "runnable_stage_ids"
    ]
    == (
        "a",
        "b",
        "c",
    ),
)

check(
    "Snapshot blocked IDs exact",
    snapshot[
        "blocked_stage_ids"
    ]
    == (
        "join",
    ),
)

check(
    "Snapshot evidence immutable tuple",
    isinstance(
        snapshot["evidence"],
        tuple,
    ),
)

check(
    "Snapshot nested evidence immutable",
    isinstance(
        snapshot["evidence"][0],
        MappingProxyType,
    ),
)

blocked = False

try:
    snapshot[
        "evidence"
    ][0][
        "reason"
    ] = "changed"

except Exception:
    blocked = True

check(
    "Snapshot deep mutation blocked",
    blocked,
)


# =============================================================================
# 28. Architecture evidence
# =============================================================================

architecture = explain_runnable_stage_resolver_v4_4()

check(
    "Architecture MappingProxyType",
    isinstance(
        architecture,
        MappingProxyType,
    ),
)

check(
    "Architecture phase exact",
    architecture["phase"] == "4.4",
)

check(
    "Architecture component exact",
    architecture["component"]
    == "Runnable Stage Resolver",
)

check(
    "Architecture version exact",
    architecture["version"]
    == RUNNABLE_STAGE_RESOLVER_VERSION,
)

check(
    "Architecture schema exact",
    architecture["schema_version"]
    == RUNNABLE_STAGE_RESOLVER_SCHEMA_VERSION,
)

check(
    "Topology authority exact",
    architecture["topology_authority"]
    == "Phase 4.1 DependencyGraph",
)

check(
    "Validation precondition exact",
    architecture["validation_precondition"]
    == "Phase 4.2 Dependency Validation",
)

check(
    "Acyclic precondition exact",
    architecture["acyclic_precondition"]
    == "Phase 4.3 Cycle Detection",
)

check(
    "Workflow progress authority exact",
    architecture["workflow_progress_authority"]
    == (
        "immutable projection of frozen "
        "Universal Workflow Contract"
    ),
)


upstream = architecture[
    "upstream_versions"
]

check(
    "Upstream versions immutable",
    isinstance(
        upstream,
        MappingProxyType,
    ),
)

check(
    "4.1 upstream version exact",
    upstream["4.1"]
    == DEPENDENCY_GRAPH_VERSION,
)

check(
    "4.2 upstream version exact",
    upstream["4.2"]
    == DEPENDENCY_VALIDATION_VERSION,
)

check(
    "4.3 upstream version exact",
    upstream["4.3"]
    == CYCLE_DETECTION_VERSION,
)


candidate_semantics = architecture[
    "candidate_semantics"
]

check(
    "Candidate semantics immutable",
    isinstance(
        candidate_semantics,
        MappingProxyType,
    ),
)

check(
    "Candidate universe exact",
    candidate_semantics[
        "candidate_universe"
    ]
    == "pending stages within graph.node_ids",
)

check(
    "Completed stage not runnable",
    candidate_semantics[
        "completed_stage"
    ] == "not runnable",
)

check(
    "Failed stage not runnable",
    candidate_semantics[
        "failed_stage"
    ] == "not runnable",
)

check(
    "Skipped stage not runnable",
    candidate_semantics[
        "skipped_stage"
    ] == "not runnable",
)

check(
    "Current stage not runnable",
    candidate_semantics[
        "current_stage"
    ] == "not runnable",
)

check(
    "Untracked graph node not runnable",
    candidate_semantics[
        "untracked_graph_node"
    ] == "not runnable",
)

check(
    "Root candidate semantics exact",
    candidate_semantics[
        "root_stage"
    ]
    == "runnable when pending and not current",
)

check(
    "Isolated candidate semantics exact",
    candidate_semantics[
        "isolated_stage"
    ]
    == "runnable when pending and not current",
)


prerequisite_semantics = architecture[
    "prerequisite_semantics"
]

check(
    "Prerequisite semantics immutable",
    isinstance(
        prerequisite_semantics,
        MappingProxyType,
    ),
)

check(
    "Completed prerequisite satisfies",
    prerequisite_semantics[
        "completed"
    ] == "satisfied",
)

check(
    "Failed prerequisite unsatisfied",
    prerequisite_semantics[
        "failed"
    ] == "unsatisfied",
)

check(
    "Skipped prerequisite base semantics exact",
    prerequisite_semantics[
        "skipped"
    ]
    == (
        "unsatisfied in base Phase 4.4; "
        "advanced Skip Semantics belong to Phase 7.7"
    ),
)

check(
    "All prerequisites completed means runnable",
    prerequisite_semantics[
        "all_direct_prerequisites_completed"
    ] == "runnable",
)

check(
    "Any incomplete prerequisite means blocked",
    prerequisite_semantics[
        "any_direct_prerequisite_not_completed"
    ] == "blocked",
)


result_semantics = architecture[
    "result_semantics"
]

check(
    "Result semantics immutable",
    isinstance(
        result_semantics,
        MappingProxyType,
    ),
)

check(
    "Runnable IDs lexical",
    result_semantics[
        "runnable_stage_ids"
    ] == "lexically ordered",
)

check(
    "Blocked IDs lexical",
    result_semantics[
        "blocked_stage_ids"
    ] == "lexically ordered",
)

check(
    "Evidence per pending stage exact",
    result_semantics[
        "evidence"
    ] == "one entry per pending stage",
)

check(
    "Execution order absent",
    result_semantics[
        "execution_order"
    ] == "not produced",
)


future = architecture[
    "future_authority"
]

check(
    "Future authority immutable",
    isinstance(
        future,
        MappingProxyType,
    ),
)

check(
    "Future authority exact",
    dict(future)
    == {
        "4.5":
            "Execution Planner",
        "4.6":
            "Planning Certification",
        "7.7":
            "Skip Semantics",
    },
)


execution = architecture[
    "execution_properties"
]

check(
    "Execution properties immutable",
    isinstance(
        execution,
        MappingProxyType,
    ),
)

check(
    "4.4 read-only",
    execution[
        "read_only"
    ] is True,
)

check(
    "4.4 deterministic",
    execution[
        "deterministic"
    ] is True,
)

check(
    "4.4 side-effect free",
    execution[
        "side_effect_free"
    ] is True,
)

check(
    "4.4 graph mutation disabled",
    execution[
        "graph_mutation"
    ] is False,
)

check(
    "4.4 workflow mutation disabled",
    execution[
        "workflow_mutation"
    ] is False,
)

check(
    "4.4 Runtime execution disabled",
    execution[
        "runtime_execution"
    ] is False,
)

check(
    "4.4 persistence disabled",
    execution[
        "persistence"
    ] is False,
)


# =============================================================================
# 29. Determinism
# =============================================================================

check(
    "Repeated chain resolution deterministic",
    resolve_runnable_stages(
        chain_graph,
        chain_initial,
    )
    == chain_initial_result,
)

check(
    "Repeated parallel resolution deterministic",
    resolve_runnable_stages(
        parallel_graph,
        parallel_initial,
    )
    == parallel_initial_result,
)

check(
    "Repeated large resolution deterministic",
    resolve_runnable_stages(
        large_graph,
        large_mid_state,
    )
    == large_mid_result,
)

check(
    "Repeated snapshot deterministic",
    dict(
        runnable_stage_resolution_snapshot(
            parallel_graph,
            parallel_initial,
        )
    )
    == dict(snapshot),
)

check(
    "Repeated architecture deterministic",
    dict(
        explain_runnable_stage_resolver_v4_4()
    )
    == dict(architecture),
)


# =============================================================================
# 30. Static import boundary
# =============================================================================

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

            module = node.module or ""

            if module.startswith(
                "backend."
            ):
                backend_imports.append(
                    module
                )


allowed_backend_imports = {
    (
        "backend.server.coordination."
        "dependency_planning.dependency_graph"
    ),
    (
        "backend.server.coordination."
        "dependency_planning.dependency_validation"
    ),
    (
        "backend.server.coordination."
        "dependency_planning.cycle_detection"
    ),
}

check(
    "4.4 imports only frozen 4.1/4.2/4.3",
    set(
        backend_imports
    ).issubset(
        allowed_backend_imports
    ),
    repr(backend_imports),
)


# =============================================================================
# 31. No Runtime / planner / persistence authority
# =============================================================================

forbidden_calls = {
    "dispatch",
    "enqueue",
    "execute",
    "register",
    "register_workflow",
    "register_coordinator",
    "save",
    "commit",
    "checkpoint",
    "recover",
    "resume",
    "pause",
    "plan_execution",
    "create_execution_plan",
    "schedule_stage",
    "submit_job",
    "create_job",
}

bad_calls = []

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
            bad_calls.append(
                name
            )


check(
    "4.4 performs no Runtime/planning/persistence execution",
    not bad_calls,
    repr(bad_calls),
)


# =============================================================================
# 32. Public API boundary
# =============================================================================

public_names = []

if tree is not None:

    for node in tree.body:

        if isinstance(
            node,
            (
                ast.ClassDef,
                ast.FunctionDef,
            ),
        ):

            if not node.name.startswith(
                "_"
            ):
                public_names.append(
                    node.name
                )


forbidden_public_tokens = (
    "execution_plan",
    "schedule",
    "dispatch",
    "enqueue",
    "runtime",
    "persist",
    "recover",
)

check(
    "4.4 exposes no planning/Runtime/persistence API",
    not any(
        any(
            token in name.lower()
            for token
            in forbidden_public_tokens
        )
        for name
        in public_names
    ),
    repr(public_names),
)


# =============================================================================
# 33. Source authority assertions
# =============================================================================

source_assertions = (
    (
        "Source owns runnable-stage resolution",
        "deterministic runnable-stage resolution",
    ),
    (
        "Source owns blocked-stage prerequisite evidence",
        "blocked-stage prerequisite evidence",
    ),
    (
        "Source owns workflow/graph identity validation",
        "workflow/graph identity validation",
    ),
    (
        "Source states completed prerequisite satisfies",
        "COMPLETED satisfies a prerequisite",
    ),
    (
        "Source states failed prerequisite unsatisfied",
        "FAILED does not satisfy a prerequisite",
    ),
    (
        "Source states skipped prerequisite unsatisfied",
        "SKIPPED does not satisfy a prerequisite",
    ),
    (
        "Source reserves advanced skip semantics for 7.7",
        "Advanced skip semantics belong to Phase 7.7",
    ),
    (
        "Source defers graph construction to 4.1",
        "dependency graph construction (Phase 4.1)",
    ),
    (
        "Source defers semantic validation to 4.2",
        "dependency semantic validation (Phase 4.2)",
    ),
    (
        "Source defers cycle detection to 4.3",
        "cycle detection (Phase 4.3)",
    ),
    (
        "Source defers execution planning to 4.5",
        "execution ordering/planning (Phase 4.5)",
    ),
    (
        "Source defers planning certification to 4.6",
        "planning certification (Phase 4.6)",
    ),
    (
        "Source excludes Runtime execution",
        "Runtime dispatch/execution (Phase 5)",
    ),
    (
        "Source excludes stage handoff",
        "stage handoff (Phase 6)",
    ),
    (
        "Source excludes advanced orchestration",
        "fan-out/fan-in or advanced skip policy (Phase 7)",
    ),
    (
        "Source excludes persistence",
        "persistence/checkpointing (Phase 8)",
    ),
    (
        "Source excludes recovery",
        "recovery policy (Phase 9)",
    ),
    (
        "Source explicitly says no execution order",
        "No execution order is produced.",
    ),
)

for name, marker in source_assertions:
    check(
        name,
        marker in source,
    )


# =============================================================================
# FINAL
# =============================================================================

passed = sum(
    1
    for _, ok, _
    in checks
    if ok
)

failed = len(checks) - passed


report_lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 4.4 — RUNNABLE STAGE RESOLVER INITIAL VERIFICATION",
    "=" * 104,
    "",
    (
        "Runnable Stage Resolver Version: "
        + RUNNABLE_STAGE_RESOLVER_VERSION
    ),
    (
        "Runnable Stage Resolver Schema: "
        + RUNNABLE_STAGE_RESOLVER_SCHEMA_VERSION
    ),
    "",
    (
        "Frozen Phase 4.1 SHA256: "
        + actual_41_sha
    ),
    (
        "Frozen Phase 4.2 SHA256: "
        + actual_42_sha
    ),
    (
        "Frozen Phase 4.3 SHA256: "
        + actual_43_sha
    ),
    (
        "Phase 4.4 SHA256: "
        + actual_44_sha
    ),
    "",
    f"Checks: {len(checks)}",
    f"Passed: {passed}",
    f"Failed: {failed}",
    "",
    (
        "STATUS: VERIFICATION PASSED"
        if failed == 0
        else "STATUS: VERIFICATION FAILED"
    ),
    "",
]


for name, ok, detail in checks:

    report_lines.append(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if detail:
        report_lines.append(
            "    " + detail
        )


REPORT.write_text(
    "\n".join(
        report_lines
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 104)
print("PHASE 4.4 INITIAL VERIFICATION RESULT")
print("=" * 104)
print("Checks:", len(checks))
print("Passed:", passed)
print("Failed:", failed)
print(
    "STATUS:",
    (
        "VERIFICATION PASSED"
        if failed == 0
        else "VERIFICATION FAILED"
    ),
)
print(
    "REPORT:",
    REPORT.name,
)
print("=" * 104)


raise SystemExit(
    0
    if failed == 0
    else 1
)
