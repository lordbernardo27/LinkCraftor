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
    "runnable_stage_resolver_phase_4_4_final_certification.txt"
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

EXPECTED_44_SHA = (
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
print("=" * 108)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 4.4 — RUNNABLE STAGE RESOLVER FINAL CERTIFICATION")
print("=" * 108)


# =============================================================================
# 1. Canonical files
# =============================================================================

for label, path in (
    ("Frozen Phase 4.1", PHASE_41),
    ("Frozen Phase 4.2", PHASE_42),
    ("Frozen Phase 4.3", PHASE_43),
    ("Canonical Phase 4.4", PHASE_44),
):
    check(
        f"{label} file exists",
        path.exists(),
        str(
            path.relative_to(ROOT)
        ),
    )


# =============================================================================
# 2. Frozen SHA integrity
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
    "Phase 4.4 SHA exact",
    actual_44_sha == EXPECTED_44_SHA,
    actual_44_sha,
)


# =============================================================================
# 3. Syntax / import
# =============================================================================

source = PHASE_44.read_text(
    encoding="utf-8-sig"
)

try:
    tree = ast.parse(source)
    syntax_ok = True

except SyntaxError:
    tree = None
    syntax_ok = False

check(
    "Phase 4.4 syntax parses",
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
# 4. Canonical identity
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
# 5. Exact dataclass contracts
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
    "RunnableStageState exact field contract",
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
    "StageRunnabilityEvidence exact field contract",
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
    "RunnableStageResolution exact field contract",
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
# 6. Workflow identity validation
# =============================================================================

for label, value in (
    ("None", None),
    ("integer", 1),
    ("float", 1.5),
    ("bytes", b"wf"),
    ("empty", ""),
    ("leading whitespace", " wf"),
    ("trailing whitespace", "wf "),
):
    expect_exception(
        f"Invalid workflow_id rejected: {label}",
        InvalidRunnableStageStateError,
        lambda value=value: create_runnable_stage_state(
            workflow_id=value
        ),
    )


# =============================================================================
# 7. Stage-ID validation
# =============================================================================

for label, value in (
    ("non-string", 1),
    ("empty", ""),
    ("leading whitespace", " a"),
    ("trailing whitespace", "a "),
):
    expect_exception(
        f"Invalid pending stage ID rejected: {label}",
        InvalidRunnableStageStateError,
        lambda value=value: create_runnable_stage_state(
            workflow_id="wf",
            pending_stage_ids=(value,),
        ),
    )


for label, value in (
    ("string", "a"),
    ("integer", 1),
    ("mapping", {"a": 1}),
):
    expect_exception(
        f"Invalid pending collection rejected: {label}",
        InvalidRunnableStageStateError,
        lambda value=value: create_runnable_stage_state(
            workflow_id="wf",
            pending_stage_ids=value,
        ),
    )


# =============================================================================
# 8. Canonicalization / deduplication
# =============================================================================

canonical_state = create_runnable_stage_state(
    workflow_id="canonical",
    current_stage_id="current",
    completed_stage_ids=(
        "z",
        "a",
        "m",
        "a",
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
        "f1",
    ),
    skipped_stage_ids=(
        "s2",
        "s1",
        "s2",
    ),
)

check(
    "Completed IDs lexical and unique",
    canonical_state.completed_stage_ids
    == (
        "a",
        "m",
        "z",
    ),
)

check(
    "Pending IDs lexical and unique",
    canonical_state.pending_stage_ids
    == (
        "p1",
        "p2",
        "p3",
    ),
)

check(
    "Failed IDs lexical and unique",
    canonical_state.failed_stage_ids
    == (
        "f1",
        "f2",
    ),
)

check(
    "Skipped IDs lexical and unique",
    canonical_state.skipped_stage_ids
    == (
        "s1",
        "s2",
    ),
)

check(
    "Current stage preserved exactly",
    canonical_state.current_stage_id
    == "current",
)


# =============================================================================
# 9. Cross-state disjointness
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
# 10. Empty graph
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
    "Empty graph runnable IDs empty",
    empty_result.runnable_stage_ids == (),
)

