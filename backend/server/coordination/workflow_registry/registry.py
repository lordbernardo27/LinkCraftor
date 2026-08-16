"""
LinkCraftor Universal Coordination Framework
Phase 2.1 - Workflow Registry
============================================

Canonical in-memory registry of known workflow definitions.

Registry identity
-----------------
A workflow is uniquely identified by:

    workflow_type + workflow_version

Authority boundaries
--------------------
The Workflow Registry owns:
- declaration that a workflow type/version exists;
- exact workflow-version lookup;
- duplicate identity rejection;
- immutable workflow registry entries;
- registry inspection/snapshot operations.

The Workflow Registry does NOT own:
- coordinator registration;
- coordinator resolution;
- stage ordering;
- dependency graphs;
- runnable-stage selection;
- execution planning;
- Runtime Registration;
- runtime handlers;
- runtime job creation;
- workflow lifecycle state;
- workflow execution state;
- persistence;
- version preference / latest-version selection;
- workflow migration.

Those responsibilities belong to later Universal Coordination
Framework phases.
"""

from __future__ import annotations

import hashlib
import json
import re

from dataclasses import (
    dataclass,
    field,
)

from threading import RLock

from types import MappingProxyType

from typing import (
    Any,
    Final,
    Mapping,
    Optional,
    Tuple,
)

from backend.server.coordination.universal_workflows.contract import (
    UNIVERSAL_WORKFLOW_CONTRACT_VERSION,
)


# ============================================================================
# 1. Registry identity
# ============================================================================

WORKFLOW_REGISTRY_VERSION: Final[str] = (
    "workflow_registry_v2.1.0"
)

WORKFLOW_REGISTRY_ENTRY_SCHEMA_VERSION: Final[str] = (
    "workflow_registry_entry_schema_v1"
)


# ============================================================================
# 2. Validation
# ============================================================================

_NAME_PATTERN: Final[
    re.Pattern[str]
] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$"
)


class WorkflowRegistryError(
    ValueError
):
    """Base error for Workflow Registry failures."""


class WorkflowAlreadyRegisteredError(
    WorkflowRegistryError
):
    """Raised when an exact workflow identity already exists."""


class WorkflowNotRegisteredError(
    WorkflowRegistryError
):
    """Raised when an exact workflow identity cannot be resolved."""


def _normalize_name(
    value: Any,
    *,
    field_name: str,
) -> str:

    if not isinstance(
        value,
        str,
    ):
        raise WorkflowRegistryError(
            f"{field_name} must be a string"
        )

    normalized = (
        value.strip()
    )

    if not normalized:
        raise WorkflowRegistryError(
            f"{field_name} must be non-empty"
        )

    if not _NAME_PATTERN.fullmatch(
        normalized
    ):
        raise WorkflowRegistryError(
            f"{field_name} contains unsupported characters"
        )

    return normalized


def _normalize_description(
    value: Any,
) -> str:

    if not isinstance(
        value,
        str,
    ):
        raise WorkflowRegistryError(
            "description must be a string"
        )

    return (
        value.strip()
    )


# ============================================================================
# 3. Immutable metadata
# ============================================================================

_EMPTY_MAPPING: Final[
    Mapping[str, Any]
] = MappingProxyType({})


