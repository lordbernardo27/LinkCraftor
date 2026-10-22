from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field, fields, is_dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Any, ClassVar

from backend.server.runtime.runtime_compatibility import (
    RuntimeVersionRequirement,
)
from backend.server.runtime.runtime_configuration import (
    RuntimeConfiguration,
)


RUNTIME_REGISTRATION_PACKAGE_SCHEMA_VERSION = (
    "universal_runtime_registration_package_v1"
)

CANONICAL_RUNTIME_VERSION_CONTRACTS = frozenset(
    {
        "manifest.schema",
        "runtime.version",
        "kernel.api",
        "service.contract",
        "job.contract",
        "state.schema",
        "configuration.schema",
    }
)


class RuntimeRegistrationPackageError(ValueError):
    """Base error for registration-package failures."""


class RuntimeRegistrationPackageValidationError(
    RuntimeRegistrationPackageError
):
    """Raised when package declarations fail closed."""


def _empty_mapping() -> Mapping[str, Any]:
    return MappingProxyType({})


def _required_text(
    value: Any,
    field_name: str,
) -> str:
    normalized = str(value or "").strip()

    if not normalized:
        raise RuntimeRegistrationPackageValidationError(
            f"{field_name} must be a non-empty string."
        )

    return normalized


def _optional_text(
    value: Any,
) -> str | None:
    normalized = str(value or "").strip()
    return normalized or None


def _string_tuple(
    values: Iterable[Any] | Any | None,
    field_name: str,
) -> tuple[str, ...]:
    if values is None:
        return ()

    try:
        source = (
            (values,)
            if isinstance(values, str)
            else tuple(values)
        )
    except TypeError as exc:
        raise RuntimeRegistrationPackageValidationError(
            f"{field_name} must be an iterable of strings."
        ) from exc

    result: list[str] = []
    seen: set[str] = set()

    for raw_value in source:
        value = _required_text(
            raw_value,
            field_name,
        )

        if value in seen:
            raise RuntimeRegistrationPackageValidationError(
                f"{field_name} contains duplicate value "
                f"{value!r}."
            )

        seen.add(value)
        result.append(value)

    return tuple(result)


def _freeze(
    value: Any,
    field_name: str,
    active: set[int],
) -> Any:
    if value is None or isinstance(
        value,
        (str, bool, int),
    ):
        return value

    if isinstance(value, float):
        if not math.isfinite(value):
            raise RuntimeRegistrationPackageValidationError(
                f"{field_name} contains a non-finite float."
            )

        return value

    if isinstance(
        value,
        (Enum, datetime, date, Path),
    ):
        return value

    if isinstance(
        value,
        RuntimeVersionRequirement,
    ):
        return value

    if isinstance(value, Mapping):
        identity = id(value)

        if identity in active:
            raise RuntimeRegistrationPackageValidationError(
                f"{field_name} contains a cycle."
            )

        active.add(identity)

        try:
            result: dict[str, Any] = {}

            for raw_key, raw_value in value.items():
                key = _required_text(
                    raw_key,
                    f"{field_name} key",
                )

                if key in result:
                    raise RuntimeRegistrationPackageValidationError(
                        f"{field_name} contains duplicate "
                        f"key {key!r}."
                    )

                result[key] = _freeze(
                    raw_value,
                    f"{field_name}.{key}",
                    active,
                )

            return MappingProxyType(result)
        finally:
            active.remove(identity)

    if isinstance(value, (tuple, list)):
        identity = id(value)

        if identity in active:
            raise RuntimeRegistrationPackageValidationError(
                f"{field_name} contains a cycle."
            )

        active.add(identity)

        try:
            return tuple(
                _freeze(
                    item,
                    f"{field_name}[{index}]",
                    active,
                )
                for index, item in enumerate(value)
            )
        finally:
            active.remove(identity)

    if isinstance(value, (set, frozenset)):
        raise RuntimeRegistrationPackageValidationError(
            f"{field_name} cannot contain an unordered set."
        )

    raise RuntimeRegistrationPackageValidationError(
        f"{field_name} contains unsupported type "
        f"{type(value).__name__}."
    )


def _mapping(
    value: Mapping[str, Any] | None,
    field_name: str,
) -> Mapping[str, Any]:
    if value is None:
        return _empty_mapping()

    if not isinstance(value, Mapping):
        raise RuntimeRegistrationPackageValidationError(
            f"{field_name} must be a mapping."
        )

    result = _freeze(
        value,
        field_name,
        set(),
    )

    if not isinstance(result, Mapping):
        raise RuntimeRegistrationPackageValidationError(
            f"{field_name} must normalize to a mapping."
        )

    return result


