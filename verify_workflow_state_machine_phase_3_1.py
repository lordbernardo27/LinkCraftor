from __future__ import annotations

import ast
import hashlib
import importlib
import json
from pathlib import Path

from backend.server.coordination.workflow_lifecycle.state_machine import (
    WORKFLOW_STATE_MACHINE_VERSION,
    WORKFLOW_STATE_MACHINE_SCHEMA_VERSION,
    coerce_workflow_state,
    workflow_states,
    terminal_workflow_states,
    non_terminal_workflow_states,
    is_terminal_workflow_state,
    is_non_terminal_workflow_state,
    workflow_state_semantics,
    allowed_next_states,
    has_transition_edge,
    transition_edges,
    workflow_state_machine_snapshot,
    explain_workflow_state_machine_v3_1,
)

from backend.server.coordination.universal_workflows.contract import (
    UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
    UniversalWorkflowStatus,
    TERMINAL_WORKFLOW_STATUSES,
)


TARGET = Path(
    "backend/server/coordination/"
    "workflow_lifecycle/state_machine.py"
)

REPORT = Path(
    "workflow_state_machine_phase_3_1_certification.txt"
)

checks = []


def check(
    name,
    condition,
    detail="",
):
    ok = bool(
        condition
    )

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
print("=" * 84)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 3.1 WORKFLOW STATE MACHINE CERTIFICATION")
print("=" * 84)


# ============================================================================
# 1. File / syntax / import
# ============================================================================

check(
    "Canonical Workflow State Machine file exists",
    TARGET.exists(),
    str(
        TARGET
    ),
)

source = TARGET.read_text(
    encoding="utf-8-sig"
)

try:

    ast.parse(
        source
    )

    syntax_ok = True

except SyntaxError as exc:

    syntax_ok = False
    print(
        exc
    )

check(
    "Python syntax parses successfully",
    syntax_ok,
)


try:

    importlib.import_module(
        "backend.server.coordination."
        "workflow_lifecycle.state_machine"
    )

    import_ok = True

except Exception as exc:

    import_ok = False
    print(
        repr(
            exc
        )
    )

check(
    "Workflow State Machine imports successfully",
    import_ok,
)


# ============================================================================
# 2. Component identity
# ============================================================================

check(
    "State Machine version is canonical",
    WORKFLOW_STATE_MACHINE_VERSION
    == "workflow_state_machine_v3.1.0",
)

check(
    "State Machine schema is canonical",
    WORKFLOW_STATE_MACHINE_SCHEMA_VERSION
    == "workflow_state_machine_schema_v1",
)

check(
    "Universal Workflow Contract version is canonical",
    UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    == "universal_workflow_contract_v1.1.0",
)


# ============================================================================
# 3. Canonical state vocabulary
# ============================================================================

states = workflow_states()

expected_states = (
    UniversalWorkflowStatus.CREATED,
    UniversalWorkflowStatus.READY,
    UniversalWorkflowStatus.RUNNING,
    UniversalWorkflowStatus.WAITING,
    UniversalWorkflowStatus.PAUSED,
    UniversalWorkflowStatus.RECOVERING,
    UniversalWorkflowStatus.COMPLETED,
    UniversalWorkflowStatus.FAILED,
    UniversalWorkflowStatus.CANCELLED,
    UniversalWorkflowStatus.ABORTED,
)

check(
    "State Machine contains exactly ten workflow states",
    len(
        states
    )
    == 10,
)

check(
    "State Machine reuses exact frozen workflow-state vocabulary",
    states
    == expected_states,
)

check(
    "State Machine invents no additional workflow states",
    set(
        states
    )
    == set(
        UniversalWorkflowStatus
    ),
)


# ============================================================================
# 4. Terminal / non-terminal classification
# ============================================================================

terminal = terminal_workflow_states()

non_terminal = (
    non_terminal_workflow_states()
)

check(
    "Exactly four workflow states are terminal",
    len(
        terminal
    )
    == 4,
)

