from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional

from .security_threat_model_registry import (
    SecurityThreatModelRegistry,
    get_security_threat_model_registry,
)


class SecurityContinuousThreatReview:
    ALLOWED_STATUSES = {
        "scheduled",
        "due",
        "in-review",
        "completed",
        "cancelled",
    }

    def __init__(
        self,
        path: Optional[Path] = None,
        threat_registry: Optional[SecurityThreatModelRegistry] = None,
    ):
        if path is None:
            path = (
                Path(__file__).with_name("data")
                / "security_threat_reviews.json"
            )

        self.path = Path(path)
        self.threat_registry = (
            threat_registry
            if threat_registry is not None
            else get_security_threat_model_registry()
        )

        self._lock = RLock()
        self._data = self._load()

    def _empty(self):
        return {
            "schema_version": "1.0.0",
            "registry_name": "LinkCraftor Continuous Threat Review Registry",
            "reviews": {},
        }

    def _load(self):
        if not self.path.exists():
            return self._empty()

        with self.path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)

        if not isinstance(data.get("reviews"), dict):
            raise ValueError("reviews must be an object")

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

    def schedule(
        self,
        *,
        review_id: str,
        threat_model_id: str,
        reason: str,
        due_at: str,
    ) -> Dict[str, Any]:

        review_id = review_id.strip().upper()

        if not review_id.startswith("SEC-TMR-"):
            raise ValueError(
                "review_id must start with SEC-TMR-"
            )

        model = self.threat_registry.get(threat_model_id)

        due = datetime.fromisoformat(due_at)

        if due.tzinfo is None:
            raise ValueError("due_at must include timezone")

        record = {
            "review_id": review_id,
            "threat_model_id": model["threat_model_id"],
            "component_id": model["component_id"],
            "reason": reason,
            "due_at": due_at,
            "status": "scheduled",
        }

        with self._lock:
            if review_id in self._data["reviews"]:
                raise ValueError(
                    f"threat review already exists: {review_id}"
                )

            self._data["reviews"][review_id] = record
            self._save()

        return deepcopy(record)

    def due(self) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)

        return [
            item
            for item in self.list()
            if item["status"] == "scheduled"
            and datetime.fromisoformat(item["due_at"]) <= now
        ]

    def complete(
        self,
        review_id: str,
        *,
        reviewer: str,
        result: str,
        evidence: List[str],
    ) -> Dict[str, Any]:

        review_id = review_id.strip().upper()

        with self._lock:
            if review_id not in self._data["reviews"]:
                raise KeyError(
                    f"threat review not found: {review_id}"
                )

            record = self._data["reviews"][review_id]
            record["status"] = "completed"
            record["reviewer"] = reviewer
            record["result"] = result
            record["evidence"] = deepcopy(evidence)
            record["completed_at"] = datetime.now(
                timezone.utc
            ).isoformat()

            self._save()

            return deepcopy(record)

    def get(self, review_id: str) -> Dict[str, Any]:
        review_id = review_id.strip().upper()

        with self._lock:
            if review_id not in self._data["reviews"]:
                raise KeyError(
                    f"threat review not found: {review_id}"
                )

            return deepcopy(
                self._data["reviews"][review_id]
            )

    def list(self) -> List[Dict[str, Any]]:
        with self._lock:
            return deepcopy(
                list(self._data["reviews"].values())
            )


_default_service = None


def get_security_continuous_threat_review():
    global _default_service

    if _default_service is None:
        _default_service = SecurityContinuousThreatReview()

    return _default_service