def _configuration_requirements(
    value: Mapping[str, Any] | None,
) -> Mapping[str, Any]:
    result = _mapping(
        value,
        "configuration_requirements",
    )

    canonical_fields = {
        config_field.name
        for config_field in fields(
            RuntimeConfiguration
        )
    }

    unknown = tuple(
        sorted(
            set(result) - canonical_fields
        )
    )

    if unknown:
        raise RuntimeRegistrationPackageValidationError(
            "Unknown RuntimeConfiguration fields: "
            f"{unknown!r}."
        )

    return result


def _contract_key(
    requirement: RuntimeVersionRequirement,
) -> str:
    contract = getattr(
        requirement,
        "contract",
        "",
    )

    return str(
        getattr(
            contract,
            "value",
            contract,
        )
        or ""
    ).strip()


def _version_requirements(
    value: Mapping[str, Any] | None,
) -> Mapping[str, RuntimeVersionRequirement]:
    if value is None:
        return MappingProxyType({})

    if not isinstance(value, Mapping):
        raise RuntimeRegistrationPackageValidationError(
            "runtime_version_requirements must be a mapping."
        )

    result: dict[
        str,
        RuntimeVersionRequirement,
    ] = {}

    for raw_key, raw_requirement in value.items():
        key = _required_text(
            raw_key,
            "runtime version contract",
        )

        if key not in CANONICAL_RUNTIME_VERSION_CONTRACTS:
            raise RuntimeRegistrationPackageValidationError(
                "Unknown runtime version contract: "
                f"{key!r}."
            )

        if key in result:
            raise RuntimeRegistrationPackageValidationError(
                "Duplicate runtime version contract: "
                f"{key!r}."
            )

        if isinstance(
            raw_requirement,
            RuntimeVersionRequirement,
        ):
            requirement = raw_requirement

        elif isinstance(
            raw_requirement,
            Mapping,
        ):
            constructor_values = dict(
                raw_requirement
            )
            constructor_values.setdefault(
                "contract",
                key,
            )

            try:
                requirement = RuntimeVersionRequirement(
                    **constructor_values
                )
            except Exception as exc:
                raise RuntimeRegistrationPackageValidationError(
                    f"Invalid requirement for {key!r}: "
                    f"{type(exc).__name__}: {exc}"
                ) from exc

        else:
            raise RuntimeRegistrationPackageValidationError(
                "Version requirement values must use "
                "RuntimeVersionRequirement or a mapping."
            )

        actual_key = _contract_key(
            requirement
        )

        if actual_key != key:
            raise RuntimeRegistrationPackageValidationError(
                "Version contract mismatch: "
                f"{key!r} != {actual_key!r}."
            )

        result[key] = requirement

    return MappingProxyType(result)


def _public(
    value: Any,
) -> Any:
    if value is None or isinstance(
        value,
        (str, bool, int, float),
    ):
        return value

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, Mapping):
        return {
            str(key): _public(item)
            for key, item in value.items()
        }

    if isinstance(value, (tuple, list)):
        return [
            _public(item)
            for item in value
        ]

    if is_dataclass(value):
        return {
            data_field.name: _public(
                getattr(
                    value,
                    data_field.name,
                )
            )
            for data_field in fields(value)
        }

    to_dict = getattr(
        value,
        "to_dict",
        None,
    )

    if callable(to_dict):
        return _public(to_dict())

    return str(value)


