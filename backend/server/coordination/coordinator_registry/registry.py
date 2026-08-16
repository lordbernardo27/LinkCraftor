"""
LinkCraftor Universal Coordination Framework
Phase 2.2 - Coordinator Registration
============================================

Canonical in-memory registry of Pipeline Coordinator Contracts.

Coordinator registration identity
---------------------------------
A coordinator registration is uniquely identified by:

    coordinator_id + coordinator_version

Registered object
-----------------
The registered object is the frozen Phase 1.2
PipelineCoordinatorContract itself.

This registry intentionally does NOT copy the coordinator contract fields
into another registration schema. The Phase 1.2 contract remains the
single source of truth.

Authority boundaries
--------------------
Coordinator Registration owns:
- declaration that a coordinator identity/version exists;
- exact coordinator-version registration;
- exact coordinator-version lookup;
- duplicate coordinator identity rejection;
- immutable registry inspection;
- deterministic listing;
- inspection of coordinators declaring a workflow identity.

Coordinator Registration does NOT own:
- workflow existence validation;
- workflow/coordinator cross-registration validation;
- coordinator selection for execution;
- latest/default coordinator selection;
- coordinator activation/deactivation;
- stage ordering;
- dependency planning;
- Runtime Registration;
- runtime handler resolution;
- runtime job creation;
- coordinator invocation;
- workflow execution;
- lifecycle state;
- persistence;
- migration/version governance.

Cross-registry validation belongs to Phase 2.3.
Version selection/governance belongs to Phase 2.4.
"""

from __future__ import annotations

from threading import RLock
from types import MappingProxyType
from typing import (
    Any,
    Final,
    Mapping,
    Optional,
    Tuple,
)

from backend.server.coordination.pipeline_coordinators.contract import (
    PIPELINE_COORDINATOR_CONTRACT_VERSION,
    PipelineCoordinatorContract,
)


# ============================================================================
# 1. Registry identity
# ============================================================================

COORDINATOR_REGISTRY_VERSION: Final[str] = (
    "coordinator_registry_v2.2.0"
)

COORDINATOR_REGISTRY_SCHEMA_VERSION: Final[str] = (
    "coordinator_registry_schema_v1"
)


# ============================================================================
# 2. Errors
# ============================================================================

class CoordinatorRegistryError(
    ValueError
):
    """Base Coordinator Registry error."""


class CoordinatorAlreadyRegisteredError(
    CoordinatorRegistryError
):
    """Raised when an exact coordinator identity already exists."""


class CoordinatorNotRegisteredError(
    CoordinatorRegistryError
):
    """Raised when an exact coordinator identity cannot be resolved."""


# ============================================================================
# 3. Canonical identity
# ============================================================================

CoordinatorRegistryKey = Tuple[
    str,
    str,
]


def coordinator_registry_key(
    *,
    coordinator_id: str,
    coordinator_version: str,
) -> CoordinatorRegistryKey:
    """
    Construct the exact coordinator registry key.

    Validation is intentionally delegated to the frozen
    PipelineCoordinatorContract when contracts are registered.
    Lookup keys still require non-empty strings.
    """

    if not isinstance(
        coordinator_id,
        str,
    ):
        raise CoordinatorRegistryError(
            "coordinator_id must be a string"
        )

    if not isinstance(
        coordinator_version,
        str,
    ):
        raise CoordinatorRegistryError(
            "coordinator_version must be a string"
        )

    normalized_id = (
        coordinator_id.strip()
    )

    normalized_version = (
        coordinator_version.strip()
    )

    if not normalized_id:
        raise CoordinatorRegistryError(
            "coordinator_id must be non-empty"
        )

    if not normalized_version:
        raise CoordinatorRegistryError(
            "coordinator_version must be non-empty"
        )

    return (
        normalized_id,
        normalized_version,
    )


# ============================================================================
# 4. Immutable snapshot helpers
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


# ============================================================================
# 5. Registry state
# ============================================================================

_REGISTRY_LOCK: Final[
    RLock
] = RLock()

