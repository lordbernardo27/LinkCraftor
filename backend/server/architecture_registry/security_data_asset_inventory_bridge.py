from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class SecurityDataAssetInventoryBridge:
    ALLOWED_KINDS = {
        "runtime-state-store",
        "persistence-backend",
        "semantic-context-store",
        "semantic-memory-store",
        "document-content-store",
        "unified-content-store",
        "dataset",
        "database",
        "cache",
        "object-store",
        "file-store",
        "index",
        "queue-data-store",
        "audit-data-store",
        "workspace-data-store",
        "data-domain",
        "data-schema",
        "data-lineage-record",
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

    UDA_REFERENCE_FIELDS = {
        "uda_asset_id",
        "uda_domain_id",
        "uda_dataset_id",
        "uda_schema_id",
        "uda_lineage_id",
    }

    def __init__(
        self,
        path: Optional[Path] = None,
    ):
        if path is None:
            path = (
                Path(__file__).with_name("data")
                / "security_data_assets.json"
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
                "LinkCraftor Security Data Asset Inventory",
            "architecture_id":
                "platform-security-architecture",
            "component_id":
                "3.1.7",
            "inventory_role":
                "security-governance-projection",
            "future_uda_compatible": True,
            "operational_authorities": [
                "backend/server/runtime/"
                "runtime_state_store.py",
                "backend/server/runtime/"
                "runtime_persistence.py",
            ],
            "future_authorities": [
                "universal-data-architecture",
            ],
            "data_assets": {},
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
                "security data asset inventory "
                "root must be an object"
            )

        if not isinstance(
            data.get("data_assets"),
            dict,
        ):
            raise ValueError(
                "security data asset inventory "
                "data_assets must be an object"
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

    @staticmethod
    def _normalize_optional(
        value: Any,
    ) -> Optional[str]:
        if value is None:
            return None

        normalized = str(
            value
        ).strip()

        if not normalized:
            return None

        return normalized

    def register(
        self,
        asset: Dict[str, Any],
        *,
        replace: bool = False,
    ) -> Dict[str, Any]:

        required = {
            "security_data_asset_id",
            "asset_key",
            "asset_name",
            "asset_kind",
            "environment",
            "status",
            "source",
            "source_authority",
        }

        missing = required - set(
            asset
        )

        if missing:
            raise ValueError(
                "security data asset missing "
                "required fields: "
                + ", ".join(
                    sorted(missing)
                )
            )

        security_id = str(
            asset[
                "security_data_asset_id"
            ]
        ).strip().upper()

        if not security_id.startswith(
            "SEC-DATA-"
        ):
            raise ValueError(
                "security_data_asset_id "
                "must start with SEC-DATA-"
            )

        asset_key = str(
            asset["asset_key"]
        ).strip()

        if not asset_key:
            raise ValueError(
                "asset_key must not be empty"
            )

        asset_name = str(
            asset["asset_name"]
        ).strip()

        if not asset_name:
            raise ValueError(
                "asset_name must not be empty"
            )

        asset_kind = str(
            asset["asset_kind"]
        ).strip().lower()

        if asset_kind not in self.ALLOWED_KINDS:
            raise ValueError(
                "invalid data asset kind"
            )

        environment = str(
            asset["environment"]
        ).strip().lower()

        if environment not in (
            self.ALLOWED_ENVIRONMENTS
        ):
            raise ValueError(
                "invalid data asset environment"
            )

        status = str(
            asset["status"]
        ).strip().lower()

        if status not in (
            self.ALLOWED_STATUSES
        ):
            raise ValueError(
                "invalid data asset status"
            )

        source = str(
            asset["source"]
        ).strip()

        if not source:
            raise ValueError(
                "data asset source "
                "must not be empty"
            )

        source_authority = str(
            asset["source_authority"]
        ).strip()

        if not source_authority:
            raise ValueError(
                "source_authority "
                "must not be empty"
            )

        now = self._now()

        stored = deepcopy(
            asset
        )

        stored[
            "security_data_asset_id"
        ] = security_id

        stored[
            "asset_key"
        ] = asset_key

        stored[
            "asset_name"
        ] = asset_name

        stored[
            "asset_kind"
        ] = asset_kind

        stored[
            "environment"
        ] = environment

        stored[
            "status"
        ] = status

        stored[
            "source"
        ] = source

        stored[
            "source_authority"
        ] = source_authority

        stored[
            "asset_type"
        ] = "data"

        stored[
            "architecture_id"
        ] = (
            "platform-security-architecture"
        )

        stored[
            "component_id"
        ] = "3.1.7"

        for field in (
            self.UDA_REFERENCE_FIELDS
        ):
            if field in stored:
                stored[field] = (
                    self._normalize_optional(
                        stored[field]
                    )
                )

        with self._lock:
            existing = self._data[
                "data_assets"
            ].get(
                security_id
            )

            if (
                existing is not None
                and not replace
            ):
                raise ValueError(
                    "security data asset "
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
                "data_assets"
            ][security_id] = stored

            self._save()

        return deepcopy(
            stored
        )

    def get(
        self,
        security_data_asset_id: str,
    ) -> Dict[str, Any]:

        security_id = (
            security_data_asset_id
            .strip()
            .upper()
        )

        with self._lock:
            if security_id not in (
                self._data[
                    "data_assets"
                ]
            ):
                raise KeyError(
                    "security data asset "
                    "not found: "
                    + security_id
                )

            return deepcopy(
                self._data[
                    "data_assets"
                ][security_id]
            )

    def by_asset_key(
        self,
        asset_key: str,
    ) -> Dict[str, Any]:

        normalized = str(
            asset_key
        ).strip()

        with self._lock:
            matches = [
                deepcopy(
                    record
                )
                for record in (
                    self._data[
                        "data_assets"
                    ].values()
                )
                if record.get(
                    "asset_key"
                ) == normalized
            ]

        if not matches:
            raise KeyError(
                "data asset key not found: "
                + normalized
            )

        if len(matches) > 1:
            raise ValueError(
                "duplicate data asset key: "
                + normalized
            )

        return matches[0]

    def ingest_state_store_snapshot(
        self,
        snapshot: Any,
        *,
        environment: str,
        id_map: Dict[str, str],
    ) -> List[Dict[str, Any]]:

        store_ids = tuple(
            getattr(
                snapshot,
                "store_ids",
                (),
            )
        )

        domains = tuple(
            getattr(
                snapshot,
                "domains",
                (),
            )
        )

        if len(
            store_ids
        ) != len(
            domains
        ):
            raise ValueError(
                "state-store snapshot "
                "store_ids and domains "
                "lengths differ"
            )

        ingested = []

        for store_id, domain in zip(
            store_ids,
            domains,
        ):
            asset_key = (
                "runtime-state-store:"
                + str(store_id)
            )

            security_id = id_map.get(
                asset_key
            )

            if not security_id:
                raise ValueError(
                    "missing security ID "
                    "mapping for "
                    + asset_key
                )

            record = {
                "security_data_asset_id":
                    security_id,
                "asset_key":
                    asset_key,
                "asset_name":
                    str(store_id),
                "asset_kind":
                    "runtime-state-store",
                "environment":
                    environment,
                "status":
                    "active",
                "source":
                    "universal-runtime",
                "source_authority":
                    "runtime-state-store-registry",
                "logical_domain":
                    str(domain),
                "source_generation":
                    getattr(
                        snapshot,
                        "generation",
                        None,
                    ),
                "source_fingerprint":
                    getattr(
                        snapshot,
                        "fingerprint",
                        None,
                    ),
            }

            existing = None

            try:
                existing = (
                    self.by_asset_key(
                        asset_key
                    )
                )
            except KeyError:
                pass

            if existing is not None:
                record[
                    "security_data_asset_id"
                ] = existing[
                    "security_data_asset_id"
                ]

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

    def ingest_persistence_snapshot(
        self,
        snapshot: Any,
        *,
        environment: str,
        id_map: Dict[str, str],
    ) -> List[Dict[str, Any]]:

        backend_ids = tuple(
            getattr(
                snapshot,
                "backend_ids",
                (),
            )
        )

        active_backend_id = getattr(
            snapshot,
            "active_backend_id",
            None,
        )

        ingested = []

        for backend_id in backend_ids:
            asset_key = (
                "runtime-persistence-backend:"
                + str(backend_id)
            )

            security_id = id_map.get(
                asset_key
            )

            if not security_id:
                raise ValueError(
                    "missing security ID "
                    "mapping for "
                    + asset_key
                )

            record = {
                "security_data_asset_id":
                    security_id,
                "asset_key":
                    asset_key,
                "asset_name":
                    str(backend_id),
                "asset_kind":
                    "persistence-backend",
                "environment":
                    environment,
                "status":
                    "active",
                "source":
                    "universal-runtime",
                "source_authority":
                    "runtime-persistence-registry",
                "backend_id":
                    str(backend_id),
                "active_backend":
                    (
                        str(backend_id)
                        == str(
                            active_backend_id
                        )
                    ),
                "source_generation":
                    getattr(
                        snapshot,
                        "generation",
                        None,
                    ),
                "source_fingerprint":
                    getattr(
                        snapshot,
                        "fingerprint",
                        None,
                    ),
            }

            existing = None

            try:
                existing = (
                    self.by_asset_key(
                        asset_key
                    )
                )
            except KeyError:
                pass

            if existing is not None:
                record[
                    "security_data_asset_id"
                ] = existing[
                    "security_data_asset_id"
                ]

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

    def ingest_uda_asset(
        self,
        asset: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Future UDA compatibility adapter.

        This method accepts metadata only.
        It does not create or mutate UDA records.
        """

        required = {
            "security_data_asset_id",
            "asset_key",
            "asset_name",
            "asset_kind",
            "environment",
            "status",
            "uda_asset_id",
        }

        missing = required - set(
            asset
        )

        if missing:
            raise ValueError(
                "UDA security projection "
                "missing required fields: "
                + ", ".join(
                    sorted(missing)
                )
            )

        projected = deepcopy(
            asset
        )

        projected[
            "source"
        ] = "universal-data-architecture"

        projected[
            "source_authority"
        ] = "universal-data-architecture"

        existing = None

        try:
            existing = self.by_asset_key(
                projected[
                    "asset_key"
                ]
            )
        except KeyError:
            pass

        if existing is not None:
            projected[
                "security_data_asset_id"
            ] = existing[
                "security_data_asset_id"
            ]

            return self.register(
                {
                    **existing,
                    **projected,
                },
                replace=True,
            )

        return self.register(
            projected
        )

    def list(
        self,
        *,
        status: Optional[str] = None,
        environment: Optional[str] = None,
        asset_kind: Optional[str] = None,
        source_authority: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        with self._lock:
            records = deepcopy(
                list(
                    self._data[
                        "data_assets"
                    ].values()
                )
            )

        filters = {
            "status": status,
            "environment": environment,
            "asset_kind": asset_kind,
            "source_authority":
                source_authority,
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

    def unauthorized_assets(
        self,
    ) -> List[Dict[str, Any]]:
        return self.list(
            status="unauthorized"
        )

    def uda_linked_assets(
        self,
    ) -> List[Dict[str, Any]]:
        with self._lock:
            return [
                deepcopy(record)
                for record in self._data[
                    "data_assets"
                ].values()
                if record.get(
                    "uda_asset_id"
                )
            ]

    def count(self) -> int:
        with self._lock:
            return len(
                self._data[
                    "data_assets"
                ]
            )


_default_bridge = None


def get_security_data_asset_inventory_bridge():
    global _default_bridge

    if _default_bridge is None:
        _default_bridge = (
            SecurityDataAssetInventoryBridge()
        )

    return _default_bridge
