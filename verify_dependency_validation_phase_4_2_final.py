from __future__ import annotations

import ast
import hashlib
import importlib
from dataclasses import fields
from pathlib import Path
from types import MappingProxyType

from backend.server.coordination.dependency_planning.dependency_graph import (
    DEPENDENCY_GRAPH_VERSION,
    DependencyEdge,
    DependencyGraph,
    create_dependency_graph,
)

from backend.server.coordination.dependency_planning.dependency_validation import (
    DEPENDENCY_VALIDATION_VERSION,
    DEPENDENCY_VALIDATION_SCHEMA_VERSION,
    DEPENDENCY_VALIDATION_RESULT_FIELD_COUNT,
    SELF_DEPENDENCY_VIOLATION_CODE,
    GRAPH_INVARIANT_VIOLATION_CODE,
    DependencyValidationError,
    InvalidDependencyValidationRequestError,
    DependencyGraphValidationFailedError,
    DependencyValidationViolation,
    DependencyValidationResult,
    validate_dependency_graph,
    require_valid_dependency_graph,
    dependency_validation_snapshot,
    explain_dependency_validation_v4_2,
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

REPORT = ROOT / (
    "dependency_validation_phase_4_2_final_certification.txt"
)


EXPECTED_41_SHA = (
    "4F6BA62D011C31D9D851FBBABC37C12B"
    "7DDAA1FD9A91E34788EBCE25741A1F70"
)

EXPECTED_42_CANDIDATE_SHA = (
    "1D053C0036EA9F7A8AEDFAFC36F6EB82"
    "A681EDC7EF206409E9FFB8C7F212852D"
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
print("PHASE 4.2 — DEPENDENCY VALIDATION FINAL CERTIFICATION")
print("=" * 104)


# ============================================================================
# 1. Canonical files
# ============================================================================

check(
    "Frozen Phase 4.1 file exists",
    PHASE_41.exists(),
    str(
        PHASE_41.relative_to(ROOT)
    ),
)

check(
    "Canonical Phase 4.2 file exists",
    PHASE_42.exists(),
    str(
        PHASE_42.relative_to(ROOT)
    ),
)


# ============================================================================
# 2. Frozen 4.1 integrity
# ============================================================================

actual_41_sha = sha256(
    PHASE_41
)

check(
    "Frozen Phase 4.1 SHA exact",
    actual_41_sha
    == EXPECTED_41_SHA,
    actual_41_sha,
)


# ============================================================================
# 3. Syntax / import
# ============================================================================

source = PHASE_42.read_text(
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
    "Phase 4.2 Python syntax parses",
    syntax_ok,
)


try:
    importlib.import_module(
        "backend.server.coordination."
        "dependency_planning.dependency_validation"
    )
    import_ok = True
    import_detail = ""

except Exception as exc:
    import_ok = False
    import_detail = repr(exc)

check(
    "Phase 4.2 module imports successfully",
    import_ok,
    import_detail,
)


# ============================================================================
# 4. Canonical identity
# ============================================================================

check(
    "Dependency Validation version exact",
    DEPENDENCY_VALIDATION_VERSION
    == "dependency_validation_v4.2.0",
)

check(
    "Dependency Validation schema exact",
    DEPENDENCY_VALIDATION_SCHEMA_VERSION
    == "dependency_validation_schema_v1",
)

check(
    "Validation result field-count constant exact",
    DEPENDENCY_VALIDATION_RESULT_FIELD_COUNT
    == 10,
)

check(
    "Self-dependency violation code exact",
    SELF_DEPENDENCY_VIOLATION_CODE
    == "self_dependency_prohibited",
)

check(
    "Graph invariant violation code exact",
    GRAPH_INVARIANT_VIOLATION_CODE
    == "dependency_graph_invariant_violation",
)


# ============================================================================
# 5. Exact public contracts
# ============================================================================

violation_fields = tuple(
    field.name
    for field
    in fields(
        DependencyValidationViolation
    )
)

result_fields = tuple(
    field.name
    for field
    in fields(
        DependencyValidationResult
    )
)


check(
    "Violation field count exact",
    len(
        violation_fields
    ) == 4,
)

check(
    "Violation field order exact",
    violation_fields
    == (
        "code",
        "message",
        "prerequisite_stage_id",
        "dependent_stage_id",
    ),
)

check(
    "Result field count exact",
    len(
        result_fields
    ) == 10,
)

check(
    "Result field order exact",
    result_fields
    == (
        "is_valid",
        "checks_run",
        "checks_passed",
        "checks_failed",
        "node_count",
        "edge_count",
        "self_dependency_count",
        "violations",
        "graph_version",
        "validation_version",
    ),
)


# ============================================================================
# 6. Invalid request boundary
# ============================================================================

for label, value in (
    ("None", None),
    ("string", "not-a-graph"),
    ("bytes", b"graph"),
    ("integer", 1),
    ("float", 1.5),
    ("tuple", ()),
    ("list", []),
    ("mapping", {}),
):
    expect_exception(
        f"Invalid validation request rejected: {label}",
        InvalidDependencyValidationRequestError,
        lambda value=value: validate_dependency_graph(
            value
        ),
    )


# ============================================================================
# 7. Empty graph
# ============================================================================

empty_graph = create_dependency_graph(
    workflow_id="empty-workflow"
)

empty_result = validate_dependency_graph(
    empty_graph
)

check(
    "Empty graph valid",
    empty_result.is_valid is True,
)

check(
    "Empty graph zero failures",
    empty_result.checks_failed == 0,
)

check(
    "Empty graph zero nodes",
    empty_result.node_count == 0,
)

check(
    "Empty graph zero edges",
    empty_result.edge_count == 0,
)

check(
    "Empty graph zero self dependencies",
    empty_result.self_dependency_count == 0,
)

check(
    "Empty graph no violations",
    empty_result.violations == (),
)


# ============================================================================
# 8. Large valid acyclic graph
# ============================================================================

large_edges = tuple(
    (
        f"stage-{index:03d}",
        f"stage-{index + 1:03d}",
    )
    for index
    in range(199)
)

large_graph = create_dependency_graph(
    workflow_id="large-valid-workflow",
    node_ids=(
        "isolated-a",
        "isolated-b",
    ),
    edges=large_edges,
)

large_result = validate_dependency_graph(
    large_graph
)

check(
    "Large graph valid",
    large_result.is_valid is True,
)

check(
    "Large graph zero failures",
    large_result.checks_failed == 0,
)

check(
    "Large graph zero violations",
    large_result.violations == (),
)

check(
    "Large graph node count exact",
    large_result.node_count == 202,
)

check(
    "Large graph edge count exact",
    large_result.edge_count == 199,
)

check(
    "Large graph self-dependency count zero",
    large_result.self_dependency_count == 0,
)


# ============================================================================
# 9. Large multi-self-dependency graph
# ============================================================================

self_edges = tuple(
    (
        f"self-{index:03d}",
        f"self-{index:03d}",
    )
    for index
    in range(50)
)

multi_self_graph = create_dependency_graph(
    workflow_id="multi-self-workflow",
    edges=(
        self_edges
        + (
            ("a", "b"),
            ("b", "c"),
        )
    ),
)

multi_self_result = validate_dependency_graph(
    multi_self_graph
)

check(
    "50-self-dependency graph invalid",
    multi_self_result.is_valid is False,
)

check(
    "50 self dependencies counted exactly",
    multi_self_result.self_dependency_count == 50,
)

check(
    "50 self dependencies produce 50 violations",
    len(
        multi_self_result.violations
    ) == 50,
)

check(
    "50 self dependencies produce 50 failed checks",
    multi_self_result.checks_failed == 50,
)

check(
    "Every multi-self violation uses canonical code",
    all(
        item.code
        == SELF_DEPENDENCY_VIOLATION_CODE
        for item
        in multi_self_result.violations
    ),
)

check(
    "Multi-self violation ordering deterministic",
    tuple(
        item.prerequisite_stage_id
        for item
        in multi_self_result.violations
    )
    == tuple(
        f"self-{index:03d}"
        for index
        in range(50)
    ),
)


# ============================================================================
# 10. CRITICAL — cycle authority remains 4.3
# ============================================================================

two_cycle = create_dependency_graph(
    workflow_id="cycle-two",
    edges=(
        ("a", "b"),
        ("b", "a"),
    ),
)

two_cycle_result = validate_dependency_graph(
    two_cycle
)

check(
    "Two-node cycle valid in Phase 4.2",
    two_cycle_result.is_valid is True,
)

check(
    "Two-node cycle zero violations",
    two_cycle_result.violations == (),
)


three_cycle = create_dependency_graph(
    workflow_id="cycle-three",
    edges=(
        ("a", "b"),
        ("b", "c"),
        ("c", "a"),
    ),
)

three_cycle_result = validate_dependency_graph(
    three_cycle
)

check(
    "Three-node cycle valid in Phase 4.2",
    three_cycle_result.is_valid is True,
)

check(
    "Three-node cycle zero failures",
    three_cycle_result.checks_failed == 0,
)


large_cycle_edges = tuple(
    (
        f"cycle-{index:03d}",
        f"cycle-{index + 1:03d}",
    )
    for index
    in range(99)
) + (
    (
        "cycle-099",
        "cycle-000",
    ),
)

large_cycle = create_dependency_graph(
    workflow_id="large-cycle",
    edges=large_cycle_edges,
)

large_cycle_result = validate_dependency_graph(
    large_cycle
)

check(
    "100-node cycle valid in Phase 4.2",
    large_cycle_result.is_valid is True,
)

check(
    "100-node cycle zero 4.2 failures",
    large_cycle_result.checks_failed == 0,
)

check(
    "100-node cycle zero 4.2 violations",
    large_cycle_result.violations == (),
)


# ============================================================================
# 11. Mixed cycle plus self-edge
# ============================================================================

mixed_graph = create_dependency_graph(
    workflow_id="mixed-cycle-self",
    edges=(
        ("a", "b"),
        ("b", "c"),
        ("c", "a"),
        ("z", "z"),
    ),
)

mixed_result = validate_dependency_graph(
    mixed_graph
)

check(
    "Cycle plus self-edge invalid only because of self-edge",
    mixed_result.is_valid is False,
)

check(
    "Cycle plus self-edge counts one self dependency",
    mixed_result.self_dependency_count == 1,
)

check(
    "Cycle plus self-edge reports one failure",
    mixed_result.checks_failed == 1,
)

check(
    "Cycle plus self-edge reports one violation",
    len(
        mixed_result.violations
    ) == 1,
)

check(
    "Mixed graph violation is self-dependency only",
    mixed_result.violations[0].code
    == SELF_DEPENDENCY_VIOLATION_CODE,
)


# ============================================================================
# 12. Isolated nodes
# ============================================================================

isolated_graph = create_dependency_graph(
    workflow_id="isolated-workflow",
    node_ids=tuple(
        f"isolated-{index:03d}"
        for index
        in range(100)
    ),
)

isolated_result = validate_dependency_graph(
    isolated_graph
)

check(
    "100 isolated nodes valid",
    isolated_result.is_valid is True,
)

check(
    "100 isolated nodes counted exactly",
    isolated_result.node_count == 100,
)

check(
    "100 isolated nodes have zero edges",
    isolated_result.edge_count == 0,
)

check(
    "100 isolated nodes have zero violations",
    isolated_result.violations == (),
)


# ============================================================================
# 13. Require-valid behavior
# ============================================================================

required_valid = require_valid_dependency_graph(
    large_graph
)

check(
    "Require-valid returns deterministic valid result",
    required_valid == large_result,
)


caught = None

try:
    require_valid_dependency_graph(
        multi_self_graph
    )

except DependencyGraphValidationFailedError as exc:
    caught = exc

check(
    "Require-valid raises canonical validation failure",
    isinstance(
        caught,
        DependencyGraphValidationFailedError,
    ),
)

check(
    "Require-valid failure derives from DependencyValidationError",
    isinstance(
        caught,
        DependencyValidationError,
    ),
)

check(
    "Require-valid failure preserves exact result",
    caught is not None
    and caught.result
    == multi_self_result,
)

check(
    "Require-valid error contains canonical violation code",
    caught is not None
    and SELF_DEPENDENCY_VIOLATION_CODE
    in str(
        caught
    ),
)


# ============================================================================
# 14. Violation evidence immutability
# ============================================================================

sample_violation = (
    multi_self_result.violations[0]
)

blocked = False

try:
    sample_violation.code = "changed"

except Exception:
    blocked = True

check(
    "Violation dataclass immutable",
    blocked,
)


violation_mapping = (
    sample_violation.to_dict()
)

check(
    "Violation mapping MappingProxyType",
    isinstance(
        violation_mapping,
        MappingProxyType,
    ),
)

blocked = False

try:
    violation_mapping["code"] = "changed"

except Exception:
    blocked = True

check(
    "Violation mapping mutation blocked",
    blocked,
)


# ============================================================================
# 15. Result deep immutability
# ============================================================================

blocked = False

try:
    large_result.is_valid = False

except Exception:
    blocked = True

check(
    "Validation result immutable",
    blocked,
)


result_mapping = (
    multi_self_result.to_dict()
)

check(
    "Result to_dict MappingProxyType",
    isinstance(
        result_mapping,
        MappingProxyType,
    ),
)

check(
    "Result violations serialized as immutable tuple",
    isinstance(
        result_mapping[
            "violations"
        ],
        tuple,
    ),
)

check(
    "Result nested violation mapping immutable",
    isinstance(
        result_mapping[
            "violations"
        ][0],
        MappingProxyType,
    ),
)

blocked = False

try:
    result_mapping[
        "violations"
    ][0][
        "code"
    ] = "changed"

except Exception:
    blocked = True

check(
    "Result nested violation mutation blocked",
    blocked,
)


# ============================================================================
# 16. Snapshot integrity
# ============================================================================

snapshot = dependency_validation_snapshot(
    multi_self_graph
)

check(
    "Snapshot MappingProxyType",
    isinstance(
        snapshot,
        MappingProxyType,
    ),
)

check(
    "Snapshot validation version exact",
    snapshot[
        "validation_version"
    ]
    == DEPENDENCY_VALIDATION_VERSION,
)

check(
    "Snapshot schema exact",
    snapshot[
        "schema_version"
    ]
    == DEPENDENCY_VALIDATION_SCHEMA_VERSION,
)

check(
    "Snapshot graph version exact",
    snapshot[
        "graph_version"
    ]
    == DEPENDENCY_GRAPH_VERSION,
)

check(
    "Snapshot validity exact",
    snapshot[
        "is_valid"
    ] is False,
)

check(
    "Snapshot failure count exact",
    snapshot[
        "checks_failed"
    ] == 50,
)

check(
    "Snapshot self-dependency count exact",
    snapshot[
        "self_dependency_count"
    ] == 50,
)

check(
    "Snapshot violations tuple immutable",
    isinstance(
        snapshot[
            "violations"
        ],
        tuple,
    ),
)

check(
    "Snapshot nested violation immutable",
    isinstance(
        snapshot[
            "violations"
        ][0],
        MappingProxyType,
    ),
)

blocked = False

try:
    snapshot[
        "violations"
    ][0][
        "message"
    ] = "changed"

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
    "Repeated large valid result deterministic",
    validate_dependency_graph(
        large_graph
    )
    == large_result,
)

check(
    "Repeated multi-self result deterministic",
    validate_dependency_graph(
        multi_self_graph
    )
    == multi_self_result,
)

check(
    "Repeated cycle result deterministic",
    validate_dependency_graph(
        large_cycle
    )
    == large_cycle_result,
)

snapshot_again = dependency_validation_snapshot(
    multi_self_graph
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
# 18. Architecture evidence
# ============================================================================

architecture = (
    explain_dependency_validation_v4_2()
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
    architecture[
        "phase"
    ] == "4.2",
)

check(
    "Architecture component exact",
    architecture[
        "component"
    ]
    == "Dependency Validation",
)

check(
    "Architecture version exact",
    architecture[
        "version"
    ]
    == DEPENDENCY_VALIDATION_VERSION,
)

check(
    "Architecture schema exact",
    architecture[
        "schema_version"
    ]
    == DEPENDENCY_VALIDATION_SCHEMA_VERSION,
)

check(
    "Architecture input authority exact",
    architecture[
        "input_authority"
    ]
    == "Phase 4.1 DependencyGraph",
)

check(
    "Architecture upstream version exact",
    architecture[
        "upstream_version"
    ]
    == DEPENDENCY_GRAPH_VERSION,
)


rules = architecture[
    "validation_rules"
]

check(
    "Validation rules immutable",
    isinstance(
        rules,
        MappingProxyType,
    ),
)

check(
    "Graph type rule exact",
    rules[
        "graph_type"
    ]
    == "DependencyGraph",
)

check(
    "Graph version rule exact",
    rules[
        "graph_version"
    ]
    == DEPENDENCY_GRAPH_VERSION,
)

check(
    "Node identity rule exact",
    rules[
        "node_identity"
    ]
    == "canonical stage_id",
)

check(
    "Edge identity rule exact",
    rules[
        "edge_identity"
    ]
    == "DependencyEdge",
)

check(
    "Endpoint membership rule exact",
    rules[
        "edge_endpoint_membership"
    ]
    == "required",
)

check(
    "Self-dependency rule exact",
    rules[
        "self_dependency"
    ]
    == "prohibited",
)

check(
    "Isolated-node rule exact",
    rules[
        "isolated_nodes"
    ]
    == "valid",
)

check(
    "Cycle rule explicitly deferred to 4.3",
    rules[
        "cycles"
    ]
    == (
        "not evaluated; "
        "Phase 4.3 owns cycle detection"
    ),
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
        "4.3":
            "Cycle Detection",
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
        "4.3"
    ] = "changed"

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
    "4.2 read-only",
    execution[
        "read_only"
    ] is True,
)

check(
    "4.2 deterministic",
    execution[
        "deterministic"
    ] is True,
)

check(
    "4.2 side-effect free",
    execution[
        "side_effect_free"
    ] is True,
)

check(
    "4.2 graph mutation disabled",
    execution[
        "graph_mutation"
    ] is False,
)

check(
    "4.2 Runtime execution disabled",
    execution[
        "runtime_execution"
    ] is False,
)

check(
    "4.2 persistence disabled",
    execution[
        "persistence"
    ] is False,
)


check(
    "Repeated architecture deterministic",
    dict(
        explain_dependency_validation_v4_2()
    )
    == dict(
        architecture
    ),
)


# ============================================================================
# 19. Static import boundary
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
}

