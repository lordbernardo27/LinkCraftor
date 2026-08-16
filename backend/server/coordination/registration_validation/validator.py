"""
LinkCraftor Universal Coordination Framework
Phase 2.3 - Registration Validation
============================================

Read-only validation layer across the frozen Workflow Registry and
Coordinator Registry.

Canonical validation direction
------------------------------
Every registered coordinator must reference an exact registered workflow.

Validation checks:
1. PipelineCoordinatorContract compatibility.
2. Exact workflow existence.
3. workflow_type agreement.
4. workflow_version agreement.
5. workflow_contract_version agreement.
6. frozen Universal Workflow Contract compatibility.

This phase validates consistency only.

It does NOT:
- register workflows;
- register coordinators;
- choose a coordinator version;
- activate/deactivate coordinators;
- inspect Runtime Registrations;
- resolve runtime handlers;
- execute coordinators;
- create jobs;
- order stages;
- construct dependency graphs;
- persist validation results.
"""

from __future__ import annotations

from dataclasses import dataclass

from types import MappingProxyType

from typing import (
    Any,
    Final,
    Mapping,
    Tuple,
)

from backend.server.coordination.universal_workflows.contract import (
    UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
)

from backend.server.coordination.pipeline_coordinators.contract import (
    PIPELINE_COORDINATOR_CONTRACT_VERSION,
    PipelineCoordinatorContract,
)

from backend.server.coordination.workflow_registry.registry import (
    WORKFLOW_REGISTRY_VERSION,
    WorkflowRegistryEntry,
    get_registered_workflow,
    list_registered_workflows,
)

from backend.server.coordination.coordinator_registry.registry import (
    COORDINATOR_REGISTRY_VERSION,
    get_registered_coordinator,
    list_registered_coordinators,
)


# ============================================================================
# 1. Component identity
# ============================================================================

REGISTRATION_VALIDATION_VERSION: Final[str] = (
    "registration_validation_v2.3.0"
)

REGISTRATION_VALIDATION_SCHEMA_VERSION: Final[str] = (
    "registration_validation_schema_v1"
)


# ============================================================================
# 2. Violation codes
# ============================================================================

VIOLATION_COORDINATOR_TYPE: Final[str] = (
    "coordinator_type_invalid"
)

VIOLATION_COORDINATOR_CONTRACT_VERSION: Final[str] = (
    "coordinator_contract_version_mismatch"
)

VIOLATION_WORKFLOW_NOT_REGISTERED: Final[str] = (
    "workflow_not_registered"
)

VIOLATION_WORKFLOW_TYPE_MISMATCH: Final[str] = (
    "workflow_type_mismatch"
)

VIOLATION_WORKFLOW_VERSION_MISMATCH: Final[str] = (
    "workflow_version_mismatch"
)

VIOLATION_WORKFLOW_CONTRACT_MISMATCH: Final[str] = (
    "workflow_contract_version_mismatch"
)

VIOLATION_UNIVERSAL_WORKFLOW_CONTRACT: Final[str] = (
    "universal_workflow_contract_version_mismatch"
)


# ============================================================================
# 3. Immutable helpers
# ============================================================================

def _freeze(
    value: Any,
) -> Any:

    if isinstance(
        value,
        Mapping,
    ):

        return MappingProxyType(
            {
                str(key): _freeze(item)
                for key, item
                in value.items()
            }
        )

    if isinstance(
        value,
        list,
    ):

        return tuple(
            _freeze(item)
            for item in value
        )

    if isinstance(
        value,
        tuple,
    ):

        return tuple(
            _freeze(item)
            for item in value
        )

    if isinstance(
        value,
        (set, frozenset),
    ):

        return tuple(
            sorted(
                (
                    _freeze(item)
                    for item in value
                ),
                key=repr,
            )
        )

    return value


def _violation(
    *,
    code: str,
    message: str,
    field: str,
    expected: Any = None,
    actual: Any = None,
) -> Mapping[str, Any]:

    return _freeze(
        {
            "code": code,
            "message": message,
            "field": field,
            "expected": expected,
            "actual": actual,
        }
    )


# ============================================================================
# 4. Validation result
# ============================================================================