@dataclass(frozen=True, slots=True)
class RuntimeRegistrationPackage:
    """
    Immutable, side-effect-free runtime registration package.
    """

    schema_version: ClassVar[str] = (
        RUNTIME_REGISTRATION_PACKAGE_SCHEMA_VERSION
    )

    job_type: str
    pipeline: str
    stage: str
    handler_ref: str
    handler: Callable[..., Any] = field(
        repr=False,
        compare=False,
    )

    required_payload_fields: tuple[str, ...] = ()
    required_worker_capabilities: tuple[str, ...] = ()
    predecessor_stages: tuple[str, ...] = ()
    successor_stages: tuple[str, ...] = ()
    idempotency_fields: tuple[str, ...] = ()

    retry_policy: Mapping[str, Any] = field(
        default_factory=_empty_mapping
    )
    concurrency_policy: Mapping[str, Any] = field(
        default_factory=_empty_mapping
    )
    lifecycle_policy: Mapping[str, Any] = field(
        default_factory=_empty_mapping
    )
    configuration_requirements: Mapping[str, Any] = field(
        default_factory=_empty_mapping
    )

    feature_flag_key: str | None = None

    runtime_version_requirements: Mapping[
        str,
        RuntimeVersionRequirement,
    ] = field(
        default_factory=_empty_mapping
    )

    description: str = ""

    metadata: Mapping[str, Any] = field(
        default_factory=_empty_mapping
    )

    persistent: bool = False
    registered_at: str = ""

    # Reserved for A2.2-G deterministic generation.
    registration_fingerprint: str = ""

    def __post_init__(self) -> None:
        if not callable(self.handler):
            raise RuntimeRegistrationPackageValidationError(
                "handler must be callable."
            )

        if not isinstance(self.persistent, bool):
            raise RuntimeRegistrationPackageValidationError(
                "persistent must be a Boolean."
            )

        supplied_fingerprint = (
            _optional_text(
                self.registration_fingerprint
            )
            or ""
        )

        object.__setattr__(
            self,
            "job_type",
            _required_text(
                self.job_type,
                "job_type",
            ),
        )
        object.__setattr__(
            self,
            "pipeline",
            _optional_text(
                self.pipeline
            )
            or "",
        )
        object.__setattr__(
            self,
            "stage",
            _optional_text(
                self.stage
            )
            or "",
        )
        object.__setattr__(
            self,
            "handler_ref",
            _required_text(
                self.handler_ref,
                "handler_ref",
            ),
        )
        object.__setattr__(
            self,
            "required_payload_fields",
            _string_tuple(
                self.required_payload_fields,
                "required_payload_fields",
            ),
        )
        object.__setattr__(
            self,
            "required_worker_capabilities",
            _string_tuple(
                self.required_worker_capabilities,
                "required_worker_capabilities",
            ),
        )
        object.__setattr__(
            self,
            "predecessor_stages",
            _string_tuple(
                self.predecessor_stages,
                "predecessor_stages",
            ),
        )
        object.__setattr__(
            self,
            "successor_stages",
            _string_tuple(
                self.successor_stages,
                "successor_stages",
            ),
        )
        object.__setattr__(
            self,
            "idempotency_fields",
            _string_tuple(
                self.idempotency_fields,
                "idempotency_fields",
            ),
        )
        object.__setattr__(
            self,
            "retry_policy",
            _mapping(
                self.retry_policy,
                "retry_policy",
            ),
        )
        object.__setattr__(
            self,
            "concurrency_policy",
            _mapping(
                self.concurrency_policy,
                "concurrency_policy",
            ),
        )
        object.__setattr__(
            self,
            "lifecycle_policy",
            _mapping(
                self.lifecycle_policy,
                "lifecycle_policy",
            ),
        )
        object.__setattr__(
            self,
            "configuration_requirements",
            _configuration_requirements(
                self.configuration_requirements
            ),
        )
        object.__setattr__(
            self,
            "feature_flag_key",
            _optional_text(
                self.feature_flag_key
            ),
        )
        object.__setattr__(
            self,
            "runtime_version_requirements",
            _version_requirements(
                self.runtime_version_requirements
            ),
        )
        object.__setattr__(
            self,
            "description",
            str(
                self.description or ""
            ).strip(),
        )
        object.__setattr__(
            self,
            "metadata",
            _mapping(
                self.metadata,
                "metadata",
            ),
        )
        object.__setattr__(
            self,
            "registered_at",
            _optional_text(
                self.registered_at
            )
            or "",
        )
        canonical_fingerprint = (
            calculate_runtime_registration_fingerprint(
                self
            )
        )

        if (
            supplied_fingerprint
            and supplied_fingerprint
            != canonical_fingerprint
        ):
            raise RuntimeRegistrationPackageValidationError(
                "registration_fingerprint does not match "
                "the canonical package declarations."
            )

        object.__setattr__(
            self,
            "registration_fingerprint",
            canonical_fingerprint,
        )

    def to_public_dict(
        self,
    ) -> dict[str, Any]:
        """
        Return evidence-safe declarations without the handler.
        """

        return {
            "schema_version": self.schema_version,
            "job_type": self.job_type,
            "pipeline": self.pipeline,
            "stage": self.stage,
            "handler_ref": self.handler_ref,
            "required_payload_fields": list(
                self.required_payload_fields
            ),
            "required_worker_capabilities": list(
                self.required_worker_capabilities
            ),
            "predecessor_stages": list(
                self.predecessor_stages
            ),
            "successor_stages": list(
                self.successor_stages
            ),
            "idempotency_fields": list(
                self.idempotency_fields
            ),
            "retry_policy": _public(
                self.retry_policy
            ),
            "concurrency_policy": _public(
                self.concurrency_policy
            ),
            "lifecycle_policy": _public(
                self.lifecycle_policy
            ),
            "configuration_requirements": _public(
                self.configuration_requirements
            ),
            "feature_flag_key": self.feature_flag_key,
            "runtime_version_requirements": _public(
                self.runtime_version_requirements
            ),
            "description": self.description,
            "metadata": _public(
                self.metadata
            ),
            "persistent": self.persistent,
            "registered_at": self.registered_at,
            "registration_fingerprint": (
                self.registration_fingerprint
            ),
        }


