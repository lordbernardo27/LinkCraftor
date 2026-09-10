from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class SecurityControlOwnershipRegistry:
    """
    Canonical registry mapping security controls to accountable owners.
    """

    def __init__(self, path: Optional[Path] = None):
        if path is None:
            path = (
                Path(__file__).with_name("data")
                / "security_control_ownership.json"
            )

        self.path = Path(path)
        self._lock = RLock()
        self._data = self._load()

    def _empty(self):
        return {
            "schema_version": "1.0.0",
            "registry_name": "LinkCraftor Security Control Ownership Registry",
            "controls": {},
        }

    def _load(self):
        if not self.path.exists():
            return self._empty()

        with self.path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)

        if not isinstance(data.get("controls"), dict):
            raise ValueError("controls must be a JSON object")

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

    def assign(self, control: Dict[str, Any]) -> Dict[str, Any]:
        required = {
            "control_id",
            "control_name",
            "architecture_id",
            "accountable_owner",
            "operational_owner",
            "status",
        }

        missing = required - set(control)

        if missing:
            raise ValueError(
                "Control ownership record missing fields: "
                + ", ".join(sorted(missing))
            )

        control_id = control["control_id"].strip().upper()

        if not control_id:
            raise ValueError("control_id cannot be empty")

        stored = deepcopy(control)
        stored["control_id"] = control_id

        with self._lock:
            self._data["controls"][control_id] = stored
            self._save()

        return deepcopy(stored)

    def get(self, control_id: str) -> Dict[str, Any]:
        control_id = control_id.strip().upper()

        with self._lock:
            if control_id not in self._data["controls"]:
                raise KeyError(
                    f"Security control ownership not found: {control_id}"
                )

            return deepcopy(self._data["controls"][control_id])

    def list(self) -> List[Dict[str, Any]]:
        with self._lock:
            return deepcopy(list(self._data["controls"].values()))

    def unowned_controls(self) -> List[Dict[str, Any]]:
        results = []

        for control in self.list():
            if not control.get("accountable_owner"):
                results.append(control)

        return results


_default_registry = None


def get_security_control_ownership_registry():
    global _default_registry

    if _default_registry is None:
        _default_registry = SecurityControlOwnershipRegistry()

    return _default_registry
