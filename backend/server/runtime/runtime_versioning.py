from __future__ import annotations

"""
Universal Runtime Versioning.

This module defines immutable version identifiers and manifests for the
Universal Runtime Infrastructure.

It records versions. It does not decide whether two versions are
compatible; compatibility policy belongs to the Runtime Compatibility
Layer.
"""

import hashlib
import json
import re
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


__all__ = [
    "DEFAULT_CONFIGURATION_SCHEMA_VERSION",
    "DEFAULT_JOB_CONTRACT_VERSION",
    "DEFAULT_KERNEL_API_VERSION",
    "DEFAULT_RUNTIME_VERSION",
    "DEFAULT_SERVICE_CONTRACT_VERSION",
    "DEFAULT_STATE_SCHEMA_VERSION",
    "RUNTIME_VERSION_MANIFEST_SCHEMA_VERSION",
    "RuntimeComponentVersion",
    "RuntimeReleaseChannel",
    "RuntimeSemanticVersion",
    "RuntimeVersionError",
    "RuntimeVersionManifest",
    "RuntimeVersionManager",
    "RuntimeVersionMissingError",
    "RuntimeVersionRegistrationError",
    "RuntimeVersionSnapshot",
    "RuntimeVersionStateError",
    "RuntimeVersionValidationError",
    "create_default_runtime_version_manager",
]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


RUNTIME_VERSION_MANIFEST_SCHEMA_VERSION = "1.0.0"

DEFAULT_RUNTIME_VERSION = "0.1.0"
DEFAULT_KERNEL_API_VERSION = "0.1.0"
DEFAULT_SERVICE_CONTRACT_VERSION = "0.1.0"
DEFAULT_JOB_CONTRACT_VERSION = "0.1.0"
DEFAULT_STATE_SCHEMA_VERSION = "0.1.0"
DEFAULT_CONFIGURATION_SCHEMA_VERSION = "1.0.0"


_SEMVER_PATTERN = re.compile(
    r"^(?P<major>0|[1-9][0-9]*)"
    r"\.(?P<minor>0|[1-9][0-9]*)"
    r"\.(?P<patch>0|[1-9][0-9]*)"
    r"(?:-(?P<prerelease>"
    r"(?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*))*"
    r"))?"
    r"(?:\+(?P<build>"
    r"[0-9A-Za-z-]+"
    r"(?:\.[0-9A-Za-z-]+)*"
    r"))?$"
)

_COMPONENT_KEY_PATTERN = re.compile(
    r"^[a-z][a-z0-9_.-]{1,127}$"
)

_CONTRACT_KEY_PATTERN = re.compile(
    r"^[a-z][a-z0-9_.:-]{1,127}$"
)

_BUILD_ID_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$"
)

_METADATA_KEY_PATTERN = re.compile(
    r"^[A-Za-z][A-Za-z0-9_.:-]{0,127}$"
)


class RuntimeVersionError(RuntimeError):
    """Base runtime-versioning failure."""


class RuntimeVersionValidationError(
    RuntimeVersionError
):
    """Raised when a version or manifest is invalid."""


class RuntimeVersionRegistrationError(
    RuntimeVersionError
):
    """Raised when component-version registration is invalid."""


class RuntimeVersionMissingError(
    RuntimeVersionError
):
    """Raised when a component version is unavailable."""


class RuntimeVersionStateError(
    RuntimeVersionError
):
    """Raised when a sealed version manager is mutated."""


class RuntimeReleaseChannel(str, Enum):
    DEVELOPMENT = "development"
    ALPHA = "alpha"
    BETA = "beta"
    RELEASE_CANDIDATE = "release_candidate"
    STABLE = "stable"


