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
    CYCLE_DETECTION_SCHEMA_VERSION,
    CYCLE_DETECTION_RESULT_FIELD_COUNT,
    CycleDetectionError,
    InvalidCycleDetectionRequestError,
    CyclicDependencyGraphError,
    CycleWitness,
    CycleDetectionResult,
    detect_dependency_cycles,
    require_acyclic_dependency_graph,
    cycle_detection_snapshot,
    explain_cycle_detection_v4_3,
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

REPORT = ROOT / (
    "cycle_detection_phase_4_3_initial_verification.txt"
)


EXPECTED_41_SHA = (
    "4F6BA62D011C31D9D851FBBABC37C12B"
    "7DDAA1FD9A91E34788EBCE25741A1F70"
)

EXPECTED_42_SHA = (
    "1D053C0036EA9F7A8AEDFAFC36F6EB82"
    "A681EDC7EF206409E9FFB8C7F212852D"
)

EXPECTED_43_CANDIDATE_SHA = (
    "E77BF605724F991E85C7FE2E5329051E"
    "16ECB2F30ACDAEA8AA40A2FD47487CEA"
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
print("=" * 100)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 4.3 — CYCLE DETECTION INITIAL VERIFICATION")
print("=" * 100)


# ============================================================================
# 1. Files / syntax / imports
# ============================================================================

check(
    "Canonical Phase 4.3 file exists",
    PHASE_43.exists(),
    str(
        PHASE_43.relative_to(ROOT)
    ),
)

source = PHASE_43.read_text(
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
    "Phase 4.3 Python syntax parses",
    syntax_ok,
)

try:
    importlib.import_module(
        "backend.server.coordination."
        "dependency_planning.cycle_detection"
    )
    import_ok = True
    import_detail = ""

except Exception as exc:
    import_ok = False
    import_detail = repr(exc)

check(
    "Phase 4.3 module imports successfully",
    import_ok,
    import_detail,
)


# ============================================================================
# 2. Frozen upstream integrity
# ============================================================================

actual_41_sha = sha256(
    PHASE_41
)

actual_42_sha = sha256(
    PHASE_42
)

actual_43_sha = sha256(
    PHASE_43
)

check(
    "Frozen Phase 4.1 SHA exact",
    actual_41_sha
    == EXPECTED_41_SHA,
    actual_41_sha,
)

check(
    "Frozen Phase 4.2 SHA exact",
    actual_42_sha
    == EXPECTED_42_SHA,
    actual_42_sha,
)

check(
    "Phase 4.3 candidate SHA unchanged",
    actual_43_sha
    == EXPECTED_43_CANDIDATE_SHA,
    actual_43_sha,
)


# ============================================================================
# 3. Canonical identity
# ============================================================================

check(
    "Cycle Detection version exact",
    CYCLE_DETECTION_VERSION
    == "cycle_detection_v4.3.0",
)

check(
    "Cycle Detection schema exact",
    CYCLE_DETECTION_SCHEMA_VERSION
    == "cycle_detection_schema_v1",
)

check(
    "Cycle Detection result field-count constant exact",
    CYCLE_DETECTION_RESULT_FIELD_COUNT
    == 8,
)


# ============================================================================
# 4. Exact contracts
# ============================================================================

witness_fields = tuple(
    field.name
    for field
    in fields(
        CycleWitness
    )
)

result_fields = tuple(
    field.name
    for field
    in fields(
        CycleDetectionResult
    )
)

check(
    "CycleWitness field count exact",
    len(
        witness_fields
    ) == 1,
)

check(
    "CycleWitness field order exact",
    witness_fields
    == (
        "stage_ids",
    ),
)

check(
    "CycleDetectionResult field count exact",
    len(
        result_fields
    ) == 8,
)

check(
    "CycleDetectionResult field order exact",
    result_fields
    == (
        "is_acyclic",
        "has_cycle",
        "node_count",
        "edge_count",
        "cycle_witness_count",
        "cycle_witnesses",
        "graph_version",
        "detection_version",
    ),
)


# ============================================================================
# 5. Invalid request boundary
# ============================================================================

for label, value in (
    ("None", None),
    ("string", "graph"),
    ("bytes", b"graph"),
    ("integer", 123),
    ("float", 1.5),
    ("tuple", ()),
    ("list", []),
    ("mapping", {}),
):
    expect_exception(
        f"Invalid cycle request rejected: {label}",
        InvalidCycleDetectionRequestError,
        lambda value=value: detect_dependency_cycles(
            value
        ),
    )


# ============================================================================
# 6. CycleWitness contract validation
# ============================================================================

expect_exception(
    "CycleWitness rejects too-short path",
    CycleDetectionError,
    lambda: CycleWitness(
        stage_ids=(
            "a",
            "a",
        )
    ),
)

expect_exception(
    "CycleWitness rejects non-closed path",
    CycleDetectionError,
    lambda: CycleWitness(
        stage_ids=(
            "a",
            "b",
            "c",
        )
    ),
)


valid_witness = CycleWitness(
    stage_ids=(
        "a",
        "b",
        "a",
    )
)

check(
    "Valid CycleWitness accepted",
    valid_witness.stage_ids
    == (
        "a",
        "b",
        "a",
    ),
)

check(
    "CycleWitness edge_count exact",
    valid_witness.edge_count == 2,
)


# ============================================================================
# 7. Empty / isolated / simple DAGs
# ============================================================================

empty_graph = create_dependency_graph(
    workflow_id="empty"
)

empty_result = detect_dependency_cycles(
    empty_graph
)

check(
    "Empty graph acyclic",
    empty_result.is_acyclic is True,
)

check(
    "Empty graph has_cycle false",
    empty_result.has_cycle is False,
)

check(
    "Empty graph zero witnesses",
    empty_result.cycle_witness_count == 0,
)


isolated_graph = create_dependency_graph(
    workflow_id="isolated",
    node_ids=(
        "a",
        "b",
        "c",
    ),
)

isolated_result = detect_dependency_cycles(
    isolated_graph
)

check(
    "Isolated graph acyclic",
    isolated_result.is_acyclic is True,
)

check(
    "Isolated graph node count exact",
    isolated_result.node_count == 3,
)

check(
    "Isolated graph edge count zero",
    isolated_result.edge_count == 0,
)


chain = create_dependency_graph(
    workflow_id="chain",
    edges=(
        ("a", "b"),
        ("b", "c"),
        ("c", "d"),
    ),
)

chain_result = detect_dependency_cycles(
    chain
)

check(
    "Linear chain acyclic",
    chain_result.is_acyclic is True,
)

check(
    "Linear chain zero witnesses",
    chain_result.cycle_witnesses == (),
)


branch_join = create_dependency_graph(
    workflow_id="branch-join",
    edges=(
        ("start", "a"),
        ("start", "b"),
        ("a", "join"),
        ("b", "join"),
    ),
)

branch_join_result = detect_dependency_cycles(
    branch_join
)

check(
    "Branch/join DAG acyclic",
    branch_join_result.is_acyclic is True,
)


diamond = create_dependency_graph(
    workflow_id="diamond",
    edges=(
        ("a", "b"),
        ("a", "c"),
        ("b", "d"),
        ("c", "d"),
    ),
)

check(
    "Diamond DAG acyclic",
    detect_dependency_cycles(
        diamond
    ).is_acyclic is True,
)


# ============================================================================
# 8. Two-node and three-node cycles
# ============================================================================

two_cycle = create_dependency_graph(
    workflow_id="two-cycle",
    edges=(
        ("a", "b"),
        ("b", "a"),
    ),
)

two_result = detect_dependency_cycles(
    two_cycle
)

check(
    "Two-node cycle detected",
    two_result.has_cycle is True,
)

check(
    "Two-node witness count exact",
    two_result.cycle_witness_count == 1,
)

check(
    "Two-node witness exact",
    two_result.cycle_witnesses[0].stage_ids
    == (
        "a",
        "b",
        "a",
    ),
)


three_cycle = create_dependency_graph(
    workflow_id="three-cycle",
    edges=(
        ("c", "a"),
        ("a", "b"),
        ("b", "c"),
    ),
)

three_result = detect_dependency_cycles(
    three_cycle
)

check(
    "Three-node cycle detected",
    three_result.has_cycle is True,
)

check(
    "Three-node witness canonical rotation exact",
    three_result.cycle_witnesses[0].stage_ids
    == (
        "a",
        "b",
        "c",
        "a",
    ),
)


# ============================================================================
# 9. Longer cycle
# ============================================================================

long_cycle = create_dependency_graph(
    workflow_id="long-cycle",
    edges=tuple(
        (
            f"n{index}",
            f"n{index + 1}",
        )
        for index
        in range(9)
    )
    + (
        (
            "n9",
            "n0",
        ),
    ),
)

long_result = detect_dependency_cycles(
    long_cycle
)

check(
    "Ten-node cycle detected",
    long_result.has_cycle is True,
)

check(
    "Ten-node cycle witness count exact",
    long_result.cycle_witness_count == 1,
)

check(
    "Ten-node cycle witness edge count exact",
    long_result.cycle_witnesses[0].edge_count
    == 10,
)


# ============================================================================
# 10. Multiple disconnected cyclic components
# ============================================================================

multiple_cycles = create_dependency_graph(
    workflow_id="multiple-cycles",
    edges=(
        ("a", "b"),
        ("b", "a"),

        ("m", "n"),
        ("n", "o"),
        ("o", "m"),

        ("x", "y"),
        ("y", "z"),
        ("z", "w"),
        ("w", "x"),
    ),
)

multiple_result = detect_dependency_cycles(
    multiple_cycles
)

check(
    "Three disconnected cyclic regions detected",
    multiple_result.has_cycle is True,
)

check(
    "Three disconnected witnesses found",
    multiple_result.cycle_witness_count == 3,
)

check(
    "Disconnected witness ordering deterministic",
    tuple(
        witness.stage_ids
        for witness
        in multiple_result.cycle_witnesses
    )
    == (
        ("a", "b", "a"),
        ("m", "n", "o", "m"),
        ("w", "x", "y", "z", "w"),
    ),
)


# ============================================================================
# 11. Cycle embedded in larger DAG
# ============================================================================

embedded = create_dependency_graph(
    workflow_id="embedded-cycle",
    edges=(
        ("start", "a"),
        ("a", "b"),
        ("b", "c"),
        ("c", "a"),
        ("c", "after"),
        ("after", "finish"),
    ),
)

embedded_result = detect_dependency_cycles(
    embedded
)

check(
    "Embedded cycle detected",
    embedded_result.has_cycle is True,
)

check(
    "Embedded cycle witness exact",
    embedded_result.cycle_witnesses[0].stage_ids
    == (
        "a",
        "b",
        "c",
        "a",
    ),
)


# ============================================================================
# 12. Shared-node cyclic topology
# ============================================================================

shared = create_dependency_graph(
    workflow_id="shared-cycles",
    edges=(
        ("a", "b"),
        ("b", "c"),
        ("c", "a"),
        ("c", "d"),
        ("d", "c"),
    ),
)

shared_result = detect_dependency_cycles(
    shared
)

check(
    "Shared-node cyclic topology detected",
    shared_result.has_cycle is True,
)

check(
    "Shared-node topology produces cycle evidence",
    shared_result.cycle_witness_count >= 1,
)


# ============================================================================
# 13. Phase 4.2 precondition
# ============================================================================

self_graph = create_dependency_graph(
    workflow_id="self",
    edges=(
        ("a", "a"),
    ),
)

self_blocked = False

try:
    detect_dependency_cycles(
        self_graph
    )

except DependencyGraphValidationFailedError:
    self_blocked = True

check(
    "Self-dependency rejected before cycle analysis",
    self_blocked,
)


# ============================================================================
# 14. Require-acyclic guard
# ============================================================================

required_chain = require_acyclic_dependency_graph(
    chain
)

check(
    "Require-acyclic accepts DAG",
    required_chain
    == chain_result,
)


caught = None

try:
    require_acyclic_dependency_graph(
        three_cycle
    )

except CyclicDependencyGraphError as exc:
    caught = exc

check(
    "Require-acyclic raises canonical error",
    isinstance(
        caught,
        CyclicDependencyGraphError,
    ),
)

check(
    "Cyclic error derives from CycleDetectionError",
    isinstance(
        caught,
        CycleDetectionError,
    ),
)

check(
    "Cyclic error preserves exact result",
    caught is not None
    and caught.result
    == three_result,
)

check(
    "Cyclic error message reports witness count",
    caught is not None
    and "1 cycle witness"
    in str(
        caught
    ),
)


# ============================================================================
# 15. Result immutability
# ============================================================================

blocked = False

try:
    three_result.has_cycle = False

except Exception:
    blocked = True

check(
    "CycleDetectionResult immutable",
    blocked,
)


blocked = False

try:
    three_result.cycle_witnesses += (
        valid_witness,
    )

except Exception:
    blocked = True

check(
    "CycleDetectionResult witness tuple immutable",
    blocked,
)


blocked = False

try:
    three_result.cycle_witnesses[
        0
    ].stage_ids = ()

except Exception:
    blocked = True

check(
    "Nested CycleWitness immutable",
    blocked,
)


# ============================================================================
# 16. to_dict deep immutability
# ============================================================================

witness_dict = (
    three_result.cycle_witnesses[0].to_dict()
)

check(
    "CycleWitness to_dict immutable",
    isinstance(
        witness_dict,
        MappingProxyType,
    ),
)

blocked = False

try:
    witness_dict[
        "edge_count"
    ] = 999

except Exception:
    blocked = True

check(
    "CycleWitness to_dict mutation blocked",
    blocked,
)


result_dict = three_result.to_dict()

check(
    "CycleDetectionResult to_dict immutable",
    isinstance(
        result_dict,
        MappingProxyType,
    ),
)

check(
    "CycleDetectionResult witness serialization tuple",
    isinstance(
        result_dict[
            "cycle_witnesses"
        ],
        tuple,
    ),
)

check(
    "CycleDetectionResult nested witness mapping immutable",
    isinstance(
        result_dict[
            "cycle_witnesses"
        ][0],
        MappingProxyType,
    ),
)

blocked = False

try:
    result_dict[
        "cycle_witnesses"
    ][0][
        "edge_count"
    ] = 999

except Exception:
    blocked = True

check(
    "CycleDetectionResult deep mutation blocked",
    blocked,
)


# ============================================================================
# 17. Snapshot
# ============================================================================

snapshot = cycle_detection_snapshot(
    multiple_cycles
)

check(
    "Snapshot MappingProxyType",
    isinstance(
        snapshot,
        MappingProxyType,
    ),
)

check(
    "Snapshot detection version exact",
    snapshot[
        "detection_version"
    ]
    == CYCLE_DETECTION_VERSION,
)

check(
    "Snapshot schema exact",
    snapshot[
        "schema_version"
    ]
    == CYCLE_DETECTION_SCHEMA_VERSION,
)

check(
    "Snapshot graph version exact",
    snapshot[
        "graph_version"
    ]
    == DEPENDENCY_GRAPH_VERSION,
)

check(
    "Snapshot cycle flag exact",
    snapshot[
        "has_cycle"
    ] is True,
)

check(
    "Snapshot cycle witness count exact",
    snapshot[
        "cycle_witness_count"
    ] == 3,
)

check(
    "Snapshot witness tuple immutable",
    isinstance(
        snapshot[
            "cycle_witnesses"
        ],
        tuple,
    ),
)

check(
    "Snapshot nested witness immutable",
    isinstance(
        snapshot[
            "cycle_witnesses"
        ][0],
        MappingProxyType,
    ),
)

blocked = False

try:
    snapshot[
        "cycle_witnesses"
    ][0][
        "stage_ids"
    ] = ()

except Exception:
    blocked = True

check(
    "Snapshot deep mutation blocked",
    blocked,
)


# ============================================================================
# 18. Architecture evidence
# ============================================================================

architecture = explain_cycle_detection_v4_3()

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
    ] == "4.3",
)

