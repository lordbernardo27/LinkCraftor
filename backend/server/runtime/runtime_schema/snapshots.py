# -*- coding: utf-8 -*-
"""Runtime Schema Snapshot Engine (1.1.14.14) - value objects.

This module defines the immutable value objects that capture the state of
a runtime schema registry at a point in time, together with their
canonical serialization, deterministic fingerprints, integrity
verification and comparison logic.

The module is deliberately pure:

* It performs no I/O, no persistence, no filesystem or database access.
* It contains no registry, loader or persistence implementation.
* It carries no business-domain knowledge; a snapshot is described purely
  by counts and fingerprints, never by the meaning of any schema.

It depends only on the subsystem's own leaf modules
:mod:`runtime_schema.types`, :mod:`runtime_schema.fingerprint`,
:mod:`runtime_schema.serialization` and :mod:`runtime_schema.audit`.

Two identifiers are attached to every snapshot and must never be
conflated, mirroring the ``schema_id`` / ``content_fingerprint``
distinction used elsewhere in the subsystem:

``snapshot_id``
    Deterministic identity derived from *what the snapshot captures* - its
    generation number together with the registry and audit-head
    fingerprints. It answers "which snapshot is this".

``snapshot_fingerprint``
    Deterministic integrity fingerprint over the snapshot's *entire*
    canonical content, including its identity and metadata. It answers
    "have the contents been altered".
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Final, Iterator, Mapping, Optional

from .audit import GENESIS_HASH, AuditLog
from .fingerprint import sha256_hex
from .serialization import (
    SERIALIZATION_FORMAT_VERSION,
    canonical_json,
    parse_canonical_json,
    structure_fingerprint,
)
from .types import (
    EMPTY_FROZEN_MAPPING,
    SchemaSerializationError,
    SchemaValidationError,
    deep_freeze,
    is_canonical_timestamp,
    utc_now_iso,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Prefix distinguishing deterministic snapshot identifiers.
SNAPSHOT_ID_PREFIX: Final[str] = "snap_"

#: Hex length of the identifier portion of a ``snapshot_id``.
SNAPSHOT_ID_HEX_LENGTH: Final[int] = 32

#: Version of the Runtime Schema snapshot contract itself.
SNAPSHOT_SCHEMA_VERSION: Final[str] = "1.0.0"

#: Structure tags, mixed into canonical forms so that a snapshot and a
#: snapshot collection can never collide with each other - or with any
#: other structure in the subsystem - even given identical field values.
SNAPSHOT_STRUCTURE_KIND: Final[str] = "runtime.schema.snapshot"
SNAPSHOT_COLLECTION_STRUCTURE_KIND: Final[str] = "runtime.schema.snapshot_collection"

#: Length in hex characters of a SHA-256 fingerprint.
_SHA256_HEX_LENGTH: Final[int] = 64
_HEX_ALPHABET: Final[frozenset[str]] = frozenset("0123456789abcdef")


# ---------------------------------------------------------------------------
# Internal validation helpers
# ---------------------------------------------------------------------------


def _is_sha256_hex(value: object) -> bool:
    """True if *value* is a lowercase 64-character hexadecimal digest."""
    return (
        isinstance(value, str)
        and len(value) == _SHA256_HEX_LENGTH
        and all(char in _HEX_ALPHABET for char in value)
    )


def _require(condition: bool, message: str) -> None:
    """Raise :class:`SchemaValidationError` when *condition* is false."""
    if not condition:
        raise SchemaValidationError(message)


def _require_non_negative_int(value: object, label: str) -> None:
    """Validate that *value* is a non-negative, non-boolean integer."""
    _require(
        isinstance(value, int) and not isinstance(value, bool) and value >= 0,
        f"{label} must be a non-negative integer",
    )


def _freeze_annotations(annotations: Mapping[str, Any]) -> Mapping[str, Any]:
    """Validate and deep-freeze a free-form annotation mapping.

    Keys must be strings; the whole mapping must be canonically
    serializable. The returned mapping is a read-only, deeply immutable
    view.
    """
    _require(isinstance(annotations, Mapping), "annotations must be a mapping")
    for key in annotations:
        _require(isinstance(key, str), "annotation keys must be strings")
    frozen = deep_freeze(dict(annotations))
    try:
        canonical_json(frozen)
    except SchemaSerializationError as exc:
        raise SchemaValidationError(f"annotations are not serializable: {exc}") from exc
    return frozen


def audit_head_fingerprint(audit_log: AuditLog) -> str:
    """Return the hash-chain head fingerprint of *audit_log*.

    The head is the ``record_hash`` of the most recent audit record, or
    :data:`runtime_schema.audit.GENESIS_HASH` when the log is empty. The
    read is delegated to the thread-safe :class:`AuditLog` API; this
    function neither mutates the log nor performs any I/O.
    """
    if not isinstance(audit_log, AuditLog):
        raise SchemaValidationError("audit_log must be an AuditLog instance")
    history = audit_log.history()
    if not history:
        return GENESIS_HASH
    return history[-1].record_hash


# ---------------------------------------------------------------------------
# Snapshot metadata (item 3)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, eq=False, slots=True)
class SnapshotMetadata:
    """Immutable descriptive envelope for a snapshot.

    Groups the generation number, timestamp, the registry and audit-head
    fingerprints, the three aggregate counts and a free-form annotation
    mapping. It contains only counts and fingerprints - never any
    schema content - so it stays business-logic agnostic.
    """

    generation: int
    created_at: str
    registry_fingerprint: str
    audit_head_fingerprint: str
    schema_count: int
    namespace_count: int
    schema_namespace_count: int
    version_count: int
    annotations: Mapping[str, Any] = EMPTY_FROZEN_MAPPING

    def __post_init__(self) -> None:
        _require_non_negative_int(self.generation, "generation")
        _require(
            is_canonical_timestamp(self.created_at),
            "created_at must be a canonical UTC timestamp",
        )
        _require(
            _is_sha256_hex(self.registry_fingerprint),
            "registry_fingerprint must be a 64-character hex digest",
        )
        _require(
            _is_sha256_hex(self.audit_head_fingerprint),
            "audit_head_fingerprint must be a 64-character hex digest",
        )
        _require_non_negative_int(self.schema_count, "schema_count")
        _require_non_negative_int(self.namespace_count, "namespace_count")
        _require_non_negative_int(
            self.schema_namespace_count,
            "schema_namespace_count",
        )
        _require_non_negative_int(self.version_count, "version_count")
        _require(
            self.schema_namespace_count <= self.namespace_count,
            "schema_namespace_count cannot exceed namespace_count",
        )
        _require(
            self.version_count >= self.schema_count,
            "version_count cannot be smaller than schema_count",
        )
        object.__setattr__(
            self, "annotations", _freeze_annotations(self.annotations)
        )

    def to_canonical_dict(self) -> dict[str, Any]:
        """Deterministic, JSON-native representation of this metadata."""
        return {
            "generation": self.generation,
            "created_at": self.created_at,
            "registry_fingerprint": self.registry_fingerprint,
            "audit_head_fingerprint": self.audit_head_fingerprint,
            "schema_count": self.schema_count,
            "namespace_count": self.namespace_count,
            "schema_namespace_count": self.schema_namespace_count,
            "version_count": self.version_count,
            "annotations": dict(self.annotations),
        }

    @classmethod
    def from_canonical_dict(cls, data: Mapping[str, Any]) -> "SnapshotMetadata":
        """Rebuild metadata from its canonical representation."""
        _require(isinstance(data, Mapping), "metadata payload must be a mapping")
        annotations = data.get("annotations", EMPTY_FROZEN_MAPPING)
        _require(
            isinstance(annotations, Mapping),
            "annotations payload must be a mapping",
        )
        return cls(
            generation=data["generation"],
            created_at=data["created_at"],
            registry_fingerprint=data["registry_fingerprint"],
            audit_head_fingerprint=data["audit_head_fingerprint"],
            schema_count=data["schema_count"],
            namespace_count=data["namespace_count"],
            schema_namespace_count=data.get(
                "schema_namespace_count",
                data["namespace_count"],
            ),
            version_count=data["version_count"],
            annotations=annotations,
        )

    def fingerprint(self) -> str:
        """Deterministic fingerprint of this metadata's canonical form."""
        return structure_fingerprint(self.to_canonical_dict())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SnapshotMetadata):
            return NotImplemented
        return self.to_canonical_dict() == other.to_canonical_dict()

    def __hash__(self) -> int:
        return hash(self.fingerprint())


