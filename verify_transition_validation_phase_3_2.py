from __future__ import annotations

import ast
import hashlib
import importlib
import json
from pathlib import Path

from backend.server.coordination.workflow_lifecycle.transition_validation import (
    TRANSITION_VALIDATION_VERSION,
    TRANSITION_VALIDATION_SCHEMA_VERSION,
    VIOLATION_CURRENT_STATE_INVALID,
    VIOLATION_REQUESTED_STATE_INVALID,
    VIOLATION_TRANSITION_NOT_DECLARED,
    TransitionValidationResult,
    TransitionValidationError,
    InvalidWorkflowTransitionError,
    validate_workflow_transition,
    require_valid_workflow_transition,
    explain_transition_validation_v3_2,
)

from backend.server.coordination.workflow_lifecycle.state_machine import (
    WORKFLOW_STATE_MACHINE_VERSION,
    workflow_states,
    transition_edges,
)

from backend.server.coordination.universal_workflows.contract import (
    UniversalWorkflowStatus,
)


TARGET = Path(
    "backend/server/coordination/"
    "workflow_lifecycle/transition_validation.py"
)

STATE_MACHINE = Path(
    "backend/server/coordination/"
    "workflow_lifecycle/state_machine.py"
)

REPORT = Path(
    "transition_validation_phase_3_2_certification.txt"
)

checks = []


def check(
    name,
    condition,
    detail="",
):
    ok = bool(condition)

    checks.append(
        (
            name,
            ok,
            detail,
        )
    )

    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if detail:
        print(
            f"       {detail}"
        )

    return ok


print()
print("=" * 86)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 3.2 TRANSITION VALIDATION CERTIFICATION")
print("=" * 86)


# ============================================================================
# 1. File / syntax / import
# ============================================================================

check(
    "Canonical Transition Validation file exists",
    TARGET.exists(),
    str(TARGET),
)

source = TARGET.read_text(
    encoding="utf-8-sig"
)

try:
    ast.parse(source)
    syntax_ok = True
except SyntaxError as exc:
    syntax_ok = False
    print(exc)

check(
    "Python syntax parses successfully",
    syntax_ok,
)


try:
    importlib.import_module(
        "backend.server.coordination."
        "workflow_lifecycle.transition_validation"
    )
    import_ok = True
except Exception as exc:
    import_ok = False
    print(repr(exc))

check(
    "Transition Validation imports successfully",
    import_ok,
)


# ============================================================================
# 2. Identity
# ============================================================================

check(
    "Transition Validation version is canonical",
    TRANSITION_VALIDATION_VERSION
    == "transition_validation_v3.2.0",
)

check(
    "Transition Validation schema is canonical",
    TRANSITION_VALIDATION_SCHEMA_VERSION
    == "transition_validation_schema_v1",
)

check(
    "Frozen Workflow State Machine version is canonical",
    WORKFLOW_STATE_MACHINE_VERSION
    == "workflow_state_machine_v3.1.0",
)


# ============================================================================
# 3. Violation vocabulary
# ============================================================================

check(
    "current_state_invalid violation code is canonical",
    VIOLATION_CURRENT_STATE_INVALID
    == "current_state_invalid",
)

check(
    "requested_state_invalid violation code is canonical",
    VIOLATION_REQUESTED_STATE_INVALID
    == "requested_state_invalid",
)

check(
    "transition_not_declared violation code is canonical",
    VIOLATION_TRANSITION_NOT_DECLARED
    == "transition_not_declared",
)


# ============================================================================
# 4. Every 3.1 declared edge validates
# ============================================================================

declared_edges = transition_edges()

check(
    "Frozen Phase 3.1 exposes 32 declared edges",
    len(declared_edges) == 32,
)

for current, requested in declared_edges:

    result = validate_workflow_transition(
        current,
        requested,
    )

    check(
        (
            "Declared edge validates: "
            f"{current.value}->{requested.value}"
        ),
        (
            isinstance(
                result,
                TransitionValidationResult,
            )
            and result.is_valid is True
            and result.current_state == current
            and result.requested_state == requested
            and result.violations == ()
            and result.checked_rule_count == 3
        ),
    )


