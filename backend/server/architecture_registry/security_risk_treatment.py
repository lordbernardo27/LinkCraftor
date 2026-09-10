from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional

from .security_risk_registry import (
    SecurityRiskRegistry,
    get_security_risk_registry,
)


class SecurityRiskTreatmentRegistry:
    ALLOWED_STRATEGIES = {
        "avoid",
        "mitigate",
        "transfer",
        "accept",
    }

    ALLOWED_STATUSES = {
        "planned",
        "in-progress",
        "validation",
        "completed",
        "failed",
        "cancelled",
    }

    def __init__(
        self,
        path: Optional[Path] = None,
        risk_registry: Optional[SecurityRiskRegistry] = None,
    ):
        if path is None:
            path = (
                Path(__file__).with_name("data")
                / "security_risk_treatments.json"
            )

        self.path = Path(path)
        self.risk_registry = (
            risk_registry
            if risk_registry is not None
            else get_security_risk_registry()
        )

        self._lock = RLock()
        self._data = self._load()

    def _empty(self):
        return {
            "schema_version": "1.0.0",
            "registry_name": "LinkCraftor Security Risk Treatment Registry",
            "treatments": {},
        }

    def _load(self):
        if not self.path.exists():
            return self._empty()

        with self.path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)

        if not isinstance(data.get("treatments"), dict):
            raise ValueError("treatments must be an object")

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

    def create(self, record: Dict[str, Any]) -> Dict[str, Any]:
        required = {
            "treatment_id",
            "risk_id",
            "strategy",
            "owner",
            "actions",
            "target_date",
        }

        missing = required - set(record)

        if missing:
            raise ValueError(
                "risk treatment missing fields: "
                + ", ".join(sorted(missing))
            )

        treatment_id = record["treatment_id"].strip().upper()

        if not treatment_id.startswith("SEC-RT-"):
            raise ValueError(
                "treatment_id must start with SEC-RT-"
            )

        strategy = record["strategy"].strip().lower()

        if strategy not in self.ALLOWED_STRATEGIES:
            raise ValueError("invalid treatment strategy")

        if not isinstance(record["actions"], list):
            raise ValueError("actions must be a list")

        risk = self.risk_registry.get(record["risk_id"])

        stored = deepcopy(record)
        stored["treatment_id"] = treatment_id
        stored["risk_id"] = risk["risk_id"]
        stored["strategy"] = strategy
        stored["status"] = "planned"

        with self._lock:
            if treatment_id in self._data["treatments"]:
                raise ValueError(
                    f"risk treatment already exists: {treatment_id}"
                )

            self._data["treatments"][treatment_id] = stored
            self._save()

        self.risk_registry.update(
            risk["risk_id"],
            {"status": "treatment-planned"},
        )

        return deepcopy(stored)

    def transition(
        self,
        treatment_id: str,
        status: str,
    ) -> Dict[str, Any]:

        treatment_id = treatment_id.strip().upper()
        status = status.strip().lower()

        if status not in self.ALLOWED_STATUSES:
            raise ValueError("invalid treatment status")

        with self._lock:
            if treatment_id not in self._data["treatments"]:
                raise KeyError(
                    f"risk treatment not found: {treatment_id}"
                )

            record = self._data["treatments"][treatment_id]
            record["status"] = status
            self._save()

        if status == "in-progress":
            self.risk_registry.update(
                record["risk_id"],
                {"status": "treatment-in-progress"},
            )

        if status == "completed":
            self.risk_registry.update(
                record["risk_id"],
                {"status": "monitoring"},
            )

        return deepcopy(record)

    def get(self, treatment_id: str) -> Dict[str, Any]:
        treatment_id = treatment_id.strip().upper()

        with self._lock:
            if treatment_id not in self._data["treatments"]:
                raise KeyError(
                    f"risk treatment not found: {treatment_id}"
                )

            return deepcopy(
                self._data["treatments"][treatment_id]
            )

    def list(self) -> List[Dict[str, Any]]:
        with self._lock:
            return deepcopy(
                list(self._data["treatments"].values())
            )


_default_registry = None


def get_security_risk_treatment_registry():
    global _default_registry

    if _default_registry is None:
        _default_registry = SecurityRiskTreatmentRegistry()

    return _default_registry