@dataclass(
    frozen=True,
    slots=True,
)
class RegistrationValidationResult:
    """
    Immutable validation result for one coordinator registration.
    """

    coordinator_id: str
    coordinator_version: str

    workflow_type: str
    workflow_version: str

    is_valid: bool

    violations: Tuple[
        Mapping[str, Any],
        ...
    ]

    checked_rule_count: int

    validation_version: str = (
        REGISTRATION_VALIDATION_VERSION
    )


    def __post_init__(
        self,
    ) -> None:

        object.__setattr__(
            self,
            "violations",
            tuple(
                _freeze(item)
                for item
                in self.violations
            ),
        )


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "coordinator_id":
                self.coordinator_id,

            "coordinator_version":
                self.coordinator_version,

            "workflow_type":
                self.workflow_type,

            "workflow_version":
                self.workflow_version,

            "is_valid":
                self.is_valid,

            "violations":
                [
                    dict(item)
                    for item
                    in self.violations
                ],

            "checked_rule_count":
                self.checked_rule_count,

            "validation_version":
                self.validation_version,
        }


# ============================================================================
# 5. Core coordinator ↔ workflow validation
# ============================================================================

def validate_coordinator_registration(
    coordinator: PipelineCoordinatorContract,
) -> RegistrationValidationResult:
    """
    Validate one coordinator declaration against the Workflow Registry.

    This function performs no registration and no execution.
    """

    violations: list[
        Mapping[str, Any]
    ] = []

    checked_rule_count = 0


    # ------------------------------------------------------------------------
    # Rule 1 - registered object type
    # ------------------------------------------------------------------------

    checked_rule_count += 1

    if not isinstance(
        coordinator,
        PipelineCoordinatorContract,
    ):

        violations.append(
            _violation(
                code=VIOLATION_COORDINATOR_TYPE,
                message=(
                    "coordinator must be a "
                    "PipelineCoordinatorContract"
                ),
                field="coordinator",
                expected="PipelineCoordinatorContract",
                actual=type(
                    coordinator
                ).__name__,
            )
        )

        return RegistrationValidationResult(
            coordinator_id="",
            coordinator_version="",
            workflow_type="",
            workflow_version="",
            is_valid=False,
            violations=tuple(
                violations
            ),
            checked_rule_count=(
                checked_rule_count
            ),
        )


    # ------------------------------------------------------------------------
    # Rule 2 - Pipeline Coordinator Contract compatibility
    # ------------------------------------------------------------------------

    checked_rule_count += 1

    if (
        coordinator.contract_version
        != PIPELINE_COORDINATOR_CONTRACT_VERSION
    ):

        violations.append(
            _violation(
                code=(
                    VIOLATION_COORDINATOR_CONTRACT_VERSION
                ),
                message=(
                    "coordinator contract version "
                    "does not match the frozen "
                    "Pipeline Coordinator Contract"
                ),
                field="contract_version",
                expected=(
                    PIPELINE_COORDINATOR_CONTRACT_VERSION
                ),
                actual=(
                    coordinator.contract_version
                ),
            )
        )


    # ------------------------------------------------------------------------
    # Rule 3 - exact workflow existence
    # ------------------------------------------------------------------------

    checked_rule_count += 1

    workflow = get_registered_workflow(
        workflow_type=(
            coordinator.workflow_type
        ),
        workflow_version=(
            coordinator.workflow_version
        ),
    )

    if workflow is None:

        violations.append(
            _violation(
                code=(
                    VIOLATION_WORKFLOW_NOT_REGISTERED
                ),
                message=(
                    "coordinator references an exact "
                    "workflow that is not registered"
                ),
                field=(
                    "workflow_type+workflow_version"
                ),
                expected=(
                    "exact registered workflow"
                ),
                actual=(
                    f"{coordinator.workflow_type}@"
                    f"{coordinator.workflow_version}"
                ),
            )
        )

        return RegistrationValidationResult(
            coordinator_id=(
                coordinator.coordinator_id
            ),
            coordinator_version=(
                coordinator.coordinator_version
            ),
            workflow_type=(
                coordinator.workflow_type
            ),
            workflow_version=(
                coordinator.workflow_version
            ),
            is_valid=False,
            violations=tuple(
                violations
            ),
            checked_rule_count=(
                checked_rule_count
            ),
        )


    # ------------------------------------------------------------------------
    # Rule 4 - workflow_type agreement
    # ------------------------------------------------------------------------

    checked_rule_count += 1

    if (
        coordinator.workflow_type
        != workflow.workflow_type
    ):

        violations.append(
            _violation(
                code=(
                    VIOLATION_WORKFLOW_TYPE_MISMATCH
                ),
                message=(
                    "coordinator workflow_type does "
                    "not match Workflow Registry entry"
                ),
                field="workflow_type",
                expected=(
                    workflow.workflow_type
                ),
                actual=(
                    coordinator.workflow_type
                ),
            )
        )


    # ------------------------------------------------------------------------
    # Rule 5 - workflow_version agreement
    # ------------------------------------------------------------------------

    checked_rule_count += 1

    if (
        coordinator.workflow_version
        != workflow.workflow_version
    ):

        violations.append(
            _violation(
                code=(
                    VIOLATION_WORKFLOW_VERSION_MISMATCH
                ),
                message=(
                    "coordinator workflow_version does "
                    "not match Workflow Registry entry"
                ),
                field="workflow_version",
                expected=(
                    workflow.workflow_version
                ),
                actual=(
                    coordinator.workflow_version
                ),
            )
        )


    # ------------------------------------------------------------------------
    # Rule 6 - coordinator ↔ workflow contract compatibility
    # ------------------------------------------------------------------------

    checked_rule_count += 1

    if (
        coordinator.workflow_contract_version
        != workflow.workflow_contract_version
    ):

        violations.append(
            _violation(
                code=(
                    VIOLATION_WORKFLOW_CONTRACT_MISMATCH
                ),
                message=(
                    "coordinator workflow_contract_version "
                    "does not match Workflow Registry entry"
                ),
                field="workflow_contract_version",
                expected=(
                    workflow.workflow_contract_version
                ),
                actual=(
                    coordinator.workflow_contract_version
                ),
            )
        )


    # ------------------------------------------------------------------------
    # Rule 7 - frozen Universal Workflow Contract compatibility
    # ------------------------------------------------------------------------

    checked_rule_count += 1

    if (
        workflow.workflow_contract_version
        != UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ):

        violations.append(
            _violation(
                code=(
                    VIOLATION_UNIVERSAL_WORKFLOW_CONTRACT
                ),
                message=(
                    "Workflow Registry entry does not use "
                    "the frozen Universal Workflow Contract"
                ),
                field="workflow_contract_version",
                expected=(
                    UNIVERSAL_WORKFLOW_CONTRACT_VERSION
                ),
                actual=(
                    workflow.workflow_contract_version
                ),
            )
        )


    return RegistrationValidationResult(
        coordinator_id=(
            coordinator.coordinator_id
        ),
        coordinator_version=(
            coordinator.coordinator_version
        ),
        workflow_type=(
            coordinator.workflow_type
        ),
        workflow_version=(
            coordinator.workflow_version
        ),
        is_valid=(
            len(
                violations
            )
            == 0
        ),
        violations=tuple(
            violations
        ),
        checked_rule_count=(
            checked_rule_count
        ),
    )