# ============================================================================
# 5. Every undeclared state-pair is invalid
# ============================================================================

states = workflow_states()

declared_edge_set = set(
    declared_edges
)

undeclared_count = 0

for current in states:

    for requested in states:

        if (
            current,
            requested,
        ) in declared_edge_set:
            continue

        undeclared_count += 1

        result = validate_workflow_transition(
            current,
            requested,
        )

        check(
            (
                "Undeclared edge rejected: "
                f"{current.value}->{requested.value}"
            ),
            (
                result.is_valid is False
                and result.current_state == current
                and result.requested_state == requested
                and result.checked_rule_count == 3
                and len(result.violations) == 1
                and result.violations[0]["code"]
                == VIOLATION_TRANSITION_NOT_DECLARED
            ),
        )


check(
    "Undeclared edge count is 68",
    undeclared_count == 68,
)


# ============================================================================
# 6. Same-state transitions are invalid
# ============================================================================

for state in states:

    result = validate_workflow_transition(
        state,
        state,
    )

    check(
        f"Self-transition rejected: {state.value}->{state.value}",
        (
            result.is_valid is False
            and result.violations[0]["code"]
            == VIOLATION_TRANSITION_NOT_DECLARED
        ),
    )


# ============================================================================
# 7. Terminal outgoing requests are invalid
# ============================================================================

terminal_states = (
    UniversalWorkflowStatus.COMPLETED,
    UniversalWorkflowStatus.FAILED,
    UniversalWorkflowStatus.CANCELLED,
    UniversalWorkflowStatus.ABORTED,
)

for terminal in terminal_states:

    for requested in states:

        result = validate_workflow_transition(
            terminal,
            requested,
        )

        check(
            (
                "Terminal outgoing transition rejected: "
                f"{terminal.value}->{requested.value}"
            ),
            (
                result.is_valid is False
                and result.violations[0]["code"]
                == VIOLATION_TRANSITION_NOT_DECLARED
            ),
        )


# ============================================================================
# 8. Invalid current-state input
# ============================================================================

invalid_current_inputs = (
    "UNKNOWN",
    "",
    "   ",
    None,
    123,
    [],
    {},
)

for value in invalid_current_inputs:

    result = validate_workflow_transition(
        value,
        "RUNNING",
    )

    check(
        f"Invalid current input rejected: {value!r}",
        (
            result.is_valid is False
            and result.current_state is None
            and result.requested_state is None
            and result.checked_rule_count == 1
            and len(result.violations) == 1
            and result.violations[0]["code"]
            == VIOLATION_CURRENT_STATE_INVALID
            and result.violations[0]["field"]
            == "current_state"
        ),
    )


# ============================================================================
# 9. Invalid requested-state input
# ============================================================================

invalid_requested_inputs = (
    "UNKNOWN",
    "",
    "   ",
    None,
    123,
    [],
    {},
)

for value in invalid_requested_inputs:

    result = validate_workflow_transition(
        "RUNNING",
        value,
    )

    check(
        f"Invalid requested input rejected: {value!r}",
        (
            result.is_valid is False
            and result.current_state
            == UniversalWorkflowStatus.RUNNING
            and result.requested_state is None
            and result.checked_rule_count == 2
            and len(result.violations) == 1
            and result.violations[0]["code"]
            == VIOLATION_REQUESTED_STATE_INVALID
            and result.violations[0]["field"]
            == "requested_state"
        ),
    )


# ============================================================================
# 10. Normalization
# ============================================================================

normalization_cases = (
    (
        " running ",
        " waiting ",
        UniversalWorkflowStatus.RUNNING,
        UniversalWorkflowStatus.WAITING,
    ),
    (
        "ready",
        "paused",
        UniversalWorkflowStatus.READY,
        UniversalWorkflowStatus.PAUSED,
    ),
    (
        " recovering ",
        " failed ",
        UniversalWorkflowStatus.RECOVERING,
        UniversalWorkflowStatus.FAILED,
    ),
)

for (
    current,
    requested,
    expected_current,
    expected_requested,
) in normalization_cases:

    result = validate_workflow_transition(
        current,
        requested,
    )

    check(
        f"Normalization succeeds: {current!r}->{requested!r}",
        (
            result.is_valid
            and result.current_state == expected_current
            and result.requested_state == expected_requested
        ),
    )


