from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class SecuritySoftwareAssetRegistry:
    ALLOWED_TYPES = {
        "operating-system",
        "runtime",
        "database-engine",
        "web-server",
        "reverse-proxy",
        "queue-platform",
        "worker-runtime",
        "build-tool",
        "deployment-tool",
        "security-tool",
        "monitoring-tool",
        "backup-tool",
        "administrative-tool",
        "development-tool",
        "infrastructure-software",
        "other",
    }

    ALLOWED_STATUSES = {
        "discovered",
        "active",
        "inactive",
        "unsupported",
        "prohibited",
        "quarantined",
        "decommissioning",
        "decommissioned",
    }

    ALLOWED_ENVIRONMENTS = {
        "development",
        "testing",
        "staging",
        "production",
        "corporate",
        "security",
        "shared",
        "unknown",
    }

    def __init__(self, path: Optional[Path] = None):
        if path is None:
            path = (
                Path(__file__).with_name("data")
                / "security_software_assets.json"
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
                "LinkCraftor Security Software Asset Registry",
            "architecture_id":
                "platform-security-architecture",
            "component_id":
                "3.1.2",
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
                "software asset registry root must be an object"
            )

        if not isinstance(data.get("assets"), dict):
            raise ValueError(
                "software asset registry assets must be an object"
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
            "software_asset_id",
            "software_name",
            "software_type",
            "environment",
            "status",
            "source",
        }

        missing = required - set(asset)

        if missing:
            raise ValueError(
                "software asset missing required fields: "
                + ", ".join(sorted(missing))
            )

        asset_id = str(
            asset["software_asset_id"]
        ).strip().upper()

        if not asset_id.startswith("SEC-SW-"):
            raise ValueError(
                "software_asset_id must start with SEC-SW-"
            )

        software_name = str(
            asset["software_name"]
        ).strip()

        if not software_name:
            raise ValueError(
                "software_name must not be empty"
            )

        software_type = str(
            asset["software_type"]
        ).strip().lower()

        if software_type not in self.ALLOWED_TYPES:
            raise ValueError(
                "invalid software_type"
            )

        environment = str(
            asset["environment"]
        ).strip().lower()

        if environment not in self.ALLOWED_ENVIRONMENTS:
            raise ValueError(
                "invalid software environment"
            )

        status = str(
            asset["status"]
        ).strip().lower()

        if status not in self.ALLOWED_STATUSES:
            raise ValueError(
                "invalid software asset status"
            )

        source = str(
            asset["source"]
        ).strip()

        if not source:
            raise ValueError(
                "software source must not be empty"
            )

        now = self._now()
        stored = deepcopy(asset)

        stored["software_asset_id"] = asset_id
        stored["software_name"] = software_name
        stored["software_type"] = software_type
        stored["environment"] = environment
        stored["status"] = status
        stored["source"] = source
        stored["asset_type"] = "software"
        stored["architecture_id"] = (
            "platform-security-architecture"
        )
        stored["component_id"] = "3.1.2"

        with self._lock:
            existing = self._data["assets"].get(
                asset_id
            )

            if existing is not None and not replace:
                raise ValueError(
                    f"software asset already exists: {asset_id}"
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
        software_asset_id: str,
    ) -> Dict[str, Any]:

        asset_id = software_asset_id.strip().upper()

        with self._lock:
            if asset_id not in self._data["assets"]:
                raise KeyError(
                    f"software asset not found: {asset_id}"
                )

            return deepcopy(
                self._data["assets"][asset_id]
            )

    def update(
        self,
        software_asset_id: str,
        changes: Dict[str, Any],
    ) -> Dict[str, Any]:

        asset_id = software_asset_id.strip().upper()

        forbidden = {
            "software_asset_id",
            "asset_type",
            "architecture_id",
            "component_id",
            "first_seen_at",
        }

        if forbidden.intersection(changes):
            raise ValueError(
                "immutable software asset identity fields "
                "cannot be changed"
            )

        with self._lock:
            if asset_id not in self._data["assets"]:
                raise KeyError(
                    f"software asset not found: {asset_id}"
                )

            current = deepcopy(
                self._data["assets"][asset_id]
            )

        merged = {
            **current,
            **deepcopy(changes),
            "software_asset_id": asset_id,
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
        software_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        with self._lock:
            records = deepcopy(
                list(
                    self._data["assets"].values()
                )
            )

        if status is not None:
            normalized = status.strip().lower()

            records = [
                record
                for record in records
                if record.get("status") == normalized
            ]

        if environment is not None:
            normalized = environment.strip().lower()

            records = [
                record
                for record in records
                if record.get("environment") == normalized
            ]

        if software_type is not None:
            normalized = software_type.strip().lower()

            records = [
                record
                for record in records
                if record.get("software_type") == normalized
            ]

        return records

    def active_assets(self) -> List[Dict[str, Any]]:
        return self.list(
            status="active"
        )

    def unsupported_assets(
        self,
    ) -> List[Dict[str, Any]]:
        return self.list(
            status="unsupported"
        )

    def prohibited_assets(
        self,
    ) -> List[Dict[str, Any]]:
        return self.list(
            status="prohibited"
        )

    def count(self) -> int:
        with self._lock:
            return len(
                self._data["assets"]
            )


_default_registry = None


def get_security_software_asset_registry():
    global _default_registry

    if _default_registry is None:
        _default_registry = (
            SecuritySoftwareAssetRegistry()
        )

    return _default_registry