# ============================================================================
# 6. Validate one exact registered coordinator
# ============================================================================

def validate_registered_coordinator(
    *,
    coordinator_id: str,
    coordinator_version: str,
) -> RegistrationValidationResult:
    """
    Validate an exact registered coordinator.

    Missing coordinator identity is treated as caller/lookup failure rather
    than coordinator/workflow consistency evidence.
    """

    coordinator = (
        get_registered_coordinator(
            coordinator_id=coordinator_id,
            coordinator_version=coordinator_version,
        )
    )

    if coordinator is None:

        raise LookupError(
            "coordinator is not registered: "
            f"{coordinator_id}@"
            f"{coordinator_version}"
        )

    return validate_coordinator_registration(
        coordinator
    )


# ============================================================================
# 7. Registry-wide validation
# ============================================================================

def validate_registration_registry(
) -> Mapping[
    str,
    Any,
]:
    """
    Validate all currently registered coordinators deterministically.

    A workflow without a registered coordinator is reported as an unbound
    workflow for evidence only. It is not a Phase 2.3 violation.

    Phase 2.3 validates coordinator -> workflow consistency.
    It does not select or require an active/default coordinator.
    """

    coordinators = (
        list_registered_coordinators()
    )

    workflows = (
        list_registered_workflows()
    )

    results = tuple(
        validate_coordinator_registration(
            coordinator
        )
        for coordinator
        in coordinators
    )

    valid_count = sum(
        1
        for result
        in results
        if result.is_valid
    )

    invalid_count = (
        len(
            results
        )
        - valid_count
    )

    coordinator_workflow_keys = {
        (
            coordinator.workflow_type,
            coordinator.workflow_version,
        )
        for coordinator
        in coordinators
    }

    unbound_workflows = tuple(
        workflow
        for workflow
        in workflows
        if (
            workflow.workflow_type,
            workflow.workflow_version,
        )
        not in coordinator_workflow_keys
    )

    violation_count = sum(
        len(
            result.violations
        )
        for result
        in results
    )

    report = {
        "validation_version":
            REGISTRATION_VALIDATION_VERSION,

        "schema_version":
            REGISTRATION_VALIDATION_SCHEMA_VERSION,

        "workflow_registry_version":
            WORKFLOW_REGISTRY_VERSION,

        "coordinator_registry_version":
            COORDINATOR_REGISTRY_VERSION,

        "universal_workflow_contract_version":
            UNIVERSAL_WORKFLOW_CONTRACT_VERSION,

        "pipeline_coordinator_contract_version":
            PIPELINE_COORDINATOR_CONTRACT_VERSION,

        "coordinator_count":
            len(
                coordinators
            ),

        "workflow_count":
            len(
                workflows
            ),

        "valid_coordinator_count":
            valid_count,

        "invalid_coordinator_count":
            invalid_count,

        "violation_count":
            violation_count,

        "is_valid":
            invalid_count == 0,

        "results":
            tuple(
                _freeze(
                    result.to_dict()
                )
                for result
                in results
            ),

        "unbound_workflow_count":
            len(
                unbound_workflows
            ),

        "unbound_workflows":
            tuple(
                _freeze(
                    {
                        "workflow_type":
                            workflow.workflow_type,

                        "workflow_version":
                            workflow.workflow_version,
                    }
                )
                for workflow
                in unbound_workflows
            ),

        "unbound_workflows_are_violations":
            False,

        "persistence":
            False,

        "version_selection":
            False,

        "runtime_validation":
            False,

        "dependency_validation":
            False,
    }

    return _freeze(
        report
    )