# ---------------------------------------------------------------------------
# Integrity + comparison result objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SnapshotIntegrityReport:
    """Immutable, complete result of an integrity verification.

    Verification never raises; every discovered problem is collected into
    :attr:`issues` and reported together, so a caller sees the full
    picture in one pass.
    """

    subject_id: str
    valid: bool
    issues: tuple[str, ...]

    def to_canonical_dict(self) -> dict[str, Any]:
        return {
            "subject_id": self.subject_id,
            "valid": self.valid,
            "issues": list(self.issues),
        }


@dataclass(frozen=True, slots=True)
class SnapshotComparison:
    """Immutable structural comparison between two snapshots.

    Purely descriptive: it reports deltas and change flags and never
    interprets what the change means.
    """

    base_snapshot_id: str
    other_snapshot_id: str
    base_generation: int
    other_generation: int
    generation_delta: int
    registry_fingerprint_changed: bool
    audit_head_changed: bool
    schema_count_delta: int
    namespace_count_delta: int
    version_count_delta: int
    namespaces_added: int
    namespaces_removed: int
    metadata_changed: bool
    identical: bool

    def to_canonical_dict(self) -> dict[str, Any]:
        return {
            "base_snapshot_id": self.base_snapshot_id,
            "other_snapshot_id": self.other_snapshot_id,
            "base_generation": self.base_generation,
            "other_generation": self.other_generation,
            "generation_delta": self.generation_delta,
            "registry_fingerprint_changed": self.registry_fingerprint_changed,
            "audit_head_changed": self.audit_head_changed,
            "schema_count_delta": self.schema_count_delta,
            "namespace_count_delta": self.namespace_count_delta,
            "version_count_delta": self.version_count_delta,
            "namespaces_added": self.namespaces_added,
            "namespaces_removed": self.namespaces_removed,
            "metadata_changed": self.metadata_changed,
            "identical": self.identical,
        }

    def fingerprint(self) -> str:
        return structure_fingerprint(self.to_canonical_dict())