_COORDINATOR_REGISTRY: dict[
    CoordinatorRegistryKey,
    PipelineCoordinatorContract,
] = {}


# ============================================================================
# 6. Registration
# ============================================================================

def register_coordinator(
    coordinator: PipelineCoordinatorContract,
) -> PipelineCoordinatorContract:
    """
    Register one exact PipelineCoordinatorContract.

    Duplicate coordinator_id + coordinator_version identities are rejected.

    There is deliberately no ``replace`` option in Phase 2.2.
    Replacement/version-governance belongs to Phase 2.4.
    """

    if not isinstance(
        coordinator,
        PipelineCoordinatorContract,
    ):
        raise CoordinatorRegistryError(
            "coordinator must be a PipelineCoordinatorContract"
        )

    if (
        coordinator.contract_version
        != PIPELINE_COORDINATOR_CONTRACT_VERSION
    ):
        raise CoordinatorRegistryError(
            "coordinator contract_version must be "
            + PIPELINE_COORDINATOR_CONTRACT_VERSION
        )

    key = coordinator_registry_key(
        coordinator_id=(
            coordinator.coordinator_id
        ),
        coordinator_version=(
            coordinator.coordinator_version
        ),
    )

    with _REGISTRY_LOCK:

        if key in _COORDINATOR_REGISTRY:

            raise CoordinatorAlreadyRegisteredError(
                "coordinator is already registered: "
                f"{coordinator.coordinator_id}@"
                f"{coordinator.coordinator_version}"
            )

        _COORDINATOR_REGISTRY[
            key
        ] = coordinator

    return coordinator


# ============================================================================
# 7. Exact lookup
# ============================================================================

def get_registered_coordinator(
    *,
    coordinator_id: str,
    coordinator_version: str,
) -> Optional[
    PipelineCoordinatorContract
]:
    """
    Return one exact coordinator version or None.

    No latest/default version resolution occurs in Phase 2.2.
    """

    key = coordinator_registry_key(
        coordinator_id=coordinator_id,
        coordinator_version=coordinator_version,
    )

    with _REGISTRY_LOCK:

        return _COORDINATOR_REGISTRY.get(
            key
        )


def require_registered_coordinator(
    *,
    coordinator_id: str,
    coordinator_version: str,
) -> PipelineCoordinatorContract:
    """
    Return one exact registered coordinator or raise.
    """

    coordinator = (
        get_registered_coordinator(
            coordinator_id=coordinator_id,
            coordinator_version=coordinator_version,
        )
    )

    if coordinator is None:

        raise CoordinatorNotRegisteredError(
            "coordinator is not registered: "
            f"{coordinator_id}@"
            f"{coordinator_version}"
        )

    return coordinator


def is_coordinator_registered(
    *,
    coordinator_id: str,
    coordinator_version: str,
) -> bool:

    return (
        get_registered_coordinator(
            coordinator_id=coordinator_id,
            coordinator_version=coordinator_version,
        )
        is not None
    )


# ============================================================================
# 8. Inspection
# ============================================================================

def registered_coordinator_count(
) -> int:

    with _REGISTRY_LOCK:

        return len(
            _COORDINATOR_REGISTRY
        )


def list_registered_coordinators(
) -> Tuple[
    PipelineCoordinatorContract,
    ...
]:
    """
    Return all coordinator contracts in deterministic identity order.
    """

    with _REGISTRY_LOCK:

        coordinators = tuple(
            _COORDINATOR_REGISTRY.values()
        )

    return tuple(
        sorted(
            coordinators,
            key=lambda item: (
                item.coordinator_id,
                item.coordinator_version,
            ),
        )
    )