# ============================================================================
# 11. Result immutability
# ============================================================================

sample_invalid = validate_workflow_transition(
    "WAITING",
    "COMPLETED",
)

immutable_result = False

try:
    sample_invalid.is_valid = True
except Exception:
    immutable_result = True

check(
    "TransitionValidationResult is immutable",
    immutable_result,
)


immutable_violation = False

try:
    sample_invalid.violations[0]["code"] = "changed"
except Exception:
    immutable_violation = True

check(
    "Violation evidence is immutable",
    immutable_violation,
)


sample_dict = sample_invalid.to_dict()

immutable_dict = False

try:
    sample_dict["is_valid"] = True
except Exception:
    immutable_dict = True

check(
    "Result mapping is immutable",
    immutable_dict,
)


# ============================================================================
# 12. Result evidence
# ============================================================================

valid_result = validate_workflow_transition(
    "RUNNING",
    "WAITING",
)

check(
    "Valid result has zero violations",
    valid_result.violations == (),
)

check(
    "Valid result evaluates all three rules",
    valid_result.checked_rule_count == 3,
)

check(
    "Valid result carries canonical validation version",
    valid_result.validation_version
    == TRANSITION_VALIDATION_VERSION,
)


invalid_result = validate_workflow_transition(
    "WAITING",
    "COMPLETED",
)

check(
    "Invalid edge result carries transition_not_declared",
    invalid_result.violations[0]["code"]
    == VIOLATION_TRANSITION_NOT_DECLARED,
)

check(
    "Invalid edge result identifies transition field",
    invalid_result.violations[0]["field"]
    == "transition",
)

check(
    "Invalid edge evidence carries normalized current state",
    invalid_result.violations[0]["current_state"]
    == "WAITING",
)

check(
    "Invalid edge evidence carries normalized requested state",
    invalid_result.violations[0]["requested_state"]
    == "COMPLETED",
)


# ============================================================================
# 13. require-style API
# ============================================================================

required_valid = require_valid_workflow_transition(
    "RUNNING",
    "WAITING",
)

check(
    "Require API returns valid result",
    required_valid.is_valid is True,
)


raised = False
captured = None

try:
    require_valid_workflow_transition(
        "FAILED",
        "RECOVERING",
    )
except InvalidWorkflowTransitionError as exc:
    raised = True
    captured = exc

check(
    "Require API raises InvalidWorkflowTransitionError",
    raised,
)

check(
    "InvalidWorkflowTransitionError inherits base validation error",
    (
        captured is not None
        and isinstance(
            captured,
            TransitionValidationError,
        )
    ),
)

check(
    "Require API exception carries validation result",
    (
        captured is not None
        and captured.result.is_valid is False
        and captured.result.violations[0]["code"]
        == VIOLATION_TRANSITION_NOT_DECLARED
    ),
)


# ============================================================================
# 14. Architecture declaration
# ============================================================================

explanation = explain_transition_validation_v3_2()

check(
    "Architecture declaration identifies Phase 3.2",
    explanation["phase"] == "3.2",
)

check(
    "Architecture declaration identifies Transition Validation",
    explanation["component"]
    == "Transition Validation",
)

check(
    "Architecture declaration references frozen 3.1 version",
    explanation["state_machine_version"]
    == WORKFLOW_STATE_MACHINE_VERSION,
)

check(
    "Validation direction is canonical",
    explanation["validation_direction"]
    == "current_state_to_requested_state",
)

check(
    "Exactly three validation rules are declared",
    len(explanation["validation_rules"]) == 3,
)

check(
    "Violation vocabulary is exact",
    explanation["violation_codes"]
    == (
        "current_state_invalid",
        "requested_state_invalid",
        "transition_not_declared",
    ),
)


# ============================================================================
# 15. Ownership / exclusions
# ============================================================================

required_owns = (
    "requested workflow transition validation",
    "current/requested lifecycle state normalization",
    "exact edge validation against frozen Phase 3.1",
    "deterministic transition-validation result",
    "immutable validation violations/evidence",
    (
        "canonical invalid-transition error "
        "for require-style API"
    ),
    "validation inspection/explanation",
)

