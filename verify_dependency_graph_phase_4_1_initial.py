from __future__ import annotations

import ast
import importlib
from dataclasses import fields
from pathlib import Path
from types import MappingProxyType

from backend.server.coordination.dependency_planning.dependency_graph import (
    DEPENDENCY_GRAPH_VERSION,
    DEPENDENCY_GRAPH_SCHEMA_VERSION,
    DEPENDENCY_EDGE_FIELD_COUNT,
    DEPENDENCY_GRAPH_FIELD_COUNT,
    DependencyGraphError,
    InvalidWorkflowIdError,
    InvalidDependencyStageIdError,
    InvalidDependencyEdgeError,
    DependencyEdge,
    DependencyGraph,
    create_dependency_graph,
    dependency_nodes,
    dependency_edges,
    has_dependency_node,
    has_dependency_edge,
    stage_prerequisites,
    stage_dependents,
    dependency_roots,
    dependency_leaves,
    dependency_graph_snapshot,
    explain_dependency_graph_v4_1,
)


ROOT = Path.cwd()

FILE = ROOT / (
    "backend/server/coordination/"
    "dependency_planning/dependency_graph.py"
)

REPORT = ROOT / (
    "dependency_graph_phase_4_1_initial_verification.txt"
)

checks = []


def check(name, condition, detail=""):
    ok = bool(condition)
    checks.append((name, ok, detail))

    print(f"[{'PASS' if ok else 'FAIL'}] {name}")

    if detail:
        print(f"       {detail}")


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


print()
print("=" * 100)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 4.1 — DEPENDENCY GRAPH INITIAL VERIFICATION")
print("=" * 100)


# ============================================================================
# 1. File / syntax / import
# ============================================================================

check(
    "Canonical Phase 4.1 file exists",
    FILE.exists(),
    str(FILE.relative_to(ROOT)),
)

source = FILE.read_text(
    encoding="utf-8-sig"
)

try:
    tree = ast.parse(source)
    syntax_ok = True
except SyntaxError:
    tree = None
    syntax_ok = False

check(
    "Phase 4.1 Python syntax parses",
    syntax_ok,
)

try:
    importlib.import_module(
        "backend.server.coordination."
        "dependency_planning.dependency_graph"
    )
    import_ok = True
except Exception as exc:
    import_ok = False
    import_detail = repr(exc)
else:
    import_detail = ""

check(
    "Phase 4.1 module imports successfully",
    import_ok,
    import_detail,
)


# ============================================================================
# 2. Canonical identity
# ============================================================================

check(
    "Dependency Graph version exact",
    DEPENDENCY_GRAPH_VERSION
    == "dependency_graph_v4.1.0",
)

check(
    "Dependency Graph schema exact",
    DEPENDENCY_GRAPH_SCHEMA_VERSION
    == "dependency_graph_schema_v1",
)

check(
    "DependencyEdge field-count constant exact",
    DEPENDENCY_EDGE_FIELD_COUNT == 2,
)

check(
    "DependencyGraph field-count constant exact",
    DEPENDENCY_GRAPH_FIELD_COUNT == 4,
)


# ============================================================================
# 3. Exact dataclass contracts
# ============================================================================

edge_fields = tuple(
    field.name
    for field
    in fields(DependencyEdge)
)

graph_fields = tuple(
    field.name
    for field
    in fields(DependencyGraph)
)

check(
    "DependencyEdge has exactly 2 fields",
    len(edge_fields) == 2,
)

check(
    "DependencyEdge field order exact",
    edge_fields
    == (
        "prerequisite_stage_id",
        "dependent_stage_id",
    ),
)

check(
    "DependencyGraph has exactly 4 fields",
    len(graph_fields) == 4,
)

check(
    "DependencyGraph field order exact",
    graph_fields
    == (
        "workflow_id",
        "node_ids",
        "edges",
        "graph_version",
    ),
)


# ============================================================================
# 4. Canonical edge behavior
# ============================================================================

edge = DependencyEdge(
    " stage-a ",
    " stage-b ",
)

check(
    "DependencyEdge normalizes prerequisite stage_id",
    edge.prerequisite_stage_id == "stage-a",
)

check(
    "DependencyEdge normalizes dependent stage_id",
    edge.dependent_stage_id == "stage-b",
)

