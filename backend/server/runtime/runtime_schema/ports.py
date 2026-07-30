# -*- coding: utf-8 -*-
"""Abstract ports for Runtime Schema Management.

This module defines implementation-neutral interfaces for the Runtime Schema
Management subsystem.

The ports follow these rules:

* no registry, loader, persistence, database, filesystem, or network logic;
* no product-specific business logic;
* deterministic canonical contracts;
* thread-safe implementation requirements;
* immutable value objects where concrete subsystem types are exposed;
* canonical mappings where importing implementation-layer value types would
  create unnecessary coupling.

Concrete implementations may hold state, but these abstract port definitions
hold no state and perform no work.
"""

from __future__ import annotations

import abc
from typing import (
    Any,
    Mapping,
    Sequence,
    TypeAlias,
)

from .fingerprint import (
    FINGERPRINT_ALGORITHM,
    SCHEMA_ID_PREFIX,
)
from .serialization import (
    SERIALIZATION_FORMAT_VERSION,
)
from .snapshots import (
    RuntimeSchemaSnapshot,
    SnapshotCollection,
    SnapshotComparison,
    SnapshotIntegrityReport,
)
from .types import (
    AuditAction,
    CompatibilityMode,
    SchemaLifecycleState,
    TransitionDirection,
    UnknownFieldPolicy,
)
from .validation import ValidationReport


CANONICAL_FINGERPRINT_ALGORITHM: str = (
    FINGERPRINT_ALGORITHM
)

CANONICAL_SCHEMA_ID_PREFIX: str = (
    SCHEMA_ID_PREFIX
)

CANONICAL_SERIALIZATION_FORMAT_VERSION: str = (
    SERIALIZATION_FORMAT_VERSION
)


CanonicalMapping: TypeAlias = Mapping[str, Any]
CanonicalDocument: TypeAlias = Mapping[str, Any]

Namespace: TypeAlias = str
SchemaName: TypeAlias = str
VersionString: TypeAlias = str
Coordinate: TypeAlias = str
SchemaId: TypeAlias = str
SnapshotId: TypeAlias = str
Fingerprint: TypeAlias = str
ActorId: TypeAlias = str
OwnerId: TypeAlias = str
Reference: TypeAlias = str


