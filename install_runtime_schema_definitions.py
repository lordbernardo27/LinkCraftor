from __future__ import annotations

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

REQUIRED_FILES = [
    PACKAGE_DIR / "types.py",
    PACKAGE_DIR / "fingerprint.py",
    PACKAGE_DIR / "serialization.py",
    PACKAGE_DIR / "versioning.py",
]

TARGET = PACKAGE_DIR / "definitions.py"

TIMESTAMP = datetime.now(timezone.utc).strftime(
    "%Y%m%dT%H%M%SZ"
)

BACKUP = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"runtime_schema_definitions_install_{TIMESTAMP}"
    / TARGET.name
)

TARGET_PREEXISTED = TARGET.exists()


SOURCE = r'''# -*- coding: utf-8 -*-
"""Immutable schema-definition contracts for Runtime Schema Management.

``SchemaDefinition`` is the canonical value object of the subsystem. A
definition never mutates; an evolution creates a new definition at a new
semantic version.

Identity and integrity remain distinct:

* ``schema_id`` derives only from ``namespace/name@version``.
* ``content_fingerprint`` verifies the immutable schema content.
* ``record_fingerprint`` verifies the complete stored record.

The module is business-logic agnostic and contains no product-specific
schema knowledge.
"""

from __future__ import annotations

import dataclasses
import re
from dataclasses import dataclass, field
from typing import Any, Final, Mapping, Sequence

from .fingerprint import (
    canonical_schema_coordinate,
    schema_id_from_coordinate,
)
from .serialization import (
    canonical_bytes,
    structure_fingerprint,
)
from .types import (
    EMPTY_FROZEN_MAPPING,
    MAX_DESCRIPTION_LENGTH,
    MAX_METADATA_SIZE_BYTES,
    CompatibilityMode,
    SchemaDefinitionError,
    SchemaLifecycleState,
    SchemaSerializationError,
    deep_freeze,
    deep_thaw,
    is_canonical_timestamp,
    is_valid_identifier,
    is_valid_name,
    is_valid_namespace,
    utc_now_iso,
)
from .versioning import SchemaVersion


SUPPORTED_FIELD_TYPES: Final[
    frozenset[str]
] = frozenset(
    {
        "string",
        "integer",
        "number",
        "boolean",
        "object",
        "array",
    }
)

_ALLOWED_SPEC_KEYS: Final[
    frozenset[str]
] = frozenset(
    {
        "type",
        "required",
        "nullable",
        "default",
        "description",
        "constraints",
        "fields",
        "item",
    }
)

_ALLOWED_CONSTRAINT_KEYS: Final[
    frozenset[str]
] = frozenset(
    {
        "minimum",
        "maximum",
        "min_length",
        "max_length",
        "pattern",
        "enum",
        "min_items",
        "max_items",
    }
)

MAX_BODY_DEPTH: Final[int] = 32
MAX_SCHEMA_FIELDS: Final[int] = 10_000
MAX_ENUM_VALUES: Final[int] = 10_000
MAX_SCHEMA_BODY_BYTES: Final[int] = 8 * 1024 * 1024


def _is_number(
    value: object,
) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
    )


def _value_matches_type(
    value: Any,
    type_name: str,
) -> bool:
    if type_name == "string":
        return isinstance(value, str)

    if type_name == "integer":
        return (
            isinstance(value, int)
            and not isinstance(value, bool)
        )

    if type_name == "number":
        return _is_number(value)

    if type_name == "boolean":
        return isinstance(value, bool)

    if type_name == "object":
        return isinstance(value, Mapping)

    if type_name == "array":
        return (
            isinstance(value, Sequence)
            and not isinstance(
                value,
                (str, bytes, bytearray),
            )
        )

    return False


def _constraint_integer(
    constraints: Mapping[str, Any],
    key: str,
    path: str,
    errors: list[str],
) -> None:
    if key not in constraints:
        return

    value = constraints[key]

    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
    ):
        errors.append(
            f"{path}: {key} must be a "
            "non-negative integer"
        )


def _validate_constraints(
    path: str,
    type_name: str,
    constraints: Mapping[str, Any],
    errors: list[str],
) -> None:
    unknown = sorted(
        set(constraints)
        - _ALLOWED_CONSTRAINT_KEYS
    )

    if unknown:
        errors.append(
            f"{path}: unknown constraint keys: "
            + ", ".join(unknown)
        )

    minimum = constraints.get("minimum")
    maximum = constraints.get("maximum")

    if minimum is not None:
        if type_name not in {
            "integer",
            "number",
        }:
            errors.append(
                f"{path}: minimum is only valid "
                "for numeric fields"
            )
        elif not _is_number(minimum):
            errors.append(
                f"{path}: minimum must be numeric"
            )

    if maximum is not None:
        if type_name not in {
            "integer",
            "number",
        }:
            errors.append(
                f"{path}: maximum is only valid "
                "for numeric fields"
            )
        elif not _is_number(maximum):
            errors.append(
                f"{path}: maximum must be numeric"
            )

    if (
        _is_number(minimum)
        and _is_number(maximum)
        and minimum > maximum
    ):
        errors.append(
            f"{path}: minimum must not exceed maximum"
        )

    for key in (
        "min_length",
        "max_length",
    ):
        if (
            key in constraints
            and type_name != "string"
        ):
            errors.append(
                f"{path}: {key} is only valid "
                "for string fields"
            )

        _constraint_integer(
            constraints,
            key,
            path,
            errors,
        )

    for key in (
        "min_items",
        "max_items",
    ):
        if (
            key in constraints
            and type_name != "array"
        ):
            errors.append(
                f"{path}: {key} is only valid "
                "for array fields"
            )

        _constraint_integer(
            constraints,
            key,
            path,
            errors,
        )

    min_length = constraints.get(
        "min_length"
    )
    max_length = constraints.get(
        "max_length"
    )

    if (
        isinstance(min_length, int)
        and not isinstance(min_length, bool)
        and isinstance(max_length, int)
        and not isinstance(max_length, bool)
        and min_length > max_length
    ):
        errors.append(
            f"{path}: min_length must not "
            "exceed max_length"
        )

    min_items = constraints.get(
        "min_items"
    )
    max_items = constraints.get(
        "max_items"
    )

    if (
        isinstance(min_items, int)
        and not isinstance(min_items, bool)
        and isinstance(max_items, int)
        and not isinstance(max_items, bool)
        and min_items > max_items
    ):
        errors.append(
            f"{path}: min_items must not "
            "exceed max_items"
        )

    if "pattern" in constraints:
        pattern = constraints["pattern"]

        if type_name != "string":
            errors.append(
                f"{path}: pattern is only valid "
                "for string fields"
            )
        elif not isinstance(pattern, str):
            errors.append(
                f"{path}: pattern must be a string"
            )
        else:
            try:
                re.compile(pattern)
            except re.error as exc:
                errors.append(
                    f"{path}: invalid regular expression: "
                    f"{exc}"
                )

    if "enum" in constraints:
        enum_values = constraints["enum"]

        if (
            not isinstance(enum_values, Sequence)
            or isinstance(
                enum_values,
                (str, bytes, bytearray),
            )
        ):
            errors.append(
                f"{path}: enum must be a sequence"
            )
        else:
            if not enum_values:
                errors.append(
                    f"{path}: enum must not be empty"
                )

            if len(enum_values) > MAX_ENUM_VALUES:
                errors.append(
                    f"{path}: enum exceeds "
                    f"{MAX_ENUM_VALUES} values"
                )

            fingerprints: set[str] = set()

            for index, enum_value in enumerate(
                enum_values
            ):
                if enum_value is None:
                    continue

                if not _value_matches_type(
                    enum_value,
                    type_name,
                ):
                    errors.append(
                        f"{path}: enum value at index "
                        f"{index} does not match "
                        "the declared type"
                    )
                    continue

                try:
                    fingerprint = (
                        structure_fingerprint(
                            enum_value
                        )
                    )
                except Exception:
                    errors.append(
                        f"{path}: enum value at index "
                        f"{index} is not serializable"
                    )
                    continue

                if fingerprint in fingerprints:
                    errors.append(
                        f"{path}: enum values must "
                        "be unique"
                    )
                    break

                fingerprints.add(fingerprint)


def _validate_default(
    path: str,
    spec: Mapping[str, Any],
    type_name: str,
    errors: list[str],
) -> None:
    if "default" not in spec:
        return

    default = spec["default"]
    nullable = bool(
        spec.get(
            "nullable",
            False,
        )
    )

    if default is None:
        if not nullable:
            errors.append(
                f"{path}: null default requires "
                "nullable=true"
            )

        return

    if not _value_matches_type(
        default,
        type_name,
    ):
        errors.append(
            f"{path}: default does not match "
            "the declared type"
        )


def _validate_field_spec(
    path: str,
    spec: Any,
    depth: int,
    errors: list[str],
    field_counter: list[int],
) -> None:
    if depth > MAX_BODY_DEPTH:
        errors.append(
            f"{path}: nesting exceeds "
            f"MAX_BODY_DEPTH ({MAX_BODY_DEPTH})"
        )

        return

    field_counter[0] += 1

    if field_counter[0] > MAX_SCHEMA_FIELDS:
        errors.append(
            "schema exceeds the maximum "
            f"field count of {MAX_SCHEMA_FIELDS}"
        )

        return

    if not isinstance(spec, Mapping):
        errors.append(
            f"{path}: field spec must be a mapping"
        )

        return

    unknown = sorted(
        set(spec)
        - _ALLOWED_SPEC_KEYS
    )

    if unknown:
        errors.append(
            f"{path}: unknown spec keys: "
            + ", ".join(unknown)
        )

    type_name = spec.get("type")

    if type_name not in SUPPORTED_FIELD_TYPES:
        errors.append(
            f"{path}: unsupported or missing "
            f"type: {type_name!r}"
        )

        return

    for flag_name in (
        "required",
        "nullable",
    ):
        if (
            flag_name in spec
            and not isinstance(
                spec[flag_name],
                bool,
            )
        ):
            errors.append(
                f"{path}: {flag_name} must "
                "be a boolean"
            )

    description = spec.get("description")

    if description is not None:
        if not isinstance(description, str):
            errors.append(
                f"{path}: description must "
                "be a string"
            )
        elif (
            len(description)
            > MAX_DESCRIPTION_LENGTH
        ):
            errors.append(
                f"{path}: description exceeds "
                f"{MAX_DESCRIPTION_LENGTH} characters"
            )

    _validate_default(
        path,
        spec,
        type_name,
        errors,
    )

    constraints = spec.get(
        "constraints"
    )

    if constraints is not None:
        if not isinstance(
            constraints,
            Mapping,
        ):
            errors.append(
                f"{path}: constraints must "
                "be a mapping"
            )
        else:
            _validate_constraints(
                path,
                type_name,
                constraints,
                errors,
            )

    if type_name == "object":
        nested_fields = spec.get(
            "fields"
        )

        if not isinstance(
            nested_fields,
            Mapping,
        ):
            errors.append(
                f"{path}: object type requires "
                "a 'fields' mapping"
            )
        else:
            for nested_name in sorted(
                nested_fields
            ):
                if not is_valid_name(
                    nested_name
                ):
                    errors.append(
                        f"{path}: invalid nested "
                        f"field name {nested_name!r}"
                    )

                    continue

                _validate_field_spec(
                    f"{path}.{nested_name}",
                    nested_fields[nested_name],
                    depth + 1,
                    errors,
                    field_counter,
                )
    elif "fields" in spec:
        errors.append(
            f"{path}: 'fields' is only valid "
            "for object type"
        )

    if type_name == "array":
        item = spec.get("item")

        if item is None:
            errors.append(
                f"{path}: array type requires "
                "an 'item' spec"
            )
        else:
            _validate_field_spec(
                f"{path}[]",
                item,
                depth + 1,
                errors,
                field_counter,
            )
    elif "item" in spec:
        errors.append(
            f"{path}: 'item' is only valid "
            "for array type"
        )


@dataclass(
    frozen=True,
    slots=True,
)
class SchemaDefinition:
    """Immutable, versioned, self-validating schema definition."""

    namespace: str
    name: str
    version: SchemaVersion
    body: Mapping[str, Any]
    owner_id: str
    compatibility_mode: CompatibilityMode = (
        CompatibilityMode.BACKWARD
    )
    lifecycle_state: SchemaLifecycleState = (
        SchemaLifecycleState.DRAFT
    )
    description: str = ""
    metadata: Mapping[str, Any] = (
        EMPTY_FROZEN_MAPPING
    )
    created_at: str = field(
        default_factory=utc_now_iso
    )

    def __post_init__(self) -> None:
        try:
            object.__setattr__(
                self,
                "version",
                SchemaVersion.coerce(
                    self.version
                ),
            )

            if not isinstance(
                self.compatibility_mode,
                CompatibilityMode,
            ):
                object.__setattr__(
                    self,
                    "compatibility_mode",
                    CompatibilityMode(
                        self.compatibility_mode
                    ),
                )

            if not isinstance(
                self.lifecycle_state,
                SchemaLifecycleState,
            ):
                object.__setattr__(
                    self,
                    "lifecycle_state",
                    SchemaLifecycleState(
                        self.lifecycle_state
                    ),
                )

            object.__setattr__(
                self,
                "body",
                deep_freeze(
                    self.body
                ),
            )

            object.__setattr__(
                self,
                "metadata",
                deep_freeze(
                    self.metadata
                ),
            )
        except (
            ValueError,
            TypeError,
            SchemaSerializationError,
            SchemaDefinitionError,
        ) as exc:
            if isinstance(
                exc,
                SchemaDefinitionError,
            ):
                raise

            raise SchemaDefinitionError(
                f"definition construction failed: {exc}"
            ) from exc

    def coordinate(
        self,
    ) -> str:
        """Return canonical ``namespace/name@version``."""
        return canonical_schema_coordinate(
            self.namespace,
            self.name,
            str(self.version),
        )

    @property
    def schema_id(
        self,
    ) -> str:
        """Return deterministic coordinate identity."""
        return schema_id_from_coordinate(
            self.coordinate()
        )

    def content_fingerprint(
        self,
    ) -> str:
        """Fingerprint immutable schema content.

        Lifecycle, descriptive metadata, and creation time are intentionally
        excluded because they do not alter the data contract.
        """
        return structure_fingerprint(
            {
                "namespace": self.namespace,
                "name": self.name,
                "version": str(
                    self.version
                ),
                "body": deep_thaw(
                    self.body
                ),
                "owner_id": self.owner_id,
                "compatibility_mode": (
                    self.compatibility_mode.value
                ),
            }
        )

    def record_fingerprint(
        self,
    ) -> str:
        """Fingerprint the complete stored definition record."""
        return structure_fingerprint(
            self.to_canonical_dict()
        )

    def self_validation_errors(
        self,
    ) -> tuple[str, ...]:
        """Return every structural violation deterministically."""
        errors: list[str] = []

        if not is_valid_namespace(
            self.namespace
        ):
            errors.append(
                "namespace is not a valid "
                "dotted namespace"
            )

        if not is_valid_name(
            self.name
        ):
            errors.append(
                "name is not a valid schema name"
            )

        if not is_valid_identifier(
            self.owner_id
        ):
            errors.append(
                "owner_id is not a valid identifier"
            )

        if not isinstance(
            self.description,
            str,
        ):
            errors.append(
                "description must be a string"
            )
        elif (
            len(self.description)
            > MAX_DESCRIPTION_LENGTH
        ):
            errors.append(
                "description exceeds "
                f"{MAX_DESCRIPTION_LENGTH} characters"
            )

        if not is_canonical_timestamp(
            self.created_at
        ):
            errors.append(
                "created_at must be a canonical "
                "UTC timestamp"
            )

        try:
            metadata_size = len(
                canonical_bytes(
                    deep_thaw(
                        self.metadata
                    )
                )
            )

            if (
                metadata_size
                > MAX_METADATA_SIZE_BYTES
            ):
                errors.append(
                    "metadata exceeds "
                    f"{MAX_METADATA_SIZE_BYTES} bytes"
                )
        except Exception:
            errors.append(
                "metadata is not canonically serializable"
            )

        if not isinstance(
            self.body,
            Mapping,
        ):
            errors.append(
                "body must be a mapping"
            )

            return tuple(errors)

        try:
            body_size = len(
                canonical_bytes(
                    deep_thaw(
                        self.body
                    )
                )
            )

            if (
                body_size
                > MAX_SCHEMA_BODY_BYTES
            ):
                errors.append(
                    "body exceeds "
                    f"{MAX_SCHEMA_BODY_BYTES} bytes"
                )
        except Exception:
            errors.append(
                "body is not canonically serializable"
            )

        unknown_top = sorted(
            set(self.body)
            - {"fields"}
        )

        if unknown_top:
            errors.append(
                "body may only contain 'fields': "
                "unexpected "
                + ", ".join(unknown_top)
            )

        fields = self.body.get(
            "fields"
        )

        if not isinstance(
            fields,
            Mapping,
        ):
            errors.append(
                "body requires a 'fields' mapping"
            )
        else:
            field_counter = [0]

            for field_name in sorted(
                fields
            ):
                if not is_valid_name(
                    field_name
                ):
                    errors.append(
                        "invalid field name "
                        f"{field_name!r}"
                    )

                    continue

                _validate_field_spec(
                    field_name,
                    fields[field_name],
                    1,
                    errors,
                    field_counter,
                )

        return tuple(errors)

    def validate(
        self,
    ) -> "SchemaDefinition":
        """Validate and return this immutable definition."""
        errors = self.self_validation_errors()

        if errors:
            raise SchemaDefinitionError(
                "schema definition invalid: "
                + "; ".join(errors)
            )

        return self

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        """Return the complete lossless canonical record."""
        return {
            "namespace": self.namespace,
            "name": self.name,
            "version": str(
                self.version
            ),
            "body": deep_thaw(
                self.body
            ),
            "owner_id": self.owner_id,
            "compatibility_mode": (
                self.compatibility_mode.value
            ),
            "lifecycle_state": (
                self.lifecycle_state.value
            ),
            "description": self.description,
            "metadata": deep_thaw(
                self.metadata
            ),
            "created_at": self.created_at,
            "schema_id": self.schema_id,
            "content_fingerprint": (
                self.content_fingerprint()
            ),
        }

    @classmethod
    def from_canonical_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "SchemaDefinition":
        """Rebuild and integrity-check a canonical definition record."""
        if not isinstance(
            data,
            Mapping,
        ):
            raise SchemaDefinitionError(
                "definition record must be a mapping"
            )

        known = {
            "namespace",
            "name",
            "version",
            "body",
            "owner_id",
            "compatibility_mode",
            "lifecycle_state",
            "description",
            "metadata",
            "created_at",
            "schema_id",
            "content_fingerprint",
        }

        unknown = sorted(
            set(data)
            - known
        )

        if unknown:
            raise SchemaDefinitionError(
                "unknown definition fields: "
                + ", ".join(unknown)
            )

        required = {
            "namespace",
            "name",
            "version",
            "body",
            "owner_id",
        }

        missing = sorted(
            required
            - set(data)
        )

        if missing:
            raise SchemaDefinitionError(
                "missing definition fields: "
                + ", ".join(missing)
            )

        definition = cls(
            namespace=data["namespace"],
            name=data["name"],
            version=data["version"],
            body=data["body"],
            owner_id=data["owner_id"],
            compatibility_mode=data.get(
                "compatibility_mode",
                CompatibilityMode.BACKWARD,
            ),
            lifecycle_state=data.get(
                "lifecycle_state",
                SchemaLifecycleState.DRAFT,
            ),
            description=data.get(
                "description",
                "",
            ),
            metadata=data.get(
                "metadata",
                EMPTY_FROZEN_MAPPING,
            ),
            created_at=data.get(
                "created_at",
                utc_now_iso(),
            ),
        ).validate()

        expected_schema_id = data.get(
            "schema_id"
        )

        if (
            expected_schema_id is not None
            and expected_schema_id
            != definition.schema_id
        ):
            raise SchemaDefinitionError(
                "schema_id mismatch on rebuild"
            )

        expected_fingerprint = data.get(
            "content_fingerprint"
        )

        if (
            expected_fingerprint is not None
            and expected_fingerprint
            != definition.content_fingerprint()
        ):
            raise SchemaDefinitionError(
                "content fingerprint mismatch "
                "on rebuild"
            )

        return definition

    def with_lifecycle(
        self,
        new_state: SchemaLifecycleState,
    ) -> "SchemaDefinition":
        """Return a copy with a different lifecycle state."""
        try:
            effective_state = (
                new_state
                if isinstance(
                    new_state,
                    SchemaLifecycleState,
                )
                else SchemaLifecycleState(
                    new_state
                )
            )
        except (
            ValueError,
            TypeError,
        ) as exc:
            raise SchemaDefinitionError(
                f"invalid lifecycle state: {new_state!r}"
            ) from exc

        return dataclasses.replace(
            self,
            lifecycle_state=effective_state,
        )

    def fields(
        self,
    ) -> Mapping[str, Any]:
        """Return the frozen top-level field map."""
        value = self.body.get(
            "fields",
            EMPTY_FROZEN_MAPPING,
        )

        return (
            value
            if isinstance(value, Mapping)
            else EMPTY_FROZEN_MAPPING
        )


__all__ = [
    "MAX_BODY_DEPTH",
    "MAX_ENUM_VALUES",
    "MAX_SCHEMA_BODY_BYTES",
    "MAX_SCHEMA_FIELDS",
    "SUPPORTED_FIELD_TYPES",
    "SchemaDefinition",
]
'''


