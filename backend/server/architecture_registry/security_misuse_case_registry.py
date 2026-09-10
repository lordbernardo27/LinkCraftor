from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class SecurityMisuseCaseRegistry:
    def __init__(self, path: Optional[Path] = None):
        if path is None:
            path = (
                Path(__file__).with_name("data")
                / "security_misuse_cases.json"
            )

        self.path = Path(path)
        self._lock = RLock()
        self._data = self._load()

    def _empty(self):
        return {
            "schema_version": "1.0.0",
            "registry_name": "LinkCraftor Security Misuse Case Registry",
            "misuse_cases": {},
        }

    def _load(self):
        if not self.path.exists():
            return self._empty()

        with self.path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)

        if not isinstance(data.get("misuse_cases"), dict):
            raise ValueError("misuse_cases must be an object")

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
            "misuse_case_id",
            "architecture_id",
            "name",
            "actor",
            "capability",
            "impact",
            "status",
        }

        missing = required - set(record)

        if missing:
            raise ValueError(
                "misuse case missing fields: "
                + ", ".join(sorted(missing))
            )

        misuse_case_id = record["misuse_case_id"].strip().upper()

        if not misuse_case_id.startswith("SEC-MISUSE-"):
            raise ValueError(
                "misuse_case_id must start with SEC-MISUSE-"
            )

        stored = deepcopy(record)
        stored["misuse_case_id"] = misuse_case_id

        with self._lock:
            if (
                misuse_case_id in self._data["misuse_cases"]
                and not replace
            ):
                raise ValueError(
                    f"misuse case already exists: {misuse_case_id}"
                )

            self._data["misuse_cases"][misuse_case_id] = stored
            self._save()

        return deepcopy(stored)

    def get(self, misuse_case_id: str) -> Dict[str, Any]:
        misuse_case_id = misuse_case_id.strip().upper()

        with self._lock:
            if misuse_case_id not in self._data["misuse_cases"]:
                raise KeyError(
                    f"misuse case not found: {misuse_case_id}"
                )

            return deepcopy(
                self._data["misuse_cases"][misuse_case_id]
            )

    def list(self) -> List[Dict[str, Any]]:
        with self._lock:
            return deepcopy(
                list(self._data["misuse_cases"].values())
            )


_default_registry = None


def get_security_misuse_case_registry():
    global _default_registry

    if _default_registry is None:
        _default_registry = SecurityMisuseCaseRegistry()

    return _default_registry
