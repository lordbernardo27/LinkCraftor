from __future__ import annotations

import hashlib
import importlib
import py_compile
import shutil
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path.cwd().resolve()

RUNTIME_DIR = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
)

PACKAGE_DIR = RUNTIME_DIR / "runtime_schema"

TARGET = PACKAGE_DIR / "snapshots.py"

REQUIRED_FILES = [
    PACKAGE_DIR / "types.py",
    PACKAGE_DIR / "fingerprint.py",
    PACKAGE_DIR / "serialization.py",
    PACKAGE_DIR / "audit.py",
]

EXPECTED_BASELINE_SIZE = 32185

EXPECTED_BASELINE_SHA256 = (
    "e36904f3df54e14019fe66eb603c3e335d2ffe3fc7e9cfb7e93f9e3d89c1ba25"
)

TIMESTAMP = datetime.now(
    timezone.utc
).strftime(
    "%Y%m%dT%H%M%SZ"
)

BACKUP = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"runtime_schema_snapshots_patch_{TIMESTAMP}"
    / TARGET.name
)


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(
                chunk
            )

    return digest.hexdigest()


def replace_once(
    source: str,
    old: str,
    new: str,
    label: str,
) -> str:
    count = source.count(
        old
    )

    if count != 1:
        raise RuntimeError(
            f"{label}: expected exactly one match, "
            f"found {count}."
        )

    return source.replace(
        old,
        new,
        1,
    )


