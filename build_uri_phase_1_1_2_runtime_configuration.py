from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
import py_compile
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BUILD_VERSION = "uri_phase_1_1_2_runtime_configuration_v1"

PROJECT_ROOT = Path.cwd().resolve()

TARGET = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_configuration.py"
)

KERNEL_FILE = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_runtime_kernel.py"
)

EXISTING_RUNTIME_FACADE = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "universal_runtime_infrastructure.py"
)

MAIN_FILE = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "main.py"
)

TIMESTAMP = datetime.now(timezone.utc).strftime(
    "%Y%m%dT%H%M%SZ"
)

BACKUP_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime_backups"
    / f"uri_phase1_1_2_runtime_configuration_{TIMESTAMP}"
)

BACKUP_TARGET = (
    BACKUP_ROOT
    / "backend"
    / "server"
    / "runtime"
    / "runtime_configuration.py"
)

EVIDENCE_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
    / "runtime"
    / "uri_phase_1"
    / "1_1_2_runtime_configuration"
)

EVIDENCE_JSON = (
    EVIDENCE_ROOT
    / f"runtime_configuration_build_{TIMESTAMP}.json"
)

EVIDENCE_TEXT = (
    EVIDENCE_ROOT
    / f"runtime_configuration_build_{TIMESTAMP}.txt"
)


