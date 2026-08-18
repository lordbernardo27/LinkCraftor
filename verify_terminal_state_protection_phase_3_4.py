from __future__ import annotations

import ast
import hashlib
import importlib
import json
from dataclasses import fields
from pathlib import Path

from backend.server.coordination.workflow_lifecycle.terminal_state_protection import (
    TERMINAL_STATE_PROTECTION_VERSION,
    TERMINAL_STATE_PROTECTION_SCHEMA_VERSION,
    TERMINAL_STATE_PROTECTION_RESULT_FIELD_COUNT,
    TERMINAL_STATE_MUTATION_PROHIBITED,
    TerminalStateProtectionError,
    TerminalStateMutationProhibitedError,
    InvalidTerminalStateProtectionRequestError,
    TerminalStateProtectionResult,
    inspect_terminal_state_protection,
    validate_terminal_state_mutation,
    require_terminal_state_mutation_allowed,
    terminal_state_protection_snapshot,
    explain_terminal_state_protection_v3_4,
)

from backend.server.coordination.workflow_lifecycle.transition_validation import (
    TRANSITION_VALIDATION_VERSION,
    VIOLATION_CURRENT_STATE_INVALID,
    VIOLATION_REQUESTED_STATE_INVALID,
    VIOLATION_TRANSITION_NOT_DECLARED,
    validate_workflow_transition,
)

from backend.server.coordination.workflow_lifecycle.state_machine import (
    WORKFLOW_STATE_MACHINE_VERSION,
    workflow_states,
    terminal_workflow_states,
    non_terminal_workflow_states,
)

from backend.server.coordination.universal_workflows.contract import (
    UniversalWorkflowStatus,
)


TARGET = Path(
    "backend/server/coordination/"
    "workflow_lifecycle/terminal_state_protection.py"
)

PHASE_33 = Path(
    "backend/server/coordination/"
    "workflow_lifecycle/lifecycle_history.py"
)

PHASE_32 = Path(
    "backend/server/coordination/"
    "workflow_lifecycle/transition_validation.py"
)

PHASE_31 = Path(
    "backend/server/coordination/"
    "workflow_lifecycle/state_machine.py"
)