check(
    "4.2 imports only frozen 4.1",
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
    "detect_cycle",
    "find_cycle",
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
    "4.2 performs no cycle/runtime/planning/persistence execution",
    not bad_calls,
    repr(
        bad_calls
    ),
)


# ============================================================================
# 21. Source authority assertions
# ============================================================================

check(
    "Source declares semantic validation ownership",
    "dependency-graph semantic validity"
    in source,
)

check(
    "Source declares self-dependency rejection ownership",
    "self-dependency rejection"
    in source,
)

check(
    "Source explicitly defers cycle detection",
    "cycle detection (Phase 4.3)"
    in source,
)

check(
    "Source explicitly defers topological sorting",
    "topological sorting (Phase 4.3 / 4.5)"
    in source,
)

check(
    "Source explicitly defers runnable-stage resolution",
    "runnable-stage resolution (Phase 4.4)"
    in source,
)

check(
    "Source explicitly defers execution planning",
    "execution planning (Phase 4.5)"
    in source,
)

check(
    "Source explicitly excludes Runtime execution",
    "Runtime execution (Phase 5)"
    in source,
)

check(
    "Source explicitly excludes stage handoff",
    "stage handoff (Phase 6)"
    in source,
)

check(
    "Source explicitly excludes persistence",
    "persistence (Phase 8)"
    in source,
)

