from __future__ import annotations

import json

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class SecurityThirdPartyInventory:

    ALLOWED_TYPES = {
        "cloud-provider",
        "external-content-provider",
        "email-provider",
        "payment-provider",
        "identity-provider",
        "oauth-provider",
        "webhook-provider",
        "api-provider",
        "monitoring-provider",
        "storage-provider",
        "communications-provider",
        "analytics-provider",
        "security-provider",
        "development-platform",
        "commerce-platform",
        "cms-platform",
        "other",
    }

    ALLOWED_STATUSES = {
        "discovered",
        "approved",
        "active",
        "inactive",
        "pending-review",
        "restricted",
        "unauthorized",
        "suspended",
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

    FORBIDDEN_FIELDS = {
        "api_key",
        "apikey",
        "password",
        "secret",
        "client_secret",
        "access_token",
        "refresh_token",
        "bearer_token",
        "private_key",
        "private_key_pem",
        "webhook_secret",
        "webhook_signing_secret",
        "aws_access_key",
        "aws_secret_access_key",
        "stripe_secret_key",
        "smtp_password",
    }

    def __init__(
        self,
        path: Optional[Path] = None,
    ):
        if path is None:
            path = (
                Path(__file__).with_name("data")
                / "security_third_party_integrations.json"
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
                "LinkCraftor Security Third-Party Integration Inventory",
            "architecture_id":
                "platform-security-architecture",
            "component_id":
                "3.1.11",
            "inventory_role":
                "security-governance-projection",
            "operational_authority_policy":
                "distributed-subsystem-authorities-remain-authoritative",
            "credential_storage":
                "prohibited",
            "integrations": {},
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
                "third-party inventory root "
                "must be an object"
            )

        if not isinstance(
            data.get("integrations"),
            dict,
        ):
            raise ValueError(
                "third-party integrations "
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

    def _assert_no_secrets(
        self,
        record: Dict[str, Any],
    ) -> None:

        supplied = {
            str(key).strip().lower()
            for key in record
        }

        forbidden = (
            supplied
            & self.FORBIDDEN_FIELDS
        )

        if forbidden:

            raise ValueError(
                "third-party inventory must not "
                "store credentials or secrets: "
                + ", ".join(
                    sorted(forbidden)
                )
            )

    def register(
        self,
        record: Dict[str, Any],
        *,
        replace: bool = False,
    ) -> Dict[str, Any]:

        self._assert_no_secrets(
            record
        )

        required = {
            "security_third_party_id",
            "provider_name",
            "integration_type",
            "environment",
            "status",
            "operational_authority",
        }

        missing = (
            required
            - set(record)
        )

        if missing:

            raise ValueError(
                "third-party integration missing "
                "required fields: "
                + ", ".join(
                    sorted(missing)
                )
            )

        security_id = str(
            record[
                "security_third_party_id"
            ]
        ).strip().upper()

        if not security_id.startswith(
            "SEC-3P-"
        ):
            raise ValueError(
                "security_third_party_id must "
                "start with SEC-3P-"
            )

        provider_name = str(
            record[
                "provider_name"
            ]
        ).strip()

        if not provider_name:
            raise ValueError(
                "provider_name must not be empty"
            )

        integration_type = str(
            record[
                "integration_type"
            ]
        ).strip().lower()

        if integration_type not in (
            self.ALLOWED_TYPES
        ):
            raise ValueError(
                "invalid integration_type"
            )

        environment = str(
            record[
                "environment"
            ]
        ).strip().lower()

        if environment not in (
            self.ALLOWED_ENVIRONMENTS
        ):
            raise ValueError(
                "invalid environment"
            )

        status = str(
            record[
                "status"
            ]
        ).strip().lower()

        if status not in (
            self.ALLOWED_STATUSES
        ):
            raise ValueError(
                "invalid status"
            )

        operational_authority = str(
            record[
                "operational_authority"
            ]
        ).strip()

        if not operational_authority:
            raise ValueError(
                "operational_authority must "
                "not be empty"
            )

        stored = deepcopy(
            record
        )

        stored[
            "security_third_party_id"
        ] = security_id

        stored[
            "provider_name"
        ] = provider_name

        stored[
            "integration_type"
        ] = integration_type

        stored[
            "environment"
        ] = environment

        stored[
            "status"
        ] = status

        stored[
            "operational_authority"
        ] = operational_authority

        stored[
            "asset_type"
        ] = "third-party-integration"

        stored[
            "architecture_id"
        ] = (
            "platform-security-architecture"
        )

        stored[
            "component_id"
        ] = "3.1.11"

        now = self._now()

        with self._lock:

            existing = self._data[
                "integrations"
            ].get(
                security_id
            )

            if (
                existing is not None
                and not replace
            ):
                raise ValueError(
                    "third-party integration "
                    "already exists: "
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

            if existing is None:

                stored[
                    "first_seen_at"
                ] = (
                    stored.get(
                        "first_seen_at"
                    )
                    or now
                )

            stored[
                "last_seen_at"
            ] = now

            self._data[
                "integrations"
            ][security_id] = stored

            self._save()

        return deepcopy(
            stored
        )

    def get(
        self,
        security_third_party_id: str,
    ) -> Dict[str, Any]:

        normalized = str(
            security_third_party_id
        ).strip().upper()

        with self._lock:

            if normalized not in (
                self._data[
                    "integrations"
                ]
            ):
                raise KeyError(
                    "third-party integration "
                    "not found: "
                    + normalized
                )

            return deepcopy(
                self._data[
                    "integrations"
                ][normalized]
            )

    def by_provider_name(
        self,
        provider_name: str,
    ) -> List[Dict[str, Any]]:

        normalized = str(
            provider_name
        ).strip().lower()

        with self._lock:

            return [
                deepcopy(record)
                for record
                in self._data[
                    "integrations"
                ].values()
                if str(
                    record.get(
                        "provider_name",
                        "",
                    )
                ).strip().lower()
                == normalized
            ]

    def list(
        self,
        *,
        integration_type: Optional[str] = None,
        environment: Optional[str] = None,
        status: Optional[str] = None,
        subsystem: Optional[str] = None,
        operational_authority: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        with self._lock:

            records = deepcopy(
                list(
                    self._data[
                        "integrations"
                    ].values()
                )
            )

        filters = {
            "integration_type":
                integration_type,
            "environment":
                environment,
            "status":
                status,
            "subsystem":
                subsystem,
            "operational_authority":
                operational_authority,
        }

        for field, value in (
            filters.items()
        ):

            if value is None:
                continue

            normalized = str(
                value
            ).strip().lower()

            records = [
                record
                for record
                in records
                if str(
                    record.get(
                        field,
                        "",
                    )
                ).strip().lower()
                == normalized
            ]

        return records

    def unauthorized_integrations(
        self,
    ) -> List[Dict[str, Any]]:

        return self.list(
            status="unauthorized"
        )

    def production_integrations(
        self,
    ) -> List[Dict[str, Any]]:

        return self.list(
            environment="production"
        )

    def internet_dependencies(
        self,
    ) -> List[Dict[str, Any]]:

        with self._lock:

            return [
                deepcopy(record)
                for record
                in self._data[
                    "integrations"
                ].values()
                if record.get(
                    "internet_dependency"
                ) is True
            ]

    def count(self) -> int:

        with self._lock:

            return len(
                self._data[
                    "integrations"
                ]
            )


_default_inventory = None


def get_security_third_party_inventory():
    global _default_inventory

    if _default_inventory is None:

        _default_inventory = (
            SecurityThirdPartyInventory()
        )

    return _default_inventory