REPORT = Path(
    "terminal_state_protection_phase_3_4_certification.txt"
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
print("=" * 92)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 3.4 TERMINAL-STATE PROTECTION CERTIFICATION")
print("=" * 92)


# ============================================================================
# 1. File / syntax / import
# ============================================================================

check(
    "Canonical Terminal-State Protection file exists",
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
        "workflow_lifecycle.terminal_state_protection"
    )
    import_ok = True
except Exception as exc:
    import_ok = False
    print(repr(exc))

check(
    "Terminal-State Protection imports successfully",
    import_ok,
)


# ============================================================================
# 2. Canonical identity
# ============================================================================

check(
    "Protection version is canonical",
    TERMINAL_STATE_PROTECTION_VERSION
    == "terminal_state_protection_v3.4.0",
)

check(
    "Protection schema is canonical",
    TERMINAL_STATE_PROTECTION_SCHEMA_VERSION
    == "terminal_state_protection_schema_v1",
)

check(
    "Protection result field count constant is 10",
    TERMINAL_STATE_PROTECTION_RESULT_FIELD_COUNT
    == 10,
)

check(
    "Terminal protection code is canonical",
    TERMINAL_STATE_MUTATION_PROHIBITED
    == "terminal_state_mutation_prohibited",
)

check(
    "Frozen Phase 3.2 version remains canonical",
    TRANSITION_VALIDATION_VERSION
    == "transition_validation_v3.2.0",
)

check(
    "Frozen Phase 3.1 version remains canonical",
    WORKFLOW_STATE_MACHINE_VERSION
    == "workflow_state_machine_v3.1.0",
)


# ============================================================================
# 3. Exact result schema
# ============================================================================

expected_fields = (
    "current_state",
    "requested_state",
    "current_state_is_terminal",
    "mutation_allowed",
    "protection_triggered",
    "code",
    "reason",
    "transition_validation_version",
    "state_machine_version",
    "protection_version",
)

actual_fields = tuple(
    field.name
    for field
    in fields(
        TerminalStateProtectionResult
    )
)

check(
    "TerminalStateProtectionResult has exactly 10 fields",
    len(actual_fields) == 10,
)

check(
    "TerminalStateProtectionResult field order is exact",
    actual_fields == expected_fields,
)


# ============================================================================
# 4. Canonical state model
# ============================================================================

all_states = workflow_states()
terminal_states = terminal_workflow_states()
non_terminal_states = non_terminal_workflow_states()

check(
    "Canonical workflow-state count is 10",
    len(all_states) == 10,
)

check(
    "Canonical terminal-state count is 4",
    len(terminal_states) == 4,
)

check(
    "Canonical non-terminal-state count is 6",
    len(non_terminal_states) == 6,
)

check(
    "Canonical terminal-state set is exact",
    set(terminal_states)
    == {
        UniversalWorkflowStatus.COMPLETED,
        UniversalWorkflowStatus.FAILED,
        UniversalWorkflowStatus.CANCELLED,
        UniversalWorkflowStatus.ABORTED,
    },
)

check(
    "Canonical non-terminal-state set is exact",
    set(non_terminal_states)
    == {
        UniversalWorkflowStatus.CREATED,
        UniversalWorkflowStatus.READY,
        UniversalWorkflowStatus.RUNNING,
        UniversalWorkflowStatus.WAITING,
        UniversalWorkflowStatus.PAUSED,
        UniversalWorkflowStatus.RECOVERING,
    },
)


# ============================================================================
# 5. Inspection - all 10 states
# ============================================================================

for state in all_states:

    result = inspect_terminal_state_protection(
        state
    )

    expected_terminal = (
        state
        in terminal_states
    )

    check(
        f"Inspection classification exact: {state.value}",
        (
            result.current_state == state
            and result.requested_state is None
            and result.current_state_is_terminal
            is expected_terminal
            and result.transition_validation_version
            == TRANSITION_VALIDATION_VERSION
            and result.state_machine_version
            == WORKFLOW_STATE_MACHINE_VERSION
            and result.protection_version
            == TERMINAL_STATE_PROTECTION_VERSION
        ),
    )

    if expected_terminal:

        check(
            f"Inspection protection exact: {state.value}",
            (
                result.mutation_allowed is False
                and result.protection_triggered is True
                and result.code
                == TERMINAL_STATE_MUTATION_PROHIBITED
            ),
        )

    else:

        check(
            f"Inspection unprotected exact: {state.value}",
            (
                result.mutation_allowed is True
                and result.protection_triggered is False
                and result.code is None
            ),
        )


# ============================================================================
# 6. FULL 10 x 10 CANONICAL MATRIX
#
# 100 ordered state pairs:
#
# terminal current states: 4 x 10 = 40
# non-terminal current states: 6 x 10 = 60
# ============================================================================

pair_count = 0
terminal_pair_count = 0
non_terminal_pair_count = 0
non_terminal_phase32_match_count = 0

for current in all_states:

    for requested in all_states:

        pair_count += 1

        protection = (
            validate_terminal_state_mutation(
                current,
                requested,
            )
        )

        phase32 = (
            validate_workflow_transition(
                current,
                requested,
            )
        )

        if current in terminal_states:

            terminal_pair_count += 1

            check(
                (
                    "Terminal pair protected: "
                    f"{current.value}->{requested.value}"
                ),
                (
                    protection.current_state
                    == current
                    and protection.requested_state
                    == requested
                    and protection.current_state_is_terminal
                    is True
                    and protection.mutation_allowed
                    is False
                    and protection.protection_triggered
                    is True
                    and protection.code
                    == TERMINAL_STATE_MUTATION_PROHIBITED
                ),
            )

        else:

            non_terminal_pair_count += 1

            phase32_match = (
                protection.mutation_allowed
                == phase32.is_valid
            )

            if phase32_match:
                non_terminal_phase32_match_count += 1

            check(
                (
                    "Non-terminal pair mirrors Phase 3.2: "
                    f"{current.value}->{requested.value}"
                ),
                phase32_match,
            )

            if phase32.is_valid:

                check(
                    (
                        "Valid non-terminal pair is not protection failure: "
                        f"{current.value}->{requested.value}"
                    ),
                    (
                        protection.current_state_is_terminal
                        is False
                        and protection.mutation_allowed
                        is True
                        and protection.protection_triggered
                        is False
                        and protection.code
                        is None
                    ),
                )

            else:

                expected_code = (
                    phase32.violations[
                        0
                    ][
                        "code"
                    ]
                    if phase32.violations
                    else VIOLATION_TRANSITION_NOT_DECLARED
                )

                check(
                    (
                        "Invalid non-terminal pair preserves Phase 3.2 code: "
                        f"{current.value}->{requested.value}"
                    ),
                    (
                        protection.current_state_is_terminal
                        is False
                        and protection.mutation_allowed
                        is False
                        and protection.protection_triggered
                        is False
                        and protection.code
                        == expected_code
                    ),
                )


check(
    "Exactly 100 canonical ordered state pairs tested",
    pair_count == 100,
)

check(
    "Exactly 40 terminal-current pairs protected",
    terminal_pair_count == 40,
)

check(
    "Exactly 60 non-terminal-current pairs tested",
    non_terminal_pair_count == 60,
)

check(
    "All 60 non-terminal pairs mirror frozen Phase 3.2",
    non_terminal_phase32_match_count == 60,
)


# ============================================================================
# 7. Terminal short-circuit with malformed requested states
# ============================================================================

malformed_requested = (
    "UNKNOWN",
    "",
    None,
    123,
    [],
    {},
)

terminal_malformed_count = 0

for current in terminal_states:

    for requested in malformed_requested:

        terminal_malformed_count += 1

        result = (
            validate_terminal_state_mutation(
                current,
                requested,
            )
        )

        check(
            (
                "Terminal finality overrides malformed target: "
                f"{current.value}->{requested!r}"
            ),
            (
                result.current_state
                == current
                and result.current_state_is_terminal
                is True
                and result.mutation_allowed
                is False
                and result.protection_triggered
                is True
                and result.code
                == TERMINAL_STATE_MUTATION_PROHIBITED
            ),
        )


check(
    "Exactly 24 malformed-target terminal cases tested",
    terminal_malformed_count == 24,
)


# ============================================================================
# 8. Invalid current-state inputs
# ============================================================================

invalid_current_values = (
    "UNKNOWN",
    "",
    None,
    123,
    [],
    {},
)

for current in invalid_current_values:

    result = (
        validate_terminal_state_mutation(
            current,
            "RUNNING",
        )
    )

    check(
        f"Invalid current state rejected: {current!r}",
        (
            result.current_state is None
            and result.requested_state is None
            and result.current_state_is_terminal
            is False
            and result.mutation_allowed
            is False
            and result.protection_triggered
            is False
            and result.code
            == VIOLATION_CURRENT_STATE_INVALID
        ),
    )


# ============================================================================
# 9. Invalid requested-state inputs for non-terminal current
# ============================================================================

for requested in malformed_requested:

    result = (
        validate_terminal_state_mutation(
            "RUNNING",
            requested,
        )
    )

    check(
        f"Invalid non-terminal target rejected: {requested!r}",
        (
            result.current_state
            == UniversalWorkflowStatus.RUNNING
            and result.requested_state
            is None
            and result.current_state_is_terminal
            is False
            and result.mutation_allowed
            is False
            and result.protection_triggered
            is False
            and result.code
            == VIOLATION_REQUESTED_STATE_INVALID
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
        True,
    ),
    (
        " READY ",
        " paused ",
        UniversalWorkflowStatus.READY,
        UniversalWorkflowStatus.PAUSED,
        True,
    ),
    (
        UniversalWorkflowStatus.PAUSED,
        UniversalWorkflowStatus.READY,
        UniversalWorkflowStatus.PAUSED,
        UniversalWorkflowStatus.READY,
        True,
    ),
)

for (
    current,
    requested,
    expected_current,
    expected_requested,
    expected_allowed,
) in normalization_cases:

    result = (
        validate_terminal_state_mutation(
            current,
            requested,
        )
    )

    check(
        (
            "State normalization exact: "
            f"{current!r}->{requested!r}"
        ),
        (
            result.current_state
            == expected_current
            and result.requested_state
            == expected_requested
            and result.mutation_allowed
            is expected_allowed
        ),
    )


terminal_normalized = (
    validate_terminal_state_mutation(
        " failed ",
        " recovering ",
    )
)

check(
    "Normalized terminal state remains protected",
    (
        terminal_normalized.current_state
        == UniversalWorkflowStatus.FAILED
        and terminal_normalized.requested_state
        == UniversalWorkflowStatus.RECOVERING
        and terminal_normalized.current_state_is_terminal
        is True
        and terminal_normalized.protection_triggered
        is True
        and terminal_normalized.code
        == TERMINAL_STATE_MUTATION_PROHIBITED
    ),
)


# ============================================================================
# 11. Require API
# ============================================================================

allowed = (
    require_terminal_state_mutation_allowed(
        "RUNNING",
        "WAITING",
    )
)

check(
    "Require API returns allowed result",
    (
        isinstance(
            allowed,
            TerminalStateProtectionResult,
        )
        and allowed.mutation_allowed
        is True
    ),
)


terminal_error = None

try:

    require_terminal_state_mutation_allowed(
        "FAILED",
        "RECOVERING",
    )

except TerminalStateMutationProhibitedError as exc:

    terminal_error = exc


check(
    "Require API raises terminal-specific error",
    (
        terminal_error is not None
        and terminal_error.result.code
        == TERMINAL_STATE_MUTATION_PROHIBITED
        and terminal_error.result.protection_triggered
        is True
    ),
)


terminal_bad_target_error = None

try:

    require_terminal_state_mutation_allowed(
        "FAILED",
        "UNKNOWN",
    )

except TerminalStateMutationProhibitedError as exc:

    terminal_bad_target_error = exc


check(
    "Terminal-specific error wins over malformed target",
    (
        terminal_bad_target_error
        is not None
        and terminal_bad_target_error.result.code
        == TERMINAL_STATE_MUTATION_PROHIBITED
    ),
)


ordinary_error = None

try:

    require_terminal_state_mutation_allowed(
        "WAITING",
        "COMPLETED",
    )

except InvalidTerminalStateProtectionRequestError as exc:

    ordinary_error = exc


check(
    "Require API preserves ordinary Phase-3.2 failure",
    (
        ordinary_error is not None
        and ordinary_error.result.code
        == VIOLATION_TRANSITION_NOT_DECLARED
        and ordinary_error.result.protection_triggered
        is False
    ),
)


invalid_target_error = None

try:

    require_terminal_state_mutation_allowed(
        "RUNNING",
        "UNKNOWN",
    )

except InvalidTerminalStateProtectionRequestError as exc:

    invalid_target_error = exc


check(
    "Require API preserves requested-state-invalid failure",
    (
        invalid_target_error
        is not None
        and invalid_target_error.result.code
        == VIOLATION_REQUESTED_STATE_INVALID
        and invalid_target_error.result.protection_triggered
        is False
    ),
)


# ============================================================================
# 12. Error hierarchy
# ============================================================================

check(
    "TerminalStateMutationProhibitedError derives from base protection error",
    issubclass(
        TerminalStateMutationProhibitedError,
        TerminalStateProtectionError,
    ),
)

check(
    "InvalidTerminalStateProtectionRequestError derives from base protection error",
    issubclass(
        InvalidTerminalStateProtectionRequestError,
        TerminalStateProtectionError,
    ),
)


# ============================================================================
# 13. Result immutability
# ============================================================================

sample = (
    validate_terminal_state_mutation(
        "FAILED",
        "RECOVERING",
    )
)

result_immutable = False

try:
    sample.code = None
except Exception:
    result_immutable = True

check(
    "Protection result dataclass is immutable",
    result_immutable,
)


mapping = sample.to_dict()

mapping_immutable = False

try:
    mapping[
        "code"
    ] = None
except Exception:
    mapping_immutable = True

check(
    "Protection result mapping is immutable",
    mapping_immutable,
)

check(
    "Protection result mapping has exactly 10 fields",
    len(mapping) == 10,
)


check(
    "Protection result carries exact Phase 3.2 provenance",
    sample.transition_validation_version
    == TRANSITION_VALIDATION_VERSION,
)

check(
    "Protection result carries exact Phase 3.1 provenance",
    sample.state_machine_version
    == WORKFLOW_STATE_MACHINE_VERSION,
)

check(
    "Protection result carries exact Phase 3.4 provenance",
    sample.protection_version
    == TERMINAL_STATE_PROTECTION_VERSION,
)


# ============================================================================
# 14. Determinism
# ============================================================================

first = (
    validate_terminal_state_mutation(
        "FAILED",
        "RECOVERING",
    )
)

second = (
    validate_terminal_state_mutation(
        "FAILED",
        "RECOVERING",
    )
)

check(
    "Terminal protection result is deterministic",
    first == second,
)


first = (
    validate_terminal_state_mutation(
        "RUNNING",
        "WAITING",
    )
)

second = (
    validate_terminal_state_mutation(
        "RUNNING",
        "WAITING",
    )
)

check(
    "Non-terminal delegation result is deterministic",
    first == second,
)


# ============================================================================
# 15. Snapshot
# ============================================================================

snapshot = (
    terminal_state_protection_snapshot()
)

check(
    "Snapshot protection version exact",
    snapshot[
        "protection_version"
    ]
    == TERMINAL_STATE_PROTECTION_VERSION,
)

check(
    "Snapshot schema exact",
    snapshot[
        "schema_version"
    ]
    == TERMINAL_STATE_PROTECTION_SCHEMA_VERSION,
)

check(
    "Snapshot result-field count exact",
    snapshot[
        "result_field_count"
    ]
    == 10,
)

check(
    "Snapshot references exact Phase 3.2",
    snapshot[
        "transition_validation_version"
    ]
    == TRANSITION_VALIDATION_VERSION,
)

check(
    "Snapshot references exact Phase 3.1",
    snapshot[
        "state_machine_version"
    ]
    == WORKFLOW_STATE_MACHINE_VERSION,
)

check(
    "Snapshot exposes exactly four terminal states",
    snapshot[
        "terminal_state_count"
    ]
    == 4,
)

check(
    "Snapshot terminal-state set exact",
    set(
        snapshot[
            "terminal_states"
        ]
    )
    == {
        "COMPLETED",
        "FAILED",
        "CANCELLED",
        "ABORTED",
    },
)

check(
    "Snapshot protection code exact",
    snapshot[
        "protection_code"
    ]
    == TERMINAL_STATE_MUTATION_PROHIBITED,
)

check(
    "Snapshot declares terminal states protected",
    snapshot[
        "terminal_states_protected"
    ]
    is True,
)


for flag in (
    "workflow_mutation",
    "transition_execution",
    "history_recording",
    "durable_persistence",
    "runtime_execution",
    "recovery_execution",
    "security_audit_trail",
):

    check(
        f"Snapshot declares {flag}=False",
        snapshot[
            flag
        ]
        is False,
    )


snapshot_immutable = False

try:
    snapshot[
        "terminal_state_count"
    ] = 99
except Exception:
    snapshot_immutable = True

check(
    "Snapshot mapping is immutable",
    snapshot_immutable,
)


# ============================================================================
# 16. Architecture declaration
# ============================================================================

explanation = (
    explain_terminal_state_protection_v3_4()
)

check(
    "Architecture identifies Phase 3.4",
    explanation[
        "phase"
    ]
    == "3.4",
)

check(
    "Architecture identifies Terminal-State Protection",
    explanation[
        "component"
    ]
    == "Terminal-State Protection",
)

check(
    "Architecture version exact",
    explanation[
        "version"
    ]
    == TERMINAL_STATE_PROTECTION_VERSION,
)

check(
    "Architecture schema exact",
    explanation[
        "schema_version"
    ]
    == TERMINAL_STATE_PROTECTION_SCHEMA_VERSION,
)

check(
    "Architecture result field count exact",
    explanation[
        "result_field_count"
    ]
    == 10,
)

check(
    "Architecture has exactly four protection rules",
    len(
        explanation[
            "protection_rules"
        ]
    )
    == 4,
)

check(
    "Architecture references exact Phase 3.2",
    explanation[
        "transition_validation_version"
    ]
    == TRANSITION_VALIDATION_VERSION,
)

check(
    "Architecture references exact Phase 3.1",
    explanation[
        "state_machine_version"
    ]
    == WORKFLOW_STATE_MACHINE_VERSION,
)

check(
    "Architecture terminal-state set exact",
    set(
        explanation[
            "terminal_states"
        ]
    )
    == {
        "COMPLETED",
        "FAILED",
        "CANCELLED",
        "ABORTED",
    },
)

check(
    "Architecture protection code exact",
    explanation[
        "protection_code"
    ]
    == TERMINAL_STATE_MUTATION_PROHIBITED,
)


required_owns = (
    "canonical terminal-state immutability policy",
    "terminal lifecycle mutation prohibition",
    "terminal protection inspection",
    "deterministic terminal protection evidence",
    "terminal-state mutation guard",
    "canonical terminal protection code/error",
    "composition with frozen Phase 3.2 for non-terminal requests",
    "terminal protection architecture explanation",
)

for item in required_owns:

    check(
        f"Terminal-State Protection owns: {item}",
        item
        in explanation[
            "owns"
        ],
    )


required_exclusions = (
    "terminal-state vocabulary",
    "lifecycle graph",
    "requested-transition edge legality",
    "workflow object mutation",
    "lifecycle history recording",
    "transition timestamp generation",
    "durable persistence",
    "checkpoints",
    "pause execution",
    "resume execution",
    "recovery execution",
    "recovery policy",
    "Runtime Registration",
    "Runtime jobs",
    "coordinator execution",
    "dependency planning",
    "stage result handoff",
    "security audit trail",
)

for item in required_exclusions:

    check(
        f"Terminal-State Protection excludes: {item}",
        item
        in explanation[
            "does_not_own"
        ],
    )


future = explanation[
    "future_authority"
]

check(
    "3.5 remains Lifecycle Certification authority",
    future[
        "3.5"
    ]
    == "Lifecycle Certification",
)

check(
    "Phase 8 remains persistence authority",
    future[
        "8.0"
    ]
    == "Workflow State Persistence",
)

check(
    "Phase 9 remains recovery authority",
    future[
        "9.0"
    ]
    == "Coordination Recovery",
)

check(
    "10.5 remains Audit Trail authority",
    future[
        "10.5"
    ]
    == "Audit Trail",
)


future_immutable = False

try:
    future[
        "X"
    ] = "changed"
except Exception:
    future_immutable = True

check(
    "Future authority mapping is immutable",
    future_immutable,
)


explanation_immutable = False

try:
    explanation[
        "phase"
    ] = "changed"
except Exception:
    explanation_immutable = True

check(
    "Architecture explanation mapping is immutable",
    explanation_immutable,
)


# ============================================================================
# 17. Static import boundary
# ============================================================================

tree = ast.parse(
    source
)

backend_imports = []

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
        "universal_workflows.contract"
    ),
    (
        "backend.server.coordination."
        "workflow_lifecycle.state_machine"
    ),
    (
        "backend.server.coordination."
        "workflow_lifecycle.transition_validation"
    ),
}


