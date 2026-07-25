# -*- coding: utf-8 -*-
"""Shared vocabulary for the Runtime Schema Management subsystem.

This module is the dependency root of :mod:`runtime_schema`.

It owns shared enums, exceptions, validation constants, canonical timestamp
helpers, namespace rules, and deep immutability primitives. It imports no
other runtime_schema module, which prevents circular dependencies.

The module is business-logic agnostic and contains no product-pipeline logic.
"""

from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Final, Mapping


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class SchemaError(Exception):
    """Base class for every error raised by schema management."""


class SchemaDefinitionError(SchemaError):
    """A schema definition is structurally invalid."""


class SchemaValidationError(SchemaError):
    """A data document violates its schema."""


class SchemaCompatibilityError(SchemaError):
    """A schema change violates a declared compatibility mode."""


class SchemaRegistryError(SchemaError):
    """A registry operation violates registry rules."""


class SchemaMigrationError(SchemaError):
    """A migration plan is invalid or cannot be constructed."""


class SchemaAuditError(SchemaError):
    """The audit chain is corrupt or an audit action is illegal."""


class SchemaSerializationError(SchemaError):
    """A value cannot be canonically serialized or deserialized."""


# ---------------------------------------------------------------------------
# Core enums
# ---------------------------------------------------------------------------


class SchemaLifecycleState(str, Enum):
    """Lifecycle of a registered schema version."""

    DRAFT = "draft"
    REGISTERED = "registered"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEPRECATED = "deprecated"
    RETIRED = "retired"
    QUARANTINED = "quarantined"


class CompatibilityMode(str, Enum):
    """Compatibility guarantee declared by a schema."""

    NONE = "none"
    BACKWARD = "backward"
    FORWARD = "forward"
    FULL = "full"
    BACKWARD_TRANSITIVE = "backward_transitive"
    FORWARD_TRANSITIVE = "forward_transitive"
    FULL_TRANSITIVE = "full_transitive"

    @property
    def is_transitive(self) -> bool:
        return self.value.endswith("_transitive")

    @property
    def base_mode(self) -> "CompatibilityMode":
        if not self.is_transitive:
            return self

        return CompatibilityMode(
            self.value.removesuffix("_transitive")
        )


class ChangeClass(str, Enum):
    """Semantic classification of a schema change."""

    COSMETIC = "cosmetic"
    COMPATIBLE = "compatible"
    ADDITIVE = "additive"
    BREAKING = "breaking"


_CHANGE_SEVERITY: Final[
    Mapping[ChangeClass, int]
] = MappingProxyType(
    {
        ChangeClass.COSMETIC: 0,
        ChangeClass.COMPATIBLE: 1,
        ChangeClass.ADDITIVE: 2,
        ChangeClass.BREAKING: 3,
    }
)


def change_severity(
    change_class: ChangeClass,
) -> int:
    """Return numeric severity for a change class."""
    return _CHANGE_SEVERITY[change_class]


class TransitionDirection(str, Enum):
    """Direction of a version-to-version data transition."""

    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"


class SchemaTransitionType(str, Enum):
    """Broader schema lifecycle or version transition operation."""

    CREATE = "create"
    REGISTER = "register"
    ACTIVATE = "activate"
    SUSPEND = "suspend"
    RESUME = "resume"
    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"
    DEPRECATE = "deprecate"
    RETIRE = "retire"
    QUARANTINE = "quarantine"
    RESTORE = "restore"


class RuntimeScope(str, Enum):
    """Scope at which a schema-management operation applies."""

    GLOBAL = "global"
    RUNTIME = "runtime"
    ORGANIZATION = "organization"
    TENANT = "tenant"
    WORKSPACE = "workspace"


class SchemaIdentityType(str, Enum):
    """Kinds of deterministic identity used by schema management."""

    SCHEMA_ID = "schema_id"
    CONTENT_FINGERPRINT = "content_fingerprint"
    SNAPSHOT_ID = "snapshot_id"
    DIFF_ID = "diff_id"
    MIGRATION_PLAN_ID = "migration_plan_id"
    CERTIFICATE_ID = "certificate_id"


class SchemaActorType(str, Enum):
    """Kinds of actors that may perform schema operations."""

    SYSTEM = "system"
    RUNTIME = "runtime"
    OWNER = "owner"
    OPERATOR = "operator"
    SERVICE = "service"
    SUBSYSTEM = "subsystem"
    WORKER = "worker"
    CERTIFICATION = "certification"
    TENANT = "tenant"


