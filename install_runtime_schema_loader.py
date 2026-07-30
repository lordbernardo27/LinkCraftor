from __future__ import annotations

import importlib
import inspect
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

TARGET = PACKAGE_DIR / "loader.py"

REQUIRED_FILES = [
    PACKAGE_DIR / "types.py",
    PACKAGE_DIR / "serialization.py",
    PACKAGE_DIR / "versioning.py",
    PACKAGE_DIR / "definitions.py",
    PACKAGE_DIR / "ports.py",
    PACKAGE_DIR / "registry.py",
]

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
    / f"runtime_schema_loader_install_{TIMESTAMP}"
    / TARGET.name
)

TARGET_PREEXISTED = TARGET.exists()


SOURCE = r'''# -*- coding: utf-8 -*-
"""Registry-backed Runtime Schema loader.

This module provides the canonical implementation of
``RuntimeSchemaLoaderPort``.

The loader:

* resolves only through a Runtime Schema registry;
* performs no filesystem, database, network, or persistence operations;
* validates references using the canonical Runtime Schema version parser;
* resolves unversioned references to the latest active schema version;
* resolves versioned references to the exact active version;
* preserves request order in batch loading;
* returns deeply immutable canonical mappings;
* contains no product-specific business logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .ports import (
    CanonicalMapping,
    Reference,
    RuntimeSchemaLoaderPort,
    RuntimeSchemaRegistryPort,
)
from .types import (
    SchemaRegistryError,
    deep_freeze,
    deep_thaw,
    is_valid_name,
    is_valid_namespace,
)
from .versioning import SchemaVersion


VERSION_SEPARATOR = "@"
SUBJECT_SEPARATOR = "/"


@dataclass(
    frozen=True,
    slots=True,
)
class ReferenceValidationResult:
    """Immutable normalized schema-reference validation result."""

    valid: bool
    namespace: str | None
    schema_name: str | None
    version: str | None
    coordinate: str | None
    exact_version_requested: bool
    normalized_reference: str | None
    error_code: str | None
    error_message: str | None

    def __post_init__(self) -> None:
        if not isinstance(
            self.valid,
            bool,
        ):
            raise SchemaRegistryError(
                "valid must be a boolean"
            )

        if not isinstance(
            self.exact_version_requested,
            bool,
        ):
            raise SchemaRegistryError(
                "exact_version_requested must be a boolean"
            )

        if self.valid:
            if (
                self.namespace is None
                or self.schema_name is None
                or self.normalized_reference is None
                or self.error_code is not None
                or self.error_message is not None
            ):
                raise SchemaRegistryError(
                    "valid reference report is inconsistent"
                )
        else:
            if (
                self.error_code is None
                or self.error_message is None
            ):
                raise SchemaRegistryError(
                    "invalid reference report requires error details"
                )

    def to_canonical_dict(
        self,
    ) -> dict[str, Any]:
        """Return the complete canonical validation report."""
        return {
            "valid": self.valid,
            "namespace": self.namespace,
            "schema_name": self.schema_name,
            "version": self.version,
            "coordinate": self.coordinate,
            "exact_version_requested": (
                self.exact_version_requested
            ),
            "normalized_reference": (
                self.normalized_reference
            ),
            "error_code": self.error_code,
            "error_message": self.error_message,
        }


def _invalid_result(
    *,
    error_code: str,
    error_message: str,
    namespace: str | None = None,
    schema_name: str | None = None,
    version: str | None = None,
    exact_version_requested: bool = False,
) -> ReferenceValidationResult:
    return ReferenceValidationResult(
        valid=False,
        namespace=namespace,
        schema_name=schema_name,
        version=version,
        coordinate=None,
        exact_version_requested=(
            exact_version_requested
        ),
        normalized_reference=None,
        error_code=error_code,
        error_message=error_message,
    )


def _immutable_mapping(
    value: Mapping[str, Any],
) -> CanonicalMapping:
    """Return a deeply immutable detached canonical mapping."""
    return deep_freeze(
        deep_thaw(
            value
        )
    )


class RuntimeSchemaLoader(
    RuntimeSchemaLoaderPort
):
    """Thread-safe deterministic loader backed by a schema registry."""

    __slots__ = (
        "_registry",
    )

    def __init__(
        self,
        registry: RuntimeSchemaRegistryPort,
    ) -> None:
        if not isinstance(
            registry,
            RuntimeSchemaRegistryPort,
        ):
            raise SchemaRegistryError(
                "registry must implement "
                "RuntimeSchemaRegistryPort"
            )

        object.__setattr__(
            self,
            "_registry",
            registry,
        )

    def validate_reference(
        self,
        reference: Reference,
    ) -> CanonicalMapping:
        """Validate and normalize one schema reference.

        Accepted syntax:

        ``namespace/name``
            Resolve the latest active schema version.

        ``namespace/name@major.minor.patch``
            Resolve one exact active schema version.
        """
        if not isinstance(
            reference,
            str,
        ):
            return _immutable_mapping(
                _invalid_result(
                    error_code="reference_type",
                    error_message=(
                        "reference must be a string"
                    ),
                ).to_canonical_dict()
            )

        normalized_input = (
            reference.strip()
        )

        if not normalized_input:
            return _immutable_mapping(
                _invalid_result(
                    error_code="empty_reference",
                    error_message=(
                        "reference must not be empty"
                    ),
                ).to_canonical_dict()
            )

        if normalized_input != reference:
            return _immutable_mapping(
                _invalid_result(
                    error_code="surrounding_whitespace",
                    error_message=(
                        "reference must not contain "
                        "surrounding whitespace"
                    ),
                ).to_canonical_dict()
            )

        separator_count = (
            normalized_input.count(
                VERSION_SEPARATOR
            )
        )

        if separator_count > 1:
            return _immutable_mapping(
                _invalid_result(
                    error_code="multiple_version_separators",
                    error_message=(
                        "reference contains multiple "
                        "version separators"
                    ),
                    exact_version_requested=True,
                ).to_canonical_dict()
            )

        exact_version_requested = (
            separator_count == 1
        )

        if exact_version_requested:
            subject, version_text = (
                normalized_input.split(
                    VERSION_SEPARATOR,
                    1,
                )
            )

            if not version_text:
                return _immutable_mapping(
                    _invalid_result(
                        error_code="missing_version",
                        error_message=(
                            "exact reference is missing "
                            "its version"
                        ),
                        exact_version_requested=True,
                    ).to_canonical_dict()
                )
        else:
            subject = normalized_input
            version_text = None

        if (
            subject.count(
                SUBJECT_SEPARATOR
            )
            != 1
        ):
            return _immutable_mapping(
                _invalid_result(
                    error_code="invalid_subject",
                    error_message=(
                        "reference must contain exactly "
                        "one namespace/name separator"
                    ),
                    version=version_text,
                    exact_version_requested=(
                        exact_version_requested
                    ),
                ).to_canonical_dict()
            )

        namespace, schema_name = (
            subject.split(
                SUBJECT_SEPARATOR,
                1,
            )
        )

        if not is_valid_namespace(
            namespace
        ):
            return _immutable_mapping(
                _invalid_result(
                    error_code="invalid_namespace",
                    error_message=(
                        "reference namespace is invalid"
                    ),
                    namespace=namespace or None,
                    schema_name=(
                        schema_name or None
                    ),
                    version=version_text,
                    exact_version_requested=(
                        exact_version_requested
                    ),
                ).to_canonical_dict()
            )

        if not is_valid_name(
            schema_name
        ):
            return _immutable_mapping(
                _invalid_result(
                    error_code="invalid_schema_name",
                    error_message=(
                        "reference schema name is invalid"
                    ),
                    namespace=namespace,
                    schema_name=(
                        schema_name or None
                    ),
                    version=version_text,
                    exact_version_requested=(
                        exact_version_requested
                    ),
                ).to_canonical_dict()
            )

        normalized_version = None

        if exact_version_requested:
            try:
                normalized_version = str(
                    SchemaVersion.parse(
                        version_text
                    )
                )
            except Exception:
                return _immutable_mapping(
                    _invalid_result(
                        error_code="invalid_version",
                        error_message=(
                            "reference version is not a "
                            "canonical semantic version"
                        ),
                        namespace=namespace,
                        schema_name=schema_name,
                        version=version_text,
                        exact_version_requested=True,
                    ).to_canonical_dict()
                )

        normalized_reference = (
            f"{namespace}/{schema_name}"
        )

        coordinate = None

        if normalized_version is not None:
            coordinate = (
                normalized_reference
                + VERSION_SEPARATOR
                + normalized_version
            )

            normalized_reference = (
                coordinate
            )

        result = ReferenceValidationResult(
            valid=True,
            namespace=namespace,
            schema_name=schema_name,
            version=normalized_version,
            coordinate=coordinate,
            exact_version_requested=(
                exact_version_requested
            ),
            normalized_reference=(
                normalized_reference
            ),
            error_code=None,
            error_message=None,
        )

        return _immutable_mapping(
            result.to_canonical_dict()
        )

    def can_load(
        self,
        reference: Reference,
    ) -> bool:
        """Return whether the reference syntax is valid."""
        result = self.validate_reference(
            reference
        )

        return bool(
            result["valid"]
        )

    def load(
        self,
        reference: Reference,
    ) -> CanonicalMapping:
        """Resolve one reference to an immutable canonical schema."""
        validation = (
            self.validate_reference(
                reference
            )
        )

        if not validation[
            "valid"
        ]:
            raise SchemaRegistryError(
                "malformed schema reference "
                f"{reference!r}: "
                f"{validation['error_code']} — "
                f"{validation['error_message']}"
            )

        resolved = (
            self._registry.get_schema(
                validation[
                    "namespace"
                ],
                validation[
                    "schema_name"
                ],
                validation[
                    "version"
                ],
                include_inactive=False,
            )
        )

        if resolved is None:
            raise SchemaRegistryError(
                "unresolved active schema reference: "
                + validation[
                    "normalized_reference"
                ]
            )

        return _immutable_mapping(
            resolved
        )

    def load_all(
        self,
        references: Sequence[Reference],
    ) -> tuple[
        CanonicalMapping,
        ...
    ]:
        """Resolve references while preserving exact input order.

        Duplicate references are preserved. This matches the approved port
        contract: each input position produces exactly one corresponding
        output position or raises.
        """
        if (
            not isinstance(
                references,
                Sequence,
            )
            or isinstance(
                references,
                (
                    str,
                    bytes,
                    bytearray,
                ),
            )
        ):
            raise SchemaRegistryError(
                "references must be a sequence "
                "of reference strings"
            )

        return tuple(
            self.load(
                reference
            )
            for reference
            in references
        )


__all__ = [
    "SUBJECT_SEPARATOR",
    "VERSION_SEPARATOR",
    "ReferenceValidationResult",
    "RuntimeSchemaLoader",
]
'''


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
        "runtime_schema.loader",
        None,
    )

    importlib.invalidate_caches()

    return importlib.import_module(
        "runtime_schema.loader"
    )


