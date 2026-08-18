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
    RunnableStageResolution,
    create_runnable_stage_state,
    resolve_runnable_stages,
)

from backend.server.coordination.dependency_planning.execution_planner import (
    EXECUTION_PLANNER_VERSION,
    EXECUTION_PLANNER_SCHEMA_VERSION,
    EXECUTION_WAVE_FIELD_COUNT,
    EXECUTION_PLAN_FIELD_COUNT,
    ExecutionPlannerError,
    InvalidExecutionPlanningRequestError,
    ExecutionPlanWorkflowMismatchError,
    ExecutionPlanRunnabilityMismatchError,
    ExecutionWave,
    ExecutionPlan,
    create_execution_plan,
    execution_plan_snapshot,
    explain_execution_planner_v4_5,
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

PHASE_45 = ROOT / (
    "backend/server/coordination/"
    "dependency_planning/execution_planner.py"
)

REPORT = ROOT / (
    "execution_planner_phase_4_5_final_certification.txt"
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

EXPECTED_45_SHA = (
    "808743F566978530B2FC774DBD70A5FFA"
    "820F0EFE431512E882E0CF0F7B81958"
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


def synthetic_resolution(
    *,
    workflow_id,
    runnable=(),
    blocked=(),
    untracked=(),
    graph_version=DEPENDENCY_GRAPH_VERSION,
    cycle_version=CYCLE_DETECTION_VERSION,
    resolver_version=RUNNABLE_STAGE_RESOLVER_VERSION,
):
    return RunnableStageResolution(
        workflow_id=workflow_id,
        runnable_stage_ids=tuple(runnable),
        blocked_stage_ids=tuple(blocked),
        untracked_stage_ids=tuple(untracked),
        evidence=(),
        graph_version=graph_version,
        cycle_detection_version=cycle_version,
        resolver_version=resolver_version,
    )


print()
print("=" * 108)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 4.5 — EXECUTION PLANNER FINAL CERTIFICATION")
print("=" * 108)


# =============================================================================
# 1. Canonical files
# =============================================================================

for label, path in (
    ("Frozen Phase 4.1", PHASE_41),
    ("Frozen Phase 4.2", PHASE_42),
    ("Frozen Phase 4.3", PHASE_43),
    ("Frozen Phase 4.4", PHASE_44),
    ("Canonical Phase 4.5", PHASE_45),
):
    check(
        f"{label} file exists",
        path.exists(),
        str(
            path.relative_to(ROOT)
        ),
    )


# =============================================================================
# 2. SHA integrity
# =============================================================================

actual_41_sha = sha256(PHASE_41)
actual_42_sha = sha256(PHASE_42)
actual_43_sha = sha256(PHASE_43)
actual_44_sha = sha256(PHASE_44)
actual_45_sha = sha256(PHASE_45)

for phase, actual, expected in (
    ("4.1", actual_41_sha, EXPECTED_41_SHA),
    ("4.2", actual_42_sha, EXPECTED_42_SHA),
    ("4.3", actual_43_sha, EXPECTED_43_SHA),
    ("4.4", actual_44_sha, EXPECTED_44_SHA),
    ("4.5", actual_45_sha, EXPECTED_45_SHA),
):
    check(
        f"Phase {phase} SHA exact",
        actual == expected,
        actual,
    )


# =============================================================================
# 3. Syntax / import
# =============================================================================

source = PHASE_45.read_text(
    encoding="utf-8-sig"
)

try:
    tree = ast.parse(source)
    syntax_ok = True

except SyntaxError:
    tree = None
    syntax_ok = False

check(
    "Phase 4.5 syntax parses",
    syntax_ok,
)

try:
    importlib.import_module(
        "backend.server.coordination."
        "dependency_planning.execution_planner"
    )
    import_ok = True
    import_detail = ""

except Exception as exc:
    import_ok = False
    import_detail = repr(exc)

check(
    "Phase 4.5 module imports successfully",
    import_ok,
    import_detail,
)


# =============================================================================
# 4. Exact identity
# =============================================================================

check(
    "Planner version exact",
    EXECUTION_PLANNER_VERSION
    == "execution_planner_v4.5.0",
)

check(
    "Planner schema exact",
    EXECUTION_PLANNER_SCHEMA_VERSION
    == "execution_planner_schema_v1",
)

check(
    "ExecutionWave field-count constant exact",
    EXECUTION_WAVE_FIELD_COUNT == 3,
)

check(
    "ExecutionPlan field-count constant exact",
    EXECUTION_PLAN_FIELD_COUNT == 8,
)


wave_fields = tuple(
    field.name
    for field
    in fields(ExecutionWave)
)

plan_fields = tuple(
    field.name
    for field
    in fields(ExecutionPlan)
)

check(
    "ExecutionWave exact field contract",
    wave_fields == (
        "wave_index",
        "stage_ids",
        "execution_semantics",
    ),
)

check(
    "ExecutionPlan exact field contract",
    plan_fields == (
        "workflow_id",
        "wave_count",
        "waves",
        "planned_stage_ids",
        "graph_version",
        "cycle_detection_version",
        "runnable_stage_resolver_version",
        "planner_version",
    ),
)


# =============================================================================
# 5. Invalid input types
# =============================================================================

base_graph = create_dependency_graph(
    workflow_id="base",
    edges=(
        ("a", "b"),
        ("b", "c"),
    ),
)

base_state = create_runnable_stage_state(
    workflow_id="base",
    pending_stage_ids=(
        "a",
        "b",
        "c",
    ),
)

base_resolution = resolve_runnable_stages(
    base_graph,
    base_state,
)

for label, value in (
    ("None", None),
    ("string", "bad"),
    ("integer", 1),
    ("mapping", {}),
    ("tuple", ()),
):
    expect_exception(
        f"Invalid graph rejected: {label}",
        InvalidExecutionPlanningRequestError,
        lambda value=value: create_execution_plan(
            value,
            base_resolution,
        ),
    )

for label, value in (
    ("None", None),
    ("string", "bad"),
    ("integer", 1),
    ("mapping", {}),
    ("tuple", ()),
):
    expect_exception(
        f"Invalid resolution rejected: {label}",
        InvalidExecutionPlanningRequestError,
        lambda value=value: create_execution_plan(
            base_graph,
            value,
        ),
    )


# =============================================================================
# 6. Empty graph
# =============================================================================

empty_graph = create_dependency_graph(
    workflow_id="empty"
)

empty_state = create_runnable_stage_state(
    workflow_id="empty"
)

empty_resolution = resolve_runnable_stages(
    empty_graph,
    empty_state,
)

empty_plan = create_execution_plan(
    empty_graph,
    empty_resolution,
)

check(
    "Empty graph produces zero-wave plan",
    empty_plan.wave_count == 0,
)

check(
    "Empty graph waves empty",
    empty_plan.waves == (),
)

check(
    "Empty graph planned IDs empty",
    empty_plan.planned_stage_ids == (),
)


# =============================================================================
# 7. Single isolated runnable stage
# =============================================================================

single_graph = create_dependency_graph(
    workflow_id="single",
    node_ids=("only",),
)

single_state = create_runnable_stage_state(
    workflow_id="single",
    pending_stage_ids=("only",),
)

single_resolution = resolve_runnable_stages(
    single_graph,
    single_state,
)

single_plan = create_execution_plan(
    single_graph,
    single_resolution,
)

check(
    "Single isolated stage creates one wave",
    single_plan.wave_count == 1,
)

check(
    "Single isolated planned exact",
    single_plan.planned_stage_ids
    == ("only",),
)

check(
    "Single isolated wave index exact",
    single_plan.waves[0].wave_index == 1,
)


# =============================================================================
# 8. Linear progression
# =============================================================================

check(
    "Initial chain plans A only",
    create_execution_plan(
        base_graph,
        base_resolution,
    ).planned_stage_ids
    == ("a",),
)

after_a_state = create_runnable_stage_state(
    workflow_id="base",
    completed_stage_ids=("a",),
    pending_stage_ids=(
        "b",
        "c",
    ),
)

after_a_resolution = resolve_runnable_stages(
    base_graph,
    after_a_state,
)

check(
    "After A completion plans B only",
    create_execution_plan(
        base_graph,
        after_a_resolution,
    ).planned_stage_ids
    == ("b",),
)

after_ab_state = create_runnable_stage_state(
    workflow_id="base",
    completed_stage_ids=(
        "a",
        "b",
    ),
    pending_stage_ids=("c",),
)

after_ab_resolution = resolve_runnable_stages(
    base_graph,
    after_ab_state,
)

check(
    "After A+B completion plans C only",
    create_execution_plan(
        base_graph,
        after_ab_resolution,
    ).planned_stage_ids
    == ("c",),
)


# =============================================================================
# 9. Parallel roots / join
# =============================================================================

parallel_graph = create_dependency_graph(
    workflow_id="parallel",
    edges=(
        ("a", "join"),
        ("b", "join"),
        ("c", "join"),
        ("d", "join"),
        ("e", "join"),
    ),
)

parallel_state = create_runnable_stage_state(
    workflow_id="parallel",
    pending_stage_ids=(
        "join",
        "e",
        "d",
        "c",
        "b",
        "a",
    ),
)

parallel_resolution = resolve_runnable_stages(
    parallel_graph,
    parallel_state,
)

parallel_plan = create_execution_plan(
    parallel_graph,
    parallel_resolution,
)

check(
    "Five parallel roots remain one wave",
    parallel_plan.wave_count == 1,
)

check(
    "Five parallel roots lexical",
    parallel_plan.planned_stage_ids
    == (
        "a",
        "b",
        "c",
        "d",
        "e",
    ),
)

check(
    "Blocked join excluded",
    "join"
    not in parallel_plan.planned_stage_ids,
)

check(
    "Wave IDs equal planned IDs",
    parallel_plan.waves[0].stage_ids
    == parallel_plan.planned_stage_ids,
)

check(
    "Execution semantics parallel eligible",
    parallel_plan.waves[0].execution_semantics
    == "parallel_eligible",
)


# =============================================================================
# 10. Large parallel wave
# =============================================================================

large_nodes = tuple(
    f"p-{i:04d}"
    for i in range(500)
)

large_graph = create_dependency_graph(
    workflow_id="large-parallel",
    node_ids=large_nodes,
)

large_state = create_runnable_stage_state(
    workflow_id="large-parallel",
    pending_stage_ids=tuple(
        reversed(large_nodes)
    ),
)

large_resolution = resolve_runnable_stages(
    large_graph,
    large_state,
)

large_plan = create_execution_plan(
    large_graph,
    large_resolution,
)

check(
    "500 runnable stages remain one wave",
    large_plan.wave_count == 1,
)

check(
    "500 runnable stages all planned",
    len(
        large_plan.planned_stage_ids
    ) == 500,
)

check(
    "500 runnable stage ordering lexical",
    large_plan.planned_stage_ids
    == large_nodes,
)

check(
    "500-stage wave not artificially split",
    len(
        large_plan.waves
    ) == 1,
)


# =============================================================================
# 11. Current-stage exclusion inherited from 4.4
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

current_resolution = resolve_runnable_stages(
    current_graph,
    current_state,
)

current_plan = create_execution_plan(
    current_graph,
    current_resolution,
)

check(
    "Current stage excluded from plan",
    current_plan.planned_stage_ids
    == (
        "a",
        "c",
    ),
)

check(
    "Current B not planned",
    "b"
    not in current_plan.planned_stage_ids,
)


# =============================================================================
# 12. Failed / skipped prerequisites remain blocked
# =============================================================================

prereq_graph = create_dependency_graph(
    workflow_id="prereq",
    edges=(
        ("a", "target"),
    ),
)

failed_state = create_runnable_stage_state(
    workflow_id="prereq",
    failed_stage_ids=("a",),
    pending_stage_ids=("target",),
)

failed_resolution = resolve_runnable_stages(
    prereq_graph,
    failed_state,
)

failed_plan = create_execution_plan(
    prereq_graph,
    failed_resolution,
)

check(
    "Failed prerequisite yields empty immediate plan",
    failed_plan.planned_stage_ids == (),
)

skipped_state = create_runnable_stage_state(
    workflow_id="prereq",
    skipped_stage_ids=("a",),
    pending_stage_ids=("target",),
)

skipped_resolution = resolve_runnable_stages(
    prereq_graph,
    skipped_state,
)

skipped_plan = create_execution_plan(
    prereq_graph,
    skipped_resolution,
)

check(
    "Skipped prerequisite yields empty base-4.5 plan",
    skipped_plan.planned_stage_ids == (),
)


# =============================================================================
# 13. Workflow mismatch
# =============================================================================

other_graph = create_dependency_graph(
    workflow_id="other",
    node_ids=("a",),
)

expect_exception(
    "Workflow mismatch rejected",
    ExecutionPlanWorkflowMismatchError,
    lambda: create_execution_plan(
        other_graph,
        base_resolution,
    ),
)


# =============================================================================
# 14. Cycle / self-edge upstream protection
# =============================================================================

cyclic_graph = create_dependency_graph(
    workflow_id="cycle",
    edges=(
        ("a", "b"),
        ("b", "a"),
    ),
)

cyclic_resolution = synthetic_resolution(
    workflow_id="cycle",
    runnable=("a",),
    blocked=("b",),
)

expect_exception(
    "Cyclic graph rejected by 4.3",
    CyclicDependencyGraphError,
    lambda: create_execution_plan(
        cyclic_graph,
        cyclic_resolution,
    ),
)

self_graph = create_dependency_graph(
    workflow_id="self",
    edges=(
        ("a", "a"),
    ),
)

self_resolution = synthetic_resolution(
    workflow_id="self",
    runnable=("a",),
)

expect_exception(
    "Self-dependency rejected by 4.2",
    DependencyGraphValidationFailedError,
    lambda: create_execution_plan(
        self_graph,
        self_resolution,
    ),
)


# =============================================================================
# 15. Frozen version-integrity guards
# =============================================================================

expect_exception(
    "Stale graph version rejected",
    ExecutionPlanRunnabilityMismatchError,
    lambda: create_execution_plan(
        base_graph,
        synthetic_resolution(
            workflow_id="base",
            runnable=("a",),
            graph_version="stale",
        ),
    ),
)

expect_exception(
    "Stale cycle version rejected",
    ExecutionPlanRunnabilityMismatchError,
    lambda: create_execution_plan(
        base_graph,
        synthetic_resolution(
            workflow_id="base",
            runnable=("a",),
            cycle_version="stale",
        ),
    ),
)

expect_exception(
    "Stale resolver version rejected",
    ExecutionPlanRunnabilityMismatchError,
    lambda: create_execution_plan(
        base_graph,
        synthetic_resolution(
            workflow_id="base",
            runnable=("a",),
            resolver_version="stale",
        ),
    ),
)


# =============================================================================
# 16. Canonical collection integrity
# =============================================================================

malformed_collection_cases = (
    (
        "Non-lexical runnable IDs rejected",
        synthetic_resolution(
            workflow_id="base",
            runnable=(
                "b",
                "a",
            ),
        ),
    ),
    (
        "Duplicate runnable IDs rejected",
        synthetic_resolution(
            workflow_id="base",
            runnable=(
                "a",
                "a",
            ),
        ),
    ),
    (
        "Non-lexical blocked IDs rejected",
        synthetic_resolution(
            workflow_id="base",
            runnable=("a",),
            blocked=(
                "c",
                "b",
            ),
        ),
    ),
    (
        "Duplicate blocked IDs rejected",
        synthetic_resolution(
            workflow_id="base",
            runnable=("a",),
            blocked=(
                "b",
                "b",
            ),
        ),
    ),
    (
        "Non-lexical untracked IDs rejected",
        synthetic_resolution(
            workflow_id="base",
            runnable=("a",),
            untracked=(
                "c",
                "b",
            ),
        ),
    ),
    (
        "Duplicate untracked IDs rejected",
        synthetic_resolution(
            workflow_id="base",
            runnable=("a",),
            untracked=(
                "b",
                "b",
            ),
        ),
    ),
)

for name, malformed_resolution in malformed_collection_cases:
    expect_exception(
        name,
        ExecutionPlanRunnabilityMismatchError,
        lambda malformed_resolution=malformed_resolution:
            create_execution_plan(
                base_graph,
                malformed_resolution,
            ),
    )


# =============================================================================
# 17. Graph membership guards
# =============================================================================

for label, kwargs in (
    (
        "runnable",
        dict(
            runnable=("outside",),
        ),
    ),
    (
        "blocked",
        dict(
            runnable=("a",),
            blocked=("outside",),
        ),
    ),
    (
        "untracked",
        dict(
            runnable=("a",),
            untracked=("outside",),
        ),
    ),
):
    expect_exception(
        f"Outside-graph {label} stage rejected",
        ExecutionPlanRunnabilityMismatchError,
        lambda kwargs=kwargs: create_execution_plan(
            base_graph,
            synthetic_resolution(
                workflow_id="base",
                **kwargs,
            ),
        ),
    )


# =============================================================================
# 18. Cross-collection disjointness
# =============================================================================

overlap_cases = (
    (
        "runnable/blocked",
        dict(
            runnable=("a",),
            blocked=("a",),
        ),
    ),
    (
        "runnable/untracked",
        dict(
            runnable=("a",),
            untracked=("a",),
        ),
    ),
    (
        "blocked/untracked",
        dict(
            runnable=("a",),
            blocked=("b",),
            untracked=("b",),
        ),
    ),
)

for label, kwargs in overlap_cases:
    expect_exception(
        f"Overlap rejected: {label}",
        ExecutionPlanRunnabilityMismatchError,
        lambda kwargs=kwargs: create_execution_plan(
            base_graph,
            synthetic_resolution(
                workflow_id="base",
                **kwargs,
            ),
        ),
    )


# =============================================================================
# 19. Immutability
# =============================================================================

blocked = False

try:
    parallel_plan.planned_stage_ids = ()

except Exception:
    blocked = True

check(
    "ExecutionPlan immutable",
    blocked,
)

blocked = False

try:
    parallel_plan.waves = ()

except Exception:
    blocked = True

check(
    "ExecutionPlan wave tuple immutable",
    blocked,
)

wave = parallel_plan.waves[0]

blocked = False

try:
    wave.stage_ids = ()

except Exception:
    blocked = True

check(
    "ExecutionWave immutable",
    blocked,
)


wave_map = wave.to_dict()

check(
    "ExecutionWave mapping immutable",
    isinstance(
        wave_map,
        MappingProxyType,
    ),
)

blocked = False

try:
    wave_map[
        "execution_semantics"
    ] = "serial"

except Exception:
    blocked = True

check(
    "ExecutionWave mapping mutation blocked",
    blocked,
)


plan_map = parallel_plan.to_dict()

check(
    "ExecutionPlan mapping immutable",
    isinstance(
        plan_map,
        MappingProxyType,
    ),
)

check(
    "ExecutionPlan nested waves tuple",
    isinstance(
        plan_map["waves"],
        tuple,
    ),
)

check(
    "ExecutionPlan nested wave immutable",
    isinstance(
        plan_map["waves"][0],
        MappingProxyType,
    ),
)

blocked = False

try:
    plan_map[
        "waves"
    ][0][
        "stage_ids"
    ] = ()

except Exception:
    blocked = True

check(
    "ExecutionPlan deep mutation blocked",
    blocked,
)


# =============================================================================
# 20. Snapshot
# =============================================================================

snapshot = execution_plan_snapshot(
    parallel_graph,
    parallel_resolution,
)

check(
    "Snapshot MappingProxyType",
    isinstance(
        snapshot,
        MappingProxyType,
    ),
)

check(
    "Snapshot planner version exact",
    snapshot[
        "planner_version"
    ]
    == EXECUTION_PLANNER_VERSION,
)

check(
    "Snapshot schema exact",
    snapshot[
        "schema_version"
    ]
    == EXECUTION_PLANNER_SCHEMA_VERSION,
)

check(
    "Snapshot workflow exact",
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
    "Snapshot resolver version exact",
    snapshot[
        "runnable_stage_resolver_version"
    ]
    == RUNNABLE_STAGE_RESOLVER_VERSION,
)

check(
    "Snapshot wave count exact",
    snapshot[
        "wave_count"
    ] == 1,
)

check(
    "Snapshot planned IDs exact",
    snapshot[
        "planned_stage_ids"
    ]
    == (
        "a",
        "b",
        "c",
        "d",
        "e",
    ),
)

check(
    "Snapshot nested wave immutable",
    isinstance(
        snapshot[
            "waves"
        ][0],
        MappingProxyType,
    ),
)


# =============================================================================
# 21. Architecture contract
# =============================================================================

architecture = explain_execution_planner_v4_5()

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
    == "4.5",
)

check(
    "Architecture component exact",
    architecture["component"]
    == "Execution Planner",
)

check(
    "Architecture version exact",
    architecture["version"]
    == EXECUTION_PLANNER_VERSION,
)

check(
    "Architecture schema exact",
    architecture["schema_version"]
    == EXECUTION_PLANNER_SCHEMA_VERSION,
)

check(
    "Topology authority exact",
    architecture["topology_authority"]
    == "Phase 4.1 DependencyGraph",
)

check(
    "Validation authority exact",
    architecture["validation_authority"]
    == "Phase 4.2 Dependency Validation",
)

check(
    "Acyclic authority exact",
    architecture["acyclic_authority"]
    == "Phase 4.3 Cycle Detection",
)

check(
    "Runnability authority exact",
    architecture["runnability_authority"]
    == "Phase 4.4 RunnableStageResolution",
)


upstream = architecture[
    "upstream_versions"
]

check(
    "Architecture upstream versions immutable",
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

check(
    "Architecture 4.4 version exact",
    upstream["4.4"]
    == RUNNABLE_STAGE_RESOLVER_VERSION,
)


scope = architecture[
    "planning_scope"
]

check(
    "Planning scope immutable",
    isinstance(
        scope,
        MappingProxyType,
    ),
)

check(
    "Immediate-current-wave mode exact",
    scope["mode"]
    == "immediate_current_execution_wave",
)

check(
    "Future-stage prediction disabled",
    scope[
        "future_stage_prediction"
    ] is False,
)

check(
    "Full remaining-workflow plan disabled",
    scope[
        "full_remaining_workflow_topological_plan"
    ] is False,
)

check(
    "Only currently runnable stages enabled",
    scope[
        "only_currently_runnable_stages"
    ] is True,
)


wave_semantics = architecture[
    "wave_semantics"
]

check(
    "Wave semantics immutable",
    isinstance(
        wave_semantics,
        MappingProxyType,
    ),
)

check(
    "Parallel stages one wave exact",
    wave_semantics[
        "simultaneously_runnable_stages"
    ]
    == "one execution wave",
)

check(
    "Within-wave lexical ordering exact",
    wave_semantics[
        "within_wave_order"
    ]
    == "lexical deterministic",
)

check(
    "Lexical order meaning exact",
    wave_semantics[
        "lexical_order_meaning"
    ]
    == "serialization and evidence only",
)

check(
    "Forced serial execution disabled",
    wave_semantics[
        "forced_serial_execution"
    ] is False,
)

check(
    "Artificial dependencies disabled",
    wave_semantics[
        "artificial_dependencies"
    ] is False,
)

check(
    "Empty runnable set valid",
    wave_semantics[
        "empty_runnable_set"
    ]
    == "valid empty plan",
)


runtime_policy = architecture[
    "runtime_policy"
]

check(
    "Runtime policy immutable",
    isinstance(
        runtime_policy,
        MappingProxyType,
    ),
)

for key in (
    "worker_capacity",
    "queue_state",
    "priority",
    "retries",
    "cost",
    "resource_availability",
):
    check(
        f"Runtime policy excluded: {key}",
        runtime_policy[key]
        == "not considered",
    )

check(
    "Runtime job creation disabled",
    runtime_policy[
        "job_creation"
    ] is False,
)

check(
    "Runtime dispatch disabled",
    runtime_policy[
        "dispatch"
    ] is False,
)


execution_properties = architecture[
    "execution_properties"
]

check(
    "Execution properties immutable",
    isinstance(
        execution_properties,
        MappingProxyType,
    ),
)

for key in (
    "read_only",
    "deterministic",
    "side_effect_free",
):
    check(
        f"Execution property true: {key}",
        execution_properties[
            key
        ] is True,
    )

for key in (
    "graph_mutation",
    "resolution_mutation",
    "runtime_execution",
    "runtime_job_creation",
    "persistence",
):
    check(
        f"Execution property false: {key}",
        execution_properties[
            key
        ] is False,
    )


# =============================================================================
# 22. Determinism
# =============================================================================

check(
    "Repeated base plan deterministic",
    create_execution_plan(
        base_graph,
        base_resolution,
    )
    == create_execution_plan(
        base_graph,
        base_resolution,
    ),
)

check(
    "Repeated parallel plan deterministic",
    create_execution_plan(
        parallel_graph,
        parallel_resolution,
    )
    == parallel_plan,
)

check(
    "Repeated 500-stage plan deterministic",
    create_execution_plan(
        large_graph,
        large_resolution,
    )
    == large_plan,
)

check(
    "Repeated snapshot deterministic",
    dict(
        execution_plan_snapshot(
            parallel_graph,
            parallel_resolution,
        )
    )
    == dict(snapshot),
)

check(
    "Repeated architecture deterministic",
    dict(
        explain_execution_planner_v4_5()
    )
    == dict(architecture),
)


# =============================================================================
# 23. Static import boundary
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
    (
        "backend.server.coordination."
        "dependency_planning.runnable_stage_resolver"
    ),
}

check(
    "4.5 imports only frozen Phase 4 upstream components",
    set(
        backend_imports
    ).issubset(
        allowed_imports
    ),
    repr(
        backend_imports
    ),
)


# =============================================================================
# 24. No forbidden execution authority
# =============================================================================

forbidden_calls = {
    "dispatch",
    "dispatch_job",
    "enqueue",
    "enqueue_job",
    "submit_job",
    "create_job",
    "execute",
    "execute_job",
    "register",
    "register_workflow",
    "register_coordinator",
    "select_worker",
    "schedule_stage",
    "save",
    "persist",
    "commit",
    "checkpoint",
    "pause",
    "resume",
    "recover",
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
    "4.5 performs no Runtime/dispatch/persistence execution",
    not bad_calls,
    repr(
        bad_calls
    ),
)


# =============================================================================
# 25. Public API boundary
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
    "dispatch",
    "enqueue",
    "worker",
    "runtime",
    "persist",
    "recover",
    "checkpoint",
    "schedule",
    "future_plan",
    "full_workflow",
)

check(
    "4.5 exposes no Runtime/persistence/future-planning API",
    not any(
        any(
            token in name.lower()
            for token
            in forbidden_public_tokens
        )
        for name
        in public_names
    ),
    repr(
        public_names
    ),
)


# =============================================================================
# 26. Source authority evidence
# =============================================================================

source_assertions = (
    (
        "Source owns immediate execution wave",
        "immediate execution wave",
    ),
    (
        "Source plans runnable NOW only",
        "runnable NOW",
    ),
    (
        "Source excludes future prediction",
        "predict future workflow stages",
    ),
    (
        "Source excludes full future topological planning",
        "full remaining-workflow topological plan",
    ),
    (
        "Source excludes artificial dependencies",
        "invent dependencies between simultaneously runnable stages",
    ),
    (
        "Source excludes job dispatch",
        "dispatch jobs",
    ),
    (
        "Source excludes Runtime job creation",
        "create Runtime jobs",
    ),
    (
        "Source excludes worker selection",
        "select workers",
    ),
    (
        "Source excludes Runtime queue state",
        "inspect Runtime queue state",
    ),
    (
        "Source excludes Runtime scheduling policy",
        "capacity/priority/retry/resource policy",
    ),
    (
        "Source excludes persistence",
        "persist planning state",
    ),
    (
        "Source lexical order is not serial execution",
        "does not imply forced serial execution",
    ),
    (
        "Source defers planning certification to 4.6",
        "planning certification -> Phase 4.6",
    ),
    (
        "Source defers Runtime execution to Phase 5",
        "Runtime execution -> Phase 5",
    ),
    (
        "Source defers handoff to Phase 6",
        "handoff -> Phase 6",
    ),
    (
        "Source defers advanced orchestration to Phase 7",
        "advanced orchestration -> Phase 7",
    ),
    (
        "Source defers persistence to Phase 8",
        "persistence -> Phase 8",
    ),
    (
        "Source defers recovery to Phase 9",
        "recovery -> Phase 9",
    ),
)

for name, marker in source_assertions:
    check(
        name,
        marker in source,
    )


# =============================================================================
# 27. Freeze candidate
# =============================================================================

check(
    "Phase 4.5 SHA remains final freeze candidate",
    actual_45_sha
    == EXPECTED_45_SHA,
    actual_45_sha,
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
    "PHASE 4.5 — EXECUTION PLANNER FINAL CERTIFICATION",
    "=" * 108,
    "",
    (
        "Execution Planner Version: "
        + EXECUTION_PLANNER_VERSION
    ),
    (
        "Execution Planner Schema: "
        + EXECUTION_PLANNER_SCHEMA_VERSION
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
        "Frozen Phase 4.4 SHA256: "
        + actual_44_sha
    ),
    (
        "Phase 4.5 SHA256: "
        + actual_45_sha
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
print("PHASE 4.5 FINAL CERTIFICATION RESULT")
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
    "PHASE 4.5 SHA256:",
    actual_45_sha,
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