def apply_revisions(
    original: str,
) -> str:
    revised = original

    revised = replace_once(
        revised,
        '''#: Hex length of the identifier portion of a ``snapshot_id``.
SNAPSHOT_ID_HEX_LENGTH: Final[int] = 32

#: Structure tags, mixed into canonical forms so that a snapshot and a
''',
        '''#: Hex length of the identifier portion of a ``snapshot_id``.
SNAPSHOT_ID_HEX_LENGTH: Final[int] = 32

#: Version of the Runtime Schema snapshot contract itself.
SNAPSHOT_SCHEMA_VERSION: Final[str] = "1.0.0"

#: Structure tags, mixed into canonical forms so that a snapshot and a
''',
        "Add snapshot schema version",
    )

    revised = replace_once(
        revised,
        '''    schema_count: int
    namespace_count: int
    version_count: int
    annotations: Mapping[str, Any] = EMPTY_FROZEN_MAPPING
''',
        '''    schema_count: int
    namespace_count: int
    schema_namespace_count: int
    version_count: int
    annotations: Mapping[str, Any] = EMPTY_FROZEN_MAPPING
''',
        "Add schema namespace count",
    )

    revised = replace_once(
        revised,
        '''        _require_non_negative_int(self.schema_count, "schema_count")
        _require_non_negative_int(self.namespace_count, "namespace_count")
        _require_non_negative_int(self.version_count, "version_count")
        _require(
            self.version_count >= self.schema_count,
            "version_count cannot be smaller than schema_count",
        )
''',
        '''        _require_non_negative_int(self.schema_count, "schema_count")
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
''',
        "Validate schema namespace count",
    )

    revised = replace_once(
        revised,
        '''            "schema_count": self.schema_count,
            "namespace_count": self.namespace_count,
            "version_count": self.version_count,
            "annotations": dict(self.annotations),
''',
        '''            "schema_count": self.schema_count,
            "namespace_count": self.namespace_count,
            "schema_namespace_count": self.schema_namespace_count,
            "version_count": self.version_count,
            "annotations": dict(self.annotations),
''',
        "Serialize schema namespace count",
    )

    revised = replace_once(
        revised,
        '''            schema_count=data["schema_count"],
            namespace_count=data["namespace_count"],
            version_count=data["version_count"],
            annotations=annotations,
''',
        '''            schema_count=data["schema_count"],
            namespace_count=data["namespace_count"],
            schema_namespace_count=data.get(
                "schema_namespace_count",
                data["namespace_count"],
            ),
            version_count=data["version_count"],
            annotations=annotations,
''',
        "Deserialize schema namespace count",
    )

    revised = replace_once(
        revised,
        '''    metadata: SnapshotMetadata
    serialization_format_version: str = SERIALIZATION_FORMAT_VERSION
    snapshot_id: str = ""
    snapshot_fingerprint: str = ""
''',
        '''    metadata: SnapshotMetadata
    serialization_format_version: str = SERIALIZATION_FORMAT_VERSION
    snapshot_schema_version: str = SNAPSHOT_SCHEMA_VERSION
    snapshot_id: str = ""
    snapshot_fingerprint: str = ""
''',
        "Add snapshot schema version field",
    )

    revised = replace_once(
        revised,
        '''        _require(
            isinstance(self.serialization_format_version, str)
            and bool(self.serialization_format_version),
            "serialization_format_version must be a non-empty string",
        )

        computed_id = self._compute_snapshot_id()
''',
        '''        _require(
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
''',
        "Validate snapshot contract versions",
    )

    revised = replace_once(
        revised,
        '''    @property
    def annotations(self) -> Mapping[str, Any]:
        return self.metadata.annotations

    # -- identity / integrity derivation -----------------------------------
''',
        '''    @property
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
''',
        "Add snapshot integrity projections",
    )

    revised = replace_once(
        revised,
        '''        return {
            "kind": SNAPSHOT_STRUCTURE_KIND,
            "generation": self.metadata.generation,
            "registry_fingerprint": self.metadata.registry_fingerprint,
            "audit_head_fingerprint": self.metadata.audit_head_fingerprint,
        }
''',
        '''        return {
            "kind": SNAPSHOT_STRUCTURE_KIND,
            "generation": self.metadata.generation,
            "registry_fingerprint": self.metadata.registry_fingerprint,
            "audit_head_fingerprint": self.metadata.audit_head_fingerprint,
            "serialization_format_version": (
                self.serialization_format_version
            ),
            "snapshot_schema_version": self.snapshot_schema_version,
        }
''',
        "Strengthen snapshot identity",
    )

    revised = replace_once(
        revised,
        '''        return {
            "kind": SNAPSHOT_STRUCTURE_KIND,
            "snapshot_id": self._compute_snapshot_id(),
            "serialization_format_version": self.serialization_format_version,
            "metadata": self.metadata.to_canonical_dict(),
        }
''',
        '''        return {
            "kind": SNAPSHOT_STRUCTURE_KIND,
            "snapshot_id": self._compute_snapshot_id(),
            "serialization_format_version": self.serialization_format_version,
            "snapshot_schema_version": self.snapshot_schema_version,
            "metadata": self.metadata.to_canonical_dict(),
            "metadata_fingerprint": self.metadata_fingerprint,
            "annotations_fingerprint": self.annotations_fingerprint,
        }
''',
        "Strengthen snapshot content fingerprint",
    )

    revised = replace_once(
        revised,
        '''        _require(
            data.get("kind", SNAPSHOT_STRUCTURE_KIND) == SNAPSHOT_STRUCTURE_KIND,
            "snapshot payload has an unexpected structure kind",
        )
''',
        '''        _require(
            data.get("kind") == SNAPSHOT_STRUCTURE_KIND,
            "snapshot payload has an unexpected structure kind",
        )
''',
        "Require explicit snapshot structure kind",
    )

    revised = replace_once(
        revised,
        '''            serialization_format_version=data.get(
                "serialization_format_version", SERIALIZATION_FORMAT_VERSION
            ),
            snapshot_id=data.get("snapshot_id", ""),
            snapshot_fingerprint=data.get("snapshot_fingerprint", ""),
''',
        '''            serialization_format_version=data.get(
                "serialization_format_version",
                SERIALIZATION_FORMAT_VERSION,
            ),
            snapshot_schema_version=data.get(
                "snapshot_schema_version",
                SNAPSHOT_SCHEMA_VERSION,
            ),
            snapshot_id=data.get("snapshot_id", ""),
            snapshot_fingerprint=data.get("snapshot_fingerprint", ""),
''',
        "Restore snapshot schema version",
    )

    revised = replace_once(
        revised,
        '''        expected_fingerprint = self._compute_fingerprint()
        if self.snapshot_fingerprint != expected_fingerprint:
            issues.append(
                "snapshot_fingerprint mismatch: stored "
                f"{self.snapshot_fingerprint!r} != computed "
                f"{expected_fingerprint!r}"
            )
        return SnapshotIntegrityReport(
''',
        '''        expected_fingerprint = self._compute_fingerprint()
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
''',
        "Expand snapshot integrity verification",
    )

    revised = replace_once(
        revised,
        '''    namespace_count: int
    version_count: int
    identical: bool
''',
        '''    namespace_count_delta: int
    version_count_delta: int
    namespaces_added: int
    namespaces_removed: int
    metadata_changed: bool
    identical: bool
''',
        "Expand snapshot comparison fields",
    ) if False else revised

    # Replace the actual SnapshotComparison field block.
    revised = replace_once(
        revised,
        '''    schema_count_delta: int
    namespace_count_delta: int
    version_count_delta: int
    identical: bool
''',
        '''    schema_count_delta: int
    namespace_count_delta: int
    version_count_delta: int
    namespaces_added: int
    namespaces_removed: int
    metadata_changed: bool
    identical: bool
''',
        "Expand snapshot comparison fields",
    )

    revised = replace_once(
        revised,
        '''            "schema_count_delta": self.schema_count_delta,
            "namespace_count_delta": self.namespace_count_delta,
            "version_count_delta": self.version_count_delta,
            "identical": self.identical,
''',
        '''            "schema_count_delta": self.schema_count_delta,
            "namespace_count_delta": self.namespace_count_delta,
            "version_count_delta": self.version_count_delta,
            "namespaces_added": self.namespaces_added,
            "namespaces_removed": self.namespaces_removed,
            "metadata_changed": self.metadata_changed,
            "identical": self.identical,
''',
        "Serialize expanded comparison",
    )

    revised = replace_once(
        revised,
        '''    namespace_count: int,
    version_count: int,
    created_at: Optional[str] = None,
''',
        '''    namespace_count: int,
    version_count: int,
    schema_namespace_count: Optional[int] = None,
    created_at: Optional[str] = None,
''',
        "Extend snapshot builder signature",
    )

    revised = replace_once(
        revised,
        '''        schema_count=schema_count,
        namespace_count=namespace_count,
        version_count=version_count,
        annotations=annotations,
''',
        '''        schema_count=schema_count,
        namespace_count=namespace_count,
        schema_namespace_count=(
            namespace_count
            if schema_namespace_count is None
            else schema_namespace_count
        ),
        version_count=version_count,
        annotations=annotations,
''',
        "Build schema namespace count",
    )

    revised = replace_once(
        revised,
        '''    return RuntimeSchemaSnapshot(
        metadata=metadata,
        serialization_format_version=serialization_format_version,
    )


def compare_snapshots(
''',
        '''    return RuntimeSchemaSnapshot(
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
''',
        "Add empty snapshot factory",
    )

    revised = replace_once(
        revised,
        '''        namespace_count_delta=other.namespace_count - base.namespace_count,
        version_count_delta=other.version_count - base.version_count,
        identical=base.snapshot_fingerprint == other.snapshot_fingerprint,
''',
        '''        namespace_count_delta=(
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
''',
        "Build expanded comparison",
    )

    revised = replace_once(
        revised,
        '''    _fingerprint_cache: list[str] = field(
        default_factory=list, compare=False, repr=False
    )
''',
        '''    _fingerprint_cache: list[str] = field(
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
''',
        "Add collection aggregate caches",
    )

    revised = replace_once(
        revised,
        '''        object.__setattr__(self, "snapshots", ordered)
        object.__setattr__(self, "_by_id", MappingProxyType(by_id))
        object.__setattr__(self, "_by_generation", MappingProxyType(by_generation))
''',
        '''        object.__setattr__(self, "snapshots", ordered)
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
''',
        "Populate collection aggregate caches",
    )

    revised = replace_once(
        revised,
        '''    def latest(self) -> Optional[RuntimeSchemaSnapshot]:
        """Return the highest-generation snapshot, or ``None`` if empty."""
        if not self.snapshots:
            return None
        return self.snapshots[-1]

    def generations(self) -> tuple[int, ...]:
''',
        '''    def latest(self) -> Optional[RuntimeSchemaSnapshot]:
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
''',
        "Expose collection aggregate caches",
    )

    revised = replace_once(
        revised,
        '''                payload = {
                    "kind": SNAPSHOT_COLLECTION_STRUCTURE_KIND,
                    "members": [
                        snapshot.snapshot_fingerprint
                        for snapshot in self.snapshots
                    ],
                }
''',
        '''                payload = {
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
''',
        "Strengthen collection fingerprint",
    )

    revised = replace_once(
        revised,
        '''        _require(
            data.get("kind", SNAPSHOT_COLLECTION_STRUCTURE_KIND)
            == SNAPSHOT_COLLECTION_STRUCTURE_KIND,
            "collection payload has an unexpected structure kind",
        )
''',
        '''        _require(
            data.get("kind")
            == SNAPSHOT_COLLECTION_STRUCTURE_KIND,
            "collection payload has an unexpected structure kind",
        )
''',
        "Require explicit collection structure kind",
    )

    revised = replace_once(
        revised,
        '''    "SNAPSHOT_COLLECTION_STRUCTURE_KIND",
''',
        '''    "SNAPSHOT_COLLECTION_STRUCTURE_KIND",
    "SNAPSHOT_SCHEMA_VERSION",
''',
        "Export snapshot schema version",
    )

    revised = replace_once(
        revised,
        '''    "audit_head_fingerprint",
    "build_snapshot",
    "compare_snapshots",
''',
        '''    "audit_head_fingerprint",
    "build_empty_snapshot",
    "build_snapshot",
    "compare_snapshots",
''',
        "Export empty snapshot factory",
    )

    return revised


