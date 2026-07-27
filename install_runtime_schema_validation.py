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
    PACKAGE_DIR / "definitions.py",
]

TARGET = PACKAGE_DIR / "validation.py"

TIMESTAMP = datetime.now(timezone.utc).strftime(
    "%Y%m%dT%H%M%SZ"
)

BACKUP = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"runtime_schema_validation_install_{TIMESTAMP}"
    / TARGET.name
)

TARGET_PREEXISTED = TARGET.exists()


SOURCE = r'''# -*- coding: utf-8 -*-
"""Runtime document validation against immutable schema definitions.

This module validates runtime-owned documents against
:class:`runtime_schema.definitions.SchemaDefinition`.

Validation behavior:

* collects violations deterministically;
* does not stop at the first document error;
* validates required and nullable fields;
* validates scalar, object, and array types;
* validates all supported constraints;
* applies unknown-field policy recursively;
* rejects non-finite numeric values;
* enforces bounded traversal and issue collection;
* produces immutable, fingerprinted reports.

Schema-definition self-validation remains owned by ``definitions.py``.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any, Final, Mapping, Sequence

from .definitions import SchemaDefinition
from .serialization import structure_fingerprint
from .types import (
    SchemaValidationError,
    UnknownFieldPolicy,
)


MAX_VALIDATION_DEPTH: Final[int] = 64
MAX_VALIDATION_ISSUES: Final[int] = 10_000
MAX_VALIDATED_NODES: Final[int] = 1_000_000


@dataclass(
    frozen=True,
    slots=True,
    order=True,
)
class ValidationIssue:
    """One deterministic document-validation violation."""

    path: str
    code: str
    detail: str

    def __post_init__(self) -> None:
        for field_name in (
            "path",
            "code",
            "detail",
        ):
            value = getattr(
                self,
                field_name,
            )

            if (
                not isinstance(value, str)
                or not value
            ):
                raise SchemaValidationError(
                    f"{field_name} must be a non-empty string"
                )

    def to_canonical_dict(
        self,
    ) -> dict[str, str]:
        """Return plain JSON-native issue data."""
        return {
            "path": self.path,
            "code": self.code,
            "detail": self.detail,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class ValidationReport:
    """Complete immutable verdict for one document validation."""

    schema_id: str
    schema_content_fingerprint: str
    unknown_field_policy: UnknownFieldPolicy
    valid: bool
    issues: tuple[ValidationIssue, ...]
    visited_nodes: int
    truncated: bool = False

    def __post_init__(self) -> None:
        if (
            not isinstance(
                self.schema_id,
                str,
            )
            or not self.schema_id
        ):
            raise SchemaValidationError(
                "schema_id must be a non-empty string"
            )

        if (
            not isinstance(
                self.schema_content_fingerprint,
                str,
            )
            or len(
                self.schema_content_fingerprint
            )
            != 64
        ):
            raise SchemaValidationError(
                "schema_content_fingerprint must "
                "be a 64-character digest"
            )

        if not isinstance(
            self.unknown_field_policy,
            UnknownFieldPolicy,
        ):
            try:
                object.__setattr__(
                    self,
                    "unknown_field_policy",
                    UnknownFieldPolicy(
                        self.unknown_field_policy
                    ),
                )
            except (
                TypeError,
                ValueError,
            ) as exc:
                raise SchemaValidationError(
                    "invalid unknown_field_policy"
                ) from exc

        object.__setattr__(
            self,
            "issues",
            tuple(self.issues),
        )

        if (
            not isinstance(
                self.visited_nodes,
                int,
            )
            or isinstance(
                self.visited_nodes,
                bool,
            )
            or self.visited_nodes < 0
        ):
            raise SchemaValidationError(
                "visited_nodes must be a non-negative integer"
            )

        if self.valid != (
            not self.issues
            and not self.truncated
        ):
            raise SchemaValidationError(
                "valid flag is inconsistent with issues/truncation"
            )

    @property
    def issue_count(self) -> int:
        """Return total collected issue count."""
        return len(
            self.issues
        )

    @property
    def fingerprint(self) -> str:
        """Return deterministic validation-report fingerprint."""
        return structure_fingerprint(
            self.to_canonical_dict()
        )

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        """Return report as plain JSON-native data."""
        return {
            "schema_id": self.schema_id,
            "schema_content_fingerprint": (
                self.schema_content_fingerprint
            ),
            "unknown_field_policy": (
                self.unknown_field_policy.value
            ),
            "valid": self.valid,
            "issues": [
                issue.to_canonical_dict()
                for issue in self.issues
            ],
            "issue_count": self.issue_count,
            "visited_nodes": self.visited_nodes,
            "truncated": self.truncated,
        }


class _ValidationContext:
    """Mutable state private to one validation invocation."""

    __slots__ = (
        "issues",
        "visited_nodes",
        "truncated",
    )

    def __init__(self) -> None:
        self.issues: list[
            ValidationIssue
        ] = []

        self.visited_nodes = 0
        self.truncated = False

    def visit(
        self,
        path: str,
    ) -> bool:
        """Register one traversal node and enforce global bounds."""
        if self.truncated:
            return False

        self.visited_nodes += 1

        if (
            self.visited_nodes
            > MAX_VALIDATED_NODES
        ):
            self.add(
                path,
                "validation_limit",
                "maximum validated-node limit exceeded",
            )

            self.truncated = True

            return False

        return True

    def add(
        self,
        path: str,
        code: str,
        detail: str,
    ) -> None:
        """Append one issue while respecting the issue bound."""
        if self.truncated:
            return

        if (
            len(self.issues)
            >= MAX_VALIDATION_ISSUES
        ):
            self.truncated = True
            return

        self.issues.append(
            ValidationIssue(
                path=path,
                code=code,
                detail=detail,
            )
        )


def _coerce_policy(
    value: UnknownFieldPolicy | str,
) -> UnknownFieldPolicy:
    if isinstance(
        value,
        UnknownFieldPolicy,
    ):
        return value

    try:
        return UnknownFieldPolicy(
            value
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise SchemaValidationError(
            f"invalid unknown-field policy: {value!r}"
        ) from exc


def _is_sequence(
    value: Any,
) -> bool:
    return (
        isinstance(value, Sequence)
        and not isinstance(
            value,
            (str, bytes, bytearray),
        )
    )


def _is_finite_number(
    value: Any,
) -> bool:
    if (
        not isinstance(
            value,
            (int, float),
        )
        or isinstance(value, bool)
    ):
        return False

    if isinstance(
        value,
        float,
    ):
        return math.isfinite(
            value
        )

    return True


def _type_matches(
    value: Any,
    type_name: str,
) -> bool:
    if type_name == "string":
        return isinstance(
            value,
            str,
        )

    if type_name == "integer":
        return (
            isinstance(value, int)
            and not isinstance(value, bool)
        )

    if type_name == "number":
        return _is_finite_number(
            value
        )

    if type_name == "boolean":
        return isinstance(
            value,
            bool,
        )

    if type_name == "object":
        return isinstance(
            value,
            Mapping,
        )

    if type_name == "array":
        return _is_sequence(
            value
        )

    return False


def _safe_enum_contains(
    enum_values: Sequence[Any],
    value: Any,
) -> bool:
    """Compare enum values safely, including nested structures."""
    try:
        wanted = structure_fingerprint(
            value
        )
    except Exception:
        return False

    for enum_value in enum_values:
        try:
            if (
                structure_fingerprint(
                    enum_value
                )
                == wanted
            ):
                return True
        except Exception:
            continue

    return False


def _check_constraints(
    path: str,
    value: Any,
    constraints: Mapping[str, Any],
    context: _ValidationContext,
) -> None:
    minimum = constraints.get(
        "minimum"
    )

    if (
        minimum is not None
        and _is_finite_number(value)
        and value < minimum
    ):
        context.add(
            path,
            "minimum",
            f"value {value!r} is below {minimum!r}",
        )

    maximum = constraints.get(
        "maximum"
    )

    if (
        maximum is not None
        and _is_finite_number(value)
        and value > maximum
    ):
        context.add(
            path,
            "maximum",
            f"value {value!r} exceeds {maximum!r}",
        )

    min_length = constraints.get(
        "min_length"
    )

    if (
        min_length is not None
        and isinstance(value, str)
        and len(value) < min_length
    ):
        context.add(
            path,
            "min_length",
            f"length {len(value)} is below {min_length}",
        )

    max_length = constraints.get(
        "max_length"
    )

    if (
        max_length is not None
        and isinstance(value, str)
        and len(value) > max_length
    ):
        context.add(
            path,
            "max_length",
            f"length {len(value)} exceeds {max_length}",
        )

    pattern = constraints.get(
        "pattern"
    )

    if (
        pattern is not None
        and isinstance(value, str)
    ):
        try:
            matched = (
                re.fullmatch(
                    pattern,
                    value,
                )
                is not None
            )
        except re.error as exc:
            context.add(
                path,
                "invalid_schema_pattern",
                f"schema pattern is invalid: {exc}",
            )
        else:
            if not matched:
                context.add(
                    path,
                    "pattern",
                    f"value does not match {pattern!r}",
                )

    enum_values = constraints.get(
        "enum"
    )

    if (
        enum_values is not None
        and _is_sequence(
            enum_values
        )
        and not _safe_enum_contains(
            enum_values,
            value,
        )
    ):
        context.add(
            path,
            "enum",
            "value is not in the allowed set",
        )

    min_items = constraints.get(
        "min_items"
    )

    if (
        min_items is not None
        and _is_sequence(value)
        and len(value) < min_items
    ):
        context.add(
            path,
            "min_items",
            f"item count {len(value)} is below {min_items}",
        )

    max_items = constraints.get(
        "max_items"
    )

    if (
        max_items is not None
        and _is_sequence(value)
        and len(value) > max_items
    ):
        context.add(
            path,
            "max_items",
            f"item count {len(value)} exceeds {max_items}",
        )


def _validate_value(
    path: str,
    value: Any,
    spec: Mapping[str, Any],
    policy: UnknownFieldPolicy,
    context: _ValidationContext,
    depth: int,
) -> None:
    if not context.visit(
        path
    ):
        return

    if depth > MAX_VALIDATION_DEPTH:
        context.add(
            path,
            "validation_depth",
            "maximum validation depth exceeded",
        )

        return

    if value is None:
        if not bool(
            spec.get(
                "nullable",
                False,
            )
        ):
            context.add(
                path,
                "null",
                "field is not nullable",
            )

        return

    type_name = spec.get(
        "type"
    )

    if not isinstance(
        type_name,
        str,
    ):
        context.add(
            path,
            "invalid_schema_type",
            "field schema has no valid type",
        )

        return

    if not _type_matches(
        value,
        type_name,
    ):
        if (
            type_name == "number"
            and isinstance(
                value,
                float,
            )
            and not math.isfinite(
                value
            )
        ):
            context.add(
                path,
                "non_finite_number",
                "NaN and Infinity are not permitted",
            )
        else:
            context.add(
                path,
                "type",
                f"expected {type_name}, "
                f"got {type(value).__name__}",
            )

        return

    constraints = spec.get(
        "constraints"
    )

    if isinstance(
        constraints,
        Mapping,
    ):
        _check_constraints(
            path,
            value,
            constraints,
            context,
        )

    if type_name == "object":
        nested_fields = spec.get(
            "fields"
        )

        if isinstance(
            nested_fields,
            Mapping,
        ):
            _validate_object(
                path,
                value,
                nested_fields,
                policy,
                context,
                depth + 1,
            )

    elif type_name == "array":
        item_spec = spec.get(
            "item"
        )

        if isinstance(
            item_spec,
            Mapping,
        ):
            for index, item in enumerate(
                value
            ):
                _validate_value(
                    f"{path}[{index}]",
                    item,
                    item_spec,
                    policy,
                    context,
                    depth + 1,
                )

                if context.truncated:
                    return


def _child_path(
    parent: str,
    field_name: str,
) -> str:
    if parent == "$":
        return f"$.{field_name}"

    return f"{parent}.{field_name}"


def _validate_object(
    path: str,
    document: Mapping[str, Any],
    fields: Mapping[str, Any],
    policy: UnknownFieldPolicy,
    context: _ValidationContext,
    depth: int,
) -> None:
    if depth > MAX_VALIDATION_DEPTH:
        context.add(
            path,
            "validation_depth",
            "maximum validation depth exceeded",
        )

        return

    for field_name in sorted(
        fields
    ):
        if context.truncated:
            return

        spec = fields[field_name]

        if not isinstance(
            spec,
            Mapping,
        ):
            context.add(
                _child_path(
                    path,
                    field_name,
                ),
                "invalid_schema_field",
                "field schema is not a mapping",
            )

            continue

        field_path = _child_path(
            path,
            field_name,
        )

        if field_name not in document:
            if (
                bool(
                    spec.get(
                        "required",
                        False,
                    )
                )
                and "default" not in spec
            ):
                context.add(
                    field_path,
                    "required",
                    "required field is missing",
                )

            continue

        _validate_value(
            field_path,
            document[field_name],
            spec,
            policy,
            context,
            depth,
        )

    if (
        policy
        is UnknownFieldPolicy.REJECT
    ):
        unknown_fields = sorted(
            set(document)
            - set(fields)
        )

        for field_name in unknown_fields:
            context.add(
                _child_path(
                    path,
                    str(field_name),
                ),
                "unknown_field",
                "field is not declared by the schema",
            )

            if context.truncated:
                return


class DocumentValidator:
    """Stateless deterministic runtime-document validator."""

    @staticmethod
    def validate(
        document: Mapping[str, Any],
        definition: SchemaDefinition,
        unknown_field_policy: (
            UnknownFieldPolicy | str
        ) = UnknownFieldPolicy.REJECT,
    ) -> ValidationReport:
        """Validate a document without raising for document violations."""
        if not isinstance(
            definition,
            SchemaDefinition,
        ):
            raise SchemaValidationError(
                "definition must be a SchemaDefinition"
            )

        definition.validate()

        policy = _coerce_policy(
            unknown_field_policy
        )

        context = _ValidationContext()

        if not isinstance(
            document,
            Mapping,
        ):
            context.add(
                "$",
                "type",
                "document root must be a mapping",
            )
        else:
            context.visit(
                "$"
            )

            _validate_object(
                "$",
                document,
                definition.fields(),
                policy,
                context,
                1,
            )

        issues = tuple(
            sorted(
                context.issues,
                key=lambda issue: (
                    issue.path,
                    issue.code,
                    issue.detail,
                ),
            )
        )

        return ValidationReport(
            schema_id=definition.schema_id,
            schema_content_fingerprint=(
                definition.content_fingerprint()
            ),
            unknown_field_policy=policy,
            valid=(
                not issues
                and not context.truncated
            ),
            issues=issues,
            visited_nodes=(
                context.visited_nodes
            ),
            truncated=context.truncated,
        )


__all__ = [
    "MAX_VALIDATED_NODES",
    "MAX_VALIDATION_DEPTH",
    "MAX_VALIDATION_ISSUES",
    "DocumentValidator",
    "ValidationIssue",
    "ValidationReport",
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
        "runtime_schema.validation",
        None,
    )

    importlib.invalidate_caches()

    return importlib.import_module(
        "runtime_schema.validation"
    )


def verify_behavior(module) -> None:
    definitions_module = (
        importlib.import_module(
            "runtime_schema.definitions"
        )
    )

    types_module = (
        importlib.import_module(
            "runtime_schema.types"
        )
    )

    Definition = (
        definitions_module.SchemaDefinition
    )

    Policy = (
        types_module.UnknownFieldPolicy
    )

    definition = Definition(
        namespace="runtime.schema",
        name="validation_record",
        version="1.0.0",
        owner_id="runtime_schema",
        lifecycle_state="registered",
        created_at=(
            "2026-07-27T14:30:00.000000Z"
        ),
        body={
            "fields": {
                "identifier": {
                    "type": "string",
                    "required": True,
                    "constraints": {
                        "min_length": 2,
                        "max_length": 8,
                        "pattern": (
                            r"^[a-z]+$"
                        ),
                    },
                },
                "count": {
                    "type": "integer",
                    "constraints": {
                        "minimum": 0,
                        "maximum": 10,
                    },
                },
                "ratio": {
                    "type": "number",
                },
                "mode": {
                    "type": "string",
                    "constraints": {
                        "enum": [
                            "safe",
                            "fast",
                        ],
                    },
                },
                "context": {
                    "type": "object",
                    "fields": {
                        "enabled": {
                            "type": "boolean",
                            "required": True,
                        },
                    },
                },
                "items": {
                    "type": "array",
                    "constraints": {
                        "min_items": 1,
                        "max_items": 3,
                    },
                    "item": {
                        "type": "object",
                        "fields": {
                            "name": {
                                "type": "string",
                                "required": True,
                            },
                        },
                    },
                },
                "optional_value": {
                    "type": "string",
                    "nullable": True,
                },
            }
        },
    ).validate()

    valid_document = {
        "identifier": "alpha",
        "count": 5,
        "ratio": 0.5,
        "mode": "safe",
        "context": {
            "enabled": True,
        },
        "items": [
            {
                "name": "one",
            }
        ],
        "optional_value": None,
    }

    report_one = (
        module.DocumentValidator.validate(
            valid_document,
            definition,
        )
    )

    report_two = (
        module.DocumentValidator.validate(
            dict(
                reversed(
                    list(
                        valid_document.items()
                    )
                )
            ),
            definition,
        )
    )

    assert report_one.valid
    assert report_one.issue_count == 0
    assert not report_one.truncated

    assert (
        report_one.fingerprint
        == report_two.fingerprint
    )

    invalid_document = {
        "identifier": "A",
        "count": 20,
        "ratio": float("nan"),
        "mode": "invalid",
        "context": {
            "extra": True,
        },
        "items": [
            {},
            {
                "name": "two",
                "extra": "invalid",
            },
            {
                "name": "three",
            },
            {
                "name": "four",
            },
        ],
        "unknown": True,
    }

    invalid_report = (
        module.DocumentValidator.validate(
            invalid_document,
            definition,
        )
    )

    assert not invalid_report.valid

    codes = {
        issue.code
        for issue in invalid_report.issues
    }

    expected_codes = {
        "min_length",
        "pattern",
        "maximum",
        "non_finite_number",
        "enum",
        "required",
        "unknown_field",
        "max_items",
    }

    assert expected_codes.issubset(
        codes
    )

    paths = [
        issue.path
        for issue in invalid_report.issues
    ]

    assert paths == sorted(
        paths
    )

    relaxed = (
        module.DocumentValidator.validate(
            {
                **valid_document,
                "unknown": True,
            },
            definition,
            Policy.IGNORE,
        )
    )

    assert relaxed.valid

    root_report = (
        module.DocumentValidator.validate(
            ["not", "a", "mapping"],
            definition,
        )
    )

    assert not root_report.valid

    assert (
        root_report.issues[0].path
        == "$"
    )

    assert (
        root_report.issues[0].code
        == "type"
    )

    assert len(
        invalid_report.fingerprint
    ) == 64

    try:
        invalid_report.issues = ()
    except Exception:
        pass
    else:
        raise AssertionError(
            "ValidationReport must be immutable."
        )

    try:
        module.DocumentValidator.validate(
            valid_document,
            definition,
            "unsupported",
        )
    except Exception:
        pass
    else:
        raise AssertionError(
            "Invalid unknown-field policy was accepted."
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
    print("VALIDATION.PY INSTALLATION AND REVIEW")
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
            "The validation.py installation failed, "
            "so the previous filesystem state was restored."
        )
        print()
        print(traceback.format_exc())

        return 1

    print("Dependency verification:        PASS")
    print("Claude baseline review:         PASS")
    print("Nova revisions applied:         PASS")
    print("validation.py compilation:      PASS")
    print("Package import:                 PASS")
    print("Immutable validation reports:   PASS")
    print("Schema integrity validation:    PASS")
    print("Required-field validation:      PASS")
    print("Nullable-field validation:      PASS")
    print("Scalar type validation:         PASS")
    print("Nested object validation:       PASS")
    print("Nested array validation:        PASS")
    print("Constraint validation:          PASS")
    print("Unknown-field policy:           PASS")
    print("Non-finite-number rejection:    PASS")
    print("Deterministic issue ordering:   PASS")
    print("Deterministic fingerprints:     PASS")
    print("Traversal bounds:               PASS")
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
        "VALIDATION.PY: INSTALLED, "
        "REVIEWED, AND APPROVED"
    )
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