def _freeze(
    value: Any,
) -> Any:

    if isinstance(
        value,
        Mapping,
    ):

        return MappingProxyType(
            {
                str(key): _freeze(
                    item
                )
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


def _thaw(
    value: Any,
) -> Any:

    if isinstance(
        value,
        Mapping,
    ):

        return {
            str(key): _thaw(
                item
            )
            for key, item
            in value.items()
        }

    if isinstance(
        value,
        tuple,
    ):

        return [
            _thaw(item)
            for item in value
        ]

    return value


def _normalize_metadata(
    value: Any,
) -> Mapping[str, Any]:

    if value is None:
        return _EMPTY_MAPPING

    if not isinstance(
        value,
        Mapping,
    ):
        raise WorkflowRegistryError(
            "metadata must be a mapping"
        )

    return _freeze(
        value
    )


# ============================================================================
# 4. Canonical registry key
# ============================================================================

WorkflowRegistryKey = Tuple[
    str,
    str,
]


def workflow_registry_key(
    *,
    workflow_type: str,
    workflow_version: str,
) -> WorkflowRegistryKey:
    """
    Build the canonical exact-version registry key.
    """

    return (
        _normalize_name(
            workflow_type,
            field_name="workflow_type",
        ),
        _normalize_name(
            workflow_version,
            field_name="workflow_version",
        ),
    )


# ============================================================================
# 5. Registry entry
# ============================================================================

@dataclass(
    frozen=True,
    slots=True,
)
class WorkflowRegistryEntry:
    """
    Immutable declaration that one workflow type/version exists.

    This entry intentionally contains no coordinator identity and
    no stage/dependency definition. Those authorities belong to
    later UCF phases.
    """

    workflow_type: str
    workflow_version: str

    workflow_contract_version: str

    description: str = ""

    metadata: Mapping[
        str,
        Any,
    ] = field(
        default_factory=dict
    )


    def __post_init__(
        self,
    ) -> None:

        workflow_type = _normalize_name(
            self.workflow_type,
            field_name="workflow_type",
        )

        workflow_version = _normalize_name(
            self.workflow_version,
            field_name="workflow_version",
        )

        workflow_contract_version = (
            _normalize_name(
                self.workflow_contract_version,
                field_name="workflow_contract_version",
            )
        )

        if (
            workflow_contract_version
            != UNIVERSAL_WORKFLOW_CONTRACT_VERSION
        ):

            raise WorkflowRegistryError(
                "workflow_contract_version must be "
                + UNIVERSAL_WORKFLOW_CONTRACT_VERSION
            )

        description = (
            _normalize_description(
                self.description
            )
        )

        metadata = (
            _normalize_metadata(
                self.metadata
            )
        )

        object.__setattr__(
            self,
            "workflow_type",
            workflow_type,
        )

        object.__setattr__(
            self,
            "workflow_version",
            workflow_version,
        )

        object.__setattr__(
            self,
            "workflow_contract_version",
            workflow_contract_version,
        )

        object.__setattr__(
            self,
            "description",
            description,
        )

        object.__setattr__(
            self,
            "metadata",
            metadata,
        )


    @property
    def key(
        self,
    ) -> WorkflowRegistryKey:

        return (
            self.workflow_type,
            self.workflow_version,
        )


    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "workflow_type":
                self.workflow_type,

            "workflow_version":
                self.workflow_version,

            "workflow_contract_version":
                self.workflow_contract_version,

            "description":
                self.description,

            "metadata":
                _thaw(
                    self.metadata
                ),
        }


    def canonical_json(
        self,
    ) -> str:

        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
            ensure_ascii=False,
        )


    def identity_fingerprint(
        self,
    ) -> str:

        material = json.dumps(
            {
                "workflow_type":
                    self.workflow_type,

                "workflow_version":
                    self.workflow_version,
            },
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
        )

        return hashlib.sha256(
            material.encode(
                "utf-8"
            )
        ).hexdigest()


    def content_fingerprint(
        self,
    ) -> str:

        return hashlib.sha256(
            self.canonical_json().encode(
                "utf-8"
            )
        ).hexdigest()


# ============================================================================
# 6. Registry state
# ============================================================================

_REGISTRY_LOCK: Final[
    RLock
] = RLock()

_WORKFLOW_REGISTRY: dict[
    WorkflowRegistryKey,
    WorkflowRegistryEntry,
] = {}


# ============================================================================
# 7. Registration
# ============================================================================

def register_workflow(
    entry: WorkflowRegistryEntry,
) -> WorkflowRegistryEntry:
    """
    Register one exact workflow identity.

    Duplicate workflow_type + workflow_version identities are rejected.

    There is intentionally no ``replace`` option in Phase 2.1.
    Replacement and version-governance rules belong to Phase 2.4.
    """

    if not isinstance(
        entry,
        WorkflowRegistryEntry,
    ):
        raise WorkflowRegistryError(
            "entry must be a WorkflowRegistryEntry"
        )

    key = entry.key

    with _REGISTRY_LOCK:

        if key in _WORKFLOW_REGISTRY:

            raise WorkflowAlreadyRegisteredError(
                "workflow is already registered: "
                f"{entry.workflow_type}@"
                f"{entry.workflow_version}"
            )

        _WORKFLOW_REGISTRY[
            key
        ] = entry

    return entry


def register_workflow_definition(
    *,
    workflow_type: str,
    workflow_version: str,
    workflow_contract_version: str = (
        UNIVERSAL_WORKFLOW_CONTRACT_VERSION
    ),
    description: str = "",
    metadata: Optional[
        Mapping[str, Any]
    ] = None,
) -> WorkflowRegistryEntry:
    """
    Convenience constructor + registration operation.
    """

    entry = WorkflowRegistryEntry(
        workflow_type=workflow_type,
        workflow_version=workflow_version,
        workflow_contract_version=(
            workflow_contract_version
        ),
        description=description,
        metadata=(
            metadata
            if metadata is not None
            else {}
        ),
    )

    return register_workflow(
        entry
    )


