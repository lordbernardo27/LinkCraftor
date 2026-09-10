from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class SecurityFoundationCertificationRegistry:
    ALLOWED_STATUSES = {
        "pending",
        "certified",
        "conditional",
        "failed",
        "revoked",
        "superseded",
    }

    def __init__(self, path: Optional[Path] = None):
        if path is None:
            path = (
                Path(__file__).with_name("data")
                / "security_foundation_certifications.json"
            )

        self.path = Path(path)
        self._lock = RLock()
        self._data = self._load()

    def _empty(self):
        return {
            "schema_version": "1.0.0",
            "registry_name": "LinkCraftor Security Foundation Certification Registry",
            "certifications": {},
        }

    def _load(self):
        if not self.path.exists():
            return self._empty()

        with self.path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)

        if not isinstance(data.get("certifications"), dict):
            raise ValueError("certifications must be an object")

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

    def record(self, certification: Dict[str, Any]) -> Dict[str, Any]:
        required = {
            "certification_id",
            "architecture_id",
            "scope",
            "status",
            "evidence",
            "certifier",
        }

        missing = required - set(certification)

        if missing:
            raise ValueError(
                "Certification missing fields: "
                + ", ".join(sorted(missing))
            )

        certification_id = certification["certification_id"].strip().upper()

        if not certification_id.startswith("SEC-CERT-"):
            raise ValueError("certification_id must start with SEC-CERT-")

        status = certification["status"].strip().lower()

        if status not in self.ALLOWED_STATUSES:
            raise ValueError("invalid certification status")

        if not isinstance(certification["evidence"], list):
            raise ValueError("certification evidence must be a list")

        stored = deepcopy(certification)
        stored["certification_id"] = certification_id
        stored["status"] = status

        with self._lock:
            self._data["certifications"][certification_id] = stored
            self._save()

        return deepcopy(stored)

    def get(self, certification_id: str) -> Dict[str, Any]:
        certification_id = certification_id.strip().upper()

        with self._lock:
            if certification_id not in self._data["certifications"]:
                raise KeyError(
                    f"certification not found: {certification_id}"
                )

            return deepcopy(
                self._data["certifications"][certification_id]
            )

    def list(self) -> List[Dict[str, Any]]:
        with self._lock:
            return deepcopy(
                list(self._data["certifications"].values())
            )


_default_registry = None


def get_security_foundation_certification_registry():
    global _default_registry

    if _default_registry is None:
        _default_registry = SecurityFoundationCertificationRegistry()

    return _default_registry