check(
    "3.4 imports only canonical lifecycle dependencies",
    set(
        backend_imports
    ).issubset(
        allowed_backend_imports
    ),
    json.dumps(
        backend_imports
    ),
)


forbidden_import_fragments = (
    "backend.server.runtime",
    "backend.server.workers",
    "backend.server.jobs",
    "backend.server.routes",
    "backend.server.pipelines",
    "backend.server.coordination.workflow_registry",
    "backend.server.coordination.coordinator_registry",
    "backend.server.coordination.registration_validation",
    "backend.server.coordination.version_management",
    "backend.server.coordination.workflow_lifecycle.lifecycle_history",
)

bad_imports = [
    item
    for item
    in backend_imports
    if any(
        fragment
        in item
        for fragment
        in forbidden_import_fragments
    )
]

check(
    "3.4 has no Runtime/registry/history/execution imports",
    not bad_imports,
    json.dumps(
        bad_imports
    ),
)


# ============================================================================
# 18. No second lifecycle authority
# ============================================================================

duplicate_authority_markers = (
    "_WORKFLOW_TRANSITION_GRAPH",
    "_ALLOWED_TRANSITIONS",
    "allowed_transitions = {",
    "transition_graph = {",
    "TERMINAL_WORKFLOW_STATUSES =",
    "class UniversalWorkflowStatus",
    "def validate_workflow_transition(",
)

