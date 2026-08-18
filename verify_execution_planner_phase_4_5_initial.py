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
    "execution_planner_phase_4_5_initial_verification.txt"
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

EXPECTED_45_CANDIDATE_SHA = (
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
print("PHASE 4.5 — EXECUTION PLANNER INITIAL VERIFICATION")
print("=" * 108)


# =============================================================================
# 1. Canonical file / syntax / import
# =============================================================================

check(
    "Canonical Phase 4.5 file exists",
    PHASE_45.exists(),
    str(
        PHASE_45.relative_to(ROOT)
    ),
)

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
    "Phase 4.5 Python syntax parses",
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
# 2. Frozen upstream integrity
# =============================================================================

actual_41_sha = sha256(PHASE_41)
actual_42_sha = sha256(PHASE_42)
actual_43_sha = sha256(PHASE_43)
actual_44_sha = sha256(PHASE_44)
actual_45_sha = sha256(PHASE_45)

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
    "Frozen Phase 4.4 SHA exact",
    actual_44_sha == EXPECTED_44_SHA,
    actual_44_sha,
)

check(
    "Phase 4.5 candidate SHA unchanged",
    actual_45_sha == EXPECTED_45_CANDIDATE_SHA,
    actual_45_sha,
)


# =============================================================================
# 3. Identity / contracts
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
# 4. Invalid input types
# =============================================================================

graph = create_dependency_graph(
    workflow_id="chain",
    edges=(
        ("a", "b"),
        ("b", "c"),
    ),
)

state = create_runnable_stage_state(
    workflow_id="chain",
    pending_stage_ids=(
        "a",
        "b",
        "c",
    ),
)

resolution = resolve_runnable_stages(
    graph,
    state,
)


for label, value in (
    ("None", None),
    ("string", "graph"),
    ("integer", 1),
    ("mapping", {}),
    ("tuple", ()),
):
    expect_exception(
        f"Invalid graph rejected: {label}",
        InvalidExecutionPlanningRequestError,
        lambda value=value: create_execution_plan(
            value,
            resolution,
        ),
    )


for label, value in (
    ("None", None),
    ("string", "resolution"),
    ("integer", 1),
    ("mapping", {}),
    ("tuple", ()),
):
    expect_exception(
        f"Invalid resolution rejected: {label}",
        InvalidExecutionPlanningRequestError,
        lambda value=value: create_execution_plan(
            graph,
            value,
        ),
    )


# =============================================================================
# 5. Empty plan
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
    "Empty plan wave tuple empty",
    empty_plan.waves == (),
)

check(
    "Empty plan stage IDs empty",
    empty_plan.planned_stage_ids == (),
)


# =============================================================================
# 6. Linear workflow progression
# =============================================================================

initial_plan = create_execution_plan(
    graph,
    resolution,
)

check(
    "Initial chain plans root A only",
    initial_plan.planned_stage_ids
    == ("a",),
)

check(
    "Initial chain has one wave",
    initial_plan.wave_count == 1,
)


after_a_state = create_runnable_stage_state(
    workflow_id="chain",
    completed_stage_ids=("a",),
    pending_stage_ids=(
        "b",
        "c",
    ),
)

after_a_resolution = resolve_runnable_stages(
    graph,
    after_a_state,
)

after_a_plan = create_execution_plan(
    graph,
    after_a_resolution,
)

check(
    "After A completion planner plans B only",
    after_a_plan.planned_stage_ids
    == ("b",),
)


after_ab_state = create_runnable_stage_state(
    workflow_id="chain",
    completed_stage_ids=(
        "a",
        "b",
    ),
    pending_stage_ids=("c",),
)

after_ab_resolution = resolve_runnable_stages(
    graph,
    after_ab_state,
)

after_ab_plan = create_execution_plan(
    graph,
    after_ab_resolution,
)

check(
    "After A+B completion planner plans C only",
    after_ab_plan.planned_stage_ids
    == ("c",),
)


# =============================================================================
# 7. Parallel-wave preservation
# =============================================================================

parallel_graph = create_dependency_graph(
    workflow_id="parallel",
    edges=(
        ("a", "join"),
        ("b", "join"),
        ("c", "join"),
        ("d", "join"),
    ),
)

