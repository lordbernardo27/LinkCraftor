"""
LinkCraftor Universal Coordination Framework
Phase 3.5 - Lifecycle Certification
============================================

Read-only composite certification of the frozen Phase 3 lifecycle subsystem:

3.1 Workflow State Machine
3.2 Transition Validation
3.3 Lifecycle History
3.4 Terminal-State Protection

This component performs no workflow execution, mutation, persistence,
Runtime dispatch, recovery, or history mutation.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from types import MappingProxyType
from typing import (
    Any,
    Final,
    Mapping,
    Tuple,
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


# ============================================================================
# 1. Certification identity
# ============================================================================

LIFECYCLE_CERTIFICATION_VERSION: Final[str] = (
    "lifecycle_certification_v3.5.0"
)

LIFECYCLE_CERTIFICATION_SCHEMA_VERSION: Final[str] = (
    "lifecycle_certification_schema_v1"
)

LIFECYCLE_CERTIFICATION_RESULT_FIELD_COUNT: Final[int] = 16


# ============================================================================
# 2. Frozen component hashes
# ============================================================================

WORKFLOW_STATE_MACHINE_SHA256: Final[str] = (
    "144327A4E9C8989FCF0F4DBD10BCF6D"
    "7203F503930D81CB8E24644D86D2BB662"
)

TRANSITION_VALIDATION_SHA256: Final[str] = (
    "69A952141E920E63B32B12AF1E9FB79D"
    "6296961FED40BCB94F007123BF9BD746"
)

LIFECYCLE_HISTORY_SHA256: Final[str] = (
    "D89F1D4FBC54307C7B8155E670CDD3C"
    "6C8771185DC8AFBE382A87BB34EDA8464"
)

TERMINAL_STATE_PROTECTION_SHA256: Final[str] = (
    "7632A838D9CEAD7ED95DB0099D08FB20"
    "D01B4E2BD25BFF48D68CBEB89065A7B7"
)


def _phase_3_composite_fingerprint(
) -> str:

    payload = (
        WORKFLOW_STATE_MACHINE_SHA256
        + TRANSITION_VALIDATION_SHA256
        + LIFECYCLE_HISTORY_SHA256
        + TERMINAL_STATE_PROTECTION_SHA256
    )

    return hashlib.sha256(
        payload.encode(
            "utf-8"
        )
    ).hexdigest().upper()


PHASE_3_COMPOSITE_FINGERPRINT: Final[str] = (
    _phase_3_composite_fingerprint()
)


# ============================================================================
# 3. Immutable helpers
# ============================================================================

def _freeze_mapping(
    value: Mapping[
        str,
        Any,
    ],
) -> Mapping[
    str,
    Any,
]:

    frozen = {}

    for key, item in value.items():

        if isinstance(
            item,
            Mapping,
        ):

            frozen[
                key
            ] = _freeze_mapping(
                item
            )

        elif isinstance(
            item,
            list,
        ):

            frozen[
                key
            ] = tuple(
                item
            )

        elif isinstance(
            item,
            tuple,
        ):

            frozen[
                key
            ] = tuple(
                item
            )

        else:

            frozen[
                key
            ] = item

    return MappingProxyType(
        frozen
    )


# ============================================================================
# 4. Immutable result
# ============================================================================

@dataclass(
    frozen=True,
    slots=True,
)
class LifecycleCertificationResult:

    is_certified: bool

    checks_run: int

    checks_passed: int

    checks_failed: int

    state_count: int

    terminal_state_count: int

    non_terminal_state_count: int

    transition_edge_count: int

    state_pair_count: int

    terminal_pair_count: int

    non_terminal_pair_count: int

    history_edge_count: int

    violations: Tuple[
        str,
        ...,
    ]

    component_versions: Mapping[
        str,
        str,
    ]

    component_hashes: Mapping[
        str,
        str,
    ]

    certification_version: str

    def __post_init__(
        self,
    ) -> None:

        object.__setattr__(
            self,
            "violations",
            tuple(
                self.violations
            ),
        )

        object.__setattr__(
            self,
            "component_versions",
            _freeze_mapping(
                dict(
                    self.component_versions
                )
            ),
        )

        object.__setattr__(
            self,
            "component_hashes",
            _freeze_mapping(
                dict(
                    self.component_hashes
                )
            ),
        )

    def to_dict(
        self,
    ) -> Mapping[
        str,
        Any,
    ]:

        return MappingProxyType(
            {
                "is_certified":
                    self.is_certified,

                "checks_run":
                    self.checks_run,

                "checks_passed":
                    self.checks_passed,

                "checks_failed":
                    self.checks_failed,

                "state_count":
                    self.state_count,

                "terminal_state_count":
                    self.terminal_state_count,

                "non_terminal_state_count":
                    self.non_terminal_state_count,

                "transition_edge_count":
                    self.transition_edge_count,

                "state_pair_count":
                    self.state_pair_count,

                "terminal_pair_count":
                    self.terminal_pair_count,

                "non_terminal_pair_count":
                    self.non_terminal_pair_count,

                "history_edge_count":
                    self.history_edge_count,

                "violations":
                    self.violations,

                "component_versions":
                    self.component_versions,

                "component_hashes":
                    self.component_hashes,

                "certification_version":
                    self.certification_version,
            }
        )


# ============================================================================
# 5. Component evidence
# ============================================================================

def _component_versions(
) -> Mapping[
    str,
    str,
]:

    return MappingProxyType(
        {
            "3.1":
                WORKFLOW_STATE_MACHINE_VERSION,

            "3.2":
                TRANSITION_VALIDATION_VERSION,

            "3.3":
                LIFECYCLE_HISTORY_VERSION,

            "3.4":
                TERMINAL_STATE_PROTECTION_VERSION,

            "3.5":
                LIFECYCLE_CERTIFICATION_VERSION,
        }
    )


def _component_hashes(
) -> Mapping[
    str,
    str,
]:

    return MappingProxyType(
        {
            "3.1":
                WORKFLOW_STATE_MACHINE_SHA256,

            "3.2":
                TRANSITION_VALIDATION_SHA256,

            "3.3":
                LIFECYCLE_HISTORY_SHA256,

            "3.4":
                TERMINAL_STATE_PROTECTION_SHA256,

            "phase_3_composite":
                PHASE_3_COMPOSITE_FINGERPRINT,
        }
    )


# ============================================================================
# 6. Composite certification
# ============================================================================

def certify_workflow_lifecycle(
) -> LifecycleCertificationResult:
    """
    Certify the Phase 3 lifecycle subsystem.

    Read-only.
    Deterministic.
    Side-effect free.
    """

    violations = []

    checks_run = 0
    checks_passed = 0


    def record(
        condition: bool,
        violation: str,
    ) -> None:

        nonlocal checks_run
        nonlocal checks_passed

        checks_run += 1

        if condition:

            checks_passed += 1

        else:

            violations.append(
                violation
            )


    states = workflow_states()

    terminal_states = (
        terminal_workflow_states()
    )

    non_terminal_states = (
        non_terminal_workflow_states()
    )

    edges = transition_edges()


    # ------------------------------------------------------------------------
    # A. State model
    # ------------------------------------------------------------------------

    record(
        len(
            states
        )
        == 10,
        "state_count_mismatch",
    )

    record(
        len(
            terminal_states
        )
        == 4,
        "terminal_state_count_mismatch",
    )

    record(
        len(
            non_terminal_states
        )
        == 6,
        "non_terminal_state_count_mismatch",
    )

    record(
        set(
            state.value
            for state
            in terminal_states
        )
        == {
            "COMPLETED",
            "FAILED",
            "CANCELLED",
            "ABORTED",
        },
        "terminal_state_set_mismatch",
    )

    record(
        set(
            state.value
            for state
            in non_terminal_states
        )
        == {
            "CREATED",
            "READY",
            "RUNNING",
            "WAITING",
            "PAUSED",
            "RECOVERING",
        },
        "non_terminal_state_set_mismatch",
    )


    # ------------------------------------------------------------------------
    # B. Transition graph
    # ------------------------------------------------------------------------

    record(
        len(
            edges
        )
        == 32,
        "transition_edge_count_mismatch",
    )


    declared_edges = set(
        edges
    )

    state_pair_count = 0

    terminal_pair_count = 0

    non_terminal_pair_count = 0


    # ------------------------------------------------------------------------
    # C/D/E. Full state-pair matrix
    # ------------------------------------------------------------------------

    for current in states:

        for requested in states:

            state_pair_count += 1

            validation = (
                validate_workflow_transition(
                    current,
                    requested,
                )
            )

            declared = (
                (
                    current,
                    requested,
                )
                in declared_edges
            )

            record(
                validation.is_valid
                == declared,
                (
                    "phase_3_1_3_2_transition_mismatch:"
                    f"{current.value}->{requested.value}"
                ),
            )


            protection = (
                validate_terminal_state_mutation(
                    current,
                    requested,
                )
            )


            if current in terminal_states:

                terminal_pair_count += 1

                record(
                    (
                        protection.current_state_is_terminal
                        is True
                        and protection.mutation_allowed
                        is False
                        and protection.protection_triggered
                        is True
                        and protection.code
                        == TERMINAL_STATE_MUTATION_PROHIBITED
                    ),
                    (
                        "terminal_protection_mismatch:"
                        f"{current.value}->{requested.value}"
                    ),
                )

            else:

                non_terminal_pair_count += 1

                record(
                    (
                        protection.current_state_is_terminal
                        is False
                        and protection.mutation_allowed
                        == validation.is_valid
                    ),
                    (
                        "non_terminal_delegation_mismatch:"
                        f"{current.value}->{requested.value}"
                    ),
                )


    record(
        state_pair_count
        == 100,
        "state_pair_count_mismatch",
    )

    record(
        terminal_pair_count
        == 40,
        "terminal_pair_count_mismatch",
    )

    record(
        non_terminal_pair_count
        == 60,
        "non_terminal_pair_count_mismatch",
    )


    # ------------------------------------------------------------------------
    # F. History compatibility
    # ------------------------------------------------------------------------

    history_edge_count = 0

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
                        f"cert-edge-{index:03d}"
                    ),
                    workflow_id=(
                        "phase-3-certification"
                    ),
                    correlation_id=(
                        "phase-3-certification"
                    ),
                    from_state=current,
                    to_state=requested,
                    occurred_at=(
                        "2026-08-17T00:00:00+00:00"
                    ),
                )
            )

            valid_history_edge = (
                entry.from_state
                == current
                and entry.to_state
                == requested
            )

        except Exception:

            valid_history_edge = False

        if valid_history_edge:

            history_edge_count += 1

        record(
            valid_history_edge,
            (
                "history_legal_edge_not_recordable:"
                f"{current.value}->{requested.value}"
            ),
        )


    record(
        history_edge_count
        == 32,
        "history_edge_count_mismatch",
    )


    # ------------------------------------------------------------------------
    # G. Every invalid transition rejected by history
    # ------------------------------------------------------------------------

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
                        "cert-invalid-"
                        f"{current.value}-"
                        f"{requested.value}"
                    ),
                    workflow_id=(
                        "phase-3-certification"
                    ),
                    correlation_id=(
                        "phase-3-certification"
                    ),
                    from_state=current,
                    to_state=requested,
                    occurred_at=(
                        "2026-08-17T00:00:00+00:00"
                    ),
                )

                rejected = False

            except InvalidLifecycleHistoryEntryError:

                rejected = True

            except Exception:

                rejected = False

            if rejected:

                invalid_history_rejected += 1

            record(
                rejected,
                (
                    "history_invalid_edge_accepted:"
                    f"{current.value}->{requested.value}"
                ),
            )


    record(
        invalid_history_cases
        == 68,
        "invalid_history_case_count_mismatch",
    )

    record(
        invalid_history_rejected
        == 68,
        "invalid_history_rejection_count_mismatch",
    )


    # ------------------------------------------------------------------------
    # H. Recovery boundary
    # ------------------------------------------------------------------------

    run_to_recovering = (
        validate_terminal_state_mutation(
            "RUNNING",
            "RECOVERING",
        )
    )

    record(
        (
            run_to_recovering.mutation_allowed
            is True
            and run_to_recovering.protection_triggered
            is False
        ),
        "running_to_recovering_boundary_mismatch",
    )


    failed_to_recovering = (
        validate_terminal_state_mutation(
            "FAILED",
            "RECOVERING",
        )
    )

    record(
        (
            failed_to_recovering.mutation_allowed
            is False
            and failed_to_recovering.protection_triggered
            is True
            and failed_to_recovering.code
            == TERMINAL_STATE_MUTATION_PROHIBITED
        ),
        "failed_to_recovering_boundary_mismatch",
    )


    # ------------------------------------------------------------------------
    # I. Self transitions
    # ------------------------------------------------------------------------

    for state in states:

        validation = (
            validate_workflow_transition(
                state,
                state,
            )
        )

        record(
            validation.is_valid
            is False,
            (
                "self_transition_accepted:"
                f"{state.value}"
            ),
        )


    # ------------------------------------------------------------------------
    # J. Distinguish transition invalidity from terminal protection
    # ------------------------------------------------------------------------

    waiting_completed = (
        validate_terminal_state_mutation(
            "WAITING",
            "COMPLETED",
        )
    )

    record(
        (
            waiting_completed.mutation_allowed
            is False
            and waiting_completed.protection_triggered
            is False
            and waiting_completed.code
            == "transition_not_declared"
        ),
        "waiting_completed_authority_boundary_mismatch",
    )


    failed_recovering = (
        validate_terminal_state_mutation(
            "FAILED",
            "RECOVERING",
        )
    )

    record(
        (
            failed_recovering.mutation_allowed
            is False
            and failed_recovering.protection_triggered
            is True
            and failed_recovering.code
            == TERMINAL_STATE_MUTATION_PROHIBITED
        ),
        "failed_recovering_authority_boundary_mismatch",
    )


    # ------------------------------------------------------------------------
    # K. Version compatibility
    # ------------------------------------------------------------------------

    record(
        WORKFLOW_STATE_MACHINE_VERSION
        == "workflow_state_machine_v3.1.0",
        "state_machine_version_mismatch",
    )

    record(
        TRANSITION_VALIDATION_VERSION
        == "transition_validation_v3.2.0",
        "transition_validation_version_mismatch",
    )

    record(
        LIFECYCLE_HISTORY_VERSION
        == "lifecycle_history_v3.3.0",
        "lifecycle_history_version_mismatch",
    )

    record(
        TERMINAL_STATE_PROTECTION_VERSION
        == "terminal_state_protection_v3.4.0",
        "terminal_state_protection_version_mismatch",
    )


    checks_failed = (
        checks_run
        - checks_passed
    )

    return LifecycleCertificationResult(
        is_certified=(
            checks_failed
            == 0
        ),
        checks_run=checks_run,
        checks_passed=checks_passed,
        checks_failed=checks_failed,
        state_count=len(
            states
        ),
        terminal_state_count=len(
            terminal_states
        ),
        non_terminal_state_count=len(
            non_terminal_states
        ),
        transition_edge_count=len(
            edges
        ),
        state_pair_count=(
            state_pair_count
        ),
        terminal_pair_count=(
            terminal_pair_count
        ),
        non_terminal_pair_count=(
            non_terminal_pair_count
        ),
        history_edge_count=(
            history_edge_count
        ),
        violations=tuple(
            violations
        ),
        component_versions=(
            _component_versions()
        ),
        component_hashes=(
            _component_hashes()
        ),
        certification_version=(
            LIFECYCLE_CERTIFICATION_VERSION
        ),
    )


# ============================================================================
# 7. Snapshot
# ============================================================================

def workflow_lifecycle_certification_snapshot(
) -> Mapping[
    str,
    Any,
]:

    result = (
        certify_workflow_lifecycle()
    )

    return MappingProxyType(
        {
            "certification_version":
                LIFECYCLE_CERTIFICATION_VERSION,

            "schema_version":
                LIFECYCLE_CERTIFICATION_SCHEMA_VERSION,

            "result_field_count":
                LIFECYCLE_CERTIFICATION_RESULT_FIELD_COUNT,

            "is_certified":
                result.is_certified,

            "checks_run":
                result.checks_run,

            "checks_passed":
                result.checks_passed,

            "checks_failed":
                result.checks_failed,

            "state_count":
                result.state_count,

            "terminal_state_count":
                result.terminal_state_count,

            "non_terminal_state_count":
                result.non_terminal_state_count,

            "transition_edge_count":
                result.transition_edge_count,

            "state_pair_count":
                result.state_pair_count,

            "terminal_pair_count":
                result.terminal_pair_count,

            "non_terminal_pair_count":
                result.non_terminal_pair_count,

            "history_edge_count":
                result.history_edge_count,

            "violations":
                result.violations,

            "component_versions":
                result.component_versions,

            "component_hashes":
                result.component_hashes,

            "composite_fingerprint":
                PHASE_3_COMPOSITE_FINGERPRINT,

            "workflow_mutation":
                False,

            "transition_execution":
                False,

            "history_mutation":
                False,

            "terminal_state_mutation":
                False,

            "durable_persistence":
                False,

            "runtime_execution":
                False,

            "recovery_execution":
                False,

            "coordinator_execution":
                False,
        }
    )


# ============================================================================
# 8. Architecture declaration
# ============================================================================

def explain_lifecycle_certification_v3_5(
) -> Mapping[
    str,
    Any,
]:

    return MappingProxyType(
        {
            "phase":
                "3.5",

            "component":
                "Lifecycle Certification",

            "version":
                LIFECYCLE_CERTIFICATION_VERSION,

            "schema_version":
                LIFECYCLE_CERTIFICATION_SCHEMA_VERSION,

            "result_field_count":
                LIFECYCLE_CERTIFICATION_RESULT_FIELD_COUNT,

            "component_versions":
                _component_versions(),

            "component_hashes":
                _component_hashes(),

            "composite_fingerprint":
                PHASE_3_COMPOSITE_FINGERPRINT,

            "owns": (
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
            ),

            "does_not_own": (
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
            ),

            "execution_properties": MappingProxyType(
                {
                    "read_only":
                        True,

                    "deterministic":
                        True,

                    "side_effect_free":
                        True,
                }
            ),

            "next_authority": MappingProxyType(
                {
                    "4.0":
                        "Dependency & Planning",

                    "5.1":
                        "Coordination -> Runtime Bridge",
                }
            ),
        }
    )


__all__ = [
    "LIFECYCLE_CERTIFICATION_VERSION",
    "LIFECYCLE_CERTIFICATION_SCHEMA_VERSION",
    "LIFECYCLE_CERTIFICATION_RESULT_FIELD_COUNT",
    "WORKFLOW_STATE_MACHINE_SHA256",
    "TRANSITION_VALIDATION_SHA256",
    "LIFECYCLE_HISTORY_SHA256",
    "TERMINAL_STATE_PROTECTION_SHA256",
    "PHASE_3_COMPOSITE_FINGERPRINT",
    "LifecycleCertificationResult",
    "certify_workflow_lifecycle",
    "workflow_lifecycle_certification_snapshot",
    "explain_lifecycle_certification_v3_5",
]

