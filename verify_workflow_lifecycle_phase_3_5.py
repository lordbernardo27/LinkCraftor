from __future__ import annotations

import ast
import hashlib
import importlib
from dataclasses import fields
from pathlib import Path

from backend.server.coordination.workflow_lifecycle.lifecycle_certification import (
    LIFECYCLE_CERTIFICATION_VERSION,
    LIFECYCLE_CERTIFICATION_SCHEMA_VERSION,
    LIFECYCLE_CERTIFICATION_RESULT_FIELD_COUNT,
    WORKFLOW_STATE_MACHINE_SHA256,
    TRANSITION_VALIDATION_SHA256,
    LIFECYCLE_HISTORY_SHA256,
    TERMINAL_STATE_PROTECTION_SHA256,
    PHASE_3_COMPOSITE_FINGERPRINT,
    LifecycleCertificationResult,
    certify_workflow_lifecycle,
    workflow_lifecycle_certification_snapshot,
    explain_lifecycle_certification_v3_5,
)

from backend.server.coordination.workflow_lifecycle.state_machine import (
    WORKFLOW_STATE_MACHINE_VERSION,
    workflow_states,
    terminal_workflow_states,
    non_terminal_workflow_states,
    transition_edges,
)

from backend.server.coordination.workflow_lifecycle.transition_validation import (
    TRANSITION_VALIDATION_VERSION,
    VIOLATION_TRANSITION_NOT_DECLARED,
    validate_workflow_transition,
)

from backend.server.coordination.workflow_lifecycle.lifecycle_history import (
    LIFECYCLE_HISTORY_VERSION,
    InvalidLifecycleHistoryEntryError,
    create_lifecycle_history_entry,
)

from backend.server.coordination.workflow_lifecycle.terminal_state_protection import (
    TERMINAL_STATE_PROTECTION_VERSION,
    TERMINAL_STATE_MUTATION_PROHIBITED,
    validate_terminal_state_mutation,
)


ROOT = Path.cwd()

PHASE_31 = ROOT / (
    "backend/server/coordination/"
    "workflow_lifecycle/state_machine.py"
)

PHASE_32 = ROOT / (
    "backend/server/coordination/"
    "workflow_lifecycle/transition_validation.py"
)

PHASE_33 = ROOT / (
    "backend/server/coordination/"
    "workflow_lifecycle/lifecycle_history.py"
)

PHASE_34 = ROOT / (
    "backend/server/coordination/"
    "workflow_lifecycle/terminal_state_protection.py"
)

PHASE_35 = ROOT / (
    "backend/server/coordination/"
    "workflow_lifecycle/lifecycle_certification.py"
)

REPORT = ROOT / (
    "workflow_lifecycle_phase_3_5_certification.txt"
)


EXPECTED_HASHES = {
    "3.1": (
        "144327A4E9C8989FCF0F4DBD10BCF6D"
        "7203F503930D81CB8E24644D86D2BB662"
    ),
    "3.2": (
        "69A952141E920E63B32B12AF1E9FB79D"
        "6296961FED40BCB94F007123BF9BD746"
    ),
    "3.3": (
        "739CD8D959F4176071FE7698D3098A1D"
        "C5DE23FF056D118F3DF32FEEDB79E5ED"
    ),
    "3.4": (
        "7632A838D9CEAD7ED95DB0099D08FB20"
        "D01B4E2BD25BFF48D68CBEB89065A7B7"
    ),
}