check(
    "Empty graph blocked IDs empty",
    empty_result.blocked_stage_ids == (),
)

check(
    "Empty graph untracked IDs empty",
    empty_result.untracked_stage_ids == (),
)

check(
    "Empty graph evidence empty",
    empty_result.evidence == (),
)


# =============================================================================
# 11. 100 isolated pending stages
# =============================================================================

isolated_ids = tuple(
    f"isolated-{i:03d}"
    for i in range(100)
)

isolated_graph = create_dependency_graph(
    workflow_id="isolated",
    node_ids=isolated_ids,
)

isolated_state = create_runnable_stage_state(
    workflow_id="isolated",
    pending_stage_ids=tuple(
        reversed(
            isolated_ids
        )
    ),
)

isolated_result = resolve_runnable_stages(
    isolated_graph,
    isolated_state,
)

check(
    "100 isolated pending stages all runnable",
    isolated_result.runnable_stage_ids
    == isolated_ids,
)

check(
    "100 isolated stages zero blocked",
    isolated_result.blocked_stage_ids == (),
)

check(
    "100 isolated stages evidence count exact",
    len(
        isolated_result.evidence
    ) == 100,
)


# =============================================================================
# 12. Large linear topology
# =============================================================================

chain_edges = tuple(
    (
        f"s{i:03d}",
        f"s{i + 1:03d}",
    )
    for i in range(199)
)

chain_graph = create_dependency_graph(
    workflow_id="chain",
    edges=chain_edges,
)

chain_initial_state = create_runnable_stage_state(
    workflow_id="chain",
    pending_stage_ids=tuple(
        f"s{i:03d}"
        for i in range(200)
    ),
)

chain_initial_result = resolve_runnable_stages(
    chain_graph,
    chain_initial_state,
)

check(
    "200-stage chain root exact",
    chain_initial_result.runnable_stage_ids
    == ("s000",),
)

check(
    "200-stage chain blocked count exact",
    len(
        chain_initial_result.blocked_stage_ids
    ) == 199,
)


chain_mid_state = create_runnable_stage_state(
    workflow_id="chain",
    completed_stage_ids=tuple(
        f"s{i:03d}"
        for i in range(125)
    ),
    pending_stage_ids=tuple(
        f"s{i:03d}"
        for i in range(125, 200)
    ),
)

chain_mid_result = resolve_runnable_stages(
    chain_graph,
    chain_mid_state,
)

check(
    "200-stage chain midpoint runnable exact",
    chain_mid_result.runnable_stage_ids
    == ("s125",),
)

check(
    "200-stage chain midpoint blocked count exact",
    len(
        chain_mid_result.blocked_stage_ids
    ) == 74,
)


# =============================================================================
# 13. Large parallel join
# =============================================================================

parallel_roots = tuple(
    f"root-{i:03d}"
    for i in range(50)
)

parallel_edges = tuple(
    (
        root,
        "join",
    )
    for root
    in parallel_roots
)

parallel_graph = create_dependency_graph(
    workflow_id="parallel",
    edges=parallel_edges,
)

parallel_initial = create_runnable_stage_state(
    workflow_id="parallel",
    pending_stage_ids=(
        "join",
        *parallel_roots,
    ),
)

parallel_initial_result = resolve_runnable_stages(
    parallel_graph,
    parallel_initial,
)

check(
    "50 parallel roots runnable",
    parallel_initial_result.runnable_stage_ids
    == parallel_roots,
)

check(
    "Large join initially blocked",
    parallel_initial_result.blocked_stage_ids
    == ("join",),
)


parallel_partial = create_runnable_stage_state(
    workflow_id="parallel",
    completed_stage_ids=parallel_roots[:49],
    pending_stage_ids=(
        parallel_roots[49],
        "join",
    ),
)

parallel_partial_result = resolve_runnable_stages(
    parallel_graph,
    parallel_partial,
)

check(
    "Final parallel root remains runnable",
    parallel_partial_result.runnable_stage_ids
    == (
        parallel_roots[49],
    ),
)

check(
    "Join blocked until all 50 roots complete",
    parallel_partial_result.blocked_stage_ids
    == ("join",),
)


