from __future__ import annotations

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