@dataclass(frozen=True, slots=True)
class RuntimeSemanticVersion:
    """
    Strict Semantic Versioning 2.0.0 identifier.

    Build metadata is retained as identity information but does not
    influence precedence comparison.
    """

    major: int
    minor: int
    patch: int
    prerelease: tuple[str, ...] = ()
    build: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field_name in (
            "major",
            "minor",
            "patch",
        ):
            value = getattr(self, field_name)

            if isinstance(value, bool) or value < 0:
                raise RuntimeVersionValidationError(
                    f"{field_name} must be a non-negative integer."
                )

        for identifier in self.prerelease:
            if not identifier:
                raise RuntimeVersionValidationError(
                    "Prerelease identifiers must not be empty."
                )

            if (
                identifier.isdigit()
                and len(identifier) > 1
                and identifier.startswith("0")
            ):
                raise RuntimeVersionValidationError(
                    "Numeric prerelease identifiers must not "
                    "contain leading zeroes."
                )

        for identifier in self.build:
            if not identifier:
                raise RuntimeVersionValidationError(
                    "Build identifiers must not be empty."
                )

    @classmethod
    def parse(
        cls,
        value: "RuntimeSemanticVersion | str",
    ) -> "RuntimeSemanticVersion":
        if isinstance(value, cls):
            return value

        normalized = str(value or "").strip()
        match = _SEMVER_PATTERN.fullmatch(normalized)

        if match is None:
            raise RuntimeVersionValidationError(
                f"Invalid Semantic Version: {value!r}"
            )

        prerelease_text = match.group("prerelease")
        build_text = match.group("build")

        return cls(
            major=int(match.group("major")),
            minor=int(match.group("minor")),
            patch=int(match.group("patch")),
            prerelease=(
                ()
                if prerelease_text is None
                else tuple(prerelease_text.split("."))
            ),
            build=(
                ()
                if build_text is None
                else tuple(build_text.split("."))
            ),
        )

    def __str__(self) -> str:
        value = (
            f"{self.major}."
            f"{self.minor}."
            f"{self.patch}"
        )

        if self.prerelease:
            value += "-" + ".".join(self.prerelease)

        if self.build:
            value += "+" + ".".join(self.build)

        return value

    def compare_precedence(
        self,
        other: "RuntimeSemanticVersion | str",
    ) -> int:
        """
        Compare Semantic Version precedence.

        Returns:
        -1 when self has lower precedence
         0 when precedence is equal
         1 when self has higher precedence
        """

        resolved = self.parse(other)

        self_core = (
            self.major,
            self.minor,
            self.patch,
        )

        other_core = (
            resolved.major,
            resolved.minor,
            resolved.patch,
        )

        if self_core < other_core:
            return -1

        if self_core > other_core:
            return 1

        if not self.prerelease and not resolved.prerelease:
            return 0

        if not self.prerelease:
            return 1

        if not resolved.prerelease:
            return -1

        for left, right in zip(
            self.prerelease,
            resolved.prerelease,
        ):
            if left == right:
                continue

            left_numeric = left.isdigit()
            right_numeric = right.isdigit()

            if left_numeric and right_numeric:
                left_number = int(left)
                right_number = int(right)

                return (
                    -1
                    if left_number < right_number
                    else 1
                )

            if left_numeric and not right_numeric:
                return -1

            if not left_numeric and right_numeric:
                return 1

            return -1 if left < right else 1

        if len(self.prerelease) < len(
            resolved.prerelease
        ):
            return -1

        if len(self.prerelease) > len(
            resolved.prerelease
        ):
            return 1

        return 0

    def same_precedence(
        self,
        other: "RuntimeSemanticVersion | str",
    ) -> bool:
        return self.compare_precedence(other) == 0


