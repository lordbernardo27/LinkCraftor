from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class SecurityADRRegistry:
    """
    Canonical operational registry for LinkCraftor Security Architecture
    Decision Records.
    """

    ALLOWED_STATUSES = {
        "proposed",
        "accepted",
        "rejected",
        "superseded",
        "deprecated",
    }

    def __init__(self, path: Optional[Path] = None):
        if path is None:
            path = Path(__file__).with_name("data") / "security_adrs.json"

        self.path = Path(path)
        self._lock = RLock()
        self._data = self._load()

    def _empty(self):
        return {
            "schema_version": "1.0.0",
            "registry_name": "LinkCraftor Security ADR Registry",
            "records": {},
        }

    def _load(self):
        if not self.path.exists():
            return self._empty()

        with self.path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)

        if not isinstance(data.get("records"), dict):
            raise ValueError("Security ADR registry records must be an object")

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
            "adr_id",
            "title",
            "status",
            "architecture_id",
            "decision",
            "owner",
        }

        missing = required - set(record)

        if missing:
            raise ValueError(
                "Security ADR missing fields: "
                + ", ".join(sorted(missing))
            )

        adr_id = record["adr_id"].strip().upper()

        if not adr_id.startswith("SEC-ADR-"):
            raise ValueError("Security ADR ID must start with SEC-ADR-")

        status = record["status"].strip().lower()

        if status not in self.ALLOWED_STATUSES:
            raise ValueError("Invalid Security ADR status")

        stored = deepcopy(record)
        stored["adr_id"] = adr_id
        stored["status"] = status

        with self._lock:
            if adr_id in self._data["records"]:
                raise ValueError(f"Security ADR already exists: {adr_id}")

            self._data["records"][adr_id] = stored
            self._save()

        return deepcopy(stored)

    def get(self, adr_id: str) -> Dict[str, Any]:
        adr_id = adr_id.strip().upper()

        with self._lock:
            if adr_id not in self._data["records"]:
                raise KeyError(f"Security ADR not found: {adr_id}")

            return deepcopy(self._data["records"][adr_id])

    def list(self) -> List[Dict[str, Any]]:
        with self._lock:
            return deepcopy(list(self._data["records"].values()))


_default_registry = None


def get_security_adr_registry():
    global _default_registry

    if _default_registry is None:
        _default_registry = SecurityADRRegistry()

    return _default_registry