EXPECTED_COMPOSITE = (
    "7EBEB4357A555A93BDE885922E561A7B"
    "87AD1751CACDED5C10641C61A0BB778D"
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


def sha256_file(
    path: Path,
) -> str:

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest().upper()


print()
print("=" * 96)
print("LINKCRAFTOR")
print("UNIVERSAL COORDINATION FRAMEWORK")
print("PHASE 3.5 - WORKFLOW LIFECYCLE FINAL CERTIFICATION")
print("=" * 96)


# ============================================================================
# 1. Canonical files exist
# ============================================================================

for phase, path in (
    ("3.1", PHASE_31),
    ("3.2", PHASE_32),
    ("3.3", PHASE_33),
    ("3.4", PHASE_34),
    ("3.5", PHASE_35),
):

    check(
        f"Phase {phase} canonical file exists",
        path.exists(),
        str(path.relative_to(ROOT)),
    )


# ============================================================================
# 2. Phase 3.5 syntax / import
# ============================================================================

source = PHASE_35.read_text(
    encoding="utf-8-sig"
)

try:

    tree = ast.parse(
        source
    )

    syntax_ok = True

except SyntaxError as exc:

    syntax_ok = False
    tree = None

    print(
        repr(exc)
    )


check(
    "Phase 3.5 Python syntax parses",
    syntax_ok,
)


try:

    importlib.import_module(
        "backend.server.coordination."
        "workflow_lifecycle.lifecycle_certification"
    )

    import_ok = True

except Exception as exc:

    import_ok = False

    print(
        repr(exc)
    )


check(
    "Phase 3.5 module imports successfully",
    import_ok,
)


# ============================================================================
# 3. Canonical identities
# ============================================================================

check(
    "3.1 version exact",
    WORKFLOW_STATE_MACHINE_VERSION
    == "workflow_state_machine_v3.1.0",
)

check(
    "3.2 version exact",
    TRANSITION_VALIDATION_VERSION
    == "transition_validation_v3.2.0",
)

check(
    "3.3 version exact",
    LIFECYCLE_HISTORY_VERSION
    == "lifecycle_history_v3.3.0",
)

check(
    "3.4 version exact",
    TERMINAL_STATE_PROTECTION_VERSION
    == "terminal_state_protection_v3.4.0",
)

check(
    "3.5 version exact",
    LIFECYCLE_CERTIFICATION_VERSION
    == "lifecycle_certification_v3.5.0",
)

check(
    "3.5 schema exact",
    LIFECYCLE_CERTIFICATION_SCHEMA_VERSION
    == "lifecycle_certification_schema_v1",
)

check(
    "3.5 result field count constant is 16",
    LIFECYCLE_CERTIFICATION_RESULT_FIELD_COUNT
    == 16,
)


# ============================================================================
# 4. Exact result contract
# ============================================================================

expected_fields = (
    "is_certified",
    "checks_run",
    "checks_passed",
    "checks_failed",
    "state_count",
    "terminal_state_count",
    "non_terminal_state_count",
    "transition_edge_count",
    "state_pair_count",
    "terminal_pair_count",
    "non_terminal_pair_count",
    "history_edge_count",
    "violations",
    "component_versions",
    "component_hashes",
    "certification_version",
)

actual_fields = tuple(
    field.name
    for field
    in fields(
        LifecycleCertificationResult
    )
)

check(
    "LifecycleCertificationResult has exactly 16 fields",
    len(actual_fields) == 16,
)

check(
    "LifecycleCertificationResult field order exact",
    actual_fields == expected_fields,
)


# ============================================================================
# 5. Frozen component disk hashes
# ============================================================================

actual_hashes = {
    "3.1": sha256_file(
        PHASE_31
    ),
    "3.2": sha256_file(
        PHASE_32
    ),
    "3.3": sha256_file(
        PHASE_33
    ),
    "3.4": sha256_file(
        PHASE_34
    ),
}

for phase in (
    "3.1",
    "3.2",
    "3.3",
    "3.4",
):

    check(
        f"Frozen Phase {phase} SHA256 unchanged",
        actual_hashes[
            phase
        ]
        == EXPECTED_HASHES[
            phase
        ],
        actual_hashes[
            phase
        ],
    )


# ============================================================================
# 6. 3.5 embedded hash evidence matches disk
# ============================================================================

embedded_hashes = {
    "3.1":
        WORKFLOW_STATE_MACHINE_SHA256,

    "3.2":
        TRANSITION_VALIDATION_SHA256,

    "3.3":
        LIFECYCLE_HISTORY_SHA256,

    "3.4":
        TERMINAL_STATE_PROTECTION_SHA256,
}

for phase in (
    "3.1",
    "3.2",
    "3.3",
    "3.4",
):

    check(
        f"3.5 embedded Phase {phase} SHA equals actual frozen file",
        embedded_hashes[
            phase
        ]
        == actual_hashes[
            phase
        ],
    )


# ============================================================================
# 7. Independently recompute composite fingerprint
# ============================================================================

composite_payload = (
    actual_hashes[
        "3.1"
    ]
    + actual_hashes[
        "3.2"
    ]
    + actual_hashes[
        "3.3"
    ]
    + actual_hashes[
        "3.4"
    ]
)

independent_composite = hashlib.sha256(
    composite_payload.encode(
        "utf-8"
    )
).hexdigest().upper()


check(
    "Independent Phase-3 composite fingerprint exact",
    independent_composite
    == EXPECTED_COMPOSITE,
    independent_composite,
)

check(
    "3.5 exported composite fingerprint matches independent computation",
    PHASE_3_COMPOSITE_FINGERPRINT
    == independent_composite,
)


# ============================================================================
# 8. Built-in certification
# ============================================================================

result = (
    certify_workflow_lifecycle()
)

check(
    "Certification returns LifecycleCertificationResult",
    isinstance(
        result,
        LifecycleCertificationResult,
    ),
)

check(
    "Built-in Phase 3 certification reports certified",
    result.is_certified
    is True,
)

check(
    "Built-in certification reports zero failures",
    result.checks_failed
    == 0,
)

check(
    "Built-in certification passed every check",
    result.checks_run
    == result.checks_passed,
)

check(
    "Built-in certification has no violations",
    result.violations
    == (),
)

check(
    "Built-in certification check count is 330",
    result.checks_run
    == 330,
)


# ============================================================================
# 9. State-model invariants
# ============================================================================

states = (
    workflow_states()
)

terminals = (
    terminal_workflow_states()
)

non_terminals = (
    non_terminal_workflow_states()
)

edges = (
    transition_edges()
)


check(
    "Workflow state count is 10",
    len(
        states
    )
    == 10,
)

check(
    "Terminal state count is 4",
    len(
        terminals
    )
    == 4,
)

check(
    "Non-terminal state count is 6",
    len(
        non_terminals
    )
    == 6,
)

check(
    "Transition edge count is 32",
    len(
        edges
    )
    == 32,
)

check(
    "Terminal state set exact",
    {
        item.value
        for item
        in terminals
    }
    == {
        "COMPLETED",
        "FAILED",
        "CANCELLED",
        "ABORTED",
    },
)

check(
    "Non-terminal state set exact",
    {
        item.value
        for item
        in non_terminals
    }
    == {
        "CREATED",
        "READY",
        "RUNNING",
        "WAITING",
        "PAUSED",
        "RECOVERING",
    },
)


# ============================================================================
# 10. Full 100-pair 3.1 / 3.2 matrix
# ============================================================================

declared_edges = set(
    edges
)

pair_count = 0
transition_agreement_count = 0
declared_valid_count = 0
undeclared_invalid_count = 0

for current in states:

    for requested in states:

        pair_count += 1

        declared = (
            (
                current,
                requested,
            )
            in declared_edges
        )

        validation = (
            validate_workflow_transition(
                current,
                requested,
            )
        )

        if (
            validation.is_valid
            == declared
        ):

            transition_agreement_count += 1

        if (
            declared
            and validation.is_valid
        ):

            declared_valid_count += 1

        if (
            not declared
            and not validation.is_valid
        ):

            undeclared_invalid_count += 1


check(
    "Exactly 100 canonical state pairs evaluated",
    pair_count
    == 100,
)

check(
    "All 100 Phase 3.1/3.2 pairs agree",
    transition_agreement_count
    == 100,
)

check(
    "All 32 declared edges valid under Phase 3.2",
    declared_valid_count
    == 32,
)

check(
    "All 68 undeclared pairs invalid under Phase 3.2",
    undeclared_invalid_count
    == 68,
)


# ============================================================================
# 11. Full 3.4 compatibility matrix
# ============================================================================

terminal_set = set(
    terminals
)

terminal_pair_count = 0
terminal_protected_count = 0

non_terminal_pair_count = 0
non_terminal_delegation_count = 0

for current in states:

    for requested in states:

        protection = (
            validate_terminal_state_mutation(
                current,
                requested,
            )
        )

        validation = (
            validate_workflow_transition(
                current,
                requested,
            )
        )

        if current in terminal_set:

            terminal_pair_count += 1

            if (
                protection.current_state_is_terminal
                is True
                and protection.mutation_allowed
                is False
                and protection.protection_triggered
                is True
                and protection.code
                == TERMINAL_STATE_MUTATION_PROHIBITED
            ):

                terminal_protected_count += 1

        else:

            non_terminal_pair_count += 1

            if (
                protection.current_state_is_terminal
                is False
                and protection.protection_triggered
                is False
                and protection.mutation_allowed
                == validation.is_valid
            ):

                non_terminal_delegation_count += 1


check(
    "Terminal-current matrix contains 40 pairs",
    terminal_pair_count
    == 40,
)

check(
    "All 40 terminal-current pairs protected",
    terminal_protected_count
    == 40,
)

check(
    "Non-terminal matrix contains 60 pairs",
    non_terminal_pair_count
    == 60,
)

check(
    "All 60 non-terminal pairs delegate to Phase 3.2",
    non_terminal_delegation_count
    == 60,
)


# ============================================================================
# 12. Every legal edge recordable by 3.3
# ============================================================================

history_legal_count = 0

for index, (
    current,
    requested,
) in enumerate(
    edges,
    start=1,
):

    try:

        entry = (
            create_lifecycle_history_entry(
                event_id=(
                    f"final-cert-edge-{index:03d}"
                ),
                workflow_id=(
                    "phase-3-final-certification"
                ),
                correlation_id=(
                    "phase-3-final-certification"
                ),
                from_state=current,
                to_state=requested,
                occurred_at=(
                    "2026-08-17T00:00:00+00:00"
                ),
            )
        )

        if (
            entry.from_state
            == current
            and entry.to_state
            == requested
        ):

            history_legal_count += 1

    except Exception:

        pass


check(
    "All 32 legal edges recordable by Lifecycle History",
    history_legal_count
    == 32,
)


# ============================================================================
# 13. Every undeclared transition rejected by 3.3
# ============================================================================

invalid_history_cases = 0
invalid_history_rejected = 0

for current in states:

    for requested in states:

        if (
            (
                current,
                requested,
            )
            in declared_edges
        ):

            continue

        invalid_history_cases += 1

        try:

            create_lifecycle_history_entry(
                event_id=(
                    "final-cert-invalid-"
                    f"{current.value}-"
                    f"{requested.value}"
                ),
                workflow_id=(
                    "phase-3-final-certification"
                ),
                correlation_id=(
                    "phase-3-final-certification"
                ),
                from_state=current,
                to_state=requested,
                occurred_at=(
                    "2026-08-17T00:00:00+00:00"
                ),
            )

        except InvalidLifecycleHistoryEntryError:

            invalid_history_rejected += 1


check(
    "Exactly 68 undeclared history cases tested",
    invalid_history_cases
    == 68,
)

check(
    "All 68 undeclared history cases rejected",
    invalid_history_rejected
    == 68,
)


# ============================================================================
# 14. Self-transition invariant
# ============================================================================

self_rejected = 0

for state in states:

    validation = (
        validate_workflow_transition(
            state,
            state,
        )
    )

    if not validation.is_valid:

        self_rejected += 1


check(
    "All 10 self-transitions rejected",
    self_rejected
    == 10,
)


# ============================================================================
# 15. Recovery boundary
# ============================================================================

running_recovering = (
    validate_terminal_state_mutation(
        "RUNNING",
        "RECOVERING",
    )
)

check(
    "RUNNING->RECOVERING remains valid non-terminal progression",
    (
        running_recovering.mutation_allowed
        is True
        and running_recovering.protection_triggered
        is False
    ),
)


failed_recovering = (
    validate_terminal_state_mutation(
        "FAILED",
        "RECOVERING",
    )
)

check(
    "FAILED->RECOVERING remains terminal-final",
    (
        failed_recovering.mutation_allowed
        is False
        and failed_recovering.protection_triggered
        is True
        and failed_recovering.code
        == TERMINAL_STATE_MUTATION_PROHIBITED
    ),
)


# ============================================================================
# 16. Authority distinction
# ============================================================================

waiting_completed = (
    validate_terminal_state_mutation(
        "WAITING",
        "COMPLETED",
    )
)

check(
    "WAITING->COMPLETED is Phase-3.2 transition failure",
    (
        waiting_completed.mutation_allowed
        is False
        and waiting_completed.protection_triggered
        is False
        and waiting_completed.code
        == VIOLATION_TRANSITION_NOT_DECLARED
    ),
)


check(
    "FAILED->RECOVERING is Phase-3.4 terminal-protection failure",
    (
        failed_recovering.mutation_allowed
        is False
        and failed_recovering.protection_triggered
        is True
        and failed_recovering.code
        == TERMINAL_STATE_MUTATION_PROHIBITED
    ),
)


# ============================================================================
# 17. Result evidence and immutability
# ============================================================================

check(
    "Result state count exact",
    result.state_count
    == 10,
)

check(
    "Result terminal-state count exact",
    result.terminal_state_count
    == 4,
)

check(
    "Result non-terminal-state count exact",
    result.non_terminal_state_count
    == 6,
)

check(
    "Result transition-edge count exact",
    result.transition_edge_count
    == 32,
)

check(
    "Result state-pair count exact",
    result.state_pair_count
    == 100,
)

check(
    "Result terminal-pair count exact",
    result.terminal_pair_count
    == 40,
)

check(
    "Result non-terminal-pair count exact",
    result.non_terminal_pair_count
    == 60,
)

check(
    "Result history-edge count exact",
    result.history_edge_count
    == 32,
)


result_immutable = False

try:

    result.is_certified = False

except Exception:

    result_immutable = True


check(
    "LifecycleCertificationResult is immutable",
    result_immutable,
)


versions_immutable = False

try:

    result.component_versions[
        "3.1"
    ] = "changed"

except Exception:

    versions_immutable = True


check(
    "component_versions mapping immutable",
    versions_immutable,
)


hashes_immutable = False

try:

    result.component_hashes[
        "3.1"
    ] = "changed"

except Exception:

    hashes_immutable = True


check(
    "component_hashes mapping immutable",
    hashes_immutable,
)


result_dict = (
    result.to_dict()
)

result_dict_immutable = False

try:

    result_dict[
        "is_certified"
    ] = False

except Exception:

    result_dict_immutable = True


check(
    "Result to_dict mapping immutable",
    result_dict_immutable,
)

check(
    "Result to_dict exposes exactly 16 fields",
    len(
        result_dict
    )
    == 16,
)


# ============================================================================
# 18. Result component evidence
# ============================================================================

for phase, version in (
    (
        "3.1",
        WORKFLOW_STATE_MACHINE_VERSION,
    ),
    (
        "3.2",
        TRANSITION_VALIDATION_VERSION,
    ),
    (
        "3.3",
        LIFECYCLE_HISTORY_VERSION,
    ),
    (
        "3.4",
        TERMINAL_STATE_PROTECTION_VERSION,
    ),
    (
        "3.5",
        LIFECYCLE_CERTIFICATION_VERSION,
    ),
):

    check(
        f"Result component version {phase} exact",
        result.component_versions[
            phase
        ]
        == version,
    )


for phase in (
    "3.1",
    "3.2",
    "3.3",
    "3.4",
):

    check(
        f"Result component hash {phase} equals disk",
        result.component_hashes[
            phase
        ]
        == actual_hashes[
            phase
        ],
    )


check(
    "Result composite fingerprint equals independent computation",
    result.component_hashes[
        "phase_3_composite"
    ]
    == independent_composite,
)


# ============================================================================
# 19. Determinism
# ============================================================================

second_result = (
    certify_workflow_lifecycle()
)

check(
    "Repeated composite certification is deterministic",
    second_result
    == result,
)


# ============================================================================
# 20. Snapshot
# ============================================================================

snapshot = (
    workflow_lifecycle_certification_snapshot()
)

check(
    "Snapshot certification version exact",
    snapshot[
        "certification_version"
    ]
    == LIFECYCLE_CERTIFICATION_VERSION,
)

check(
    "Snapshot schema exact",
    snapshot[
        "schema_version"
    ]
    == LIFECYCLE_CERTIFICATION_SCHEMA_VERSION,
)

check(
    "Snapshot result field count exact",
    snapshot[
        "result_field_count"
    ]
    == 16,
)

check(
    "Snapshot certified",
    snapshot[
        "is_certified"
    ]
    is True,
)

check(
    "Snapshot failed-check count zero",
    snapshot[
        "checks_failed"
    ]
    == 0,
)

check(
    "Snapshot composite fingerprint independently verified",
    snapshot[
        "composite_fingerprint"
    ]
    == independent_composite,
)


for flag in (
    "workflow_mutation",
    "transition_execution",
    "history_mutation",
    "terminal_state_mutation",
    "durable_persistence",
    "runtime_execution",
    "recovery_execution",
    "coordinator_execution",
):

    check(
        f"Snapshot {flag}=False",
        snapshot[
            flag
        ]
        is False,
    )


snapshot_immutable = False

try:

    snapshot[
        "is_certified"
    ] = False

except Exception:

    snapshot_immutable = True


check(
    "Snapshot mapping immutable",
    snapshot_immutable,
)


# ============================================================================
# 21. Architecture declaration
# ============================================================================

explanation = (
    explain_lifecycle_certification_v3_5()
)

check(
    "Architecture phase exact",
    explanation[
        "phase"
    ]
    == "3.5",
)

check(
    "Architecture component exact",
    explanation[
        "component"
    ]
    == "Lifecycle Certification",
)

check(
    "Architecture version exact",
    explanation[
        "version"
    ]
    == LIFECYCLE_CERTIFICATION_VERSION,
)

check(
    "Architecture schema exact",
    explanation[
        "schema_version"
    ]
    == LIFECYCLE_CERTIFICATION_SCHEMA_VERSION,
)

check(
    "Architecture result-field count exact",
    explanation[
        "result_field_count"
    ]
    == 16,
)

check(
    "Architecture composite fingerprint exact",
    explanation[
        "composite_fingerprint"
    ]
    == independent_composite,
)


required_owns = (
    "Phase 3 lifecycle composite certification",
    "component identity verification",
    "component hash verification",
    "state-model consistency verification",
    "transition matrix consistency verification",
    "terminal-state consistency verification",
    "history compatibility verification",
    "terminal-protection compatibility verification",
    "lifecycle authority-boundary verification",
    "deterministic lifecycle evidence",
    "composite certification report",
    "composite lifecycle fingerprint",
)

for item in required_owns:

    check(
        f"3.5 ownership: {item}",
        item
        in explanation[
            "owns"
        ],
    )


required_exclusions = (
    "new workflow statuses",
    "new transition edges",
    "transition execution",
    "workflow object mutation",
    "lifecycle-history mutation",
    "terminal-state mutation",
    "persistence",
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
    "observability runtime",
    "security audit trail",
)

for item in required_exclusions:

    check(
        f"3.5 exclusion: {item}",
        item
        in explanation[
            "does_not_own"
        ],
    )


execution = (
    explanation[
        "execution_properties"
    ]
)

check(
    "Architecture declares read-only",
    execution[
        "read_only"
    ]
    is True,
)

check(
    "Architecture declares deterministic",
    execution[
        "deterministic"
    ]
    is True,
)

check(
    "Architecture declares side-effect free",
    execution[
        "side_effect_free"
    ]
    is True,
)


execution_immutable = False

try:

    execution[
        "read_only"
    ] = False

except Exception:

    execution_immutable = True


check(
    "Execution-properties mapping immutable",
    execution_immutable,
)


next_authority = (
    explanation[
        "next_authority"
    ]
)

check(
    "Phase 4 next authority exact",
    next_authority[
        "4.0"
    ]
    == "Dependency & Planning",
)

check(
    "Runtime bridge remains Phase 5.1",
    next_authority[
        "5.1"
    ]
    == "Coordination -> Runtime Bridge",
)


next_authority_immutable = False

try:

    next_authority[
        "4.0"
    ] = "changed"

except Exception:

    next_authority_immutable = True


check(
    "Next-authority mapping immutable",
    next_authority_immutable,
)


# ============================================================================
# 22. Static dependency boundary
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
        "workflow_lifecycle.state_machine"
    ),
    (
        "backend.server.coordination."
        "workflow_lifecycle.transition_validation"
    ),
    (
        "backend.server.coordination."
        "workflow_lifecycle.lifecycle_history"
    ),
    (
        "backend.server.coordination."
        "workflow_lifecycle.terminal_state_protection"
    ),
}


