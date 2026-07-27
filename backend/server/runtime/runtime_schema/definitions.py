# -*- coding: utf-8 -*-
"""Immutable schema-definition contracts for Runtime Schema Management.

A schema definition is never mutated. Evolution always creates a new
definition at a new semantic version.

Two identities remain separate:

* ``schema_id`` identifies ``namespace/name@version``.
* ``content_fingerprint`` verifies canonical definition content.
"""

from __future__ import annotations

import dataclasses
import json
import re
from dataclasses import dataclass, field
from typing import Any, Final, Mapping, Sequence

from .fingerprint import (
    canonical_schema_coordinate,
    schema_id_from_coordinate,
)
from .serialization import (
    canonical_json,
    structure_fingerprint,
)
from .types import (
    EMPTY_FROZEN_MAPPING,
    MAX_DESCRIPTION_LENGTH,
    MAX_METADATA_SIZE_BYTES,
    CompatibilityMode,
    SchemaDefinitionError,
    SchemaLifecycleState,
    deep_freeze,
    deep_thaw,
    is_canonical_timestamp,
    is_valid_identifier,
    is_valid_name,
    is_valid_namespace,
    utc_now_iso,
)
from .versioning import SchemaVersion


SUPPORTED_FIELD_TYPES: Final[frozenset[str]] = frozenset(
    {
        "string",
        "integer",
        "number",
        "boolean",
        "object",
        "array",
    }
)