check(
    "Terminal states exactly match frozen contract",
    set(
        terminal
    )
    == set(
        TERMINAL_WORKFLOW_STATUSES
    ),
)

check(
    "Terminal state ordering is canonical",
    terminal
    == (
        UniversalWorkflowStatus.COMPLETED,
        UniversalWorkflowStatus.FAILED,
        UniversalWorkflowStatus.CANCELLED,
        UniversalWorkflowStatus.ABORTED,
    ),
)

check(
    "Exactly six workflow states are non-terminal",
    len(
        non_terminal
    )
    == 6,
)

check(
    "Non-terminal states are canonical",
    non_terminal
    == (
        UniversalWorkflowStatus.CREATED,
        UniversalWorkflowStatus.READY,
        UniversalWorkflowStatus.RUNNING,
        UniversalWorkflowStatus.WAITING,
        UniversalWorkflowStatus.PAUSED,
        UniversalWorkflowStatus.RECOVERING,
    ),
)


for state in terminal:

    check(
        f"{state.value} classifies as terminal",
        is_terminal_workflow_state(
            state
        )
        is True,
    )


for state in non_terminal:

    check(
        f"{state.value} classifies as non-terminal",
        is_non_terminal_workflow_state(
            state
        )
        is True,
    )


# ============================================================================
# 5. Coercion behavior
# ============================================================================

for state in states:

    check(
        f"String coercion resolves {state.value}",
        coerce_workflow_state(
            state.value.lower()
        )
        == state,
    )

    check(
        f"Enum coercion preserves {state.value}",
        coerce_workflow_state(
            state
        )
        == state,
    )


# ============================================================================
# 6. Exact canonical graph
# ============================================================================

expected_graph = {
    UniversalWorkflowStatus.CREATED: (
        UniversalWorkflowStatus.READY,
        UniversalWorkflowStatus.CANCELLED,
        UniversalWorkflowStatus.ABORTED,
    ),

    UniversalWorkflowStatus.READY: (
        UniversalWorkflowStatus.RUNNING,
        UniversalWorkflowStatus.PAUSED,
        UniversalWorkflowStatus.CANCELLED,
        UniversalWorkflowStatus.ABORTED,
    ),

    UniversalWorkflowStatus.RUNNING: (
        UniversalWorkflowStatus.WAITING,
        UniversalWorkflowStatus.PAUSED,
        UniversalWorkflowStatus.RECOVERING,
        UniversalWorkflowStatus.COMPLETED,
        UniversalWorkflowStatus.FAILED,
        UniversalWorkflowStatus.CANCELLED,
        UniversalWorkflowStatus.ABORTED,
    ),

    UniversalWorkflowStatus.WAITING: (
        UniversalWorkflowStatus.RUNNING,
        UniversalWorkflowStatus.PAUSED,
        UniversalWorkflowStatus.RECOVERING,
        UniversalWorkflowStatus.FAILED,
        UniversalWorkflowStatus.CANCELLED,
        UniversalWorkflowStatus.ABORTED,
    ),

    UniversalWorkflowStatus.PAUSED: (
        UniversalWorkflowStatus.READY,
        UniversalWorkflowStatus.RUNNING,
        UniversalWorkflowStatus.RECOVERING,
        UniversalWorkflowStatus.FAILED,
        UniversalWorkflowStatus.CANCELLED,
        UniversalWorkflowStatus.ABORTED,
    ),

    UniversalWorkflowStatus.RECOVERING: (
        UniversalWorkflowStatus.READY,
        UniversalWorkflowStatus.RUNNING,
        UniversalWorkflowStatus.WAITING,
        UniversalWorkflowStatus.FAILED,
        UniversalWorkflowStatus.CANCELLED,
        UniversalWorkflowStatus.ABORTED,
    ),

    UniversalWorkflowStatus.COMPLETED: (),
    UniversalWorkflowStatus.FAILED: (),
    UniversalWorkflowStatus.CANCELLED: (),
    UniversalWorkflowStatus.ABORTED: (),
}