@dataclass(frozen=True, slots=True)
class RuntimeVersionManifest:
    """Immutable runtime foundation version manifest."""

    manifest_schema_version: RuntimeSemanticVersion
    runtime_name: str
    runtime_version: RuntimeSemanticVersion
    kernel_api_version: RuntimeSemanticVersion
    service_contract_version: RuntimeSemanticVersion
    job_contract_version: RuntimeSemanticVersion
    state_schema_version: RuntimeSemanticVersion
    configuration_schema_version: RuntimeSemanticVersion
    release_channel: RuntimeReleaseChannel
    created_at: datetime
    build_id: str | None
    metadata: Mapping[str, str]

    def __post_init__(self) -> None:
        runtime_name = str(
            self.runtime_name or ""
        ).strip()

        if not runtime_name:
            raise RuntimeVersionValidationError(
                "runtime_name must not be empty."
            )

        if len(runtime_name) > 128:
            raise RuntimeVersionValidationError(
                "runtime_name must not exceed 128 characters."
            )

        if (
            self.build_id is not None
            and not _BUILD_ID_PATTERN.fullmatch(
                self.build_id
            )
        ):
            raise RuntimeVersionValidationError(
                "build_id contains invalid characters."
            )

        if self.created_at.tzinfo is None:
            raise RuntimeVersionValidationError(
                "created_at must be timezone-aware."
            )

        normalized_metadata: dict[str, str] = {}

        for raw_key, raw_value in self.metadata.items():
            key = str(raw_key or "").strip()
            value = str(raw_value or "").strip()

            if not _METADATA_KEY_PATTERN.fullmatch(key):
                raise RuntimeVersionValidationError(
                    f"Invalid metadata key: {raw_key!r}"
                )

            if len(value) > 1024:
                raise RuntimeVersionValidationError(
                    f"Metadata value for {key!r} exceeds "
                    "1024 characters."
                )

            normalized_metadata[key] = value

        object.__setattr__(
            self,
            "runtime_name",
            runtime_name,
        )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(normalized_metadata),
        )

    def to_dict(
        self,
        *,
        include_created_at: bool = True,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {
            "manifest_schema_version": str(
                self.manifest_schema_version
            ),
            "runtime_name": self.runtime_name,
            "runtime_version": str(
                self.runtime_version
            ),
            "kernel_api_version": str(
                self.kernel_api_version
            ),
            "service_contract_version": str(
                self.service_contract_version
            ),
            "job_contract_version": str(
                self.job_contract_version
            ),
            "state_schema_version": str(
                self.state_schema_version
            ),
            "configuration_schema_version": str(
                self.configuration_schema_version
            ),
            "release_channel": (
                self.release_channel.value
            ),
            "build_id": self.build_id,
            "metadata": dict(self.metadata),
        }

        if include_created_at:
            result["created_at"] = (
                self.created_at.isoformat()
            )

        return result

    def fingerprint(self) -> str:
        """
        Return a deterministic effective-version fingerprint.

        created_at is excluded because it does not change the effective
        version contract.
        """

        payload = json.dumps(
            self.to_dict(
                include_created_at=False
            ),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

        return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True, slots=True)
class RuntimeComponentVersion:
    """Immutable version registration for one runtime component."""

    component_key: str
    version: RuntimeSemanticVersion
    contract: str
    registered_at: datetime
    generation: int


@dataclass(frozen=True, slots=True)
class RuntimeVersionSnapshot:
    """Immutable point-in-time version-manager snapshot."""

    sealed: bool
    generation: int
    component_count: int
    manifest_fingerprint: str
    version_graph_fingerprint: str
    manifest: RuntimeVersionManifest
    components: tuple[RuntimeComponentVersion, ...]


class RuntimeVersionManager:
    """
    Thread-safe version manifest and component-version registry.

    This class records exact versions. It deliberately does not make
    compatibility decisions.
    """

    __slots__ = (
        "_manifest",
        "_components",
        "_generation",
        "_sealed",
        "_lock",
    )

    def __init__(
        self,
        manifest: RuntimeVersionManifest,
    ) -> None:
        if not isinstance(
            manifest,
            RuntimeVersionManifest,
        ):
            raise RuntimeVersionValidationError(
                "A RuntimeVersionManifest is required."
            )

        self._manifest = manifest
        self._components: dict[
            str,
            RuntimeComponentVersion,
        ] = {}
        self._generation = 0
        self._sealed = False
        self._lock = threading.RLock()

    @staticmethod
    def normalize_component_key(
        component_key: str,
    ) -> str:
        key = str(component_key or "").strip().lower()

        if not _COMPONENT_KEY_PATTERN.fullmatch(key):
            raise RuntimeVersionRegistrationError(
                "component_key must be 2-128 characters, "
                "begin with a lowercase letter, and contain "
                "only lowercase letters, numbers, dots, "
                "underscores, or hyphens."
            )

        return key

    @staticmethod
    def normalize_contract(
        contract: str,
    ) -> str:
        normalized = str(contract or "").strip().lower()

        if not _CONTRACT_KEY_PATTERN.fullmatch(
            normalized
        ):
            raise RuntimeVersionRegistrationError(
                "contract must be 2-128 characters, begin "
                "with a lowercase letter, and contain only "
                "lowercase letters, numbers, dots, "
                "underscores, colons, or hyphens."
            )

        return normalized

    @property
    def manifest(
        self,
    ) -> RuntimeVersionManifest:
        return self._manifest

    @property
    def sealed(self) -> bool:
        with self._lock:
            return self._sealed

    @property
    def generation(self) -> int:
        with self._lock:
            return self._generation

    @property
    def component_count(self) -> int:
        with self._lock:
            return len(self._components)

    def _assert_mutable(self) -> None:
        if self._sealed:
            raise RuntimeVersionStateError(
                "The runtime version manager is sealed."
            )

    def _record_mutation(self) -> int:
        self._generation += 1
        return self._generation

    def register_component(
        self,
        component_key: str,
        version: RuntimeSemanticVersion | str,
        *,
        contract: str = "implementation",
        replace: bool = False,
    ) -> RuntimeComponentVersion:
        key = self.normalize_component_key(
            component_key
        )

        resolved_version = (
            RuntimeSemanticVersion.parse(version)
        )

        resolved_contract = self.normalize_contract(
            contract
        )

        with self._lock:
            self._assert_mutable()

            if key in self._components and not replace:
                raise RuntimeVersionRegistrationError(
                    f"Runtime component {key!r} already "
                    "has a registered version."
                )

            generation = self._record_mutation()

            registration = RuntimeComponentVersion(
                component_key=key,
                version=resolved_version,
                contract=resolved_contract,
                registered_at=_utc_now(),
                generation=generation,
            )

            self._components[key] = registration

            return registration

    def has_component(
        self,
        component_key: str,
    ) -> bool:
        key = self.normalize_component_key(
            component_key
        )

        with self._lock:
            return key in self._components

    def get_component_version(
        self,
        component_key: str,
    ) -> RuntimeComponentVersion:
        key = self.normalize_component_key(
            component_key
        )

        with self._lock:
            try:
                return self._components[key]
            except KeyError as exc:
                raise RuntimeVersionMissingError(
                    f"No version is registered for "
                    f"runtime component {key!r}."
                ) from exc

    def components_for_contract(
        self,
        contract: str,
    ) -> tuple[RuntimeComponentVersion, ...]:
        resolved_contract = self.normalize_contract(
            contract
        )

        with self._lock:
            return tuple(
                self._components[key]
                for key in sorted(self._components)
                if (
                    self._components[key].contract
                    == resolved_contract
                )
            )

    def version_graph_fingerprint(
        self,
    ) -> str:
        with self._lock:
            components = [
                {
                    "component_key": registration.component_key,
                    "version": str(registration.version),
                    "contract": registration.contract,
                }
                for registration in (
                    self._components[key]
                    for key in sorted(self._components)
                )
            ]

        payload = json.dumps(
            {
                "manifest_fingerprint": (
                    self._manifest.fingerprint()
                ),
                "components": components,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

        return hashlib.sha256(payload).hexdigest()

    def seal(
        self,
    ) -> RuntimeVersionSnapshot:
        with self._lock:
            self._sealed = True
            self._record_mutation()

        return self.snapshot()

    def snapshot(
        self,
    ) -> RuntimeVersionSnapshot:
        with self._lock:
            components = tuple(
                self._components[key]
                for key in sorted(self._components)
            )

            return RuntimeVersionSnapshot(
                sealed=self._sealed,
                generation=self._generation,
                component_count=len(self._components),
                manifest_fingerprint=(
                    self._manifest.fingerprint()
                ),
                version_graph_fingerprint=(
                    self.version_graph_fingerprint()
                ),
                manifest=self._manifest,
                components=components,
            )


def create_default_runtime_version_manager(
    *,
    runtime_name: str = "Universal Runtime",
    runtime_version: RuntimeSemanticVersion | str = (
        DEFAULT_RUNTIME_VERSION
    ),
    kernel_api_version: RuntimeSemanticVersion | str = (
        DEFAULT_KERNEL_API_VERSION
    ),
    service_contract_version: (
        RuntimeSemanticVersion | str
    ) = DEFAULT_SERVICE_CONTRACT_VERSION,
    job_contract_version: (
        RuntimeSemanticVersion | str
    ) = DEFAULT_JOB_CONTRACT_VERSION,
    state_schema_version: (
        RuntimeSemanticVersion | str
    ) = DEFAULT_STATE_SCHEMA_VERSION,
    configuration_schema_version: (
        RuntimeSemanticVersion | str
    ) = DEFAULT_CONFIGURATION_SCHEMA_VERSION,
    release_channel: RuntimeReleaseChannel | str = (
        RuntimeReleaseChannel.DEVELOPMENT
    ),
    build_id: str | None = None,
    metadata: Mapping[str, str] | None = None,
) -> RuntimeVersionManager:
    """Create the initial Universal Runtime version manager."""

    if isinstance(
        release_channel,
        RuntimeReleaseChannel,
    ):
        resolved_channel = release_channel
    else:
        try:
            resolved_channel = RuntimeReleaseChannel(
                str(release_channel or "").strip().lower()
            )
        except ValueError as exc:
            raise RuntimeVersionValidationError(
                f"Unknown release channel: "
                f"{release_channel!r}"
            ) from exc

    manifest = RuntimeVersionManifest(
        manifest_schema_version=(
            RuntimeSemanticVersion.parse(
                RUNTIME_VERSION_MANIFEST_SCHEMA_VERSION
            )
        ),
        runtime_name=runtime_name,
        runtime_version=(
            RuntimeSemanticVersion.parse(
                runtime_version
            )
        ),
        kernel_api_version=(
            RuntimeSemanticVersion.parse(
                kernel_api_version
            )
        ),
        service_contract_version=(
            RuntimeSemanticVersion.parse(
                service_contract_version
            )
        ),
        job_contract_version=(
            RuntimeSemanticVersion.parse(
                job_contract_version
            )
        ),
        state_schema_version=(
            RuntimeSemanticVersion.parse(
                state_schema_version
            )
        ),
        configuration_schema_version=(
            RuntimeSemanticVersion.parse(
                configuration_schema_version
            )
        ),
        release_channel=resolved_channel,
        created_at=_utc_now(),
        build_id=build_id,
        metadata=MappingProxyType(
            dict(metadata or {})
        ),
    )

    return RuntimeVersionManager(manifest)