class SchemaManagementCapability(str, Enum):
    """Capabilities exposed by Runtime Schema Management."""

    REGISTRY = "registry"
    DEFINITION = "definition"
    OWNERSHIP = "ownership"
    NAMESPACE = "namespace"
    VERSIONING = "versioning"
    COMPATIBILITY = "compatibility"
    VALIDATION = "validation"
    FINGERPRINTING = "fingerprinting"
    SERIALIZATION = "serialization"
    MIGRATION_PLANNING = "migration_planning"
    TRANSITION_VALIDATION = "transition_validation"
    DEPRECATION = "deprecation"
    SNAPSHOTS = "snapshots"
    CHANGE_DETECTION = "change_detection"
    DIFF = "diff"
    AUDIT = "audit"
    CERTIFICATION = "certification"


class EnforcementLevel(str, Enum):
    """How strictly a policy is enforced."""

    WARN = "warn"
    BLOCK = "block"


class OwnerKind(str, Enum):
    """Kind of principal that can own a schema."""

    RUNTIME = "runtime"
    SERVICE = "service"
    SUBSYSTEM = "subsystem"
    TENANT = "tenant"


class AuditAction(str, Enum):
    """Action recorded in schema audit history."""

    NAMESPACE_REGISTERED = "namespace_registered"
    SCHEMA_REGISTERED = "schema_registered"
    LIFECYCLE_CHANGED = "lifecycle_changed"
    OWNERSHIP_TRANSFERRED = "ownership_transferred"
    SNAPSHOT_TAKEN = "snapshot_taken"
    CERTIFICATION_RUN = "certification_run"


class UnknownFieldPolicy(str, Enum):
    """How validation handles fields absent from the schema."""

    REJECT = "reject"
    IGNORE = "ignore"


# ---------------------------------------------------------------------------
# Canonical limits
# ---------------------------------------------------------------------------


MAX_SCHEMA_NAME_LENGTH: Final[int] = 128
MAX_NAMESPACE_LENGTH: Final[int] = 256
MAX_IDENTIFIER_LENGTH: Final[int] = 256
MAX_DESCRIPTION_LENGTH: Final[int] = 4096
MAX_METADATA_SIZE_BYTES: Final[int] = 65536
MAX_TAG_COUNT: Final[int] = 128


# ---------------------------------------------------------------------------
# Reserved runtime namespaces
# ---------------------------------------------------------------------------


RESERVED_RUNTIME_ROOT: Final[str] = "runtime"
RESERVED_RUNTIME_PREFIX: Final[str] = "runtime."
RESERVED_SCHEMA_NAMESPACE: Final[str] = "runtime.schema"
RESERVED_SCHEMA_REGISTRY_NAMESPACE: Final[str] = (
    "runtime.schema.registry"
)
RESERVED_SCHEMA_CERTIFICATION_NAMESPACE: Final[str] = (
    "runtime.schema.certification"
)


# ---------------------------------------------------------------------------
# Identifier and timestamp formats
# ---------------------------------------------------------------------------


NAMESPACE_RE: Final[re.Pattern[str]] = re.compile(
    r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$"
)

NAME_RE: Final[re.Pattern[str]] = re.compile(
    r"^[a-z][a-z0-9_]{0,127}$"
)

IDENTIFIER_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9._:\-]{1,256}$"
)

TIMESTAMP_RE: Final[re.Pattern[str]] = re.compile(
    r"^\d{4}-\d{2}-\d{2}T"
    r"\d{2}:\d{2}:\d{2}\.\d{6}Z$"
)

_TIMESTAMP_FORMAT: Final[str] = (
    "%Y-%m-%dT%H:%M:%S.%fZ"
)


def utc_now_iso() -> str:
    """Return current UTC time in canonical wire format."""
    return datetime.now(
        timezone.utc
    ).strftime(
        _TIMESTAMP_FORMAT
    )


def is_canonical_timestamp(
    value: object,
) -> bool:
    """Return whether a value is a canonical UTC timestamp."""
    if (
        not isinstance(value, str)
        or TIMESTAMP_RE.fullmatch(value) is None
    ):
        return False

    try:
        datetime.strptime(
            value,
            _TIMESTAMP_FORMAT,
        )
    except ValueError:
        return False

    return True


def parse_canonical_timestamp(
    value: str,
) -> datetime:
    """Parse a canonical timestamp into an aware UTC datetime."""
    if not is_canonical_timestamp(value):
        raise SchemaSerializationError(
            f"not a canonical UTC timestamp: {value!r}"
        )

    return datetime.strptime(
        value,
        _TIMESTAMP_FORMAT,
    ).replace(
        tzinfo=timezone.utc
    )


