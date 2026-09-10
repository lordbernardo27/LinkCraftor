from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional


class SecurityAbuseCaseRegistry:
    def __init__(self, path: Optional[Path] = None):
        if path is None:
            path = (
                Path(__file__).with_name("data")
                / "security_abuse_cases.json"
            )

        self.path = Path(path)
        self._lock = RLock()
        self._data = self._load()

    def _empty(self):
        return {
            "schema_version": "1.0.0",
            "registry_name": "LinkCraftor Security Abuse Case Registry",
            "abuse_cases": {},
        }

    def _load(self):
        if not self.path.exists():
            return self._empty()

        with self.path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)

        if not isinstance(data.get("abuse_cases"), dict):
            raise ValueError("abuse_cases must be an object")

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
            "abuse_case_id",
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
                "abuse case missing fields: "
                + ", ".join(sorted(missing))
            )

        abuse_case_id = record["abuse_case_id"].strip().upper()

        if not abuse_case_id.startswith("SEC-ABUSE-"):
            raise ValueError(
                "abuse_case_id must start with SEC-ABUSE-"
            )

        stored = deepcopy(record)
        stored["abuse_case_id"] = abuse_case_id

        with self._lock:
            if (
                abuse_case_id in self._data["abuse_cases"]
                and not replace
            ):
                raise ValueError(
                    f"abuse case already exists: {abuse_case_id}"
                )

            self._data["abuse_cases"][abuse_case_id] = stored
            self._save()

        return deepcopy(stored)

    def get(self, abuse_case_id: str) -> Dict[str, Any]:
        abuse_case_id = abuse_case_id.strip().upper()

        with self._lock:
            if abuse_case_id not in self._data["abuse_cases"]:
                raise KeyError(
                    f"abuse case not found: {abuse_case_id}"
                )

            return deepcopy(
                self._data["abuse_cases"][abuse_case_id]
            )

    def list(self) -> List[Dict[str, Any]]:
        with self._lock:
            return deepcopy(
                list(self._data["abuse_cases"].values())
            )


_default_registry = None


def get_security_abuse_case_registry():
    global _default_registry

    if _default_registry is None:
        _default_registry = SecurityAbuseCaseRegistry()

    return _default_registry
