from __future__ import annotations

"""
Universal Runtime Infrastructure
Phase 1.1.11 — Runtime Capability Negotiation

This module provides business-logic-agnostic capability registration,
discovery, comparison, and negotiation for runtime components.

It supports safe mixed-version operation during rolling deployments,
worker upgrades, service upgrades, schema migrations, protocol migrations,
blue-green deployments, and multi-region operation.
"""

import hashlib
import json
import re
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping


_VERSION_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z.-]+))?$"
)


class RuntimeCapabilityError(RuntimeError):
    """Base exception for capability-negotiation failures."""


class RuntimeCapabilityValidationError(RuntimeCapabilityError):
    """Raised when capability contracts are invalid."""


class RuntimeCapabilityConflictError(RuntimeCapabilityError):
    """Raised when a component manifest conflicts with existing state."""


class RuntimeCapabilityNotFoundError(RuntimeCapabilityError):
    """Raised when a component capability manifest is unavailable."""


class RuntimeCapabilityNegotiationError(RuntimeCapabilityError):
    """Raised when required capabilities cannot be satisfied."""


class RuntimeCapabilityRequirementLevel(str, Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"


class RuntimeCapabilityStatus(str, Enum):
    SATISFIED = "satisfied"
    MISSING = "missing"
    VERSION_MISMATCH = "version_mismatch"
    PROTOCOL_MISMATCH = "protocol_mismatch"
    SERIALIZATION_MISMATCH = "serialization_mismatch"
    SCHEMA_MISMATCH = "schema_mismatch"
    DEPRECATED = "deprecated"


class RuntimeCapabilityAuditAction(str, Enum):
    REGISTERED = "registered"
    REPLACED = "replaced"
    REMOVED = "removed"
    NEGOTIATED = "negotiated"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _normalise_text(
    value: str,
    *,
    field_name: str,
) -> str:
    if not isinstance(value, str):
        raise RuntimeCapabilityValidationError(
            f"{field_name} must be a string."
        )

    normalised = value.strip()

    if not normalised:
        raise RuntimeCapabilityValidationError(
            f"{field_name} must not be empty."
        )

    return normalised


def _normalise_optional_text(
    value: str | None,
    *,
    field_name: str,
) -> str | None:
    if value is None:
        return None

    return _normalise_text(
        value,
        field_name=field_name,
    )


def _normalise_string_set(
    values: Iterable[str] | None,
    *,
    field_name: str,
) -> frozenset[str]:
    if values is None:
        return frozenset()

    return frozenset(
        _normalise_text(
            value,
            field_name=field_name,
        )
        for value in values
    )


def _normalise_datetime(
    value: datetime,
    *,
    field_name: str,
) -> datetime:
    if not isinstance(value, datetime):
        raise RuntimeCapabilityValidationError(
            f"{field_name} must be a datetime."
        )

    if value.tzinfo is None:
        raise RuntimeCapabilityValidationError(
            f"{field_name} must be timezone-aware."
        )

    return value.astimezone(timezone.utc)


def _freeze_mapping(
    values: Mapping[str, Any] | None,
) -> Mapping[str, Any]:
    return MappingProxyType(
        dict(values or {})
    )


def _canonical_json(
    value: Mapping[str, Any],
) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def _fingerprint(
    value: Mapping[str, Any],
) -> str:
    return hashlib.sha256(
        _canonical_json(value).encode("utf-8")
    ).hexdigest()


@dataclass(
    frozen=True,
    order=True,
    slots=True,
)
class RuntimeCapabilityVersion:
    major: int
    minor: int
    patch: int
    prerelease: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "major",
            "minor",
            "patch",
        ):
            value = getattr(
                self,
                field_name,
            )

            if not isinstance(value, int):
                raise RuntimeCapabilityValidationError(
                    f"{field_name} must be an integer."
                )

            if value < 0:
                raise RuntimeCapabilityValidationError(
                    f"{field_name} must not be negative."
                )

        object.__setattr__(
            self,
            "prerelease",
            _normalise_optional_text(
                self.prerelease,
                field_name="prerelease",
            ),
        )

    @classmethod
    def parse(
        cls,
        value: str,
    ) -> RuntimeCapabilityVersion:
        normalised = _normalise_text(
            value,
            field_name="version",
        )

        match = _VERSION_PATTERN.fullmatch(
            normalised
        )

        if match is None:
            raise RuntimeCapabilityValidationError(
                f"Invalid semantic version: {normalised}"
            )

        return cls(
            major=int(match.group(1)),
            minor=int(match.group(2)),
            patch=int(match.group(3)),
            prerelease=match.group(4),
        )

    def __str__(self) -> str:
        value = (
            f"{self.major}."
            f"{self.minor}."
            f"{self.patch}"
        )

        if self.prerelease:
            value += f"-{self.prerelease}"

        return value