def is_valid_namespace(
    value: object,
) -> bool:
    """Return whether a value is a valid schema namespace."""
    return (
        isinstance(value, str)
        and len(value) <= MAX_NAMESPACE_LENGTH
        and NAMESPACE_RE.fullmatch(value) is not None
    )


def is_valid_name(
    value: object,
) -> bool:
    """Return whether a value is a valid schema or field name."""
    return (
        isinstance(value, str)
        and len(value) <= MAX_SCHEMA_NAME_LENGTH
        and NAME_RE.fullmatch(value) is not None
    )


def is_valid_identifier(
    value: object,
) -> bool:
    """Return whether a value is a valid safe identifier."""
    return (
        isinstance(value, str)
        and len(value) <= MAX_IDENTIFIER_LENGTH
        and IDENTIFIER_RE.fullmatch(value) is not None
    )


def is_reserved_runtime_namespace(
    value: object,
) -> bool:
    """Return whether a namespace belongs to frozen ``runtime.*``."""
    return (
        isinstance(value, str)
        and (
            value == RESERVED_RUNTIME_ROOT
            or value.startswith(
                RESERVED_RUNTIME_PREFIX
            )
        )
    )


# ---------------------------------------------------------------------------
# Immutability primitives
# ---------------------------------------------------------------------------


_SCALAR_TYPES: Final[
    tuple[type, ...]
] = (
    str,
    int,
    float,
    bool,
    type(None),
)

EMPTY_FROZEN_MAPPING: Final[
    Mapping[str, Any]
] = MappingProxyType({})


def deep_freeze(
    value: Any,
) -> Any:
    """Recursively convert JSON-compatible structures to immutable form."""
    if isinstance(value, Enum):
        return value

    if isinstance(value, _SCALAR_TYPES):
        if (
            isinstance(value, float)
            and not math.isfinite(value)
        ):
            raise SchemaSerializationError(
                "non-finite float values are not permitted"
            )

        return value

    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}

        for key, item in value.items():
            if not isinstance(key, str):
                raise SchemaSerializationError(
                    "mapping keys must be strings"
                )

            frozen[key] = deep_freeze(item)

        return MappingProxyType(frozen)

    if isinstance(value, (list, tuple)):
        return tuple(
            deep_freeze(item)
            for item in value
        )

    raise SchemaSerializationError(
        "unsupported type in frozen structure: "
        f"{type(value).__name__}"
    )


def deep_thaw(
    value: Any,
) -> Any:
    """Convert immutable structures back to plain JSON-native values."""
    if isinstance(value, Enum):
        return value.value

    if isinstance(value, _SCALAR_TYPES):
        return value

    if isinstance(value, Mapping):
        return {
            key: deep_thaw(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            deep_thaw(item)
            for item in value
        ]

    raise SchemaSerializationError(
        "unsupported type in structure: "
        f"{type(value).__name__}"
    )


__all__ = [
    "AuditAction",
    "ChangeClass",
    "CompatibilityMode",
    "EMPTY_FROZEN_MAPPING",
    "EnforcementLevel",
    "IDENTIFIER_RE",
    "MAX_DESCRIPTION_LENGTH",
    "MAX_IDENTIFIER_LENGTH",
    "MAX_METADATA_SIZE_BYTES",
    "MAX_NAMESPACE_LENGTH",
    "MAX_SCHEMA_NAME_LENGTH",
    "MAX_TAG_COUNT",
    "NAME_RE",
    "NAMESPACE_RE",
    "OwnerKind",
    "RESERVED_RUNTIME_PREFIX",
    "RESERVED_RUNTIME_ROOT",
    "RESERVED_SCHEMA_CERTIFICATION_NAMESPACE",
    "RESERVED_SCHEMA_NAMESPACE",
    "RESERVED_SCHEMA_REGISTRY_NAMESPACE",
    "RuntimeScope",
    "SchemaActorType",
    "SchemaAuditError",
    "SchemaCompatibilityError",
    "SchemaDefinitionError",
    "SchemaError",
    "SchemaIdentityType",
    "SchemaLifecycleState",
    "SchemaManagementCapability",
    "SchemaMigrationError",
    "SchemaRegistryError",
    "SchemaSerializationError",
    "SchemaTransitionType",
    "SchemaValidationError",
    "TIMESTAMP_RE",
    "TransitionDirection",
    "UnknownFieldPolicy",
    "change_severity",
    "deep_freeze",
    "deep_thaw",
    "is_canonical_timestamp",
    "is_reserved_runtime_namespace",
    "is_valid_identifier",
    "is_valid_name",
    "is_valid_namespace",
    "parse_canonical_timestamp",
    "utc_now_iso",
]