check(
    "DependencyEdge tuple representation exact",
    edge.to_tuple()
    == (
        "stage-a",
        "stage-b",
    ),
)

edge_mapping = edge.to_dict()

check(
    "DependencyEdge mapping immutable",
    isinstance(
        edge_mapping,
        MappingProxyType,
    ),
)

edge_mapping_mutation_blocked = False

try:
    edge_mapping[
        "dependent_stage_id"
    ] = "changed"
except Exception:
    edge_mapping_mutation_blocked = True

check(
    "DependencyEdge mapping mutation blocked",
    edge_mapping_mutation_blocked,
)

edge_attribute_mutation_blocked = False

try:
    edge.dependent_stage_id = "changed"
except Exception:
    edge_attribute_mutation_blocked = True

check(
    "DependencyEdge dataclass immutable",
    edge_attribute_mutation_blocked,
)


# ============================================================================
# 5. Invalid edge/stage input handling
# ============================================================================

for label, value in (
    ("None", None),
    ("empty", ""),
    ("whitespace", "   "),
    ("integer", 123),
    ("list", []),
    ("mapping", {}),
):
    expect_exception(
        f"Invalid prerequisite stage_id rejected: {label}",
        InvalidDependencyStageIdError,
        lambda value=value: DependencyEdge(
            value,
            "stage-b",
        ),
    )

    expect_exception(
        f"Invalid dependent stage_id rejected: {label}",
        InvalidDependencyStageIdError,
        lambda value=value: DependencyEdge(
            "stage-a",
            value,
        ),
    )


for label, value in (
    ("scalar string", "stage-a"),
    ("bytes", b"stage-a"),
    ("one-item tuple", ("stage-a",)),
    (
        "three-item tuple",
        (
            "stage-a",
            "stage-b",
            "stage-c",
        ),
    ),
    ("mapping", {}),
):
    expect_exception(
        f"Invalid dependency edge representation rejected: {label}",
        InvalidDependencyEdgeError,
        lambda value=value: create_dependency_graph(
            workflow_id="workflow-a",
            edges=(value,),
        ),
    )


# ============================================================================
# 6. Workflow identity handling
# ============================================================================

for label, value in (
    ("None", None),
    ("empty", ""),
    ("whitespace", "   "),
    ("integer", 123),
    ("list", []),
):
    expect_exception(
        f"Invalid workflow_id rejected: {label}",
        InvalidWorkflowIdError,
        lambda value=value: create_dependency_graph(
            workflow_id=value,
        ),
    )


normalized_workflow = create_dependency_graph(
    workflow_id=" workflow-a ",
)

check(
    "workflow_id normalized",
    normalized_workflow.workflow_id
    == "workflow-a",
)


# ============================================================================
# 7. Empty graph
# ============================================================================

empty_graph = create_dependency_graph(
    workflow_id="empty-workflow",
)

check(
    "Empty graph supports zero nodes",
    empty_graph.node_ids == (),
)

check(
    "Empty graph supports zero edges",
    empty_graph.edges == (),
)

check(
    "Empty graph roots empty",
    dependency_roots(
        empty_graph
    ) == (),
)

check(
    "Empty graph leaves empty",
    dependency_leaves(
        empty_graph
    ) == (),
)


# ============================================================================
# 8. Canonicalization / deterministic topology
# ============================================================================

graph = create_dependency_graph(
    workflow_id="workflow-main",
    node_ids=(
        "stage-z",
        "stage-a",
        "isolated",
        "stage-a",
    ),
    edges=(
        ("stage-c", "stage-d"),
        ("stage-a", "stage-b"),
        ("stage-b", "stage-c"),
        ("stage-a", "stage-b"),
    ),
)

check(
    "Graph node set canonicalized",
    graph.node_ids
    == (
        "isolated",
        "stage-a",
        "stage-b",
        "stage-c",
        "stage-d",
        "stage-z",
    ),
)

check(
    "Graph edge set canonicalized",
    tuple(
        edge.to_tuple()
        for edge
        in graph.edges
    )
    == (
        (
            "stage-a",
            "stage-b",
        ),
        (
            "stage-b",
            "stage-c",
        ),
        (
            "stage-c",
            "stage-d",
        ),
    ),
)

check(
    "Exact duplicate edge removed",
    len(graph.edges) == 3,
)