@dataclass(frozen=True, slots=True)
class RuntimeCapabilityVersionRange:
    minimum: RuntimeCapabilityVersion | None = None
    maximum: RuntimeCapabilityVersion | None = None
    include_minimum: bool = True
    include_maximum: bool = True
    allow_prerelease: bool = False

    def __post_init__(self) -> None:
        if (
            self.minimum is not None
            and not isinstance(
                self.minimum,
                RuntimeCapabilityVersion,
            )
        ):
            raise RuntimeCapabilityValidationError(
                "minimum must be a RuntimeCapabilityVersion."
            )

        if (
            self.maximum is not None
            and not isinstance(
                self.maximum,
                RuntimeCapabilityVersion,
            )
        ):
            raise RuntimeCapabilityValidationError(
                "maximum must be a RuntimeCapabilityVersion."
            )

        if (
            self.minimum is not None
            and self.maximum is not None
            and self.minimum > self.maximum
        ):
            raise RuntimeCapabilityValidationError(
                "minimum must not exceed maximum."
            )

    def contains(
        self,
        version: RuntimeCapabilityVersion,
    ) -> bool:
        if version.prerelease and not self.allow_prerelease:
            return False

        if self.minimum is not None:
            if self.include_minimum:
                if version < self.minimum:
                    return False
            elif version <= self.minimum:
                return False

        if self.maximum is not None:
            if self.include_maximum:
                if version > self.maximum:
                    return False
            elif version >= self.maximum:
                return False

        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "minimum": (
                str(self.minimum)
                if self.minimum is not None
                else None
            ),
            "maximum": (
                str(self.maximum)
                if self.maximum is not None
                else None
            ),
            "include_minimum": self.include_minimum,
            "include_maximum": self.include_maximum,
            "allow_prerelease": self.allow_prerelease,
        }