check(
    "Architecture component exact",
    architecture[
        "component"
    ]
    == "Cycle Detection",
)

check(
    "Architecture version exact",
    architecture[
        "version"
    ]
    == CYCLE_DETECTION_VERSION,
)

check(
    "Architecture schema exact",
    architecture[
        "schema_version"
    ]
    == CYCLE_DETECTION_SCHEMA_VERSION,
)

check(
    "Architecture input authority exact",
    architecture[
        "input_authority"
    ]
    == "Phase 4.1 DependencyGraph",
)

check(
    "Architecture validation precondition exact",
    architecture[
        "validation_precondition"
    ]
    == "Phase 4.2 Dependency Validation",
)


upstream_versions = architecture[
    "upstream_versions"
]

check(
    "Upstream versions immutable",
    isinstance(
        upstream_versions,
        MappingProxyType,
    ),
)

check(
    "4.1 upstream version exact",
    upstream_versions[
        "4.1"
    ]
    == DEPENDENCY_GRAPH_VERSION,
)

check(
    "4.2 upstream version exact",
    upstream_versions[
        "4.2"
    ]
    == DEPENDENCY_VALIDATION_VERSION,
)


algorithm = architecture[
    "algorithm"
]

check(
    "Algorithm mapping immutable",
    isinstance(
        algorithm,
        MappingProxyType,
    ),
)

