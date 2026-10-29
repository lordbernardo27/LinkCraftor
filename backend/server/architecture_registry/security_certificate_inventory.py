from __future__ import annotations

import json

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class SecurityCertificateInventory:

    ALLOWED_TYPES = {
        "tls-server",
        "tls-client",
        "mutual-tls",
        "code-signing",
        "email",
        "intermediate-ca",
        "root-ca",
        "internal-service",
        "wildcard",
        "other",
    }

    ALLOWED_STATUSES = {
        "discovered",
        "active",
        "pending",
        "expiring",
        "expired",
        "revoked",
        "invalid",
        "unauthorized",
        "quarantined",
        "superseded",
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
        "private_key",
        "private_key_pem",
        "private_key_material",
        "pkcs12_private_key",
        "passphrase",
        "password",
        "acme_account_private_key",
        "certificate_management_secret",
        "hsm_secret",
        "tls_session_secret",
    }

    def __init__(
        self,
        path: Optional[Path] = None,
    ):
        if path is None:
            path = (
                Path(__file__).with_name("data")
                / "security_certificates.json"
            )

        self.path = Path(path)
        self._lock = RLock()
        self._data = self._load()

    @staticmethod
    def _now() -> str:
        return datetime.now(
            timezone.utc
        ).isoformat()

    @staticmethod
    def _parse_time(
        value: Optional[str],
    ) -> Optional[datetime]:

        if value is None:
            return None

        text = str(value).strip()

        if not text:
            return None

        if text.endswith("Z"):
            text = text[:-1] + "+00:00"

        parsed = datetime.fromisoformat(
            text
        )

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed.astimezone(
            timezone.utc
        )

    def _empty(self) -> Dict[str, Any]:
        return {
            "schema_version": "1.0.0",
            "registry_name":
                "LinkCraftor Security Certificate Inventory",
            "architecture_id":
                "platform-security-architecture",
            "component_id":
                "3.1.10",
            "inventory_role":
                "security-governance-inventory",
            "certificate_lifecycle_authority":
                "external-or-future-certificate-management-authority",
            "private_key_storage":
                "prohibited",
            "certificates": {},
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
                "security certificate inventory "
                "root must be an object"
            )

        if not isinstance(
            data.get("certificates"),
            dict,
        ):
            raise ValueError(
                "security certificate inventory "
                "certificates must be an object"
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

    def _assert_no_private_material(
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
                "certificate inventory must not "
                "store private material: "
                + ", ".join(
                    sorted(forbidden)
                )
            )

    def _decorate_expiry(
        self,
        record: Dict[str, Any],
    ) -> Dict[str, Any]:

        decorated = deepcopy(record)

        not_after = self._parse_time(
            decorated.get(
                "not_after"
            )
        )

        if not_after is None:
            decorated[
                "days_until_expiry"
            ] = None

            decorated[
                "expiry_state"
            ] = "unknown"

            return decorated

        now = datetime.now(
            timezone.utc
        )

        delta = (
            not_after - now
        )

        days = int(
            delta.total_seconds()
            // 86400
        )

        decorated[
            "days_until_expiry"
        ] = days

        if not_after <= now:
            state = "expired"

        elif days <= 30:
            state = "expiring"

        else:
            state = "valid"

        decorated[
            "expiry_state"
        ] = state

        return decorated

    def register(
        self,
        record: Dict[str, Any],
        *,
        replace: bool = False,
    ) -> Dict[str, Any]:

        self._assert_no_private_material(
            record
        )

        required = {
            "security_certificate_id",
            "certificate_type",
            "subject",
            "environment",
            "status",
            "source_authority",
        }

        missing = (
            required
            - set(record)
        )

        if missing:
            raise ValueError(
                "security certificate missing "
                "required fields: "
                + ", ".join(
                    sorted(missing)
                )
            )

        security_id = str(
            record[
                "security_certificate_id"
            ]
        ).strip().upper()

        if not security_id.startswith(
            "SEC-CERT-"
        ):
            raise ValueError(
                "security_certificate_id must "
                "start with SEC-CERT-"
            )

        certificate_type = str(
            record[
                "certificate_type"
            ]
        ).strip().lower()

        if certificate_type not in (
            self.ALLOWED_TYPES
        ):
            raise ValueError(
                "invalid certificate_type"
            )

        subject = str(
            record["subject"]
        ).strip()

        if not subject:
            raise ValueError(
                "subject must not be empty"
            )

        environment = str(
            record["environment"]
        ).strip().lower()

        if environment not in (
            self.ALLOWED_ENVIRONMENTS
        ):
            raise ValueError(
                "invalid environment"
            )

        status = str(
            record["status"]
        ).strip().lower()

        if status not in (
            self.ALLOWED_STATUSES
        ):
            raise ValueError(
                "invalid status"
            )

        source_authority = str(
            record[
                "source_authority"
            ]
        ).strip()

        if not source_authority:
            raise ValueError(
                "source_authority must not be empty"
            )

        stored = deepcopy(
            record
        )

        stored[
            "security_certificate_id"
        ] = security_id

        stored[
            "certificate_type"
        ] = certificate_type

        stored[
            "subject"
        ] = subject

        stored[
            "environment"
        ] = environment

        stored[
            "status"
        ] = status

        stored[
            "source_authority"
        ] = source_authority

        stored[
            "asset_type"
        ] = "certificate"

        stored[
            "architecture_id"
        ] = (
            "platform-security-architecture"
        )

        stored[
            "component_id"
        ] = "3.1.10"

        stored = self._decorate_expiry(
            stored
        )

        now = self._now()

        with self._lock:

            existing = self._data[
                "certificates"
            ].get(
                security_id
            )

            if (
                existing is not None
                and not replace
            ):
                raise ValueError(
                    "security certificate "
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
                "certificates"
            ][security_id] = stored

            self._save()

        return deepcopy(
            stored
        )

    def get(
        self,
        security_certificate_id: str,
    ) -> Dict[str, Any]:

        normalized = str(
            security_certificate_id
        ).strip().upper()

        with self._lock:

            if normalized not in (
                self._data[
                    "certificates"
                ]
            ):
                raise KeyError(
                    "security certificate "
                    "not found: "
                    + normalized
                )

            return deepcopy(
                self._data[
                    "certificates"
                ][normalized]
            )

    def by_fingerprint(
        self,
        fingerprint: str,
    ) -> Dict[str, Any]:

        normalized = str(
            fingerprint
        ).strip().lower()

        with self._lock:

            matches = [
                deepcopy(record)
                for record
                in self._data[
                    "certificates"
                ].values()
                if str(
                    record.get(
                        "fingerprint",
                        "",
                    )
                ).strip().lower()
                == normalized
            ]

        if not matches:
            raise KeyError(
                "certificate fingerprint "
                "not found"
            )

        if len(matches) > 1:
            raise ValueError(
                "duplicate certificate "
                "fingerprint"
            )

        return matches[0]

    def list(
        self,
        *,
        status: Optional[str] = None,
        environment: Optional[str] = None,
        certificate_type: Optional[str] = None,
        source_authority: Optional[str] = None,
        expiry_state: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        with self._lock:

            records = deepcopy(
                list(
                    self._data[
                        "certificates"
                    ].values()
                )
            )

        filters = {
            "status":
                status,
            "environment":
                environment,
            "certificate_type":
                certificate_type,
            "source_authority":
                source_authority,
            "expiry_state":
                expiry_state,
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

    def expired_certificates(
        self,
    ) -> List[Dict[str, Any]]:

        return self.list(
            expiry_state="expired"
        )

    def expiring_certificates(
        self,
    ) -> List[Dict[str, Any]]:

        return self.list(
            expiry_state="expiring"
        )

    def unauthorized_certificates(
        self,
    ) -> List[Dict[str, Any]]:

        return self.list(
            status="unauthorized"
        )

    def count(self) -> int:

        with self._lock:

            return len(
                self._data[
                    "certificates"
                ]
            )


_default_inventory = None


def get_security_certificate_inventory():
    global _default_inventory

    if _default_inventory is None:
        _default_inventory = (
            SecurityCertificateInventory()
        )

    return _default_inventory