CONFIGURATION_SOURCE = r'''from __future__ import annotations

"""
Universal Runtime Configuration.

This module owns the centralized, immutable, validated configuration
contract for the Universal Runtime Infrastructure.

It does not start the runtime, select application environments, execute
jobs, initialize workers, or contain product-pipeline business logic.
"""

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping


__all__ = [
    "ALLOWED_ENVIRONMENT_NAMES",
    "CONFIGURATION_ENV_PREFIX",
    "CONFIGURATION_SCHEMA_VERSION",
    "RuntimeConfiguration",
    "RuntimeConfigurationError",
    "RuntimeConfigurationLoader",
    "RuntimeConfigurationSourceError",
    "RuntimeConfigurationValidationError",
    "load_runtime_configuration",
]


CONFIGURATION_SCHEMA_VERSION = "1.0.0"

CONFIGURATION_ENV_PREFIX = "LINKCRAFTOR_RUNTIME_"

ALLOWED_ENVIRONMENT_NAMES = frozenset(
    {
        "development",
        "testing",
        "staging",
        "production",
    }
)

_ALLOWED_LOG_LEVELS = frozenset(
    {
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    }
)

_ALLOWED_STATE_BACKENDS = frozenset(
    {
        "filesystem",
        "memory",
        "database",
    }
)

_RUNTIME_ID_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9_.:-]{2,127}$"
)

_CONFIGURATION_VERSION_PATTERN = re.compile(
    r"^[0-9]+\.[0-9]+\.[0-9]+$"
)

_TRUE_VALUES = frozenset(
    {
        "1",
        "true",
        "yes",
        "on",
        "enabled",
    }
)

_FALSE_VALUES = frozenset(
    {
        "0",
        "false",
        "no",
        "off",
        "disabled",
    }
)

_SECRET_FIELD_PATTERN = re.compile(
    r"(secret|password|token|credential|api[_-]?key)",
    re.IGNORECASE,
)

_CONFIGURATION_FIELDS = frozenset(
    {
        "configuration_schema_version",
        "runtime_id",
        "product_name",
        "environment",
        "debug",
        "log_level",
        "data_root",
        "state_backend",
        "worker_enabled",
        "startup_timeout_seconds",
        "shutdown_timeout_seconds",
        "queue_poll_interval_seconds",
        "max_concurrency",
        "strict_compatibility",
        "schema_auto_migrate",
    }
)

_ENVIRONMENT_FIELD_MAP = MappingProxyType(
    {
        "RUNTIME_ID": "runtime_id",
        "PRODUCT_NAME": "product_name",
        "ENVIRONMENT": "environment",
        "DEBUG": "debug",
        "LOG_LEVEL": "log_level",
        "DATA_ROOT": "data_root",
        "STATE_BACKEND": "state_backend",
        "WORKER_ENABLED": "worker_enabled",
        "STARTUP_TIMEOUT_SECONDS": (
            "startup_timeout_seconds"
        ),
        "SHUTDOWN_TIMEOUT_SECONDS": (
            "shutdown_timeout_seconds"
        ),
        "QUEUE_POLL_INTERVAL_SECONDS": (
            "queue_poll_interval_seconds"
        ),
        "MAX_CONCURRENCY": "max_concurrency",
        "STRICT_COMPATIBILITY": (
            "strict_compatibility"
        ),
        "SCHEMA_AUTO_MIGRATE": (
            "schema_auto_migrate"
        ),
    }
)

_DEFAULT_VALUES = MappingProxyType(
    {
        "configuration_schema_version": (
            CONFIGURATION_SCHEMA_VERSION
        ),
        "runtime_id": "linkcraftor.primary",
        "product_name": "LinkCraftor",
        "environment": "development",
        "debug": False,
        "log_level": "INFO",
        "data_root": "backend/server/data/runtime",
        "state_backend": "filesystem",
        "worker_enabled": True,
        "startup_timeout_seconds": 30.0,
        "shutdown_timeout_seconds": 30.0,
        "queue_poll_interval_seconds": 1.0,
        "max_concurrency": 4,
        "strict_compatibility": True,
        "schema_auto_migrate": False,
    }
)


class RuntimeConfigurationError(RuntimeError):
    """Base error for runtime-configuration failures."""


class RuntimeConfigurationSourceError(
    RuntimeConfigurationError
):
    """Raised for unknown or invalid configuration sources."""


class RuntimeConfigurationValidationError(
    RuntimeConfigurationError
):
    """Raised when configuration values violate the contract."""


def _serialize_value(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)

    return value


@dataclass(frozen=True, slots=True)
class RuntimeConfiguration:
    """
    Immutable resolved runtime configuration.

    field_sources records where each final value came from:

    - default
    - environment:<VARIABLE>
    - override
    """

    configuration_schema_version: str
    runtime_id: str
    product_name: str
    environment: str
    debug: bool
    log_level: str
    data_root: Path
    state_backend: str
    worker_enabled: bool
    startup_timeout_seconds: float
    shutdown_timeout_seconds: float
    queue_poll_interval_seconds: float
    max_concurrency: int
    strict_compatibility: bool
    schema_auto_migrate: bool
    field_sources: Mapping[str, str]

    def __post_init__(self) -> None:
        self._validate()

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    def source_for(self, field_name: str) -> str:
        normalized = str(field_name or "").strip()

        if normalized not in _CONFIGURATION_FIELDS:
            raise RuntimeConfigurationSourceError(
                f"Unknown runtime configuration field: "
                f"{field_name!r}"
            )

        try:
            return self.field_sources[normalized]
        except KeyError as exc:
            raise RuntimeConfigurationSourceError(
                "No source record exists for runtime "
                f"configuration field {normalized!r}."
            ) from exc

    def to_dict(
        self,
        *,
        include_sources: bool = False,
        redact_sensitive: bool = True,
    ) -> dict[str, Any]:
        values: dict[str, Any] = {
            "configuration_schema_version": (
                self.configuration_schema_version
            ),
            "runtime_id": self.runtime_id,
            "product_name": self.product_name,
            "environment": self.environment,
            "debug": self.debug,
            "log_level": self.log_level,
            "data_root": str(self.data_root),
            "state_backend": self.state_backend,
            "worker_enabled": self.worker_enabled,
            "startup_timeout_seconds": (
                self.startup_timeout_seconds
            ),
            "shutdown_timeout_seconds": (
                self.shutdown_timeout_seconds
            ),
            "queue_poll_interval_seconds": (
                self.queue_poll_interval_seconds
            ),
            "max_concurrency": self.max_concurrency,
            "strict_compatibility": (
                self.strict_compatibility
            ),
            "schema_auto_migrate": (
                self.schema_auto_migrate
            ),
        }

        if redact_sensitive:
            for key in tuple(values):
                if _SECRET_FIELD_PATTERN.search(key):
                    values[key] = "[REDACTED]"

        if include_sources:
            values["field_sources"] = dict(
                self.field_sources
            )

        return values

    def fingerprint(self) -> str:
        """
        Return a deterministic value fingerprint.

        Source labels are intentionally excluded. Equal effective
        configuration values produce equal fingerprints regardless of
        whether they came from defaults, environment variables, or
        explicit overrides.
        """

        payload = json.dumps(
            self.to_dict(
                include_sources=False,
                redact_sensitive=False,
            ),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

        return hashlib.sha256(payload).hexdigest()

    def _validate(self) -> None:
        if not _CONFIGURATION_VERSION_PATTERN.fullmatch(
            self.configuration_schema_version
        ):
            raise RuntimeConfigurationValidationError(
                "configuration_schema_version must use "
                "MAJOR.MINOR.PATCH format."
            )

        if (
            self.configuration_schema_version
            != CONFIGURATION_SCHEMA_VERSION
        ):
            raise RuntimeConfigurationValidationError(
                "Unsupported configuration schema version: "
                f"{self.configuration_schema_version!r}."
            )

        if not _RUNTIME_ID_PATTERN.fullmatch(
            self.runtime_id
        ):
            raise RuntimeConfigurationValidationError(
                "runtime_id must be 3-128 characters and "
                "contain only letters, numbers, dots, "
                "underscores, colons, or hyphens."
            )

        if not self.product_name.strip():
            raise RuntimeConfigurationValidationError(
                "product_name must not be empty."
            )

        if len(self.product_name) > 128:
            raise RuntimeConfigurationValidationError(
                "product_name must not exceed 128 characters."
            )

        if (
            self.environment
            not in ALLOWED_ENVIRONMENT_NAMES
        ):
            raise RuntimeConfigurationValidationError(
                "environment must be one of: "
                + ", ".join(
                    sorted(ALLOWED_ENVIRONMENT_NAMES)
                )
            )

        if self.log_level not in _ALLOWED_LOG_LEVELS:
            raise RuntimeConfigurationValidationError(
                "log_level must be one of: "
                + ", ".join(sorted(_ALLOWED_LOG_LEVELS))
            )

        if not self.data_root.is_absolute():
            raise RuntimeConfigurationValidationError(
                "data_root must be resolved to an absolute path."
            )

        if self.state_backend not in _ALLOWED_STATE_BACKENDS:
            raise RuntimeConfigurationValidationError(
                "state_backend must be one of: "
                + ", ".join(
                    sorted(_ALLOWED_STATE_BACKENDS)
                )
            )

        if not (
            0.1
            <= self.startup_timeout_seconds
            <= 3600.0
        ):
            raise RuntimeConfigurationValidationError(
                "startup_timeout_seconds must be between "
                "0.1 and 3600 seconds."
            )

        if not (
            0.1
            <= self.shutdown_timeout_seconds
            <= 3600.0
        ):
            raise RuntimeConfigurationValidationError(
                "shutdown_timeout_seconds must be between "
                "0.1 and 3600 seconds."
            )

        if not (
            0.05
            <= self.queue_poll_interval_seconds
            <= 300.0
        ):
            raise RuntimeConfigurationValidationError(
                "queue_poll_interval_seconds must be between "
                "0.05 and 300 seconds."
            )

        if not 1 <= self.max_concurrency <= 1024:
            raise RuntimeConfigurationValidationError(
                "max_concurrency must be between 1 and 1024."
            )

        if self.is_production and self.debug:
            raise RuntimeConfigurationValidationError(
                "debug must be disabled in production."
            )

        if (
            self.is_production
            and self.state_backend == "memory"
        ):
            raise RuntimeConfigurationValidationError(
                "The memory state backend is not permitted "
                "in production."
            )

        if (
            self.is_production
            and self.schema_auto_migrate
        ):
            raise RuntimeConfigurationValidationError(
                "Automatic runtime schema migration is not "
                "permitted in production."
            )

        missing_sources = sorted(
            field
            for field in _CONFIGURATION_FIELDS
            if field not in self.field_sources
        )

        if missing_sources:
            raise RuntimeConfigurationValidationError(
                "Missing configuration-source records: "
                + ", ".join(missing_sources)
            )


class RuntimeConfigurationLoader:
    """
    Resolve runtime configuration from controlled sources.

    Precedence, from lowest to highest:

    1. Built-in defaults
    2. Runtime-prefixed environment variables
    3. Explicit overrides

    The loader does not mutate os.environ and does not create any
    configured directories.
    """

    __slots__ = (
        "_project_root",
        "_environment_prefix",
    )

    def __init__(
        self,
        *,
        project_root: Path,
        environment_prefix: str = (
            CONFIGURATION_ENV_PREFIX
        ),
    ) -> None:
        resolved_root = Path(project_root).expanduser()

        if not resolved_root.is_absolute():
            resolved_root = resolved_root.resolve()

        normalized_prefix = str(
            environment_prefix or ""
        ).strip().upper()

        if not normalized_prefix:
            raise RuntimeConfigurationSourceError(
                "environment_prefix must not be empty."
            )

        if not normalized_prefix.endswith("_"):
            raise RuntimeConfigurationSourceError(
                "environment_prefix must end with an underscore."
            )

        self._project_root = resolved_root.resolve()
        self._environment_prefix = normalized_prefix

    @property
    def project_root(self) -> Path:
        return self._project_root

    @property
    def environment_prefix(self) -> str:
        return self._environment_prefix

    def defaults(self) -> Mapping[str, Any]:
        return MappingProxyType(dict(_DEFAULT_VALUES))

    def load(
        self,
        *,
        environ: Mapping[str, str] | None = None,
        overrides: Mapping[str, Any] | None = None,
    ) -> RuntimeConfiguration:
        environment_values = (
            os.environ
            if environ is None
            else environ
        )

        explicit_overrides = (
            {}
            if overrides is None
            else dict(overrides)
        )

        unknown_override_fields = sorted(
            set(explicit_overrides)
            - _CONFIGURATION_FIELDS
        )

        if unknown_override_fields:
            raise RuntimeConfigurationSourceError(
                "Unknown runtime configuration overrides: "
                + ", ".join(unknown_override_fields)
            )

        if "field_sources" in explicit_overrides:
            raise RuntimeConfigurationSourceError(
                "field_sources cannot be supplied as an override."
            )

        values = dict(_DEFAULT_VALUES)

        sources = {
            field: "default"
            for field in _CONFIGURATION_FIELDS
        }

        environment_updates = (
            self._collect_environment_updates(
                environment_values
            )
        )

        for field, update in environment_updates.items():
            raw_value, source_name = update
            values[field] = self._coerce_value(
                field,
                raw_value,
            )
            sources[field] = source_name

        for field, raw_value in explicit_overrides.items():
            values[field] = self._coerce_value(
                field,
                raw_value,
            )
            sources[field] = "override"

        values["data_root"] = self._resolve_data_root(
            values["data_root"]
        )

        frozen_sources = MappingProxyType(
            dict(sources)
        )

        return RuntimeConfiguration(
            configuration_schema_version=str(
                values[
                    "configuration_schema_version"
                ]
            ),
            runtime_id=str(values["runtime_id"]).strip(),
            product_name=str(
                values["product_name"]
            ).strip(),
            environment=str(
                values["environment"]
            ).strip().lower(),
            debug=bool(values["debug"]),
            log_level=str(
                values["log_level"]
            ).strip().upper(),
            data_root=values["data_root"],
            state_backend=str(
                values["state_backend"]
            ).strip().lower(),
            worker_enabled=bool(
                values["worker_enabled"]
            ),
            startup_timeout_seconds=float(
                values["startup_timeout_seconds"]
            ),
            shutdown_timeout_seconds=float(
                values["shutdown_timeout_seconds"]
            ),
            queue_poll_interval_seconds=float(
                values[
                    "queue_poll_interval_seconds"
                ]
            ),
            max_concurrency=int(
                values["max_concurrency"]
            ),
            strict_compatibility=bool(
                values["strict_compatibility"]
            ),
            schema_auto_migrate=bool(
                values["schema_auto_migrate"]
            ),
            field_sources=frozen_sources,
        )

    def _collect_environment_updates(
        self,
        environ: Mapping[str, str],
    ) -> dict[str, tuple[str, str]]:
        updates: dict[str, tuple[str, str]] = {}
        unknown_keys: list[str] = []

        for raw_name, raw_value in environ.items():
            name = str(raw_name).strip()
            upper_name = name.upper()

            if not upper_name.startswith(
                self._environment_prefix
            ):
                continue

            suffix = upper_name[
                len(self._environment_prefix):
            ]

            field = _ENVIRONMENT_FIELD_MAP.get(
                suffix
            )

            if field is None:
                unknown_keys.append(name)
                continue

            updates[field] = (
                str(raw_value),
                f"environment:{name}",
            )

        if unknown_keys:
            raise RuntimeConfigurationSourceError(
                "Unknown runtime environment variables: "
                + ", ".join(sorted(unknown_keys))
            )

        return updates

    def _coerce_value(
        self,
        field: str,
        raw_value: Any,
    ) -> Any:
        if field not in _CONFIGURATION_FIELDS:
            raise RuntimeConfigurationSourceError(
                f"Unknown runtime configuration field: "
                f"{field!r}"
            )

        if field in {
            "debug",
            "worker_enabled",
            "strict_compatibility",
            "schema_auto_migrate",
        }:
            return self._parse_boolean(
                field,
                raw_value,
            )

        if field == "max_concurrency":
            return self._parse_integer(
                field,
                raw_value,
            )

        if field in {
            "startup_timeout_seconds",
            "shutdown_timeout_seconds",
            "queue_poll_interval_seconds",
        }:
            return self._parse_float(
                field,
                raw_value,
            )

        if field == "data_root":
            if isinstance(raw_value, Path):
                return raw_value

            return Path(
                str(raw_value or "").strip()
            )

        return str(raw_value or "").strip()

    def _parse_boolean(
        self,
        field: str,
        raw_value: Any,
    ) -> bool:
        if isinstance(raw_value, bool):
            return raw_value

        normalized = str(raw_value or "").strip().lower()

        if normalized in _TRUE_VALUES:
            return True

        if normalized in _FALSE_VALUES:
            return False

        raise RuntimeConfigurationValidationError(
            f"{field} must be a recognized boolean value."
        )

    def _parse_integer(
        self,
        field: str,
        raw_value: Any,
    ) -> int:
        if isinstance(raw_value, bool):
            raise RuntimeConfigurationValidationError(
                f"{field} must be an integer, not a boolean."
            )

        try:
            return int(str(raw_value).strip())
        except (TypeError, ValueError) as exc:
            raise RuntimeConfigurationValidationError(
                f"{field} must be a valid integer."
            ) from exc

    def _parse_float(
        self,
        field: str,
        raw_value: Any,
    ) -> float:
        if isinstance(raw_value, bool):
            raise RuntimeConfigurationValidationError(
                f"{field} must be numeric, not a boolean."
            )

        try:
            return float(str(raw_value).strip())
        except (TypeError, ValueError) as exc:
            raise RuntimeConfigurationValidationError(
                f"{field} must be a valid number."
            ) from exc

    def _resolve_data_root(
        self,
        raw_value: Any,
    ) -> Path:
        path = (
            raw_value
            if isinstance(raw_value, Path)
            else Path(str(raw_value))
        ).expanduser()

        if not path.is_absolute():
            path = self._project_root / path

        return path.resolve()


def load_runtime_configuration(
    *,
    project_root: Path,
    environ: Mapping[str, str] | None = None,
    overrides: Mapping[str, Any] | None = None,
) -> RuntimeConfiguration:
    """Convenience entry point for configuration resolution."""

    return RuntimeConfigurationLoader(
        project_root=project_root
    ).load(
        environ=environ,
        overrides=overrides,
    )
'''


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None

    return sha256_bytes(path.read_bytes())