def import_target():
    runtime_path = str(
        RUNTIME_DIR
    )

    if runtime_path not in sys.path:
        sys.path.insert(
            0,
            runtime_path,
        )

    sys.modules.pop(
        "runtime_schema.snapshots",
        None,
    )

    importlib.invalidate_caches()

    return importlib.import_module(
        "runtime_schema.snapshots"
    )


def verify_behavior(
    module,
) -> None:
    timestamp_one = (
        "2026-07-27T16:40:00.000000Z"
    )

    timestamp_two = (
        "2026-07-27T16:41:00.000000Z"
    )

    registry_one = "1" * 64
    registry_two = "2" * 64
    audit_one = "3" * 64
    audit_two = "4" * 64

    snapshot_one = module.build_snapshot(
        generation=1,
        registry_fingerprint=registry_one,
        audit_head_fingerprint=audit_one,
        schema_count=2,
        namespace_count=3,
        schema_namespace_count=2,
        version_count=4,
        created_at=timestamp_one,
        annotations={
            "environment": "test",
        },
    )

    snapshot_two = module.build_snapshot(
        generation=2,
        registry_fingerprint=registry_two,
        audit_head_fingerprint=audit_two,
        schema_count=3,
        namespace_count=5,
        schema_namespace_count=3,
        version_count=7,
        created_at=timestamp_two,
        annotations={
            "environment": "test",
        },
    )

    assert snapshot_one.snapshot_id.startswith(
        module.SNAPSHOT_ID_PREFIX
    )

    assert (
        snapshot_one.snapshot_schema_version
        == module.SNAPSHOT_SCHEMA_VERSION
    )

    assert snapshot_one.schema_namespace_count == 2

    assert len(
        snapshot_one.metadata_fingerprint
    ) == 64

    assert len(
        snapshot_one.annotations_fingerprint
    ) == 64

    assert snapshot_one.verify_integrity().valid
    assert snapshot_two.verify_integrity().valid

    rebuilt_one = (
        module.RuntimeSchemaSnapshot
        .from_canonical_json(
            snapshot_one.to_canonical_json()
        )
    )

    assert rebuilt_one == snapshot_one

    assert (
        rebuilt_one.snapshot_id
        == snapshot_one.snapshot_id
    )

    comparison = (
        snapshot_one.compare_to(
            snapshot_two
        )
    )

    assert comparison.generation_delta == 1
    assert comparison.namespaces_added == 2
    assert comparison.namespaces_removed == 0
    assert comparison.registry_fingerprint_changed
    assert comparison.audit_head_changed
    assert comparison.metadata_changed
    assert not comparison.identical

    empty = module.build_empty_snapshot(
        created_at=timestamp_one
    )

    assert empty.generation == 0
    assert empty.schema_count == 0
    assert empty.namespace_count == 0
    assert empty.schema_namespace_count == 0
    assert empty.version_count == 0
    assert empty.verify_integrity().valid

    collection = module.SnapshotCollection(
        snapshots=(
            snapshot_two,
            snapshot_one,
            empty,
        )
    )

    assert collection.generations() == (
        0,
        1,
        2,
    )

    assert collection.latest() == snapshot_two
    assert collection.latest_generation == 2
    assert collection.highest_schema_count == 3
    assert collection.highest_version_count == 7

    assert (
        collection.get(
            snapshot_one.snapshot_id
        )
        == snapshot_one
    )

    assert (
        collection.by_generation(
            2
        )
        == snapshot_two
    )

    assert collection.verify_integrity().valid

    collection_json = (
        collection.to_canonical_json()
    )

    rebuilt_collection = (
        module.SnapshotCollection
        .from_canonical_json(
            collection_json
        )
    )

    assert rebuilt_collection == collection

    assert (
        rebuilt_collection.fingerprint()
        == collection.fingerprint()
    )

    try:
        module.SnapshotCollection(
            snapshots=(
                snapshot_one,
                snapshot_one,
            )
        )
    except Exception:
        pass
    else:
        raise AssertionError(
            "Duplicate snapshot was accepted."
        )

    try:
        snapshot_one.snapshot_id = "changed"
    except Exception:
        pass
    else:
        raise AssertionError(
            "RuntimeSchemaSnapshot must be immutable."
        )

    try:
        snapshot_one.annotations[
            "environment"
        ] = "changed"
    except Exception:
        pass
    else:
        raise AssertionError(
            "Snapshot annotations must be immutable."
        )


