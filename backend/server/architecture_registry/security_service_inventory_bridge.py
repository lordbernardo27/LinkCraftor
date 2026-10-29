from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class SecurityServiceInventoryBridge:
    ALLOWED_KINDS = {
        "runtime-service",
        "microservice",
        "worker-service",
        "background-service",
        "internal-service",
        "edge-service",
        "integration-service",
        "platform-service",
        "other",
    }

    ALLOWED_STATUSES = {
        "discovered",
        "active",
        "inactive",
        "degraded",
        "failed",
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
                / "security_services.json"
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
                "LinkCraftor Security Service Inventory",
            "architecture_id":
                "platform-security-architecture",
            "component_id":
                "3.1.5",
            "runtime_authority":
                "backend/server/runtime/"
                "runtime_service_registry.py",
            "services": {},
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
                "security service inventory root must be an object"
            )

        if not isinstance(data.get("services"), dict):
            raise ValueError(
                "security service inventory services must be an object"
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
        service: Dict[str, Any],
        *,
        replace: bool = False,
    ) -> Dict[str, Any]:

        required = {
            "security_service_id",
            "service_key",
            "service_name",
            "service_kind",
            "environment",
            "status",
            "source",
        }

        missing = required - set(service)

        if missing:
            raise ValueError(
                "security service missing required fields: "
                + ", ".join(sorted(missing))
            )

        security_id = str(
            service["security_service_id"]
        ).strip().upper()

        if not security_id.startswith("SEC-SVC-"):
            raise ValueError(
                "security_service_id must start with SEC-SVC-"
            )

        service_key = str(
            service["service_key"]
        ).strip().lower()

        if not service_key:
            raise ValueError(
                "service_key must not be empty"
            )

        service_name = str(
            service["service_name"]
        ).strip()

        if not service_name:
            raise ValueError(
                "service_name must not be empty"
            )

        service_kind = str(
            service["service_kind"]
        ).strip().lower()

        if service_kind not in self.ALLOWED_KINDS:
            raise ValueError(
                "invalid service_kind"
            )

        environment = str(
            service["environment"]
        ).strip().lower()

        if environment not in self.ALLOWED_ENVIRONMENTS:
            raise ValueError(
                "invalid service environment"
            )

        status = str(
            service["status"]
        ).strip().lower()

        if status not in self.ALLOWED_STATUSES:
            raise ValueError(
                "invalid service status"
            )

        source = str(
            service["source"]
        ).strip()

        if not source:
            raise ValueError(
                "service source must not be empty"
            )

        now = self._now()
        stored = deepcopy(service)

        stored["security_service_id"] = security_id
        stored["service_key"] = service_key
        stored["service_name"] = service_name
        stored["service_kind"] = service_kind
        stored["environment"] = environment
        stored["status"] = status
        stored["source"] = source
        stored["asset_type"] = "service"
        stored["architecture_id"] = (
            "platform-security-architecture"
        )
        stored["component_id"] = "3.1.5"

        with self._lock:
            existing = self._data["services"].get(
                security_id
            )

            if existing is not None and not replace:
                raise ValueError(
                    f"security service already exists: {security_id}"
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

            self._data["services"][
                security_id
            ] = stored

            self._save()

        return deepcopy(stored)

    def get(
        self,
        security_service_id: str,
    ) -> Dict[str, Any]:

        security_id = (
            security_service_id.strip().upper()
        )

        with self._lock:
            if security_id not in self._data["services"]:
                raise KeyError(
                    f"security service not found: {security_id}"
                )

            return deepcopy(
                self._data["services"][security_id]
            )

    def by_service_key(
        self,
        service_key: str,
    ) -> Dict[str, Any]:

        normalized = service_key.strip().lower()

        with self._lock:
            matches = [
                deepcopy(record)
                for record in self._data["services"].values()
                if record.get("service_key") == normalized
            ]

        if not matches:
            raise KeyError(
                f"service key not found: {normalized}"
            )

        if len(matches) > 1:
            raise ValueError(
                f"duplicate service key in security inventory: "
                f"{normalized}"
            )

        return matches[0]

    def ingest_runtime_snapshot(
        self,
        snapshot: Any,
        *,
        environment: str,
        id_map: Dict[str, str],
    ) -> List[Dict[str, Any]]:

        ingested: List[Dict[str, Any]] = []

        services = getattr(
            snapshot,
            "services",
            (),
        )

        for binding in services:
            service_key = str(
                getattr(
                    binding,
                    "key",
                )
            ).strip().lower()

            security_id = id_map.get(
                service_key
            )

            if not security_id:
                raise ValueError(
                    f"missing security ID mapping for {service_key}"
                )

            capabilities = list(
                getattr(
                    binding,
                    "capabilities",
                    (),
                )
            )

            dependencies = list(
                getattr(
                    binding,
                    "dependencies",
                    (),
                )
            )

            record = {
                "security_service_id": security_id,
                "service_key": service_key,
                "service_name": service_key,
                "service_kind": "runtime-service",
                "environment": environment,
                "status": "active",
                "source":
                    "universal-runtime-service-registry",
                "runtime_service_type":
                    getattr(
                        binding,
                        "service_type",
                        None,
                    ),
                "runtime_capabilities":
                    capabilities,
                "runtime_dependencies":
                    dependencies,
                "runtime_startup_order":
                    getattr(
                        binding,
                        "startup_order",
                        None,
                    ),
            }

            existing = None

            try:
                existing = self.by_service_key(
                    service_key
                )
            except KeyError:
                pass

            if existing is not None:
                record["security_service_id"] = (
                    existing["security_service_id"]
                )

                ingested.append(
                    self.register(
                        {
                            **existing,
                            **record,
                        },
                        replace=True,
                    )
                )

                continue

            ingested.append(
                self.register(
                    record
                )
            )

        return ingested

    def list(
        self,
        *,
        status: Optional[str] = None,
        environment: Optional[str] = None,
        service_kind: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        with self._lock:
            records = deepcopy(
                list(
                    self._data["services"].values()
                )
            )

        filters = {
            "status": status,
            "environment": environment,
            "service_kind": service_kind,
        }

        for field, value in filters.items():
            if value is None:
                continue

            normalized = str(
                value
            ).strip().lower()

            records = [
                record
                for record in records
                if str(
                    record.get(field, "")
                ).strip().lower() == normalized
            ]

        return records

    def unauthorized_services(
        self,
    ) -> List[Dict[str, Any]]:
        return self.list(
            status="unauthorized"
        )

    def internet_exposed_services(
        self,
    ) -> List[Dict[str, Any]]:

        with self._lock:
            records = deepcopy(
                list(
                    self._data["services"].values()
                )
            )

        return [
            record
            for record in records
            if record.get("internet_exposed") is True
        ]

    def count(self) -> int:
        with self._lock:
            return len(
                self._data["services"]
            )


_default_bridge = None


def get_security_service_inventory_bridge():
    global _default_bridge

    if _default_bridge is None:
        _default_bridge = (
            SecurityServiceInventoryBridge()
        )

    return _default_bridge

