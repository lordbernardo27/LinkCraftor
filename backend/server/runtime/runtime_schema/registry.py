# -*- coding: utf-8 -*-
"""Central in-memory Runtime Schema Registry.

The registry composes the reviewed Runtime Schema Management components into
one business-logic-agnostic, thread-safe, deterministic implementation of
``RuntimeSchemaRegistryPort``.

All mutations are transactional in memory. Before a mutation begins, the
registry captures its complete internal state, including namespace,
ownership, audit, definition, lifecycle-policy, index, and generation state.
Any exception restores that state before it is re-raised.

The module performs no filesystem, database, network, or external persistence
operations.
"""

from __future__ import annotations

import copy
import threading
from dataclasses import dataclass
from typing import Any, Mapping

from .audit import AuditLog
from .change_detection import ChangeDetector
from .compatibility import CompatibilityChecker
from .definitions import SchemaDefinition
from .deprecation import (
    DeprecationPolicy,
    require_legal_transition,
)
from .fingerprint import (
    is_sha256_hex,
    schema_id_from_coordinate,
)
from .namespaces import (
    RESERVED_RUNTIME_PREFIX,
    NamespaceManager,
    is_reserved_namespace,
)
from .ownership import (
    OwnershipLedger,
    SchemaOwner,
)
from .ports import (
    ActorId,
    CanonicalMapping,
    Fingerprint,
    Namespace,
    OwnerId,
    RuntimeSchemaRegistryPort,
    SchemaName,
    VersionString,
)
from .serialization import structure_fingerprint
from .snapshots import build_snapshot
from .types import (
    AuditAction,
    OwnerKind,
    SchemaLifecycleState,
    SchemaRegistryError,
    is_valid_identifier,
)
from .versioning import (
    SchemaVersion,
    satisfies_required_bump,
)


REGISTRY_STRUCTURE_KIND = "runtime.schema.registry"
REGISTRY_CONTRACT_VERSION = "1.0.0"


def _require_non_empty(
    value: object,
    field_name: str,
) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
    ):
        raise SchemaRegistryError(
            f"{field_name} must be a non-empty string"
        )

    return value.strip()


