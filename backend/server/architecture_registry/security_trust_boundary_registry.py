from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class SecurityTrustBoundaryRegistry:
    ALLOWED_STATUSES = {
        "identified",
        "active",
        "under-review",
        "deprecated",
        "retired",
    }

    def __init__(self, path: Optional[Path] = None):
        if path is None:
            path = (
                Path(__file__).with_name("data")
                / "security_trust_boundaries.json"
            )

        self.path = Path(path)
        self._lock = RLock()
        self._data = self._load()

    def _empty(self):
        return {
            "schema_version": "1.0.0",
            "registry_name": "LinkCraftor Security Trust Boundary Registry",
            "boundaries": {},
        }

    def _load(self):
        if not self.path.exists():
            return self._empty()

        with self.path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)

        if not isinstance(data.get("boundaries"), dict):
            raise ValueError("trust boundaries must be an object")

        return data

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(self.path.suffix + ".tmp")

        with temp.open("w", encoding="utf-8") as handle:
            json.dump(
                self._data,
                handle,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )
            handle.write("\n")

        temp.replace(self.path)

    def register(
        self,
        boundary: Dict[str, Any],
        *,
        replace: bool = False,
    ) -> Dict[str, Any]:

        required = {
            "boundary_id",
            "name",
            "architecture_id",
            "source_zone",
            "destination_zone",
            "status",
        }

        missing = required - set(boundary)

        if missing:
            raise ValueError(
                "trust boundary missing fields: "
                + ", ".join(sorted(missing))
            )

        boundary_id = boundary["boundary_id"].strip().upper()

        if not boundary_id.startswith("SEC-TB-"):
            raise ValueError("boundary_id must start with SEC-TB-")

        status = boundary["status"].strip().lower()

        if status not in self.ALLOWED_STATUSES:
            raise ValueError("invalid trust boundary status")

        stored = deepcopy(boundary)
        stored["boundary_id"] = boundary_id
        stored["status"] = status

        with self._lock:
            if (
                boundary_id in self._data["boundaries"]
                and not replace
            ):
                raise ValueError(
                    f"trust boundary already exists: {boundary_id}"
                )

            self._data["boundaries"][boundary_id] = stored
            self._save()

        return deepcopy(stored)

    def get(self, boundary_id: str) -> Dict[str, Any]:
        boundary_id = boundary_id.strip().upper()

        with self._lock:
            if boundary_id not in self._data["boundaries"]:
                raise KeyError(
                    f"trust boundary not found: {boundary_id}"
                )

            return deepcopy(
                self._data["boundaries"][boundary_id]
            )

    def list(self) -> List[Dict[str, Any]]:
        with self._lock:
            return deepcopy(
                list(self._data["boundaries"].values())
            )


_default_registry = None


def get_security_trust_boundary_registry():
    global _default_registry

    if _default_registry is None:
        _default_registry = SecurityTrustBoundaryRegistry()

    return _default_registry