check(
    "Edge endpoints inferred into nodes",
    all(
        stage_id in graph.node_ids
        for stage_id
        in (
            "stage-b",
            "stage-c",
            "stage-d",
        )
    ),
)

check(
    "Explicit isolated node retained",
    "isolated"
    in graph.node_ids,
)


# ============================================================================
# 9. Direct DependencyGraph construction canonicalization
# ============================================================================

direct_graph = DependencyGraph(
    workflow_id=" direct ",
    node_ids=(
        "z",
        "a",
        "a",
    ),
    edges=(
        DependencyEdge(
            "z",
            "m",
        ),
        DependencyEdge(
            "z",
            "m",
        ),
    ),
)

check(
    "Direct graph workflow_id normalized",
    direct_graph.workflow_id == "direct",
)

check(
    "Direct graph nodes canonicalized",
    direct_graph.node_ids
    == (
        "a",
        "m",
        "z",
    ),
)

check(
    "Direct graph edges canonicalized",
    len(
        direct_graph.edges
    ) == 1,
)

expect_exception(
    "Non-canonical graph_version rejected",
    DependencyGraphError,
    lambda: DependencyGraph(
        workflow_id="workflow",
        node_ids=(),
        edges=(),
        graph_version="wrong-version",
    ),
)


# ============================================================================
# 10. Inspection APIs
# ============================================================================

check(
    "dependency_nodes returns exact canonical tuple",
    dependency_nodes(graph)
    == graph.node_ids,
)

check(
    "dependency_edges returns exact canonical tuple",
    dependency_edges(graph)
    == graph.edges,
)

check(
    "Existing node membership true",
    has_dependency_node(
        graph,
        "stage-c",
    ),
)

check(
    "Absent node membership false",
    not has_dependency_node(
        graph,
        "missing-stage",
    ),
)

check(
    "Existing edge membership true",
    has_dependency_edge(
        graph,
        "stage-a",
        "stage-b",
    ),
)

check(
    "Absent edge membership false",
    not has_dependency_edge(
        graph,
        "stage-a",
        "stage-d",
    ),
)

check(
    "stage_prerequisites exact",
    stage_prerequisites(
        graph,
        "stage-c",
    )
    == (
        "stage-b",
    ),
)

check(
    "stage_dependents exact",
    stage_dependents(
        graph,
        "stage-a",
    )
    == (
        "stage-b",
    ),
)

check(
    "Unknown stage prerequisites empty",
    stage_prerequisites(
        graph,
        "missing-stage",
    ) == (),
)

check(
    "Unknown stage dependents empty",
    stage_dependents(
        graph,
        "missing-stage",
    ) == (),
)


# ============================================================================
# 11. Roots / leaves
# ============================================================================

roots = dependency_roots(
    graph
)

leaves = dependency_leaves(
    graph
)

check(
    "Structural roots exact",
    roots
    == (
        "isolated",
        "stage-a",
        "stage-z",
    ),
)

check(
    "Structural leaves exact",
    leaves
    == (
        "isolated",
        "stage-d",
        "stage-z",
    ),
)


# ============================================================================
# 12. Self-edge representation belongs structurally to 4.1
# ============================================================================

self_graph = create_dependency_graph(
    workflow_id="self-edge-workflow",
    edges=(
        (
            "stage-self",
            "stage-self",
        ),
    ),
)

check(
    "Self-edge retained structurally",
    self_graph.edges
    == (
        DependencyEdge(
            "stage-self",
            "stage-self",
        ),
    ),
)

check(
    "Self-edge node inferred once",
    self_graph.node_ids
    == (
        "stage-self",
    ),
)

check(
    "Self-edge graph has no structural root",
    dependency_roots(
        self_graph
    ) == (),
)

check(
    "Self-edge graph has no structural leaf",
    dependency_leaves(
        self_graph
    ) == (),
)


# ============================================================================
# 13. Cycle representation belongs structurally to 4.1
# ============================================================================

cycle_graph = create_dependency_graph(
    workflow_id="cycle-workflow",
    edges=(
        (
            "stage-a",
            "stage-b",
        ),
        (
            "stage-b",
            "stage-c",
        ),
        (
            "stage-c",
            "stage-a",
        ),
    ),
)

check(
    "Three-edge cycle retained structurally",
    len(
        cycle_graph.edges
    ) == 3,
)