check(
    "Algorithm family exact",
    algorithm[
        "family"
    ]
    == "deterministic DFS active-stack",
)

check(
    "Algorithm node ordering lexical",
    algorithm[
        "node_order"
    ]
    == "lexical",
)

check(
    "Algorithm dependent ordering lexical",
    algorithm[
        "dependent_order"
    ]
    == "lexical",
)

check(
    "Algorithm evidence canonical witnesses",
    algorithm[
        "evidence"
    ]
    == "canonical cycle witnesses",
)

check(
    "Exhaustive cycle enumeration disabled",
    algorithm[
        "exhaustive_simple_cycle_enumeration"
    ] is False,
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
    dict(
        future
    )
    == {
        "4.4":
            "Runnable Stage Resolver",
        "4.5":
            "Execution Planner",
        "4.6":
            "Planning Certification",
    },
)

blocked = False

try:
    future[
        "4.4"
    ] = "MUTATED"

except Exception:
    blocked = True

check(
    "Future authority nested mutation blocked",
    blocked,
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
    "Read-only exact",
    execution[
        "read_only"
    ] is True,
)

check(
    "Deterministic exact",
    execution[
        "deterministic"
    ] is True,
)

check(
    "Side-effect free exact",
    execution[
        "side_effect_free"
    ] is True,
)