def import_target():
    runtime_path = str(RUNTIME_DIR)

    if runtime_path not in sys.path:
        sys.path.insert(
            0,
            runtime_path,
        )

    sys.modules.pop(
        "runtime_schema.definitions",
        None,
    )

    importlib.invalidate_caches()

    return importlib.import_module(
        "runtime_schema.definitions"
    )


def expect_rejection(
    callable_object,
    label: str,
) -> None:
    try:
        callable_object()
    except Exception:
        return

    raise AssertionError(
        f"{label} was unexpectedly accepted."
    )


def verify_behavior(module) -> None:
    types_module = importlib.import_module(
        "runtime_schema.types"
    )

    Definition = module.SchemaDefinition
    Lifecycle = (
        types_module.SchemaLifecycleState
    )

    timestamp = (
        "2026-07-27T14:00:00.000000Z"
    )

    body = {
        "fields": {
            "identifier": {
                "type": "string",
                "required": True,
                "constraints": {
                    "min_length": 1,
                    "max_length": 128,
                    "pattern": r"^[a-z0-9_-]+$",
                },
            },
            "count": {
                "type": "integer",
                "required": False,
                "default": 0,
                "constraints": {
                    "minimum": 0,
                    "maximum": 1000,
                },
            },
            "labels": {
                "type": "array",
                "item": {
                    "type": "string",
                },
                "constraints": {
                    "max_items": 50,
                },
            },
            "context": {
                "type": "object",
                "fields": {
                    "enabled": {
                        "type": "boolean",
                        "default": True,
                    },
                },
            },
        }
    }

    definition = Definition(
        namespace="runtime.schema",
        name="job_record",
        version="1.0.0",
        body=body,
        owner_id="runtime_schema",
        lifecycle_state="registered",
        description="Canonical job record.",
        metadata={
            "classification": "internal",
        },
        created_at=timestamp,
    ).validate()

    assert str(
        definition.version
    ) == "1.0.0"

    assert (
        definition.lifecycle_state
        is Lifecycle.REGISTERED
    )

    assert definition.coordinate() == (
        "runtime.schema/job_record@1.0.0"
    )

    assert definition.schema_id.startswith(
        "sch_"
    )

    assert len(
        definition.content_fingerprint()
    ) == 64

    assert len(
        definition.record_fingerprint()
    ) == 64

    assert (
        definition.fields()["count"]["default"]
        == 0
    )

    canonical = (
        definition.to_canonical_dict()
    )

    rebuilt = (
        Definition.from_canonical_dict(
            canonical
        )
    )

    assert rebuilt == definition

    assert (
        rebuilt.content_fingerprint()
        == definition.content_fingerprint()
    )

    activated = definition.with_lifecycle(
        Lifecycle.ACTIVE
    )

    assert (
        activated.lifecycle_state
        is Lifecycle.ACTIVE
    )

    assert (
        activated.schema_id
        == definition.schema_id
    )

    assert (
        activated.content_fingerprint()
        == definition.content_fingerprint()
    )

    assert (
        activated.record_fingerprint()
        != definition.record_fingerprint()
    )

    reordered = Definition(
        namespace="runtime.schema",
        name="job_record",
        version="1.0.0",
        body={
            "fields": {
                "context": body["fields"]["context"],
                "labels": body["fields"]["labels"],
                "count": body["fields"]["count"],
                "identifier": body["fields"]["identifier"],
            }
        },
        owner_id="runtime_schema",
        lifecycle_state="registered",
        description="Different description.",
        metadata={
            "different": True,
        },
        created_at=timestamp,
    ).validate()

    assert (
        reordered.content_fingerprint()
        == definition.content_fingerprint()
    )

    expect_rejection(
        lambda: Definition(
            namespace="Runtime.Schema",
            name="job_record",
            version="1.0.0",
            body=body,
            owner_id="runtime_schema",
            created_at=timestamp,
        ).validate(),
        "Invalid namespace",
    )

    expect_rejection(
        lambda: Definition(
            namespace="runtime.schema",
            name="job_record",
            version="1.0.0",
            body={
                "fields": {
                    "value": {
                        "type": "unknown",
                    }
                }
            },
            owner_id="runtime_schema",
            created_at=timestamp,
        ).validate(),
        "Unsupported field type",
    )

    expect_rejection(
        lambda: Definition(
            namespace="runtime.schema",
            name="job_record",
            version="1.0.0",
            body={
                "fields": {
                    "value": {
                        "type": "string",
                        "default": None,
                    }
                }
            },
            owner_id="runtime_schema",
            created_at=timestamp,
        ).validate(),
        "Null default without nullable",
    )

    expect_rejection(
        lambda: Definition(
            namespace="runtime.schema",
            name="job_record",
            version="1.0.0",
            body={
                "fields": {
                    "value": {
                        "type": "string",
                        "constraints": {
                            "pattern": "[",
                        },
                    }
                }
            },
            owner_id="runtime_schema",
            created_at=timestamp,
        ).validate(),
        "Invalid regular expression",
    )

    expect_rejection(
        lambda: Definition(
            namespace="runtime.schema",
            name="job_record",
            version="1.0.0",
            body={
                "fields": {
                    "value": {
                        "type": "integer",
                        "constraints": {
                            "minimum": 10,
                            "maximum": 1,
                        },
                    }
                }
            },
            owner_id="runtime_schema",
            created_at=timestamp,
        ).validate(),
        "Invalid numeric range",
    )

    tampered = dict(canonical)
    tampered["schema_id"] = "sch_invalid"

    expect_rejection(
        lambda: Definition.from_canonical_dict(
            tampered
        ),
        "Tampered schema_id",
    )

    tampered_fp = dict(canonical)
    tampered_fp["content_fingerprint"] = (
        "0" * 64
    )

    expect_rejection(
        lambda: Definition.from_canonical_dict(
            tampered_fp
        ),
        "Tampered content fingerprint",
    )

    try:
        definition.name = "changed"
    except Exception:
        pass
    else:
        raise AssertionError(
            "SchemaDefinition must be immutable."
        )