# ---------------------------------------------------------------------------
# The snapshot itself (items 1, 4-14)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, eq=False, slots=True)
class RuntimeSchemaSnapshot:
    """Immutable capture of a runtime schema registry at a point in time.

    Construction validates every field, then derives - and, when values
    were supplied, verifies - the deterministic :attr:`snapshot_id` and
    :attr:`snapshot_fingerprint`. Instances are deeply immutable, so all
    read operations are inherently safe to call concurrently.
    """

    metadata: SnapshotMetadata
    serialization_format_version: str = SERIALIZATION_FORMAT_VERSION
    snapshot_schema_version: str = SNAPSHOT_SCHEMA_VERSION
    snapshot_id: str = ""
    snapshot_fingerprint: str = ""

    def __post_init__(self) -> None:
        _require(
            isinstance(self.metadata, SnapshotMetadata),
            "metadata must be a SnapshotMetadata instance",
        )
        _require(
            isinstance(self.serialization_format_version, str)
            and bool(self.serialization_format_version),
            "serialization_format_version must be a non-empty string",
        )
        _require(
            self.serialization_format_version
            == SERIALIZATION_FORMAT_VERSION,
            "unsupported serialization_format_version",
        )
        _require(
            isinstance(self.snapshot_schema_version, str)
            and bool(self.snapshot_schema_version),
            "snapshot_schema_version must be a non-empty string",
        )
        _require(
            self.snapshot_schema_version
            == SNAPSHOT_SCHEMA_VERSION,
            "unsupported snapshot_schema_version",
        )

        computed_id = self._compute_snapshot_id()
        if self.snapshot_id:
            _require(
                self.snapshot_id == computed_id,
                "snapshot_id does not match the snapshot identity",
            )
        else:
            object.__setattr__(self, "snapshot_id", computed_id)

        computed_fingerprint = self._compute_fingerprint()
        if self.snapshot_fingerprint:
            _require(
                self.snapshot_fingerprint == computed_fingerprint,
                "snapshot_fingerprint does not match the snapshot content",
            )
        else:
            object.__setattr__(
                self, "snapshot_fingerprint", computed_fingerprint
            )

    # -- convenience read-only projections (items 4-10) --------------------

    @property
    def generation(self) -> int:
        return self.metadata.generation

    @property
    def created_at(self) -> str:
        return self.metadata.created_at

    @property
    def registry_fingerprint(self) -> str:
        return self.metadata.registry_fingerprint

    @property
    def audit_head_fingerprint(self) -> str:
        return self.metadata.audit_head_fingerprint

    @property
    def schema_count(self) -> int:
        return self.metadata.schema_count

    @property
    def namespace_count(self) -> int:
        return self.metadata.namespace_count

    @property
    def version_count(self) -> int:
        return self.metadata.version_count

    @property
    def annotations(self) -> Mapping[str, Any]:
        return self.metadata.annotations

    @property
    def schema_namespace_count(self) -> int:
        return self.metadata.schema_namespace_count

    @property
    def metadata_fingerprint(self) -> str:
        """Return the deterministic metadata fingerprint."""
        return self.metadata.fingerprint()

    @property
    def annotations_fingerprint(self) -> str:
        """Return the deterministic annotation fingerprint."""
        return structure_fingerprint(
            dict(self.metadata.annotations)
        )

    # -- identity / integrity derivation -----------------------------------

    def _identity_payload(self) -> dict[str, Any]:
        """The minimal payload that *identifies* this snapshot."""
        return {
            "kind": SNAPSHOT_STRUCTURE_KIND,
            "generation": self.metadata.generation,
            "registry_fingerprint": self.metadata.registry_fingerprint,
            "audit_head_fingerprint": self.metadata.audit_head_fingerprint,
            "serialization_format_version": (
                self.serialization_format_version
            ),
            "snapshot_schema_version": self.snapshot_schema_version,
        }

    def _compute_snapshot_id(self) -> str:
        digest = sha256_hex(canonical_json(self._identity_payload()))
        return SNAPSHOT_ID_PREFIX + digest[:SNAPSHOT_ID_HEX_LENGTH]

    def _content_payload(self) -> dict[str, Any]:
        """Full canonical content excluding the fingerprint itself."""
        return {
            "kind": SNAPSHOT_STRUCTURE_KIND,
            "snapshot_id": self._compute_snapshot_id(),
            "serialization_format_version": self.serialization_format_version,
            "snapshot_schema_version": self.snapshot_schema_version,
            "metadata": self.metadata.to_canonical_dict(),
            "metadata_fingerprint": self.metadata_fingerprint,
            "annotations_fingerprint": self.annotations_fingerprint,
        }

    def _compute_fingerprint(self) -> str:
        return structure_fingerprint(self._content_payload())

    # -- canonical serialization (items 12, 13) ----------------------------

    def to_canonical_dict(self) -> dict[str, Any]:
        """Full canonical dictionary, including both derived identifiers."""
        payload = self._content_payload()
        payload["snapshot_fingerprint"] = self.snapshot_fingerprint
        return payload

    def to_canonical_json(self) -> str:
        """Canonical JSON text export of this snapshot."""
        return canonical_json(self.to_canonical_dict())

    @classmethod
    def from_canonical_dict(
        cls, data: Mapping[str, Any]
    ) -> "RuntimeSchemaSnapshot":
        """Rebuild a snapshot from canonical data, verifying integrity.

        :raises SchemaValidationError: if the payload is malformed or its
            embedded ``snapshot_id`` / ``snapshot_fingerprint`` do not
            match the values recomputed from the content.
        """
        _require(isinstance(data, Mapping), "snapshot payload must be a mapping")
        _require(
            data.get("kind") == SNAPSHOT_STRUCTURE_KIND,
            "snapshot payload has an unexpected structure kind",
        )
        metadata_payload = data.get("metadata")
        _require(
            isinstance(metadata_payload, Mapping),
            "snapshot payload is missing its metadata",
        )
        metadata = SnapshotMetadata.from_canonical_dict(metadata_payload)
        return cls(
            metadata=metadata,
            serialization_format_version=data.get(
                "serialization_format_version",
                SERIALIZATION_FORMAT_VERSION,
            ),
            snapshot_schema_version=data.get(
                "snapshot_schema_version",
                SNAPSHOT_SCHEMA_VERSION,
            ),
            snapshot_id=data.get("snapshot_id", ""),
            snapshot_fingerprint=data.get("snapshot_fingerprint", ""),
        )

    @classmethod
    def from_canonical_json(cls, text: str | bytes) -> "RuntimeSchemaSnapshot":
        """Rebuild a snapshot from canonical JSON text."""
        return cls.from_canonical_dict(parse_canonical_json(text))

    # -- integrity verification (item 14) ----------------------------------

    def verify_integrity(self) -> SnapshotIntegrityReport:
        """Recompute the identity and content fingerprints and compare.

        Never raises; collects every mismatch into the returned report.
        """
        issues: list[str] = []
        expected_id = self._compute_snapshot_id()
        if self.snapshot_id != expected_id:
            issues.append(
                f"snapshot_id mismatch: stored {self.snapshot_id!r} "
                f"!= computed {expected_id!r}"
            )
        expected_fingerprint = self._compute_fingerprint()
        if self.snapshot_fingerprint != expected_fingerprint:
            issues.append(
                "snapshot_fingerprint mismatch: stored "
                f"{self.snapshot_fingerprint!r} != computed "
                f"{expected_fingerprint!r}"
            )

        if (
            self.serialization_format_version
            != SERIALIZATION_FORMAT_VERSION
        ):
            issues.append(
                "unsupported serialization format version"
            )

        if (
            self.snapshot_schema_version
            != SNAPSHOT_SCHEMA_VERSION
        ):
            issues.append(
                "unsupported snapshot schema version"
            )

        canonical_payload = self.to_canonical_dict()

        if (
            canonical_payload.get("metadata_fingerprint")
            != self.metadata_fingerprint
        ):
            issues.append(
                "metadata fingerprint mismatch"
            )

        if (
            canonical_payload.get("annotations_fingerprint")
            != self.annotations_fingerprint
        ):
            issues.append(
                "annotations fingerprint mismatch"
            )

        return SnapshotIntegrityReport(
            subject_id=self.snapshot_id,
            valid=not issues,
            issues=tuple(issues),
        )

    # -- comparison (item 15) ----------------------------------------------

    def compare_to(self, other: "RuntimeSchemaSnapshot") -> SnapshotComparison:
        """Structural comparison of this snapshot against *other*."""
        return compare_snapshots(self, other)

    # -- equality by deterministic fingerprint (item 16) -------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuntimeSchemaSnapshot):
            return NotImplemented
        return self.snapshot_fingerprint == other.snapshot_fingerprint

    def __hash__(self) -> int:
        return hash(self.snapshot_fingerprint)