check(
    "Cycle graph has no structural root",
    dependency_roots(
        cycle_graph
    ) == (),
)

check(
    "Cycle graph has no structural leaf",
    dependency_leaves(
        cycle_graph
    ) == (),
)


# ============================================================================
# 14. Determinism across input orderings
# ============================================================================

graph_a = create_dependency_graph(
    workflow_id="determinism",
    node_ids=(
        "isolated",
        "c",
        "a",
    ),
    edges=(
        ("b", "c"),
        ("a", "b"),
    ),
)

graph_b = create_dependency_graph(
    workflow_id="determinism",
    node_ids=(
        "a",
        "isolated",
        "c",
    ),
    edges=(
        ("a", "b"),
        ("b", "c"),
    ),
)

check(
    "Equivalent unordered inputs produce equal graphs",
    graph_a == graph_b,
)

check(
    "Equivalent unordered inputs produce equal node tuples",
    graph_a.node_ids
    == graph_b.node_ids,
)

check(
    "Equivalent unordered inputs produce equal edge tuples",
    graph_a.edges
    == graph_b.edges,
)


# ============================================================================
# 15. Snapshot
# ============================================================================

snapshot = dependency_graph_snapshot(
    graph
)

check(
    "Snapshot is MappingProxyType",
    isinstance(
        snapshot,
        MappingProxyType,
    ),
)

check(
    "Snapshot workflow_id exact",
    snapshot["workflow_id"]
    == "workflow-main",
)

check(
    "Snapshot version exact",
    snapshot["graph_version"]
    == DEPENDENCY_GRAPH_VERSION,
)

check(
    "Snapshot schema exact",
    snapshot["schema_version"]
    == DEPENDENCY_GRAPH_SCHEMA_VERSION,
)

check(
    "Snapshot node count exact",
    snapshot["node_count"]
    == len(
        graph.node_ids
    ),
)

check(
    "Snapshot edge count exact",
    snapshot["edge_count"]
    == len(
        graph.edges
    ),
)

check(
    "Snapshot node_ids exact",
    snapshot["node_ids"]
    == graph.node_ids,
)

check(
    "Snapshot roots exact",
    snapshot["roots"]
    == roots,
)

check(
    "Snapshot leaves exact",
    snapshot["leaves"]
    == leaves,
)

snapshot_mutation_blocked = False

try:
    snapshot["node_count"] = 999
except Exception:
    snapshot_mutation_blocked = True

check(
    "Snapshot top-level mutation blocked",
    snapshot_mutation_blocked,
)


# ============================================================================
# 16. Architecture explanation / deep immutability
# ============================================================================

architecture = explain_dependency_graph_v4_1()

check(
    "Architecture explanation MappingProxyType",
    isinstance(
        architecture,
        MappingProxyType,
    ),
)

check(
    "Architecture phase exact",
    architecture["phase"]
    == "4.1",
)

check(
    "Architecture component exact",
    architecture["component"]
    == "Dependency Graph",
)

check(
    "Architecture version exact",
    architecture["version"]
    == DEPENDENCY_GRAPH_VERSION,
)

check(
    "Architecture schema exact",
    architecture["schema_version"]
    == DEPENDENCY_GRAPH_SCHEMA_VERSION,
)

check(
    "Architecture edge direction exact",
    architecture["edge_direction"]
    == (
        "prerequisite_stage_id"
        " -> "
        "dependent_stage_id"
    ),
)

check(
    "Architecture graph scope exact",
    architecture["graph_scope"]
    == "workflow",
)

check(
    "Architecture graph identity exact",
    architecture["graph_identity"]
    == "workflow_id",
)

check(
    "Architecture node identity exact",
    architecture["node_identity"]
    == "stage_id",
)


future = architecture[
    "future_authority"
]

check(
    "Future authority mapping immutable",
    isinstance(
        future,
        MappingProxyType,
    ),
)

for phase, component in (
    (
        "4.2",
        "Dependency Validation",
    ),
    (
        "4.3",
        "Cycle Detection",
    ),
    (
        "4.4",
        "Runnable Stage Resolver",
    ),
    (
        "4.5",
        "Execution Planner",
    ),
    (
        "4.6",
        "Planning Certification",
    ),
):
    check(
        f"Future authority exact: {phase}",
        future[phase]
        == component,
    )


