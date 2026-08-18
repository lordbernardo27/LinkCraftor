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
    "cycle_detection_phase_4_3_final_certification.txt"
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


checks = []


def check(name, condition, detail=""):
    ok = bool(condition)
    checks.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    if detail:
        print(f"       {detail}")


def expect_exception(name, exception_type, callable_):
    try:
        callable_()
    except exception_type:
        check(name, True)
    except Exception as exc:
        check(
            name,
            False,
            f"unexpected {type(exc).__name__}: {exc}",
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
print("PHASE 4.3 — CYCLE DETECTION FINAL CERTIFICATION")
print("=" * 104)


# ============================================================================
# 1. Canonical files
# ============================================================================

check(
    "Frozen Phase 4.1 file exists",
    PHASE_41.exists(),
    str(PHASE_41.relative_to(ROOT)),
)

check(
    "Frozen Phase 4.2 file exists",
    PHASE_42.exists(),
    str(PHASE_42.relative_to(ROOT)),
)

check(
    "Canonical Phase 4.3 file exists",
    PHASE_43.exists(),
    str(PHASE_43.relative_to(ROOT)),
)


# ============================================================================
# 2. Frozen integrity
# ============================================================================

actual_41_sha = sha256(PHASE_41)
actual_42_sha = sha256(PHASE_42)
actual_43_sha = sha256(PHASE_43)

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
    "Phase 4.3 SHA exact",
    actual_43_sha == EXPECTED_43_SHA,
    actual_43_sha,
)


# ============================================================================
# 3. Syntax / import
# ============================================================================

source = PHASE_43.read_text(
    encoding="utf-8-sig"
)

try:
    tree = ast.parse(source)
    syntax_ok = True
except SyntaxError:
    tree = None
    syntax_ok = False

check(
    "Phase 4.3 syntax parses",
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
# 4. Canonical identity and contracts
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
    "Cycle Detection field-count constant exact",
    CYCLE_DETECTION_RESULT_FIELD_COUNT == 8,
)

witness_fields = tuple(
    field.name
    for field
    in fields(CycleWitness)
)

result_fields = tuple(
    field.name
    for field
    in fields(CycleDetectionResult)
)

check(
    "CycleWitness exact field contract",
    witness_fields == ("stage_ids",),
)