check(
    "3.5 imports only frozen Phase-3 lifecycle dependencies",
    set(
        backend_imports
    ).issubset(
        allowed_backend_imports
    ),
    repr(
        backend_imports
    ),
)


forbidden_import_fragments = (
    "backend.server.runtime",
    "backend.server.workers",
    "backend.server.jobs",
    "backend.server.routes",
    "backend.server.pipelines",
    "workflow_registry",
    "coordinator_registry",
    "registration_validation",
    "version_management",
)

bad_imports = [
    module
    for module
    in backend_imports
    if any(
        fragment
        in module
        for fragment
        in forbidden_import_fragments
    )
]


check(
    "3.5 has no Runtime/registry/execution imports",
    not bad_imports,
    repr(
        bad_imports
    ),
)


# ============================================================================
# 23. No duplicate lifecycle authority
# ============================================================================

forbidden_definition_names = {
    "UniversalWorkflowStatus",
    "validate_workflow_transition",
    "validate_terminal_state_mutation",
    "create_lifecycle_history_entry",
}

defined_classes = set()
defined_functions = set()

if tree is not None:

    for node in tree.body:

        if isinstance(
            node,
            ast.ClassDef,
        ):

            defined_classes.add(
                node.name
            )

        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):

            defined_functions.add(
                node.name
            )