for state in states:

    check(
        f"{state.value} allowed-next-state model is exact",
        allowed_next_states(
            state
        )
        == expected_graph[
            state
        ],
    )


# ============================================================================
# 7. Transition edges
# ============================================================================

edges = transition_edges()

check(
    "Canonical transition edge count is 32",
    len(
        edges
    )
    == 32,
)

expected_edges = tuple(
    (
        from_state,
        to_state,
    )
    for from_state
    in expected_states
    for to_state
    in expected_graph[
        from_state
    ]
)

check(
    "Transition edge sequence is deterministic and exact",
    edges
    == expected_edges,
)


for (
    from_state,
    to_state,
) in expected_edges:

    check(
        (
            f"Declared edge exists: "
            f"{from_state.value}->{to_state.value}"
        ),
        has_transition_edge(
            from_state,
            to_state,
        )
        is True,
    )


# ============================================================================
# 8. Critical forbidden edges
# ============================================================================

forbidden_edges = (
    (
        UniversalWorkflowStatus.WAITING,
        UniversalWorkflowStatus.READY,
    ),
    (
        UniversalWorkflowStatus.WAITING,
        UniversalWorkflowStatus.COMPLETED,
    ),
    (
        UniversalWorkflowStatus.RECOVERING,
        UniversalWorkflowStatus.COMPLETED,
    ),
    (
        UniversalWorkflowStatus.FAILED,
        UniversalWorkflowStatus.RECOVERING,
    ),
    (
        UniversalWorkflowStatus.COMPLETED,
        UniversalWorkflowStatus.RUNNING,
    ),
    (
        UniversalWorkflowStatus.CANCELLED,
        UniversalWorkflowStatus.RUNNING,
    ),
    (
        UniversalWorkflowStatus.ABORTED,
        UniversalWorkflowStatus.READY,
    ),
)

for (
    from_state,
    to_state,
) in forbidden_edges:

    check(
        (
            f"Forbidden edge absent: "
            f"{from_state.value}->{to_state.value}"
        ),
        has_transition_edge(
            from_state,
            to_state,
        )
        is False,
    )


# ============================================================================
# 9. Terminal states expose zero outgoing edges
# ============================================================================

for state in terminal:

    check(
        f"{state.value} exposes zero outgoing lifecycle edges",
        allowed_next_states(
            state
        )
        == (),
    )


# ============================================================================
# 10. State semantics
# ============================================================================

for state in states:

    semantics = (
        workflow_state_semantics(
            state
        )
    )

    check(
        f"{state.value} has non-empty lifecycle semantics",
        isinstance(
            semantics,
            str,
        )
        and bool(
            semantics.strip()
        ),
    )


check(
    "WAITING semantics differ from PAUSED semantics",
    workflow_state_semantics(
        UniversalWorkflowStatus.WAITING
    )
    != workflow_state_semantics(
        UniversalWorkflowStatus.PAUSED
    ),
)

check(
    "RECOVERING semantics identify non-terminal recovery handling",
    "non-terminal"
    in workflow_state_semantics(
        UniversalWorkflowStatus.RECOVERING
    ).lower(),
)

check(
    "FAILED semantics identify terminal failure",
    "terminal"
    in workflow_state_semantics(
        UniversalWorkflowStatus.FAILED
    ).lower(),
)


# ============================================================================
# 11. Snapshot
# ============================================================================

snapshot = (
    workflow_state_machine_snapshot()
)

check(
    "Snapshot exposes canonical state-machine version",
    snapshot[
        "state_machine_version"
    ]
    == WORKFLOW_STATE_MACHINE_VERSION,
)

check(
    "Snapshot exposes canonical schema",
    snapshot[
        "schema_version"
    ]
    == WORKFLOW_STATE_MACHINE_SCHEMA_VERSION,
)

