from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class SecurityRiskRegistry:
    """
    Canonical operational registry for LinkCraftor security risks.

    This registry records risk state. Detailed risk scoring, acceptance,
    treatment planning, and residual-risk automation are provided by later
    PSA components.
    """

    ALLOWED_STATUSES = {
        "identified",
        "assessing",
        "treatment-planned",
        "treatment-in-progress",
        "acceptance-pending",
        "accepted",
        "monitoring",
        "mitigated",
        "closed",
        "reopened",
        "superseded",
    }

    ALLOWED_SEVERITIES = {
        "low",
        "medium",
        "high",
        "critical",
        "unscored",
    }

    def __init__(self, path: Optional[Path] = None):
        if path is None:
            path = Path(__file__).with_name("data") / "security_risks.json"

        self.path = Path(path)
        self._lock = RLock()
        self._data = self._load()

    def _empty(self):
        return {
            "schema_version": "1.0.0",
            "registry_name": "LinkCraftor Security Risk Registry",
            "risks": {},
        }

    def _load(self):
        if not self.path.exists():
            return self._empty()

        with self.path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)

        if not isinstance(data.get("risks"), dict):
            raise ValueError("security risks must be an object")

        return data

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)

        temporary = self.path.with_suffix(self.path.suffix + ".tmp")

        with temporary.open("w", encoding="utf-8") as handle:
            json.dump(
                self._data,
                handle,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )
            handle.write("\n")

        temporary.replace(self.path)

    def register(self, risk: Dict[str, Any]) -> Dict[str, Any]:
        required = {
            "risk_id",
            "title",
            "architecture_id",
            "risk_statement",
            "category",
            "risk_owner",
            "status",
            "severity",
        }

        missing = required - set(risk)

        if missing:
            raise ValueError(
                "security risk missing fields: "
                + ", ".join(sorted(missing))
            )

        risk_id = risk["risk_id"].strip().upper()

        if not risk_id.startswith("SEC-RISK-"):
            raise ValueError("risk_id must start with SEC-RISK-")

        status = risk["status"].strip().lower()
        severity = risk["severity"].strip().lower()

        if status not in self.ALLOWED_STATUSES:
            raise ValueError("invalid security risk status")

        if severity not in self.ALLOWED_SEVERITIES:
            raise ValueError("invalid security risk severity")

        stored = deepcopy(risk)
        stored["risk_id"] = risk_id
        stored["status"] = status
        stored["severity"] = severity

        with self._lock:
            if risk_id in self._data["risks"]:
                raise ValueError(f"security risk already exists: {risk_id}")

            self._data["risks"][risk_id] = stored
            self._save()

        return deepcopy(stored)

    def get(self, risk_id: str) -> Dict[str, Any]:
        risk_id = risk_id.strip().upper()

        with self._lock:
            if risk_id not in self._data["risks"]:
                raise KeyError(f"security risk not found: {risk_id}")

            return deepcopy(self._data["risks"][risk_id])

    def update(
        self,
        risk_id: str,
        changes: Dict[str, Any],
    ) -> Dict[str, Any]:

        risk_id = risk_id.strip().upper()

        with self._lock:
            if risk_id not in self._data["risks"]:
                raise KeyError(f"security risk not found: {risk_id}")

            updated = deepcopy(self._data["risks"][risk_id])
            updated.update(deepcopy(changes))
            updated["risk_id"] = risk_id

            status = updated["status"].strip().lower()
            severity = updated["severity"].strip().lower()

            if status not in self.ALLOWED_STATUSES:
                raise ValueError("invalid security risk status")

            if severity not in self.ALLOWED_SEVERITIES:
                raise ValueError("invalid security risk severity")

            updated["status"] = status
            updated["severity"] = severity

            self._data["risks"][risk_id] = updated
            self._save()

            return deepcopy(updated)

    def list(self) -> List[Dict[str, Any]]:
        with self._lock:
            return deepcopy(list(self._data["risks"].values()))

    def open_risks(self) -> List[Dict[str, Any]]:
        return [
            risk
            for risk in self.list()
            if risk.get("status")
            not in {"closed", "superseded"}
        ]

    def critical_risks(self) -> List[Dict[str, Any]]:
        return [
            risk
            for risk in self.open_risks()
            if risk.get("severity") == "critical"
        ]


_default_registry = None


def get_security_risk_registry():
    global _default_registry

    if _default_registry is None:
        _default_registry = SecurityRiskRegistry()

    return _default_registry