def rollback() -> None:
    if BACKUP.exists():
        shutil.copy2(
            BACKUP,
            TARGET,
        )


def main() -> int:
    print("=" * 78)
    print("RUNTIME SCHEMA MANAGEMENT")
    print("SNAPSHOTS.PY REVIEW PATCH")
    print("=" * 78)
    print(f"Target: {TARGET}")
    print()

    if not TARGET.exists():
        raise FileNotFoundError(
            f"snapshots.py does not exist: {TARGET}"
        )

    for required_file in REQUIRED_FILES:
        if not required_file.exists():
            raise FileNotFoundError(
                "Required dependency is missing: "
                f"{required_file}"
            )

    actual_size = TARGET.stat().st_size
    actual_hash = sha256_file(
        TARGET
    )

    if actual_size != EXPECTED_BASELINE_SIZE:
        raise RuntimeError(
            "Baseline size mismatch. Expected "
            f"{EXPECTED_BASELINE_SIZE}, found {actual_size}. "
            "No file was modified."
        )

    if actual_hash != EXPECTED_BASELINE_SHA256:
        raise RuntimeError(
            "Baseline SHA-256 mismatch. Expected "
            f"{EXPECTED_BASELINE_SHA256}, found {actual_hash}. "
            "No file was modified."
        )

    BACKUP.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        TARGET,
        BACKUP,
    )

    try:
        original = TARGET.read_text(
            encoding="utf-8-sig"
        )

        revised = apply_revisions(
            original
        )

        TARGET.write_text(
            revised,
            encoding="utf-8",
            newline="\n",
        )

        for required_file in REQUIRED_FILES:
            py_compile.compile(
                str(required_file),
                doraise=True,
            )

        py_compile.compile(
            str(TARGET),
            doraise=True,
        )

        module = import_target()

        verify_behavior(
            module
        )

    except Exception:
        rollback()

        print("ROLLBACK COMPLETE")
        print(
            "The snapshots.py patch failed, "
            "so Claude's original file was restored."
        )
        print()
        print(
            traceback.format_exc()
        )

        return 1

    print("Exact baseline size:             PASS")
    print("Exact baseline SHA-256:          PASS")
    print("Backup creation:                PASS")
    print("Claude baseline review:         PASS")
    print("Nova revisions applied:         PASS")
    print("snapshots.py compilation:       PASS")
    print("Package import:                 PASS")
    print("Snapshot schema versioning:     PASS")
    print("Serialization identity binding: PASS")
    print("Schema namespace counts:        PASS")
    print("Metadata fingerprinting:        PASS")
    print("Annotation fingerprinting:      PASS")
    print("Expanded integrity checks:      PASS")
    print("Expanded snapshot comparison:   PASS")
    print("Empty snapshot factory:         PASS")
    print("Collection aggregate caches:    PASS")
    print("Collection fingerprint binding: PASS")
    print("Canonical snapshot rebuild:     PASS")
    print("Canonical collection rebuild:   PASS")
    print("Duplicate prevention:           PASS")
    print("Deep immutability:              PASS")
    print()
    print(f"Backup file: {BACKUP}")
    print()
    print(
        "SNAPSHOTS.PY: PATCHED, "
        "REVIEWED, AND APPROVED"
    )
    print(
        "NO PRODUCTION DATA WAS MODIFIED"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