def build_snapshot(
    *,
    generation: int,
    registry_fingerprint: str,
    audit_head_fingerprint: str,
    schema_count: int,
    namespace_count: int,
    version_count: int,
    schema_namespace_count: Optional[int] = None,
    created_at: Optional[str] = None,
    annotations: Mapping[str, Any] = EMPTY_FROZEN_MAPPING,
    serialization_format_version: str = SERIALIZATION_FORMAT_VERSION,
) -> RuntimeSchemaSnapshot:
    """Construct a :class:`RuntimeSchemaSnapshot` from raw measurements.

    A convenience constructor that assembles the :class:`SnapshotMetadata`
    envelope and stamps ``created_at`` with the current canonical UTC time
    when it is not supplied. It performs no I/O and reads nothing from any
    registry; the caller provides all measured values.
    """
    metadata = SnapshotMetadata(
        generation=generation,
        created_at=created_at if created_at is not None else utc_now_iso(),
        registry_fingerprint=registry_fingerprint,
        audit_head_fingerprint=audit_head_fingerprint,
        schema_count=schema_count,
        namespace_count=namespace_count,
        schema_namespace_count=(
            namespace_count
            if schema_namespace_count is None
            else schema_namespace_count
        ),
        version_count=version_count,
        annotations=annotations,
    )
    return RuntimeSchemaSnapshot(
        metadata=metadata,
        serialization_format_version=serialization_format_version,
        snapshot_schema_version=SNAPSHOT_SCHEMA_VERSION,
    )


