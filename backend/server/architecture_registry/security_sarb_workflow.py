from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class SecuritySARBWorkflow:
    ALLOWED_STATUSES = {
        "submitted",
        "under-review",
        "approved",
        "rejected",
        "changes-requested",
        "closed",
    }

    FINAL_STATUSES = {
        "approved",
        "rejected",
        "closed",
    }

    def __init__(self, path: Optional[Path] = None):
        if path is None:
            path = Path(__file__).with_name("data") / "security_sarb_reviews.json"

        self.path = Path(path)
        self._lock = RLock()
        self._data = self._load()

    def _empty(self):
        return {
            "schema_version": "1.0.0",
            "registry_name": "LinkCraftor Security Architecture Review Board Workflow",
            "reviews": {},
        }

    def _load(self):
        if not self.path.exists():
            return self._empty()

        with self.path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)

        if not isinstance(data.get("reviews"), dict):
            raise ValueError("SARB reviews must be an object")

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

    def submit(self, review: Dict[str, Any]) -> Dict[str, Any]:
        required = {
            "review_id",
            "architecture_id",
            "title",
            "requester",
            "reason",
        }

        missing = required - set(review)

        if missing:
            raise ValueError(
                "SARB review missing fields: "
                + ", ".join(sorted(missing))
            )

        review_id = review["review_id"].strip().upper()

        if not review_id.startswith("SEC-SARB-"):
            raise ValueError("review_id must start with SEC-SARB-")

        stored = deepcopy(review)
        stored["review_id"] = review_id
        stored["status"] = "submitted"
        stored.setdefault("decision", None)
        stored.setdefault("reviewer", None)

        with self._lock:
            if review_id in self._data["reviews"]:
                raise ValueError(f"SARB review already exists: {review_id}")

            self._data["reviews"][review_id] = stored
            self._save()

        return deepcopy(stored)

    def transition(
        self,
        review_id: str,
        status: str,
        *,
        reviewer: Optional[str] = None,
        decision: Optional[str] = None,
    ) -> Dict[str, Any]:
        review_id = review_id.strip().upper()
        status = status.strip().lower()

        if status not in self.ALLOWED_STATUSES:
            raise ValueError("invalid SARB status")

        with self._lock:
            if review_id not in self._data["reviews"]:
                raise KeyError(f"SARB review not found: {review_id}")

            record = self._data["reviews"][review_id]

            if record["status"] in self.FINAL_STATUSES:
                raise ValueError("final SARB review cannot transition")

            record["status"] = status

            if reviewer is not None:
                record["reviewer"] = reviewer

            if decision is not None:
                record["decision"] = decision

            if status in {"approved", "rejected", "changes-requested"}:
                if not reviewer or not decision:
                    raise ValueError(
                        "reviewer and decision are required for SARB decision"
                    )

            self._save()

            return deepcopy(record)

    def get(self, review_id: str) -> Dict[str, Any]:
        review_id = review_id.strip().upper()

        with self._lock:
            if review_id not in self._data["reviews"]:
                raise KeyError(f"SARB review not found: {review_id}")

            return deepcopy(self._data["reviews"][review_id])

    def pending(self) -> List[Dict[str, Any]]:
        return [
            review
            for review in self.list()
            if review["status"] in {
                "submitted",
                "under-review",
                "changes-requested",
            }
        ]

    def list(self) -> List[Dict[str, Any]]:
        with self._lock:
            return deepcopy(list(self._data["reviews"].values()))


_default_workflow = None


def get_security_sarb_workflow():
    global _default_workflow

    if _default_workflow is None:
        _default_workflow = SecuritySARBWorkflow()

    return _default_workflow
