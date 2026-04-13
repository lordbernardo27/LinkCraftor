from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from ..engine.profiles import normalize_profile_id

DEFAULT_PROFILE = "general"

STORE_PATH = Path("backend/server/data/workspace_profiles.json")

DEFAULT_WORKSPACE_PROFILE_MAP: Dict[str, str] = {
    "ws_betterhealthcheck_com": "medical",
    "ws_superapihelp_com": "saas",
    "ws_examplefinance_com": "finance",
    "ws_examplestore_com": "ecommerce",
    "ws_test": "general",
}


def _ensure_store_dir() -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)


def _load_store() -> Dict[str, str]:
    _ensure_store_dir()

    if not STORE_PATH.exists():
        _save_store(DEFAULT_WORKSPACE_PROFILE_MAP)
        return dict(DEFAULT_WORKSPACE_PROFILE_MAP)

    try:
        raw = json.loads(STORE_PATH.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return dict(DEFAULT_WORKSPACE_PROFILE_MAP)

        cleaned: Dict[str, str] = {}
        for workspace_id, profile_id in raw.items():
            key = str(workspace_id or "").strip()
            if not key:
                continue
            cleaned[key] = normalize_profile_id(profile_id, default=DEFAULT_PROFILE)

        if not cleaned:
            cleaned = dict(DEFAULT_WORKSPACE_PROFILE_MAP)

        return cleaned
    except Exception:
        return dict(DEFAULT_WORKSPACE_PROFILE_MAP)


def _save_store(data: Dict[str, str]) -> None:
    _ensure_store_dir()
    STORE_PATH.write_text(
        json.dumps(data, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def get_workspace_profile(workspace_id: str | None) -> str:
    workspace_profile_map = _load_store()
    key = str(workspace_id or "").strip()
    if not key:
        return DEFAULT_PROFILE
    return workspace_profile_map.get(key, DEFAULT_PROFILE)


def set_workspace_profile(workspace_id: str | None, profile_id: str | None) -> str:
    key = str(workspace_id or "").strip()
    if not key:
        return DEFAULT_PROFILE

    workspace_profile_map = _load_store()
    normalized = normalize_profile_id(profile_id, default=DEFAULT_PROFILE)
    workspace_profile_map[key] = normalized
    _save_store(workspace_profile_map)
    return normalized