class RuntimeSchemaRegistryPort(
    abc.ABC
):
    """Authoritative schema-registry contract.

    A conforming implementation must perform every mutation atomically.
    Failed registration or lifecycle transitions must leave the registry,
    ownership state, audit state, and generation unchanged.
    """

    __slots__ = ()

    @abc.abstractmethod
    def register_namespace(
        self,
        namespace: Namespace,
        owner_id: OwnerId,
        actor: ActorId,
        *,
        runtime_actor: bool = False,
        description: str = "",
    ) -> CanonicalMapping:
        """Register a namespace and return its canonical record."""
        raise NotImplementedError

    @abc.abstractmethod
    def register_schema(
        self,
        definition: CanonicalMapping,
        actor: ActorId,
        *,
        runtime_actor: bool = False,
    ) -> CanonicalMapping:
        """Atomically register one immutable schema version.

        Implementations must enforce:

        * namespace authorization;
        * subject ownership;
        * version uniqueness;
        * compatibility policy;
        * semantic-version bump policy;
        * deterministic audit creation.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_schema(
        self,
        namespace: Namespace,
        name: SchemaName,
        version: VersionString | None = None,
        *,
        include_inactive: bool = False,
    ) -> CanonicalMapping | None:
        """Return one canonical schema definition or ``None``.

        When ``version`` is omitted, the latest eligible version is returned.
        Retired, quarantined, suspended, or deprecated versions may be omitted
        unless ``include_inactive`` is explicitly enabled.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def require_schema(
        self,
        namespace: Namespace,
        name: SchemaName,
        version: VersionString | None = None,
        *,
        include_inactive: bool = False,
    ) -> CanonicalMapping:
        """Return one canonical schema definition or raise."""
        raise NotImplementedError

    @abc.abstractmethod
    def list_schemas(
        self,
        *,
        namespace: Namespace | None = None,
        name: SchemaName | None = None,
        lifecycle_state: SchemaLifecycleState | None = None,
    ) -> tuple[CanonicalMapping, ...]:
        """Return matching schemas in deterministic coordinate order."""
        raise NotImplementedError

    @abc.abstractmethod
    def list_versions(
        self,
        namespace: Namespace,
        name: SchemaName,
    ) -> tuple[CanonicalMapping, ...]:
        """Return every registered version in semantic-version order."""
        raise NotImplementedError

    @abc.abstractmethod
    def contains(
        self,
        namespace: Namespace,
        name: SchemaName,
        version: VersionString | None = None,
    ) -> bool:
        """Return whether the registry contains the requested subject/version."""
        raise NotImplementedError

    @abc.abstractmethod
    def transition_lifecycle(
        self,
        namespace: Namespace,
        name: SchemaName,
        version: VersionString,
        new_state: SchemaLifecycleState,
        actor: ActorId,
        *,
        policy: CanonicalMapping | None = None,
    ) -> CanonicalMapping:
        """Atomically transition one schema version's lifecycle.

        ``policy`` carries canonical deprecation data when required.
        The result must include the updated canonical schema record and
        mutation evidence.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def registry_generation(
        self,
    ) -> int:
        """Return the monotonic registry generation."""
        raise NotImplementedError

    @abc.abstractmethod
    def registry_fingerprint(
        self,
    ) -> Fingerprint:
        """Return the deterministic aggregate registry fingerprint."""
        raise NotImplementedError

    @abc.abstractmethod
    def registry_measurements(
        self,
    ) -> CanonicalMapping:
        """Return canonical snapshot measurements.

        The mapping must include at least:

        * generation;
        * registry fingerprint;
        * schema count;
        * namespace count;
        * schema namespace count;
        * version count.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def verify_integrity(
        self,
    ) -> CanonicalMapping:
        """Return a complete canonical registry-integrity report."""
        raise NotImplementedError


class RuntimeSchemaLoaderPort(
    abc.ABC
):
    """Contract for resolving schema references into canonical definitions."""

    __slots__ = ()

    @abc.abstractmethod
    def can_load(
        self,
        reference: Reference,
    ) -> bool:
        """Return whether this loader recognizes the reference syntax."""
        raise NotImplementedError

    @abc.abstractmethod
    def load(
        self,
        reference: Reference,
    ) -> CanonicalMapping:
        """Resolve one reference into one canonical schema definition."""
        raise NotImplementedError

    @abc.abstractmethod
    def load_all(
        self,
        references: Sequence[Reference],
    ) -> tuple[CanonicalMapping, ...]:
        """Resolve references deterministically while preserving input order."""
        raise NotImplementedError

    @abc.abstractmethod
    def validate_reference(
        self,
        reference: Reference,
    ) -> CanonicalMapping:
        """Return a canonical reference-validation report."""
        raise NotImplementedError