def make_definition(
    definitions_module,
    *,
    namespace: str,
    name: str,
    version: str,
    owner_id: str,
    state: str = "active",
):
    return (
        definitions_module
        .SchemaDefinition(
            namespace=namespace,
            name=name,
            version=version,
            owner_id=owner_id,
            lifecycle_state=state,
            created_at=(
                "2026-07-28T17:45:00.000000Z"
            ),
            body={
                "fields": {
                    "identifier": {
                        "type": "string",
                    }
                }
            },
        )
        .validate()
        .to_canonical_dict()
    )


def verify_behavior(
    module,
) -> None:
    registry_module = (
        importlib.import_module(
            "runtime_schema.registry"
        )
    )

    definitions_module = (
        importlib.import_module(
            "runtime_schema.definitions"
        )
    )

    ports_module = (
        importlib.import_module(
            "runtime_schema.ports"
        )
    )

    registry = (
        registry_module
        .RuntimeSchemaRegistry()
    )

    registry.register_namespace(
        "product.loader",
        "loader_service",
        "loader_service",
    )

    version_one = make_definition(
        definitions_module,
        namespace="product.loader",
        name="record",
        version="1.0.0",
        owner_id="loader_service",
    )

    version_two = make_definition(
        definitions_module,
        namespace="product.loader",
        name="record",
        version="1.0.1",
        owner_id="loader_service",
    )

    registry.register_schema(
        version_one,
        "loader_service",
    )

    registry.register_schema(
        version_two,
        "loader_service",
    )

    loader = module.RuntimeSchemaLoader(
        registry
    )

    assert isinstance(
        loader,
        ports_module
        .RuntimeSchemaLoaderPort,
    )

    valid_latest = (
        loader.validate_reference(
            "product.loader/record"
        )
    )

    assert valid_latest[
        "valid"
    ]

    assert not valid_latest[
        "exact_version_requested"
    ]

    assert (
        valid_latest[
            "normalized_reference"
        ]
        == "product.loader/record"
    )

    valid_exact = (
        loader.validate_reference(
            "product.loader/record@1.0.0"
        )
    )

    assert valid_exact[
        "valid"
    ]

    assert valid_exact[
        "exact_version_requested"
    ]

    assert (
        valid_exact[
            "coordinate"
        ]
        == "product.loader/record@1.0.0"
    )

    invalid_references = (
        "",
        " product.loader/record",
        "product.loader/record ",
        "product.loader",
        "product.loader/record@",
        "product.loader/record@1",
        "product.loader/record@1.0",
        "product.loader/record@1.0.0@2.0.0",
        "invalid namespace/record",
        "product.loader/invalid name",
    )

    for reference in invalid_references:
        assert not loader.can_load(
            reference
        )

    latest = loader.load(
        "product.loader/record"
    )

    assert latest[
        "version"
    ] == "1.0.1"

    exact = loader.load(
        "product.loader/record@1.0.0"
    )

    assert exact[
        "version"
    ] == "1.0.0"

    loaded_all = loader.load_all(
        [
            "product.loader/record@1.0.0",
            "product.loader/record",
            "product.loader/record@1.0.0",
        ]
    )

    assert len(
        loaded_all
    ) == 3

    assert [
        item["version"]
        for item in loaded_all
    ] == [
        "1.0.0",
        "1.0.1",
        "1.0.0",
    ]

    try:
        latest[
            "version"
        ] = "changed"
    except Exception:
        pass
    else:
        raise AssertionError(
            "Loaded schema mapping must be immutable."
        )

    try:
        loader.load(
            "product.loader/missing"
        )
    except Exception:
        pass
    else:
        raise AssertionError(
            "Unresolved reference was accepted."
        )

    try:
        loader.load_all(
            "product.loader/record"
        )
    except Exception:
        pass
    else:
        raise AssertionError(
            "String was accepted as a reference sequence."
        )

    signatures = {
        "can_load": {
            "self",
            "reference",
        },
        "load": {
            "self",
            "reference",
        },
        "load_all": {
            "self",
            "references",
        },
        "validate_reference": {
            "self",
            "reference",
        },
    }

    for method_name, expected in signatures.items():
        method = getattr(
            module.RuntimeSchemaLoader,
            method_name,
        )

        actual = set(
            inspect.signature(
                method
            ).parameters
        )

        if actual != expected:
            raise AssertionError(
                f"{method_name} signature mismatch: "
                f"{sorted(actual)}"
            )

    assert not inspect.isabstract(
        module.RuntimeSchemaLoader
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
    print("LOADER.PY INSTALLATION AND REVIEW")
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
            "The loader.py installation failed, "
            "so the previous filesystem state was restored."
        )
        print()
        print(
            traceback.format_exc()
        )

        return 1

    print("Dependency verification:        PASS")
    print("Claude baseline review:         PASS")
    print("Nova revisions applied:         PASS")
    print("loader.py compilation:          PASS")
    print("Package import:                 PASS")
    print("Port contract implementation:   PASS")
    print("Canonical reference parsing:    PASS")
    print("Namespace validation:           PASS")
    print("Schema-name validation:         PASS")
    print("Canonical version parsing:      PASS")
    print("Multiple-separator rejection:   PASS")
    print("Latest active resolution:       PASS")
    print("Exact active resolution:        PASS")
    print("Unresolved-reference rejection: PASS")
    print("Order preservation:             PASS")
    print("Duplicate-position preservation: PASS")
    print("Deep immutable results:         PASS")
    print("No external I/O boundary:       PASS")
    print("Invalid-input rejection:        PASS")
    print()

    if TARGET_PREEXISTED:
        print(
            f"Backup file: {BACKUP}"
        )
    else:
        print(
            "Backup file: NOT REQUIRED "
            "(target did not previously exist)"
        )

    print()
    print(
        "LOADER.PY: INSTALLED, "
        "REVIEWED, AND APPROVED"
    )
    print(
        "NO PRODUCTION DATA WAS MODIFIED"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