future_mutation_blocked = False

try:
    future["4.2"] = "MUTATED"
except Exception:
    future_mutation_blocked = True

check(
    "Future authority nested mutation blocked",
    future_mutation_blocked,
)


rules = architecture[
    "structural_rules"
]

check(
    "Structural rules mapping immutable",
    isinstance(
        rules,
        MappingProxyType,
    ),
)

check(
    "Duplicate-edge structural rule exact",
    rules[
        "exact_duplicate_edges"
    ]
    == "canonicalize_to_one",
)

check(
    "Isolated-node structural rule exact",
    rules[
        "isolated_nodes"
    ]
    == "supported",
)

check(
    "Self-edge authority deferred to 4.2",
    rules[
        "self_edges"
    ]
    == (
        "representable; "
        "Phase 4.2 owns validity"
    ),
)

check(
    "Cycle authority deferred to 4.3",
    rules[
        "cycles"
    ]
    == (
        "representable; "
        "Phase 4.3 owns detection"
    ),
)


execution = architecture[
    "execution_properties"
]

check(
    "Execution properties mapping immutable",
    isinstance(
        execution,
        MappingProxyType,
    ),
)

check(
    "Architecture declares read_only=True",
    execution["read_only"] is True,
)

check(
    "Architecture declares deterministic=True",
    execution["deterministic"] is True,
)

check(
    "Architecture declares side_effect_free=True",
    execution["side_effect_free"] is True,
)

check(
    "Architecture declares runtime_execution=False",
    execution[
        "runtime_execution"
    ] is False,
)

check(
    "Architecture declares workflow_mutation=False",
    execution[
        "workflow_mutation"
    ] is False,
)

check(
    "Architecture declares persistence=False",
    execution[
        "persistence"
    ] is False,
)


# ============================================================================
# 17. Architecture determinism
# ============================================================================

architecture_again = (
    explain_dependency_graph_v4_1()
)

check(
    "Repeated architecture explanation deterministic",
    dict(
        architecture_again
    )
    == dict(
        architecture
    ),
)

snapshot_again = dependency_graph_snapshot(
    graph
)

check(
    "Repeated graph snapshot deterministic",
    dict(
        snapshot_again
    )
    == dict(
        snapshot
    ),
)


# ============================================================================
# 18. Static authority boundary
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


check(
    "4.1 has no backend subsystem imports",
    backend_imports == [],
    repr(
        backend_imports
    ),
)


forbidden_call_names = {
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
    "topological_sort",
    "resolve_runnable",
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
            call_name = func.id

        elif isinstance(
            func,
            ast.Attribute,
        ):
            call_name = func.attr

        else:
            continue

        if call_name in forbidden_call_names:
            bad_calls.append(
                call_name
            )


check(
    "4.1 performs no Runtime/planning/persistence execution",
    not bad_calls,
    repr(
        bad_calls
    ),
)


# ============================================================================
# 19. Phase boundary source checks
# ============================================================================

check(
    "Source explicitly defers semantic validation to 4.2",
    "semantic dependency validity (Phase 4.2)"
    in source,
)

check(
    "Source explicitly defers cycle detection to 4.3",
    "cycle detection (Phase 4.3)"
    in source,
)

check(
    "Source explicitly defers runnable resolution to 4.4",
    "runnable-stage resolution (Phase 4.4)"
    in source,
)

check(
    "Source explicitly defers execution planning to 4.5",
    "execution planning (Phase 4.5)"
    in source,
)

check(
    "Source explicitly excludes Runtime execution",
    "Runtime dispatch or job execution (Phase 5)"
    in source,
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

failed = len(
    checks
) - passed

report_lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 4.1 — DEPENDENCY GRAPH INITIAL VERIFICATION",
    "=" * 100,
    "",
    (
        "Dependency Graph Version: "
        + DEPENDENCY_GRAPH_VERSION
    ),
    (
        "Dependency Graph Schema: "
        + DEPENDENCY_GRAPH_SCHEMA_VERSION
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
print("=" * 100)
print("PHASE 4.1 INITIAL VERIFICATION RESULT")
print("=" * 100)
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
print("REPORT:", REPORT.name)
print("=" * 100)

raise SystemExit(
    0
    if failed == 0
    else 1
)