def list_coordinators_for_workflow(
    *,
    workflow_type: str,
    workflow_version: str,
) -> Tuple[
    PipelineCoordinatorContract,
    ...
]:
    """
    Inspection query for coordinators declaring one exact workflow identity.

    This does NOT choose, activate, validate, or resolve an execution
    coordinator. Those authorities belong to later phases.
    """

    if not isinstance(
        workflow_type,
        str,
    ):
        raise CoordinatorRegistryError(
            "workflow_type must be a string"
        )

    if not isinstance(
        workflow_version,
        str,
    ):
        raise CoordinatorRegistryError(
            "workflow_version must be a string"
        )

    workflow_type = (
        workflow_type.strip()
    )

    workflow_version = (
        workflow_version.strip()
    )

    if not workflow_type:
        raise CoordinatorRegistryError(
            "workflow_type must be non-empty"
        )

    if not workflow_version:
        raise CoordinatorRegistryError(
            "workflow_version must be non-empty"
        )

    coordinators = (
        list_registered_coordinators()
    )

    return tuple(
        coordinator
        for coordinator
        in coordinators
        if (
            coordinator.workflow_type
            == workflow_type
            and coordinator.workflow_version
            == workflow_version
        )
    )


# ============================================================================
# 9. Snapshot
# ============================================================================

def coordinator_registry_snapshot(
) -> Mapping[
    str,
    Any,
]:
    """
    Immutable inspection snapshot.

    Snapshot generation is not persistence.
    """

    coordinators = (
        list_registered_coordinators()
    )

    snapshot = {
        "registry_version":
            COORDINATOR_REGISTRY_VERSION,

        "schema_version":
            COORDINATOR_REGISTRY_SCHEMA_VERSION,

        "pipeline_coordinator_contract_version":
            PIPELINE_COORDINATOR_CONTRACT_VERSION,

        "identity_fields": (
            "coordinator_id",
            "coordinator_version",
        ),

        "count":
            len(coordinators),

        "coordinators":
            tuple(
                _freeze(
                    coordinator.to_dict()
                )
                for coordinator
                in coordinators
            ),

        "persistence":
            False,

        "exact_version_lookup_only":
            True,

        "cross_registry_validation":
            False,

        "version_selection":
            False,
    }

    return _freeze(
        snapshot
    )


# ============================================================================
# 10. Architecture declaration
# ============================================================================

def explain_coordinator_registry_v2_2(
) -> Mapping[
    str,
    Any,
]:

    return _freeze(
        {
            "phase":
                "2.2",

            "component":
                "Coordinator Registration",

            "version":
                COORDINATOR_REGISTRY_VERSION,

            "registered_object":
                "PipelineCoordinatorContract",

            "canonical_identity": (
                "coordinator_id",
                "coordinator_version",
            ),

            "owns": (
                "coordinator existence declaration",
                "exact-version coordinator registration",
                "exact-version coordinator lookup",
                "duplicate coordinator identity rejection",
                "deterministic coordinator inspection",
                "workflow-identity inspection",
            ),

            "does_not_own": (
                "workflow existence validation",
                "workflow/coordinator cross-registration validation",
                "coordinator selection for execution",
                "latest coordinator selection",
                "default coordinator selection",
                "coordinator activation",
                "coordinator deactivation",
                "stage ordering",
                "dependency planning",
                "Runtime Registration",
                "runtime handler resolution",
                "runtime job creation",
                "coordinator invocation",
                "workflow execution",
                "workflow lifecycle state",
                "workflow execution state",
                "persistence",
                "migration",
                "version governance",
            ),

            "future_authority": {
                "2.3":
                    "Registration Validation",

                "2.4":
                    "Version Management",
            },
        }
    )


__all__ = [
    "COORDINATOR_REGISTRY_VERSION",
    "COORDINATOR_REGISTRY_SCHEMA_VERSION",
    "CoordinatorRegistryKey",
    "CoordinatorRegistryError",
    "CoordinatorAlreadyRegisteredError",
    "CoordinatorNotRegisteredError",
    "coordinator_registry_key",
    "register_coordinator",
    "get_registered_coordinator",
    "require_registered_coordinator",
    "is_coordinator_registered",
    "registered_coordinator_count",
    "list_registered_coordinators",
    "list_coordinators_for_workflow",
    "coordinator_registry_snapshot",
    "explain_coordinator_registry_v2_2",
]