def fail(message: str) -> None:
    raise RuntimeError(message)


def load_module(
    path: Path,
    module_name: str,
) -> Any:
    spec = importlib.util.spec_from_file_location(
        module_name,
        path,
    )

    if spec is None or spec.loader is None:
        fail(
            f"Could not create import specification "
            f"for {path}."
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module

    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        raise

    return module


def unload_module(module_name: str) -> None:
    sys.modules.pop(module_name, None)


def verify_ast_contract(
    path: Path,
) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(path))

    classes: dict[str, set[str]] = {}
    functions: set[str] = set()

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            classes[node.name] = {
                child.name
                for child in node.body
                if isinstance(
                    child,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                    ),
                )
            }

        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            functions.add(node.name)

    required_classes = {
        "RuntimeConfiguration",
        "RuntimeConfigurationLoader",
        "RuntimeConfigurationError",
        "RuntimeConfigurationSourceError",
        "RuntimeConfigurationValidationError",
    }

    required_configuration_methods = {
        "source_for",
        "to_dict",
        "fingerprint",
        "_validate",
    }

    required_loader_methods = {
        "defaults",
        "load",
        "_collect_environment_updates",
        "_coerce_value",
        "_parse_boolean",
        "_parse_integer",
        "_parse_float",
        "_resolve_data_root",
    }

    missing_classes = sorted(
        required_classes - set(classes)
    )

    missing_configuration_methods = sorted(
        required_configuration_methods
        - classes.get(
            "RuntimeConfiguration",
            set(),
        )
    )

    missing_loader_methods = sorted(
        required_loader_methods
        - classes.get(
            "RuntimeConfigurationLoader",
            set(),
        )
    )

    if missing_classes:
        fail(
            "Runtime configuration AST contract is "
            "missing classes: "
            + ", ".join(missing_classes)
        )

    if missing_configuration_methods:
        fail(
            "RuntimeConfiguration is missing methods: "
            + ", ".join(
                missing_configuration_methods
            )
        )

    if missing_loader_methods:
        fail(
            "RuntimeConfigurationLoader is missing methods: "
            + ", ".join(missing_loader_methods)
        )

    if "load_runtime_configuration" not in functions:
        fail(
            "The load_runtime_configuration entry point "
            "is missing."
        )

    forbidden_business_terms = (
        "udare",
        "website_article_integrity",
        "article_validation",
        "semantic_intelligence",
        "uploaded_document_unified_content",
        "universal_unified_content_document",
    )

    source_lower = text.lower()

    detected_forbidden_terms = [
        term
        for term in forbidden_business_terms
        if term in source_lower
    ]

    if detected_forbidden_terms:
        fail(
            "Runtime configuration contains pipeline-specific "
            "business terms: "
            + ", ".join(detected_forbidden_terms)
        )

    return {
        "required_classes": sorted(
            required_classes
        ),
        "missing_classes": missing_classes,
        "missing_configuration_methods": (
            missing_configuration_methods
        ),
        "missing_loader_methods": (
            missing_loader_methods
        ),
        "load_entry_point_present": True,
        "pipeline_business_terms_detected": (
            detected_forbidden_terms
        ),
    }