# ============================================================================
# 8. Exact lookup
# ============================================================================

def get_registered_workflow(
    *,
    workflow_type: str,
    workflow_version: str,
) -> Optional[
    WorkflowRegistryEntry
]:
    """
    Return an exact workflow version, or None.

    Phase 2.1 performs no latest/default-version resolution.
    """

    key = workflow_registry_key(
        workflow_type=workflow_type,
        workflow_version=workflow_version,
    )

    with _REGISTRY_LOCK:

        return _WORKFLOW_REGISTRY.get(
            key
        )


def require_registered_workflow(
    *,
    workflow_type: str,
    workflow_version: str,
) -> WorkflowRegistryEntry:
    """
    Resolve an exact workflow version or raise.
    """

    entry = get_registered_workflow(
        workflow_type=workflow_type,
        workflow_version=workflow_version,
    )

    if entry is None:

        raise WorkflowNotRegisteredError(
            "workflow is not registered: "
            f"{workflow_type}@"
            f"{workflow_version}"
        )

    return entry


def is_workflow_registered(
    *,
    workflow_type: str,
    workflow_version: str,
) -> bool:

    return (
        get_registered_workflow(
            workflow_type=workflow_type,
            workflow_version=workflow_version,
        )
        is not None
    )


# ============================================================================
# 9. Inspection
# ============================================================================

def registered_workflow_count(
) -> int:

    with _REGISTRY_LOCK:

        return len(
            _WORKFLOW_REGISTRY
        )


def list_registered_workflows(
) -> Tuple[
    WorkflowRegistryEntry,
    ...
]:
    """
    Return all entries in deterministic identity order.
    """

    with _REGISTRY_LOCK:

        entries = tuple(
            _WORKFLOW_REGISTRY.values()
        )

    return tuple(
        sorted(
            entries,
            key=lambda entry: (
                entry.workflow_type,
                entry.workflow_version,
            ),
        )
    )


def workflow_registry_snapshot(
) -> Mapping[
    str,
    Any,
]:
    """
    Return an immutable inspection snapshot.

    The snapshot is evidence/inspection only and is not persistence.
    """

    entries = (
        list_registered_workflows()
    )

    snapshot = {
        "registry_version":
            WORKFLOW_REGISTRY_VERSION,

        "entry_schema_version":
            WORKFLOW_REGISTRY_ENTRY_SCHEMA_VERSION,

        "workflow_contract_version":
            UNIVERSAL_WORKFLOW_CONTRACT_VERSION,

        "identity_fields": (
            "workflow_type",
            "workflow_version",
        ),

        "count":
            len(entries),

        "entries":
            tuple(
                _freeze(
                    entry.to_dict()
                )
                for entry
                in entries
            ),

        "persistence":
            False,

        "exact_version_lookup_only":
            True,
    }

    return _freeze(
        snapshot
    )


# ============================================================================
# 10. Architecture explanation
# ============================================================================

def explain_workflow_registry_v2_1(
) -> Mapping[str, Any]:

    return _freeze(
        {
            "phase":
                "2.1",

            "component":
                "Workflow Registry",

            "version":
                WORKFLOW_REGISTRY_VERSION,

            "canonical_identity": (
                "workflow_type",
                "workflow_version",
            ),

            "owns": (
                "workflow existence declaration",
                "exact-version registration",
                "exact-version lookup",
                "duplicate identity rejection",
                "immutable registry entries",
                "registry inspection",
            ),

            "does_not_own": (
                "coordinator registration",
                "coordinator resolution",
                "stage ordering",
                "dependency graphs",
                "runnable-stage selection",
                "execution planning",
                "Runtime Registration",
                "runtime handlers",
                "runtime job creation",
                "workflow lifecycle state",
                "workflow execution state",
                "persistence",
                "latest-version selection",
                "workflow migration",
            ),
        }
    )


__all__ = [
    "WORKFLOW_REGISTRY_VERSION",
    "WORKFLOW_REGISTRY_ENTRY_SCHEMA_VERSION",
    "WorkflowRegistryKey",
    "WorkflowRegistryEntry",
    "WorkflowRegistryError",
    "WorkflowAlreadyRegisteredError",
    "WorkflowNotRegisteredError",
    "workflow_registry_key",
    "register_workflow",
    "register_workflow_definition",
    "get_registered_workflow",
    "require_registered_workflow",
    "is_workflow_registered",
    "registered_workflow_count",
    "list_registered_workflows",
    "workflow_registry_snapshot",
    "explain_workflow_registry_v2_1",
]
