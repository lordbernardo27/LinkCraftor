from __future__ import annotations

import ast
import hashlib
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

PHASE_35 = ROOT / (
    "backend/server/coordination/"
    "workflow_lifecycle/lifecycle_certification.py"
)

REPORT = ROOT / (
    "dependency_graph_phase_4_1_final_certification.txt"
)


EXPECTED_PHASE_35_SHA = (
    "0A1F2BCFFCFFC56AC96F7383AF3ACCEA"
    "61314952D59CC0CC8A58B1FA0B9060DF"
)

EXPECTED_PHASE_3_COMPOSITE = (
    "63A2038DF85AFC3BF621AAC13FEECF29"
    "F0B3E672E2B3590CF29401D3FB6790FE"
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


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


print()
print("=" * 104)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 4.1 — DEPENDENCY GRAPH FINAL CERTIFICATION")
print("=" * 104)


# ============================================================================
# 1. Canonical files / syntax / imports
# ============================================================================

check(
    "Canonical Phase 4.1 file exists",
    FILE.exists(),
    str(FILE.relative_to(ROOT)),
)

check(
    "Frozen Phase 3.5 file exists",
    PHASE_35.exists(),
    str(PHASE_35.relative_to(ROOT)),
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
    import_detail = ""

except Exception as exc:
    import_ok = False
    import_detail = repr(exc)

check(
    "Phase 4.1 module imports successfully",
    import_ok,
    import_detail,
)


# ============================================================================
# 2. Frozen Phase 3 downstream integrity
# ============================================================================

actual_phase_35_sha = sha256(
    PHASE_35
)

check(
    "Frozen Phase 3.5 SHA unchanged",
    actual_phase_35_sha
    == EXPECTED_PHASE_35_SHA,
    actual_phase_35_sha,
)


from backend.server.coordination.workflow_lifecycle.lifecycle_certification import (
    PHASE_3_COMPOSITE_FINGERPRINT,
    certify_workflow_lifecycle,
)


check(
    "Frozen Phase 3 composite fingerprint unchanged",
    PHASE_3_COMPOSITE_FINGERPRINT
    == EXPECTED_PHASE_3_COMPOSITE,
    PHASE_3_COMPOSITE_FINGERPRINT,
)


phase_3_result = certify_workflow_lifecycle()

check(
    "Frozen Phase 3 remains certified",
    phase_3_result.is_certified is True,
)

check(
    "Frozen Phase 3 still reports zero failures",
    phase_3_result.checks_failed == 0,
)

check(
    "Frozen Phase 3 built-in certification remains 330/330",
    (
        phase_3_result.checks_run == 330
        and phase_3_result.checks_passed == 330
    ),
)


# ============================================================================
# 3. Canonical identity
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
# 4. Exact dataclass contracts
# ============================================================================

edge_fields = tuple(
    item.name
    for item
    in fields(DependencyEdge)
)

graph_fields = tuple(
    item.name
    for item
    in fields(DependencyGraph)
)


check(
    "DependencyEdge field count exact",
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
    "DependencyGraph field count exact",
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
# 5. Edge normalization and immutability
# ============================================================================

edge = DependencyEdge(
    " prerequisite ",
    " dependent ",
)

check(
    "Edge prerequisite normalized",
    edge.prerequisite_stage_id
    == "prerequisite",
)

check(
    "Edge dependent normalized",
    edge.dependent_stage_id
    == "dependent",
)

check(
    "Edge tuple exact",
    edge.to_tuple()
    == (
        "prerequisite",
        "dependent",
    ),
)

edge_dict = edge.to_dict()

check(
    "Edge mapping immutable",
    isinstance(
        edge_dict,
        MappingProxyType,
    ),
)


blocked = False

try:
    edge_dict[
        "dependent_stage_id"
    ] = "changed"

except Exception:
    blocked = True

check(
    "Edge mapping mutation blocked",
    blocked,
)


blocked = False

try:
    edge.dependent_stage_id = "changed"

except Exception:
    blocked = True

check(
    "DependencyEdge object immutable",
    blocked,
)


# ============================================================================
# 6. Invalid inputs
# ============================================================================

for label, value in (
    ("None", None),
    ("empty", ""),
    ("whitespace", "   "),
    ("integer", 123),
    ("float", 1.5),
    ("list", []),
    ("mapping", {}),
):
    expect_exception(
        f"Invalid prerequisite stage rejected: {label}",
        InvalidDependencyStageIdError,
        lambda value=value: DependencyEdge(
            value,
            "stage-b",
        ),
    )

    expect_exception(
        f"Invalid dependent stage rejected: {label}",
        InvalidDependencyStageIdError,
        lambda value=value: DependencyEdge(
            "stage-a",
            value,
        ),
    )


for label, value in (
    ("scalar string", "stage-a"),
    ("bytes", b"stage-a"),
    ("empty tuple", ()),
    ("one item", ("stage-a",)),
    (
        "three items",
        (
            "stage-a",
            "stage-b",
            "stage-c",
        ),
    ),
    ("mapping", {}),
    ("integer", 123),
):
    expect_exception(
        f"Invalid edge representation rejected: {label}",
        InvalidDependencyEdgeError,
        lambda value=value: create_dependency_graph(
            workflow_id="workflow",
            edges=(value,),
        ),
    )


for label, value in (
    ("None", None),
    ("empty", ""),
    ("whitespace", "   "),
    ("integer", 123),
    ("float", 1.5),
    ("list", []),
    ("mapping", {}),
):
    expect_exception(
        f"Invalid workflow_id rejected: {label}",
        InvalidWorkflowIdError,
        lambda value=value: create_dependency_graph(
            workflow_id=value,
        ),
    )


# ============================================================================
# 7. Empty graph
# ============================================================================

empty_graph = create_dependency_graph(
    workflow_id="empty-workflow",
)

check(
    "Empty graph node set empty",
    empty_graph.node_ids == (),
)

check(
    "Empty graph edge set empty",
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
# 8. Large deterministic topology
# ============================================================================

node_ids = tuple(
    f"stage-{index:03d}"
    for index
    in range(100)
)

edges = tuple(
    (
        f"stage-{index:03d}",
        f"stage-{index + 1:03d}",
    )
    for index
    in range(99)
)

large_graph = create_dependency_graph(
    workflow_id="large-workflow",
    node_ids=reversed(
        node_ids
    ),
    edges=reversed(
        edges
        + edges
    ),
)

check(
    "100-node graph canonicalized",
    len(
        large_graph.node_ids
    ) == 100,
)

check(
    "99 unique edges canonicalized",
    len(
        large_graph.edges
    ) == 99,
)

check(
    "Large graph lexical node ordering deterministic",
    large_graph.node_ids
    == node_ids,
)

check(
    "Large graph root exact",
    dependency_roots(
        large_graph
    )
    == (
        "stage-000",
    ),
)

check(
    "Large graph leaf exact",
    dependency_leaves(
        large_graph
    )
    == (
        "stage-099",
    ),
)


for index in range(
    1,
    99,
):
    stage = (
        f"stage-{index:03d}"
    )

    expected_previous = (
        f"stage-{index - 1:03d}"
    )

    expected_next = (
        f"stage-{index + 1:03d}"
    )

    check(
        (
            "Large graph prerequisite exact: "
            + stage
        ),
        stage_prerequisites(
            large_graph,
            stage,
        )
        == (
            expected_previous,
        ),
    )

    check(
        (
            "Large graph dependent exact: "
            + stage
        ),
        stage_dependents(
            large_graph,
            stage,
        )
        == (
            expected_next,
        ),
    )


# ============================================================================
# 9. Branching topology
# ============================================================================

branch_graph = create_dependency_graph(
    workflow_id="branch-workflow",
    edges=(
        (
            "start",
            "branch-a",
        ),
        (
            "start",
            "branch-b",
        ),
        (
            "start",
            "branch-c",
        ),
        (
            "branch-a",
            "join",
        ),
        (
            "branch-b",
            "join",
        ),
        (
            "branch-c",
            "join",
        ),
    ),
)

check(
    "Branch graph root exact",
    dependency_roots(
        branch_graph
    )
    == (
        "start",
    ),
)

check(
    "Branch graph leaf exact",
    dependency_leaves(
        branch_graph
    )
    == (
        "join",
    ),
)

check(
    "Branch dependents lexical and exact",
    stage_dependents(
        branch_graph,
        "start",
    )
    == (
        "branch-a",
        "branch-b",
        "branch-c",
    ),
)

check(
    "Join prerequisites lexical and exact",
    stage_prerequisites(
        branch_graph,
        "join",
    )
    == (
        "branch-a",
        "branch-b",
        "branch-c",
    ),
)


# ============================================================================
# 10. Isolated nodes
# ============================================================================

isolated_graph = create_dependency_graph(
    workflow_id="isolated-workflow",
    node_ids=(
        "isolated-b",
        "isolated-a",
    ),
    edges=(
        (
            "stage-a",
            "stage-b",
        ),
    ),
)

check(
    "Isolated nodes preserved",
    isolated_graph.node_ids
    == (
        "isolated-a",
        "isolated-b",
        "stage-a",
        "stage-b",
    ),
)

check(
    "Isolated nodes are structural roots",
    dependency_roots(
        isolated_graph
    )
    == (
        "isolated-a",
        "isolated-b",
        "stage-a",
    ),
)

check(
    "Isolated nodes are structural leaves",
    dependency_leaves(
        isolated_graph
    )
    == (
        "isolated-a",
        "isolated-b",
        "stage-b",
    ),
)


# ============================================================================
# 11. Self-edge remains representable
# ============================================================================

self_graph = create_dependency_graph(
    workflow_id="self-workflow",
    edges=(
        (
            "self",
            "self",
        ),
    ),
)

check(
    "Self-edge retained",
    has_dependency_edge(
        self_graph,
        "self",
        "self",
    ),
)

check(
    "Self-edge node canonicalized once",
    self_graph.node_ids
    == (
        "self",
    ),
)

check(
    "Self-edge has no structural root",
    dependency_roots(
        self_graph
    ) == (),
)

check(
    "Self-edge has no structural leaf",
    dependency_leaves(
        self_graph
    ) == (),
)


# ============================================================================
# 12. Cycles remain representable
# ============================================================================

two_cycle = create_dependency_graph(
    workflow_id="cycle-two",
    edges=(
        (
            "a",
            "b",
        ),
        (
            "b",
            "a",
        ),
    ),
)

check(
    "Two-node cycle retained",
    len(
        two_cycle.edges
    ) == 2,
)

check(
    "Two-node cycle has no roots",
    dependency_roots(
        two_cycle
    ) == (),
)

check(
    "Two-node cycle has no leaves",
    dependency_leaves(
        two_cycle
    ) == (),
)


three_cycle = create_dependency_graph(
    workflow_id="cycle-three",
    edges=(
        (
            "a",
            "b",
        ),
        (
            "b",
            "c",
        ),
        (
            "c",
            "a",
        ),
    ),
)

check(
    "Three-node cycle retained",
    len(
        three_cycle.edges
    ) == 3,
)


# ============================================================================
# 13. Deterministic canonical equality
# ============================================================================

graph_a = create_dependency_graph(
    workflow_id="determinism",
    node_ids=(
        "z",
        "a",
        "isolated",
    ),
    edges=(
        (
            "a",
            "b",
        ),
        (
            "b",
            "c",
        ),
        (
            "c",
            "z",
        ),
    ),
)

graph_b = create_dependency_graph(
    workflow_id="determinism",
    node_ids=(
        "isolated",
        "a",
        "z",
    ),
    edges=(
        (
            "c",
            "z",
        ),
        (
            "b",
            "c",
        ),
        (
            "a",
            "b",
        ),
        (
            "a",
            "b",
        ),
    ),
)

check(
    "Equivalent topology produces equal graphs",
    graph_a == graph_b,
)

check(
    "Equivalent topology produces equal nodes",
    graph_a.node_ids
    == graph_b.node_ids,
)

check(
    "Equivalent topology produces equal edges",
    graph_a.edges
    == graph_b.edges,
)


# ============================================================================
# 14. Direct construction normalization
# ============================================================================

direct = DependencyGraph(
    workflow_id=" workflow-direct ",
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
    "Direct workflow_id normalized",
    direct.workflow_id
    == "workflow-direct",
)

check(
    "Direct nodes canonicalized",
    direct.node_ids
    == (
        "a",
        "m",
        "z",
    ),
)

check(
    "Direct duplicate edges removed",
    len(
        direct.edges
    ) == 1,
)


expect_exception(
    "Invalid graph_version rejected",
    DependencyGraphError,
    lambda: DependencyGraph(
        workflow_id="workflow",
        node_ids=(),
        edges=(),
        graph_version="v999",
    ),
)


# ============================================================================
# 15. Membership / unknown-stage inspection
# ============================================================================

check(
    "Known node membership true",
    has_dependency_node(
        graph_a,
        "b",
    ),
)

check(
    "Unknown node membership false",
    not has_dependency_node(
        graph_a,
        "missing",
    ),
)

check(
    "Known edge membership true",
    has_dependency_edge(
        graph_a,
        "a",
        "b",
    ),
)

check(
    "Unknown edge membership false",
    not has_dependency_edge(
        graph_a,
        "a",
        "z",
    ),
)

check(
    "Unknown prerequisite lookup empty",
    stage_prerequisites(
        graph_a,
        "missing",
    ) == (),
)

check(
    "Unknown dependent lookup empty",
    stage_dependents(
        graph_a,
        "missing",
    ) == (),
)


# ============================================================================
# 16. Snapshot immutability and determinism
# ============================================================================

snapshot = dependency_graph_snapshot(
    branch_graph
)

check(
    "Snapshot MappingProxyType",
    isinstance(
        snapshot,
        MappingProxyType,
    ),
)

check(
    "Snapshot workflow exact",
    snapshot[
        "workflow_id"
    ]
    == "branch-workflow",
)

check(
    "Snapshot graph version exact",
    snapshot[
        "graph_version"
    ]
    == DEPENDENCY_GRAPH_VERSION,
)

check(
    "Snapshot schema exact",
    snapshot[
        "schema_version"
    ]
    == DEPENDENCY_GRAPH_SCHEMA_VERSION,
)

check(
    "Snapshot node count exact",
    snapshot[
        "node_count"
    ]
    == len(
        branch_graph.node_ids
    ),
)

check(
    "Snapshot edge count exact",
    snapshot[
        "edge_count"
    ]
    == len(
        branch_graph.edges
    ),
)

check(
    "Snapshot roots exact",
    snapshot[
        "roots"
    ]
    == (
        "start",
    ),
)

check(
    "Snapshot leaves exact",
    snapshot[
        "leaves"
    ]
    == (
        "join",
    ),
)


blocked = False

try:
    snapshot[
        "node_count"
    ] = 999

except Exception:
    blocked = True

check(
    "Snapshot top-level mutation blocked",
    blocked,
)


snapshot_again = dependency_graph_snapshot(
    branch_graph
)

check(
    "Repeated snapshot deterministic",
    dict(
        snapshot_again
    )
    == dict(
        snapshot
    ),
)


# ============================================================================
# 17. Architecture evidence
# ============================================================================

architecture = explain_dependency_graph_v4_1()

check(
    "Architecture MappingProxyType",
    isinstance(
        architecture,
        MappingProxyType,
    ),
)

check(
    "Architecture phase exact",
    architecture[
        "phase"
    ]
    == "4.1",
)

check(
    "Architecture component exact",
    architecture[
        "component"
    ]
    == "Dependency Graph",
)

check(
    "Architecture version exact",
    architecture[
        "version"
    ]
    == DEPENDENCY_GRAPH_VERSION,
)

check(
    "Architecture schema exact",
    architecture[
        "schema_version"
    ]
    == DEPENDENCY_GRAPH_SCHEMA_VERSION,
)

check(
    "Architecture edge direction exact",
    architecture[
        "edge_direction"
    ]
    == (
        "prerequisite_stage_id"
        " -> "
        "dependent_stage_id"
    ),
)

check(
    "Architecture workflow scope exact",
    architecture[
        "graph_scope"
    ]
    == "workflow",
)

check(
    "Architecture graph identity exact",
    architecture[
        "graph_identity"
    ]
    == "workflow_id",
)

check(
    "Architecture node identity exact",
    architecture[
        "node_identity"
    ]
    == "stage_id",
)


future = architecture[
    "future_authority"
]

check(
    "Future authority MappingProxyType",
    isinstance(
        future,
        MappingProxyType,
    ),
)

expected_future = {
    "4.2":
        "Dependency Validation",

    "4.3":
        "Cycle Detection",

    "4.4":
        "Runnable Stage Resolver",

    "4.5":
        "Execution Planner",

    "4.6":
        "Planning Certification",
}

check(
    "Future authority exact",
    dict(
        future
    )
    == expected_future,
)


blocked = False

try:
    future[
        "4.2"
    ] = "MUTATED"

except Exception:
    blocked = True

check(
    "Future authority nested mutation blocked",
    blocked,
)


rules = architecture[
    "structural_rules"
]

check(
    "Structural rules immutable",
    isinstance(
        rules,
        MappingProxyType,
    ),
)

check(
    "Self-edge remains Phase 4.2 validity authority",
    rules[
        "self_edges"
    ]
    == (
        "representable; "
        "Phase 4.2 owns validity"
    ),
)

check(
    "Cycle remains Phase 4.3 detection authority",
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
    "Execution properties immutable",
    isinstance(
        execution,
        MappingProxyType,
    ),
)

check(
    "Phase 4.1 read-only",
    execution[
        "read_only"
    ] is True,
)

check(
    "Phase 4.1 deterministic",
    execution[
        "deterministic"
    ] is True,
)

check(
    "Phase 4.1 side-effect free",
    execution[
        "side_effect_free"
    ] is True,
)

check(
    "Phase 4.1 runtime execution disabled",
    execution[
        "runtime_execution"
    ] is False,
)

check(
    "Phase 4.1 workflow mutation disabled",
    execution[
        "workflow_mutation"
    ] is False,
)

check(
    "Phase 4.1 persistence disabled",
    execution[
        "persistence"
    ] is False,
)


architecture_again = (
    explain_dependency_graph_v4_1()
)

check(
    "Architecture explanation deterministic",
    dict(
        architecture_again
    )
    == dict(
        architecture
    ),
)


# ============================================================================
# 18. Static architecture boundary
# ============================================================================

backend_imports = []

if tree is not None:

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


check(
    "4.1 has zero backend subsystem imports",
    backend_imports == [],
    repr(
        backend_imports
    ),
)


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
    "topological_sort",
    "resolve_runnable",
    "plan_execution",
}

bad_calls = []

if tree is not None:

    for node in ast.walk(
        tree
    ):

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
    "4.1 performs no forbidden execution/planning/persistence work",
    not bad_calls,
    repr(
        bad_calls
    ),
)


# ============================================================================
# 19. Source-level phase boundary
# ============================================================================

check(
    "Source assigns semantic validity to Phase 4.2",
    (
        "semantic dependency validity (Phase 4.2)"
        in source
    ),
)

check(
    "Source assigns self-dependency rejection to Phase 4.2",
    (
        "self-dependency rejection (Phase 4.2)"
        in source
    ),
)

check(
    "Source assigns cycle detection to Phase 4.3",
    (
        "cycle detection (Phase 4.3)"
        in source
    ),
)

check(
    "Source assigns runnable resolution to Phase 4.4",
    (
        "runnable-stage resolution (Phase 4.4)"
        in source
    ),
)

check(
    "Source assigns execution planning to Phase 4.5",
    (
        "execution planning (Phase 4.5)"
        in source
    ),
)

check(
    "Source excludes Runtime execution until Phase 5",
    (
        "Runtime dispatch or job execution (Phase 5)"
        in source
    ),
)

check(
    "Source excludes stage handoff until Phase 6",
    (
        "stage handoff (Phase 6)"
        in source
    ),
)

check(
    "Source excludes persistence until Phase 8",
    (
        "workflow persistence (Phase 8)"
        in source
    ),
)

check(
    "Source excludes recovery until Phase 9",
    (
        "recovery (Phase 9)"
        in source
    ),
)


# ============================================================================
# 20. Canonical Phase 4.1 SHA
# ============================================================================

phase_41_sha = sha256(
    FILE
)

print()
print(
    "PHASE 4.1 SHA256 CANDIDATE:"
)
print(
    phase_41_sha
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
    "PHASE 4.1 — DEPENDENCY GRAPH FINAL CERTIFICATION",
    "=" * 104,
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
    (
        "Frozen Phase 3.5 SHA256: "
        + actual_phase_35_sha
    ),
    (
        "Frozen Phase 3 Composite: "
        + PHASE_3_COMPOSITE_FINGERPRINT
    ),
    "",
    (
        "Phase 4.1 SHA256: "
        + phase_41_sha
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
print("=" * 104)
print("PHASE 4.1 FINAL CERTIFICATION RESULT")
print("=" * 104)
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
    phase_41_sha,
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
