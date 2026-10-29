from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class SecurityApplicationRegistry:
    ALLOWED_TYPES = {
        "customer-web",
        "staff-web",
        "owner-web",
        "admin-web",
        "internal-platform",
        "plugin",
        "integration-application",
        "mobile",
        "desktop",
        "background-application",
        "other",
    }

    ALLOWED_STATUSES = {
        "discovered",
        "active",
        "inactive",
        "deprecated",
        "unauthorized",
        "quarantined",
        "decommissioning",
        "decommissioned",
    }

    ALLOWED_ENVIRONMENTS = {
        "development",
        "testing",
        "staging",
        "production",
        "shared",
        "internal",
        "unknown",
    }

    def __init__(self, path: Optional[Path] = None):
        if path is None:
            path = (
                Path(__file__).with_name("data")
                / "security_applications.json"
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
                "LinkCraftor Security Application Registry",
            "architecture_id":
                "platform-security-architecture",
            "component_id":
                "3.1.4",
            "applications": {},
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
                "application registry root must be an object"
            )

        if not isinstance(
            data.get("applications"),
            dict,
        ):
            raise ValueError(
                "application registry applications must be an object"
            )

        return data

    def _save(self) -> None:
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary = self.path.with_suffix(
            self.path.suffix + ".tmp"
        )

        with temporary.open(
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

        temporary.replace(self.path)

    def register(
        self,
        application: Dict[str, Any],
        *,
        replace: bool = False,
    ) -> Dict[str, Any]:

        required = {
            "application_id",
            "application_name",
            "application_type",
            "environment",
            "status",
            "source",
        }

        missing = required - set(application)

        if missing:
            raise ValueError(
                "application missing required fields: "
                + ", ".join(sorted(missing))
            )

        application_id = str(
            application["application_id"]
        ).strip().upper()

        if not application_id.startswith("SEC-APP-"):
            raise ValueError(
                "application_id must start with SEC-APP-"
            )

        application_name = str(
            application["application_name"]
        ).strip()

        if not application_name:
            raise ValueError(
                "application_name must not be empty"
            )

        application_type = str(
            application["application_type"]
        ).strip().lower()

        if application_type not in self.ALLOWED_TYPES:
            raise ValueError(
                "invalid application_type"
            )

        environment = str(
            application["environment"]
        ).strip().lower()

        if environment not in self.ALLOWED_ENVIRONMENTS:
            raise ValueError(
                "invalid application environment"
            )

        status = str(
            application["status"]
        ).strip().lower()

        if status not in self.ALLOWED_STATUSES:
            raise ValueError(
                "invalid application status"
            )

        source = str(
            application["source"]
        ).strip()

        if not source:
            raise ValueError(
                "application source must not be empty"
            )

        now = self._now()
        stored = deepcopy(application)

        stored["application_id"] = application_id
        stored["application_name"] = application_name
        stored["application_type"] = application_type
        stored["environment"] = environment
        stored["status"] = status
        stored["source"] = source
        stored["asset_type"] = "application"
        stored["architecture_id"] = (
            "platform-security-architecture"
        )
        stored["component_id"] = "3.1.4"

        with self._lock:
            existing = self._data["applications"].get(
                application_id
            )

            if existing is not None and not replace:
                raise ValueError(
                    f"application already exists: {application_id}"
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

            self._data["applications"][
                application_id
            ] = stored

            self._save()

        return deepcopy(stored)

    def get(
        self,
        application_id: str,
    ) -> Dict[str, Any]:

        application_id = application_id.strip().upper()

        with self._lock:
            if application_id not in self._data["applications"]:
                raise KeyError(
                    f"application not found: {application_id}"
                )

            return deepcopy(
                self._data["applications"][
                    application_id
                ]
            )

    def update(
        self,
        application_id: str,
        changes: Dict[str, Any],
    ) -> Dict[str, Any]:

        application_id = application_id.strip().upper()

        forbidden = {
            "application_id",
            "asset_type",
            "architecture_id",
            "component_id",
            "first_seen_at",
        }

        if forbidden.intersection(changes):
            raise ValueError(
                "immutable application identity fields "
                "cannot be changed"
            )

        with self._lock:
            if application_id not in self._data["applications"]:
                raise KeyError(
                    f"application not found: {application_id}"
                )

            current = deepcopy(
                self._data["applications"][
                    application_id
                ]
            )

        merged = {
            **current,
            **deepcopy(changes),
            "application_id": application_id,
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
        application_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        with self._lock:
            records = deepcopy(
                list(
                    self._data["applications"].values()
                )
            )

        filters = {
            "status": status,
            "environment": environment,
            "application_type": application_type,
        }

        for field, value in filters.items():
            if value is None:
                continue

            normalized = str(value).strip().lower()

            records = [
                record
                for record in records
                if str(
                    record.get(field, "")
                ).strip().lower() == normalized
            ]

        return records

    def unauthorized_applications(
        self,
    ) -> List[Dict[str, Any]]:
        return self.list(
            status="unauthorized"
        )

    def internet_exposed_applications(
        self,
    ) -> List[Dict[str, Any]]:

        with self._lock:
            records = deepcopy(
                list(
                    self._data["applications"].values()
                )
            )

        return [
            record
            for record in records
            if record.get("internet_exposed") is True
        ]

    def tenant_aware_applications(
        self,
    ) -> List[Dict[str, Any]]:

        with self._lock:
            records = deepcopy(
                list(
                    self._data["applications"].values()
                )
            )

        return [
            record
            for record in records
            if record.get("tenant_aware") is True
        ]

    def production_applications(
        self,
    ) -> List[Dict[str, Any]]:
        return self.list(
            environment="production"
        )

    def count(self) -> int:
        with self._lock:
            return len(
                self._data["applications"]
            )


_default_registry = None


def get_security_application_registry():
    global _default_registry

    if _default_registry is None:
        _default_registry = (
            SecurityApplicationRegistry()
        )

    return _default_registry