check(
    "Graph mutation false",
    execution[
        "graph_mutation"
    ] is False,
)

check(
    "Runtime execution false",
    execution[
        "runtime_execution"
    ] is False,
)

check(
    "Persistence false",
    execution[
        "persistence"
    ] is False,
)


# ============================================================================
# 19. Determinism
# ============================================================================

check(
    "Repeated DAG detection deterministic",
    detect_dependency_cycles(
        branch_join
    )
    == branch_join_result,
)

check(
    "Repeated cycle detection deterministic",
    detect_dependency_cycles(
        three_cycle
    )
    == three_result,
)

check(
    "Repeated multiple-cycle detection deterministic",
    detect_dependency_cycles(
        multiple_cycles
    )
    == multiple_result,
)

check(
    "Repeated snapshot deterministic",
    dict(
        cycle_detection_snapshot(
            multiple_cycles
        )
    )
    == dict(
        snapshot
    ),
)

check(
    "Repeated architecture deterministic",
    dict(
        explain_cycle_detection_v4_3()
    )
    == dict(
        architecture
    ),
)


# ============================================================================
# 20. Static import boundary
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


allowed_backend_imports = {
    (
        "backend.server.coordination."
        "dependency_planning.dependency_graph"
    ),
    (
        "backend.server.coordination."
        "dependency_planning.dependency_validation"
    ),
}