duplicates = (
    defined_classes
    | defined_functions
) & forbidden_definition_names


check(
    "3.5 defines no duplicate lifecycle authorities",
    not duplicates,
    repr(
        sorted(
            duplicates
        )
    ),
)


# ============================================================================
# 24. No hidden execution / persistence / Runtime behavior
# ============================================================================

forbidden_call_names = {
    "open",
    "dispatch",
    "execute",
    "enqueue",
    "register_workflow",
    "register_coordinator",
    "run_coordinator",
    "invoke_coordinator",
    "uuid4",
}

forbidden_call_attributes = {
    "write_text",
    "write_bytes",
    "unlink",
    "mkdir",
    "rename",
    "replace",
    "send",
    "publish",
    "enqueue",
    "dispatch",
    "execute",
    "commit",
    "save",
}

behavior_violations = []

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

            if func.id in forbidden_call_names:

                behavior_violations.append(
                    f"call:{func.id}"
                )

        elif isinstance(
            func,
            ast.Attribute,
        ):

            if func.attr in forbidden_call_attributes:

                behavior_violations.append(
                    f"call-attribute:{func.attr}"
                )


check(
    "3.5 performs no hidden execution/persistence/runtime mutation work",
    not behavior_violations,
    repr(
        behavior_violations
    ),
)


