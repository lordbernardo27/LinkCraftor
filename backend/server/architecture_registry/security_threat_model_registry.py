from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class SecurityThreatModelRegistry:
    """
    Canonical structured registry for LinkCraftor threat models.

    Each specialist PSA threat-model component registers its canonical model
    here while its detailed architecture remains in its canonical document.
    """

    ALLOWED_STATUSES = {
        "draft",
        "active",
        "under-review",
        "superseded",
        "retired",
    }

    def __init__(self, path: Optional[Path] = None):
        if path is None:
            path = (
                Path(__file__).with_name("data")
                / "security_threat_models.json"
            )

        self.path = Path(path)
        self._lock = RLock()
        self._data = self._load()

    def _empty(self):
        return {
            "schema_version": "1.0.0",
            "registry_name": "LinkCraftor Security Threat Model Registry",
            "models": {},
        }

    def _load(self):
        if not self.path.exists():
            return self._empty()

        with self.path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)

        if not isinstance(data.get("models"), dict):
            raise ValueError("threat models must be an object")

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

    def register(
        self,
        model: Dict[str, Any],
        *,
        replace: bool = False,
    ) -> Dict[str, Any]:

        required = {
            "threat_model_id",
            "component_id",
            "architecture_id",
            "name",
            "scope",
            "status",
            "canonical_path",
            "threat_categories",
        }

        missing = required - set(model)

        if missing:
            raise ValueError(
                "threat model missing fields: "
                + ", ".join(sorted(missing))
            )

        model_id = model["threat_model_id"].strip().upper()

        if not model_id.startswith("SEC-TM-"):
            raise ValueError("threat_model_id must start with SEC-TM-")

        status = model["status"].strip().lower()

        if status not in self.ALLOWED_STATUSES:
            raise ValueError("invalid threat model status")

        if not isinstance(model["threat_categories"], list):
            raise ValueError("threat_categories must be a list")

        stored = deepcopy(model)
        stored["threat_model_id"] = model_id
        stored["status"] = status

        with self._lock:
            if model_id in self._data["models"] and not replace:
                raise ValueError(
                    f"threat model already exists: {model_id}"
                )

            self._data["models"][model_id] = stored
            self._save()

        return deepcopy(stored)

    def get(self, threat_model_id: str) -> Dict[str, Any]:
        threat_model_id = threat_model_id.strip().upper()

        with self._lock:
            if threat_model_id not in self._data["models"]:
                raise KeyError(
                    f"threat model not found: {threat_model_id}"
                )

            return deepcopy(
                self._data["models"][threat_model_id]
            )

    def list(self) -> List[Dict[str, Any]]:
        with self._lock:
            return deepcopy(list(self._data["models"].values()))

    def by_component(self, component_id: str) -> List[Dict[str, Any]]:
        return [
            model
            for model in self.list()
            if model.get("component_id") == component_id
        ]


_default_registry = None


def get_security_threat_model_registry():
    global _default_registry

    if _default_registry is None:
        _default_registry = SecurityThreatModelRegistry()

    return _default_registry