check(
    "Source explicitly excludes recovery",
    "recovery (Phase 9)"
    in source,
)

check(
    "Source explicitly states cycles remain valid in 4.2",
    (
        "A cyclic graph without a self-dependency "
        "remains valid at Phase 4.2."
    )
    in source,
)


# ============================================================================
# 22. SHA candidate
# ============================================================================

actual_42_sha = sha256(
    PHASE_42
)

check(
    "Phase 4.2 SHA matches installation candidate",
    actual_42_sha
    == EXPECTED_42_CANDIDATE_SHA,
    actual_42_sha,
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
    "PHASE 4.2 — DEPENDENCY VALIDATION FINAL CERTIFICATION",
    "=" * 104,
    "",
    (
        "Dependency Validation Version: "
        + DEPENDENCY_VALIDATION_VERSION
    ),
    (
        "Dependency Validation Schema: "
        + DEPENDENCY_VALIDATION_SCHEMA_VERSION
    ),
    "",
    (
        "Frozen Phase 4.1 SHA256: "
        + actual_41_sha
    ),
    (
        "Phase 4.2 SHA256: "
        + actual_42_sha
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
print("PHASE 4.2 FINAL CERTIFICATION RESULT")
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
    "REPORT:",
    REPORT.name,
)
print("=" * 104)


raise SystemExit(
    0
    if failed == 0
    else 1
)