check(
    "Snapshot exposes frozen workflow contract version",
    snapshot[
        "workflow_contract_version"
    ]
    == UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
)

check(
    "Snapshot state count is 10",
    snapshot[
        "state_count"
    ]
    == 10,
)

check(
    "Snapshot terminal-state count is 4",
    snapshot[
        "terminal_state_count"
    ]
    == 4,
)

check(
    "Snapshot non-terminal-state count is 6",
    snapshot[
        "non_terminal_state_count"
    ]
    == 6,
)

check(
    "Snapshot transition-edge count is 32",
    snapshot[
        "transition_edge_count"
    ]
    == 32,
)

check(
    "Snapshot state vocabulary is exact",
    snapshot[
        "states"
    ]
    == tuple(
        state.value
        for state
        in expected_states
    ),
)

check(
    "Snapshot terminal-state vocabulary is exact",
    snapshot[
        "terminal_states"
    ]
    == (
        "COMPLETED",
        "FAILED",
        "CANCELLED",
        "ABORTED",
    ),
)

check(
    "Snapshot non-terminal-state vocabulary is exact",
    snapshot[
        "non_terminal_states"
    ]
    == (
        "CREATED",
        "READY",
        "RUNNING",
        "WAITING",
        "PAUSED",
        "RECOVERING",
    ),
)


# ============================================================================
# 12. Snapshot boundary flags
# ============================================================================

boundary_flags = (
    "transition_validation",
    "workflow_mutation",
    "history_recording",
    "terminal_protection_enforcement",
    "persistence",
    "runtime_execution",
    "recovery_execution",
)

for field in boundary_flags:

    check(
        f"Snapshot declares {field}=False",
        snapshot[
            field
        ]
        is False,
    )


# ============================================================================
# 13. Snapshot immutability
# ============================================================================

immutable = False

try:

    snapshot[
        "state_count"
    ] = 999

except Exception:

    immutable = True

check(
    "Workflow State Machine snapshot is immutable",
    immutable,
)


# ============================================================================
# 14. Architecture declaration
# ============================================================================

explanation = (
    explain_workflow_state_machine_v3_1()
)

check(
    "Architecture declaration identifies Phase 3.1",
    explanation[
        "phase"
    ]
    == "3.1",
)

check(
    "Architecture declaration identifies Workflow State Machine",
    explanation[
        "component"
    ]
    == "Workflow State Machine",
)

check(
    "Model authority is canonical_lifecycle_graph",
    explanation[
        "model_authority"
    ]
    == "canonical_lifecycle_graph",
)

check(
    "Status authority remains UniversalWorkflowStatus",
    "UniversalWorkflowStatus"
    in explanation[
        "status_authority"
    ],
)


required_owns = (
    "canonical workflow lifecycle state reference",
    "canonical terminal-state classification",
    "canonical non-terminal-state classification",
    "canonical lifecycle transition graph",
    "immutable transition-model declaration",
    "deterministic state inspection",
    "deterministic transition inspection",
    "state classification helpers",
    "state semantics",
    "allowed-next-state model inspection",
)

for item in required_owns:

    check(
        f"Workflow State Machine owns: {item}",
        item
        in explanation[
            "owns"
        ],
    )


required_exclusions = (
    "runtime transition request validation",
    "transition rejection policy",
    "workflow status mutation",
    "lifecycle history recording",
    "transition timestamps",
    "terminal-state protection enforcement",
    "workflow persistence",
    "checkpoints",
    "pause execution behavior",
    "resume execution behavior",
    "recovery execution",
    "failure recovery policy",
    "coordinator invocation",
    "workflow execution",
    "Runtime Registration",
    "Runtime jobs",
    "stage dependency planning",
    "stage result handoff",
)

for item in required_exclusions:

    check(
        f"Workflow State Machine excludes: {item}",
        item
        in explanation[
            "does_not_own"
        ],
    )


# ============================================================================
# 15. Future authority boundaries
# ============================================================================