def runtime_registration_fingerprint_payload(
    package: RuntimeRegistrationPackage,
) -> dict[str, Any]:
    """
    Return only declarations participating in registration identity.

    The executable handler object, registration timestamp and
    fingerprint itself are deliberately excluded.
    """

    if not isinstance(
        package,
        RuntimeRegistrationPackage,
    ):
        raise TypeError(
            "package must be a RuntimeRegistrationPackage."
        )

    payload = package.to_public_dict()

    payload.pop(
        "registered_at",
        None,
    )
    payload.pop(
        "registration_fingerprint",
        None,
    )
    payload.pop(
        "handler",
        None,
    )

    return payload


def calculate_runtime_registration_fingerprint(
    package: RuntimeRegistrationPackage,
) -> str:
    """
    Calculate the deterministic SHA-256 package fingerprint.
    """

    payload = runtime_registration_fingerprint_payload(
        package
    )

    canonical_json = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )

    return hashlib.sha256(
        canonical_json.encode("utf-8")
    ).hexdigest()


def create_runtime_registration_package(
    *,
    job_type: str,
    handler_ref: str,
    handler: Callable[..., Any],
    pipeline: str = "",
    stage: str = "",
    description: str = "",
    required_payload_fields: Iterable[Any] | None = None,
    required_worker_capabilities: Iterable[Any] | None = None,
    predecessor_stages: Iterable[Any] | None = None,
    successor_stages: Iterable[Any] | None = None,
    idempotency_fields: Iterable[Any] | None = None,
    retry_policy: Mapping[str, Any] | None = None,
    concurrency_policy: Mapping[str, Any] | None = None,
    lifecycle_policy: Mapping[str, Any] | None = None,
    configuration_requirements: Mapping[str, Any] | None = None,
    feature_flag_key: str | None = None,
    runtime_version_requirements: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
    persistent: bool = False,
    registered_at: str = "",
    registration_fingerprint: str | None = None,
) -> RuntimeRegistrationPackage:
    """
    Build the canonical package without registry side effects.
    """

    return RuntimeRegistrationPackage(
        job_type=job_type,
        pipeline=pipeline,
        stage=stage,
        handler_ref=handler_ref,
        handler=handler,
        required_payload_fields=_string_tuple(
            required_payload_fields,
            "required_payload_fields",
        ),
        required_worker_capabilities=_string_tuple(
            required_worker_capabilities,
            "required_worker_capabilities",
        ),
        predecessor_stages=_string_tuple(
            predecessor_stages,
            "predecessor_stages",
        ),
        successor_stages=_string_tuple(
            successor_stages,
            "successor_stages",
        ),
        idempotency_fields=_string_tuple(
            idempotency_fields,
            "idempotency_fields",
        ),
        retry_policy=_mapping(
            retry_policy,
            "retry_policy",
        ),
        concurrency_policy=_mapping(
            concurrency_policy,
            "concurrency_policy",
        ),
        lifecycle_policy=_mapping(
            lifecycle_policy,
            "lifecycle_policy",
        ),
        configuration_requirements=(
            _configuration_requirements(
                configuration_requirements
            )
        ),
        feature_flag_key=feature_flag_key,
        runtime_version_requirements=(
            _version_requirements(
                runtime_version_requirements
            )
        ),
        description=description,
        metadata=_mapping(
            metadata,
            "metadata",
        ),
        persistent=persistent,
        registered_at=registered_at,
        registration_fingerprint=(
            registration_fingerprint
            or ""
        ),
    )


__all__ = [
    "CANONICAL_RUNTIME_VERSION_CONTRACTS",
    "RUNTIME_REGISTRATION_PACKAGE_SCHEMA_VERSION",
    "RuntimeRegistrationPackage",
    "RuntimeRegistrationPackageError",
    "RuntimeRegistrationPackageValidationError",
    "calculate_runtime_registration_fingerprint",
    "create_runtime_registration_package",
    "runtime_registration_fingerprint_payload",
]