def _require_non_negative_int(
    value: object,
    field_name: str,
) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
    ):
        raise SchemaRegistryError(
            f"{field_name} must be a non-negative integer"
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class RegistryRegistrationResult:
    """Immutable evidence of one successful schema registration."""

    schema_id: str
    coordinate: str
    namespace: str
    name: str
    version: str
    content_fingerprint: str
    record_fingerprint: str
    lifecycle_state: str
    first_version: bool
    change_class: str | None
    required_version_bump: str | None
    compatibility_fingerprint: str
    audit_sequence: int
    audit_record_hash: str
    generation: int
    registry_fingerprint: str

    def __post_init__(self) -> None:
        for field_name in (
            "schema_id",
            "coordinate",
            "namespace",
            "name",
            "version",
            "lifecycle_state",
            "compatibility_fingerprint",
            "audit_record_hash",
            "registry_fingerprint",
        ):
            _require_non_empty(
                getattr(self, field_name),
                field_name,
            )

        for field_name in (
            "content_fingerprint",
            "record_fingerprint",
            "compatibility_fingerprint",
            "audit_record_hash",
            "registry_fingerprint",
        ):
            if not is_sha256_hex(
                getattr(self, field_name)
            ):
                raise SchemaRegistryError(
                    f"{field_name} must be a SHA-256 digest"
                )

        _require_non_negative_int(
            self.audit_sequence,
            "audit_sequence",
        )

        _require_non_negative_int(
            self.generation,
            "generation",
        )

        if not isinstance(
            self.first_version,
            bool,
        ):
            raise SchemaRegistryError(
                "first_version must be a boolean"
            )

    @property
    def fingerprint(self) -> str:
        return structure_fingerprint(
            self.to_canonical_dict()
        )

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "schema_id": self.schema_id,
            "coordinate": self.coordinate,
            "namespace": self.namespace,
            "name": self.name,
            "version": self.version,
            "content_fingerprint": (
                self.content_fingerprint
            ),
            "record_fingerprint": (
                self.record_fingerprint
            ),
            "lifecycle_state": (
                self.lifecycle_state
            ),
            "first_version": (
                self.first_version
            ),
            "change_class": (
                self.change_class
            ),
            "required_version_bump": (
                self.required_version_bump
            ),
            "compatibility_fingerprint": (
                self.compatibility_fingerprint
            ),
            "audit_sequence": (
                self.audit_sequence
            ),
            "audit_record_hash": (
                self.audit_record_hash
            ),
            "generation": self.generation,
            "registry_fingerprint": (
                self.registry_fingerprint
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class RegistryLifecycleResult:
    """Immutable evidence of one successful lifecycle transition."""

    coordinate: str
    previous_state: str
    new_state: str
    deprecation_policy: Mapping[str, Any] | None
    audit_sequence: int
    audit_record_hash: str
    generation: int
    registry_fingerprint: str

    def __post_init__(self) -> None:
        for field_name in (
            "coordinate",
            "previous_state",
            "new_state",
            "audit_record_hash",
            "registry_fingerprint",
        ):
            _require_non_empty(
                getattr(self, field_name),
                field_name,
            )

        if not is_sha256_hex(
            self.audit_record_hash
        ):
            raise SchemaRegistryError(
                "audit_record_hash must be a SHA-256 digest"
            )

        if not is_sha256_hex(
            self.registry_fingerprint
        ):
            raise SchemaRegistryError(
                "registry_fingerprint must be a SHA-256 digest"
            )

        _require_non_negative_int(
            self.audit_sequence,
            "audit_sequence",
        )

        _require_non_negative_int(
            self.generation,
            "generation",
        )

        if self.deprecation_policy is not None:
            object.__setattr__(
                self,
                "deprecation_policy",
                copy.deepcopy(
                    dict(self.deprecation_policy)
                ),
            )

    @property
    def fingerprint(self) -> str:
        return structure_fingerprint(
            self.to_canonical_dict()
        )

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "coordinate": self.coordinate,
            "previous_state": (
                self.previous_state
            ),
            "new_state": self.new_state,
            "deprecation_policy": (
                copy.deepcopy(
                    dict(self.deprecation_policy)
                )
                if self.deprecation_policy is not None
                else None
            ),
            "audit_sequence": (
                self.audit_sequence
            ),
            "audit_record_hash": (
                self.audit_record_hash
            ),
            "generation": self.generation,
            "registry_fingerprint": (
                self.registry_fingerprint
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class RegistryMeasurements:
    """Immutable registry measurements used by snapshots."""

    generation: int
    registry_fingerprint: str
    audit_head_fingerprint: str
    audit_generation: int
    namespace_count: int
    schema_namespace_count: int
    schema_count: int
    version_count: int

    def __post_init__(self) -> None:
        for field_name in (
            "generation",
            "audit_generation",
            "namespace_count",
            "schema_namespace_count",
            "schema_count",
            "version_count",
        ):
            _require_non_negative_int(
                getattr(self, field_name),
                field_name,
            )

        for field_name in (
            "registry_fingerprint",
            "audit_head_fingerprint",
        ):
            if not is_sha256_hex(
                getattr(self, field_name)
            ):
                raise SchemaRegistryError(
                    f"{field_name} must be a SHA-256 digest"
                )

        if (
            self.schema_namespace_count
            > self.namespace_count
        ):
            raise SchemaRegistryError(
                "schema_namespace_count cannot exceed namespace_count"
            )

        if self.version_count < self.schema_count:
            raise SchemaRegistryError(
                "version_count cannot be smaller than schema_count"
            )

    @property
    def fingerprint(self) -> str:
        return structure_fingerprint(
            self.to_canonical_dict()
        )

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "generation": self.generation,
            "registry_fingerprint": (
                self.registry_fingerprint
            ),
            "audit_head_fingerprint": (
                self.audit_head_fingerprint
            ),
            "audit_generation": (
                self.audit_generation
            ),
            "namespace_count": (
                self.namespace_count
            ),
            "schema_namespace_count": (
                self.schema_namespace_count
            ),
            "schema_count": (
                self.schema_count
            ),
            "version_count": (
                self.version_count
            ),
        }

    def as_snapshot(
        self,
        *,
        annotations: Mapping[str, Any] | None = None,
    ):
        return build_snapshot(
            generation=self.generation,
            registry_fingerprint=(
                self.registry_fingerprint
            ),
            audit_head_fingerprint=(
                self.audit_head_fingerprint
            ),
            schema_count=self.schema_count,
            namespace_count=self.namespace_count,
            schema_namespace_count=(
                self.schema_namespace_count
            ),
            version_count=self.version_count,
            annotations=(
                annotations
                if annotations is not None
                else {}
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
    order=True,
)
class RegistryIntegrityIssue:
    """One immutable registry-integrity violation."""

    category: str
    subject: str
    detail: str

    def __post_init__(self) -> None:
        for field_name in (
            "category",
            "subject",
            "detail",
        ):
            _require_non_empty(
                getattr(self, field_name),
                field_name,
            )

    def to_canonical_dict(
        self,
    ) -> dict[str, str]:
        return {
            "category": self.category,
            "subject": self.subject,
            "detail": self.detail,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class RegistryIntegrityReport:
    """Complete immutable registry-integrity verdict."""

    valid: bool
    complete: bool
    checked_namespaces: int
    checked_subjects: int
    checked_versions: int
    registry_generation: int
    ownership_generation: int
    audit_generation: int
    registry_fingerprint: str
    audit_valid: bool
    issues: tuple[
        RegistryIntegrityIssue,
        ...
    ]

    def __post_init__(self) -> None:
        for field_name in (
            "checked_namespaces",
            "checked_subjects",
            "checked_versions",
            "registry_generation",
            "ownership_generation",
            "audit_generation",
        ):
            _require_non_negative_int(
                getattr(self, field_name),
                field_name,
            )

        if not is_sha256_hex(
            self.registry_fingerprint
        ):
            raise SchemaRegistryError(
                "registry_fingerprint must be a SHA-256 digest"
            )

        object.__setattr__(
            self,
            "issues",
            tuple(self.issues),
        )

        expected_valid = (
            self.complete
            and self.audit_valid
            and not self.issues
        )

        if self.valid != expected_valid:
            raise SchemaRegistryError(
                "valid flag is inconsistent"
            )

    @property
    def fingerprint(self) -> str:
        return structure_fingerprint(
            self.to_canonical_dict()
        )

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "complete": self.complete,
            "checked_namespaces": (
                self.checked_namespaces
            ),
            "checked_subjects": (
                self.checked_subjects
            ),
            "checked_versions": (
                self.checked_versions
            ),
            "registry_generation": (
                self.registry_generation
            ),
            "ownership_generation": (
                self.ownership_generation
            ),
            "audit_generation": (
                self.audit_generation
            ),
            "registry_fingerprint": (
                self.registry_fingerprint
            ),
            "audit_valid": self.audit_valid,
            "issues": [
                issue.to_canonical_dict()
                for issue in self.issues
            ],
            "issue_count": len(
                self.issues
            ),
        }


class RuntimeSchemaRegistry(
    RuntimeSchemaRegistryPort
):
    """Thread-safe transactional in-memory Runtime Schema Registry."""

    def __init__(
        self,
    ) -> None:
        self._lock = threading.RLock()

        self._namespaces = (
            NamespaceManager()
        )

        self._ownership = (
            OwnershipLedger()
        )

        self._audit = (
            AuditLog()
        )

        self._compatibility = (
            CompatibilityChecker()
        )

        self._definitions: dict[
            str,
            dict[str, SchemaDefinition],
        ] = {}

        self._schema_ids: dict[
            str,
            str,
        ] = {}

        self._deprecation_policies: dict[
            str,
            DeprecationPolicy,
        ] = {}

        self._generation = 0

    @staticmethod
    def _subject(
        namespace: str,
        name: str,
    ) -> str:
        return f"{namespace}/{name}"

    @staticmethod
    def _coerce_state(
        value: SchemaLifecycleState | str,
    ) -> SchemaLifecycleState:
        if isinstance(
            value,
            SchemaLifecycleState,
        ):
            return value

        try:
            return SchemaLifecycleState(
                value
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise SchemaRegistryError(
                "invalid lifecycle state"
            ) from exc

    def _sorted_versions(
        self,
        versions: Mapping[
            str,
            SchemaDefinition,
        ],
    ) -> tuple[
        SchemaDefinition,
        ...
    ]:
        return tuple(
            versions[key]
            for key in sorted(
                versions,
                key=lambda version: (
                    SchemaVersion.parse(
                        version
                    )
                ),
            )
        )

    def _all_definitions(
        self,
    ) -> tuple[
        SchemaDefinition,
        ...
    ]:
        result: list[
            SchemaDefinition
        ] = []

        for subject in sorted(
            self._definitions
        ):
            result.extend(
                self._sorted_versions(
                    self._definitions[
                        subject
                    ]
                )
            )

        return tuple(
            result
        )

    def _capture_transaction_state(
        self,
    ) -> dict[str, Any]:
        """Capture all mutable subsystem state while holding the registry lock."""
        return {
            "definitions": {
                subject: dict(versions)
                for subject, versions
                in self._definitions.items()
            },
            "schema_ids": dict(
                self._schema_ids
            ),
            "deprecation_policies": dict(
                self._deprecation_policies
            ),
            "generation": (
                self._generation
            ),
            "namespace_records": dict(
                self._namespaces._namespaces
            ),
            "ownership_current": dict(
                self._ownership._current
            ),
            "ownership_history": list(
                self._ownership._history
            ),
            "ownership_subject_history": {
                key: list(value)
                for key, value in getattr(
                    self._ownership,
                    "_subject_history",
                    {},
                ).items()
            },
            "ownership_owner_subjects": {
                key: set(value)
                for key, value in getattr(
                    self._ownership,
                    "_owner_subjects",
                    {},
                ).items()
            },
            "ownership_generation": getattr(
                self._ownership,
                "_generation",
                len(
                    self._ownership._history
                ),
            ),
            "audit_records": list(
                self._audit._records
            ),
            "audit_subject_index": {
                key: list(value)
                for key, value in self._audit._subject_index.items()
            },
            "audit_generation": (
                self._audit._generation
            ),
        }

    def _restore_transaction_state(
        self,
        state: Mapping[str, Any],
    ) -> None:
        self._definitions = {
            subject: dict(versions)
            for subject, versions
            in state[
                "definitions"
            ].items()
        }

        self._schema_ids = dict(
            state[
                "schema_ids"
            ]
        )

        self._deprecation_policies = dict(
            state[
                "deprecation_policies"
            ]
        )

        self._generation = state[
            "generation"
        ]

        self._namespaces._namespaces = dict(
            state[
                "namespace_records"
            ]
        )

        self._ownership._current = dict(
            state[
                "ownership_current"
            ]
        )

        self._ownership._history = list(
            state[
                "ownership_history"
            ]
        )

        if hasattr(
            self._ownership,
            "_subject_history",
        ):
            self._ownership._subject_history = (
                copy.deepcopy(
                    state[
                        "ownership_subject_history"
                    ]
                )
            )

        if hasattr(
            self._ownership,
            "_owner_subjects",
        ):
            self._ownership._owner_subjects = (
                copy.deepcopy(
                    state[
                        "ownership_owner_subjects"
                    ]
                )
            )

        if hasattr(
            self._ownership,
            "_generation",
        ):
            self._ownership._generation = (
                state[
                    "ownership_generation"
                ]
            )

        self._audit._records = list(
            state[
                "audit_records"
            ]
        )

        self._audit._subject_index = (
            copy.deepcopy(
                state[
                    "audit_subject_index"
                ]
            )
        )

        self._audit._generation = state[
            "audit_generation"
        ]

    def register_namespace(
        self,
        namespace: Namespace,
        owner_id: OwnerId,
        actor: ActorId,
        *,
        runtime_actor: bool = False,
        description: str = "",
    ) -> CanonicalMapping:
        if not is_valid_identifier(
            actor
        ):
            raise SchemaRegistryError(
                f"invalid actor: {actor!r}"
            )

        if (
            actor != owner_id
            and not runtime_actor
        ):
            raise SchemaRegistryError(
                "namespace registration actor must "
                "be the namespace owner"
            )

        with self._lock:
            transaction = (
                self._capture_transaction_state()
            )

            try:
                record = (
                    self._namespaces
                    .register_namespace(
                        namespace,
                        owner_id,
                        runtime_actor=(
                            runtime_actor
                        ),
                        description=description,
                    )
                )

                audit = self._audit.append(
                    actor=actor,
                    action=(
                        AuditAction
                        .NAMESPACE_REGISTERED
                    ),
                    subject=namespace,
                    detail=(
                        "namespace registered"
                    ),
                    after_fingerprint=(
                        structure_fingerprint(
                            record
                            .to_canonical_dict()
                        )
                    ),
                )

                self._generation += 1

                payload = (
                    record.to_canonical_dict()
                )

                payload.update(
                    {
                        "audit_sequence": (
                            audit.sequence
                        ),
                        "audit_record_hash": (
                            audit.record_hash
                        ),
                        "generation": (
                            self._generation
                        ),
                        "registry_fingerprint": (
                            self.registry_fingerprint()
                        ),
                    }
                )

                return payload

            except Exception:
                self._restore_transaction_state(
                    transaction
                )

                raise

    def register_schema(
        self,
        definition: CanonicalMapping,
        actor: ActorId,
        *,
        runtime_actor: bool = False,
    ) -> CanonicalMapping:
        if not is_valid_identifier(
            actor
        ):
            raise SchemaRegistryError(
                f"invalid actor: {actor!r}"
            )

        try:
            schema = (
                SchemaDefinition
                .from_canonical_dict(
                    definition
                )
            )
        except Exception as exc:
            raise SchemaRegistryError(
                f"invalid schema definition: {exc}"
            ) from exc

        with self._lock:
            namespace_record = (
                self._namespaces
                .authorize_schema_namespace(
                    schema.namespace,
                    actor_id=actor,
                    runtime_actor=(
                        runtime_actor
                    ),
                )
            )

            if (
                actor
                != namespace_record.owner_id
                and not runtime_actor
            ):
                raise SchemaRegistryError(
                    "actor is not authorized by "
                    "the namespace owner"
                )

            if (
                is_reserved_namespace(
                    schema.namespace
                )
                and not runtime_actor
            ):
                raise SchemaRegistryError(
                    "reserved runtime schemas require "
                    "runtime_actor=True"
                )

            subject = self._subject(
                schema.namespace,
                schema.name,
            )

            versions = (
                self._definitions.get(
                    subject,
                    {},
                )
            )

            version_text = str(
                schema.version
            )

            if version_text in versions:
                raise SchemaRegistryError(
                    "duplicate schema version: "
                    + schema.coordinate()
                )

            if (
                schema.schema_id
                in self._schema_ids
            ):
                raise SchemaRegistryError(
                    "duplicate schema_id: "
                    + schema.schema_id
                )

            chain = self._sorted_versions(
                versions
            )

            first_version = not chain

            current_owner = (
                self._ownership
                .current_owner(
                    subject
                )
            )

            if first_version:
                if (
                    actor != schema.owner_id
                    and not runtime_actor
                ):
                    raise SchemaRegistryError(
                        "first schema registration actor "
                        "must be the schema owner"
                    )

                if (
                    schema.owner_id
                    != namespace_record.owner_id
                    and not runtime_actor
                ):
                    raise SchemaRegistryError(
                        "first schema owner must match "
                        "the namespace owner"
                    )
            else:
                if current_owner is None:
                    raise SchemaRegistryError(
                        "schema subject has versions "
                        "but no ownership record"
                    )

                if (
                    schema.owner_id
                    != current_owner.owner_id
                ):
                    raise SchemaRegistryError(
                        "schema owner does not match "
                        "the current subject owner"
                    )

                if (
                    actor
                    != current_owner.owner_id
                    and not runtime_actor
                ):
                    raise SchemaRegistryError(
                        "actor is not authorized by "
                        "the schema subject owner"
                    )

                if (
                    schema.version
                    <= chain[-1].version
                ):
                    raise SchemaRegistryError(
                        "schema version must strictly "
                        "succeed the latest version"
                    )

            compatibility = (
                self._compatibility.check(
                    schema,
                    chain,
                )
            )

            if not compatibility.complete:
                raise SchemaRegistryError(
                    "compatibility analysis is incomplete"
                )

            if not compatibility.compatible:
                raise SchemaRegistryError(
                    "compatibility check failed: "
                    + "; ".join(
                        (
                            violation.path
                            + ": "
                            + violation.detail
                        )
                        for violation
                        in compatibility.violations
                    )
                )

            change = None

            if chain:
                change = (
                    ChangeDetector.detect(
                        chain[-1],
                        schema,
                    )
                )

                if not change.complete:
                    raise SchemaRegistryError(
                        "change detection is incomplete"
                    )

                if (
                    not change.identical
                    and not satisfies_required_bump(
                        chain[-1].version,
                        schema.version,
                        change.overall_class,
                    )
                ):
                    raise SchemaRegistryError(
                        f"{change.overall_class.value} "
                        "change requires at least a "
                        f"{change.required_version_bump.value} "
                        "version bump"
                    )

            transaction = (
                self._capture_transaction_state()
            )

            try:
                self._definitions.setdefault(
                    subject,
                    {},
                )[version_text] = schema

                self._schema_ids[
                    schema.schema_id
                ] = schema.coordinate()

                if first_version:
                    owner = SchemaOwner(
                        owner_id=(
                            schema.owner_id
                        ),
                        owner_kind=(
                            OwnerKind.RUNTIME
                            if runtime_actor
                            else OwnerKind.SERVICE
                        ),
                    )

                    self._ownership.assign(
                        subject,
                        owner,
                        actor,
                        reason=(
                            "initial ownership on "
                            "first schema registration"
                        ),
                        runtime_actor=(
                            runtime_actor
                        ),
                    )

                before_fingerprint = (
                    chain[-1]
                    .content_fingerprint()
                    if chain
                    else None
                )

                audit = self._audit.append(
                    actor=actor,
                    action=(
                        AuditAction
                        .SCHEMA_REGISTERED
                    ),
                    subject=(
                        schema.coordinate()
                    ),
                    detail=(
                        "schema version registered"
                    ),
                    before_fingerprint=(
                        before_fingerprint
                    ),
                    after_fingerprint=(
                        schema
                        .content_fingerprint()
                    ),
                )

                self._generation += 1

                registry_fingerprint = (
                    self.registry_fingerprint()
                )

                return (
                    RegistryRegistrationResult(
                        schema_id=(
                            schema.schema_id
                        ),
                        coordinate=(
                            schema.coordinate()
                        ),
                        namespace=(
                            schema.namespace
                        ),
                        name=schema.name,
                        version=version_text,
                        content_fingerprint=(
                            schema
                            .content_fingerprint()
                        ),
                        record_fingerprint=(
                            schema
                            .record_fingerprint()
                        ),
                        lifecycle_state=(
                            schema
                            .lifecycle_state
                            .value
                        ),
                        first_version=(
                            first_version
                        ),
                        change_class=(
                            change
                            .overall_class
                            .value
                            if change is not None
                            else None
                        ),
                        required_version_bump=(
                            change
                            .required_version_bump
                            .value
                            if change is not None
                            else None
                        ),
                        compatibility_fingerprint=(
                            compatibility
                            .fingerprint
                        ),
                        audit_sequence=(
                            audit.sequence
                        ),
                        audit_record_hash=(
                            audit.record_hash
                        ),
                        generation=(
                            self._generation
                        ),
                        registry_fingerprint=(
                            registry_fingerprint
                        ),
                    ).to_canonical_dict()
                )

            except Exception:
                self._restore_transaction_state(
                    transaction
                )

                raise

    def get_schema(
        self,
        namespace: Namespace,
        name: SchemaName,
        version: VersionString | None = None,
        *,
        include_inactive: bool = False,
    ) -> CanonicalMapping | None:
        with self._lock:
            subject = self._subject(
                namespace,
                name,
            )

            versions = (
                self._definitions.get(
                    subject
                )
            )

            if not versions:
                return None

            if version is not None:
                try:
                    wanted = str(
                        SchemaVersion.parse(
                            str(version)
                        )
                    )
                except Exception as exc:
                    raise SchemaRegistryError(
                        "invalid schema version"
                    ) from exc

                definition = (
                    versions.get(
                        wanted
                    )
                )

                if definition is None:
                    return None

                if (
                    not include_inactive
                    and definition.lifecycle_state
                    is not SchemaLifecycleState.ACTIVE
                ):
                    return None

                return (
                    definition
                    .to_canonical_dict()
                )

            eligible = [
                definition
                for definition
                in self._sorted_versions(
                    versions
                )
                if (
                    include_inactive
                    or definition.lifecycle_state
                    is SchemaLifecycleState.ACTIVE
                )
            ]

            if not eligible:
                return None

            return (
                eligible[-1]
                .to_canonical_dict()
            )

    def require_schema(
        self,
        namespace: Namespace,
        name: SchemaName,
        version: VersionString | None = None,
        *,
        include_inactive: bool = False,
    ) -> CanonicalMapping:
        result = self.get_schema(
            namespace,
            name,
            version,
            include_inactive=(
                include_inactive
            ),
        )

        if result is None:
            coordinate = (
                f"{namespace}/{name}"
                if version is None
                else (
                    f"{namespace}/{name}"
                    f"@{version}"
                )
            )

            raise SchemaRegistryError(
                "schema not found or inactive: "
                + coordinate
            )

        return result

    def list_schemas(
        self,
        *,
        namespace: Namespace | None = None,
        name: SchemaName | None = None,
        lifecycle_state: (
            SchemaLifecycleState
            | None
        ) = None,
    ) -> tuple[
        CanonicalMapping,
        ...
    ]:
        effective_state = (
            self._coerce_state(
                lifecycle_state
            )
            if lifecycle_state
            is not None
            else None
        )

        with self._lock:
            results = []

            for definition in (
                self._all_definitions()
            ):
                if (
                    namespace is not None
                    and definition.namespace
                    != namespace
                ):
                    continue

                if (
                    name is not None
                    and definition.name
                    != name
                ):
                    continue

                if (
                    effective_state is not None
                    and definition
                    .lifecycle_state
                    is not effective_state
                ):
                    continue

                results.append(
                    definition
                    .to_canonical_dict()
                )

            return tuple(
                results
            )

    def list_versions(
        self,
        namespace: Namespace,
        name: SchemaName,
    ) -> tuple[
        CanonicalMapping,
        ...
    ]:
        with self._lock:
            versions = (
                self._definitions.get(
                    self._subject(
                        namespace,
                        name,
                    )
                )
            )

            if not versions:
                return ()

            return tuple(
                definition
                .to_canonical_dict()
                for definition
                in self._sorted_versions(
                    versions
                )
            )

    def contains(
        self,
        namespace: Namespace,
        name: SchemaName,
        version: VersionString | None = None,
    ) -> bool:
        with self._lock:
            versions = (
                self._definitions.get(
                    self._subject(
                        namespace,
                        name,
                    )
                )
            )

            if not versions:
                return False

            if version is None:
                return True

            try:
                wanted = str(
                    SchemaVersion.parse(
                        str(version)
                    )
                )
            except Exception:
                return False

            return wanted in versions

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
        if not is_valid_identifier(
            actor
        ):
            raise SchemaRegistryError(
                f"invalid actor: {actor!r}"
            )

        target_state = (
            self._coerce_state(
                new_state
            )
        )

        with self._lock:
            subject = self._subject(
                namespace,
                name,
            )

            versions = (
                self._definitions.get(
                    subject
                )
            )

            if not versions:
                raise SchemaRegistryError(
                    "schema subject not found"
                )

            try:
                wanted = str(
                    SchemaVersion.parse(
                        str(version)
                    )
                )
            except Exception as exc:
                raise SchemaRegistryError(
                    "invalid schema version"
                ) from exc

            current = versions.get(
                wanted
            )

            if current is None:
                raise SchemaRegistryError(
                    "schema version not found"
                )

            owner = (
                self._ownership
                .current_owner(
                    subject
                )
            )

            if (
                owner is None
                or actor != owner.owner_id
            ):
                raise SchemaRegistryError(
                    "actor is not the schema owner"
                )

            require_legal_transition(
                current.lifecycle_state,
                target_state,
            )

            effective_policy = None

            if (
                target_state
                is SchemaLifecycleState.DEPRECATED
            ):
                if policy is None:
                    raise SchemaRegistryError(
                        "deprecation policy is required"
                    )

                try:
                    effective_policy = (
                        DeprecationPolicy(
                            notice_period_days=(
                                policy[
                                    "notice_period_days"
                                ]
                            ),
                            deprecated_at=(
                                policy.get(
                                    "deprecated_at",
                                    "",
                                )
                            ),
                            sunset_at=(
                                policy.get(
                                    "sunset_at"
                                )
                            ),
                            replacement_coordinate=(
                                policy.get(
                                    "replacement_coordinate"
                                )
                            ),
                            enforcement=(
                                policy.get(
                                    "enforcement",
                                    "warn",
                                )
                            ),
                            reason=(
                                policy.get(
                                    "reason",
                                    "",
                                )
                            ),
                        )
                    )
                except Exception as exc:
                    raise SchemaRegistryError(
                        "invalid deprecation policy: "
                        + str(exc)
                    ) from exc

            elif policy is not None:
                raise SchemaRegistryError(
                    "deprecation policy is only valid "
                    "when entering DEPRECATED"
                )

            updated = (
                current.with_lifecycle(
                    target_state
                )
            )

            transaction = (
                self._capture_transaction_state()
            )

            try:
                versions[
                    wanted
                ] = updated

                coordinate = (
                    current.coordinate()
                )

                if effective_policy is None:
                    self._deprecation_policies.pop(
                        coordinate,
                        None,
                    )
                else:
                    self._deprecation_policies[
                        coordinate
                    ] = effective_policy

                audit = self._audit.append(
                    actor=actor,
                    action=(
                        AuditAction
                        .LIFECYCLE_CHANGED
                    ),
                    subject=coordinate,
                    detail=(
                        current
                        .lifecycle_state
                        .value
                        + " -> "
                        + target_state.value
                    ),
                    before_fingerprint=(
                        current
                        .record_fingerprint()
                    ),
                    after_fingerprint=(
                        updated
                        .record_fingerprint()
                    ),
                )

                self._generation += 1

                return (
                    RegistryLifecycleResult(
                        coordinate=coordinate,
                        previous_state=(
                            current
                            .lifecycle_state
                            .value
                        ),
                        new_state=(
                            target_state.value
                        ),
                        deprecation_policy=(
                            effective_policy
                            .to_canonical_dict()
                            if effective_policy
                            is not None
                            else None
                        ),
                        audit_sequence=(
                            audit.sequence
                        ),
                        audit_record_hash=(
                            audit.record_hash
                        ),
                        generation=(
                            self._generation
                        ),
                        registry_fingerprint=(
                            self.registry_fingerprint()
                        ),
                    ).to_canonical_dict()
                )

            except Exception:
                self._restore_transaction_state(
                    transaction
                )

                raise

    def registry_generation(
        self,
    ) -> int:
        with self._lock:
            return self._generation

    def _registry_fingerprint_payload(
        self,
    ) -> dict[str, Any]:
        namespaces = [
            record.to_canonical_dict()
            for record
            in self._namespaces
            .list_namespaces()
        ]

        ownership_history = [
            record.to_canonical_dict()
            for record
            in self._ownership.history()
        ]

        schemas = []

        for definition in (
            self._all_definitions()
        ):
            coordinate = (
                definition.coordinate()
            )

            policy = (
                self._deprecation_policies
                .get(
                    coordinate
                )
            )

            schemas.append(
                {
                    "definition": (
                        definition
                        .to_canonical_dict()
                    ),
                    "record_fingerprint": (
                        definition
                        .record_fingerprint()
                    ),
                    "deprecation_policy": (
                        policy
                        .to_canonical_dict()
                        if policy is not None
                        else None
                    ),
                    "deprecation_policy_fingerprint": (
                        policy.fingerprint
                        if policy is not None
                        else None
                    ),
                }
            )

        return {
            "kind": (
                REGISTRY_STRUCTURE_KIND
            ),
            "contract_version": (
                REGISTRY_CONTRACT_VERSION
            ),
            "generation": (
                self._generation
            ),
            "ownership_generation": getattr(
                self._ownership,
                "generation",
                len(ownership_history),
            ),
            "audit_generation": (
                self._audit.generation
            ),
            "audit_head_hash": (
                self._audit.head_hash
            ),
            "namespaces": namespaces,
            "ownership_history": (
                ownership_history
            ),
            "schemas": schemas,
        }

    def registry_fingerprint(
        self,
    ) -> Fingerprint:
        with self._lock:
            return structure_fingerprint(
                self
                ._registry_fingerprint_payload()
            )

    def _measurements(
        self,
    ) -> RegistryMeasurements:
        namespace_records = (
            self._namespaces
            .list_namespaces()
        )

        schema_namespaces = {
            definition.namespace
            for definition
            in self._all_definitions()
        }

        return RegistryMeasurements(
            generation=self._generation,
            registry_fingerprint=(
                structure_fingerprint(
                    self
                    ._registry_fingerprint_payload()
                )
            ),
            audit_head_fingerprint=(
                self._audit.head_hash
            ),
            audit_generation=(
                self._audit.generation
            ),
            namespace_count=len(
                namespace_records
            ),
            schema_namespace_count=len(
                schema_namespaces
            ),
            schema_count=len(
                self._definitions
            ),
            version_count=sum(
                len(versions)
                for versions
                in self._definitions.values()
            ),
        )

    def registry_measurements(
        self,
    ) -> CanonicalMapping:
        with self._lock:
            return (
                self._measurements()
                .to_canonical_dict()
            )

    def capture_snapshot(
        self,
        *,
        annotations: (
            Mapping[str, Any]
            | None
        ) = None,
    ):
        """Return an immutable snapshot without storing it."""
        with self._lock:
            return self._measurements().as_snapshot(
                annotations=annotations
            )

    def verify_integrity(
        self,
    ) -> CanonicalMapping:
        with self._lock:
            issues: list[
                RegistryIntegrityIssue
            ] = []

            namespaces = {
                record.namespace: record
                for record
                in self._namespaces
                .list_namespaces()
            }

            seen_schema_ids: dict[
                str,
                str,
            ] = {}

            checked_versions = 0

            for subject in sorted(
                self._definitions
            ):
                versions = (
                    self._definitions[
                        subject
                    ]
                )

                owner = (
                    self._ownership
                    .current_owner(
                        subject
                    )
                )

                if owner is None:
                    issues.append(
                        RegistryIntegrityIssue(
                            "ownership",
                            subject,
                            "schema subject has no owner",
                        )
                    )

                previous_version = None

                for version_key in sorted(
                    versions,
                    key=lambda value: (
                        SchemaVersion.parse(
                            value
                        )
                    ),
                ):
                    checked_versions += 1

                    definition = (
                        versions[
                            version_key
                        ]
                    )

                    coordinate = (
                        definition.coordinate()
                    )

                    if (
                        str(definition.version)
                        != version_key
                    ):
                        issues.append(
                            RegistryIntegrityIssue(
                                "version_index",
                                coordinate,
                                "version index key mismatch",
                            )
                        )

                    if (
                        self._subject(
                            definition.namespace,
                            definition.name,
                        )
                        != subject
                    ):
                        issues.append(
                            RegistryIntegrityIssue(
                                "subject_index",
                                coordinate,
                                "subject index mismatch",
                            )
                        )

                    if (
                        definition.namespace
                        not in namespaces
                    ):
                        issues.append(
                            RegistryIntegrityIssue(
                                "namespace",
                                coordinate,
                                "schema namespace is not registered",
                            )
                        )

                    expected_schema_id = (
                        schema_id_from_coordinate(
                            coordinate
                        )
                    )

                    if (
                        definition.schema_id
                        != expected_schema_id
                    ):
                        issues.append(
                            RegistryIntegrityIssue(
                                "schema_id",
                                coordinate,
                                "schema_id does not match coordinate",
                            )
                        )

                    try:
                        rebuilt = (
                            SchemaDefinition
                            .from_canonical_dict(
                                definition
                                .to_canonical_dict()
                            )
                        )
                    except Exception as exc:
                        issues.append(
                            RegistryIntegrityIssue(
                                "definition_integrity",
                                coordinate,
                                str(exc),
                            )
                        )
                    else:
                        if (
                            rebuilt
                            .record_fingerprint()
                            != definition
                            .record_fingerprint()
                        ):
                            issues.append(
                                RegistryIntegrityIssue(
                                    "record_fingerprint",
                                    coordinate,
                                    "rebuilt record fingerprint mismatch",
                                )
                            )

                    if (
                        definition.schema_id
                        in seen_schema_ids
                    ):
                        issues.append(
                            RegistryIntegrityIssue(
                                "duplicate_schema_id",
                                coordinate,
                                (
                                    "also used by "
                                    + seen_schema_ids[
                                        definition
                                        .schema_id
                                    ]
                                ),
                            )
                        )
                    else:
                        seen_schema_ids[
                            definition.schema_id
                        ] = coordinate

                    if (
                        self._schema_ids.get(
                            definition.schema_id
                        )
                        != coordinate
                    ):
                        issues.append(
                            RegistryIntegrityIssue(
                                "schema_id_index",
                                coordinate,
                                "schema_id index mismatch",
                            )
                        )

                    if (
                        owner is not None
                        and definition.owner_id
                        != owner.owner_id
                    ):
                        issues.append(
                            RegistryIntegrityIssue(
                                "ownership",
                                coordinate,
                                "definition owner differs from subject owner",
                            )
                        )

                    if (
                        is_reserved_namespace(
                            definition.namespace
                        )
                        and (
                            owner is None
                            or owner.owner_kind
                            is not OwnerKind.RUNTIME
                        )
                    ):
                        issues.append(
                            RegistryIntegrityIssue(
                                "reserved_namespace",
                                coordinate,
                                (
                                    "schemas under "
                                    f"{RESERVED_RUNTIME_PREFIX}* "
                                    "must be runtime-owned"
                                ),
                            )
                        )

                    policy = (
                        self._deprecation_policies
                        .get(
                            coordinate
                        )
                    )

                    if (
                        definition.lifecycle_state
                        is SchemaLifecycleState.DEPRECATED
                        and policy is None
                    ):
                        issues.append(
                            RegistryIntegrityIssue(
                                "deprecation_policy",
                                coordinate,
                                "deprecated schema has no policy",
                            )
                        )

                    if (
                        definition.lifecycle_state
                        is not SchemaLifecycleState.DEPRECATED
                        and policy is not None
                    ):
                        issues.append(
                            RegistryIntegrityIssue(
                                "deprecation_policy",
                                coordinate,
                                "policy exists on non-deprecated schema",
                            )
                        )

                    if (
                        previous_version is not None
                        and definition.version
                        <= previous_version
                    ):
                        issues.append(
                            RegistryIntegrityIssue(
                                "version_chain",
                                coordinate,
                                "version chain is not strictly increasing",
                            )
                        )

                    previous_version = (
                        definition.version
                    )

            version_count = sum(
                len(versions)
                for versions
                in self._definitions
                .values()
            )

            if (
                len(self._schema_ids)
                != version_count
            ):
                issues.append(
                    RegistryIntegrityIssue(
                        "schema_id_index",
                        "<registry>",
                        "schema_id index size mismatch",
                    )
                )

            audit_verification = (
                self._audit.verify_chain()
            )

            if not audit_verification.valid:
                issues.append(
                    RegistryIntegrityIssue(
                        "audit_chain",
                        "<registry>",
                        audit_verification.detail,
                    )
                )

            if (
                self._generation
                != self._audit.generation
            ):
                issues.append(
                    RegistryIntegrityIssue(
                        "generation",
                        "<registry>",
                        "registry generation differs "
                        "from audit generation",
                    )
                )

            fingerprint_one = (
                structure_fingerprint(
                    self
                    ._registry_fingerprint_payload()
                )
            )

            fingerprint_two = (
                structure_fingerprint(
                    self
                    ._registry_fingerprint_payload()
                )
            )

            if (
                fingerprint_one
                != fingerprint_two
            ):
                issues.append(
                    RegistryIntegrityIssue(
                        "registry_fingerprint",
                        "<registry>",
                        "registry fingerprint is not deterministic",
                    )
                )

            ordered_issues = tuple(
                sorted(
                    issues
                )
            )

            report = RegistryIntegrityReport(
                valid=(
                    audit_verification.valid
                    and not ordered_issues
                ),
                complete=True,
                checked_namespaces=len(
                    namespaces
                ),
                checked_subjects=len(
                    self._definitions
                ),
                checked_versions=(
                    checked_versions
                ),
                registry_generation=(
                    self._generation
                ),
                ownership_generation=getattr(
                    self._ownership,
                    "generation",
                    len(
                        self._ownership
                        .history()
                    ),
                ),
                audit_generation=(
                    self._audit.generation
                ),
                registry_fingerprint=(
                    fingerprint_one
                ),
                audit_valid=(
                    audit_verification.valid
                ),
                issues=ordered_issues,
            )

            return report.to_canonical_dict()


__all__ = [
    "REGISTRY_CONTRACT_VERSION",
    "REGISTRY_STRUCTURE_KIND",
    "RegistryIntegrityIssue",
    "RegistryIntegrityReport",
    "RegistryLifecycleResult",
    "RegistryMeasurements",
    "RegistryRegistrationResult",
    "RuntimeSchemaRegistry",
]
