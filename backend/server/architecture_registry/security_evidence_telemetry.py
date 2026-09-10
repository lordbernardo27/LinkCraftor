from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class SecurityEvidenceTelemetry:
    def __init__(
        self,
        evidence_path: Optional[Path] = None,
        telemetry_path: Optional[Path] = None,
    ):
        base = Path(__file__).with_name("data")

        self.evidence_path = (
            Path(evidence_path)
            if evidence_path is not None
            else base / "security_evidence.json"
        )

        self.telemetry_path = (
            Path(telemetry_path)
            if telemetry_path is not None
            else base / "security_telemetry.jsonl"
        )

        self._lock = RLock()
        self._data = self._load()

    def _empty(self):
        return {
            "schema_version": "1.0.0",
            "registry_name": "LinkCraftor Security Evidence Registry",
            "evidence": {},
        }

    def _load(self):
        if not self.evidence_path.exists():
            return self._empty()

        with self.evidence_path.open(
            "r",
            encoding="utf-8-sig",
        ) as handle:
            data = json.load(handle)

        if not isinstance(data.get("evidence"), dict):
            raise ValueError("evidence must be an object")

        return data

    def _save(self):
        self.evidence_path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.evidence_path.with_suffix(
            self.evidence_path.suffix + ".tmp"
        )

        with temp.open("w", encoding="utf-8") as handle:
            json.dump(
                self._data,
                handle,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )
            handle.write("\n")

        temp.replace(self.evidence_path)

    def record_evidence(self, record: Dict[str, Any]) -> Dict[str, Any]:
        required = {
            "evidence_id",
            "architecture_id",
            "control_or_component",
            "evidence_type",
            "source",
            "result",
        }

        missing = required - set(record)

        if missing:
            raise ValueError(
                "Security evidence missing fields: "
                + ", ".join(sorted(missing))
            )

        evidence_id = record["evidence_id"].strip().upper()

        if not evidence_id.startswith("SEC-EVID-"):
            raise ValueError("evidence_id must start with SEC-EVID-")

        stored = deepcopy(record)
        stored["evidence_id"] = evidence_id
        stored.setdefault("recorded_at", self._utc_now())

        with self._lock:
            self._data["evidence"][evidence_id] = stored
            self._save()

        self.emit_event(
            "security.evidence.recorded",
            {
                "evidence_id": evidence_id,
                "architecture_id": stored["architecture_id"],
                "result": stored["result"],
            },
        )

        return deepcopy(stored)

    def emit_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        event = {
            "timestamp": self._utc_now(),
            "event_type": event_type,
            "payload": deepcopy(payload),
        }

        self.telemetry_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self._lock:
            with self.telemetry_path.open(
                "a",
                encoding="utf-8",
            ) as handle:
                handle.write(
                    json.dumps(
                        event,
                        ensure_ascii=False,
                        sort_keys=True,
                    )
                    + "\n"
                )

        return deepcopy(event)

    def get_evidence(self, evidence_id: str) -> Dict[str, Any]:
        evidence_id = evidence_id.strip().upper()

        with self._lock:
            if evidence_id not in self._data["evidence"]:
                raise KeyError(f"evidence not found: {evidence_id}")

            return deepcopy(
                self._data["evidence"][evidence_id]
            )

    def list_evidence(self) -> List[Dict[str, Any]]:
        with self._lock:
            return deepcopy(list(self._data["evidence"].values()))

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()


_default_service = None


def get_security_evidence_telemetry():
    global _default_service

    if _default_service is None:
        _default_service = SecurityEvidenceTelemetry()

    return _default_service