@dataclass(frozen=True, slots=True)
class RuntimeCapability:
    name: str
    version: RuntimeCapabilityVersion
    protocols: frozenset[str] = field(
        default_factory=frozenset
    )
    serialization_formats: frozenset[str] = field(
        default_factory=frozenset
    )
    schema_versions: frozenset[str] = field(
        default_factory=frozenset
    )
    deprecated: bool = False
    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "name",
            _normalise_text(
                self.name,
                field_name="name",
            ),
        )

        if not isinstance(
            self.version,
            RuntimeCapabilityVersion,
        ):
            raise RuntimeCapabilityValidationError(
                "version must be a RuntimeCapabilityVersion."
            )

        object.__setattr__(
            self,
            "protocols",
            _normalise_string_set(
                self.protocols,
                field_name="protocol",
            ),
        )

        object.__setattr__(
            self,
            "serialization_formats",
            _normalise_string_set(
                self.serialization_formats,
                field_name="serialization_format",
            ),
        )

        object.__setattr__(
            self,
            "schema_versions",
            _normalise_string_set(
                self.schema_versions,
                field_name="schema_version",
            ),
        )

        object.__setattr__(
            self,
            "metadata",
            _freeze_mapping(
                self.metadata
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": str(self.version),
            "protocols": sorted(self.protocols),
            "serialization_formats": sorted(
                self.serialization_formats
            ),
            "schema_versions": sorted(
                self.schema_versions
            ),
            "deprecated": self.deprecated,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class RuntimeCapabilityRequirement:
    name: str
    level: RuntimeCapabilityRequirementLevel
    version_range: RuntimeCapabilityVersionRange = field(
        default_factory=RuntimeCapabilityVersionRange
    )
    accepted_protocols: frozenset[str] = field(
        default_factory=frozenset
    )
    accepted_serialization_formats: frozenset[str] = field(
        default_factory=frozenset
    )
    accepted_schema_versions: frozenset[str] = field(
        default_factory=frozenset
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "name",
            _normalise_text(
                self.name,
                field_name="name",
            ),
        )

        if not isinstance(
            self.level,
            RuntimeCapabilityRequirementLevel,
        ):
            try:
                object.__setattr__(
                    self,
                    "level",
                    RuntimeCapabilityRequirementLevel(
                        self.level
                    ),
                )
            except Exception as exc:
                raise RuntimeCapabilityValidationError(
                    "level is invalid."
                ) from exc

        if not isinstance(
            self.version_range,
            RuntimeCapabilityVersionRange,
        ):
            raise RuntimeCapabilityValidationError(
                "version_range must be a "
                "RuntimeCapabilityVersionRange."
            )

        object.__setattr__(
            self,
            "accepted_protocols",
            _normalise_string_set(
                self.accepted_protocols,
                field_name="accepted_protocol",
            ),
        )

        object.__setattr__(
            self,
            "accepted_serialization_formats",
            _normalise_string_set(
                self.accepted_serialization_formats,
                field_name="accepted_serialization_format",
            ),
        )

        object.__setattr__(
            self,
            "accepted_schema_versions",
            _normalise_string_set(
                self.accepted_schema_versions,
                field_name="accepted_schema_version",
            ),
        )


@dataclass(frozen=True, slots=True)
class RuntimeCapabilityManifest:
    component_id: str
    component_type: str
    component_version: RuntimeCapabilityVersion
    runtime_version: RuntimeCapabilityVersion
    capabilities: tuple[RuntimeCapability, ...]
    generated_at: datetime = field(
        default_factory=_utc_now
    )
    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "component_id",
            _normalise_text(
                self.component_id,
                field_name="component_id",
            ),
        )

        object.__setattr__(
            self,
            "component_type",
            _normalise_text(
                self.component_type,
                field_name="component_type",
            ),
        )

        if not isinstance(
            self.component_version,
            RuntimeCapabilityVersion,
        ):
            raise RuntimeCapabilityValidationError(
                "component_version must be a "
                "RuntimeCapabilityVersion."
            )

        if not isinstance(
            self.runtime_version,
            RuntimeCapabilityVersion,
        ):
            raise RuntimeCapabilityValidationError(
                "runtime_version must be a "
                "RuntimeCapabilityVersion."
            )

        capabilities = tuple(
            self.capabilities
        )

        names = [
            capability.name
            for capability in capabilities
        ]

        if len(names) != len(set(names)):
            raise RuntimeCapabilityValidationError(
                "Capability names must be unique within a manifest."
            )

        object.__setattr__(
            self,
            "capabilities",
            tuple(
                sorted(
                    capabilities,
                    key=lambda item: item.name,
                )
            ),
        )

        object.__setattr__(
            self,
            "generated_at",
            _normalise_datetime(
                self.generated_at,
                field_name="generated_at",
            ),
        )

        object.__setattr__(
            self,
            "metadata",
            _freeze_mapping(
                self.metadata
            ),
        )

    @property
    def capability_map(
        self,
    ) -> Mapping[str, RuntimeCapability]:
        return MappingProxyType(
            {
                capability.name: capability
                for capability in self.capabilities
            }
        )

    @property
    def fingerprint(self) -> str:
        return _fingerprint(
            self.to_dict()
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "component_id": self.component_id,
            "component_type": self.component_type,
            "component_version": str(
                self.component_version
            ),
            "runtime_version": str(
                self.runtime_version
            ),
            "capabilities": [
                capability.to_dict()
                for capability in self.capabilities
            ],
            "generated_at": (
                self.generated_at.isoformat()
            ),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class RuntimeCapabilityMatch:
    requirement_name: str
    level: RuntimeCapabilityRequirementLevel
    status: RuntimeCapabilityStatus
    provider_component_id: str
    provider_version: str | None
    message: str

    @property
    def satisfied(self) -> bool:
        return self.status in {
            RuntimeCapabilityStatus.SATISFIED,
            RuntimeCapabilityStatus.DEPRECATED,
        }


@dataclass(frozen=True, slots=True)
class RuntimeCapabilityNegotiationReport:
    consumer_component_id: str
    provider_component_id: str
    compatible: bool
    matches: tuple[RuntimeCapabilityMatch, ...]
    warnings: tuple[str, ...]
    evaluated_at: datetime
    fingerprint: str

    def require_compatible(self) -> None:
        if not self.compatible:
            failures = [
                match.message
                for match in self.matches
                if (
                    match.level
                    is RuntimeCapabilityRequirementLevel.REQUIRED
                    and not match.satisfied
                )
            ]

            raise RuntimeCapabilityNegotiationError(
                "Capability negotiation failed: "
                + "; ".join(failures)
            )


@dataclass(frozen=True, slots=True)
class RuntimeCapabilityRegistrySnapshot:
    generation: int
    manifests: tuple[RuntimeCapabilityManifest, ...]
    captured_at: datetime
    fingerprint: str


@dataclass(frozen=True, slots=True)
class RuntimeCapabilityAuditEvent:
    sequence: int
    action: RuntimeCapabilityAuditAction
    component_id: str
    actor: str
    occurred_at: datetime
    details: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if self.sequence < 1:
            raise RuntimeCapabilityValidationError(
                "sequence must be at least 1."
            )

        object.__setattr__(
            self,
            "component_id",
            _normalise_text(
                self.component_id,
                field_name="component_id",
            ),
        )

        object.__setattr__(
            self,
            "actor",
            _normalise_text(
                self.actor,
                field_name="actor",
            ),
        )

        object.__setattr__(
            self,
            "occurred_at",
            _normalise_datetime(
                self.occurred_at,
                field_name="occurred_at",
            ),
        )

        object.__setattr__(
            self,
            "details",
            _freeze_mapping(
                self.details
            ),
        )


class RuntimeCapabilityRegistry:
    """Thread-safe capability-manifest registry."""

    def __init__(self) -> None:
        self._manifests: dict[
            str,
            RuntimeCapabilityManifest,
        ] = {}
        self._audit_events: list[
            RuntimeCapabilityAuditEvent
        ] = []
        self._generation = 0
        self._sequence = 0
        self._lock = threading.RLock()

    @property
    def generation(self) -> int:
        with self._lock:
            return self._generation

    def register(
        self,
        manifest: RuntimeCapabilityManifest,
        *,
        actor: str,
        replace: bool = False,
    ) -> RuntimeCapabilityManifest:
        if not isinstance(
            manifest,
            RuntimeCapabilityManifest,
        ):
            raise RuntimeCapabilityValidationError(
                "manifest must be a RuntimeCapabilityManifest."
            )

        normalised_actor = _normalise_text(
            actor,
            field_name="actor",
        )

        with self._lock:
            existing = self._manifests.get(
                manifest.component_id
            )

            if existing is not None and not replace:
                raise RuntimeCapabilityConflictError(
                    "Capability manifest already exists for "
                    f"{manifest.component_id}."
                )

            self._manifests[
                manifest.component_id
            ] = manifest

            self._generation += 1

            self._append_audit(
                action=(
                    RuntimeCapabilityAuditAction.REPLACED
                    if existing is not None
                    else RuntimeCapabilityAuditAction.REGISTERED
                ),
                component_id=manifest.component_id,
                actor=normalised_actor,
                details={
                    "generation": self._generation,
                    "fingerprint": manifest.fingerprint,
                },
            )

            return manifest

    def get(
        self,
        component_id: str,
    ) -> RuntimeCapabilityManifest:
        normalised = _normalise_text(
            component_id,
            field_name="component_id",
        )

        with self._lock:
            manifest = self._manifests.get(
                normalised
            )

            if manifest is None:
                raise RuntimeCapabilityNotFoundError(
                    f"No manifest exists for {normalised}."
                )

            return manifest

    def remove(
        self,
        component_id: str,
        *,
        actor: str,
    ) -> RuntimeCapabilityManifest:
        normalised = _normalise_text(
            component_id,
            field_name="component_id",
        )

        normalised_actor = _normalise_text(
            actor,
            field_name="actor",
        )

        with self._lock:
            try:
                manifest = self._manifests.pop(
                    normalised
                )
            except KeyError as exc:
                raise RuntimeCapabilityNotFoundError(
                    f"No manifest exists for {normalised}."
                ) from exc

            self._generation += 1

            self._append_audit(
                action=RuntimeCapabilityAuditAction.REMOVED,
                component_id=normalised,
                actor=normalised_actor,
                details={
                    "generation": self._generation,
                    "fingerprint": manifest.fingerprint,
                },
            )

            return manifest

    def snapshot(
        self,
    ) -> RuntimeCapabilityRegistrySnapshot:
        with self._lock:
            manifests = tuple(
                sorted(
                    self._manifests.values(),
                    key=lambda item: item.component_id,
                )
            )

            payload = {
                "generation": self._generation,
                "manifests": [
                    manifest.to_dict()
                    for manifest in manifests
                ],
            }

            return RuntimeCapabilityRegistrySnapshot(
                generation=self._generation,
                manifests=manifests,
                captured_at=_utc_now(),
                fingerprint=_fingerprint(
                    payload
                ),
            )

    def audit_history(
        self,
    ) -> tuple[RuntimeCapabilityAuditEvent, ...]:
        with self._lock:
            return tuple(
                self._audit_events
            )

    def negotiate(
        self,
        *,
        consumer_component_id: str,
        provider_component_id: str,
        requirements: Iterable[
            RuntimeCapabilityRequirement
        ],
        actor: str = "runtime",
    ) -> RuntimeCapabilityNegotiationReport:
        consumer = self.get(
            consumer_component_id
        )

        provider = self.get(
            provider_component_id
        )

        report = negotiate_runtime_capabilities(
            consumer_manifest=consumer,
            provider_manifest=provider,
            requirements=requirements,
        )

        with self._lock:
            self._append_audit(
                action=RuntimeCapabilityAuditAction.NEGOTIATED,
                component_id=provider.component_id,
                actor=_normalise_text(
                    actor,
                    field_name="actor",
                ),
                details={
                    "consumer_component_id": (
                        consumer.component_id
                    ),
                    "compatible": report.compatible,
                    "fingerprint": report.fingerprint,
                },
            )

        return report

    def _append_audit(
        self,
        *,
        action: RuntimeCapabilityAuditAction,
        component_id: str,
        actor: str,
        details: Mapping[str, Any],
    ) -> None:
        self._sequence += 1

        self._audit_events.append(
            RuntimeCapabilityAuditEvent(
                sequence=self._sequence,
                action=action,
                component_id=component_id,
                actor=actor,
                occurred_at=_utc_now(),
                details=details,
            )
        )


def negotiate_runtime_capabilities(
    *,
    consumer_manifest: RuntimeCapabilityManifest,
    provider_manifest: RuntimeCapabilityManifest,
    requirements: Iterable[
        RuntimeCapabilityRequirement
    ],
) -> RuntimeCapabilityNegotiationReport:
    if not isinstance(
        consumer_manifest,
        RuntimeCapabilityManifest,
    ):
        raise RuntimeCapabilityValidationError(
            "consumer_manifest must be a RuntimeCapabilityManifest."
        )

    if not isinstance(
        provider_manifest,
        RuntimeCapabilityManifest,
    ):
        raise RuntimeCapabilityValidationError(
            "provider_manifest must be a RuntimeCapabilityManifest."
        )

    requirement_tuple = tuple(
        requirements
    )

    for requirement in requirement_tuple:
        if not isinstance(
            requirement,
            RuntimeCapabilityRequirement,
        ):
            raise RuntimeCapabilityValidationError(
                "requirements must contain "
                "RuntimeCapabilityRequirement values."
            )

    capability_map = provider_manifest.capability_map
    matches: list[RuntimeCapabilityMatch] = []
    warnings: list[str] = []

    for requirement in sorted(
        requirement_tuple,
        key=lambda item: item.name,
    ):
        capability = capability_map.get(
            requirement.name
        )

        if capability is None:
            match = RuntimeCapabilityMatch(
                requirement_name=requirement.name,
                level=requirement.level,
                status=RuntimeCapabilityStatus.MISSING,
                provider_component_id=(
                    provider_manifest.component_id
                ),
                provider_version=None,
                message=(
                    f"Capability {requirement.name} is missing "
                    f"from {provider_manifest.component_id}."
                ),
            )

            matches.append(match)

            if (
                requirement.level
                is RuntimeCapabilityRequirementLevel.OPTIONAL
            ):
                warnings.append(match.message)

            continue

        if not requirement.version_range.contains(
            capability.version
        ):
            match = RuntimeCapabilityMatch(
                requirement_name=requirement.name,
                level=requirement.level,
                status=(
                    RuntimeCapabilityStatus.VERSION_MISMATCH
                ),
                provider_component_id=(
                    provider_manifest.component_id
                ),
                provider_version=str(
                    capability.version
                ),
                message=(
                    f"Capability {requirement.name} version "
                    f"{capability.version} is outside the "
                    "accepted range."
                ),
            )

            matches.append(match)

            if (
                requirement.level
                is RuntimeCapabilityRequirementLevel.OPTIONAL
            ):
                warnings.append(match.message)

            continue

        if (
            requirement.accepted_protocols
            and not (
                requirement.accepted_protocols
                & capability.protocols
            )
        ):
            match = RuntimeCapabilityMatch(
                requirement_name=requirement.name,
                level=requirement.level,
                status=(
                    RuntimeCapabilityStatus.PROTOCOL_MISMATCH
                ),
                provider_component_id=(
                    provider_manifest.component_id
                ),
                provider_version=str(
                    capability.version
                ),
                message=(
                    f"Capability {requirement.name} has no "
                    "accepted protocol."
                ),
            )

            matches.append(match)

            if (
                requirement.level
                is RuntimeCapabilityRequirementLevel.OPTIONAL
            ):
                warnings.append(match.message)

            continue

        if (
            requirement.accepted_serialization_formats
            and not (
                requirement.accepted_serialization_formats
                & capability.serialization_formats
            )
        ):
            match = RuntimeCapabilityMatch(
                requirement_name=requirement.name,
                level=requirement.level,
                status=(
                    RuntimeCapabilityStatus.SERIALIZATION_MISMATCH
                ),
                provider_component_id=(
                    provider_manifest.component_id
                ),
                provider_version=str(
                    capability.version
                ),
                message=(
                    f"Capability {requirement.name} has no "
                    "accepted serialization format."
                ),
            )

            matches.append(match)

            if (
                requirement.level
                is RuntimeCapabilityRequirementLevel.OPTIONAL
            ):
                warnings.append(match.message)

            continue

        if (
            requirement.accepted_schema_versions
            and not (
                requirement.accepted_schema_versions
                & capability.schema_versions
            )
        ):
            match = RuntimeCapabilityMatch(
                requirement_name=requirement.name,
                level=requirement.level,
                status=(
                    RuntimeCapabilityStatus.SCHEMA_MISMATCH
                ),
                provider_component_id=(
                    provider_manifest.component_id
                ),
                provider_version=str(
                    capability.version
                ),
                message=(
                    f"Capability {requirement.name} has no "
                    "accepted schema version."
                ),
            )

            matches.append(match)

            if (
                requirement.level
                is RuntimeCapabilityRequirementLevel.OPTIONAL
            ):
                warnings.append(match.message)

            continue

        if capability.deprecated:
            match = RuntimeCapabilityMatch(
                requirement_name=requirement.name,
                level=requirement.level,
                status=RuntimeCapabilityStatus.DEPRECATED,
                provider_component_id=(
                    provider_manifest.component_id
                ),
                provider_version=str(
                    capability.version
                ),
                message=(
                    f"Capability {requirement.name} is available "
                    "but deprecated."
                ),
            )

            warnings.append(match.message)
            matches.append(match)
            continue

        matches.append(
            RuntimeCapabilityMatch(
                requirement_name=requirement.name,
                level=requirement.level,
                status=RuntimeCapabilityStatus.SATISFIED,
                provider_component_id=(
                    provider_manifest.component_id
                ),
                provider_version=str(
                    capability.version
                ),
                message=(
                    f"Capability {requirement.name} is satisfied."
                ),
            )
        )

    compatible = all(
        match.satisfied
        for match in matches
        if (
            match.level
            is RuntimeCapabilityRequirementLevel.REQUIRED
        )
    )

    evaluated_at = _utc_now()

    payload = {
        "consumer_component_id": (
            consumer_manifest.component_id
        ),
        "provider_component_id": (
            provider_manifest.component_id
        ),
        "compatible": compatible,
        "matches": [
            {
                "requirement_name": match.requirement_name,
                "level": match.level.value,
                "status": match.status.value,
                "provider_component_id": (
                    match.provider_component_id
                ),
                "provider_version": (
                    match.provider_version
                ),
                "message": match.message,
            }
            for match in matches
        ],
        "warnings": warnings,
    }

    return RuntimeCapabilityNegotiationReport(
        consumer_component_id=(
            consumer_manifest.component_id
        ),
        provider_component_id=(
            provider_manifest.component_id
        ),
        compatible=compatible,
        matches=tuple(matches),
        warnings=tuple(warnings),
        evaluated_at=evaluated_at,
        fingerprint=_fingerprint(payload),
    )


_default_registry = RuntimeCapabilityRegistry()


def get_runtime_capability_registry(
) -> RuntimeCapabilityRegistry:
    return _default_registry


def register_runtime_capability_manifest(
    manifest: RuntimeCapabilityManifest,
    *,
    actor: str,
    replace: bool = False,
) -> RuntimeCapabilityManifest:
    return _default_registry.register(
        manifest,
        actor=actor,
        replace=replace,
    )


__all__ = [
    "RuntimeCapability",
    "RuntimeCapabilityAuditAction",
    "RuntimeCapabilityAuditEvent",
    "RuntimeCapabilityConflictError",
    "RuntimeCapabilityError",
    "RuntimeCapabilityManifest",
    "RuntimeCapabilityMatch",
    "RuntimeCapabilityNegotiationError",
    "RuntimeCapabilityNegotiationReport",
    "RuntimeCapabilityNotFoundError",
    "RuntimeCapabilityRegistry",
    "RuntimeCapabilityRegistrySnapshot",
    "RuntimeCapabilityRequirement",
    "RuntimeCapabilityRequirementLevel",
    "RuntimeCapabilityStatus",
    "RuntimeCapabilityValidationError",
    "RuntimeCapabilityVersion",
    "RuntimeCapabilityVersionRange",
    "get_runtime_capability_registry",
    "negotiate_runtime_capabilities",
    "register_runtime_capability_manifest",
]