def build_empty_snapshot(
    *,
    created_at: Optional[str] = None,
    annotations: Mapping[str, Any] = EMPTY_FROZEN_MAPPING,
) -> RuntimeSchemaSnapshot:
    """Build the canonical generation-zero runtime snapshot."""
    return build_snapshot(
        generation=0,
        registry_fingerprint=structure_fingerprint(
            {
                "kind": "runtime.schema.empty_registry",
                "schemas": [],
            }
        ),
        audit_head_fingerprint=GENESIS_HASH,
        schema_count=0,
        namespace_count=0,
        schema_namespace_count=0,
        version_count=0,
        created_at=created_at,
        annotations=annotations,
    )


def compare_snapshots(
    base: RuntimeSchemaSnapshot, other: RuntimeSchemaSnapshot
) -> SnapshotComparison:
    """Return a :class:`SnapshotComparison` between two snapshots."""
    _require(
        isinstance(base, RuntimeSchemaSnapshot)
        and isinstance(other, RuntimeSchemaSnapshot),
        "compare_snapshots requires two RuntimeSchemaSnapshot instances",
    )
    return SnapshotComparison(
        base_snapshot_id=base.snapshot_id,
        other_snapshot_id=other.snapshot_id,
        base_generation=base.generation,
        other_generation=other.generation,
        generation_delta=other.generation - base.generation,
        registry_fingerprint_changed=(
            base.registry_fingerprint != other.registry_fingerprint
        ),
        audit_head_changed=(
            base.audit_head_fingerprint != other.audit_head_fingerprint
        ),
        schema_count_delta=other.schema_count - base.schema_count,
        namespace_count_delta=(
            other.namespace_count
            - base.namespace_count
        ),
        version_count_delta=(
            other.version_count
            - base.version_count
        ),
        namespaces_added=max(
            0,
            other.namespace_count
            - base.namespace_count,
        ),
        namespaces_removed=max(
            0,
            base.namespace_count
            - other.namespace_count,
        ),
        metadata_changed=(
            base.metadata_fingerprint
            != other.metadata_fingerprint
        ),
        identical=(
            base.snapshot_fingerprint
            == other.snapshot_fingerprint
        ),
    )


