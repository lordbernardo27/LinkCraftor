from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class SecurityCloudResourceRegistry:
    ALLOWED_PROVIDERS = {
        "aws",
    }

    ALLOWED_ENVIRONMENTS = {
        "development",
        "testing",
        "staging",
        "production",
        "sandbox",
        "shared",
        "security",
        "infrastructure",
        "deployment",
        "management",
        "unknown",
    }

    ALLOWED_STATUSES = {
        "discovered",
        "active",
        "inactive",
        "unauthorized",
        "quarantined",
        "decommissioning",
        "decommissioned",
    }

    ALLOWED_PORTFOLIO_STATUSES = {
        "approved",
        "conditionally-approved",
        "future",
        "not-approved",
        "unclassified",
    }

    def __init__(self, path: Optional[Path] = None):
        if path is None:
            path = (
                Path(__file__).with_name("data")
                / "security_cloud_resources.json"
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
                "LinkCraftor Security Cloud Resource Registry",
            "architecture_id":
                "platform-security-architecture",
            "component_id":
                "3.1.3",
            "provider_scope": [
                "aws",
            ],
            "authoritative_architecture_sources": [
                "backend/infra/architecture/"
                "cloud_resource_organization.md",
                "backend/infra/architecture/"
                "cloud_service_portfolio.md",
            ],
            "resources": {},
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
                "cloud resource registry root must be an object"
            )

        if not isinstance(data.get("resources"), dict):
            raise ValueError(
                "cloud resource registry resources must be an object"
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
        resource: Dict[str, Any],
        *,
        replace: bool = False,
    ) -> Dict[str, Any]:

        required = {
            "cloud_resource_id",
            "provider",
            "provider_resource_type",
            "resource_name",
            "account_reference",
            "region",
            "environment",
            "status",
            "source",
        }

        missing = required - set(resource)

        if missing:
            raise ValueError(
                "cloud resource missing required fields: "
                + ", ".join(sorted(missing))
            )

        resource_id = str(
            resource["cloud_resource_id"]
        ).strip().upper()

        if not resource_id.startswith("SEC-CLD-"):
            raise ValueError(
                "cloud_resource_id must start with SEC-CLD-"
            )

        provider = str(
            resource["provider"]
        ).strip().lower()

        if provider not in self.ALLOWED_PROVIDERS:
            raise ValueError(
                "unsupported cloud provider"
            )

        provider_resource_type = str(
            resource["provider_resource_type"]
        ).strip()

        if not provider_resource_type:
            raise ValueError(
                "provider_resource_type must not be empty"
            )

        resource_name = str(
            resource["resource_name"]
        ).strip()

        if not resource_name:
            raise ValueError(
                "resource_name must not be empty"
            )

        account_reference = str(
            resource["account_reference"]
        ).strip()

        if not account_reference:
            raise ValueError(
                "account_reference must not be empty"
            )

        region = str(
            resource["region"]
        ).strip()

        if not region:
            raise ValueError(
                "region must not be empty"
            )

        environment = str(
            resource["environment"]
        ).strip().lower()

        if environment not in self.ALLOWED_ENVIRONMENTS:
            raise ValueError(
                "invalid cloud resource environment"
            )

        status = str(
            resource["status"]
        ).strip().lower()

        if status not in self.ALLOWED_STATUSES:
            raise ValueError(
                "invalid cloud resource status"
            )

        source = str(
            resource["source"]
        ).strip()

        if not source:
            raise ValueError(
                "cloud resource source must not be empty"
            )

        portfolio_status = str(
            resource.get(
                "portfolio_status",
                "unclassified",
            )
        ).strip().lower()

        if portfolio_status not in self.ALLOWED_PORTFOLIO_STATUSES:
            raise ValueError(
                "invalid portfolio_status"
            )

        now = self._now()
        stored = deepcopy(resource)

        stored["cloud_resource_id"] = resource_id
        stored["asset_type"] = "cloud-resource"
        stored["provider"] = provider
        stored["provider_resource_type"] = (
            provider_resource_type
        )
        stored["resource_name"] = resource_name
        stored["account_reference"] = account_reference
        stored["region"] = region
        stored["environment"] = environment
        stored["status"] = status
        stored["source"] = source
        stored["portfolio_status"] = portfolio_status
        stored["architecture_id"] = (
            "platform-security-architecture"
        )
        stored["component_id"] = "3.1.3"

        with self._lock:
            existing = self._data["resources"].get(
                resource_id
            )

            if existing is not None and not replace:
                raise ValueError(
                    f"cloud resource already exists: {resource_id}"
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

            self._data["resources"][resource_id] = stored
            self._save()

        return deepcopy(stored)

    def get(
        self,
        cloud_resource_id: str,
    ) -> Dict[str, Any]:

        resource_id = (
            cloud_resource_id.strip().upper()
        )

        with self._lock:
            if resource_id not in self._data["resources"]:
                raise KeyError(
                    f"cloud resource not found: {resource_id}"
                )

            return deepcopy(
                self._data["resources"][resource_id]
            )

    def update(
        self,
        cloud_resource_id: str,
        changes: Dict[str, Any],
    ) -> Dict[str, Any]:

        resource_id = (
            cloud_resource_id.strip().upper()
        )

        forbidden = {
            "cloud_resource_id",
            "asset_type",
            "architecture_id",
            "component_id",
            "first_seen_at",
        }

        if forbidden.intersection(changes):
            raise ValueError(
                "immutable cloud-resource identity fields "
                "cannot be changed"
            )

        with self._lock:
            if resource_id not in self._data["resources"]:
                raise KeyError(
                    f"cloud resource not found: {resource_id}"
                )

            current = deepcopy(
                self._data["resources"][resource_id]
            )

        merged = {
            **current,
            **deepcopy(changes),
            "cloud_resource_id": resource_id,
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
        account_reference: Optional[str] = None,
        region: Optional[str] = None,
        provider_resource_type: Optional[str] = None,
        portfolio_status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        with self._lock:
            records = deepcopy(
                list(
                    self._data["resources"].values()
                )
            )

        filters = {
            "status": status,
            "environment": environment,
            "account_reference": account_reference,
            "region": region,
            "provider_resource_type": provider_resource_type,
            "portfolio_status": portfolio_status,
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

    def unauthorized_resources(
        self,
    ) -> List[Dict[str, Any]]:
        return self.list(
            status="unauthorized"
        )

    def unmanaged_resources(
        self,
    ) -> List[Dict[str, Any]]:

        with self._lock:
            records = deepcopy(
                list(
                    self._data["resources"].values()
                )
            )

        return [
            record
            for record in records
            if record.get("managed") is False
        ]

    def production_resources(
        self,
    ) -> List[Dict[str, Any]]:
        return self.list(
            environment="production"
        )

    def not_approved_resources(
        self,
    ) -> List[Dict[str, Any]]:
        return self.list(
            portfolio_status="not-approved"
        )

    def count(self) -> int:
        with self._lock:
            return len(
                self._data["resources"]
            )


_default_registry = None


def get_security_cloud_resource_registry():
    global _default_registry

    if _default_registry is None:
        _default_registry = (
            SecurityCloudResourceRegistry()
        )

    return _default_registry
