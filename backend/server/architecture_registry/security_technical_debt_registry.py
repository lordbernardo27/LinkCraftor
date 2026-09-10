from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class SecurityTechnicalDebtRegistry:
    ALLOWED_STATUSES = {
        "identified",
        "planned",
        "in-progress",
        "accepted",
        "resolved",
        "closed",
        "reopened",
    }

    def __init__(self, path: Optional[Path] = None):
        if path is None:
            path = Path(__file__).with_name("data") / "security_technical_debt.json"

        self.path = Path(path)
        self._lock = RLock()
        self._data = self._load()

    def _empty(self):
        return {
            "schema_version": "1.0.0",
            "registry_name": "LinkCraftor Security Technical Debt Registry",
            "records": {},
        }

    def _load(self):
        if not self.path.exists():
            return self._empty()

        with self.path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)

        if not isinstance(data.get("records"), dict):
            raise ValueError("technical debt records must be an object")

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
            "debt_id",
            "title",
            "architecture_id",
            "description",
            "risk",
            "owner",
            "status",
        }

        missing = required - set(record)

        if missing:
            raise ValueError(
                "Security technical debt record missing fields: "
                + ", ".join(sorted(missing))
            )

        debt_id = record["debt_id"].strip().upper()

        if not debt_id.startswith("SEC-DEBT-"):
            raise ValueError("debt_id must start with SEC-DEBT-")

        status = record["status"].strip().lower()

        if status not in self.ALLOWED_STATUSES:
            raise ValueError("invalid technical debt status")

        stored = deepcopy(record)
        stored["debt_id"] = debt_id
        stored["status"] = status

        with self._lock:
            if debt_id in self._data["records"]:
                raise ValueError(f"technical debt already exists: {debt_id}")

            self._data["records"][debt_id] = stored
            self._save()

        return deepcopy(stored)

    def get(self, debt_id: str) -> Dict[str, Any]:
        debt_id = debt_id.strip().upper()

        with self._lock:
            if debt_id not in self._data["records"]:
                raise KeyError(f"technical debt not found: {debt_id}")

            return deepcopy(self._data["records"][debt_id])

    def update_status(
        self,
        debt_id: str,
        status: str,
    ) -> Dict[str, Any]:
        debt_id = debt_id.strip().upper()
        status = status.strip().lower()

        if status not in self.ALLOWED_STATUSES:
            raise ValueError("invalid technical debt status")

        with self._lock:
            if debt_id not in self._data["records"]:
                raise KeyError(f"technical debt not found: {debt_id}")

            self._data["records"][debt_id]["status"] = status
            self._save()

            return deepcopy(self._data["records"][debt_id])

    def list(self) -> List[Dict[str, Any]]:
        with self._lock:
            return deepcopy(list(self._data["records"].values()))


_default_registry = None


def get_security_technical_debt_registry():
    global _default_registry

    if _default_registry is None:
        _default_registry = SecurityTechnicalDebtRegistry()

    return _default_registry