for item in required_owns:

    check(
        f"Transition Validation owns: {item}",
        item in explanation["owns"],
    )


required_exclusions = (
    "workflow lifecycle graph definition",
    "workflow status vocabulary",
    "workflow status mutation",
    "workflow object reconstruction",
    "lifecycle history",
    "transition timestamp generation",
    "terminal-state protection enforcement",
    "workflow persistence",
    "checkpointing",
    "pause execution behavior",
    "resume execution behavior",
    "recovery execution",
    "recovery policy",
    "coordinator execution",
    "Runtime Registration",
    "Runtime jobs",
    "dependency planning",
    "stage result handoff",
)

for item in required_exclusions:

    check(
        f"Transition Validation excludes: {item}",
        item in explanation["does_not_own"],
    )


# ============================================================================
# 16. Future authority
# ============================================================================

check(
    "3.3 remains Lifecycle History authority",
    explanation["future_authority"]["3.3"]
    == "Lifecycle History",
)

check(
    "3.4 remains Terminal-State Protection authority",
    explanation["future_authority"]["3.4"]
    == "Terminal-State Protection",
)

check(
    "Phase 8 remains persistence authority",
    explanation["future_authority"]["8.0"]
    == "Workflow State Persistence",
)

check(
    "Phase 9 remains recovery authority",
    explanation["future_authority"]["9.0"]
    == "Coordination Recovery",
)


# ============================================================================
# 17. Static import boundary
# ============================================================================

tree = ast.parse(source)

backend_imports = []

for node in ast.walk(tree):

    if isinstance(node, ast.Import):

        for alias in node.names:

            if alias.name.startswith("backend."):
                backend_imports.append(alias.name)

    elif isinstance(node, ast.ImportFrom):

        module = node.module or ""

        if module.startswith("backend."):
            backend_imports.append(module)


allowed_backend_imports = {
    (
        "backend.server.coordination."
        "universal_workflows.contract"
    ),
    (
        "backend.server.coordination."
        "workflow_lifecycle.state_machine"
    ),
}

check(
    "Transition Validation imports only canonical lifecycle dependencies",
    set(backend_imports).issubset(
        allowed_backend_imports
    ),
    json.dumps(backend_imports),
)


forbidden_import_fragments = (
    "backend.server.runtime",
    "backend.server.workers",
    "backend.server.jobs",
    "backend.server.pipelines",
    "backend.server.routes",
    "backend.server.coordination.workflow_registry",
    "backend.server.coordination.coordinator_registry",
    "backend.server.coordination.registration_validation",
    "backend.server.coordination.version_management",
)

violating_imports = [
    item
    for item in backend_imports
    if any(
        fragment in item
        for fragment in forbidden_import_fragments
    )
]

check(
    "Transition Validation has no runtime/registry/execution imports",
    not violating_imports,
    json.dumps(violating_imports),
)


# ============================================================================
# 18. Static authority boundary
# ============================================================================

forbidden_markers = (
    "transition_universal_orchestration_state",
    "dispatch(",
    "execute(",
    "run_coordinator(",
    "invoke_coordinator(",
    "register_workflow",
    "register_coordinator",
    "set_preferred_",
    "write_text(",
    "write_bytes(",
    "sqlite",
    "boto3",
    "requests.",
    "datetime.now(",
    "datetime.utcnow(",
)

violations = [
    marker
    for marker in forbidden_markers
    if marker in source
]

check(
    "Transition Validation performs no execution/registration/persistence",
    not violations,
    json.dumps(violations),
)


# ============================================================================
# 19. No second transition graph
# ============================================================================

graph_markers = (
    "_WORKFLOW_TRANSITION_GRAPH",
    "_ALLOWED_TRANSITIONS",
    "allowed_transitions = {",
    "transition_graph = {",
)

duplicate_graph_markers = [
    marker
    for marker in graph_markers
    if marker in source
]

check(
    "Transition Validation defines no second transition graph",
    not duplicate_graph_markers,
    json.dumps(duplicate_graph_markers),
)


check(
    "Transition Validation consumes frozen has_transition_edge",
    "has_transition_edge("
    in source,
)


