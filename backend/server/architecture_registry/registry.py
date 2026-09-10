from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class ArchitectureRegistryError(RuntimeError):
    """Base error for Central Architecture Registry operations."""


class ArchitectureNotFoundError(ArchitectureRegistryError):
    """Raised when a requested architecture is not registered."""


class ArchitectureAlreadyRegisteredError(ArchitectureRegistryError):
    """Raised when duplicate registration is attempted without replacement."""


class ArchitectureRegistry:
    """
    Canonical LinkCraftor Central Architecture Registry.

    The registry does not execute an architecture.

    It records and governs architecture identity, canonical locations,
    versions, components, dependencies, ownership, certification state,
    integration state, and lifecycle metadata.

    Execution remains in the architecture's real modules and services.
    """

    SCHEMA_VERSION = "1.0.0"

    def __init__(self, registry_path: Optional[Path] = None) -> None:
        self._lock = RLock()

        if registry_path is None:
            registry_path = Path(__file__).with_name(
                "architecture_registry.json"
            )

        self.registry_path = Path(registry_path)
        self._data = self._load()

    def _empty_registry(self) -> Dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "registry_name": "LinkCraftor Central Architecture Registry",
            "architectures": {},
        }

    def _load(self) -> Dict[str, Any]:
        if not self.registry_path.exists():
            return self._empty_registry()

        with self.registry_path.open(
            "r",
            encoding="utf-8-sig",
        ) as handle:
            data = json.load(handle)

        if not isinstance(data, dict):
            raise ArchitectureRegistryError(
                "Architecture registry root must be a JSON object."
            )

        architectures = data.get("architectures")

        if not isinstance(architectures, dict):
            raise ArchitectureRegistryError(
                "Architecture registry must contain an architectures object."
            )

        return data

    def _save(self) -> None:
        self.registry_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_path = self.registry_path.with_suffix(
            self.registry_path.suffix + ".tmp"
        )

        with temporary_path.open(
            "w",
            encoding="utf-8",
        ) as handle:
            json.dump(
                self._data,
                handle,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )
            handle.write("\n")

        temporary_path.replace(self.registry_path)

    def reload(self) -> None:
        with self._lock:
            self._data = self._load()

    def list_architectures(self) -> List[Dict[str, Any]]:
        with self._lock:
            values = list(
                self._data["architectures"].values()
            )

            return deepcopy(
                sorted(
                    values,
                    key=lambda item: item["architecture_id"],
                )
            )

    def exists(self, architecture_id: str) -> bool:
        normalized = self._normalize_id(architecture_id)

        with self._lock:
            return normalized in self._data["architectures"]

    def get(self, architecture_id: str) -> Dict[str, Any]:
        normalized = self._normalize_id(architecture_id)

        with self._lock:
            architecture = self._data["architectures"].get(
                normalized
            )

            if architecture is None:
                raise ArchitectureNotFoundError(
                    f"Architecture is not registered: {normalized}"
                )

            return deepcopy(architecture)

    def register(
        self,
        architecture: Dict[str, Any],
        *,
        replace: bool = False,
    ) -> Dict[str, Any]:
        self._validate_architecture(architecture)

        normalized = self._normalize_id(
            architecture["architecture_id"]
        )

        record = deepcopy(architecture)
        record["architecture_id"] = normalized

        with self._lock:
            if (
                normalized in self._data["architectures"]
                and not replace
            ):
                raise ArchitectureAlreadyRegisteredError(
                    f"Architecture already registered: {normalized}"
                )

            self._data["architectures"][normalized] = record
            self._save()

        return deepcopy(record)

    def update(
        self,
        architecture_id: str,
        changes: Dict[str, Any],
    ) -> Dict[str, Any]:
        normalized = self._normalize_id(architecture_id)

        protected_fields = {
            "architecture_id",
        }

        forbidden = protected_fields.intersection(changes)

        if forbidden:
            raise ArchitectureRegistryError(
                "Protected architecture fields cannot be changed: "
                + ", ".join(sorted(forbidden))
            )

        with self._lock:
            if normalized not in self._data["architectures"]:
                raise ArchitectureNotFoundError(
                    f"Architecture is not registered: {normalized}"
                )

            updated = deepcopy(
                self._data["architectures"][normalized]
            )
            updated.update(deepcopy(changes))

            self._validate_architecture(updated)

            self._data["architectures"][normalized] = updated
            self._save()

            return deepcopy(updated)

    def get_component(
        self,
        architecture_id: str,
        component_id: str,
    ) -> Dict[str, Any]:
        architecture = self.get(architecture_id)

        for component in architecture.get("components", []):
            if component.get("component_id") == component_id:
                return deepcopy(component)

        raise ArchitectureNotFoundError(
            f"Architecture component not registered: "
            f"{architecture_id}/{component_id}"
        )

    def find_by_family(
        self,
        architecture_family: str,
    ) -> List[Dict[str, Any]]:
        wanted = architecture_family.strip().lower()

        return [
            architecture
            for architecture in self.list_architectures()
            if architecture.get(
                "architecture_family",
                "",
            ).strip().lower() == wanted
        ]

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return deepcopy(self._data)

    @staticmethod
    def _normalize_id(value: str) -> str:
        if not isinstance(value, str):
            raise ArchitectureRegistryError(
                "architecture_id must be a string."
            )

        normalized = value.strip().lower()

        if not normalized:
            raise ArchitectureRegistryError(
                "architecture_id cannot be empty."
            )

        return normalized

    def _validate_architecture(
        self,
        architecture: Dict[str, Any],
    ) -> None:
        if not isinstance(architecture, dict):
            raise ArchitectureRegistryError(
                "Architecture record must be a dictionary."
            )

        required_fields = (
            "architecture_id",
            "architecture_name",
            "architecture_family",
            "version",
            "status",
            "canonical_root",
            "owner",
            "components",
        )

        missing = [
            field
            for field in required_fields
            if field not in architecture
        ]

        if missing:
            raise ArchitectureRegistryError(
                "Architecture record missing required fields: "
                + ", ".join(missing)
            )

        self._normalize_id(
            architecture["architecture_id"]
        )

        for field in (
            "architecture_name",
            "architecture_family",
            "version",
            "status",
            "canonical_root",
            "owner",
        ):
            value = architecture[field]

            if not isinstance(value, str) or not value.strip():
                raise ArchitectureRegistryError(
                    f"{field} must be a non-empty string."
                )

        components = architecture["components"]

        if not isinstance(components, list):
            raise ArchitectureRegistryError(
                "components must be a list."
            )

        seen_component_ids = set()

        for component in components:
            if not isinstance(component, dict):
                raise ArchitectureRegistryError(
                    "Each component must be a dictionary."
                )

            component_id = component.get("component_id")
            name = component.get("name")
            canonical_path = component.get("canonical_path")

            if (
                not isinstance(component_id, str)
                or not component_id.strip()
            ):
                raise ArchitectureRegistryError(
                    "Each component requires component_id."
                )

            if component_id in seen_component_ids:
                raise ArchitectureRegistryError(
                    f"Duplicate component_id: {component_id}"
                )

            seen_component_ids.add(component_id)

            if not isinstance(name, str) or not name.strip():
                raise ArchitectureRegistryError(
                    f"Component {component_id} requires name."
                )

            if (
                not isinstance(canonical_path, str)
                or not canonical_path.strip()
            ):
                raise ArchitectureRegistryError(
                    f"Component {component_id} requires canonical_path."
                )


_registry_instance: Optional[ArchitectureRegistry] = None
_registry_instance_lock = RLock()


def get_architecture_registry() -> ArchitectureRegistry:
    global _registry_instance

    with _registry_instance_lock:
        if _registry_instance is None:
            _registry_instance = ArchitectureRegistry()

        return _registry_instance