parallel_state = create_runnable_stage_state(
    workflow_id="parallel",
    pending_stage_ids=(
        "join",
        "d",
        "b",
        "a",
        "c",
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
    "Four parallel roots remain one wave",
    parallel_plan.wave_count == 1,
)

check(
    "Parallel wave IDs exact and lexical",
    parallel_plan.planned_stage_ids
    == (
        "a",
        "b",
        "c",
        "d",
    ),
)

check(
    "Wave and plan IDs identical",
    parallel_plan.waves[0].stage_ids
    == parallel_plan.planned_stage_ids,
)

check(
    "Blocked join absent from plan",
    "join"
    not in parallel_plan.planned_stage_ids,
)

check(
    "Wave execution semantics exact",
    parallel_plan.waves[0].execution_semantics
    == "parallel_eligible",
)


# =============================================================================
# 8. Large parallel wave
# =============================================================================

large_nodes = tuple(
    f"stage-{i:03d}"
    for i in range(200)
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
    "200 runnable stages remain one wave",
    large_plan.wave_count == 1,
)

check(
    "200 runnable stages all planned",
    len(
        large_plan.planned_stage_ids
    ) == 200,
)

check(
    "200-stage wave ordering lexical",
    large_plan.planned_stage_ids
    == large_nodes,
)

check(
    "Planner does not split large parallel set",
    len(
        large_plan.waves
    ) == 1,
)


# =============================================================================
# 9. Workflow mismatch
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
        resolution,
    ),
)


# =============================================================================
# 10. Cyclic graph protection
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
    "Cyclic graph rejected by Phase 4.3",
    CyclicDependencyGraphError,
    lambda: create_execution_plan(
        cyclic_graph,
        cyclic_resolution,
    ),
)


# =============================================================================
# 11. Self-edge rejected upstream
# =============================================================================

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
    "Self-dependency rejected by frozen 4.2",
    DependencyGraphValidationFailedError,
    lambda: create_execution_plan(
        self_graph,
        self_resolution,
    ),
)


# =============================================================================
# 12. Unknown runnable stage
# =============================================================================

expect_exception(
    "Runnable stage outside graph rejected",
    ExecutionPlanRunnabilityMismatchError,
    lambda: create_execution_plan(
        graph,
        synthetic_resolution(
            workflow_id="chain",
            runnable=("outside",),
        ),
    ),
)


# =============================================================================
# 13. Runnable/blocked overlap
# =============================================================================

expect_exception(
    "Runnable/blocked overlap rejected",
    ExecutionPlanRunnabilityMismatchError,
    lambda: create_execution_plan(
        graph,
        synthetic_resolution(
            workflow_id="chain",
            runnable=("a",),
            blocked=("a",),
        ),
    ),
)


# =============================================================================
# 14. Runnable/untracked overlap
# =============================================================================

expect_exception(
    "Runnable/untracked overlap rejected",
    ExecutionPlanRunnabilityMismatchError,
    lambda: create_execution_plan(
        graph,
        synthetic_resolution(
            workflow_id="chain",
            runnable=("a",),
            untracked=("a",),
        ),
    ),
)


# =============================================================================
# 15. Canonical Phase 4.4 version integrity
# =============================================================================

expect_exception(
    "Stale graph version in resolution rejected",
    ExecutionPlanRunnabilityMismatchError,
    lambda: create_execution_plan(
        graph,
        synthetic_resolution(
            workflow_id="chain",
            runnable=("a",),
            graph_version="stale_dependency_graph_version",
        ),
    ),
)

expect_exception(
    "Stale cycle-detection version rejected",
    ExecutionPlanRunnabilityMismatchError,
    lambda: create_execution_plan(
        graph,
        synthetic_resolution(
            workflow_id="chain",
            runnable=("a",),
            cycle_version="stale_cycle_detection_version",
        ),
    ),
)

expect_exception(
    "Stale resolver version rejected",
    ExecutionPlanRunnabilityMismatchError,
    lambda: create_execution_plan(
        graph,
        synthetic_resolution(
            workflow_id="chain",
            runnable=("a",),
            resolver_version="stale_resolver_version",
        ),
    ),
)


# =============================================================================
# 16. Canonical runnable tuple integrity
# =============================================================================

expect_exception(
    "Non-lexical runnable tuple rejected",
    ExecutionPlanRunnabilityMismatchError,
    lambda: create_execution_plan(
        graph,
        synthetic_resolution(
            workflow_id="chain",
            runnable=(
                "b",
                "a",
            ),
        ),
    ),
)

expect_exception(
    "Duplicate runnable IDs rejected",
    ExecutionPlanRunnabilityMismatchError,
    lambda: create_execution_plan(
        graph,
        synthetic_resolution(
            workflow_id="chain",
            runnable=(
                "a",
                "a",
            ),
        ),
    ),
)


# =============================================================================
# 17. Blocked/untracked graph membership
# =============================================================================

expect_exception(
    "Blocked stage outside graph rejected",
    ExecutionPlanRunnabilityMismatchError,
    lambda: create_execution_plan(
        graph,
        synthetic_resolution(
            workflow_id="chain",
            runnable=("a",),
            blocked=("outside",),
        ),
    ),
)

expect_exception(
    "Untracked stage outside graph rejected",
    ExecutionPlanRunnabilityMismatchError,
    lambda: create_execution_plan(
        graph,
        synthetic_resolution(
            workflow_id="chain",
            runnable=("a",),
            untracked=("outside",),
        ),
    ),
)


# =============================================================================
# 18. Blocked/untracked disjointness
# =============================================================================