def verify_behavior(
    configuration_module: Any,
    kernel_module: Any,
) -> dict[str, Any]:
    Loader = (
        configuration_module.RuntimeConfigurationLoader
    )

    Configuration = (
        configuration_module.RuntimeConfiguration
    )

    SourceError = (
        configuration_module
        .RuntimeConfigurationSourceError
    )

    ValidationError = (
        configuration_module
        .RuntimeConfigurationValidationError
    )

    Kernel = kernel_module.UniversalRuntimeKernel

    assertions: dict[str, str] = {}

    with tempfile.TemporaryDirectory(
        prefix="uri_runtime_config_test_"
    ) as temporary_directory:
        temporary_root = Path(
            temporary_directory
        ).resolve()

        loader = Loader(
            project_root=temporary_root
        )

        default_configuration = loader.load(
            environ={}
        )

        if not isinstance(
            default_configuration,
            Configuration,
        ):
            fail(
                "Default configuration has the wrong type."
            )

        if (
            default_configuration.runtime_id
            != "linkcraftor.primary"
        ):
            fail(
                "Default runtime_id is incorrect."
            )

        if (
            default_configuration.environment
            != "development"
        ):
            fail(
                "Default environment is incorrect."
            )

        if not default_configuration.data_root.is_absolute():
            fail(
                "Default data_root was not resolved "
                "to an absolute path."
            )

        if default_configuration.data_root.exists():
            fail(
                "Loading configuration unexpectedly "
                "created the data_root directory."
            )

        assertions[
            "default_resolution"
        ] = "PASS"

        environment_values = {
            "LINKCRAFTOR_RUNTIME_ENVIRONMENT": (
                "testing"
            ),
            "LINKCRAFTOR_RUNTIME_DEBUG": "yes",
            "LINKCRAFTOR_RUNTIME_LOG_LEVEL": (
                "warning"
            ),
            "LINKCRAFTOR_RUNTIME_MAX_CONCURRENCY": (
                "8"
            ),
            "LINKCRAFTOR_RUNTIME_WORKER_ENABLED": (
                "off"
            ),
            "UNRELATED_APPLICATION_VALUE": "ignored",
        }

        resolved = loader.load(
            environ=environment_values,
            overrides={
                "max_concurrency": 12,
                "queue_poll_interval_seconds": 0.25,
            },
        )

        if resolved.environment != "testing":
            fail(
                "Environment variable resolution failed."
            )

        if resolved.debug is not True:
            fail(
                "Boolean environment parsing failed."
            )

        if resolved.log_level != "WARNING":
            fail(
                "Log-level normalization failed."
            )

        if resolved.worker_enabled is not False:
            fail(
                "False boolean environment parsing failed."
            )

        if resolved.max_concurrency != 12:
            fail(
                "Override did not take precedence over "
                "the environment value."
            )

        if (
            resolved.queue_poll_interval_seconds
            != 0.25
        ):
            fail(
                "Explicit numeric override failed."
            )

        assertions[
            "source_precedence"
        ] = "PASS"

        if (
            resolved.source_for("environment")
            != (
                "environment:"
                "LINKCRAFTOR_RUNTIME_ENVIRONMENT"
            )
        ):
            fail(
                "Environment source tracking is incorrect."
            )

        if (
            resolved.source_for("max_concurrency")
            != "override"
        ):
            fail(
                "Override source tracking is incorrect."
            )

        if (
            resolved.source_for(
                "shutdown_timeout_seconds"
            )
            != "default"
        ):
            fail(
                "Default source tracking is incorrect."
            )

        assertions[
            "field_source_tracking"
        ] = "PASS"

        unknown_override_rejected = False

        try:
            loader.load(
                environ={},
                overrides={
                    "unknown_runtime_setting": True,
                },
            )
        except SourceError:
            unknown_override_rejected = True

        if not unknown_override_rejected:
            fail(
                "Unknown override was not rejected."
            )

        assertions[
            "unknown_override_rejection"
        ] = "PASS"

        unknown_environment_rejected = False

        try:
            loader.load(
                environ={
                    "LINKCRAFTOR_RUNTIME_TYPO_VALUE": (
                        "1"
                    )
                }
            )
        except SourceError:
            unknown_environment_rejected = True

        if not unknown_environment_rejected:
            fail(
                "Unknown runtime environment variable "
                "was not rejected."
            )

        assertions[
            "unknown_environment_rejection"
        ] = "PASS"

        invalid_boolean_rejected = False

        try:
            loader.load(
                environ={
                    "LINKCRAFTOR_RUNTIME_DEBUG": (
                        "sometimes"
                    )
                }
            )
        except ValidationError:
            invalid_boolean_rejected = True

        if not invalid_boolean_rejected:
            fail(
                "Invalid boolean configuration "
                "was not rejected."
            )

        assertions[
            "invalid_boolean_rejection"
        ] = "PASS"

        invalid_concurrency_rejected = False

        try:
            loader.load(
                environ={},
                overrides={
                    "max_concurrency": 0,
                },
            )
        except ValidationError:
            invalid_concurrency_rejected = True

        if not invalid_concurrency_rejected:
            fail(
                "Invalid concurrency limit was not rejected."
            )

        assertions[
            "range_validation"
        ] = "PASS"

        production_debug_rejected = False

        try:
            loader.load(
                environ={},
                overrides={
                    "environment": "production",
                    "debug": True,
                },
            )
        except ValidationError:
            production_debug_rejected = True

        if not production_debug_rejected:
            fail(
                "Production debug mode was not rejected."
            )

        assertions[
            "production_debug_protection"
        ] = "PASS"

        production_memory_rejected = False

        try:
            loader.load(
                environ={},
                overrides={
                    "environment": "production",
                    "state_backend": "memory",
                },
            )
        except ValidationError:
            production_memory_rejected = True

        if not production_memory_rejected:
            fail(
                "Production memory state backend "
                "was not rejected."
            )

        assertions[
            "production_state_backend_protection"
        ] = "PASS"

        production_migration_rejected = False

        try:
            loader.load(
                environ={},
                overrides={
                    "environment": "production",
                    "schema_auto_migrate": True,
                },
            )
        except ValidationError:
            production_migration_rejected = True

        if not production_migration_rejected:
            fail(
                "Production automatic schema migration "
                "was not rejected."
            )

        assertions[
            "production_migration_protection"
        ] = "PASS"

        immutable_configuration = False

        try:
            resolved.debug = False
        except (AttributeError, TypeError):
            immutable_configuration = True

        if not immutable_configuration:
            fail(
                "Runtime configuration was mutable."
            )

        assertions[
            "immutable_configuration"
        ] = "PASS"

        immutable_sources = False

        try:
            resolved.field_sources[
                "debug"
            ] = "illegal"
        except TypeError:
            immutable_sources = True

        if not immutable_sources:
            fail(
                "Configuration source mapping was mutable."
            )

        assertions[
            "immutable_source_mapping"
        ] = "PASS"

        same_values_different_sources = loader.load(
            environ={},
            overrides={
                "environment": "testing",
                "debug": True,
                "log_level": "warning",
                "max_concurrency": 12,
                "worker_enabled": False,
                "queue_poll_interval_seconds": 0.25,
            },
        )

        if (
            resolved.fingerprint()
            != same_values_different_sources.fingerprint()
        ):
            fail(
                "Equal effective configuration values "
                "produced different fingerprints."
            )

        changed_configuration = loader.load(
            environ={},
            overrides={
                "max_concurrency": 13,
            },
        )

        if (
            default_configuration.fingerprint()
            == changed_configuration.fingerprint()
        ):
            fail(
                "Different configuration values produced "
                "the same fingerprint."
            )

        assertions[
            "deterministic_fingerprint"
        ] = "PASS"

        original_process_environment = dict(
            os.environ
        )

        loader.load(
            environ={
                "LINKCRAFTOR_RUNTIME_LOG_LEVEL": (
                    "ERROR"
                )
            }
        )

        if dict(os.environ) != original_process_environment:
            fail(
                "Configuration loading mutated os.environ."
            )

        assertions[
            "environment_non_mutation"
        ] = "PASS"

        serialized = resolved.to_dict(
            include_sources=True
        )

        if not isinstance(
            serialized.get("data_root"),
            str,
        ):
            fail(
                "Configuration serialization did not "
                "convert data_root to a string."
            )

        if "field_sources" not in serialized:
            fail(
                "Configuration serialization omitted "
                "requested source records."
            )

        assertions[
            "safe_serialization"
        ] = "PASS"

        kernel = Kernel(
            runtime_id=resolved.runtime_id,
            product_name=resolved.product_name,
        )

        binding = kernel.bind_component(
            "configuration",
            resolved,
        )

        if binding.key != "configuration":
            fail(
                "Kernel configuration binding failed."
            )

        retrieved = kernel.get_component(
            "configuration",
            Configuration,
        )

        if retrieved is not resolved:
            fail(
                "Kernel returned the wrong configuration "
                "component."
            )

        if (
            "configuration"
            in kernel.missing_foundation_components()
        ):
            fail(
                "Kernel still reported configuration "
                "as missing after binding."
            )

        assertions[
            "kernel_configuration_binding"
        ] = "PASS"

        return {
            "assertions": assertions,
            "default_fingerprint": (
                default_configuration.fingerprint()
            ),
            "resolved_fingerprint": (
                resolved.fingerprint()
            ),
            "resolved_environment": (
                resolved.environment
            ),
            "resolved_max_concurrency": (
                resolved.max_concurrency
            ),
            "resolved_data_root": str(
                resolved.data_root
            ),
            "kernel_generation": (
                kernel.generation
            ),
            "kernel_missing_foundation_components": (
                list(
                    kernel
                    .missing_foundation_components()
                )
            ),
        }


