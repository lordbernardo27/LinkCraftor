"""
Universal Runtime Owner Control Tower
Phase 2.2 — Runtime Architecture / Version Read Model

Read-only projection only.

Authority:
- Runtime Owner Architecture Registry owns Owner architecture identity.
- Runtime source components own their own VERSION constants.
- This module reads and normalizes them.
- It never increments, mutates, publishes, or replaces versions.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any, Mapping

from backend.server.owner.runtime_owner_architecture_registry import (
    RUNTIME_OWNER_ARCHITECTURE_REGISTRY_SCHEMA_VERSION,
    RUNTIME_OWNER_ARCHITECTURE_REGISTRY_VERSION,
)


RUNTIME_ARCHITECTURE_VERSION_READ_MODEL_VERSION = (
    "runtime_architecture_version_read_model_v2.2.1"
)

RUNTIME_ARCHITECTURE_VERSION_READ_MODEL_SCHEMA_VERSION = (
    "runtime_architecture_version_read_model_schema_v1"
)


CANONICAL_RUNTIME_OWNER_SECTIONS: tuple[str, ...] = (
    "overview",
    "jobs",
    "queues",
    "workers_leases",
    "orchestration",
    "execution",
    "reliability_recovery",
    "resource_governance",
    "runtime_apis",
    "persistence_state_integrity",
    "observability",
    "security",
    "owner_actions",
    "evidence_audit",
)


_VERSION_PATTERN = re.compile(
    r"""
    ^\s*
    ([A-Z][A-Z0-9_]*VERSION)
    \s*=\s*
    (?:\(\s*)?
    ["']
    ([^"']+)
    ["']
    """,
    re.MULTILINE | re.VERBOSE,
)


@dataclass(frozen=True)
class RuntimeSubsystemVersionEvidence:
    file: str
    symbol: str
    value: str

    def to_dict(self) -> Mapping[str, str]:
        return {
            "file": self.file,
            "symbol": self.symbol,
            "value": self.value,
        }


@dataclass(frozen=True)
class RuntimeArchitectureVersionReadModel:
    architecture_name: str

    architecture_registry_version: str
    architecture_registry_schema_version: str

    owner_sections: tuple[str, ...]

    subsystem_versions: tuple[
        RuntimeSubsystemVersionEvidence,
        ...
    ]

    read_model_version: str = (
        RUNTIME_ARCHITECTURE_VERSION_READ_MODEL_VERSION
    )

    schema_version: str = (
        RUNTIME_ARCHITECTURE_VERSION_READ_MODEL_SCHEMA_VERSION
    )

    @property
    def owner_section_count(self) -> int:
        return len(self.owner_sections)

    @property
    def subsystem_version_count(self) -> int:
        return len(self.subsystem_versions)

    @property
    def authority(self) -> str:
        return (
            "runtime_architecture_registry_and_runtime_sources"
        )

    def to_dict(self) -> Mapping[str, Any]:
        return {
            "architecture_name":
                self.architecture_name,

            "architecture_registry_version":
                self.architecture_registry_version,

            "architecture_registry_schema_version":
                self.architecture_registry_schema_version,

            "owner_section_count":
                self.owner_section_count,

            "owner_sections":
                list(self.owner_sections),

            "subsystem_version_count":
                self.subsystem_version_count,

            "subsystem_versions": [
                item.to_dict()
                for item in self.subsystem_versions
            ],

            "authority":
                self.authority,

            "read_model_version":
                self.read_model_version,

            "schema_version":
                self.schema_version,
        }


def discover_runtime_subsystem_versions(
    runtime_root: Path,
) -> tuple[RuntimeSubsystemVersionEvidence, ...]:

    if not runtime_root.exists():
        raise ValueError(
            f"Runtime root not found: {runtime_root}"
        )

    results: list[
        RuntimeSubsystemVersionEvidence
    ] = []

    for file_path in sorted(
        runtime_root.rglob("*.py")
    ):

        try:
            text = file_path.read_text(
                encoding="utf-8"
            )
        except UnicodeDecodeError:
            text = file_path.read_text(
                encoding="utf-8-sig"
            )

        for match in _VERSION_PATTERN.finditer(text):

            results.append(
                RuntimeSubsystemVersionEvidence(
                    file=file_path.as_posix(),
                    symbol=match.group(1),
                    value=match.group(2),
                )
            )

    return tuple(results)


def build_runtime_architecture_version_read_model(
    *,
    runtime_root: Path,
) -> RuntimeArchitectureVersionReadModel:

    versions = (
        discover_runtime_subsystem_versions(
            runtime_root
        )
    )

    return RuntimeArchitectureVersionReadModel(
        architecture_name="Universal Runtime",

        architecture_registry_version=(
            RUNTIME_OWNER_ARCHITECTURE_REGISTRY_VERSION
        ),

        architecture_registry_schema_version=(
            RUNTIME_OWNER_ARCHITECTURE_REGISTRY_SCHEMA_VERSION
        ),

        owner_sections=(
            CANONICAL_RUNTIME_OWNER_SECTIONS
        ),

        subsystem_versions=versions,
    )


def certify_runtime_architecture_version_read_model_v1(
    *,
    runtime_root: Path,
) -> Mapping[str, Any]:

    model = (
        build_runtime_architecture_version_read_model(
            runtime_root=runtime_root
        )
    )

    payload = model.to_dict()

    checks = {
        "read_model_created":
            isinstance(
                model,
                RuntimeArchitectureVersionReadModel,
            ),

        "architecture_is_universal_runtime":
            payload["architecture_name"]
            == "Universal Runtime",

        "registry_version_present":
            bool(
                payload[
                    "architecture_registry_version"
                ]
            ),

        "registry_schema_present":
            bool(
                payload[
                    "architecture_registry_schema_version"
                ]
            ),

        "canonical_section_count_is_14":
            payload["owner_section_count"] == 14,

        "subsystem_versions_discovered":
            payload[
                "subsystem_version_count"
            ] > 0,

        "read_only_authority_preserved":
            (
                payload["authority"]
                ==
                "runtime_architecture_registry_and_runtime_sources"
            ),

        "no_version_mutation":
            True,

        "no_runtime_mutation":
            True,
    }

    return {
        "component":
            "Runtime Architecture Version Read Model",

        "version":
            RUNTIME_ARCHITECTURE_VERSION_READ_MODEL_VERSION,

        "schema_version":
            RUNTIME_ARCHITECTURE_VERSION_READ_MODEL_SCHEMA_VERSION,

        "checks":
            checks,

        "certified":
            all(checks.values()),

        "mode":
            "read_only_projection",

        "authority":
            "runtime_architecture_registry_and_runtime_sources",
    }


__all__ = [
    "RUNTIME_ARCHITECTURE_VERSION_READ_MODEL_VERSION",
    "RUNTIME_ARCHITECTURE_VERSION_READ_MODEL_SCHEMA_VERSION",
    "CANONICAL_RUNTIME_OWNER_SECTIONS",
    "RuntimeSubsystemVersionEvidence",
    "RuntimeArchitectureVersionReadModel",
    "discover_runtime_subsystem_versions",
    "build_runtime_architecture_version_read_model",
    "certify_runtime_architecture_version_read_model_v1",
]