expected_future_authority = {
    "3.2": "Transition Validation",
    "3.3": "Lifecycle History",
    "3.4": "Terminal-State Protection",
    "8.0": "Workflow State Persistence",
    "9.0": "Coordination Recovery",
}

for (
    phase,
    authority,
) in expected_future_authority.items():

    check(
        f"{phase} remains authority for {authority}",
        explanation[
            "future_authority"
        ][
            phase
        ]
        == authority,
    )


# ============================================================================
# 16. Static import boundary
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
}

check(
    "State Machine imports only frozen workflow contract",
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
    "backend.server.pipelines",
    "backend.server.routes",
    "backend.server.coordination.workflow_registry",
    "backend.server.coordination.coordinator_registry",
    "backend.server.coordination.registration_validation",
    "backend.server.coordination.version_management",
)

violating_imports = [
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
    "State Machine has no runtime/registry/execution imports",
    not violating_imports,
    json.dumps(
        violating_imports
    ),
)


# ============================================================================
# 17. Static mutation / execution boundary
# ============================================================================

forbidden_markers = (
    "create_universal",
    "dispatch(",
    "execute(",
    "run_coordinator(",
    "invoke_coordinator(",
    "register_workflow",
    "register_coordinator",
    "set_preferred_",
    "validate_transition(",
    "transition_history",
    "write_text(",
    "write_bytes(",
    "open(",
    "sqlite",
    "boto3",
    "requests.",
)

violations = [
    marker
    for marker
    in forbidden_markers
    if marker
    in source
]

check(
    "State Machine performs no execution/registration/persistence",
    not violations,
    json.dumps(
        violations
    ),
)


# ============================================================================
# 18. Frozen Phase 2 hash integrity
# ============================================================================

frozen_files = (
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
        actual
        == expected,
        actual,
    )


# ============================================================================
# 19. Canonical SHA256
# ============================================================================

sha256 = hashlib.sha256(
    TARGET.read_bytes()
).hexdigest().upper()

print()
print("Canonical SHA256:")
print(
    sha256
)


# ============================================================================
# 20. Final result
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


lines = [
    "LINKCRAFTOR",
    "UNIVERSAL COORDINATION FRAMEWORK",
    "PHASE 3.1 WORKFLOW STATE MACHINE CERTIFICATION",
    "=" * 84,
    "",
    (
        "State Machine Version: "
        + WORKFLOW_STATE_MACHINE_VERSION
    ),
    (
        "State Machine Schema: "
        + WORKFLOW_STATE_MACHINE_SCHEMA_VERSION
    ),
    (
        "Workflow Contract Version: "
        + UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
    "",
    "Canonical State Count: 10",
    "Terminal State Count: 4",
    "Non-Terminal State Count: 6",
    "Canonical Transition Edge Count: 32",
    "",
    (
        "Terminal States: "
        "COMPLETED, FAILED, CANCELLED, ABORTED"
    ),
    "",
    "Model Authority: canonical_lifecycle_graph",
    "Transition Validation Authority: NONE (Phase 3.2)",
    "History Authority: NONE (Phase 3.3)",
    "Terminal Protection Enforcement: NONE (Phase 3.4)",
    "Persistence Authority: NONE (Phase 8)",
    "Recovery Execution Authority: NONE (Phase 9)",
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

    lines.append(
        f"[{'PASS' if ok else 'FAIL'}] {name}"
    )

    if detail:

        lines.append(
            f"    {detail}"
        )


REPORT.write_text(
    "\n".join(
        lines
    )
    + "\n",
    encoding="utf-8",
)


print()
print("=" * 84)
print("CERTIFICATION RESULT")
print("=" * 84)

print(
    f"Checks: {len(checks)}"
)

print(
    f"Passed: {passed}"
)

print(
    f"Failed: {failed}"
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

print("=" * 84)

raise SystemExit(
    0
    if failed == 0
    else 1
)