def rollback(
    *,
    target_existed: bool,
) -> None:
    if target_existed:
        if not BACKUP_TARGET.exists():
            raise RuntimeError(
                "Runtime configuration rollback "
                "backup is missing."
            )

        TARGET.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            BACKUP_TARGET,
            TARGET,
        )

    elif TARGET.exists():
        TARGET.unlink()


def main() -> int:
    print("=" * 78)
    print("UNIVERSAL RUNTIME INFRASTRUCTURE")
    print("1.1.2 — RUNTIME CONFIGURATION BUILD")
    print("=" * 78)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Target:       {TARGET}")
    print()

    required_files = [
        KERNEL_FILE,
        EXISTING_RUNTIME_FACADE,
        MAIN_FILE,
    ]

    missing_required_files = [
        path
        for path in required_files
        if not path.exists()
    ]

    if missing_required_files:
        fail(
            "Required files are missing:\n"
            + "\n".join(
                str(path)
                for path in missing_required_files
            )
        )

    target_existed = TARGET.exists()
    target_original_hash = sha256_file(TARGET)

    protected_hashes_before = {
        "kernel": sha256_file(KERNEL_FILE),
        "runtime_facade": sha256_file(
            EXISTING_RUNTIME_FACADE
        ),
        "main": sha256_file(MAIN_FILE),
    }

    if target_existed:
        BACKUP_TARGET.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            TARGET,
            BACKUP_TARGET,
        )

        print(
            "Existing runtime configuration backed up:"
        )
        print(BACKUP_TARGET)
        print()

    TARGET.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    configuration_module_name = (
        "_uri_phase_1_1_2_runtime_configuration_test"
    )

    kernel_module_name = (
        "_uri_phase_1_1_2_runtime_kernel_test"
    )

    try:
        TARGET.write_text(
            CONFIGURATION_SOURCE,
            encoding="utf-8",
            newline="\n",
        )

        py_compile.compile(
            str(TARGET),
            doraise=True,
        )

        py_compile.compile(
            str(KERNEL_FILE),
            doraise=True,
        )

        py_compile.compile(
            str(MAIN_FILE),
            doraise=True,
        )

        ast_contract = verify_ast_contract(
            TARGET
        )

        configuration_module = load_module(
            TARGET,
            configuration_module_name,
        )

        kernel_module = load_module(
            KERNEL_FILE,
            kernel_module_name,
        )

        behavioral_results = verify_behavior(
            configuration_module,
            kernel_module,
        )

        protected_hashes_after = {
            "kernel": sha256_file(KERNEL_FILE),
            "runtime_facade": sha256_file(
                EXISTING_RUNTIME_FACADE
            ),
            "main": sha256_file(MAIN_FILE),
        }

        if (
            protected_hashes_before
            != protected_hashes_after
        ):
            fail(
                "A protected existing runtime file "
                "changed unexpectedly."
            )

    except Exception:
        rollback(
            target_existed=target_existed,
        )

        print()
        print("ROLLBACK COMPLETE")
        print(
            "Runtime configuration verification failed. "
            "The previous filesystem state was restored."
        )
        raise

    finally:
        unload_module(
            configuration_module_name
        )
        unload_module(
            kernel_module_name
        )

    target_final_hash = sha256_file(TARGET)

    evidence = {
        "build_version": BUILD_VERSION,
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "target": str(TARGET),
        "target_existed_before_build": (
            target_existed
        ),
        "target_backup": (
            str(BACKUP_TARGET)
            if target_existed
            else None
        ),
        "target_original_sha256": (
            target_original_hash
        ),
        "target_final_sha256": (
            target_final_hash
        ),
        "protected_hashes_before": (
            protected_hashes_before
        ),
        "protected_hashes_after": (
            protected_hashes_after
        ),
        "verification": {
            "configuration_py_compile": "PASS",
            "kernel_py_compile": "PASS",
            "main_py_compile": "PASS",
            "ast_contract": "PASS",
            "behavioral_contract": "PASS",
            "source_precedence": "PASS",
            "validation_contract": "PASS",
            "immutability_contract": "PASS",
            "production_safety_contract": "PASS",
            "kernel_binding_contract": "PASS",
            "business_logic_agnostic_test": "PASS",
            "protected_files_unchanged": "PASS",
            "automatic_rollback_required": False,
        },
        "ast_contract_details": ast_contract,
        "behavioral_results": behavioral_results,
        "phase_status": {
            "phase": "1",
            "item": "1.1.2",
            "name": "Runtime Configuration",
            "implementation_status": "IMPLEMENTED",
            "verification_status": "PASS",
            "kernel_binding_status": "PASS",
            "application_boot_integration": "PENDING",
            "certification_status": "NOT_CERTIFIED",
        },
    }

    EVIDENCE_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    EVIDENCE_JSON.write_text(
        json.dumps(
            evidence,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    evidence_lines = [
        "=" * 78,
        "UNIVERSAL RUNTIME INFRASTRUCTURE",
        "1.1.2 — RUNTIME CONFIGURATION EVIDENCE",
        "=" * 78,
        "",
        f"Build version: {BUILD_VERSION}",
        f"Timestamp UTC: {evidence['timestamp_utc']}",
        f"Target: {TARGET}",
        "",
        "VERIFICATION",
        "-" * 78,
        "Runtime configuration compilation: PASS",
        "Universal Runtime Kernel compilation: PASS",
        "main.py compilation: PASS",
        "Configuration AST contract: PASS",
        "Business-logic-agnostic boundary: PASS",
        "Protected existing files unchanged: PASS",
        "",
        "BEHAVIORAL TESTS",
        "-" * 78,
    ]

    for name, status in behavioral_results[
        "assertions"
    ].items():
        evidence_lines.append(
            f"{name}: {status}"
        )

    evidence_lines.extend(
        [
            "",
            "KERNEL INTEGRATION",
            "-" * 78,
            "Configuration kernel binding: PASS",
            (
                "Kernel generation after binding: "
                f"{behavioral_results['kernel_generation']}"
            ),
            "",
            "CHECKLIST POSITION",
            "-" * 78,
            "1.1.1 kernel implementation: PASS",
            (
                "1.1.1 configuration-binding "
                "compatibility: PASS"
            ),
            "1.1.1 full runtime integration: PENDING",
            "1.1.2 implementation: PASS",
            "1.1.2 isolated verification: PASS",
            "1.1.2 kernel binding: PASS",
            (
                "1.1.2 application boot integration: "
                "PENDING"
            ),
            "1.1.2 certification: NOT CERTIFIED",
            "Phase 1 certification: NOT CERTIFIED",
            "",
        ]
    )

    EVIDENCE_TEXT.write_text(
        "\n".join(evidence_lines),
        encoding="utf-8",
    )

    print("BUILD VERIFICATION")
    print("-" * 78)
    print(
        "Runtime configuration compilation:  PASS"
    )
    print(
        "Universal Runtime Kernel compilation: PASS"
    )
    print(
        "main.py compilation:                  PASS"
    )
    print(
        "Configuration AST contract:           PASS"
    )
    print(
        "Configuration behavioral contract:    PASS"
    )
    print(
        "Source precedence and tracking:        PASS"
    )
    print(
        "Strict validation:                     PASS"
    )
    print(
        "Production safety controls:            PASS"
    )
    print(
        "Immutable configuration contract:      PASS"
    )
    print(
        "Kernel configuration binding:          PASS"
    )
    print(
        "Business-logic-agnostic boundary:      PASS"
    )
    print(
        "Protected existing files unchanged:    PASS"
    )
    print()

    print("FILES")
    print("-" * 78)
    print(f"Configuration: {TARGET}")
    print(f"Evidence JSON: {EVIDENCE_JSON}")
    print(f"Evidence text: {EVIDENCE_TEXT}")
    print()

    print("1.1.2 RUNTIME CONFIGURATION")
    print("IMPLEMENTATION: PASS")
    print("ISOLATED VERIFICATION: PASS")
    print("KERNEL BINDING: PASS")
    print("APPLICATION BOOT INTEGRATION: PENDING")
    print("CERTIFICATION: NOT CERTIFIED")
    print()
    print("NO PRODUCTION DATA WAS MODIFIED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