parallel_complete = create_runnable_stage_state(
    workflow_id="parallel",
    completed_stage_ids=parallel_roots,
    pending_stage_ids=("join",),
)

parallel_complete_result = resolve_runnable_stages(
    parallel_graph,
    parallel_complete,
)

check(
    "Join runnable after all 50 roots complete",
    parallel_complete_result.runnable_stage_ids
    == ("join",),
)


# =============================================================================
# 14. Current-stage exclusion
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
    "Current stage excluded from runnable result",
    current_result.runnable_stage_ids
    == (
        "a",
        "c",
    ),
)

check(
    "Current stage represented as blocked",
    current_result.blocked_stage_ids
    == ("b",),
)

current_evidence = next(
    item
    for item
    in current_result.evidence
    if item.stage_id == "b"
)

check(
    "Current-stage reason exact",
    current_evidence.reason
    == "current_stage_not_runnable",
)


# =============================================================================
# 15. Completed/failed/skipped prerequisite matrix
# =============================================================================

matrix_graph = create_dependency_graph(
    workflow_id="matrix",
    edges=(
        ("a", "target"),
        ("b", "target"),
        ("c", "target"),
    ),
)

completed_only_state = create_runnable_stage_state(
    workflow_id="matrix",
    completed_stage_ids=(
        "a",
        "b",
        "c",
    ),
    pending_stage_ids=(
        "target",
    ),
)

completed_only_result = resolve_runnable_stages(
    matrix_graph,
    completed_only_state,
)

check(
    "All-completed prerequisites release target",
    completed_only_result.runnable_stage_ids
    == ("target",),
)


failed_matrix_state = create_runnable_stage_state(
    workflow_id="matrix",
    completed_stage_ids=(
        "a",
        "b",
    ),
    failed_stage_ids=(
        "c",
    ),
    pending_stage_ids=(
        "target",
    ),
)

failed_matrix_result = resolve_runnable_stages(
    matrix_graph,
    failed_matrix_state,
)

check(
    "One failed prerequisite blocks target",
    failed_matrix_result.runnable_stage_ids == (),
)

check(
    "Failed prerequisite appears unsatisfied",
    failed_matrix_result.evidence[0]
    .unsatisfied_prerequisite_stage_ids
    == ("c",),
)


skipped_matrix_state = create_runnable_stage_state(
    workflow_id="matrix",
    completed_stage_ids=(
        "a",
        "b",
    ),
    skipped_stage_ids=(
        "c",
    ),
    pending_stage_ids=(
        "target",
    ),
)

skipped_matrix_result = resolve_runnable_stages(
    matrix_graph,
    skipped_matrix_state,
)

check(
    "One skipped prerequisite blocks target in base 4.4",
    skipped_matrix_result.runnable_stage_ids == (),
)

check(
    "Skipped prerequisite appears unsatisfied",
    skipped_matrix_result.evidence[0]
    .unsatisfied_prerequisite_stage_ids
    == ("c",),
)


# =============================================================================
# 16. Multiple unsatisfied prerequisites evidence
# =============================================================================

blocked_state = create_runnable_stage_state(
    workflow_id="matrix",
    completed_stage_ids=("a",),
    pending_stage_ids=(
        "b",
        "c",
        "target",
    ),
)

blocked_result = resolve_runnable_stages(
    matrix_graph,
    blocked_state,
)

target_evidence = next(
    item
    for item
    in blocked_result.evidence
    if item.stage_id == "target"
)

check(
    "Target prerequisite tuple exact",
    target_evidence.prerequisite_stage_ids
    == (
        "a",
        "b",
        "c",
    ),
)

check(
    "Satisfied prerequisite evidence exact",
    target_evidence.satisfied_prerequisite_stage_ids
    == ("a",),
)

check(
    "Unsatisfied prerequisite evidence exact",
    target_evidence.unsatisfied_prerequisite_stage_ids
    == (
        "b",
        "c",
    ),
)

check(
    "Blocked reason exact",
    target_evidence.reason
    == "prerequisites_incomplete",
)


# =============================================================================
# 17. Identity mismatch
# =============================================================================

