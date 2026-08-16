"""
LinkCraftor Universal Coordination Framework
Phase 2.4 - Version Management
============================================

Explicit, in-memory version preference policy for registered workflows
and registered coordinators.

Canonical policy maps
---------------------

1. workflow_type
       -> preferred workflow_version

2. coordinator_id
       -> preferred coordinator_version

3. workflow_type + workflow_version
       -> preferred coordinator_id + coordinator_version

All selections are explicit.

This component does NOT infer "latest", parse semantic versions, modify
registries, execute coordinators, create Runtime jobs, persist preferences,
or manage coordinator lifecycle/deprecation.
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

from backend.server.coordination.workflow_registry.registry import (
    WORKFLOW_REGISTRY_VERSION,
    WorkflowRegistryEntry,
    get_registered_workflow,
)

from backend.server.coordination.coordinator_registry.registry import (
    COORDINATOR_REGISTRY_VERSION,
    get_registered_coordinator,
)

from backend.server.coordination.pipeline_coordinators.contract import (
    PipelineCoordinatorContract,
)

from backend.server.coordination.registration_validation.validator import (
    REGISTRATION_VALIDATION_VERSION,
    validate_coordinator_registration,
)


# ============================================================================
# 1. Component identity
# ============================================================================

VERSION_MANAGEMENT_VERSION: Final[str] = (
    "version_management_v2.4.0"
)

VERSION_MANAGEMENT_SCHEMA_VERSION: Final[str] = (
    "version_management_schema_v1"
)


# ============================================================================
# 2. Errors
# ============================================================================

class VersionManagementError(
    ValueError
):
    """Base Version Management error."""


class VersionPreferenceNotFoundError(
    VersionManagementError
):
    """Raised when an explicit preference has not been declared."""


class InvalidVersionPreferenceError(
    VersionManagementError
):
    """Raised when a requested preference is not valid."""


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


def _required_string(
    value: Any,
    *,
    field_name: str,
) -> str:

    if not isinstance(
        value,
        str,
    ):

        raise VersionManagementError(
            f"{field_name} must be a string"
        )

    normalized = value.strip()

    if not normalized:

        raise VersionManagementError(
            f"{field_name} must be non-empty"
        )

    return normalized


# ============================================================================
# 4. Preference state
# ============================================================================

_VERSION_LOCK: Final[
    RLock
] = RLock()


# workflow_type -> workflow_version
_WORKFLOW_VERSION_PREFERENCES: dict[
    str,
    str,
] = {}


# coordinator_id -> coordinator_version
_COORDINATOR_VERSION_PREFERENCES: dict[
    str,
    str,
] = {}


# (workflow_type, workflow_version)
#     -> (coordinator_id, coordinator_version)
_WORKFLOW_COORDINATOR_PREFERENCES: dict[
    Tuple[str, str],
    Tuple[str, str],
] = {}


# ============================================================================
# 5. Workflow version preference
# ============================================================================

def set_preferred_workflow_version(
    *,
    workflow_type: str,
    workflow_version: str,
) -> WorkflowRegistryEntry:
    """
    Explicitly prefer one exact registered workflow version.

    No automatic latest-version inference is performed.
    """

    workflow_type = _required_string(
        workflow_type,
        field_name="workflow_type",
    )

    workflow_version = _required_string(
        workflow_version,
        field_name="workflow_version",
    )

    workflow = get_registered_workflow(
        workflow_type=workflow_type,
        workflow_version=workflow_version,
    )

    if workflow is None:

        raise InvalidVersionPreferenceError(
            "preferred workflow version is not registered: "
            f"{workflow_type}@{workflow_version}"
        )

    with _VERSION_LOCK:

        _WORKFLOW_VERSION_PREFERENCES[
            workflow_type
        ] = workflow_version

    return workflow


def get_preferred_workflow_version(
    *,
    workflow_type: str,
) -> Optional[str]:

    workflow_type = _required_string(
        workflow_type,
        field_name="workflow_type",
    )

    with _VERSION_LOCK:

        return (
            _WORKFLOW_VERSION_PREFERENCES.get(
                workflow_type
            )
        )


def resolve_preferred_workflow(
    *,
    workflow_type: str,
) -> Optional[
    WorkflowRegistryEntry
]:

    workflow_type = _required_string(
        workflow_type,
        field_name="workflow_type",
    )

    version = get_preferred_workflow_version(
        workflow_type=workflow_type
    )

    if version is None:
        return None

    workflow = get_registered_workflow(
        workflow_type=workflow_type,
        workflow_version=version,
    )

    if workflow is None:

        raise VersionManagementError(
            "preferred workflow version no longer "
            "resolves in Workflow Registry"
        )

    return workflow


def require_preferred_workflow(
    *,
    workflow_type: str,
) -> WorkflowRegistryEntry:

    workflow = resolve_preferred_workflow(
        workflow_type=workflow_type
    )

    if workflow is None:

        raise VersionPreferenceNotFoundError(
            "no preferred workflow version declared: "
            f"{workflow_type}"
        )

    return workflow


# ============================================================================
# 6. Coordinator version preference
# ============================================================================

def set_preferred_coordinator_version(
    *,
    coordinator_id: str,
    coordinator_version: str,
) -> PipelineCoordinatorContract:
    """
    Explicitly prefer one exact registered coordinator version.

    The selected coordinator must also pass Phase 2.3 Registration Validation.
    """

    coordinator_id = _required_string(
        coordinator_id,
        field_name="coordinator_id",
    )

    coordinator_version = _required_string(
        coordinator_version,
        field_name="coordinator_version",
    )

    coordinator = get_registered_coordinator(
        coordinator_id=coordinator_id,
        coordinator_version=coordinator_version,
    )

    if coordinator is None:

        raise InvalidVersionPreferenceError(
            "preferred coordinator version is not registered: "
            f"{coordinator_id}@{coordinator_version}"
        )

    validation = (
        validate_coordinator_registration(
            coordinator
        )
    )

    if not validation.is_valid:

        raise InvalidVersionPreferenceError(
            "preferred coordinator registration "
            "failed Phase 2.3 validation: "
            f"{coordinator_id}@{coordinator_version}"
        )

    with _VERSION_LOCK:

        _COORDINATOR_VERSION_PREFERENCES[
            coordinator_id
        ] = coordinator_version

    return coordinator


def get_preferred_coordinator_version(
    *,
    coordinator_id: str,
) -> Optional[str]:

    coordinator_id = _required_string(
        coordinator_id,
        field_name="coordinator_id",
    )

    with _VERSION_LOCK:

        return (
            _COORDINATOR_VERSION_PREFERENCES.get(
                coordinator_id
            )
        )


def resolve_preferred_coordinator(
    *,
    coordinator_id: str,
) -> Optional[
    PipelineCoordinatorContract
]:

    coordinator_id = _required_string(
        coordinator_id,
        field_name="coordinator_id",
    )

    version = (
        get_preferred_coordinator_version(
            coordinator_id=coordinator_id
        )
    )

    if version is None:
        return None

    coordinator = get_registered_coordinator(
        coordinator_id=coordinator_id,
        coordinator_version=version,
    )

    if coordinator is None:

        raise VersionManagementError(
            "preferred coordinator version no longer "
            "resolves in Coordinator Registry"
        )

    validation = (
        validate_coordinator_registration(
            coordinator
        )
    )

    if not validation.is_valid:

        raise VersionManagementError(
            "preferred coordinator no longer passes "
            "Phase 2.3 Registration Validation"
        )

    return coordinator


def require_preferred_coordinator(
    *,
    coordinator_id: str,
) -> PipelineCoordinatorContract:

    coordinator = (
        resolve_preferred_coordinator(
            coordinator_id=coordinator_id
        )
    )

    if coordinator is None:

        raise VersionPreferenceNotFoundError(
            "no preferred coordinator version declared: "
            f"{coordinator_id}"
        )

    return coordinator


# ============================================================================
# 7. Workflow-bound coordinator preference
# ============================================================================

def set_preferred_workflow_coordinator(
    *,
    workflow_type: str,
    workflow_version: str,
    coordinator_id: str,
    coordinator_version: str,
) -> PipelineCoordinatorContract:
    """
    Select one exact validated coordinator for one exact workflow identity.

    This is declaration/selection only.
    It does not invoke the coordinator.
    """

    workflow_type = _required_string(
        workflow_type,
        field_name="workflow_type",
    )

    workflow_version = _required_string(
        workflow_version,
        field_name="workflow_version",
    )

    coordinator_id = _required_string(
        coordinator_id,
        field_name="coordinator_id",
    )

    coordinator_version = _required_string(
        coordinator_version,
        field_name="coordinator_version",
    )

    workflow = get_registered_workflow(
        workflow_type=workflow_type,
        workflow_version=workflow_version,
    )

    if workflow is None:

        raise InvalidVersionPreferenceError(
            "workflow-bound coordinator preference "
            "references an unregistered workflow: "
            f"{workflow_type}@{workflow_version}"
        )

    coordinator = get_registered_coordinator(
        coordinator_id=coordinator_id,
        coordinator_version=coordinator_version,
    )

    if coordinator is None:

        raise InvalidVersionPreferenceError(
            "workflow-bound coordinator preference "
            "references an unregistered coordinator: "
            f"{coordinator_id}@{coordinator_version}"
        )

    if (
        coordinator.workflow_type
        != workflow_type
        or coordinator.workflow_version
        != workflow_version
    ):

        raise InvalidVersionPreferenceError(
            "coordinator does not declare the exact "
            "workflow identity being selected"
        )

    validation = (
        validate_coordinator_registration(
            coordinator
        )
    )

    if not validation.is_valid:

        raise InvalidVersionPreferenceError(
            "workflow-bound preferred coordinator "
            "failed Phase 2.3 Registration Validation"
        )

    key = (
        workflow_type,
        workflow_version,
    )

    value = (
        coordinator_id,
        coordinator_version,
    )

    with _VERSION_LOCK:

        _WORKFLOW_COORDINATOR_PREFERENCES[
            key
        ] = value

    return coordinator


def get_preferred_workflow_coordinator_identity(
    *,
    workflow_type: str,
    workflow_version: str,
) -> Optional[
    Tuple[str, str]
]:

    workflow_type = _required_string(
        workflow_type,
        field_name="workflow_type",
    )

    workflow_version = _required_string(
        workflow_version,
        field_name="workflow_version",
    )

    key = (
        workflow_type,
        workflow_version,
    )

    with _VERSION_LOCK:

        return (
            _WORKFLOW_COORDINATOR_PREFERENCES.get(
                key
            )
        )


def resolve_preferred_workflow_coordinator(
    *,
    workflow_type: str,
    workflow_version: str,
) -> Optional[
    PipelineCoordinatorContract
]:

    identity = (
        get_preferred_workflow_coordinator_identity(
            workflow_type=workflow_type,
            workflow_version=workflow_version,
        )
    )

    if identity is None:
        return None

    coordinator_id, coordinator_version = (
        identity
    )

    coordinator = get_registered_coordinator(
        coordinator_id=coordinator_id,
        coordinator_version=coordinator_version,
    )

    if coordinator is None:

        raise VersionManagementError(
            "preferred workflow coordinator no longer "
            "resolves in Coordinator Registry"
        )

    if (
        coordinator.workflow_type
        != workflow_type
        or coordinator.workflow_version
        != workflow_version
    ):

        raise VersionManagementError(
            "preferred workflow coordinator no longer "
            "declares the expected workflow identity"
        )

    validation = (
        validate_coordinator_registration(
            coordinator
        )
    )

    if not validation.is_valid:

        raise VersionManagementError(
            "preferred workflow coordinator no longer "
            "passes Phase 2.3 Registration Validation"
        )

    return coordinator


def require_preferred_workflow_coordinator(
    *,
    workflow_type: str,
    workflow_version: str,
) -> PipelineCoordinatorContract:

    coordinator = (
        resolve_preferred_workflow_coordinator(
            workflow_type=workflow_type,
            workflow_version=workflow_version,
        )
    )

    if coordinator is None:

        raise VersionPreferenceNotFoundError(
            "no preferred coordinator declared for workflow: "
            f"{workflow_type}@{workflow_version}"
        )

    return coordinator


# ============================================================================
# 8. Inspection
# ============================================================================

def version_management_snapshot(
) -> Mapping[
    str,
    Any,
]:
    """
    Return immutable deterministic preference evidence.

    This snapshot is not persistence.
    """

    with _VERSION_LOCK:

        workflow_preferences = tuple(
            sorted(
                _WORKFLOW_VERSION_PREFERENCES.items()
            )
        )

        coordinator_preferences = tuple(
            sorted(
                _COORDINATOR_VERSION_PREFERENCES.items()
            )
        )

        workflow_coordinator_preferences = tuple(
            sorted(
                (
                    (
                        workflow_type,
                        workflow_version,
                        coordinator_id,
                        coordinator_version,
                    )
                    for (
                        (
                            workflow_type,
                            workflow_version,
                        ),
                        (
                            coordinator_id,
                            coordinator_version,
                        ),
                    )
                    in _WORKFLOW_COORDINATOR_PREFERENCES.items()
                )
            )
        )

    return _freeze(
        {
            "version_management_version":
                VERSION_MANAGEMENT_VERSION,

            "schema_version":
                VERSION_MANAGEMENT_SCHEMA_VERSION,

            "workflow_registry_version":
                WORKFLOW_REGISTRY_VERSION,

            "coordinator_registry_version":
                COORDINATOR_REGISTRY_VERSION,

            "registration_validation_version":
                REGISTRATION_VALIDATION_VERSION,

            "workflow_preferences":
                workflow_preferences,

            "coordinator_preferences":
                coordinator_preferences,

            "workflow_coordinator_preferences":
                workflow_coordinator_preferences,

            "workflow_preference_count":
                len(
                    workflow_preferences
                ),

            "coordinator_preference_count":
                len(
                    coordinator_preferences
                ),

            "workflow_coordinator_preference_count":
                len(
                    workflow_coordinator_preferences
                ),

            "automatic_latest_inference":
                False,

            "semantic_version_ordering":
                False,

            "registry_mutation":
                False,

            "execution":
                False,

            "persistence":
                False,
        }
    )


# ============================================================================
# 9. Architecture declaration
# ============================================================================

def explain_version_management_v2_4(
) -> Mapping[
    str,
    Any,
]:

    return _freeze(
        {
            "phase":
                "2.4",

            "component":
                "Version Management",

            "version":
                VERSION_MANAGEMENT_VERSION,

            "selection_policy":
                "explicit_exact_preference",

            "workflow_preference_identity":
                "workflow_type",

            "coordinator_preference_identity":
                "coordinator_id",

            "workflow_coordinator_preference_identity":
                (
                    "workflow_type",
                    "workflow_version",
                ),

            "owns": (
                "explicit workflow version preference",
                "explicit coordinator version preference",
                "explicit workflow-bound coordinator preference",
                "exact preferred-version resolution",
                "preference validation against frozen registries",
                "preferred coordinator validation through Phase 2.3",
                "deterministic preference inspection",
                "immutable version-management snapshot",
            ),

            "does_not_own": (
                "workflow registration",
                "coordinator registration",
                "registration validation rules",
                "automatic latest inference",
                "semantic version parsing",
                "registry replacement",
                "registry deletion",
                "coordinator execution",
                "workflow execution",
                "Runtime Registration",
                "runtime job creation",
                "stage ordering",
                "dependency planning",
                "workflow lifecycle transitions",
                "persistence",
                "coordinator lifecycle",
                "coordinator deprecation",
                "migration execution",
            ),

            "future_authority": {
                "8.0":
                    "Workflow State Persistence",

                "11.5":
                    "Coordinator Lifecycle",
            },
        }
    )


__all__ = [
    "VERSION_MANAGEMENT_VERSION",
    "VERSION_MANAGEMENT_SCHEMA_VERSION",
    "VersionManagementError",
    "VersionPreferenceNotFoundError",
    "InvalidVersionPreferenceError",
    "set_preferred_workflow_version",
    "get_preferred_workflow_version",
    "resolve_preferred_workflow",
    "require_preferred_workflow",
    "set_preferred_coordinator_version",
    "get_preferred_coordinator_version",
    "resolve_preferred_coordinator",
    "require_preferred_coordinator",
    "set_preferred_workflow_coordinator",
    "get_preferred_workflow_coordinator_identity",
    "resolve_preferred_workflow_coordinator",
    "require_preferred_workflow_coordinator",
    "version_management_snapshot",
    "explain_version_management_v2_4",
]
