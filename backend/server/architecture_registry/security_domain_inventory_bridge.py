from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class SecurityDomainInventoryBridge:

    ALLOWED_TYPES = {
        "domain",
        "subdomain",
        "hostname",
        "service-hostname",
        "internal-hostname",
        "external-hostname",
        "other",
    }

    ALLOWED_STATUSES = {
        "discovered",
        "active",
        "inactive",
        "pending",
        "unauthorized",
        "quarantined",
        "deprecated",
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

    ALLOWED_EXPOSURES = {
        "unknown",
        "internal",
        "restricted",
        "external",
        "internet-exposed",
    }

    def __init__(
        self,
        path: Optional[Path] = None,
    ):
        if path is None:
            path = (
                Path(__file__).with_name("data")
                / "security_domains.json"
            )

        self.path = Path(path)
        self._lock = RLock()
        self._data = self._load()

    @staticmethod
    def _now() -> str:
        return datetime.now(
            timezone.utc
        ).isoformat()

    def _empty(self) -> Dict[str, Any]:
        return {
            "schema_version": "1.0.0",
            "registry_name":
                "LinkCraftor Security Domain Inventory",
            "architecture_id":
                "platform-security-architecture",
            "component_id":
                "3.1.9",
            "inventory_role":
                "security-governance-projection",
            "operational_authorities": [
                "canonical-connect-domain-coordinator",
                "website-knowledge-pipeline-domain-authority",
            ],
            "domains": {},
        }

    def _load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return self._empty()

        with self.path.open(
            "r",
            encoding="utf-8-sig",
        ) as handle:
            data = json.load(handle)

        if not isinstance(
            data,
            dict,
        ):
            raise ValueError(
                "security domain inventory root "
                "must be an object"
            )

        if not isinstance(
            data.get("domains"),
            dict,
        ):
            raise ValueError(
                "security domain inventory domains "
                "must be an object"
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

        temporary.replace(
            self.path
        )

    def register(
        self,
        record: Dict[str, Any],
        *,
        replace: bool = False,
    ) -> Dict[str, Any]:

        required = {
            "security_domain_id",
            "hostname",
            "domain_type",
            "environment",
            "status",
            "source_authority",
        }

        missing = required - set(record)

        if missing:
            raise ValueError(
                "security domain missing required fields: "
                + ", ".join(sorted(missing))
            )

        security_id = str(
            record["security_domain_id"]
        ).strip().upper()

        if not security_id.startswith(
            "SEC-DOM-"
        ):
            raise ValueError(
                "security_domain_id must "
                "start with SEC-DOM-"
            )

        hostname = str(
            record["hostname"]
        ).strip().lower()

        if not hostname:
            raise ValueError(
                "hostname must not be empty"
            )

        domain_type = str(
            record["domain_type"]
        ).strip().lower()

        if domain_type not in self.ALLOWED_TYPES:
            raise ValueError(
                "invalid domain_type"
            )

        environment = str(
            record["environment"]
        ).strip().lower()

        if environment not in self.ALLOWED_ENVIRONMENTS:
            raise ValueError(
                "invalid environment"
            )

        status = str(
            record["status"]
        ).strip().lower()

        if status not in self.ALLOWED_STATUSES:
            raise ValueError(
                "invalid status"
            )

        source_authority = str(
            record["source_authority"]
        ).strip()

        if not source_authority:
            raise ValueError(
                "source_authority must not be empty"
            )

        stored = deepcopy(record)

        stored["security_domain_id"] = security_id
        stored["hostname"] = hostname
        stored["domain_type"] = domain_type
        stored["environment"] = environment
        stored["status"] = status
        stored["source_authority"] = source_authority
        stored["asset_type"] = "domain"
        stored[
            "architecture_id"
        ] = "platform-security-architecture"
        stored["component_id"] = "3.1.9"

        if "exposure" in stored:
            exposure = str(
                stored.get("exposure") or "unknown"
            ).strip().lower()

            if exposure not in self.ALLOWED_EXPOSURES:
                raise ValueError(
                    "invalid exposure"
                )

            stored["exposure"] = exposure

        now = self._now()

        with self._lock:

            existing = self._data[
                "domains"
            ].get(security_id)

            if (
                existing is not None
                and not replace
            ):
                raise ValueError(
                    "security domain already exists: "
                    + security_id
                )

            if existing is not None:
                stored[
                    "first_seen_at"
                ] = (
                    existing.get(
                        "first_seen_at"
                    )
                    or now
                )
            else:
                stored[
                    "first_seen_at"
                ] = (
                    stored.get(
                        "first_seen_at"
                    )
                    or now
                )

            stored["last_seen_at"] = now

            self._data[
                "domains"
            ][security_id] = stored

            self._save()

        return deepcopy(stored)

    def get(
        self,
        security_domain_id: str,
    ) -> Dict[str, Any]:

        normalized = str(
            security_domain_id
        ).strip().upper()

        with self._lock:

            if normalized not in (
                self._data["domains"]
            ):
                raise KeyError(
                    "security domain not found: "
                    + normalized
                )

            return deepcopy(
                self._data[
                    "domains"
                ][normalized]
            )

    def by_hostname(
        self,
        hostname: str,
    ) -> Dict[str, Any]:

        normalized = str(
            hostname
        ).strip().lower()

        with self._lock:

            matches = [
                deepcopy(record)
                for record in self._data[
                    "domains"
                ].values()
                if record.get(
                    "hostname"
                ) == normalized
            ]

        if not matches:
            raise KeyError(
                "hostname not found: "
                + normalized
            )

        if len(matches) > 1:
            raise ValueError(
                "duplicate hostname: "
                + normalized
            )

        return matches[0]

    def ingest_connected_domain(
        self,
        *,
        security_domain_id: str,
        domain: str,
        workspace_id: str,
        environment: str,
        site_url: Optional[str] = None,
        workspace_name: Optional[str] = None,
        workspace_profile_reference: Optional[str] = None,
        connection_status: Optional[str] = None,
        connected_at: Optional[str] = None,
        status: str = "active",
        domain_type: str = "domain",
    ) -> Dict[str, Any]:

        from backend.server.pipelines.connect_domain.website_knowledge_pipeline.coordinator import (
            _normalize_domain,
        )

        normalized_domain = _normalize_domain(
            domain
        )

        identity = {
            "security_domain_id":
                security_domain_id,
            "hostname":
                normalized_domain,
            "domain_type":
                domain_type,
            "environment":
                environment,
            "status":
                status,
            "source_authority":
                "canonical-connect-domain-coordinator",
            "workspace_id":
                str(workspace_id).strip(),
            "site_url":
                str(site_url or "").strip(),
            "workspace_name":
                str(workspace_name or "").strip(),
            "workspace_profile_reference":
                str(
                    workspace_profile_reference
                    or ""
                ).strip(),
            "connection_status":
                str(
                    connection_status
                    or ""
                ).strip(),
            "connected_at":
                connected_at,
            "source_type":
                "domain",
        }

        existing = None

        try:
            existing = self.by_hostname(
                normalized_domain
            )
        except KeyError:
            pass

        if existing is not None:

            identity[
                "security_domain_id"
            ] = existing[
                "security_domain_id"
            ]

            return self.register(
                {
                    **existing,
                    **identity,
                },
                replace=True,
            )

        return self.register(identity)

    def list(
        self,
        *,
        status: Optional[str] = None,
        environment: Optional[str] = None,
        domain_type: Optional[str] = None,
        source_authority: Optional[str] = None,
        exposure: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        with self._lock:
            records = deepcopy(
                list(
                    self._data[
                        "domains"
                    ].values()
                )
            )

        filters = {
            "status": status,
            "environment": environment,
            "domain_type": domain_type,
            "source_authority":
                source_authority,
            "exposure": exposure,
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
                ).strip().lower()
                == normalized
            ]

        return records

    def unauthorized_domains(
        self,
    ) -> List[Dict[str, Any]]:
        return self.list(
            status="unauthorized"
        )

    def internet_exposed_domains(
        self,
    ) -> List[Dict[str, Any]]:
        return self.list(
            exposure="internet-exposed"
        )

    def count(self) -> int:
        with self._lock:
            return len(
                self._data[
                    "domains"
                ]
            )


_default_bridge = None


def get_security_domain_inventory_bridge():
    global _default_bridge

    if _default_bridge is None:
        _default_bridge = (
            SecurityDomainInventoryBridge()
        )

    return _default_bridge