expect_exception(
    "Workflow/graph identity mismatch rejected",
    WorkflowGraphIdentityMismatchError,
    lambda: resolve_runnable_stages(
        matrix_graph,
        create_runnable_stage_state(
            workflow_id="other",
            pending_stage_ids=("target",),
        ),
    ),
)


# =============================================================================
# 18. Out-of-graph references
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
        f"Out-of-graph stage rejected: {label}",
        InvalidRunnableStageStateError,
        lambda kwargs=kwargs: resolve_runnable_stages(
            matrix_graph,
            create_runnable_stage_state(
                workflow_id="matrix",
                **kwargs,
            ),
        ),
    )


# =============================================================================
# 19. Cyclic graph protection
# =============================================================================

cyclic_graph = create_dependency_graph(
    workflow_id="cycle",
    edges=(
        ("a", "b"),
        ("b", "a"),
    ),
)

cyclic_state = create_runnable_stage_state(
    workflow_id="cycle",
    pending_stage_ids=(
        "a",
        "b",
    ),
)

expect_exception(
    "Cyclic graph rejected by Phase 4.3",
    CyclicDependencyGraphError,
    lambda: resolve_runnable_stages(
        cyclic_graph,
        cyclic_state,
    ),
)


# =============================================================================
# 20. Self-dependency protection
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
    "Self-dependency rejected by frozen 4.2",
    DependencyGraphValidationFailedError,
    lambda: resolve_runnable_stages(
        self_graph,
        self_state,
    ),
)


# =============================================================================
# 21. Untracked-stage behavior
# =============================================================================

untracked_graph = create_dependency_graph(
    workflow_id="untracked",
    node_ids=(
        "a",
        "b",
        "c",
        "d",
        "e",
    ),
)

untracked_state = create_runnable_stage_state(
    workflow_id="untracked",
    completed_stage_ids=("a",),
    pending_stage_ids=("b",),
    failed_stage_ids=("c",),
)

untracked_result = resolve_runnable_stages(
    untracked_graph,
    untracked_state,
)

check(
    "Untracked IDs exact and lexical",
    untracked_result.untracked_stage_ids
    == (
        "d",
        "e",
    ),
)

check(
    "Untracked IDs absent from runnable result",
    not (
        set(
            untracked_result.untracked_stage_ids
        )
        & set(
            untracked_result.runnable_stage_ids
        )
    ),
)

check(
    "Evidence generated only for pending stage",
    tuple(
        item.stage_id
        for item
        in untracked_result.evidence
    )
    == ("b",),
)


# =============================================================================
# 22. State immutability
# =============================================================================

blocked = False

try:
    canonical_state.workflow_id = "changed"

except Exception:
    blocked = True

check(
    "RunnableStageState immutable",
    blocked,
)

state_map = canonical_state.to_dict()

check(
    "RunnableStageState mapping immutable",
    isinstance(
        state_map,
        MappingProxyType,
    ),
)

blocked = False

try:
    state_map[
        "pending_stage_ids"
    ] = ()

except Exception:
    blocked = True

check(
    "RunnableStageState mapping mutation blocked",
    blocked,
)


# =============================================================================
# 23. Evidence immutability
# =============================================================================

sample_evidence = (
    chain_initial_result.evidence[1]
)

blocked = False

try:
    sample_evidence.reason = "changed"

except Exception:
    blocked = True

check(
    "StageRunnabilityEvidence immutable",
    blocked,
)

evidence_map = sample_evidence.to_dict()

check(
    "StageRunnabilityEvidence mapping immutable",
    isinstance(
        evidence_map,
        MappingProxyType,
    ),
)

blocked = False

try:
    evidence_map[
        "reason"
    ] = "changed"

except Exception:
    blocked = True

check(
    "StageRunnabilityEvidence mapping mutation blocked",
    blocked,
)


# =============================================================================
# 24. Resolution immutability
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

resolution_map = (
    chain_initial_result.to_dict()
)

check(
    "RunnableStageResolution mapping immutable",
    isinstance(
        resolution_map,
        MappingProxyType,
    ),
)

check(
    "Resolution evidence tuple immutable",
    isinstance(
        resolution_map["evidence"],
        tuple,
    ),
)