check(
    "CycleDetectionResult exact field contract",
    result_fields == (
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
        lambda value=value: detect_dependency_cycles(value),
    )


# ============================================================================
# 6. CycleWitness contract boundary
# ============================================================================

expect_exception(
    "CycleWitness rejects too-short path",
    CycleDetectionError,
    lambda: CycleWitness(
        stage_ids=("a", "a")
    ),
)

expect_exception(
    "CycleWitness rejects non-closed path",
    CycleDetectionError,
    lambda: CycleWitness(
        stage_ids=("a", "b", "c")
    ),
)

witness = CycleWitness(
    stage_ids=("a", "b", "a")
)

check(
    "Valid CycleWitness accepted",
    witness.stage_ids == ("a", "b", "a"),
)

check(
    "Valid CycleWitness edge count exact",
    witness.edge_count == 2,
)


# ============================================================================
# 7. Empty / isolated / DAG coverage
# ============================================================================

empty = create_dependency_graph(
    workflow_id="empty"
)

empty_result = detect_dependency_cycles(empty)

check(
    "Empty graph acyclic",
    empty_result.is_acyclic is True,
)

check(
    "Empty graph has_cycle false",
    empty_result.has_cycle is False,
)

check(
    "Empty graph witness count zero",
    empty_result.cycle_witness_count == 0,
)


isolated = create_dependency_graph(
    workflow_id="isolated",
    node_ids=tuple(
        f"isolated-{i:03d}"
        for i in range(100)
    ),
)

isolated_result = detect_dependency_cycles(
    isolated
)

check(
    "100 isolated nodes acyclic",
    isolated_result.is_acyclic is True,
)

check(
    "100 isolated node count exact",
    isolated_result.node_count == 100,
)

check(
    "100 isolated edges zero",
    isolated_result.edge_count == 0,
)


chain = create_dependency_graph(
    workflow_id="large-chain",
    edges=tuple(
        (
            f"stage-{i:03d}",
            f"stage-{i + 1:03d}",
        )
        for i in range(199)
    ),
)

chain_result = detect_dependency_cycles(
    chain
)

check(
    "200-stage chain acyclic",
    chain_result.is_acyclic is True,
)

check(
    "200-stage chain zero witnesses",
    chain_result.cycle_witness_count == 0,
)

check(
    "200-stage chain edge count exact",
    chain_result.edge_count == 199,
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
    "Two-node cycle witness exact",
    two_result.cycle_witnesses[0].stage_ids
    == ("a", "b", "a"),
)


three_cycle = create_dependency_graph(
    workflow_id="three-cycle",
    edges=(
        ("b", "c"),
        ("c", "a"),
        ("a", "b"),
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
    "Three-node canonical witness exact",
    three_result.cycle_witnesses[0].stage_ids
    == ("a", "b", "c", "a"),
)


# ============================================================================
# 9. 100-node cycle
# ============================================================================

hundred_cycle_edges = tuple(
    (
        f"c{i:03d}",
        f"c{i + 1:03d}",
    )
    for i in range(99)
) + (
    ("c099", "c000"),
)

hundred_cycle = create_dependency_graph(
    workflow_id="hundred-cycle",
    edges=hundred_cycle_edges,
)

hundred_result = detect_dependency_cycles(
    hundred_cycle
)

check(
    "100-node cycle detected",
    hundred_result.has_cycle is True,
)

check(
    "100-node cycle one witness",
    hundred_result.cycle_witness_count == 1,
)

check(
    "100-node witness edge count exact",
    hundred_result.cycle_witnesses[0].edge_count
    == 100,
)

check(
    "100-node witness begins canonically",
    hundred_result.cycle_witnesses[0].stage_ids[0]
    == "c000",
)

check(
    "100-node witness closes canonically",
    hundred_result.cycle_witnesses[0].stage_ids[-1]
    == "c000",
)


# ============================================================================
# 10. Many disconnected cycles
# ============================================================================

many_cycle_edges = []

for group in range(20):
    a = f"g{group:02d}-a"
    b = f"g{group:02d}-b"
    c = f"g{group:02d}-c"

    many_cycle_edges.extend(
        (
            (a, b),
            (b, c),
            (c, a),
        )
    )

many_cycles = create_dependency_graph(
    workflow_id="many-cycles",
    edges=tuple(many_cycle_edges),
)

many_result = detect_dependency_cycles(
    many_cycles
)

check(
    "20 disconnected cyclic regions detected",
    many_result.has_cycle is True,
)

check(
    "20 disconnected witnesses exact",
    many_result.cycle_witness_count == 20,
)

check(
    "20 disconnected witnesses sorted deterministically",
    tuple(
        witness.stage_ids[0]
        for witness
        in many_result.cycle_witnesses
    )
    == tuple(
        f"g{group:02d}-a"
        for group
        in range(20)
    ),
)


# ============================================================================
# 11. Embedded and shared-node cycles
# ============================================================================

embedded = create_dependency_graph(
    workflow_id="embedded",
    edges=(
        ("start", "a"),
        ("a", "b"),
        ("b", "c"),
        ("c", "a"),
        ("c", "finish"),
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
    == ("a", "b", "c", "a"),
)


shared = create_dependency_graph(
    workflow_id="shared",
    edges=(
        ("a", "b"),
        ("b", "c"),
        ("c", "a"),
        ("c", "d"),
        ("d", "c"),
        ("d", "e"),
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
    "Shared-node topology returns witness evidence",
    shared_result.cycle_witness_count >= 1,
)


# ============================================================================
# 12. Mixed cyclic + acyclic disconnected regions
# ============================================================================

mixed = create_dependency_graph(
    workflow_id="mixed",
    edges=(
        ("a", "b"),
        ("b", "a"),
        ("x", "y"),
        ("y", "z"),
        ("m", "n"),
        ("n", "o"),
        ("o", "p"),
    ),
)

mixed_result = detect_dependency_cycles(
    mixed
)

check(
    "Mixed cyclic/acyclic graph detected cyclic",
    mixed_result.has_cycle is True,
)

check(
    "Mixed graph witness count exact",
    mixed_result.cycle_witness_count == 1,
)

check(
    "Mixed graph cycle evidence exact",
    mixed_result.cycle_witnesses[0].stage_ids
    == ("a", "b", "a"),
)


# ============================================================================
# 13. 4.2 precondition protection
# ============================================================================

self_graph = create_dependency_graph(
    workflow_id="self",
    edges=(("a", "a"),),
)

self_blocked = False

try:
    detect_dependency_cycles(
        self_graph
    )
except DependencyGraphValidationFailedError:
    self_blocked = True

check(
    "Self-dependency rejected by frozen 4.2 before 4.3",
    self_blocked,
)


# ============================================================================
# 14. Require-acyclic guard
# ============================================================================

required_chain = require_acyclic_dependency_graph(
    chain
)

check(
    "Require-acyclic returns DAG result",
    required_chain == chain_result,
)


caught = None

try:
    require_acyclic_dependency_graph(
        hundred_cycle
    )
except CyclicDependencyGraphError as exc:
    caught = exc

check(
    "Require-acyclic rejects large cyclic graph",
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
    and caught.result == hundred_result,
)

check(
    "Cyclic error reports witness count",
    caught is not None
    and "1 cycle witness"
    in str(caught),
)


# ============================================================================
# 15. Deep immutability
# ============================================================================

blocked = False

try:
    hundred_result.has_cycle = False
except Exception:
    blocked = True

check(
    "CycleDetectionResult immutable",
    blocked,
)


blocked = False

try:
    hundred_result.cycle_witnesses[0].stage_ids = ()
except Exception:
    blocked = True

check(
    "Nested CycleWitness immutable",
    blocked,
)


witness_map = (
    hundred_result.cycle_witnesses[0].to_dict()
)

check(
    "CycleWitness mapping immutable",
    isinstance(
        witness_map,
        MappingProxyType,
    ),
)

blocked = False

try:
    witness_map["edge_count"] = 999
except Exception:
    blocked = True

check(
    "CycleWitness mapping mutation blocked",
    blocked,
)


result_map = hundred_result.to_dict()

check(
    "CycleDetectionResult mapping immutable",
    isinstance(
        result_map,
        MappingProxyType,
    ),
)

check(
    "CycleDetectionResult nested tuple immutable",
    isinstance(
        result_map["cycle_witnesses"],
        tuple,
    ),
)

check(
    "CycleDetectionResult nested witness mapping immutable",
    isinstance(
        result_map["cycle_witnesses"][0],
        MappingProxyType,
    ),
)

blocked = False

try:
    result_map[
        "cycle_witnesses"
    ][0][
        "stage_ids"
    ] = ()
except Exception:
    blocked = True

check(
    "CycleDetectionResult deep mutation blocked",
    blocked,
)


# ============================================================================
# 16. Snapshot
# ============================================================================

snapshot = cycle_detection_snapshot(
    many_cycles
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
    snapshot["detection_version"]
    == CYCLE_DETECTION_VERSION,
)

check(
    "Snapshot schema exact",
    snapshot["schema_version"]
    == CYCLE_DETECTION_SCHEMA_VERSION,
)

check(
    "Snapshot graph version exact",
    snapshot["graph_version"]
    == DEPENDENCY_GRAPH_VERSION,
)

check(
    "Snapshot cycle flag exact",
    snapshot["has_cycle"] is True,
)

check(
    "Snapshot witness count exact",
    snapshot["cycle_witness_count"] == 20,
)

check(
    "Snapshot nested witness immutable",
    isinstance(
        snapshot["cycle_witnesses"][0],
        MappingProxyType,
    ),
)

blocked = False

try:
    snapshot[
        "cycle_witnesses"
    ][0][
        "edge_count"
    ] = 999
except Exception:
    blocked = True

check(
    "Snapshot deep mutation blocked",
    blocked,
)


# ============================================================================
# 17. Determinism
# ============================================================================

check(
    "Repeated 100-node cycle deterministic",
    detect_dependency_cycles(
        hundred_cycle
    ) == hundred_result,
)

check(
    "Repeated 20-cycle graph deterministic",
    detect_dependency_cycles(
        many_cycles
    ) == many_result,
)

check(
    "Repeated embedded-cycle graph deterministic",
    detect_dependency_cycles(
        embedded
    ) == embedded_result,
)

check(
    "Repeated snapshot deterministic",
    dict(
        cycle_detection_snapshot(
            many_cycles
        )
    )
    == dict(snapshot),
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
    architecture["phase"] == "4.3",
)

check(
    "Architecture component exact",
    architecture["component"]
    == "Cycle Detection",
)

check(
    "Architecture version exact",
    architecture["version"]
    == CYCLE_DETECTION_VERSION,
)

check(
    "Architecture schema exact",
    architecture["schema_version"]
    == CYCLE_DETECTION_SCHEMA_VERSION,
)

check(
    "Architecture input authority exact",
    architecture["input_authority"]
    == "Phase 4.1 DependencyGraph",
)

check(
    "Architecture validation precondition exact",
    architecture["validation_precondition"]
    == "Phase 4.2 Dependency Validation",
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
    algorithm["family"]
    == "deterministic DFS active-stack",
)

check(
    "Algorithm node order lexical",
    algorithm["node_order"]
    == "lexical",
)

check(
    "Algorithm dependent order lexical",
    algorithm["dependent_order"]
    == "lexical",
)

check(
    "Algorithm evidence canonical witnesses",
    algorithm["evidence"]
    == "canonical cycle witnesses",
)

check(
    "Exhaustive simple-cycle enumeration false",
    algorithm[
        "exhaustive_simple_cycle_enumeration"
    ] is False,
)


semantics = architecture[
    "graph_semantics"
]

check(
    "Graph semantics immutable",
    isinstance(
        semantics,
        MappingProxyType,
    ),
)

check(
    "Empty graph semantics exact",
    semantics["empty_graph"]
    == "acyclic",
)

check(
    "Isolated-node semantics exact",
    semantics["isolated_nodes"]
    == "acyclic",
)

check(
    "Two-node cycle semantics exact",
    semantics["two_node_cycle"]
    == "cyclic",
)

check(
    "Multi-node cycle semantics exact",
    semantics["multi_node_cycle"]
    == "cyclic",
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
        "4.4":
            "Runnable Stage Resolver",
        "4.5":
            "Execution Planner",
        "4.6":
            "Planning Certification",
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
    "4.3 read-only",
    execution["read_only"] is True,
)

check(
    "4.3 deterministic",
    execution["deterministic"] is True,
)

check(
    "4.3 side-effect free",
    execution["side_effect_free"] is True,
)

check(
    "4.3 graph mutation disabled",
    execution["graph_mutation"] is False,
)

check(
    "4.3 Runtime execution disabled",
    execution["runtime_execution"] is False,
)

check(
    "4.3 persistence disabled",
    execution["persistence"] is False,
)


# ============================================================================
# 19. Static import boundary
# ============================================================================

backend_imports = []

if tree is not None:
    for node in ast.walk(tree):

        if isinstance(node, ast.Import):
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
}

check(
    "4.3 imports only frozen 4.1 and 4.2",
    set(
        backend_imports
    ).issubset(
        allowed_imports
    ),
    repr(backend_imports),
)


# ============================================================================
# 20. No forbidden execution authority
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
    "4.3 performs no Runtime/runnability/planning/persistence execution",
    not bad_calls,
    repr(bad_calls),
)


# ============================================================================
# 21. No execution-order public authority
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
    "4.3 exposes no execution-order/runnability API",
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


# ============================================================================
# 22. Source authority assertions
# ============================================================================

source_assertions = (
    (
        "Source owns deterministic cycle detection",
        "deterministic directed-cycle detection",
    ),
    (
        "Source owns cycle witness evidence",
        "canonical cycle-witness evidence",
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
        "Source defers self dependency to 4.2",
        "self-dependency validation (Phase 4.2)",
    ),
    (
        "Source defers runnable stage resolution to 4.4",
        "runnable-stage resolution (Phase 4.4)",
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
        "Runtime execution (Phase 5)",
    ),
    (
        "Source excludes stage handoff",
        "stage handoff (Phase 6)",
    ),
    (
        "Source excludes persistence",
        "persistence (Phase 8)",
    ),
    (
        "Source excludes recovery",
        "recovery (Phase 9)",
    ),
)

for name, marker in source_assertions:
    check(
        name,
        marker in source,
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
# 23. Final SHA freeze candidate
# ============================================================================

check(
    "Phase 4.3 SHA remains freeze candidate",
    actual_43_sha == EXPECTED_43_SHA,
    actual_43_sha,
)


# ============================================================================
# FINAL RESULT
# ============================================================================

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
    "PHASE 4.3 — CYCLE DETECTION FINAL CERTIFICATION",
    "=" * 104,
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
    "\n".join(report_lines) + "\n",
    encoding="utf-8",
)


print()
print("=" * 104)
print("PHASE 4.3 FINAL CERTIFICATION RESULT")
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
    "REPORT:",
    REPORT.name,
)
print("=" * 104)


raise SystemExit(
    0 if failed == 0 else 1
)
