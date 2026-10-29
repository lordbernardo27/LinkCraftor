from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class SecurityHardwareAssetRegistry:
    ALLOWED_STATUSES = {
        "discovered",
        "active",
        "inactive",
        "quarantined",
        "decommissioning",
        "decommissioned",
        "unauthorized",
    }

    ALLOWED_ENVIRONMENTS = {
        "development",
        "testing",
        "staging",
        "production",
        "corporate",
        "security",
        "unknown",
    }

    def __init__(self, path: Optional[Path] = None):
        if path is None:
            path = (
                Path(__file__).with_name("data")
                / "security_hardware_assets.json"
            )

        self.path = Path(path)
        self._lock = RLock()
        self._data = self._load()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _empty(self) -> Dict[str, Any]:
        return {
            "schema_version": "1.0.0",
            "registry_name":
                "LinkCraftor Security Hardware Asset Registry",
            "architecture_id":
                "platform-security-architecture",
            "component_id":
                "3.1.1",
            "assets": {},
        }

    def _load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return self._empty()

        with self.path.open(
            "r",
            encoding="utf-8-sig",
        ) as handle:
            data = json.load(handle)

        if not isinstance(data, dict):
            raise ValueError(
                "hardware asset registry root must be an object"
            )

        if not isinstance(data.get("assets"), dict):
            raise ValueError(
                "hardware asset registry assets must be an object"
            )

        return data

    def _save(self) -> None:
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp = self.path.with_suffix(
            self.path.suffix + ".tmp"
        )

        with temp.open(
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

        temp.replace(self.path)

    def register(
        self,
        asset: Dict[str, Any],
        *,
        replace: bool = False,
    ) -> Dict[str, Any]:

        required = {
            "asset_id",
            "asset_name",
            "environment",
            "status",
            "source",
        }

        missing = required - set(asset)

        if missing:
            raise ValueError(
                "hardware asset missing required fields: "
                + ", ".join(sorted(missing))
            )

        asset_id = str(
            asset["asset_id"]
        ).strip().upper()

        if not asset_id.startswith("SEC-HW-"):
            raise ValueError(
                "hardware asset_id must start with SEC-HW-"
            )

        asset_name = str(
            asset["asset_name"]
        ).strip()

        if not asset_name:
            raise ValueError(
                "hardware asset_name must not be empty"
            )

        environment = str(
            asset["environment"]
        ).strip().lower()

        if environment not in self.ALLOWED_ENVIRONMENTS:
            raise ValueError(
                "invalid hardware asset environment"
            )

        status = str(
            asset["status"]
        ).strip().lower()

        if status not in self.ALLOWED_STATUSES:
            raise ValueError(
                "invalid hardware asset status"
            )

        source = str(
            asset["source"]
        ).strip()

        if not source:
            raise ValueError(
                "hardware asset source must not be empty"
            )

        now = self._now()

        stored = deepcopy(asset)

        stored["asset_id"] = asset_id
        stored["asset_type"] = "hardware"
        stored["asset_name"] = asset_name
        stored["architecture_id"] = (
            "platform-security-architecture"
        )
        stored["component_id"] = "3.1.1"
        stored["environment"] = environment
        stored["status"] = status
        stored["source"] = source

        with self._lock:
            existing = self._data["assets"].get(
                asset_id
            )

            if existing is not None and not replace:
                raise ValueError(
                    f"hardware asset already exists: {asset_id}"
                )

            if existing is not None:
                stored["first_seen_at"] = (
                    existing.get("first_seen_at")
                    or now
                )
            else:
                stored["first_seen_at"] = (
                    stored.get("first_seen_at")
                    or now
                )

            stored["last_seen_at"] = now

            self._data["assets"][asset_id] = stored
            self._save()

        return deepcopy(stored)

    def get(
        self,
        asset_id: str,
    ) -> Dict[str, Any]:

        asset_id = asset_id.strip().upper()

        with self._lock:
            if asset_id not in self._data["assets"]:
                raise KeyError(
                    f"hardware asset not found: {asset_id}"
                )

            return deepcopy(
                self._data["assets"][asset_id]
            )

    def update(
        self,
        asset_id: str,
        changes: Dict[str, Any],
    ) -> Dict[str, Any]:

        asset_id = asset_id.strip().upper()

        forbidden = {
            "asset_id",
            "asset_type",
            "architecture_id",
            "component_id",
            "first_seen_at",
        }

        if forbidden.intersection(changes):
            raise ValueError(
                "immutable hardware asset identity fields "
                "cannot be changed"
            )

        with self._lock:
            if asset_id not in self._data["assets"]:
                raise KeyError(
                    f"hardware asset not found: {asset_id}"
                )

            current = deepcopy(
                self._data["assets"][asset_id]
            )

        merged = {
            **current,
            **deepcopy(changes),
            "asset_id": asset_id,
        }

        return self.register(
            merged,
            replace=True,
        )

    def list(
        self,
        *,
        status: Optional[str] = None,
        environment: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        with self._lock:
            records = deepcopy(
                list(
                    self._data["assets"].values()
                )
            )

        if status is not None:
            normalized_status = status.strip().lower()

            records = [
                record
                for record in records
                if record.get("status")
                == normalized_status
            ]

        if environment is not None:
            normalized_environment = (
                environment.strip().lower()
            )

            records = [
                record
                for record in records
                if record.get("environment")
                == normalized_environment
            ]

        return records

    def active_assets(self) -> List[Dict[str, Any]]:
        return self.list(
            status="active"
        )

    def unauthorized_assets(
        self,
    ) -> List[Dict[str, Any]]:
        return self.list(
            status="unauthorized"
        )

    def count(self) -> int:
        with self._lock:
            return len(
                self._data["assets"]
            )


_default_registry = None


def get_security_hardware_asset_registry():
    global _default_registry

    if _default_registry is None:
        _default_registry = (
            SecurityHardwareAssetRegistry()
        )

    return _default_registry