# ============================================================================
# 20. Frozen hash integrity
# ============================================================================

frozen_files = (
    (
        "Phase 3.1 Workflow State Machine",
        STATE_MACHINE,
        (
            "144327A4E9C8989FCF0F4DBD10BCF6D7"
            "203F503930D81CB8E24644D86D2BB662"
        ),
    ),
    (
        "Phase 2.1 Workflow Registry",
        Path(
            "backend/server/coordination/"
            "workflow_registry/registry.py"
        ),
        (
            "34786F74443BAC9049F3CD805CBF8BDB"
            "6275C6EF05B94C9BF42579E114CA4564"
        ),
    ),
    (
        "Phase 2.2 Coordinator Registration",
        Path(
            "backend/server/coordination/"
            "coordinator_registry/registry.py"
        ),
        (
            "C9E324DF0C4D5AEA8D1D0C91D8FB3A3"
            "B479BB9A0830B0C4494186C01C298F071"
        ),
    ),
    (
        "Phase 2.3 Registration Validation",
        Path(
            "backend/server/coordination/"
            "registration_validation/validator.py"
        ),
        (
            "30853E34C6F09B89A2C67D50D91C06EB"
            "4B2436A12918DC4E26197EB6159E8453"
        ),
    ),
    (
        "Phase 2.4 Version Management",
        Path(
            "backend/server/coordination/"
            "version_management/manager.py"
        ),
        (
            "118B628ABFCA7CF74B218520D6CF6E0AD"
            "4AF2CD6FFE9FB7FE711927A68412E25"
        ),
    ),
)


for name, path, expected in frozen_files:

    actual = hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()

    check(
        f"Frozen {name} hash unchanged",
        actual == expected,
        actual,
    )


# ============================================================================
# 21. Canonical SHA256
# ============================================================================

sha256 = hashlib.sha256(
    TARGET.read_bytes()
).hexdigest().upper()

print()
print("Canonical SHA256:")
print(sha256)


# ============================================================================
# 22. Final result
# ============================================================================

passed = sum(
    1
    for _, ok, _ in checks
    if ok
)

failed = len(checks) - passed


lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 3.2 TRANSITION VALIDATION CERTIFICATION",
    "=" * 86,
    "",
    (
        "Transition Validation Version: "
        + TRANSITION_VALIDATION_VERSION
    ),
    (
        "Transition Validation Schema: "
        + TRANSITION_VALIDATION_SCHEMA_VERSION
    ),
    (
        "Workflow State Machine Version: "
        + WORKFLOW_STATE_MACHINE_VERSION
    ),
    "",
    "Validation Direction: current_state_to_requested_state",
    "Validation Rule Count: 3",
    (
        "Violation Codes: "
        "current_state_invalid, "
        "requested_state_invalid, "
        "transition_not_declared"
    ),
    "",
    f"Declared Phase-3.1 Edges Tested: {len(declared_edges)}",
    f"Undeclared State Pairs Tested: {undeclared_count}",
    "",
    "Workflow Mutation Authority: NONE",
    "Lifecycle History Authority: NONE (Phase 3.3)",
    "Terminal Protection Authority: NONE (Phase 3.4)",
    "Persistence Authority: NONE (Phase 8)",
    "Recovery Authority: NONE (Phase 9)",
    "Runtime Execution Authority: NONE",
    "",
    f"Checks: {len(checks)}",
    f"Passed: {passed}",
    f"Failed: {failed}",
    f"SHA256: {sha256}",
    "",
    (
        "STATUS: CERTIFICATION PASSED"
        if failed == 0
        else "STATUS: CERTIFICATION FAILED"
    ),
    "",
]


for name, ok, detail in checks:

    lines.append(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if detail:
        lines.append(
            f"    {detail}"
        )


REPORT.write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8",
)


print()
print("=" * 86)
print("CERTIFICATION RESULT")
print("=" * 86)
print(f"Checks: {len(checks)}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print()

print(
    "STATUS: CERTIFICATION PASSED"
    if failed == 0
    else "STATUS: CERTIFICATION FAILED"
)

print()
print(
    "REPORT:",
    REPORT,
)
print("=" * 86)

raise SystemExit(
    0 if failed == 0 else 1
)