duplicate_authority = [
    marker
    for marker
    in duplicate_authority_markers
    if marker
    in source
]

check(
    "3.4 defines no duplicate state vocabulary, graph, or Phase-3.2 validator",
    not duplicate_authority,
    json.dumps(
        duplicate_authority
    ),
)

check(
    "3.4 consumes frozen terminal_workflow_states",
    "terminal_workflow_states("
    in source,
)

check(
    "3.4 consumes frozen is_terminal_workflow_state",
    "is_terminal_workflow_state("
    in source,
)

check(
    "3.4 consumes frozen validate_workflow_transition",
    "validate_workflow_transition("
    in source,
)


# ============================================================================
# 19. No mutation / execution / persistence / recovery behavior
# ============================================================================

# Detect executable behavior through AST rather than raw substring matches.
#
# Raw substring detection is inappropriate here because architectural
# declarations intentionally contain terms such as "checkpoints" and
# "recovery policy" inside does_not_own metadata.

forbidden_call_names = {
    "uuid4",
    "create_lifecycle_history_entry",
    "append_lifecycle_history",
    "open",
    "dispatch",
    "execute",
    "enqueue",
    "register_workflow",
    "register_coordinator",
    "run_coordinator",
    "invoke_coordinator",
}

forbidden_call_attributes = {
    "now",
    "utcnow",
    "write_text",
    "write_bytes",
}