class RuntimeSchemaSnapshotPort(
    abc.ABC
):
    """Contract for immutable registry snapshot capture and inspection."""

    __slots__ = ()

    @abc.abstractmethod
    def capture(
        self,
        actor: ActorId,
        *,
        annotations: Mapping[str, Any] | None = None,
    ) -> RuntimeSchemaSnapshot:
        """Capture the current registry and audit state atomically."""
        raise NotImplementedError

    @abc.abstractmethod
    def get(
        self,
        snapshot_id: SnapshotId,
    ) -> RuntimeSchemaSnapshot | None:
        """Return one captured snapshot or ``None``."""
        raise NotImplementedError

    @abc.abstractmethod
    def require(
        self,
        snapshot_id: SnapshotId,
    ) -> RuntimeSchemaSnapshot:
        """Return one captured snapshot or raise."""
        raise NotImplementedError

    @abc.abstractmethod
    def latest(
        self,
    ) -> RuntimeSchemaSnapshot | None:
        """Return the highest-generation snapshot or ``None``."""
        raise NotImplementedError

    @abc.abstractmethod
    def collection(
        self,
    ) -> SnapshotCollection:
        """Return every captured snapshot as an immutable collection."""
        raise NotImplementedError

    @abc.abstractmethod
    def compare(
        self,
        base_snapshot_id: SnapshotId,
        other_snapshot_id: SnapshotId,
    ) -> SnapshotComparison:
        """Compare two captured snapshots."""
        raise NotImplementedError

    @abc.abstractmethod
    def verify(
        self,
        snapshot_id: SnapshotId,
    ) -> SnapshotIntegrityReport:
        """Verify one captured snapshot."""
        raise NotImplementedError

    @abc.abstractmethod
    def verify_collection(
        self,
    ) -> SnapshotIntegrityReport:
        """Verify the complete snapshot collection."""
        raise NotImplementedError


