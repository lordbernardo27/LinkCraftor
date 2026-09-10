from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class SecurityExceptionRegistry:
    """
    Canonical operational registry for LinkCraftor security exceptions.

    Exceptions are explicit, traceable, time-bound governance records.
    """

    ALLOWED_STATUSES = {
        "requested",
        "under-review",
        "approved",
        "rejected",
        "expired",
        "revoked",
        "closed",
    }

    def __init__(self, path: Optional[Path] = None):
        if path is None:
            path = Path(__file__).with_name("data") / "security_exceptions.json"

        self.path = Path(path)
        self._lock = RLock()
        self._data = self._load()

    def _empty(self):
        return {
            "schema_version": "1.0.0",
            "registry_name": "LinkCraftor Security Exception Registry",
            "exceptions": {},
        }

    def _load(self):
        if not self.path.exists():
            return self._empty()

        with self.path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)

        if not isinstance(data.get("exceptions"), dict):
            raise ValueError("exceptions must be a JSON object")

        return data

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)

        temp = self.path.with_suffix(self.path.suffix + ".tmp")

        with temp.open("w", encoding="utf-8") as handle:
            json.dump(
                self._data,
                handle,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )
            handle.write("\n")

        temp.replace(self.path)

    def register(self, record: Dict[str, Any]) -> Dict[str, Any]:
        required = {
            "exception_id",
            "title",
            "architecture_id",
            "control_id",
            "reason",
            "risk_owner",
            "status",
            "expires_at",
            "compensating_controls",
        }

        missing = required - set(record)

        if missing:
            raise ValueError(
                "Security exception missing fields: "
                + ", ".join(sorted(missing))
            )

        exception_id = record["exception_id"].strip().upper()

        if not exception_id.startswith("SEC-EXC-"):
            raise ValueError(
                "Security exception ID must start with SEC-EXC-"
            )

        status = record["status"].strip().lower()

        if status not in self.ALLOWED_STATUSES:
            raise ValueError("Invalid security exception status")

        self._parse_datetime(record["expires_at"])

        stored = deepcopy(record)
        stored["exception_id"] = exception_id
        stored["status"] = status

        with self._lock:
            if exception_id in self._data["exceptions"]:
                raise ValueError(
                    f"Security exception already exists: {exception_id}"
                )

            self._data["exceptions"][exception_id] = stored
            self._save()

        return deepcopy(stored)

    def get(self, exception_id: str) -> Dict[str, Any]:
        exception_id = exception_id.strip().upper()

        with self._lock:
            if exception_id not in self._data["exceptions"]:
                raise KeyError(
                    f"Security exception not found: {exception_id}"
                )

            return deepcopy(
                self._data["exceptions"][exception_id]
            )

    def list(self) -> List[Dict[str, Any]]:
        with self._lock:
            return deepcopy(
                list(self._data["exceptions"].values())
            )

    def expired(self) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        results = []

        for record in self.list():
            if record["status"] not in {"approved", "under-review"}:
                continue

            expiry = self._parse_datetime(record["expires_at"])

            if expiry <= now:
                results.append(record)

        return results

    @staticmethod
    def _parse_datetime(value: str) -> datetime:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("expires_at must be a non-empty ISO timestamp")

        normalized = value.strip().replace("Z", "+00:00")

        parsed = datetime.fromisoformat(normalized)

        if parsed.tzinfo is None:
            raise ValueError(
                "expires_at must include timezone information"
            )

        return parsed.astimezone(timezone.utc)


_default_registry = None


def get_security_exception_registry():
    global _default_registry

    if _default_registry is None:
        _default_registry = SecurityExceptionRegistry()

    return _default_registry
