from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class SecurityApiInventoryBridge:
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
                / "security_apis.json"
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
                "LinkCraftor Security API Inventory",
            "architecture_id":
                "platform-security-architecture",
            "component_id":
                "3.1.6",
            "runtime_authority":
                "backend/server/main.py::app.routes",
            "apis": {},
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
                "security API inventory root must be an object"
            )

        if not isinstance(
            data.get("apis"),
            dict,
        ):
            raise ValueError(
                "security API inventory apis must be an object"
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

    @staticmethod
    def route_key(
        path: str,
        methods: List[str],
    ) -> str:
        normalized_methods = ",".join(
            sorted(
                str(method).upper()
                for method in methods
            )
        )

        return (
            normalized_methods
            + " "
            + str(path).strip()
        )

    def register(
        self,
        api: Dict[str, Any],
        *,
        replace: bool = False,
    ) -> Dict[str, Any]:

        required = {
            "security_api_id",
            "path",
            "methods",
            "route_name",
            "environment",
            "status",
            "source",
        }

        missing = required - set(api)

        if missing:
            raise ValueError(
                "security API missing required fields: "
                + ", ".join(sorted(missing))
            )

        security_id = str(
            api["security_api_id"]
        ).strip().upper()

        if not security_id.startswith("SEC-API-"):
            raise ValueError(
                "security_api_id must start with SEC-API-"
            )

        path = str(
            api["path"]
        ).strip()

        if not path:
            raise ValueError(
                "API path must not be empty"
            )

        methods = sorted(
            {
                str(method).strip().upper()
                for method in api["methods"]
                if str(method).strip()
            }
        )

        route_name = str(
            api["route_name"]
        ).strip()

        environment = str(
            api["environment"]
        ).strip().lower()

        if environment not in self.ALLOWED_ENVIRONMENTS:
            raise ValueError(
                "invalid API environment"
            )

        status = str(
            api["status"]
        ).strip().lower()

        if status not in self.ALLOWED_STATUSES:
            raise ValueError(
                "invalid API status"
            )

        source = str(
            api["source"]
        ).strip()

        if not source:
            raise ValueError(
                "API source must not be empty"
            )

        now = self._now()

        stored = deepcopy(api)

        stored["security_api_id"] = security_id
        stored["path"] = path
        stored["methods"] = methods
        stored["route_name"] = route_name
        stored["environment"] = environment
        stored["status"] = status
        stored["source"] = source
        stored["asset_type"] = "api"
        stored["architecture_id"] = (
            "platform-security-architecture"
        )
        stored["component_id"] = "3.1.6"
        stored["route_key"] = self.route_key(
            path,
            methods,
        )

        with self._lock:
            existing = self._data["apis"].get(
                security_id
            )

            if existing is not None and not replace:
                raise ValueError(
                    f"security API already exists: {security_id}"
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

            self._data["apis"][
                security_id
            ] = stored

            self._save()

        return deepcopy(stored)

    def by_route(
        self,
        path: str,
        methods: List[str],
    ) -> Dict[str, Any]:

        key = self.route_key(
            path,
            methods,
        )

        with self._lock:
            matches = [
                deepcopy(record)
                for record in self._data["apis"].values()
                if record.get("route_key") == key
            ]

        if not matches:
            raise KeyError(
                f"API route not found: {key}"
            )

        if len(matches) > 1:
            raise ValueError(
                f"duplicate API route in security inventory: {key}"
            )

        return matches[0]

    def ingest_fastapi_routes(
        self,
        app: Any,
        *,
        environment: str,
        id_map: Dict[str, str],
    ) -> List[Dict[str, Any]]:

        ingested: List[Dict[str, Any]] = []

        for route in app.routes:
            path = getattr(
                route,
                "path",
                None,
            )

            if not path:
                continue

            methods = sorted(
                getattr(
                    route,
                    "methods",
                    [],
                )
                or []
            )

            if not methods:
                continue

            key = self.route_key(
                path,
                methods,
            )

            security_id = id_map.get(
                key
            )

            if not security_id:
                continue

            route_name = str(
                getattr(
                    route,
                    "name",
                    "",
                )
                or ""
            )

            tags = list(
                getattr(
                    route,
                    "tags",
                    [],
                )
                or []
            )

            record = {
                "security_api_id":
                    security_id,
                "path":
                    path,
                "methods":
                    methods,
                "route_name":
                    route_name,
                "environment":
                    environment,
                "status":
                    "active",
                "source":
                    "fastapi-app-routes",
                "tags":
                    tags,
            }

            existing = None

            try:
                existing = self.by_route(
                    path,
                    methods,
                )
            except KeyError:
                pass

            if existing is not None:
                record["security_api_id"] = (
                    existing["security_api_id"]
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

    def get(
        self,
        security_api_id: str,
    ) -> Dict[str, Any]:

        security_id = (
            security_api_id.strip().upper()
        )

        with self._lock:
            if security_id not in self._data["apis"]:
                raise KeyError(
                    f"security API not found: {security_id}"
                )

            return deepcopy(
                self._data["apis"][
                    security_id
                ]
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
                    self._data["apis"].values()
                )
            )

        filters = {
            "status": status,
            "environment": environment,
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
                    record.get(
                        field,
                        "",
                    )
                ).strip().lower() == normalized
            ]

        return records

    def unauthorized_apis(
        self,
    ) -> List[Dict[str, Any]]:
        return self.list(
            status="unauthorized"
        )

    def deprecated_apis(
        self,
    ) -> List[Dict[str, Any]]:
        return self.list(
            status="deprecated"
        )

    def count(self) -> int:
        with self._lock:
            return len(
                self._data["apis"]
            )


_default_bridge = None


def get_security_api_inventory_bridge():
    global _default_bridge

    if _default_bridge is None:
        _default_bridge = (
            SecurityApiInventoryBridge()
        )

    return _default_bridge