ALLOWED_FIELD_SPEC_KEYS: Final[frozenset[str]] = frozenset(
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

ALLOWED_CONSTRAINT_KEYS: Final[frozenset[str]] = frozenset(
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
MAX_FIELD_COUNT: Final[int] = 10_000
MAX_ENUM_VALUES: Final[int] = 1_000
MAX_PATTERN_LENGTH: Final[int] = 4_096


def _is_number(
    value: Any,
) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
    )


def _value_matches_type(
    value: Any,
    type_name: str,
) -> bool:
    if value is None:
        return True

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


def _validate_constraints(
    path: str,
    type_name: str,
    constraints: Any,
    errors: list[str],
) -> None:
    if constraints is None:
        return

    if not isinstance(
        constraints,
        Mapping,
    ):
        errors.append(
            f"{path}: constraints must be a mapping"
        )
        return

    unknown = sorted(
        set(constraints)
        - ALLOWED_CONSTRAINT_KEYS
    )

    if unknown:
        errors.append(
            f"{path}: unsupported constraints: "
            + ", ".join(unknown)
        )

    numeric_keys = {
        "minimum",
        "maximum",
    }

    for key in numeric_keys:
        if (
            key in constraints
            and not _is_number(
                constraints[key]
            )
        ):
            errors.append(
                f"{path}: {key} must be numeric"
            )

    integer_keys = {
        "min_length",
        "max_length",
        "min_items",
        "max_items",
    }

    for key in integer_keys:
        if key in constraints:
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

    minimum = constraints.get(
        "minimum"
    )

    maximum = constraints.get(
        "maximum"
    )

    if (
        _is_number(minimum)
        and _is_number(maximum)
        and minimum > maximum
    ):
        errors.append(
            f"{path}: minimum exceeds maximum"
        )

    min_length = constraints.get(
        "min_length"
    )

    max_length = constraints.get(
        "max_length"
    )

    if (
        isinstance(min_length, int)
        and isinstance(max_length, int)
        and min_length > max_length
    ):
        errors.append(
            f"{path}: min_length exceeds max_length"
        )

    min_items = constraints.get(
        "min_items"
    )

    max_items = constraints.get(
        "max_items"
    )

    if (
        isinstance(min_items, int)
        and isinstance(max_items, int)
        and min_items > max_items
    ):
        errors.append(
            f"{path}: min_items exceeds max_items"
        )

    if "pattern" in constraints:
        pattern = constraints["pattern"]

        if not isinstance(pattern, str):
            errors.append(
                f"{path}: pattern must be a string"
            )
        elif len(pattern) > MAX_PATTERN_LENGTH:
            errors.append(
                f"{path}: pattern exceeds maximum length"
            )
        else:
            try:
                re.compile(pattern)
            except re.error as exc:
                errors.append(
                    f"{path}: invalid pattern: {exc}"
                )

    if "enum" in constraints:
        enum_values = constraints["enum"]

        if (
            not isinstance(
                enum_values,
                Sequence,
            )
            or isinstance(
                enum_values,
                (str, bytes, bytearray),
            )
        ):
            errors.append(
                f"{path}: enum must be a sequence"
            )
        else:
            if len(enum_values) > MAX_ENUM_VALUES:
                errors.append(
                    f"{path}: enum exceeds "
                    f"{MAX_ENUM_VALUES} values"
                )

            canonical_values: set[str] = set()

            for index, item in enumerate(
                enum_values
            ):
                if not _value_matches_type(
                    item,
                    type_name,
                ):
                    errors.append(
                        f"{path}: enum value at index "
                        f"{index} does not match {type_name}"
                    )
                    continue

                try:
                    encoded = canonical_json(item)
                except Exception as exc:
                    errors.append(
                        f"{path}: enum value at index "
                        f"{index} is not serializable: {exc}"
                    )
                    continue

                if encoded in canonical_values:
                    errors.append(
                        f"{path}: enum contains duplicate values"
                    )
                    break

                canonical_values.add(encoded)

    if type_name not in {
        "integer",
        "number",
    }:
        for key in numeric_keys:
            if key in constraints:
                errors.append(
                    f"{path}: {key} is only valid "
                    "for numeric fields"
                )

    if type_name != "string":
        for key in {
            "min_length",
            "max_length",
            "pattern",
        }:
            if key in constraints:
                errors.append(
                    f"{path}: {key} is only valid "
                    "for string fields"
                )

    if type_name != "array":
        for key in {
            "min_items",
            "max_items",
        }:
            if key in constraints:
                errors.append(
                    f"{path}: {key} is only valid "
                    "for array fields"
                )


def _validate_field_spec(
    path: str,
    spec: Any,
    depth: int,
    errors: list[str],
) -> None:
    if depth > MAX_BODY_DEPTH:
        errors.append(
            f"{path}: maximum body depth exceeded"
        )
        return

    if not isinstance(
        spec,
        Mapping,
    ):
        errors.append(
            f"{path}: field specification must be a mapping"
        )
        return

    unknown = sorted(
        set(spec)
        - ALLOWED_FIELD_SPEC_KEYS
    )

    if unknown:
        errors.append(
            f"{path}: unsupported field keys: "
            + ", ".join(unknown)
        )

    type_name = spec.get(
        "type"
    )

    if type_name not in SUPPORTED_FIELD_TYPES:
        errors.append(
            f"{path}: unsupported or missing type"
        )
        return

    for boolean_key in (
        "required",
        "nullable",
    ):
        if (
            boolean_key in spec
            and not isinstance(
                spec[boolean_key],
                bool,
            )
        ):
            errors.append(
                f"{path}: {boolean_key} must be boolean"
            )

    description = spec.get(
        "description",
        "",
    )

    if not isinstance(
        description,
        str,
    ):
        errors.append(
            f"{path}: description must be a string"
        )
    elif len(description) > MAX_DESCRIPTION_LENGTH:
        errors.append(
            f"{path}: description exceeds maximum length"
        )

    _validate_constraints(
        path,
        type_name,
        spec.get("constraints"),
        errors,
    )

    if "default" in spec:
        default = spec["default"]
        nullable = bool(
            spec.get(
                "nullable",
                False,
            )
        )

        if default is None and not nullable:
            errors.append(
                f"{path}: null default requires nullable=true"
            )
        elif not _value_matches_type(
            default,
            type_name,
        ):
            errors.append(
                f"{path}: default does not match "
                f"declared type {type_name}"
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
                f"{path}: object requires a fields mapping"
            )
        else:
            if len(nested_fields) > MAX_FIELD_COUNT:
                errors.append(
                    f"{path}: field count exceeds "
                    f"{MAX_FIELD_COUNT}"
                )

            for nested_name in sorted(
                nested_fields
            ):
                if not is_valid_name(
                    nested_name
                ):
                    errors.append(
                        f"{path}: invalid nested field name "
                        f"{nested_name!r}"
                    )
                    continue

                _validate_field_spec(
                    f"{path}.{nested_name}",
                    nested_fields[nested_name],
                    depth + 1,
                    errors,
                )
    elif "fields" in spec:
        errors.append(
            f"{path}: fields is only valid "
            "for object fields"
        )

    if type_name == "array":
        item_spec = spec.get(
            "item"
        )

        if item_spec is None:
            errors.append(
                f"{path}: array requires an item specification"
            )
        else:
            _validate_field_spec(
                f"{path}[]",
                item_spec,
                depth + 1,
                errors,
            )
    elif "item" in spec:
        errors.append(
            f"{path}: item is only valid "
            "for array fields"
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
            try:
                object.__setattr__(
                    self,
                    "compatibility_mode",
                    CompatibilityMode(
                        self.compatibility_mode
                    ),
                )
            except Exception as exc:
                raise SchemaDefinitionError(
                    "invalid compatibility_mode"
                ) from exc

        if not isinstance(
            self.lifecycle_state,
            SchemaLifecycleState,
        ):
            try:
                object.__setattr__(
                    self,
                    "lifecycle_state",
                    SchemaLifecycleState(
                        self.lifecycle_state
                    ),
                )
            except Exception as exc:
                raise SchemaDefinitionError(
                    "invalid lifecycle_state"
                ) from exc

        try:
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
        except Exception as exc:
            raise SchemaDefinitionError(
                f"definition contains unsupported content: {exc}"
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
        """Return deterministic schema-version identity."""
        return schema_id_from_coordinate(
            self.coordinate()
        )

    def content_dict(
        self,
    ) -> dict[str, Any]:
        """Return immutable identity-bearing content."""
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
        }

    def content_fingerprint(
        self,
    ) -> str:
        """Return deterministic integrity fingerprint."""
        return structure_fingerprint(
            self.content_dict()
        )

    def record_fingerprint(
        self,
    ) -> str:
        """Return deterministic fingerprint of the complete record."""
        return structure_fingerprint(
            self.to_canonical_dict()
        )

    def self_validation_errors(
        self,
    ) -> tuple[str, ...]:
        """Return every structural violation."""
        errors: list[str] = []

        if not is_valid_namespace(
            self.namespace
        ):
            errors.append(
                "namespace is not a valid dotted namespace"
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
                "description exceeds maximum length"
            )

        if not is_canonical_timestamp(
            self.created_at
        ):
            errors.append(
                "created_at must be a canonical UTC timestamp"
            )

        if not isinstance(
            self.metadata,
            Mapping,
        ):
            errors.append(
                "metadata must be a mapping"
            )
        else:
            try:
                metadata_size = len(
                    canonical_json(
                        deep_thaw(
                            self.metadata
                        )
                    ).encode("utf-8")
                )

                if (
                    metadata_size
                    > MAX_METADATA_SIZE_BYTES
                ):
                    errors.append(
                        "metadata exceeds maximum size"
                    )
            except Exception as exc:
                errors.append(
                    f"metadata is invalid: {exc}"
                )

        if not isinstance(
            self.body,
            Mapping,
        ):
            errors.append(
                "body must be a mapping"
            )
        else:
            unknown_top = sorted(
                set(self.body)
                - {"fields"}
            )

            if unknown_top:
                errors.append(
                    "body may only contain fields: "
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
                    "body requires a fields mapping"
                )
            else:
                if len(fields) > MAX_FIELD_COUNT:
                    errors.append(
                        "body field count exceeds "
                        f"{MAX_FIELD_COUNT}"
                    )

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
                    )

        return tuple(errors)

    def validate(
        self,
    ) -> "SchemaDefinition":
        """Raise when this definition is invalid."""
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
        """Return the complete lossless record."""
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
        """Rebuild and verify a canonical definition record."""
        if not isinstance(
            data,
            Mapping,
        ):
            raise SchemaDefinitionError(
                "definition record must be a mapping"
            )

        known_fields = {
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
            - known_fields
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
                "content fingerprint mismatch on rebuild"
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
        except Exception as exc:
            raise SchemaDefinitionError(
                "invalid lifecycle state"
            ) from exc

        return dataclasses.replace(
            self,
            lifecycle_state=effective_state,
        )

    def fields(
        self,
    ) -> Mapping[str, Any]:
        """Return the immutable top-level field mapping."""
        value = self.body.get(
            "fields",
            EMPTY_FROZEN_MAPPING,
        )

        if isinstance(
            value,
            Mapping,
        ):
            return value

        return EMPTY_FROZEN_MAPPING


__all__ = [
    "ALLOWED_CONSTRAINT_KEYS",
    "ALLOWED_FIELD_SPEC_KEYS",
    "MAX_BODY_DEPTH",
    "MAX_ENUM_VALUES",
    "MAX_FIELD_COUNT",
    "MAX_PATTERN_LENGTH",
    "SUPPORTED_FIELD_TYPES",
    "SchemaDefinition",
]
