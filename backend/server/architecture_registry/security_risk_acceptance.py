from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional

from .security_risk_registry import (
    SecurityRiskRegistry,
    get_security_risk_registry,
)


class SecurityRiskAcceptanceWorkflow:
    ALLOWED_STATUSES = {
        "requested",
        "under-review",
        "approved",
        "rejected",
        "expired",
        "revoked",
    }

    def __init__(
        self,
        path: Optional[Path] = None,
        risk_registry: Optional[SecurityRiskRegistry] = None,
    ):
        if path is None:
            path = (
                Path(__file__).with_name("data")
                / "security_risk_acceptances.json"
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
            "registry_name": "LinkCraftor Security Risk Acceptance Workflow",
            "acceptances": {},
        }

    def _load(self):
        if not self.path.exists():
            return self._empty()

        with self.path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)

        if not isinstance(data.get("acceptances"), dict):
            raise ValueError("acceptances must be an object")

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

    def request(self, record: Dict[str, Any]) -> Dict[str, Any]:
        required = {
            "acceptance_id",
            "risk_id",
            "requested_by",
            "rationale",
            "expires_at",
        }

        missing = required - set(record)

        if missing:
            raise ValueError(
                "risk acceptance missing fields: "
                + ", ".join(sorted(missing))
            )

        acceptance_id = record["acceptance_id"].strip().upper()

        if not acceptance_id.startswith("SEC-RA-"):
            raise ValueError(
                "acceptance_id must start with SEC-RA-"
            )

        risk = self.risk_registry.get(record["risk_id"])

        if risk.get("severity") in {None, "unscored"}:
            raise ValueError(
                "risk must be scored before acceptance request"
            )

        expires_at = datetime.fromisoformat(record["expires_at"])

        if expires_at.tzinfo is None:
            raise ValueError("expires_at must include timezone")

        stored = deepcopy(record)
        stored["acceptance_id"] = acceptance_id
        stored["risk_id"] = risk["risk_id"]
        stored["status"] = "requested"
        stored["risk_severity"] = risk["severity"]

        with self._lock:
            if acceptance_id in self._data["acceptances"]:
                raise ValueError(
                    f"risk acceptance already exists: {acceptance_id}"
                )

            self._data["acceptances"][acceptance_id] = stored
            self._save()

        return deepcopy(stored)

    def approve(
        self,
        acceptance_id: str,
        *,
        approver: str,
        sarb_approved: bool = False,
        platform_owner_approved: bool = False,
    ) -> Dict[str, Any]:

        acceptance_id = acceptance_id.strip().upper()

        with self._lock:
            if acceptance_id not in self._data["acceptances"]:
                raise KeyError(
                    f"risk acceptance not found: {acceptance_id}"
                )

            record = self._data["acceptances"][acceptance_id]

            severity = record["risk_severity"]

            if severity == "high" and not platform_owner_approved:
                raise ValueError(
                    "High risk requires Platform Owner approval"
                )

            if severity == "critical":
                if not platform_owner_approved:
                    raise ValueError(
                        "Critical risk requires Platform Owner approval"
                    )

                if not sarb_approved:
                    raise ValueError(
                        "Critical risk requires SARB approval"
                    )

            record["status"] = "approved"
            record["approver"] = approver
            record["platform_owner_approved"] = platform_owner_approved
            record["sarb_approved"] = sarb_approved
            record["approved_at"] = datetime.now(
                timezone.utc
            ).isoformat()

            self._save()

        self.risk_registry.update(
            record["risk_id"],
            {"status": "accepted"},
        )

        return deepcopy(record)

    def get(self, acceptance_id: str) -> Dict[str, Any]:
        acceptance_id = acceptance_id.strip().upper()

        with self._lock:
            if acceptance_id not in self._data["acceptances"]:
                raise KeyError(
                    f"risk acceptance not found: {acceptance_id}"
                )

            return deepcopy(
                self._data["acceptances"][acceptance_id]
            )

    def list(self) -> List[Dict[str, Any]]:
        with self._lock:
            return deepcopy(
                list(self._data["acceptances"].values())
            )

    def expired(self) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)

        return [
            item
            for item in self.list()
            if item.get("status") == "approved"
            and datetime.fromisoformat(item["expires_at"]) <= now
        ]


_default_workflow = None


def get_security_risk_acceptance_workflow():
    global _default_workflow

    if _default_workflow is None:
        _default_workflow = SecurityRiskAcceptanceWorkflow()

    return _default_workflow