check(
    "4.3 imports only frozen 4.1 and 4.2",
    set(
        backend_imports
    ).issubset(
        allowed_backend_imports
    ),
    repr(
        backend_imports
    ),
)


# ============================================================================
# 21. Forbidden authority checks
# ============================================================================

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
    "resolve_runnable",
    "plan_execution",
    "create_execution_plan",
    "schedule_stage",
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
    "4.3 performs no Runtime/runnability/planning/persistence execution",
    not bad_calls,
    repr(
        bad_calls
    ),
)


# ============================================================================
# 22. No authoritative topological execution output
# ============================================================================

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
    "topological",
    "execution_plan",
    "runnable",
    "schedule",
)

check(
    "4.3 exposes no public execution-order/planning API",
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


# ============================================================================
# 23. Source authority assertions
# ============================================================================

check(
    "Source declares cycle detection ownership",
    "deterministic directed-cycle detection"
    in source,
)

check(
    "Source declares cycle witness ownership",
    "canonical cycle-witness evidence"
    in source,
)

check(
    "Source defers semantic validation to 4.2",
    "dependency semantic validation (Phase 4.2)"
    in source,
)

check(
    "Source defers self-dependency validation to 4.2",
    "self-dependency validation (Phase 4.2)"
    in source,
)

check(
    "Source defers runnable-stage resolution to 4.4",
    "runnable-stage resolution (Phase 4.4)"
    in source,
)

check(
    "Source defers execution planning to 4.5",
    "execution ordering/planning (Phase 4.5)"
    in source,
)

check(
    "Source excludes Runtime execution",
    "Runtime execution (Phase 5)"
    in source,
)

check(
    "Source excludes persistence",
    "persistence (Phase 8)"
    in source,
)

check(
    "Source excludes recovery",
    "recovery (Phase 9)"
    in source,
)

check(
    "Source explicitly rejects exhaustive simple-cycle enumeration",
    (
        "does not attempt\n"
        "exhaustive enumeration of every possible simple cycle"
    )
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

failed = (
    len(
        checks
    )
    - passed
)


report_lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 4.3 — CYCLE DETECTION INITIAL VERIFICATION",
    "=" * 100,
    "",
    (
        "Cycle Detection Version: "
        + CYCLE_DETECTION_VERSION
    ),
    (
        "Cycle Detection Schema: "
        + CYCLE_DETECTION_SCHEMA_VERSION
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
        "Phase 4.3 SHA256: "
        + actual_43_sha
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
print("PHASE 4.3 INITIAL VERIFICATION RESULT")
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
print(
    "REPORT:",
    REPORT.name,
)
print("=" * 100)


raise SystemExit(
    0
    if failed == 0
    else 1
)