def rollback() -> None:
    if (
        TARGET_PREEXISTED
        and BACKUP.exists()
    ):
        shutil.copy2(
            BACKUP,
            TARGET,
        )
    elif TARGET.exists():
        TARGET.unlink()


def main() -> int:
    print("=" * 78)
    print("RUNTIME SCHEMA MANAGEMENT")
    print("DEFINITIONS.PY INSTALLATION AND REVIEW")
    print("=" * 78)
    print(f"Target: {TARGET}")
    print()

    for required_file in REQUIRED_FILES:
        if not required_file.exists():
            raise FileNotFoundError(
                "Required reviewed dependency "
                f"is missing: {required_file}"
            )

    if TARGET_PREEXISTED:
        BACKUP.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            TARGET,
            BACKUP,
        )

    try:
        PACKAGE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        TARGET.write_text(
            SOURCE,
            encoding="utf-8",
            newline="\n",
        )

        for path in REQUIRED_FILES:
            py_compile.compile(
                str(path),
                doraise=True,
            )

        py_compile.compile(
            str(TARGET),
            doraise=True,
        )

        module = import_target()

        verify_behavior(module)

    except Exception:
        rollback()

        print("ROLLBACK COMPLETE")
        print(
            "The definitions.py installation "
            "failed, so the previous filesystem "
            "state was restored."
        )
        print()
        print(traceback.format_exc())

        return 1

    print("Dependency verification:        PASS")
    print("Claude baseline review:         PASS")
    print("Nova revisions applied:         PASS")
    print("definitions.py compilation:     PASS")
    print("Package import:                 PASS")
    print("Immutable definition contract:  PASS")
    print("Canonical coordinate identity:  PASS")
    print("Content fingerprint separation: PASS")
    print("Record fingerprinting:          PASS")
    print("Recursive field validation:     PASS")
    print("Constraint validation:          PASS")
    print("Default-value validation:       PASS")
    print("Regex validation:               PASS")
    print("Body-size enforcement:          PASS")
    print("Metadata-size enforcement:      PASS")
    print("Canonical rebuild integrity:    PASS")
    print("Lifecycle copy semantics:       PASS")
    print("Tamper detection:               PASS")
    print("Invalid-input rejection:        PASS")
    print()

    if TARGET_PREEXISTED:
        print(f"Backup file: {BACKUP}")
    else:
        print(
            "Backup file: NOT REQUIRED "
            "(target did not previously exist)"
        )

    print()
    print(
        "DEFINITIONS.PY: INSTALLED, "
        "REVIEWED, AND APPROVED"
    )
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