check(
    "Resolution nested evidence immutable",
    isinstance(
        resolution_map["evidence"][0],
        MappingProxyType,
    ),
)

blocked = False

try:
    resolution_map[
        "evidence"
    ][0][
        "reason"
    ] = "changed"

except Exception:
    blocked = True

check(
    "Resolution deep mutation blocked",
    blocked,
)


# =============================================================================
# 25. Snapshot
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
    == parallel_roots,
)

check(
    "Snapshot blocked IDs exact",
    snapshot[
        "blocked_stage_ids"
    ]
    == ("join",),
)

check(
    "Snapshot evidence tuple",
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
# 26. Determinism
# =============================================================================

check(
    "Repeated 200-stage chain deterministic",
    resolve_runnable_stages(
        chain_graph,
        chain_mid_state,
    )
    == chain_mid_result,
)

check(
    "Repeated 50-root topology deterministic",
    resolve_runnable_stages(
        parallel_graph,
        parallel_initial,
    )
    == parallel_initial_result,
)

check(
    "Repeated matrix topology deterministic",
    resolve_runnable_stages(
        matrix_graph,
        blocked_state,
    )
    == blocked_result,
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


# =============================================================================
# 27. Architecture evidence
# =============================================================================

architecture = (
    explain_runnable_stage_resolver_v4_4()
)

check(
    "Architecture MappingProxyType",
    isinstance(
        architecture,
        MappingProxyType,
    ),
)

check(
    "Architecture phase exact",
    architecture["phase"]
    == "4.4",
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
    architecture[
        "workflow_progress_authority"
    ]
    == (
        "immutable projection of frozen "
        "Universal Workflow Contract"
    ),
)


upstream = architecture[
    "upstream_versions"
]

check(
    "Architecture upstream mapping immutable",
    isinstance(
        upstream,
        MappingProxyType,
    ),
)

check(
    "Architecture 4.1 version exact",
    upstream["4.1"]
    == DEPENDENCY_GRAPH_VERSION,
)

check(
    "Architecture 4.2 version exact",
    upstream["4.2"]
    == DEPENDENCY_VALIDATION_VERSION,
)

check(
    "Architecture 4.3 version exact",
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
    "Completed stage candidate semantics exact",
    candidate_semantics[
        "completed_stage"
    ] == "not runnable",
)

check(
    "Failed stage candidate semantics exact",
    candidate_semantics[
        "failed_stage"
    ] == "not runnable",
)

check(
    "Skipped stage candidate semantics exact",
    candidate_semantics[
        "skipped_stage"
    ] == "not runnable",
)

check(
    "Current stage candidate semantics exact",
    candidate_semantics[
        "current_stage"
    ] == "not runnable",
)

check(
    "Untracked node semantics exact",
    candidate_semantics[
        "untracked_graph_node"
    ] == "not runnable",
)

check(
    "Root semantics exact",
    candidate_semantics[
        "root_stage"
    ]
    == "runnable when pending and not current",
)

check(
    "Isolated semantics exact",
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
    "Completed prerequisite exact",
    prerequisite_semantics[
        "completed"
    ] == "satisfied",
)

check(
    "Failed prerequisite exact",
    prerequisite_semantics[
        "failed"
    ] == "unsatisfied",
)

check(
    "Skipped prerequisite exact",
    prerequisite_semantics[
        "skipped"
    ]
    == (
        "unsatisfied in base Phase 4.4; "
        "advanced Skip Semantics belong to Phase 7.7"
    ),
)

check(
    "All completed prerequisites exact",
    prerequisite_semantics[
        "all_direct_prerequisites_completed"
    ] == "runnable",
)

check(
    "Incomplete prerequisite exact",
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
    "Runnable IDs lexical exact",
    result_semantics[
        "runnable_stage_ids"
    ] == "lexically ordered",
)

check(
    "Blocked IDs lexical exact",
    result_semantics[
        "blocked_stage_ids"
    ] == "lexically ordered",
)

check(
    "Evidence scope exact",
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
    execution["read_only"] is True,
)

check(
    "4.4 deterministic",
    execution["deterministic"] is True,
)

check(
    "4.4 side-effect free",
    execution["side_effect_free"] is True,
)

check(
    "4.4 graph mutation disabled",
    execution["graph_mutation"] is False,
)

check(
    "4.4 workflow mutation disabled",
    execution["workflow_mutation"] is False,
)

check(
    "4.4 Runtime execution disabled",
    execution["runtime_execution"] is False,
)

check(
    "4.4 persistence disabled",
    execution["persistence"] is False,
)


# =============================================================================
# 28. Static import boundary
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


allowed_imports = {
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
        allowed_imports
    ),
    repr(backend_imports),
)


# =============================================================================
# 29. Forbidden execution authority
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
    "dispatch_job",
    "persist",
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
            bad_calls.append(name)


check(
    "4.4 performs no Runtime/planning/persistence execution",
    not bad_calls,
    repr(bad_calls),
)


# =============================================================================
# 30. Public API authority boundary
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
    "fan_out",
    "fan_in",
)