# ---------------------------------------------------------------------------
# Snapshot collection (items 2, 11-17)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, eq=False, slots=True)
class SnapshotCollection:
    """Immutable, ordered collection of snapshots.

    Members are stored in a deterministic order (ascending generation,
    then ``snapshot_id``). Generation numbers and snapshot identifiers
    must both be unique within a collection. The instance is immutable;
    "mutating" helpers such as :meth:`with_snapshot` return a new
    collection.

    Read operations are thread-safe: the members are immutable and the
    lookup indexes are built once at construction, while the lazily
    memoized collection fingerprint is guarded by an internal lock.
    """

    snapshots: tuple[RuntimeSchemaSnapshot, ...] = ()
    _by_id: Mapping[str, RuntimeSchemaSnapshot] = field(
        default=EMPTY_FROZEN_MAPPING, compare=False, repr=False
    )
    _by_generation: Mapping[int, RuntimeSchemaSnapshot] = field(
        default=EMPTY_FROZEN_MAPPING, compare=False, repr=False
    )
    _lock: threading.RLock = field(
        default_factory=threading.RLock, compare=False, repr=False
    )
    _fingerprint_cache: list[str] = field(
        default_factory=list, compare=False, repr=False
    )
    _latest_generation: int = field(
        default=-1, compare=False, repr=False
    )
    _highest_schema_count: int = field(
        default=0, compare=False, repr=False
    )
    _highest_version_count: int = field(
        default=0, compare=False, repr=False
    )

    def __post_init__(self) -> None:
        members = tuple(self.snapshots)
        for member in members:
            _require(
                isinstance(member, RuntimeSchemaSnapshot),
                "every member must be a RuntimeSchemaSnapshot",
            )
        ordered = tuple(
            sorted(members, key=lambda s: (s.generation, s.snapshot_id))
        )

        by_id: dict[str, RuntimeSchemaSnapshot] = {}
        by_generation: dict[int, RuntimeSchemaSnapshot] = {}
        for member in ordered:
            _require(
                member.snapshot_id not in by_id,
                f"duplicate snapshot_id in collection: {member.snapshot_id}",
            )
            _require(
                member.generation not in by_generation,
                f"duplicate generation in collection: {member.generation}",
            )
            by_id[member.snapshot_id] = member
            by_generation[member.generation] = member

        object.__setattr__(self, "snapshots", ordered)
        object.__setattr__(self, "_by_id", MappingProxyType(by_id))
        object.__setattr__(
            self,
            "_by_generation",
            MappingProxyType(by_generation),
        )
        object.__setattr__(
            self,
            "_latest_generation",
            (
                ordered[-1].generation
                if ordered
                else -1
            ),
        )
        object.__setattr__(
            self,
            "_highest_schema_count",
            max(
                (
                    member.schema_count
                    for member in ordered
                ),
                default=0,
            ),
        )
        object.__setattr__(
            self,
            "_highest_version_count",
            max(
                (
                    member.version_count
                    for member in ordered
                ),
                default=0,
            ),
        )

    # -- sized / iterable / container (item 17) ----------------------------

    def __len__(self) -> int:
        return len(self.snapshots)

    def __iter__(self) -> Iterator[RuntimeSchemaSnapshot]:
        return iter(self.snapshots)

    def __getitem__(self, index: int) -> RuntimeSchemaSnapshot:
        return self.snapshots[index]

    def __contains__(self, snapshot_id: object) -> bool:
        return snapshot_id in self._by_id

    # -- lookups (item 17) -------------------------------------------------

    def get(self, snapshot_id: str) -> Optional[RuntimeSchemaSnapshot]:
        """Return the snapshot with *snapshot_id*, or ``None``."""
        return self._by_id.get(snapshot_id)

    def by_generation(self, generation: int) -> Optional[RuntimeSchemaSnapshot]:
        """Return the snapshot at *generation*, or ``None``."""
        return self._by_generation.get(generation)

    def latest(self) -> Optional[RuntimeSchemaSnapshot]:
        """Return the highest-generation snapshot, or ``None`` if empty."""
        if self._latest_generation < 0:
            return None

        return self._by_generation[
            self._latest_generation
        ]

    @property
    def latest_generation(self) -> Optional[int]:
        """Return the highest generation, or ``None`` when empty."""
        return (
            None
            if self._latest_generation < 0
            else self._latest_generation
        )

    @property
    def highest_schema_count(self) -> int:
        return self._highest_schema_count

    @property
    def highest_version_count(self) -> int:
        return self._highest_version_count

    def generations(self) -> tuple[int, ...]:
        """All generation numbers in ascending order."""
        return tuple(snapshot.generation for snapshot in self.snapshots)

    # -- immutable evolution -----------------------------------------------

    def with_snapshot(
        self, snapshot: RuntimeSchemaSnapshot
    ) -> "SnapshotCollection":
        """Return a new collection with *snapshot* added.

        :raises SchemaValidationError: if a snapshot with the same
            identifier or generation is already present.
        """
        _require(
            isinstance(snapshot, RuntimeSchemaSnapshot),
            "with_snapshot requires a RuntimeSchemaSnapshot",
        )
        _require(
            snapshot.snapshot_id not in self._by_id,
            f"snapshot_id already present: {snapshot.snapshot_id}",
        )
        _require(
            snapshot.generation not in self._by_generation,
            f"generation already present: {snapshot.generation}",
        )
        return SnapshotCollection(snapshots=self.snapshots + (snapshot,))

    # -- deterministic fingerprint (item 11) -------------------------------

    def fingerprint(self) -> str:
        """Deterministic fingerprint over the ordered member fingerprints.

        Lazily computed and memoized under the collection's lock, so that
        concurrent readers observe a single, stable value.
        """
        with self._lock:
            if not self._fingerprint_cache:
                payload = {
                    "kind": SNAPSHOT_COLLECTION_STRUCTURE_KIND,
                    "serialization_format_version": (
                        SERIALIZATION_FORMAT_VERSION
                    ),
                    "snapshot_schema_version": (
                        SNAPSHOT_SCHEMA_VERSION
                    ),
                    "collection_size": len(
                        self.snapshots
                    ),
                    "latest_generation": (
                        self.latest_generation
                    ),
                    "highest_schema_count": (
                        self.highest_schema_count
                    ),
                    "highest_version_count": (
                        self.highest_version_count
                    ),
                    "members": [
                        snapshot.snapshot_fingerprint
                        for snapshot in self.snapshots
                    ],
                }
                self._fingerprint_cache.append(structure_fingerprint(payload))
            return self._fingerprint_cache[0]

    # -- canonical serialization (items 12, 13) ----------------------------

    def to_canonical_dict(self) -> dict[str, Any]:
        """Full canonical dictionary export of the collection."""
        return {
            "kind": SNAPSHOT_COLLECTION_STRUCTURE_KIND,
            "serialization_format_version": SERIALIZATION_FORMAT_VERSION,
            "snapshots": [
                snapshot.to_canonical_dict() for snapshot in self.snapshots
            ],
            "collection_fingerprint": self.fingerprint(),
        }

    def to_canonical_json(self) -> str:
        """Canonical JSON text export of the collection."""
        return canonical_json(self.to_canonical_dict())

    @classmethod
    def from_canonical_dict(
        cls, data: Mapping[str, Any]
    ) -> "SnapshotCollection":
        """Rebuild a collection from canonical data, verifying integrity.

        :raises SchemaValidationError: if the payload is malformed, any
            member fails its own integrity check, or the stored
            ``collection_fingerprint`` does not match the recomputed value.
        """
        _require(isinstance(data, Mapping), "collection payload must be a mapping")
        _require(
            data.get("kind")
            == SNAPSHOT_COLLECTION_STRUCTURE_KIND,
            "collection payload has an unexpected structure kind",
        )
        raw_members = data.get("snapshots", ())
        _require(
            isinstance(raw_members, (list, tuple)),
            "collection payload 'snapshots' must be a sequence",
        )
        members = tuple(
            RuntimeSchemaSnapshot.from_canonical_dict(member)
            for member in raw_members
        )
        collection = cls(snapshots=members)
        expected = data.get("collection_fingerprint")
        if expected is not None:
            _require(
                expected == collection.fingerprint(),
                "collection_fingerprint does not match the rebuilt collection",
            )
        return collection

    @classmethod
    def from_canonical_json(cls, text: str | bytes) -> "SnapshotCollection":
        """Rebuild a collection from canonical JSON text."""
        return cls.from_canonical_dict(parse_canonical_json(text))

    # -- integrity verification (item 14) ----------------------------------

    def verify_integrity(self) -> SnapshotIntegrityReport:
        """Verify every member plus ordering, uniqueness and fingerprint.

        Never raises; all problems are aggregated into one report.
        """
        issues: list[str] = []
        seen_ids: set[str] = set()
        seen_generations: set[int] = set()
        previous_key: Optional[tuple[int, str]] = None

        for member in self.snapshots:
            member_report = member.verify_integrity()
            if not member_report.valid:
                issues.extend(
                    f"{member.snapshot_id}: {issue}"
                    for issue in member_report.issues
                )
            if member.snapshot_id in seen_ids:
                issues.append(f"duplicate snapshot_id: {member.snapshot_id}")
            seen_ids.add(member.snapshot_id)
            if member.generation in seen_generations:
                issues.append(f"duplicate generation: {member.generation}")
            seen_generations.add(member.generation)

            key = (member.generation, member.snapshot_id)
            if previous_key is not None and key < previous_key:
                issues.append(
                    f"members out of order at generation {member.generation}"
                )
            previous_key = key

        return SnapshotIntegrityReport(
            subject_id=self.fingerprint(),
            valid=not issues,
            issues=tuple(issues),
        )

    # -- equality by deterministic fingerprint (item 16) -------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SnapshotCollection):
            return NotImplemented
        return self.fingerprint() == other.fingerprint()

    def __hash__(self) -> int:
        return hash(self.fingerprint())


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    # constants
    "SNAPSHOT_ID_PREFIX",
    "SNAPSHOT_ID_HEX_LENGTH",
    "SNAPSHOT_STRUCTURE_KIND",
    "SNAPSHOT_COLLECTION_STRUCTURE_KIND",
    "SNAPSHOT_SCHEMA_VERSION",
    # value objects
    "SnapshotMetadata",
    "RuntimeSchemaSnapshot",
    "SnapshotCollection",
    "SnapshotComparison",
    "SnapshotIntegrityReport",
    # helpers
    "audit_head_fingerprint",
    "build_empty_snapshot",
    "build_snapshot",
    "compare_snapshots",
]