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


class SecurityResidualRiskTracker:
    def __init__(
        self,
        path: Optional[Path] = None,
        risk_registry: Optional[SecurityRiskRegistry] = None,
    ):
        if path is None:
            path = (
                Path(__file__).with_name("data")
                / "security_residual_risk.json"
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
            "registry_name": "LinkCraftor Residual Risk Tracker",
            "assessments": {},
        }

    def _load(self):
        if not self.path.exists():
            return self._empty()

        with self.path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)

        if not isinstance(data.get("assessments"), dict):
            raise ValueError("assessments must be an object")

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

    def record(
        self,
        *,
        assessment_id: str,
        risk_id: str,
        assessor: str,
        evidence: List[str],
    ) -> Dict[str, Any]:

        assessment_id = assessment_id.strip().upper()

        if not assessment_id.startswith("SEC-RR-"):
            raise ValueError(
                "assessment_id must start with SEC-RR-"
            )

        risk = self.risk_registry.get(risk_id)

        required_fields = {
            "inherent_score",
            "inherent_severity",
            "control_effectiveness",
            "residual_score",
            "residual_severity",
        }

        missing = [
            field
            for field in required_fields
            if field not in risk
        ]

        if missing:
            raise ValueError(
                "risk has not completed scoring: "
                + ", ".join(sorted(missing))
            )

        record = {
            "assessment_id": assessment_id,
            "risk_id": risk["risk_id"],
            "inherent_score": risk["inherent_score"],
            "inherent_severity": risk["inherent_severity"],
            "control_effectiveness": risk["control_effectiveness"],
            "residual_score": risk["residual_score"],
            "residual_severity": risk["residual_severity"],
            "assessor": assessor,
            "evidence": deepcopy(evidence),
            "assessed_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        with self._lock:
            if assessment_id in self._data["assessments"]:
                raise ValueError(
                    f"residual assessment exists: {assessment_id}"
                )

            self._data["assessments"][assessment_id] = record
            self._save()

        return deepcopy(record)

    def get(self, assessment_id: str) -> Dict[str, Any]:
        assessment_id = assessment_id.strip().upper()

        with self._lock:
            if assessment_id not in self._data["assessments"]:
                raise KeyError(
                    f"assessment not found: {assessment_id}"
                )

            return deepcopy(
                self._data["assessments"][assessment_id]
            )

    def list(self) -> List[Dict[str, Any]]:
        with self._lock:
            return deepcopy(
                list(self._data["assessments"].values())
            )

    def for_risk(self, risk_id: str) -> List[Dict[str, Any]]:
        risk_id = risk_id.strip().upper()

        return [
            record
            for record in self.list()
            if record["risk_id"] == risk_id
        ]


_default_tracker = None


def get_security_residual_risk_tracker():
    global _default_tracker

    if _default_tracker is None:
        _default_tracker = SecurityResidualRiskTracker()

    return _default_tracker