forbidden_name_prefixes = (
    "sqlite",
    "redis",
    "boto3",
    "requests",
)

behavior_violations = []

for node in ast.walk(tree):

    if isinstance(node, ast.Call):

        func = node.func

        if isinstance(func, ast.Name):

            if func.id in forbidden_call_names:

                behavior_violations.append(
                    f"call:{func.id}"
                )

        elif isinstance(func, ast.Attribute):

            if func.attr in forbidden_call_attributes:

                behavior_violations.append(
                    f"call-attribute:{func.attr}"
                )

            root = func

            while isinstance(
                root,
                ast.Attribute,
            ):

                root = root.value

            if isinstance(
                root,
                ast.Name,
            ):

                if root.id.startswith(
                    forbidden_name_prefixes
                ):

                    behavior_violations.append(
                        (
                            "forbidden-call-root:"
                            f"{root.id}"
                        )
                    )


check(
    "3.4 performs no hidden mutation/history/persistence/runtime/recovery work",
    not behavior_violations,
    json.dumps(
        behavior_violations
    ),
)


# ============================================================================
# 20. Frozen upstream SHA256 integrity
# ============================================================================

frozen_files = (
    (
        "Phase 3.3 Lifecycle History",
        PHASE_33,
        (
            "D89F1D4FBC54307C7B8155E670CDD3C"
            "6C8771185DC8AFBE382A87BB34EDA8464"
        ),
    ),
    (
        "Phase 3.2 Transition Validation",
        PHASE_32,
        (
            "69A952141E920E63B32B12AF1E9FB79D"
            "6296961FED40BCB94F007123BF9BD746"
        ),
    ),
    (
        "Phase 3.1 Workflow State Machine",
        PHASE_31,
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


for (
    name,
    path,
    expected,
) in frozen_files:

    actual = hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()

    check(
        f"Frozen {name} hash unchanged",
        actual == expected,
        actual,
    )


# ============================================================================
# 21. Canonical Phase 3.4 SHA256
# ============================================================================

sha256 = hashlib.sha256(
    TARGET.read_bytes()
).hexdigest().upper()

print()
print("Canonical Phase 3.4 SHA256:")
print(
    sha256
)


# ============================================================================
# 22. Final result / report
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
    "PHASE 3.4 TERMINAL-STATE PROTECTION CERTIFICATION",
    "=" * 92,
    "",
    (
        "Protection Version: "
        + TERMINAL_STATE_PROTECTION_VERSION
    ),
    (
        "Protection Schema: "
        + TERMINAL_STATE_PROTECTION_SCHEMA_VERSION
    ),
    (
        "Transition Validation Version: "
        + TRANSITION_VALIDATION_VERSION
    ),
    (
        "Workflow State Machine Version: "
        + WORKFLOW_STATE_MACHINE_VERSION
    ),
    "",
    "Protection Result Fields: 10",
    "Canonical Workflow States: 10",
    "Canonical Terminal States: 4",
    "Canonical Non-Terminal States: 6",
    "Canonical State-Pair Matrix Tested: 100",
    "Terminal-Current Matrix Protected: 40",
    "Non-Terminal Matrix Compared Against Phase 3.2: 60",
    "Malformed Terminal Targets Tested: 24",
    "",
    (
        "Protection Code: "
        + TERMINAL_STATE_MUTATION_PROHIBITED
    ),
    "",
    "Workflow Mutation Authority: NONE",
    "Transition Edge Authority: NONE (Phase 3.2)",
    "History Recording Authority: NONE (Phase 3.3)",
    "Durable Persistence Authority: NONE (Phase 8)",
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


for (
    name,
    ok,
    detail,
) in checks:

    report_lines.append(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if detail:

        report_lines.append(
            f"    {detail}"
        )


REPORT.write_text(
    "\n".join(
        report_lines
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 92)
print("PHASE 3.4 CERTIFICATION RESULT")
print("=" * 92)

print(
    "Checks:",
    len(checks),
)

print(
    "Passed:",
    passed,
)

print(
    "Failed:",
    failed,
)

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

print("=" * 92)

raise SystemExit(
    0
    if failed == 0
    else 1
)



