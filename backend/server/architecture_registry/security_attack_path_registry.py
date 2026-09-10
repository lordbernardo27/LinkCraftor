from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class SecurityAttackPathRegistry:
    def __init__(self, path: Optional[Path] = None):
        if path is None:
            path = (
                Path(__file__).with_name("data")
                / "security_attack_paths.json"
            )

        self.path = Path(path)
        self._lock = RLock()
        self._data = self._load()

    def _empty(self):
        return {
            "schema_version": "1.0.0",
            "registry_name": "LinkCraftor Security Attack Path Registry",
            "attack_paths": {},
        }

    def _load(self):
        if not self.path.exists():
            return self._empty()

        with self.path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)

        if not isinstance(data.get("attack_paths"), dict):
            raise ValueError("attack_paths must be an object")

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

    def register(
        self,
        record: Dict[str, Any],
        *,
        replace: bool = False,
    ) -> Dict[str, Any]:

        required = {
            "attack_path_id",
            "architecture_id",
            "name",
            "entry_point",
            "target_asset",
            "steps",
            "status",
        }

        missing = required - set(record)

        if missing:
            raise ValueError(
                "attack path missing fields: "
                + ", ".join(sorted(missing))
            )

        attack_path_id = record["attack_path_id"].strip().upper()

        if not attack_path_id.startswith("SEC-AP-"):
            raise ValueError(
                "attack_path_id must start with SEC-AP-"
            )

        if not isinstance(record["steps"], list):
            raise ValueError("attack path steps must be a list")

        stored = deepcopy(record)
        stored["attack_path_id"] = attack_path_id

        with self._lock:
            if (
                attack_path_id in self._data["attack_paths"]
                and not replace
            ):
                raise ValueError(
                    f"attack path already exists: {attack_path_id}"
                )

            self._data["attack_paths"][attack_path_id] = stored
            self._save()

        return deepcopy(stored)

    def get(self, attack_path_id: str) -> Dict[str, Any]:
        attack_path_id = attack_path_id.strip().upper()

        with self._lock:
            if attack_path_id not in self._data["attack_paths"]:
                raise KeyError(
                    f"attack path not found: {attack_path_id}"
                )

            return deepcopy(
                self._data["attack_paths"][attack_path_id]
            )

    def list(self) -> List[Dict[str, Any]]:
        with self._lock:
            return deepcopy(
                list(self._data["attack_paths"].values())
            )


_default_registry = None


def get_security_attack_path_registry():
    global _default_registry

    if _default_registry is None:
        _default_registry = SecurityAttackPathRegistry()

    return _default_registry
