from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class SecurityIdentityInventoryBridge:

    RUNTIME_PRINCIPAL_TYPE_MAP = {
        "USER": "user",
        "WORKER": "worker",
        "SERVICE": "service",
        "SYSTEM": "system",
        "ADMINISTRATOR": "administrator",
    }

    ALLOWED_IDENTITY_TYPES = {
        "user",
        "worker",
        "service",
        "system",
        "administrator",
        "staff",
        "integration",
        "automation",
        "machine",
        "external",
        "other",
    }

    ALLOWED_STATUSES = {
        "discovered",
        "active",
        "inactive",
        "disabled",
        "suspended",
        "stale",
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

    FORBIDDEN_FIELDS = {
        "password",
        "password_hash",
        "api_key",
        "api_secret",
        "access_token",
        "refresh_token",
        "bearer_token",
        "private_key",
        "mfa_secret",
        "recovery_code",
        "session_token",
        "session_secret",
    }

    def __init__(
        self,
        path: Optional[Path] = None,
    ):
        if path is None:
            path = (
                Path(__file__).with_name("data")
                / "security_identities.json"
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
                "LinkCraftor Security Identity Inventory",
            "architecture_id":
                "platform-security-architecture",
            "component_id":
                "3.1.8",
            "inventory_role":
                "security-governance-projection",
            "runtime_principal_types": [
                "USER",
                "WORKER",
                "SERVICE",
                "SYSTEM",
                "ADMINISTRATOR",
            ],
            "operational_authorities": [
                "runtime-authentication-boundaries",
                "existing-user-account-authorities",
                "existing-worker-authority",
                "existing-service-authorities",
                "existing-system-authorities",
            ],
            "identities": {},
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
                "security identity inventory "
                "root must be an object"
            )

        if not isinstance(
            data.get("identities"),
            dict,
        ):
            raise ValueError(
                "security identity inventory "
                "identities must be an object"
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
        identity: Dict[str, Any],
    ) -> None:

        found = {
            str(key).strip().lower()
            for key in identity
            if str(key).strip().lower()
            in self.FORBIDDEN_FIELDS
        }

        if found:
            raise ValueError(
                "security identity inventory "
                "must not store credentials: "
                + ", ".join(
                    sorted(found)
                )
            )

    def register(
        self,
        identity: Dict[str, Any],
        *,
        replace: bool = False,
    ) -> Dict[str, Any]:

        self._assert_no_secrets(
            identity
        )

        required = {
            "security_identity_id",
            "identity_key",
            "identity_name",
            "identity_type",
            "source_authority",
            "environment",
            "status",
            "human_identity",
            "privileged",
        }

        missing = required - set(
            identity
        )

        if missing:
            raise ValueError(
                "security identity missing "
                "required fields: "
                + ", ".join(
                    sorted(missing)
                )
            )

        security_id = str(
            identity[
                "security_identity_id"
            ]
        ).strip().upper()

        if not security_id.startswith(
            "SEC-ID-"
        ):
            raise ValueError(
                "security_identity_id must "
                "start with SEC-ID-"
            )

        identity_key = str(
            identity["identity_key"]
        ).strip()

        if not identity_key:
            raise ValueError(
                "identity_key must not be empty"
            )

        identity_name = str(
            identity["identity_name"]
        ).strip()

        if not identity_name:
            raise ValueError(
                "identity_name must not be empty"
            )

        identity_type = str(
            identity["identity_type"]
        ).strip().lower()

        if identity_type not in (
            self.ALLOWED_IDENTITY_TYPES
        ):
            raise ValueError(
                "invalid identity_type"
            )

        source_authority = str(
            identity["source_authority"]
        ).strip()

        if not source_authority:
            raise ValueError(
                "source_authority must not be empty"
            )

        environment = str(
            identity["environment"]
        ).strip().lower()

        if environment not in (
            self.ALLOWED_ENVIRONMENTS
        ):
            raise ValueError(
                "invalid identity environment"
            )

        status = str(
            identity["status"]
        ).strip().lower()

        if status not in (
            self.ALLOWED_STATUSES
        ):
            raise ValueError(
                "invalid identity status"
            )

        if not isinstance(
            identity["human_identity"],
            bool,
        ):
            raise ValueError(
                "human_identity must be boolean"
            )

        if not isinstance(
            identity["privileged"],
            bool,
        ):
            raise ValueError(
                "privileged must be boolean"
            )

        now = self._now()

        stored = deepcopy(
            identity
        )

        stored[
            "security_identity_id"
        ] = security_id

        stored[
            "identity_key"
        ] = identity_key

        stored[
            "identity_name"
        ] = identity_name

        stored[
            "identity_type"
        ] = identity_type

        stored[
            "source_authority"
        ] = source_authority

        stored[
            "environment"
        ] = environment

        stored[
            "status"
        ] = status

        stored[
            "asset_type"
        ] = "identity"

        stored[
            "architecture_id"
        ] = (
            "platform-security-architecture"
        )

        stored[
            "component_id"
        ] = "3.1.8"

        with self._lock:

            existing = self._data[
                "identities"
            ].get(
                security_id
            )

            if (
                existing is not None
                and not replace
            ):
                raise ValueError(
                    "security identity already exists: "
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

            stored[
                "last_seen_at"
            ] = now

            self._data[
                "identities"
            ][security_id] = stored

            self._save()

        return deepcopy(
            stored
        )

    def get(
        self,
        security_identity_id: str,
    ) -> Dict[str, Any]:

        normalized = str(
            security_identity_id
        ).strip().upper()

        with self._lock:

            if normalized not in (
                self._data[
                    "identities"
                ]
            ):
                raise KeyError(
                    "security identity not found: "
                    + normalized
                )

            return deepcopy(
                self._data[
                    "identities"
                ][normalized]
            )

    def by_identity_key(
        self,
        identity_key: str,
    ) -> Dict[str, Any]:

        normalized = str(
            identity_key
        ).strip()

        with self._lock:

            matches = [
                deepcopy(record)
                for record in self._data[
                    "identities"
                ].values()
                if record.get(
                    "identity_key"
                ) == normalized
            ]

        if not matches:
            raise KeyError(
                "identity key not found: "
                + normalized
            )

        if len(matches) > 1:
            raise ValueError(
                "duplicate identity key: "
                + normalized
            )

        return matches[0]

    def ingest_runtime_principal(
        self,
        principal: Any,
        *,
        security_identity_id: str,
        source_authority: str,
        environment: str,
        status: str = "active",
        privileged: Optional[bool] = None,
    ) -> Dict[str, Any]:

        principal_type_value = getattr(
            getattr(
                principal,
                "principal_type",
                None,
            ),
            "value",
            None,
        )

        if principal_type_value is None:
            principal_type_value = str(
                getattr(
                    principal,
                    "principal_type",
                    "",
                )
            )

        principal_type_value = str(
            principal_type_value
        ).strip().upper()

        if principal_type_value not in (
            self.RUNTIME_PRINCIPAL_TYPE_MAP
        ):
            raise ValueError(
                "unsupported runtime principal type: "
                + principal_type_value
            )

        principal_id = str(
            getattr(
                principal,
                "principal_id",
                "",
            )
        ).strip()

        if not principal_id:
            raise ValueError(
                "runtime principal_id is required"
            )

        identity_type = (
            self.RUNTIME_PRINCIPAL_TYPE_MAP[
                principal_type_value
            ]
        )

        human_identity = (
            identity_type
            in {
                "user",
                "administrator",
            }
        )

        if privileged is None:
            privileged = (
                identity_type
                == "administrator"
            )

        identity = {
            "security_identity_id":
                security_identity_id,
            "identity_key":
                "runtime-principal:"
                + principal_type_value
                + ":"
                + principal_id,
            "identity_name":
                principal_id,
            "identity_type":
                identity_type,
            "source_authority":
                source_authority,
            "environment":
                environment,
            "status":
                status,
            "human_identity":
                human_identity,
            "privileged":
                bool(privileged),
            "authoritative_identity_id":
                principal_id,
            "principal_type":
                principal_type_value,
        }

        worker_id = getattr(
            principal,
            "worker_id",
            None,
        )

        worker_instance_id = getattr(
            principal,
            "worker_instance_id",
            None,
        )

        service_name = getattr(
            principal,
            "service_name",
            None,
        )

        if worker_id:
            identity[
                "worker_id"
            ] = str(worker_id)

        if worker_instance_id:
            identity[
                "worker_instance_id"
            ] = str(
                worker_instance_id
            )

        if service_name:
            identity[
                "service_name"
            ] = str(service_name)

        existing = None

        try:
            existing = self.by_identity_key(
                identity[
                    "identity_key"
                ]
            )
        except KeyError:
            pass

        if existing is not None:

            identity[
                "security_identity_id"
            ] = existing[
                "security_identity_id"
            ]

            return self.register(
                {
                    **existing,
                    **identity,
                },
                replace=True,
            )

        return self.register(
            identity
        )

    def list(
        self,
        *,
        status: Optional[str] = None,
        environment: Optional[str] = None,
        identity_type: Optional[str] = None,
        source_authority: Optional[str] = None,
        human_identity: Optional[bool] = None,
        privileged: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:

        with self._lock:
            records = deepcopy(
                list(
                    self._data[
                        "identities"
                    ].values()
                )
            )

        text_filters = {
            "status": status,
            "environment": environment,
            "identity_type":
                identity_type,
            "source_authority":
                source_authority,
        }

        for field, value in (
            text_filters.items()
        ):
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

        if human_identity is not None:
            records = [
                record
                for record in records
                if record.get(
                    "human_identity"
                ) is human_identity
            ]

        if privileged is not None:
            records = [
                record
                for record in records
                if record.get(
                    "privileged"
                ) is privileged
            ]

        return records

    def privileged_identities(
        self,
    ) -> List[Dict[str, Any]]:
        return self.list(
            privileged=True
        )

    def unauthorized_identities(
        self,
    ) -> List[Dict[str, Any]]:
        return self.list(
            status="unauthorized"
        )

    def stale_identities(
        self,
    ) -> List[Dict[str, Any]]:
        return self.list(
            status="stale"
        )

    def human_identities(
        self,
    ) -> List[Dict[str, Any]]:
        return self.list(
            human_identity=True
        )

    def non_human_identities(
        self,
    ) -> List[Dict[str, Any]]:
        return self.list(
            human_identity=False
        )

    def count(self) -> int:
        with self._lock:
            return len(
                self._data[
                    "identities"
                ]
            )


_default_bridge = None


def get_security_identity_inventory_bridge():
    global _default_bridge

    if _default_bridge is None:
        _default_bridge = (
            SecurityIdentityInventoryBridge()
        )

    return _default_bridge