# ============================================================================
# 25. No generated clock / identity / randomness
# ============================================================================

forbidden_generation_calls = {
    "now",
    "utcnow",
    "uuid4",
    "uuid1",
    "random",
    "randint",
    "randrange",
    "choice",
}

generation_violations = []

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

            if func.id in forbidden_generation_calls:

                generation_violations.append(
                    func.id
                )

        elif isinstance(
            func,
            ast.Attribute,
        ):

            if func.attr in forbidden_generation_calls:

                generation_violations.append(
                    func.attr
                )


check(
    "3.5 generates no timestamps/UUIDs/random values",
    not generation_violations,
    repr(
        generation_violations
    ),
)


# ============================================================================
# 26. Canonical Phase 3.5 SHA256
# ============================================================================

phase_35_sha = (
    sha256_file(
        PHASE_35
    )
)


print()
print("Canonical Phase 3.5 SHA256:")
print(
    phase_35_sha
)

print()
print("Canonical Phase 3.0 Composite Fingerprint:")
print(
    independent_composite
)


# ============================================================================
# 27. Final report
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
    "PHASE 3.5 - WORKFLOW LIFECYCLE FINAL CERTIFICATION",
    "=" * 96,
    "",
    (
        "Lifecycle Certification Version: "
        + LIFECYCLE_CERTIFICATION_VERSION
    ),
    (
        "Lifecycle Certification Schema: "
        + LIFECYCLE_CERTIFICATION_SCHEMA_VERSION
    ),
    "",
    (
        "3.1 Workflow State Machine: "
        + WORKFLOW_STATE_MACHINE_VERSION
    ),
    (
        "3.2 Transition Validation: "
        + TRANSITION_VALIDATION_VERSION
    ),
    (
        "3.3 Lifecycle History: "
        + LIFECYCLE_HISTORY_VERSION
    ),
    (
        "3.4 Terminal-State Protection: "
        + TERMINAL_STATE_PROTECTION_VERSION
    ),
    "",
    "Canonical Workflow States: 10",
    "Canonical Terminal States: 4",
    "Canonical Non-Terminal States: 6",
    "Canonical Transition Edges: 32",
    "Canonical Ordered State Pairs: 100",
    "Terminal-Current Pairs: 40",
    "Non-Terminal-Current Pairs: 60",
    "Legal History Edges: 32",
    "Undeclared History Pairs Rejected: 68",
    "",
    (
        "Phase 3.0 Composite Fingerprint: "
        + independent_composite
    ),
    (
        "Phase 3.5 SHA256: "
        + phase_35_sha
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
print("=" * 96)
print("PHASE 3.5 FINAL CERTIFICATION RESULT")
print("=" * 96)

print(
    "Checks:",
    len(
        checks
    ),
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
    REPORT.name,
)

print("=" * 96)


raise SystemExit(
    0
    if failed == 0
    else 1
)