check(
    "4.4 exposes no planner/Runtime/persistence/advanced-orchestration API",
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
# 31. Source authority assertions
# =============================================================================

source_assertions = (
    (
        "Source owns runnable-stage resolution",
        "deterministic runnable-stage resolution",
    ),
    (
        "Source owns blocked-stage evidence",
        "blocked-stage prerequisite evidence",
    ),
    (
        "Source owns workflow/graph identity validation",
        "workflow/graph identity validation",
    ),
    (
        "Source owns base prerequisite semantics",
        "base prerequisite-satisfaction semantics",
    ),
    (
        "Source says COMPLETED satisfies prerequisite",
        "COMPLETED satisfies a prerequisite",
    ),
    (
        "Source says FAILED does not satisfy prerequisite",
        "FAILED does not satisfy a prerequisite",
    ),
    (
        "Source says SKIPPED does not satisfy prerequisite",
        "SKIPPED does not satisfy a prerequisite",
    ),
    (
        "Source reserves Skip Semantics for 7.7",
        "Advanced skip semantics belong to Phase 7.7",
    ),
    (
        "Source defers graph construction to 4.1",
        "dependency graph construction (Phase 4.1)",
    ),
    (
        "Source defers validation to 4.2",
        "dependency semantic validation (Phase 4.2)",
    ),
    (
        "Source defers cycle detection to 4.3",
        "cycle detection (Phase 4.3)",
    ),
    (
        "Source defers planning to 4.5",
        "execution ordering/planning (Phase 4.5)",
    ),
    (
        "Source defers certification to 4.6",
        "planning certification (Phase 4.6)",
    ),
    (
        "Source excludes Runtime",
        "Runtime dispatch/execution (Phase 5)",
    ),
    (
        "Source excludes handoff",
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
# 32. Final freeze candidate
# =============================================================================

check(
    "Phase 4.4 SHA remains freeze candidate",
    actual_44_sha == EXPECTED_44_SHA,
    actual_44_sha,
)


# =============================================================================
# FINAL RESULT
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
    "PHASE 4.4 — RUNNABLE STAGE RESOLVER FINAL CERTIFICATION",
    "=" * 108,
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
        "STATUS: CERTIFICATION PASSED"
        if failed == 0
        else "STATUS: CERTIFICATION FAILED"
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
print("=" * 108)
print("PHASE 4.4 FINAL CERTIFICATION RESULT")
print("=" * 108)
print("Checks:", len(checks))
print("Passed:", passed)
print("Failed:", failed)
print(
    "STATUS:",
    (
        "CERTIFICATION PASSED"
        if failed == 0
        else "CERTIFICATION FAILED"
    ),
)
print(
    "PHASE 4.1 SHA256:",
    actual_41_sha,
)
print(
    "PHASE 4.2 SHA256:",
    actual_42_sha,
)
print(
    "PHASE 4.3 SHA256:",
    actual_43_sha,
)
print(
    "PHASE 4.4 SHA256:",
    actual_44_sha,
)
print(
    "REPORT:",
    REPORT.name,
)
print("=" * 108)


raise SystemExit(
    0
    if failed == 0
    else 1
)