class RuntimeSchemaValidationPort(
    abc.ABC
):
    """Contract for deterministic definition and document validation."""

    __slots__ = ()

    @abc.abstractmethod
    def validate_definition(
        self,
        definition: CanonicalMapping,
    ) -> CanonicalMapping:
        """Return a canonical schema-definition validation report.

        This report is intentionally canonical rather than
        :class:`ValidationReport`, because ``ValidationReport`` describes
        document validation against an already valid schema definition.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def validate_document(
        self,
        document: CanonicalDocument,
        definition: CanonicalMapping,
        *,
        unknown_field_policy: UnknownFieldPolicy = (
            UnknownFieldPolicy.REJECT
        ),
    ) -> ValidationReport:
        """Validate one document against one canonical schema definition."""
        raise NotImplementedError


class RuntimeSchemaMigrationPort(
    abc.ABC
):
    """Contract for migration planning and transition validation only."""

    __slots__ = ()

    @abc.abstractmethod
    def plan_migration(
        self,
        source: CanonicalMapping,
        target: CanonicalMapping,
        *,
        change_report: CanonicalMapping | None = None,
    ) -> CanonicalMapping:
        """Return a deterministic canonical migration plan."""
        raise NotImplementedError

    @abc.abstractmethod
    def validate_transition(
        self,
        plan: CanonicalMapping,
        source: CanonicalMapping,
        target: CanonicalMapping,
        direction: TransitionDirection,
        *,
        acknowledge_data_loss: bool = False,
    ) -> CanonicalMapping:
        """Validate one upgrade or downgrade plan.

        Source and target definitions are required because transition
        validation recomputes and verifies deterministic plan integrity.
        """
        raise NotImplementedError


class RuntimeSchemaAuditPort(
    abc.ABC
):
    """Contract for append-only, hash-chained audit evidence."""

    __slots__ = ()

    @abc.abstractmethod
    def append(
        self,
        actor: ActorId,
        action: AuditAction,
        subject: str,
        *,
        detail: str = "",
        before_fingerprint: Fingerprint | None = None,
        after_fingerprint: Fingerprint | None = None,
        expected_head_hash: Fingerprint | None = None,
    ) -> CanonicalMapping:
        """Append one audit record under optional compare-and-append control."""
        raise NotImplementedError

    @abc.abstractmethod
    def history(
        self,
        subject: str | None = None,
    ) -> tuple[CanonicalMapping, ...]:
        """Return global or subject-filtered audit history."""
        raise NotImplementedError

    @abc.abstractmethod
    def records_for_action(
        self,
        action: AuditAction,
    ) -> tuple[CanonicalMapping, ...]:
        """Return audit records matching one action."""
        raise NotImplementedError

    @abc.abstractmethod
    def head_fingerprint(
        self,
    ) -> Fingerprint:
        """Return the current audit-chain head."""
        raise NotImplementedError

    @abc.abstractmethod
    def generation(
        self,
    ) -> int:
        """Return the current audit generation."""
        raise NotImplementedError

    @abc.abstractmethod
    def verify_chain(
        self,
    ) -> CanonicalMapping:
        """Return a canonical full-chain verification report."""
        raise NotImplementedError

    @abc.abstractmethod
    def export_records(
        self,
    ) -> tuple[CanonicalMapping, ...]:
        """Return a lossless canonical audit export."""
        raise NotImplementedError


class RuntimeSchemaDiffPort(
    abc.ABC
):
    """Contract for structural diffing and semantic change detection."""

    __slots__ = ()

    @abc.abstractmethod
    def diff(
        self,
        source: CanonicalMapping,
        target: CanonicalMapping,
    ) -> CanonicalMapping:
        """Return a canonical structural schema diff."""
        raise NotImplementedError

    @abc.abstractmethod
    def detect_changes(
        self,
        source: CanonicalMapping,
        target: CanonicalMapping,
    ) -> CanonicalMapping:
        """Return the canonical semantic change report for a schema pair."""
        raise NotImplementedError


class RuntimeSchemaCompatibilityPort(
    abc.ABC
):
    """Contract for candidate compatibility evaluation."""

    __slots__ = ()

    @abc.abstractmethod
    def check(
        self,
        candidate: CanonicalMapping,
        prior_versions: Sequence[CanonicalMapping],
        *,
        mode: CompatibilityMode | None = None,
    ) -> CanonicalMapping:
        """Return a complete canonical compatibility report."""
        raise NotImplementedError

    @abc.abstractmethod
    def is_compatible(
        self,
        candidate: CanonicalMapping,
        prior_versions: Sequence[CanonicalMapping],
        *,
        mode: CompatibilityMode | None = None,
    ) -> bool:
        """Return only the compatibility verdict."""
        raise NotImplementedError

    @abc.abstractmethod
    def runtime_requirement_satisfied(
        self,
        required_runtime_version: VersionString | None,
    ) -> bool:
        """Return whether the running runtime satisfies a requirement."""
        raise NotImplementedError


class RuntimeSchemaCertificationPort(
    abc.ABC
):
    """Contract for deterministic Runtime Schema subsystem certification."""

    __slots__ = ()

    @abc.abstractmethod
    def certify(
        self,
    ) -> CanonicalMapping:
        """Run the fixed certification matrix and return canonical evidence."""
        raise NotImplementedError

    @abc.abstractmethod
    def last_report(
        self,
    ) -> CanonicalMapping | None:
        """Return the most recent certification report or ``None``."""
        raise NotImplementedError

    @abc.abstractmethod
    def certification_fingerprint(
        self,
    ) -> Fingerprint | None:
        """Return the latest certification fingerprint or ``None``."""
        raise NotImplementedError


__all__ = [
    "CANONICAL_FINGERPRINT_ALGORITHM",
    "CANONICAL_SCHEMA_ID_PREFIX",
    "CANONICAL_SERIALIZATION_FORMAT_VERSION",
    "ActorId",
    "CanonicalDocument",
    "CanonicalMapping",
    "Coordinate",
    "Fingerprint",
    "Namespace",
    "OwnerId",
    "Reference",
    "SchemaId",
    "SchemaName",
    "SnapshotId",
    "VersionString",
    "RuntimeSchemaAuditPort",
    "RuntimeSchemaCertificationPort",
    "RuntimeSchemaCompatibilityPort",
    "RuntimeSchemaDiffPort",
    "RuntimeSchemaLoaderPort",
    "RuntimeSchemaMigrationPort",
    "RuntimeSchemaRegistryPort",
    "RuntimeSchemaSnapshotPort",
    "RuntimeSchemaValidationPort",
]