expect_exception(
    "Blocked/untracked overlap rejected",
    ExecutionPlanRunnabilityMismatchError,
    lambda: create_execution_plan(
        graph,
        synthetic_resolution(
            workflow_id="chain",
            runnable=("a",),
            blocked=("b",),
            untracked=("b",),
        ),
    ),
)


# =============================================================================
# 19. Immutable plan
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


# =============================================================================
# 20. Immutable wave
# =============================================================================

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
    "ExecutionWave to_dict immutable",
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


# =============================================================================
# 21. Plan deep immutability
# =============================================================================

plan_map = parallel_plan.to_dict()

check(
    "ExecutionPlan to_dict immutable",
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
    "ExecutionPlan nested wave mapping immutable",
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
# 22. Snapshot contract
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
    ] == "parallel",
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
    ),
)

check(
    "Snapshot nested wave immutable",
    isinstance(
        snapshot["waves"][0],
        MappingProxyType,
    ),
)


# =============================================================================
# 23. Architecture evidence
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
    architecture["phase"] == "4.5",
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
    "Upstream mapping immutable",
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

check(
    "4.4 upstream version exact",
    upstream["4.4"]
    == RUNNABLE_STAGE_RESOLVER_VERSION,
)


planning_scope = architecture[
    "planning_scope"
]

check(
    "Planning scope immutable",
    isinstance(
        planning_scope,
        MappingProxyType,
    ),
)

check(
    "Planner scope immediate-wave exact",
    planning_scope[
        "mode"
    ]
    == "immediate_current_execution_wave",
)

check(
    "Future prediction disabled",
    planning_scope[
        "future_stage_prediction"
    ] is False,
)

check(
    "Full remaining topological plan disabled",
    planning_scope[
        "full_remaining_workflow_topological_plan"
    ] is False,
)

check(
    "Only current runnable stages allowed",
    planning_scope[
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
    "Simultaneously runnable stages one wave",
    wave_semantics[
        "simultaneously_runnable_stages"
    ] == "one execution wave",
)

check(
    "Within-wave ordering lexical",
    wave_semantics[
        "within_wave_order"
    ] == "lexical deterministic",
)

check(
    "Lexical order evidence-only exact",
    wave_semantics[
        "lexical_order_meaning"
    ] == "serialization and evidence only",
)

check(
    "Forced serial execution false",
    wave_semantics[
        "forced_serial_execution"
    ] is False,
)

check(
    "Artificial dependencies false",
    wave_semantics[
        "artificial_dependencies"
    ] is False,
)

check(
    "Empty runnable set valid",
    wave_semantics[
        "empty_runnable_set"
    ] == "valid empty plan",
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
        runtime_policy[
            key
        ] == "not considered",
    )

check(
    "Runtime job creation false",
    runtime_policy[
        "job_creation"
    ] is False,
)

check(
    "Runtime dispatch false",
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
# 24. Determinism
# =============================================================================

check(
    "Repeated chain plan deterministic",
    create_execution_plan(
        graph,
        resolution,
    )
    == initial_plan,
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
    "Repeated large plan deterministic",
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
# 25. Static import boundary
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
# 26. Forbidden execution authority
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
    "save",
    "persist",
    "commit",
    "checkpoint",
    "recover",
    "resume",
    "pause",
    "select_worker",
    "schedule_stage",
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
# 27. Public API boundary
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
# 28. Source authority boundaries
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
        "Source rejects future prediction",
        "predict future workflow stages",
    ),
    (
        "Source rejects full future topological plan",
        "full remaining-workflow topological plan",
    ),
    (
        "Source rejects artificial dependencies",
        "invent dependencies between simultaneously runnable stages",
    ),
    (
        "Source rejects job dispatch",
        "dispatch jobs",
    ),
    (
        "Source rejects Runtime job creation",
        "create Runtime jobs",
    ),
    (
        "Source rejects worker selection",
        "select workers",
    ),
    (
        "Source rejects Runtime queue inspection",
        "inspect Runtime queue state",
    ),
    (
        "Source rejects Runtime scheduling policy",
        "capacity/priority/retry/resource policy",
    ),
    (
        "Source rejects persistence",
        "persist planning state",
    ),
    (
        "Source says lexical order is evidence only",
        "does not imply forced serial execution",
    ),
    (
        "Source defers planning certification to 4.6",
        "planning certification -> Phase 4.6",
    ),
    (
        "Source defers Runtime to Phase 5",
        "Runtime execution -> Phase 5",
    ),
    (
        "Source defers advanced orchestration to Phase 7",
        "advanced orchestration -> Phase 7",
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
    "PHASE 4.5 — EXECUTION PLANNER INITIAL VERIFICATION",
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
print("=" * 108)
print("PHASE 4.5 INITIAL VERIFICATION RESULT")
print("=" * 108)
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
print("=" * 108)


raise SystemExit(
    0
    if failed == 0
    else 1
)