# ============================================================================
# 8. Validation explanation
# ============================================================================

def explain_registration_validation_v2_3(
) -> Mapping[
    str,
    Any,
]:

    return _freeze(
        {
            "phase":
                "2.3",

            "component":
                "Registration Validation",

            "version":
                REGISTRATION_VALIDATION_VERSION,

            "validation_direction":
                "coordinator_to_workflow",

            "owns": (
                "Workflow Registry to Coordinator Registry consistency",
                "exact workflow existence validation",
                "exact workflow identity agreement",
                "Workflow Contract compatibility",
                "Pipeline Coordinator Contract compatibility",
                "deterministic validation results",
                "deterministic registry-wide validation report",
                "validation violations and evidence",
            ),

            "does_not_own": (
                "workflow registration",
                "coordinator registration",
                "version selection",
                "latest coordinator selection",
                "default coordinator selection",
                "coordinator activation",
                "coordinator deactivation",
                "stage ordering",
                "dependency graphs",
                "Runtime Registration",
                "runtime handler lookup",
                "runtime job creation",
                "coordinator invocation",
                "workflow execution",
                "lifecycle transitions",
                "persistence",
                "recovery",
            ),

            "future_authority": {
                "2.4":
                    "Version Management",

                "4.0":
                    "Dependency & Planning",

                "5.0":
                    "Runtime Integration",
            },
        }
    )


__all__ = [
    "REGISTRATION_VALIDATION_VERSION",
    "REGISTRATION_VALIDATION_SCHEMA_VERSION",
    "VIOLATION_COORDINATOR_TYPE",
    "VIOLATION_COORDINATOR_CONTRACT_VERSION",
    "VIOLATION_WORKFLOW_NOT_REGISTERED",
    "VIOLATION_WORKFLOW_TYPE_MISMATCH",
    "VIOLATION_WORKFLOW_VERSION_MISMATCH",
    "VIOLATION_WORKFLOW_CONTRACT_MISMATCH",
    "VIOLATION_UNIVERSAL_WORKFLOW_CONTRACT",
    "RegistrationValidationResult",
    "validate_coordinator_registration",
    "validate_registered_coordinator",
    "validate_registration_registry",
    "explain_registration_validation_v2_3",
]
