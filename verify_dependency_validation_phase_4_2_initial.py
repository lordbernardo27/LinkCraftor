from __future__ import annotations

import ast
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

FILE = ROOT / (
    "backend/server/coordination/"
    "dependency_planning/dependency_validation.py"
)

PHASE_41 = ROOT / (
    "backend/server/coordination/"
    "dependency_planning/dependency_graph.py"
)

REPORT = ROOT / (
    "dependency_validation_phase_4_2_initial_verification.txt"
)

EXPECTED_41_SHA = (
    "4F6BA62D011C31D9D851FBBABC37C12B"
    "7DDAA1FD9A91E34788EBCE25741A1F70"
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
    exc_type,
    func,
):
    try:
        func()

    except exc_type:
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
            "expected exception not raised",
        )


print()
print("=" * 100)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 4.2 — DEPENDENCY VALIDATION INITIAL VERIFICATION")
print("=" * 100)


# ============================================================================
# 1. File / syntax / import
# ============================================================================

check(
    "Canonical Phase 4.2 file exists",
    FILE.exists(),
    str(
        FILE.relative_to(ROOT)
    ),
)

source = FILE.read_text(
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
# 2. Frozen Phase 4.1 upstream integrity
# ============================================================================

import hashlib

actual_41_sha = hashlib.sha256(
    PHASE_41.read_bytes()
).hexdigest().upper()

check(
    "Frozen Phase 4.1 SHA exact",
    actual_41_sha
    == EXPECTED_41_SHA,
    actual_41_sha,
)


# ============================================================================
# 3. Canonical identity
# ============================================================================

check(
    "Validation version exact",
    DEPENDENCY_VALIDATION_VERSION
    == "dependency_validation_v4.2.0",
)

check(
    "Validation schema exact",
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
    "Graph-invariant violation code exact",
    GRAPH_INVARIANT_VIOLATION_CODE
    == "dependency_graph_invariant_violation",
)


# ============================================================================
# 4. Exact contracts
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
    len(violation_fields) == 4,
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
    len(result_fields) == 10,
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
# 5. Request type guard
# ============================================================================

for label, value in (
    ("None", None),
    ("string", "graph"),
    ("integer", 123),
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
# 6. Valid graph
# ============================================================================

valid_graph = create_dependency_graph(
    workflow_id="workflow-valid",
    node_ids=(
        "isolated",
    ),
    edges=(
        ("a", "b"),
        ("b", "c"),
    ),
)

valid_result = validate_dependency_graph(
    valid_graph
)

check(
    "Valid graph accepted",
    valid_result.is_valid is True,
)

check(
    "Valid graph checks all passed",
    valid_result.checks_passed
    == valid_result.checks_run,
)

check(
    "Valid graph failed count zero",
    valid_result.checks_failed == 0,
)

check(
    "Valid graph violations empty",
    valid_result.violations == (),
)

check(
    "Valid graph node count exact",
    valid_result.node_count == 4,
)

check(
    "Valid graph edge count exact",
    valid_result.edge_count == 2,
)

check(
    "Valid graph self-dependency count zero",
    valid_result.self_dependency_count == 0,
)

check(
    "Valid graph version exact",
    valid_result.graph_version
    == DEPENDENCY_GRAPH_VERSION,
)

check(
    "Valid result version exact",
    valid_result.validation_version
    == DEPENDENCY_VALIDATION_VERSION,
)


# ============================================================================
# 7. Self-dependency rejection
# ============================================================================

self_graph = create_dependency_graph(
    workflow_id="workflow-self",
    edges=(
        ("a", "a"),
    ),
)

self_result = validate_dependency_graph(
    self_graph
)

check(
    "Self-dependent graph invalid",
    self_result.is_valid is False,
)

check(
    "Self-dependent graph failed count exact",
    self_result.checks_failed == 1,
)

check(
    "Self-dependent graph self count exact",
    self_result.self_dependency_count == 1,
)

check(
    "Self-dependent graph one violation",
    len(
        self_result.violations
    ) == 1,
)

violation = self_result.violations[0]

check(
    "Self-dependency violation code exact",
    violation.code
    == SELF_DEPENDENCY_VIOLATION_CODE,
)

check(
    "Self-dependency violation message exact",
    violation.message
    == "A stage must not depend on itself.",
)

check(
    "Self-dependency prerequisite exact",
    violation.prerequisite_stage_id == "a",
)

check(
    "Self-dependency dependent exact",
    violation.dependent_stage_id == "a",
)


# ============================================================================
# 8. Multiple self-dependencies
# ============================================================================

multi_self_graph = create_dependency_graph(
    workflow_id="workflow-multi-self",
    edges=(
        ("a", "a"),
        ("b", "b"),
        ("c", "d"),
        ("z", "z"),
    ),
)

multi_self_result = validate_dependency_graph(
    multi_self_graph
)

check(
    "Multiple self-dependencies invalidate graph",
    multi_self_result.is_valid is False,
)

check(
    "Multiple self-dependency count exact",
    multi_self_result.self_dependency_count == 3,
)

check(
    "Multiple self-dependencies produce three violations",
    len(
        multi_self_result.violations
    ) == 3,
)

check(
    "Multiple self-dependency failed checks exact",
    multi_self_result.checks_failed == 3,
)

check(
    "Self-dependency evidence deterministic",
    tuple(
        (
            item.prerequisite_stage_id,
            item.dependent_stage_id,
        )
        for item
        in multi_self_result.violations
    )
    == (
        ("a", "a"),
        ("b", "b"),
        ("z", "z"),
    ),
)


# ============================================================================
# 9. CRITICAL Phase boundary — cycles allowed in 4.2
# ============================================================================

two_cycle = create_dependency_graph(
    workflow_id="two-cycle",
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
    "Two-node cycle has zero 4.2 violations",
    two_cycle_result.violations == (),
)


three_cycle = create_dependency_graph(
    workflow_id="three-cycle",
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
    "Three-node cycle has zero 4.2 failures",
    three_cycle_result.checks_failed == 0,
)


branch_cycle = create_dependency_graph(
    workflow_id="branch-cycle",
    edges=(
        ("start", "a"),
        ("start", "b"),
        ("a", "join"),
        ("b", "join"),
        ("join", "start"),
    ),
)

branch_cycle_result = validate_dependency_graph(
    branch_cycle
)

check(
    "Branch/join cycle remains valid in 4.2",
    branch_cycle_result.is_valid is True,
)


# ============================================================================
# 10. Isolated / empty graphs valid
# ============================================================================

isolated = create_dependency_graph(
    workflow_id="isolated",
    node_ids=(
        "a",
        "b",
        "c",
    ),
)

isolated_result = validate_dependency_graph(
    isolated
)

check(
    "Isolated-node graph valid",
    isolated_result.is_valid is True,
)

check(
    "Isolated-node graph edge count zero",
    isolated_result.edge_count == 0,
)


empty = create_dependency_graph(
    workflow_id="empty"
)

empty_result = validate_dependency_graph(
    empty
)

check(
    "Empty graph valid",
    empty_result.is_valid is True,
)

check(
    "Empty graph checks passed",
    empty_result.checks_failed == 0,
)


# ============================================================================
# 11. Require-valid guard
# ============================================================================

required_valid = require_valid_dependency_graph(
    valid_graph
)

check(
    "Require-valid returns original valid result semantics",
    required_valid == valid_result,
)


caught = None

try:
    require_valid_dependency_graph(
        self_graph
    )

except DependencyGraphValidationFailedError as exc:
    caught = exc

check(
    "Require-valid raises canonical failure error",
    isinstance(
        caught,
        DependencyGraphValidationFailedError,
    ),
)

check(
    "Failure error is DependencyValidationError",
    isinstance(
        caught,
        DependencyValidationError,
    ),
)

check(
    "Failure error preserves result",
    caught is not None
    and caught.result == self_result,
)

check(
    "Failure error message includes violation code",
    caught is not None
    and SELF_DEPENDENCY_VIOLATION_CODE
    in str(caught),
)


# ============================================================================
# 12. Result / evidence immutability
# ============================================================================

blocked = False

try:
    valid_result.is_valid = False

except Exception:
    blocked = True

check(
    "ValidationResult immutable",
    blocked,
)


blocked = False

try:
    self_result.violations += (
        violation,
    )

except Exception:
    blocked = True

check(
    "ValidationResult violations tuple immutable",
    blocked,
)


violation_dict = violation.to_dict()

check(
    "Violation to_dict immutable",
    isinstance(
        violation_dict,
        MappingProxyType,
    ),
)

blocked = False

try:
    violation_dict["code"] = "changed"

except Exception:
    blocked = True

check(
    "Violation to_dict mutation blocked",
    blocked,
)


result_dict = valid_result.to_dict()

check(
    "Result to_dict immutable",
    isinstance(
        result_dict,
        MappingProxyType,
    ),
)

check(
    "Result to_dict violations tuple exact",
    isinstance(
        result_dict["violations"],
        tuple,
    ),
)

blocked = False

try:
    result_dict["is_valid"] = False

except Exception:
    blocked = True

check(
    "Result to_dict mutation blocked",
    blocked,
)


# ============================================================================
# 13. Snapshot
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
    "Snapshot version exact",
    snapshot["validation_version"]
    == DEPENDENCY_VALIDATION_VERSION,
)

check(
    "Snapshot schema exact",
    snapshot["schema_version"]
    == DEPENDENCY_VALIDATION_SCHEMA_VERSION,
)

check(
    "Snapshot graph version exact",
    snapshot["graph_version"]
    == DEPENDENCY_GRAPH_VERSION,
)

check(
    "Snapshot invalid flag exact",
    snapshot["is_valid"] is False,
)

check(
    "Snapshot self-dependency count exact",
    snapshot["self_dependency_count"]
    == 3,
)

check(
    "Snapshot violations immutable tuple",
    isinstance(
        snapshot["violations"],
        tuple,
    ),
)

check(
    "Snapshot nested violation immutable",
    isinstance(
        snapshot["violations"][0],
        MappingProxyType,
    ),
)

blocked = False

try:
    snapshot["violations"][0]["code"] = "changed"

except Exception:
    blocked = True

check(
    "Snapshot deep mutation blocked",
    blocked,
)


# ============================================================================
# 14. Architecture evidence
# ============================================================================

architecture = explain_dependency_validation_v4_2()

check(
    "Architecture MappingProxyType",
    isinstance(
        architecture,
        MappingProxyType,
    ),
)

check(
    "Architecture phase exact",
    architecture["phase"] == "4.2",
)

check(
    "Architecture component exact",
    architecture["component"]
    == "Dependency Validation",
)

check(
    "Architecture version exact",
    architecture["version"]
    == DEPENDENCY_VALIDATION_VERSION,
)

check(
    "Architecture schema exact",
    architecture["schema_version"]
    == DEPENDENCY_VALIDATION_SCHEMA_VERSION,
)

check(
    "Architecture input authority exact",
    architecture["input_authority"]
    == "Phase 4.1 DependencyGraph",
)

check(
    "Architecture upstream version exact",
    architecture["upstream_version"]
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
    "Self-dependency policy prohibited",
    rules["self_dependency"]
    == "prohibited",
)

check(
    "Isolated nodes valid",
    rules["isolated_nodes"]
    == "valid",
)

check(
    "Cycle policy deferred to 4.3",
    rules["cycles"]
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
    dict(future)
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
    future["4.3"] = "MUTATED"

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
    execution["read_only"] is True,
)

check(
    "Deterministic exact",
    execution["deterministic"] is True,
)

check(
    "Side-effect free exact",
    execution["side_effect_free"] is True,
)

check(
    "Graph mutation false",
    execution["graph_mutation"] is False,
)

check(
    "Runtime execution false",
    execution["runtime_execution"] is False,
)

check(
    "Persistence false",
    execution["persistence"] is False,
)


# ============================================================================
# 15. Determinism
# ============================================================================

check(
    "Repeated valid validation deterministic",
    validate_dependency_graph(
        valid_graph
    )
    == valid_result,
)

check(
    "Repeated invalid validation deterministic",
    validate_dependency_graph(
        multi_self_graph
    )
    == multi_self_result,
)

check(
    "Repeated snapshot deterministic",
    dict(
        dependency_validation_snapshot(
            multi_self_graph
        )
    )
    == dict(
        snapshot
    ),
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
# 16. Static architecture boundary
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


allowed_imports = {
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
        allowed_imports
    ),
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
    "detect_cycle",
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
# 17. Source boundary assertions
# ============================================================================

check(
    "Source states self-dependency rejection ownership",
    "self-dependency rejection"
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
    "Runtime execution (Phase 5)"
    in source,
)

check(
    "Source explicitly excludes persistence",
    "persistence (Phase 8)"
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
# FINAL
# ============================================================================

passed = sum(
    1
    for _, ok, _
    in checks
    if ok
)

failed = (
    len(checks)
    - passed
)


report_lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 4.2 — DEPENDENCY VALIDATION INITIAL VERIFICATION",
    "=" * 100,
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
print("PHASE 4.2 INITIAL VERIFICATION RESULT")
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
